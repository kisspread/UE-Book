# Windows Movie Player

> Windows Specific Movie Player using Media Foundation

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | true |
| 包含内容 | false |
| 模块 | WindowsMoviePlayer (RuntimeNoCommandlet) |
| 加载阶段 | PreLoadingScreen |
| 平台 | Win64 |
| 创建时间 | 2014-03-14 |
| 年龄标签 | 🏛️ 文物(>10年) |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WindowsMoviePlayer) | |

## 用途

为 UE5 的 **过场动画 / 加载画面** 系统提供 Windows 平台专属的视频播放后端。

引擎内置的 `MoviePlayer` 模块定义了 `IMovieStreamer` 接口，而本 plugin 在模块启动时将 `FMediaFoundationMovieStreamer` 注册为该接口的实现。底层使用 **Windows Media Foundation (MF)** 解码 .mp4 视频，将每一帧抓取后通过 GPU shader 转换为 Slate 可显示的纹理。

简单来说：**引擎播放启动影片、加载画面时，实际解码视频的就是这个 plugin。**

## 使用场景

- 游戏启动时播放 Splash / 开发商 Logo 影片
- 关卡加载时显示带动画的 Loading 画面
- 需要在 Windows 上原生播放 MP4 视频作为背景（无需 Media Framework 的 MediaPlayer 复杂管线）

## 蓝图用法

本 plugin **没有暴露任何蓝图节点**。它是一个纯系统级模块，在引擎启动时自动注册，无需手动调用。

过场动画/加载画面的播放通常通过 `MoviePlayer` 子系统（C++ 层面）或项目设置中的 Splash Screen 配置触发，而非蓝图节点。

## C++ 用法

本 plugin 不对外暴露公共 API。它的行为是自动的：模块加载 → 注册 MovieStreamer → 引擎的 MoviePlayer 子系统使用它播放影片。

### 工作原理

```
引擎启动
  ↓
FWindowsMoviePlayerModule::StartupModule()
  ↓ 加载 shlwapi.dll, mf.dll, mfplat.dll, mfplay.dll
  ↓ MFStartup(MF_VERSION)
  ↓ 创建 FMediaFoundationMovieStreamer
  ↓ FCoreDelegates::RegisterMovieStreamerDelegate.Broadcast()
  ↓
引擎 MoviePlayer 子系统持有 Streamer 引用
  ↓ 需要播放影片时调用 Init(MoviePaths, PlaybackType)
  ↓ FMediaFoundationMovieStreamer 内部用 FVideoPlayer (Media Foundation) 解码
  ↓ FSampleGrabberCallback 抓取每帧原始像素
  ↓ ConvertSample() 用 MediaShaders 做 YUV→RGB 转换
  ↓ FSlateTexture2DRHIRef 渲染到 Slate Viewport
```

### 支持的视频格式

| 编解码器 | 采样格式 | 转换方式 |
|---|---|---|
| H.264 / H.264_ES | CharYUY2 | YUV→RGB shader（Rec709） |
| RGB555 / RGB565 / RGB24 / RGB32 / ARGB32 | CharBMP | BMP 转换 shader |

- 容器格式：**MP4**（硬编码 `.mp4` 扩展名）
- H.264 视频宽度会被对齐到 16 像素边界

### 关键实现细节

1. **影片路径解析**：路径相对于 `FPaths::ProjectContentDir() + "Movies/"`，自动追加 `.mp4` 后缀
   ```cpp
   // WindowsMovieStreamer.cpp:258
   FString MoviePath = FPaths::ProjectContentDir() + TEXT("Movies/") + StoredMoviePaths[MovieIndex];
   // 实际加载: MoviePath.mp4
   ```

2. **音频失败自动重试**：如果音频设备不可用（`MF_E_CANNOT_CREATE_SINK`），会自动禁用声音重试播放
   ```cpp
   // WindowsMovieStreamer.cpp:206-210
   if (VideoPlayer->FailedToCreateMediaSink() && bUseSound)
   {
       bUseSound = false;
       --MovieIndex; // 重试当前影片
   }
   ```

3. **HMD 音频路由**：如果存在 VR 头显，音频会自动路由到 HMD 的音频输出设备

4. **播放模式**：支持 `MT_Normal`（播完停止）、`MT_LoadingLoop`（循环最后一段）、`MT_Looped`（循环全部）

## Demo 示例

由于本 plugin 是系统级自动注册模块，不需要编写额外代码。要在项目中使用它播放加载画面影片：

1. 将 `.mp4` 文件放到 `Content/Movies/` 目录下
2. 在代码或配置中调用 MoviePlayer 子系统：

```cpp
// MyGameLoadingScreen.cpp
#include "MoviePlayer.h"

void ShowLoadingScreen(const FString& MovieName)
{
    // MovieName 不含扩展名，引擎会自动追加 .mp4
    // 文件实际路径: {ProjectDir}/Content/Movies/{MovieName}.mp4
    GetMoviePlayer()->PlayMovie(MovieName);
}
```

如果需要在项目设置中配置 Splash Screen，走 **Project Settings → Platforms → Windows → Splash** 路径即可，底层同样使用本 plugin。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础框架 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入系统（间接依赖） |
| `MoviePlayer` | 过场动画/加载画面播放器接口 |
| `RenderCore` | 渲染核心 |
| `RHI` | 渲染硬件接口 |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate UI 框架 |

运行时还依赖以下 Windows DLL（延迟加载）：
- `shlwapi.dll` — Shell 轻量工具
- `mf.dll` — Media Foundation 核心
- `mfplat.dll` — Media Foundation 平台
- `mfplay.dll` — Media Foundation 播放
- `mfuuid.dll` — Media Foundation UUID

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-27 | `7766f4c6` | Fixed return value of movie streamers to be the result of the actual open call | 修复 `Init()` 的返回值，使其正确反映影片是否成功打开 |
| 2025-08-12 | `6214b8aa` | Cleaning up a few movie streamer issues | 修复若干 MovieStreamer 问题 |
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions | RHI Command List 重构，适配新版渲染管线 |

### 维护评价

- **年龄**：2014 年创建，已超过 10 年，是引擎最古老的 plugin 之一
- **活跃度**：2025 年 8 月仍有功能性更新（RHI Command List 重构 + bug 修复），属于 **活跃维护** 状态
- **稳定性**：代码量小（~820 行 .cpp + ~230 行 .h），结构稳定，改动通常是为了适配引擎底层 API 变化
- **推荐**：Windows 平台上播放过场动画影片的默认方案，**放心使用**。如需跨平台视频播放，应考虑 Media Framework（WmfMedia / AvfMedia 等）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WindowsMoviePlayer)
- [MoviePlayer 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Runtime/MoviePlayer)（本 plugin 的上游接口）
