# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra Player 是 UE5 的核心媒体播放后端，提供跨平台的视频/音频播放能力。它解决的核心问题是：**在不同平台上统一本地文件和网络流媒体的播放体验**。

该插件包含两个主要播放引擎：

- **ElectraPlayerRuntime** — 通用播放器，支持本地文件和互联网流媒体（HLS/DASH 等），是 Media Framework 的默认后端实现
- **ElectraProtron** — 专门针对桌面平台优化的本地 MP4 文件播放器，使用独立的解码管线和帧缓存策略，提供更高效的本地文件播放性能

从架构上看，插件采用了工厂模式（`ElectraPlayerFactory` / `ElectraProtronFactory`）分离播放器的创建逻辑，并通过 `ElectraPlayerPluginHandler` 统一调度不同后端。整个播放器实现了完整的 `IMediaPlayer`、`IMediaControls`、`IMediaTracks`、`IMediaSamples` 等 Media Framework 接口。

## 使用场景

- 你需要在游戏内播放过场动画视频 → 使用 Media Player + Media Texture
- 你需要从互联网流式播放视频内容（HLS/DASH） → 使用通用 Electra 后端
- 你在桌面平台上需要高性能播放本地 MP4 文件 → ElectraProtron 优化路径自动生效
- 你需要播放带有多音轨、多字幕轨的视频文件 → 通过 IMediaTracks 接口选择轨

## 蓝图用法

ElectraPlayer 是 Media Framework 的底层实现，不直接暴露蓝图节点。蓝图层面通过标准的 Media Framework 类进行操作：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开媒体源（URL/文件路径） | `UMediaPlayer` |
| `Play` | 开始播放 | `UMediaPlayer` |
| `Pause` | 暂停播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |
| `Set Rate` | 设置播放速率 | `UMediaPlayer` |
| `Close` | 关闭媒体 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1. 创建一个 `Media Player` 资产，在属性中确认 Media Player Class 使用 Electra
2. 创建 `Media Texture` 和 `Media Material`，将 Media Player 关联到 Media Texture
3. 在蓝图中：
   - 使用 `Open Source` 节点，传入文件路径或 URL
   - 使用 `Create Media Sound Component` 创建音频组件
   - 通过 `Event On Media Opened` / `Event On Playback Resumed` 等委托响应播放状态
4. 对于 UI 显示，将 Media Material 应用到 Image 控件上

## C++ 用法

### 头文件引入

```cpp
#include "IElectraProtronModule.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
```

### 基本用法

通过 Media Framework 标准接口使用，Electra 后端作为自动选择的播放器实现：

```cpp
// 创建 Media Player 实例（系统自动选择 Electra 作为后端）
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();

// 打开本地文件
FString FilePath = TEXT("file:///C:/Videos/MyMovie.mp4");
bool bOpened = MediaPlayer->OpenUrl(FilePath);

// 打开网络流
FString StreamUrl = TEXT("https://example.com/stream.m3u8");
bOpened = MediaPlayer->OpenUrl(StreamUrl);

// 控制播放
MediaPlayer->Play();
MediaPlayer->Pause();
MediaPlayer->Seek(FTimespan::FromSeconds(30.0));
MediaPlayer->SetRate(1.0f);
```

### 进阶用法

直接使用 ElectraProtron 模块接口创建播放器实例（适用于需要完全控制播放器生命周期的场景）：

