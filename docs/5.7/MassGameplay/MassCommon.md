# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件是 Unreal Engine 5 中基于 MassEntity (ECS) 框架构建的大规模智能体（Agent）模拟系统。它旨在解决传统基于 Actor 的架构在处理成千上万个游戏实体（如 NPC、子弹、粒子、载具等）时遇到的性能瓶颈。

**核心价值**：
1.  **数据驱动与缓存友好**：通过将实体数据（如位置、速度、生命值）存储在连续的内存块（Fragment）中，极大地提高了 CPU 缓存的命中率，从而显著提升处理速度。
2.  **并行处理**：系统（Processor）可以轻松地并行处理大量实体，充分利用多核 CPU。
3.  **解耦与模块化**：实体的行为由独立的、可组合的“处理器”定义，而不是庞大的单体 Actor 类，使得逻辑更清晰、更易于维护和扩展。
4.  **大规模模拟**：专为需要同时模拟数千甚至数万个动态对象的场景而设计，是传统 Actor 模型的高性能替代方案。

简而言之，MassGameplay 为需要极致性能和大规模实体管理的游戏玩法（如 RTS、开放世界、弹幕射击）提供了底层框架支持。

## 使用场景

-   **即时战略游戏 (RTS)**：你需要同时控制和渲染成百上千个单位、建筑和投射物。
-   **开放世界游戏**：你需要在广阔的地图上模拟大量密集的 NPC、野生动物或交通载具。
-   **弹幕射击游戏**：你需要高效地管理屏幕上同时存在的成千上万颗子弹和特效。
-   **大规模战斗模拟**：你需要模拟大型战场，包含大量士兵、车辆和环境交互。
-   **任何需要高性能实体管理的场景**：当标准的 Actor 数量成为性能瓶颈时，考虑使用 MassGameplay。

## 蓝图用法

MassGameplay 主要通过 C++ 进行深度定制和系统开发，但其基础组件和配置也暴露给蓝图。核心的“片段”（Fragment）是数据容器，通常通过 C++ 添加到实体中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Transform` | 获取实体的变换信息 | `FTransformFragment` |
| `Set Transform` | 设置实体的变换信息 | `FTransformFragment` |
| `Get Radius` | 获取实体的代理半径 | `FAgentRadiusFragment` |
| `Set Radius` | 设置实体的代理半径 | `FAgentRadiusFragment` |

### 使用示例（蓝图描述）

虽然 Mass 实体本身不直接作为蓝图对象存在，但你可以通过 `MassSpawner` 或自定义的 Actor 包装器来与蓝图交互。一个典型的蓝图工作流是：
1.  创建一个继承自 `AMassActor` 或实现了 `IMassEntityInterface` 的 Actor 蓝图。
2.  在该 Actor 蓝图中，你可以定义如何将蓝图中的属性（如移动速度）映射到 Mass 片段（如 `FMovementParameters`）上。
3.  使用 `MassSpawner` 蓝图或 C++ 代码在世界中生成这些实体。
4.  通过 Mass 系统（处理器）来批量更新所有实体的状态，而不是逐个 Actor 更新。

## C++ 用法

### 头文件引入

```cpp
#include "MassCommonFragments.h" // 基础片段，如 FTransformFragment
#include "MassCommonTypes.h"     // 基础类型和工具
#include "RandomSequence.h"      // 确定性随机数生成
```

### 基本用法

**1. 定义自定义片段 (Fragment)**
片段是附加到实体上的纯数据结构。
```cpp
// MyFragments.h
#pragma once
#include "MassEntityTypes.h"
#include "MyFragments.generated.h"

USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "")
    float MaxHealth = 100.0f;
};
```

**2. 创建和配置实体**
在处理器或生成器中，为实体添加片段。
```cpp
// 假设在一个处理器的 Execute 函数中
void UMyProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // 遍历所有拥有 FTransformFragment 和 FHealthFragment 的实体
    Context.ForEachEntityChunk(EntitySubsystem, [this](FMassExecutionContext& Context)
    {
        // 获取片段数组（连续内存）
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const TArrayView<FHealthFragment> HealthList = Context.GetMutableFragmentView<FHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FTransform& Transform = TransformList[i].GetMutableTransform();
            FHealthFragment& Health = HealthList[i];

            // 示例：根据生命值调整缩放
            const float HealthPercent = Health.CurrentHealth / Health.MaxHealth;
            Transform.SetScale3D(FVector(HealthPercent));

            // 使用确定性随机数（来自 MassCommonUtils）
            if (UE::Mass::Utils::IsDeterministic())
            {
                // 使用实体索引作为种子，确保结果可重现
                const int32 EntityIndex = Context.GetEntity(i).SerialNumber;
                const float RandomOffset = UE::RandomSequence::FRandRange(EntityIndex, -10.f, 10.f);
                // ... 应用随机偏移
            }
        }
    });
}
```
*（来源：基于 `MassCommonFragments.h` 和 `RandomSequence.h` 的典型用法推断）*

### 进阶用法

**1. 定义处理器 (Processor)**
处理器是包含逻辑的系统，用于查询和操作特定组合的实体。
```cpp
// MyProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyProcessor.generated.h"

UCLASS()
class UMyHealthRegenerationProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyHealthRegenerationProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context) override;

private:
    // 查询：需要同时拥有 FHealthFragment 和 FTransformFragment 的实体
    FMassEntityQuery EntityQuery;
};

// MyProcessor.cpp
UMyHealthRegenerationProcessor::UMyHealthRegenerationProcessor()
{
    // 设置处理器执行的组和阶段
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Behavior;
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
}

void UMyHealthRegenerationProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddTagRequirement<FMassNeedsRegenerationTag>(EMassFragmentPresence::All);
}

void UMyHealthRegenerationProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // 使用查询遍历实体
    EntityQuery.ForEachEntityChunk(EntitySubsystem, Context, [this](FMassExecutionContext& Context)
    {
        // ... 逻辑与基本用法类似
    });
}
```

**2. 使用标签 (Tag) 控制行为**
标签是空的片段，用于标记实体状态。
```cpp
// 在 ConfigureQueries 中添加标签要求
EntityQuery.AddTagRequirement<FMassIsAliveTag>(EMassFragmentPresence::All);
EntityQuery.AddTagRequirement<FMassIsDeadTag>(EMassFragmentPresence::None); // 确保实体没有死亡标签
```

## Demo 示例

一个最小的示例，展示如何创建一个带有生命值和变换的 Mass 实体。

**MyMassEntity.h**
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MyMassEntity.generated.h"

// 自定义片段
USTRUCT()
struct FSimpleHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float Health = 100.f;
};

// 一个简单的 Actor，用于在蓝图中生成 Mass 实体
UCLASS()
class AMyMassSpawnerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMassSpawnerActor();

    UFUNCTION(BlueprintCallable, Category = "Mass")
    void SpawnMassEntity();

protected:
    UPROPERTY(EditAnywhere, Category = "Mass")
    int32 NumEntitiesToSpawn = 100;

    UPROPERTY(EditAnywhere, Category = "Mass")
    FVector SpawnAreaExtent = FVector(1000.f, 1000.f, 0.f);
};
```

**MyMassEntity.cpp**
```cpp
#include "MyMassEntity.h"
#include "MassEntitySubsystem.h"
#include "MassCommonFragments.h"

AMyMassSpawnerActor::AMyMassSpawnerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMassSpawnerActor::SpawnMassEntity()
{
    UMassEntitySubsystem* MassSubsystem = UWorld::GetSubsystem<UMassEntitySubsystem>(GetWorld());
    if (!MassSubsystem)
    {
        return;
    }

    // 创建实体模板（Archetype），定义该类实体拥有的片段组合
    FMassArchetypeCompositionDescriptor Composition;
    Composition.Fragments.Add<FTransformFragment>();
    Composition.Fragments.Add<FSimpleHealthFragment>();

    const FMassArchetypeHandle Archetype = MassSubsystem->CreateArchetype(Composition);

    // 批量生成实体
    for (int32 i = 0; i < NumEntitiesToSpawn; ++i)
    {
        const FVector SpawnLocation = GetActorLocation() + FMath::RandPointInBox(FBox(-SpawnAreaExtent, SpawnAreaExtent));
        const FTransform SpawnTransform(SpawnLocation);

        // 创建实体并获取其句柄
        const FMassEntityHandle EntityHandle = MassSubsystem->CreateEntity(Archetype);

        // 设置初始数据
        if (FTransformFragment* TransformFragment = MassSubsystem->GetFragmentDataPtr<FTransformFragment>(EntityHandle))
        {
            TransformFragment->SetTransform(SpawnTransform);
        }
        if (FSimpleHealthFragment* HealthFragment = MassSubsystem->GetFragmentDataPtr<FSimpleHealthFragment>(EntityHandle))
        {
            HealthFragment->Health = FMath::RandRange(50.f, 150.f);
        }
    }
}
```

## 模块依赖

MassGameplay 插件内部模块高度耦合，但对外部模块的依赖相对集中。使用此插件时，你的项目模块通常需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的基石，提供 ECS 核心框架（实体、片段、系统）。 |
| `MassSpawner` | 提供实体生成和模板管理功能。 |
| `MassRepresentation` | 处理实体的视觉表现（如 Static Mesh、Anim Instance）。 |
| `MassMovement` | 处理实体的移动和导航。 |
| `MassCommon` | 提供通用片段（如 `FTransformFragment`）和工具函数。 |

**注意**：由于 MassGameplay 是实验性插件且默认禁用，你需要在项目的 `.uproject` 文件中显式启用它，并在你的模块的 `Build.cs` 文件中添加对上述模块的依赖。

## 维护状态

### 近期更新

```
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- cd3c2a716daa Replace some usages of FORCEINLINE with inline in Mass modules.
- 939cc6e51c10 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
```

### 维护评价

-   **创建时间**：2021年9月，作为 UE5 的新特性引入，历史约3年。
-   **最近更新频率**：最近的提交（截至提供信息）均为代码维护性改动（如内联优化、符号导出规范），**没有实质性的功能更新或 bug 修复**。
-   **维护状态**：**维护不活跃**。自创建以来，该插件一直处于“实验性”状态（`IsExperimentalVersion: true`），且默认禁用。最近的提交表明 Epic 可能仍在进行底层代码清理，但没有迹象表明该插件即将脱离实验阶段或获得重大功能增强。
-   **已知问题/限制**：
    1.  **实验性**：API 可能不稳定，在未来版本中可能发生破坏性更改。
    2.  **学习曲线陡峭**：需要理解 ECS 编程范式，与传统的 Actor 思维模式差异很大。
    3.  **工具链支持有限**：编辑器内的可视化调试和编辑工具可能不如传统 Actor 完善。
    4.  **文档和社区资源较少**：作为实验性功能，官方文档和社区教程相对匮乏。
-   **推荐使用**：
    -   **不推荐**用于需要快速迭代、稳定 API 或团队对 ECS 不熟悉的**生产项目**。
    -   **推荐**用于**技术预研、原型开发**或**对性能有极致要求且团队具备 ECS 经验**的特定项目模块。在决定使用前，务必评估其“实验性”状态带来的风险。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) (插件内测试套件)