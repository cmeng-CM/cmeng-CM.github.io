---
title: 回溯
tags: 回溯
categories: 算法
mathjax: true
abbrlink: f92eff5d
date: 2020-08-17 16:13:12
---

## 回溯
### **概述**
**回溯法**（英语：backtracking）是暴力搜索法中的一种。
对于某些计算问题而言，回溯法是一种可以找出所有（或一部分）解的一般性算法，尤其适用于约束满足问题（在解决约束满足问题时，我们逐步构造更多的候选解，并且在确定某一部分候选解不可能补全成正确解之后放弃继续搜索这个部分候选解本身及其可以拓展出的子候选解，转而测试其他的部分候选解）。  

回溯算法又称 <font color=#0099ff>试探法</font>，采用试错的思想。在分步解决问题的过程中，当它通过尝试发现，现有的分步答案不能得到有效的正确的解答的时候，它将取消上一步甚至是上几步的计算，再通过其它的可能的分步解答再次尝试寻找问题的答案。回溯法通常用最简单的递归方法来实现，在反复重复上述的步骤后可能出现两种情况：
  * 找到一个可能存在的正确的答案
  * 在尝试了所有可能的分步方法后宣告该问题没有答案  

在最坏的情况下，回溯法会导致一次复杂度为指数时间的计算。

**例如:**
在统计1~N中整数的所有子集问题时，就可以使用 <font color = #0099ff>回溯法</font> 进行处理。从1开始每个数字都有两种可能，存在子集或不存在子集，每种可能都会有一种结果，那么问题的结果就是所有可能的子集的集合。



### **实例**  
**1. 实例1**
[](https://leetcode-cn.com/problems/subsets/)