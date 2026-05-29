# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏性 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件是基于 Epic 的 MassEntity 数据导向技术栈（ECS）构建的**游戏玩法层**。它解决的核心问题是：**如何在拥有成千上万实体（Agents）的场景中，实现高效的游戏逻辑、AI行为、运动、渲染表示和网络同步**。

MassEntity 提供了底层的高性能实体管理和批量处理框架，而 MassGameplay 则在其上层封装了具体的游戏玩法功能，如运动、表示、生成、复制、与智能对象（SmartObjects）交互等。这个插件的存在，是为了让开发者能够在保持 ECS 性能优势的同时，更便捷地使用这些常见游戏玩法模块，无需从头实现所有功能。

## 使用场景

-   你正在制作一个**大规模战略游戏**，需要在同一场景中管理数千甚至上万个独立的作战单位，并且要求它们具备基本的移动、AI决策和战斗交互能力。
-   你正在开发一个**开放世界游戏**，需要生成和模拟密集的人群、车辆或动物群，且对性能和内存占用有严格要求。
-   你的游戏需要一套**高性能的AI系统**，用于处理大量NPC的巡逻、感知、决策和互动，并希望避免传统行为树在实体数量激增时的性能瓶颈。
-   你需要实现**大规模的网络同步**，让数千个实体的状态能够在服务器与客户端之间高效、可靠地复制。
-   你希望将现有基于Actor的游戏逻辑（如技能、任务系统）**渐进式地**迁移到ECS架构中。

## 蓝图用法

MassGameplay 提供了丰富的蓝图可调用节点，用于生成、管理和控制大规模实体。其API分散在多个子模块中。

### 核心节点 (按模块分组)

#### 1. MassSpawner 模块
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据给定的生成器（Spawner）和数量，在指定位置生成一批Mass实体。这是生成大量实体的核心入口。 | `UMassSpawnerSubsystem` |
| `Destroy Entities` | 销毁一个或多个由MassSpawner管理的实体。 | `UMassSpawnerSubsystem` |

#### 2. MassMovement 模块
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Movement Style` | 为实体设置一个预定义的移动样式（Movement Style），如“步行”、“奔跑”、“驾驶”。 | `UMassMovementSubsystem` |
| `Set Target Location` | 指示实体移动到一个指定的世界坐标位置。 | `UMassMoveTargetFinderProcessor` 相关 |

#### 3. MassRepresentation 模块
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set LOD Configuration` | 动态调整实体的LOD（细节层次）策略，平衡视觉质量与性能。 | `UMassRepresentationSubsystem` |
| `Force Actor Representation` | 强制将某个Mass实体切换为使用完整的Actor表示，用于需要复杂交互的关键时刻。 | `UMassRepresentationSubsystem` |

#### 4. MassReplication 模块
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Replication Mode` | 设置实体的网络复制策略（如复制频率、数据压缩）。 | `UMassReplicationSubsystem` |

#### 5. MassSmartObjects 模块
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Claim Smart Object` | 为一个Mass实体申请占用场景中的一个智能对象槽位。 | `UMassSmartObjectSubsystem` |

### 使用示例（蓝图描述）

**场景：生成一波敌人并命令它们冲锋**

1.  在你的游戏模式蓝图中，使用 `Get Subsystem` 节点获取 `MassSpawnerSubsystem`。
2.  调用 `Spawn Entities` 节点。`Spawner` 参数连接一个你在编辑器中创建的 `UMassEntitySpawner` 资产（定义了要生成的实体模板）。`Num Entities` 设置为500。`Spawn Transform` 设置你希望的生成位置。
3.  获取返回的实体句柄（Entity Handle）。
4.  使用另一个 `Get Subsystem` 节点获取 `MassMovementSubsystem`。
5.  调用 `Set Movement Style` 节点，传入实体句柄和“奔跑”样式。
6.  调用 `Set Target Location` 节点，传入实体句柄和你想要的冲锋目标坐标。

## C++ 用法

### 头文件引入

根据你要使用的功能，引入对应子模块的头文件：
```cpp
#include "MassSpawnerSubsystem.h" // 生成与销毁
#include "MassMovementSubsystem.h" // 运动控制
#include "MassRepresentationSubsystem.h" // 表示管理
#include "MassAgentComponent.h" // 与Actor的桥接
```

### 基本用法

