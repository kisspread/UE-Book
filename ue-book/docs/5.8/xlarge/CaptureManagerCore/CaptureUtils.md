# Capture Manager Core

> The Capture Manager Core plugin contains utility modules that are shared between Capture Manager App plugin and Capture Manager Editor plugin.

| 属性 | 值 |
|---|---|
| 中文名 | 捕获管理器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CaptureDataConverter` (Runtime), `CaptureManagerCPSClient` (Runtime), `CaptureManagerMediaRW` (Runtime), `CaptureManagerPipeline` (Runtime), `CaptureManagerStyle` (Runtime), `CaptureManagerTakeMetadata` (Runtime), `CaptureMetadataExtraction` (Runtime), `CaptureProtocolStack` (Runtime), `CaptureUtils` (Runtime), `DataIngestCore` (Runtime), `LiveLinkHubCaptureMessaging` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-02-04 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore) | |

## 用途

CaptureManagerCore 是虚幻引擎虚拟制片流水线中 **Capture Manager** 生态系统的核心基础层。它不直接面向最终用户，而是为 **Capture Manager App**（桌面捕获应用）和 **Capture Manager Editor**（编辑器内管理工具）提供共享的底层工具模块。

该插件解决的核心问题是：在虚拟制片场景中，需要从外部设备（如摄像头、深度传感器、MoCap 系统等）实时或离线捕获数据，并将其导入 UE5。这个过程涉及复杂的**异步通信**、**网络协议**、**数据格式转换**、**管线调度**和**进度追踪**——CaptureManagerCore 将这些基础设施统一封装为 11 个独立模块，避免 App 端和 Editor 端重复实现。

本插件默认 **未启用**，需要在项目中手动开启，或在使用 Capture Manager 系列插件时被自动依赖。

## 使用场景

- 你在开发**虚拟制片流水线**，需要从外部设备捕获表演数据（MoCap、LidarScan 等）→ 使用 CaptureManagerCore 作为底层通信和调度框架
- 你需要实现 **Capture Manager App 与 UE5 之间的 TCP/UDP 通信** → 使用 CaptureUtils 模块中的网络工具类
- 你需要在多线程环境下管理**事件发布、委托执行、异步任务** → 使用 CaptureUtils 的异步工具类
- 你需要解析捕获会话的 **Take 元数据**（镜头编号、录制时间、设备信息等） → 使用 CaptureManagerTakeMetadata 模块
- 你需要将捕获的原始数据转换为 UE5 可用的资产格式 → 使用 CaptureDataConverter 模块

## 蓝图用法

CaptureUtils 模块主要是 C++ 底层工具库，**不直接暴露蓝图节点**。其功能通过上层模块（CaptureManagerApp、CaptureManagerEditor）间接暴露给蓝图。

如果在 C++ 中使用本模块，主要通过以下类实现程序逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureUtilsModule.h"       // 模块入口
#include "Async/Event.h"              // 事件系统
#include "Async/EventSourceUtils.h"   // 事件源基类
#include "Async/ManagedDelegate.h"    // 线程安全委托
#include "Async/Task.h"               // 可取消异步任务
#include "Async/TaskProgress.h"       // 任务进度追踪
#include "Async/StopToken.h"          // 停止令牌
#include "Network/TcpServer.h"        // TCP 服务器
#include "Network/TcpClient.h"        // TCP 客户端
#include "Network/UdpClient.h"        // UDP 客户端
#include "Asset/CaptureAssetSanitization.h" // 资产路径清理
#include "Async/HelperFunctions.h"    // 工具函数
```

### 事件系统

事件系统是 CaptureUtils 最核心的子系统，基于**发布-订阅模式**，所有操作均为线程安全。

