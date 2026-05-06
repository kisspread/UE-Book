# BackChannel

> BackChannel is an experimental plugin that allows external tools and apps to query for and push data into a running Unreal session.

| 属性 | 值 |
|---|---|
| 中文名 | 后端通道 |
| 分类 | Experimental |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `BackChannel` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel) | |

## 用途

BackChannel 是一个轻量级的网络通信插件，采用 **OSC（Open Sound Control）** 协议（扩展自 UDP 版本的 OSC，使用 TCP 传输），提供双向数据通道。它允许外部工具、App 或脚本在运行时与 Unreal Engine 会话交换结构化数据（整数、浮点数、布尔值、字符串、二进制数据），实现 **实时查询、命令推送和状态同步**。

核心解决以下问题：
- 外部工具需要如何安全、高效地与运行中的 UE 实例通信？
- 如何支持自定义消息路由，将不同消息分发到不同的处理逻辑？
- 如何在后台异步接收网络数据，同时保持主线程安全？

BackChannel 不依赖于蓝图，完全面向 C++ 使用，但提供清晰的接口和委托机制。

## 使用场景

- **外部编辑器工具**：在 UE 外部调整场景参数（灯光颜色、材质属性、Actor 变换），实时生效。
- **可视化调试与数据提取**：从运行的游戏/编辑器进程中拉取性能数据、内存快照、场景状态。
- **手机 App 或 Web 端控制**：通过 TCP 连接将触摸事件、控制指令发送到 UE。
- **自动化测试/集成**：测试脚本通过 BackChannel 发送模拟输入或查询断言结果，实现黑盒测试。
- **协同工作流**：多个 UE 实例或外部平台之间交换同步数据（如时间码、标记信息）。

## 蓝图用法

BackChannel 插件**不提供任何蓝图公开 API**（所有类和方法均标记为 `UE_API` 但无 `BlueprintCallable` 或 `BlueprintType`）。所有交互均需通过 C++ 完成。

## C++ 用法

### 头文件引入

```cpp
#include "BackChannel/IBackChannelTransport.h"
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/IBackChannelPacket.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCConnection.h"
#include "BackChannel/Transport/IBackChannelSocketConnection.h"
```

### 基本用法：创建连接并发送一个消息

```cpp
// 获取 BackChannel 传输模块（单例工厂）
IBackChannelTransport* Transport = IBackChannelTransport::Get();
if (!Transport) return;

// 创建一个 TCP 连接对象
TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);

// 作为客户端连接到远程服务器（端口 3099）
if (SocketConn->Connect(TEXT("127.0.0.1:3099")))
{
    // 用该 Socket 创建一个 OSC 连接（带后台线程）
    TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShared<FBackChannelOSCConnection>(SocketConn.ToSharedRef());
    OSCConn->StartReceiveThread();

    // 创建一个 OSC 报文（写入模式），设置路径
    TBackChannelSharedPtr<IBackChannelPacket> Packet = OSCConn->CreatePacket();
    Packet->SetPath(TEXT("/myapp/setLight"));

    // 写入参数（名称-值对）
    Packet->Write(TEXT("intensity"), 1.5f);
    Packet->Write(TEXT("color"), TEXT("red"));

    // 发送
    OSCConn->SendPacket(Packet);
}
else
{
    UE_LOG(LogTemp, Error, TEXT("BackChannel: Failed to connect to 127.0.0.1:3099"));
}
```

*来源：基于 `IBackChannelTransport::CreateConnection` 和 `FBackChannelOSCConnection` 的公开接口组合，参考 `BackChannel/Transport/IBackChannelTransport.h` 和 `BackChannel/Protocol/OSC/BackChannelOSCConnection.h`。*

### 进阶用法：作为服务器接收消息并绑定路由

