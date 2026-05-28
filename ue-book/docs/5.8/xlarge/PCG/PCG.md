# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG（Procedural Content Generation Framework）是 UE5 的程序化内容生成框架，提供了一套**可视化节点图**系统，用于在编辑器或运行时程序化地生成和填充世界内容。

这个框架解决了以下核心问题：

- **大规模场景程序化生成**：通过节点图定义生成规则，自动在世界中放置植被、建筑、装饰物等
- **GPU 加速计算**：通过 Compute Shader 支持，将点操作、实例化等计算密集型任务卸载到 GPU
- **运行时动态生成**：支持基于玩家位置、摄像机朝向等运行时条件，按需流式生成/清理世界内容
- **World Partition 集成**：与 UE5 的 World Partition 系统深度集成，支持分区块生成
- **变更追踪与缓存**：自动检测源数据变化并智能刷新，避免不必要的重新生成
- **确定性输出**：相同输入产生相同结果，支持多人协作和增量构建

框架基于 **点数据（Point Data）** 的概念——程序化生成的每个"点"包含变换、密度、颜色、种子等属性，通过节点链处理后最终转化为实例化静态网格、景观层等实际世界对象。

## 使用场景

- 你正在构建开放世界游戏，需要在大面积地形上程序化放置植被、岩石、建筑 → 用 PCG 节点图定义规则并自动生成
- 你需要根据玩家位置动态生成/回收世界内容，减少内存和渲染开销 → 用 PCG 的运行时生成功能
- 你希望美术师能通过可视化方式调整程序化生成规则 → 用 PCG 的节点图编辑器
- 你的生成逻辑涉及大量点操作（采样、过滤、变换）→ 用 PCG 的 GPU Compute 加速
- 你使用 World Partition 进行大规模世界管理 → 用 PCG 的分区生成和 Partition Actor 支持
- 你需要基于规则将线段/路径细分并填充模块（如建筑立面、栅栏）→ 用 PCG 的 Grammar/Subdivision 节点

## 蓝图用法

### 核心节点 — 自定义 PCG 节点

通过继承 `UPCGBlueprintBaseElement` 创建自定义 PCG 蓝图节点。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 节点主执行函数，接收输入数据，写入输出数据 | `UPCGBlueprintBaseElement` |
| `NodeTitleOverride` | 覆盖节点在图中显示的名称 | `UPCGBlueprintBaseElement` |
| `NodeColorOverride` | 覆盖节点在图中显示的颜色 | `UPCGBlueprintBaseElement` |
| `NodeTypeOverride` | 覆盖节点类型 | `UPCGBlueprintBaseElement` |
| `GetContextHandle` | 获取当前执行上下文句柄 | `UPCGBlueprintBaseElement` |
| `GetSeedWithContext` | 从上下文获取确定性种子 | `UPCGBlueprintBaseElement` |
| `GetRandomStreamWithContext` | 创建基于种子的随机流 | `UPCGBlueprintBaseElement` |
| `GetInputPins` | 获取输入引脚列表 | `UPCGBlueprintBaseElement` |
| `GetOutputPins` | 获取输出引脚列表 | `UPCGBlueprintBaseElement` |
| `CustomInputLabels` | 获取自定义输入引脚标签 | `UPCGBlueprintBaseElement` |
| `CustomOutputLabels` | 获取自定义输出引脚标签 | `UPCGBlueprintBaseElement` |

### 核心节点 — 点数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 获取点数量 | `UPCGBasePointData` |
| `SetNumPoints` | 设置点数量 | `UPCGBasePointData` |
| `GetTransform` | 按索引获取单个点变换 | `UPCGBasePointData` |
| `SetTransform` | 将所有点变换设为同一值 | `UPCGBasePointData` |
| `GetDensity` / `SetDensity` | 获取/设置点密度 | `UPCGBasePointData` |
| `GetColor` / `SetColor` | 获取/设置点颜色 | `UPCGBasePointData` |
| `GetSeed` / `SetSeed` | 获取/设置点种子 | `UPCGBasePointData` |
| `GetBoundsMin` / `SetBoundsMin` | 获取/设置包围盒最小值 | `UPCGBasePointData` |
| `GetBoundsMax` / `SetBoundsMax` | 获取/设置包围盒最大值 | `UPCGBasePointData` |
| `GetExtents` | 获取点范围 | `UPCGBasePointData` |
| `GetLocalBounds` | 获取局部包围盒 | `UPCGBasePointData` |
| `GetDensityBounds` | 获取密度包围盒 | `UPCGBasePointData` |
| `BP_SetPointsFrom` | 从源数据复制指定索引的点 | `UPCGBasePointData` |
| `BP_AllocateProperties` | 按位掩码分配点属性内存 | `UPCGBasePointData` |

