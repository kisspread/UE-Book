# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模玩法 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产、演示用例） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine 的**大规模智能体（Agent）模拟**系统。它建立在底层 ECS 框架 MassEntity 之上，为游戏玩法场景（如人群、AI 代理、大量可交互物体）提供了高效运行所需的全部上层功能。

这个插件解决了在单个游戏关卡中模拟和控制**数以万计**的动态实体所带来的性能和管理挑战。它包含从实体的生成、移动、表现（Actor 或 ISM）、LOD（细节层次）管理，到网络复制、交互（Smart Objects）和调试工具的全套方案。其核心设计思想是数据导向（Data-Oriented），通过将功能分解为可组合的片段（Fragments）和处理器（Processors）来实现极致的性能和可扩展性。

## 使用场景

-   **你需要模拟一个大规模城市交通系统**：数千辆车辆和行人需要高效寻路、避障和渲染，同时保持合理的性能。使用 MassGameplay 的 `MassMovement` 和 `MassLOD` 模块。
-   **你需要制作一个包含大量可破坏或可交互物体的游戏**：例如，一个战场上有数千个弹药箱、沙袋或碎片。使用 `MassRepresentation` 和 `MassSpawner`。
-   **你的游戏需要大量 AI 控制的 NPC**，例如 RTS 游戏中的士兵或开放世界中的村民。使用 `MassAI`（另一个配套插件）与 `MassGameplay` 结合。
-   **你需要在网络游戏中同步大量实体的状态**。使用 `MassReplication` 模块。

## 蓝图用法

MassGameplay 的大部分核心逻辑运行在 C++ 的 Mass 处理器中，通过片段和标签进行数据驱动，直接暴露给蓝图的高级节点较少。但可以通过 `MassSpawner` 等模块在蓝图中触发实体的生成。

### 核心节点

本模块 (MassCommon) 主要定义了基础数据类型，不直接提供蓝图节点。蓝图可用的节点分散在其他模块中，例如 `MassSpawner` 的生成相关节点。

### 使用示例（蓝图描述）

通常，你会在场景中放置一个 `MassSpawner` Actor，配置要生成的实体类型（Archetype）和数量。其他 MassGameplay Actor，如 `MassAgentComponent` 或自定义的处理器管理器，负责定义这些实体的行为。

## C++ 用法

MassCommon 模块为整个 MassGameplay 系统提供了核心数据类型和工具函数。

### 头文件引入

```cpp
#include "MassCommonTypes.h"
#include "MassCommonFragments.h"
#include "MassCommonUtils.h"
```

### 基本用法

**使用压缩数据类型以节省内存**：当定义代表大量实体的数据结构时，使用 `FMassInt16Real` 等类型代替 `float`。

```cpp
// 来源: Source/MassCommon/Public/MassCommonTypes.h
// 用于定义一个节省内存的实体位置片段
USTRUCT()
struct FCompressedPositionFragment : public FMassFragment
{
    GENERATED_BODY()

    // 使用 16 位整数存储位置，精度为 1 厘米
    UPROPERTY()
    FMassInt16Vector Position;

    void SetFromWorldLocation(const FVector& WorldLocation)
    {
        Position.Set(WorldLocation);
    }

    FVector GetWorldLocation() const
    {
        return Position.Get();
    }
};
```

**使用确定性随机序列**：在需要可重现或跨客户端一致的随机行为时使用。

```cpp
// 来源: Source/MassCommon/Public/RandomSequence.h
// 在处理器中为每个实体生成一个确定的随机种子，用于决策
const int32 EntityIndex = Entity.GetIndex();
const float RandomValue = UE::RandomSequence::FRandRange(EntityIndex, 0.0f, 1.0f);
if (RandomValue > 0.8f)
{
    // 执行某个特定行为
}
```

### 进阶用法

结合多个片段和工具函数来构建一个自定义的实体行为。

```cpp
// 来源: Source/MassCommon/Public/MassCommonFragments.h, MassCommonUtils.h
// 一个简单的“徘徊”处理器，要求实体拥有位置和半径片段
USTRUCT()
struct FWanderFragment : public FMassFragment
{
    GENERATED_BODY()
    FVector TargetLocation;
};

// 在处理器中
void UWanderProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 使用确定性随机种子覆盖，用于测试
    if (UE::Mass::Utils::IsDeterministic())
    {
        // 在某些调试场景下强制使用固定种子
    }

    // 查询所有拥有位置、半径和我们自定义徘徊片段的实体
    auto Query = EntityManager.CreateQuery<FCompressedPositionFragment, FAgentRadiusFragment, FWanderFragment>();

    Query.ForEachEntityChunk(Context, [&](FMassExecutionContext& Context)
    {
        // ... 遍历实体，更新 TargetLocation，并根据 FAgentRadiusFragment 进行避障计算
    });
}
```

