# Replication Graph

> The Replication Graph plugin provides a Replication Driver implementation designed for a large number of actors and connections by mainting persistent replicated actor lists in a graph structure.

| 属性 | 值 |
|---|---|
| 分类 | Performance |
| 默认启用 | ❌ No |
| 包含内容 | ❌ No |
| 模块 | ReplicationGraph (Runtime, LoadingPhase=PreDefault) |
| 创建时间 | 2018-05-04 |
| 年龄标签 | 👴 老古董(>5年) |
| 实验性 | ⚠️ IsBetaVersion=true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ReplicationGraph) | |

## 用途

ReplicationGraph 是 UE5 网络复制系统的**可替换后端**（Replication Driver），用于解决传统复制系统在**大量 Actor × 大量连接**场景下的性能瓶颈。

传统复制系统每帧对每个连接遍历所有 Actor 判断相关性（relevancy），时间复杂度约为 O(Actors × Connections)。ReplicationGraph 将 Actor 按类别（空间相关、始终相关、仅 Owner 相关等）组织到**图节点**中，维护持久化的复制列表，多个连接可以**共享**同一节点的计算结果，大幅降低 CPU 开销。

核心设计理念：
- **图节点共享**：空间化节点计算一次，所有连接共享结果
- **帧频率控制**：将 `NetUpdateFrequency` 转换为帧间隔，按帧批量调度
- **FastShared 路径**：对近距离、高更新频率的 Actor 使用轻量级快速复制路径
- **休眠优化**：利用 NetDormancy 跳过无变化 Actor 的复制评估

⚠️ **重要变化**：使用 ReplicationGraph 后，`IsNetRelevantFor()` 和 `GetNetPriority()` 等虚函数**不再被调用**。相关性判断和优先级计算由图节点和关联数据（`FGlobalActorReplicationInfo`、`FConnectionReplicationActorInfo`）接管。

## 使用场景

- 你的游戏有 **100+ 同时在线玩家**且世界中有 **数千个复制 Actor** → 用 ReplicationGraph（如大逃杀、MMO）
- 你需要**自定义空间相关性策略**（如基于网格、基于区域） → 用 ReplicationGraph 的节点系统
- 你只是做一个小规模多人游戏（<32 人） → **不需要**此插件，默认复制系统足够

## 蓝图用法

此插件**没有蓝图接口**。它是纯 C++ 系统，通过 INI 配置文件激活，通过子类化定制。

## C++ 用法

### 启用插件

ReplicationGraph 默认禁用（`EnabledByDefault=false`）。启用方式有两种：

**方式一：使用内置的 BasicReplicationGraph（最简单）**

在 `DefaultEngine.ini` 中添加：

```ini
[/Script/OnlineSubsystemUtils.IpNetDriver]
ReplicationDriverClassName="/Script/ReplicationGraph.BasicReplicationGraph"
```

**方式二：通过代码委托创建（高级）**

```cpp
#include "Engine/ReplicationDriver.h"

UReplicationDriver::CreateReplicationDriverDelegate().BindLambda(
    [](UNetDriver* ForNetDriver, const FURL& URL, UWorld* World) -> UReplicationDriver*
    {
        // 返回你自定义的 UReplicationGraph 子类实例
        return NewObject<UMyReplicationGraph>();
    }
);
```

### 头文件引入

```cpp
#include "ReplicationGraph.h"
#include "ReplicationGraphTypes.h"
#include "BasicReplicationGraph.h"  // 如果要参考或继承 BasicReplicationGraph
```

### 核心架构

ReplicationGraph 的核心是一个由 `UReplicationGraphNode` 组成的树形结构：

```
UReplicationGraph (根)
├── GlobalGraphNodes (全局节点，对所有连接生效)
│   ├── UReplicationGraphNode_GridSpatialization2D  ← 空间相关 Actor
│   │   └── UReplicationGraphNode_GridCell (×N)     ← 每个网格单元
│   │       ├── UReplicationGraphNode_DormancyNode  ← 休眠静态 Actor
│   │       └── UReplicationGraphNode_DynamicSpatialFrequency ← 动态 Actor
│   └── UReplicationGraphNode_ActorList             ← 始终相关 Actor
└── ConnectionGraphNodes (每连接节点)
    ├── UReplicationGraphNode_AlwaysRelevant_ForConnection ← PC + ViewTarget
    └── UReplicationGraphNode_TearOff_ForConnection        ← TearOff Actor
```

