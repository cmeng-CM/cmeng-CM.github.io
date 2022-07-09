---
title: rust基础信息
date: 2020-08-17 16:13:12
tags: rust
categories: rust
mathjax: true
---


### 一、rust基础信息
1. **在 Linux 或 macOS 上安装 rustup**
```rust
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```
此命令下载一个脚本并开始安装 rustup 工具，这会安装最新稳定版 Rust。过程中可能会提示你输入密码。如果安装成功，将会出现如下内容：
```
Rust is installed now. Great!
```    

2. **rust版本**
```rust
rustc --version
```

### 二、cargo基础信息
1. **cargo版本**
```rust
cargo --version
```

2. **使用 Cargo 创建项目**
```rust
cargo new hello_cargo
cd hello_cargo
```

3. **编译运行**
    * 编译
    ```rust
    cargo build
        Compiling world_hello v0.1.0 (/Users/workerspace/rust/world_hello)
        Finished dev [unoptimized + debuginfo] target(s) in 1.72s
    ```
    * 编译运行
    ```rust
    cargo run
        Finished dev [unoptimized + debuginfo] target(s) in 0.00s
        Running `target/debug/world_hello`
        Hello, world!
    ```
    * 检查，check，该命令会快速很多，因为它不会生成相关的可执行文件
    ```rust
    cargo check
        Checking world_hello v0.1.0 (/Users/workerspace/rust/world_hello)
        Finished dev [unoptimized + debuginfo] target(s) in 0.14s
    ```
4. **发布（release）构建**
当项目最终准备好发布时，可以使用 cargo build --release 来优化编译项目。这会在 target/release 而不是 target/debug 下生成可执行文件。这些优化可以让 Rust 代码运行的更快，不过启用这些优化也需要消耗更长的编译时间。这也就是为什么会有两种不同的配置：一种是为了开发，你需要经常快速重新构建；另一种是为用户构建最终程序，它们不会经常重新构建，并且希望程序运行得越快越好。如果你在测试代码的运行时间，请确保运行 cargo build --release 并使用 target/release 下的可执行文件进行测试。

### 三、基础概念
####  3.1、变量与可变性
```rust
fn main(){
    // 定义不可变变量
    let x = 1;  //不可变量
    x = 1;  //会报错：cannot assign twice to immutable variable

    //定义可变变量
    let mut y = 2;
    y = 3;  //允许

    //常量
    const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;
}
```

#### 3.2、数据类型
1. **标量类型**
整型、浮点型、布尔类型和字符类型。    

    长度 | 有符号 | 无符号
    :-|:-|:-|
    8-bit	|i8	     |u8
    16-bit	|i16	 |u16
    32-bit	|i32	 |u32
    64-bit	|i64	 |u64
    128-bit	|i128	 |u128
    arch	|isize	 |usize

2. **元组类型**
元组是一个将多个其他类型的值组合进一个复合类型的主要方式。元组长度固定：一旦声明，其长度不会增大或缩小。
```rust
let x: (i32, f64, u8) = (500, 6.4, 1); //定义
let five_hundred = x.0; //取值

let tup = (500, 6.4, 1);    //绑定
let (x, y, z) = tup;        //解构
println!("The value of y is: {}", y);   //取值应用
```

3. **数组类型**
包含多个相同类型数值的方式就是数组，且长度固定。
```rust
//定义
let a = [1, 2, 3, 4, 5];
let a: [i32; 5] = [1, 2, 3, 4, 5];
let a = [3; 5]; //等价于 let a = [3,3,3,3,3];

let first = a[0];   //取值，下标以0为起始。
```

#### 3.3、函数定义 
1. 基础规则  
    * 关键字：fn
    * 参数必须指定类型
    * 函数名命名规则：snake case
    * 函数具备返回值时，不对返回值指定命名，但要指定类型
示例：
```rust
//无参、无返回
fn another_function() {
    println!("Another function.");
}

//有参、无返回
fn another_function(x: i32) {
    println!("The value of x is: {}", x);
}

//无参、有返回
fn five() -> i32 {
    5
}

//有参、有返回
fn five(x: i32) -> i32 {
    x+5
}
```

2. 语句和表达式的区别
函数体由一系列的语句和一个可选的结尾表达式构成。    
* **语句（Statements）**：是执行一些操作但不返回值的指令。
* **表达式（Expressions）**：计算并产生一个值。
* 区别:
    * 语句由 **;** 结尾，表达式无 **;** 结尾
    * 语句代表执行某些逻辑，但不返回值，表达式则即有逻辑也返回具体值。
    * 函数可以使用 return 关键字和指定值，从函数中提前返回；但大部分函数隐式的返回最后的表达式。

示例：
```rust
//返回为：5
fn plus_one() -> i32 {
    5
}

//返回：（x+1）
fn plus_one(x: i32) -> i32 {
    x + 1
}

//无返回，会报错
fn plus_one(x: i32) -> i32 {
    x + 1;
}

let y = {
    let x = 3;
    x + 1
};
//其中下面代码块代表数值：4，因（x+1）无分号
{
    let x = 3;
    x + 1
}
```

#### 3.4、控制流
* if
* loop
* while
* for
````rust
fn main() {
    
    //if
    let number = 3;
    if number > 5 {
        println!("number greater than 5");
    } else if number > 3 {
        println!("number greater than 3");
    }else {
        println!("number less than or equal to 3");
    }

    let condition = true;
    let number = if condition { 5 } else { 6 };

    //loop
    loop {
        println!("again!");
    }

    let mut remaining = 10;
    loop {
        println!("remaining = {}", remaining);
        if remaining == 9 {
            break;
        }
        if count == 2 {
            break 'counting_up;
        }
        remaining -= 1;
    }

    let mut counter = 0;
    let result = loop {
        counter += 1;
        if counter == 10 {
            break counter * 2;
        }
    };

    //while
    while index < 5 {
        println!("the value is: {}", a[index]);
        index += 1;
    }

    //for
    let a = [10, 20, 30, 40, 50];
    for element in a {
        println!("the value is: {}", element);
    }
}
````

