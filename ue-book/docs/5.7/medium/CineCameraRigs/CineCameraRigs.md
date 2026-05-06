# CineCameraRigs

> Extended camera rigs for cinematic workflow

| 属性 | 值 |
|---|---|
| 中文名 | 影视摄像机装备 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、蓝图） |
| 模块 | `CineCameraRigs` (Runtime), `CineCameraRigsEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs) | |

## 用途

CineCameraRigs 提供了一套面向影视制作流程的扩展摄像机装备。核心组件包括：

- **CineCameraRigRail** —— 沿样条线移动的摄像机轨道，支持光滑的相机运动，并实时控制焦距、光圈、对焦距离等电影参数。
- **CineCameraAttachMount** —— 可附着到目标 Actor 的摄像机安装座，支持位置/旋转延迟（Lag）效果，用于模拟摇臂或斯坦尼康的惯性。
- **CineSplineComponent** —— 扩展自 `USplineComponent`，在样条点处存储额外的电影元数据（焦距、光圈、对焦距离、自定义位置、旋转），支持按位置查询与编辑。

这些组件主要为虚拟制片场景设计，可与 Sequencer（定序器）深度集成，实现镜头参数的时间驱动动画。

## 使用场景

- 在虚拟制片中，导演需要沿预设轨迹平滑移动摄像机，同时调整镜头光学参数。
- 建筑漫游、车辆追逐等需要固定轨道或跟随目标的拍摄场景。
- 需要摄像机运动与镜头参数（焦距、光圈）分别受独立曲线控制的复杂镜头。
- 结合 Sequencer，利用 `AbsolutePositionOnRail` 属性在时间轴上自动关键帧，制作“一镜到底”效果。

## 蓝图用法

所有核心类均标记为 `Blueprintable`，可在蓝图中直接创建与使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AbsolutePositionOnRail` (属性) | 设置/读取沿轨道的绝对位置（基于样条自定义位置） | `ACineCameraRigRail` |
| `SetAbsolutePositionOnRail` | 蓝图设置器，更新轨道位置 | `ACineCameraRigRail` |
| `SetSplineMeshMaterial` | 设置轨道样条线的视觉材质 | `ACineCameraRigRail` |
| `SetDisplaySpeedHeatmap` | 启用/禁用速度热力图可视化 | `ACineCameraRigRail` |
| `SetFocalLengthAtSplinePoint` | 在指定样条点设置焦距 | `UCineSplineComponent` |
| `SetApertureAtSplinePoint` | 在指定样条点设置光圈 | `UCineSplineComponent` |
| `SetFocusDistanceAtSplinePoint` | 在指定样条点设置对焦距离 | `UCineSplineComponent` |
| `SetAbsolutePositionAtSplinePoint` | 在指定样条点设置自定义位置 | `UCineSplineComponent` |
| `SetPointRotationAtSplinePoint` | 在指定样条点设置摄像机旋转 | `UCineSplineComponent` |
| `GetSplineDataAtPosition` | 根据自定义位置获取该点的完整数据（位置、旋转、焦段等） | `UCineSplineComponent` |
| `FindSplineDataAtPosition` | 查找给定自定义位置对应的样条点索引 | `UCineSplineComponent` |
| `GetInputKeyAtPosition` | 根据自定义位置获取样条输入键值 | `UCineSplineComponent` |
| `GetPositionAtInputKey` | 根据样条输入键值获取自定义位置 | `UCineSplineComponent` |
| `TargetActor` (属性) | 摄像机的约束目标 Actor | `ACineCameraAttachMount` |
| `bEnableLocationLag` | 启用/禁用位置延迟 | `ACineCameraAttachMount` |
| `bEnableRotationLag` | 启用/禁用旋转延迟 | `ACineCameraAttachMount` |
| `LocationLagSpeed` | 位置延迟速度 | `ACineCameraAttachMount` |
| `RotationLagSpeed` | 旋转延迟速度 | `ACineCameraAttachMount` |
| `CreateOrUpdateSplineHeatmapTexture` | 从数据数组生成或更新热力图纹理（用于速度可视化） | `UCineCameraRigRailHelpers` |

### 使用示例（蓝图描述）

