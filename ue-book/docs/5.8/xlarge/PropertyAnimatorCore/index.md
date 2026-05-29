# Property Animator Core

> Re-usable behaviors to control properties at runtime and in editor

| 属性 | 值 |
|---|---|
| 中文名 | 属性动画核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `PropertyAnimatorCore` (Runtime), `PropertyAnimatorCoreEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore) | |

## 用途

这是一个用于在运行时和编辑器中控制对象属性动画的**基础框架插件**。它提供了可重用的行为和核心系统，允许开发者在不编写底层代码的情况下，通过蓝图或编辑器工具驱动各种对象属性的变化。

**解决什么问题**：在虚拟制片（Virtual Production）、建筑可视化或动态演示项目中，经常需要同步、驱动或动画化大量对象的各种属性（如位置、旋转、缩放、材质参数等）。此插件提供了一套标准化的机制来管理这些属性动画。

**为什么存在**：它作为其他更具体属性动画插件（如 `PropertyAnimator`）的**核心基础**，将通用的动画逻辑、数据结构和接口抽象出来，便于扩展和维护。它是 Epic Games Motion Design 工具链的一部分。

## 使用场景

- 你需要在虚拟制片环境中，批量、程序化地控制场景中物体的属性变化。
- 你正在开发编辑器扩展或运行时工具，需要为不同类型的属性（Transform、颜色、数值等）提供统一的动画驱动接口。
- 你希望基于 OperatorStack 或其他 Motion Design 插件构建更复杂的属性动画逻辑，此插件提供底层支持。

## 模块列表

| 模块 | 用途 |
|---|---|
| `PropertyAnimatorCore` | **运行时核心模块**。定义属性动画的核心数据结构、接口和运行时行为。 |
| `PropertyAnimatorCoreEditor` | **编辑器扩展模块**。在核心模块基础上，提供编辑器专属的 UI、工具和资产类型支持。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)
- [子模块文档：PropertyAnimatorCore](PropertyAnimatorCore.md)
- [子模块文档：PropertyAnimatorCoreEditor](PropertyAnimatorCoreEditor.md)
- 依赖插件：[OperatorStack](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/OperatorStack)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中可能导致输出混乱的问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，统一日志格式。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd | 废弃了接受 `bIncludeNestedObjects` 布尔参数的 `GetObjects*` 和 `ForEachObjectWithOuter` 函数，并引入新的替代接口。 |
| 2025-12-19 | `a01aeeaa` | check for UObjectInitialized && !IsEngineExitRequested() before running clean-up code that involves | 在运行涉及 UObject 的清理代码前，增加了对引擎是否已初始化且未在退出的检查，提升稳定性。 |
| 2025-11-18 | `36825f29` | Motion Design: corrected log verbosity from Log to Verbose for logs that were constantly outputting | 将一些频繁输出的日志的详细程度从 `Log` 级别更正为 `Verbose`，减少日志刷屏。 |

### 维护评价

**维护状态：活跃维护中**

- **创建时间**：插件于 2025 年 5 月创建，至今约 1 年，属于较新的工具。
- **更新频率**：从 Git 历史看，在 2025 年末至 2026 年 4 月期间有**持续的功能更新和稳定性修复**，最近一次更新在 2026 年 4 月 28 日。
- **更新内容**：近期更新包括日志系统优化、API 废弃与重构、枚举修复和初始化检查，表明插件在积极进行**代码维护、优化和迭代**。
- **推荐使用**：该插件是 Epic 官方 Virtual Production 工具链的一部分，对于需要属性动画驱动的项目，特别是使用 Motion Design 工作流的，**推荐使用**。它提供了稳定的核心基础。