---
title: RocketMQ——《1、启动脚本》
tags: RocketMQ
categories:
  - MQ
  - RocketMQ
keywords: 源码、原理、RocketMQ
abbrlink: 10a565f9
date: 2022-11-13 16:13:12
---

# RocketMQ使用记录
**RocketMQ** 相关的操作和使用官方的文档是有具体步骤讲解的：[RocketMQ官方](https://rocketmq.apache.org/zh/docs/)。本文基于官方文档的基础上 **深入每步的具体操作** 及后续 **运行原理和源码** 进行进一步分析和讨论。

## 一、启动
安装好Rocket后，启动操作如下：
```bash
### 启动namesrv
$ nohup sh bin/mqnamesrv &
 
### 验证namesrv是否启动成功
$ tail -f ~/logs/rocketmqlogs/namesrv.log
The Name Server boot success...
```
下面分解启动流程内包含的所有操作和配置。

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
* 设置环境变量 **ROCKETMQ_HOME**
* 启动 **runserver.sh** 脚本，并带有指定类 **NamesrvStartup**。
* 如果运行 **mqnamesrv** 时有额外参数也一并带入 **runserver.sh** 脚本中。

### 1.2、runserver
源码：
```bash
# 错误日志输出
error_exit ()
{
    echo "ERROR: $1 !!"
    exit 1
}

# 校验JAVA环境是否存在
[ ! -e "$JAVA_HOME/bin/java" ] && JAVA_HOME=$HOME/jdk/java
[ ! -e "$JAVA_HOME/bin/java" ] && JAVA_HOME=/usr/java
[ ! -e "$JAVA_HOME/bin/java" ] && error_exit "Please set the JAVA_HOME variable in your environment, We need java(x64)!"

# 定义环境变量
export JAVA_HOME
export JAVA="$JAVA_HOME/bin/java"
export BASE_DIR=$(dirname $0)/..
export CLASSPATH=.:${BASE_DIR}/conf:${BASE_DIR}/lib/*:${CLASSPATH}

#===========================================================================================
# JVM Configuration
#===========================================================================================
# The RAMDisk initializing size in MB on Darwin OS for gc-log
DIR_SIZE_IN_MB=600

# 选择GC日志目录
choose_gc_log_directory()
{
    case "`uname`" in
        Darwin)
            if [ ! -d "/Volumes/RAMDisk" ]; then
                # create ram disk on Darwin systems as gc-log directory
                DEV=`hdiutil attach -nomount ram://$((2 * 1024 * DIR_SIZE_IN_MB))` > /dev/null
                diskutil eraseVolume HFS+ RAMDisk ${DEV} > /dev/null
                echo "Create RAMDisk /Volumes/RAMDisk for gc logging on Darwin OS."
            fi
            GC_LOG_DIR="/Volumes/RAMDisk"
        ;;
        *)
            # check if /dev/shm exists on other systems
            if [ -d "/dev/shm" ]; then
                GC_LOG_DIR="/dev/shm"
            else
                GC_LOG_DIR=${BASE_DIR}
            fi
        ;;
    esac
}

# 设置JVM启动参数
choose_gc_options()
{
    # Example of JAVA_MAJOR_VERSION value : '1', '9', '10', '11', ...
    # '1' means releases befor Java 9
    JAVA_MAJOR_VERSION=$("$JAVA" -version 2>&1 | sed -r -n 's/.* version "([0-9]*).*$/\1/p')
    if [ -z "$JAVA_MAJOR_VERSION" ] || [ "$JAVA_MAJOR_VERSION" -lt "9" ] ; then
      JAVA_OPT="${JAVA_OPT} -server -Xms4g -Xmx4g -Xmn2g -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m"
      JAVA_OPT="${JAVA_OPT} -XX:+UseConcMarkSweepGC -XX:+UseCMSCompactAtFullCollection -XX:CMSInitiatingOccupancyFraction=70 -XX:+CMSParallelRemarkEnabled -XX:SoftRefLRUPolicyMSPerMB=0 -XX:+CMSClassUnloadingEnabled -XX:SurvivorRatio=8 -XX:-UseParNewGC"
      JAVA_OPT="${JAVA_OPT} -verbose:gc -Xloggc:${GC_LOG_DIR}/rmq_srv_gc_%p_%t.log -XX:+PrintGCDetails -XX:+PrintGCDateStamps"
      JAVA_OPT="${JAVA_OPT} -XX:+UseGCLogFileRotation -XX:NumberOfGCLogFiles=5 -XX:GCLogFileSize=30m"
    else
      JAVA_OPT="${JAVA_OPT} -server -Xms4g -Xmx4g -XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=320m"
      JAVA_OPT="${JAVA_OPT} -XX:+UseG1GC -XX:G1HeapRegionSize=16m -XX:G1ReservePercent=25 -XX:InitiatingHeapOccupancyPercent=30 -XX:SoftRefLRUPolicyMSPerMB=0"
      JAVA_OPT="${JAVA_OPT} -Xlog:gc*:file=${GC_LOG_DIR}/rmq_srv_gc_%p_%t.log:time,tags:filecount=5,filesize=30M"
    fi
}

