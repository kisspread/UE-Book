# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 Mass Entity (ECS) 架构构建的**大规模玩法框架**。它并非一个独立的运行时插件，而是一个**模块集合**，为游戏中的“群体”、“市民”、“大量可交互实体”等 gameplay 元素提供底层支持。它解决了在传统对象模型下，难以高效管理、模拟和驱动数以万计智能实体（Agent）的难题。该框架将实体的状态数据（Fragment）与逻辑处理（Processor）分离，利用数据局部性和并行处理来实现高性能，同时通过 Trait 系统提供灵活的组件化配置。

## 使用场景

- **你需要一个城市里有成千上万行为各异的市民、车辆或士兵**：MassGameplay 提供了生成、LOD、移动、复制和表现的全套解决方案。
- **你的大规模实体需要复杂的群体 AI 和寻路**：结合 MassAI 插件（本插件的兄弟模块），可以为海量实体规划路径和决策。
- **你需要为大量实体驱动骨骼网格体动画**：特别是需要平滑的转向和移动过渡时，`MassCharacterTrajectory` 模块是关键。
- **你需要高效地模拟大量实体与场景中 Smart Objects 的交互**：`MassSmartObjects` 模块处理此类需求。
- **你需要在编辑器中方便地配置和调试海量实体**：配套的 Editor 模块和 Debug 模块提供了相应工具。

## 蓝图用法

核心的蓝图交互主要通过 `Trait` 类完成，用于在实体模板中配置能力和参数。真正的逻辑由后台的 Processor 自动执行。

### 核心 Trait (蓝图中可配置)

| Trait | 说明 |
|---|---|
| `UCharacterTrajectoryTrait` | 为实体添加轨迹生成能力。配置历史采样数、预测采样数等参数。 |
| `UCharacterTrajectoryMovementTrait` | 重写默认移动，使实体沿生成的轨迹运动。需要与 `UCharacterTrajectoryTrait` 配合使用。 |
| (其他 Trait 如移动、表示、LOD等，属于其他子模块) | |

### 配置示例（蓝图描述）

1.  在你的 MassEntityDataAsset 或通过 `UObjectLibrary` 配置实体模板时，为模板添加 `UCharacterTrajectoryTrait`。
2.  在该 Trait 的细节面板中，设置 `PoseTrajectoryParameters`，例如将 `NumHistorySamples` 设为 30，`NumPredictionSamples` 设为 15。
3.  如果希望角色动画完全由轨迹驱动（平滑转向），再添加 `UCharacterTrajectoryMovementTrait`。
4.  将此配置好的实体模板赋予 `MassSpawner` 即可。

## C++ 用法

### 头文件引入

```cpp
#include “MassCharacterTrajectoryTrait.h”
#include “MassCharacterTrajectoryFragments.h”
```

### 基本用法：获取实体轨迹数据

在一个自定义的 Processor 中，查询并读取实体的轨迹数据。
```cpp
// 自定义处理器的 ConfigureQueries 中
MyEntityQuery.AddRequirement<FCharacterTrajectoryFragment>(EMassFragmentAccess::ReadOnly);

// 在 Execute 函数中
MyEntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
{
    const TConstArrayView<FCharacterTrajectoryFragment> Trajectories = Context.GetFragmentView<FCharacterTrajectoryFragment>();
    for (const FCharacterTrajectoryFragment& Trajectory : Trajectories)
    {
        // 使用 Trajectory.Trajectory.Samples 获取轨迹点序列
        // 使用 Trajectory.SteeringTarget 获取期望朝向
    }
});
```

### 进阶用法：自定义轨迹生成处理器

虽然提供了默认的 `USpringMovementToCharacterTrajectoryProcessor` 和 `UMovementToCharacterTrajectoryProcessor`，但你也可以实现自己的处理器来生成特殊轨迹。
```cpp
// 在 ConfigureQueries 中
CalculateTrajectoryEntityQuery.AddRequirement<FCharacterTrajectoryFragment>(EMassFragmentAccess::ReadWrite);
CalculateTrajectoryEntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
// 添加你需要的其它 Fragment，如自定义的力场或路径点数据
```

## Demo 示例

一个简单的处理器，用于在调试时输出实体轨迹的当前朝向。
```cpp
// MyTrajectoryDebugProcessor.h
#pragma once
#include “MassProcessor.h”
#include “MassEntityQuery.h”
#include “MassCharacterTrajectoryFragments.h”
#include “MyTrajectoryDebugProcessor.generated.h”

UCLASS()
class UMyTrajectoryDebugProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyTrajectoryDebugProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```
```cpp
// MyTrajectoryDebugProcessor.cpp
#include “MyTrajectoryDebugProcessor.h”
#include “MassEntityView.h”

UMyTrajectoryDebugProcessor::UMyTrajectoryDebugProcessor()
{
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::CharacterTrajectoryDebug;
}

void UMyTrajectoryDebugProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FCharacterTrajectoryFragment>(EMassFragmentAccess::ReadOnly);
}

void UMyTrajectoryDebugProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        const TConstArrayView<FCharacterTrajectoryFragment> Trajectories = Context.GetFragmentView<FCharacterTrajectoryFragment>();
        for (const FCharacterTrajectoryFragment& Trajectory : Trajectories)
        {
            // 在控制台打印当前帧的轨迹起始朝向（SteeringTarget）
            UE_LOG(LogTemp, Log, TEXT(“Entity Steering Target Quat: %s”), *Trajectory.SteeringTarget.ToString());
        }
    });
}
```

## 模块依赖

要使用 `MassCharacterTrajectory` 子模块，你的模块需要依赖以下 Mass 框架模块：

| 模块 | 用途 |
|---|---|
| `MassCommon` | 提供基础的 Fragment、Tag、Trait 等 ECS 数据结构定义 |
| `MassEntity` | Mass Entity 核心框架，提供实体管理器和处理器基类 |
| `MassMovement` | 移动相关的 Fragment（如 `FMassMovementParameters`）和处理器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgent 组件的一项修改，可能修复了引入的问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了表示模块中，切换掉 ISM 前等待 Actor 就绪的逻辑。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在人群中处理非 Puppet Actor（可能是手动放置的）的逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中按查看器计算 LOD 路径的一系列已知 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | 优化了表示模块中保留 Actor 额外帧的标志位计算逻辑。 |

### 维护评价

MassGameplay 是 Unreal Engine 5 大规模实体玩法的**核心官方实现**。虽然创建于 2021 年，但从近期的 git 提交（2026年5月）来看，它仍在**积极维护和修复 Bug**。作为实验性插件，其 API 可能仍在演变，但 Epic 官方显然在其上持续投入，用于构建如《城市：天际线 2》等需要海量实体管理的游戏。它代表了 UE 未来大规模模拟的方向，**强烈推荐**有大规模实体需求的团队研究和使用，但需注意其 API 可能不稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) (MassGameplayTestSuite 模块)