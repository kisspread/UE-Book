# Mesh Modeling Toolset

> A set of modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质模板、蓝图资产） |
| 模块 | `MeshModelingTools` (Runtime), `MeshModelingToolsEditorOnly` (Runtime), `ModelingComponents` (Runtime), `ModelingComponentsEditorOnly` (Runtime), `ModelingOperators` (Runtime), `ModelingOperatorsEditorOnly` (Runtime), `SkeletalMeshModifiers` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset) | |

> **⚠️ 重要提示**：此插件标记为 `Hidden=true` 且 `IsBetaVersion=true`，默认**不会**出现在插件列表中。需要在项目设置中手动搜索并启用。本文档聚焦于 **ModelingOperators** 模块，该模块实现了插件中所有网格操作的底层计算逻辑。

## 用途

MeshModelingToolset 是 UE5 的运行时程序化网格建模框架。它将传统的"编辑器内建模"抽象为可后台执行的**操作符（Operator）模式**——每个网格操作（布尔运算、偏移、平滑、UV 重算等）被封装为独立的 `FDynamicMeshOperator` 子类，可异步执行、可取消、可参数化。

**为什么存在**：UE5 的 Interactive Tools Framework 需要一种标准化的方式来运行复杂的几何操作，而不会阻塞游戏线程。ModelingOperators 提供了：
- 统一的异步计算框架（`TBackgroundModelingComputeSource`）
- 可取消的后台任务（`FAbortableBackgroundTask`）
- 数十个即用型几何操作符（布尔、偏移、平滑、UV、切割等）

当前聚焦模块 **ModelingOperators** 是纯计算层，不包含 UI 或编辑器交互逻辑，可在运行时安全使用。

## 使用场景

- 你在运行时需要程序化地对网格做布尔运算（合并/相减/相交）→ 使用 `FBooleanMeshesOp`
- 你需要在后台线程中执行昂贵的网格操作并支持用户取消 → 使用 `TBackgroundModelingComputeSource`
- 你需要沿法线方向偏移网格表面（如生成壳体/护盾效果）→ 使用 `FIterativeOffsetMeshOp`
- 你需要程序化重算 UV 展开 → 使用 `URecomputeUVsOpFactory`
- 你需要对骨骼蒙皮网格做程序化修改 → 使用 `FSkinBindingOp`
- 你需要在运行时对网格做平滑处理 → 使用 `FIterativeSmoothingOp` / `FCotanSmoothingOp`

## 蓝图用法

ModelingOperators 模块主要是 C++ 运算层，但部分操作通过 UObject 工厂暴露给蓝图系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeNewOperator` | 创建 UV 重算操作符实例 | `URecomputeUVsOpFactory` |
| `MakeNewOperator` | 创建 UV 布局操作符实例 | `UUVLayoutOperatorFactory` |
| `MakeNewOperator` | 创建 Texel Density 操作符实例 | `UUVTexelDensityOperatorFactory` |
| `MakeNewOperator` | 创建截面操作符实例 | `UGenerateCrossSectionOpFactory` |

### 蓝图属性集

模块还暴露了以下 `UInteractiveToolPropertySet` 子类，可用于蓝图 Details 面板配置：

| 类名 | 说明 |
|---|---|
| `URecomputeUVsToolProperties` | UV 重算参数（展开方式、岛合并、布局策略） |
| `UUVLayoutProperties` | UV 布局参数（缩放、平移、打包、UDIM） |
| `UUVEditorTexelDensitySettings` | Texel Density 参数（世界单位、像素密度） |

### 使用示例（蓝图描述）

**在蓝图中使用 UV 布局操作符**：
1. 创建 `UUVLayoutOperatorFactory` 对象
2. 设置其 `Settings` 属性（引用 `UUVLayoutProperties`）
3. 设置 `OriginalMesh` 为你的 `FDynamicMesh3`
4. 调用 `MakeNewOperator()` 获取 `FDynamicMeshOperator`
5. 在后台线程调用 `CalculateResult()` 并通过 `ExtractResult()` 获取结果网格

## C++ 用法

### 头文件引入

```cpp
// 核心操作符基类
#include "ModelingOperators.h"

