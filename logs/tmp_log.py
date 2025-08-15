
import pandas as pd
def read_log(pth=None):
    if pth is None:
        pth = r'/home/zzj/projects/CCE/logs/AccQ-R_log.csv'
    try:
        df = pd.read_csv(pth)
        # 去除重复行
        df2 = df.drop_duplicates()
        # 重置索引
        df2.reset_index(drop=True, inplace=True)
        # saving
        print("Original number of rows:", len(df))
        print(len(df2), "rows after removing duplicates.")

        df2.to_csv(pth, index=False)
    except FileNotFoundError:
        print(f"File not found: {pth}")
        return pd.DataFrame()  # Return an empty DataFrame if the file does not exist

# read_log()
def test_time():
    import time
    start_time = time.time()
    # 模拟一些处理
    time.sleep(2)  # 假设处理耗时2秒
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")

    st_time = time.perf_counter()
    time.sleep(2)  # 假设处理耗时2秒
    en_time = time.perf_counter()
    elapsed_time2 = (en_time - st_time)*1000
    print(f"Elapsed time (perf_counter): {elapsed_time2:.2f} ms")

# test_time()
def split_files():
    pth = r'/home/zzj/projects/CCE/logs/LowDisAccQ_log.csv'
    pth = r'/home/zzj/projects/CCE/logs/AccQ-R_log.csv'
    d1 = pd.read_csv(pth)
    # 找到metric_name==CCE的
    d_cce = d1[d1['metric_name'] == 'CCE']
    d_f1 = d1[d1['metric_name'] == 'F1']
    print(len(d1),len(d_cce), len(d_f1))

def cal_acc_q_r_num():
    num_model_type_list = 60 + 120
    num_exp_cnt = 3
    num_case = 30 + 7
    accq = 10 * num_exp_cnt * num_case
    print("AccQ:", accq)

    
def tmp_robust(pth = r'logs/CCE/AccQ-R_log.csv'):
    ori_pth = pth.replace('-R_', '_')
    df = pd.read_csv(pth)
    df_ori = pd.read_csv(ori_pth)
    
    print("=== 数据分析开始 ===")
    print(f"原始数据（无噪声）: {len(df_ori)} 行")
    print(f"噪声数据: {len(df)} 行")
    
    # 1. 分析不同case_name, case_seed, score_seed组合下的平均指标水平
    print("\n=== 1. 不同case下的平均指标水平 ===")
    
    # 计算无噪声情况下的平均值
    avg_ori = df_ori.groupby(['case_name', 'case_seed', 'score_seed', 'q']).agg({
        'val': 'mean',
        'latency': 'mean'
    }).reset_index()
    
    # 计算有噪声情况下的平均值
    avg_noise = df.groupby(['case_name', 'case_seed', 'score_seed', 'q', 'noise_std']).agg({
        'val': 'mean',
        'latency': 'mean'
    }).reset_index()
    
    print(f"无噪声情况下的唯一组合数: {len(avg_ori)}")
    print(f"有噪声情况下的唯一组合数: {len(avg_noise)}")
    
    # 2. 分析latency的变化
    print("\n=== 2. Latency变化分析 ===")
    
    # 计算无噪声情况下的latency统计
    latency_stats_ori = df_ori.groupby(['case_name', 'q'])['latency'].agg(['mean', 'std', 'min', 'max']).reset_index()
    print("无噪声情况下的latency统计:")
    print(latency_stats_ori.head(10))
    
    # 计算有噪声情况下的latency统计
    latency_stats_noise = df.groupby(['case_name', 'q', 'noise_std'])['latency'].agg(['mean', 'std', 'min', 'max']).reset_index()
    print("\n有噪声情况下的latency统计:")
    print(latency_stats_noise.head(10))
    
    # 3. 分析噪声对指标分数的影响
    print("\n=== 3. 噪声对指标分数的影响分析 ===")
    
    # 合并数据以便比较
    # 首先标准化列名
    df_ori_renamed = df_ori.rename(columns={'val': 'val_ori', 'latency': 'latency_ori'})
    df_noise_renamed = df.rename(columns={'val': 'val_noise', 'latency': 'latency_noise'})
    
    # 合并数据
    merged_data = pd.merge(
        df_noise_renamed,
        df_ori_renamed,
        on=['case_name', 'case_seed', 'score_seed', 'q'],
        how='inner'
    )
    
    if len(merged_data) > 0:
        # 计算指标变化
        merged_data['val_change'] = merged_data['val_noise'] - merged_data['val_ori']
        merged_data['val_change_abs'] = abs(merged_data['val_change'])
        merged_data['val_change_ratio'] = (merged_data['val_change'] / merged_data['val_ori']) * 100
        
        # 计算latency变化
        merged_data['latency_change'] = merged_data['latency_noise'] - merged_data['latency_ori']
        merged_data['latency_change_ratio'] = (merged_data['latency_change'] / merged_data['latency_ori']) * 100
        
        print(f"成功合并的数据行数: {len(merged_data)}")
        
        # 按噪声水平分析影响
        noise_impact = merged_data.groupby(['noise_std', 'q']).agg({
            'val_change': ['mean', 'std'],
            'val_change_abs': ['mean', 'std'],
            'val_change_ratio': ['mean', 'std'],
            'latency_change': ['mean', 'std'],
            'latency_change_ratio': ['mean', 'std']
        }).round(4)
        
        print("\n不同噪声水平对指标的影响:")
        print(noise_impact)
        
        # 按case_name分析影响
        case_impact = merged_data.groupby(['case_name', 'noise_std']).agg({
            'val_change_abs': 'mean',
            'val_change_ratio': 'mean',
            'latency_change_ratio': 'mean'
        }).round(4)
        
        print("\n不同case下噪声的影响:")
        print(case_impact)
        
        # 4. 详细分析特定case
        print("\n=== 4. 特定case的详细分析 ===")
        
        # 选择第一个case进行详细分析
        first_case = merged_data['case_name'].iloc[0]
        case_detail = merged_data[merged_data['case_name'] == first_case]
        
        print(f"详细分析case: {first_case}")
        print(f"该case下的数据行数: {len(case_detail)}")
        
        # 按q值分析
        q_analysis = case_detail.groupby(['q', 'noise_std']).agg({
            'val_change': 'mean',
            'val_change_abs': 'mean',
            'latency_change': 'mean'
        }).round(4)
        
        print(f"\n{first_case} case下不同q值和噪声水平的影响:")
        print(q_analysis)
        
        return merged_data, avg_ori, avg_noise
        
    else:
        print("警告: 无法合并数据，请检查case_name, case_seed, score_seed, q的匹配情况")
        return None, avg_ori, avg_noise

