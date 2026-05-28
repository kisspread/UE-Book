# Geometry Collection Nodes

> Adds Geometry Collection Container.

| 属性 | 值 |
|---|---|
| 中文名 | 几何体集合节点 |
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Dataflow 节点库） |
| 模块 | `GeometryCollectionDepNodes` (Runtime), `GeometryCollectionEditor` (Runtime), `GeometryCollectionNodes` (Runtime), `GeometryCollectionSequencer` (Runtime), `GeometryCollectionTracks` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-07-31 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin) | |

## 用途

本插件提供了 **Dataflow 节点库**，用于在 Dataflow 图（可视化节点编辑器）中创建、处理和操作 **Geometry Collection（几何体集合）**。Geometry Collection 是 UE5 Chaos Destruction 系统的核心数据结构，它将一个完整网格体拆分为层级化的碎片集合，支持多层级破碎、聚类（Clustering）、凸包碰撞体生成、材质分配等。

**为什么存在**：在 Chaos Destruction 工作流中，艺术家和开发者需要一套可视化的、可组合的节点来定义破碎参数——包括切割点分布模式（Voronoi、径向、网格等）、聚类层级结构、碰撞凸包生成、材质内外表面分配等。本插件将这些功能封装为 Dataflow 节点，使几何体集合资产的创建过程完全数据驱动、可复现。

**注意**：本插件处于实验性/Beta 状态，`EnabledByDefault=false`，需要手动在 Plugins 面板中启用。

## 使用场景

- 你需要制作可破坏的建筑/物体 → 使用 Chaos Destruction + Geometry Collection，通过 Dataflow 图定义破碎效果
- 你需要对静态网格体进行程序化破碎 → 使用 Voronoi/Planar/Radial 切割节点生成碎片
- 你需要将碎片组织成多层级聚类 → 使用 AutoCluster、Cluster、Flatten 等聚类节点
- 你需要为每个碎片生成优化的碰撞凸包 → 使用 GenerateClusterConvexHulls 节点
- 你需要为内表面/外表面分配不同材质 → 使用 AssignMaterialToCollection 节点
- 你需要从静态网格体/骨骼网格体/蓝图创建几何体集合资产 → 使用 StaticMeshToCollection、SkeletalMeshToCollection 等导入节点
- 你需要自定义破碎效果（程序化裂缝、字段驱动破碎）→ 使用 Field 节点与 Boolean Mesh 节点

## 蓝图用法

本插件的核心 API 是 **Dataflow 节点**（`USTRUCT` + `FDataflowNode`），它们在 Dataflow 图编辑器中作为可视化节点使用，而非传统蓝图节点。以下是按功能分组的主要节点：

### 几何体集合资产节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StaticMeshToCollection` | 从静态网格体创建几何体集合 | `FStaticMeshToCollectionDataflowNode_v2` |
| `SkeletalMeshToCollection` | 从骨骼网格体创建几何体集合 | `FSkeletalMeshToCollectionDataflowNode` |
| `GeometryCollectionToCollection` | 将 UGeometryCollection 资产转换为 FManagedArrayCollection | `FGeometryCollectionToCollectionDataflowNode_v2` |
| `CreateGeometryCollectionFromSources` | 从几何体源数组创建集合 | `FCreateGeometryCollectionFromSourcesDataflowNode_v2` |
| `BlueprintToCollection` | 从蓝图资产创建几何体集合 | `FBlueprintToCollectionDataflowNode_v2` |
| `GeometryCollectionTerminal` | 终端节点，将处理结果保存为资产 | `FGeometryCollectionTerminalDataflowNode_v2` |
| `GetGeometryCollectionSources` | 获取几何体集合的源网格信息 | `FGetGeometryCollectionSourcesDataflowNode` |
| `AppendCollections` | 合并两个几何体集合 | `FAppendCollectionAssetsDataflowNode` |

### 破碎/切割节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `VoronoiFracture` | Voronoi 图破碎 | `FVoronoiFractureDataflowNode` |
| `PlaneCutter` | 平面切割（Planar Cut） | `FPlaneCutterDataflowNode` |
| `RadialCutter` | 径向切割 | `FRadialCutterDataflowNode` |
| `RemoveMeshOverlaps` | 移除网格体间的重叠 | `FRemoveMeshOverlapsDataflowNode` |
| `BooleanMeshes` | 布尔运算（交集/并集/差集） | 布尔节点 |

