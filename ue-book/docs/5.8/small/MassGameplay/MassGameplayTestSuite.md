# MassGameplay

> 基于MassEntity的大规模智能体仿真实现（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、调试可视化） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

`MassGameplay` 是 Unreal Engine 中用于高效模拟和管理大规模实体（如人群、NPC 群体、可交互物体集合）的游戏玩法插件。它建立在 `MassEntity`（ECS 架构）之上，解决了传统 Actor 模型在成千上万个实例同时活动时性能瓶颈的问题。该插件提供了将游戏逻辑（如移动、表示、状态同步）以数据驱动的方式附加到轻量级实体上的能力，从而实现高效的大规模世界模拟。其主要存在意义是为开放世界、实时策略（RTS）等需要处理大量动态对象的游戏类型提供底层基础设施。

## 使用场景

-   **开放世界或 RTS 游戏**：你需要同时模拟成千上万的 NPC、单位或动态物体，并保持高性能。
-   **人群模拟**：你需要创建和管理具有基本 AI 行为（如导航、避障）的密集人群。
-   **可扩展的游戏逻辑**：你的游戏需要基于实体数量动态扩展逻辑系统，而无需为每个对象创建独立的 Actor。
-   **原型开发**：你需要快速验证大量实体交互的游戏概念。

## 蓝图用法

核心的蓝图功能通过 `MassAgentComponent` 暴露，该组件充当传统 Actor 和 Mass 实体系统之间的桥梁。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnAgent` | 根据提供的模板在指定位置生成一个新的 Mass 智能体，并返回其实体句柄。 | `UMassAgentComponent` |
| `SetEntityData` | 向与该组件关联的实体写入指定类型的数据（Fragment）。 | `UMassAgentComponent` |
| `GetEntityData` | 从与该组件关联的实体读取指定类型的数据（Fragment）。 | `UMassAgentComponent` |

### 使用示例（蓝图描述）

要在蓝图中生成 Mass 智能体，通常：
1.  创建一个 Actor，并为其添加 `MassAgentComponent` 组件。
2.  通过“Spawn Agent”节点，传入一个预定义的 `MassEntityConfig`（包含要附加的 Fragment 和 Trait 配置）以及世界位置。
3.  生成的实体句柄可用于后续的实体数据读写操作。要影响实体行为（如移动），可以通过 `SetEntityData` 写入 `FMassMoveTargetFragment` 等数据来驱动对应的处理器。

## C++ 用法

`MassGameplay` 的 C++ 用法主要围绕配置实体、处理实体数据以及编写自定义的处理器（Processor）和片段（Fragment）。

### 头文件引入

```cpp
#include "MassAgentComponent.h"
#include "MassEntityConfigAsset.h"
#include "MassEntityTypes.h"
```

### 基本用法

以下代码展示了如何以编程方式生成一个 Mass 智能体（来源：基于官方 MassAgent 相关测试实践）。

```cpp
// 假设你有一个 UMassAgentComponent* AgentComponent 和一个 UMassEntityConfigAsset* EntityConfig
void AMySpawnerActor::SpawnMassAgent()
{
    if (AgentComponent && EntityConfig)
    {
        // 使用 AgentComponent 的 SpawnAgent 方法生成实体
        FMassEntityHandle EntityHandle = AgentComponent->SpawnAgent(EntityConfig, GetActorLocation());
        
        if (EntityHandle.IsValid())
        {
            // 实体生成成功，可以对其进行后续操作
            UE_LOG(LogTemp, Log, TEXT("Spawned Mass Agent: %s"), *EntityHandle.DebugGetDescription());
        }
    }
}
```

### 进阶用法

进阶用法涉及直接操作实体管理器（`UMassEntityManager`）和编写自定义的片段（Fragment）与处理器（Processor），这构成了 `MassGameplay` 的核心逻辑层。一个典型的处理器示例（来自 `MassMovement` 模块）：

```cpp
// 定义一个移动处理器，根据速度片段更新位置
UCLASS()
class UMyMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyMovementProcessor();
protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
};

