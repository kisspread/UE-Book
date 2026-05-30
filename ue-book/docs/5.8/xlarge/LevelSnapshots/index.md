# LevelSnapshots

> 快照工具，用于捕获和恢复关卡状态

| 属性 | 值 |
|---|---|
| 中文名 | 关卡快照 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `LevelSnapshots` (Runtime), `LevelSnapshotFilters` (Runtime), `FoliageSupport` (Runtime), `LevelSnapshotsEditor` (Runtime), `nDisplaySupport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-02-03 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots) | |

## 用途

LevelSnapshots 是一个用于关卡状态管理的高级工具。它解决了虚拟制片和复杂关卡迭代中的核心痛点：在编辑器中进行大量修改（如调整灯光、移动Actor、修改材质参数）后，很难精确回退到之前的某个状态。传统的“撤销”操作栈有限，且无法跨会话保存状态。

该插件允许用户在任何时刻为整个关卡（或选定的Actor集合）创建一个完整的、结构化的“快照”。这个快照不仅记录Actor的变换和属性，还记录了组件结构、蓝图实例数据，甚至支持植被等复杂资产的快照。用户可以在多个快照之间自由切换、比较差异，并选择性地恢复特定部分，是关卡设计师和虚拟制片团队进行非破坏性工作流程和A/B测试的强大工具。

## 使用场景

- **虚拟制片预演**：在拍摄前创建多个灯光和场景布局的快照，以便在片场快速切换不同方案。
- **关卡迭代与A/B测试**：对同一关卡进行不同风格的设计尝试（如不同天气、不同时间），并方便地切换比较。
- **资产安全备份**：在进行大量重构或实验性修改前创建快照，作为可快速恢复的检查点。
- **团队协作**：不同美术师可以在同一关卡上工作，各自创建快照保存自己的修改，然后由主美合并或选择最佳方案。

## 模块列表

| 模块 | 说明 |
|---|---|
| [**LevelSnapshots**](LevelSnapshots.md) | 核心运行时模块，提供快照创建、存储、差异比较和应用的基础架构。 |
| [**LevelSnapshotFilters**](LevelSnapshotFilters.md) | 运行时过滤系统，用于在创建快照或应用快照时，精细地控制哪些Actor或属性被包含或排除。 |
| [**FoliageSupport**](FoliageSupport.md) | 为引擎的Foliage（植被）系统提供专用支持，确保植被实例可以被正确地快照和恢复。 |
| [**LevelSnapshotsEditor**](LevelSnapshotsEditor.md) | 编辑器扩展模块，提供UI界面（如快照管理器、差异查看器）来操作快照。 |
| [**nDisplaySupport**](nDisplaySupport.md) | 为nDisplay（多屏幕渲染）场景提供支持，确保与nDisplay相关的Actor状态能被正确处理。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/LevelSnapshots)
- [官方文档]() (暂无)