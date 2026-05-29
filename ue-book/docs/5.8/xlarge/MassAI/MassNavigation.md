# MassAI

> AI-specific functionality extending MassGameplay

| 属性 | 值 |
|---|---|
| 中文名 | 大规模AI导航 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavMeshNavigation` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 插件是 UE5 MassEntity 框架（MassGameplay）在 AI 领域的功能扩展。它并非一个独立的 AI 系统，而是为基于 MassEntity 框架构建的大量 AI 代理（Agent）提供核心的**导航、避障和运动转向**能力。

它的存在是为了解决在超大规模场景（例如成千上万的 NPC 或载具）中，传统的逐个 Actor 进行路径规划和移动模拟所带来的性能瓶颈。通过利用 MassEntity 的数据驱动和批量处理架构，MassAI 能够实现高性能的群体模拟。

## 使用场景

-   **大规模人群模拟**：模拟城市、体育场或战场中的数千名 NPC 的移动、聚集和避让。
-   **交通流模拟**：管理大量车辆或行人的交通网络，实现流畅的流动和路口交互。
-   **RTS/Swarm 游戏**：控制大量单位在复杂地形中移动、攻击阵型变换，并避免单位互相穿插。
-   **开放世界游戏**：在玩家视野内动态生成并管理大量远处或近处的 AI 角色，维持合理的移动行为。

## 蓝图用法

MassAI 主要通过向 MassEntity 模板添加特定的 **Trait（特征）** 来使用，这些 Trait 会自动附加必要的 Fragment（数据片段）并注册对应的 Processor（处理器）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Steering` (Trait) | 为实体添加运动转向能力，配置移动和站立时的转向参数。 | `UMassSteeringTrait` |
| `Avoidance` (Trait) | 为实体添加障碍物和人群避让能力，配置移动和站立时的避障参数。 | `UMassObstacleAvoidanceTrait` |
| `Navigation Obstacle` (Trait) | 将实体标记为导航障碍物，使其能被其他代理检测和避让。 | `UMassNavigationObstacleTrait` |
| `Smooth Orientation` (Trait) | 平滑更新实体的朝向，使其跟随移动方向或目标朝向。 | `UMassSmoothOrientationTrait` |

### 使用示例（蓝图描述）

1.  **创建或编辑一个 MassEntity 模板**（例如在 `UDataAsset` 或实体配置资产中）。
2.  在模板的 `Trait` 列表中，添加 `Steering`、`Avoidance` 等 Trait。
3.  展开每个 Trait，根据需求调整其内部参数（如 `ReactionTime`, `PredictiveAvoidanceTime` 等）。
4.  当带有这些 Trait 的实体被创建时，MassAI 的处理器将自动接管其移动、避障和转向计算。

## C++ 用法

### 头文件引入

```cpp
#include "MassNavigationFragments.h"
#include "Avoidance/MassAvoidanceFragments.h"
#include "Steering/MassSteeringFragments.h"
#include "MassNavigationSubsystem.h"
#include "MassNavigationProcessors.h"
```

### 基本用法

在 MassEntity 的 Fragment 组合中使用 MassAI 提供的 Fragment。

```cpp
// 定义一个需要导航能力的实体结构体
USTRUCT()
struct FMyAIEntityFragment : public FMassFragment
{
    GENERATED_BODY()

    // 移动目标，由 MassNavigation 系统更新
    UPROPERTY()
    FMassMoveTargetFragment MoveTarget;

    // 转向数据，由转向处理器更新
    UPROPERTY()
    FMassSteeringFragment Steering;

    // 避障碰撞体数据
    UPROPERTY()
    FMassAvoidanceColliderFragment Collider;

    // 其他自定义数据...
};
```

### 进阶用法

手动查询和操作导航子系统及障碍物网格。

```cpp
// 在某个处理器或子系统中，访问全局的障碍物网格
UMassNavigationSubsystem* NavSubsystem = UWorld::GetSubsystem<UMassNavigationSubsystem>(World);
if (NavSubsystem)
{
    FNavigationObstacleHashGrid2D& ObstacleGrid = NavSubsystem->GetObstacleGridMutable();

    // 例如，查询某个位置附近的障碍物
    TArray<FMassNavigationObstacleItem> NearbyObstacles;
    ObstacleGrid.FindNearbyElements(Location, [&](const FMassNavigationObstacleItem& Item)
    {
        NearbyObstacles.Add(Item);
        return true; // 继续搜索
    });
}
```

