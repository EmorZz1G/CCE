from deprecated import deprecated
import numpy as np
import random

# 定义生成连续段的函数，生成的信号长度为ts_len
# 异常片段
def generate_continuous_segments(num_points, num_segments, max_length, min_length=1):
    # signal = np.random.randint(0, 2, size=num_points)
    signal = np.zeros(num_points)
    for _ in range(num_segments):
        start = np.random.randint(0, len(signal) - max_length)
        end = start + max(np.random.randint(1, max_length + 1), min_length)
        signal[start:end] = 1
    return signal


"""
创建不同类型的测试模型
"""
# short for AccQ
def accuracy_q_model(labels, q=0.1, init_seed=42):
    """准确率为q的模型，正常与异常的检测概率为prob"""

    np.random.seed(init_seed)
    random.seed(init_seed)

    # the model has a probability of prob to predict an anomaly
    num_points = len(labels)
    prob = q
    pred_prob = np.random.rand(num_points)
    # print(pred_prob)
    tmp = (pred_prob <= prob)
    # print(tmp)
    anomaly_scores = np.zeros(num_points)
    for i in range(0, num_points):
        if tmp[i] == 1:
            if labels[i] == 1:
                anomaly_scores[i] = np.random.rand() * 0.1 + 0.9
            else:
                anomaly_scores[i] = np.random.rand() * 0.05
        else:
            if labels[i] == 0:
                anomaly_scores[i] = np.random.rand()* 0.1 + 0.9
            else:
                anomaly_scores[i] = np.random.rand() * 0.05

    return anomaly_scores

# short for LowDisAccQ
def low_discrimination_accuracy_q_model(labels, q=0.1, init_seed=42):
    np.random.seed(init_seed)
    random.seed(init_seed)
    # the model has a probability of prob to predict an anomaly
    num_points = len(labels)
    prob = q
    pred_prob = np.random.rand(num_points)
    # print(pred_prob)
    tmp = (pred_prob <= prob)
    # print(tmp)
    anomaly_scores = np.zeros(num_points)
    for i in range(0, num_points):
        if tmp[i] == 1:
            if labels[i] == 1:
                anomaly_scores[i] = np.random.rand() * 0.1 + 0.6
            else:
                anomaly_scores[i] = np.random.rand() * 0.4
        else:
            if labels[i] == 0:
                anomaly_scores[i] = np.random.rand() * 0.1 + 0.6
            else:
                anomaly_scores[i] = np.random.rand() * 0.4

    return anomaly_scores

# short for PreQ-NegP
def precision_q_nagative_alert_p_model(labels, q=0.8, p=0.05, init_seed=42):
    np.random.seed(init_seed)
    random.seed(init_seed)
    scores = np.random.uniform(0, 0.1, len(labels))
    anomaly_indices = np.where(labels == 1)[0]
    precision_q = q
    nagative_alert_p = p
    # 100*precsion_q%的异常被检测到
    detected = np.random.choice(anomaly_indices, size=int(precision_q * len(anomaly_indices)), replace=False)
    scores[detected] = np.random.uniform(0.8, 1.0, len(detected))
    
    # 100*nagative_alert_p%的正常点被误报
    normal_indices = np.where(labels == 0)[0]
    false_positives = np.random.choice(normal_indices, size=int(nagative_alert_p * len(normal_indices)), replace=False)
    scores[false_positives] = np.random.uniform(0.7, 1.0, len(false_positives))
    return scores

# short for XXX-R
def noise_robust_test(labels, base_model_func, noise_std=0.1, init_seed=42):
    np.random.seed(init_seed)
    random.seed(init_seed)
    """测试模型对噪声的鲁棒性"""
    base_scores = base_model_func(labels)
    noise = np.random.normal(0, noise_std, len(base_scores))
    noisy_scores = base_scores + noise
    return np.clip(noisy_scores, 0, 1)

# import partial
from functools import partial

