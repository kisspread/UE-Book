# Animation Locomotion Library

> Collection of techniques for driving locomotion animations

| 属性 | 值 |
|---|---|
| 中文名 | 动画移动库 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画资产、曲线数据） |
| 模块 | `AnimationLocomotionLibraryRuntime` (Runtime), `AnimationLocomotionLibraryEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-09-17 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary) | |

## 用途

这个插件解决的是角色动画与实际移动不匹配导致的**脚部滑步**问题。传统做法是动画按固定时间线播放，但角色实际移动速度与动画中根骨骼的速度往往不一致，导致脚在地上滑动。

Animation Locomotion Library 提供了一套**基于距离匹配（Distance Matching）**的技术方案：

1. **距离曲线驱动**：动画资产附带一条距离曲线（Distance Curve），描述根骨骼在每一帧实际走了多远。播放时根据角色实际移动距离来推进动画时间，而非按时间线推进。
2. **停止/转向预测**：精确预测角色停止（Stop）和转向（Pivot）的位置，用于在距离曲线上找到最匹配的动画帧，实现无滑步的停止动画。
3. **播放速率匹配**：循环动画（走、跑）通过调整播放速率来匹配实际移动速度。
4. **原地转向偏移**：通过应用旋转偏移避免角色胶囊体旋转时带动全身旋转，配合原地转向动画进行补偿。

该插件是 Lyra 示例项目移动动画系统的基石。

## 使用场景

- 你正在制作第三人称角色 → 用距离匹配消除走路/跑步/停止动画的脚部滑步
- 角色需要根据速度动态切换播放速率 → 用 `SetPlayrateToMatchSpeed`
- 需要精确的停止动画，脚必须踩在正确的地面上 → 用 `PredictGroundMovementStopLocation` + `DistanceMatchToTarget`
- 角色频繁转向，需要原地转向补偿 → 用 Turn in Place 功能
- 动画需要基于距离曲线而非时间线推进 → 用 `AdvanceTimeByDistanceMatching`

## 蓝图用法

所有核心节点都是 **蓝图线程安全**（`BlueprintThreadSafe`）的，可以直接在动画蓝图的 AnimGraph 中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AdvanceTimeByDistanceMatching` | 按照角色实际移动距离推进序列评估器，而非按时间推进。需要动画上有距离曲线 | `UAnimDistanceMatchingLibrary` |
| `DistanceMatchToTarget` | 将序列评估器设置到动画中距离曲线与剩余距离匹配的帧，常用于停止动画 | `UAnimDistanceMatchingLibrary` |
| `SetPlayrateToMatchSpeed` | 调整序列播放器的播放速率，使动画速度匹配角色实际移动速度 | `UAnimDistanceMatchingLibrary` |
| `PredictGroundMovementStopLocation` | 根据当前速度和移动组件参数预测角色停止位置（角色本地空间） | `UAnimCharacterMovementLibrary` |
| `PredictGroundMovementPivotLocation` | 根据当前加速度和速度预测角色转向枢轴位置（角色本地空间） | `UAnimCharacterMovementLibrary` |

### 使用示例（蓝图描述）

**实现无滑步停止动画：**

1. 在动画蓝图的 Update 事件中，每帧获取角色的当前速度向量
2. 调用 `PredictGroundMovementStopLocation`，传入 `Velocity`、`BrakingFriction`、`GroundFriction` 等参数（这些参数通常通过 Property Access 系统从移动组件获取），得到停止距离
3. 将该距离传入 `DistanceMatchToTarget`，连同停止动画的序列评估器引用和距离曲线名称
4. 序列评估器会自动跳到动画中距离曲线值与剩余停止距离最接近的帧
5. 随着角色减速接近停止点，每帧更新，动画自然过渡到完全停止的姿势

**实现基于距离的循环播放：**

1. 在状态转换完成时，将序列评估器初始化
2. 每帧调用 `AdvanceTimeByDistanceMatching`，传入 `DistanceTraveled`（上一帧到这一帧的实际移动距离）和距离曲线名称
3. 设置 `PlayRateClamp`（如 `(0.75, 1.25)`）防止播放速率过低或过高
4. 如果播放速率被钳制，剩余的速度差异可以用 Stride Warping 等技术补偿

**实现速度匹配的循环动画：**

1. 获取角色当前移动速度（`Speed`）
2. 调用 `SetPlayrateToMatchSpeed`，传入序列播放器引用和速度值
3. 动画播放速率会自动调整，走路快时播放快，走路慢时播放慢

## C++ 用法

### 头文件引入

```cpp
#include "AnimDistanceMatchingLibrary.h"
#include "AnimCharacterMovementLibrary.h"
```

### 基本用法

所有函数都是静态的蓝图函数库方法，可以在 C++ 动画节点中直接调用：

```cpp
// 在 AnimNode 的 UpdateAssetPlayer 中使用距离匹配推进动画
// 来源: Public/AnimDistanceMatchingLibrary.h

// 假设在自定义 AnimNode 的 Evaluate_AnyThread 中
void FMyAnimNode::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    // 计算角色上一帧的移动距离
    float DeltaDistance = FVector::Dist2D(PreviousPosition, CurrentPosition);
    
    // 通过距离匹配推进序列评估器
    SequenceEvaluator = UAnimDistanceMatchingLibrary::AdvanceTimeByDistanceMatching(
        Context.GetUpdateContext(),
        SequenceEvaluator,
        DeltaDistance,                                      // 实际移动距离
        FName("DistanceCurve"),                              // 动画上的距离曲线名称
        FVector2D(0.75f, 1.25f)                             // 播放速率钳制范围
    );
}
```

### 进阶用法

结合停止预测与距离匹配实现完整的停止动画系统：

