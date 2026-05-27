# Media Movie Streamer

> Movie Streamer using MediaFramework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体电影流媒体器 |
| 分类 | Movie Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaMovieStreamer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-12 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaMovieStreamer) | |

## 用途

该插件的核心是实现了一个符合 `IMovieStreamer` 接口的 `FMediaMovieStreamer` 类。它的主要目的是将 Unreal Engine 的 **媒体框架（MediaFramework）** 集成到引擎内置的 **电影序列播放器（Movie Player）** 系统中。

通常，引擎的电影序列播放器用于播放启动加载画面或过场动画，其内容（如 `.bink` 视频）是静态绑定的。此插件改变了这一点，它允许开发者使用 `UMediaPlayer`、`UMediaSource` 等媒体框架的组件来动态地提供和控制这些视频流。这意味着你可以在游戏启动或关卡过渡时，播放通过网络或本地文件加载的视频内容，而不是只能使用引擎内置的单一开机动画。

本质上，它解决的是在引擎关键流程（如加载）中播放**自定义、可编程控制的视频内容**的需求，为更灵活的加载画面和过场动画提供了可能。

## 使用场景

-   你的游戏需要在**启动或关卡加载时**播放一个自定义的宣传视频或剧情动画。
-   你希望利用**媒体框架**的强大功能（如网络流、多种视频格式、硬件加速解码）来播放这些过渡视频。
-   你需要对播放的媒体进行更精细的控制（如暂停、跳转、音量调节），而不仅仅是播放到结束。
-   你正在开发一个需要动态加载和播放视频内容的应用程序，例如数字展厅、媒体播放器等。

## 蓝图用法

此插件的接口主要暴露给 C++，蓝图层面的直接控制非常有限。核心控制逻辑都封装在 C++ 的 `FMediaMovieStreamer` 类中。唯一的蓝图相关功能是 `UMediaMovieAssets` 中用于响应媒体结束事件的 `OnMediaEnd` 回调，但该函数是私有的，无法在蓝图中直接调用。因此，要使用此插件，开发者几乎必须通过 C++ 进行编程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnMediaEnd` (UFUNCTION) | 内部回调，当媒体播放结束时触发。 | `UMediaMovieAssets` (Private) |

## C++ 用法

### 头文件引入

```cpp
#include "MediaMovieStreamerModule.h"
#include "MediaMovieStreamer.h"
```

### 基本用法

基本用法包括获取流媒体器实例，并配置它使用你准备好的媒体组件。你需要手动设置一个外部控制模式，然后配置各个媒体组件。

```cpp
// 来自 MediaMovieStreamerModule.h
// 获取模块和流媒体器的单例
FMediaMovieStreamerModule& Module = FMediaMovieStreamerModule::Get();
const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer = FMediaMovieStreamerModule::GetMovieStreamer();

// 1. 启用外部控制模式（必须调用）
// 设置后，插件将不再自动管理媒体播放，你需要自行控制。
Streamer->SetIsMediaControlledExternally(true);

// 2. 配置媒体组件（需要自行创建并管理这些对象的生命周期）
UMediaPlayer* MyMediaPlayer = ...; // 你的媒体播放器实例
UMediaSource* MyMediaSource = ...; // 你的媒体源
UMediaTexture* MyMediaTexture = ...; // 你的媒体纹理
UMediaSoundComponent* MyMediaSoundComp = ...; // 你的媒体声音组件

Streamer->SetMediaPlayer(MyMediaPlayer);
Streamer->SetMediaSource(MyMediaSource);
Streamer->SetMediaTexture(MyMediaTexture);
Streamer->SetMediaSoundComponent(MyMediaSoundComp);
```

**注意**：在启用外部控制模式后，插件**不会**在播放结束后自动清理上述媒体对象。你需要在适当时机（例如视频播放完毕后）将这些对象的指针设置为 `nullptr`，以释放插件对它们的引用。

### 进阶用法

你可以订阅流媒体器的 Tick 事件，以便在引擎 Tick 的特定阶段注入自定义逻辑，这对于同步其他游戏元素（如 UI）非常有用。

```cpp
// 来自 MediaMovieStreamer.h
// 订阅引擎 Tick 之后的事件
Streamer->MovieStreamerPostEngineTick.AddLambda([this]()
{
    // 在这里处理引擎主 Tick 之后需要执行的逻辑
    // 例如，更新与视频同步的UI
});

