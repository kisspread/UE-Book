# WebM Video Player

> WebM Video Player

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-12 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 是 Unreal Engine 5 媒体框架的一个后端实现，它提供了对 `.webm` 格式（主要是 VP8 和 VP9 视频编码）媒体文件的解码和播放能力。该插件的目的是在支持的操作系统（如 Windows 和 Linux）上，让 UE5 项目能够直接播放 WebM 格式的视频，无需额外的第三方库或转码。它解决了在特定平台（特别是开源和跨平台场景）下对 WebM 这一开放媒体格式的原生支持需求。

## 使用场景

-   你正在开发一款面向 PC (Windows/Linux) 的游戏，并希望使用开源、免版税的 WebM 格式作为游戏内过场动画、背景视频或 UI 动画资源。
-   你的项目需要支持 Linux 平台，而该平台对 WebM 格式有更好的系统支持。
-   你需要一种无需依赖特定硬件解码器或专利授权（如 H.264）的视频播放方案，特别是在使用 VP9 编码时。
-   你希望在 UE5 编辑器中预览和测试 `.webm` 文件。

## 蓝图用法

WebMMedia 插件本身主要作为媒体框架的底层实现，不直接提供新的蓝图节点。用户通常通过 UE5 内置的媒体播放器蓝图功能来使用它。核心在于设置正确的媒体源。

### 核心节点

该插件通过媒体框架体系工作，因此主要使用通用媒体播放器节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` | 打开一个媒体源进行播放。当源指向 `.webm` 文件时，系统会自动调用 WebMMedia 解码器。 | `UMediaPlayer` |
| `Play` | 开始播放已打开的媒体。 | `UMediaPlayer` |
| `Pause` | 暂停播放。 | `UMediaPlayer` |
| `Close` | 关闭当前媒体。 | `UMediaPlayer` |
| `Seek` | 定位到视频的特定时间点。 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  **准备资产**：将 `.webm` 文件导入到 UE5 项目内容浏览器中。
2.  **创建媒体源**：在内容浏览器中，右键点击导入的 `.webm` 文件，选择“创建媒体源”（`Create Media Source`）。这将生成一个对应的 `UMediaSource` 资产。
3.  **添加媒体播放器**：在你的 UI 蓝图（`UMG Widget`）或 Actor 中，添加一个 `Media Player` 组件。
4.  **连接蓝图**：
    -   在蓝图中，拖入 `Media Player` 组件引用。
    -   调用 `Open Source` 节点，将上一步创建的 `UMediaSource` 资产作为输入。
    -   连接 `Play` 节点即可开始播放。
    -   你还可以连接 `Set Loop` 节点来控制是否循环播放，使用 `Set Playback Speed` 节点调整播放速度。

## C++ 用法

### 头文件引入

使用 WebMMedia 功能通常不需要直接包含其头文件，而是通过 UE5 的媒体框架（`MediaAssets`）进行操作。如果需要进行底层调试或查询模块状态，可以引入：

```cpp
#include "WebMMedia/WebMMediaModule.h"
```

### 基本用法

```cpp
// 示例来源：基于媒体框架通用用法
#include "MediaSource.h"
#include "MediaPlayer.h"
#include "MediaTexture.h"
#include "Components/Image.h"

// 在某个初始化函数中
void AMyActor::SetupMediaPlayer()
{
    // 1. 获取或创建 MediaPlayer
    MediaPlayer = NewObject<UMediaPlayer>();

    // 2. 加载媒体源（指向 .webm 文件）
    FString MediaPath = FPaths::ProjectContentDir() / TEXT("Videos/MyVideo.webm");
    UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
    MediaSource->SetFilePath(MediaPath);

    // 3. 打开媒体源
    if (MediaPlayer->OpenSource(MediaSource))
    {
        // 4. 设置媒体纹理（用于在 UMG 或 3D 场景中显示）
        UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
        MediaTexture->SetMediaPlayer(MediaPlayer);

        // 5. 将 MediaTexture 应用到 UMG 的 Image 组件
        UImage* ImageWidget = /* 获取你的 Image 组件 */;
        FSlateBrush Brush;
        Brush.SetResourceObject(MediaTexture);
        ImageWidget->SetBrush(Brush);

        // 6. 播放
        MediaPlayer->Play();
    }
}
```

### 进阶用法

```cpp
// 处理播放事件
void AMyActor::BindMediaPlayerEvents()
{
    if (MediaPlayer)
    {
        // 绑定媒体打开成功事件
        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::OnMediaOpened);
        // 绑定播放结束事件
        MediaPlayer->OnPlaybackEnd.AddDynamic(this, &AMyActor::OnPlaybackEnd);
        // 绑定媒体打开失败事件
        MediaPlayer->OnMediaOpenFailed.AddDynamic(this, &AMyActor::OnMediaOpenFailed);
    }
}

void AMyActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("WebM Media Opened: %s"), *OpenedUrl);
    // 可以在此获取视频时长等信息
    FTimespan Duration = MediaPlayer->GetDuration();
}

void AMyActor::OnPlaybackEnd()
{
    UE_LOG(LogTemp, Log, TEXT("WebM Playback Finished"));
    // 播放结束后的逻辑，例如关闭或切换视频
}

void AMyActor::OnMediaOpenFailed(FString FailedUrl)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to Open WebM Media: %s"), *FailedUrl);
}
```

## Demo 示例

一个最小的可运行示例，展示如何在 C++ 中控制 WebM 视频的播放。

**WebMPlayerDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaSource.h"
#include "MediaPlayer.h"
#include "WebMPlayerDemo.generated.h"

UCLASS()
class AWebMPlayerDemo : public AActor
{
    GENERATED_BODY()

public:
    AWebMPlayerDemo();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "Media")
    void PlayWebMVideo(const FString& VideoFilePath);

    UFUNCTION(BlueprintCallable, Category = "Media")
    void StopWebMVideo();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Media")
    UMediaPlayer* MediaPlayer;

private:
    UPROPERTY()
    UFileMediaSource* CurrentMediaSource;
};
```

**WebMPlayerDemo.cpp**
```cpp
#include "WebMPlayerDemo.h"
#include "MediaSource.h"

AWebMPlayerDemo::AWebMPlayerDemo()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
}

void AWebMPlayerDemo::BeginPlay()
{
    Super::BeginPlay();
    // 可以在蓝图中调用 PlayWebMVideo 或在此自动播放
    // PlayWebMVideo(FPaths::ProjectContentDir() / TEXT("Videos/Example.webm"));
}

void AWebMPlayerDemo::PlayWebMVideo(const FString& VideoFilePath)
{
    if (!MediaPlayer || VideoFilePath.IsEmpty())
    {
        return;
    }

    // 创建并设置媒体源
    CurrentMediaSource = NewObject<UFileMediaSource>(this);
    CurrentMediaSource->SetFilePath(VideoFilePath);

    // 打开媒体并播放
    if (MediaPlayer->OpenSource(CurrentMediaSource))
    {
        MediaPlayer->Play();
        UE_LOG(LogTemp, Log, TEXT("Started Playing WebM Video: %s"), *VideoFilePath);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to Play WebM Video: %s"), *VideoFilePath);
    }
}

void AWebMPlayerDemo::StopWebMVideo()
{
    if (MediaPlayer && MediaPlayer->IsPlaying())
    {
        MediaPlayer->Close();
        UE_LOG(LogTemp, Log, TEXT("Stopped WebM Video Playback"));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LibVpx` | 核心视频解码库，用于解码 VP8/VP9 视频流。 |
| `MediaFrameworkUtilities` | 媒体框架的通用工具函数和基类，插件集成的基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `6fa2f4c5` | WebMMedia: Fixed video full range yuv offsets | 修复了全范围 YUV 视频的色彩偏移问题。 |
| 2026-04-21 | `f9163c8f` | WebMMedia: Added support for 10 bit VP9 files; fixed an issue where images were overwritten before t... | 增加了对 10 位色深 VP9 文件的支持，并修复了图片被过早覆盖的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF。 |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 升级底层 libvpx 解码库到 1.15.1 版本。 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | 对插件进行了整体重写，是重大的结构性更新。 |

### 维护评价

WebMMedia 插件在 2026 年初经历了一次重大重写（`0bfe789b`），随后有多次针对性的功能增强（如 10 位 VP9 支持）和错误修复。提交历史显示其维护状态**非常活跃**。虽然 .uplugin 中 `IsBetaVersion=true` 表明它仍处于实验阶段，但持续的更新表明 Epic Games 正在积极改进和稳定它。考虑到 WebM 是开源社区常用的格式，且该插件正在不断进化，**推荐在 Windows/Linux 项目中尝试使用**，但需注意其“实验性”标签可能意味着未来 API 或行为仍有变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)
- 官方文档：无（目前未在官方文档中发现独立页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia/Source/WebMMedia/Tests) （存在于源码目录中，用于自动化测试）