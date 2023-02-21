---
title: 二分查找法
tags: 二分查找法
categories: 算法
mathjax: true
abbrlink: aee0601b
date: 2020-08-17 16:13:12
---

## 二分查找法
### **概述**
二分搜索是一种在有序数组中查找某一特定元素的搜索算法。  
* 搜索过程从数组的中间元素开始，如果中间元素正好是要查找的元素，则搜索过程结束；
* 如果某一特定元素大于或者小于中间元素，则在数组大于或小于中间元素的那一半中查找，而且跟开始一样从中间元素开始比较。
* 如果在某一步骤数组为空，则代表找不到。这种搜索算法每一次比较都使搜索范围缩小一半。

### **实例**  

**1. 实例1**    
给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target ，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。  

示例1  
>输入: nums = [-1,0,3,5,9,12], target = 9  
>输出: 4  
>解释: 9 出现在 nums 中并且下标为 4  

示例2  
>输入: nums = [-1,0,3,5,9,12], target = 2  
>输出: -1  
>解释: 2 不存在 nums 中因此返回 -1  

**代码**
```Java
public int search(int[] nums, int target) {
    int start = 0;
    int end = nums.length-1;
    while(start <= end){
        //取中间元素下标
        int mid = start + (end - start)/2;
        //比较大小，进行区间区分或直接返回结果
        if(target == nums[mid])
            return mid;
        if(target > nums[mid]){
            start = mid + 1;
        }else{
            end = mid - 1;
        }
    }
    return -1;
    }
```

**2. 实例2**  
给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。如果目标值不存在于数组中，返回它将会被按顺序插入的位置。

示例 1:  
>输入: nums = [1,3,5,6], target = 5  
>输出: 2  

示例 2:  
>输入: nums = [1,3,5,6], target = 2  
>输出: 1

**代码**
```Java
public int searchInsert(int[] nums, int target) {
    int start = 0;
    int end = nums.length - 1;
    while (start <= end){
        int mid = start + (end - start) / 2 ;
        if(target == nums[mid])
            return mid;
        if(target > nums[mid])
            start = mid + 1;
        else
            end = mid -1;
    }
    return start;
    }
```

**3. 实例3**  
[leetcode-33. 搜索旋转排序数组](https://leetcode-cn.com/problems/search-in-rotated-sorted-array/)  

整数数组 nums 按升序排列，数组中的值 互不相同 。
在传递给函数之前，nums 在预先未知的某个下标 k（0 <= k < nums.length）上进行了 旋转，使数组变为 [nums[k], nums[k+1], ..., nums[n-1], nums[0], nums[1], ..., nums[k-1]]（下标 从 0 开始 计数）。例如， [0,1,2,4,5,6,7] 在下标 3 处经旋转后可能变为 [4,5,6,7,0,1,2] 。
给你 旋转后 的数组 nums 和一个整数 target ，如果 nums 中存在这个目标值 target ，则返回它的下标，否则返回 -1 。

示例 1：
>输入：nums = [4,5,6,7,0,1,2], target = 0
>输出：4

示例 2：
>输入：nums = [4,5,6,7,0,1,2], target = 3
>输出：-1

**解1：** 根据其旋转坐标，可将数组分为两个升序数组。分别对二者进行二分法查找即可。

**代码**
```Java
public int search(int[] nums, int target) {
    int size = nums.length;
    int rotatedIndex=0;
    //查询第一组升序的最大值下标
    for(int i =0;i<size-1;i++){
        if(nums[i]>nums[i+1]){
            rotatedIndex = i;
            break;
        }
    }
    int ans1 = binarySearch(nums,target,0,rotatedIndex);
    int ans2 = binarySearch(nums,target,rotatedIndex+1,size-1);
    if(ans1!=-1){
        return ans1;
    }else if(ans2!=-1){
        return ans2;
    }else{
        return -1;
    }

}

public Integer binarySearch(int[] nums,int target,int left,int reight){
    while(left<=reight){
        int mid = left + (reight - left) / 2;
        if(nums[mid]==target){
            return mid;
        }else if(target>nums[mid]){
            left = mid + 1;
        }else {
            reight = mid - 1;
        }
    }
    return -1;
}
```
**解2：** 直接进行二分法查找。数组旋转后一定分为各自两段有序数组，可进行如下步骤：
  1. 进行二分操作,可分为两部分，一定有有一部分为有序数组
  2. 如果target在有序数组的部分，则以有序数组为基础继续进行二分法查找。
  3. 如果target不在有序数组部分，继续进行【1】操作

```Java
public int search(int[] nums, int target) {
    int n = nums.length;
    if (n == 0) {
        return -1;
    }
    if (n == 1) {
        return nums[0] == target ? 0 : -1;
    }
    int l = 0, r = n - 1;
    while (l <= r) {
        int mid = (l + r) / 2;
        if (nums[mid] == target) {
            return mid;
        }
        if (nums[0] <= nums[mid]) {
            if (nums[0] <= target && target < nums[mid]) {
                r = mid - 1;
            } else {
                l = mid + 1;
            }
        } else {
            if (nums[mid] < target && target <= nums[n - 1]) {
                l = mid + 1;
            } else {
                r = mid - 1;
            }
        }
    }
    return -1;
}

```


