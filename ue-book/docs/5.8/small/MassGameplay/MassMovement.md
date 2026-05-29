# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏性 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例Trait和配置） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 UE5 质量实体（MassEntity）ECS 框架在游戏玩法层面的高级实现。它构建于核心 MassEntity 系统之上，专注于解决使用大规模智能体（Agent）进行游戏时的复杂性问题。它提供了一套模块化、可组合的 Trait（特征）和处理器（Processor），用于控制智能体的移动、表示、复制、LOD（细节层次）以及与世界智能对象的交互。

该插件的核心目标是让开发者能够高效地模拟和控制成千上万个游戏实体（如人群、NPC、RTS单位），而无需为每个实体都创建一个完整的 Actor。它抽象了底层数据布局和并行处理细节，提供了更易于使用的“特征”系统来定义实体的行为和外观。

## 使用场景

- **大型人群模拟**：你需要模拟城市街道、体育场或战场上的大量人群，每个个体都有独立的行为和外观。
- **即时战略（RTS）游戏**：你需要高效地控制数百甚至数千个游戏单位（士兵、车辆）的寻路、避障和状态同步。
- **开放世界填充**：你需要动态生成大量野生生物、平民NPC或载具来丰富世界，同时保持高性能。
- **需要精细LOD控制的场景**：你需要根据智能体与玩家的距离，动态切换其表现形式（如从骨骼网格体降级为静态网格体或完全不可见）。

## 蓝图用法

通过组合不同的 Trait（特征）来定义实体模板，从而在蓝图中创建具有复杂行为的实体类型。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MassMovementTrait` | 为实体添加基础的移动能力，包括速度、加速度等参数。 | `UMassMovementTrait` |
| `SpringMovementTrait` | 为实体添加基于弹簧阻尼器的平滑移动，用于插值位置和朝向，使移动更自然。 | `USpringMovementTrait` |
| `MassSimpleMovementTrait` | 提供最简单的移动实现，直接将期望速度应用到位置。 | `UMassSimpleMovementTrait` |
| `MassVelocityRandomizerTrait` | 一个示例Trait，在实体创建时为其赋予一个随机速度。 | `UMassVelocityRandomizerTrait` |

### 使用示例（蓝图描述）

1.  **创建基础移动实体**：在Mass Entity模板资产中，添加 `MassMovementTrait`。在其属性中设置 `MaxSpeed` 和 `MaxAcceleration`。这将创建一个拥有基本移动能力的实体。
2.  **创建平滑移动实体**：在模板中添加 `SpringMovementTrait`。调整 `SpringSettings` 中的 `VelocitySmoothingTime` 和 `FacingSmoothingTime`，使移动过渡更平滑。该Trait常与动画系统配合使用。
3.  **组合示例**：你可以同时为一个实体添加 `MassMovementTrait` 和 `SpringMovementTrait`。`SpringMovementTrait` 的处理器将读取 `MassMovementTrait` 输出的期望速度和朝向，并进行平滑处理。

## C++ 用法

基于MassGameplay的开发通常涉及两方面：1) 配置现有Trait；2) 创建自定义的处理器和Trait。

### 头文件引入

```cpp
#include "MassMovement.h"
```

### 基本用法

**创建并配置移动参数 (C++ 中配置 Trait 属性)**

```cpp
// 在某个构建模板的函数中（如 UMassEntityTraitBase::BuildTemplate）
UMassMovementTrait* MovementTrait = NewObject<UMassMovementTrait>(GetTransientPackage());
FMassMovementParameters& MovementParams = MovementTrait->Movement;
MovementParams.MaxSpeed = 300.0f; // 最大速度 300 厘米/秒
MovementParams.MaxAcceleration = 400.0f;
MovementParams.bIsCodeDrivenMovement = true; // 由代码直接控制速度
BuildContext.AddTrait(*MovementTrait);
```

**示例来自**：基于 `UMassMovementTrait::BuildTemplate` 的典型用法。

### 进阶用法

**创建一个自定义移动处理器**

你可以继承 `UMassProcessor` 来创建自定义的移动逻辑，例如实现一个追踪玩家的处理器。

```cpp
// 头文件
UCLASS()
class UMyChasePlayerProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyChasePlayerProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
private:
    FMassEntityQuery EntityQuery;
};

// CPP文件
UMyChasePlayerProcessor::UMyChaseProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    // 设置执行顺序，在 MassMovement 处理器之后
    ProcessingPhase = EMassProcessingPhase::PostPhysics;
}

void UMyChasePlayerProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询同时具有移动参数片段和期望移动片段的实体
    EntityQuery.AddRequirement<FMassMovementParameters>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassDesiredMovementFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddConstSharedRequirement<FMassMovementParameters>(EMassFragmentPresence::All);
}

void UMyChasePlayerProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 假设有一个获取玩家位置的全局函数
    const FVector PlayerLocation = GetPlayerLocation();

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMassMovementParameters> MovementParamsList = Context.GetFragmentView<FMassMovementParameters>();
        const TArrayView<FMassDesiredMovementFragment> DesiredMovementList = Context.GetMutableFragmentView<FMassDesiredMovementFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 简单的追踪逻辑：朝向玩家
            FMassDesiredMovementFragment& DesiredMovement = DesiredMovementList[i];
            const FVector ToPlayer = PlayerLocation - Context.GetEntityLocation(Context.GetEntity(i));
            DesiredMovement.DesiredVelocity = ToPlayer.GetSafeNormal() * MovementParamsList[i].MaxSpeed;
            DesiredMovement.DesiredFacing = ToPlayer.ToOrientationQuat();
        }
    });
}
```

## Demo 示例

一个完整的自定义移动处理器示例：**“缓慢转向移动”**。该处理器让实体以缓慢的速度转向指定的目标点。

**SlowTurnMovementProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MassMovementFragments.h"
#include "SlowTurnMovementProcessor.generated.h"

UCLASS()
class USlowTurnMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    USlowTurnMovementProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;

    // 可调整的转向速度（度/秒）
    UPROPERTY(EditAnywhere, Category = "Movement")
    float TurnSpeed = 30.0f;
};
```

**SlowTurnMovementProcessor.cpp**
```cpp
#include "SlowTurnMovementProcessor.h"
#include "MassEntityUtils.h"

USlowTurnMovementProcessor::USlowTurnMovementProcessor()
{
    bAutoRegisterWithProcessingPhases = true;
    ExecutionFlags = static_cast<int32>(EProcessorExecutionFlags::All);
    ProcessingPhase = EMassProcessingPhase::DoNotSet;
    // 执行顺序在标准移动处理之前
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::Movement);
}

void USlowTurnMovementProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassDesiredMovementFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddConstSharedRequirement<FMassMovementParameters>(EMassFragmentPresence::All);
}

void USlowTurnMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        const TConstArrayView<FTransformFragment> TransformList = Context.GetFragmentView<FTransformFragment>();
        const TConstArrayView<FMassMovementParameters> ParamsList = Context.GetFragmentView<FMassMovementParameters>();
        const TArrayView<FMassDesiredMovementFragment> DesiredMovementList = Context.GetMutableFragmentView<FMassDesiredMovementFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FTransform& EntityTransform = TransformList[i].GetTransform();
            FMassDesiredMovementFragment& DesiredMovement = DesiredMovementList[i];
            const float MaxSpeed = ParamsList[i].MaxSpeed;

            // 1. 计算到目标的方向（这里假设目标是某个固定的点，实际项目中可能来自另一个Fragment）
            const FVector TargetLocation(1000.f, 1000.f, 0.f);
            const FVector DesiredDirection = (TargetLocation - EntityTransform.GetLocation()).GetSafeNormal2D();

            // 2. 获取当前朝向和计算新朝向
            const FRotator CurrentRotation = EntityTransform.GetRotation().Rotator();
            const FRotator DesiredRotation = DesiredDirection.Rotation();
            const FRotator NewRotation = FMath::RInterpConstantTo(CurrentRotation, DesiredRotation, Context.GetDeltaTimeSeconds(), TurnSpeed);

            // 3. 将旋转应用到速度方向，并设置期望移动
            const FVector NewForward = NewRotation.Vector();
            DesiredMovement.DesiredVelocity = NewForward * MaxSpeed;
            DesiredMovement.DesiredFacing = NewRotation.Quaternion();
        }
    });
}
```

## 模块依赖

`MassGameplay` 插件内部包含大量子模块。对于开发者而言，主要依赖其暴露的公共头文件。该插件本身没有特别的外部模块依赖。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心基础，提供ECS框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对MassAgent组件的先前修改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [表现] 在关闭实例化静态网格体(ISM)前等待Actor就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了Mass人群中非傀儡Actor的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [表现] 修复了LOD计算器中按查看者计算LOD路径的一系列已有bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [表现] 将两处手动计算的Actor额外帧保留逻辑改为使用新的UE::M框架接口。 |

### 维护评价

- **活跃维护**：从提交记录看，该插件在 **2026年5月** 仍有频繁的功能改进和bug修复，主要集中在 `MassRepresentation` 和 `MassLOD` 模块，说明 Epic Games 内部仍在积极开发和维护此系统。
- **实验性状态**：尽管代码活跃，但 `.uplugin` 文件仍标记为 `IsExperimentalVersion: true` 且 `VersionName` 仅为 `0.4`。这表明该插件虽然功能强大，但 **API和功能可能在未来版本中发生变化**，不建议在追求长期稳定的生产项目中作为核心依赖。
- **推荐**：**有条件推荐**。非常适合对大规模实体模拟有强烈需求、且团队有能力跟进API变化的技术型项目。对于一般规模的项目，应谨慎评估引入复杂性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)