def create_model_scores(model_config):
    """
    model_config: dict, e.g.,
        {
            'name': 'AccQ',
            'q': 0.1,
        }
        {
            'name': 'LowDisAccQ',
            'q': 0.1,
        }
        {
            'name': 'PreQ-NegP',
            'q': 0.8,
            'p': 0.05,
        }
        {
            'name': 'AccQ-R',
            'q': 0.1,
            'noise_std': 0.1,
        }
        {
            'name': 'LowDisAccQ-R',
            'q': 0.1,
            'noise_std': 0.1,
        }
        {
            'name': 'PreQ-NegP-R',
            'q': 0.8,
            'p': 0.05,
            'noise_std': 0.1,
        }
    return: dict, e.g.,
    {
        'name': 'AccQ',
        'q': 0.1,
        'func': <function accuracy_q_model at 0x7f8c8c8c8c80>
    }
    """
    if model_config['name'] == 'AccQ':
        q = model_config.get('q', None)
        if q is None:
            raise ValueError("Model 'AccQ' requires parameter 'q'.")
        model_func = partial(accuracy_q_model, q=q)
        # 只保留必要的参数
        config = {'name': 'AccQ', 'q': q, 'func': model_func}
    elif model_config['name'] == 'LowDisAccQ':
        q = model_config.get('q', None)
        if q is None:
            raise ValueError("Model 'LowDisAccQ' requires parameter 'q'.")
        model_func = partial(low_discrimination_accuracy_q_model, q=q)
        config = {'name': 'LowDisAccQ', 'q': q, 'func': model_func}
    elif model_config['name'] == 'PreQ-NegP':
        q = model_config.get('q', None)
        p = model_config.get('p', None)
        if q is None or p is None:
            raise ValueError("Model 'PreQ-NegP' requires parameters 'q' and 'p'.")
        model_func = partial(precision_q_nagative_alert_p_model, q=q, p=p)
        config = {'name': 'PreQ-NegP', 'q': q, 'p': p, 'func': model_func}
    elif '-R' in model_config['name']:
        base_name = model_config['name'].replace('-R', '')
        base_config = model_config.copy()
        base_config['name'] = base_name
        noise_std = model_config.get('noise_std', None)
        if noise_std is None:
            raise ValueError("Robust model requires parameter 'noise_std'.")
        try:
            results = create_model_scores(base_config)
            base_model_func = results['func']
        except ValueError as e:
            raise e
        model_func = partial(noise_robust_test, base_model_func=base_model_func, noise_std=noise_std)
        # 得到基础模型的配置
        results.pop('func')  # 移除基础模型的函数引用
        results.pop('name')  # 移除基础模型的名称
        config = {'name': model_config['name'], 'noise_std': noise_std, 'func': model_func}
        config.update(results)  # 添加基础模型的配置参数
    else:
        raise ValueError(f"Unknown model name: {model_config['name']}, available models are: 'AccQ', 'LowDisAccQ', 'PreQ-NegP', and their robust versions with '-R' suffix.")
    
    return config