```cpp
// 在 C++ 动画节点中实现停止动画逻辑
// 来源: Public/AnimCharacterMovementLibrary.h + Public/AnimDistanceMatchingLibrary.h

void FMyAnimNode::EvaluateStopAnimation(
    const FAnimationUpdateContext& Context,
    const FVector& CurrentVelocity,
    float BrakingFriction,
    float GroundFriction,
    float BrakingFrictionFactor,
    float BrakingDecelerationWalking)
{
    // 1. 预测停止位置（返回角色本地空间的向量，其大小即为到停止点的距离）
    FVector StopLocation = UAnimCharacterMovementLibrary::PredictGroundMovementStopLocation(
        CurrentVelocity,
        /* bUseSeparateBrakingFriction */ true,
        BrakingFriction,
        GroundFriction,
        BrakingFrictionFactor,
        BrakingDecelerationWalking
    );
    
    float DistanceToStop = StopLocation.Size();
    
    // 2. 在停止动画中找到匹配该距离的帧
    SequenceEvaluator = UAnimDistanceMatchingLibrary::DistanceMatchToTarget(
        SequenceEvaluator,
        DistanceToStop,
        FName("DistanceCurve")
    );
}

// 同理，转向枢轴预测用于转向动画
FVector PivotLocation = UAnimCharacterMovementLibrary::PredictGroundMovementPivotLocation(
    CurrentAcceleration,
    CurrentVelocity,
    GroundFriction
);
float DistanceToPivot = PivotLocation.Size();
```

## Demo 示例

```cpp
// MyLocomotionAnimNode.h
#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimNodeBase.h"
#include "AnimDistanceMatchingLibrary.h"
#include "AnimCharacterMovementLibrary.h"
#include "MyLocomotionAnimNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyLocomotion : public FAnimNode_Base
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Settings")
    FSequenceEvaluatorReference SequenceEvaluator;

    UPROPERTY(EditAnywhere, Category = "Settings")
    FName DistanceCurveName = TEXT("DistanceCurve");

    // FAnimNode_Base interface
    virtual void Evaluate_AnyThread(FPoseContext& Output) override;
    virtual void Update_AnyThread(const FAnimationUpdateContext& Context) override;
    
    FVector PreviousPosition = FVector::ZeroVector;
    bool bIsStopping = false;
};

// MyLocomotionAnimNode.cpp
#include "MyLocomotionAnimNode.h"

void FAnimNode_MyLocomotion::Update_AnyThread(const FAnimationUpdateContext& Context)
{
    FAnimNode_Base::Update_AnyThread(Context);

    // 获取角色当前移动属性
    AActor* OwnerActor = GetOwnerActor(Context);
    UCharacterMovementComponent* CMC = OwnerActor ? 
        OwnerActor->FindComponentByClass<UCharacterMovementComponent>() : nullptr;
    
    if (!CMC) return;

    FVector CurrentVelocity = CMC->Velocity;
    float Speed = CurrentVelocity.Size2D();

    if (bIsStopping)
    {
        // 停止动画：预测停止位置并匹配
        FVector StopLocation = UAnimCharacterMovementLibrary::PredictGroundMovementStopLocation(
            CurrentVelocity,
            CMC->bUseSeparateBrakingFriction,
            CMC->BrakingFriction,
            CMC->GroundFriction,
            CMC->BrakingFrictionFactor,
            CMC->BrakingDecelerationWalking
        );
        
        SequenceEvaluator = UAnimDistanceMatchingLibrary::DistanceMatchToTarget(
            SequenceEvaluator,
            StopLocation.Size(),
            DistanceCurveName
        );
    }
    else
    {
        // 循环动画：按距离推进
        float DistanceTraveled = FVector::Dist2D(PreviousPosition, OwnerActor->GetActorLocation());
        PreviousPosition = OwnerActor->GetActorLocation();
        
        SequenceEvaluator = UAnimDistanceMatchingLibrary::AdvanceTimeByDistanceMatching(
            Context.GetUpdateContext(),
            SequenceEvaluator,
            DistanceTraveled,
            DistanceCurveName,
            FVector2D(0.75f, 1.25f)
        );
    }
}

void FAnimNode_MyLocomotion::Evaluate_AnyThread(FPoseContext& Output)
{
    SequenceEvaluator.Evaluate_AnyThread(Output);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationLocomotionLibraryRuntime` | 运行时蓝图函数库和动画节点（使用插件时的主要依赖） |
| `AnimationLocomotionLibraryEditor` | 编辑器工具，包含距离曲线生成的 Animation Modifier |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新格式 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 添加内联生成宏优化编译 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 同上，批量应用内联宏 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 统一 DLL 导出声明风格 |
| 2025-03-13 | `b059f7b4` | Fix trivial unreachable code warnings. | 修复不可达代码警告 |

### 维护评价

该插件创建于 2021 年 9 月，至今约 5 年。**近期所有更新均为全局性的编译/代码风格迁移**（如 UE_INLINE_GENERATED_CPP_BY_NAME、DLL 导出声明统一），并非针对插件功能本身的实质性改进。

核心 API 自首次提交以来基本保持稳定，说明功能设计已经成熟。但该插件仍标记为 **Beta** 且 **EnabledByDefault=false**，这意味着 Epic 尚未将其视为正式稳定的功能。

该插件是 Lyra 项目移动系统的核心依赖之一，实际使用中较为可靠，但需注意：
- 标记为 Beta，未来 API 可能发生变化
- 需要手动启用
- Editor 模块包含距离曲线生成的 Animation Modifier，首次使用时需要为动画资产生成距离曲线

**推荐使用**：如果你正在开发第三人称移动动画系统，这是 Epic 官方推荐的方案，建议参考 Lyra 项目的实际用法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationLocomotionLibrary)
- 官方文档：无（DocsURL 为空）