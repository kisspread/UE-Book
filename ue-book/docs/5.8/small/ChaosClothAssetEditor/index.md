# Chaos Cloth Asset Editor (Deprecated)

> Deprecated plugin, please use the Chaos Cloth Asset Editor Core and Chaos Cloth Asset Usd Dataflow Nodes plugins instead.

| 属性 | 值 |
|---|---|
| 中文名 | 布料资产编辑器（已废弃） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（已废弃内容） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

这是一个**已废弃**的插件。其原始用途是为 UE5 的 Chaos 布料资产系统提供编辑器集成和工具。它现在已不再被推荐使用。

该插件在历史上曾作为一个聚合容器，将 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 两个插件的功能模块整合在一起。后来，Epic Games 将这个“聚合”插件标记为废弃，并将其中的模块拆分到上述两个更专注于特定功能的独立插件中。因此，这个插件目前的存在价值主要是一个**向后兼容的占位符**和**功能迁移的导向标志**，其实际功能已完全由其依赖的两个插件承接。

**核心要点**：如果你在项目中看到或需要使用此插件，应立即迁移到 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 插件。

## 使用场景

- 你的项目较老，最初使用 `ChaosClothAssetEditor` 插件进行布料物理模拟和资产创建，现在需要升级到最新版本。
- 你正在清理项目插件列表，发现此插件被禁用或标记为废弃，并希望了解其替代方案。
- **新项目**：**绝对不要使用此插件**，请直接使用 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes`。

## 蓝图用法

由于此插件本身**没有模块（Modules 为空）**，它不提供任何可直接在蓝图中调用的函数或节点。所有蓝图相关的功能均由其依赖的 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 插件提供。

请查阅上述两个插件的文档以获取蓝图用法。

## C++ 用法

同样，由于此插件没有模块，它不包含任何 C++ API。如果你需要在 C++ 中操作布料资产，应该链接并使用 `ChaosClothAssetEditorCore` 或 `ChaosClothAssetUsdDataflowNodes` 插件的模块。

## Demo 示例

不适用。此插件已废弃，且不包含代码模块。相关示例请参考 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 插件。

## 模块依赖

此插件本身没有代码模块，但它通过 `Plugins` 部分声明了对以下插件的硬性依赖。这意味着启用此插件会强制启用其依赖项。

| 插件 | 用途 |
|---|---|
| `ChaosClothAssetEditorCore` | 提供 Chaos 布料资产编辑器的核心功能、节点和资产类型。 |
| `ChaosClothAssetUsdDataflowNodes` | 提供与 USD (Universal Scene Description) 数据流相关的布料资产处理节点。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产模块从 Beta 状态毕业，标志着相关系统趋于稳定。 |
| 2026-01-27 | `4c7d09a3` | Chaos Cloth Asset - Split the ChaosClothEditor plugin into three plugins in order to move USD code o... | 将原 ChaosClothEditor 插件拆分为三个插件，以隔离 USD 相关代码，导致此插件被废弃。 |
| 2026-01-26 | `ae188081` | Guard against crash and unexpected results in cloth remesh node | 修复了布料重网格节点中的崩溃和非预期结果问题。 |
| 2026-01-26 | `306c3592` | Chaos Cloth Asset - Replaced lambda by existing LinearToSRGB function in the static mesh color space | 在静态网格颜色空间处理中用现有函数替换 lambda，进行代码重构。 |
| 2026-01-26 | `d217d1d3` | Chaos Cloth Asset: ... | （摘要截断）这是将模块拆分出的那批提交之一。 |

### 维护评价

- **状态**：**已废弃 (Deprecated)**。该插件在 2026 年初被正式废弃，其功能被更现代的插件组合所取代。
- **更新频率**：插件本身已停止更新。但其依赖的 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 插件仍在**活跃维护**中（如2026年4月仍有更新），证明 Chaos 布料资产系统本身是持续发展的。
- **推荐使用**：**不推荐**。这是一个历史遗留插件，用于保持旧项目的兼容性。对于新功能开发或新项目，请直接使用 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes`。
- **迁移建议**：应在项目设置中**禁用**此插件，并**启用**其依赖的两个新插件，以确保获得最新的功能、修复和性能优化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor)