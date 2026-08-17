"""
STREAM-VAE: Dual-Path Routing for Slow and Fast Dynamics in Vehicle Telemetry Anomaly Detection
"""

from __future__ import division
from __future__ import print_function

import copy
import math

import numpy as np
import torch
import torch.nn.functional as F
import tqdm
from torch import nn
from torch.distributions import Normal, kl_divergence
from torch.utils.data import DataLoader

from .base import BaseDetector
from ..utils.dataset import ReconstructDataset
from ..utils.torch_utility import get_gpu


class _EarlyStoppingTorch:
    def __init__(self, patience=10, min_delta=0.0):
        self.patience = int(patience)
        self.min_delta = float(min_delta)
        self.counter = 0
        self.best = None
        self.best_state = None
        self.early_stop = False

    def __call__(self, val_loss, model):
        score = float(val_loss)
        if self.best is None or score < (self.best - self.min_delta):
            self.best = score
            self.counter = 0
            self.best_state = copy.deepcopy({
                name: tensor.detach().cpu()
                for name, tensor in model.state_dict().items()
            })
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True

    def restore(self, model):
        if self.best_state is not None:
            model.load_state_dict(self.best_state, strict=True)


class _MultiheadGQA(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.head_dim = d_model // num_heads
        self.w_q = nn.Linear(d_model, d_model, bias=False)
        self.w_k = nn.Linear(d_model, d_model, bias=False)
        self.w_v = nn.Linear(d_model, d_model, bias=False)
        self.w_o = nn.Linear(d_model, d_model)

    def forward(self, query, key, value):
        batch_size, steps, _ = query.shape
        q = self.w_q(query).view(batch_size, steps, self.num_heads, self.head_dim).transpose(1, 2)
        k = self.w_k(key).view(batch_size, steps, self.num_heads, self.head_dim).transpose(1, 2)
        v = self.w_v(value).view(batch_size, steps, self.num_heads, self.head_dim).transpose(1, 2)
        out = F.scaled_dot_product_attention(q, k, v, dropout_p=0.0)
        out = out.transpose(1, 2).contiguous().view(batch_size, steps, -1)
        return self.w_o(out)


class _LearnableSoftThreshold(nn.Module):
    def __init__(self, n_feats, init=1.0):
        super().__init__()
        init_value = torch.log(torch.expm1(torch.tensor(init)))
        self.log_tau = nn.Parameter(init_value * torch.ones(n_feats))

    def forward(self, x):
        tau = F.softplus(self.log_tau).view(1, 1, -1)
        return torch.sign(x) * F.relu(torch.abs(x) - tau)


class _LearnableEMA(nn.Module):
    def __init__(self, n_feats, init_alpha=0.9):
        super().__init__()
        logit_alpha = math.log(init_alpha / (1.0 - init_alpha))
        self.logit_alpha = nn.Parameter(torch.full((n_feats,), logit_alpha))

    def forward(self, x):
        _, steps, dims = x.shape
        alpha = torch.sigmoid(self.logit_alpha).view(1, 1, dims)
        one_minus_alpha = 1.0 - alpha

        outputs = []
        previous = x[:, 0, :]
        outputs.append(previous)
        for step in range(1, steps):
            current = alpha.squeeze(1) * previous + one_minus_alpha.squeeze(1) * x[:, step, :]
            outputs.append(current)
            previous = current
        return torch.stack(outputs, dim=1)


class StreamVAEModel(nn.Module):
    def __init__(self, feats, latent_dim, hidden_dim, device):
        super().__init__()
        self.name = "StreamVAE"
        self.device = device
        self.n_feats = feats
        self.n_hidden = hidden_dim
        self.n_latent = latent_dim
        self.beta = 1e-4

        self.enc_l1 = nn.LSTM(feats, self.n_hidden, 1, bidirectional=True, batch_first=True)
        self.enc_l2 = nn.LSTM(self.n_hidden * 2, self.n_hidden // 2, 1, bidirectional=True, batch_first=True)

        enc_out_dim = self.n_hidden
        self.inj = nn.Linear(feats, self.n_latent, bias=False)
        self.inj_gate = nn.Parameter(torch.tensor(-2.0))
        self.to_mean = nn.Linear(enc_out_dim + self.n_latent, self.n_latent)
        self.to_logvar = nn.Linear(enc_out_dim + self.n_latent, self.n_latent)

        self.proj_z = nn.Linear(self.n_latent, self.n_latent)
        self.proj_enc = nn.Linear(enc_out_dim, self.n_latent)

        self.ema_z = _LearnableEMA(self.n_latent, init_alpha=0.9)
        self.ema_enc = _LearnableEMA(self.n_latent, init_alpha=0.9)

        heads = max(2, self.n_latent // 8)
        self.attn_a = _MultiheadGQA(self.n_latent, heads)
        self.attn_b = _MultiheadGQA(self.n_latent, heads)

        self.attn_gain = nn.Parameter(torch.zeros(1))
        self.gate_merge = nn.Linear(2, 1)

        self.ln1 = nn.LayerNorm(self.n_latent)
        self.ffn = nn.Sequential(
            nn.Linear(self.n_latent, self.n_latent * 3),
            nn.GELU(),
            nn.Linear(self.n_latent * 3, self.n_latent),
        )
        self.ln2 = nn.LayerNorm(self.n_latent)
        self.ffn_scale = nn.Parameter(torch.zeros(1))

        self.dec_l1 = nn.LSTM(self.n_latent, self.n_hidden // 2, 1, bidirectional=True, batch_first=True)
        self.dec_l2 = nn.LSTM(self.n_hidden, self.n_hidden, 1, bidirectional=True, batch_first=True)

        dec_out_dim = self.n_hidden * 2
        self.K = 4
        self.dec_mean_k = nn.Linear(dec_out_dim, feats * self.K)
        self.dec_logvar = nn.Parameter(torch.full((feats,), -1.0))
        self.dec_gate = nn.Linear(self.n_latent, feats * self.K)

        self.event_head = nn.Linear(self.n_latent, feats, bias=False)
        self.event_shrink = _LearnableSoftThreshold(feats)
        self.event_gate = nn.Parameter(torch.tensor(-3.0))
        self.ev_gamma = nn.Parameter(torch.zeros(feats))

    def _rms(self, x, eps=1e-8):
        return (x.pow(2).mean(dim=-1, keepdim=True) + eps).sqrt()

    def _first_diff(self, x):
        diff = x[:, 1:] - x[:, :-1]
        zeros = torch.zeros_like(x[:, :1])
        return torch.cat([zeros, diff], dim=1)

    def forward(self, x):
        batch_size, win_size, _ = x.shape

        h, _ = self.enc_l1(x)
        h, _ = self.enc_l2(h)

        s = self.inj(x)
        alpha = torch.sigmoid(self.inj_gate)
        h_cat = torch.cat([h, alpha * s], dim=-1)

        mu = self.to_mean(h_cat)
        logvar = self.to_logvar(h_cat)

        std = torch.sqrt(F.softplus(logvar) + 1e-8)
        z = mu + std * torch.randn_like(mu) if self.training else mu

        z_proj = self.proj_z(z)
        enc_proj = self.proj_enc(h)

        enc_smooth = self.ema_enc(enc_proj)
        z_smooth = self.ema_z(z_proj)

        enc_grad = self._first_diff(enc_smooth)
        q_a = F.normalize(enc_grad, dim=-1)
        k_a = F.normalize(enc_grad, dim=-1)
        out_a = self.attn_a(q_a, k_a, z_smooth)

        enc_dev = enc_proj - enc_smooth
        z_dev = z_proj - z_smooth
        q_b = F.normalize(enc_dev, dim=-1)
        k_b = F.normalize(enc_dev, dim=-1)
        out_b = self.attn_b(q_b, k_b, z_dev)

        weight_a = out_a.pow(2).mean(dim=-1, keepdim=True)
        weight_b = out_b.pow(2).mean(dim=-1, keepdim=True)
        gate = torch.sigmoid(self.gate_merge(torch.cat([weight_a, weight_b], dim=-1)))
        attn_out = self.attn_gain * (gate * out_a + (1 - gate) * out_b)

        scale = self._rms(attn_out).detach() / (self._rms(z_proj).detach() + 1e-8)
        out1 = self.ln1(z_proj * scale + attn_out)
        out2 = self.ln2(out1 + self.ffn_scale * self.ffn(out1))

        h_dec, _ = self.dec_l1(out2)
        h_dec, _ = self.dec_l2(h_dec)

        mu_k = self.dec_mean_k(h_dec).view(batch_size, win_size, self.n_feats, self.K)
        gate_logits = self.dec_gate(z_proj).view(batch_size, win_size, self.n_feats, self.K)
        gate_norm = (gate_logits - gate_logits.mean(-1, keepdim=True)) / (gate_logits.std(-1, keepdim=True) + 1e-5)
        gate_probs = F.softmax(gate_norm, dim=-1)
        mu_base = (mu_k * gate_probs).sum(dim=-1)

        z_spike = self._first_diff(z_proj)
        ev_raw = self.event_head(z_spike)
        ev_norm = ev_raw / (self._rms(ev_raw.detach()) + 1e-8)
        ev_shrunk = self.event_shrink(ev_norm)
        ev_final = ev_shrunk * self._rms(mu_base.detach()) * torch.exp(self.ev_gamma).view(1, 1, -1)
        ev_res = torch.sigmoid(self.event_gate) * ev_final

        rec_mu = mu_base + ev_res
        rec_std = torch.sqrt(F.softplus(self.dec_logvar.view(1, 1, -1)) + 1e-4)
        return rec_mu, rec_std, mu, std, gate_probs, ev_res


class StreamVAE(BaseDetector):
    def __init__(self,
                 win_size=100,
                 feats=1,
                 latent_dim=64,
                 batch_size=128,
                 epochs=50,
                 patience=10,
                 lr=1e-3,
                 validation_size=0.2,
                 target_kl=100.0,
                 event_l1_weight=1e-3):
        super().__init__()

        self.__anomaly_score = None

        self.cuda = True
        self.device = get_gpu(self.cuda)

        self.win_size = int(win_size)
        self.batch_size = int(batch_size)
        self.epochs = int(epochs)
        self.feats = int(feats)
        self.validation_size = float(validation_size)
        self.target_kl = float(target_kl)
        self.event_l1_weight = float(event_l1_weight)

        self.model = StreamVAEModel(feats, latent_dim, 256, self.device).to(self.device)
        self.optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=1e-5)
        self.early_stopping = _EarlyStoppingTorch(patience=patience)
        self.kl_ema = None

    def _update_beta(self, current_kl):
        if self.kl_ema is None:
            self.kl_ema = current_kl
        else:
            self.kl_ema = 0.95 * self.kl_ema + 0.05 * current_kl
        err = (self.kl_ema - self.target_kl) / (self.target_kl + 1e-8)
        new_beta = self.model.beta * np.exp(0.01 * err)
        self.model.beta = float(np.clip(new_beta, 1e-6, 10.0))

    def fit(self, data):
        ts_train = data[:int((1 - self.validation_size) * len(data))]
        ts_valid = data[int((1 - self.validation_size) * len(data)):]

        train_loader = DataLoader(
            dataset=ReconstructDataset(ts_train, window_size=self.win_size, normalize=False),
            batch_size=self.batch_size,
            shuffle=True,
        )
        valid_loader = DataLoader(
            dataset=ReconstructDataset(ts_valid, window_size=self.win_size, normalize=False),
            batch_size=self.batch_size,
            shuffle=False,
        )

        for epoch in range(1, self.epochs + 1):
            self.model.train()
            avg_loss = 0.0

            loop = tqdm.tqdm(enumerate(train_loader), total=len(train_loader), leave=True)
            for idx, (batch, _) in loop:
                batch = batch.to(self.device)

                rec_mu, rec_std, z_mu, z_std, gates, ev_res = self.model(batch)

                dist = Normal(rec_mu, rec_std)
                nll = -dist.log_prob(batch).sum(dim=-1).sum(dim=1).mean()

                posterior = Normal(z_mu, z_std)
                prior = Normal(torch.zeros_like(z_mu), torch.ones_like(z_std))
                kl = kl_divergence(posterior, prior).sum(dim=(1, 2)).mean()

                entropy = -(gates * (gates + 1e-8).log()).sum(-1).mean()
                reg_entropy = 0.001 * (math.log(4) * 0.5 - entropy).relu()
                l1_events = ev_res.abs().mean()

                loss = nll + self.model.beta * kl + reg_entropy + self.event_l1_weight * l1_events

                self.optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 10.0)
                self.optimizer.step()

                self._update_beta(float(kl.item()))
                avg_loss += float(loss.item())
                loop.set_description(f"Training Epoch [{epoch}/{self.epochs}]")
                loop.set_postfix(loss=float(loss.item()), beta=self.model.beta, kl=float(kl.item()))

            if len(valid_loader) > 0:
                self.model.eval()
                avg_loss_val = 0.0
                with torch.no_grad():
                    for _, (batch, _) in enumerate(valid_loader):
                        batch = batch.to(self.device)
                        rec_mu, rec_std, z_mu, z_std, gates, ev_res = self.model(batch)

                        dist = Normal(rec_mu, rec_std)
                        nll = -dist.log_prob(batch).sum(dim=(1, 2)).mean()
                        kl = kl_divergence(
                            Normal(z_mu, z_std),
                            Normal(torch.zeros_like(z_mu), torch.ones_like(z_std)),
                        ).sum(dim=(1, 2)).mean()

                        entropy = -(gates * (gates + 1e-8).log()).sum(-1).mean()
                        reg_entropy = 0.001 * (math.log(4) * 0.5 - entropy).relu()
                        l1_events = ev_res.abs().mean()

                        loss = nll + self.model.beta * kl + reg_entropy + self.event_l1_weight * l1_events
                        avg_loss_val += float(loss.item())

                avg_loss = avg_loss_val / len(valid_loader)
            else:
                avg_loss = avg_loss / len(train_loader)

            self.early_stopping(avg_loss, self.model)
            if self.early_stopping.early_stop:
                print("   Early stopping<<<")
                break

        self.early_stopping.restore(self.model)
        return self

    def decision_function(self, data):
        test_loader = DataLoader(
            dataset=ReconstructDataset(data, window_size=self.win_size, normalize=False),
            batch_size=self.batch_size,
            shuffle=False,
        )

        self.model.eval()
        scores = []
        loop = tqdm.tqdm(enumerate(test_loader), total=len(test_loader), leave=True)
        with torch.inference_mode():
            for _, (batch, _) in loop:
                batch = batch.to(self.device)
                rec_mu, rec_std, _, _, _, _ = self.model(batch)

                dist = Normal(rec_mu, rec_std)
                log_prob = dist.log_prob(batch).sum(dim=-1)
                score_win = -log_prob.mean(dim=1)
                scores.append(score_win.detach().cpu())

        anomaly_score = torch.cat(scores, dim=0).numpy()

        if anomaly_score.shape[0] < len(data):
            pad_l = math.ceil((self.win_size - 1) / 2)
            pad_r = (self.win_size - 1) // 2
            anomaly_score = np.array(
                [anomaly_score[0]] * pad_l + list(anomaly_score) + [anomaly_score[-1]] * pad_r
            )

        self.__anomaly_score = anomaly_score
        return self.__anomaly_score

    def anomaly_score(self) -> np.ndarray:
        return self.__anomaly_score

    def param_statistic(self, save_file):
        pass