### 点分布节点（切割点生成）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UniformScatterPoints` | 均匀随机散点 | `FUniformScatterPointsDataflowNode_v2` |
| `ClusterScatterPoints` | 聚类散点 | `FClusterScatterPointsDataflowNode` |
| `RadialScatterPoints` | 径向散点 | `FRadialScatterPointsDataflowNode_v2` |
| `GridScatterPoints` | 网格散点 | `FGridScatterPointsDataflowNode` |
| `NoiseScatterPoints` | 噪声散点 | `FNoiseScatterPointsDataflowNode` |

### 聚类节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AutoCluster` | 自动聚类（支持多种聚类策略） | `FAutoClusterDataflowNode` |
| `Cluster` | 将选中骨骼聚类到新父节点下 | `FClusterDataflowNode` |
| `Uncluster` | 取消聚类 | `FClusterUnclusterDataflowNode` |
| `Flatten` | 将选中层级展平 | `FClusterFlattenDataflowNode` |
| `ClusterMerge` | 合并选中骨骼 | `FClusterMergeDataflowNode` |
| `ClusterMergeToNeighbors` | 合并到最近邻居 | `FClusterMergeToNeighborsDataflowNode` |
| `ClusterMagnet` | 磁力聚类（基于邻接关系） | `FClusterMagnetDataflowNode` |

### 选择节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CollectionTransformSelectAll` | 选中所有骨骼 | `FCollectionSelectionAllDataflowNode` |
| `CollectionTransformSelectRandom` | 随机选择骨骼 | `FCollectionSelectionRandomDataflowNode` |
| `CollectionTransformSelectRoot` | 选择根骨骼 | `FCollectionTransformSelectionRootDataflowNode` |
| `SelectByVolume` | 按体积选择 | `FSelectByVolumeDataflowNode` |
| `SelectByAttr` | 按属性选择 | 选择节点 |
| `CollectionSelectionToAttribute` | 将选择存储为属性 | `FCollectionSelectionToAttributeDataflowNode` |

### 碰撞/凸包节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateLeafConvexHulls` | 为叶子节点创建凸包碰撞体 | `FCreateLeafConvexHullsDataflowNode` |
| `GenerateClusterConvexHulls` | 为聚类节点创建凸包碰撞体 | 集群凸包节点 |
| `MakeConvexDecompositionSettings` | 创建凸包分解设置 | `FMakeDataflowConvexDecompositionSettingsNode` |

### 材质节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AssignMaterialToCollection` | 为集合面分配材质 | `FAssignMaterialInterfaceToCollectionDataflowNode` |
| `MakeMaterialArray` | 创建材质数组 | `FMakeMaterialInterfaceArrayDataflowNode` |
| `GetMaterialAsset` | 获取材质资产引用 | `FGetMaterialInterfaceAssetDataflowNode` |

### 编辑节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PruneInCollection` | 删除选中骨骼（空聚类自动清除） | `FPruneInCollectionDataflowNode` |
| `SetVisibilityInCollection` | 设置可见性 | `FSetVisibilityInCollectionDataflowNode` |
| `MergeInCollection` | 合并选中骨骼 | `FMergeInCollectionDataflowNode` |
| `ValidateGeometryCollection` | 验证并清理集合 | `FValidateGeometryCollectionDataflowNode` |

### 使用示例（Dataflow 图描述）

典型的破碎 Dataflow 图流程：

1. **导入**：`StaticMeshToCollection` → 输出 `Collection` 和 `Materials`
2. **点生成**：`UniformScatterPoints` 或 `RadialScatterPoints` → 输出 `Points`
3. **破碎**：`VoronoiFracture` ← 输入 `Collection` + `Points`
4. **聚类**：`AutoCluster` ← 输入 `Collection`
5. **碰撞**：`CreateLeafConvexHulls` ← 输入 `Collection`
6. **材质**：`AssignMaterialToCollection` ← 输入 `Collection` + `Materials`
7. **输出**：`GeometryCollectionTerminal` ← 输入 `Collection` + `Materials`

## C++ 用法

### 头文件引入

```cpp
#include "GeometryCollectionNodes.h"

// 按需引入特定功能头文件
#include "Dataflow/GeometryCollectionFracturingNodes.h"
#include "Dataflow/GeometryCollectionClusteringNodes.h"
#include "Dataflow/GeometryCollectionAssetNodes.h"
#include "Dataflow/GeometryCollectionSelectionNodes.h"
```

