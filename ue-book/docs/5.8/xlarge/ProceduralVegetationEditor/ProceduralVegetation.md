# Procedural Vegetation Editor

> Node Graph based Editor that allows users to create Nanite Foliage ready vegetation directly in the engine. Users can load Procedural Vegetation Presets that contain prebuilt data for a species, and customize/create variations using the node graph.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化植被编辑器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ProceduralVegetation` (Runtime), `ProceduralVegetationEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-29 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ProceduralVegetationEditor) | |

## 用途

ProceduralVegetationEditor 是一个基于 UE5 PCG（Procedural Content Generation）框架的**程序化植被创建系统**。它解决的核心问题是：**如何在引擎中直接创建符合植物学规律的、支持 Nanite Foliage 的植被资产**。

该插件的工作流程分为三大阶段：

1. **生长模拟（Grower）**：基于植物学模型（向光性、顶端优势、乙烯/生长素激素系统、叶序排列、重力弯曲等）模拟植物从种子到成熟体的生长过程。通过循环迭代来模拟季节性生长，产出完整的骨架结构（枝干点、分枝拓扑）。

2. **叶片分布（Foliage Distributor）**：在生长出的骨架上按照叶序、光照条件、枝干粗细等属性放置叶片实例。支持激素驱动（Hormone-Based）和参数化（Parametric）两种分布模式，以及方向控制（Aim Vector、Face Vector、Roll/Pitch/Yaw）。

3. **网格构建与导出（Mesher / Export）**：将骨架数据转换为可渲染的 3D 网格（支持骨架平滑、噪声变形、半径重映射、Displacement 等），最终导出为 StaticMesh 或 SkeletalMesh，支持 Nanite Foliage、骨骼动画（风力）、物理碰撞等。

## 使用场景

- 你需要在引擎中直接创建真实感植物（树木、灌木、草本），而不是用 DCC 工具建模 → 用 ProceduralVegetationEditor
- 你要制作支持 Nanite Foliage 的植被，利用 UE5 的 Nanite 虚拟几何体优化渲染 → 用此插件的导出流程
- 你希望植物有风力摇摆动画（Skeletal Mesh + 骨骼） → 导出为 SkeletalMesh 并配置 WindSettings
- 你需要植物自动避开环境中的碰撞体（柱子、墙壁、岩石） → 用 Object Interaction 节点设置碰撞避让/裁剪
- 你需要从一张植物图片快速生成 3D 骨架 → 用 Import Texture 2D 功能
- 你想链式组合多个 Grower（先长主干，再长侧枝），或在同一骨架上放置多种叶片 → 用 Subgraph 和多 Foliage Distributor 链

## 蓝图用法

