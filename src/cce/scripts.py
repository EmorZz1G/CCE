#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Scripts module for CCE package.
This module imports scripts from the src/scripts directory.
"""

import sys
from pathlib import Path

# Add src directory to path if not already there
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import all from scripts module
from .scripts import *

__all__ = [
    'run_real_world',
    'run_baseline',
    'auto_RankEval',
] 