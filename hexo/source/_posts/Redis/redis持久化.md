---
title: redis持久化
date: 2019-08-12 15:25:11
tags: Redis
categories: Redis

---
# Redis
- Redis作为一个键值对内存数据库(Nosql)，它的强大性能很大程度上是因为所有数据都存储在内存当中，很显然
如果服务器重启(各种因素导致)，内存中存储的所有数据都会丢失，而且不光是重启，守护进程退出，数据一样会
丢失，现在Redis用作存储的业务场景变多，数据丢失对业务是致命的影响，如：
	1. 缓存的应用场景，如果大量缓存数据丢失，往往导致后端存储组件”打死“，应用程序雪崩的情况。
	2. Redis存储的应用场景，数据丢失是不能接受的;

# Redis持久化方案
### redis提供了两种持久化的方案，分别是RDB和AOF
## RDB：
##### RDB是一种快照存储持久化方式，将Redis内存中的数据保存到硬盘的文件中，生产的RDB文件是一个经过压缩的二进制文件，默认保存的文件名为dump.rdb，redis启动时会自动载入。
###### RDB实现方式有两种，手动执行和服务器配置定期执行
  - 手动执行有两个命令可用于生成RDB文件，SAVE和BGSAVE
	1. SAVE命令，但SAVE命令会阻塞服务进程，阻塞其它命令，直到RDB文件创建完成，才执行。如若数据量较大不建议使用该命令。
	2. BGSAVE命令，与SAVE不同，BGSAVE是通过派生子进程来实现的，主进程依旧可以接收命令，但派生子进程是同步的，所以派生子进程过程较长(一版很快)也会出现阻塞的情况。
  - BGSAVE命令执行过程中，无法同时执行SAVE和BESAVE，避免产生竞争条件。
  - 服务器配置定时执行
	```
	save 900 1      // 900内,有1条写入,则产生快照 
	save 300 1000   // 如果300秒内有1000次写入,则产生快照
	save 60 10000  // 如果60秒内有10000次写入,则产生快照

	```
	通过配置文件进行触发，如上所示，根据操作次数进行触发，redis服务器的周期性函数serverCorn会每一百毫秒进行一次，它的工作之前就是判断是否满足配置参数条件，如果满足就执行BGSAVE命令。
	RDB其它相关配置
	```
	stop-writes-on-bgsave-error yes  // 后台备份进程出错时,主进程停不停止写入?
    rdbcompression yes    // 导出的rdb文件是否压缩
    Rdbchecksum   yes //  导入rbd恢复时数据时,要不要检验rdb的完整性
    dbfilename dump.rdb  //导出来的rdb文件名
    dir ./  //rdb的放置路径
	```

## AOF
##### AOF(Append-Only File)，与RDB某个时刻的快照不同，AOF持久化会记录每次操作，形成后缀为aof的文件，类似mysql的binlog。在重启后会通过运行aof文件，以达到回复文件的目的。相较而言会对redis性能有些影响，但大部分情况是可接受的.
- Redis默认不开启AOF持久化方式，我们可以在配置文件中开启
    ```
    appendonly no # 是否打开 aof日志功能

    ```
