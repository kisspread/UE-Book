# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | QUIC 消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-10-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging) | |

---

## 用途

本插件为 UE 自带的 **消息子系统（Messaging Subsystem）** 添加了一个基于 **QUIC 协议** 的传输层。QUIC（Quick UDP Internet Connections）是一种基于 UDP 的现代传输协议，具有以下特点：

- **低延迟连接建立**：0-RTT 或 1-RTT 握手
- **内置加密**：TLS 1.3 支持
- **多路复用**：单个连接上多个流，无队头阻塞
- **连接迁移**：网络切换时保持连接

该插件解决了传统基于 TCP 的消息传输在高延迟、丢包或网络切换环境下的性能瓶颈，适合需要可靠、低延迟、加密通信的场景，例如多人在线游戏、远程协作工具、实时数据同步等。

---

## 使用场景

- 需要可靠的点对点或点到服务器通信，且要求低连接延迟（如频繁断线重连的移动游戏）
- 同时与多个远程节点通信，需要多路复用减少连接数
- 要求传输层自带加密，简化安全配置
- 需要应对网络切换（如从 Wi-Fi 切到蜂窝数据）而不断开连接
- 作为现有 UDP/TCP 消息传输的替代或补充

---

## 蓝图用法

该插件不提供任何直接暴露给蓝图的函数或节点。所有功能需通过 C++ 调用 `FQuicEndpointManager` 及相关 API。

---

## C++ 用法

### 头文件引入

```cpp
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"
#include "QuicFlags.h"
```

### 基本用法

#### 1. 创建端点管理器并启动客户端

```cpp
// 创建客户端配置
TSharedRef<FQuicEndpointConfig> ClientConfig = MakeShared<FQuicEndpointConfig>();
ClientConfig->Endpoint = FIPv4Endpoint(FIPv4Address(192, 168, 1, 100), 12000);
ClientConfig->LocalNodeId = FGuid::NewGuid();
ClientConfig->EncryptionMode = EEncryptionMode::Enabled;
ClientConfig->DiscoveryTimeoutSec = 5;

// 初始化端点管理器（默认客户端模式）
FQuicEndpointManager* EndpointManager = new FQuicEndpointManager(ClientConfig);
```

#### 2. 转换为服务器模式

```cpp
// 服务器需要证书和私钥路径
FString CertPath = FPaths::ProjectContentDir() / TEXT("Certificates/server.pem");
FString KeyPath  = FPaths::ProjectContentDir() / TEXT("Certificates/server.key");

TSharedRef<FQuicServerConfig> ServerConfig = MakeShared<FQuicServerConfig>();
ServerConfig->Endpoint = FIPv4Endpoint(FIPv4Address(192, 168, 1, 100), 12000);
ServerConfig->AuthenticationMode = EAuthenticationMode::Enabled;
ServerConfig->ConnCooldownMode = EConnectionCooldownMode::Enabled;
ServerConfig->ConnCooldownMaxAttempts = 5;

FQuicEndpointManager* EndpointManager = new FQuicEndpointManager(ServerConfig);
EndpointManager->InitializeServer(CertPath, KeyPath);
```

#### 3. 发送消息

```cpp
// 创建出站消息
TSharedPtr<TArray<uint8>, ESPMode::ThreadSafe> Payload = MakeShared<TArray<uint8>>();
Payload->Append(/* your serialized data */);

FGuid RecipientId(/* 目标节点 ID */);
FOutboundMessage OutMsg(Payload, RecipientId, EndpointManager->GetLocalNodeId());
EndpointManager->EnqueueOutboundMessage(OutMsg);
```

#### 4. 处理入站消息

```cpp
// 在 Tick 或事件中处理入站队列
FInboundMessage InMsg;
while (EndpointManager->DequeueInboundMessage(InMsg))
{
    // 解析 InMsg.UnserializedMessage 中的自定义协议数据
}
```

#### 5. 获取连接统计信息

```cpp
FMessageTransportStatistics Stats;
if (EndpointManager->GetConnectionStatistics(RemoteEndpoint, Stats))
{
    UE_LOG(LogTemp, Log, TEXT("RTT: %f ms, PacketLoss: %f"), Stats.AverageRTT, Stats.PacketLoss);
}
```

