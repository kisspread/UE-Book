# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（基于 MassEntity 实现的大规模智能体模拟）

| 属性 | 值 |
|---|---|
| 中文名 | 大规模游戏逻辑 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MassActors` (Runtime), `MassCharacterTrajectory` (Runtime), `MassCommon` (Runtime), `MassEQS` (Runtime), `MassGameplayDebug` (Runtime), `MassGameplayEditor` (Runtime), `MassGameplayExternalTraits` (Runtime), `MassGameplayTestSuite` (Runtime), `MassLOD` (Runtime), `MassMovement` (Runtime), `MassMovementEditor` (Runtime), `MassReplication` (Runtime), `MassRepresentation` (Runtime), `MassSimulation` (Runtime), `MassSmartObjects` (Runtime), `MassSpawner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay) | |

## 用途

MassGameplay 是一个基于 Mass Entity System 的高级框架，专门用于处理大规模实体（如成千上万的 NPC、车辆、掉落物等）的游戏逻辑。它在 MassEntity 的纯数据处理能力之上，提供了面向游戏玩法的系统，包括但不限于：
1.  **高效复制与同步**：通过 `MassReplication` 模块，为大规模实体提供了专用的、优化的网络复制方案，解决了传统 Actor 复制在大量实体下的性能瓶颈。
2.  **实体生命周期管理**：通过 `MassSpawner` 模块，方便地管理和生成/销毁大量实体。
3.  **运动与AI**：通过 `MassMovement`、`MassLOD` 等模块，为实体提供面向性能的移动、LOD（细节层次）切换和感知（如 EQS 查询）。
4.  **可视化与表示**：通过 `MassRepresentation` 模块，将 ECS 数据转化为视觉表示（如 Actor、静态网格体）。

简而言之，该插件解决了传统面向对象（Actor-per-entity）模式在面对海量实体时遇到的性能、内存和同步难题，让开发者能够更高效地构建拥有大量动态实体的游戏世界。

## 使用场景

- 你在开发一个开放世界游戏，场景中有成百上千的平民 NPC、动物或车辆需要持续运行行为和模拟。
- 你正在制作一个即时战略（RTS）游戏或大逃杀游戏，需要管理地图上数以万计的单位、子弹或可拾取物品。
- 你需要实现一个大规模人群系统，例如体育场观众、城市街道人流，且要求这些实体能够与玩家进行一定程度的交互并支持网络同步。
- 你的游戏对性能要求极高，需要将实体逻辑与渲染完全解耦，利用批处理和 ECS 架构的优势。

## 蓝图用法

MassGameplay 主要是一个 C++ 优先的框架，其核心功能（如自定义复制逻辑、自定义处理器）需要通过 C++ 扩展。部分管理类和数据结构暴露了蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNetIDFromHandle` | 根据实体句柄获取其网络ID。 | `UMassReplicationSubsystem` |
| `RegisterBubbleInfoClass` | 注册一种客户端气泡（Bubble）信息类，用于管理特定类型实体的网络复制。 | `UMassReplicationSubsystem` |
| `GetClientBubble` | 安全地获取指定客户端句柄和气泡类型对应的客户端气泡 Actor。 | `UMassReplicationSubsystem` |

### 使用示例（蓝图描述）
由于 MassGameplay 的核心是 C++ 系统，蓝图通常用于触发或配置。例如，你可以在一个自定义 GameMode 的 `BeginPlay` 事件中，通过蓝图调用 C++ 函数来初始化复制子系统，或者通过编辑器中的 `MassReplicationTrait` 来配置实体的复制参数。

## C++ 用法

MassGameplay 的强大之处在于其高度可定制的 C++ 扩展点，特别是 `MassReplication` 模块。以下示例展示了如何扩展复制系统以复制自定义数据。

### 头文件引入

```cpp
#include "MassReplicationTypes.h"
#include "MassReplicationTemplates.h"
#include "MassReplicationProcessor.h"
#include "MassClientBubbleHandler.h"
#include "MassReplicationTrait.h"
```

### 基本用法：定义可复制数据和处理程序

首先，定义你想要复制的结构化数据。

```cpp
// MyReplicatedData.h
#pragma once
#include "MassReplicationTypes.h"

// 复制数据结构，需要继承自某种基础类型或包含网络ID等核心数据
USTRUCT()
struct FMyReplicatedData : public FReplicatedAgentBase
{
    GENERATED_BODY()
    // 继承自 FReplicatedAgentBase 已包含 NetID 和 TemplateID
    // 添加你需要复制的额外数据，例如生命值
    UPROPERTY(Transient)
    float Health = 100.0f;
};

// 声明模板特化，定义如何从 Fragment 提取数据和应用数据到 Fragment
// 通常在 .h 文件中声明，在 .cpp 中实现
template<>
struct UE::Mass::Replication::TReplicationTraits<FMyReplicatedData>
{
    // 定义如何从 FHealthFragment 提取数据到 FMyReplicatedData
    static void ExtractData(const FHealthFragment& Fragment, FMyReplicatedData& OutData)
    {
        OutData.Health = Fragment.Health;
    }

