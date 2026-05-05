# Animation Warping

> Framework for animation and pose warping. This plugin includes Stride, Orientation, and Slope Warping alongside the Root Motion Delta animation attribute.

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationWarpingRuntime` (Runtime), `AnimationWarpingEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-12-04 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationWarping) | |

## 用途

Animation Warping 是一套**动画变形框架**，用于在运行时程序化地调整动画姿态，使角色的运动与游戏逻辑（如速度、朝向、地面坡度）精确匹配。

核心问题：预录制的动画资产是静态的，无法完美适应所有运行时条件。例如，一个向前跑步的动画无法自动适配角色实际移动速度的变化、转向、上下坡等情况。Animation Warping 通过程序化地**拉伸步幅、旋转下半身、调整骨盆高度、对齐脚部到地面**等手段，在不创建额外动画资产的情况下解决这些问题。

该插件依赖 Root Motion Delta 动画属性（`IAnimRootMotionProvider`），在 `Graph` 模式下可自动从动画图的 root motion 数据驱动变形参数。

### 节点总览

该插件提供 **7 个动画图节点** + **1 个蓝图函数库** + **1 个动画修改器**：

| 节点 | 功能 | 标记 |
|---|---|---|
| **Orientation Warping** | 上半身保持朝向，下半身旋转匹配移动方向 | — |
| **Stride Warping** | 根据移动速度拉伸/压缩步幅 | — |
| **Slope Warping** | 使脚部和骨盆适应斜坡地形 | Experimental |
| **Foot Placement** | 高级脚部固定：锁定脚部位置、骨盆调整、地面追踪 | Experimental |
| **Offset Root Bone** | 偏移根骨骼位置，解耦 mesh component 与根骨骼变换 | Experimental |
| **Steering** | 通过缩放 root motion 旋转 + 弹簧修正来转向目标朝向 | — |
| **Override Root Motion** | 覆盖 root motion 速度 | Experimental |
| **Warp Test** | 测试用节点，按时间循环传送到指定变换 | Experimental |

## 使用场景

- 你的角色需要根据移动速度调整跑步步幅，但只有单一速度的动画 → 用 **Stride Warping**
- 角色在转向时下半身应该跟随移动方向旋转，上半身保持瞄准方向 → 用 **Orientation Warping**
- 角色在上下坡时脚部需要贴合地面 → 用 **Slope Warping** 或 **Foot Placement**
- 你需要将角色的根骨骼偏移（如实现"滑步"效果或角色与 capsule 的分离） → 用 **Offset Root Bone**
- 你需要根据目标朝向自动缩放动画的转向量 → 用 **Steering**

## 蓝图用法

### 核心节点

