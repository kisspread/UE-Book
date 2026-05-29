# ZoneGraph

> Description missing.

| 属性 | 值 |
|---|---|
| 中文名 | 区域图 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ZoneGraph` (Runtime), `ZoneGraphEditor` (Editor), `ZoneGraphTestSuite` (UncookedOnly), `ZoneGraphDebug` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph) | |

## 用途

ZoneGraph 是 UE5 中的一个**实验性运行时 AI 导航与车道系统**。它并非简单的 NavMesh 替代品，而是一个更高级的、用于**模拟复杂交通和移动模式**的框架。

其核心思想是将世界空间划分为**区域（Zone）**，每个区域可以包含多条**车道（Lane）**，这些车道描述了可移动的路径、方向、宽度和属性（标签）。系统支持：
1. **车道连接与拓扑**：自动计算车道间的连接（出入、相邻），形成可导航的图。
2. **高效查询**：基于 BV 树和空间哈希，快速查找最近车道、重叠区域等。
3. **A* 寻路**：在车道网络上进行 A* 算法寻路，支持标签过滤。
4. **可视化调试**：提供丰富的可视化工具，用于查看区域、车道、连接和寻路结果。

它主要用于需要**预定义、结构化移动路径**的场景，例如：车辆交通流、巡逻路线、复杂的 NPC 移动、竞技场中的路径规划等。它比通用的 NavMesh 更精确，但灵活性较低，需要预先在编辑器中绘制区域和车道。

## 使用场景

- **车辆交通系统**：为城市交通模拟定义双向车道、路口、转弯规则。
- **NPC 巡逻路线**：为守卫或巡逻兵定义精确的巡逻路径和区域。
- **竞技场/关卡设计**：在 MOBA 或 RTS 地图中预定义兵线或移动走廊。
- **复杂移动模式**：需要角色遵循特定车道（如滑行、游泳）的场景。
- **AI 群体行为**：引导大量 AI 在指定区域沿特定路径移动。

## 蓝图用法

ZoneGraph 的蓝图 API 主要集中在 `UZoneShapeComponent`（用于绘制形状）和 `UZoneGraphSubsystem`（用于查询）上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetShapeType` | 设置形状类型（样条或多边形） | `UZoneShapeComponent` |
| `SetTags` | 为形状设置区域标签 | `UZoneShapeComponent` |
| `SetReverseLaneProfile` | 设置是否反转车道配置文件 | `UZoneShapeComponent` |
| `SetPolygonRoutingType` | 设置多边形形状的路由类型（如贝塞尔） | `UZoneShapeComponent` |
| `GetShapeType` | 获取形状类型 | `UZoneShapeComponent` |
| `GetTags` | 获取形状的标签 | `UZoneShapeComponent` |
| `FindNearestLane` | 在查询范围内查找最近的车道 | `UZoneGraphSubsystem` |
| `FindOverlappingLanes` | 查找与查询范围重叠的车道 | `UZoneGraphSubsystem` |
| `AdvanceLaneLocation` | 沿车道移动位置 | `UZoneGraphSubsystem` |
| `GetLinkedLanes` | 获取指定车道的所有连接车道 | `UZoneGraphSubsystem` |

### 使用示例（蓝图描述）

1.  **创建车道路径**：
    - 在场景中放置 `AZoneShape` Actor。
    - 在其 `UZoneShapeComponent` 的细节面板中，设置 `ShapeType` 为 `Spline` 或 `Polygon`。
    - 编辑控制点以绘制路径（样条线）或多边形区域。
    - 通过 `LaneProfile` 和 `Tags` 属性配置车道的宽度、方向、标签等。
2.  **运行时查询**：
    - 获取 `UZoneGraphSubsystem` 子系统。
    - 使用 `FindNearestLane` 传入一个包围盒和标签过滤器，查找 AI 附近的合适车道。
    - 获取返回的 `FZoneGraphLaneHandle`。
    - 使用 `AdvanceLaneLocation` 或 `CalculateLocationAlongLane` 来模拟沿车道的移动。
    - 使用 `GetLinkedLanes` 来获取下一段车道，以实现转弯或变道。

