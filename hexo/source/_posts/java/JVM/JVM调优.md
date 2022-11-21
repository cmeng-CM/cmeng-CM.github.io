---
title: JVM调优之jps jinfo jstat jmap jhat
date: 2020-08-18 16:13:12
tags: JVM
categories: [java,JVM]
top: true
---

## JVM调优
#### 概述
虽然jvm调优成熟的工具已经有很多：jconsole、大名鼎鼎的VisualVM，IBM的Memory Analyzer等等。但生产环境出现问题时，一是受环境所限，二是所有工具几乎都是依赖JDK的接口和底层连接命令，所以研究JDK的这些命令有助我们进一步了解JDK的构成和特性。

#### 调优原则
多数应用在服务器不需要怎么进行GC优化，多数导致GC问题的应用，主要问题并不在于GC的参数上，而更多的在代码上面。如：全局变量对象创建过多等。GC是最后不得已下的手段而已。所以通过GC情况分析并优化代码比GC调优要更多。

本文基于JDK8，相关监控和处理故障的命令有：jps、jinfo、jstat、jmap、jhat。

## jps
jps（JVM Process Status Tool）：显示指定系统内所有Hotspot虚拟机进程

命令格式：
```xshell
jps [options] [hostid]
```
options参数：  
  * -l：输入主类的全名或路径  
  * -q：输出LVMID  
  * -m：输出JVM启动时传递给main()的参数  
  * -v：输出JVM启动时显示指定的参数    

示例：
```xshell
λ jps -l
39392 org.jetbrains.jps.cmdline.Launcher
77060 sun.tools.jps.Jps
115404 org.jetbrains.idea.maven.server.RemoteMavenServer
```

## jinfo
jinfo(JVM Configuration info)：生成指定进程的JVM配置信息。

命令格式：
```xshell
jinfo -<options> vmid
```
### options参数
* -flag <name>：打印指定参数的名称和值。
* -flag [+|-]name：启用或禁用指定的布尔命令标志。
* -flag <name>=<value>：设定指定参数的值。
* -flags：输出所有JVM参数。
* -sysprops：以key-value形式，输出Java系统属性。

示例：
```xshell
λ jinfo -flag MaxNewSize 75052
  -XX:MaxNewSize=1418723328
```

## jstat
jstat（JVM Statistics Monitoring）：监视虚拟机运行时状态信息的命令，它可显示JVM的类加载、内存、垃圾收集、JIT编译等运行数据等。

命令格式：
```xshell
jstat -<option> [-t] [-h<lines>] <vmid> [<interval> [<count>]]
```
* option：操作参数
* -t ：将时间戳列显示为输出的第一列。时间戳是自目标JVM启动时间以来的时间。
* -h<lines>：即-h跟数字，代表隔几行显示标题，默认为0
* vmid ：代表vm进程id
* interval：代表监控间隔时间段，默认毫秒做单位
* count：代表取数次数

### options参数
#### 总览
参数|描述|备注
:-|:-|:-|
class|class loader的行为统计<br>Statistics about the behavior of the class loader.|
compiler|HotSpt JIT编译器行为统计。<br>Statistics about the behavior of the Java HotSpot VM Just-in-Time compiler.|
gc|垃圾收集堆行为统计.<br>Statistics about the behavior of the garbage collected heap.|
gccapacity|代的容量及其相应空间的统计信息。<br>Statistics about the capacities of the generations and their corresponding spaces.|
gccause|垃圾收集器统计概述(同gcutil)，及最近两次垃圾回收原因。<br>A summary about garbage collection statistics (same as -gcutil), with the cause of the last and current (when applicable) garbage collection events.|
gcnew|新生代代行为统计<br>Statistics about the behavior of the new generation.|
gcnewcapacity|新生代与其相应的内存空间统计。<br>Statistics about the sizes of the new generations and their corresponding spaces.|
gcold|老年代和元空间的行为统计。<br>Statistics about the behavior of the old generation and metaspace statistics.|
gcoldcapacity|老年代大小统计。<br>Statistics about the sizes of the old generation.|
gcmetacapacity|元空间大小统计。<br>Statistics about the sizes of the metaspace.|
gcutil|垃圾收集器统计概述。<br>A summary about garbage collection statistics.|
printcompilation|HotSpot编译方法统计。<br>Java HotSpot VM compilation method statistics.|