1. **创建轨道摄像机**  
   - 在关卡中拖入 `BP_CineCameraRigRail`（若存在）或直接放置 `ACineCameraRigRail`。  
   - 将摄像机作为子 Actor 附加到 RigRail 的默认挂载点上。  
   - 选中 RigRail，在细节面板中调整样条形状。  
   - 设置 `bUseAbsolutePosition` 为 true，拖动 `AbsolutePositionOnRail` 滑动条即可沿轨道移动摄像机。  
   - 在样条点编辑器中，选中某样条点，展开 `Camera` 组，可单独设置该点的焦距、光圈、对焦距离。

2. **使用 CineCameraAttachMount 实现跟随与延迟**  
   - 放置 `ACineCameraAttachMount`，在细节面板中指定 `TargetActor`（例如玩家角色）。  
   - 将摄像机作为子 Actor 挂载到 Mount 的默认附着点上。  
   - 启用 `bEnableLocationLag` 和 `bEnableRotationLag`，调整 `LagSpeed` 产生平滑跟随效果。

3. **在 Sequencer 中驱动轨道位置**  
   - 将 RigRail 拖入 Sequencer，找到 `AbsolutePositionOnRail` 属性，添加关键帧。  
   - 在时间轴上调整位置曲线，实现精确的摄像机运动。  
   - 当 Sequencer 驱动该属性时，速度热力图自动禁用，避免编辑器干扰。

## C++ 用法

### 头文件引入

```cpp
#include "CineCameraRigRail.h"
#include "CineCameraAttachMount.h"
#include "CineSplineComponent.h"
#include "CineCameraRigs.h"
```

### 基本用法

#### 创建并配置 CineCameraRigRail

```cpp
// 在 Actor 或 GameMode 中创建轨道
ACineCameraRigRail* RigRail = GetWorld()->SpawnActor<ACineCameraRigRail>(ACineCameraRigRail::StaticClass(), SpawnTransform);
if (RigRail)
{
    UCineSplineComponent* Spline = RigRail->GetCineSplineComponent();
    // 添加样条点并设置电影参数
    Spline->AddSplinePoint(FVector(0, 0, 0), ESplineCoordinateSpace::World);
    Spline->AddSplinePoint(FVector(500, 0, 100), ESplineCoordinateSpace::World);
    Spline->SetFocalLengthAtSplinePoint(0, 35.0f);
    Spline->SetFocalLengthAtSplinePoint(1, 85.0f);

    // 启用绝对位置并设置初始位置
    RigRail->bUseAbsolutePosition = true;
    RigRail->SetAbsolutePositionOnRail(0.5f);
}
```

#### 通过模块静态函数驱动位置

```cpp
// 在任意地方设置 RigRail 的绝对位置（常用于 Sequencer 求值回调）
ACineCameraRigRail* MyRail = ...;
FCineCameraRigsModule::SetAbsolutePositionOnRail(MyRail, NewPosition);
float CurrentPos = FCineCameraRigsModule::GetAbsolutePositionOnRail(MyRail);
```

#### 使用 CineCameraAttachMount 并启用延迟

```cpp
ACineCameraAttachMount* Mount = GetWorld()->SpawnActor<ACineCameraAttachMount>();
if (Mount)
{
    Mount->TargetActor = TargetActor; // TSoftObjectPtr，需先加载
    Mount->SetEnableLocationLag(true);
    Mount->SetLocationLagSpeed(5.0f);
    Mount->SetTransformFilter(FTransformFilter()); // 默认全部开启
}
```

### 进阶用法

#### 动态更新样条点数据并获取所有点

```cpp
UCineSplineComponent* Spline = RigRail->GetCineSplineComponent();
// 查找自定义位置对应的样条点
int32 PointIndex;
if (Spline->FindSplineDataAtPosition(100.0f, PointIndex))
{
    FCineSplinePointData Data = Spline->GetSplineDataAtPosition(100.0f);
    Data.FocalLength = 50.0f;
    Spline->UpdateSplineDataAtIndex(PointIndex, Data);
}
```

#### 结合热力图可视化

```cpp
// 在编辑器或运行时生成速度热力图
UTexture2D* HeatmapTexture = nullptr;
TArray<float> SpeedValues; // 填充速度采样数据
UCineCameraRigRailHelpers::CreateOrUpdateSplineHeatmapTexture(HeatmapTexture, SpeedValues, 0.0f, 2.0f, 10.0f);
// 将纹理赋给 RigRail 的 SplineMeshMIDs
for (auto MID : RigRail->SplineMeshMIDs)
{
    MID->SetTextureParameterValue(FName("Heatmap"), HeatmapTexture);
}
```

## Demo 示例

