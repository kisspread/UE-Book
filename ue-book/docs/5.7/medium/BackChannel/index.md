# BackChannel

> BackChannel is an experimental plugin that allows external tools and apps to query for and push data into a running Unreal session.

| 属性 | 值 |
|---|---|
| 中文名 | 后台通信 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `BackChannel` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel) | |

## 用途

BackChannel 是一个实验性插件，旨在建立运行时 Unreal 引擎与外部工具之间的双向通信通道。它基于 **OSC（Open Sound Control）** 协议实现数据序列化，并通过 **TCP 套接字** 进行传输。该插件解决了在游戏或应用中实时与外部进程交互的需求，例如：

- 外部控制台发送命令并获取引擎状态
- 自动化测试框架推送数据并检查响应
- 性能监控工具查询实时数据

相比于原生 Socket 编程，BackChannel 提供了高层抽象：自动解析 OSC 包、路由分发消息、后台线程接收等，简化了跨进程通信的开发。

## 使用场景

- **外部编辑器/工具**：你在开发一个关卡编辑器或自定义面板，需要让桌面应用读取引擎中的 Actor 状态或发送生成指令。
- **远程调试**：在运行中的游戏或模拟器中，通过外部终端发送 `set` 或 `get` 命令来修改变量、触发事件。
- **自动化集成测试**：使用测试框架（如 Python、C#）向 Unreal 发送 OSC 消息，验证游戏逻辑。
- **数据可视化**：将引擎内部的实时数据（如 FPS、物理碰撞）推送到外部图表工具中。

## 蓝图用法

> ⚠️ BackChannel 未暴露任何蓝图可调用函数或可编辑属性，所有交互需通过 **C++** 完成。以下表格仅列出核心接口类，便于理解整体架构。

| 核心类 | 说明 | 所在头文件 |
|---|---|---|
| `IBackChannelTransport` | 插件主模块接口，用于创建连接 | `IBackChannelTransport.h` |
| `IBackChannelSocketConnection` | 底层 TCP 连接抽象（连接、监听、收发数据） | `IBackChannelSocketConnection.h` |
| `IBackChannelConnection` | 高层 OSC 连接接口（创建包、路由委托） | `IBackChannelConnection.h` |
| `IBackChannelPacket` | OSC 数据包读写接口（路径、参数） | `IBackChannelPacket.h` |
| `FBackChannelDispatchMap` | 基于路径的委托分发映射 | `DispatchMap.h` |
| `FBackChannelThreadedListener` | 后台线程循环接收数据 | `BackChannelThreadedConnection.h` |

## C++ 用法

### 头文件引入

```cpp
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/IBackChannelPacket.h"
#include "BackChannel/Transport/IBackChannelTransport.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCConnection.h"
```

### 基本用法（客户端连接并发送消息）

```cpp
// 1. 获取插件模块，创建 TCP 连接
IBackChannelTransport* Transport = IBackChannelTransport::Get();
if (!Transport) return;

TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);
if (!SocketConn) return;

// 2. 连接到目标机器（IP 和端口）
const FString EndPoint = TEXT("127.0.0.1:12345");
if (!SocketConn->Connect(*EndPoint))
{
    UE_LOG(LogTemp, Error, TEXT("BackChannel 连接失败"));
    return;
}

// 3. 用底层 Socket 创建 OSC 连接
TSharedRef<IBackChannelSocketConnection> SocketRef = SocketConn.ToSharedRef();
TSharedPtr<FBackChannelOSCConnection> OSCConn = MakeShareable(new FBackChannelOSCConnection(SocketRef));
if (!OSCConn->StartReceiveThread())
{
    UE_LOG(LogTemp, Error, TEXT("无法启动接收线程"));
    return;
}

// 4. 创建一个 OSC 包（写入模式）
TBackChannelSharedPtr<IBackChannelPacket> Packet = OSCConn->CreatePacket();
Packet->SetPath(TEXT("/hello"));

// 5. 写入参数
Packet->Write(TEXT("Name"), FString(TEXT("BackChannel")));
Packet->Write(TEXT("Value"), 42);

// 6. 发送
int32 SentSize = OSCConn->SendPacket(Packet);
UE_LOG(LogTemp, Log, TEXT("发送了 %d 字节的 OSC 消息"), SentSize);
```

### 进阶用法（服务端接收消息 + 路由）