#### options参数详解
##### -class
Class loader statistics.
```xshell
λ jstat -class 62044
  Loaded  Bytes    Unloaded  Bytes     Time
  6152    12149.8     0       0.0       8.72
```
* Loaded：加载class数量。  
* Bytes：加载的class字节大小（KB）。
* Unloaded：未加载的class数量。
* Bytes：未加载calss字节大小（KB）。
* Time：执行类加载和卸载的总时间。

##### -compiler
Java HotSpot VM Just-in-Time compiler statistics.
```xshell
λ jstat -compiler 62044
  Compiled Failed Invalid   Time   FailedType FailedMethod
      8306      2       0    34.24          1 com/alibaba/druid/pool/DruidDataSource shrink
```
* Compilerd：编译数量
* Failed：编译失败的数量
* Invalid：无效的数量
* Time：执行编译时长
* FailedType : 失败类型
* FailedMethod : 失败方法的全限定名

##### -gc
Garbage collected heap statistics.  
```xshell
λ jstat -gc 62044
 S0C    S1C    S0U    S1U      EC       EU        OC         OU       MC     MU    CCSC   CCSU   YGC     YGCT    FGC    FGCT     GCT
512.0  512.0   0.0    96.0  27648.0   6616.5   67584.0    55474.4   42112.0 41055.1 4736.0 4522.8  50299   94.002  12      0.677   94.679
```
C：Capacity，即总容量，容量单位为KB；U：Used，即已使用容量。  
* S0C：survivor0总容量  
* S1C：survivor1总容量  
* S0U：survivor0已使用容量
* S1U：survivor1已使用容量
* EC：Eden区总容量
* EU：Eden区已使用容量
* OC：老年代总容量
* OU：老年代已使用容量
* MC：元空间承诺大小
* MU：元空间已使用容量
* CCSC：压缩类容量大小
* CCSU：压缩类已使用容量
* YGC：新生代垃圾回收次数
* YGCT：新生代垃圾回收时间
* FGC：老年代垃圾回收次数
* FGCT：老年代垃圾回收时间
* GCT：垃圾回收总耗时

##### -gccapacity
Memory pool generation and space capacities.  
```xshell
jstat -gccapacity 62044
 NGCMN    NGCMX     NGC     S0C   S1C       EC      OGCMN      OGCMX       OGC         OC       MCMN     MCMX      MC     CCSMN    CCSMX     CCSC    YGC    FGC
 86528.0 1385472.0  32256.0  512.0  512.0  30720.0   173568.0  2771968.0    83968.0    83968.0      0.0 1085440.0  39936.0      0.0 1048576.0   4608.0   1306     2
```
* NGCMN：新生代最小容量
* NGCMX：新生代最大容量
* NGC：当前新生代容量
* S0C：survivor0总容量  
* S1C：survivor1总容量  
* EC：Eden区总容量  
* OGCMN：老年代最小容量
* OGCMX：老年代最大容量
* OGC：当前老年代容量
* OC：老年代总容量
* MCMN：元空间最小容量
* MCMX：元空间最大容量
* MC：元空间当前容量
* CCSMN：压缩类空间最小容量
* CCSMX：压缩类空间最大容量
* CCSC：当前压缩类空间容量
* YGC：年轻的GC次数
* FGC：老年代GC次数

##### -gccause
垃圾收集器统计概述(同gcutil)，及最近两次垃圾回收原因。
```xshell
λ jstat -gccause 62044
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT    LGCC                 GCC
 25.00   0.00  49.19  37.97  97.21  96.06   2360    4.765     2    0.099    4.865 Allocation Failure   No GC
```
* LGCC：上次垃圾回收原因
* GCC：当前垃圾回收原因

