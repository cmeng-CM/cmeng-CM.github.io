---
title: Ollama命令介绍
tags: AI
categories:
  - 理论知识
top: false
abbrlink: 44fab019
date: 2025-02-17 16:13:12
---

# Ollama CLI
Ollama 命令行工具 (`ollama`) 的主要实现代码，使用 Go 语言编写。它定义了 `ollama` 命令及其所有子命令（如 `run`, `pull`, `create` 等）的行为。

根据代码分析，以下是所有命令行操作及其具体含义：

1.  **`ollama` (根命令)**
    *   **用途**: 显示 Ollama CLI 的基本使用信息和可用命令列表。
    *   **参数**:
        *   `-v, --version`: 显示 Ollama 客户端和服务端（如果正在运行）的版本信息。

2.  **`ollama serve` (或 `ollama start`)**
    *   **用途**: 在前台启动 Ollama 服务。这通常在后台运行，以提供 API 服务供 `ollama run` 等命令使用。如果需要，它还会生成用于安全通信的 SSH 密钥对。
    *   **参数**: 无
    *   **相关环境变量**: 控制服务行为，如 `OLLAMA_HOST` (监听地址), `OLLAMA_DEBUG` (调试模式), `OLLAMA_MODELS` (模型存储路径) 等。

3.  **`ollama create MODEL`**
    *   **用途**: 从指定的 `Modelfile` 创建一个新的本地模型。
    *   **参数**:
        *   `MODEL`: 要创建的模型的名称。
        *   `-f, --file string`: 指定 `Modelfile` 的路径（默认为当前目录下的 `Modelfile`）。
        *   `-q, --quantize string`: （代码中定义但帮助文本未明确显示）指定量化模型的级别（例如 `q4_K_M`）。

4.  **`ollama run MODEL [PROMPT]`**
    *   **用途**: 运行指定的模型。如果提供了 `PROMPT`，则执行一次生成；如果没有提供或在交互模式下，则启动一个交互式会话。
    *   **参数**:
        *   `MODEL`: 要运行的模型名称。
        *   `PROMPT`: （可选）传递给模型的初始提示文本。
        *   `--format string`: 指定响应的格式（例如 `json`）。
        *   `--keepalive string`: 指定模型在空闲状态下保持加载的持续时间（例如 `5m`）。
        *   `--nowordwrap`: 禁用自动换行显示响应。
        *   `--verbose`: 显示响应的计时信息。
        *   `--think [string]`: 启用模型的“思考”模式。可以是 `true`, `false`, `high`, `medium`, `low`。不带值时默认为 `true`。
        *   `--hidethinking`: 隐藏模型的“思考”输出（如果模型产生）。
    *   **交互模式特殊命令**:
        *   在 `ollama run` 启动的交互会话中，可以输入 `/help` 查看帮助，包括 `/set`, `/show`, `/load`, `/bye` 等命令（虽然 `/load`, `/set`, `/show` 在代码中定义，但 `/help` 和 `/bye` 未在提供的代码片段中明确显示，但属于标准交互功能）。

5.  **`ollama stop MODEL`**
    *   **用途**: 停止指定模型的运行实例（将其从内存中卸载）。
    *   **参数**:
        *   `MODEL`: 要停止的模型名称。

6.  **`ollama pull MODEL`**
    *   **用途**: 从模型库（默认是 ollama.com/library）下载指定的模型到本地。
    *   **参数**:
        *   `MODEL`: 要下载的模型名称。
        *   `--insecure`: 使用不安全的 HTTP 连接（而非 HTTPS）。

7.  **`ollama push MODEL`**
    *   **用途**: 将本地自定义模型推送到模型库（需要先登录）。
    *   **参数**:
        *   `MODEL`: 要推送的模型名称（格式通常为 `username/model_name:tag`）。
        *   `--insecure`: 使用不安全的 HTTP 连接。

8.  **`ollama list` (或 `ollama ls`)**
    *   **用途**: 列出所有已下载到本地的模型及其基本信息（名称、ID、大小、修改时间）。
    *   **参数**: 无

9.  **`ollama ps`**
    *   **用途**: 列出当前正在运行（已加载到内存中）的模型及其状态信息（名称、ID、大小、处理器使用情况、上下文长度、过期时间）。
    *   **参数**: 无

10. **`ollama show MODEL`**
    *   **用途**: 显示指定模型的详细信息。
    *   **参数**:
        *   `MODEL`: 要显示信息的模型名称。
        *   `--license`: 仅显示模型的许可证信息。
        *   `--modelfile`: 仅显示模型的 `Modelfile` 内容。
        *   `--parameters`: 仅显示模型的参数设置。
        *   `--system`: 仅显示模型的系统消息。
        *   `--template`: 仅显示模型的提示模板。
        *   `-v, --verbose`: 显示更详细的模型元数据。

11. **`ollama cp SOURCE DESTINATION` (或 `ollama copy SOURCE DESTINATION`)**
    *   **用途**: 在本地复制或重命名一个已存在的模型。
    *   **参数**:
        *   `SOURCE`: 源模型名称。
        *   `DESTINATION`: 目标模型名称。

12. **`ollama rm MODEL [MODEL...]` (或 `ollama delete MODEL [MODEL...]`)**
    *   **用途**: 从本地删除一个或多个已下载的模型。
    *   **参数**:
        *   `MODEL`: 要删除的一个或多个模型名称。

这些命令共同构成了 Ollama CLI 的核心功能，允许用户管理、运行和与本地大型语言模型进行交互。