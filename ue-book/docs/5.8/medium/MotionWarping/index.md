# Motion Warping

> 

| 属性 | 值 |
|---|---|
| 中文名 | 运动扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MotionWarping` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MotionWarping) | |

## 用途

Motion Warping 解决的是 **动画播放过程中动态调整角色位置和朝向** 的问题。

在动作游戏中，角色执行攻击、闪避、跳跃等动画时，目标位置在动画设计时是未知的——敌人可能在不同距离、不同方向。传统方案要么让动画严格按根运动播放（导致"打空气"），要么完全放弃根运动（失去动画的精确感）。Motion Warping 通过在动画的特定时间窗口内实时修改根运动，让角色精确到达游戏逻辑指定的世界空间目标点，同时保留动画本身的运动质感。

核心机制：
1. **在动画中设置扭曲窗口**（通过 AnimNotifyState）
2. **运行时设置扭曲目标**（世界空间中的位置/朝向，或跟随某个组件）
3. **在窗口期间自动修改根运动**，使角色平滑地对齐到目标

## 使用场景

- 你在做一个动作游戏，攻击动画需要根据敌人距离自动调整位移 → 用 SkewWarp
- 你需要角色在翻越障碍时精确落在对侧的特定位置 → 用 Motion Warping + Warp Target
- 你想让动画效果既能保持根运动的质感又能命中实际目标 → 用 AdjustmentBlendWarp
- 你需要在动画执行中途根据距离/角度条件取消对齐效果 → 用 SwitchOffCondition
- 你想在蓝图中完全自定义根运动扭曲逻辑 → 用 Blueprintable 修饰器
- 你需要在动画蒙太奇轨迹预测中应用扭曲 → 用 MontageTrajectoryAdapter

## 蓝图用法

### 核心节点

#### 扭曲目标管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddOrUpdateWarpTarget` | 添加或更新一个扭曲目标 | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromTransform` | 从 Transform 创建扭曲目标 | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromComponent` | 从场景组件创建扭曲目标（可跟随） | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromLocation` | 从位置创建扭曲目标 | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromLocationAndRotation` | 从位置+旋转创建扭曲目标 | `UMotionWarpingComponent` |
| `RemoveWarpTarget` | 移除指定扭曲目标 | `UMotionWarpingComponent` |
| `RemoveAllWarpTargets` | 移除所有扭曲目标 | `UMotionWarpingComponent` |
| `RemoveWarpTargets` | 批量移除扭曲目标 | `UMotionWarpingComponent` |
| `DisableAllRootMotionModifiers` | 禁用所有根运动修改器 | `UMotionWarpingComponent` |

#### 工具函数（UMotionWarpingUtilities）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ExtractRootMotionFromAnimation` | 从动画中提取指定时间段的根运动 | `UMotionWarpingUtilities` |
| `GetMotionWarpingWindowsFromAnimation` | 获取动画中所有扭曲窗口 | `UMotionWarpingUtilities` |
| `GetMotionWarpingWindowsForWarpTargetFromAnimation` | 获取指定目标名的扭曲窗口 | `UMotionWarpingUtilities` |
| `ExtractBoneTransformFromAnimationAtTime` | 在指定时间提取骨骼变换 | `UMotionWarpingUtilities` |

#### 添加修改器（静态工厂函数）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddRootMotionModifierSkewWarp` | 添加基于扭曲的根运动修改器 | `URootMotionModifier_SkewWarp` |
| `AddRootMotionModifierScale` | 添加缩放根运动修改器 | `URootMotionModifier_Scale` |

#### 关闭条件（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSwitchOffCondition` | 为扭曲目标添加关闭条件 | `UMotionWarpingComponent` |
| `CreateSwitchOffDistanceCondition` | 创建基于距离的关闭条件 | `UMotionWarpingSwitchOffDistanceCondition` |
| `CreateSwitchOffAngleToTargetCondition` | 创建基于角度的关闭条件 | `UMotionWarpingSwitchOffAngleToTargetCondition` |
| `CreateSwitchOffCompositeCondition` | 创建组合关闭条件（AND/OR） | `UMotionWarpingSwitchOffCompositeCondition` |
| `CreateSwitchOffBlueprintableCondition` | 创建蓝图自定义关闭条件 | `UMotionWarpingSwitchOffBlueprintableCondition` |

