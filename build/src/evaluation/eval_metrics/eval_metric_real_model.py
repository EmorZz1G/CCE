default_baseline_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC', 'PATE']
model_list = ['LOF', 'IForest', 'PCA', 'LSTMAD', 'USAD', 'AnomalyTransformer', 'TimesNet', 'Donut']

Unsupervise_AD_Pool = ['FFT', 'SR', 'NORMA', 'Series2Graph', 'Sub_IForest', 'IForest', 'LOF', 'Sub_LOF', 'POLY', 'MatrixProfile', 'Sub_PCA', 'PCA', 'HBOS', 'Sub_HBOS', 'KNN', 'Sub_KNN','KMeansAD', 'KMeansAD_U', 'KShapeAD', 'COPOD', 'CBLOF', 'COF', 'EIF', 'RobustPCA', 'Lag_Llama', 'TimesFM', 'Chronos', 'MOMENT_ZS', 'Random']
Semisupervise_AD_Pool = ['Left_STAMPi', 'SAND', 'MCD', 'Sub_MCD', 'OCSVM', 'Sub_OCSVM', 'AutoEncoder', 'CNN', 'LSTMAD', 'TranAD', 'USAD', 'OmniAnomaly', 'AnomalyTransformer', 'TimesNet', 'FITS', 'Donut', 'OFA', 'MOMENT_FT', 'M2N2', 'DualTF']

model_sets = set(Unsupervise_AD_Pool+Semisupervise_AD_Pool)

abs_file = __file__
import os
import pandas as pd

proj_pth = os.path.abspath(os.path.join(os.path.dirname(abs_file), '..', '..', '..'))
import sys
sys.path.append(proj_pth)

# from src.evaluation.eval_metrics.eval_utils import generate_real_world_dataset, REAL_WORLD_CASE_NUM
from src.evaluation.eval_metrics.eval_utils import generate_real_world_dataset_extra as generate_real_world_dataset, EXTRA_REAL_WORLD_CASE_NUM as REAL_WORLD_CASE_NUM
from src.utils.model_wrapper import run_Unsupervise_AD, run_Semisupervise_AD
from src.metrics.basic_metrics import basic_metricor, METRIC_LIST

log_dir = os.path.join(proj_pth, 'logs', 'RealWorldAD')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
output_path = os.path.join(log_dir, 'real_model_performance1.csv')

import argparse
import time

argparser = argparse.ArgumentParser()
argparser.add_argument('--model_list', type=str, nargs='+', default=model_list, help='List of models to evaluate')
argparser.add_argument('--dataset_id_list', type=int, nargs='+', default=list(range(REAL_WORLD_CASE_NUM)), help='List of dataset IDs to evaluate')
argparser.add_argument('--metric_list', type=str, nargs='+', default=default_baseline_list, help='List of metrics to compute')
argparser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
argparser.add_argument('--save_score', action='store_true', help='Whether to save the scores to a CSV file')

args = argparser.parse_args()

model_list = args.model_list
dataset_id_list = args.dataset_id_list
metric_list = args.metric_list
seed = args.seed
save_score = args.save_score

if seed >= 0:
    print(f"Setting random seed to {seed} for reproducibility.")
    import random
    random.seed(seed)
    import numpy as np
    np.random.seed(seed)
    import torch
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


global_dataframe = []

if set(dataset_id_list).issubset(set(range(REAL_WORLD_CASE_NUM))) is False:
    print(f"数据集ID列表中包含不支持的ID: {dataset_id_list}")
    raise ValueError(f"dataset_id_list should be a subset of {list(range(REAL_WORLD_CASE_NUM))}")

if not set(model_list).issubset(model_sets):
    notin = set(model_list) - model_sets
    print(f"模型列表中包含不支持的模型: {notin}")
    raise ValueError(f"model_list should be a subset of {model_sets}, but got {notin}")

def main():
    global global_dataframe
    bm = basic_metricor()
    def ana_model_by_metrics(model_name, dataset_name_new, score, test_y, metric):
        pred = bm.get_pred(score)
        result_dict = {}
        st = time.perf_counter()
        score = bm.metric_by_name(metric, test_y, score, pred)
        et = time.perf_counter()
        print(f"  {metric}计算耗时: {et - st:.4f}秒")
        latency = (et - st)*1000  # 转换为毫秒
        result_dict['case_name'] = dataset_name_new
        result_dict['model_name'] = model_name
        result_dict['metric_name'] = metric
        result_dict['val'] = score
        result_dict['latency'] = latency
        return result_dict

    for model in model_list:
        print(f"\n正在处理模型: {model}")
        for dataset_id in dataset_id_list:
            print(f"  处理数据集ID: {dataset_id}")
            # 清空显存
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            dataset_name_new, score, test_y, model_name = run_model(model, dataset_id)
            for metric in metric_list:
                if metric not in METRIC_LIST:
                    raise ValueError(f"Metric {metric} is not supported. Supported metrics are: {METRIC_LIST}")
                result_dict = ana_model_by_metrics(model_name, dataset_name_new, score, test_y, metric)
                global_dataframe.append(result_dict)
            if os.path.exists(output_path):
                df = pd.DataFrame(global_dataframe).to_csv(output_path, index=False, mode='a', header=False)
            else:
                df = pd.DataFrame(global_dataframe).to_csv(output_path, index=False)

def run_model(model_name, dataset_id):
    dataset_name_new, train_x, test_x, test_y = generate_real_world_dataset(dataset_id)
    print(f"  数据集名称: {dataset_name_new}, 模型名称: {model_name}, 训练集: {train_x.shape} 测试集大小: {test_x.shape} Label: {test_y.shape}")
    if model_name in Unsupervise_AD_Pool:
        score = run_Unsupervise_AD(model_name, test_x)
    elif model_name in Semisupervise_AD_Pool:
        score = run_Semisupervise_AD(model_name, train_x, test_x)
    else:
        raise ValueError(f"Model {model_name} is not in the supported model pools.")
    if save_score:
        fil_name = f'{dataset_name_new}_{model_name}_score.npy'
        np.save(os.path.join(log_dir, fil_name), score)
        test_x = test_x.cpu().numpy() if isinstance(test_x, torch.Tensor) else test_x
        test_y = test_y.cpu().numpy() if isinstance(test_y, torch.Tensor) else test_y
        test_x_name = f'{dataset_name_new}_test_x.npy'
        test_y_name = f'{dataset_name_new}_test_y.npy'
        if not os.path.exists(os.path.join(log_dir, test_x_name)):
            np.save(os.path.join(log_dir, test_x_name), test_x)
        if not os.path.exists(os.path.join(log_dir, test_y_name)):
            np.save(os.path.join(log_dir, test_y_name), test_y)
        
    return dataset_name_new, score, test_y, model_name


if __name__ == "__main__":
    print("开始运行真实模型评估指标分析...")
    main()
    