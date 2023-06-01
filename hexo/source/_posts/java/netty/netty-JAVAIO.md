---
title: netty第一弹——JAVA的IO
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

**Netty** 本质上是一个 **NIO** 客户端服务器框架。它极大地简化和流线化了网络编程，例如 **TCP和UDP** 套接字服务器。

所以学习 **Netty** 要先了解下 **JAVA** 本身的 **IO模型理念**。JAVA的IO模型有三种分别为 **BIO、NIO和AIO** 下面逐个了解下。

## 二、JAVA的IO模型——BIO
**JAVA BIO（Java Blocking I/O）**：<font color='#0000FF'>同步并阻塞</font> 即Java 网络编程的传统阻塞型，服务器实现模式为一个连接一个线程，即客户端有连接请求时服务器端就需要启动一个线程进行处理，如果这个连接不作任何事情会造成不必要的线程开销。
* 客户端：发送消息后，等待服务端返回，再未收到返回前阻塞等待。
* 服务端：等待接收客户端消息，未收到消息阻塞等待。

基于以上的 **BIO** 设计逻辑，分为两种BIO模型，分别是服务端 **单线程** 处理逻辑和  **多线程** 处理逻辑


### 2.1、单线程 BIO
![JAVA_BIO_MODEL]

<font size=5>单线程BIO：</font>
* 同一时间，服务端只能接收处理一个客户端的请求，即使多个客户端同时发送，也只能一个一个的串行处理。
* 由于服务端是串行处理，在高并发情况是不可取的。


服务端代码：
```Java
public static void main(String[] args) throws IOException {
    ServerSocket serverSocket = new ServerSocket(9999);
    log.info("==== 服务端启动 ====");
    try {
        while(true) {
            //阻塞，直至有新的连接建立
            Socket socket = serverSocket.accept();

            InputStream inputStream = socket.getInputStream();
            byte[] bytes = new byte[2048];

            //阻塞，等待数据到达
            int length = inputStream.read(bytes);
            String msg = new String(bytes,0,length);
            log.info(String.format("==== 收到信息：%s",msg));

            //下面开始发送信息
            OutputStream outputStream = socket.getOutputStream();
            outputStream.write("向服务端发起请求：hello client".getBytes());
            outputStream.flush();

            //关闭
            outputStream.close();
            inputStream.close();
        }
    } catch(Exception e) {
        log.error(e.getMessage(), e);
    } finally {
        if(serverSocket != null) {
            serverSocket.close();
        }
    }
}
```

客户端代码，模拟50个客户端发送请求:
```Java
public static void main(String[] args) throws IOException {
        for (int i=0;i<50;i++){
            new Thread(()->{
                try {
                    Client.client();
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }).start();
        }
    }

public static void client() throws IOException {
    Socket socket = new Socket("127.0.0.1",9999);
    log.info("==== 客户端启动 ====");
    OutputStream outputStream= null;
    InputStream inputStream = null;
    try {
        //发送请求
        outputStream = socket.getOutputStream();
        outputStream.write(String.format("客户端线程名称：%s；hello server",Thread.currentThread().getName()).getBytes());
        outputStream.flush();

        //等待响应
        inputStream = socket.getInputStream();
        byte[] bytes = new byte[2048];

        //阻塞等待数据到达
        int length = inputStream.read(bytes);
        String msg = new String(bytes,0,length);
        log.info(String.format("==== 当前线程名称：%s ==== 服务器响应：%s",Thread.currentThread().getName(),msg));
    }catch (Exception e){
        log.error(e.getMessage(),e);
    }finally {
        if(outputStream!=null){
            outputStream.close();
        }
        if(inputStream != null) {
            inputStream.close();
        }
    }
}
```

上述单线程BIO的demo中，两个地方存在阻塞阶段，分别是：
* Socket socket = serverSocket.accept()：等待新的客户端建立连接。
* inputStream.read(bytes)：读取客户端消息。需阻塞等待数据达到并准备好。

### 2.1、多线程 BIO
![JAVA_BIO_MODEL_MULTI]

