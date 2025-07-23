---
title: `tauri.conf.json` 配置详解
tags: 
    - rust
    - tauri
    - config
categories: 
    - rust
    - tauri
mathjax: true
date: 2025-01-17 16:13:12
---


### Tauri 2.0 的 `tauri.conf.json` 配置详解

#### 1. tauri.conf.json的内容模块

在Tauri 2.0框架中，`tauri.conf.json`是核心配置文件，它负责定义应用的各个方面，包括但不限于前端资源、构建选项、安全策略以及窗口行为。该文件通常位于项目的`src-tauri`目录下，并且可以针对不同操作系统（如Linux、Windows、macOS）提供特定的配置。

#### 2. 各个模块的含义

- **package**: 这部分包含了应用的基本信息，比如产品名称和版本号。
- **build**: 包含了构建过程中的各种命令和路径设置。
- **tauri**: 此模块涵盖了应用的行为和特性，例如API白名单、捆绑器配置、安全性配置等。
- **windows**: 定义了应用程序窗口的各种属性，如尺寸、标题、是否可调整大小等。
- **systemTray** (可选): 如果你的应用需要系统托盘图标，则需在此定义相关配置。
- **updater** (可选): 对于支持自动更新的应用程序，这部分将定义更新逻辑。

#### 3. 各个模块可配置的选项

##### Package
- **productName**: 应用程序的名称。
- **version**: 应用程序的版本号，遵循语义化版本控制规范。

##### Build
- **beforeDevCommand**: 开发模式启动前执行的命令。
- **beforeBuildCommand**: 构建生产版本前执行的命令。
- **devPath**: 开发模式下的前端资源路径。
- **distDir**: 构建后输出的目录。

##### Tauri
- **allowlist**: 定义哪些API可以被前端调用，默认情况下所有API都被允许访问。
- **bundle**: 配置打包参数，如目标平台、应用标识符等。
- **security**: 设置内容安全策略（CSP），保护应用免受XSS攻击。
- **updater**: 配置应用的更新机制，包括更新服务器地址和公钥。

##### Windows
- **title**: 窗口标题。
- **width & height**: 窗口的初始宽度和高度。
- **fullscreen**: 是否以全屏模式启动。

#### 4. 全量的配置示例

```json
{
  "$schema": "../node_modules/@tauri-apps/cli/schema.json",
  "build": {
    "beforeDevCommand": "npm run serve",
    "beforeBuildCommand": "npm run build",
    "devPath": "http://localhost:8080",
    "distDir": "../dist"
  },
  "package": {
    "productName": "MyApp",
    "version": "1.0.0"
  },
  "tauri": {
    "allowlist": {
      "all": true,
      "shell": false,
      "http": true
    },
    "bundle": {
      "identifier": "com.example.myapp",
      "targets": "all",
      "icon": [
        "icons/32x32.png",
        "icons/128x128.png",
        "icons/256x256.png"
      ]
    },
    "security": {
      "csp": "default-src 'self'"
    },
    "updater": {
      "active": true,
      "endpoints": ["https://your-update-server.com"],
      "pubkey": "YOUR_PUBLIC_KEY_HERE"
    },
    "windows": [
      {
        "label": "main",
        "title": "My Application",
        "width": 800,
        "height": 600,
        "resizable": true,
        "center": true
      }
    ]
  }
}
```

此配置文件为一个基本的Tauri应用提供了全面的配置示例，从开发环境到生产环境，再到应用的安全性和更新机制都进行了详细的设定。通过合理配置这些选项，你可以定制出符合自己需求的桌面应用程序。需要注意的是，根据实际需求的不同，可能还需要对其他部分进行相应的调整或扩展。