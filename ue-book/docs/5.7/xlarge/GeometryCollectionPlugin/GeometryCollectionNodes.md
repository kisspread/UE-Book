# Geometry Collection Nodes

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何集合节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeometryCollectionNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionNodes) | |

## 用途

`GeometryCollectionNodes` 是一个仅 Runtime 的 Dataflow 节点模块，专门为 **GeometryCollection（几何集合）** 提供节点化的数据处理和生成功能。它解决了以下问题：

- **破碎与聚类**：通过 Voronoi、网格、数量等算法自动或手动将几何集合的块（Bones）分组为集群（Clusters）。
- **选择与编辑**：对变换、面、顶点进行选择、可见性、剔除等操作。
- **字段与纹理**：生成径向衰减场、烘焙纹理属性（距离、AO、曲率等）。
- **网格与材质**：在静态网格、动态网格、UV、材质接口之间转换和操作。
- **几何处理**：闭合几何、近似凸包生成、保凹槽的凸分解等。

该模块使艺术家和技术美术能够在 **Dataflow 编辑器**中以可视化脚本方式构建复杂的 GeometryCollection 处理管线，无需编写 C++ 代码。

## 使用场景

- **程序化破碎**：你需要对静态网格或骨骼网格生成多级破碎的 GeometryCollection → 使用 `UniformScatterPoints` 生成碎裂点，`RadialFalloffField` 控制损伤范围，`AutoCluster` 自动分组。
- **UV 与纹理烘焙**：需要将 Distance to External、Ambient Occlusion 等属性烘焙到 UV 通道的纹理中 → 使用 `AutoUnwrapUV` + `BakeTextureFromCollection`。
- **编辑已有集合**：你有一份破碎后的几何集合，想要隐藏某些碎片、合并或删除选中的块 → 使用 `CollectionTransformSelection*` 节点 + `PruneInCollection` / `SetVisibilityInCollection`。

## 蓝图用法

`GeometryCollectionNodes` 中的节点主要在 **Dataflow 编辑器** 中使用，蓝图本身无法直接调用这些 C++ 节点。但你可以通过 Dataflow 资产暴露参数到蓝图（通过 `Set Variable` 节点间接控制）。以下描述在 Dataflow 图表中的操作方式。

### 核心节点分类

| 分类 | 代表节点 | 说明 |
|---|---|---|
| 集合资产 | `GetCollectionFromAsset` | 从 UGeometryCollection 资产加载数据为 FManagedArrayCollection |
| 选择 | `CollectionTransformSelectAll` | 全选所有变换（Bones） |
| 选择操作 | `CollectionTransformSelectionSetOperation` (Deprecated) / `CollectionSelectionSetOperation` | 对两个选择进行交、并、差、异或 |
| 聚类 | `AutoCluster` | 按多种尺寸方法（数量、比例、网格、大小）自动分组 Bones |
| 碎裂 | `UniformScatterPoints` (v2) | 在给定包围盒内均匀生成随机点，用于后代 Voronoi 碎裂 |
| 材质 | `AddMaterialToCollection` / `AssignMaterialToCollection` | 为选定面分配外部/内部材质 |
| UV | `AddUVChannel` / `AutoUnwrapUV` / `MergeUVIslands` | 添加、展开、合并 UV 通道 |
| 纹理 | `BakeTextureFromCollection` | 将几何属性（距离、AO、法向、位置）烘焙为 4 通道图像 |
| 网格 | `StaticMeshToCollection` (v2) | 将 StaticMesh 转换为 GeometryCollection |
| 凸包 | `GenerateClusterConvexHulls` / `ConvexHullToMesh` | 生成或可视化凸包 |
| 调试 | `ConvexHullToMesh` / `SphereCoveringToMesh` | 将凸包或球体覆盖转化为动态网格用于预览 |

### 使用示例（蓝图描述）

在 Dataflow 编辑器中：

