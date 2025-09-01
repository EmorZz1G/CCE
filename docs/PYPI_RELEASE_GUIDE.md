# CCE PyPI 发布指南

本指南将帮助您将CCE包发布到PyPI（Python Package Index）。

## 📋 发布前准备

### 1. 检查包配置

确保以下文件配置正确：

- `setup.py` - 包的基本信息
- `pyproject.toml` - 现代Python包配置
- `MANIFEST.in` - 包含的文件列表
- `README.md` - 项目说明文档
- `LICENSE` - 许可证文件

### 2. 更新版本号

在发布新版本前，需要更新版本号：

```bash
# 编辑 setup.py 和 pyproject.toml 中的版本号
# 例如：从 0.1.0 改为 0.1.1
```

### 3. 检查包名可用性

确保包名 `cce` 在PyPI上可用：

```bash
# 检查包名是否已被占用
pip search cce  # 如果命令可用
# 或者直接访问 https://pypi.org/project/cce/
```

## 配置API
vi ~/.pypirc

## 🛠️ 安装构建工具

```bash
# 安装必要的构建工具
pip install build wheel twine

# 或者使用conda
conda install build wheel twine
```

## 📦 构建分发包

### 1. 清理之前的构建

```bash
rm -rf dist/ build/ *.egg-info/ .eggs/ && python -m build
```

### 2. 构建分发包

```bash
python -m build

# 构建完成后，检查生成的文件
ls -la dist/
```

应该会生成以下文件：
- `dist/cce-0.1.0-py3-none-any.whl` (wheel包)
- `dist/cce-0.1.0.tar.gz` (源码包)

### 3. 检查构建的包

```bash
# 检查包的内容和元数据
twine check dist/*

# 如果检查通过，会显示：
# checking dist/cce-0.1.0-py3-none-any.whl: PASSED
# checking dist/cce-0.1.0.tar.gz: PASSED
```

## 🧪 测试发布

### 1. 发布到测试PyPI

首先发布到测试PyPI，确保一切正常：

```bash
# 上传到测试PyPI
twine upload --repository testpypi dist/*
# 上传到正式服PyPI
twine upload dist/*

# 系统会提示输入用户名和密码
# 用户名：您的PyPI用户名
# 密码：您的PyPI密码或API token
```

### 2. 从测试PyPI安装测试

```bash
# 从测试PyPI安装测试
pip install --index-url https://test.pypi.org/simple/ cce

# 测试安装是否成功
python -c "import cce; print(cce.__version__)"

# 测试命令行工具
cce --help
```

### 3. 卸载测试包

```bash
pip uninstall cce
```

## 🚀 正式发布

### 1. 发布到正式PyPI

如果测试PyPI上的包工作正常，就可以发布到正式PyPI：

```bash
# 上传到正式PyPI
twine upload dist/*

# 系统会提示输入用户名和密码
# 用户名：您的PyPI用户名
# 密码：您的PyPI密码或API token
```

### 2. 验证发布

```bash
# 等待几分钟让PyPI更新，然后安装测试
pip install cce

# 测试安装
python -c "import cce; print(cce.__version__)"
cce --help
```

## 🔐 PyPI账户设置

### 1. 创建PyPI账户

1. 访问 [https://pypi.org/account/register/](https://pypi.org/account/register/)
2. 创建账户并验证邮箱
3. 启用双因素认证（推荐）

### 2. 创建API Token

1. 登录PyPI
2. 进入 [Account Settings](https://pypi.org/manage/account/)
3. 滚动到 "API tokens" 部分
4. 点击 "Add API token"
5. 选择 "Entire account" 或 "Specific project"
6. 复制生成的token

### 3. 配置认证

创建 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

## 📝 发布检查清单

发布前请确认：

- [ ] 版本号已更新
- [ ] README.md 内容完整
- [ ] LICENSE 文件存在
- [ ] 所有依赖在 requirements.txt 中
- [ ] 代码已测试
- [ ] 包名在PyPI上可用
- [ ] 构建工具已安装
- [ ] 分发包构建成功
- [ ] twine check 通过
- [ ] 测试PyPI发布成功
- [ ] 从测试PyPI安装测试通过

## 🔄 更新版本

发布新版本时：

1. 更新版本号（在 `setup.py` 和 `pyproject.toml` 中）
2. 更新 CHANGELOG.md（如果有）
3. 重新构建分发包
4. 发布到PyPI

## 🆘 常见问题

### 1. 包名已被占用

如果包名 `cce` 已被占用，可以：
- 使用不同的包名，如 `cce-tsad`
- 联系包的原作者
- 使用带前缀的名称，如 `yourname-cce`

### 2. 构建失败

检查：
- Python版本兼容性
- 依赖包版本
- 文件路径是否正确

### 3. 上传失败

检查：
- 网络连接
- PyPI账户权限
- API token是否正确

### 4. 安装失败

检查：
- 包依赖是否完整
- 包结构是否正确
- 导入路径是否正确

## 📚 相关链接

- [PyPI官网](https://pypi.org/)
- [Python Packaging User Guide](https://packaging.python.org/)
- [setuptools文档](https://setuptools.pypa.io/)
- [twine文档](https://twine.readthedocs.io/)

## 🎉 发布成功

发布成功后，用户可以通过以下方式安装您的包：

```bash
pip install cce
```

您的包将在以下地址可见：
- https://pypi.org/project/cce/
- https://pypi.org/project/cce/#history