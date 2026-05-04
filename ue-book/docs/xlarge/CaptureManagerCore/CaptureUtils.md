# docs/xlarge/CaptureManagerCore/index.md

```markdown
# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式资产） |
| 模块 | `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

Capture Manager Core 是 Unreal Engine 虚拟制片（Virtual Production）中 **Capture Manager** 系统的底层基础设施库。它不直接面向最终用户，而是为上层的 **Capture Manager App**（移动端/桌面端捕获应用）和 **Capture Manager Editor**（编辑器内捕获管理工具）提供共享的核心能力。

该插件解决的核心问题：

1. **跨设备捕获通信**：提供 TCP/UDP 网络客户端与服务端，用于 PC 与移动设备之间的捕获数据传输（如 Live Link 数据、Take 上传等）
2. **异步任务编排**：提供可取消的异步任务、进度追踪、回调同步、队列处理等基础设施，支撑长时间运行的捕获和数据摄取流程
3. **事件发布/订阅**：提供线程安全的事件系统（含速率限制），用于捕获状态变更的解耦通知
4. **协议错误处理**：提供 `TProtocolResult<T>` 类型，以类型安全的方式处理网络协议操作的成功/失败
5. **Take 元数据管理**：管理捕获 Take 的元数据结构
6. **资产路径清理**：确保从外部设备导入的文件名符合 UE 资产命名规范

**注意**：此插件默认未启用（`EnabledByDefault: false`），通常由 Capture Manager App 或 Capture Manager Editor 插件自动拉取依赖，无需手动启用。

## 模块列表

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `CaptureManagerStyle` | Runtime | 编辑器 UI 样式定义（图标、颜色等） | — |
| `CaptureManagerTakeMetadata` | Runtime | Take 捕获元数据的数据结构定义 | — |
| `CaptureProtocolStack` | Runtime | 捕获协议栈的完整实现（消息编解码、会话管理） | — |
| `CaptureUtils` | Runtime | 核心工具库：网络通信、异步原语、事件系统、资产清理 | [CaptureUtils](CaptureUtils.md) |
| `DataIngestCore` | Runtime | 数据摄取核心逻辑（文件导入、格式转换） | — |
| `LiveLinkHubCaptureMessaging` | Runtime | 与 Live Link Hub 之间的消息通信协议 | — |

## 使用场景

- 你在开发 **Virtual Production 捕获流水线** → 需要 Capture Manager App/Editor 插件，它们会自动依赖本插件
- 你需要在自定义插件中实现 **TCP/UDP 网络通信** → 可以单独引用 `CaptureUtils` 模块
- 你需要 **可取消的异步任务 + 进度追踪** → `CaptureUtils` 提供了完整的异步原语
- 你需要 **线程安全的发布/订阅事件系统** → `CaptureUtils` 的 `FCaptureEventSource` 及其变体

## 模块依赖

从各模块的 Build.cs 可推断出以下独特依赖（标准 Core/Engine/Slate 等已省略）：

| 模块 | 用途 |
|---|---|
| `Sockets` | TCP/UDP 底层 Socket 操作 |
| `Networking` | UDP Socket 发送/接收、TCP 监听器等高级封装 |

无其他特殊依赖。

## 维护状态

### 近期更新

```
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
- c5b82d054083 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 6/n
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
```

- `fdaf85b`：修复了取消 Take 上传时的多个崩溃，属于重要的稳定性修复
- `c5b82d0`、`2739c3d`：批量更新头文件中的 `dllstorage` 标注位置，属于代码规范化工作（UnrealCodeFixup 自动化工具）

### 维护评价

- **创建时间**：2025-02-04，非常新的插件（约 5 个月）
- **维护状态**：活跃维护中。作为 Epic 官方 Virtual Production 工具链的一部分，随引擎版本持续更新
- **稳定性**：近期有崩溃修复，说明仍在积极打磨中
- **推荐度**：如果你在做 Virtual Production 捕获相关工作，这是必经之路；如果是独立项目需要网络/异步工具，建议评估是否值得引入整个依赖链

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- [CaptureManagerApp 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)（依赖本插件）
- [CaptureManagerEditor 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)（依赖本插件）
```

---

# docs/xlarge/CaptureManagerCore/CaptureUtils.md

```markdown
# CaptureUtils 模块