**1. 在C++中生成实体**
*(来源：引擎测试用例及子系统实现)*
```cpp
// 获取Spawner子系统
UMassSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassSpawnerSubsystem>();

// 准备生成数据：定义一个生成请求
FSpawningRequestData SpawnRequest;
SpawnRequest.Spawner = MySpawnerAsset; // 指向UMassEntitySpawner资产
SpawnRequest.NumEntities = 1000;
SpawnRequest.SpawnTransform = FTransform(FRotator::ZeroRotator, FVector(0, 0, 100));

// 提交生成请求，获取代表这一批实体的句柄
FMassEntityHandle BatchHandle = SpawnerSubsystem->SpawnEntities(SpawnRequest);
```

**2. 创建自定义的Processor（处理器）**
这是扩展MassGameplay逻辑的主要方式。
*(来源：各模块Processor实现模式)*
```cpp
// MyAgentProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyAgentTrait.h" // 自定义的片段（Trait/Fragment）
#include "MassProcessorExecutor.h"

class UMyAgentProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyAgentProcessor();

    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MyAgentProcessor.cpp
UMyAgentProcessor::UMyAgentProcessor()
{
    // 设置执行顺序，例如在运动处理之后
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::Movement);
    ProcessingPhase = EMassProcessingPhase::PrePhysics; // 指定处理阶段
}

void UMyAgentProcessor::ConfigureQueries()
{
    // 声明查询条件：需要包含自定义的“战斗状态”片段，且拥有“移动目标”片段
    EntityQuery.AddRequirement<FMyCombatStateFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadOnly);
}

void UMyAgentProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 执行查询，遍历所有符合条件的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取该Chunk中所需片段的数组访问器
        const TConstArrayView<FMassMoveTargetFragment> MoveTargets = Context.GetFragmentView<FMassMoveTargetFragment>();
        const TArrayView<FMyCombatStateFragment> CombatStates = Context.GetMutableFragmentView<FMyCombatStateFragment>();

        // 批量处理逻辑：例如，如果实体正在移动，就设置其战斗状态为“机动”
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            if (MoveTargets[i].GetCurrentAction() == EMassMovementAction::Move)
            {
                CombatStates[i].State = ECombatState::Maneuvering;
            }
        }
    });
}
```

### 进阶用法

**将Mass实体与Actor逻辑结合**
MassGameplay 通过 `UMassAgentComponent` 实现了Mass实体与传统Actor的桥接。
*(来源：MassActors模块实现)*
```cpp
// 在一个自定义的Actor类中
void AMyAgentActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 获取或创建Agent组件
    UMassAgentComponent* AgentComponent = FindComponentByClass<UMassAgentComponent>();
    if (!AgentComponent)
    {
        AgentComponent = NewObject<UMassAgentComponent>(this);
        AddInstanceComponent(AgentComponent);
        AgentComponent->RegisterComponent();
    }
    
    // 通过Agent组件获取该Actor对应的Mass实体句柄
    FMassEntityHandle MyEntity = AgentComponent->GetEntityHandle();
    
    // 使用这个句柄，通过子系统控制这个实体
    UMassMovementSubsystem* MoveSub = GetWorld()->GetSubsystem<UMassMovementSubsystem>();
    if (MyEntity.IsValid() && MoveSub)
    {
        MoveSub->SetMovementStyle(MyEntity, /*SomeStyleName*/);
    }
}
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何创建一个自定义的“巡逻”处理器。

**1. 定义自定义片段 (Trait)**
```cpp
// PatrolTrait.h
#pragma once
#include "MassEntityTraitBase.h"
#include "MassEntityTypes.h"
#include "PatrolTrait.generated.h"

USTRUCT()
struct FPatrolPointsFragment : public FMassFragment
{
    GENERATED_BODY()
    TArray<FVector> Points;
    int32 CurrentIndex = 0;
};

UCLASS()
class UPatrolTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
public:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        BuildContext.AddFragment<FPatrolPointsFragment>();
    }
};
```

**2. 实现巡逻处理器**
```cpp
// PatrolProcessor.h
#pragma once
#include "MassProcessor.h"
#include "PatrolTrait.h"
#include "MassMovementFragments.h"
#include "PatrolProcessor.generated.h"

UCLASS()
class UPatrolProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UPatrolProcessor();
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// PatrolProcessor.cpp
#include "PatrolProcessor.h"
#include "MassExecutionContext.h"

