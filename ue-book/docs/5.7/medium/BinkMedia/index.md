# Bink Media

> Implements a media player using Bink.

| 属性 | 值 |
|---|---|
| 中文名 | Bink 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `BinkMediaPlayer` (Runtime), `BinkMediaPlayerEditor` (Editor), `BinkMediaPlayerSDK` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-07-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia) | |

## 总体用途

Bink Media 是 Epic Games 为 Unreal Engine 5 提供的第三方视频格式支持插件，基于 RAD Game Tools 的 Bink 视频编解码器。该插件实现了一个媒体播放器，能够在游戏中高效播放 Bink 格式的视频（如过场动画、UI 背景等），并针对 UE5 的渲染管道进行了深度集成（RHI、Renderer、桌面小部件等）。

**核心价值**：Bink 格式在游戏行业中广泛使用，以极高的压缩率和硬件解码性能著称。该插件将 Bink 视频无缝接入 UE5 的媒体框架，支持预加载屏幕、多平台部署（排除 tvOS 和 Server），并提供蓝图/C++ 调用接口。

## 模块列表

| 模块 | 一句话总结 | 详情文档 |
|---|---|---|
| `BinkMediaPlayer` (Runtime) | 运行时核心模块，提供媒体播放器、纹理输出和 PreLoadingScreen 集成 | [BinkMediaPlayer.md](BinkMediaPlayer.md) |
| `BinkMediaPlayerEditor` (Editor) | 编辑器模块，扩展媒体控制面板，支持 Metal RHI 预览 | [BinkMediaPlayerEditor.md](BinkMediaPlayerEditor.md) |
| `BinkMediaPlayerSDK` (External) | 第三方 SDK 封装，处理 Bink 格式解码、文件 I/O 和平台适配 | [BinkMediaPlayerSDK.md](BinkMediaPlayerSDK.md) |

## 使用场景

- **过场动画播放**：在游戏启动、关卡过渡或剧情章节中使用 Bink 视频作为预渲染动画。
- **UI 背景视频**：在菜单、加载界面或商店中循环播放 Bink 格式的背景视频。
- **PreLoadingScreen 集成**：利用 `PreLoadingScreen` 模块在资源加载期间显示 Bink 视频，优化玩家体验。
- **多平台发布**：需要为 Windows、Mac、Linux、iOS、Android、Xbox、PlayStation 等平台提供统一视频体验，同时避免 tvOS（已排除）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/BinkMedia)
- [模块文档 - BinkMediaPlayer](BinkMediaPlayer.md)
- [模块文档 - BinkMediaPlayerEditor](BinkMediaPlayerEditor.md)
- [模块文档 - BinkMediaPlayerSDK](BinkMediaPlayerSDK.md)