## Demo 示例

以下是一个展示如何在自定义片段中组合使用 MassCommon 类型的最小 C++ 示例。

### MyCustomFragment.h
```cpp
// 文件路径: YourProject/Source/YourProject/Public/MyCustomFragment.h
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTypes.h"
#include "MassCommonTypes.h"
#include "MassCommonFragments.h"
#include "MyCustomFragment.generated.h"

/**
 * 一个自定义的智能体数据片段，结合了 MassCommon 的基础类型。
 * 这个片段可以附加到 Mass Archetype 上，供处理器读写。
 */
USTRUCT()
struct FMyCustomAgentFragment : public FMassFragment
{
    GENERATED_BODY()

    // 使用压缩向量节省内存（精度 1cm）
    UPROPERTY()
    FMassInt16Vector GoalLocation;

    // 使用压缩半径（精度 1cm）
    UPROPERTY()
    FMassInt16Real CurrentSpeed;

    // 引用基础的 AgentRadius 片段（已由系统提供）
    // 注意：这里仅作演示，实际使用中通常在同一 Archetype 中与 FAgentRadiusFragment 并列。
    // UPROPERTY()
    // FAgentRadiusFragment RadiusFragment; // 直接包含不推荐，应作为独立片段。

    // 设置目标位置的辅助函数
    void SetGoal(const FVector& InGoal)
    {
        GoalLocation.Set(InGoal);
    }

    FVector GetGoal() const
    {
        return GoalLocation.Get();
    }

    void SetSpeed(const float Speed)
    {
        CurrentSpeed.Set(Speed);
    }

    float GetSpeed() const
    {
        return CurrentSpeed.Get();
    }
};
```

## 模块依赖

MassGameplay 及其子模块对外部模块的依赖已被其内部模块封装。对于 **使用 MassGameplay 的游戏项目**，通常只需在游戏模块的 `.Build.cs` 中依赖相关的 Mass 模块（如 `MassGameplay`, `MassAI` 等），无需关心其内部依赖的 `UnrealEd` 等编辑器模块。

**特殊依赖说明**：MassCommon 模块的 Build.cs 列出了对 `UnrealEd` 的依赖，这可能是因为它提供了编辑器工具、序列化支持或调试可视化功能，这些在打包后（Shipping Build）会被剔除。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的基础 ECS 框架（作为基础依赖） |
| `SmartObjectsModule` | 为 `MassSmartObjects` 子模块提供智能对象框架支持 |
| `StateTreeModule` | 为状态树集成提供支持（用于 AI 决策） |
| `GameplayBehaviorSmartObjectsModule` | 将游戏行为与智能对象连接 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤回了对 MassAgentComponent 的先前改动，修复了潜在的兼容性问题。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 修复了表示系统：在切换掉实例化静态网格体（ISM）前会等待 Actor 准备就绪，避免渲染错误。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了人群模拟中非傀儡（non-puppet）Actor 的处理逻辑。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了 LOD 计算器中针对每个观察者的 LOD 路径的一系列历史遗留 Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 表示系统重构：将两处手动计算的 `bDoKeepActorExtraFrame` 改为使用新的统一接口。 |

### 维护评价

MassGameplay 是一个**大型、复杂且活跃维护的核心系统**。

-   **年龄与状态**：尽管标记为“实验性”且默认禁用，但它自 2021 年存在至今，是 Epic 用于自家项目（如《堡垒之夜》大规模模式）的成熟技术栈。
-   **更新频率**：从近期 git 历史看，**维护非常活跃**（最近一次更新在 2026 年 5 月）。更新内容集中在 Bug 修复、表示系统优化和稳定性提升，表明该插件处于持续迭代和打磨阶段。
-   **推荐度**：**强烈推荐**给需要实现大规模实体模拟的项目。虽然存在实验性标签且有一定学习曲线，但它是目前 UE 中处理该类问题的**唯一官方且高性能解决方案**。使用时需注意其接口可能随着版本迭代而发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/mass-gameplay-in-unreal-engine/) (UE5 官方文档中的 Mass Gameplay 概述)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)