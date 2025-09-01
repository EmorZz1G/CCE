#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for CCE package.
This is a fallback setup.py for compatibility with older build tools.
The main configuration is in pyproject.toml.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from setuptools import setup, find_packages
    from setuptools.config import read_configuration
except ImportError:
    print("Error: setuptools is required to build this package")
    sys.exit(1)

# Read package metadata
def get_package_info():
    """Get package information from __init__.py"""
    init_file = Path(__file__).parent / "src" / "cce" / "__init__.py"
    if not init_file.exists():
        raise FileNotFoundError(f"Package init file not found: {init_file}")
    
    # Read version and metadata
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract metadata using simple parsing
    metadata = {}
    for line in content.split('\n'):
        if line.strip().startswith('__version__'):
            metadata['version'] = line.split('=')[1].strip().strip('"\'')
        elif line.strip().startswith('__author__'):
            metadata['author'] = line.split('=')[1].strip().strip('"\'')
        elif line.strip().startswith('__email__'):
            metadata['email'] = line.split('=')[1].strip().strip('"\'')
        elif line.strip().startswith('__license__'):
            metadata['license'] = line.split('=')[1].strip().strip('"\'')
        elif line.strip().startswith('__url__'):
            metadata['url'] = line.split('=')[1].strip().strip('"\'')
    
    return metadata

def get_long_description():
    """Get long description from README.md"""
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection"

def get_requirements():
    """Get requirements from requirements.txt"""
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

# Get package information
try:
    pkg_info = get_package_info()
except Exception as e:
    print(f"Warning: Could not read package info: {e}")
    pkg_info = {
        'version': '0.1.0',
        'author': 'EmorZz1G',
        'email': 'csemor@mail.scut.edu.cn',
        'license': 'MIT',
        'url': 'https://github.com/EmorZz1G/CCE'
    }

# Setup configuration
setup(
    name="cce",
    version=pkg_info['version'],
    author=pkg_info['author'],
    author_email=pkg_info['email'],
    maintainer=pkg_info['author'],
    maintainer_email=pkg_info['email'],
    description="Confidence-Consistency Evaluation for Time Series Anomaly Detection",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url=pkg_info['url'],
    project_urls={
        "Homepage": pkg_info['url'],
        "Documentation": f"{pkg_info['url']}#readme",
        "Repository": f"{pkg_info['url']}.git",
        "Issues": f"{pkg_info['url']}/issues",
    },
    license=pkg_info['license'],
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    package_data={
        "cce": ["*.yaml", "*.yml", "*.json", "*.txt"],
    },
    
    # Dependencies
    python_requires=">=3.8",
    install_requires=get_requirements(),
    
    # Optional dependencies
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
        "jupyter": [
            "jupyter>=1.0.0",
            "ipython>=7.0.0",
            "plotly>=5.0.0",
            "bokeh>=2.4.0",
            "streamlit>=1.20.0",
        ],
        "all": [
            "cce[dev,docs,jupyter]",
        ],
    },
    
    # Entry points
    entry_points={
        "console_scripts": [
            "cce=cce.cli:main",
        ],
    },
    
    # Classifiers
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Keywords
    keywords=[
        "time-series",
        "anomaly-detection",
        "evaluation",
        "metrics",
        "machine-learning",
        "confidence-consistency",
    ],
    
    # Zip safe
    zip_safe=False,
)