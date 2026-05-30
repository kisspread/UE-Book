# UMG Viewmodel

> A plugin to support the Model-View-Viewmodel pattern in UMG.

| 属性 | 值 |
|---|---|
| 中文名 | MVVM框架 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ModelViewViewModel` (Runtime), `ModelViewViewModelAssetSearch` (Runtime), `ModelViewViewModelBlueprint` (Runtime), `ModelViewViewModelDebugger` (Runtime), `ModelViewViewModelDebuggerEditor` (Runtime), `ModelViewViewModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-04-01 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel) | |

## 用途
该插件为 Unreal Motion Graphics (UMG) UI 框架提供了 Model-View-Viewmodel (MVVM) 设计模式的官方实现。它旨在解决复杂UI应用中的逻辑与表现分离问题，通过引入 ViewModel 层作为 Model（数据）和 View（UI控件）之间的中间代理，使UI逻辑更清晰、可测试且易于维护。这避免了在蓝图或控件蓝图中编写过于复杂和耦合的逻辑。

## 使用场景
- **数据驱动的复杂 UI**：当你在制作一个需要频繁更新显示（如RPG角色属性、背包物品、聊天窗口）且逻辑复杂的UI时。
- **团队协作与测试**：当项目需要将UI逻辑（ViewModel）与游戏逻辑（Model）和视觉表现（View）解耦，方便不同工种分工或进行单元测试时。
- **追求架构清晰**：希望UI开发遵循更结构化、更易于理解和扩展的架构模式。

## 模块列表

| 模块 | 说明 |
|---|---|
| `ModelViewViewModel` | 核心运行时框架，提供 MVVM 模式的核心类与接口。 |
| `ModelViewViewModelBlueprint` | 提供蓝图集成，允许在蓝图中创建和使用 ViewModel。 |
| `ModelViewViewModelEditor` | 提供编辑器内支持，例如创建 ViewModel 资产的向导。 |
| `ModelViewViewModelDebugger` | 运行时调试器，用于在运行时检查 ViewModel 的状态。 |
| `ModelViewViewModelDebuggerEditor` | 调试器的编辑器集成部分，提供调试器UI。 |
| `ModelViewViewModelAssetSearch` | 提供资产搜索功能，便于在编辑器中查找 MVVM 相关资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `f172f2b0` | MVVMToolset: Initial MVVM toolset plugin that supports creating and modifying Viewmodel via blueprint | 新增 MVVM 工具集插件，支持通过蓝图创建和修改 ViewModel。 |
| 2026-05-13 | `825be502` | Listview/Panel Extension: use widget blueprint class directly to get the MVVM view during compilatio | 扩展 ListView/Panel，编译期间可直接使用控件蓝图类获取 MVVM 视图。 |
| 2026-05-12 | `21f108ac` | Cherry-pick UMGToolSet | 摘取 UMG 工具集的更新。 |
| 2026-04-23 | `e24ce23f` | MVVM: Remove unused USTRUCT specifiers | 移除了未使用的 USTRUCT 说明符，进行代码清理。 |
| 2026-04-22 | `cd8175a0` | MVVM: Resolve invalid transient outer when importing copyied conditions and events. UMVVMBlueprintVi | 修复了导入复制条件和事件时出现的无效瞬态外部对象引用问题。 |

### 维护评价
**活跃维护中**。尽管插件标记为“Beta”且默认未启用，但从近期（2026年4-5月）的提交历史来看，它仍在被积极开发和改进，包括增加新工具集（MVVMToolset）、修复bug和优化API。这表明Epic仍在推进此功能，它是一个前沿的、但尚未最终稳定的特性。**推荐关注和尝试**，尤其适合在新项目中追求更佳UI架构的开发者，但需注意其Beta状态可能带来的API变动。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ModelViewViewModel)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/model-view-viewmodel-in-unreal-engine/)