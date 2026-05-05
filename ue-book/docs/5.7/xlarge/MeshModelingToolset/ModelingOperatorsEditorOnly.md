# Mesh Modeling Toolset — ModelingOperatorsEditorOnly 模块

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-10-01 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset) | |

---

## 用途

**ModelingOperatorsEditorOnly** 是 MeshModelingToolset 插件中的**计算后端模块**，提供网格建模操作的底层算法实现。它不包含任何 UI 或交互式工具，而是封装了纯计算性的几何处理算子（Operator），供上层工具模块（MeshModelingTools / MeshModelingToolsEditorOnly）调用。

本模块包含以下核心算子类别：

| 子目录 | 算子 | 功能 |
|---|---|---|
| `CompositionOps` | `FVoxelMergeMeshesOp` | 基于体素化的多网格合并 |
| `CompositionOps` | `FVoxelBooleanMeshesOp` | 基于体素化的布尔运算（并集、差集、交集） |
| `ParameterizationOps` | `FCalculateTangentsOp` | 网格切线计算（MikkTSpace / FastMikkTSpace / PerTriangle / CopyExisting） |
| `ParameterizationOps` | `FParameterizeMeshOp` | 自动 UV 展开（UVAtlas / XAtlas / PatchBuilder 三种后端） |
| `CuttingOps` | `FEmbedPolygonsOp` | 多边形嵌入/裁剪（TrimOutside / TrimInside / InsertPolygon / CutThrough / CutOutside） |
| `CleaningOps` | `FSimplifyMeshOp` | 网格简化（QEM / Attribute / UEStandard / ClusterBased 等多种算法） |
| `Properties` | `UParameterizeMeshTool*Properties` | UV 参数化工具的配置属性集 |

**为什么存在这个模块？** MeshModelingToolset 采用分层架构：上层工具负责交互逻辑和 UI，本模块负责纯粹的几何计算。这种分离使得算子可以在不同上下文中复用（例如 Geometry Script 也可以调用切线计算算子）。

---

## 使用场景

- 你在编写自定义的网格编辑工具，需要执行**体素布尔运算**（镂空、合并、求交）→ 使用 `FVoxelBooleanMeshesOp`
- 你需要对网格进行**自动 UV 展开**，支持 UVAtlas / XAtlas / PatchBuilder 三种算法 → 使用 `FParameterizeMeshOp`
- 你需要计算网格切线，支持 MikkTSpace 等多种算法 → 使用 `FCalculateTangentsOp`
- 你需要将网格面数从 10 万降到 1 万 → 使用 `FSimplifyMeshOp`
- 你需要在网格表面裁剪出一个形状（如窗户开口）→ 使用 `FEmbedPolygonsOp`
- 你在开发运行时程序化内容生成管线，需要合并多个网格体 → 使用 `FVoxelMergeMeshesOp`

---

## 蓝图用法

本模块的算子均为 C++ 原生类（`FDynamicMeshOperator` / `TGenericDataOperator`），**不直接暴露 BlueprintCallable 函数**。但以下类型在蓝图中可用：

### 可用的蓝图枚举

| 枚举 | 说明 | 所在头文件 |
|---|---|---|
| `EMeshTangentsType` | 切线计算方法（MikkTSpace / FastMikkTSpace / PerTriangle / CopyExisting） | `CalculateTangentsOp.h` |
| `EBooleanOperation` | 布尔运算类型（DifferenceAB / DifferenceBA / Intersect / Union） | `VoxelBooleanMeshesOp.h` |
| `ESimplifyTargetType` | 简化目标类型（Percentage / TriangleCount / VertexCount / EdgeLength） | `SimplifyMeshOp.h` |
| `ESimplifyType` | 简化算法类型（QEM / Attribute / UEStandard / ClusterBased 等） | `SimplifyMeshOp.h` |
| `EEmbeddedPolygonOpMethod` | 嵌入多边形操作方法（TrimOutside / TrimInside / InsertPolygon / CutThrough / CutOutside） | `EmbedPolygonsOp.h` |
| `EParameterizeMeshUVMethod` | UV 参数化方法（PatchBuilder / UVAtlas / XAtlas） | `ParameterizeMeshProperties.h` |

### 可用的蓝图属性集

