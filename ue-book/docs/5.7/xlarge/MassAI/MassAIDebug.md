# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine 5 中 MassGameplay (ECS) 框架的 AI 扩展插件。它解决了在大规模实体（成千上万）场景下，传统基于 Actor 的 AI 系统（如行为树、导航网格）性能瓶颈的问题。

该插件的核心目的是为 MassGameplay 实体提供高效的 AI 行为、导航和调试能力。它将 AI 逻辑（如状态树、行为决策）和导航逻辑（如路径跟随、避障）以处理器（Processor）的形式实现，能够与 MassGameplay 的实体查询和执行系统无缝集成，从而实现高性能的群体 AI 模拟。

## 使用场景

- **大规模 RTS 或模拟游戏**：你需要控制成百上千个单位进行寻路、战斗和协作，传统 Actor 方式性能无法满足。
- **开放世界 NPC 群体**：城市中有大量市民、车辆等实体需要基础的 AI 行为（如巡逻、避障），但不需要复杂的个体逻辑。
- **大规模战斗模拟**：需要模拟成千上万士兵的冲锋、阵型移动和简单战斗决策。
- **使用 MassGameplay 构建游戏**：你的项目已经基于 MassGameplay 框架，需要为其添加 AI 能力。

## 蓝图用法

由于该插件主要面向运行时和底层 ECS 逻辑，其大部分功能通过 C++ 处理器和子系统暴露。蓝图中主要通过 Gameplay Debugger 和一些配置资产进行交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Toggle Archetypes` | 在 Gameplay Debugger 中切换是否显示实体原型信息 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Shapes` | 在 Gameplay Debugger 中切换是否显示实体碰撞形状 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Agent Fragments` | 在 Gameplay Debugger 中切换是否显示实体的 AI 相关片段（Fragment）信息 | `FGameplayDebuggerCategory_Mass` |
| `Pick Entity` | 在 Gameplay Debugger 中拾取一个实体进行详细查看 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Entity Details` | 在 Gameplay Debugger 中切换是否显示被拾取实体的详细信息 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Near Entity Overview` | 在 Gameplay Debugger 中切换是否显示附近实体的概览 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Near Entity Avoidance` | 在 Gameplay Debugger 中切换是否显示附近实体的避障信息 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Near Entity Path` | 在 Gameplay Debugger 中切换是否显示附近实体的路径 | `FGameplayDebuggerCategory_Mass` |
| `Toggle Entity Look At` | 在 Gameplay Debugger 中切换是否显示实体的视线方向 | `FGameplayDebuggerCategory_Mass` |
| `Cycle Entity Description` | 在 Gameplay Debugger 中循环切换实体描述的详细程度 | `FGameplayDebuggerCategory_Mass` |

### 使用示例（蓝图描述）

1.  **启用插件**：在项目设置中启用 `MassAI` 插件。
2.  **配置导航**：在 `MassNavigation` 相关的配置资产中，设置导航类型（如使用 NavMesh 或 ZoneGraph）。
3.  **运行时调试**：
    - 按 `'` 键打开 Gameplay Debugger。
    - 选择 `Mass` 分类。
    - 使用上述节点对应的快捷键（如 `1` 切换原型显示，`2` 切换形状显示等）来可视化 Mass 实体的 AI 状态、导航路径和避障情况。
    - 使用 `Pick Entity` 功能（默认快捷键 `P`）点击一个实体，查看其详细的状态树执行情况、片段数据和导航信息。

## C++ 用法

### 头文件引入

```cpp
#include "MassAIDebugModule.h" // 用于访问调试模块
#include "MassDebugStateTreeProcessor.h" // 用于自定义调试处理器
#include "GameplayDebuggerCategory_Mass.h" // 用于扩展调试类别
```

### 基本用法

创建一个自定义的 Mass 处理器，用于处理带有特定 AI 标签的实体。此示例基于 `UMassDebugStateTreeProcessor` 的结构。

```cpp
// MyMassAIPorcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MyMassAIProcessor.generated.h"

UCLASS()
class UMyMassAIProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMassAIProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyMassAIProcessor.cpp
#include "MyMassAIProcessor.h"
#include "MassEntityTypes.h" // 用于 FMassEntityHandle
#include "MassExecutionContext.h"

UMyMassAIProcessor::UMyMassAIProcessor()
{
    // 设置处理器执行顺序，例如在导航之后执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
    ProcessingPhase = EMassProcessingPhase::PostPhysics; // 或其他合适的阶段
}

void UMyMassAIProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询，只处理带有 FMyAITag 片段的实体
    EntityQuery.AddRequirement<FMyAITag>(EMassFragmentAccess::ReadWrite);
    // 可以添加其他需求，例如位置、速度等
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    // 将查询与处理器关联
    ProcessorRequirements.AddEntityRequirement(EntityQuery);
}

void UMyMassAIProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取实体数组
        const int32 NumEntities = Context.GetNumEntities();
        const TConstArrayView<FTransformFragment> TransformList = Context.GetFragmentView<FTransformFragment>();
        const TArrayView<FMassMoveTargetFragment> MoveTargetList = Context.GetMutableFragmentView<FMassMoveTargetFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            // 在这里实现你的 AI 逻辑
            // 例如，根据 TransformList[i] 的位置，计算一个新的移动目标到 MoveTargetList[i]
            const FVector CurrentLocation = TransformList[i].GetTransform().GetLocation();
            // ... 简单的 AI 决策逻辑 ...
            MoveTargetList[i].TargetLocation = CurrentLocation + FVector(100.f, 0.f, 0.f); // 示例：向前移动
        }
    });
}
```