所有动画图节点通过 AnimGraph（动画蓝图编辑器）使用，而非直接在事件图表中使用。蓝图函数库 `UAnimationWarpingLibrary` 提供以下辅助函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOffsetRootTransform` | 获取 OffsetRootBone 节点当前的世界空间根骨骼变换 | `UAnimationWarpingLibrary` |
| `GetCurveValueFromAnimation` | 从动画序列中按时间采样曲线值 | `UAnimationWarpingLibrary` |
| `GetFloatValueFromCurve` | 从 UCurveFloat 资产中按时间采样值 | `UAnimationWarpingLibrary` |
| `GetVectorValueFromCurve` | 从 UCurveVector 资产中按时间采样向量值 | `UAnimationWarpingLibrary` |

所有函数均标记为 `BlueprintThreadSafe`，可在动画线程安全调用。

### 动画图节点属性（AnimGraph 用法）

#### Orientation Warping 属性

| 属性 | 说明 |
|---|---|
| `Mode` | 评估模式：`Manual`（手动指定角度）或 `Graph`（自动从 root motion 计算） |
| `OrientationAngle` | Manual 模式下的变形角度（度） |
| `LocomotionAngle` | 角色移动角度，Graph 模式下用于计算朝向差值 |
| `LocomotionDirection` | 移动方向向量（世界空间），设置后自动计算 LocomotionAngle |
| `SpineBones` | 脊椎骨骼数组，变形会沿这些骨骼渐进分配旋转 |
| `IKFootRootBone` / `IKFootBones` | IK 脚部骨骼，用于补偿脚部旋转 |
| `RotationAxis` | 旋转轴（默认 Z 轴） |
| `RotationInterpSpeed` | 旋转插值速度，> 0 时启用平滑 |
| `DistributedBoneOrientationAlpha` | 身体 vs 脚部的旋转分配权重 |
| `MinRootMotionSpeedThreshold` | 最低 root motion 速度阈值，低于此值不执行变形 |
| `LocomotionAngleDeltaThreshold` | 防止过度旋转的阈值（默认 90°） |
| `WarpingSpace` | 变形空间：`ComponentTransform`、`RootBoneTransform`、`CustomTransform` |

#### Stride Warping 属性

| 属性 | 说明 |
|---|---|
| `Mode` | 评估模式：`Manual` 或 `Graph` |
| `StrideDirection` | 组件空间步幅方向（默认 Forward） |
| `StrideScale` | Manual 模式下的步幅缩放值 |
| `LocomotionSpeed` | Graph 模式下的移动速度，自动计算 StrideScale = LocomotionSpeed / RootMotionSpeed |
| `PelvisBone` | 骨盆骨骼 |
| `IKFootRootBone` | IK 脚部根骨骼 |
| `FootDefinitions` | 脚部定义数组（IK 骨骼、FK 骨骼、大腿骨骼） |
| `FloorNormalDirection` | 地面法线方向 |
| `GravityDirection` | 重力方向 |
| `PelvisIKFootSolver` | 骨盆 IK 拉下求解器 |
| `StrideScaleModifier` | 步幅缩放的钳制/插值修改器 |

#### Slope Warping 属性

| 属性 | 说明 |
|---|---|
| `IKFootRootBone` | IK 脚部根骨骼 |
| `PelvisBone` | 骨盆骨骼 |
| `FeetDefinitions` | 每只脚的定义（IK 骨骼、FK 骨骼、腿骨骼数、脚尺寸） |
| `PelvisOffsetInterpolator` | 骨盆偏移弹簧插值器 |
| `FloorNormalInterpolator` | 地面法线弹簧插值器 |
| `FloorOffsetInterpolator` | 地面偏移弹簧插值器 |
| `GravityDir` | 重力方向 |
| `MaxStepHeight` | 最大台阶高度 |
| `bPullPelvisDown` | 是否将骨盆向下拉 |
| `bKeepMeshInsideOfCapsule` | 是否保持 mesh 在 capsule 内 |

#### Foot Placement 属性

Foot Placement 是最复杂的节点，包含以下设置组：

| 设置组 | 关键属性 |
|---|---|
| **Leg Definitions** | `FKFootBone`、`IKFootBone`、`BallBone`、`NumBonesInLimb`、`SpeedCurveName`、`DisableLockCurveName` |
| **Plant Settings** | `SpeedThreshold`、`DistanceToGround`、`LockType`（Unlocked/PivotAroundBall/PivotAroundAnkle/LockRotation）、`UnplantRadius`、`MaxExtensionRatio` |
| **Pelvis Settings** | `MaxOffset`、`LinearStiffness`、`LinearDamping`、`HorizontalRebalancingWeight`、`HeelLiftRatio`、`PelvisHeightMode`（AllLegs/AllPlantedFeet/FrontPlantedFeetUphill）、`ActorMovementCompensationMode` |
| **Interpolation Settings** | `UnplantLinearStiffness`/`Damping`、`FloorLinearStiffness`/`Damping`、`SeparationStiffness`/`Damping` |
| **Trace Settings** | `StartOffset`、`EndOffset`、`SweepRadius`、`SimpleTraceChannel`、`ComplexTraceChannel`、`MaxGroundPenetration` |
| **PlantSpeedMode** | `Manual`（使用曲线名）或 `Graph`（从 root motion 计算） |

#### Offset Root Bone 属性

| 属性 | 说明 |
|---|---|
| `TranslationMode` / `RotationMode` | 偏移模式：`Accumulate`、`Interpolate`、`LockOffsetAndConsumeAnimation`、`Release` 等 |
| `TranslationHalflife` / `RotationHalfLife` | 平移/旋转偏移的半衰期（越小越快收敛） |
| `MaxTranslationError` / `MaxRotationError` | 最大偏移限制 |
| `TranslationDelta` / `RotationDelta` | 每帧增量 |
| `bOnGround` / `GroundNormal` | 地面投影设置 |
| `CollisionTestingMode` | 碰撞检测模式：`Disabled`、`ShrinkMaxTranslation`、`PlanarCollision` |

#### Steering 属性

| 属性 | 说明 |
|---|---|
| `TargetOrientation` | 目标朝向四元数 |
| `ProceduralTargetTime` | 程序化修正的时间尺度（秒） |
| `AnimatedTargetTime` | 动画前瞻时间（秒），用于采样 root motion 预测 |
| `CurrentAnimAsset` / `CurrentAnimAssetTime` | 当前动画资产和播放时间 |
| `MinScaleRatio` / `MaxScaleRatio` | Root motion 缩放范围 |
| `DisableSteeringBelowSpeed` | 低于此速度禁用转向 |
| `bMirrored` / `MirrorDataTable` | 镜像动画支持 |

## C++ 用法

### 头文件引入

```cpp
// Runtime 模块 - 动画节点
#include "BoneControllers/AnimNode_OrientationWarping.h"
#include "BoneControllers/AnimNode_StrideWarping.h"
#include "BoneControllers/AnimNode_SlopeWarping.h"
#include "BoneControllers/AnimNode_FootPlacement.h"
#include "BoneControllers/AnimNode_OffsetRootBone.h"
#include "BoneControllers/AnimNode_Steering.h"
#include "BoneControllers/AnimNode_OverrideRootMotion.h"

