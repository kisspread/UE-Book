# Electra Player

> Cross platform media player for local files and internet streaming.
> Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 电子播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

**Electra Player** 是 UE 内置的跨平台媒体播放器插件。它提供了两大核心能力：
1.  **通用媒体播放器**：能够解码和播放多种媒体格式（包括本地文件和互联网流媒体），是 UE 媒体框架的重要底层实现之一。
2.  **Protron 优化播放器**：一个专为桌面平台优化的、高性能的 **仅限本地 MP4 文件** 的播放器。从源码结构看，`ElectraProtron` 模块实现了基于 `IMediaPlayer` 接口的专用播放器，通过 `FProtronVideoCache` 等机制管理视频帧缓存，旨在提供流畅、低延迟的本地 MP4 回放体验。

简而言之，这个插件解决了在 Unreal Engine 项目中集成和播放视频内容的需求，无论是用于过场动画、游戏内电视屏幕、背景视频还是网络视频流。`Protron` 子系统则是为追求极致本地 MP4 播放性能（如赛车游戏中的回放）而提供的专用方案。

## 使用场景

-   你需要在游戏中播放一段过场动画（CG）→ 使用通用播放器 `ElectraPlayerRuntime`。
-   你需要游戏内的角色观看“电视”直播（如模拟新闻播报）→ 使用通用播放器接入网络流。
-   你在开发一个赛车游戏，需要高性能回放比赛录像（本地 MP4 文件）→ 使用 `ElectraProtron` 优化播放器。
-   你需要一个不依赖特定平台解码器的、可靠的跨平台媒体播放方案。

## 蓝图用法

`ElectraPlayer` 本身是一个底层媒体播放器插件，其上层交互通常通过 UE 的 **媒体框架（Media Framework）** 进行。在蓝图中，你会使用 `Media Player` 资产，并通过 `Open Source`、`Play`、`Pause` 等节点来控制播放。`ElectraPlayer` 和 `ElectraProtron` 作为其背后的播放器实现，对蓝图用户大部分时间是透明的。

核心的创建接口 `IElectraProtronModule::CreatePlayer` 被媒体框架内部调用。在蓝图层面，你通常会看到类似如下的节点连接：

1.  **创建媒体播放器**：蓝图中拖入 `Media Player` 对象。
2.  **打开媒体源**：使用 `Open File` 或 `Open URL` 节点，并提供媒体文件路径或 URL。
3.  **控制播放**：连接 `Play`、`Pause`、`Seek` 等节点到相应的事件（如按钮点击）。
4.  **获取播放状态/信息**：使用 `Is Playing`、`Get Duration` 等节点。

## C++ 用法

### 头文件引入

```cpp
#include "IElectraProtronModule.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
```

### 基本用法

通过模块接口创建 `Protron` 播放器实例。
（来源：`Public/IElectraProtronModule.h`）

```cpp
// 获取 Protron 模块
IElectraProtronModule* ProtronModule = FModuleManager::GetModulePtr<IElectraProtronModule>(TEXT("ElectraProtron"));
if (ProtronModule)
{
    // 创建一个媒体事件接收器（通常由你的播放器组件或UI提供）
    IMediaEventSink& MyEventSink = ...; // 需要实现此接口或获取一个实例

    // 创建 Protron 播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer = ProtronModule->CreatePlayer(MyEventSink);

    if (MediaPlayer.IsValid())
    {
        // 打开一个本地 MP4 文件
        const FString MoviePath = FPaths::ProjectContentDir() / TEXT("Movies/MyVideo.mp4");
        bool bOpened = MediaPlayer->Open(MoviePath, nullptr);

        if (bOpened)
        {
            // 开始播放
            MediaPlayer->GetControls().Play();

            // 在 Tick 中调用以更新播放状态
            // MediaPlayer->TickFetch(DeltaTime, Timecode);
            // MediaPlayer->TickInput(DeltaTime, Timecode);
        }
    }
}
```

### 进阶用法

使用 `IMediaPlayer` 接口查询详细的媒体信息和控制播放范围。
（来源：`Private/Player/ElectraProtronPlayer.h`, `Private/Player/ElectraProtronPlayerImpl.h`）

```cpp
// 假设我们已经通过媒体框架或直接创建的方式获得了一个指向 Electra/Protron 播放器的指针
TSharedPtr<IMediaPlayer> MediaPlayer = ...;

// 查询视频轨道信息
int32 NumVideoTracks = MediaPlayer->GetTracks().GetNumTracks(EMediaTrackType::Video);
if (NumVideoTracks > 0)
{
    FMediaVideoTrackFormat VideoFormat;
    MediaPlayer->GetTracks().GetVideoTrackFormat(0, 0, VideoFormat);
    UE_LOG(LogTemp, Log, TEXT("Video Resolution: %d x %d"), VideoFormat.Width, VideoFormat.Height);
}

// 设置循环播放
MediaPlayer->GetControls().SetLooping(true);

// 跳转到特定时间点
FTimespan SeekTime = FTimespan::FromSeconds(30.0);
MediaPlayer->GetControls().Seek(SeekTime);

// 获取媒体总时长
FTimespan Duration = MediaPlayer->GetControls().GetDuration();
UE_LOG(LogTemp, Log, TEXT("Media Duration: %s"), *Duration.ToString());

// 查询视频缓存状态 (IMediaCache接口)
TRangeSet<FTimespan> CachedTimeRanges;
MediaPlayer->GetCache().QueryCacheState(EMediaCacheState::Loaded, CachedTimeRanges);
// 分析 CachedTimeRanges 可知已缓存的时间段
```

