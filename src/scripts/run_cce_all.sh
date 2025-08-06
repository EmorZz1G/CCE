#!/bin/bash
pwd
# model_typs=('AccQ' 'LowDisAccQ' 'PreQ-NegP' 'AccQ-R' 'LowDisAccQ-R' 'PreQ-NegP-R')
# log_dirs=('AccQ_log.csv' 'LowDisAccQ_log.csv' 'PreQ-NegP_log.csv' 'AccQ-R_log.csv' 'LowDisAccQ-R_log.csv' 'PreQ-NegP-R_log.csv')
model_typs=('LowDisAccQ' 'PreQ-NegP' 'AccQ-R' 'LowDisAccQ-R' 'PreQ-NegP-R')
log_dirs=('LowDisAccQ_log.csv' 'PreQ-NegP_log.csv' 'AccQ-R_log.csv' 'LowDisAccQ-R_log.csv' 'PreQ-NegP-R_log.csv')
# 构造一个数组
for i in "${!model_typs[@]}"; do
    echo "Running model type: ${model_typs[$i]}"
    python evaluation/eval_metrics/eval_latency.py --log_filename "${log_dirs[$i]}" --model_type "${model_typs[$i]}" -A
done