> CaptureManagerCore 的核心工具库，提供网络通信、异步原语、事件系统和资产清理等基础设施。

| 属性 | 值 |
|---|---|
| 模块名 | `CaptureUtils` |
| 类型 | Runtime |
| API 宏 | `CAPTUREUTILS_API` |
| 命名空间 | `UE::CaptureManager` |

## 概述

`CaptureUtils` 是 CaptureManagerCore 中最基础的模块，几乎所有其他模块都依赖它。它提供以下几大类功能：

| 功能域 | 关键类/函数 | 说明 |
|---|---|---|
| **网络通信** | `FTcpClient`, `FTcpServer`, `FUdpClient` | TCP 客户端/服务端、UDP 组播客户端 |
| **异步原语** | `FCancelableAsyncTask`, `FTaskProgress`, `TQueueRunner`, `TMonitor`, `FCallbackSynchronizer` | 可取消任务、进度追踪、队列处理、线程安全包装、回调同步 |
| **事件系统** | `FCaptureEvent`, `FCaptureEventSource`, `FCaptureEventSourceWithLimiter` | 发布/订阅事件框架，支持速率限制 |
| **线程管理** | `FStopToken`, `FStopRequester`, `FTaskWaiter`, `FCaptureTimerManager`, `CallOnGameThread` | 协作式取消、任务等待、定时器、GameThread 调度 |
| **委托管理** | `TManagedDelegate` | 线程感知的委托执行（可指定在 GameThread/任意线程执行） |
| **错误处理** | `FCaptureProtocolError`, `TProtocolResult<T>` | 协议操作的结果/错误类型 |
| **资产清理** | `SanitizePackagePath`, `SanitizeAssetName` | 清理非法字符以符合 UE 命名规范 |

## 蓝图用法

本模块为纯 C++ 基础设施，**不包含任何 BlueprintCallable 函数**。所有 API 均为 C++ 模块级接口。

## C++ 用法

### 头文件引入

```cpp
// 网络通信
#include "Network/TcpClient.h"
#include "Network/TcpServer.h"
#include "Network/UdpClient.h"
#include "Network/NetworkMisc.h"
#include "Network/Error.h"

// 异步原语
#include "Async/Task.h"
#include "Async/TaskProgress.h"
#include "Async/TaskWaiter.h"
#include "Async/QueueRunner.h"
#include "Async/Monitor.h"
#include "Async/CallbackSynchronizer.h"
#include "Async/StopToken.h"
#include "Async/HelperFunctions.h"
#include "Async/CaptureTimerManager.h"

// 事件系统
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"
#include "Async/ManagedDelegate.h"

// 资产清理
#include "Asset/CaptureAssetSanitization.h"

// 模块接口
#include "CaptureUtilsModule.h"
```

### 错误处理：TProtocolResult

`TProtocolResult<T>` 是本模块中几乎所有网络操作的返回类型，基于 `TValueOrError` 实现。

```cpp
#include "Network/Error.h"

using namespace UE::CaptureManager;

// 成功时返回值
TProtocolResult<int32> SuccessResult(42);

// 失败时返回错误
TProtocolResult<int32> ErrorResult(FCaptureProtocolError(TEXT("Connection failed"), -1));

// void 特化版本
TProtocolResult<void> VoidSuccess(TInPlaceType<void>{});
TProtocolResult<void> VoidError(FCaptureProtocolError(TEXT("Timeout")));

// 使用方式
TProtocolResult<FString> Result = SomeNetworkOperation();
if (Result.HasValue())
{
    FString Value = Result.GetValue();
    // 处理成功
}
else
{
    FCaptureProtocolError Error = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("Error: %s (Code: %d)"), *Error.GetMessage(), Error.GetCode());
}
```

### TCP 客户端

