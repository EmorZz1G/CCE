# default_baseline_list = ['CCE', 'F1', 'F1-PA', 'Reduced-F1', 'R-based F1', 'eTaPR', 'Aff-F1', 'UAff-F1', 'AUC-ROC', 'VUS-ROC']
# model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']

# default_baseline_list = ['CCE']
# model_type_list = ['AccQ']

default_baseline_list = ['F1']
model_type_list = ['LowDisAccQ-R', 'PreQ-NegP-R']

import subprocess
abs_file = __file__
import os

def run_evals(default_baseline_list, model_type_list):
    abs_dir = os.path.dirname(abs_file)
    # cd到上一级
    abs_dir = os.path.abspath(os.path.join(abs_dir, '..'))
    # 然后到evaluation, eval_metrics
    work_dir = os.path.join(abs_dir, 'evaluation', 'eval_metrics')
    # 改变当前 Python 进程的工作目录
    os.chdir(work_dir)
    subprocess.run(['pwd'])
    for baseline in default_baseline_list:
        for model_type in model_type_list:
            cmd = ['python3', 'eval_latency_baselines.py', '-M', model_type, '-B', baseline, '-L', f'{model_type}_log.csv']
            print("Running command:", ' '.join(cmd))
            subprocess.run(cmd)

# run_evals(default_baseline_list, model_type_list)

# default_baseline_list = ['F1-PA', 'Reduced-F1', 'R-based F1', 'AUC-ROC']
# model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
# run_evals(default_baseline_list, model_type_list)

# default_baseline_list = ['eTaPR', 'Aff-F1', 'UAff-F1', 'VUS-ROC']
# model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
# run_evals(default_baseline_list, model_type_list)
            

# default_baseline_list = ['eTaPR','UAff-F1']
# model_type_list = ['AccQ-R']
# run_evals(default_baseline_list, model_type_list)


default_baseline_list = ['PATE']
model_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']
run_evals(default_baseline_list, model_type_list)