```cpp
// 基于 Event.h
using namespace UE::CaptureManager;

// 1. 定义自定义事件（无数据事件）
CAPTURE_DEFINE_EMPTY_EVENT(FMyCaptureStarted, "CaptureStarted");
CAPTURE_DEFINE_EMPTY_EVENT(FMyCaptureStopped, "CaptureStopped");

// 2. 定义携带数据的事件
struct FMyProgressEvent : public FCaptureEvent
{
    static inline const FString Name = TEXT("Progress");
    double Progress;
    FMyProgressEvent(double InProgress)
        : FCaptureEvent(Name)
        , Progress(InProgress)
    {}
};
```

**自定义事件源类**（继承 `FCaptureEventSource`）：

```cpp
// 基于 EventSourceUtils.h
class FMyCaptureDevice : public FCaptureEventSource
{
public:
    FMyCaptureDevice()
    {
        // 注册支持的事件
        RegisterEvent(FMyCaptureStarted::Name);
        RegisterEvent(FMyCaptureStopped::Name);
        RegisterEvent(FMyProgressEvent::Name);
    }

    void SimulateCapture()
    {
        // 发布事件（自动包装为 SharedPtr<const Event>）
        PublishEvent<FMyCaptureStarted>();

        for (int32 i = 0; i <= 100; ++i)
        {
            PublishEvent<FMyProgressEvent>(static_cast<double>(i) / 100.0);
        }

        PublishEvent<FMyCaptureStopped>();
    }
};
```

**订阅事件**：

```cpp
// 基于 Event.h
auto Device = MakeShared<FMyCaptureDevice>();

Device->SubscribeToEvent(
    FMyCaptureStarted::Name,
    FCaptureEventHandler(
        [](TSharedPtr<const FCaptureEvent> InEvent)
        {
            UE_LOG(LogTemp, Log, TEXT("Capture started!"));
        },
        EDelegateExecutionThread::GameThread  // 在 GameThread 上执行回调
    )
);

Device->SubscribeToEvent(
    FMyProgressEvent::Name,
    FCaptureEventHandler(
        [](TSharedPtr<const FCaptureEvent> InEvent)
        {
            auto ProgressEvent = StaticCastSharedPtr<const FMyProgressEvent>(InEvent);
            UE_LOG(LogTemp, Log, TEXT("Progress: %.1f%%"), ProgressEvent->Progress * 100.0);
        },
        EDelegateExecutionThread::GameThread
    )
);
```

**限频事件源**（`FCaptureEventSourceWithLimiter`）：适用于高频更新场景（如进度报告），可限制事件发布频率：

```cpp
// 基于 EventSourceUtils.h
class FHighFreqDevice : public FCaptureEventSourceWithLimiter
{
public:
    FHighFreqDevice()
        : FCaptureEventSourceWithLimiter(100) // 最低 100ms 间隔
    {
        RegisterEvent(FMyProgressEvent::Name);
    }

    void OnDataReceived(double InProgress)
    {
        // 仅当距上次发布超过 100ms 时才真正发布；否则丢弃
        PublishIfThresholdReached<FMyProgressEvent>(false, InProgress);
    }

    void OnFinalData(double InProgress)
    {
        // 强制发布（忽略阈值），并重置时间戳
        PublishIfThresholdReached<FMyProgressEvent>(true, InProgress);
    }
};
```

### 线程安全委托

```cpp
// 基于 ManagedDelegate.h

// TManagedDelegate — 单播委托，支持指定执行线程
TManagedDelegate<FString> OnStatusChanged(
    [](FString InStatus)
    {
        // 这个 lambda 会在 GameThread 上执行
        GEngine->AddOnScreenDebugMessage(-1, 5.0f, FColor::Green, InStatus);
    },
    EDelegateExecutionThread::GameThread
);

OnStatusChanged(TEXT("Recording started"));

// TManagedMulticastDelegate — 多播委托
TManagedMulticastDelegate<float, float> OnPositionUpdated;

OnPositionUpdated.Add(
    [](float X, float Y)
    {
        UE_LOG(LogTemp, Log, TEXT("Position: (%.2f, %.2f)"), X, Y);
    },
    EDelegateExecutionThread::GameThread
);

// 发布（可从任意线程调用）
OnPositionUpdated(1.0f, 2.0f);
```

