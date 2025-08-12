default_baseline_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based-F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
import os
proj_pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
log_dir = os.path.join(proj_pth, 'logs')
from os.path import join as opj
import pandas as pd
import sys

def expected_ranking(df, model_type):
    # Build expected rank maps from unique values present in df
    if model_type in ['AccQ', 'AccQ-R', 'LowDisAccQ', 'LowDisAccQ-R'] or 'p' not in df.columns:
        q_values = sorted(df['q'].unique().tolist(), reverse=True)
        q_2rank = {val: rank for rank, val in enumerate(q_values, start=1)}
        return q_2rank, None
    else:
        p_values = sorted(df['p'].unique().tolist())
        q_values = sorted(df['q'].unique().tolist(), reverse=True)
        p_2rank = {val: rank for rank, val in enumerate(p_values, start=1)}
        q_2rank = {val: rank for rank, val in enumerate(q_values, start=1)}
        return q_2rank, p_2rank


def ana_ranking_helper(df, q_2rank, p_2rank, verbose=0):
    # Import ranking evaluators with a tolerant path
    try:
        sys.path.append(proj_pth)
        from src.evaluation.eval_metrics.eval_rank_utils import get_ranking_score
    except Exception:
        from evaluation.eval_metrics.eval_rank_utils import get_ranking_score

    def ensure_rank_map(values, provided_map):
        values_unique = sorted(list(set(values)), reverse=True)
        if provided_map is None or any(v not in provided_map for v in values_unique):
            return {val: i for i, val in enumerate(values_unique, start=1)}
        return provided_map

    has_p = 'p' in df.columns
    has_noise = 'noise_std' in df.columns

    # Ensure rank maps cover the present values
    q_2rank = ensure_rank_map(df['q'].tolist(), q_2rank)
    p_2rank = ensure_rank_map(df['p'].tolist(), p_2rank) if has_p else None

    group_keys = ['case_name'] + (['noise_std'] if has_noise else [])
    results = []      # ranking q given fixed p
    results_p = []    # ranking p given fixed q
    for keys, sub in df.groupby(group_keys):
        if has_p:
            # For each fixed p, rank q by val
            for p_val, sub_p in sub.groupby('p'):
                q_stats = sub_p.groupby('q')['val'].mean().reset_index()
                actual_q = [float(x) for x in q_stats.sort_values('val', ascending=False)['q'].tolist()]
                expected_q = sorted(actual_q, key=lambda q: q_2rank[q])

                score = get_ranking_score(expected_q, actual_q)
                row = {
                    'case_name': keys[0] if isinstance(keys, tuple) else keys,
                    'num_items': len(actual_q),
                    'spearman': round(score['spearman'], 4),
                    'kendall': round(score['kendall'], 4),
                    'mean_deviation': round(score['mean_deviation'], 4),
                }
                if has_noise:
                    row['noise_std'] = keys[1] if isinstance(keys, tuple) else None
                results.append(row)

            # For each fixed q, rank p by val
            for q_val, sub_q in sub.groupby('q'):
                p_stats = sub_q.groupby('p')['val'].mean().reset_index()
                actual_p = [float(x) for x in p_stats.sort_values('val', ascending=False)['p'].tolist()]
                expected_p = sorted(actual_p, key=lambda p: p_2rank[p])

                score = get_ranking_score(expected_p, actual_p)
                row = {
                    'case_name': keys[0] if isinstance(keys, tuple) else keys,
                    'num_items': len(actual_p),
                    'spearman': round(score['spearman'], 4),
                    'kendall': round(score['kendall'], 4),
                    'mean_deviation': round(score['mean_deviation'], 4),
                }
                if has_noise:
                    row['noise_std'] = keys[1] if isinstance(keys, tuple) else None
                results_p.append(row)
        else:
            # No p: rank q globally within case/noise
            q_stats = sub.groupby('q')['val'].mean().reset_index()
            actual_q = [float(x) for x in q_stats.sort_values('val', ascending=False)['q'].tolist()]
            expected_q = sorted(actual_q, key=lambda q: q_2rank[q])

            score = get_ranking_score(expected_q, actual_q)
            row = {
                'case_name': keys[0] if isinstance(keys, tuple) else keys,
                'num_items': len(actual_q),
                'spearman': round(score['spearman'], 4),
                'kendall': round(score['kendall'], 4),
                'mean_deviation': round(score['mean_deviation'], 4),
            }
            if has_noise:
                row['noise_std'] = keys[1] if isinstance(keys, tuple) else None
            results.append(row)

    if not results and not results_p:
        print('无可用于排名分析的数据')
        return

    # Print per-case summary and overall averages
    df_res = pd.DataFrame(results)
    # print('\n=== 排序一致性评估 ===')
    # print(df_res.head(20).to_string(index=False))

    # print('\n总体均值:')
    mean_vals = df_res[['spearman', 'kendall', 'mean_deviation']].mean().to_dict()
    mean_vals = {k: round(v, 4) for k, v in mean_vals.items()}
    print(mean_vals)

    if has_p and len(results_p) > 0:
        print('P')
        df_res = pd.DataFrame(results_p)
        mean_vals = df_res[['spearman', 'kendall', 'mean_deviation']].mean().to_dict()
        mean_vals = {k: round(v, 4) for k, v in mean_vals.items()}
        print(mean_vals)


def ana_ranking(log_dir, baseline, model_type, latency_ana=False,verbose=0):
    ori_pth = opj(log_dir,baseline,model_type+'_log.csv')
    pth = opj(log_dir,baseline,model_type+'-R_log.csv')
    df = pd.read_csv(pth)
    df_ori = pd.read_csv(ori_pth)
    
    if verbose:
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
    
    if verbose:
        print(f"无噪声情况下的唯一组合数: {len(avg_ori)}")
        print(f"有噪声情况下的唯一组合数: {len(avg_noise)}")
    

    if latency_ana:
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

    q_2rank, p_2rank = expected_ranking(df_ori, model_type)
    ana_ranking_helper(df_ori, q_2rank, p_2rank)
    q_2rank, p_2rank = expected_ranking(df, model_type)
    ana_ranking_helper(df, q_2rank, p_2rank)


def ana_metrics_ranking():
    default_baseline_list = ['CCE2', 'F1', 'F1-PA', 'Reduced-F1', 'R-based-F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
    model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
    model_type_list = ['AccQ']
    # model_type_list = ['LowDisAccQ']
    model_type_list = ['PreQ-NegP']
    for b in default_baseline_list:
        for m in model_type_list:
            print(b)
            try:
                ana_ranking(log_dir,b,m)
            except Exception as e:
                raise e
                print('No File')

if '__main__' == __name__:
    model_type = 'AccQ'; metric='eTaPR';
    model_type = 'LowDisAccQ'; metric='eTaPR';
    # model_type = 'LowAccQ'; metric='UAff-F1';
    # model_type = 'LowDisAccQ'; metric='UAff-F1';
    model_type = 'LowDisAccQ'; metric='CCE2';
    model_type = 'AccQ'; metric='CCE2';
    # ana_ranking(log_dir,'CCE','AccQ')
    # ana_ranking(log_dir,'CCE','AccQ')
    # ana_ranking(log_dir,'F1','AccQ')
    # ana_ranking(log_dir,'AUC-ROC','AccQ')
    # ana_ranking(log_dir,metric,model_type)
    ana_metrics_ranking()