// 蓝图函数库
#include "AnimationWarpingLibrary.h"

// 类型定义
#include "AnimationWarpingTypes.h"
```

### 基本用法

动画节点在 C++ 中通过 `UAnimInstance` 子类或自定义 AnimNode 使用。以下示例展示如何在自定义 AnimInstance 中引用 Orientation Warping 节点：

```cpp
// 在自定义 AnimInstance 中获取 OffsetRootBone 的变换
// 来源: AnimationWarpingLibrary.h

#include "AnimationWarpingLibrary.h"

void UMyAnimInstance::SomeFunction()
{
    // 在 AnimBP 中使用蓝图函数库获取根骨骼偏移
    // 通过 FAnimNodeReference 获取节点引用
    FTransform OffsetTransform = UAnimationWarpingLibrary::GetOffsetRootTransform(NodeReference);
    
    // 从动画序列中采样曲线值
    float CurveValue;
    bool bFound = UAnimationWarpingLibrary::GetCurveValueFromAnimation(
        MyAnimSequence, FName("FootSpeed"), CurrentTime, CurveValue);
}
```

### 进阶用法

#### Orientation Warping + Offset Root Bone 组合

当使用 OffsetRootBone 节点时，OrientationWarping 需要将 `WarpingSpace` 设置为 `RootBoneTransform`，以便基于偏移后的根骨骼变换进行变形：

```cpp
// 在动画图中，OrientationWarping 会通过 FRootOffsetProvider 消息
// 从 OffsetRootBone 节点获取根骨骼变换
// 来源: AnimNode_OffsetRootBone.h - FRootOffsetProvider

// OrientationWarping 在 UpdateInternal 中检查消息:
// if (WarpingSpace == EOrientationWarpingSpace::RootBoneTransform)
// {
//     if (auto* RootOffsetProvider = Context.GetMessage<FRootOffsetProvider>())
//         WarpingSpaceTransform = RootOffsetProvider->GetRootTransform();
// }
```

#### Foot Placement 的脚部锁定系统

Foot Placement 使用速度曲线和弹簧插值来决定何时锁定/解锁脚部：

```cpp
// 脚部定义中的关键曲线
// 来源: AnimNode_FootPlacement.h - FFootPlacemenLegDefinition

// SpeedCurveName: 表示脚部速度的动画曲线名
//   - 速度低于 SpeedThreshold 时脚部被认为"已固定"
//   - Graph 模式下自动从 root motion 计算

// DisableLockCurveName: 控制锁定 alpha 的曲线
//   - 允许精确禁用锁定，而非依赖程序化机制

