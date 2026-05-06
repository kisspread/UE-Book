# Pixel Capture

> Framework for capturing pixel buffers in other formats while allowing for disconnected produce/consume rates.

| 属性 | 值 |
|---|---|
| 中文名 | 像素捕获 |
| 分类 | Graphics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例配置、内容资源） |
| 模块 | `PixelCapture` (Runtime), `PixelCaptureShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture) | |

## 总体用途

Pixel Capture 提供了一套用于捕获像素缓冲区并将其转换为其他格式的框架，支持生产者和消费者以解耦的速率运行（即 produce/consume 速率不同）。它专门为像素流送（Pixel Streaming）场景设计，能够从渲染输出、媒体管线或其他像素源抓取帧，并通过内部缓冲和回调机制传递给下游处理。同时依赖 MediaIO 框架实现媒体输入输出集成。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| [PixelCapture](PixelCapture.md) | **核心帧捕获引擎**：提供 `FPixelCapturePipeline`、`FPixelCaptureBuffer` 等基础设施，管理生产者/消费者缓冲池和帧生命周期。 |
| [PixelCaptureShaders](PixelCaptureShaders.md) | **着色器辅助处理**：封装 GPU 端颜色转换、缩放等像素操作（如 RGB→YUV），供捕获管道调用。 |

## 使用场景

- **开发基于 WebRTC 的像素流送应用**：使用 Pixel Capture 从 UE 视图抓取帧并转换为流式编码器所需的格式。
- **需要异步、解耦的像素数据生产/消费**：例如高帧率渲染与低帧率编码之间的速率匹配。
- **自定义媒体管线的帧源**：作为 BufferSource 将 UE 窗口内容输出到自定义媒体框架。

## 相关链接

- [源码（5.7 分支）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/PixelCapture)
- [官方文档 – Pixel Streaming](https://docs.unrealengine.com/en-US/Platforms/PixelStreaming/index.html)
- [模块详情：PixelCapture](PixelCapture.md)
- [模块详情：PixelCaptureShaders](PixelCaptureShaders.md)