##### -gcnew
新生代代行为统计  
```xshell
λ jstat -gcnew 62044
 S0C    S1C    S0U    S1U   TT MTT  DSS      EC       EU     YGC     YGCT
 512.0  512.0    0.0   96.0 15  15  512.0  30720.0   6082.8   2557    5.169
```
* S0C：survivor0总容量  
* S1C：survivor1总容量  
* S0U：survivor0已使用容量
* S1U：survivor1已使用容量
* TT：Tenuring threshold.(任期阈值)
* DTT： Maximum tenuring threshold.
* DSS：DSS: Desired survivor size (KB).survivor的容量
* EC：Eden区总容量
* EU：Eden区已使用容量
* YGC：新生代垃圾回收次数
* YGCT：新生代垃圾回收时间

#### -gcnewcapacity
新生代与其相应的内存空间统计。
```xshell
λ jstat -gcnewcapacity 105308
  NGCMN      NGCMX       NGC      S0CMX     S0C     S1CMX     S1C       ECMX        EC      YGC   FGC
   86528.0  1385472.0    64512.0 461824.0   9728.0 461824.0    512.0  1384448.0    45056.0    25     2
```
* NGCMN：新生代最小容量
* NGCMX：新生代最大容量
* NGC：当前新生代容量
* S0CMX：survivor0最大容量
* S0C：当前survivor0容量
* ECMX：Eden最大容量
* EC：当前Eden容量
* YGC：新生代垃圾回收次数
* FGC：老年代GC次数

##### -gcold
老年代和元空间的行为统计。
```xshell
λ jstat -gcold 105308
   MC       MU      CCSC     CCSU       OC          OU       YGC    FGC    FGCT     GCT
 39680.0  38773.6   4608.0   4422.3     80896.0     22094.7    313     2    0.098    0.805
```
* MC：元空间承诺大小
* MU：元空间已使用容量
* CCSC：压缩类容量大小
* CCSU：压缩类已使用容量
* OC：老年代总容量
* OU：老年代已使用容量
* YGC：新生代垃圾回收次数
* FGC：老年代垃圾回收次数
* FGCT：老年代垃圾回收时间
* GCT：垃圾回收总耗时

##### -gcoldcapacity
老年代大小统计。
```xshell
λ jstat -gcoldcapacity 105308
   OGCMN       OGCMX        OGC         OC       YGC   FGC    FGCT     GCT
   173568.0   2771968.0     80896.0     80896.0   740     2    0.098    1.668
```
* OGCMN：老年代最小容量
* OGCMX：老年代最大容量
* OGC：当前老年代容量
* OC：老年代总容量
* YGC：年轻的GC次数
* FGC：老年代GC次数
* FGCT：老年代垃圾回收时间
* GCT：垃圾回收总耗时

##### -gcmetacapacity
元空间大小统计。
```xshell
λ jstat -gcmetacapacity 105308
   MCMN       MCMX        MC       CCSMN      CCSMX       CCSC     YGC   FGC    FGCT     GCT
       0.0  1085440.0    40448.0        0.0  1048576.0     4608.0   848     2    0.098    1.885
```

* MCMN：元空间最小容量
* MCMX：元空间最大容量
* MC：元空间当前容量
* CCSMN：压缩类空间最小容量
* CCSMX：压缩类空间最大容量
* CCSC：当前压缩类空间容量
* YGC：年轻的GC次数
* FGC：老年代GC次数
* FGCT：老年代垃圾回收时间
* GCT：垃圾回收总耗时

##### -gcutil
垃圾收集器统计概述。
```xshell
λ jstat -gcutil 105308
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
  0.00  31.25  57.06  30.97  97.41  96.00    959    2.047     2    0.098    2.145
```

* S0、S1、E、O、M、CCS分别为对应内存空间已使用容量占总容量的百分比。

