# MassMovement

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassMovement 是 MassGameplay 插件中的一个核心模块，它为基于 MassEntity 的大规模智能体（Agent）模拟系统提供移动能力。它解决的核心问题是：在传统 Actor 系统中，为成千上万个实体（如 NPC、生物、单位）实现高效、可配置且多样化的移动逻辑会带来巨大的性能开销。

该模块通过 ECS（实体-组件-系统）架构，将移动相关的数据（如速度、力、移动风格）作为“片段”（Fragment）附加到实体上，并通过专门的“处理器”（Processor）进行批量、高效的更新。它允许开发者定义不同的“移动风格”（Movement Style），并为每个实体根据其唯一 ID 确定性地分配一个速度，从而在保证性能的同时，实现群体移动的自然多样性。

## 使用场景

- **大规模 RTS 游戏**：你需要控制屏幕上成百上千个单位的移动，每个单位可能有不同的移动速度和转向行为。
- **开放世界游戏**：你需要模拟大量 NPC 或生物在世界中的巡逻、漫游或追逐行为。
- **模拟游戏**：你需要模拟大量独立实体（如人群、车辆、动物）的物理移动和交互。
- **任何需要高性能群体移动逻辑的场景**：当传统的 `CharacterMovementComponent` 或 `Pawn` 系统成为性能瓶颈时，MassMovement 提供了一个基于数据的替代方案。

## 蓝图用法

MassMovement 模块主要通过其 Trait 和 Processor 在蓝图中使用。核心的移动逻辑由处理器在后台自动执行，开发者主要通过配置 Trait 和移动风格来影响行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ApplyForce` | 向实体施加一个力，影响其期望速度。 | `UMassApplyForceProcessor` |
| `ApplyMovement` | 根据实体的期望速度更新其实际位置。 | `UMassApplyMovementProcessor` |
| `GetMovementStyle` | 根据移动风格引用获取对应的风格参数。 | `UMassMovementSettings` |
| `GenerateDesiredSpeed` | 根据移动风格和实体唯一 ID 生成一个确定性的期望速度。 | `FMassMovementParameters` |

### 使用示例（蓝图描述）

1.  **配置移动风格**：
    *   在项目设置中找到 `Mass Movement` 设置项。
    *   添加一个或多个 `Movement Style`（例如 “Walk”, “Run”）。
    *   为每个风格配置 `Desired Speeds` 数组，设置不同的速度值、变化范围和概率。

2.  **为实体添加移动能力**：
    *   在你的实体模板（Entity Template）中，添加 `Movement` Trait。
    *   在该 Trait 的属性中，选择一个 `Movement Style` 引用（如 “Walk”）。
    *   （可选）添加 `Simple Movement` Trait 以启用最基础的代码驱动移动。
    *   （可选）添加 `Velocity Randomizer` Trait 以在实体生成时随机初始化其速度。

3.  **施加力（蓝图）**：
    *   在需要影响实体移动的逻辑中（如行为树任务、自定义处理器），获取实体的 `FMassForceFragment`。
    *   将计算出的力向量设置到该片段的 `Value` 属性上。`UMassApplyForceProcessor` 会在下一帧自动将此力应用到实体的期望速度上。

## C++ 用法

### 头文件引入

```cpp
#include "MassMovementFragments.h"
#include "MassMovementTypes.h"
#include "MassMovementProcessors.h"
#include "MassMovementTrait.h"
```

### 基本用法

以下示例展示如何创建一个简单的自定义移动处理器，它查询所有具有速度和力片段的实体，并将力应用到速度上。

```cpp
// MyMovementProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MyMovementProcessor.generated.h"

UCLASS()
class UMyMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMovementProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyMovementProcessor.cpp
#include "MyMovementProcessor.h"
#include "MassMovementFragments.h"

UMyMovementProcessor::UMyMovementProcessor()
{
    // 设置处理器执行顺序，确保在力计算之后、位置更新之前执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::ApplyForce);
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::ApplyMovement);
}

void UMyMovementProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询所有同时拥有速度片段和力片段的实体
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassForceFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMassCodeDrivenMovementTag>(EMassFragmentPresence::All);
}

