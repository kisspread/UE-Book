# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源与示例） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途
MassGameplay 是 Unreal Engine 中基于 **MassEntity** ECS（实体组件系统）框架的**上层应用插件**。它的核心目的是将底层的、高性能的 MassEntity 框架扩展为可用于游戏玩法的具体功能模块，专门用于实现**大规模的实体（Agent）模拟和管理**。它解决了在开放世界、大规模人群、战略游戏等场景下，需要高效管理成百上千个相似游戏对象（如NPC、敌人、动物、车辆）的需求，通过批处理和数据导向设计极大提升了性能。该插件并非提供一个单一的“人群模拟器”，而是一个模块化工具集，开发者可以根据需要组合这些模块来构建自己的大规模实体系统。

## 使用场景
- 你需要在一个开放世界中生成和管理成千上万的NPC或野生动物，且对性能有极高要求 → 组合使用 `MassSpawner`, `MassRepresentation`, `MassLOD`, `MassMovement` 模块。
- 你在开发一个塔防或战略游戏，场上有大量同类型的敌人或单位 → 使用 `MassEntity` 作为基础，并利用 `MassActors` 将实体与 Actor 关联。
- 你需要为海量实体实现复杂的群体寻路和移动逻辑 → 使用 `MassMovement` 和 `MassCharacterTrajectory`。
- 你需要为大量实体实现不同距离下的不同表现（如远距离用Impostor，近距离用完整模型）→ 使用 `MassRepresentation` 和 `MassLOD`。
- 你需要将大量的实体通过网络同步给多人游戏的客户端 → 使用 `MassReplication`。

## 蓝图用法
该插件大部分是底层框架和运行时逻辑，蓝图接口主要集中在实体生成、组件控制和调试方面。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnEntity` | 在指定位置生成一个Mass实体，并为其添加配置好的片段（Fragment）。 | `UMassSpawnerSubsystem` |
| `GetEntityForActor` | 获取与一个已存在的Actor相关联的Mass实体句柄。 | `UMassSpawnerSubsystem` |
| `SetEntityTransform` | 设置一个Mass实体的世界变换。 | `UMassAgentComponent` |
| `SetEntityVelocity` | 设置一个Mass实体的移动速度。 | `UMassAgentComponent` |
| `RequestDespawn` | 请求销毁一个Mass实体。 | `UMassAgentComponent` |
| `EnableVisualization` / `DisableVisualization` | 控制实体的视觉表示（如是否显示Actor或StaticMesh）。 | `UMassRepresentationSubsystem` |

### 使用示例（蓝图描述）
1.  **生成一个实体**：
    *   调用 `GetMassSpawnerSubsystem` 获取子系统。
    *   创建一个 `FMassSpawnedEntityData` 结构体，设置其 `EntityConfig`（引用一个配置了所需片段的DataAsset）和 `Transform`。
    *   调用子系统的 `SpawnEntity` 节点，传入上面的数据结构。
2.  **控制一个实体**：
    *   通过 `GetEntityForActor` 节点获取实体句柄。
    *   使用 `UMassAgentComponent` 上的 `SetEntityTransform` 或 `SetEntityVelocity` 节点直接修改其状态。

## C++ 用法
用法核心在于定义自己的 **片段（Fragment）**、**标签（Tag）** 和 **处理器（Processor）**。

### 头文件引入
```cpp
#include "MassEntityTypes.h" // 基础类型
#include "MassProcessor.h"   // 处理器基类
#include "MassSpawnerSubsystem.h" // 生成实体
```

### 基本用法
定义并使用自定义片段。
```cpp
// MyFragments.h
#pragma once
#include "MassEntityTypes.h"

// 定义一个速度片段
USTRUCT()
struct FMyVelocityFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY()
    FVector Value = FVector::ZeroVector;
};
```

### 进阶用法
创建一个处理器来移动实体。
```cpp
// MyMovementProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MassCommonFragments.h" // 包含FTransformFragment
#include "MyFragments.h"

UCLASS()
class UMyMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMovementProcessor();
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询：需要FTransformFragment和FMyVelocityFragment的实体
    FMassEntityQuery EntityQuery;
};

// MyMovementProcessor.cpp
#include "MyMovementProcessor.h"
#include "MassEntityTypes.h"

UMyMovementProcessor::UMyMovementProcessor()
{
    // 设置处理器为运行时执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
}

void UMyMovementProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMyVelocityFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.RegisterWithProcessor(*this);
}

void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合查询条件的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMyVelocityFragment> Velocities = Context.GetFragmentView<FMyVelocityFragment>();
        const TArrayView<FTransformFragment> Transforms = Context.GetMutableFragmentView<FTransformFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            Transforms[i].GetMutableTransform().AddToTranslation(Velocities[i].Value * Context.GetDeltaTimeSeconds());
        }
    });
}
```

## Demo 示例
一个最小化的实体定义和自定义处理器。

```cpp
// DemoFragments.h
#pragma once
#include "MassEntityTypes.h"

// 标识一个“敌人”实体
USTRUCT()
struct FEnemyTag : public FMassTag
{
    GENERATED_BODY()
};

// 存储生命值
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    UPROPERTY()
    float Health = 100.0f;
};
```

```cpp
// DemoHealthProcessor.h
#pragma once
#include "MassProcessor.h"

UCLASS()
class UDemoHealthProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UDemoHealthProcessor();

private:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery HealthQuery;
};

// DemoHealthProcessor.cpp
#include "DemoHealthProcessor.h"
#include "MassEntityTypes.h"
#include "DemoFragments.h"

UDemoHealthProcessor::UDemoHealthProcessor()
{
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Logic;
}

void UDemoHealthProcessor::ConfigureQueries()
{
    HealthQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    HealthQuery.AddTagRequirement<FEnemyTag>(EMassFragmentPresence::All);
    HealthQuery.RegisterWithProcessor(*this);
}

void UDemoHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    HealthQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FHealthFragment> Healths = Context.GetMutableFragmentView<FHealthFragment>();
        // 模拟每帧扣血
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            Healths[i].Health -= 1.0f * Context.GetDeltaTimeSeconds();
        }
    });
}
```

## 模块依赖
该插件的模块依赖MassEntity框架，并部分依赖编辑器工具。普通游戏模块主要依赖运行时模块。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心ECS框架，提供实体、片段、处理器、系统管理等基础功能。 |
| `MassEntityEditor` | 为MassEntity相关的资产（如EntityConfig）提供编辑器支持。 |
| `SmartObjectsModule` | `MassSmartObjects` 模块的依赖，用于实体与智能对象交互。 |
| `GameplayInteractionsModule` | `MassSmartObjects` 模块的依赖，用于具体的交互逻辑。 |
| `AIModule` | `MassEQS` 模块的依赖，用于将环境查询系统（EQS）与Mass实体集成。 |
| `GeometryCollectionEngine` | `MassRepresentation` 模块的依赖，用于表示层中的几何体集合支持。 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回退了之前对 MassAgentComponent 的更改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 在关闭实例化静态网格体(ISM)前等待Actor准备就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了Mass人群中非傀儡Actor的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复了 `TMassLODCalculator` 中逐观察者LOD路径的一系列已知缺陷。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [Mass 表示层] 将两处手动计算的 `bDoKeepActorExtraFrame` 替换为使用新的 UE::M 接口。 |

### 维护评价
- **创建时间与年龄**：该插件创建于2021年9月，已有约4年历史，但仍被标记为**实验性**(`IsExperimentalVersion: true`)。
- **近期更新频率**：近期更新非常频繁（2026年5月有多次提交），但内容**集中于修复已知的Bug和改进表示层（Representation）**，例如处理Actor、LOD、ISM等具体问题，而非添加全新的大规模功能。
- **活跃度**：尽管是实验性的，但从提交记录看**仍在活跃维护和调优中**，尤其在表现层和与传统Actor系统的集成方面。
- **已知问题与限制**：作为实验性插件，其API和行为可能不稳定。主要功能模块（如Spawning, Movement, Representation）虽可用，但开发者需要准备应对未来的变化和潜在的复杂调试问题。
- **推荐使用**：**谨慎推荐**。它是一个功能强大且性能卓越的框架，非常适合需要处理海量实体的项目。但由于其**实验性状态**，建议仅在项目对大规模实体模拟有硬性需求，且团队有能力消化其复杂性和潜在风险时采用。对于常规游戏玩法，传统的Actor组件或HISM方案可能更易用、更稳定。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （当前为空，可参考 Epic 官方学习资源和社区教程）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)