#### -printcompilation
HotSpot编译方法统计。
```xshell
λ jstat -printcompilation 105308
Compiled  Size  Type Method
    7351     30    1 org/apache/http/message/TokenParser isWhitespace
```
* Compiled：被执行的编译任务的数量
* Size：方法字节码的字节数
* Type：编译类型
* Method：编译方法的类名和方法名。类名使用"/" 代替 "." 作为空间分隔符. 方法名是给出类的方法名. 格式是一致于HotSpot - XX:+PrintComplation 选项

### 示例分析
```xshell
λ jstat -gcutil 105308 200 10
  S0     S1     E      O      M     CCS    YGC     YGCT    FGC    FGCT     GCT
 31.25   0.00  69.70  41.31  97.43  96.12   3050    6.466     2    0.098    6.564
  0.00  25.00  25.65  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  38.43  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  50.31  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  63.75  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  73.27  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  84.72  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
  0.00  25.00  99.04  41.31  97.43  96.12   3051    6.468     2    0.098    6.566
 31.25   0.00  11.40  41.31  97.43  96.12   3052    6.469     2    0.098    6.567
 31.25   0.00  20.88  41.31  97.43  96.12   3052    6.469     2    0.098    6.567
```
示例中vmid为105308，指令含义为输出垃圾收集统计概述，输出策略为每200毫秒一次共输出10次  
根据结果可得出以下结果：
1. 10次内进行两次新生代GC
2. 第一次新生代GC耗时0.002秒，第二次耗时0.001秒。
3. 没有进行老年代收集，老年代没有空间上的变化，说明Eden区没有对象年龄晋升到老年代
4. 第一次YGC将S0内对象提升到S1，S1部分对象提升到Eden区
5. 元空间没有变化，但元空间使用程度已经极高，到了96.12%，这个时候就可以考虑下元空间调优的问题了。


## jmap - print details of a specified process
jmap(JVM Memory Map)：用于生成heap dump文件，还可以查询finalize执行队列、Java堆和永久代的详细信息，如当前使用率、当前使用的是哪种收集器等。    
可以使用XX:+HeapDumpOnOutOfMemoryError参数来让虚拟机出现OOM的时候·自动生成dump文件。

命令格式：
```xshell
jmap -<options> <vmid>
```

### options参数
#### 总览
参数|描述
:-|:-
-clstats|打印java堆类加载统计信息<br>Prints class loader wise statistics of Java heap.
-finalizerinfo|打印等待结束的对象信息<br>Prints information about objects that are awaiting finalization.
-histo[:live]|打印堆的对象统计，包括对象数量，大小等。也可以单独指定子项：live，只打印存活对象。<br>Prints a histogram of the heap. For each Java class, the number of objects, memory size in bytes, and the fully qualified class names are printed. The JVM internal class names are printed with an asterisk (*) prefix. If the live suboption is specified, then only active objects are counted.
-dump:[live,] format=b, file=filename| 将Java堆以hprof二进制格式转储为文件名filename。live子选项选定时，只转储存活对象。<br>Dumps the Java heap in hprof binary format to filename. The live suboption is optional, but when specified, only the active objects in the heap are dumped. To browse the heap dump, you can use the jhat(1) command to read the generated file.
-heap|输出java堆概览.<br>Prints a heap summary of the garbage collection used, the head configuration, and generation-wise heap usage. In addition, the number and size of interned Strings are printed.


