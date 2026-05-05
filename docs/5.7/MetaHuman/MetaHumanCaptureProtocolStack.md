# MetaHuman Capture Protocol Stack

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## ⚠️ 废弃警告

**本模块 `MetaHumanCaptureProtocolStack` 已在 UE 5.7 中被标记为废弃（Deprecated）。** 其功能已迁移至 `CaptureManagerCore/CaptureProtocolStack` 模块。本文档仅作历史参考，新项目应使用新模块。

## 用途

`MetaHumanCaptureProtocolStack` 是 MetaHuman Animator 插件中的**网络协议栈模块**，用于与外部面部捕捉设备（如运行 Live Link Face 的 iPhone）进行通信。它实现了一套完整的三层网络协议：

1. **发现层（Discovery）**：通过 UDP 多播在网络上自动发现可用的捕捉设备
2. **控制层（Control）**：通过 TCP 连接发送 JSON 格式的控制命令（开始/停止会话、录制、获取设备信息等）
3. **导出层（Export）**：通过 TCP 连接以二进制协议从设备下载捕捉数据（视频帧、深度数据等）

这个模块解决的核心问题是：**如何在 Unreal Engine 中与运行 MetaHuman 捕捉应用的移动设备建立可靠的双向通信，并管理捕捉数据的传输**。它是 MetaHuman Animator 工作流中"从设备获取面部表演数据"这一环节的底层通信基础。

## 使用场景

- 你正在使用 MetaHuman Animator 工作流，需要从 iPhone（运行 Live Link Face）捕获面部表演数据
- 你需要在局域网中自动发现可用的捕捉设备
- 你需要控制远程设备的录制会话（开始/停止录制、管理 Takes）
- 你需要从捕捉设备导出视频帧和深度数据到 Unreal Engine

**注意**：由于此模块已废弃，新项目应使用 `CaptureManagerCore/CaptureProtocolStack` 模块。

## 蓝图用法

本模块为纯 C++ 运行时模块，**不包含 BlueprintCallable 节点**。所有 API 均为 C++ 接口，供 MetaHuman Animator 插件的其他模块（如 `MetaHumanCaptureSource`、`MetaHumanFootageIngest`）内部调用。

## C++ 用法

### 头文件引入

```cpp
#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"
#include "ExportClient/ExportClient.h"
```

### 基本用法 — 设备发现

通过 UDP 多播在网络上发现 MetaHuman 捕捉设备：

```cpp
#include "Discovery/DiscoveryMessenger.h"

// 创建发现信使
FDiscoveryMessenger DiscoveryMessenger;

// 设置响应回调 — 设备回复发现请求时触发
DiscoveryMessenger.SetResponseHandler(
    FDiscoveryMessenger::FOnResponseArrived::CreateLambda(
        [](FDiscoveryResponse InResponse)
        {
            // 获取设备的控制端口，用于后续 TCP 连接
            uint16 ControlPort = InResponse.GetControlPort();
            const auto& ServerId = InResponse.GetServerId();
            const auto& SupportedVersions = InResponse.GetSupportedVersions();
            
            UE_LOG(LogTemp, Log, TEXT("发现设备，控制端口: %d"), ControlPort);
        }
    )
);

// 设置通知回调 — 设备上线/下线时触发
DiscoveryMessenger.SetNotifyHandler(
    FDiscoveryMessenger::FOnNotifyArrived::CreateLambda(
        [](FDiscoveryNotify InNotify)
        {
            if (InNotify.GetConnectionState() == FDiscoveryNotify::EConnectionState::Online)
            {
                UE_LOG(LogTemp, Log, TEXT("设备上线"));
            }
        }
    )
);

// 启动发现服务并发送多播请求
DiscoveryMessenger.Start();
DiscoveryMessenger.SendMulticastRequest();

// ... 使用完毕后停止
DiscoveryMessenger.Stop();
```

### 基本用法 — 控制连接

与已发现的设备建立 TCP 控制连接，发送命令：

```cpp
#include "Control/ControlMessenger.h"

// 创建控制信使
FControlMessenger ControlMessenger;

// 注册更新处理器（设备主动推送的状态变更）
ControlMessenger.RegisterUpdateHandler(
    UE::CPS::AddressPaths::GRecordingStatus,
    FControlUpdate::FOnUpdateMessage::CreateLambda(
        [](TSharedPtr<FControlUpdate> InUpdate)
        {
            if (auto* RecordingUpdate = static_cast<FRecordingStatusUpdate*>(InUpdate.Get()))
            {
                bool bRecording = RecordingUpdate->IsRecording();
                UE_LOG(LogTemp, Log, TEXT("录制状态变更: %s"), bRecording ? TEXT("录制中") : TEXT("已停止"));
            }
        }
    )
);

// 注册断连处理器
ControlMessenger.RegisterDisconnectHandler(
    FControlMessenger::FOnDisconnect::CreateLambda(
        [](const FString& InCause)
        {
            UE_LOG(LogTemp, Warning, TEXT("设备断开连接: %s"), *InCause);
        }
    )
);

// 连接到设备（阻塞直到连接建立）
TProtocolResult<void> ConnectResult = ControlMessenger.Start(TEXT("192.168.1.100"), 14444);
if (ConnectResult.IsError())
{
    UE_LOG(LogTemp, Error, TEXT("连接失败: %s"), *ConnectResult.ClaimError().GetMessage());
    return;
}

// 开始会话
TProtocolResult<void> SessionResult = ControlMessenger.StartSession();
if (SessionResult.IsError())
{
    UE_LOG(LogTemp, Error, TEXT("开始会话失败"));
    return;
}

// 获取设备信息
TProtocolResult<FGetServerInformationResponse> InfoResult = ControlMessenger.GetServerInformation();
if (!InfoResult.IsError())
{
    const auto& Info = InfoResult.GetValue();
    UE_LOG(LogTemp, Log, TEXT("设备: %s, 平台: %s %s"),
        *Info.GetName(), *Info.GetPlatformName(), *Info.GetPlatformVersion());
}

// 开始录制一个 Take
FStartRecordingTakeRequest RecordRequest(
    TEXT("MySlate"),    // Slate 名称
    1,                  // Take 编号
    TOptional<FString>(TEXT("Subject1")),  // 可选：主题
    TOptional<FString>(TEXT("Scenario1")), // 可选：场景
    TOptional<TArray<FString>>()           // 可选：标签
);

auto RecordResult = ControlMessenger.SendRequest(RecordRequest);
if (!RecordResult.IsError())
{
    UE_LOG(LogTemp, Log, TEXT("录制已开始"));
}

// ... 录制完成后停止
FStopRecordingTakeRequest StopRequest;
auto StopResult = ControlMessenger.SendRequest(StopRequest);

// 停止会话并断开
ControlMessenger.Stop();
```

### 进阶用法 — 导出捕捉数据

从设备导出已录制的 Take 数据：

```cpp
#include "ExportClient/ExportClient.h"

// 创建导出客户端（需要设备的导出端口，从 GetServerInformation 获取）
FExportClient ExportClient(TEXT("192.168.1.100"), /*ExportPort*/ 15555);

// 定义要导出的文件列表
TArray<FTakeFile> Files;
Files.Add({ TEXT("video.mp4"), /*Length*/ 0, /*Offset*/ 0 });
Files.Add({ TEXT("depth.bin"), /*Length*/ 0, /*Offset*/ 0 });

// 创建流用于接收数据（实际实现取决于你的存储需求）
// TUniquePtr<FBaseStream> Stream = MakeUnique<FYourFileStream>(...);

// 提交导出任务
FExportClient::FTaskId TaskId = ExportClient.ExportTakeFiles(
    TEXT("MySlate_001"),  // Take 名称
    Files,
    MoveTemp(Stream)
);

// 可以取消导出
// ExportClient.AbortExport(TaskId);

// 或取消所有导出
// ExportClient.AbortAllExports();
```

### 进阶用法 — 自定义 TCP 通信

直接使用底层 TCP/UDP 客户端进行自定义通信：

```cpp
#include "Communication/TcpClient.h"
#include "Communication/UdpClient.h"

// TCP 客户端示例
FTcpClient TcpClient;
TcpClient.Init();
TcpClient.Start(TEXT("192.168.1.100:8080"));

// 发送数据
TArray<uint8> Payload;
// ... 填充数据
TcpClient.SendMessage(Payload);

// 接收数据
auto Received = TcpClient.ReceiveMessage(/*Size*/ 1024, /*TimeoutMs*/ 5000);
if (!Received.IsError())
{
    TArray<uint8> Data = Received.GetValue();
    // 处理数据...
}

TcpClient.Stop();

// UDP 客户端示例（用于发现）
FUdpClient UdpClient;
FUdpClientConfigure Config;
Config.ListenPort = 14445;
Config.MulticastIpAddress = TEXT("239.255.255.250");

UdpClient.Init(Config, [](const FArrayReaderPtr& Payload, const FIPv4Endpoint& Endpoint)
{
    // 处理接收到的 UDP 数据包
});
UdpClient.Start();

// 发送 UDP 消息
TArray<uint8> DiscoveryPayload;
UdpClient.SendMessage(DiscoveryPayload, TEXT("239.255.255.250"));

UdpClient.Stop();
```

