# WebM Video Player

> A media player for WebM video files.

| 属性 | 值 |
|---|---|
| 中文名 | WebM视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (RuntimeNoCommandlet), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-12 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 插件为 Unreal Engine 提供了播放 WebM 格式视频文件（通常包含 VP8/VP9 视频编码和 Vorbis/Opus 音频编码）的能力。它集成了 `libvpx` 解码库，将 WebM 容器中的视频帧解码为引擎媒体框架可以处理的纹理格式，从而支持在游戏运行时、编辑器内或基于媒体框架的 UI 中播放 WebM 视频。该插件默认不启用，主要服务于需要支持 WebM 这一开放、免版税视频格式的跨平台（Windows/Linux）项目。

## 使用场景

- 你正在开发一款需要在 Windows 和 Linux 平台上播放 WebM 格式过场动画或教程视频的游戏。
- 你的项目使用了在线服务，需要播放来自网络的 VP9 编码视频流。
- 你在编辑器中需要预览 WebM 格式的素材，而不想依赖系统级的解码器。

## 蓝图用法

该插件作为底层媒体播放器实现，主要通过 UE 的 **Media Framework** 进行访问。核心蓝图节点通常来自 `MediaPlayer` 或 `MediaTexture` 类，而非本插件直接暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Open Source` / `Open Source Latent` | 打开一个媒体源（包括指向 WebM 文件的 `FileMediaSource`） | `UMediaPlayer` |
| `Play` / `Pause` / `Stop` | 控制媒体播放 | `UMediaPlayer` |
| `Seek` | 跳转到指定时间 | `UMediaPlayer` |
| `Get Time` / `Get Duration` | 获取当前时间和总时长 | `UMediaPlayer` |
| `Is Playing` / `Is Paused` | 检查播放状态 | `UMediaPlayer` |

### 使用示例（蓝图描述）

1.  在内容浏览器中创建一个 `FileMediaSource` 资产，在其设置中选择你的 `.webm` 文件。
2.  创建一个 `MediaPlayer` 资产，并确保其支持的媒体格式包含 `WebM`。
3.  在蓝图中：
    *   使用 “Create Media Source” 节点（或直接引用已创建的 `FileMediaSource`）获取源。
    *   将 `MediaPlayer` 的 “Open Source” 节点与媒体源连接。
    *   连接 “Play” 节点开始播放。
    *   通过 “Media Event” 节点（如 `On Media Opened`, `On Playback Resumed`）来响应播放状态变化。
    *   可以使用 “Seek” 节点实现拖拽进度条功能。

## C++ 用法

### 头文件引入

```cpp
#include "MediaPlayer.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"
#include "WebMMedia/WebMMediaModule.h" // 可选，用于查询模块状态
```

### 基本用法

通过 C++ 控制 WebM 视频的播放，与播放其他媒体格式（如 MP4）的流程一致。核心是创建并配置 `UMediaPlayer` 和 `UMediaSource` 对象。
**来源**: 引擎媒体框架通用测试用例，以及 `WebMMedia` 模块本身的集成代码。

```cpp
// 假设你已经有一个 UMediaPlayer* MediaPlayer 和一个指向 .webm 文件的路径 FilePath
UFileMediaSource* MediaSource = NewObject<UFileMediaSource>();
MediaSource->SetFilePath(FPaths::ProjectContentDir() + TEXT("Videos/MyVideo.webm"));

// 设置媒体播放器的事件回调
MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyActor::HandleMediaOpened);
MediaPlayer->OnPlaybackResumed.AddDynamic(this, &AMyActor::HandlePlaybackResumed);

// 打开媒体源
if (MediaPlayer->OpenSource(MediaSource))
{
    UE_LOG(LogTemp, Log, TEXT("WebM media source opening..."));
}

// 在事件处理函数中
void AMyActor::HandleMediaOpened(FString OpenedUrl)
{
    // 媒体已打开，可以开始播放
    MediaPlayer->Play();
}

