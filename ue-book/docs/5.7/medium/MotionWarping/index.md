# Motion Warping

> A runtime plugin for warping (adjusting) root motion from animations to align characters with target transforms in the world.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MotionWarping` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-23 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MotionWarping) | |

## 用途

Motion Warping 解决的核心问题是：**动画中预烘焙的 Root Motion 无法动态适应运行时的目标位置**。

在传统工作流中，一个攻击动画会把角色从 A 点移动到 B 点，但 B 点是动画制作时硬编码的。当敌人实际站在不同位置时，要么动画打空，要么需要大量手动调整。Motion Warping 通过在动画播放窗口内实时"扭曲"Root Motion 的位移和旋转，让角色精确对齐到运行时指定的世界空间目标点。

关键设计思想：
- 通过 **AnimNotifyState** 在动画编辑器中定义"warping window"（变形窗口）
- 通过 **Warp Target** 在运行时指定目标位置/旋转
- 通过 **Root Motion Modifier** 在窗口持续期间修改每一帧的 Root Motion
- 系统完全集成在 CharacterMovementComponent 的 Root Motion 管线中

## 使用场景

- **近战攻击**：攻击动画有固定的位移，但敌人位置不确定。Motion Warping 让角色自动滑动到敌人面前
- **翻越/攀爬**：跳跃动画需要对齐到障碍物边缘。设置 Warp Target 为障碍物顶点，动画自动适配
- **终结技/QTE**：需要角色精确站到特定位置播放处决动画
- **平台跳跃**：角色需要跳到移动平台，实时更新 Warp Target 追踪平台位置
- **任何需要动态对齐的 Root Motion 动画**：冲刺、滑铲、闪避等

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddOrUpdateWarpTargetFromTransform` | 添加/更新一个基于 Transform 的 Warp Target | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromComponent` | 添加/更新一个基于 SceneComponent 的 Warp Target（可追踪移动目标） | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromLocation` | 添加/更新一个仅基于位置的 Warp Target | `UMotionWarpingComponent` |
| `AddOrUpdateWarpTargetFromLocationAndRotation` | 添加/更新一个基于位置+旋转的 Warp Target | `UMotionWarpingComponent` |
| `RemoveWarpTarget` | 移除指定名称的 Warp Target | `UMotionWarpingComponent` |
| `RemoveAllWarpTargets` | 移除所有 Warp Targets | `UMotionWarpingComponent` |
| `DisableAllRootMotionModifiers` | 禁用所有活跃的 Root Motion Modifier | `UMotionWarpingComponent` |
| `GetMotionWarpingWindowsFromAnimation` | 从动画中提取所有 Motion Warping 窗口信息 | `UMotionWarpingUtilities` |
| `GetMotionWarpingWindowsForWarpTargetFromAnimation` | 按 Warp Target 名称筛选动画中的 Motion Warping 窗口 | `UMotionWarpingUtilities` |
| `ExtractRootMotionFromAnimation` | 从动画中提取指定时间范围的 Root Motion | `UMotionWarpingUtilities` |
| `ExtractBoneTransformFromAnimationAtTime` | 从动画中提取指定骨骼在指定时间的变换 | `UMotionWarpingUtilities` |
| `MakeMotionWarpingTarget` | 创建 FMotionWarpingTarget 结构体（蓝图 Pure 节点） | `UMotionWarpingFunctionLibrary` |
| `AddRootMotionModifierSkewWarp` | 动态添加 SkewWarp Modifier | `URootMotionModifier_SkewWarp` |
| `AddRootMotionModifierScale` | 动态添加 Scale Modifier | `URootMotionModifier_Scale` |

### Switch Off Condition 节点（实验性）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddSwitchOffCondition` | 为指定 Warp Target 添加关闭条件 | `UMotionWarpingComponent` |
| `CreateSwitchOffDistanceCondition` | 创建基于距离的关闭条件 | `UMotionWarpingSwitchOffDistanceCondition` |
| `CreateSwitchOffAngleToTargetCondition` | 创建基于角度的关闭条件 | `UMotionWarpingSwitchOffAngleToTargetCondition` |
| `CreateSwitchOffCompositeCondition` | 创建组合逻辑关闭条件（AND/OR） | `UMotionWarpingSwitchOffCompositeCondition` |
| `CreateSwitchOffBlueprintableCondition` | 从蓝图子类创建自定义关闭条件 | `UMotionWarpingSwitchOffBlueprintableCondition` |

