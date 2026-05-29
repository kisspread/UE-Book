# MassSmartObjects

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模智能对象模块 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（核心模块，处理实体与智能对象交互） |
| 模块 | `MassSmartObjects` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassSmartObjects) | |

## 用途

`MassSmartObjects` 模块是 **MassEntity 大规模实体仿真框架** 与 **SmartObjects 智能对象系统** 之间的桥梁。它解决的核心问题是：在需要同时处理成千上万个实体（如NPC、单位）的场景中，如何让这些实体能够高效地与场景中的可交互点（智能对象，如长椅、车辆、交互设备）进行交互。

传统的基于 Actor 的智能对象系统无法承受如此高的实体数量。该模块通过 MassEntity 的组件化架构和批处理查询机制，使得大规模实体能够：
1. **高效搜索**：批量异步查询周围可用的智能对象。
2. **竞争与认领**：当多个实体竞争同一个智能对象时，提供基于优先级的认领机制。
3. **状态管理**：管理实体与智能对象交互的完整生命周期（寻找 -> 认领 -> 使用 -> 释放）。
4. **集成路径图**：与 ZoneGraph 系统集成，使实体能够沿着路径图（如人行道）寻找智能对象。

## 使用场景

- **城市模拟游戏**：数以千计的市民需要自动寻找并使用长椅、饮水机、商店等。
- **大规模 RTS**：大量单位需要使用维修站、资源点、集结点等。
- **开放世界沙盒**：高密度的NPC群体需要与场景中分散的交互点互动。
- **任何使用 MassEntity 仿真大量AI，且需要与场景物体进行交互的游戏或应用**。

## 蓝图用法

核心功能通过 `FMassSmartObjectHandler` 结构体暴露，在 `UMassProcessor` 或 `UMassObserverProcessor` 的 `Execute` 函数中使用。

### 核心节点

| 节点 | 说明 | 所在类/结构 |
|---|---|---|
| `FindCandidatesAsync` | 创建一个异步请求，在指定位置或路径点附近搜索兼容的智能对象。返回请求ID。 | `FMassSmartObjectHandler` |
| `GetRequestCandidates` | 轮询请求结果，检查搜索是否完成并获取候选列表。 | `FMassSmartObjectHandler` |
| `ClaimCandidate` | 从候选列表中认领第一个可用的智能对象槽位。 | `FMassSmartObjectHandler` |
| `ClaimSmartObject` | 直接认领一个智能对象中任意可用的、包含特定行为定义的槽位。 | `FMassSmartObjectHandler` |
| `StartUsingSmartObject` | 激活已认领智能对象关联的 Mass 行为（开始交互）。 | `FMassSmartObjectHandler` |
| `StopUsingSmartObject` | 停止当前正在进行的交互。 | `FMassSmartObjectHandler` |
| `ReleaseSmartObject` | 释放对智能对象槽位的占用，更新用户状态。 | `FMassSmartObjectHandler` |
| `AddUserTag` | 为实体添加用户标签，用于智能对象过滤。 | 蓝图（通过 Trait） |

### 使用示例（蓝图描述）

在一个 Mass Processor 的 `Execute` 节点中：
1. 从上下文中获取 `SmartObjectSubsystem` 和 `SignalSubsystem`。
2. 创建一个 `FMassSmartObjectHandler` 实例。
3. 查询带有 `FMassSmartObjectUserFragment` 的实体。
4. 对于每个需要寻找交互的实体，调用 `FindCandidatesAsync`，传入实体位置和用户标签。
5. 在下一帧或稍后，使用 `GetRequestCandidates` 和存储的请求ID检查结果。
6. 若有候选结果，调用 `ClaimCandidate` 认领一个。
7. 认领成功后，调用 `StartUsingSmartObject` 开始交互。
8. 交互完成后，调用 `ReleaseSmartObject` 释放。

## C++ 用法

### 头文件引入

```cpp
#include "MassSmartObjectHandler.h"
#include "MassSmartObjectFragments.h"
#include "MassSmartObjectProcessor.h"
#include "MassSmartObjectTypes.h"
```

### 基本用法

