---
title: MySQL主从、主主、主备模式
tags: 
  - MySQL
  - 同步
categories: Mysql
abbrlink: 30e0af
date: 2020-08-18 16:13:12
---

## 一、主从、主主、主备模式介绍
![主从、主主、主备模式](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/mysql/MySQL主主、主从、主备、单点模型.png)  

主从、主主、主备的基层逻辑都是数据的同步，而主从则将相关的数据同步机制全涉及，所以数据同步逻辑以解析主从逻辑为主。

**mysql主从配置分为三种模式，分别是：**
* 异步复制（Asynchronous replication）：即使用二进制日志文件进行异步操作。master在执行完事后会直接给返回客户端，不考虑从库同步是否完成，从库的同步操做是通过异步线程读取二进制日志文件完成的。
* 全同步复制（Fully synchronous replication）：指当主库执行完一个事务，所有的从库都执行了该事务才返回给客户端。因为需要等待所有从库执行完该事务才能返回，所以全同步复制的性能必然会收到严重的影响。
* 半同步复制（Semisynchronous replication）：介于异步复制和全同步复制之间，主库在执行完客户端提交的事务后不是立刻返回给客户端，而是等待至少一个从库接收到并写到relay log中才返回给客户端。相对于异步复制，半同步复制提高了数据的安全性，同时它也造成了一定程度的延迟，这个延迟最少是一个TCP/IP往返的时间。所以，半同步复制最好在低延时的网络中使用。


## 二、主从同步——异步复制（Asynchronous replication）
### 2.1、异步复制——原理

#### 2.1.1、复制线程
MySQL 复制功能使用三个主线程实现，一个在源服务器上，两个在副本上：
* **二进制日志转储线程（Binary log dump thread）**：当副本连接时，源创建一个线程以将二进制日志内容发送到副本。该线程可以在 **SHOW PROCESSLIST** 源上的输出中标识为该Binlog Dump线程。
二进制日志转储线程获取源二进制日志上的锁，以读取要发送到副本的每个事件。一旦事件被读取，锁就会被释放，甚至在事件被发送到副本之前。
具备多个从库的主库会为每个链接到主库的从库创建一个Binary log dump thread。

* **复制 I/O 线程（Replication I/O thread）**：当 **START SLAVE** 在副本服务器上发出语句时，副本会创建一个 I/O 线程，该线程连接到源并要求它发送记录在其二进制日志中的更新。
复制 I/O 线程读取源 Binlog Dump线程发送的更新（参见上一项）并将它们复制到组成 **副本中继日志的本地文件中**。
该线程的状态：可以通过**SHOW SLAVE STATUS**语句查询 **Slave_IO_running**字段的状态值。

* **复制 SQL 线程（Replication SQL thread）**。  副本创建一个 SQL 线程来读取由复制 I/O 线程写入的中继日志并执行其中包含的事务。

#### 2.1.2、主从复制流程图
![主从复制流程图](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/mysql/主从同步流程图.jpeg) 




### 2.2、异步复制——配置
#### 2.2.1、编码值设置
主从同步或多数据源同步时，一定要保证多个数据的编码值一致，否则在同步阶段会出现乱码，甚至无法解析的情况。编码设置如下：
```bash
# mysqld.cnf

[client]
# 客户端设置
default_character_set=utf8mb4


[mysqld]
# 服务端设置
default-storage-engine=INNODB
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci
```
主从库均需要设置编码。

#### 2.2.2、主库配置
**主库设置分为：server-id设置、二进制日志设置、同步用户设置等三部。**
##### 1. 服务ID
要将源配置为使用基于二进制日志文件位置的复制，必须确保启用二进制日志记录，并建立唯一的服务ID。并且必须是介于 1 和 (2 32 )-1 之间的正整数。
使用默认服务器 ID 为 0，且拒绝来自副本的任何连接，所以必须保证服务ID各个数据库服务不重复且大于0。配置如下：
```bash
# 服务唯一ID
server-id=9000
```

