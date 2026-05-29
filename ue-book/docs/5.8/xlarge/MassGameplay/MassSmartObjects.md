# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体游戏逻辑 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（智能对象资产、ZoneGraph注解组件） |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 插件并非一个独立的游戏玩法实现，而是基于底层 MassEntity ECS 框架，为大规模智能体（AI、NPC、可交互物体等）构建游戏逻辑提供**标准化、可复用、高性能**的“积木”。它解决的核心问题是：当游戏世界中有成百上千甚至数万个 AI 代理时，如何高效地管理它们的行为（如移动、感知、决策、交互），并确保它们能与游戏世界（如智能对象、ZoneGraph 路径）进行标准化、高性能的互动。

插件将原本属于单个 Actor 的复杂游戏逻辑（如“走到桌子旁 → 坐下 → 吃东西”）抽象为可附加到 Mass Entity 上的 Fragment（数据）和 Processor（系统）。其核心亮点是 **MassSmartObjects** 子模块，它桥接了 MassEntity 系统与 UE 的 SmartObjects 框架，使得海量实体能够以批处理的方式搜索、认领、使用环境中的交互点（如长椅、工作台、车辆），极大地提升了交互逻辑的管理效率和运行时性能。

## 使用场景

- **大规模人群/市民模拟**：在开放世界或城市模拟游戏中，成千上万的市民需要导航、寻找并使用公共设施（长椅、商店、公交站）。MassGameplay 提供了管理这些行为和交互的高效方案。
- **RTS/大战略游戏**：管理大量作战单位的编队移动、攻击、占领建筑等行为。
- **带有大量环境交互点的游戏**：任何需要让大量 AI 角色与游戏世界中预设的“交互点”进行标准化互动的游戏。例如，让一队士兵自动找到并使用地图上的补给箱。
- **需要高度可复用 AI 行为逻辑的项目**：通过将行为定义为 Mass Behavior Definition，可以在不同的实体模板间轻松复用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SmartObject User` (Trait) | 将实体标记为智能对象用户，并允许为其指定 `UserTags`。 | `UMassSmartObjectUserTrait` |
| `Smart Object Zone Annotations` (Component) | Actor 组件，用于在 ZoneGraph 上为地图中的智能对象注册和管理入口点注解。 | `USmartObjectZoneAnnotations` |

### 使用示例（蓝图描述）

1.  **使实体成为智能对象用户**：
    *   在创建 Mass Entity Template 时，添加 `UMassSmartObjectUserTrait`。
    *   在该 Trait 的属性面板中，设置 `UserTags`（例如 `NPC.Civilian`），这些标签将用于后续的智能对象搜索过滤。

2.  **管理智能对象入口点（编辑器工作流）**：
    *   在关卡中放置一个 Actor（例如一个 `AZoneGraphManager` 或自定义 Actor）。
    *   为该 Actor 添加 `USmartObjectZoneAnnotations` 组件。
    *   在组件属性中配置 `AffectedLaneTags`，指定哪些类型的 ZoneGraph 车道会被标记为拥有智能对象。
    *   插件会自动在编辑器中为地图上的智能对象（如长椅 Actor）在最近的 ZoneGraph 车道上创建入口点注解，并在运行时维护这些数据。

## C++ 用法

### 头文件引入

```cpp
#include "MassSmartObjects/MassSmartObjectHandler.h"
#include "MassSmartObjects/MassSmartObjectFragments.h"
#include "MassSmartObjects/MassSmartObjectRequest.h"
#include "MassSmartObjects/MassSmartObjectTypes.h"
```

### 基本用法：查找并使用智能对象

以下示例展示了一个自定义的 Mass Processor，它让符合条件的实体查找附近的智能对象并开始使用。

*(来源: 基于 `FMassSmartObjectHandler` 和 `UMassSmartObjectCandidatesFinderProcessor` 等类的典型用法推断)*

```cpp
// MySmartObjectUserProcessor.h
#pragma once

#include "MassProcessor.h"
#include "MassSmartObjectFragments.h"
#include "MassSmartObjectRequest.h"
#include "MassSmartObjectTypes.h"
#include "SmartObjectTypes.h"

class UMassSignalSubsystem;
class USmartObjectSubsystem;

UCLASS()
class UMySmartObjectUserProcessor : public UMassProcessor
{
    GENERATED_BODY()

public:
    UMySmartObjectUserProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 查询包含用户 Fragment 且当前未在交互中的实体
    FMassEntityQuery EntityQuery;

    TWeakObjectPtr<UMassSignalSubsystem> SignalSubsystem;
    TWeakObjectPtr<USmartObjectSubsystem> SmartObjectSubsystem;
};
```

```cpp
// MySmartObjectUserProcessor.cpp
#include "MySmartObjectUserProcessor.h"
#include "MassSmartObjectHandler.h"
#include "MassExecutionContext.h"
#include "SignalSubsystem.h"
#include "SmartObjectSubsystem.h"

