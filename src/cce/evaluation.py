#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Evaluation module for CCE package.
This module imports evaluation from the src/evaluation directory.
"""

import sys
from pathlib import Path

# Add src directory to path if not already there
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import all from evaluation module
from . import evaluation

__all__ = [
    'eval_metrics',
    'analysis_metrics',
]