choose_gc_log_directory
choose_gc_options
JAVA_OPT="${JAVA_OPT} -XX:-OmitStackTraceInFastThrow"
JAVA_OPT="${JAVA_OPT} -XX:-UseLargePages"
#JAVA_OPT="${JAVA_OPT} -Xdebug -Xrunjdwp:transport=dt_socket,address=9555,server=y,suspend=n"
JAVA_OPT="${JAVA_OPT} ${JAVA_OPT_EXT}"
JAVA_OPT="${JAVA_OPT} -cp ${CLASSPATH}"

$JAVA ${JAVA_OPT} $@
```
流程：
1. 校验JAVA环境信息
2. 定义环境变量，包含JAVA、RocketMQ等。
3. 设置JVM的GC日志目录
4. 设置JVM启动信息，设置参数如下：
  * -Xms4g：堆的最小和初始大小4G。
  * -Xmx4g：堆的最大值4G。
  * -Xmn2g：新生代2G。
  * -XX:MetaspaceSize=128m：元数据空间为128M
  * -XX:MaxMetaspaceSize=320m：类元数据的最大本机内存量为320M
  * -XX:+UseConcMarkSweepGC：为老年代启用 CMS 垃圾收集器。
  * -XX:CMSInitiatingOccupancyFraction=70：设置开始 CMS 收集周期的老年代占用百分比（0 到 100）。
  * -XX:SoftRefLRUPolicyMSPerMB=0：设置软可达对象在上次被引用后在堆上保持活动状态的时间量（以毫秒为单位）。
  * -XX:+CMSClassUnloadingEnabled：使用并发标记清除 (CMS) 垃圾收集器时启用类卸载。
  * -XX:SurvivorRatio=8：设置伊甸园空间大小和幸存者空间大小之间的比率。
  * -verbose:gc：显示有关每个垃圾回收 (GC) 事件的信息。
  * -Xloggc：设置详细 GC 事件信息应重定向到的文件以进行日志记录。
  * -XX:+PrintGCDetails：允许在每次 GC 时打印详细消息。默认情况下，此选项被禁用。
  * -XX:+PrintGCDateStamps：启用在每个 GC 上打印日期戳。默认情况下，此选项被禁用。
  * -XX:+UseGCLogFileRotation：此参数主要定义GC Log 的滚动功能
  * -XX:NumberOfGCLogFiles=5：此参数主要定义滚动日志文件的个数
  * -XX:GCLogFileSize=30m：此参数主要定义滚动日志文件的大小
  * -XX:-OmitStackTraceInFastThrow：禁用fast throw。fast throw：优化这个抛出异常的地方，同一个异常多次抛出会直接抛出一个事先分配好的、类型匹配的对象，这个对象的message和stack trace都被清空
  * -XX:+UseCMSCompactAtFullCollection：使用并发收集器时,开启对年老代的压缩.
  * -XX:+CMSParallelRemarkEnabled：降低标记停顿
  * -XX:+UseLargePages：启用大页面内存的使用。默认情况下，禁用此选项并且不使用大页面内存。
5. 启动org.apache.rocketmq.namesrv.NamesrvStartup类。