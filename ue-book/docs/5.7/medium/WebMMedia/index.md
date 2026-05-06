# WebM Video Player

> WebM video player plugin for Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | WebM 视频播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `WebMMedia` (Runtime), `WebMMediaEditor` (Runtime), `WebMMediaFactory` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia) | |

---

## 总体用途

WebM Video Player 是一个实验性媒体播放器插件，为 Unreal Engine 添加 **WebM 容器格式** 的原生播放能力。它基于开源库 `libwebm`（解析 WebM/Matroska）和 `libvpx`（解码 VP8/VP9 视频），支持 Vorbis/Opus 音频解码，解决了引擎默认不支持 WebM 视频流的问题。该插件主要用于需要播放 WebM 格式视频的媒体播放器资产、虚拟现实内容或游戏内过场动画等场景。

---

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [WebMMedia](WebMMedia.md) | Runtime | 核心播放器模块，负责 WebM 流解析、音视频解码、帧同步与渲染。 |
| [WebMMediaEditor](WebMMediaEditor.md) | Runtime | 编辑器集成模块，提供 WebM 媒体源配置界面与自定义属性面板。 |
| [WebMMediaFactory](WebMMediaFactory.md) | Runtime | 媒体源工厂模块，负责创建 `UWebMMediaPlayer` 并将其注册到引擎媒体框架。 |

---

## 使用场景

- 需要在项目中播放 `*.webm` 格式视频（如 VP8/VP9 + Vorbis/Opus）。
- 利用现有的 WebM 素材库制作游戏内 cinematics、UI 动画或 VR 背景视频。
- 实验性项目探索新的视频格式支持，作为自定义媒体管线的参考。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WebMMedia/Tests)