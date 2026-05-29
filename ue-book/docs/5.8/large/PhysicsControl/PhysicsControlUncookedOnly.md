# PhysicsControl

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图节点、材质、物理资产） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlEditor` (Editor), `PhysicsControlUncookedOnly` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl) | |

## 用途

PhysicsControl 插件提供了一个比传统布娃娃系统更精细、可控的物理驱动动画解决方案。它通过 `PhysicsControlComponent` 和 `UAnimGraphNode_RigidBodyWithControl` 动画节点，允许开发者对骨骼网格体和静态网格体的各个刚体施加精确的力、力矩或约束，以实现高度可控的物理模拟效果。其核心价值在于将物理模拟与角色动画相结合，既保留了物理的随机性和真实感，又给予了艺术家和设计师足够的控制权，使其可以用于实现诸如受击反馈、物理驱动的姿态、或可控的布娃娃等复杂动画效果。

## 使用场景

-   你正在开发一个动作游戏，希望角色在受到不同方向和力度的攻击时，身体相应部位能产生符合物理规律且可控的扭曲和反应，而不是播放固定的受击动画。
-   你需要创建一个“有意识”的布娃娃系统，可以在物理模拟过程中保持或趋向于某个目标姿势，用于角色死亡后的自然倒地效果或解谜游戏中的物理操控。
-   你在制作动画时，希望在特定关键帧为角色的某些骨骼（如飘动的衣角、尾巴、饰品）添加基于物理的真实二级运动，且这些运动受到预设力和约束的精确控制。

## 蓝图用法

蓝图接口主要集中在 `UPhysicsControlComponent` 和 `UAnimGraphNode_RigidBodyWithControl` 类上。

### 核心节点

#### 物理控制组件 (PhysicsControlComponent)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableControl` / `DisableControl` | 启用或禁用对特定控制集的物理控制。 | `UPhysicsControlComponent` |
| `SetControlTarget` | 为控制集设置目标变换（位置、旋转）。 | `UPhysicsControlComponent` |
| `SetControlStrength` | 设置控制的强度和阻尼系数。 | `UPhysicsControlComponent` |
| `AddForce` / `AddTorque` | 向受控刚体施加一个世界空间的力或力矩。 | `UPhysicsControlComponent` |
| `EnableCollisionBetweenBodies` / `DisableCollisionBetweenBodies` | 控制两个指定刚体之间的碰撞。 | `UPhysicsControlComponent` |

#### 刚体控制动画节点 (AnimGraphNode_RigidBodyWithControl)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ToggleBodyVisibility` | 在动画蓝图编辑器中切换预览时的刚体网格体可见性。 | `UAnimGraphNode_RigidBodyWithControl` |
| `ToggleConstraintVisibility` | 在动画蓝图编辑器中切换预览时的物理约束可见性。 | `UAnimGraphNode_RigidBodyWithControl` |
| `ToggleControlSetViewerTab` | 打开或关闭用于查看和调试控制集的专用编辑器标签页。 | `UAnimGraphNode_RigidBodyWithControl` |
| `GenerateControlsAndBodyModifierNames` | 生成当前节点定义的控制集和身体修改器名称列表，供调试和程序化访问使用。 | `UAnimGraphNode_RigidBodyWithControl` |

### 使用示例（蓝图描述）

假设你有一个角色蓝图，并已添加了 `PhysicsControlComponent`。
1.  **创建控制集**：在角色的动画蓝图或直接在角色蓝图的初始化事件中，通过 `PhysicsControlComponent` 创建针对特定骨骼（如 `spine_02`）的“父空间”或“世界空间”控制集。
2.  **响应事件**：当角色受到伤害时（例如，`Event AnyDamage`），调用 `PhysicsControlComponent` 的 `AddForce` 函数，根据伤害方向和大小，向 `spine_02` 对应的刚体施加一个力。
3.  **设置目标**：同时，可以调用 `SetControlTarget` 将该骨骼的物理目标旋转设置为一个夸张的扭曲姿态，然后通过 `SetControlStrength` 高强度值让物理模拟快速趋向于该目标，产生一个有力的受击反应。
4.  **恢复**：在一段时间后或使用计时器，逐渐减小控制强度或切换控制集，让角色平滑地从物理驱动状态过渡回动画驱动状态。

