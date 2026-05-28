# Draw Debug Library

> A library of common debug drawing functions.

| 属性 | 值 |
|---|---|
| 中文名 | 调试绘制库 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DrawDebugLibrary` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-28 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DrawDebugLibrary) | |

## 用途

DrawDebugLibrary 是 UE5 原生 `DrawDebug*` 函数族的**高级抽象层**。它解决的核心问题是：原生调试绘制只能输出到视口，而这个插件通过 `FDebugDrawer` 抽象，让同一套绘制调用可以**分发到多种输出目标**：

- **视口（Viewport）**：传统的 3D 调试绘制，使用 PDI（Primitive Draw Interface）
- **Visual Logger**：录制到可视化日志中，可在回放时查看
- **2D Canvas**：屏幕空间的 2D 叠加绘制，支持缓冲输出
- **RigVM 控制台**：在 Control Rig 图表中直接绘制调试信息

此外，插件提供了远超原生 Debug 库的**高级形状绘制**能力：不仅有基本的点、线、箭头，还能绘制椅子、背包、门、公文包等复杂物体，以及完整的图表系统（坐标轴、图例、曲线绘制），非常适合用于动画、AI 行为和复杂空间逻辑的可视化调试。

## 使用场景

- 你在开发 Control Rig 动画，需要在编辑器中可视化骨骼变换和调试数据 → 用 RigVM 调试绘制节点
- 你在调试 AI 寻路或导航，需要绘制路径、朝向箭头、空间标记 → 用 DrawDebugArrow / DrawDebugTriangularBasePyramid
- 你需要录制调试信息到 Visual Logger 以便回放分析 → 创建 VisualLogger DebugDrawer
- 你在开发物理或交互系统，需要可视化门的开合角度、座位区域等 → 用 DrawDebugDoor / DrawDebugChair
- 你需要实时绘制数据曲线（如速度变化、压力曲线）并带有坐标轴和图例 → 用 DrawDebugGraph* 系列函数
- 你需要 2D 屏幕叠加调试信息，如 HUD 上的文本和图表 → 用 CanvasBuffer + 2D 绘制

## 蓝图用法

所有蓝图函数通过 `UDrawDebugLibraryBPLibrary` 静态库暴露，标记为 `DevelopmentOnly`（仅在开发版本中生效）。

### 核心节点

**基础形状绘制**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DrawDebugPoint` | 绘制单个调试点 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugPoints` | 批量绘制多个调试点（优先使用，性能更好） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugLine` | 绘制单条线段 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugLines` | 批量绘制多条线段 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugArrow` | 绘制箭头，支持多种箭头类型和起止端样式 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugSphere` | 绘制球体 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugBox` | 绘制盒体 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugCapsule` | 绘制胶囊体 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugHemisphere` | 绘制半球体 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugCircle` | 绘制圆 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugCone` | 绘制锥体 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugFrustum` | 绘制视锥体 | `UDrawDebugLibraryBPLibrary` |

**高级形状绘制**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DrawDebugChair` | 绘制椅子模型（含座位、靠背、倾斜角） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugDoor` | 绘制门模型（含框架、把手、开合角度、入口箭头） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugBackpack` | 绘制背包模型（含背带） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugBriefcase` | 绘制公文包模型（含提手） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugTriangularBasePyramid` | 绘制三角底金字塔 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugSquareBasePyramid` | 绘制方底金字塔 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugSkeleton` | 绘制骨骼 | `UDrawDebugLibraryBPLibrary` |

**文本与字符串**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DrawDebugString` | 在 3D 空间绘制文本（支持等宽字体、对齐方式） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugStringOnCanvas` | 在 2D Canvas 上绘制文本（支持阴影、描边、自定义字体） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugStringAsCurveOnCanvas` | 将曲线数据渲染为 Canvas 上的文本图表 | `UDrawDebugLibraryBPLibrary` |

**图表系统**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DrawDebugGraph` | 绘制完整的图表（坐标轴 + 曲线 + 图例） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugGraphAxes` | 仅绘制图表坐标轴 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugGraphAxesLabels` | 仅绘制图表坐标轴标签 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugGraphLine` | 在已有坐标轴上绘制一条数据曲线 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugGraphLegend` | 绘制图表图例 | `UDrawDebugLibraryBPLibrary` |