**委托执行线程选项**（`EDelegateExecutionThread`）：
- `GameThread` — 回调在 GameThread 执行
- `InternalThread` — 回调在调用方当前线程执行
- `AnyThread` — 回调在任意可用线程执行

### 可取消异步任务与停止令牌

```cpp
// 基于 Task.h 和 StopToken.h

// 创建可取消的异步任务
FCancelableAsyncTask Task([/*捕获列表*/](const FStopToken& InStopToken)
{
    for (int32 i = 0; i < 1000; ++i)
    {
        if (InStopToken.IsStopRequested())
        {
            UE_LOG(LogTemp, Warning, TEXT("Task cancelled at step %d"), i);
            return;
        }
        // 执行耗时操作...
        FPlatformProcess::Sleep(0.01f);
    }
});

// 异步启动（在后台线程执行）
Task.StartAsync();

// 同步启动（阻塞当前线程）
// Task.StartSync();

// 检查是否完成
if (Task.IsDone())
{
    UE_LOG(LogTemp, Log, TEXT("Task completed"));
}

// 取消任务
Task.Cancel();
```

**独立使用停止令牌**（用于自定义循环）：

```cpp
// 基于 StopToken.h
FStopRequester Requester;

// 创建令牌并传递给工作线程
FStopToken Token = Requester.CreateToken();

AsyncTask(ENamedThreads::AnyBackgroundThreadNormalTask, [Token]()
{
    while (!Token.IsStopRequested())
    {
        // 持续处理...
    }
});

// 从另一个线程请求停止
Requester.RequestStop();
```

### 任务进度追踪

```cpp
// 基于 TaskProgress.h

// 创建进度追踪器（3 个子任务，完成时回调）
auto Progress = MakeShared<FTaskProgress>(3,
    FTaskProgress::FProgressReporter::CreateLambda([](double InProgress)
    {
        UE_LOG(LogTemp, Log, TEXT("Overall progress: %.1f%%"), InProgress * 100.0);
    })
);

// 可选：设置汇报阈值（进度变化超过此百分比才触发回调）
Progress->SetReportThreshold(0.05); // 5%

// 启动子任务并更新进度
auto Task1 = Progress->StartTask();
auto Task2 = Progress->StartTask();
auto Task3 = Progress->StartTask();

Task1.Update(0.5);  // 子任务 1 完成 50%
Task2.Update(1.0);  // 子任务 2 完成 100%
Task1.Update(1.0);  // 子任务 1 完成 100%
Task3.Update(1.0);  // 子任务 3 完成 100%

// 获取总进度
double Total = Progress->GetTotalProgress();
```

### 回调同步器

```cpp
// 基于 CallbackSynchronizer.h

// 创建回调同步器
auto Sync = FCallbackSynchronizer::Create();

// 创建回调包装器（自动计数）
auto Callback1 = Sync->CreateCallback([]()
{
    UE_LOG(LogTemp, Log, TEXT("Step 1 done"));
});

auto Callback2 = Sync->CreateCallback([]()
{
    UE_LOG(LogTemp, Log, TEXT("Step 2 done"));
});

// 当所有回调都执行完毕后触发
Sync->AfterAll(FCallbackSynchronizer::FAfterAllDelegate::CreateLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("All steps completed!"));
}));

// 在不同线程/时间点执行回调
AsyncTask(ENamedThreads::AnyBackgroundNormalThreadNormalTask, [Callback1]()
{
    // 做一些工作...
    Callback1(); // 计数器 -1
});

// 当 Callback1 和 Callback2 都被调用后，AfterAll 自动触发
```

### TCP 网络通信

**TCP 服务器端**：

