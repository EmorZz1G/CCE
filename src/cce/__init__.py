#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection

A comprehensive framework for evaluating time series anomaly detection methods
with confidence-consistency metrics.
"""

__version__ = "0.2.0"
__author__ = "EmorZz1G"
__email__ = "csemor@mail.scut.edu.cn"
__license__ = "MIT"
__url__ = "https://github.com/EmorZz1G/CCE"

import sys
from pathlib import Path

# 确保src目录在Python搜索路径中（关键：让解释器能找到平级包）
src_path = Path(__file__).parent.parent  # __file__是src/cce/__init__.py，parent.parent是src
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


# 导入cce内部模块（相对导入，正确）
from . import config
from . import cli

# 导入平级包（evaluation、models等与cce平级，在src目录下）
try:
    import evaluation
    import models
    import metrics
    import utils
    import data_utils
    
    # 关键：在sys.modules中注册这些模块，使其看起来像是cce的子包
    sys.modules['cce.evaluation'] = evaluation
    sys.modules['cce.models'] = models
    sys.modules['cce.metrics'] = metrics
    sys.modules['cce.utils'] = utils
    sys.modules['cce.data_utils'] = data_utils
    
    # print("📌 已将平级包绑定到 cce 命名空间")
    # print(f"cce 包路径：{__file__}")
    # print(f"cce.evaluation 路径：{evaluation.__file__}")
    
except ImportError as e:
    print(f"❌ 导入平级包失败: {e}")
    # 如果导入失败，设置为None
    globals()['evaluation'] = None
    globals()['models'] = None
    globals()['metrics'] = None
    globals()['utils'] = None
    globals()['data_utils'] = None

# 定义from cce import *时导出的内容
__all__ = [
    '__version__',
    '__author__', 
    '__email__',
    '__license__',
    '__url__',
    'config',
    'cli',
    'evaluation',
    'models', 
    'metrics',
    'utils',
    'data_utils',
]

# 自动创建全局配置（保持不变）
def _auto_create_global_config():
    """Automatically create global configuration if it doesn't exist"""
    try:
        from pathlib import Path
        home_config_path = Path.home() / '.cce' / 'config.yaml'
        
        if not home_config_path.exists():
            from .config import create_install_config
            create_install_config()
            print("✅ CCE global configuration auto-created")
            print("💡 Use 'cce config create' in your projects to copy this configuration")
    except Exception:
        # 静默失败，用户可后续手动创建
        pass

# 执行自动配置
_auto_create_global_config()
del _auto_create_global_config
