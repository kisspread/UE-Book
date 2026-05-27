# Media Movie Streamer

> Movie Streamer using MediaFramework.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体影片流播放器 |
| 分类 | Movie Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MediaMovieStreamer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-05-12 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaMovieStreamer) | |

## 用途

MediaMovieStreamer 插件提供了一个基于 UE Media Framework 的影片流播放器实现，用于替换默认的 Bink 视频播放方案。它实现了 `IMovieStreamer` 接口，使得开发者可以使用 `UMediaPlayer`、`UMediaSource`、`UMediaTexture` 等 Media Framework 组件来播放关卡加载画面（Loading Screen）期间的影片。

与传统的 Bink 影片播放器不同，该插件利用 Media Framework 的灵活性，支持更广泛的视频格式和自定义媒体播放控制。插件还提供了外部控制模式，允许开发者接管媒体播放的生命周期，实现更精细的控制。

## 使用场景

- 你希望在关卡加载时播放自定义格式的视频（非 Bink） → 使用此插件替代默认 MoviePlayer
- 你需要在加载画面期间播放 Media Framework 支持的流媒体内容 → 使用此插件
- 你需要外部精确控制加载画面视频的播放时机和生命周期 → 调用 `SetIsMediaControlledExternally(true)`

## 蓝图用法

该插件主要为 C++ Runtime 模块，不暴露蓝图节点。影片流播放器的配置通常在引擎层面通过 `MoviePlayer` 子系统完成。

## C++ 用法

### 头文件引入

```cpp
#include "MediaMovieStreamerModule.h"
#include "MediaMovieStreamer.h"
```

### 基本用法

获取 MovieStreamer 实例并配置媒体资源：

```cpp
// 来源: Source/MediaMovieStreamer/Public/MediaMovieStreamerModule.h

// 获取全局 MovieStreamer 实例
const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer = 
    FMediaMovieStreamerModule::GetMovieStreamer();

if (Streamer.IsValid())
{
    // 设置要播放的媒体源
    Streamer->SetMediaPlayer(MyMediaPlayer);
    Streamer->SetMediaSource(MyMediaSource);
    Streamer->SetMediaTexture(MyMediaTexture);
    Streamer->SetMediaSoundComponent(MyMediaSoundComponent);
}
```

### 外部控制模式

当你需要自己控制媒体播放生命周期时：

```cpp
// 来源: Source/MediaMovieStreamer/Public/MediaMovieStreamer.h

const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer = 
    FMediaMovieStreamerModule::GetMovieStreamer();

// 启用外部控制 —— MovieStreamer 不会自动播放或清理资源
Streamer->SetIsMediaControlledExternally(true);

// 手动设置媒体资源
Streamer->SetMediaPlayer(MyMediaPlayer);
Streamer->SetMediaSource(MyMediaSource);
Streamer->SetMediaTexture(MyMediaTexture);
Streamer->SetMediaSoundComponent(MyMediaSoundComponent);

// ... 媒体播放完成后，手动清理（传入 nullptr）
Streamer->SetMediaPlayer(nullptr);
Streamer->SetMediaSoundComponent(nullptr);
Streamer->SetMediaSource(nullptr);
Streamer->SetMediaTexture(nullptr);
```

### 监听外部 Tick 事件

```cpp
// 来源: Source/MediaMovieStreamer/Public/MediaMovieStreamer.h

const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer = 
    FMediaMovieStreamerModule::GetMovieStreamer();

// 绑定引擎 Tick 前后和渲染后的回调
Streamer->MovieStreamerPreEngineTick.AddLambda([]()
{
    // 引擎 Tick 前执行
});
Streamer->MovieStreamerPostEngineTick.AddLambda([]()
{
    // 引擎 Tick 后执行
});
Streamer->MovieStreamerPostRenderTick.AddLambda([]()
{
    // 渲染 Tick 后执行
});
```

## Demo 示例

### 头文件

```cpp
// MyMediaMovieExample.h
#pragma once

#include "CoreMinimal.h"

class UMediaPlayer;
class UMediaSource;
class UMediaTexture;
class UMediaSoundComponent;

class FMyMediaMovieExample
{
public:
    void SetupAndPlayMovie();
    void StopAndCleanup();

private:
    UMediaPlayer* CachedMediaPlayer = nullptr;
    UMediaSource* CachedMediaSource = nullptr;
    UMediaTexture* CachedMediaTexture = nullptr;
    UMediaSoundComponent* CachedSoundComponent = nullptr;
};
```

### 实现文件

```cpp
// MyMediaMovieExample.cpp
#include "MyMediaMovieExample.h"
#include "MediaMovieStreamerModule.h"
#include "MediaMovieStreamer.h"
#include "MediaPlayer.h"
#include "MediaSource.h"
#include "MediaTexture.h"
#include "MediaSoundComponent.h"

void FMyMediaMovieExample::SetupAndPlayMovie()
{
    const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer =
        FMediaMovieStreamerModule::GetMovieStreamer();
    
    if (!Streamer.IsValid())
    {
        UE_LOG(LogMediaMovieStreamer, Error, TEXT("MovieStreamer is not available"));
        return;
    }

    // 启用外部控制模式，接管媒体播放生命周期
    Streamer->SetIsMediaControlledExternally(true);

    // 配置媒体资源
    Streamer->SetMediaPlayer(CachedMediaPlayer);
    Streamer->SetMediaSource(CachedMediaSource);
    Streamer->SetMediaTexture(CachedMediaTexture);
    Streamer->SetMediaSoundComponent(CachedSoundComponent);
}

void FMyMediaMovieExample::StopAndCleanup()
{
    const TSharedPtr<FMediaMovieStreamer, ESPMode::ThreadSafe> Streamer =
        FMediaMovieStreamerModule::GetMovieStreamer();

    if (Streamer.IsValid())
    {
        // 传入 nullptr 释放引用，允许垃圾回收
        Streamer->SetMediaPlayer(nullptr);
        Streamer->SetMediaSource(nullptr);
        Streamer->SetMediaTexture(nullptr);
        Streamer->SetMediaSoundComponent(nullptr);
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

该模块在 Build.cs 中依赖 MediaFramework 相关模块（`MediaAssets`、`MediaUtils` 等），但这些属于 UE 标准媒体模块，使用者无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码规范化，析构函数改用 `= default` |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | RHI 命令列表透传至 MoviePlayer 接口 |
| 2025-04-23 | `939cc6e5` | Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticv | 为所有方法添加 DLL 导出标记 |
| 2024-11-10 | `66e9bb39` | Removed all #if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2 scopes from the code base | 清理废弃的头文件包含宏 |
| 2024-02-22 | `01203093` | Deprecate: | 废弃标记相关改动 |

### 维护评价

该插件自 2021 年创建以来，标记为 **Beta** 且 **默认未启用**。近期的更新均为全局性代码维护（代码规范化、API 签名变更、头文件清理），没有任何功能性更新。4 年来始终停留在 Beta 状态，说明该功能可能从未达到生产就绪标准。

**状态**：维护不活跃，功能未完成
**建议**：仅在需要 Media Framework 作为加载画面播放器的特定场景中考虑使用。由于长期处于 Beta 状态且无实质性功能迭代，生产环境中应谨慎使用，建议优先使用默认的 Bink 影片播放器或自定义加载画面方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaMovieStreamer)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [Media Framework 文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)