# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格缩放 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 (Dataflow 节点资产) |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

`MeshResizing` 是一个实验性的网格处理插件，其核心功能是**在保持网格拓扑结构和物理约束的前提下，对静态网格或骨骼网格进行“缩放”或“变形”**。与简单的缩放变换不同，该插件旨在生成更符合物理规律和原始形状特征的变形结果，适用于需要网格适配不同尺寸的资产（如服装、装备）或进行程序化形变的场景。它通过基于物理的约束（PBD）和基于径向基函数（RBF）的插值技术来实现高质量的网格变形。

## 使用场景

- **角色服装适配**：为不同体型（高矮胖瘦）的角色适配相同的服装基础网格。
- **程序化生成**：在 Dataflow 或运行时，动态调整环境资产（如管道、布料）的尺寸和形状。
- **动画制作**：在角色动画中，需要非线性的、基于物理的网格形变，而不是简单的骨骼蒙皮。
- **数据准备**：为需要特定尺寸比例的资产（如需要适配不同UI布局的3D图标）生成变体。

## 蓝图用法

该插件的核心功能通过 C++ 静态工具类和 Dataflow 节点提供。主要的蓝图交互可能通过 `MeshResizingDataflowNodes` 模块中定义的 Dataflow 节点实现，这些节点可以在 Dataflow 图中作为可操作的步骤使用。

### 核心节点 (Dataflow)

由于插件的核心逻辑以 C++ 工具类形式存在，蓝图可调用的高层接口主要体现在 Dataflow 节点中。从代码结构和 Dataflow 模块的命名推断，可能的节点包括：

| 节点 (推测) | 说明 | 所在模块 |
|---|---|---|
| `GenerateResizableProxy` | 根据源网格和目标网格的顶点映射数据，生成一个可调整大小的代理网格。 | `MeshResizingDataflowNodes` |
| `ApplyMeshConstraints` | 应用物理约束（剪切、弯曲、边长）到正在变形的网格上，以保持其形状特性。 | `MeshResizingDataflowNodes` |
| `DeformWithRBF` | 使用径向基函数插值，根据一组目标顶点位置来变形整个网格。 | `MeshResizingDataflowNodes` |

### 使用示例（蓝图/Dataflow图描述）

1.  **准备顶点映射**：使用 `BaseBodyTools::AttachVertexMappingData` 或类似工具，为源网格和目标网格（经过简单缩放）创建顶点对应的映射数据。
2.  **构建 Dataflow 图**：
    - 添加一个节点来读取或生成源网格和目标网格。
    - 使用 `GenerateResizableProxy` 节点，结合映射数据，生成一个初始的变形网格（Proxy Mesh）。
    - 将生成的代理网格连接到 `ApplyMeshConstraints` 节点，设置约束强度和权重，进行物理模拟以优化形状。
    - 最后，将结果输出到网格组件或保存为资产。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyTools.h"
#include "MeshResizing/Mesh3DConstraints.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/CustomRegionResizing.h"
```

### 基本用法

**1. 生成可调整大小的代理网格 (来自 `BaseBodyTools.h`)**

此功能用于根据顶点映射关系，将源网格的形变信息传递给目标网格，生成一个中间代理网格。

```cpp
// 假设 SourceMesh 和 TargetMesh 是 FDynamicMesh3，且已通过某种方式（如UV采样）建立了顶点映射。
TArray<int32> SourceMappingData; // 源网格每个顶点对应到基础网格的某个ID
TArray<int32> TargetMappingData; // 目标网格每个顶点对应到基础网格的某个ID

// 将映射数据附加到网格上
UE::MeshResizing::FBaseBodyTools::AttachVertexMappingData(
    UE::MeshResizing::FBaseBodyTools::ImportedVertexVIDsAttrName,
    SourceMappingData,
    SourceMesh
);
UE::MeshResizing::FBaseBodyTools::AttachVertexMappingData(
    UE::MeshResizing::FBaseBodyTools::ImportedVertexVIDsAttrName,
    TargetMappingData,
    TargetMesh
);

