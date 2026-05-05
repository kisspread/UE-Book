# Zone Graph

> Description missing.

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphTestSuite` (UncookedOnly), `ZoneGraphDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途

ZoneGraph 是 UE5 的**区域图（Zone Graph）系统**，用于在关卡中标记可行走/可驾驶区域并生成车道网络。它解决的核心问题是：**在编辑器中用可视化的方式定义区域和车道拓扑，运行时自动构建空间索引结构，供 AI 寻路、交通模拟、导航查询等系统使用**。

与 NavMesh 的区别在于，ZoneGraph 专注于**结构化的车道/区域描述**——每条车道有宽度、方向、标签、连接关系等语义信息，适合需要精确车道级路径规划的场景（如城市交通、赛车 AI）。

核心概念：
- **Zone（区域）**：由多边形或样条线定义的空间区域，包含边界点和车道
- **Lane（车道）**：区域内的可行走/可驾驶路径，有宽度、方向、标签
- **Tag（标签）**：最多 32 个自定义标签，用于过滤和分类区域/车道（如"人行道"、"高速公路"）
- **Lane Profile（车道配置模板）**：预定义的多车道模板，在项目设置中配置
- **Shape（形状）**：`UZoneShapeComponent` 定义的编辑器端标记，构建时转换为 Zone/Lane 数据

## 使用场景

- 你在做一个城市交通模拟游戏，需要定义道路网络和车道 → 用 ZoneGraph
- 你的 AI 需要沿车道级路径导航（如赛车 AI、自动驾驶模拟）→ 用 ZoneGraph
- 你需要为 MassEntity（ECS 框架）提供车道查询能力 → ZoneGraph 与 MassEntity 集成
- 你需要可视化调试车道和区域 → 用 ZoneGraphDebug 模块

## 蓝图用法

ZoneGraph 的蓝图接口主要通过 `UZoneShapeComponent` 暴露，用于运行时查询则通过 `UZoneGraphSubsystem`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetShapeType` | 获取形状类型（Spline/Polygon） | `UZoneShapeComponent` |
| `SetShapeType` | 设置形状类型 | `UZoneShapeComponent` |
| `GetTags` | 获取形状的标签掩码 | `UZoneShapeComponent` |
| `SetTags` | 设置形状标签 | `UZoneShapeComponent` |
| `IsLaneProfileReversed` | 车道配置是否反转 | `UZoneShapeComponent` |
| `SetReverseLaneProfile` | 设置车道配置反转状态 | `UZoneShapeComponent` |
| `SetPolygonRoutingType` | 设置多边形路由类型（Bezier/Arcs） | `UZoneShapeComponent` |

### 使用示例（蓝图描述）

**查询最近车道**：
1. 获取 `UZoneGraphSubsystem`（通过 `GetWorldSubsystem` 节点）
2. 创建 `FZoneGraphTagFilter` 设置过滤条件
3. 调用 `FindNearestLane` 传入查询边界和过滤器
4. 返回 `FZoneGraphLaneLocation` 包含位置、方向等信息

**沿车道移动**：
1. 获取当前 `FZoneGraphLaneLocation`
2. 调用 `AdvanceLaneLocation` 传入移动距离
3. 返回新的位置信息

## C++ 用法

### 头文件引入

```cpp
#include "ZoneGraphSubsystem.h"
#include "ZoneGraphTypes.h"
#include "ZoneGraphQuery.h"
#include "ZoneGraphAStar.h"
```

### 基本用法 — 查询最近车道

```cpp
// 获取子系统
UZoneGraphSubsystem* ZoneGraph = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();

// 设置过滤器：只查找包含 Tag 0 的车道
FZoneGraphTagFilter Filter;
Filter.AnyTags = FZoneGraphTagMask(FZoneGraphTag(0));

// 查询最近车道
FZoneGraphLaneLocation LaneLocation;
float DistanceSqr;
FBox QueryBounds = FBox::BuildAABB(ActorLocation, FVector(500.0f));

if (ZoneGraph->FindNearestLane(QueryBounds, Filter, LaneLocation, DistanceSqr))
{
    // 使用 LaneLocation.Position, .Direction, .LaneHandle 等
}
```

*来源：`ZoneGraphSubsystem.h` 公共 API*

### 进阶用法 — A* 寻路

```cpp
#include "ZoneGraphAStar.h"

// 假设已有 StartLocation 和 EndLocation (FZoneGraphLaneLocation)
const FZoneGraphStorage& Storage = ZoneGraphData->GetStorage();

FZoneGraphAStarWrapper Wrapper(Storage);
FZoneGraphAStar AStar(Wrapper);

FZoneGraphTagFilter TagFilter; // 可选过滤
FZoneGraphPathFilter PathFilter(Storage, StartLocation, EndLocation, TagFilter);

TArray<int32> PathLaneIndices;
AStar.FindPath(StartLocation.LaneHandle.Index, EndLocation.LaneHandle.Index, PathFilter, PathLaneIndices);

// PathLaneIndices 包含从起点到终点的车道索引序列
```

*来源：`ZoneGraphAStar.h`*

### 进阶用法 — 低层查询 API

```cpp
#include "ZoneGraphQuery.h"

