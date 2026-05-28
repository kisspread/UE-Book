# BackChannel

> BackChannel is an experimental plugin that allows external tools and apps to query for and push data into a running Unreal session.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 后台通道 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `BackChannel` (RuntimeNoCommandlet) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-03-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BackChannel) | |

## 用途

`BackChannel` 是一个**基于 OSC (Open Sound Control) 协议**的通信框架。它解决的核心问题是：为运行中的 UE5 项目建立一个标准化的、双向的数据通道，允许外部程序（如定制的控制台应用、移动 App、测试脚本等）通过网络（主要是 TCP）与游戏/引擎实例进行实时、低延迟的通信。

**与 RemoteSession 的关系**：从 git 历史看，`BackChannel` 和 `RemoteSession` 最初是合并提交的 (`3865357`)。`BackChannel` 提供了底层的、协议无关的传输和消息分派能力（基于 OSC），而 `RemoteSession` 可能是基于此构建的更上层、针对特定场景（如远程查看）的应用框架。因此，`BackChannel` 更偏向于底层基础设施。

## 使用场景

- 你需要开发一个独立的平板端或手机端应用，作为游戏内的无线控制台（如调整灯光、查看调试信息、触发游戏事件）。
- 你正在开发一个需要与外部硬件（如特定追踪设备、传感器）进行自定义数据交换的 VR/AR 项目。
- 你需要编写自动化测试脚本或监控工具，需要从正在运行的游戏实例中查询数据或注入输入。
- 你希望使用标准的 OSC 协议工具（如 TouchDesigner、Max/MSP 等）与 UE 项目进行交互。

## 蓝图用法

`BackChannel` 主要是 C++ 层的通信框架，提供的蓝图接口主要集中在**建立连接**和**路由管理**上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` (Static) | 获取 `IBackChannelTransport` 模块单例，是创建所有连接的起点 | `IBackChannelTransport` |
| `CreateConnection` | 根据指定类型（如 TCP）创建一个新的 Socket 连接对象 | `IBackChannelTransport` |
| `AddRouteDelegate` | 为指定的消息路径注册一个委托，当收到该路径的消息时触发 | `IBackChannelConnection` |
| `RemoveRouteDelegate` | 移除指定的路由委托 | `IBackChannelConnection` |
| `CreatePacket` | 通过连接创建一个可读写的 `IBackChannelPacket`（用于 OSC 消息） | `IBackChannelConnection` |
| `SendPacket` | 通过连接发送一个数据包 | `IBackChannelConnection` |

### 使用示例（蓝图描述）

1.  **创建连接**：使用 `IBackChannelTransport::Get` 获取模块，然后调用 `CreateConnection` (传入类型 `IBackChannelTransport::TCP`)。
2.  **作为服务器监听**：在连接对象上调用 `Listen` (传入端口号)，然后调用 `WaitForConnection` 等待客户端接入。
3.  **作为客户端连接**：在连接对象上调用 `Connect` (传入如 `“127.0.0.1:12345”` 的端点字符串)，然后调用 `WaitForConnection` 等待连接成功。
4.  **监听消息**：在连接对象上调用 `AddRouteDelegate`，为路径如 `/game/status` 绑定一个委托。当收到该路径的 OSC 消息时，委托被调用。
5.  **发送消息**：通过连接创建 `IBackChannelPacket`，使用 `Write` 方法序列化数据到消息中，然后调用 `SendPacket` 发送。

## C++ 用法

### 头文件引入

```cpp
#include “BackChannel/Transport/IBackChannelTransport.h“
#include “BackChannel/IBackChannelConnection.h“
#include “BackChannel/Protocol/OSC/BackChannelOSCMessage.h“
```

### 基本用法

以下代码演示如何创建一个简单的 TCP 服务器，监听并回复消息。

```cpp
// 来源: 基于 IBackChannelTransport， IBackChannelConnection， FBackChannelOSCMessage 接口整合而成

// 1. 获取传输模块
IBackChannelTransport* TransportModule = IBackChannelTransport::Get();
if (!TransportModule) return;

// 2. 创建一个 TCP 连接对象
TSharedPtr<IBackChannelSocketConnection> SocketConnection = TransportModule->CreateConnection(IBackChannelTransport::TCP);
if (!SocketConnection.IsValid()) return;

// 3. 设置为监听模式，并等待客户端连接
const int16 ListenPort = 9876;
SocketConnection->Listen(ListenPort);

