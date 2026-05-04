# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是基于 Unreal Engine 5 的 MassEntity（ECS）框架构建的**大规模智能体（Agent）模拟系统**。它并非一个简单的组件，而是一套完整的、用于驱动成千上万个实体（如 NPC、子弹、粒子、可交互物体）运行时行为的**游戏逻辑框架**。

它解决的核心问题是：如何在保证高性能的前提下，让海量实体（数万甚至数十万）能够执行复杂的游戏逻辑（如移动、感知、决策、状态同步）。传统的 Actor 模型在处理如此规模时会遇到严重的性能瓶颈，而 MassGameplay 通过以下方式解决：

1.  **ECS 架构**：将数据（Fragment）与行为（Processor）分离，数据以连续内存块（Chunk）存储，极大提高了 CPU 缓存命中率。
2.  **分阶段处理**：将游戏逻辑分解为多个处理阶段（Phase），如 `Preparation`, `Logic`, `Movement`, `Representation` 等，每个阶段由一组处理器（Processor）按顺序执行，结构清晰且易于优化。
3.  **LOD 与表示管理**：根据实体与玩家的距离和重要性，动态切换其表现形式（如完整 Actor、简化网格、点状表示），甚至完全停止逻辑更新，以节省资源。
4.  **网络复制**：为大规模实体提供了高效的网络同步方案，解决了传统 Actor 复制在数量巨大时的带宽问题。

简而言之，MassGameplay 是 UE5 中实现“万人同屏”或“海量动态物体”场景的**官方高级解决方案**。

## 使用场景

-   **即时战略游戏 (RTS)**：管理成千上万的士兵、车辆单位，执行寻路、攻击、阵型等逻辑。
-   **大型多人在线角色扮演游戏 (MMORPG)**：处理大量玩家角色、NPC、宠物的移动、状态同步和简单 AI。
-   **开放世界游戏**：驱动城市中的行人、车辆，或野外生物群落的动态行为。
-   **弹幕射击游戏**：高效管理成千上万的子弹、投射物。
-   **大规模模拟游戏**：如城市建造、生态系统模拟，需要大量实体进行独立计算。
-   **任何需要高性能处理大量相似或简单逻辑实体的场景**。

## 蓝图用法

MassGameplay 的核心逻辑通常在 C++ 中通过处理器（Processor）实现，但提供了关键的子系统和类供蓝图交互，主要用于控制模拟和查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Mass Simulation Subsystem` | 获取当前世界的 Mass 模拟子系统实例。 | `UMassSimulationSubsystem` |
| `Pause Simulation` | 暂停整个 Mass 模拟的处理器执行。 | `UMassSimulationSubsystem` |
| `Resume Simulation` | 恢复 Mass 模拟的处理器执行。 | `UMassSimulationSubsystem` |
| `Is Simulation Paused` | 查询模拟是否处于暂停状态。 | `UMassSimulationSubsystem` |
| `Register Dynamic Processor` | 在运行时动态注册一个处理器到模拟中。 | `UMassSimulationSubsystem` |
| `Unregister Dynamic Processor` | 在运行时动态注销一个处理器。 | `UMassSimulationSubsystem` |
| `Is During Mass Processing` | 查询当前是否正处于 Mass 处理阶段（用于避免在处理期间修改数据）。 | `UMassSimulationSubsystem` |

### 使用示例（蓝图描述）

1.  **暂停/恢复游戏**：
    *   在游戏暂停菜单的“暂停”按钮事件中，调用 `Get Mass Simulation Subsystem`，然后调用 `Pause Simulation`。
    *   在“继续”按钮事件中，调用 `Resume Simulation`。

2.  **动态启用/禁用 AI 行为**：
    *   创建一个自定义的 `UMassProcessor` 子类（C++），用于处理某种特定的 AI 逻辑。
    *   在蓝图中，当需要启用该 AI 时（如玩家进入区域），获取子系统并调用 `Register Dynamic Processor`，传入该处理器的实例。
    *   当需要禁用时，调用 `Unregister Dynamic Processor`。

## C++ 用法

MassGameplay 的核心用法是编写自定义的 `UMassProcessor` 来处理实体数据。

### 头文件引入

```cpp
#include "MassProcessor.h"
#include "MassEntityTypes.h"
#include "MassSimulationSubsystem.h"
```

### 基本用法

以下是一个简单的处理器示例，它将所有带有 `FTransformFragment` 的实体的 Z 轴位置每帧增加 10 个单位。

```cpp
// MyRisingProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyRisingProcessor.generated.h"

UCLASS()
class UMyRisingProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyRisingProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MyRisingProcessor.cpp
#include "MyRisingProcessor.h"
#include "MassMovementFragments.h" // 假设 FTransformFragment 在此

UMyRisingProcessor::UMyRisingProcessor()
{
    // 设置处理器在哪个阶段执行，例如在 Movement 阶段
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::Movement;
}

