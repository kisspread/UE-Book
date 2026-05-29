# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 群体玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Epic 基于 MassEntity（实体组件系统，ECS）框架构建的一套大规模 AI 智能体（Agent）模拟实现。它解决的核心问题是：如何在保持高帧率的同时，模拟成千上万个具有独立行为、移动和外观的智能体。

此插件在底层 `MassEntity` 的数据驱动和并行处理能力之上，为常见的游戏玩法需求提供了开箱即用的解决方案，包括：
- **大规模移动**：通过物理或动画驱动，高效更新海量实体的位置和朝向。
- **可扩展表现**：根据距离（LOD）动态切换实体的表现形式（如网格体、动画、物理模拟）。
- **网络复制**：优化大量实体状态在客户端和服务器之间的同步。
- **智能物体交互**：让大量实体能与场景中的“智能物体”（如掩体、载具）进行交互。
- **空间查询与导航**：集成环境查询系统（EQS）以支持复杂的寻路和决策。

其存在意义在于，传统的 `AActor` 和行为树（Behavior Tree）方案在处理数千个单位时性能开销巨大，而 MassGameplay 利用 ECS 的架构，通过内存布局优化和批处理，将模拟性能提升了数个量级。

## 使用场景

- **你在开发大型多人在线游戏（MMO）或大逃杀游戏**：需要同时模拟大量玩家角色、AI敌人或中立生物 → 使用 MassGameplay 驱动这些实体的移动、动画和网络同步。
- **你在制作一个开放世界游戏**：需要一个充满动态NPC和野生动物的活生生的世界，且不能严重影响性能 → 用 MassGameplay 来管理这些非关键但数量庞大的实体。
- **你在开发塔防、策略或即时战略（RTS）游戏**：屏幕上可能同时存在数百甚至数千个战斗单位 → 用 MassGameplay 作为其底层模拟引擎。
- **你需要为 MassEntity 系统快速添加游戏玩法功能**：不想从零开始编写移动、表现、复制等处理器 → 直接使用或继承 MassGameplay 提供的 Trait 和 Processor。

## 蓝图用法

MassGameplay 的功能主要通过 **MassEntity Trait** 在资产配置中添加，而不是通过蓝图节点动态调用。核心配置在 `UMassEntityConfig` 资产中完成。

### 核心 Trait（在实体配置中添加）

| Trait（显示名） | 说明 | 所在类 |
|---|---|---|
| `Movement` | 为实体添加基础移动能力（速度、加速度、转向等），并配置相关的处理器。 | `UMassMovementTrait` |
| `Spring Movement` | 为实体添加平滑的弹簧阻尼移动，可消除急停急转，使运动更自然。 | `USpringMovementTrait` |
| `Simple Movement` | 一个极简的移动示例Trait，直接将速度应用到位置上，无平滑处理。 | `UMassSimpleMovementTrait` |
| `Velocity Randomizer` | 为新生成的实体随机设置初始速度。 | `UMassVelocityRandomizerTrait` |

### 使用示例（蓝图描述）

1.  创建一个 `UMassEntityConfig` 蓝图资产。
2.  在资产的 “Traits” 数组中，添加 `Movement` Trait。在细节面板中，可以配置 `MaxSpeed`、`MaxAcceleration` 等参数。
3.  （可选）为了更平滑的移动，将 `Movement` Trait 替换或叠加 `Spring Movement` Trait，并调整其 `VelocitySmoothingTime` 和 `FacingSmoothingTime`。
4.  （可选）添加 `Velocity Randomizer` Trait 使每个生成的实体速度略有不同，增加多样性。
5.  将配置好的 `UMassEntityConfig` 通过 `AMassSpawner` 或其他生成器应用到世界上，即可生成具有相应移动行为的实体。

## C++ 用法

### 头文件引入

```cpp
#include "MassMovementFragments.h"
#include "MassMovementProcessors.h"
#include "MassSpringMovementFragments.h"
// 根据具体需求包含其他头文件
```

### 基本用法：添加移动片段和处理器

以下代码展示如何在一个自定义 MassEntity Trait 中添加移动所需的片段和处理器。
（来源：`Source/MassMovement/Private/Movement/MassMovementTrait.cpp`）

