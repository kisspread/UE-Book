# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

该插件为 Unreal Engine 提供了与 **Blackmagic Design** 专业视频采集卡的深度集成。它不仅仅是一个简单的视频播放器，而是作为 **媒体框架** 的一个后端，实现了基于 Blackmagic DeckLink SDK 的 **媒体输入（采集）** 和 **媒体输出** 功能。

**核心解决的问题：**
1.  **硬件抽象**：将 Blackmagic 特定的硬件 API 封装成 UE5 标准的 `IMediaPlayer`、`IMediaCapture` 和 `IMediaOutput` 接口，使其他引擎系统（如 `MediaFramework`、`nDisplay`、`LiveLink`）能够无缝使用 Blackmagic 硬件。
2.  **低延迟/高带宽**：支持通过 Blackmagic 硬件进行超低延迟的视频采集和输出，适用于虚拟制片、广播图形、实时合成等专业场景。
3.  **专业格式支持**：支持 Blackmagic 硬件特有的视频格式、色彩空间、时间码（Timecode）以及自定义时间步长（Custom Time Step）功能，确保与广播级设备精确同步。

**简而言之，这个插件让 UE5 项目能够将 Blackmagic 采集卡作为输入源（如摄像机、监视器信号）或输出目标（如监视器、流媒体编码器），是构建专业级视频制作管线的关键组件。**

## 使用场景

-   你正在使用 **虚拟制片**（Virtual Production）流程，需要将 LED 墙的渲染画面以超低延迟输出到 Blackmagic 设备，或从 Blackmagic 摄像机实时采集画面用于合成。
-   你需要为 **广播或实时图形** 项目（如体育赛事直播、新闻包装）在 UE5 中生成内容，并通过 Blackmagic 硬件输出到专业播出设备。
-   你在开发一个 **视频会议或监控系统**，需要从 Blackmagic 捕获卡采集多个视频源。
-   你需要一个支持硬件加速和专业时间码同步的 **媒体播放器**，用于高端演示或主题公园娱乐设施。

## 蓝图用法

插件主要通过其媒体工厂和具体的媒体资产类型暴露功能，核心蓝图节点通常围绕媒体源、播放和捕获操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init Media Event` | 初始化媒体事件提供者，开始监听来自 Blackmagic 设备的事件（如连接/断开）。 | `UMediaEventProvider` |
| `Get Media Event` | 获取当前待处理的媒体事件信息。 | `UMediaEventProvider` |
| `Get Media Event Name` | 获取媒体事件的文本名称。 | `UMediaEventProvider` |
| `Get Media Capture` | 从一个媒体输出对象获取对应的媒体捕获接口。 | `UBlackmagicMediaOutput` |
| `Get Supported Video Modes` | 查询当前连接的 Blackmagic 设备支持的所有视频模式（分辨率、帧率等）。 | `UBlackmagicMediaSource` |
| `Open Media` | 使用配置好的 `UBlackmagicMediaSource` 打开媒体，开始采集。 | `UBlackmagicMediaPlayer` |

### 使用示例（蓝图描述）

1.  **从 Blackmagic 摄像机采集画面**：
    *   创建一个 `UBlackmagicMediaSource` 资产，在详细面板中配置设备、端口和视频格式。
    *   创建一个 `UBlackmagicMediaPlayer` 或在 `Media Player` 资产中指定此媒体源。
    *   使用 `Media Texture` 渲染采集的画面，并将其应用到 `Media Plate` 或 `Material` 上。
    *   在蓝图中，可以调用 `Open Media` 来启动采集。

2.  **将画面输出到 Blackmagic 监视器**：
    *   创建一个 `UBlackmagicMediaOutput` 资产，配置目标设备和输出格式。
    *   在需要输出的画面（如场景捕获组件 `SceneCaptureComponent2D` 的渲染目标）上，创建一个 `Media Capture`。
    *   在蓝图中，将 `Media Capture` 的 `Media Output` 属性指向创建的 `UBlackmagicMediaOutput` 资产，然后开始捕获。

## C++ 用法

### 头文件引入

```cpp
// 核心媒体接口
#include "IMediaEventSink.h"
// Blackmagic 媒体源，用于创建和配置
#include "BlackmagicMediaSource.h"
// Blackmagic 媒体捕获（用于输出）
#include "BlackmagicMediaCapture.h"
// 或者使用更通用的媒体捕获接口
#include "MediaCapture.h"
```

### 基本用法

**从媒体源获取支持的视频模式 (来源：`BlackmagicMediaSource.h` 及相关测试逻辑)**
```cpp
// 假设已有一个配置好的 UBlackmagicMediaSource 指针 MediaSourcePtr
TArray<FMediaIOVideoMode> SupportedModes = MediaSourcePtr->GetSupportedVideoModes();

