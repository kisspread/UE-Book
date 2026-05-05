# Control Rig Spline

> Allows creation and use of splines for Control Rig

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | true |
| 包含内容 | true |
| 模块 | ControlRigSpline (Runtime) |
| 创建时间 | 2021-08-24 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRigSpline) | |

## 用途

ControlRigSpline 为 Control Rig 动画系统提供样条曲线（Spline）功能。它解决的核心问题是：**在 Control Rig 的 RigVM 图中创建和操作数学样条曲线，并将骨骼链（bone chain）沿曲线分布**。

这个 plugin 存在的原因是 Control Rig 本身不内置样条数学运算。当动画师需要在 Control Rig 中实现"蛇形运动"、"触手摆动"、"尾巴跟随"等效果时，需要一种方式让一组骨骼沿着一条平滑曲线分布——ControlRigSpline 就是为此而生。

它提供了两种样条类型：
- **BSpline**：B 样条，曲线平滑但不一定经过所有控制点（仅首尾通过）
- **Hermite**：埃尔米特样条，曲线经过所有控制点，更直观可控

plugin 还提供了压缩/拉伸限制（Compression/Stretch），可以控制曲线长度变化的约束，适用于需要保持体积感的生物动画。

## 使用场景

- 你在做一个有蛇/龙/触手角色的动画 → 用 ControlRigSpline 创建样条，然后用 Fit Chain on Spline Curve 将骨骼链沿曲线分布
- 你需要在 Control Rig 中动态生成平滑路径 → 用 Spline From Points 从位置数组创建样条
- 你需要让角色的尾巴/绳索跟随某个运动轨迹 → 先用 Fit Spline Curve on Chain 从现有骨骼链创建样条，再用样条驱动其他骨骼
- 你需要在视口中可视化调试样条曲线 → 用 Draw Spline 节点

## 蓝图用法

ControlRigSpline 的所有节点都是 **RigVM 节点**（不是传统蓝图节点），在 Control Rig 蓝图编辑器中使用。节点分为三类：创建样条、查询样条、约束骨骼链。

### 核心节点

**创建样条**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Spline From Points` | 从位置数组创建样条（至少 4 个点） | `FRigUnit_ControlRigSplineFromPoints` |
| `Spline From Transforms` | 从变换数组创建样条（保留旋转信息） | `FRigUnit_ControlRigSplineFromTransforms` |
| `Set Spline Points` | 更新已有样条的控制点 | `FRigUnit_SetSplinePoints` |
| `Set Spline Transforms` | 更新已有样条的控制变换 | `FRigUnit_SetSplineTransforms` |
| `Fit Spline Curve on Chain` | 从骨骼链反向拟合样条 | `FRigUnit_FitSplineCurveToChainItemArray` |

**查询样条**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Position From Spline` | 给定 U 值（0-1），返回样条上的位置 | `FRigUnit_PositionFromControlRigSpline` |
| `Transform From Spline (with UpVector)` | 给定 U 值和上方向量，返回变换 | `FRigUnit_TransformFromControlRigSpline` |
| `Transform From Spline` | 给定 U 值和主/副轴，返回变换 | `FRigUnit_TransformFromControlRigSpline2` |
| `Tangent From Spline` | 给定 U 值，返回切线向量 | `FRigUnit_TangentFromControlRigSpline` |
| `Closest Parameter From Spline` | 给定位置，返回样条上最近的 U 值 | `FRigUnit_ClosestParameterFromControlRigSpline` |
| `Get Length Of Spline` | 返回样条总长度 | `FRigUnit_GetLengthControlRigSpline` |
| `Get Length At Param Of Spline` | 返回从起点到 U 值处的弧长 | `FRigUnit_GetLengthAtParamControlRigSpline` |
| `Parameter At Length Percentage` | 给定长度百分比，返回对应的 U 值 | `FRigUnit_ParameterAtPercentage` |