```cpp
// 在你的 Trait 的 BuildTemplate 函数中
void UMassMovementTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 1. 添加移动数据片段
    BuildContext.AddFragment<FMassVelocityFragment>();
    BuildContext.AddFragment<FMassDesiredMovementFragment>();
    BuildContext.AddFragment<FMassForceFragment>();

    // 2. 根据配置添加移动模式标签
    if (Movement.bIsCodeDrivenMovement)
    {
        BuildContext.AddTag<FMassCodeDrivenMovementTag>();
    }

    // 3. 添加共享的移动参数（性能优化，相同参数的实体共享一份数据）
    BuildContext.AddConstSharedFragment(Movement);

    // 4. 注册核心移动处理器（在 MassEntity 系统中排队执行）
    BuildContext.AddProcessor<UMassApplyForceProcessor>();
    BuildContext.AddProcessor<UMassApplyMovementProcessor>();
}
```

### 进阶用法：创建自定义移动处理器

创建一个处理器来读取实体的位置和速度，并执行自定义逻辑（例如，简单的巡逻行为）。
（参考 `Source/MassMovement/Public/MassSimpleMovementTrait.h` 和 `Source/MassMovement/Private/Movement/MassSimpleMovementProcessor.cpp` 的逻辑）

```cpp
// MyPatrolProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MassEntityQuery.h"
#include "MyPatrolProcessor.generated.h"

UCLASS()
class UMyPatrolProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyPatrolProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询拥有位置、速度和我们自定义的巡逻数据片段的实体
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyPatrolProcessor.cpp
#include "MyPatrolProcessor.h"
#include "MassMovementFragments.h" // For FMassVelocityFragment, FMassDesiredMovementFragment
#include "MassCommonFragments.h"   // For FTransformFragment

UMyPatrolProcessor::UMyPatrolProcessor()
{
    // 设置执行顺序，在力应用之后，位置更新之前
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyPatrolProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    // 配置查询：必须同时拥有变换、速度、期望移动片段和我们的自定义巡逻片段
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassVelocityFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassDesiredMovementFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMyPatrolFragment>(EMassFragmentAccess::ReadWrite); // 假设你定义了这个片段
    // 添加对共享参数的依赖，如果有的话
    // EntityQuery.AddConstSharedRequirement<FMassMovementParameters>();
}

void UMyPatrolProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量处理所有符合条件的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const TArrayView<FMassVelocityFragment> VelocityList = Context.GetMutableFragmentView<FMassVelocityFragment>();
        const TArrayView<FMassDesiredMovementFragment> DesiredMovementList = Context.GetMutableFragmentView<FMassDesiredMovementFragment>();
        const TArrayView<FMyPatrolFragment> PatrolList = Context.GetMutableFragmentView<FMyPatrolFragment>();

        // 获取共享参数（如果有）
        // const FMassMovementParameters& MovementParams = Context.GetConstSharedFragment<FMassMovementParameters>();

        const float DeltaTime = Context.GetDeltaTimeSeconds();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FTransform& EntityTransform = TransformList[i].GetMutableTransform();
            FVector& Velocity = VelocityList[i].Value;
            FVector& DesiredVelocity = DesiredMovementList[i].DesiredVelocity;
            FMyPatrolFragment& PatrolData = PatrolList[i];

            // 示例巡逻逻辑：如果到达当前目标点，切换到下一个
            const FVector CurrentLocation = EntityTransform.GetLocation();
            if (FVector::Dist(CurrentLocation, PatrolData.CurrentWaypoint) < 100.f)
            {
                PatrolData.WaypointIndex = (PatrolData.WaypointIndex + 1) % PatrolData.Waypoints.Num();
                PatrolData.CurrentWaypoint = PatrolData.Waypoints[PatrolData.WaypointIndex];
            }

            // 计算朝向目标点的期望速度
            const FVector DirectionToWaypoint = (PatrolData.CurrentWaypoint - CurrentLocation).GetSafeNormal();
            DesiredVelocity = DirectionToWaypoint * 200.f; // 200 cm/s 巡逻速度

            // 注意：通常不直接在此处修改 Velocity，而是设置 DesiredVelocity，
            // 由后续的 UMassApplyMovementProcessor 或 UMassSpringUpdateProcessor 来平滑并应用。
        }
    });
}
```

## Demo 示例

一个完整的、可编译的最小示例，演示如何创建一个带有弹簧阻尼移动的自定义 MassEntity。

**头文件 (`SimpleSpringAgentTrait.h`)**:
```cpp
#pragma once
#include "MassEntityTraitBase.h"
#include "MassMovementFragments.h"
#include "MassSpringMovementTrait.h"
#include "SimpleSpringAgentTrait.generated.h"

UCLASS(meta=(DisplayName="Simple Spring Agent"))
class USimpleSpringAgentTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;

    // 配置弹簧移动参数
    UPROPERTY(EditAnywhere, Category="Movement")
    FSpringMovementSettings MySpringSettings;

    // 配置目标速度
    UPROPERTY(EditAnywhere, Category="Movement")
    FVector DesiredVelocity = FVector(100.f, 0.f, 0.f); // 向X轴正方向移动
};
```

