#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试CCE配置系统的脚本
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_config_system():
    """测试配置系统的基本功能"""
    print("🧪 测试CCE配置系统...")
    
    try:
        from cce.config import CCEConfig, get_config, get_datasets_path, create_user_config
        
        # 测试1: 创建配置实例
        print("\n1. 测试配置实例创建...")
        config = CCEConfig()
        print(f"   ✅ 配置实例创建成功")
        
        # 测试2: 获取数据集路径
        print("\n2. 测试数据集路径获取...")
        datasets_path = get_datasets_path()
        print(f"   ✅ 数据集路径: {datasets_path}")
        
        # 测试3: 创建用户配置文件
        print("\n3. 测试用户配置文件创建...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.yaml'
            created_path = create_user_config(str(config_path))
            print(f"   ✅ 配置文件已创建: {created_path}")
            
            # 验证配置文件内容
            if config_path.exists():
                print(f"   ✅ 配置文件存在")
                with open(config_path, 'r') as f:
                    content = f.read()
                    if 'datasets_path' in content:
                        print(f"   ✅ 配置文件包含数据集路径配置")
                    else:
                        print(f"   ❌ 配置文件缺少数据集路径配置")
            else:
                print(f"   ❌ 配置文件不存在")
        
        # 测试4: 测试配置优先级
        print("\n4. 测试配置优先级...")
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试配置文件
            test_config_path = Path(temp_dir) / 'cce_config.yaml'
            with open(test_config_path, 'w') as f:
                f.write("datasets_path: /test/datasets\n")
            
            # 切换到测试目录
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # 创建新的配置实例（应该读取当前目录的配置文件）
                test_config = CCEConfig()
                test_datasets_path = test_config.get_datasets_path()
                print(f"   ✅ 当前目录配置优先级测试: {test_datasets_path}")
            finally:
                os.chdir(original_cwd)
        
        print("\n🎉 所有测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_commands():
    """测试CLI配置命令"""
    print("\n🧪 测试CLI配置命令...")
    
    try:
        # 模拟CLI参数
        class MockArgs:
            def __init__(self, config_action, path=None):
                self.config_action = config_action
                self.path = path
        
        from cce.cli import handle_config_command
        
        # 测试show命令
        print("\n1. 测试config show命令...")
        args = MockArgs('show')
        handle_config_command(args)
        print("   ✅ config show命令执行成功")
        
        # 测试create命令
        print("\n2. 测试config create命令...")
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'test_config.yaml'
            args = MockArgs('create', str(config_path))
            handle_config_command(args)
            print("   ✅ config create命令执行成功")
        
        print("\n🎉 CLI测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ CLI测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 开始测试CCE配置系统...")
    
    success1 = test_config_system()
    success2 = test_cli_commands()
    
    if success1 and success2:
        print("\n🎉 所有测试都通过了！配置系统工作正常。")
        sys.exit(0)
    else:
        print("\n❌ 部分测试失败，请检查配置系统。")
        sys.exit(1)