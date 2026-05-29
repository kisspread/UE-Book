# Electra Player

> Cross platform media player for local files and internet streaming.
Also provides optimized local mp4 file only player (Protron) for desktop machines.

| 属性 | 值 |
|---|---|
| 中文名 | 闪电媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraPlayerFactory` (Runtime), `ElectraPlayerPlugin` (Runtime), `ElectraPlayerPluginHandler` (Runtime), `ElectraPlayerRuntime` (Runtime), `ElectraProtron` (Runtime), `ElectraProtronFactory` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-01-06 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer) | |

## 用途

ElectraPlayer 是 UE5 中一个高性能的跨平台媒体播放器插件。它旨在替代或补充 UE 的原生媒体框架，主要解决以下问题：
1.  **统一且高效的媒体播放**：提供一套能够处理本地文件（特别是 MP4）和互联网流媒体（如 HLS, MPEG-DASH）的通用播放器。
2.  **性能优化**：包含一个名为 **Protron** 的专用播放器，专门针对桌面平台（Windows）的本地 MP4 文件播放进行深度优化，利用 DirectX 12 等底层技术实现更高的解码和渲染效率。
3.  **平台覆盖**：作为“跨平台”方案，它旨在为不同操作系统提供一致且稳定的媒体播放能力。

简单来说，它解决了在 UE 中播放网络视频流或需要高性能播放本地视频时的需求。

## 使用场景

-   你需要在游戏中播放来自互联网的实时视频流（如直播、广告视频）。
-   你需要在桌面平台上（特别是 Windows）以最高性能播放本地的 MP4 文件（如过场动画、背景视频）。
-   你需要一个统一的媒体播放接口，既能处理本地文件，也能处理网络流媒体。
-   你遇到了 UE 原生媒体播放器的性能或兼容性问题，希望寻找更优的解决方案。

## 蓝图用法

由于当前分析的 `ElectraPlayerPluginHandler` 模块主要负责插件生命周期管理，不直接暴露媒体播放控制节点。媒体播放的核心蓝图节点（如打开媒体、播放、暂停等）通常由 `MediaPlayer` 资产配合 `MediaTexture` 实现，并通过 `ElectraPlayerPlugin` 和 `ElectraPlayerRuntime` 提供底层支持。

**核心蓝图节点示例**（基于常见媒体播放器模式）：

| 节点 | 说明 | 所在类/上下文 |
|---|---|---|
| `Open Source` / `Open URL` | 在媒体播放器资产上打开本地文件或网络流地址 | `UMediaPlayer` |
| `Play` | 开始播放媒体 | `UMediaPlayer` |
| `Pause` / `Stop` | 暂停或停止播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间点 | `UMediaPlayer` |
| `Get Time` / `Get Duration` | 获取当前播放时间和总时长 | `UMediaPlayer` |
| `Is Playing` / `Is Paused` | 获取播放状态 | `UMediaPlayer` |

**使用示例（蓝图描述）**：
1.  在内容浏览器中，创建一个 `Media Player` 资产（例如 `MP_ElectraPlayer`）。
2.  在蓝图中，添加一个 `Media Texture` 组件或引用一个 `MediaTexture` 资产。
3.  将 `Media Texture` 设置为使用 `MP_ElectraPlayer`。
4.  在事件图表中，使用 `Open URL` 节点，将 `MP_ElectraPlayer` 拖入目标，并填入视频的 URL（如 `https://example.com/video.mp4`）或本地文件路径（如 `Game/Movies/Intro.mp4`）。
5.  连接一个 `Play` 节点来开始播放。
6.  使用 `Get Time` 等节点获取播放信息，或通过 `On Media Opened` 等事件委托处理播放状态。

## C++ 用法

当前模块 `ElectraPlayerPluginHandler` 仅包含模块接口。更深入的媒体控制 API 主要通过 UE 标准的 `UMediaPlayer` 类和其依赖的底层解码器（由本插件提供）来使用。

### 头文件引入

对于基本的媒体播放功能，使用 UE 的公共头文件即可：
```cpp
#include "MediaPlayer.h"
#include "MediaTexture.h"
```
对于更底层的、直接与 Electra 播放器交互的 API，可能需要引入特定模块的头文件（通常不推荐直接使用，除非进行引擎级开发）。

### 基本用法

使用标准的 `UMediaPlayer` API 进行媒体播放，底层会自动使用 Electra 播放器。
```cpp
// 假设已有 UMediaPlayer* MediaPlayer;
// 打开一个网络流
FString URL = TEXT("http://example.com/live/stream.m3u8");
MediaPlayer->OpenUrl(URL);

// 打开一个本地文件（会自动使用Protron优化播放器）
FString FilePath = FPaths::ProjectContentDir() / TEXT("Movies/MyVideo.mp4");
MediaPlayer->OpenFile(FilePath);

// 播放
if (MediaPlayer->Play())
{
    UE_LOG(LogTemp, Log, TEXT("Media playback started."));
}
```

