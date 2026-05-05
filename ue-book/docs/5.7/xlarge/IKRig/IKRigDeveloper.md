# IK Rig

> （Description from .uplugin is empty）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画蓝图节点、资产类型） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (UncookedOnly), `IKRigEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig) | |

## 用途

IK Rig 插件提供了一套用于创建和运行时驱动 **IK（反向运动学）解算器** 的框架，并集成了 **IK 重定向** 功能。它解决了以下核心问题：

1.  **程序化 IK 控制**：允许开发者在动画蓝图中为角色骨骼（如手、脚）创建 IK 目标（Goals），并实时驱动骨骼链到达这些目标，实现抓取、脚部贴地等效果。
2.  **动画重定向**：通过 `AnimNode_RetargetPoseFromMesh` 节点，可以将一个骨骼网格体的动画姿态，实时重定向到另一个具有不同骨骼结构的网格体上，是实现跨角色动画共享的关键工具。

它本质上是一个**动画蓝图节点库和资产系统**，让复杂的 IK 设置和动画重定向工作流可以在编辑器中可视化配置，并在运行时高效执行。

## 使用场景

-   你需要为角色的手部或脚部添加 IK，使其能准确地抓住物体或踩在不平坦的地面上 → 使用 `AnimNode_IKRig` 节点和 `IKRig` 资产。
-   你有一个标准人形角色的动画，想把它应用到另一个骨骼比例或结构不同的角色（如从写实人形到卡通角色）上 → 使用 `AnimNode_RetargetPoseFromMesh` 节点和 `IKRetargeter` 资产。
-   你希望在动画蓝图中以可视化、节点化的方式配置复杂的 IK 链和目标，而不是编写大量 C++ 代码 → 使用 `UAnimGraphNode_IKRig` 和 `UAnimGraphNode_RetargetPoseFromMesh` 蓝图节点。

## 蓝图用法

IKRig 的核心功能通过动画蓝图节点暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IK Rig` | 在动画蓝图中应用一个 `IKRig` 资产，驱动骨骼链到达指定的目标（Goals）。 | `UAnimGraphNode_IKRig` |
| `Retarget Pose From Mesh` | 从另一个骨骼网格体组件复制动画姿态，并使用 `IKRetargeter` 资产将其重定向到当前角色。 | `UAnimGraphNode_RetargetPoseFromMesh` |

### 使用示例（蓝图描述）

1.  **IK Rig 节点**：
    -   在动画蓝图的事件图表中，添加一个 `IK Rig` 节点。
    -   在节点的细节面板中，指定一个已创建的 `IKRig` 资产。
    -   节点会暴露该 `IKRig` 资产中定义的所有 `Goal`（如 `LeftHandGoal`, `RightFootGoal`）作为输入引脚。
    -   将这些 Goal 引脚连接到其他节点（如 `Transform (Modify) Bone` 节点或蓝图变量），以在运行时动态设置目标位置和旋转。
    -   节点的输出是经过 IK 解算后的最终骨骼姿态。

2.  **Retarget Pose From Mesh 节点**：
    -   在动画蓝图中添加 `Retarget Pose From Mesh` 节点。
    -   在细节面板中，指定一个 `IKRetargeter` 资产。
    -   通过 `Source Mesh Component` 引脚，连接到场景中另一个角色的骨骼网格体组件引用（例如，通过 `Get Player Character` -> `Get Mesh` 获取）。
    -   节点会从源组件获取当前动画姿态，应用重定向规则，并输出重定向后的姿态。

## C++ 用法

### 头文件引入

```cpp
#include "AnimNodes/AnimNode_IKRig.h"
#include "AnimNodes/AnimNode_RetargetPoseFromMesh.h"
```

### 基本用法

以下代码展示了如何在 C++ 中创建和配置一个 `FAnimNode_IKRig` 实例（通常在自定义动画节点或组件中）。

```cpp
// 假设在某个动画实例或组件中
FAnimNode_IKRig MyIKRigNode;

// 设置要使用的 IKRig 资产
MyIKRigNode.IKRigAsset = LoadObject<UIKRigDefinition>(nullptr, TEXT("/Game/Characters/Humanoid/IK_Humanoid"));

// 设置一个 Goal 的目标变换 (例如，左手目标)
FTransform HandTargetTransform = /* 从世界空间或其他逻辑计算得出 */;
MyIKRigNode.SetGoalTransform(TEXT("LeftHandGoal"), HandTargetTransform);

// 在动画更新流程中调用 Evaluate 来执行 IK 解算
// MyIKRigNode.Evaluate(OutputPose, Context);
```

### 进阶用法

`AnimNode_RetargetPoseFromMesh` 通常在动画蓝图中使用，但其底层逻辑也可以通过 C++ 访问。关键在于正确设置 `IKRetargeter` 资产和源网格体组件。

