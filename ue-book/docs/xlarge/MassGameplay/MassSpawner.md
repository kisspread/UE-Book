# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 Unreal Engine 5 的 MassEntity (ECS) 框架构建的**大规模智能体（Agent）模拟与游戏玩法系统**。它并非一个独立的物理或动画系统，而是一个**高层级的游戏逻辑框架**，旨在解决在开放世界或需要处理成千上万动态实体（如 NPC、车辆、动物、可交互物体）的场景中，如何高效地组织、更新和交互这些实体的核心问题。

它通过将游戏对象分解为数据（Fragments）和行为（Processors），并利用 MassEntity 的数据导向设计，实现了极高的性能和可扩展性。该插件提供了从实体生成、空间管理、LOD 控制、移动、表示、网络复制到智能对象交互等一系列完整的子系统，是构建下一代大规模游戏玩法的基石。

## 使用场景

- **开放世界游戏**：你需要在大地图上生成并管理成千上万的 NPC、野生动物、行驶的车辆，且要求它们有基础的 AI 行为（如巡逻、避障）和高效的性能。
- **即时战略（RTS）或大规模战斗游戏**：你需要同时控制数百甚至数千个单位进行寻路、战斗和阵型变换。
- **模拟经营类游戏**：你需要模拟一个城市中大量市民的日常行为、交通流量等。
- **任何需要“群体智能”或“生态系统”的游戏**：你需要一个框架来定义实体的“特征”（Trait），并让它们基于这些特征在世界中自动地生成、交互和消亡。

## 蓝图用法

MassGameplay 的蓝图接口主要集中在实体的生成、销毁和配置上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoSpawning` | 根据配置的实体类型和生成器，开始生成实体。 | `AMassSpawner` |
| `DoDespawning` | 销毁由该 `MassSpawner` 生成的所有实体。 | `AMassSpawner` |
| `ScaleSpawningCount` | 缩放所有实体类型的生成数量。 | `AMassSpawner` |
| `SpawnEntities` | 通过子系统直接生成指定模板和数量的实体。 | `UMassSpawnerSubsystem` |
| `DestroyEntities` | 通过子系统销毁一组实体。 | `UMassSpawnerSubsystem` |

### 使用示例（蓝图描述）

1.  **放置生成器**：在关卡中放置一个 `AMassSpawner` Actor。
2.  **配置实体类型**：在 `AMassSpawner` 的细节面板中，配置 `Entity Types` 数组。每个元素引用一个 `UMassEntityConfigAsset` 数据资产，并设置其生成比例。
3.  **配置生成点**：在 `Spawn Data Generators` 数组中，添加一个或多个生成器（如 `UMassEntityEQSSpawnPointsGenerator` 或 `UMassEntityZoneGraphSpawnPointsGenerator`），用于决定实体在世界中的生成位置。
4.  **触发生成**：在游戏逻辑中（如 BeginPlay 或某个事件），调用 `AMassSpawner` 的 `DoSpawning` 蓝图节点。生成完成后，会触发 `OnSpawningFinishedEvent` 委托。
5.  **销毁实体**：需要清理时，调用 `DoDespawning` 节点。

## C++ 用法

### 头文件引入

```cpp
#include "MassSpawnerSubsystem.h"
#include "MassEntityConfigAsset.h"
#include "MassSpawnerTypes.h"
```

### 基本用法

通过 `UMassSpawnerSubsystem` 生成实体是最直接的方式。

```cpp
// 假设在某个 Actor 或 Subsystem 中
void AMyGameMode::SpawnInitialEntities()
{
    // 1. 获取世界子系统
    UMassSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassSpawnerSubsystem>();
    if (!SpawnerSubsystem) return;

    // 2. 准备实体配置资产 (通常在蓝图或编辑器中创建)
    UMassEntityConfigAsset* EntityConfig = LoadObject<UMassEntityConfigAsset>(nullptr, TEXT("/Game/Data/DA_NPC_Villager"));
    if (!EntityConfig) return;

    // 3. 定义要生成的实体类型和数量
    TArray<FMassSpawnedEntityType> EntityTypes;
    FMassSpawnedEntityType& EntityType = EntityTypes.AddDefaulted_GetRef();
    EntityType.EntityConfig = EntityConfig;
    EntityType.Proportion = 1.0f;

    // 4. 准备生成数据 (例如位置数组)
    TArray<FTransform> SpawnTransforms;
    // ... 填充 SpawnTransforms ...

    // 5. 创建生成数据结构
    FMassTransformsSpawnData SpawnData;
    SpawnData.Transforms = SpawnTransforms;
    SpawnData.bRandomize = true;

    // 6. 调用生成
    TArray<FMassEntityHandle> SpawnedEntities;
    TSharedPtr<FMassEntityManager::FEntityCreationContext> CreationContext = SpawnerSubsystem->SpawnEntities(
        EntityConfig->GetEntityTemplate(*GetWorld()),
        SpawnTransforms.Num(),
        FConstStructView::Make(SpawnData),
        nullptr, // 使用默认的初始化处理器
        SpawnedEntities
    );

    // CreationContext 释放时，会执行所有积攒的观察者和命令
}
```

### 进阶用法

自定义生成点生成器和实体特征（Trait）。

```cpp
// 1. 自定义生成点生成器 (继承 UMassEntitySpawnDataGeneratorBase)
UCLASS()
class UMyVolumeSpawnGenerator : public UMassEntitySpawnDataGeneratorBase
{
    GENERATED_BODY()
public:
    virtual void Generate(UObject& QueryOwner, TConstArrayView<FMassSpawnedEntityType> EntityTypes, int32 Count, FFinishedGeneratingSpawnDataSignature& FinishedGeneratingSpawnPointsDelegate) const override
    {
        // 在指定体积内随机生成点
        TArray<FMassEntitySpawnDataGeneratorResult> Results;
        BuildResultsFromEntityTypes(Count, EntityTypes, Results);

        for (FMassEntitySpawnDataGeneratorResult& Result : Results)
        {
            FMassTransformsSpawnData& SpawnData = Result.SpawnData.GetMutable<FMassTransformsSpawnData>();
            for (int32 i = 0; i < Result.NumEntities; ++i)
            {
                SpawnData.Transforms.Add(FTransform(FVector(FMath::RandPointInBox(SpawnVolume))));
            }
        }
        // 通过委托返回结果
        FinishedGeneratingSpawnPointsDelegate.Execute(Results);
    }

