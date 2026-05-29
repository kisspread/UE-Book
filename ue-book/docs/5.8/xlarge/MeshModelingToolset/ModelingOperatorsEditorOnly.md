# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（网格创建与编辑操作符、组件及属性类） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

## 用途

该插件是一个庞大的运行时工具集合，旨在通过可扩展的 `Interactive Tools Framework` 提供程序化的 3D 网格创建和编辑能力。它并非面向最终用户的单个工具，而是底层操作符、组件和属性的“引擎”，供上层编辑器工具（如 `ModelingToolsEditorMode`）调用。核心目标是提供一套高性能、可异步执行的网格操作算子（Operators），涵盖从几何体创建、UV 计算、网格清理到布尔运算等广泛的建模功能。

## 使用场景

- 你需要通过 C++ 或蓝图在运行时动态地创建、修改或优化一个 3D 静态网格体。
- 你需要实现自动 UV 展开功能，支持多种算法（如 Patch Builder、UVAtlas、XAtlas）。
- 你需要对网格进行简化、重拓扑、切割、打孔或布尔运算等复杂编辑。
- 你正在开发一个自定义的建模工具或工作流，并希望使用 UE 官方验证过的底层几何处理逻辑。

## 蓝图用法

本插件的核心操作符主要面向 C++ 开发，但通过 `UInteractiveToolPropertySet` 派生类暴露了大量可编辑的属性，这些属性可在蓝图中配置并用于驱动操作。

### 核心节点（属性配置）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Method` (EParameterizeMeshUVMethod) | 选择自动UV生成算法（PatchBuilder, UVAtlas, XAtlas） | `UParameterizeMeshToolProperties` |
| `IslandStretch` (float) | (UVAtlas) 控制UV岛的最大拉伸程度 | `UParameterizeMeshToolUVAtlasProperties` |
| `NumIslands` (int) | (UVAtlas) 提示期望的UV岛数量，0为自动 | `UParameterizeMeshToolUVAtlasProperties` |
| `InitialPatches` (int) | (PatchBuilder) 网格初始分割的面片数 | `UParameterizeMeshToolPatchBuilderProperties` |
| `bRepack` (bool) | (PatchBuilder) 是否将结果UV自动打包到[0,1]单位区间 | `UParameterizeMeshToolPatchBuilderProperties` |
| `TargetMode` (ESimplifyTargetType) | 简化目标类型（按百分比、三角形数、边长等） | `UParameterizeMeshToolPatchBuilderProperties` |

### 使用示例（蓝图描述）

1.  创建一个 `UParameterizeMeshToolProperties` 对象，将其 `Method` 属性设置为 `PatchBuilder`。
2.  创建对应的 `UParameterizeMeshToolPatchBuilderProperties` 对象，配置 `InitialPatches`、`bRepack` 等参数。
3.  将这些属性对象传递给 `UParameterizeMeshOperatorFactory`，该工厂负责创建实际执行UV计算的 `FDynamicMeshOperator`。
4.  将工厂与一个 `UMeshOpPreviewWithBackgroundCompute` 组件关联，以异步、可预览的方式执行操作。

## C++ 用法

### 头文件引入

```cpp
#include "ParameterizeMeshOp.h"
#include "SimplifyMeshOp.h"
#include "EmbedPolygonsOp.h"
```

### 基本用法

使用 `FSimplifyMeshOp` 简化一个动态网格。
*来源：基于 `Public/CleaningOps/SimplifyMeshOp.h` 的接口推断*

```cpp
#include "DynamicMesh/DynamicMesh3.h"
#include "ModelingOperators/CleaningOps/SimplifyMeshOp.h"

// 假设已有源网格
TSharedPtr<UE::Geometry::FDynamicMesh3, ESPMode::ThreadSafe> SourceMesh = ...;

// 创建简化操作符
UE::Geometry::FSimplifyMeshOp SimplifyOp;
SimplifyOp.OriginalMesh = SourceMesh;
SimplifyOp.SimplifierType = UE::Geometry::ESimplifyType::QEM;
SimplifyOp.TargetMode = UE::Geometry::ESimplifyTargetType::Percentage;
SimplifyOp.TargetPercentage = 50; // 简化50%
SimplifyOp.bDiscardAttributes = false;

// 执行操作（通常在后台线程）
SimplifyOp.CalculateResult(nullptr);

// 获取结果
TUniquePtr<UE::Geometry::FDynamicMesh3> ResultMesh = SimplifyOp.ExtractResult();
```

### 进阶用法