<font size=5>多线程模式的BIO</font>
* 依旧由主线程一个一个的接收客户端连接请求，但后续的业务处理则交给独立线程去处理。
* 当并发数量起来时，则需要创建足够多的线程去处理业务逻辑。不过需要考虑线程资源是有限的。

服务端多线程模式优化代码：
```Java
public static void main(String[] args) throws IOException {
    ServerSocket serverSocket = new ServerSocket(9999);
    log.info("==== 服务端启动 ====");
    try {
        while(true) {
            //阻塞，直至有新的连接建立
            Socket socket = serverSocket.accept();
            SocketServerThread socketServerThread = new SocketServerThread(socket);
            new Thread(socketServerThread).start();
        }
    } catch(Exception e) {
        log.error(e.getMessage(), e);
    } finally {
        if(serverSocket != null) {
            serverSocket.close();
        }
    }
}

// 业务处理线程
public class SocketServerThread implements Runnable{
    private Socket socket;
    public SocketServerThread (Socket socket) {
        this.socket = socket;
    }

    @Override
    public void run() {
        try {
            InputStream inputStream = socket.getInputStream();
            byte[] bytes = new byte[2048];

            //阻塞，等待数据到达
            int length = inputStream.read(bytes);
            String msg = new String(bytes,0,length);
            log.info(String.format("==== 当前线程名称：%s；收到信息：%s",Thread.currentThread().getName(),msg));

            //下面开始发送信息
            OutputStream outputStream = socket.getOutputStream();
            outputStream.write("向服务端发起请求：hello client".getBytes());
            outputStream.flush();

            //关闭
            outputStream.close();
            inputStream.close();
        }catch (Exception e){
            log.error(e.getMessage(), e);
        }
    }
}
```

多线程BIO和单线程BIO的区别主要在于接收到请求后的数据处理过程。但 **accept()** 和 **read(bytes)** 两处依旧是阻塞运行的状态，这两处才是 <font color='#0000FF'>同步阻塞</font>  模型的关键处。多线程的BIO并没有从根源上解决这个问题，同时又容易造成资源的失控。

所以想要效率和资源的进一步优化，则要考虑如何才能不阻塞？基于此JAVA引入 **NIO**


## 三、JAVA的IO模型——NIO
<font color='#0000FF'>NIO（Java non-blocking IO）模型，即非阻塞模型。</font> 这个模型其实就是基于 **BIO** 中的两处阻塞处进行修改，即：
* accept()：无论是否有新客户端连接，都立即返回。如果没有新客户端，则不断去获取，直至有新的客户端发来请求。
* read(bytes)：无论是否接收到信息，都立即返回。如果没有数据达到，则不断接收，直到有数据到达服务端。

但如上述则会导致程序不断调用IO，多线程模式，单单创建线程就是一项不小的开销了，再加上线程之间要来回切换，资源消耗根本扛不住，所以最好的方式就是有一个线程负责去不断轮询新链接、消息达到等，等有响应时则通知对应线程进行操作，这样就是避免了所有线程都是轮询，这就是 <font color='#0000FF'>IO多路复用模式</font>。

**JAVA NIO** 也实现了 **IO多路复用** 这种模型。
![JAVA_NIO_MODEL]


<font size=5>JAVA-NIO</font>:
* 主要由 Channel(通道)、Buffer(缓冲区)、Selector(选择器)三部分组成。
* **Channel(通道)**：客户端连接的抽象，每个客户端连接都对应一个 channel，负责数据的读写操作。并且每个 channel 都要注册在 Selector 上
* **Buffer(缓冲区)**：在NIO 库中，所有数据都是用缓冲区处理的。任何时候访问 NIO 中的数据，都是将它放到缓冲区中。
* **Selector(选择器)**：负责轮询注册在其上的 channel，这样的优点在于只需要一个线程就可以处理大量的客户端连接，当有客户端事件到达时，再将其分发出去交由其它线程处理；通过 selector 来实现 IO多路复用 原理。

