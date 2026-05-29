# Physics Control

> Physically control static and skeletal meshes through the Physics Control Component and the Rigid Body With Control animation graph node.

| 属性 | 值 |
|---|---|
| 中文名 | 物理控制 |
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（物理控制资产、编辑器资产） |
| 模块 | `PhysicsControl` (Runtime), `PhysicsControlUncookedOnly` (UncookedOnly), `PhysicsControlEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2026-05-12 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl) | |

## 用途

Physics Control 提供了一套通过**命名物理弹簧/阻尼器驱动器**来精确控制物理刚体运动的框架。它解决了传统物理控制中的两大核心问题：

1. **角色物理动画的精细控制**：在骨骼网格体上创建、配置和管理物理控制（Controls）和刚体修改器（Body Modifiers），实现从完全动画到完全布娃娃之间的平滑过渡，以及肢体级别的物理驱动效果。
2. **物理驱动器的声明式管理**：通过命名控制（Named Controls）和集合（Sets）系统，批量创建、修改和销毁物理控制，使复杂的物理动画逻辑可以被高效地组织和重用。

**核心概念**：
- **Controls（物理控制）**：通过 Chaos 物理约束连接两个物体（或一个物体与世界），使用弹簧/阻尼器参数驱动物体运动到目标位置/朝向。
- **Body Modifiers（刚体修改器）**：控制物体的物理属性，如运动类型（静态/运动学/模拟）、重力倍率、碰撞类型等。
- **控制资产（Physics Control Asset）**：可复用的控制配置文件，支持继承和配置文件系统。

插件提供两种使用路径：
- `UPhysicsControlComponent`：附加到 Actor 上，以声明式方式管理物理控制。
- `FAnimNode_RigidBodyWithControl`：动画图节点，在动画蓝图中直接使用，基于 Immediate Physics 进行本地模拟。

## 使用场景

- 你需要实现**布娃娃混合**（Ragdoll Blend）—— 让角色部分肢体从动画过渡到物理驱动 → 使用 `FAnimNode_RigidBodyWithControl`
- 你需要让角色的**特定部位跟随物理目标**（如武器后坐力导致手臂回弹）→ 使用 `UPhysicsControlComponent` 创建 Target 控制
- 你需要在动画中实现**惯性效果**（如角色急停时身体继续前倾）→ 配置 `ExternalForce` 和 `SimSpaceSettings`
- 你需要批量控制角色各肢体的物理行为，且不同肢体使用不同参数 → 利用 **Limb Setup** 和 **控制集合（Sets）** 系统
- 你需要在运行时切换不同的物理动画配置（如行走/奔跑/跳跃的不同物理参数）→ 使用 **Physics Control Asset** 的 **Profile** 系统
- 你需要禁用骨骼间的碰撞（如防止大腿与小腿在布娃娃中互相穿插）→ 使用 `DisableCollisionBetweenBodies`

## 蓝图用法

### 核心节点 — 物理控制组件

以下节点位于 `UPhysicsControlComponent`，按功能分组：

#### 控制创建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateControl` | 为两个网格体组件之间创建单个物理控制（自动生成名称） | `UPhysicsControlComponent` |
| `CreateNamedControl` | 用指定名称创建物理控制（名称已存在则失败） | `UPhysicsControlComponent` |
| `CreateControlsFromSkeletalMeshBelow` | 从骨骼网格体的指定骨骼开始，向下递归创建批量控制 | `UPhysicsControlComponent` |
| `CreateControlsFromSkeletalMesh` | 为指定骨骼名称数组创建批量控制 | `UPhysicsControlComponent` |
| `CreateControlsFromSkeletalMeshAndConstraintProfile` | 使用约束配置文件参数为骨骼创建 ParentSpace 控制 | `UPhysicsControlComponent` |
| `CreateControlsFromLimbBones` | 从肢体骨骼映射表创建批量控制（按肢体分组） | `UPhysicsControlComponent` |
| `GetLimbBonesFromSkeletalMesh` | 分析骨骼网格体，返回肢体名称到骨骼列表的映射 | `UPhysicsControlComponent` |

