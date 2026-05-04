# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（代码模块） |
| 模块 | `MassActors` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSignals` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是 Unreal Engine MassEntity 框架在游戏玩法层面的完整实现。它并非一个独立的物理或动画系统，而是一个基于 ECS（实体组件系统）架构的**大规模实体模拟解决方案**。

**核心问题**：传统的 Actor 模型在处理成千上万个具有相似行为逻辑的实体（如 RTS 游戏中的单位、开放世界中的 NPC 群体、塔防游戏中的敌人波次）时，会因对象管理、蓝图虚拟机调用、组件遍历等开销导致严重的性能瓶颈。

**解决方案**：MassGameplay 将这些实体抽象为“Mass Entity”，其数据（如位置、速度、生命值）存储在连续的内存块（Fragment）中，行为逻辑由无状态的“Processor”批量处理。这种数据导向的设计极大地提升了 CPU 缓存命中率和并行处理能力，使得模拟数万甚至数十万个实体成为可能。

该插件提供了将 MassEntity 与 UE 传统游戏系统（如 Actor、动画、AI、网络复制）桥接的完整功能集，是构建高性能大规模模拟游戏的基础。

## 使用场景

- **即时战略 (RTS) / 大型多人在线 (MMO) 游戏**：你需要同时控制和渲染成千上万的士兵、单位或玩家角色。
- **开放世界游戏**：你需要在广阔的地图上模拟大量动态的 NPC、野生动物或交通载具，且要求它们具备基础的 AI 行为（如巡逻、避障、交互）。
- **塔防 / 生存类游戏**：你需要生成并管理海量的敌人波次或环境实体（如树木、石头），并要求它们具备统一的移动和寻路逻辑。
- **任何需要“群体模拟”的场景**：例如鸟群、鱼群、人群等，需要高效处理大量遵循简单规则的个体。

## 蓝图用法

MassGameplay 主要通过配置和数据驱动的方式在蓝图中使用，而非直接调用大量函数。核心在于定义实体模板（Entity Template）和配置相关子系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Trait` | 在实体模板构建器中添加一个特性（Trait），如 `SmartObject User`。 | `UMassEntityConfigAsset` (编辑器中配置) |
| `Set User Tags` | 为 `SmartObject User` 特性设置描述用户身份的 GameplayTag。 | `UMassSmartObjectUserTrait` (编辑器属性) |
| `Add Component` | 将 `SmartObjectZoneAnnotations` 组件添加到场景中的 Actor（通常是 ZoneGraphData Actor）。 | `AActor` (蓝图编辑器) |

### 使用示例（蓝图描述）

1.  **创建实体模板**：
    - 在内容浏览器中右键 -> `Mass` -> `Entity Config` 创建一个新的实体配置资产。
    - 打开该资产，在 `Traits` 列表中，点击 `+` 添加 `SmartObject User` 特性。
    - 在 `SmartObject User` 特性的属性中，设置 `User Tags`，例如添加一个 `AI.Type.Soldier` 的标签，用于后续匹配智能对象。

2.  **配置场景**：
    - 在场景中，确保有 `ZoneGraphData` Actor 并已生成区域图。
    - 将 `SmartObjectZoneAnnotations` 组件添加到该 `ZoneGraphData` Actor 上。该组件会自动扫描场景中的智能对象，并将它们与区域图的车道关联起来，以实现高效的基于车道的智能对象查询。

3.  **生成实体**：
    - 使用 `Mass Spawner` 或其他生成机制，引用你创建的实体配置资产来生成 Mass Entity。这些实体将自动具备与智能对象交互的能力。

## C++ 用法

### 头文件引入

```cpp
#include "MassSmartObjects/Public/MassSmartObjectHandler.h"
#include "MassSmartObjects/Public/MassSmartObjectFragments.h"
#include "MassSmartObjects/Public/MassSmartObjectBehaviorDefinition.h"
```

### 基本用法

以下代码展示了如何在自定义的 Mass Processor 中，为实体请求并认领一个智能对象交互。

