# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（基于 MassEntity 的大规模智能体模拟实现）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板等） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine 中基于 MassEntity（一种高性能的 ECS 数据导向框架）构建的游戏玩法扩展层。它解决了传统基于 Actor 模型在处理成千上万甚至百万级实体（如 NPC、生物、物体）时的性能瓶颈问题。

核心在于：它将传统的、以个体为中心的 OOP 对象（Actor）逻辑，拆解为以数据（Fragment）和行为（Processor）为中心的 ECS 组件系统。游戏玩法逻辑不再直接作用于单个 Actor，而是通过 Processor 在每帧批量处理拥有特定数据组合（Fragment）的实体（Entity）。这使得 CPU 缓存命中率极大提高，逻辑得以并行化，从而能够高效地模拟大规模的群体行为、环境交互和物理运动。

它本质上是 MassEntity 的上层应用框架，为游戏开发者提供了现成的、可扩展的“大规模模拟能力工具箱”。

## 使用场景

- **开放世界 NPC 模拟**：需要同时模拟成千上万的市民、敌人或动物，它们拥有简单的 AI 行为（巡逻、交谈、反应），但不需要昂贵的个体 Actor。
- **RTS/战争游戏**：管理庞大的军队单位，实现高效的寻路、阵型、攻击和死亡。
- **模拟/经营类游戏**：如模拟城市中的市民、交通车辆，或主题公园中的游客。
- **大世界收集品/环境物**：管理遍布大世界的可交互物品（如草药、矿石、任务物品），它们需要逻辑但不需要独立的 Actor。
- **需要复杂群体行为**：如鸟群、鱼群、人群恐慌等，通过简单的数据规则驱动涌现出复杂行为。
- **性能敏感场景**：当传统 Actor 的数量成为性能瓶颈时，可以考虑将实体逻辑迁移到 Mass 系统。

## 蓝图用法

MassGameplay 主要通过其配置子系统、生成器和调试工具暴露蓝图接口。核心的“玩法逻辑”通常在 C++ Processor 中编写，但配置和触发可以在蓝图中完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Trait Class` | 根据特征（Trait）的类名获取其 UClass 指针，用于代码中引用。 | `UMassTraitRepository` (编辑器子系统) |
| `Get Traits Adding Fragment` | 获取所有会添加指定碎片（Fragment）的特征（Trait）的名称列表。便于查找功能来源。 | `UMassTraitRepository` (编辑器子系统) |
| `Get Mutable Actor Manager` | 获取编辑器内的 Actor 管理器实例，用于调试和检查。 | `UMassActorEditorSubsystem` (编辑器子系统) |
| `Spawn Entities from Data` | 从 `UMassEntityConfig` 资产中批量生成实体。这是蓝图中最常用的生成方式。 | `AMassSpawner` |
| `Get Entity Manager` | 获取当前世界的 Mass Entity 管理器。 | `UMassEntitySubsystem` |

### 使用示例（蓝图描述）

1.  **配置实体**：在内容浏览器中创建 `MassEntityConfig` 资产。在资产的细节面板中，为实体添加所需的“Trait”（特征），如 `MassCharacterMovementTrait`, `MassRepresentationTrait`。这些 Trait 会自动引入必要的 Fragment 和 Processor。
2.  **放置生成器**：在场景中放置一个 `MassSpawner` Actor。
3.  **设置生成器**：选中 `MassSpawner`，在其细节面板中：
    - 设置 `Entity Config` 为你刚刚创建的配置资产。
    - 设置 `Spawn Method`，例如选择 `Grid`（网格）来在区域内生成一片实体。
    - 设置生成数量 `Count`。
4.  **运行游戏**：游戏运行时，`MassSpawner` 会根据配置在指定位置批量生成成千上万个“实体”。它们的移动、表现等行为由对应的 Mass Processor 驱动。
5.  **调试**：使用 `ShowDebug Mass` 控制台命令或编辑器内的 Mass 调试视图，来可视化实体的位置、Fragment 数据和活跃 Processor。

## C++ 用法

MassGameplay 的核心是定义数据（Fragment/Chunk Fragment）和行为（Processor）。

### 头文件引入

```cpp
#include "MassEntityTypes.h"
#include "MassProcessor.h"
#include "MassEntityView.h"
// 根据需要引入特定模块的头文件
#include "MassMovementFragments.h"
#include "MassRepresentationFragments.h"
```

### 基本用法

**定义自定义碎片（Fragment）和标签（Tag）**：

```cpp
// 定义一个存储生命值的碎片
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Health")
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};

// 定义一个标记“受伤”状态的标签（Tag）
USTRUCT()
struct FInjuredTag : public FMassTag
{
    GENERATED_BODY()
};
```

**创建处理器（Processor）来操作数据**：

```cpp
// 一个简单的处理器：检查生命值，低于阈值时添加“受伤”标签
UCLASS()
class UHealthCheckProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    virtual void ConfigureQueries() override
    {
        // 定义查询：寻找所有拥有 FHealthFragment，但没有 FInjuredTag 的实体
        ProcessingQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadOnly);
        ProcessingQuery.AddRequirement<FInjuredTag>(EMassFragmentAccess::None);
    }

    virtual void Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context) override
    {
        // 执行查询
        ProcessingQuery.ForEachEntityChunk(EntitySubsystem, Context, [this](FMassExecutionContext& Context)
        {
            // 获取实体视图以读写数据
            const TConstArrayView<FHealthFragment> HealthList = Context.GetFragmentView<FHealthFragment>();
            
            for (int32 i = 0; i < Context.GetNumEntities(); ++i)
            {
                const FHealthFragment& HealthData = HealthList[i];
                if (HealthData.CurrentHealth < HealthData.MaxHealth * 0.3f) // 30% 血量
                {
                    // 为实体添加“受伤”标签
                    Context.Defer().AddTag<FInjuredTag>(Context.GetEntity(i));
                }
            }
        });
    }

