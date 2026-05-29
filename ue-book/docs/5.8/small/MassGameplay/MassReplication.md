# MassReplication

> Implementation of large-scale agent simulation based on MassEntity

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体复制 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、演示资源、测试套件） |
| 模块 | `MassReplication` (Runtime), `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

`MassReplication` 是 `MassGameplay` 插件的核心模块之一，专门解决基于 **MassEntity (ECS)** 架构的大规模实体（如NPC、AI代理）的**网络同步**问题。它并非简单的 Actor 复制系统，而是一个高度优化的、面向数据的网络复制框架，专为海量实体设计。

**核心问题**：传统的 UE Actor 复制系统在面对成百上千个网络同步实体时，会遇到严重的性能和带宽瓶颈。`MassReplication` 通过以下方式解决：
1.  **Bubble 系统**：为每个客户端（玩家）创建独立的“数据泡泡”（Bubble），仅同步该玩家附近或关注的数据，避免全局广播。
2.  **数据驱动**：复制的数据（如位置、状态）以轻量级的 Fragment 形式存储和传输，比 Actor 的属性复制更高效。
3.  **LOD 集成**：与 `MassLOD` 紧密结合，根据实体与玩家的距离和重要性，动态调整复制精度（LOD）和频率。

**为什么存在**：它是为了实现《堡垒之夜》等游戏中大规模、高并发的玩家/NPC 环境而生的，是 Unreal Engine 5 “Mass” 框架实现真正“海量”规模网络多人游戏的关键技术栈。

## 使用场景

- 你需要在大型多人在线游戏（MMO）或大逃杀游戏中同步数千个AI敌人或中立生物。
- 你在制作一款实时战略（RTS）游戏，需要同步大量单位和建筑的状态。
- 你的游戏有大量玩家可见但交互性不同的实体（如远处的车辆、群众），需要一种高性能的网络方案。

## 蓝图用法

`MassReplication` 主要是一个 C++ 驱动的底层系统，其核心类（如处理器、子系统）不直接暴露为蓝图节点。蓝图层面主要通过配置和使用相关的 `UMassEntityTraitBase` 来间接应用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Replication` (Trait) | 为实体模板添加网络复制能力，配置 LOD 参数、复制器类等。 | `UMassReplicationTrait` |

### 使用示例（蓝图描述）

1.  在创建 `MassEntityTemplate` 的蓝图（或代码）中，为实体添加 `Replication` Trait。
2.  在该 Trait 的属性中，设置 `BubbleInfoClass`（例如，使用自定义的 `AMassClientBubbleInfoBase` 子类）和 `ReplicatorClass`（例如，使用自定义的 `UMassReplicatorBase` 子类）。
3.  配置 `FMassReplicationParameters`，包括各级LOD的距离、最大数量限制等。
4.  游戏运行时，`MassReplication` 系统会自动根据这些配置，为该类实体执行网络同步。

## C++ 用法

该模块的设计极度模块化和可扩展，主要通过继承和模板特化来定义具体的复制逻辑。

### 头文件引入

```cpp
#include "MassReplicationSubsystem.h"
#include "MassReplicationProcessor.h"
#include "MassClientBubbleHandler.h"
#include "MassReplicationTransformHandlers.h"
```

### 基本用法：定义一个可复制的 Agent 数据

首先，定义在客户端和服务器之间传输的数据结构。
*来源: Public/MassReplicationTypes.h, Public/MassReplicationTemplates.h*

```cpp
// 1. 定义需要复制的数据结构
USTRUCT()
struct FMyReplicatedAgentData
{
    GENERATED_BODY()

    UPROPERTY(Transient)
    FVector Position;

    UPROPERTY(Transient)
    float Health = 100.f;

    // 可选：自定义脏检查
    static bool IsDirty(const FMyReplicatedAgentData& A, const FMyReplicatedAgentData& B)
    {
        return !A.Position.Equals(B.Position, 1.0f) || !FMath::IsNearlyEqual(A.Health, B.Health);
    }
};

// 2. 定义 Agent 基类，包含网络ID和模板ID
USTRUCT()
struct FMyAgent : public FReplicatedAgentBase
{
    GENERATED_BODY()
    // 使用宏声明访问器
    UE_MASSREPLICATION_DECLARE_ACCESSORS()
private:
    UPROPERTY(Transient)
    FMyReplicatedAgentData MyData;
};

// 3. 实现访问器
UE_MASSREPLICATION_IMPLEMENT_ACCESSOR(FMyAgent, FMyReplicatedAgentData, MyData)

// 4. （可选）特化复制 Trait，定义如何从 Fragment 提取/应用数据
template<>
struct UE::Mass::Replication::TReplicationTraits<FMyReplicatedAgentData>
{
    // 示例：从 FHealthFragment 提取数据
    static void ExtractData(const FHealthFragment& Fragment, FMyReplicatedAgentData& OutData)
    {
        OutData.Health = Fragment.Health;
    }

    // 示例：应用数据到 FHealthFragment
    static void ApplyData(FHealthFragment& Fragment, const FMyReplicatedAgentData& Data)
    {
        Fragment.Health = Data.Health;
    }
};
```

