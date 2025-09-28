---
title: MQ原理和技术选型
tags: MQ
categories:
  - MQ
keywords: MQ、选型
abbrlink: 8911925b
date: 2022-11-13 16:13:12
---

# MQ原理及选型

## 一、消息队列概念
### 1.1、概述
**消息队列（英语：Message queue，简称：MQ）**：是一种进程间通信或同一进程的不同线程间的通信方式。
* 消息（Message）：是指在应用之间传送的数据，消息可以非常简单，比如只包含文本字符串，也可以更复杂，可能包含嵌入对象。
* 队列（Queue）：保持消息的容器，本质上为队列。

**原始模型：**
![MQ基本模型][MQ_basic_model]

消息队列的本质很好理解，本质都是：**<font color='red'>一发、一存、一消</font>**，所有复杂模型和中间件实现都是基于这个最初原理和模型来实现的。


### 1.2、MQ模型
现在有MQ产品都是在上面的原始模型基础上进行演化、扩展出来的功能更完善、性能更稳定的中间件。目前比较通用的MQ模型有两种：
* 点对点模型（point to point，queue）模型。
* 发布/订阅（publish/subscribe，topic）模型。

#### 点对点模型
![MQ_peertopeer_model][MQ_peertopeer_model]

**特点：**
* 消息的消费顺序和生产顺序一致。
* 它允许多个生产者往同一个队列发送消息。
* 若多消费者接收同一队列的消息，这些消费者间就是竞争关系。一条消息只能被其中一个消费者接收到，读完即被删除。
* 接收者在成功接收消息之后需向队列应答成功


#### 发布/订阅模型
![MQ_pub-sub_model][MQ_pub-sub_model]

**特点：**
* 每个消息可以有多个消费者：和点对点方式不同，发布消息可以被所有订阅者消费。
* 发布者和订阅者之间有时间上的依赖性。
* 针对某个主题 **（Topic）** 的订阅者，它必须创建一个订阅者之后，才能消费发布者的消息。
* 为了消费消息，订阅者必须保持运行的状态。

---

## 二、消息队列优、缺
消息队列使用三个经典的场景：异步、解耦、削峰。无论因为什么都是这三点的延伸。下面就这三个模块展开细说。

### 2.1、优-异步
消息队列的主要特点就是异步执行，以异步的方式执行非核心业务逻辑来降低 **RT（Response Time）**，提高用户体验和流畅性。

比如某个充值场景，最初可能就是个简单的充值，充值支付成功就OK。但随着迭代和推广，出现了充值返利、积分、充值赠券、充值后短信通知等等功能。这个时候同步操作就很影响响应时间了。

此时就需要考虑异步操作，将非必要的放在MQ异步完成，压缩响应时间。

![异步模型][MQ_Async_model]

### 2.2、优-解耦
还是上面充值的场景，假如不用MQ，我直接使用异步线程或者分布式情况下调用其它服务接口不一样实现异步的操作么。

其实是可以的，但弊端就是后续再有相关的流程加入到充值操作里面，就需要改代码、加调用。流程越多改的次数越多。

所以MQ的另一个特性就体现出来了：**解耦**。如果使用MQ充值成功后发布个充值成功到队列，谁需要谁就去消费，这样充值就直负责充值，其它的就不用管了。各自系统负责自己的任务就可以了。

所以MQ可实现模块、服务、接口等不同粒度上实现解耦。


### 2.3、优-削峰
削峰就比较好理解了，比如系统推广或秒杀的时候，突然**QPS**（QPS：Queries Per Second：每秒查询率）极速上涨。这个时候就得考虑服务是否能承载这么大的访问，如果超出系统负责可能直接就是崩掉了。

这个时候就可以把请求先放到MQ中，至于每秒消费多少就根据数据库、中间件以及服务本身的实际情况来判断并消费对应的消息就可以了。虽然响应慢一些，但不至于直接把服务干蹦掉。

![削峰模型][MQ_weaken_peak_model]


### 2.4、使用MQ的缺点
以上均为系统加入MQ的优点，那么有没有缺点呢？当然有了，所有东西都要辩证的来得。
* 系统复杂性：原本系统的基础上增加中间件，就要考虑其使用、维护、问题定位等问题。再加上MQ机制本身也要考虑：重复消费、消息丢失、消息的顺序消费等等问题。系统复杂性的增加不言而喻了。
* 数据一致性：比如刚刚的充值，充值操作是完成了，那返利是否完成？优惠券是否发放？短信是否已通知到位？
* 可用性：原本只需要考虑系统的健壮性就可以，现在增加了中间件MQ，那MQ挂了怎么处理？系统是否就直接宕掉了？

