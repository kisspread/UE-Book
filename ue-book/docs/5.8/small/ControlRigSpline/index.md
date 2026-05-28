# Control Rig Spline

> Allows creation and use of splines for Control Rig

| 属性 | 值 |
|---|---|
| 中文名 | 样条线控制 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ControlRigSpline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-08-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRigSpline) | |

## 用途

ControlRigSpline 为 Control Rig 动画系统提供了样条线（Spline）的创建与操作能力。它解决的核心问题是：**如何在 Control Rig 的动画蓝图节点图中，基于一系列控制点动态生成并采样一条平滑的曲线路径**。该插件将复杂的样条线数学计算封装成一系列易用的 RigVM 节点，使得动画师和技术美术能够在 Control Rig 编辑器中，通过直观的节点连接来控制如绳索、尾巴、触手、甚至自定义的骨骼链运动路径，而无需编写底层的曲线代码。

## 使用场景

- 你正在制作一条蛇、章鱼触手或长绳索的动画，需要其骨骼链跟随一条动态生成的平滑路径运动。
- 你需要将角色身上的一串骨骼（如头发、飘带）精确地分布到一条自定义的路径曲线上。
- 你在 Control Rig 中想实时调试和预览一条由关键点构成的样条线形状。

## 蓝图用法

此插件主要通过 **Control Rig 节点图** 使用，而非传统的蓝图节点。它提供了一系列 `USTRUCT` 类型的 RigVM 节点，这些节点在 Control Rig 节点库的 **“Splines”** 分类下可用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| **创建样条线** | | |
| `Spline From Points` | 从一组 `FVector` 位置点创建样条线。 | `FRigUnit_ControlRigSplineFromPoints` |
| `Spline From Transforms` | 从一组 `FTransform` 变换创建样条线（包含旋转信息）。 | `FRigUnit_ControlRigSplineFromTransforms` |
| **修改样条线** | | |
| `Set Spline Points` | 更新已有样条线的控制点位置。 | `FRigUnit_SetSplinePoints` |
| `Set Spline Transforms` | 更新已有样条线的控制变换。 | `FRigUnit_SetSplineTransforms` |
| **采样样条线** | | |
| `Position From Spline` | 获取样条线上参数 `U` (0.0-1.0) 对应的位置。 | `FRigUnit_PositionFromControlRigSpline` |
| `Transform From Spline (with UpVector)` | 基于上方向向量和滚转角，获取样条线上参数 `U` 对应的完整变换。 | `FRigUnit_TransformFromControlRigSpline` |
| `Transform From Spline` | 基于主次轴，获取样条线上参数 `U` 对应的完整变换。 | `FRigUnit_TransformFromControlRigSpline2` |
| `Tangent From Spline` | 获取样条线上参数 `U` 对应的切线向量。 | `FRigUnit_TangentFromControlRigSpline` |
| `Get Length Of Spline` | 获取样条线的总长度。 | `FRigUnit_GetLengthControlRigSpline` |
| `Closest Parameter From Spline` | 获取空间点在样条线上最近点的参数 `U`。 | `FRigUnit_ClosestParameterFromControlRigSpline` |
| **拟合操作** | | |
| `Fit Spline Curve on Chain` | 将一条样条线拟合到骨骼链上（根据骨骼位置生成控制点）。 | `FRigUnit_FitSplineCurveToChainItemArray` |
| `Fit Chain on Spline Curve` (Deprecated) | 将骨骼链分布拟合到样条线上（提供旋转控制）。 | `FRigUnit_FitChainToSplineCurve` |
| **调试** | | |
| `Draw Spline` | 在视口中绘制样条线用于调试。 | `FRigUnit_DrawControlRigSpline` |

### 使用示例（节点图描述）

1.  **创建路径动画**：使用 `Spline From Points` 节点，将一组动态变化的位置（例如来自其他骨骼或控制）作为输入，生成一条 `FControlRigSpline`。然后，在每帧中使用 `Position From Spline` 或 `Transform From Spline` 节点，传入一个从 0 到 1 循环变化的 `U` 值（例如基于时间或另一个参数），将输出的位置/变换应用到目标骨骼上。
2.  **修复/调整现有曲线**：先用 `Fit Spline Curve on Chain` 节点，将一个 `FControlRigSpline` 对象根据当前骨骼链的位置重新拟合其控制点。然后可以再对这个样条线进行采样或进一步操作。

## C++ 用法

该插件提供了 `FControlRigSpline` 结构体和相关类型，可在 C++ 中直接使用其底层功能。

### 头文件引入

```cpp
#include “ControlRigSplineTypes.h”
// 如果需要使用具体的 RigUnit 节点，通常在 RigVM 图中通过节点使用，但也可以直接引用
#include “ControlRigSplineUnits.h”
```

### 基本用法

以下示例展示了如何在 C++ 中创建和采样一个 `FControlRigSpline` 对象。

