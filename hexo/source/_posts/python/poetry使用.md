---
title: Poetry在Mac上构建项目的全流程指南
tags: Poetry
categories:
  - Poetry
top: true
keywords: Poetry
abbrlink: 6821884a
date: 2025-09-03 10:00:00
---

# Poetry在Mac上构建项目的全流程指南

## 一、安装Poetry

在Mac上有几种安装Poetry的方法：

### 方法1：使用Homebrew（推荐）
```bash
# 安装Homebrew（如果尚未安装）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 使用Homebrew安装Poetry
brew install poetry
```
Homebrew是macOS的包管理器，通过它安装Poetry最为便捷。

### 方法2：使用官方安装脚本
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
此命令会下载并运行官方安装脚本。

### 验证安装
```bash
poetry --version
```

### 配置环境变量（如果需要）
如果使用官方脚本安装，可能需要将Poetry添加到PATH：
```bash
# 对于Zsh用户
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```
这将把Poetry添加到你的shell配置中。

## 二、创建新项目

### 1. 创建新项目
```bash
poetry new my-project
cd my-project
```
这会创建一个包含基本项目结构的目录，包括pyproject.toml文件和src目录。

### 2. 项目结构说明
```
my-project/
├── pyproject.toml  # 项目配置文件
├── README.md
├── my_project/     # 源代码目录
│   └── __init__.py
└── tests/          # 测试目录
    ├── __init__.py
    └── test_my_project.py
```

## 三、配置项目

### 1. 编辑pyproject.toml
打开pyproject.toml文件，配置项目信息：
```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "一个示例项目"
authors = ["Your Name <your.email@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.8"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

### 2. 配置虚拟环境（可选但推荐）
```bash
poetry config virtualenvs.in-project true
```
这会将虚拟环境创建在项目目录中（.venv文件夹），便于团队协作。

## 四、添加依赖

### 1. 添加主依赖
```bash
poetry add requests
```
这会安装requests库并自动更新pyproject.toml和poetry.lock文件。

### 2. 添加开发依赖（如测试框架）
```bash
poetry add --group dev pytest black
```
使用`--group dev`参数添加仅用于开发的依赖。

## 五、开发环境设置

### 1. 安装项目依赖
```bash
poetry install
```
此命令会根据pyproject.toml安装所有依赖，并创建虚拟环境（如果尚未创建）。

### 2. 激活虚拟环境
```bash
poetry shell
```
这会启动一个新的shell会话，其中已激活项目的虚拟环境。

或者，不激活环境直接运行命令：
```bash
poetry run python your_script.py
```

## 六、编写代码

1. 在`src/my_project/`目录下编写你的Python代码
2. 在`tests/`目录下编写测试代码

示例：编辑`src/my_project/__init__.py`
```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

## 七、运行测试

1. 编写测试文件`tests/test_my_project.py`：
```python
from my_project import greet

def test_greet():
    assert greet("World") == "Hello, World!"
```

2. 运行测试：
```bash
poetry run pytest
```
这会使用项目虚拟环境中的pytest运行测试。

## 八、构建和发布项目

### 1. 构建项目
```bash
poetry build
```
这会生成dist目录，包含wheel和源码分发包。

### 2. 发布到PyPI（可选）
```bash
# 首先配置PyPI令牌
poetry config pypi-token.pypi your-api-token

# 然后发布
poetry publish
```

## 九、常用命令总结

| 命令 | 说明 |
|------|------|
| `poetry init` | 交互式创建新项目（现有目录）|
| `poetry add package` | 添加依赖 |
| `poetry remove package` | 移除依赖 |
| `poetry update` | 更新所有依赖 |
| `poetry show --tree` | 查看依赖树 |
| `poetry env info` | 查看虚拟环境信息 |
| `poetry run command` | 在虚拟环境中运行命令 |

Poetry会自动管理项目环境隔离，确保工作始终与全局Python安装隔离。

## 十、完整工作流程示例

```bash
# 1. 创建并进入项目目录
mkdir myapp && cd myapp

# 2. 初始化项目
poetry init  # 交互式创建

# 3. 配置虚拟环境在项目内
poetry config virtualenvs.in-project true

# 4. 添加依赖
poetry add flask
poetry add --group dev pytest

# 5. 创建源代码目录和文件
mkdir -p src/myapp
echo 'def hello(): return "Hello World!"' > src/myapp/__init__.py

# 6. 创建测试
mkdir tests
echo 'from myapp import hello; def test_hello(): assert hello() == "Hello World!"' > tests/test_app.py

# 7. 运行测试
poetry run pytest

# 8. 构建项目
poetry build
```

通过以上步骤，你可以在Mac上使用Poetry完整地创建、开发和构建Python项目。