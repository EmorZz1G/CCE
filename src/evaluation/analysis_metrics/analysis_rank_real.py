import os
proj_pth = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
log_dir = os.path.join(proj_pth, 'logs')

output_dir = os.path.join(log_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
from os.path import join as opj
import pandas as pd
import sys

# Import ranking evaluators with a tolerant path
try:
    sys.path.append(proj_pth)
    from src.evaluation.eval_metrics.eval_rank_utils import get_ranking_score_v2 as get_ranking_score
except Exception:
    from evaluation.eval_metrics.eval_rank_utils import get_ranking_score_v2 as get_ranking_score

metric_list_ = ['CCE', 'AUC-ROC', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'VUS-ROC']
metric_list_ = ['CCE', 'AUC-ROC', 'F1', 'F1-PA', 'Reduced-F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'VUS-ROC']
metric_list_ = ['CCE', 'AUC-ROC', 'eTaPR', 'UAff-F1', 'VUS-ROC']
metric_list_ = ['CCE', 'AUC-ROC', 'F1', 'Aff-F1', 'VUS-ROC', 'PATE']
metric_list_ = ['CCE', 'AUC-ROC',  'F1', 'eTaPR', 'Aff-F1', 'VUS-ROC']
# metric_list_ = ['CCE', 'UAff-F1', 'VUS-ROC']

def expected_ranking(df):
    pass

def ana_UCR():
    df_file = os.path.join(output_dir, 'RealWorldAD', 'real_model_performance1.csv')
    df = pd.read_csv(df_file)
    df = df.drop_duplicates(subset=['case_name', 'model_name', 'metric_name'])
    ecg_list = [124, 125, 126]
    power_list = [152, 153, 154]
    ecg_list = ["UCR-"+str(i) for i in ecg_list]
    power_list = ["UCR-"+str(i) for i in power_list]
    df = df[df['case_name'].isin(ecg_list + power_list)]
    df = df[df['metric_name'].isin(metric_list_)]
    df.loc[df['model_name'] == 'AnomalyTransformer', 'model_name'] = 'A.T.'
    case_name_list = df['case_name'].unique().tolist() + ['Avg.']
    case_name_list = ['UCR-125','UCR-126','UCR-153','UCR-154']
    model_list = ['LOF','IForest','LSTMAD', 'USAD', 'AnomalyTransformer','A.T.','Random']
    df = df.sort_values(by='metric_name', key=lambda x: x.map(lambda name: metric_list_.index(name) if name in metric_list_ else len(metric_list_)))
    for case_name in case_name_list:
        if case_name == 'Avg.':
            df_case = df.groupby(['model_name', 'metric_name']).agg({'val': 'mean'}).reset_index()
            df_case['case_name'] = 'Avg.'
        else:
            df_case = df[df['case_name'] == case_name]
        try:
            df_case = df_case.pivot(index='model_name', columns='metric_name', values='val')
            df_case = df_case.reindex(columns=metric_list_)
            df_case = df_case.sort_values(by='model_name', key=lambda x: x.map(lambda name: model_list.index(name) if name in model_list else len(model_list)))
        except:
            print(df_case.head(30))
            raise Exception("Pivot failed, check the data format.")
        df_case = (df_case*100).round(2).astype(str)
        df_case = df_case.reset_index()
        # 计算不同指标给不同模型的排名
        df_case_copy = df_case.copy()
        for mt in metric_list_:
            if mt in df_case_copy.columns:
                df_case_copy[mt] = df_case_copy[mt].astype(float)
                df_case_copy[mt] = df_case_copy[mt].rank(ascending=False, method='min').astype(int)
        print(f"Case: {case_name}"+"===="*20)
        # 对于每一个模型，得到它们的期望排序，期望排序的计算是，所有指标的排名的众数
        # df_case_copy['Expected_Rank'] = df_case_copy[metric_list_].mode(axis=1).iloc[:, 0]
        df_case_copy['Expected_Rank'] = df_case_copy[metric_list_].mean(axis=1)
        sorted_ = df_case_copy['Expected_Rank'].values.argsort()
        print(sorted_)
        df_case_copy['Expected_Rank'] = sorted_ + 1
        print(df_case_copy)
        # 计算每个指标的get_ranking_score
        rank_scores = {}
        for metric in metric_list_:
            if metric in df_case_copy.columns:
                a,b = df_case_copy['Expected_Rank'].values, df_case_copy[metric].values
                rank_scores[metric] = get_ranking_score(a,b)
        # 添加排名分数到df_case
        print("Ranking Scores:")
        print(rank_scores)

        df_case = df_case.rename(columns={'metric_name': 'Metric'})
        print(df_case)
        out_pth = os.path.join(output_dir, 'RealWorldAD', 'UCR')
        df_case = df_case.sort_values(by='model_name', key=lambda x: x.map(lambda name: model_list.index(name) if name in model_list else len(model_list)))
        latex_str = df_case.to_latex(f'{out_pth}/{case_name}.txt', float_format='%.3f', index=False)
        print(latex_str)
        
        
        # print(latex_str)

def ana_msl_etal():
    df_file = os.path.join(output_dir, 'RealWorldAD', 'real_model_performance.csv')
    df_dir = os.path.dirname(df_file)
    if not os.path.exists(df_file):
        print(f"File {df_file} does not exist.")
        sys.exit(1)
    df = pd.read_csv(df_file)
    # 去重复
    df = df.drop_duplicates()
    # 聚合SMD
    df_smd = df[df['case_name'].str.contains('SMD')]
    df_smd = df_smd.groupby(['metric_name','model_name']).agg(
        {
            'val': 'mean',
            'latency': 'mean',
        }
    )
    df_smd = df_smd.reset_index()
    df_smd['case_name'] = 'SMD'
    df_2 = df[df['case_name'].str.contains('SMD') == False]
    df = pd.concat([df_smd, df_2], axis=0)
    # df = df_smd
    df = df[df['metric_name'].isin(metric_list_)]
    print(df)
    # 把NIPS_TS_Creditcard改成CC
    df.loc[df['case_name'] == 'NIPS_TS_Creditcard', 'case_name'] = 'CC'
    # 把模型AnomalyTransformer改成A.T.
    df.loc[df['model_name'] == 'AnomalyTransformer', 'model_name'] = 'A.T.'
    # 输出latex
    case_name_list = ['MSL','SMD','PSM','SWAT','CC','Avg.']
    # case_name_list = df['case_name'].unique().tolist()
    model_list = ['LOF', 'IForest',  'LSTMAD', 'USAD' , 'A.T.', 'Donut',  'TimesNet']
    print(df['model_name'].unique())
    # df根据model_list排序
    df = df.sort_values(by='model_name', key=lambda x: x.map(lambda name: model_list.index(name)))
    # df根据case_name_list排序
    df = df.sort_values(by='metric_name', key=lambda x: x.map(lambda name: metric_list_.index(name) if name in metric_list_ else len(metric_list_)))
    dfs = []
    out_pth = os.path.join(output_dir, 'RealWorldAD', 'REAL')
    if not os.path.exists(out_pth):
        os.makedirs(out_pth)
    for case_name in case_name_list:
        if case_name == 'Avg.':
            df_case = df.groupby(['model_name', 'metric_name']).agg({'val': 'mean'}).reset_index()
            df_case['case_name'] = 'Avg.'
            print("Average DataFrame:")
            print(df_case)
        else:
            df_case = df[df['case_name'] == case_name]
        try:
            df_case = df_case.pivot(index='model_name', columns='metric_name', values='val')
            df_case = df_case.reindex(columns=metric_list_)
        except:
            print(df_case.head(30))
            raise Exception("Pivot failed, check the data format.")
        df_case = (df_case*100).round(2).astype(str)
        df_case = df_case.reset_index()
        df_case = df_case.sort_values(by='model_name', key=lambda x: x.map(lambda name: model_list.index(name) if name in model_list else len(model_list)))
        # 计算不同指标给不同模型的排名
        df_case_copy = df_case.copy()
        for mt in metric_list_:
            if mt in df_case_copy.columns:
                df_case_copy[mt] = df_case_copy[mt].astype(float)
                df_case_copy[mt] = df_case_copy[mt].rank(ascending=False, method='min').astype(int)
        print("Ranked DataFrame:")
        # 对于每一个模型，得到它们的期望排序，期望排序的计算是，所有指标的排名的众数
        # df_case_copy['Expected_Rank'] = df_case_copy[metric_list_].mode(axis=1).iloc[:, 0]
        # df_case_copy['Expected_Rank'] = df_case_copy[metric_list_].mean(axis=1)
        # print(df_case_copy)
        # 计算每个指标的get_ranking_score
        # rank_scores = {}
        # for metric in metric_list_:
        #     if metric in df_case_copy.columns:
        #         a,b = df_case_copy['Expected_Rank'].values, df_case_copy[metric].values
        #         rank_scores[metric] = get_ranking_score(a,b)
        # # 添加排名分数到df_case
        # print("Ranking Scores:")
        # print(rank_scores)

        df_case = df_case.rename(columns={'model_name': case_name})
        print(df_case.columns)
        latex_str = df_case.to_latex(f'{out_pth}/{case_name}.txt', float_format='%.3f', index=False)
        print(f"Case: {case_name}")
        dfs.append(df_case.copy())
   
        
    # 生成每个表格的 LaTeX 代码
    latex_tables = [df.to_latex(float_format='%.3f', index=False) for df in dfs]

    # 创建 2x3 的 LaTeX 表格布局
    latex_str = r"""
    \begin{table}[ht]
    \centering
    \begin{tabular}{ccc}
    """

    # 将每个表格插入到布局中
    for i, table in enumerate(latex_tables):
        latex_str += r"\begin{minipage}{0.33\textwidth}" + "\n"
        latex_str += table + "\n"
        latex_str += r"\end{minipage}" + "\n"
        if (i + 1) % 3 == 0 and i != len(latex_tables) - 1:
            latex_str += r"\\ \hline" + "\n"  # 换行并添加水平线
        elif i != len(latex_tables) - 1:
            latex_str += r"&" + "\n"  # 添加列间分隔符

    latex_str += r"""
    \end{tabular}
    \caption{Comparison of Cases}
    \label{tab:cases}
    \end{table}
    """

    # 输出到文件
    with open(f'{out_pth}/combined_table.txt', 'w') as f:
        f.write(latex_str)

def main():
    # ana_UCR()
    ana_msl_etal()


if __name__ == '__main__':
    main()
