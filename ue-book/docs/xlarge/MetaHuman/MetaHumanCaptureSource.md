# MetaHuman Capture Source

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

`MetaHumanCaptureSource` 模块是 MetaHuman Animator 工作流中的**数据输入层**。它负责连接外部面部捕捉设备（如 iPhone 上的 LiveLinkFace 应用或专业的头部运动捕捉设备 HMC），管理捕捉会话，并将原始的视频、深度和音频数据（称为“Take”）从设备或本地存档导入到 Unreal Engine 项目中，为后续的面部动画解算（Performance）提供数据源。

**核心功能**：
1.  **设备连接与控制**：通过 IP 网络连接到运行 LiveLinkFace 应用的设备，发送开始/停止录制等命令。
2.  **Take 管理**：枚举、获取和管理设备或本地存档中的 Take 列表及其元数据（如时长、帧率、分辨率）。
3.  **数据导入（Ingest）**：将 Take 的视频、深度图等媒体文件从设备或存档复制到项目的指定目录，并创建对应的引擎资产（如 `UImgMediaSource`）。
4.  **异步处理**：支持异步导入，避免阻塞编辑器，并提供进度回调和取消功能。

**注意**：根据源码中的 `UE_DEPRECATED(5.7, ...)` 标记，此模块及其功能在 UE 5.7 中已被废弃，相关功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。新项目应使用新模块。

## 使用场景

-   你正在使用 MetaHuman Animator 工作流，需要从 iPhone 上的 **LiveLinkFace** 应用实时或离线导入面部表演数据。
-   你拥有专业的**头部运动捕捉（HMC）** 设备拍摄的立体视频存档，需要将其导入引擎进行面部动画解算。
-   你需要编写自动化脚本或蓝图，批量管理多个 Take 的导入过程。
-   你需要监控设备连接状态、录制状态以及数据导入的进度。

## 蓝图用法

`UMetaHumanCaptureSourceSync` 类提供了主要的蓝图接口，用于同步操作（适合蓝图和 Python 脚本）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Startup` | 初始化捕获源，连接设备或扫描存档目录。 | `UMetaHumanCaptureSourceSync` |
| `Refresh` | 刷新可用的 Take 列表。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeIds` | 获取所有可用 Take 的 ID 列表。 | `UMetaHumanCaptureSourceSync` |
| `GetTakeInfo` | 根据 Take ID 获取详细的 Take 信息（名称、帧数、分辨率等）。 | `UMetaHumanCaptureSourceSync` |
| `GetTakes` | 根据 Take ID 列表，获取完整的 Take 数据（包含视频、深度等资产引用）。 | `UMetaHumanCaptureSourceSync` |
| `SetTargetPath` | 设置导入数据的目标存储路径和资产文件夹路径。 | `UMetaHumanCaptureSourceSync` |
| `Shutdown` | 关闭连接，释放资源。 | `UMetaHumanCaptureSourceSync` |
| `IsProcessing` | 检查当前是否有 Take 正在导入。 | `UMetaHumanCaptureSourceSync` |
| `CancelProcessing` | 取消指定 Take 的导入过程。 | `UMetaHumanCaptureSourceSync` |

### 使用示例（蓝图描述）

1.  **创建并初始化捕获源**：
    *   在蓝图中创建一个 `UMetaHumanCaptureSourceSync` 对象。
    *   设置其 `CaptureSourceType` 属性（例如 `LiveLinkFaceConnection`）。
    *   对于网络连接类型，设置 `DeviceIpAddress` 和 `DeviceControlPort`。
    *   调用 `Startup` 节点。

2.  **获取并导入 Take**：
    *   调用 `Refresh` 节点更新 Take 列表。
    *   调用 `GetTakeIds` 获取所有 Take ID。
    *   使用 `GetTakeInfo` 遍历并显示 Take 信息给用户选择。
    *   用户选择后，调用 `SetTargetPath` 设置导入目录。
    *   调用 `GetTakes` 节点，传入选择的 Take ID 列表。此节点会触发实际的文件复制和资产创建过程。
    *   可以使用 `IsProcessing` 和 `CancelProcessing` 节点来监控和控制导入。

## C++ 用法

核心的异步操作由 `UE::MetaHuman::FIngester` 类处理，它提供了更灵活的回调和事件驱动机制。

### 头文件引入

```cpp
#include "MetaHumanCaptureSource.h"
#include "MetaHumanCaptureIngester.h"
```