```cpp
// 在一个 UMassProcessor 的 Execute 函数中
void UMySmartObjectProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 1. 获取所需的子系统
    USmartObjectSubsystem* SmartObjectSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(GetWorld());
    UMassSignalSubsystem* SignalSubsystem = UWorld::GetSubsystem<UMassSignalSubsystem>(GetWorld());
    if (!SmartObjectSubsystem || !SignalSubsystem)
    {
        return;
    }

    // 2. 创建 Handler
    FMassSmartObjectHandler SOHandler(Context, *SmartObjectSubsystem, *SignalSubsystem);

    // 3. 查询所有有智能对象用户 Fragment 的实体
    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& ExecContext)
    {
        const int32 NumEntities = ExecContext.GetNumEntities();
        const TConstArrayView<FMassSmartObjectUserFragment> UserFragments = ExecContext.GetFragmentView<FMassSmartObjectUserFragment>();
        const TConstArrayView<FTransformFragment> TransformFragments = ExecContext.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            FMassSmartObjectUserFragment& User = UserFragments[i];
            const FVector Location = TransformFragments[i].GetTransform().GetLocation();

            // 如果实体当前空闲且不在冷却期
            if (User.InteractionStatus == EMassSmartObjectInteractionStatus::Unset
                && User.InteractionCooldownEndTime <= GetWorld()->GetTimeSeconds())
            {
                // 4. 异步查找附近的智能对象
                UE::Mass::SmartObject::FFindCandidatesParameters Params;
                Params.UserTags = User.UserTags;
                Params.Location = Location;
                FMassSmartObjectRequestID RequestID = SOHandler.FindCandidatesAsync(ExecContext.GetEntity(i), MoveTemp(Params));

                // 注意：真实情况中，请求是异步的，需要在后续的 Tick 中通过 RequestID 查询结果。
                // 此处仅为流程示意。
            }
        }
    });
}
```
*来源文件: `MassSmartObjectProcessor.cpp`*

### 进阶用法

结合请求结果和认领：
```cpp
// 在一个处理请求结果的处理器中
if (const FMassSmartObjectCandidateSlots* Candidates = SOHandler.GetRequestCandidates(RequestID))
{
    if (Candidates->NumSlots > 0)
    {
        // 5. 认领一个候选对象
        FSmartObjectClaimHandle ClaimHandle = SOHandler.ClaimCandidate(Entity, User, *Candidates, ESmartObjectClaimPriority::Normal);
        if (ClaimHandle.IsValid())
        {
            // 6. 开始使用智能对象
            if (SOHandler.StartUsingSmartObject(Entity, User, ClaimHandle))
            {
                // 交互已开始，User.InteractionStatus 变为 InProgress
                // 可以添加一个定时 Fragment 来管理交互时间
                CommandBuffer.AddFragment<FMassSmartObjectTimedBehaviorFragment>(Entity);
            }
        }
    }
    // 7. 清理请求
    SOHandler.RemoveRequest(RequestID);
}
```

## Demo 示例

一个自定义的、用于让实体随机寻找并使用智能对象的简单处理器：

**MySmartObjectUserProcessor.h**
```cpp
#pragma once
#include "MassProcessor.h"
#include "MySmartObjectUserProcessor.generated.h"

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
    FMassEntityQuery EntityQuery;
};
```

