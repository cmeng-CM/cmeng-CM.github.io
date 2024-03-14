---
title: Zookeeper之Watcher机制
tags: zookeeper
categories: zookeeper
abbrlink: f91292b9
date: 2020-08-17 16:13:12
---




 <font size=7>Zookeeper之Watcher</font>

watcher机制是zookeeper的三大特性之一，它是很多应用场景的前提，比如：集群配置、管理，发布、订阅，资源抢占协调等等。

## watcher原理
原理框架图：  
![zookeeper原理框架](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/zookeeper/zookeeper-watcher原理框架.jpeg)   

## 注册和通知
zookeeper的watcher机制主要由client、server和watcherManager组成，包含注册和通知两个阶段。  
### 注册表
#### 客户端注册表  
在 client 端注册表为 ZkWatchManager，ZkWatchManager的存储机制为三种
  * dataWatches：针对节点的数据监听。
  * existWatches：客户端独有的存储方式，因为节点是否存在需要客户端自己判断。
  * childWatches：子节点监听。
源码：

```Java
//客户端  其中Set<Watcher>实际复制对象类型为HashSet<Watcher>
private static class ZKWatchManager implements ClientWatchManager {
    private final Map<String, Set<Watcher>> dataWatches =
        new HashMap<String, Set<Watcher>>();
    private final Map<String, Set<Watcher>> existWatches =
        new HashMap<String, Set<Watcher>>();
    private final Map<String, Set<Watcher>> childWatches =
        new HashMap<String, Set<Watcher>>();

    //创建Zoookeeper链接时传入的watcher会赋值到：defaultWatcher
    private volatile Watcher defaultWatcher;
}
```

三种存储机制中，Set<Watcher>的实现都是HashSet<Watcher>，由此可得出：
  * 同一路径下的同一watcher实例，无论注册多少次都只会记录一次，即触发后只通知一次。
  * 同一路径注册多个不同的watcher，会通知多次。即每个注册watcher都会被通知。

#### 服务端注册表
在 server 端注册表为 WatcherWatchManager，WatcherWatchManager的存储机制分为两种：
  * dataWatches：针对节点的数据监听。
  * childWatches：子节点监听。  

与 client 比少的 existWatches 也很容易理解，因为节点是否存在需要客户端去判断。  
两种机制均由 WatchManager 类来实现，WatchManager中包含两个重要的数据结构，分别是：
  * watchTable：从数据节点(即路径)的粒度来维护  
  * watch2Paths：从watcher的粒度来维护。  

注意这里的watcher含义表示远程连接，所以watchTable表示一个目录下可能有多个消费者的监听连接，而watch2Paths表示一个消费者可能会对多个目录建立监听，显然多目录的监听会复用一个连接。

源码：
```Java
//服务端
public class DataTree {
    private static final Logger LOG = LoggerFactory.getLogger(DataTree.class);

    /**
     * This hashtable provides a fast lookup to the datanodes. The tree is the
     * source of truth and is where all the locking occurs
     */
    private final ConcurrentHashMap<String, DataNode> nodes =
        new ConcurrentHashMap<String, DataNode>();

    private final WatchManager dataWatches = new WatchManager();

    private final WatchManager childWatches = new WatchManager();
    ....
  }
//dataWatches和childWatches是同一类的不同实例。即：
public class WatchManager {
    private static final Logger LOG = LoggerFactory.getLogger(WatchManager.class);

    private final HashMap<String, HashSet<Watcher>> watchTable =
        new HashMap<String, HashSet<Watcher>>();

    private final HashMap<Watcher, HashSet<String>> watch2Paths =
        new HashMap<Watcher, HashSet<String>>();

    public synchronized int size(){
        int result = 0;
        for(Set<Watcher> watches : watchTable.values()) {
            result += watches.size();
        }
        return result;
    }
    ......
  }
```



### 注册
#### 注册方式  
创建Zookeeper链接时会传入的watcher，这个watcher即为注册表中的defaultWatcher。  
其它注册方式：
  * getChildren(String path, Watcher watcher)
  * getChildren(String path, boolean watch)
  * getData(String path, boolean watch, Stat stat)
  * getData(String path, Watcher watcher, AsyncCallback.DataCallback cb, Object ctx)
  * exists(String path, boolean watch)
  * exists(String path, Watcher watcher)   

其中Boolean watch表示是否使用上下文中默认的watcher，即创建zk实例时设置的watcher. getData 和 exists 请求可以注册服务端注册表-dataWatches，getChilden 可以注册服务端注册表-childWatches。  
每个客户端都会维护 2 个线程，SendThread 负责处理客户端与服务端的请求通信，比如发送 getDataRequest，而 EventThread 则负责处理服务端的事件通知，即 watcher 的事件。

