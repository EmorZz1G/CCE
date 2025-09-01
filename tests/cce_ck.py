#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection

A comprehensive framework for evaluating time series anomaly detection methods
with confidence-consistency metrics.
"""

__version__ = "0.1.3"
__author__ = "EmorZz1G"
__email__ = "csemor@mail.scut.edu.cn"
__license__ = "MIT"
__url__ = "https://github.com/EmorZz1G/CCE"

# Import main modules with proper relative imports
try:
    from . import config
    from . import cli
    from . import evaluation
    from . import models
    from . import metrics
    from . import utils
    from . import data_utils
except ImportError:
    print("ImportError")
    # Fallback for direct script execution
    import sys
    from pathlib import Path
    
    # Get absolute path to src/cce directory
    src_cce_path = Path(__file__).parent
    src_path = src_cce_path  # Get src directory
    
    # Add src to path for proper module resolution
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    # Import modules from src/cce
    import config
    import cli
    import evaluation
    import models
    import metrics
    import utils
    import data_utils


# Define what gets imported with "from cce import *"
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

# Auto-create global configuration on first import (if not exists)
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
        # Silently fail - user can manually create config later
        pass

# Run auto-setup
_auto_create_global_config()
del _auto_create_global_config