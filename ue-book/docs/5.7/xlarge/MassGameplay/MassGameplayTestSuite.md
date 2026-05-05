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
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 UE5 MassEntity (ECS) 框架在游戏玩法层面的完整实现。它解决的核心问题是：如何在保持高性能的同时，为成千上万的游戏实体（如 NPC、车辆、子弹、环境物体）赋予复杂的游戏逻辑和行为。

传统的 Actor 模型在处理海量实体时会遇到严重的性能瓶颈（内存占用高、Tick 开销大）。MassGameplay 基于 MassEntity 的数据导向设计，将实体的状态（Fragment）和行为（Processor）分离，使得对大量实体的批量处理变得极其高效。它提供了从实体生成、移动、视觉表示、LOD 管理、网络复制到与游戏系统（如 EQS、SmartObjects）集成的全套解决方案，是构建大规模模拟游戏（如 RTS、开放世界 NPC 群、弹幕射击）的基石。

## 使用场景

- **你需要模拟成千上万的单位**：例如即时战略游戏（RTS）中的士兵、车辆，或塔防游戏中的敌人波次。
- **你需要高效管理大量动态物体**：例如开放世界中的野生动物群、飞鸟、可破坏的环境碎片。
- **你需要实现复杂的群体行为**：例如 NPC 的巡逻、聚集、避障，这些行为可以通过 MassProcessor 批量高效计算。
- **你需要为大量实体实现网络同步**：MassReplication 模块提供了针对 ECS 架构优化的网络复制方案。
- **你需要将 MassEntity 与现有游戏系统集成**：例如通过 MassEQS 为大量实体执行环境查询，或通过 MassSmartObjects 让实体与场景交互点互动。

## 蓝图用法

MassGameplay 的蓝图接口主要集中在实体生成、配置和调试上。核心功能通过 `MassSpawner` 和 `MassRepresentation` 模块暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spawn Entities` | 根据指定的 `MassEntityConfig` 和数量，在指定位置生成实体。 | `UMassSpawnerSubsystem` |
| `Get Entity Config` | 通过名称获取一个 `UMassEntityConfig` 资产。 | `UMassEntityConfigBlueprintLibrary` |
| `Set Static Mesh` | 为实体的可视化表示设置静态网格体。 | `UMassRepresentationSubsystem` |
| `Set Actor Instance` | 为实体的可视化表示设置一个 Actor 原型。 | `UMassRepresentationSubsystem` |
| `Get Entity Location` | 获取指定实体句柄的世界位置。 | `UMassEntitySubsystem` |
| `Set Entity Location` | 设置指定实体句柄的世界位置。 | `UMassEntitySubsystem` |
| `Signal Entities` | 向一组实体发送信号，触发其关联的处理器。 | `UMassSignalSubsystem` |

### 使用示例（蓝图描述）

1.  **生成实体**：
    - 创建一个 `UMassEntityConfig` 资产，在其中定义实体的初始 Fragment 组合（例如，包含位置、移动速度、网格体信息）。
    - 在蓝图中，调用 `Get Entity Config` 节点获取该配置资产。
    - 使用 `Spawn Entities` 节点，传入配置、生成数量和生成位置，即可批量生成实体。

2.  **控制实体外观**：
    - 生成后，可以通过 `Set Static Mesh` 或 `Set Actor Instance` 节点动态更改实体的视觉表现。这通常用于实现 LOD（不同距离显示不同精度的模型）。

3.  **与实体交互**：
    - 使用 `Get Entity Location` 查询实体位置，用于游戏逻辑判断。
    - 使用 `Signal Entities` 向实体发送“攻击”、“移动到目标点”等信号，触发其内部的 MassProcessor 进行响应。

## C++ 用法

MassGameplay 的 C++ 用法核心在于定义自定义的 Fragment（数据）和 Processor（逻辑），并与现有的 Mass 子系统交互。

### 头文件引入

```cpp
#include "MassEntityTypes.h" // 基础类型
#include "MassEntitySubsystem.h" // 实体子系统
#include "MassSpawnerSubsystem.h" // 生成子系统
#include "MassCommonFragments.h" // 通用 Fragment，如 FTransformFragment
#include "MassMovementFragments.h" // 移动相关 Fragment
```

### 基本用法

以下示例展示了如何定义一个简单的自定义 Fragment 和一个移动 Processor。
（来源：基于 `MassGameplayTestSuite` 和 `MassMovement` 模块的测试用例模式）

```cpp
// MyFragments.h
#pragma once
#include "MassEntityTypes.h"

// 定义一个自定义 Fragment，用于存储实体的生命值
USTRUCT()
struct FHealthFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Mass")
    float CurrentHealth = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Mass")
    float MaxHealth = 100.0f;
};
```

```cpp
// MyProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyFragments.h"

// 定义一个处理器，用于每帧减少所有实体的生命值
UCLASS()
class UHealthDecayProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UHealthDecayProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询：需要包含 FHealthFragment 和 FTransformFragment 的实体
    FMassEntityQuery EntityQuery;
};
```

```cpp
// MyProcessor.cpp
#include "MyProcessor.h"
#include "MassCommonFragments.h"