以下是一个完整的 Actor 类，它在生成时自动创建轨道并驱动摄像机。

**CineCameraRigDemo.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CineCameraRigDemo.generated.h"

class ACineCameraRigRail;
class UCineSplineComponent;

UCLASS()
class ACineCameraRigDemo : public AActor
{
    GENERATED_BODY()

public:
    ACineCameraRigDemo();

    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Demo")
    ACineCameraRigRail* RigRail;

    UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Demo")
    float PlaySpeed = 0.2f;

protected:
    virtual void BeginPlay() override;

private:
    float CurrentPosition;
};
```

**CineCameraRigDemo.cpp**

```cpp
#include "CineCameraRigDemo.h"
#include "CineCameraRigRail.h"
#include "CineSplineComponent.h"
#include "CineCameraRigs.h"

ACineCameraRigDemo::ACineCameraRigDemo()
{
    PrimaryActorTick.bCanEverTick = true;
    RigRail = nullptr;
    CurrentPosition = 0.0f;
}

void ACineCameraRigDemo::BeginPlay()
{
    Super::BeginPlay();

    FTransform SpawnTransform(FVector(0, 0, 0));
    RigRail = GetWorld()->SpawnActor<ACineCameraRigRail>(ACineCameraRigRail::StaticClass(), SpawnTransform);
    if (RigRail)
    {
        UCineSplineComponent* Spline = RigRail->GetCineSplineComponent();
        Spline->ClearSplinePoints();
        Spline->AddSplinePoint(FVector(0, 0, 50), ESplineCoordinateSpace::World, false);
        Spline->AddSplinePoint(FVector(500, 300, 100), ESplineCoordinateSpace::World, false);
        Spline->AddSplinePoint(FVector(1000, 0, 80), ESplineCoordinateSpace::World, false);
        Spline->UpdateSpline();

        // 设定各点的电影参数
        Spline->SetFocalLengthAtSplinePoint(0, 35.0f);
        Spline->SetFocalLengthAtSplinePoint(1, 50.0f);
        Spline->SetFocalLengthAtSplinePoint(2, 85.0f);

        RigRail->bUseAbsolutePosition = true;
        RigRail->bUsePointRotation = true;
        CurrentPosition = 0.0f;
    }
}

void ACineCameraRigDemo::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (RigRail)
    {
        CurrentPosition += DeltaSeconds * PlaySpeed;
        if (CurrentPosition > 3.0f) CurrentPosition = 0.0f;
        FCineCameraRigsModule::SetAbsolutePositionOnRail(RigRail, CurrentPosition);
    }
}
```

## 模块依赖

以下列出 CineCameraRigs 运行时模块的**独特依赖**（常见依赖已省略）：

| 模块 | 用途 |
|---|---|
| `MovieSceneTracks` | 提供基类 `ACameraRig_Rail` 及相关轨道求值逻辑 |
| `Constraints` | 提供 `UTickableParentConstraint`，用于 `CineCameraAttachMount` 的约束系统 |

编辑器模块 `CineCameraRigsEditor` 额外依赖 `SequencerScripting`、`LevelSequenceEditor`、`EditorScriptingUtilities`、`ConcertSyncCore` 等（非运行时必需，列在此处供编辑器扩展参考）。

## 维护状态

### 近期更新

- 2025-10-14 `11f72ed1` Constraints: fix misuse of invalid worlds
- 2025-10-03 `c69ace01` CineCameraRigs: UE_API
- 2025-08-05 `ae82625a` Sequencer: Deprecate old binding API; adjust CineCameraRigs accordingly
- 2025-06-17 `7502b8cd` Splines - Fixed property change notification broadcast
- 2025-06-16 `aeaa4f48` [Backout] - CL43554745

### 维护评价

- **创建时间**：2025-06-16，非常年轻（约 0 年）。
- **近期更新**：最近三个月内有多次功能性更新（UE_API 导出、约束修复、Sequencer 适配），说明团队在持续开发。
- **活跃度**：活跃维护中，每月都有提交。
- **已知问题**：作为 **IsBetaVersion=true** 的实验性插件，API 仍可能变动，未包含在默认启用列表中。
- **推荐度**：对于虚拟制片项目值得尝试，但生产环境中应谨慎评估稳定性和后续升级兼容性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/CineCameraRigs)
- [官方文档]（暂无独立文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/CineCameraRigs/Source/CineCameraRigs/Private/CineCameraRigRail.cpp)（可参考实现细节）