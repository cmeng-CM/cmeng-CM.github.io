---
title: 用户态、内核态
date: 2023-02-17 16:13:12
tags: 虚拟空间,用户态,内核态
categories: [理论知识,内存]
mathjax: true
---

## 一、虚拟内存定义

[维基百科定义](https://zh.wikipedia.org/wiki/%E8%99%9A%E6%8B%9F%E5%86%85%E5%AD%98)

**虚拟内存**：在多任务系统系统中，多任务并行，大大提升了 **CPU** 利用率，但却引出了多个进程对内存操作冲突的问题，**虚拟内存** 概念的提出就是为了解决这个问题，每个进程都运行在属于自己的 **虚拟内存** 中。

![虚拟内存页表映射物理内存][虚拟内存页表映射物理内存]

如上图，虚拟内存通过 **MMU** 将自己映射到物理内存上，使程序认为它拥有连续的可用的内存（一个连续完整的地址空间），而实际上，它通常是被分隔成多个 **物理内存碎片** 。至于具体使用的 **物理内存** 是哪块他们不需知道。所以保证了进程之间不会互相影响。

<hr class="dotted">

## 二、虚拟内存构成

**虚拟内存** 通常会被分成 **用户空间（User Space）**，与 **核心空间/内核空间（Kernel Space）** 这两个区段。对于 32 位的操作系统，在 Linux 的虚拟地址空间中，用户空间和内核空间的大小比例为 3:1，而在 window 中则为 2:2。

![虚拟内存结构][虚拟内存结构]

### 2.1. 用户空间
进程能实际操作百分百权限的空间
1. 用户空间是在虚拟内存上连续的，物理内存上 **不连续的，碎片状**。
2. 通过 **MMU** 来映射。

### 2.2、内核空间
针对一些特权指令并不允许进程直接调用，必须由系统内核调用。因系统内核也在内存中，同时防止用户进程干扰，操作系统为内核单独划分了一块内存区域，这块区域就是内核空间。

1. 内核空间是在虚拟内存和物料内存上都是 **连续的**。
    * **系统内核** 在系统启动时就需要加载到 **物理内存的内核空间上运行**，又要保证在虚拟内存内存在内核空间，所以进程的 **虚拟地址空间中的内核空间** 映射到 **物理内存中的内核空间**上。
    * 物理内存的内核空间唯一，所以所有进程的 **虚拟内存中内核空间** 都映射到了 **同一块物理内存区域**。

2. 通过 **MMU** 来映射。

3. 分级保护域
![分级保护域][priv_rings]

比如 Intel 的 CPU 将特权等级分为 4 个级别：Ring0~Ring3。其实 Linux 系统只使用了 Ring0 和 Ring3 两个运行级别(Windows 系统也是一样的)。当进程运行在 Ring3 级别时被称为运行在用户态，而运行在 Ring0 级别时被称为运行在内核态。

>>详见：[分级保护域](https://zh.wikipedia.org/wiki/%E5%88%86%E7%BA%A7%E4%BF%9D%E6%8A%A4%E5%9F%9F)

<hr class="dotted">

## 三、虚拟内存存在的意义

* 虚拟内存可以利用内存起到缓存的作用，提高进程访问磁盘的速度；
* 虚拟内存可以为进程提供独立的内存空间，简化程序的链接、加载过程并通过动态库 共享内存；
* 虚拟内存可以控制进程对物理内存的访问，隔离不同进程的访问权限，提高系统的安全性；


<hr class="dotted">

## 四、用户态、内核态
通俗点讲，**用户态** 就是程序在用户空间运行的状态，**内核态** 就是系统内核在内核空间运行的状态。

其实所有涉及系统资源管理的操作都是在 **内核空间** 内完成的，比如读写磁盘文件，分配回收内存，从网络接口读写数据等等。程序是无法直接访问的，这就涉及到了 **用户态** 和 **内核态** 的通讯机制。通常我们在调用系统提供的接口操作系统资源时都属于这种通讯机制。

从用户空间和内核空间及通讯角度来看：

![虚拟内存结构2][虚拟内存结构2]
**ps：图片来源于网络**

**用户态 <—> 内核态** 状态切换流程（大致示意）：
```java
//读取文件
File file = new File("/demo.txt");
long length = file.length();
```
![file_read][file_read]

上图为文件读取过程程序的用户态和内核态之前的切换，可以看到程序无法直接访问系统资源，如果涉及系统资源的访问都需要通过 **内核空间** ，切换为 **内核态** 才可以。

**用户态切换到内核态的 3 种方式：**
* 系统调用：用户态主动切换为内核的方式，如上述示例。
* 异常：当 CPU 在用户态执行时，发生不可预知异常，则会切换到内核处理异常的机制中，比如缺页异常。
* 外围设备的中断。












<style>
.dotted {
    border-top: 2px dotted #eed5d2;
}
</style>

[虚拟内存结构]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/虚拟内存结构.jpg
[虚拟内存页表映射物理内存]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/虚拟内存页表映射物理内存.jpg

[priv_rings]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/priv_rings.jpg

[虚拟内存结构2]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/虚拟内存结构2.png

[file_read]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/file_read.jpg