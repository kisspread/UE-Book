# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画重定向操作模块） |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

这是一个专注于动画重定向过程中保持空间关系的插件集合。当将动画从一个骨骼网格体重定向到另一个时，简单的骨骼映射往往会导致空间关系错乱（如角色脚部穿模、手部抓取位置偏移等）。此插件提供了一系列“重定向操作”（Retarget Ops），通过空间感知算法，在重定向过程中调整动画数据，以保持角色与环境、道具之间的正确交互关系，从而避免穿模、滑步、抓取错位等问题。

它解决的核心问题是：**在不同比例、不同骨架的动画重定向中，如何保持关键的物理空间交互（如脚部接触地面、手部抓取道具）的正确性**。

## 模块列表

本插件由五个运行时模块组成，各司其职：

| 模块 | 用途简述 |
|---|---|
| `BodyIntersectIKOp` | 处理角色身体与场景物体相交的IK（反向运动学）操作，主要用于防止穿模。 |
| `PreviewPropOp` | 提供在编辑器中预览道具交互效果的操作。 |
| `RelativeBodyAnimInfo` | 存储和管理“相对身体动画信息”，即描述身体各部位相对位置和旋转的数据结构。 |
| `RelativeBodyAnimUtils` | 提供处理相对身体动画数据的工具函数库。 |
| `RelativeIKOp` | 核心模块，执行基于相对空间关系的IK重定向操作。 |

## 使用场景

- **角色与环境交互动画**：当需要将角色A的行走、攀爬、跳跃动画重定向给体型、比例完全不同的角色B时，使用本插件确保角色B的脚部依然能正确接触地面，避免悬空或穿入地面。
- **道具交互动画**：将一个角色抓取、使用道具的动画重定向给另一个角色时，确保重定向后的手部位置依然能正确抓取或对准原设计中的道具位置和方向。
- **大规模动画资产迁移**：在项目需要为多个不同体型的角色复用同一套动画资源时，使用本插件作为重定向流程中的关键步骤，以减少手动调整的工作量。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为重定向操作中的标量TArray属性添加不可覆盖元数据，增强数据保护。 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版日志宏，统一日志规范。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏迁移至新版日志宏，统一日志规范。 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具相交推出（Prop Intersection Pushout）逻辑中的错误。 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 实现或改进了道具交互中的推出算法。 |

### 维护评价

- **状态**: **活跃维护中**。虽然插件创建于约1年前（2025-07），但从git记录看，最近一次更新在2026-04-23，说明仍在持续开发和修复。
- **成熟度**: 作为实验性插件（`IsExperimentalVersion=true`），其API和功能可能在未来版本中发生变化。近期的更新集中在日志规范化和功能修复上，表明其正在从早期开发向稳定版本过渡。
- **推荐度**: 对于有复杂动画重定向需求，且常规重定向器无法满足空间保持要求的项目，可以**实验性采用**。但由于其为实验性插件，建议在使用前进行充分测试，并准备好应对未来可能的API变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- [官方文档]() （暂无）
- [测试用例]() （路径未提供，通常位于插件目录下的`Tests`文件夹中）