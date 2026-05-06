# ChaosVehiclesPlugin

> Chaos Vehicle Integration

| 属性 | 值 |
|---|---|
| 中文名 | 混沌车辆插件 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图节点、资源样式） |
| 模块 | `ChaosVehicles` (Runtime), `ChaosVehiclesEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin) | |

## 用途

ChaosVehiclesPlugin 是虚幻引擎 5 中基于 Chaos 物理系统的车辆集成插件。它提供了完整的车辆模拟框架，包括车轮控制、动画蓝图节点和编辑器工具，允许开发者创建物理驱动的载具。该插件替代了旧的 PhysX 车辆系统，利用 Chaos 的刚体、碰撞和约束系统实现更稳定、可扩展的车辆物理。

## 使用场景

- 开发基于物理的载具游戏（赛车、模拟驾驶、载具射击）
- 需要使用混沌物理引擎的强大刚体模拟来提升车辆真实感
- 在动画蓝图中精确控制车轮的旋转、地面碰撞和悬挂效果
- 需要编辑器中快速创建和配置车辆资产

## 蓝图用法

以下节点来自运行时模块（ChaosVehicles）的公开 API，编辑器模块主要提供动画蓝图节点。

### 核心动画节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WheelController` | 控制车轮的旋转和位置，响应车辆物理状态 | `UAnimGraphNode_WheelController` |
| `StageCoachWheelController` | 用于多轮（如马车）的特殊车轮控制器，支持更多车轮 | `UAnimGraphNode_StageCoachWheelController` |

### 使用示例（蓝图描述）

1. **创建车辆蓝图**：新建继承自 `WheeledVehiclePawn`（来自运行时模块）的蓝图，添加 `ChaosVehicleMovementComponent`。
2. **设置车轮网格体**：为每个车轮骨骼指定 `WheelSetups` 属性。
3. **动画蓝图**：创建 `AnimBlueprint`，使用 `WheelController` 节点，将其连接到最终动画融合，即可自动根据车辆物理状态驱动车轮旋转。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosVehicles.h"               // 运行时主模块头
#include "VehicleAnimInstance.h"         // 动画实例基类
#include "AnimNode_WheelController.h"    // 车轮动画节点
```

### 基本用法

创建自定义车辆类，继承 `AWheeledVehiclePawn`，配置车轮和物理参数。

```cpp
// MyVehicle.h
#include "WheeledVehiclePawn.h"
#include "MyVehicle.generated.h"

UCLASS()
class AMYVEHICLE_API AMyVehicle : public AWheeledVehiclePawn
{
    GENERATED_BODY()
public:
    AMyVehicle();
};

// MyVehicle.cpp
#include "MyVehicle.h"
#include "ChaosVehicleMovementComponent.h"

AMyVehicle::AMyVehicle()
{
    // 设置车辆运动组件
    GetVehicleMovementComponent()->EngineSetup.MaxRPM = 6000.0f;
    GetVehicleMovementComponent()->EngineSetup.TorqueCurve.GetRichCurve()->AddKey(0.0f, 400.0f);
    GetVehicleMovementComponent()->EngineSetup.TorqueCurve.GetRichCurve()->AddKey(5000.0f, 400.0f);
    GetVehicleMovementComponent()->EngineSetup.TorqueCurve.GetRichCurve()->AddKey(6000.0f, 0.0f);
}
```

> 来源：`Engine/Plugins/Experimental/ChaosVehiclesPlugin/Source/ChaosVehicles/Private/WheeledVehiclePawn.cpp`

### 进阶用法

在动画蓝图中使用 `FWheelAnimNode` 直接计算车轮动画参数。

```cpp
// 在 AnimInstance 的 NativeUpdateAnimation 中获取车轮状态
void UMyVehicleAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    if (const AMyVehicle* Vehicle = Cast<AMyVehicle>(TryGetPawnOwner()))
    {
        const UChaosVehicleMovementComponent* MoveComp = Vehicle->GetVehicleMovementComponent();
        if (MoveComp)
        {
            // 获取每个车轮的转速和悬挂偏移
            for (int32 i = 0; i < MoveComp->Wheels.Num(); i++)
            {
                float WheelRotationSpeed = MoveComp->Wheels[i]->GetRotationAngle();
                float SuspensionOffset = MoveComp->Wheels[i]->GetSuspensionOffset();
                // 驱动骨骼
            }
        }
    }
}
```

## Demo 示例

以下是一个最小 C++ 车辆类与动画蓝图配合的示例。

### MyVehicle.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "WheeledVehiclePawn.h"
#include "MyVehicle.generated.h"

UCLASS()
class MYVEHICLEMODULE_API AMyVehicle : public AWheeledVehiclePawn
{
    GENERATED_BODY()

public:
    AMyVehicle();
};
```

