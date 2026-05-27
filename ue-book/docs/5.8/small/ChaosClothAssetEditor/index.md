# Chaos Cloth Asset Editor (Deprecated)

> Deprecated plugin, please use the Chaos Cloth Asset Editor Core and Chaos Cloth Asset Usd Dataflow Nodes plugins instead.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器（已废弃） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

这是一个**已废弃**的过渡性插件，本身不包含任何代码或模块。它曾经是 Chaos Cloth Asset 编辑器功能的入口插件，但在 2026 年初被拆分为两个独立插件：

- **ChaosClothAssetEditorCore** — 核心编辑器功能
- **ChaosClothAssetUsdDataflowNodes** — USD 数据流节点相关功能

该插件现在仅作为兼容性包装存在，启用时会自动加载上述两个后继插件。**不应在新项目中使用此插件**。

## 使用场景

- ❌ **不要使用此插件** — 它已被废弃
- 如果你需要布料资产编辑功能 → 请使用 **ChaosClothAssetEditorCore**
- 如果你需要 USD 布料数据流节点 → 请使用 **ChaosClothAssetUsdDataflowNodes**

## 蓝图用法

此插件无任何蓝图节点（无模块，无源码）。

## C++ 用法

此插件无任何 C++ API（无模块，无源码）。

## 模块依赖

此插件本身无模块，但依赖以下插件：

| 插件 | 用途 |
|---|---|
| `ChaosClothAssetEditorCore` | Chaos 布料资产编辑器核心功能 |
| `ChaosClothAssetUsdDataflowNodes` | Chaos 布料资产 USD 数据流节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产模块正式脱离 Beta 状态 |
| 2026-01-27 | `4c7d09a3` | Chaos Cloth Asset - Split the ChaosClothEditor plugin into three plugins in order to move USD code o | 将编辑器插件拆分为三个插件，分离 USD 相关代码 |
| 2026-01-26 | `ae188081` | Guard against crash and unexpected results in cloth remesh node | 修复布料重新网格化节点的崩溃和异常问题 |
| 2026-01-26 | `306c3592` | Chaos Cloth Asset - Replaced lambda by existing LinearToSRGB function in the static mesh color space | 使用现有 LinearToSRGB 函数替代 lambda 表达式 |
| 2026-01-26 | `d217d1d3` | Chaos Cloth Asset: | Chaos 布料资产相关改动 |

### 维护评价

**⚠️ 已废弃 — 请勿使用**

该插件在 2026 年 1 月的 `4c7d09a3` 提交中被正式标记为废弃，其功能被拆分到 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 两个插件中。从 `.uplugin` 的 `Installed: false` 和空模块列表可以看出，该插件已不再包含实质内容，仅作为向后兼容的占位符存在。

创建于 2024 年 3 月，作为 Chaos Cloth Asset 系统从 Experimental 目录迁移到正式目录的产物。在运行约 2 年后被废弃并拆分，这是 Epic 对插件架构进行合理化的正常流程。

**建议**：如果你的项目中启用了此插件，应迁移到后继插件。如果不使用 USD 相关功能，只需依赖 `ChaosClothAssetEditorCore` 即可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor)
- [后继插件: ChaosClothAssetEditorCore](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [后继插件: ChaosClothAssetUsdDataflowNodes](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)