```cpp
#include "Network/TcpClient.h"

using namespace UE::CaptureManager;

// 创建并连接 TCP 客户端
FTcpClient Client;
TProtocolResult<void> InitResult = Client.Init();
if (InitResult.HasError())
{
    // 处理初始化失败
    return;
}

// 阻塞直到连接建立
TProtocolResult<void> ConnectResult = Client.Start(TEXT("192.168.1.100:8080"));
if (ConnectResult.HasError())
{
    // 处理连接失败
    return;
}

// 发送数据
TArray<uint8> Payload;
// ... 填充 Payload ...
auto SendResult = Client.SendMessage(Payload);

// 接收数据（等待最多 2 秒）
auto RecvResult = Client.ReceiveMessage(ExpectedSize, 2000);
if (RecvResult.HasValue())
{
    TArray<uint8> Data = RecvResult.GetValue();
    // 处理接收到的数据
}

// 断开连接
Client.Stop();
```

### TCP 服务端

```cpp
#include "Network/TcpServer.h"

using namespace UE::CaptureManager;

// 创建服务端，最多接受 5 个客户端
FTcpServer Server(5);

// 注册连接/断开回调
Server.SetConnectionHandler(
    FTcpServer::FConnectionHandler::CreateLambda(
        [](TWeakPtr<FTcpClientHandler> InClient, bool bConnected)
        {
            if (bConnected)
            {
                UE_LOG(LogTemp, Log, TEXT("Client connected"));
            }
            else
            {
                UE_LOG(LogTemp, Log, TEXT("Client disconnected"));
            }
        }
    )
);

// 启动监听（端口 0 表示由 OS 分配）
TProtocolResult<uint16> StartResult = Server.Start(9090);
if (StartResult.HasValue())
{
    uint16 ActualPort = StartResult.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Server listening on port %d"), ActualPort);
}

// 向指定客户端发送消息
TArray<uint8> Message;
auto SendResult = Server.SendMessage(Message, TEXT("192.168.1.100:12345"));

// 断开指定客户端
Server.DisconnectClient(TEXT("192.168.1.100:12345"));

// 停止服务端
Server.Stop();
```

### UDP 组播客户端

```cpp
#include "Network/UdpClient.h"

using namespace UE::CaptureManager;

FUdpClient UdpClient;

FUdpClientConfigure Config;
Config.ListenPort = 12345;
Config.MulticastIpAddress = TEXT("239.0.0.1");

// 初始化并注册接收回调
auto InitResult = UdpClient.Init(Config,
    FOnSocketDataReceived::CreateLambda(
        [](const FArrayReaderPtr& Data, const FIPv4Endpoint& Endpoint)
        {
            // 处理接收到的 UDP 数据
        }
    )
);

UdpClient.Start();

// 发送 UDP 消息到指定端点
TArray<uint8> Payload;
auto SendResult = UdpClient.SendMessage(Payload, TEXT("192.168.1.255:12345"));

UdpClient.Stop();
```

### 可取消的异步任务

```cpp
#include "Async/Task.h"

using namespace UE::CaptureManager;

// 创建可取消的异步任务
FCancelableAsyncTask Task(
    [](const FStopToken& StopToken)
    {
        for (int32 i = 0; i < 1000; ++i)
        {
            // 检查是否被请求取消
            if (StopToken.IsStopRequested())
            {
                UE_LOG(LogTemp, Log, TEXT("Task cancelled at step %d"), i);
                return;
            }

            // 执行耗时工作...
            FPlatformProcess::Sleep(0.01f);
        }
    }
);

// 异步启动
Task.StartAsync();

// 稍后取消
Task.Cancel();

// 等待完成
while (!Task.IsDone())
{
    FPlatformProcess::Sleep(0.01f);
}

// 也可以同步执行（阻塞当前线程）
FCancelableAsyncTask SyncTask([](const FStopToken&) { /* work */ });
SyncTask.StartSync();
```

### 进度追踪

