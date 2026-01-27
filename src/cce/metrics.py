#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Metrics module for CCE package.
This module imports metrics from the src/metrics directory.
"""

import sys
from pathlib import Path

# Add src directory to path if not already there
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import all from metrics module in src directory
import metrics
from metrics import *

__all__ = [
    'basic_metrics',
    'precision_at_k',
    'fc_score',
    'evaluate_utils',
    'f1_series',
    'customizable_f1_score',
    'combine_all_scores',
    'Matthews_correlation_coefficient',
    'AUC',
] 