---
title: Docker之MySQL安装
tags: MySQL
categories:
  - docker
  - mysql
abbrlink: bd5c77e2
date: 2020-08-18 16:13:12
---

# docker 安装 mysql

## 一、下载镜像
以最新版为例：
```bash
docker pull mysql
```
下载后通过 **docker images** 查看：
>REPOSITORY              TAG       IMAGE ID       CREATED        SIZE
>mysql                   latest    7b94cda7ffc7   2 weeks ago    446MB
>redis                   latest    7614ae9453d1   8 months ago   113MB

## 二、启动mysql容器
### 2.1、启动
```bash
docker run -d \
--name mysql-2 \
-p 9000:3306 \
-e MYSQL_ROOT_PASSWORD=123456 \
mysql:latest
```
* **-d**：后台运行
* **--name**：设置容器名称
* **-p**：将主机的9000端口绑定到容器的3306端口，**-p格式：主机(宿主)端口:容器端口**
* **-e**：设置root用户密码
* **mysql:latest**：指定镜像和版本


### 2.2、数据用户密码加密机制

**mysql8及以上**，需要使用navicat链接的话需要修改用户密码的加密方式，该版本有修改：
```mysql
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
```
修改后可查看 mysql库下的user表：
> mysql> select host,user,plugin from user;
> +-----------+------------------+-----------------------+
> | host      | user             | plugin                |
> +-----------+------------------+-----------------------+
> | %         | root             | mysql_native_password |
> | localhost | mysql.infoschema | caching_sha2_password |
> | localhost | mysql.session    | caching_sha2_password |
> | localhost | mysql.sys        | caching_sha2_password |
> +-----------+------------------+-----------------------+
> 4 rows in set (0.01 sec)

## 三、文件挂载
以为启动容器，但文件及配置信息均在容器内部，为了防止数据丢失可将容器内文件挂在到宿主机上，命令如下：
```bash
# 将容器中的 mysql 配置文件复制到宿主机中指定路径下，路径你可以根据需要，自行修改
docker cp mysql:/etc/mysql/mysql.conf.d/mysqld.cnf /usr/local/docker/mysql/config
# 将容器中的 mysql 存储目录复制到宿主机中
docker cp mysql:/var/lib/mysql/ /usr/local/docker/mysql/data
```

总和挂在一起创建及启动容器的命令如下：
```bash
docker run -d \
--name mysql \
-p 3306:3306 \
-v /usr/local/docker/mysql/config/mysqld.cnf:/etc/mysql/mysql.conf.d/mysqld.cnf \
-v /usr/local/docker/mysql/data/mysql:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=123456 \
mysql:latest
```
其余命令不变，多了两个 **-v** 参数用于文件挂载。
后续即可直接使用数据库。

## MySQL配置文件
通过 **mysql --help** 可以获得以下描述：
> Default options are read from the following files in the given order:
> /etc/my.cnf /etc/mysql/my.cnf /usr/etc/my.cnf ~/.my.cnf

**/etc/my.cnf** 文件结尾处：
```bash
!includedir /etc/mysql/conf.d/
!includedir /etc/mysql/mysql.conf.d/
```

所以几处的配置文件按照顺序都会加载到mysql中，所以只需求一处即可，因此本文挂载文件为：**/etc/mysql/mysql.conf.d/mysqld.cnf**