## C++ 用法

### 头文件引入

```cpp
#include “PhysicsControlComponent.h”
#include “AnimGraphNode_RigidBodyWithControl.h” // 通常在编辑器或动画蓝图代码中使用
#include “PhysicsControlSettings.h”
```

### 基本用法

以下示例展示了如何在 C++ 中为角色的 `PhysicsControlComponent` 添加力。
（注：此用法基于典型组件模式，具体函数名和结构请参考最新源码。）

```cpp
// 在角色类中获取或创建 PhysicsControlComponent
UPhysicsControlComponent* PhysicsControlComp = FindComponentByClass<UPhysicsControlComponent>();
if (!PhysicsControlComp)
{
    PhysicsControlComp = NewObject<UPhysicsControlComponent>(this);
    PhysicsControlComp->RegisterComponent();
}

// 当角色受到伤害时
void AMyCharacter::OnHit(const FVector& ImpactDirection, float DamageAmount)
{
    if (PhysicsControlComp && PhysicsControlComp->IsControlEnabled())
    {
        // 计算一个基于伤害的力向量
        FVector Force = ImpactDirection.GetSafeNormal() * DamageAmount * HitForceMultiplier;

        // 假设我们已经为 “spine_02” 骨骼创建了名为 “SpineControl” 的控制集
        PhysicsControlComp->AddForce(FName(“SpineControl”), Force);

        // 也可以设置一个目标姿态
        // PhysicsControlComp->SetControlTarget(FName(“SpineControl”), TargetTransform);
    }
}
```

### 进阶用法

结合 `PhysicsControlComponent` 和 `UAnimGraphNode_RigidBodyWithControl` 的动画节点设置，可以在动画实例中驱动更复杂的物理行为。

```cpp
// 在自定义动画实例 (UAnimInstance) 中
void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    AActor* OwnerActor = GetOwningActor();
    UPhysicsControlComponent* PhysicsComp = OwnerActor->FindComponentByClass<UPhysicsControlComponent>();

    // 根据游戏状态（例如，是否在格挡）动态调整物理控制强度
    if (bIsBlocking && PhysicsComp)
    {
        // 增强上半身控制刚度，使其感觉更“结实”
        PhysicsComp->SetControlStrength(FName(“SpineControl”), BlockingStiffness, BlockingDamping);
    }
    else if (PhysicsComp)
    {
        // 恢复到默认的柔韧设置
        PhysicsComp->SetControlStrength(FName(“SpineControl”), DefaultStiffness, DefaultDamping);
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示了如何创建一个带有 `PhysicsControlComponent` 的 Actor，并在被点击时施加一个力。
（注意：此示例省略了组件创建和注册的完整上下文。）

**MyPhysicsControlActor.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “MyPhysicsControlActor.generated.h”

class UPhysicsControlComponent;

UCLASS()
class MYPROJECT_API AMyPhysicsControlActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsControlActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void NotifyActorOnClicked(FKey ButtonPressed) override;

private:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = “Physics”, meta = (AllowPrivateAccess = “true”))
    UPhysicsControlComponent* PhysicsControlComponent;

    UPROPERTY(EditAnywhere, Category = “Physics”)
    float ImpulseStrength = 500.f;

    UPROPERTY(EditAnywhere, Category = “Physics”)
    FName TargetBoneName = NAME_None; // 需要驱动的骨骼名称
};
```