### 使用示例

**基本攻击对齐**：

1. 角色蓝图中添加 `MotionWarpingComponent`
2. 在攻击动画中添加 `AnimNotifyState_MotionWarping` 通知，配置 RootMotionModifier 为 `SkewWarp`
3. 攻击触发时（如按键事件）：
   - 通过 AI 或检测系统找到目标敌人位置
   - 调用 `AddOrUpdateWarpTargetFromComponent`，WarpTargetName 设为 "AttackTarget"，Component 设为敌人的 Mesh
4. 播放攻击动画蒙太奇
5. 在动画通知窗口期间，角色会自动对齐到目标位置

**蓝图连接逻辑**：

```
[玩家按下攻击] → [射线检测/获取最近敌人]
    → [MotionWarpingComponent: AddOrUpdateWarpTargetFromComponent]
        - WarpTargetName: "AttackTarget"
        - Component: 敌人 Mesh
        - BoneName: "spine_01"
        - bFollowComponent: true
    → [PlayMontage (攻击蒙太奇)]
```

## C++ 用法

### 头文件引入

```cpp
#include "MotionWarpingComponent.h"
#include "AnimNotifyState_MotionWarping.h"
#include "RootMotionModifier_SkewWarp.h"
#include "MotionWarpingFunctionLibrary.h"
```

### 基本用法

从源码中提取的核心 API 用法：

```cpp
// 在角色中获取 MotionWarpingComponent
UMotionWarpingComponent* WarpComp = Character->FindComponentByClass<UMotionWarpingComponent>();

// 添加扭曲目标（从场景组件）
WarpComp->AddOrUpdateWarpTargetFromComponent(
    FName("AttackTarget"),          // 目标名称
    EnemyMeshComponent,             // 目标组件
    FName("spine_01"),              // 骨骼名
    true,                           // 是否跟随组件
    FVector::ZeroVector,            // 位置偏移
    FRotator::ZeroRotator           // 旋转偏移
);

// 添加扭曲目标（从 Transform）
WarpComp->AddOrUpdateWarpTargetFromTransform(
    FName("DodgeTarget"),
    FTransform(TargetRotation, TargetLocation)
);

// 查找扭曲目标
const FMotionWarpingTarget* FoundTarget = WarpComp->FindWarpTarget(FName("AttackTarget"));

// 移除扭曲目标
WarpComp->RemoveWarpTarget(FName("AttackTarget"));

// 禁用所有修改器
WarpComp->DisableAllRootMotionModifiers();
```

### 进阶用法

**程序化添加根运动修改器**（来源：`RootMotionModifier_SkewWarp.h`）：

```cpp
// 通过蓝图可调用的静态函数添加 SkewWarp 修改器
URootMotionModifier_SkewWarp* Modifier = URootMotionModifier_SkewWarp::AddRootMotionModifierSkewWarp(
    WarpComp,                           // MotionWarpingComponent
    AttackAnimation,                    // 动画资产
    0.3f,                               // 窗口开始时间
    0.8f,                               // 窗口结束时间
    FName("AttackTarget"),              // 扭曲目标名
    EWarpPointAnimProvider::Bone,       // 动画中扭曲点来源
    FTransform::Identity,               // 静态扭曲点变换
    FName("weapon_tip"),                // 动画中扭曲点骨骼名
    true,                               // 是否扭曲位移
    true,                               // 是否忽略 Z 轴
    true,                               // 是否扭曲旋转
    EMotionWarpRotationType::Default,   // 旋转类型
    EMotionWarpRotationMethod::Slerp    // 旋转方法
);
```

**程序化添加缩放修改器**（来源：`RootMotionModifier.h`）：