```cpp
// 1. 创建监听 Socket
TSharedPtr<IBackChannelSocketConnection> ListenSocket = Transport->CreateConnection(IBackChannelTransport::TCP);
ListenSocket->Listen(3099);

// 2. 等待客户端连接（阻塞超时）
bool bAccepted = ListenSocket->WaitForConnection(5.0, [&](TSharedRef<IBackChannelSocketConnection> Incoming) {
    // 创建一个 OSC 连接来处理该客户端
    TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShared<FBackChannelOSCConnection>(Incoming);
    OSCConn->StartReceiveThread();

    // 绑定路由：当收到 "/myapp/setLight" 消息时，执行回调
    OSCConn->AddRouteDelegate(TEXT("/myapp/setLight"),
        FBackChannelRouteDelegate::FDelegate::CreateLambda([](IBackChannelPacket& Packet) {
            float Intensity;
            FString Color;
            if (Packet.Read(TEXT("intensity"), Intensity) && Packet.Read(TEXT("color"), Color))
            {
                UE_LOG(LogTemp, Log, TEXT("SetLight: intensity=%.2f, color=%s"), Intensity, *Color);
                // 更新场景灯光...
            }
        }));

    // 持续分派消息（通常在 Tick 中调用）
    OSCConn->ReceiveAndDispatchMessages(0.0f);

    return true; // 接受连接
});
```

*来源：`IBackChannelSocketConnection::Listen` 和 `FBackChannelOSCConnection::AddRouteDelegate`，参考 `BackChannel/Transport/IBackChannelSocketConnection.h` 和 `BackChannel/Protocol/OSC/BackChannelOSCConnection.h`。*

## Demo 示例

以下是一个完整的、可编译的最小 C++ 类，演示 BackChannel 作为客户端发送一条消息。假设已在模块的 `Build.cs` 中添加依赖（见模块依赖）。

**MyBackChannelClient.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "BackChannel/IBackChannelTransport.h"
#include "BackChannel/IBackChannelConnection.h"
#include "BackChannel/IBackChannelPacket.h"
#include "BackChannel/Protocol/OSC/BackChannelOSCConnection.h"
#include "BackChannel/Transport/IBackChannelSocketConnection.h"

class FMyBackChannelClient
{
public:
    void SendTestMessage();
};
```

**MyBackChannelClient.cpp**
```cpp
#include "MyBackChannelClient.h"

void FMyBackChannelClient::SendTestMessage()
{
    IBackChannelTransport* Transport = IBackChannelTransport::Get();
    if (!Transport) { UE_LOG(LogTemp, Error, TEXT("BackChannel transport not available")); return; }

    TSharedPtr<IBackChannelSocketConnection> SocketConn = Transport->CreateConnection(IBackChannelTransport::TCP);
    if (!SocketConn->Connect(TEXT("127.0.0.1:3099")))
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to connect, ensure server is running on port 3099"));
        return;
    }

    TSharedRef<FBackChannelOSCConnection> OSCConn = MakeShared<FBackChannelOSCConnection>(SocketConn.ToSharedRef());
    // 不启动接收线程（本例只发送）
    // OSCConn->StartReceiveThread();

    auto Packet = OSCConn->CreatePacket();
    Packet->SetPath(TEXT("/test/hello"));
    Packet->Write(TEXT("value"), 42);
    Packet->Write(TEXT("message"), TEXT("Hello from UE!"));

    int32 BytesSent = OSCConn->SendPacket(Packet);
    UE_LOG(LogTemp, Log, TEXT("Sent %d bytes via BackChannel"), BytesSent);

    // 清理
    OSCConn->Stop();
    SocketConn->Close();
}
```

## 模块依赖

在你的模块 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "BackChannel" });
```

无需额外依赖，因为 `BackChannel` 插件本身已封装了所需的网络模块。插件内部的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 TCP 连接（通过 `IBackChannelSocketConnection` 使用） |

## 维护状态

### 近期更新

- 2025-09-23 `85a3d91` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.
- 2025-09-03 `28e61d0` — Added RemoteSession Hello protocol to sync PixelStreaming version and the Signalling server port.
- 2025-04-23 `6ae5733` — Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i
- 2025-01-28 `22b7270` — FPlatformString and FCString: Deprecate Strcpy and Strcat that take a DestLen, because some platform

### 维护评价

| 维度 | 评估 |
|---|---|
| 活跃度 | 活跃（最近一个月内有功能性提交） |
| 创建时间 | 2025-01-28（约 9 个月） |
| 稳定性 | 实验性插件，API 可能变动，但代码质量较高 |
| 推荐使用 | ✅ 推荐，尤其适合需要快速搭建 C++ 双向通信管道的项目 |

BackChannel 位于 `Experimental` 分类，但已有多处提交且最近仍被维护。如果项目接受实验性插件的潜在风险，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel)
- [官方文档（暂无）]()
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/BackChannel/Source/BackChannel/Private/Tests)