class ModelConfigUtils:
    def __init__(self) -> None:
        self.model_config_lists = []
        self.robust_model_config_lists = []
        self.init_model_config_lists()
        print(f"Initialized {len(self.model_config_lists)} non-robust models and {len(self.robust_model_config_lists)} robust models.")

    def get_model_list_by_name(self, model_name):
        """根据模型名称获取模型配置列表"""
        if model_name == 'AccQ':
            return self.get_AccQ_list()
        elif model_name == 'LowDisAccQ':
            return self.get_LowDisAccQ_list()
        elif model_name == 'PreQ-NegP':
            return self.get_PreQ_NegP_list()
        elif model_name == 'AccQ-R':
            return self.get_AccQ_R_list()
        elif model_name == 'LowDisAccQ-R':
            return self.get_LowDisAccQ_R_list()
        elif model_name == 'PreQ-NegP-R':
            return self.get_PreQ_NegP_R_list()
        else:
            raise ValueError(f"Unknown model name: {model_name}, available models are: 'AccQ', 'LowDisAccQ', 'PreQ-NegP', and their robust versions with '-R' suffix.")
        
    def get_all_model_wo_robust_list(self):
        """获取所有非Robust模型配置列表"""
        return self.model_config_lists
    
    def get_all_model_w_robust_list(self):
        """获取所有Robust模型配置列表"""
        return self.robust_model_config_lists

    def get_AccQ_list(self):
        """获取AccQ模型配置列表"""
        return [config for config in self.model_config_lists if config['name'] == 'AccQ']

    def get_LowDisAccQ_list(self):
        """获取LowDisAccQ模型配置列表"""
        return [config for config in self.model_config_lists if config['name'] == 'LowDisAccQ']
    
    def get_PreQ_NegP_list(self):
        """获取PreQ-NegP模型配置列表"""
        return [config for config in self.model_config_lists if config['name'] == 'PreQ-NegP']
    
    def get_AccQ_R_list(self):
        """获取AccQ-R模型配置列表"""
        return [config for config in self.robust_model_config_lists if config['name'] == 'AccQ-R']
    
    def get_LowDisAccQ_R_list(self):
        """获取LowDisAccQ-R模型配置列表"""
        return [config for config in self.robust_model_config_lists if config['name'] == 'LowDisAccQ-R']
    
    def get_PreQ_NegP_R_list(self):
        """获取PreQ-NegP-R模型配置列表"""
        return [config for config in self.robust_model_config_lists if config['name'] == 'PreQ-NegP-R']

    def init_model_config_lists(self):
        """初始化模型配置列表"""
        self.model_config_lists = self.add_model_config()
        self.robust_model_config_lists = self.add_model_config(robust=0.05) + self.add_model_config(robust=0.1)
        return self.model_config_lists, self.robust_model_config_lists
    
    def add_model_config(self, robust=0):
        model_config_lists = []
        # AccQ类型
        q_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for q in q_list:
            config = {'name': 'AccQ', 'q': q}
            if robust>0:
                config['name'] = 'AccQ-R'
                config['noise_std'] = robust
            model_config_lists.append(create_model_scores(config))
        # LowDisAccQ类型
        q_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for q in q_list:
            config = {'name': 'LowDisAccQ', 'q': q}
            if robust>0:
                config['name'] = 'LowDisAccQ-R'
                config['noise_std'] = robust
            model_config_lists.append(create_model_scores(config))
        # PreQ-NegP类型
        q_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        p_list = [0.01, 0.05, 0.1, 0.3]
        for q in q_list:
            for p in p_list:
                config = {'name': 'PreQ-NegP', 'q': q, 'p': p}
                if robust>0:
                    config['name'] = 'PreQ-NegP-R'
                    config['noise_std'] = robust
                model_config_lists.append(create_model_scores(config))
        return model_config_lists


@deprecated
def generate_random_scores(num_points, labels, typs=0, prob=0.1, init_seed=42):
    np.random.seed(init_seed)
    random.seed(init_seed)
    
    if typs == 0:
        # uniform noise
        anomaly_scores = np.random.rand(num_points)
    elif typs == 1:
        # gaussian noise
        anomaly_scores = np.random.randn(num_points)
        # min-max normalization
        anomaly_scores = (anomaly_scores - np.min(anomaly_scores)) / (np.max(anomaly_scores) - np.min(anomaly_scores))
    elif typs == 2:
        # the model has a probability of prob to predict an anomaly
        pred_prob = np.random.rand(num_points)
        # print(pred_prob)
        tmp = (pred_prob <= prob)
        # print(tmp)
        anomaly_scores = np.zeros(num_points)
        for i in range(0, num_points):
            if tmp[i] == 1:
                if labels[i] == 1:
                    anomaly_scores[i] = np.random.rand() * 0.1 + 0.9
                else:
                    anomaly_scores[i] = np.random.rand() * 0.05
            else:
                if labels[i] == 0:
                    anomaly_scores[i] = np.random.rand()* 0.1 + 0.9
                else:
                    anomaly_scores[i] = np.random.rand() * 0.05
    elif typs == 3:
        pass
                
    return anomaly_scores


