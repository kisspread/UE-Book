# UDP Messaging

> Adds a UDP based transport and tunneling layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 中文名 | UDP 消息传输 |
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UdpMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/UdpMessaging) | |

## 用途

UdpMessaging 为 Unreal Engine 的消息子系统（Messaging Subsystem）提供了基于 UDP 的网络传输层。它是 UE5 内部 `FMessageEndpoint` / `IMessageBus` 架构的底层网络实现，解决了以下核心问题：

1. **跨机器消息传递**：允许不同计算机上的 UE 实例（编辑器、游戏进程、工具等）通过 UDP 多播/单播相互发送结构化消息，用于远程控制、分布式处理等场景。
2. **网络隧道桥接**：提供 TCP 隧道功能，可将 UDP 消息封装在 TCP 连接中传输，解决跨子网（如移动设备通过 WiFi 连接）无法直接进行 UDP 多播的问题。
3. **可靠传输协议**：内置消息分段、重组、确认、重传等机制，在 UDP 之上构建了可靠的有序消息传递，包含 AIMD 拥塞控制和自适应 RTT 计算。
4. **消息序列化格式**：支持 CBOR 编码（平台字节序和标准字节序两种模式），提供高效的二进制序列化。

## 使用场景

- 你需要在局域网中的多台机器上协同工作（如多编辑器联动、远程控制 PIE） → 启用 UdpMessaging，所有实例自动通过多播发现并通信
- 你需要让移动设备（手机/平板）与桌面上的编辑器通信（如远程预览、Live Coding on device） → 配置 StaticEndpoints 或启用 Tunnel 连接
- 你在开发需要进程间通信的分布式工具（如 Shader Compiler Farm、资产管理管线） → 通过 FMessageEndpoint 发送/接收 UDP 消息
- 你需要在跨子网环境中使用消息系统 → 启用 Tunnel 功能通过 TCP 中转 UDP 消息

## 蓝图用法

UdpMessaging 插件本身**不暴露任何蓝图节点**。它是 Messaging Subsystem 的底层传输实现，蓝图层面的使用通过 UE 内置的消息系统完成：

- 蓝图中使用 **Event Dispatcher** 和 **Messaging** 节点（如游戏内 RPC）
- 编辑器中通过 **Settings → Plugins → UDP Messaging** 面板配置参数

所有关键设置（`UUdpMessagingSettings`）均通过编辑器项目设置面板暴露，可配置：

| 设置项 | 说明 |
|---|---|
| `EnableTransport` | 是否启用 UDP 传输通道 |
| `UnicastEndpoint` | 本地监听端点（IP:Port） |
| `MulticastEndpoint` | 多播组端点（IP:Port） |
| `MessageFormat` | 消息编码格式（CBOR 平台字节序/标准字节序） |
| `StaticEndpoints` | 静态设备端点列表（用于跨子网通信） |
| `ExcludedEndpoints` | 被屏蔽的 IP 地址列表（支持通配符） |
| `MaxSendRate` | 最大持续发送速率（Gbit/s） |
| `MaxPacketSize` | 每个消息段的最大包大小 |
| `ConnectionTimeoutPeriod` | 连接超时时间（秒） |
| `EnableTunnel` | 是否启用 TCP 隧道 |
| `TunnelUnicastEndpoint` | 隧道本地监听端点 |
| `RemoteTunnelEndpoints` | 远程隧道节点端点列表 |

### 命令行覆盖

关键设置可通过命令行参数覆盖：

```
-UDPMESSAGING_TRANSPORT_ENABLE=1
-UDPMESSAGING_TRANSPORT_UNICAST=0.0.0.0:0
-UDPMESSAGING_TRANSPORT_MULTICAST=230.0.0.1:6666
```

## C++ 用法

UdpMessaging 的 C++ 接口主要是 `IUdpMessageTunnel` 和 `IUdpMessageTunnelConnection`，用于程序化控制 TCP 隧道。

### 头文件引入

```cpp
#include "IUdpMessageTunnel.h"
#include "IUdpMessageTunnelConnection.h"
#include "UdpMessagingSettings.h"
```

### 基本用法 — 通过 Messaging Subsystem 发送消息

UdpMessaging 作为传输层自动挂载到消息总线上，你通常不需要直接调用它的 API，而是使用 UE 的消息端点：

```cpp
#include "IMessagingModule.h"
#include "MessageEndpoint.h"
#include "MessageEndpointBuilder.h"

// 定义消息结构
USTRUCT()
struct FMyNetworkMessage
{
    GENERATED_BODY()

    UPROPERTY()
    FString Payload;
};

// 创建消息端点（UdpMessaging 作为传输层自动参与）
TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> Endpoint =
    FMessageEndpoint::Builder("MyService")
        .Handling<FMyNetworkMessage>(this, &UMyClass::HandleMessage);

// 广播消息到所有已发现的节点
Endpoint->Publish(new FMyNetworkMessage{TEXT("Hello from UDP")});

// 发送到特定地址
FMessageAddress RecipientAddress;
FMessageAddress::Parse(TEXT("..."), RecipientAddress);
Endpoint->Send(new FMyNetworkMessage{TEXT("Direct message")}, RecipientAddress);
```

### 基本用法 — 隧道（Tunnel）API

