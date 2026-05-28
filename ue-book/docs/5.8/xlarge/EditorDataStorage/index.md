# TEDS: Editor Data Storage

> A central extendable data storage for editors and their corresponding data with support for viewing and editing through a collection of widgets.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器数据和控件） |
| 模块 | `TedsCore` (UncookedOnly), `TedsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage) | |

## 用途

TEDS 是一个面向编辑器的中央可扩展数据存储系统。它旨在解决编辑器中数据分散、难以统一管理和展示的问题。通过提供一个中心化的数据存储，TEDS 允许编辑器的不同部分共享和操作同一数据源，并支持通过可扩展的 UI 控件集来查看和编辑这些数据。它为构建复杂、数据驱动的编辑器工具和界面提供了基础架构。

## 模块列表

| 模块 | 说明 |
|---|---|
| [`TedsCore`](TedsCore.md) | 核心数据存储引擎，负责数据的定义、存储、查询和动态列管理。 |
| [`TedsUI`](TedsUI.md) | UI 集成层，提供用于查看和编辑存储数据的可扩展控件集。 |

## 使用场景

- **开发复杂编辑器工具**：当你需要构建一个包含大量可配置数据（如关卡设计参数、资产属性、游戏规则）的自定义编辑器面板时，可以使用 TEDS 作为统一的数据后端，并使用其提供的 UI 控件进行展示和编辑。
- **构建数据驱动的界面**：需要创建一个能动态反映底层数据变化的 UI，例如一个属性编辑器、数据表格或图表生成器，TEDS 的 UI 层可以简化这类工作的开发。
- **扩展编辑器功能**：为 Unreal 编辑器添加新的数据面板或自定义检查器，这些功能需要与引擎的其他部分共享数据。
- **为特定工具（如 ChaosVisualDebugger）提供数据支持**：TEDS 是 ChaosVisualDebugger 等编辑器工具的底层数据框架。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `cc577021` | Fix race condition in TEDS Dynamic Column Generation | 修复动态列生成中的竞态条件问题。 |
| 2026-04-16 | `419974fc` | [TEDS] Fixed incorrect pre-check before calling `AddCompositionToEntity_GetDelta`. | 修复在调用特定函数前的错误预检查。 |
| 2026-04-16 | `dfebe6ae` | [TEDS] Add Filter Config to allow filtering to continue if a row is hit that fails VerifyColumns | 添加过滤器配置，允许在遇到验证失败的行时继续过滤。 |
| 2026-04-14 | `b78fe9c6` | [TEDS] Deprecated `CurrentRowHasColumns` and `CurrentBatchTableHasColumns` in favor of `CurrentTable` | 废弃旧 API，推荐使用新的 `CurrentTable` 方法。 |
| 2026-04-14 | `86eacb4b` | [TEDS] Fixed the result counter in FQueryResult not being atomic. | 修复查询结果计数器的非原子性问题。 |

### 维护评价

**活跃维护**。插件创建于 2024 年 7 月，距今约一年。从最近的提交记录看，维护非常活跃（最近更新在 2026 年 5 月）。提交内容集中在修复核心功能（如竞态条件、原子性）和改进 API 易用性（废弃旧函数、增加新配置）。鉴于其 **实验性** 标签且仍处于 `Experimental` 目录，表明该插件仍在快速迭代和演进中，API 可能发生变化。目前是 Unreal 编辑器数据架构的重要发展方向，推荐关注和用于实验性项目，但生产环境使用需谨慎。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage)
- [TedsCore 模块文档](TedsCore.md)
- [TedsUI 模块文档](TedsUI.md)