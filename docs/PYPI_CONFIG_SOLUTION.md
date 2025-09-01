# PyPI发布配置问题解决方案

## 🎯 问题描述

在发布CCE包到PyPI时，原有的配置系统存在以下问题：

1. **硬编码路径问题**：`global_config.yaml` 中的 `datasets_abs_path` 是绝对路径，用户无法使用
2. **配置文件位置问题**：代码中硬编码了配置文件路径，用户安装后可能找不到
3. **用户体验问题**：用户需要手动创建和配置 `global_config.yaml` 文件

## 🛠️ 解决方案

### 1. 智能配置加载系统

创建了新的配置管理模块 `src/cce/config.py`，支持多种配置方式：

- **当前工作目录**: `./cce_config.yaml`
- **用户主目录**: `~/.cce/config.yaml`
- **环境变量**: `CCE_CONFIG_PATH` 指定的路径
- **包默认配置**: 内置的默认配置

### 2. 用户友好的CLI命令

添加了配置管理命令：

```bash
# 创建配置文件
cce config create

# 设置数据集路径
cce config set-datasets-path /path/to/datasets

# 查看当前配置
cce config show
```

### 3. 向后兼容性

更新了 `eval_utils.py`，使其能够：
- 优先使用新的配置系统
- 如果新系统不可用，回退到原有的配置方式
- 保持与现有代码的兼容性

## 📁 新增文件

### 核心文件
- `src/cce/config.py` - 配置管理模块
- `src/cce/default_config.yaml` - 默认配置文件

### 文档文件
- `docs/CONFIGURATION_GUIDE.md` - 详细配置指南
- `docs/PYPI_CONFIG_SOLUTION.md` - 本解决方案文档

### 构建文件
- `MANIFEST.in` - 确保配置文件被包含在分发包中

## 🔧 修改的文件

### 1. `setup.py`
- 添加了 `package_data` 配置，包含默认配置文件
- 确保配置文件被正确打包

### 2. `src/cce/cli.py`
- 添加了配置管理命令
- 实现了配置文件的创建、查看和修改功能

### 3. `src/evaluation/eval_metrics/eval_utils.py`
- 更新为使用新的配置系统
- 保持向后兼容性

### 4. `README.md`
- 添加了配置相关的快速开始指南

## 🚀 使用方法

### 用户安装后配置

```bash
# 1. 安装包
pip install cce

# 2. 创建配置文件
cce config create

# 3. 设置数据集路径
cce config set-datasets-path /path/to/your/datasets

# 4. 查看配置
cce config show
```

### 开发者配置

```python
from cce.config import get_config, get_datasets_path

# 获取配置实例
config = get_config()

# 获取数据集路径
datasets_path = get_datasets_path()

# 获取其他配置
log_level = config.get('log_level', 'INFO')
```

## ✅ 测试验证

配置系统已经过测试验证：

1. **基本功能测试**：配置加载、路径解析、文件创建
2. **CLI命令测试**：所有配置管理命令正常工作
3. **向后兼容性测试**：与现有代码兼容
4. **路径处理测试**：支持绝对路径、相对路径和波浪号路径

## 🎉 优势

1. **用户友好**：简单的CLI命令，无需手动编辑配置文件
2. **灵活配置**：支持多种配置方式和优先级
3. **向后兼容**：不影响现有代码的使用
4. **自动处理**：自动创建目录，处理路径问题
5. **详细文档**：提供完整的配置指南

## 📝 注意事项

1. 用户首次使用时需要运行 `cce config create` 创建配置文件
2. 数据集路径会自动创建（如果不存在）
3. 支持环境变量 `CCE_CONFIG_PATH` 来指定配置文件位置
4. 配置文件使用YAML格式，支持中文注释

这个解决方案彻底解决了PyPI发布时的配置问题，为用户提供了简单易用的配置管理方式。