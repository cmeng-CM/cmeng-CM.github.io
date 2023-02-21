---
title: JVM启动参数
tags: JVM
categories:
  - java
  - JVM
top: true
abbrlink: 9074d23e
date: 2023-01-18 16:13:12
---

[​JAVA8虚拟机参数官方文档​](https://docs.oracle.com/javase/8/docs/technotes/tools/unix/java.html)

### 一、-X：显示所有可用-X选项的帮助。
|参数名称|含义|默认值|描述/示例|
|:-:|:-:|:-:|:-:|
|-Xms|堆的最小和初始大小（以字节为单位），可以使用 -Xmn 选项或 -XX:NewSize 选项设置年轻代堆的初始大小。|初始大小将被设置为分配给老年代和年轻代的大小之和|示例：大小设置为 **6MB** 的方式有以下三种： **-Xms6291456**；**-Xms6144k**；**-Xms6m**|
|-Xmx|堆的最大值|默认值是在运行时根据系统配置选择的。|-Xms 通常与 -Xmx 设置为相同的值，该 -Xmx 选项相当于 -XX:MaxHeapSize.|
|-Xmn|新生代（nursery）设置堆的初始大小和最大大小（以字节为单位）||Oracle 建议将新生代的大小保持在整个堆大小的一半到四分之一之间。相当于 -XX:NewSize、-XX:MaxNewSize|
|-XX:MetaspaceSize|设置分配的类元数据空间的大小||该空间将在第一次超出时触发垃圾回收。垃圾回收的阈值根据使用的元数据量增加或减少。默认大小取决于平台。| 
|-XX:MaxMetaspaceSize|设置可以分配给类元数据的最大本机内存量。|设置为 256 MB：-XX:MaxMetaspaceSize=256m|默认情况下，大小不受限制。应用程序的元数据量取决于应用程序本身、其他正在运行的应用程序以及系统上可用的内存量。|
|-XX:+UseConcMarkSweepGC|为老年代启用 CMS 垃圾收集器。||默认情况下，这个选项是禁用的，收集器是根据机器的配置和 JVM 的类型自动选择的。启用此选项后，该-XX:+UseParNewGC选项会自动设置，以下选项组合已在 JDK 8 中弃用：-XX:+UseConcMarkSweepGC -XX:-UseParNewGC。|
|-XX:CMSInitiatingOccupancyFraction|设置开始 CMS 收集周期的老年代占用百分比（0 到 100）。|默认值设置为 -1。任何负值（包括默认值）都意味着-XX:CMSTriggerRatio用于定义初始占用率的值。|以下示例显示如何将占用率设置为 20%：-XX:CMSInitiatingOccupancyFraction=20|
|-XX:SoftRefLRUPolicyMSPerMB|设置软可达对象在上次被引用后在堆上保持活动状态的时间量（以毫秒为单位）。|默认值是堆中每兆字节的生命周期一秒。|以下示例显示如何将值设置为 2.5 秒：-XX:SoftRefLRUPolicyMSPerMB=2500|
|-XX:+CMSClassUnloadingEnabled|使用并发标记清除 (CMS) 垃圾收集器时启用类卸载。||默认情况下启用此选项。要禁用 CMS 垃圾收集器的类卸载，请指定-XX:-CMSClassUnloadingEnabled.|
|-XX:SurvivorRatio|设置伊甸园空间大小和幸存者空间大小之间的比率。|默认情况下，此选项设置为 8。|示例显示如何将 eden/survivor 空间比率设置为 4：-XX:SurvivorRatio=4|
|-verbose:gc|显示有关每个垃圾回收 (GC) 事件的信息。|||
|-Xloggc|设置详细 GC 事件信息应重定向到的文件以进行日志记录。||写入此文件的信息类似于-verbose:gc自每个记录事件之前的第一个 GC 事件以来经过的时间的输出。如果两者都使用相同的命令，则该-Xloggc选项会覆盖。-verbose:gcjava 例子：-Xloggc:garbage-collection.log|
|-XX:+PrintGCDetails|允许在每次 GC 时打印详细消息。默认情况下，此选项被禁用。|||
|-XX:+PrintGCDateStamps|启用在每个 GC 上打印日期戳。默认情况下，此选项被禁用。|||
|-XX:+UseGCLogFileRotation|此参数主要定义GC Log 的滚动功能|||
|-XX:NumberOfGCLogFiles|此参数主要定义滚动日志文件的个数，此参数值必须大于等于1，对应的日志文件命名策略为：<filename>.0、<filename>.1、 ... 、 <filename>.n-1等，其中 n 是 该参数的值。|||
|-XX:GCLogFileSize|此参数主要定义滚动日志文件的大小，必须大于 8k，当前写日志文件大小超过该参数值时，日志将写入下一个文件，依次类推。|||
|-XX:-OmitStackTraceInFastThrow|禁用fast throw。fast throw：优化这个抛出异常的地方，同一个异常多次抛出会直接抛出一个事先分配好的、类型匹配的对象，这个对象的message和stack trace都被清空|||
|-XX:+UseCMSCompactAtFullCollection|使用并发收集器时,开启对年老代的压缩.|||
|-XX:+CMSParallelRemarkEnabled|降低标记停顿|||
|-XX:+UseLargePages|启用大页面内存的使用。默认情况下，禁用此选项并且不使用大页面内存。|||

