# IK Rig

> 

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (UncookedOnly), `IKRigEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 是 UE5 的核心动画系统插件，提供两大功能：

1. **IK Rig**：在骨骼网格体上定义 IK 求解器栈（Solver Stack），通过配置 Goal（目标点）和多种求解器（Limb IK、Pole Solver、Body Mover、Set Transform、Stretch Limb 等），在运行时对骨骼姿态进行逆运动学修正。与 ControlRig 不同，IKRig 专注于**轻量级、数据驱动的 IK 求解**，无需编写蓝图或 C++ 逻辑即可配置完整的 IK 管线。

2. **IK Retargeter**：将动画从一个骨骼重定向到另一个骨骼。采用**模块化 Op 管线**架构，每个 Op 负责一个独立的重定向步骤（FK 链映射、IK 目标传递、骨盆运动、步幅变形、速度固定、地面约束等），可以自由组合和排序。解决了不同骨架比例、骨骼命名、层级结构之间的动画迁移问题。

## 使用场景

- 你有一个角色需要脚部 IK（脚踩地面）→ 用 IK Rig 定义 Foot IK Goal + Limb Solver
- 你有一套 Mixamo 动画要应用到 MetaHuman → 用 IK Retargeter 建立源/目标骨架映射
- 你需要将四足动物动画重定向到不同体型的四足角色 → 用 IK Retargeter 的 Chain Mapping + Stride Warping
- 你需要在运行时动态调整 IK 目标位置（如手抓物体）→ 用 `UIKRigComponent` 或 AnimNode 的 Goal 输入
- 你需要将动画从一个骨架批量导出到另一个骨架 → 用 IK Retargeter 的动画导出功能
- 你需要在 ControlRig 中使用 IK Rig 求解 → 用 `FRigUnit_IKRig` 节点

## 蓝图用法

### 核心节点

#### IK Rig Goal 设置（UIKRigComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetIKRigGoalPositionAndRotation` | 设置 IK Goal 的位置和旋转（组件空间），支持独立的 Position/Rotation Alpha | `UIKRigComponent` |
| `SetIKRigGoalTransform` | 用 FTransform 设置 IK Goal（组件空间），支持独立 Alpha | `UIKRigComponent` |
| `SetIKRigGoal` | 应用完整的 FIKRigGoal 结构体 | `UIKRigComponent` |
| `ClearAllGoals` | 清除组件上存储的所有 Goal | `UIKRigComponent` |

#### IK Goal Creator 接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddIKGoals` | 实现此接口以向 IK Rig AnimNode 提供自定义 Goal | `IIKGoalCreatorInterface` |

#### Retarget Op 控制器（蓝图/Python API）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSettings` / `SetSettings` | 获取/设置 Pelvis Motion Op 的设置 | `UIKRetargetPelvisMotionController` |
| `GetSettings` / `SetSettings` | 获取/设置 FK Chain Op 的设置 | `UIKRetargetFKChainController` |
| `GetSettings` / `SetSettings` | 获取/设置 IK Chain Op 的设置 | `UIKRetargetIKChainController` |
| `GetSettings` / `SetSettings` | 获取/设置 Stride Warping Op 的设置 | `UIKRetargetStrideWarpingController` |
| `GetSettings` / `SetSettings` | 获取/设置 Speed Planting Op 的设置 | `UIKRetargetSpeedPlantingController` |
| `GetSettings` / `SetSettings` | 获取/设置 Floor Constraint Op 的设置 | `UIKRetargetFloorConstraintController` |
| `GetSettings` / `SetSettings` | 获取/设置 Copy Base Pose Op 的设置 | `UIKRetargetCopyBasePoseController` |
| `GetSettings` / `SetSettings` | 获取/设置 Scale Source Op 的设置 | `UIKRetargetScaleSourceController` |
| `GetSettings` / `SetSettings` | 获取/设置 Additive Pose Op 的设置 | `UIKRetargetAdditivePoseController` |
| `GetSettings` / `SetSettings` | 获取/设置 Pin Bone Op 的设置 | `UIKRetargetPinBoneController` |
| `GetSettings` / `SetSettings` | 获取/设置 Filter Bone Op 的设置 | `UIKRetargetFilterBoneController` |
| `GetSettings` / `SetSettings` | 获取/设置 Curve Remap Op 的设置 | `UIKRetargetCurveRemapController` |
| `GetSettings` / `SetSettings` | 获取/设置 Root Motion Generator Op 的设置 | `UIKRetargetRootMotionController` |
| `GetSettings` / `SetSettings` | 获取/设置 Stretch Chain Op 的设置 | `UIKRetargetStretchChainController` |
| `GetSettings` / `SetSettings` | 获取/设置 Align Pole Vector Op 的设置 | `UIKRetargetAlignPoleVectorController` |