### 核心节点 — 批量读写（基于范围）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTransformValuesFromRange` | 从范围批量读取变换 | `UPCGBasePointData` (Static) |
| `SetTransformValuesOnRange` | 向范围批量写入变换 | `UPCGBasePointData` (Static) |
| `GetDensityValuesFromRange` / `SetDensityValuesOnRange` | 批量读写密度 | `UPCGBasePointData` (Static) |
| `GetPointFromRange` | 从范围获取单个点 | `UPCGBasePointData` (Static) |
| `SetPointOnRange` | 向范围设置单个点 | `UPCGBasePointData` (Static) |

### 核心节点 — 运行时调度

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ScheduleGraph` | 调度 PCG 图执行 | `IPCGBaseSubsystem` |
| `ScheduleGeneric` | 调度通用任务 | `IPCGBaseSubsystem` |
| `CancelGeneration` | 取消正在执行的生成 | `IPCGBaseSubsystem` |
| `IsGraphCurrentlyExecuting` | 检查图是否正在执行 | `IPCGBaseSubsystem` |
| `GetOutputData` | 获取任务输出数据 | `IPCGBaseSubsystem` |

### 使用示例（蓝图描述）

**创建自定义 PCG 蓝图节点：**

1. 在内容浏览器中右键 → Blueprint Class → 选择 `PCGBlueprintBaseElement` 作为父类
2. 打开蓝图，在 `Class Defaults` 中配置：
   - `Custom Input Pins`：添加你需要的输入引脚（如 "Points" 类型为 Point）
   - `Custom Output Pins`：添加你需要的输出引脚
   - `b Has Default In Pin` / `b Has Default Out Pin`：控制是否保留默认 In/Out 引脚
   - `b Is Cacheable`：如果你的节点不产生副作用，设为 true 以启用缓存
3. 覆盖 `Execute` 函数：
   - 从 `Input` 参数的 `TaggedData` 数组中读取输入数据
   - 创建或修改 `UPCGBasePointData` 对象
   - 将结果写入 `Output` 参数的 `TaggedData` 数组
4. （可选）覆盖 `Node Title Override` 和 `Node Color Override` 自定义外观

**读写点数据：**

```
[Get Input Data] → (Cast to UPCGBasePointData) → [Get Num Points] → Loop
    → [Get Transform(Index)] → [计算新变换] → [Set Transform 在新 PointData 上]
    → [Set Density / Set Color / ...]
    → [将 PointData 添加到 Output Tagged Data]
```

## C++ 用法

### 头文件引入

```cpp
#include "PCGBlueprintBaseElement.h"
#include "PCGBasePointData.h"
#include "PCGContext.h"
#include "PCGDataCollection.h"
#include "PCGModule.h"
```

### 基本用法 — 创建自定义 PCG 元素

从源码中的蓝图元素接口提取的标准用法。

```cpp
// MyPCGElement.h
#pragma once

#include "PCGBlueprintBaseElement.h"
#include "MyPCGElement.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyPCGElement : public UPCGBlueprintBaseElement
{
    GENERATED_BODY()

public:
    // 主执行函数
    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PCG|Execution")
    void Execute(const FPCGDataCollection& Input, FPCGDataCollection& Output);

    // 自定义节点名称
    UFUNCTION(BlueprintNativeEvent, Category = "PCG|Node Customization")
    FName NodeTitleOverride() const;

    // 自定义节点颜色
    UFUNCTION(BlueprintNativeEvent, Category = "PCG|Node Customization")
    FLinearColor NodeColorOverride() const;
};
```

```cpp
// MyPCGElement.cpp
#include "MyPCGElement.h"
#include "PCGBasePointData.h"
#include "PCGContext.h"

void UMyPCGElement::Execute_Implementation(const FPCGDataCollection& Input, FPCGDataCollection& Output)
{
    // 获取执行上下文中的种子
    FPCGBlueprintContextHandle ContextHandle = GetContextHandle();
    int32 Seed = GetSeedWithContext(ContextHandle);
    FRandomStream RandomStream = GetRandomStreamWithContext(ContextHandle);

    // 遍历输入数据
    for (const FPCGTaggedData& TaggedInput : Input.TaggedData)
    {
        const UPCGBasePointData* InputPointData = Cast<UPCGBasePointData>(TaggedInput.Data);
        if (!InputPointData || InputPointData->IsEmpty())
        {
            continue;
        }

        // 创建输出点数据
        UPCGBasePointData* OutputPointData = NewObject<UPCGBasePointData>();
        int32 NumPoints = InputPointData->GetNumPoints();
        OutputPointData->SetNumPoints(NumPoints);

        // 获取变换的值范围（高效批量访问）
        auto InputTransforms = InputPointData->GetConstTransformValueRange();
        auto OutputTransforms = OutputPointData->GetTransformValueRange();

        // 批量处理点
        for (int32 i = 0; i < NumPoints; ++i)
        {
            FTransform T = InputTransforms[i];
            // 对变换进行修改...
            T.AddToTranslation(FVector(0, 0, RandomStream.FRandRange(-10.f, 10.f)));
            OutputTransforms[i] = T;
        }

        // 将结果添加到输出
        FPCGTaggedData& TaggedOutput = Output.TaggedData.Emplace_GetRef();
        TaggedOutput.Data = OutputPointData;
        TaggedOutput.Pin = TaggedInput.Pin;
    }
}

