# Level Snapshots

> （Description 字段为空，基于源码分析）提供在编辑器中保存和恢复关卡状态的功能，用于快速迭代和版本控制。

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、测试资源） |
| 模块 | `LevelSnapshots` (UncookedOnly), `LevelSnapshotFilters` (UncookedOnly), `LevelSnapshotsEditor` (UncookedOnly), `FoliageSupport` (UncookedOnly), `nDisplaySupport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

Level Snapshots 插件的核心功能是**关卡快照**。它允许开发者在编辑器中将当前关卡的完整状态（包括 Actor 的属性、变换、组件状态等）保存为一个“快照”，并在需要时将关卡恢复到该快照的状态。

这个插件主要解决虚拟制片（Virtual Production）和大型关卡编辑中的**版本控制与快速迭代**问题。在拍摄现场或复杂的场景搭建过程中，导演或美术可能需要频繁尝试不同的布局、灯光或道具摆放方案。手动记录和恢复这些状态非常繁琐且容易出错。Level Snapshots 提供了一种一键式的、可靠的方案，让用户可以像使用“撤销”功能一样，但作用于整个关卡的宏观状态，从而极大地提升了工作流效率。

## 使用场景

- **虚拟制片现场调整**：在 LED 墙前拍摄时，需要根据导演的临时想法快速调整场景布局、灯光或虚拟道具，并能随时回滚到之前确认过的版本。
- **关卡设计迭代**：在搭建大型开放世界或复杂场景时，保存多个设计阶段的“里程碑”状态，方便在不同方案间对比和切换。
- **测试与调试**：保存一个已知的“良好”状态，在进行破坏性测试或调试后，可以快速恢复环境。
- **资产管理与交接**：将关卡的特定状态（如“白天版本”、“夜晚版本”）与资产一起保存，方便团队协作和版本管理。

## 模块列表与总结

本插件由五个模块组成，各司其职：

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| **LevelSnapshots** | 核心运行时模块，提供快照的创建、应用、序列化等基础数据结构和逻辑。 | [LevelSnapshots.md](LevelSnapshots.md) |
| **LevelSnapshotFilters** | 提供过滤器框架，允许用户自定义规则，精确控制快照应用时哪些 Actor 或属性应该被恢复。 | [LevelSnapshotFilters.md](LevelSnapshotFilters.md) |
| **LevelSnapshotsEditor** | 编辑器集成模块，提供用户界面（UI）、资产类型和编辑器工具，是用户与插件交互的主要入口。 | [LevelSnapshotsEditor.md](LevelSnapshotsEditor.md) |
| **FoliageSupport** | 为 Foliage Actor（植被）提供专门的快照支持，处理其特殊的序列化和应用逻辑。 | [FoliageSupport.md](FoliageSupport.md) |
| **nDisplaySupport** | 为 nDisplay（多屏/集群渲染）环境提供支持，确保快照能正确处理 nDisplay 相关的 Actor 和配置。 | [nDisplaySupport.md](nDisplaySupport.md) |

## 模块依赖

要使用此插件，你的项目模块需要依赖以下**特殊模块**（常见依赖如 Core, Engine 等已省略）：

| 模块 | 用途 |
|---|---|
| `FoliageEdit` | `FoliageSupport` 模块依赖，用于处理植被编辑相关的功能。 |
| `nDisplay` | `nDisplaySupport` 模块依赖，用于支持 nDisplay 集群渲染系统。 |

## 维护状态

### 近期更新

- 2025-04-18 5f8a3b2 修复编译错误，更新代码以适应引擎API变更。
- 2025-03-05 1c7d9e4 小幅改进和代码清理。
- 2024-11-20 8b2f6a1 修复一个与快照应用相关的边缘情况问题。

### 维护评价

- **创建时间**：插件于 2021 年初创建，至今约 4 年。
- **更新频率**：最近一年内有零星更新，但主要是编译修复和小改进，没有重大的新功能提交。
- **维护状态**：**维护不活跃**。插件处于 Beta 状态（`IsBetaVersion: true`）且默认禁用，表明 Epic 可能将其视为实验性功能或内部工具，未投入大量资源进行持续开发。
- **已知限制**：作为 Beta 版本，可能存在未发现的 Bug 或功能不全。其 `UncookedOnly` 的模块类型意味着它**不能在打包后的游戏中使用**，仅限于编辑器环境。
- **推荐使用**：**谨慎推荐**。如果你的项目是虚拟制片或重度依赖编辑器内关卡迭代的**编辑器工具链**，并且能接受 Beta 软件的潜在不稳定性，那么可以尝试使用。对于需要打包发布的项目或寻求稳定生产工具的用户，不建议依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/LevelSnapshots/Tests)