# NDI Media

> Implements media source and media output using NDI protocol

| 属性 | 值 |
|---|---|
| 中文名 | NDI 媒体插件 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、媒体配置） |
| 模块 | `NDIMedia` (Runtime), `NDIMediaEditor` (Editor), `NDIMediaRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia) | |

## 总体用途

NDI Media 插件为 Unreal Engine 提供了完整的 NDI（Network Device Interface）协议支持，使引擎能够作为 NDI 源发送画面，也可以作为接收器从网络接收 NDI 流。它集成在 UE 的媒体框架中，支持高分辨率、低延迟的实时视频传输，并具备 Alpha 通道传递、时间码同步、Just-in-Time 渲染等高级特性。该插件主要应用于虚拟制片、现场制作、远程协作等需要多机位或远程画面传输的场景。

> 该插件仍处于**实验性**阶段，EnabledByDefault 为 `false`，需手动启用。当前版本 1.0。

## 模块列表

| 模块 | 类型 | 一句话总结（详细文档） |
|---|---|---|
| `NDIMedia` | Runtime | 核心模块，实现 NDI 媒体源（接收）和媒体输出（发送）的底层逻辑。 → [NDIMedia 文档](NDIMedia.md) |
| `NDIMediaEditor` | Editor | 编辑器模块，提供 NDI 设备选择、参数配置 UI 及媒体配置文件编辑。 → [NDIMediaEditor 文档](NDIMediaEditor.md) |
| `NDIMediaRendering` | Runtime | 渲染模块，负责 NDI 流的 GPU 渲染、Alpha 通道处理及 Just-in-Time 渲染同步。 → [NDIMediaRendering 文档](NDIMediaRendering.md) |
| `NDISDK` | External (ThirdParty) | 外部 SDK 封装，包含 NDI 原生库及其平台适配。 → [NDISDK 文档](NDISDK.md) |

## 使用场景

- **虚拟制片 / 实时合成**：将 UE 渲染的画面通过 NDI 发送至导播台（如 vMix、 OBS），或将摄影机 NDI 信号接入 UE 作为实时背景。
- **多机位切换**：在同一局域网内，多台 UE 实例互相传输视音频，实现分布式渲染或画面共享。
- **远程审阅 / 协作**：导演或美术可以在另一台设备上低延迟观看 UE 视角，无需占用显卡输出。
- **后期同步**：利用 NDI 时间码（Timecode）将不同机器的画面与音频对齐。

## 依赖关系

使用此插件时，你的模块通常需要引入：

| 模块 | 用途 |
|---|---|
| `MediaIOFramework` | 媒体 I/O 框架，提供基础设备角色与时间码接口 |
| `NDISDK` | 外部 SDK（已在插件中打包） |

> 常见依赖如 `Core`, `Engine`, `Slate`, `UMG`, `InputCore` 等不再列出。

## 相关链接

- [源码仓库（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/NDIMedia)
- [NDIMedia 模块文档](NDIMedia.md)
- [NDIMediaEditor 模块文档](NDIMediaEditor.md)
- [NDIMediaRendering 模块文档](NDIMediaRendering.md)
- [NDISDK 模块文档](NDISDK.md)