# Blackmagic Media Player

> Implements input and output using Blackmagic Capture cards.

| 属性 | 值 |
|---|---|
| 中文名 | 黑魔法媒体 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BlackmagicCore` (Runtime), `BlackmagicMedia` (Runtime), `BlackmagicMediaEditor` (Runtime), `BlackmagicMediaFactory` (Runtime), `BlackmagicMediaOutput` (Runtime), `BlackmagicSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia) | |

## 用途

该插件为 Unreal Engine 提供了与 Blackmagic Design 专业级采集卡（如 DeckLink、UltraStudio）的深度集成。其核心目的是在**虚拟制片（Virtual Production）**、**实况转播**和**专业视频制作**工作流中，实现**低延迟、高精度、高可靠性的视频信号输入与输出**。

它解决了通用媒体框架无法充分利用 Blackmagic 硬件特性（如多通道支持、精确的硬件时间码、参考信号同步）的问题，并特别优化了在 Unreal Engine 的 nDisplay 多屏幕渲染和虚拟摄影机跟踪等场景中的表现。

## 使用场景

- **虚拟制片片场**：将 Unreal Engine 渲染的虚拟场景以极低延迟（<1 帧）输出到 LED 墙，并将现实摄影机的信号作为视频源输入，用于实时合成与监看。
- **多机位同步直播**：通过 Blackmagic 采集卡同时接入多路摄影机信号，在 UE 内部进行切换、合成，并输出干净信号。
- **精确的录制与回放**：利用 Blackmagic 硬件的时间码（LTC）和参考信号（Ref In），确保所有媒体资产（视频、音频、动画数据）拥有完美同步的时间码，便于后期制作。
- **自定义渲染节点**：在 nDisplay 环境中，为每个渲染节点配置独立的 Blackmagic 输出，用于驱动不同的物理显示器或投影仪。

## 模块列表

| 模块 | 说明 |
|---|---|
| `BlackmagicCore` | 核心模块，管理 Blackmagic SDK 的初始化、设备发现和底层资源。 |
| `BlackmagicMedia` | 媒体播放器核心实现，提供 `UBlackmagicMediaSource` (输入) 和 `UBlackmagicMediaPlayer`。 |
| `BlackmagicMediaFactory` | 媒体工厂模块，向引擎注册自定义的媒体源和播放器类型。 |
| `BlackmagicMediaOutput` | 提供 `UBlackmagicMediaOutput`，支持将引擎画面捕获并输出到 Blackmagic 设备。 |
| `BlackmagicMediaEditor` | 编辑器集成模块，提供设备选择、格式配置等 UI 和资产编辑器支持。 |
| `BlackmagicSDK` | 第三方 Blackmagic Desktop Video SDK 的封装与依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `fe681f84` | MediaIO: Fix Blackmagic auto-detect misinterpreting interlaced signals as progressive. | 修复自动检测功能将隔行信号误判为逐行信号的问题。 |
| 2026-05-26 | `36c08694` | Media IO - Populate Media Configuration when using auto for Blackmagic and Aja cards | 使用自动模式时，现在会正确填充 Blackmagic 和 AJA 卡的媒体配置信息。 |
| 2026-05-23 | `42746f7a` | Media IO: Added additional engine analytics information to various media players and capture and pro | 为各类媒体播放器和捕获工具添加了额外的引擎分析信息。 |
| 2026-05-12 | `b7bb4354` | Media IO - Fix bob deinterlacer field samples sharing source-frame timestamp | 修复了 Bob 反交错处理器中，场样本共享源帧时间戳的错误。 |
| 2026-05-12 | `b046e53d` | Virtual Production: Moved various VP assets to different asset categories, and migrated them to the | 虚拟制片：将多个虚拟制片资产迁移至新的资产类别。 |

### 维护评价

**活跃维护**。该插件自创建以来一直持续更新，最近在 2026 年 5 月仍有实质性功能增强和错误修复，表明 Epic Games 仍在积极维护此插件以支持其虚拟制片工作流。

- **优点**：作为 Epic 官方支持的专业级媒体插件，与引擎核心功能（如 nDisplay, Timecode）集成紧密，稳定性高。
- **缺点**：默认未启用，需要用户手动激活并确保硬件和驱动兼容性。插件功能高度专业化，非虚拟制片或专业视频用户可能无需使用。
- **推荐**：**强烈推荐**给所有使用 Blackmagic 硬件进行虚拟制片、实况制作或专业视频输出的用户。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/BlackmagicMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)