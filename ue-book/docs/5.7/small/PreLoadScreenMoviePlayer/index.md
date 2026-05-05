# Pre-Load Screen Movie Player

> Handles a default implementation of using a Pre-Load screen to display an engine loading movie.

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | false |
| 包含内容 | true |
| 模块 | PreLoadScreenMoviePlayer (RuntimeNoCommandlet, PreEarlyLoadingScreen) |
| 支持平台 | Android, IOS, Win64 |
| 创建时间 | 2018-09-25 |
| 年龄标签 | 👴 老古董(>5年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PreLoadScreenMoviePlayer) | |

## 用途

这个 plugin 是 UE5 引擎启动阶段「加载画面播放视频」功能的默认实现。它在引擎最早期的加载阶段（`PreEarlyLoadingScreen`）就被加载，负责将 `MoviePlayer` 模块的视频流渲染能力与 `PreLoadScreen` 模块的加载画面管理框架连接起来。

核心工作流程：

1. **模块启动时**，创建一个 `FPreLoadMoviePlayerScreenBase` 实例并注册到 `FPreLoadScreenManager`
2. **监听视频流注册**，通过 `FCoreDelegates::RegisterMovieStreamerDelegate` 接收引擎提供的视频流播放器
3. **读取配置**，从 `Game.ini` 的 `/Script/MoviePlayer.MoviePlayerSettings` 段读取启动视频列表和播放参数
4. **渲染视频**，创建 Slate Viewport 将视频流画面显示在加载屏幕上
5. **处理完成逻辑**，根据配置决定何时结束加载画面（视频播完 / 加载完成 / 用户跳过 / 最低显示时间）

简单来说：引擎启动时你看到的那个播放视频的加载画面，就是这个 plugin 在工作。

## 使用场景

- 你想在引擎启动时播放一段品牌视频 / loading 动画 → 启用此 plugin
- 你需要自定义加载画面的行为（跳过、循环、最低显示时间等） → 通过 `DefaultGame.ini` 配置
- 你在做移动端游戏，需要在引擎加载期间展示 splash 视频 → 此 plugin 支持 Android / iOS
- 你想自己实现完全自定义的加载画面 → 不用这个 plugin，直接基于 `PreLoadScreen` 模块开发

## 配置用法

本 plugin 没有暴露任何 Blueprint 节点，所有配置通过 `DefaultGame.ini` 完成。

### 基本配置

在项目的 `Config/DefaultGame.ini` 中添加：

```ini
[/Script/MoviePlayer.MoviePlayerSettings]
; 启动时播放的视频文件名（放在 Content/Movies/ 目录下，不含扩展名）
+StartupMovies=MyStartupMovie
+StartupMovies=MySecondMovie
; 视频是否可以被点击/按键跳过
bMoviesAreSkippable=true
; 是否等待视频播放完毕再继续加载（false = 加载完成就立即关闭）
bWaitForMoviesToComplete=false
```

### 播放模式

播放模式通过代码中的 `FPreLoadMovieAttributes::PlaybackType` 控制：

| 模式 | 枚举值 | 说明 |
|---|---|---|
| 普通播放 | `MT_MS_Normal` | 按顺序播放每个视频一次 |
| 循环播放 | `MT_MS_Looped` | 播放完所有视频后从头循环，直到手动取消 |
| 末尾循环 | `MT_MS_LoadingLoop` | 播放完所有视频后循环最后一个，直到加载完成 |

### 注意事项

- 视频文件放在项目的 `Content/Movies/` 目录下
- 如果没有配置任何 `StartupMovies`，默认会尝试播放 `Default_Startup`
- 插件会验证视频文件是否存在，不存在的文件会被跳过
- `MinimumLoadingScreenDisplayTime` 可通过代码设置最低显示时间（默认 -1.0f，即不限制）

## C++ 用法

### 头文件引入

```cpp
#include "PreLoadMoviePlayerModule.h"        // 模块接口
#include "PreLoadMoviePlayerScreenBase.h"    // 加载屏幕实现
#include "MoviePlayerAttributes.h"           // 播放属性结构体
```

### 核心类关系

```
IModuleInterface
  └── IPreLoadMoviePlayerScreenModule     ← 模块接口（PreLoadMoviePlayerModule.h）
        └── FPreLoadMoviePlayerScreenModuleBase  ← 模块实现（PreLoadMoviePlayerModuleBase.h）

FPreLoadScreenBase
  └── FPreLoadMoviePlayerScreenBase       ← 加载屏幕实现（PreLoadMoviePlayerScreenBase.h）

FPreLoadMovieAttributes                   ← 播放属性配置（MoviePlayerAttributes.h）
```

### 自定义 MovieStreamer

如果你想用自己的视频流播放器替换默认实现，可以通过 `FCoreDelegates` 注册：

