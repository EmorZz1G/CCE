# CCE 配置指南

本指南将帮助您配置CCE包，特别是数据集路径和其他重要设置。

## 🚀 快速开始

### 1. 安装后首次配置

安装CCE包后，建议首先创建用户配置文件：

```bash
# 创建默认配置文件
cce config create

# 或者指定配置文件位置
cce config create --path /path/to/your/config.yaml
```

### 2. 设置数据集路径

```bash
# 设置数据集目录路径
cce config set-datasets-path /path/to/your/datasets

# 查看当前配置
cce config show
```

## 📁 配置文件位置

CCE支持多种配置文件位置，按优先级排序：

1. **当前工作目录**: `./cce_config.yaml`
2. **用户主目录**: `~/.cce/config.yaml`
3. **环境变量**: `CCE_CONFIG_PATH` 指定的路径
4. **包默认配置**: 内置的默认配置

## ⚙️ 配置选项

### 基本配置

```yaml
# 数据集路径 - 支持绝对路径和相对路径
datasets_abs_path: ~/.cce/datasets

# 日志级别: DEBUG, INFO, WARNING, ERROR
log_level: INFO

# 缓存目录
cache_dir: ~/.cce/cache

# 最大工作线程数
max_workers: 4
```

### 评估配置

```yaml
evaluation:
  # 评估时的随机种子
  random_seed: 42
  
  # 是否保存中间结果
  save_intermediate: true
  
  # 结果保存目录
  results_dir: ~/.cce/results
```

### 数据集配置

```yaml
datasets:
  # 默认数据集格式
  default_format: csv
  
  # 是否自动下载缺失的数据集
  auto_download: false
  
  # 数据集缓存策略
  cache_strategy: memory
```

## 🔧 配置管理命令

### 创建配置文件

```bash
# 在默认位置创建配置文件
cce config create

# 在指定位置创建配置文件
cce config create --path /custom/path/config.yaml
```

### 查看当前配置

```bash
cce config show
```

### 设置数据集路径

```bash
# 设置绝对路径
cce config set-datasets-path /absolute/path/to/datasets

# 设置相对路径（相对于当前工作目录）
cce config set-datasets-path ./datasets
```

## 🌍 环境变量

您也可以通过环境变量来配置CCE：

```bash
# 设置配置文件路径
export CCE_CONFIG_PATH=/path/to/config.yaml

# 设置数据集路径
export CCE_DATASETS_PATH=/path/to/datasets
```

## 📝 配置文件示例

### 完整配置文件示例

```yaml
# CCE配置文件
# 数据集路径 - 请根据您的实际情况修改
datasets_abs_path: /home/user/datasets

# 日志配置
log_level: INFO

# 缓存配置
cache_dir: ~/.cce/cache

# 性能配置
max_workers: 4

# 评估配置
evaluation:
  random_seed: 42
  save_intermediate: true
  results_dir: ~/.cce/results

# 数据集配置
datasets:
  default_format: csv
  auto_download: false
  cache_strategy: memory
```

## 🚨 常见问题

### Q: 如何知道当前使用的配置文件？

A: 运行 `cce config show` 命令，它会显示当前配置的详细信息。

### Q: 数据集路径不存在怎么办？

A: CCE会自动尝试创建指定的数据集目录。如果创建失败，会使用默认路径 `~/.cce/datasets`。

### Q: 如何重置为默认配置？

A: 删除用户配置文件，CCE会自动使用默认配置：

```bash
rm ~/.cce/config.yaml
```

### Q: 配置文件格式错误怎么办？

A: CCE会显示错误信息并回退到默认配置。请检查YAML语法是否正确。

## 🔄 从旧版本迁移

如果您之前使用的是 `global_config.yaml` 文件，可以按以下步骤迁移：

1. 创建新的配置文件：
   ```bash
   cce config create
   ```

2. 将旧配置中的 `datasets_abs_path` 复制到新配置文件中

3. 删除旧的 `global_config.yaml` 文件

## 📞 获取帮助

如果您在配置过程中遇到问题，可以：

1. 查看配置帮助：
   ```bash
   cce config --help
   ```

2. 查看当前配置：
   ```bash
   cce config show
   ```

3. 查看版本信息：
   ```bash
   cce version
   ```