# Spatially Aware Retarget Ops

> A collection of Retarget Ops for preserving spatial relationships on retargeted animations

| 属性 | 值 |
|---|---|
| 中文名 | 空间感知重定向操作 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画资产） |
| 模块 | `BodyIntersectIKOp` (Runtime), `PreviewPropOp` (Runtime), `RelativeBodyAnimInfo` (Runtime), `RelativeBodyAnimUtils` (Runtime), `RelativeIKOp` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-07-23 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp) | |

## 用途

该插件提供了一套专门用于动画重定向（Retarget）的 Retarget 操作（Ops），其核心功能是**在将动画从一个骨骼网格体重定向到另一个骨骼网格体时，保留身体各部分之间的空间关系**。它解决了一个常见问题：标准的 IK 重定向可能无法保持手脚与身体或其他部位的原始相对位置和接触关系（例如，一只手放在口袋里，或者双手交叉放在胸前），导致重定向后的动画出现穿模、悬空或位置偏移。通过计算和记录源动画中身体部位（如手、脚）相对于身体其他部位（如躯干、大腿）的空间关系，并在重定向时将这些关系应用到目标角色上，从而实现更真实、更具空间一致性的动画重定向结果。

## 使用场景

- 你正在为两个体型差异较大的角色（如高瘦角色与矮胖角色）进行动画重定向，需要保持手部与身体接触的动画（如手插口袋、扶墙）。
- 你在进行全身 IK 重定向时，希望保留源动画中肢体与环境的精确互动关系。
- 你需要批量处理大量动画序列，应用空间感知的重定向规则。
- 你的动画中包含了道具（如手持武器、工具）与角色身体的精确附着关系，需要在重定向后保持这种关系。

## 蓝图用法

该插件的核心蓝图节点主要集中在 `URelativeBodyAnimBlueprintFunctions` 和 `URelativeIKBulkExportHelper` 工具类中，用于批量设置和执行重定向操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BulkUpdateRelativeBodyModifiers` | 批量为一组动画序列应用或更新相对身体动画修改器，设置采样率、接触阈值等参数。 | `URelativeBodyAnimBlueprintFunctions` |
| `BulkUpdatePropBodyModifiers` | 批量为一组动画序列应用或更新包含道具信息的相对身体动画修改器。 | `URelativeBodyAnimBlueprintFunctions` |
| `SetRelativeAnimModifiers` | 批量设置相对动画修改器，适用于包含道具信息的复杂情况。 | `URelativeBodyAnimBlueprintFunctions` |
| `BulkRetargetSequences` | 使用指定的 IK 重定向器资产，批量执行动画序列的重定向并输出到指定路径。 | `URelativeIKBulkExportHelper` |

### 使用示例（蓝图描述）

**场景：批量应用空间感知重定向**
1. 在动画编辑器中选择一系列需要处理的 `UAnimSequence` 资产，创建一个数组（`AnimationList`）。
2. 创建一个 `FRelativeBodyAnimModifierOptions` 结构体变量，设置：
   - `SampleRate` (如 30Hz)
   - `ContactThreshold` (如 150.0)
   - `SkeletalMeshAsset` (目标骨骼网格体)
   - `PhysicsAssetOverride` (可选)
   - `DomainBodyNames` (需要检查关系的部位，如“head”, “spine_01”)
   - `ContactBodyNames` (需要保持接触的部位，如“hand_l”, “foot_r”)
3. 将上述数组和结构体连接到 `BulkUpdateRelativeBodyModifiers` 节点的输入引脚。
4. 执行该节点，插件会为列表中的每个动画序列计算并应用空间关系数据。

**场景：批量重定向动画**
1. 准备好一个配置好的 `UIKRetargeter` 资产。
2. 创建一个包含源动画序列的数组。
3. 调用 `BulkRetargetSequences` 节点，传入重定向器、序列数组、输出路径以及源/目标网格体（可选）。
4. 重定向后的动画将保存到指定路径。

## C++ 用法

插件的核心功能通过 `URelativeBodyAnimModifier` 和 `URelativePropsAnimModifier` 动画修改器实现，它们继承自 `UAnimationModifier`。

### 头文件引入

```cpp
#include "RelativeBodyAnimModifier.h"
#include "RelativePropsAnimModifier.h"
#include "RelativeBodyBlueprintFunctions.h"
```

### 基本用法

以下代码演示如何创建一个相对身体动画修改器并将其应用到单个动画序列中。

```cpp
// 假设你已经有了 InAnimationSequence 和 InSkeletalMesh 的引用
UAnimSequence* MyAnimation = /* ... */;
USkeletalMesh* MyMesh = /* ... */;

// 创建修改器实例
URelativeBodyAnimModifier* Modifier = NewObject<URelativeBodyAnimModifier>();

// 配置修改器参数
Modifier->SampleRate = 30;
Modifier->ContactThreshold = 150.0f;
Modifier->SkeletalMeshAsset = MyMesh;
Modifier->DomainBodyNames = { TEXT("head"), TEXT("spine_02") };
Modifier->ContactBodyNames = { TEXT("hand_l"), TEXT("hand_r") };

// 应用修改器到动画序列
Modifier->OnApply(MyAnimation);

// 保存动画序列以持久化通知数据
MyAnimation->Modify();
MyAnimation->PostEditChange();
```

**代码来源**：基于 `URelativeBodyAnimModifier::OnApply_Implementation` 的推断用法。

### 进阶用法

对于需要处理道具（如武器、工具）附着关系的复杂情况，可以使用 `URelativePropsAnimModifier`。

```cpp
// 创建包含道具信息的修改器
URelativePropsAnimModifier* PropModifier = NewObject<URelativePropsAnimModifier>();
PropModifier->SkeletalMeshAsset = MyMesh; // 角色的骨骼网格体