// DisableLegCurveName: 禁用该腿的 FootPlacement 效果
```

#### Steering 节点的双修正机制

```cpp
// Steering 通过两种技术组合修正 root motion:
// 来源: AnimNode_Steering.h 注释
//
// 1) 缩放动画中的 root motion 旋转
//    - 使用 AnimatedTargetTime 前瞻采样预期旋转
//    - 与 TargetOrientation 比较计算缩放比
//    - 缩放比被 Clamp(MinScaleRatio, MaxScaleRatio)
//
// 2) 添加额外的弹簧修正
//    - 使用 ProceduralTargetTime 作为时间尺度
//    - 处理缩放后剩余的误差
```

## Demo 示例

### 最小 Stride Warping AnimNode 使用

```cpp
// MyAnimInstance.h
#pragma once
#include "Animation/AnimInstance.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 从角色移动组件获取速度，连接到 AnimBP 中 StrideWarping 节点的 LocomotionSpeed pin
    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    float LocomotionSpeed = 0.f;

    // 从角色胶囊体获取移动方向，连接到 OrientationWarping 的 LocomotionDirection pin
    UPROPERTY(BlueprintReadOnly, Category = "Animation")
    FVector LocomotionDirection = FVector::ZeroVector;
};
```

```cpp
// MyCharacter.cpp
void AMyCharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    if (UMyAnimInstance* AnimInst = Cast<UMyAnimInstance>(GetMesh()->GetAnimInstance()))
    {
        // 获取移动速度
        AnimInst->LocomotionSpeed = GetVelocity().Size();
        
        // 获取移动方向
        AnimInst->LocomotionDirection = GetVelocity().GetSafeNormal();
    }
}
```

```
// AnimBP 节点连接说明:
//
// [State Machine] → [Orientation Warping] → [Stride Warping] → [Output Pose]
//
// Orientation Warping 设置:
//   Mode = Graph
//   LocomotionDirection = (连接到 AnimInstance 的 LocomotionDirection)
//   SpineBones = [spine_01, spine_02, spine_03]
//   IKFootRootBone = ik_foot_root
//   IKFootBones = [ik_foot_l, ik_foot_r]
//   RotationInterpSpeed = 10
//
// Stride Warping 设置:
//   Mode = Graph
//   LocomotionSpeed = (连接到 AnimInstance 的 LocomotionSpeed)
//   PelvisBone = pelvis
//   IKFootRootBone = ik_foot_root
//   FootDefinitions = [{IK: ik_foot_l, FK: foot_l, Thigh: thigh_l},
//                      {IK: ik_foot_r, FK: foot_r, Thigh: thigh_r}]
```

### Build.cs 依赖

```csharp
// 如果你的模块需要使用 AnimationWarping 的运行时功能:
PublicDependencyModuleNames.AddRange(new string[]
{
    "AnimationWarpingRuntime",
    "AnimGraphRuntime",
    "AnimationCore",
});
```

## 模块依赖

### AnimationWarpingRuntime

你的模块要使用运行时动画节点，需要依赖：

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 动画核心类型（FBoneReference 等） |
| `AnimGraphRuntime` | 动画图运行时（FAnimNode_SkeletalControlBase 等基类） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎基础（UCurveFloat 等） |

### AnimationWarpingEditor

插件自身的编辑器模块额外依赖：

| 模块 | 用途 |
|---|---|
| `AnimGraph` | 动画图编辑器节点基类 |
| `AnimationModifiers` | 动画修改器框架 |
| `AnimationBlueprintLibrary` | 动画蓝图工具库 |
| `AnimationModifierLibrary` | 动画修改器库（插件依赖） |
| `SlateCore` | 编辑器 UI |
| `BlueprintGraph` / `UnrealEd` / `Kismet` | 编辑器编译框架 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-10-01 | `c6acf9c9` | 由 roland.munguia 提交的更新（内容未详述） |
| 2025-09-23 | `500535bc` | SpringMath API 调整：重命名 SpringDamper → CriticalSpringDamper，添加文档 |
| 2025-09-12 | `70c9e98a` | SpringMath API 更新：标记为 Experimental，统一命名，添加蓝图库 |
| 2025-08-08 | `97776670` | 重命名 AnimationMath → SpringMath，添加速度弹簧和角色预测函数 |
| 2025-06-26 | `a2e75189` | 为源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏 |

### 维护评价

- **创建时间**: 2021 年 12 月，约 4 年历史
- **维护状态**: **活跃维护** — 2025 年有多次实质性更新，涉及 SpringMath API 重构和底层改进
- **关键维护者**: Epic Games 内部团队（roland.munguia 等）
- **实验性节点**: SlopeWarping、FootPlacement、OffsetRootBone、OverrideRootMotion、WarpTest 标记为 `Experimental`，意味着 API 可能在未来版本中变更
- **非实验性节点**: OrientationWarping 和 StrideWarping 已是正式 API
- **注意事项**: 该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用
- **推荐**: ✅ 推荐用于需要程序化动画调整的项目。OrientationWarping 和 StrideWarping 已是稳定 API，可放心使用。实验性节点建议在 Lyra 等官方示例中验证用法后再用于生产。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationWarping)
- 官方文档（.uplugin 中无 DocsURL）
- 相关插件依赖：[AnimationModifierLibrary](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationModifierLibrary)