void AMyActor::HandlePlaybackResumed()
{
    UE_LOG(LogTemp, Log, TEXT("WebM playback started."));
}
```

### 进阶用法

结合 `MediaTexture` 将视频帧渲染到物体表面。
**来源**: 引擎材质和媒体框架集成示例。

```cpp
// 在某个组件或资产上创建 MediaTexture
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
MediaTexture->SetMediaPlayer(MediaPlayer);
MediaTexture->UpdateResource(); // 确保资源初始化

// 然后，可以将 MediaTexture 作为纹理参数设置到材质实例上
UMaterialInstanceDynamic* MatInst = UMaterialInstanceDynamic::Create(BaseMaterial, this);
MatInst->SetTextureParameterValue(TEXT("VideoTexture"), MediaTexture);
// 应用 MatInst 到你的网格体组件上
```

## Demo 示例

一个最小化的 Actor，用于控制 WebM 视频播放。
**MyWebMPlayerActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayer.h"
#include "MyWebMPlayerActor.generated.h"

UCLASS()
class MYPROJECT_API AMyWebMPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyWebMPlayerActor();

    UPROPERTY(EditAnywhere, Category = "Media")
    FString WebMFilePath;

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Media")
    UMediaPlayer* MediaPlayer;

    UFUNCTION()
    void OnMediaOpened(FString OpenedUrl);
};
```
**MyWebMPlayerActor.cpp**
```cpp
#include "MyWebMPlayerActor.h"
#include "FileMediaSource.h"
#include "MediaTexture.h"

AMyWebMPlayerActor::AMyWebMPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;
    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("WebMPlayer"));
}

void AMyWebMPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (!WebMFilePath.IsEmpty())
    {
        UFileMediaSource* Source = NewObject<UFileMediaSource>();
        Source->SetFilePath(WebMFilePath);

        MediaPlayer->OnMediaOpened.AddDynamic(this, &AMyWebMPlayerActor::OnMediaOpened);
        MediaPlayer->OpenSource(Source);
    }
}

void AMyWebMPlayerActor::OnMediaOpened(FString OpenedUrl)
{
    UE_LOG(LogTemp, Log, TEXT("WebM video opened: %s"), *OpenedUrl);
    MediaPlayer->Play();
}
```

## 模块依赖

该插件依赖于以下不常见的模块：

| 模块 | 用途 |
|---|---|
| `LibVpx` | 提供 VP8/VP9 视频编解码器的静态库，是 WebM 视频解码的核心。 |
| `MediaUtils` | UE 媒体框架的工具函数库。 |

要使用此插件，你的项目模块（在 `.Build.cs` 文件中）需要添加对 `MediaUtils` 的依赖。`LibVpx` 由插件自身的 `WebMMedia` 模块链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `6fa2f4c5` | WebMMedia: Fixed video full range yuv offsets | 修复了视频全范围 YUV 色彩偏移问题 |
| 2026-04-21 | `f9163c8f` | WebMMedia: Added support for 10 bit VP9 files; fixed an issue where images were overwritten before t | 增加了 10 位 VP9 文件支持；修复了图像在处理前被覆盖的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 将 libvpx 库更新至 1.15.1 版本 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | 对 WebMMedia 插件进行了重写 |

### 维护评价

该插件自 2018 年创建，历史较长，但**近期（2026年初）有明显的活跃开发迹象**。最近的提交包括一次插件重写、依赖库升级、功能增强（10位色深支持）以及重要的色彩空间bug修复。这表明该插件正在积极维护和改进。尽管标记为实验性且默认禁用，但对于有 WebM 格式硬需求的 Windows/Linux 项目来说，它是一个可行且正在完善的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/webm-media-player-plugin-for-unreal-engine/) (从 .uplugin 信息推断)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia/Tests) (路径推断，实际测试可能位于 MediaFramework 框架测试中)