#### IK Rig Solver 控制器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetSolverSettings` / `SetSolverSettings` | 获取/设置 Limb Solver 设置 | `UIKRigLimbSolverController` |
| `GetSolverSettings` / `SetSolverSettings` | 获取/设置 Pole Solver 设置 | `UIKRigPoleSolverController` |
| `GetSolverSettings` / `SetSolverSettings` | 获取/设置 Body Mover 设置 | `UIKRigBodyMoverSolverController` |
| `GetSolverSettings` / `SetSolverSettings` | 获取/设置 Set Transform 设置 | `UIKRigSetTransformController` |
| `GetSolverSettings` / `SetSolverSettings` | 获取/设置 Stretch Limb 设置 | `UIKRigStretchLimbSolverController` |

### 使用示例（蓝图描述）

**示例 1：运行时设置 Foot IK Goal**

1. 在角色蓝图中添加 `UIKRigComponent`
2. 在 Tick 事件中，从脚部骨骼下方做射线检测获取地面位置
3. 调用 `SetIKRigGoalTransform`，GoalName 设为 "LeftFootGoal"，Transform 设为射线检测命中的世界空间位置（需转换为组件空间），PositionAlpha 设为 1.0

**示例 2：AnimGraph 中使用 IK Retarget**

1. 在目标角色的 AnimGraph 中添加 `Retarget Pose From Mesh` 节点
2. 设置 `RetargetFrom` 为 `CustomSkeletalMeshComponent`
3. 在蓝图的 `PreUpdate` 中将源角色的 SkeletalMeshComponent 赋值给 `SourceMeshComponent` 引脚
4. 设置 `IKRetargeterAsset` 为你的重定向资产

**示例 3：在 ControlRig 中使用 IK Rig**

1. 在 ControlRig 蓝图中添加 `IK Rig` 节点（FRigUnit_IKRig）
2. 将 `IKRigAsset` 引脚连接到你的 IKRigDefinition 资产
3. 在 `Goals` 数组中添加 `FIKRigGoalInput`，指定 GoalName 和 Transform

## C++ 用法

### 头文件引入

```cpp
#include "Rig/IKRigProcessor.h"
#include "Rig/IKRigDefinition.h"
#include "Rig/IKRigDataTypes.h"
#include "Retargeter/IKRetargetProcessor.h"
#include "Retargeter/IKRetargeter.h"
```

### 基本用法：IK Rig Processor

IKRigProcessor 是 IK Rig 的核心运行时类，用于在代码中驱动 IK 求解。

```cpp
// 来源: Engine/Plugins/Animation/IKRig/Source/IKRig/Public/Rig/IKRigProcessor.h

// 1. 创建 Processor 并初始化
FIKRigProcessor Processor;
FIKRigGoalContainer GoalContainer;
Processor.Initialize(IKRigDefinitionAsset, SkeletalMesh, GoalContainer);

// 2. 每帧设置输入姿态（全局空间）
TArray<FTransform> InputPose;
// ... 从骨骼网格体获取当前姿态
Processor.SetInputPoseGlobal(InputPose);

// 3. 设置 IK Goal
FIKRigGoal Goal;
Goal.Name = FName("LeftFootGoal");
Goal.Position = FVector(100.f, 0.f, 0.f);
Goal.PositionAlpha = 1.0f;
Goal.RotationAlpha = 0.0f;
Goal.PositionSpace = EIKRigGoalSpace::Component;
Processor.SetIKGoal(Goal);

// 4. 执行求解
Processor.Solve();

// 5. 获取输出姿态
TArray<FTransform> OutputPose;
Processor.GetOutputPoseGlobal(OutputPose);
```

### 基本用法：IK Retarget Processor

```cpp
// 来源: Engine/Plugins/Animation/IKRig/Source/IKRig/Public/Retargeter/IKRetargetProcessor.h

// 1. 创建 Retarget Processor
FIKRetargetProcessor RetargetProcessor;

// 2. 初始化（需要 Retargeter 资产、源/目标骨骼网格体）
FRetargetProfile Profile; // 可选的运行时覆盖设置
RetargetProcessor.Initialize(
    RetargeterAsset,
    SourceSkeletalMesh,
    TargetSkeletalMesh,
    Profile
);

// 3. 每帧设置源姿态并运行
TArray<FTransform> SourceGlobalPose;
// ... 获取源骨骼的全局姿态
TArray<FTransform> TargetGlobalPose;
RetargetProcessor.RunRetarget(
    SourceGlobalPose,
    TargetGlobalPose,
    DeltaTime
);

// 4. TargetGlobalPose 现在包含重定向后的目标姿态
```

### 进阶用法：自定义 Goal Creator 接口

```cpp
// 来源: Engine/Plugins/Animation/IKRig/Source/IKRig/Public/ActorComponents/IKRigInterface.h

// 实现 IIKGoalCreatorInterface 接口，让 Actor 向 IK Rig 提供 Goal
UCLASS()
class UMyGoalProvider : public UActorComponent, public IIKGoalCreatorInterface
{
    GENERATED_BODY()

public:
    virtual void AddIKGoals_Implementation(TMap<FName, FIKRigGoal>& OutGoals) override
    {
        FIKRigGoal HandGoal;
        HandGoal.Name = FName("RightHandGoal");
        HandGoal.Position = GetRightHandTargetLocation();
        HandGoal.PositionAlpha = 1.0f;
        HandGoal.PositionSpace = EIKRigGoalSpace::Component;
        OutGoals.Add(HandGoal.Name, HandGoal);
    }
};
```