服务端代码：
```Java
@Slf4j
public class SocketServer {

    //轮询周期
    private static final int POLLING_PERIOD = 1000;

    public static void main(String[] args) throws IOException {
        SocketServer socketServer = new SocketServer();
        socketServer.startServer();
    }

    private void startServer() throws IOException {
        //打开选择器
        Selector selector = Selector.open();

        //获取客户端连接抽象chennel、指定监听端口、指定阻塞模式为非阻塞
        ServerSocketChannel serverSocketChannel = ServerSocketChannel.open();
        serverSocketChannel.bind(new InetSocketAddress(9999));
        serverSocketChannel.configureBlocking(false);
        //注册，并监听客户端连接事件
        serverSocketChannel.register(selector, SelectionKey.OP_ACCEPT);

        while (true){
            //每分钟轮询一次，存在就绪事件则进行逻辑处理
            if(0 == selector.select(POLLING_PERIOD)){
                log.info("======== 服务端——尚未有就绪事件 ========");
                continue;
            }

            //获取就绪时间列表
            Set<SelectionKey> selectionKeys = selector.selectedKeys();
            Iterator<SelectionKey> iterator = selectionKeys.iterator();
            while (iterator.hasNext()){
                SelectionKey selectionKey = iterator.next();

                //根据注册时间状态，进行不同处理
                if(selectionKey.isAcceptable()){

                    //新链接建立
                    accept(selectionKey,selector);
                }else if (selectionKey.isReadable()){

                    //数据读取
                    read(selectionKey);
                }else if(selectionKey.isValid() && selectionKey.isWritable()){

                    //数据写入
                    write(selectionKey);
                }
                iterator.remove();
            }

        }
    }

    private void accept(SelectionKey selectionKey, Selector selector) throws IOException {
        ServerSocketChannel serverSocketChannel = (ServerSocketChannel) selectionKey.channel();
        SocketChannel socketChannel = serverSocketChannel.accept();
        socketChannel.configureBlocking(false);
        socketChannel.register(selector,SelectionKey.OP_READ);
    }

    private void read(SelectionKey selectionKey) throws IOException {
        log.info("===========服务端读取数据===========");
        SocketChannel socketChannel = (SocketChannel) selectionKey.channel();
        ByteBuffer buffer = ByteBuffer.wrap(new byte[1024]);
        int read = socketChannel.read(buffer);
        log.info("========== 服务端读取数据为："+new String(buffer.array(),0,read));

        selectionKey.interestOps(SelectionKey.OP_READ | SelectionKey.OP_WRITE);
    }
    private void write(SelectionKey selectionKey) throws IOException {
        log.info("===========服务端写入数据===========");
        String message = "hello client";
        ByteBuffer buffer = ByteBuffer.wrap(message.getBytes());
        SocketChannel socketChannel = (SocketChannel) selectionKey.channel();
        if(socketChannel.isOpen()){
            socketChannel.write(buffer);
        }
        //监听OP_WRITE不可一直监听，因为连接打开，缓冲区未满或者客户后端未调用shutdownOutPut等，一直都处于可写状态。
        selectionKey.interestOps(selectionKey.interestOps() & ~SelectionKey.OP_WRITE);
    }
}

```

