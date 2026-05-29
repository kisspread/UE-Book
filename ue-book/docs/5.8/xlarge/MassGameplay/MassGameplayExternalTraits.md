# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件是建立在 Unreal Engine 的 Entity Component System (ECS) 框架 —— **MassEntity** 之上的**高级游戏玩法框架**。它的核心目的是解决在大型开放世界或 RTS（即时战略）等游戏中，需要同时模拟和渲染**成千上万个**具有相似行为模式的实体（如人群、NPC 群、军队单位）时的性能和管理问题。

与传统的 Actor 模型相比，MassGameplay 通过数据驱动的方式，将实体的状态（Fragment）和行为逻辑（Processor）分离，并利用 MassEntity 框架的内存布局和批量处理能力，极大地提升了处理海量实体时的 CPU 性能和内存访问效率。它提供了从生成、表示、移动、复制到调试的完整解决方案。

## 使用场景

- **开放世界游戏**：你需要一个充满生气的城市，街道上有成百上千个拥有独立 AI 和路径的市民。
- **即时战略游戏 (RTS)**：你的游戏需要同时控制成千上万的士兵、车辆单位进行寻路、战斗和集结。
- **大型模拟游戏**：你在制作一个农场模拟或生态系统模拟，需要大量动态生物（如羊群、鸟群）以自然的行为模式活动。
- **任何需要“数量即质量”视觉效果的场景**：例如需要渲染大量粒子化但具有简单逻辑的敌人（如丧尸群）或魔法特效。

**不推荐的场景**：如果你的游戏只需要少量（例如少于 100 个）高度复杂、具有独特动画和深度交互的 AI 角色，传统的 Actor 和 Behavior Tree 方案可能更简单直接。

## 蓝图用法

MassGameplay 主要通过 `MassSpawner` 组件和各种 Processor 配置来与蓝图交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据指定的 `MassEntityConfig` 和数量，在指定位置批量生成实体。 | `UMassSpawnerSubsystem` |
| `Get Entity Handle` | 根据一个 `FMassEntityHandle`（可从其他组件或追踪结果获取）获取实体句柄。 | `UMassEntitySubsystem` |
| `Set Entity Transform` | 设置指定实体的变换（位置、旋转、缩放）。 | `UMassEntitySubsystem` |
| `Kill Entity` | 销毁一个指定的实体。 | `UMassEntitySubsystem` |
| `Get Mass Entity Manager` | 获取全局的 `UMassEntitySubsystem` 实例。 | `UGameInstanceSubsystem` |

### 使用示例（蓝图描述）

1.  **准备阶段**：创建一个基于 `MassEntityConfig` 的资产（Data Asset）。在该资产中，配置一个或多个 `MassEntityTrait`（如 `MassRepresentationTrait` 用于视觉表现，`MassMovementTrait` 用于移动）。
2.  **生成实体**：在你的 Actor（如 `MassSpawnerActor`）上添加 `MassSpawnerComponent`。将之前创建的 `MassEntityConfig` 资产赋予它。调用 `Spawn Entities` 节点，设置生成数量和位置，即可批量生成实体。
3.  **驱动行为**：实体的行为由其配置的 `MassProcessor` 驱动。你通常不直接在蓝图中写每个实体的逻辑，而是通过配置 Trait 和 Processor 来定义数据（如移动速度 Fragment）和逻辑（如移动 Processor）。蓝图可以用来触发批量操作，例如向某个区域的所有实体发送一个“惊吓”事件（通过修改 Fragment 数据）。

## C++ 用法

### 头文件引入

```cpp
#include "MassEntityTypes.h" // 包含基础的 Fragment, Chunk 等定义
#include "MassSpawnerTypes.h" // 包含 MassEntityConfig 等类型
#include "MassProcessor.h" // 定义 Processor 基类
```

### 基本用法

自定义一个 Fragment（数据组件）和一个 Trait（行为组件）。

```cpp
// MyHealthFragment.h
#pragma once
#include "MassEntityTypes.h"

USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere)
    float CurrentHealth = 100.0f;
};

// MyDumbAITrait.h
#pragma once
#include "MassEntityTraitBase.h"
#include "MyHealthFragment.h" // 引用我们自定义的 Fragment

UCLASS()
class UMyDumbAITrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        // 向实体模板添加我们的健康 Fragment
        BuildContext.AddFragment<FMyHealthFragment>();
        // 还可以添加其他逻辑需要的 Fragment，例如移动信息
    }
};
```

### 进阶用法

编写一个简单的 Processor 来处理拥有 `FMyHealthFragment` 的实体。

```cpp
// MyHealthProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyHealthFragment.h"

UCLASS()
class UMyHealthProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyHealthProcessor();
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MyHealthProcessor.cpp
#include "MyHealthProcessor.h"
#include "MassCommonTypes.h"

UMyHealthProcessor::UMyHealthProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::AllNetModes;
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::Processor::Names::Avoidance); // 指定执行顺序
}

void UMyHealthProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite); // 声明需要读写 FMyHealthFragment
}

void UMyHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合查询条件的实体 Chunk
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        // 获取 Chunk 中所有 FMyHealthFragment 的数组
        const TArrayView<FMyHealthFragment> HealthList = Context.GetMutableFragmentView<FMyHealthFragment>();

        // 批量处理逻辑：每帧微量恢复生命值
        for (FMyHealthFragment& Health : HealthList)
        {
            Health.CurrentHealth += 0.01f;
            Health.CurrentHealth = FMath::Clamp(Health.CurrentHealth, 0.0f, 100.0f);
        }
    });
}
```