**约束骨骼链**

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Fit Chain on Spline Curve` | 将骨骼链沿样条分布（推荐版本） | `FRigUnit_FitChainToSplineCurveItemArray` |
| `Spline Constraint` | 将骨骼链约束到样条上（简化版） | `FRigUnit_SplineConstraint` |
| `Draw Spline` | 在视口中绘制样条（调试用） | `FRigUnit_DrawControlRigSpline` |

### 使用示例（RigVM 图描述）

**基本用法：从控制点创建样条并沿曲线分布骨骼**

1. 在 Control Rig 的 Forwards Solve 图中，添加 `Spline From Points` 节点
2. 将控制点数组连接到 `Points` 输入（至少需要 4 个点）
3. 设置 `SplineMode`（Hermite 或 BSpline）、`bClosed`（是否闭合）
4. 添加 `Fit Chain on Spline Curve` 节点
5. 将上一步的 `Spline` 输出连接到此节点的 `Spline` 输入
6. 将 `Items` 设置为目标骨骼链（如从根骨骼到末梢骨骼的一组 bone keys）
7. 设置 `PrimaryAxis` 为骨骼主轴方向（通常是 X 轴 `(1,0,0)`）
8. 运行后，骨骼链将沿样条曲线均匀分布

**查询样条上的位置**

1. 添加 `Position From Spline` 节点
2. 连接已有的 `Spline` 输出
3. 设置 `U` 值（0.0 = 起点，1.0 = 终点）
4. `Position` 输出即为该参数位置的世界坐标

**调试可视化**

1. 添加 `Draw Spline` 节点
2. 连接 `Spline` 输入
3. 设置 `Color`（默认红色）和 `Thickness`
4. `Detail` 控制绘制精度（4-64 个采样点）

## C++ 用法

### 头文件引入

```cpp
#include "ControlRigSplineTypes.h"
#include "ControlRigSplineUnits.h"
```

### 基本用法

**创建和查询样条**（基于 `FControlRigSpline` 的 API）：

```cpp
#include "ControlRigSplineTypes.h"

// 创建样条
FControlRigSpline Spline;

// 定义控制点（至少 4 个）
TArray<FVector> ControlPoints;
ControlPoints.Add(FVector(0, 0, 0));
ControlPoints.Add(FVector(100, 0, 50));
ControlPoints.Add(FVector(200, 0, 100));
ControlPoints.Add(FVector(300, 0, 0));

// 设置控制点，使用 Hermite 样条，不闭合，每段 16 个采样
Spline.SetControlPoints(
    MakeArrayView(ControlPoints),
    ESplineType::Hermite,  // 或 ESplineType::BSpline
    false,                  // bClosed
    16,                     // SamplesPerSegment
    1.0f,                   // Compression（1.0 = 不允许压缩）
    1.0f                    // Stretch（1.0 = 不允许拉伸）
);

// 查询样条上的位置
FVector PosAtMid = Spline.PositionAtParam(0.5f);  // 中点位置
FVector TangentAtMid = Spline.TangentAtParam(0.5f);  // 中点切线
float TotalLength = Spline.LengthAtParam(1.0f);  // 总长度

// 获取变换（含旋转）
FTransform TransformAtQuarter = Spline.TransformAtParam(0.25f);
```

### 进阶用法

**使用 FControlRigSplineImpl 进行更底层的操作**：

```cpp
#include "ControlRigSplineTypes.h"

FControlRigSpline Spline;
TArray<FVector> Points = { /* ... */ };
Spline.SetControlPoints(MakeArrayView(Points), ESplineType::BSpline, false, 16);

// 访问底层实现
TSharedPtr<FControlRigSplineImpl>& Data = Spline.SplineData;
if (Data.IsValid())
{
    // 获取所有采样点
    const TArray<FTransform>& Samples = Data->SamplesArray;
    uint16 NumSamples = Data->NumSamples();

    // 获取控制点（无重复，闭合样条会去掉首尾重复点）
    TArray<FVector> UniquePoints = Data->GetControlPointsWithoutDuplicates();

    // 获取累积长度
    const TArray<float>& Lengths = Data->AccumulatedLenth;

    // 获取曲线阶数
    uint8 Degree = Data->GetDegree();  // BSpline: 3, Hermite: 3
}
```

## Demo 示例

一个完整的最小示例，展示如何在 Actor 中使用 `FControlRigSpline`：

```cpp
// MySplineActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ControlRigSplineTypes.h"
#include "MySplineActor.generated.h"

UCLASS()
class AMySplineActor : public AActor
{
    GENERATED_BODY()

public:
    AMySplineActor();

    UPROPERTY(EditAnywhere, Category = "Spline")
    TArray<FVector> ControlPoints;

    UPROPERTY(EditAnywhere, Category = "Spline")
    ESplineType SplineType = ESplineType::Hermite;

