# NavCorridor

> Experimental Navigation Corridor

| 属性 | 值 |
|---|---|
| 中文名 | 导航走廊 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NavCorridor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-06-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NavCorridor) | |

## 用途

NavCorridor 插件为 AI 角色的路径跟随提供了一种**导航走廊（Navigation Corridor）**机制。它解决的核心问题是：AI 沿最短路径移动时，路径过于贴近墙壁和障碍物，导致角色碰撞卡住或外观不自然。这个插件在标准的寻路路径周围构建一个“安全走廊”，定义了可通行的空间范围。通过这个走廊，AI 可以：
1. **路径偏移**：自动将路径远离墙壁，防止穿模或卡死。
2. **平滑转向**：在走廊内执行字符串拉伸（String Pulling）来优化路径，使移动更平滑。
3. **约束视线**：确保 AI 角色的视线或移动方向不会穿出走廊边界。
4. **动态跟随**：追踪在走廊内移动的路径位置，并支持提前预测移动方向。

它本质上是一个**路径后处理**工具，为寻路结果增加了一个可控的安全边界，特别适用于狭窄通道、复杂地形或需要精确移动控制的场景（如动作游戏中的 AI 格斗、潜行游戏中的巡逻 AI）。

## 使用场景

- **潜行游戏**：AI 巡逻时，确保其移动路线紧贴墙壁内侧，既不穿过墙壁，也不会离墙太远而暴露。
- **动作游戏**：敌人 AI 在追击玩家时，在狭窄的走廊或房间中能平滑地绕过障碍物，不会卡在角落。
- **RTS/MOBA**：单位在复杂建筑群中移动，通过走廊机制防止多个单位在拐角处相互卡住。
- **任何需要 AI 在导航网格上移动但需要额外空间控制的场景**。

## 蓝图用法

蓝图中主要通过 `UNavCorridorTestingComponent` 来可视化测试和调试导航走廊。该组件本身就是一个测试和演示工具。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateTests` | 手动触发一次测试，根据当前设置重新计算走廊。 | `UNavCorridorTestingComponent` |

### 属性（编辑器中可配置）

在 `UNavCorridorTestingComponent` 的详情面板中，你可以配置：
- **Nav Agent Properties**：定义测试所用的导航代理尺寸（如半径、高度）。
- **Filter Class**：指定使用的导航查询过滤器。
- **bFindCorridorToGoal**：勾选后，组件会寻找一条从起点到目标 Actor 的路径，并为其构建走廊。
- **bFollowPathOnGoalCorridor**：勾选后，组件会模拟一个点在走廊内的路径上移动。
- **FollowLookAheadDistance**：当点沿路径移动时，提前预测的距离。
- **GoalActor**：目标 Actor。
- **CorridorParams**：构建走廊的参数（宽度、简化设置等）。
- **PathOffset**：路径相对于走廊边界的偏移量。

### 使用示例（蓝图描述）

1.  **创建测试 Actor**：
    - 在场景中放置一个 `ANavCorridorTestingActor`。
    - 它会自动包含一个 `UNavCorridorTestingComponent`。
2.  **设置目标**：
    - 在场景中放置另一个 Actor（如一个 `TargetPoint`）。
    - 在 `UNavCorridorTestingComponent` 的属性中，将 `GoalActor` 指向这个 Actor。
3.  **配置与查看**：
    - 根据需要调整 `CorridorParams` 中的 `Width` 等参数。
    - 运行游戏，组件会自动计算路径和走廊，并在游戏中绘制调试信息（绿色的走廊边界、黄色的偏移后路径）。
4.  **手动测试**：
    - 你也可以通过调用 `UpdateTests` 函数在运行时重新计算走廊（例如，当目标 Actor 移动时）。

## C++ 用法

核心的 C++ API 是 `FNavCorridor` 结构体和 `FNavCorridorParams`。以下示例展示了如何从一条导航路径构建走廊，并在其中移动。

### 头文件引入

```cpp
#include "NavCorridor.h"
```

### 基本用法

首先，你需要一条已经计算好的导航路径 (`FNavigationPath`)。

```cpp
// 假设已有 FNavPathSharedPtr Path（例如从 UNavigationSystemV1 获取）
// 和 FSharedConstNavQueryFilter NavQueryFilter

