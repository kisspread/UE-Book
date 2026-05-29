# Animation Modifier Library

> Collection of Animation Modifiers

| 属性 | 值 |
|---|---|
| 中文名 | 动画修改器库 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationModifierLibrary` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-08-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationModifierLibrary) | |

## 用途

该插件提供了一系列预制的 `UAnimationModifier` 子类，用于在编辑器中批量处理和编辑动画序列（`UAnimSequence`）数据。这些修改器旨在自动化常见的动画后处理任务，例如自动检测脚印并生成动画事件、提取骨骼的运动信息并将其烘焙为曲线、镜像动画、零化根骨骼运动等。通过应用这些修改器，动画师和技术美术可以快速、一致地处理大量动画资产，无需手动为每个动画重复繁琐的操作。

## 使用场景

- **为第三人称角色动画自动生成脚步声动画事件或同步标记** → 使用 `UFootstepAnimEventsModifier`
- **需要从动画中提取特定骨骼（如武器、特效挂点）的位移、旋转或速度数据，并写入曲线以驱动游戏逻辑** → 使用 `UMotionExtractorModifier`
- **在多个动画之间快速复制特定骨骼的变换数据** → 使用 `UCopyBonesModifier`
- **需要制作镜像动画，如左跑转为右跑** → 使用 `UMirrorModifier`
- **需要重置或修改动画的根骨骼运动，例如去除起始帧或调整朝向** → 使用 `UZeroOutRootBoneModifier` 或 `UReOrientRootBoneModifier`
- **希望根据动画中的同步标记（Sync Markers）时间点生成自定义的浮点曲线** → 使用 `UCurveFromSyncMarkersModifier` (实验性)

## 蓝图用法

虽然 `AnimationModifier` 主要在编辑器中应用，但插件包含的 `UMotionExtractorUtilityLibrary` 提供了一些可在蓝图中使用的静态函数，用于查询动画信息。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCurveName` | 根据骨骼名、运动类型和轴向生成一个描述性的曲线名称 | `UMotionExtractorUtilityLibrary` |
| `GetDesiredValue` | 根据给定的骨骼变换、上一帧变换、时间步长和运动类型，计算所需的提取值 | `UMotionExtractorUtilityLibrary` |
| `GetStoppedRangesFromRootMotion` | 返回动画中根运动速度低于阈值的时间范围（认为是静止的） | `UMotionExtractorUtilityLibrary` |
| `GetMovingRangesFromRootMotion` | 返回动画中根运动速度高于阈值的时间范围（认为是在移动的） | `UMotionExtractorUtilityLibrary` |

### 使用示例（蓝图描述）

在蓝图中，你可以直接拖拽使用 `Motion Extractor Utility Library` 类下的这些节点。例如，要判断一个动画序列在哪些时间段角色是静止的，你可以调用 `GetStoppedRangesFromRootMotion` 节点，传入动画序列资产引用和一个速度阈值（如 10.0），该节点会返回一个 `TArray<FVector2D>`，其中每个 `FVector2D` 的 X 和 Y 分别代表静止区间的开始和结束时间。

## C++ 用法

### 头文件引入

```cpp
// 使用特定的动画修改器
#include "FootstepAnimEventsModifier.h"
#include "MotionExtractorModifier.h"
// 使用动画提取工具库
#include "MotionExtractorUtilities.h"
```

### 基本用法

动画修改器通常通过编辑器界面应用。在 C++ 中，你可以通过修改其属性来定制行为。以下示例展示了如何配置一个 `UMotionExtractorModifier`。

```cpp
// 创建一个 UMotionExtractorModifier 实例
UMotionExtractorModifier* MotionExtractor = NewObject<UMotionExtractorModifier>();

// 配置要提取的骨骼和运动类型
MotionExtractor->BoneName = TEXT("weapon_tip");
MotionExtractor->MotionType = EMotionExtractor_MotionType::Translation; // 提取平移
MotionExtractor->Axis = EMotionExtractor_Axis::Z; // 只关心Z轴（上下）
MotionExtractor->Space = EMotionExtractor_Space::ComponentSpace; // 使用组件空间
MotionExtractor->bRelativeToFirstFrame = true; // 相对于第一帧
MotionExtractor->SampleRate = 30; // 采样率30Hz

// 在某个动画序列上应用此修改器（通常在编辑器工具或命令中执行）
if (UAnimSequence* MyAnimSequence = /* 获取动画序列 */)
{
    MotionExtractor->OnApply(MyAnimSequence);
    // 应用后，动画序列中会新增一条由 BoneName、MotionType 和 Axis 决定名称的曲线
}
```

### 进阶用法

你可以使用 `UMotionExtractorUtilityLibrary` 的静态函数进行更底层的计算。例如，在动画蓝图或游戏逻辑中，实时计算某个骨骼的即时速度。

```cpp
// 假设我们获取到了当前帧和上一帧的骨骼变换
FTransform CurrentBoneTransform = /* ... */;
FTransform LastBoneTransform = /* ... */;
float DeltaTime = /* ... */;

// 计算该骨骼在 Z 轴的平移速度
float SpeedZ = UMotionExtractorUtilityLibrary::GetDesiredValue(
    CurrentBoneTransform,
    LastBoneTransform,
    DeltaTime,
    EMotionExtractor_MotionType::TranslationSpeed,
    EMotionExtractor_Axis::Z
);

// 现在你可以使用 SpeedZ 来驱动游戏逻辑，例如判断角色是否在落地瞬间
```

