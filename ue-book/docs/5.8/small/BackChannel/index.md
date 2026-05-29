# BackChannel

> BackChannel is an experimental plugin that allows external tools and apps to query for and push data into a running Unreal session.

| 属性 | 值 |
|---|---|
| 中文名 | 反向通道通信 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `BackChannel` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-10-30 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BackChannel) | |

## 用途

BackChannel 插件提供了一套轻量级的基于 OSC（Open Sound Control）协议的通信框架，允许外部工具、编辑器扩展或自动化脚本通过 TCP 网络连接到正在运行中的 Unreal 实例，并进行实时数据查询和推送。它解决了动态运行时数据交互的需求，常用于编辑器自动化测试、实时调参、外部控制台、远程监控等场景。

- **为什么存在**：传统的 UE 进程间通信（如 UObject 反射、RPC、命令行）要么过于重量级，要么不适合跨平台/跨进程的轻量交互。BackChannel 提供了一个简单的消息路由机制，将外部数据包（OSC 格式）映射到 UE 内部的委托（Delegate），从而让外部工具能够以极低耦合的方式“注入”数据。
- **解决什么问题**：实现外部应用（如 Python 脚本、自定义 UI 工具、游戏测试框架）与 Unreal 运行时之间的双向、实时的数据通道，无需停机或重启编辑器。

## 使用场景

- 你正在开发编辑器下的自动化测试框架，需要从外部发送指令控制关卡状态、查询性能数据 → 使用 BackChannel 的 OSC 消息路由。
- 你需要远程调优游戏参数（如 AI 行为、物理参数），但不想修改源码重新编译 → 通过外部工具实时发送参数更新包。
- 你想搭建一个外部 UI 控制台，用于监控和调整运行中的 UE 实例 → 通过 BackChannel 的 TCP 连接接收外部命令。
- 你需要集成外部数据源（如传感器、模拟器）到 UE 的实时渲染中 → 使用 BackChannel 的包写入和路由功能。

## 蓝图用法

BackChannel 插件主要提供了 C++ 接口，蓝图方面未暴露大量节点。但在 `BackChannel` 模块中包含了一些可用的蓝图函数库（需要进一步确认）。目前核心接口集中在 `IBackChannelConnection` 和 `IBackChannelPacket`，这些接口通常通过 C++ 使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Packet` | 创建一个新的消息包（可写入） | `IBackChannelConnection` |
| `Send Packet` | 发送一个包到连接的另一端 | `IBackChannelConnection` |
| `Add Route Delegate` | 绑定一个委托到指定路径，当收到该路径消息时触发 | `IBackChannelConnection` |
| `Remove Route Delegate` | 移除已绑定的委托 | `IBackChannelConnection` |

**使用示例（蓝图描述）**：  
在蓝图中无法直接获取 `IBackChannelConnection` 对象，通常需要先从 `BackChannelTransport` 模块创建一个连接。建议在 C++ 中创建连接并暴露给蓝图。典型的蓝图节点调用链：  
1. `Get BackChannel Transport`（内部获取 `IBackChannelTransport` 单例）  
2. `Create Connection`（选择协议类型，如 `IBackChannelTransport::TCP`）  
3. `Connect`（输入目标地址和端口）  
4. `Create Packet` → 写入数据（`Write Int32`, `Write String` 等）→ `Send Packet`  
5. `Add Route Delegate`（指定路径和事件，当收到该路径消息时执行自定义事件）

## C++ 用法

### 头文件引入

```cpp
#include "BackChannel/Transport/IBackChannelTransport.h"
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCMessage.h"
```

### 基本用法

**创建并连接一个客户端（连接到远程监听端）**：

```cpp
// 获取传输模块
IBackChannelTransport* Transport = IBackChannelTransport::Get();
if (!Transport) return;

// 创建一个 TCP 连接
TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);
if (!SocketConn.IsValid()) return;

// 连接到目标地址（例如 localhost:1024）
bool bConnected = SocketConn->Connect(TEXT("127.0.0.1:1024"));
if (!bConnected) 
{
    UE_LOG(LogBackChannel, Error, TEXT("Failed to connect"));
    return;
}

// 将原始连接包装为 OSC 连接
TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShareable(new FBackChannelOSCConnection(SocketConn.ToSharedRef()));
OSCConn->StartReceiveThread(); // 启动后台接收线程

// 绑定一个路由委托，当收到 "/test/hello" 消息时触发
OSCConn->AddRouteDelegate(TEXT("/test/hello"),
    FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Packet)
    {
        FString Msg;
        Packet.Read(TEXT("message"), Msg);
        UE_LOG(LogBackChannel, Log, TEXT("Received message: %s"), *Msg);
    }));
```

**发送一个 OSC 包**：

```cpp
// 创建可写入的包
TBackChannelSharedPtr<IBackChannelPacket> Packet = OSCConn->CreatePacket();
Packet->SetPath(TEXT("/test/hello"));
Packet->Write(TEXT("message"), TEXT("Hello from Unreal!"));

