# Mass AI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `MassNavigation` (Runtime), `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine MassGameplay 框架的 AI 扩展插件。它为大规模实体（Mass Entity）提供了一套完整的 AI 行为与导航解决方案，旨在高效处理成千上万个 AI 代理的移动、避障、转向和行为逻辑。该插件解决了在传统 Actor 模型下，处理海量 AI 代理时性能瓶颈的问题，通过数据驱动的 ECS（实体组件系统）架构，实现了高度并行化和优化的 AI 模拟。

## 使用场景

- **开放世界游戏**：你需要在大地图中模拟成千上万的 NPC、平民或野生动物，且要求它们具有基本的导航和避障能力。
- **即时战略（RTS）游戏**：你需要控制大量单位进行编队移动、寻路和相互避让。
- **大规模模拟**：你需要创建一个包含大量自主代理的模拟系统，例如交通模拟、人群模拟。
- **性能敏感的 AI**：你的项目对 AI 的 CPU 开销有严格要求，需要比传统行为树和导航系统更高效的解决方案。

## 蓝图用法

MassAI 的蓝图用法主要通过 **Trait（特征）** 和 **Subsystem（子系统）** 来实现。Trait 用于为实体模板添加特定的 AI 功能（如导航、避障），而 Subsystem 提供全局服务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Navigation Obstacle` (Trait) | 为实体添加导航障碍物标记，使其能被其他代理的避障系统检测到。 | `UMassNavigationObstacleTrait` |
| `Smooth Orientation` (Trait) | 为实体添加平滑的朝向更新功能，使其在移动和站立时朝向更自然。 | `UMassSmoothOrientationTrait` |
| `Avoidance` (Trait) | 为实体添加移动和站立时的避障能力。 | `UMassObstacleAvoidanceTrait` |
| `Steering` (Trait) | 为实体添加转向能力，使其能够朝向移动目标。 | `UMassSteeringTrait` |
| `Get Obstacle Grid` | 从 `UMassNavigationSubsystem` 获取用于避障查询的层级哈希网格。 | `UMassNavigationSubsystem` |

### 使用示例（蓝图描述）

1.  **创建实体模板**：在 `MassEntityConfig` 资产中，添加 `Navigation Obstacle`、`Smooth Orientation`、`Avoidance` 和 `Steering` 这些 Trait。在每个 Trait 的细节面板中，可以调整其参数（如避障半径、转向反应时间）。
2.  **生成实体**：使用 `Spawn Entities From Config` 节点，基于配置好的实体模板在世界中生成大量实体。
3.  **查询障碍物**：在自定义的 `MassProcessor` 或蓝图逻辑中，通过 `Get Game Instance Subsystem` 节点获取 `UMassNavigationSubsystem`，然后调用 `Get Obstacle Grid` 来查询特定区域内的障碍物实体，用于自定义的 AI 决策。

## C++ 用法

### 头文件引入

```cpp
#include "MassNavigation.h"
#include "MassNavigationSubsystem.h"
#include "MassNavigationFragments.h"
#include "Steering/MassSteeringFragments.h"
#include "Avoidance/MassAvoidanceFragments.h"
```

### 基本用法

以下代码展示了如何为一个实体模板添加导航相关的 Fragment 和 Trait。

```cpp
// 来源: 基于 MassNavigationTrait 类的 BuildTemplate 方法推断
#include "MassEntityTemplateBuildContext.h"
#include "MassNavigationFragments.h"
#include "Steering/MassSteeringFragments.h"

void UMyCustomTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 1. 添加移动目标 Fragment，这是导航的核心
    BuildContext.AddFragment<FMassMoveTargetFragment>();

    // 2. 添加转向参数（共享数据，所有使用此模板的实体共享同一份数据）
    BuildContext.AddConstSharedFragment<FMassMovingSteeringParameters>(FMassMovingSteeringParameters());
    BuildContext.AddConstSharedFragment<FMassStandingSteeringParameters>(FMassStandingSteeringParameters());

    // 3. 添加转向状态 Fragment（每个实体独立的状态）
    BuildContext.AddFragment<FMassSteeringFragment>();
    BuildContext.AddFragment<FMassStandingSteeringFragment>();

    // 4. 添加标签，表示该实体需要转向处理
    BuildContext.AddTag<FMassNeedsSteeringTag>();
}
```

### 进阶用法

以下代码展示了如何在自定义的 `MassProcessor` 中使用 `UMassNavigationSubsystem` 来查询附近的障碍物。

```cpp
// 来源: 基于 MassAvoidanceProcessors.h 中的处理器实现推断
#include "MassProcessor.h"
#include "MassNavigationSubsystem.h"
#include "MassNavigationFragments.h"