## Demo 示例

以下是一个简单的自定义动画修改器的示例，演示了如何继承 `UAnimationModifier` 并实现自己的逻辑。

### MyCustomModifier.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "AnimationModifier.h"
#include "MyCustomModifier.generated.h"

/**
 * 一个简单的自定义动画修改器示例。
 * 功能：将动画序列中指定骨骼在每一帧的旋转值清零。
 */
UCLASS(BlueprintType, EditInlineNew, meta = (DisplayName = "Zero Out Bone Rotation"))
class UMyCustomModifier : public UAnimationModifier
{
	GENERATED_BODY()

public:
	/** 要清零旋转的骨骼 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Settings")
	FBoneReference TargetBone;

	virtual void OnApply_Implementation(UAnimSequence* Animation) override;
	virtual void OnRevert_Implementation(UAnimSequence* Animation) override;
};
```

### MyCustomModifier.cpp

```cpp
#include "MyCustomModifier.h"
#include "Animation/AnimPose.h"

void UMyCustomModifier::OnApply_Implementation(UAnimSequence* Animation)
{
	if (!Animation || !TargetBone.Initialize(Animation->GetSkeleton()))
	{
		return;
	}

	const FBoneContainer& BoneContainer = Animation->GetSkeleton()->GetReferenceSkeleton();

	// 确保目标骨骼有效
	const FCompactPoseBoneIndex CompactPoseBoneIndex = TargetBone.GetCompactPoseIndex(BoneContainer);
	if (CompactPoseBoneIndex == INDEX_NONE)
	{
		return;
	}

	// 遍历动画的每一帧
	const int32 NumFrames = Animation->GetNumberOfSampledKeys();
	for (int32 FrameIndex = 0; FrameIndex < NumFrames; ++FrameIndex)
	{
		// 获取当前帧的骨骼变换（在Component Space）
		FTransform BoneTransform = Animation->GetBoneTransform(FrameIndex, CompactPoseBoneIndex, EAnimPoseSpaces::Component);

		// 清零旋转
		BoneTransform.SetRotation(FQuat::Identity);

		// 将修改后的变换设置回去（需要转换回动画数据模型所需的格式）
		// 注意：实际实现需要更复杂的处理，这里仅为概念演示。
		// Animation->SetBoneTransformForFrame(CompactPoseBoneIndex, FrameIndex, BoneTransform, EAnimPoseSpaces::Component);
	}

	// 标记动画数据已被修改，以便保存
	Animation->Modify();
}

void UMyCustomModifier::OnRevert_Implementation(UAnimSequence* Animation)
{
	// “Revert”操作通常意味着移除此修改器添加的数据。
	// 对于这个简单的示例，由于我们是直接修改骨骼变换，难以完美撤销。
	// 更好的做法是在OnApply时添加自定义曲线或标记，然后在OnRevert时移除它们。
	// 此处留空，因为没有可以安全移除的独立数据。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationModifier` | 核心依赖，提供了 `UAnimationModifier` 基类 |
| `AnimationDataController` | 用于在编辑器中修改动画数据 |
| `AnimationBlueprintLibrary` | 提供了动画相关的工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `75b83bff` | AnimationModifierLibrary - UCurveFromSyncMarkersModifier::CurveName defaulted to "CurveFromSyncMarke | 修复了 `UCurveFromSyncMarkersModifier` 默认曲线名称拼写不完整的问题。 |
| 2026-04-15 | `8f0c0fe4` | AnimationModifierLibrary - adding UCurveFromSyncMarkersModifier to generate a curve from synch marke | 新增实验性修改器 `UCurveFromSyncMarkersModifier`，可根据同步标记生成曲线。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出从 `UE_LOG` 迁移至 `UE_LOGF`，属于代码规范化更新。 |
| 2025-11-07 | `622fa568` | PR #13938: Fix CopyBonesModifier for bones without pre-existing curves | 修复了 `CopyBonesModifier` 在处理没有预先存在的骨骼曲线时的错误。 |
| 2025-07-11 | `1bb7cec8` | Ran update script to removed null initializers when creating TSubclassOf<T> since it will use a code | 自动化脚本移除了 `TSubclassOf` 初始化时多余的 null 初始化代码。 |

### 维护评价

该插件创建于约 4 年前（2021年），处于“活跃维护”状态。从最近的提交历史来看，Epic 团队在 2025 年和 2026 年持续为其添加新功能（如 `UCurveFromSyncMarkersModifier`）并修复 Bug（如 `CopyBonesModifier` 的问题），表明该插件仍在被积极使用和改进。作为 Epic 官方提供的动画工具集，其稳定性和可靠性较高。推荐在需要批量、程序化处理动画数据的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationModifierLibrary)
- [官方文档]() (暂无直接链接，请参考引擎内置文档中关于 Animation Modifiers 的章节)
- [测试用例]() (测试用例路径未知，通常位于 `Engine/Tests` 或插件目录下的 `Tests` 文件夹)