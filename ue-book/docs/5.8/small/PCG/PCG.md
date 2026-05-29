# Procedural Content Generation Framework (PCG)

> Visual scripting framework for procedurally populating worlds with content in editor and/or at run-time.

| 属性 | 值 |
|---|---|
| 中文名 | 程序化内容生成框架 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（内置节点、Compute Shader 内核、蓝图模板） |
| 模块 | `PCG` (Runtime), `PCGCompute` (Runtime), `PCGEditor` (Runtime), `PCGTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-01-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG) | |

## 用途

PCG 是 UE5 的程序化内容生成核心框架，提供**基于节点图的可视化脚本系统**，用于在编辑器和/或运行时程序化地填充世界内容。

它解决的核心问题是：**如何高效、可复用地在大型开放世界中放置和管理海量程序化内容**。PCG 不仅是一个节点编辑器，更是一套完整的数据流执行架构，包含：

- **点云数据系统**：基于 `UPCGBasePointData` 的高性能点数据，支持 Transform、Density、Color、Seed 等属性的原生存储与内存映射操作
- **分区执行与 World Partition 集成**：通过 `APCGPartitionActor` 将大型生成任务拆分为网格单元，支持流式加载
- **GPU 计算加速**：通过 `PCGCompute` 模块将生成逻辑推送到 Compute Shader，实现 GPU 加速的采样、实例放置等操作
- **运行时生成调度**：`FPCGRuntimeGenScheduler` + `UPCGSchedulingPolicyBase` 提供基于优先级的运行时生成调度策略
- **变更追踪与增量更新**：`FPCGTrackingManager` 自动追踪场景变化，仅重新生成受影响区域

与简单的 `Foliage` 系统或手动物件放置不同，PCG 是面向**设计师工作流**的完整解决方案——通过节点图定义规则，在不同项目中复用，支持蓝图扩展，且可在运行时动态响应游戏状态变化。

## 使用场景

- 你需要在开放世界中根据地形高度、坡度和噪声分布植被、岩石 → 用 PCG Graph 定义采样规则和过滤条件
- 你需要在走廊和房间中程序化放置家具和装饰物，且要遵循空间约束 → 用 PCG 的 Subdivision 节点做语法驱动的分割放置
- 你需要根据玩家位置动态加载/卸载世界内容 → 用 PCG 的 Runtime Generation + Scheduling Policy
- 你需要在 GPU 上大规模生成和过滤点数据以获得更高性能 → 用 PCGCompute 的 Custom HLSL Kernel
- 你需要将 PCG 集成到游戏逻辑中，根据游戏事件触发内容重新生成 → 用 `UPCGSubsystem` 的 `ScheduleGraph` / `RefreshRuntimeGenExecutionSource` API

## 蓝图用法

### 点数据操作（UPCGBasePointData）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumPoints` | 获取点数量 | `UPCGBasePointData` |
| `IsEmpty` | 检查点数据是否为空 | `UPCGBasePointData` |
| `GetTransform` / `SetTransform` | 获取/设置所有点的变换 | `UPCGBasePointData` |
| `GetDensity` / `SetDensity` | 获取/设置点的密度值 | `UPCGBasePointData` |
| `GetColor` / `SetColor` | 获取/设置点的颜色 | `UPCGBasePointData` |
| `GetSeed` / `SetSeed` | 获取/设置点的随机种子 | `UPCGBasePointData` |
| `GetBoundsMin` / `GetBoundsMax` | 获取点的包围盒边界 | `UPCGBasePointData` |
| `BP_SetPointsFrom` | 从另一组点数据复制点（按索引） | `UPCGBasePointData` |
| `BP_AllocateProperties` | 分配指定的原生点属性内存 | `UPCGBasePointData` |
| `SetNumPoints` | 设置点数量（可选初始化默认值） | `UPCGBasePointData` |
| `GetTransformValuesFromRange` | 从范围获取变换值数组 | `UPCGBasePointData` (Static) |
| `SetTransformValuesOnRange` | 在范围内设置变换值数组 | `UPCGBasePointData` (Static) |

### 蓝图元素自定义（UPCGBlueprintBaseElement）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 主执行函数，接收输入/输出数据集合 | `UPCGBlueprintBaseElement` |
| `NodeTitleOverride` | 自定义节点显示名称 | `UPCGBlueprintBaseElement` |
| `NodeColorOverride` | 自定义节点颜色 | `UPCGBlueprintBaseElement` |
| `GetContextHandle` | 获取当前执行上下文句柄 | `UPCGBlueprintBaseElement` |
| `GetSeedWithContext` | 从上下文获取随机种子 | `UPCGBlueprintBaseElement` |
| `GetRandomStreamWithContext` | 从上下文获取随机流 | `UPCGBlueprintBaseElement` |
| `GetInputPins` / `GetOutputPins` | 获取输入/输出引脚列表 | `UPCGBlueprintBaseElement` |

