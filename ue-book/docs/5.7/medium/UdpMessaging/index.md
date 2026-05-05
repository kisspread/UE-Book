# UDP Messaging

> Adds a UDP based transport and tunneling layer to the messaging sub-system for sending and receiving messages between networked computers and devices.

| 属性 | 值 |
|---|---|
| 分类 | Messaging |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `UdpMessaging` (RuntimeAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/UdpMessaging) | |

## 用途

UDP Messaging 是 UE 消息总线（MessageBus）的 UDP 传输层实现，负责在网络中的不同进程、不同设备之间传递消息。它解决了"如何让运行在同一局域网内的多个 UE 实例（编辑器、独立进程、设备）互相发现并交换消息"的问题。

该插件提供两个核心子系统：

1. **Transport（传输层）**：基于 UDP 多播（multicast）和单播（unicast）的消息传输。在局域网内通过多播自动发现节点，通过单播实现点对点可靠/不可靠消息传递。支持消息分段、重组、重传、拥塞控制（AIMD 算法）等机制，可以传输远超单个 UDP 数据报大小的消息。

2. **Tunnel（隧道层）**：将 UDP 消息封装在 TCP 连接中传输，用于跨子网或无法直接使用 UDP 多播的场景。隧道服务在桌面平台运行，作为 TCP 服务器接受远程连接，在本地通过 UDP 多播与消息总线通信。

该插件以 `INetworkMessagingExtension` 模块化特性的形式注册自身，使得 MessageBridge 可以自动使用 UDP 传输。

## 使用场景

- 你在做多人协作编辑（Multi-User Editing），需要在局域网内的多个编辑器实例之间同步消息 → 使用 Transport 的多播发现和消息传递
- 你需要跨子网连接两组 UE 实例（例如移动设备在不同网段） → 配置 Tunnel 或使用 StaticEndpoints
- 你的 Standalone Slate 应用需要与编辑器通信 → UDP Messaging 默认在非游戏程序中启用
- 你需要 UnrealInsights、LiveLinkHub 等工具之间的消息传递 → 该插件已在 `SupportedPrograms` 中声明支持这些程序
- 你需要消息的可靠传输（保证送达）或不可靠传输（允许丢包） → 消息标志 `EMessageFlags::Reliable` 控制

## 蓝图用法

该插件没有暴露 BlueprintCallable 节点。所有配置通过 **项目设置 → Plugins → UDP Messaging** 完成。

### 设置面板（编辑器）

在编辑器中通过 **Project Settings → Plugins → UDP Messaging** 可以配置：

| 设置项 | 说明 |
|---|---|
| **Availability: Enabled By Default** | 是否默认启用 UDP 消息（非编辑器构建需要 `-messaging` 命令行参数） |
| **Transport: Enable Transport** | 启用/禁用 UDP 传输层 |
| **Transport: Unicast Endpoint** | 本地单播端点，格式 `IP:PORT`，`0.0.0.0:0` 表示默认 |
| **Transport: Multicast Endpoint** | 多播组端点，格式 `IP:PORT`，默认 `230.0.0.1:6666` |
| **Transport: Message Format** | 消息序列化格式：CBOR (Platform Endianness) 或 CBOR (Standard Endianness) |
| **Transport: Static Endpoints** | 静态设备端点列表，用于跨子网通信 |
| **Transport: Excluded Endpoints** | 排除的 IP 地址列表，支持通配符 `*` 和 `?` |
| **Tunnel: Enable Tunnel** | 启用/禁用 UDP 隧道 |
| **Tunnel: Tunnel Unicast Endpoint** | 隧道本地监听端点 |
| **Tunnel: Remote Tunnel Endpoints** | 远程隧道服务器端点列表 |

### 控制台命令

在运行时可以通过控制台命令管理 UDP Messaging：

```
UDPMESSAGING STATUS     -- 显示传输层和隧道层的状态信息
UDPMESSAGING RESTART    -- 重启消息桥和隧道服务
UDPMESSAGING SHUTDOWN   -- 关闭消息桥和隧道服务
```

## C++ 用法

### 架构概览

```
FUdpMessagingModule (模块入口)
├── FUdpMessageTransport (IMessageTransport 实现)
│   ├── FUdpMessageProcessor (独立线程，处理收发)
│   │   ├── FUdpMessageBeacon (节点发现 Hello/Bye)
│   │   ├── FUdpMessageSegmenter (消息分段发送)
│   │   ├── FUdpMessageResequencer (消息重排序)
│   │   └── FSocketSender (异步 UDP 发送)
│   ├── FUdpSerializedMessage (序列化消息)
│   ├── FUdpReassembledMessage (重组消息)
│   └── FUdpDeserializedMessage (反序列化消息)
├── FUdpMessageTunnel (TCP 隧道, 仅桌面平台)
│   └── FUdpMessageTunnelConnection (隧道连接)
└── UUdpMessagingSettings (UObject 配置)
```

### 核心消息段类型

UDP 协议定义了以下段类型（`EUdpMessageSegments`）：

| 段类型 | 说明 |
|---|---|
| `Hello` | 节点加入通知（Beacon 发送） |
| `Bye` | 节点离开通知 |
| `Data` | 消息数据段 |
| `Acknowledge` | 整条消息确认 |
| `AcknowledgeSegments` | 单独段确认 |
| `Retransmit` | 请求重传指定段 |
| `Abort` | 中止消息发送 |
| `Timeout` | 入站消息超时通知 |
| `Ping` / `Pong` | 静态端点发现 |
| `Mesh` | 共享已知端点列表 |

### 命令行参数

可以通过命令行覆盖设置：

```
-messaging                              -- 强制启用消息传递
-UDPMESSAGING_TRANSPORT_ENABLE=1        -- 启用/禁用传输
-UDPMESSAGING_TRANSPORT_UNICAST=0.0.0.0:0  -- 单播端点
-UDPMESSAGING_TRANSPORT_MULTICAST=230.0.0.1:6666  -- 多播端点
-UDPMESSAGING_TRANSPORT_STATIC=192.168.1.10:6666  -- 静态端点（逗号分隔）
-UDPMESSAGING_WORK_QUEUE_SIZE=1024      -- 工作队列大小
-UDPMESSAGING_SHARE_KNOWN_NODES=1       -- 与活跃连接共享已知节点
```

### 控制台变量

| CVar | 默认值 | 说明 |
|---|---|---|
| `MessageBus.UDP.MaxRetriesForBadEndpoint` | 5 | 错误端点最大重试次数 |
| `MessageBus.UDP.BadEndpointPeriod` | 60 | 判定错误端点的时间窗口（秒） |
| `MessageBus.UDP.EndpointDenyListEnabled` | true | 是否启用端点拒绝列表 |
| `MessageBus.UDP.ClearDenyList` | — | 控制台命令，清除拒绝列表 |

### 关键常量

| 常量 | 值 | 说明 |
|---|---|---|
| `UDP_MESSAGING_TRANSPORT_PROTOCOL_VERSION` | 17 | 当前协议版本 |
| `UDP_MESSAGING_DEFAULT_MULTICAST_ENDPOINT` | `230.0.0.1:6666` | 默认多播地址 |
| `UDP_MESSAGING_SEGMENT_SIZE` | 1024 | 每个 UDP 段的数据大小 |
| `UDP_MESSAGING_RECEIVE_BUFFER_SIZE` | 2 MB | Socket 接收缓冲区大小 |
| `UDP_MESSAGING_MAX_RECIPIENTS` | 1024 | 单条消息最大接收者数量 |
| `UDP_MESSAGING_MAX_ANNOTATIONS` | 128 | 单条消息最大注解数量 |

### 消息传输可靠性机制

该插件实现了类似 TCP 的可靠传输机制：

1. **AIMD 拥塞控制**：使用 Additive Increase / Multiplicative Decrease 算法动态调整发送窗口大小（`WindowSize`），最小 64，最大可配置（默认 2048）
2. **RTT 估算**：加权移动平均计算往返时间，权重 0.6
3. **丢包检测**：超过 2 倍平均 RTT 未收到 ACK 的段标记为丢失并重传
4. **可靠/不可靠模式**：通过 `EMessageFlags::Reliable` 标志控制，不可靠消息不等待 ACK
5. **工作队列调度**：可靠消息和不可靠消息分别排队，按优先级轮询发送（可靠队列优先级默认 75%）
6. **发送速率限制**：`MaxSendRate` 控制最大发送速率（默认 1 Gbit/s）
7. **自动修复**：`bAutoRepair` 启用传输层错误后自动重连

### 模块初始化流程

`FUdpMessagingModule::StartupModule()` 的执行流程：

1. 检查 `IsSupportEnabled()` — 非 Shipping 构建或显式启用时才初始化
2. 加载 `Networking` 模块依赖
3. 在编辑器中注册 Project Settings 面板和自定义属性布局
4. 解析命令行参数覆盖设置
5. 调用 `RestartServices()` 创建 MessageBridge 和 MessageTunnel
6. 注册 `INetworkMessagingExtension` 模块化特性

### 头文件引入

```cpp
// 公共接口
#include "IUdpMessageTunnel.h"
#include "IUdpMessageTunnelConnection.h"
#include "Shared/UdpMessagingSettings.h"

// 消息模块日志
#include "UdpMessagingPrivate.h"  // DECLARE_LOG_CATEGORY_EXTERN(LogUdpMessaging)
```

### 基本用法：通过 INetworkMessagingExtension 交互

该模块注册为 `INetworkMessagingExtension` 模块化特性，可以通过模块化特性接口动态添加/移除静态端点：

```cpp
// 获取 UDP Messaging 扩展
IModularFeatures& ModularFeatures = IModularFeatures::Get();
if (ModularFeatures.IsModularFeatureAvailable(INetworkMessagingExtension::ModularFeatureName))
{
    INetworkMessagingExtension& Extension = ModularFeatures.GetModularFeature<INetworkMessagingExtension>(
        INetworkMessagingExtension::ModularFeatureName);
    
    // 动态添加一个静态端点
    Extension.AddEndpoint(TEXT("192.168.1.100:6666"));
    
    // 获取当前已知端点
    TArray<FString> KnownEndpoints = Extension.GetKnownEndpoints();
    
    // 获取监听地址
    TArray<FString> ListeningAddresses = Extension.GetListeningAddresses();
    
    // 获取网络统计信息
    if (Extension.CanProvideNetworkStatistics())
    {
        FGuid NodeId = Extension.GetNodeIdFromAddress(SomeMessageAddress);
        FMessageTransportStatistics Stats = Extension.GetLatestNetworkStatistics(NodeId);
    }
    
    // 移除端点
    Extension.RemoveEndpoint(TEXT("192.168.1.100:6666"));
}
```
*来源: `UdpMessagingModule.cpp` — `FUdpMessagingModule` 实现 `INetworkMessagingExtension`*

### 隧道用法（仅桌面平台）

```cpp
#include "IUdpMessageTunnel.h"
#include "IUdpMessageTunnelConnection.h"

// 通过模块化特性获取隧道接口（需要自行持有引用）
// 通常通过 FUdpMessagingModule 内部使用，外部一般不直接访问
// 但接口是 Public 的，理论上可自行构造 FUdpMessageTunnel

TSharedPtr<IUdpMessageTunnel> Tunnel = MakeShareable(
    new FUdpMessageTunnel(UnicastEndpoint, MulticastEndpoint));

// 启动隧道服务器
Tunnel->StartServer(FIPv4Endpoint(FIPv4Address(0, 0, 0, 0), 5678));

// 连接到远程隧道
Tunnel->Connect(FIPv4Endpoint(FIPv4Address(10, 0, 0, 1), 5678));

// 获取连接信息
TArray<TSharedPtr<IUdpMessageTunnelConnection>> Connections;
int32 NumConnections = Tunnel->GetConnections(Connections);

for (const auto& Connection : Connections)
{
    FText Name = Connection->GetName();
    bool bOpen = Connection->IsOpen();
    FTimespan Uptime = Connection->GetUptime();
    uint64 BytesReceived = Connection->GetTotalBytesReceived();
    uint64 BytesSent = Connection->GetTotalBytesSent();
}

// 统计
uint64 TotalIn = Tunnel->GetTotalInboundBytes();
uint64 TotalOut = Tunnel->GetTotalOutboundBytes();
```
*来源: `IUdpMessageTunnel.h`, `IUdpMessageTunnelConnection.h`*

### 进阶用法：自定义消息传输

```cpp
#include "Transport/UdpMessageTransport.h"
#include "IMessageTransportHandler.h"

// 实现 IMessageTransportHandler 来接收消息
class FMyTransportHandler : public IMessageTransportHandler
{
public:
    virtual void DiscoverTransportNode(const FGuid& NodeId) override
    {
        UE_LOG(LogTemp, Log, TEXT("Node discovered: %s"), *NodeId.ToString());
    }
    
    virtual void ForgetTransportNode(const FGuid& NodeId) override
    {
        UE_LOG(LogTemp, Log, TEXT("Node lost: %s"), *NodeId.ToString());
    }
    
    virtual void ReceiveTransportMessage(
        const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context,
        const FGuid& NodeId) override
    {
        // 处理接收到的消息
    }
};

// 创建传输实例
TArray<FIPv4Endpoint> StaticEndpoints;
TArray<FString> ExcludedEndpoints;

auto Transport = MakeShared<FUdpMessageTransport, ESPMode::ThreadSafe>(
    FIPv4Endpoint::Any,                                    // 单播端点
    FIPv4Endpoint(FIPv4Address(230, 0, 0, 1), 6666),      // 多播端点
    MoveTemp(StaticEndpoints),
    MoveTemp(ExcludedEndpoints),
    1                                                       // TTL
);

FMyTransportHandler Handler;
Transport->StartTransport(Handler);

// 发送消息
TArray<FGuid> Recipients; // 空 = 广播给所有已知节点
Transport->TransportMessage(MyContext, Recipients);
```
*来源: `UdpMessageTransport.h`, `UdpMessageTransportTest.cpp`*