```cpp
// 创建一些控制点
TArray<FVector> ControlPoints;
ControlPoints.Add(FVector(0, 0, 0));
ControlPoints.Add(FVector(100, 0, 50));
ControlPoints.Add(FVector(200, 50, 100));
ControlPoints.Add(FVector(300, 0, 0));

// 创建一个 FControlRigSpline 对象并设置控制点
FControlRigSpline MySpline;
MySpline.SetControlPoints(ControlPoints, ESplineType::Hermite, false, 16, 0.f, 0.f);

// 在样条线上采样位置 (U 从 0.0 到 1.0)
float SampleParam = 0.5f; // 中点
FVector PositionAtMiddle = MySpline.PositionAtParam(SampleParam);

// 采样变换
FTransform TransformAtMiddle = MySpline.TransformAtParam(SampleParam);

// 采样切线
FVector TangentAtMiddle = MySpline.TangentAtParam(SampleParam);

// 获取总长度
float TotalLength = MySpline.LengthAtParam(1.0f);
```

### 进阶用法

可以通过 `FControlRigSplineImpl` 的成员获取更多控制细节。

```cpp
// 假设 MySpline 已经设置好控制点
TSharedPtr<FControlRigSplineImpl> SplineImpl = MySpline.SplineData;
if (SplineImpl)
{
    // 获取去重后的控制点（用于闭合样条线）
    TArray<FVector> CleanControlPoints = SplineImpl->GetControlPointsWithoutDuplicates();
    
    // 获取缓存的采样点数量（由 SamplesPerSegment 决定）
    uint16 NumCachedSamples = SplineImpl->NumSamples();
    
    // 访问累积长度数组（用于更精确的长度映射）
    TArray<float>& AccumulatedLengths = SplineImpl->AccumulatedLenth;
}
```

## Demo 示例

一个简单的 Actor 类，在 Tick 中创建并采样样条线，将结果输出到日志。

```cpp
// MySplineDemoActor.h
#pragma once
#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “ControlRigSplineTypes.h”
#include “MySplineDemoActor.generated.h”

UCLASS()
class AMySplineDemoActor : public AActor
{
    GENERATED_BODY()
public:
    AMySplineDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    FControlRigSpline DemoSpline;
    float CurrentParam;
};
```

```cpp
// MySplineDemoActor.cpp
#include “MySplineDemoActor.h”
#include “ControlRigSplineTypes.h”

AMySplineDemoActor::AMySplineDemoActor()
{
    PrimaryActorTick.bCanEverTick = true;
    CurrentParam = 0.0f;
}

void AMySplineDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个简单的样条线
    TArray<FVector> Points;
    Points.Add(GetActorLocation());
    Points.Add(GetActorLocation() + FVector(100, 0, 0));
    Points.Add(GetActorLocation() + FVector(100, 100, 0));
    Points.Add(GetActorLocation() + FVector(0, 100, 0));
    
    DemoSpline.SetControlPoints(Points, ESplineType::Hermite, false, 16, 0.f, 0.f);
}

void AMySplineDemoActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    CurrentParam += DeltaTime * 0.2f; // 循环移动
    if (CurrentParam > 1.0f) CurrentParam -= 1.0f;

    FVector SampledPos = DemoSpline.PositionAtParam(CurrentParam);
    UE_LOG(LogTemp, Log, TEXT(“Spline Position at U=%f: %s”), CurrentParam, *SampledPos.ToString());
}
```

## 模块依赖

在你的模块 `Build.cs` 文件中，如果需要使用该插件提供的类型和功能（例如直接操作 `FControlRigSpline`），需要添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ControlRig` | Control Rig 核心框架，提供 `FRigUnit` 基类和 RigVM 上下文。 |
| `RigVM` | RigVM 虚拟机，是 Control Rig 节点图执行的底层基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统日志宏更新为新式 `UE_LOGF` 格式。 |
| 2025-11-21 | `53340f1c` | Control Rig: Fix TangentAtParam returns bad value when param is 1 | 修复当参数为 1 时，`TangentAtParam` 返回错误值的问题。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 代码规范化，将析构函数改为默认实现。 |
| 2025-10-14 | `f0ed5774` | Control Rig: Apply strict documentation policy to ... nodes | 为节点应用严格的文档策略，可能涉及添加或改进节点说明。 |
| 2025-06-03 | `8403f5c4` | [Control Rig Spline] added tangent interpolation between spline samples. | 增强功能：在样条线采样点之间增加了切线插值，使变换采样更平滑。 |

### 维护评价

- **活跃维护**：插件创建于 2021 年，至今约 4 年。从 git 记录看，最近一次更新在 2026 年，且近一年内有多次功能性更新（如修复切线 bug、增加切线插值、文档策略调整），表明该插件仍在被 Epic Games 活跃维护和改进。
- **实验性状态**：**需特别注意**，`.uplugin` 中明确标记 `IsBetaVersion: true`。这意味着插件的 API 和功能在未来版本中可能发生不兼容的变更。虽然它默认启用并被集成在官方动画流程中，但将其用于生产环境前应充分测试，并关注引擎版本更新日志。
- **已知限制**：历史版本中的 `Fit Chain on Spline Curve` 节点已被标记为 `Deprecated` (在 5.0 版本)，官方推荐使用更新的节点。在使用前应查阅最新文档。
- **推荐使用**：**推荐在开发和学习中使用**，特别是需要进行 Control Rig 样条线动画时。对于项目，鉴于其实验性状态，建议在稳定版本上充分测试，并准备好在引擎大版本更新时进行适配。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/ControlRigSpline)