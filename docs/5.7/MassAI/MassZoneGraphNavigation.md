# MassAI

> AI-specific functionality extending MassGameplay（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `MassAIBehavior` (Runtime), `MassAIBehaviorEditor` (Runtime), `MassAIDebug` (Runtime), `MassAIReplication` (Runtime), `MassAITestSuite` (Runtime), `MassNavigation` (Runtime), `MassNavigationEditor` (Runtime), `MassNavMeshNavigation` (Runtime), `MassZoneGraphNavigation` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI) | |

## 用途

MassAI 是 Epic Games 为 Unreal Engine 的 **MassGameplay** 框架提供的 AI 扩展插件。它并非一个独立的 AI 系统，而是专门为大规模实体（Mass Entity）设计的 AI 功能模块。

**核心解决的问题**：传统 AI 系统（如行为树、EQS）在管理成千上万个 AI 代理时，会遇到严重的性能瓶颈。MassAI 利用 MassGameplay 的 ECS（实体组件系统）架构，将 AI 的决策、导航、行为等逻辑数据化、批量化处理，从而实现高性能的大规模 AI 模拟。

**为什么存在**：MassGameplay 本身专注于实体管理和数据驱动的处理流程，但缺乏具体的 AI 行为和导航逻辑。MassAI 填补了这一空白，提供了：
1.  **基于 ZoneGraph 的导航**：让大量实体能够高效地在预定义的 ZoneGraph 路径网络上移动。
2.  **行为管理**：为实体提供状态机或行为树的集成点。
3.  **调试与可视化**：提供专门的调试工具来观察大规模 AI 的状态。
4.  **网络复制**：处理大规模 AI 实体的状态同步。

## 使用场景

-   **大规模 RTS 或战场模拟**：你需要控制成百上千个士兵、单位在复杂的战场地图上移动、寻路、执行简单指令。
-   **开放世界 NPC 群体**：城市中熙熙攘攘的行人、集市上的商贩，他们需要沿着街道（ZoneGraph）自然行走，并在特定地点停留或互动。
-   **塔防或生存游戏中的大量敌人**：敌人需要沿着固定路径（如 ZoneGraph 定义的路线）涌向玩家基地。
-   **任何需要高性能、数据驱动 AI 的场景**：当传统 AI 方案成为性能瓶颈时，考虑使用 MassAI。

## 蓝图用法

MassAI 的蓝图接口主要通过 **MassEntityTrait** 和 **工具函数** 暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ZoneGraph Navigation` (Trait) | 为实体模板添加基于 ZoneGraph 的导航能力。 | `UMassZoneGraphNavigationTrait` |
| `Activate Action Move` | 激活实体的移动动作，使其沿 ZoneGraph 路径移动到指定距离。 | `UE::MassNavigation` (命名空间) |
| `Activate Action Stand` | 激活实体的站立动作，使其在当前位置停止。 | `UE::MassNavigation` (命名空间) |
| `Activate Action Animate` | 激活实体的动画动作。 | `UE::MassNavigation` (命名空间) |

### 使用示例（蓝图描述）

1.  **配置实体模板**：
    *   在你的 `MassEntityConfig` 资产中，添加 `ZoneGraph Navigation` 特性。
    *   在该特性的细节面板中，配置 `Lane Filter`（指定实体可以使用的 ZoneGraph 车道类型）和 `Query Radius`（实体生成时寻找最近车道的搜索半径）。

2.  **驱动实体移动**：
    *   通过 MassGameplay 的信号或处理器，获取到需要移动的实体句柄 (`FMassEntityHandle`)。
    *   构造一个 `FZoneGraphShortPathRequest` 结构体，指定目标距离、是否反向移动、路径结束意图等。
    *   调用 `Activate Action Move` 工具函数，传入世界上下文、实体句柄、ZoneGraph 子系统、路径请求以及实体的移动目标片段 (`FMassMoveTargetFragment`)、短路径片段 (`FMassZoneGraphShortPathFragment`) 和缓存车道片段 (`FMassZoneGraphCachedLaneFragment`)。
    *   函数执行后，实体的移动目标将被更新，MassNavigation 处理器会在后续帧驱动实体沿路径移动。

## C++ 用法

### 头文件引入

```cpp
// 核心导航特性
#include "MassZoneGraphNavigationTrait.h"
// 导航工具函数
#include "MassZoneGraphNavigationUtils.h"
// 导航相关的片段（数据）
#include "MassZoneGraphNavigationFragments.h"
// 导航处理器
#include "MassZoneGraphNavigationProcessors.h"
```

### 基本用法

以下示例展示了如何在 C++ 中为实体添加 ZoneGraph 导航并激活移动。
*（注：此示例基于头文件推断，实际使用需结合 MassGameplay 的实体创建流程）*

```cpp
// 假设你已经通过 MassEntityManager 创建或获取了一个实体 EntityHandle
// 并且该实体已经拥有 FMassMoveTargetFragment, FMassZoneGraphLaneLocationFragment 等必要片段

