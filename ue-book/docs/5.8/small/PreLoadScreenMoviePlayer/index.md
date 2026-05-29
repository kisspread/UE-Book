# Pre-Load Screen Movie Player

> Handles a default implementation of using a Pre-Load screen to display an engine loading movie.

| 属性 | 值 |
|---|---|
| 中文名 | 预加载屏幕电影播放器 |
| 分类 | PreLoadScreenMoviePlayer |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `PreLoadScreenMoviePlayer` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2018-09-25 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PreLoadScreenMoviePlayer) | |

## 用途

该插件为引擎启动过程中的预加载屏幕提供了一个默认的电影播放实现。它解决的核心问题是：在引擎初始化（如资产加载）期间，向用户展示一个可自定义的、动态的（通常是视频）启动画面，而非静态图片或黑屏。它主要用于移动平台（Android， iOS）和 Windows，为游戏提供品牌展示或过渡体验。需要注意的是，此插件**默认不启用**，需要项目手动激活。

## 使用场景

- **移动游戏快速启动**：在 Android/iOS 游戏启动时，播放一段简短的品牌视频或游戏宣传片，提升玩家初始体验。
- **特定于加载的视觉反馈**：需要比静态图片更吸引人的加载画面，例如播放循环动画或视频。
- **复杂的加载流程控制**：通过 `FPreLoadMovieAttributes` 配置播放列表、循环模式、最短显示时间等，实现更精细的加载流程控制。
- **需要默认预加载电影功能的项目**：项目不想从零实现 `IPreLoadScreen` 的电影播放逻辑，可以直接使用此插件提供的基础实现。

## 蓝图用法

该插件主要通过 C++ 模块和类接口工作，在提供的公共头文件中未发现 `BlueprintCallable` 或 `BlueprintReadWrite` 的函数/属性。其配置（如电影路径）通常通过配置文件或 C++ 代码设置，而非直接在蓝图中暴露节点。

## C++ 用法

### 头文件引入

```cpp
#include "PreLoadMoviePlayerModule.h"
#include "PreLoadMoviePlayerScreenBase.h"
#include "MoviePlayerAttributes.h"
```

### 基本用法

此插件的核心是模块接口和电影播放屏幕基类。以下代码演示了如何在你的游戏模块中与这个预加载电影播放器交互。

```cpp
// 你的游戏模块实现（例如 MyGameModule.cpp）
#include "PreLoadMoviePlayerModule.h"
#include "PreLoadMoviePlayerScreenBase.h"
#include "MoviePlayerAttributes.h"

class FMyGameModule : public FDefaultGameModuleImpl
{
    virtual void StartupModule() override
    {
        // 检查预加载电影播放器模块是否可用
        if (IPreLoadMoviePlayerScreenModule::IsAvailable())
        {
            IPreLoadMoviePlayerScreenModule& MovieModule = IPreLoadMoviePlayerScreenModule::Get();
            
            // 获取模块创建的默认电影播放屏幕实例
            // （该实例在 PreLoadMoviePlayerScreenModuleBase::StartupModule 中创建）
            // 你可以通过模块接口配置或注册自定义的电影流。
            // 具体注册逻辑需要查看 PreLoadMoviePlayerScreenModuleBase 的实现。
        }
    }
};
```

**配置电影属性 (FPreLoadMovieAttributes)**
电影播放的行为由 `FPreLoadMovieAttributes` 结构体控制，通常通过 `InitSettingsFromConfig` 从配置文件加载或在代码中直接设置。

```cpp
// 假设你有一个 FPreLoadMoviePlayerScreenBase 的实例或子类
FPreLoadMoviePlayerScreenBase* MyMovieScreen = /* ... */;

// 方法1：从配置文件初始化（常见方式）
// MyMovieScreen->InitSettingsFromConfig(TEXT("DefaultGame"));

// 方法2：直接设置属性
FPreLoadMovieAttributes Attrs;
Attrs.MoviePaths = {TEXT("MyBrandVideo"), TEXT("LoadingLoop")};
Attrs.PlaybackType = EMovieScreenPlaybackType::MT_MS_LoadingLoop; // 最后一个视频循环
Attrs.MinimumLoadingScreenDisplayTime = 2.0f; // 至少显示2秒
Attrs.bMoviesAreSkippable = true; // 加载完成后允许跳过
Attrs.bAutoCompleteWhenLoadingCompletes = true; // 加载完成后自动结束
MyMovieScreen->SetMovieAttributes(Attrs);
```

### 进阶用法

继承 `FPreLoadMoviePlayerScreenBase` 来完全自定义预加载电影屏幕的渲染和行为。