此插件的核心交互方式是**PCG 节点图（Node Graph）**，而非传统的蓝图节点。所有设置均通过 PCG Graph 编辑器中的属性面板配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Grower` | 植物生长模拟主节点，从种子开始迭代生长 | `UPVGrowerSettings`（推断） |
| `Foliage Distributor` | 在骨架上分布叶片实例 | `UPVFoliageDistributorSettings` |
| `Foliage Palette` | 定义叶片网格列表及其条件属性 | `UPVFoliagePaletteSettings` |
| `Mesh Builder` | 将骨架转换为可渲染网格 | `UPVMeshBuilderSettings`（推断） |
| `Object Interaction` | 碰撞体交互（避让/裁剪） | `UPVObjectInteractionSettings` |
| `Manual Edit` | 手动编辑骨架（移动/删除枝干） | `UPVManualEditSettings` |
| `Subgraph` | 嵌入可复用的 PVE 子图 | `UPVSubgraphSettings` |
| `Graft Distributor` | 在已有骨架上嫁接新枝条/叶片 | `UPVGraftDistributorSettings` |
| `Recompute Point Scale` | 重算骨架点的半径缩放 | `UPVRecomputePointScaleSettings` |
| `Rotate Branches` | 旋转枝干方向 | `UPVRotateBranchesSettings`（推断） |
| `Carve` | 裁剪植物结构 | `UPVCarveSettings`（推断） |
| `Import Texture 2D` | 从图片提取植物骨架 | `UPVImportTexture2DSettings`（推断） |
| `Trunk Texture Setup` | 配置树皮纹理烘焙 | `UPVTrunkTextureSetupSettings`（推断） |
| `Export` | 导出为 Static/Skeletal Mesh | `UPVExportSettings`（推断） |
| `Distribution Hormone Based Settings` | 激素驱动的叶片分布参数 | `UPVDistributionHormoneBasedSettings` |
| `Mesh Builder Skeleton Shaping Settings` | 骨架噪声变形参数 | `UPVMeshBuilderSkeletonShapingSettings` |
| `Subgraph` | 可复用子图封装 | `UPVSubgraphSettings` |

### 节点分类

节点按颜色和功能分为以下类别（来自 `PV::Categories`）：

| 类别 | 颜色 | 说明 |
|---|---|---|
| Growth | 橙色 `#EFB09E` | 生长模拟相关节点 |
| Input Output | 金色 `#EFB441` | 输入输出节点 |
| Foliage | 绿色 `#7BF851` | 叶片分布相关节点 |
| Post Growth Modifiers | 黄色 `#FCFD58` | 生长后修改器 |
| Mesh | 青色 `#7DEDF1` | 网格构建相关节点 |
| Seed | 橙色 `#EFB09E` | 种子生成节点 |
| Development | 黑色 | 开发调试节点 |

### 使用示例（节点图描述）

**创建一棵基本树木：**

1. **Seed** 节点（或 Convert To Seed Point 从 PCG 点数据转换） → 输出种子点
2. **Grower** 节点 ← 连接 Seed 输出，配置：
   - `GrowthCycles`：5-15（决定树木大小）
   - `Phyllotaxy`：Spiral + Octastichous（叶序排列）
   - `TrunkGrowth.PlantTargetLength`：5.0m（目标高度）
   - `GravityParams.GravitationalForce`：9.8（重力）
   - `bSenescence`：true（允许枯死修剪）
3. **Foliage Distributor** 节点 ← 连接 Grower 输出，配置分布模式和方向
4. **Foliage Palette** 节点 ← 配置叶片网格和条件属性
5. **Mesh Builder** 节点 ← 连接 Grower 输出，配置网格细节和材质
6. **Export** 节点 ← 导出为 Nanite 支持的 Skeletal Mesh

**碰撞体避让：**
- **Object Interaction** 节点插入 Grower 和后续节点之间
- 配置 `Colliders` 数组，添加 Mesh + Transform + `CollisionType`（Avoid/TrimInside/TrimOutside）

## C++ 用法

此插件的核心逻辑通过 `FPVGrower`、`FPVMeshBuilder`、`FPVLightDetection` 等结构体的静态函数执行。

### 头文件引入

```cpp
#include "ProceduralVegetation.h"
#include "DataTypes/PVGrowerParams.h"
#include "Implementations/PVGrower.h"
#include "DataTypes/PVData.h"
```

### 基本用法

```cpp
// 从种子点生成植物骨架
// 来源: Private/Implementations/PVGrower.h

#include "Implementations/PVGrower.h"
#include "Implementations/PVGrowerData.h"
#include "DataTypes/PVGrowerParams.h"
#include "PVSeedGenerator.h"

// 创建种子点
FPVSeedPoint SeedPoint;
SeedPoint.Position = FVector::ZeroVector;
SeedPoint.ApicalDirection = FVector::UpVector;
SeedPoint.SeedPScale = 0.1f;

// 配置生长参数
FPVGrowerParams GrowerParams;
GrowerParams.GrowthCycles = 10;
GrowerParams.RandomSeed = 7023;
GrowerParams.TrunkGrowth.PlantTargetLength = 5.0f;
GrowerParams.TrunkGrowth.MaxGeneration = 15;
GrowerParams.TrunkGrowth.SegmentLength = 0.25f;

// 设置叶序
GrowerParams.Phyllotaxy.Type = EPVGrowthPhyllotaxyType::Spiral;
GrowerParams.Phyllotaxy.Formation = EPVGrowthPhyllotaxyFormation::Octasticious;
GrowerParams.Phyllotaxy.AxilAngle = 35.0f;

// 配置重力
GrowerParams.GravityParams.GravitationalForce = 9.8f;
GrowerParams.GravityParams.CellWeight = 0.05f;
GrowerParams.GravityParams.FoliageWeight = 0.05f;

// 执行生长（输出到 FManagedArrayCollection）
FManagedArrayCollection OutputCollection;
FPVGrower::Grow(SeedPoint, GrowerParams, OutputCollection);
```