**辅助节点**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeDebugDrawer` | 创建一个标准调试绘制器（输出到视口） | `UDrawDebugLibraryBPLibrary` |
| `MakeVisualLoggerDebugDrawer` | 创建一个 Visual Logger 调试绘制器 | `UDrawDebugLibraryBPLibrary` |
| `MakeMergedDebugDrawer` | 合并多个绘制器（一次调用输出到多个目标） | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugLocalOffset` | 计算局部空间偏移后的世界坐标 | `UDrawDebugLibraryBPLibrary` |
| `DrawDebugOrientUprightToCamera` | 将朝上的物体旋转面向相机 | `UDrawDebugLibraryBPLibrary` |

### 使用示例（蓝图描述）

**示例 1：绘制一条带圆锥箭头的彩色线段**

1. 创建变量 `Drawer`，类型 `FDebugDrawer`，调用 `MakeDebugDrawer` 节点获取绘制器
2. 创建变量 `ArrowSettings`，类型 `FDrawDebugArrowSettings`，设置 `ArrowHeadEndType = Cone`，`bArrowheadOnEnd = true`
3. 创建变量 `LineStyle`，类型 `FDrawDebugLineStyle`，设置 `Color = (1, 0, 0, 1)`（红色），`Thickness = 2.0`
4. 调用 `DrawDebugArrow`，连接 `Drawer`、`StartLocation`、`EndLocation`、`LineStyle`、`ArrowSettings`

**示例 2：绘制带坐标轴和图例的实时数据曲线**

1. 调用 `MakeDebugDrawer` 创建绘制器
2. 调用 `DrawDebugGraph`，传入位置、旋转、X 值数组、Y 值数组、坐标轴长度、各线条样式和图例信息
3. 在 Tick 中持续更新 Y 值数组以实现动态曲线

**示例 3：同时输出到视口和 Visual Logger**

1. 调用 `MakeDebugDrawer` 创建视口绘制器 `Drawer1`
2. 调用 `MakeVisualLoggerDebugDrawer`（设置 Category 和 Verbosity）创建日志绘制器 `Drawer2`
3. 调用 `MakeMergedDebugDrawer`，将 `Drawer1` 和 `Drawer2` 作为输入数组
4. 使用合并后的绘制器进行绘制，结果同时出现在视口和 Visual Logger 中

## C++ 用法

### 头文件引入

```cpp
#include "DrawDebugLibrary.h"
```

### 基本用法

```cpp
// 创建一个标准调试绘制器（输出到视口）
FDebugDrawer Drawer = FDebugDrawer::MakeDebugDrawer(GetWorld());

// 绘制一个红色球体
FDrawDebugLineStyle LineStyle;
LineStyle.Color = FLinearColor::Red;
LineStyle.Thickness = 1.0f;
UDrawDebugLibraryBPLibrary::DrawDebugSphere(
    Drawer,
    FVector(0, 0, 100),  // Location
    50.0f,               // Radius
    16,                  // Segments
    LineStyle,
    true                 // bDepthTest
);

// 绘制一条带虚线样式的线段
FDrawDebugLineStyle DashLineStyle;
DashLineStyle.Color = FLinearColor::Green;
DashLineStyle.LineType = EDrawDebugLineType::Dashed;
DashLineStyle.DashWidth = 5.0f;
DashLineStyle.DashSpacing = 3.0f;
UDrawDebugLibraryBPLibrary::DrawDebugLine(
    Drawer,
    FVector(0, 0, 0),
    FVector(100, 0, 0),
    DashLineStyle,
    true
);
```

### 进阶用法