### 四、所有权
所有权（系统）是 Rust 最为与众不同的特性，对语言的其他部分有着深刻含义。它让 Rust 无需垃圾回收（garbage collector）即可保障内存安全，因此理解 Rust 中所有权如何工作是十分重要的。本章，我们将讲到所有权以及相关功能：借用（borrowing）、slice 以及 Rust 如何在内存中布局数据。

#### 4.1、基础规则
1. **赋值相关操作**
* Rust 中的每一个值都有一个被称为其 所有者（owner）的变量。  
* 值在任一时刻有且只有一个所有者。
* 当所有者（变量）离开作用域，这个值将被丢弃。
示例：
```rust
fn main(){
    let x = 5; //x有效
    y = x;  //x y均有效

    let s1 = String::from("hello"); //s1有效
    let s2 = s1;            //s1无效，s2有效，此种赋值称为移动（move）

}
```

2. **克隆**
如果我们 确实 需要深度复制 String 中堆上的数据，而不仅仅是栈上的数据，可以使用一个叫做 clone 的通用函数。
```rust
fn main() {
    let s1 = String::from("hello");
    let s2 = s1.clone();

    println!("s1 = {}, s2 = {}", s1, s2);   //s1,s2都有效
}
```

但针对存储在栈上的数据，因其大小都是固定的，所有拷贝是速度最快，所有才会有x赋值给y后，x依旧有效 。Rust 有一个叫做 **Copy trait** 的特殊注解，可以用在类似整型这样的存储在栈上的类型上（。如果一个类型实现了 **Copy trait**，那么一个旧的变量在将其赋值给其他变量后仍然可用。Rust 不允许自身或其任何部分实现了 **Drop trait** 的类型使用 **Copy trait**。


一般情况下任何一组简单标量值的组合都可以实现 Copy，任何不需要分配内存或某种形式资源的类型都可以实现 Copy。如下是一些 Copy 的类型：     
* 所有整数类型，比如 u32。
* 布尔类型，bool，它的值是 true 和 false。
* 所有浮点数类型，比如 f64。
* 字符类型，char。
* 元组，当且仅当其包含的类型也都实现 Copy 的时候。比如，(i32, i32) 实现了 Copy，但 (i32, String) 就没有。

3. ***所有权与函数*
```rust
fn main() {
    let s1 = gives_ownership();         // gives_ownership 将返回值
                                        // 转移给 s1

    let s2 = String::from("hello");     // s2 进入作用域

    let s3 = takes_and_gives_back(s2);  // s2 被移动到
                                        // takes_and_gives_back 中,
                                        // 它也将返回值移给 s3
} // 这里, s3 移出作用域并被丢弃。s2 也移出作用域，但已被移走，
  // 所以什么也不会发生。s1 离开作用域并被丢弃

fn gives_ownership() -> String {             // gives_ownership 会将
                                             // 返回值移动给
                                             // 调用它的函数

    let some_string = String::from("yours"); // some_string 进入作用域.

    some_string                              // 返回 some_string 
                                             // 并移出给调用的函数
                                             // 
}

// takes_and_gives_back 将传入字符串并返回该值
fn takes_and_gives_back(a_string: String) -> String { // a_string 进入作用域
                                                      // 

    a_string  // 返回 a_string 并移出给调用的函数
}

```

#### 4.2、引用与借用
1. **不可变引用**  
当参数被传递给函数后，我们依旧需要使用它，如果单纯的使用函数返回的模式，就很形式主义了，所以我们需要一种方式，来保证将参数传递给函数我们依旧可以对其进行操作，这就是**引用**。**引用**（reference）像一个指针，因为它是一个地址，我们可以由此访问储存于该地址的属于其他变量的数据。与指针不同，引用确保指向某个特定类型的有效值。   

**规则：**
* 引用后变量并不具备该参数的所有权，所以当引用停止使用时，它所指向的值也不会被丢弃。
* 我们将创建一个引用的行为称为 借用（borrowing）。正如现实生活中，如果一个人拥有某样东西，你可以从他那里借来。当你使用完毕，必须还回去。我们并不拥有它。
* 对引用变量进行修改会报错，（默认）不允许修改引用的值。

```rust
fn main() {
    let s1 = String::from("hello");

    let len = calculate_length(&s1);

    println!("The length of '{}' is {}.", s1, len);
}

fn main() {
    let s1 = String::from("hello");

    let len = calculate_length(&s1);

    println!("The length of '{}' is {}.", s1, len);
}

fn calculate_length(s: &String) -> usize { // s is a reference to a String
    s.len()
} // 这里，s 离开了作用域。但因为它并不拥有引用值的所有权，
  // 所以什么也不会发生
```

2. 可变引用
针对不可变引用增加 <font color="red" size="5"><b>mut</b></font> 关键词即可变为可变引用。
```rust
fn main() {
    let mut s = String::from("hello");

    change(&mut s);
}

fn change(some_string: &mut String) {
    some_string.push_str(", world");
}
```
**可变引用和不可变引用的使用规则：**
* 在任意给定时间，要么 只能有一个可变引用，要么 只能有多个不可变引用。
* 引用必须总是有效的。

```rust
fn main() {
    let mut s = String::from("hello");
    {
        let r1 = &mut s;
    } // r1 在这里离开了作用域，所以我们完全可以创建一个新的引用

    let r2 = &mut s;
}

fn main() {
    let mut s = String::from("hello");

    let r1 = &s; // 没问题
    let r2 = &s; // 没问题
    let r3 = &mut s; // 大问题

    println!("{}, {}, and {}", r1, r2, r3);
}

```

#### 4.3、Slice 类型
**slice:** 允许你引用集合中一段连续的元素序列，而不用引用整个集合。slice 是一类引用，所以它没有所有权。
```rust
fn main() {
    //字符串类型
    let s = String::from("hello world");
    let hello = &s[0..5];
    let world = &s[6..11];

    //数组
    let a = [1, 2, 3, 4, 5];
    let slice = &a[1..3];
}
```

