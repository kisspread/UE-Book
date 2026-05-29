# UAF Warping

> Framework for animation and pose warping for UAF.

| 属性 | 值 |
|---|---|
| 中文名 | UAF扭曲框架 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UAFWarping` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping) | |

## 用途

UAFWarping 是 UAF（Unreal Animation Framework）动画框架的插件，专注于提供高级动画和姿态扭曲（Warping）功能。其核心目的是解决动画系统中角色根运动（Root Motion）与游戏玩法目标（如目标朝向、路径点）不匹配的问题。

该插件主要提供以下核心能力：
1.  **方向扭曲（Strafe Warping）**：自动调整动画姿态，使角色面朝移动方向，减少角色转身时的动画不自然感。
2.  **转向控制（Steering）**：程序化地修正根运动，使角色在移动过程中平滑地朝向目标方向。
3.  **根骨偏移（Offset Root Bone）**：通过程序化偏移根骨骼，减少角色在动作匹配（Motion Matching）或转向时的脚部滑动。
4.  **根运动覆盖（Override Root Motion）**：允许用代码驱动的运动直接注入或叠加到动画系统的根运动上。
5.  **瞬移扭曲（Warp To Target）**：将角色的根骨骼扭曲到指定的目标变换。

简而言之，该插件让动画师或程序能够更精细地控制角色的朝向和移动，使动画播放结果更贴合实际的游戏逻辑和玩家意图，常用于第三人称动作、射击或需要精确运动控制的游戏中。

## 使用场景

- 你在制作一个第三人称射击或动作游戏，需要角色在移动时始终保持面向移动方向或瞄准目标 → 使用 **Strafe Warping**。
- 你正在实现一个运动匹配（Motion Matching）系统，但角色在快速转身或转向时脚部滑动严重 → 使用 **Offset Root Bone** 结合 **Steering**。
- 游戏角色需要平滑地跟随一个复杂的导航路径或追逐目标，而非动画本身能提供的转向 → 使用 **Steering**。
- 你需要通过代码完全接管角色的位移和旋转，但又想利用现有的动画播放系统 → 使用 **Override Root Motion**。
- 你的游戏包含瞬移或快速传送机制，需要动画能够平滑过渡到新位置 → 使用 **Warp To Target**。

## 蓝图用法

此插件的核心功能主要在 **动画蓝图（AnimGraph）** 中使用，通过配置 `AnimNode` 实现。它本身不提供大量的 `BlueprintCallable` 运行时函数，而是通过暴露在动画节点 `Details` 面板中的属性进行配置。

### 核心配置（AnimNode 数据结构）

以下是在动画蓝图节点中可以配置的关键属性（来自 `FUAFStrafeWarpingData`、`FSteeringTraitSharedData` 等结构体）：

| 节点属性 | 说明 | 所在数据结构 |
|---|---|---|
| `Alpha` | 整体效果的强度，0为无效果，1为完全生效。 | `StrafeWarping`, `Steering`, `OffsetRootBone` |
| `TargetOrientation` | 角色期望面向的目标朝向（四元数）。 | `StrafeWarping`, `Steering` |
| `RootBoneTransform` | 当前帧的根骨骼变换，通常由动画或之前的节点提供。 | `StrafeWarping`, `Steering`, `WarpToTarget` |
| `RotationAxis` | 旋转所围绕的轴，通常为 `Z` 轴（上下方向）。 | `StrafeWarping` |
| `DistributedBoneOrientationAlpha` | 在身体旋转和脚部IK之间分配朝向修正的比例。0为纯身体旋转，1为纯脚部修正。 | `StrafeWarping` |
| `SpineBones` | 脊柱骨骼名称数组，用于进行分布式旋转修正。 | `StrafeWarping` |
| `FootData` | 腿部IK数据数组，用于进行基础的脚部IK计算。 | `StrafeWarping` |
| `TranslationMode` | 根骨偏移的平移模式（`Accumulate`, `Interpolate`, `Release`）。 | `OffsetRootBone` |
| `RotationMode` | 根骨偏移的旋转模式（同上）。 | `OffsetRootBone` |
| `OverrideRootMotionDelta` | 需要覆盖或叠加到根运动上的变换增量。 | `OverrideRootMotion` |
| `OverrideRootMotionMode` | 覆盖模式：`Replace`（替换）或 `Additive`（叠加）。 | `OverrideRootMotion` |
| `TargetRootBoneTransform` | 瞬移扭曲的目标根骨骼变换。 | `WarpToTarget` |

### 使用示例（动画蓝图描述）

1.  **配置 Strafe Warping**：
    - 在角色的动画蓝图事件图中，根据角色移动输入或AI计算出 `Target Orientation`（目标朝向）。
    - 在动画图中，将你的动画序列或状态机输出连接到 **Strafe Warping** 节点的 `Input Pose`。
    - 将计算好的 `Target Orientation` 传入该节点的 `Target Orientation` 引脚。
    - 配置 `SpineBones`（如 `["spine_01", "spine_02", "spine_03"]`）和 `FootData`，并调整 `DistributedBoneOrientationAlpha` 来平衡身体转动和脚步IK。
    - 将该节点的输出连接到 `Output Pose`。

2.  **使用 Steering**：
    - 将一个播放带根运动动画的节点（如行走、奔跑）连接到 **Steering** 节点的 `Input Pose`。
    - 同样，传入 `Target Orientation` 和 `Root Bone Transform`。
    - 调整 `AnimatedTargetTime` 和 `ProceduralTargetTime` 来控制转向的平滑度和提前量。

3.  **应用 Offset Root Bone**：
    - 将运动匹配系统或任何产生根运动的动画节点连接到 **Offset Root Bone** 节点。
    - 传入 `Mesh Component Transform World`（通常来自蓝图中的 `GetActorTransform` 或组件变换）。
    - 设置 `TranslationMode` 和 `RotationMode` 为 `Interpolate`，并调整 `TranslationSmoothingTime` 等参数来减少脚滑。

## C++ 用法

UAFWarping 插件提供了底层 C++ 结构（Trait）用于更底层的集成和自定义。这些 Trait 遵循 UAF 的 Trait 系统架构。

### 头文件引入

```cpp
#include "UAFWarping.h"
// 具体 Trait 的头文件位于 Private 目录下，通常不直接包含，而是通过上层系统（如 AnimNode）使用。
```

### 基本用法

以下示例展示了如何通过 C++ 创建和配置一个 `StrafeWarping` 节点（源自 `UAFStrafeWarpingNode.h` 的逻辑推断）。

```cpp
// 在某个自定义的 UAnimInstance 子类或 AnimationGraph 函数中
#include "AnimNode/UAFStrafeWarpingNode.h"