```cpp
// 1. 创建 Visual Logger 绘制器，同时记录到可视化日志
FDebugDrawer VLDrawer = FDebugDrawer::MakeVisualLoggerDebugDrawer(
    FName("MyCategory"),
    EDrawDebugLogVerbosity::Display
);

// 2. 绘制带箭头的路径指示
FDrawDebugArrowSettings ArrowSettings;
ArrowSettings.bArrowheadOnEnd = true;
ArrowSettings.ArrowHeadEndType = EDrawDebugArrowHead::Cone;
ArrowSettings.ArrowHeadEndSize = 10.0f;
ArrowSettings.bArrowheadOnStart = true;
ArrowSettings.ArrowHeadStartType = EDrawDebugArrowHead::Circle;

FDrawDebugLineStyle ArrowLineStyle;
ArrowLineStyle.Color = FLinearColor::Yellow;
ArrowLineStyle.Thickness = 2.0f;

UDrawDebugLibraryBPLibrary::DrawDebugArrow(
    VLDrawer,
    FVector(0, 0, 0),
    FVector(200, 0, 0),
    ArrowLineStyle,
    ArrowSettings,
    true
);

// 3. 绘制数据图表
TArray<float> XValues, YValues;
for (int32 i = 0; i < 60; i++)
{
    XValues.Add(static_cast<float>(i));
    YValues.Add(FMath::Sin(i * 0.1f) * 50.0f);
}

FDrawDebugGraphAxesSettings AxesSettings;
AxesSettings.Title = TEXT("Sin Wave");
AxesSettings.XaxisLabel = TEXT("Time");
AxesSettings.YaxisLabel = TEXT("Value");

FDrawDebugLineStyle AxesLineStyle;
FDrawDebugLineStyle PlotLineStyle;
PlotLineStyle.Color = FLinearColor::Cyan;

UDrawDebugLibraryBPLibrary::DrawDebugGraph(
    VLDrawer,
    FVector(0, 0, 200),
    FRotator::ZeroRotator,
    XValues,
    YValues,
    0.0f, 60.0f,   // X range
    -60.0f, 60.0f, // Y range
    200.0f,        // X axis length
    100.0f,        // Y axis length
    FDrawDebugLineStyle(),  // Text line style
    AxesLineStyle,
    PlotLineStyle,
    true,
    AxesSettings
);

// 4. 合并多个绘制器
TArray<FDebugDrawer> Drawers;
Drawers.Add(FDebugDrawer::MakeDebugDrawer(GetWorld()));
Drawers.Add(FDebugDrawer::MakeVisualLoggerDebugDrawer());
FDebugDrawer MergedDrawer = FDebugDrawer::MakeMergedDebugDrawer(Drawers);
// 现在使用 MergedDrawer 的绘制调用会同时输出到视口和 Visual Logger
```

## Demo 示例

```cpp
// MyDebugActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DrawDebugLibrary.h"
#include "MyDebugActor.generated.h"

UCLASS()
class AMyDebugActor : public AActor
{
	GENERATED_BODY()

public:
	virtual void Tick(float DeltaTime) override;

private:
	// 历史数据缓冲
	TArray<float> SpeedHistory;
	FDebugDrawer Drawer;
	float TimeAccumulator = 0.0f;
};
```