```cpp
#include "Async/TaskProgress.h"

using namespace UE::CaptureManager;

// 创建进度追踪器，总共有 4 个子任务
auto Progress = MakeShared<FTaskProgress>(4,
    FTaskProgress::FProgressReporter::CreateLambda(
        [](double InProgress)
        {
            UE_LOG(LogTemp, Log, TEXT("Overall progress: %.1f%%"), InProgress * 100.0);
        }
    )
);

// 设置报告阈值（变化超过 5% 才报告）
Progress->SetReportThreshold(0.05);

// 启动子任务并更新进度
{
    FTaskProgress::FTask SubTask1 = Progress->StartTask();
    // ... 执行工作 ...
    SubTask1.Update(0.5);  // 子任务 1 完成 50%
    // ... 继续工作 ...
    SubTask1.Update(1.0);  // 子任务 1 完成 100%
}

{
    FTaskProgress::FTask SubTask2 = Progress->StartTask();
    SubTask2.Update(1.0);  // 子任务 2 完成
}

// 获取总进度
double Total = Progress->GetTotalProgress();
```

### 回调同步器

等待多个异步回调全部完成后再执行后续操作：

```cpp
#include "Async/CallbackSynchronizer.h"

using namespace UE::CaptureManager;

auto Sync = FCallbackSynchronizer::Create();

// 创建包装后的回调（每创建一个，内部计数器 +1）
auto OnFileLoaded = Sync->CreateCallback(
    [](const FString& FileName)
    {
        UE_LOG(LogTemp, Log, TEXT("File loaded: %s"), *FileName);
    }
);

auto OnMetadataParsed = Sync->CreateCallback(
    [](bool bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Metadata parsed: %s"), bSuccess ? TEXT("OK") : TEXT("Failed"));
    }
);

// 所有回调都执行完毕后触发
Sync->AfterAll(
    FCallbackSynchronizer::FAfterAllDelegate::CreateLambda(
        []()
        {
            UE_LOG(LogTemp, Log, TEXT("All operations completed!"));
        }
    )
);

// 将回调分发到不同异步操作...
OnFileLoaded.Execute(TEXT("take_001.mov"));
OnMetadataParsed.Execute(true);
// AfterAll 会在两个回调都执行后自动触发
```

### 线程安全包装器 TMonitor

```cpp
#include "Async/Monitor.h"

using namespace UE::CaptureManager;

// 包装一个需要线程安全访问的数据结构
struct FCaptureState
{
    FString CurrentTake;
    bool bIsRecording = false;
    TArray<FString> LogEntries;
};

TMonitor<FCaptureState> SafeState;

// 通过 -> 操作符自动加锁访问（作用域结束自动释放）
{
    auto Locked = SafeState->;
    Locked->CurrentTake = TEXT("Take_001");
    Locked->bIsRecording = true;
    Locked->LogEntries.Add(TEXT("Recording started"));
}

// 也可以用 Lock() 方法
{
    auto Locked = SafeState.Lock();
    if (Locked->bIsRecording)
    {
        // ...
    }
}

// 非线程安全的直接访问（仅在确定单线程时使用）
FCaptureState& UnsafeRef = SafeState.GetUnsafe();

// 移动所有权
FCaptureState Owned = SafeState.Claim();
```

### 队列处理器 TQueueRunner

```cpp
#include "Async/QueueRunner.h"

using namespace UE::CaptureManager;

// 创建队列处理器，在独立线程上处理元素
TQueueRunner<FString> FileProcessor(
    TQueueRunner<FString>::FOnProcess::CreateLambda(
        [](FString InFilePath)
        {
            // 在专用线程上处理每个文件
            UE_LOG(LogTemp, Log, TEXT("Processing: %s"), *InFilePath);
            // ... 文件处理逻辑 ...
        }
    )
);

// 添加任务到队列
FileProcessor.Add(TEXT("/path/to/file1.mov"));
FileProcessor.Add(TEXT("/path/to/file2.mov"));
FileProcessor.Add(TEXT("/path/to/file3.mov"));

// 检查是否正在运行
if (FileProcessor.IsRunning())
{
    // ...
}

// 清空队列
FileProcessor.Empty();
```

### 协作式取消（StopToken / StopRequester）