for (const FMediaIOVideoMode& Mode : SupportedModes)
{
    UE_LOG(LogTemp, Log, TEXT("Supported Mode: %dx%d @ %.2f Hz, Interlaced: %s"),
        Mode.Resolution.X, Mode.Resolution.Y,
        Mode.FrameRate.AsDecimal(),
        Mode.bIsInterlaced ? TEXT("Yes") : TEXT("No"));
}
```

**处理媒体事件 (基于 `MediaEventSink` 接口)**
```cpp
// 实现 IMediaEventSink 接口的类（例如，你的媒体播放器或管理器）
void FMyMediaPlayer::HandleMediaEvent(EMediaEvent EventType)
{
    switch (EventType)
    {
    case EMediaEvent::MediaOpened:
        UE_LOG(LogTemp, Log, TEXT("Blackmagic media opened successfully."));
        break;
    case EMediaEvent::MediaClosed:
        UE_LOG(LogTemp, Warning, TEXT("Blackmagic media connection closed."));
        break;
    case EMediaEvent::MediaError:
        UE_LOG(LogTemp, Error, TEXT("Blackmagic media error occurred."));
        break;
    default:
        break;
    }
}
```

### 进阶用法

**使用媒体捕获将场景渲染输出到 Blackmagic 设备 (结合 `MediaCapture` 和 `BlackmagicMediaOutput`)**
```cpp
// 1. 创建输出配置
UBlackmagicMediaOutput* MediaOutput = NewObject<UBlackmagicMediaOutput>();
MediaOutput->MediaConfiguration.MediaConnection.Device.DeviceName = TEXT("DeckLink Mini Monitor");
MediaOutput->MediaConfiguration.MediaConnection.Port.PortName = TEXT("Video");
// ... 设置分辨率、帧率等

// 2. 创建媒体捕获实例
UMediaCapture* MediaCapture = UMediaCapture::CreateMediaCapture();

// 3. 设置捕获目标为我们的 Blackmagic 输出
MediaCapture->SetMediaOutput(MediaOutput);

// 4. 准备捕获（可以捕获一个渲染目标、整个视口或一个 SceneCaptureComponent）
UTextureRenderTarget2D* RenderTarget = ...; // 获取你的渲染目标
bool bSuccess = MediaCapture->CaptureActiveRenderTarget();

// 5. 或者，捕获一个特定的 SceneCaptureComponent
// ASceneCapture2D* MyCaptureActor = ...;
// bool bSuccess = MediaCapture->CaptureScene(MyCaptureActor->GetCaptureComponent());

// 6. 在不需要时停止捕获
// MediaCapture->StopCapture();
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建 Blackmagic 媒体源并打开它。

**BlackmagicDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BlackmagicDemo.generated.h"

class UBlackmagicMediaPlayer;
class UBlackmagicMediaSource;

UCLASS()
class ABlackmagicDemo : public AActor
{
    GENERATED_BODY()

public:
    ABlackmagicDemo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(Transient)
    TObjectPtr<UBlackmagicMediaPlayer> MediaPlayer;

    UPROPERTY(Transient)
    TObjectPtr<UBlackmagicMediaSource> MediaSource;
};
```

**BlackmagicDemo.cpp**
```cpp
#include "BlackmagicDemo.h"
#include "BlackmagicMediaSource.h"
#include "BlackmagicMediaPlayer.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"

ABlackmagicDemo::ABlackmagicDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ABlackmagicDemo::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建媒体源
    MediaSource = NewObject<UBlackmagicMediaSource>(this, TEXT("BM_MediaSource"));
    // 在这里配置 MediaSource 的属性，例如：
    // MediaSource->MediaConnection.Device.DeviceName = TEXT("DeckLink Mini Recorder");
    // MediaSource->MediaConnection.Port.PortName = TEXT("Video");
    // MediaSource->VideoMode = ...; // 设置一个具体的视频模式

    // 2. 创建媒体播放器
    MediaPlayer = NewObject<UBlackmagicMediaPlayer>(this, TEXT("BM_MediaPlayer"));
    // 确保播放器有一个事件接收器，例如自身
    // MediaPlayer->SetEventSink(this);

    // 3. 打开媒体
    if (MediaPlayer->OpenUrl(MediaSource->GetUrl()))
    {
        UE_LOG(LogTemp, Log, TEXT("Attempted to open Blackmagic media source."));
        // 成功打开后，可以关联一个 MediaTexture 来显示画面
        // UMediaTexture* Texture = NewObject<UMediaTexture>();
        // Texture->SetMediaPlayer(MediaPlayer->GetMediaPlayer());
    }
}

void ABlackmagicDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

使用此插件，你的项目模块通常需要依赖以下插件模块：

| 模块 | 用途 |
|---|---|
| `BlackmagicMedia` | 核心运行时模块，提供 `UBlackmagicMediaSource`, `UBlackmagicMediaPlayer` 等类。 |
| `MediaIOCore` | 提供与媒体 I/O 框架相关的基础结构和接口。 |
| `BlackmagicSDK` (External) | Blackmagic Design 提供的底层 DeckLink SDK，用于直接硬件通信。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复自动检测功能错误地将隔行扫描信号识别为逐行信号的问题。 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 为Blackmagic和AJA卡在使用“自动”模式时填充媒体配置信息。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为各类媒体播放器和捕获产品添加了额外的引擎分析信息。 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复Bob去隔行处理器的场采样共享源帧时间戳的问题。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 将各种虚拟制片资产移动到了不同的资产分类，并进行了迁移。 |

### 维护评价

- **活跃维护**：从提交历史看，该插件**仍在积极维护和更新**。最近的提交集中在 2026 年 5 月，主要修复了与信号检测、媒体配置和去隔行相关的专业问题，并增加了分析功能。
- **稳定性**：作为 Epic 官方维护的媒体后端插件，其稳定性相对有保障，但使用门槛较高，依赖于 Blackmagic 硬件和驱动程序。
- **推荐程度**：如果你的项目 **必须** 使用 Blackmagic 的 DeckLink 系列采集卡进行专业视频输入/输出，那么此插件是**必备且推荐**的。它提供了官方支持、稳定且功能完善的集成方案。对于不需要 Blackmagic 硬件的项目，则无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/working-with-media-in-unreal-engine/) (Unreal Engine Media Framework 通用文档)