// 1. 获取必要的子系统
UZoneGraphSubsystem* ZoneGraphSubsystem = UWorld::GetSubsystem<UZoneGraphSubsystem>(GetWorld());
check(ZoneGraphSubsystem);

// 2. 准备路径请求
FZoneGraphShortPathRequest PathRequest;
PathRequest.StartPosition = EntityLocation; // 实体当前位置
PathRequest.TargetDistance = 1000.0f; // 向前移动1000单位
PathRequest.EndOfPathIntent = EMassMovementAction::Stand; // 到达后站立
PathRequest.bMoveReverse = false; // 正向移动

// 3. 获取实体的导航相关片段（假设已存在）
FMassMoveTargetFragment* MoveTarget = EntityManager.GetFragmentDataPtr<FMassMoveTargetFragment>(EntityHandle);
FMassZoneGraphLaneLocationFragment* LaneLocation = EntityManager.GetFragmentDataPtr<FMassZoneGraphLaneLocationFragment>(EntityHandle);
FMassZoneGraphShortPathFragment* ShortPath = EntityManager.GetFragmentDataPtr<FMassZoneGraphShortPathFragment>(EntityHandle);
FMassZoneGraphCachedLaneFragment* CachedLane = EntityManager.GetFragmentDataPtr<FMassZoneGraphCachedLaneFragment>(EntityHandle);

// 4. 调用工具函数激活移动
bool bSuccess = UE::MassNavigation::ActivateActionMove(
    *GetWorld(),
    this, // 请求者对象
    EntityHandle,
    *ZoneGraphSubsystem,
    *LaneLocation,
    PathRequest,
    AgentRadius, // 代理半径
    DesiredSpeed, // 期望速度
    *MoveTarget,
    *ShortPath,
    *CachedLane
);

if (bSuccess)
{
    // 移动已成功激活，实体将在后续帧由 MassZoneGraphPathFollowProcessor 驱动移动
}
```

### 进阶用法

MassAI 的强大之处在于其处理器 (`UMassProcessor`) 和观察者处理器 (`UMassObserverProcessor`)。你可以通过继承这些处理器来注入自定义逻辑。

```cpp
// 示例：创建一个自定义处理器，在实体进入特定ZoneGraph区域时触发事件
UCLASS()
class UMyZoneGraphAreaTriggerProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMyZoneGraphAreaTriggerProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    FMassEntityQuery EntityQuery;
};

// 在 ConfigureQueries 中，查询拥有 FMassZoneGraphLaneLocationFragment 且位于特定区域的实体
// 在 Execute 中，遍历查询结果，检查 LaneLocation 的距离或车道标签，然后触发你的游戏逻辑
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建一个带有 ZoneGraph 导航能力的实体并命令其移动。

**MyMassAICharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MassEntityTypes.h"
#include "MyMassAICharacter.generated.h"

class UMassEntityConfigAsset;
class UZoneGraphSubsystem;

UCLASS()
class AMyMassAICharacter : public AActor
{
    GENERATED_BODY()

public:
    AMyMassAICharacter();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "MassAI")
    void CommandMoveToDistance(float Distance);

protected:
    UPROPERTY(EditAnywhere, Category = "MassAI")
    TObjectPtr<UMassEntityConfigAsset> EntityConfig;

    UPROPERTY(Transient)
    FMassEntityHandle EntityHandle;

    UPROPERTY(Transient)
    TObjectPtr<UZoneGraphSubsystem> ZoneGraphSubsystem;
};
```

**MyMassAICharacter.cpp**
```cpp
#include "MyMassAICharacter.h"
#include "MassEntitySubsystem.h"
#include "MassEntityConfigAsset.h"
#include "MassZoneGraphNavigationUtils.h"
#include "MassZoneGraphNavigationFragments.h"
#include "ZoneGraphSubsystem.h"

AMyMassAICharacter::AMyMassAICharacter()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMassAICharacter::BeginPlay()
{
    Super::BeginPlay();

    UMassEntitySubsystem* EntitySubsystem = UWorld::GetSubsystem<UMassEntitySubsystem>(GetWorld());
    ZoneGraphSubsystem = UWorld::GetSubsystem<UZoneGraphSubsystem>(GetWorld());

    if (EntitySubsystem && EntityConfig && ZoneGraphSubsystem)
    {
        // 使用配置资产创建实体
        FMassEntityTemplateBuildContext BuildContext;
        EntityConfig->GetOrCreateEntityTemplate(*GetWorld(), BuildContext);
        EntityHandle = EntitySubsystem->GetEntityManager().CreateEntity(BuildContext.GetTemplateID());

        // 注意：在实际项目中，实体创建和片段初始化通常由 MassGameplay 的 SpawnData 和 Trait 系统处理。
        // 此处为简化演示，假设实体已通过 Trait 获得了所有必要片段。
    }
}

