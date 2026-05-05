# Chaos Cloth Asset Editor

> Editor for modifying cloth assets（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow节点、编辑器工具） |
| 模块 | `ChaosClothAssetEditor` (Editor), `ChaosClothAssetDataflowNodes` (Runtime), `ChaosClothAssetEditorTools` (Runtime), `ChaosClothAssetTools` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor) | |

## 用途

ChaosClothAssetEditor 是一个基于 **Dataflow** 的布料资产编辑器插件，用于创建和编辑 **Chaos 布料资产** (`UChaosClothAsset`)。它解决了传统布料编辑流程复杂、不直观的问题，通过节点化的方式，让美术和技术美术能够以可视化、非破坏性的方式构建和配置布料模拟的完整流程，包括网格导入、拓扑修改、蒙皮、物理属性配置、约束设置等。

## 使用场景

- 你需要为角色创建复杂的、可精细控制的布料模拟（如长裙、斗篷、飘带）。
- 你需要从第三方软件（如 Marvelous Designer）导入布料网格，并在引擎内进行后续处理和优化。
- 你需要为布料的不同区域（如边缘、中心）设置不同的物理属性（如刚度、阻尼、质量）。
- 你需要通过节点图来实验和迭代布料的模拟效果，而不是通过传统的属性面板。

## 蓝图用法