// 后台计算框架
#include "BackgroundModelingComputeSource.h"

// 具体操作符
#include "BooleanMeshesOp.h"
#include "IterativeOffsetMeshOp.h"
#include "IterativeSmoothingOp.h"
#include "RemeshMeshOp.h"
#include "PlaneCutOp.h"
#include "ExtrudeOp.h"
```

### 基本用法：执行布尔运算

从源码中 `FBooleanMeshesOp` 的接口提取：

```cpp
// 来源: Public/CompositionOps/BooleanMeshesOp.h

#include "CompositionOps/BooleanMeshesOp.h"

using namespace UE::Geometry;

// 创建布尔操作符
FBooleanMeshesOp BooleanOp;

// 设置输入网格（两个相交的网格）
BooleanOp.Meshes.Add(MeshA);
BooleanOp.Meshes.Add(MeshB);
BooleanOp.Transforms.Add(TransformA);
BooleanOp.Transforms.Add(TransformB);

// 设置操作类型：差集、交集、并集
BooleanOp.CSGOperation = ECSGOperation::Union;
BooleanOp.bAttemptFixHoles = true;

// 设置输出变换
BooleanOp.SetTransform(OutputTransform);

// 执行计算（可传入 FProgressCancel 实现取消）
BooleanOp.CalculateResult(nullptr);

// 提取结果
TUniquePtr<FDynamicMesh3> ResultMesh = BooleanOp.ExtractResult();
```

### 基本用法：网格偏移（生成壳体）

```cpp
// 来源: Public/DeformationOps/MeshOffsetOps.h

#include "DeformationOps/MeshOffsetOps.h"

using namespace UE::Geometry;

// 创建迭代偏移操作符
FIterativeOffsetMeshOp OffsetOp(InputMesh);

// 配置偏移参数
OffsetOp.OffsetRange = FInterval1d(0.0, 5.0);  // 偏移范围 0-5 单位
OffsetOp.OffsetSign = 1.0;                       // 正向偏移（向外）
OffsetOp.bCreateShell = true;                     // 创建壳体（双面网格）
OffsetOp.Steps = 3;                               // 多步迭代
OffsetOp.SmoothAlpha = 0.1;                       // 平滑系数
OffsetOp.bFixedBoundary = false;                  // 边界不固定

// 需要设置法线
OffsetOp.BaseNormals = MakeShared<FMeshNormals>(InputMesh);
OffsetOp.BaseNormals->ComputeVertexNormals();

// 需要设置边界信息（壳体模式需要）
OffsetOp.BoundaryLoops = MakeShared<FMeshBoundaryLoops>();
OffsetOp.BoundaryLoops->FindBoundaryLoops(*InputMesh);

// 执行偏移
OffsetOp.CalculateResult(nullptr);

// 获取结果（壳体 = 内外两个网格通过边界焊接/缝合）
TUniquePtr<FDynamicMesh3> ShellMesh = OffsetOp.ExtractResult();
```

### 基本用法：平滑操作

```cpp
// 来源: Public/SmoothingOps/IterativeSmoothingOp.h

#include "SmoothingOps/IterativeSmoothingOp.h"

using namespace UE::Geometry;

// 配置平滑选项
FSmoothingOpBase::FOptions SmoothOpts;
SmoothOpts.SmoothAlpha = 0.5f;           // 平滑强度
SmoothOpts.BoundarySmoothAlpha = 0.3f;   // 边界平滑强度
SmoothOpts.Iterations = 10;              // 迭代次数
SmoothOpts.bSmoothBoundary = true;       // 是否平滑边界
SmoothOpts.bUniform = false;             // 使用非均匀权重

// 创建迭代平滑操作符
FIterativeSmoothingOp SmoothOp(InputMesh, SmoothOpts);

// 执行平滑
SmoothOp.CalculateResult(nullptr);

// 获取结果
TUniquePtr<FDynamicMesh3> SmoothedMesh = SmoothOp.ExtractResult();
```

### 进阶用法：后台异步计算框架

这是 ModelingOperators 最核心的架构组件——`TBackgroundModelingComputeSource` 提供了支持取消、延迟重启、进度查询的异步执行框架。

```cpp
// 来源: Public/BackgroundModelingComputeSource.h