void UMyRisingProcessor::ConfigureQueries()
{
    // 配置查询：需要哪些 Fragment（数据）
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
}

void UMyRisingProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有符合查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中所有实体的 TransformFragment 数组
        const TArrayView<FTransformFragment> TransformList = Context.GetMutableFragmentView<FTransformFragment>();
        const int32 NumEntities = Context.GetNumEntities();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            // 修改每个实体的 Transform
            FTransform& Transform = TransformList[i].GetMutableTransform();
            FVector Location = Transform.GetLocation();
            Location.Z += 10.0f; // 每帧上升 10 单位
            Transform.SetLocation(Location);
        }
    });
}
```

### 进阶用法

结合 `UMassSimulationSubsystem` 的事件来动态控制处理器。

```cpp
// 在某个游戏模式或管理器类中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取模拟子系统
    UMassSimulationSubsystem* MassSubsystem = UWorld::GetSubsystem<UMassSimulationSubsystem>(GetWorld());
    if (MassSubsystem)
    {
        // 监听模拟开始事件
        MassSubsystem->GetOnSimulationStarted().AddUObject(this, &AMyGameMode::OnMassSimulationStarted);

        // 动态注册一个处理器
        MyDynamicProcessor = NewObject<UMyRisingProcessor>(this);
        MassSubsystem->RegisterDynamicProcessor(*MyDynamicProcessor);
    }
}

void AMyGameMode::OnMassSimulationStarted(UWorld* World)
{
    UE_LOG(LogTemp, Log, TEXT("Mass Simulation has started in world: %s"), *World->GetName());
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个自定义处理器并将其注册到模拟中。

```cpp
// SimpleMassProcessor.h
#pragma once
#include "MassProcessor.h"
#include "SimpleMassProcessor.generated.h"

UCLASS()
class USimpleColorChangeProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    USimpleColorChangeProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// SimpleMassProcessor.cpp
#include "SimpleMassProcessor.h"
#include "MassRepresentationFragments.h" // 假设 FStaticMeshInstanceVisualizationFragment 在此

USimpleColorChangeProcessor::USimpleColorChangeProcessor()
{
    ProcessingPhase = EMassProcessingPhase::Representation; // 在表示阶段执行
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
}

void USimpleColorChangeProcessor::ConfigureQueries()
{
    // 需要一个可写的静态网格实例可视化 Fragment
    EntityQuery.AddRequirement<FStaticMeshInstanceVisualizationFragment>(EMassFragmentAccess::ReadWrite);
}

void USimpleColorChangeProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [](FMassExecutionContext& Context)
    {
        TArrayView<FStaticMeshInstanceVisualizationFragment> VizFragments = Context.GetMutableFragmentView<FStaticMeshInstanceVisualizationFragment>();
        for (FStaticMeshInstanceVisualizationFragment& Viz : VizFragments)
        {
            // 随机改变颜色（示例逻辑）
            Viz.Color = FLinearColor::MakeRandomColor();
        }
    });
}
```

## 模块依赖

要使用 MassGameplay 插件，你的项目模块需要依赖以下核心模块（除了标准的 Core/Engine 等）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的基石，提供 ECS 核心框架（实体、片段、处理器、世界）。 |
| `MassEntityEditor` | 提供编辑器支持，用于可视化调试和编辑 Mass 实体。 |
| `MassSpawner` | 提供实体生成器（Spawner）和模板（Template）系统，用于在世界中创建 Mass 实体。 |
| `MassRepresentation` | 处理实体的视觉表现，如 Actor、网格实例、点状表示之间的切换。 |
| `MassMovement` | 提供移动相关的片段和处理器，如速度、转向、寻路集成。 |
| `MassSignals` | 提供实体间的信号/事件通信系统。 |
| `MassSmartObjects` | 集成 SmartObject 系统，让 Mass 实体可以与场景中的交互点互动。 |

## 维护状态

### 近期更新

```
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 939cc6e51c10 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- b737320b78c1 PR #12696: Add ability to Pause and Resume a Mass Simulation
```

### 维护评价

MassGameplay 是一个**活跃维护中**的实验性插件。

-   **创建时间**：约 4 年前（2021年），相对较新，是 UE5 时代的重要特性。
-   **更新频率**：从 git 历史看，近期有代码优化（内联宏、导出符号）和功能增强（暂停/恢复模拟），表明 Epic 仍在积极开发和改进。
-   **状态**：`.uplugin` 中 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，明确标记为**实验性**。这意味着其 API 可能在未来版本中发生变化，不建议在追求长期稳定的商业项目核心功能中直接使用，但非常适合原型开发、技术预研或对性能有极致要求的特定场景。
-   **推荐度**：如果你需要处理海量实体，且项目可以接受实验性 API 的潜在变动，MassGameplay 是 UE5 官方提供的最强有力的工具，**强烈推荐学习和使用**。务必关注其版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mass-gameplay-in-unreal-engine/) (UE5 官方文档中的 Mass Gameplay 章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)