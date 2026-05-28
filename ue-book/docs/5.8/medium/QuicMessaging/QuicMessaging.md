# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | QUIC 消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-16 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging) | |

## 用途

QuicMessaging 插件为 Unreal Engine 的消息子系统 (`IMessaging`) 提供了一个基于 **QUIC 协议** 的传输层实现。QUIC 是一个现代的、基于 UDP 的传输协议，它内置了 TLS 1.3 加密、多路复用和连接迁移等特性。

此插件旨在解决传统 TCP/UDP 网络消息传输中的痛点：
1.  **性能与可靠性**：相比 TCP，QUIC 可以减少连接建立的延迟（0-RTT 握手），并更好地处理网络抖动和丢包。
2.  **安全性**：默认提供端到端加密（TLS 1.3），无需在应用层额外实现。
3.  **连接管理**：内置连接迁移功能，可在网络切换（如 Wi-Fi 到移动网络）时保持连接。
4.  **服务器-客户端模型**：支持标准的服务器-客户端网络拓扑，适用于需要中央协调器（如编辑器、会话主机）的场景。

它本质上是 `IMessageTransport` 接口的一个高级替代品，适用于对网络性能、安全性和可靠性有更高要求的场景，例如多人游戏会话、分布式计算或需要跨网络设备通信的工具。

## 使用场景

-   你需要为你的多人游戏或网络工具构建一个比默认 UDP 广播更可靠、更安全的消息传输层。
-   你需要实现服务器-客户端架构，其中服务器（如编辑器）需要验证连接的客户端（如移动设备或远程调试工具）。
-   你的应用需要在弱网环境下（如移动设备）保持更稳定的连接。
-   你需要对网络连接进行精细控制，例如实现连接冷却（防止暴力重连）或自定义身份验证流程。

## 蓝图用法

此插件主要提供 C++ 层面的 API 以集成到引擎的网络消息子系统中。其核心类和接口（如 `FQuicMessageTransport`, `IQuicNetworkMessagingExtension`）并非直接暴露为蓝图节点。网络消息的发送和接收通常通过引擎的 `FMessageEndpoint` 或上层网络抽象（如 `IOnlineSubsystem`）进行，而 QuicMessaging 作为底层传输层在幕后工作。

因此，**没有直接的蓝图节点**用于操作此插件。其配置和控制主要通过以下方式：
1.  **配置文件**：通过 `DefaultEngine.ini` 或编辑器项目设置中的 `UQuicMessagingSettings` 进行配置。
2.  **命令行参数**：在启动时通过 `-QUICMESSAGING_TRANSPORT_ENABLE=1` 等参数覆盖配置。
3.  **C++ 编程**：通过 `IQuicNetworkMessagingExtension` 接口在 C++ 中访问高级功能，如身份验证和连接管理。

## C++ 用法

### 头文件引入

使用此插件的核心功能，通常需要包含其公共头文件和相关模块的头文件：

```cpp
#include "QuicMessagingModule.h"
#include "IQuicNetworkMessagingExtension.h"
#include "QuicMessagingSettings.h"
```

### 基本用法

插件通过引擎的模块系统集成。当插件启用并正确配置后，它会自动注册为 `IMessageTransport` 的一个实现。

**获取插件扩展接口**
为了使用 QUIC 特有的高级功能（如身份验证），你需要获取 `IQuicNetworkMessagingExtension` 接口指针。通常通过模块加载实现。

```cpp
// 来自: IQuicNetworkMessagingExtension.h 的典型使用模式
IQuicNetworkMessagingExtension* QuicExtension = nullptr;
if (FModuleManager::Get().IsModuleLoaded("QuicMessaging"))
{
    // 获取模块并查询接口
    IQuicMessagingModule& QuicModule = FModuleManager::GetModuleChecked<IQuicMessagingModule>("QuicMessaging");
    QuicExtension = QuicModule.GetNetworkMessagingExtension();
}

if (QuicExtension)
{
    // 现在可以使用 QUIC 扩展功能
    FGuid EndpointGuid = QuicExtension->GetEndpointGuid();
    UE_LOG(LogTemp, Log, TEXT("Local QUIC Endpoint GUID: %s"), *EndpointGuid.ToString());
}
```

**配置与启动**
传输层的配置主要通过 `UQuicMessagingSettings` 完成，它通常在引擎初始化时加载。

```cpp
// 配置通常通过.ini文件或代码中的 CDO (Class Default Object) 完成
// 示例：在代码中访问设置
UQuicMessagingSettings* Settings = GetMutableDefault<UQuicMessagingSettings>();
if (Settings)
{
    Settings->EnableTransport = true;
    Settings->bIsClient = true; // 设置为客户端
    Settings->UnicastEndpoint = TEXT("0.0.0.0:0"); // 自动绑定
    Settings->MessageFormat = EQuicMessageFormat::CborPlatformEndianness;
}
```