### 进阶用法

结合 `MassNavigation` 模块的片段，实现一个简单的跟随行为。

```cpp
// 在 ConfigureQueries 中添加导航相关片段
EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
EntityQuery.AddTagRequirement<FMyFollowerTag>(EMassFragmentPresence::All);

// 在 Execute 中
for (int32 i = 0; i < NumEntities; ++i)
{
    // 获取目标（例如玩家或另一个实体）的位置
    FVector TargetLocation = GetTargetLocation(); // 你需要实现这个函数
    // 设置移动目标，MassNavigation 处理器会处理实际的路径跟随和避障
    MoveTargetList[i].TargetLocation = TargetLocation;
    MoveTargetList[i].DesiredSpeed = 300.f;
    // 可以设置其他导航参数，如接受半径等
    MoveTargetList[i].AcceptableRadius = 50.f;
}
```

## Demo 示例

一个最小的自定义 Mass AI 处理器示例，它让实体向世界原点移动。

```cpp
// MoveToOriginProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MoveToOriginProcessor.generated.h"

UCLASS()
class UMoveToOriginProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMoveToOriginProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MoveToOriginProcessor.cpp
#include "MoveToOriginProcessor.h"
#include "MassMovementFragments.h" // FMassMoveTargetFragment, FMassVelocityFragment
#include "MassCommonFragments.h"   // FTransformFragment
#include "MassExecutionContext.h"

UMoveToOriginProcessor::UMoveToOriginProcessor()
{
    // 在行为阶段执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UMoveToOriginProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 需要变换和移动目标片段
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
    // 可以添加一个自定义标签来限制范围
    // EntityQuery.AddTagRequirement<FMoveToOriginTag>(EMassFragmentPresence::All);
    ProcessorRequirements.AddEntityRequirement(EntityQuery);
}

void UMoveToOriginProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        const int32 NumEntities = Context.GetNumEntities();
        const TConstArrayView<FTransformFragment> Transforms = Context.GetFragmentView<FTransformFragment>();
        const TArrayView<FMassMoveTargetFragment> MoveTargets = Context.GetMutableFragmentView<FMassMoveTargetFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            // 将移动目标设置为世界原点
            MoveTargets[i].TargetLocation = FVector::ZeroVector;
            MoveTargets[i].DesiredSpeed = 200.f;
            MoveTargets[i].AcceptableRadius = 10.f;
        }
    });
}
```

## 模块依赖

从各模块的 `Build.cs` 文件中提取的依赖关系。要使用此插件的功能，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心实体管理模块 |
| `MassSpawner` | 用于生成 Mass 实体 |
| `MassNavigation` | 提供基础的导航功能和片段定义 |
| `MassNavMeshNavigation` | 提供基于 NavMesh 的导航实现 |
| `MassZoneGraphNavigation` | 提供基于 ZoneGraph 的导航实现 |
| `MassAIBehavior` | 提供 AI 行为相关功能（如状态树集成） |
| `MassCommon` | Mass 框架的通用类型和工具 |
| `StateTreeModule` | 状态树模块，用于定义 AI 行为逻辑 |
| `GameplayDebugger` | 用于运行时 AI 调试可视化 |

## 维护状态

### 近期更新

```
- a01ceff5fb6d [Mass] Limited access to FMassArchetypeComposition's bitsets in preparation for near-future changes
- 220dcdcb3754 [MassGameplay] MassAgentComponent changes to update EntityHandle-to-actor mapping in MassActorSubsystem when dealing with a player-owned component
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
```

- `a01ceff5fb6d`：限制了对原型组合位集的访问，为即将到来的架构变更做准备。这表明底层系统仍在积极重构和优化。
- `220dcdcb3754`：修复了玩家拥有组件时实体到 Actor 映射的更新问题，属于重要的功能修复。
- `ec9009980d52`：代码维护，添加内联宏以提高编译效率。

### 维护评价

MassAI 是一个**实验性**插件，创建于约 4 年前。从近期的提交记录看，它仍在被 Epic Games 的开发团队**积极维护和改进**，主要集中在底层架构优化和关键 Bug 修复上。

**优点**：
- 作为官方 MassGameplay 框架的 AI 扩展，与引擎核心 ECS 系统深度集成，性能潜力巨大。
- 持续有来自 Epic 的更新，表明其是引擎 AI 发展的重要方向。

**风险与限制**：
- **实验性状态**：API 和功能可能在未来版本中发生 breaking changes。
- **学习曲线高**：需要理解 MassGameplay (ECS) 概念，与传统 Actor 思维模式不同。
- **文档和示例相对较少**：主要依赖源码和测试用例学习。

**推荐**：如果你正在开发一个需要大规模 AI 实体、且愿意拥抱 ECS 架构的项目，MassAI 是一个值得投入研究和使用的**前沿选择**。但对于原型开发或小型项目，传统的 AI 系统可能更简单直接。建议在项目早期进行充分的技术验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)