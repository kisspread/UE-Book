# HardwareEncoders

> Adds support of hardware encoders to AVEncoder

| 属性 | 值 |
|---|---|
| 中文名 | 硬件编码器 |
| 分类 | Encoders |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `EncoderAMF` (Runtime), `EncoderNVENC` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-14 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders) | |

## 用途

该插件为 `AVEncoder`（已废弃）提供硬件加速视频编码支持，包含两个独立运行时模块：

- **EncoderAMF** – 基于 AMD Advanced Media Framework（AMF）的硬件编码器，可在 AMD GPU 上实现低延迟、高性能的 H.264/H.265 编码。
- **EncoderNVENC** – 基于 NVIDIA NVENC API 的硬件编码器，可在 NVIDIA GPU 上实现硬件加速的视频编码（H.264/H.265）。

插件将硬件编码能力从引擎核心解耦，便于维护和独立更新。注意：`AVEncoder` 已在 2024 年标记为废弃，该插件本身仍处于 Beta 阶段，后续可能随引擎重构迁移。

## 模块列表

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `EncoderAMF` (Runtime) | 通过 AMD AMF 提供 AMD GPU 硬件视频编码 | [EncoderAMF.md](EncoderAMF.md) |
| `EncoderNVENC` (Runtime) | 通过 NVIDIA NVENC 提供 NVIDIA GPU 硬件视频编码 | [EncoderNVENC.md](EncoderNVENC.md) |

## 使用场景

- **直播推流** – 在 AMD 或 NVIDIA 显卡上使用硬件编码器减少 CPU 负载，提升推流帧率。
- **视频录制** – 对游戏画面或渲染输出进行硬件加速录制，降低对游戏性能的影响。
- **视频会议 / 远程协作** – 在实时通信场景中利用硬件编码降低延迟和码率。
- **内容创作** – 批量处理视频编码任务时，借助 GPU 加速大幅缩短等待时间。

## 相关链接

- [源码（HardwareEncoders 根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/HardwareEncoders)
- [UE 官方文档 - 硬件编码器（如需）](https://docs.unrealengine.com/)（本插件暂无独立官方文档）