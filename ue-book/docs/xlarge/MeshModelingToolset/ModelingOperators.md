# Mesh Modeling Toolset — ModelingOperators 模块

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 🏛️ 文物（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

---

## 用途

ModelingOperators 是 Mesh Modeling Toolset 插件的**纯计算引擎模块**。它不包含任何 UI、蓝图工具或编辑器交互逻辑——只包含可复用的网格操作算法（Operators）。

该模块的核心设计模式是：每个操作都继承自 `FDynamicMeshOperator`，通过 `CalculateResult(FProgressCancel*)` 执行计算，产出一个 `FDynamicMesh3` 结果网格。这种设计使得操作可以：
- 在后台线程异步执行（通过 `FAsyncTaskExecuterWithAbort`）
- 支持进度报告和取消
- 与 Interactive Tools Framework 的预览系统无缝集成

**为什么存在这个模块？** Mesh Modeling Toolset 的架构将"计算逻辑"与"工具 UI/交互"分离。ModelingOperators 只负责数学和几何计算，而 MeshModelingTools 模块负责构建交互式工具。这种分离使得操作可以在不同上下文中复用（编辑器工具、运行时程序化生成、批处理等）。

## 使用场景

- 你需要在运行时对网格执行布尔运算（CSG）→ 使用 `FBooleanMeshesOp`
- 你需要对网格进行体素化处理（实心化、混合、形态学操作）→ 使用 `FVoxelSolidifyMeshesOp` / `FVoxelBlendMeshesOp` / `FVoxelMorphologyMeshesOp`
- 你需要对网格执行空间变形（弯曲、扭曲、膨胀）→ 使用 `FBendMeshOp` / `FTwistMeshOp` / `FFlareMeshOp`
- 你需要重新网格化（Remesh）以改善三角形质量 → 使用 `FRemeshMeshOp`
- 你需要填充网格孔洞 → 使用 `FHoleFillOp`
- 你需要 UV 投影或重新计算 UV → 使用 `FUVProjectionOp` / `FRecomputeUVsOp`
- 你需要网格平滑 → 使用 `FIterativeSmoothingOp` / `FCotanSmoothingOp`
- 你需要平面切割网格 → 使用 `FPlaneCutOp`
- 你需要挤出选中的三角面 → 使用 `FExtrudeOp` / `FLinearExtrusionOp`
- 你需要镜像网格 → 使用 `FMirrorOp`
- 你需要网格蒙皮绑定 → 使用 `FSkinBindingOp`
- 你需要沿曲线扫掠生成网格 → 使用 `FCurveSweepOp`

## 蓝图用法

ModelingOperators 是一个纯 C++ 运算模块，**不直接暴露蓝图节点**。它通过 `MeshModelingTools` 模块中的交互式工具间接使用。

但模块中包含少量 `UCLASS` 工厂类，可用于蓝图桥接：

### 核心工厂类

| 类 | 说明 | 用途 |
|---|---|---|
| `UGenerateCrossSectionOpFactory` | 横截面生成操作工厂 | 创建 `FGenerateCrossSectionOp` 实例 |
| `UUVLayoutOperatorFactory` | UV 布局操作工厂 | 创建 `FUVLayoutOp` 实例 |
| `UUVLayoutProperties` | UV 布局属性集 | 配置 UV 布局参数（Repack/Stack/Normalize） |
| `URecomputeUVsToolProperties` | UV 重计算属性集 | 配置 UV 展开算法参数 |
| `UUVEditorTexelDensitySettings` | Texel Density 设置 | 配置纹素密度参数 |

### 使用示例（蓝图描述）

由于 ModelingOperators 是底层计算模块，蓝图中通常不直接使用。推荐通过 MeshModelingTools 模块的交互式工具使用这些操作。如果需要在蓝图中直接调用操作，需要通过 C++ 创建操作实例并调用 `CalculateResult()`。

## C++ 用法

### 头文件引入

```cpp
#include "ModelingOperators.h"                    // 基类 FDynamicMeshOperator
#include "CompositionOps/BooleanMeshesOp.h"       // 布尔运算
#include "CompositionOps/VoxelSolidifyMeshesOp.h" // 体素实心化
#include "SpaceDeformerOps/BendMeshOp.h"          // 弯曲变形
#include "SmoothingOps/IterativeSmoothingOp.h"    // 迭代平滑
#include "CuttingOps/PlaneCutOp.h"                // 平面切割
#include "CleaningOps/RemeshMeshOp.h"             // 重新网格化
#include "CleaningOps/HoleFillOp.h"               // 孔洞填充
#include "ParameterizationOps/UVProjectionOp.h"   // UV 投影
#include "DeformationOps/ExtrudeOp.h"             // 挤出
```

### 基本用法：布尔运算

所有操作遵循相同的模式：创建操作 → 设置输入参数 → 调用 `CalculateResult()` → 提取结果。

```cpp
// 来源: CompositionOps/BooleanMeshesOp.h
#include "CompositionOps/BooleanMeshesOp.h"

using namespace UE::Geometry;

// 创建布尔运算操作
FBooleanMeshesOp BoolOp;

// 设置输入网格（需要 FDynamicMesh3 的共享指针）
TSharedPtr<FDynamicMesh3, ESPMode::ThreadSafe> MeshA = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>();
TSharedPtr<FDynamicMesh3, ESPMode::ThreadSafe> MeshB = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>();
// ... 填充 MeshA 和 MeshB 数据 ...

BoolOp.Meshes.Add(MeshA);
BoolOp.Meshes.Add(MeshB);

// 设置变换（1:1 对应 Meshes）
BoolOp.Transforms.Add(FTransformSRT3d::Identity());
BoolOp.Transforms.Add(FTransformSRT3d::Identity());

// 设置布尔运算类型
BoolOp.CSGOperation = ECSGOperation::DifferenceAB;  // A - B
BoolOp.bAttemptFixHoles = true;
BoolOp.WindingThreshold = 0.5;

// 执行计算
BoolOp.CalculateResult(nullptr);  // nullptr = 无进度回调

// 提取结果
TUniquePtr<FDynamicMesh3> ResultMesh = BoolOp.ExtractResult();
FTransformSRT3d ResultTransform = BoolOp.GetResultTransform();
```

### 基本用法：平面切割

```cpp
// 来源: CuttingOps/PlaneCutOp.h
#include "CuttingOps/PlaneCutOp.h"

using namespace UE::Geometry;

FPlaneCutOp CutOp;

// 设置输入网格
CutOp.OriginalMesh = InputMesh;  // TSharedPtr<const FDynamicMesh3, ESPMode::ThreadSafe>

// 设置切割平面（网格局部空间）
CutOp.LocalPlaneOrigin = FVector3d(0, 0, 50);   // 平面原点
CutOp.LocalPlaneNormal = FVector3d(0, 0, 1);     // 平面法线（向上）

// 设置选项
CutOp.bFillCutHole = true;         // 填充切割孔洞
CutOp.bKeepBothHalves = false;     // 只保留一半
CutOp.bSimplifyAlongNewEdges = true; // 简化切割边缘

// 设置输出变换
CutOp.SetTransform(FTransformSRT3d::Identity());

// 执行
CutOp.CalculateResult(nullptr);

// 获取结果
TUniquePtr<FDynamicMesh3> Result = CutOp.ExtractResult();
```

### 基本用法：空间变形（弯曲）

```cpp
// 来源: SpaceDeformerOps/BendMeshOp.h, SpaceDeformerOps/MeshSpaceDeformerOp.h
#include "SpaceDeformerOps/BendMeshOp.h"

using namespace UE::Geometry;

FBendMeshOp BendOp;

// 设置输入网格
BendOp.OriginalMesh = InputMesh;

// 设置 Gizmo 帧（变形的参考坐标系）
BendOp.GizmoFrame = FFrame3d(FVector3d::ZeroVector, FVector3d::UpVector);

// 设置变形影响范围（相对于 Gizmo 位置）
BendOp.LowerBoundsInterval = -100.0;
BendOp.UpperBoundsInterval = 100.0;

// 设置弯曲参数
BendOp.BendDegrees = 90.0;    // 弯曲角度
BendOp.bLockBottom = false;    // 是否锁定底部

BendOp.SetTransform(FTransformSRT3d::Identity());
BendOp.CalculateResult(nullptr);

TUniquePtr<FDynamicMesh3> Result = BendOp.ExtractResult();
```