- AOF持久化的实现可分为三步，追加(append)、文件写入、文件同步(sync)
	1. 命令追加，服务器每次操作都会以redis的协议方式形成二进制文件，追加到aof_buf缓冲区的末尾。
	```
    struct redisServer{
        sds aof_buf;/* AOF buffer, written before entering the event loop */
    }

	```
    2.  文件写入与同步
    redis服务器进程就是一个事件循环函数，每次循环结束前，都会调用
    flushAppendOnlyFile()，考虑是否将aof缓冲区中的内容写入到aof文件当中，flushAppendOnlyFile()函数的行为由配置appendfsync参数控制，一共如下三种策略，缺省情况下默认为everysec策略。
    缓冲区确实提高了效率，但也存在一定安全问题，如果发生停机，那么缓冲区的数据也会丢失，为此redis提供了两个同步函数，fsync和fdatasync，强制将缓冲区的数据写入到硬盘文件。

    ```
    appendfsync always   # 每1个命令,都立即同步到aof. 安全,速度慢
    appendfsync everysec # 折衷方案,每秒写1次
    appendfsync no #写入工作交给操作系统,由操作系统判断缓冲区大小,统一写入到aof. 同步频率低,速度快
    ```

    3. AOF文件载入与还原
    aof文件已经包含所有操作命令，所以数据还原其实就是再次执行一次aof中的命令。步骤：
    1) 创建一个不带网络伪客户端，因为redis命令只能在客户端执行，并且执行命令来源于aof文件。
    2) 从aof文件中读取一条命令
    3) 在伪客户端执行
    4) 反复执行二三步，直至aof文件中的命令执行完毕

- AOF重写
    1. 因为aof会把每一步操作都记录到文件，aof文件会越来越大，数据还原时间会越来越长。
    如下命令操作为了记录list键的状态，aof文件就保存了五条命令，为了解决aof文件膨胀的问题，redis提供了重写(rewrite)机制，通过重写aof，可以生成一个恢复当前redis中数据的最少命令集，比如上面五条就可以合为一条。虽然功能命名为"aof文件重写"，但实际不会对aof文件进行分析处理，而是根据数据库状态来实现的。
    ```
    RPUSH enlist "A" "B"
    RPUSH enlist "C" "V"
    RPUSH enlist "D" "G"
    LPOP enlist "G"
    LPOP list "A"

    ```

    2. 重写策略
    2.1配置文件方式：
    默认情况下是不开启重写的,打开后每次fsync都会进行rewrite
    ```
    no-appendfsync-on-rewrite no

    ```

    当然单独配置会比较影响服务器性能，所以可以与另外两个参数一起配置，三个参数一起配置就可以控制rewrite的运行时机，此逻辑也是通过serverCron()函数进行判断控制的
    ```
    auto-aof-rewrite-percentage 100 #aof文件大小比起上次重写时的大小
                                    增长率100%时,重写
    auto-aof-rewrite-min-size 64mb #aof文件,至少超过64M时,重写
    ```

    2.2 手动触发
    客户端向服务器发送BGREWRITEAOF命令，也可以让服务器进行AOF重写。并且是异步进行
    注：BGREWRITEAOF正在执行，客户端发送BGSAVE命令会被服务器拒绝，BGSAVE正在执行，客户端发送BGREWRITEAOF，两者在操作上没有冲突，只是都是由子进程进行工作，不能同时执行只是性能方面的考虑——并发两个线程，并且都是大量磁盘写入工作。
- AOF文件破损
  因服务宕机会造成aof文件格式紊乱，这种情况下服务会拒绝加载aof文件，出现文件损坏的情况可以通过以下命令进行修复
    ```
    $ redis-check-aof -fix file.aof

    ```
    重启服务后可重新载入aof文件进行数据恢复。
## 总结
- RDB
    1. RDB相较AOF而言，恢复数据快，数据紧凑
    2. SAVE命令容易阻塞服务器，影响性能，BGSAVE虽然由子进行进行工作，但数据量较大时，也会有影响
    3. 容易造成某时间段数据丢失
- AOF
    1. AOF为追加操作记录形式，对服务器影响小，速度快
    2. 数据量大时，AOF文件体积太大，恢复慢，即使通过重写，文件体积依然较大。
- 具体选择哪种方式就需要根据具体场景需求进行选择，当然也可以两种方式配合进行，但redis会优先使用AOF文件方式恢复数据，因为AOF文件保存数据比较完整。

![Alt](https://user-gold-cdn.xitu.io/2019/6/26/16b918cd860b0ffd?imageslim)

---
### 源码资料
https://github.com/huangz1990/redis-3.0-annotated.git

### 参考资料
https://juejin.im/post/5d09a9ff51882577eb133aa9#heading-7





















