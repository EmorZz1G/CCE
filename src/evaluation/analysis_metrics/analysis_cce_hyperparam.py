import sys



import os, sys
import numpy as np

fil_pth = os.path.dirname(os.path.abspath(__file__))
proj_pth = os.path.dirname(os.path.dirname(os.path.dirname(fil_pth)))

sys.path.append(proj_pth)
from src.evaluation.eval_metrics.eval_utils import ModelConfigUtils, generate_dataset, CASE_NUM, generate_real_world_dataset, REAL_WORLD_CASE_NUM

log_pth = proj_pth
log_pth = os.path.join(log_pth, 'logs')
print(f"Project path: {proj_pth}", f"Log path: {log_pth}")
if not os.path.exists(log_pth):
    os.makedirs(log_pth)
    
sys.path.append(proj_pth)
from src.metrics.basic_metrics import basic_metricor
import time
from contextlib import contextmanager
import pandas as pd

log_data = []

import argparse


default_baseline_list = ['CCE']

args = argparse.ArgumentParser()
args.add_argument('--log_filename', '-L', type=str, default='_param_log.csv', help='The filename for the latency log.', required=False)
args.add_argument('--log_append', '-A', action='store_true', help='Whether to append to the log file instead of overwriting it.', required=False)
args.add_argument('--model_type', '-M', type=str, default='AccQ', choices=['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R'], help='The type of model to evaluate.', required=False)
args_config = args.parse_args()
baseline = default_baseline_list[0]  # 默认基线
args_config.log_filename = args_config.model_type + args_config.log_filename

log_file = os.path.join(log_pth, baseline, args_config.log_filename)
log_file_load = os.path.join(log_pth, baseline, args_config.log_filename)
out_dir = os.path.join(log_pth, 'RankEval', 'plots', 'cce_hyperparam')
if args_config.log_append:
    pass
elif os.path.exists(log_file):
    print(f"Log file {log_file} already exists.")
    args_config.log_filename += f"_{int(time.time())}.csv"
    print(f"Renaming log file to {args_config.log_filename}.")
else:
    print(f"Creating new log file: {log_file}")
    if not os.path.exists(os.path.join(log_pth, baseline)):
        os.makedirs(os.path.join(log_pth, baseline))

@contextmanager
def timer(case_name, model_name, case_seed, score_seed, model_config, metric_name):
    start_time = time.perf_counter()
    data_item = {
        'case_name': case_name,
        'model_name': model_name,
        'case_seed': case_seed,
        'score_seed': score_seed,
        'metric_name': metric_name,
    }
    model_config_tmp = model_config.copy()
    model_config_tmp.pop('func', None)  # 移除函数引用，避免序列化问题
    model_config_tmp.pop('name', None)  # 移除模型名称，避免重复
    data_item.update(model_config_tmp)
    yield data_item
    end_time = time.perf_counter()
    latency = (end_time - start_time) * 1000  # 转换为毫秒
    print(f"{case_name}: {model_name} {metric_name} latency: {latency:.2f} ms val: {data_item.get('val', 'N/A')}")
    data_item['latency'] = latency
    log_data.append(data_item)
    # 将日志数据写入csv
    df = pd.DataFrame(log_data)
    if os.path.exists(os.path.join(log_pth, baseline, args_config.log_filename)) and not args_config.log_append:
        df.to_csv(os.path.join(log_pth, baseline, args_config.log_filename), index=False, mode='w', header=True)
    else:
        if not os.path.exists(os.path.join(log_pth, baseline, args_config.log_filename)):
            df.to_csv(os.path.join(log_pth, baseline, args_config.log_filename), index=False, mode='w', header=True)
        else:
            df.to_csv(os.path.join(log_pth, baseline, args_config.log_filename), index=False, mode='a', header=False)
        

model_utils = ModelConfigUtils()

model_list = model_utils.get_model_list_by_name(args_config.model_type)

print(f"Model list: {model_list}")

def eval_latency(cnt=3):
    case_seed = 42
    for case_idx in range(CASE_NUM):
        case_seed_new = case_seed + case_idx
        for model in model_list:
            model_name = model['name']
            model_func = model['func']
            score_seed = 2025
            for e in range(cnt):
                score_seed_new = score_seed + e
                case_name, labels = generate_dataset(case_idx, init_seed=case_seed_new)
                print(f"Evaluating case: {case_name}, dataset: {labels}")
                score = model_func(labels, init_seed=score_seed_new)
                # Initialize the metricor

                confidence_list = [0.1, 0.3, 0.5, 0.7, 0.9]
                gamma_list = [1, 5, 10, 20, 30]

                metricor = basic_metricor(case_name, labels, log_pth)
                
                for conf in confidence_list:
                    for gamma in gamma_list:
                        # Evaluate with confidence
                        with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='CCE') as data_item:
                            CCE = metricor.metric_CCE(labels, score, confidence_level=conf, bayesian_scale=gamma)
                            data_item['val'] = CCE
                            data_item['tau'] = conf
                            data_item['gamma'] = gamma
                
        print(f"Finished evaluating case: {case_name}")

