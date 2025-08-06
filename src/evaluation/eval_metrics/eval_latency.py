from eval_utils import ModelConfigUtils, generate_dataset, CASE_NUM, generate_real_world_dataset, REAL_WORLD_CASE_NUM
import os, sys
import numpy as np

fil_pth = os.path.dirname(os.path.abspath(__file__))
proj_pth = os.path.dirname(os.path.dirname(os.path.dirname(fil_pth)))
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

args = argparse.ArgumentParser()
args.add_argument('--log_filename', '-L', type=str, default='cce_log.csv', help='The filename for the latency log.', required=False)
args.add_argument('--log_append', '-A', action='store_true', help='Whether to append to the log file instead of overwriting it.', required=False)
args.add_argument('--model_type', '-M', type=str, default='AccQ', choices=['AccQ', 'LowDisAccQ', 'PreQ-NegP', 'AccQ-R', 'LowDisAccQ-R', 'PreQ-NegP-R'], help='The type of model to evaluate.', required=False)
args_config = args.parse_args()

log_file = os.path.join(log_pth, args_config.log_filename)
if args_config.log_append:
    pass
elif os.path.exists(log_file):
    print(f"Log file {log_file} already exists.")
    args_config.log_filename += f"_{int(time.time())}.csv"
    print(f"Renaming log file to {args_config.log_filename}.")

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
    print(f"{case_name}: {model_name} {metric_name} latency: {latency:.2f} ms")
    data_item['latency'] = latency
    log_data.append(data_item)
    # 将日志数据写入csv
    df = pd.DataFrame(log_data)
    if os.path.exists(os.path.join(log_pth, args_config.log_filename)) and not args_config.log_append:
        df.to_csv(os.path.join(log_pth, args_config.log_filename), index=False, mode='w', header=True)
    else:
        if not os.path.exists(os.path.join(log_pth, args_config.log_filename)):
            df.to_csv(os.path.join(log_pth, args_config.log_filename), index=False, mode='w', header=True)
        else:
            df.to_csv(os.path.join(log_pth, args_config.log_filename), index=False, mode='a', header=False)
        

model_utils = ModelConfigUtils()

model_list = model_utils.get_AccQ_list()

print(f"Model list: {model_list}")

# CASE_NUM = 1

def eval_latency(cnt=1):
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
                metricor = basic_metricor(case_name, labels, log_pth)
                # metricor.cal_unbiased_aff_prec_bias(labels)
                pred = metricor.get_pred(score)

                with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='F1') as data_item: 
                    F1 = metricor.metric_PointF1(labels, score, pred)
                    data_item['val'] = F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='F1-PA') as data_item: 
                #     F1PA, pre, rec = metricor.metric_PointF1PA(labels, score, pred)
                #     data_item['val'] = F1PA
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='Reduced-F1') as data_item:
                #     Reduced_F1, Pre, Rec = metricor.metric_Reduced_F1(labels, score, pred)
                #     data_item['val'] = Reduced_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='PA%K') as data_item:
                #     F1_Per_K, Prec_Per_K, Rec_Per_K = metricor.metric_PA_percentile_K(labels, score, pred)
                #     data_item['val'] = F1_Per_K
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='R-based F1') as data_item:
                #     RbasedF1 = metricor.metric_RF1(labels, score, pred)
                #     data_item['val'] = RbasedF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='TaPR') as data_item:
                #     TaF1, TaP, TaR = metricor.metric_TaPR_F1(labels, score, pred)
                #     data_item['val'] = TaF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='eTaPR') as data_item:
                #     eTaF1, eTaP, eTaR = metricor.metric_eTaPR_F1(labels, score, pred)
                #     data_item['val'] = eTaF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='Aff-F1') as data_item:
                #     Aff_F1, Aff_pre, Aff_rec = metricor.metric_Affiliation(labels, score, pred)
                #     data_item['val'] = Aff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='NAff-F1') as data_item:
                #     NAff_F1, NAff_pre, NAff_rec = metricor.metric_N_Affiliation_f1_pre_rec(labels, score, pred)
                #     data_item['val'] = NAff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='UAff-F1') as data_item:
                #     UAff_F1, UAff_pre, UAff_rec = metricor.metric_U_Affiliation_f1_pre_rec(labels, score, pred)
                #     data_item['val'] = UAff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='PATE') as data_item:
                #     PATE = metricor.metric_PATE(labels, score, n_jobs=100, num_desired_thresholds=100)
                #     data_item['val'] = PATE
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='AUC-ROC') as data_item:
                #     AUCROC = metricor.metric_ROC(labels, score)
                #     data_item['val'] = AUCROC
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='AUC-PR') as data_item:
                #     AUCPR = metricor.metric_PR(labels, score)
                #     data_item['val'] = AUCPR
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='VUS-ROC') as data_item:
                #     VUS_ROC = metricor.metric_VUS_ROC(labels, score, thre=100)
                #     data_item['val'] = VUS_ROC
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='VUS-PR') as data_item:
                #     VUS_PR = metricor.metric_VUS_PR(labels, score, thre=100)
                #     data_item['val'] = VUS_ROC
                with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='CCE') as data_item:
                    CCE = metricor.metric_CCE(labels, score)
                    data_item['val'] = CCE
        print(f"Finished evaluating case: {case_name}")