**MyPhysicsControlActor.cpp**
```cpp
#include “MyPhysicsControlActor.h”
#include “PhysicsControlComponent.h”
#include “Components/SkeletalMeshComponent.h”

AMyPhysicsControlActor::AMyPhysicsControlActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建一个骨骼网格体组件作为根组件
    USkeletalMeshComponent* SkeletalMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT(“SkeletalMesh”));
    RootComponent = SkeletalMesh;

    // 创建物理控制组件
    PhysicsControlComponent = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT(“PhysicsControl”));
}

void AMyPhysicsControlActor::BeginPlay()
{
    Super::BeginPlay();

    // 在 BeginPlay 中，为指定的骨骼创建并启用一个控制集
    // （具体 API 调用需参考实际类定义，此处为概念演示）
    if (PhysicsControlComponent && !TargetBoneName.IsNone())
    {
        // 伪代码： PhysicsControlComponent->CreateControlSet(TargetBoneName, ControlMode);
        // PhysicsControlComponent->EnableControl(TargetBoneName);
    }
}

void AMyPhysicsControlActor::NotifyActorOnClicked(FKey ButtonPressed)
{
    Super::NotifyActorOnClicked(ButtonPressed);

    // 当 Actor 被点击时，施加一个向上的冲击力
    if (PhysicsControlComponent && !TargetBoneName.IsNone())
    {
        FVector UpwardForce = FVector(0.f, 0.f, ImpulseStrength);
        // 伪代码： PhysicsControlComponent->AddImpulse(TargetBoneName, UpwardForce);
    }
}
```

## 模块依赖

使用 PhysicsControl 插件的功能，你的项目模块通常需要在 `.Build.cs` 文件中添加以下依赖（具体请参考插件各模块的 `Build.cs` 文件）：

| 模块 | 用途 |
|---|---|
| `PhysicsControl` | 运行时核心模块，包含物理控制组件和逻辑。 |
| `PhysicsControlEditor` | 提供 `UAnimGraphNode_RigidBodyWithControl` 的编辑器UI、细节面板自定义和调试视图。 |
| `PhysicsControlUncookedOnly` | 包含仅在未烘焙（开发）状态下需要的代码，如用于编辑器内预览的特定功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `6df5417c` | PhysicsControl: Clamp skeletal animation drive targets to joint limits to prevent spurious forces an | 骨骼动画驱动目标将被限制在关节极限内，防止产生异常的力和抖动。 |
| 2026-05-14 | `99441775` | Physics Control - Fix for Enable/DiableDisableCollisionBetweenBody when called on the same frame as | 修复了在同一帧调用启用/禁用刚体间碰撞功能时可能出现的错误。 |
| 2026-05-13 | `78406e38` | Control rig physics and Physics Control - clamp strength so that value < 0 don't cause unwanted beha | 对强度值进行钳制，防止负值导致意外行为。 |
| 2026-05-12 | `d5ffc351` | Add simple array versions of the Blueprint Enable/DisableCollisionBetweenBodies in PhysicsControl | 在蓝图中添加了针对多个刚体间碰撞启用/禁用的数组版本函数。 |
| 2026-05-12 | `647e07c7` | Add support for acceleration/force mode (a simple toggle) in physics control - control rig physics, | 为物理控制（包括控制绑物理）添加了加速度/力模式的支持（一个简单的切换开关）。 |

### 维护评价

PhysicsControl 插件于 **2026年5月12日** 从 Experimental 迁移到稳定版本，表明其已达到一定的成熟度。从近期的提交记录来看，插件在**发布后一周内持续收到了多个功能增强和重要的Bug修复**，涉及动画目标约束、碰撞控制稳定性和参数安全等多个方面。这表明该插件**正处于活跃的维护和迭代期**。由于其刚从实验版移出，目前暂无已知的长期未解决问题。对于需要精细物理动画控制的项目，**目前推荐使用此插件**。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl)
-   官方文档链接（`.uplugin` 中未提供）