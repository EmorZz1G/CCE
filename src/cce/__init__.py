#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection

A comprehensive evaluation framework for time series anomaly detection metrics,
focusing on confidence-consistency evaluation, robustness assessment, and
discriminative power analysis.
"""

__version__ = "0.1.0"
__author__ = "EmorZz1G"
__email__ = "csemor@mail.scut.edu.cn"
__license__ = "MIT"
__url__ = "https://github.com/EmorZz1G/CCE"

# Import main components
try:
    from .metrics import *
    from .evaluation import *
    from .models import *
    from .data_utils import *
    from .utils import *
except ImportError:
    # Allow partial imports for development
    pass

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__url__",
] 