### 使用示例（蓝图描述）

**创建自定义 PCG 蓝图节点**：
1. 创建一个继承 `UPCGBlueprintBaseElement` 的蓝图类
2. 在类默认中设置 `CustomInputPins` 和 `CustomOutputPins` 定义引脚
3. 重写 `Execute` 函数：从 `Input` 的 `TaggedData` 中获取输入数据，处理后写入 `Output`
4. 设置 `bIsCacheable = true`（如果输出确定性可缓存）以提升性能
5. 在 PCG Graph 编辑器中即可找到并使用该自定义节点

**读取点数据属性**：
1. 从 PCG 图的输出 pin 获取 `UPCGBasePointData`
2. 调用 `GetNumPoints()` 获取数量
3. 使用 `GetTransform(Index)`、`GetDensity(Index)` 等逐点读取
4. 或使用 `GetTransformValuesFromRange` 批量获取范围数据

## C++ 用法

### 头文件引入

```cpp
#include "PCGComponent.h"
#include "PCGSubsystem.h"
#include "PCGGraph.h"
#include "Data/PCGBasePointData.h"
#include "Elements/Blueprint/PCGBlueprintBaseElement.h"
```

### 基本用法 - 点数据操作

```cpp
// 来源: Public/Data/PCGBasePointData.h

// 创建点数据并操作
UPCGBasePointData* PointData = ...; // 从 PCG 执行获取

// 设置点数量
PointData->SetNumPoints(100);

// 批量设置所有点的密度
PointData->SetDensity(0.5f);

// 逐点读写
for (int32 i = 0; i < PointData->GetNumPoints(); ++i)
{
    FTransform Transform = PointData->GetTransform(i);
    float Density = PointData->GetDensity(i);
    FVector4 Color = PointData->GetColor(i);
    
    // 修改后写回
    // 使用 ValueRange API 进行高效批量操作
}
```

### 进阶用法 - ValueRange 高性能访问

```cpp
// 来源: Public/Data/PCGBasePointData.h

UPCGBasePointData* PointData = ...;

// 使用 ValueRange 进行内存映射的高效批量读写
// 先确保属性已分配
PointData->AllocateProperties(EPCGPointNativeProperties::Transform | EPCGPointNativeProperties::Density);

// 获取可写范围（内存映射，零拷贝）
FPCGPointTransform::ValueRange TransformRange = PointData->GetTransformValueRange(true);
FPCGPointDensity::ValueRange DensityRange = PointData->GetDensityValueRange(true);

for (int32 i = 0; i < PointData->GetNumPoints(); ++i)
{
    TransformRange[i] = FTransform(FRotator(0, FMath::FRandRange(0, 360), 0), FVector(i * 100, 0, 0));
    DensityRange[i] = FMath::FRandRange(0.1f, 1.0f);
}

// 获取只读范围
FPCGPointTransform::ConstValueRange ConstTransforms = PointData->GetConstTransformValueRange();

// 注意：SetNumPoints/AllocateProperties/FreeProperties 会使范围失效，操作后需重新获取
```

### 进阶用法 - 运行时图调度

```cpp
// 来源: Public/Subsystems/PCGSubsystem.h

UPCGSubsystem* Subsystem = UPCGSubsystem::GetInstance(GetWorld());
if (Subsystem)
{
    // 调度 PCG 组件生成
    FPCGTaskId TaskId = Subsystem->ScheduleComponent(PCGComponent, GridSize, bForce, Dependencies);
    
    // 调度自定义图
    FPCGTaskId GraphTaskId = Subsystem->ScheduleGraph(
        Graph, ExecutionSource, PreGraphElement, InputElement, Dependencies, FromStack, bAllowHierarchical);
    
    // 调度自定义工作
    FPCGTaskId GenericTaskId = Subsystem->ScheduleGeneric(
        []() { /* 返回 true 表示完成 */ return true; },
        ExecutionSource, TaskDependencies);
    
    // 刷新运行时生成源
    Subsystem->RefreshRuntimeGenExecutionSource(ExecutionSource, EPCGChangeType::None);
}
```

## Demo 示例

```cpp
// MyPCGPointProcessor.h
#pragma once

#include "PCGSettings.h"
#include "PCGContext.h"
#include "Elements/PCGPointOperationElementBase.h"
#include "MyPCGPointProcessor.generated.h"

UCLASS(BlueprintType, ClassGroup = (Procedural))
class UMyPCGPointProcessorSettings : public UPCGSettings
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float DensityThreshold = 0.5f;

    UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Settings, meta = (PCG_Overridable))
    float ScaleMultiplier = 1.0f;

protected:
    virtual TArray<FPCGPinProperties> InputPinProperties() const override;
    virtual TArray<FPCGPinProperties> OutputPinProperties() const override;
    virtual FPCGElementPtr CreateElement() const override;
};

class FMyPCGPointProcessorElement : public FPCGPointOperationElementBase
{
protected:
    virtual bool ExecuteInternal(FPCGContext* Context) const override;
};
```

