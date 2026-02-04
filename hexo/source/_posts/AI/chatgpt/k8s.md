网络
# 一张“全景图”（先建立直觉）

先给你一条 **真实生产请求链路**，后面所有概念都在这条链路上：

```
[Pod]
  ↓（Pod CIDR）
[Service]
  ↓（Service CIDR / kube-proxy）
[Node]
  ↓（SNAT / NAT 出口 / Egress）
[外部系统]
```

---

# 1️⃣ Pod CIDR ——「Pod 的 IP 世界」

### 是什么

**Pod CIDR** 是 Kubernetes 给 **Pod 分配 IP 的网段**。

* Pod 有自己独立 IP（不是 NAT 出来的）
* Pod ↔ Pod 是三层直连（理想状态）

例子：

```
Pod CIDR: 10.244.0.0/16
某 Pod IP: 10.244.1.23
```

---

### 解决什么问题

* 让每个 Pod 都像一台“独立主机”
* 支持 Pod 之间直接通信（微服务基础）

---

### 生产中怎么用

* **只用于集群内部通信**
* 一般：

  * Pod ↔ Pod
  * Pod ↔ Node

👉 **外部系统基本“看不到” Pod CIDR**

---

### 常见误区

❌ 想让外部系统直接访问 Pod IP
→ **99% 的生产环境不允许**

---

# 2️⃣ Service CIDR ——「稳定访问入口」

### 是什么

**Service CIDR** 是给 **Service 虚拟 IP（ClusterIP）** 用的网段。

例子：

```
Service CIDR: 10.96.0.0/12
某 Service IP: 10.96.12.8
```

---

### 解决什么问题

* Pod IP 会变
* Service IP **永远不变**
* Service = 稳定入口 + 负载均衡

---

### 生产中怎么用

* Pod 调 Pod **几乎都是通过 Service**
* kube-proxy / iptables / ipvs 在背后做转发

```
Pod A → Service IP → Pod B / Pod C
```

---

### 常见误区

❌ Service IP 可以被集群外访问
→ **ClusterIP 只能集群内用**

---

# 3️⃣ CNI ——「真正的网络实现者」

### 是什么

**CNI（Container Network Interface）** 是：

> **“K8s 网络的底层实现插件”**

常见：

* Calico
* Flannel
* Cilium

---

### 解决什么问题

* Pod IP 如何分配
* Pod ↔ Pod 怎么通
* 网络策略怎么做

---

### 生产中怎么用

* **你几乎每天都在用，但没直接配置**
* 不同 CNI 决定：

  * 是否支持 NetworkPolicy
  * 是否支持 Egress 控制
  * 性能模型

---

### 常见误区

❌ Kubernetes 自带网络
→ **K8s 没有网络，只有接口标准**

---

# 4️⃣ SNAT ——「对外访问的关键动作」

### 是什么

**SNAT（Source NAT）** = 修改 **源 IP**

```
Pod IP: 10.244.1.23
↓
SNAT
↓
Node IP: 10.172.143.81
```

---

### 解决什么问题

* Pod IP 外部不可路由
* 外部系统需要“认识”的 IP

---

### 生产中怎么用

* **Pod 访问外部服务必经**
* 默认行为：

  * Pod → Node IP → 外部

---

### 常见误区

❌ Pod 直接暴露 IP 给外部
→ **基本不可控 / 不安全**

---

# 5️⃣ NAT 出口 ——「统一对外身份」

### 是什么

**NAT 出口**是：

> 对外访问时，统一使用的 IP / IP 段

可以是：

* 防火墙
* 路由器
* 云 NAT Gateway

---

### 解决什么问题

* 外部系统 IP 白名单
* 节点频繁扩缩容

---

### 生产中怎么用

```
Pod → Node → NAT Gateway → 外部系统
```

外部只看到：

```
10.200.0.0/24
```

---

### 常见误区

❌ 认为 NAT 出口是 K8s 概念
→ **它是网络 / 基础设施概念**

---

# 6️⃣ Egress ——「从集群出去的流量」

### 是什么

**Egress = 出站流量（集群 → 外部）**

> Ingress：外 → 集群
> Egress：集群 → 外

---

### 解决什么问题

* 谁可以访问外部
* 访问哪些外部系统

---

### 生产中怎么用

#### 1️⃣ 网络策略（CNI 支持）

```yaml
egress:
  - to:
      - ipBlock:
          cidr: 10.156.56.253/32
```

#### 2️⃣ Egress Gateway（进阶）

* 指定出口节点
* 固定出口 IP

---

### 常见误区

❌ 只关注 Ingress
→ **很多安全事故来自 Egress**

---

# 七、把所有概念“连成一条生产逻辑”

### 你当前的真实路径是：

```
Pod (Pod CIDR)
 → Service (Service CIDR)
 → Node
 → SNAT (Node IP)
 → 外部系统
```

### 你想要的是：

```
Pod
 → Service
 → Node
 → SNAT
 → NAT 出口子网
 → 外部系统
```

---

# 八、一句话总结（架构视角）

| 概念           | 本质一句话           |
| ------------ | --------------- |
| Pod CIDR     | Pod 在集群里的“内网地址” |
| Service CIDR | 稳定访问入口          |
| CNI          | K8s 网络的“发动机”    |
| SNAT         | Pod 出去时“换身份证”   |
| NAT 出口       | 集群对外的“统一身份”     |
| Egress       | 谁能出去、去哪         |