configs = {
    '100k-20seg-50L': {'num_points': 100000, 'num_segments': 20, 'max_length': 60, 'min_length': 40}, # anomaly ratio: 0.01,
    '100k-200seg-50L': {'num_points': 100000, 'num_segments': 200, 'max_length': 60, 'min_length': 40}, # anomaly ratio: 0.1,
    '100k-20seg-50H': {'num_points': 100000, 'num_segments': 20, 'max_length': 99, 'min_length': 1}, # anomaly ratio: 0.01,
    '100k-200seg-50H': {'num_points': 100000, 'num_segments': 200, 'max_length': 99, 'min_length': 1}, # anomaly ratio: 0.1,
    '100k-50seg-20L': {'num_points': 100000, 'num_segments': 50, 'max_length': 30, 'min_length': 10}, # anomaly ratio: 0.01,
    '100k-500seg-20L': {'num_points': 100000, 'num_segments': 500, 'max_length': 30, 'min_length': 10}, # anomaly ratio: 0.1,
    '100k-50seg-20H': {'num_points': 100000, 'num_segments': 50, 'max_length': 39, 'min_length': 1}, # anomaly ratio: 0.01,
    '100k-500seg-20H': {'num_points': 100000, 'num_segments': 500, 'max_length': 39, 'min_length': 1}, # anomaly ratio: 0.1,
    '100k-10seg-100L': {'num_points': 100000, 'num_segments': 10, 'max_length': 110, 'min_length': 90}, # anomaly ratio: 0.01,
    '100k-100seg-100L': {'num_points': 100000, 'num_segments': 100, 'max_length': 110, 'min_length': 110}, # anomaly ratio: 0.1,
    '100k-10seg-100H': {'num_points': 100000, 'num_segments': 10, 'max_length': 199, 'min_length': 1}, # anomaly ratio: 0.01,
    '100k-100seg-100H': {'num_points': 100000, 'num_segments': 100, 'max_length': 199, 'min_length': 1}, # anomaly ratio: 0.1,
    '100k-2seg-500L': {'num_points': 100000, 'num_segments': 2, 'max_length': 550, 'min_length': 450}, # anomaly ratio: 0.01,
    '100k-20seg-500L': {'num_points': 100000, 'num_segments': 20, 'max_length': 550, 'min_length': 450}, # anomaly ratio: 0.1,
    '100k-2seg-500H': {'num_points': 100000, 'num_segments': 2, 'max_length': 999, 'min_length': 1}, # anomaly ratio: 0.01,
    '100k-20seg-500H': {'num_points': 100000, 'num_segments': 20, 'max_length': 999, 'min_length': 1}, # anomaly ratio: 0.1,

    '10k-2seg-50L': {'num_points': 10000, 'num_segments': 2, 'max_length': 60, 'min_length': 40}, # anomaly ratio: 0.01,
    '10k-20seg-50L': {'num_points': 10000, 'num_segments': 20, 'max_length': 60, 'min_length': 40}, # anomaly ratio: 0.1,
    '10k-2seg-50H': {'num_points': 10000, 'num_segments': 2, 'max_length': 99, 'min_length': 1}, # anomaly ratio: 0.01,
    '10k-20seg-50H': {'num_points': 10000, 'num_segments': 20, 'max_length': 99, 'min_length': 1}, # anomaly ratio: 0.1,
    '10k-5seg-20L': {'num_points': 10000, 'num_segments': 5, 'max_length': 30, 'min_length': 10}, # anomaly ratio: 0.01,
    '10k-50seg-20L': {'num_points': 10000, 'num_segments': 50, 'max_length': 30, 'min_length': 10}, # anomaly ratio: 0.1,
    '10k-5seg-20H': {'num_points': 10000, 'num_segments': 5, 'max_length': 39, 'min_length': 1}, # anomaly ratio: 0.01,
    '10k-50seg-20H': {'num_points': 10000, 'num_segments': 50, 'max_length': 39, 'min_length': 1}, # anomaly ratio: 0.1,
    '10k-1seg-100L': {'num_points': 10000, 'num_segments': 1, 'max_length': 110, 'min_length': 90}, # anomaly ratio: 0.01,
    '10k-10seg-100L': {'num_points': 10000, 'num_segments': 10, 'max_length': 110, 'min_length': 110}, # anomaly ratio: 0.1,
    '10k-1seg-100H': {'num_points': 10000, 'num_segments': 1, 'max_length': 199, 'min_length': 1}, # anomaly ratio: 0.01,
    '10k-10seg-100H': {'num_points': 10000, 'num_segments': 10, 'max_length': 199, 'min_length': 1}, # anomaly ratio: 0.1,
    '10k-2seg-500L': {'num_points': 10000, 'num_segments': 2, 'max_length': 550, 'min_length': 450}, # anomaly ratio: 0.1,
    '10k-2seg-500H': {'num_points': 10000, 'num_segments': 2, 'max_length': 999, 'min_length': 1}, # anomaly ratio: 0.1,
}

