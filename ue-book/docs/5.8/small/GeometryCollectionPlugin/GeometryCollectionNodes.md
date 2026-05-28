# Geometry Collection Plugin

> Adds Geometry Collection Container.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合容器 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

GeometryCollectionPlugin 是 UE5 中用于程序化破碎（Procedural Fracture）和可破坏几何体的核心基础设施。它提供了一个名为 **Geometry Collection** 的数据容器，能够存储层级化的破碎几何体（mesh 集合、变换层级、材质索引、碰撞凸包等），配合 **Dataflow** 节点图系统，实现了从源网格到破碎资产的完整工作流。

该插件的核心价值在于：
- **程序化破碎管线**：通过 Voronoi、径向、网格、平面切割等方式将网格分解为碎片，并自动聚类（Cluster）为多层级结构
- **Dataflow 节点图**：提供数百个节点，覆盖破碎、聚类、选择、材质分配、UV、凸包生成、采样、骨架绑定等全流程
- **Chaos Destruction 集成**：与 Chaos 物理系统的 Destruction 功能配合，实现运行时可破坏物体

`EnabledByDefault=false` 且 `IsBetaVersion=true`，说明该插件仍处于实验阶段，需要手动启用。

## 使用场景

- 你需要制作可被物理系统实时破坏的建筑物 → 使用 Geometry Collection + Chaos Destruction
- 你需要在编辑器中以节点图方式程序化破碎资产 → 使用 Dataflow 编辑器中的 Geometry Collection 节点
- 你需要对破碎后的碎片进行层级聚类（Cluster）以控制破坏级别 → 使用 AutoCluster / Cluster / Flatten 等节点
- 你需要为破碎物体分配不同的内外材质 → 使用 AssignMaterialToCollection 节点
- 你需要将 StaticMesh 转换为 Geometry Collection 资产 → 使用 StaticMeshToCollection 节点
- 你需要为碎片生成精确的碰撞凸包 → 使用 CreateLeafConvexHulls / CreateClusterConvexHulls 节点
- 你需要将几何体转换为骨骼动画骨架 → 使用 MedialToAnimSkeleton / BindSkeletonToMesh 节点

## 蓝图用法

本插件的核心 API 不是传统的 `UFUNCTION(BlueprintCallable)`，而是通过 **Dataflow 节点图** 系统暴露。所有节点均为 `USTRUCT`，在 Dataflow 编辑器中以图形化节点形式使用。

### 核心节点 — 破碎（Fracturing）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `VoronoiFracture` | Voronoi 破碎，在指定点集合处将几何体分割为碎片 | `FVoronoiFractureDataflowNode` |
| `PlaneCutter` | 平面切割，使用平面集合切割几何体 | `FPlaneCutterDataflowNode` |
| `UniformScatterPoints` | 在包围盒内均匀散射 Voronoi 破碎点 | `FUniformScatterPointsDataflowNode_v2` |
| `RadialScatterPoints` | 以径向模式散射破碎点 | `FRadialScatterPointsDataflowNode_v2` |
| `GridScatterPoints` | 以网格模式散射破碎点 | `FGridScatterPointsDataflowNode` |
| `ClusterScatterPoints` | 聚集式散射点（模拟自然破碎模式） | `FClusterScatterPointsDataflowNode` |
| `ExplodedView` | 将碎片以爆炸视图方式展示，用于调试 | `FExplodedViewDataflowNode` |
| `VisualizeFracture` | 可视化破碎层级和颜色 | `FVisualizeFractureDataflowNode` |

### 核心节点 — 聚类（Clustering）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AutoCluster` | 自动将碎片聚类为指定数量或大小的簇 | `FAutoClusterDataflowNode` |
| `Cluster` | 将选中的骨骼在新父节点下聚类 | `FClusterDataflowNode` |
| `Flatten` | 将选定骨骼的层级展平 | `FClusterFlattenDataflowNode` |
| `Uncluster` | 取消选定节点的聚类 | `FClusterUnclusterDataflowNode` |
| `ClusterMerge` | 将选中骨骼合并到新父聚类 | `FClusterMergeDataflowNode` |
| `ClusterMergeToNeighbors` | 将选中骨骼合并到相邻聚类 | `FClusterMergeToNeighborsDataflowNode` |
| `ClusterMagnet` | 将选中骨骼与邻近骨骼分组聚类 | `FClusterMagnetDataflowNode` |