```cpp
// 来源: Engine/Plugins/Runtime/MassGameplay/Source/MassSmartObjects/Public/MassSmartObjectHandler.h
// 假设我们有一个处理器 UMySmartObjectUserProcessor

void UMySmartObjectUserProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 1. 获取必要的子系统
    USmartObjectSubsystem* SmartObjectSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(EntityManager.GetWorld());
    UMassSignalSubsystem* SignalSubsystem = UWorld::GetSubsystem<UMassSignalSubsystem>(EntityManager.GetWorld());
    if (!SmartObjectSubsystem || !SignalSubsystem) return;

    // 2. 创建处理器作用域内的 Handler
    FMassSmartObjectHandler Handler(Context, *SmartObjectSubsystem, *SignalSubsystem);

    // 3. 遍历需要寻找智能对象的实体
    EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& ExecContext)
    {
        const int32 NumEntities = ExecContext.GetNumEntities();
        const TConstArrayView<FMassSmartObjectUserFragment> UserFragments = ExecContext.GetFragmentView<FMassSmartObjectUserFragment>();
        const TConstArrayView<FTransformFragment> TransformFragments = ExecContext.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FMassEntityHandle Entity = ExecContext.GetEntity(i);
            const FMassSmartObjectUserFragment& UserFragment = UserFragments[i];
            const FVector& Location = TransformFragments[i].GetTransform().GetLocation();

            // 4. 如果实体没有正在进行的交互，则发起异步查找请求
            if (UserFragment.InteractionStatus == EMassSmartObjectInteractionStatus::Unset)
            {
                UE::Mass::SmartObject::FFindCandidatesParameters Params;
                Params.UserTags = UserFragment.UserTags;
                Params.QueryOrigin = Location;
                // ... 设置其他参数，如活动需求等

                FMassSmartObjectRequestID RequestID = Handler.FindCandidatesAsync(Entity, MoveTemp(Params));
                // 将 RequestID 存储在实体的某个 Fragment 中以便后续轮询
            }
            // 5. 如果已有请求ID，则轮询结果
            else if (/* Entity has a pending RequestID */)
            {
                const FMassSmartObjectCandidateSlots* Candidates = Handler.GetRequestCandidates(PendingRequestID);
                if (Candidates && Candidates->NumSlots > 0)
                {
                    // 6. 尝试认领第一个候选槽位
                    if (Handler.ClaimCandidate(Entity, UserFragment, *Candidates, 0 /* ClaimPriority */))
                    {
                        // 认领成功，交互状态将由系统更新为 InProgress
                    }
                    Handler.RemoveRequest(PendingRequestID);
                }
            }
        }
    });
}
```

### 进阶用法

**自定义智能对象行为定义**：继承 `USmartObjectMassBehaviorDefinition` 来定义实体在交互期间的具体行为。

```cpp
// 来源: Engine/Plugins/Runtime/MassGameplay/Source/MassSmartObjects/Public/MassSmartObjectBehaviorDefinition.h
UCLASS()
class UMyHealBehaviorDefinition : public USmartObjectMassBehaviorDefinition
{
    GENERATED_BODY()
public:
    UPROPERTY(EditDefaultsOnly, Category = "Heal")
    float HealAmount = 50.f;

    virtual void Activate(FMassCommandBuffer& CommandBuffer, const FMassBehaviorEntityContext& EntityContext) const override
    {
        // 在交互开始时，可以为实体添加一个临时的“正在治疗”Fragment
        // CommandBuffer.AddFragment<FMassIsHealingFragment>(EntityContext.EntityView.GetEntity());
    }

    virtual void Deactivate(FMassCommandBuffer& CommandBuffer, const FMassBehaviorEntityContext& EntityContext) const override
    {
        // 在交互结束时，移除临时Fragment并应用治疗效果
        // CommandBuffer.RemoveFragment<FMassIsHealingFragment>(EntityContext.EntityView.GetEntity());
        // ... 应用 HealAmount 到实体的生命值 Fragment
    }
};
```

**使用 MRU (最近使用) 槽位**：通过 `UMassSmartObjectSettings` 配置，防止实体反复使用同一个智能对象槽位。

```cpp
// 在项目的 DefaultGame.ini 或通过编辑器设置
// [/Script/MassSmartObjects.MassSmartObjectSettings]
// MRUSlotsMaxCount=4
// bUseCooldownForMRUSlots=true
// MRUSlotsCooldown=10.0
```

## Demo 示例

一个最小化的示例，展示如何创建一个会寻找并使用“治疗站”智能对象的 Mass 实体。

```cpp
// MyHealerEntityTrait.h
#pragma once
#include "MassEntityTraitBase.h"
#include "MyHealerEntityTrait.generated.h"

UCLASS(meta = (DisplayName = "Healer Entity"))
class UMyHealerEntityTrait : public UMassEntityTraitBase
{
    GENERATED_BODY()
protected:
    virtual void BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const override;
};

// MyHealerEntityTrait.cpp
#include "MyHealerEntityTrait.h"
#include "MassSmartObjectUserTrait.h"
#include "MassSmartObjectFragments.h"

void UMyHealerEntityTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 1. 添加基础的 SmartObject User 特性
    UMassSmartObjectUserTrait* SOUserTrait = BuildContext.AddTrait<UMassSmartObjectUserTrait>();
    SOUserTrait->UserTags.AddTag(FGameplayTag::RequestGameplayTag(TEXT("Role.Healer")));

    // 2. 添加自定义的 Fragment 来存储治疗相关数据（可选）
    // BuildContext.AddFragment<FMyHealerDataFragment>();
}
```

```cpp
// MyHealerProcessor.h
#pragma once
#include "MassProcessor.h"
#include "MyHealerProcessor.generated.h"

UCLASS()
class UMyHealerProcessor : public UMassProcessor
{
    GENERATED_BODY()
public:
    UMyHealerProcessor();
protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

    FMassEntityQuery EntityQuery;
};

// MyHealerProcessor.cpp
#include "MyHealerProcessor.h"
#include "MassSmartObjectHandler.h"
#include "MassSmartObjectFragments.h"
#include "MassSignalSubsystem.h"
#include "SmartObjectSubsystem.h"

UMyHealerProcessor::UMyHealerProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EProcessingPhase::PrePhysics; // 或合适的阶段
}

void UMyHealerProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassSmartObjectUserFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    // 添加其他需要的 Fragment，如生命值
    EntityQuery.AddTagRequirement<FMassInActiveSmartObjectsRangeTag>(EMassFragmentPresence::None); // 确保实体不在非活动区域
}

void UMyHealerProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    USmartObjectSubsystem* SOSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(EntityManager.GetWorld());
    UMassSignalSubsystem* SignalSubsystem = UWorld::GetSubsystem<UMassSignalSubsystem>(EntityManager.GetWorld());
    if (!SOSubsystem || !SignalSubsystem) return;

    FMassSmartObjectHandler Handler(Context, *SOSubsystem, *SignalSubsystem);

    EntityQuery.ForEachEntityChunk(Context, [&](FMassExecutionContext& ExecContext)
    {
        const int32 NumEntities = ExecContext.GetNumEntities();
        auto UserFragments = ExecContext.GetMutableFragmentView<FMassSmartObjectUserFragment>();
        auto TransformFragments = ExecContext.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FMassEntityHandle Entity = ExecContext.GetEntity(i);
            FMassSmartObjectUserFragment& User = UserFragments[i];
            const FVector& Loc = TransformFragments[i].GetTransform().GetLocation();

            // 简化逻辑：如果没有交互且不在冷却中，则寻找治疗站
            if (User.InteractionStatus == EMassSmartObjectInteractionStatus::Unset
                && User.InteractionCooldownEndTime <= EntityManager.GetWorld()->GetTimeSeconds())
            {
                UE::Mass::SmartObject::FFindCandidatesParameters Params;
                Params.UserTags = User.UserTags;
                Params.QueryOrigin = Loc;
                // 可以添加 ActivityRequirements 来过滤只找治疗类型的智能对象

                FMassSmartObjectRequestID ReqID = Handler.FindCandidatesAsync(Entity, MoveTemp(Params));
                // 在实际项目中，你需要将 ReqID 存储起来（例如通过一个临时的 Fragment 或 Map）
            }
            // ... 后续处理请求结果和认领逻辑，参考“基本用法”部分
        }
    });
}
```

## 模块依赖

MassGameplay 插件内部模块众多，但对外部使用者而言，主要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 框架的核心，提供实体、Fragment、Processor 等基础概念。 |
| `SmartObjects` | 提供智能对象定义、子系统和运行时逻辑，是 MassSmartObjects 模块的基础。 |
| `ZoneGraph` | 提供区域图数据结构和查询，用于基于车道的智能对象搜索和寻路。 |
| `MassSignals` | Mass 框架的信号系统，用于实体间异步通信（如通知交互完成）。 |
| `MassNavigation` | 提供寻路和移动功能，常与 MassMovement 模块配合使用。 |
| `MassRepresentation` | 处理实体的视觉表示（如静态网格体、骨骼网格体、Niagara 粒子）。 |
| `MassSpawner` | 提供实体生成和管理的功能。 |

## 维护状态

### 近期更新

```
- 2024-10-24 457eba2e5782 PR #13332: Added std::is_trivially_copyable to the CFragment concept.
- 2024-10-22 1192ee320773 [MassAI] minor update to SmartObject task to expose NumSlots for bindings and fail claim task when no slots are available
- 2024-10-18 bd64013409de [MassSmartObject] Added basic MRU slots implementation - Added new options in UMassSmartObjectSettings -- MRUSlotsMaxCount: Possible values between 0 and 4 (Default: 0, meaning that the feature is not used; up to 4 slots) -- bUseCooldownForMRUSlots: to allow the most recently used slots to be considered again a given period of time -- MRUSlotsCooldown: period of time during which a given slot will not be considered after being used - Enabled UE types in namespaces for MassSmartObject (i.e., AllowUETypesInNamespaces)
```

### 维护评价

MassGameplay 是 Unreal Engine 5 中**活跃维护**的核心实验性功能之一。

- **创建时间**：约 4 年前（2021年），相对较新。
- **更新频率**：近期（2024年10月）仍有实质性功能更新（如 MRU 槽位）和底层改进，表明 Epic 官方仍在积极开发和完善。
- **维护状态**：**活跃维护**。作为 UE5 大规模模拟的官方解决方案，其重要性不言而喻。
- **已知限制**：插件本身标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，意味着 API 可能还不稳定，需要开发者手动启用并承担未来版本变动的风险。文档相对较少，学习曲线较陡。
- **推荐使用**：**强烈推荐**给有明确大规模实体模拟需求的项目。它是目前 UE 生态中解决此类性能问题的最正统、最强大的方案。建议在项目早期进行技术验证，并密切关注引擎版本更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/mass-entity-in-unreal-engine/) (MassEntity 框架总览，MassGameplay 是其应用层)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)