```cpp
// 添加缩放修改器来放大或缩小根运动
URootMotionModifier_Scale* ScaleModifier = URootMotionModifier_Scale::AddRootMotionModifierScale(
    WarpComp,
    Animation,
    0.1f,                               // 开始时间
    0.9f,                               // 结束时间
    FVector(2.0f, 2.0f, 1.0f)          // X/Y 方向放大两倍，Z 不变
);
```

**使用工具函数提取根运动**（来源：`MotionWarpingComponent.h`）：

```cpp
// 从动画提取根运动
FTransform RootMotion = UMotionWarpingUtilities::ExtractRootMotionFromAnimation(
    Animation, 0.3f, 0.8f
);

// 获取动画中所有扭曲窗口
TArray<FMotionWarpingWindowData> Windows;
UMotionWarpingUtilities::GetMotionWarpingWindowsFromAnimation(Animation, Windows);

for (const FMotionWarpingWindowData& Window : Windows)
{
    UAnimNotifyState_MotionWarping* Notify = Window.AnimNotify;
    float StartTime = Window.StartTime;
    float EndTime = Window.EndTime;
}

// 获取指定扭曲目标的窗口
TArray<FMotionWarpingWindowData> TargetWindows;
UMotionWarpingUtilities::GetMotionWarpingWindowsForWarpTargetFromAnimation(
    Animation, FName("AttackTarget"), TargetWindows
);
```

**创建关闭条件**（来源：`MotionWarpingSwitchOffCondition.h`）：

```cpp
// 创建距离关闭条件：目标距离超过 500 时取消扭曲
UMotionWarpingSwitchOffDistanceCondition* DistCondition = 
    UMotionWarpingSwitchOffDistanceCondition::CreateSwitchOffDistanceCondition(
        OwnerActor,
        ESwitchOffConditionEffect::CancelWarping,
        ESwitchOffConditionDistanceOp::GreaterThan,
        ESwitchOffConditionDistanceAxesType::AllAxes,
        500.0f
    );

WarpComp->AddSwitchOffCondition(FName("AttackTarget"), DistCondition);
```

**监听扭曲事件**：

```cpp
// 绑定预更新事件
WarpComp->OnPreUpdate.AddDynamic(this, &AMyCharacter::OnMotionWarpingPreUpdate);

void AMyCharacter::OnMotionWarpingPreUpdate(UMotionWarpingComponent* MotionWarpingComp)
{
    // 在根运动修改器更新前执行自定义逻辑
    // 例如动态更新扭曲目标位置
    MotionWarpingComp->AddOrUpdateWarpTargetFromComponent(
        FName("AttackTarget"), EnemyMesh, NAME_None, true
    );
}
```

## Demo 示例

### 头文件

```cpp
// MotionWarpingDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MotionWarpingDemoComponent.generated.h"

class UMotionWarpingComponent;
class UAnimMontage;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURGAME_API UMotionWarpingDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMotionWarpingDemoComponent();

    /** 执行攻击并自动对齐到目标 */
    UFUNCTION(BlueprintCallable, Category = "Combat")
    void PerformAttackWithWarping(AActor* TargetActor, UAnimMontage* AttackMontage, FName WarpTargetBone = NAME_None);

    /** 执行闪避到指定位置 */
    UFUNCTION(BlueprintCallable, Category = "Combat")
    void PerformDodgeToLocation(FVector TargetLocation, UAnimMontage* DodgeMontage);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TWeakObjectPtr<UMotionWarpingComponent> WarpComp;

    static constexpr FName AttackTargetName = TEXT("AttackTarget");
    static constexpr FName DodgeTargetName = TEXT("DodgeTarget");
};
```

### 源文件