| 属性集类 | 说明 |
|---|---|
| `UParameterizeMeshToolProperties` | UV 生成方法选择 |
| `UParameterizeMeshToolUVAtlasProperties` | UVAtlas 参数（拉伸度、岛数、纹理分辨率、UDIM 支持） |
| `UParameterizeMeshToolXAtlasProperties` | XAtlas 参数（迭代次数） |
| `UParameterizeMeshToolPatchBuilderProperties` | PatchBuilder 参数（初始面片数、曲率对齐、合并阈值等） |

> **提示**：如需在蓝图中使用这些算子，请通过上层工具（如 MeshModelingTools 模块中的 `USimplifyMeshTool`、`UUVProjectionTool` 等）间接调用，这些工具已封装为 BlueprintCallable 的交互式工具。

---

## C++ 用法

### 头文件引入

```cpp
// 体素布尔运算
#include "CompositionOps/VoxelBooleanMeshesOp.h"

// 体素合并
#include "CompositionOps/VoxelMergeMeshesOp.h"

// 切线计算
#include "ParameterizationOps/CalculateTangentsOp.h"

// UV 参数化
#include "ParameterizationOps/ParameterizeMeshOp.h"

// 网格简化
#include "CleaningOps/SimplifyMeshOp.h"

// 多边形嵌入/裁剪
#include "CuttingOps/EmbedPolygonsOp.h"
```

### 基本用法 — 体素布尔运算

```cpp
// 来源: CompositionOps/VoxelBooleanMeshesOp.h
#include "CompositionOps/VoxelBooleanMeshesOp.h"
#include "DynamicMesh/DynamicMesh3.h"

using namespace UE::Geometry;

// 准备输入网格（需要以 ThreadSafe 共享指针提供）
TArray<TSharedPtr<const FDynamicMesh3, ESPMode::ThreadSafe>> InputMeshes;
TArray<FTransformSRT3d> InputTransforms;

// 假设已有两个 FDynamicMesh3 实例
InputMeshes.Add(MakeShared<const FDynamicMesh3, ESPMode::ThreadSafe>(MeshA));
InputMeshes.Add(MakeShared<const FDynamicMesh3, ESPMode::ThreadSafe>(MeshB));
InputTransforms.Add(FTransformSRT3d::Identity());
InputTransforms.Add(FTransformSRT3d(FVector3d(100, 0, 0)));

// 创建布尔运算算子
FVoxelBooleanMeshesOp BoolOp;
BoolOp.Meshes = InputMeshes;
BoolOp.Transforms = InputTransforms;
BoolOp.Operation = FVoxelBooleanMeshesOp::EBooleanOperation::Union;
BoolOp.VoxelCount = 128;        // 体素分辨率
BoolOp.IsoSurfaceD = 0.0;      // 等值面阈值
BoolOp.AdaptivityD = 0.0;      // 自适应细分
BoolOp.bAutoSimplify = false;

// 执行计算（可传入 Progress 取消回调）
BoolOp.CalculateResult(nullptr);

// 获取结果
const FDynamicMesh3& ResultMesh = BoolOp.ResultMesh;
```

### 基本用法 — 网格简化

```cpp
// 来源: CleaningOps/SimplifyMeshOp.h
#include "CleaningOps/SimplifyMeshOp.h"

using namespace UE::Geometry;

FSimplifyMeshOp SimplifyOp;

// 设置输入网格
SimplifyOp.OriginalMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(SourceMesh);

// 配置简化参数
SimplifyOp.TargetMode = ESimplifyTargetType::Percentage;
SimplifyOp.SimplifierType = ESimplifyType::QEM;  // Quadric Error Metric
SimplifyOp.TargetPercentage = 50;  // 保留 50% 的三角形
SimplifyOp.bDiscardAttributes = false;
SimplifyOp.bReproject = true;      // 将结果投影回原始表面
SimplifyOp.bPreserveSharpEdges = true;
SimplifyOp.bPreventNormalFlips = true;

// 边界约束
SimplifyOp.MeshBoundaryConstraint = EEdgeRefineFlags::NoChange;
SimplifyOp.GroupBoundaryConstraint = EEdgeRefineFlags::NoChange;
SimplifyOp.MaterialBoundaryConstraint = EEdgeRefineFlags::NoChange;

// 执行
SimplifyOp.CalculateResult(nullptr);

const FDynamicMesh3& SimplifiedMesh = SimplifyOp.ResultMesh;
```

