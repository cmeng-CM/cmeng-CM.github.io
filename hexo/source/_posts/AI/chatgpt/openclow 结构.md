---
title: AI学习
tags: 英语
categories:
  - 理论知识
mathjax: true
top: false
hide: true
abbrlink: ba82741a
date: 2025-12-17 16:13:12
---


很好，这个 repo 是**当前最标准的 OpenClaw TS 实现**，我帮你做一份**“按源码真实结构拆解 + 怎么读”**，而不是泛讲👇

---

# 🧠 一、整体架构（基于该仓库）

先给你一个**还原后的真实结构（核心）**👇

```text
openclaw/
├── src/
│   ├── cli/                # CLI入口
│   ├── commands/           # 命令系统
│   ├── agents/             # Agent核心逻辑
│   ├── config/             # 配置系统
│   ├── infra/              # 基础设施（日志/依赖等）
│   ├── media/              # 多媒体处理（语音/图片）
│   ├── provider-web.ts     # Web模型调用
│
├── extensions/             # 插件/扩展（skills）
├── docs/                   # 文档
├── dist/                   # 构建产物
├── package.json
```

👉 这个结构是 repo 官方描述的核心划分 ([agent-mds.com][1])

---

# 🏗️ 二、核心模块拆解（按真实代码职责）

我帮你用**工程视角（重要程度排序）**拆👇

---

# 🔥 1️⃣ src/cli —— 入口层（你第一步必须看）

核心文件：

```ts
src/cli/program.ts
```

---

## 作用：

👉 启动整个系统

---

## 你会看到：

```ts
program
  .command("run")
  .action(...)
```

---

👉 本质：

> **把 CLI → Agent 执行链路串起来**

---

## 🧠 你要搞清楚：

* 用户输入 → 怎么进入系统
* command → 怎么触发 agent

---

# 🧠 2️⃣ src/agents —— Agent核心（最重要）

这是整个系统的“大脑”

---

## 你会看到：

```text
agents/
├── subagent-*.ts
├── registry
├── runtime
```

---

## 核心逻辑：

```ts
while (true) {
  think()
  decide()
  act()
}
```

---

👉 对应：

> **ReAct / Agent Loop**

---

## 🔑 重点看：

* Agent 如何调用 LLM
* 如何决定 tool / skill
* 子 Agent 怎么调度

---

# 🔧 3️⃣ extensions/ —— Skill系统（OpenClaw精髓）

这是 OpenClaw 和普通 Agent 最大区别👇

---

## 结构：

```text
extensions/
  ├── xxx/
      ├── SKILL.md
      ├── code.ts
```

---

👉 官方机制：

> 每个 skill = 一个目录 + 一个 `SKILL.md` 描述能力 ([维基百科][2])

---

## 🧠 本质：

* SKILL.md = prompt + tool说明
* code = 执行逻辑

---

👉 这就是：

> **“LLM + Tool + Prompt 封装单元”**

---

## 🔥 你重点看：

* SKILL.md 怎么写
* skill 如何被加载
* 如何被 agent 选择

---

# 🤖 4️⃣ provider-web.ts —— 模型调用层

这是：

> **LLM 抽象层**

---

## 作用：

* 调 GPT / Claude / DeepSeek
* 统一接口

---

## 核心：

```ts
generate(prompt)
```

---

👉 你要看：

* prompt 是怎么拼的
* tool call 怎么处理

---

# ⚙️ 5️⃣ src/commands —— 命令系统

---

## 作用：

👉 CLI → 业务行为

---

比如：

```bash
openclaw run
openclaw doctor
```

---

👉 每个命令：

```ts
export async function runCommand()
```

---

# 🧩 6️⃣ src/config —— 配置系统

---

## 你会看到：

```text
config/
├── config.ts
├── types.ts
├── zod-schema.ts
```

---

👉 特点：

* 用 Zod 做 schema 校验
* JSON config 驱动

---

👉 对应：

> 用户所有行为（模型 / memory / tools）

---

# 🧱 7️⃣ src/infra —— 基础设施

---

包括：

* logging
* utils
* 生命周期

---

👉 这个你可以后看

---

# 🎬 8️⃣ src/media —— 多模态

---

处理：

* 图片
* 音频

---

👉 不是核心，可以先跳过

---

# 🧠 三、OpenClaw 的真实运行链路（最关键）

你一定要搞懂这一条👇

---

```text
CLI输入
  ↓
commands
  ↓
Agent启动
  ↓
构建prompt（含memory + skill）
  ↓
LLM调用
  ↓
决定：
   - 回复
   - 调用skill
  ↓
执行skill
  ↓
返回结果
```

---

👉 本质：

> **Agent Loop + Skill System**

---

# 🔥 四、你应该怎么读这个 TS 项目（最优路径）

结合你（Java + AI工程），我给你最有效路线👇

---

# 🥇 Step 1：入口 → Agent

顺序：

```text
src/cli/program.ts
→ src/commands
→ src/agents
```

---

👉 目标：

> **搞清楚一次请求怎么跑完**

---

# 🥈 Step 2：只盯一个 Skill

去看：

```text
extensions/xxx/
```

---

👉 理解：

* SKILL.md → prompt
* code → tool

---

👉 你会突然明白：

> **OpenClaw = Skill 驱动系统**

---

# 🥉 Step 3：看 prompt 构建

重点：

```ts
provider-web.ts
```

---

👉 看：

* memory 怎么拼进去
* skill 怎么注入

---

# ⚠️ 五、这个项目最核心的3个设计（必须理解）

---

## 🔥 1️⃣ Skill = Prompt + Tool

👉 不是函数调用，而是：

> **LLM驱动的能力模块**

---

## 🔥 2️⃣ Agent 是“调度器”

👉 不干活，只负责：

* 决策
* 调用 skill

---

## 🔥 3️⃣ Memory 是“隐式的”

👉 不像 LangChain 明显

而是：

* workspace 文件
* markdown context

---

👉 这点很多人看源码会懵

---

# 🧠 六、你用“架构思维”看它

你可以这样理解👇

---

## OpenClaw =

```text
Agent Runtime
+ Skill System
+ Local Workspace（记忆）
+ LLM Provider
```

---

👉 而不是：

> 一个复杂框架

---

# 🚀 七、给你一个“高手读法”（很关键）

---

## 用 Debug 跑一条链

1. 断点：

```ts
program.ts
```

2. 输入：

```bash
openclaw run "帮我做一个任务"
```

3. 单步看：

* prompt
* skill选择
* tool执行

---

👉 这个效率 > 看源码 10倍

---

# ✅ 最后一段总结（帮你定性）

> **这个 TS 版 OpenClaw，本质是：CLI驱动的 Agent Runtime + Skill 插件系统 + 本地上下文记忆，而不是传统“多模块复杂后端”。**

---

# 👍 如果你要更深入（我建议下一步）

我可以帮你👇

👉 **把这个仓库“核心执行链（100行级别）抽出来 + 画调用图”**
👉 或者直接帮你写一个 **Java版简化OpenClaw（适合你转型AI负责人）**

只要你说一句：
👉 “给我最小实现版”

[1]: https://agent-mds.com/openclaw/openclaw?utm_source=chatgpt.com "openclaw/openclaw | Agent Docs"
[2]: https://en.wikipedia.org/wiki/OpenClaw?utm_source=chatgpt.com "OpenClaw"