// 1. 准备走廊参数
FNavCorridorParams CorridorParams;
CorridorParams.SetFromWidth(200.0f); // 根据一个基础宽度设置合理的参数

// 2. 构建走廊
FNavCorridor Corridor;
Corridor.BuildFromPath(*Path, NavQueryFilter, CorridorParams);

if (Corridor.IsValid())
{
    // 3. 获取路径上的位置
    // 例如，从路径起点开始
    FNavCorridorLocation CurrentLocation = Corridor.FindNearestLocationOnPath(Path->GetPathPoints()[0].Location);

    // 4. 沿路径移动
    float MoveSpeed = 100.0f;
    float DeltaTime = 0.016f;
    CurrentLocation = Corridor.AdvancePathLocation(CurrentLocation, MoveSpeed * DeltaTime);

    // 5. 获取当前位置、方向和剩余距离
    FVector CurrentPosition = CurrentLocation.Location;
    FVector ForwardDirection = Corridor.GetPathDirection(CurrentLocation);
    float DistanceToEnd = Corridor.GetDistanceToEndOfPath(CurrentLocation);
}
```

**来源文件**： `Source/NavCorridor/Public/NavCorridor.h`

### 进阶用法：约束视线

在走廊内，你可以约束一个目标点，使其始终在从当前位置可见的范围内。

```cpp
// 假设 Corridor 和 CurrentLocation 已如上定义
FVector SourcePosition = CurrentLocation.Location; // AI 眼睛位置
FVector DesiredTarget = PlayerActor->GetActorLocation(); // 玩家位置

// 获取一个在走廊内且从 SourcePosition 可见的约束后目标点
FVector ConstrainedTarget = Corridor.ConstrainVisibility(CurrentLocation, SourcePosition, DesiredTarget);

// 现在可以让 AI 看向或移动向 ConstrainedTarget，而不用担心穿过墙壁
AIController->SetFocalPoint(ConstrainedTarget);
```

**来源文件**： `Source/NavCorridor/Public/NavCorridor.h`

## Demo 示例

一个最小的 C++ 示例，展示如何构建并使用 NavCorridor。

```cpp
// NavCorridorDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NavCorridor.h"
#include "NavCorridorDemo.generated.h"

UCLASS()
class ANavCorridorDemo : public AActor
{
	GENERATED_BODY()
	
public:
	ANavCorridorDemo();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	// 绘制调试信息
	void DrawDebugCorridor();

private:
	FNavCorridor Corridor;
	FNavCorridorLocation CurrentPathLocation;
	FNavPathSharedPtr Path;
};
```

```cpp
// NavCorridorDemo.cpp
#include "NavCorridorDemo.h"
#include "NavigationSystem.h"
#include "DrawDebugHelpers.h"

ANavCorridorDemo::ANavCorridorDemo()
{
	PrimaryActorTick.bCanEverTick = true;
}

void ANavCorridorDemo::BeginPlay()
{
	Super::BeginPlay();

	UNavigationSystemV1* NavSys = UNavigationSystemV1::GetCurrent(GetWorld());
	if (!NavSys) return;

	// 1. 计算一条简单的路径（这里用直线代替，实际应使用NavSys->FindPathSync）
	TArray<FNavPathPoint> PathPoints;
	PathPoints.Add(FNavPathPoint(GetActorLocation()));
	PathPoints.Add(FNavPathPoint(GetActorLocation() + FVector(1000, 500, 0)));
	Path = MakeShareable(new FNavigationPath(PathPoints, nullptr));

	// 2. 准备参数并构建走廊
	FNavCorridorParams Params;
	Params.SetFromWidth(300.0f); // 走廊宽度300单位

	Corridor.BuildFromPath(*Path, nullptr, Params);

	if (Corridor.IsValid())
	{
		// 3. 初始化当前位置
		CurrentPathLocation = Corridor.FindNearestLocationOnPath(PathPoints[0].Location);
	}
}