def eval_latency_real_world_case(cnt=3):
    case_seed = 42
    for case_idx in range(REAL_WORLD_CASE_NUM):
        case_seed_new = case_seed #+ case_idx
        for i, model in enumerate(model_list):
            # if i==0:continue
            model_name = model['name']
            model_func = model['func']
            score_seed = 2025
            for e in range(cnt):
                score_seed_new = score_seed + e
                case_name, train_x, test_x, labels = generate_real_world_dataset(case_idx, return_data=True)
                print(f"Evaluating case: {case_name}, dataset: {labels}")
                score = model_func(labels, init_seed=score_seed_new)
                # Initialize the metricor
                metricor = basic_metricor(case_name, labels, log_pth)

                if baseline == 'CCE':
                    with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='CCE') as data_item:
                        CCE = metricor.metric_CCE(labels, score)
                        data_item['val'] = CCE
                else:
                    raise ValueError("Error")
        
        print(f"Finished evaluating case: {case_name}")
        
        
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd


def plot_3d_metrics(results_df):
    # 设置中文字体
    plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
    # 设置seaborn风格
    sns.set_style("whitegrid")
    """
    绘制三个指标的3D图，X轴为tau，Y轴为gamma，Z轴为指标值
    
    参数:
        results_df: 包含tau, gamma和三个指标的数据框
    """
    # 创建一个包含3个子图的图形
    fig = plt.figure(figsize=(18, 5))
    
    # 定义要绘制的指标
    metrics = ['spearman', 'kendall', 'mean_deviation']
    titles = ['Spearman相关系数', 'Kendall相关系数', '平均偏差']
    
    # 创建自定义颜色映射，实现平滑过渡
    colors = ["#4B0082", "#0000FF", "#00FFFF", "#00FF00", "#FFFF00", "#FF0000"]
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('custom_cmap', colors, N=n_bins)
    
    for i, (metric, title) in enumerate(zip(metrics, titles), 1):
        # 创建3D子图
        ax = fig.add_subplot(1, 3, i, projection='3d')
        
        # 提取数据
        x = results_df['tau']
        y = results_df['gamma']
        z = results_df[metric]
        
        # 创建散点图
        scatter = ax.bar3d(x, y, z, dx=1,dy=1,dz=1, cmap=cmap)#, s=50, alpha=0.8, edgecolors='w', linewidth=0.5)
        
        # 添加颜色条
        cbar = fig.colorbar(scatter, ax=ax, pad=0.1)
        cbar.set_label(title)
        
        # 设置坐标轴标签
        ax.set_xlabel('tau')
        ax.set_ylabel('gamma')
        ax.set_zlabel(title)
        
        # 设置标题
        ax.set_title(title, fontsize=12, pad=20)
        
        # 设置刻度标签大小
        ax.tick_params(axis='both', which='major', labelsize=8)
        
        # 添加网格
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # 设置视角
        ax.view_init(elev=30, azim=45 + i*30)  # 每个图稍微调整视角
        
    # 调整布局
    plt.tight_layout()
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    # 保存图形（可选）
    fil = os.path.join(out_dir, 'cce_3d.jpg')
    plt.savefig(fil, dpi=400, bbox_inches='tight')
    
    # 显示图形
    plt.show()

def ana_cce_hyperparam(task_type='AccQ'):
    df = pd.read_csv(log_file_load)
    from analysis_rank import expected_ranking
    # from analysis_cce_latency import load_dataset_config
    # dataset_df = load_dataset_config()
    # df = df.merge(dataset_df, left_on='case_name', right_on='Case Name', how='left')
    # df = df.drop(columns=['Case Name'])
        
    def ensure_rank_map(values, provided_map):
        values_unique = sorted(list(set(values)), reverse=True)
        if provided_map is None or any(v not in provided_map for v in values_unique):
            return {val: i for i, val in enumerate(values_unique, start=1)}
        return provided_map
    # Import ranking evaluators with a tolerant path
    try:
        sys.path.append(proj_pth)
        from src.evaluation.eval_metrics.eval_rank_utils import get_ranking_score
    except Exception:
        from evaluation.eval_metrics.eval_rank_utils import get_ranking_score
    
    q_2rank = expected_ranking(df, task_type)[0]
    # Ensure rank maps cover the present values
    q_2rank = ensure_rank_map(df['q'].tolist(), q_2rank)

    groups = ['case_name', 'tau', 'gamma']
    results = []
    for keys, sub in df.groupby(groups):
        q_stats = sub.groupby('q')['val'].mean().reset_index()
        actual_q = [float(x) for x in q_stats.sort_values('val', ascending=False)['q'].tolist()]
        expected_q = sorted(actual_q, key=lambda q: q_2rank[q])
        score = get_ranking_score(expected_q, actual_q)
        row = {
            'case_name': keys[0] if isinstance(keys, tuple) else keys,
            'tau': keys[1] if isinstance(keys, tuple) else None,
            'gamma': keys[2] if isinstance(keys, tuple) else None,
            'spearman': round(score['spearman'], 4),
            'kendall': round(score['kendall'], 4),
            'mean_deviation': round(score['mean_deviation'], 4),
        }
        results.append(row)
    
    results_df = pd.DataFrame(results)
    results_df = results_df.groupby(['tau', 'gamma']).agg({
        'spearman': 'mean',
        'kendall': 'mean',
        'mean_deviation': 'mean'
    }).reset_index()

    results_df.to_csv(os.path.join(out_dir, f'cce_hyperparam_{task_type}.csv'), index=False)
    print(f"Results saved to {os.path.join(out_dir, f'cce_hyperparam_{task_type}.csv')}")
    # 调用绘图函数
    plot_3d_metrics(results_df)
    
if __name__ == "__main__":
    # eval_latency(cnt=3)
    print("Latency evaluation completed.")
    ana_cce_hyperparam()
