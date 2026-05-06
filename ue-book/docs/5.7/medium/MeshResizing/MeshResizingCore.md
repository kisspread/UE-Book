# Mesh Resizing

> Mesh Resizing

| 属性 | 值 |
|---|---|
| 中文名 | 网格大小调整 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++模块） |
| 模块 | `MeshResizingCore` (Runtime), `MeshResizingEditorTools` (Runtime), `MeshResizingEngine` (Runtime), `MeshResizingDataflowNodes` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-15 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing) | |

## 用途

Mesh Resizing 插件提供了一套用于动态调整网格大小的核心工具集。它支持基于顶点映射、自定义区域、RBF 径向基函数插值和物理约束（剪切、弯曲、边缘拉伸）的变形算法，允许用户在保持网格几何特征和拓扑结构的前提下对网格进行非均匀缩放或形状调整。该插件处于实验阶段，底层算法侧重于提供高可控性的变形方式，适用于需要程序化调整角色、道具或环境网格尺寸的场景。

## 使用场景

- 在运行时或编辑器中调整角色网格的局部比例，以适应不同体型或服装形态。
- 自定义网格区域的渐进式变形，如局部膨胀、拉伸或收缩。
- 基于一组控制点或曲线驱动网格变形，实现类似蒙皮的效果。
- 对程序化生成的网格进行后续形状调整，无需重新建模。

## 蓝图用法

该模块为底层核心库，其 API 均为 C++ 静态函数，未暴露为蓝图节点。相关功能需要通过 C++ 扩展或编写蓝图函数库来封装。高级蓝图用法可参考 `MeshResizingEditorTools` 模块（若提供蓝图节点）。

## C++ 用法

### 头文件引入

```cpp
#include "MeshResizing/BaseBodyTools.h"
#include "MeshResizing/CustomRegionResizing.h"
#include "MeshResizing/Mesh3DConstraints.h"
#include "MeshResizing/RBFInterpolation.h"
```

### 基本用法

#### 顶点映射与代理网格生成（`FBaseBodyTools`）

```cpp
// 将原始顶点索引映射附加到动态网格
using namespace UE::Geometry;
using namespace UE::MeshResizing;

FDynamicMesh3 SourceMesh, TargetMesh;
// ... 填充网格数据

TArray<int32> VertexIDs;
// ... 填充顶点映射数据
bool bSuccess = FBaseBodyTools::AttachVertexMappingData(
    FBaseBodyTools::ImportedVertexVIDsAttrName,
    VertexIDs,
    SourceMesh
);

// 从源网格和目标网格生成可调整的代理网格
FDynamicMesh3 ProxyMesh;
bSuccess = FBaseBodyTools::GenerateResizableProxyFromVertexMappingData(
    SourceMesh,
    FBaseBodyTools::ImportedVertexVIDsAttrName,
    TargetMesh,
    FBaseBodyTools::RawPointIndicesVIDsAttrName,
    ProxyMesh
);

// 插值得到最终变形网格
bSuccess = FBaseBodyTools::InterpolateResizableProxy(
    SourceMesh,
    TargetMesh,
    0.5f,    // 混合系数
    ProxyMesh
);
```

#### 自定义区域调整（`FCustomRegionResizing`）

```cpp
using namespace UE::MeshResizing;

FDynamicMesh3 SourceMesh;
TSet<int32> BoundVertices;
TArray<FVector3f> BoundPositions;
FMeshResizingCustomRegion CustomRegion;

// 生成自定义变形区域数据
FCustomRegionResizing::GenerateCustomRegion(
    BoundPositions,
    SourceMesh,
    BoundVertices,
    CustomRegion
);

// 计算区域的局部坐标系
FVector3d Origin;
FVector3f TangentU, TangentV, Normal;
bool bOK = FCustomRegionResizing::CalculateFrameForCustomRegion(
    SourceMesh,
    CustomRegion,
    Origin,
    TangentU,
    TangentV,
    Normal
);
```

#### 物理约束变形（`FShearConstraint`、`FBendingConstraint` 等）

```cpp
using namespace UE::MeshResizing;

const int32 NumVerts = 1000;
TArray<float> ShearWeights;
ShearWeights.Init(1.0f, NumVerts);

FShearConstraint Shear(0.8f, ShearWeights, NumVerts);

FDynamicMesh3 ResizedMesh, InitialResizedMesh, BaseMesh;
TArray<float> InvMass;
InvMass.Init(1.0f, NumVerts);

// 应用剪切约束
Shear.Apply(ResizedMesh, InitialResizedMesh, BaseMesh, InvMass);
```

#### RBF 插值变形（`FRBFInterpolation`）

```cpp
using namespace UE::MeshResizing;

FDynamicMesh3 BaseMesh;
FMeshResizingRBFInterpolationData InterpData;

// 基于网格生成权重
FRBFInterpolation::GenerateWeights(BaseMesh, 64, InterpData);

// 获取目标点的位置并应用变形
TArray<FVector3f> TargetPositions;
// ... 填充目标点位置
TArray<FVector3f> DeformedPoints;
FRBFInterpolation::GenerateMeshSamples(TargetPositions, InterpData, DeformedPoints);

// 直接变形网格顶点
bool bInterpolateNormals = true;
FRBFInterpolation::DeformPoints(
    TargetPositions,
    InterpData,
    bInterpolateNormals,
    DeformingMesh
);
```

### 进阶用法

