# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | 苹果媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet, Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia) | |

## 用途

AVF Media Player 是 Unreal Engine 的媒体播放器插件，底层基于 Apple 的 AV Foundation 框架。它在 iOS、macOS 和 tvOS 平台上提供高效的音频/视频解码与播放能力，支持本地文件、网络流媒体以及系统摄像头/麦克风采集（通过 `AvfMediaCapture` 模块）。该插件是 UE 媒体框架在 Apple 平台上的官方实现，负责将原生媒体样本转换为引擎内部的 `IMediaTextureSample` 和 `IMediaAudioSample`，并同步到渲染与音频管线。

## 使用场景

- 在 Apple 设备上播放游戏内过场动画、背景视频、UI 滚动视频
- 加载远程 HLS 或 HTTP 直播流媒体（取决于 AV Foundation 支持格式）
- 通过 `AvfMediaCapture` 使用设备的摄像头和麦克风进行实时视频/音频捕获
- 项目中需要跨平台媒体播放时，作为 Apple 平台的默认后端（引擎会自动选择）

## 蓝图用法

AVF Media Player 是一个底层插件，不直接暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有常用媒体操作通过标准 `MediaPlayer` 蓝图节点完成，例如：

- **打开媒体源** → `Open Source` 节点（指定媒体源资产）
- **播放/暂停** → `Play` / `Pause`
- **跳转** → `Seek`
- **获取状态** → `Is Playing` / `Get Duration` / `Get Time`

这些节点由引擎的 **Media Framework** 提供，底层自动调用本插件的实现。无需额外蓝图节点。

如需在蓝图中启用摄像头/麦克风捕获，使用 `MediaBundle` 或 `Media Capture` 相关节点，并选择 `AvfMediaCapture` 作为捕获源。

## C++ 用法

### 头文件引入

```cpp
#include "IAvfMediaModule.h"
#include "IMediaPlayer.h"
#include "IMediaEventSink.h"
```

### 基本用法

通过模块接口创建播放器，然后使用标准 `IMediaPlayer` 接口打开媒体资源：

```cpp
// 获取 AVF Media 模块
IAvfMediaModule* AvfMediaModule = FModuleManager::LoadModulePtr<IAvfMediaModule>("AvfMedia");
if (AvfMediaModule)
{
    // 创建事件接收器（来自媒体框架）
    IMediaEventSink* EventSink = ...;

    // 创建播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = AvfMediaModule->CreatePlayer(*EventSink);

    // 打开本地文件或 URL
    Player->Open(TEXT("/Game/Movies/MyVideo.mp4"), nullptr);

    // 开始播放
    Player->SetRate(1.0f);

    // 获取轨道信息
    IMediaTracks& Tracks = Player->GetTracks();
    int32 TrackCount = Tracks.GetNumTracks(EMediaTrackType::Video);
}
```

*来源：`IAvfMediaModule.h`，`FAvfMediaPlayer.h`*

### 进阶用法

结合 Media Framework 的 `FMediaPlayer` 对象使用（推荐方式）：

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"

// 创建引擎级媒体播放器
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaSource* MediaSource = ...; // 从资产加载或动态创建

// 打开媒体
MediaPlayer->OpenSource(MediaSource);

// 绑定到媒体纹理
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
MediaTexture->UpdateResource();

// 在游戏线程控制播放
MediaPlayer->Play();
```

这种方式会自动选择当前平台对应的 `IMediaPlayer` 实现（包括 AVF Media Player）。

**注意事项**：
- 所有播放器操作必须在游戏线程执行（`GameThread`）。
- 视频帧通过 `TickFetch` 在渲染线程更新，无需手动处理。
- 支持字幕（`FAvfMediaOverlaySample`），通过 `IMediaOverlaySample` 接口获取。

## Demo 示例

以下是一个最小 C++ 示例，创建 AVF 媒体播放器并循环播放本地视频（用于 macOS/iOS 平台）。

**DemoAvfMediaPlayer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "DemoAvfMediaPlayer.generated.h"

UCLASS()
class ADemoAvfMediaPlayer : public AActor
{
    GENERATED_BODY()

public:
    // 在 BeginPlay 中设置
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    FString MediaFilePath;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
};
```

**DemoAvfMediaPlayer.cpp**

```cpp
#include "DemoAvfMediaPlayer.h"
#include "FileMediaSource.h"

void ADemoAvfMediaPlayer::BeginPlay()
{
    Super::BeginPlay();

    if (!MediaPlayer)
    {
        MediaPlayer = NewObject<UMediaPlayer>(this);
    }
    if (!MediaTexture)
    {
        MediaTexture = NewObject<UMediaTexture>(this);
    }

    // 创建文件媒体源
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->FilePath = MediaFilePath;

    // 打开媒体（底层会使用 AVF Media Player）
    if (MediaPlayer->OpenSource(MediaSource))
    {
        // 绑定纹理到播放器
        MediaTexture->SetMediaPlayer(MediaPlayer);
        MediaTexture->UpdateResource();

        // 设置循环播放
        MediaPlayer->SetLooping(true);
        MediaPlayer->Play();
    }
}

void ADemoAvfMediaPlayer::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

本插件依赖以下 UE 模块（非标准框架依赖）：

| 模块 | 用途 |
|---|---|
| `Media` | 提供核心媒体接口 `IMediaPlayer`、`IMediaSamples` 等 |
| `MediaUtils` | 媒体框架工具类 |
| `RHI` | 渲染硬件接口，用于创建 GPU 纹理 |
| `AVFoundation` (系统框架) | Apple 原生媒体解码框架 |

**注意**：AV Foundation 是 Apple 平台专有系统库，插件仅在 iOS、macOS、tvOS 上可用。

## 维护状态

### 近期更新

- 2025-06-26 `d2ec2238` Generalized IOSAsyncTask to AppleAsyncTask
- 2025-06-02 `2c095ca4` Replace EBulkDataType in MetalRHI with Metal-specific RHI functions
- 2025-05-06 `5243d97b` Merging //UE5/Dev-ParallelRendering to Main
- 2025-04-23 `6ae57335` Used UnrealGame build target to convert all files to have dllstorage on methods/staticvar
- 2025-04-10 `ea97db60` Movie Render Queue: High-res tiling support for paging scene view state persistent data

### 维护评价

AVF Media Player 是一个较新（2025 年创建）且活跃维护的插件。近期更新涉及底层框架兼容性（MetalRHI、异步任务重构），没有出现废弃标记或重大功能缺失。建议在所有 iOS/macOS/tvOS 项目中使用该插件作为媒体播放后端。若有复杂媒体播放需求（如自定义捕获），可进一步利用 `AvfMediaCapture` 模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia)
- [官方文档 - Media Framework](https://docs.unrealengine.com/5.4/en-US/media-framework-for-unreal-engine/) (通用媒体框架文档)
- [测试用例]() （未提供独立测试文件，可参考引擎测试 `Engine/Source/Runtime/Core/Private/Tests/` 中与媒体相关的自动化测试）