## C++ 用法

### 头文件引入

```cpp
#include "ZoneGraphSubsystem.h"
#include "ZoneGraphQuery.h"
#include "ZoneGraphTypes.h"
```

### 基本用法

**来源**: `ZoneGraphSubsystem.h` 和 `ZoneGraphQuery.h`

```cpp
// 获取子系统
UZoneGraphSubsystem* ZoneGraphSubsystem = UWorld::GetSubsystem<UZoneGraphSubsystem>(GetWorld());
if (ZoneGraphSubsystem)
{
    // 查找最近的车道（例如，在 AI 位置附近）
    FBox QueryBounds = FBox(MyAIPosition - FVector(100, 100, 0), MyAIPosition + FVector(100, 100, 0));
    FZoneGraphTagFilter TagFilter; // 可以设置标签过滤器
    FZoneGraphLaneLocation OutLocation;
    float OutDistanceSqr;
    if (ZoneGraphSubsystem->FindNearestLane(QueryBounds, TagFilter, OutLocation, OutDistanceSqr))
    {
        // OutLocation 包含车道句柄和沿车道的距离
        UE_LOG(LogTemp, Log, TEXT("Found lane: Index %d, Distance %f"), OutLocation.LaneHandle.Index, OutLocation.DistanceAlongLane);

        // 沿车道向前移动 50 个单位
        FZoneGraphLaneLocation NewLocation;
        if (ZoneGraphSubsystem->AdvanceLaneLocation(OutLocation, 50.0f, NewLocation))
        {
            // NewLocation 是移动后的新位置
        }
    }
}
```

### 进阶用法

**来源**: 结合 `ZoneGraphQuery.h` 和 `ZoneGraphAStar.h`

```cpp
// 使用底层查询函数进行更精细的操作
if (const FZoneGraphStorage* Storage = ZoneGraphSubsystem->GetZoneGraphStorage(DataHandle))
{
    // 直接使用命名空间下的查询函数
    float LaneLength;
    UE::ZoneGraph::Query::GetLaneLength(*Storage, LaneIndex, LaneLength);

    // 获取车道的所有连接（出入口、相邻）
    TArray<FZoneGraphLinkedLane> LinkedLanes;
    UE::ZoneGraph::Query::GetLinkedLanes(*Storage, LaneIndex, 
        EZoneLaneLinkType::Outgoing | EZoneLaneLinkType::Adjacent, // 包含出入口和相邻
        EZoneLaneLinkFlags::None, // 不特别包含的标志
        EZoneLaneLinkFlags::OppositeDirection, // 排除反向车道
        LinkedLanes);

    // 进行 A* 寻路（需要两个车道位置作为起点和终点）
    FZoneGraphLaneLocation StartLoc, EndLoc;
    // ... 初始化 StartLoc 和 EndLoc ...
    
    FZoneGraphAStarWrapper GraphWrapper(*Storage);
    FZoneGraphAStar AStar(GraphWrapper);
    FZoneGraphPathFilter PathFilter(*Storage, StartLoc, EndLoc);
    TArray<FZoneGraphAStarNode> Path;
    EGraphAStarResult Result = AStar.FindPath(StartLoc.LaneHandle.Index, EndLoc.LaneHandle.Index, PathFilter, Path);
    if (Result == EGraphAStarResult::SearchSuccess)
    {
        // Path 包含了从起点到终点的车道节点序列
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何查询并获取一个车道的位置信息。

**ZoneGraphDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ZoneGraphDemo.generated.h"

UCLASS()
class AZoneGraphDemo : public AActor
{
	GENERATED_BODY()
	
public:	
	AZoneGraphDemo();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;

private:
	// 存储上一帧查找到的车道位置，用于可视化
	struct FZoneGraphLaneLocation CachedLaneLocation;
};
```

