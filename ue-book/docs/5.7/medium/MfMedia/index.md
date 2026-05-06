# Media Foundation Media Player

> Implements a media player using the Microsoft Media Foundation framework. Requires Xbox One or Windows 7 and higher.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体基础播放器 |
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MfMedia` (Runtime), `MfMediaEditor` (Editor), `MfMediaFactory` (Runtime/Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia) | |

---

## 总体用途

MfMedia 插件为 Unreal Engine 提供了基于 **Microsoft Media Foundation** 框架的媒体播放能力。它允许在 Windows 平台上播放各种常见媒体格式（如 MP4、WMV、AAC 等），是 UE 媒体框架的标准 Windows 后端之一。该插件集成了播放控制、缓冲状态通知、时序关联等核心功能，适用于需要内嵌视频播放的游戏、影视可视化或多媒体交互应用。

---

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| MfMedia | Runtime | 核心播放逻辑：实现 Media Foundation 的流读取、解码、播放控制及事件回调。 | [MfMedia.md](MfMedia.md) |
| MfMediaEditor | Editor | 编辑器设置与平台验证：提供播放器的编辑器配置窗口及平台可用性检查。 | [MfMediaEditor.md](MfMediaEditor.md) |
| MfMediaFactory | Runtime / Editor | 媒体播放器工厂：根据平台创建设备兼容的播放器实例，并注册到媒体框架。 | [MfMediaFactory.md](MfMediaFactory.md) |

---

## 使用场景

- **Windows 游戏内视频播放**：在界面或过场动画中嵌入 MP4/WMV 等格式视频，使用 Media Player 组件配合 MfMedia 播放器。
- **多媒体预览工具**：在编辑器或运行时需要预览本地媒体文件，借助 MfMedia 的缓冲与播放控制。
- **直播流或点播场景**：利用 Media Foundation 的源解复用器支持 HTTP/RTSP 流媒体（取决于系统装好相应解码器）。
- **与 UE Media Framework 配合**：作为 `UMediaPlayer` 的底层实现之一，通过 `MediaPlayer->OpenSource(MediaSource)` 即可自动调用。

> **注意**：该插件默认不启用，需在项目设置中手动启用；且仅在 Windows 7+ 或 Xbox One 平台有效。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [模块文档](MfMedia.md)（核心播放器）
- [模块文档](MfMediaEditor.md)（编辑器设置）
- [模块文档](MfMediaFactory.md)（工厂注册）