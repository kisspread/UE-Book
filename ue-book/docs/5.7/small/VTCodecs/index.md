# VTCodecs

> Adds codecs from the Apple Video Toolbox Framework to AVCodecs

| 属性 | 值 |
|---|---|
| 中文名 | Apple 编解码器 |
| 分类 | Codecs |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `VTCodecs` (Runtime), `VTCodecsRHI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-25 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs) | |

---

## 总体用途

VTCodecs 是 AVCodecs 框架的 Apple 平台适配层，利用系统 VideoToolbox 框架提供硬件加速的音视频编解码能力。它封装了 macOS/iOS 原生的编解码器（如 H.264、H.265/HEVC、VP9 等），使得 UE 的通用 AVCodecs 接口可以透明调用 Apple 硬件编解码器，实现低延迟、高性能的媒体处理。

该插件解决了跨平台媒体框架中 Apple 后端缺失的问题，使得开发者无需手动调用 VideoToolbox 原生 API，即可在 UE 中利用 Apple 芯片的硬件编码/解码能力。

---

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [VTCodecs](VTCodecs.md) | Runtime | 核心编解码器封装，提供 VideoToolbox 的编码/解码实例创建与配置 |
| [VTCodecsRHI](VTCodecsRHI.md) | Runtime | 与 RHI（渲染硬件接口）集成，支持编解码帧到 GPU 纹理的零拷贝传递 |

---

## 使用场景

- 在 Apple 设备上（macOS、iOS、tvOS）使用硬件加速实时视频编解码（如直播推流、视频通话、本地视频播放）。
- 需要将解码后的像素数据直接作为 UE 纹理使用，避免 CPU-GPU 拷贝（借助 VTCodecsRHI 模块）。
- 结合 AVCodecs 的通用接口，开发跨平台视频工具，在 Windows（NVIDIA/AMD）、Android（MediaCodec）和 Apple 之间平滑切换。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/AVCodecs/VTCodecs)
- [AVCodecs 框架文档（官方）](https://docs.unrealengine.com/5.4/en-US/avcodecs-in-unreal-engine/)（VTCodecs 作为其 Apple 后端子插件）