```cpp
#include "Async/StopToken.h"

using namespace UE::CaptureManager;

// 创建请求者
FStopRequester Requester;

// 从请求者创建令牌（可创建多个）
FStopToken Token1 = Requester.CreateToken();
FStopToken Token2 = Requester.CreateToken();

// 在工作线程中检查令牌
auto Worker = [&Token1]()
{
    while (!Token1.IsStopRequested())
    {
        // 执行工作...
    }
    UE_LOG(LogTemp, Log, TEXT("Worker stopped gracefully"));
};

// 请求停止
Requester.RequestStop();

// 检查是否已请求停止
if (Requester.IsStopRequested())
{
    // ...
}
```

### GameThread 调度

```cpp
#include "Async/HelperFunctions.h"

using namespace UE::CaptureManager;

// 在网络回调线程中需要更新 UI 时
void OnNetworkDataReceived(const TArray<uint8>& Data)
{
    // 将 UI 更新调度到 GameThread 并等待完成
    CallOnGameThread([&Data]()
    {
        // 这里安全地操作 UMG Widget 或其他 GameThread-only 对象
    });
}
```

### 定时器管理器

```cpp
#include "Async/CaptureTimerManager.h"
#include "CaptureUtilsModule.h"

// 通过模块获取定时器管理器
FCaptureUtilsModule& Module = FModuleManager::GetModuleChecked<FCaptureUtilsModule>(TEXT("CaptureUtils"));
TSharedRef<FCaptureTimerManager> TimerMgr = Module.GetTimerManager();

// 添加定时器（每 0.5 秒触发一次，循环）
auto Handle = TimerMgr->AddTimer(
    FTimerDelegate::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Timer tick"));
    }),
    0.5f,   // 间隔（秒）
    true,   // 循环
    0.0f    // 首次延迟
);

// 移除定时器
TimerMgr->RemoveTimer(Handle);
```

### 事件系统

```cpp
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"

using namespace UE::CaptureManager;

// 1. 定义事件类型
CAPTURE_DEFINE_EMPTY_EVENT(FRecordingStartedEvent, "RecordingStarted")

struct FCaptureProgressEvent : public FCaptureEvent
{
    inline static const FString Name = TEXT("CaptureProgress");

    double Progress;
    FString Message;

    FCaptureProgressEvent(double InProgress, const FString& InMessage)
        : FCaptureEvent(Name)
        , Progress(InProgress)
        , Message(InMessage)
    {
    }
};

// 2. 创建事件源
class FMyCaptureSession : public FCaptureEventSource
{
public:
    FMyCaptureSession()
    {
        // 注册可用事件
        RegisterEvent(FRecordingStartedEvent::Name);
        RegisterEvent(FCaptureProgressEvent::Name);
    }

    void DoCapture()
    {
        // 发布无数据事件
        PublishEvent<FRecordingStartedEvent>();

        // 发布带数据事件
        PublishEvent<FCaptureProgressEvent>(0.5, TEXT("Halfway done"));
        PublishEvent<FCaptureProgressEvent>(1.0, TEXT("Complete"));
    }
};

// 3. 订阅事件
FMyCaptureSession Session;

Session.SubscribeToEvent(FRecordingStartedEvent::Name,
    FCaptureEventHandler(
        [](TSharedPtr<const FCaptureEvent> InEvent)
        {
            UE_LOG(LogTemp, Log, TEXT("Recording started!"));
        },
        EDelegateExecutionThread::GameThread  // 在 GameThread 上执行
    )
);

Session.SubscribeToEvent(FCaptureProgressEvent::Name,
    FCaptureEventHandler(
        [](TSharedPtr<const FCaptureEvent> InEvent)
        {
            auto ProgressEvent = StaticCastSharedPtr<const FCaptureProgressEvent>(InEvent);
            UE_LOG(LogTemp, Log, TEXT("Progress: %.0f%% - %s"),
                ProgressEvent->Progress * 100, *ProgressEvent->Message);
        },
        EDelegateExecutionThread::AnyThread  // 在任意线程执行
    )
);

// 获取可用事件列表
TArray<FString> Events = Session.GetAvailableEvents();

// 取消所有订阅
Session.UnsubscribeAll();
```

### 速率限制事件源

