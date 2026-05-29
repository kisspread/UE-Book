# Animation Data

> Animation Data

| 属性 | 值 |
|---|---|
| 中文名 | 动画数据模型 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationData` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2022-06-10 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationData) | |

## 用途

该插件为 `UAnimSequence` 动画序列资产提供了一个基于 Sequencer 轨道数据模型的实现。它将动画数据（骨骼变换、曲线、属性）表示为 Sequencer 的轨道和区段，从而能够利用 Sequencer 强大的编辑、事务处理和数据处理能力。其核心是定义了 `IAnimationDataModel` 接口和基于 Sequencer 的 `UAnimationSequencerDataModel` 及 `UAnimSequencerController`，用于在编辑器中程序化地创建和操作动画数据。

## 使用场景

- 你需要在编辑器或开发工具中，通过蓝图或 C++ 代码程序化地创建或修改 `UAnimSequence` 的动画数据（如批量处理、生成动画）。
- 你需要将动画数据与 ControlRig 结合使用，利用其 FK 控制器进行更复杂的动画操作。
- 你需要对动画编辑操作（如添加关键帧、调整曲线）支持撤销/重做事务性功能。

## 蓝图用法

核心功能通过 `IAnimationDataController` 接口暴露。蓝图节点通常从 `UAnimSequence` 的数据模型控制器获取。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Controller` | 获取动画序列数据模型的控制器接口。 | `IAnimationDataModel` |
| `Open Bracket` / `Close Bracket` | 开始和结束一个可撤销的编辑操作块（事务）。 | `IAnimationDataController` |
| `Set Bone Track Keys` | 为指定的骨骼轨道设置位置、旋转、缩放关键帧。 | `IAnimationDataController` |
| `Set Curve Keys` | 为指定的动画曲线设置 RichCurve 关键帧数据。 | `IAnimationDataController` |
| `Set Number of Frames` | 设置动画序列的总帧数。 | `IAnimationDataController` |
| `Set Frame Rate` | 设置动画序列的帧率。 | `IAnimationDataController` |

### 使用示例（蓝图描述）
1.  获取一个 `AnimSequence` 引用。
2.  通过调用 `Get Controller` 获取其 `IAnimationDataController` 接口。
3.  调用 `Open Bracket` 开始一个编辑操作。
4.  使用 `Set Bone Track Keys` 或 `Set Curve Keys` 等节点修改动画数据。
5.  调用 `Close Bracket` 提交编辑，所有操作将被合并为一个撤销步骤。

## C++ 用法

### 头文件引入
```cpp
#include "AnimationDataModule.h"
// 或直接包含实现类头文件
#include "AnimSequencerDataModel.h"
#include "AnimSequencerController.h"
```

### 基本用法
获取动画序列的 Sequencer 数据模型和控制器。
```cpp
// (来源: AnimSequencerDataModel.h 及通用用法)
UAnimSequence* AnimSequence = ...; // 获取或加载动画序列
if (AnimSequence)
{
    // 获取基于 Sequencer 的数据模型（IAnimationDataModel 接口）
    TScriptInterface<IAnimationDataModel> DataModel = AnimSequence->GetDataModel();
    if (DataModel)
    {
        // 获取控制器（IAnimationDataController 接口）
        TScriptInterface<IAnimationDataController> Controller = DataModel->GetController();
        // ... 使用Controller进行操作
    }
}
```

### 进阶用法
使用控制器进行事务性编辑，并设置骨骼关键帧。
```cpp
// (来源: AnimSequencerController.h 中 IAnimationDataController 的接口定义)
if (Controller)
{
    // 开始一个名为“BatchEdit”的事务
    Controller->OpenBracket(NSLOCTEXT("MyTool", "BatchEdit", "Batch Edit Bones"));
    
    // 为 “spine_01” 骨骼设置关键帧
    FName BoneName = TEXT("spine_01");
    TArray<FVector> Positions = {FVector(0,0,0), FVector(0,0,10)};
    TArray<FQuat> Rotations = {FQuat::Identity, FQuat(FVector::UpVector, PI/4)};
    TArray<FVector> Scales = {FVector(1), FVector(1)};
    // 在帧号0和30处设置关键帧
    Controller->SetBoneTrackKeys(BoneName, Positions, Rotations, Scales);
    
    // 关闭事务，提交所有更改
    Controller->CloseBracket();
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何获取并使用控制器为动画序列添加一个骨骼关键帧。

**AnimDataDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AnimDataDemoActor.generated.h"

class UAnimSequence;

UCLASS()
class AAnimDataDemoActor : public AActor
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Demo")
    UAnimSequence* TargetAnimSequence;

    UFUNCTION(CallInEditor, BlueprintCallable, Category = "Demo")
    void AddKeyframeToSpine();

    // ... 其他 Actor 生命周期函数省略
};
```

