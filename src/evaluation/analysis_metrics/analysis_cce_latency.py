dataset_config1 = r'/home/zzj/projects/CCE/datasets/config_table.csv'
dataset_config2 = r'/home/zzj/projects/CCE/datasets/real_config_table.csv'

import pandas as pd
# plot
import seaborn as sns
import matplotlib.pyplot as plt

def load_dataset_config(file_path1, file_path2):
    """
    Load dataset configurations from two CSV files and merge them.
    
    Args:
        file_path1 (str): Path to the first CSV file.
        file_path2 (str): Path to the second CSV file.
        
    Returns:
        pd.DataFrame: Merged DataFrame containing dataset configurations.
    """
    df1 = pd.read_csv(file_path1)
    df2 = pd.read_csv(file_path2)
    
    # Merge the two DataFrames
    merged_df = pd.concat([df1, df2], ignore_index=True)
    
    return merged_df



def get_cce_logs(base_pth=r'/home/zzj/projects/CCE/logs/CCE'):
    """
    Get the CCE logs from the specified base path.
    
    Args:
        base_pth (str): Base path where the CCE logs are stored.
        
    Returns:
        list: List of log file paths.
    """
    import os
    import glob
    
    # Find all log files in the base path
    log_files = glob.glob(os.path.join(base_pth, '*.csv'))
    
    # concat
    df = pd.concat([pd.read_csv(f) for f in log_files], ignore_index=True)
    print(f"Found {len(log_files)} log files.")
    return df

fig_size = (5, 4)

def ana_cce_df1(df):
    df2 = df.copy()
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=fig_size)
    task_order =  ['AccQ','AccQ-R', 'LowDisAccQ', 'LowDisAccQ-R',  'PreQ-NegP', 'PreQ-NegP-R']
    ax = sns.violinplot(
        x='model_name', 
        y='latency', 
        hue='model_name', 
        order=task_order,  # 指定x轴的顺序
        data=df2,
        palette='pastel',
        split=False,  # 不拆分小提琴图
        inner='quartile',  # 在小提琴内部显示四分位数
        linewidth=1,
    )
    outpth = r'/home/zzj/projects/CCE/logs/RankEval/plots/cce_latency_task.jpg'
    plt.xticks(rotation=0, ha='center', fontsize=7)
    plt.yticks(fontsize=8)
    plt.xlabel('Task Name', fontsize=9)
    plt.ylabel('Latency (ms)', fontsize=9)
    plt.title('Latency Distribution in Different Tasks', fontsize=10)
    plt.tight_layout()
    plt.savefig(outpth, dpi=400, bbox_inches='tight')
    plt.show()

def ana_cce_df2(df):
    df2 = df.copy()
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=fig_size)
    ax = sns.violinplot(
        x='TS Length', 
        y='latency', 
        hue='TS Length', 
        data=df2,
        palette='pastel',
        split=False,  # 不拆分小提琴图
        inner='quartile',  # 在小提琴内部显示四分位数
        linewidth=1,
        legend=False,  # 不显示图例
    )
    outpth = r'/home/zzj/projects/CCE/logs/RankEval/plots/cce_latency_ts_len.jpg'
    plt.xticks(rotation=0, ha='center', fontsize=7)
    plt.yticks(fontsize=8)
    plt.xlabel('TS Length', fontsize=9)
    plt.ylabel('Latency (ms)', fontsize=9)
    plt.title('Latency Distribution in Different TS Length', fontsize=10)
    # plt.legend(title='TS Length', fontsize=8, loc='upper left',
            #    title_fontsize='9')
    # 图例标题的字体大小
    plt.tight_layout()
    plt.savefig(outpth, dpi=400, bbox_inches='tight')
    plt.show()