    // 定义如何将 FMyReplicatedData 的数据应用到 FHealthFragment
    static void ApplyData(FHealthFragment& Fragment, const FMyReplicatedData& Data)
    {
        Fragment.Health = Data.Health;
    }

    // 可选：自定义脏检查逻辑
    static bool IsDirty(const FMyReplicatedData& OldData, const FMyReplicatedData& NewData)
    {
        return !FMath::IsNearlyEqual(OldData.Health, NewData.Health, 0.1f);
    }
};
```

### 进阶用法：配置实体复制处理器

使用宏或手动创建处理器，将定义的 Fragment 与复制数据关联起来。

```cpp
// MyReplicationHandlers.h
#pragma once
#include "MassReplicationTemplates.h"
#include "MyReplicatedData.h"
#include "Fragments/HealthFragment.h" // 假设你有一个生命值 Fragment

// 便捷方式：使用宏声明服务器和客户端的处理器类型
// 它会生成 FMassReplicationProcessorMyDataHandler 和 FMassClientBubbleMyDataHandler
UE_MASSREPLICATION_DECLARE_HANDLERS(MyData, FMyReplicatedData, FHealthFragment);

// 或者手动定义（效果相同）：
/*
using FMassReplicationProcessorMyDataHandler = UE::Mass::Replication::TReplicationProcessorHandler<FMyReplicatedData, FHealthFragment>;
using FMassClientBubbleMyDataHandler = UE::Mass::Replication::TClientBubbleFragmentHandler<FMyReplicatedData, FHealthFragment>;
*/
```

接下来，创建实际的处理器类来使用这些 Handler。

```cpp
// MyReplicationProcessor.h
#pragma once
#include "MassReplicationProcessor.h"
#include "MyReplicationHandlers.h"

UCLASS()
class UMyReplicationProcessor : public UMassReplicationProcessor
{
    GENERATED_BODY()
public:
    UMyReplicationProcessor();

protected:
    virtual void ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager) override;
    virtual void Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context) override;

private:
    // 服务器端数据处理器，负责从实体 Fragment 提取数据
    FMassReplicationProcessorMyDataHandler ServerDataHandler;
};
```

```cpp
// MyReplicationProcessor.cpp
#include "MyReplicationProcessor.h"

UMyReplicationProcessor::UMyReplicationProcessor()
{
    bAutoRegisterWithProcessingPhases = false; // 复制处理器通常手动管理执行
}

void UMyReplicationProcessor::ConfigureQueries(const TSharedRef<FMassEntityManager>& EntityManager)
{
    Super::ConfigureQueries(EntityManager);
    // 为服务器端处理器添加 Fragment 需求
    ServerDataHandler.AddRequirements(EntityQuery);
    // 还需要其他必要的 Fragment，例如位置、网络ID等（由父类或 Replicator 处理）
    EntityQuery.AddRequirement<FMassNetworkIDFragment>(EMassFragmentAccess::ReadOnly);
}

void UMyReplicationProcessor::Execute(FMassEntityManager& EntityManager, FMassExecutionContext& Context)
{
    // 此处理器的 Execute 逻辑通常由父类 UMassReplicationProcessor::Execute 驱动
    // 核心复制逻辑在 UMassReplicatorBase::CalculateClientReplication 中，它会调用你提供的回调。
    // 你需要派生一个 UMassReplicatorBase 的子类来整合你的处理器。
    // 示例：UMassReplicatorBase 子类会在它的 ProcessClientReplication 中调用：
    // ServerDataHandler.CacheFragmentViews(Context);
    // 然后循环实体，并调用 ServerDataHandler.AddEntity(...) 或 ModifyEntity(...)
}
```

### Demo 示例

一个最小化的、专注于展示复制数据定义的示例。

**MyMinimalReplicator.h**
```cpp
#pragma once
#include "MassReplicationProcessor.h"
#include "MassReplicationTemplates.h"
#include "MyReplicatedData.h" // 包含前面定义的 FMyReplicatedData 和 Traits

// 为生命值数据创建处理程序包
using FMyReplicationServerHandlerPack = UE::Mass::Replication::TReplicationProcessorHandlerPack<
    UE::Mass::Replication::TReplicationProcessorHandler<FMyReplicatedData, FHealthFragment>
>;

// 配套的客户端气泡数据处理器包
using FMyReplicationClientHandlerPack = UE::Mass::Replication::TClientBubbleDataHandlerPack<
    UE::Mass::Replication::TClientBubbleFragmentHandler<FMyReplicatedData, FHealthFragment>
>;

// 一个具体的复制器，负责协调多个处理器包
UCLASS()
class UMyMinimalReplicator : public UMassReplicatorBase
{
    GENERATED_BODY()
public:
    virtual void AddRequirements(FMassEntityQuery& EntityQuery) override;
    virtual void ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext) override;