def analyze_noise_robustness():
    """
    专门分析噪声鲁棒性的函数
    """
    print("=== 噪声鲁棒性分析 ===")
    
    # 读取数据
    df_robust = pd.read_csv(r'logs/CCE/AccQ-R_log.csv')
    df_original = pd.read_csv(r'logs/CCE/AccQ_log.csv')
    
    # 过滤CCE指标
    df_robust_cce = df_robust[df_robust['metric_name'] == 'CCE']
    df_original_cce = df_original[df_original['metric_name'] == 'CCE']
    
    # 计算每个配置下的稳定性指标
    stability_metrics = []
    
    for _, group in df_robust_cce.groupby(['case_name', 'case_seed', 'score_seed', 'q', 'noise_std']):
        if len(group) >= 3:  # 至少有3个重复实验
            stability_metrics.append({
                'case_name': group['case_name'].iloc[0],
                'case_seed': group['case_seed'].iloc[0],
                'score_seed': group['score_seed'].iloc[0],
                'q': group['q'].iloc[0],
                'noise_std': group['noise_std'].iloc[0],
                'val_mean': group['val'].mean(),
                'val_std': group['val'].std(),
                'val_cv': group['val'].std() / abs(group['val'].mean()) if group['val'].mean() != 0 else float('inf'),
                'latency_mean': group['latency'].mean(),
                'latency_std': group['latency'].std(),
                'latency_cv': group['latency'].std() / group['latency'].mean() if group['latency'].mean() != 0 else float('inf')
            })
    
    stability_df = pd.DataFrame(stability_metrics)
    
    if len(stability_df) > 0:
        print(f"稳定性分析完成，共 {len(stability_df)} 个配置")
        
        # 分析不同噪声水平下的稳定性
        noise_stability = stability_df.groupby('noise_std').agg({
            'val_cv': ['mean', 'std'],
            'latency_cv': ['mean', 'std']
        }).round(4)
        
        print("\n不同噪声水平下的稳定性:")
        print(noise_stability)
        
        # 分析不同q值下的稳定性
        q_stability = stability_df.groupby('q').agg({
            'val_cv': ['mean', 'std'],
            'latency_cv': ['mean', 'std']
        }).round(4)
        
        print("\n不同q值下的稳定性:")
        print(q_stability)
        
        return stability_df
    
    return stability_df

# 运行分析
if __name__ == "__main__":
    print("开始运行噪声鲁棒性分析...")
    

    pth1  = r'logs/CCE/AccQ-R_log.csv'
    pth2  = r'logs/CCE/LowDisAccQ-R_log.csv'
    pth3  = r'logs/CCE/PreQ-NegP-R_log.csv'
    pths = [pth1, pth2, pth3]
    
    metric = 'Aff-F1'
    
    metric = 'VUS-ROC'
    metric = 'UAff-F1'
    # metric = 'F1-PA'
    # metric = 'R-based F1'
    # metric = 'Reduced-F1'
    # metric = 'F1'
    # metric = 'eTaPR'
    # metric = 'CCE2'

    new_pths = [p.replace('CCE',metric) for p in pths]

    # new_pths = pths

    print(new_pths[0])

    # 运行主要分析
    merged_data, avg_ori, avg_noise = tmp_robust(new_pths[0])
    
    # 运行稳定性分析
    # stability_df = analyze_noise_robustness()
    # print(stability_df)
    
    print("\n=== 分析完成 ===")
    