# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Unreal Engine 5 中 **MassGameplay** 框架的 AI 扩展插件。它解决的核心问题是：**如何在拥有成千上万个实体（如 NPC、单位、生物）的大型游戏世界中，高效地管理它们的 AI 行为、导航和状态同步。**

传统的 AI 系统（如行为树）为每个 AI 代理分配独立的资源，在大规模场景下会导致严重的性能瓶颈。MassAI 基于 **实体组件系统（ECS）** 架构，将 AI 逻辑（行为、导航决策）与实体数据（位置、状态）分离，通过批量处理（Mass Processing）来实现极高的性能。它不是一个通用的 AI 系统，而是专门为 **大规模、高性能 AI** 场景设计的底层框架。

## 使用场景

- **开放世界游戏**：需要同时模拟数百甚至数千个市民、动物或敌人的行为和移动。
- **即时战略（RTS）游戏**：需要高效控制大量作战单位的寻路、编队和简单战斗逻辑。
- **模拟经营游戏**：需要模拟大量顾客、员工等角色的日常行为和路径规划。
- **任何需要“群体智能”或“海量实体 AI”** 且对性能有严格要求的项目。

## 蓝图用法

MassAI 的蓝图接口主要分布在 `MassNavigation` 和 `MassAIBehavior` 等模块中，用于配置和驱动大规模实体的 AI 行为。`MassNavigationEditor` 模块本身主要提供编辑器工具，公开的蓝图 API 较少。

### 核心节点

由于 MassAI 是底层框架，其核心功能通常通过 **Mass 处理器（Processor）** 和 **片段（Fragment）** 在 C++ 层面实现。蓝图主要用于配置资产和触发高层级逻辑。以下是一些关键的可配置类和概念：

| 节点/概念 | 说明 | 所在类/模块 |
|---|---|---|
| `MassNavigation` 相关片段 | 定义实体的移动能力、速度、转向等属性。 | `MassNavigation` 模块 |
| `MassAIBehavior` 相关片段 | 定义实体的行为状态、目标、感知结果等。 | `MassAIBehavior` 模块 |
| `ZoneGraph` 路径数据 | 用于基于区域图（ZoneGraph）的高性能导航。 | `MassZoneGraphNavigation` 模块 |
| `NavMesh` 路径数据 | 用于基于传统导航网格（NavMesh）的导航。 | `MassNavMeshNavigation` 模块 |

### 使用示例（蓝图描述）

1.  **配置实体**：在你的 Mass Entity 配置资产（如 `MassEntityConfig`）中，添加来自 `MassNavigation` 和 `MassAIBehavior` 模块的片段（Fragment），以赋予实体移动和 AI 行为能力。
2.  **设置导航数据**：根据你的场景，选择使用 `ZoneGraph` 或 `NavMesh` 模块提供的导航数据片段，并将其关联到配置中。
3.  **触发行为**：通过 `MassSignal` 或自定义的处理器，向实体发送信号（如“移动到某点”、“攻击目标”），驱动其 AI 行为。

## C++ 用法

MassAI 的核心用法是编写自定义的 **Mass 处理器（Processor）** 来处理带有特定 AI 片段的实体。

### 头文件引入

```cpp
// 引入导航相关片段和处理器基类
#include "MassNavigationFragments.h"
#include "MassProcessor.h"

// 引入行为相关片段
#include "MassAIBehaviorTypes.h"
```

### 基本用法

创建一个简单的处理器，读取实体的导航意图并应用移动。

```cpp
// MyMovementProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MyMovementProcessor.generated.h"

UCLASS()
class UMyMovementProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyMovementProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MyMovementProcessor.cpp
#include "MyMovementProcessor.h"
#include "MassMovementFragments.h" // 假设的移动片段头文件

UMyMovementProcessor::UMyMovementProcessor()
{
    // 设置处理器执行阶段，例如在移动阶段
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Movement;
}

void UMyMovementProcessor::ConfigureQueries()
{
    // 查询所有拥有“移动意图”和“变换”片段的实体
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FMassMoveTargetFragment>(EMassFragmentAccess::ReadOnly); // 假设的意图片段
    // 可能还需要速度、转向等片段
}

void UMyMovementProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 批量遍历所有匹配的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [this](FMassExecutionContext& Context)
    {
        // 获取片段数组
        const TConstArrayView<FMassMoveTargetFragment> MoveTargets = Context.GetFragmentView<FMassMoveTargetFragment>();
        const TArrayView<FTransformFragment> Transforms = Context.GetMutableFragmentView<FTransformFragment>();

        // 批量处理
        for (int32 i = 0; i < Context.GetNumEntities(); ++i)
        {
            // 根据意图更新位置（简化示例）
            FTransform& Transform = Transforms[i].GetMutableTransform();
            const FVector& TargetLocation = MoveTargets[i].TargetLocation;
            // ... 执行移动逻辑，更新 Transform ...
        }
    });
}
```

