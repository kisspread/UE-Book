# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏性 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试套件，模块示例） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine 的 ECS（实体-组件-系统）框架 **MassEntity** 的游戏性层实现。它解决的核心问题是：**如何高效模拟数以万计的游戏实体（如 NPC、子弹、特效粒子、战略单位等）**。

传统 Actor 模型在实体数量巨大时，其内存布局和 Tick 开销会成为性能瓶颈。MassGameplay 基于 MassEntity 提供的数据导向设计，将实体的状态（Fragment）和行为（Processor）分离，并通过高效的批量查询与处理机制，使得大规模并行模拟成为可能。

它存在的意义在于为开发者提供一套标准化的、可扩展的范式，用于构建需要处理海量实体的游戏逻辑，例如开放世界中的密集人群、策略游戏中的庞大军队、或弹幕射击游戏中的成千上万子弹。

## 使用场景

- 你需要模拟一个拥有数千个动态 NPC 的开放世界城市 → 使用 `MassSpawner` 生成，通过 `MassRepresentation` 控制其外观（静态网格体或 Actor），并利用 `MassMovement` 驱动其寻路与移动。
- 你在开发一个大规模即时战略游戏，需要管理数百个单位 → 用 `MassEntity` 定义单位的 Fragment（如生命值、攻击力），用 `MassEQS` 为其寻找目标或位置，并用 `MassReplication` 在多人游戏中同步状态。
- 你需要一个超高性能的弹幕系统，需要同时处理上万颗子弹 → 将子弹定义为 MassEntity，通过 `MassCharacterTrajectory` 或自定义 Processor 批量更新其轨迹。
- 你希望根据距离对大量实体进行 LOD（细节层次）管理，近距离用精细 Actor，远距离用静态网格体或完全不渲染 → 使用 `MassLOD` 和 `MassRepresentation` 模块来智能切换。

## 蓝图用法

MassGameplay 主要通过 `MassSpawner` 模块提供的组件来与蓝图交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据给定的 `MassEntityConfig` 资产，在指定位置批量生成实体。这是从蓝图创建 Mass 实体的最主要入口。 | `UMassSpawnerSubsystem` |
| `Spawn Entities In Environment Query` | 在由环境查询系统（EQS）定义的上下文中生成实体。 | `UMassSpawnerSubsystem` |
| `Get All Spawned Entities` | 获取由特定 Spawner 生成的所有实体句柄，便于后续操作。 | `AMassSpawner` |

### 使用示例（蓝图描述）

1.  **创建配置资产**：在内容浏览器中，右键 -> Mass -> Mass Entity Config，创建一个定义实体初始 Fragment 组合（如 Transform, AgentRadius）的配置资产。
2.  **放置 Spawner**：将 `MassSpawner` Actor 拖入关卡。
3.  **配置 Spawner**：在 `MassSpawner` 的细节面板中，指定之前创建的 `MassEntityConfig`，设置生成数量（如 1000）、生成区域和类型（如 `StaticMesh` 或 `Actor`）。
4.  **触发生成**：游戏运行时，Spawner 会根据配置批量生成实体。你也可以通过蓝图调用 `Spawn Entities` 节点，传入配置资产和位置，进行动态生成。
5.  **行为控制**：通过为实体附加或修改 Fragment，并利用特定的 Processor（如移动、LOD）来控制其行为。这些通常通过 C++ 实现，并由框架自动调度。

## C++ 用法

MassGameplay 的强大功能主要通过 C++ 实现。核心工作流是：**定义数据（Fragment）**、**编写逻辑（Processor）**、**组合配置（Config）**。

### 头文件引入

```cpp
// 核心依赖
#include "MassEntityTypes.h"
#include "MassEntityQuery.h"

// 游戏性模块常用
#include "MassSpawnerTypes.h"
#include "MassAgentComponent.h"
#include "MassRepresentationTypes.h"
#include "MassMovementFragments.h"
```

### 基本用法

**1. 定义自定义 Fragment（数据）**

```cpp
// 来源：常见模式，参考 MassMovement 中的片段定义
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

**2. 创建 Processor（逻辑）**

```cpp
// 来源：常见模式，参考 MassCommon 中的 Processor
UCLASS()
class UMyDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyDamageProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// .cpp
UMyDamageProcessor::UMyDamageProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PrePhysics; // 选择合适的执行阶段
}

void UMyDamageProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddTagRequirement<FMyDamagedTag>(EMassFragmentPresence::All); // 可选：仅处理带特定标签的实体
}

void UMyDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前块（Chunk）中的 Fragment 数组
        const TArrayView<FMyHealthFragment> HealthList = Context.GetMutableFragmentView<FMyHealthFragment>();

        for (FMyHealthFragment& Health : HealthList)
        {
            // 批量处理逻辑
            Health.CurrentHealth -= 10.0f;
            if (Health.CurrentHealth <= 0)
            {
                // 可能在这里添加销毁标签或队列销毁事件
            }
        }
    });
}
```

### 进阶用法

**组合使用多个 Fragment 和 System**

```cpp
// 来源：综合参考 MassMovement 和 MassRepresentation
void UMyMovementWithHealthProcessor::ConfigureQueries(...)
{
    // 要求实体同时具有 Transform、Health 和 AgentRadius 片段
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FAgentRadiusFragment>(EMassFragmentAccess::ReadOnly);
    // 排除正在死亡的实体
    EntityQuery.AddTagRequirement<FMyDyingTag>(EMassFragmentPresence::None);
}