**MySmartObjectUserProcessor.cpp**
```cpp
#include "MySmartObjectUserProcessor.h"
#include "MassSmartObjectHandler.h"
#include "MassSmartObjectFragments.h"
#include "MassSmartObjectTypes.h"
#include "MassSignalSubsystem.h"
#include "SmartObjectSubsystem.h"
#include "MassExecutionContext.h"
#include "MassEntityTemplateTypes.h"

UMySmartObjectUserProcessor::UMySmartObjectUserProcessor()
{
    ExecutionFlags = (int32)EProcessorExecutionFlags::All;
    ProcessingPhase = EProcessingPhase::PrePhysics;
}

void UMySmartObjectUserProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    EntityQuery.AddRequirement<FMassSmartObjectUserFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddTagRequirement<FMassSmartObjectsTag>(EMassFragmentPresence::All); // 需要匹配的标签
}

void UMySmartObjectUserProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    USmartObjectSubsystem* SmartObjectSubsystem = UWorld::GetSubsystem<USmartObjectSubsystem>(GetWorld());
    UMassSignalSubsystem* SignalSubsystem = UWorld::GetSubsystem<UMassSignalSubsystem>(GetWorld());
    if (!SmartObjectSubsystem || !SignalSubsystem)
    {
        return;
    }

    const UMassSmartObjectSettings* Settings = GetDefault<UMassSmartObjectSettings>();
    FMassSmartObjectHandler SOHandler(Context, *SmartObjectSubsystem, *SignalSubsystem);

    EntityQuery.ForEachEntityChunk(EntityManager, Context, [&](FMassExecutionContext& ExecContext)
    {
        const int32 NumEntities = ExecContext.GetNumEntities();
        const TConstArrayView<FMassSmartObjectUserFragment> UserFragments = ExecContext.GetFragmentView<FMassSmartObjectUserFragment>();
        const TConstArrayView<FTransformFragment> TransformFragments = ExecContext.GetFragmentView<FTransformFragment>();

        for (int32 i = 0; i < NumEntities; ++i)
        {
            const FMassEntityHandle Entity = ExecContext.GetEntity(i);
            FMassSmartObjectUserFragment& User = UserFragments[i];

            // 处理状态机
            switch (User.InteractionStatus)
            {
            case EMassSmartObjectInteractionStatus::Unset:
            {
                // 没有交互，尝试寻找
                const FVector Location = TransformFragments[i].GetTransform().GetLocation();
                UE::Mass::SmartObject::FFindCandidatesParameters Params;
                Params.UserTags = User.UserTags;
                Params.Location = Location;
                // 异步请求，并存储 RequestID（实际项目需要存储在 Fragment 或其他地方）
                FMassSmartObjectRequestID RequestID = SOHandler.FindCandidatesAsync(Entity, MoveTemp(Params));
                // 将 RequestID 存储到用户的某个临时 Fragment 或 Map 中以便后续查询
                break;
            }
            case EMassSmartObjectInteractionStatus::InProgress:
            {
                // 交互中，等待定时处理器或行为完成信号来切换状态
                // 此处可以添加自定义逻辑
                break;
            }
            case EMassSmartObjectInteractionStatus::BehaviorCompleted:
            case EMassSmartObjectInteractionStatus::TaskCompleted:
            {
                // 交互完成，释放
                SOHandler.ReleaseSmartObject(Entity, User, User.InteractionHandle);
                break;
            }
            case EMassSmartObjectInteractionStatus::Aborted:
            {
                // 被中止，同样释放
                SOHandler.ReleaseSmartObject(Entity, User, User.InteractionHandle);
                break;
            }
            }
        }
    });
}
```

## 模块依赖

从 `MassSmartObjects.Build.cs` 分析，该模块的**特有依赖**如下：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 MassEntity 框架，提供实体、处理器、片段等基础设施。 |
| `SmartObjects` | 智能对象子系统，提供场景中可交互对象的定义、注册和查找功能。 |
| `ZoneGraph` | 路径图系统，提供车道数据和基于路径的查询支持。 |
| `MassSignals` | Mass 信号系统，用于向实体发送异步通知（如智能对象激活状态变化）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回退了之前对 MassAgentComponent 的修改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 在切换掉 ISM 之前等待 Actor 准备就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复 Mass 人群中非 puppet Actor 的处理。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复 `TMassLODCalculator` 每个观察者 LOD 路径中的已有 bug 集群。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 将两个手动计算的 `bDoKeepActorExtraFrame` 切换为使用新的 UE::M 方法。 |

*注：以上 git 历史来自 `MassGameplay` 插件根目录，涵盖所有子模块。最近提交主要集中在 `MassRepresentation` 模块。*

### 维护评价

- **状态**：**实验性且持续维护中**。
- **分析**：
    1.  `MassSmartObjects` 模块是 `MassGameplay` 这一实验性插件的一部分，自 2021 年创建以来一直处于活跃开发中。
    2.  最近的提交（2026年5月）虽然没有直接针对 `MassSmartObjects` 的改动，但关联模块（如 `MassRepresentation`）的持续更新表明整个框架仍在积极维护。
    3.  从源码注释和废弃标记（如 `UE_DEPRECATED(5.7, ...)`）可以看出，API 在不断演进和优化，保持着向后兼容的意识。
    4.  作为实验性功能，其 API 可能在未来版本中发生变化，不适合用于追求长期稳定性的生产项目核心功能，但非常适合用于原型开发和对性能有极致要求的项目。
- **建议**：**推荐在实验性项目或需要超高实体交互密度的场景中使用**。在生产项目中使用前，需评估其 API 稳定性风险，并密切关注引擎更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassSmartObjects)
- [官方文档]() （暂无专门文档，可参考 [MassEntity 文档](https://docs.unrealengine.com/5.8/en-US/mass-entity-in-unreal-engine/) 和 [Smart Objects 文档](https://docs.unrealengine.com/5.8/en-US/smart-objects-in-unreal-engine/)）