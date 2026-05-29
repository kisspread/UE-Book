# Actor Modifier Core

> Use modifier objects on actors to apply a custom behavior

| 属性 | 值 |
|---|---|
| 中文名 | Actor 修改器核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ActorModifierCore` (Runtime), `ActorModifierCoreBlueprint` (UncookedOnly), `ActorModifierCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore) | |

## 用途

ActorModifierCore 是一个**虚拟制片（Motion Design）工作流中的框架性插件**，旨在为 Actor 提供可组合、可复用的行为修改能力。

它**不是一个具体的修改器实现**，而是定义了如何创建和应用修改器的**核心系统**。该插件的核心价值在于解决虚拟制片场景下，需要频繁对多个 Actor 施加相同或类似逻辑（如统一调整材质参数、几何体变形等）的需求。通过修改器模式，开发者可以将复杂的行为封装为独立的修改器对象，附加到 Actor 上，实现行为的解耦、复用和顺序控制，从而高效迭代内容，避免大量蓝图或代码的重复编写。

## 使用场景

- **虚拟制片/动态设计 (Motion Design)**：在创建复杂的动态场景时，需要为大量 Actor（如克隆体、文字、几何体）批量应用相似的材质调整、位移变换或显示逻辑。
- **程序化内容生成 (PCG)**：作为 PCG 框架的补充，提供更细粒度的、可叠加的 Actor 后处理行为。
- **工作流自动化**：创建一套标准的修改器，确保场景中所有特定类型的 Actor 都遵循统一的行为规范，提高协作效率。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `ActorModifierCore` | Runtime | **核心运行时模块**。定义修改器的基础架构（`UActorModifierBase`）、生命周期管理、排序与执行逻辑。 |
| `ActorModifierCoreBlueprint` | UncookedOnly | **蓝图支持模块**。提供蓝图友好的 API 和函数库（`UActorModifierBlueprintLibrary`），便于在蓝图中创建、查询和操作修改器。 |
| `ActorModifierCoreEditor` | Editor | **编辑器集成模块**。提供编辑器内的可视化操作支持，例如在细节面板中管理 Actor 上的修改器堆栈。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/ActorModifierCore)
- （官方文档链接暂缺）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2d1c7712` | Motion Design: fixed issue where duplicating actors with modifiers and deleting those new duplicates | 修复了复制带有修改器的 Actor 后删除副本可能导致的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了可能导致格式化函数输出乱码的枚举作用域问题。 |
| 2026-04-14 | `abb26688` | Actor Modifiers: added experimental freeze modifier feature. | 为修改器新增了实验性的“冻结”功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 代码重构，统一日志宏。 |
| 2026-04-09 | `bdd66985` | Motion Design: made render state dirty reason optional + added some fixes to the text3d update | 优化渲染状态更新逻辑，并修复了文本3D组件的更新问题。 |

### 维护评价

该插件**处于活跃维护中**。
1.  **创建时间较短**：于 2025 年 5 月从 Experimental 目录迁移至 Virtual Production 目录，表明其已脱离实验阶段，成为正式工作流的一部分。
2.  **更新频繁**：近一个月内有多次功能性提交，内容涉及 bug 修复、新功能（冻结）和代码质量优化，表明开发团队正在积极使用和改进此框架。
3.  **定位清晰**：作为 Motion Design 工具链的基础组件，其存在与同目录下的 `ClonerEffector`, `PropertyAnimator` 等插件紧密关联，是虚拟制片核心工作流的一部分。
4.  **推荐使用**：如果你正在使用 UE5 的虚拟制片/Motion Design 工作流，或需要为 Actor 创建可管理的行为堆栈，此插件提供了强大而灵活的基础架构。注意观察其实验性功能（如“冻结”）的稳定进展。