UMySmartObjectUserProcessor::UMySmartObjectUserProcessor()
{
    // 设置处理器在哪个阶段运行
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EProcessingPhase::PrePhysics; // 示例阶段
}

void UMySmartObjectUserProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassSmartObjectUserFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    // 仅查找交互状态为 Unset 的实体
    EntityQuery.AddConstSharedRequirement<FMassSmartObjectUserFragment>([](const FMassSmartObjectUserFragment& UserFragment)
    {
        return UserFragment.InteractionStatus == EMassSmartObjectInteractionStatus::Unset;
    });
}

void UMySmartObjectUserProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    if (!SignalSubsystem.IsValid() || !SmartObjectSubsystem.IsValid())
    {
        SignalSubsystem = Context.GetMutableSubsystem<UMassSignalSubsystem>();
        SmartObjectSubsystem = Context.GetMutableSubsystem<USmartObjectSubsystem>();
        if (!SignalSubsystem.IsValid() || !SmartObjectSubsystem.IsValid())
        {
            return;
        }
    }

    // 创建一个处理器作用域内的智能对象操作处理器
    FMassSmartObjectHandler SOHandler(Context, *SmartObjectSubsystem, *SignalSubsystem);

    EntityQuery.ForEachEntityChunk(Context, [this, &SOHandler](FMassExecutionContext& ChunkContext)
    {
        const TConstArrayView<FMassSmartObjectUserFragment> UserFragments = ChunkContext.GetFragmentView<FMassSmartObjectUserFragment>();
        const TConstArrayView<FTransformFragment> TransformFragments = ChunkContext.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < ChunkContext.GetNumEntities(); ++i)
        {
            const FMassEntityHandle Entity = ChunkContext.GetEntity(i);
            const FMassSmartObjectUserFragment& User = UserFragments[i];
            const FVector& EntityLocation = TransformFragments[i].GetTransform().GetLocation();

            // 步骤 1: 异步查找候选智能对象
            // 此处使用基于位置的查找，也可以使用基于 ZoneGraph 车道的查找
            UE::Mass::SmartObject::FFindCandidatesParameters Params;
            Params.UserTags = User.UserTags;
            Params.Location = EntityLocation;
            FMassSmartObjectRequestID RequestID = SOHandler.FindCandidatesAsync(Entity, MoveTemp(Params));

            // 步骤 2: 检查请求是否完成 (通常在下一帧或通过信号检查)
            if (const FMassSmartObjectCandidateSlots* Candidates = SOHandler.GetRequestCandidates(RequestID))
            {
                if (Candidates->NumSlots > 0)
                {
                    // 步骤 3: 认领一个候选对象
                    FSmartObjectClaimHandle ClaimHandle = SOHandler.ClaimCandidate(Entity, ChunkContext.GetMutableFragmentView<FMassSmartObjectUserFragment>()[i], *Candidates);
                    if (ClaimHandle.IsValid())
                    {
                        // 步骤 4: 开始使用智能对象 (会激活关联的 Mass Behavior Definition)
                        SOHandler.StartUsingSmartObject(Entity, ChunkContext.GetMutableFragmentView<FMassSmartObjectUserFragment>()[i], ClaimHandle);
                    }
                }
                // 步骤 5: 清理请求
                SOHandler.RemoveRequest(RequestID);
            }
        }
    });
}
```

### 进阶用法：自定义智能对象行为定义

通过继承 `USmartObjectMassBehaviorDefinition`，可以定义实体与智能对象交互时的具体行为。

```cpp
// MassSmartObjectEatBehaviorDefinition.h
#pragma once

#include "MassSmartObjectBehaviorDefinition.h"
#include "MassCommandBuffer.h"
#include "MassEntityTypes.h"

// 自定义的行为定义子类
UCLASS(EditInlineNew, meta=(DisplayName="Eat Behavior"))
class UMassSmartObjectEatBehaviorDefinition : public USmartObjectMassBehaviorDefinition
{
    GENERATED_BODY()

public:
    virtual void Activate(FMassCommandBuffer& CommandBuffer, const FMassBehaviorEntityContext& EntityContext) const override
    {
        // 当实体开始使用智能对象（如餐桌）时，在实体上添加“正在进食”片段
        CommandBuffer.PushCommand<FMassDeferredSetCommand>([Entity = EntityContext.Entity](FMassEntityManager& System)
        {
            if (FMassSmartObjectTimedBehaviorFragment* TimedBehavior = System.GetFragmentDataPtr<FMassSmartObjectTimedBehaviorFragment>(Entity))
            {
                // 使用基类定义的 UseTime
                TimedBehavior->UseTime = UseTime;
            }
        });
        // 也可以在这里播放动画、播放声音的信号等
        // CommandBuffer.PushCommand<FMassAddFragmentInstanceCommand>(...);
    }