1. **从静态网格创建破碎集合**：放置 `StaticMeshToCollection` 节点，连接 StaticMesh 输入，设置 `bSetInternalFromMaterialIndex` 为 true → 输出 Collection。
2. **均匀碎裂**：放置 `UniformScatterPoints`，连接 BoundingBox（可从 `GetBoundingBox` 节点获取），设置 Min/Max 点数 → 输出 Points 连接到 `VoronoiFracture` 节点。
3. **自动聚类**：将上一步的 Collection 连接 `AutoCluster`，选择 SizeMethod 为 ByNumber，设置 ClusterSites = 10 → 输出分组后的 Collection。
4. **烘焙纹理**：连接 Collection 到 `BakeTextureFromCollection`，选择 RedChannel=DistanceToExternal，设置 Resolution=1024 → 输出 Image 可以导出为 UTexture2D。

## C++ 用法

`GeometryCollectionNodes` 模块主要提供 Dataflow 节点类，通常在 Dataflow 图表中实例化。但在 C++ 中也可以通过编程方式创建并评估节点。

### 头文件引入

```cpp
#include "Dataflow/DataflowEngine.h"
#include "GeometryCollectionNodes.h"          // 通用节点
#include "Dataflow/GeometryCollectionFracturingNodes.h"  // 碎裂节点
#include "Dataflow/GeometryCollectionClusteringNodes.h"  // 聚类节点
```

### 基本用法

从测试用例提取（模拟）：

```cpp
// test case: FractureTest.cpp
// 创建均匀散射点节点并评估
UDataflow* Dataflow = NewObject<UDataflow>();
FDataflowNode* ScatterNode = nullptr;

FUniformScatterPointsDataflowNode_v2* Scatter = 
    Dataflow->NewNode<FUniformScatterPointsDataflowNode_v2>(
        FNodeParameters(/*OwningObject*/Dataflow, /*Name*/"Scatter"));

// 设置输入参数
Scatter->MinNumberOfPoints = 10;
Scatter->MaxNumberOfPoints = 30;
Scatter->BoundingBox = FBox(FVector(-100), FVector(100));

// 执行评估
Dataflow->Evaluate(DataflowContext);

// 读取输出
TArray<FVector> Points = Scatter->Points;
```

### 进阶用法

组合多个节点构建完整处理管线：

```cpp
// 加载资产 → 执行 Voronoi 碎裂 → 自动聚类 → 烘焙纹理
#include "Dataflow/GeometryCollectionNodes.h"
#include "Dataflow/GeometryCollectionFracturingNodes.h"
#include "Dataflow/GeometryCollectionClusteringNodes.h"
#include "Dataflow/GeometryCollectionTextureNodes.h"

void BuildAndProcessGeometryCollection(UGeometryCollection* InAsset)
{
    UDataflow* Dataflow = NewObject<UDataflow>();

    // 1. 从资产获取集合
    auto* GetAsset = Dataflow->NewNode<FGetCollectionFromAssetDataflowNode>(/*...*/);
    GetAsset->CollectionAsset = InAsset;

    // 2. Voronoi 碎裂 (通过点集)
    auto* Fracture = Dataflow->NewNode<FVoronoiFractureDataflowNode>(/*...*/);
    Fracture->SetInput("Collection", GetAsset->GetOutput("Collection"));
    // 设置碎裂参数...

    // 3. 自动聚类
    auto* Cluster = Dataflow->NewNode<FAutoClusterDataflowNode>(/*...*/);
    Cluster->SetInput("Collection", Fracture->GetOutput("Collection"));
    Cluster->ClusterSizeMethod = EClusterSizeMethodEnum::Dataflow_ClusterSizeMethod_ByNumber;
    Cluster->ClusterSites = 20;

    // 4. 烘焙纹理
    auto* Bake = Dataflow->NewNode<FBakeTextureFromCollectionDataflowNode>(/*...*/);
    Bake->SetInput("Collection", Cluster->GetOutput("Collection"));
    Bake->Resolution = EDataflowImageResolution::Resolution1024;
    Bake->RedChannel = ECollectionBakeTextureAttribute::DistanceToExternal;

    // 执行整个图
    Dataflow->Evaluate();

    // 访问最终结果
    FManagedArrayCollection Result = *Bake->GetOutputValue<FManagedArrayCollection>("Collection");
    FDataflowImage* TextureImage = Bake->GetOutputValue<FDataflowImage>("Image");
}
```

