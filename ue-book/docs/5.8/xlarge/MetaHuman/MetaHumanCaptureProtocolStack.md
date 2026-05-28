# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、工作流工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 插件是 Epic Games 提供的官方工具集，旨在简化从性能捕获数据（如 iPhone 上的 LiveLink Face 应用记录的视频）到最终 UE5 中 MetaHuman 角色面部动画的完整工作流程。它不仅仅是一个单一工具，而是一个包含多个子模块的生态系统，覆盖了从数据导入、面部追踪、解算、拟合到最终动画生成和编辑的各个环节。

插件的核心目的是将昂贵的、需要专业动捕设备和复杂后期处理的面部动画制作流程，转化为一个在 UE5 编辑器内即可完成的、相对自动化的过程。它解决了从消费级捕获设备（如手机）获取高质量、可直接用于生产的面部动画数据的问题。

## 使用场景

*   **快速面部动画制作**：你使用 iPhone 的 LiveLink Face 应用录制了一段表演视频 → 将视频导入 UE5 → 使用 MetaHuman Animator 工具自动生成驱动 MetaHuman 角色的动画序列。
*   **编辑器内动画编辑**：你已经通过外部动捕获得了基础面部动画 → 将其导入 UE5 → 使用插件的编辑工具（如 MetaHuman Performance）在 Sequencer 中进行精细调整、混合和修正。
*   **批量处理**：你需要为多个角色或多个表演片段重复相同的捕获和动画生成流程 → 使用 MetaHuman BatchProcessor 工具进行批量自动化处理。
*   **集成第三方捕获数据**：你拥有来自其他设备（非 iPhone）的面部捕获数据（如深度视频或标记点数据）→ 通过插件提供的接口和工具（如 MetaHumanCaptureSource）进行适配和导入。

## 蓝图用法

**注意**：MetaHuman Animator 主要是一个编辑器工具集，其核心功能和工作流通过编辑器面板、资产操作和 Sequencer 扩展提供，而非直接暴露大量蓝图可调用节点。大部分高级自动化应通过 C++ 或编辑器脚本（Python）实现。

### 核心节点

基于源码分析，此插件（特别是其当前审查的模块 `MetaHumanCaptureProtocolStack`）主要提供 C++ 网络协议接口，并未在提供的代码片段中找到标记为 `BlueprintCallable` 的公开函数。其功能通常通过更高级的编辑器UI工具（如“MetaHuman Performance”资产的编辑器界面）来使用。

## C++ 用法

**警告**：提供的代码片段显示，`MetaHumanCaptureProtocolStack` 模块中的绝大部分接口已在 UE 5.7 中被标记为 `UE_DEPRECATED`，并建议迁移到 `CaptureManagerCore/CaptureProtocolStack` 模块。以下示例展示的是该模块在废弃前的典型用法，仅用于理解其设计，**新项目不应使用此模块**。

### 头文件引入

```cpp
#include "ControlMessenger.h"
#include "ControlRequest.h"
#include "ControlResponse.h"
#include "DiscoveryMessenger.h"
```

### 基本用法

以下代码展示了如何使用 `FDiscoveryMessenger` 发现局域网中的捕获设备，以及使用 `FControlMessenger` 与已发现的设备建立会话并查询信息。

**来源文件路径**: `Public/Discovery/DiscoveryMessenger.h`, `Public/Control/ControlMessenger.h`