### 进阶用法：体素实心化（多网格合并）

```cpp
// 来源: CompositionOps/VoxelSolidifyMeshesOp.h, BaseOps/VoxelBaseOp.h
#include "CompositionOps/VoxelSolidifyMeshesOp.h"

using namespace UE::Geometry;

FVoxelSolidifyMeshesOp SolidifyOp;

// 添加多个输入网格
SolidifyOp.Meshes.Add(Mesh1);
SolidifyOp.Meshes.Add(Mesh2);
SolidifyOp.Transforms.Add(Transform1);
SolidifyOp.Transforms.Add(Transform2);

// 体素化参数
SolidifyOp.WindingThreshold = 0.5;     // 缠绕数阈值
SolidifyOp.ExtendBounds = 1.0;         // 边界扩展
SolidifyOp.bSolidAtBoundaries = true;  // 边界处实心化
SolidifyOp.SurfaceSearchSteps = 3;     // 表面搜索步数

// 可选：加厚薄壳
SolidifyOp.bApplyThickenShells = true;
SolidifyOp.ThickenShells = 5.0;

// 基类参数（来自 FVoxelBaseOp）
SolidifyOp.OutputVoxelCount = 1024;    // 输出体素分辨率
SolidifyOp.bAutoSimplify = true;       // 自动简化结果
SolidifyOp.bRemoveInternalSurfaces = false;

SolidifyOp.SetTransform(FTransformSRT3d::Identity());
SolidifyOp.CalculateResult(nullptr);

TUniquePtr<FDynamicMesh3> Result = SolidifyOp.ExtractResult();
```

### 进阶用法：迭代平滑（带权重图）

```cpp
// 来源: SmoothingOps/IterativeSmoothingOp.h, SmoothingOps/SmoothingOpBase.h
#include "SmoothingOps/IterativeSmoothingOp.h"

using namespace UE::Geometry;

// 配置平滑选项
FSmoothingOpBase::FOptions SmoothOptions;
SmoothOptions.SmoothAlpha = 0.5f;          // 平滑强度 [0,1]
SmoothOptions.BoundarySmoothAlpha = 0.3f;  // 边界平滑强度
SmoothOptions.Iterations = 5;              // 迭代次数
SmoothOptions.bSmoothBoundary = true;      // 是否平滑边界
SmoothOptions.bUniform = false;            // 使用非均匀权重（质量更好）
SmoothOptions.bUseImplicit = false;        // 使用显式迭代

// 创建平滑操作（支持子网格选择性平滑）
FIterativeSmoothingOp SmoothOp(InputMesh.Get(), SmoothOptions);

SmoothOp.SetTransform(FTransformSRT3d::Identity());
SmoothOp.CalculateResult(nullptr);

// 结果通过 UpdateResultMesh() 更新到内部 ResultMesh
TUniquePtr<FDynamicMesh3> Result = SmoothOp.ExtractResult();
```

### 进阶用法：网格蒙皮绑定

```cpp
// 来源: SkinningOps/SkinBindingOp.h
#include "SkinningOps/SkinBindingOp.h"

using namespace UE::Geometry;

FSkinBindingOp SkinOp;

// 设置输入网格
SkinOp.OriginalMesh = InputMesh;

// 从 ReferenceSkeleton 设置骨骼层级
SkinOp.SetTransformHierarchyFromReferenceSkeleton(RefSkeleton);

// 配置绑定参数
SkinOp.BindType = ESkinBindingType::GeodesicVoxel;  // 测地线体素距离（更精确但更慢）
SkinOp.Stiffness = 0.2f;       // 刚度
SkinOp.MaxInfluences = 5;      // 每顶点最大骨骼影响数
SkinOp.VoxelResolution = 256;  // 体素分辨率（仅 GeodesicVoxel 模式）

SkinOp.CalculateResult(nullptr);

TUniquePtr<FDynamicMesh3> Result = SkinOp.ExtractResult();
// 结果网格包含 SkinWeights 属性
```

