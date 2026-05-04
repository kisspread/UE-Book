# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

---

# MassLOD 模块文档

> MassLOD 是 MassGameplay 插件的核心子模块，为大规模实体（Mass Entity）提供基于距离和可见性的 LOD（Level of Detail）管理系统。

## 用途

MassLOD 解决的是大规模实体模拟中的性能优化问题。当你有成千上万个实体（如 NPC、粒子、装饰物）同时存在于场景中时，不可能对所有实体都进行完整的逻辑更新和渲染。MassLOD 通过以下机制解决这个问题：

1. **基于距离的 LOD 分级**：根据实体与观察者（玩家/摄像机）的距离，将实体分为 High、Medium、Low、Off 四个 LOD 等级
2. **视锥体剔除**：判断实体是否在摄像机视野内，结合距离进行更精细的 LOD 控制
3. **可变 Tick 频率**：低 LOD 等级的实体可以降低更新频率，节省 CPU 开销
4. **最大数量限制**：每个 LOD 等级可以设置最大实体数量，防止性能瓶颈
5. **多观察者支持**：支持多个玩家/摄像机同时影响 LOD 计算

## 使用场景

- 你在做一个开放世界游戏，场景中有大量 NPC → 用 MassLOD 控制 NPC 的更新频率
- 你需要实现大规模战斗场景（如 RTS 游戏）→ 用 MassLOD 根据距离降低远处单位的更新频率
- 你有一个包含大量装饰性实体的场景 → 用 MassLOD 将远处实体设为 Off LOD 完全跳过更新
- 你需要在多人游戏中对不同玩家分别计算 LOD → MassLOD 支持多观察者系统

## 蓝图用法

MassLOD 模块主要通过 Entity Trait 和配置参数在蓝图中使用，而非直接暴露 BlueprintCallable 函数。

### 核心 Trait

| Trait | 说明 | 用途 |
|---|---|---|
| `UMassLODCollectorTrait` | LOD 收集器 Trait | 为实体添加完整的 LOD 收集能力（含视锥体可见性判断） |
| `UMassDistanceLODCollectorTrait` | 距离 LOD 收集器 Trait | 仅基于距离的简化版 LOD 收集（无视锥体判断） |
| `UMassSimulationLODTrait` | 模拟 LOD Trait | 为实体添加模拟级别的 LOD 参数配置 |

### 配置参数

**FMassSimulationLODParameters**（通过 `UMassSimulationLODTrait` 配置）：

| 参数 | 类型 | 说明 |
|---|---|---|
| `LODDistance[4]` | float 数组 | 每个 LOD 等级的距离阈值（High/Medium/Low/Off） |
| `BufferHysteresisOnDistancePercentage` | float | 距离滞回百分比，防止 LOD 频繁切换（默认 10%） |
| `LODMaxCount[4]` | int32 数组 | 每个 LOD 等级的最大实体数量限制 |

### 使用示例（蓝图描述）

1. **创建 Mass Entity 模板**：
   - 在 Mass Entity 配置资产中，添加 `LODCollector` Trait
   - 添加 `SimulationLOD` Trait 并配置距离参数

2. **配置 LOD 距离**：
   - 设置 High LOD 距离为 1000（近距离，高细节）
   - 设置 Medium LOD 距离为 3000（中距离）
   - 设置 Low LOD 距离为 8000（远距离，低细节）
   - 设置 Off LOD 距离为 15000（超远距离，完全跳过）

3. **配置可变 Tick**：
   - 在 `UMassSimulationLODTrait` 中启用 `bEnableVariableTicking`
   - 配置 `VariableTickParams` 设置不同 LOD 的 Tick 频率

## C++ 用法

### 头文件引入

```cpp
#include "MassLODSubsystem.h"
#include "MassSimulationLOD.h"
#include "MassLODCollector.h"
#include "MassLODCalculator.h"
#include "MassLODTickRateController.h"
#include "MassLODFragments.h"
```

### 基本用法

**获取 LOD 子系统并管理观察者**：

