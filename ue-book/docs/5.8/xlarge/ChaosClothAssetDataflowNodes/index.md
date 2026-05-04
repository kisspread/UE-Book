# Chaos Cloth Asset Dataflow Nodes

> Dataflow node plugin required to edit a Cloth Asset.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `ChaosClothAssetDataflowNodes` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetDataflowNodes) | |

## 用途

该插件为 Chaos 布料资产（Cloth Asset）提供了一整套 **Dataflow 节点**，用于在 Dataflow 图编辑器中构建和编辑布料资产的完整工作流。它解决了以下核心问题：

- **布料网格的导入与转换**：从 USD/Datasmith 文件、已有 Cloth Asset、或模拟缓存中导入布料数据
- **网格拓扑操作**：重网格化（Remesh）、合并多个布料集合、删除元素、缝合（Stitch）
- **蒙皮与绑定**：将网格绑定到骨骼根节点、设置物理资产用于碰撞
- **权重图与选择集管理**：绘制/添加权重图、程序化生成选择集、选择集与权重图之间的转换
- **渲染网格处理**：将模拟网格复制到渲染网格、应用代理变形器（Proxy Deformer）、重算法线
- **高级功能**：服装缩放（Resizing）、UV 缩放、Morph Target 生成、顶点混合、自定义区域缩放

该插件是 ChaosClothAsset 插件的配套编辑器工具，本身不包含运行时逻辑，仅在编辑器中使用。

## 使用场景

- 你在使用 Chaos 布料系统制作角色服装 → 用此插件的 Dataflow 节点在图编辑器中构建布料资产
- 你需要从外部文件（USD）导入布料数据 → 使用 `USDImport` 节点（替代已废弃的 DatasmithImport）
- 你需要对布料网格进行重网格化以调整分辨率 → 使用 `Remesh` 节点
- 你需要为不同体型缩放服装 → 使用 `ApplyResizing` 和 `CustomRegionResizing` 节点
- 你需要将多个布料部件合并为一个完整服装 → 使用 `MergeClothCollections` 节点
- 你需要为布料绘制权重图来控制物理行为 → 使用 `WeightMap` 节点（替代已废弃的 `AddWeightMap`）
- 你需要从模拟缓存中导入布料动画 → 使用 `ImportSimulationCache` 节点

## 蓝图用法

该插件的所有节点均为 **Dataflow 节点**（`FDataflowNode` 子类），不直接暴露为蓝图节点。它们在 Dataflow 图编辑器中以节点形式使用，通过 `USTRUCT` 的 `UPROPERTY` 标记的 `DataflowInput`/`DataflowOutput` 元数据定义输入输出引脚。

### 核心节点一览

#### 网格导入与导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClothAssetImport` | 导入已有 Cloth Asset 到集合中 | `FChaosClothAssetImportNode` |
| `USDImport` | 从 USD 文件导入布料数据 | （替代已废弃的 DatasmithImport） |
| `ImportSimulationCache` | 从模拟缓存导入顶点数据 | `FChaosClothAssetImportSimulationCacheNode` |
| `ClothCollectionToDynamicMesh` | 将布料集合转换为动态网格 | `FChaosClothAssetCollectionToDynamicMeshNode` |
| `UpdateClothFromDynamicMesh` | 从动态网格更新布料集合属性 | `FChaosClothAssetUpdateClothFromDynamicMeshNode` |

#### 网格拓扑操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Remesh` | 对布料表面进行重网格化 | `FChaosClothAssetRemeshNode_v2` |
| `MergeClothCollections` | 合并多个布料集合为一个 | `FChaosClothAssetMergeClothCollectionsNode_v2` |
| `DeleteElement` | 删除布料集合中的指定元素 | `FChaosClothAssetDeleteElementNode` |
| `AddStitch` | 将一组顶点缝合在一起 | `FChaosClothAssetAddStitchNode` |
| `BlendVertices` | 从另一个集合混合顶点数据 | `FChaosClothAssetBlendVerticesNode` |
| `RecalculateNormals` | 重新计算渲染网格法线 | `FChaosClothAssetRecalculateNormalsNode` |
| `ReverseNormals` | 反转法线和/或三角形绕序 | `FChaosClothAssetReverseNormalsNode` |
| `CopySimulationToRenderMesh` | 将模拟网格复制到渲染网格 | `FChaosClothAssetCopySimulationToRenderMeshNode` |

