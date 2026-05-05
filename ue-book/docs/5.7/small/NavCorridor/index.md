# NavCorridor

> Experimental Navigation Corridor

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 否 |
| 模块 | NavCorridor (Runtime, PreDefault) |
| 创建时间 | 2022-06-22 |
| 年龄标签 | 🆕（约3.9年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NavCorridor) | |

## 用途

NavCorridor plugin 提供了一个**导航走廊（Navigation Corridor）系统**，用于在已有的导航路径周围构建可行走的自由空间表示。

核心思路是：从一条已计算好的导航路径（`FNavigationPath`）出发，沿着路径两侧扩展出一个"走廊"，走廊由一系列**门户（Portal）**组成，相邻门户之间的区域形成**凸扇区（Convex Sector）**。这个走廊定义了路径附近的可行走空间，可以用于：

- **路径平滑**：通过 String Pull（拉绳算法）在走廊内找到最短路径
- **路径偏移**：将路径点推离墙壁，避免角色贴墙行走
- **可见性约束**：限制目标点在走廊可见范围内，防止视线穿过障碍物
- **碰撞检测**：检测线段是否与走廊边界相交

这个 plugin 是 **实验性的**（`IsExperimentalVersion: true`），版本号 0.1，默认不启用。它是一个底层工具，主要被 AI 移动系统（如 MassNavMeshPathFollowTask）使用，而非直接面向最终用户。

## 使用场景

- 你在做 RTS/TD 游戏，需要 AI 角色沿路径行走时自然地偏移避墙 → 用 NavCorridor 的 `OffsetPathLocationsFromWalls`
- 你需要 AI 在走廊内做 string pulling 获得最短平滑路径 → 用 `BuildFromPath` + 内置 String Pull
- 你需要限制 AI 的注视目标在走廊可见范围内 → 用 `ConstrainVisibility`
- 你在开发 Mass Entity AI 系统，需要路径跟随 → MassNavMeshPathFollowTask 内部使用 NavCorridor

## 蓝图用法

NavCorridor 本身是一个纯 C++ 运行时模块，**没有暴露蓝图节点**。`FNavCorridor` 和 `FNavCorridorParams` 是结构体而非 UObject，无法直接在蓝图中使用。

插件附带的 `ANavCorridorTestingActor` 和 `UNavCorridorTestingComponent` 是**编辑器调试工具**，可以在关卡中放置用来可视化走廊效果：

### 调试 Actor 使用

1. 在编辑器中放置 `ANavCorridorTestingActor`
2. 设置 `GoalActor` 指向目标 Actor
3. 调整 `CorridorParams`（Width、ObstacleTaperAngle 等）
4. 勾选 `bFindCorridorToGoal` 查看走廊生成结果
5. 勾选 `bFollowPathOnGoalCorridor` 查看路径跟随和可见性约束

### 调试组件属性

| 属性 | 说明 | 默认值 |
|---|---|---|
| `CorridorParams.Width` | 走廊宽度 | 200 |
| `CorridorParams.ObstacleTaperAngle` | 障碍物边缘锥角（度） | 30 |
| `CorridorParams.SmallSectorThreshold` | 移除小于此宽度的扇区 | 60 |
| `CorridorParams.LargeSectorThreshold` | 跳过大于此长度的简化 | 200 |
| `CorridorParams.SimplifyEdgeThreshold` | 边缘简化阈值 | 20 |
| `PathOffset` | 路径离墙偏移距离 | 40 |
| `bUpdateParametersFromWidth` | 从 Width 自动计算其他参数 | false |

## C++ 用法

### 头文件引入

```cpp
#include "NavCorridor.h"
```

### 核心结构体

NavCorridor 由四个核心结构体组成：

```cpp
// 走廊构建参数
FNavCorridorParams Params;
Params.Width = 200.0f;
Params.PathOffsetFromBoundaries = 0.0f;
Params.ObstacleTaperAngle = 30.0f;

// 或者直接从宽度设置合理默认值
Params.SetFromWidth(200.0f);

// 走廊本体（门户数组）
FNavCorridor Corridor;

// 走廊上的位置（用于路径跟踪）
FNavCorridorLocation Location;

// 单个门户（Left + Right + Location）
FNavCorridorPortal Portal;
```

### 基本用法：构建走廊

以下代码来自 `NavCorridorTestingComponent.cpp` 的 `UpdateTests()` 方法：