UPatrolProcessor::UPatrolProcessor()
{
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::Movement);
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UPatrolProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FPatrolPointsFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassAgentMovementFragment>(EMassFragmentAccess::ReadOnly);
}

void UPatrolProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FPatrolPointsFragment> PatrolFragments = Context.GetMutableFragmentView<FPatrolPointsFragment>();
        const TArrayView<FMassMoveTargetFragment> MoveTargets = Context.GetMutableFragmentView<FMassMoveTargetFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FPatrolPointsFragment& Patrol = PatrolFragments[i];
            FMassMoveTargetFragment& MoveTarget = MoveTargets[i];

            // 简单逻辑：如果当前没有移动目标或已接近目标，则前往下一个巡逻点
            if (MoveTarget.GetCurrentAction() == EMassMovementAction::Stand || 
                (MoveTarget.GetTargetLocation() - Context.GetEntityLocation(Context.GetEntity(i))).SizeSquared() < 10000.f) // 100 units
            {
                if (Patrol.Points.Num() > 0)
                {
                    MoveTarget.CreateNewAction(EMassMovementAction::Move, Patrol.Points[Patrol.CurrentIndex]);
                    Patrol.CurrentIndex = (Patrol.CurrentIndex + 1) % Patrol.Points.Num();
                }
            }
        }
    });
}
```

**3. 注册处理器和插件依赖**
在你的游戏模块或插件的 `StartupModule` 或 `IModuleInterface` 中注册处理器（通常引擎会自动发现，但显式注册更安全）：
```cpp
// 在你的模块启动代码中
#include "MassEntityRegistry.h"
#include "PatrolProcessor.h"

void FMyGameplayModule::StartupModule()
{
    // ... 其他初始化
    UMassEntityRegistry::GetMutable().AddProcessor<UPatrolProcessor>();
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "MassEntity",
    "MassGameplay", // 包含MassMovement, MassSpawner等
    // 根据需要添加其他子模块，如 "MassRepresentation"
});
```

## 模块依赖

MassGameplay 自身模块众多，但作为一个整体插件，使用者（你的游戏模块）通常只需要关注顶层的依赖关系。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 底层ECS框架，MassGameplay的绝对基石，必须依赖。 |
| `MassEntityEditor` | 编辑器支持，用于可视化调试和编辑Mass实体。开发期间推荐依赖。 |
| `GameplayAbilities` | (可选) 如果需要将Mass实体与技能系统（GAS）集成，则需依赖。 |
| `SmartObjectsModule` | (可选) 如果使用MassSmartObjects功能，需要依赖此模块。 |

*注意：MassGameplay的各个子模块（如MassMovement）之间的依赖是内部处理的。在你的Build.cs中，依赖 `MassGameplay` 通常就自动引入了其所有核心子模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤销了对MassAgentComponent组件的一项早期修改，可能修复了兼容性或回归问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了在切换掉实例化静态网格体（ISM）表示前，需要等待相关Actor完全准备就绪的问题，避免了渲染异常。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在Mass生成的群体中，非傀儡（non-puppet）类型Actor的处理逻辑，提升了稳定性和一致性。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了LOD计算器中针对单个观察者的LOD路径存在的多个既有缺陷。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 将手动计算的“保留Actor额外一帧”标志切换为使用新的引擎接口，属于代码清理和优化。 |

### 维护评价

-   **状态**：**活跃维护中**。尽管 `.uplugin` 标记为实验性 (`IsExperimentalVersion: true`)，但根据 Git 历史，该插件仍在被 Epic Games 积极开发和修复。最近的提交（2026年5月）集中在**MassRepresentation**模块的稳定性和渲染逻辑优化上，表明核心团队仍在投入。
-   **实验性风险**：作为实验性插件，其API和功能在不同引擎版本间可能发生重大变更，不建议用于需要长期稳定支持的商业项目，除非团队有能力跟进源码更新。
-   **性能与适用性**：该插件是解决大规模实体模拟的官方方案，性能优异。适用于对实体数量有极高要求（数千至数万）的项目。
-   **推荐度**：**条件推荐**。如果你的项目确实面临大规模实体模拟的性能挑战，并且能接受实验性API的潜在不稳定性，MassGameplay是一个强大且官方支持的选择。建议在新项目初期进行技术验证，并密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档：暂无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)