UHealthDecayProcessor::UHealthDecayProcessor()
{
    // 设置处理器在模拟阶段执行
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void UHealthDecayProcessor::ConfigureQueries()
{
    // 配置查询，要求实体同时拥有 FHealthFragment 和 FTransformFragment
    EntityQuery.AddRequirement<FHealthFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
}

void UHealthDecayProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 遍历所有匹配查询的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中的 Fragment 数组
        const TArrayView<FHealthFragment> HealthList = Context.GetMutableFragmentView<FHealthFragment>();
        const int32 NumEntities = Context.GetNumEntities();

        // 批量处理：每帧减少 1 点生命值
        for (int32 i = 0; i < NumEntities; ++i)
        {
            HealthList[i].CurrentHealth -= 1.0f;
            // 可以在此处添加死亡逻辑，例如当生命值<=0时销毁实体
        }
    });
}
```

### 进阶用法

结合 `MassSpawnerSubsystem` 在运行时生成实体，并为其添加自定义 Fragment。

```cpp
// 在某个游戏模式或 Actor 的 BeginPlay 中
void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    UMassSpawnerSubsystem* SpawnerSubsystem = UWorld::GetSubsystem<UMassSpawnerSubsystem>(GetWorld());
    if (SpawnerSubsystem)
    {
        // 1. 准备实体配置（通常从资产加载，这里动态创建）
        FMassEntityConfig Config;
        // 添加基础 Fragment
        Config.AddFragment<FTransformFragment>();
        Config.AddFragment<FHealthFragment>();
        // 可以添加更多 Fragment，如移动、表示等

        // 2. 定义生成位置
        TArray<FTransform> SpawnTransforms;
        for (int32 i = 0; i < 100; ++i)
        {
            SpawnTransforms.Add(FTransform(FVector(i * 100.f, 0.f, 0.f)));
        }

        // 3. 批量生成实体
        SpawnerSubsystem->BatchSpawnEntities(Config, SpawnTransforms);
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个带有自定义“颜色” Fragment 的实体，并用一个 Processor 随机改变其颜色。

```cpp
// ColorFragment.h
#pragma once
#include "MassEntityTypes.h"
#include "ColorFragment.generated.h"

USTRUCT()
struct FColorFragment : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Mass")
    FLinearColor Color = FLinearColor::White;
};
```

```cpp
// RandomColorProcessor.h
#pragma once
#include "MassProcessor.h"
#include "ColorFragment.generated.h"

UCLASS()
class URandomColorProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    URandomColorProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

```cpp
// RandomColorProcessor.cpp
#include "RandomColorProcessor.h"
#include "MassCommonFragments.h"

URandomColorProcessor::URandomColorProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EMassProcessingPhase::PrePhysics;
}

void URandomColorProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FColorFragment>(EMassFragmentAccess::ReadWrite);
}

void URandomColorProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        TArrayView<FColorFragment> ColorList = Context.GetMutableFragmentView<FColorFragment>();
        const int32 NumEntities = Context.GetNumEntities();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            // 每帧随机改变颜色
            ColorList[i].Color = FLinearColor::MakeRandomColor();
        }
    });
}
```

## 模块依赖

要使用 MassGameplay 插件，你的项目模块通常需要依赖以下核心模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassEntity 核心框架，提供 ECS 基础架构。 |
| `MassEntityEditor` | MassEntity 编辑器支持，用于资产编辑和调试。 |
| `SmartObjectsModule` | 智能对象系统，用于 MassSmartObjects 模块集成。 |
| `GameplayAbilities` | （可选）如果使用 MassGameplayExternalTraits 与 GAS 集成。 |
| `AIModule` | （可选）如果使用 MassEQS 进行环境查询。 |

## 维护状态

### 近期更新

```
- 39120795f693 [Mass] Made fragment value setting directly via archetypes properly handle the given fragment type not being a part of a given archetype's composition
- a01ceff5fb6d [Mass] Limited access to FMassArchetypeComposition's bitsets in preparation for near-future changes
- 372bd724a122 [Mass] more Mass-related header cleanups.
```

### 维护评价

MassGameplay 是 UE5 MassEntity 生态系统的核心玩法层实现，由 Epic Games 官方维护。

- **创建时间**：2021年9月，与 UE5 早期开发同步，是较新的系统。
- **近期活动**：最近的提交集中在底层架构优化和清理（如 Fragment 处理、头文件整理），表明系统仍在积极演进和稳定化。
- **维护状态**：**活跃维护中**。作为实验性（`IsExperimentalVersion=true`）但默认未启用（`EnabledByDefault=false`）的插件，它处于快速迭代期，API 可能发生变化。
- **已知限制**：作为实验性功能，其 API 和最佳实践可能随版本更新。文档相对较少，主要依赖源码和测试用例学习。
- **推荐使用**：**推荐用于新项目或愿意承担实验性 API 变更风险的项目**。对于需要大规模实体模拟的游戏，它是目前 UE5 官方提供的最强大、最高效的解决方案。建议密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)