### 使用示例（蓝图描述）

**基本近战攻击 Warping 流程：**

1. 给角色添加 `MotionWarpingComponent`
2. 在攻击动画（AnimSequence 或 AnimMontage）上添加 `AnimNotifyState_MotionWarping`，覆盖需要变形的时间段
3. 在 Notify 的 `RootMotionModifier` 属性中选择 `Skew Warp`（推荐）或 `Adjustment Blend Warp`
4. 设置 Modifier 的 `WarpTargetName`（如 `"AttackTarget"`）
5. 在蓝图中，播放动画前调用 `AddOrUpdateWarpTargetFromComponent`，将 `"AttackTarget"` 指向敌人位置
6. 播放动画（`PlayMontage`），Motion Warping 自动在窗口内将角色对齐到目标

**追踪移动目标：**

在 `AddOrUpdateWarpTargetFromComponent` 中设置 `bFollowComponent = true`，Warp Target 会每帧更新位置。配合 `LocationOffset` 和 `RotationOffset` 可以微调对齐位置。

**通过 Notify 事件控制 Warping：**

AnimNotifyState_MotionWarping 提供了三个蓝图可实现事件：
- `OnWarpBegin` — Warping 窗口开始时触发
- `OnWarpUpdate` — 每帧更新时触发
- `OnWarpEnd` — Warping 窗口结束时触发

## C++ 用法

### 头文件引入

```cpp
#include "MotionWarpingComponent.h"
#include "MotionWarpingFunctionLibrary.h"
#include "RootMotionModifier.h"
#include "AnimNotifyState_MotionWarping.h"
```

### 基本用法

**添加 Warp Target 并播放动画：**

```cpp
// 获取 MotionWarpingComponent（假设已添加到角色上）
UMotionWarpingComponent* MWComp = Character->FindComponentByClass<UMotionWarpingComponent>();

// 添加基于 Component 的 Warp Target（追踪目标骨骼位置）
MWComp->AddOrUpdateWarpTargetFromComponent(
    FName("AttackTarget"),        // 目标名称（与动画 Notify 中的 WarpTargetName 匹配）
    EnemyMesh,                     // 目标组件
    FName("spine_03"),             // 目标骨骼名
    true,                          // bFollowComponent - 持续追踪
    FVector::ZeroVector,           // LocationOffset
    FRotator::ZeroRotator          // RotationOffset
);

// 或者添加基于 Transform 的 Warp Target
FTransform TargetTransform(EnemyRotation, EnemyLocation);
MWComp->AddOrUpdateWarpTargetFromTransform(FName("AttackTarget"), TargetTransform);

// 播放攻击动画 Montage
Character->PlayAnimMontage(AttackMontage);
```

（来源：`MotionWarpingComponent.h` / `MotionWarpingComponent.cpp`）

**程序化添加 Root Motion Modifier：**

```cpp
// 不依赖 AnimNotifyState，直接在代码中创建 Modifier
URootMotionModifier_SkewWarp* Modifier = URootMotionModifier_SkewWarp::AddRootMotionModifierSkewWarp(
    MWComp,
    AttackAnimation,    // 动画资产
    0.5f,               // StartTime
    1.2f,               // EndTime
    FName("AttackTarget"),
    EWarpPointAnimProvider::None,
    FTransform::Identity,
    NAME_None,
    true,   // bWarpTranslation
    true,   // bIgnoreZAxis
    true,   // bWarpRotation
    EMotionWarpRotationType::Default,
    EMotionWarpRotationMethod::Slerp,
    1.0f,   // WarpRotationTimeMultiplier
    0.0f    // WarpMaxRotationRate
);
```

（来源：`RootMotionModifier_SkewWarp.h`）

### 进阶用法

**自定义 Adapter（非 Character Actor）：**

UE 5.5 之后 Motion Warping 不再局限于 ACharacter。你可以创建自定义 Adapter 让非 Character Actor 也能使用 Motion Warping：

