# WebM Movie Player

> Movie Player for WebM files

| 属性 | 值 |
|---|---|
| 中文名 | WebM 影片播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMoviePlayer` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2018-10-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebMMoviePlayer) | |

## 用途

该插件为引擎的 MoviePlayer 系统提供 WebM 格式影片的流式播放能力。它实现了 `IMovieStreamer` 接口，主要用于**加载画面（Loading Screen）**期间播放 WebM 格式的视频文件。

核心工作流程：
1. 接收影片路径列表，按顺序依次播放
2. 内部创建 WebM 容器解析器、视频解码器和音频解码器（依赖 WebMMedia 插件）
3. 逐帧解码并通过 RHI 命令列表提交纹理到 Slate 视口
4. 处理前后台切换时的暂停/恢复逻辑
5. 当前影片播完后自动播放队列中的下一部

**平台限制**：仅支持 Win64、Linux、Mac，不支持 Server 目标。

**音频特殊说明**：Linux 平台通过 SDL3 播放音频，而 **Windows 和 Mac 使用空音频后端（无音频输出）**。

## 使用场景

- 你的游戏需要在加载画面播放 WebM 格式的品牌视频或过场动画
- 你在 Linux 平台部署游戏，需要加载画面视频播放支持
- 你想通过引擎内置的 MoviePlayer 控制台命令播放 WebM 文件（如 `movie play MyVideo`）

## 蓝图用法

该插件不暴露任何蓝图 API。它是引擎 MoviePlayer 系统的内部实现，通过引擎自动发现和注册。播放 WebM 影片通常通过以下方式触发：

- 控制台命令 `movie play <MovieName>`
- C++ 中调用 `GetMoviePlayer()->PlayMovie()`
- 加载关卡时引擎自动播放指定的加载影片

## C++ 用法

该插件作为 `IMovieStreamer` 的实现，由引擎 MoviePlayer 模块自动发现和使用，通常**无需直接引用**。了解其内部机制有助于调试和扩展。

### 核心接口

`FWebMMovieStreamer` 同时实现了两个接口：

| 接口 | 用途 |
|---|---|
| `IMovieStreamer` | 引擎影片播放器的流式播放接口 |
| `IWebMSamplesSink` | 接收 WebM 解码后的音视频采样 |

### IMovieStreamer 关键方法

```cpp
// 初始化影片播放队列
bool Init(const TArray<FString>& InMoviePaths, TEnumAsByte<EMoviePlaybackType> InPlaybackType);

// 每帧驱动解码和显示（在渲染线程通过 RHI 命令列表执行）
bool Tick(FRHICommandListBase& RHICmdList, float InDeltaTime);

// 获取当前帧纹理（用于 Slate 视口显示）
FTextureRHIRef GetTexture();

// 获取 Slate 视口接口（用于绘制到屏幕）
TSharedPtr<ISlateViewport> GetViewportInterface();

// 强制完成播放
void ForceCompletion();
```

### IWebMSamplesSink 回调

```cpp
// 从解码线程接收视频采样
virtual void AddVideoSampleFromDecodingThread(
    TSharedRef<FWebMMediaTextureSample, ESPMode::ThreadSafe> Sample) override;

// 从解码线程接收音频采样
virtual void AddAudioSampleFromDecodingThread(
    TSharedRef<FWebMMediaAudioSample, ESPMode::ThreadSafe> Sample) override;
```

## Demo 示例

该插件无用户直接编写的示例——它是引擎 MoviePlayer 系统的内部组件。以下展示如何通过引擎的 MoviePlayer 系统触发 WebM 播放：

```cpp
// MyGameInstance.cpp
#include "MoviePlayer.h"

void UMyGameInstance::OnPreLoadMap(const FString& MapName)
{
    FLoadingScreenAttributes LoadingScreen;
    LoadingScreen.bAutoCompleteWhenLoadingCompletes = true;
    LoadingScreen.bMoviesAreSkippable = false;
    LoadingScreen.bWaitForManualStop = false;

    // 指定 WebM 文件名（放在 Content/Movies/ 目录下）
    LoadingScreen.MoviePaths.Add(TEXT("MyLoadingVideo"));

    GetMoviePlayer()->SetupLoadingScreen(LoadingScreen);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SDL3` | Linux 平台音频输出（仅 Linux 使用） |
| `WebMMedia` | 插件级依赖，提供 WebM 解码能力 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | 对 WebMMedia 插件进行重大重写 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions. | MoviePlayer 的 Tick 方法现在通过 RHI 命令列表执行 |
| 2025-06-05 | `2d71abc7` | fix WITH_WEBM_LIBS mismatched define on Windows Arm64 | 修复 Windows Arm64 平台上 WebM 库宏定义不匹配的问题 |
| 2025-05-13 | `279bfd56` | Engine Changes for SDL3 | 引擎级别的 SDL3 适配变更 |

### 维护评价

该插件自 2018 年创建，近期仍有实质性更新（2026 年初有一次重写级改动）。但需要注意：

- ⚠️ **Windows 和 Mac 平台音频不工作**——这两个平台使用 Null 音频后端，播放 WebM 影片时只有画面没有声音
- 该插件非常轻量（仅 11 个源文件），属于引擎内部组件，不需要用户直接维护
- 作为引擎默认启用的插件，Epic 会在引擎迭代中持续维护

**推荐使用**：如果你需要在加载画面播放 WebM 视频，该插件会自动工作。但请注意音频限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WebMMoviePlayer)
- [WebMMedia 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)（依赖的 WebM 解码器插件）