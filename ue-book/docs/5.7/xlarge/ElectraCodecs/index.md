# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 编解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraDecoders` (Runtime), `ElectraCodecFactory` (Runtime), `ElectraCodecFactory` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-09-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs) | |

## 用途

该插件为 [Electra 多媒体播放器](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview) 提供底层的音视频编解码能力。它封装了各平台的硬件/软件解码器（Windows 的 Media Foundation、Android 的 MediaCodec、Apple 的 VideoToolbox 等），支持常见格式如 H.264/H.265 视频解码以及 AAC、MP3 等音频解码。通过 `ElectraDecoders` 模块实现具体解码逻辑，`ElectraCodecFactory` 模块提供统一的工厂接口以创建和管理解码器实例，从而与 Electra 播放器的管线上层解耦。

## 使用场景

- 项目中使用了 **ElectraPlayer** 插件（或其衍生产品）播放网络流（HLS、DASH、MP4 等）时，需要此插件来提供解码能力。
- 需要利用平台原生硬件加速解码以降低 CPU 占用、提高播放流畅度。
- 自定义解码管道或测试新的编解码器时，可通过 `ElectraCodecFactory` 注册自定义解码器。

## 模块文档

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `ElectraDecoders` | 音视频解码器核心实现，封装并管理各平台的原生解码器（如 MF、MediaCodec、VideoToolbox） | [ElectraDecoders.md](./ElectraDecoders.md) |
| `ElectraCodecFactory` | 编解码器工厂，提供统一的接口来创建、注册、销毁解码器实例，同时支持编辑器下的预览与调试 | [ElectraCodecFactory.md](./ElectraCodecFactory.md) |

## 维护状态

该插件于 2025 年 9 月创建，属于较新的组件。从近期 Git 提交看（2025-09-11 至 2025-09-24），主要集中在 `ElectraDecoders` 的 bug 修复（如 D3D12 错误处理、JNI 异常崩溃修复）以及 `ElectraUtil` 的优化。开发团队活跃维护中，推荐在需要 Electra 播放能力的项目中启用。

> ⚠️ 注意：默认不启用，需在 **Plugins** 面板中手动勾选 **Electra Codecs**，并确保已启用 `ElectraUtil` 插件（作为依赖自动启用）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/ElectraCodecs)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)