    virtual void Deactivate(FMassCommandBuffer& CommandBuffer, const FMassBehaviorEntityContext& EntityContext) const override
    {
        // 当行为结束时（用时结束或被中断），清理相关片段
        CommandBuffer.PushCommand<FMassRemoveFragmentCommand<FMassSmartObjectTimedBehaviorFragment>>(EntityContext.Entity);
    }

    /** 预计进食时长 (秒) */
    UPROPERTY(EditDefaultsOnly, Category = "Eat Behavior")
    float EatDuration = 30.0f;
};
```

## Demo 示例

一个最小化的示例，展示如何创建一个能够查找并使用智能对象的 Mass Entity。

**EntityTemplate.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "MassEntityTemplate.h"
#include "MassEntityTypes.h"

class UMassSmartObjectUserTrait;

// 定义一个简单的实体模板构建器
struct FMyEntityTemplateBuilder
{
    static TSharedRef<FMassEntityTemplate> BuildTemplate(const UWorld& World)
    {
        FMassEntityTemplateBuildContext BuildContext;
        
        // 1. 添加变换 (位置， 旋转)
        BuildContext.AddFragment<FTransformFragment>();
        
        // 2. 添加智能对象用户能力 (关键步骤)
        UMassSmartObjectUserTrait* SOUserTrait = NewObject<UMassSmartObjectUserTrait>();
        SOUserTrait->UserTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT("AI.Civilian")));
        BuildContext.AddTrait(*SOUserTrait, World);
        
        // 3. (可选) 添加移动、渲染等其他 Trait/Fragment
        // ...
        
        // 构建最终模板
        return MakeShared<FMassEntityTemplate>(MoveTemp(BuildContext));
    }
};
```

**Spawner.cpp (生成实体)**
```cpp
#include "EntityTemplate.h"
#include "MassSpawnerSubsystem.h"

void SpawnCivilianEntities(UWorld* World, const FVector& SpawnCenter, int32 Count)
{
    if (UMassSpawnerSubsystem* SpawnerSubsystem = World->GetSubsystem<UMassSpawnerSubsystem>())
    {
        // 获取我们定义的模板
        TSharedRef<FMassEntityTemplate> Template = FMyEntityTemplateBuilder::BuildTemplate(*World);
        
        // 在指定区域生成 Count 个实体
        FTransform SpawnTransform;
        SpawnTransform.SetLocation(SpawnCenter);
        SpawnerSubsystem->SpawnEntities(Template->GetTemplateID(), Count, SpawnTransform);
    }
}
```

## 模块依赖

从 Build.cs 分析，使用 `MassSmartObjects` 模块（或插件的核心功能）通常需要以下**非通用**依赖：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 提供核心的 ECS 框架 (EntityManager, Fragment, Processor)。 |
| `GameplayTags` | 用于智能对象用户标签和活动需求的过滤。 |
| `ZoneGraph` | 用于 `SmartObjectZoneAnnotations` 组件和基于车道的智能对象查找。 |
| `SmartObjects` | 提供底层的智能对象定义、子系统和交互句柄。 |
| `MassSpawner` | (可选) 用于从模板生成大量 Mass 实体。 |
| `MassSignals` | 用于实体间通信（如状态改变信号）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了之前对 MassAgentComponent 的改动。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 在关闭实例化静态网格体(ISM)前等待Actor准备就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了在 Mass 人群中对非傀儡(Puppet) Actor 的处理。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复了 `TMassLODCalculator` 按查看器LOD路径的一系列既有Bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | [Mass representation] 将两处手动计算的 `bDoKeepActorExtraFrame` 改为使用新的 UE::M 接口。 |

### 维护评价

MassGameplay 插件处于**活跃维护**状态，尽管仍被标记为实验性。从 Git 历史看，在 2026 年 5 月仍有持续的 Bug 修复和稳定性改进，主要集中在 `MassRepresentation`、`MassSpawner` 等子模块上。创建于 2021 年，已有约 5 年历史，但核心架构（MassEntity）非常新且是 Epic 重点发展对象。

**注意事项**：
1.  **实验性**：插件 `.uplugin` 标记为 `IsExperimentalVersion: true`，API 可能发生不兼容的更改（例如头文件中可见的 `UE_DEPRECATED` 标记）。
2.  **默认禁用**：需要在项目设置或 `.uproject` 中手动启用。
3.  **学习曲线**：使用此插件需要先理解 MassEntity ECS 概念（Entity, Fragment, Processor, Archetype），门槛较高。

**推荐**：对于计划或已经大规模使用 MassEntity 的项目，并需要高效管理海量 AI 与环境交互，强烈建议研究和使用此插件。对于小规模项目，传统的 Actor-Based AI 可能更简单直接。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- [官方文档]()（未提供）
- [测试用例]()（未提供，但插件内含 `MassGameplayTestSuite` 模块）