UMyMovementProcessor::UMyMovementProcessor()
{
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyMovementProcessor::ConfigureQueries()
{
    // 查询包含变换和移动速度片段的实体
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMovementParameters>(EMassFragmentAccess::ReadOnly);
}

void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合条件的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        const int32 NumEntities = Context.GetNumEntities();
        const TConstArrayView<FMassVelocityFragment> VelocityList = Context.GetFragmentView<FMassVelocityFragment>();
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FVector& Velocity = VelocityList[i].Value;
            FTransform& Transform = TransformList[i].GetMutableTransform();
            
            // 简单的位置更新逻辑
            Transform.AddToTranslation(Velocity * Context.GetDeltaTimeSeconds());
        }
    });
}
```

## Demo 示例

一个最小可编译示例，展示如何在 C++ Actor 中使用 `MassAgentComponent` 生成大量智能体。

**MyMassSpawnerComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MassAgentComponent.h"
#include "MyMassSpawnerComponent.generated.h"

UCLASS(ClassGroup=(Mass), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyMassSpawnerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMassSpawnerComponent();

protected:
    virtual void BeginPlay() override;

    /** 用于生成智能体的配置资产 */
    UPROPERTY(EditAnywhere, Category = "Mass")
    TObjectPtr<UMassEntityConfigAsset> AgentConfig;

    /** 生成数量 */
    UPROPERTY(EditAnywhere, Category = "Mass")
    int32 AgentsToSpawn = 1000;

private:
    UPROPERTY()
    TObjectPtr<UMassAgentComponent> AgentComponent;
};
```

**MyMassSpawnerComponent.cpp**
```cpp
#include "MyMassSpawnerComponent.h"
#include "MassEntityConfigAsset.h"

UMyMassSpawnerComponent::UMyMassSpawnerComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMassSpawnerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 确保拥有一个 MassAgentComponent
    AgentComponent = GetOwner()->FindComponentByClass<UMassAgentComponent>();
    if (!AgentComponent)
    {
        AgentComponent = NewObject<UMassAgentComponent>(GetOwner(), TEXT("MassAgent"));
        AgentComponent->RegisterComponent();
    }

    // 生成指定数量的智能体
    if (AgentConfig && AgentComponent)
    {
        const FVector SpawnOrigin = GetOwner()->GetActorLocation();
        for (int32 i = 0; i < AgentsToSpawn; ++i)
        {
            // 在附近随机位置生成
            FVector RandomOffset = FMath::VRand() * 1000.0f;
            RandomOffset.Z = 0.0f; // 保持在同一平面
            AgentComponent->SpawnAgent(AgentConfig, SpawnOrigin + RandomOffset);
        }
        UE_LOG(LogTemp, Warning, TEXT("Spawned %d Mass Agents."), AgentsToSpawn);
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，使用者需要关注以下**独特**的依赖模块（已排除 Core, Engine 等标准依赖）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心依赖，提供 ECS 架构的基础（实体、片段、处理器）。 |
| `MassEntityEditor` | 用于编辑器中 MassEntity 相关资产的编辑支持。 |
| `AIModule` | 为 MassAI 和某些 Trait 提供 AI 子系统集成（如感知）。 |
| `NavigationSystem` | 为 MassMovement 和智能体寻路提供导航支持。 |
| `GameplayTasks` | MassStateTree 等特性可能与异步任务系统集成。 |
| `StateTreeModule` | `MassStateTree` 模块用于将 StateTree 状态机绑定到 Mass 实体。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚对 MassAgentComponent 的先前更改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 表示模块：关闭实例化静态网格（ISM）前等待 Actor 就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds. | 修复大规模人群中非傀儡 Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 表示模块：修复 LOD 计算器在每观众器 LOD 路径中的一系列原有 bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 表示模块：将两处手动计算的 `bDoKeepActorExtraFrame` 切换为使用新的 UE::M... 宏/方法。 |

### 维护评价

- **状态**：**维护中**。虽然标记为实验性且默认不启用，但根据近期提交记录（最新在 2026 年 5 月），该插件仍在活跃开发和 bug 修复中，特别是在 `MassRepresentation`（表示）和 `MassAgentComponent` 等关键子模块。
- **活跃度**：近期更新集中于 bug 修复和稳定性改进，表明团队仍在维护其代码质量。这并非一个已被抛弃的实验性功能。
- **推荐**：**谨慎推荐**。对于需要大规模实体模拟的项目，`MassGameplay` 是目前 UE5 官方提供的核心解决方案。然而，由于其标记为**实验性**，API 可能不稳定，在未来版本中有破坏性更改的风险。建议在项目早期采用，并做好应对未来版本迁移的准备。适合有经验的 UE5 开发者用于原型验证或性能要求极高的特定场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Tests)