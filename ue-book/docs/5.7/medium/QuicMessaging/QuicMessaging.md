# QUIC Messaging

> Adds a QUIC based transport layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | QUIC消息传输 |
| 分类 | Messaging |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `QuicMessaging` (Runtime), `QuicMessagingTransport` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-10-11 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging) | |

## 用途

该插件为 Unreal Engine 的 `MessageBus` 消息子系统提供基于 QUIC 协议的网络传输层。QUIC 是一种基于 UDP 的现代传输协议，具有低延迟、多路复用、0-RTT 握手、连接迁移及内置加密（TLS 1.3）等特性。

插件允许 UE 的网络消息以 QUIC 格式编码并通过 QUIC 连接发送，替代默认的 UDP 或 TCP 传输。它专注于高性能、低延迟且可靠的双向消息通信，适用于对实时性要求较高的场景，例如多人游戏、实时协作工具、远程控制、数据同步等。

核心功能包括：
- **QUIC 协议传输**：使用 [MsQuic](https://github.com/microsoft/msquic) 库作为底层 QUIC 实现。
- **消息序列化**：支持 CBOR 格式（平台字节序或标准大端序），高效且可互操作。
- **客户端/服务器模式**：插件可配置为客户端或服务器端点。
- **连接管理**：自动重连、心跳检测、发现超时。
- **认证机制**：可选的服务器端身份验证（支持自定义认证消息）。
- **流量控制**：通过 `INetworkMessagingExtension` 接口暴露传输统计信息（丢包率、延迟等）。
- **安全传输**：QUIC 默认启用加密（TLS 1.3）。

## 使用场景

- **实时多人游戏**：需要低延迟、可靠且安全的房间/世界状态同步。
- **远程编辑与协作**：例如 Live Link、多用户编辑（Multi-User Editing）等需要高频、低抖动数据传输的工具。
- **分布式系统通信**：在微服务或集群节点间传递指令、状态通知。
- **边缘计算/物联网**：设备与服务器间通过 QUIC 保持高效长连接。

## 蓝图用法

该插件主要为 C++ 开发者设计，目前**没有对外公开的 BlueprintCallable 函数或 Blueprint 节点**。所有与 QUIC 传输的交互均通过 C++ 接口（`IQuicNetworkMessagingExtension`、`FQuicMessageTransport`）和 `MessageBus` 系统间接完成。若需在蓝图层面使用消息传输，请配合 `Messaging Component`（来自 `Messaging` 模块的蓝图节点）使用，但传输层细节由本插件在后台处理。

## C++ 用法

### 头文件引入

```cpp
#include "IMessageBus.h"
#include "IMessageTransport.h"
#include "IQuicNetworkMessagingExtension.h"
#include "QuicMessagingSettings.h"
```

### 基本用法：启动 QUIC 传输并发送消息

```cpp
// 1. 获取消息总线
IMessageBusPtr MessageBus = IMessagingModule::Get().GetDefaultBus();

// 2. 创建 QUIC 传输实例（以客户端模式为例）
TSharedRef<FQuicEndpointConfig> EndpointConfig = MakeShared<FQuicEndpointConfig>();
EndpointConfig->bIsClient = true;
EndpointConfig->bEncryption = true;
EndpointConfig->DiscoveryTimeoutSeconds = 5;

TArray<FIPv4Endpoint> StaticEndpoints;
StaticEndpoints.Add(FIPv4Endpoint(FIPv4Address(192, 168, 1, 100), 9001));

TSharedPtr<FQuicMessageTransport, ESPMode::ThreadSafe> QuicTransport =
    MakeShared<FQuicMessageTransport, ESPMode::ThreadSafe>(true, EndpointConfig, StaticEndpoints);

// 3. 注册传输到消息总线
MessageBus->RegisterTransport(QuicTransport);

// 4. 发送消息（通过 MessageBus 标准接口）
IMutableMessageContextRef Context = MessageBus->CreateMessageContext();
Context->SetMessage(MakeShared<FMyMessage>(...));
Context->AddRecipient(FMessageAddress::Parse("myNodeId"));
MessageBus->SendMessage(Context);
```

*来源：结合 `FQuicMessageTransport` 构造函数及 `IMessageBus` 接口推导。*

### 进阶用法：获取传输统计信息

```cpp
// 通过 IQuicNetworkMessagingExtension 接口获取节点统计
if (IQuicNetworkMessagingExtension* Ext = IModularFeatures::Get().GetModularFeature<IQuicNetworkMessagingExtension>(IQuicNetworkMessagingExtension::ModularFeatureName))
{
    FMessageTransportStatistics Stats = Ext->GetLatestStatistics(NodeId);
    UE_LOG(LogTemp, Log, TEXT("Latency: %.2f ms, PacketLoss: %.3f%%"), Stats.AverageRoundTripTime, Stats.PacketLossPercentage);
}
```

### 配置认证与连接冷却

```cpp
IQuicNetworkMessagingExtension* Ext = ...;
Ext->SetMaxAuthenticationMessageSize(4096);
Ext->SetConnectionCooldown(true, 3, 60, 10, 120);  // 60秒内允许3次尝试，冷却10秒，最大冷却120秒
Ext->SetNodeAuthenticated(NodeId);
```

*来源：`IQuicNetworkMessagingExtension` 头文件。*

## Demo 示例

以下是一个最小 C++ 模块，展示如何创建 QUIC 传输并接收消息。

### QuicDemo.h

```cpp
#pragma once
#include "Modules/ModuleManager.h"

class FQuicDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<FQuicMessageTransport, ESPMode::ThreadSafe> QuicTransport;
    FDelegateHandle OnMessageReceivedHandle;
};
```

### QuicDemo.cpp

```cpp
#include "QuicDemo.h"
#include "IMessageBus.h"
#include "IMessagingModule.h"
#include "IMessageTransport.h"
#include "QuicMessageTransport.h"
#include "QuicEndpointConfig.h"
#include "QuicMessagingSettings.h"
#include "QuicTransportNotifications.h"

IMPLEMENT_MODULE(FQuicDemoModule, QuicDemo)

void FQuicDemoModule::StartupModule()
{
    // 创建传输
    TSharedRef<FQuicEndpointConfig> Config = MakeShared<FQuicEndpointConfig>();
    Config->bIsClient = true;
    Config->bEncryption = true;
    Config->bAutoRepair = true;
    Config->DiscoveryTimeoutSeconds = 5;

    TArray<FIPv4Endpoint> StaticEndpoints;
    // 假设已知服务器地址
    StaticEndpoints.Add(FIPv4Endpoint(FIPv4Address(10, 0, 0, 1), 9001));

    QuicTransport = MakeShared<FQuicMessageTransport, ESPMode::ThreadSafe>(true, Config, StaticEndpoints);

    // 获取默认消息总线并注册传输
    IMessageBusPtr Bus = IMessagingModule::Get().GetDefaultBus();
    Bus->RegisterTransport(QuicTransport.ToSharedRef());

    // 监听客户端连接状态变化
    FOnQuicClientConnectionChanged& ConnectionDelegate = QuicTransport->OnClientConnectionChanged();
    ConnectionDelegate.AddRaw(this, [](const FGuid& NodeId, const FIPv4Endpoint& RemoteEndpoint, EQuicClientConnectionState State)
    {
        UE_LOG(LogTemp, Log, TEXT("QUIC client %s to %s"), 
               State == EQuicClientConnectionState::Connected ? TEXT("connected") : TEXT("disconnected"),
               *RemoteEndpoint.ToString());
    });

    // 接收消息（需通过消息总线订阅，此处略）
}

void FQuicDemoModule::ShutdownModule()
{
    if (IMessageBusPtr Bus = IMessagingModule::Get().GetDefaultBus())
    {
        Bus->UnregisterTransport(QuicTransport.ToSharedRef());
    }
    QuicTransport.Reset();
}
```

## 模块依赖

要使用本插件中的任何一个模块，你的模块需要在 `Build.cs` 中添加以下依赖（仅列出独特依赖，标准 Core/Engine/Slate 等省略）：

| 模块 | 用途 |
|---|---|
| `Messaging` | 提供消息总线基础架构（`IMessageBus`, `IMessageContext` 等） |
| `MessagingCommon` | 消息传输辅助类 |
| `Networking` | 网络基础（`FIPv4Endpoint` 等） |
| `Sockets` | 底层套接字支持 |
| `MsQuic` (第三方) | QUIC 协议实现（包含在插件 `Binaries/ThirdParty/` 中，无需额外链接） |

**注意**：`QuicMessagingTransport` 模块内部链接了 MsQuic 库，使用本插件时无需手动配置 MsQuic。

## 维护状态

### 近期更新

| 日期 | Hash | 原始 Commit 解读 |
|---|---|---|
| 2025-09-12 | `ce6ff392` | 处理“忽略 nodiscard 函数返回值”警告 |
| 2025-03-13 | `b059f7b4` | 修复无用不可达代码警告 |
| 2024-06-12 | `e7a04268` | 替换 `EAutomationTestFlags::ApplicationContextMask` 为 `EAutomationTestFlags_ApplicationContextMa` |
| 2023-10-16 | `572e87bd` | 重命名 `LiveLinkHubLauncher` 为 `LiveLinkHub`（间接影响） |
| 2023-10-11 | `00d774b9` | 修复因某些模块检查目标类型编辑器而非……导致的 LiveLinkHub 编译错误（首次提交） |

### 维护评价

- **创建时间**：2023-10-11，至今约2年。
- **最近更新频率和内容**：2025 年有两次编译警告修复，2024 年有自动化测试标记更新，无功能性新增。
- **活跃程度**：**维护不活跃**。自2024年3月以来无实质性功能更新，仅修复编译问题。插件仍处于“Experimental”状态，且默认禁用（`EnabledByDefault=false`）。
- **已知问题**：未提供官方文档（`DocsURL` 为空），部分 API 命名可能随版本变化。
- **推荐使用**：**谨慎使用**。适用于对 QUIC 传输有强烈需求且能自行维护的团队。若你的项目需要稳定可靠的即时消息传输，建议优先使用内置的 UDP/TCP 传输，或等待该插件进入正式版。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/QuicMessaging)
- [官方文档](https://docs.unrealengine.com)（搜索“QUIC Messaging”）
- [测试类型](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/QuicMessaging/Source/QuicMessaging/Private/Tests/QuicMessagingTestTypes.h)
- [MsQuic 官方](https://github.com/microsoft/msquic)