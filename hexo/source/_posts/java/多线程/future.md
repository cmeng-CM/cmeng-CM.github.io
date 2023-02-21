---
title: java的future体系
tags: JVM
categories:
  - java
  - 多线程
top: true
keywords: Future
abbrlink: 9fca4482
date: 2020-08-18 16:13:12
---

## 一、Future概念
### 1.1、概念
<font color='blue'> **[Oracle官方文档](https://docs.oracle.com/en/java/javase/18/docs/api/java.base/java/util/concurrent/Future.html)** </font> 针对Future接口解释如下：未来表示异步计算的结果。提供了检查计算是否完成，等待计算完成以及检索计算结果的方法。只有在计算完成时，才能使用方法 **get()** 检索结果，如有必要，在计算准备就绪之前将其阻止。取消由取消方法执行。

举个例子：发快递时的快递单号，整个快递过程中单号就是唯一的重要标识与凭证。**Future** 就类似于这个单号，在异步操作中，可以根据 **Future** 去提取相关的操作结果。所以**Future** 表示的是异步任务还没完成提前给出的未来结果。

### 1.2、Future  
java中 Future 就是对于具体的 **Runnable** 或者 **Callable**（下面会详细介绍） 任务的执行结果进行取消、查询是否完成、获取结果。必要时可以通过get方法获取执行结果，该方法会阻塞直到任务返回结果。

**代码定义**：
```Java
public interface Future<V> {
    boolean cancel(boolean mayInterruptIfRunning);
    boolean isCancelled();
    boolean isDone();
    V get() throws InterruptedException, ExecutionException;
    V get(long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
}
```

**提供功能点：**
* cancel：用来取消任务，成功：true，失败：false。如果任务【已完成】或【未执行】或【被取消过】则返回false。
    * 参数 **mayInterruptIfRunning** 表示是否允许取消正在执行却没有执行完毕的任务。
* isCancelled：方法表示任务是否被取消成功，如果在任务正常完成前被取消成功，则返回 true。
* isDone方法表示任务是否已经完成，若任务完成，则返回true；
* get()方法用来获取执行结果，这个方法会产生阻塞，会一直等到任务执行完毕才返回；
* get(long timeout, TimeUnit unit)用来获取执行结果，如果在指定时间内，还没获取到结果，就直接返回null。

**也就是说Future提供了三种功能：**
* 判断任务是否完成；
* 能够中断任务；
* 能够获取任务执行结果。
因为Future只是一个接口，所以是无法直接用来创建对象使用的，因此就有了下面的FutureTask。


### 1.2、与Thread区别
常见的两种创建线程的方式。一种是直接继承Thread，另外一种就是实现Runnable接口。Future与这二者的唯一区别就是：**Thread是没有返回结果的，而Future模式是有返回结果的。**


## 二、Future使用
先假设个场景，我们要做烧仙草奶茶。那么就需要分别把烧仙草和奶茶做好，然后再做出烧仙草奶茶，前面的烧仙草的制作和奶茶的制作都耗时不短，而且二者完全独立，所以可以有二者同时进行即有两个线程分别去制作。等均完成后进行最后的制作。
```Java
public static void main(String[] args) throws Exception {
    ExecutorService executorService = Executors.newCachedThreadPool();

    FutureTask<String> makeGrassJelly = new FutureTask<>(new Callable<String>() {
        @Override
        public String call() throws Exception {
            System.out.println(Thread.currentThread().getName() + ":" + "开始制作烧仙草。。。。。");
            // 模拟制作耗时耗时
            Thread.sleep(3000);
            System.out.println(Thread.currentThread().getName() + ":"  + "烧仙草已经做好了...");
            return "烧仙草";
        }
    });
    executorService.submit(makeGrassJelly);

    //也可使用如下方式，两种方式的效果一样，只不过一个使用的是ExecutorService，一个使用的是Thread
    /*
    Thread thread = new Thread(makeGrassJelly);
    thread.start();
    */

    // 在制作烧仙草的同时制作奶茶
    System.out.println(Thread.currentThread().getName() + ":"  + " 烧仙草的线程已经开始，下面我们做奶茶...");
    // 模拟奶茶制作的耗时
    Thread.sleep(2000);
    System.out.println(Thread.currentThread().getName() + ":"  + "奶茶准备好了");
    String milkTea = "奶茶";

    // 开水已经稍好，我们取得烧好的开水
    String grassJelly = makeGrassJelly.get();

    System.out.println(Thread.currentThread().getName() + ":"  + grassJelly  + milkTea + "：制作完成了，可以开吃了");
}
```

执行结果：
> main: 烧仙草的线程已经开始，下面我们做奶茶...
> pool-1-thread-1:开始制作烧仙草。。。。。
> main:奶茶准备好了
> pool-1-thread-1:烧仙草已经做好了...
> main:烧仙草奶茶：制作完成了，可以开吃了

**从demo可知，使用Future步骤如下：**
* 新建一个Callable匿名函数实现类对象，我们的业务逻辑在Callable的call方法中实现，其中Callable的泛型是返回结果类型；
* 然后把Callable匿名函数对象作为FutureTask的构造参数传入，构建一个futureTask对象；
* 然后再把futureTask对象作为Thread构造参数传入并开启这个线程执行去执行业务逻辑；
* 最后我们调用futureTask对象的get方法得到业务逻辑执行结果。

可以看到跟 Future 使用有关的JDK类主要有 **FutureTask** 和 **Callable** 两个，下面分别对对 **Callable** 和 **FutureTask** 进行源码分析。



## 三、Callable
正式进入Future模式讲解前，先了解下预备知识之——Callable。

### 3.1、Callable 介绍
**Callable：** 代表一段可以调用并返回结果的代码；**Future接口** 表示异步任务，是还没有完成的任务给出的未来结果。所以说 **Callable** 用于产生结果，**Future** 用于获取结果。 

**代码声明**：
```java
public interface Callable<V> {
    /**
     * 计算结果，如果计算失败则抛出异常
     *
     * @return computed result
     * @throws Exception if unable to compute a result
     */
    V call() throws Exception;
}
```

可以看到，这是一个泛型接口，call()函数返回的类型就是传递进来的V类型。  
一般情况下是配合 ExecutorService 来使用的，在 ExecutorService 接口中声明了若干个submit方法的重载版本：
```Java
<T> Future<T> submit(Callable<T> task);
<T> Future<T> submit(Runnable task, T result);
Future<?> submit(Runnable task);
```
第一个 **submit** 方法里面的参数类型就是 **Callable**。返回的是 **Future** 类型对象。

### 3.2、与Runnable
1. 相同点
    * 都可以开发多线程。
    * 都可以使用ExecutorService来执行。   

2. 不同点
    * Callable有返回值，可以向上抛异常。Runnable不行。
    * 都使用 ExecutorService 来执行，Callable 的返回值有意义，Runnable 的返回值为空。

### 3.3、Callable执行
**Callable** 的使用方式有两种一种是结合 **ExecutorService** 提交使用，一种是构建 **FutureTask** 对象来使用。

就先聊聊 Callable 的使用方法之一是：ExecutorService 的 submit 方法，那么我们就看下具体的执行逻辑和涉及的相关类型。

**异步执行demo**

```java
public void executeTask(){
    ExecutorService executorService = Executors.newCachedThreadPool();

    //提交带有返回值的任务以供执行，并返回表示任务挂起结果的 Future
    Future submit = executorService.submit(()->{
        //业务逻辑执行
        log.info("in callable!!!!");
        return "callable";
    });
    try {
        //获取执行结果
        submit.get();
    } catch (Exception e) {
        log.error("==== Asynchronous execution exception");
        throw new RuntimeException(e);
    }
}
```

**执行逻辑：**
**1. 获取 ExecutorService 实例**：
获取 **ExecutorService** 实例，用于任务提交操作。**newCachedThreadPool()** 将返回 **ThreadPoolExecutor** 类型对象实例。

**2. submit() 提交任务**
* 执行对象类型
**Executors.newCachedThreadPool()** 产生的对象实例类型为 **ThreadPoolExecutor**。其继承实现模型为：  
![ThreadPoolExecutor类结构模型][ThreadPoolExecutor类结构模型]
* 方法调用源码分析
提交任务的方法 **submit** 由 **ExecutorService** 接口定义，在 **AbstractExecutorService** 里面实现。**ThreadPoolExecutor** 类没有再次覆盖实现。因此最终调用的代码逻辑为 AbstractExecutorService 内的逻辑，其实现逻辑如下：    

```Java
// AbstractExecutorService.java
public <T> Future<T> submit(Callable<T> task) {
    if (task == null) throw new NullPointerException();
    RunnableFuture<T> ftask = newTaskFor(task);
    execute(ftask);
    return ftask;
}

// newTaskFor实现
protected <T> RunnableFuture<T> newTaskFor(Callable<T> callable) {
    return new FutureTask<T>(callable);
}
```
由源码可知，submit执行时：
1. 先将Callable接口实现转化为 **FutureTask** 类型对象。
2. 然后再通过 **execute** 执行。  

具体执行逻辑下面聊到 **FutureTask** 会详细说明。此处已经说明了 **Callable 最终一定通过与 Future 结合进行使用**，达到异步执行任务且返回相关结果的功能。所以两种执行方式的底层实现实为一种：即结合 **FutureTask** 进行使用。

那么接下来就聊聊 **FutureTask** 。

## 四、FutureTask

### 4.1、FutureTask类结构分析
FutureTask的类结构：
![FutureTask类结构模型][FutureTask类结构模型]

通过类图我们不难看出,**RunnableFuture** 继承了 **Runable** 以及 **Future** 接口，所以它即可以被线程异步执行，也可作为Future得到callable的计算结果。

下面进入正题聊聊 **FutureTask**，它实现了**RunnableFuture** 接口，所以也是 **Future** 和**Runnable** 接口的具体实现类，即异步任务执行后我们能够获取到异步任务的执行结果。

下面就详详细的通过源码分析下 **FutureTask** 的执行逻辑。

### 4.2、源码分析——属性
先看下具体属性，这个在整体运行逻辑中都是很重要的。
```Java
// FutureTask.java

/* Possible state transitions:
 * NEW -> COMPLETING -> NORMAL
 * NEW -> COMPLETING -> EXCEPTIONAL
 * NEW -> CANCELLED
 * NEW -> INTERRUPTING -> INTERRUPTED
*/
// 任务执行状态标识
private volatile int state;

//定义运行状态码
private static final int NEW          = 0;
private static final int COMPLETING   = 1;
private static final int NORMAL       = 2;
private static final int EXCEPTIONAL  = 3;
private static final int CANCELLED    = 4;
private static final int INTERRUPTING = 5;
private static final int INTERRUPTED  = 6;


/** Callable对象实现，用于异步执行 */
private Callable<V> callable;

/** 从 get() 返回的结果或抛出的异常 */
private Object outcome; 

/** 用来执行callable任务的线程 */
private volatile Thread runner;

/** 在 Treiber 中记录等待线程的简单链表节点 */
private volatile WaitNode waiters;


// VarHandle mechanics
private static final VarHandle STATE;
private static final VarHandle RUNNER;
private static final VarHandle WAITERS;
```
根据Java并发工具类三板斧：
* 状态
* 队列
* CAS操作
从这个方面分别对不同的属性进行详细的解析。

#### 4.2.1、属性——状态
```Java
// FutureTask.java

private static final int NEW          = 0;
private static final int COMPLETING   = 1;
private static final int NORMAL       = 2;
private static final int EXCEPTIONAL  = 3;
private static final int CANCELLED    = 4;
private static final int INTERRUPTING = 5;
private static final int INTERRUPTED  = 6;
```
**FutureTask** 中定义了七种状态，一种初始状态，四种终态，两种中间态，由 **0-6** 分别代表分别如下：
1. 初始状态：
    * NEW：初始状态，这是由构造函数保证的。
2. 中间态：**瞬间状态，而且此状态并不代表任务正执行，而是已经执行完成正（成功或失败异常）在设置返回结果**
    * COMPLETING： 正在设置任务结果
    * INTERRUPTING： 正在中断运行任务的线程
3. 终态
    * NORMAL：任务正常执行完毕
    * EXCEPTIONAL：任务执行过程中发生异常
    * CANCELLED：任务被取消
    * INTERRUPTED：任务被中断


**执行状态流转顺序如下**：
1. **NEW -> COMPLETING -> NORMAL**
    * 任务正常执行且完成设置返回结果。
    * 状态由 **set** 方法设置。
2. **NEW -> COMPLETING -> EXCEPTIONAL**
    * 任务执行异常。
    * 状态由 **setException** 方法设置。
3. **NEW -> CANCELLED**
    * 任务取消，即调用了 **cancel(false)**
    * 状态由 **cancel** 方法设置。
4. **NEW -> INTERRUPTING -> INTERRUPTED**
    * 任务取消，即调用了 **cancel(true)**
    * 状态由 **cancel** 方法设置。

因此涉及状态修改的只有 set、setException、cancel这三个方法，方法的具体逻辑后面再详细分析。


#### 4.2.2、属性——队列
聊队列时同时将其它相关操作的属性一块聊一聊，
1. **处理逻辑（callable）**
包含具体的异步执行逻辑内容，整个生命周期从构造函数接收，到call()方法调用执行，到最后的移除销毁整个过程与线程的具体执行逻辑息息相关。后面聊到具体执行逻辑再分析。
2. **执行（runner）**
用来执行 callable 任务的线程，**runner 属性是在运行时被初始化的。** 简单点说，就是run方法被调用时赋值。
3. **结果（outcome）**
任务的执行结果，成功为 callable 内的返回结果，失败为异常对象。
4. **队列（waiters）**
所有等待任务执行完毕的线程的集合。

在并发编程中使用队列通常是将 **当前线程包装成某种类型的数据结构扔到等待队列中，** 接下来看下waiters的结构定义：
```Java
static final class WaitNode {
    volatile Thread thread;
    volatile WaitNode next;
    WaitNode() { thread = Thread.currentThread(); }
}
```
简单的单项链表结构，仅有两个属性一个是当前线程 **thread**，一个是下一个队列节点对象 **next**。
*  **thread**：存放当前调用 **FutureTask** 内各相关方法的线程信息。
*  **next**：指向下一个节点的next属性。

根据 **WaitNode** 对象的数据结构和属性内容，可以很明显的知道它的作用，即：将当前线程信息存放至链表，按照 **后进先出** 的规则进行相关操作。

因为 **Future** 的 **get()/get(timeout)** 在 task 处于非完成状态时是需要 **阻塞等待** 的，如果多个线程进行 get 操作，显然需要一个链表/队列来维护这些等待线程，这就是waiters的意义所在。

简答模拟了一下五个线程同时调用 **get()** 方法，可看到当第5个线程进行时，**队列（waiters）** 已经有五个等待线程了：

![Future-waiters模拟][Future-waiters模拟]


其中 **runner** , **waiters** 和 **state** 都是用 **volatile** 关键字修饰，说明这三个变量都是多线程共享的对象（成员变量），会被多线程操作，此时用volatile关键字修饰是为了一个线程操作volatile属性变量值后，能够及时对其他线程可见。当然仅仅如此依旧存在线程安全的问题，所以其相关操作使用的CAS机制来确保线程的安全性。下面就聊下CAS。

#### 4.2.3、属性——CAS
```Java
// FutureTask.java

private static final VarHandle STATE;
private static final VarHandle RUNNER;
private static final VarHandle WAITERS;
static {
    try {
        MethodHandles.Lookup l = MethodHandles.lookup();
        STATE = l.findVarHandle(FutureTask.class, "state", int.class);
        RUNNER = l.findVarHandle(FutureTask.class, "runner", Thread.class);
        WAITERS = l.findVarHandle(FutureTask.class, "waiters", WaitNode.class);
    } catch (ReflectiveOperationException e) {
        throw new ExceptionInInitializerError(e);
    }
}
```
从这个静态代码块中我们也可以看出，CAS操作主要针对3个属性，包括 **STATE**、**RUNNER** 和  **WAITERS**，说明这3个属性基本是会被多个线程同时访问的。其中 **STATE**属性代表了任务的状态，**WAITERS** 属性代表了指向栈顶节点的指针。**RUNNER** 主要是为了 **中断或者取消任务** 做准备的，只有知道了执行任务的线程是谁，我们才能去中断它。

具体的操作也是使用了CAS方法即 **compareAndSet** 来完成的。


### 4.3、源码分析——构造函数
FutureTask有两个构造函数，分别看下源码：
```Java
// 构造函数1
// FutureTask.java

public FutureTask(Callable<V> callable) {
    if (callable == null)
        throw new NullPointerException();
    this.callable = callable;
    this.state = NEW;       // ensure visibility of callable
}

// 构造函数2
public FutureTask(Runnable runnable, V result) {
    this.callable = Executors.callable(runnable, result);
    this.state = NEW;       // ensure visibility of callable
}
```

构造函数1很好理解，传入 **Callable** 的实现类，将参数赋值属性 **callable**，同时将状态 **state** 置为初始状态 **NEW**，代表新建任务状态。

接着看构造函数2，很明显的区别在于入参变成了 **Runnable** 实现类，且增加了返回结果的泛型集。然后将二者通过 **Executors.callable()** 方法转变成了 **callable** 类型，那么就进入方法具体看下源码：
```Java
// FutureTask.java

public static <T> Callable<T> callable(Runnable task, T result) {
    if (task == null)
        throw new NullPointerException();
    return new RunnableAdapter<T>(task, result);
}

private static final class RunnableAdapter<T> implements Callable<T> {
    private final Runnable task;
    private final T result;

    RunnableAdapter(Runnable task, T result) {
        this.task = task;
        this.result = result;
    }
    public T call() {
        task.run();
        return result;
    }
    public String toString() {
        return super.toString() + "[Wrapped task = " + task + "]";
    }
}
```

由源码可知，方法直接调用了 **RunnableAdapter** 的构造函数，这个方法采用了设计模式中的适配器模式，将一个Runnable类型对象适配成Callable类型。当然 **result** 参数的存在只是为了将一个Runnable 类型适配成 Callable 类型，确实没什么实际意义。   


### 4.4、源码分析——执行(run方法)

#### 4.4.1、执行(run方法)——执行逻辑
**FutureTask** 实现了 **Runnable**，覆写了 **run** 方法，即用于异步执行的线程逻辑。**Callable** 即是需要执行的业务逻辑，他是业务逻辑的基本表现形式，保存在类属性callable，在run函数里面，调用callalbe.call()来执行业务逻辑。下面从源码来了解具体的执行逻辑：
```Java
// FutureTask.java

public void run() {
    //1、判断是否满足执行条件，满足条件设置runner属性
    if (state != NEW ||
        !RUNNER.compareAndSet(this, null, Thread.currentThread()))
        return;
    try {
        // 2、具体执行业务逻辑，根据执行情况做不同处理
        Callable<V> c = callable;
        // 执行前再次判断状态
        if (c != null && state == NEW) {
            V result;
            // 执行状态标识
            boolean ran;
            try {
                // 具体业务执行
                result = c.call();
                ran = true;
            } catch (Throwable ex) {
                result = null;
                ran = false;
                // 失败结果集设置
                setException(ex);
            }
            if (ran)
            // 成功结果集设置
                set(result);
        }
    } finally {
        //3、执行完的后处理逻辑
        runner = null;
        
        int s = state;
        if (s >= INTERRUPTING)
            handlePossibleCancellationInterrupt(s);
    }
}
```
从源码可知，具体执行共三步：
1. 判断是否满足执行条件，满足条件设置runner属性
    * 判断任务状态是否为 **NEW** 状态，如果不是，则可能执行完毕或已经被取消，所以直接返回。
    * 如果任务为 **NEW** 状态，则通过 **CAS操作** 将 **runner** 置为当前正在执行异步任务的线程。此处有两种情况：
        * **runner!=null**：则说明任务依旧处于NEW状态，但已经有线程在执行该任务，所以无需再次执行，CAS操作失败，直接返回。
        * **runner==null** ：说明还未有线程执行过异步任务，此时满足执行异步任务的条件，CAS操作成功，继续执行任务。
2. 具体执行，并根据结果进行相关操作
    * **if (c != null && state == NEW)**：再次判断任务状态，状态为NEW则继续执行。
    * **result = c.call();**：调用call()方法执行具体的业务逻辑，根据结果进行操作。
        * 失败则进入异常操作设置结果集 **setException(ex)**；并设置失败标识 **ran = false**。
        * 成功则设置成功标识 **ran = true** ，并进行成功后结果集的设置 **set(result)**；
3. 后处理逻辑
不管异步任务执行成功还是失败，首先将当前执行任务线程 **runner** 置为空，若其他线程有调用 **FutureTask.cancel(true)**，此时需要调用**handlePossibleCancellationInterrupt** 方法处理中断。

#### 4.4.2、执行(run方法)——Java线程的实现
Java线程的使用方式有很多，但最后都会归于 **Thread.start()**方法，无论是使用 Thread 直接调用 start()方法还是使用线程池进行多线程调用，最终都会归于此处。start()内容：
```Java
// Thread.java
public synchronized void start() {
        if (threadStatus != 0)
            throw new IllegalThreadStateException();
        group.add(this);
        boolean started = false;
        try {
            start0();
            started = true;
        } finally {
            try {
                if (!started) {
                    group.threadStartFailed(this);
                }
            } catch (Throwable ignore) {
                /* do nothing. If start0 threw a Throwable then
                  it will be passed up the call stack */
            }
        }
    }

// 本地方法start
private native void start0();

// 注册本地方法栈
private static native void registerNatives();
static {
    registerNatives();
}
```
可以看到，最终实现都是调用本地方法栈的 **start0();**。而这些native方法的注册是在Thread对象初始化的时候完成的，即上面的静态代码块内调用的 **registerNatives();** 。当该类被加载到 JVM 中的时候，它就会被调用，进而注册相应的本地方法。

而本地方法 **registerNatives** 是定义在 Thread.c 文件中的。Thread.c 是个很小的文件，它定义了各个操作系统平台都要用到的关于线程的公用数据和操作，如下：
```c
// openJdk-10版本  THread.c
static JNINativeMethod methods[] = {
    {"start0",           "()V",        (void *)&JVM_StartThread}, //java start0
    {"stop0",            "(" OBJ ")V", (void *)&JVM_StopThread},
    {"isAlive",          "()Z",        (void *)&JVM_IsThreadAlive},
    {"suspend0",         "()V",        (void *)&JVM_SuspendThread},
    {"resume0",          "()V",        (void *)&JVM_ResumeThread},
    {"setPriority0",     "(I)V",       (void *)&JVM_SetThreadPriority},
    {"yield",            "()V",        (void *)&JVM_Yield},
    {"sleep",            "(J)V",       (void *)&JVM_Sleep},
    {"currentThread",    "()" THD,     (void *)&JVM_CurrentThread},
    {"countStackFrames", "()I",        (void *)&JVM_CountStackFrames},
    {"interrupt0",       "()V",        (void *)&JVM_Interrupt},
    {"isInterrupted",    "(Z)Z",       (void *)&JVM_IsInterrupted},
    {"holdsLock",        "(" OBJ ")Z", (void *)&JVM_HoldsLock},
    {"getThreads",        "()[" THD,   (void *)&JVM_GetAllThreads},
    {"dumpThreads",      "([" THD ")[[" STE, (void *)&JVM_DumpThreads},
    {"setNativeName",    "(" STR ")V", (void *)&JVM_SetNativeThreadName},
};

#undef THD
#undef OBJ
#undef STE
#undef STR

JNIEXPORT void JNICALL
Java_java_lang_Thread_registerNatives(JNIEnv *env, jclass cls)
{
    (*env)->RegisterNatives(env, cls, methods, ARRAY_LENGTH(methods));
}
```
下面就要找具体是怎么调用的 **Thread.run()** 方法，在 jvm.cpp 中有如下代码：
```cpp
// hotSpot-10版本  jvm.cpp
JVM_ENTRY(void, JVM_StartThread(JNIEnv* env, jobject jthread))
  JVMWrapper("JVM_StartThread");
  JavaThread *native_thread = NULL;

  bool throw_illegal_thread_state = false;
  {
    MutexLocker mu(Threads_lock);
    if (java_lang_Thread::thread(JNIHandles::resolve_non_null(jthread)) != NULL) {
      throw_illegal_thread_state = true;
    } else {
      jlong size =
             java_lang_Thread::stackSize(JNIHandles::resolve_non_null(jthread));
      
      NOT_LP64(if (size > SIZE_MAX) size = SIZE_MAX;)
      size_t sz = size > 0 ? (size_t) size : 0;
    
    //主要看这里
      native_thread = new JavaThread(&thread_entry, sz);

      if (native_thread->osthread() != NULL) {
        
        native_thread->prepare(jthread);
      }
    }
  }
```
这里JVM_ENTRY是一个宏，用来定义JVM_StartThread 函数，可以看到函数内创建了真正的平台相关的本地线程，其线程函数是**thread_entry**，如下：
```Java 
// hotSpot-10版本  jvm.cpp
static void thread_entry(JavaThread* thread, TRAPS) {
    HandleMark hm(THREAD);
    Handle obj(THREAD, thread->threadObj());
    JavaValue result(T_VOID);
    JavaCalls::call_virtual(&result,obj,
    KlassHandle(THREAD,SystemDictionary::Thread_klass()),
    vmSymbolHandles::run_method_name(),    //看这里
    vmSymbolHandles::void_method_signature(),THREAD);
 }

class vmSymbolHandles: AllStatic {
   ...
    template(run_method_name,"run")  //这里!!! 这里决定了调用的方法名称是 “run”!
   ...
}
```
自此调用流程就清晰了：
![Thread-JVM运行机制.png][Thread-JVM运行机制] 


#### 4.4.3、执行(run方法)——成功结果set()
老规矩，首先看源码：
```Java
// FutureTask.java

protected void set(V v) {
    if (STATE.compareAndSet(this, NEW, COMPLETING)) {
        outcome = v;
        STATE.setRelease(this, NORMAL); // final state
        finishCompletion();
    }
}
```
该方法的调用只有通过 **FutureTask.run()** 方法才可以被调用，而 run 方法本身能执行到此处也是不会存在多线程的情况，因为能进行的前置要求存在 **CAS操作修改状态** 的步骤，由此分析其代码逻辑及含义：
1. 状态校验
其校验操作位**CAS修改NEW状态为COMPLETING**，所以只有状态为 **NEW** 的任务才可以进入其操作逻辑。这么做的意义在于执行**run** 方法逻辑时可能存在**cancel** 方法被调用，所以需要CAS操作来保证任务的状态为 NEW 才可以进入结果集设置的操作。
2. 设置结果集
根据执行结果即 **set的入参：V** 设置返回结果集。
3. 修改状态
将任务状态设置为 **NORMAL**，表示任务正常结束。此处对应的状态变化为：**NEW -> COMPLETING -> NORMAL。** 
4. 唤醒阻塞进程
调用任务执行完成方法，此时会唤醒阻塞的线程，调用done()方法和清空等待线程链表等。具体阻塞的进程的来源，上面聊队列的时候分析过具体的原因和情况。

#### 4.4.4、执行(run方法)——异常结果setException()
先上源码：
```Java
// FutureTask.java

protected void setException(Throwable t) {
    if (STATE.compareAndSet(this, NEW, COMPLETING)) {
        outcome = t;
        STATE.setRelease(this, EXCEPTIONAL); // final state
        finishCompletion();
    }
}
```
可以看到 **setException** 内的逻辑与 **set** 基本一致，区别在于返回结果此处是将异常设置进去，终态设置为 **EXCEPTIONAL** ，其它无区别。此处状态转换为： **NEW -> COMPLETING -> EXCEPTIONAL。**

#### 4.4.5、执行(run方法)——finishCompletion()
先上源码：
```Java
// FutureTask.java

private void finishCompletion() {
    // assert state > COMPLETING;
    // 根据 get 方法阻塞的队列，进行唤醒、移除等操作，若是get方法未被调用，则不进入循环
    for (WaitNode q; (q = waiters) != null;) {
        if (WAITERS.weakCompareAndSet(this, q, null)) {
            for (;;) {
                Thread t = q.thread;
                if (t != null) {
                    q.thread = null;
                    // 唤醒线程
                    LockSupport.unpark(t);
                }
                WaitNode next = q.next;
                if (next == null)
                    break;
                q.next = null; // unlink to help gc
                q = next;
            }
            break;
        }
    }
    // 无论有无阻塞队列，都调用done()，FutureTask内done()无任务实现内容。
    done();
    // 任务已执行完毕，已将结果存储至outcome中，因此将callable属性置为空
    callable = null;        // to reduce footprint
}
```
此处主要是针对 **waiters** 内被阻塞的线程队列，针对阻塞的线程进行唤醒、移除等操作。由于FutureTask中的队列本质上是一个Treiber栈，因此操作的顺序是 **后进先出** 即后面先来的线程先被先操作。  

#### 4.4.6、执行(run方法)——执行完成共有操作handlePossibleCancellationInterrupt()
先上源码：
```Java
private void handlePossibleCancellationInterrupt(int s) {
    if (s == INTERRUPTING)
        while (state == INTERRUPTING)
            Thread.yield(); // wait out pending interrupt
    }
```
可见该方法是一个自旋操作，如果当前的state状态是 **INTERRUPTING**，我们在原地自旋，直到 **state** 状态转换成终止态。意义在于：检查是否有遗漏的中断，如果有，等待中断状态完成。具体 **handlePossibleCancellationInterrupt** 为什么在任务执行完毕后调用，等聊到 **cancel()** 方法再详细分析。

### 4.5、源码分析——获取执行结果

#### 4.5.1、获取执行结果——get()
先上源码：
```Java
public V get() throws InterruptedException, ExecutionException {
        int s = state;
        if (s <= COMPLETING)
            s = awaitDone(false, 0L);
        return report(s);
    }

/**
    * @throws CancellationException {@inheritDoc}
    */
public V get(long timeout, TimeUnit unit)
    throws InterruptedException, ExecutionException, TimeoutException {
    if (unit == null)
        throw new NullPointerException();
    int s = state;
    if (s <= COMPLETING &&
        (s = awaitDone(true, unit.toNanos(timeout))) <= COMPLETING)
        throw new TimeoutException();
    return report(s);
}
```
由源码可知，获取执行结果有两个方法：
* **get()**：获取执行结果，如果未执行完毕，则阻塞等待。
* **get(long timeout, TimeUnit unit)**：获取执行结果，并设置超时时间，如果未超时则阻塞等待，如果已超时则 **移除当前阻塞线程** 并 **直接返回当前执行状态**
除了后者存在超时时间设置外，其他执行逻辑并无区别，主要阻塞获取执行结果的方法都是 **awaitDone** 下面详细分析下此方法。

#### 4.5.2、获取执行结果——awaitDone()
先上源码：
```Java
private int awaitDone(boolean timed, long nanos)
        throws InterruptedException {
    
    //超时相关设置
    long startTime = 0L;
    // 线程链表头节点
    WaitNode q = null;
    //是否已入阻塞队列
    boolean queued = false;
    for (;;) {
        // 【1-4】状态校验，如果已执行完毕，且当前队列节点不为空则将队列当前线程置为空后返回状态。如果当前队列节点为空则直接返回状态
        int s = state;
        if (s > COMPLETING) {
            if (q != null)
                q.thread = null;
            return s;
        }

        // 状态为COMPLETING则说明正在设置结果集，当前线程让出CPU时间片段，等待设置结果集完毕
        else if (s == COMPLETING)
            Thread.yield();

        // 【3-1】当前执行线程被中断，则移除队列节点，抛出中断异常
        else if (Thread.interrupted()) {
            removeWaiter(q);
            throw new InterruptedException();
        }

        // 【1-1】当前线程还未进入阻塞队列，则创建包含当前线程信息的队列节点。
        else if (q == null) {
            if (timed && nanos <= 0L)
                return s;
            q = new WaitNode();
        }

        // 【1-2】如果当前队列节点未入阻塞队列，则加入队列头部
        else if (!queued)
            queued = WAITERS.weakCompareAndSet(this, q.next = waiters, q);
        
        // 【2-1】若有超时设置，那么处理超时获取任务结果的逻辑
        else if (timed) {
            final long parkNanos;
            if (startTime == 0L) { // first time
                startTime = System.nanoTime();
                if (startTime == 0L)
                    startTime = 1L;
                parkNanos = nanos;
            } else {
                long elapsed = System.nanoTime() - startTime;
                if (elapsed >= nanos) {
                    removeWaiter(q);
                    return state;
                }
                parkNanos = nanos - elapsed;
            }
            // nanoTime may be slow; recheck before parking
            if (state < COMPLETING)
                LockSupport.parkNanos(this, parkNanos);
        }

        // 【1-3】阻塞当前线程
        else
            LockSupport.park(this);
    }
}
```
获取结果集的自旋循环处理逻辑，存在多个分支处理，每个分支的校验条件和操作逻辑均已在注释中描述，那么下面就看下每次循环都会执行哪些分支，同时进一步了解为什么每个分支的逻辑如此设计。

**情况 1：1、任务状态为NEW；2、无超时时间设置时，3、不存在中断操做时。循环内的情况**：
1. 第一次循环：
此时 **q=null**，进入队列节点创建操作，即：【1-1】，操作完此次循环结束。此时队列节点已创建，但尚未放入阻塞队列内。
2. 第二次循环：
此时  **queued=false**，进入将当前节点放入阻塞队列操作，即【1-2】，操作完此次循环结束。
3. 第三次循环
当前队列节点已创建且已放入阻塞队列，此时进入阻塞阶段，即【1-3】，操作完成循环结束。
4. 第四次循环
此时任务已执行完毕，阻塞线程被激活，进入结果集获取操作，即【1-4】，**awaitDone** 方法执行完毕，返回异步任务结果集。

**情况 2：1、任务状态为NEW；2、存在超时时间设置时，3、不存在中断操做时。循环内的情况**：
则在【1-3】和【1-4】中间加入【2-1】超时判断操作。其它同 **情况1**。

**情况 3：1、任务状态为NEW；2、无超时时间设置时，3、存在中断操做时。循环内情况：**
直接进入中断操作，移除当前队列节点，抛出异常即【3-1】。任务执行和任务取消都调用 **finishCompletion()** 方法，那么此处调用的意义在哪？此处调用意义：执行 **awaitDone** 时存在一种情况，即刚进行队列节点创建但还未将队列节点放入阻塞队列即【第一次循环】时。此时进行任务中断则队列节点无法在 **finishCompletion()** 中移除，所以需要在此处进行置空操作，方便GC回收。

**情况 4：1、任务状态为不为NEW。循环内情况：**
直接返回当前任务状态，存在当前队列节点则移除当前队列节点即【1-4】。原因类似 **情况2**，只不过中断操作变为任务完成。

#### 4.5.3、获取执行结果——report()
先上源码：
```Java
private V report(int s) throws ExecutionException {
    Object x = outcome;
    if (s == NORMAL)
        return (V)x;
    if (s >= CANCELLED)
        throw new CancellationException();
    throw new ExecutionException((Throwable)x);
}
```
根据状态获取结果集就很简单了，一共三个分支：
1. 状态为 **NORMAL**：即正常执行完成，返回 **Callable.call()** 方法执行结果即可。
2. 状态 **s >= CANCELLED**，说明存在取消情况，则抛出中断异常。
3. 其它状态为执行过程存在异常，则将异常类返回即可。

### 4.6、源码分析——取消任务
线上源码：
```Java
public boolean cancel(boolean mayInterruptIfRunning) {
    // 任务状态为NEW且根据mayInterruptIfRunning参数修改状态为INTERRUPTING或CANCELLED，二者任一
    // 失败或同时失败均返回 False
    if (!(state == NEW && STATE.compareAndSet
            (this, NEW, mayInterruptIfRunning ? INTERRUPTING : CANCELLED)))
        return false;
    try {    
        // 如果mayInterruptIfRunning=true，则获取当前任务执行线程，进行中断操作
        if (mayInterruptIfRunning) {
            try {
                Thread t = runner;
                if (t != null)
                    t.interrupt();
            } finally { // final state
                // 最后任务状态赋值为INTERRUPTED
                STATE.setRelease(this, INTERRUPTED);
            }
        }
    } finally {
        // 针对阻塞进程进行唤醒、移除等操作
        finishCompletion();
    }
    return true;
}
```
由源码可知：
1. 状态校验：
    * 状态不为NEW，直接返回false
    * 状态为NEW，根据参数 **mayInterruptIfRunning** 不同值，进行不同的状态修改，此处修改为CAS操作，修改失败则返回false。成功则继续执行取消操作。
2. 根据 mayInterruptIfRunning 不同值进行操作：
    * 为flase：跳过 **try** 代码块，直接执行 **finally** 操作。此时状态变化为：**NEW -> CANCELLED。**
    * 为true：则 **runner==null**，因为可能存在此时任务已经执行完成，将 runner 置为空了。如果不为空，则发送线程中断信号，发送中中断信号并不代表一定会真正的中断线程。此时状态变化为：**NEW -> INTERRUPTING -> INTERRUPTED**。

3. 唤醒阻塞线程
无论 **mayInterruptIfRunning** 参数为何值，最终都会唤醒阻塞的线程，即调用 **finishCompletion** 方法，因为此时任务已经是终态了。 **cancel()** 方法返回true。  
如果**cancel()** 返回true了，那么线程无论最终是否执行，**get()** 方法都会抛出**CancellationException**异常，因为 **report(int s)** 内会校验 **s >= CANCELLED**，具体可看上一节的 **report()**源码。

### 

### 4.7、源码分析——移除任务
```Java
private void removeWaiter(WaitNode node) {
    if (node != null) {
        node.thread = null;
        retry:
        for (;;) {          // restart on removeWaiter race
            for (WaitNode pred = null, q = waiters, s; q != null; q = s) {
                s = q.next;
                if (q.thread != null)
                    pred = q;
                else if (pred != null) {
                    pred.next = s;
                    if (pred.thread == null) // check for race
                        continue retry;
                }
                else if (!WAITERS.compareAndSet(this, q, s))
                    continue retry;
            }
            break;
        }
    }
}
```
移除指定节点，该方法仅在 **awaitDone** 方法内 **等待执行结果超时** 和 **遇到线程中断** 时调用。

## 五、总结
至此 **FutureTask** 体系相关的逻辑已经分析完毕。直接使用就只关心三块内容即可：
1. Callable实现想要做的业务逻辑，
2. 构建FutureTask类。
3. 使用 Thread或ExecutorService来执行，并在执行后阻塞获取执行结果。

**Callable**也可直接执行，但只能通过 **ExecutorService.submit** 方法来执行，但内部实际上还是转换为FutureTask来执行，FutureTask则既可以 **ExecutorService.submit** 来执行，也可以直接使用 **Thread** 来直接执行，因为它既实现 **Runnable** 又实现了 **Future** 。

**FutureTask** 内部则关系主要是 **runner,waiters和state** 这三个属性的定义概念和执行逻辑理清晰差不多也就把**FutureTask** 理解透彻了。

至此 **future体系** 算是分析完毕了。



参考：
https://juejin.cn/post/6844903774985650183
https://segmentfault.com/a/1190000015739343




[ThreadPoolExecutor类结构模型]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/java/多线程/ThreadPoolExecutor类结构模型.png

[FutureTask类结构模型]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/java/多线程/FutureTask类结构模型.png

[Future-waiters模拟]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/java/多线程/Future-waiters模拟.png

[Thread-JVM运行机制]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/java/多线程/Thread-JVM运行机制.png