#include "BackgroundModelingComputeSource.h"

using namespace UE::Geometry;

// 1. 定义操作符工厂（负责创建操作符实例）
class FMyOpFactory
{
public:
    TSharedPtr<FDynamicMesh3, ESPMode::ThreadSafe> Mesh;
    
    TUniquePtr<FBooleanMeshesOp> MakeNewOperator()
    {
        auto Op = MakeUnique<FBooleanMeshesOp>();
        Op->Meshes.Add(Mesh);
        Op->CSGOperation = ECSGOperation::Union;
        return Op;
    }
};

// 2. 创建后台计算源
FMyOpFactory Factory;
Factory.Mesh = MyMesh;

TBackgroundModelingComputeSource<FBooleanMeshesOp, FMyOpFactory> 
    ComputeSource(&Factory);

// 配置取消延迟（默认 0.5 秒，避免参数拖动时频繁重启）
ComputeSource.CancelActiveOpDelaySeconds = 0.3;

// 3. 当参数变化时通知重新计算
void OnParameterChanged()
{
    ComputeSource.NotifyActiveComputeInvalidated();
}

// 4. 每帧 Tick（必须调用，用于管理取消/重启时序）
void Tick(float DeltaTime)
{
    ComputeSource.Tick(DeltaTime);
    
    // 5. 检查状态
    auto Status = ComputeSource.CheckStatus();
    switch (Status.TaskStatus)
    {
    case EBackgroundComputeTaskStatus::ValidResultAvailable:
    {
        // 获取结果并应用
        auto ResultOp = ComputeSource.ExtractResult();
        TUniquePtr<FDynamicMesh3> NewMesh = ResultOp->ExtractResult();
        ApplyResult(MoveTemp(NewMesh));
        break;
    }
    case EBackgroundComputeTaskStatus::InProgress:
        // 显示进度条
        UE_LOG(LogTemp, Log, TEXT("Computing... %.2f seconds elapsed"), 
               Status.ElapsedTime);
        break;
    case EBackgroundComputeTaskStatus::Aborted:
        // 操作被取消
        break;
    default:
        break;
    }
}
```

### 进阶用法：可取消的后台任务

```cpp
// 来源: Public/ModelingTaskTypes.h

#include "ModelingTaskTypes.h"

using namespace UE::Geometry;

// 创建可取消的异步任务
auto* TaskExec = new FAsyncTaskExecuterWithAbort<TModelingOpTask<FRemeshMeshOp>>(
    MoveTemp(RemeshOp)
);

// 启动后台任务
TaskExec->StartBackgroundTask();

// ... 稍后需要取消时
TaskExec->CancelAndDelete();  // 设置取消标志，启动清理任务，可安全丢弃指针

// 如果需要进度轮询：
auto* ProgressTask = new FAsyncTaskExecuterWithProgressCancel<TModelingOpTask<FRemeshMeshOp>>(
    MoveTemp(RemeshOp)
);
ProgressTask->StartBackgroundTask();

float Progress;
FText Message;
if (ProgressTask->PollProgress(Progress, Message))
{
    UpdateProgressBar(Progress, Message);
}
```

## Demo 示例

以下是一个完整的、可在运行时执行的网格布尔运算最小示例：

```cpp
// MyMeshBooleanComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "CompositionOps/BooleanMeshesOp.h"
#include "MyMeshBooleanComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMeshBooleanComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UStaticMesh* MeshA;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    UStaticMesh* MeshB;

    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    TEnumAsByte<ECSGOperation> Operation = ECSGOperation::Union;

    UFUNCTION(BlueprintCallable)
    void ExecuteBoolean();

private:
    TUniquePtr<UE::Geometry::FBooleanMeshesOp> ActiveOp;
    bool bIsComputing = false;
};

// MyMeshBooleanComponent.cpp
#include "MyMeshBooleanComponent.h"
#include "DynamicMesh/DynamicMesh3.h"
#include "MeshDescriptionToDynamicMesh.h"
#include "DynamicMeshToMeshDescription.h"
#include "StaticMeshResources.h"

using namespace UE::Geometry;