// 4. 等待连接，并在连接建立时获取一个协议级连接包装器
SocketConnection->WaitForConnection(5.0, [this](TSharedRef<IBackChannelSocketConnection> NewConnection) -> bool
{
    // 包装成支持 OSC 协议的连接
    FBackChannelOSCConnection OSCConnection(NewConnection);
    
    // 注册路由处理器，响应 ‘/ping‘ 路径
    OSCConnection.AddRouteDelegate(TEXT(“/ping“), FBackChannelRouteDelegate::FDelegate::CreateLambda(
        [&OSCConnection](IBackChannelPacket& Packet)
        {
            // 读取发送来的数据（可选）
            int32 ReceivedValue;
            Packet.Read(TEXT(“id“), ReceivedValue);
            
            // 创建一个响应包并回复
            TBackChannelSharedPtr<IBackChannelPacket> ResponsePacket = OSCConnection.CreatePacket();
            ResponsePacket->SetPath(TEXT(“/pong“));
            ResponsePacket->Write(TEXT(“status“), (int32)1);
            ResponsePacket->Write(TEXT(“echo_id“), ReceivedValue);
            OSCConnection.SendPacket(ResponsePacket);
        }
    ));

    // 启动后台线程接收消息
    OSCConnection.StartReceiveThread();
    
    return true; // 返回 false 则拒绝连接
});
```

### 进阶用法

结合多个功能，实现一个周期性向外广播数据的客户端。

```cpp
// 作为客户端连接到已知地址
SocketConnection->Connect(TEXT(“127.0.0.1:9876“));
SocketConnection->WaitForConnection(10.0, [this](TSharedRef<IBackChannelSocketConnection> NewConnection) -> bool
{
    FBackChannelOSCConnection* OSCConnection = new FBackChannelOSCConnection(NewConnection);
    
    // 每帧或定时器回调中，创建并发送消息
    auto SendGameTime = [OSCConnection]()
    {
        TBackChannelSharedPtr<IBackChannelPacket> Packet = OSCConnection->CreatePacket();
        Packet->SetPath(TEXT(“/game/time“));
        Packet->Write(TEXT(“seconds“), (float)GetWorld()->GetTimeSeconds());
        OSCConnection->SendPacket(Packet);
    };
    
    // 设置一个定时发送器
    GetWorld()->GetTimerManager().SetTimer(
        BroadcastTimerHandle,
        FTimerDelegate::CreateLambda(SendGameTime),
        1.0f, // 每秒一次
        true
    );

    // 同时可以监听来自服务器的命令
    OSCConnection->AddRouteDelegate(TEXT(“/cmd/pause“), 
        FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket&)
        {
            // 处理暂停命令
            UGameplayStatics::SetGamePaused(GetWorld(), true);
        })
    );
    
    OSCConnection->StartReceiveThread();
    return true;
});
```

## Demo 示例

一个最小化、可编译的示例，展示如何创建连接并收发基本消息。

**MyBackChannelDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h“
#include “Subsystems/GameInstanceSubsystem.h“
#include “MyBackChannelDemo.generated.h“
class IBackChannelSocketConnection;
class FBackChannelOSCConnection;

UCLASS()
class UMyBackChannelDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

private:
    void StartServer();
    void OnClientConnected(TSharedRef<IBackChannelSocketConnection> NewConnection);
    void OnGameTimeMessage(IBackChannelPacket& Packet);

    TSharedPtr<FBackChannelOSCConnection> ActiveOSCConnection;
    FTimerHandle SendTimerHandle;
};
```