void ANavCorridorDemo::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!Corridor.IsValid()) return;

	// 4. 沿走廊移动
	float Speed = 200.0f;
	CurrentPathLocation = Corridor.AdvancePathLocation(CurrentPathLocation, Speed * DeltaTime);

	// 5. 更新Actor位置（简单地设置到路径点，实际应进行平滑插值）
	if (CurrentPathLocation.IsValid())
	{
		SetActorLocation(CurrentPathLocation.Location);
	}

	// 6. 绘制调试信息
	DrawDebugCorridor();
}

void ANavCorridorDemo::DrawDebugCorridor()
{
	if (!Corridor.IsValid()) return;

	// 绘制所有门户（Portals）
	for (int32 i = 0; i < Corridor.Portals.Num(); i++)
	{
		const FNavCorridorPortal& Portal = Corridor.Portals[i];
		DrawDebugLine(GetWorld(), Portal.Left, Portal.Right, FColor::Green, false, -1.0f, 0, 5.0f);

		// 绘制门户中心点（路径点）
		DrawDebugPoint(GetWorld(), Portal.Location, 10.0f, FColor::Yellow, false, -1.0f);
	}

	// 绘制当前位置
	if (CurrentPathLocation.IsValid())
	{
		DrawDebugSphere(GetWorld(), CurrentPathLocation.Location, 30.0f, 8, FColor::Red, false, -1.0f, 0, 3.0f);
	}
}
```

## 模块依赖

从 `NavCorridor.Build.cs` 分析，该插件依赖于 Unreal Engine 的核心导航系统。

| 模块 | 用途 |
|---|---|
| `NavigationSystem` | 提供核心寻路、导航网格（NavMesh）和路径查询功能，是构建走廊的基础。 |
| `AIModule` | 提供 `FNavAgentProperties`、`FNavigationPath`、`FNavPathPoint` 等 AI 和导航相关的数据结构。 |

**注意**：使用者通常不需要在自己的模块 `.Build.cs` 中显式依赖 `NavCorridor`，而是依赖 `AIModule` 和 `NavigationSystem`。`NavCorridor` 模块本身会链接这些依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-03 | `1798f2dc` | Integration: MassNavMeshPathFollowTask: remove overlapping points when building corridor. | 修复在构建走廊时移除重叠点的问题，集成到 Mass AI 系统。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 使用 LyraGame 构建目标进行项目清理和符号导出规范调整。 |
| 2025-04-22 | `50b3bdb6` | Fix issue with nav corridor SimplifyConcavePortals that could break some portals while simplifying t | 修复了简化凹门户（SimplifyConcavePortals）时可能破坏门户结构的 Bug。 |
| 2024-12-12 | `7a8e3e22` | Trivial: Fixing wrong argument type passed to UE_VLOG_SEGMENT_THICK in NavCorridor.cpp. | 修复了调试日志中一个无关紧要的参数类型错误。 |
| 2024-12-12 | `31fcd67d` | NavCorridor: | （提交信息不完整，但日期与上一条相同，可能是一个相关修复）。 |

### 维护评价

NavCorridor 是一个**维护中的实验性插件**。
- **活跃度**：近期（2025年）有实质性功能更新和 Bug 修复，表明 Epic 在持续开发和集成它（例如，集成到 Mass AI 系统）。
- **状态**：`.uplugin` 中明确标记为 `IsExperimentalVersion: true`，并且默认不启用（`EnabledByDefault: false`）。这意味着它仍处于实验阶段，API 可能发生变化，不适合在稳定的生产项目中直接使用。
- **推荐**：如果你的项目需要先进的路径跟随和走廊控制，并且可以接受实验性 API 的变动，可以尝试使用。否则，建议作为学习和研究用途，并在生产项目中谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NavCorridor)
- 官方文档：无（实验性插件通常没有正式文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/NavCorridor/Source/NavCorridor/Tests)（如果存在，通常在模块内的 Tests 目录）