### 核心节点 — 选择（Selection）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CollectionTransformSelectAll` | 选中所有骨骼 | `FCollectionTransformSelectionAllDataflowNode` |
| `CollectionTransformSelectNone` | 清空选择 | `FCollectionTransformSelectionNoneDataflowNode` |
| `CollectionTransformSelectRandom` | 随机选择骨骼 | `FCollectionTransformSelectionRandomDataflowNode` |
| `CollectionTransformSelectRoot` | 选中根骨骼 | `FCollectionTransformSelectionRootDataflowNode` |
| `SelectByCollectionAttribute` | 按属性值筛选选择 | `FSelectByCollectionAttributeDataflowNode` |
| `SelectByAttrValue` | 按属性值匹配选择 | `FSelectByAttrValueDataflowNode` |
| `SelectionIntersection` | 两个选择集的交集 | `FCollectionSelectionIntersectionDataflowNode` |
| `SelectionUnion` | 两个选择集的并集 | `FCollectionSelectionUnionDataflowNode` |

### 核心节点 — 资产与转换（Asset & Conversion）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StaticMeshToCollection` | 将 StaticMesh 转换为 Geometry Collection | `FStaticMeshToCollectionDataflowNode_v2` |
| `GeometryCollectionToCollection` | 将 Geometry Collection 资产转为可编辑的 Collection | `FGeometryCollectionToCollectionDataflowNode_v2` |
| `BlueprintToCollection` | 从 Blueprint 资产创建 Geometry Collection | `FBlueprintToCollectionDataflowNode_v2` |
| `GeometryCollectionTerminal` | 终端节点，将处理结果保存为 Geometry Collection 资产 | `FGeometryCollectionTerminalDataflowNode_v2` |
| `GetGeometryCollectionAsset` | 获取当前 Dataflow 图关联的资产 | `FGetGeometryCollectionAssetDataflowNode` |
| `GetGeometryCollectionSources` | 获取用于创建 Collection 的原始网格信息 | `FGetGeometryCollectionSourcesDataflowNode` |

### 核心节点 — 材质（Materials）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeMaterialArray` | 从用户列表创建材质数组 | `FMakeMaterialInterfaceArrayDataflowNode` |
| `AssignMaterialToCollection` | 将材质分配到 Collection 的面集 | `FAssignMaterialInterfaceToCollectionDataflowNode` |
| `GetMaterialAsset` | 从资产获取材质接口 | `FGetMaterialInterfaceAssetDataflowNode` |
| `SetIntoMaterialsArray` | 在材质数组指定位置设置材质 | `FSetIntoMaterialInterfaceArrayDataflowNode` |
| `AddToMaterialArray` | 向材质数组添加材质 | `FAddToMaterialInterfaceArrayDataflowNode` |

### 核心节点 — 凸包与碰撞（Convex Hulls）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLeafConvexHulls` | 为叶子几何体创建碰撞凸包 | `FCreateLeafConvexHullsDataflowNode` |
| `CreateClusterConvexHulls` | 为聚类创建碰撞凸包 | `FCreateClusterConvexHullsDataflowNode` |
| `MergeConvexHulls` | 合并凸包 | `FMergeConvexHullsDataflowNode` |
| `MakeConvexDecompositionSettings` | 创建凸分解设置对象 | `FMakeDataflowConvexDecompositionSettingsNode` |

### 核心节点 — 网格操作（Mesh）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PointsToMesh` | 将点数组转换为 DynamicMesh | `FPointsToMeshDataflowNode` |
| `BoxToMesh` | 将包围盒转换为 DynamicMesh | `FBoxToMeshDataflowNode` |
| `StaticMeshToMesh` | 将 StaticMesh 转换为 DataflowMesh | `FStaticMeshToMeshDataflowNode_v2` |
| `ApplyGeometryScriptToMesh` | 对 DynamicMesh 应用 Geometry Script 处理器 | `FApplyMeshProcessorToMeshDataflowNode` |
| `ApplyGeometryScriptToCollection` | 对 Collection 中选中变换的几何体应用处理器 | `FApplyMeshProcessorToGeometryCollectionDataflowNode` |
| `TransformMesh` | 变换 DataflowMesh（平移/旋转/缩放） | `FTransformMeshDataflowNode_v2` |
| `RemoveMeshOverlaps` | 移除网格之间的重叠 | `FRemoveMeshOverlapsDataflowNode` |

