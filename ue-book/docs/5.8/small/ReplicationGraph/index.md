# Replication Graph

> The Replication Graph plugin provides a Replication Driver implementation designed for a large number of actors and connections by mainting persistent replicated actor lists in a graph structure.

| 属性 | 值 |
|---|---|
| 中文名 | 复制图 |
| 分类 | Performance |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ReplicationGraph` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-05-04 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ReplicationGraph) | |

## 用途

ReplicationGraph 是一种专为大规模多人游戏（如大逃杀模式）设计的高级网络复制驱动程序。传统的网络复制系统在面对成百上千个 Actor 和玩家连接时，性能开销巨大且难以优化。此插件通过维护一个持久化的 Actor 列表“图”结构，让服务器能够更智能、更高效地决定“将哪个 Actor 复制给哪个连接”。

其核心解决的问题是：**如何在拥有海量网络 Actor 的游戏中，以可预测且高效的方式管理网络复制的相关性与频率，从而极大降低服务器 CPU 开销。**

## 使用场景

*   **大逃杀/大型开放世界游戏**：地图上有大量玩家、载具、道具和动态生成的 Actor，需要精细控制其复制范围和频率。
*   **需要自定义复制逻辑的游戏**：引擎默认的“每个连接独立评估相关性”模型性能不足，需要基于空间网格、Actor 类型、休眠状态等维度进行分层和分组管理。
*   **追求极致服务器性能的多人游戏**：需要利用 `FastPath`（快速路径）、频率桶（Frequency Buckets）等机制，将网络更新均匀分布到不同帧，避免单帧复制压力过大。

## 蓝图用法

ReplicationGraph 主要通过 C++ 配置和扩展，蓝图接口相对有限，主要用于调试和运行时查询。核心节点通常暴露在 `AReplicationGraphDebugActor` 中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ServerStartDebugging` | 开启复制图调试信息收集（服务器 RPC） | `AReplicationGraphDebugActor` |
| `ServerStopDebugging` | 停止调试信息收集 | `AReplicationGraphDebugActor` |
| `ServerPrintAllActorInfo` | 打印所有 Actor 的复制图信息（服务器 RPC） | `AReplicationGraphDebugActor` |
| `ServerSetCullDistanceForClass` | 为指定类设置网络剔除距离（服务器 RPC） | `AReplicationGraphDebugActor` |
| `ServerSetPeriodFrameForClass` | 为指定类设置复制周期帧数（服务器 RPC） | `AReplicationGraphDebugActor` |

### 使用示例（蓝图描述）

1.  **连接调试 Actor**：在服务器上，通过 `SpawnActor` 生成一个 `AReplicationGraphDebugActor`，并将其 `ConnectionManager` 设置为对应的 `UNetReplicationGraphConnection`。
2.  **远程调试**：客户端通过该调试 Actor 的 Server RPC（如 `ServerPrintAllActorInfo`）向服务器发送指令，服务器执行后，可通过 Client RPC（如 `ClientCellInfo`）将结果返回给客户端进行显示。
3.  **配置参数**：在服务器初始化阶段，通过 C++ 调用类似 `SetClassInfo` 的函数来设置 `FClassReplicationInfo`，从而控制各类的复制距离、优先级、周期等，这些参数会在蓝图的 `ServerSet*` 节点中生效。

## C++ 用法

ReplicationGraph 的核心在于通过 C++ 继承和重写关键虚函数来构建自定义的复制图。

### 头文件引入

```cpp
#include "ReplicationGraph.h"
#include "ReplicationGraphTypes.h"
#include "BasicReplicationGraph.h" // 包含一个简单实现参考
```

### 基本用法

创建一个自定义的复制图类，继承自 `UReplicationGraph`。来源文件：`Engine/Plugins/Runtime/ReplicationGraph/Source/ReplicationGraph/Public/BasicReplicationGraph.h`。

