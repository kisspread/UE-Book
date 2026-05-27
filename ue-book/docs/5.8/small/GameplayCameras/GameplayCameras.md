# Gameplay Cameras

> A modular and data-driven camera system for Unreal

| 属性 | 值 |
|---|---|
| 中文名 | 模块化游戏摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、编辑器图表工具） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Runtime), `GameplayCamerasUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 概述

本文档为大型插件（729 源文件），按子模块拆分为多页文档：

| 子文档 | 内容 |
|---|---|
| [Core 系统](#core-系统) | 汇总页，系统架构、模块列表、维护状态 |
| [Camera Rig](camera-rig.md) | 摄像机骨架资产：节点树、变量、参数接口 |
| [Camera Director](camera-director.md) | 摄像机导演：Blueprint 导演、代理资产 |
| [Camera Nodes](camera-nodes.md) | 内置摄像机节点：混合、碰撞、构图、蓝图节点 |
| [Evaluation Pipeline](evaluation-pipeline.md) | 评估管线：求值上下文、系统求值器、混合栈 |
| [Blueprint Integration](blueprint-integration.md) | 蓝图集成：组件、评估数据、Pose |
| [Game Framework](game-framework.md) | 游戏框架：PlayerCameraManager、摄像机动作、震动 |

## Core 系统

### 用途

GameplayCameras 是 UE5 中新一代的**模块化、数据驱动摄像机系统**，旨在替代传统的 `APlayerCameraManager` + `UCameraComponent` 架构。它解决了以下问题：

- **传统摄像机系统难以复用**：新系统通过 `UCameraRigAsset`（摄像机骨架资产）将摄像机行为封装为可复用的数据资产，而非硬编码的 C++ 类
- **摄像机切换不够灵活**：通过 `UCameraDirector`（摄像机导演）和 `UCameraRigTransition`（过渡）提供声明式的摄像机切换规则和混合控制
- **参数驱动不足**：完善的参数系统支持通过变量表（`FCameraVariableTable`）和上下文数据表（`FCameraContextDataTable`）在运行时动态驱动摄像机行为
- **蓝图可定制性差**：`UBlueprintCameraNode` 和 `UBlueprintCameraDirector` 允许纯蓝图实现自定义摄像机逻辑
- **摄像机分层管理缺失**：支持 Main/Global/Visual/Base 多层混合栈，每层独立管理摄像机骨架的生命周期

**核心架构**：Camera Asset → Camera Director → Camera Rig → Camera Node Tree → Evaluator，形成完整的数据驱动摄像机管线。

### 使用场景

- 你在做一个第三人称动作游戏，需要复杂的肩后视角 + 过场切换 → 使用 `UCameraRigAsset` 定义肩后摄像机，在 `UCameraDirector` 中管理不同状态的切换
- 你需要实现瞄准时 FOV 缩放、摄像机碰撞避让 → 使用内置节点（Zoom、CollisionPush）组装到摄像机骨架节点树中
- 你需要让策划通过数据资产自定义摄像机行为，而非每次都要程序员改代码 → 数据驱动的参数系统 + 编辑器图表工具
- 你需要在一个 PlayerController 下同时运行多个摄像机效果层（如基础视角 + 全局震动 + 视觉层特效） → 多层混合栈（Main/Global/Visual）
- 你需要纯蓝图实现一个特殊玩法的摄像机（如赛车回放视角） → `UBlueprintCameraNode` + `UBlueprintCameraDirector`

### 模块依赖

该插件依赖 `EnhancedInput`，无其他特殊依赖。

### 维护状态

#### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 模式下摄像机变量覆盖不生效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 为部分追踪通道添加或更新描述 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 通用提交（无详细描述） |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |

#### 维护评价

- **创建时间**：2020 年 10 月，约 6 年历史
- **更新频率**：近期（2026 年 4-5 月）仍有活跃提交，包含 bug 修复和代码质量改进
- **实验性状态**：`IsExperimentalVersion = true`，但仍默认启用，说明 Epic 认为已足够稳定
- **代码规模**：729 个源文件，属于大型插件，架构成熟
- **依赖**：依赖 `EnhancedInput`，与 UE5 输入系统深度集成
- **推荐程度**：⚠️ **谨慎使用**——虽然是默认启用的实验性插件，代码质量高且持续维护，但实验性标签意味着 API 可能在未来版本中有 breaking changes。适合新项目或愿意跟进更新的项目采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()（暂无）