### 核心节点 — 采样（Sampling）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UniformPointSampling` | 在网格上均匀采样点 | `FUniformPointSamplingDataflowNode_v2` |
| `NonUniformPointSampling` | 在网格上非均匀采样点 | `FNonUniformPointSamplingDataflowNode_v2` |
| `FilterPointsWithMesh` | 用网格过滤点集（内部/外部） | `FFilterPointSetWithMeshDataflowNode_v2` |
| `BakeVertexToTexture` | 将顶点属性烘焙到纹理 | `FBakeVertexToTextureDataflowNode` |

### 使用示例（Dataflow 图描述）

典型的破碎工作流如下：

1. **输入资产**：使用 `GetGeometryCollectionAsset` 节点获取当前编辑的 Geometry Collection
2. **转换为可编辑数据**：使用 `GeometryCollectionToCollection` 将资产转为 `FManagedArrayCollection`
3. **生成破碎点**：使用 `UniformScatterPoints` 在包围盒中生成 Voronoi 破碎点
4. **执行破碎**：使用 `VoronoiFracture` 传入 Collection 和破碎点
5. **自动聚类**：使用 `AutoCluster` 将碎片分层聚类
6. **生成碰撞**：使用 `CreateLeafConvexHulls` 为叶子碎片创建碰撞凸包
7. **分配材质**：使用 `AssignMaterialToCollection` 为外表面和内切面分配不同材质
8. **输出资产**：使用 `GeometryCollectionTerminal` 将结果保存为 Geometry Collection 资产

## C++ 用法

> **重要提示**：本插件的核心工作流通过 Dataflow 节点图系统实现，而非直接的 C++ API。C++ 用法主要涉及自定义 Dataflow 节点的开发。

### 头文件引入

```cpp
#include "GeometryCollectionNodesPlugin.h"

// 引入各节点类别
#include "Dataflow/GeometryCollectionFracturingNodes.h"
#include "Dataflow/GeometryCollectionClusteringNodes.h"
#include "Dataflow/GeometryCollectionUtilityNodes.h"
#include "Dataflow/GeometryCollectionSelectionNodes.h"
#include "Dataflow/GeometryCollectionAssetNodes.h"
#include "Dataflow/GeometryCollectionMaterialInterfaceNodes.h"
```

### 基本用法 — 创建自定义 Dataflow 节点

所有 Dataflow 节点均继承自 `FDataflowNode`，通过 `USTRUCT` 宏定义，并使用 `DATAFLOW_NODE_DEFINE_INTERNAL` 注册。

```cpp
// 来源: Public/Dataflow/GeometryCollectionClusteringNodes.h
USTRUCT(meta = (DataflowGeometryCollection))
struct FMyCustomNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomNode, "MyCustomNode", "MyCategory", "")

    // 输入：Geometry Collection（支持直通）
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowIntrinsic))
    FManagedArrayCollection Collection;

    // 输入：变换选择集
    UPROPERTY(meta = (DataflowInput, DisplayName = "TransformSelection", DataflowIntrinsic))
    FDataflowTransformSelection TransformSelection;

    FMyCustomNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&TransformSelection);
        RegisterOutputConnection(&Collection, &Collection);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

### 进阶用法 — 注册节点

每个节点类别都有一个注册函数，在模块启动时调用：

```cpp
// 来源: Public/Dataflow/GeometryCollectionNodesPlugin.h
namespace UE::Dataflow
{
    void GeometryCollectionClusteringNodes();     // 注册聚类节点
    void GeometryCollectionFieldNodes();           // 注册场节点
    void GeometryCollectionFracturingNodes();      // 注册破碎节点
    void GeometryCollectionMakeNodes();            // 注册创建节点
    void GeometryCollectionMathNodes();            // 注册数学节点
    void GeometryCollectionMeshNodes();            // 注册网格节点
    void GeometryCollectionSelectionNodes();       // 注册选择节点
    void GeometryCollectionUtilityNodes();         // 注册工具节点
    void GeometryCollectionArrayNodes();           // 注册数组节点
    void GeometryCollectionAssetNodes();           // 注册资产节点
    void GeometryCollectionEditNodes();            // 注册编辑节点
    void GeometryCollectionConversionNodes();      // 注册转换节点
    void GeometryCollectionOverrideNodes();        // 注册覆盖节点
    void GeometryCollectionDebugNodes();           // 注册调试节点
    void GeometryCollectionEngineNodes();          // 注册引擎节点
    void RegisterGeometryCollectionMaterialInterfaceNodes(); // 注册材质节点
    void RegisterGeometryCollectionTextureNodes(); // 注册纹理节点
    void RegisterGeometryCollectionUVNodes();      // 注册UV节点
    void GeometryCollectionVerticesNodes();        // 注册顶点节点
}
```

### 进阶用法 — 带几何 Script 处理器的节点

插件支持通过蓝图定义的 `UDynamicMeshProcessorBlueprint` 动态扩展网格处理能力：

```cpp
// 来源: Public/Dataflow/GeometryCollectionMeshNodes.h
USTRUCT(meta = (DataflowGeometryCollection))
struct FApplyMeshProcessorToGeometryCollectionDataflowNode : public FMeshProcessorDataflowNodeBase
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FApplyMeshProcessorToGeometryCollectionDataflowNode, 
        "ApplyGeometryScriptToCollection", "Mesh|Utilities", "")

    // 支持选择 Blueprint 实现的 Mesh Processor
    UPROPERTY(EditAnywhere, Category = "Processor Type")
    TSubclassOf<UDynamicMeshProcessorBlueprint> MeshProcessor;

    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowIntrinsic))
    FManagedArrayCollection Collection;
};
```

## Demo 示例

### 自定义破碎处理节点

```cpp
// MyFractureModifierNode.h
#pragma once

