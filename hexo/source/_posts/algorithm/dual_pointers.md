---
title: 双指针
tags: 双指针
categories: 算法
mathjax: true
abbrlink: 91a7e4d1
date: 2020-08-17 16:13:12
---

## 双指针
### **概述**
双指针是一种简单而又灵活的技巧和思想，单独使用可以轻松解决一些特定问题，和其他算法结合也能发挥多样的用处。  
双指针顾名思义，就是同时使用两个指针，在数组、序列、链表结构上指向的是位置，在树、图结构中指向的是节点，通过或同向移动，或相向移动来维护、统计信息。  

### **实例**  

**1. 实例1**    
[leetcode-167. 两数之和 II - 输入有序数组](https://leetcode-cn.com/problems/two-sum-ii-input-array-is-sorted/)  
给你一个下标从 1 开始的整数数组 numbers ，该数组已按 非递减顺序排列  ，请你从数组中找出满足相加之和等于目标数 target 的两个数。如果设这两个数分别是 numbers[index1] 和 numbers[index2] ，则 1 <= index1 < index2 <= numbers.length 。

以长度为 2 的整数数组 [index1, index2] 的形式返回这两个整数的下标 index1 和 index2。

你可以假设每个输入 只对应唯一的答案 ，而且你 不可以 重复使用相同的元素。

你所设计的解决方案必须只使用常量级的额外空间。


示例1  
>输入：numbers = [2,7,11,15], target = 9
>输出：[1,2]
>解释：2 与 7 之和等于目标数 9 。因此 index1 = 1, index2 = 2 。返回 [1, 2] 。

给出数组为升序排序，所以双指针一头一尾，根据二者之和与目标值的大小比较来判断指针移动方向。

**代码**
```Java
public int[] twoSum(int[] numbers, int target) {
    int[] ans = new int[2];
    int n= numbers.length;
    for(int i =0,j=n-1;i<j;){
        int sum = numbers[i]+numbers[j];
        if(sum==target){
            ans[0] = i+1;
            ans[1] = j+1;
            return ans;
        }
        if(sum>target){
            --j;
        }else if (sum<target){
            ++i;
        }
    }
    return ans;
}
```

**2. 实例2**  
[leetcode-19. 删除链表的倒数第 N 个结点](https://leetcode-cn.com/problems/remove-nth-node-from-end-of-list/)  
给你一个链表，删除链表的倒数第 n 个结点，并且返回链表的头结点。  

示例 1:  
![](https://raw.githubusercontent.com/cmeng-CM/image-hosting/master/img/algorithm/双指针1.jpg)  
>输入：head = [1,2,3,4,5], n = 2
>输出：[1,2,3,5]

双指针形式，当快慢两个指针之差为n时，二者保持同时移动，当快到达最后节点，慢指针正好符合删除的节点要求。

**代码**
```Java
public ListNode removeNthFromEnd(ListNode head, int n) {
    ListNode zero = new ListNode(0, head);
    ListNode slow = zero;
    ListNode fast= head;
    for(int i=0;i<n;i++){
        fast = fast.next;
    }
    while(fast!=null){
        slow = slow.next;
        fast =fast.next;
    }
    slow.next = slow.next.next;
    return zero.next;
}
```