## Demo 示例

一个最小的、可运行的示例，展示如何定义实体、生成它们并用 Processor 简单驱动。

```cpp
// MyMinimalEntity.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MassEntitySubsystem.h" // 用于访问 Manager

// 简单的数据 Fragment
USTRUCT()
struct FVelocityFragment : public FMassFragment
{
    GENERATED_BODY()
    FVector Velocity = FVector::ForwardVector * 100.0f;
};

// Trait：向实体添加移动能力
UCLASS()
class UMoveableTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override
    {
        BuildContext.AddFragment<FVelocityFragment>();
    }
};

// Processor：根据速度移动实体
UCLASS()
class UMoveProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMoveProcessor();
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
private:
    FMassEntityQuery EntityQuery;
};

// MyMinimalEntity.cpp
#include "MyMinimalEntity.h"
#include "MassMovementFragments.h" // 用于 FTransformFragment

UMoveProcessor::UMoveProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::AllNetModes;
}

void UMoveProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FVelocityFragment>(EMassFragmentAccess::ReadOnly);
}

void UMoveProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const TConstArrayView<FVelocityFragment> VelocityList = Context.GetFragmentView<FVelocityFragment>();

        const float DeltaTime = Context.GetDeltaTimeSeconds();

        for (int32 i = 0; i < TransformList.Num(); ++i)
        {
            FTransform& Transform = TransformList[i].GetMutableTransform();
            const FVector& Velocity = VelocityList[i].Velocity;
            // 简单的移动：位置 += 速度 * 时间
            Transform.AddToTranslation(Velocity * DeltaTime);
        }
    });
}
```

**如何使用上述代码**：
1.  在项目的 `.Build.cs` 文件中添加对 `MassEntity`, `MassGameplay` 的模块依赖。
2.  创建一个基于 `MassEntityConfig` 的蓝图资产，添加 `UMoveableTrait`。
3.  在场景中放置一个 `AMassSpawnerActor`，设置它的配置资产为上一步创建的蓝图资产，并设置生成数量（如 1000）。
4.  游戏运行后，`UMoveProcessor` 会自动被加载并执行，驱动所有带有 `FVelocityFragment` 的实体进行移动。

## 模块依赖

使用 MassGameplay 插件，你的项目模块需要依赖其中的子模块。以下是一些关键的独特依赖（省略了 Core, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的基石，提供 ECS 核心框架、实体管理、Fragment 和 Processor 基础。 |
| `MassRepresentation` | 处理实体的视觉表现，如将 MassEntity 转换为 Actor、ISM (Instance Static Mesh) 或动态网格体。 |
| `MassSpawner` | 提供批量生成实体的基础设施和蓝图组件。 |
| `MassMovement` | 实现基于 Mass 的移动系统，包括速度、转向和简单的物理。 |
| `MassReplication` | 支持将 MassEntity 的状态通过网络进行复制，用于多人游戏。 |
| `MassLOD` | 实现细节层次（LOD）系统，根据距离和重要性动态调整实体的更新频率和表示方式，优化性能。 |
| `MassEQS` | 将 MassEntity 与环境查询系统（EQS）集成，允许 AI 基于 Mass 数据做出决策。 |
| `MassSmartObjects` | 将 MassEntity 与 SmartObject 系统集成，允许实体使用场景中的交互点。 |
| `MassCommon` | 包含被多个子模块共享的常用数据类型和 Fragment。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了 MassAgentComponent 之前的改动。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 等待 Actor 准备就绪后才关闭 ISM 表示，修复切换逻辑。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 人群中对非傀儡 Actor 的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 `TMassLODCalculator` 中基于查看器的 LOD 路径里的一系列原有 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两处手动计算的 `bDoKeepActorExtraFrame` 切换为使用新的 UE::M 相关函数。 |

### 维护评价

**综合评价：实验性但活跃维护。**

- **状态**：插件标记为 `IsExperimentalVersion = true` 且默认不启用（`EnabledByDefault = false`），表明 Epic 官方认为其 API 和功能仍处于实验阶段，未来可能发生不兼容的变更。
- **活跃度**：根据最近的 Git 历史（截至 2026 年 5 月），该插件仍在被**积极开发和维护**中。更新内容集中在修复 Bug、优化性能（如 Representation 和 LOD）和改进现有功能。
- **推荐**：如果你正在开发一个**需要处理海量实体**的**大型项目**，并且愿意接受实验性 API 可能带来的维护成本，那么 MassGameplay 是**强烈推荐**的核心技术栈。对于小型或中等规模的项目，或者实体数量不多的情况，使用传统的 Actor 方案会更简单。

**警告**：由于其实验性标签，在商业项目中使用前，请评估升级引擎版本时可能需要的适配工作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mass-gameplay-in-unreal-engine/) (基于 MassEntity 和 MassGameplay 的官方概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Tests)