#### 详解
##### -clstats
连接正在运行的进程，打印类加载器的统计信息
```xshell
λ jmap -clstats 75052
Attaching to process ID 75052, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.131-b11
finding class loader instances ..done.
computing per loader stat ..done.
please wait.. computing liveness.liveness analysis may be inaccurate ...
class_loader    classes bytes   parent_loader   alive?  type

<bootstrap>     3735    6715263   null          live    <internal>
0x00000006c24851c8      1       889     0x00000006c24853f0      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3220ba0      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3820380      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c383c380      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2cea748      1       878       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf8178      1       1472      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c337c6f0      1       1483    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2485100      1       878       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2418f08      2749    5382011 0x00000006c2418f68      dead    sun/misc/Launcher$AppClassLoader@0x00000007c000f6a0
0x00000006c3220c68      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2cea680      1       880       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c337c838      1       1473    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3908b40      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2ceab58      1       880       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3908c08      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c28bafd0      0       0       0x00000006c2418f08      dead    java/util/ResourceBundle$RBClassLoader@0x00000007c0089950
0x00000006c2ceaa90      1       1472    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf87a0      1       1473      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf89a0      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2485328      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c39089b0      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3222ec0      1       880     0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c37cced8      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bd2298      40      93710   0x00000006c2418f08      dead    com/alibaba/fastjson/util/ASMClassLoader@0x00000007c02af098
0x00000006c2cea428      1       1474      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf86d8      1       1473      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c337d290      1       1485    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c3908a78      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2418f68      124     266033    null          dead    sun/misc/Launcher$ExtClassLoader@0x00000007c000fa48
0x00000006c3222f88      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c37cce10      1       1471    0x00000006c2418f08      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2cea360      1       1485      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf8610      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2485038      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2cea5b8      1       880       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf8308      1       1471    0x00000006c2418f68      dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf8548      1       1473      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c337cf80      1       878       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2484ef0      1       880       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c24853f0      12      37276   0x00000006c2418f08      dead    sun/reflect/misc/MethodUtil@0x00000007c0116af8
0x00000006c2cea4f0      1       880       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c2bf8240      1       1473      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c337d048      1       878       null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8
0x00000006c37fe380      1       1471      null          dead    sun/reflect/DelegatingClassLoader@0x00000007c0009df8

total = 45      6699    12545217            N/A         alive=1, dead=44            N/A
```
* class_loader：类加载器
* classes：加载的class数
* bytes：加载字节码大小
* parent_loader：父类加载器
* live：存活状态
* type：加载器类型

##### -finalizerinfo
打印等待结束的对象信息
```xshell
λ jmap -finalizerinfo 75052
  Attaching to process ID 75052, please wait...
  Debugger attached successfully.
  Server compiler detected.
  JVM version is 25.131-b11
  Number of objects pending for finalization: 0
```
可以看出来，目前没有等待结束的对象