**MyBackChannelDemo.cpp**
```cpp
#include “MyBackChannelDemo.h“
#include “BackChannel/Transport/IBackChannelTransport.h“
#include “BackChannel/IBackChannelConnection.h“
#include “BackChannel/Protocol/OSC/BackChannelOSCConnection.h“
#include “Engine/World.h“
#include “TimerManager.h“
#include “Kismet/GameplayStatics.h“
#include “BackChannel/IBackChannelPacket.h“ // 用于 FBackChannelRouteDelegate

void UMyBackChannelDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    StartServer();
}

void UMyBackChannelDemoSubsystem::Deinitialize()
{
    if (ActiveOSCConnection.IsValid())
    {
        // 停止接收线程并断开连接
        ActiveOSCConnection->Stop();
        // ActiveOSCConnection 会随智能指针自动清理
        ActiveOSCConnection.Reset();
    }
    Super::Deinitialize();
}

void UMyBackChannelDemoSubsystem::StartServer()
{
    IBackChannelTransport* Transport = IBackChannelTransport::Get();
    if (!Transport) return;

    TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);
    if (SocketConn.IsValid())
    {
        SocketConn->Listen(7890);
        SocketConn->WaitForConnection(30.0f, 
            FBackChannelListenerDelegate::CreateUObject(this, &UMyBackChannelDemoSubsystem::OnClientConnected));
    }
}

void UMyBackChannelDemoSubsystem::OnClientConnected(TSharedRef<IBackChannelSocketConnection> NewConnection)
{
    UE_LOG(LogTemp, Log, TEXT(“BackChannel: Client Connected!“));
    
    // 创建 OSC 协议层连接
    ActiveOSCConnection = MakeShareable(new FBackChannelOSCConnection(NewConnection));
    
    // 注册一个路径为 ‘/cmd/sendtime‘ 的处理器
    ActiveOSCConnection->AddRouteDelegate(TEXT(“/cmd/sendtime“), 
        FBackChannelRouteDelegate::FDelegate::CreateUObject(this, &UMyBackChannelDemoSubsystem::OnGameTimeMessage));
    
    // 启动后台接收线程
    ActiveOSCConnection->StartReceiveThread();
    
    // 设置一个定时器，每 2 秒主动广播一次游戏时间
    GetWorld()->GetTimerManager().SetTimer(SendTimerHandle, [this]()
    {
        if (!ActiveOSCConnection.IsValid()) return;
        TSharedPtr<IBackChannelPacket> Packet = ActiveOSCConnection->CreatePacket();
        Packet->SetPath(TEXT(“/game/status“));
        Packet->Write(TEXT(“time“), (float)GetWorld()->GetTimeSeconds());
        Packet->Write(TEXT(“frame“), (int32)GFrameNumber);
        ActiveOSCConnection->SendPacket(Packet);
    }, 2.0f, true);
}

void UMyBackChannelDemoSubsystem::OnGameTimeMessage(IBackChannelPacket& Packet)
{
    // 客户端请求我们发送时间，我们可以直接回复这个请求包
    // 或者像上面定时器那样独立广播。这里演示读取请求参数。
    int32 RequestID = 0;
    Packet.Read(TEXT(“request_id“), RequestID);
    UE_LOG(LogTemp, Log, TEXT(“Received /cmd/sendtime request with ID: %d“), RequestID);
    
    // 创建一个回复包
    if (ActiveOSCConnection.IsValid())
    {
        TSharedPtr<IBackChannelPacket> Reply = ActiveOSCConnection->CreatePacket();
        Reply->SetPath(TEXT(“/game/timereply“));
        Reply->Write(TEXT(“request_id“), RequestID);
        Reply->Write(TEXT(“current_time“), (float)GetWorld()->GetTimeSeconds());
        ActiveOSCConnection->SendPacket(Reply);
    }
}
```

## 模块依赖

从 `BackChannel.Build.cs` 分析，其独特依赖如下：

| 模块 | 用途 |
|---|---|
| `Sockets` | 提供底层的网络 Socket 抽象 (`FSocket`)，用于建立 TCP 连接和数据传输。 |
| `Networking` | 提供更高级的网络功能和工具，可能用于连接管理和缓冲区设置。 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF（UE 日志新格式）。 |
| 2026-04-13 | `fb2897b0` | IPv6 support for RemoteSession client and server | 为 RemoteSession 的客户端和服务器添加了 IPv6 支持。 |
| 2026-03-18 | `7a14fcb0` | RemoteSessionApp: Negotiate PixelStreaming availability via Hello handshake | RemoteSession 应用程序：通过 Hello 握手协议协商 PixelStreaming 的可用性。 |
| 2026-02-25 | `12a309dc` | Remove as many PVS suppressions as possible that are no longer needed | 移除了尽可能多的、不再需要的 PVS (Project Validation System) 代码抑制项。 |

### 维护评价

- **创建时间**：2018 年，是一个有一定历史的实验性项目。
- **近期更新**：最近的更新集中在 2026 年初，内容包括代码质量改进（编译警告、日志格式）、网络协议扩展（IPv6）以及关联功能（RemoteSession）的完善。这表明它**仍在被积极维护和改进**。
- **状态**：该插件状态为“Experimental”，且被 `EnabledByDefault` 设置为 `true`，这意味着它随引擎默认分发，但其 API 可能不稳定。从近期的更新来看，Epic 仍在使用和维护它。
- **已知限制**：作为一个底层协议库，它本身不提供图形界面或复杂的会话管理，这些需要上层应用（如 RemoteSession）或开发者自行实现。
- **推荐使用**：**推荐给有明确需求的开发者**。如果你需要建立一个基于标准 OSC 协议的自定义网络通信通道，它是官方提供的可靠选择。对于简单的远程查看或控制，可能更推荐使用 `RemoteSession` 或 Unreal Insights 等内置工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BackChannel)
- [官方文档] 暂无独立官方文档。
- [测试用例] 未在插件目录内发现独立的自动化测试文件。