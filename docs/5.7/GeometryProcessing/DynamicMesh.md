# Geometry Processing

> Data Structures and Algorithms for Processing 2D and 3D Geometry（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Geometry |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（ChaosVisualDebugger 支持资源） |
| 模块 | `GeometryAlgorithms` (Runtime), `DynamicMesh` (Runtime), `MeshFileUtils` (DeveloperTool) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-08-18 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing) | |

## 用途

GeometryProcessing 是 UE5 的**底层几何处理基础设施**，提供用于处理 2D 和 3D 几何体的数据结构与算法。它不是一个面向最终用户的工具插件，而是为其他高级工具（如 MeshModelingToolset、ModelingToolsEditorMode、UVEditor 等）提供核心计算能力的**算法库**。

该插件解决的核心问题包括：

- **动态网格表示**：`FDynamicMesh3` 是 UE5 中替代 `UStaticMesh` 的运行时可编辑网格数据结构，支持增量修改（添加/删除顶点、三角形、边），无需重建整个网格
- **网格几何操作**：孔洞填充、网格镜像、法线修复、网格平滑、PN Triangles 细分等
- **UV 参数化与打包**：提供 LSCM（最小二乘共形映射）、Spectral Conformal 等 UV 展开算法，以及 UV 岛打包
- **纹理烘焙**：法线贴图、AO、曲率、高度图等纹理烘焙管线
- **网格修复**：方向修复、属性转移、拓扑修复等
- **数学求解器**：拉普拉斯平滑、约束变形、参数化求解等线性系统求解

**为什么存在**：UE5 的建模工具（Geometry Script、Modeling Tools）需要一个高性能、可增量编辑的网格数据结构和配套算法库，而传统的 `UStaticMesh` 不支持运行时编辑。GeometryProcessing 填补了这一空白。

## 模块概览

本插件包含三个模块：

| 模块 | 类型 | 职责 |
|---|---|---|
| **DynamicMesh** | Runtime | 核心动态网格数据结构、网格操作、UV 参数化、纹理烘焙、求解器 |
| **GeometryAlgorithms** | Runtime | 底层几何算法（空间查询、三角化、凸包等） |
| **MeshFileUtils** | DeveloperTool | 网格文件 I/O 工具（OBJ/STL 读写等） |

## 使用场景

- 你在使用 **Geometry Script** 蓝图做程序化建模 → 底层依赖此插件的 `FDynamicMesh3`
- 你在使用 **Modeling Tools** 编辑器工具进行网格编辑 → 底层依赖此插件的网格操作算法
- 你需要在运行时**动态修改网格**（如地形变形、程序化生成）→ 使用 `FDynamicMesh3`
- 你需要**烘焙法线贴图/AO** 到纹理 → 使用 `FMeshNormalMapBaker`、`FMeshOcclusionMapBaker`
- 你需要**UV 展开和打包** → 使用 `ConstructSpectralConformalParamSolver`、`FDynamicMeshUVPacker`
- 你需要**修复导入网格**的法线方向 → 使用 `FMeshRepairOrientation`
- 你需要**填充网格孔洞** → 使用 `FMinimalHoleFiller`、`FPlanarHoleFiller`
- 你在做 **Chaos 物理可视化调试** → 此插件被列为 SupportedPrograms

## 蓝图用法

本插件主要面向 C++ 开发者，**不直接暴露蓝图节点**。蓝图用户应通过以下上层插件间接使用：

- **Geometry Script**：提供 `UGeometryScriptLibrary_*` 蓝图函数库，底层调用本插件
- **Modeling Tools Editor Mode**：编辑器建模工具，底层调用本插件

如需在蓝图中使用网格操作功能，请使用 Geometry Script 插件。

## C++ 用法

### 头文件引入

```cpp
// DynamicMesh 核心
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAttributeSet.h"

// 网格操作
#include "Operations/MeshMirror.h"
#include "Operations/RepairOrientation.h"
#include "Operations/MinimalHoleFiller.h"
#include "Operations/PNTriangles.h"

// UV 参数化
#include "Solvers/MeshParameterizationSolvers.h"
#include "Parameterization/MeshUVPacking.h"

// 纹理烘焙
#include "Sampling/MeshNormalMapBaker.h"
#include "Sampling/MeshOcclusionMapBaker.h"
#include "Sampling/MeshCurvatureMapBaker.h"

// 求解器
#include "Solvers/ConstrainedMeshSmoother.h"
#include "Solvers/MeshLaplacian.h"
```

### 基本用法：创建和操作 FDynamicMesh3

