# Animation Modifier Library

> Collection of Animation Modifiers

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationModifierLibrary` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-08-19 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationModifierLibrary) | |

## 用途

Animation Modifier Library 提供一组现成的 `UAnimationModifier` 子类，用于在编辑器中对 `UAnimSequence` 进行批量后处理。每个 Modifier 都可以在动画资产的 **Asset → Animation Modifiers** 面板中添加并应用，实现自动化的工作流，避免手动逐帧编辑。

核心解决的问题：
- **动作数据提取**：从骨骼动画中提取位移/旋转/缩放信息并烘焙为曲线（MotionExtractor），驱动 Blend Graph 中的状态判断
- **足迹事件生成**：自动检测脚部触地时刻，生成 AnimNotify 和 SyncMarker（FootstepAnimEvents）
- **动画镜像**：使用 MirrorDataTable 对整个动画序列进行骨骼镜像（Mirror）
- **骨骼变换复制**：将一个骨骼的变换复制到另一个骨骼（CopyBones）
- **根骨骼处理**：零化根运动（ZeroOutRootBone）、重新定向根骨骼朝向（ReOrientRootBone）、从加权子骨骼编码根骨骼变换（EncodeRootBone）

模块类型为 `UncookedOnly`，意味着这些 Modifier 仅在编辑器中运行（烘焙/导入阶段），不会被打包到最终游戏中。

## 使用场景

- 你通过 Take Recorder 捕获了角色在世界空间中的移动动画，需要将根运动归零以便导出 FBX 给动画师 → 用 **ZeroOutRootBoneModifier**
- 你有一组跑步/走路动画，需要自动检测脚步落地帧来放置脚步声 AnimNotify → 用 **FootstepAnimEventsModifier**
- 你需要从动画中提取根骨骼的 Y 轴位移速度作为 Blend Graph 的参数 → 用 **MotionExtractorModifier**
- 你有一个左手持枪的动画，需要快速生成右手版本 → 用 **MirrorModifier**
- 你需要让根骨骼的朝向始终跟随某个子骨骼（如 pelvis）的运动方向 → 用 **EncodeRootBoneModifier**

## 蓝图用法

### 核心节点

本插件的 Modifier 主要在编辑器动画面板中使用，但也通过 `UMotionExtractorUtilityLibrary` 暴露了一些蓝图可用的静态函数：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateCurveName` | 根据骨骼名、运动类型、轴向自动生成曲线名称 | `UMotionExtractorUtilityLibrary` |
| `GetDesiredValue` | 从骨骼变换中提取指定类型的运动值（位移/旋转/速度等） | `UMotionExtractorUtilityLibrary` |
| `GetStoppedRangesFromRootMotion` | 返回动画中根运动静止的时间段（FVector2D 数组，X=起始 Y=结束） | `UMotionExtractorUtilityLibrary` |
| `GetMovingRangesFromRootMotion` | 返回动画中根运动活跃的时间段 | `UMotionExtractorUtilityLibrary` |

### 使用示例（蓝图描述）

**获取动画中角色静止的时间段**：
1. 拥有一个 `UAnimSequence` 引用
2. 调用 `GetStoppedRangesFromRootMotion`，设置 `StopSpeedThreshold`（默认 10.0）和 `SampleRate`（默认 120.0）
3. 返回的 `TArray<FVector2D>` 中每个元素代表一段静止区间，X 为起始时间，Y 为结束时间
4. 可用于在动画中自动分割移动/静止片段

## C++ 用法

### 头文件引入

```cpp
#include "MotionExtractorModifier.h"
#include "FootstepAnimEventsModifier.h"
#include "MirrorModifier.h"
#include "CopyBonesModifier.h"
#include "ZeroOutRootBoneModifier.h"
#include "ReOrientRootBoneModifier.h"
#include "EncodeRootBoneModifier.h"
#include "MotionExtractorUtilities.h"
#include "MotionExtractorTypes.h"
```

### 基本用法 — MotionExtractor

从动画中提取根骨骼 Y 轴位移并烘焙为曲线：