CASE_NUM = len(configs)

import os
from os.path import dirname as upd

# 使用新的配置系统
try:
    from cce.config import get_datasets_path
    data_pth = get_datasets_path()
    print(f"Using datasets path from CCE config: {data_pth}")
except ImportError:
    # 如果无法导入新配置系统，使用传统方式
    file_pth = os.path.dirname(os.path.abspath(__file__))
    file_pth = upd(upd(file_pth))
    proj_pth = upd(file_pth)
    data_pth = os.path.join(proj_pth, 'datasets')
    
    # 尝试读取项目路径下的global配置文件
    glo_config = os.path.join(proj_pth, 'default_config.yaml')
    if os.path.exists(glo_config):
        import yaml
        with open(glo_config, 'r') as f:
            global_config = yaml.safe_load(f)
            datasets_path = global_config.get('datasets_path', None)
            if datasets_path is not None:
                data_pth = datasets_path
                print(f"Using datasets path from global config: {data_pth}")
    else:
        print(f"Using default datasets path: {data_pth}")

import sys
sys.path.append(proj_pth)

from src.data_utils.SimAD_data_loader2 import get_loader_segment

def generate_dataset(case_idx=0, init_seed=42):
    def get_config(case_idx):
        if not isinstance(case_idx, int):
            if case_idx in configs.keys():
                return configs[case_idx]
            else:
                raise ValueError(f"If case_idx is not an integer, it must be a key in the config dictionary. Available keys: {list(config.keys())}")
        if case_idx < 0 or case_idx >= len(configs):
            raise ValueError(f"Invalid case index, case_idx={case_idx}. It should be between 0 and {len(config) - 1}.")
        else:
            return list(configs.values())[case_idx]
        

    config = get_config(case_idx)
    num_points = config['num_points']
    num_segments = config['num_segments']
    max_length = config['max_length']
    min_length = config['min_length']
    dataset_ver = list(configs.keys())[case_idx]
    # set random seed
    np.random.seed(init_seed)
    random.seed(init_seed)
    # generate anomaly segments
    gen_seg = generate_continuous_segments(num_points, num_segments, max_length, min_length)
    return dataset_ver, gen_seg


real_world_configs = [
    {'dataset_name': 'MSL'},
    {'dataset_name': 'SMD_Ori_Pikled', 'index': "1-1"},
    {'dataset_name': 'SMD_Ori_Pikled', 'index': "2-1"},
    {'dataset_name': 'SMD_Ori_Pikled', 'index': "3-1"},
    {'dataset_name': 'PSM'},
    {'dataset_name': 'SWAT'},
    {'dataset_name': 'NIPS_TS_Creditcard'}
]

REAL_WORLD_CASE_NUM = len(real_world_configs)

extra_data_configs = [
    {'dataset_name': 'UCR', 'index': "123"},
    {'dataset_name': 'UCR', 'index': "124"},
    {'dataset_name': 'UCR', 'index': "125"},
    {'dataset_name': 'UCR', 'index': "126"},
    {'dataset_name': 'UCR', 'index': "152"}, 
    {'dataset_name': 'UCR', 'index': "153"}, 
    {'dataset_name': 'UCR', 'index': "154"}, 
    {'dataset_name': 'UCR', 'index': "155"}, 
]

EXTRA_REAL_WORLD_CASE_NUM = len(extra_data_configs)

# 测试数据集是否存在
if not os.path.exists(data_pth):
    raise ValueError(f"Datasets path {data_pth} does not exist.")
