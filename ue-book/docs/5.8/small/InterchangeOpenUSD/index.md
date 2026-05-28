# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | 通用 USD 转换器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（翻译器、工厂、处理程序等） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

本插件是 **Interchange 框架** 的一个扩展，专门用于实现 **通用场景描述（OpenUSD）** 格式文件的导入功能。它解决了在 Unreal Engine 5 中直接使用 USD 格式资产（如复杂场景、动画、材质）的需求，允许艺术家和开发者将 USD 资产无缝地引入到 UE5 项目中，是连接主流数字内容创建（DCC）工具与 UE5 实时引擎的重要桥梁。

## 使用场景

- 你需要在 UE5 中直接导入来自 Pixar、Apple USD 生态或 Autodesk Maya 等工具创建的 USD 资产。
- 你的团队在进行影视虚拟制作或大型场景时，需要将基于 USD 流程构建的资产导入 UE5。
- 你希望利用 USD 强大的层级和组合特性来管理复杂场景，并在 UE5 中保持数据结构。

## 蓝图用法

本插件主要作为框架的后端翻译器，不直接提供大量蓝图节点，其功能通过 Interchange 导入管线触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （通过 Interchange 导入资产调用） | 当用户导入 .usd, .usda, .usdc 或 .usdz 文件时，系统会自动调用本插件提供的翻译器进行处理。 | 无直接暴露 |

### 使用示例（蓝图描述）

1.  在 Content Browser 中右键，选择 “Import Asset”。
2.  选择一个 USD 文件。
3.  在出现的导入选项窗口中，Interchange 框架会自动识别文件类型，并调用本插件中注册的翻译器来解析 USD 数据。
4.  导入完成后，USD 文件中的网格、材质、动画等资产将按照插件配置被转换为 UE5 原生资产。

## C++ 用法

本插件的使用主要是注册和扩展，而非直接调用。

### 头文件引入

根据具体模块需要，可能需引入：
```cpp
#include "InterchangeOpenUSDEditorModule.h"
#include "InterchangeOpenUSDImportModule.h"
```

### 基本用法

本插件的功能主要在模块加载时通过注册 **Interchange 工厂（Factory）** 和 **翻译器（Translator）** 来实现。开发者通常无需直接调用其 API，而是通过 Interchange 管线使用。

```cpp
// 以下为概念性代码，说明插件如何融入框架
// 当一个 USD 文件被传递到 Interchange 管线时...
UInterchangeSourceData* SourceData = ...; // 包含 USD 文件路径
UInterchangeFactoryBaseNode* RootNode = ...; // 根工厂节点

// Interchange 管线会查找并使用本插件注册的 USD 翻译器
// InterchangeOpenUSDImport 模块提供了 FInterchangeUSDTranslator
// 该翻译器负责解析 USD Stage 并构建对应的 Interchange 节点树
// 之后由对应的工厂（如 Mesh Factory）将节点树转换为 UE5 资产
```

### 进阶用法

开发者可以参考插件源码，学习如何为新的文件格式实现类似的 **Interchange 翻译器**和**工厂**，从而扩展 Interchange 框架。

## 模块依赖

**注意**：以下依赖基于插件类型推测，具体依赖请查阅各模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 框架核心模块，提供工厂、翻译器等基类。 |
| `InterchangeNodes` | 定义 Interchange 节点（如网格、材质、纹理等）的数据结构。 |
| `USD` (UnrealUSDWrapper) | Unreal Engine 的 USD 核心库，用于加载和遍历 USD Stage。 |
| `USDClasses` | 提供 UE5 针对 USD 的特定资产类和工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 实现了骨骼和物理资产的跟踪功能。 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | 修复了 USDZ 文件的处理问题。 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | 修复了 MaterialX 转换器生成的节点标记，使其能正确关联原始 USD Prim 路径。 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复了实例内部材质未被去重的问题。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 产生的警告。 |

### 维护评价

- **活跃维护**：从 git 记录看，插件在 2026 年 5 月持续有密集的更新，主要集中在 **USD 预生成（Pregen）** 功能的改进和 bug 修复上，表明其处于**非常活跃的开发阶段**。
- **实验性**：插件元数据明确标记为 `IsExperimentalVersion: true`，且默认未启用，说明其 API 和功能可能尚未完全稳定，使用者需自行承担风险。
- **推荐使用**：对于需要在 UE5 中处理 USD 资产，且不介意使用实验性功能的团队，本插件是**必选**的扩展。鉴于其活跃的维护状态，可以预期未来会有持续的功能完善和稳定性提升。使用时应密切关注更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [官方文档（Interchange 框架）](https://docs.unrealengine.com/5.8/en-US/interchange-framework-in-unreal-engine/)
- [测试用例（请参考各子模块文档）]()