### 五、结构体
#### 5.1、实例化
1. 概念
结构体类型面向对象语言中的类的概念，一样含有自身的属性字段等信息。
```rust
struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}

//创建
fn main() {
    let user1 = User {
        email: String::from("someone@example.com"),
        username: String::from("someusername123"),
        active: true,
        sign_in_count: 1,
    };
}
fn build_user(email: String, username: String) -> User {
    User {
        email: email,
        username: username,
        active: true,
        sign_in_count: 1,
    }
}

fn build_user(email: String, username: String) -> User {
    User {
        email,
        username,
        active: true,
        sign_in_count: 1,
    }
}
fn main() {
    // --snip--

    let user2 = User {
        active: user1.active,
        username: user1.username,
        email: String::from("another@example.com"),
        sign_in_count: user1.sign_in_count,
    };
}
```
2. 所有权
我们使用了自身拥有所有权的 String 类型而不是 &str 字符串 slice 类型。这是一个有意而为之的选择，因为我们想要这个结构体拥有它所有的数据，为此只要整个结构体是有效的话其数据也是有效的。
可以使结构体存储被其他对象拥有的数据的引用，不过这么做的话需要用上 生命周期（lifetimes）。

```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

fn main() {
    let scale = 2;
    let rect1 = Rectangle {
        width: dbg!(30 * scale),
        height: 50,
    };

    dbg!(&rect1);/* 输出：&rect1 = Rectangle {
                                width: 60,
                                height: 50,
                            } */

    println!("rect1 is {:?}", rect1);//输出：rect1 is Rectangle { width: 30, height: 50 }
    //{:#?}：也可用此表达书进行输出格式化
}

```
**#[derive(Debug)]：**配和 **{:?}** 方便输出调试
**dbg!：** 放在表达式 30 * scale 周围，因为 dbg! 返回表达式的值的所有权。

#### 5.2、方法语法
* 方法（method）：与函数类似，它们使用 fn 关键字和名称声明，可以拥有参数和返回值，同时包含在某处调用该方法时会执行的代码。不过方法与函数是不同的，因为它们在结构体的上下文中被定义（，并且它们第一个参数总是 self，它代表调用该方法的结构体实例。
* impl：是 implementation 的缩写），这个 impl 块中的所有内容都将与**所实现的结构体**类型相关联。
* 每个结构体都允许拥有多个 impl 块。
* 关联函数：所有在 impl 块中定义的函数被称为 **关联函数（associated functions）**，因为它们与 **impl** 后面命名的类型相关。我们可以定义不以 self 为第一参数的关联函数（因此不是方法），因为它们并不作用于一个结构体的实例。如：代码示例中的《square》.
* 非结构体方法类关联函数使用 **结构体名** 和 **::** 语法来调用这个关联函数
```rust
#[derive(Debug)]
struct Rectangle {
    width: u32,
    height: u32,
}

impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }
}

impl Rectangle {
    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}

impl Rectangle {
    fn square(size: u32) -> Rectangle {
        Rectangle {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    let rect2 = Rectangle {
        width: 10,
        height: 40,
    };
    let rect3 = Rectangle {
        width: 60,
        height: 45,
    };

    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));
}
```

### 六、枚举和模式匹配
#### 6.1、枚举
1. **枚举**：枚举是一个不同于结构体的定义自定义数据类型的方式。
```rust
// 简单型枚举
enum IpAddrKind {
    V4,
    V6,
}

fn main() {
    let four = IpAddrKind::V4;
    let six = IpAddrKind::V6;

    route(IpAddrKind::V4);
    route(IpAddrKind::V6);
}

fn route(ip_kind: IpAddrKind) {}

// 标量类型为内容的枚举
fn main() {
    enum IpAddr {
        V4(u8, u8, u8, u8),
        V6(String),
    }

    let home = IpAddr::V4(127, 0, 0, 1);

    let loopback = IpAddr::V6(String::from("::1"));
}
// 结构体为内容的枚举
#![allow(unused)]
fn main() {
    struct Ipv4Addr {
        // --snip--
    }

    struct Ipv6Addr {
        // --snip--
    }

    enum IpAddr {
        V4(Ipv4Addr),
        V6(Ipv6Addr),
    }
}
```
2. **Option**：Option 是标准库定义的另一个枚举。Option 类型应用广泛因为它编码了一个非常普遍的场景，即一个值要么有值要么没值。在[标准库](https://doc.rust-lang.org/std/option/enum.Option.html)中的源码：
```rust
#![allow(unused)]
fn main() {
enum Option<T> {
    None,
    Some(T),
}
}

```

#### 6.2：match 控制流运算符
Rust 有一个叫做 match 的极为强大的控制流运算符，它允许我们将一个值与一系列的模式相比较，并根据相匹配的模式执行相应代码。类似Java中的**switch-case**。
```rust
enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
    Other,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => 1,
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => {
            // 逻辑处理，此代码块，即{}之内的内容为表达式，而表达式的结果值将作为整个 match 表达式的返回值。
            println!("Coin is Quarter!");
            1
        }
        // other:Other,    //此处为通配符，满足match为有穷尽的匹配规则。
        // _ => (),     //  "_"，这是一个特殊的模式，可以匹配任意值而不绑定到该值。

    }
}
```
#### 6.3、if let 简单控制流
**if let** 语法让我们以一种不那么冗长的方式结合 **if** 和 **let**，来处理只匹配一个模式的值而忽略其他模式的情况。换句话说，可以认为 **if let** 是 **match** 的一个语法糖，它当值匹配某一模式时执行代码而忽略所有其他值。
```rust
#[derive(Debug)]
enum UsState {
    Alabama,
    Alaska,
    // --snip--
}

enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter(UsState),
}

fn main() {
    // let mut count = 0;
    // match coin {
    //     Coin::Quarter(state) => println!("State quarter from {:?}!", state),
    //     _ => count += 1,
    // }

    // if let 模式
    let coin = Coin::Penny;
    let mut count = 0;
    if let Coin::Quarter(state) = coin {
        println!("State quarter from {:?}!", state);
    } else {
        count += 1;
    }
}

```

### 七、package/crate/module
1. **crate**
**crate**：是一个二进制项或者库。crate root 是一个源文件，Rust 编译器以它为起始点，并构成你的 crate 的根模块。

**create类型：**
rust里有两种crate，lib类型和bin类型，并且默认以文件名为标准按以下规则处理crate：
* src/main.rs：表示该crate是一个bin类型的crate
* src/lib.rs：表示该crate是一个lib类型的crate
src/main.rs和src/lib.rs都是crate的根，也就是crate引用、rustc编译的入口。

2. **包（package）** 
**包（package）**：是提供一系列功能的一个或者多个 crate。cargo new 命令会创建一个新项目，也是一个package，里面有一个Cargo.toml文件，用于定义package、所需外部依赖，以及如何编译crate等。

**包的规则：**
    * 包中可以包含至多一个库 crate(library crate)。
    * 包中可以包含任意多个二进制 crate(binary crate),但是必须至少包含一个 crate.     

此外，一个package中的crate还有如下约束：
* 多个bin类型的crate
* 0个或1个lib类型的crate
其中，1和2并不互斥，也就是说一个项目下可以有1个lib和多个bin类型的crate，即一个package还以编译出多个可执行文件。

只是如果有多个bin类型的crate，一个src/main.rs就不行了，就得放到 src/bin 下面，每个crate一个文件，换句话说，每个文件都是一个不同的crate。

3. **模块**
**模块**：让我们可以将一个 crate 中的代码进行分组，以提高可读性与重用性。模块还可以控制项的 私有性，即项是可以被外部代码使用的（public），还是作为一个内部实现的内容，不能被外部代码使用（private）。
```rust
mod front_of_house {
    mod hosting {
        fn add_to_waitlist() {}

        fn seat_at_table() {}
    }

    mod serving {
        fn take_order() {}

        fn serve_order() {}

        fn take_payment() {}
    }
}
```
我们定义一个模块，是以 mod 关键字为起始，然后指定模块的名字（本例中叫做 front_of_house），并且用花括号包围模块的主体。在模块内，我们还可以定义其他的模块，就像本例中的 hosting 和 serving 模块。模块还可以保存一些定义的其他项，比如结构体、枚举、常量、特性、或者函数。

4. **路径及引用**   
**use**：在crate和模块了可能定义了函数、结构体等，要想在其他模块或crate使用，需要将其引入到当前scope中，类似java的import的功能，rust里需要使用use。  

**路径**：rust中use引用的路径分为两种：
* 绝对路径（absolute path）从 crate 根开始，以 crate 名或者字面值 crate 开头。
* 相对路径（relative path）从当前模块开始，以 self、super 或当前模块的标识符开头。

```rust
mod front_of_house {
    pub mod hosting {
        pub fn add_to_waitlist() {}
    }
}

pub fn eat_at_restaurant() {
    // 绝对路径
    crate::front_of_house::hosting::add_to_waitlist();

    // 相对路径
    front_of_house::hosting::add_to_waitlist();
}

// 引用相关操作
use std::io;
use std::cmp::Ordering;
// 以上两行引用等价于：use std::{cmp::Ordering, io};

use std::io;
use std::io::Write;
// 等价于：use std::io::{self, Write};

// 通配符
use std::collections::*;

```

**pub修饰符**
结构体和枚举:要想访问其他mod里的结构体，需要将结构体声明为pub，但是这也只能访问到结构体而已，如果要想操作里面的字段，可以有两种方式：
* 提供pub的方法修改字段
* 将需要操作的字段直接修改为pub类型  
* 在父模块中不能使用子模块中的private项目
* 子模块可以使用父模块中的所有item

可能前者更“面向对象”一些。
而枚举类型的话只需要在枚举名前面加上pub即可，不需要对其中的variant进行设置。

**re-exporting 再导出**
当使用use关键字将外部item导入到当前scope之后，这个item在当前scope是private的，如果使用 pub use 的话，还能让使用当前mod的第三者，使用在该mod中引入的item。

5. **workspace**
workspace用于管理多个相关的package，不同的package有各自的Cargo.toml，但是整个workspace共享一个Cargo.lock，也只有一个target目录（编译输出）。

虽然workspace内的项目共享一个Cargo.lock，但是他们之间默认不互相依赖，需要显示添加它们之间的依赖关系。而且在一个项目中添加的依赖，在其他项目中如果想使用，还需要再次声明依赖才行。

### 八、错误处理
Rust 将错误分为两大类：
* **可恢复的（recoverable）**：比如文件未找到的错误，我们很可能只想向用户报告问题并重试操作。此种错误使用 **Result<T, E>** 类型来处理问题。
* **不可恢复的（unrecoverable）**：对于一个可恢复的错误，不可恢复的错误总是 bug 出现的征兆，比如试图访问一个超过数组末端的位置，因此我们要立即停止程序。此种错误由 **panic! 宏** 来处理。

#### 8.1、panic! 与不可恢复的错误
**panic** ：处理的两种机制：
* **展开（unwinding）**：这意味着 Rust 会回溯栈并清理它遇到的每一个函数的数据，不过这个回溯并清理的过程有很多工作。
* **终止（abort）**：这会不清理数据就退出程序。
切换方式：Cargo.toml 的 [profile] 部分增加 panic = 'abort'，可以由展开切换为终止。

#### 8.2、Result 与可恢复的错误
1. **Result枚举**，它定义有如下两个成员，Ok 和 Err：
```rust
#![allow(unused)]
fn main() {
    enum Result<T, E> {
        Ok(T),
        Err(E),
    }
}

// 应用示例
use std::fs::File;
use std::io::ErrorKind;

fn main() {
    let f = File::open("hello.txt");

    let f = match f {
        Ok(file) => file,
        Err(error) => match error.kind() {
            ErrorKind::NotFound => match File::create("hello.txt") {
                Ok(fc) => fc,
                Err(e) => panic!("Problem creating the file: {:?}", e),
            },
            other_error => {
                panic!("Problem opening the file: {:?}", other_error)
            }
        },
    };
}
```
2. 失败时 panic 的简写：**unwrap** 和 **expect**
```rust
use std::fs::File;

fn main() {
    let f = File::open("hello.txt").unwrap();
    let f = File::open("hello.txt").expect("Failed to open hello.txt");
}
```
3. 传播错误
**传播（propagating）错误**：当编写一个其实先会调用一些可能会失败的操作的函数时，除了在这个函数中处理错误外，还可以选择让调用者知道这个错误并决定该如何处理。
```rust
use std::fs::File;
use std::io::{self, Read};

#![allow(unused)]
fn main() {

    fn read_username_from_file() -> Result<String, io::Error> {
        let f = File::open("hello.txt");

        let mut f = match f {
            Ok(file) => file,
            Err(e) => return Err(e),
        };

        let mut s = String::new();

        match f.read_to_string(&mut s) {
            Ok(_) => Ok(s),
            Err(e) => Err(e),
        }
    }
}

// 传播错误的简写：? 运算符
fn read_username_from_file() -> Result<String, io::Error> {
    let mut f = File::open("hello.txt")?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
```

### 九、泛型、trait 与生命周期
#### 9.1、泛型
我们可以使用泛型为像函数签名或结构体这样的项创建定义，这样它们就可以用于多种不同的具体数据类型。
```rust
struct Point<X1, Y1> {
    x: X1,
    y: Y1,
}

impl<X1, Y1> Point<X1, Y1> {
    fn mixup<X2, Y2>(self, other: Point<X2, Y2>) -> Point<X1, Y2> {
        Point {
            x: self.x,
            y: other.y,
        }
    }
}

fn main() {
    let p1 = Point { x: 5, y: 10.4 };
    let p2 = Point { x: "Hello", y: 'c' };

    let p3 = p1.mixup(p2);

    println!("p3.x = {}, p3.y = {}", p3.x, p3.y);
}
```

#### 9.2、trait：定义共享的行为
**trait** 告诉 Rust 编译器某个特定类型拥有可能与其他类型共享的功能。可以通过 trait 以一种抽象的方式定义共享的行为。可以使用 trait bounds 指定泛型是任何拥有特定行为的类型。
**<font color='red'>注意</font>**：trait 类似于其他语言中的常被称为 接口（interfaces）的功能，虽然有一些不同。  

1. **trait** 的定义和实现
* **trait 定义**：是一种将方法签名组合起来的方法，目的是定义一个实现某些目的所必需的行为的集合。trait体中可以有多个方法：一行一个方法签名且都以分号结尾。
```rust
pub trait Summary {
    fn summarize(&self) -> String;
}
```
* **trait 实现**：在类型上实现 trait 类似于实现与 trait 无关的方法。区别在于 impl 关键字之后，我们提供需要实现 trait 的名称，接着是 for 和需要实现 trait 的类型的名称。
```rust
pub trait Summary {
    fn summarize(&self) -> String;
}

// 默认实现
// pub trait Summary {
//     fn summarize(&self) -> String {
//         String::from("(Read more...)")
//     }
// }

pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}


pub struct NewsArticle {
    pub headline: String,
    pub location: String,
    pub author: String,
    pub content: String,
}

impl Summary for NewsArticle {
    fn summarize(&self) -> String {
        format!("{}, by {} ({})", self.headline, self.author, self.location)
    }
}

pub struct Tweet {
    pub username: String,
    pub content: String,
    pub reply: bool,
    pub retweet: bool,
}

impl Summary for Tweet {
    fn summarize(&self) -> String {
        format!("{}: {}", self.username, self.content)
    }
}

```

2. **trait** 作为参数
```rust
pub fn notify(item: &impl Summary) {
    println!("Breaking news! {}", item.summarize());
}

// Trait Bound 语法
pub fn notify<T: Summary>(item: &T) {
    println!("Breaking news! {}", item.summarize());
}

// 通过 + 指定多个 trait bound
pub fn notify(item: &(impl Summary + Display)) {}
pub fn notify<T: Summary + Display>(item: &T) {}

// 通过 where 简化 trait bound
fn some_function<T: Display + Clone, U: Clone + Debug>(t: &T, u: &U) -> i32 {}

fn some_function<T, U>(t: &T, u: &U) -> i32
    where T: Display + Clone,
          U: Clone + Debug{}
```

#### 9.3、生命周期与引用有效性
**生命周期（lifetime）**：也就是引用保持有效的作用域。

1. **悬垂引用**：
```rust
fn main() {
    {
        let r;
        {
            let x = 5;
            r = &x;
        }
        println!("r: {}", r);
    }
}

// 生命周期展示
fn main() {
    {
        let r;                // ---------+-- 'a
        {                     //          |
            let x = 5;        // -+-- 'b  |
            r = &x;           //  |       |
        }                     // -+       |
        println!("r: {}", r); //          |
    }                         // ---------+
}

```
外部作用域声明了一个没有初值的变量 r，而内部作用域声明了一个初值为 5 的变量x。在内部作用域中，我们尝试将 r 的值设置为一个 x 的引用。接着在内部作用域结束后，尝试打印出 r 的值。这段代码不能编译因为 r 引用的值在尝试使用之前就离开了作用域。

2. **生命周期注解语法**
**生命周期注解**：一个不太常见的语法：生命周期参数名称必须以撇号（**'**）开头，其名称通常全是小写，类似于泛型其名称非常短。**'a** 是大多数人默认使用的名称。生命周期参数注解位于引用的 & 之后，并有一个**空格**来将引用类型与生命周期注解分隔开。
```rust
&i32        // 引用
&'a i32     // 带有显式生命周期的引用
&'a mut i32 // 带有显式生命周期的可变引用

// 函数中的使用
fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";

    let result = longest(string1.as_str(), string2);
    println!("The longest string is {}", result);
}

// 现在函数签名表明对于某些生命周期 'a，函数会获取两个参数，他们都是与生命周期 'a 存在的一样长的字符串 slice。
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() {
        x
    } else {
        y
    }
}
```

3. **生命周期省略（Lifetime Elision）**
* **生命周期省略（Lifetime Elision）**：针对一些可预测的并且遵循几个明确的模式的场景，Rust 团队就把这些模式编码进了 Rust 编译器中，如此借用检查器在这些情况下就能推断出生命周期而不再强制程序员显式的增加注解。
* **输入生命周期（input lifetimes）**：函数或方法的参数的生命周期。
* **输出生命周期（output lifetimes）**：返回值的生命周期。
* **生命周期省略规则（lifetime elision rules）**：即编码进 Rust 引用分析的模式。这并不是需要程序员遵守的规则；这些规则是一系列特定的场景，此时编译器会考虑，如果代码符合这些场景，就无需明确指定生命周期。省略规则适用于 fn 定义，以及 impl 块。
    * 规则一：每一个是引用的参数都有它自己的生命周期参数。换句话说就是，有一个引用参数的函数有一个生命周期参数：fn foo<'a>(x: &'a i32)，有两个引用参数的函数有两个不同的生命周期参数，fn foo<'a, 'b>(x: &'a i32, y: &'b i32)，依此类推。
    * 规则二：如果只有一个输入生命周期参数，那么它被赋予所有输出生命周期参数：fn foo<'a>(x: &'a i32) -> &'a i32。
    * 规则三：如果方法有多个输入生命周期参数并且其中一个参数是 &self 或 &mut self，说明是个对象的方法(method), 那么所有输出生命周期参数被赋予 self 的生命周期。

4. **静态生命周期**
这里有一种特殊的生命周期值得讨论：**'static**，其生命周期能够存活于整个程序期间。所有的字符串字面值都拥有 'static 生命周期，我们也可以选择像下面这样标注出来：
```rust
#![allow(unused)]
fn main() {
let s: &'static str = "I have a static lifetime.";
}
```

5. 结合泛型类型参数、trait bounds 和生命周期
```rust
fn main() {
    let string1 = String::from("abcd");
    let string2 = "xyz";

    let result = longest_with_an_announcement(
        string1.as_str(),
        string2,
        "Today is someone's birthday!",
    );
    println!("The longest string is {}", result);
}

use std::fmt::Display;

fn longest_with_an_announcement<'a, T>(
    x: &'a str,
    y: &'a str,
    ann: T,
) -> &'a str
where
    T: Display,
{
    println!("Announcement! {}", ann);
    if x.len() > y.len() {
        x
    } else {
        y
    }
}

```

### 十、Rust 中的函数式语言功能
Rust 的设计灵感来源于很多现存的语言和技术。其中一个显著的影响就是 **函数式编程（functional programming）**。函数式编程风格通常包含将函数作为参数值或其他函数的返回值、将函数赋值给变量以供之后执行等等。
* **闭包（Closures）**：一个可以储存在变量里的类似函数的结构。
* **迭代器（Iterators）**：一种处理元素序列的方式。