### 进阶用法：运行时 Retarget Profile 覆盖

```cpp
// 来源: Engine/Plugins/Animation/IKRig/Source/IKRig/Public/Retargeter/IKRetargetProfile.h

// 创建 Retarget Profile 以在运行时覆盖 Op 设置
FRetargetProfile Profile;

// 覆盖 Pelvis Motion Op 的设置
FRetargetOpProfile PelvisOverride;
PelvisOverride.OpToApplySettingsTo = NAME_None; // 匹配所有使用该设置类型的 Op
FIKRetargetPelvisMotionOpSettings PelvisSettings;
PelvisSettings.TranslationAlpha = 0.5f;
PelvisSettings.RotationAlpha = 0.8f;
PelvisOverride.SettingsToApply = PelvisSettings;
Profile.RetargetOpProfiles.Add(PelvisOverride);

// 覆盖 Retarget Pose
Profile.bApplyTargetRetargetPose = true;
Profile.TargetRetargetPoseName = FName("CrouchPose");
```

## Demo 示例

### IK Rig Processor 最小示例

```cpp
// MyIKRigActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Rig/IKRigProcessor.h"
#include "MyIKRigActor.generated.h"

class USkeletalMeshComponent;
class UIKRigDefinition;

UCLASS()
class AMyIKRigActor : public AActor
{
    GENERATED_BODY()

public:
    AMyIKRigActor();

    UPROPERTY(EditAnywhere, Category = "IK Rig")
    TObjectPtr<UIKRigDefinition> IKRigAsset;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    FIKRigProcessor IKProcessor;
    bool bInitialized = false;
};
```

```cpp
// MyIKRigActor.cpp
#include "MyIKRigActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Rig/IKRigDefinition.h"

AMyIKRigActor::AMyIKRigActor()
{
    PrimaryActorTick.bCanEverTick = true;
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;
}

void AMyIKRigActor::BeginPlay()
{
    Super::BeginPlay();

    if (IKRigAsset && MeshComponent->GetSkeletalMeshAsset())
    {
        FIKRigGoalContainer EmptyGoals;
        IKProcessor.Initialize(IKRigAsset, MeshComponent->GetSkeletalMeshAsset(), EmptyGoals);
        bInitialized = true;
    }
}

void AMyIKRigActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (!bInitialized) return;

    // 从骨骼网格体获取当前姿态
    const TArray<FTransform>& ComponentSpacePose = MeshComponent->GetBoneSpaceTransforms();
    // 注意：实际使用中需要将组件空间转换为全局空间
    TArray<FTransform> GlobalPose;
    // ... 转换逻辑
    IKProcessor.SetInputPoseGlobal(GlobalPose);

    // 设置一个简单的脚部 IK Goal
    FIKRigGoal FootGoal;
    FootGoal.Name = FName("LeftFootGoal");
    FootGoal.Position = FVector(0.f, 0.f, 0.f); // 地面位置
    FootGoal.PositionAlpha = 1.0f;
    FootGoal.RotationAlpha = 0.0f;
    FootGoal.PositionSpace = EIKRigGoalSpace::Component;
    IKProcessor.SetIKGoal(FootGoal);

    // 求解
    IKProcessor.Solve();

    // 获取结果
    TArray<FTransform> OutputPose;
    IKProcessor.GetOutputPoseGlobal(OutputPose);

    // 将结果应用回骨骼网格体
    // ... 应用逻辑
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | IK Rig 的 ControlRig 集成（FRigUnit_IKRig 节点） |
| `FullBodyIK` | Full Body IK 求解器支持 |
| `StructUtils` | FInstancedStruct 用于多态 Op 设置存储 |
| `AnimGraphRuntime` | 动画图节点基类（FAnimNode_Base） |

## 维护状态

### 近期更新

```
- 7637f502422a [IK Retarget] Fixes issue causing broken retarget chains (regression from 46194288)
- 4ee7b05bff58 [IK Retarget] Better error checking for resolved chains to resolve crash potential.
- 4b1b55cc05d7 [IK Rig] Exposed IK Rig Control Rig node inputs to details panel.
```

第一条修复了重定向链断裂的回归问题；第二条增强了链解析的错误检查以防止崩溃；第三条将 IK Rig 的 ControlRig 节点输入暴露到 Details 面板。

### 维护评价

IKRig 是 UE5 动画系统的核心组件之一，由 Epic Games 直接维护。自 2020 年创建以来持续活跃更新，近期 commit 集中在 bug 修复和 API 改进。该插件**默认启用**，是 UE5 动画重定向和 IK 求解的官方推荐方案。从代码结构看，采用了模块化 Op 管线架构，版本序列化系统完善（FIKRigObjectVersion），表明设计成熟且考虑了长期维护。

**推荐使用**：这是 UE5 动画工作流的基础设施级插件，任何涉及 IK 求解或动画重定向的项目都应该使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/ik-rig-in-unreal-engine/)