### 进阶用法

结合 `MassZoneGraphNavigation` 模块，实现基于区域图的寻路。

```cpp
// 引入区域图导航相关头文件
#include "MassZoneGraphNavigationFragments.h"
#include "ZoneGraphQuery.h"

// 在处理器中查询拥有区域图路径请求的实体
void UMyZoneGraphPathProcessor::ConfigureQueries()
{
    EntityQuery.AddRequirement<FZoneGraphPathRequestFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    // ... 其他需求
}

void UMyZoneGraphPathProcessor::Execute(...)
{
    // 获取区域图子系统
    UZoneGraphSubsystem* ZoneGraphSubsystem = UWorld::GetSubsystem<UZoneGraphSubsystem>(Context.GetWorld());

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& Context)
    {
        const TConstArrayView<FZoneGraphPathRequestFragment> PathRequests = Context.GetFragmentView<FZoneGraphPathRequestFragment>();
        // ... 处理每个寻路请求，使用 ZoneGraphSubsystem 进行查询和路径计算 ...
    });
}
```

## Demo 示例

一个最小的、可编译的处理器示例，用于打印拥有特定 AI 标签的实体数量。

```cpp
// MassAIDemoProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassAIDemoProcessor.generated.h"

// 定义一个简单的标签片段，用于标识需要被此处理器处理的实体
USTRUCT()
struct FMassAIDemoTag : public FMassTag
{
    GENERATED_BODY()
};

UCLASS()
class UMassAIDemoProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMassAIDemoProcessor();

protected:
    virtual void ConfigureQueries() override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// MassAIDemoProcessor.cpp
#include "MassAIDemoProcessor.h"
#include "MassExecutionContext.h"

UMassAIDemoProcessor::UMassAIDemoProcessor()
{
    // 设置为调试或开发阶段执行
    ExecutionOrder.ExecuteInGroup = UE::Mass::ProcessorGroupNames::Debug;
    ProcessingPhase = EMassProcessingPhase::PostPhysics; // 示例阶段
}

void UMassAIDemoProcessor::ConfigureQueries()
{
    // 查询所有带有 FMassAIDemoTag 标签的实体
    EntityQuery.AddTagRequirement<FMassAIDemoTag>(EMassFragmentPresence::All);
}

void UMassAIDemoProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    int32 TotalEntities = 0;
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&TotalEntities](FMassExecutionContext& Context)
    {
        TotalEntities += Context.GetNumEntities();
    });

    UE_LOG(LogTemp, Log, TEXT("MassAI Demo: Found %d entities with DemoTag."), TotalEntities);
}
```

## 模块依赖

MassAI 插件内部模块相互依赖，对外部项目的依赖主要是 MassGameplay 核心框架。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心实体管理框架，提供 ECS 基础。 |
| `MassGameplay` | MassGameplay 的游戏逻辑层，提供通用的游戏相关片段和处理器。 |
| `MassSpawner` | 用于在世界中生成和管理 Mass 实体。 |
| `ZoneGraph` | 提供区域图（ZoneGraph）数据结构和查询接口，用于高性能导航。 |
| `NavigationSystem` | 传统导航系统，`MassNavMeshNavigation` 模块依赖于此。 |

## 维护状态

### 近期更新

```
- 9803c443cfab Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 2057280165b3 Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 1/n
- d348655b8cad [Mass] headers cleanup, mainly pushing IWYU
```

以上提交均为代码维护和清理工作（添加宏、调整头文件包含、IWYU 合规），**没有新的功能特性或重大 bug 修复**。

### 维护评价

- **创建时间**：2021 年 9 月，作为 UE5 早期实验性功能推出。
- **最近更新**：最近的更新集中在代码质量维护（IWYU、宏使用），表明代码库仍在被维护以保持与引擎新版本的兼容性，但**缺乏实质性的功能迭代**。
- **活跃度**：作为 Epic 官方维护的实验性插件，其生命周期与 MassGameplay 框架绑定。目前处于 **“维护但不活跃开发”** 状态。
- **已知限制**：文档和示例稀缺，API 可能随版本变动。作为实验性功能，其稳定性和最终形态存在不确定性。
- **推荐使用**：**仅推荐给对 MassGameplay 有深入研究，并且项目确实面临大规模 AI 性能瓶颈的高级开发者**。对于大多数项目，传统的 AI 系统（行为树、EQS）配合优化策略是更稳妥的选择。使用前务必评估其“实验性”状态带来的风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI/Source/MassAITestSuite)