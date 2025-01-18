---
title: Common Table Expressions (CTE)
tags: 
  - CTE
  - Mysql
categories: Mysql
keywords: CTE
date: 2024-12-18 21:13:12
---
### Common Table Expressions (CTE) 的详细描述

Common Table Expressions（通常称为 CTE 或者公共表表达式）是 SQL 中的一种结构，它允许你定义一个临时的结果集，并且可以在同一个查询中引用这个结果集。CTE 有助于简化复杂的查询，提高代码的可读性和维护性。它们特别适用于以下场景：

1. **简化复杂查询**：将复杂的逻辑分解成更小、更易管理的部分。
2. **递归查询**：处理层级或树形结构的数据（如组织架构、分类目录等）。
3. **避免重复计算**：对于需要多次使用相同子查询的情况，可以先通过 CTE 计算一次，然后在主查询中引用。

#### CTE 的主要特点

- **作用范围有限**：CTE 只能在紧随其后的 `SELECT`、`INSERT`、`UPDATE` 或 `DELETE` 语句中使用。
- **一次性计算**：CTE 中的结果集只计算一次，之后可以多次引用，减少了重复计算。
- **可嵌套**：可以在一个 CTE 内部引用另一个 CTE。
- **支持递归**：某些数据库系统（如 PostgreSQL、SQL Server）支持递归 CTE，用于处理层次结构数据。

### 使用范例

为了更好地理解 CTE 的功能，下面通过几个具体例子来展示如何使用 CTE。

#### 示例 1：简化复杂查询

假设我们有一个销售记录表 `sales` 和一个产品表 `products`，我们想要获取每个产品的总销售额以及销售数量。

```sql
WITH ProductSales AS (
    SELECT
        p.product_id,
        p.product_name,
        SUM(s.amount) AS total_sales,
        COUNT(*) AS sales_count
    FROM
        sales s
    JOIN
        products p ON s.product_id = p.product_id
    GROUP BY
        p.product_id, p.product_name
)
SELECT
    product_name,
    total_sales,
    sales_count
FROM
    ProductSales;
```

在这个例子中，`ProductSales` 是一个 CTE，它预先计算了每个产品的总销售额和销售次数。然后，在主查询中，我们可以简单地从 `ProductSales` 中选择所需的字段。

#### 示例 2：递归查询（以员工层级为例）

假设我们有一个员工表 `employees`，其中包含员工 ID (`employee_id`)、经理 ID (`manager_id`) 和姓名 (`name`)。我们想构建一个报告来显示每个员工及其直接下属。

```sql
WITH RECURSIVE EmployeeHierarchy AS (
    -- 基础情况：选择没有经理的顶级员工（即最高层管理者）
    SELECT
        employee_id,
        name,
        manager_id,
        0 AS level
    FROM
        employees
    WHERE
        manager_id IS NULL

    UNION ALL

    -- 递归部分：选择每个员工的直接下属，并增加层级计数
    SELECT
        e.employee_id,
        e.name,
        e.manager_id,
        eh.level + 1
    FROM
        employees e
    JOIN
        EmployeeHierarchy eh ON e.manager_id = eh.employee_id
)
SELECT
    employee_id,
    name,
    manager_id,
    level
FROM
    EmployeeHierarchy
ORDER BY
    level, name;
```

在这个例子中，`EmployeeHierarchy` 是一个递归 CTE。首先，它选择了所有没有经理的顶级员工作为基础情况。然后，它递归地选择每个员工的直接下属，并为每一层增加一个层级计数。最终结果展示了整个公司的员工层级结构。

#### 示例 3：避免重复计算

考虑一个场景，我们需要从订单表 `orders` 中获取每个客户的最新订单信息（订单日期和金额），并且这些信息将在多个地方使用。

```sql
WITH LatestOrder AS (
    SELECT
        customer_id,
        MAX(order_date) AS latest_order_date
    FROM
        orders
    GROUP BY
        customer_id
)
SELECT
    o.customer_id,
    c.customer_name,
    o.order_date,
    o.amount
FROM
    orders o
JOIN
    LatestOrder lo ON o.customer_id = lo.customer_id AND o.order_date = lo.latest_order_date
JOIN
    customers c ON c.customer_id = o.customer_id;
```

这里，`LatestOrder` CTE 计算了每个客户的最新订单日期。然后，主查询利用这个 CTE 来获取具体的订单信息，包括客户名称、订单日期和金额。这样就避免了在主查询中重复执行相同的聚合操作。

### 总结

CTE 提供了一种强大而灵活的方式来构建复杂的 SQL 查询。通过将查询逻辑拆分为易于理解的小块，CTE 不仅提高了代码的可读性和维护性，还能够优化性能，尤其是在涉及重复计算或递归查询的情况下。如果你有技术基础但对 CTE 不熟悉，希望上述示例能帮助你直观地了解这一功能的强大之处。