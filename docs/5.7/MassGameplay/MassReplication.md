# MassGameplay

> Implementation of large-scale agent simulation based on MassEntity（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MassReplication` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-29 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassReplication) | |

## 用途

MassReplication 模块是 MassGameplay 插件的核心网络复制组件，专门用于解决**海量实体（Mass Entity）在多人游戏环境下的高效同步问题**。它基于 MassEntity 框架，通过一系列优化策略（如客户端气泡、LOD、空间网格）来最小化网络带宽和服务器 CPU 开销，使得在 MMO、RTS 或大型开放世界游戏中同步成千上万的 NPC、载具或其他动态实体成为可能。其存在是为了解决传统 Actor 复制模式在面对超大规模实体时性能崩溃的根本问题。

## 使用场景

- 你正在开发一款大型多人在线游戏（MMO），需要同步数千名玩家和 NPC 的位置与状态。
- 你正在制作一款即时战略游戏（RTS），需要同步成百上千个作战单位。
- 你的开放世界游戏中有大量动态生成的、需要网络同步的实体（如野生动物、行人）。
- 你需要为基于 MassEntity 的实体系统添加网络复制功能，并希望获得最佳性能。

## 蓝图用法

MassReplication 模块主要通过 Trait 和 Settings 进行配置，其核心逻辑在 C++ 处理器中运行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Build Template` | 为实体模板添加复制所需的 Fragment 和 Trait | `UMassReplicationTrait` |
| `Get Replication Grid Cell Size` | 获取用于空间查询的复制网格单元格大小（单位：厘米） | `UMassReplicationSettings` |

### 使用示例（蓝图描述）

1.  **配置实体模板**：在创建 `FMassEntityTemplate` 时，添加 `UMassReplicationTrait`。在该 Trait 的细节面板中，可以配置 `FMassReplicationParameters`，例如设置不同 LOD 级别的距离。
2.  **调整全局设置**：在项目设置（Project Settings）中找到 “Mass Replication” 分类，可以调整 `ReplicationGridCellSize`。该值决定了用于快速查找客户端附近实体的空间网格精度，值越小精度越高，但内存和计算开销也越大。

## C++ 用法

### 头文件引入

```cpp
#include "MassReplicationSubsystem.h"
#include "MassReplicationTrait.h"
#include "MassReplicationSettings.h"
```

### 基本用法

**1. 为实体模板添加复制支持**
```cpp
// 来源：MassReplicationTrait.h
void UMassReplicationTrait::BuildTemplate(FMassEntityTemplateBuildContext& BuildContext, const UWorld& World) const
{
    // 添加网络ID片段
    BuildContext.AddFragment<FMassNetworkIDFragment>();
    // 添加复制代理片段
    BuildContext.AddFragment<FMassReplicatedAgentFragment>();
    // 添加查看器信息片段
    BuildContext.AddFragment<FMassReplicationViewerInfoFragment>();
    // 添加LOD片段
    BuildContext.AddFragment<FMassReplicationLODFragment>();
    // 添加共享的复制参数
    BuildContext.AddConstSharedFragment(Params);
}
```

**2. 获取复制子系统**
```cpp
// 来源：MassReplicationSubsystem.h
UMassReplicationSubsystem* ReplicationSubsystem = UWorld::GetSubsystem<UMassReplicationSubsystem>(GetWorld());
if (ReplicationSubsystem)
{
    // 使用子系统功能，例如获取客户端句柄、网络ID等
}
```

### 进阶用法

**自定义复制处理器**
要复制自定义的实体数据，需要继承 `UMassReplicatorBase` 并实现其纯虚函数。
```cpp
// 来源：MassReplicationProcessor.h
class UMyCustomReplicator : public UMassReplicatorBase
{
    GENERATED_BODY()
public:
    // 1. 声明查询需求
    virtual void AddRequirements(FMassEntityQuery& EntityQuery) override
    {
        EntityQuery.AddRequirement<FMassNetworkIDFragment>(EMassFragmentAccess::ReadOnly);
        EntityQuery.AddRequirement<FMassReplicatedAgentFragment>(EMassFragmentAccess::ReadWrite);
        // 添加你的自定义片段需求
        EntityQuery.AddRequirement<FMyCustomDataFragment>(EMassFragmentAccess::ReadOnly);
    }

    // 2. 实现客户端复制逻辑
    virtual void ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext) override
    {
        // 使用模板化的 CalculateClientReplication 函数
        CalculateClientReplication<FMyReplicatedAgentItem>(
            Context,
            ReplicationContext,
            // CacheViews 回调
            [&](FMassExecutionContext& ExecContext) { /* 缓存你的片段视图 */ },
            // AddEntity 回调
            [&](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
            {
                // 当实体首次对某个客户端可见时调用
                // 从实体读取数据，设置到客户端气泡的 Agent 项中
            },
            // ModifyEntity 回调
            [&](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
            {
                // 当实体数据发生变化时调用
                // 更新客户端气泡中对应 Agent 项的数据
            },
            // RemoveEntity 回调
            [&](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
            {
                // 当实体对某个客户端不再可见时调用
                // 从客户端气泡中移除该 Agent 项
            }
        );
    }
};
```

