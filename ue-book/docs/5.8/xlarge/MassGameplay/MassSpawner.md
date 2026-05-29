# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏实体 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件并非一个独立的 ECS 框架，而是**构建于 MassEntity (ECS) 核心框架之上的游戏性功能层**。其核心目的是为大规模实体（Mass Agents）提供标准的游戏性解决方案，包括但不限于：实体生成、移动、LOD、动画表示、网络复制、与 SmartObject 的交互等。

它解决的问题是：当开发者使用 MassEntity 创建成千上万个实体时，如何将这些实体与 Unreal 的传统 Actor 体系、动画系统、AI 系统以及网络复制系统无缝对接。MassGameplay 提供了一套可扩展的架构（如 Entity Trait、Translator），允许开发者以模块化的方式为实体添加复杂的游戏行为。

## 使用场景

- **大规模人群/生物群落模拟**：你需要创建上千个 NPC、动物或怪物，它们需要简单的 AI 行为、动画和网络同步。
- **即时战略 (RTS) 或塔防游戏**：你需要生成和管理大量单位（士兵、车辆、建筑），并要求高性能的寻路（MassMovement）和状态同步（MassReplication）。
- **开放世界填充**：你需要动态生成大量的环境实体（如草、石头、可破坏物）或次要角色，并需要 LOD（MassLOD）来优化性能。
- **自定义实体行为**：你希望利用 MassEntity 的 ECS 架构来定义全新的实体类型，并需要一套标准方法来将 ECS 数据翻译（Translator）为 Actor 或动画蓝图能理解的格式。

## 蓝图用法

MassGameplay 的蓝图 API 主要集中在 `MassSpawner` Actor 和 `UMassSpawnerSubsystem` 子系统上，用于控制实体的生成和销毁。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoSpawning` | 根据配置开始生成所有实体 | `AMassSpawner` |
| `DoDespawning` | 销毁由该生成器生成的所有实体 | `AMassSpawner` |
| `ScaleSpawningCount` | 按比例缩放所有实体类型的生成数量 | `AMassSpawner` |
| `GetCount` | 获取当前该生成器管理的实体总数 | `AMassSpawner` |
| `DEBUG_Spawn` | （仅编辑器）在当前位置立即生成实体用于调试 | `AMassSpawner` |
| `DEBUG_Clear` | （仅编辑器）清除所有由该生成器创建的实体 | `AMassSpawner` |

### 使用示例（蓝图描述）

1.  **基础使用**：
    *   在场景中放置一个 `AMassSpawner` Actor。
    *   在其 `Details` 面板的 `Entity Types` 数组中，添加一个或多个元素。
    *   为每个元素指定一个 `UMassEntityConfigAsset`（定义了实体的 Trait 组合）和生成比例 `Proportion`。
    *   在 `Spawn Data Generators` 数组中，配置生成位置的方式（例如，使用 `UMassEntityZoneGraphSpawnPointsGenerator` 在 ZoneGraph 路径上生成）。
    *   设置 `Count` 为要生成的实体总数。
    *   将 `bAutoSpawnOnBeginPlay` 设为 `true`，则游戏开始时自动生成；否则，需要在其他蓝图（如关卡蓝图）中调用 `DoSpawning` 节点。

2.  **程序化生成**：
    *   获取 `UMassSpawnerSubsystem` 实例（通过 `Get Game Instance` -> `Get Subsystem`）。
    *   使用子系统提供的 `Spawn Entities` 函数，传入一个 `UMassEntityConfigAsset` 和要生成的数量。
    *   可以通过返回的 `FMassEntityHandle` 数组来管理生成的实体。

## C++ 用法

### 头文件引入

```cpp
#include "MassSpawnerSubsystem.h"
#include "MassEntityConfigAsset.h"
#include "MassSpawnerTypes.h"
```

### 基本用法

**通过子系统程序化生成实体**。
（来源：基于 `MassSpawnerSubsystem.h` 和 `MassSpawnerTypes.h` 推断的标准用法）

```cpp
// 在某个 WorldContext（如 GameMode 或 Actor）中
UWorld* World = GetWorld();
if (World)
{
    // 1. 获取 Mass Spawner 子系统
    UMassSpawnerSubsystem* SpawnerSubsystem = World->GetSubsystem<UMassSpawnerSubsystem>();
    if (SpawnerSubsystem)
    {
        // 2. 加载或引用你的 EntityConfig 资产
        UMassEntityConfigAsset* MyEntityConfig = LoadObject<UMassEntityConfigAsset>(nullptr, TEXT("/Game/Path/To/MyEntityConfig"));

        if (MyEntityConfig)
        {
            TArray<FMassEntityHandle> SpawnedEntities;
            // 3. 调用生成函数，指定数量
            SpawnerSubsystem->SpawnEntities(MyEntityConfig->GetConfig(), 100, SpawnedEntities);

            // SpawnedEntities 现在包含 100 个新生成实体的句柄
        }
    }
}
```

### 进阶用法

**使用自定义生成数据生成实体**。
（来源：`MassEntitySpawnDataGeneratorBase.h` 中 `FMassEntitySpawnDataGeneratorResult` 的定义）

```cpp
// 假设你已经实现了自定义的 SpawnDataGenerator
TArray<FMassEntitySpawnDataGeneratorResult> SpawnResults;