```cpp
// MotionWarpingDemoComponent.cpp
#include "MotionWarpingDemoComponent.h"
#include "MotionWarpingComponent.h"
#include "GameFramework/Character.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimMontage.h"

UMotionWarpingDemoComponent::UMotionWarpingDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMotionWarpingDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 获取同角色上的 MotionWarpingComponent
    WarpComp = GetOwner()->FindComponentByClass<UMotionWarpingComponent>();
    if (!WarpComp.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("MotionWarpingDemoComponent: Owner missing MotionWarpingComponent"));
    }
}

void UMotionWarpingDemoComponent::PerformAttackWithWarping(
    AActor* TargetActor, UAnimMontage* AttackMontage, FName WarpTargetBone)
{
    if (!WarpComp.IsValid() || !TargetActor || !AttackMontage) return;

    USkeletalMeshComponent* TargetMesh = TargetActor->FindComponentByClass<USkeletalMeshComponent>();
    if (!TargetMesh) return;

    // 设置扭曲目标，跟随目标的骨骼
    WarpComp->AddOrUpdateWarpTargetFromComponent(
        AttackTargetName,
        TargetMesh,
        WarpTargetBone,
        true  // 跟随目标移动
    );

    // 播放攻击蒙太奇（其中应包含 AnimNotifyState_MotionWarping）
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (Character)
    {
        Character->PlayAnimMontage(AttackMontage);
    }
}

void UMotionWarpingDemoComponent::PerformDodgeToLocation(
    FVector TargetLocation, UAnimMontage* DodgeMontage)
{
    if (!WarpComp.IsValid() || !DodgeMontage) return;

    // 设置闪避目标为固定位置
    ACharacter* Character = Cast<ACharacter>(GetOwner());
    if (!Character) return;

    // 计算闪避方向，让角色面向目标
    FRotator LookAtRotation = (TargetLocation - Character->GetActorLocation()).Rotation();

    WarpComp->AddOrUpdateWarpTargetFromTransform(
        DodgeTargetName,
        FTransform(LookAtRotation, TargetLocation)
    );

    Character->PlayAnimMontage(DodgeMontage);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | AttributeBasedRootMotionComponent 可能用于基于属性的根运动控制 |
| `AnimationCore` | 动画核心处理 |
| `AnimGraphRuntime` | 动画图运行时 |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-15 | `b281d45d` | Fix SkewWarp math errors producing NaN when animated root motion is extremely small but non-zero | 修复 SkewWarp 在极小根运动下产生 NaN 的数学错误 |
| 2026-05-14 | `c2022a2e` | Motion Warping: Account for mesh scale when calculating warp points (see CachedOffsetFromWarpPoint) | 计算扭曲点时考虑网格缩放 |
| 2026-04-28 | `fa3424ae` | MotionWarping - exposing FindWarpTarget to BP | 将 FindWarpTarget 暴露给蓝图 |
| 2026-04-27 | `a7418fe1` | Merging from Main | 主分支合并 |
| 2026-04-22 | `e62384ba` | UE 5.8 Animation deprecation clean up (CL 3/10): MotionWarping | UE 5.8 动画废弃清理 |

### 维护评价

Motion Warping 处于 **活跃维护** 状态。该插件虽然仍标记为 Beta 版本（`IsBetaVersion: true`），但功能已经相当成熟，在商业项目（如 Lyra 示例项目）中有广泛使用。

**优点**：
- 近期持续有功能性更新和 bug 修复（2026 年 4-5 月有多次提交）
- API 逐步完善（如将 FindWarpTarget 暴露给蓝图）
- 数学精度问题得到修复（NaN 修复）
- 支持网格缩放等新特性

**注意事项**：
- `EnabledByDefault: false`，需要在项目设置中手动启用
- 标记为实验性的 API（如 SwitchOffCondition、PrecomputedWarp、MontageTrajectoryAdapter）可能在后续版本中发生变化
- 已废弃 `OppositeDefault` 和 `OppositeFacing` 旋转类型（建议使用 `AdditionalRotationOffset` 替代）
- `RootMotionModifier_SimpleWarp` 已废弃，应使用 `RootMotionModifier_SkewWarp`
- `AddOrUpdateWarpTargetFromComponent` 的旧签名（无 `LocationOffsetDirection` 参数）计划废弃

**推荐使用**：✅ 推荐。这是 Epic 官方维护的动作游戏核心功能插件，功能成熟且持续更新。在生产项目中使用时注意关注实验性 API 的变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MotionWarping)