# RTSP Media

> Real-time media streaming via the RTSP protocol

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（媒体资产） |
| 模块 | `RTSPMedia` (Runtime), `RTSPMediaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia) | |

## 用途

本插件为 Unreal Engine 5 提供了通过 RTSP (Real Time Streaming Protocol) 协议接收和播放实时媒体流的能力。它解决了引擎原生媒体框架不支持 RTSP 协议的问题，使得开发者能够将安防摄像头、视频会议系统、直播推流等基于 RTSP 的实时视频源无缝集成到 UE5 项目中，用于监控可视化、远程协作、虚拟制作等场景。

## 使用场景

- **安防监控集成**：将工厂、园区或城市的实时监控摄像头画面接入 UE5，用于数字孪生或可视化大屏。
- **视频会议接入**：在虚拟会议或远程协作应用中，接入来自 Zoom、Teams 等支持 RTSP 输出的视频流。
- **直播推流预览**：在直播或虚拟制作流程中，预览来自编码器或导播台的实时 RTSP 流。
- **媒体内容测试**：快速测试和验证基于 RTSP 协议的媒体播放功能。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [RTSPMedia](RTSPMedia.md) | Runtime | 核心运行时模块，负责 RTSP 连接、流媒体解复用、解码和播放。 |
| [RTSPMediaEditor](RTSPMediaEditor.md) | Editor | 编辑器集成模块，提供媒体源资产的创建和编辑器内的播放预览功能。 |

### 近期更新

- 2026-04-20 `3ed2062b` ElectraDecoders: modernized the decoder factory to be more usable for other clients
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-04-10 `e18acf19` More unreachable code warning fixes
- 2026-03-25 `160bc52a` [RTSPMedia] Enable bProvideCpuBuffer by default
- 2026-03-20 `1330a56b` [RTSPMedia] Add Provide CPU buffer option

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/RTSPMedia)