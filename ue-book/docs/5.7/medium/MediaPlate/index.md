# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体板 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate) | |

## 总体用途

Media Plate 插件提供了一个可在世界中直接放置的 Actor，用于播放媒体源（如视频、音频）。它将媒体播放功能与直观的编辑器操作相结合，允许开发者在场景中快速添加一个始终面向摄像机的平面（或自定义网格体），并将媒体内容实时渲染到其表面。适用于虚拟制片参考回放、动态广告牌、交互式展示等场景。

## 模块列表

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| `MediaPlate` | Runtime | 核心模块：实现 `AMediaPlateActor` 和 `UMediaPlateComponent`，负责媒体播放、网格体更新和编辑器内播放控制。 | [MediaPlate.md](./MediaPlate.md) |
| `MediaPlateEditor` | Runtime | 编辑器扩展：提供自定义细节面板、播放控制按钮（播放/暂停/步进）、多用户同步支持及“Hidden In Game”选项的材质修复。 | [MediaPlateEditor.md](./MediaPlateEditor.md) |

## 使用场景

- **虚拟制片参考**：在场景中放置一个平面，播放参考视频，方便导演和摄影师对照。
- **动态标牌与广告**：在展览或游戏中展示动态媒体内容，无需手动切换材质。
- **媒体预览**：在关卡设计时直接预览媒体素材的播放效果，提高迭代效率。
- **教学与演示**：在场景内嵌教学视频，辅助用户操作。

## 相关链接

- [源码（GitHub）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/MediaPlate)
- [官方文档 - 媒体框架](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [MediaPlate 模块文档](./MediaPlate.md)
- [MediaPlateEditor 模块文档](./MediaPlateEditor.md)