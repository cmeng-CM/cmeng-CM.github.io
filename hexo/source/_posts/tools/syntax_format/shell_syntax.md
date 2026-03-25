---
title: shell脚本相关笔记
hide: true
abbrlink: 206f81a4
---

### -a到-z的含义
变量	含义
[ -a FILE ]	如果 FILE 存在则为真
[ -b FILE ]	如果 FILE 存在且是一个块特殊文件则为真
[ -c FILE ]	如果 FILE 存在且是一个字特殊文件则为真
[ -e FILE ]	如果 FILE 存在则为真
[ -f FILE ]	如果 FILE 存在且是一个普通文件则为真
[ -g FILE ]	如果 FILE 存在且已经设置了SGID则为真
[ -h FILE ]	如果 FILE 存在且是一个符号连接则为真
[ -k FILE ]	如果 FILE 存在且已经设置了粘制位则为真
[ -r FILE ]	如果 FILE 存在且是可读的则为真
[ -s FILE ]	如果 FILE 存在且大小不为0则为真
[ -t FD ]	如果文件描述符 FD 打开且指向一个终端则为真
[ -u FILE ]	如果 FILE 存在且设置了SUID (set user ID)则为真
[ -w FILE ]	如果 FILE 如果 FILE 存在且是可写的则为真
[ -x FILE ]	如果 FILE 存在且是可执行的则为真
[ -O FILE ]	如果 FILE 存在且属有效用户ID则为真
[ - G FILE ]	如果 FILE 存在且属有效用户组则为真
[ -L FILE ]	如果 FILE 存在且是一个符号连接则为真
[ -N FILE ]	如果 FILE 存在 and has been mod如果ied since it was last read则为真
[ -S FILE ]	如果 FILE 存在且是一个套接字则为真
[ -z STRING ]	“STRING” 的长度为零则为真

字符串判断
变量	含义
str1 = str2	两个字符串完全相等为真
str1 != str2	两个字符串不完全相等为真
-n str1	当串的长度大于0时为真(串非空)
-z str1	当串的长度为0时为真(空串)
str1	当串str1为非空时为真
数字判断
变量	含义
int1 -eq int2	两数字相等为真
int1 -ne int2	两数字不相等为真
int1 -gt int2	int1大于int2为真
int1 -ge int2	int1>= int2为真
in1 -lt int2	int1<int2 为真
int1 -le int2	int1 <= int2为真
文件判断
变量名	含义
-r file	用户可读为真
-w file	用户可写为真
-f file	文件为正规文件为真
-x file	用户可执行为真
-d file	文件为目录为真
-c file	闻见味特殊字符文件为真
-s file	文件大小非0为真
-b file	文件为块特殊文件为真
-t file	文件描述符(默认1)指定的设备为终端时为真
复杂逻辑
变量名	含义
-a	与
-o	或
!	非
!=	不等于

作者：PengboGai
链接：https://www.jianshu.com/p/73b562050e83
来源：简书
著作权归作者所有。商业转载请联系作者获得授权，非商业转载请注明出处。