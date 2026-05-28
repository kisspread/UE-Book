# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画蓝图资产、动画通知） |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

该插件旨在解决动画重定向过程中空间关系丢失的问题。当一个角色的动画被重定向到另一个比例或骨骼结构不同的角色时，简单的骨骼映射无法保留原始动画中身体部位之间（如手与腰）或身体与道具之间（如手持武器）的精确接触点和相对空间关系。

这个插件提供了一套 Retarget Ops（重定向操作），其核心功能是在重定向前“烘焙”（Bake）源动画中身体部位之间、以及身体与道具之间的相对位置信息，并将这些空间约束数据存储在动画通知（AnimNotify）中。在目标角色播放重定向后的动画时，这些通知被触发，系统利用存储的约束数据，结合目标角色的当前骨骼姿态，通过 IK（反向动力学）等技术，动态地调整身体部位或道具的位置，从而最大限度地保留原始动画中的空间接触和交互关系。

简单来说，它让重定向后的动画不仅骨骼动作相似，连“手摸到哪里”、“武器放在哪里”这些细节也尽量保持一致。

## 使用场景

-   **角色换装/体型差异大的动画迁移**：当从一个体型标准的角色动画，重定向到一个体型差异巨大的角色（如从成人到儿童，或正常体型到魁梧体型）时，使用此插件可以防止手臂穿入身体、武器悬浮等穿帮问题。
-   **需要精确道具交互的动画**：在动作游戏或剧情动画中，当角色需要做出精确的持枪、握剑、扶墙等动作时，此插件能确保重定向后，道具（如武器）与角色身体的相对位置保持正确。
-   **保留身体接触点的攀爬或格斗动画**：对于涉及角色之间或角色与环境有特定接触点的动画（如格斗中的击打点、攀爬时的抓握点），此插件能维持这些关键空间信息。

## 蓝图用法

该插件的核心功能通过动画通知（AnimNotify）类暴露给蓝图，允许用户在动画中添加这些通知来触发空间关系重定向逻辑。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnRelativeBodyDenseNotify` | 蓝图可实现事件。接收一组烘焙好的身体部位对之间的相对空间约束数据，用于驱动IK以校正身体部位位置。 | `URelativeBodyBakeAnimNotify` |
| `OnRelativeBodyAnimNotify` | 蓝图可实现事件。接收单个身体部位对（如手和腰）之间的相对空间约束数据，用于驱动IK以校正该对部位的位置。 | `URelativeBodyPerFrameAnimNotify` |
| `OnRelativePropsDenseNotify` | 蓝图可实现事件。接收一组烘焙好的道具与身体部位之间的相对空间约束数据，用于调整道具位置。 | `URelativePropsBakeAnimNotify` |

### 使用示例（蓝图描述）

1.  **添加通知**：在动画编辑器的时间轴上，为需要进行空间关系校正的动画添加通知。根据需求选择 `RelativeBodyBakeAnimNotify`（批量身体对）或 `RelativeBodyPerFrameAnimNotify`（单个身体对）。
2.  **配置通知**：在通知的细节面板中，你会看到“预烘焙”或运行时填充的属性，如 `BodyPairs`、`BodyPairsLocalReference` 等。这些数据通常由插件的其他工具模块（如 `RelativeIKOp`）在动画处理或编辑器中生成并填充。
3.  **实现事件**：选中添加的通知，在蓝图编辑器中重写（Override）对应的 `BlueprintImplementableEvent`（如 `OnRelativeBodyDenseNotify`）。
4.  **逻辑实现**：在事件图表中，你可以接收到如 `BodyPairs`（身体对名称）、`BodyPairsLocalReference`（局部参考点）等参数。你需要编写逻辑，获取目标角色的 `SkeletalMeshComponent`，结合这些空间约束数据，计算出所需的IK目标位置，并将其应用到相应的骨骼链上，从而实现空间关系的校正。

## C++ 用法

### 头文件引入

```cpp
#include "RelativeBodyAnimNotifies.h"
```

### 基本用法：创建并响应单个身体部位对通知

以下示例展示了如何在 C++ 中创建一个 `URelativeBodyPerFrameAnimNotify` 子类，并重写其通知函数以处理单个身体部位对的空间关系。

```cpp
// 来源：基于 URelativeBodyPerFrameAnimNotify 的用法模式推断
#include "UObject/ConstructorHelpers.h"
#include "Animation/AnimSequenceBase.h"
#include "Components/SkeletalMeshComponent.h"

UCLASS()
class UMyHandOnHipNotify : public URelativeBodyPerFrameAnimNotify
{
    GENERATED_BODY()

public:
    UMyHandOnHipNotify()
    {
        // 可以在这里设置一些默认属性
    }