void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量遍历所有匹配的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取实体数据视图
        const TConstArrayView<FMassForceFragment> ForceList = Context.GetFragmentView<FMassForceFragment>();
        const TArrayView<FMassVelocityFragment> VelocityList = Context.GetMutableFragmentView<FMassVelocityFragment>();

        // 遍历当前块中的所有实体
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 将力应用到速度上 (简化示例，实际可能需要考虑质量和时间步长)
            VelocityList[i].Value += ForceList[i].Value;
            // 清除已应用的力
            // ForceList[i].Value = FVector::ZeroVector; // 注意：需要可写访问
        }
    });
}
```
*（来源：基于 `UMassApplyForceProcessor` 和 `UMassApplyMovementProcessor` 的实现模式推断）*

### 进阶用法

结合移动风格（Movement Style）和实体唯一 ID 来分配多样化的速度。

```cpp
// 在某个处理器或函数中
void AssignSpeedBasedOnStyle(FMassMovementParameters& MovementParams, const FMassMovementStyleRef& StyleRef, int32 EntityUniqueID)
{
    // 根据风格和实体ID生成一个确定性的速度
    float DesiredSpeed = MovementParams.GenerateDesiredSpeed(StyleRef, EntityUniqueID);
    
    // 将生成的速度设置到实体的期望移动片段中
    // FMassDesiredMovementFragment& DesiredMovement = ...;
    // DesiredMovement.DesiredVelocity = DesiredMovement.DesiredVelocity.GetSafeNormal() * DesiredSpeed;
}
```
*（来源：`FMassMovementParameters::GenerateDesiredSpeed` 函数逻辑）*

## Demo 示例

一个最小的自定义移动处理器，它查询所有带有 `FMassSimpleMovementTag` 的实体，并以恒定速度向前移动。

```cpp
// SimpleMovementDemoProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "SimpleMovementDemoProcessor.generated.h"

UCLASS()
class USimpleMovementDemoProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    USimpleMovementDemoProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// SimpleMovementDemoProcessor.cpp
#include "SimpleMovementDemoProcessor.h"
#include "MassMovementFragments.h"
#include "Example/MassSimpleMovementTrait.h" // 包含 FMassSimpleMovementTag

USimpleMovementDemoProcessor::USimpleMovementDemoProcessor()
{
    // 设置执行顺序
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::ProcessorGroupNames::ApplyForce);
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::ApplyMovement);
}

void USimpleMovementDemoProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 查询所有带有简单移动标签和速度片段的实体
    EntityQuery.AddTagRequirement<FMassSimpleMovementTag>(EMassFragmentPresence::All);
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
}

void USimpleMovementDemoProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    const float MoveSpeed = 100.0f; // 100 cm/s
    const FVector ForwardDirection = FVector::ForwardVector; // 世界坐标系前向

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        const TArrayView<FMassVelocityFragment> VelocityList = Context.GetMutableFragmentView<FMassVelocityFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 为每个实体设置一个恒定的向前速度
            VelocityList[i].Value = ForwardDirection * MoveSpeed;
        }
    });
}
```

## 模块依赖

MassMovement 模块自身的依赖相对简单，但作为 MassGameplay 插件的一部分，其完整功能依赖于插件内的其他模块。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 Mass Entity 框架，提供实体、片段、处理器等基础架构。 |
| `MassCommon` | 提供 Mass 系统通用的类型、工具和调试支持。 |
| `MassSpawner` | 负责实体的生成和模板管理，移动能力通常在生成时通过 Trait 添加。 |
| `MassRepresentation` | 处理实体的视觉表现（如 Actor、ISM），移动逻辑需要与之协同更新位置。 |
| `MassLOD` | 实现基于距离的细节层次（LOD）管理，移动处理器需要根据 LOD 状态决定是否执行。 |

## 维护状态

### 近期更新

```
- 2024-05-15 0ebe081b7ad3 [MassGameplay] * Fixed non unity compile errors
- 2024-05-14 ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2024-05-13 b1980471196e [Mass] Minor MassEntityManager cleanup, including removing some header inclusion
```

### 维护评价

MassMovement 模块创建于 2021 年，作为实验性功能（`IsExperimentalVersion: true`）的一部分。从最近的提交记录看，最后一次实质性功能更新未知，近期的提交主要是编译错误修复和代码清理等维护性工作。

**综合评价**：
- **状态**：实验性功能，仍在维护中，但近期无重大功能迭代。
- **活跃度**：维护不活跃。最近的更新是基础的代码维护，没有新特性或重大改进。
- **风险**：作为实验性 API，其接口和功能在未来版本中可能发生不兼容的变更。
- **推荐**：适用于对大规模实体移动有迫切性能需求且愿意承担实验性 API 风险的项目。对于新项目，建议评估其与项目需求的匹配度，并关注 Epic 官方的更新公告。不建议在追求长期稳定性的核心项目中作为唯一移动方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassMovement)
- [官方文档]()
- [测试用例]()