void UMyMovementWithHealthProcessor::Execute(...)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const TConstArrayView<FMyHealthFragment> HealthList = Context.GetFragmentView<FMyHealthFragment>();
        const TConstArrayView<FAgentRadiusFragment> RadiusList = Context.GetFragmentView<FAgentRadiusFragment>();

        for (int32 i = 0; i < TransformList.Num(); ++i)
        {
            if (HealthList[i].CurrentHealth > 50.0f)
            {
                // 仅当生命值高于50时才执行复杂移动逻辑
                FTransform& Transform = TransformList[i].GetMutableTransform();
                // ... 移动逻辑，结合 RadiusList[i] 进行避障
            }
        }
    });
}
```

## Demo 示例

以下是一个最小的 MassGameplay “伤害处理” 系统示例，包含自定义 Fragment 和 Processor。

### MyHealthFragment.h
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MyHealthFragment.generated.h"

USTRUCT()
struct MYGAME_API FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Health")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Health")
    float MaxHealth = 100.0f;
};
```

### MyDamageProcessor.h
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyDamageProcessor.generated.h"

UCLASS()
class MYGAME_API UMyDamageProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyDamageProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

### MyDamageProcessor.cpp
```cpp
#include "MyDamageProcessor.h"
#include "MyHealthFragment.h"
#include "MassCommonFragments.h" // for FTagsFragment if needed

UMyDamageProcessor::UMyDamageProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PostPhysics; // 伤害通常在物理后处理
}

void UMyDamageProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly); // 示例：也可能需要位置信息
}

void UMyDamageProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        const TArrayView<FMyHealthFragment> HealthList = Context.GetMutableFragmentView<FMyHealthFragment>();
        // const TConstArrayView<FTransformFragment> TransformList = Context.GetFragmentView<FTransformFragment>();

        for (FMyHealthFragment& Health : HealthList)
        {
            // 示例：每帧恢复 0.1 点生命
            Health.CurrentHealth = FMath::Min(Health.CurrentHealth + 0.1f, Health.MaxHealth);

            // 示例：如果生命低于 0，可以在此添加逻辑（如标记销毁）
            if (Health.CurrentHealth <= 0.0f)
            {
                // 实际项目中，这里通常会触发一个事件或设置一个 Tag，由另一个 Processor 处理销毁
                UE_LOG(LogTemp, Warning, TEXT("Entity died!"));
            }
        }
    });
}
```

## 模块依赖

要使用 MassGameplay，你的项目模块通常需要依赖 `MassEntity` 和 `MassGameplay` 及其子模块。具体取决于你使用哪些功能。

| 模块 | 用途 |
|---|---|
| `MassEntity` | **核心依赖**。提供 MassEntity ECS 框架的核心类（FMassEntity, FMassProcessor, UMassEntitySubsystem）。 |
| `MassGameplay` | **主要聚合模块**。包含多个子模块的构建目标，是引入 MassGameplay 功能的主要入口。 |
| `MassSpawner` | 提供从配置资产批量生成 Mass 实体的组件和子系统（`MassSpawnerSubsystem`）。 |
| `MassRepresentation` | 管理实体在游戏世界中的视觉表示（静态网格体、Actor、LOD）。 |
| `MassMovement` | 提供实体的移动和导航逻辑。 |
| `MassLOD` | 根据距离和视角管理实体的细节层次，优化性能。 |
| `MassReplication` | 在多人游戏中支持 Mass 实体的状态复制。 |
| `MassCommon` | 包含通用的 Fragment 和 Processor，如 `FTransformFragment`。 |

**注意**：许多子模块（如 `MassActors`, `MassMovement`）在 `Build.cs` 中依赖 `UnrealEd`，这在纯 Runtime 模块中不寻常，可能是因为需要编辑器支持进行资产处理或调试。在打包的发布版本中，这些模块通常会自动处理依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 之前的更改，可能修复了引入的回归问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 改进表示模块，在禁用实例化静态网格体（ISM）前等待Actor就绪，提升稳定性。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在大规模人群中对非傀儡 Actor 的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 `TMassLODCalculator` 中按观察者计算LOD路径的一系列历史遗留bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 在表示模块中，将两个手动计算的 `bDoKeepActorExtraFrame` 改为使用新的引擎模块功能，简化代码。 |

### 维护评价

MassGameplay 插件目前处于**活跃维护**状态。
*   **创建时间**：约4年前（2021年9月），作为 UE5 新范式的一部分。
*   **更新频率**：近期（2026年5月）有密集的更新，主要集中在 `MassRepresentation`、`MassActor` 等核心功能模块的稳定性修复和优化上，表明 Epic 内部仍在积极使用和打磨此框架。
*   **实验性状态**：`.uplugin` 中标记为 `IsExperimentalVersion: true`，且默认不启用。这意味着该 API 可能在未来版本中发生变化，不建议在追求长期稳定性的商业项目中作为核心架构使用，除非团队有能力跟随引擎更新进行适配。
*   **推荐使用**：**推荐用于原型开发、性能密集型项目或与 Epic 有紧密合作的团队**。它非常适合验证大规模实体模拟的游戏玩法，并能带来显著的性能提升。但对于中小型项目或对 API 稳定性要求极高的项目，应谨慎评估其带来的开发与维护成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （无直接链接，可参考 Epic 官方博客、GDC 演讲或 Unreal Engine 文档中关于 MassEntity 的部分）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite) （包含在插件内的测试套件模块）