```cpp
// 1. 先做路径查找
const FPathFindingQuery PathQuery(this, *NavData, ActorLocation, GoalLocation,
    UNavigationQueryFilter::GetQueryFilter(*NavData, this, FilterClass));
const FSharedConstNavQueryFilter NavQueryFilter = PathQuery.QueryFilter
    ? PathQuery.QueryFilter : NavData->GetDefaultQueryFilter();
FPathFindingResult PathResult = NavSys->FindPathSync(NavAgentProps, PathQuery);

if (PathResult.IsSuccessful())
{
    // 2. 移除重叠点（重要！走廊不支持重叠路径点）
    PathResult.Path->RemoveOverlappingPoints(FNavCorridor::OverlappingPointTolerance);

    // 3. 从路径构建走廊
    FNavCorridor Corridor;
    FNavCorridorParams CorridorParams;
    CorridorParams.SetFromWidth(200.0f);
    Corridor.BuildFromPath(*PathResult.Path, NavQueryFilter, CorridorParams);

    // 4. 将路径点推离墙壁
    Corridor.OffsetPathLocationsFromWalls(40.0f);
}
```

### 进阶用法：路径跟踪与可见性约束

```cpp
// 假设已有一个有效的 Corridor

// 1. 找到当前位置在走廊路径上的最近点
FNavCorridorLocation NearestLocation = Corridor.FindNearestLocationOnPath(ActorLocation);

// 2. 沿路径前进一定距离，得到前瞻点
float LookAheadDistance = 200.0f;
FNavCorridorLocation LookAheadLocation = Corridor.AdvancePathLocation(NearestLocation, LookAheadDistance);

// 3. 用可见性约束限制前瞻点（防止穿过墙壁）
FVector ClampedTarget = Corridor.ConstrainVisibility(
    NearestLocation, ActorLocation, LookAheadLocation.Location);

// 4. 获取路径方向
FVector Direction = Corridor.GetPathDirection(NearestLocation);

// 5. 获取剩余距离
double RemainingDist = Corridor.GetDistanceToEndOfPath(NearestLocation);

// 6. 碰撞检测：检查线段是否穿过走廊边界
double HitT;
bool bHit = Corridor.HitTest(SegmentStart, SegmentEnd, HitT);
```

### 关键 API 说明

| 方法 | 说明 |
|---|---|
| `BuildFromPath(Path, Filter, Params)` | 从导航路径构建走廊。内部会查询导航网格边界、裁剪障碍物边缘、生成门户、简化、string pull |
| `BuildFromPathPoints(Path, Points, BaseIndex, Filter, Params)` | 从路径点数组构建，支持部分路径 |
| `OffsetPathLocationsFromWalls(Offset, bFirst, bLast)` | 将路径位置推离走廊边界，利用前后角落门户的可见性计算安全偏移范围 |
| `FindNearestLocationOnPath(Location)` | 用逆双线性插值找到走廊路径上的最近点，保证内角处不会跳跃 |
| `AdvancePathLocation(Location, Distance)` | 沿路径前进指定距离，超出终点时会外推 |
| `ConstrainVisibility(Location, Source, Target)` | 在走廊内计算可见锥体，将 Target 约束在可见范围内 |
| `HitTest(Start, End, HitT)` | 检测线段与走廊左右边界的交点 |

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "NavCorridor",
    "NavigationSystem",
    "AIModule",
    "Core",
    "CoreUObject",
    "Engine"
});
```

### 完整示例：AI 沿走廊平滑移动

```cpp
// MyAIController.h
#pragma once
#include "AIController.h"
#include "NavCorridor.h"
#include "MyAIController.generated.h"

UCLASS()
class AMyAIController : public AAIController
{
    GENERATED_BODY()
public:
    virtual void Tick(float DeltaTime) override;

private:
    FNavCorridor Corridor;
    FNavCorridorLocation CurrentPathLocation;
    float LookAheadDistance = 200.0f;
};
```

```cpp
// MyAIController.cpp
#include "MyAIController.h"
#include "NavigationSystem.h"
#include "NavMesh/NavMeshPath.h"

