default_baseline_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
import os
proj_pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
log_dir = os.path.join(proj_pth, 'logs')

plots_dir = os.path.join(log_dir, 'RankEval', 'plots')
# Ensure the plots directory exists
if not os.path.exists(plots_dir):
    os.makedirs(plots_dir)

import sys
import matplotlib.colors as mcolors
sys.path.append(proj_pth)

from src.evaluation.eval_metrics.eval_utils import configs

import argparse
import pandas as pd
from typing import List, Union
import seaborn as sns
import matplotlib.pyplot as plt

argparser = argparse.ArgumentParser(description="Run latency-based evaluation benchmark for model metrics.")
argparser.add_argument('--metric_list', type=str, nargs='+', default=default_baseline_list, help='List of baselines to evaluate.')
argparser.add_argument('--task_list', type=str, nargs='+', default=model_type_list, help='List of model types to evaluate.')

def ana_latency_all(metric_list, task_list):
    # 对任意指标在所有数据集，所有任务类型上计算
    sns.set_theme(style="whitegrid")
    
    # 收集所有数据
    all_data = None
    for metric in metric_list:
        metric_dir = os.path.join(log_dir, metric)
        for task in task_list:
            metric_file = os.path.join(metric_dir, f'{task}_log.csv')
            latency_df = pd.read_csv(metric_file)
            # case_name in configs
            latency_df = latency_df[latency_df['case_name'].isin(configs.keys())]

            # 提取需要的列并添加任务类型标识
            sub_df = latency_df[['metric_name', 'latency', 'model_name']].copy()
            sub_df['task_type'] = task  # 添加任务类型列用于分组
            
            
            # 合并数据
            if all_data is None:
                all_data = sub_df
            else:
                all_data = pd.concat([all_data, sub_df], ignore_index=True)
    
    # 创建大图
    plt.figure(figsize=(10, 6))
    
    # 使用小提琴图展示分布特征
    ax = sns.violinplot(
        x='metric_name', 
        y='latency', 
        hue='metric_name', 
        data=all_data,
        palette='pastel',
        split=False,  # 不拆分小提琴图
        inner='quartile',  # 在小提琴内部显示四分位数
        linewidth=1,
    )

    # 获取每个小提琴的颜色
    violin_colors = [patch.get_facecolor() for patch in ax.collections]

    # 调整均值线样式
    for i, line in enumerate(ax.lines):
        # 每4条线为一组，第4条是均值线
        if i % 3 == 2:
            # 计算对应的小提琴索引
            violin_idx = i // 3
            # 获取对应小提琴的颜色
            base_color = violin_colors[violin_idx]
            
            # 将RGBA颜色转换为HSV，降低亮度（使其更深）
            rgb = mcolors.rgb_to_hsv(mcolors.to_rgb(base_color))
            rgb = (rgb[0], min(rgb[1] * 2, 1), min(rgb[2]*0.8,1))  # 亮度降低30%
            darker_color = mcolors.hsv_to_rgb(rgb)
            
            # 设置均值线样式
            line.set_linewidth(1.5)
            line.set_color(darker_color)
    
    # 叠加散点图展示原始数据点，增强分布感知
    sns.stripplot(
        x='metric_name', 
        y='latency', 
        hue='metric_name', 
        data=all_data,
        palette='dark', 
        size=2,  # 进一步减小点的大小
        alpha=0.2,  # 降低透明度，密集区域更清晰
        dodge=False,  # 关闭偏移，确保在中心
        jitter=0.01,  # 适当增加抖动范围，减少重叠
        ax=ax,
    )
    grouped_data = all_data.groupby('metric_name')['latency'].mean().reset_index()
    print(grouped_data)  # 确认数据是否存在且格式正确
    sns.lineplot(
        x='metric_name', 
        y='latency', 
        hue='metric_name', 
        data=grouped_data,
        linewidth=10, 
        ax=ax,
        # legend=False  # 不重复图例
    )
    
    # 设置y轴为对数刻度，更好地展示可能存在的大范围值
    ax.set_yscale('log', base=10)

    y_min, y_max = all_data['latency'].min(), all_data['latency'].max()
    ax.set_ylim(y_min * 10**-1, y_max*10**1)  # 扩展范围，避免边缘被截断
    
    # 添加整体平均值线
    overall_mean = all_data['latency'].mean()
    h1 = ax.axhline(
        overall_mean, 
        color='red', 
        linestyle='--', 
        linewidth=1.5,
        alpha=0.7,
        label=f'Overall Mean: {overall_mean:.2f} ms'
    )

    ax.legend([h1], [h1.get_label()], fontsize=10,loc='upper right')
    
    # 设置标题和标签
    plt.title('Latency Distribution Across All Metrics and Model Types', fontsize=12)
    plt.xlabel('Metric', fontsize=10)
    plt.ylabel('Latency (ms) - Log2 Scale', fontsize=10)
    
    # 旋转x轴标签避免重叠
    plt.xticks(rotation=0, ha='center', fontsize=8)
    plt.yticks(fontsize=10)
    
    # 调整图例
    handles, labels = ax.get_legend_handles_labels()
    # 只保留一套图例（小提琴图和散点图会各生成一套）
    unique_labels = list(dict.fromkeys(labels))  # 保持顺序去重
    unique_handles = [handles[labels.index(label)] for label in unique_labels]
    # ax.legend(unique_handles, unique_labels, title='Model Type', 
    #           fontsize=10, title_fontsize=12, loc='upper right')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(plots_dir, 'latency_dist.jpg'), bbox_inches='tight', dpi=400)
    
    # 显示图片
    plt.show()
        