void UMyMeshBooleanComponent::ExecuteBoolean()
{
    if (!MeshA || !MeshB) return;

    // 从 StaticMesh 提取 DynamicMesh
    auto DynMeshA = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>();
    auto DynMeshB = MakeShared<FDynamicMesh3, ESPMode::ThreadSafe>();

    const FMeshDescription* DescA = MeshA->GetMeshDescription(0);
    const FMeshDescription* DescB = MeshB->GetMeshDescription(0);

    FMeshDescriptionToDynamicMesh Converter;
    Converter.Convert(DescA, *DynMeshA);
    Converter.Convert(DescB, *DynMeshB);

    // 创建布尔操作符
    ActiveOp = MakeUnique<FBooleanMeshesOp>();
    ActiveOp->Meshes.Add(DynMeshA);
    ActiveOp->Meshes.Add(DynMeshB);
    ActiveOp->Transforms.Add(FTransformSRT3d::Identity());
    ActiveOp->Transforms.Add(FTransformSRT3d::Identity());
    ActiveOp->CSGOperation = static_cast<ECSGOperation>(Operation.GetValue());
    ActiveOp->bAttemptFixHoles = true;

    // 同步执行（也可使用 TBackgroundModelingComputeSource 异步执行）
    ActiveOp->CalculateResult(nullptr);

    // 提取结果并转换回 MeshDescription
    TUniquePtr<FDynamicMesh3> Result = ActiveOp->ExtractResult();
    if (Result)
    {
        FMeshDescription OutputDesc;
        FDynamicMeshToMeshDescription ConverterOut;
        ConverterOut.Convert(Result.Get(), OutputDesc);

        // 创建新的 StaticMesh 或更新现有网格
        UE_LOG(LogTemp, Log, TEXT("Boolean operation completed: %d triangles"),
               Result->TriangleCount());
    }

    ActiveOp.Reset();
}
```

## 模块依赖

ModelingOperators 依赖以下**非标准**模块：

| 模块 | 用途 |
|---|---|
| `GeometryCore` | 动态网格（`FDynamicMesh3`）、几何算法基类 |
| `GeometryFramework` | `FProgressCancel`、交互工具框架基础设施 |
| `MeshConversion` | `FMeshDescriptionToDynamicMesh`、`FDynamicMeshToMeshDescription` 转换 |
| `MeshDescription` | 静态网格的中间表示格式 |
| `SkeletalMeshAttributes` | 骨骼网格权重属性（`FSkinBindingOp` 使用） |

> **注意**：已在 `Engine/Tests` 下发现相关自动化测试，编写自定义操作符时建议参考其用法模式。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `2cd4fab7` | SReferenceSkeletonTree: preserve selection across RefreshTreeView so unrelated | 骨骼树刷新时保留选择状态 |
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 顶点属性/蒙皮绘制工具添加跨模式笔刷同步 |
| 2026-05-26 | `1b791587` | [SkeletalMeshModelingTools] Edit Skeleton tool: route deleted-bone weights to root instead of droppi | 编辑骨骼工具：删除骨骼时将权重路由到根骨骼 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构笔划累加器以支持松弛笔刷并修复问题 |
| 2026-05-22 | `27bc20e6` | [GeometrySelection] Skip GroupTopology rebuild on vertex-only edits | 仅编辑顶点时跳过组拓扑重建以优化性能 |

### 维护评价

| 指标 | 评价 |
|---|---|
| 活跃度 | ✅ **活跃维护** — 2026 年 5 月仍有功能性更新 |
| 更新频率 | 高频更新，每周多次提交 |
| 功能状态 | Beta 但功能成熟，已深度集成到 UE5 编辑器工具链 |
| 稳定性 | 从 commit 来看持续有 bug 修复和性能优化 |
| 推荐度 | ⭐⭐⭐⭐ — **推荐使用**。虽然是 Beta 标记，但已成为 UE5 内置建模工具的核心引擎。注意标记为 Hidden，需手动启用。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MeshModelingToolset)
- [测试用例（Engine/Tests）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)
- [Interactive Tools Framework](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/ToolWidgets)
- [ModelingTools 编辑器层文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/ModelingToolsEditorMode)