#include "Dataflow/DataflowNode.h"
#include "GeometryCollection/GeometryCollection.h"

USTRUCT(meta = (DataflowGeometryCollection))
struct FMyFractureModifierDataflowNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyFractureModifierDataflowNode, "MyFractureModifier", "Custom|Fracture", "")

    // 输入/输出 Collection（直通）
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowIntrinsic))
    FManagedArrayCollection Collection;

    // 变换选择集
    UPROPERTY(meta = (DataflowInput, DisplayName = "TransformSelection"))
    FDataflowTransformSelection TransformSelection;

    // 破碎阈值
    UPROPERTY(EditAnywhere, Category = "Options", meta = (DataflowInput, ClampMin = 0.0, ClampMax = 1.0))
    float FractureThreshold = 0.5f;

    FMyFractureModifierDataflowNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&TransformSelection);
        RegisterInputConnection(&FractureThreshold);
        RegisterOutputConnection(&Collection, &Collection);
    }

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;
};
```

```cpp
// MyFractureModifierNode.cpp
#include "MyFractureModifierNode.h"
#include "Dataflow/DataflowReflection.h"

void FMyFractureModifierDataflowNode::Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const
{
    // 获取输入 Collection
    const FManagedArrayCollection& InCollection = GetValue(Context, &Collection);
    const FDataflowTransformSelection& Selection = GetValue(Context, &TransformSelection);
    const float Threshold = GetValue(Context, &FractureThreshold);

    FManagedArrayCollection Result = InCollection;

    // 遍历选中的变换
    for (int32 TransformIndex : Selection.AsSet())
    {
        // 对每个选中的变换应用自定义破碎修改逻辑
        // ... 自定义逻辑 ...
    }

    SetValue(Context, MoveTemp(Result), &Collection);
}
```

## 模块依赖

从各模块的 Build.cs 分析，该插件的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `GeometryCollection` | 核心几何集合数据结构 |
| `GeometryCollectionEngine` | 几何集合引擎运行时支持 |
| `GeometryCollectionSimulationCore` | 几何集合模拟核心 |
| `Chaos` / `ChaosSolverEngine` | Chaos 物理破碎系统 |
| `Dataflow` | Dataflow 节点图框架 |
| `GeometryFramework` | 几何体框架 |
| `ModelingComponents` | 建模组件 |
| `DynamicMesh` | 动态网格数据结构 |
| `MeshConversion` | 网格格式转换 |
| `PlanarCut` | 平面切割算法 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 的本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 相关更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退 CL53945814 的修改 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 相关更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增创建几何集合外部碰撞的节点 |

### 维护评价

- **活跃维护中**：最近一次更新在 2026-05-23，距今仅数天，持续有功能性更新
- **实验性标记**：`IsBetaVersion=true`、`EnabledByDefault=false`，仍在实验阶段
- **大量废弃节点**：源码中有许多标记 `Deprecated = "5.6"` / `Deprecated = "5.8"` 的节点（如旧版材质、数组、选择节点），说明 API 在持续演进和优化
- **持续演进**：许多节点同时存在 v1（已废弃）和 v2 版本，反映了从 `UDynamicMesh` 到 `UDataflowMesh` 等核心类型的迁移
- **推荐使用**：虽然标记为实验性，但作为 Chaos Destruction 系统的核心基础设施，该插件在破坏类项目中是必不可少的。建议在生产环境中充分测试后使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档]()（.uplugin 中未提供 DocsURL）