class UMyCustomAvoidanceProcessor : public UMassProcessor
{
public:
    UMyCustomAvoidanceProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
    TObjectPtr<UMassNavigationSubsystem> NavigationSubsystem;
};

void UMyCustomAvoidanceProcessor::InitializeInternal(UObject& Owner, const TSharedRef<FMassEntityManager>& EntityManager)
{
    Super::InitializeInternal(Owner, EntityManager);
    // 获取导航子系统
    NavigationSubsystem = UWorld::GetSubsystem<UMassNavigationSubsystem>(Owner.GetWorld());
}

void UMyCustomAvoidanceProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    if (!NavigationSubsystem) return;

    // 获取障碍物网格
    const FNavigationObstacleHashGrid2D& ObstacleGrid = NavigationSubsystem->GetObstacleGrid();

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        // 获取当前 Chunk 中实体的位置数据
        const TArrayView<FVector> Locations = Context.GetMutableFragmentView<FVector>();

        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            const FVector& CurrentLocation = Locations[i];

            // 查询当前位置附近半径 200cm 内的障碍物
            TArray<FMassNavigationObstacleItem> NearbyObstacles;
            ObstacleGrid.Query(CurrentLocation, 200.0f, NearbyObstacles);

            // ... 在此处根据 NearbyObstacles 进行自定义的避障或决策逻辑
        }
    });
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个带有基本转向和朝向功能的实体。

**MyMassAIAgent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTraitBase.h"
#include "MyMassAIAgent.generated.h"

UCLASS(meta = (DisplayName = "My AI Agent"))
class UMyMassAIAgentTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()

protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};
```

**MyMassAIAgent.cpp**
```cpp
#include "MyMassAIAgent.h"
#include "MassEntityTemplateBuildContext.h"
#include "MassNavigationFragments.h"
#include "Steering/MassSteeringFragments.h"
#include "SmoothOrientation/MassSmoothOrientationFragments.h"

void UMyMassAIAgentTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 核心导航
    BuildContext.AddFragment<FMassMoveTargetFragment>();

    // 转向
    BuildContext.AddConstSharedFragment<FMassMovingSteeringParameters>(FMassMovingSteeringParameters());
    BuildContext.AddConstSharedFragment<FMassStandingSteeringParameters>(FMassStandingSteeringParameters());
    BuildContext.AddFragment<FMassSteeringFragment>();
    BuildContext.AddFragment<FMassStandingSteeringFragment>();
    BuildContext.AddTag<FMassNeedsSteeringTag>();

    // 平滑朝向
    BuildContext.AddConstSharedFragment<FMassSmoothOrientationParameters>(FMassSmoothOrientationParameters());
    BuildContext.AddFragment<FMassSmoothOrientationWeights>();
    BuildContext.AddTag<FMassNeedsOrientationSmoothingTag>();
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的多个模块依赖 `EditorFramework` 和 `UnrealEd`，但这些是编辑器插件的常见依赖，对于运行时功能无特殊要求。

## 维护状态

### 近期更新

- 457eba2e5782 PR #13332: Added std::is_trivially_copyable to the CFragment concept.
  - *解读：对 Mass 框架的 Fragment 概念进行了底层的 C++ 类型特征检查，属于框架层面的维护性改进。*
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
  - *解读：代码生成相关的优化，旨在减少编译时间和头文件依赖，属于构建系统维护。*
- e488be12753f Add missing headers that cause compile errors in non-unity builds with Mass debug tools disabled.
  - *解读：修复了在特定编译配置下的编译错误，属于 bug 修复。*

### 维护评价

MassAI 插件创建于 2021 年，已有约 4 年历史。从最近的提交记录来看，它仍在被维护，但近期的更新**全部是底层的框架维护、编译修复和代码优化**，没有看到新功能或重大改进的提交。结合其 `.uplugin` 中 `EnabledByDefault: false` 和 `IsExperimentalVersion: true` 的标记，可以判断该插件仍处于**实验性阶段**，尚未达到生产就绪的稳定状态。

**综合评价**：该插件提供了处理大规模 AI 的强大潜力，但作为实验性功能，其 API 和行为可能在未来版本中发生变化。它适合用于技术预研、原型开发或对稳定性要求不高的项目。不建议在需要长期稳定维护的商业项目中作为核心依赖使用。建议密切关注其在新引擎版本中的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [官方文档]()（暂无）
- [测试用例]()（暂未在提供的信息中发现）