```cpp
// 基于 Network/TcpServer.h
using namespace UE::CaptureManager;

// 创建 TCP 服务器（最多 5 个客户端）
FTcpServer Server(5);

// 设置连接处理回调
Server.SetConnectionHandler(
    FTcpServer::FConnectionHandler::CreateLambda(
        [](TWeakPtr<FTcpClientHandler> InClient, bool bConnected)
        {
            if (bConnected)
            {
                UE_LOG(LogTemp, Log, TEXT("Client connected: %s"),
                    InClient.Pin()->GetEndpoint());
            }
            else
            {
                UE_LOG(LogTemp, Log, TEXT("Client disconnected"));
            }
        }
    )
);

// 启动服务器（OS 自动分配端口）
TProtocolResult<uint16> Result = Server.Start(FTcpServer::AnyPort);
if (Result.HasValue())
{
    uint16 Port = Result.GetValue();
    UE_LOG(LogTemp, Log, TEXT("Server listening on port %d"), Port);
}

// 发送消息到指定客户端
TArray<uint8> Data;
Server.SendMessage(Data, TEXT("192.168.1.100:12345"));

// 断开指定客户端
Server.DisconnectClient(TEXT("192.168.1.100:12345"));

// 停止服务器
Server.Stop();
```

**TCP 客户端**：

```cpp
// 基于 Network/TcpClient.h
using namespace UE::CaptureManager;

FTcpClient Client;
Client.Init();

// 阻塞连接到服务器
TProtocolResult<void> ConnectResult = Client.Start(TEXT("127.0.0.1:8080"));
if (ConnectResult.HasError())
{
    UE_LOG(LogTemp, Error, TEXT("Connection failed: %s"),
        *ConnectResult.GetError().GetMessage());
    return;
}

// 发送数据
TArray<uint8> Payload = { 0x01, 0x02, 0x03 };
Client.SendMessage(Payload);

// 接收数据（阻塞等待，超时 1000ms）
TProtocolResult<TArray<uint8>> RecvResult = Client.ReceiveMessage(
    1024,                              // 期望接收字节数
    ITcpSocketReader::DefaultWaitTimeoutMs  // 超时毫秒数
);

if (RecvResult.HasValue())
{
    TArray<uint8> ReceivedData = RecvResult.GetValue();
    // 处理数据...
}

Client.Stop();
```

### UDP 客户端

```cpp
// 基于 Network/UdpClient.h
using namespace UE::CaptureManager;

FUdpClient UdpClient;

// 配置
FUdpClientConfigure Config;
Config.ListenPort = 9000;
Config.MulticastIpAddress = TEXT("239.0.0.1");

// 初始化（设置数据接收回调）
UdpClient.Init(Config, FOnSocketDataReceived::CreateLambda(
    [](const FArrayReaderPtr& InData, const FIPv4Endpoint& InEndpoint)
    {
        UE_LOG(LogTemp, Log, TEXT("Received UDP data from %s"), *InEndpoint.ToString());
    }
));

UdpClient.Start();

// 发送数据到指定端点
TArray<uint8> Payload;
UdpClient.SendMessage(Payload, TEXT("192.168.1.200:9001"));

UdpClient.Stop();
```

### 协议错误处理

```cpp
// 基于 Network/Error.h
using namespace UE::CaptureManager;

// TProtocolResult 是通用的结果类型：Value 或 Error
TProtocolResult<TArray<uint8>> Result = SomeNetworkCall();

if (Result.HasValue())
{
    TArray<uint8> Data = Result.GetValue();
    // 正常处理...
}
else if (Result.HasError())
{
    const FCaptureProtocolError& Error = Result.GetError();
    UE_LOG(LogTemp, Error, TEXT("Error [%d]: %s"),
        Error.GetCode(), *Error.GetMessage());
}

// 返回成功
TProtocolResult<void> OkResult = ResultOk;  // 预定义的成功结果

// 返回失败
TProtocolResult<void> FailResult = FCaptureProtocolError(TEXT("Connection timeout"), -1);
```

### 资产路径清理