    UPROPERTY(EditAnywhere)
    FBox SpawnVolume;
};

// 2. 自定义实体特征 (继承 UMassEntityTraitBase)
UCLASS()
class UMyHealthTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 为实体模板添加一个生命值 Fragment
        FMyHealthFragment& HealthFragment = BuildContext.AddFragment_GetRef<FMyHealthFragment>();
        HealthFragment.MaxHealth = MaxHealth;
        HealthFragment.CurrentHealth = MaxHealth;
    }

    UPROPERTY(EditAnywhere)
    float MaxHealth = 100.0f;
};
```

## Demo 示例

一个最小的可编译示例，展示如何通过 C++ 代码生成实体。

**MyMassSpawner.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MyMassSpawner.generated.h"

class UMassEntityConfigAsset;

UCLASS()
class AMyMassSpawner : public AActor
{
    GENERATED_BODY()
public:
    AMyMassSpawner();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Mass")
    TSoftObjectPtr<UMassEntityConfigAsset> EntityConfigAsset;

    UPROPERTY(EditAnywhere, Category = "Mass")
    int32 NumToSpawn = 100;

private:
    TArray<FMassEntityHandle> SpawnedEntities;
};
```

**MyMassSpawner.cpp**
```cpp
#include "MyMassSpawner.h"
#include "MassSpawnerSubsystem.h"
#include "MassEntityConfigAsset.h"
#include "MassSpawnerTypes.h"

AMyMassSpawner::AMyMassSpawner()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMassSpawner::BeginPlay()
{
    Super::BeginPlay();

    UMassSpawnerSubsystem* SpawnerSubsystem = GetWorld()->GetSubsystem<UMassSpawnerSubsystem>();
    if (!SpawnerSubsystem || !EntityConfigAsset.IsValid()) return;

    // 异步加载配置资产
    EntityConfigAsset.LoadSynchronous();
    UMassEntityConfigAsset* ConfigAsset = EntityConfigAsset.Get();
    if (!ConfigAsset) return;

    // 获取或创建实体模板
    const FMassEntityTemplate& EntityTemplate = ConfigAsset->GetOrCreateEntityTemplate(*GetWorld());

    // 生成实体 (这里使用默认位置，实际应配合生成器)
    SpawnerSubsystem->SpawnEntities(EntityTemplate, NumToSpawn, SpawnedEntities);
}
```

## 模块依赖

要使用 `MassSpawner` 模块，你的项目模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassEntity 核心 ECS 框架。 |
| `MassSpawner` | 本模块，提供实体生成、模板和配置功能。 |

（注：其他子模块如 `MassMovement`, `MassRepresentation` 等有各自的依赖，需按需添加。）

## 维护状态

### 近期更新

- 269dce9fd11c [Mass] reconfigured the FMassProcessingContext created for initializer-processors in UMassSpawnerSubsystem::DoSpawning.
- 457eba2e5782 PR #13332: Added std::is_trivially_copyable to the CFragment concept.
- 0ebe081b7ad3 [MassGameplay] * Fixed non unity compile errors

### 维护评价

MassGameplay 是 Unreal Engine 5 中**实验性**的核心大规模模拟框架。自 2021 年创建以来，它一直是 Epic 重点开发和迭代的对象，从近期的 commit 可以看出仍在进行积极的底层优化和错误修复。

- **活跃度**：**高**。作为 UE5 的旗舰特性之一，持续得到更新和维护。
- **稳定性**：虽然标记为实验性，但其核心 API 已趋于稳定，被用于《黑客帝国：觉醒》等技术演示中。
- **推荐度**：**强烈推荐**用于需要大规模实体模拟的新项目。它是 UE5 面向未来游戏开发的关键技术栈之一。需要注意的是，由于其复杂性和实验性，学习曲线较陡，且部分 API 可能在未来版本中调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mass-entity-in-unreal-engine/) (MassEntity 框架文档，MassGameplay 基于此构建)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)