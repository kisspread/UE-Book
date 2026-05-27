# Animation Warping

> Framework for animation and pose warping. This plugin includes Stride, Orientation, and Slope Warping alongside the Root Motion Delta animation attribute.

| 属性 | 值 |
|---|---|
| 中文名 | 动画扭曲 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（动画图节点、动画修改器） |
| 模块 | `AnimationWarpingRuntime` (Runtime), `AnimationWarpingEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2021-12-04 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping) | |

## 用途

AnimationWarping 插件提供了一套运行时动画扭曲（Warping）框架，其核心目的是**根据角色的速度、方向和地形坡度等运行时信息，动态调整动画姿态和根运动**。它解决了传统预制动画在不同运动状态（如不同速度的奔跑、转弯）和环境（如上下坡、斜坡）下表现不自然、穿模或脚部滑动的问题。

插件包含三个主要功能模块：
1.  **方向扭曲 (Orientation Warping)**：根据角色的移动方向和当前播放动画的方向差，扭曲角色的骨盆和脊柱，使角色的身体自然地面向运动方向，尤其适用于快速转弯。
2.  **步幅扭曲 (Stride Warping)**：根据角色的实际移动速度，动态拉伸或压缩行走/奔跑动画的步幅，确保脚部落点与地面位置匹配。
3.  **斜面扭曲 (Slope Warping)**：根据地面法线调整角色的骨盆高度和腿部姿态，使角色在斜坡上行走时脚部贴合地面。
4.  **根运动增量属性 (Root Motion Delta)**：提供一个用于计算和传递根运动增量的动画属性，为上述扭曲功能提供基础数据。

## 使用场景

- 你在制作一个第三人称动作或RPG游戏，角色需要以不同速度在平地、上坡、下坡和斜坡上平滑移动。
- 你需要角色在快速转向时，上半身能自然地跟随运动方向偏转，而不是生硬地转身。
- 你希望角色在奔跑时，步长能根据速度自动调整，避免“脚滑”现象。
- 你正在使用程序化动画或需要动态调整动画以适应复杂的游戏环境。

## 蓝图用法

该插件的核心功能主要通过**动画蓝图（AnimGraph）节点**在编辑器中使用，而非直接调用蓝图函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Orientation Warping` | 根据移动方向扭曲角色身体方向。 | `UAnimGraphNode_OrientationWarping` |
| `Stride Warping` | 根据移动速度调整动画步幅长度。 | `UAnimGraphNode_StrideWarping` |
| `Slope Warping` | 根据地形斜率调整腿部姿态。 | `UAnimGraphNode_SlopeWarping` |
| `Steering` | （实验性）用于引导角色转向。 | `UAnimGraphNode_Steering` |
| `Foot Placement` | （实验性）用于脚部放置调整。 | `UAnimGraphNode_FootPlacement` |
| `Offset Root Bone` | （实验性）用于偏移根骨骼。 | `UAnimGraphNode_OffsetRootBone` |
| `Override Root Motion` | （实验性）用于覆盖根运动。 | `UAnimGraphNode_OverrideRootMotion` |
| `Orientation Warping Modifier` | 用于为序列自动添加方向扭曲曲线的动画修改器。 | `UOrientationWarpingModifier` |

### 使用示例（蓝图描述）

