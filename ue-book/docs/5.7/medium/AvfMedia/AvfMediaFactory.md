# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | AVF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (RuntimeNoCommandlet), `AvfMediaCapture` (RuntimeNoCommandlet), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor), `AvfMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia) | |

## 用途

AVF Media Player 是苹果平台（iOS、macOS、tvOS）的原生媒体播放解决方案。它基于 Apple AV Foundation 框架，提供了高性能的视频/音频解码和渲染能力。该插件解决了在虚幻引擎中使用苹果设备硬件加速播放本地或远程媒体文件的需求，适用于播放高分辨率视频、流媒体、电影片段等场景。

插件分为多个模块：
- `AvfMedia`：核心播放与渲染逻辑。
- `AvfMediaCapture`：媒体捕获功能（如从设备摄像头/麦克风采集）。
- `AvfMediaEditor`：编辑器支持，如媒体源配置。
- `AvfMediaFactory`：提供工厂类注册和全局设置（如 `UAvfMediaSettings`）。

## 使用场景

- 在 iOS/macOS/tvOS 游戏中播放过场动画或视频纹理（如电视屏幕、全屏背景动画）。
- 流媒体播放需求，如在线广告、直播内容（需 AVFoundation 支持的网络协议）。
- 视频编辑工具中预览和播放本地媒体文件。
- 需要在苹果设备上利用硬件解码减轻 CPU 负载时。

## 蓝图用法

本插件提供的蓝图可用节点主要集中在媒体播放器的常规流程（打开媒体源、播放、暂停等），这些节点属于引擎内置的 `MediaPlayer` 蓝图函数库，并非本插件独有。本插件仅提供平台实现，不对蓝图暴露额外函数。

唯一可通过蓝图访问的是 **项目设置** 中的 `AvfMediaSettings` 配置。

### 项目设置配置

| 属性 | 说明 |
|---|---|
| `NativeAudioOut` | 是否使用操作系统的原生音频混合器播放音频（而非虚幻的音频引擎）。启用后可能与某些音频处理效果冲突，但可降低延迟。 |

设置路径：`项目设置 -> 插件 -> Avf Media Player -> Debug -> Native Audio Out`

## C++ 用法

### 头文件引入

```cpp
#include "AvfMediaSettings.h"
```

### 基本用法

获取全局设置并修改 `NativeAudioOut`：

```cpp
#include "AvfMediaSettings.h"

void ConfigureAvfMedia()
{
    if (UAvfMediaSettings* Settings = GetMutableDefault<UAvfMediaSettings>())
    {
        Settings->NativeAudioOut = true;
        Settings->SaveConfig();  // 持久化到配置文件
    }
}
```

### 进阶用法

创建媒体播放器并使用 AVF 播放（需要先启用插件并确保平台支持）：

```cpp
#include "MediaPlayer.h"
#include "MediaSource.h"

void PlayLocalVideo()
{
    UMediaPlayer* Player = NewObject<UMediaPlayer>();
    UMediaSource* Source = LoadObject<UMediaSource>(nullptr, TEXT("/Game/Movies/MyVideo.uasset"));

    if (Player && Source)
    {
        Player->PlayOnOpen = true;
        Player->OpenSource(Source);
    }
}
```
> 注：以上代码为通用媒体播放流程，`AvfMediaFactory` 会自动注册媒体播放器实现。插件启用后，默认即可处理 `mov`、`mp4`、`m4v` 等常见格式（取决于平台支持）。

## Demo 示例

以下是一个最小 C++ 示例，展示如何在关卡中加载并播放本地媒体文件（假设已创建 `UMediaPlayer` 和 `UMediaSource` 资产）：

**MediaPlayerActor.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MediaPlayerActor.generated.h"

class UMediaPlayer;
class UMediaSource;
class UMediaSoundComponent;

UCLASS()
class AMediaPlayerActor : public AActor
{
    GENERATED_BODY()

public:
    AMediaPlayerActor();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere, Category="Media")
    UMediaPlayer* MediaPlayer;

    UPROPERTY(VisibleAnywhere, Category="Media")
    UMediaSoundComponent* SoundComponent;

    UPROPERTY(EditAnywhere, Category="Media")
    UMediaSource* MediaSource;
};
```

**MediaPlayerActor.cpp**

```cpp
#include "MediaPlayerActor.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "Components/MediaSoundComponent.h"

AMediaPlayerActor::AMediaPlayerActor()
{
    PrimaryActorTick.bCanEverTick = false;

    MediaPlayer = CreateDefaultSubobject<UMediaPlayer>(TEXT("MediaPlayer"));
    SoundComponent = CreateDefaultSubobject<UMediaSoundComponent>(TEXT("SoundComponent"));
    
    // 将音频输出连接到媒体播放器
    SoundComponent->SetMediaPlayer(MediaPlayer);

    // 设置媒体选项（可选）：使用原生音频输出
    // 需先修改 UAvfMediaSettings
}

void AMediaPlayerActor::BeginPlay()
{
    Super::BeginPlay();

    if (MediaPlayer && MediaSource)
    {
        MediaPlayer->PlayOnOpen = true;
        MediaPlayer->OpenSource(MediaSource);
    }
}
```

## 模块依赖

根据各模块 `Build.cs` 分析，本插件的依赖较为精简，主要依赖引擎核心模块。

| 模块 | 用途 |
|---|---|
| `AvfMedia` | 核心 AVF 媒体播放器实现 |
| `Media` | 虚幻媒体框架接口 |
| `MediaAssets` | 媒体相关资产类（如 `UMediaPlayer` 等） |
| `MediaUtils` | 媒体工具函数 |

**省略常见依赖**：`Core`、`CoreUObject`、`Engine`、`Slate`、`SlateCore`、`UMG`、`InputCore`。

> 注意：若需要在编辑器中使用，还需依赖 `UnrealEd`、`PropertyEditor` 等，但本插件的 `AvfMediaEditor` 模块已自带这些依赖。

## 维护状态

### 近期更新

- 2025-06-26 `d2ec2238` — Generalized IOSAsyncTask to AppleAsyncTask in preparation for using WebKit in the macOS WebBrowser e
- 2025-06-02 `2c095ca4` — Replace EBulkDataType in MetalRHI with Metal-specific RHI functions
- 2025-05-06 `5243d97b` — Merging //UE5/Dev-ParallelRendering to Main (//UE5/Main)
- 2025-04-23 `6ae57335` — Used UnrealGame build target to find and convert all files to have dllstorage on methods/staticvar i
- 2025-04-10 `ea97db60` — Movie Render Queue:  High-res tiling support for paging scene view state persistent data to system m

### 维护评价

**综合评价**：✅ 推荐使用

- **创建时间**：2025年4月，距今不到1年。
- **最近更新**：2025年6月仍有涉及该插件的提交，表明处于活跃维护状态。
- **内容**：提交涉及平台适配性改进（如 `AppleAsyncTask` 泛化）和渲染管线适配，属于正常迭代。
- **限制**：仅支持苹果平台（iOS、macOS、tvOS），且需要设备支持 AVFoundation 框架。在某些老旧设备上可能性能不佳。
- **兼容性**：插件内置了 `PlatformAllowList`，确保仅在苹果设备上加载，无需担心跨平台冲突。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia)
- [官方文档（UE4 媒体框架）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia/Tests)（如果仓库中存在）