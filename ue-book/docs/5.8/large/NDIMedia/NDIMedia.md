# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（NDI媒体源/输出资产） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia) | |

## 用途

NDIMedia 插件为虚幻引擎提供了通过 **NDI（Network Device Interface）** 协议进行实时、低延迟音视频输入和输出的能力。它解决了在虚拟制片（Virtual Production）和广播工作流中，需要与外部基于NDI的设备（如摄像机、显示器、视频墙、导播系统）进行高效、高质量音视频数据交换的核心问题。

该插件主要包含两大功能：
1.  **媒体源（Media Source）**：将外部的NDI发送端（Sender）作为视频、音频和元数据输入流接入虚幻引擎。
2.  **媒体输出（Media Output）**：将虚幻引擎渲染的视口、渲染目标或场景捕获的视频与音频，实时编码并通过NDI协议作为流发送出去，供其他NDI接收端使用。

它旨在成为UE Media Framework的一部分，与已有的媒体播放器（Media Player）和媒体捕获（Media Capture）架构无缝集成。

## 使用场景

*   **虚拟制片（Virtual Production）**：
    *   你正在使用虚幻引擎驱动LED墙，并需要从外部NDI摄像机接收实拍画面，将其与引擎场景合成 → 使用 `UNDIMediaSource` 作为媒体源。
    *   你需要将引擎渲染的合成画面实时输出到控制LED墙的NDI接收器 → 使用 `UNDIMediaOutput` 作为媒体输出。
*   **广播与实况制作**：
    *   你希望将游戏引擎的画面作为一路信号源，通过NDI发送给导播系统（如vMix, OBS with NDI插件）进行切换和播出 → 配置 `UNDIMediaOutput`。
    *   你需要在引擎内监控来自其他应用（如OBS、Zoom）通过NDI发送的视频源 → 配置 `UNDIMediaSource`。
*   **时间码同步**：
    *   你需要使用来自外部NDI源的时间码（Timecode）来同步引擎中的动画、录制或回放 → 使用 `UNDIMediaTimecodeProvider`。
*   **调试与分析**：
    *   你需要捕获并查看外部NDI流中附带的元数据（Metadata），或向NDI源发送自定义元数据 → 通过 `FNDIStreamReceiver` 的委托或 `SendMetadataFrame` 方法实现。

## 蓝图用法

该插件的核心交互通过编辑器资产（`MediaSource`, `MediaOutput`）和少量蓝图可用的运行时对象实现。

### 核心资产

| 资产类 | 说明 | 所在模块 |
|---|---|---|
| `UNDIMediaSource` | NDI 媒体源资产。在“媒体源”资产中创建，用于配置要接收的NDI源、带宽、捕获选项（视频/音频/辅助数据）等。 | `NDIMedia` |
| `UNDIMediaOutput` | NDI 媒体输出资产。在“媒体输出”资产中创建，用于配置要输出的NDI源名称、输出类型（填充/填充与键控）、视频格式、音频设置等。 | `NDIMedia` |
| `UNDIMediaTimecodeProvider` | NDI 时间码提供程序资产。用于从指定的NDI源获取时间码，并可设置为引擎的时间码提供程序。 | `NDIMedia` |

### 核心节点（在 C++ 公开，蓝图通常不直接调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetPerformanceData` | 获取接收器的性能数据（帧计数、丢帧数等）。 | `FNDIStreamReceiver` |
| `SendMetadataFrame` | 向已连接的NDI发送端发送一帧XML格式的元数据。 | `FNDIStreamReceiver` |

### 使用示例（蓝图描述）

1.  **接收NDI视频**：
    *   在内容浏览器中右键 -> 媒体 -> `NDIMediaSource`。
    *   在资产编辑器中，配置 `MediaConfiguration` 选择要连接的NDI源（需要先确保网络上有NDI源）。
    *   设置 `Bandwidth`、勾选 `bCaptureVideo` 和/或 `bCaptureAudio`。
    *   创建一个 `MediaPlayer` 资产，在蓝图中调用 `Open Source` 节点，传入此 `NDIMediaSource`。
    *   将 `MediaPlayer` 关联到 `MediaTexture`，再将其连接到材质或直接显示。

2.  **输出NDI视频**：
    *   在内容浏览器中右键 -> 媒体 -> `NDIMediaOutput`。
    *   配置 `SourceName`（输出流的名称）、`FrameRate` 等。
    *   在蓝图中，使用 `Media Capture` 节点，将其 `Media Output` 属性设置为创建的 `NDIMediaOutput` 资产。
    *   将需要捕获的视口（Viewport）或 `RenderTarget` 指定给捕获节点，即可开始输出。

## C++ 用法

### 头文件引入

```cpp
#include "NDIMediaSource.h"
#include "NDIMediaOutput.h"
#include "NDIMediaTimecodeProvider.h"

// 访问流接收器等内部类（通常在插件内部使用）
#include "Player/NDIStreamReceiver.h"
#include "NDISourceFinder.h"
```

