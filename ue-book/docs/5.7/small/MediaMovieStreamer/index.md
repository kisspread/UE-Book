# Media Movie Streamer

> Movie Streamer using MediaFramework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体电影流播放器 |
| 分类 | Movie Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaMovieStreamer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-13 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaMovieStreamer) | |

## 用途

MediaMovieStreamer 插件利用 MediaFramework 提供一种在关卡加载、切换等阻塞操作期间播放视频（电影）的能力。它实现了一个 `IMovieStreamer`，与 UE 的 `MoviePlayer` 系统集成，可以在加载屏幕或过渡场景中显示媒体内容（如视频）。该插件允许外部控制媒体播放，开发者可以手动管理媒体源、播放器、音效组件和纹理，而不是让插件自动创建和管理。这为需要自定义视频播放流程的项目（如游戏内的过场动画、动态加载界面）提供了灵活性。

## 使用场景

- 你在制作一个包含大量加载场景的开放世界游戏，希望在加载界面播放动态视频而非静态图片。
- 你需要精确控制视频播放的开始、暂停、结束时机，比如在特定逻辑完成后关闭加载画面。
- 你想在游戏内播放实时流媒体或视频文件，并与游戏逻辑（如跳过、回调）紧密结合。

## 蓝图用法

该插件主要面向 C++ 开发者，未暴露直接的蓝图可调用函数。所有核心操作均通过 `FMediaMovieStreamer` 类在 C++ 中完成。若希望从蓝图控制播放，需要编写 C++ 接口或使用 MediaFramework 原生的蓝图节点（如 `MediaPlayer`、`MediaSource` 等），再通过 C++ 桥接传递到插件。

**无原生蓝图节点**。

## C++ 用法

### 头文件引入

```cpp
#include "MediaMovieStreamerModule.h"
#include "MediaMovieStreamer.h"
```

### 基本用法

在模块启动时获取电影流播放器实例，配置媒体资产并启动播放。

```cpp
// Source: Engine/Plugins/Media/MediaMovieStreamer/Private/MediaMovieStreamer.cpp

// 获取模块的单例流播放器
TSharedPtr<FMediaMovieStreamer> MovieStreamer = FMediaMovieStreamerModule::GetMovieStreamer();

// 创建媒体资产
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaSource* MediaSource = LoadObject<UMediaSource>(nullptr, TEXT("/Game/Videos/MyVideo.uasset"));
UMediaTexture* MediaTexture = NewObject<UMediaTexture>();
UMediaSoundComponent* MediaSoundComponent = NewObject<UMediaSoundComponent>();

// 配置播放器
MovieStreamer->SetMediaPlayer(MediaPlayer);
MovieStreamer->SetMediaSource(MediaSource);
MovieStreamer->SetMediaTexture(MediaTexture);
MovieStreamer->SetMediaSoundComponent(MediaSoundComponent);

// 开始播放（插件自动处理）
// 当关卡加载完成后，媒体播放会自动结束或由外部控制
```

### 进阶用法：外部控制模式

如果希望完全手动控制媒体生命周期，调用 `SetIsMediaControlledExternally(true)`。在此模式下，插件不会自动清理媒体对象，你在结束后必须手动释放。

```cpp
// 设置外部控制
MovieStreamer->SetIsMediaControlledExternally(true);

// 手动播放媒体
MediaPlayer->OpenSource(MediaSource);

// 监听媒体结束事件（通过 UMediaMovieAssets 的回调）
UMediaMovieAssets* Assets = FMediaMovieStreamerModule::GetMovieAssets();
Assets->OnMediaEnded.AddLambda([&]()
{
    // 执行结束逻辑，然后清理
    MovieStreamer->SetMediaPlayer(nullptr);
    MovieStreamer->SetMediaSource(nullptr);
    MovieStreamer->SetMediaTexture(nullptr);
    MovieStreamer->SetMediaSoundComponent(nullptr);
});
```

### 使用事件 Tick

电影流播放器暴露了三个事件委托，可在不同时机插入自定义逻辑：

- `MovieStreamerPostEngineTick` – 引擎 Tick 后
- `MovieStreamerPreEngineTick` – 引擎 Tick 前
- `MovieStreamerPostRenderTick` – 渲染后

```cpp
MovieStreamer->MovieStreamerPreEngineTick.AddLambda([]()
{
    // 在每帧渲染前更新某些状态
});
```

## Demo 示例

以下是一个最小可编译示例，展示如何在自定义 `IGameInstance` 类中使用 MediaMovieStreamer 播放加载视频。假设你已经正确启用了插件并配置了媒体资源。

**DemoGameInstance.h**

