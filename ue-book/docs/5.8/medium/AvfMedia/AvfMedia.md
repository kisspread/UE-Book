# AVF Media Player

> Implements a media player using Apple AV Foundation.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | AV媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-09-16 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia) | |

## 用途

AvfMedia 插件为 Unreal Engine 的媒体框架（Media Framework）提供了一个基于苹果 **AV Foundation** 框架的底层媒体播放器实现。它并非一个独立的、直接供用户使用的媒体播放器应用，而是作为媒体框架的一个 **媒体播放器插件**，专门用于在 Apple 平台（iOS、macOS、tvOS）上播放音频和视频文件。当开发者在这些平台上使用 `MediaPlayer` 资产并选择 AVF 作为媒体源时，引擎会调用此插件来执行实际的解码、同步和渲染工作。它解决了在 Apple 生态系统中利用原生、高效、兼容性好的 AV Foundation API 来处理媒体内容的问题。

## 使用场景

- 你的游戏或应用需要部署到 **iOS、macOS 或 tvOS** 平台。
- 你需要在这些平台上播放本地或网络的 **视频、音频** 文件。
- 你希望利用苹果原生的、经过高度优化的媒体播放能力，以获得最佳的性能和兼容性。
- 你正在使用 UE 的 **Media Framework**，并需要一个在 Apple 设备上稳定运行的媒体播放器后端。

## 蓝图用法

AvfMedia 插件本身主要作为底层实现，其公开的蓝图接口非常有限。开发者通常不直接调用该插件的蓝图节点，而是通过 UE 标准的 **Media Player** 蓝图节点来使用。插件在幕后负责提供具体的播放功能。

### 核心节点

该插件未暴露任何特定的 `BlueprintCallable` 节点供蓝图直接调用。所有媒体操作均通过 `MediaPlayer` 资产和 `MediaSoundComponent`、`MediaTexture` 等标准引擎组件完成。

### 使用示例（蓝图描述）

1.  **创建媒体资产**：
    *   在内容浏览器中右键创建 `MediaPlayer` 资产和 `MediaSoundComponent`。
2.  **配置播放器**：
    *   打开 `MediaPlayer` 资产，在“媒体源”部分选择 **“文件”** 或 **“URL”**。
    *   输入本地视频文件路径（如 `/Game/Movies/MyVideo.mp4`）或网络 URL。
    *   在“播放器选项”中，**“媒体播放器工厂”** 会自动或手动选择支持 AV Foundation 的选项（通常由插件注册）。
3.  **在场景中播放**：
    *   将 `MediaSoundComponent` 添加到 Actor。
    *   在蓝图中，使用 **“Open Source”** 或 **“Open URL”** 节点打开 `MediaPlayer`，然后调用 **“Play”** 节点即可开始播放。插件会负责处理底层的 AV Foundation 调用。

## C++ 用法

开发者通常通过 UE 的 `IMediaPlayer` 接口和 `FMediaModule` 来与 AvfMedia 插件交互，而不是直接实例化其内部类。以下是典型的 C++ 用法模式。

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaSoundComponent.h"
```

### 基本用法

通过 `FMediaModule` 获取特定的媒体播放器实例。通常，你不会直接调用 `IAvfMediaModule::CreatePlayer`，而是使用媒体模块的标准流程。

```cpp
// 假设你已经有一个 UMediaPlayer* MediaPlayer 和 UMediaSource* MediaSource

// 1. 打开媒体源
FString ErrorReason;
bool bSuccess = MediaPlayer->OpenSource(MediaSource, ErrorReason);
if (bSuccess)
{
    // 2. 播放媒体
    MediaPlayer->Play();
}

// 3. 在 Tick 或需要的地方查询状态
if (MediaPlayer->IsReady() && MediaPlayer->IsPlaying())
{
    FTimespan CurrentTime = MediaPlayer->GetTime();
    FTimespan Duration = MediaPlayer->GetDuration();
    // ... 使用时间信息
}
```

**来源**：此用法基于 UE Media Framework 的标准流程，具体实现由 AvfMedia 插件的 `FAvfMediaPlayer` 类完成。

### 进阶用法

访问媒体轨道和样本。这通常用于更精细的控制或分析，例如获取视频帧纹理或音频波形。

```cpp
// 假设 MediaPlayer 已成功打开并播放
IMediaPlayer& PlayerInterface = MediaPlayer->GetPlayer(); // 获取底层播放器接口
IMediaTracks& Tracks = PlayerInterface.GetTracks();