// 生成代理网格
UE::Geometry::FDynamicMesh3 ProxyMesh;
bool bSuccess = UE::MeshResizing::FBaseBodyTools::GenerateResizableProxyFromVertexMappingData(
    SourceMesh,
    UE::MeshResizing::FBaseBodyTools::ImportedVertexVIDsAttrName,
    TargetMesh,
    UE::MeshResizing::FBaseBodyTools::ImportedVertexVIDsAttrName,
    ProxyMesh
);
```

**2. 应用物理约束进行变形 (来自 `Mesh3DConstraints.h`)**

约束类用于在基于物理的变形（PBD）模拟中，约束网格的形状。

```cpp
// 初始化约束参数
float ShearStrength = 1.0f;
TArray<float> ShearWeights; // 每个粒子的权重
int32 NumParticles = ProxyMesh.VertexCount();

UE::MeshResizing::FShearConstraint ShearConstraint(ShearStrength, ShearWeights, NumParticles);
// ... 类似初始化其他约束 (FEdgeConstraint, FBendingConstraint)

// 在迭代求解循环中应用约束
for (int32 Iter = 0; Iter < NumIterations; ++Iter)
{
    // 应用外力或初始猜测
    // ...

    // 应用约束
    ShearConstraint.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);
    // EdgeConstraint.Apply(...);
    // BendingConstraint.Apply(...);
}
```

**3. 使用 RBF 插值进行网格变形 (来自 `RBFInterpolation.h`)**

RBF 插值适合根据稀疏的控制点（如标记的顶点）来变形整个密集网格。

```cpp
// BaseMesh 是原始网格，TargetPositions 是控制点变形后的目标位置
UE::Geometry::FDynamicMesh3 DeformingMesh = BaseMesh; // 复制一份用于变形

// 步骤1：生成插值权重数据（只需计算一次）
UE::MeshResizing::FMeshResizingRBFInterpolationData InterpolationData;
UE::MeshResizing::FRBFInterpolation::GenerateWeights(BaseMesh, NumInterpolationPoints, InterpolationData);

// 步骤2：根据目标位置变形网格
TArray<FVector3f> TargetPositions; // 假设已填充好与插值点对应的目标位置
UE::MeshResizing::FRBFInterpolation::DeformPoints(TargetPositions, InterpolationData, /*bInterpolateNormals=*/ true, DeformingMesh);

// 现在 DeformingMesh 包含了变形后的结果
```

### 进阶用法

结合自定义区域调整 (`CustomRegionResizing`) 和约束，实现局部精确控制的变形。

```cpp
// 1. 定义一个自定义区域（例如，基于某个三角面和边界框）
UE::MeshResizing::FMeshResizingCustomRegion CustomRegion;
TSet<int32> BoundVertices = { /* 属于该区域的顶点索引集合 */ };
TArray<FVector3f> BoundPositions; // 这些顶点的初始位置
UE::MeshResizing::FCustomRegionResizing::GenerateCustomRegion(BoundPositions, SourceMesh, BoundVertices, CustomRegion);

// 2. 计算该区域的坐标系
FVector3d Origin; FVector3f TangentU, TangentV, Normal;
UE::MeshResizing::FCustomRegionResizing::CalculateFrameForCustomRegion(SourceMesh, CustomRegion, Origin, TangentU, TangentV, Normal);

// 3. 定义新的边界框角点（表示新的位置和方向）
TArray<FVector3d> NewBoundsCorners; // 8个角点

// 4. 计算区域内顶点的新位置
TArray<FVector3f> NewBoundPositions;
NewBoundPositions.SetNum(CustomRegion.RegionVertices.Num());
UE::MeshResizing::FCustomRegionResizing::InterpolateCustomRegionPoints(CustomRegion, NewBoundsCorners, NewBoundPositions);