结合 `FBaseBodyTools` 的顶点映射和物理约束可以实现稳定且可控的网格缩放：

```cpp
// 1. 生成代理网格
FDynamicMesh3 Proxy;
FBaseBodyTools::GenerateResizableProxyFromVertexMappingData(Source, VIDAttr, Target, RawIdxAttr, Proxy);

// 2. 计算初始插值结果
FBaseBodyTools::InterpolateResizableProxy(Source, Target, 0.5f, Proxy);

// 3. 添加约束（保持边缘长度和弯曲角度）
TArray<float> EdgeWeights, BendWeights;
EdgeWeights.Init(1.0f, Proxy.VertexCount());
BendWeights.Init(1.0f, Proxy.VertexCount());
FEdgeConstraint Edge(0.9f, EdgeWeights, Proxy.VertexCount());
FBendingConstraint Bend(BaseMesh, 0.7f, BendWeights, Proxy.VertexCount());

TArray<float> InvMass;
InvMass.Init(1.0f, Proxy.VertexCount());

Edge.Apply(Proxy, Proxy, BaseMesh, InvMass);
Bend.Apply(Proxy, InvMass);
```

## Demo 示例

以下是一个完整的控制台示例，展示如何使用 RBF 插值和顶点映射对网格进行变形（依赖 `FDynamicMesh3` 和 `MeshResizingCore`）。

**MyMeshResizingDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyMeshResizingDemo
{
public:
    static void Run();
};
```

**MyMeshResizingDemo.cpp**
```cpp
#include "MyMeshResizingDemo.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "MeshResizing/RBFInterpolation.h"
#include "MeshResizing/BaseBodyTools.h"

void FMyMeshResizingDemo::Run()
{
    using namespace UE::Geometry;
    using namespace UE::MeshResizing;

    // 1. 创建一个简单的源网格（一个立方体）
    FDynamicMesh3 SourceMesh;
    SourceMesh.AddVertex(FVector3d(0,0,0));
    SourceMesh.AddVertex(FVector3d(1,0,0));
    SourceMesh.AddVertex(FVector3d(0,1,0));
    SourceMesh.AddVertex(FVector3d(1,1,0));
    SourceMesh.AddVertex(FVector3d(0,0,1));
    SourceMesh.AddVertex(FVector3d(1,0,1));
    SourceMesh.AddVertex(FVector3d(0,1,1));
    SourceMesh.AddVertex(FVector3d(1,1,1));
    // 添加两个三角形面（未完整，仅示意）
    SourceMesh.AddTriangle(0,1,2);
    SourceMesh.AddTriangle(1,3,2);

    // 2. 生成 RBF 插值数据（使用所有顶点作为样本）
    TArray<int32> AllVertices;
    for (int32 VID : SourceMesh.VertexIndicesItr())
        AllVertices.Add(VID);
    FMeshResizingRBFInterpolationData InterpData;
    TArray<FVector3f> SourcePositions;
    for (int32 VID : AllVertices)
        SourcePositions.Add(FVector3f(SourceMesh.GetVertex(VID)));
    FRBFInterpolation::GenerateWeights(SourcePositions, SourcePositions.Num(), InterpData);

    // 3. 定义目标变形位置（将顶点向上移动）
    TArray<FVector3f> TargetPositions = SourcePositions;
    for (auto& Pos : TargetPositions)
        Pos.Z += 1.0f;

    // 4. 对源网格进行变形
    FDynamicMesh3 DeformedMesh = SourceMesh;
    TArray<FVector3f> DeformedPoints;
    FRBFInterpolation::GenerateMeshSamples(TargetPositions, InterpData, DeformedPoints);
    for (int32 i = 0; i < DeformedPoints.Num(); ++i)
    {
        DeformedMesh.SetVertex(AllVertices[i], FVector3d(DeformedPoints[i]));
    }

    // 5. 使用顶点映射工具验证（将源顶点 ID 映射到变形网格）
    FBaseBodyTools::AttachVertexMappingData(FBaseBodyTools::ImportedVertexVIDsAttrName, AllVertices, DeformedMesh);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 提供 `FDynamicMesh3` 网格数据结构 |
| `Chaos` | 提供物理约束求解器（`FPBDFlatWeightMap`、`FSolverReal` 等） |
| `MeshDescription` | 支持 `FMeshDescription` 格式的网格数据（用于 `RBFInterpolation`） |

> 其余依赖（Core、CoreUObject、Engine 等）为标准常见模块，未列出。

## 维护状态

### 近期更新

- 2025-09-29 `92ddeeb8` [MeshResizing] Fixed vertices per task allocation bug
- 2025-09-23 `ca2d126b` Dataflow Editor: make the tool add node buttons work for tools that don't operate on ManagedArrayCol
- 2025-08-19 `d66ea4c2` Dataflow landmark tool : fix some pointer checks
- 2025-08-19 `a5c868d7` Dataflow Landmark tool : fix the tool marking the node invalid even when no changes were made
- 2025-08-15 `e79d88de` Fix possible divide by zero in RBFInterpolation when the mesh is empty.

### 维护评价

该插件创建于 2025 年 8 月，属于实验性功能，目前仍在积极开发中。最近几个月有多次 bug 修复和与 Dataflow 工具相关的调整，表明开发团队持续投入。由于版本号仅为 0.1，API 可能不稳定，不建议在生产项目中使用核心 API。推荐在原型开发或非关键场景下试用，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshResizing)
- [官方文档]（无）
- [测试用例]（未提供）