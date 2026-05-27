# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体播放器 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

MediaPlate插件提供了一种在UE5中播放媒体（如视频）的完整解决方案，其核心是一个可放置在场景中的`AMediaPlate` Actor。它封装了复杂的媒体加载、解码和渲染流程，允许用户通过简单的属性设置（如媒体源路径、播放设置）和蓝图函数，在场景中的几何体上播放媒体内容。它解决了在3D环境中集成和控制视频播放的需求，是传统MediaFramework的高层封装和便捷扩展。

## 使用场景

- 你需要在游戏场景中创建一个播放预录制视频的电视屏幕或广告牌。
- 你需要为交互式装置或展厅项目制作一个可控的多媒体播放器。
- 你希望快速原型化一个具有媒体播放功能的场景，而无需手动构建复杂的媒体播放逻辑。

## 模块概览

- **MediaPlate** (Runtime): 提供核心的`AMediaPlate` Actor、媒体播放组件及底层管理逻辑，是插件的运行时核心。
- **MediaPlateEditor** (Runtime): 提供`AMediaPlate`在编辑器内的自定义细节面板、资产创建及播放预览功能。

详细API请参阅各子模块文档：
- [MediaPlate 模块文档](MediaPlate.md)
- [MediaPlateEditor 模块文档](MediaPlateEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版UE_LOG迁移到新版UE_LOGF。 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 编辑器中修复：防止在同一MediaPlate绑定下添加多个媒体轨道。 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the “material instance constant” code path. | 运行时功能增强：在材质实例常量路径中支持多个媒体纹理。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的查找替换操作。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回退一个变更。 |

### 维护评价

MediaPlate插件目前仍处于**Beta**状态（`IsBetaVersion: true`），表明其API和功能未来可能发生变化。从最近的提交记录看，插件在2026年4月仍有功能增强和错误修复，表明它**处于活跃开发与维护中**。其核心功能稳定，但作为Beta插件，在生产环境中使用需谨慎，并关注版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)