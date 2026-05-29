# Windows Movie Player

> Windows Specific Movie Player using Media Foundation（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Windows视频播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WindowsMoviePlayer` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 12 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WindowsMoviePlayer) | |

## 用途

该插件为 Windows 平台提供了基于 Microsoft Media Foundation 的视频播放能力。它主要用于在引擎启动早期（PreLoadingScreen阶段）播放启动视频、Logo动画或加载画面，其核心功能是将视频文件解码为纹理，并通过引擎的Slate视口系统进行渲染显示，同时支持音频播放。这是一个平台特定的底层媒体播放器实现。

## 使用场景

- 你的游戏需要在 Windows 平台启动时显示一个自定义的加载动画或制作商Logo。
- 你需要一个轻量级、在引擎初始化早期阶段就能工作的视频播放器来播放“开机动画”。

## 蓝图用法

经过源码分析，此插件主要提供内部C++实现，**没有直接暴露** `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)` 给蓝图使用。其核心类 `FMediaFoundationMovieStreamer` 是一个实现了 `IMovieStreamer` 接口的C++类，通过引擎的全局 `MoviePlayer` 子系统进行注册和调用。

**间接蓝图控制**：你可以通过 `UGameplayStatics` 或蓝图中的 `Get Movie Player` 节点获取 `UMoviePlayer` 对象，然后调用其蓝图接口函数（如 `Play Movie`）来触发由本插件实现的播放流程。

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Get Movie Player` 节点获取 `Movie Player` 子系统对象。
2.  调用 `Play Movie` 节点，并传入视频文件的路径（例如，指向你的项目的 `/Content/Movies/` 目录下的 .wmv 或 .mp4 文件）。
3.  引擎将自动调用已注册的 `FMediaFoundationMovieStreamer` 来处理该视频的播放、渲染和音频。

## C++ 用法

核心用法是创建并注册一个 `FMediaFoundationMovieStreamer` 实例到全局电影播放器。

### 头文件引入

```cpp
#include "WindowsMoviePlayer.h"
```

### 基本用法

```cpp
// 示例：在游戏模块或合适的初始化点，向全局电影播放器注册Windows流媒体器
#include "MoviePlayer.h"
#include "WindowsMoviePlayer.h"

// 假设在某个初始化函数中
void InitializeMoviePlayer()
{
    // 获取全局电影播放器
    IMoviePlayer* MoviePlayer = IMoviePlayer::Get();
    if (MoviePlayer)
    {
        // 创建Windows平台特定的流媒体器实例
        TSharedRef<FMediaFoundationMovieStreamer> Streamer = MakeShareable(new FMediaFoundationMovieStreamer());
        // 将其注册为电影播放器的流媒体提供器
        MoviePlayer->SetStreamer(Streamer);
    }
}
```
*（代码逻辑基于 `WindowsMoviePlayer.h` 和 `WindowsMovieStreamer.h` 中的类定义推断）*

### 进阶用法

监听视频播放完成事件，并处理播放错误。
```cpp
// 注册流媒体器时，绑定其播放完成委托
TSharedRef<FMediaFoundationMovieStreamer> Streamer = MakeShareable(new FMediaFoundationMovieStreamer());
Streamer->OnCurrentMovieClipFinished().BindLambda([](const FString& MovieName, bool bSuccess)
{
    if (!bSuccess)
    {
        UE_LOG(LogWindowsMoviePlayer, Warning, TEXT("Movie playback failed: %s"), *MovieName);
        // 在这里可以处理播放失败的情况，例如尝试播放备用视频或跳过
    }
    else
    {
        UE_LOG(LogWindowsMoviePlayer, Log, TEXT("Movie finished: %s"), *MovieName);
    }
});

// 然后在电影播放器中使用这个Streamer
IMoviePlayer::Get()->SetStreamer(Streamer);
```
*（代码逻辑基于 `FMediaFoundationMovieStreamer` 的 `OnCurrentMovieClipFinished` 委托定义）*

## Demo 示例

一个最小化的、演示如何创建并使用 `FMediaFoundationMovieStreamer` 的示例。

