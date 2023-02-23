---
title: netty第一弹————netty概述、演变
tags:
  - java
  - netty
categories:
  - java
  - netty
top: true
keywords: netty
abbrlink: ad72082d
date: 2023-02-23 16:13:12
---

## 前言
netty系列的IO逻辑基于 **I/O模型** 架构基础进行讲解，不会再次深入讲解具体I/O模型的原理和设计理念，具体可参考一下文章：

[I/O模型](https://cmeng-cm.github.io/posts/aeafbee0.html)
[用户空间、用户态、内核空间、内核态](https://cmeng-cm.github.io/posts/a46eba31.html)

下面正式进入：

## 一、netty概述
**Netty** 是一个 **非阻塞I/O客户端-服务器框架** ，主要用于开发 **Java网络应用程序**，如协议服务器和客户端。异步事件驱动的网络应用程序框架和工具用于简化网络编程，例如TCP和UDP套接字服务器。Netty包括了反应器编程模式的实现。Netty最初由JBoss开发，现在由Netty项目社区开发和维护。

> [官网](https://netty.io/)

## 二、JAVA的IO模型

