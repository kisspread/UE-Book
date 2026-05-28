# ML Deformer Nearest Neighbor Model (DEPRECATED)

> Nearest Neighbor Model for the ML Deformer Framework. This model has been deprecated. Please use the Detail Pose Model instead.

| 属性 | 值 |
|---|---|
| 中文名 | 最近邻ML变形模型（已废弃） |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NearestNeighborModel` (Runtime), `NearestNeighborModelEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel) | |

> ⚠️ **此插件已废弃**。自 UE 5.8 起，功能已迁移至 **Detail Pose Model**。请勿在新项目中使用此插件。

## 用途

这是一个基于 **最近邻（Nearest Neighbor）** 算法的机器学习变形器（ML Deformer）模型。它属于 ML Deformer 框架的一部分，通过在运行时查找与当前骨骼姿态最接近的预计算样本来驱动高质量的网格变形，主要用于将高精度的离线模拟/布料变形效果实时还原到游戏角色上。

该插件已被 Epic 标记为 DEPRECATED，官方推荐使用功能更完善的 **Detail Pose Model** 替代。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `NearestNeighborModel` | Runtime | 最近邻模型的核心运行时逻辑，包含模型资产定义、推理计算和编辑器数据支持 |
| `NearestNeighborModelEditor` | Runtime | 模型编辑器UI、训练图表管理、LOD选择和编辑器自定义属性面板 |

## 使用场景

- 你需要将高精度离线布料/肌肉模拟结果实时还原到游戏角色 → 使用 ML Deformer 框架，**但请选择 Detail Pose Model 而非本插件**
- 你正在维护一个使用了 NearestNeighborModel 的旧项目 → 本插件仍可工作，但建议逐步迁移到 Detail Pose Model

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- 子模块文档：[NearestNeighborModel](NearestNeighborModel.md) · [NearestNeighborModelEditor](NearestNeighborModelEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | MLDeformer 废弃清理，标记为已废弃 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移为新格式 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复变形器图运行时问题 |
| 2026-03-26 | `1bbb77b5` | Optimization to avoid creating duplicate section buffers in Optimus. | 优化避免重复创建缓冲区 |
| 2025-10-07 | `746137a4` | Refactored skinned mesh system to enable GPU skin support | 蒙皮网格系统重构以支持GPU蒙皮 |

### 维护评价

⚠️ **已废弃，不推荐使用。** 最新更新（2026-04-22）明确将该插件标记为 deprecated。尽管近期仍有 commit 涉及此目录，但均为全局性的废弃清理和代码重构，而非功能性维护。官方已推荐使用 **Detail Pose Model** 作为替代方案。新项目不应使用此插件，现有项目应规划迁移。