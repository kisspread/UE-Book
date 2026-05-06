# Chaos Cloth Editor

> Deprecated plugin, please use the Chaos Cloth plugin instead.

| 属性 | 值 |
|---|---|
| 中文名 | 废弃布料编辑器 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件，实际无内容） |
| 实验性 | 否 |
| 创建时间 | 2023-01-12 |
| 年龄标签 | 🆕（约2年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosClothEditor) | |

## 用途

该插件是**空壳占位符**，仅用于声明依赖关系，无任何功能代码或资源。其唯一作用是**提醒开发者**：此功能已合并至 `ChaosCloth` 插件，请直接使用 `ChaosCloth` 插件进行布料编辑。官方推荐统一使用 Chaos 布料系统，不再提供单独编辑器子插件。

## 使用场景

⚠️ **不推荐使用此插件**。所有 Chaos 布料编辑器功能目前由 `ChaosCloth` 插件提供。如果你需要布料编辑功能，请直接启用 `ChaosCloth` 插件。

- **编辑布料资产** → 启用 `ChaosCloth` 插件，在骨架网格体编辑器中操作布料数据。
- **布料模拟调试** → 使用 Chaos 物理系统的调试工具。

## 蓝图用法

无。该插件不包含任何公开的蓝图可调用函数、属性或类。

## C++ 用法

无。该插件不包含任何 C++ 头文件或源文件。

## Demo 示例

无代码示例。由于插件无实质内容，无法提供可编译示例。

## 模块依赖

要使用此插件（本身无用），你的模块需要依赖以下插件（来自 `.uplugin` 的 `Plugins` 字段）：

| 插件 | 用途 |
|---|---|
| `ChaosCloth` | 提供 Chaos 布料系统全部功能（包括编辑器支持） |

但既然此插件已废弃，建议直接在项目或模块中依赖 `ChaosCloth` 而非 `ChaosClothEditor`。

## 维护状态

### 近期更新

从 git log 分析（仅当前路径，文件稀少）：

- 2024-03-22 `f55988ce` — Chaos Cloth: 一些布料相关变更（可能涉及编辑器依赖调整）
- 2024-01-29 `3148c950` — Property Editor: Added ctrl/shift multiplier increments to spin box. 修改公共头包含路径（仅维护性编译修复）
- 2023-02-21 `d5a5a356` — Remove unnecessary Public and Private entries for the current module being added to PublicIncludePat（清理构建文件）
- 2023-01-13 `3c9aacb1` — [Engine/Plugins] 初始创建提交
- 2023-01-12 `2f78497e` — [Engine/Plugins] 基础结构首次提交

### 维护评价

- **年龄**：创建于2023年1月，距今约2年。
- **更新频率**：仅有少量构建维护和整理提交，无功能性更新。
- **活跃度**：已明确声明 `Deprecated`，不再活跃。从2024年3月之后未见功能性改动，推测已被官方停止维护。
- **风险**：作为废弃插件，可能在后续UE版本中被移除。**强烈不建议使用**，应直接使用 `ChaosCloth` 插件。
- **推荐情况**：不使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosClothEditor)
- [ChaosCloth 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosCloth)（替代方案）