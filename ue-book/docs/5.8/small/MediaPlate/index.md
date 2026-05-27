# Media Plate

> Actor that can play media.

| 属性 | 值 |
|---|---|
| 中文名 | 媒体板块 |
| 分类 | Media |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MediaPlate` (Runtime), `MediaPlateEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-01-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate) | |

## 用途

MediaPlate 插件提供了一个媒体播放器 Actor（`AMediaPlate`），用于在场景中播放各类视频、音频等媒体内容。它是对 UE 媒体框架（Media Framework）的高级封装，简化了媒体在关卡中的集成和播放。插件包含运行时播放逻辑和对应的编辑器扩展，支持蓝图和 C++ 调用，旨在为游戏、影视、建筑可视化等项目提供便捷的媒体展示方案。

## 使用场景

- 在建筑可视化项目中，将视频或直播流作为屏幕内容播放。
- 在游戏关卡中，通过媒体播放器实现过场动画或环境广播。
- 需要在场景中放置可交互的媒体播放控制界面（如视频墙、电视）。
- 需要同步多个媒体播放器以实现联动播放效果。

## 模块说明

| 模块 | 说明 | 文档链接 |
|---|---|---|
| `MediaPlate` | 运行时模块，包含核心 `AMediaPlate` Actor 类及其播放、同步逻辑。 | [MediaPlate.md](MediaPlate.md) |
| `MediaPlateEditor` | 编辑器模块，提供媒体板块的资产编辑器、自定义细节面板和蓝图节点。 | [MediaPlateEditor.md](MediaPlateEditor.md) |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Media/MediaPlate)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/MediaFramework/Overview)
- [MediaPlate 模块文档](MediaPlate.md)
- [MediaPlateEditor 模块文档](MediaPlateEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移至 UE_LOGF。 |
| 2026-04-09 | `17c8eeed` | [MediaPlateEditor] Prevent adding multiple media tracks under the same media plate binding. | 在编辑器中防止在同一媒体板块绑定下添加多个媒体轨道。 |
| 2026-04-08 | `786c0a7e` | [MediaPlate] Support multiple media textures in the "material instance constant" code path. | 在材质实例常量代码路径中支持多个媒体纹理。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前错误的查找替换后的第二次提交。 |
| 2026-02-27 | `6759aa54` | [Backout] - CL51314860 | 回滚 CL51314860 的改动。 |

### 维护评价

MediaPlate 插件自 2022 年创建以来持续更新，最近一次更新在 2026 年 4 月，属于**活跃维护**。更新内容包括新功能（多纹理支持）、编辑器改进和代码优化。虽然插件标记为**实验性**（`IsBetaVersion = true`），但其稳定性和功能在持续完善中。鉴于其活跃的维护状态和明确的用途，推荐在需要媒体播放功能的项目中使用，但需留意其 Beta 标签可能带来的潜在变动。