#### 控制数据修改

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetControlData` | 修改单个控制的强度/阻尼等参数 | `UPhysicsControlComponent` |
| `SetControlDatas` | 批量修改多个控制的参数 | `UPhysicsControlComponent` |
| `SetControlDatasInSet` | 修改某个集合内所有控制的参数 | `UPhysicsControlComponent` |
| `SetControlLinearData` | 设置控制的线性运动参数（强度、阻尼比、额外阻尼、最大力） | `UPhysicsControlComponent` |
| `SetControlSparseData` | 使用稀疏数据修改控制（仅更新指定字段） | `UPhysicsControlComponent` |
| `SetControlMultiplier` | 使用乘数修改控制参数（支持方向性强度） | `UPhysicsControlComponent` |
| `SetControlEnabled` | 启用/禁用单个控制 | `UPhysicsControlComponent` |
| `SetControlsEnabledInSet` | 启用/禁用某个集合内所有控制 | `UPhysicsControlComponent` |

#### 控制目标设置

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetControlTarget` | 设置单个控制的目标位置和朝向 | `UPhysicsControlComponent` |
| `SetControlTargets` | 批量设置多个控制的目标 | `UPhysicsControlComponent` |

#### 刚体修改器操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateBodyModifier` | 创建刚体修改器（控制物体的运动类型、重力等） | `UPhysicsControlComponent` |
| `CreateNamedBodyModifier` | 用指定名称创建刚体修改器 | `UPhysicsControlComponent` |
| `SetBodyModifierData` | 修改刚体修改器的参数 | `UPhysicsControlComponent` |
| `SetKinematicTarget` | 设置运动学物体的目标变换 | `UPhysicsControlComponent` |

#### 生命周期管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DestroyControl` | 销毁单个控制或某个集合内的控制 | `UPhysicsControlComponent` |
| `DestroyControlsInSet` | 销毁某个集合内的所有控制 | `UPhysicsControlComponent` |
| `DestroyAllControlsAndBodyModifiers` | 销毁所有控制和刚体修改器 | `UPhysicsControlComponent` |
| `UpdateTargetCaches` | 手动更新目标缓存（用于自定义 Tick 流程） | `UPhysicsControlComponent` |
| `UpdateControls` | 手动更新控制和修改器（用于自定义 Tick 流程） | `UPhysicsControlComponent` |

### 核心节点 — 蓝图函数库