// 如果你需要手动控制媒体结束（例如，用户按下了跳过按钮）
// 调用 OnMediaEnd 会触发 IMovieStreamer 接口完成的流程
Streamer->OnMediaEnd();
```

## Demo 示例

这是一个展示如何初始化并启动 `MediaMovieStreamer` 播放视频的最小示例。

```cpp
// MyMovieStreamerSetup.h
#pragma once

#include "CoreMinimal.h"

class UMediaPlayer;
class UMediaSource;
class UMediaTexture;
class UMediaSoundComponent;
class FMediaMovieStreamer;

class FMyMovieStreamerSetup
{
public:
    void StartMovie(const FString& MediaSourceUrl);
    void StopMovie();

private:
    // 保持对媒体对象的强引用，防止被垃圾回收
    UPROPERTY()
    TObjectPtr<UMediaPlayer> MediaPlayer;
    UPROPERTY()
    TObjectPtr<UMediaSource> MediaSource;
    UPROPERTY()
    TObjectPtr<UMediaTexture> MediaTexture;
    UPROPERTY()
    TObjectPtr<UMediaSoundComponent> MediaSoundComponent;

    // 流媒体器共享指针
    TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> MovieStreamer;

    void OnMediaEndCallback();
};
```

```cpp
// MyMovieStreamerSetup.cpp
#include "MyMovieStreamerSetup.h"
#include "MediaMovieStreamerModule.h"
#include "MediaMovieStreamer.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"
#include "UObject/SoftObjectPath.h"

void FMyMovieStreamerSetup::StartMovie(const FString& MediaSourceUrl)
{
    // 1. 创建媒体组件
    MediaPlayer = NewObject<UMediaPlayer>();
    MediaSource = NewObject<UMediaSource>();
    MediaTexture = NewObject<UMediaTexture>();
    MediaSoundComponent = NewObject<UMediaSoundComponent>();

    // 2. 配置媒体源路径
    FSoftObjectPath MediaPath(MediaSourceUrl);
    MediaSource->SetMediaSourcePath(MediaPath);

    // 3. 获取并配置流媒体器
    MovieStreamer = FMediaMovieStreamerModule::GetMovieStreamer();
    if (MovieStreamer.IsValid())
    {
        // 启用外部控制模式
        MovieStreamer->SetIsMediaControlledExternally(true);

        // 设置各个组件
        MovieStreamer->SetMediaPlayer(MediaPlayer);
        MovieStreamer->SetMediaSource(MediaSource);
        MovieStreamer->SetMediaTexture(MediaTexture);
        MovieStreamer->SetMediaSoundComponent(MediaSoundComponent);

        // 开始播放媒体
        // 注意：具体的播放控制（如 Play）需要在配置完成后由外部逻辑触发
        // 例如： MediaPlayer->OpenSource(MediaSource);
    }
}

void FMyMovieStreamerSetup::StopMovie()
{
    if (MovieStreamer.IsValid())
    {
        // 清理插件持有的引用
        MovieStreamer->SetMediaPlayer(nullptr);
        MovieStreamer->SetMediaSource(nullptr);
        MovieStreamer->SetMediaTexture(nullptr);
        MovieStreamer->SetMediaSoundComponent(nullptr);
        MovieStreamer.Reset();
    }

    // 此处可以添加销毁 MediaPlayer, MediaSource 等 UObject 的逻辑
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `Media` | 媒体框架核心，提供 `UMediaPlayer`, `UMediaSource`, `IMediaModule` 等基础功能。 |
| `MoviePlayer` | 引擎的电影播放器框架，提供 `IMovieStreamer` 接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎级代码规范修复，将析构函数改为 `= default`。 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 将 RHI 命令列表传递给电影播放器相关函数，为底层渲染命令准备。 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 调整导出符号（DLL linkage），属于构建配置更新。 |

### 维护评价

**维护中**。该插件自2021年创建以来，虽然功能没有显著变化，但最近一次更新在2025年10月，表明它仍被包含在引擎的维护和构建流程中。近期更新主要是与引擎底层代码规范、渲染线程和构建系统相关的维护性改动，并未添加新功能或进行重大重构。

**重要提醒**：该插件的 `.uplugin` 文件中 `IsBetaVersion: true` 且 `EnabledByDefault: false`。这表明它仍处于**实验性**阶段，Epic 官方可能未将其视为稳定或完整功能。在生产项目中使用前，请务必进行充分的测试，了解其潜在的限制和不稳定性。

**推荐**：对于需要高度定制加载画面或过场动画，并希望深度集成媒体框架的项目，此插件是一个有价值的参考和起点。但应做好应对 API 变化和潜在问题的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaMovieStreamer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview) (Media Framework 概述)