当然这些都是可以处理，只不过增加相应的开发、维护成本。最终是否使用MQ还是需要根据实际的系统和业务需求来考虑其使用情况

---

## 三、消息队列协议

### 3.1、JMS：Java Message Service（Java 消息服务）
[JMS][JMS]：Java 消息服务 (JMS) API 是一种消息传递标准，它允许基于 Java 平台企业版 (Java EE) 的应用程序组件创建、发送、接收和读取消息。它支持松耦合、可靠和异步的分布式通信。

<font size = 5 color='#b9268d'>支持两种模型： </font>

* 点对点（队列目的地）：在此模型中，消息从生产者传递到一个消费者。
* 发布/订阅（主题目的地）：在此模型中，消息从生产者传递到任意数量的消费者。

<font size = 5 color='#b9268d'>JMS优点：</font>

* 同时支持同步和异步
    * 同步：在这种模式下，客户端通过调用对象的receive()方法来接收消息MessageConsumer。应用程序线程阻塞直到方法返回，这会导致如果消息不可用，它会阻塞直到消息可用或receive()方法超时。
    * 异步：在这种模式下，客户端MessageListener向消息消费者注册一个对象。这类似于回调，其中客户端在会话调用onMessage()方法时使用消息。
* 可靠的；JMS 定义了两种传递模式：
    * 持久化消息：保证一次且仅一次成功消费。消息不会丢失。
    * 非持久消息：保证最多传递一次。消息丢失不是问题。
    JMS 提供了确保消息将被传递一次且仅一次的设施。我们知道重复的消息会产生问题。JMS 可以帮助您避免此类问题。

[ActiveMQ][ActiveMQ]：就是**JMS**规范中的一种消息中间件。

<hr class="dotted">

### 3.2、AMQP：Advanced Message Queuing Protocol（高级消息队列协议）
**AMQP：** 是一个二进制的、面向消息的中间件的开放标准，应用层协议。
* 旨在有效地支持各种消息传递应用程序和通信模式。
* 其特征是消息导向、队列、路由（包括点对点和发布-订阅）、可靠性和安全性。
* 基于此协议的客户端与消息中间件可传递消息，并不受客户端/中间件不同产品，不同开发语言等条件的限制。

[RabbitMQ][RabbitMQ]：就是AMQP协议的标准实现。
**基础模型：**
![MQ_amqp_model][MQ_amqp_model]

<hr class="dotted">


### 3.3、STOMP：The Simple Text Oriented Messaging Protocol（面向简单文本的消息协议）
**STOMP：** 是简单（或流式）文本导向消息传递协议，其设计的主要理念是简单性和互操作性。
**STOMP：** 是一种基于框架的协议，框架以 **HTTP** 为模型。一个框架由一个命令、一组可选的头部和一个可选的主体组成。**STOMP** 基于文本，但也允许传输二进制消息。

**兼容STOMP协议的中间件：**
![MQ_compatible_stomp_server][MQ_compatible_stomp_server]

<hr class="dotted">

### 3.4、MQTT
**MQTT：** 最初IBM最初发布时定义名称为：Message Queuing Telemetry Transport（消息队列遥测传输协议），但随着在物联网内的应用和发展 **MQTT** 正迅速成为IOT（物联网）部署的主要协议之一。所以称它为：**用于物联网 (IoT) 的 OASIS 标准消息传递协议** 更为准确。

**MQTT：** 被设计为一种极其轻量级的发布/订阅消息传输，非常适合连接具有小代码占用空间和最小网络带宽的远程设备。如今，MQTT 被广泛用于各种行业，例如汽车、制造、电信、石油和天然气等。

**官方架构图：**
![MQ_mqtt_official_architecture][MQ_mqtt_official_architecture]

<hr class="dotted">

### 3.5、XMPP：Extensible Messaging and Presence Protocol（可扩展消息与存在协议）
**XXMP：** 是一种以XML为基础的开放式即时通信协议。该协议于 1999 年从 Jabber 开源社区出现，最初旨在为 ICQ、AIM 和 MSN 等面向消费者的即时消息 (IM) 服务提供一种开放、安全、去中心化的替代方案。核心技术于 2004 年在IETF中以可扩展消息传递和存在协议 (XMPP) 的名称正式确定  。这些核心技术包括：
* 基本 XML 流层
* 使用传输层安全性 (TLS) 的通道加密
* 使用简单身份验证和安全层 (SASL) 的强身份验证
* 使用 UTF-8 获得完整的 Unicode 支持，包括完全国际化的地址
* 关于网络可用性的内置信息（“存在”）
* 用于双向授权的 Presence 订阅
* 启用在线状态的联系人列表（“花名册”）


