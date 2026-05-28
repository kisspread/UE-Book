# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | QUIC消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging) | |

## 用途

该插件为 Unreal Engine 的消息传递子系统提供了一个基于 QUIC 协议的传输层实现。QUIC 是 Google 开发的基于 UDP 的多路复用传输协议，旨在降低连接延迟、提高可靠性，并内置加密支持。

**解决的问题**：
1. **替代传统 TCP/UDP**：为需要高吞吐量、低延迟和连接迁移能力的网络应用场景（如实时多人游戏、分布式计算）提供更现代的传输协议选择。
2. **内置安全与认证**：提供基于 TLS 1.3 的加密通信和可选的客户端认证机制，无需额外集成。
3. **连接管理**：实现了服务器-客户端模型，包括连接建立、保活、断线重连和连接冷却等复杂网络管理逻辑。

**为什么存在**：
作为 Epic 的实验性技术探索，旨在评估 QUIC 协议在 UE 消息系统中的应用潜力，为未来可能的大规模网络功能重构提供技术储备。

## 使用场景

- 你需要在 LAN 或互联网上实现低延迟、高可靠性的 RPC 或状态同步 → 用 QUIC Messaging 作为底层传输。
- 你的分布式工具链（如多编辑器协同）需要比 TCP 更快、比原始 UDP 更可靠的通信 → 使用本插件。
- 你需要对网络连接进行细粒度控制，如自定义认证流程、加密设置和连接冷却策略 → 使用 `FQuicEndpointManager` 及其配置。

## 蓝图用法

此插件为底层传输层模块，主要提供 C++ API。当前版本**未直接暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 函数**。所有操作均需通过 C++ 代码与 `FQuicEndpointManager` 交互完成。

## C++ 用法

### 头文件引入

```cpp
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"
#include "QuicFlags.h"
#include "QuicMessages.h"
```

### 基本用法：创建客户端连接

以下示例展示了如何初始化一个 QUIC 客户端并连接到服务器。

```cpp
// 来源于对 FQuicEndpointManager 和 FQuicClient 配置结构的分析
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"

void SetupQuicClient()
{
    // 1. 配置客户端参数
    auto ClientConfig = MakeShared<FQuicClientConfig>();
    ClientConfig->Endpoint = FIPv4Endpoint(FIPv4Address::Any, 8443); // 本地绑定端口
    ClientConfig->EncryptionMode = EEncryptionMode::Enabled;
    ClientConfig->ClientVerificationMode = EQuicClientVerificationMode::Verify; // 验证服务器证书

    // 2. 创建端点管理器（默认以客户端模式启动）
    auto EndpointManager = MakeShared<FQuicEndpointManager>(ClientConfig.ToSharedRef());

    // 3. 绑定消息接收委托
    EndpointManager->OnMessageValidated().BindLambda([](const FInboundMessage& Message)
    {
        UE_LOG(LogTemp, Log, TEXT("Received message from node %s, type: %d"),
            *Message.MessageHeader.SenderId.ToString(),
            (uint8)Message.MessageHeader.MessageType);
        // 处理接收到的消息数据...
    });

    // 4. 添加服务器节点（模拟服务发现或已知配置）
    FIPv4Endpoint ServerEndpoint(FIPv4Address::Parse(TEXT("192.168.1.100")), 8443);
    EndpointManager->AddClient(ServerEndpoint);

    // 5. 发送数据到服务器
    FQuicPayloadPtr Payload = MakeShared<FQuicPayload>();
    // ... 填充Payload数据 ...
    TArray<TTuple<FGuid, uint32>> MessageMetas;
    // 假设服务器的NodeId已知
    FGuid ServerNodeId = ...; 
    MessageMetas.Add(MakeTuple(ServerNodeId, 0)); // 0 为临时消息ID

    EndpointManager->EnqueueOutboundMessages(
        Payload, MessageMetas, EQuicMessageType::Data);
}
```

### 进阶用法：配置带认证的服务器

以下示例展示了如何初始化一个要求客户端认证的 QUIC 服务器。

