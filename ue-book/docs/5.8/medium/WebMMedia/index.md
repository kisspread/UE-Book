# WebM Video Player

> WebM Video Player Plugin.

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `libwebm` (External), `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-09-12 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia) | |

## 用途

WebMMedia 插件为 Unreal Engine 的 Media Framework 提供了 WebM 视频格式的解码与播放支持。它集成了 `libvpx`（VP8/VP9 编解码器）和 `libwebm` 库，使得引擎能够在 Windows 和 Linux 平台上播放 `.webm` 格式的视频文件。该插件是 Media Framework 的一个媒体源工厂，用于扩展引擎对 WebM 容器格式的原生支持。

## 使用场景

-   **游戏内视频播放**：在游戏开发中播放预先录制的 WebM 格式过场动画、叙事片段或游戏内电视屏幕内容。
-   **编辑器预览**：在虚幻编辑器中预览 WebM 格式的视频资产，用于内容检查和质量控制。
-   **跨平台媒体内容**：当项目的目标平台包含 Windows 或 Linux，且视频内容格式为 WebM 时使用。
-   **VP9 高清视频**：需要播放 VP9 编码的高质量、高压缩率视频流。

## 蓝图用法

本插件主要通过 Media Framework 的标准流程在蓝图中使用，即创建媒体源、媒体播放器组件并绑定。详细 API 请参考各子模块文档。
-   [WebMMedia 模块](WebMMedia.md)
-   [WebMMediaFactory 模块](WebMMediaFactory.md)
-   [WebMMediaEditor 模块](WebMMediaEditor.md)

## C++ 用法

本插件作为 Media Framework 的扩展，其 C++ 用法与标准 Media Framework API 一致，主要区别在于媒体源的创建。详细 API 和示例请参考各子模块文档。
-   [WebMMedia 模块](WebMMedia.md)
-   [WebMMediaFactory 模块](WebMMediaFactory.md)
-   [WebMMediaEditor 模块](WebMMediaEditor.md)

## 模块列表

| 模块 | 说明 |
|---|---|
| `libwebm` | 第三方外部模块，提供解析 WebM 容器格式的 C++ 库。 |
| `WebMMedia` | 核心运行时模块，实现 `FWebMMediaPlayer` 媒体播放器，负责使用 `libvpx` 和 `libwebm` 解码并播放 WebM 视频流。 |
| `WebMMediaFactory` | 运行时模块，提供 `UWebMMediaPlayerFactory`，使 Media Framework 能够识别并创建 WebM 格式的媒体播放器。 |
| `WebMMediaEditor` | 编辑器运行时模块，为 WebM 媒体源资产提供缩略图生成等编辑器支持功能。 |

## 模块依赖

要使用此插件，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `LibVpx` | 提供 VP8/VP9 视频编解码器的核心库。 |
| `MediaUtils` | 提供 Media Framework 的通用工具类和接口。 |
| `WebM` | 提供 WebM 容器格式解析的第三方库接口。 |

其他依赖（如 `Core`, `Engine` 等）为引擎标准模块，此处省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `6fa2f4c5` | WebMMedia: Fixed video full range yuv offsets | 修复视频全范围 YUV 颜色偏移问题。 |
| 2026-04-21 | `f9163c8f` | WebMMedia: Added support for 10 bit VP9 files; fixed an issue where images were overwritten before t | 添加 10 位 VP9 视频支持，并修复了图像被覆盖的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-11 | `2639e40b` | Updated libvpx to 1.15.1, did not copy the duplicated headers layout from 1.14.1 | 更新了 libvpx 第三方库至 1.15.1 版本。 |
| 2026-01-22 | `0bfe789b` | WebMMedia: Rewrite of the plugin | 对插件进行了重写，是重要的架构更新。 |

### 维护评价

**活跃维护**。尽管该插件标记为实验性（`IsBetaVersion=true`），但近期（2026 年）更新非常频繁，包含了功能增强（如 10 位 VP9 支持）、重要 Bug 修复和底层库更新。最近的“重写”提交表明开发者正在积极改进其架构和功能。目前仍在活跃维护中，可以推荐使用，但需注意其“实验性”标签，意味着 API 或行为可能在未来版本中发生变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/WebMMedia)
-   [WebMMedia 模块文档](WebMMedia.md)
-   [WebMMediaFactory 模块文档](WebMMediaFactory.md)
-   [WebMMediaEditor 模块文档](WebMMediaEditor.md)
-   [libwebm 模块文档](libwebm.md)