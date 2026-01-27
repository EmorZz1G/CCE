import cce
print(cce.__package__)
from cce import evaluation, data_utils, metrics
import cce.evaluation
from cce.metrics import basic_metricor
tmp = basic_metricor()
print("CCE测试：成功导入cce包及其子模块，basic_metricor实例：", tmp)

metricor = cce.metrics.basic_metricor()
tmp2 = metrics.basic_metricor()
print("CCE测试：成功通过cce.metrics导入basic_metricor实例：", tmp2)