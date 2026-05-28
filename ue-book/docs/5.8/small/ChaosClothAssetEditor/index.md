# Chaos Cloth Asset Editor (Deprecated)

> Deprecated plugin, please use the Chaos Cloth Asset Editor Core and Chaos Cloth Asset Usd Dataflow Nodes plugins instead.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产编辑器（已废弃） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯依赖插件） |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

这是一个**已被废弃的过渡性插件**，本身不包含任何源代码或功能模块。它的唯一作用是声明对两个替代插件的依赖，确保依赖旧名称的项目仍能正常加载：

- **ChaosClothAssetEditorCore** — 布料资产编辑器的核心功能
- **ChaosClothAssetUsdDataflowNodes** — 布料资产的 USD 数据流节点

原始的 `ChaosClothAssetEditor` 插件在 2026 年 1 月被拆分为三个独立插件（将 USD 相关代码分离出去），这个废弃插件作为向后兼容的占位符保留。

## 使用场景

- 你的项目之前依赖 `ChaosClothAssetEditor`，升级后需要保持兼容 → 该插件会自动拉取新的替代插件
- **新项目不应使用此插件** → 直接启用 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes`

## 蓝图用法

该插件无任何模块，不提供蓝图节点。所有功能请参阅替代插件的文档：

- `ChaosClothAssetEditorCore` — 布料资产编辑器核心
- `ChaosClothAssetUsdDataflowNodes` — USD 数据流节点

## C++ 用法

该插件无任何 C++ 模块，不提供 API。如需在 C++ 中使用布料资产编辑器功能，请直接依赖替代插件对应的模块。

## Demo 示例

不适用。该插件不包含源代码。

## 模块依赖

该插件无自身模块。它通过 `.uplugin` 的 `Plugins` 字段声明对以下插件的依赖：

| 插件 | 用途 |
|---|---|
| `ChaosClothAssetEditorCore` | 布料资产编辑器核心功能（原 ChaosClothAssetEditor 的主体） |
| `ChaosClothAssetUsdDataflowNodes` | 布料资产与 USD 格式互转的数据流节点 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 布料资产模块正式脱离 Beta 状态 |
| 2026-01-27 | `4c7d09a3` | Chaos Cloth Asset - Split the ChaosClothEditor plugin into three plugins in order to move USD code o | 将编辑器插件拆分为三个插件，分离 USD 相关代码 |
| 2026-01-26 | `ae188081` | Guard against crash and unexpected results in cloth remesh node | 修复布料重网格节点的崩溃和异常结果 |
| 2026-01-26 | `306c3592` | Chaos Cloth Asset - Replaced lambda by existing LinearToSRGB function in the static mesh color space | 用已有的 LinearToSRGB 函数替换自定义 lambda |
| 2026-01-26 | `d217d1d3` | Chaos Cloth Asset: | 布料资产相关改动（提交信息被截断） |

### 维护评价

⚠️ **此插件已被废弃（Deprecated），不建议在任何项目中使用。**

- 该插件在 2026 年 1 月拆分后即成为一个空壳过渡插件，仅用于向后兼容
- 最近的更新（2026-04-21）是将替代插件标记为正式版，与本插件无直接关系
- 所有实际功能已迁移至 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes`
- **迁移建议**：如果你的项目仍在引用此插件，请移除它，改为直接引用上述两个替代插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor)
- [ChaosClothAssetEditorCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
- [ChaosClothAssetUsdDataflowNodes 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)