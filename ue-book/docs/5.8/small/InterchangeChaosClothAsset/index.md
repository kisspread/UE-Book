# Interchange Chaos Cloth Asset

> Contains the classes and objects required to allow Interchange to produce Chaos Cloth Assets

| 属性 | 值 |
|---|---|
| 中文名 | Chaos布料资产导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产相关） |
| 模块 | `InterchangeChaosClothAssetImport` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-06-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset) | |

## 用途

此插件是 Unreal Engine 的 Interchange 框架与 Chaos 布料资产系统之间的桥梁。它的核心作用是为 Interchange 框架提供必要的工厂节点（Factory Node）、处理管线（Pipeline）和负载数据（Payload Data）类，使得从外部数字内容创建工具（如 Marvelous Designer、Clo3D 或其他支持 USD/OBJ 格式的软件）导出的布料模拟数据，能够通过 Interchange 流水线顺利导入并转换为引擎原生的 `UChaosClothAsset` 资产。

它解决的问题是：将复杂的布料模拟网格（Simulation Mesh）和渲染网格（Render Mesh）及其物理属性（如重力、阻尼）从 DCC 工具数据准确地映射到 Chaos 布料资产的 Dataflow 图和集合（Collection）中，实现布料资产的自动化、可配置化导入。

## 使用场景

- **从 Marvelous Designer/Clo3D 等服装设计软件导出服装布料数据**，需要在 Unreal Engine 中用于高品质布料实时模拟。
- **导入包含物理布料信息的 USD 或 OBJ 场景文件**，希望自动生成 Chaos Cloth 资产。
- **需要通过蓝图或自动化流程批量导入布料资产**，并统一设置求解器参数（如重力、阻尼）。
- **在项目管线中集成布料资产的重新导入（Reimport）功能**，确保源文件更新后资产能同步更新。

## 蓝图用法

### 导入设置节点

这些节点用于控制布料资产导入过程中的细节。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetImportSimulationMeshes` | 设置是否导入模拟网格到最终的布料资产中 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetImportRenderMeshes` | 设置是否导入渲染网格到最终的布料资产中 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetDataflowGraphPath` | 设置要实例化到生成的布料资产中的 Dataflow 图模板的资产路径 | `UInterchangeChaosClothAssetFactoryNode` |

### 求解器属性节点

这些节点用于在导入时设置或获取布料模拟求解器的物理参数。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetAirDamping` / `GetAirDamping` | 设置/获取空气阻尼 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetGravity` / `GetGravity` | 设置/获取重力向量 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetSubStepCount` / `GetSubStepCount` | 设置/获取子步进数量 | `UInterchangeChaosClothAssetFactoryNode` |
| `SetTimeStep` / `GetTimeStep` | 设置/获取时间步长 | `UInterchangeChaosClothAssetFactoryNode` |

### 使用示例（蓝图描述）

在 Interchange 导入对话框中选择或创建一个 `UInterchangeChaosClothAssetPipeline` 管线实例。在管线的属性面板中，可以勾选 `bImportClothAssets` 来启用布料导入，然后通过 `bImportSimulationMeshes` 和 `bImportRenderMeshes` 控制网格导入，通过 `DataflowGraphAsset` 指定 Dataflow 模板。这些设置会在导入流程中传递给对应的 `FactoryNode`，最终影响生成的布料资产。

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeChaosClothAssetFactoryNode.h"
#include "InterchangeChaosClothAssetPipeline.h"
#include "InterchangeChaosClothAssetFactory.h"
```

### 基本用法

在创建自定义的 Interchange 导入流程时，可以手动配置布料资产的导入参数。

```cpp
// 假设已从 InterchangeBaseNodeContainer 中获取到布料工厂节点
UInterchangeChaosClothAssetFactoryNode* ClothFactoryNode = GetClothFactoryNode(); // 获取节点

if (ClothFactoryNode)
{
    // 配置导入选项
    ClothFactoryNode->SetImportSimulationMeshes(true);
    ClothFactoryNode->SetImportRenderMeshes(true);
    ClothFactoryNode->SetDataflowGraphPath(FSoftObjectPath(TEXT("/Game/Dataflow/ClothTemplate.ClothTemplate")));

    // 配置求解器参数
    ClothFactoryNode->SetAirDamping(0.1f);
    ClothFactoryNode->SetGravity(FVector3f(0.f, 0.f, -980.f));
    ClothFactoryNode->SetSubStepCount(3);
    ClothFactoryNode->SetTimeStep(1.f/30.f);
}
```
*（此代码基于 `UInterchangeChaosClothAssetFactoryNode` 的公开 API 推导）*

### 进阶用法

了解 `UInterchangeChaosClothAssetFactory` 如何处理负载数据（Payload）。工厂会异步提取渲染网格和模拟网格的数据，并存储在 `RenderMeshPayloadDataArray` 和 `SimMeshPayloadDataArray` 中，最后合并成一个 `CombinedCollection` 作为最终的 `ImportedCollection` 变量覆盖到 Dataflow 图上。负载数据 `UInterchangeChaosClothAssetPayloadData` 包含了模拟网格的集合和渲染网格的模式映射。

## Demo 示例

一个最小化的 C++ 示例，展示如何在代码中使用工厂节点设置参数。

**MyClothImporter.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyClothImporter
{
public:
    void ConfigureClothImportOptions();
};
```

**MyClothImporter.cpp**
```cpp
#include "MyClothImporter.h"
#include "InterchangeChaosClothAssetFactoryNode.h"
#include "InterchangeChaosClothAssetPipeline.h"

void FMyClothImporter::ConfigureClothImportOptions()
{
    // 此示例仅演示节点API的用法。
    // 在实际插件流程中，这些节点由 Interchange 框架根据管线创建和管理。
    
    // 通常，你会在自定义管线的 `ExecutePipeline` 中访问或修改这些节点。
    UInterchangeChaosClothAssetPipeline* MyPipeline = NewObject<UInterchangeChaosClothAssetPipeline>();
    MyPipeline->bImportClothAssets = true;
    MyPipeline->bImportSimulationMeshes = true;
    MyPipeline->bImportRenderMeshes = true;
    MyPipeline->DataflowGraphAsset = FSoftObjectPath(TEXT("/Path/To/Your/Dataflow/Template"));
    
    UE_LOG(LogTemp, Log, TEXT("布料导入管线已配置。"));
}
```

## 模块依赖

要使用此插件的功能，你的项目或模块需要依赖以下插件：

| 模块 | 用途 |
|---|---|
| `Interchange` | 提供核心的资产交换框架 |
| `ChaosClothAsset` | 提供 `UChaosClothAsset` 资产类型和相关数据结构 |
| `ChaosClothAssetDataflowNodes` | 提供布料资产使用的 Dataflow 节点 |
| `DataflowEngine` | 提供 Dataflow 图引擎（`DataflowGraphPath` 属性所用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `c97da6bd` | Interchange ClothAsset: Use ShortName on the new modules to mitigate some long filepath issues | 使用模块的 ShortName 来缓解长文件路径问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告 |
| 2026-05-12 | `a7e94182` | Interchange Cloth Asset: Add support for reimporting; | 为 Interchange 布料资产添加了重新导入的支持 |
| 2026-04-27 | `60127194` | [ChaosClothAsset] Simple fix for static analysis violation | 修复了简单的静态分析违规问题 |
| 2026-04-27 | `665076e6` | USD Interchange: Add support for ChaosCloth asset. | USD Interchange 添加了对 ChaosCloth 资产的支持 |

### 维护评价

**综合评价：活跃开发中的实验性功能模块。**

- **年龄**：插件创建于2024年中，年龄尚不足2年，是一个较新的模块。
- **近期活动**：从2026年4月至今有密集的更新记录，集中在功能完善（支持重新导入）、平台扩展（USD支持）和代码质量优化（路径、警告、静态分析）上，表明其处于**活跃维护和功能扩展期**。
- **状态**：`.uplugin` 中明确标记 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着该功能尚未稳定，API 和行为可能在后续版本中发生变化，不建议在需要长期稳定性的核心生产管线中未经充分测试直接使用。
- **推荐**：推荐给需要探索或集成 Chaos 布料资产自动导入工作流的开发者，但应做好随引擎版本更新而调整代码的准备。适合用于原型开发、内部工具或作为未来生产流程的技术储备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset)
- 官方文档（无）
- [测试用例（可能位于）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/ChaosClothAsset/Tests)