## Demo 示例

一个完整的设备发现与控制示例：

```cpp
// MetaHumanCaptureDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Discovery/DiscoveryMessenger.h"
#include "Control/ControlMessenger.h"

class FMetaHumanCaptureDemo
{
public:
    void StartDiscovery();
    void ConnectToDevice(const FString& InIp, uint16 InControlPort);
    void StartRecording(const FString& InSlateName, uint16 InTakeNumber);
    void StopRecording();
    void Disconnect();

private:
    TUniquePtr<FDiscoveryMessenger> Discovery;
    TUniquePtr<FControlMessenger> Control;
    bool bConnected = false;
};
```

```cpp
// MetaHumanCaptureDemo.cpp
#include "MetaHumanCaptureDemo.h"

void FMetaHumanCaptureDemo::StartDiscovery()
{
    Discovery = MakeUnique<FDiscoveryMessenger>();

    Discovery->SetResponseHandler(
        FDiscoveryMessenger::FOnResponseArrived::CreateLambda(
            [this](FDiscoveryResponse InResponse)
            {
                uint16 ControlPort = InResponse.GetControlPort();
                UE_LOG(LogTemp, Log, TEXT("发现设备，控制端口: %d"), ControlPort);
                // 自动连接到第一个发现的设备
                // ConnectToDevice(TEXT("192.168.1.100"), ControlPort);
            }
        )
    );

    Discovery->Start();
    Discovery->SendMulticastRequest();
}

void FMetaHumanCaptureDemo::ConnectToDevice(const FString& InIp, uint16 InControlPort)
{
    Control = MakeUnique<FControlMessenger>();

    Control->RegisterDisconnectHandler(
        FControlMessenger::FOnDisconnect::CreateLambda(
            [this](const FString& InCause)
            {
                bConnected = false;
                UE_LOG(LogTemp, Warning, TEXT("断开: %s"), *InCause);
            }
        )
    );

    auto Result = Control->Start(InIp, InControlPort);
    if (Result.IsError())
    {
        UE_LOG(LogTemp, Error, TEXT("连接失败"));
        return;
    }

    auto SessionResult = Control->StartSession();
    if (!SessionResult.IsError())
    {
        bConnected = true;
        UE_LOG(LogTemp, Log, TEXT("已连接并开始会话"));
    }
}

void FMetaHumanCaptureDemo::StartRecording(const FString& InSlateName, uint16 InTakeNumber)
{
    if (!bConnected || !Control) return;

    FStartRecordingTakeRequest Request(InSlateName, InTakeNumber);
    auto Result = Control->SendRequest(Request);
    if (Result.IsError())
    {
        UE_LOG(LogTemp, Error, TEXT("开始录制失败"));
    }
}

void FMetaHumanCaptureDemo::StopRecording()
{
    if (!bConnected || !Control) return;

    FStopRecordingTakeRequest Request;
    auto Result = Control->SendRequest(Request);
    if (Result.IsError())
    {
        UE_LOG(LogTemp, Error, TEXT("停止录制失败"));
    }
}

void FMetaHumanCaptureDemo::Disconnect()
{
    if (Control)
    {
        Control->Stop();
        Control.Reset();
    }
    if (Discovery)
    {
        Discovery->Stop();
        Discovery.Reset();
    }
    bConnected = false;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- 77f392c7c872 [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 9afffeda15e1 [Backout] - CL45863710 [FYI] peter.wigg #rnx Original CL Desc ----------------------------------------------------------------- [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 207cd4d313ff [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
```

### 维护评价

**⚠️ 此模块已被废弃，不推荐使用。**

- **创建时间**：2024-02-02，约 1 年历史
- **最近更新**：最近 3 次 commit 全部是废弃标记操作，无功能性更新
- **废弃状态**：所有主要类（`FDiscoveryMessenger`、`FDiscoveryResponse`、`FDiscoveryNotify`、`FControlMessenger`、`FControlMessage`、`FControlRequest`、`FControlResponse`、`FControlUpdate`、`FExportClient`、`FJsonUtility` 等）均已标记 `UE_DEPRECATED(5.7, ...)`
- **迁移目标**：功能已迁移至 `CaptureManagerCore/CaptureProtocolStack` 模块
- **注意**：commit 历史显示有一次 backout（回退），说明废弃过程经历了反复确认

**建议**：如果你正在开发新功能，请直接使用 `CaptureManagerCore/CaptureProtocolStack` 模块。如果你的项目已在使用此模块，应尽快规划迁移。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack)
- [MetaHuman Animator 插件根目录](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- 迁移目标模块：`CaptureManagerCore/CaptureProtocolStack`