
import cce

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