#### 蒙皮与物理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BindToRootBone` | 将整个网格绑定到骨架根骨骼 | `FChaosClothAssetBindToRootBoneNode` |
| `SetPhysicsAsset` | 设置用于碰撞的物理资产 | `FChaosClothAssetSetPhysicsAssetNode` |
| `ProxyDeformer` | 添加代理变形器信息到渲染数据 | `FChaosClothAssetProxyDeformerNode`（已废弃） |
| `ApplyProxyDeformer` | 应用已有的代理变形器数据 | `FChaosClothAssetApplyProxyDeformerNode` |

#### 权重图与选择集

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WeightMap` | 添加/绘制权重图属性 | （替代已废弃的 AddWeightMap） |
| `Selection` | 创建和管理选择集 | `FChaosClothAssetSelectionNode_v2` |
| `ProceduralSelection` | 程序化生成选择集 | `FChaosClothAssetProceduralSelectionNode` |
| `SelectionToWeightMap` | 将选择集转换为权重图 | `FChaosClothAssetSelectionToWeightMapNode` |
| `SelectionToIntMap` | 将选择集转换为整数图 | `FChaosClothAssetSelectionToIntMapNode` |

#### 属性与查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Attribute` | 为指定组创建新属性 | `FChaosClothAssetAttributeNode_v2` |
| `ClothCollectionQuery` | 查询布料集合的属性信息 | `FChaosClothAssetCollectionQueryNode` |
| `GenerateSimMorphTarget` | 从布料集合生成模拟 Morph Target | `FChaosClothAssetGenerateSimMorphTargetNode` |

#### 缩放功能（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyResizing` | 应用服装缩放到目标网格 | `FChaosClothAssetApplyResizingNode` |
| `CustomRegionResizing` | 添加自定义区域缩放数据 | `FChaosClothAssetCustomRegionResizingNode` |
| `EnableUVResizing` | 启用 UV 缩放 | `FChaosClothAssetEnableUVResizingNode` |

### 使用示例（Dataflow 图描述）

**基础布料资产构建流程**：

1. 添加 `ClothAssetImport` 节点，指定要导入的 Cloth Asset
2. 连接到 `Remesh` 节点调整网格分辨率
3. 连接到 `Selection` 节点创建顶点选择集
4. 连接到 `WeightMap` 节点基于选择集绘制权重图
5. 连接到 `BindToRootBone` 节点绑定蒙皮
6. 连接到 `SetPhysicsAsset` 节点设置碰撞体
7. 连接到 `CopySimulationToRenderMesh` 节点生成渲染网格

**合并多部件服装**：

1. 多个 `ClothAssetImport` 节点分别导入各部件
2. 每个部件分别经过 `Remesh` 和 `Selection` 处理
3. 所有部件连接到 `MergeClothCollections` 节点的输入引脚
4. 合并后的集合继续后续处理

## C++ 用法

该插件的节点均为 Dataflow 系统的 `FDataflowNode` 子类，通过 `USTRUCT` 宏注册。以下展示如何在 C++ 中使用这些节点。

### 头文件引入

```cpp
#include "ChaosClothAsset/ImportNode.h"
#include "ChaosClothAsset/RemeshNode.h"
#include "ChaosClothAsset/SelectionNode.h"
#include "ChaosClothAsset/WeightMapNode.h"
#include "ChaosClothAsset/BindToRootBoneNode.h"
#include "ChaosClothAsset/SetPhysicsAssetNode.h"
```

### 基本用法

Dataflow 节点主要在编辑器的 Dataflow 图中使用，C++ 侧主要涉及节点的定义和评估。以下是节点评估的基本模式：

```cpp
// Dataflow 节点通过 Evaluate 函数执行逻辑
// 以 FChaosClothAssetBindToRootBoneNode 为例
void FChaosClothAssetBindToRootBoneNode::Evaluate(
    UE::Dataflow::FContext& Context, 
    const FDataflowOutput* Out) const
{
    // 获取输入的布料集合
    FManagedArrayCollection InCollection = GetValue<FManagedArrayCollection>(
        Context, &Collection);
    
    // 执行绑定逻辑...
    // 将结果设置到输出
    SetValue(Context, InCollection, &Collection);
}
```

### 进阶用法

**自定义 Dataflow 节点**：如果需要扩展布料 Dataflow 工作流，可以继承 `FDataflowNode` 创建自定义节点：

```cpp
#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyCustomClothNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomClothNode, "MyCustomNode", "Cloth", "My Custom Cloth Node")

    // 输入/输出布料集合（透传模式）
    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    // 自定义参数
    UPROPERTY(EditAnywhere, Category = "Custom")
    float MyParam = 1.0f;

    FMyCustomClothNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        // 注册输入输出引脚
        RegisterInputConnection(&Collection);
        RegisterOutputConnection(&Collection, &Collection); // 透传
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override
    {
        FManagedArrayCollection ClothCollection = GetValue<FManagedArrayCollection>(Context, &Collection);
        
        // 自定义处理逻辑...
        
        SetValue(Context, ClothCollection, &Collection);
    }
};
```