```cpp
// 自定义 Adapter 头文件
UCLASS()
class UMyCustomAdapter : public UMotionWarpingBaseAdapter
{
    GENERATED_BODY()
public:
    virtual AActor* GetActor() const override { return MyActor; }
    virtual USkeletalMeshComponent* GetMesh() const override { return MyMesh; }
    virtual FVector GetVisualRootLocation() const override;
    virtual FVector GetBaseVisualTranslationOffset() const override;
    virtual FQuat GetBaseVisualRotationOffset() const override;
    
    void SetActor(AActor* InActor) { MyActor = InActor; }
    void SetMesh(USkeletalMeshComponent* InMesh) { MyMesh = InMesh; }

private:
    TWeakObjectPtr<AActor> MyActor;
    TWeakObjectPtr<USkeletalMeshComponent> MyMesh;
};

// 初始化时创建 Adapter
UMotionWarpingComponent* MWComp = MyActor->FindComponentByClass<UMotionWarpingComponent>();
UMyCustomAdapter* Adapter = MWComp->CreateOwnerAdapter<UMyCustomAdapter>();
Adapter->SetActor(MyActor);
Adapter->SetMesh(MyMesh);
```

（来源：`MotionWarpingAdapter.h`、`MotionWarpingCharacterAdapter.h`）

**使用 Switch Off Condition 控制 Warping 行为：**

```cpp
// 基于距离的关闭条件：当角色距离目标太远时取消追踪
UMotionWarpingSwitchOffDistanceCondition* DistanceCondition =
    UMotionWarpingSwitchOffDistanceCondition::CreateSwitchOffDistanceCondition(
        Character,
        ESwitchOffConditionEffect::CancelFollow,   // 取消追踪，锁定当前位置
        ESwitchOffConditionDistanceOp::GreaterThan,
        500.0f,                                      // 距离阈值
        true                                         // 使用 Warp Target 位置
    );
MWComp->AddSwitchOffCondition(FName("AttackTarget"), DistanceCondition);
```

（来源：`MotionWarpingSwitchOffCondition.h`）

**Scale Modifier — 缩放 Root Motion：**

```cpp
// 将动画的 Root Motion 位移放大 1.5 倍
URootMotionModifier_Scale* ScaleMod = URootMotionModifier_Scale::AddRootMotionModifierScale(
    MWComp,
    MyAnimation,
    0.0f,   // StartTime
    1.0f,   // EndTime
    FVector(1.5f, 1.5f, 1.0f)  // Scale（X/Y/Z 分别缩放）
);
```

（来源：`RootMotionModifier.h`）

## Root Motion Modifier 类型总览

Motion Warping 的核心在于 Root Motion Modifier。每个 Modifier 负责在指定动画窗口内修改 Root Motion：

| 类型 | 说明 | 状态 |
|---|---|---|
| `URootMotionModifier_SkewWarp` | **推荐**。通过 skew（倾斜）变换将 Root Motion 对齐到目标位置。支持平移和旋转的独立控制 | 正式 |
| `URootMotionModifier_AdjustmentBlendWarp` | 高级模式。预计算变形后的骨骼轨迹，支持 IK 骨骼对齐（如脚部精确踩地） | 实验性（UI 中隐藏） |
| `URootMotionModifier_PrecomputedWarp` | 首帧计算完整对齐路径，后续帧直接应用。仅适用于静态目标 | 实验性 |
| `URootMotionModifier_Scale` | 简单缩放 Root Motion 位移，不做位置对齐 | 正式 |
| `URootMotionModifier_SimpleWarp` | 简单 Warp，已被 SkewWarp 取代 | 已废弃 |

### SkewWarp 详解

SkewWarp 是最常用的 Modifier。它的核心参数：

- **WarpTargetName** — 要对齐的 Warp Target 名称
- **bWarpTranslation** — 是否扭曲位移
- **bIgnoreZAxis** — 忽略 Z 轴（通常为 true，保留跳跃/落地的 Z 运动）
- **bWarpToFeetLocation** — 对齐到脚部位置还是 Actor 中心
- **bWarpRotation** — 是否扭曲旋转
- **RotationType** — `Default`（匹配目标旋转）、`Facing`（面向目标）、`OppositeDefault`/`OppositeFacing`（反向）
- **RotationMethod** — `Slerp`、`SlerpWithClampedRate`、`ConstantRate`、`Scale`
- **bSubtractRemainingRootMotion** — 通知结束后是否继续扣除剩余 Root Motion，让角色在动画结束时才到达目标
- **MaxSpeedClampRatio** — 限制最大位移速度倍率（相对于原始动画速度）