```cpp
// MyCustomMovieScreen.h
#pragma once
#include "PreLoadMoviePlayerScreenBase.h"

class FMyCustomMovieScreen : public FPreLoadMoviePlayerScreenBase
{
public:
    // 重写 IsDone 以实现自定义完成逻辑
    virtual bool IsDone() const override
    {
        // 例如：除了电影播放完，还要求用户点击
        return FPreLoadMoviePlayerScreenBase::IsDone() && bUserClicked;
    }

    // 重写鼠标点击处理
    virtual FReply OnLoadingScreenMouseButtonDown(const FGeometry& Geometry, const FPointerEvent& PointerEvent) override
    {
        if (IsMovieStreamingFinished() || MovieAttributes.bMoviesAreSkippable)
        {
            bUserClicked = true;
            return FReply::Handled();
        }
        return FReply::Unhandled();
    }

private:
    bool bUserClicked = false;
};
```

## Demo 示例

以下是一个最小化的、可运行的 C++ 模块示例，演示如何创建并激活一个使用此插件的预加载电影屏幕。

**MyPreLoadScreenModule.h**
```cpp
#pragma once
#include "Modules/ModuleManager.h"
#include "PreLoadMoviePlayerScreenBase.h"

class FMyPreLoadScreenModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<FPreLoadMoviePlayerScreenBase> PreLoadScreen;
};
```

**MyPreLoadScreenModule.cpp**
```cpp
#include "MyPreLoadScreenModule.h"
#include "PreLoadMoviePlayerModule.h" // 依赖 PreLoadScreenMoviePlayer 插件

#define LOCTEXT_NAMESPACE "FMyPreLoadScreenModule"

void FMyPreLoadScreenModule::StartupModule()
{
    // 确保依赖的预加载电影播放器模块已加载
    if (IPreLoadMoviePlayerScreenModule::IsAvailable())
    {
        // 获取电影播放器模块创建的基础屏幕
        // 注意：实际获取方式取决于 IPreLoadMoviePlayerScreenModule 的实现。
        // 此处假设我们使用插件默认创建的那个。
        IPreLoadMoviePlayerScreenModule& MovieModule = IPreLoadMoviePlayerScreenModule::Get();
        // ... 通常模块内部会持有并管理一个 FPreLoadMoviePlayerScreenBase 实例。
        // 为了演示，我们假设可以直接使用它。
        
        // 更常见的做法是，你通过 IPreLoadScreenManager 注册一个自定义的 FPreLoadScreenBase 子类。
        // 例如：
        // PreLoadScreen = MakeShared<FMyCustomMovieScreen>();
        // IPreLoadScreenManager::Get().RegisterPreLoadScreen(PreLoadScreen);
        
        UE_LOG(LogTemp, Log, TEXT("PreLoadScreenMoviePlayer module integration ready."));
    }
}

void FMyPreLoadScreenModule::ShutdownModule()
{
    PreLoadScreen.Reset();
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FMyPreLoadScreenModule, MyPreLoadScreen);
```

**配置 (DefaultGame.ini 示例)**
```ini
[/Script/PreLoadScreenMoviePlayer.PreLoadMoviePlayerScreenBase]
+MoviePaths="StartupMovie"
MinimumLoadingScreenDisplayTime=3.0
bMoviesAreSkippable=true
PlaybackType=1
```

## 模块依赖

要使用此插件的功能，你的模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `PreLoadScreenMoviePlayer` | 核心插件模块，提供电影播放屏幕基类和模块接口。 |
| `MoviePlayer` | 引擎的电影播放器模块，提供 `IMovieStreamer` 等核心接口。 |
| `CoreMedia` | 平台相关的媒体框架，用于解码和播放视频。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版UE_LOG迁移到新的UE_LOGF格式。 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | 优化渲染线程，将 RHI 命令列表传递给电影播放器和可 Tick 的渲染线程对象。 |
| 2025-06-10 | `285e8eda` | With Pre-Load Movie Player plugin active, the Preload movie would play on startup but then the Defau... | 修复了在预加载电影播放器插件激活时，启动电影播放后默认加载屏幕会再次出现的 Bug。 |
| 2025-04-16 | `7b99f63d` | UE-248290 - Ensuring skipping logic is respected in PreLoadScreenMoviePlayer plugin, matching the lo... | 修复了跳过逻辑，使其行为与默认加载屏幕匹配（UE-248290）。 |
| 2025-04-11 | `c7b99e9b` | Fixed Preload Movies not playing if Pre-Load Screen Movie Player plugin is enabled. | 修复了当插件启用时，预加载电影不播放的关键问题。 |

### 维护评价

该插件创建于 2018 年，是一个老古董级插件。从提交记录看，它在 2025 年有过一波针对移动平台加载流程的 Bug 修复（特别是跳过逻辑和电影不播放的问题），随后在 2025 年底和 2026 年初主要进行了一些引擎内部的重构（如日志宏迁移和 RHI 命令列表优化），这表明它仍在随引擎主线维护，但**功能性更新已很少**。

**推荐**：如果你需要在 Android/iOS 上实现带视频的启动加载画面，并且不想完全从零开始，可以考虑启用此插件并继承其基类。但需要注意，它默认不启用，且配置相对底层。对于更简单的需求，引擎自带的 `StartupLoadingScreen` 模块或 `DefaultPreLoadScreen` 可能更合适。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/PreLoadScreenMoviePlayer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/PreLoadScreenMoviePlayer)