```cpp
// 来源: MassLODSubsystem.h
// 获取 LOD 子系统
UMassLODSubsystem* LODSubsystem = GetWorld()->GetSubsystem<UMassLODSubsystem>();

// 获取所有同步后的观察者信息
const TArray<FViewerInfo>& Viewers = LODSubsystem->GetSynchronizedViewers();

// 从 Actor 获取观察者句柄
FMassViewerHandle Handle = LODSubsystem->GetViewerHandleFromActor(*MyActor);

// 检查观察者是否有效
if (LODSubsystem->IsValidViewer(Handle))
{
    // 获取观察者索引
    int32 ViewerIdx = LODSubsystem->GetValidViewerIdx(Handle);
}
```

**在 Processor 中使用 LOD 信息**：

```cpp
// 来源: MassLODUtils.h
// 在 Processor 的 Execute 中获取当前 Chunk 的 LOD 等级
EMassLOD::Type CurrentLOD = UE::MassLOD::GetLODFromArchetype(Context);

// 检查特定 LOD Tag 是否设置
bool bIsHighLOD = UE::MassLOD::IsLODTagSet(Context, EMassLOD::High);

// 根据 LOD 等级获取对应的 Tag 类型
const UScriptStruct* LODTag = UE::MassLOD::GetLODTagFromLOD(EMassLOD::Medium);
```

**使用可变 Tick Chunk Fragment**：

```cpp
// 来源: MassSimulationLOD.h
// 检查 Chunk 是否应该在本帧 Tick
bool bShouldTick = FMassSimulationVariableTickChunkFragment::ShouldTickChunkThisFrame(Context);

// 获取 Chunk 的 LOD 等级
EMassLOD::Type ChunkLOD = FMassSimulationVariableTickChunkFragment::GetChunkLOD(Context);

// 检查 Chunk 是否在本帧被处理（用于 LOD 收集器的 Chunk 过滤）
bool bHandled = FMassSimulationVariableTickChunkFragment::IsChunkHandledThisFrame(Context);
```

### 进阶用法

**自定义 LOD 逻辑**：

```cpp
// 来源: MassLODLogic.h
// 定义自定义 LOD 逻辑 Trait
struct FMyCustomLODLogic : public FLODDefaultLogic
{
    enum
    {
        bStoreInfoPerViewer = true,        // 存储每个观察者的信息
        bCalculateLODPerViewer = true,     // 为每个观察者计算独立的 LOD
        bDoVisibilityLogic = true,         // 启用视锥体可见性判断
        bCalculateLODSignificance = true,  // 计算 LOD 重要性值
        bLocalViewersOnly = true,          // 仅使用本地观察者
    };
};
```

**自定义 LOD 收集器和计算器**：

```cpp
// 来源: MassLODCollector.h, MassLODCalculator.h
// 创建自定义 LOD 收集器
TMassLODCollector<FMyCustomLODLogic> MyCollector;

// 初始化计算器
float BaseLODDistance[EMassLOD::Max] = { 1000.0f, 3000.0f, 8000.0f, 15000.0f };
float Hysteresis = 0.1f;
int32 LODMaxCount[EMassLOD::Max] = { 100, 500, 2000, INT_MAX };

TMassLODCalculator<FMyCustomLODLogic> MyCalculator;
MyCalculator.Initialize(BaseLODDistance, Hysteresis, LODMaxCount);

// 每帧准备执行
MyCalculator.PrepareExecution(Viewers);

// 在 Chunk 执行中计算 LOD
MyCalculator.CalculateLOD<FViewerInfoFragment, FMassSimulationLODFragment>(
    Context, ViewersInfoList, LODList);
```

**使用 Tick Rate 控制器**：

