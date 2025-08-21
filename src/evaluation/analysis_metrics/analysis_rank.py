default_baseline_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
import os
proj_pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
log_dir = os.path.join(proj_pth, 'logs')

output_dir = os.path.join(log_dir, 'RankEval')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
from os.path import join as opj
import pandas as pd
import sys
from deprecated import deprecated

metric_list_ = ['CCE', 'AUC-ROC', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'VUS-ROC']
task_list_ = ['AccQ', 'LowDisAccQ', 'PreQ-NegP']
import argparse
argparser = argparse.ArgumentParser(description='Analyze ranking metrics')
argparser.add_argument('--metric_list', type=str, nargs='+', default=metric_list_, help='List of metrics to analyze')
argparser.add_argument('--task_list', type=str, nargs='+', default=task_list_, help='List of tasks to analyze')

args = argparser.parse_args()

metric_list = args.metric_list
task_list = args.task_list




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


def ana_ranking_helper(df, q_2rank, p_2rank, baseline, model_type, verbose=0):
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
                else:
                    row['noise_std'] = 0
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
                else:
                    row['noise_std'] = 0
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
            else:
                row['noise_std'] = 0
            results.append(row)

    if not results and not results_p:
        print('无可用于排名分析的数据')
        return

    # Print per-case summary and overall averages
    df_res = pd.DataFrame(results)
    
    
    # 有噪声的情况下，按noise_std分组，计算平均排序
    grouped = df_res.groupby(['noise_std'])[['spearman', 'kendall', 'mean_deviation']].mean().reset_index()
    grouped['metric_name'] = baseline
    print(grouped)
    # rename
    grouped.rename(columns={'spearman': 'spearman_q', 'kendall': 'kendall_q', 'mean_deviation': 'mean_deviation_q'}, inplace=True)
        

    if has_p and len(results_p) > 0:
        df_res2 = pd.DataFrame(results_p)
        # 有噪声的情况下，按noise_std分组，计算平均排序
        grouped2 = df_res2.groupby('noise_std')[['spearman', 'kendall', 'mean_deviation']].mean().reset_index()
        grouped2['metric_name'] = baseline
        grouped2.rename(columns={'spearman': 'spearman_p', 'kendall': 'kendall_p', 'mean_deviation': 'mean_deviation_p'}, inplace=True)

    group2 = grouped if not has_p else grouped.merge(grouped2, on=['noise_std','metric_name'], how='outer')
    output_pth1 = opj(output_dir, f'{model_type}_ranking_all.csv')
    if os.path.exists(output_pth1):
        # 追加保存
        df_res_existing = pd.read_csv(output_pth1)
        group2 = pd.concat([df_res_existing, group2], ignore_index=True)
        # 去除重复行
        group2.drop_duplicates(keep='last', inplace=True)
    group2.to_csv(output_pth1, index=False)
        

    df_res.rename(columns={'spearman': 'spearman_q', 'kendall': 'kendall_q', 'mean_deviation': 'mean_deviation_q'}, inplace=True)
    if has_p:
        df_res2.rename(columns={'spearman': 'spearman_p', 'kendall': 'kendall_p', 'mean_deviation': 'mean_deviation_p'}, inplace=True)
        df_res = pd.merge(df_res, df_res2, on=['case_name', 'num_items','noise_std'], how='outer')
    # df_res 加一列，metric_name：baseline
    df_res['metric_name'] = baseline
    # Save results to CSV
    output_pth = opj(output_dir, f'{model_type}_ranking.csv')
    if os.path.exists(output_pth):
        # 追加保存
        df_res_existing = pd.read_csv(output_pth)
        df_res = pd.concat([df_res_existing, df_res], ignore_index=True)
        # 去除重复行
        df_res.drop_duplicates(keep='last', inplace=True)
        
    # 说实话，好像没必要保存全部的，直接mean就足够了
    df_res.to_csv(output_pth, index=False)
    print(f'=== 排序分析结果已保存到 {output_pth} ===')


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
    # merged_data = pd.merge(
    #     df_noise_renamed,
    #     df_ori_renamed,
    #     on=['case_name', 'case_seed', 'score_seed', 'q'],
    #     how='inner'
    # )

    q_2rank, p_2rank = expected_ranking(df_ori, model_type)
    ana_ranking_helper(df_ori, q_2rank, p_2rank, baseline, model_type)
    q_2rank, p_2rank = expected_ranking(df, model_type)
    ana_ranking_helper(df, q_2rank, p_2rank, baseline, model_type)


