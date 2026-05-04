# Apple Movie Player

> Apple Platform Movie Player using AVPlayer library

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AppleMoviePlayer (RuntimeNoCommandlet, PreLoadingScreen) |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物 (>10年) |
| 平台 | IOS, TVOS, Mac |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/AppleMoviePlayer) | |

## 用途

为 Apple 平台（iOS、tvOS、Mac）提供基于 AVFoundation 框架的过场视频（Loading Screen / Movie Player）播放能力。该 Plugin 是 UE5 `MoviePlayer` 子系统的 Apple 平台后端实现——当引擎需要播放启动视频、关卡加载画面等过场动画时，它负责通过 `AVAssetReader` 逐帧解码 MP4 视频，使用 Metal 纹理缓存将视频帧直接传入 GPU，并通过 `AVAudioPlayer` 同步播放音频。

**为什么存在？** UE5 的 `MoviePlayer` 是一个跨平台的接口抽象，每个平台需要自己的流媒体后端。在 Apple 平台上，`AVFoundation` 是系统原生的媒体框架，相比其他方案（如 FFmpeg），它有硬件加速解码、系统级 DRM 支持、以及与系统音频路由的无缝集成等优势。

## 使用场景

- **启动画面/Logo 视频**：游戏启动时播放开发商 Logo、引擎 Logo 等过场视频
- **关卡加载画面**：在关卡切换时播放加载动画视频，掩盖加载时间
- **On-Demand Resources 视频**：iOS 上使用 Apple On-Demand Resources 系统动态下载并播放视频内容

### 不适用场景

- 实时游戏内视频播放（该 Plugin 通过 `IMovieStreamer` 接口工作，专为 `MoviePlayer` 系统设计，不适合用于游戏内媒体播放）
- 从网络流播放视频（仅支持本地文件）

## 蓝图用法

该 Plugin 不暴露任何 Blueprint 节点。它是一个纯底层 Runtime 模块，在模块启动时自动注册为 `MoviePlayer` 的流媒体后端，对蓝图完全透明。

过场视频的播放由引擎的 `MoviePlayer` 子系统统一控制，相关蓝图节点位于 `FLoadingScreenAttributes` / `UMoviePlayerSettings` 等类中（属于 Engine 模块，不属于本 Plugin）。

## C++ 用法

### 工作原理

该 Plugin 的核心是 `FAVPlayerMovieStreamer` 类，它实现了 `IMovieStreamer` 接口：

1. **模块启动时**自动注册：`StartupModule()` 创建 `FAVPlayerMovieStreamer` 实例并通过 `FCoreDelegates::RegisterMovieStreamerDelegate` 注册
2. **播放时**引擎调用 `Init()` 传入视频路径队列，Streamer 通过 `AVURLAsset` 异步加载视频轨道
3. **每帧更新**由 `Tick()` 驱动：使用 `CVMetalTextureCacheCreateTextureFromImage` 将 `CVPixelBuffer` 直接包装为 Metal 纹理，实现零拷贝 GPU 上传
4. **音视频同步**：音频由 `AVAudioPlayer` 播放，视频帧通过时间戳与 `CACurrentMediaTime()` 对比实现同步（Ready/Ahead/Behind 状态机）
5. **暂停/恢复**支持 iOS 后台挂起场景，通过记录 `ResumeTime` 实现断点续播

### 关键类

| 类 | 说明 |
|---|---|
| `FAVPlayerMovieStreamer` | 核心流媒体实现，管理 AVFoundation 播放器生命周期 |
| `FAppleMoviePlayerModule` | 模块入口，负责注册/注销 Streamer |

### 视频文件要求

从源码分析可知，播放视频有以下约束：

- **格式**：MP4（硬编码 `@\"mp4\"` 扩展名）
- **宽度**：必须是 16 像素的倍数（源码中有 `int(naturalSize.width) % 16 != 0` 检查）
- **路径**：视频文件必须放在 `Content/Movies/` 目录下（由 `FPaths::ProjectContentDir() + TEXT("Movies/")` 拼接）
- **像素格式**：BGRA 32 位（`kCVPixelFormatType_32BGRA`）

### 头文件引入

```cpp
// 通常不需要直接引入，Plugin 自动注册。
// 如果需要访问 MoviePlayer API：
#include "MoviePlayer.h"
```

### 基本用法

该 Plugin 是自动工作的——只要启用，引擎的 MoviePlayer 系统会自动使用它来播放过场视频。以下展示如何从 C++ 触发过场视频播放（属于 Engine 的 MoviePlayer API，不是本 Plugin 独有）：

```cpp
#include "MoviePlayer.h"

// 播放一个 Loading Screen 视频
void PlayLoadingScreen()
{
    FLoadingScreenAttributes LoadingScreen;
    LoadingScreen.bAutoCompleteWhenLoadingCompletes = true;
    LoadingScreen.bMoviesAreSkippable = false;
    LoadingScreen.bWaitForManualStop = false;
    
    // 指定要播放的视频名称（对应 Content/Movies/YourMovie.mp4）
    LoadingScreen.MoviePaths.Add(TEXT("YourMovie"));
    
    GetMoviePlayer()->SetupLoadingScreen(LoadingScreen);
}
```

