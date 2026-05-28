# Water

> Full suite of water tools and rendering techniques to easily add oceans, river, lakes or custom water bodies that carve landscape and interacts with gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 水体 |
| 分类 | Water |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、蓝图资产） |
| 模块 | `Water` (Runtime), `WaterEditor` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2020-10-22 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water) | |

## 用途

Water 插件为虚幻引擎提供了一套完整的水体解决方案。它解决了在游戏中添加逼真、可交互的海洋、河流、湖泊等水体，并使其与地形（Landscape）系统深度融合的复杂问题。插件的核心在于其运行时模块（`Water`）负责处理水体的渲染、碰撞、物理交互和材质；而编辑器模块（`WaterEditor`）则提供了创建和编辑水体几何体（如水体Spline）、配置水体属性以及管理水体与地形切割关系的强大工具集。其最终目标是让开发者能够高效地创建出视觉上吸引人且在游戏玩法层面具有深度交互性的水体环境。

## 使用场景

*   **开放世界游戏**：为大型地图添加动态的海洋、蜿蜒的河流和广阔的湖泊，并实现水面船只行驶、水下探索等玩法。
*   **地形改造**：创建河流或湖泊时，插件可以自动在景观（Landscape）上雕刻出河床或湖盆，实现水体与地形的无缝融合。
*   **环境交互**：水体可以与游戏中的物理对象、角色和Niagara粒子系统产生交互（如波浪、水流影响）。
*   **需要复杂水体艺术的项目**：通过材质和蓝图高度定制水面的外观，如平静的湖面、汹涌的激流或神秘的沼泽。

## 模块

| 模块 | 类型 | 简介 |
|---|---|---|
| `Water` | Runtime | 负责水体的运行时渲染、碰撞、物理交互、材质实例管理以及与Landscape的交互。 |
| `WaterEditor` | Editor | 提供在编辑器中创建、编辑水体Actor（如WaterBody, WaterZone）的工具、自定义面板和蓝图节点。 |

> ⚠️ **注意**：此插件为实验性功能（`IsExperimentalVersion=true`），默认未启用（`EnabledByDefault=false`）。使用前需在“插件”面板中手动启用，并可能需要重启编辑器。其实验性状态意味着API和功能在未来的引擎版本中可能发生不兼容的变更。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `5fd19ba7` | [Water] Trash the old ocean collision components to free up their path names so new components will | 清理旧的海洋碰撞组件，释放其路径名以便新组件使用。 |
| 2026-05-14 | `1e201bfa` | Fix UWaterSplineMetadata parallel-curve desync when Depth, WaterVelocityScalar, or AudioIntensity ar | 修复当深度、水流速度标量或音频强度变化时，水体Spline元数据平行曲线不同步的问题。 |
| 2026-05-12 | `dc876c8f` | [Water] Restored the behavior where if a water body has an unset material and "always generate water | 恢复了当水体材质未设置且“总是生成水网格体”选项开启时的行为。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为硬件光线追踪动态几何更新参数添加MeshBatchesView，并统一网格体批次所有权。（相关改进） |
| 2026-05-12 | `40da2015` | Only perform the water body static mesh conservative rasterization check if the static mesh is valid | 仅当静态网格体有效时，才执行水体静态网格体的保守光栅化检查。 |

### 维护评价

Water 插件创建于 2020 年，是一个相对成熟的**实验性**插件。从最近的提交记录（2026年5月）来看，Epic 仍在对其进行积极的维护和优化，修复了多个具体的使用问题和功能缺陷。这表明该插件虽然标签为“实验性”，但已达到一个相当可用的状态，并持续得到官方关注。

**综合建议**：
1.  **推荐尝试**：对于需要高级水体功能的新项目，该插件是 Epic 官方提供的最强大且持续维护的解决方案，值得尝试。
2.  **注意风险**：由于其“实验性”状态，在项目升级引擎版本时，需要密切关注该插件的更新日志，以防API变更导致兼容性问题。
3.  **依赖关系**：启用此插件将自动启用 `Landmass`、`Niagara`、`GeometryProcessing` 和 `BlueprintMaterialTextureNodes` 插件，增加了项目的依赖复杂度。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Water)
*   官方文档：暂无公开链接
*   测试用例：请参阅 [Water 模块文档](./Water.md) 和 [WaterEditor 模块文档](./WaterEditor.md) 中的用法示例。