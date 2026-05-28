# Apple ProRes Media

> Implements video playback and the export of the Apple ProRes Codec.  Apple ProRes is a high quality, lossy video compression format.

| 属性 | 值 |
|---|---|
| 中文名 | ProRes 视频 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AppleProResMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-08-16 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia) | |

## 用途

此插件为 Unreal Engine 的媒体框架（Media Framework）提供了对 **Apple ProRes** 编解码器的原生支持。ProRes 是一种广泛应用于专业影视制作的高质量、有损视频压缩格式，常用于视频编辑和后期工作流。

该插件解决了在 Unreal Engine 中直接播放和导出 `.mov` 容器中的 ProRes 编码视频文件的问题，填补了引擎在苹果专业视频格式支持上的空白。它依赖并扩展了 WmfMedia 和 MovieRenderPipeline 模块的功能。

## 使用场景

- **影视后期制作**：当你的项目需要在 Unreal Engine 中预览或合成为 ProRes 格式渲染的视频素材时。
- **游戏过场动画/电影化内容渲染**：使用 Movie Render Pipeline 或类似工具导出过场动画时，希望输出为行业标准的 ProRes 格式以便于进一步的剪辑和调色。
- **苹果生态系统对接**：工作流需要与 Final Cut Pro 等苹果系专业视频软件无缝衔接，使用 ProRes 作为中间编码格式。

## 模块

此插件包含两个模块，共同实现完整的 ProRes 媒体处理能力。

| 模块 | 类型 | 说明 |
|---|---|---|
| `AppleProResMedia` | Runtime | 核心运行时模块，实现了 UE 媒体框架与 ProRes 编解码器之间的集成接口。 |
| `ProResToolbox` | External | 第三方外部库，提供了底层的 ProRes 编解码算法实现。 |

## 使用示例

### 蓝图用法

本插件主要扩展了媒体框架和影片渲染管线，不直接暴露特定的蓝图节点，而是通过通用的媒体播放和渲染输出 API 来使用。

- **播放 ProRes 视频**：使用 `MediaPlayer` 组件加载并播放包含 ProRes 轨道的 `.mov` 文件。
- **渲染输出为 ProRes**：在 `Movie Pipeline` 或 `Level Sequence` 的输出设置中，选择 ProRes 作为视频编码格式。

### C++ 用法

本插件的 C++ 使用方式主要是确保其模块在依赖链中被正确加载。开发者通常无需直接调用其内部 API，而是通过 UE 的媒体框架进行交互。

```cpp
// 在需要访问媒体功能的模块中，确保依赖已声明。
// Build.cs 文件中通常无需显式依赖本插件模块，因为它是媒体框架的扩展。
// 但你需要确保对 MediaAssets 等模块的依赖。

#include "MediaPlayer.h"
#include "MediaTexture.h"

// 示例：通过 C++ 创建媒体播放器并打开一个可能包含 ProRes 的媒体源。
UMediaPlayer* MediaPlayer = NewObject<UMediaPlayer>();
UMediaSource* MediaSource = /* 从资产或路径创建 */;
MediaPlayer->OpenSource(MediaSource);
```

## 模块依赖

你的项目或模块通常不需要直接依赖 `AppleProResMedia`。但要使此插件生效，项目必须启用并能正常加载以下插件/模块：

| 模块 | 用途 |
|---|---|
| `WmfMedia` | 提供 Windows 媒体基础（WMF）的媒体播放支持，本插件在此基础上实现 ProRes 解码。 |
| `MovieRenderPipeline` | 提供高质量的影片渲染管线功能，本插件在此基础上实现 ProRes 编码输出。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-18 | `d3e56b35` | MoviePipeline: Updated icons for MRG. | 更新了 Movie Render Graph 的相关图标。 |
| 2026-05-14 | `546ea87d` | MoviePipeline: Fixed several audio present in MRG. | 修复了 Movie Render Graph 中存在的多个音频问题。 |
| 2026-05-12 | `3af0fac2` | MoviePipeline: Added some telemetry for newly-added graph features, and existing MRQ/MRG features | 为新增的图功能以及现有的 MRQ/MRG 功能添加了遥测数据。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了在 64 位参数下使用 32 位格式说明符，反之亦然的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF。 |

### 维护评价

该插件创建于 2019 年，但**仍在活跃维护**。从近期提交历史可以看出，其维护工作紧密围绕其依赖的 `MovieRenderPipeline` 核心模块进行，包括功能更新、错误修复和代码质量改进。这表明 Epic 依然重视并维护着这条专业媒体处理路径。

插件默认未启用（`EnabledByDefault: false`），需要用户在项目设置中手动开启。它是一个功能明确、依赖清晰的专业工具，推荐在有特定 ProRes 媒体处理需求的影视或游戏开发项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/AppleProResMedia)
- [AppleProResMedia 模块文档](AppleProResMedia.md)
- [ProResToolbox 模块文档](ProResToolbox.md)