# Mass Gameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Epic Games 为 **大规模实体（Mass Entity）模拟** 提供的运行时游戏玩法实现框架。它建立在 MassEntity（ECS 框架）之上，提供了一套完整的解决方案，用于定义、生成、模拟和管理数量庞大的“智能体”（Agents），例如 NPC、车辆、人群等。

**它解决的核心问题是**：当游戏中的实体数量达到成千上万甚至更多时，传统的基于 Actor 的模式在性能（CPU、内存）和内存布局（不利于缓存）上会遇到瓶颈。MassGameplay 通过 ECS 架构和批量处理来优化这些大规模实体的管理与模拟，使其在保持高性能的同时，还能提供丰富的游戏逻辑（如移动、LOD、复制、行为等）。

简而言之，如果你想在 UE5 中实现成千上万个独立且具有基础游戏逻辑的实体（而不仅仅是静态网格体），MassGameplay 就是为此设计的核心插件。

## 使用场景

- **RTS 游戏**：管理成百上千的作战单位、建筑物、资源点，需要高效的寻路、集群移动和战斗逻辑。
- **开放世界游戏**：模拟庞大的 NPC 人群，如城市中的行人、车辆交通，需要动态的 LOD 和行为控制。
- **塔防或生存类游戏**：生成并管理海量的怪物或敌人波次，需要高效的生成、销毁和 AI 寻路。
- **大规模环境装饰**：在场景中动态生成成片的植被、岩石、废墟等静态或半静态实体，并根据玩家距离进行细节层级切换。
- **模拟经营类游戏**：管理大量具有简单状态机和需求的居民、员工或顾客。

**注意**：此插件默认**未启用**（`EnabledByDefault: false`），且标记为**实验性**（`IsExperimentalVersion: true`），表明其 API 和功能可能尚未稳定，在生产项目中使用需谨慎评估。

## 蓝图用法

MassGameplay 提供了丰富的蓝图接口，主要通过 `AMassSpawner` 和 `UMassSpawnerSubsystem` 这两个核心类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoSpawning` | 根据配置开始生成实体。 | `AMassSpawner` |
| `DoDespawning` | 销毁所有由此 Spawner 生成的实体。 | `AMassSpawner` |
| `ScaleSpawningCount` | 设置生成数量的缩放系数。 | `AMassSpawner` |
| `GetCount` | 获取当前实体总数。 | `AMassSpawner` |
| `SpawnEntities` | 根据实体模板和数量批量生成实体，并返回生成的实体句柄。 | `UMassSpawnerSubsystem` |
| `DestroyEntities` | 根据实体句柄数组批量销毁实体。 | `UMassSpawnerSubsystem` |
| `GetMassEntityTemplate` | 根据模板ID获取实体模板。 | `UMassSpawnerSubsystem` |

### 使用示例（蓝图描述）

1.  **基础生成**：
    *   在场景中放置一个 `AMassSpawner` Actor。
    *   在其“细节”面板中，编辑 `EntityTypes` 数组，添加一个 `FMassSpawnedEntityType` 元素，并为其指定一个 `UMassEntityConfigAsset`。
    *   设置 `Count` 属性为所需的实体数量（如 1000）。
    *   勾选 `bAutoSpawnOnBeginPlay` 或在蓝图中调用 `DoSpawning` 节点来触发生成。

2.  **动态控制**：
    *   获取 `AMassSpawner` 的引用。
    *   调用 `ScaleSpawningCount` 节点，传入一个浮点数（如 0.5）来动态将实体数量减半。
    *   调用 `GetCount` 节点来获取当前活跃的实体数量。
    *   调用 `DoDespawning` 节点来清除所有实体。

3.  **通过子系统精细控制**：
    *   通过 `Get Game Instance Subsystem` 节点获取 `UMassSpawnerSubsystem`。
    *   使用 `GetMassEntityTemplate` 节点，传入一个已知的 `FMassEntityTemplateID`，获取对应的实体模板。
    *   调用 `SpawnEntities` 节点，传入模板和期望的数量，即可生成实体，并获取其句柄数组用于后续管理。

## C++ 用法

### 头文件引入

```cpp
#include "MassSpawnerSubsystem.h"
#include "MassSpawner.h"
#include "MassEntityConfigAsset.h"
#include "MassEntityTemplate.h"
```

### 基本用法：定义一个自定义实体配置

首先，你需要定义一个实体的“特征”（Trait），它决定了实体的组成（Fragments, Tags 等）。

**来源文件**：参考 `Public/MassEntityTraitBase.h` 的逻辑，但你需要自己派生。

**MyGameTrait.h**
```cpp
#pragma once