##### -histo
打印堆的对象统计，包括对象数量，大小等。也可以单独指定子项：live，只打印存活对象。
```xshell
λ jmap -histo:live 75052|more

 num     #instances         #bytes  class name
----------------------------------------------
   1:          4071        5668128  [I
   2:         52491        4982384  [C
   3:          3629        1511648  [B
   4:         51380        1233120  java.lang.String
   5:          6620         751480  java.lang.Class
   6:         16354         523328  java.util.concurrent.ConcurrentHashMap$Node
   7:         15464         494848  java.util.HashMap$Node
   8:          6599         409624  [Ljava.lang.Object;
   9:          2787         245256  java.lang.reflect.Method
  10:          1363         200728  [Ljava.util.HashMap$Node;
  11:          8237         197688  sun.font.TrueTypeFont$DirectoryEntry
  12:          6121         195872  java.util.Hashtable$Entry
  13:           209         143976  [J
-- More  --
```
因histo统计对象的类型很多，带上more后，可根据命令窗口大小进行部分展示，可回车后继续展示。  
其中class name为对象类型的，部分为简写，含义如下：
* B  byte
* C  char
* D  double
* F  float
* I  int
* J  long
* Z  boolean
* [  数组，如[I表示int[]
* [L+类名 其他对象

##### -dump
转储java堆信息，包含子项如下：
* live：当指定后，只转储存活对象
* format=b：转储格式，以hprof二进制格式转储Java堆
* file=filename：转储文件名  

```xshell
λ jmap -dump:live,format=b,file=heap 75052
  Dumping heap to C:\Users\Y\heap1 ...
  Heap dump file created
```
示例中转储文件会生成在C:\Users\Y\目录下，后续dump文件分析可以根据文件大小进行选择。  
分析工具：
* JDK自带程序jvisiualvm.exe
* jhat命令
* Eclipse Memory Analyzer(MAT)

##### -heap
输出java堆概览
```xshell
λ jmap -heap 75052
Attaching to process ID 75052, please wait...
Debugger attached successfully.
Server compiler detected.
JVM version is 25.131-b11

using thread-local object allocation.
Parallel GC with 4 thread(s)  //GC方式，并行

Heap Configuration:			//堆初始配置，可以通过 -XX:*(eg:NewSize) 进行对应参数设置
   MinHeapFreeRatio         = 0		//最小空闲比率
   MaxHeapFreeRatio         = 100		//最大空闲比率
   MaxHeapSize              = 4257218560 (4060.0MB)		//最大堆内存
   NewSize                  = 88604672 (84.5MB)		//新生代内存容量
   MaxNewSize               = 1418723328 (1353.0MB)		//最大新生代内存容量
   OldSize                  = 177733632 (169.5MB)		//老年代内存容量
   NewRatio                 = 2		//新生代和老年代大小比例
   SurvivorRatio            = 8		//Eden区与Survivor区的大小比值
   MetaspaceSize            = 21807104 (20.796875MB)		//元空内存容量
   CompressedClassSpaceSize = 1073741824 (1024.0MB)		//压缩类空间内存容量
   MaxMetaspaceSize         = 17592186044415 MB		//最大元空间内存
   G1HeapRegionSize         = 0 (0.0MB)		//G1垃圾回收器中指定分区大小(1MB~32MB，且必须是2的幂)，默认将整堆划分为2048个分区

Heap Usage:
PS Young Generation
Eden Space:		//Eden区使用情况：总容量、已使用、空闲、使用比例
   capacity = 31981568 (30.5MB)
   used     = 5003392 (4.7716064453125MB)
   free     = 26978176 (25.7283935546875MB)
   15.644611296106557% used
From Space:		//survivor0使用情况
   capacity = 524288 (0.5MB)
   used     = 131072 (0.125MB)
   free     = 393216 (0.375MB)
   25.0% used
To Space:		//survivor1使用情况
   capacity = 524288 (0.5MB)
   used     = 0 (0.0MB)
   free     = 524288 (0.5MB)
   0.0% used
PS Old Generation		//老年代使用情况
   capacity = 88604672 (84.5MB)
   used     = 22120552 (21.095802307128906MB)
   free     = 66484120 (63.404197692871094MB)
   24.965446517312316% used

21409 interned Strings occupying 2142768 bytes.
```


## jhat
jhat(JVM Heap Analysis Tool)与jmap结合使用，用来分析dump文件。jhat内置了一个微型的HTTP/HTML服务器，生成dump的分析结果后，可以在浏览器中查看.  
本文基于JDK8来分析使用相关命令，所以依旧存在jhat命令。从JDK9的时候已经删除了（JEP 241: Remove the jhat Tool）。现在Oracle官方推荐的分析工具是Eclipse Memory Analyzer Tool (MAT) 和 VisualVM(jvisualvm.exe)。

相关操作参数,有兴趣的可以深入了解一下：
```xshell
Usage:  jhat [-stack <bool>] [-refs <bool>] [-port <port>] [-baseline <file>] [-debug <int>] [-version] [-h|-help] <file>

        -J<flag>          Pass <flag> directly to the runtime system. For
                          example, -J-mx512m to use a maximum heap size of 512MB
        -stack false:     Turn off tracking object allocation call stack.
        -refs false:      Turn off tracking of references to objects
        -port <port>:     Set the port for the HTTP server.  Defaults to 7000
        -exclude <file>:  Specify a file that lists data members that should
                          be excluded from the reachableFrom query.
        -baseline <file>: Specify a baseline object dump.  Objects in
                          both heap dumps with the same ID and same class will
                          be marked as not being "new".
        -debug <int>:     Set debug level.
                            0:  No debug output
                            1:  Debug hprof file parsing
                            2:  Debug hprof file parsing, no server
        -version          Report version number
        -h|-help          Print this help and exit
        <file>            The file to read
```