### 基本用法

以下示例展示了如何创建一个 Ingester，连接到 LiveLinkFace 设备，并异步获取 Take 列表。

```cpp
// 来源: MetaHumanCaptureSource/Public/MetaHumanCaptureIngester.h
// 创建 Ingester 参数
UE::MetaHuman::FIngesterParams Params(
    EMetaHumanCaptureSourceType::LiveLinkFaceConnection, // 捕获源类型
    FDirectoryPath{TEXT("/Game/MetaHuman/Takes")},       // 本地存储路径
    FDeviceAddress{TEXT("192.168.1.100")},               // 设备 IP
    14785,                                               // 控制端口
    false, false,                                        // 压缩深度、复制图像选项
    0.0f, 1.0f,                                          // 深度范围
    EMetaHumanCaptureDepthPrecisionType::Full,
    EMetaHumanCaptureDepthResolutionType::Full
);

// 创建 Ingester 实例
TUniquePtr<UE::MetaHuman::FIngester> Ingester = MakeUnique<UE::MetaHuman::FIngester>(Params);

// 设置导入目标路径
Ingester->SetTargetPath(TEXT("/Game/MetaHuman/Imported"), TEXT("/Game/MetaHuman/Assets"));

// 启动并异步刷新 Take 列表
Ingester->Startup(ETakeIngestMode::Async);
Ingester->Refresh(UE::MetaHuman::FIngester::FRefreshCallback::CreateLambda(
    [](FMetaHumanCaptureVoidResult Result)
    {
        if (Result.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT("Take list refreshed successfully."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to refresh takes: %s"), *Result.Message);
        }
    }
));
```

### 进阶用法

监听连接状态变化和导入进度事件。

```cpp
// 来源: MetaHumanCaptureSource/Public/MetaHumanCaptureEvents.h, MetaHumanCaptureIngester.h
// 监听连接状态变化事件
Ingester->AddEventHandler<FConnectionChangedEvent>(
    [](const FConnectionChangedEvent& Event)
    {
        if (Event.ConnectionState == FConnectionChangedEvent::EState::Connected)
        {
            UE_LOG(LogTemp, Log, TEXT("Device connected."));
        }
        else if (Event.ConnectionState == FConnectionChangedEvent::EState::Disconnected)
        {
            UE_LOG(LogTemp, Warning, TEXT("Device disconnected."));
        }
    }
);

// 监听新 Take 添加事件
Ingester->AddEventHandler<FNewTakesAddedEvent>(
    [](const FNewTakesAddedEvent& Event)
    {
        for (TakeId NewTakeId : Event.NewTakes)
        {
            UE_LOG(LogTemp, Log, TEXT("New take available: %d"), NewTakeId);
        }
    }
);

// 异步导入指定的 Take，并监控进度
TArray<TakeId> TakesToImport = {1, 2, 3};
Ingester->GetTakes(TakesToImport, UE::MetaHuman::FIngester::FGetTakesCallbackPerTake::CreateLambda(
    [IngesterPtr = Ingester.Get()](FMetaHumanCapturePerTakeVoidResult PerTakeResult)
    {
        if (PerTakeResult.Result.bIsValid)
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d imported successfully."), PerTakeResult.TakeId);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to import take %d: %s"),
                PerTakeResult.TakeId, *PerTakeResult.Result.Message);
        }
    }
));

// 在 Tick 或定时器中查询进度
if (Ingester->IsProcessing())
{
    for (TakeId Id : TakesToImport)
    {
        TOptional<float> Progress = Ingester->GetProcessingProgress(Id);
        if (Progress.IsSet())
        {
            UE_LOG(LogTemp, Log, TEXT("Take %d progress: %.1f%%"), Id, Progress.GetValue() * 100.0f);
        }
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何使用 `FIngester` 连接设备并获取 Take 信息。

```cpp
// MyCaptureManager.h
#pragma once
#include "CoreMinimal.h"
#include "MetaHumanCaptureIngester.h"

class FMyCaptureManager
{
public:
    void Initialize();
    void Shutdown();

private:
    TUniquePtr<UE::MetaHuman::FIngester> CaptureIngester;
    void OnRefreshComplete(FMetaHumanCaptureVoidResult Result);
};
```

```cpp
// MyCaptureManager.cpp
#include "MyCaptureManager.h"
#include "MetaHumanCaptureSource.h"