> 上述代码来源于 `QuicEndpointManager.h` 和 `QuicClient.h` 中的公开方法。完整用法请参考 `Engine/Plugins/Experimental/QuicMessaging/Source/QuicMessagingTransport/Private/` 下各文件。

---

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何启动 QUIC 服务器等待客户端连接，并接收/发送消息。

### QuicMessagingDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"

class FQuicMessagingDemo
{
public:
    void StartServer();
    void Stop();
    void SendToClient(const FIPv4Endpoint& ClientEndpoint, const TArray<uint8>& Data);

private:
    FQuicEndpointManager* EndpointManager = nullptr;
    TSharedPtr<FQuicServerConfig> ServerConfig;
};
```

### QuicMessagingDemo.cpp

```cpp
#include "QuicMessagingDemo.h"
#include "QuicFlags.h"
#include "Misc/Paths.h"
#include "HAL/PlatformProcess.h"

void FQuicMessagingDemo::StartServer()
{
    // 证书路径（自行生成或使用内置证书）
    FString CertPath = FPaths::ProjectContentDir() / TEXT("QuicCerts/server.pem");
    FString KeyPath  = FPaths::ProjectContentDir() / TEXT("QuicCerts/server.key");

    ServerConfig = MakeShared<FQuicServerConfig>();
    ServerConfig->Endpoint = FIPv4Endpoint(FIPv4Address(0, 0, 0, 0), 12000);
    ServerConfig->AuthenticationMode = EAuthenticationMode::Enabled;
    ServerConfig->ConnCooldownMode = EConnectionCooldownMode::Enabled;

    EndpointManager = new FQuicEndpointManager(ServerConfig);
    EndpointManager->InitializeServer(CertPath, KeyPath);

    UE_LOG(LogTemp, Log, TEXT("QUIC Server started on port 12000"));
}

void FQuicMessagingDemo::Stop()
{
    if (EndpointManager)
    {
        EndpointManager->Shutdown();
        delete EndpointManager;
        EndpointManager = nullptr;
    }
}

void FQuicMessagingDemo::SendToClient(const FIPv4Endpoint& ClientEndpoint, const TArray<uint8>& Data)
{
    TSharedPtr<TArray<uint8>, ESPMode::ThreadSafe> Payload = MakeShared<TArray<uint8>>(Data);
    FOutboundMessage OutMsg(Payload, FGuid(), EndpointManager->GetLocalNodeId());
    EndpointManager->EnqueueOutboundMessage(OutMsg);
}
```

> 注意：实际项目中需要处理认证握手、消息序列化/反序列化、多线程安全等细节。此示例仅展示基本生命周期。

---

## 模块依赖

使用 `QuicMessagingTransport` 模块时，你的 `Build.cs` 需要添加以下独特依赖：

| 模块 | 用途 |
|---|---|
| `Networking` | 网络地址和套接字处理 |
| `MessagingCommon` | 消息系统公共接口 |
| `MessageBus` | 消息总线（若使用消息系统） |
| `OpenSSL` | 证书生成与 TLS 握手 |
| `msquic` | 微软 QUIC 实现（第三方库） |
| `Sockets` | UDP 套接字封装 |

> 其他常见依赖（Core、CoreUObject、Engine 等）不再列出。

---

## 维护状态

### 近期更新

- `ce6ff39` 2025-09-12 — 修复 `nodiscard` 属性警告
- `b059f7b` 2025-03-13 — 修复不可达代码警告
- `e7a0426` 2024-06-12 — 更新测试标记宏
- `572e87b` 2023-10-16 — 无关的插件更名提交
- `00d774b` 2023-10-11 — 修复编译错误

### 维护评价

- **创建时间**：2023-10-11，距今约 2 年
- **更新频率**：2025 年仍有两次提交（主要为警告修复），表明团队仍在维护
- **功能更新**：近期无功能性新增，以编译兼容性和警告清理为主
- **稳定性**：没有明显已知问题或废弃标记
- **推荐程度**：✅ 推荐用于新项目，特别是需要高性能 QUIC 传输的场景。但注意其位于 `Experimental` 目录，API 可能在未来版本变化。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging)
- [官方文档](https://docs.unrealengine.com/5.7/API/Plugins/QuicMessaging)（若存在）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging/Tests)（可能无）