### 进阶用法

监控媒体状态变化，处理播放完成事件。
```cpp
// 绑定媒体打开成功事件
MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::HandleMediaOpened);
// 绑定播放完成事件
MediaPlayer->OnPlaybackEnd.AddDynamic(this, &AMyActor::HandlePlaybackEnd);
```

## Demo 示例

一个最小的 Actor 示例，用于在构造时打开并循环播放一个本地 MP4 文件。

```cpp
// MyMediaActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MyMediaActor.generated.h"

UCLASS()
class AMyMediaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMediaActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere)
    UMediaTexture* MediaTexture;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
};
```

```cpp
// MyMediaActor.cpp
#include "MyMediaActor.h"
#include "MediaTexture.h"

AMyMediaActor::AMyMediaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建媒体播放器组件（实际使用中通常在蓝图中创建资产）
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    // 创建媒体纹理组件并关联
    MediaTexture = CreateDefaultSubobject<UMediaTexture>(TEXT("MediaTexture"));
    MediaTexture->SetMediaPlayer(MediaPlayer);
    // 设置循环播放
    MediaPlayer->SetLooping(true);
}

void AMyMediaActor::BeginPlay()
{
    Super::BeginPlay();

    // 绑定媒体打开完成事件
    MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyMediaActor::OnMediaOpened);

    // 尝试打开一个测试视频文件
    FString TestVideoPath = FPaths::ProjectContentDir() / TEXT("Movies/Test.mp4");
    MediaPlayer->OpenFile(TestVideoPath);
}

void AMyMediaActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Warning, TEXT("Media successfully opened: %s"), *OpenedUrl);
    // 媒体打开后，播放会由 MediaPlayer 的 SetLooping 控制自动开始
}
```

## 模块依赖

本插件由多个内部模块构成，对于使用者而言，**无需直接依赖这些模块**。使用者只需像使用任何其他媒体播放器一样，依赖 `MediaAssets` 模块并使用 `UMediaPlayer` 等公共类。插件的底层模块会被引擎自动加载。

| 模块 | 用途 |
|---|---|
| `ElectraPlayerRuntime` | Electra 播放器的核心解码和渲染运行时 |
| `ElectraPlayerPlugin` | 作为 `MediaPlayer` 的插件后端，将播放请求转发给 Electra 运行时 |
| `ElectraPlayerPluginHandler` | 插件生命周期管理，注册和注销播放器 |
| `ElectraPlayerFactory` | 创建 Electra 播放器实例的工厂 |
| `ElectraProtron` | 专门针对桌面 MP4 播放优化的解码器和渲染器 |
| `ElectraProtronFactory` | 创建 Protron 优化播放器实例的工厂 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `ff9996e8` | Media Profile: Fixed issue where ElectraProtron issue would not play a new video after it had alread | 修复了 Protron 播放器播放完一个视频后无法播放新视频的问题 |
| 2026-05-14 | `d15b78b3` | ElectraPlayer: Fixed streamed album metadata | 修复了流式播放专辑元数据的解析问题 |
| 2026-05-13 | `4340cfa6` | ElectraPlayer: Added configuration and cvars to control if decoders need to be suspended during play | 新增配置和控制台变量，用于控制播放期间是否挂起解码器 |
| 2026-05-12 | `a6372743` | ElectraPlayer: changed an assertion to an if() condition to handle cases where .ts internal timestam | 将断言改为 if 条件判断，以处理 .ts 内部时间戳异常的情况 |
| 2026-05-12 | `e3746831` | ElectraPlayer: Checking for sequence index when prefetching subtitle media segments to reduce unnece | 在预加载字幕分片时检查序列索引，以减少不必要的网络请求 |

### 维护评价

该插件由 Epic Games 官方维护，是 UE 媒体播放体系的核心组成部分。

-   **活跃维护**：从 git 历史看，该插件（包括其子模块）持续收到更新，最近一次更新在 2026 年 5 月，包含功能增强和 Bug 修复。这表明它仍处于活跃开发和维护中。
-   **重要性**：作为官方提供的跨平台媒体播放解决方案，特别是在高性能本地播放（Protron）和流媒体支持方面，它在项目中的重要性很高。
-   **推荐使用**：对于需要在 UE5 项目中集成媒体播放功能，尤其是涉及网络流或追求桌面端本地播放性能的项目，**强烈推荐使用**。它比引擎原生媒体框架通常更强大和稳定。由于是官方插件，其兼容性和支持有保障。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraPlayer)
-   [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)