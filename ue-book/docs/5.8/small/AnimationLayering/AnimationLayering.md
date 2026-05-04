# Animation Layering

> （.uplugin 的 Description 字段为空）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationLayering` (Runtime), `AnimationLayeringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimationLayering) | |

## 用途

AnimationLayering 插件提供了一套高级的动画层叠和骨骼遮罩工具，旨在解决复杂角色动画中需要精细控制身体不同部位动画混合的需求。它扩展了引擎内置的 `AnimNode_LayeredBoneBlend`，通过引入“身体部位 (Body Part)”概念，允许开发者以更直观、动态的方式定义和混合动画层。此外，它还包含用于高级骨骼复制的节点，支持更灵活的运动传递和骨骼控制。

## 使用场景

- **角色装备系统**：当角色穿戴不同装备（如盔甲、背包）时，需要为装备影响的身体部位（如肩部、背部）叠加独立的动画层，同时保持其他部位动画不变。
- **动态动画混合**：需要根据游戏逻辑（如受伤状态、技能释放）在运行时动态调整身体特定部位（如手臂、腿部）的动画权重。
- **精确骨骼运动复制**：需要将一个骨骼的运动（如武器挥舞）精确地复制到另一个骨骼（如角色手部），并支持延迟、空间转换和分轴控制。

## 蓝图用法

该插件主要提供动画蓝图节点，其属性可在动画蓝图编辑器中配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BoneMask` | 基于身体部位定义的动态骨骼遮罩混合节点。 | `FAnimNode_BoneMask` |
| `CopyBoneAdvanced` | 高级骨骼复制节点，支持分轴权重和空间转换。 | `FAnimNode_CopyBoneAdvanced` |
| `CopyBoneMotion` | 从源骨骼或历史姿态复制运动到目标骨骼的节点。 | `FAnimNode_CopyBoneMotion` |

### 使用示例（蓝图描述）

1.  **使用 `BoneMask` 节点**：
    *   在动画蓝图中添加 `BoneMask` 节点。
    *   连接一个基础姿态（`BasePose`）和多个需要混合的动画姿态（`BlendPoses`）。
    *   在 `BodyParts` 数组中为每个混合姿态指定对应的身体部位名称（如 `“UpperBody”`, `“LeftArm”`）。
    *   通过 `BlendWeights` 数组或 `BoneMask` 属性中的 `BoneMaskMap`，在运行时动态设置每个身体部位的混合权重（`LocalSpaceWeight` 和 `MeshSpaceWeight`）。

2.  **使用 `CopyBoneAdvanced` 节点**：
    *   在动画蓝图中添加 `CopyBoneAdvanced` 节点。
    *   设置 `SourceBone`（源骨骼）和 `TargetBone`（目标骨骼）。
    *   调整 `TranslationWeight`、`RotationWeight` 和 `ScaleWeight` 来控制复制的强度。
    *   可选地设置 `ControlSpace` 和 `TranslationSpaceBone` 来定义复制操作的空间。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNode_BoneMask.h"
#include "BoneControllers/AnimNode_CopyBoneAdvanced.h"
#include "BoneControllers/AnimNode_CopyBoneMotion.h"
#include "BoneMaskTypes.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建和配置 `FAnimNode_BoneMask` 节点。

```cpp
// 假设在某个动画实例或自定义节点中
FAnimNode_BoneMask BoneMaskNode;

// 1. 配置身体部位定义
FBoneMaskBodyPartDefinition UpperBodyDef;
UpperBodyDef.Name = FName("UpperBody");
UpperBodyDef.BranchFilters.Add(FBranchFilter(FName("spine_01"), MAX_int32)); // 从spine_01开始的所有子骨骼
BoneMaskNode.BoneMaskDefinitionDataAsset->BoneMaskDefinition.AddBodyPartDefinition(UpperBodyDef.Name, UpperBodyDef.BranchFilters);