else:
    real_data_configs_ = real_world_configs.copy()
    for i, config in enumerate(real_data_configs_):
        name = config['dataset_name']
        index_ = config.get('index', 1)
        data_pth_ = os.path.join(data_pth, name)
        if not os.path.exists(data_pth_):
            # 用红色打印
            print(f"\033[91mDatasets path {data_pth_} does not exist. Test will be skipped. You can set the datasets path in CCE config or global config. Please run `cce config set-datasets-path` to set the datasets path. Details in README.md\033[0m")
            REAL_WORLD_CASE_NUM -= 1
            real_world_configs.pop(i)
    extra_data_configs_ = extra_data_configs.copy()
    for i, config in enumerate(extra_data_configs_):
        name = config['dataset_name']
        index_ = config.get('index', 1)
        data_pth_ = os.path.join(data_pth, name)
        if not os.path.exists(data_pth_):
            print(f"\033[91mDatasets path {data_pth_} does not exist. Test will be skipped. You can set the datasets path in CCE config or global config. Please run `cce config set-datasets-path` to set the datasets path. Details in README.md\033[0m")
            EXTRA_REAL_WORLD_CASE_NUM -= 1
            extra_data_configs.pop(i)
    

from functools import lru_cache



@lru_cache(maxsize=20)
def generate_real_world_dataset(case_idx=0, return_data=True):
    def get_config(case_idx):
        if not isinstance(case_idx, int):
            raise ValueError(f"case_idx must be an integer, got {type(case_idx)}. And it should be between 0 and {REAL_WORLD_CASE_NUM - 1}.")
        if case_idx < 0 or case_idx >= REAL_WORLD_CASE_NUM:
            raise ValueError(f"Invalid case index, case_idx={case_idx}. It should be between 0 and {REAL_WORLD_CASE_NUM - 1}.")
        return real_world_configs[case_idx]
    
    config = get_config(case_idx)
    # Here you would implement the logic to generate the real-world dataset based on the config
    # For now, we just return the config as a placeholder
    dataset_name = config['dataset_name']
    index_ = config.get('index', 1)
    data_pth_ = os.path.join(data_pth, dataset_name)
    dataset = get_loader_segment(index_, data_path=data_pth_, batch_size=100, win_size=100, step=100, dataset=dataset_name, ret_data=return_data)
    if config.get('index', None) is not None:
        if "SMD" in dataset_name:
            dataset_name_new = f"SMD-{index_}"
        elif "UCR" in dataset_name:
            dataset_name_new = f"UCR-{index_}"
        else:
            print(f"Dataset name {dataset_name} does not match any known patterns for index naming.")
            dataset_name_new = f"{dataset_name}-{index_}"
    else:
        dataset_name_new = f"{dataset_name}"
    
    if return_data:
        train_x, test_x, test_y = dataset.load_data()
        return dataset_name_new, train_x, test_x, test_y
    else:
        return dataset_name_new, dataset
    

    
@lru_cache(maxsize=20)
def generate_real_world_dataset_extra(case_idx=0, return_data=True):
    def get_config(case_idx):
        if not isinstance(case_idx, int):
            raise ValueError(f"case_idx must be an integer, got {type(case_idx)}. And it should be between 0 and {EXTRA_REAL_WORLD_CASE_NUM - 1}.")
        if case_idx < 0 or case_idx >= EXTRA_REAL_WORLD_CASE_NUM:
            raise ValueError(f"Invalid case index, case_idx={case_idx}. It should be between 0 and {EXTRA_REAL_WORLD_CASE_NUM - 1}.")
        return extra_data_configs[case_idx]
    
    config = get_config(case_idx)
    # Here you would implement the logic to generate the real-world dataset based on the config
    # For now, we just return the config as a placeholder
    dataset_name = config['dataset_name']
    index_ = config.get('index', 1)
    data_pth_ = os.path.join(data_pth, dataset_name)
    dataset = get_loader_segment(index_, data_path=data_pth_, batch_size=100, win_size=100, step=100, dataset=dataset_name, ret_data=return_data)
    if config.get('index', None) is not None:
        if "SMD" in dataset_name:
            dataset_name_new = f"SMD-{index_}"
        elif "UCR" in dataset_name:
            dataset_name_new = f"UCR-{index_}"
        else:
            print(f"Dataset name {dataset_name} does not match any known patterns for index naming.")
            dataset_name_new = f"{dataset_name}-{index_}"
    else:
        dataset_name_new = f"{dataset_name}"
    
    if return_data:
        train_x, test_x, test_y = dataset.load_data()
        return dataset_name_new, train_x, test_x, test_y
    else:
        return dataset_name_new, dataset