private:
    // 处理器内部查询
    FMassEntityQuery ProcessingQuery;
};
```

### 进阶用法

**1. 使用自定义处理器**：
你可以创建继承自 `UMassProcessor` 或 `UMassObserverProcessor` 的类。
- `UMassProcessor`：每帧或按特定频率执行逻辑。
- `UMassObserverProcessor`：监听实体的创建、销毁，或特定 Fragment/Tag 的添加和移除。

**2. 集成现有系统**：
`MassActors` 模块提供了将 Mass 实体与 Actor 同步的功能（通过 `MassActorSpawnRequestProcessor`）。`MassRepresentation` 模块负责将实体渲染为实例化静态网格（ISM）或简化 Actor。

```cpp
// 在处理器中生成一个临时的Actor来代表一个实体（用于复杂动画或交互）
#include "MassActorSubsystem.h"

// ... 在处理器执行中
FMassActorSpawnRequest SpawnRequest;
SpawnRequest.Template = SomeActorTemplate; // 蓝图类模板
SpawnRequest.Transform = EntityTransform;
EntitySubsystem.Defer().PushCommand<FMassActorSpawnRequest>(MoveTemp(SpawnRequest));
```

## Demo 示例

一个最小化的自定义处理器示例，它会让所有拥有 `FHealthFragment` 的实体每帧缓慢恢复生命值。

**HealthRegenerationProcessor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "HealthRegenerationProcessor.generated.h"

UCLASS()
class UHealthRegenerationProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UHealthRegenerationProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context) override;

private:
    /** 每秒恢复的生命值 */
    UPROPERTY(EditAnywhere, Category = "Regeneration")
    float RegenerationRate = 1.0f;

    FMassEntityQuery HealthQuery;
};
```

**HealthRegenerationProcessor.cpp**
```cpp
#include "HealthRegenerationProcessor.h"
#include "MassEntityTypes.h"
#include "MassExecutionContext.h"
#include "Gameplay/HealthFragment.h" // 假设的碎片头文件

UHealthRegenerationProcessor::UHealthRegenerationProcessor()
{
    // 标记为每帧执行
    ExecutionOrder.ExecuteInGroup = TEXT("Health");
    bAutoRegisterWithProcessingPhases = true;
}

void UHealthRegenerationProcessor::ConfigureQueries()
{
    // 需要读写 HealthFragment
    HealthQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UHealthRegenerationProcessor::Execute(UMassEntitySubsystem& EntitySubsystem, FMassExecutionContext& Context)
{
    // 计算本帧恢复量
    const float DeltaTime = Context.GetDeltaTimeSeconds();
    const float FrameRegen = RegenerationRate * DeltaTime;

    // 对所有匹配的实体执行恢复
    HealthQuery.ForEachEntityChunk(EntitySubsystem, Context, [FrameRegen](FMassExecutionContext& Context)
    {
        TArrayView<FHealthFragment> HealthFragments = Context.GetMutableFragmentView<FHealthFragment>();
        for (FHealthFragment& Health : HealthFragments)
        {
            Health.CurrentHealth = FMath::Min(Health.CurrentHealth + FrameRegen, Health.MaxHealth);
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心实体系统，提供 Fragment、Entity、Query 等基础框架。 |
| `SmartObjectsModule` | 与智能对象系统集成，用于实体与场景中可交互点的交互。 |
| `AI` | 与行为树（BehaviorTree）和黑板（Blackboard）集成，提供高层决策。 |
| `GameplayAbilities` | 与 Gameplay Ability System (GAS) 集成，用于为实体赋予技能。 |
| `GameplayInteractionsModule` | 提供更复杂的场景交互框架。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的早期改动。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 关闭实例化静态网格 (ISM) 前等待 Actor 就绪，修复切换问题。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 人群组中对非木偶 Actor 的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复 `TMassLODCalculator` 按查看器 LOD 路径中的一系列历史遗留 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [MassRepresentation] 将两处手动计算 `bDoKeepActorExtraFrame` 改为使用新的 `UE::Mass` 公共工具函数。 |

### 维护评价

MassGameplay 作为 Unreal Engine 5.1 及以后版本的重点发展技术栈之一，目前处于**活跃维护**状态。

- **创建时间**：约5年前推出，正值 UE5 开发周期。
- **更新频率**：最近更新非常密集（2026年5月），集中在修复 Bug、优化表现（LOD、ISM 切换）和提升稳定性上。这表明 Epic 正在积极打磨其作为生产就绪的工具。
- **实验性状态**：插件仍标记为 `IsExperimentalVersion: true`，意味着其 API 未来可能发生 breaking changes，不建议在对稳定性要求极高的商业项目核心中直接使用，但非常适合原型开发和性能探索。
- **已知限制**：生态系统（如与 GAS、AI 的深度集成）仍在完善中。调试工具虽然强大，但学习曲线较陡峭。
- **推荐使用**：**强烈推荐**所有需要模拟大规模实体的游戏项目进行技术评估和原型验证。它是解决大规模实体性能问题的**未来标准方案**。建议从 `MassGameplayTestSuite` 模块中的示例开始学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （暂无独立文档，主要集成在引擎文档中）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)