**源文件 (`SimpleSpringAgentTrait.cpp`)**:
```cpp
#include "SimpleSpringAgentTrait.h"
#include "MassCommonFragments.h" // For FTransformFragment
#include "MassMovementTypes.h"

void USimpleSpringAgentTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 1. 确保基础结构：位置
    BuildContext.AddFragment<FTransformFragment>();

    // 2. 添加弹簧移动的核心片段和处理器（由 USpringMovementTrait 处理）
    // 这会添加 FSpringMovementRuntime, FMassVelocityFragment 等，并注册相关处理器
    BuildContext.AddTrait(*GetMutableDefault<USpringMovementTrait>());

    // 3. 添加期望移动片段，并设置初始期望速度
    // 我们可以创建一个自定义的初始化器（Observer Processor）在实体生成时设置，
    // 但为简化演示，我们直接添加一个共享的期望移动片段。
    // 更好的做法是创建一个类似 UMassRandomVelocityInitializer 的Observer。
    FMassDesiredMovementFragment DesiredMovement;
    DesiredMovement.DesiredVelocity = DesiredVelocity;
    BuildContext.AddFragment(DesiredMovement); // 注意：这通常不是直接添加，而是作为SharedFragment。

    // 4. 为了让弹簧移动处理器生效，需要添加一个标记
    BuildContext.AddTag<FMassCodeDrivenMovementTag>();

    // 5. 添加我们的弹簧设置作为常量共享片段
    // 注意：实际构建中，SpringMovementTrait 内部会处理其自己的设置。
    // 这里仅为演示如何传递参数。
    // BuildContext.AddConstSharedFragment(MySpringSettings);
}
```
**说明**：上述示例为了清晰，简化了部分步骤。在实际项目中，`USpringMovementTrait` 本身已经包含了添加弹簧相关片段和处理器的逻辑，你只需要将其作为 Trait 添加到你的配置中，并调整其暴露的 `SpringSettings` 属性。

## 模块依赖

要使用 `MassGameplay` 插件，你的游戏模块需要依赖以下核心模块（通常在 `Build.cs` 中）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 提供底层 ECS 框架、实体管理器、片段、处理器基础类。 |
| `MassSpawner` | 提供实体生成器（`AMassSpawner`），用于根据配置在世界上批量生成实体。 |
| `MassCommon` | 提供通用的片段和处理器，如 `FTransformFragment`、基础的LOD处理。 |
| `AIModule` | 用于集成行为树、EQS等传统AI系统，是 `MassEQS` 模块的依赖。 |
| `GameplayAbilities` | 用于 `MassGameplayExternalTraits` 模块，为实体添加游戏能力系统支持。 |

**编辑器依赖**（如需自定义编辑器工具）：`EditorFramework`, `UnrealEd`, `MassEntityEditor`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回退了对MassAgent组件的一项早期修改，可能修复了引入的回归问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在关闭实例化静态网格体（ISM）前等待Actor就绪，避免了表现切换时的潜在问题。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在Mass群组中对非傀儡（non-puppet）Actor的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了LOD计算器中逐观察者计算路径的一系列历史遗留bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 表现系统中，将两个手动计算的“额外保留一帧”标志切换为使用新的引擎宏，使代码更简洁。 |

### 维护评价

MassGameplay 插件创建于 2021 年 9 月，距今约 4 年。从近期提交记录看，该插件**仍在被 Epic 积极维护和开发中**，最近的更新集中在 2026 年 5 月，主要围绕 `MassRepresentation` 和 `MassAgentComponent` 的bug修复和逻辑优化。

然而，需要注意的是，该插件在 `.uplugin` 文件中被标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`。这意味着：
1.  **API 可能不稳定**：核心结构和接口在未来的引擎版本中可能会发生重大变更。
2.  **并非默认启用**：需要开发者手动在插件列表中启用。
3.  **可能缺少完整的文档和支持**：作为实验性功能，官方文档可能不完善。

**结论**：MassGameplay 是一个**处于活跃开发中的实验性插件**。它非常适合追求前沿性能优化、愿意承担API变更风险的大型项目或技术预研。对于稳定性要求极高的生产项目，需谨慎评估其带来的收益与可能的维护成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)