使用 `UParameterizeMeshOperatorFactory` 配置并执行自动UV展开。
*来源：基于 `Public/ParameterizationOps/ParameterizeMeshOp.h` 和 `Public/Properties/ParameterizeMeshProperties.h` 的组合*

```cpp
#include "ParameterizeMeshOp.h"
#include "Properties/ParameterizeMeshProperties.h"

// 创建属性对象
UParameterizeMeshToolProperties* Settings = NewObject<UParameterizeMeshToolProperties>();
Settings->Method = EParameterizeMeshUVMethod::PatchBuilder;

UParameterizeMeshToolPatchBuilderProperties* PatchSettings = NewObject<UParameterizeMeshToolPatchBuilderProperties>();
PatchSettings->InitialPatches = 200;
PatchSettings->bRepack = true;

// 创建操作符工厂
UParameterizeMeshOperatorFactory* OperatorFactory = NewObject<UParameterizeMeshOperatorFactory>();
OperatorFactory->Settings = Settings;
OperatorFactory->PatchBuilderProperties = PatchSettings;
OperatorFactory->OriginalMesh = SourceMesh; // 传入源网格

// 创建操作符实例并执行
TUniquePtr<UE::Geometry::FDynamicMeshOperator> Op = OperatorFactory->MakeNewOperator();
Op->CalculateResult(nullptr);

// 从操作符中获取结果（具体方法取决于操作符实现）
// ...
```

## Demo 示例

一个最小的 C++ 示例，演示如何使用 `FSimplifyMeshOp`。
*注意：实际应用中，操作通常在 `BackgroundCompute` 或 `AsyncTask` 中执行。*

```cpp
// MinimalSimplifyExample.h
#pragma once

#include "CoreMinimal.h"
#include "DynamicMesh/DynamicMesh3.h"

class FMinimalSimplifyExample
{
public:
    static TUniquePtr<UE::Geometry::FDynamicMesh3> SimplifyMesh(
        const TSharedPtr<UE::Geometry::FDynamicMesh3, ESPMode::ThreadSafe>& InputMesh,
        float ReducePercentage);
};
```

```cpp
// MinimalSimplifyExample.cpp
#include "MinimalSimplifyExample.h"
#include "ModelingOperators/CleaningOps/SimplifyMeshOp.h"

TUniquePtr<UE::Geometry::FDynamicMesh3> FMinimalSimplifyExample::SimplifyMesh(
    const TSharedPtr<UE::Geometry::FDynamicMesh3, ESPMode::ThreadSafe>& InputMesh,
    float ReducePercentage)
{
    using namespace UE::Geometry;

    if (!InputMesh.IsValid())
    {
        return nullptr;
    }

    FSimplifyMeshOp SimplifyOp;
    SimplifyOp.OriginalMesh = InputMesh;
    SimplifyOp.SimplifierType = ESimplifyType::QEM;
    SimplifyOp.TargetMode = ESimplifyTargetType::Percentage;
    SimplifyOp.TargetPercentage = FMath::Clamp(ReducePercentage, 0.f, 100.f);
    SimplifyOp.bDiscardAttributes = false;

    // 同步执行（仅用于示例，生产环境应使用异步）
    SimplifyOp.CalculateResult(nullptr);

    return SimplifyOp.ExtractResult();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GeometryProcessing` | 提供核心的几何处理算法（如简化、UV计算、布尔运算） |
| `GeometryFramework` | 提供交互式工具框架（Interactive Tools Framework）的基础设施 |
| `DynamicMesh` | 提供 `FDynamicMesh3` 等核心动态网格数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树刷新时保持选择状态，防止不相关操作重置选择 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 网格顶点属性绘制和蒙皮权重绘制工具新增跨模式同步画笔半径功能 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 编辑骨骼工具在删除骨骼时，将权重重定向至根骨骼而非丢失 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点属性绘制笔画累加器以支持松弛笔刷，并修复问题 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 几何体选择在仅编辑顶点时跳过组拓扑重建，优化性能 |

### 维护评价

该插件处于**活跃维护**状态。尽管其初始版本标记为 Beta 且默认隐藏，但从近期（2026年5月）的频繁提交可以看出，它仍是 Epic 官方建模工具链的核心组成部分，持续获得新功能和优化（如笔刷同步、骨骼编辑改进、性能优化）。它作为底层“引擎”为 `ModelingToolsEditorMode` 等上层模块提供动力，对于需要运行时网格操作或自定义建模工具的开发者来说，这是一个强大但复杂的工具集。由于其 `IsBetaVersion = true` 且 `Hidden = true`，在生产环境中使用需谨慎评估稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- [官方文档]() （暂无）
- [测试用例]() （暂未发现插件目录内的标准测试）