### 基本用法 — 切线计算

```cpp
// 来源: ParameterizationOps/CalculateTangentsOp.h
#include "ParameterizationOps/CalculateTangentsOp.h"

using namespace UE::Geometry;

FCalculateTangentsOp TangentsOp;

// 设置输入
TangentsOp.SourceMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(Mesh);
TangentsOp.CalculationMethod = EMeshTangentsType::MikkTSpace;
TangentsOp.TargetUVLayer = 0;  // 使用第 0 层 UV

// 执行
TangentsOp.CalculateResult(nullptr);

// 获取结果
TUniquePtr<FMeshTangentsd> Tangents = TangentsOp.ExtractResult();
```

### 进阶用法 — UV 参数化（UVAtlas 后端）

```cpp
// 来源: ParameterizationOps/ParameterizeMeshOp.h + Properties/ParameterizeMeshProperties.h
#include "ParameterizationOps/ParameterizeMeshOp.h"

using namespace UE::Geometry;

FParameterizeMeshOp ParamOp;

// 设置输入网格
ParamOp.InputMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(Mesh);

// 选择 UVAtlas 后端
ParamOp.Method = EParamOpBackend::UVAtlas;

// UVAtlas 参数
ParamOp.Stretch = 0.11f;        // 拉伸容忍度 (0=无拉伸, 1=最大)
ParamOp.NumCharts = 0;          // 0 = 自动确定岛数

// Atlas 打包参数
ParamOp.bEnablePacking = true;
ParamOp.Width = 1024;
ParamOp.Height = 1024;
ParamOp.Gutter = 2.5f;          // UV 岛之间的间距（像素）

// UDIM 支持
ParamOp.bPackToUDIMSByOriginPolygroup = false;

// UV 层
ParamOp.UVLayer = 0;

// 设置变换
ParamOp.SetTransform(FTransformSRT3d::Identity());

// 执行
ParamOp.CalculateResult(nullptr);

// 结果在 ParamOp.ResultMesh 中，UV 已写入 DynamicMesh 的属性层
```

### 进阶用法 — 多边形嵌入裁剪

```cpp
// 来源: CuttingOps/EmbedPolygonsOp.h
#include "CuttingOps/EmbedPolygonsOp.h"
#include "Polygon2.h"

using namespace UE::Geometry;

FEmbedPolygonsOp EmbedOp;

// 设置输入网格
EmbedOp.OriginalMesh = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>(Mesh);

// 定义裁剪多边形（2D）
FPolygon2d CutPolygon;
CutPolygon.AppendVertex(FVector2d(-50, -50));
CutPolygon.AppendVertex(FVector2d( 50, -50));
CutPolygon.AppendVertex(FVector2d( 50,  50));
CutPolygon.AppendVertex(FVector2d(-50,  50));
EmbedOp.EmbedPolygon = CutPolygon;

// 定义多边形在 3D 空间中的位置和朝向
EmbedOp.PolygonFrame = FFrame3d(FVector3d(0, 0, 100), FVector3d::UnitZ());

// 选择操作类型
EmbedOp.Operation = EEmbeddedPolygonOpMethod::TrimOutside;  // 保留多边形内部，裁掉外部
EmbedOp.bCutWithBoolean = true;
EmbedOp.bAttemptFixHolesOnBoolean = true;
EmbedOp.bDiscardAttributes = false;

// 执行
EmbedOp.CalculateResult(nullptr);

if (EmbedOp.bOperationSucceeded)
{
    const FDynamicMesh3& ResultMesh = EmbedOp.ResultMesh;
    // EmbedOp.EmbeddedEdges 包含嵌入的边 ID
}
else
{
    // EmbedOp.EdgesOnFailure 包含失败时需要高亮的边
}
```

---

## Demo 示例

以下是一个完整的最小示例，展示如何在 C++ 中使用体素布尔运算算子对两个网格执行 Union 操作：

### VoxelBooleanDemo.h

```cpp
// VoxelBooleanDemo.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "CompositionOps/VoxelBooleanMeshesOp.h"

class FVoxelBooleanDemo
{
public:
    /** 对两个网格执行体素布尔并集运算 */
    static TUniquePtr<UE::Geometry::FDynamicMesh3> UnionMeshes(
        const UE::Geometry::FDynamicMesh3& MeshA,
        const FTransform& TransformA,
        const UE::Geometry::FDynamicMesh3& MeshB,
        const FTransform& TransformB,
        int32 Resolution = 128);
};
```