**AnimDataDemoActor.cpp**
```cpp
#include "AnimDataDemoActor.h"
#include "Animation/AnimSequence.h"
#include "IAnimationDataModel.h"
#include "IAnimationDataController.h"
#include "AnimationDataModule.h" // 确保模块被链接

void AAnimDataDemoActor::AddKeyframeToSpine()
{
    if (!TargetAnimSequence) return;

    // 1. 获取数据模型和控制器
    TScriptInterface<IAnimationDataModel> DataModel = TargetAnimSequence->GetDataModel();
    if (!DataModel) return;

    TScriptInterface<IAnimationDataController> Controller = DataModel->GetController();
    if (!Controller) return;

    // 2. 开始事务
    Controller->OpenBracket(NSLOCTEXT("Demo", "AddKey", "Add Spine Key"));

    // 3. 准备关键帧数据（在第0帧和第10帧各设置一个关键帧）
    const FName SpineBone = TEXT("spine_02");
    TArray<FVector> Positions = { FVector::ZeroVector, FVector(0.f, 0.f, 50.f) };
    TArray<FQuat> Rotations = { FQuat::Identity, FQuat(FVector::RightVector, FMath::DegreesToRadians(45.f)) };
    TArray<FVector> Scales = { FVector::OneVector, FVector::OneVector };

    // 4. 设置骨骼轨道关键帧
    bool bSuccess = Controller->SetBoneTrackKeys(SpineBone, Positions, Rotations, Scales);

    // 5. 关闭事务，提交更改（可撤销）
    Controller->CloseBracket();

    if (bSuccess)
    {
        UE_LOG(LogTemp, Warning, TEXT("Successfully added keys to spine_02 in %s"), *TargetAnimSequence->GetName());
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | 插件强制依赖，用于提供 FK 控制器和 Sequencer 控制逻辑 |
| `MovieScene` | 用于创建和操作内部的 MovieScene 序列数据 |
| `MovieSceneTools` | 提供 Sequencer 相关的编辑器工具和功能 |
| `Sequencer` | 核心 Sequencer 框架，用于轨道和区段管理 |
| `AnimationData` | 本插件自身的运行时模块 |

*注意：此插件的模块类型为 `UncookedOnly`，意味着它仅在编辑器和未打包版本中可用，不会包含在最终打包的游戏中。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `546a1036` | Fix residual "Unable to find Control Rig Track" outside of async anim compression | 修复了在异步动画压缩之外出现的“找不到控制绑定轨道”错误 |
| 2026-05-14 | `76d76853` | Add CVar that allows for using MovieScene GUID rather than channel hashing for partial-UAnimSequence | 增加了控制台变量，允许使用MovieScene GUID而非通道哈希来处理部分动画序列 |
| 2026-05-12 | `fc5fa56c` | [CrashReport][Assert] AnimationData!UAnimSequencerController::RemoveBoneTracksMissingFromSkeleton() | 修复了 `RemoveBoneTracksMissingFromSkeleton` 函数的断言崩溃问题 |
| 2026-05-12 | `956fbf23` | [CrashReport][Assert] AnimationData!UAnimSequencerController::SetCurveControlKey() | 修复了 `SetCurveControlKey` 函数的断言崩溃问题 |
| 2026-04-24 | `544e5099` | UE 5.8 Animation deprecation clean up (CL 1/10): Core Animation Runtime + AnimGraphRuntime + AnimGra | UE 5.8 动画废弃API清理（第1部分） |

### 维护评价

该插件**活跃维护中**。创建于2022年，属于相对较新的插件。从git历史看，2026年5月有多次提交，主要涉及错误修复（特别是崩溃修复）和功能优化（如增加控制台变量），表明其仍在被Epic Games团队积极使用和维护。作为 `UAnimSequence` 内部数据操作的核心实现，其稳定性对动画编辑流程至关重要。目前无已知的大型限制或废弃计划，推荐在需要进行程序化动画数据操作的场景中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationData)
- 官方文档：暂无
- 测试用例：通常位于 `Engine/Tests/Animation` 相关目录下（路径待确认）