def ana_latency_v2(metric_list, task='AccQ'):
    # 对任意指标在所有数据集，所有任务类型上计算
    sns.set_theme(style="whitegrid")
    
    # 收集所有数据
    all_data = None
    for metric in metric_list:
        metric_dir = os.path.join(log_dir, metric)
        metric_file = os.path.join(metric_dir, f'{task}_log.csv')
        latency_df = pd.read_csv(metric_file)
        # case_name in configs
        latency_df = latency_df[latency_df['case_name'].isin(configs.keys())]

        # 提取需要的列并添加任务类型标识
        sub_df = latency_df[['metric_name', 'latency', 'model_name']].copy()
        sub_df['task_type'] = task  # 添加任务类型列用于分组
        
        
        # 合并数据
        if all_data is None:
            all_data = sub_df
        else:
            all_data = pd.concat([all_data, sub_df], ignore_index=True)
    
    # 创建大图
    plt.figure(figsize=(10, 6))
    
    # 使用小提琴图展示分布特征
    ax = sns.violinplot(
        x='metric_name', 
        y='latency', 
        hue='metric_name', 
        data=all_data,
        palette='pastel',
        split=False,  # 不拆分小提琴图
        inner='quartile',  # 在小提琴内部显示四分位数
        linewidth=1,
    )

    # 获取每个小提琴的颜色
    violin_colors = [patch.get_facecolor() for patch in ax.collections]

    # 调整线样式
    for i, line in enumerate(ax.lines):
        if i % 3 == 1:
            # 计算对应的小提琴索引
            violin_idx = i // 3
            # 获取对应小提琴的颜色
            base_color = violin_colors[violin_idx]
            
            # 将RGBA颜色转换为HSV，降低亮度（使其更深）
            rgb = mcolors.rgb_to_hsv(mcolors.to_rgb(base_color))
            rgb = (rgb[0], min(rgb[1] * 2, 1), min(rgb[2]*0.8,1))  # 亮度降低30%
            darker_color = mcolors.hsv_to_rgb(rgb)
            
            # 设置均值线样式
            line.set_linewidth(1.5)
            line.set_color(darker_color)
    
    # 叠加散点图展示原始数据点，增强分布感知
    sns.stripplot(
        x='metric_name', 
        y='latency', 
        hue='metric_name', 
        data=all_data,
        palette='dark', 
        size=2,  # 进一步减小点的大小
        alpha=0.2,  # 降低透明度，密集区域更清晰
        dodge=False,  # 关闭偏移，确保在中心
        jitter=0.01,  # 适当增加抖动范围，减少重叠
        legend=False,
        ax=ax,
    )
    # grouped_data = all_data.groupby('metric_name')['latency'].mean().reset_index()
    # print(grouped_data)  # 确认数据是否存在且格式正确
    # sns.lineplot(
    #     x='metric_name', 
    #     y='latency', 
    #     hue='metric_name', 
    #     data=grouped_data,
    #     linewidth=10, 
    #     ax=ax,
    #     # legend=False  # 不重复图例
    # )
    
    # 设置y轴为对数刻度，更好地展示可能存在的大范围值
    ax.set_yscale('log', base=10)

    y_min, y_max = all_data['latency'].min(), all_data['latency'].max()
    ax.set_ylim(y_min * 10**-1, y_max*10**1)  # 扩展范围，避免边缘被截断
    
    # 添加整体平均值线
    overall_mean = all_data['latency'].mean()
    h1 = ax.axhline(
        overall_mean, 
        color='red', 
        linestyle='--', 
        linewidth=1.5,
        alpha=0.7,
        label=f'Overall Mean: {overall_mean:.2f} ms'
    )

    # 添加每个指标的均值线
    metric_mean = all_data.groupby('metric_name')['latency'].mean().reset_index()
    sns.lineplot(
        x='metric_name',
        y='latency',
        data=metric_mean,
        ax=ax,
        linewidth=1.5,
        linestyle='-',
        color='green',
        alpha=0.7,
        label='Mean per Metric'
    )
    # handles, labels = ax.get_legend_handles_labels()
    # 1. 获取小提琴图的句柄和标签（每个指标对应一个）
    violin_handles = ax.collections[:len(metric_list)]  # 前N个是小提琴的句柄
    violin_labels = metric_list  # 指标名称
    new_labels=[]
    new_handles = []
    print(metric_mean)
    for handle, label in zip(violin_handles, violin_labels):
        # 正确获取均值（修正索引）
        print(f"Processing metric: {label}")
        mean_val = metric_mean.loc[metric_mean['metric_name'] == label, 'latency']
        print(f"Metric: {label}, Mean Latency: {mean_val.values[0] if not mean_val.empty else 'N/A'}")
        new_labels.append(f'{label}: {mean_val.values[0]:.2f} ms')
        new_handles.append(handle)  # 保留小提琴的颜色句柄
    
    # 3. 按metric_list顺序排序（确保与x轴一致）
    sorted_pairs = sorted(zip(new_handles, new_labels), 
                         key=lambda x: metric_list.index(x[1].split(':')[0].strip()))
    sorted_handles, sorted_labels = zip(*sorted_pairs)
    
    # 4. 组合整体均值线和指标图例
    final_handles = [h1] + list(sorted_handles)
    final_labels = [h1.get_label()] + list(sorted_labels)
    
    # 5. 设置最终图例
    ax.legend(final_handles, final_labels, fontsize=8, loc='upper left')
    
    # 设置标题和标签
    plt.title('Latency Distribution', fontsize=12)
    plt.xlabel('Metric', fontsize=10)
    plt.ylabel('Latency (ms) - Log2 Scale', fontsize=10)
    
    # 旋转x轴标签避免重叠
    plt.xticks(rotation=0, ha='center', fontsize=8)
    plt.yticks(fontsize=10)
    
    # 调整图例
    handles, labels = ax.get_legend_handles_labels()
    # 只保留一套图例（小提琴图和散点图会各生成一套）
    unique_labels = list(dict.fromkeys(labels))  # 保持顺序去重
    unique_handles = [handles[labels.index(label)] for label in unique_labels]
    # ax.legend(unique_handles, unique_labels, title='Model Type', 
    #           fontsize=10, title_fontsize=12, loc='upper right')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig(os.path.join(plots_dir, 'latency_dist_v2.jpg'), bbox_inches='tight', dpi=400)
    
    # 显示图片
    plt.show()
            