### 进阶用法

```cpp
// 完整的生长 + 网格生成流程
// 来源: Private/Implementations/PVGrower.h, Private/Implementations/PVMeshBuilder.h

#include "Implementations/PVGrower.h"
#include "Implementations/PVMeshBuilder.h"
#include "DataTypes/PVData.h"

// 步骤1: 生长模拟
FManagedArrayCollection SkeletonCollection;
FPVGrower::Grow(SeedPoint, GrowerParams, SkeletonCollection);

// 步骤2: 配置网格构建参数
FPVMeshBuilderParams MeshBuilderParams;
MeshBuilderParams.MeshDetails.SkeletonResolution = 10;
MeshBuilderParams.MeshDetails.MinDivisions = 6;
MeshBuilderParams.MeshDetails.MaxDivisions = 12;
MeshBuilderParams.MeshDetails.AddEndCaps = true;

// 配置骨架噪声变形（每个分枝代数不同噪声）
FPVSkeletonShapingEntry ShapeEntry;
ShapeEntry.Generation = 1;
ShapeEntry.NoiseStrength = 5.0f;
ShapeEntry.NoiseFrequency = 0.05f;
ShapeEntry.Smoothness = 0.0f;
MeshBuilderParams.SkeletonShaping.Entries.Add(ShapeEntry);

// 配置半径控制
MeshBuilderParams.BranchRadius.DaVinciRuleStrength = 0.5f;
MeshBuilderParams.BranchRadius.MinRadius = 0.01f;

// 配置置换贴图
MeshBuilderParams.Displacement.Texture = DisplacementTexture; // UTexture2D*
MeshBuilderParams.Displacement.Strength = 0.5f;
MeshBuilderParams.Displacement.GenerationUpperLimit = 1;

// 步骤3: 生成动态网格
TObjectPtr<UDynamicMesh> OutMesh = NewObject<UDynamicMesh>();
FManagedArrayCollection PlantProfileCollection; // 可选的植物剖面数据
FPVMeshBuilder::GenerateDynamicMesh(
    SkeletonCollection,
    PlantProfileCollection,
    MeshBuilderParams,
    OutMesh
);

// 步骤4: 生成几何体集合（用于 Geometry Collection / Nanite）
FGeometryCollection GeometryCollection;
FPVMeshBuilder::GenerateGeometryCollection(
    SkeletonCollection,
    PlantProfileCollection,
    MeshBuilderParams,
    GeometryCollection
);
```

```cpp
// 光照检测
// 来源: Private/Implementations/PVLightDetection.h

#include "Implementations/PVLightDetection.h"

// 构建碰撞数据（场景中的遮挡体）
FPVColliderMeshData ColliderData;
TArray<FPVColliderParams> ColliderParams;
// ... 添加碰撞体参数
FPVLightDetection::BuildPVCollisionData(ColliderParams, ColliderData);

// 构建射线起点（从骨架的每个芽点发射）
TArray<FPVRaycastOrigin> RayOrigins = FPVLightDetection::BuildPVRayOriginData(Skeleton);

// 构建碰撞几何数据
TArray<FPVCollisionData> CollisionData = FPVLightDetection::BuildPVCollisionDataSkeleton(Skeleton);

// 执行光照检测（GPU 计算着色器）
TArray<FPVPointLightVectorData> LightResults =
    FPVLightDetection::ExecuteLightDetection(CollisionData, RayOrigins, ColliderData);
```