void AMyAIController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    APawn* MyPawn = GetPawn();
    if (!MyPawn) return;

    // 如果走廊无效，重新构建
    if (!Corridor.IsValid())
    {
        // 假设已有目标位置
        FVector GoalLocation = FVector::ZeroVector; // 替换为实际目标

        const UNavigationSystemV1* NavSys = FNavigationSystem::GetCurrent<UNavigationSystemV1>(GetWorld());
        if (!NavSys) return;

        const ANavigationData* NavData = NavSys->GetNavDataForProps(
            MyPawn->GetNavAgentPropertiesRef(), MyPawn->GetActorLocation());
        if (!NavData) return;

        FPathFindingResult Result = NavSys->FindPathSync(
            MyPawn->GetNavAgentPropertiesRef(),
            FPathFindingQuery(this, *NavData, MyPawn->GetActorLocation(), GoalLocation));

        if (Result.IsSuccessful())
        {
            Result.Path->RemoveOverlappingPoints(FNavCorridor::OverlappingPointTolerance);

            FNavCorridorParams Params;
            Params.SetFromWidth(MyPawn->GetNavAgentPropertiesRef().AgentRadius * 2.0f);

            Corridor.BuildFromPath(*Result.Path, NavData->GetDefaultQueryFilter(), Params);
            Corridor.OffsetPathLocationsFromWalls(Params.Width * 0.2f);
        }
    }

    if (Corridor.IsValid())
    {
        // 找最近点 + 前瞻 + 可见性约束
        CurrentPathLocation = Corridor.FindNearestLocationOnPath(MyPawn->GetActorLocation());
        FNavCorridorLocation LookAhead = Corridor.AdvancePathLocation(CurrentPathLocation, LookAheadDistance);
        FVector Target = Corridor.ConstrainVisibility(
            CurrentPathLocation, MyPawn->GetActorLocation(), LookAhead.Location);

        // 移动到目标
        MoveToLocation(Target);

        // 检查是否到达终点
        if (Corridor.GetDistanceToEndOfPath(CurrentPathLocation) < 100.0f)
        {
            Corridor.Reset(); // 重置，下次 Tick 重新构建
        }
    }
}
```

## 调试命令

| 控制台变量 | 说明 |
|---|---|
| `ai.nav.EnableNavCorridorVLog 1` | 启用 Visual Logger 记录走廊信息 |
| `ai.nav.bUseSimplifyConcavePortalsFix 0` | 禁用凹门户简化修复（回退旧行为） |

使用 Visual Logger（`EnableVisualLogger` 开关）可以看到：
- 走廊扇区四边形（彩色）
- 障碍物边缘（箭头）
- 走廊门户（橙色/红色）
- 原始路径（灰色）
- String Pulled 路径（粉色）

## 模块依赖

从 `NavCorridor.Build.cs` 提取，你的模块需要依赖以下模块才能使用 NavCorridor：

| 模块 | 用途 |
|---|---|
| `NavigationSystem` | 导航系统核心，路径查找和导航数据 |
| `AIModule` | AI 控制器、导航查询过滤器 |
| `Core` | 基础类型、数学库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 世界、Actor、组件 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-03 | `1798f2dc` | MassNavMeshPathFollowTask: remove overlapping points when building corridor | 集成修复：Mass 实体路径跟随任务在构建走廊前移除重叠路径点，避免构建失败 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types | DLL 导出符号重构，从类型级改为方法/静态变量级 `dllexport`，无功能变化 |
| 2025-04-22 | `50b3bdb6` | Fix issue with nav corridor SimplifyConcavePortals that could break some portals while simplifying the corridor | **Bug 修复**：修复凹门户简化过程中可能破坏门户结构的问题 |

### 维护评价

- **年龄**：创建于 2022 年 6 月，约 4 年历史
- **更新频率**：2025 年 4-6 月有 3 次更新，说明仍在维护中
- **更新内容**：最近更新包括 Bug 修复和 Mass Entity 集成，说明正在与 UE5 新的 Mass 框架对接
- **实验状态**：标记为 `IsExperimentalVersion: true`，`EnabledByDefault: false`，版本号 0.1
- **代码质量**：约 1872 行实现代码，包含完整的 Visual Logger 支持和 CSV 性能分析
- **已知限制**：不支持重叠路径点（需要先调用 `RemoveOverlappingPoints`），走廊可能自重叠

**综合评价**：这是一个成熟的实验性基础设施模块，虽然标记为实验性，但已有近 10 年历史且最近仍在活跃维护（特别是与 Mass Entity 的集成）。适用于需要在导航路径周围精确控制可行走空间的高级 AI 场景。由于是实验性 API，接口可能在未来版本中变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/NavCorridor)
- [NavCorridor.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/NavCorridor/Source/NavCorridor/Public/NavCorridor.h)
- [NavCorridorTestingComponent.cpp](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/NavCorridor/Source/NavCorridor/Private/NavCorridorTestingComponent.cpp)（最佳用法参考）