### PrecomputedWarp 详解（实验性）

PrecomputedWarp 在第一帧计算完整的对齐轨迹，适用于静态目标。额外支持：

- **TranslationWarpingCurve / RotationWarpingCurve** — 控制位移/旋转的混合曲线
- **AlignOffset** — 从 Root 到对齐点的偏移
- **bEnableSteering** — 启用转向，根据变形方向自动旋转角色面向运动方向
- **UpdateMode** — `World`（每帧计算世界空间位置）或 `Relative`（每帧相对应用）
- **bSeparateTranslationCurves** — 分别控制运动方向和非运动方向的位移混合

### EMotionWarpRotationType 说明

| 值 | 效果 |
|---|---|
| `Default` | 角色旋转匹配 Warp Target 的旋转 |
| `Facing` | 角色旋转面向 Warp Target |
| `OppositeDefault` | 匹配目标旋转 + 180° 偏航 |
| `OppositeFacing` | 背对 Warp Target（面向 + 180°） |

### EMotionWarpRotationMethod 说明

| 值 | 效果 |
|---|---|
| `Slerp` | 球面线性插值（默认，最平滑） |
| `SlerpWithClampedRate` | Slerp 但限制最大旋转速率 |
| `ConstantRate` | 恒定旋转速率 |
| `Scale` | 缩放旋转，确保窗口结束时精确到达目标旋转 |

## Switch Off Condition 系统（实验性）

Switch Off Condition 允许在运行时动态判断是否应取消/暂停 Warping。支持的效果：

| Effect | 说明 |
|---|---|
| `CancelFollow` | 停止追踪 Component，锁定当前位置为静态目标 |
| `CancelWarping` | 完全取消 Warping，移除 Warp Target |
| `PauseWarping` | 暂停 Warping（仅播放原始 Root Motion） |
| `PauseRootMotion` | 暂停 Root Motion（原地播放动画） |

内置条件类型：
- **Distance Condition** — 基于距离判断（大于/小于阈值）
- **Angle To Target Condition** — 基于角度判断（角色朝向与目标方向的夹角）
- **Composite Condition** — AND/OR 组合多个条件
- **Blueprintable Condition** — 蓝图自定义条件（重写 `BP_Check`）

## 动画设置

在动画编辑器中使用 Motion Warping：

1. 打开 AnimSequence 或 AnimMontage
2. 在 Notify Track 上右键 → 添加 `Motion Warping`（AnimNotifyState）
3. 拖拽 Notify 的起止范围定义 warping window
4. 在 Notify 的 Details 面板中，配置 `RootMotionModifier`：
   - 选择类型（Skew Warp、Scale 等）
   - 设置 `WarpTargetName`
   - 配置平移/旋转参数

### Warp Point Anim Provider

在动画中可以定义"warp point"，让系统计算角色 Root 相对于 warp point 的偏移：

| 值 | 说明 |
|---|---|
| `None` | 不使用动画中的 warp point，直接使用运行时 Warp Target |
| `Static` | 在 Notify 中手动输入一个静态 Transform 作为 warp point |
| `Bone` | 使用动画中某个骨骼的位置作为 warp point |

## 调试

Motion Warping 提供了丰富的控制台变量用于调试：

| CVar | 说明 |
|---|---|
| `a.MotionWarping.Disable` | 设为 1 禁用所有 Motion Warping |
| `a.MotionWarping.Debug` | 0=关闭, 1=仅日志, 2=仅 DrawDebug, 3=两者都开 |
| `a.MotionWarping.DrawDebugLifeTime` | DrawDebug 持续时间（秒），默认 1.0 |
| `a.MotionWarping.Debug.Target` | 0=关闭, 1=选中Actor, 2=所有Actor |
| `a.MotionWarping.Debug.SwitchOffCondition` | 0=关闭, 1=选中Actor, 2=所有Actor |