### 子类化 UReplicationGraph

子类需要重写以下 4 个关键函数：

```cpp
class UMyReplicationGraph : public UReplicationGraph
{
    GENERATED_BODY()

public:
    // 1. 初始化每个 Actor 类的复制设置（剔除距离、复制频率等）
    virtual void InitGlobalActorClassSettings() override;

    // 2. 创建并注册全局图节点
    virtual void InitGlobalGraphNodes() override;

    // 3. 为每个新连接初始化节点
    virtual void InitConnectionGraphNodes(UNetReplicationGraphConnection* Connection) override;

    // 4. 将 Actor 路由到正确的节点
    virtual void RouteAddNetworkActorToNodes(
        const FNewReplicatedActorInfo& ActorInfo,
        FGlobalActorReplicationInfo& GlobalInfo) override;

    virtual void RouteRemoveNetworkActorToNodes(
        const FNewReplicatedActorInfo& ActorInfo) override;
};
```

### 基本用法：参考 BasicReplicationGraph

以下是 `UBasicReplicationGraph` 的实现逻辑（来自 `Source/Private/BasicReplicationGraph.cpp`）：

**InitGlobalActorClassSettings** — 遍历所有复制 Actor 的 CDO，构建类级别复制信息：

```cpp
void UBasicReplicationGraph::InitGlobalActorClassSettings()
{
    Super::InitGlobalActorClassSettings();

    for (TObjectIterator<UClass> It; It; ++It)
    {
        UClass* Class = *It;
        AActor* ActorCDO = Cast<AActor>(Class->GetDefaultObject());
        if (!ActorCDO || !ActorCDO->GetIsReplicated())
            continue;

        // 跳过 SKEL_ 和 REINST_ 类
        if (Class->GetName().StartsWith(TEXT("SKEL_")) || Class->GetName().StartsWith(TEXT("REINST_")))
            continue;

        FClassReplicationInfo ClassInfo;
        // 将 NetUpdateFrequency 转换为帧周期
        ClassInfo.ReplicationPeriodFrame = GetReplicationPeriodFrameForFrequency(
            ActorCDO->GetNetUpdateFrequency());

        if (ActorCDO->bAlwaysRelevant || ActorCDO->bOnlyRelevantToOwner)
            ClassInfo.SetCullDistanceSquared(0.f);
        else
            ClassInfo.SetCullDistanceSquared(ActorCDO->GetNetCullDistanceSquared());

        GlobalActorReplicationInfoMap.SetClassInfo(Class, ClassInfo);
    }
}
```

**InitGlobalGraphNodes** — 创建全局节点：

```cpp
void UBasicReplicationGraph::InitGlobalGraphNodes()
{
    // 空间化网格节点：CellSize=10000
    GridNode = CreateNewNode<UReplicationGraphNode_GridSpatialization2D>();
    GridNode->CellSize = 10000.f;
    GridNode->SpatialBias = FVector2D(-UE_OLD_WORLD_MAX, -UE_OLD_WORLD_MAX);
    AddGlobalGraphNode(GridNode);

    // 始终相关节点（bAlwaysRelevant=true 的 Actor）
    AlwaysRelevantNode = CreateNewNode<UReplicationGraphNode_ActorList>();
    AddGlobalGraphNode(AlwaysRelevantNode);
}
```

**RouteAddNetworkActorToNodes** — 根据 Actor 属性路由到不同节点：