```cpp
// 来源: MotionExtractorModifier.cpp
UMotionExtractorModifier* Modifier = NewObject<UMotionExtractorModifier>();
Modifier->BoneName = FName(TEXT("root"));
Modifier->MotionType = EMotionExtractor_MotionType::Translation;
Modifier->Axis = EMotionExtractor_Axis::Y;
Modifier->SampleRate = 30;
Modifier->bRelativeToFirstFrame = false;
Modifier->Space = EMotionExtractor_Space::ComponentSpace;
Modifier->bNormalize = false;
Modifier->bAbsoluteValue = false;
Modifier->MathOperation = EMotionExtractor_MathOperation::None;

// 应用到动画序列（编辑器中通常通过 Animation Modifier 面板操作）
Modifier->OnApply(AnimSequence);
```

生成的曲线名称格式为 `{BoneName}_{MotionType}_{Axis}`，例如 `root_translation_Y`。

### 基本用法 — FootstepAnimEventsModifier

自动检测脚步落地并放置 AnimNotify：

```cpp
// 来源: FootstepAnimEventsModifier.cpp
UFootstepAnimEventsModifier* Modifier = NewObject<UFootstepAnimEventsModifier>();
Modifier->SampleRate = 60;
Modifier->GroundThreshold = 4.0f;
Modifier->SpeedThreshold = 0.1f;

// 配置左脚
FFootDefinition LeftFoot;
LeftFoot.FootBoneName = FName("foot_l");
LeftFoot.ReferenceBoneName = FName("root");
LeftFoot.bShouldGenerateNotifies = true;
LeftFoot.FootstepNotify = UMyFootstepNotify::StaticClass();
LeftFoot.FootstepNotifyTrackName = FName("FootAnimEvents");
LeftFoot.FootstepNotifyDetectionTechnique = EDetectionTechnique::FootBoneSpeed;

// 配置右脚
FFootDefinition RightFoot;
RightFoot.FootBoneName = FName("foot_r");
RightFoot.bShouldGenerateSyncMarkers = true;
RightFoot.SyncMarkerName = FName("RightFootSync");
RightFoot.SyncMarkerTrackName = FName("FootSyncMarkers");

Modifier->FootDefinitions.Add(LeftFoot);
Modifier->FootDefinitions.Add(RightFoot);

Modifier->OnApply(AnimSequence);
```

### 进阶用法 — MotionExtractorUtilityLibrary

直接在 C++ 中使用工具函数提取运动数据：

```cpp
// 来源: MotionExtractorUtilities.cpp
// 从骨骼变换中提取 Y 轴位移速度
FTransform CurrentTransform = ...;
FTransform LastTransform = ...;
float DeltaTime = 1.0f / 30.0f;

float Speed = UMotionExtractorUtilityLibrary::GetDesiredValue(
    CurrentTransform, LastTransform, DeltaTime,
    EMotionExtractor_MotionType::TranslationSpeed,
    EMotionExtractor_Axis::Y);

// 获取动画中静止/移动的时间段
TArray<FVector2D> StoppedRanges = UMotionExtractorUtilityLibrary::GetStoppedRangesFromRootMotion(
    AnimSequence, 10.0f, 120.0f);

for (const FVector2D& Range : StoppedRanges)
{
    UE_LOG(LogAnimation, Log, TEXT("Stopped: %.2f -> %.2f"), Range.X, Range.Y);
}
```

### 进阶用法 — EncodeRootBoneModifier

从加权子骨骼自动计算根骨骼位置和朝向：

```cpp
// 来源: EncodeRootBoneModifier.cpp
UEncodeRootBoneModifier* Modifier = NewObject<UEncodeRootBoneModifier>();

// 用 pelvis 和 spine_01 的加权平均位置作为根骨骼位置
FEncodeRootBoneWeightedBone PelvisPos;
PelvisPos.Bone.BoneName = FName("pelvis");
PelvisPos.Weight = 0.7f;
Modifier->WeightedBoneToComputeRootPosition.Add(PelvisPos);

FEncodeRootBoneWeightedBone SpinePos;
SpinePos.Bone.BoneName = FName("spine_01");
SpinePos.Weight = 0.3f;
Modifier->WeightedBoneToComputeRootPosition.Add(SpinePos);

// 用 pelvis 的 Y 轴方向确定根骨骼朝向
FEncodeRootBoneWeightedBoneAxis PelvisOrient;
PelvisOrient.Bone.BoneName = FName("pelvis");
PelvisOrient.BoneAxis = EEncodeRootBoneAxis::Y;
PelvisOrient.Weight = 1.0f;
Modifier->WeightedBoneToComputeRootOrientation.Add(PelvisOrient);

Modifier->OnApply(AnimSequence);
```