## Demo 示例

### 最小可编译示例

**MyCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "MyCharacter.generated.h"

class UMotionWarpingComponent;

UCLASS()
class AMyCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AMyCharacter();

    /** 对目标执行攻击，自动 warp 到目标面前 */
    UFUNCTION(BlueprintCallable)
    void PerformAttack(AActor* TargetActor);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UMotionWarpingComponent> MotionWarpingComp;

    UPROPERTY(EditDefaultsOnly, Category = "Combat")
    TObjectPtr<UAnimMontage> AttackMontage;

    UPROPERTY(EditDefaultsOnly, Category = "Combat")
    FName WarpTargetName = "AttackTarget";
};
```

**MyCharacter.cpp**
```cpp
#include "MyCharacter.h"
#include "MotionWarpingComponent.h"
#include "Components/SkeletalMeshComponent.h"

AMyCharacter::AMyCharacter()
{
    MotionWarpingComp = CreateDefaultSubobject<UMotionWarpingComponent>(TEXT("MotionWarping"));
}

void AMyCharacter::PerformAttack(AActor* TargetActor)
{
    if (!TargetActor || !MotionWarpingComp || !AttackMontage)
    {
        return;
    }

    // 设置 Warp Target 指向目标的 Mesh 组件
    if (USkeletalMeshComponent* TargetMesh = TargetActor->FindComponentByClass<USkeletalMeshComponent>())
    {
        MotionWarpingComp->AddOrUpdateWarpTargetFromComponent(
            WarpTargetName,
            TargetMesh,
            NAME_None,     // 不使用特定骨骼
            true,          // bFollowComponent - 追踪目标
            FVector::ZeroVector,
            FRotator::ZeroRotator
        );
    }
    else
    {
        MotionWarpingComp->AddOrUpdateWarpTargetFromTransform(
            WarpTargetName,
            TargetActor->GetActorTransform()
        );
    }

    // 播放攻击动画
    PlayAnimMontage(AttackMontage);
}
```

**Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "MotionWarping"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统、反射、序列化 |
| `Engine` | 引擎核心（Actor、Component、动画系统） |
| `NetCore` | 网络核心（Push Model 复制支持） |
| `Slate` | 编辑器 UI（Private，仅编辑器构建） |
| `SlateCore` | Slate 核心（Private，仅编辑器构建） |
| `UnrealEd` | 编辑器工具（Public，仅编辑器构建） |
| `AnimGraph` | 动画图编辑器（Public，仅编辑器构建） |

注意：Motion Warping **不依赖** `GameplayAbilities` 或 `EnhancedInput` 等模块，是一个独立的动画插件。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `8aeb226038a2` | 添加 PrecomputedWarp 实验性 Root Motion Modifier，支持首帧计算完整对齐路径 |
| 2025-09-03 | `edbc30913b46` | 将 Switch Off Condition 和 Warp Target Direction Mode 标记为实验性，提示 API 将来会变更 |
| 2025-09-01 | `5ad5ec9e76fc` | 修复 Switch Off Condition 在 Component 跟踪结束时使用错误目标 Transform 的 bug（UE-314986） |

### 维护评价

- **活跃维护**：Motion Warping 在 2025 年仍有频繁的功能更新和 bug 修复
- **持续演进**：从 UE 5.5 开始扩展了 Adapter 系统，不再局限于 ACharacter，架构更加通用
- **实验性功能扩展**：PrecomputedWarp、Switch Off Condition 等实验性功能持续迭代
- **已知限制**：
  - `AdjustmentBlendWarp` 仍标记为实验性且在 UI 中隐藏（`hidedropdown`）
  - `PrecomputedWarp` 仅适用于静态目标
  - `SimpleWarp` 已废弃，应使用 `SkewWarp`
  - 部分 API 标记为实验性，未来可能变更
- **推荐使用**：✅ 推荐。Motion Warping 是 Epic 官方维护的核心动画工具，被 Lyra、Fortnite 等项目广泛使用。基本的 SkewWarp 功能稳定可靠，实验性功能可在非关键场景中使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/MotionWarping)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/motion-warping-in-unreal-engine)
