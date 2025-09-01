#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CCE Command Line Interface
Command line interface for the CCE (Confidence-Consistency Evaluation) framework.
"""

import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CCE: Confidence-Consistency Evaluation for Time Series Anomaly Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Configuration management
  cce config install           # Create global config in home directory
  cce config create            # Create project config (copy from home)
  cce config create --default  # Create project config with default settings
  cce config copy              # Copy home config to current project
  cce config show              # Show current configuration
  cce config set-datasets-path /path/to/datasets  # Set datasets path
  
  # Evaluation commands
  cce run-baseline             # Run baseline evaluation
  cce run-real-world           # Run real-world dataset evaluation
  cce add-metric NewMetric     # Add a new metric for evaluation
  
  # Other commands
  cce version                  # Show version information
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run baseline command
    baseline_parser = subparsers.add_parser(
        'run-baseline',
        help='Run baseline evaluation'
    )
    baseline_parser.add_argument(
        '--config',
        type=str,
        default='global_config.yaml',
        help='Configuration file path'
    )
    
    # Run real-world command
    realworld_parser = subparsers.add_parser(
        'run-real-world',
        help='Run real-world dataset evaluation'
    )
    realworld_parser.add_argument(
        '--config',
        type=str,
        default='global_config.yaml',
        help='Configuration file path'
    )
    
    # Add metric command
    metric_parser = subparsers.add_parser(
        'add-metric',
        help='Add a new metric for evaluation'
    )
    metric_parser.add_argument(
        'metric_name',
        type=str,
        help='Name of the new metric'
    )
    metric_parser.add_argument(
        '--description',
        type=str,
        help='Description of the metric'
    )
    
    # Config command
    config_parser = subparsers.add_parser(
        'config',
        help='Configuration management'
    )
    config_subparsers = config_parser.add_subparsers(dest='config_action', help='Config actions')
    
    # Install config command
    install_config_parser = config_subparsers.add_parser(
        'install',
        help='Create global configuration file in home directory'
    )
    
    # Create config command
    create_config_parser = config_subparsers.add_parser(
        'create',
        help='Create project configuration file'
    )
    create_config_parser.add_argument(
        '--path',
        type=str,
        help='Path where to create the config file (default: .cce/config.yaml)'
    )
    create_config_parser.add_argument(
        '--default',
        action='store_true',
        help='Create with default settings instead of copying from home'
    )
    
    # Copy config command
    copy_config_parser = config_subparsers.add_parser(
        'copy',
        help='Copy home configuration to current project'
    )
    copy_config_parser.add_argument(
        '--path',
        type=str,
        help='Path where to copy the config file (default: .cce/config.yaml)'
    )
    
    # Show config command
    show_config_parser = config_subparsers.add_parser(
        'show',
        help='Show current configuration'
    )
    
    # Set datasets path command
    set_datasets_parser = config_subparsers.add_parser(
        'set-datasets-path',
        help='Set the datasets directory path'
    )
    set_datasets_parser.add_argument(
        'path',
        type=str,
        help='Path to the datasets directory'
    )
    
    # Version command
    version_parser = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute commands
    if args.command == 'run-baseline':
        run_baseline(args.config)
    elif args.command == 'run-real-world':
        run_real_world(args.config)
    elif args.command == 'add-metric':
        add_metric(args.metric_name, args.description)
    elif args.command == 'config':
        handle_config_command(args)
    elif args.command == 'version':
        show_version()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()

def run_baseline(config_path):
    """Run baseline evaluation."""
    print("Running baseline evaluation...")
    try:
        # Import and run baseline evaluation
        from evaluation.eval_metrics.eval_latency_baselines import main as run_baseline_eval
        run_baseline_eval()
        print("Baseline evaluation completed successfully!")
    except ImportError as e:
        print(f"Error importing baseline evaluation: {e}")
        print("Please ensure you're running this from the CCE directory.")
    except Exception as e:
        print(f"Error running baseline evaluation: {e}")

def run_real_world(config_path):
    """Run real-world dataset evaluation."""
    print("Running real-world dataset evaluation...")
    try:
        # Import and run real-world evaluation
        from evaluation.eval_metrics.eval_latency_baselines import main as run_realworld_eval
        run_realworld_eval()
        print("Real-world evaluation completed successfully!")
    except ImportError as e:
        print(f"Error importing real-world evaluation: {e}")
        print("Please ensure you're running this from the CCE directory.")
    except Exception as e:
        print(f"Error running real-world evaluation: {e}")

def add_metric(metric_name, description):
    """Add a new metric for evaluation."""
    print(f"Adding new metric: {metric_name}")
    if description:
        print(f"Description: {description}")
    
    # This would typically involve:
    # 1. Creating metric implementation
    # 2. Adding evaluation logic
    # 3. Updating configuration files
    
    print("Metric addition functionality not yet implemented.")
    print("Please manually add the metric following the documentation.")

def handle_config_command(args):
    """Handle configuration management commands."""
    try:
        from cce.config import (
            get_config, 
            create_install_config, 
            create_user_config, 
            copy_home_config_to_project
        )
        config = get_config()
        
        if args.config_action == 'install':
            config_path = create_install_config()
            print(f"✅ 全局配置文件已创建: {config_path}")
            print("📝 请根据需要修改全局配置文件中的设置")
            print("💡 提示: 使用 'cce config create' 在新项目中复制此配置")
            
        elif args.config_action == 'create':
            config_path = create_user_config(args.path, args.default)
            if args.default:
                print(f"✅ 默认项目配置文件已创建: {config_path}")
            else:
                print(f"✅ 项目配置文件已创建: {config_path}")
                print("📋 已从全局配置复制设置，路径已调整为项目相对路径")
            print("📝 请根据需要修改项目配置文件中的设置")
            
        elif args.config_action == 'copy':
            config_path = copy_home_config_to_project(args.path)
            print(f"✅ 配置已复制到项目: {config_path}")
            print("📋 已从全局配置复制设置，路径已调整为项目相对路径")
            
        elif args.config_action == 'show':
            print("📋 当前配置:")
            print(f"  数据集路径: {config.get_datasets_path()}")
            print(f"  日志级别: {config.get('log_level', 'INFO')}")
            print(f"  缓存目录: {config.get('cache_dir', '~/.cce/cache')}")
            print(f"  最大工作线程: {config.get('max_workers', 4)}")
            
            # 显示配置文件来源
            from pathlib import Path
            project_config = Path.cwd() / '.cce' / 'config.yaml'
            home_config = Path.home() / '.cce' / 'config.yaml'
            
            if project_config.exists():
                print(f"📁 使用项目配置: {project_config}")
            elif home_config.exists():
                print(f"📁 使用全局配置: {home_config}")
            else:
                print("📁 使用默认配置")
            
        elif args.config_action == 'set-datasets-path':
            import yaml
            from pathlib import Path
            
            # 优先更新项目配置，如果不存在则创建
            project_config_path = Path.cwd() / '.cce' / 'config.yaml'
            project_config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 读取或创建配置
            if project_config_path.exists():
                with open(project_config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f) or {}
            else:
                # 如果项目配置不存在，尝试从home配置复制
                home_config_path = Path.home() / '.cce' / 'config.yaml'
                if home_config_path.exists():
                    with open(home_config_path, 'r', encoding='utf-8') as f:
                        user_config = yaml.safe_load(f) or {}
                    # 调整路径为项目相对路径
                    user_config['datasets_path'] = str(Path.cwd() / '.cce' / 'datasets')
                    user_config['cache_dir'] = str(Path.cwd() / '.cce' / 'cache')
                else:
                    user_config = {}
            
            # 更新数据集路径
            user_config['datasets_path'] = args.path
            
            # 保存配置
            with open(project_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(user_config, f, default_flow_style=False, allow_unicode=True)
            
            print(f"✅ 数据集路径已设置为: {args.path}")
            print(f"📁 配置文件位置: {project_config_path}")
            
        else:
            print("❌ 未知的配置操作")
            print("💡 可用操作: install, create, copy, show, set-datasets-path")
            
    except ImportError:
        print("❌ 无法导入配置模块，请确保CCE包已正确安装")
    except Exception as e:
        print(f"❌ 配置操作失败: {e}")

def show_version():
    """Show version information."""
    try:
        import cce
        print(f"CCE version: {getattr(cce, '__version__', '0.1.0')}")
    except ImportError:
        print("CCE version: 0.1.0 (development)")
    
    print("Python version:", sys.version)
    print("Platform:", sys.platform)

if __name__ == '__main__':
    main() 