## Demo 示例

以下是一个最小的自定义 Animation Modifier，利用 MotionExtractorUtilities 来提取运动数据：

```cpp
// MyCustomModifier.h
#pragma once
#include "AnimationModifier.h"
#include "MotionExtractorTypes.h"
#include "MyCustomModifier.generated.h"

UCLASS()
class UMyCustomModifier : public UAnimationModifier
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Settings")
    FName TargetBoneName = FName("root");

    virtual void OnApply_Implementation(UAnimSequence* Animation) override;
};
```

```cpp
// MyCustomModifier.cpp
#include "MyCustomModifier.h"
#include "MotionExtractorUtilities.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"

void UMyCustomModifier::OnApply_Implementation(UAnimSequence* Animation)
{
    if (!Animation) return;

    USkeleton* Skeleton = Animation->GetSkeleton();
    const int32 BoneIndex = Skeleton->GetReferenceSkeleton().FindBoneIndex(TargetBoneName);
    if (BoneIndex == INDEX_NONE) return;

    TArray<FBoneIndexType> RequiredBones;
    RequiredBones.Add(static_cast<FBoneIndexType>(BoneIndex));
    Skeleton->GetReferenceSkeleton().EnsureParentsExistAndSort(RequiredBones);
    FBoneContainer BoneContainer(RequiredBones, UE::Anim::ECurveFilterMode::DisallowAll, *Skeleton);
    auto CompactIndex = BoneContainer.MakeCompactPoseIndex(FMeshPoseBoneIndex(BoneIndex));

    const float AnimLength = Animation->GetPlayLength();
    const float SampleInterval = 1.0f / 30.0f;

    FTransform LastTransform = FTransform::Identity;
    for (int32 i = 0; i * SampleInterval < AnimLength; ++i)
    {
        float Time = FMath::Clamp(i * SampleInterval, 0.f, AnimLength);
        FTransform BoneTransform = UMotionExtractorUtilityLibrary::ExtractBoneTransform(
            Animation, BoneContainer, CompactIndex, Time, true);

        float Value = UMotionExtractorUtilityLibrary::GetDesiredValue(
            BoneTransform, LastTransform, SampleInterval,
            EMotionExtractor_MotionType::TranslationSpeed,
            EMotionExtractor_Axis::Y);

        // 处理 Value...
        LastTransform = BoneTransform;
    }
}
```

Build.cs 依赖：

```csharp
PrivateDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "AnimationModifiers",
    "AnimationBlueprintLibrary",
    "AnimationModifierLibrary"  // 你的模块需要依赖此插件模块
});
```

## 模块依赖

从 `AnimationModifierLibrary.Build.cs` 的 `PrivateDependencyModuleNames` 提取。如果你想在自己的模块中使用这些 Modifier 或工具类，需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、数学库 |
| `CoreUObject` | UObject 系统、反射 |
| `Engine` | 动画系统核心（UAnimSequence、USkeleton 等） |
| `AnimationModifiers` | `UAnimationModifier` 基类 |
| `AnimationBlueprintLibrary` | 动画蓝图工具函数（添加 Notify、管理曲线等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-11 | `1bb7cec8` | 移除 TSubclassOf 的 nullptr 初始化器，改用 `{}` 默认初始化 | 代码规范化，跟随 UE 编码规范变更 |
| 2025-06-26 | `a2e75189` | 为源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏 | 编译优化，减少编译时间和头文件依赖 |
| 2025-05-30 | `20572801` | 更新头文件的 DLL 导出标记，将 `UE_API` 放到方法上而非类型上 | API 导出规范化，修复跨模块链接问题 |

### 维护评价

- **创建时间**：2021 年 8 月，约 5 年历史
- **最近更新**：2025 年 7 月，近期三次更新均为代码规范化/编译优化，非功能性变更
- **维护状态**：**维护中** — 代码持续跟随 UE 源码规范化流程更新，但无新功能添加
- **稳定性**：高 — 所有 Modifier 都是经过验证的成熟功能，接口稳定
- **推荐使用**：✅ 推荐。这是 Epic 官方维护的动画 Modifier 合集，代码质量高，功能实用。特别是 MotionExtractorModifier 和 FootstepAnimEventsModifier 在实际项目中非常常用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationModifierLibrary)
- [UAnimationModifier 基类](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/AnimationModifiers)