#### 注册流程
##### 客户端注册流程

zookeeper客户端watcher注册流程:
![zookeeper客户端watcher注册流程](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/zookeeper/zookeeper客户端watcher注册流程.jpeg)

几种客户端注册的流程大致相同,我们以exists为例。源码：

```Java
public Stat exists(final String path, Watcher watcher)
        throws KeeperException, InterruptedException
    {
        ......

        RequestHeader h = new RequestHeader();
        h.setType(ZooDefs.OpCode.exists);
        ExistsRequest request = new ExistsRequest();
        request.setPath(serverPath);
        request.setWatch(watcher != null);
        SetDataResponse response = new SetDataResponse();
        ReplyHeader r = cnxn.submitRequest(h, request, response, wcb);

        ......
    }
```


总的来说就是针对不同API进行类似的请求标记，watcher封装，然后将请求放入队列等待(SendThread)调度后发送到服务端。

##### 服务端注册流程
server端接收到请求后的处理流程：
![zookeeper原理框架](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/zookeeper/zookeeper注册server端流程.jpeg)   

*FinalRequestProcessor*：为服务端统一处理类，客户端所有操作及请求最终都会在此进行相应流程处理
```Java
/**
 * This Request processor actually applies any transaction associated with a
 * request and services any queries. It is always at the end of a
 * RequestProcessor chain (hence the name), so it does not have a nextProcessor
 * member.
 *
 * This RequestProcessor counts on ZooKeeperServer to populate the
 * outstandingRequests member of ZooKeeperServer.
 */
public class FinalRequestProcessor implements RequestProcessor{}
```

以exists为例：

```Java
case OpCode.exists: {
    lastOp = "EXIS";
    // TODO we need to figure out the security requirement for this!
    ExistsRequest existsRequest = new ExistsRequest();
    ByteBufferInputStream.byteBuffer2Record(request.request,
            existsRequest);
    String path = existsRequest.getPath();
    if (path.indexOf('\0') != -1) {
        throw new KeeperException.BadArgumentsException();
    }
    Stat stat = zks.getZKDatabase().statNode(path, existsRequest
            .getWatch() ? cnxn : null);
    rsp = new ExistsResponse(stat);
    break;
}
```

由源码可知，这边会通过一些 case 来判断请求类型，watcher最后会经由ZKDatabase的statNode进行操作。根据源码追寻可知：

*ZKDatabase*
```Java

 /**
  * This class maintains the in memory database of zookeeper
  * server states that includes the sessions, datatree and the
  * committed logs. It is booted up  after reading the logs
  * and snapshots from the disk.
  */
 public class ZKDatabase{
   ....

   public Stat statNode(String path, ServerCnxn serverCnxn) throws KeeperException.NoNodeException {
       return dataTree.statNode(path, serverCnxn);
   }

   .....
 }
```
```Java

public Stat statNode(String path, Watcher watcher)
        throws KeeperException.NoNodeException {
    Stat stat = new Stat();
    DataNode n = nodes.get(path);
    if (watcher != null) {
        dataWatches.addWatch(path, watcher);
    }
    if (n == null) {
        throw new KeeperException.NoNodeException();
    }
    synchronized (n) {
        n.copyStat(stat);
        return stat;
    }
}
```

ZKDatabase是在zookeeper运行时的数据库，server端注册表就存储在此，最后通过dataTree将watcher存储到dataWatches中。  

server端正常存储后返回客户端，在 ClientCnxn$SendThread 类的 readResponse->finishPacket 方法中会对watcher进行存储。  
可以看到这边调用了 watchRegistration 的 register 方法，而它就是根据请求类型来装入对应的 watchManager 中了(dataWatches、existWatches、childWatches)。

```Java
private void finishPacket(Packet p) {
        if (p.watchRegistration != null) {
            p.watchRegistration.register(p.replyHeader.getErr());
        }

        if (p.cb == null) {
            synchronized (p) {
                p.finished = true;
                p.notifyAll();
            }
        } else {
            p.finished = true;
            eventThread.queuePacket(p);
        }
    }
```


### 通知/watcher触发
#### 通知状态和事件类型
server端通知时主要内容为通知状态(org.apache.zookeeper.Watcher.Event.KeeperState)和事件类型(org.apache.zookeeper.Watcher.Event.EventType)，二者均于WatchedEvent对象内进行传输。
```Java
/**
 *  A WatchedEvent represents a change on the ZooKeeper that a Watcher
 *  is able to respond to.  The WatchedEvent includes exactly what happened,
 *  the current state of the ZooKeeper, and the path of the znode that
 *  was involved in the event.
 */
public class WatchedEvent {
  ......
  }
```