```cpp
// 服务端：监听端口并等待连接
TSharedPtr<IBackChannelSocketConnection> Listener = Transport->CreateConnection(IBackChannelTransport::TCP);
if (!Listener->Listen(12345))
{
    UE_LOG(LogTemp, Error, TEXT("监听端口失败"));
    return;
}

// 等待客户端连接
Listener->WaitForConnection(10.0, [](TSharedRef<IBackChannelSocketConnection> Incoming)
{
    // 创建 OSC 连接
    TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShareable(new FBackChannelOSCConnection(Incoming));
    OSCConn->StartReceiveThread();

    // 注册路由委托：当收到 /hello 消息时触发
    OSCConn->AddRouteDelegate(TEXT("/hello"),
        FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Message)
        {
            FString Name;
            int32 Value = 0;
            Message.Read(TEXT("Name"), Name);
            Message.Read(TEXT("Value"), Value);
            UE_LOG(LogTemp, Log, TEXT("收到消息: Name=%s, Value=%d"), *Name, Value);
        })
    );

    return true; // 接受连接
});
```

## Demo 示例

以下是一个最小可编译的示例，展示服务端监听 + 客户端发送的完整流程（假设在 GameInstance 或 Actor 中调用）。

**MyBackChannelDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyBackChannelDemo.generated.h"

class IBackChannelSocketConnection;
class FBackChannelOSCConnection;

UCLASS()
class UMyBackChannelDemo : public UObject
{
    GENERATED_BODY()

public:
    void StartServer();
    void StartClient();

private:
    TSharedPtr<FBackChannelOSCConnection> OSCConnection;
    TSharedPtr<IBackChannelSocketConnection> Listener;
};
```

**MyBackChannelDemo.cpp**

```cpp
#include "MyBackChannelDemo.h"
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/IBackChannelPacket.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCConnection.h"

void UMyBackChannelDemo::StartServer()
{
    IBackChannelTransport* Transport = IBackChannelTransport::Get();
    if (!Transport) return;

    Listener = Transport->CreateConnection(IBackChannelTransport::TCP);
    if (!Listener->Listen(9001))
    {
        UE_LOG(LogTemp, Error, TEXT("服务器监听失败"));
        return;
    }

    Listener->WaitForConnection(0.0, [this](TSharedRef<IBackChannelSocketConnection> Incoming)
    {
        OSCConnection = MakeShareable(new FBackChannelOSCConnection(Incoming));
        OSCConnection->StartReceiveThread();

        // 注册默认路由
        OSCConnection->AddRouteDelegate(TEXT("/test"),
            FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Msg)
            {
                FString Path = Msg.GetPath();
                UE_LOG(LogTemp, Log, TEXT("收到消息，路径: %s"), *Path);
            })
        );
        return true;
    });
}

void UMyBackChannelDemo::StartClient()
{
    IBackChannelTransport* Transport = IBackChannelTransport::Get();
    if (!Transport) return;

    TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);
    if (!SocketConn->Connect(TEXT("127.0.0.1:9001")))
    {
        UE_LOG(LogTemp, Error, TEXT("客户端连接失败"));
        return;
    }

    TSharedRef<FBackChannelOSCConnection> ClientOSC = MakeShareable(new FBackChannelOSCConnection(SocketConn.ToSharedRef()));
    ClientOSC->StartReceiveThread();

    TBackChannelSharedPtr<IBackChannelPacket> Packet = ClientOSC->CreatePacket();
    Packet->SetPath(TEXT("/test"));
    Packet->Write(TEXT("x"), 123);
    ClientOSC->SendPacket(Packet);
}
```

## 模块依赖

> 在模块的 `Build.cs` 中需要添加以下依赖（省略了标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 TCP 套接字通信 |
| `Networking` | 网络地址解析、连接管理等高级封装 |

## 维护状态

### 近期更新

- 2025-09-23 `85a3d914` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.
- 2025-09-03 `28e61d07` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.（重覆提交，但实为Backout后重新提交）
- 2025-04-23 `6ae57335` — Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i
- 2025-01-28 `22b72707` — FPlatformString and FCString: Deprecate Strcpy and Strcat that take a DestLen, because some platform...

### 维护评价

BackChannel 是一个较新的实验性插件，自 2025 年 1 月创建以来保持活跃维护，最近一次更新在 2025 年 9 月（增加了 RemoteSession Hello 协议支持）。由于是实验性插件，API 可能在未来版本中调整或废弃。目前功能稳定，推荐用于需要简单 OSC 通信的原型开发或内部工具。暂无已知严重问题。**注意：本插件尚未在发布游戏中被广泛验证，请谨慎用于生产项目。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel/Source/BackChannel/Private)（私有实现中包含协议测试）