// 5. 使用这些新位置作为约束或RBF的目标点，驱动整个网格或局部网格的变形。
```

## Demo 示例

一个演示如何使用 RBF 插值将一个立方体变形为球体形状的最小示例。

**MeshResizingDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"

class FMeshResizingDemo
{
public:
    static void RunDeformationDemo();
};
```

**MeshResizingDemo.cpp**
```cpp
#include "MeshResizingDemo.h"
#include "MeshResizing/RBFInterpolation.h"
#include "Generators/GridBoxMeshGenerator.h"

void FMeshResizingDemo::RunDeformationDemo()
{
    // 1. 创建一个基础立方体网格
    UE::Geometry::FDynamicMesh3 BaseMesh;
    UE::Geometry::FGridBoxMeshGenerator BoxGen;
    BoxGen.Box = UE::Geometry::FOrientedBox3d(FVector3d::Zero(), FVector3d(50, 50, 50));
    BoxGen.Generate();
    BaseMesh.Copy(&BoxGen);

    // 2. 准备控制点和目标位置（将立方体顶角向球心拉近，模拟球体）
    const int32 NumVertices = BaseMesh.VertexCount();
    const int32 NumControlPoints = 8; // 使用立方体的8个角点作为控制
    TArray<FVector3f> TargetPositions;
    for (int32 i = 0; i < NumControlPoints; ++i)
    {
        FVector3f OriginalPos = (FVector3f)BaseMesh.GetVertex(i);
        FVector3f ToCenter = -OriginalPos.GetSafeNormal();
        // 将角点向内移动一段距离
        TargetPositions.Add(OriginalPos + ToCenter * 20.0f);
    }

    // 3. 生成权重
    UE::MeshResizing::FMeshResizingRBFInterpolationData InterpWeightData;
    UE::MeshResizing::FRBFInterpolation::GenerateWeights(BaseMesh, NumControlPoints, InterpWeightData);

    // 4. 执行变形
    UE::Geometry::FDynamicMesh3 DeformedMesh = BaseMesh;
    UE::MeshResizing::FRBFInterpolation::DeformPoints(
        TargetPositions,
        InterpWeightData,
        true, // 插值法线
        DeformedMesh
    );

    // DeformedMesh 现在是一个近似球体的网格。
    // 在实际插件中，您可能会将其应用到 UStaticMeshComponent 或保存为资产。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Chaos` | 提供基于物理的约束系统（PBD）所需的 `FPBDFlatWeightMapView` 等数学工具。 |
| `GeometryCore` | 提供核心的网格数据结构 `FDynamicMesh3` 及相关操作。 |
| `MeshDescription` | 用于处理引擎的网格描述资产，`FRBFInterpolation` 中部分函数使用它作为输入/输出。 |
| `DynamicMesh` | `FDynamicMesh3` 的运行时操作环境。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `a7802337` | Dataflow: | (标题) Dataflow相关更新。 |
| 2026-03-16 | `1f05dc85` | Adding includes before upcoming header cleanup. | 为即将到来的头文件清理添加包含声明。 |
| 2026-01-30 | `7b60de76` | Dataflow : add support to lasso to the paint tool by leveraging the newly added feature in the mesh | Dataflow：为绘画工具添加套索支持，利用网格模块的新功能。 |
| 2025-12-19 | `f86e1e20` | Dataflow : update a lot of nodes to use the new rendering system | Dataflow：更新大量节点以使用新的渲染系统。 |

### 维护评价

`MeshResizing` 插件创建于2024年底，目前处于 **实验性** 阶段（`IsExperimentalVersion=true`，且 `EnabledByDefault=false`）。从近期提交记录看，开发在 **2026年5月** 仍有活跃更新，主要集中在 Dataflow 节点的功能增强（如套索工具支持）和渲染系统适配上，同时也进行代码清理和警告修复。这表明该插件仍在 **积极开发和完善中**。

由于它是实验性插件，API 可能尚未稳定，且功能可能不完整。目前没有发现明显的废弃标记。**适合对前沿网格变形技术有探索需求的开发者关注和试用，但不建议用于关键的生产项目。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]() (暂无)