```cpp
void UBasicReplicationGraph::RouteAddNetworkActorToNodes(
    const FNewReplicatedActorInfo& ActorInfo,
    FGlobalActorReplicationInfo& GlobalInfo)
{
    if (ActorInfo.Actor->bAlwaysRelevant)
    {
        AlwaysRelevantNode->NotifyAddNetworkActor(ActorInfo);
    }
    else if (ActorInfo.Actor->bOnlyRelevantToOwner)
    {
        // 延迟到有连接时再添加
        ActorsWithoutNetConnection.Add(ActorInfo.Actor);
    }
    else
    {
        // 基于休眠状态的空间化：不休眠时当动态 Actor，休眠时当静态 Actor
        GridNode->AddActor_Dormancy(ActorInfo, GlobalInfo);
    }
}
```

### 进阶用法：自定义网格节点

```cpp
void UMyReplicationGraph::InitGlobalGraphNodes()
{
    // 创建空间化节点，限制网格范围
    GridNode = CreateNewNode<UReplicationGraphNode_GridSpatialization2D>();
    GridNode->CellSize = 15000.f;  // 更大的网格单元
    GridNode->SpatialBias = FVector2D(-UE_OLD_WORLD_MAX, -UE_OLD_WORLD_MAX);

    // 可选：限制网格边界到特定区域
    FBox WorldBounds(FVector(-100000, -100000, 0), FVector(100000, 100000, 0));
    GridNode->SetBiasAndGridBounds(WorldBounds);

    // 自定义网格单元创建逻辑
    GridNode->CreateCellNodeOverride = [this](UReplicationGraphNode_GridSpatialization2D* Parent)
        -> UReplicationGraphNode_GridCell*
    {
        auto* Cell = Parent->CreateChildNode<UReplicationGraphNode_GridCell>();
        // 自定义动态节点创建
        Cell->CreateDynamicNodeOverride = [](UReplicationGraphNode_GridCell* CellParent)
            -> UReplicationGraphNode*
        {
            auto* FreqNode = CellParent->CreateChildNode<UReplicationGraphNode_DynamicSpatialFrequency>();
            // 配置频率节点...
            return FreqNode;
        };
        return Cell;
    };

    AddGlobalGraphNode(GridNode);

    // 始终相关节点
    AlwaysRelevantNode = CreateNewNode<UReplicationGraphNode_ActorList>();
    AddGlobalGraphNode(AlwaysRelevantNode);
}
```

### 频率桶节点（负载均衡）

`UReplicationGraphNode_ActorListFrequencyBuckets` 将非空间化 Actor 分成多个桶，每帧只从部分桶中收集 Actor，实现帧间负载均衡：

```cpp
// 修改全局默认设置
UReplicationGraphNode_ActorListFrequencyBuckets::DefaultSettings.NumBuckets = 5;
UReplicationGraphNode_ActorListFrequencyBuckets::DefaultSettings.ListSize = 20;
```

### 调试

```cpp
// 打印所有 Actor 的剔除距离
RepGraph->DebugPrintCullDistances();

// 打印所有 Actor 的剔除距离（含特定连接的信息）
RepGraph->DebugPrintCullDistances(ConnectionManager);
```

控制台变量：
- `net.RepGraph.Verify=1` — 启用 Actor 引用验证（仅非 Shipping 构建）

## Demo 示例

### 最小可运行的自定义 ReplicationGraph

**MyReplicationGraph.h**

```cpp
#pragma once

#include "ReplicationGraph.h"
#include "MyReplicationGraph.generated.h"

UCLASS()
class UMyReplicationGraph : public UReplicationGraph
{
    GENERATED_BODY()

public:
    virtual void InitGlobalActorClassSettings() override;
    virtual void InitGlobalGraphNodes() override;
    virtual void InitConnectionGraphNodes(UNetReplicationGraphConnection* Connection) override;
    virtual void RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo) override;
    virtual void RouteRemoveNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo) override;

protected:
    UPROPERTY()
    TObjectPtr<UReplicationGraphNode_GridSpatialization2D> GridNode;

    UPROPERTY()
    TObjectPtr<UReplicationGraphNode_ActorList> AlwaysRelevantNode;
};
```

**MyReplicationGraph.cpp**

