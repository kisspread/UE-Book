# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 游戏摄像机 |
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 插件旨在取代传统的 `CameraAnim`、`CameraComponent` 和 `CameraShake` 系统，提供一个**模块化、数据驱动**的摄像机系统。其核心设计思想是将摄像机行为（如摇摄、缩放、跟踪、震动）封装为可独立创建、组合和复用的**资产（Asset）**，而非硬编码在代码或组件中。

这个插件解决的主要问题是：
- **传统摄像机难以组合与扩展**： `UCameraComponent` 和 `ACameraActor` 的功能相对固定，难以在运行时动态混合多个摄像机效果。
- **缺乏可视化编辑与调试**： 复杂的摄像机动画逻辑难以用蓝图直观表达和调试。
- **数据驱动需求**： 期望摄像机行为可以像材料或动画蒙太奇一样，由设计师或艺术家在编辑器中独立创建、编辑和复用。

## 使用场景

- **制作复杂、电影化或可数据驱动的摄像机动画**： 用于过场动画、角色对话、Boss战演出、技能镜头特写等。
- **需要运行时动态混合多个摄像机效果**： 例如，角色在奔跑时同时应用手持摇晃、瞄准聚焦和受伤震动效果。
- **需要让设计师或艺术家独立编辑摄像机逻辑**： 通过自定义资产编辑器和节点化（Blueprint-like）界面，无需程序员参与即可调整摄像机行为。
- **项目需要标准化、可维护的摄像机系统**： 利用资产的组合性，避免蓝图或代码中充斥大量硬编码的摄像机逻辑。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `GameplayCameras` | Runtime | **核心运行时模块**，包含摄像机系统框架、资产类型定义、执行器（Executor）和混合器（Blender）等。 |
| `GameplayCamerasEditor` | Editor | **编辑器集成模块**，提供自定义资产编辑器、节点可视化编辑器、调试工具和资产工厂。 |
| `GameplayCamerasUncookedOnly` | UncookedOnly | **仅未打包模块**，包含仅在编辑器或开发构建中使用的功能，如蓝图节点或特定编辑器工具。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Cameras/GameplayCameras)
- [官方文档]()

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `671f5d81` | Camera: Fix camera variable overrides not working in PIE | 修复 PIE 中摄像机变量覆盖失效的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的双精度常量截断警告 |
| 2026-05-13 | `928a7f23` | Add or update descriptions to some trace channels. | 补充或更新部分追踪通道的描述信息 |
| 2026-04-28 | `1e68de2e` | GameplayCameras | 提交信息为模块名，可能为日常维护或小修复 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF |

### 维护评价

- **创建于 2020 年**，是一个**老古董**级别的插件。
- **近期维护活跃**：从 2026 年 4 月至 5 月有多次功能性更新和错误修复，表明仍在积极开发中。
- **实验性状态**：虽然默认启用，但 `IsExperimentalVersion` 标记为 `true`，意味着其 API 和功能未来可能发生**不兼容的变更**。
- **推荐使用**：如果你的项目需要强大、灵活且数据驱动的摄像机系统，并且愿意接受实验性 API 的潜在变动，这是一个非常值得采用和贡献的现代解决方案。建议密切跟踪其更新日志以应对未来变更。