```cpp
#include "Async/EventSourceUtils.h"

using namespace UE::CaptureManager;

// 创建带速率限制的事件源（最少 100ms 间隔）
class FMySensorSource : public FCaptureEventSourceWithLimiter
{
public:
    FMySensorSource()
        : FCaptureEventSourceWithLimiter(100)  // 100ms 阈值
    {
        RegisterEvent(TEXT("SensorUpdate"));
    }

    void OnSensorData(double Value)
    {
        // 仅在距上次发布超过 100ms 时才发布
        // 不满足条件时事件会被丢弃（不缓冲）
        PublishIfThresholdReached<FSensorUpdateEvent>(false, Value);
    }

    void OnSensorDisconnected()
    {
        // 强制发布（忽略阈值），确保最终状态通知不被丢弃
        PublishIfThresholdReached<FSensorUpdateEvent>(true, 0.0);
    }
};
```

### 资产路径清理

```cpp
#include "Asset/CaptureAssetSanitization.h"

using namespace UE::CaptureManager;

// 清理包路径（替换非法字符为下划线）
FString PackagePath = TEXT("/Game/Captures/Take 001 (v2)");
SanitizePackagePath(PackagePath);
// 结果: "/Game/Captures/Take_001__v2_"

// 清理资产名称
FString AssetName = TEXT("MyAsset@#$%");
SanitizeAssetName(AssetName);
// 结果: "MyAsset____"

// 使用自定义替换字符
FString Path2 = TEXT("/Game/Invalid:Path");
SanitizePackagePath(Path2, TEXT('-'));
// 结果: "/Game/Invalid-Path"
```

### 网络信息查询

```cpp
#include "Network/NetworkMisc.h"

using namespace UE::CaptureManager;

// 获取本机 IP 地址（可能失败）
TOptional<FString> Ip = GetLocalIpAddress();
if (Ip.IsSet())
{
    UE_LOG(LogTemp, Log, TEXT("Local IP: %s"), *Ip.GetValue());
}

// 获取本机主机名（可能失败）
TOptional<FString> HostName = GetLocalHostName();

// 获取本机主机名（失败时断言）
FString CheckedName = GetLocalHostNameChecked();
```

## Demo 示例

以下示例展示了一个完整的 TCP 服务端，接受客户端连接、接收消息、发送响应，并支持优雅关闭：

### CaptureServerExample.h

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "Network/TcpServer.h"
#include "Async/StopToken.h"
#include "Async/Event.h"
#include "Async/EventSourceUtils.h"

using namespace UE::CaptureManager;

// 自定义事件
CAPTURE_DEFINE_EMPTY_EVENT(FServerStartedEvent, "ServerStarted")

struct FClientMessageEvent : public FCaptureEvent
{
    inline static const FString Name = TEXT("ClientMessage");
    FString Endpoint;
    FString Message;

    FClientMessageEvent(const FString& InEndpoint, const FString& InMessage)
        : FCaptureEvent(Name), Endpoint(InEndpoint), Message(InMessage)
    {
    }
};

class FCaptureServerExample : public FCaptureEventSource
{
public:
    FCaptureServerExample();
    ~FCaptureServerExample();

    bool Start(uint16 InPort);
    void Stop();
    void SendToClient(const FString& InEndpoint, const FString& InMessage);

private:
    void OnConnection(TWeakPtr<FTcpClientHandler> InClient, bool bConnected);
    void HandleClient(TSharedPtr<FTcpClientHandler> InClient);

    TUniquePtr<FTcpServer> Server;
    FStopRequester StopRequester;
    TMap<FString, FStopRequester> ClientStopRequesters;
};
```

### CaptureServerExample.cpp

```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "CaptureServerExample.h"

FCaptureServerExample::FCaptureServerExample()
{
    RegisterEvent(FServerStartedEvent::Name);
    RegisterEvent(FClientMessageEvent::Name);
}

FCaptureServerExample::~FCaptureServerExample()
{
    Stop();
}

bool FCaptureServerExample::Start(uint16 InPort)
{
    Server = MakeUnique<FTcpServer>(10); // 最多 10 个客户端

    Server->SetConnectionHandler(
        FTcpServer::FConnectionHandler::CreateRaw(this, &FCaptureServerExample::OnConnection)
    );

    auto Result = Server->Start(InPort);
    if (Result.HasError())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to start server: %s"),
            *Result.GetError().GetMessage());
        return false;
    }

    PublishEvent<FServerStartedEvent>();
    UE_LOG(LogTemp, Log, TEXT("Server started on port %d"), Result.GetValue());
    return true;
}