```cpp
// 来源: Public/IElectraProtronModule.h
#include "IElectraProtronModule.h"

// 获取 ElectraProtron 模块
IElectraProtronModule& ProtronModule = FModuleManager::GetModuleChecked<IElectraProtronModule>("ElectraProtron");

// 通过事件接收器创建播放器
class FMyEventSink : public IMediaEventSink
{
public:
    virtual void ReceiveMediaEvent(EMediaEvent Event) override
    {
        switch (Event)
        {
        case EMediaEvent::MediaOpened:
            UE_LOG(LogTemp, Log, TEXT("媒体已打开"));
            break;
        case EMediaEvent::PlaybackEndReached:
            UE_LOG(LogTemp, Log, TEXT("播放结束"));
            break;
        case EMediaEvent::MediaClosed:
            UE_LOG(LogTemp, Log, TEXT("媒体已关闭"));
            break;
        }
    }
};

FMyEventSink EventSink;
TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> Player = ProtronModule.CreatePlayer(EventSink);

if (Player.IsValid())
{
    // 打开文件
    Player->Open(TEXT("file:///C:/Videos/local.mp4"), nullptr);
    
    // 获取媒体信息
    FString Info = Player->GetInfo();
    
    // 通过 Controls 接口控制播放
    IMediaControls& Controls = Player->GetControls();
    Controls.SetRate(1.0f);
    Controls.SetLooping(true);
    
    // 通过 Tracks 接口查询轨道信息
    IMediaTracks& Tracks = Player->GetTracks();
    int32 NumVideoTracks = Tracks.GetNumTracks(EMediaTrackType::Video);
    int32 NumAudioTracks = Tracks.GetNumTracks(EMediaTrackType::Audio);
    
    // 查询视频格式
    FMediaVideoTrackFormat VideoFormat;
    if (Tracks.GetVideoTrackFormat(0, 0, VideoFormat))
    {
        UE_LOG(LogTemp, Log, TEXT("视频: %dx%d @ %d kbps"),
            VideoFormat.Width, VideoFormat.Height, VideoFormat.BitRate);
    }
    
    // 获取时长
    IMediaControls& C = Player->GetControls();
    FTimespan Duration = C.GetDuration();
    
    // 查询缓存状态
    IMediaCache& Cache = Player->GetCache();
    TRangeSet<FTimespan> BufferedRanges;
    Cache.QueryCacheState(EMediaCacheState::Loaded, BufferedRanges);
}
```

## Demo 示例

一个完整的最小示例，展示如何在 Actor 中使用 Electra Player 播放视频：

### MyVideoPlayerActor.h

```cpp
// MyVideoPlayerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"
#include "MyVideoPlayerActor.generated.h"

UCLASS()
class AMyVideoPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVideoPlayerActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(EditAnywhere, Category = "Media")
    UMediaTexture* MediaTexture;

    UPROPERTY(EditAnywhere, Category = "Media")
    FString VideoUrl;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayVideo();

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopVideo();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);

    UFUNCTION()
    void OnMediaOpenFailed(FString FailedUrl);

private:
    UPROPERTY()
    UMediaSoundComponent* SoundComponent;
};
```

### MyVideoPlayerActor.cpp

```cpp
// MyVideoPlayerActor.cpp
#include "MyVideoPlayerActor.h"
#include "MediaSoundComponent.h"

AMyVideoPlayerActor::AMyVideoPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建音频组件
    SoundComponent = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("MediaSound"));
    RootComponent = SoundComponent;
}

void AMyVideoPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && SoundComponent)
    {
        // 将 MediaPlayer 关联到音频组件
        SoundComponent->SetMediaPlayer(MediaPlayer);

        // 绑定回调
        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyVideoPlayerActor::OnMediaOpened);
        MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyVideoPlayerActor::OnMediaOpenFailed);
    }
}

void AMyVideoPlayerActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyVideoPlayerActor::PlayVideo()
{
    if (MediaPlayer && !VideoUrl.IsEmpty())
    {
        MediaPlayer->OpenUrl(VideoUrl);
    }
}

void AMyVideoPlayerActor::StopVideo()
{
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }
}

void AMyVideoPlayerActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("视频已打开: %s"), *OpenedUrl);

    // 自动开始播放
    if (MediaPlayer)
    {
        MediaPlayer->Play();
    }
}

void AMyVideoPlayerActor::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogWarning, Log, TEXT("视频打开失败: %s"), *FailedUrl);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ElectraBase` | Electra 系列插件的公共基础库 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（ElectraProtron 的 GPU 加速解码支持） |
| `DirectX` | DirectX 底层 API 访问 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Protron 播放完一个视频后无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流媒体专辑元数据解析问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置项控制播放期间解码器是否需要暂停 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将断言改为条件判断以处理 .ts 内部时间戳异常情况 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 预加载字幕时检查序列索引以减少不必要的加载 |

### 维护评价

- **创建时间**：2021 年 1 月，从 Epic 内部（NFL 项目）迁移至公开版本
- **活跃度**：非常活跃，2026 年 5 月仍有密集的 bug 修复和功能增强
- **维护等级**：**积极维护** — 作为 UE5 Media Framework 的核心后端，由 Epic 官方团队持续维护
- **代码质量**：采用 PImpl 模式封装实现细节，多线程架构设计合理，有完整的线程安全保护
- **推荐度**：✅ **强烈推荐** — 这是 UE5 的默认媒体播放后端，所有使用 Media Framework 的项目都会间接依赖此插件。无需手动启用，系统默认集成。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)