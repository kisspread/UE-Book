# Image Plate

> Actor and component types that provide a camera-aligned image plate

| 属性 | 值 |
|---|---|
| 中文名 | 图像板 |
| 分类 | Rendering |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板） |
| 模块 | `ImagePlate` (Runtime), `ImagePlateEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-07-13 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate) | |

## 用途

该插件提供了一个`AImagePlate` Actor 和一个`UImagePlateComponent`组件，用于在 3D 世界场景中创建一个始终面向摄像机（或基于用户设置）的平面。它的核心功能是将一张 2D 图像（或视频）准确地叠加在 3D 场景的特定位置上，主要服务于影视和视觉特效（VFX）领域的合成工作流程，解决实景拍摄素材与 CG 元素匹配的问题。

## 使用场景

- **实景合成**：你需要将绿幕或蓝幕拍摄的演员素材，以正确的透视关系和遮挡关系，实时或离线合成到虚幻引擎创建的虚拟场景中。
- **虚幻摄像机内视觉特效 (In-Camera VFX)**：在使用 LED 棒拍摄时，用于在舞台环境内显示动态背景板，这些背景板需要跟随摄像机视角移动。
- **绿幕替代**：为虚拟制片设置中无法物理搭建的背景，提供基于图像的替代方案。
- **环境参考**：在场景中快速放置一张参考图（如概念图、实拍环境照片），用于辅助场景布局和光照匹配。

## 模块列表

- **ImagePlate (Runtime)**: 运行时核心模块，包含`AImagePlate`、`UImagePlateComponent`等关键类及渲染逻辑。
- **ImagePlateEditor (Editor)**: 编辑器模块，提供细节面板自定义、资产创建向导等编辑器增强功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `8d566979` | [ContentBrowser] New Add Menu Media Menu | 为内容浏览器添加了新的媒体相关菜单选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-03-25 | `d59d85d1` | [HWRT] Fix crash when UImagePlateComponent doesn't have a valid material assigned. | 修复了硬件光线追踪下，图像板组件未分配有效材质时导致的崩溃问题。 |
| 2026-02-06 | `af701dad` | [HWRT] Deprecate public FRayTracingGeometry Initializer. | 弃用了公共的 FRayTracingGeometry 初始化器，涉及光线追踪几何结构。 |
| 2025-10-08 | `018dadd6` | Changing a number of places that use implicit command lists to instead use the one already available | 优化了渲染命令列表的使用，将隐式列表替换为已有的可用列表。 |

### 维护评价

**维护中**。该插件创建于 2017 年，虽然仍标记为实验性（`IsBetaVersion=true`）且默认未启用，但其核心模块持续收到更新。从近期提交记录看，它正在积极适配新的引擎特性（如硬件光线追踪）和进行内部优化（日志宏迁移、命令列表优化）。尽管开发活跃，但其“实验性”状态意味着 API 可能变动，且功能集可能不完整。它适合在当前版本中用于原型验证或特定需求（如虚拟制片），但不推荐用于需要长期稳定性的生产项目，除非你愿意承担其潜在的变化风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) （虚幻引擎文档站，需搜索“Image Plate”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ImagePlate/Tests) （插件内可能存在的测试）