```cpp
// 使用 Facade 访问骨架数据
// 来源: Public/Facades/PVPointFacade.h, PVBranchFacade.h, PVFoliageFacade.h

#include "Facades/PVPointFacade.h"
#include "Facades/PVBranchFacade.h"
#include "Facades/PVFoliageFacade.h"

using namespace PV::Facades;

// 访问枝干数据
FBranchFacade BranchFacade(Collection);
if (BranchFacade.IsValid())
{
    for (int32 i = 0; i < BranchFacade.GetElementCount(); ++i)
    {
        int32 BranchNumber = BranchFacade.GetBranchNumber(i);
        int32 HierarchyNumber = BranchFacade.GetBranchHierarchyNumber(i);
        const TArray<int32>& Points = BranchFacade.GetPoints(i);
        const TArray<int32>& Children = BranchFacade.GetChildren(i);
        bool bIsTrunk = BranchFacade.IsTrunk(i);
    }
}

// 访问点数据
FPointFacade PointFacade(Collection);
if (PointFacade.IsValid())
{
    for (int32 i = 0; i < PointFacade.GetElementCount(); ++i)
    {
        FVector3f Position = PointFacade.GetPosition(i);
        float Scale = PointFacade.GetPointScale(i);
        float LengthFromRoot = PointFacade.GetLengthFromRoot(i);
    }
}

// 访问叶片数据
FFoliageFacade FoliageFacade(Collection);
if (FoliageFacade.IsValid())
{
    for (int32 i = 0; i < FoliageFacade.NumFoliageEntries(); ++i)
    {
        FFoliageEntryData Entry = FoliageFacade.GetFoliageEntry(i);
        // Entry.PivotPoint, Entry.UpVector, Entry.Scale 等
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PCG` | PCG 框架（节点图、Settings、Data 基类） |
| `GeometryCollectionEngine` | ManagedArrayCollection 数据存储和 GeometryCollection 输出 |
| `GeometryCore` / `GeometryFramework` | DynamicMesh 生成和网格操作 |
| `MeshDescription` | 网格构建和导入管线 |
| `DynamicMesh` | 运行时动态网格构建 |
| `NaniteCore` | Nanite Foliage 支持 |
| `MeshConversion` | 网格格式转换 |
| `RenderCore` | GPU 计算着色器（光照检测） |
| `ImageWriteQueue` | 纹理烘焙写入 |
| `PhysicsUtilities` | 物理资产导出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `6587e553` | [PVE] Fix for Material look broken in the saved sample content. | 修复示例内容中材质显示异常 |
| 2026-05-22 | `ef6788f5` | Fix crash on platforms using HotReload where ProceduralVegetationEditor.plugin attempts to register | 修复热重载平台的崩溃问题 |
| 2026-05-21 | `5b49f4b9` | [PV] Fixed Incorrect/misleading and missing tooltips for the following nodes | 修正多个节点的工具提示文本 |
| 2026-05-21 | `461f91d8` | Re-write PV::Export::Internal::ReplaceAssetInPackage to resolve various crashes in the engine when o | 重写资产替换逻辑以修复引擎崩溃 |
| 2026-05-20 | `dc74565d` | [PVE] Major fixes | 多项重大修复 |

### 维护评价

- **创建时间**：2025-08-29，非常新的插件（约 1 年）
- **活跃度**：近期（2026年5月）有密集的修复和改进，处于**活跃开发**阶段
- **实验性标记**：位于 `Experimental` 目录，.uplugin 中标注为实验性版本
- **初始状态**：首次提交即注明"Materials are broken on the sample assets and still need to be fixed"，说明仍在快速迭代
- **推荐使用**：此插件功能极为丰富（347 个源文件），已可使用但仍处于实验阶段，API 和功能可能随版本变化。适合对程序化植被有强需求的项目提前探索，但**不建议在生产环境的稳定版本中依赖**，需关注后续更新。