客户端代码：
```Java
@Slf4j
public class SocketClient {

    //轮询周期
    private static final int POLLING_PERIOD = 1000;

    public static void main(String[] args) throws IOException {
        new SocketClient().clientStart();

    }

    public void clientStart() throws IOException {
        //创建客户端
        SocketChannel socketChannel = SocketChannel.open();
        socketChannel.configureBlocking(false);
        socketChannel.connect(new InetSocketAddress("127.0.0.1",9999));

        //绑定selector
        Selector selector = Selector.open();
        socketChannel.register(selector, SelectionKey.OP_CONNECT);

        while (true){
            //每分钟轮询一次，存在就绪事件则进行逻辑处理
            if(0 == selector.select(POLLING_PERIOD)){
                log.info("======== 客户端——尚未有就绪事件 ========");
                continue;
            }

            Iterator<SelectionKey> iterator = selector.selectedKeys().iterator();
            while (iterator.hasNext()){
                SelectionKey selectionKey = iterator.next();

                if(selectionKey.isConnectable()){
                    //连接事件
                    connect(selectionKey,selector);
                }else if (selectionKey.isReadable()){

                    //数据读取
                    read(selectionKey);
                }else if(selectionKey.isValid() && selectionKey.isWritable()){

                    //数据写入
                    write(selectionKey,selector);
                }
                iterator.remove();
            }
        }
    }

    private void connect(SelectionKey selectionKey,Selector selector) throws IOException {
        // 由于是客户端Channel，因而可以直接强转为SocketChannel对象
        SocketChannel channel = (SocketChannel) selectionKey.channel();
        channel.finishConnect();
        // 连接建立完成后就监听该Channel的WRITE事件，以供客户端写入数据发送到服务器
        channel.register(selector, SelectionKey.OP_WRITE);
    }

    private void write(SelectionKey key, Selector selector) throws IOException {
        log.info("===========客户端写入数据===========");
        SocketChannel channel = (SocketChannel) key.channel();
        String message = Thread.currentThread().getId()+"hello client";
        channel.write(ByteBuffer.wrap(message.getBytes()));
        // 数据写入完成后，客户端Channel监听OP_READ事件，以等待服务器发送数据过来
        channel.register(selector, SelectionKey.OP_READ);
    }

    private void read(SelectionKey key) throws IOException {
        log.info("===========客户端读取===========");
        SocketChannel channel = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.wrap(new byte[1024]);
        int read = channel.read(buffer);
        if (read == -1) {
            channel.close();
            return;
        }
        log.info("========== 客户端读取数据为："+new String(buffer.array(),0,read));
    }
}
```
上述是简单的 **NIO** 应用的示例，实际项目中应用时最好使用 **reactor模式** 进行封装处理。
![Reactor_MODEL]
> 图片来源于大神 **Doug Lea** 的 [Scalable IO in Java](https://gee.cs.oswego.edu/dl/cpjslides/nio.pdf) 文章。



## 四、JAVA的IO模型——AIO
<font color='#0000FF'>AIO（Java Asynchronous I/O）</font>： 叫做异步非阻塞的 I/O，引入了异步通道的概念，采用了 **Proactor** 模式，有效的请求才会启动线程，特点就是先由操作系统完成后才通知服务端程序启动线程去处理，一般用于连接数较多且连接时长较长的应用。

区别于 **NIO** 的轮询操作不同，**AIO** 基于事件回调来完成IO操作。即当客户端发送消息之后，操作系统接收消息并将消息准备好后才通知服务端，服务端直接回调已注册好的回调方式直接执行操作。

![异步IO]

服务端代码：
```Java
private static final Object waitObject = new Object();

public static void main(String[] args) throws IOException{
    ByteBuffer byteBuffer = ByteBuffer.allocate(1024);
    AsynchronousServerSocketChannel serverSocketChannel = AsynchronousServerSocketChannel.open().bind(new InetSocketAddress(9999));
    serverSocketChannel.accept(null, new CompletionHandler<AsynchronousSocketChannel, Object>() {
        @Override
        public void completed(AsynchronousSocketChannel asc, Object attachment) {
            byteBuffer.clear();
            byteBuffer.put("hello client".getBytes());
            byteBuffer.flip();
            asc.read(byteBuffer, null, new CompletionHandler<Integer, Object>() {
                @Override
                public void completed(Integer result, Object attachment) {

                    byteBuffer.flip();
                    String rs = new String(byteBuffer.array(),0,result);
                    System.out.println("=========== 服务端读取："+rs);
                }
                @Override
                public void failed(Throwable exc, Object attachment) {}
            });

            asc.write(byteBuffer, null, new CompletionHandler<Integer, Object>() {
                @Override
                public void completed(Integer result, Object attachment) {
                    byteBuffer.clear();
                }
                @Override
                public void failed(Throwable exc, Object attachment) {

                }
            });
        }
        @Override
        public void failed(Throwable exc, Object attachment) {}
    });
    while(true) {}
}
```

客户端代码：
```Java
public static void main(String[] args) throws IOException{
    ByteBuffer byteBuffer = ByteBuffer.allocate(1024);
    AsynchronousSocketChannel asynchronousSocketChannel = AsynchronousSocketChannel.open();
    asynchronousSocketChannel.connect(new InetSocketAddress("127.0.0.1", 9999), null, new CompletionHandler<Void, Object>() {
        @Override
        public void completed(Void result, Object attachment) {
            byteBuffer.clear();

            asynchronousSocketChannel.read(byteBuffer, null, new CompletionHandler<Integer, Object>() {
                @Override
                public void completed(Integer result, Object attachment) {
                    byteBuffer.flip();
                    String rs = new String(byteBuffer.array(),0,result);
                    System.out.println("======== 客户端读取："+rs);

                    byteBuffer.clear();
                    byteBuffer.put("hello server".getBytes());
                    byteBuffer.flip();
                    asynchronousSocketChannel.write(byteBuffer);
                }
                @Override
                public void failed(Throwable exc, Object attachment) {}
            });
        }

        @Override
        public void failed(Throwable exc, Object attachment) {}
    });
    while(true) {}
}
```

**Java的AIO** 是基于NIO的基础上发展出来的异步IO，相关实现类也都是在NIO
的包下面，主要有以下几种：
* AsynchronousServerSocketChannel：服务端Socket通道类，负责服务端Socket的创建和监听；
  * 使用主要经历经过三个步骤：创建/打开通道、绑定地址和端口和监听客户端连接请求。从上面的demo也可以看出来。
* AsynchronousSocketChannel：客户端Socket通道类，负责客户端消息读写；
  * 需要先通过 **open()** 创建和打开一个AsynchronousSocketChannel实例，再调用其 **connect()** 方法连接到服务端，接着才可以与服务端交互。
* CompletionHandler<A,V>：消息处理回调接口，是一个负责消费异步IO操作结果的消息处理器；
*ByteBuffer：负责承载通信过程中需要读、写的消息。

JAVA NIO和JAVA AIO框架，除了因为操作系统的实现不一样而去掉了Selector外，其他的重要概念都是存在的，例如上文中提到的Channel的概念，还有演示代码中使用的Buffer缓存方式。实际上JAVA NIO和JAVA AIO框架您可以看成是一套完整的“高并发IO处理”的实现。


## 五、总结
既然Java本身提供了各种IO模型的实现，那么为什么还要使用Netty呢？首先说下为什么不用原生Java IO：
* NIO、AIO的类库和API繁杂，使用麻烦。
* 需要具备其他的额外技能做铺垫，例如熟悉Java多线程编程。这是因为NIO编程涉及到Reactor模式，你必须对多线程和网路编程非常熟悉，才能编写出高质量的NIO程序。
* 可靠性能力补齐，工作量和难度都非常大。例如客户端面临断连重连、网络闪断、半包读写、失败缓存、网络拥塞和异常码流的处理等问题，NIO编程的特点是功能开发相对容易，但是可靠性能力补齐的工作量和难度都非常大。

再说下为什么选择Netty：
* API使用简单，开发门槛低；
* 功能强大，预置了多种编解码功能，支持多种主流协议；定制能力强，可以通过ChannelHandler对通信框架进行灵活地扩展；
* 提供可靠的、易维护的、高性能的 **NIO/AIO** 服务器应用。
* 经历了大规模的商业应用考验，质量得到验证。在互联网、大数据、网络游戏、企业应用、电信软件等众多行业得到成功商用，证明了它已经完全能够满足不同行业的商业应用了。















[JAVA_BIO_MODEL]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/JAVA_BIO_MODEL.jpg

[JAVA_BIO_MODEL_MULTI]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/JAVA_BIO_MODEL_MULTI.jpg

[JAVA_NIO_MODEL]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/JAVA_NIO_MODEL.jpg

[Reactor_MODEL]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/Reactor_MODEL.jpg

[异步IO]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/theoretical_knowledge/异步IO.jpg