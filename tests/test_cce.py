
import cce
import numpy as np
labels = np.array([0, 1, 1, 0, 0]).astype(np.float32)
scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5]).astype(np.float32)

from cce import metrics
metricor = metrics.basic_metricor()
CCE_score = metricor.metric_CCE(labels, scores)

print(f"CCE: {CCE_score}")

# 打印 cce 包信息（确认路径正确）
print(f"cce 包路径：{cce.__file__}")

# 验证 evaluation 是否绑定成功
try:
    print(f"cce.evaluation 路径：{cce.evaluation.__file__}")
    from cce.evaluation import eval_metrics
    print("✅ 成功从 cce.evaluation 导入 eval_metrics")
except AttributeError:
    print("❌ cce 包中没有 evaluation 属性")
except ImportError as e:
    print(f"❌ 从 cce.evaluation 导入失败：{e}")