```cpp
#include "MyReplicationGraph.h"

void UMyReplicationGraph::InitGlobalActorClassSettings()
{
    Super::InitGlobalActorClassSettings();
    // 复制 BasicReplicationGraph 的逻辑：遍历 CDO 设置类信息
    // 参考 UBasicReplicationGraph::InitGlobalActorClassSettings
}

void UMyReplicationGraph::InitGlobalGraphNodes()
{
    GridNode = CreateNewNode<UReplicationGraphNode_GridSpatialization2D>();
    GridNode->CellSize = 10000.f;
    GridNode->SpatialBias = FVector2D(-UE_OLD_WORLD_MAX, -UE_OLD_WORLD_MAX);
    AddGlobalGraphNode(GridNode);

    AlwaysRelevantNode = CreateNewNode<UReplicationGraphNode_ActorList>();
    AddGlobalGraphNode(AlwaysRelevantNode);
}

void UMyReplicationGraph::InitConnectionGraphNodes(UNetReplicationGraphConnection* Connection)
{
    Super::InitConnectionGraphNodes(Connection);

    auto* AlwaysRelevant = CreateNewNode<UReplicationGraphNode_AlwaysRelevant_ForConnection>();
    AddConnectionGraphNode(AlwaysRelevant, Connection);
}

void UMyReplicationGraph::RouteAddNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo, FGlobalActorReplicationInfo& GlobalInfo)
{
    if (ActorInfo.Actor->bAlwaysRelevant)
        AlwaysRelevantNode->NotifyAddNetworkActor(ActorInfo);
    else if (ActorInfo.Actor->bOnlyRelevantToOwner)
        ; // 处理 OwnerOnly 逻辑
    else
        GridNode->AddActor_Dormancy(ActorInfo, GlobalInfo);
}

void UMyReplicationGraph::RouteRemoveNetworkActorToNodes(const FNewReplicatedActorInfo& ActorInfo)
{
    if (ActorInfo.Actor->bAlwaysRelevant)
        AlwaysRelevantNode->NotifyRemoveNetworkActor(ActorInfo);
    else if (ActorInfo.Actor->bOnlyRelevantToOwner)
        ; // 处理 OwnerOnly 逻辑
    else
        GridNode->RemoveActor_Dormancy(ActorInfo);
}
```

**YourGame.Build.cs**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "ReplicationGraph"
});
```

**DefaultEngine.ini**

```ini
[/Script/OnlineSubsystemUtils.IpNetDriver]
ReplicationDriverClassName="/Script/YourGame.MyReplicationGraph"
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、容器、日志 |
| `CoreUObject` | UObject 系统、反射 |
| `NetCore` | 网络核心基础设施 |
| `Engine` | UReplicationDriver 基类、UNetDriver、AActor |
| `EngineSettings` | 引擎设置 |
| `PerfCounters` | 性能计数器 |
| `GameplayDebugger` | 可选，调试器支持（条件编译） |

使用者需要在自己的 Build.cs 中依赖 `ReplicationGraph` 模块。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-02 | `5d4f40c8` | 代码清理：修复 `nullptr_t` 不在全局命名空间的用法 |
| 2025-07-12 | `b8bdcd83` | 运行 UnrealCodeFixup 修复 DLL 导出符号 |
| 2025-06-11 | `df9dd35c` | 将部分 `FORCEINLINE` 替换为 `inline` |

以上更新均为**维护性/编译修复**，无功能性变更。

### 维护评价

- **创建时间**：2018 年 5 月，已有 7+ 年历史
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true`，Epic 从未将其标记为正式版
- **默认关闭**：`EnabledByDefault=false`，需要手动启用
- **更新频率**：近期仅有编译修复和代码清理，无功能性更新
- **官方参考**：ShooterGame 示例项目中有 `UShooterReplicationGraph` 的高级实现；Lyra 项目使用了基于 ClassRouting 的方式
- **推荐度**：适合大规模多人游戏，但需注意仍标记为 Beta，生产环境使用需自行充分测试

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ReplicationGraph)
- [UReplicationDriver 基类](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Source/Runtime/Engine/Classes/Engine/ReplicationDriver.h)
- Epic 官方博客文章：[Replication Graph](https://www.unrealengine.com/en-US/tech-blog/replication-graph)（概念介绍）
