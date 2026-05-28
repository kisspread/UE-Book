# Android Media Player

> Implements a media player using the Android Media library.

| 属性 | 值 |
|---|---|
| 中文名 | 安卓媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AndroidMedia` (RuntimeNoCommandlet), `AndroidMediaEditor` (Editor), `AndroidMediaFactory` (Editor), `AndroidMediaFactory` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-11-17 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia) | |

## 用途

本插件为 Android 平台提供了基于原生 `android.media.MediaPlayer` API 的媒体播放器实现。它解决了在 Unreal Engine 项目中于 Android 设备上播放视频和音频的核心需求，深度集成了 Android 的媒体框架，提供了高性能的纹理流送和精确的播放控制。它主要通过 JNI 与 Java 层的 `MediaPlayer` 对象交互，处理媒体轨道（音频、视频、字幕）、播放状态管理以及在应用前后台切换时的生命周期处理。

## 使用场景

- **播放过场动画或游戏内视频**：在 Android 设备上播放预制的过场动画、背景视频或游戏内新闻。
- **实现游戏内媒体播放器功能**：为 Android 平台的媒体播放器应用或功能提供底层支持。
- **处理应用生命周期**：确保在应用切换至后台时媒体播放能正确暂停，返回前台时恢复，避免崩溃或资源泄漏。
- **需要精确纹理控制**：当视频需要作为纹理映射到场景物体上，且对纹理的上传和转换（如 OES 或 Vulkan 路径）有特定要求时。

## 蓝图用法

该插件主要通过 Unreal Engine 的 **Media Player** 蓝图资产系统使用。`AndroidMedia` 模块本身并不直接暴露 `BlueprintCallable` 节点，而是作为 Media Player 框架的 Android 平台后端被自动调用。用户主要在蓝图中使用标准的 `MediaPlayer` 资产和 `MediaTexture` 资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接暴露节点） | 插件功能通过 Media Player 框架的 `OpenUrl`, `Play`, `Pause` 等标准接口访问 | `UMediaPlayer`, `IMediaPlayer` |

### 使用示例（蓝图描述）

1.  创建一个 **Media Player** 资产。
2.  在需要播放视频的 Actor 或 Widget 中，添加一个 **Media Sound Component** 和一个使用 **Media Texture** 的 **Material**。
3.  通过蓝图，使用 **Open Source** 节点并传入媒体 URL（例如 `file:///sdcard/movie.mp4` 或 OBB 包内的路径）来打开媒体。
4.  随后，调用 **Play**、**Pause**、**Seek** 等标准媒体控制节点进行操作。当在 Android 设备上运行时，底层的媒体播放将由 `AndroidMedia` 插件处理。

## C++ 用法

通过 C++ 可以更直接地控制媒体播放器实例，例如自定义创建逻辑或处理播放事件。

### 头文件引入

```cpp
#include "IMediaPlayer.h"
#include "IAndroidMediaModule.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建一个 Android 媒体播放器并打开一个媒体文件。代码逻辑源于 `IAndroidMediaModule` 的接口定义和典型的媒体框架使用方式。

```cpp
// 假设你已经有一个有效的 IMediaEventSink 实现（例如你的播放器类）
IMediaEventSink& MyEventSink = /* ... */;

// 获取 AndroidMedia 模块
IAndroidMediaModule* AndroidMediaModule = FModuleManager::GetModulePtr<IAndroidMediaModule>(“AndroidMedia”);

if (AndroidMediaModule)
{
    // 创建 Android 媒体播放器实例
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer = AndroidMediaModule->CreatePlayer(MyEventSink);

    if (MediaPlayer.IsValid())
    {
        // 打开一个位于设备存储上的媒体文件
        FString MediaUrl = TEXT(“file:///sdcard/Download/sample.mp4”);
        MediaPlayer->Open(MediaUrl, nullptr);

        // 开始播放
        MediaPlayer->GetControls().SetRate(1.0f);
    }
}
```

### 进阶用法

`FAndroidMediaPlayer` 内部处理了应用前后台切换的暂停与恢复逻辑，这是 Android 平台开发的关键。开发者也可以监听相关的媒体事件来同步状态。

```cpp
// 在你的播放器类中，监听媒体状态变化
// 源自 FAndroidMediaPlayer 的实现逻辑，它通过 IMediaEventSink 发送事件。
void UMyMediaPlayerComponent::OnMediaEvent(EMediaEvent Event)
{
    switch (Event)
    {
    case EMediaEvent::MediaOpened:
        // 媒体已打开，可以查询轨道信息
        if (MediaPlayer.IsValid())
        {
            int32 NumVideoTracks = MediaPlayer->GetTracks().GetNumTracks(EMediaTrackType::Video);
            UE_LOG(LogTemp, Log, TEXT(“Video tracks found: %d”), NumVideoTracks);
        }
        break;

    case EMediaEvent::PlaybackEndReached:
        // 播放结束
        break;

    case EMediaEvent::PlaybackSuspended:
        // 播放已挂起（可能因为应用进入后台）
        break;

    case EMediaEvent::PlaybackResumed:
        // 播放已恢复
        break;
    }
}
```

## Demo 示例

一个最小的、可编译的 C++ 示例，演示如何持有并使用 Android 媒体播放器。

```cpp
// AndroidMediaDemoActor.h
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “IMediaPlayer.h”
#include “IMediaEventSink.h”
#include “AndroidMediaDemoActor.generated.h”

UCLASS()
class AAndroidMediaDemoActor : public AActor, public IMediaEventSink
{
    GENERATED_BODY()

public:
    AAndroidMediaDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // IMediaEventSink interface
    virtual void ReceiveMediaEvent(EMediaEvent Event) override;

private:
    TSharedPtr<IMediaPlayer, ESPMode::ThreadSafe> MediaPlayer;

    UPROPERTY(EditAnywhere, Category = “Media”)
    FString MediaUrl = TEXT(“file:///sdcard/UE5Demo/video.mp4”);

    void HandleMediaOpened();
};
```

```cpp
// AndroidMediaDemoActor.cpp
#include “AndroidMediaDemoActor.h”
#include “Modules/ModuleManager.h”
#include “IAndroidMediaModule.h”

AAndroidMediaDemoActor::AAndroidMediaDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AAndroidMediaDemoActor::BeginPlay()
{
    Super::BeginPlay();

    IAndroidMediaModule* AndroidMediaModule = FModuleManager::GetModulePtr<IAndroidMediaModule>(“AndroidMedia”);

    if (AndroidMediaModule)
    {
        MediaPlayer = AndroidMediaModule->CreatePlayer(*this);
        if (MediaPlayer.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT(“Android Media Player created. Opening: %s”), *MediaUrl);
            MediaPlayer->Open(MediaUrl, nullptr);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT(“Failed to create Android Media Player”));
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT(“AndroidMedia module not found.”));
    }
}

void AAndroidMediaDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MediaPlayer.IsValid())
    {
        MediaPlayer->Close();
        MediaPlayer.Reset();
    }
    Super::EndPlay(EndPlayReason);
}

void AAndroidMediaDemoActor::ReceiveMediaEvent(EMediaEvent Event)
{
    switch (Event)
    {
    case EMediaEvent::MediaOpened:
        HandleMediaOpened();
        break;
    case EMediaEvent::PlaybackEndReached:
        UE_LOG(LogTemp, Log, TEXT(“Playback finished.”));
        break;
    default:
        break;
    }
}

void AAndroidMediaDemoActor::HandleMediaOpened()
{
    if (MediaPlayer.IsValid())
    {
        // 媒体打开成功，开始播放
        MediaPlayer->GetControls().SetRate(1.0f);
        UE_LOG(LogTemp, Log, TEXT(“Media opened, playback started.”));
    }
}
```

## 模块依赖

该插件包含四个模块，每个模块的依赖关系在其对应的 `Build.cs` 中定义。

**`AndroidMedia` (RuntimeNoCommandlet):**
- 平台限制：仅限 Android。
- 特有依赖：`AndroidMediaFactory`。

**`AndroidMediaEditor` (Editor):**
- 特有依赖：`AndroidMediaFactory`。

**`AndroidMediaFactory` (Editor & RuntimeNoCommandlet):**
- 特有依赖：`MediaAssets`。

**总结：** 在你的项目模块中使用此插件时，通常需要链接 `MediaAssets` 模块。若需要直接创建播放器实例，则需链接 `AndroidMedia` 模块（需条件判断平台）。

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 提供媒体播放器、纹理等资产类型和框架接口 |
| `AndroidMediaFactory` | 为 `AndroidMedia` 播放器提供创建工厂，被 `AndroidMedia` 和 `AndroidMediaEditor` 模块依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移到新的 `UE_LOGF` 宏 |
| 2026-02-05 | `d5be7e14` | Fixed printfs. | 修复了 `printf` 调用 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码风格优化，将析构函数体清空改为显式默认 |
| 2025-08-29 | `32884de4` | Changing more uses of RHICreateTexture to RHICmdList.CreateTexture. | 继续将旧的纹理创建 API 迁移到命令列表的新 API |
| 2025-06-18 | `79ad0f74` | Updated CameraPlayer14 to Camera2 API. | 将相机播放器从过时的 Camera1 API 更新到 Camera2 API |

### 维护评价

- **创建时间**：2014 年创建，是一个非常成熟的“文物级”插件。
- **近期活跃度**：截至 2026 年 4 月仍有更新，主要涉及引擎 API 升级（日志、渲染 API 迁移）和 Android 平台 API 更新（Camera2）。这表明 Epic 仍在维持其与最新引擎版本和 Android SDK 的兼容性。
- **功能稳定性**：核心功能（基于 `MediaPlayer` 的播放）已非常稳定。近期的更新多为维护性和兼容性改进，而非重大新功能。
- **限制**：作为运行时模块，它严格限于 `Android` 平台（`PlatformAllowList`）。其 `Editor` 模块仅用于编辑器内的资产处理和预览。
- **推荐**：**强烈推荐使用**。它是 Unreal Engine 在 Android 平台上官方且默认启用的媒体播放解决方案。只要你的项目需要支持 Android 平台的媒体播放，就应该使用此插件。其长期的维护历史和近期的更新证明了它的可靠性和 Epic 的支持承诺。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AndroidMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview) (Media Framework 概述文档)
- [测试用例]（无特定测试文件，可通过 Media Framework 的通用测试或 Android 平台功能测试验证）