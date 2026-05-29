# Mass AI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | Mass AI |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

`MassAI` 是 `MassGameplay` 框架在人工智能领域的扩展，旨在为大规模实体（如人群、车辆队列）提供高效的 AI 功能。它解决的核心问题是：如何让成千上万个 AI 实体同时进行寻路、移动、行为决策和状态同步，同时保持极高的性能和较低的 CPU 开销。

该插件基于 ECS (Entity Component System) 架构，将 AI 功能分解为可组合的片段（Fragment）和处理器（Processor）。其中，`MassZoneGraphNavigation` 模块是关键，它利用 `ZoneGraph` 系统（一种预定义的道路/车道网格）实现高效的路径跟随和移动，避免了为每个实体单独进行昂贵的寻路计算。

## 使用场景

- 你在开发一款大型城市模拟游戏，需要数百个市民沿着人行道自然行走 → 使用 `MassZoneGraphNavigation` 控制移动。
- 你正在制作一个 RTS 或塔防游戏，需要大量单位沿固定路线巡逻或进攻 → 通过 `ZoneGraph` 定义路线，并使用本模块进行移动控制。
- 你需要为人群模拟（如体育场、广场）中的每个个体赋予基础的导航和避障能力 → `MassAI` 提供了处理大规模移动和避撞的框架。
- 你希望在 MassGameplay 框架下实现自定义的 AI 行为树逻辑 → 参考 `MassAIBehavior` 模块的设计模式。

## 蓝图用法

`MassAI` 的大部分功能是底层运行时模块，不直接暴露大量蓝图节点。主要的蓝图交互点在于通过 `Trait` 和 `DataAsset` 为实体配置 AI 属性。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ZoneGraph Navigation` (Trait) | 为实体模板添加基于 ZoneGraph 的导航能力。可在编辑器中配置车道过滤和查询半径。 | `UMassZoneGraphNavigationTrait` |
| `FMassZoneGraphNavigationParameters` | 配置参数结构体，包含 `LaneFilter` (车道过滤器) 和 `QueryRadius` (查询半径)，可在蓝图可编辑属性或数据资产中使用。 | 结构体 |

### 使用示例（蓝图描述）

1.  **配置实体模板**：在创建 `MassEntityTemplate` 资产时，通过“Add Trait”添加 `ZoneGraph Navigation`。
2.  **设置参数**：在 Trait 的详细面板中，设置 `Lane Filter`（例如，只允许在“人行道”类型的车道上移动）和 `Query Radius`（实体生成后寻找最近车道的搜索范围）。
3.  **动态触发移动**：运行时，通过 `Mass` 系统向实体发送信号或命令，驱动 `UMassZoneGraphPathFollowProcessor` 等处理器更新实体的 `FMassMoveTargetFragment`，从而控制移动。

## C++ 用法

核心用法围绕着向实体添加特定的 Fragment（数据）并编写或使用 Processor（逻辑）来处理它们。

### 头文件引入

```cpp
#include "MassZoneGraphNavigationFragments.h"
#include "MassZoneGraphNavigationProcessors.h"
#include "MassZoneGraphNavigationUtils.h"
```

### 基本用法：缓存车道数据

`FMassZoneGraphCachedLaneFragment` 缓存了实体当前及即将跟随的车道局部数据。以下示例展示了如何手动缓存一段车道数据（通常由处理器在内部完成）。

```cpp
// 假设你有一个有效的 ZoneGraph 存储和车道句柄
const FZoneGraphStorage& ZoneGraphStorage = /* ... */;
FZoneGraphLaneHandle CurrentLaneHandle = /* ... */;
float CurrentDistance = 100.0f;
float TargetDistance = 200.0f; // 想要预读取的目标距离

FMassZoneGraphCachedLaneFragment CachedLane;
// 缓存从 CurrentDistance 到 TargetDistance 之间的车道数据，并向外膨胀10厘米
CachedLane.CacheLaneData(ZoneGraphStorage, CurrentLaneHandle, CurrentDistance, TargetDistance, 10.0f);

// 之后可以查询缓存数据
FVector Point, Tangent;
CachedLane.GetPointAndTangentAtDistance(CurrentDistance, Point, Tangent);
```

*来源：`Public/MassZoneGraphNavigationFragments.h` 中 `FMassZoneGraphCachedLaneFragment` 类*

### 进阶用法：激活导航操作

`UE::MassNavigation` 命名空间提供了便捷函数来启动常见的导航操作。这些函数封装了设置多个 Fragment 状态的逻辑。

```cpp
// 包含工具头文件
#include "MassZoneGraphNavigationUtils.h"

// 假设已获取 World, Subsystem，以及实体所需的 Fragment 引用
UWorld* World = GetWorld();
const UZoneGraphSubsystem* ZoneGraphSubsystem = World->GetSubsystem<UZoneGraphSubsystem>();
FMassEntityHandle Entity = /* ... */;
FMassZoneGraphLaneLocationFragment LaneLocation = /* ... */; // 实体当前在 ZoneGraph 上的位置
FMassMoveTargetFragment MoveTarget;
FMassZoneGraphShortPathFragment ShortPath;
FMassZoneGraphCachedLaneFragment CachedLane;

// 准备一个路径请求
FZoneGraphShortPathRequest PathRequest;
PathRequest.TargetDistance = 1000.0f; // 沿车道移动10米
PathRequest.EndOfPathIntent = EMassMovementAction::Stand; // 到达后站立