FName UMyPCGElement::NodeTitleOverride_Implementation() const
{
    return TEXT("My Custom Node");
}

FLinearColor UMyPCGElement::NodeColorOverride_Implementation() const
{
    return FLinearColor::Green;
}
```

### 进阶用法 — 使用时间切片（Time-Sliced）执行

从 `PCGTimeSlicedElementBase.h` 和 `PCGSurfaceSampler.h` 提取的模式，用于长时间运行的操作。

```cpp
// 声明 per-execution 和 per-iteration 状态
struct FMyExecState
{
    // 在整个执行期间不变的数据（如节点设置）
    FBox Bounds;
    float Density;
    int32 NumPoints;
};

struct FMyIterState
{
    // 每次迭代变化的数据（如当前处理的形状）
    TArray<FTransform> GeneratedTransforms;
};

// 继承时间切片元素基类
class FMyTimeSlicedElement : public TPCGTimeSlicedElementBase<FMyExecState, FMyIterState>
{
protected:
    virtual bool PrepareDataInternal(FPCGContext* Context) const override
    {
        auto* MyContext = static_cast<ContextType*>(Context);

        // 初始化 per-execution 状态（只执行一次）
        auto ExecResult = MyContext->InitializePerExecutionState(
            [](ContextType* InContext, FMyExecState& OutState) -> EPCGTimeSliceInitResult
            {
                // 从上下文/设置中读取参数
                OutState.Bounds = FBox(FVector(-1000), FVector(1000));
                OutState.Density = 0.5f;
                OutState.NumPoints = 1000;
                return EPCGTimeSliceInitResult::Success;
            });

        if (ExecResult == EPCGTimeSliceInitResult::AbortExecution)
        {
            return false;
        }

        // 初始化 per-iteration 状态（每个输入形状执行一次）
        MyContext->InitializePerIterationStates(/*NumIterations=*/1,
            [](FMyIterState& OutState, const FMyExecState& ExecState, uint32 Index) -> EPCGTimeSliceInitResult
            {
                // 准备迭代数据
                return EPCGTimeSliceInitResult::Success;
            });

        return MyContext->DataIsPreparedForExecution();
    }

    virtual bool ExecuteInternal(FPCGContext* Context) const override
    {
        auto* MyContext = static_cast<ContextType*>(Context);

        return ExecuteSlice(MyContext,
            [](ContextType* InContext, const FMyExecState& ExecState,
               FMyIterState& IterState, uint32 IterationIndex) -> bool
            {
                // 每次切片处理一部分工作
                // 返回 true 表示当前迭代完成，false 表示还需要继续
                return true;
            });
    }
};
```

### 进阶用法 — 通过 PCGSubsystem 调度图执行

```cpp
#include "Subsystems/PCGSubsystem.h"

void AMyActor::SpawnProceduralContent()
{
    UWorld* World = GetWorld();
    UPCGSubsystem* PCGSubsystem = UPCGSubsystem::GetInstance(World);
    if (!PCGSubsystem) return;

    // 通过子系统调度通用任务
    PCGSubsystem->ScheduleGeneric(
        [this]() -> bool
        {
            // 执行任务逻辑
            // 返回 true 表示任务完成
            return true;
        },
        /*ExecutionSource=*/nullptr,
        /*TaskDependencies=*/{});
}
```

## Demo 示例

### 自定义 PCG 元素（C++）

```cpp
// RandomOffsetPCGNode.h
#pragma once

#include "PCGBlueprintBaseElement.h"
#include "RandomOffsetPCGNode.generated.h"

/**
 * 自定义 PCG 节点：对输入点施加随机偏移
 */
UCLASS(BlueprintType, Blueprintable)
class URandomOffsetPCGNode : public UPCGBlueprintBaseElement
{
    GENERATED_BODY()

public:
    URandomOffsetPCGNode();

    UFUNCTION(BlueprintNativeEvent, BlueprintCallable, Category = "PCG|Execution")
    void Execute(const FPCGDataCollection& Input, FPCGDataCollection& Output);

    UFUNCTION(BlueprintNativeEvent, Category = "PCG|Node Customization")
    FName NodeTitleOverride() const;