```cpp
// MyDebugActor.cpp
#include "MyDebugActor.h"
#include "DrawDebugLibraryBPLibrary.h"

void AMyDebugActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 首次 Tick 初始化绘制器
	if (!Drawer.IsValid())
	{
		Drawer = FDebugDrawer::MakeDebugDrawer(GetWorld());
	}

	TimeAccumulator += DeltaTime;

	// 每 0.1 秒采集一次数据
	if (TimeAccumulator >= 0.1f)
	{
		TimeAccumulator = 0.0f;
		float CurrentSpeed = GetVelocity().Size();
		SpeedHistory.Add(CurrentSpeed);
		if (SpeedHistory.Num() > 120)
		{
			SpeedHistory.RemoveAt(0);
		}
	}

	// 绘制运动方向箭头
	FDrawDebugLineStyle ArrowLineStyle;
	ArrowLineStyle.Color = FLinearColor::Green;
	ArrowLineStyle.Thickness = 3.0f;

	FDrawDebugArrowSettings ArrowSettings;
	ArrowSettings.bArrowheadOnEnd = true;
	ArrowSettings.ArrowHeadEndType = EDrawDebugArrowHead::Cone;
	ArrowSettings.ArrowHeadEndSize = 15.0f;

	UDrawDebugLibraryBPLibrary::DrawDebugArrow(
		Drawer,
		GetActorLocation(),
		GetActorLocation() + GetActorForwardVector() * 200.0f,
		ArrowLineStyle,
		ArrowSettings,
		true
	);

	// 绘制速度曲线图表
	if (SpeedHistory.Num() > 1)
	{
		TArray<float> XValues;
		for (int32 i = 0; i < SpeedHistory.Num(); i++)
		{
			XValues.Add(static_cast<float>(i));
		}

		FDrawDebugLineStyle PlotLineStyle;
		PlotLineStyle.Color = FLinearColor::Cyan;
		PlotLineStyle.Thickness = 1.0f;

		FDrawDebugGraphAxesSettings AxesSettings;
		AxesSettings.Title = TEXT("Speed History");

		UDrawDebugLibraryBPLibrary::DrawDebugGraph(
			Drawer,
			GetActorLocation() + FVector(0, 0, 300),
			FRotator(0, GetActorRotation().Yaw, 0),
			XValues,
			SpeedHistory,
			0.0f, 120.0f,
			0.0f, FMath::Max(GetVelocity().Size() * 1.5f, 100.0f),
			200.0f,
			100.0f,
			FDrawDebugLineStyle(),
			FDrawDebugLineStyle(),
			PlotLineStyle,
			true,
			AxesSettings
		);
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `RigVM` | RigVM 函数节点和 Control Rig 集成 |
| `VisualLogger` | Visual Logger 集成，支持将调试输出录制到可视化日志 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `f1493428` | DrawDebugLibrary: Made RigVM draws happen in world space and removed immediate draw option for visual logger | RigVM 绘制改为世界空间，移除 Visual Logger 立即绘制选项 |
| 2026-04-28 | `26260a3d` | DrawDebugLibrary: Minor bug fix for axes drawing | 修复坐标轴绘制的小 bug |
| 2026-04-27 | `0def0a3f` | DrawDebugLibrary: Added function for debug drawing curves as canvas text | 新增将曲线绘制为 Canvas 文本的功能 |
| 2026-04-24 | `be27af59` | DrawDebugLibrary: Added a few more functions | 新增多个调试绘制函数 |
| 2026-04-24 | `847016a0` | DrawDebugLibrary: Added support for 2D screen drawing | 新增 2D 屏幕绘制支持 |

### 维护评价

- **活跃维护中**：最近一次更新距今约 1 个月，2026 年 4 月有一波密集的功能迭代（4 次提交），包括新增 2D 绘制、Canvas 文本曲线等重要功能
- **成长期插件**：创建于 2025 年 8 月，版本号 0.1，仍处于早期快速迭代阶段
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，需要在 Plugins 面板手动启用
- **推荐使用**：对于需要 Visual Logger 集成或多目标调试输出的场景，该插件提供了显著优于原生 DrawDebug 函数的体验。但需注意这是实验性插件，API 可能随版本变化（如最近移除了 immediate draw 选项）
- **注意**：RigVM 节点在 2026-05-14 被改为世界空间坐标，如果你在该日期前已有 Control Rig 图表使用了这些节点，可能需要更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/DrawDebugLibrary)
- [DrawDebugLibrary.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/DrawDebugLibrary/Source/DrawDebugLibrary/Public/DrawDebugLibrary.h)
- [RigUnit_DrawDebugLibrary.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Experimental/DrawDebugLibrary/Source/DrawDebugLibrary/Public/RigUnit_DrawDebugLibrary.h)