def ana_metrics_ranking(metric_list=None, task_list=None):
    """
    这个方程用于聚合所有的数据
    """
    metric_list_ = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
    task_list_ = ['AccQ', 'LowDisAccQ', 'PreQ-NegP']
    if metric_list is None:
        metric_list = metric_list_
        print('Using default metric list:', metric_list)
    if task_list is None:
        task_list = task_list_
        print('Using default task list:', task_list)
    for b in metric_list:
        for m in task_list:
            try:
                ana_ranking(log_dir,b,m)
            except Exception as e:
                print('No File', m)
                raise e

def plot_rank_by_task(task_type, metric_list=None, qp_metric='spearman_q'):
    """
    画出每个任务类型下的指标排名
    """
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    task_list_ = ['AccQ', 'LowDisAccQ', 'PreQ-NegP']
    assert task_type in task_list_, f"Task type {task_type} not in {task_list_}"
    sns.set_style("whitegrid")
    if metric_list is None:
        metric_list = ['CCE','AUC-ROC', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1',  'VUS-ROC']

    # df = pd.read_csv(opj(output_dir, f'{task_type}_ranking_all.csv'))
    df = pd.read_csv(opj(output_dir, f'{task_type}_ranking.csv'))

    # 画出每个指标的排名分布
    print(df['noise_std'].unique())
    
    # 关键修复：确保noise_std为数值型并获取数据中实际存在的所有值
    df['noise_std'] = pd.to_numeric(df['noise_std'])
    # 筛选出有数据的(metric_name, noise_std)组合
    combination_counts = df.groupby(['metric_name', 'noise_std']).size().reset_index(name='counts')
    valid_combinations = combination_counts[combination_counts['counts'] > 0][['metric_name', 'noise_std']]
    df_filtered = pd.merge(df, valid_combinations, on=['metric_name', 'noise_std'])
    # df_filtered 按照metric_list排序
    
    # 获取排序后的噪声水平和指标列表
    noise_levels = sorted(df_filtered['noise_std'].unique())
    metric_order = metric_list

    # 生成颜色映射：每个指标对应一种pastel颜色
    n_metrics = len(metric_order)
    metric_color_map = {metric: color for metric, color in 
                       zip(metric_order, sns.color_palette("pastel", n_colors=n_metrics))}
    import matplotlib.colors as mcolors  # 用于调整颜色
    # 辅助函数：调整颜色深浅（替代seaborn.darken）
    def adjust_color_lightness(color, amount=0.5):
        """
        调整颜色的亮度
        amount > 1 使颜色更亮，amount < 1 使颜色更深
        """
        try:
            c = mcolors.cnames[color]
        except:
            c = color
        c = mcolors.to_rgb(c)
        return tuple(max(0, min(1, x * amount)) for x in c)
    
    # 为每个噪声水平生成深浅变化（同一指标下，噪声越大颜色越深）
    noise_intensity = {noise: 1 - (i/len(noise_levels))*0.5 for i, noise in enumerate(noise_levels)}
    # 说明：值越接近0颜色越深，这里设置为1到0.5之间变化（noise越大，值越小，颜色越深）
    
    violin_color_map = {}
    for metric in metric_order:
        base_color = metric_color_map[metric]
        for noise in noise_levels:
            # 根据噪声水平调整颜色深度
            violin_color_map[(metric, noise)] = adjust_color_lightness(base_color, noise_intensity[noise])

    # 使用分面图：每个指标一个子图，x 轴为 noise_std，这样虚线能与对应的小提琴对齐
    noise_palette = sns.color_palette("Blues", n_colors=len(noise_levels))
    g = sns.catplot(
        data=df_filtered,
        x='noise_std',
        y=qp_metric,
        col='metric_name',
        col_order=metric_order,
        kind='violin',
        order=noise_levels,
        inner='quartile',
        cut=0,
        palette=noise_palette,
        height=3,
        aspect=1,
        sharey=True,
        col_wrap=5,
    )

    # 在每个子图上叠加该指标在不同噪声下的均值虚线
    noise_to_pos = {noise: idx for idx, noise in enumerate(noise_levels)}
    def _draw_mean_line(data, color, **kwargs):
        ax = plt.gca()
        mean_local = data.groupby('noise_std', as_index=False)[qp_metric].mean()
        # 按照分类顺序排序并映射到分类位置以确保与小提琴对齐
        mean_local['x_pos'] = mean_local['noise_std'].map(noise_to_pos)
        mean_local = mean_local.sort_values('x_pos')
        ax.plot(
            mean_local['x_pos'],
            mean_local[qp_metric],
            marker='o',
            linestyle='--',
            color='red',
            markeredgecolor='black',  # 标记边缘颜色
            alpha=0.6,
            linewidth=1.8,
            markersize=3,
            zorder=3,
        )

    g.map_dataframe(_draw_mean_line)
    if 'spearman' in qp_metric:
        name = 'Spearman'
    elif 'kendall' in qp_metric:
        name = 'Kendall'
    elif 'mean_deviation' in qp_metric:
        name = 'Mean Deviation'
    g.set_axis_labels('Noise Std', f"{name}'s Rank")
    g.set_titles('{col_name}')
    for ax in g.axes.flatten():
        if ax is None:
            continue
        ax.tick_params(axis='x', labelrotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout()
    
    g.figure.suptitle(f"{name} Ranking for {task_type} Task", fontsize=12)
    g.figure.subplots_adjust(top=0.88)
    print(qp_metric)
    if '_p' in qp_metric:
        tmp = '_p'
    else:
        tmp = ''
    if 'spearman' in qp_metric:
        qp_name = 'Sp'
    elif 'kendall' in qp_metric:
        qp_name = 'Kd'
    elif 'mean_deviation' in qp_metric:
        qp_name = 'MD'
    g.figure.savefig(opj(output_dir, 'plots', f'{task_type}{tmp}_rank_{qp_name}.jpg'), dpi=500)
    plt.show()


def plot_rank_by_p_noise_std(task_type, metric_=None, qp_metric='spearman_p'):
    """
    画出每个任务类型下的指标排名
    """
    
    import seaborn as sns
    import matplotlib.pyplot as plt
    task_list_ = ['PreQ-NegP']
    assert task_type in task_list_, f"Task type {task_type} not in {task_list_}"
    sns.set_style("whitegrid")
    if metric_ is None:
        # metric_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
        metric_ = 'CCE'

    df1 = pd.read_csv(opj(log_dir, metric_, f'PreQ-NegP_log.csv'))
    df1['noise_std'] = 0.
    df2 = pd.read_csv(opj(log_dir, metric_, f'PreQ-NegP-R_log.csv'))

    df = pd.concat([df1, df2], ignore_index=True)

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

    group_keys = ['case_name'] + ['noise_std','p']
    results = []      # ranking q given fixed p
    for keys, sub in df.groupby(group_keys):
        q_stats = sub.groupby('q')['val'].mean().reset_index()
        actual_q = [float(x) for x in q_stats.sort_values('val', ascending=False)['q'].tolist()]
        expected_q = sorted(actual_q, key=lambda q: q_2rank[q])

        score = get_ranking_score(expected_q, actual_q)
        row = {
            'case_name': keys[0] if isinstance(keys, tuple) else keys,
            'noise_std': keys[1] if isinstance(keys, tuple) else 0,
            'p': keys[2] if isinstance(keys, tuple) else 0,
            'spearman': round(score['spearman'], 4),
            'kendall': round(score['kendall'], 4),
            'mean_deviation': round(score['mean_deviation'], 4),
            'metric_name': metric_,
        }
        results.append(row)

    df = pd.DataFrame(results)

    # 画出每个指标的排名分布
    print(df['noise_std'].unique())
    
    # 关键修复：确保noise_std为数值型并获取数据中实际存在的所有值
    df['noise_std'] = pd.to_numeric(df['noise_std'])
    combination_counts = df.groupby(['metric_name', 'noise_std']).size().reset_index(name='counts')
    valid_combinations = combination_counts[combination_counts['counts'] > 0][['metric_name', 'noise_std']]
    df_filtered = pd.merge(df, valid_combinations, on=['metric_name', 'noise_std'])
    # df_filtered 按照metric_list排序
    
    # 获取排序后的噪声水平和指标列表
    noise_levels = sorted(df_filtered['noise_std'].unique())
    p_levels = sorted(df_filtered['p'].unique())
    print(p_levels)
    metric_order = metric_list

    # 生成颜色映射：每个指标对应一种pastel颜色
    n_metrics = len(p_levels)
    metric_color_map = {metric: color for metric, color in 
                       zip(metric_order, sns.color_palette("pastel", n_colors=n_metrics))}
    import matplotlib.colors as mcolors  # 用于调整颜色
    # 辅助函数：调整颜色深浅（替代seaborn.darken）
    def adjust_color_lightness(color, amount=0.5):
        """
        调整颜色的亮度
        amount > 1 使颜色更亮，amount < 1 使颜色更深
        """
        try:
            c = mcolors.cnames[color]
        except:
            c = color
        c = mcolors.to_rgb(c)
        return tuple(max(0, min(1, x * amount)) for x in c)
    
    # 为每个噪声水平生成深浅变化（同一指标下，噪声越大颜色越深）
    noise_intensity = {noise: 1 - (i/len(noise_levels))*0.5 for i, noise in enumerate(noise_levels)}
    p_intensity = {noise: 1 - (i/len(noise_levels))*0.5 for i, noise in enumerate(p_levels)}
    # 说明：值越接近0颜色越深，这里设置为1到0.5之间变化（noise越大，值越小，颜色越深）
    
    violin_color_map = {}
    for metric in metric_order:
        base_color = metric_color_map[metric]
        for noise in p_levels:
            # 根据噪声水平调整颜色深度
            violin_color_map[(metric, noise)] = adjust_color_lightness(base_color, p_intensity[noise])

    # 使用分面图：每个指标一个子图，x 轴为 noise_std，这样虚线能与对应的小提琴对齐
    noise_palette = sns.color_palette("Blues", n_colors=len(noise_levels))
    p_palette = sns.color_palette("Blues", n_colors=len(p_levels))
    g = sns.catplot(
        data=df_filtered,
        # x='noise_std',
        x = 'p',
        y=qp_metric,
        # col='metric_name',
        col='noise_std',
        # col_order=metric_order,
        col_order=noise_levels,
        kind='violin',
        # order=noise_levels,
        order=p_levels,
        inner='quartile',
        cut=0,
        # palette=noise_palette,
        palette=p_palette,
        height=3,
        aspect=1,
        sharey=True,
        col_wrap=3,
    )


    # 在每个子图上叠加该指标在不同噪声下的均值虚线
    noise_to_pos = {noise: idx for idx, noise in enumerate(p_levels)}
    def _draw_mean_line(data, color, **kwargs):
        ax = plt.gca()
        mean_local = data.groupby('p', as_index=False)[qp_metric].mean()
        # 按照分类顺序排序并映射到分类位置以确保与小提琴对齐
        mean_local['x_pos'] = mean_local['p'].map(noise_to_pos)
        mean_local = mean_local.sort_values('x_pos')
        ax.plot(
            mean_local['x_pos'],
            mean_local[qp_metric],
            marker='o',
            linestyle='--',
            color='red',
            markeredgecolor='black',  # 标记边缘颜色
            alpha=0.6,
            linewidth=1.8,
            markersize=3,
            zorder=3,
        )

    g.map_dataframe(_draw_mean_line)
    if 'spearman' in qp_metric:
        name = 'Spearman'
    elif 'kendall' in qp_metric:
        name = 'Kendall'
    elif 'mean_deviation' in qp_metric:
        name = 'Mean Deviation'
    # g.set_axis_labels('Noise Std', "Spearman's Rank")
    g.set_axis_labels('False Alert Ratio', f"{name}'s Rank")
    g.set_titles('Noise Std: {col_name}')
    for ax in g.axes.flatten():
        if ax is None:
            continue
        ax.tick_params(axis='x', labelrotation=0, labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
    plt.tight_layout()
    
    # g.figure.suptitle(f"{name} Ranking for {task_type} Task", fontsize=12)
    g.figure.subplots_adjust(top=0.88)
    if 'spearman' in qp_metric:
        qp_name = 'Sp'
    elif 'kendall' in qp_metric:
        qp_name = 'Kd'
    elif 'mean_deviation' in qp_metric:
        qp_name = 'MD'
    if not os.path.exists(opj(output_dir, 'plots', 'p_rank')):
        os.makedirs(opj(output_dir, 'plots', 'p_rank'))
    g.figure.savefig(opj(output_dir, 'plots', 'p_rank', f'{metric_}_PreQ-NegP_{qp_name}.jpg'), dpi=500)
    plt.show()

def gen_rank_table(metric_list):
    """
    生成排名表格
    """
   
    df = pd.read_csv(opj(output_dir, 'AccQ_ranking_all.csv'))
    df2 = pd.read_csv(opj(output_dir, 'LowDisAccQ_ranking_all.csv'))
    df3 = pd.read_csv(opj(output_dir, 'PreQ-NegP_ranking_all.csv'))
    # noise_std,spearman_q,kendall_q,mean_deviation_q,metric_name
    df = df.groupby('metric_name').agg({
        'spearman_q': 'mean',
        'kendall_q': 'mean',
        'mean_deviation_q': 'mean'
    }).reset_index()
    df.rename(columns={
        'spearman_q': 'Sp',
        'kendall_q': 'Kd',
        'mean_deviation_q': 'MD'
    }, inplace=True)
    df_new = pd.DataFrame({
        'Metric': df['metric_name'],
        'AccQ_Sp': df['Sp'],
        'AccQ_Kd': df['Kd'],
        'AccQ_MD': df['MD']
    })
    df2 = df2.groupby('metric_name').agg({
        'spearman_q': 'mean',
        'kendall_q': 'mean',
        'mean_deviation_q': 'mean'
    }).reset_index()
    df2.rename(columns={
        'spearman_q': 'Sp',
        'kendall_q': 'Kd',
        'mean_deviation_q': 'MD'
    }, inplace=True)
    df_new2 = pd.DataFrame({
        'Metric': df2['metric_name'],
        'LowDisAccQ_Sp': df2['Sp'],
        'LowDisAccQ_Kd': df2['Kd'],
        'LowDisAccQ_MD': df2['MD']
    })
    df3 = df3.groupby('metric_name').agg({
        'spearman_q': 'mean',
        'kendall_q': 'mean',
        'mean_deviation_q': 'mean',
        'spearman_p': 'mean',
        'kendall_p': 'mean',
        'mean_deviation_p': 'mean'
    }).reset_index()
    df_new3 = pd.DataFrame({
        'Metric': df3['metric_name'],
        'PreQ-NegP-Q_Sp': df3['spearman_q'],
        'PreQ-NegP-Q_Kd': df3['kendall_q'],
        'PreQ-NegP-Q_MD': df3['mean_deviation_q'],
        'PreQ-NegP-P_Sp': df3['spearman_p'],
        'PreQ-NegP-P_Kd': df3['kendall_p'],
        'PreQ-NegP-P_MD': df3['mean_deviation_p']
    })
    # 合并三个DataFrame
    df_final = pd.merge(df_new, df_new2, on='Metric', how='outer')
    df_final = pd.merge(df_final, df_new3, on='Metric', how='outer')

    # 创建排序键并排序
    df_final["sort_key"] = df_final["Metric"].apply(lambda x: metric_list.index(x) if x in metric_list else len(metric_list))
    df_final = df_final.sort_values("sort_key").drop(columns=["sort_key"]).reset_index(drop=True)
    # 保存到CSV
    if not os.path.exists(opj(output_dir, 'tables')):
        os.makedirs(opj(output_dir, 'tables'))
    output_pth = opj(output_dir, 'tables', 'rank_table.csv')
    df_final.to_csv(output_pth, index=False)
    # 三行是不同指标的Sp, Kd, MD分数



if '__main__' == __name__:
    # ana_metrics_ranking(metric_list, task_list)
    rank_metric_list = ['spearman', 'kendall', 'mean_deviation']
    for rk in rank_metric_list:
        plot_rank_by_task('AccQ', metric_list, rk+'_q')
        plot_rank_by_task('LowDisAccQ', metric_list, rk+'_q')
        plot_rank_by_task('PreQ-NegP', metric_list, rk+'_q')
        plot_rank_by_task('PreQ-NegP', metric_list, rk+'_p')
    # pass
    # gen_rank_table(metric_list)
    # metric_list = ['CCE', "Aff-F1", 'AUC-ROC', 'VUS-ROC']
    # for mt in metric_list:
    #     for rk in rank_metric_list:
    #         plot_rank_by_p_noise_std('PreQ-NegP', metric_=mt, qp_metric=rk)