def ana_latency(metric_list=
 ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', "UAff-F1", 'PATE', 'AUC-ROC', 'VUS-ROC']
,task='AccQ', 
 low_latency_group=None, 
 medium_latency_group=None, 
 high_latency_group=None):
    # 对任意指标在所有数据集，单个任务类型上计算
    
    # 如果没有指定分组，使用默认分组
    if low_latency_group is None:
        low_latency_group = ['CCE', 'F1', 'F1-PA', 'Reduced-F1']
    if medium_latency_group is None:
        medium_latency_group = ['R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC']
    if high_latency_group is None:
        high_latency_group = ['PATE', 'VUS-ROC']
    
    # 验证所有指标都被包含在分组中
    all_grouped = set(low_latency_group + medium_latency_group + high_latency_group)
    all_metrics = set(metric_list)
    if all_grouped != all_metrics:
        missing = all_metrics - all_grouped
        extra = all_grouped - all_metrics
        if missing:
            print(f"警告：以下指标未包含在任何组中: {missing}")
        if extra:
            print(f"警告：以下指标不在metric_list中: {extra}")
    
    # 收集所有数据
    all_data = None
    for metric in metric_list:
        metric_dir = os.path.join(log_dir, metric)
        metric_file = os.path.join(metric_dir, f'{task}_log.csv')
        latency_df = pd.read_csv(metric_file)
        # case_name in configs
        latency_df = latency_df[latency_df['case_name'].isin(configs.keys())]

        # 提取需要的列并添加任务类型标识
        sub_df = latency_df[['metric_name', 'latency', 'model_name']].copy()
        sub_df['task_type'] = task  # 添加任务类型列用于分组
        
        # 合并数据
        if all_data is None:
            all_data = sub_df
        else:
            all_data = pd.concat([all_data, sub_df], ignore_index=True)
    
    # 计算每个指标的平均时延和中位数时延
    metric_stats = all_data.groupby('metric_name')['latency'].agg(['mean', 'median']).sort_values('mean')
    print("各指标时延统计:")
    print(metric_stats)
    
    # 使用指定的分组
    group_metrics = [low_latency_group, medium_latency_group, high_latency_group]
    
    print(f"\n分组结果:")
    print(f"低时延组 ({len(low_latency_group)}个): {low_latency_group}")
    print(f"中时延组 ({len(medium_latency_group)}个): {medium_latency_group}")
    print(f"高时延组 ({len(high_latency_group)}个): {high_latency_group}")
    
    # 创建三个子图，每个组一个
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'Latency Distribution by Groups - Task: {task}', fontsize=16, y=0.95)
    
    # 定义颜色方案
    colors = ['#2E8B57', '#4682B4', '#CD5C5C']  # 绿色、蓝色、红色
    group_names = ['Low Latency', 'Medium Latency', 'High Latency']
    
    for i, (ax, metrics, group_name, color) in enumerate(zip(axes, group_metrics, group_names, colors)):
        # 筛选当前组的数据
        group_data = all_data[all_data['metric_name'].isin(metrics)]
        
        if len(group_data) > 0:
            # 绘制小提琴图，显示中位数
            sns.violinplot(
                x='metric_name',
                y='latency',
                data=group_data,
                ax=ax,
                palette='Set3',
                inner='box',  # 改为'box'显示中位数和四分位数
                linewidth=1
            )
            
            # 叠加散点图
            sns.stripplot(
                x='metric_name',
                y='latency',
                data=group_data,
                ax=ax,
                size=3,
                alpha=0.4,
                color='darkblue',
                jitter=0.1
            )
            
            # 添加均值线（红色虚线）
            group_means = group_data.groupby('metric_name')['latency'].mean()
            for j, metric in enumerate(metrics):
                if metric in group_means.index:
                    mean_val = group_means[metric]
                    # 计算x轴位置
                    x_pos = j
                    ax.axhline(y=mean_val, xmin=(x_pos+0.1)/len(metrics), xmax=(x_pos+0.9)/len(metrics), 
                              color='red', linestyle='--', linewidth=2, alpha=0.8, label='Mean' if j==0 else "")
            
            # 设置y轴为对数刻度
            # ax.set_yscale('log', base=10)
            
            # 设置标题和标签
            ax.set_title(f'{group_name} Group', fontsize=14, fontweight='bold', color=color)
            ax.set_xlabel('Metric', fontsize=12)
            if i == 0:  # 只在最左边的子图设置y轴标签
                ax.set_ylabel('Latency (ms)', fontsize=12)
            
            # 旋转x轴标签
            ax.tick_params(axis='x', rotation=45, labelsize=10)
            ax.tick_params(axis='y', labelsize=10)
            
            # 添加网格
            ax.grid(True, alpha=0.3)
            
            # 设置y轴范围
            y_min, y_max = group_data['latency'].min(), group_data['latency'].max()
            if y_min > 0 and y_max > 0:
                ax.set_ylim(y_min * 0.5, y_max * 2)
                
            # 添加图例说明
            if i == 0:
                ax.legend(['Mean'], loc='upper right', fontsize=10)
        else:
            ax.text(0.5, 0.5, 'No data available', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=14)
            ax.set_title(f'{group_name} Group', fontsize=14, fontweight='bold', color=color)
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    output_file = os.path.join(plots_dir, f'latency_groups_{task}.jpg')
    plt.savefig(output_file, bbox_inches='tight', dpi=400)
    print(f"\n图片已保存到: {output_file}")
    
    # 显示图片
    plt.show()
    
    # 返回分组信息供进一步分析
    return {
        'low_latency': low_latency_group,
        'medium_latency': medium_latency_group,
        'high_latency': high_latency_group,
        'metric_stats': metric_stats
    }

if __name__ == "__main__":
    args = argparser.parse_args()
    metric_list = args.metric_list
    task_list = args.task_list
    
    # 调用函数进行分析
    # ana_latency_all(metric_list, task_list)
    # 新版：每个指标一个子图并高亮CCE
    # ana_latency_all_v2(metric_list, task_list)
    
    # 分析单个任务类型的时延分组
    
    # 使用默认分组（根据你的预期）
    # print("使用默认分组进行分析...")


    v2_list = ['CCE', 'AUC-ROC', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', "UAff-F1", 'PATE', 'VUS-ROC']
    result = ana_latency_v2(v2_list)
    
    # 如果需要自定义分组，可以这样调用：
    # custom_low = ['CCE', 'F1', 'F1-PA',  'AUC-ROC', 'Reduced-F1']
    # custom_medium = ['R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1',]
    # custom_high = ['PATE', 'VUS-ROC']
    # result = ana_latency(low_latency_group=custom_low, 
    #                     medium_latency_group=custom_medium, 
    #                     high_latency_group=custom_high)

    
    print("\n所有分析完成！")