```cpp
// MyReplicationGraph.h
#include "ReplicationGraph.h"

UCLASS()
class UMyReplicationGraph : public UReplicationGraph
{
    GENERATED_BODY()

public:
    // 初始化全局的 Actor 类设置（如剔除距离、复制频率）
    virtual void InitGlobalActorClassSettings() override;

    // 初始化全局图节点（如空间网格节点、始终相关节点）
    virtual void InitGlobalGraphNodes() override;

    // 为每个新连接初始化图节点（如为玩家创建相关的节点）
    virtual void InitConnectionGraphNodes(UNetReplicationGraphConnection* RepGraphConnection) override;

    // 将新网络化的 Actor 路由到正确的图节点
    virtual void RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo) override;

    // 从图节点中移除 Actor
    virtual void RouteRemoveNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo) override;
};
```

```cpp
// MyReplicationGraph.cpp
#include "MyReplicationGraph.h"

void UMyReplicationGraph::InitGlobalActorClassSettings()
{
    Super::InitGlobalActorClassSettings();

    // 为特定的 Actor 类配置复制信息
    FClassReplicationInfo PawnReplicationInfo;
    PawnReplicationInfo.SetCullDistanceSquared(100000000.f); // 10000 单位距离平方
    PawnReplicationInfo.ReplicationPeriodFrame = 3; // 每3帧复制一次
    GlobalActorReplicationInfoMap.SetClassInfo(APawn::StaticClass(), PawnReplicationInfo);
}

void UMyReplicationGraph::InitGlobalGraphNodes()
{
    Super::InitGlobalGraphNodes();

    // 创建一个2D空间网格节点，用于根据距离剔除动态 Actor
    GridNode = CreateNode<UReplicationGraphNode_GridSpatialization2D>();
    GridNode->CellSize = 10000.f;
    GridNode->SpatialBias = FVector2D(10000.f, 10000.f);
    AddNode(GridNode);

    // 创建一个始终相关节点
    AlwaysRelevantNode = CreateNode<UReplicationGraphNode_ActorList>();
    AddNode(AlwaysRelevantNode);
}

void UMyReplicationGraph::RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo)
{
    AActor* Actor = ActorInfo.Actor;
    if (Actor->bAlwaysRelevant)
    {
        AlwaysRelevantNode->NotifyAddNetworkActor(ActorInfo);
    }
    else
    {
        GridNode->NotifyAddNetworkActor(ActorInfo);
    }
}
```

### 进阶用法

使用 `UReplicationGraphNode_ActorListFrequencyBuckets` 来平衡复制负载。结合 `FGlobalActorReplicationInfoMap::AddDependentActor` 建立父子复制依赖。来源文件：`Engine/Plugins/Runtime/ReplicationGraph/Source/ReplicationGraph/Public/ReplicationGraph.h` 和 `ReplicationGraphTypes.h`。

```cpp
// 在 InitGlobalGraphNodes 中
UReplicationGraphNode_ActorListFrequencyBuckets* FrequencyBucketsNode = CreateNode<UReplicationGraphNode_ActorListFrequencyBuckets>();
// 配置 3 个桶，每个桶列表大小 16
UReplicationGraphNode_ActorListFrequencyBuckets::FSettings BucketSettings;
BucketSettings.NumBuckets = 3;
BucketSettings.ListSize = 16;
FrequencyBucketsNode->Settings = MakeShared<UReplicationGraphNode_ActorListFrequencyBuckets::FSettings>(BucketSettings);
AddNode(FrequencyBucketsNode);

// 在路由添加 Actor 时，如果希望负载均衡
void UMyReplicationGraph::RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo)
{
    // ... 其他路由逻辑
    if (ShouldUseFrequencyBuckets(ActorInfo.Actor))
    {
        FrequencyBucketsNode->NotifyAddNetworkActor(ActorInfo);
    }
}

// 设置依赖复制：当载具复制时，骑在上面的玩家也一起复制
void UMyReplicationGraph::SetVehicleDynamicsDependencies(AVehicle* Vehicle, APlayerController* Driver)
{
    GlobalActorReplicationInfoMap.AddDependentActor(Vehicle, Driver->GetPawn(), FGlobalActorReplicationInfoMap::EWarnFlag::AllWarnings);
}
```