#### 10.1、闭包（Closures）
Rust 的 闭包（closures）是可以保存进变量或作为参数传递给其他函数的匿名函数。可以在一个地方创建闭包，然后在不同的上下文中执行闭包运算。不同于函数，闭包允许捕获调用者作用域中的值。

1. 闭包的定义
```rust
// 示例
fn main() {
    let expensive_closure = |num| {
        println!("calculating slowly...");
        thread::sleep(Duration::from_secs(2));
        num
    };
}
// 类比函数和闭包的可允许规则
fn  add_one_v1   (x: u32) -> u32 { x + 1 }
let add_one_v2 = |x: u32| -> u32 { x + 1 };
let add_one_v3 = |x|             { x + 1 };
let add_one_v4 = |x|               x + 1  ;

```
**规则**：闭包定义是 expensive_closure 赋值的 **=** 之后的部分。闭包的定义以一对竖线（**|**）开始，在竖线中指定闭包的参数；之所以选择这个语法是因为它与 Smalltalk 和 Ruby 的闭包定义类似。这个闭包有一个参数 num；如果有多于一个参数，可以使用逗号分隔，比如 **|param1, param2|**。

2. 闭包会捕获其环境
闭包还有另一个函数所没有的功能：他们可以捕获其环境并访问其被定义的作用域的变量。
```rust
// 这里，即便 x 并不是 equal_to_x 的一个参数，equal_to_x 闭包也被允许使用变量 x，因为它与 equal_to_x 定义于相同的作用域。
fn main() {
    let x = 4;
    let equal_to_x = |z| z == x;
    let y = 4;
    assert!(equal_to_x(y));
}

// 编译报错，编译器甚至会提示我们这只能用于闭包！
fn main() {
    let x = 4;
    fn equal_to_x(z: i32) -> bool {
        z == x
    }
    let y = 4;
    assert!(equal_to_x(y));
}
```
当闭包从环境中捕获一个值，闭包会在闭包体中储存这个值以供使用。这会使用内存并产生额外的开销，在更一般的场景中，当我们不需要闭包来捕获环境时，我们不希望产生这些开销。因为函数从未允许捕获环境，定义和使用函数也就从不会有这些额外开销。

闭包可以通过三种方式捕获其环境，他们直接对应函数的三种获取参数的方式：**获取所有权**，**可变借用**和**不可变借用**。这三种捕获值的方式被编码为如下三个 Fn trait：
* **FnOnce**： 消费从周围作用域捕获的变量，闭包周围的作用域被称为其 **环境（environment）**。为了消费捕获到的变量，闭包必须获取其所有权并在定义闭包时将其移动进闭包。其名称的 **Once** 部分代表了闭包不能多次获取相同变量的所有权的事实，所以它只能被调用一次。
* **FnMut**： 获取可变的借用值所以可以改变其环境。
* **Fn**： 从其环境获取不可变的借用值。

#### 10.2、迭代器
**迭代器模式**：允许你对一个序列的项进行某些处理。**迭代器（iterator）** 负责遍历序列中的每一项和决定序列何时结束的逻辑。当使用迭代器时，我们无需重新实现这些逻辑。在 Rust 中，迭代器是 惰性的（lazy），这意味着在调用方法使用迭代器之前它都不会有效果。

### 十一、智能指针
**指针 （pointer）**：是一个包含内存地址的变量的通用概念。
**智能指针（smart pointers）**：是一类数据结构，他们的表现类似指针，但是也拥有额外的元数据和功能。
在 Rust 中，普通引用和智能指针的一个额外的区别是引用是一类只借用数据的指针；相反，在大部分情况下，智能指针 **拥有** 他们指向的数据。如 **String** 和 **Vec<T>** 。

#### 10.1、Deref trait
1. **通过解引用运算符追踪指针的值**
实现 **Deref trait** 允许我们重载 **解引用运算符（dereference operator）***（与乘法运算符或通配符相区别）。通过这种方式实现 Deref trait 的智能指针可以被当作常规引用来对待，可以编写操作引用的代码并用于智能指针。
```rust
fn main() {
    let x = 5;
    let y = &x;

    assert_eq!(5, x);
    assert_eq!(5, *y); //编译通过
    assert_eq!(5, y); //编译异常  
    // assert_eq!(5, y);
    // ^^^^^^^^^^^^^^^^ no implementation for `{integer} == &{integer}`
     
}
```

