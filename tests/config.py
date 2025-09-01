#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CCE配置管理模块

提供智能的配置加载功能，支持多种配置方式：
1. 用户主目录下的配置文件
2. 当前工作目录下的配置文件
3. 环境变量
4. 默认配置
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class CCEConfig:
    """CCE配置管理器"""
    
    def __init__(self):
        self.config = {}
        self._load_config()
    
    def _get_config_paths(self) -> list:
        """获取可能的配置文件路径，按优先级排序"""
        paths = []
        
        # 1. 当前工作目录下的.cce文件夹（最高优先级）
        project_cce_config = Path.cwd() / '.cce' / 'config.yaml'
        if project_cce_config.exists():
            paths.append(project_cce_config)
        
        # 2. 当前工作目录
        cwd_config = Path.cwd() / 'cce_config.yaml'
        if cwd_config.exists():
            paths.append(cwd_config)
        
        # 3. 用户主目录
        home_config = Path.home() / '.cce' / 'config.yaml'
        if home_config.exists():
            paths.append(home_config)
        
        # 4. 环境变量指定的路径
        env_config = os.environ.get('CCE_CONFIG_PATH')
        if env_config and Path(env_config).exists():
            paths.append(Path(env_config))
        
        # 5. 包内默认配置
        package_config = Path(__file__).parent / 'default_config.yaml'
        if package_config.exists():
            paths.append(package_config)
        
        return paths
    
    def _load_config(self):
        """加载配置文件"""
        config_paths = self._get_config_paths()
        
        if not config_paths:
            logger.warning("未找到配置文件，使用默认配置")
            self._set_default_config()
            return
        
        # 使用第一个找到的配置文件
        config_path = config_paths[0]
        logger.info(f"加载配置文件: {config_path}")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            self._set_default_config()
            return
        
        # 处理数据集路径
        self._process_datasets_path()
    
    def _process_datasets_path(self):
        """处理数据集路径配置"""
        datasets_path = self.config.get('datasets_path')
        
        if datasets_path:
            # 展开波浪号路径
            datasets_path = os.path.expanduser(datasets_path)
            
            # 如果是相对路径，转换为绝对路径
            if not os.path.isabs(datasets_path):
                datasets_path = os.path.abspath(datasets_path)
            
            # 检查路径是否存在
            if not os.path.exists(datasets_path):
                logger.warning(f"数据集路径不存在: {datasets_path}")
                # 尝试创建目录
                try:
                    os.makedirs(datasets_path, exist_ok=True)
                    logger.info(f"已创建数据集目录: {datasets_path}")
                except Exception as e:
                    logger.error(f"无法创建数据集目录: {e}")
                    # 使用默认路径
                    datasets_path = self._get_default_datasets_path()
            else:
                logger.info(f"使用数据集路径: {datasets_path}")
        else:
            # 使用默认路径
            datasets_path = self._get_default_datasets_path()
        
        self.config['datasets_path'] = datasets_path
    
    def _get_default_datasets_path(self) -> str:
        """获取默认数据集路径"""
        # 优先使用项目目录下的.cce/datasets
        project_datasets = Path.cwd() / '.cce' / 'datasets'
        project_datasets.mkdir(parents=True, exist_ok=True)
        return str(project_datasets)
    
    def _set_default_config(self):
        """设置默认配置"""
        self.config = {
            'datasets_path': self._get_default_datasets_path(),
            'log_level': 'INFO',
            'cache_dir': str(Path.cwd() / '.cce' / 'cache'),
            'max_workers': 8
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
    
    def get_datasets_path(self) -> str:
        """获取数据集路径"""
        return self.config.get('datasets_path', self._get_default_datasets_path())
    
    def create_install_config(self) -> str:
        """安装时在home目录创建默认配置文件"""
        home_config_path = Path.home() / '.cce' / 'config.yaml'
        home_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            'datasets_path': str(Path.home() / '.cce' / 'datasets'),
            'log_level': 'INFO',
            'cache_dir': str(Path.home() / '.cce' / 'cache'),
            'max_workers': 4,
            'comment': 'CCE全局配置文件 - 安装时自动创建'
        }
        
        with open(home_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"已创建全局配置文件: {home_config_path}")
        return str(home_config_path)
    
    def copy_home_config_to_project(self, project_config_path: Optional[str] = None) -> str:
        """复制home配置到当前项目目录"""
        home_config_path = Path.home() / '.cce' / 'config.yaml'
        
        if not home_config_path.exists():
            logger.warning("Home目录配置文件不存在，将创建默认配置")
            self.create_install_config()
        
        if project_config_path is None:
            project_config_path = Path.cwd() / '.cce' / 'config.yaml'
        
        project_config_path = Path(project_config_path)
        project_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取home配置并调整路径
        with open(home_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f) or {}
        
        # 调整路径为项目相对路径
        config['datasets_path'] = str(Path.cwd() / '.cce' / 'datasets')
        config['cache_dir'] = str(Path.cwd() / '.cce' / 'cache')
        config['comment'] = 'CCE项目配置文件 - 从全局配置复制而来'
        
        with open(project_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"已复制配置到项目目录: {project_config_path}")
        return str(project_config_path)
    
    def create_user_config(self, config_path: Optional[str] = None, use_default: bool = False) -> str:
        """为用户创建配置文件
        
        Args:
            config_path: 配置文件路径，默认为当前目录的.cce/config.yaml
            use_default: 是否使用默认配置，False时复制home配置，True时生成默认配置
        """
        if config_path is None:
            config_path = Path.cwd() / '.cce' / 'config.yaml'
        
        if use_default:
            # 生成默认配置
            return self._create_default_config(config_path)
        else:
            # 复制home配置
            return self.copy_home_config_to_project(config_path)
    
    def _create_default_config(self, config_path: str) -> str:
        """创建默认配置文件"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        default_config = {
            'datasets_path': str(Path.cwd() / '.cce' / 'datasets'),
            'log_level': 'INFO',
            'cache_dir': str(Path.cwd() / '.cce' / 'cache'),
            'max_workers': 4,
            'comment': 'CCE项目配置文件 - 默认配置'
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        logger.info(f"已创建默认配置文件: {config_path}")
        return str(config_path)


# 全局配置实例
config = CCEConfig()


def get_config() -> CCEConfig:
    """获取全局配置实例"""
    return config


def get_datasets_path() -> str:
    """获取数据集路径的便捷函数"""
    return config.get_datasets_path()


def create_install_config() -> str:
    """安装时创建全局配置文件的便捷函数"""
    return config.create_install_config()


def create_user_config(config_path: Optional[str] = None, use_default: bool = False) -> str:
    """创建用户配置文件的便捷函数
    
    Args:
        config_path: 配置文件路径，默认为当前目录的.cce/config.yaml
        use_default: 是否使用默认配置，False时复制home配置，True时生成默认配置
    """
    return config.create_user_config(config_path, use_default)


def copy_home_config_to_project(project_config_path: Optional[str] = None) -> str:
    """复制home配置到当前项目目录的便捷函数"""
    return config.copy_home_config_to_project(project_config_path)