private:
    FMyReplicationServerHandlerPack ServerHandlerPack;
    // 注意：客户端气泡处理器包通常与 TClientBubbleHandlerBase 的子类配合使用，而不是在这里直接持有
};
```

**MyMinimalReplicator.cpp**
```cpp
#include "MyMinimalReplicator.h"
#include "MassClientBubbleHandler.h"

void UMyMinimalReplicator::AddRequirements(FMassEntityQuery& EntityQuery)
{
    ServerHandlerPack.AddRequirements(EntityQuery);
    // 添加其他必要 Fragment...
}

void UMyMinimalReplicator::ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext)
{
    // 使用父类提供的模板函数来执行复制逻辑
    CalculateClientReplication<FMassFastArrayItemBase>(
        Context, ReplicationContext,
        // CacheViews 回调
        [&](FMassExecutionContext& Ctx) {
            ServerHandlerPack.CacheFragmentViews(Ctx);
        },
        // AddEntity 回调
        [&](FMassExecutionContext& Ctx, int32 EntityIndex, FReplicatedAgentBase& ReplicatedAgent, FMassClientHandle Handle) -> FMassReplicatedAgentHandle
        {
            // 此处应调用对应客户端气泡处理器的 AddAgent
            // 简化示意：实际需要从 ReplicationContext 获取 BubbleInfo 并操作其内部的 TClientBubbleHandlerBase
            // FMassReplicatedAgentHandle AgentHandle = ...;
            // ServerHandlerPack.AddEntity(EntityIndex, static_cast<FMyReplicatedData&>(ReplicatedAgent));
            // return AgentHandle;
            return FMassReplicatedAgentHandle(); // 占位
        },
        // ModifyEntity 回调
        [&](FMassExecutionContext& Ctx, int32 EntityIndex, EMassLOD::Type LOD, double Time, FMassReplicatedAgentHandle Handle, FMassClientHandle ClientHandle)
        {
            // 此处应调用对应客户端气泡处理器的 ModifyEntity
            // ServerHandlerPack.ModifyEntity(Handle, EntityIndex, *SomeBubbleHandler);
        },
        // RemoveEntity 回调
        [&](FMassExecutionContext& Ctx, FMassReplicatedAgentHandle Handle, FMassClientHandle ClientHandle)
        {
            // 此处应调用对应客户端气泡处理器的 RemoveAgent
        }
    );
}
```

## 模块依赖

要使用 `MassGameplay` 及其 `MassReplication` 模块，你的项目模块需要在 `Build.cs` 中添加对以下模块的依赖（除了常见的 Core/Engine 模块外）：

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass Entity System 的核心，提供基础的 ECS 架构。 |
| `MassGameplay` | 本插件的主模块，提供游戏逻辑框架。 |
| `MassReplication` | **（当前模块）** 提供大规模实体的网络复制框架。 |
| `MassLOD` | 提供实体的细节层次（LOD）管理和距离计算。 |
| `MassSpawner` | 提供实体生成和销毁的管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `07ab5d30` | Revert earlier change to MassAgentComponent. | 撤销了先前对 MassAgentComponent 的修改。 |
| 2026-05-13 | `751e48da` | [MassRepresentation] Wait for actor readiness before switching off ISM | [MassRepresentation] 在关闭实例化静态网格体（ISM）前等待 Actor 就绪。 |
| 2026-05-13 | `022b39e0` | Fix handling of non-puppet actors in Mass crowds | 修复了 Mass 人群中非傀儡 Actor 的处理问题。 |
| 2026-05-12 | `7c7f835b` | [MassRepresentation] Cluster of pre-existing bugs in `TMassLODCalculator`'s per-viewer LOD path. | [MassRepresentation] 修复了 `TMassLODCalculator` 按查看者LOD路径的一系列已存在缺陷。 |
| 2026-05-12 | `f59bc340` | [Mass representation] Switched two manually calculated `bDoKeepActorExtraFrame` to use the new UE::M... | [Mass representation] 将两个手动计算的 `bDoKeepActorExtraFrame` 切换为使用新的 UE::M... |

### 维护评价

MassGameplay 于 2021 年末创建，是一个相对较新的系统。从 Git 记录看，它仍处于活跃开发中（最近提交在 2026 年 5 月），但主要是 bug 修复和底层优化，而非功能大改。`.uplugin` 中 `IsExperimentalVersion=true` 和 `EnabledByDefault=false` 明确表明它**仍处于实验性阶段**。这意味着 API 可能不稳定，使用它需要承担风险，并准备好应对未来的重大变更。

**综合评价**：该模块功能强大，是 Epic 为解决大规模实体问题提供的官方方案，但使用者需要有较强的 C++ 和 ECS 背景，并接受其“实验性”状态。对于生产项目，建议密切关注官方的更新日志和迁移指南。目前**推荐用于原型开发或对新技术有较强承受能力的项目**，不建议在对稳定性要求极高的项目中毫无准备地直接使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MassGameplay)
- 官方文档：无
- 测试用例：无（在提供的模块信息中未指明独立的测试文件路径，测试可能集成在 `MassGameplayTestSuite` 模块或 Engine 测试中）