### 进阶用法：创建自定义复制处理器

服务器端需要处理器来收集实体数据并发送到客户端泡泡。
*来源: Public/MassReplicationProcessor.h, Public/MassReplicationTemplates.h*

```cpp
// 1. 声明处理器和泡泡处理器类型 (使用便捷宏)
UE_MASSREPLICATION_DECLARE_HANDLERS(MyData, FMyReplicatedAgentData, FTransformFragment, FHealthFragment);

// 2. 创建客户端泡泡处理器基类
using FMyFastArrayItem = FMassFastArrayItemBase; // 通常需要派生并添加更多数据

class UMyClientBubbleHandler : public TClientBubbleHandlerBase<FMyFastArrayItem>
{
    // 内部组合一个或多个数据处理器
    FMassClientBubbleTransformHandler<FMyFastArrayItem> TransformHandler;
    FMassClientBubbleMyDataHandler<FMyFastArrayItem> MyDataHandler;

public:
    UMyClientBubbleHandler()
        : TransformHandler(*this)
        , MyDataHandler(*this)
    {}

    // 重写 PostReplicatedAdd，当客户端泡泡新增数据时调用
    virtual void PostReplicatedAdd(const TArrayView<int32> AddedIndices, int32 FinalSize) override
    {
        // 使用模板方法处理添加
        PostReplicatedAddHelper(AddedIndices, MyDataHandler);
    }

    // 重写 PostReplicatedChange
    virtual void PostReplicatedChange(const TArrayView<int32> ChangedIndices, int32 FinalSize) override
    {
        PostReplicatedChangeHelper(ChangedIndices, MyDataHandler);
    }
};

// 3. 创建服务器端复制器
class UMyReplicator : public UMassReplicatorBase
{
    // 使用模板包组合多个处理器
    UE::Mass::Replication::TReplicationProcessorHandlerPack<
        FMassReplicationProcessorTransformHandlerBase,
        FMassReplicationProcessorMyDataHandler
    > ProcessorHandlerPack;

public:
    virtual void AddRequirements(FMassEntityQuery& EntityQuery) override
    {
        ProcessorHandlerPack.AddRequirements(EntityQuery);
    }

    virtual void ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext) override
    {
        // 调用基类模板方法，传入对应的回调
        CalculateClientReplication<FMyFastArrayItem>(
            Context, ReplicationContext,
            [this](FMassExecutionContext& Ctx) { ProcessorHandlerPack.CacheFragmentViews(Ctx); },
            [this](FMassExecutionContext& Ctx, int32 Idx, FMyAgent& Agent, const FMassClientHandle& Handle) -> FMassReplicatedAgentHandle
            {
                // 添加实体逻辑，返回新句柄
                return FMassReplicatedAgentHandle();
            },
            [this](FMassExecutionContext& Ctx, int32 Idx, EMassLOD::Type LOD, double Time, FMassReplicatedAgentHandle Handle, const FMassClientHandle& ClientHandle)
            {
                // 修改实体逻辑
                ProcessorHandlerPack.ModifyEntity(Handle, Idx, *ClientBubbles[ClientHandle.GetIndex()]);
            },
            [](FMassExecutionContext& Ctx, FMassReplicatedAgentHandle Handle, const FMassClientHandle& ClientHandle)
            {
                // 移除实体逻辑
            }
        );
    }
};
```

## Demo 示例

以下是一个最小化的服务器端复制处理器实现框架。
*来源: Public/MassReplicationProcessor.h*