本插件的核心功能通过 **Dataflow 图表** 实现，而非传统的蓝图函数。用户在编辑器中创建 `UChaosClothAsset` 资产，然后在 Dataflow 编辑器中使用本插件提供的节点来构建处理流程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClothAssetImport` | 将一个已有的 `UChaosClothAsset` 导入到当前图表中作为数据源。 | `FChaosClothAssetImportNode` |
| `SetPhysicsAsset` | 为布料集合指定一个用于碰撞检测的物理资产 (`UPhysicsAsset`)。 | `FChaosClothAssetSetPhysicsAssetNode` |
| `BindToRootBone` | 将整个网格（模拟网格和/或渲染网格）绑定到当前骨架的根骨骼。 | `FChaosClothAssetBindToRootBoneNode` |
| `AddStitch` | 在指定的顶点集上创建缝合线，将它们合并为一个3D顶点。 | `FChaosClothAssetAddStitchNode` |
| `SimulationGravityConfig` | 配置布料模拟的重力属性，支持缩放或覆盖世界重力。 | `FChaosClothAssetSimulationGravityConfigNode` |
| `SimulationMassConfig` | 配置布料粒子的质量模式（统一质量、总质量、密度）。 | `FChaosClothAssetSimulationMassConfigNode` |
| `SimulationStretchConfig` | 配置布料的拉伸约束属性（刚度、阻尼、求解器类型）。 | `FChaosClothAssetSimulationStretchConfigNode` |
| `SimulationBendingConfig` | 配置布料的弯曲约束属性（刚度、阻尼、静止角）。 | `FChaosClothAssetSimulationBendingConfigNode` |
| `SimulationMaxDistanceConfig` | 配置布料粒子距离其蒙皮位置的最大距离约束。 | `FChaosClothAssetSimulationMaxDistanceConfigNode` |
| `SimulationBackstopConfig` | 配置布料的背停（Backstop）约束，防止布料穿透角色身体。 | `FChaosClothAssetSimulationBackstopConfigNode` |
| `SimulationAnimDriveConfig` | 配置动画驱动约束，将布料拉向动画目标网格。 | `FChaosClothAssetSimulationAnimDriveConfigNode` |
| `CopySimulationToRenderMesh` | 将模拟网格复制到渲染网格，用于直接渲染模拟结果或简化流程。 | `FChaosClothAssetCopySimulationToRenderMeshNode` |
| `RecalculateNormals` | 重新计算几何体的法线（目前仅针对渲染网格）。 | `FChaosClothAssetRecalculateNormalsNode` |
| `ReverseNormals` | 反转几何体的法线和/或三角形绕序。 | `FChaosClothAssetReverseNormalsNode` |
| `TransformUVs` | 对UV坐标进行平移、旋转、缩放变换。 | `FChaosClothAssetTransformUVsNode` |
| `SelectionToWeightMap` | 将一个整数索引选择集转换为顶点权重图。 | `FChaosClothAssetSelectionToWeightMapNode` |
| `WeightMapToSelection` | 将一个顶点权重图转换为整数索引选择集。 | `FChaosClothAssetWeightMapToSelectionNode` |
| `ProceduralSelection` | 程序化生成一个布料选择集（如选择所有顶点）。 | `FChaosClothAssetProceduralSelectionNode` |
| `ClothCollectionQuery` | 查询一个布料集合的属性（如是否包含模拟网格）。 | `FChaosClothAssetCollectionQueryNode` |

### 使用示例（蓝图描述）

1.  **创建布料资产**：在内容浏览器中右键 -> `Animation` -> `Chaos Cloth Asset`。
2.  **打开Dataflow编辑器**：双击新创建的布料资产。
3.  **构建节点图**：
    - 从 `ClothAssetImport` 节点开始，或使用其他网格导入节点（如 `USDImport`）。
    - 连接 `SetPhysicsAsset` 节点来设置碰撞体。
    - 使用 `BindToRootBone` 节点绑定网格。
    - 串联多个 `Simulation*Config` 节点（如 `SimulationGravityConfig`, `SimulationMassConfig`, `SimulationStretchConfig`）来配置物理属性。这些节点通常通过 `Collection` 引脚串联。
    - 使用 `AddStitch` 节点创建缝合线。
    - 最后连接 `CopySimulationToRenderMesh` 节点来生成可渲染的网格。
4.  **预览与调整**：在Dataflow编辑器中实时预览布料模拟效果，并调整各节点的参数。

## C++ 用法

本插件的节点均为 `USTRUCT`，继承自 `FDataflowNode` 或 `FChaosClothAssetSimulationBaseConfigNode`。它们主要在 Dataflow 图表中使用，但也可以在 C++ 中程序化地创建和评估。

### 头文件引入

```cpp
#include "ChaosClothAsset/ImportNode.h"
#include "ChaosClothAsset/SetPhysicsAssetNode.h"
#include "ChaosClothAsset/SimulationGravityConfigNode.h"
// ... 其他需要的节点头文件
```

### 基本用法

创建并评估一个简单的节点。

```cpp
// 来源: Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/SetPhysicsAssetNode.h
// 创建一个设置物理资产的节点
FChaosClothAssetSetPhysicsAssetNode SetPhysicsNode(FDataflowNode::FNodeParameters());
SetPhysicsNode.PhysicsAsset = MyPhysicsAsset; // 设置物理资产

// 创建一个Dataflow上下文并评估节点
UE::Dataflow::FContext Context;
// ... (设置上下文所需的输入数据)
SetPhysicsNode.Evaluate(Context, nullptr); // 评估节点，结果会写入其输出引脚
```

### 进阶用法

组合多个节点来构建一个简单的处理链。

```cpp
// 来源: Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/ImportNode.h
// 来源: Engine/Plugins/ChaosClothAssetEditor/Source/ChaosClothAssetDataflowNodes/Public/ChaosClothAsset/SimulationGravityConfigNode.h

// 1. 创建导入节点
FChaosClothAssetImportNode ImportNode(FDataflowNode::FNodeParameters());
ImportNode.ClothAsset = MyClothAsset;
ImportNode.ImportLod = 0;

// 2. 创建重力配置节点
FChaosClothAssetSimulationGravityConfigNode GravityNode(FDataflowNode::FNodeParameters());
GravityNode.bUseGravityOverride = true;
GravityNode.GravityOverrideImported.ImportedValue = FVector3f(0.f, 0.f, -500.f); // 自定义重力