### 基本用法

以下示例展示了如何以编程方式创建和使用NDI媒体源。

```cpp
// 来源: Public/NDIMediaSource.h
#include "NDIMediaSource.h"
#include "MediaPlayer.h"

// 1. 创建并配置媒体源
UNDIMediaSource* NDISource = NewObject<UNDIMediaSource>();
// 可以在此配置Source属性，或者直接使用默认值
// NDISource->MediaConfiguration.Device.DeviceName = TEXT("My NDI Source");
NDISource->Bandwidth = ENDIReceiverBandwidth::Highest;
NDISource->bCaptureVideo = true;
NDISource->bCaptureAudio = true;

// 2. 创建媒体播放器并打开源
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
MediaPlayer->OpenSource(NDISource);
```

### 进阶用法

直接使用 `FNDIStreamReceiver` 可以更精细地控制接收流程，例如手动获取帧数据或监听元数据。

```cpp
// 来源: Private/Player/NDIStreamReceiver.h, Public/NDIMediaDefines.h
#include "Player/NDIStreamReceiver.h"
#include "NDIMediaModule.h"

// 1. 通过模块获取接收器管理器并创建接收器
FNDIMediaModule* NDIModule = FNDIMediaModule::Get();
if (NDIModule)
{
    FNDIStreamReceiverManager& ReceiverManager = NDIModule->GetStreamReceiverManager();
    
    // 创建一个新的接收器
    TSharedPtr<FNDIStreamReceiver> Receiver = MakeShared<FNDIStreamReceiver>(NDIModule->GetNDIRuntimeLibrary());
    
    // 2. 配置源设置
    FNDISourceSettings SourceSettings;
    SourceSettings.SourceName = TEXT("My NDI Source");
    SourceSettings.Bandwidth = ENDIReceiverBandwidth::Highest;
    SourceSettings.bCaptureVideo = true;
    SourceSettings.bCaptureAudio = true;
    
    // 3. 初始化并启动连接
    if (Receiver->Initialize(SourceSettings, FNDIStreamReceiver::ECaptureMode::Manual))
    {
        Receiver->StartConnection();
        
        // 4. 绑定委托以接收数据
        Receiver->OnVideoFrameReceived.AddLambda([](FNDIStreamReceiver* InReceiver, const NDIlib_video_frame_v2_t& InFrame, const FTimespan& InTime)
        {
            UE_LOG(LogTemp, Log, TEXT("Received video frame: %dx%d"), InFrame.xres, InFrame.yres);
            // 在此处处理视频帧数据...
        });
        
        Receiver->OnMetaDataReceived.AddLambda([](FNDIStreamReceiver* InReceiver, const FString& InData, bool bAttachedToVideo)
        {
            UE_LOG(LogTemp, Log, TEXT("Received metadata: %s"), *InData);
        });
        
        // 5. 手动获取一帧（例如，在 Tick 或渲染线程回调中）
        // Receiver->FetchVideo(FTimespan::FromSeconds(GetGameTimeSinceCreation()));
        // Receiver->FetchAudio(FTimespan::FromSeconds(GetGameTimeSinceCreation()));
    }
}
```

另一个常见的进阶操作是发现局域网中的NDI源：

```cpp
// 来源: Private/NDISourceFinder.h
#include "NDISourceFinder.h"
#include "NDIMediaModule.h"

FNDIMediaModule* NDIModule = FNDIMediaModule::Get();
if (NDIModule)
{
    TSharedPtr<FNDISourceFinder> FindInstance = NDIModule->GetFindInstance();
    if (FindInstance)
    {
        TArray<FNDISourceFinder::FNDISourceInfo> Sources = FindInstance->GetSources();
        for (const auto& Source : Sources)
        {
            UE_LOG(LogTemp, Log, TEXT("Found NDI Source: Name=%s, URL=%s"), *Source.Name, *Source.Url);
        }
    }
}
```

## Demo 示例

以下是一个最小化的 Actor 类示例，演示如何从指定的NDI源接收视频帧，并记录其分辨率。

**NDIVideoReceiverActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Player/NDIStreamReceiver.h"
#include "NDIVideoReceiverActor.generated.h"

UCLASS()
class ANDIVideoReceiverActor : public AActor
{
    GENERATED_BODY()

public:
    ANDIVideoReceiverActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    void OnVideoFrameReceived(FNDIStreamReceiver* InReceiver, const NDIlib_video_frame_v2_t& InFrame, const FTimespan& InTime);

    TSharedPtr<FNDIStreamReceiver> VideoReceiver;
    FDelegateHandle VideoFrameHandle;
};
```

**NDIVideoReceiverActor.cpp**
```cpp
#include "NDIVideoReceiverActor.h"
#include "NDIMediaModule.h"
#include "NDISourceSettings.h"