```cpp
// 基于 Asset/CaptureAssetSanitization.h
using namespace UE::CaptureManager;

FString PackagePath = TEXT("/Game/Captures/Session 01/My:Asset!Name");
SanitizePackagePath(PackagePath);
// 结果: "/Game/Captures/Session_01/My_Asset_Name"

FString AssetName = TEXT("Take 01 [Frame 001]");
SanitizeAssetName(AssetName);
// 结果: "Take_01__Frame_001_"
```

### 外部进程执行

```cpp
// 基于 Internal/ProcessRunner/ProcessRunner.h
using namespace UE::CaptureManager;

// 运行外部进程（如 FFmpeg 转码）
FStopToken StopToken = /* ... */;
TOptional<int32> Timeout = 60; // 60 秒超时

FProcessRunnerResult Result = FProcessRunner::Run(
    TEXT("ffmpeg"),
    TEXT("-i input.mp4 -c:v libx264 output.mp4"),
    &StopToken,
    Timeout
);

if (Result.HasValue())
{
    TArray<uint8> Stdout = Result.GetValue();
    // 处理进程输出...
}
else
{
    EProcessRunnerError Error = Result.GetError();
    // 处理错误...
}
```

### 其他工具函数

```cpp
// 基于 Async/HelperFunctions.h
using namespace UE::CaptureManager;

// 在 GameThread 上执行函数并等待完成
CallOnGameThread([]()
{
    UGameplayStatics::GetPlayerController(GWorld, 0)->ConsoleCommand(TEXT("stat fps"));
});
```

```cpp
// 基于 Network/NetworkMisc.h
using namespace UE::CaptureManager;

TOptional<FString> Ip = GetLocalIpAddress();
TOptional<FString> HostName = GetLocalHostName();
FString HostNameChecked = GetLocalHostNameChecked(); // 无值时返回默认值
```

## Demo 示例

一个完整的最小示例：自定义事件源 + 可取消异步任务 + 进度追踪。

```cpp
// MyCaptureTask.h
#pragma once

#include "Async/Event.h"
#include "Async/EventSourceUtils.h"
#include "Async/Task.h"
#include "Async/TaskProgress.h"
#include "Async/StopToken.h"

namespace UE::CaptureManager
{

CAPTURE_DEFINE_EMPTY_EVENT(FScanStarted, "ScanStarted");

struct FScanProgressEvent : public FCaptureEvent
{
    static inline const FString Name = TEXT("ScanProgress");
    double Progress;
    FScanProgressEvent(double InProgress)
        : FCaptureEvent(Name), Progress(InProgress) {}
};

CAPTURE_DEFINE_EMPTY_EVENT(FScanCompleted, "ScanCompleted");
CAPTURE_DEFINE_EMPTY_EVENT(FScanCancelled, "ScanCancelled");

class FMyCaptureDevice : public FCaptureEventSource
{
public:
    FMyCaptureDevice()
    {
        RegisterEvent(FScanStarted::Name);
        RegisterEvent(FScanProgressEvent::Name);
        RegisterEvent(FScanCompleted::Name);
        RegisterEvent(FScanCancelled::Name);
    }

    void StartScan();
    void CancelScan();

private:
    FStopRequester StopRequester;
    FCancelableAsyncTask* AsyncTask = nullptr;
};

} // namespace UE::CaptureManager
```

```cpp
// MyCaptureTask.cpp
#include "MyCaptureTask.h"
#include "Async/HelperFunctions.h"

namespace UE::CaptureManager
{

void FMyCaptureDevice::StartScan()
{
    PublishEvent<FScanStarted>();

    // 创建进度追踪器（1 个子任务）
    auto Progress = MakeShared<FTaskProgress>(1,
        FTaskProgress::FProgressReporter::CreateLambda([WeakThis = AsWeak()](double InProgress)
        {
            if (auto Self = WeakThis.Pin())
            {
                StaticCastSharedPtr<FMyCaptureDevice>(Self)
                    ->PublishEvent<FScanProgressEvent>(InProgress);
            }
        })
    );

    FStopToken Token = StopRequester.CreateToken();
    auto Task = MakeUnique<FCancelableAsyncTask>(
        [Token, Progress](const FStopToken& InStopToken)
        {
            auto SubTask = Progress->StartTask();
            for (int32 i = 0; i <= 100; ++i)
            {
                if (InStopToken.IsStopRequested())
                {
                    return;
                }
                FPlatformProcess::Sleep(0.05f);
                SubTask.Update(static_cast<double>(i) / 100.0);
            }
        }
    );

    Task->StartAsync();
}

void FMyCaptureDevice::CancelScan()
{
    StopRequester.RequestStop();
    PublishEvent<FScanCancelled>();
}

} // namespace UE::CaptureManager
```

**使用方**（在 GameThread 上订阅事件）：

```cpp
auto Device = MakeShared<UE::CaptureManager::FMyCaptureDevice>();

Device->SubscribeToEvent(
    UE::CaptureManager::FScanProgressEvent::Name,
    UE::CaptureManager::FCaptureEventHandler(
        [](TSharedPtr<const UE::CaptureManager::FCaptureEvent> InEvent)
        {
            auto E = StaticCastSharedPtr<const UE::CaptureManager::FScanProgressEvent>(InEvent);
            UE_LOG(LogTemp, Log, TEXT("Scan progress: %.0f%%"), E->Progress * 100.0);
        },
        UE::CaptureManager::EDelegateExecutionThread::GameThread
    )
);

Device->StartScan();

// 5 秒后取消
FTimerHandle Handle;
GWorld->GetTimerManager().SetTimer(Handle, [Device]()
{
    Device->CancelScan();
}, 5.0f, false);
```

## 模块依赖

本文档聚焦的 **CaptureUtils** 模块的 Build.cs 未完整提供，但根据源码分析，它依赖以下 UE 模块：

| 模块 | 用途 |
|---|---|
| `Sockets` | TCP/UDP 底层 Socket API (`FSocket`) |
| `Networking` | `FTcpListener`、`FUdpSocketReceiver` 等 |
| `Json` | JSON 解析（被其他模块使用） |
| `MediaUtils` | 媒体工具（跨模块共享） |

其余 10 个模块（CaptureDataConverter、CaptureProtocolStack 等）可能有各自独特的依赖，本节仅列出 CaptureUtils 模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `a2e4a9e3` | Forward the stop token to third-party encoder commands so audio and video conversion can be cancelle | 转发 StopToken 到第三方编码器命令，支持音视频转换中途取消 |
| 2026-05-12 | `218704d7` | [CaptureManager] Added missing fix from 51621159 which was dropped during conversion module move. | 补充之前模块迁移时遗漏的修复 |
| 2026-05-12 | `16e184f7` | [CaptureManager] Fix transaction ID data race causing transient download failures. | 修复事务 ID 数据竞争导致的偶发下载失败 |
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以支持 FString 和 FSharedString |
| 2026-04-30 | `d6f72591` | [CaptureManager] Add CaptureManagerDeviceBlueprint module | 新增 CaptureManagerDeviceBlueprint 模块 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2025-02-04，插件较为年轻（约 1 年），仍在积极开发阶段
- **更新频率**：近 1 个月内有多次实质性提交，包括新模块添加、bug 修复和架构改进
- **代码质量**：模块划分清晰（11 个独立模块），异步工具设计成熟（事件系统、可取消任务、线程安全委托等），有完善的线程安全保障
- **已知限制**：插件默认未启用（`EnabledByDefault=false`），表明仍在完善中，可能不是所有功能都经过充分验证
- **推荐程度**：如果你在使用 Capture Manager 生态（App 或 Editor 插件），本插件是**必须依赖**的基础模块。不建议将其工具类独立用于其他项目，因为 API 未设计为通用用途

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerCore)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- [CaptureManager App 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerApp)（依赖方）
- [CaptureManager Editor 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CaptureManager/CaptureManagerEditor)（依赖方）