```cpp
// 来源: MassLODTickRateController.h
TMassLODTickRateController<FMassSimulationVariableTickChunkFragment> TickRateController;

// 初始化 Tick 频率（每个 LOD 等级的 Tick 间隔秒数）
float TickRates[EMassLOD::Max] = { 0.0f, 0.1f, 0.5f, 1.0f }; // High 每帧，Off 每秒
TickRateController.Initialize(TickRates, /*bShouldSpreadFirstUpdate=*/true);

// 检查是否需要为当前 Chunk 计算 LOD
if (TickRateController.ShouldCalculateLODForChunk(Context))
{
    // 执行 LOD 计算
}

// 更新 Tick 频率并检查是否应该 Tick
bool bShouldTick = TickRateController.UpdateTickRateFromLOD<FMassSimulationLODFragment, FMassSimulationVariableTickFragment>(
    Context, LODList, TickRateList, CurrentTime);
```

## Demo 示例

### 自定义 LOD Processor

```cpp
// MyLODProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassLODCollector.h"
#include "MassLODCalculator.h"
#include "MassSimulationLOD.h"
#include "MassLODFragments.h"
#include "MyLODProcessor.generated.h"

UCLASS()
class UMyLODProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyLODProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    TMassLODCollector<FMassRepresentationLODLogic> Collector;
    TMassLODCalculator<FMassRepresentationLODLogic> Calculator;

    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyLODProcessor.cpp
#include "MyLODProcessor.h"
#include "MassLODSubsystem.h"
#include "MassExecutionContext.h"

UMyLODProcessor::UMyLODProcessor()
{
    // 配置为在 LOD 处理阶段执行
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::LOD);
}

void UMyLODProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询：需要 Transform、ViewerInfo 和 SimulationLOD Fragment
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassViewerInfoFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassSimulationLODFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddChunkRequirement<FMassSimulationVariableTickChunkFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.SetChunkFilter(&FMassSimulationVariableTickChunkFragment::ShouldTickChunkThisFrame);
}

void UMyLODProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 获取 LOD 子系统和观察者信息
    UWorld* World = EntityManager.GetWorld();
    UMassLODSubsystem* LODSubsystem = World->GetSubsystem<UMassLODSubsystem>();
    const TArray<FViewerInfo>& Viewers = LODSubsystem->GetSynchronizedViewers();

    // 准备收集器和计算器
    Collector.PrepareExecution(Viewers);
    Calculator.PrepareExecution(Viewers);

    // 处理每个 Chunk
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        // 收集 LOD 信息
        Collector.CollectLODInfo<FTransformFragment, FMassViewerInfoFragment>(
            Context,
            Context.GetFragmentView<FTransformFragment>(),
            Context.GetMutableFragmentView<FMassViewerInfoFragment>());

        // 计算 LOD
        Calculator.CalculateLOD<FMassViewerInfoFragment, FMassSimulationLODFragment>(
            Context,
            Context.GetFragmentView<FMassViewerInfoFragment>(),
            Context.GetMutableFragmentView<FMassSimulationLODFragment>());
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass Entity 核心框架（MassGameplay 的基础依赖） |
| `MassRepresentation` | 实体可视化表示（LOD 与渲染关联） |
| `MassCommon` | Mass 通用类型和工具 |

## 维护状态

### 近期更新

```
- 8cded7886207 [Mass] removed code deprecated in 5.4
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- cd3c2a716daa Replace some usages of FORCEINLINE with inline in Mass modules.
```

### 维护评价

MassLOD 模块作为 MassGameplay 插件的核心组件，处于**活跃维护**状态：

- **创建时间**：2021 年 9 月，约 4 年历史
- **维护频率**：近期有代码清理和优化更新（移除废弃代码、优化内联函数）
- **实验性状态**：标记为 `IsExperimentalVersion = true`，API 可能在未来版本中发生变化
- **启用状态**：默认未启用（`EnabledByDefault = false`），需要手动在项目设置中启用
- **推荐使用**：适合需要大规模实体模拟的项目，但需注意这是实验性功能，建议在生产环境中谨慎使用并做好版本升级准备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassLOD)
- [MassEntity 文档](https://docs.unrealengine.com/5.7/en-US/mass-entity-in-unreal-engine/)（Mass Entity 框架文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)