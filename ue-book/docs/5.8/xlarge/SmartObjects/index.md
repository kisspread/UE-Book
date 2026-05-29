# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 中文名 | 智能对象系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

Smart Objects 是一个为游戏世界中的**环境生命体**（如 NPC、动物、场景互动道具）提供标准化互动逻辑的系统。它解决的核心问题是：如何让大量 AI 角色或玩家能够高效地发现、申请、并使用场景中预设的“智能”互动点（如长椅、篝火、小贩摊位），而无需为每种场景单独编写复杂的交互脚本。

该系统通过将场景中的可交互元素抽象为“智能对象槽位”（Smart Object Slots），并允许角色（用户）通过“智能对象组件”（Smart Object Component）进行注册、查询和占用，实现了互动逻辑的复用和解耦。

## 使用场景

*   **开放世界 NPC 行为**：你的世界中有许多动态 NPC，他们需要在场景中寻找长椅休息、到篝火旁取暖、在摊位上交易。使用 Smart Objects 可以为这些互动点定义通用行为，让 NPC 自主发现并参与。
*   **玩家与场景互动**：玩家角色需要与场景中大量的可互动物品（如打开一个特定的门、使用一台机器）进行交互。Smart Objects 可以管理这些互动的触发、状态和占用关系。
*   **多人游戏中的资源竞争**：在多人游戏中，多个玩家或 AI 可能竞争同一个智能对象（例如，只有一个玩家能使用某个补给箱）。系统提供了内置的槽位分配和冲突解决机制。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindAndClaimSlot` | 为当前用户查找并申请一个可用的智能对象槽位。 | `USmartObjectSubsystem` |
| `ReleaseSlot` | 释放当前用户占用的槽位。 | `USmartObjectSubsystem` |
| `UseSmartObject` | 触发一个完整的智能对象使用流程（查找、申请、执行、释放）。 | `USmartObjectComponent` |

### 使用示例（蓝图描述）

1.  **创建智能对象**：在场景中的静态网格体（如一个长椅）上添加 `SmartObjectComponent`。在该组件的详情面板中，配置一个或多个“槽位”（Slots），每个槽位代表一个可供互动的位置，并关联一个行为定义（Behavior Definition）。
2.  **角色申请使用**：在 NPC 的蓝图中，使用 `SmartObjectSubsystem` 的 `FindAndClaimSlot` 节点，传入 NPC 本身和一个 `SmartObjectRequest` 结构体（用于筛选条件，如互动类型）。如果成功，则返回一个 `ClaimedSlot` 句柄。
3.  **执行互动**：使用返回的句柄，通过 `SmartObjectSubsystem` 的 `UseSlot` 节点，触发动画、播放声音或执行其他逻辑。
4.  **完成并释放**：互动完成后，调用 `ReleaseSlot` 节点，让槽位可以被其他用户使用。

## 模块依赖

该插件无特殊依赖，主要依赖常见的 Gameplay 和 AI 框架模块。使用者通常需要依赖 `GameplayBehaviors`、`StateTree` 和 `ZoneGraph` 等模块来实现完整的 AI 行为树集成。

| 模块 | 用途 |
|---|---|
| `GameplayBehaviors` | 定义和执行附加在智能对象上的具体游戏行为。 |
| `StateTree` | 用于驱动基于状态树的复杂 AI 决策逻辑。 |
| `ZoneGraph` | 提供基于区域的空间数据查询，常用于确定 NPC 可访问的智能对象范围。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于代码质量改进。 |
| 2026-04-13 | `f10a2daf` | [ContentBrowser] New Add Menu AI Menu | 在内容浏览器的“添加”菜单中新增了“AI”子菜单，可能包含了与智能对象相关的资产创建选项。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 重构了 MassCore 模块的头文件结构，属于底层框架调整，可能间接影响 SmartObjects 的依赖。 |
| 2026-03-31 | `d7c5497a` | [SmartObjects][Debug] Three-level debug rejection tracking in FindSlotsInternal and FindMatchingSlot | 为智能对象的槽位查找功能添加了三级详细的调试拒绝跟踪，便于开发者诊断为何查找失败。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 将 MassCore 模块从 MassEntity 中独立出来，是大规模 AI 系统的重构，与 SmartObjects 底层支持相关。 |

### 维护评价

*   **创建时间**：约5年前创建，是一个相对成熟的系统。
*   **最近更新**：最近更新非常频繁（2026年4月仍有活跃提交），内容涉及功能增强、调试工具和底层重构。
*   **活跃度**：**活跃维护中**。最近的提交显示开发团队仍在积极优化和集成该系统，特别是与 AI 框架（Mass、StateTree）的深度整合。
*   **已知限制**：该插件默认未启用（`EnabledByDefault: false`），表明它可能仍处于稳定但非核心的功能阶段，或需要特定场景才会使用。
*   **推荐使用**：如果你的游戏有大量需要与场景互动的 AI 角色或玩家，且追求行为逻辑的标准化和可扩展性，**推荐使用**。它能够有效减少重复代码，提升开发效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects)
- [官方文档](暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)