*来源：引擎 MoviePlayer API，AppleMoviePlayer 作为后端自动参与播放*

### 进阶用法

#### 多视频无缝连播

`Init()` 接受 `TArray<FString>` 形式的视频路径队列，支持多视频无缝播放：

```cpp
// MovieQueue 内部机制：
// 1. Init() 将所有路径加入队列
// 2. StartNextMovie() 依次取出播放
// 3. 前一个视频播完后自动启动下一个
// 4. IsLastMovieInPlaylist() 判断是否是最后一个
```

#### iOS 暂停/恢复

在 iOS 上，当 App 进入后台时，Plugin 自动暂停播放并保存恢复时间点；回到前台时自动从断点恢复：

```cpp
// Suspend() 内部逻辑：
// 1. 记录当前播放时间到 ResumeTime
// 2. 暂停 AudioPlayer
// 3. 取消 AVReader 读取
// 4. 释放视频资源

// Resume() 内部逻辑：
// 1. 从 ResumeTime 时间点重新加载同一视频
// 2. AVReader 的 timeRange 从 ResumeTime 开始
```

## Demo 示例

该 Plugin 不需要用户编写额外代码。最小使用步骤：

### 1. 确认 Plugin 已启用

在 `.uproject` 文件中确认没有禁用它（默认已启用）：

```json
{
    "Plugins": [
        {
            "Name": "AppleMoviePlayer",
            "Enabled": true
        }
    ]
}
```

### 2. 放置视频文件

将 MP4 文件放入项目的 `Content/Movies/` 目录：

```
YourProject/
└── Content/
    └── Movies/
        └── Loading.mp4
```

### 3. 在代码或配置中引用

在 GameInstance 或其他合适位置设置 Loading Screen：

```cpp
// MyGameInstance.cpp
#include "MoviePlayer.h"
#include "Kismet/GameplayStatics.h"

void UMyGameInstance::Init()
{
    Super::Init();
    
    FLoadingScreenAttributes LoadingScreen;
    LoadingScreen.bAutoCompleteWhenLoadingCompletes = true;
    LoadingScreen.MoviePaths.Add(TEXT("Loading"));
    GetMoviePlayer()->SetupLoadingScreen(LoadingScreen);
}
```

### Build.cs 依赖

```csharp
// 如果你需要直接使用 MoviePlayer API
PublicDependencyModuleNames.AddRange(new string[] {
    "MoviePlayer"
});
```

> **注意**：AppleMoviePlayer 本身会自动注册，不需要在你的 Build.cs 中依赖它。

## 模块依赖

以下是 AppleMoviePlayer 自身的依赖（来自 Build.cs），供了解其内部构成：

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `MoviePlayer` | 过场播放器接口（`IMovieStreamer` 抽象） |
| `RenderCore` | 渲染核心（纹理管理） |
| `RHI` | 渲染硬件接口（RHI 命令列表） |
| `Slate` | UI 框架（`FSlateTexture2DRHIRef` 视口纹理） |
| `ApplicationCore` | 应用核心 |
| `MetalRHI` | Metal 渲染后端（`IMetalDynamicRHI`、`CVMetalTextureCache`） |
| `SlateCore` (Private) | Slate 核心 |

> **使用者注意**：你不需要依赖 AppleMoviePlayer 模块本身。你只需要依赖 `MoviePlayer` 模块来使用过场播放 API，AppleMoviePlayer 作为平台后端自动生效。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions | 适配 UE5 RHI 命令列表重构，`Tick()` 和 `CheckForNextFrameAndCopy()` 的签名从 `FRHICommandListImmediate&` 改为 `FRHICommandListBase&` |
| 2025-06-02 | `2c095ca4` | Replace EBulkDataType in MetalRHI with Metal-specific RHI functions | 适配 MetalRHI 接口变更 |
| 2025-05-06 | `5243d97b` | RHI CreateTexture refactor - Textures are now created using FRHITextureInitializer objects | 适配 RHI 纹理创建重构，使用新的 `FRHITextureCreateDesc` API |

### 维护评价

- **创建时间**：2014 年 3 月，已有 12+ 年历史（🏛️ 文物级）
- **更新频率**：近期更新密集（2025 年有 3 次提交），但全部是**被动适配** RHI/MetalRHI 接口变更，无功能性更新
- **代码规模**：非常小（约 665 行 .cpp + 96 行 .h），结构稳定
- **活跃度**：作为 Apple 平台的基础媒体后端，随引擎 RHI 层变更被动维护，但核心逻辑多年未变
- **限制**：仅支持 Apple 平台（iOS/tvOS/Mac），依赖 Metal 渲染后端
- **推荐**：✅ 在 Apple 平台上这是默认启用的基础组件，无需额外决策。如果你需要播放过场视频，它会自动工作

⚠️ 该 Plugin 的核心播放逻辑自创建以来变化极小，近期更新仅为适配底层 RHI 接口变更。功能层面已多年未有实质性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/AppleMoviePlayer)
- 官方文档：无（`.uplugin` 中 DocsURL 为空）
- 相关引擎模块：`Engine/Source/Runtime/MoviePlayer/`（MoviePlayer 接口定义）
