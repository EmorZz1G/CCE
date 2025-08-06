
## 使用方式
### 如何测评新的指标？
1. 在`CCE/src/metrics/basic_metrics.py`中引入指标，并增加新的函数，通常命名为`metric_XXX()`，例如`metric_F1(), metric_AUCROC()`。
2. 在`CCE/src/evaluation/eval_metrics/eval_latency_baselines.py`中增加新的指标评估，例如，下面是对`VUS-PR`的评估。你需要修改`baseline == 'NewMetric'`并传入正确的指标名字`metric_name='NewMetric'`。
    ```py
    elif baseline == 'VUS-PR':
        with timer(case_name, model_name, case_seed_new, score_seed_new, model, metric_name='VUS-PR') as data_item:
            VUS_PR = metricor.metric_VUS_PR(labels, score, thre=100)
            data_item['val'] = VUS_ROC
    ```
3. 执行指标评估脚本:

    `eval_latency_baselines.py --baseline NewMetric`
4. 随后会在`CCE/logs/NewMetric`中生成所有案例的测试结果。
5. **注意**，如果需要使用真实数据集，那么需要将数据集放置在`CCE/datasets`中。或者，你也可以设置全局配置，在`CCE/global_config.yaml`中修改`datasets_abs_path: ABSOLUTE/PATH/OF/DATASETS`。

## 支持的测评
1. 指标计算时延。
2. 根据理论排名排序，计算偏序对/总排序数

## Updates
1. 2025-08-05 开始项目（初始化代码，项目网站）

## TODO List
1. 增加不同的评估SOP

## Acknowledgment
1. 感谢FTSAD提供时序异常检测评估指标测试框架。我们在此基础上进行了扩展，增加了更多类型的测试。
2. 感谢TSB-AD提供许多模型的实现代码。