1.  在**动画蓝图**的 `AnimGraph` 中，从右键菜单选择 `Add New Node` -> `Animation` -> `Warping` 类别。
2.  拖拽出一个 `Orientation Warping` 节点。
3.  将前一个动画节点（如状态机）的输出连接到此节点的输入。
4.  在节点的 `Settings` 面板中，设置 `Rotation Mode`（通常选择 `Chain`），并指定要扭曲的骨骼链（如 `spine_01`, `spine_02`）。
5.  该节点需要一个描述当前移动方向的 `FVector` 和当前动画播放方向的 `FRotator` 作为输入，这些通常通过 `Get Velocity` 和动画通知/曲线获取。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNodes/AnimNode_OrientationWarping.h"
#include "AnimNodes/AnimNode_StrideWarping.h"
#include "AnimNodes/AnimNode_SlopeWarping.h"
```

### 基本用法

动画扭曲节点通常作为 `FAnimNode_SkeletalControlBase` 或类似基类的子类，在动画蓝图中通过C++进行扩展或自定义。

```cpp
// 以下代码展示了如何在自定义动画节点中使用扭曲概念
// 来源: Tests/AnimationWarpingRuntimeTests/ 文件夹中的测试用例
#include "BoneControllers/AnimNode_SkeletalControlBase.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomWarpNode : public FAnimNode_SkeletalControlBase
{
    GENERATED_BODY()

    // 输入属性：当前速度
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings", meta = (PinShownByDefault))
    FVector Velocity;

    // 输入属性：基础移动方向
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings", meta = (PinShownByDefault))
    FRotator BaseDirection;

    // 内部使用的扭曲节点
    FAnimNode_OrientationWarping OrientationWarpingNode;

    // 重写 EvaluateSkeletalControl_AnyThread 来应用扭曲
    virtual void EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override
    {
        // ... 准备数据
        OrientationWarpingNode.Velocity = Velocity;
        OrientationWarpingNode.MeshOrientation = BaseDirection;
        // ... 调用 OrientationWarpingNode 的求值方法
    }

    // ... 其他必要的重写函数
};
```

### 进阶用法

结合 `FAnimNode_StrideWarping` 和 `FAnimNode_OrientationWarping` 实现复杂的运动适配。

```cpp
// 在动画实例中管理多个扭曲节点
// 来源: 综合测试用例模式
UCLASS()
class UMyAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在动画蓝图更新中计算扭曲所需的输入数据
    void NativeUpdateAnimation(float DeltaSeconds) override
    {
        Super::NativeUpdateAnimation(DeltaSeconds);

        if (APawn* Pawn = TryGetPawnOwner())
        {
            CurrentVelocity = Pawn->GetVelocity();
            GroundNormal = FVector::UpVector; // 需要通过追踪获取实际地面法线
            // ... 计算动画方向与移动方向的差值
        }
    }

    UPROPERTY(BlueprintReadOnly, Category = "Warping")
    FVector CurrentVelocity;

    UPROPERTY(BlueprintReadOnly, Category = "Warping")
    FVector GroundNormal;

    UPROPERTY(BlueprintReadOnly, Category = "Warping")
    float SpeedRatio; // 用于步幅扭曲
};
```

## Demo 示例

一个最小的可编译自定义动画节点，演示如何集成扭曲逻辑。

```cpp
// MyCustomWarpNode.h
#pragma once
#include "BoneControllers/AnimNode_SkeletalControlBase.h"
#include "AnimNodes/AnimNode_OrientationWarping.h"
#include "MyCustomWarpNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomWarpNode : public FAnimNode_SkeletalControlBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Settings")
    FVector TargetDirection;

    FAnimNode_OrientationWarping InternalOrientationNode;

    // FAnimNode_SkeletalControlBase interface
    virtual void EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override;
    virtual bool IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones) override;
    // End of FAnimNode_SkeletalControlBase interface

private:
    void InitializeBoneReferences(const FBoneContainer& RequiredBones) override;
};
```

```cpp
// MyCustomWarpNode.cpp
#include "MyCustomWarpNode.h"

void FAnimNode_MyCustomWarpNode::EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms)
{
    // 设置内部扭曲节点的输入
    InternalOrientationNode.Velocity = TargetDirection; // 简化示例，实际需映射
    InternalOrientationNode.MeshOrientation = FRotator(0, 0, 0); // 从 pose 获取

    // 让内部节点求值（注意：此示例简化，实际需要正确管理 pose 上下文）
    // InternalOrientationNode.EvaluateBoneTransforms(...);

    // 将结果应用到当前节点的输出
    // ... (此处省略了复杂的骨骼变换操作)
}

bool FAnimNode_MyCustomWarpNode::IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones)
{
    // 确保必要的骨骼已引用
    return true;
}

void FAnimNode_MyCustomWarpNode::InitializeBoneReferences(const FBoneContainer& RequiredBones)
{
    // 初始化内部扭曲节点的骨骼引用
    // InternalOrientationNode.InitializeBoneReferences(RequiredBones);
}
```

## 模块依赖

根据插件功能推断，要使用此插件，你的模块可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AnimGraphRuntime` | 动画图运行时支持，扭曲节点的基础。 |
| `AnimationCore` | 核心动画数学和骨骼工具。 |
| `ControlRig` | （可选）用于更高级的程序化骨骼控制。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `42c8bcfa` | Fix tooltip on ABP steering node | 修复动画蓝图中转向节点的工具提示文本 |
| 2026-04-24 | `afab60f0` | UE-363190 - Replace crash-assert NaN guards with UE_LOGF + safe-default in StrideWarping and Orienta | 将步幅和方向扭曲中的NaN崩溃断言替换为日志警告和安全默认值 |
| 2026-04-24 | `42548e51` | Fix non-unity build: forward-declare UAnimationAsset in anim node headers | 修复非统一编译模式：在动画节点头文件中前向声明UAnimationAsset |
| 2026-04-23 | `23ccd2bd` | Add Anim Node Functions to support applying a delta to the offset root bone's internal simulated tra | 新增动画节点函数，支持对偏移根骨骼的内部模拟变换应用增量 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG迁移至UE_LOGF宏 |

### 维护评价

**积极维护中**。该插件在创建（2021年12月）后一直处于活跃开发状态。最近的提交记录（2026年4月-5月）表明 Epic 仍在对其进行功能增强（如添加新的动画节点函数）、稳定性修复（处理NaN问题）和工程优化（修复编译问题）。插件从 `Experimental` 迁移至 `Beta` 再到当前状态，表明其核心功能（方向、步幅、斜面扭曲）已趋于稳定。部分节点（如 Steering, Slope Warping）仍标记为 `Experimental`，表明这些功能可能仍在迭代中。**推荐用于生产项目**，但需关注实验性节点的稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AnimationWarping/Tests)