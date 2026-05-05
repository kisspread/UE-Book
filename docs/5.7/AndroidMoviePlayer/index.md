# Android Movie Player

> Android Platform Movie Player using Android Media library

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | AndroidMoviePlayer (RuntimeNoCommandlet, PreLoadingScreen) |
| 创建时间 | 2014-11-20 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidMoviePlayer) | |

## 用途

AndroidMoviePlayer 是 UE5 的 **启动影片/加载画面播放器** 在 Android 平台上的原生实现。它通过 Java 层的 `android.media.MediaPlayer` API 来解码和播放 MP4 视频文件，并将视频帧渲染到 Slate 纹理上显示。

这个 plugin 存在的原因是：UE5 的 MoviePlayer 模块定义了一个 `IMovieStreamer` 接口，各平台需要提供各自的实现。Android 平台无法直接使用桌面端的 Bink 视频解码器，因此需要通过 JNI 调用 Android 系统自带的 MediaPlayer 来完成视频播放。

**核心职责：**
- 注册为 Android 平台的 MovieStreamer（通过 `FCoreDelegates::RegisterMovieStreamerDelegate`）
- 从 PAK 文件或文件系统中读取 MP4 视频
- 通过 JNI 调用 Java MediaPlayer 解码视频帧
- 将解码后的帧数据写入 RHI 纹理并显示到 Slate Viewport

**最低系统要求：** Android API Level 14 (Android 4.0 Ice Cream Sandwich)

## 使用场景

- **启动画面（Startup Movies）**：游戏启动时播放公司 Logo 或品牌动画，在 `DefaultEngine.ini` 中配置
- **关卡加载画面**：在地图切换时播放过渡视频，遮盖加载过程
- **过场动画**：使用全屏视频播放简单的过场动画（适合不需要实时渲染的场景）

典型配置示例（`DefaultEngine.ini`）：

```ini
[/Script/MoviePlayer.MoviePlayerSettings]
bMoviesAreSkippable=True
bWaitForManualStop=False

[/Script/UnrealEd.StartupMovies]
+StartupMovies=MyStartupMovie
```

将 MP4 文件放置在项目的 `Content/Movies/` 目录下即可。

## 蓝图用法

此 plugin **没有提供任何蓝图接口**。它是一个纯平台层的 Runtime 模块，在模块加载时自动注册为 MovieStreamer，不需要手动调用。

加载画面的配置通过以下方式：
1. **DefaultEngine.ini** 配置（`StartupMovies`、`MoviePlayerSettings`）
2. **C++ 代码**中调用 `IGameMoviePlayer::SetupLoadingScreen()`

## C++ 用法

此 plugin 的所有类都在 `Private` 目录下，**不暴露任何公共 API** 给外部模块。它通过引擎的 MoviePlayer 子系统自动工作，开发者通常不需要直接引用此模块。

### 头文件引入

不需要直接引入。此模块在加载时自动通过 delegate 注册到引擎的 MoviePlayer 系统。

### 间接使用（通过 MoviePlayer 接口）

```cpp
#include "MoviePlayer.h"

// 设置加载画面并播放视频
void UMyGameInstance::SetupLoadingScreen()
{
    FLoadingScreenAttributes LoadingScreen;
    LoadingScreen.bAutoCompleteWhenLoadingCompletes = true;
    LoadingScreen.bMoviesAreSkippable = true;
    LoadingScreen.MoviePaths.Add(TEXT("MyLoadingMovie"));  // 不需要扩展名，自动补 .mp4

    GetMoviePlayerRef().SetupLoadingScreen(LoadingScreen);
    GetMoviePlayerRef().PlayMovie();
}
```

### 模块内部工作原理

1. **StartupModule** 时创建 `FAndroidMediaPlayerStreamer` 实例
2. 通过 `FCoreDelegates::RegisterMovieStreamerDelegate` 注册到引擎
3. `Init()` 接收影片路径列表，调用 `StartNextMovie()` 开始播放
4. `StartNextMovie()` 构造完整路径（`Content/Movies/{name}.mp4`），支持：
   - 普通文件系统
   - OBB/APK Asset 文件
   - PAK 文件（未压缩/未加密时直接用文件偏移量；压缩或加密时需要 Android 6.0+ 的 MediaDataSource）
5. `Tick()` 每帧检查 MediaPlayer 播放位置，获取新帧并更新到 Slate 纹理
6. 视频播放完毕后自动播放队列中的下一个视频

### 渲染路径

- **OpenGL 模式**：通过 JNI 直接将 MediaPlayer 的 SurfaceTexture 绑定到 OpenGL 纹理
- **Vulkan 模式**：通过 `GetVideoLastFrameData()` 获取 CPU 侧像素数据，然后 `RHILockTexture2D` / `RHIUnlockTexture2D` 拷贝到 GPU 纹理

## Demo 示例

此 plugin 不适合提供独立的 Demo——它是平台层基础设施，由引擎的 MoviePlayer 子系统自动调用。

### 最小配置示例

**1. 在 `DefaultEngine.ini` 中添加启动影片：**

```ini
[/Script/UnrealEd.StartupMovies]
+StartupMovies=MyStartupMovie

[/Script/MoviePlayer.MoviePlayerSettings]
bMoviesAreSkippable=True
```

**2. 将视频文件放入：**

```
YourProject/Content/Movies/MyStartupMovie.mp4
```

**3. 打包 Android APK 后，启动影片会自动播放。**

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础设施、日志、路径处理、Delegate 系统 |
| `CoreUObject` | UObject 基础支持 |
| `Engine` | 引擎核心模块，提供 `FCoreDelegates` |
| `MoviePlayer` | 定义 `IMovieStreamer` 接口和 `IGameMoviePlayer` 系统 |
| `RenderCore` | RHI 渲染命令、纹理管理 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-08 | `40e2c8da10c3` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions | 引擎级 RHI 命令列表重构，MoviePlayer 的 `Tick()` 签名更新以接受 `FRHICommandListBase&` |
| 2025-06-16 | `ad86fe41bbf3` | Fixed black screen when playing start movies by forcing MovieStreamer to use BitmapRendererLegacy | 修复了启动影片黑屏问题，强制使用旧版位图渲染器 |
| 2025-06-05 | `092054b1ddd3` | A temporary fix to the black screen when playing startup movies | 上述修复的临时版本 |

### 维护评价

- **年龄**：超过 10 年（2014 年创建），属于 🏛️ 文物级 plugin
- **活跃度**：2025 年有两次实质性的 bug 修复（黑屏问题），说明仍在维护
- **稳定性**：代码非常成熟，近年来更新主要是适应引擎底层 API 变化（RHI 命令列表重构）和 bug 修复
- **风险**：最近两次更新都围绕启动影片黑屏问题，暗示这个功能可能存在边缘情况
- **推荐**：作为 Android 平台的基础设施 plugin，**不需要也无法手动启用或禁用**。如果你的项目面向 Android，此 plugin 在后台自动工作。如果你遇到启动影片黑屏问题，确保使用 5.6+ 版本以包含最新修复

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AndroidMoviePlayer)
- [MoviePlayer 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MoviePlayer)（定义 `IMovieStreamer` 接口）
- [官方文档](https://docs.unrealengine.com/en-US/)（.uplugin 中未提供专属文档链接）