## Demo 示例

以下是一个最小化示例，展示如何在 C++ 中定义一个具备基本导航能力的 MassEntity 模板。

```cpp
// MyAINavEntity.h
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTypes.h"
#include "MassNavigationFragments.h"
#include "Steering/MassSteeringFragments.h"
#include "Avoidance/MassAvoidanceFragments.h"

USTRUCT()
struct FMyAINavEntity : public FMassSharedFragment
{
    GENERATED_BODY()
};

USTRUCT()
struct FMyAINavEntityData : public FMassFragment
{
    GENERATED_BODY()

    UPROPERTY()
    FMassMoveTargetFragment MoveTarget;

    UPROPERTY()
    FMassSteeringFragment Steering;

    UPROPERTY()
    FMassAvoidanceColliderFragment Collider;

    UPROPERTY()
    FMassMovingSteeringParameters SteeringParams;

    UPROPERTY()
    FMassMovingAvoidanceParameters AvoidanceParams;
};
```

```cpp
// MyAINavEntity.cpp
#include "MyAINavEntity.h"
#include "MassEntityTemplateRegistry.h"

// 注册模板
void RegisterMyAINavEntityTemplate(FMassEntityManager& EntityManager)
{
    FMassEntityTemplateBuildContext BuildContext;
    BuildContext.AddFragment<FMyAINavEntityData>();
    BuildContext.AddSharedFragment<FMyAINavEntity>();

    // 可以通过 BuildContext.AddTag<...>() 添加特定标签，如 FMassInNavigationObstacleGridTag

    const FMassEntityTemplate& Template = EntityManager.CreateEntityTemplate(BuildContext);
    // 使用 Template 来实例化实体...
}
```

## 模块依赖

使用 `MassNavigation` 模块时，你的模块需要在 `Build.cs` 中添加以下依赖（取决于你用到的功能）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 MassEntity 框架，必须依赖。 |
| `MassGameplay` | 提供 MassGameplay 基础设施，通常与 MassEntity 一起使用。 |
| `MassNavigation` | 本插件的核心导航与避障逻辑。 |
| `MassNavMeshNavigation` | （可选）用于与 NavMesh 集成的路径跟随。 |
| `MassZoneGraphNavigation` | （可选）用于与 ZoneGraph 系统集成的导航。 |

**注意**：该插件的多个模块（如 `MassAIBehavior`, `MassNavigation`）在 `Build.cs` 中声明了对 `EditorFramework` 和 `UnrealEd` 的依赖。这通常意味着这些模块可能包含一些编辑器专用功能或调试工具。对于纯运行时使用，依赖 `MassNavigation` 本身通常足够。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8e83e6bf` | Remove use of INFINITY to fix compile error on latest Windows SDK | 移除 INFINITY 宏的使用以修复最新 Windows SDK 上的编译错误。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量被截断为浮点数的警告。 |
| 2026-05-12 | `328c7999` | [Mass] PR #14001: Fix Mass debugger running with invalid entity | [Mass] 修复 Mass 调试器在处理无效实体时运行的问题。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用的 scoped enum 可能导致输出乱码的问题。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | [RewindDebugger] （相关改动，可能涉及 Mass 调试功能）。 |

### 维护评价

MassAI 是一个活跃维护的实验性插件。从近期的提交记录可以看出，Epic 的工程师正在持续进行代码质量改进、编译兼容性修复和功能修正（如调试器修复）。这些更新表明该插件正在被用于生产环境，并得到持续的优化。

**推荐使用**：对于需要实现大规模群体 AI 行为的项目，MassAI 是官方提供且持续维护的解决方案，值得评估和使用。由于它被标记为实验性，且默认未启用，使用者需要自行评估其稳定性和是否符合项目需求，并准备好可能需要进行一些底层调试或自定义。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/MassAI)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的路径中发现独立测试目录)