## Demo 示例

一个最小的自定义复制处理器示例。

**MyCustomReplicator.h**
```cpp
#pragma once

#include "MassReplicationProcessor.h"
#include "MyCustomReplicator.generated.h"

// 自定义的复制代理数据结构
USTRUCT()
struct FMyReplicatedAgentItem : public FMassFastArrayItemBase
{
    GENERATED_BODY()

    // 包含需要复制的数据
    FReplicatedAgentPositionYawData PositionYawData;
    // 添加其他需要复制的字段...
};

// 自定义的复制处理器
UCLASS()
class UMyCustomReplicator : public UMassReplicatorBase
{
    GENERATED_BODY()

public:
    virtual void AddRequirements(FMassEntityQuery& EntityQuery) override;
    virtual void ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext) override;
};
```

**MyCustomReplicator.cpp**
```cpp
#include "MyCustomReplicator.h"
#include "MassReplicationTransformHandlers.h"

void UMyCustomReplicator::AddRequirements(FMassEntityQuery& EntityQuery)
{
    EntityQuery.AddRequirement<FMassNetworkIDFragment>(EMassFragmentAccess::ReadOnly);
    EntityQuery.AddRequirement<FMassReplicatedAgentFragment>(EMassFragmentAccess::ReadWrite);
    EntityQuery.AddRequirement<FTransformFragment>(EMassFragmentAccess::ReadOnly); // 假设需要复制变换
}

void UMyCustomReplicator::ProcessClientReplication(FMassExecutionContext& Context, FMassReplicationContext& ReplicationContext)
{
    // 使用基类提供的模板函数进行复制计算
    CalculateClientReplication<FMyReplicatedAgentItem>(
        Context,
        ReplicationContext,
        // CacheViews: 缓存需要读取的片段视图
        [](FMassExecutionContext& ExecContext) {},
        // AddEntity: 当实体对客户端新可见时，初始化气泡中的数据
        [](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
        {
            // 这里通常需要访问实体视图来获取初始数据
            // 例如：FMassEntityView EntityView(EntityManager, Entity);
            // 然后设置到对应的 FMyReplicatedAgentItem 中
        },
        // ModifyEntity: 当实体数据变化时更新气泡
        [](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
        {
            // 更新逻辑
        },
        // RemoveEntity: 当实体对客户端不可见时清理
        [](FMassReplicatedAgentHandle Handle, const FMassEntityHandle& Entity, const FMassNetworkID& NetID, const int32 AgentIdx)
        {
            // 清理逻辑
        }
    );
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 实体框架的核心模块，提供实体管理、处理器等基础功能 |
| `MassLOD` | 提供实体 LOD（细节层次）计算和管理，是复制系统进行距离剔除和优化的基础 |
| `MassSpawner` | 提供实体生成和模板管理功能，复制系统需要与其交互来在客户端生成实体 |
| `MassSmartObjects` | 可能用于将智能对象系统与复制系统集成（根据模块列表推断） |
| `MassCommon` | 提供 Mass 系统通用的类型、片段和工具函数 |

## 维护状态

### 近期更新

```
- 457eba2e5782 PR #13332: Added std::is_trivially_copyable to the CFragment concept.
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- b1980471196e [Mass] Minor MassEntityManager cleanup, including removing some header inclusion
```

### 维护评价

MassReplication 模块创建于 2021 年，是 MassGameplay 插件中相对较新的部分。从 git 历史看，近期的更新主要是代码清理、编译优化和概念完善（如 `std::is_trivially_copyable`），没有重大的功能添加或架构变更。考虑到该插件整体标记为 **实验性（IsExperimentalVersion=true）**，且默认未启用，表明 Epic 可能仍在对其进行内部测试和迭代，尚未将其作为稳定、推荐的生产方案。

**综合评价**：
- **状态**：实验性，维护中但非活跃开发。
- **风险**：API 和功能可能在未来的引擎版本中发生变化。
- **建议**：适用于原型开发、性能研究或对网络同步有极致要求的项目。在生产环境中使用前，需要充分测试并准备应对可能的 API 变更。如果你的项目规模确实需要 Mass 级别的复制，这是一个值得深入研究和跟进的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MassGameplay/Source/MassReplication)
- [官方文档]()（暂无）
- [测试用例]()（暂未在提供的路径中发现独立测试文件）