### 基本用法 — 注册节点

Dataflow 节点需要在模块启动时注册：

```cpp
// 来源: Public/Dataflow/GeometryCollectionNodesPlugin.h
#include "GeometryCollectionNodesPlugin.h"

void IGeometryCollectionNodesPlugin::StartupModule()
{
    // 注册各类节点到 Dataflow 框架
    UE::Dataflow::GeometryCollectionEngineNodes();        // 核心节点
    UE::Dataflow::GeometryCollectionFracturingNodes();     // 破碎节点
    UE::Dataflow::GeometryCollectionClusteringNodes();     // 聚类节点
    UE::Dataflow::GeometryCollectionSelectionNodes();      // 选择节点
    UE::Dataflow::GeometryCollectionMakeNodes();           // Make 节点
    UE::Dataflow::GeometryCollectionMaterialNodes();       // 材质节点（旧版）
    UE::Dataflow::RegisterGeometryCollectionMaterialInterfaceNodes(); // 材质节点（新版）
    UE::Dataflow::GeometryCollectionArrayNodes();          // 数组节点
    UE::Dataflow::GeometryCollectionMathNodes();           // 数学节点
    UE::Dataflow::GeometryCollectionConversionNodes();     // 转换节点
    UE::Dataflow::GeometryCollectionFieldNodes();          // 场节点
    UE::Dataflow::GeometryCollectionMeshNodes();           // 网格节点
    UE::Dataflow::GeometryCollectionSamplingNodes();       // 采样节点
    UE::Dataflow::GeometryCollectionUtilityNodes();        // 工具节点
    UE::Dataflow::GeometryCollectionEditNodes();           // 编辑节点
    UE::Dataflow::GeometryCollectionUVNodes();             // UV 节点
    UE::Dataflow::GeometryCollectionTextureNodes();        // 纹理节点
    UE::Dataflow::GeometryCollectionOverrideNodes();       // Override 节点
    UE::Dataflow::GeometryCollectionDebugNodes();          // 调试节点
    UE::Dataflow::GeometryCollectionEngineAssetNodes();    // 资产节点
    UE::Dataflow::GeometryCollectionVerticesNodes();       // 顶点节点
    UE::Dataflow::RegisterMeshToSkeletalMeshTerminalNode();// 骨骼网格终端
    UE::Dataflow::RegisterSubdivideMeshDataflowNodes();    // 细分节点
    UE::Dataflow::RegisterGeometryCollectionUVNodes();     // UV 节点
    UE::Dataflow::RegisterMeshMedialSkeletonConversionNodes(); // 骨架转换
    UE::Dataflow::RegisterMeshWeightEditingNodes();        // 权重编辑
}
```

### 进阶用法 — 创建自定义 Dataflow 节点

继承 `FDataflowNode` 并使用宏注册：

```cpp
// 来源: Public/Dataflow/GeometryCollectionFracturingNodes.h
// 自定义破碎节点结构体模式

USTRUCT(meta = (DataflowGeometryCollection))
struct FMyCustomNode : public FDataflowNode
{
    GENERATED_USTRUCT_BODY()
    // 注册节点: 显示名、分类、搜索关键字
    DATAFLOW_NODE_DEFINE_INTERNAL(FMyCustomNode, "MyCustom", "GeometryCollection|Custom", "")

    // 输入：几何体集合（穿透类型 = 输入输出共享）
    UPROPERTY(meta = (DataflowInput, DataflowOutput, DataflowPassthrough = "Collection", DataflowIntrinsic))
    FManagedArrayCollection Collection;

    // 输入：变换选择
    UPROPERTY(meta = (DataflowInput, DisplayName = "TransformSelection"))
    FDataflowTransformSelection TransformSelection;

    // 输入：用户参数
    UPROPERTY(EditAnywhere, Category = "Options", meta = (DataflowInput))
    float Intensity = 1.0f;

    // 输出
    UPROPERTY(meta = (DataflowOutput))
    TArray<FVector> OutputPoints;

    virtual void Evaluate(UE::Dataflow::FContext& Context, const FDataflowOutput* Out) const override;

    FMyCustomNode(const UE::Dataflow::FNodeParameters& InParam, FGuid InGuid = FGuid::NewGuid())
        : FDataflowNode(InParam, InGuid)
    {
        RegisterInputConnection(&Collection);
        RegisterInputConnection(&TransformSelection);
        RegisterInputConnection(&Intensity);
        RegisterOutputConnection(&Collection, &Collection);
        RegisterOutputConnection(&OutputPoints);
    }
};
```