def ana_cce_df3(df):
    df2 = df.copy()
    seg_list = [1, 2, 10, 20, 50, 100, 200, 500]
    df2 = df2[df2['Segments'].isin(seg_list)]
    
    # 计算每个分段的平均异常长度（优化空值判断）
    def avg_anomaly_length(row):
        if 'Avg Anomaly Length' in row and pd.notna(row['Avg Anomaly Length']):
            return row['Avg Anomaly Length']
        else:
            min_seg_len = row['Min Seg Length']
            max_seg_len = row['Max Seg Length']
            # if pd.notna(min_seg_len) and pd.notna(max_seg_len):
            if min_seg_len is not None and max_seg_len is not None:
                print(f"Calculating Avg Anomaly Length for Segments: {row['Segments']}, Min: {min_seg_len}, Max: {max_seg_len}")
                return (min_seg_len + max_seg_len) / 2
            else:
                raise ValueError("Min Seg Length and Max Seg Length must be provided.")
    
    # df2['Avg Anomaly Length'] = df2.apply(avg_anomaly_length, axis=1)
    df2['TS Length'] = df2['TS Length'].astype(str)
    
    sns.set_theme(style="whitegrid")
    # 创建共享Y轴的子图
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4), sharey=True)
    
    # 第一个子图：TS Length=10000
    sns.violinplot(
        x='Segments', 
        y='latency', 
        hue='Segments', 
        data=df2[df2['TS Length'] == '10000'],  # 注意这里是字符串匹配
        palette='pastel',
        split=False,
        inner='quartile',
        linewidth=1,
        ax=ax1  # 指定子图轴
    )
    ax1.set_xticks(range(len(seg_list)))
    ax1.set_xticklabels(seg_list, rotation=0, ha='center', fontsize=8)
    ax1.set_xlabel('Segments', fontsize=9)  # 修正X轴标签
    ax1.set_ylabel('Latency (ms)', fontsize=9)
    ax1.set_title('TS Length = 10000', fontsize=10)  # 标题区分TS长度
    ax1.legend_.remove()  # 移除重复图例
    
    # 第二个子图：TS Length=100000
    sns.violinplot(
        x='Segments', 
        y='latency', 
        hue='Segments', 
        data=df2[df2['TS Length'] == '100000'],  # 注意这里是字符串匹配
        palette='pastel',
        split=False,
        inner='quartile',
        linewidth=1,
        ax=ax2  # 指定子图轴
    )
    ax2.set_xticks(range(len(seg_list)))
    ax2.set_xticklabels(seg_list, rotation=0, ha='center', fontsize=8)
    ax2.set_xlabel('Segments', fontsize=9)  # 修正X轴标签
    ax2.set_ylabel('')  # 共享Y轴，右侧不显示Y标签
    ax2.set_title('TS Length = 100000', fontsize=10)  # 标题区分TS长度
    ax2.legend(title='Segments', fontsize=8, loc='upper left', title_fontsize='9')
    
    # 调整布局避免重叠
    plt.tight_layout()
    
    outpth = r'/home/zzj/projects/CCE/logs/RankEval/plots/cce_latency_seg2.jpg'
    plt.savefig(outpth, dpi=400, bbox_inches='tight')
    plt.show()
    plt.close(fig)  # 关闭图形以释放内存


def ana_cce_df4(df):
    df2 = df.copy()
    seg_list = [1, 2, 10, 20, 50, 100, 200, 500]
    df2 = df2[df2['Segments'].isin(seg_list)]
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=fig_size)
    ax = sns.violinplot(
        x='Segments', 
        y='latency', 
        hue='TS Length', 
        data=df2,
        palette='pastel',
        split=True,  # 不拆分小提琴图
        inner='quartile',  # 在小提琴内部显示四分位数
        linewidth=1,
        cut=0,
    )
    outpth = r'/home/zzj/projects/CCE/logs/RankEval/plots/cce_latency_seg.jpg'
    plt.yscale('log',base=10)  # 使用对数坐标轴
    plt.xticks(rotation=0, ha='center', fontsize=8)
    plt.yticks(fontsize=8)
    plt.xlabel('Segments', fontsize=9)
    plt.ylabel('Latency (ms) - Log Scale', fontsize=9)
    plt.title('Latency Distribution in Different Segments', fontsize=10)
    plt.legend(title='TS Length', fontsize=8,
               title_fontsize='9')
    plt.tight_layout()
    # 图例标题的字体大小
    plt.savefig(outpth, dpi=400, bbox_inches='tight')
    plt.show()

def main():
    dataset_df = load_dataset_config(dataset_config1, dataset_config2)
    logs_df = get_cce_logs()
    new_df = logs_df.merge(dataset_df, left_on='case_name', right_on='Case Name', how='left')
    print(new_df.columns)
    # ana_cce_df1(new_df)
    # ana_cce_df2(new_df)
    # ana_cce_df3(new_df)
    ana_cce_df4(new_df)

main()