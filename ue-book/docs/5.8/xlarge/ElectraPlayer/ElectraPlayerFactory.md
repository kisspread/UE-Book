# Electra Player

> Cross platform media player for local files and internet streaming. Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

Electra Player 是 UE5 中的一个核心媒体播放插件，旨在提供一个跨平台、高性能的媒体播放解决方案。它的核心价值在于：

1.  **统一播放框架**：提供一套标准化的接口来播放本地文件（如 MP4、WebM）和各种互联网流媒体协议（如 HLS、DASH）。
2.  **平台优化**：针对不同平台（Windows, Android, iOS, 主机等）提供了优化的解码和渲染后端。
3.  **高级功能**：除了基础播放，它还支持 DRM 保护内容、字幕、元数据、缓冲和自适应比特率切换等高级流媒体特性。
4.  **高性能本地播放 (Protron)**：提供一个名为“Protron”的专用路径，在桌面平台（主要依赖 DirectX 12）上对本地 MP4 文件进行更优化的解码和渲染，以实现更低的延迟和更高的性能。

简单来说，它解决了“如何在 Unreal Engine 的各种平台上稳定、高效地播放各种格式和来源的视频/音频内容”这一核心问题。

## 使用场景

-   你在制作一个需要播放过场动画、背景视频或用户生成视频的应用程序（游戏、虚拟制片、架构可视化）。
-   你的应用需要从互联网上拉取和播放实时视频流，例如观看直播或点播视频。
-   你正在开发一个需要 DRM 保护的付费视频内容播放功能。
-   你需要为视频添加多语言字幕或显示专辑封面等元数据。
-   你在开发一个面向 PC 的应用，希望以最高性能和最低延迟播放本地 MP4 文件（使用 Protron 路径）。

## 蓝图用法

媒体播放功能通常通过 `UMediaPlayer` 资产和 `UMediaComponent` 组件来实现。Electra Player 作为底层引擎，其接口被这些上层组件封装。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 使用 `FMediaSource`（如 `UFileMediaSource`， `UStreamMediaSource`）打开媒体。 | `UMediaPlayer` |
| `Open URL` | 使用字符串 URL 打开本地文件或网络流。 | `UMediaPlayer` |
| `Play` / `Pause` / `Stop` | 控制媒体播放状态。 | `UMediaPlayer` |
| `Seek` | 跳转到媒体的指定时间点。 | `UMediaPlayer` |
| `Set Looping` | 设置是否循环播放。 | `UMediaPlayer` |
| `On Media Opened` / `On Media Closed` / `On Playback Resumed` 等 | 各种播放状态变化的事件委托。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  **播放本地文件**：
    *   在场景中添加一个 `Media Component`。
    *   在 `Media Component` 的细节面板中，创建一个新的 `Media Player` 资产。
    *   创建或指定一个 `File Media Source` 资产，并设置其 `File` 路径（例如 `/Game/Movies/MyVideo.mp4`）。
    *   在事件图表中，调用 `Media Player` 的 `Open Source` 节点，并传入 `File Media Source`。
    *   监听 `On Media Opened` 事件，在成功后调用 `Play` 开始播放。

2.  **播放网络流**：
    *   流程与播放本地文件类似，但使用 `UStreamMediaSource` 资产。
    *   在 `Stream Media Source` 中设置流媒体的 URL（例如 `http://example.com/live/stream.m3u8`）。
    *   同样通过 `Open Source` 打开并播放。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "FileMediaSource.h"
#include "StreamMediaSource.h"
#include "MediaTexture.h" // 若需渲染到纹理
```

### 基本用法

以下示例演示了如何在 C++ 中动态创建 `UMediaPlayer` 并播放一个本地文件。
(思路源自引擎内部媒体框架的标准用法模式)

```cpp
// MyMediaActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMediaActor.generated.h"

class UMediaPlayer;
class UMediaTexture;
class UFileMediaSource;

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    FString VideoFilePath; // 例如: "/Game/Movies/TestVideo.mp4"

    virtual void BeginPlay() override;

    // 处理媒体打开成功的回调
    UFUNCTION()
    void HandleMediaOpened(FString OpenedUrl);

    // 处理媒体打开失败的回调
    UFUNCTION()
    void HandleMediaOpenFailed(FString FailedUrl);