// 1. 准备配置数据
UE::UAF::FUAFStrafeWarpingData StrafeWarpingConfig;
StrafeWarpingConfig.Alpha = 1.0f;
StrafeWarpingConfig.TargetOrientation = FQuat(FRotator(0.f, DesiredYaw, 0.f)); // 期望的朝向
StrafeWarpingConfig.RotationAxis = EAxis::Z;
StrafeWarpingConfig.DistributedBoneOrientationAlpha = 0.6f;
StrafeWarpingConfig.SpineBones = { TEXT("spine_01"), TEXT("spine_02") };
StrafeWarpingConfig.RotationInterpSpeed = 12.f; // 开启插值平滑

// 2. 假设在某个评估上下文（如 FAnimUpdateContext）中创建节点实例
// 实际创建通常由 UAF AnimGraph 系统管理
// UE::UAF::FUAFAnimNodePtr StrafeNode = StrafeWarpingConfig.CreateInstance(UpdateContext);

// 3. 在每帧更新前，需要提供最新的根骨骼变换（通常从动画资产采样或上一节点获取）
// 然后调用节点的 PreUpdate 方法
```

### 进阶用法

结合 `Offset Root Bone` 和 `Steering` 来创建更复杂的运动控制系统。

```cpp
// 假设你已经有了一个处理根运动的动画实例（MotionMatchingInstance）
// 你想要在转向时应用根骨偏移来减少脚滑

