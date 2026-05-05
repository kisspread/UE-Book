# Movie Player for WebM files

> Movie Player for WebM files

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | 否 |
| 模块 | WebMMoviePlayer (RuntimeNoCommandlet, PreLoadingScreen) |
| 创建时间 | 2018-10-16 |
| 年龄标签 | 👴 老古董（约 7.5 年） |
| 支持平台 | Win64, Linux, Mac（排除 Server） |
| 依赖插件 | WebMMedia |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebMMoviePlayer) | |

## 用途

WebMMoviePlayer 是 UE5 的**启动画面（Startup Movies）**播放器，用于在引擎加载阶段播放 `.webm` 格式的视频文件。

它解决了什么问题：UE 的 MoviePlayer 系统需要一个具体的视频解码后端来播放启动画面。传统上 UE 使用 Bink 视频（BinkMovieStreamer），但 Bink 是第三方商业库。这个 plugin 通过 WebM/VP8+Vorbis 开源编解码器提供了替代方案，使启动画面可以在不依赖 Bink 的情况下工作。

核心工作流程：
1. 模块启动时创建 `FWebMMovieStreamer` 并注册到 `MoviePlayer` 系统
2. 引擎请求播放启动画面时，从 `Content/Movies/` 目录加载 `.webm` 文件
3. 使用 `FWebMContainer` 解析 WebM 容器，分别用 `FWebMVideoDecoder`（VP8 视频）和 `FWebMAudioDecoder`（Vorbis 音频）异步解码
4. 视频帧渲染到 Slate 纹理上显示，音频通过平台音频后端输出
5. 支持播放队列（多个文件无缝衔接播放）

**重要限制**：由于 `WITH_WEBM_STARTUP_MOVIES` 宏的定义，此 plugin 仅在 **Linux** 平台上作为启动画面播放器生效。在 Windows 和 Mac 上，虽然 plugin 会被加载，但 `WITH_WEBM_STARTUP_MOVIES=0`，Streamer 不会注册（这两个平台走 BinkMovieStreamer）。

## 使用场景

- 你在 Linux 平台打包游戏，需要在启动时显示公司 Logo 或加载画面 → 用此 plugin
- 你需要用开源编解码器替代商业 Bink 库来播放启动视频 → 用此 plugin
- 你不想为 Bink 授权付费，只需在启动阶段播放简单视频 → 用此 plugin

## 蓝图用法

此 plugin **不暴露任何蓝图接口**。它是一个纯 Runtime 自动注册模块，所有行为由 MoviePlayer 系统自动驱动。

配置启动画面的标准方式是通过 `DefaultGame.ini`：

```ini
[/Script/MoviePlayer.MoviePlayerSettings]
bMoviesAreSkippable=True
+StartupMovies=MyStartupMovie
+StartupMovies=MySecondMovie
```

将 `.webm` 文件放在 `Content/Movies/` 目录下即可。

## C++ 用法

此 plugin 通常**不需要直接 C++ 交互**。它通过 MoviePlayer 框架自动工作。如果你需要在代码中控制启动画面的播放，使用的是 MoviePlayer 模块的 API，而非本 plugin 的 API。

### 间接使用（通过 MoviePlayer）

```cpp
#include "MoviePlayer.h"

// 检查是否有启动画面在播放
if (IsMoviePlayerEnabled())
{
    // 获取 MoviePlayer 实例
    IMoviePlayer* MoviePlayer = GetMoviePlayer();
    
    // 等待启动画面完成
    // MoviePlayer 内部会使用已注册的 Streamer（如 FWebMMovieStreamer）
}
```

### 内部架构（供参考）

此 plugin 的核心类 `FWebMMovieStreamer` 实现了 `IMovieStreamer` 接口：

- **Init()** — 初始化音频后端，注册前后台切换委托，开始播放队列中的第一个视频
- **Tick()** — 每帧调用，驱动视频帧显示、音频发送和帧读取解码
- **ForceCompletion()** — 强制停止播放并清空队列
- **HandleApplicationWillEnterBackground()** — 进入后台时暂停播放
- **HandleApplicationHasEnteredForeground()** — 回到前台时恢复播放

## Demo 示例

### 最小配置示例

1. 启用 plugin（默认已启用，无需额外操作）
2. 将 `.webm` 文件放入项目的 `Content/Movies/` 目录
3. 在 `Config/DefaultGame.ini` 中添加：

```ini
[/Script/MoviePlayer.MoviePlayerSettings]
bMoviesAreSkippable=True
+StartupMovies=YourMovieName
```

4. 打包 Linux 版本，启动时即可看到视频播放

**注意**：`.webm` 文件名不含扩展名，上面的 `YourMovieName` 对应 `Content/Movies/YourMovieName.webm`。

## 模块依赖

本 plugin 的所有依赖都是 **PrivateDependencyModuleNames**，意味着使用者不需要在自己的模块中引用这些模块。

| 模块 | 用途 |
|---|---|
| `Core` | 基础核心库 |
| `Engine` | 引擎核心 |
| `MoviePlayer` | 启动画面播放框架（IMovieStreamer 接口） |
| `RenderCore` | 渲染核心（纹理管理） |
| `RHI` | 渲染硬件接口 |
| `SlateCore` | Slate UI 核心 |
| `Slate` | Slate UI 框架 |
| `MediaUtils` | 媒体工具（采样缓冲区） |
| `WebMMedia` | WebM 解码器和容器解析 |
| `SDL3` | 仅 Unix 平台，音频输出（SDL3 backend） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-08 | `40e2c8da` | Passing RHI Command Lists through to MoviePlayer and TickableObjectRenderThread functions | 架构更新：Tick 函数签名变更，需要传入 RHI Command List。这是 UE5 渲染管线现代化的一部分 |
| 2025-06-05 | `2d71abc7` | fix WITH_WEBM_LIBS mismatched define on Windows Arm64 | Bug 修复：修复 Windows Arm64 平台上 `WITH_WEBM_LIBS` 宏定义不匹配的问题 |
| 2025-05-13 | `279bfd56` | Engine Changes for SDL3 | 平台适配：从 SDL2 迁移到 SDL3 音频后端 |

### 维护评价

- **创建时间**：2018 年 10 月，已存在约 7.5 年
- **维护状态**：**活跃维护** — 2025 年有多次实质性更新（RHI 签名变更、平台修复、SDL3 迁移）
- **代码质量**：代码简洁清晰，~350 行核心实现，职责分明
- **限制**：
  - 实际仅在 Linux 平台作为启动画面播放器生效（Windows/Mac 使用 Bink）
  - 无蓝图接口，无测试用例
  - 依赖 WebMMedia plugin 提供底层解码能力
- **推荐度**：如果你的目标平台包含 Linux 且需要播放启动画面，此 plugin 是默认且推荐的选择。它默认启用，无需额外配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/WebMMoviePlayer)
- 无官方文档（.uplugin 中 DocsURL 为空）
- 无测试用例