// 直接操作 Storage，不经过 Subsystem
const FZoneGraphStorage& Storage = ZoneGraphData->GetStorage();

// 获取车道长度
float LaneLength;
UE::ZoneGraph::Query::GetLaneLength(Storage, LaneIndex, LaneLength);

// 沿车道计算位置
FZoneGraphLaneLocation Location;
UE::ZoneGraph::Query::CalculateLocationAlongLane(Storage, LaneHandle, 100.0f, Location);

// 获取连接的车道
TArray<FZoneGraphLinkedLane> LinkedLanes;
UE::ZoneGraph::Query::GetLinkedLanes(Storage, LaneIndex,
    EZoneLaneLinkType::Outgoing, EZoneLaneLinkFlags::None, EZoneLaneLinkFlags::None,
    LinkedLanes);
```

*来源：`ZoneGraphQuery.h`*

## Demo 示例

### 最小查询示例

```cpp
// MyZoneGraphQuery.h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ZoneGraphSubsystem.h"
#include "MyZoneGraphQuery.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyZoneGraphQuery : public UActorComponent
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable)
    bool FindNearestRoad(FVector Location, FVector& OutLanePosition, FVector& OutLaneDirection);

    UFUNCTION(BlueprintCallable)
    bool AdvanceAlongLane(const FZoneGraphLaneLocation& CurrentLocation, float Distance,
                          FZoneGraphLaneLocation& OutNewLocation);
};
```

```cpp
// MyZoneGraphQuery.cpp
#include "MyZoneGraphQuery.h"

bool UMyZoneGraphQuery::FindNearestRoad(FVector Location, FVector& OutLanePosition, FVector& OutLaneDirection)
{
    UZoneGraphSubsystem* ZoneGraph = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();
    if (!ZoneGraph) return false;

    FZoneGraphTagFilter Filter;
    FZoneGraphLaneLocation LaneLocation;
    float DistanceSqr;
    FBox Bounds = FBox::BuildAABB(Location, FVector(1000.0f));

    if (ZoneGraph->FindNearestLane(Bounds, Filter, LaneLocation, DistanceSqr))
    {
        OutLanePosition = LaneLocation.Position;
        OutLaneDirection = LaneLocation.Direction;
        return true;
    }
    return false;
}

bool UMyZoneGraphQuery::AdvanceAlongLane(const FZoneGraphLaneLocation& CurrentLocation, float Distance,
                                          FZoneGraphLaneLocation& OutNewLocation)
{
    UZoneGraphSubsystem* ZoneGraph = GetWorld()->GetSubsystem<UZoneGraphSubsystem>();
    if (!ZoneGraph) return false;
    return ZoneGraph->AdvanceLaneLocation(CurrentLocation, Distance, OutNewLocation);
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "Core", "CoreUObject", "Engine", "ZoneGraph" });
```

## 模块依赖

### ZoneGraph (Runtime)

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | Actor/Component 框架 |
| `RHI` | 渲染硬件接口 |
| `RenderCore` | 渲染核心 |
| `DeveloperSettings` | 项目设置基类 |
| `MassEntity` | ECS 框架集成 |

### ZoneGraphEditor (Editor)

| 模块 | 用途 |
|---|---|
| `ZoneGraph` | 运行时核心 |
| `UnrealEd` | 编辑器框架 |
| `PropertyEditor` | 属性自定义面板 |
| `ComponentVisualizers` | 组件可视化器 |
| `DetailCustomizations` | Detail 面板自定义 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-15 | `93f3073b` | 修复 FZoneGraphTag::None 转 FZoneGraphTagMask 的问题 (UE-302178) |
| 2025-07-14 | `23fd0d7c` | 修复 X+拖拽创建交叉口的崩溃；修复无选中点时 V 快捷键崩溃 |
| 2025-07-10 | `9803c443` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME（批量代码修正） |

### 维护评价

- **活跃维护**：最近 6 个月内有实质性更新（bug 修复、功能改进）
- 创建于 2021 年，已持续维护约 5 年
- 由 Epic 的 Yoan StAmant 负责，定期有更新
- 标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`——需要手动启用
- 虽然标记为实验性，但代码成熟度较高，被 MassEntity 等系统依赖
- **推荐使用**：适合需要结构化车道网络的项目，但需注意实验性标记

## 子模块文档

| 模块 | 类型 | 说明 |
|---|---|---|
| [ZoneGraph](ZoneGraph.md) | Runtime | 核心运行时模块：数据类型、构建器、查询、A*寻路、BV树 |
| [ZoneGraphDebug](ZoneGraphDebug.md) | Runtime | 调试可视化模块：测试 Actor、Gameplay Debugger 集成 |
| [ZoneGraphEditor](ZoneGraphEditor.md) | Editor | 编辑器模块：形状可视化器、属性自定义、样式 |
| [ZoneGraphTestSuite](ZoneGraphTestSuite.md) | UncookedOnly | 自动化测试套件（当前为空壳） |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/ZoneGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite/Private/ZoneGraphTest.cpp)