```cpp
// MyPCGPointProcessor.cpp
#include "MyPCGPointProcessor.h"
#include "PCGContext.h"
#include "Data/PCGBasePointData.h"

TArray<FPCGPinProperties> UMyPCGPointProcessorSettings::InputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultInputLabel, EPCGDataType::Point);
    return Pins;
}

TArray<FPCGPinProperties> UMyPCGPointProcessorSettings::OutputPinProperties() const
{
    TArray<FPCGPinProperties> Pins;
    Pins.Emplace(PCGPinConstants::DefaultOutputLabel, EPCGDataType::Point);
    return Pins;
}

FPCGElementPtr UMyPCGPointProcessorSettings::CreateElement() const
{
    return MakeShared<FMyPCGPointProcessorElement>();
}

bool FMyPCGPointProcessorElement::ExecuteInternal(FPCGContext* Context) const
{
    const UMyPCGPointProcessorSettings* Settings = Context->GetInputSettings<UMyPCGPointProcessorSettings>();
    check(Settings);

    // 准备点数据
    if (!PreparePointOperationData(Context))
    {
        return true;
    }

    ContextType* TimeSlicedContext = static_cast<ContextType*>(Context);

    // 使用 ExecutePointOperation 对每个点执行操作
    const float Threshold = Settings->DensityThreshold;
    const float Scale = Settings->ScaleMultiplier;

    return ExecutePointOperation(TimeSlicedContext,
        [Threshold, Scale](const FPCGPoint& InPoint, FPCGPoint& OutPoint) -> bool
        {
            // 过滤低密度点
            if (InPoint.Density < Threshold)
            {
                OutPoint.Density = 0.0f; // 标记移除
                return true;
            }

            // 缩放变换
            OutPoint.Transform = InPoint.Transform;
            OutPoint.Transform.SetScale3D(InPoint.Transform.GetScale3D() * Scale);
            OutPoint.Density = InPoint.Density;
            return true;
        });
}
```

## 模块依赖

该插件模块众多，以下仅列出使用者需要关注的非标准依赖：

| 模块 | 用途 |
|---|---|
| `PCG` | 核心运行时模块（点数据、图执行、子系统） |
| `PCGCompute` | GPU 计算框架（Compute Shader 数据接口、内核） |
| `RenderCore` | Compute Framework 的渲染核心依赖 |
| `ComputeFramework` | GPU Compute 数据接口/提供者基础架构 |
| `Landscape` | 地形数据采样和缓存 |
| `WorldPartition` | World Partition 集成（分区 Actor 管理） |
| `StructUtils` | `FInstancedStruct` 支持（数据类型注册） |

使用者的 Build.cs 通常只需依赖 `PCG`（运行时使用）或 `PCG` + `PCGEditor`（编辑器扩展）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `1cd8cea5` | [PCG] Fixed potential crash when building the landscape cache, when some entries can't be resolved. | 修复构建地形缓存时未解析条目导致的潜在崩溃 |
| 2026-05-26 | `788faf05` | [PCG] Optimize FPCGComponentVisualizer | 优化 PCG 组件可视化器性能 |
| 2026-05-26 | `0532b644` | [PCG] Fix crash with null objects with accessors | 修复访问器处理空对象时的崩溃 |
| 2026-05-26 | `82ca98ed` | [PCG] Optimized & cached metadata size computation, but gated on a flag w/ TLS backing so the normal | 优化并缓存元数据大小计算，使用 TLS 标志控制 |
| 2026-05-26 | `585bbecb` | [PCG] Fixed editor update performance issue related to manual edit (+ a double update) and inspectio | 修复编辑器中手动编辑相关的性能问题和双重更新 |

### 维护评价

**活跃维护**。PCG 是 Epic 的重点维护项目，具备以下特征：

- **高频率更新**：几乎每天都有提交，涵盖 bug 修复、性能优化和新功能
- **近期有实质性改动**：2026 年 5 月仍在积极修复崩溃和优化性能
- **架构持续演进**：从 5.4 版本移出实验状态后，持续引入 Compute GPU 加速、Scheduling Policy 等新架构
- **向后兼容处理**：源码中可见大量 `UE_DEPRECATED` 标记和 `ApplyDeprecation` 调用，说明 API 有完善的迁移路径
- **1472 个源文件的大型项目**：说明功能覆盖面广，包含完整的测试套件

⚠️ **注意**：由于 PCG 是 UE5 的核心程序化工具，其 API 在主要版本间可能有较大变化。关注 `ApplyDeprecation` 方法和 `UE_DEPRECATED` 宏标注以跟踪 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/PCG)
- [官方文档](https://docs.unrealengine.com/latest/en-US/procedural-content-generation--framework-in-unreal-engine/)