```cpp
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::Geometry;

// 创建一个空的动态网格
FDynamicMesh3 Mesh;

// 添加三角形（三个顶点位置）
int32 V0 = Mesh.AppendVertex(FVector3d(0, 0, 0));
int32 V1 = Mesh.AppendVertex(FVector3d(1, 0, 0));
int32 V2 = Mesh.AppendVertex(FVector3d(0, 1, 0));
int32 T0 = Mesh.AppendTriangle(V0, V1, V2);

// 遍历所有三角形
for (int32 TriangleID : Mesh.TriangleIndicesItr())
{
    FIndex3i Tri = Mesh.GetTriangle(TriangleID);
    // 处理三角形...
}

// 获取顶点法线
FVector3d Normal = Mesh.GetTriNormal(T0);
```

### 基本用法：网格镜像

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/MeshMirror.h"

using namespace UE::Geometry;

// 假设 Mesh 已经有数据
FDynamicMesh3 Mesh;
// ... 填充网格数据 ...

// 沿 X 轴镜像并追加镜像副本
FVector3d Origin = FVector3d::Zero();
FVector3d Normal = FVector3d::UnitX(); // X 轴方向

FMeshMirror MirrorOp(&Mesh, Origin, Normal);
MirrorOp.bWeldAlongPlane = true;           // 沿镜像面焊接顶点
MirrorOp.WeldNormalMode = EMeshMirrorNormalMode::AverageMirrorNormals; // 平均法线
MirrorOp.MirrorAndAppend();
```

### 基本用法：修复法线方向

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/DynamicMeshAABBTree3.h"
#include "Operations/RepairOrientation.h"

using namespace UE::Geometry;

FDynamicMesh3 Mesh;
// ... 填充网格数据 ...

// 修复法线方向
FMeshRepairOrientation RepairOp(&Mesh);
RepairOp.OrientComponents(); // 局部修复各连通分量

// 如需全局一致方向（需要空间加速结构）
FDynamicMeshAABBTree3 Spatial(&Mesh);
RepairOp.SolveGlobalOrientation(&Spatial);
```

### 进阶用法：UV 参数化

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Solvers/MeshParameterizationSolvers.h"
#include "Parameterization/MeshUVPacking.h"

using namespace UE::Geometry;
using namespace UE::MeshDeformation;

FDynamicMesh3 Mesh;
// ... 填充网格数据，确保是单连通分量 ...

// 创建 Spectral Conformal UV 参数化求解器
auto Solver = ConstructSpectralConformalParamSolver(Mesh, false);

// 设置固定 UV 约束（至少需要 2 个固定点）
// Solver->SetFixedPosition(VertexID, UVPosition);
// Solver->Solve();

// UV 打包
FDynamicMeshUVOverlay* UVOverlay = Mesh.Attributes()->GetUVLayer(0);
FDynamicMeshUVPacker Packer(UVOverlay);
Packer.TextureResolution = 1024;
Packer.GutterSize = 2.0f;
Packer.StandardPack(); // 标准打包到 [0,1] 范围
```

### 进阶用法：纹理烘焙（法线贴图）

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/MeshTangents.h"
#include "Sampling/MeshNormalMapBaker.h"
#include "Sampling/MeshImageBakingCache.h"

using namespace UE::Geometry;

// 假设已有 BaseMesh（低模）和 DetailMesh（高模）
FDynamicMesh3 BaseMesh;
FDynamicMesh3 DetailMesh;

// 计算基础网格切线
TMeshTangents<double> BaseTangents(&BaseMesh);
BaseTangents.ComputeTriVertexTangents(
    [BaseUVOverlay = BaseMesh.Attributes()->GetUVLayer(0)](int TriID, int VertID, FVector2d& UV)
    {
        BaseUVOverlay->GetElement(VertID, UV);
    }
);

// 设置烘焙缓存（定义低模和高模之间的对应关系）
FMeshImageBakingCache BakeCache;
// ... 配置 BakeCache 的源网格、目标网格、UV 等 ...

// 创建法线贴图烘焙器
FMeshNormalMapBaker NormalBaker;
NormalBaker.SetCache(&BakeCache);
NormalBaker.BaseMeshTangents = &BaseTangents;
NormalBaker.Bake();

// 获取结果
const auto& ResultImage = NormalBaker.GetResult();
```

### 进阶用法：约束网格平滑

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "Solvers/ConstrainedMeshSmoother.h"
#include "Solvers/MeshLaplacian.h"

using namespace UE::Geometry;
using namespace UE::MeshDeformation;

FDynamicMesh3 Mesh;
// ... 填充网格数据 ...

// 创建约束网格平滑器（使用 Cotangent 拉普拉斯权重）
auto Smoother = ConstructConstrainedMeshSmoother(
    ELaplacianWeightScheme::Cotangent, Mesh);

// 设置约束顶点（固定位置）
// Smoother->SetConstraint(VertexID, TargetPosition, Weight);

// 求解线性系统
// Smoother->Solve();
```

## Demo 示例

### 完整示例：网格孔洞填充

```cpp
// MyHoleFillExample.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "DynamicMesh/MeshBoundaryLoops.h"
#include "Operations/MinimalHoleFiller.h"