### MyVehicle.cpp

```cpp
#include "MyVehicle.h"
#include "ChaosVehicleMovementComponent.h"

AMyVehicle::AMyVehicle()
{
    // 设置基本悬挂参数
    for (auto& Wheel : GetVehicleMovementComponent()->WheelSetups)
    {
        Wheel.SuspensionParams.RaiseMultiplier = 1.0f;
        Wheel.BoneName = FName(*FString::Printf(TEXT("Wheel_%d"), Wheel.WheelIndex));
    }
}
```

### MyAnimInstance.h

```cpp
#pragma once

#include "VehicleAnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class MYVEHICLEMODULE_API UMyAnimInstance : public UVehicleAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

    UPROPERTY(BlueprintReadOnly, Category = "Vehicle")
    TArray<float> WheelRotationAngles;

    UPROPERTY(BlueprintReadOnly, Category = "Vehicle")
    TArray<float> SuspensionOffsets;
};
```

### MyAnimInstance.cpp

```cpp
#include "MyAnimInstance.h"
#include "WheeledVehiclePawn.h"
#include "ChaosVehicleMovementComponent.h"

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    if (const AMyVehicle* Vehicle = Cast<AMyVehicle>(TryGetPawnOwner()))
    {
        const UChaosVehicleMovementComponent* MoveComp = Vehicle->GetVehicleMovementComponent();
        if (MoveComp)
        {
            WheelRotationAngles.SetNum(MoveComp->Wheels.Num());
            SuspensionOffsets.SetNum(MoveComp->Wheels.Num());
            for (int32 i = 0; i < MoveComp->Wheels.Num(); i++)
            {
                WheelRotationAngles[i] = MoveComp->Wheels[i]->GetRotationAngle();
                SuspensionOffsets[i] = MoveComp->Wheels[i]->GetSuspensionOffset();
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosVehicles` (Runtime) | 车辆物理核心逻辑，所有车辆组件和动画节点依赖 |
| `Chaos` | 混沌物理引擎的基础刚体、碰撞、约束 |
| `AnimGraphRuntime` | 动画蓝图运行时节点支持 |
| `BlueprintGraph`（编辑器） | 动画节点在蓝图编辑器中的显示 |
| `UnrealEd`（编辑器） | 资源类型注册、编辑器样式 |

**其他常见依赖**（标准 Core/Engine/Slate 等已省略）。

## 维护状态

### 近期更新

- 2025-07-28 `b8b21b7a` 修复部分情况下物理解算器时间被缓存为 32 位浮点导致精度丢失的问题
- 2025-06-09 `87ed9fc8` 抑制 UChaosWheeledVehicleMovementComponent::DrawDebug 中的除零编译器 SA 错误
- 2025-06-09 `4e0b9b90` 修复关闭时崩溃的 Bug
- 2025-06-05 `0500d1c4` 修复车辆缓慢移动时被小台阶卡住的 bug（错误的法线使用）
- 2025-05-22 `39d3ddff` 将日志警告改为低优先级日志

### 维护评价

该插件于 2025 年 5 月创建，目前处于实验性阶段。从近期提交看，Epic 仍在积极修复 bug 和优化性能，无明显弃用迹象。由于是 Chaos 物理系统的重要组件，推荐在支持混沌的项目中使用。注意其尚处实验期，API 可能发生变动，建议持续关注更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin)
- [官方文档](https://docs.unrealengine.com/5.1/en-US/chaos-vehicles-in-unreal-engine/)（通用车辆文档，非插件专页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/ChaosVehiclesPlugin/Tests)（如果存在）