```cpp
// 在自定义动画节点中
FAnimNode_RetargetPoseFromMesh RetargetNode;

// 设置重定向器资产
RetargetNode.IKRetargeterAsset = LoadObject<UIKRetargeter>(nullptr, TEXT("/Game/Retarget/RTG_HumanoidToQuadruped"));

// 在运行时，需要动态设置源网格体组件
// 这通常通过蓝图引脚暴露，但在纯 C++ 中，你可能需要缓存一个指向源组件的指针
// RetargetNode.SourceMeshComponent = SomeOtherSkeletalMeshComponent;
```

## Demo 示例

一个最小的自定义动画节点，内部使用 `FAnimNode_IKRig` 来应用 IK。

**MyCustomIKNode.h**
```cpp
#pragma once
#include "BoneControllers/AnimNode_SkeletalControlBase.h"
#include "AnimNodes/AnimNode_IKRig.h"
#include "MyCustomIKNode.generated.h"

USTRUCT(BlueprintInternalUseOnly)
struct FAnimNode_MyCustomIK : public FAnimNode_SkeletalControlBase
{
    GENERATED_BODY()

    // 内嵌的 IKRig 节点
    UPROPERTY(EditAnywhere, Category = "IK")
    FAnimNode_IKRig IKRigNode;

    // FAnimNode_SkeletalControlBase interface
    virtual void InitializeBoneReferences(const FBoneContainer& RequiredBones) override;
    virtual void EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms) override;
    virtual bool IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones) override;
    // End of interface
};
```

**MyCustomIKNode.cpp**
```cpp
#include "MyCustomIKNode.h"

void FAnimNode_MyCustomIK::InitializeBoneReferences(const FBoneContainer& RequiredBones)
{
    // 初始化内部 IKRig 节点的骨骼引用
    IKRigNode.InitializeBoneReferences(RequiredBones);
}

bool FAnimNode_MyCustomIK::IsValidToEvaluate(const USkeleton* Skeleton, const FBoneContainer& RequiredBones)
{
    // 检查 IKRig 资产是否有效
    return IKRigNode.IKRigAsset != nullptr;
}

void FAnimNode_MyCustomIK::EvaluateSkeletalControl_AnyThread(FComponentSpacePoseContext& Output, TArray<FBoneTransform>& OutBoneTransforms)
{
    // 1. 先让 IKRig 节点进行解算
    IKRigNode.Evaluate(Output);

    // 2. 从解算后的姿态中获取你需要的骨骼变换
    // 例如，获取左手骨骼的变换
    const FCompactPoseBoneIndex LeftHandBoneIndex = Output.Pose.GetPose().GetBoneContainer().GetCompactPoseIndexFromSkeletonIndex(/* 左手骨骼索引 */);
    if (LeftHandBoneIndex != INDEX_NONE)
    {
        FTransform LeftHandTransform = Output.Pose.GetComponentSpaceTransform(LeftHandBoneIndex);
        // 可以将此变换应用到 OutBoneTransforms 中，或进行其他处理
        OutBoneTransforms.Add(FBoneTransform(LeftHandBoneIndex, LeftHandTransform));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ControlRig` | IKRig 的底层 IK 解算和骨骼控制框架可能依赖于 ControlRig 的核心功能。 |
| `FullBodyIK` | 提供全身 IK 解算算法，是 `IKRig` 资产中可能使用的解算器类型之一。 |
| `AnimGraphRuntime` | 运行时动画图节点（如 `FAnimNode_IKRig`）的基础。 |
| `PropertyEditor` | `IKRigDeveloper` 模块用于在编辑器中自定义 `IKRig` 资产和节点的属性面板。 |

## 维护状态

### 近期更新

-   `c9ae4a3d51a5` 2025-10-03 将默认动画混合选项从线性更改为 Hermite Cubic（即平滑步进）。注意：旧数据将保留之前的线性默认值，因此现有数据应不受影响。
    *解读：这是一个动画混合行为的优化/改进，提升了默认效果的平滑度。*
-   `2057280165b3` 2025-09-15 使用 UnrealCodeFixup 更新了头文件，确保 dllstorage 位于方法/静态变量上而不是类型上。第 1/n 部分。
    *解读：代码维护和编译兼容性修复，不影响功能。*
-   `a989b108aaa4` 2025-08-20 [IKRig] 重大重构第 3 部分（共 3 部分）。
    *解读：表明插件在近期经历了重大的架构重构，是活跃开发和功能演进的标志。*

### 维护评价

**活跃维护**。IKRig 插件创建于 2020 年底，是一个相对年轻的插件。从近期的 git 历史看，它在 2025 年 8 月进行了重大重构，并在 10 月仍有功能优化提交。这表明该插件处于**积极开发和维护**状态，是 Epic 官方动画工具链的重要组成部分。它作为 `ControlRig` 生态的上层应用，解决了具体的 IK 和重定向工作流问题，推荐在需要此类功能的项目中使用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/IKRig/Tests) (如果存在)