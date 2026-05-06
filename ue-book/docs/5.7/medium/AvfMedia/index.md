# AVF Media Player

> Implements a media player using Apple AV Foundation.

| 属性 | 值 |
|---|---|
| 中文名 | AVF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AvfMedia` (Runtime), `AvfMediaCapture` (Runtime), `AvfMediaEditor` (Editor), `AvfMediaFactory` (Editor, Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia) | |

## 总体用途

AVF Media Player 是专为 Apple 平台（iOS、macOS、tvOS）设计的媒体播放框架，基于原生 AV Foundation API 实现。它提供了高性能的本地媒体播放能力，支持视频（H.264、HEVC 等）、音频（AAC、MP3 等）以及字幕轨道播控。内置的捕获模块（AvfMediaCapture）还可用于从摄像头、屏幕等设备实时采集音视频数据。该插件是虚幻引擎“Media Framework”生态的 Apple 后端实现，编辑器模块（AvfMediaEditor、AvfMediaFactory）则负责媒体源资产的管理和播放器创建。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `AvfMedia` | Runtime | 核心播放器实现，提供播放控制、轨道选择、状态回调等基础功能 | [AvfMedia.md](AvfMedia.md) |
| `AvfMediaCapture` | Runtime | 媒体捕获模块，支持从摄像头、屏幕、麦克风等源实时采集 | [AvfMediaCapture.md](AvfMediaCapture.md) |
| `AvfMediaEditor` | Editor | 编辑器扩展，提供媒体源资产导入、检查、属性编辑 | [AvfMediaEditor.md](AvfMediaEditor.md) |
| `AvfMediaFactory` | Editor, Runtime | 媒体工厂，负责创建 `UMediaPlayer` 和 `UMediaSource` 实例，注册媒体格式支持 | [AvfMediaFactory.md](AvfMediaFactory.md) |

## 使用场景

- **播放本地视频文件** – 在 iOS/macOS 游戏中播放片头动画、过场视频或动态背景。
- **流媒体播放** – 通过 HTTP Live Streaming (HLS) 或自定义协议播放远程媒体。
- **摄像头/屏幕录制** – 利用 AvfMediaCapture 实时获取摄像头画面或屏幕截图，用于 AR、远程协作、录屏分享等。
- **媒体资产浏览** – 在编辑器中直接选择一个 `.mov` 或 `.mp4` 文件作为媒体源，快速预览并调整播放设置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia)
- [官方文档（论坛）](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/AvfMedia/Tests)（如果存在）