// 2. 在运行时设置混合权重
FBoneMaskEntry& UpperBodyEntry = BoneMaskNode.BoneMask.BoneMaskMap.FindOrAdd(FName("UpperBody"));
UpperBodyEntry.LocalSpaceWeight = 0.8f; // 80% 本地空间混合
UpperBodyEntry.MeshSpaceWeight = 0.2f;  // 20% 网格空间混合

// 3. 设置整体层混合权重
BoneMaskNode.BlendWeights[0] = 1.0f; // 第一个混合姿态的权重
```

### 进阶用法

结合 `FAnimNode_CopyBoneMotion` 实现带延迟的运动复制。

```cpp
FAnimNode_CopyBoneMotion CopyMotionNode;

// 配置从姿态历史中复制运动，并设置延迟
CopyMotionNode.bUseBasePose = false; // 使用姿态历史而非直接输入姿态
CopyMotionNode.PoseHistoryTag = FName("MainPoseHistory");
CopyMotionNode.Delay = 0.1f; // 100毫秒延迟

// 设置源和目标骨骼
CopyMotionNode.SourceBone.BoneName = FName("weapon_r");
CopyMotionNode.BoneToModify.BoneName = FName("hand_r");

// 配置应用空间
CopyMotionNode.ApplySpace.BoneName = FName("upperarm_r");
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在自定义动画实例中使用 `FAnimNode_BoneMask`。

**MyAnimInstance.h**
```cpp
#pragma once
#include "Animation/AnimInstance.h"
#include "AnimNode_BoneMask.h"
#include "MyAnimInstance.generated.h"

UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    virtual void NativeInitializeAnimation() override;
    virtual void NativeUpdateAnimation(float DeltaSeconds) override;

private:
    // 在动画蓝图中通过 `Linked Anim Graph` 或 `Proxy` 使用此节点
    UPROPERTY(Transient)
    FAnimNode_BoneMask BoneMaskNode;

    // 动态权重变量
    float CurrentUpperBodyWeight = 0.0f;
};
```

**MyAnimInstance.cpp**
```cpp
#include "MyAnimInstance.h"
#include "BoneMaskTypes.h"

void UMyAnimInstance::NativeInitializeAnimation()
{
    Super::NativeInitializeAnimation();

    // 初始化节点（通常由动画蓝图系统处理，此处仅为演示）
    // BoneMaskNode 的初始化通常发生在动画图编译时。
}

void UMyAnimInstance::NativeUpdateAnimation(float DeltaSeconds)
{
    Super::NativeUpdateAnimation(DeltaSeconds);

    // 模拟动态更新权重
    CurrentUpperBodyWeight = FMath::FInterpTo(CurrentUpperBodyWeight, 0.5f, DeltaSeconds, 2.0f);

    // 更新 BoneMask 节点中的权重
    if (FBoneMaskEntry* Entry = BoneMaskNode.BoneMask.BoneMaskMap.Find(FName("UpperBody")))
    {
        Entry->LocalSpaceWeight = CurrentUpperBodyWeight;
        Entry->MeshSpaceWeight = 1.0f - CurrentUpperBodyWeight;
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AnimationCore` | 提供动画系统核心类型和工具。 |
| `AnimGraphRuntime` | 提供动画图运行时节点基类和功能。 |

## 维护状态

### 近期更新

- 2026-04-17 (创建时间) 插件初始创建，包含核心动画层叠和骨骼复制功能。

### 维护评价

- **创建时间**：2026年4月，是一个非常新的插件。
- **更新频率**：目前仅有初始提交，尚无后续更新记录。
- **活跃状态**：作为实验性插件刚被引入，处于早期开发阶段。
- **已知限制**：标记为 `IsExperimentalVersion: true`，且 `EnabledByDefault: false`，表明其API和功能可能不稳定，不建议在生产环境中直接使用。
- **推荐度**：**谨慎使用**。适合用于原型开发和功能探索。在生产项目中使用前，需密切关注其后续更新和稳定性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Animation/AnimationLayering)
- [测试用例]（路径未知，通常位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录）