// 发送
OSCConn->SendPacket(Packet);
```

**服务端监听**：

```cpp
// 创建一个监听连接
TSharedPtr<IBackChannelSocketConnection> Listener = Transport->CreateConnection(IBackChannelTransport::TCP);
Listener->Listen(1024); // 监听端口 1024

// 等待客户端连接（超时时间 10 秒）
Listener->WaitForConnection(10.0, [](TSharedRef<IBackChannelSocketConnection> Incoming)
{
    // 处理新连接，创建 OSC 连接并绑定路由
    // ...
    return true; // 接受连接
});
```

### 进阶用法

**使用 `FBackChannelDispatchMap` 手动分发消息**（无需独立的连接线程）：

```cpp
FBackChannelDispatchMap DispatchMap;

// 注册路由
DispatchMap.AddRoute(TEXT("/param/set"),
    FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Packet)
    {
        float Value;
        Packet.Read(TEXT("value"), Value);
        // 应用值到游戏逻辑
    }));

// 在收到原始数据后，解析为 OSC 包并分发
TSharedPtr<FBackChannelOSCPacket> Parsed = FBackChannelOSCPacket::CreateFromBuffer(Data, DataLength);
if (Parsed.IsValid() && Parsed->GetType() == OSCPacketType::Message)
{
    IBackChannelPacket& Msg = static_cast<FBackChannelOSCMessage&>(*Parsed);
    DispatchMap.DispatchMessage(Msg);
}
```

## Demo 示例

以下是一个完整的单文件示例，演示一个简单的客户端连接、发送消息并接收回应。实际使用时需要包含必要的头文件和链接。

**DemoClient.h**:
```cpp
#pragma once
#include "CoreMinimal.h"
#include "BackChannel/Transport/IBackChannelTransport.h"
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCConnection.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCMessage.h"

class FBackChannelDemoClient
{
public:
    void ConnectAndSend();
};
```

**DemoClient.cpp**:
```cpp
#include "DemoClient.h"
#include "BackChannel/Common.h" // 日志类别

void FBackChannelDemoClient::ConnectAndSend()
{
    IBackChannelTransport* Transport = IBackChannelTransport::Get();
    if (!Transport) 
    {
        UE_LOG(LogTemp, Error, TEXT("BackChannel transport not available."));
        return;
    }

    // 创建 TCP 连接
    TSharedPtr<IBackChannelSocketConnection> RawConn = Transport->CreateConnection(IBackChannelTransport::TCP);
    if (!RawConn.IsValid() || !RawConn->Connect(TEXT("127.0.0.1:5500")))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to connect to :5500"));
        return;
    }

    // 包装为 OSC 连接
    TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShareable(new FBackChannelOSCConnection(RawConn.ToSharedRef()));
    OSCConn->StartReceiveThread();

    // 绑定路由，等待服务端回复
    OSCConn->AddRouteDelegate(TEXT("/response"),
        FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Packet)
        {
            FString Reply;
            Packet.Read(TEXT("text"), Reply);
            UE_LOG(LogTemp, Log, TEXT("Server replied: %s"), *Reply);
        }));

    // 发送一条消息
    TBackChannelSharedPtr<IBackChannelPacket> Packet = OSCConn->CreatePacket();
    Packet->SetPath(TEXT("/hello"));
    Packet->Write(TEXT("greeting"), TEXT("Hello Server!"));
    OSCConn->SendPacket(Packet);

    // 等待一段时间后退出（示例简单起见）
    FPlatformProcess::Sleep(5.0f);
    OSCConn->Stop();
    RawConn->Close();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 TCP 套接字通信 |
| `Networking` | 网络地址解析等 |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` — Migrate UE_LOG to UE_LOGF.  
- 2026-04-13 `fb2897b0` — IPv6 support for RemoteSession client and server  
- 2026-03-18 `7a14fcb0` — RemoteSessionApp: Negotiate PixelStreaming availability via Hello handshake  
- 2026-02-25 `12a309dc` — Remove as many PVS suppressions as possible that are no longer needed  
- 2025-10-30 `a0e12af6` — Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default

### 维护评价

- **创建时间**：2025 年 10 月（距今约 6 个月），属于较新的插件。
- **近期更新**：上个月有日志迁移、IPv6 支持和功能协商更新，表明活跃维护。
- **活跃度**：频繁且有意义的功能更新（IPv6 支持、通信协议握手），而非简单的编译修复。
- **限制**：实验性插件，API 可能不稳定；文档较少，需要直接阅读源码接口。
- **推荐使用**：推荐用于编辑器自动化、外部工具集成等场景。生产环境需注意其实验性质，做好版本锁定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BackChannel)
- [官方文档](https://docs.unrealengine.com/5.8/zh-CN/backchannel-plugin-in-unreal-engine/)（未确认）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/BackChannel/Source/BackChannel/Private/Tests)（需确认路径是否存在）