# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模智能体模拟框架 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、游戏逻辑模块） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Epic Games 基于核心 MassEntity (ECS) 框架构建的一套面向**游戏逻辑**的完整实现与解决方案。它存在的根本目的是为了在使用 MassEntity 处理海量（成千上万）实体的基础上，提供一套开箱即用的、可扩展的“游戏玩法”组件，将底层的 ECS 逻辑与上层的 Actor、动画、AI、环境交互等游戏概念连接起来。

它解决的核心问题是：如何高效地管理和驱动海量游戏角色（Agent）的**生成（Spawning）、运动（Movement）、感知与决策（EQS， Environment Query System）、表示（Representation， 包括网格体、动画）、细节层次（LOD）、网络复制（Replication）** 以及与游戏世界（如 SmartObjects）的交互。这个插件是构建大型开放世界、RTS、模拟城市、人群模拟等项目的基石。

**注意：此插件默认未启用 (`EnabledByDefault: false`)，且为实验性 (`IsExperimentalVersion: true`)，表明其 API 和功能仍在演进中。**

## 使用场景

- 你在开发一个开放世界游戏，需要同时渲染和控制成千上万的 NPC（市民、敌人、动物），以实现“活生生”的世界感。
- 你在制作一款即时战略游戏（RTS），需要同时控制和寻路上千个单位。
- 你需要一个系统，能自动根据摄像机距离对海量实体进行细节层次（LOD）管理，例如远距离只显示低模或使用实例化静态网格体（ISM），近距离显示带动画的 Actor。
- 你需要将基于 MassEntity 的高性能模拟逻辑，与现有的基于 Actor 的蓝图、动画蓝图、AI 行为树系统进行交互和桥接。
- 你需要为海量实体实现高效的环境查询（EQS）以进行寻路或决策。
- 你需要实现海量实体在多人游戏环境下的网络同步与复制。

## 蓝图用法

由于 MassGameplay 是一个 Runtime 框架，其主要蓝图节点用于控制实体的生成、管理与查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据提供的 `MassEntitySpawnDataGenerator` 配置生成一个或多个 MassEntity。这是蓝图中最主要的生成入口。 | `AMassEntitySpawnDataGenerator` |
| `Set Movement Style` | 为一个或多个实体设置运动样式（Movement Style），例如巡逻、追击、随机游走等。 | `UMassAgentComponent` |
| `Get Entities In Radius` | 获取指定半径内所有符合查询条件的 MassEntity 列表。 | `UMassAgentSubsystem` |
| `Get Entity Handle` | 从一个 Actor 获取其对应的 MassEntity Handle（如果存在）。 | `UMassAgentComponent` |
| `On Mass Entity Spawned` | 一个可绑定的蓝图事件，当通过 MassSpawnSystem 生成实体后触发。 | `UMassSpawnerSubsystem` |
| `Request Environment Query` | 为实体请求执行一个 Environment Query（EQS），获取查询结果（位置、Actor等）。 | `UMassEQSSubsystem` |

### 使用示例（蓝图描述）

1.  **生成海量实体**：在场景中放置一个 `MassEntitySpawnDataGenerator` Actor。在其细节面板中配置 `SpawnDataGenerator`（例如 `UMassCrowdSpawner`），定义生成数量、区域、实体模板等。当游戏开始或满足某个条件时，调用其 `SpawnEntities` 函数。
2.  **为实体添加AI**：在实体模板（`MassEntityTemplate`）中，可以添加 `MassMovement` 和 `MassEQS` 片段（Fragment），并配置相应的处理器（Processor）。在蓝图中，可以通过 `Set Movement Style` 节点动态改变实体的运动行为。
3.  **实体与Actor交互**：确保实体具有 `MassActor` 或 `MassRepresentation` 片段。在蓝图中，通过 `Get Entity Handle` 获取一个角色 Actor 对应的实体句柄，然后可以使用其他系统节点（如 `Set Movement Style`）来影响其 ECS 逻辑。反之，ECS 逻辑也可以通过表示系统驱动 Actor 的动画和位置。