##### 2. 二进制日志（binlog）
###### **日志格式**
**binlog日志**：数据库每提交一次事务，都会把数据变更，记录到一个二进制文件中，这个二进制文件就叫binlog。需注意：只有写操作才会记录至binlog，只读操作是不会的（如select、show语句）。
**binlog的3种格式：**
**1. statement格式：** **MySQL** 中的复制功能最初是基于 **SQL** 语句从源到副本的传播，即记录的是实际执行的sql语句。这称为 **基于语句的日志记录**。
* 优点：
    * 成熟的技术
    * 写入日志文件的数据更少。当更新或删除影响许多行时，这会导致 日志文件所需的存储空间大大减少。
    * 日志文件包含进行任何更改的所有语句，因此它们可用于审计数据库。
* 缺点：
    * 对 SBR 不安全的语句。
    * **INSERT ... SELECT** 与基于行的复制相比，它需要更多的行级锁。
    * **UPDATE** 需要表扫描的语句（因为 WHERE子句中没有使用索引）必须锁定比基于行的复制更多的行。
    * For InnoDB： INSERT使用 AUTO_INCREMENT阻塞其他非冲突语句的INSERT 语句。
    * 对于复杂的语句，在更新或插入行之前，必须在副本上评估和执行该语句。使用基于行的复制，副本只需要修改受影响的行，而不是执行完整的语句。
    * 如果对副本的评估存在错误，尤其是在执行复杂语句时，基于语句的复制可能会随着时间的推移慢慢增加受影响行的误差幅度。
    * 存储函数以与 NOW()调用语句相同的值执行。但是，存储过程并非如此。
    * 确定性可加载函数必须应用于副本。
    * 表定义在源和副本上必须（几乎）相同。

**2. row格式：** binlog记录的是变化前后的数据（涉及所有列），例如update table_a set col1=value1, col2=value2 ... where col1=condition1 and col2=condition2 ...，这称为 **基于行的日志记录**。
* 优点：
    * 所有更改都可以复制。这是最安全的复制形式。
    * INSERT对于任何、UPDATE或 DELETE语句，副本上需要的行锁更少。
    * 对于以下类型的语句，源上需要更少的行锁，从而实现更高的并发性：
        * INSERT ... SELECT
        * INSERT与声明 AUTO_INCREMENT
        * UPDATE或 带有不使用键或不更改大多数检查行的子句的 DELETE语句 。WHERE
* 缺点：
    * **RBR** 可以生成更多必须记录的数据。
    * 生成大  **BLOB** 值的确定性可加载函数使用基于行的复制进行复制比使用基于语句的复制花费更长的间。这是因为 BLOB记录的是列值，而不是生成数据的语句。
    * 无法在副本上看到从源接收并执行了哪些语句。
    * 对于使用存储引擎的表，与将它们作为语句应用时相比，将它们作为基于行的事件应用到二进制日志时，语句**MyISAM**的副本需要更强的锁定。INSERT这意味着MyISAM在使用基于行的复制时不支持对表进行并发插入。

**3. mixed格式**：默认选择statement格式，只在需要时改用row格式。这称为 **混合日志记录**。

**为获取前后变化的数据，建议使用 <font color='red'>基于行的日志记录</font>，具体配置信息如下：**
```bash
[mysqld]
# 配置bin-log信息
# 日志文件名
log-bin=master-bin
log_bin_index = master-bin.index
# 日志格式
binlog_format=row
# 日志保存天数
expire-logs-days=7

# 从 mysql 8.0.x 引进的，单位：秒
# binlog_expire_logs_seconds=2592000
```

###### **同步过滤**
基于业务情况，我们的数据库中并不是所有的库都需要进行复制同步。所以在开启同步前需要指定哪些库是需要进行同步操作的，即同步过滤。同步过滤有两种方式可以设置，分别是直接指定过滤库以及通过指定库记录二进制日志的方式，两种方式情况如下：
* 指定复制库方式
    * 同步：**replicate-do-db=db_name**
    * 不同步：**replicate-ignore-db=db_name**
* 记录二进制方式：
    * 加入记录即同步：**binlog-do-db=db_name**
    * 不加入记录即不同步：**binlog-ignore-db=db_name**

