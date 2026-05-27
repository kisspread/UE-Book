# Chaos Cloth Asset Editor

> Deprecated plugin, please use the Chaos Cloth Asset Editor Core and Chaos Cloth Asset Usd Dataflow Nodes plugins instead.

| 属性 | 值 |
|---|---|
| 中文名 | 混沌布料资产编辑器（已废弃） |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | 否 |
| 创建时间 | 2024-03-22 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

此插件是一个**已废弃的占位插件**，其本身不包含任何代码或运行时模块。它的存在是为了**向后兼容**旧版项目的插件依赖关系。

在 UE 5.4 之前，Chaos 布料资产的编辑器功能和相关的工具模块（如数据流节点）可能集成在一个名为 `ChaosClothAssetEditor` 的插件中。随着引擎版本迭代，这些功能被重构和拆分。
当前版本中，原本属于该插件的功能已经被移动到两个新的插件中：
1.  **`ChaosClothAssetEditorCore`**：提供核心的编辑器功能，如布料资产的编辑器界面、资产工厂等。
2.  **`ChaosClothAssetUsdDataflowNodes`**：提供与 USD（通用场景描述）和数据流系统相关的布料资产节点。

因此，`ChaosClothAssetEditor` 插件仅作为一个“空壳”保留，以确保旧项目在升级时，其 `.uproject` 文件中对该插件的依赖声明不会导致编译错误。**新项目不应使用此插件。**

## 使用场景

-   你正在维护一个从 UE 5.4 之前版本升级而来的项目，并且项目中引用了 `ChaosClothAssetEditor` 插件。
-   你需要理解旧版项目的插件依赖结构。

**重要提示**：对于所有新项目或需要开发新功能的情况，应直接使用 `ChaosClothAssetEditorCore` 和 `ChaosClothAssetUsdDataflowNodes` 插件。

## 蓝图用法

由于此插件是一个废弃的空壳，不包含任何模块，因此**没有**可直接在蓝图中使用的函数、属性或节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无） | 此插件无任何蓝图节点 | - |

## C++ 用法

由于此插件是一个废弃的空壳，不包含任何模块，因此**没有**可供 C++ 代码引入的头文件或 API。

### 头文件引入
```cpp
// 无可用头文件
```

### 基本用法
（无）

### 进阶用法
（无）

## Demo 示例

此插件不包含任何模块或可编译的代码，因此**没有** C++ 或蓝图的演示示例。相关功能请参考 `ChaosClothAssetEditorCore` 插件。

## 模块依赖

此插件自身无模块，但它声明了对以下两个插件的运行时依赖（`Plugins` 字段）：

| 模块 | 用途 |
|---|---|
| `ChaosClothAssetEditorCore` | 提供 Chaos 布料资产的核心编辑器功能。 |
| `ChaosClothAssetUsdDataflowNodes` | 提供 Chaos 布料资产与 USD 和数据流系统集成的节点。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `600f5cce` | [Chaos Cloth Asset] Moved Cloth Asset modules out of beta. | 将布料资产相关的模块（可能指被拆分出的新插件）移出 Beta 测试阶段，意味着它们已成为正式功能。 |
| 2026-01-27 | `4c7d09a3` | Chaos Cloth Asset - Split the ChaosClothEditor plugin into three plugins in order to move USD code o... | 将原来的 `ChaosClothEditor` 插件拆分为三个插件，以隔离 USD 相关代码，这正是本插件被废弃的根本原因。 |
| 2026-01-26 | `ae188081` | Guard against crash and unexpected results in cloth remesh node | 修复了布料重网格节点中的崩溃和意外结果问题。 |
| 2026-01-26 | `306c3592` | Chaos Cloth Asset - Replaced lambda by existing LinearToSRGB function in the static mesh color space | 在静态网格体颜色空间转换中，用已有的 `LinearToSRGB` 函数替代了 lambda 表达式，进行了代码清理。 |
| 2026-01-26 | `d217d1d3` | Chaos Cloth Asset: (信息被截断) | 布料资产相关的提交，具体信息不完整。 |

### 维护评价

*   **创建与废弃**：此插件于 2024 年 3 月创建，但其 `.uplugin` 文件明确标记为 **Deprecated（已废弃）**，并指引用户使用替代插件。
*   **维护活跃度**：从提交记录看，其相关的底层系统（Chaos Cloth Asset）在 2026 年初仍有活跃的更新和重构（如插件拆分、Bug 修复），但这些工作都发生在其替代插件上，而非本“空壳”插件本身。
*   **状态与建议**：该插件**已被正式废弃**。它仅用于向后兼容，不具备任何新功能开发价值。**强烈不建议**新项目使用，老项目在条件允许时也应迁移至新的插件结构。
*   **已知限制**：此插件本身没有功能，因此没有功能限制，但其存在标志着代码结构的旧版本状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditor)
-   [替代插件：ChaosClothAssetEditorCore](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetEditorCore)
-   [替代插件：ChaosClothAssetUsdDataflowNodes](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosClothAssetUsdDataflowNodes)