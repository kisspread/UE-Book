# Mass AI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、示例资产） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine 5 中 MassGameplay 框架的 AI 扩展插件。它旨在为大规模实体（Mass Entity）提供高效、可扩展的 AI 功能，解决传统 AI 系统在处理成千上万个 AI 代理时的性能瓶颈问题。

该插件的核心价值在于将 AI 逻辑（如行为、导航、感知）与 Mass 框架的实体组件系统（ECS）架构深度集成。它允许开发者以数据驱动的方式定义 AI 实体的行为和状态，并通过 Mass 处理器（Processor）进行批量、并行的更新，从而实现高性能的群体 AI 模拟。它解决了在 RTS、人群模拟、开放世界 NPC 等场景下，需要同时驱动大量 AI 单位时，传统 Actor 模型带来的性能开销过大的问题。

## 使用场景

- 你需要在一个 RTS 游戏中控制数百甚至数千个单位进行寻路、攻击和协同作战。
- 你在开发一个开放世界游戏，需要大量动态的 NPC 在城市中巡逻、交互，且对性能有严格要求。
- 你正在制作一个塔防或生存游戏，需要生成并管理海量的敌人波次。
- 你需要一个可扩展的框架来为大规模实体添加自定义的 AI 行为逻辑。

## 蓝图用法

由于 MassAI 是一个底层框架，其核心逻辑主要在 C++ 中通过处理器和片段实现。蓝图主要用于配置和触发，而非直接控制每个实体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindPathForEntity` | 为指定的 Mass 实体请求一条导航路径。 | `UMassNavigationSubsystem` |
| `SetEntityMoveTarget` | 设置实体的移动目标位置。 | `UMassNavigationSubsystem` |
| `AbortMove` | 中止实体的当前移动。 | `UMassNavigationSubsystem` |

### 使用示例（蓝图描述）

1.  **请求导航**：在蓝图中，你可以通过 `Get Mass Navigation Subsystem` 节点获取子系统引用，然后调用 `FindPathForEntity` 节点。你需要提供一个 `FMassEntityHandle`（实体句柄）和一个目标位置。系统会异步计算路径，并通过实体上的 `FMassMoveTargetFragment` 片段反馈结果。
2.  **设置移动目标**：使用 `SetEntityMoveTarget` 节点可以直接为实体设置一个目标位置，导航系统会自动处理后续的路径跟随。
3.  **调试**：插件包含 `MassAIDebug` 模块，可以在编辑器中可视化实体的导航路径、行为状态等，帮助调试。

## C++ 用法

### 头文件引入

根据你要使用的功能，引入对应的模块头文件。例如，使用导航功能：
```cpp
#include "MassNavigationTypes.h"
#include "MassNavigationSubsystem.h"
```

### 基本用法

MassAI 的核心用法是定义实体片段（Fragment）和处理器（Processor）。

1.  **定义 AI 片段**：创建自定义的片段来存储 AI 状态数据。
    ```cpp
    // MyAIFragment.h
    #pragma once
    #include "MassEntityTypes.h"

    USTRUCT()
    struct FMyAIFragment : public FMassFragment
    {
        GENERATED_BODY()

        UPROPERTY()
        float AlertRadius = 1000.f;

        UPROPERTY()
        bool bIsAlerted = false;
    };
    ```

2.  **创建处理器**：编写一个处理器来读取和修改这些片段。
    ```cpp
    // MyAIProcessor.h
    #pragma once
    #include "MassProcessor.h"
    #include "MyAIFragment.h"

    UCLASS()
    class UMyAIProcessor : public UMassProcessor
    {
        GENERATED_BODY()

    public:
        UMyAIProcessor();

    protected:
        virtual void ConfigureQueries() override;
        virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    private:
        FMassEntityQuery EntityQuery;
    };
    ```
    ```cpp
    // MyAIProcessor.cpp
    #include "MyAIProcessor.h"

    UMyAIProcessor::UMyAIProcessor()
    {
        ExecutionFlags = (int32)EProcessorExecutionFlags::All;
        ExecutionOrder.ExecuteBefore.Add(UE::Mass::Processor::Avoidance); // 设置执行顺序
    }

    void UMyAIProcessor::ConfigureQueries()
    {
        EntityQuery.AddRequirement<FMyAIFragment>(EMassFragmentAccess::ReadWrite);
        EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly); // 需要位置信息
    }

    void UMyAIProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
    {
        EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
        {
            const TArrayView<FMyAIFragment> AIFragments = Context.GetMutableFragmentView<FMyAIFragment>();
            const TConstArrayView<FTransformFragment> TransformFragments = Context.GetFragmentView<FTransformFragment>();

            for (int32 i = 0; i < Context.GetNumEntities(); ++i)
            {
                FMyAIFragment& AIFrag = AIFragments[i];
                const FVector& EntityLocation = TransformFragments[i].GetTransform().GetLocation();

                // 在这里实现你的 AI 逻辑，例如检查警戒范围
                // ...
            }
        });
    }
    ```

### 进阶用法

结合 `MassNavigation` 模块，可以实现复杂的移动和避障逻辑。你需要为实体添加 `FMassMoveTargetFragment` 和 `FMassVelocityFragment`，并使用 `UMassNavigationSubsystem` 来管理路径请求。处理器可以读取导航结果并应用到实体的变换上。

## Demo 示例

一个最小的 Mass AI 实体设置示例，包含一个自定义的 AI 片段和处理器。

**MyAIFragment.h**
```cpp
#pragma once
#include "MassEntityTypes.h"

USTRUCT()
struct FMyAIFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY()
    float Speed = 300.f;
};
```

**MyAIProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyAIFragment.h"

UCLASS()
class UMyAIProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyAIProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

**MyAIProcessor.cpp**
```cpp
#include "MyAIProcessor.h"
#include "MassMovementFragments.h"

UMyAIProcessor::UMyAIProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyAIProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FMyAIFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyAIProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FMyAIFragment> AIFragments = Context.GetMutableFragmentView<FMyAIFragment>();
        const TConstArrayView<FMassMoveTargetFragment> MoveTargets = Context.GetFragmentView<FMassMoveTargetFragment>();
        const TArrayView<FMassVelocityFragment> Velocities = Context.GetMutableFragmentView<FMassVelocityFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMyAIFragment& AIFrag = AIFragments[i];
            const FMassMoveTargetFragment& MoveTarget = MoveTargets[i];
            FMassVelocityFragment& Velocity = Velocities[i];

            // 简单逻辑：根据移动目标设置速度方向
            if (MoveTarget.Center.GetSafeNormal() != FVector::ZeroVector)
            {
                Velocity.Value = MoveTarget.Center.GetSafeNormal() * AIFrag.Speed;
            }
        }
    });
}
```

## 模块依赖

要使用 MassAI 插件，你的项目或模块需要依赖以下核心模块（除了常见的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 框架的核心，提供实体、片段、处理器等基础架构。 |
| `MassGameplay` | Mass 框架的游戏层扩展，提供常用的游戏相关片段和处理器。 |
| `MassNavigation` | MassAI 的核心导航模块，提供寻路、移动、避障等功能。 |
| `MassSpawner` | 用于在世界中生成和管理 Mass 实体。 |
| `ZoneGraph` | 为 `MassZoneGraphNavigation` 提供区域图数据结构和查询支持。 |
| `NavigationSystem` | UE 的传统导航系统，`MassNavMeshNavigation` 模块依赖它进行 NavMesh 查询。 |

## 维护状态

### 近期更新

- 2025-10-03 bc63a88d067f Redirect old cppcompilewarning properties to new *.CppCompileWarningSettings
  （将旧的 C++ 编译警告属性重定向到新的设置，属于项目配置维护。）
- 2025-09-15 d348655b8cad [Mass] headers cleanup, mainly pushing IWYU
  （Mass 框架头文件清理，主要推动“Include What You Use”原则，属于代码质量维护。）
- 2025-08-20 a4eade97848f [Mass] headers cleanup, take 2
  （Mass 框架头文件清理第二轮，同样是代码维护。）

### 维护评价

MassAI 插件创建于 2021 年，标记为实验性（`IsExperimentalVersion: true`）且默认未启用（`EnabledByDefault: false`）。从最近的提交记录看，过去一年内的更新全部是编译配置和头文件清理等维护性工作，没有新的功能特性或重大 bug 修复。

**综合评价**：该插件处于**维护不活跃**状态。虽然 Epic Games 仍在对其进行基础维护以确保其能编译通过，但缺乏积极的功能开发和迭代。它仍然是一个实验性功能，API 和功能可能会在未来发生变化。

**建议**：如果你的项目确实需要处理海量 AI 实体，并且愿意承担实验性 API 可能变动的风险，可以谨慎使用。对于新项目，建议密切关注 Epic Games 在 Mass 框架上的官方动态和示例项目，以评估其成熟度和适用性。不建议在需要长期稳定支持的核心功能上重度依赖此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [官方文档]() （暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)