```cpp
#include "IUdpMessageTunnel.h"
#include "IPv4Address.h"

// 获取隧道接口（通过模块获取）
IUdpMessageTunnel* Tunnel = /* 通过 IUdpMessageTunnel 接口获取 */;

// 启动隧道服务器，监听本地端口
Tunnel->StartServer(FIPv4Endpoint(FIPv4Address::Any, 19876));

// 连接到远程隧道
Tunnel->Connect(FIPv4Endpoint(FIPv4Address(192, 168, 1, 100), 19876));

// 获取所有连接
TArray<TSharedPtr<IUdpMessageTunnelConnection>> Connections;
int32 Count = Tunnel->GetConnections(Connections);

for (auto& Conn : Connections)
{
    if (Conn->IsOpen())
    {
        FText Name = Conn->GetName();
        FTimespan Uptime = Conn->GetUptime();
        uint64 BytesReceived = Conn->GetTotalBytesReceived();
        uint64 BytesSent = Conn->GetTotalBytesSent();
    }
}

// 监听连接变化
Tunnel->OnConnectionsChanged().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("Tunnel connections changed"));
});
```

### 进阶用法 — 读取传输统计

```cpp
#include "UdpMessagingSettings.h"

// 读取当前设置
UUdpMessagingSettings* Settings = GetMutableDefault<UUdpMessagingSettings>();

// 检查当前编码格式
EUdpMessageFormat Format = Settings->MessageFormat;

// 获取最大发送速率（自动钳制到合法范围）
float MaxRate = Settings->GetMaxSendRate();  // 0.01 ~ 100.0 Gbit/s

// 获取最大包大小（自动钳制到合法范围）
uint16 PacketSize = Settings->GetMaxPacketSize();  // 576 ~ 65535
```

## Demo 示例

以下示例展示如何编写一个独立的 C++ 模块，通过 UdpMessaging 消息总线发送和接收自定义消息：

### MyNetworkMessage.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/ObjectMacros.h"
#include "MyNetworkMessage.generated.h"

USTRUCT()
struct FMyNetworkMessage
{
    GENERATED_BODY()

    UPROPERTY()
    FString Text;

    UPROPERTY()
    int32 Value = 0;

    UPROPERTY()
    TArray<uint8> Payload;
};
```

### MyNetworkService.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MessageEndpoint.h"
#include "MyNetworkMessage.h"
#include "MyNetworkService.generated.h"

UCLASS(ClassGroup=(Messaging), meta=(BlueprintSpawnableComponent))
class UMyNetworkService : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 发送消息到所有已发现节点 */
    UFUNCTION(BlueprintCallable, Category = "Network")
    void BroadcastMessage(const FString& Text, int32 Value);

private:
    void HandleMyNetworkMessage(const FMyNetworkMessage& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context);

    TSharedPtr<FMessageEndpoint, ESPMode::ThreadSafe> Endpoint;
};
```

### MyNetworkService.cpp

```cpp
#include "MyNetworkService.h"
#include "MessageEndpointBuilder.h"

void UMyNetworkService::BeginPlay()
{
    Super::BeginPlay();

    // 创建消息端点，UdpMessaging 传输层会自动参与
    Endpoint = FMessageEndpoint::Builder("MyNetworkService")
        .Handling<FMyNetworkMessage>(this, &UMyNetworkService::HandleMyNetworkMessage);

    if (Endpoint.IsValid())
    {
        // 订阅 FMyNetworkMessage 消息类型
        Endpoint->Subscribe<FMyNetworkMessage>();
    }
}

void UMyNetworkService::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Endpoint.Reset();
    Super::EndPlay(EndPlayReason);
}

void UMyNetworkService::BroadcastMessage(const FString& Text, int32 Value)
{
    if (Endpoint.IsValid())
    {
        FMyNetworkMessage* Msg = new FMyNetworkMessage();
        Msg->Text = Text;
        Msg->Value = Value;

        // Publish 广播到所有订阅者（包括其他机器上的实例）
        Endpoint->Publish(Msg);
    }
}

void UMyNetworkService::HandleMyNetworkMessage(
    const FMyNetworkMessage& Message,
    const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
{
    UE_LOG(LogTemp, Log,
        TEXT("Received from %s: Text='%s', Value=%d"),
        *Context->GetSender().ToString(),
        *Message.Text,
        Message.Value);
}
```

## 模块依赖

从 Build.cs 分析，UdpMessaging 模块依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Sockets` | UDP 套接字操作 |
| `Networking` | 网络地址和基础网络设施 |
| `MessagingCommon` | 消息系统公共类型和序列化 |
| `Serialization` | CBOR/JSON 序列化支持 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double-to-float 截断警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-13 | `015f61a1` | Fixed a bunch of unreachable code warnings causing errors on some targets | 修复部分目标平台上不可达代码警告导致的编译错误 |
| 2026-01-14 | `a13b59ad` | UdpMessaging: Implement token bucket send pacing. | 实现令牌桶算法进行发送速率控制 |
| 2025-12-11 | `ca4a6ebe` | UdpMessaging: Add MessagingInsights plugin for Unreal Insights, and corresponding instrumentation. | 新增 MessagingInsights 插件集成 Unreal Insights 性能分析 |

### 维护评价

UdpMessaging 是 Unreal Engine 最核心的基础设施插件之一，**持续活跃维护**：

- **年龄**：创建于 2014 年，已有 12 年历史，是 UE 消息系统的基石
- **近期活跃度**：2025-2026 年有多次实质性功能更新（令牌桶发送控制、Unreal Insights 集成），以及持续的编译器兼容性修复
- **协议版本**：当前协议版本为 18（`UDP_MESSAGING_TRANSPORT_PROTOCOL_VERSION`），说明协议经历了多次迭代
- **向后兼容**：代码中保留了对协议版本 10/11 的序列化兼容处理
- **推荐使用**：✅ **强烈推荐**。这是 UE 消息系统的默认 UDP 传输实现，默认启用且无需额外配置。局域网内多实例通信、移动设备远程预览、分布式工具链等场景均依赖此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/UdpMessaging)
- 官方文档：无
- 测试用例：`Engine/Plugins/Messaging/UdpMessaging/Source/UdpMessaging/Private/Tests/`