// 1. 配置并应用 Steering Trait (通常在 AnimGraph 的 Trait Stack 中配置)
FSteeringTraitSharedData SteeringConfig;
SteeringConfig.TargetOrientation = CalculatedTargetOrientation;
SteeringConfig.AnimatedTargetTime = 0.25f;
SteeringConfig.MinScaleRatio = 0.7f;
SteeringConfig.MaxScaleRatio = 1.3f;
// ... 将此配置关联到动画节点

// 2. 配置并应用 OffsetRootBone Trait
FOffsetRootBoneTraitSharedData OffsetConfig;
OffsetConfig.Input = /* 上一个 Trait 或动画节点的输出 */;
OffsetConfig.TranslationMode = EUAFOffsetRootBoneMode::Interpolate;
OffsetConfig.RotationMode = EUAFOffsetRootBoneMode::Interpolate;
OffsetConfig.TranslationSmoothingTime = 0.15f;
OffsetConfig.MaxTranslationError = 25.0f; // 限制最大偏移距离
OffsetConfig.bOnGround = true; // 在地面上时，将偏移投影到地面平面
// MeshComponentTransformWorld 通常在运行时每帧从组件获取并设置
```

## Demo 示例

一个最小的 C++ 示例，展示如何在自己的动画系统评估中使用 `FOffsetRootBoneTrait`。

### OffsetRootBoneDemo.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "UAFWarping/Private/OffsetRootBoneTrait.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURGAME_API UOffsetRootBoneDemoComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UOffsetRootBoneDemoComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

protected:
	virtual void BeginPlay() override;

private:
	// 用于存储 Trait 的实例数据和状态
	UE::UAF::FOffsetRootBoneTrait::FInstanceData OffsetInstanceData;
	FOffsetRootBoneTraitSharedData OffsetSharedData;

	// 模拟的网格组件变换（实际应从组件获取）
	FTransform CurrentMeshComponentTransform = FTransform::Identity;
	FTransform PreviousMeshComponentTransform = FTransform::Identity;

	// 模拟输入的根运动
	FTransform IncomingRootMotionDelta = FTransform::Identity;
};
```

### OffsetRootBoneDemo.cpp
```cpp
#include "OffsetRootBoneDemo.h"
// 包含 UAF 相关的核心评估头文件，路径需根据实际情况调整
// #include "UAF/FEvaluationVM.h"
// #include "UAF/KeyframeState.h"

UOffsetRootBoneDemoComponent::UOffsetRootBoneDemoComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UOffsetRootBoneDemoComponent::BeginPlay()
{
	Super::BeginPlay();

	// 初始化配置
	OffsetSharedData.Alpha = 1.0f;
	OffsetSharedData.TranslationMode = EUAFOffsetRootBoneMode::Interpolate;
	OffsetSharedData.RotationMode = EUAFOffsetRootBoneMode::Interpolate;
	OffsetSharedData.TranslationSmoothingTime = 0.1f;
	OffsetSharedData.MaxTranslationError = 50.0f;
	OffsetSharedData.bOnGround = true;

	// 初始化实例数据
	OffsetInstanceData.DeltaTime = 0.f;
	OffsetInstanceData.bIsFirstUpdate = true;
	// ... 其他初始化

	// 初始化变换
	CurrentMeshComponentTransform = GetOwner()->GetActorTransform();
	PreviousMeshComponentTransform = CurrentMeshComponentTransform;
}

void UOffsetRootBoneDemoComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// 1. 更新状态 (PreUpdate 阶段)
	OffsetInstanceData.DeltaTime = DeltaTime;
	OffsetInstanceData.Alpha = OffsetSharedData.Alpha;
	OffsetInstanceData.TranslationMode = OffsetSharedData.TranslationMode;
	OffsetInstanceData.RotationMode = OffsetSharedData.RotationMode;
	// ... 将其他 SharedData 同步到 InstanceData

	PreviousMeshComponentTransform = CurrentMeshComponentTransform;
	CurrentMeshComponentTransform = GetOwner()->GetActorTransform();
	OffsetInstanceData.LastMeshComponentTransformWorld = PreviousMeshComponentTransform;
	OffsetInstanceData.MeshComponentTransformWorld = CurrentMeshComponentTransform;

	// 2. 模拟执行一个评估任务 (Execute 阶段)
	// 在真实的 UAF 系统中，这会在评估虚拟机(VM)中运行。
	// 这里我们简化模拟逻辑。
	{
		// 计算网格组件的运动增量
		FTransform MeshDelta = PreviousMeshComponentTransform.GetRelativeTransform(CurrentMeshComponentTransform);

		// 根据 OffsetMode 更新模拟的根骨骼位置
		// 这部分逻辑通常在 FAnimNextOffsetRootBoneTask::Execute 中
		if (OffsetInstanceData.TranslationMode == EUAFOffsetRootBoneMode::Interpolate)
		{
			// 平滑插值，使模拟的根骨骼位置逐渐靠近实际的网格组件位置
			OffsetInstanceData.SimulatedTranslation = FMath::VInterpTo(
				OffsetInstanceData.SimulatedTranslation,
				CurrentMeshComponentTransform.GetLocation(),
				DeltaTime,
				1.0f / FMath::Max(OffsetSharedData.TranslationSmoothingTime, 0.001f));
		}
		// ... 其他模式和旋转的处理
	}

	// 3. (可选) 打印调试信息
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 0.f, FColor::Yellow,
			FString::Printf(TEXT("Simulated Root Offset: %s"), *OffsetInstanceData.SimulatedTranslation.ToString()));
	}
}
```

