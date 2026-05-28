# Media Stream

> Content/type agnostic chainable media proxy with media player integration.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体流代理 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产、蓝图接口） |
| 模块 | `MediaStream` (Runtime), `MediaStreamEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-10 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream) | |

## 用途

MediaStream 插件旨在提供一个**灵活且可扩展的媒体处理中间层**。传统的媒体播放管线（MediaPlayer）直接与具体的媒体源（如文件、流媒体）和渲染目标（MediaTexture）绑定。该插件通过引入一个“可链式代理”（Chainable Proxy）的概念，解耦了媒体内容的来源、处理与最终输出。

它解决的问题是：当你的项目需要动态切换不同的媒体源、在不改变播放器逻辑的情况下插入自定义的媒体处理逻辑（如转码、特效、缓存策略），或需要统一管理异构媒体内容时，传统管线会显得僵化。MediaStream 提供了一个抽象层，使得媒体流的消费和处理可以像管道一样灵活连接和配置。

## 使用场景

- **虚拟制片与媒体墙**：在 LED 体积或大型媒体显示项目中，需要动态、高效地加载和切换来自不同源头（实时渲染、预录视频、网络流）的媒体内容。
- **动态媒体应用**：构建交互式艺术装置、数字标牌或多内容展示应用，要求根据运行时条件（如用户交互、时间、数据）无缝切换媒体源，而无需销毁和重建播放器。
- **媒体处理管线**：在媒体到达渲染目标前，需要插入自定义处理步骤（例如，统一颜色空间、添加实时合成层、实施DRM解密或网络优化缓存策略）。

## 蓝图用法

作为实验性插件，其核心设计是模块化与可扩展性。详细的蓝图节点和使用方法，请参阅各子模块文档。

### 核心概念

| 概念 | 说明 |
|---|---|
| **MediaStream** | 核心运行时资产，代表一个可被播放的媒体流实例。它封装了源信息和处理链。 |
| **MediaStreamComponent** | Actor组件，负责管理MediaStream的生命周期并与UE的媒体播放系统集成。 |
| **MediaStreamSource** | 抽象接口，定义了媒体内容的来源（如文件、URL、媒体纹理捕获等）。 |
| **MediaStreamProcessor** | 抽象接口，定义了对媒体流数据进行的可链接处理操作。 |

*详细的蓝图节点（如 `Create Media Stream`、`Set Media Source`、`Connect Processor` 等）请查阅 [MediaStream模块文档](MediaStream.md)。*

## C++ 用法

### 头文件引入

```cpp
#include "MediaStream.h"
// 可能还需要包含特定的子模块头文件，例如源和处理器
```

### 基本用法（创建媒体流）

```cpp
// 1. 获取MediaStream子系统
UMediaStreamSubsystem* Subsystem = UGameplayStatics::GetGameInstance(this)->GetSubsystem<UMediaStreamSubsystem>();

// 2. 创建一个MediaStream实例
UMediaStream* MyStream = Subsystem->CreateMediaStream();

// 3. 设置一个媒体源（例如，从一个现有的MediaPlayer资产）
MyStream->SetSource(ExistingMediaPlayerAsset);

// 4. 将流连接到目标（如MediaTexture）
MyStream->SetRenderTarget(MyMediaTexture);

// 5. 播放
MyStream->Play();
```
*代码基于模块设计推断，请以实际API为准，参考 [MediaStream模块文档](MediaStream.md)。*

### 进阶用法（使用自定义处理器）

```cpp
// 假设你已经实现了一个自定义的MediaStreamProcessor
UMyColorCorrectProcessor* ColorProcessor = NewObject<UMyColorCorrectProcessor>();
ColorProcessor->Initialize(MyMediaStream);

// 将处理器插入到媒体流处理链中
MyStream->AddProcessor(ColorProcessor);
```

## 模块列表

| 模块 | 说明 |
|---|---|
| [`MediaStream`](MediaStream.md) | 核心运行时模块，提供媒体流代理、组件、源和处理器抽象，以及媒体子系统。 |
| [`MediaStreamEditor`](MediaStreamEditor.md) | 编辑器模块，提供资产编辑器、自定义细节面板和相关编辑器工具，用于开发和调试媒体流资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `6ba34f64` | [MediaStream] Revert Sample Queue approach; bind MediaTexture directly to player before opening | 回滚了采样队列方案，改为在打开媒体前直接将纹理绑定到播放器 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断到浮点数产生的警告 |
| 2026-05-12 | `4fc7c47c` | [MediaViewer] Fix drop-target image identification | 修复了媒体查看器中拖放目标图像的识别问题 |
| 2026-05-12 | `82b74724` | [MediaStream] Adding a cache setting override (like MediaPlate does) for using a local cache when us | 新增缓存设置覆盖选项（类似MediaPlate），以便在使用时启用本地缓存 |
| 2026-05-12 | `aa0f454d` | [MediaViewer] Implementing a Tile visibility provider for media viewer that support zooming, panning | 为媒体查看器实现了图块可见性提供者，支持缩放和平移操作 |

### 维护评价

- **维护活跃**：插件于2025年初创建，至今约1年。最近一次更新在2026年5月，近1个月内有**多次实质性提交**，涉及核心功能回滚与重构、性能优化（缓存）、编辑器工具改进和编译警告修复。
- **实验阶段**：插件标记为 `IsExperimentalVersion`，并且 `EnabledByDefault` 为 `false`。这表明它仍处于**积极开发与实验阶段**，API和功能可能会发生变化。
- **推荐使用**：该插件提供了一种高级的、面向未来的媒体处理架构。**推荐**用于对媒体管线灵活性有高要求的新项目或研究性原型中。**不推荐**用于对稳定性和长期API兼容性要求极高的生产项目中，除非你愿意跟进其更新并处理可能的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream)
- [MediaStream 运行时模块文档](MediaStream.md)
- [MediaStreamEditor 编辑器模块文档](MediaStreamEditor.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MediaStream/Tests)