## Demo 示例

以下是一个完整的最小示例，展示如何使用 ModelingOperators 执行平面切割操作：

### MeshCutExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"

class FMeshCutExample
{
public:
    /** 对输入网格执行平面切割，返回切割后的网格 */
    static TUniquePtr<UE::Geometry::FDynamicMesh3> CutMeshWithPlane(
        const UE::Geometry::FDynamicMesh3& InputMesh,
        const FVector3d& PlaneOrigin,
        const FVector3d& PlaneNormal,
        bool bKeepBothHalves = false);
};
```

### MeshCutExample.cpp

```cpp
#include "MeshCutExample.h"
#include "CuttingOps/PlaneCutOp.h"

using namespace UE::Geometry;

TUniquePtr<FDynamicMesh3> FMeshCutExample::CutMeshWithPlane(
    const FDynamicMesh3& InputMesh,
    const FVector3d& PlaneOrigin,
    const FVector3d& PlaneNormal,
    bool bKeepBothHalves)
{
    // 创建输入网格的共享拷贝
    auto SharedMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(InputMesh);

    // 创建平面切割操作
    FPlaneCutOp CutOp;
    CutOp.OriginalMesh = SharedMesh;
    CutOp.LocalPlaneOrigin = PlaneOrigin;
    CutOp.LocalPlaneNormal = PlaneNormal;
    CutOp.bFillCutHole = true;
    CutOp.bKeepBothHalves = bKeepBothHalves;
    CutOp.bSimplifyAlongNewEdges = true;

    // 设置变换为单位变换
    CutOp.SetTransform(FTransformSRT3d::Identity());

    // 执行切割（nullptr 表示无进度回调）
    CutOp.CalculateResult(nullptr);

    // 检查结果
    const FGeometryResult& ResultInfo = CutOp.GetResultInfo();
    if (ResultInfo.Result == EGeometryResult::Success)
    {
        return CutOp.ExtractResult();
    }

    return nullptr;
}
```

## 模块依赖

ModelingOperators 的 Build.cs 依赖（基于头文件 include 分析）：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 核心几何数据结构（FDynamicMesh3、网格操作算法） |
| `GeometryFramework` | 几何框架（交互工具基础设施） |
| `MeshConversion` | 网格格式转换 |

无特殊依赖（仅标准 Core/Engine/Slate 等 + GeometryCore 几何库）。

## 维护状态

### 近期更新

```
- 10344aefd27f Fix missing include #rnx #jira
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- a48db18f6a9b Replace some usages of FORCEINLINE with inline in Mesh modules.
```

### 维护评价

- **创建时间**：2019-10-01，约 6 年历史
- **实验性状态**：`IsBetaVersion=true`，`Hidden=true`，`EnabledByDefault=false`——这是一个**隐藏的实验性插件**
- **最近更新**：近期 commit 均为代码质量修复（include 修复、宏替换），无功能性更新
- **代码规模**：850 个源文件，属于超大型插件
- **架构成熟度**：操作基类 `FDynamicMeshOperator` 设计清晰，支持异步执行和取消，架构成熟
- **活跃度**：作为 UE5 Modeling 工具链的核心计算引擎，持续维护中但近期无重大功能变更

**综合评价**：ModelingOperators 是 UE5 网格建模工具链的底层计算引擎，虽然标记为实验性，但已被广泛使用（编辑器中的建模模式依赖此模块）。代码质量高，架构设计合理。推荐在需要运行时网格操作时使用，但需注意该模块标记为 Hidden/Beta，API 可能在未来版本中发生变化。

⚠️ **注意**：该插件默认未启用（`EnabledByDefault=false`，`Hidden=true`）。使用前需在项目设置中手动启用，或在 `.uproject` 中添加插件依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Source/ModelingOperators)
- [官方文档]()（无）
- [测试用例]()（未发现独立测试文件）

---

## 操作分类速查表

### 布尔与组合操作（CompositionOps）

| 操作类 | 说明 |
|---|---|
| `FBooleanMeshesOp` | CSG 布尔运算（并集、差集、交集、修剪） |
| `FSelfUnionMeshesOp` | 自并集（合并重叠几何体） |
| `FVoxelBlendMeshesOp` | 体素混合（平滑连接多个网格） |
| `FVoxelSolidifyMeshesOp` | 体素实心化（将开放网格转为封闭实体） |
| `FVoxelMorphologyMeshesOp` | 体素形态学操作（膨胀、收缩、开运算、闭运算） |
| `FMirrorOp` | 网格镜像（沿平面翻转并可选焊接） |
| `FCurveSweepOp` | 曲线扫掠（沿路径扫掠截面生成网格） |
| `FCubeGridBooleanOp` | 立方体网格布尔（用于 CubeGrid 工具） |

### 空间变形操作（SpaceDeformerOps）

| 操作类 | 说明 |
|---|---|
| `FMeshSpaceDeformerOp` | 空间变形基类（定义 Gizmo 帧和影响范围） |
| `FBendMeshOp` | 弯曲变形 |
| `FTwistMeshOp` | 扭曲变形 |
| `FFlareMeshOp` | 膨胀/收缩变形（支持 Sin/SinSqr/Linear 曲线） |

### 平滑操作（SmoothingOps）

| 操作类 | 说明 |
|---|---|
| `FSmoothingOpBase` | 平滑基类（支持权重图、边界控制） |
| `FIterativeSmoothingOp` | 迭代平滑（Uniform/Cotan/MeanValue） |
| `FCotanSmoothingOp` | Cotan 双调和平滑（隐式求解，质量更高） |

### 切割操作（CuttingOps）

| 操作类 | 说明 |
|---|---|
| `FPlaneCutOp` | 平面切割（可填充孔洞、保留双半） |
| `FEdgeLoopInsertionOp` | 边循环插入 |
| `FGroupEdgeInsertionOp` | 组边插入 |

### 清理操作（CleaningOps）

| 操作类 | 说明 |
|---|---|
| `FRemeshMeshOp` | 重新网格化（Standard/FullPass/NormalFlow） |
| `FHoleFillOp` | 孔洞填充（TriangleFan/EarClipping/Planar/Minimal/Smooth） |
| `FEditNormalsOp` | 法线编辑（重计算、翻转、修复不一致） |
| `FRemoveOccludedTrianglesOp` | 移除被遮挡三角形 |

### 变形操作（DeformationOps）

| 操作类 | 说明 |
|---|---|
| `FExtrudeOp` | 挤出（MoveAndStitch/Boolean 模式） |
| `FLatticeDeformerOp` | 晶格变形（FFD 自由形变） |

### 参数化操作（ParameterizationOps）

| 操作类 | 说明 |
|---|---|
| `FUVProjectionOp` | UV 投影（Box/Cylinder/Plane/ExpMap） |
| `FUVLayoutOp` | UV 布局（Transform/Repack/Stack/Normalize） |
| `FRecomputeUVsOp` | UV 重计算（ExpMap/Conformal/SpectralConformal） |
| `FUVEditorTexelDensityOp` | 纹素密度调整 |

### 多边形建模操作（PolyModelingOps）

| 操作类 | 说明 |
|---|---|
| `FLinearExtrusionOp` | 线性挤出（支持细分、组推断、UV 展开） |
| `FRegionOffsetOp` | 区域偏移（沿法线方向偏移选中三角形） |

### 曲线操作（CurveOps）

| 操作类 | 说明 |
|---|---|
| `FGenerateCrossSectionOp` | 横截面生成（提取平面与网格的交线） |
| `FTriangulateCurvesOp` | 曲线三角化（将样条线转为三角网格） |

### 蒙皮操作（SkinningOps）

| 操作类 | 说明 |
|---|---|
| `FSkinBindingOp` | 蒙皮绑定（DirectDistance/GeodesicVoxel） |

### 基础操作（BaseOps）

| 操作类 | 说明 |
|---|---|
| `FVoxelBaseOp` | 体素操作基类（体素分辨率、简化、后处理） |
| `FSimpleMeshProcessingBaseOp` | 简单网格处理基类（位置缓冲区 + 法线重计算） |