以下节点位于 `UPhysicsControlBPLibrary`：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddControlParameters` | 向参数容器添加单个控制参数 | `UPhysicsControlBPLibrary` |
| `AddMultipleControlParameters` | 向参数容器添加一组控制参数 | `UPhysicsControlBPLibrary` |
| `AddModifierParameters` | 向参数容器添加单个修改器参数 | `UPhysicsControlBPLibrary` |
| `BlendParameters` | 线性插值两组参数 | `UPhysicsControlBPLibrary` |
| `BlendControlParametersThroughSet` | 沿骨骼列表从起始参数渐变到结束参数 | `UPhysicsControlBPLibrary` |
| `ConvertToRigidBodyWithControl` | 从 AnimNodeReference 转换为 RBwC 节点引用 | `UPhysicsControlBPLibrary` |
| `GetControlNamesInSet` | 获取指定集合中的控制名称列表 | `UPhysicsControlBPLibrary` |
| `DisableCollisionBetweenBodies` | 禁用两个物理体之间的碰撞 | `UPhysicsControlBPLibrary` |
| `EnableCollisionBetweenBodies` | 恢复两个物理体之间的碰撞 | `UPhysicsControlBPLibrary` |
| `DisableCollisionBetweenBodyArrays` | 批量禁用物理体数组间的碰撞 | `UPhysicsControlBPLibrary` |
| `EnableCollisionBetweenBodyArrays` | 批量恢复物理体数组间的碰撞 | `UPhysicsControlBPLibrary` |

### 使用示例（蓝图描述）

**示例 1：创建角色肢体控制**

1. 在角色 Actor 上添加 `UPhysicsControlComponent`
2. 调用 `GetLimbBonesFromSkeletalMesh`，传入 `SkeletalMeshComponent` 和 `LimbSetupData`（定义肢体：左右臂、左右腿、脊柱），获取 `TMap<FName, FPhysicsControlLimbBones>` 肢体骨骼映射
3. 调用 `CreateControlsFromLimbBones`，传入肢体骨骼映射和 `EPhysicsControlType::ParentSpace` 创建控制
4. 返回的 `TMap<FName, FPhysicsControlNames>` 包含每个肢体的控制名称
5. 使用 `SetControlDatasInSet` 设置 "ArmLeft" 集合内所有控制的强度参数
6. 使用 `SetControlsEnabledInSet` 按需启用/禁用各肢体的物理控制

**示例 2：使用动画图节点实现布娃娃混合**

1. 在动画蓝图中添加 `Rigid Body With Control` 节点（即 `FAnimNode_RigidBodyWithControl`）
2. 在节点细节面板中设置 `OverridePhysicsAsset`（可选）和 `SimulationSpace`
3. 设置 `CharacterSetupData` 中的肢体配置
4. 将 `ControlAndModifierParameters` 引脚连接到蓝图逻辑，运行时动态调整控制参数
5. 通过 `ConvertToRigidBodyWithControl` 蓝图节点获取 RBwC 引用后，调用 `GetControlNamesInSet` 查询集合中的控制名称
6. 使用 `ControlTargets` 引脚设置目标位置和朝向

**示例 3：禁用骨骼间碰撞**

1. 在事件图表中调用 `DisableCollisionBetweenBodies`
2. 传入 `SkeletalMeshComponent`、`FName("thigh_l")` 和 `SkeletalMeshComponent`、`FName("calf_l")`
3. 返回 `true` 表示成功
4. 在需要时调用 `EnableCollisionBetweenBodies` 恢复碰撞

## C++ 用法

### 头文件引入

```cpp
#include "PhysicsControlComponent.h"
#include "AnimNode_RigidBodyWithControl.h"
#include "PhysicsControlData.h"
#include "PhysicsControlBPLibrary.h"
```

### 基本用法 — 创建和控制物理体

```cpp
// 在 Actor 的 BeginPlay 中创建物理控制组件
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建物理控制组件
    UPhysicsControlComponent* ControlComp = NewObject<UPhysicsControlComponent>(this);
    ControlComp->RegisterComponent();

    // 为两个网格体之间创建一个控制
    FPhysicsControlData ControlData;
    ControlData.LinearStrength = 1000.0f;
    ControlData.LinearDampingRatio = 1.0f;  // 临界阻尼
    ControlData.AngularStrength = 500.0f;
    ControlData.AngularDampingRatio = 1.0f;

    FPhysicsControlTarget Target;
    Target.TargetPosition = FVector(0, 0, 100);
    Target.bUseSkeletalAnimation = false;

    FName ControlName = ControlComp->CreateControl(
        nullptr,                    // ParentComponent（世界空间）
        NAME_None,                  // ParentBoneName
        MeshComponent,              // ChildComponent
        FName("spine_01"),          // ChildBoneName
        ControlData,
        Target,
        FName("MySet"),             // Set 名称
        TEXT("Test_")               // 名称前缀
    );
}
```

### 基本用法 — 为骨骼网格体创建批量控制

```cpp
// 基于约束配置文件为骨骼创建 ParentSpace 控制
TArray<FName> CreatedControls = ControlComp->CreateControlsFromSkeletalMeshAndConstraintProfileBelow(
    SkeletalMeshComponent,
    FName("spine_01"),    // 从脊柱开始
    true,                 // 包含自身
    FName("Default"),     // 约束配置文件名称
    FName("Spine"),       // 集合名称
    true                  // 立即启用
);

// 修改集合中所有控制的强度
ControlComp->SetControlDatasInSet(FName("Spine"), ControlData);
```

### 进阶用法 — 使用肢体系统创建角色控制

```cpp
// 1. 定义肢体设置
TArray<FPhysicsControlLimbSetupData> LimbSetupData;

FPhysicsControlLimbSetupData& LeftArm = LimbSetupData.AddDefaulted_GetRef();
LeftArm.LimbName = FName("ArmLeft");
LeftArm.StartBone = FName("upperarm_l");
LeftArm.bIncludeParentBone = false;
LeftArm.bCreateWorldSpaceControls = true;
LeftArm.bCreateParentSpaceControls = true;
LeftArm.bCreateBodyModifiers = true;