**ZoneGraphDemo.cpp**
```cpp
#include "ZoneGraphDemo.h"
#include "ZoneGraphSubsystem.h"
#include "DrawDebugHelpers.h"

AZoneGraphDemo::AZoneGraphDemo()
{
	PrimaryActorTick.bCanEverTick = true;
}

void AZoneGraphDemo::BeginPlay()
{
	Super::BeginPlay();
}

void AZoneGraphDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	UZoneGraphSubsystem* ZoneGraphSubsystem = UWorld::GetSubsystem<UZoneGraphSubsystem>(GetWorld());
	if (!ZoneGraphSubsystem) return;

	// 在 Actor 位置附近查找车道
	FBox QueryBounds = FBox(GetActorLocation() - FVector(200, 200, 50), GetActorLocation() + FVector(200, 200, 50));
	FZoneGraphTagFilter TagFilter; // 空过滤器，接受所有标签
	FZoneGraphLaneLocation OutLocation;
	float OutDistanceSqr;

	if (ZoneGraphSubsystem->FindNearestLane(QueryBounds, TagFilter, OutLocation, OutDistanceSqr))
	{
		CachedLaneLocation = OutLocation;
		// 在编辑器中绘制找到的车道位置
		DrawDebugSphere(GetWorld(), CachedLaneLocation.Position, 25.0f, 12, FColor::Green, false, -1, 0, 2.0f);
		DrawDebugLine(GetWorld(), GetActorLocation(), CachedLaneLocation.Position, FColor::Yellow, false, -1, 0, 2.0f);
	}
}
```

## 模块依赖

从 `Build.cs` 文件分析，`ZoneGraph` 模块依赖了 `EditorFramework` 和 `UnrealEd`。这表明该运行时模块包含了一些仅编辑器可用的功能（如构建器）。在使用时，你的模块可能需要依赖：

| 模块 | 用途 |
|---|---|
| `EditorFramework` | （仅编辑器相关功能） |
| `UnrealEd` | （仅编辑器相关功能） |

**注意**：由于 ZoneGraph 是实验性插件，且其运行时模块（ZoneGraph）包含了编辑器依赖，这在实际打包时可能会带来问题。在你的项目中使用时，请确保正确处理这些依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF。 |
| 2026-04-01 | `58888966` | [MassCore] Move headers to Public/Mass/ subdirectory, strip Mass prefix from filenames | 配合 Mass 框架重构，移动头文件位置并清理命名。 |
| 2026-03-30 | `161605b0` | [Mass] Extract MassCore module from MassEntity | 配合 Mass 框架模块拆分。 |
| 2025-11-21 | `d1de0b8a` | Zone Graph: Add an extra FZoneDrawAnnotator parameter to be able to customize zone graph draw debugs | 增加 FZoneDrawAnnotator 参数，允许自定义区域图的调试绘制。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 重命名配置文件从 Base 到 Default，遵循 UE 新规范。 |

### 维护评价

- **创建时间**：2021年，相对较新。
- **最近更新频率**：近期有更新，但多为框架适配（Mass）和通用改动（日志、配置文件），非核心功能更新。
- **活跃维护**：处于实验性状态，没有积极的功能开发和 bug 修复迹象。
- **已知问题/限制**：
    1.  **实验性**：标记为 `IsExperimentalVersion=true`，API 可能不稳定。
    2.  **默认禁用**：需要在项目设置中手动启用。
    3.  **模块依赖问题**：运行时模块依赖了编辑器模块，这在纯运行时打包时可能引起问题。
    4.  **文档缺失**：官方描述为 “Description missing.”，缺乏官方文档。
- **推荐使用**：**谨慎使用**。适合研究、原型开发或内部项目。不建议在需要长期稳定支持的商业项目中使用。可以将其视为一个高级的、结构化的移动系统参考。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/ZoneGraph/Source/ZoneGraphTestSuite)