2. **通过实现 Deref trait 将某类型像引用一样处理**
为了实现 trait，需要提供 trait 所需的方法实现。**Deref trait** 由标准库提供，要求实现名为 deref 的方法，其借用 self 并返回一个内部数据的引用。
```rust
use std::ops::Deref;

impl<T> Deref for MyBox<T> {
    // 语法定义了用于此 trait 的关联类型。关联类型是一个稍有不同的定义泛型参数的方式，
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}
```
没有 Deref trait 的话，*只会解引用 & 引用类型。deref 方法向编译器提供了获取任何实现了 Deref trait 的类型的值，并且调用这个类型的 deref 方法来获取一个它知道如何解引用的 & 引用的能力。
```rust
fn main() {
    let x = 5;
    let y = MyBox::new(x);

    assert_eq!(5, x);
    assert_eq!(5, *y); //*y 等价于： *(y.deref())
}
```

3. **函数和方法的隐式 Deref 强制转换**
**Deref 强制转换（deref coercions）：** 是 Rust 在函数或方法传参上的一种便利。Deref 强制转换只能作用于实现了 Deref trait 的类型。
```rust
fn hello(name: &str) {
    println!("Hello, {}!", name);
}

fn main() {
    let m = MyBox::new(String::from("Rust"));
    // 隐式强制转换
    hello(&m);

    // 如果没有隐式强制转换
    // hello(&(*m)[..]);
}
```
**&m** 调用 hello 函数过程：    
* m 为 MyBox<String> 值的引用，在 MyBox<T> 上实现了 Deref trait，Rust 可以通过 deref 调用将 &MyBox<String> 变为 &String。
* 标准库中提供了 String 上的 Deref 实现，其会返回字符串 slice，这可以在 Deref 的 API 文档中看到。Rust 再次调用 deref 将 &String 变为 &str，这就符合 hello 函数的定义了。

#### 10.2、Drop trait清理代码
**Drop trait：** 指定在值离开作用域时应该执行的代码的方式是实现。
**Drop trait：** 要求实现一个叫做 drop 的方法，它获取一个 self 的可变引用。
1. 实现**Drop trait**来清理代码
```rust
struct CustomSmartPointer {
    data: String,
}

impl Drop for CustomSmartPointer {
    fn drop(&mut self) {
        println!("Dropping CustomSmartPointer with data `{}`!", self.data);
    }
}

fn main() {
    let c = CustomSmartPointer {
        data: String::from("my stuff"),
    };
    let d = CustomSmartPointer {
        data: String::from("other stuff"),
    };
    println!("CustomSmartPointers created.");
}
// 运行结果：
// $ cargo run。。。
// CustomSmartPointers created.
// Dropping CustomSmartPointer with data `other stuff`!
// Dropping CustomSmartPointer with data `my stuff`!
```
变量以被创建时相反的顺序被丢弃，所以 d 在 c 之前被丢弃

2. 通过 **std::mem::drop** 提早丢弃值
```rust
fn main() {
    let c = CustomSmartPointer {
        data: String::from("some data"),
    };
    println!("CustomSmartPointer created.");
    drop(c);
    println!("CustomSmartPointer dropped before the end of main.");
}
// 运行结果：
// $ cargo run。。。
// CustomSmartPointer created.
// Dropping CustomSmartPointer with data `some data`!
// CustomSmartPointer dropped before the end of main.
```

#### 10.3、Rc\<T> 引用计数智能指针
**Rc\<T>** ：为 **引用计数（reference counting）** 的缩写。引用计数意味着记录一个值引用的数量来知晓这个值是否仍在被使用。如果某个值有零个引用，就代表没有任何有效引用并可以被清理。
**Rc\<T>**: 允许在程序的多个部分之间只读地共享数据。如果 Rc 也允许多个可变引用，则会违反借用规则之一：相同位置的多个可变借用可能造成数据竞争和不一致。  
<font size=5%>总结其特性：</font>
* 使用 **Rc\<T>** 共享数据
* 克隆 **Rc\<T>** 会增加引用计数
* **Rc\<T>** 只能用于单线程场景。多线程场景需要使用Arc\<T>（原子引用计数（atomically reference counted）类型）。
* 通过 **Rc\<T>** 获取的引用为不可变引用

```rust
enum List {
    Cons(i32, Box<List>),
    Nil,
}

use crate::List::{Cons, Nil};

fn main() {
    let a = Cons(5, Box::new(Cons(10, Box::new(Nil))));
    let b = Cons(3, Box::new(a));
    let c = Cons(4, Box::new(a));
}
// 运行结果
// error[E0382]: use of moved value: `a`
//   --> src/main.rs:11:30
//    |
// 9  |     let a = Cons(5, Box::new(Cons(10, Box::new(Nil))));
//    |         - move occurs because `a` has type `List`, which does not implement the `Copy` trait
// 10 |     let b = Cons(3, Box::new(a));
//    |                              - value moved here
// 11 |     let c = Cons(4, Box::new(a));
//    |                              ^ value used here after move

// For more information about this error, try `rustc --explain E0382`.
// error: could not compile `cons-list` due to previous error
```
Cons 成员拥有其储存的数据，所以当创建 b 列表时，a 被移动进了 b 这样 b 就拥有了 a。接着当再次尝试使用 a 创建 c 时，这不被允许，因为 a 的所有权已经被移动。  
此种情况下，必须实现 **a** 同时被 **b** 和 **c** 引用。则可以使用 Rc<T> 代替 Box<T>。如下：
```rust
enum List {
    Cons(i32, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::rc::Rc;

fn main() {
    let a = Rc::new(Cons(5, Rc::new(Cons(10, Rc::new(Nil)))));
    let b = Cons(3, Rc::clone(&a));
    let c = Cons(4, Rc::clone(&a));
}
```
现在每一个 Cons 变量都包含一个值和一个指向 List 的 Rc<T>。当创建 b 时，不同于获取 a 的所有权，这里会克隆 a 所包含的 Rc<List>，这会将引用计数从 1 增加到 2 并允许 a 和 b 共享 Rc<List> 中数据的所有权。创建 c 时也会克隆 a，这会将引用计数从 2 增加为 3。每次调用 Rc::clone，Rc<List> 中数据的引用计数都会增加，直到有零个引用之前其数据都不会被清理。

