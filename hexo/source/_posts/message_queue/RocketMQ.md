---
title: RocketMQ使用记录
date: 2022-11-13 16:13:12
tags: MQ
categories: [MQ]
keywords: MQ、选型
---

# RocketMQ使用记录
**RocketMQ** 相关的操作和使用官方的文档是有具体步骤讲解的：[RocketMQ官方](https://rocketmq.apache.org/zh/docs/)。本文基于官方文档的基础上 **深入每步的具体操作** 及后续 **运行原理和源码** 进行进一步分析和讨论。

## 一、启动

### 1.1、mqnamesrv
源码：
```bash
if [ -z "$ROCKETMQ_HOME" ] ; then
  ## resolve links - $0 may be a link to maven's home
  # 获取执行文件名称   
  PRG="$0"

  # 如果 $0 是软连接则通过迭代获取其绝对路径
  # need this for relative symlinks
  while [ -h "$PRG" ] ; do
    ls=`ls -ld "$PRG"`
    link=`expr "$ls" : '.*-> \(.*\)$'`
    if expr "$link" : '/.*' > /dev/null; then
      PRG="$link"
    else
      PRG="`dirname "$PRG"`/$link"
    fi
  done

  saveddir=`pwd`

  ROCKETMQ_HOME=`dirname "$PRG"`/..

  # make it fully qualified
  ROCKETMQ_HOME=`cd "$ROCKETMQ_HOME" && pwd`

  cd "$saveddir"
fi

export ROCKETMQ_HOME

# 执行runserver.sh脚本，启动 NamesrvStartup 类文件
sh ${ROCKETMQ_HOME}/bin/runserver.sh org.apache.rocketmq.namesrv.NamesrvStartup $@
```
所以mqnamesrv内容很简单：
* 找到 **ROCKETMQ_HOME** 的绝对路径，即下载包所在的绝对路径。
* 启动 **runserver.sh** 脚本