### 进阶用法

**连接身份验证流程**
QUIC 扩展接口提供了完整的身份验证流程控制。以下是一个简化的身份验证客户端实现示例。

```cpp
// 假设已获取 IQuicNetworkMessagingExtension* QuicExtension
// 并已创建一个用于发送/接收消息的 FMessageEndpoint

void SetupAuthClient()
{
    if (!QuicExtension) return;

    // 1. 绑定接收到认证响应的委托
    QuicExtension->OnQuicMetaMessageReceived().AddLambda(
        [this](const TSharedRef<IMessageContext>& Context)
        {
            if (const FQuicAuthResponseMessage* AuthResponse = Context->GetMessage<FQuicAuthResponseMessage>())
            {
                if (AuthResponse->bAuthSuccessful)
                {
                    UE_LOG(LogTemp, Log, TEXT("Authentication successful from %s"), *AuthResponse->SenderNodeId.ToString());
                    // 开始正常游戏通信
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("Authentication failed: %s"), *AuthResponse->Reason);
                }
            }
        }
    );

    // 2. 绑定连接状态变化委托
    QuicExtension->OnClientConnectionChanged().AddLambda(
        [this](const FGuid& NodeId, const FIPv4Endpoint& Endpoint, const EQuicClientConnectionState State)
        {
            if (State == EQuicClientConnectionState::Connected)
            {
                UE_LOG(LogTemp, Log, TEXT("Connected to server. NodeId: %s, Endpoint: %s"),
                    *NodeId.ToString(), *Endpoint.ToString());
                
                // 3. 连接成功后，发送认证请求
                FQuicAuthMessage* AuthMsg = new FQuicAuthMessage();
                AuthMsg->SenderNodeId = QuicExtension->GetEndpointGuid();
                AuthMsg->Payload = TEXT("MyAuthToken123");

                // 创建消息上下文
                FQuicMetaMessageContext* MsgContext = new FQuicMetaMessageContext(AuthMsg);
                
                // 通过扩展接口发送认证消息
                QuicExtension->TransportAuthMessage(
                    MakeShareable(MsgContext),
                    NodeId // 目标服务器节点
                );
            }
            else if (State == EQuicClientConnectionState::Disconnected)
            {
                UE_LOG(LogTemp, Warning, TEXT("Disconnected from server. NodeId: %s"), *NodeId.ToString());
            }
        }
    );

    // 4. 配置并启动连接冷却（可选，服务器端通常设置）
    QuicExtension->SetConnectionCooldown(true, 5, 30, 60, 3600);
}
```

## Demo 示例

以下是一个可编译的最小示例，展示如何创建一个简单的 QUIC 网络客户端，接收服务器信息。

**QuicDemoClient.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "IQuicNetworkMessagingExtension.h"
#include "QuicTransportMessages.h"

class FQuicDemoClient
{
public:
    FQuicDemoClient();
    ~FQuicDemoClient();

    void ConnectToServer(const FString& ServerAddress);
    void Disconnect();

private:
    void HandleClientConnectionChanged(const FGuid& NodeId, const FIPv4Endpoint& Endpoint, const EQuicClientConnectionState State);
    void HandleMetaMessageReceived(const TSharedRef<IMessageContext>& Context);
    void SendAuthRequest(const FGuid& ServerNodeId);

    IQuicNetworkMessagingExtension* QuicExtension = nullptr;
    FGuid LocalEndpointGuid;
    FGuid ConnectedServerNodeId;
};
```

**QuicDemoClient.cpp**
```cpp
#include "QuicDemoClient.h"
#include "QuicMessagingModule.h"
#include "QuicMessagingSettings.h"

FQuicDemoClient::FQuicDemoClient()
{
    // 获取扩展接口
    if (FModuleManager::Get().IsModuleLoaded("QuicMessaging"))
    {
        IQuicMessagingModule& QuicModule = FModuleManager::GetModuleChecked<IQuicMessagingModule>("QuicMessaging");
        QuicExtension = QuicModule.GetNetworkMessagingExtension();
    }

    if (QuicExtension)
    {
        LocalEndpointGuid = QuicExtension->GetEndpointGuid();
        
        // 绑定委托
        QuicExtension->OnClientConnectionChanged().AddRaw(this, &FQuicDemoClient::HandleClientConnectionChanged);
        QuicExtension->OnQuicMetaMessageReceived().AddRaw(this, &FQuicDemoClient::HandleMetaMessageReceived);
    }
}

FQuicDemoClient::~FQuicDemoClient()
{
    Disconnect();
    if (QuicExtension)
    {
        QuicExtension->OnClientConnectionChanged().RemoveAll(this);
        QuicExtension->OnQuicMetaMessageReceived().RemoveAll(this);
    }
}

