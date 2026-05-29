# MassLOD

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 实体LOD系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassLOD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassLOD) | |

## 用途
MassLOD模块是MassEntity框架中专门为大规模实体（如成千上万的NPC、车辆或物体）设计的LOD（Level of Detail）管理系统。它解决的核心问题是：如何高效地根据玩家（查看者）的位置和视线，为海量动态实体计算并分配不同的LOD级别，从而在保证视觉质量的同时，极大地优化游戏性能。
与传统单个Actor的LOD系统不同，MassLOD基于MassEntity的ECS（Entity Component System）架构，能够对实体进行分块（Chunk）处理，实现超高性能的LOD计算、可见性剔除和变量节拍（Variable Tick Rate）控制。

## 使用场景
- **开放世界游戏**：管理场景中成百上千的NPC、动物或载具的LOD，确保近距离角色高精度，远距离角色简化。
- **大规模群体模拟**：如战场上的士兵、城市街道上的行人，需要根据玩家视野动态调整其模拟频率和渲染细节。
- **动态物体管理**：对于拾取物、弹药箱等大量可交互物体，根据玩家距离决定其更新频率和视觉表现。

## 蓝图用法
MassLOD模块主要通过 `UMassLODSubsystem` 子系统提供蓝图接口，用于管理LOD计算的“查看者”（Viewer）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Viewer Handle From Actor` | 从一个Actor（如PlayerController）获取其对应的查看者句柄。 | `UMassLODSubsystem` |
| `Is Valid Viewer` | 检查一个查看者句柄是否有效。 | `UMassLODSubsystem` |
| `Get Viewers` | 获取当前所有查看者信息的数组。 | `UMassLODSubsystem` |
| `Register Actor Viewer` | 将一个Actor手动注册为LOD系统的查看者。 | `UMassLODSubsystem` |
| `Unregister Actor Viewer` | 将一个已注册的Actor查看者注销。 | `UMassLODSubsystem` |

### 使用示例（蓝图描述）
1. **获取LOD子系统**：在任何需要与LOD系统交互的Actor蓝图中，使用 `Get Game Instance Subsystem` 节点，选择 `UMassLODSubsystem` 类，获取子系统实例。
2. **注册自定义查看者**：假设你有一个自定义的监视摄像头Actor，你可以调用 `Register Actor Viewer` 节点，并将该摄像头Actor作为参数传入，使其成为LOD系统的查看者之一。
3. **查询查看者信息**：通过 `Get Viewers` 节点，可以获取所有当前活跃的查看者位置、旋转等信息，用于其他游戏逻辑。

## C++ 用法
MassLOD的核心逻辑通过C++模板类实现，与MassEntity处理器（Processor）紧密集成。

### 头文件引入
```cpp
#include "MassLODSubsystem.h"
#include "MassLODCalculator.h"
#include "MassLODCollector.h"
#include "MassSimulationLOD.h"
```

### 基本用法
以下是一个典型的使用 `TMassLODCalculator` 计算LOD的流程。该代码通常位于一个自定义的 `UMassProcessor` 的 `Execute` 函数中。
*(来源：`TMassLODCalculator::CalculateLOD` 及 `UMassSimulationLODProcessor::Execute` 逻辑)*
```cpp
// 在处理器的成员中定义LOD计算器和收集器
TMassLODCalculator<FMassSimulationLODLogic> LODCalculator;
TMassLODCollector<FMassSimulationLODLogic> LODCollector;

// 1. 初始化（通常在处理器创建时完成，或从SharedFragment获取参数）
float BaseLODDistance[EMassLOD::Max] = {0.0f, 5000.0f, 15000.0f, 50000.0f};
int32 LODMaxCount[EMassLOD::Max] = {100, 500, 1000, INT_MAX};
LODCalculator.Initialize(BaseLODDistance, 0.1f, LODMaxCount);

// 2. 在每一帧处理器执行前准备
// 获取所有查看者信息（从UMassLODSubsystem）
const TArray<FViewerInfo>& Viewers = UMassLODSubsystem::Get(GetWorld())->GetSynchronizedViewers();
LODCalculator.PrepareExecution(Viewers);
LODCollector.PrepareExecution(Viewers);

// 3. 为每个实体块（Chunk）收集LOD信息
// 通过查询遍历所有带有 Transform 和 ViewerInfoFragment 的实体
ForChunkInView([&](FMassExecutionContext& Context)
{
    TConstArrayView<FTransformFragment> Transforms = Context.GetFragmentView<FTransformFragment>();
    TArrayView<FMassViewerInfoFragment> ViewerInfos = Context.GetMutableFragmentView<FMassViewerInfoFragment>();
    LODCollector.CollectLODInfo(Context, Transforms, ViewerInfos);
});

// 4. 为每个实体块计算LOD
ForChunkInView([&](FMassExecutionContext& Context)
{
    TConstArrayView<FMassViewerInfoFragment> ViewerInfos = Context.GetFragmentView<FMassViewerInfoFragment>();
    TArrayView<FMassSimulationLODFragment> LODFragments = Context.GetMutableFragmentView<FMassSimulationLODFragment>();
    LODCalculator.CalculateLOD(Context, ViewerInfos, LODFragments);
});
```

### 进阶用法
结合变量节拍（Variable Tick Rate）来根据LOD降低更新频率。
*(来源：`TMassLODTickRateController` 及 `UMassSimulationLODProcessor`)*
```cpp
// 在SharedFragment中通常包含LOD计算器和节拍控制器
// FMassSimulationLODSharedFragment, FMassSimulationVariableTickSharedFragment