**两种方式区别：**
* 相同点：都可以达到过滤的目的；可每个库需单独配置，可配置多个
* 不同点：针对日志的解析和复制有细微区别，详细可查看 [二进制日志记录选项和变量](https://dev.mysql.com/doc/refman/5.7/en/replication-options-binary-log.html#replication-optvars-binlog)

配置示例：
```bash
[mysqld]
# 需要同步的数据库
binlog-do-db=test_sync
# 不需要同步的库
binlog-ignore-db=mysql
binlog-ignore-db=sys
binlog-ignore-db=information_schema
binlog-ignore-db=performance_schema
```

##### 3. 为复制创建用户
每个从库都需要用于读取master库日志的账户信息，前提是它已被授予 **REPLICATION SLAVE** 特权。虽然可以直接使用root用户，但还是建议单独创建一个独立用户用于从库同步，因为 **复制用户名和密码以纯文本形式存储在复制元数据存储库（slave的mysql.slave_master_info表）中**。  
创建用户示例：如果只是为了同步数据，该账户只需要 **REPLICATION SLAVE** 权限即可
```sql
CREATE USER 'slave_read'@'%' IDENTIFIED BY 'password';
GRANT REPLICATION SLAVE ON *.* TO 'slave_read'@'%';
```


#### 2.2.3、从库及同步机制配置
主库设置好之后，进入从库配置及主从同步机制配置

##### 1. 设置从库配置
* 编码设置
* 服务ID：设置服务ID，原因同主库。
* 日志：副本不需要启用二进制日志记录以进行复制。但是，副本上的二进制日志记录意味着副本的二进制日志可用于数据备份和崩溃恢复。启用了二进制日志记录的副本也可以用作更复杂的复制拓扑的一部分。
* 配置如下：
```bash
# 客户端设置编码字符集为UTF8mb4
[client]
default_character_set=utf8mb4

[mysqld]
# 服务端设置编码
default-storage-engine=INNODB
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci

# 服务唯一ID
server-id=9001

# 配置bin-log信息
# 日志文件名
log-bin=slave-bin
log_bin_index=slave-bin.index
```

##### 2. 从库设置主库链接信息
要将从库设置为与主库通信，则要进行必要的连接信息配置，主要分为三个模块：
* 主库ip，port等信息
* 主库用户同步的账户信息
* 二进制相关信息。

主库ip、port和账户信息在上面已经获取或配置好，下面获取主库的二进制日志相关的信息，获取脚本如下：
```sql
SHOW MASTER STATUS;
```

**查询结果如下：**   

File|Position|Binlog_Do_DB|Binlog_Ignore_DB
:-|:-|:-|:-
master-bin.000001 |	86  |	cm_sync | mysql,sys,information_schema,performance_schema

* File：显示日志文件的名称，表格中二进制日志文件是mysql-bin.000001
* Position：显示文件中的位置。表格中位置是位置是 86
* Binlog_Do_DB：启用二进制日志的库
* Binlog_Ignore_DB：未启用二进制日志的库

**File和Position** 稍后在设置副本时需要它们。它们表示副本应该开始处理来自源的新更新的复制坐标。

通过 **CHANGE MASTER TO** （更多信息请查看官方文档：[CHANGE MASTER TO 语句](https://dev.mysql.com/doc/refman/5.7/en/change-master-to.html)）语句进行设置，登录MySQL数据，执行以下Sql：
```sql
mysql> CHANGE MASTER TO MASTER_HOST = '172.17.0.2',
    MASTER_USER = 'slave_read',
    MASTER_PASSWORD = '123456',
    MASTER_PORT = 3306,
    MASTER_LOG_FILE = 'master-bin.000001',
    MASTER_LOG_POS = 86;
```

**此处只使用几个常用参数：**

参数 | 含义 | 最大长度
:-|:-|:-
MASTER_HOST  |  主库IP  |  60
MASTER_USER  |  用于连接主库的用户   | 	96
MASTER_PASSWORD  |  用于连接主库的密码  | 32
MASTER_PORT  |  主库端口  |
MASTER_LOG_FILE  |  日志文件名称  |  511
MASTER_LOG_POS  |  日志文件中的位置  |

> 注：如果使用docker部署mysql，则ip为容器的ip，端口为容器内部mysql端口。MASTER_LOG_POS参数一定要与主库查询出来的结果一致，否则无法同步。


##### 3. 新的主库和从库配置
无历史数据，全新的主库和从库，上面两步配置完毕后，直接启动复制线程：
```sql
mysql> START SLAVE;
```
执行此过程后，从库将连接到主库并复制自拍摄快照以来在主库上发生的任何更新。

##### 4. 使用现有数据设置复制
针对已有数据的主库，主从启动之前需要先将主库数据通过快照方式导入从库，以便数据同步。
步骤如下：
* 1、先锁定主库，以防止数据新增遗漏
```sql
mysql> FLUSH TABLES WITH READ LOCK;
```
>1、此过程使用FLUSH TABLES WITH READ LOCK, 阻止 表COMMIT的操作 InnoDB。
>2、 FLUSH TABLES语句的客户端保持运行，以便读取锁保持有效。如果退出客户端，锁就会被释放。

* 2、创建数据快照
    * 使用 **[mysqldump](https://dev.mysql.com/doc/refman/5.7/en/mysqldump.html)** 创建数据快照：
    ```sql
    mysqldump --all-databases --master-data > dbdump.db
    ```
    * 使用原始数据文件创建数据快照

* 3、重新启动源服务器。
* 4、在从库导入快照数据
* 5、启动复制线程
* 6、解锁
```sql
mysql> UNLOCK TABLES;
```


##### 5. 将新的从库添加到复制拓扑
可以在不停止源服务器的情况下将另一个副本添加到现有复制配置。方式为通过复制现有副本的数据目录来设置新副本，并为新副本提供不同的 **服务器 ID（由用户指定）**和 **服务器 UUID（在启动时生成）**。

* 1、停止现有副本并记录副本状态信息，特别是源的二进制日志文件和中继日志文件位置。
```sql
mysql> STOP SLAVE;
mysql> SHOW SLAVE STATUS
```

* 2、关闭现有副本
```sql
$> mysqladmin shutdown
```

* 3、将现有副本的数据目录复制到新副本，包括日志文件和中继日志文件。可以通过使用tar或创建存档来执行此操作 ，或者使用cp或rsyncWinZip等工具执行直接复制 。
    * 在复制之前，请验证与现有副本相关的所有文件实际上都存储在数据目录中。例如，InnoDB 系统表空间、撤消表空间和重做日志可能存储在其他位置。
    * 在复制期间，如果文件已用于复制元数据存储库，确保还将这些文件从现有副本复制到新副本。如果表已用于存储库，则表位于数据目录中。
    * 复制后，从新副本上的数据目录副本中删除该 auto.cnf文件，以便新副本以不同的生成服务器 UUID 启动。服务器 UUID 必须是唯一的。

* 4、复制完成后，重新启动现有副本。

* 5、在新副本上，编辑配置并为新副本提供唯一的服务器 ID（使用 server_id系统变量），源或任何现有副本均未使用该 ID。

* 6、启动新的副本服务器，指定 --skip-slave-start选项以便复制尚未开始。使用性能模式复制表或问题SHOW SLAVE STATUS来确认新副本与现有副本相比具有正确的设置。还要显示服务器 ID 和服务器 UUID，并验证这些对于新副本是否正确且唯一。
* 7、通过发出一条 **START SLAVE** 语句来启动复制线程。


#### 2.2.4、从库状态查询
异步复制线程开启后，查看从库的相关状态：
```sql
mysql> SHOW SLAVE STATUS
```
**结果中关键字段是：**
* Slave_IO_State：副本的当前状态。
* Slave_IO_Running: 读取源二进制日志的I/O线程是否正在运行。执行完 **START SLAVE** 后为 **Yes**。
* Slave_SQL_Running：用于执行中继日志中事件的SQL线程是否正在运行。与 I/O 线程一样，执行完 **START SLAVE** 后为 **Yes**。
* Last_IO_Error, Last_SQL_Error: I/O 和 SQL 线程在处理中继日志时注册的最后一个错误。理想情况下，这些应该是空白的，表示没有错误。
* Seconds_Behind_Master：复制 SQL 线程在处理源的二进制日志之后的秒数。较大的数字（或增加的数字）可能表明副本无法及时处理来自源的事件。

在主库上进行状态查询的语句有：
* **SHOW PROCESSLIST**：用于检查正在运行的进程列表。
* **SHOW SLAVE HOSTS**：显示有关副本的基本信息。



#### 2.2.5、配置汇总
**主库配置**
```bash
# mysqld.cnf
[client]
# 客户端设置编码字符集为UTF8mb4
default_character_set=utf8mb4


[mysqld]
# 服务端设置编码
default-storage-engine=INNODB
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci

# 服务唯一ID
server-id=9000

# 配置bin-log信息
# 日志文件名
log-bin=master-bin
log_bin_index = master-bin.index
# 日志格式
binlog_format=row
# 日志保存天数
expire-logs-days=7
# 需要同步的数据库
#binlog-do-db=cm_sync
# 不需要同步的库
binlog-ignore-db=mysql
binlog-ignore-db=sys
binlog-ignore-db=information_schema
binlog-ignore-db=performance_schema
```

**从库配置**
```bash
# mysqld.cnf
# 客户端设置编码字符集为UTF8mb4
[client]
default_character_set=utf8mb4


[mysqld]
# 服务端设置编码
default-storage-engine=INNODB
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci

# 服务唯一ID
server-id=9001

# 配置bin-log信息
# 日志文件名
log-bin=slave-bin
log_bin_index=slave-bin.index

relay_log=slave-relay-bin
read_only=1
```



### 2.3、强一致性——GTID
#### 2.3.1、GTID
GTID：**全局事务标识符** 是在源服务器（master）上创建并与提交的每个事务相关联的唯一标识符。这个标识符不仅对于它起源的服务器是唯一的，而且在给定的复制拓扑中的所有服务器中都是唯一的。   
针对GTID相关操作可以分为两部分：
* 客户端事务在master上提交：提交时它会被分配一个新的 GTID，前提是该事务已写入二进制日志。保证客户端事务具有单调递增的 GTID，生成的数字之间没有间隙。如果客户端事务没有写入二进制日志（例如，因为事务被过滤掉，或者事务是只读的），则不会在源服务器上为其分配 GTID。
* 同步复制事务：从库会根据主库日志中各个GTID对应的事务操作进行数据同步操作，且在主库上提交的事务只能在副本上应用一次，这有助于保证一致性。


##### GTID组成
GTID 表示为一对坐标，由冒号字符 ( : ) 分隔，如下所示：
>GTID = source_id:transaction_id

**source_id**：标识始发服务器 。通常，源 server_uuid用于此目的。
**transaction_id**：是一个序列号，由在源上提交事务的顺序确定。其实就是一个自增序列，从1递增。

MySQL 系统表 **mysql.gtid_executed** 用于保存在 MySQL 服务器上应用的所有事务的分配 GTID，但存储在当前活动的二进制日志文件中的事务除外。

#### 2.3.2、使用 GTID 设置复制
**GTID** 模式是基于开启二进制服务的基础上进行的，下面操作步骤均已 **开启二进制日志为前提**。

##### 1、同步服务器
将mysql服务设置为只读，保证操作期间无数据丢失。  
```sql
mysql> SET @@GLOBAL.read_only = ON;
```

等待所有正在进行的事务提交或回滚。然后，让副本赶上源。在继续之前确保副本已处理所有更新非常重要。

如果是新服务则直接从第三步开始

##### 2、停止所有服务器
```bash
$>  mysqladmin -uusername -p shutdown
```

##### 3、开启主库和从库的GTID设置
开启方式增加配置文件：
```bash
[mysqld]
gtid_mode=ON
enforce-gtid-consistency=ON
```
主库和从库均需设置，设置后重启mysql服务。

##### 4、将副本配置为使用基于 GTID 的自动定位
在副本上发出一条 **CHANGE MASTER TO** 语句，包括 **MASTER_AUTO_POSITION** 在语句中告诉副本源的事务由 GTID 标识的选项。如果除 **MASTER_AUTO_POSITION** 参数外其它参数均已设置，则可以不进行重复设置。

><font color = 'red'>MASTER_LOG_FILE选项和 选项 都MASTER_LOG_POS不能与 MASTER_AUTO_POSITION=1 一起使用。尝试这样做会导致CHANGE MASTER TO语句失败并出现错误。</font>

```sql
mysql> CHANGE MASTER TO
     >     MASTER_HOST = host,
     >     MASTER_PORT = port,
     >     MASTER_USER = user,
     >     MASTER_PASSWORD = password,
     >     MASTER_AUTO_POSITION = 1;
```

##### 5、启动复制线程并禁用只读模式
启动复制线程：
```sql
mysql> START SLAVE;
```

仅当在 **步骤 1** 中将服务器配置为只读时，才需要执行以下步骤。要允许服务器再次开始接受更新，请发出以下语句：
```sql
mysql> SET @@GLOBAL.read_only = OFF;
```

#### 2.3.3、使用 GTID 复制的限制
因为基于 GTID 的复制依赖于事务，所以在使用 MySQL 时不支持一些原本在 MySQL 中可用的特性。相关限制如下：
* 涉及非事务性存储引擎的更新。 
* CREATE TABLE ... SELECT 语句。基于 GTID 的复制时不允许使用语句。
* 临时表。  使用 GTID 时（即当 系统变量设置为时），事务、过程、函数和触发器中不支持CREATE TEMPORARY TABLE和 语句。
* 防止执行不受支持的语句。  为了防止执行会导致基于 GTID 的复制失败的语句，所有服务器都必须 --enforce-gtid-consistency在启用 GTID 时使用该选项启动。
* 跳过交易。  sql_slave_skip_counter使用 GTID 时不支持。
* 忽略服务器。  使用 GTID 时不推荐使用该语句的 IGNORE_SERVER_IDS 选项CHANGE MASTER TO，因为已应用的事务将被自动忽略。


## 三、主从同步——半同步复制（Semisynchronous replication）
主从同步的三种机制分别是异步、半同步、全同步，异步逻辑已经分析完了，下面看下半同步和全同步。先了解下全同步。

**全同步（完全同步复制）**：当源提交事务时，所有副本也必须在源返回到执行事务的会话之前提交事务。即master每次提交都要等所有副本接收并记录了事件，所有副本都通知master记录成功，master才能提交本次事务。
* 优点：完全同步复制意味着可以随时从源故障转移到任何副本。
* 缺点完全同步复制的缺点是完成事务可能会有很多延迟。

**半同步复制（Semisynchronous Replication）**：介于异步复制和完全同步复制之间。源等待直到至少一个副本接收并记录了事件（所需的副本数量是可配置的），然后提交事务。源不等待所有副本确认接收，它只需要来自副本的确认，而不是事件已在副本端完全执行并提交。因此，半同步复制保证如果源崩溃，它已提交的所有事务都已传输到至少一个副本。
* 与完全同步复制相比，半同步复制更快，因为它可以配置为平衡您对数据完整性的要求（确认收到事务的副本数）和提交速度，提交速度由于需要等待而较慢复制品。
* 与异步复制相比，半同步复制的性能影响是提高数据完整性的权衡。

**源与其副本之间的半同步复制操作如下：**
* 副本在连接到源时指示它是否具有半同步能力。
* 如果在源端启用了半同步复制并且至少有一个半同步副本，则在源上执行事务提交的线程会阻塞并等待，直到至少一个半同步副本确认它已收到事务的所有事件，或者直到发生超时。
* 只有在将事件写入其中继日志并刷新到磁盘后，副本才会确认收到事务的事件。
* 如果在没有任何副本确认事务的情况下发生超时，则源将恢复为异步复制。当至少一个半同步副本赶上时，源返回到半同步复制。
* 必须在源端和副本端都启用半同步复制。如果在源上禁用半同步复制，或者在源上启用但没有副本，则源使用异步复制。

### 3.1、半同步实现
半同步复制是使用插件实现的，因此必须将插件安装到服务器中以使其可用。安装插件后，可以通过与其关联的系统变量来控制它。

#### 3.1.1、插件安装
##### 1、介绍
服务器插件必须先加载到服务器中才能使用。MySQL 支持在服务器启动和运行时加载插件。还可以在启动时控制已加载插件的激活状态，并在运行时卸载它们。

**INSTALL PLUGIN** 语句安装的插件：
* 位于插件库文件中的插件可以在运行时使用该 **INSTALL PLUGIN** 语句加载。
* 该语句还在 mysql.plugin表中注册插件，以使服务器在后续重新启动时加载它。
* 插件库文件的基本名称取决于您的平台。常见的后缀 **.so** 适用于 Unix 和类 Unix 系统，**.dll** 适用于 Windows。

##### 2、安装
**安装语句：**
```sql
-- 基于mac环境
-- 主库
INSTALL PLUGIN rpl_semi_sync_master SONAME 'semisync_master.so';

-- 从库
INSTALL PLUGIN rpl_semi_sync_slave SONAME 'semisync_slave.so';
```

**安装查看**
* 可以查看 **INFORMATION_SCHEMA.PLUGINS** 表
* 使用 **SHOW PLUGINS** 语句

此处查看PLUGINS表信息
```sql

SELECT
	PLUGIN_NAME,
	PLUGIN_STATUS 
FROM
	INFORMATION_SCHEMA.PLUGINS 
WHERE
	PLUGIN_NAME LIKE '%semi%';
```

**结果：**
![安装的插件信息](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/mysql/查看插件信息.png)

##### 3、配置
半同步相关的配置项主要使用以下几项：
* **rpl_semi_sync_master_enabled：** 控制是否在源上启用半同步复制。要启用或禁用插件，请将此变量分别设置为 1 或 0。默认值为 0（关闭）。
* **rpl_semi_sync_master_timeout：** 一个以毫秒为单位的值，用于控制源在超时和恢复到异步复制之前等待来自副本的确认提交的时间。默认值为 10000（10 秒）。
* **rpl_semi_sync_slave_enabled：** 类似于 rpl_semi_sync_master_enabled，但控制副本插件。

mysql实例运行时：
```sql
-- 主库
SET GLOBAL rpl_semi_sync_master_enabled = {0|1};
SET GLOBAL rpl_semi_sync_master_timeout = N;

-- 从库
SET GLOBAL rpl_semi_sync_slave_enabled = {0|1};
```

如果在运行时在副本上启用半同步复制，则还必须启动复制 I/O 线程（如果它已经在运行，则首先停止它）以使副本连接到源并注册为半同步副本：
```sql
STOP SLAVE IO_THREAD;
START SLAVE IO_THREAD;
```

实例启动时配置文件配置：
```bash
# 主库
[mysqld]
rpl_semi_sync_master_enabled=1
rpl_semi_sync_master_timeout=1000 # 1 second

# 从库
[mysqld]
rpl_semi_sync_slave_enabled=1
```
自此半同步配置即完成

## 四、延迟复制
MySQL 5.7 支持延迟复制，这样副本服务器故意滞后源至少指定的时间量。默认延迟为 0 秒。设置：
```sql
-- N 为延迟秒数
CHANGE MASTER TO MASTER_DELAY = N;
```
从源接收到的事件直到在源上执行至少 N几秒钟后才会执行。例外情况是格式描述事件或日志文件轮换事件没有延迟，它们只影响 SQL 线程的内部状态。

作用：
* 防止用户在源上出错。DBA 可以将延迟的副本回滚到灾难发生前的时间。
* 测试存在滞后时系统的行为。
* 检查数据库很久以前的样子，而无需重新加载备份。