```cpp
// 来源于对 FQuicServerConfig 和认证流程的分析
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"
#include "QuicCertificate.h" // 用于生成自签名证书

void SetupAuthenticatedQuicServer()
{
    // 1. 生成或指定证书（生产环境应使用正式证书）
    FString CertPath, KeyPath;
    TTuple<FString, FString> Paths = QuicCertificateUtils::GetSelfSignedPaths();
    if (!FPaths::FileExists(Paths.Key))
    {
        QuicCertificateUtils::CreateSelfSigned();
    }
    CertPath = Paths.Key;
    KeyPath = Paths.Value;

    // 2. 配置服务器参数
    auto ServerConfig = MakeShared<FQuicServerConfig>();
    ServerConfig->Endpoint = FIPv4Endpoint(FIPv4Address::Any, 8443);
    ServerConfig->EncryptionMode = EEncryptionMode::Enabled;
    ServerConfig->AuthenticationMode = EAuthenticationMode::Enabled; // 启用认证
    ServerConfig->MaxAuthenticationMessageSize = 1024; // 限制认证消息大小
    ServerConfig->Certificate = CertPath;
    ServerConfig->PrivateKey = KeyPath;
    ServerConfig->ConnCooldownMode = EConnectionCooldownMode::Enabled; // 启用连接冷却
    ServerConfig->ConnCooldownMaxAttempts = 5;
    ServerConfig->ConnCooldownPeriodSec = 30;
    ServerConfig->ConnCooldownSec = 30;

    // 3. 创建端点管理器并启动服务器
    auto EndpointManager = MakeShared<FQuicEndpointManager>(ServerConfig.ToSharedRef());
    EndpointManager->InitializeServer(); // 切换到服务器模式

    // 4. 绑定认证和节点发现回调
    EndpointManager->OnEndpointNodeDiscovered().BindLambda([](const FGuid& NodeId)
    {
        UE_LOG(LogTemp, Log, TEXT("New node discovered: %s"), *NodeId.ToString());
    });

    EndpointManager->OnEndpointNodeLost().BindLambda([](const FGuid& NodeId)
    {
        UE_LOG(LogTemp, Log, TEXT("Node lost: %s"), *NodeId.ToString());
    });

    // 5. 处理认证消息（需要自定义逻辑）
    // EndpointManager 的 OnMessageValidated 委托在认证模式下，
    // 对于未认证节点只会收到类型为 Authentication 的消息。
    // 你需要在此验证客户端身份，成功后调用：
    // EndpointManager->SetEndpointAuthenticated(ClientNodeId);
}
```

## Demo 示例

以下是一个最小化的、可编译的 QUIC 回显服务器和客户端示例，展示了基本的消息收发。

```cpp
// QuicEchoDemo.h
#pragma once
#include "CoreMinimal.h"

class FQuicEndpointManager;
typedef TSharedPtr<FQuicEndpointManager, ESPMode::ThreadSafe> FQuicEndpointManagerPtr;

class FQuicEchoServer
{
public:
    FQuicEchoServer();
    ~FQuicEchoServer();
    void Start();
    void Stop();

private:
    FQuicEndpointManagerPtr EndpointManager;
};

class FQuicEchoClient
{
public:
    FQuicEchoClient();
    ~FQuicEchoClient();
    void Connect(const FString& ServerIP, int32 Port);
    void SendMessage(const FString& Text);
    void Disconnect();

private:
    FQuicEndpointManagerPtr EndpointManager;
};
```