#### 10.4、RefCell\<T> 和内部可变性模式
**内部可变性（Interior mutability）** ：是 Rust 中的一个设计模式，它允许你即使在有不可变引用时也可以改变数据，即：**在不可变值内部改变值**。这通常是借用规则所不允许的。该模式在数据结构中使用 unsafe 代码来模糊 Rust 通常的可变性和借用规则。当可以确保代码在运行时会遵守借用规则，即使编译器不能保证的情况，可以选择使用那些运用内部可变性模式的类型。所涉及的 unsafe 代码将被封装进安全的 API 中，而外部类型仍然是不可变的。

1. **RefCell\<T>** 
**RefCell\<T>**：就是内部可变性模式的实现类型之一。与 **Rc\<T>** 不同的事，它具备数据的唯一所有权。  

如下为选择 Box<T>，Rc<T> 或 RefCell<T> 的理由：
* Rc<T> 允许相同数据有多个所有者；Box<T> 和 RefCell<T> 有单一所有者。
* Box<T> 允许在编译时执行不可变或可变借用检查；Rc<T>仅允许在编译时执行不可变借用检查；* * RefCell<T> 允许在运行时执行不可变或可变借用检查。
* 因为 RefCell<T> 允许在运行时执行可变借用检查，所以我们可以在即便 RefCell<T> 自身是不可变的情况下修改其内部的值。

```rust
pub trait Messenger {
    fn send(&self, msg: &str);
}

pub struct LimitTracker<'a, T: Messenger> {
    messenger: &'a T,
    value: usize,
    max: usize,
}

impl<'a, T> LimitTracker<'a, T>
where
    T: Messenger,
{
    pub fn new(messenger: &T, max: usize) -> LimitTracker<T> {
        LimitTracker {
            messenger,
            value: 0,
            max,
        }
    }

    pub fn set_value(&mut self, value: usize) {
        self.value = value;

        let percentage_of_max = self.value as f64 / self.max as f64;

        if percentage_of_max >= 1.0 {
            self.messenger.send("Error: You are over your quota!");
        } else if percentage_of_max >= 0.9 {
            self.messenger
                .send("Urgent warning: You've used up over 90% of your quota!");
        } else if percentage_of_max >= 0.75 {
            self.messenger
                .send("Warning: You've used up over 75% of your quota!");
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::RefCell;

    struct MockMessenger {
        sent_messages: RefCell<Vec<String>>,
    }

    impl MockMessenger {
        fn new() -> MockMessenger {
            MockMessenger {
                sent_messages: RefCell::new(vec![]),
            }
        }
    }

    impl Messenger for MockMessenger {
        fn send(&self, message: &str) {
            self.sent_messages.borrow_mut().push(String::from(message));
        }
    }

    #[test]
    fn it_sends_an_over_75_percent_warning_message() {
        // --snip--
        let mock_messenger = MockMessenger::new();
        let mut limit_tracker = LimitTracker::new(&mock_messenger, 100);

        limit_tracker.set_value(80);

        assert_eq!(mock_messenger.sent_messages.borrow().len(), 1);
    }
}

```
对于 send 方法的实现，第一个参数仍为 self 的不可变借用，这是符合方法定义的。我们调用 self.sent_messages 中 RefCell 的 borrow_mut 方法来获取 RefCell 中值的可变引用，这是一个 vector。接着可以对 vector 的可变引用调用 push 以便记录测试过程中看到的消息。

2. **RefCell 在运行时记录借用**
当创建不可变和可变引用时，我们分别使用 & 和 &mut 语法。对于 RefCell<T> 来说，则是 **borrow** 和 **borrow_mut** 方法，这属于 RefCell<T> 安全 API 的一部分。
* borrow：返回 **Ref<T>（实现了 Deref）**。每次调用 borrow，RefCell<T> 将活动的不可变借用计数加一。当 Ref<T> 值离开作用域时，不可变借用计数减一。
* borrow_mut：方法返回 **RefMut<T>（实现了 Deref）**。RefCell<T> 在任何时候只允许有多个不可变借用或一个可变借用。

3. 结合 Rc<T> 和 RefCell<T> 来拥有多个可变数据所有者
如果有一个储存了 RefCell<T> 的 Rc<T> 的话，就可以得到有多个所有者 并且 可以修改的值了！
```rust
#[derive(Debug)]
enum List {
    Cons(Rc<RefCell<i32>>, Rc<List>),
    Nil,
}

use crate::List::{Cons, Nil};
use std::cell::RefCell;
use std::rc::Rc;

fn main() {
    let value = Rc::new(RefCell::new(5));

    let a = Rc::new(Cons(Rc::clone(&value), Rc::new(Nil)));

    let b = Cons(Rc::new(RefCell::new(3)), Rc::clone(&a));
    let c = Cons(Rc::new(RefCell::new(4)), Rc::clone(&a));

    *value.borrow_mut() += 10;

    println!("a after = {:?}", a);
    println!("b after = {:?}", b);
    println!("c after = {:?}", c);
}
```

#### 10.4、Weak\<T>
**Weak\<T>**：即 **弱引用（weak reference）** 。调用 Rc::downgrade 时会得到 Weak<T> 类型的智能指针。不同于将 Rc<T> 实例的 strong_count 加 1，调用 Rc::downgrade 会将 weak_count 加 1。Rc<T> 类型使用 weak_count 来记录其存在多少个 Weak<T> 引用，类似于 strong_count。其区别在于 weak_count 无需计数为 0 就能使 Rc<T> 实例被清理。

强引用代表如何共享 Rc<T> 实例的所有权，但弱引用并不属于所有权关系。他们不会造成引用循环，因为任何弱引用的循环会在其相关的强引用计数为 0 时被打断。



测试用的提交hexo文件








