    // 重写 Notify 函数，直接在 C++ 层处理逻辑，而不通过蓝图事件
    virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override
    {
        // 调用父类的 Notify，它会触发 OnRelativeBodyAnimNotify 蓝图事件
        // 如果你希望完全在 C++ 处理，可以不调用父类，直接在此实现逻辑。
        Super::Notify(MeshComp, Animation, EventReference);

        // 或者，直接访问成员变量来获取数据
        // body1, body2, loc1, loc2, bIsParentDominates, SkeletalMeshAsset
        
        // 在这里实现你的 IK 解算逻辑
        // 例如：使用 MeshComp 和计算出的目标位置来驱动 IK
    }
};
```

### 进阶用法：处理烘焙的批量数据

处理 `URelativeBodyBakeAnimNotify` 的大量烘焙数据通常更复杂，需要遍历数据对并应用约束。

```cpp
// 来源：基于 URelativeBodyBakeAnimNotify 的数据结构推断
void UMyAnimInstance::ProcessBakedBodyConstraints(
    const URelativeBodyBakeAnimNotify* Notify,
    USkeletalMeshComponent* MeshComp)
{
    if (!Notify || !MeshComp) return;

    // 获取烘焙数据的引用
    const TArray<FName>& BodyPairs = Notify->BodyPairs;
    const TArray<FVector3f>& LocalRefs = Notify->BodyPairsLocalReference;
    const TMap<FName, FTransform>& Offsets = Notify->OffsetTransformsForBones;

    int32 NumPairs = BodyPairs.Num();

    // 遍历所有身体对约束
    for (int32 i = 0; i < NumPairs; ++i)
    {
        FName PairName = BodyPairs[i];
        // 假设 LocalRefs 是按 `Body1, Loc1, Body2, Loc2` 的顺序交错存储
        FVector3f Body1Loc = LocalRefs[i * 2];
        FVector3f Body2Loc = LocalRefs[i * 2 + 1];

        // 使用 MeshComp 的骨骼变换和这些局部参考点，计算出世界空间中的目标位置
        // 然后应用 IK 解算（如 FABRIK, CCDIK）来调整骨骼链以满足约束
        // ... IK 解算逻辑 ...
    }
}
```

## Demo 示例

一个最小的示例，展示如何创建一个简单的、只处理一对身体部位约束的动画通知子类。

```cpp
// MySimpleRelativeNotify.h
#pragma once

#include "CoreMinimal.h"
#include "RelativeBodyAnimNotifies.h"
#include "MySimpleRelativeNotify.generated.h"

UCLASS()
class UMySimpleRelativeNotify : public URelativeBodyPerFrameAnimNotify
{
    GENERATED_BODY()

public:
    // 蓝图可调用的设置函数，用于在编辑器或运行时设置约束数据
    UFUNCTION(BlueprintCallable, Category="Animation|RelativeIK")
    void SetupConstraint(FName InBody1, FName InBody2, const FVector& InLocalRef1, const FVector& InLocalRef2);

    // 重写 Notify 以添加自定义逻辑
    virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;

private:
    // 可以添加额外的成员变量
    UPROPERTY()
    bool bAppliedThisFrame = false;
};
```

```cpp
// MySimpleRelativeNotify.cpp
#include "MySimpleRelativeNotify.h"
#include "Animation/AnimSequenceBase.h"
#include "Components/SkeletalMeshComponent.h"
#include "DrawDebugHelpers.h"

void UMySimpleRelativeNotify::SetupConstraint(FName InBody1, FName InBody2, const FVector& InLocalRef1, const FVector& InLocalRef2)
{
    // 调用父类函数来设置核心数据
    SetInfo(nullptr, InBody1, InBody2,
            FVector3f(InLocalRef1), FVector3f(InLocalRef2), false);
    // SkeletalMeshAsset 在这里设为 nullptr，实际使用时可能需要从组件获取
}

void UMySimpleRelativeNotify::Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference)
{
    // 先调用父类，触发蓝图事件
    Super::Notify(MeshComp, Animation, EventReference);

    // 在此处添加 C++ 层的调试或逻辑
    if (MeshComp && bAppliedThisFrame == false)
    {
        // 例如，绘制调试线段显示约束点
        FVector WorldLoc1 = MeshComp->GetBoneLocation(body1) + MeshComp->GetBoneRotation(body1).RotateVector(FVector(loc1));
        FVector WorldLoc2 = MeshComp->GetBoneLocation(body2) + MeshComp->GetBoneRotation(body2).RotateVector(FVector(loc2));
        DrawDebugLine(MeshComp->GetWorld(), WorldLoc1, WorldLoc2, FColor::Green, false, 0.03f, 0, 2.0f);
        bAppliedThisFrame = true;
    }
}

// 在构造函数中（例如在游戏模块启动时）注册此通知类型，使其可以在编辑器中选择
UMySimpleRelativeNotify::UMySimpleRelativeNotify()
{
    // 确保 SkeletalMeshAsset 有效
    SkeletalMeshAsset = nullptr; // 实际应设置一个有效的网格体
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供核心的动画数据结构和工具，如骨骼变换计算。 |
| `Engine` | UE引擎核心模块，包含 `SkeletalMeshComponent`、`AnimSequenceBase` 等基础类。 |
| `AnimationBudgetAllocator` | （可能）用于优化大量动画通知的性能。 |

*注：以上依赖基于插件功能推断。具体依赖列表需查阅各子模块的 `.Build.cs` 文件。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为插件中的重定向操作添加了防止标量数组被覆盖的元数据。 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移为UE_LOGF，统一日志格式。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 同上，日志系统迁移。 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具相交推出逻辑中的问题。 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 实现了道具与环境碰撞后的推出功能。 |

### 维护评价

该插件创建于2025年7月，至今约1年，**仍在活跃维护中**。近期（2026年4月）有多次连续提交，主要涉及功能修复（如道具推出）、代码质量改进（日志迁移）以及编辑器集成优化（添加属性元数据）。插件标记为**实验性**（IsExperimentalVersion=true）且**默认未安装**（Installed=false），表明其处于开发验证阶段，API和功能可能发生变化。目前没有观察到明确的废弃标记。

**推荐使用**：对于在开发中遇到动画重定向后空间关系丢失问题的团队，特别是处理复杂角色交互或道具动画的项目，此插件值得一试。但由于其为实验性功能，建议在生产环境中谨慎评估，并准备好跟进其后续的API变更。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)