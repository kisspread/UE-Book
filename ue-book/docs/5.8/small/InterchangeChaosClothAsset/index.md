# Interchange Chaos Cloth Asset

> Contains the classes and objects required to allow Interchange to produce Chaos Cloth Assets

| 属性 | 值 |
|---|---|
| 中文名 | 交互布料资产导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `InterchangeChaosClothAssetImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-27 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset) | |

## 用途

这是一个为 **Interchange 导入框架**提供扩展的插件，专门用于导入 **Chaos Cloth（Chaos 布料）资产**。它解决了从外部 DCC 工具（如 Marvelous Designer、CLO3D 等）或中间格式（如 USD）将布料模拟和渲染数据导入到 Unreal Engine 的 Chaos Cloth Asset 资产中的问题。

**核心功能**：
- **扩展 Interchange 管道**：为 Interchange 导入流程添加专门的布料资产处理管线
- **解析布料数据**：从导入文件中提取模拟网格（Simulation Mesh）、渲染网格（Render Mesh）和 solver 属性（如空气阻力、重力、时间步长等）
- **生成 Chaos Cloth 资产**：将提取的数据打包成 `FManagedArrayCollection` 并应用到 Chaos Cloth Asset 上
- **支持重导入**：允许重新导入已存在的布料资产，更新模拟和渲染数据
- **集成 Dataflow**：可指定 Dataflow 图模板，在导入时自动应用数据流处理

这个插件使美术师能够在 DCC 工具中设计复杂的布料模拟，然后通过标准的 Interchange 导入流程无缝地将数据引入 UE5，无需手动重建布料资产。

## 使用场景

- 你使用 Marvelous Designer 或 CLO3D 设计服装布料 → 通过 Interchange 直接导入为 Chaos Cloth Asset
- 你需要将布料模拟数据从 USD 格式导入 UE5 → 此插件为 Chaos Cloth 提供了专门的导入支持
- 你需要批量导入大量布料资产 → 可通过 Interchange 管线配置导入选项
- 你想要在导入时自动为布料应用特定的 Dataflow 图 → 通过管道配置指定 Dataflow 模板

## 蓝图用法

此插件主要在编辑器导入流程中使用，其核心功能通过 **Interchange 导入对话框** 的管线配置暴露给用户。

### 核心节点（工厂节点）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetImportSimulationMeshes` | 获取是否导入模拟网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetImportSimulationMeshes` | 设置是否导入模拟网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetImportRenderMeshes` | 获取是否导入渲染网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetImportRenderMeshes` | 设置是否导入渲染网格 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetDataflowGraphPath` | 获取应用的 Dataflow 图模板路径 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetDataflowGraphPath` | 设置应用的 Dataflow 图模板路径 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetAirDamping` / `SetAirDamping` | 获取/设置空气阻尼系数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetGravity` / `SetGravity` | 获取/设置重力向量 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetSubStepCount` / `SetSubStepCount` | 获取/设置模拟子步数 | `UInterchangeChaosClothAssetFactoryNode` |
| `GetTimeStep` / `SetTimeStep` | 获取/设置模拟时间步长 | `UInterchangeChaosClothAssetFactoryNode` |

### 使用示例（通过 Interchange 导入对话框）

1.  **选择文件**：在 Content Browser 中右键选择“Import Asset”并选择你的布料文件（如 USD 格式）。
2.  **选择管线**：在 Interchange 导入对话框中，从管线（Pipeline）下拉菜单中选择 **"ChaosClothAsset"** 或类似名称。
3.  **配置选项**：
    *   在管线配置面板中，勾选 **"Import Cloth Assets"**。
    *   你可以设置 **"Import Simulation Meshes"** 和 **"Import Render Meshes"** 来决定是否导入对应的网格数据。
    *   **"Dataflow Graph Asset"** 允许你选择一个预先创建的 Dataflow 图模板。导入的布料资产会实例化这个图，并将提取的模拟数据作为变量（`ImportedCollection`）注入其中。
4.  **导入**：点击“Import”按钮，Interchange 会使用此插件的工厂（Factory）和管线（Pipeline）处理文件，生成 Chaos Cloth Asset 资产。

## C++ 用法

此插件主要用于扩展 Interchange 框架，开发者通常不直接使用其 C++ API，而是通过配置管线来使用。以下是其内部工作原理的示例。

### 头文件引入

```cpp
// 使用此插件的工厂和管线类
#include "InterchangeChaosClothAssetFactory.h"
#include "InterchangeChaosClothAssetPipeline.h"
#include "InterchangeChaosClothAssetFactoryNode.h"
```

### 基本用法（理解导入流程）

插件的核心是 `UInterchangeChaosClothAssetFactory`，它负责实际创建 `UChaosClothAsset`。

**导入流程简化** (基于源码分析):
1.  **管线阶段 (`ExecutePipeline`)**: `UInterchangeChaosClothAssetPipeline` 扫描场景节点，查找带有 `ClothRoot` 标签的节点，并从中提取渲染和模拟网格信息，生成 `UInterchangeChaosClothAssetFactoryNode`。
2.  **负载任务 (`CreatePayloadTasks`)**: 工厂为每个网格创建异步任务来提取网格数据（顶点、索引、法线等）。
3.  **异步导入 (`ImportAsset_Async`)**: 在后台线程处理负载数据，构建 `FManagedArrayCollection`。
4.  **游戏线程完成 (`BeginImportAsset_GameThread`)**: 在游戏线程上创建 `UChaosClothAsset` 资产，并将提取的 `CombinedCollection` 数据应用到资产的 Dataflow 图变量 `ImportedCollection` 上。

### 进阶用法（扩展或自定义）

如果需要支持新的布料格式，可能需要：
1.  实现一个新的 `UInterchangeTranslator` 来解析你的格式，生成带有 `ClothRoot` 标签和 solver 属性的场景节点。
2.  创建一个自定义管线来处理这些节点。

**关键常量定义** (来自 `InterchangeChaosClothAssetDefinitions.h`):
```cpp
namespace UE::Interchange::ChaosCloth
{
    // 布料根节点的标签
    inline const FString ClothRootTag = TEXT("ClothRoot");
    // 存储渲染和模拟网格的属性名
    inline const FString RenderMeshesAttributeName = TEXT("ClothRenderMeshes");
    inline const FString SimMeshesAttributeName = TEXT("ClothSimMeshes");
    // 注入到 Dataflow 图中的变量名
    inline const FName ImportedCollectionVariableName = TEXT("ImportedCollection");
    // Solver 属性键名
    inline const FString SolverAirDamping = TEXT("airDamping");
    inline const FString SolverGravity = TEXT("gravity");
    // ...
}
```

## Demo 示例

此插件是编辑器导入工具链的一部分，不直接提供运行时蓝图或 C++ 接口用于演示。其使用方式完全通过 **Interchange 导入对话框** 和 **项目设置中的导入管线配置** 来完成。

一个典型的配置演示流程如下：

1.  在 `Project Settings > Interchange > Pipelines` 中，可以找到并配置 "ChaosClothAsset" 管线。
2.  在 `Import` 时，在弹出的 Interchange 对话框中，选择此管线并调整参数。

## 模块依赖

从 `.uplugin` 的 `Plugins` 部分以及此插件的功能定位分析，其主要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Interchange` | 提供基础的资产翻译、管线、工厂和节点框架 |
| `ChaosClothAsset` | 提供目标资产 `UChaosClothAsset` 及其运行时组件 |
| `ChaosClothAssetDataflowNodes` | 提供布料相关的 Dataflow 节点，用于构建布料数据处理图 |
| `DataflowEngine` | 提供 Dataflow 图资产的加载和实例化功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `c97da6bd` | Interchange ClothAsset: Use ShortName on the new modules to mitigate some long filepath issues | 修复模块路径过长问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的编译警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 新增布料资产重导入支持 |
| 2026-04-27 | `60127194` | [ChaosClothAsset] Simple fix for static analysis violation | 修复静态代码分析违规 |
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | 为 USD 导入添加 ChaosCloth 支持 |

### 维护评价

- **活跃维护**：插件在最近一个月内有多次更新，包括功能增加（重导入支持）、编译修复和架构改进。
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion` 为 `true`，且默认未启用（`EnabledByDefault: false`），表明此功能仍在开发和完善中，API 和行为可能发生变化。
- **功能完整**：已实现从导入管线配置到资产生成的基本完整流程，并开始处理重导入等高级场景。
- **推荐程度**：**仅推荐用于实验和测试目的**。由于其为实验性插件且默认禁用，不建议在重要的生产项目中依赖它。应关注其后续版本，等待其成熟并正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset)
- 官方文档：暂无
- 测试用例：未在提供的源码信息中发现