**使用可连接值类型**：插件提供了 `ConnectableValue` 系列结构体用于支持 Dataflow 连接：

```cpp
#include "ChaosClothAsset/ConnectableValue.h"

// FChaosClothAssetConnectableIStringValue - 可输入的字符串值
// FChaosClothAssetConnectableOStringValue - 可输出的字符串值
// FChaosClothAssetConnectableIOStringValue - 可输入输出的字符串值（透传）

// 在节点属性中使用
UPROPERTY(EditAnywhere, Category = "MyCategory")
FChaosClothAssetConnectableIStringValue SelectionName = {TEXT("DefaultSelection")};
```

## Demo 示例

以下展示一个自定义布料 Dataflow 节点的完整实现，该节点将布料集合中所有模拟顶点的 Y 坐标偏移指定值：

### MyClothOffsetNode.h

```cpp
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/ManagedArrayCollection.h"
#include "MyClothOffsetNode.generated.h"

USTRUCT(Meta = (DataflowCloth))
struct FMyClothOffsetNode final : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyClothOffsetNode, "ClothOffset", "Cloth", "Offset Sim Vertices Y")

public:
    FMyClothOffsetNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&Offset);
        RegisterOutputConnection(&Collection, &Collection);
    }

private:
    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

    UPROPERTY(Meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection"))
    FManagedArrayCollection Collection;

    /** Y 轴偏移量 */
    UPROPERTY(EditAnywhere, Category = "Offset", Meta = (DataflowInput))
    float Offset = 0.0f;
};
```

### MyClothOffsetNode.cpp

```cpp
#include "MyClothOffsetNode.h"

void FMyClothOffsetNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    FManagedArrayCollection ClothCollection = GetValue<FManagedArrayCollection>(Context, &Collection);
    const float YOffset = GetValue<float>(Context, &Offset);

    // 获取 3D 模拟顶点位置并偏移 Y 坐标
    if (TManagedArray<FVector3f>* SimPositions3D = ClothCollection.FindAttribute<FVector3F>(
            TEXT("SimVertices3D"), TEXT("Position")))
    {
        for (FVector3f& Pos : *SimPositions3D)
        {
            Pos.Y += YOffset;
        }
    }

    SetValue(Context, ClothCollection, &Collection);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosCloth` | Chaos 布料运行时模拟核心 |
| `ChaosClothAsset` | 布料资产定义和基础节点 |
| `Dataflow` | Dataflow 图系统框架 |
| `GeometryProcessing` | 几何处理工具（重网格化等） |
| `MeshResizing` | 网格缩放/RBF 插值 |

## 维护状态

### 近期更新

```
- 2026-04-21 600f5cce [Chaos Cloth Asset] Moved Cloth Asset modules out of beta.
- 2026-04-15 948c01a1 Dataflow : add a method to the view mode to inform about gizmo support
- 2026-04-14 66a98b79 Migrate UE_LOG to UE_LOGF.
```

### 维护评价

该插件创建于 2026 年 4 月 13 日，是一个**非常新的插件**。从近期提交记录来看：

- **活跃维护**：最近一周内有多次提交，包括功能更新（移出 beta 状态）和代码质量改进（日志迁移）
- **成熟度提升**：最新的 commit 明确将 Cloth Asset 模块移出 beta，表明 Epic 认为该功能已趋于稳定
- **实验性节点**：部分节点仍标记为 `Experimental`（如 `ApplyResizing`、`CustomRegionResizing`、`EnableUVResizing`、`Attribute`、`RecalculateNormals`、`ImportSimulationCache`），这些功能可能在未来版本中有 API 变化
- **废弃节点**：多个旧版节点标记为 `Deprecated`（如 `AddWeightMap`、`DatasmithImport`、`ProxyDeformer`），均有对应的替代节点
- **推荐使用**：✅ 推荐。作为 Chaos 布料系统的核心编辑工具，该插件是使用 Chaos 布料的必备组件，且正在被 Epic 积极维护

⚠️ **注意**：该插件为 Editor 类型，仅在编辑器中可用。部分实验性节点的 API 可能在后续版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/ChaosClothAssetDataflowNodes)
- [官方文档]()（暂无）
- [测试用例]()（暂未发现独立测试文件）