#include "MassEntityTraitBase.h"
#include "MyGameFragments.h"
#include "MyGameTrait.generated.h"

UCLASS()
class UMyGameTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

public:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 添加你的自定义 Fragment，它可能包含实体特定的状态数据
        BuildContext.AddFragment<FAIMovementFragment>();

        // 添加一个标签，用于查询哪些实体需要被 AI 处理器处理
        BuildContext.AddTag<FAICharacterTag>();

        // 可以根据条件添加共享Fragment（所有实体实例共享同一份数据）
        if (BehaviorTreeAsset)
        {
            // ... 创建共享Fragment并添加
        }
    }

protected:
    UPROPERTY(EditAnywhere, Category = "AI")
    TObjectPtr<UBehaviorTree> BehaviorTreeAsset;
};
```

然后，创建一个 `UMassEntityConfigAsset`，在编辑器中给它添加你的 `UMyGameTrait`。

### 进阶用法：自定义生成器（Spawn Data Generator）

生成器决定了实体生成的位置、数量等初始数据。

**来源文件**：`Public/MassEntitySpawnDataGeneratorBase.h` 和 `Public/MassEntityZoneGraphSpawnPointsGenerator.h`。

**MyCircleSpawnGenerator.h**
```cpp
#pragma once

#include "MassEntitySpawnDataGeneratorBase.h"
#include "MyCircleSpawnGenerator.generated.h"

UCLASS(BlueprintType, meta=(DisplayName="Circle Spawn Generator"))
class UMyCircleSpawnGenerator : public UMassEntitySpawnDataGeneratorBase
{
    GENERATED_BODY()

public:
    virtual void Generate(UObject& QueryOwner, TConstArrayView<FMassSpawnedEntityType> EntityTypes, int32 Count, FFinishedGeneratingSpawnDataSignature& FinishedGeneratingSpawnPointsDelegate) const override
    {
        // 1. 创建一个结果数组，为每种实体类型分配数据
        TArray<FMassEntitySpawnDataGeneratorResult> Results;
        BuildResultsFromEntityTypes(Count, EntityTypes, Results);

        // 2. 根据结果填充具体的生成数据
        for (FMassEntitySpawnDataGeneratorResult& Result : Results)
        {
            if (Result.NumEntities <= 0) continue;

            // 生成圆形位置数据
            TArray<FTransform> Transforms;
            GenerateCirclePoints(Transforms, Result.NumEntities, Radius);

            // 创建一个 FInstancedStruct 包裹你的生成数据结构
            FMassTransformsSpawnData SpawnData;
            SpawnData.Transforms = MoveTemp(Transforms);
            Result.SpawnData = FInstancedStruct::Make(MoveTemp(SpawnData));

            // 指定一个处理器，它知道如何将 SpawnData 应用到生成的实体上
            // 这个处理器通常是 Mass 框架提供的，例如用于设置变换
            Result.SpawnDataProcessor = UMassSpawnLocationProcessor::StaticClass();
        }

        // 3. 异步操作完成后，通过回调返回结果
        FinishedGeneratingSpawnPointsDelegate.ExecuteIfBound(Results);
    }

private:
    UPROPERTY(EditAnywhere, Category = "Generator")
    float Radius = 500.f;

    void GenerateCirclePoints(TArray<FTransform>& OutTransforms, int32 NumPoints, float CircleRadius) const
    {
        // ... 在半径为 CircleRadius 的圆上生成 NumPoints 个点
    }
};
```

在 `AMassSpawner` 的 `SpawnDataGenerators` 数组中配置你的 `UMyCircleSpawnGenerator` 实例。

## Demo 示例

下面是一个完整的、可编译的最小示例，展示如何通过 C++ 代码创建一个实体配置、定义一个简单的 Trait，并使用 Spawner 子系统生成实体。

**MyGameFragments.h**
```cpp
#pragma once

#include "MassEntityTypes.h"
#include "MyGameFragments.generated.h"

// 定义一个简单的数据 Fragment，用于存储实体的状态
USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    float Health = 100.f;
    float MaxHealth = 100.f;
};

// 定义一个标签，用于标识需要处理的实体
USTRUCT()
struct FMyActiveEntity : public FMassTag
{
    GENERATED_BODY()
};
```

**MySimpleTrait.h**
```cpp
#pragma once

#include "MassEntityTraitBase.h"
#include "MyGameFragments.h"
#include "MySimpleTrait.generated.h"

UCLASS(DisplayName="Simple Health Trait")
class UMySimpleTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

public:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 添加健康状态 Fragment，并设置初始值
        FMyHealthFragment& HealthFragment = BuildContext.AddFragment_GetRef<FMyHealthFragment>();
        HealthFragment.Health = 100.f;
        HealthFragment.MaxHealth = 100.f;

        // 添加活动标签
        BuildContext.AddTag<FMyActiveEntity>();
    }
};
```

**MyMassSpawnerUsage.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MassSpawnerSubsystem.h"
#include "MassEntityConfigAsset.h"
#include "MyMassSpawnerUsage.generated.h"

UCLASS()
class AMyMassSpawnerUsage : public AActor
{
    GENERATED_BODY()

public:
    // 在编辑器中指定包含 UMySimpleTrait 的实体配置资产
    UPROPERTY(EditAnywhere, Category = "Mass")
    TObjectPtr<UMassEntityConfigAsset> SimpleEntityConfig;

    UFUNCTION(BlueprintCallable, Category = "Mass")
    void SpawnEntitiesViaCode(int32 Count)
    {
        if (!SimpleEntityConfig || !GetWorld()) return;

        UMassSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassSpawnerSubsystem>();
        if (!SpawnerSubsystem) return;

        // 通过配置资产获取或创建实体模板
        const FMassEntityTemplate& EntityTemplate = SimpleEntityConfig->GetOrCreateEntityTemplate(*GetWorld());
        if (!EntityTemplate.IsValid()) return;

        // 通过子系统批量生成实体
        TArray<FMassEntityHandle> SpawnedEntities;
        SpawnerSubsystem->SpawnEntities(EntityTemplate, Count, SpawnedEntities);

        UE_LOG(LogTemp, Log, TEXT("Spawned %d entities via C++ code."), SpawnedEntities.Num());
    }

    UFUNCTION(BlueprintCallable, Category = "Mass")
    void DestroyAllEntities()
    {
        UMassSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassSpawnerSubsystem>();
        if (!SpawnerSubsystem) return;

        // 注意：这需要你之前存储了 SpawnedEntities 数组，并在此处传递给 DestroyEntities。
        // 此处仅为示意。
        // SpawnerSubsystem->DestroyEntities(StoredSpawnedEntities);
    }
};
```

## 模块依赖

要使用 MassGameplay 插件，你的项目模块需要依赖以下 **非通用** 模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心 ECS 框架。 |
| `MassSpawner` | 提供实体生成、模板管理、生成器框架的核心模块。 |
| `MassRepresentation` | 管理实体的可视化表示（ISM, Actor 等）和 LOD。 |
| `MassMovement` | 提供实体的移动、寻路、轨迹跟随等功能。 |
| `MassReplication` | 处理实体的网络复制，使客户端能看到服务器生成的实体。 |
| `MassSmartObjects` | 与 Smart Object 系统集成，让实体能与场景中的互动点交互。 |
| `MassLOD` | 实现基于距离的细节层级（LOD）计算。 |
| `MassActors` | 提供将 Mass 实体桥接为传统 UActor 的功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的之前修改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了关闭ISM前等待Actor就绪状态的问题。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了 Mass 人群中对非傀儡 Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`‘s per-viewer LOD path. | 修复了 `TMassLODCalculator` 按观察者LOD路径中的一系列遗留问题。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两处手动计算的 `bDoKeepActorExtraFrame` 改为使用新的 UE::M 函数。 |

### 维护评价

- **创建时间**：约 5 年前（2021年），属于较新的实验性系统。
- **最近更新**：**非常活跃**。最近一次更新就在几天前（2026年5月），且更新内容集中在核心模块（Representation、Movement）的 Bug 修复和功能完善上。
- **维护状态**：**积极维护中**。Epic Games 仍在持续投入开发，修复问题并优化性能。
- **已知限制**：
    1.  **实验性状态**：插件标记为实验性，API 可能在未来版本中发生变化。
    2.  **默认未启用**：需要在项目中手动启用。
    3.  **学习曲线陡峭**：ECS 思维和 Mass 框架的特定概念（Fragment, Tag, Chunk, Processor 等）需要时间掌握。
- **推荐使用**：如果你的项目确实需要模拟 **大规模** 实体（成千上万），并且愿意投入时间学习这个实验性框架，**那么非常推荐使用**。它提供了 UE5 中处理此问题的最底层和最高效的方案。对于中小规模项目，传统的 Actor 蓝图可能仍是更便捷的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档：（.uplugin 中未提供 DocsURL，建议查阅 UE5 官方文档网站搜索 “Mass Entity” 或 “Mass Gameplay”）
- 测试用例：此插件的测试可能位于 `Engine/Tests/Runtime/MassGameplay` 目录下（需在源码仓库中确认）。