## Demo 示例

### 最小可编译模块示例

以下示例展示如何在自己的模块中使用 UDP Messaging 的公共接口：

**Build.cs：**
```csharp
public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "UdpMessaging"  // 依赖 UdpMessaging 插件
        });
    }
}
```

**MyClass.h：**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "IUdpMessageTunnel.h"
#include "IUdpMessageTunnelConnection.h"
#include "Shared/UdpMessagingSettings.h"

class FMyUdpMessagingExample
{
public:
    /** 打印当前 UDP Messaging 状态 */
    void PrintStatus()
    {
        const UUdpMessagingSettings* Settings = GetDefault<UUdpMessagingSettings>();
        
        UE_LOG(LogTemp, Log, TEXT("Transport enabled: %s"), 
            Settings->EnableTransport ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Log, TEXT("Unicast Endpoint: %s"), 
            *Settings->UnicastEndpoint);
        UE_LOG(LogTemp, Log, TEXT("Multicast Endpoint: %s"), 
            *Settings->MulticastEndpoint);
        UE_LOG(LogTemp, Log, TEXT("Message Format: %d"), 
            (int32)Settings->MessageFormat);
        UE_LOG(LogTemp, Log, TEXT("Max Send Rate: %.1f Gbit/s"), 
            Settings->MaxSendRate);
    }
    
    /** 动态添加静态端点 */
    void AddStaticEndpoint(const FString& Endpoint)
    {
        IModularFeatures& Features = IModularFeatures::Get();
        if (Features.IsModularFeatureAvailable(INetworkMessagingExtension::ModularFeatureName))
        {
            auto& Extension = Features.GetModularFeature<INetworkMessagingExtension>(
                INetworkMessagingExtension::ModularFeatureName);
            Extension.AddEndpoint(Endpoint);
        }
    }
};
```

## 模块依赖

### 公共依赖（使用者需要引用的）

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `Networking` | UDP Socket 抽象层 |
| `AtomicQueue` | 无锁队列实现 |

### 私有依赖（插件内部使用）

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统（设置类） |
| `Json` | JSON 格式消息序列化（遗留格式） |
| `Cbor` | CBOR 格式消息序列化（当前默认格式） |
| `Messaging` | 消息总线核心框架 |
| `Projects` | 项目信息查询 |
| `Serialization` | 序列化基础设施 |
| `TraceLog` | 追踪日志 |
| `Sockets` | Socket 子系统 |

### 编辑器额外依赖

| 模块 | 用途 |
|---|---|
| `Slate` / `SlateCore` | 设置面板 UI |
| `PropertyEditor` | 自定义属性布局 |
| `UnrealEd` | 编辑器集成 |
| `ApplicationCore` | 应用状态回调 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-11-18 | `4fbae12d` | 修复消息从"待投递"到"已投递"状态转换中的竞态条件，可能导致消息重复投递 |
| 2025-10-07 | `dfacc2f2` | 改进重组消息的投递处理，将消息交给反序列化器时处于"待投递"状态，反序列化完成后才标记为"已投递"。投递状态标记改为 atomic 以支持跨线程状态管理 |
| 2025-10-06 | `931fd281` | SocketSender 中仅在失败时才访问 errno，避免不必要的系统调用 |

### 维护评价

- **年龄**：创建于 2014 年，约 12 年历史，是 UE 消息系统的核心基础设施
- **最近活跃度**：2025 年 10-11 月有实质性更新（竞态修复、异步反序列化改进），属于活跃维护
- **协议版本**：当前协议版本 17，经历了从 JSON → TaggedProperty → CBOR 的多次格式演进，向后兼容旧版本
- **重要性**：这是 UnrealInsights、Multi-User Editing、LiveLink 等核心功能的基础设施，不太可能被废弃
- **SupportedPrograms**：支持 UnrealInsights、UnrealFrontend、UnrealMultiUserServer 等 12 个程序
- **推荐使用**：✅ 推荐。这是 UE 消息传递的标准 UDP 实现，稳定且持续维护

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Messaging/UdpMessaging)
- 测试用例：
  - [`UdpMessageTransportTest.cpp`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Messaging/UdpMessaging/Source/UdpMessaging/Private/Tests/UdpMessageTransportTest.cpp) — 传输层集成测试
  - [`UdpMessageSegmenterTest.cpp`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Messaging/UdpMessaging/Source/UdpMessaging/Private/Tests/UdpMessageSegmenterTest.cpp) — 消息分段单元测试
  - [`UdpSerializeMessageTaskTest.cpp`](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Messaging/UdpMessaging/Source/UdpMessaging/Private/Tests/UdpSerializeMessageTaskTest.cpp) — 序列化任务测试