// 创建一个结果，包含生成位置数据
FMassEntitySpawnDataGeneratorResult& NewResult = SpawnResults.Emplace_GetRef();
NewResult.NumEntities = 50; // 要生成50个实体
NewResult.EntityConfigIndex = 0; // 对应 EntityTypes 数组中的索引
NewResult.SpawnDataProcessor = UMassSpawnLocationProcessor::StaticClass(); // 指定如何处理 SpawnData

// 填充生成数据（例如位置数组）
FMassTransformsSpawnData& SpawnData = NewResult.SpawnData.GetMutable<FMassTransformsSpawnData>();
for (int32 i = 0; i < 50; ++i)
{
    SpawnData.Transforms.Add(FTransform(FVector(i * 100.f, 0.f, 0.f)));
}
SpawnData.bRandomize = false; // 按顺序分配

// 然后将 SpawnResults 传递给 AMassSpawner 的内部生成逻辑
// (具体调用需要访问 AMassSpawner 的 SpawnGeneratedEntities 方法，通常由内置的 Generator 流程驱动)
```

## Demo 示例

一个最小化的、使用 `UMassSpawnerSubsystem` 生成实体的 C++ Actor 示例。

**MyMassSpawnerActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyMassSpawnerActor.generated.h"

class UMassEntityConfigAsset;

UCLASS()
class AMyMassSpawnerActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMassSpawnerActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category="Mass")
    TObjectPtr<UMassEntityConfigAsset> EntityConfigToSpawn;

    UPROPERTY(EditAnywhere, Category="Mass")
    int32 SpawnCount = 50;

    UPROPERTY()
    TArray<FMassEntityHandle> SpawnedHandles;
};
```

**MyMassSpawnerActor.cpp**
```cpp
#include "MyMassSpawnerActor.h"
#include "MassSpawnerSubsystem.h"
#include "MassEntityConfigAsset.h"

AMyMassSpawnerActor::AMyMassSpawnerActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMassSpawnerActor::BeginPlay()
{
    Super::BeginPlay();

    UWorld* World = GetWorld();
    if (!World || !EntityConfigToSpawn) return;

    // 获取子系统
    UMassSpawnerSubsystem* SpawnerSubsystem = World->GetSubsystem<UMassSpawnerSubsystem>();
    if (SpawnerSubsystem)
    {
        // 生成实体
        SpawnerSubsystem->SpawnEntities(EntityConfigToSpawn->GetConfig(), SpawnCount, SpawnedHandles);

        UE_LOG(LogTemp, Warning, TEXT("Spawned %d Mass Entities."), SpawnedHandles.Num());
    }
}
```

## 模块依赖

要使用 MassGameplay 插件，你的游戏模块需要依赖以下核心模块（无需重复依赖 `MassEntity` 核心）：

| 模块 | 用途 |
|---|---|
| `MassSpawner` | 提供实体生成、模板管理和 `AMassSpawner` Actor |
| `MassCommon` | 提供 Mass 系统中通用的片段 (Fragment) 和标签 (Tag) |
| `MassMovement` | 提供基于 Mass 的移动系统 |
| `MassRepresentation` | 提供实体视觉表示（ISM、Actor、动画）的切换逻辑 |
| `MassReplication` | 提供实体状态的网络复制框架 |
| `MassLOD` | 提供基于距离的实体细节层次管理 |

（注：你的 `Build.cs` 文件中需要添加这些模块名到 `PublicDependencyModuleNames`。）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的先前修改 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在切换回 Actor 表示前，等待 Actor 准备就绪，修复显示问题 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了人群模拟中对非傀儡 Actor 的处理逻辑 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中按观察者计算路径的一系列现有 bug |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 重构了代码，使用新的接口来计算是否保留 Actor 额外帧 |

### 维护评价

MassGameplay 是 Unreal Engine 中管理大规模实体的核心游戏性框架。
- **创建时间**：约 4 年前（2021年），相对年轻。
- **近期活跃度**：**非常高**。从 git 历史看，在 2026 年 5 月仍有密集的功能性更新和 bug 修复（主要集中在 MassRepresentation 和 MassLOD 模块），表明 Epic Games 将其作为引擎的核心功能进行**积极维护和迭代**。
- **实验性标记**：尽管标记为实验性（`IsExperimentalVersion: true`），但从其深度和功能完整性来看，它已经是一个相当成熟且被引擎广泛依赖的系统（例如，City Sample 等大型项目都基于它构建）。
- **推荐**：**强烈推荐用于需要大规模实体的游戏项目**。虽然初期学习曲线较陡，但它提供了无与伦比的性能潜力。使用时建议密切关注引擎版本更新，以获取最新的修复和优化。

**警告**：作为实验性功能，其 API 在未来版本中**可能发生破坏性变更**。在生产环境中使用时，需做好相应的代码维护准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() (暂无独立文档页，可参考引擎内置的 Mass Entity 相关文档)
- [测试用例]() (插件自身包含 `MassGameplayTestSuite` 模块，但具体文件路径未在本次分析中提供)