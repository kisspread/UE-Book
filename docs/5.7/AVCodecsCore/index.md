# AVCodecs Core

> Core Plugin for various Audio/Video codecs

| 属性 | 值 |
|---|---|
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AVCodecsCore` (Runtime), `AVCodecsCoreRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-01-25 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore) | |

## 用途

`AVCodecsCore` 是一个**底层框架插件**，旨在为 Unreal Engine 提供统一的音视频编解码器抽象层。它解决的核心问题是：为引擎提供一个标准化的接口，用于集成和管理各种第三方或平台原生的音频/视频编解码器（如 H.264, H.265, AAC, Opus 等），并处理与渲染硬件接口（RHI）的交互，以实现高效的硬件加速编解码。

它本身不包含具体的编解码器实现，而是定义了核心的接口、数据结构和管理框架，供其他具体的编解码器插件（如 `AVCodecsH264`）依赖和实现。

## 使用场景

-   你需要在项目中集成**硬件加速**的视频解码（例如，用于播放高质量的过场动画或实时视频流）。
-   你正在开发一个需要**跨平台**音视频处理功能的插件或模块，希望有一个统一的底层接口。
-   你需要为引擎添加对**新的编解码格式**的支持，并希望遵循引擎的标准架构。
-   你的项目涉及**媒体框架**的深度定制，需要直接操作编解码器的输入输出缓冲区和 RHI 资源。

## 模块列表

本插件包含两个核心模块，共同构成编解码器的基础设施：

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [`AVCodecsCore`](./AVCodecsCore.md) | Runtime | **核心抽象层**。定义了编解码器、编码器、解码器、媒体样本等基础接口和数据结构，是所有具体编解码器实现的基石。 |
| [`AVCodecsCoreRHI`](./AVCodecsCoreRHI.md) | Runtime | **RHI 集成层**。负责处理编解码器与渲染硬件接口（RHI）之间的交互，管理 GPU 资源（如纹理、缓冲区）的创建、映射和同步，是实现硬件加速的关键。 |

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/AVCodecsCore)
-   [AVCodecsCore 模块文档](./AVCodecsCore.md)
-   [AVCodecsCoreRHI 模块文档](./AVCodecsCoreRHI.md)