## Demo 示例

一个最小的可运行复制图实现，仅演示基本结构。

```cpp
// SimpleReplicationGraph.h
#pragma once
#include "ReplicationGraph.h"

class USimpleReplicationGraph : public UReplicationGraph
{
public:
    virtual void InitGlobalGraphNodes() override;
    virtual void InitConnectionGraphNodes(UNetReplicationGraphConnection* RepGraphConnection) override;
    virtual void RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo) override;
    virtual void RouteRemoveNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo) override;

private:
    UPROPERTY()
    TObjectPtr<UReplicationGraphNode_GridSpatialization2D> GridSpatializationNode;

    UPROPERTY()
    TObjectPtr<UReplicationGraphNode_ActorList> AlwaysRelevantNode;
};
```

```cpp
// SimpleReplicationGraph.cpp
#include "SimpleReplicationGraph.h"

void USimpleReplicationGraph::InitGlobalGraphNodes()
{
    GridSpatializationNode = CreateNode<UReplicationGraphNode_GridSpatialization2D>();
    AddNode(GridSpatializationNode);

    AlwaysRelevantNode = CreateNode<UReplicationGraphNode_ActorList>();
    AddNode(AlwaysRelevantNode);
}

void USimpleReplicationGraph::InitConnectionGraphNodes(UNetReplicationGraphConnection* RepGraphConnection)
{
    // 可为每个连接创建专属节点，例如 AlwaysRelevant_ForConnection
}

void USimpleReplicationGraph::RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo)
{
    if (ActorInfo.Actor->bAlwaysRelevant)
    {
        AlwaysRelevantNode->NotifyAddNetworkActor(ActorInfo);
    }
    else
    {
        GridSpatializationNode->NotifyAddNetworkActor(ActorInfo);
    }
}

void USimpleReplicationGraph::RouteRemoveNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo)
{
    // 通常需要根据之前添加的位置进行反向操作，这里简化处理
    AlwaysRelevantNode->NotifyRemoveNetworkActor(ActorInfo, false);
    GridSpatializationNode->NotifyRemoveNetworkActor(ActorInfo, false);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的 `ReplicationGraph.Build.cs` 未显示对独特模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32 位与 64 位格式化说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 宏 |
| 2025-10-22 | `fefc9ac9` | Fix/silence PVS warnings | 修复或静音了静态代码分析（PVS）警告 |
| 2025-09-26 | `2120e69a` | Removed UE_ALLOWSHRINKING_BOOL_DEPRECATED. | 移除了已弃用的 UE_ALLOWSHRINKING_BOOL 宏 |
| 2025-09-02 | `9b75b86d` | PR #13506: Code clean: cleanup usages that expect nullptr_t to be in the global namespace. | 代码清理，移除了对 nullptr_t 全局命名空间的假设 |

### 维护评价

ReplicationGraph 插件自 2018 年随《堡垒之夜》大规模网络需求应运而生，是一个成熟且经过大型生产环境验证的模块。它**仍在持续维护中**，近期的更新（截至 2026 年）以代码清理、编译器警告修复和日志系统迁移为主，表明其作为基础设施已被稳定接受。然而，它**并非活跃开发中的新功能**。该插件默认关闭且标记为实验性（Beta），意味着 Epic 官方认为其配置和使用需要专业知识，且 API 可能随未来版本调整。对于面临大规模网络性能瓶颈的项目，它是一个**强烈推荐研究并使用的强大工具**，但需要投入学习成本进行自定义开发。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ReplicationGraph)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/networking-and-multplayer-in-unreal-engine/) (可查找“Replication Graph”相关章节)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ReplicationGraph) (插件目录内无独立测试，可参考 ShooterGame 示例)