// 查询视频轨道信息
int32 NumVideoTracks = Tracks.GetNumTracks(EMediaTrackType::Video);
if (NumVideoTracks > 0)
{
    FMediaVideoTrackFormat VideoFormat;
    Tracks.GetVideoTrackFormat(0, 0, VideoFormat);
    UE_LOG(LogTemp, Log, TEXT("Video Resolution: %dx%d"), VideoFormat.Width, VideoFormat.Height);
}

// 获取样本（此操作更底层，通常用于自定义渲染或分析）
IMediaSamples& Samples = PlayerInterface.GetSamples();
TSharedPtr<IMediaTextureSample, ESPMode::ThreadSafe> TextureSample;
if (Samples.FetchVideo(TextureSample))
{
    // TextureSample 包含了视频帧数据，可用于自定义纹理上传等
    // FAvfMediaTextureSample* AvfSample = static_cast<FAvfMediaTextureSample*>(TextureSample.Get());
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何在 Apple 平台上使用媒体框架播放视频文件。假设你已有一个播放器 Actor 类。

### MediaPlaybackActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaSoundComponent.h"
#include "MediaPlaybackActor.generated.h"

UCLASS()
class YOURPROJECT_API AMediaPlaybackActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMediaPlaybackActor();

protected:
    virtual void BeginPlay() override;

public:
    // 要播放的媒体资产
    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaSource* MediaSource;

    // 用于播放声音
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaSoundComponent* MediaSoundComp;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StartPlayback();
};
```

### MediaPlaybackActor.cpp

```cpp
#include "MediaPlaybackActor.h"

AMediaPlaybackActor::AMediaPlaybackActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaSoundComp = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("MediaSound"));
    RootComponent = MediaSoundComp;
}

void AMediaPlaybackActor::BeginPlay()
{
    Super::BeginPlay();
    // 可以在 BeginPlay 中自动播放
    if (MediaPlayer && MediaSource)
    {
        StartPlayback();
    }
}

void AMediaPlaybackActor::StartPlayback()
{
    if (MediaPlayer && MediaSource)
    {
        // 使用媒体播放器打开源并播放
        FString ErrorReason;
        bool bOpened = MediaPlayer->OpenSource(MediaSource, ErrorReason);
        if (bOpened)
        {
            MediaPlayer->Play();
            UE_LOG(LogTemp, Log, TEXT("Started media playback."));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to open media source: %s"), *ErrorReason);
        }
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 文件分析，使用者（特别是当你需要深入扩展或调试此插件时）可能需要依赖以下特定模块。常见的 Core, Engine 等依赖已省略。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 提供媒体框架的通用工具和接口，如 `IMediaPlayer`。 |
| `MediaAssets` | 提供 `UMediaPlayer`、`UMediaSource` 等蓝图资产类。 |
| `Media` | 媒体框架的核心运行时模块。 |
| `AudioMixer` | 用于处理通过媒体框架获取的音频采样并输出到音频系统。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1951db93` | [AvfMedia] Default H.264 file playback to BGRA decode and provide CPU accessible buffer for media fi | H.264 文件播放默认使用 BGRA 解码，并为媒体文件提供 CPU 可访问的缓冲区。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复或抑制不可达代码警告。 |
| 2026-04-01 | `39223292` | [AvfMedia] Provide CPU buffer alongside GPU texture when using FAvfMediaCapturePlayer | 在使用 FAvfMediaCapturePlayer 时，在 GPU 纹理旁同时提供 CPU 缓冲区。 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了 printf 输出。 |

### 维护评价

AvfMedia 插件自 **2014 年**创建，历史非常悠久，是一个成熟的底层平台组件。从 git 历史看，**直至 2026 年 5 月仍有更新**，主要集中在性能优化（如 BGRA 解码）、兼容性修复和内部日志改进上。这表明该插件仍在 **积极维护** 中，以适应新的 UE 版本和 Apple 平台变化。

**优点**：作为 Epic 官方维护的核心媒体插件之一，它在 Apple 平台上的稳定性和兼容性通常有保障，是官方推荐的解决方案。
**注意事项**：该插件主要服务于 Media Framework，不直接暴露高级 API。其内部实现与 Apple 平台紧密耦合，对跨平台开发无用。对于绝大多数开发者而言，只需将其视为 Media Framework 的透明后端即可。

**推荐使用**：如果你的目标平台包含 iOS、macOS 或 tvOS，且需要播放媒体，那么这是**必备且推荐**的插件，无需额外开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (较旧的 Media Framework 讨论帖，仍具参考价值)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AvfMedia/Tests) (位于插件目录下的测试代码)