##### 通知状态   

连接状态|描述  
:-|:-  
KeeperState.Disconnected | 当客户端断开连接（与集群中的任何一台断开连接）时的状态就是Disconnected  
KeeperState.SyncConnected | 当客户端与zookeeper集群中的任意一台建立连接，这时的事件状态就是SyncConnected  
KeeperState.AuthFailed | 客户端进行连接认证失败时，事件状态为AuthFailed
KeeperState.ConnectedReadOnly	| 当前客户端连接到的zookeeper服务是只读的，此时事件状态是ConnectedReadOnly，这时的客户端只可以进行读操作，而不能进行写操作
KeeperState.SaslAuthenticated	| 用于通知客户端它们是SASL认证的
KeeperState.Expired	| 客户端与zookeeper服务端建立连接后每隔一定时间会发送一次心跳检测，当心跳检测没有收到服务端的响应时即认定断开连接，session失效，此时的事件状态就是Expired，如果客户端想访问服务端，需要重新建立连接。  

<font color='red'>注意：</font>zookeeper上述状态在触发时，除了SyncConnected会存在包含所有事件的情况，其它状态记录的事件类型都是：EventType.None

##### 事件类型

zookeeper事件|描述
:-|:-
EventType.NodeCreated	| 当节点被创建时，该事件被触发
EventType.NodeChildrenChanged	| 当节点的直接子节点被创建、被删除、子节点数据发生变更时，该事件被触发
EventType.NodeDataChanged	| 当节点的数据变化或版本变化时，该事件被触发
EventType.NodeDeleted	| 当节点被删除时，该事件被触发
EventType.None	| 当zookeeper客户端的连接状态发生变更时（上面连接状态表格中所列），描述的事件类型为EventType.None

##### API方法与触发事件关联关系
我们以test节点为例

注册方式 |	NodeCreated	| NodeChildrenChanged	| NodeDataChanged	| NodeDeleted
:-|:-|:-|:-|:-
zk.getChildren(“/test”,watcher) |	 | 	可监控	| | 	可监控
zk.exists(“/test”,watcher) |	可监控	| |	可监控 |	可监控
zk.getData(“/test”,watcher) |	|| 	可监控 |	可监控

客户端只能收到服务器发过来的相关事件通知，并不能获取到对应数据节点变化前后的数据。

#### 触发
我们以setDate方法为例。server端所有的处理均在FinalRequestProcessor里，当请求处理完成后会进行watcher事件的触发。我们以setDate为例追踪下触发的流程。

在FinalRequestProcessor中有这么一段代码：
```Java
if (request.hdr != null) {
   TxnHeader hdr = request.hdr;
   Record txn = request.txn;

   rc = zks.processTxn(hdr, txn);
}
```
追踪下去就会找到 DataTree 类处理 setData 请求的具体逻辑。
```java
public Stat setData(String path, byte data[], int version, long zxid,
            long time) throws KeeperException.NoNodeException {
    ......
    dataWatches.triggerWatch(path, EventType.NodeDataChanged);
    return s;
}

public Set<Watcher> triggerWatch(String path, EventType type, Set<Watcher> supress) {
    WatchedEvent e = new WatchedEvent(type,
            KeeperState.SyncConnected, path);
    HashSet<Watcher> watchers;
    synchronized (this) {
        watchers = watchTable.remove(path);
        if (watchers == null || watchers.isEmpty()) {
            if (LOG.isTraceEnabled()) {
                ZooTrace.logTraceMessage(LOG,
                        ZooTrace.EVENT_DELIVERY_TRACE_MASK,
                        "No watchers for " + path);
            }
            return null;
        }
        for (Watcher w : watchers) {
            HashSet<String> paths = watch2Paths.get(w);
            if (paths != null) {
                paths.remove(path);
            }
        }
    }
    for (Watcher w : watchers) {
        if (supress != null && supress.contains(w)) {
            continue;
        }
        w.process(e);
    }
    return watchers;
}

```

可以看到逻辑处理完会调用triggerWatch方法，此方法的作用就是从server端的watchManager中获取watcher并在watchTable 和 watch2Paths 中移除自身，所以 watcher 是单次的。  

最后将封装好的通知即源码中的 e 对象放入watcher的process方法中，process的作用其实就是去发送通知。以 Watcher的一个实现类NioServerCnxn 为例就是调用了其 sendResponse 方法将通知事件发送到客户端，发送前会将 watchedEvent 转换成 watcherEvent 进行发送。

客户端最后会将通知交由EventThread进行对应watcher的process方法调用。

至此，zookeeper 的整个 watcher 交互逻辑就已经结束了。