## Demo 示例

一个展示如何使用 `ElectraProtron` 模块播放本地 MP4 文件的最小 C++ 示例。

**MyMediaPlayerComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MediaPlayer.h"
#include "MyMediaPlayerComponent.generated.h"

UCLASS(ClassGroup=(Media), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMediaPlayerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayLocalMP4(const FString& FilePath);

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopPlayback();

private:
    TSharedPtr<IMediaPlayer> MediaPlayerInstance;
};
```

**MyMediaPlayerComponent.cpp**
```cpp
#include "MyMediaPlayerComponent.h"
#include "IElectraProtronModule.h"

void UMyMediaPlayerComponent::BeginPlay()
{
    Super::BeginPlay();
}

void UMyMediaPlayerComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopPlayback();
    Super::EndPlay(EndPlayReason);
}

void UMyMediaPlayerComponent::PlayLocalMP4(const FString& FilePath)
{
    // 停止之前的播放
    StopPlayback();

    // 尝试使用 Protron 模块（专门优化本地 MP4）
    IElectraProtronModule* ProtronModule = FModuleManager::GetModulePtr<IElectraProtronModule>(TEXT("ElectraProtron"));
    if (ProtronModule)
    {
        // 注意：这里需要一个真实的 IMediaEventSink 实现。
        // 在实际项目中，通常由 UMediaPlayer 或相关组件提供。
        // 这里为示例简化，假设我们有一个静态或成员 EventSink。
        // 实际开发中，你可能需要继承自 IMediaEventSink 并传递 `this` 或另一个合适的对象。
        // 由于 IMediaEventSink 是纯虚接口，此处无法直接实例化，需读者根据项目结构适配。
        // IMediaEventSink& EventSink = ...; // 需要您提供具体实现

        // MediaPlayerInstance = ProtronModule->CreatePlayer(EventSink);
        // if (MediaPlayerInstance.IsValid())
        // {
        //     if (MediaPlayerInstance->Open(FilePath, nullptr))
        //     {
        //         MediaPlayerInstance->GetControls().Play();
        //         UE_LOG(LogTemp, Log, TEXT("Started playing: %s"), *FilePath);
        //     }
        // }
    }
}

void UMyMediaPlayerComponent::StopPlayback()
{
    if (MediaPlayerInstance.IsValid())
    {
        MediaPlayerInstance->Close();
        MediaPlayerInstance.Reset();
        UE_LOG(LogTemp, Log, TEXT("Stopped media playback."));
    }
}
```

## 模块依赖

`ElectraPlayer` 插件由多个模块组成，各模块依赖关系如下。**使用者（你的项目）通常只需依赖上层媒体框架，无需直接依赖这些内部模块。** 以下是插件内部的依赖：

| 模块 | 用途 |
|---|---|
| `ElectraPlayerFactory` | 播放器工厂，负责创建通用的 Electra 播放器实例。依赖 `ElectraBase`。 |
| `ElectraPlayerPlugin` | 通用播放器插件注册。依赖 `Engine`。 |
| `ElectraPlayerPluginHandler` | 插件处理器，管理播放器插件的生命周期。依赖 `ElectraPlayerRuntime` 和 `ElectraPlayerPlugin`。 |
| `ElectraPlayerRuntime` | 通用 Electra 播放器的核心运行时逻辑。依赖 `Engine` 和 `DirectX`。 |
| `ElectraProtron` | Protron 优化播放器的核心实现，包含视频缓存和播放控制逻辑。依赖 `D3D12RHI`。 |
| `ElectraProtronFactory` | Protron 播放器工厂，负责创建 Protron 播放器实例。依赖 `ElectraBase`。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 Protron 播放器播放完一个视频后无法播放新视频的问题。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流媒体播放时元数据（如专辑信息）的处理问题。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 增加了配置选项和控制台变量，用于控制播放期间解码器是否需要暂停。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将一处断言改为 if 条件判断，以更好地处理 .ts 文件内部时间戳异常的情况。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预取字幕媒体片段时增加序列索引检查，以减少不必要的加载操作。 |

### 维护评价

**积极维护中**。
-   **创建时间**：约4年前（2021年），是一个相对成熟的插件。
-   **近期活跃度**：从最近的提交历史（2026年5月）来看，插件仍在**积极维护**。最近的更新集中在**bug修复**（如Protron播放新视频问题、流媒体元数据、时间戳处理）和**功能增强**（添加解码器暂停控制选项），表明Epic团队持续在改进其稳定性和功能。
-   **推荐使用**：**是**。作为UE官方的媒体播放解决方案之一，其稳定性和跨平台能力有保障。`Protron`模块为特定高性能本地播放场景提供了优化选择。建议在需要稳定、跨平台媒体播放功能的项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)