## 模块依赖

该插件的源码模块 `UAFWarping` 在构建时依赖以下模块（从其运行时功能和对UAF其他部分的引用推断）：

| 模块 | 用途 |
|---|---|
| `UAF` | 核心UAF框架，提供Trait系统、动画评估虚拟机等基础架构。 |
| `UAFAnimGraph` | 提供UAF动画图（AnimGraph）集成，用于在动画蓝图中使用UAF节点。 |
| `UAFAnimNode` | 提供UAF动画节点基础类（如 `FUAFModifierAnimNode`）。 |
| `RigVM` | 提供运行时虚拟机，用于执行动画评估任务。 |
| `AnimNext` | 提供与实验性AnimNext系统的集成（Trait、评估任务等）。 |

**注意**：由于该插件在 `.uplugin` 中明确声明依赖 `UAF`, `UAFAnimGraph`, `UAFAnimNode`, `RigVM`，使用此插件**必须**在项目中启用这些插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `b604d5ca` | Handle empty value bundle in modifier AnimOps | 修复了修改器动画操作中处理空值包的问题。 |
| 2026-04-14 | `7b3fe3c2` | Use FPoseValueBundle in AnimOp value bundle evaluator | 重构为在动画操作值包评估器中使用`FPoseValueBundle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从`UE_LOG`迁移到`UE_LOGF`。 |
| 2026-04-09 | `153328f9` | UAFWarping - WarpToTargetNode | 新增了“Warp To Target”节点功能。 |
| 2026-04-06 | `0b5bc2d3` | UAFWarping - small code cleanup | 对UAFWarping进行了小规模的代码清理和优化。 |

### 维护评价

UAFWarping 是一个较新的**实验性**插件，创建于2025年6月。从近期（2026年4月）的提交历史看，它正处于**活跃开发阶段**，频繁进行功能添加（如`WarpToTargetNode`）、API重构（值包系统）和错误修复。提交信息表明其依赖的底层UAF系统（如动画操作和评估器）仍在演进中。

**建议**：
- ✅ **推荐用于实验和原型开发**：特别是当你的项目已经采用了UAF动画框架，并且需要上述描述的扭曲功能。
- ⚠️ **谨慎用于生产环境**：由于其`IsExperimentalVersion=true`且`EnabledByDefault=false`，表明该插件尚未稳定，API和行为可能在未来版本中发生变化。在生产项目中使用前，务必进行充分测试。
- 依赖此插件意味着你的项目将深度绑定于**UAF**这个实验性动画框架。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/UAF/UAFWarping)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的路径信息中发现标准测试用例目录)