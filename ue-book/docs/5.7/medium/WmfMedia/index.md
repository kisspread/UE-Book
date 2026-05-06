# WMF Media Player

> Implements a media player using the Windows Media Foundation framework.

| 属性 | 值 |
|---|---|
| 中文名 | WMF 媒体播放器 |
| 分类 | Media Players |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `WmfMedia` (Runtime), `WmfMediaEditor` (Editor), `WmfMediaFactory` (Editor, RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-04-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia) | |

## 总体用途

**WMF Media Player** 插件是 Unreal Engine 在 Windows 平台上的官方媒体播放器解决方案。它利用 Windows Media Foundation（WMF）框架实现对多种音视频格式的原生播放支持，包括 MP4、WMV、ASF 等。该插件为引擎的媒体框架（Media Framework）提供了标准化的播放器实现，使得蓝图和 C++ 项目可以通过通用媒体接口轻松控制媒体资源的加载、播放、暂停、跳转等操作，同时支持硬件加速解码（DX11/DX12）。

## 模块列表

| 模块 | 类型 | 一句话说明 | 文档 |
|---|---|---|---|
| `WmfMedia` | Runtime | 核心播放器模块，封装 WMF 会话管理、采样处理与纹理输出 | [WmfMedia.md](WmfMedia.md) |
| `WmfMediaEditor` | Editor | 编辑器集成，提供媒体播放器资源面板支持与预览设置 | [WmfMediaEditor.md](WmfMediaEditor.md) |
| `WmfMediaFactory` | Editor / RuntimeNoCommandlet | 媒体播放器工厂，负责在 Windows 平台创建 `WmfMediaPlayer` 实例并注册到引擎 | [WmfMediaFactory.md](WmfMediaFactory.md) |

## 使用场景

- 在 Windows 游戏中播放过场动画、视频背景或交互式视频内容。
- 基于 WMF 的硬件加速通道实现高帧率、低延迟的视频播放。
- 使用 Media Player 资产与 Media Texture 组件将视频渲染到 3D 表面（如 UI、世界网格体）。
- 需要调用原生 Windows 媒体能力（如视频录制、流式处理）的编辑器或运行时工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia)
- [官方文档](https://forums.unrealengine.com/showthread.php?46879-Media-Framework-Documentation-for-4-5-Preview)（论坛帖）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/WmfMedia/Source/WmfMedia/Private/Tests)