// 在处理器执行中，首先更新LOD，然后更新节拍
void UMyLODProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // ... 计算LOD ...

    // 更新变量节拍
    ForChunkInView([&](FMassExecutionContext& Context)
    {
        if (FMassSimulationVariableTickSharedFragment* TickShared = Context.GetSharedFragmentPtr<FMassSimulationVariableTickSharedFragment>())
        {
            TConstArrayView<FMassSimulationLODFragment> LODList = Context.GetFragmentView<FMassSimulationLODFragment>();
            TArrayView<FMassSimulationVariableTickFragment> TickRateList = Context.GetMutableFragmentView<FMassSimulationVariableTickFragment>();
            // 根据当前LOD更新实体是否需要在本帧更新
            TickShared->LODTickRateController.UpdateTickRateFromLOD(Context, LODList, TickRateList, Context.GetWorld()->GetTimeSeconds());
        }
    });
}
```

## Demo 示例
以下是一个最小化的Mass处理器示例，演示如何集成MassLOD系统。
*(注：需要已配置好MassEntity和MassLOD插件的项目环境)*

```cpp
// MyLODTestProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MassSimulationLOD.h" // 引入LOD相关Fragment和类型
#include "MassLODCalculator.h"
#include "MassLODCollector.h"

class UMyLODTestProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyLODTestProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
    // 这里直接使用SimulationLOD的逻辑，实际项目中可能从SharedFragment获取
    TMassLODCollector<FMassSimulationLODLogic> Collector;
    TMassLODCalculator<FMassSimulationLODLogic> Calculator;
};
```

```cpp
// MyLODTestProcessor.cpp
#include "MyLODTestProcessor.h"
#include "MassCommonFragments.h" // FTransformFragment
#include "MassLODFragments.h"    // FMassViewerInfoFragment

UMyLODTestProcessor::UMyLODTestProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
    ExecutionOrder.ExecuteAfter.Add(TEXT("MassLODCollectorProcessor")); // 确保在收集器之后执行
}

void UMyLODTestProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassViewerInfoFragment>(EMassFragmentAccess::ReadWrite); // 收集器会写入
    EntityQuery.AddRequirement<FMassSimulationLODFragment>(EMassFragmentAccess::ReadWrite); // 计算器会写入
    EntityQuery.AddSharedRequirement<FMassSimulationLODSharedFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyLODTestProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 1. 准备查看者信息
    UWorld* World = GetWorld();
    UMassLODSubsystem* LODSubsystem = UMassLODSubsystem::Get(World);
    if (!LODSubsystem) return;

    const TArray<FViewerInfo>& Viewers = LODSubsystem->GetSynchronizedViewers();
    Collector.PrepareExecution(Viewers);
    Calculator.PrepareExecution(Viewers);

    // 2. 遍历所有匹配的实体块
    EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& ChunkContext)
    {
        // 获取当前块的SharedFragment，其中包含了初始化的计算器
        FMassSimulationLODSharedFragment& LODShared = ChunkContext.GetMutableSharedFragment<FMassSimulationLODSharedFragment>();

        // 执行收集（计算距离等）
        TConstArrayView<FTransformFragment> Transforms = ChunkContext.GetFragmentView<FTransformFragment>();
        TArrayView<FMassViewerInfoFragment> ViewerInfos = ChunkContext.GetMutableFragmentView<FMassViewerInfoFragment>();
        LODShared.LODCalculator.CollectLODInfo(ChunkContext, Transforms, ViewerInfos); // 注意：这里使用了SharedFragment中的Calculator，而不是类成员

        // 执行LOD计算
        TArrayView<FMassSimulationLODFragment> LODFragments = ChunkContext.GetMutableFragmentView<FMassSimulationLODFragment>();
        LODShared.LODCalculator.CalculateLOD(ChunkContext, ViewerInfos, LODFragments);
    });
}
```

## 模块依赖
| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心ECS框架，提供实体、块、Fragment等基础概念。 |
| `MassGameplayCommon` | MassGameplay插件的通用模块，可能包含基础Fragment和类型。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回退了之前对MassAgentComponent的修改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了关闭ISM（实例化静态网格体）前的Actor就绪状态检查问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 `TMassLODCalculator` 中基于每个查看者计算LOD路径的一系列预先存在的Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两处手动计算的 `bDoKeepActorExtraFrame` 切换为使用新的UE::M函数，可能是代码规范化。 |
| 2026-05-11 | `b6284f2d` | [MassSpawner] Add actor spawning support to Mass Spawner | 为Mass Spawner添加了Actor生成支持，间接影响LOD系统管理的对象范围。 |

### 维护评价
- **年龄与状态**：该模块创建于2021年9月，是一个相对较新的模块，且从最近（2026年5月）的提交记录看，仍在进行活跃的**Bug修复和优化**。
- **实验性**：`.uplugin` 文件明确标记 `IsExperimentalVersion: true`，这意味着它**尚未稳定**，API和功能在未来版本中可能发生重大变化。
- **更新频率**：近期有连续的提交，主要集中在修复MassRepresentation子系统相关的Bug，说明核心开发者仍在维护，但重点似乎更倾向于集成和优化，而非新增大功能。
- **推荐度**：**适合用于学习和原型验证**，尤其适合研究MassEntity架构下的大规模模拟。但**不推荐用于对稳定性要求极高的生产项目**。应密切关注引擎大版本更新时的变更日志，因为实验性模块可能会被重构或合并。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassLOD)
- 官方文档：暂无
- [相关测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) (MassGameplayTestSuite模块中可能包含相关测试)