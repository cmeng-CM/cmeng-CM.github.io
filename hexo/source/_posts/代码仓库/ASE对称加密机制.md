---
title: 服务端接口鉴权机制——HMAC
tags: 
  - HMAC
  - ASE
  - 后端
categories: HMAC
mathjax: true
date: 2024-08-17 16:13:12
---


符合AES加密要求的字符串作为密钥，并且这个字符串可以直接用于加密和解密操作，那么我们需要确保这个字符串具有正确的长度（16字节/AES-128, 24字节/AES-192, 或32字节/AES-256）。下面是一个具体的例子，使用一个32字符长的字符串作为AES-256的密钥。

### 直接使用的密钥字符串

```java
public class Constants {
    // 32 字符长的字符串，适用于 AES-256
    public static final String SHARED_SECRET = "your32characterlongsecretkey";
}
```

### 完整实现示例

#### 1. **签名与验证**

##### 客户端签名请求

客户端在发送请求之前，使用共享密钥对特定的请求头字段（例如时间戳和nonce）进行签名，并将签名结果附加到请求头中。

```java
import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Base64;
import java.util.UUID;

public class ClientSignatureExample {
    private static final byte[] sharedSecretBytes = Constants.SHARED_SECRET.getBytes("UTF-8");

    public static void main(String[] args) throws Exception {
        URL url = new URL("https://api.cmeng.com/list");
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();
        conn.setRequestMethod("POST");

        // 创建唯一的时间戳和随机数
        String timestamp = Long.toString(System.currentTimeMillis());
        String nonce = UUID.randomUUID().toString();

        // 对时间戳和随机数进行签名
        String dataToSign = timestamp + nonce;
        String signature = signData(dataToSign, sharedSecretBytes);

        // 设置请求头
        conn.setRequestProperty("Timestamp", timestamp);
        conn.setRequestProperty("Nonce", nonce);
        conn.setRequestProperty("Authorization", "HMAC " + signature);

        int responseCode = conn.getResponseCode();
        System.out.println("Response Code: " + responseCode);
    }

    private static String signData(String data, byte[] secretKey) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secretKey, "HmacSHA256"));
        byte[] signedData = mac.doFinal(data.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(signedData);
    }
}
```

##### 服务端验证签名

服务端接收到请求后，使用相同的共享密钥对签名进行验证，以确保请求来自合法客户端，并且未被篡改。

```java
import javax.servlet.http.HttpServletRequest;
import java.security.MessageDigest;
import java.util.Base64;

public class ServerSignatureVerification {

    private static final byte[] sharedSecretBytes = Constants.SHARED_SECRET.getBytes("UTF-8");

    public boolean verifyRequest(HttpServletRequest request) throws Exception {
        String timestamp = request.getHeader("Timestamp");
        String nonce = request.getHeader("Nonce");
        String authorizationHeader = request.getHeader("Authorization");

        if (timestamp == null || nonce == null || authorizationHeader == null) {
            return false;
        }

        String receivedSignature = authorizationHeader.replace("HMAC ", "");
        String dataToVerify = timestamp + nonce;

        // 验证签名
        String calculatedSignature = signData(dataToVerify, sharedSecretBytes);
        return MessageDigest.isEqual(
            Base64.getDecoder().decode(receivedSignature),
            Base64.getDecoder().decode(calculatedSignature)
        );
    }

    private String signData(String data, byte[] secretKey) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secretKey, "HmacSHA256"));
        byte[] signedData = mac.doFinal(data.getBytes("UTF-8"));
        return Base64.getEncoder().encodeToString(signedData);
    }
}
```

#### 2. **防止重放攻击**

为了进一步增强安全性，可以在服务端记录每个收到的时间戳和随机数组合，确保它们不会被重复使用。可以设置一个合理的过期时间窗口，超出这个时间段的请求将被视为无效。

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

public class ReplayAttackPrevention {
    private static final long EXPIRATION_TIME_MS = TimeUnit.MINUTES.toMillis(5);
    private static final ConcurrentHashMap<String, Long> seenNonces = new ConcurrentHashMap<>();

    public static boolean isNonceValid(String nonce, String timestamp) {
        // 检查时间戳是否在有效期内
        long now = System.currentTimeMillis();
        long messageTime = Long.parseLong(timestamp);
        if (now - messageTime > EXPIRATION_TIME_MS) {
            return false;
        }

        // 检查 nonce 是否已经被使用过
        return seenNonces.putIfAbsent(nonce, now) == null;
    }
}
```

在示例代码中，`HMAC` 是“基于哈希的消息认证码”（Hash-based Message Authentication Code）的缩写。它是一种用于验证消息完整性和身份验证的机制，结合了哈希函数和密钥来生成一个固定长度的认证码。HMAC 不仅可以确保消息未被篡改，还可以验证发送者的真实性。

### HMAC 的工作原理

1. **输入**：需要一个密钥（Key）和消息（Message）。
2. **处理**：使用特定的哈希算法（如SHA-256），根据密钥对消息进行两次哈希计算。
3. **输出**：生成一个固定长度的字符串，即 HMAC 值或标签（Tag），通常以十六进制或Base64编码形式表示。

### 示例中的 `HMAC`

在之前的Java示例中，我们使用了 `HMAC` 来签名请求头中的时间戳和随机数（nonce），以便服务端能够验证这些信息的真实性和完整性。具体来说：

```java
// 对时间戳和随机数进行签名
String dataToSign = timestamp + nonce;
String signature = signData(dataToSign, sharedSecretBytes);
```

这里的 `signData` 方法实现了 HMAC 签名过程：

```java
private static String signData(String data, byte[] secretKey) throws Exception {
    Mac mac = Mac.getInstance("HmacSHA256");
    mac.init(new SecretKeySpec(secretKey, "HmacSHA256"));
    byte[] signedData = mac.doFinal(data.getBytes("UTF-8"));
    return Base64.getEncoder().encodeToString(signedData);
}
```

#### 解释

- **`HmacSHA256`**：这是指定使用的哈希算法，表示我们将使用SHA-256作为基础哈希函数来计算 HMAC。
- **`Mac.getInstance("HmacSHA256")`**：创建一个 HMAC 实例，指定使用 SHA-256 作为哈希算法。
- **`mac.init(new SecretKeySpec(secretKey, "HmacSHA256"))`**：初始化 HMAC 实例，提供共享密钥（secretKey）。
- **`mac.doFinal(data.getBytes("UTF-8"))`**：对给定的数据执行最终的 HMAC 计算，生成签名。
- **`Base64.getEncoder().encodeToString(signedData)`**：将生成的二进制签名转换为Base64编码的字符串，便于在网络上传输。

### 为什么使用 HMAC？

- **安全性**：HMAC 提供了比简单哈希更强的安全性，因为它不仅依赖于哈希算法，还依赖于一个秘密密钥，这使得攻击者即使知道了哈希算法也无法伪造签名。
- **完整性**：通过比较接收到的消息与其 HMAC 签名，接收方可以确认消息没有被篡改。
- **身份验证**：只有知道正确密钥的一方才能生成有效的 HMAC 签名，因此它可以用来验证发送者的身份。

### 总结

在API接口调用中使用 HMAC 可以有效地保护数据的完整性和真实性，同时避免直接传输敏感信息。通过将 HMAC 签名附加到每个请求，服务端可以在不暴露任何敏感信息的情况下验证客户端的身份和请求的有效性。