## C++ 用法

### 头文件引入

根据所需功能，包含对应模块的头文件。例如：
```cpp
#include "MassEntitySpawnDataGenerator.h"
#include "MassMovement/Public/MassMovementFragments.h"
#include "MassSpawner/Public/MassSpawnTypes.h"
```

### 基本用法

以下示例展示如何以编程方式生成实体。

**来源：** `Engine/Plugins/Runtime/MassGameplay/Source/MassSpawner/Tests/MassSpawnerTest.cpp`

```cpp
#include "MassSpawnerSubsystem.h"
#include "MassEntityTemplate.h"

void AMySpawnerActor::SpawnMassEntities()
{
    UWorld* World = GetWorld();
    if (!World) return;

    // 1. 获取 MassSpawner 子系统
    UMassSpawnerSubsystem* SpawnerSubsystem = World->GetSubsystem<UMassSpawnerSubsystem>();
    if (!SpawnerSubsystem) return;

    // 2. 准备实体模板 (可以在编辑器中预设或在代码中创建)
    FMassEntityTemplateID TemplateID = /* ... 从配置或资源中获取模板ID ... */;

    // 3. 准备生成上下文和数量
    FMassEntitySpawnDataGenerator Context;
    Context.TemplateID = TemplateID;
    Context.NumEntities = 1000;
    Context.SpawnLocation = GetActorLocation();
    Context.SpawnRadius = 1000.0f;

    // 4. 执行生成
    SpawnerSubsystem->SpawnEntities(Context);
}
```

### 进阶用法

结合 LOD 和 Representation 实现性能优化的实体管理。

**来源：** 基于 `MassRepresentation` 模块测试逻辑

```cpp
#include "MassRepresentationSubsystem.h"
#include "MassLOD/Public/MassLODFragments.h"
#include "MassRepresentation/Public/MassRepresentationFragments.h"

// 假设我们有一个自定义的 Processor，用于根据距离更新实体的表现
class FMyLODAndVisualProcessor : public FMassProcessor
{
    // ... 处理器定义 ...

    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override
    {
        // 查询所有具有位置、LOD和表示片段的实体
        EntityManager.ForEachEntity<FMassEntityHandle, FTransformFragment, FMassLODFragment, FMassRepresentationFragment>(
            [&](FMassEntityHandle EntityHandle,
                FTransformFragment& TransformFragment,
                FMassLODFragment& LODFragment,
                FMassRepresentationFragment& RepresentationFragment)
            {
                // 1. 计算实体与所有观察者（如玩家）的距离，更新LOD等级
                // LODFragment.LODLevel = CalculateLOD(TransformFragment.GetTransform().GetLocation());

                // 2. 根据LOD等级，决定如何表示实体
                // if (LODFragment.LODLevel == EMassLOD::High)
                // {
                //     // 使用 Actor 表示 (高保真)
                //     RepresentationFragment.VisualType = EMassVisualType::Actor;
                //     RepresentationFragment.StaticMeshDescIndex = INDEX_NONE; // 使用动画蓝图
                // }
                // else if (LODFragment.LODLevel == EMassLOD::Medium)
                // {
                //     // 使用带简单动画的 Actor
                //     RepresentationFragment.VisualType = EMassVisualType::AnimInstance;
                // }
                // else
                // {
                //     // 使用实例化静态网格体 (ISM) 或完全隐藏 (低保真)
                //     RepresentationFragment.VisualType = EMassVisualType::StaticMesh;
                //     RepresentationFragment.StaticMeshDescIndex = /* 低模索引 */;
                // }
            });
    }
};
```

## Demo 示例

一个最小化的实体生成与移动处理器示例。

**MyMassDemoEntity.h**
```cpp
// 一个简单的移动片段，存储目标位置
USTRUCT()
struct FMassMovementGoalFragment : public FMassFragment
{
    GENERATED_BODY()
    FVector GoalLocation = FVector::ZeroVector;
};
```

**MyMassDemoProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyMassDemoEntity.h"

// 一个简单的处理器，将实体向目标点移动
class FMyMassDemoMoveProcessor : public FMassProcessor
{
public:
    FMyMassDemoMoveProcessor();
protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**MyMassDemoProcessor.cpp**
```cpp
#include "MyMassDemoProcessor.h"
#include "MassMovement/Public/MassMovementFragments.h"
#include "MassCommon/Public/MassEntityView.h"

FMyMassDemoMoveProcessor::FMyMassDemoMoveProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroups::Movement;
}

void FMyMassDemoMoveProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassAccessAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMovementGoalFragment>(EMassAccessAccess::ReadOnly);
    // 假设我们有一个自定义的速度片段
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassAccessAccess::ReadWrite);
}

void FMyMassDemoMoveProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const int32 NumEntities = Context.GetNumEntities();
        const TConstArrayView<FTransformFragment> Transforms = Context.GetFragmentView<FTransformFragment>();
        const TConstArrayView<FMassMovementGoalFragment> Goals = Context.GetFragmentView<FMassMovementGoalFragment>();
        const TArrayView<FMassVelocityFragment> Velocities = Context.GetMutableFragmentView<FMassVelocityFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FVector CurrentLocation = Transforms[i].GetTransform().GetLocation();
            const FVector DirectionToGoal = (Goals[i].GoalLocation - CurrentLocation).GetSafeNormal();
            const float Speed = 500.0f; // 假设固定速度

            Velocities[i].Velocity = DirectionToGoal * Speed;
        }
    });
}
```

## 模块依赖

MassGameplay 插件内部的模块相互依赖，但对外，你的项目模块主要需要依赖你实际使用的特定模块。以下是**除 Core/Engine/Slate 等常见依赖外**，各 Mass 子模块常见的独特依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | **核心**。MassEntity 框架本身。所有子模块的基石。 |
| `MassEntityTestSuite` | 用于编写和运行 Mass 系统相关的自动化测试。 |
| `MassEntityEditor` | 提供 MassEntity 资产（如模板）的编辑器支持。`MassGameplayDebug`、`MassSimulation`、`MassSpawner` 等模块的编辑器功能依赖它。 |
| `AITestSuite` | 用于 AI 相关（如 EQS）的测试。 |
| `GameplayAbilities` | （可选）用于实现技能系统与 Mass 实体的集成。 |
| `StateTree` | （可选）用于实现基于状态树的 AI 逻辑驱动 Mass 实体。 |

**你的 Build.cs 中可能需要这样引用：**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    // 根据你需要的功能，添加对应的 Mass 模块
    "MassEntity",
    "MassCommon",
    "MassMovement",
    "MassRepresentation"
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的早期更改，可能是为了修复回归问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在关闭实例化静态网格体（ISM）表示前，等待关联的 Actor 准备就绪，提升了表示切换的稳定性。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 人群中处理非木偶（non-puppet）角色的逻辑问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 `TMassLODCalculator` 中按观察者计算 LOD 路径下的一系列已知 bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 优化了表示系统中 `bDoKeepActorExtraFrame` 标志的计算逻辑。 |

### 维护评价

MassGameplay 插件**处于活跃维护状态**。其创建于 2021 年，作为 Unreal Engine 5 的实验性核心功能之一，近一年来仍有频繁且实质性的提交（包括 bug 修复、功能优化和重构）。从最近的提交记录可以看出，开发团队正在持续改进其稳定性、性能和功能集，特别是在 **表示（Representation）**、**LOD** 和 **Actor 集成**方面。

由于其被标记为实验性 (`IsExperimentalVersion: true`)，意味着其 API 和架构在未来版本中仍可能发生变化。它是一个功能强大且被 Epic 积极推进的技术栈，非常适合用于开发需要海量实体的新项目。建议在项目中使用时，密切关注其版本更新和 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/mass-gameplay-in-unreal-engine/) （UE5 官方文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)