```cpp
// 创建自定义的 MovieStreamer
TSharedPtr<IMovieStreamer, ESPMode::ThreadSafe> MyStreamer = MakeShared<FMyCustomMovieStreamer>();

// 注册到引擎，PreLoadScreenMoviePlayer 插件会自动接收
FCoreDelegates::RegisterMovieStreamerDelegate.Broadcast(MyStreamer);
```

### 手动控制播放属性

如果需要在代码中动态设置播放参数（而非从 ini 读取），可以继承 `FPreLoadMoviePlayerScreenBase`：

```cpp
class FMyCustomMovieScreen : public FPreLoadMoviePlayerScreenBase
{
public:
    virtual void Init() override
    {
        // 设置自定义属性
        FPreLoadMovieAttributes CustomAttrs;
        CustomAttrs.MoviePaths.Add(TEXT("MyCustomMovie"));
        CustomAttrs.MinimumLoadingScreenDisplayTime = 3.0f;
        CustomAttrs.bMoviesAreSkippable = false;
        CustomAttrs.bAutoCompleteWhenLoadingCompletes = true;
        CustomAttrs.PlaybackType = MT_MS_LoadingLoop;
        SetMovieAttributes(CustomAttrs);

        // 调用父类 Init（会使用已设置的属性而非从 ini 读取）
        // 注意：需要先 RegisterMovieStreamer，否则 Init 会失败
    }

    virtual void InitSettingsFromConfig(const FString& ConfigFileName) override
    {
        // 覆盖配置读取，使用自定义属性
        // 不调用父类实现即可跳过 ini 读取
    }
};
```

## Demo 示例

### 最小配置示例

一个可工作的 PreLoadScreenMoviePlayer 最简配置：

**1. 启用插件** — 在 `DefaultEngine.ini` 中：

```ini
[/Script/Engine.Plugins]
bEnabledByDefault=true
```

或者在 `.uproject` 文件中：

```json
{
    "Plugins": [
        {
            "Name": "PreLoadScreenMoviePlayer",
            "Enabled": true
        }
    ]
}
```

**2. 放置视频文件** — 将 `.mp4` 或 `.bik` 文件放到 `Content/Movies/` 目录。

**3. 配置启动视频** — 在 `DefaultGame.ini` 中：

```ini
[/Script/MoviePlayer.MoviePlayerSettings]
+StartupMovies=MyLoadingVideo
bMoviesAreSkippable=true
bWaitForMoviesToComplete=false
```

**4. 打包运行** — 启动游戏时即可看到加载视频画面。

## 模块依赖

本 plugin 的所有依赖均为 `PrivateDependencyModuleNames`，使用者不需要额外依赖任何模块。插件内部依赖：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、委托 |
| `RHI` | 渲染硬件接口，用于视频帧渲染 |
| `RenderCore` | 渲染核心，Shader 编译管理 |
| `MoviePlayer` | 视频播放器核心，IMovieStreamer 接口 |
| `Slate` / `SlateCore` | UI 框架，构建加载画面布局 |
| `InputCore` | 输入处理，支持按键跳过 |
| `Projects` | 项目路径获取 |
| `HTTP` | 网络请求（视频流可能需要） |
| `BuildPatchServices` | 补丁服务支持 |
| `Json` | JSON 解析 |
| `Engine` | 引擎核心 |
| `ApplicationCore` | 应用核心 |
| `Analytics` / `AnalyticsET` | 分析追踪 |
| `PreLoadScreen` | 加载画面管理框架（`FPreLoadScreenBase`, `FPreLoadScreenManager`） |
| `CoreUObject` | UObject 基础设施 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions | RHI 命令列表传递方式重构，适配 UE5 渲染线程架构变更 |
| 2025-06-10 | `285e8eda` | Fix: PreLoad movie would play again on first map change; audio playing during editor launch | Bug 修复：修复了切换地图时视频重复播放、编辑器启动时视频音频播放的问题 |
| 2025-04-16 | `7b99f63d` | UE-248290 - Ensuring skipping logic is respected, matching DefaultGameMoviePlayer logic | Bug 修复：跳过逻辑与 DefaultGameMoviePlayer 保持一致 |

### 维护评价

- **创建时间**：2018 年 9 月，已有 7 年以上历史
- **近期活跃度**：2025 年有 3 次实质性提交，包含 bug 修复和架构适配，属于**维护中**状态
- **功能定位**：作为引擎核心加载流程的一部分，虽然代码量小但位置关键
- **已知限制**：
  - 仅支持 Android / iOS / Win64 三个平台
  - 需要在 `PreEarlyLoadingScreen` 阶段加载，时序要求严格
  - 不暴露 Blueprint 接口，纯 C++ 配置
  - 播放模式（Normal / Looped / LoadingLoop）无法通过 ini 配置，只能通过代码覆盖
- **推荐使用**：如果你需要引擎启动视频功能，这是官方默认实现，推荐直接使用。如果需要高度自定义的加载画面，建议基于 `PreLoadScreen` 模块自行开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/PreLoadScreenMoviePlayer)
- [MoviePlayer 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MoviePlayer)
- [PreLoadScreen 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/PreLoadScreen)