// 3. 在Dataflow上下文中连接并评估
UE::Dataflow::FContext Context;
// 评估导入节点，获取其输出的Collection
ImportNode.Evaluate(Context, nullptr);
FManagedArrayCollection ImportedCollection = ImportNode.Collection; // 假设评估后数据存储在此

// 将导入的Collection设置为重力节点的输入
GravityNode.Collection = ImportedCollection;
// 评估重力节点
GravityNode.Evaluate(Context, nullptr);
FManagedArrayCollection FinalCollection = GravityNode.Collection; // 经过重力配置的Collection
```

## Demo 示例

一个最小的自定义 Dataflow 节点示例，该节点仅将输入的布料集合作为输出传递。

**MyClothPassThroughNode.h**
```cpp
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"
#include "MyClothPassThroughNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyClothPassThroughNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyClothPassThroughNode, "MyPassThrough", "Cloth", "My Custom Pass Through Node")
    DATAFLOW_NODE_RENDER_TYPE("SurfaceRender", FName("FClothCollection"), "Collection")

public:
    FMyClothPassThroughNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid());

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;
};
```

**MyClothPassThroughNode.cpp**
```cpp
#include "MyClothPassThroughNode.h"

FMyClothPassThroughNode::FMyClothPassThroughNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid)
    : FDataflowNode(InParam, InGuid)
{
    // 注册输入输出引脚已在宏中完成
}

void FMyClothPassThroughNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 由于设置了 DataflowPassthrough，Collection 输入会自动传递到输出。
    // 此处可以添加自定义逻辑。
    // 例如，我们可以在这里修改Collection，但为了演示，我们直接传递。
    // 实际的传递逻辑由Dataflow框架根据Passthrough元数据处理。
}
```

## 模块依赖

从 Build.cs 的依赖关系分析，要使用此插件，你的模块需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | Chaos 布料资产的核心数据结构和运行时逻辑。 |
| `Dataflow` | Dataflow 节点图框架，是本插件所有节点的基础。 |
| `GeometryCollectionEngine` | 用于处理 `FManagedArrayCollection`，这是布料数据在节点间传递的主要格式。 |
| `Chaos` | Chaos 物理引擎，提供底层的布料模拟求解器。 |
| `MeshResizing` | 用于网格缩放和变形功能（如 `ApplyResizingNode`）。 |
| `ChaosClothAssetDataflowNodes` | 本插件提供的所有 Dataflow 节点定义。 |

## 维护状态

### 近期更新

```
- 2025-10-03 e6f9627a2106 Cloth Remesh Node: rollback behavior changes in V1 of the node
- 2025-09-15 b6acf678d9f4 Chaos Cloth Asset - Fixed an infinite loop while merging weightmaps using the MergeClothCollections node. Regression caused by the change to FName in CL 44486948.
- 2025-08-20 c1fe7e591bc1 Chaos Cloth Asset - Fixed a crash in the TransferSkinWeight node when a non-manifold mesh is used with the inpaint method, which is now prevented.
```

### 维护评价

- **创建时间**：2022年10月，是一个相对较新的插件。
- **最近更新**：最近的提交（2025年10月）是功能回滚和bug修复，表明插件仍在积极维护和迭代中。
- **活跃度**：**活跃维护**。最近一年内有多次实质性更新，包括新功能（如Remesh节点）和重要的bug修复。
- **已知问题/限制**：插件标记为 `IsBetaVersion=true`，意味着它仍处于测试阶段，API和功能可能会发生变化。部分节点（如 `SimulationPBDAreaSpringConfigNode`）已被标记为 `Deprecated`，应使用更新的节点替代。
- **推荐使用**：**推荐**。对于需要高级布料编辑功能的项目，这是一个强大且官方支持的工具。尽管是Beta版，但其活跃的维护状态和来自Epic Games的支持使其成为可靠的选择。建议关注其更新日志以了解API变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetEditor/Tests)