ANDIVideoReceiverActor::ANDIVideoReceiverActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ANDIVideoReceiverActor::BeginPlay()
{
    Super::BeginPlay();

    FNDIMediaModule* NDIModule = FNDIMediaModule::Get();
    if (!NDIModule) return;

    // 创建接收器
    VideoReceiver = MakeShared<FNDIStreamReceiver>(NDIModule->GetNDIRuntimeLibrary());

    // 配置源（硬编码一个源名，请替换为你网络中实际的NDI源名称）
    FNDISourceSettings Settings;
    Settings.SourceName = TEXT("My Camera (NDI)");
    Settings.Bandwidth = ENDIReceiverBandwidth::Highest;
    Settings.bCaptureVideo = true;
    Settings.bCaptureAudio = false;

    if (VideoReceiver->Initialize(Settings, FNDIStreamReceiver::ECaptureMode::Manual))
    {
        // 绑定委托
        VideoFrameHandle = VideoReceiver->OnVideoFrameReceived.AddUObject(this, &ANDIVideoReceiverActor::OnVideoFrameReceived);

        // 启动连接
        VideoReceiver->StartConnection();
        UE_LOG(LogTemp, Log, TEXT("NDI Receiver Actor started, looking for source: %s"), *Settings.SourceName);
    }
}

void ANDIVideoReceiverActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (VideoReceiver.IsValid())
    {
        // 解除委托
        VideoReceiver->OnVideoFrameReceived.Remove(VideoFrameHandle);
        // 关闭连接
        VideoReceiver->Shutdown();
    }
    Super::EndPlay(EndPlayReason);
}

void ANDIVideoReceiverActor::OnVideoFrameReceived(FNDIStreamReceiver* InReceiver, const NDIlib_video_frame_v2_t& InFrame, const FTimespan& InTime)
{
    // 处理接收到的视频帧
    UE_LOG(LogTemp, Log, TEXT("NDI Frame Received - Resolution: %dx%d, FourCC: %d"), InFrame.xres, InFrame.yres, InFrame.FourCC);
    
    // 注意：此处仅做演示。在实际应用中，你需要将 InFrame.p_data 指向的像素数据
    // 转换并应用到纹理或其他渲染目标上。
    // 通常，使用 Media Framework 路径（通过 MediaPlayer）会自动处理这些转换。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 核心媒体IO框架，提供设备枚举、媒体捕获/输出基类、时间码提供程序基类等。NDIMedia 的设备发现和媒体捕获功能建立在此之上。 |
| `MediaUtils` | 媒体工具库，提供样本池、媒体纹理样本等基础组件。 |
| `MediaAssets` | 媒体资产模块，定义 `UMediaPlayer`, `UMediaTexture` 等资产类型。 |
| `RHI` | 渲染硬件接口，用于自定义纹理样本转换（如 UYVA， P216 格式的GPU解码）。 |
| `RenderCore` | 渲染核心，用于渲染线程的同步和GPU命令列表操作。 |
| `NDISDK` | 本插件内嵌的第三方NDI SDK头文件和库，通过动态加载（`FNDIMediaRuntimeLibrary`）与运行时NDI运行时交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `96b8b04b` | Media IO: Fix to recent CL 54396736 for ImgMedia and NDI players emitting incorrect SourceOpened ana | 修复了NDI播放器在特定情况下发送错误“源已打开”分析事件的问题。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为NDI播放器和捕获添加了额外的引擎分析信息，增强了遥测数据收集。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the ... | 调整了虚拟制片相关资产（包括NDI资产）的分类和目录结构，属于维护性重构。 |
| 2026-05-12 | `c657503b` | [Media] Add missing UAssetDefinition entries for concrete UMediaSource and UMediaOutput subclasses t | 为具体的UMediaSource和UMediaOutput子类（包括NDI的）添加了缺失的资产定义，改善编辑器体验。 |
| 2026-04-23 | `efcad028` | HDR: Fix HDR normalization factor across media causing incorrect brightness levels going from/to the | 修复了跨媒体（可能包括NDI）的HDR归一化因子，解决了亮度不正确的问题。 |

### 维护评价

*   **创建时间**：2024年3月，是一个相对年轻的插件。
*   **活跃度**：**活跃维护中**。从提交记录看，最近6个月内有多次实质性更新，包括功能增强（分析信息）、Bug修复（事件、HDR）和维护工作（资产重构）。这表明 Epic Games 的虚拟制片团队仍在积极开发和完善此插件。
*   **状态**：尽管 `.uplugin` 中标记为 `IsExperimentalVersion: true` 且默认禁用，但其持续的更新和明确的虚拟制片用途表明它是一个处于积极开发中的**实验性功能**，而非已废弃。用户需在项目设置中手动启用。
*   **推荐度**：**推荐用于NDI相关的虚拟制片或广播项目**。作为 Epic 官方维护的媒体框架扩展，其质量和未来支持有保障。但由于是实验性功能，在生产环境中使用前应进行充分测试，并关注后续版本的API变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/media-io-framework-in-unreal-engine/)（UE Media IO Framework 通用文档）
- [NDI 官方网站](https://ndi.video/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/NDIMedia/Source/NDIMedia/Tests)