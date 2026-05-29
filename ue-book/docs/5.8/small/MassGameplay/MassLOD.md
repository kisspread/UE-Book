# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 Epic 的大规模实体组件系统 (ECS) 框架 MassEntity 构建的**游戏逻辑层**。它提供了一套完整的架构和工具，用于处理成千上万甚至数百万个“智能体”（Agents）的游戏逻辑，如人群模拟、大量子弹、RTS 单位、动物群等。其核心解决的问题是如何在高性能下编写和管理大量实体的行为、感知、移动、表示和同步。

插件模块化地提供了从底层的 LOD 管理、运动控制，到高层的实体表示（Actor/ISM）、网络复制、智能对象交互以及 EQS 集成等完整的解决方案。

## 使用场景

- 你需要为一个 RTS 游戏创建数百个独立行动的士兵单位。
- 你在开发一个开放世界游戏，需要模拟数千个 NPC 的日常行为路径和视觉 LOD。
- 你的项目包含大量飞行的子弹、箭矢或粒子实体，需要高效的管理和清理。
- 你需要为大规模人群（如体育场馆观众）实现基于距离的视觉质量和更新频率优化。
- 你想利用 MassEntity 的 ECS 性能优势，同时使用 UE 的 Actor 系统与游戏逻辑交互。

## 蓝图用法

MassGameplay 的大部分逻辑运行在 Mass 处理器（Processor）和特质（Trait）中，蓝图接口相对高层。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterActorViewer` | 将一个 Actor 注册为 Mass LOD 系统的观察者，影响实体的 LOD 计算。 | `UMassLODSubsystem` |
| `UnregisterActorViewer` | 移除一个已注册的 Actor 观察者。 | `UMassLODSubsystem` |
| `GetViewers` | 获取当前所有已注册的 LOD 观察者信息数组。 | `UMassLODSubsystem` |

### 使用示例（蓝图描述）

1.  **配置实体 LOD**：
    *   在创建 Mass 实体模板时，为其添加 `MassSimulationLODTrait` 特质。
    *   在该特质的详情面板中，配置 `LODDistance` 数组，定义 High/Medium/Low/Off 各档位的距离阈值。
    *   可选启用 `bEnableVariableTicking`，并设置 `TickRates` 数组，控制不同 LOD 下实体的更新频率。

2.  **注册自定义观察者**：
    *   在游戏模式或角色蓝图中，获取 `UMassLODSubsystem` 子系统。
    *   调用 `RegisterActorViewer` 节点，将你的主要玩家角色或其他需要影响 LOD 计算的 Actor 传入。
    *   这会将该 Actor 的位置和朝向作为计算实体距离和可见性的基准点之一。

## C++ 用法

### 头文件引入

```cpp
#include "MassLODSubsystem.h"
#include "MassSimulationLOD.h"
#include "MassLODTrait.h"
```

### 基本用法

**注册观察者并查询信息 (来自 MassLODSubsystem.h)**

```cpp
// 获取世界并访问 LOD 子系统
UWorld* World = GetWorld();
if (UMassLODSubsystem* LODSubsystem = UWorld::GetSubsystem<UMassLODSubsystem>(World))
{
    // 注册当前 Pawn 作为观察者
    LODSubsystem->RegisterActorViewer(*GetPawn());

    // 查询当前所有观察者
    const TArray<FViewerInfo>& Viewers = LODSubsystem->GetViewers();
    UE_LOG(LogTemp, Log, TEXT("Current number of viewers: %d"), Viewers.Num());
    
    // 通过 Actor 查找观察者句柄
    FMassViewerHandle MyHandle = LODSubsystem->GetViewerHandleFromActor(*GetPawn());
    if (LODSubsystem->IsValidViewer(MyHandle))
    {
        // 处理有效的查看器...
    }
}
```

**配置模拟 LOD 参数 (来自 MassSimulationLOD.h)**

```cpp
// 在构建实体模板时配置LOD参数
FMassSimulationLODParameters LODParams;
LODParams.LODDistance[EMassLOD::High] = 0.0f;    // 最近，最高质量
LODParams.LODDistance[EMassLOD::Medium] = 5000.0f; // 5000单位距离
LODParams.LODDistance[EMassLOD::Low] = 10000.0f;   // 10000单位距离
LODParams.LODDistance[EMassLOD::Off] = 20000.0f;   // 20000单位距离后停止更新
LODParams.BufferHysteresisOnDistancePercentage = 10.0f; // 10% 的滞后缓冲
LODParams.LODMaxCount[EMassLOD::High] = 1000;      // 最多1000个实体保持最高LOD
LODParams.bSetLODTags = true; // 自动设置LOD标签

// 将参数应用到实体模板构建上下文中
FMassEntityTemplateBuildContext BuildContext;
BuildContext.AddConstSharedFragment<FMassSimulationLODParameters>(LODParams);
```

### 进阶用法

**使用 TMassLODCalculator 自定义 LOD 逻辑 (来自 MassLODCalculator.h)**

对于需要完全自定义 LOD 判定逻辑的场景（例如，不依赖距离而是基于游戏事件），可以继承并配置 `TMassLODCalculator`。

```cpp
// 自定义LOD逻辑结构体
struct FMyCustomLODLogic : public FLODDefaultLogic
{
    enum
    {
        bDoVisibilityLogic = true, // 启用可见性计算
        bCalculateLODSignificance = true, // 计算LOD显著性
        bLocalViewersOnly = true, // 仅考虑本地观察者
    };
};

// 在处理器或共享片段中使用
class UMyCustomLODProcessor : public UMassProcessor
{
    TMassLODCalculator<FMyCustomLODLogic> LODCalculator;

    void InitializeLOD()
    {
        // 初始化计算器，设定距离和最大数量限制
        float BaseDistances[EMassLOD::Max] = {0.0f, 1000.f, 5000.f, 20000.f};
        int32 MaxCounts[EMassLOD::Max] = {500, 2000, 5000, INT_MAX};
        LODCalculator.Initialize(BaseDistances, 0.1f, MaxCounts);
    }

    void CalculateLODForEntities(FMassExecutionContext& Context, 
                                 TConstArrayView<FMassViewerInfoFragment> ViewerInfoList,
                                 TArrayView<FMassLODFragment> LODList)
    {
        // 准备执行，传入当前观察者列表
        const UMassLODSubsystem* LODSubsystem = UWorld::GetSubsystem<UMassLODSubsystem>(Context.GetWorld());
        LODCalculator.PrepareExecution(LODSubsystem->GetSynchronizedViewers());
        
        // 计算当前区块实体的LOD
        LODCalculator.CalculateLOD<FMassViewerInfoFragment, FMassLODFragment>(Context, ViewerInfoList, LODList);
    }
};
```

## Demo 示例

一个最小的处理器示例，展示如何使用 MassLOD 子系统和计算为实体设置 LOD 标签。

### MyLODTagSetterProcessor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassLODTypes.h"
#include "MyLODTagSetterProcessor.generated.h"

USTRUCT()
struct FMassLODInfoFragment : public FMassFragment
{
    GENERATED_BODY()
    EMassLOD::Type CurrentLOD = EMassLOD::Max;
};

UCLASS()
class UMyLODTagSetterProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyLODTagSetterProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

### MyLODTagSetterProcessor.cpp

```cpp
#include "MyLODTagSetterProcessor.h"
#include "MassLODSubsystem.h"
#include "MassExecutionContext.h"

UMyLODTagSetterProcessor::UMyLODTagSetterProcessor()
{
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::Processor::Names::LODCollector);
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyLODTagSetterProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassLODInfoFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    // 注意：这里不直接查询LOD标签，而是通过逻辑设置
}

void UMyLODTagSetterProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    UWorld* World = Context.GetWorld();
    UMassLODSubsystem* LODSubsystem = World->GetSubsystem<UMassLODSubsystem>();

    if (!LODSubsystem)
    {
        return;
    }

    // 获取更新后的观察者列表
    const TArray<FViewerInfo>& Viewers = LODSubsystem->GetSynchronizedViewers();

    EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& QueryContext)
    {
        const TConstArrayView<FTransformFragment> TransformList = QueryContext.GetFragmentView<FTransformFragment>();
        const TConstArrayView<FMassLODInfoFragment> LODInfoList = QueryContext.GetFragmentView<FMassLODInfoFragment>();

        for (int32 EntityIndex = 0; EntityIndex < QueryContext.GetNumEntities(); ++EntityIndex)
        {
            const FMassLODInfoFragment& LODInfo = LODInfoList[EntityIndex];
            // 此示例中，我们假设LODInfo.CurrentLOD已经由其他处理器计算好。
            // 实际应用中，你需要集成TMassLODCollector和TMassLODCalculator。
            
            // 根据计算出的LOD设置相应的标签
            if (LODInfo.CurrentLOD != EMassLOD::Max)
            {
                // 使用命令缓冲区延迟添加/移除标签
                const UScriptStruct* TagToAdd = UE::MassLOD::GetLODTagFromLOD(LODInfo.CurrentLOD);
                if (TagToAdd)
                {
                    // 此处为伪代码，实际需要使用EntityBuilder或CommandBuffer
                    // QueryContext.Defer().AddTagToEntity(QueryContext.GetEntity(EntityIndex), TagToAdd);
                }
            }
        }
    });
}
```

## 模块依赖

MassGameplay 由多个模块组成，每个模块有自身的依赖。以下是使用者最可能直接接触的模块的关键依赖（已省略 Core/Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心 ECS 框架，所有功能的基石。 |
| `MassSpawner` | 提供实体模板和大规模实体生成的功能。 |
| `MassRepresentation` | 负责将 Mass 实体可视化为 Actor、ISM 实例或其他形式。 |
| `MassCommon` | 提供通用的片段、标签和工具函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤销了之前对MassAgent组件的改动。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [表示模块] 在关闭ISM实例前等待Actor准备就绪，修复切换问题。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在大规模人群中对非傀儡Actor的处理。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [表示模块] 修复了LOD计算器中“按观察者计算”路径的一系列既有Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [表示模块] 重构代码，使用新接口替代手动计算的属性。 |

### 维护评价

MassGameplay 是一个**活跃维护**中的核心 gameplay 插件。

- **创建时间**：约4年前，属于较新的系统。
- **更新频率**：最近一周内有多次实质性更新，专注于 bug 修复和功能完善（如表示模块、LOD 计算、人群处理）。
- **维护状态**：**活跃维护中**。Epic Games 持续投入开发，修复复杂边界情况，优化性能。
- **已知限制**：作为实验性插件，其 API 可能仍会变动。大规模使用的性能调优需要深入理解 ECS 模式。
- **推荐使用**：**强烈推荐**用于需要处理大量同质实体的项目。虽然学习曲线较陡，但它是 UE 官方处理大规模实体模拟的**标准且高性能方案**。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （当前无特定文档，参考 MassEntity 和 Gameplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)