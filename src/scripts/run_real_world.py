default_metric_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
model_list = [ 'LOF', 'IForest', 'PCA', 'LSTMAD', 'USAD', 'AnomalyTransformer', 'TimesNet', 'Donut']
model_list = [ 'LSTMAD', 'USAD', 'AnomalyTransformer', 'TimesNet', 'Donut']
# model_list = [ 'LOF']


import subprocess
abs_file = __file__
import os

def run_evals(default_metric_list, model_type_list):
    abs_dir = os.path.dirname(abs_file)
    # cd到上一级
    abs_dir = os.path.abspath(os.path.join(abs_dir, '..'))
    # 然后到evaluation, eval_metrics
    work_dir = os.path.join(abs_dir, 'evaluation', 'eval_metrics')
    # 改变当前 Python 进程的工作目录
    os.chdir(work_dir)
    subprocess.run(['pwd'])
    # 将列表转换为字符串
    cmd = ['python3', 'eval_metric_real_model.py', 
            '--metric_list'] + default_metric_list + ['--model_list'] + model_type_list
    print("Running command:", ' '.join(cmd))
    subprocess.run(cmd)

run_evals(default_metric_list, model_list)