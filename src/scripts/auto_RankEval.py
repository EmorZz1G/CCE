
import subprocess
abs_file = __file__
import os

import argparse

task_type_list = ['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R']

argparser = argparse.ArgumentParser(description="Run ranking-based evaluation benchmark for model metrics.")
argparser.add_argument('--metric_list', type=str, nargs='+', default=['F1'], help='List of metrics to evaluate.')
argparser.add_argument('--task_list', type=str, nargs='+', default=task_type_list, help='List of model types to evaluate.')

args = argparser.parse_args()
metric_list = args.metric_list
task_type_list = args.task_list

def run_rank_eval():
    abs_dir = os.path.dirname(abs_file)
    # cd到上一级
    abs_dir = os.path.abspath(os.path.join(abs_dir, '..'))
    # 然后到evaluation, eval_metrics
    work_dir = os.path.join(abs_dir, 'evaluation', 'eval_metrics')
    # 改变当前 Python 进程的工作目录
    os.chdir(work_dir)
    subprocess.run(['pwd'])
    
    print("Running ranking-based evaluation benchmark for model metrics...")

    print("Task types:", task_type_list)
    for baseline in metric_list:
        for task_type in task_type_list:
            cmd = ['python3', 'eval_latency_baselines.py', '-M', task_type, '-B', baseline, '-L', f'{task_type}_log.csv']
            print("Running command:", ' '.join(cmd))
            subprocess.run(cmd)

    print("Running evaluation by real model...")
    cmd = ['python3', 'eval_metric_real_model.py', 
            '--metric_list'] + metric_list + ['--model_list'] + task_type_list
    print("Running command:", ' '.join(cmd))
    subprocess.run(cmd)

if __name__ == "__main__":
    # Ensure the script is run directly and not imported
    run_rank_eval()