void FMyCaptureManager::Initialize()
{
    // 配置参数：连接到 IP 为 10.0.0.5 的设备
    UE::MetaHuman::FIngesterParams Params(
        EMetaHumanCaptureSourceType::LiveLinkFaceConnection,
        FDirectoryPath{FPaths::ProjectSavedDir() / TEXT("MetaHumanCapture")},
        FDeviceAddress{TEXT("10.0.0.5")},
        14785,
        false, false, 0.0f, 1.0f,
        EMetaHumanCaptureDepthPrecisionType::Full,
        EMetaHumanCaptureDepthResolutionType::Full
    );

    CaptureIngester = MakeUnique<UE::MetaHuman::FIngester>(Params);
    CaptureIngester->SetTargetPath(
        FPaths::ProjectContentDir() / TEXT("ImportedTakes"),
        TEXT("/Game/ImportedTakes")
    );

    // 启动并刷新
    CaptureIngester->Startup(ETakeIngestMode::Async);
    CaptureIngester->Refresh(
        UE::MetaHuman::FIngester::FRefreshCallback::CreateRaw(this, &FMyCaptureManager::OnRefreshComplete)
    );
}

void FMyCaptureManager::OnRefreshComplete(FMetaHumanCaptureVoidResult Result)
{
    if (Result.bIsValid && CaptureIngester.IsValid())
    {
        int32 NumTakes = CaptureIngester->GetNumTakes();
        UE_LOG(LogTemp, Log, TEXT("Found %d takes on device."), NumTakes);

        // 获取第一个 Take 的信息作为示例
        TArray<TakeId> TakeIds = CaptureIngester->GetTakeIds();
        if (TakeIds.Num() > 0)
        {
            FMetaHumanTakeInfo TakeInfo;
            if (CaptureIngester->GetTakeInfo(TakeIds[0], TakeInfo))
            {
                UE_LOG(LogTemp, Log, TEXT("First take: %s, Frames: %d, Resolution: %dx%d"),
                    *TakeInfo.Name, TakeInfo.NumFrames, TakeInfo.Resolution.X, TakeInfo.Resolution.Y);
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to connect or refresh: %s"), *Result.Message);
    }
}

void FMyCaptureManager::Shutdown()
{
    if (CaptureIngester.IsValid())
    {
        CaptureIngester->Shutdown();
        CaptureIngester.Reset();
    }
}
```

## 模块依赖

根据模块命名和常见依赖推断，使用 `MetaHumanCaptureSource` 模块通常需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCaptureUtils` | 提供面部捕捉相关的通用工具函数和数据类型。 |
| `MetaHumanFootageIngest` | 提供底层的素材导入（Ingest）API 接口和实现。 |
| `MetaHumanCaptureProtocolStack` | 处理与捕捉设备（如 LiveLinkFace）的网络通信协议。 |
| `MediaUtils` | 处理媒体文件（视频、图像）的加载和管理。 |
| `ImageWriteQueue` | 用于异步写入图像文件（如深度图）。 |

## 维护状态

### 近期更新

```
- f207c623330f 2024-02-02 [MetaHuman] Fixed a couple of garbage collection issues during ingest.
- 77f392c7c872 2024-02-02 [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
- 9afffeda15e1 2024-02-02 [Backout] - CL45863710 [FYI] peter.wigg #rnx Original CL Desc ----------------------------------------------------------------- [MetaHumanAnimator] Deprecated CaptureSource, CaptureUtils, FootageIngest and the remainder of CaptureProtocolStack.
```

### 维护评价

**⚠️ 已废弃，不推荐新项目使用。**

-   **创建时间**：2024年2月，模块相对较新。
-   **最近更新**：最后一次实质性更新（垃圾回收修复）和**废弃标记**都发生在 2024 年 2 月。此后没有新的功能提交。
-   **维护状态**：**已废弃**。源码中大量类和结构体被标记为 `UE_DEPRECATED(5.7, ...)`，明确指出功能已迁移至 `CaptureManager/CaptureManagerDevices` 模块。
-   **已知问题/限制**：作为废弃模块，未来版本可能被移除，且不会再修复 bug 或添加新功能。
-   **推荐**：**不推荐**在新项目中使用此模块。对于 UE 5.7 及以后版本，应使用官方推荐的 `CaptureManager/CaptureManagerDevices` 模块来实现相同的面部捕捉数据导入功能。对于维护旧项目，需注意其废弃状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureSource)
-   官方文档：无
-   测试用例：未在提供的路径中发现明确的测试文件。