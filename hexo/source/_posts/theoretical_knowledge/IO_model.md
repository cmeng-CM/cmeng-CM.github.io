---
title: IO模型
tags: 'IO,IO模型'
categories:
  - 理论知识
  - IO
mathjax: true
top: true
abbrlink: aeafbee0
date: 2023-02-17 16:13:12
---

## 一、I/O概述

[I/O（英语：Input/Output）](https://zh.wikipedia.org/zh-cn/I/O)，即输入／输出，通常指数据在存储器（内部和外部）或其他周边设备之间的输入和输出。IO有 **内存IO、网络IO和磁盘IO** 三种，通常我们说的IO指的是后两者。

从系统角度来看，编辑器编辑文档、通讯软件消息的发送接收就分别属于网络IO和磁盘IO。为了方便理解IO模型，我们以通讯软件也就是网络IO来分析，软件程序是运行在 **用户空间** 的，并不存在实质的IO过程，真正的IO操作属于特权指令是运行在 **系统内核** 的（[用户空间和内核空间](https://cmeng-cm.github.io/2023/02/17/theoretical-knowledge/virtual-memory/)）。所以软件程序的IO操作需要分为两步即：
* **IO调用**：用户空间内软件程序像内核发起IO操作的调用
* **IO执行**：内核空间系统内核实际完成IO操作

IO调用则由应用程序发起，发起后则等待系统内核完成实际IO操作。IO操作在内核中也分为两步，以网络IO来说，分别是：
* 等待数据达到网卡后将数据拷贝至系统内核准备好。（即：**等待数据准备好**）
* 将内核读书的数据拷贝到用户空间，由程序进行相关操作。（即：**从内核向进程拷贝数据**）

![网络IO传输流程][网络IO传输流程]

根据图解，可以清晰的感受到 **IO调用** 和 **IO执行** 的两阶段，以及 **IO执行** 也就是接收数据过程的 **等待数据准备好** 和 **从内核向进程拷贝数据** 两阶段。
至于我们说的 **阻塞和非阻塞，异步和同步** 都是指的 **IO执行阶段** 的状态和处理机制。


## 二、阻塞、非阻塞

我们以【数据接收】过程来进一步理解下阻塞和非阻塞的概念。

![网络IO数据接收][网络IO数据接收]

### 2.1、阻塞式I/O
根据IO调用和IO执行过程来看，如果程序发起IO调用，但此时数据还未准备好（即数据未到达网卡并读取到内核缓冲区）。那么此时程序就一直处于等待数据准备好的状态，知道数据准备好后内核才能将数据拷贝至用户缓冲区。这个等待的过程就是阻塞。

**流程：**
1. 程序发起IO调用。
2. 系统内核进行IO操作。
    * 数据未准备好则等待，直至数据准备好。（<font color='red' size = 5>阻塞主要是这一步</font>）
    * 系统内核拷贝数据至用户缓冲区。

![阻塞式IO模型][阻塞式IO模型]

### 2.2、非阻塞式I/O
理解了阻塞式IO再进一步理解非阻塞就很容易了。既然没有数据那系统内核直接返回没有数据，即返回一个 **EWOULDBLOCK** 错误告知程序就可以了。这样就不用一直阻塞着等待数据到达准备好了。
不过这样确实不阻塞了，但程序还是需要获取到数据的，那么就只能轮询了。在未接收到数据时需要持续轮询系统内核是否准备好数据，直到准备好数据进行拷贝为止。

![非阻塞式IO模型][非阻塞式IO模型]

**流程：**
1. 程序发起IO调用。
2. 系统内核进行IO操作。
    * i：判断数据是否准备好，准备好进行下一步，未准备好将错误 **EWOULDBLOCK** 响应给用户控件的程序。
    * ii：系统内核拷贝数据至用户缓冲区。

## 三、I/O多路复用技术（multiplexing）
针对阻塞模型进一步思考，每个系统的进程都是很多的，如果每个进程都持续轮询到数据准备，先不说服务器能不能扛得住这么多线程，就算扛得住那么很明显这种方式是不是太浪费资源了。

那么基于这种情况，是不是考虑可以有一个进程专门用来做轮询操作，等数据到达且准备好之后再通知各个进程读取数据呢？这种方式是有的，那就是 **I/O 多路复用技术**

**I/O 多路复用技术**：Linux下的 **select、poll和epoll** 就是干这个的。将用户socket对应的fd（[文件描述](https://zh.wikipedia.org/wiki/%E6%96%87%E4%BB%B6%E6%8F%8F%E8%BF%B0%E7%AC%A6)）注册进epoll，然后epoll帮你监听哪些socket上有消息到达，这样就避免了大量的无用操作同时提升了CPU效率。此时的socket应该采用非阻塞模式。

![IO多路复用][IO多路复用]


**select()：** 用 **long** 组成的数据结构 **fd_set** 来存储文件句柄，每一个数组元素都能与一打开的文件句柄建立联系。当调用select()时，由内核根据IO状态修改 **fd_set** 的内容，由此来通知执行了 **select()** 的进程哪一Socket或文件可读。不过其监视的文件句柄通常最大为 **1024**

**epoll**：设计和实现与 **select** 完全不同。但是底层是链表，这就代表没有上限。

**epoll**：底层采用红黑树，在内核空间创建需要关注的文件描述符的红黑树，内核监听时会将发生事件的描述符加入队列中，返回到用户空间的时候只需要返回队列中的数据即可。epoll通过这种方式使得减少了每次用户到内核的复制过程。

## 四、信号驱动I/O
在多路复用的基础上，能不能有更加有效率的方式来避免这种暴力的轮询机制呢？毕竟大部分轮询都是无效的，且 **SELECT** 轮询时程序进程依旧属于阻塞状态，效率并没有提高多少。

针对这种情况，就衍生出了 **信号驱动I/O** 模型

**信号驱动I/O**：应用进程使用 **sigaction** 系统调用，内核立即返回，应用进程可以继续执行，也就是说等待数据阶段应用进程是非阻塞的。内核在数据到达时向应用进程发送 **SIGIO** 信号，应用进程收到之后在信号处理程序中调用 **recvfrom** 将数据从内核复制到应用进程中。

![信号驱动IO][信号驱动IO]

相交 **I/O多路复用** 这种通过不断轮询来减少线程资源创建的方式，**信号驱动I/O** 模式通过建立信号关联的机制，实现了发送后只需等待通知即可，避免大量无效的数据状态轮询操作。

## 五、异步I/O
那么在 **信号驱动I/O** 的基础上有没有更进一步效率更高更简洁的操作呢？当然有啦，那就是 **异步I/O** 这个相信大家都不陌生，进程发送 **aio_read** 系统调用会立即返回，内核会在所有操作完成之后向应用进程发送信号，这期间程序线程不阻塞继续执行。

![异步IO][异步IO]

## 六、总结
以上就是 **Unix** 中的五种 I/O 模型，列举如下:
* 阻塞式 I/O
* 非阻塞式 I/O
* I/O 复用(select 和 poll)
* 信号驱动式 I/O(SIGIO)
* 异步 I/O(AIO)

前四种模型主要区别有 **IO操作** 的第一阶段，就是等待数据阶段，至于第二阶段的数据复制都是一样的。其中 **阻塞式 I/O、非阻塞式 I/O、I/O 复用(select 和 poll)、信号驱动式 I/O(SIGIO)** 都是同步的I/O，虽然虽然非阻塞式 I/O 和信号驱动 I/O 在等待数据阶段不会阻塞，但是在之后的将数据从内核复制到应用进程这个操作会阻塞。
只有 **异步I/O** 是完全不阻塞的 **IO操作**





</br></br><h2>参考资料</h2>

[Synchronous and asynchronous I/O](https://learn.microsoft.com/zh-cn/windows/win32/fileio/synchronous-and-asynchronous-i-o?redirectedfrom=MSDN)
[6.2 I/O Models](https://www.masterraghu.com/subjects/np/introduction/unix_network_programming_v1.3/ch06lev1sec2.html#ch06fig01)
[select/poll/epoll](https://www.kancloud.cn/luoyoub/network-programming/2234074)





























[网络IO传输流程]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/网络IO传输流程.jpg

[网络IO数据接收]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/网络IO数据接收.jpg

[阻塞式IO模型]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/阻塞式IO模型.jpg

[非阻塞式IO模型]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/非阻塞式IO模型.jpg

[IO多路复用]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/IO多路复用.jpg

[信号驱动IO]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/信号驱动IO.jpg

[异步IO]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/异步IO.jpg