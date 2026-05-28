# Apple Movie Player

> Apple Platform Movie Player using AVPlayer library（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 苹果视频播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleMoviePlayer` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物（约 11 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleMoviePlayer) | |

## 用途

此插件为 Unreal Engine 提供了一个原生的苹果平台视频播放器实现。它利用 Apple 的 AVFoundation 框架（具体是 `AVPlayer` 相关的 `AVAudioPlayer`、`AVURLAsset` 等类）在 iOS、tvOS 和 macOS 平台上播放视频文件。其主要作用是处理引擎内置的电影播放流程，例如游戏启动时的加载动画、过场动画或游戏内的视频播放需求，为这些平台提供一个高性能、系统原生的视频解码和渲染管线。

## 使用场景

- **游戏启动视频**：在 iOS、tvOS 或 Mac 平台上运行游戏时，播放加载或启动视频。
- **过场动画播放**：在游戏过程中需要播放预先录制的视频片段作为过场动画。
- **游戏内视频内容**：任何需要在这些 Apple 设备上播放视频文件（如 .mp4, .mov）的场景。
- **平台特定优化**：当目标平台为 Apple 设备，且希望获得系统原生的视频播放性能和兼容性时。

## 蓝图用法

此插件主要作为底层媒体流实现，未提供额外的蓝图节点。其功能通过 Unreal Engine 内置的 **Movie Player** 系统（如 `UMoviePlayer` 蓝图节点）来间接使用。当平台为 Apple 设备时，引擎会自动选用此插件提供的流播放器。

## C++ 用法

此插件的核心类是 `FAVPlayerMovieStreamer`，它实现了 `IMovieStreamer` 接口。通常开发者不需要直接调用此类，引擎的 `FMoviePlayer` 会管理它的生命周期。以下是其关键接口的简要说明。

### 头文件引入

```cpp
// 通常不需要直接包含，引擎内部使用
// #include "AppleMovieStreamer.h"
```

### 基本用法（内部接口）

`FAVPlayerMovieStreamer` 实现了 `IMovieStreamer` 的核心方法，供引擎内部调用。

```cpp
// (源码：Source/AppleMoviePlayer/Private/AppleMovieStreamer.h)

// 1. 初始化播放器并加载电影文件
virtual bool Init(const TArray<FString>& MoviePaths, TEnumAsByte<EMoviePlaybackType> inPlaybackType) override;

// 2. 引擎每帧调用，更新视频帧和同步状态
virtual bool Tick(FRHICommandListBase& RHICmdList, float DeltaTime) override;

// 3. 获取用于 Slate 显示的视口接口
virtual TSharedPtr<class ISlateViewport> GetViewportInterface() override;

// 4. 清理资源
virtual void Cleanup() override;

// 5. 处理视频播放中断后的恢复（如接听电话）
virtual void Suspend() override;
virtual void Resume() override;
```

### 进阶用法（内部实现）

插件内部使用 AVFoundation 框架进行视频解码和音频同步。

```cpp
// (源码：Source/AppleMoviePlayer/Private/AppleMovieStreamer.h)

// 从文件路径异步加载电影资源
bool LoadMovieAsync(FString MovieName);

// 设置并开始播放队列中的下一部电影
bool StartNextMovie();

// 检查并复制下一帧视频数据到渲染纹理
bool CheckForNextFrameAndCopy(FRHICommandListBase& RHICmdList);

// 停止当前播放并释放相关 AVFoundation 对象
void TeardownPlayback();
void ReleaseMovie();
```

## Demo 示例

此插件是引擎内部模块，没有独立的示例项目。其功能通过引擎的 `MoviePlayer` 模块集成。

## 模块依赖

从插件的性质和 `LoadingPhase: PreLoadingScreen` 推断，它可能依赖于以下模块。由于是平台特定媒体播放，通常依赖于 `MediaUtils` 和 `MediaAssets`。

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 媒体播放框架工具 |
| `MediaAssets` | 媒体资产处理 |
| `MediaFoundation` (或平台特定媒体模块) | 底层媒体框架抽象 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出迁移到新版 UE_LOGF 宏 |
| 2026-04-13 | `b905d146` | Fix/Silence unreachable code warnings | 修复/屏蔽不可达代码警告 |
| 2026-01-24 | `99277a85` | Fixed compile errors when building UnrealGame with portable toolchain | 修复使用可移植工具链构建 UnrealGame 时的编译错误 |
| 2026-01-23 | `0ae4775f` | Enabling explicit partform SDK requirement in multiple modules | 在多个模块中启用明确的平台 SDK 要求 |
| 2026-01-13 | `4c04edd1` | [IOS/Mac] Initial pass to remove iOS/macOS sdk headers from Engine platform header files where possi... | [IOS/Mac] 初步尝试从引擎平台头文件中移除 iOS/macOS SDK 头文件 |

### 维护评价

- **创建时间**：2014年，是 Unreal Engine 4 时代的古老插件。
- **更新频率**：近期（2026年1月和4月）有更新，但均为工具链、编译警告、SDK 管理等维护性更新，**没有实质性的功能改进**。
- **活跃状态**：处于**低活跃维护**状态，主要目的是保持与最新引擎版本的编译兼容性。
- **已知限制**：仅限 Apple 平台（iOS, tvOS, Mac）。
- **推荐使用**：对于面向 Apple 平台的项目，当需要播放引擎内置的电影文件时，此插件是默认且必须的，**无需额外启用或配置**。但其功能局限于引擎的电影播放系统，不用于流媒体或自定义视频播放需求。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AppleMoviePlayer)
- [官方文档]()（无）
- [测试用例]()（未发现专门测试用例）