def eval_latency_real_world_case(cnt=5):
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
                # metricor.cal_unbiased_aff_prec_bias(labels)
                pred = metricor.get_pred(score)

                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='F1') as data_item: 
                #     F1 = metricor.metric_PointF1(labels, score, pred)
                #     data_item['val'] = F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='F1-PA') as data_item: 
                #     F1PA, pre, rec = metricor.metric_PointF1PA(labels, score, pred)
                #     data_item['val'] = F1PA
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='Reduced-F1') as data_item:
                #     Reduced_F1, Pre, Rec = metricor.metric_Reduced_F1(labels, score, pred)
                #     data_item['val'] = Reduced_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='PA%K') as data_item:
                #     F1_Per_K, Prec_Per_K, Rec_Per_K = metricor.metric_PA_percentile_K(labels, score, pred)
                #     data_item['val'] = F1_Per_K
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='R-based F1') as data_item:
                #     RbasedF1 = metricor.metric_RF1(labels, score, pred)
                #     data_item['val'] = RbasedF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='TaPR') as data_item:
                #     TaF1, TaP, TaR = metricor.metric_TaPR_F1(labels, score, pred)
                #     data_item['val'] = TaF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='eTaPR') as data_item:
                #     eTaF1, eTaP, eTaR = metricor.metric_eTaPR_F1(labels, score, pred)
                #     data_item['val'] = eTaF1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='Aff-F1') as data_item:
                #     Aff_F1, Aff_pre, Aff_rec = metricor.metric_Affiliation(labels, score, pred)
                #     data_item['val'] = Aff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='NAff-F1') as data_item:
                #     NAff_F1, NAff_pre, NAff_rec = metricor.metric_N_Affiliation_f1_pre_rec(labels, score, pred)
                #     data_item['val'] = NAff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='UAff-F1') as data_item:
                #     UAff_F1, UAff_pre, UAff_rec = metricor.metric_U_Affiliation_f1_pre_rec(labels, score, pred)
                #     data_item['val'] = UAff_F1
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='PATE') as data_item:
                #     PATE = metricor.metric_PATE(labels, score, n_jobs=100, num_desired_thresholds=100)
                #     data_item['val'] = PATE
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='AUC-ROC') as data_item:
                #     AUCROC = metricor.metric_ROC(labels, score)
                #     data_item['val'] = AUCROC
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='AUC-PR') as data_item:
                #     AUCPR = metricor.metric_PR(labels, score)
                #     data_item['val'] = AUCPR
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='VUS-ROC') as data_item:
                #     VUS_ROC = metricor.metric_VUS_ROC(labels, score, thre=100)
                #     data_item['val'] = VUS_ROC
                # with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='VUS-PR') as data_item:
                #     VUS_PR = metricor.metric_VUS_PR(labels, score, thre=100)
                #     data_item['val'] = VUS_ROC
                with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='CCE') as data_item:
                    CCE = metricor.metric_CCE(labels, score)
                    data_item['val'] = CCE

        
        print(f"Finished evaluating case: {case_name}")


if __name__ == "__main__":
    # eval_latency(cnt=3)
    eval_latency_real_world_case(cnt=3)
    print("Latency evaluation completed.")