### VoxelBooleanDemo.cpp

```cpp
// VoxelBooleanDemo.cpp
#include "VoxelBooleanDemo.h"
#include "TransformTypes.h"

using namespace UE::Geometry;

TUniquePtr<FDynamicMesh3> FVoxelBooleanDemo::UnionMeshes(
    const FDynamicMesh3& MeshA,
    const FTransform& TransformA,
    const FDynamicMesh3& MeshB,
    const FTransform& TransformB,
    int32 Resolution)
{
    // 构造输入
    TArray<TSharedPtr<const FDynamicMesh3, ESPMode::ThreadSafe>> Meshes;
    TArray<FTransformSRT3d> Transforms;

    Meshes.Add(MakeShared<const FDynamicMesh3, ESPMode::ThreadSafe>(MeshA));
    Meshes.Add(MakeShared<const FDynamicMesh3, ESPMode::ThreadSafe>(MeshB));

    Transforms.Add(FTransformSRT3d(TransformA));
    Transforms.Add(FTransformSRT3d(TransformB));

    // 配置算子
    FVoxelBooleanMeshesOp Op;
    Op.Meshes = MoveTemp(Meshes);
    Op.Transforms = MoveTemp(Transforms);
    Op.Operation = FVoxelBooleanMeshesOp::EBooleanOperation::Union;
    Op.VoxelCount = Resolution;
    Op.IsoSurfaceD = 0.0;
    Op.AdaptivityD = 0.0;
    Op.bAutoSimplify = false;

    // 执行
    Op.CalculateResult(nullptr);

    // 提取结果
    return MakeUnique<FDynamicMesh3>(MoveTemp(Op.ResultMesh));
}
```

---

## 模块依赖

从 Build.cs 及头文件 include 分析，本模块的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `ModelingOperators` | 基础算子框架（`FDynamicMeshOperator`、`TGenericDataOperator`） |
| `GeometryCore` | 动态网格（`FDynamicMesh3`）、切线（`FMeshTangents`）、AABB 树等核心几何数据结构 |
| `MeshDescription` | `FMeshDescription` 互操作（用于 UEStandard 简化路径） |
| `InteractiveToolsFramework` | `UInteractiveToolPropertySet` 基类（属性集类使用） |

无其他特殊依赖（仅标准 Core/Engine/CoreUObject 等）。

---

## 维护状态

### 近期更新

```
- 9046d138c10a 将动态网格 MikkT 支持从 CalculateTangentsOp 中抽出以便 Geometry Script 复用；修复 mesh overlay 中未设置元素（法线、UV）的处理
- 3bb010dedc44 切线工具改用新选中的 UV 层进行 MikkT vs FastMikkT 对比可视化；修复切线算子对无效 UV 层的 clamp 处理
- ddd02a693b66 切线工具新增选择参考 UV 层的功能，用于计算切线时指定使用哪一层 UV
```

### 维护评价

- **创建时间**：2019-10-01，约 6 年历史
- **维护状态**：**活跃维护中** — 近期 commit 集中在切线计算算子的功能增强（UV 层选择、MikkT 支持重构），表明 Epic 持续投入开发
- **实验性标记**：`.uplugin` 中 `IsBetaVersion=true` 且 `Hidden=true`，说明该插件仍处于实验阶段，API 可能发生变化
- **架构成熟度**：采用分层架构（Operator → Tool → UI），代码组织清晰，算子设计遵循统一的 `CalculateResult(FProgressCancel*)` 模式
- **已知限制**：
  - 体素布尔/合并操作的精度受 `VoxelCount` 限制，高精度场景需要较大内存
  - `FEmbedPolygonsOp` 目前不支持带孔的多边形（代码注释中有 TODO）
  - 模块名为 "EditorOnly" 但类型为 Runtime，实际使用场景主要在编辑器中
- **推荐程度**：✅ **推荐使用** — 作为 Epic 官方维护的网格建模计算后端，算法质量有保障，且与 UE5 的 Interactive Tools Framework 深度集成。但需注意 Beta 状态，生产环境使用时应做好 API 变更的准备。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset)
- [源码（本模块）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MeshModelingToolset/Source/ModelingOperatorsEditorOnly)
- [官方文档]()（暂无）