void FQuicDemoClient::ConnectToServer(const FString& ServerAddress)
{
    // 配置并启用传输
    UQuicMessagingSettings* Settings = GetMutableDefault<UQuicMessagingSettings>();
    if (Settings)
    {
        Settings->EnableTransport = true;
        Settings->bIsClient = true;
        Settings->UnicastEndpoint = TEXT("0.0.0.0:0");
        // 添加服务器为静态端点，以便发现
        Settings->StaticEndpoints.Add(ServerAddress);
    }
    
    UE_LOG(LogTemp, Log, TEXT("QUIC Client initialized. Waiting for connection to %s"), *ServerAddress);
}

void FQuicDemoClient::Disconnect()
{
    if (QuicExtension && ConnectedServerNodeId.IsValid())
    {
        QuicExtension->DisconnectNode(ConnectedServerNodeId);
        ConnectedServerNodeId.Invalidate();
    }
}

void FQuicDemoClient::HandleClientConnectionChanged(const FGuid& NodeId, const FIPv4Endpoint& Endpoint, const EQuicClientConnectionState State)
{
    if (State == EQuicClientConnectionState::Connected)
    {
        ConnectedServerNodeId = NodeId;
        UE_LOG(LogTemp, Log, TEXT("Connected to server %s at %s"), *NodeId.ToString(), *Endpoint.ToString());
        // 连接成功后自动发送认证请求
        SendAuthRequest(NodeId);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Disconnected from server %s"), *NodeId.ToString());
        ConnectedServerNodeId.Invalidate();
    }
}

void FQuicDemoClient::HandleMetaMessageReceived(const TSharedRef<IMessageContext>& Context)
{
    if (const FQuicAuthResponseMessage* AuthResponse = Context->GetMessage<FQuicAuthResponseMessage>())
    {
        if (AuthResponse->bAuthSuccessful)
        {
            UE_LOG(LogTemp, Log, TEXT("Server authenticated us! Ready for game data."));
            // 此处可以开始发送/接收游戏特定消息
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Server rejected authentication: %s"), *AuthResponse->Reason);
        }
    }
}

void FQuicDemoClient::SendAuthRequest(const FGuid& ServerNodeId)
{
    if (!QuicExtension) return;

    FQuicAuthMessage* AuthMessage = new FQuicAuthMessage();
    AuthMessage->SenderNodeId = LocalEndpointGuid;
    AuthMessage->Payload = TEXT("MySecretToken"); // 替换为实际的认证令牌

    // 创建上下文（注意：QuicMetaMessageContext的构造函数会接管Message指针的所有权）
    FQuicMetaMessageContext* MsgContext = new FQuicMetaMessageContext(AuthMessage);
    
    QuicExtension->TransportAuthMessage(
        MakeShareable(MsgContext),
        ServerNodeId
    );
    
    UE_LOG(LogTemp, Log, TEXT("Sent auth request to server %s"), *ServerNodeId.ToString());
}
```

## 模块依赖

要使用 QuicMessaging 插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `QuicMessaging` | 插件核心运行时模块，提供传输层实现。 |
| `QuicMessagingTransport` | QUIC 协议的具体传输实现，依赖 MsQuic 库。 |
| `Networking` | 提供基础的网络类型（如 `FIPv4Endpoint`）和套接字支持。 |
| `Crypto` | 提供加密、证书处理等功能，QUIC 传输层加密所需。 |

**注意**：由于此插件默认禁用 (`EnabledByDefault: false`)，你需要在你的 `.uplugin` 文件中显式声明对它的依赖，或者在项目的 `.uproject` 文件的 `Plugins` 数组中将其 `Enabled` 属性设为 `true`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化说明符与参数位数不匹配（32位/64位）的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-02-03 | `20825e79` | Fix duplicate symbol linker errors | 修复了导致链接器错误的重复符号问题。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 解决了忽略带有 `[[nodiscard]]` 属性的函数返回值的问题。 |

### 维护评价

-   **状态**：**维护中**。插件创建于2023年中，距今约两年。最近一次提交在2026年4月，表明它仍在持续维护中。
-   **活跃度**：近期更新主要是编译修复、日志规范和小问题修正，没有重大功能变更，这可能意味着核心功能已趋于稳定。
-   **风险提示**：该插件位于 `Experimental` 文件夹中，并且 `EnabledByDefault` 为 `false`，表明 Epic 将其视为实验性功能。虽然仍在维护，但 **API 和行为可能在未来版本中发生变化或被移除**。不建议在对稳定性要求极高的生产项目中作为核心依赖。
-   **推荐**：如果你正在探索高性能、安全的自定义网络方案，并且愿意承担实验性插件的风险，那么可以尝试使用它。对于常规多人游戏开发，通常仍建议优先使用 `OnlineSubsystem` 和 `Replication` 系统。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/QuicMessaging)
-   [官方文档]() (无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/QuicMessaging/Source/QuicMessaging/Private/Tests/)