private:
    UPROPERTY(Transient)
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY(Transient)
    TObjectPtr<UMediaTexture> MediaTexture; // 可选，用于渲染到纹理

    UPROPERTY(Transient)
    TObjectPtr<UFileMediaSource> FileSource;

    void InitializeMediaPlayer();
};
```

```cpp
// MyMediaActor.cpp
#include "MyMediaActor.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "FileMediaSource.h"
#include "UObject/ConstructorHelpers.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 可选：在构造函数中创建 Media Texture 组件
    // MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();
    InitializeMediaPlayer();
}

void AMyMediaActor::InitializeMediaPlayer()
{
    // 1. 创建 Media Player 实例
    MediaPlayer = NewObject<UMediaPlayer>(this, UMediaPlayer::StaticClass(), TEXT("MyMediaPlayer"));
    if (!MediaPlayer)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MediaPlayer"));
        return;
    }

    // 2. 创建 Media Source
    FileSource = NewObject<UFileMediaSource>(this, UFileMediaSource::StaticClass(), TEXT("MyFileSource"));
    FileSource->SetFilePath(VideoFilePath);

    // 3. 绑定回调（可选）
    MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyMediaActor::HandleMediaOpened);
    MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyMediaActor::HandleMediaOpenFailed);

    // 4. 打开媒体源
    if (!MediaPlayer->OpenSource(FileSource))
    {
        UE_LOG(LogTemp, Warning, TEXT("MediaPlayer failed to open source: %s"), *VideoFilePath);
    }
}

void AMyMediaActor::HandleMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("Media opened successfully: %s"), *OpenedUrl);
    // 媒体打开成功，开始播放
    if (MediaPlayer)
    {
        MediaPlayer->Play();
    }

    // 可选：将 Media Texture 绑定到 Media Player，以便在材质中使用
    if (MediaTexture && MediaPlayer)
    {
        MediaTexture->SetMediaPlayer(MediaPlayer);
    }
}

void AMyMediaActor::HandleMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to open media: %s"), *FailedUrl);
}
```

### 进阶用法

使用流媒体源并处理缓冲事件：
(根据流媒体处理的标准实践推断)

```cpp
// 假设已经有一个 UMediaPlayer* MediaPlayer
void AMyMediaActor::OpenLiveStream(const FString& StreamUrl)
{
    UStreamMediaSource* StreamSource = NewObject<UStreamMediaSource>();
    StreamSource->SetStreamUrl(StreamUrl);

    // 绑定更多事件以监控流媒体状态
    MediaPlayer->OnMediaClosed.AddDynamic(this, &AMyMediaActor::HandleMediaClosed);
    MediaPlayer->OnPlaybackSuspended.AddDynamic(this, &AMyMediaActor::HandlePlaybackSuspended);
    // ... 其他事件如 OnBuffering

    MediaPlayer->OpenSource(StreamSource);
}

void AMyMediaActor::HandleMediaClosed()
{
    // 流媒体关闭或结束
}

void AMyMediaActor::HandlePlaybackSuspended()
{
    // 播放暂停（可能是缓冲）
    UE_LOG(LogTemp, Warning, TEXT("Playback suspended, likely buffering..."));
    // 这里可以更新UI显示缓冲图标
}
```

## Demo 示例

以下是一个完整的、可编译的最小 Actor 示例，用于在关卡中播放一个指定的本地视频文件。

```cpp
// SimpleVideoPlayerActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SimpleVideoPlayerActor.generated.h"

class UMediaPlayer;
class UMediaSoundComponent;
class UFileMediaSource;

UCLASS()
class ASimpleVideoPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    ASimpleVideoPlayerActor();

    // 要播放的视频文件路径，例如 "/Game/Movies/MyVideo.mp4"
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Video")
    FString VideoPath;

    // 是否自动播放
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Video")
    bool bAutoPlay = true;

    // 是否循环播放
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Video")
    bool bLoop = false;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category = "Components")
    TObjectPtr<UMediaSoundComponent> SoundComponent;

    UPROPERTY(Transient)
    TObjectPtr<UMediaPlayer> MediaPlayer;

    UPROPERTY(Transient)
    TObjectPtr<UFileMediaSource> MediaSource;

    void SetupAndPlay();
};
```

```cpp
// SimpleVideoPlayerActor.cpp
#include "SimpleVideoPlayerActor.h"
#include "MediaPlayer.h"
#include "MediaSoundComponent.h"
#include "FileMediaSource.h"

