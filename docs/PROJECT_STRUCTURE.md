# CCE 项目结构说明

## 📁 目录结构

```
CCE/
├── README.md              # 项目主要说明文档
├── README_ZH.md           # 中文说明文档
├── LICENSE                # MIT 许可证
├── requirements.txt       # Python 依赖包列表
├── setup.py               # 简化的安装入口点
├── global_config.yaml     # 全局配置文件
├── .gitignore             # Git 忽略文件配置
├── .gitattributes         # Git 属性配置
├── PROJECT_STRUCTURE.md   # 本文件
│
├── src/                   # 源代码目录
│   └── cce/              # CCE 包源码
│       ├── __init__.py   # 包初始化文件
│       ├── cli.py        # 命令行接口
│       ├── metrics/      # 指标实现
│       ├── evaluation/   # 评估框架
│       ├── models/       # 模型实现
│       ├── data_utils/   # 数据处理工具
│       ├── utils/        # 辅助函数
│       └── scripts/      # 执行脚本
│
├──                  # 构建和安装相关文件
│   ├── README.md         # 构建说明
│   ├── setup.py          # 完整的包安装配置
│   ├── pyproject.toml    # 现代 Python 包管理配置
│   ├── MANIFEST.in       # 分发包文件包含配置
│   ├── BUILD.md          # 详细构建指南
│   ├── INSTALL.md        # 快速安装指南
│   └── test_installation.py # 安装验证脚本
│
├── datasets/              # 数据集存储目录
├── logs/                  # 评估结果日志
├── logs_backup/           # 日志备份
├── tests/                 # 测试文件
└── docs/                  # 项目文档
```

## 🎯 设计理念

### 根目录保持简洁
- 只保留用户最需要的文件
- 核心文档：README.md, LICENSE
- 基本配置：requirements.txt, global_config.yaml
- 简单入口：setup.py

### 构建文件集中管理
- 所有构建相关文件放在 `` 目录
- 便于维护和版本控制
- 不影响项目根目录的整洁性

### 源码结构清晰
- `src/cce/` 作为主要包目录
- 按功能模块组织代码
- 支持标准的 Python 包结构

## 🚀 使用方式

### 用户安装
```bash
# 从根目录安装（推荐）
pip install -e .

# 或从 build 目录安装
cd build && pip install -e .
```

### 开发者构建
```bash
# 构建分发包
cd build && python -m build

# 运行测试
cd build && python test_installation.py
```

### 发布到 PyPI
```bash
cd build
python -m build
twine upload dist/*
```

## 📝 文件说明

### 根目录文件
- `README.md`: 项目主要说明，包含安装和使用指南
- `setup.py`: 简化的安装入口，引用 build 目录中的完整配置
- `requirements.txt`: 核心依赖包列表
- `global_config.yaml`: 全局配置文件

###  目录文件
- `setup.py`: 完整的包安装配置
- `pyproject.toml`: 现代 Python 包管理配置
- `MANIFEST.in`: 指定分发包中包含的文件
- `BUILD.md`: 详细的构建和发布指南
- `INSTALL.md`: 快速安装指南
- `test_installation.py`: 安装验证脚本

## 🔧 维护说明

### 更新包配置
1. 修改 `setup.py` 或 `pyproject.toml`
2. 测试安装：`python setup.py --help`
3. 验证功能：`cd build && python test_installation.py`

### 添加新依赖
1. 更新 `requirements.txt`
2. 更新 `setup.py` 中的 `install_requires`
3. 更新 `pyproject.toml` 中的 `dependencies`

### 发布新版本
1. 更新版本号（在 build 目录的配置文件中）
2. 构建分发包：`cd build && python -m build`
3. 上传到 PyPI：`twine upload dist/*`

## ✅ 优势

1. **整洁性**: 根目录只保留必要文件
2. **可维护性**: 构建文件集中管理
3. **兼容性**: 支持多种安装方式
4. **标准化**: 遵循 Python 包开发最佳实践
5. **用户友好**: 简单的安装和使用流程