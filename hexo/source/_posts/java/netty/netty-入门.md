---
title: netty第二弹——Reactor模式
tags:
  - java
  - netty
categories:
  - java
  - netty
keywords: netty
abbrlink: ad72082d
date: 2023-03-20 16:13:12
---

## 一、Netty和Reactor
**Netty** 的线程模型是基于 **NIO的Selector**构建的，使用了异步驱动的**Reactor** 模式来构建的线程模型，可以很好的支持成百上千的 **SocketChannel** 连接。

所以 **Netty** 是一个典型的多线程的 **Reactor** 模式的使用，理解了这部分，在宏观上理解 **Netty的NIO及多线程** 部分就不会有什么困难了。

## 二、Reactor模式（Reactor Pattern）

>[维基百科](https://zh.wikipedia.org/zh-hans/%E5%8F%8D%E5%BA%94%E5%99%A8%E6%A8%A1%E5%BC%8F)：
反应器模式（Reactor_pattern）是一种为处理服务请求并发 提交到一个或者多个服务处理程序的事件设计模式。当请求抵达后，服务处理程序使用解多路分配策略，然后同步地派发这些请求至相关的请求处理程序。

![Reactor]

从结构图可以看出，有个独立的 **Service Handler** 线程进行监听就绪事件，当一个或多个事件准备好后，由 **Service Handler** 分发给具体的请求处理线程。听起来是不是很熟悉，再回想下 **IO多路复用** 模型，就明白 熟悉感在哪了。

Reactor模式是事件驱动架构的一种实现技术，这种模式将程序代码模块化与可复用反应器解耦，从而实现并发请求与事件处理分离。
其实也可理解为 **IO多路复用** 的面向对象化的包装，相较于用 I/O多路复用接口写网络程序这种面向过程的方式写代码，面向对象的方式效率肯定高很多。同时让使用者不用考虑底层网络 API 的细节，只需要关注应用代码的编写。

<font size=5>Reactor模式</font> 也可以称为：
* 反应器模式。
* 分发者模式（Dispatcher）。
* 通知者模式（notifier）。

其实根据具体模型，感觉还是称为 <font color = '#48D1CC'>分发者模式（Dispatcher）</font> 更为贴切，即 **I/O 多路复用监听事件，收到事件后，根据事件类型分配（Dispatch）给某个进程 / 线程。**

**Reactor 模式** 主要由 **Reactor** 和 **Handler（处理资源池）** 这两个核心部分组成，它俩负责的事情如下：
* Reactor：负责监听和分发事件，事件类型包含连接事件、读写事件；
* Handler：处理程序执行对应I/O事件实际需要业务逻辑，如 read -> 业务逻辑 -> send。


##  三、Reactor模式类型
根据两个核心组成可分为四种类型，分别是：
* 单 Reactor —— 单线程/进程cd -

* 单 Reactor —— 多线程/进程
* 多 Reactor —— 单线程/进程
* 多 Reactor —— 多线程/进程

其中第三种即 **多 Reactor —— 单线程/进程** 类型，相比 **单 Reactor —— 多线程/进程** 类型不仅实现复杂，也没性能优势，所以实际中并没有使用。
至于具体使线程还是进程则取决于具体的开发语言和平台，比如Java主要以线程为主。

### 3.1、单 Reactor —— 单线程/进程

































[Reactor]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/Reactor.jpg


