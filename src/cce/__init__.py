#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection

A comprehensive framework for evaluating time series anomaly detection methods
with confidence-consistency metrics.
"""

__author__ = "EmorZz1G"
__email__ = "csemor@mail.scut.edu.cn"
__license__ = "MIT"
__url__ = "https://github.com/EmorZz1G/CCE"

import sys
from pathlib import Path


from . import config
from . import cli

_submodules = ["evaluation", "models", "metrics", "data_utils"]

def __getattr__(name):
    if name in _submodules:
        import importlib
        return importlib.import_module(f".{name}", __name__)
    raise AttributeError(f"module {__name__} has no attribute {name}")

__all__ = _submodules + ['__version__', '__author__', '__email__', '__license__', '__url__']


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



# # 导入平级包（evaluation、models等与cce平级，在src目录下）
# try:
#     import evaluation
#     # 关键：在sys.modules中注册这些模块，使其看起来像是cce的子包
#     sys.modules['cce.evaluation'] = evaluation
    
# except ImportError as e:
#     try:
#         from src import evaluation
#         sys.modules['cce.evaluation'] = evaluation
#     except ImportError as e2:
#         print(f"❌ 备用导入平级包失败: {e2}")
#         # 如果导入失败，设置为None
#         globals()['evaluation'] = None

# try: 
#     import models

#     sys.modules['cce.models'] = models

# except ImportError as e:
#     try:
#         from src import models
#         sys.modules['cce.models'] = models
#     except ImportError as e2:
#         print(f"❌ 备用导入平级包失败: {e2}")
#         # 如果导入失败，设置为None  
#         globals()['models'] = None


# try: 
#     import utils
#     sys.modules['cce.utils'] = utils
# except ImportError as e:
#     try:
#         from src import utils
#         sys.modules['cce.utils'] = utils
#     except ImportError as e2:
#         print(f"❌ 备用导入平级包失败: {e2}")
#         # 如果导入失败，设置为None  
#         globals()['utils'] = None

# try: 
#     import data_utils
#     sys.modules['cce.data_utils'] = data_utils
# except ImportError as e:
#     try:
#         from src import data_utils
#         sys.modules['cce.data_utils'] = data_utils
#     except ImportError as e2:
#         print(f"❌ 备用导入平级包失败: {e2}")
#         # 如果导入失败，设置为None  
#         globals()['data_utils'] = None


# try: 
#     import metrics
#     sys.modules['cce.metrics'] = metrics
# except ImportError as e:
#     try:
#         from src import metrics
#         sys.modules['cce.metrics'] = metrics
#     except ImportError as e2:
#         print(f"❌ 备用导入平级包失败: {e2}")
#         # 如果导入失败，设置为None  
#         globals()['metrics'] = None
