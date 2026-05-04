# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据表、材质） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件是 Unreal Engine 中基于 MassEntity (ECS) 架构的大规模智能体（Agent）模拟框架的**游戏玩法层实现**。它解决了在传统 Actor 模型下，难以高效管理成千上万（甚至数十万）个同质化、行为相对简单的实体（如 NPC、野生动物、子弹、特效粒子等）的核心问题。

该插件并非一个独立的物理或 AI 系统，而是建立在底层 `MassEntity` 框架之上，提供了一套完整的游戏玩法功能模块，包括：
- **实体生成与管理** (`MassSpawner`, `MassActors`)：提供从数据表批量生成实体、将 Mass 实体与 Actor 关联等功能。
- **移动与导航** (`MassMovement`)：为大量实体提供高效的移动和转向能力。
- **视觉表现与 LOD** (`MassRepresentation`, `MassLOD`)：根据距离和重要性，使用实例化静态网格（ISM）、公告板（Billboard）或完全隐藏实体，以优化渲染性能。
- **网络复制** (`MassReplication`)：为大规模实体提供高效的网络同步方案。
- **游戏逻辑集成** (`MassSmartObjects`, `MassSignals`, `MassEQS`)：允许实体与游戏世界中的智能对象交互、发送/接收信号，并使用环境查询系统（EQS）进行决策。
- **调试工具** (`MassGameplayDebug`)：提供可视化调试工具，帮助开发者观察和诊断大量实体的行为。

**为什么存在？** 传统 Actor 模型为每个实体创建独立的对象，包含完整的组件和逻辑，当实体数量巨大时，会导致严重的内存和 CPU 开销。MassGameplay 通过数据驱动的 ECS 架构，将数据（Fragment）与逻辑（Processor）分离，实现了极高的缓存友好性和并行处理能力，从而能够支撑起开放世界、大规模战场等对实体数量要求极高的游戏场景。

## 使用场景

- **开放世界游戏**：你需要在地图上生成成千上万的野生动物、行人或敌方士兵，且要求它们有基本的 AI 行为（巡逻、逃跑）和视觉表现，但不能使用传统的 Actor 导致性能崩溃。
- **即时战略（RTS）游戏**：你需要管理数百甚至数千个作战单位，它们需要高效的移动、寻路和战斗逻辑。
- **弹幕射击游戏**：你需要同时处理屏幕上成百上千的子弹或投射物，并进行高效的碰撞检测。
- **城市模拟或交通模拟**：你需要模拟大量车辆或市民的流动。
- **任何需要“数量即质量”视觉效果的场景**：例如大规模的粒子特效、群体动画等。

## 蓝图用法

MassGameplay 的蓝图接口主要集中在实体生成、调试和部分游戏逻辑集成上。核心的 ECS 逻辑（Processor）通常在 C++ 中实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据提供的实体模板和数量，在指定位置批量生成 Mass 实体。 | `AMassSpawner` |
| `Get Debug Visualization Component` | 获取用于调试可视化的组件实例。 | `UMassDebuggerSubsystem` |
| `Set Selected Entity` | 在调试器中选中一个特定的 Mass 实体，以便查看其详细信息。 | `UMassDebuggerSubsystem` |
| `Add Debug Vis Type` | 向调试可视化组件注册一种新的实体视觉表现类型（如特定的网格和材质）。 | `UMassDebugVisualizationComponent` |
| `Add Debug Vis Instance` | 为一个实体添加一个调试可视化实例。 | `UMassDebugVisualizationComponent` |

### 使用示例（蓝图描述）

1.  **批量生成实体**：
    - 在场景中放置一个 `MassSpawner` Actor。
    - 在其细节面板中，设置 `Entity Types` 数据表，该表定义了要生成的实体类型及其对应的 Mass 模板。
    - 设置 `Spawn Count` 和 `Spawn Radius`。
    - 调用 `Spawn Entities` 节点，即可在 Spawner 周围生成大量实体。

2.  **查看实体调试信息**：
    - 确保项目启用了 `WITH_MASSGAMEPLAY_DEBUG` 宏（通常在开发版本中默认启用）。
    - 使用控制台命令 `mass.debug.DebugEntity <Index>` 或 `mass.debug.SetDebugEntityRange <Start> <End>` 来选择要调试的实体。
    - 通过 `UMassDebuggerSubsystem` 的 `Get Selected Entity Info` 节点，可以在 HUD 或日志中查看选中实体的详细 Fragment 数据。

## C++ 用法

MassGameplay 的核心用法是定义自己的 Fragment（数据）和 Processor（逻辑），并利用插件提供的基础设施。

### 头文件引入

```cpp
// 引入 MassEntity 核心
#include "MassEntityTypes.h"
#include "MassEntityManager.h"
// 引入 MassGameplay 提供的特定功能模块
#include "MassSpawnerTypes.h" // 用于生成实体
#include "MassMovementFragments.h" // 用于移动
#include "MassRepresentationFragments.h" // 用于视觉表现
```

### 基本用法

