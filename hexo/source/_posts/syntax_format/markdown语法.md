---
title: Markdowm语法
date: 2022-11-13 16:13:12
tags: Markdowm
categories: [Markdowm]
---

## 超链接
markdown内超链接分为两种形式，分别是 **行内式** 和 **参考式**
1. 行内式
    * 格式：
    ```
        [链接名称](链接地址)
        或：
        <连接>
    ```
    * 示例：[这是一个连接]()




## 分割线
### 1、markdown官方提供的分割线语法
三个星号（*）、三个中划线（-）、三个下划线（-）三者都能达到下面的效果：
___

### 2、特殊效果
**Markdown** 只控制文档的结构，不控制文档的样式。但是既然依托于**html**语法，那我们就依然能通过HTML+CSS的方式定制分割线的样式。
```html
<!-- 简单示例 -->

<!-- 实线： -->
<hr class="solid">
<!-- 虚线 -->
<hr class="dashed">
<!-- 点状 -->
<hr class="dotted">
<!-- 双线 -->
<hr class="double">

<style>
.solid {
    border-top: 5px solid #FFDEAD;
}
.dashed {
    border-top: 6px dashed #00F5FF;
}
.dotted {
    border-top: 7px dotted #C0FF3E;
}
.double {
    border-top: 8px double #FF7F24;
}

</style>
```













![效果图][dividing_line]

























[dividing_line]: https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/markdown/dividing_line.jpg