void AMyMassAICharacter::CommandMoveToDistance(float Distance)
{
    if (!EntityHandle.IsValid() || !ZoneGraphSubsystem)
    {
        return;
    }

    // 获取实体管理器和片段（简化示例，实际应通过查询获取）
    FMassEntityManager& EntityManager = /* ... */;
    FMassMoveTargetFragment* MoveTarget = EntityManager.GetFragmentDataPtr<FMassMoveTargetFragment>(EntityHandle);
    FMassZoneGraphLaneLocationFragment* LaneLocation = EntityManager.GetFragmentDataPtr<FMassZoneGraphLaneLocationFragment>(EntityHandle);
    FMassZoneGraphShortPathFragment* ShortPath = EntityManager.GetFragmentDataPtr<FMassZoneGraphShortPathFragment>(EntityHandle);
    FMassZoneGraphCachedLaneFragment* CachedLane = EntityManager.GetFragmentDataPtr<FMassZoneGraphCachedLaneFragment>(EntityHandle);

    if (MoveTarget && LaneLocation && ShortPath && CachedLane)
    {
        FZoneGraphShortPathRequest PathRequest;
        PathRequest.TargetDistance = Distance;
        PathRequest.EndOfPathIntent = EMassMovementAction::Stand;

        UE::MassNavigation::ActivateActionMove(
            *GetWorld(),
            this,
            EntityHandle,
            *ZoneGraphSubsystem,
            *LaneLocation,
            PathRequest,
            50.0f, // AgentRadius
            300.0f, // DesiredSpeed
            *MoveTarget,
            *ShortPath,
            *CachedLane
        );
    }
}
```

## 模块依赖

`MassZoneGraphNavigation` 模块的 Build.cs 显示其依赖 `EditorFramework` 和 `UnrealEd`。然而，这些是编辑器模块，对于运行时功能并非必需。该模块的核心运行时依赖是 MassGameplay 和 ZoneGraph 框架。

| 模块 | 用途 |
|---|---|
| `MassEntity` | MassGameplay 的核心实体管理框架。 |
| `MassNavigation` | MassGameplay 的通用移动和导航框架，MassZoneGraphNavigation 是其具体实现之一。 |
| `ZoneGraph` | 提供路径网络（ZoneGraph）的数据结构和查询功能。 |

## 维护状态

### 近期更新

```
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- b1980471196e [Mass] Minor MassEntityManager cleanup, including removing some header inclusion
- 52abf4910fa1 [Mass] Mass Observers can now differentiate between Add and Created operations as well as between Remove and Destroy operations. * Observer processors can now be declared to observe multiple operations, and the same processor instance will be used for all the declared operations. * With the extension of EMassObservedOperation the existing UE::Mass::ObserverManager::EObservedOperationNotification became redundant and got removed. * The observer processor can now find out which operation type is being handled. This was achieved by changing the type of payload passed to the execution context when observers are executed. * new payload contains information about the current type being handled, as well as what type of operation is being handled, and a way to peek at the other types being handled in the same operation. * a minor consequence of improvements to UE::Mass::ObserverManager::Private::AddRegisteredObserverProcessorInstances we now consider an element "observed" only if there are actually any observer instances created for that operation (i.e., we don't if all the candidate processor classes filtered out, due to, for example, world flags).
```

*   `ec9009980d52`: 代码生成优化，添加了 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏。
*   `b1980471196e`: MassEntityManager 的清理工作，移除了一些头文件包含。
*   `52abf4910fa1`: **重要功能更新**。增强了 Mass 观察者处理器的能力，现在可以区分“添加/创建”和“移除/销毁”操作，并且一个处理器实例可以观察多种操作。这提升了 Mass 框架的灵活性和表达能力。

### 维护评价

**活跃维护**。MassAI 作为 MassGameplay 框架的关键组成部分，与引擎核心的 Mass 系统同步更新。从近期提交记录看，Epic 团队仍在积极改进其底层架构（如观察者系统），并进行代码优化。该插件标记为 `IsExperimentalVersion=true`，表明其 API 和功能可能在未来版本中发生变化，但鉴于其与引擎核心的紧密集成和持续更新，可以认为是稳定且推荐用于大规模 AI 原型开发的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AI/MassAI)
- [官方文档]()（暂无）
- [测试用例]()（暂无）