```cpp
#pragma once

#include "Engine/GameInstance.h"
#include "DemoGameInstance.generated.h"

class UMediaPlayer;
class UMediaSource;
class UMediaTexture;
class UMediaSoundComponent;

UCLASS()
class MYGAME_API UDemoGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void Shutdown() override;

    void StartLoadingMovie();
    void StopLoadingMovie();

private:
    UPROPERTY()
    UMediaPlayer* MediaPlayer;

    UPROPERTY()
    UMediaSource* MediaSource;

    UPROPERTY()
    UMediaTexture* MediaTexture;

    UPROPERTY()
    UMediaSoundComponent* MediaSoundComponent;
};
```

**DemoGameInstance.cpp**

```cpp
#include "DemoGameInstance.h"
#include "MediaMovieStreamerModule.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"

void UDemoGameInstance::Init()
{
    Super::Init();
    // 插件模块已在启动时自行加载，我们直接获取流播放器
}

void UDemoGameInstance::StartLoadingMovie()
{
    // 获取电影流播放器
    TSharedPtr<FMediaMovieStreamer> MovieStreamer = FMediaMovieStreamerModule::GetMovieStreamer();
    if (!MovieStreamer.IsValid())
    {
        return;
    }

    // 创建媒体资产
    MediaPlayer = NewObject<UMediaPlayer>(this);
    MediaSource = LoadObject<UMediaSource>(nullptr, TEXT("/Game/Videos/LoadingScreen.LoadingScreen"));
    MediaTexture = NewObject<UMediaTexture>(this);
    MediaSoundComponent = NewObject<UMediaSoundComponent>(this);

    check(MediaSource && MediaPlayer && MediaTexture && MediaSoundComponent);

    // 配置流播放器
    MovieStreamer->SetMediaPlayer(MediaPlayer);
    MovieStreamer->SetMediaSource(MediaSource);
    MovieStreamer->SetMediaTexture(MediaTexture);
    MovieStreamer->SetMediaSoundComponent(MediaSoundComponent);

    // 可选：设置外部控制模式，以便在加载结束后手动停止
    MovieStreamer->SetIsMediaControlledExternally(true);

    // 手动打开媒体源开始播放
    MediaPlayer->OpenSource(MediaSource);
}

void UDemoGameInstance::StopLoadingMovie()
{
    TSharedPtr<FMediaMovieStreamer> MovieStreamer = FMediaMovieStreamerModule::GetMovieStreamer();
    if (!MovieStreamer.IsValid())
    {
        return;
    }

    // 停止播放并清理引用
    if (MediaPlayer)
    {
        MediaPlayer->Close();
    }

    MovieStreamer->SetMediaPlayer(nullptr);
    MovieStreamer->SetMediaSource(nullptr);
    MovieStreamer->SetMediaTexture(nullptr);
    MovieStreamer->SetMediaSoundComponent(nullptr);

    // 销毁资产（可选，GameInstance 销毁时会自动处理）
    MediaPlayer = nullptr;
    MediaSource = nullptr;
    MediaTexture = nullptr;
    MediaSoundComponent = nullptr;
}

void UDemoGameInstance::Shutdown()
{
    StopLoadingMovie();
    Super::Shutdown();
}
```

## 模块依赖

该插件依赖以下模块（仅列出独特依赖）：

| 模块 | 用途 |
|---|---|
| `Media` | 核心媒体框架，提供播放器、源、纹理等基础类 |
| `MediaUtils` | 媒体实用工具，如同步、时间源等 |
| `MediaAssets` | 媒体资产（`UMediaPlayer`, `UMediaTexture` 等） |
| `MoviePlayer` | 电影播放器系统，`FMediaMovieStreamer` 实现其接口 |

其他常见依赖（Core、CoreUObject、Engine、RHI、SlateCore 等）已省略。

## 维护状态

### 近期更新

- 2025-08-08 `40e2c8da` 将 RHI 命令列表传递给 MoviePlayer 和 TickableObjectRenderThread 相关函数
- 2025-04-23 `939cc6e5` 使用 FortniteClient 构建目标查找并转换所有文件以添加 dllstorage 方法/静态变量
- 2024-11-10 `66e9bb39` 移除代码库中所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 作用域
- 2024-02-22 `01203093` 弃用（部分 API 标记为弃用）
- 2023-06-13 `a9a5fa39` 弃用 `InitResource` 和 `UpdateResource` 的非命令列表变体；修补引擎以传递命令列表

### 维护评价

- **创建时间**：2023-06-13，约 2.4 年
- **更新频率**：过去一年有多次实质性更新（RHI 命令列表、构建目标转换），最近一次为 2025-08-08，说明仍在活跃维护。
- **已知问题**：当前为 Beta 版本，可能缺少完善文档或蓝图支持；`SetIsMediaControlledExternally` 模式需要开发者谨慎管理生命周期。
- **推荐使用**：适合需要自定义视频播放用于加载界面的项目；但由于是实验性插件，建议在生产环境前充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaMovieStreamer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaMovieStreamer/Private)