```cpp
// MyMassReplicator.h
#pragma once

#include "MassReplicationProcessor.h"
#include "MassReplicationTemplates.h"
#include "MyAgentData.h" // 包含之前定义的 FMyAgent 等

class UMyReplicator : public UMassReplicatorBase
{
    GENERATED_BODY()

public:
    UMyReplicator();

    virtual void AddRequirements(FMassEntityQuery& EntityQuery) override;
    virtual void ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext) override;

private:
    // 处理器包，组合了 Transform 和自定义数据的处理逻辑
    UE::Mass::Replication::TReplicationProcessorHandlerPack<
        FMassReplicationProcessorPositionYawHandler,
        FMassReplicationProcessorMyDataHandler // 需要先定义
    > ProcessorHandlerPack;
};

// MyMassReplicator.cpp
#include "MyMassReplicator.h"
#include "MassClientBubbleHandler.h"

// 假设 FMyFastArrayItem 和 UMyClientBubbleHandler 已在其他地方定义
// 假设一个静态的或可访问的 ClientBubbles 数组
// static TArray<UMyClientBubbleHandler*> ClientBubbles;

UMyReplicator::UMyReplicator()
{
}

void UMyReplicator::AddRequirements(FMassEntityQuery& EntityQuery)
{
    // 让处理器包添加所有必要的 Fragment 需求（Transform, Health 等）
    ProcessorHandlerPack.AddRequirements(EntityQuery);
}

void UMyReplicator::ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext)
{
    // 使用基类提供的强大模板方法，传入具体的回调 lambda
    CalculateClientReplication<FMyFastArrayItem>(
        Context,
        ReplicationContext,
        // CacheViews: 缓存所有 Fragment 视图
        [this](FMassExecutionContext& Ctx) {
            ProcessorHandlerPack.CacheFragmentViews(Ctx);
        },
        // AddEntity: 为新实体创建复制数据并添加到客户端泡泡
        [this](FMassExecutionContext& Ctx, int32 EntityIdx, FMyAgent& ReplicatedAgent, const FMassClientHandle& ClientHandle) -> FMassReplicatedAgentHandle {
            // 1. 从处理器包中提取数据到 ReplicatedAgent
            ProcessorHandlerPack.AddEntity(EntityIdx, ReplicatedAgent.MyData); // 简化示意
            // 2. 调用泡泡处理器的 AddAgent
            UMyClientBubbleHandler* Bubble = ClientBubbles[ClientHandle.GetIndex()];
            return Bubble->AddAgent(Ctx.GetEntity(EntityIdx), ReplicatedAgent);
        },
        // ModifyEntity: 更新现有实体的复制数据
        [this](FMassExecutionContext& Ctx, int32 EntityIdx, EMassLOD::Type LOD, double Time, FMassReplicatedAgentHandle Handle, const FMassClientHandle& ClientHandle) {
            // 让处理器包更新泡泡中的数据
            UMyClientBubbleHandler* Bubble = ClientBubbles[ClientHandle.GetIndex()];
            ProcessorHandlerPack.ModifyEntity(Handle, EntityIdx, *Bubble);
        },
        // RemoveEntity: 从客户端泡泡中移除实体
        [](FMassExecutionContext& Ctx, FMassReplicatedAgentHandle Handle, const FMassClientHandle& ClientHandle) {
            UMyClientBubbleHandler* Bubble = ClientBubbles[ClientHandle.GetIndex()];
            Bubble->RemoveAgentChecked(Handle);
        }
    );
}
```

## 模块依赖

要使用 `MassReplication` 模块，你的项目需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MassEntity` | 核心的 Mass Entity Component System (ECS) 框架，是本模块的基础。 |
| `MassLOD` | 提供大规模实体的LOD（细节层次）管理，`MassReplication` 依赖它进行基于距离的复制决策。 |
| `MassSpawner` | 提供实体生成和销毁功能，客户端复制过程中会使用它来创建/销毁实体。 |
| `MassGameplayExternalTraits` | 提供一些可选的、通用的实体 Trait 扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 回滚了对 MassAgentComponent 的更改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | 表示层：在关闭实例化静态网格（ISM）前等待Actor就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了Mass人群中非傀儡Actor的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | 修复了LOD计算器中逐个查看器路径的一系列历史遗留bug。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M | 表示层重构，简化了Actor额外帧保留逻辑的计算。 |

### 维护评价

- **状态**: **实验性但活跃维护中**。该模块被标记为 `IsExperimentalVersion: true`，说明其API和功能仍在快速演进，可能存在不稳定性。
- **活跃度**: **高**。从提交记录看，最近（2026年5月）仍有大量针对表示层（MassRepresentation）和复制逻辑的bug修复与优化，表明 Epic 的开发团队仍在积极开发和完善这个系统。
- **年龄**: 创建于 2021 年底，至今约 3 年，是 UE5 的“新”技术栈。
- **建议**: **推荐用于前沿、对性能有极致要求的大型项目**，但使用者需要接受其“实验性”状态，密切关注API变更，并准备好深入阅读和调试源码。对于中小型项目或对稳定性要求极高的商业项目，需谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassReplication)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay/Source/MassGameplayTestSuite)