## 四、MQ中间件    
#### 参照网络数据形成的各MQ不同维度的对比
| 特性             | ActiveMQ                        | RabbitMQ                                     | RocketMQ                                                            | Kafka                                                                              |
|----------------|---------------------------------|----------------------------------------------|---------------------------------------------------------------------|------------------------------------------------------------------------------------|
| 开发语言           | java                            | Erlang                                       | Java                                                                | Scala                                                                              |
| 支持的协议          | OpenWire、STOMP、REST、XMPP、AMQP   | AMQP                                         | 自定义                                                                 | 基于TCP自定义的一套                                                                        |
| 客户端支持语言        | JAVA、C、C++、Python、PHP、Pert、net等 | 官方支持Erlang、Java/Ruby等，社区产出多种语言API，几乎支持所有常用语言 | JAVA、C++（不成熟）                                                       | 官方支持JAVA,开源社区有多语言版本，如PHP,Python,GO,C/C++，Ruby，NodeJS等编程语言                          |
| 单机吞吐量          | 万级                              | 万级                                           | 10万级                                                                | 10万级别                                                                              |
| topic数量对吞吐量的影响 |                                 |                                              | topic可以达到几百，几千个的级别，吞吐量会有较小幅度的下降 这是RocketMQ的一大优势，在同等机器下，可以支撑大量的topic | topic从几十个到几百个的时候，吞吐量会大幅度下降 所以在同等机器下，kafka尽量保证topic数量不要过多。如果要支撑大规模topic，需要增加更多的机器资源 |
| 时效性            | ms级                             | 微秒级                                          | ms级                                                                 | 延迟在ms级以内                                                                           |
| 可用性            | 高，基于主从架构实现高可用性                  | 高，基于主从架构实现高可用性                               | 非常高，分布式架构                                                           | 非常高，kafka是分布式的，一个数据多个副本，少数机器宕机，不会丢失数据，不会导致不可用                                      |
| 消息可靠性          | 有较低的概率丢失数据                      | 基本不丢                                         | 经过参数优化配置，可以做到0丢失                                                    | 经过参数优化配置，消息可以做到0丢失                                                                 |
| 事物             | 支持                              | 支持                                           | 支持                                                                  | 支持                                                                                 |
| 持久化            | 内存、文件、数据库                       | 内存、文件，支持数据堆积，但数据堆积会影响生产速率                    | 磁盘文件                                                                | 磁盘文件，只要磁盘容量足够，可以做到无限消息堆积                                                           |
| 功能支持           | MQ领域的功能极其完备                     | 基于erlang开发，所以并发能力很强，性能极其好，延时很低               | MQ功能较为完善，还是分布式的，扩展性好                                                | 功能较为简单，主要支持简单的MQ功能，在大数据领域的实时计算以及日志采集被大规模使用，是事实上的标准                                 |
| 社区活跃度   | 低   | 中    | 高    | 高

综合上面的对比数据再结合项目实际的业务需求其实就已经可以很好的总结出具体的技术选型了。
<font size = 5 color='#b9268d'>记住，没有最好的技术，只有最适合的技术，不要为了用而用。</font>








































<style>
.dotted {
    border-top: 2px dotted #eed5d2;
}
</style>

[MQ_basic_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_basic_model.jpg

[MQ_Async_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_Async_model.jpeg

[MQ_weaken_peak_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_weaken_peak_model.jpg

[JMS]: https://www.oracle.com/technical-resources/articles/java/intro-java-message-service.html

[ActiveMQ]: https://activemq.apache.org/

[RabbitMQ]: https://www.rabbitmq.com/

[MQ_amqp_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_amqp_model.jpg

[MQ_compatible_stomp_server]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_compatible_stomp_server.jpg

[MQ_mqtt_official_architecture]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_mqtt_official_architecture.jpg

[MQ_peertopeer_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_peertopeer_model.jpg

[MQ_pub-sub_model]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_pub-sub_model.jpg

[MQ_contrast]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/MQ/MQ_contrast.jpg
