### 进阶用法 — 凸包分解设置

```cpp
// 来源: Public/Dataflow/GeometryCollectionUtilityNodes.h
// 配置凸包分解参数

FDataflowConvexDecompositionSettings Settings;
Settings.MinSizeToDecompose = 5.0f;              // 最小分解体积（厘米）
Settings.MaxGeoToHullVolumeRatioToDecompose = 0.9f; // 几何体/凸包体积比阈值
Settings.ErrorTolerance = 2.0f;                   // 容差（厘米）
Settings.MaxHullsPerGeometry = 4;                 // 每个几何体最大凸包数
Settings.MinThicknessTolerance = 1.0f;            // 最小厚度
Settings.NumAdditionalSplits = 4;                 // 额外分割搜索次数

// 启用负空间保护模式
Settings.bProtectNegativeSpace = true;
Settings.bOnlyConnectedToHull = true;
Settings.NegativeSpaceTolerance = 2.0f;
Settings.NegativeSpaceMinRadius = 10.0f;
```

### 进阶用法 — 骨骼蒙皮转换

```cpp
// 来源: Private/Dataflow/MeshMedialSkeletonConversionNodes.h
// 中间骨架到动画骨架的转换选项

// 边权重方法
enum class EDataflowMedialSkeletonConversionEdgeWeightMethod : uint8
{
    EdgeLength,  // 优先短边（不适合动画骨架）
    ArrayOrder,  // 按数组顺序（推荐）
    AvgRadius    // 按平均半径
};

// 断开连接处理
enum class EDataflowMedialSkeletonConversionMergeDisconnectedMethod : uint8
{
    ConnectClosestBones,  // 连接最近骨对
    AddTopLevelRoot       // 添加顶层根节点
};

// 根节点选择方法
enum class EDataflowMedialSkeletonConversionSelectRootMethod : uint8
{
    ClosestToPoint,        // 最近点
    FarthestInDirection,   // 最远方向
    ClosestToBoundsCenter, // 最近包围盒中心
    LargestSphere,         // 最大球体
    ArrayOrder             // 数组顺序
};
```

## 模块依赖

从各模块的 Build.cs 分析，无特殊依赖（仅标准 Core/Engine/Slate 等）。

> ⚠️ 实际使用中需要依赖 `GeometryCollectionEngine`、`Dataflow`、`GeometryCollectionSimulationCore` 等引擎内部模块，这些是 Chaos Destruction 系统的核心依赖。具体依赖请参考各模块的 `.Build.cs` 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-23 | `176334d2` | Fix localization warnings for UE 5.8 | 修复 UE 5.8 本地化警告 |
| 2026-05-14 | `ae91b9c4` | Dataflow: | Dataflow 框架相关更新 |
| 2026-05-14 | `28e138a1` | [Backout] - CL53945814 | 回退 CL53945814 的改动 |
| 2026-05-14 | `88fb5004` | Dataflow: | Dataflow 框架相关更新 |
| 2026-05-14 | `d2897727` | Dataflow : add a node to create external collision on a geometry collection | 新增创建外部碰撞的节点 |

### 维护评价

- **创建时间**：2018 年 7 月，至今约 8 年历史
- **活跃维护**：✅ 是 — 2026 年 5 月仍有频繁更新，持续添加新功能节点（如 MeshResizing 相关节点、SkeletalMesh 终端节点、Subdivision 节点等）
- **版本状态**：⚠️ 仍标记为 Beta/实验性（`IsBetaVersion=true`, `EnabledByDefault=false`）
- **API 稳定性**：大量节点存在 v2 版本并标记旧版为 `Deprecated`（5.5/5.6/5.7/5.8），说明 API 持续在演进
- **代码质量**：存在大量废弃节点标记，旧节点通过 `meta = (Deprecated = "5.x")` 优雅过渡，新节点版本号后缀 `_v2`/`_v3` 清晰
- **推荐使用**：推荐在 Chaos Destruction 工作流中使用，但需注意版本兼容性。作为实验性插件，API 可能在未来版本中继续变动。这是 Geometry Collection Dataflow 工作流的核心节点库，不使用则无法创建程序化的破碎效果。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GeometryCollectionPlugin)
- [官方文档]()（无）