### WindowsMoviePlayerDemo.h
```cpp
#pragma once
#include "CoreMinimal.h"

class FWindowsMoviePlayerDemo
{
public:
    /** 初始化并准备播放一个示例视频 */
    void InitializeAndPlayDemoMovie(const FString& MoviePath);
};
```

### WindowsMoviePlayerDemo.cpp
```cpp
#include "WindowsMoviePlayerDemo.h"
#include "MoviePlayer.h"
#include "WindowsMoviePlayer.h" // 关键：包含插件提供的头文件
#include "Misc/Paths.h"

void FWindowsMoviePlayerDemo::InitializeAndPlayDemoMovie(const FString& MoviePath)
{
    // 确保路径有效，通常视频应放在项目的 Content/Movies 目录下
    FString FullMoviePath = FPaths::ProjectContentDir() / TEXT("Movies") / MoviePath;

    IMoviePlayer* MoviePlayer = IMoviePlayer::Get();
    if (MoviePlayer && FPaths::FileExists(FullMoviePath))
    {
        // 创建本插件提供的流媒体器
        TSharedRef<FMediaFoundationMovieStreamer> WindowsStreamer = MakeShareable(new FMediaFoundationMovieStreamer());

        // 绑定完成事件（可选）
        WindowsStreamer->OnCurrentMovieClipFinished().BindLambda([](const FString& Name, bool bSuccess)
        {
            UE_LOG(LogTemp, Display, TEXT("Demo movie '%s' finished. Success: %s"), *Name, bSuccess ? TEXT("Yes") : TEXT("No"));
        });

        // 将流媒体器设置给电影播放器
        MoviePlayer->SetStreamer(WindowsStreamer);

        // 准备电影列表并播放
        TArray<FString> MovieQueue;
        MovieQueue.Add(FullMoviePath);

        // 开始播放。bLooping=false 表示播放一次。
        // 注意：实际调用的是MoviePlayer子系统，它会委托给WindowsStreamer。
        MoviePlayer->PlayMovie(false);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MoviePlayer or movie file not found: %s"), *FullMoviePath);
    }
}
```

## 模块依赖

根据 `WindowsMoviePlayer.Build.cs`，使用此插件的功能，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `RenderCore` | 底层渲染核心，用于纹理创建和管理 |
| `RHI` | 渲染硬件接口，用于操作GPU资源（如纹理） |
| `Media` | 引擎媒体框架基础模块 |
| `MediaFoundation` | **核心依赖**。Windows Media Foundation API 的引擎封装，是本插件工作的基础 |
| `Slate` | 用于创建和管理视频渲染的视口 (`SWidget`) |
| `SlateCore` | Slate 基础类型和绘图原语 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新的UE_LOGF格式 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了日志中printf格式说明符的问题 |
| 2025-08-27 | `7766f4c6` | Fixed return value of movie streamers to be the result of the actual open call. | 修复了流媒体器返回值，确保返回实际打开操作的结果 |
| 2025-08-12 | `6214b8aa` | Cleaning up a few movie streamer issues. | 清理了几个与电影流媒体器相关的问题 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 将RHI命令列表传递给MoviePlayer和渲染线程可Tick对象函数 |

### 维护评价

这是一个**创建时间很早（约12年）、功能稳定但非常基础**的插件。
- **维护频率**：近期仍有一些提交，但多为日志、编译兼容性等维护性修复，没有实质性功能更新。
- **活跃度**：属于**维护中**状态，但更新内容表明其设计已非常成熟，主要用于兼容性保障。
- **推荐度**：**推荐使用**。它是UE在Windows平台播放启动视频的官方和默认实现，稳定可靠。如果你需要的是“引擎启动时播放视频”这一标准功能，那么无需额外配置，此插件默认已启用并能满足需求。但如果你需要复杂的媒体播放功能（如流媒体、多音轨、字幕等），应考虑使用 `MediaFrameworkUtilities` 等更新、功能更全的媒体插件。
- **警告**：插件年龄超过10年，但仍有维护。其代码风格和技术实现（如直接使用COM接口）可能较为陈旧，但作为引擎基础组件，其核心功能依然有效。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WindowsMoviePlayer)