## Demo 示例

以下是一个 **最小 C++ 程序**，演示如何使用 `GeometryCollectionNodes` 创建一个包含两个集合的合并操作并输出结果。

```cpp
// GeometryCollectionNodesDemo.h
#pragma once
#include "Dataflow/DataflowEngine.h"
#include "GeometryCollectionNodes.h"
#include "GeometryCollection/ManagedArrayCollection.h"

class FGeometryCollectionNodesDemo
{
public:
    void Run();
};

// GeometryCollectionNodesDemo.cpp
#include "GeometryCollectionNodesDemo.h"
#include "Dataflow/DataflowContext.h"

void FGeometryCollectionNodesDemo::Run()
{
    // 创建 Dataflow 引擎
    UDataflow* Dataflow = NewObject<UDataflow>(GetTransientPackage());

    // 创建第一个集合（假数据）
    FManagedArrayCollection ColA;
    // ... 填充数据 (省略细节)

    // 创建第二个集合
    FManagedArrayCollection ColB;
    // ... 填充数据

    // 添加 AppendCollections 节点
    FAppendCollectionAssetsDataflowNode* AppendNode =
        Dataflow->NewNode<FAppendCollectionAssetsDataflowNode>(
            FNodeParameters(Dataflow, TEXT("Append")));
    AppendNode->Collection1 = ColA;
    AppendNode->Collection2 = ColB;

    // 评估图
    Dataflow->Evaluate();

    // 获取结果
    FManagedArrayCollection Result = AppendNode->Collection1; // 注意 Collection1 是输出/通过
    UE_LOG(LogTemp, Log, TEXT("Resulting collection has %d transforms"),
        Result.NumElements(FTransformCollection::TransformGroup));
}
```

## 模块依赖

从 `GeometryCollectionNodes.Build.cs` 提取（根据头文件包含推断）：

| 模块 | 用途 |
|---|---|
| `DataflowNodes` | 核心 Dataflow 节点接口 |
| `GeometryCollectionEngine` | 几何集合运行时核心 |
| `FractureEngine` | 碎裂和凸包算法引擎 |
| `DynamicMesh` | 动态网格结构（用于凸包/球体预览） |
| `GeometryCollectionTracks` | (可选) 用于动画支持 |
| `ImageWrapper` | 纹理烘焙的图片编码 |

> 注意：标准依赖如 `Core`、`Engine`、`Slate` 等已省略。

## 维护状态

从 Git 历史看，该模块处于 **活跃维护** 状态，近期更新频繁。

### 近期更新

- 2025-09-25 `745ebb5` — Add support for override materials for geometry collection root proxies
- 2025-09-24 `787ab8b` — Add cvar to disable creation dialog when opening geometry collection dataflow
- 2025-09-23 `29aa54b` — Add settings for Dataflow editor
- 2025-09-16 `9a2a247` — Fix tetrahedron rendering crash with split geometry
- 2025-09-06 `38d85df` — Expose all properties of TransformCollection node as inputs

### 维护评价

- **创建时间**：2025-09-06（约 0.1 年），非常年轻。
- **更新频率**：几乎每周都有功能性更新或 bug 修复。
- **稳定性**：标记为实验性（Beta），但核心功能已可用。
- **推荐度**：**推荐使用**，适合需要程序化生成和编辑 GeometryCollection 的项目。注意仍处于实验阶段，API 可能变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Source/GeometryCollectionNodes)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/geometry-collections-in-unreal-engine/) （通用 GeometryCollection 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/GeometryCollectionPlugin/Tests)