FPhysicsControlLimbSetupData& Spine = LimbSetupData.AddDefaulted_GetRef();
Spine.LimbName = FName("Spine");
Spine.StartBone = FName("spine_01");
Spine.bIncludeParentBone = true;  // 包含骨盆

// 2. 获取肢体骨骼映射
TMap<FName, FPhysicsControlLimbBones> LimbBones = 
    ControlComp->GetLimbBonesFromSkeletalMesh(SkeletalMeshComponent, LimbSetupData);

// 3. 创建批量控制
FPhysicsControlNames AllControls;
FPhysicsControlData WorldSpaceData;
WorldSpaceData.LinearStrength = 500.0f;
WorldSpaceData.AngularStrength = 300.0f;

TMap<FName, FPhysicsControlNames> LimbControls = 
    ControlComp->CreateControlsFromLimbBones(
        AllControls,
        LimbBones,
        EPhysicsControlType::WorldSpace,
        WorldSpaceData,
        nullptr,    // WorldComponent
        NAME_None,  // WorldBoneName
        TEXT("Char_")
    );

// 4. 按肢体设置不同的参数
FPhysicsControlData StrongData;
StrongData.LinearStrength = 2000.0f;
ControlComp->SetControlDatasInSet(FName("Char_ArmLeft"), StrongData);
```

### 进阶用法 — 自定义 Tick 流程

```cpp
// 禁用组件自动 Tick，手动控制更新时机
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 1. 先确保骨骼网格体已更新（通过 Tick Prerequisite 保证）
    
    // 2. 更新目标缓存（从动画读取目标）
    ControlComp->UpdateTargetCaches(DeltaTime);

    // 3. 在此处可以读取缓存的目标，进行自定义逻辑
    // 例如：根据当前目标修改某些控制参数

    // 4. 应用控制到物理
    ControlComp->UpdateControls(DeltaTime);
}
```

## Demo 示例

### 头文件

```cpp
// MyPhysicsControlActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "PhysicsControlComponent.h"
#include "MyPhysicsControlActor.generated.h"

UCLASS()
class AMyPhysicsControlActor : public AActor
{
    GENERATED_BODY()

public:
    AMyPhysicsControlActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // 要控制的骨骼网格体组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> SkeletalMesh;

    // 物理控制组件
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UPhysicsControlComponent> PhysicsControl;

    // 控制名称缓存
    UPROPERTY()
    TMap<FName, FPhysicsControlNames> LimbControls;

    UPROPERTY()
    TArray<FName> AllControlNames;

    // 是否启用物理混合
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bEnablePhysicsBlend = false;

    // 物理混合权重（0=纯动画，1=纯物理）
    UPROPERTY(EditAnywhere, BlueprintReadWrite, meta = (ClampMin = "0", ClampMax = "1"))
    float PhysicsBlendWeight = 0.5f;
};
```

### 源文件

```cpp
// MyPhysicsControlActor.cpp
#include "MyPhysicsControlActor.h"
#include "PhysicsControlData.h"
#include "PhysicsControlLimbData.h"

AMyPhysicsControlActor::AMyPhysicsControlActor()
{
    PrimaryActorTick.bCanEverTick = true;

    SkeletalMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("SkeletalMesh"));
    RootComponent = SkeletalMesh;

    PhysicsControl = CreateDefaultSubobject<UPhysicsControlComponent>(TEXT("PhysicsControl"));
    PhysicsControl->SetupAttachment(RootComponent);
}

