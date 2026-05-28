# Electra Codecs

> Codecs for use with Electra player.

| 属性 | 值 |
|---|---|
| 中文名 | Electra 编解码器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ElectraCodecFactory` (Runtime), `ElectraDecoders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-04-03 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs) | |

## 用途

ElectraCodecs 为 UE5 的 Electra 媒体播放器提供底层音视频解码能力。它是一个插件化的编解码器工厂框架，将解码器的注册、发现与具体解码实现分离，使 Electra Player 能够支持 H.264、H.265/HEVC、VP8、VP9、AV1 等视频编解码格式以及 AAC 等音频格式。

该插件的存在解决了 Electra 播放器解码能力的模块化扩展问题——播放器本身不硬编码任何具体解码器，而是通过本插件的工厂机制动态获取合适的解码器实例。

**注意**：此插件默认未启用（`EnabledByDefault: false`）。使用 Electra 播放媒体时如需硬件/软件解码支持，需在项目设置中手动启用。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `ElectraCodecFactory` | Runtime | 编解码器工厂框架，负责解码器的注册、查询和实例化 |
| `ElectraDecoders` | Runtime | 具体解码器实现，包含 H.264、HEVC、VP8/VP9、AV1 视频解码器及 AAC 音频解码器 |

详细 API 文档：
- [ElectraCodecFactory](ElectraCodecFactory.md)
- [ElectraDecoders](ElectraDecoders.md)

## 使用场景

- 你在使用 Electra Player 播放网络流媒体或本地视频文件 → 启用本插件以获得编解码支持
- 你需要在 Android/iOS 上播放 HEVC 内容 → 本插件提供平台适配的解码路径
- 你需要播放 AAC 音频封装的媒体（如 HLS 流） → `ElectraDecoders` 提供 AAC 解码器
- 你需要自定义或扩展 Electra 的解码能力 → 通过 `ElectraCodecFactory` 的工厂接口注册自定义解码器

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 音频信号处理（ElectraDecoders 依赖） |
| `DirectX` | DirectX 图形/媒体接口（HEVC 等硬件解码路径） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `e86f17b3` | Use ConvertToTimescale for overflow-safe milliFPS computation | 使用安全的时间刻度转换避免毫秒帧率计算溢出 |
| 2026-05-13 | `4754a81b` | Fix Invalid Frame Rate for Android HEVC ingest without Third Party Encoder | 修复 Android 上无第三方编码器时 HEVC 输入帧率错误 |
| 2026-05-12 | `3bbffee9` | ElectraCodecs: Fixed HEVC DCR array extraction. Should not append to a single array but retain indiv | 修复 HEVC DCR 数组提取，保留独立数组而非合并为单个 |
| 2026-04-27 | `53a5ec2a` | ElectraCodecs: Permitting short form codec RFC for VP8 and VP9 codec | 允许 VP8 和 VP9 使用简写形式的编解码器 RFC 标识 |
| 2026-04-23 | `0cd64869` | ElectraDecoders: Fixed an issue where mp4a audio is wrapped inside a wave box in a QuickTime file. | 修复 QuickTime 文件中 mp4a 音频被 wave box 封装的解析问题 |

### 维护评价

**活跃维护**。该插件创建于 2023 年 4 月，虽仅约 3 年历史，但近期（2026 年 4-5 月）仍有密集的功能性修复和平台兼容性改进，涉及 HEVC、VP8/VP9、AAC 等多种编解码器。更新内容涵盖解码正确性修复、平台适配（Android）和协议兼容性提升，表明 Epic 持续投入维护。

作为 Electra 播放器的解码后端，该插件是 UE5 媒体框架的关键组件，推荐在需要 Electra 播放能力的项目中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/ElectraCodecs)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)