// 配置一个道具（例如，右手持剑）
FPropsInfo SwordProp;
SwordProp.PropStaticMeshAsset = SwordStaticMesh; // 武器的静态网格体
SwordProp.SocketName = TEXT("hand_r_socket"); // 附着到角色的插槽名
SwordProp.AttachTransform = FTransform(FRotator(0, 0, 90), FVector(10, 0, -5)); // 本地偏移

// 将道具信息添加到修改器
PropModifier->PropsData.Add(SwordProp);

// 配置公共参数并应用
PropModifier->SampleRate = 30;
PropModifier->ContactThreshold = 150.0f;
PropModifier->OnApply(MyAnimation);
```

**代码来源**：基于 `URelativePropsAnimModifier` 的属性和方法定义。

## Demo 示例

一个最小的、完整的 C++ 使用示例，展示如何将空间感知重定向功能集成到编辑器工具或运行时逻辑中。

**MyAnimationProcessor.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UAnimSequence;
class USkeletalMesh;
class URelativeBodyAnimModifier;

class FMyAnimationProcessor
{
public:
    /** 为单个动画应用空间感知修改器 */
    static void ApplySpatialModifierToAnimation(UAnimSequence* InAnimSequence, USkeletalMesh* InTargetMesh);

    /** 使用蓝图函数库批量处理 */
    static void BulkProcessAnimations(const TArray<UAnimSequence*>& Animations, USkeletalMesh* InTargetMesh);
};
```

**MyAnimationProcessor.cpp**
```cpp
#include "MyAnimationProcessor.h"
#include "RelativeBodyAnimModifier.h"
#include "RelativeBodyBlueprintFunctions.h"
#include "AnimSequence.h"

void FMyAnimationProcessor::ApplySpatialModifierToAnimation(UAnimSequence* InAnimSequence, USkeletalMesh* InTargetMesh)
{
    if (!InAnimSequence || !InTargetMesh) return;

    URelativeBodyAnimModifier* Modifier = NewObject<URelativeBodyAnimModifier>();
    Modifier->SkeletalMeshAsset = InTargetMesh;
    Modifier->SampleRate = 30;
    Modifier->ContactThreshold = 100.0f;
    Modifier->ContactBodyNames = { TEXT("foot_l"), TEXT("foot_r") };
    Modifier->DomainBodyNames = { TEXT("ground") }; // 简化的域定义

    // 应用修改器
    Modifier->OnApply(InAnimSequence);
    
    UE_LOG(LogTemp, Log, TEXT("Applied spatial modifier to: %s"), *InAnimSequence->GetName());
}

void FMyAnimationProcessor::BulkProcessAnimations(const TArray<UAnimSequence*>& Animations, USkeletalMesh* InTargetMesh)
{
    // 构造蓝图函数库所需的结构体
    FRelativeBodyAnimModifierOptions Options;
    Options.SkeletalMeshAsset = InTargetMesh;
    Options.SampleRate = 30;
    Options.ContactThreshold = 120.0f;
    Options.ContactBodyNames = { TEXT("hand_l"), TEXT("hand_r"), TEXT("foot_l"), TEXT("foot_r") };
    Options.DomainBodyNames = { TEXT("pelvis"), TEXT("spine_01"), TEXT("spine_02") };

    // 使用蓝图函数库的批量更新功能
    // 注意：函数签名要求非常量引用，因此这里需要一个非const的拷贝
    TArray<UAnimSequenceBase*> AnimBases;
    for (UAnimSequence* Anim : Animations)
    {
        AnimBases.Add(Cast<UAnimSequenceBase>(Anim));
    }
    URelativeBodyAnimBlueprintFunctions::BulkUpdateRelativeBodyModifiers(AnimBases, Options);

    UE_LOG(LogTemp, Log, TEXT("Bulk processed %d animations."), Animations.Num());
}
```

## 模块依赖

从插件的模块结构（均为Runtime类型）和功能推断，你的模块若想使用此插件的功能，除了标准的Core/Engine模块外，可能需要依赖以下模块。具体依赖关系需查看每个子模块的 `Build.cs` 文件。

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 动画核心数据结构和工具（如 `FAnimPose`） |
| `AnimationBlueprintLibrary` | 用于操作动画序列和通知 |
| `PhysicsCore` / `Engine` | 物理资产（`UPhysicsAsset`）访问 |
| `MeshDescription` | 网格描述数据，用于计算顶点位置 |
| `IKRetargeter` | 核心的 IK 重定向框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-23 | `b70e3bb0` | [IK Retargeter] Add NotOverrideable meta to scalar TArrays in RelativeIK plugin retarget ops | 为插件重定向操作中的标量TArray添加NotOverrideable元数据，防止被意外覆盖。 |
| 2026-04-14 | `66a98b79` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF，进行日志系统升级。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF，进行日志系统升级。 |
| 2026-04-14 | `701659c5` | RIK: Prop Intersection Pushout fix | 修复了道具相交时的推离（Pushout）逻辑问题。 |
| 2026-04-08 | `23ef9e5c` | RelativeIK: Prop push out | 添加了道具在相交时的推离功能。 |

### 维护评价

该插件创建于2025年7月，目前年龄不足1年，属于**全新插件**。从近期更新记录看，开发团队在2026年4月仍对其进行了活跃的功能添加（道具推离）和底层维护（日志系统升级、元数据优化）。插件状态为**实验性**且默认未启用，表明它可能处于早期测试或整合阶段。鉴于其较新且最近有实质性功能更新，目前处于**活跃维护**状态。然而，作为实验性功能，其API和工作流在未来版本中可能会有较大变动。建议在非关键项目中试用，并密切关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/RelativeIKOp)
- [官方文档]() （暂无）