```cpp
// 1. 发现设备
PRAGMA_DISABLE_DEPRECATION_WARNINGS
FDiscoveryMessenger DiscoveryMessenger;

// 设置响应和通知处理器
DiscoveryMessenger.SetResponseHandler(FDiscoveryMessenger::FOnResponseArrived::CreateLambda([](FDiscoveryResponse InResponse) {
    UE_LOG(LogTemp, Log, TEXT("Found device with ControlPort: %d"), InResponse.GetControlPort());
}));

// 启动并发送发现请求
if (DiscoveryMessenger.Start() == EResult::Ok) {
    DiscoveryMessenger.SendMulticastRequest();
}

// 2. 连接到设备并控制会话
FControlMessenger ControlMessenger;

// 注册更新和断开处理器
ControlMessenger.RegisterUpdateHandler(UE::CPS::AddressPaths::GRecordingStatus, 
    FControlUpdate::FOnUpdateMessage::CreateLambda([](TSharedPtr<FControlUpdate> InUpdate) {
    if (auto* StatusUpdate = static_cast<FRecordingStatusUpdate*>(InUpdate.Get())) {
        UE_LOG(LogTemp, Log, TEXT("Recording Status: %s"), StatusUpdate->IsRecording() ? TEXT("Recording") : TEXT("Idle"));
    }
}));

// 启动连接（需要设备IP和端口）
TProtocolResult<void> StartResult = ControlMessenger.Start(TEXT("192.168.1.100"), 12345);
if (StartResult.IsOk()) {
    // 开始会话
    TProtocolResult<void> SessionResult = ControlMessenger.StartSession();
    
    // 查询服务器信息
    TProtocolResult<FGetServerInformationResponse> InfoResult = ControlMessenger.GetServerInformation();
    if (InfoResult.IsOk()) {
        const auto& Info = InfoResult.GetResult();
        UE_LOG(LogTemp, Log, TEXT("Connected to: %s (v%s)"), *Info.GetName(), *Info.GetSoftwareVersion());
    }
}
PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

### 进阶用法

以下代码展示了如何发送一个带参数的录制请求，并处理响应。这是 `FControlMessenger` 模板化 `SendRequest` 方法的典型应用。

**来源文件路径**: `Public/Control/ControlMessenger.h`, `Public/Control/Messages/ControlRequest.h`

```cpp
PRAGMA_DISABLE_DEPRECATION_WARNINGS
// 创建一个开始录制的请求，附带拍板信息
FStartRecordingTakeRequest RecordRequest(
    TEXT("SceneA_Shot1"), // SlateName
    1,                   // TakeNumber
    TOptional<FString>(TEXT("ActorA")), // Subject
    TOptional<FString>(TEXT("Dialogue")), // Scenario
    TOptional<TArray<FString>>({TEXT("Take1"), TEXT("CloseUp")}) // Tags
);

// 同步发送请求（注意：这会阻塞当前线程最多3秒）
TProtocolResult<FStartRecordingTakeResponse> RecordResult = ControlMessenger.SendRequest(RecordRequest);

if (RecordResult.IsOk()) {
    UE_LOG(LogTemp, Log, TEXT("Recording started successfully."));
} else {
    UE_LOG(LogTemp, Error, TEXT("Failed to start recording: %s"), *RecordResult.GetError().GetMessage());
}

// 或者，使用异步发送
ControlMessenger.SendAsyncRequest<FStartRecordingTakeRequest>(
    RecordRequest,
    ControlMessenger.FOnControlResponse<FStartRecordingTakeRequest>::CreateLambda([](TProtocolResult<FStartRecordingTakeResponse> InResult) {
        // 此回调在工作线程触发，注意线程安全
        AsyncTask(ENamedThreads::GameThread, [InResult = MoveTemp(InResult)]() {
            if (InResult.IsOk()) {
                UE_LOG(LogTemp, Log, TEXT("Async recording started."));
            }
        });
    })
);
PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

## Demo 示例

以下是一个简化的控制台应用程序示例片段，演示了建立控制会话并查询设备状态的基本流程。**注意：这仅为逻辑演示，实际在 UE5 中运行需要处理模块初始化和网络事件循环。**

```cpp
// MetaHumanCPSDemo.h
#pragma once

#include "CoreMinimal.h"
#include "ControlMessenger.h"
#include "ControlRequest.h"

class FMetaHumanCPSDemo
{
public:
    void RunDemo(const FString& InServerIP, uint16 InServerPort);

private:
    PRAGMA_DISABLE_DEPRECATION_WARNINGS
    void HandleDisconnect(const FString& InCause);
    void HandleRecordingStatus(TSharedPtr<FControlUpdate> InUpdate);
    PRAGMA_ENABLE_DEPRECATION_WARNINGS
};
```

```cpp
// MetaHumanCPSDemo.cpp
#include "MetaHumanCPSDemo.h"
#include "ControlResponse.h"

void FMetaHumanCPSDemo::RunDemo(const FString& InServerIP, uint16 InServerPort)
{
    PRAGMA_DISABLE_DEPRECATION_WARNINGS
    FControlMessenger Messenger;

    // 注册回调
    Messenger.RegisterDisconnectHandler(
        FControlMessenger::FOnDisconnect::CreateRaw(this, &FMetaHumanCPSDemo::HandleDisconnect));

    Messenger.RegisterUpdateHandler(
        UE::CPS::AddressPaths::GRecordingStatus,
        FControlUpdate::FOnUpdateMessage::CreateRaw(this, &FMetaHumanCPSDemo::HandleRecordingStatus));

    // 连接
    auto ConnectResult = Messenger.Start(InServerIP, InServerPort);
    if (ConnectResult.IsError())
    {
        UE_LOG(LogTemp, Error, TEXT("Connection failed: %s"), *ConnectResult.ClaimError().GetMessage());
        return;
    }

    // 开始会话并查询状态
    auto SessionResult = Messenger.StartSession();
    if (SessionResult.IsOk())
    {
        // 查询设备信息
        auto InfoResult = Messenger.GetServerInformation();
        if (InfoResult.IsOk())
        {
            const auto& Info = InfoResult.GetResult();
            UE_LOG(LogTemp, Log, TEXT("Device Info - ID: %s, Model: %s"), *Info.GetId(), *Info.GetModel());
        }

        // 查询当前状态
        FGetStateRequest StateRequest;
        auto StateResult = Messenger.SendRequest(StateRequest);
        if (StateResult.IsOk())
        {
            const auto& State = StateResult.GetResult();
            UE_LOG(LogTemp, Log, TEXT("Device State - IsRecording: %s"), State.IsRecording() ? TEXT("True") : TEXT("False"));
        }
    }

    // 实际应用中这里需要一个事件循环来保持运行和处理更新
    // Messenger.Stop();
    PRAGMA_ENABLE_DEPRECATION_WARNINGS
}

PRAGMA_DISABLE_DEPRECATION_WARNINGS
void FMetaHumanCPSDemo::HandleDisconnect(const FString& InCause)
{
    UE_LOG(LogTemp, Warning, TEXT("Disconnected: %s"), *InCause);
}

void FMetaHumanCPSDemo::HandleRecordingStatus(TSharedPtr<FControlUpdate> InUpdate)
{
    if (auto* Status = static_cast<FRecordingStatusUpdate*>(InUpdate.Get()))
    {
        UE_LOG(LogTemp, Log, TEXT("Recording status changed: %s"), Status->IsRecording() ? TEXT("Started") : TEXT("Stopped"));
    }
}
PRAGMA_ENABLE_DEPRECATION_WARNINGS
```

## 模块依赖

从各子模块的 Build.cs 分析，此插件包含多个独立模块，彼此间存在依赖。以下列出 `MetaHumanCaptureProtocolStack` 本身没有的、插件内其他模块的独特依赖，这些依赖关系复杂且分散。

| 模块 | 用途 |
|---|---|
| `MeshTrackerInterface` | 提供网格追踪的接口定义，用于面部追踪等子系统。 |
| `MetaHumanCoreTechLib` | 核心技术库，可能包含数学、网格处理等基础算法。 |
| `ControlRigDeveloper` | 用于开发和编辑 Control Rig，驱动面部动画。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，处理资产和UI。 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数。 |
| `RHI`, `RenderCore` | 用于深度生成、纹理处理等图形渲染相关功能。 |
| `MediaUtils`, `MediaAssets` | 用于处理视频捕获数据（来自手机录像）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列的导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | (MetaHuman Animator) 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

*   **活跃度**：插件整体仍在积极维护和更新（如最近的 commit 所示）。
*   **关键警告**：当前文档聚焦的子模块 `MetaHumanCaptureProtocolStack` 已被**官方正式废弃**。所有接口标记为 `UE_DEPRECATED`，并明确指引至 `CaptureManagerCore/CaptureProtocolStack`。**新项目绝对不应使用 `MetaHumanAnimator` 中的 `MetaHumanCaptureProtocolStack` 模块，而应寻找或等待对应的 `CaptureManagerCore` 模块。**
*   **现状**：插件的其他子模块（如面部解算、拟合、性能编辑）可能仍在维护。但作为整体，由于其规模和复杂性，部分组件的废弃和迁移是生命周期的一部分。
*   **建议**：对于面部捕获协议栈的功能，请关注 `CaptureManagerCore` 插件。使用 MetaHuman Animator 插件的其他功能时，请查阅最新的官方文档，以了解其推荐工作流和 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureProtocolStack/Private/Tests) (CaptureProtocolStack 的测试位于此目录)