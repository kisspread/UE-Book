# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine 5 中 **MassEntity** 框架的上层应用插件。MassEntity 本身是一个高性能的实体组件系统（ECS）框架，专注于数据布局和缓存友好性。而 MassGameplay 在此之上，提供了一套**面向游戏玩法**的模块化系统，用于实现大规模智能体（Agent）的模拟。

它解决的核心问题是：如何在 UE 中高效地管理和模拟成千上万甚至数十万个具有简单逻辑的实体（如 NPC、单位、载具、环境物体），同时保持良好的性能和可扩展性。它通过将游戏逻辑（如移动、感知、决策、表现）分解为独立的、可组合的处理器（Processor）和片段（Fragment），并利用 MassEntity 的批量处理能力来实现这一点。

## 使用场景

- **大规模 RTS 或战争游戏**：你需要模拟成千上万的士兵、载具单位，它们需要寻路、攻击、编队移动。
- **开放世界 NPC 群体**：城市中大量市民、交通载具需要具有基础的 AI 行为和 LOD（细节层次）管理。
- **大规模战斗或生存游戏**：如僵尸潮、虫群等需要大量简单 AI 敌人的场景。
- **环境模拟**：模拟大量鸟类、鱼群、昆虫等群体行为。
- **需要高性能实体管理的任何场景**：当传统的 Actor 模型因数量过多导致性能瓶颈时，可以考虑使用 MassGameplay 进行重构。

## 蓝图用法

MassGameplay 主要通过数据资产（Data Asset）和编辑器工具进行配置，其核心逻辑运行在 MassEntity 的处理器中，因此直接暴露给蓝图的函数节点相对较少。主要的蓝图交互点在于配置和触发。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpawnEntities` | 根据给定的实体模板（Entity Template）和数量，在指定位置生成 Mass 实体。 | `AMassSpawner` |
| `GetMassEntitySubsystem` | 获取世界中的 MassEntity 子系统实例，用于高级操作。 | `UMassEntitySubsystem` (引擎类) |

### 使用示例（蓝图描述）

1.  **配置实体模板**：在编辑器中创建 `UMassEntityConfigAsset`，定义实体的初始片段（Fragment）组合，例如包含位置、移动速度、网格体引用等。
2.  **放置 Spawner**：在场景中放置 `AMassSpawner` Actor。
3.  **设置 Spawner**：在 Spawner 的细节面板中，指定要使用的 `EntityConfigAsset`，并设置生成数量、生成范围等参数。
4.  **触动生成**：可以通过 Spawner 的 `SpawnEntities` 函数（蓝图可调用）或设置其自动生成功能来在游戏开始时生成实体。

## C++ 用法

MassGameplay 的 C++ 用法主要围绕定义自定义的 **Fragment**（数据）、**Processor**（逻辑）和 **Trait**（配置）。

### 头文件引入

```cpp
#include "MassEntityTypes.h" // 基础类型
#include "MassProcessor.h"   // 处理器基类
#include "MassEntityView.h"  // 实体视图
```

### 基本用法

**1. 定义自定义 Fragment**
```cpp
// MyFragments.h
#include "MassEntityTypes.h"

// 一个简单的生命值片段
USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Health")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Health")
    float MaxHealth = 100.0f;
};
```

**2. 定义自定义 Processor**
```cpp
// MyHealthProcessor.h
#include "MassProcessor.h"

UCLASS()
class UMyHealthProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyHealthProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MyHealthProcessor.cpp
UMyHealthProcessor::UMyHealthProcessor()
{
    // 设置处理器执行顺序，例如在移动之后
    ExecutionOrder.ExecuteAfter.Add(UE::Mass::Processor::Name::Movement);
}

void UMyHealthProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
    // 可以添加其他相关片段，例如位置
    // EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
}

void UMyHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量处理所有拥有 FMyHealthFragment 的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 HealthFragment 数组
        TConstArrayView<FMyHealthFragment> HealthList = Context.GetFragmentView<FMyHealthFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FMyHealthFragment& Health = HealthList[i];
            // 执行逻辑，例如每帧减少生命值（示例）
            // Health.CurrentHealth -= 1.0f * Context.GetDeltaTimeSeconds();
        }
    });
}
```

### 进阶用法

结合多个模块的功能，例如让实体在移动的同时根据 LOD 级别改变表现。
```cpp
// 在 Processor 中同时查询移动和表示片段
void UMyMovementAndRepresentationProcessor::ConfigureQueries()
{
    // 要求实体同时拥有移动意图和表示片段
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassRepresentationFragment>(EMassFragmentAccess::ReadWrite);
    // 可以添加 LOD 片段来根据距离调整行为
    EntityQuery.AddRequirement<FMassRepresentationLODFragment>(EMassFragmentAccess::ReadOnly);
}

void UMyMovementAndRepresentationProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        auto MoveTargets = Context.GetFragmentView<FMassMoveTargetFragment>();
        auto Representations = Context.GetFragmentView<FMassRepresentationFragment>();
        auto LODs = Context.GetFragmentView<FMassRepresentationLODFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMassRepresentationLODFragment& LOD = LODs[i];
            // 根据 LOD 级别决定是否更新视觉表现
            if (LOD.LODRepresentation != EMassLOD::Off)
            {
                // 更新表示组件的位置等
                Representations[i].SetRepresentationLocation(MoveTargets[i].TargetLocation);
            }
        }
    });
}
```

## Demo 示例

以下是一个最小化的自定义处理器示例，它会将所有拥有 `FMyHealthFragment` 的实体的生命值每秒减少 1 点。

**MyHealthProcessor.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "MyHealthProcessor.generated.h"

UCLASS()
class MYPROJECT_API UMyHealthProcessor : public UMassProcessor
{
	GENERATED_BODY()

public:
	UMyHealthProcessor();

protected:
	virtual void ConfigureQueries() override;
	virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
	FMassEntityQuery EntityQuery;
};
```

**MyHealthProcessor.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "MyHealthProcessor.h"
#include "MyFragments.h" // 包含 FMyHealthFragment 的定义

UMyHealthProcessor::UMyHealthProcessor()
{
	// 设置处理器在每帧执行
	ExecutionOrder.ExecuteInGroup = UE::Mass::Processor::Group::Behavior;
	ExecutionOrder.ExecuteAfter.Add(UE::Mass::Processor::Name::Movement);
}

void UMyHealthProcessor::ConfigureQueries()
{
	EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyHealthProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
	EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
	{
		const float DeltaTime = Context.GetDeltaTimeSeconds();
		TConstArrayView<FMyHealthFragment> HealthFragments = Context.GetFragmentView<FMyHealthFragment>();

		for (int32 i = 0; i < Context.GetNumEntities(); ++i)
		{
			FMyHealthFragment& Health = HealthFragments[i];
			Health.CurrentHealth -= 1.0f * DeltaTime; // 每秒减少1点生命值
			if (Health.CurrentHealth <= 0.0f)
			{
				// 标记实体待销毁（需要配合其他系统，如 MassSpawner 的销毁逻辑）
				// Context.Defer().DestroyEntity(Context.GetEntity(i));
			}
		}
	});
}
```

## 模块依赖

MassGameplay 插件内部模块相互依赖，对外部项目的依赖主要是 MassEntity 核心框架。

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心 ECS 框架，提供实体、片段、处理器、世界管理等基础功能。 |
| `MassSpawner` | 提供实体生成、配置和管理的功能。 |
| `MassRepresentation` | 处理实体的视觉表现，如静态网格体、骨骼网格体、Niagara 系统等。 |
| `MassMovement` | 实现基于意图的移动系统，包括路径跟随、避障等。 |
| `MassLOD` | 管理实体的细节层次，根据距离和重要性调整更新频率和表现。 |
| `MassSignals` | 提供实体间的信号通信机制。 |
| `MassSmartObjects` | 将 SmartObject 系统与 Mass 实体集成。 |
| `MassReplication` | 处理 Mass 实体的网络复制。 |

## 维护状态

### 近期更新

```
- 2739c3d30ebc 2024-10-03 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
- d348655b8cad 2024-09-15 [Mass] headers cleanup, mainly pushing IWYU
- 372bd724a122 2024-08-20 [Mass] more Mass-related header cleanups.
```

### 维护评价

MassGameplay 插件创建于 2021 年，是一个相对年轻的系统。从最近的提交记录看，更新主要集中在**代码清理和头文件规范化**（IWYU），而非新功能开发。这表明该插件可能已进入一个相对稳定的维护阶段。

**优点**：
- 作为 Epic 官方维护的插件，其架构设计和性能优化是经过深思熟虑的。
- 与引擎核心的 MassEntity 框架深度集成，是 UE5 大规模实体模拟的官方解决方案。

**风险与注意事项**：
- **实验性状态**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，且默认禁用。这意味着其 API 和功能在未来版本中可能发生**不兼容的变更**。
- **学习曲线陡峭**：需要理解 ECS 设计模式和 MassEntity 的特定概念（Fragment, Processor, Chunk），与传统的 Actor 思维模式差异较大。
- **文档和社区资源有限**：作为较新且实验性的系统，官方文档和社区教程相对较少，主要依赖源码和示例项目学习。

**推荐**：如果你的项目确实需要模拟**数万以上**的实体，并且对性能有极致要求，那么值得投入时间学习和使用 MassGameplay。对于中小规模项目，传统的 Actor 或 AI 系统可能更简单直接。使用前请做好应对 API 变更的准备，并密切关注引擎更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)