// 激活移动操作，该函数会尝试为实体计算一条短路径
bool bSuccess = UE::MassNavigation::ActivateActionMove(
    *World,
    this, // 请求者
    Entity,
    *ZoneGraphSubsystem,
    LaneLocation,
    PathRequest,
    40.0f, // 代理半径
    150.0f, // 期望速度
    MoveTarget,
    ShortPath,
    CachedLane
);
```

*来源：`Public/MassZoneGraphNavigationUtils.h`*

## Demo 示例

下面的示例展示了一个极简的 Mass 处理器，它读取实体在 ZoneGraph 上的位置，并更新其移动目标点，以驱动物理移动。这是路径跟随处理器的核心逻辑简化版。

### `SimpleZoneGraphMoverProcessor.h`
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "MassProcessor.h"
#include "SimpleZoneGraphMoverProcessor.generated.h"

UCLASS()
class USimpleZoneGraphMoverProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    USimpleZoneGraphMoverProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};
```

### `SimpleZoneGraphMoverProcessor.cpp`
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.

#include "SimpleZoneGraphMoverProcessor.h"
#include "MassZoneGraphNavigationFragments.h"
#include "MassMovementFragments.h"

USimpleZoneGraphMoverProcessor::USimpleZoneGraphMoverProcessor()
{
    ExecutionOrder.ExecuteBefore.Add(UE::Mass::ProcessorGroupNames::Movement);
    bRequiresGameThreadExecution = false;
}

void USimpleZoneGraphMoverProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassZoneGraphShortPathFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassZoneGraphCachedLaneFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadWrite);
}

void USimpleZoneGraphMoverProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    EntityQuery.ForEachEntityChunk(Context, [this](FMassExecutionContext& Context)
    {
        const TConstArrayView<FMassZoneGraphShortPathFragment> ShortPathList = Context.GetFragmentView<FMassZoneGraphShortPathFragment>();
        const TConstArrayView<FMassZoneGraphCachedLaneFragment> CachedLaneList = Context.GetFragmentView<FMassZoneGraphCachedLaneFragment>();
        const TArrayView<FMassMoveTargetFragment> MoveTargetList = Context.GetMutableFragmentView<FMassMoveTargetFragment>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FMassZoneGraphShortPathFragment& ShortPath = ShortPathList[i];
            const FMassZoneGraphCachedLaneFragment& CachedLane = CachedLaneList[i];
            FMassMoveTargetFragment& MoveTarget = MoveTargetList[i];

            if (ShortPath.IsDone() || ShortPath.NumPoints == 0)
            {
                continue;
            }

            // 简单示例：直接使用短路径的第一个点作为移动目标
            // 实际逻辑会更复杂，需要根据进度插值计算目标点
            const FMassZoneGraphPathPoint& NextPoint = ShortPath.Points[0];
            MoveTarget.Center = NextPoint.Position; // 设置目标位置
            MoveTarget.DistanceToGoal = (NextPoint.Position - MoveTarget.Center).Size(); // 简化的距离计算
            // ... 设置速度、朝向等其他移动目标属性
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework`, `UnrealEd` | 用于编辑器集成和扩展。这是 `MassAI` 中多个 Runtime 模块的共同依赖，用于暴露属性和编辑器功能。 |
| `MassEntityEditor` | 用于 `MassAIDebug` 模块，提供 Mass 实体调试的编辑器支持。 |

*（注：该插件的核心运行时功能不依赖任何特殊模块，仅依赖 `MassGameplay`, `ZoneGraph` 等标准引擎模块。）*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 修复在最新 Windows SDK 上的编译错误，移除了对 INFINITY 宏的使用。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转换为浮点数时产生的编译器警告。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | 修复 Mass 调试器在实体无效时运行导致的崩溃。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了作用域枚举在格式化函数中使用时可能导致输出乱码的问题。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 与回放调试器相关的更新。 |

### 维护评价

`MassAI` 插件（及其核心模块 `MassZoneGraphNavigation`）处于**实验性**（`IsExperimentalVersion: true`）且**默认禁用**的状态。从其创建时间（2021年9月）来看，它是一个相对年轻的模块。

**积极方面**：
1.  **仍在维护**：最近的提交记录显示，在2026年5月仍有针对编译警告、错误和调试器稳定性的修复，表明 Epic 团队仍在对其进行维护和打磨。
2.  **解决核心问题**：它为 UE5 的 MassGameplay 框架提供了至关重要的大规模 AI 导航解决方案，是一个有明确目标和实际应用的系统。

**需要注意的方面**：
1.  **实验性质**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，这意味着其 API、功能和稳定性未来可能发生重大变化，不推荐直接用于生产环境的关键功能。
2.  **默认禁用**：需要手动在项目设置中启用。
3.  **文档和示例稀少**：官方文档和公开的详细使用示例相对较少，主要依赖源码和引擎内置测试用例学习。

**推荐使用情况**：
- **不推荐**用于即将发布的商业项目，除非你愿意承担其 API 不稳定带来的维护风险，并有能力进行深入的源码研究和问题排查。
- **推荐**用于**原型开发、技术研究、内部项目或专门针对大规模实体模拟的特定系统**。它代表了 UE5 在该领域的前沿探索，学习价值很高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassZoneGraphNavigation)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)