void FCaptureServerExample::Stop()
{
    // 请求所有客户端处理停止
    StopRequester.RequestStop();

    if (Server)
    {
        Server->Stop();
        Server.Reset();
    }

    UnsubscribeAll();
}

void FCaptureServerExample::SendToClient(const FString& InEndpoint, const FString& InMessage)
{
    if (!Server) return;

    FTCHARToUTF8 Converter(*InMessage);
    TArray<uint8> Payload;
    Payload.Append((const uint8*)Converter.Get(), Converter.Length());

    auto Result = Server->SendMessage(Payload, InEndpoint);
    if (Result.HasError())
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to send to %s: %s"),
            *InEndpoint, *Result.GetError().GetMessage());
    }
}

void FCaptureServerExample::OnConnection(TWeakPtr<FTcpClientHandler> InClient, bool bConnected)
{
    auto Client = InClient.Pin();
    if (!Client) return;

    if (bConnected)
    {
        UE_LOG(LogTemp, Log, TEXT("Client connected: %s"), *Client->GetEndpoint());

        // 为每个客户端启动独立的处理任务
        Async(EAsyncExecution::Thread, [this, Client]()
        {
            HandleClient(Client);
        });
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Client disconnected: %s"), *Client->GetEndpoint());
    }
}

void FCaptureServerExample::HandleClient(TSharedPtr<FTcpClientHandler> InClient)
{
    const FString Endpoint = InClient->GetEndpoint();

    while (!StopRequester.IsStopRequested())
    {
        // 检查是否有待接收数据
        auto PendingResult = InClient->HasPendingData();
        if (PendingResult.HasError())
        {
            UE_LOG(LogTemp, Warning, TEXT("Client %s error, disconnecting"), *Endpoint);
            break;
        }

        if (PendingResult.GetValue() == 0)
        {
            FPlatformProcess::Sleep(0.01f);
            continue;
        }

        // 接收消息
        auto RecvResult = InClient->ReceiveMessage(1024, 1000);
        if (RecvResult.HasError())
        {
            int32 ErrorCode = RecvResult.GetError().GetCode();
            if (ErrorCode == FTcpClientHandler::DisconnectedError)
            {
                UE_LOG(LogTemp, Log, TEXT("Client %s disconnected"), *Endpoint);
            }
            break;
        }

        // 解析消息
        TArray<uint8> Data = RecvResult.GetValue();
        FString Message = FString(UTF8_TO_TCHAR(Data.GetData()));

        // 发布事件
        PublishEvent<FClientMessageEvent>(Endpoint, Message);

        // 回复客户端
        FString Response = FString::Printf(TEXT("Received: %s"), *Message);
        SendToClient(Endpoint, Response);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Sockets` | 底层 Socket API（FSocket, FIPv4Endpoint 等） |
| `Networking` | 高级网络封装（FUdpSocketReceiver, FUdpSocketSender, FTcpListener 等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- fdaf85b60939 [Capture Manager] Fixed several crashes while aborting take upload.
- c5b82d054083 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 6/n
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
```

### 维护评价

- **活跃度**：活跃维护中，作为 Capture Manager 系统的基础设施持续更新
- **稳定性**：近期有崩溃修复（`fdaf85b`），说明仍在积极打磨
- **代码质量**：有系统性的代码规范化工作（`dllstorage` 标注修正），表明 Epic 对代码质量有持续投入
- **推荐度**：如果你在做 Virtual Production 捕获流水线，这是核心依赖；如果是独立项目，其中的异步原语（`TMonitor`、`FCancelableAsyncTask`、`FCallbackSynchronizer`）设计精良，值得参考学习，但直接引入需考虑对 CaptureManager 整体的依赖

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureUtils)
- [CaptureUtils.Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore/Source/CaptureUtils/CaptureUtils.Build.cs)
```