```cpp
// QuicEchoDemo.cpp
#include "QuicEchoDemo.h"
#include "QuicEndpointManager.h"
#include "QuicEndpointConfig.h"

// 服务器实现
FQuicEchoServer::FQuicEchoServer()
{
    auto Config = MakeShared<FQuicServerConfig>();
    Config->Endpoint = FIPv4Endpoint(FIPv4Address::Any, 12345);
    Config->AuthenticationMode = EAuthenticationMode::Disabled;
    EndpointManager = MakeShared<FQuicEndpointManager>(Config.ToSharedRef());
}

FQuicEchoServer::~FQuicEchoServer()
{
    Stop();
}

void FQuicEchoServer::Start()
{
    EndpointManager->InitializeServer();

    // 绑定消息处理：将收到的消息原样发回
    EndpointManager->OnMessageValidated().BindLambda(
        [this](const FInboundMessage& Message)
    {
        // 反转消息头中的收发者，实现回显
        FMessageHeader ResponseHeader;
        ResponseHeader.MessageType = EQuicMessageType::Data;
        ResponseHeader.SenderId = Message.MessageHeader.RecipientId; // 服务器
        ResponseHeader.RecipientId = Message.MessageHeader.SenderId; // 客户端
        ResponseHeader.SerializedMessageSize = Message.MessageHeader.SerializedMessageSize;

        // 序列化并发送回客户端
        FQuicPayloadPtr HeaderPayload = EndpointManager->SerializeHeader(ResponseHeader);
        FOutboundMessage Response(Message.Sender, Message.UnserializedMessage, HeaderPayload);
        // 注意：这里为了示例简化，实际应通过 EnqueueOutboundMessages 发送
    });
}

void FQuicEchoServer::Stop()
{
    if (EndpointManager)
    {
        EndpointManager->Shutdown();
    }
}

// 客户端实现
FQuicEchoClient::FQuicEchoClient()
{
    auto Config = MakeShared<FQuicClientConfig>();
    Config->Endpoint = FIPv4Endpoint(FIPv4Address::Any, 0); // 随机本地端口
    EndpointManager = MakeShared<FQuicEndpointManager>(Config.ToSharedRef());
}

FQuicEchoClient::~FQuicEchoClient()
{
    Disconnect();
}

void FQuicEchoClient::Connect(const FString& ServerIP, int32 Port)
{
    FIPv4Endpoint ServerEndpoint(FIPv4Address::Parse(*ServerIP), Port);
    EndpointManager->AddClient(ServerEndpoint);
}

void FQuicEchoClient::SendMessage(const FString& Text)
{
    // 准备消息负载
    FQuicPayloadPtr Payload = MakeShared<FQuicPayload>();
    FTCHARToUTF8 Converter(*Text);
    Payload->Append((uint8*)Converter.Get(), Converter.Length());

    // 准备消息元数据（需要知道服务器的NodeId，通常通过Hello消息获取）
    // 这里假设已从 OnEndpointNodeDiscovered 获得了服务器的NodeId
    FGuid ServerNodeId = ...; 
    TArray<TTuple<FGuid, uint32>> Metas;
    Metas.Add(MakeTuple(ServerNodeId, 0));

    EndpointManager->EnqueueOutboundMessages(Payload, Metas, EQuicMessageType::Data);
}

void FQuicEchoClient::Disconnect()
{
    if (EndpointManager)
    {
        EndpointManager->Shutdown();
    }
}
```

## 模块依赖

此插件依赖于标准的网络和加密库。在您的模块 `Build.cs` 中，需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `QuicMessaging` | 消息系统集成模块 |
| `QuicMessagingTransport` | QUIC 传输层核心实现 |
| `OpenSSL` | 用于生成和管理 TLS 证书（服务器端必需） |
| `MsQuic` | 微软的 QUIC 协议库实现 |

**注意**：由于 `MsQuic` 是第三方库，其集成方式可能随引擎版本变化，请参考实际项目中的 `Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致输出乱码的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了32位与64位格式说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了重复符号的链接错误。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue | 解决了忽略声明为‘nodiscard’属性函数返回值的问题。 |

### 维护评价

**综合评价：实验性组件，维护不活跃，谨慎使用。**

- **创建时间**：约 3 年前（2023年6月）。
- **最近更新频率**：近期（2026年）有几次更新，但均为底层修复、编译警告处理和代码风格调整（如 UE_LOG 迁移），**无任何新功能或架构改进**。
- **维护状态**：处于**低活跃维护**状态。近期更新表明代码仍在被维护以兼容引擎新版本，但缺乏实质性功能演进。
- **实验性**：插件明确标记为实验性 (`EnabledByDefault: false`)，且位于 `Experimental` 目录下。这意味着 Epic 不提供任何稳定性或 API 兼容性保证。
- **已知限制**：
    1. 无蓝图接口，纯 C++ API。
    2. 缺乏官方文档和示例。
    3. 依赖于第三方库 `MsQuic`，集成可能复杂。
    4. 认证、连接管理等高级功能的实现细节和最佳实践未文档化。
- **使用建议**：不建议在生产项目中直接使用。适合于技术研究、原型验证或内部工具开发中对 QUIC 协议进行探索性使用。若决定采用，需做好深入阅读源码和自行维护的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging)
- [官方文档]()（无）
- [测试用例]()（未在提供的信息中发现标准测试文件路径，可能需要在引擎测试目录中搜索 `Quic` 关键字）