void AMyPhysicsControlActor::BeginPlay()
{
    Super::BeginPlay();

    if (!SkeletalMesh || !PhysicsControl)
    {
        return;
    }

    // 定义肢体
    TArray<FPhysicsControlLimbSetupData> LimbSetupData;

    FPhysicsControlLimbSetupData& SpineLimb = LimbSetupData.AddDefaulted_GetRef();
    SpineLimb.LimbName = FName("Spine");
    SpineLimb.StartBone = FName("spine_01");
    SpineLimb.bIncludeParentBone = true;
    SpineLimb.bCreateWorldSpaceControls = true;
    SpineLimb.bCreateParentSpaceControls = true;
    SpineLimb.bCreateBodyModifiers = true;

    FPhysicsControlLimbSetupData& LeftArmLimb = LimbSetupData.AddDefaulted_GetRef();
    LeftArmLimb.LimbName = FName("ArmLeft");
    LeftArmLimb.StartBone = FName("upperarm_l");
    LeftArmLimb.bCreateWorldSpaceControls = true;
    LeftArmLimb.bCreateParentSpaceControls = true;
    LeftArmLimb.bCreateBodyModifiers = true;

    FPhysicsControlLimbSetupData& RightArmLimb = LimbSetupData.AddDefaulted_GetRef();
    RightArmLimb.LimbName = FName("ArmRight");
    RightArmLimb.StartBone = FName("upperarm_r");
    RightArmLimb.bCreateWorldSpaceControls = true;
    RightArmLimb.bCreateParentSpaceControls = true;
    RightArmLimb.bCreateBodyModifiers = true;

    // 获取肢体骨骼
    TMap<FName, FPhysicsControlLimbBones> LimbBones =
        PhysicsControl->GetLimbBonesFromSkeletalMesh(SkeletalMesh, LimbSetupData);

    // 使用约束配置文件创建控制
    LimbControls = PhysicsControl->CreateControlsFromLimbBonesAndConstraintProfile(
        AllControlNames,
        LimbBones,
        FName("Default"),   // 约束配置文件
        true                // 立即启用
    );
}

void AMyPhysicsControlActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bEnablePhysicsBlend)
    {
        // 设置所有控制的强度乘数来实现动画/物理混合
        FPhysicsControlMultiplier Multiplier;
        Multiplier.LinearStrengthMultiplier = FVector(PhysicsBlendWeight);
        Multiplier.AngularStrengthMultiplier = FVector(PhysicsBlendWeight);

        PhysicsControl->SetControlMultipliersInSet(
            FName("All"),
            Multiplier,
            true   // 启用控制
        );
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

PhysicsControl 依赖于 Chaos 物理系统（Immediate Physics），但这是引擎内置模块，无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `6df5417c` | PhysicsControl: Clamp skeletal animation drive targets to joint limits to prevent spurious forces an | 限制动画驱动目标在关节角度范围内，防止异常力 |
| 2026-05-14 | `99441775` | Physics Control - Fix for Enable/DiableDisableCollisionBetweenBody when called on the same frame as | 修复同一帧创建控制时碰撞禁用/启用的错误 |
| 2026-05-13 | `78406e38` | Control rig physics and Physics Control - clamp strength so that value < 0 don't cause unwanted beha | 限制强度值不为负，防止产生意外物理行为 |
| 2026-05-12 | `d5ffc351` | Add simple array versions of the Blueprint Enable/DisableCollisionBetweenBodies in PhysicsControl | 添加碰撞控制的数组批量版本蓝图接口 |
| 2026-05-12 | `647e07c7` | Add support for acceleration/force mode (a simple toggle) in physics control - control rig physics, | 添加加速度/力模式切换，影响控制驱动行为 |

### 维护评价

PhysicsControl 是一个**全新的插件**（2026 年 5 月从 Experimental 迁移到正式目录），目前处于**快速迭代期**。

- ✅ **由 Epic Games 官方维护**，质量有保障
- ✅ 迁移后一周内持续收到实质性功能更新和 bug 修复
- ✅ API 设计成熟，包含完整的 Blueprint 支持和编辑器工具
- ✅ 与 Control Rig 物理系统深度集成，是 Epic 物理动画方案的核心组件
- ⚠️ 由于刚从 Experimental 迁移，API 可能仍会有小幅调整
- ⚠️ 部分函数标记了 `UE_DEPRECATED(5.8, ...)`，说明 API 正在快速演进

**推荐使用**：对于需要精确物理控制的动画系统（布娃娃混合、物理驱动肢体、惯性效果等），这是官方推荐的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/PhysicsControl)
- [官方文档]()（暂无）
- [测试用例]()（暂无发现独立测试文件）