    UPROPERTY(EditAnywhere, Category = "Spline")
    bool bClosed = false;

    UPROPERTY(VisibleAnywhere, Category = "Spline")
    float SplineLength = 0.f;

    virtual void OnConstruction(const FTransform& Transform) override;
    virtual void Tick(float DeltaTime) override;

private:
    FControlRigSpline Spline;
};
```

```cpp
// MySplineActor.cpp
#include "MySplineActor.h"
#include "DrawDebugHelpers.h"

AMySplineActor::AMySplineActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 默认控制点
    ControlPoints.Add(FVector(0, 0, 0));
    ControlPoints.Add(FVector(100, 0, 50));
    ControlPoints.Add(FVector(200, 100, 100));
    ControlPoints.Add(FVector(300, 0, 0));
}

void AMySplineActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);

    if (ControlPoints.Num() >= 4)
    {
        Spline.SetControlPoints(
            MakeArrayView(ControlPoints),
            SplineType,
            bClosed,
            16
        );
        SplineLength = Spline.LengthAtParam(1.0f);
    }
}

void AMySplineActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!Spline.SplineData.IsValid()) return;

    // 绘制样条
    const int32 NumSteps = 32;
    for (int32 i = 0; i < NumSteps; ++i)
    {
        float U0 = float(i) / NumSteps;
        float U1 = float(i + 1) / NumSteps;

        FVector P0 = Spline.PositionAtParam(U0);
        FVector P1 = Spline.PositionAtParam(U1);

        DrawDebugLine(GetWorld(), P0, P1, FColor::Red, false, -1.f, 0, 2.f);
    }
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "ControlRigSpline"
});
```

## 模块依赖

从 `ControlRigSpline.build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心功能 |
| `RigVM` | 虚拟机，Control Rig 的执行引擎 |
| `ControlRig` | Control Rig 动画系统核心模块 |

另外，plugin 声明了对以下 plugin 的依赖（`.uplugin` 中的 `Plugins` 字段）：

| Plugin | 用途 |
|---|---|
| `ControlRig` | Control Rig 动画系统 |
| `RigVM` | RigVM 虚拟机 |

**注意**：要使用此 plugin，你的模块至少需要依赖 `ControlRig` 和 `ControlRigSpline`。如果你只在 Control Rig 蓝图中使用（不直接在 C++ 中调用），则无需添加 C++ 依赖——只需在项目设置中启用此 plugin 即可。

## 维护状态

### 近期更新

| 日期 | Hash | 提交信息 | 解读 |
|---|---|---|---|
| 2025-06-02 | `8403f5c4` | [Control Rig Spline] added tangent interpolation between spline samples. | **功能更新**：在样条采样点之间添加了切线插值，改善了曲线在采样点之间的平滑度 |
| 2025-04-23 | `6ae57335` | Used UnrealGame build target to find and convert all files to have dllstorage... | 构建系统维护，将导出宏从类型级改为方法/静态变量级，不影响功能 |
| 2024-11-22 | `36771d79` | Updated uplugin descriptor files marked as both Experimental and Beta... | 清理 uplugin 标记，将此 plugin 标记为 Beta（非 Experimental） |

### 维护评价

- **创建时间**：2021 年 8 月，约 4.6 年历史
- **最新更新**：2025 年 6 月有实质性功能更新（切线插值）
- **维护状态**：**活跃维护**。最近 6 个月内有功能性更新
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion: true`，说明 Epic 仍将其视为 Beta 阶段
- **推荐程度**：**推荐使用**。功能完整，持续维护，但注意 Beta 标签意味着 API 可能变化
- **已知限制**：
  - 创建样条至少需要 4 个控制点
  - `FRigUnit_FitChainToSplineCurve` 和 `FRigUnit_FitSplineCurveToChain` 已标记为 `Deprecated = "5.0"`，应使用对应的 `ItemArray` 版本
  - 无独立测试用例（plugin 目录内未找到 Test 文件）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ControlRigSpline)
- [ControlRigSplineTypes.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/ControlRigSpline/Source/ControlRigSpline/Public/ControlRigSplineTypes.h)
- [ControlRigSplineUnits.h](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Animation/ControlRigSpline/Source/ControlRigSpline/Public/ControlRigSplineUnits.h)
- 官方文档：无（`.uplugin` 中 `DocsURL` 为空）