ASimpleVideoPlayerActor::ASimpleVideoPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建媒体声音组件，用于播放音频
    SoundComponent = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("MediaSound"));
    SoundComponent->SetupAttachment(RootComponent);
}

void ASimpleVideoPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (!VideoPath.IsEmpty())
    {
        SetupAndPlay();
    }
}

void ASimpleVideoPlayerActor::SetupAndPlay()
{
    // 创建媒体播放器
    MediaPlayer = NewObject<UMediaPlayer>(this, TEXT("VideoPlayer"));
    MediaPlayer->SetLooping(bLoop);

    // 创建并配置媒体源
    MediaSource = NewObject<UFileMediaSource>(this, TEXT("VideoSource"));
    MediaSource->SetFilePath(VideoPath);

    // 将媒体声音组件连接到媒体播放器
    if (SoundComponent)
    {
        SoundComponent->SetMediaPlayer(MediaPlayer);
    }

    // 尝试打开并播放
    if (MediaPlayer->OpenSource(MediaSource))
    {
        UE_LOG(LogTemp, Log, TEXT("Opening video: %s"), *VideoPath);
        if (bAutoPlay)
        {
            // 打开是异步的，Play 会在媒体真正就绪后生效
            // 也可以绑定 OnMediaOpened 事件来确保立即播放
            MediaPlayer->Play();
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to open video source: %s"), *VideoPath);
    }
}
```

## 模块依赖

要使用 Electra Player，你的项目模块通常需要依赖以下模块（基于其内部模块的 `Build.cs` 分析）：

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供上层封装，如 `UMediaPlayer`, `UMediaSource`, `UMediaTexture` 等资产类。这是蓝图和C++访问媒体功能的主要入口。 |
| `MediaUtils` | 提供媒体播放相关的工具类和接口。 |
| `ElectraBase` | Electra 框架的基础模块，包含核心数据类型、接口和通用工具。`ElectraPlayerFactory` 和 `ElectraProtronFactory` 依赖它。 |
| `DirectX` | 平台特定依赖，用于支持 DirectX 相关的媒体解码和渲染（尤其影响 Protron 路径）。 |
| `D3D12RHI` | DirectX 12 渲染硬件接口模块，是 `ElectraProtron` 模块的依赖，用于高性能本地视频播放。 |

**重要提示**：对于大多数游戏逻辑，你**不需要**直接依赖 Electra 的底层运行时模块（如 `ElectraPlayerRuntime`）。你应通过 `MediaAssets` 模块提供的标准 `UMediaPlayer` API 进行操作，引擎会自动加载合适的底层播放器后端（可能是 Electra，也可能是其他平台默认播放器）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复 Protron 在播完一个视频后无法播放新视频的问题。 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复流媒体专辑元数据的读取错误。 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 增加配置选项，可控制播放时是否暂停解码器。 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将断言改为条件判断，以处理 .ts 文件内部时间戳异常的情况，提升稳定性。 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预加载字幕段时检查序列索引，减少不必要的请求。 |

### 维护评价

-   **创建时间**：创建于 2021 年初，作为“从内部（NFL）迁移到公开版本”的插件，历史约 4 年。
-   **活跃度**：**非常活跃**。从最近的提交记录看，就在几天前（2026年5月）仍有连续的、实质性的 Bug 修复和功能增强（涉及 Protron、元数据、稳定性等）。
-   **维护状态**：**活跃维护中**。作为 UE5 核心媒体框架的一部分，由 Epic 工程师持续维护和改进。
-   **已知问题**：从提交历史看，仍在不断发现和修复特定场景下的播放问题（如特定格式、特定平台、特定工作流）。
-   **推荐使用**：**强烈推荐**。它是 UE5 媒体播放的主力和未来方向，跨平台兼容性好，性能持续优化。对于新的媒体播放需求，应优先考虑使用 Electra Player 及其提供的标准 `UMediaPlayer` 接口。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
-   [测试用例] (待补充 - 测试用例通常位于 `Engine/Tests/` 目录下与 Media 或 Electra 相关的路径中)