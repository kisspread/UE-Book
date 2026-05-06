# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | VT编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-01-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

## 总体用途

VTCodecs 插件将 Apple 的 Video Toolbox 框架集成到 Unreal Engine 的 AVCodecs 系统中，使开发者能够在 macOS 和 iOS 平台上利用硬件加速的 H.264、H.265 (HEVC)、ProRes 等视频编解码能力。该插件是 AVCodecs 生态的一部分，为实时视频处理提供了高效的编解码方案。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| [VTCodecs](VTCodecs.md) | Runtime | 核心模块，封装 Video Toolbox 的编码器和解码器工厂，实现 AVCodecs 接口 |
| [VTCodecsRHI](VTCodecsRHI.md) | Runtime | RHI 适配模块，管理 GPU 纹理和 Metal 资源，支持编解码过程中的跨平台纹理共享 |

## 使用场景

- 开发需要硬件加速视频编解码的 macOS/iOS 应用，如视频会议、直播推流、视频播放器。
- 在虚幻引擎中利用 Apple 设备的高性能视频处理能力，进行实时的视频流输入或输出。
- 与 AVCodecs 系统结合，构建跨平台的视频编解码管线，并在 Apple 平台上启用 Video Toolbox 后端。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [VTCodecs 模块文档](VTCodecs.md)
- [VTCodecsRHI 模块文档](VTCodecsRHI.md)