class FMyHoleFillExample
{
public:
    /**
     * 填充网格中的所有边界孔洞
     * @param Mesh 要处理的动态网格
     * @return 成功填充的孔洞数量
     */
    static int32 FillAllHoles(UE::Geometry::FDynamicMesh3& Mesh);
};
```

```cpp
// MyHoleFillExample.cpp
#include "MyHoleFillExample.h"

using namespace UE::Geometry;

int32 FMyHoleFillExample::FillAllHoles(FDynamicMesh3& Mesh)
{
    // 1. 检测所有边界环
    FMeshBoundaryLoops BoundaryLoops(&Mesh, false);
    if (BoundaryLoops.GetLoopCount() == 0)
    {
        return 0; // 没有孔洞
    }

    int32 FilledCount = 0;

    // 2. 逐个填充孔洞
    for (int32 i = 0; i < BoundaryLoops.GetLoopCount(); ++i)
    {
        const FEdgeLoop& Loop = BoundaryLoops[i];

        // 使用最小孔洞填充器（产生准可展表面，重建锐边）
        FMinimalHoleFiller Filler(&Mesh, Loop);
        Filler.bOptimizeDevelopability = true;
        Filler.bOptimizeTriangles = true;

        if (Filler.Fill())
        {
            FilledCount++;
        }
    }

    return FilledCount;
}
```

### 完整示例：PN Triangles 细分

```cpp
// MySubdivideExample.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "Operations/PNTriangles.h"

class FMySubdivideExample
{
public:
    /**
     * 对网格应用 PN Triangles 曲面细分
     * @param Mesh 要细分的动态网格
     * @param Level 细分级别（递归次数）
     * @return 是否成功
     */
    static bool SubdivideMesh(UE::Geometry::FDynamicMesh3& Mesh, int32 Level);
};
```

```cpp
// MySubdivideExample.cpp
#include "MySubdivideExample.h"

using namespace UE::Geometry;

bool FMySubdivideExample::SubdivideMesh(FDynamicMesh3& Mesh, int32 Level)
{
    FPNTriangles PNTriOp(&Mesh);
    PNTriOp.TessellationLevel = Level;
    PNTriOp.bRecalculateNormals = true;

    // 验证输入
    if (PNTriOp.Validate() != EOperationValidationResult::Ok)
    {
        return false;
    }

    // 执行细分
    return PNTriOp.Compute();
}
```

## 模块依赖

### DynamicMesh 模块

| 模块 | 用途 |
|---|---|
| `MeshConversion` | 网格格式转换（FDynamicMesh3 ↔ UStaticMesh） |
| `ImageCore` | 图像处理基础（纹理烘焙输出） |
| `MeshDescription` | MeshDescription 数据结构互操作 |

### GeometryAlgorithms 模块

无特殊依赖（仅标准 Core/Engine/Slate 等）。

### MeshFileUtils 模块

| 模块 | 用途 |
|---|---|
| `DynamicMesh` | 依赖 DynamicMesh 模块的网格数据结构 |

## 维护状态

### 近期更新

```
- b6681495f0a Fixes for Mesh Bevel -- 1. Handle bevels where the bevel edge is not a group boundary edge 2. Detect + handle fallback case where a non-subdivided quad is used so there is no quad strip to process 3. Stop processing earlier when encountering bad cases (invalid edge IDs, or non-boundary edge IDs, in the stitch-up pass)
- 70470a0a990 [Backout] - CL45842950 Fixes for Mesh Bevel (回退了上一个提交)
- b2c975fde11 make another mesh bevel check() into a soft failure / return
```

### 维护评价

**活跃维护** — GeometryProcessing 是 UE5 建模工具链的核心基础设施，持续获得更新和修复。

- **创建时间**：约 2020 年，随 UE5 开发周期创建
- **更新频率**：近期提交集中在 Mesh Bevel 操作的 bug 修复，说明该模块仍在被积极使用和维护
- **代码规模**：738 个源文件，属于超大型插件，功能覆盖面广
- **实验性状态**：`IsBetaVersion=true`，API 可能在未来版本中发生变化
- **依赖关系**：被 Geometry Script、Modeling Tools、UV Editor 等多个上层工具依赖，是不可替代的核心模块
- **已知限制**：作为 Beta 版本，部分 API 可能不稳定；UV 参数化求解器假设网格为单连通分量

**推荐使用**：✅ 强烈推荐作为底层几何处理库使用。虽然标记为 Beta，但它是 UE5 建模工具链的基石，经过大量实际使用验证。C++ 开发者在需要运行时网格操作时应优先考虑此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GeometryProcessing)
- [官方文档]()（无）
- [测试用例]()（需确认 Engine/Tests/ 下是否有相关测试）