**定义自定义 Fragment 和 Processor**
```cpp
// MyHealthFragment.h
#pragma once
#include "MassEntityTypes.h"
#include "MyHealthFragment.generated.h"

USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
    float MaxHealth = 100.f;
};

// MyHealthRegenProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyHealthRegenProcessor.generated.h"

UCLASS()
class UMyHealthRegenProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyHealthRegenProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyHealthRegenProcessor.cpp
#include "MyHealthRegenProcessor.h"
#include "MyHealthFragment.h"

UMyHealthRegenProcessor::UMyHealthRegenProcessor()
{
    // 设置处理器执行顺序，例如在移动之后
    ProcessingPhase = EMassProcessingPhase::PostPhysics;
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyHealthRegenProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyHealthRegenProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 FMyHealthFragment 数据
        TConstArrayView<FMyHealthFragment> HealthFragments = Context.GetFragmentView<FMyHealthFragment>();
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            FMyHealthFragment& Health = const_cast<FMyHealthFragment&>(HealthFragments[i]); // 注意：这里简化了，实际应使用 ReadWrite 访问
            Health.CurrentHealth = FMath::Min(Health.CurrentHealth + 1.f, Health.MaxHealth);
        }
    });
}
```
*来源：基于 MassProcessor 的通用模式，参考 `MassGameplayDebug` 中的 `UDebugVisLocationProcessor` 等处理器的实现。*

### 进阶用法

**使用 MassSpawner 生成实体**
```cpp
#include "MassSpawnerSubsystem.h"
#include "MassEntityTemplate.h"

void SpawnMyEntities(UWorld* World, const FVector& Location, int32 Count)
{
    if (UMassSpawnerSubsystem* SpawnerSubsystem = World->GetSubsystem<UMassSpawnerSubsystem>())
    {
        // 假设你已经通过数据表或代码创建了一个名为 “MyAgent” 的实体模板
        const FMassEntityTemplate* Template = SpawnerSubsystem->FindEntityTemplate(TEXT("MyAgent"));
        if (Template)
        {
            FTransform SpawnTransform(Location);
            SpawnerSubsystem->SpawnEntities(Template->GetTemplateID(), Count, SpawnTransform);
        }
    }
}
```
*来源：`MassSpawner` 模块的典型用法。*

## Demo 示例

以下是一个最小示例，展示如何定义一个带有自定义生命值片段的实体，并创建一个简单的处理器来增加其生命值。

**MyHealthFragment.h**
```cpp
#pragma once
#include "MassEntityTypes.h"
#include "MyHealthFragment.generated.h"

USTRUCT()
struct FMyHealthFragment : public FMassFragment
{
    GENERATED_BODY()
    float CurrentHealth = 100.f;
};
```

**MyHealthRegenProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MyHealthRegenProcessor.generated.h"

UCLASS()
class UMyHealthRegenProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyHealthRegenProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;
    FMassEntityQuery EntityQuery;
};
```

**MyHealthRegenProcessor.cpp**
```cpp
#include "MyHealthRegenProcessor.h"
#include "MyHealthFragment.h"

UMyHealthRegenProcessor::UMyHealthRegenProcessor()
{
    ProcessingPhase = EMassProcessingPhase::PostPhysics;
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    bAutoRegisterWithProcessingPhases = true;
}

void UMyHealthRegenProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMyHealthFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyHealthRegenProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        TArrayView<FMyHealthFragment> HealthFragments = Context.GetMutableFragmentView<FMyHealthFragment>();
        for (FMyHealthFragment& Health : HealthFragments)
        {
            Health.CurrentHealth += 1.f;
        }
    });
}
```

## 模块依赖

要使用 `MassGameplay` 插件的功能，你的项目模块通常需要依赖 `MassEntity` 核心模块以及你实际使用的具体子模块。以下是 `MassGameplayDebug` 模块的特殊依赖：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器功能，用于调试可视化组件的编辑器内支持。 |
| `MassEntityEditor` | 提供 MassEntity 的编辑器扩展功能。 |

对于其他子模块，请参考其各自的 `Build.cs` 文件。例如，使用 `MassMovement` 功能需要依赖 `MassMovement` 模块。

## 维护状态

### 近期更新

```
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- cd3c2a716daa Replace some usages of FORCEINLINE with inline in Mass modules.
- b1980471196e [Mass] Minor MassEntityManager cleanup, including removing some header inclusion
```

### 维护评价

MassGameplay 是一个**实验性**插件，且默认**未启用**。从创建时间（2021年）看，它已有约4年历史，属于较新的系统。

**积极方面**：
- 作为 Epic 官方推出的大规模实体解决方案，其架构设计先进，是 UE5 面向未来的核心技术之一。
- 代码库庞大（555个文件），功能模块划分清晰，表明其设计成熟且功能完备。

**注意事项与风险**：
1.  **实验性状态**：`IsExperimentalVersion: true` 和 `EnabledByDefault: false` 明确表明该系统尚未稳定，API 和功能可能在未来的引擎版本中发生重大变更。
2.  **维护活跃度**：最近的提交均为代码维护和清理（如内联函数替换、头文件整理），没有看到新功能开发或重大 bug 修复。这可能意味着该系统已进入一个相对稳定的“维护期”，但也可能意味着活跃开发已暂停。
3.  **学习曲线**：基于 ECS 的架构与传统的 Actor/Component 模型差异巨大，需要开发者转变思维，学习成本较高。
4.  **生态集成**：虽然提供了与 EQS、SmartObjects 等系统的集成，但可能不如原生 Actor 系统那样无缝和全面。

**推荐**：MassGameplay 是面向特定高性能需求场景的**高级解决方案**。如果你的项目确实需要管理海量实体，并且愿意承担实验性 API 变更的风险和较高的学习成本，那么它值得深入研究和使用。对于中小型项目或实体数量需求不高的场景，传统的 Actor 模型或更简单的池化方案可能更为合适。在使用前，务必在目标引擎版本上进行充分的性能测试和稳定性验证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]() （.uplugin 中未提供 DocsURL）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)