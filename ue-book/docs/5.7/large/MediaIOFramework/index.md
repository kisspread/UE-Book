# Media IO Framework

> Media Framework classes to support Professional Media IO used by the Virtual Production industry.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体IO框架 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GPUTextureTransfer` (Runtime), `MediaIOCore` (Runtime), `MediaIOEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-10-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework) | |

## 总体用途

Media IO Framework 是虚幻引擎面向虚拟制作和广播级实时媒体工作流的专业插件。它为接入专业视频硬件（如 AJA、Blackmagic 等采集/输出卡）提供了统一的框架，包括视频流的捕获、回放、GPU 纹理传输以及编辑器配置。该插件实现了低延迟、高可靠的媒体 IO 管线，是虚拟演播室、现场制作、LED 舞台等场景的核心依赖。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `GPUTextureTransfer` | Runtime | 提供 GPU 纹理的直接传输（基于 Vulkan RHI），优化视频帧送达渲染管线的效率。 |
| `MediaIOCore` | Runtime | 核心框架，定义媒体 IO 的基类（播放器、采集器、时钟同步等），供具体硬件插件扩展。 |
| `MediaIOEditor` | Editor | 编辑器模块，提供媒体 IO 属性的详细配置面板、设备选择 UI，集成到虚拟制作工具链中。 |

各模块的详细 API 与用法请参阅：
- [GPUTextureTransfer 模块文档](GPUTextureTransfer.md)
- [MediaIOCore 模块文档](MediaIOCore.md)
- [MediaIOEditor 模块文档](MediaIOEditor.md)

## 使用场景

- **虚拟制作 / LED 舞台**：将摄影机实时画面采集到引擎中，用于背景合成或相机跟踪。
- **现场直播与多机位切换**：同时捕获多路 SDI 输入，进行实时抠像、包装输出。
- **专业视频监控 / 回放**：对采集到的帧进行颜色校正（通过 OpenColorIO 插件配合）和 GPU 纹理传输。
- **自定义媒体硬件集成**：基于 `MediaIOCore` 扩展新的设备类型（如 SDI、NDI、IP 视频设备）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaIOFramework/Tests)（若存在）
- 官方文档：无专页，参见 [Virtual Production 文档](https://docs.unrealengine.com/5.7/en-US/virtual-production-in-unreal-engine/) 中媒体相关章节。