    UFUNCTION(BlueprintNativeEvent, Category = "PCG|Node Customization")
    FLinearColor NodeColorOverride() const;

    /** 随机偏移范围 (cm) */
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = "Settings")
    float OffsetRadius = 100.0f;
};
```

```cpp
// RandomOffsetPCGNode.cpp
#include "RandomOffsetPCGNode.h"
#include "PCGBasePointData.h"
#include "PCGContext.h"

URandomOffsetPCGNode::URandomOffsetPCGNode()
{
    // 配置输入引脚：接受 Point 数据
    CustomInputPins.Emplace(TEXT("In"), EPCGDataType::Point);
    // 配置输出引脚：输出 Point 数据
    CustomOutputPins.Emplace(TEXT("Out"), EPCGDataType::Point);
    bHasDefaultInPin = false;
    bHasDefaultOutPin = false;
    bIsCacheable = true;
}

void URandomOffsetPCGNode::Execute_Implementation(
    const FPCGDataCollection& Input, FPCGDataCollection& Output)
{
    // 获取种子用于确定性随机
    FPCGBlueprintContextHandle ContextHandle = GetContextHandle();
    FRandomStream RandomStream = GetRandomStreamWithContext(ContextHandle);

    for (const FPCGTaggedData& TaggedInput : Input.TaggedData)
    {
        if (TaggedInput.Pin != TEXT("In"))
        {
            continue;
        }

        const UPCGBasePointData* InputData =
            Cast<const UPCGBasePointData>(TaggedInput.Data);
        if (!InputData || InputData->IsEmpty())
        {
            continue;
        }

        const int32 NumPoints = InputData->GetNumPoints();

        // 创建输出数据并复制输入点
        UPCGBasePointData* OutputData = InputData->DuplicateData();
        OutputData->SetNumPoints(NumPoints);

        // 获取高效批量访问器
        auto InTransforms = InputData->GetConstTransformValueRange();
        auto OutTransforms = OutputData->GetTransformValueRange();

        // 处理每个点
        for (int32 i = 0; i < NumPoints; ++i)
        {
            FTransform T = InTransforms[i];
            FVector RandomOffset(
                RandomStream.FRandRange(-OffsetRadius, OffsetRadius),
                RandomStream.FRandRange(-OffsetRadius, OffsetRadius),
                RandomStream.FRandRange(-OffsetRadius * 0.1f, OffsetRadius * 0.1f)
            );
            T.AddToTranslation(RandomOffset);
            OutTransforms[i] = T;
        }

        FPCGTaggedData& TaggedOutput = Output.TaggedData.Emplace_GetRef();
        TaggedOutput.Data = OutputData;
        TaggedOutput.Pin = TEXT("Out");
    }
}

FName URandomOffsetPCGNode::NodeTitleOverride_Implementation() const
{
    return TEXT("Random Offset");
}

FLinearColor URandomOffsetPCGNode::NodeColorOverride_Implementation() const
{
    return FLinearColor(0.2f, 0.8f, 0.4f); // 浅绿色
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

PCG 框架的各个模块之间有以下内部依赖关系：

| 模块 | 用途 |
|---|---|
| `PCGCompute` | GPU Compute Shader 集成（Landscape/Texture 数据接口、内核参数传递） |
| `PCGEditor` | 编辑器图编辑器 UI、节点可视化、调试工具 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复构建地形缓存时部分条目无法解析导致的潜在崩溃 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化 PCG 组件可视化器的性能 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复访问器中空对象导致的崩溃 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存元数据大小计算，通过标志门控 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspection | 修复手动编辑相关的编辑器更新性能问题和双重更新 |

### 维护评价

PCG 框架是 **Epic Games 官方维护**的核心插件，**处于高度活跃维护状态**：

- **创建时间**：2024 年 1 月从 Experimental 迁移为正式插件
- **更新频率**：非常频繁，仅最近一批提交就包含 5 个同日 commit，涵盖 bug 修复、性能优化和新功能
- **代码规模**：1472 个源文件，是引擎中最大规模的插件之一，说明持续投入大量开发资源
- **模块完善**：包含运行时核心（PCG）、GPU 计算（PCGCompute）、编辑器（PCGEditor）、测试（PCGTests）完整四模块
- **测试覆盖**：内置 PCGTests 模块，有完善的确定性测试和自动化测试

**推荐使用**。PCG 是 UE5 的战略性功能，Epic Games 在每个版本中持续改进。虽然框架相对年轻（约 2.5 年），但已从 Experimental 毕业，API 趋于稳定。注意部分功能仍标记为实验性（如交互式工具相关代码），使用时关注 API 废弃标记（`UE_DEPRECATED`）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG/Tests)