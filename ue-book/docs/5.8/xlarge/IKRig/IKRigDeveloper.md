# IK Rig

> （Description为空，无描述可照抄）

| 属性 | 值 |
|---|---|
| 中文名 | IK 索具 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（动画资产、蓝图资产） |
| 模块 | `IKRig` (Runtime), `IKRigDeveloper` (Runtime), `IKRigEditor` (Runtime), `IKRigUAF` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-11-25 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig) | |

## 用途

IKRig 是一个用于在运行时和编辑器中创建和执行反向动力学 (IK) 的插件。它的核心是定义一个 **IKRig 资产**（`UIKRigDefinition`），该资产描述了骨骼网格体的 IK 链、目标点（Goals）和解算器（Solvers）。此资产可用于驱动角色的骨骼，使其末端（如手、脚）精确地到达目标位置。

该插件解决的主要问题是 **动画重定向**。通过为不同体型的角色创建各自的 IKRig 资产，并配对一个 **IK 重定向器**（`UIKRigRetargeter`），可以在运行时将一个角色的动画无缝地应用到另一个完全不同比例的角色上，而不会出现骨骼扭曲或滑动。这是 UE5 中实现高质量、可定制动画重定向的核心工具。

## 使用场景

-   **跨体型动画重定向**：你正在制作一个支持多角色（如巨人、人类、矮人）的游戏，需要共享同一套动画。使用 IKRig 和 IK 重定向器可以精确地将动画从一个骨架重定向到另一个。
-   **精确的肢体放置**：在攀爬、格斗或与环境交互的游戏中，需要角色的手或脚精确地抓在特定的抓点或踩在地面上。IKRig 的 IK 解算器可以运行时调整骨骼链以满足这些目标。
-   **程序化动画**：通过蓝图或代码动态修改 IK 目标（Goal）的位置和旋转，可以实现程序化的角色姿态调整，例如自动调整角色视线方向或武器持握位置。
-   **动画蓝图中的复杂 IK 解决方案**：使用 `AnimNode_IKRig` 节点，将整个 IKRig 解决方案作为一个黑盒节点插入到动画蓝图中，简化复杂的 IK 逻辑。

## 蓝图用法

IKRig 主要通过其 **动画图节点** 在动画蓝图中使用。开发者通常不直接调用函数，而是配置节点和资产。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IK Rig` | 核心动画节点。使用一个 `UIKRigDefinition` 资产来驱动骨骼。其输入引脚（Goals）根据资产定义动态生成。 | `UAnimGraphNode_IKRig` |
| `Retarget Pose From Mesh` | 重定向动画节点。使用一个 `UIKRigRetargeter` 资产，将源骨骼网格体的动画重定向到当前角色上。 | `UAnimGraphNode_RetargetPoseFromMesh` |

### 使用示例（蓝图描述）

1.  **为角色创建 IKRig 资产**：
    *   在内容浏览器中右键 -> Animation -> IK Rig。
    *   打开资产编辑器，为角色的骨架设置根骨骼、IK 链（如 LeftArm -> LeftHand）和目标点。
    *   保存资产。

2.  **在动画蓝图中使用 IK Rig 节点**：
    *   在动画图中，添加一个 `IK Rig` 节点。
    *   在节点的细节面板中，选择上一步创建的 `UIKRigDefinition` 资产。
    *   节点会自动生成多个输入引脚（对应资产中定义的每个 Goal）。你需要通过其他节点（如骨骼查找节点、世界空间位置计算等）为这些引脚提供值（Transform）。
    *   将节点的输出连接到最终的 `Output Pose`。

3.  **设置动画重定向**：
    *   创建两个 `UIKRigDefinition` 资产，分别用于源角色和目标角色。
    *   创建一个 `UIKRigRetargeter` 资产，将两个 IKRig 资产关联起来，并映射对应的骨骼链。
    *   在目标角色的动画蓝图中，添加 `Retarget Pose From Mesh` 节点。
    *   在节点细节面板中，选择重定向器资产，并指定一个 **源骨骼网格体组件**（通常是场景中另一个角色的组件，或通过引用获取）。
    *   该节点将输出经过重定向的动画姿势。

## C++ 用法

主要使用场景是在编辑器扩展或自定义工具中创建和处理 IKRig 相关资产。

### 头文件引入

```cpp
// 核心数据类型和节点
#include "IKRigDefinition.h"
#include "AnimNode_IKRig.h"
#include "AnimNode_RetargetPoseFromMesh.h"

// 开发者工具（如果需要在编辑器中程序化修改资产）
#include "IKRigDeveloper.h"
```

### 基本用法

以下代码展示了如何在代码中引用和检查一个 IKRig 资产。 (来源：基于 `UIKRigDefinition` 的典型使用模式推断)

```cpp
// 假设 AssetPath 是 UIKRigDefinition 资产的路径，如 "/Game/Characters/HumanoidRig"
FString AssetPath = TEXT("/Game/Characters/HumanoidRig");
UIKRigDefinition* RigDef = Cast<UIKRigDefinition>(StaticLoadObject(UIKRigDefinition::StaticClass(), nullptr, *AssetPath));

if (RigDef)
{
    // 成功加载，可以访问其数据
    UE_LOG(LogTemp, Log, TEXT("Loaded IKRig Definition: %s"), *RigDef->GetName());
    
    // 例如，检查它有哪些效应器目标
    for (const UIKRigEffectorGoal* Goal : RigDef->GetEffectors())
    {
        UE_LOG(LogTemp, Log, TEXT("Goal: %s, Bone: %s"), *Goal->GoalName.ToString(), *Goal->BoneName.ToString());
    }
}
```

### 进阶用法

进阶用法通常涉及在编辑器工具中程序化地构建或修改 IKRig 资产。`IKRigDeveloper` 模块提供了此类功能的入口。虽然提供的源文件较少，但基于其命名和模块类型，可以推断其用途。

```cpp
// 该代码片段展示概念，具体函数需查阅 IKRigDeveloper 模块的头文件
#include "IKRigDeveloper.h"

// 假设要在编辑器工具中创建一个新的简单IKRig
void CreateSimpleIKRigProgrammatically(USkeleton* TargetSkeleton)
{
    if (!TargetSkeleton) return;

    // 创建一个新的IKRig资产
    UIKRigDefinition* NewRig = NewObject<UIKRigDefinition>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
    
    // 使用 IKRigDeveloper 模块提供的工具函数来设置骨骼、链等
    // FIKRigDeveloper::SetSkeletonForRig(NewRig, TargetSkeleton);
    // FIKRigDeveloper::AddNewChain(NewRig, "LeftArm", "upperarm_l", "hand_l");
    // FIKRigDeveloper::AddEffectorGoal(NewRig, "LeftHandGoal", "hand_l");

    // 保存资产到磁盘
    // FAssetRegistryModule::AssetCreated(NewRig);
    // UPackage::SavePackage(NewRig->GetOutermost(), NewRig, EObjectFlags::RF_Public, *FPaths::ProjectContentDir());
}
```

## Demo 示例

一个最小的示例，演示如何在 C++ 动画实例中获取和使用一个 IKRig 解算器的状态（假设你已经有一个 `UIKRigDefinition` 资产和对应的 `FAnimNode_IKRig` 节点在动画蓝图中运行）。

**MyCharacterAnimInstance.h**
```cpp
#pragma once
#include "Animation/AnimInstance.h"
#include "MyCharacterAnimInstance.generated.h"

class UIKRigDefinition;

UCLASS()
class UMyCharacterAnimInstance : public UAnimInstance
{
    GENERATED_BODY()

public:
    // 在蓝图中设置或通过代码加载的 IKRig 资产引用
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IK")
    UIKRigDefinition* CharacterRig;

    // 示例：一个蓝图可调用的函数，用于查询某个IK目标（Goal）的状态
    UFUNCTION(BlueprintCallable, Category = "IK")
    FTransform GetHandGoalTransform(const FName& GoalName) const;

protected:
    // 通常动画节点的数据是在动画线程上处理的，直接访问可能不安全。
    // 更好的做法是通过蓝图或动画图传递数据。
    // 此处仅为演示获取资产数据。
};
```

**MyCharacterAnimInstance.cpp**
```cpp
#include "MyCharacterAnimInstance.h"
#include "IKRigDefinition.h"
#include "IKRigEffectorGoal.h"

FTransform UMyCharacterAnimInstance::GetHandGoalTransform(const FName& GoalName) const
{
    if (!CharacterRig)
    {
        return FTransform::Identity;
    }

    // 从IKRig资产中查找目标
    const UIKRigEffectorGoal* Goal = CharacterRig->FindGoal(GoalName);
    if (Goal)
    {
        // 注意：这里返回的是资产中定义的初始变换。
        // 运行时实际的IK解算器计算的位置会由AnimNode_IKRig处理。
        return Goal->CurrentTransform;
    }

    return FTransform::Identity;
}
```

## 模块依赖

该插件的模块依赖其他特定的动画模块。

| 模块 | 用途 |
|---|---|
| `ControlRig` | IKRig 依赖于 ControlRig 基础设施，可能用于底层节点或未来扩展。 |
| `FullBodyIK` | 提供全身体IK解算器，是IKRig中可选的、更高级的解算器之一。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `d96c8edf` | Fix root motion trajectory visualization in IK Retarget editor | 修复了 IK 重定向编辑器中根运动轨迹的可视化问题。 |
| 2026-05-12 | `b9da6b61` | [IK Retargeter] Fix curve-bound override values having no effect on exported batch retarget animation | 修复了曲线绑定的覆盖值在批量导出重定向动画时无效的问题。 |
| 2026-05-12 | `553f4a7e` | [IK Retargeter] Fix pre-5.6 RTG assets having all ops enabled in 5.8: narrow PostLoad version guard | 修复了 5.6 之前的重定向资产在 5.8 中所有操作被错误启用的问题，收紧了 PostLoad 版本检查。 |
| 2026-05-12 | `0171c6fd` | [IK Retargeter] Fix null deref crashes in GenerateAssetLists: guard GC'd weak ptrs, uncompiled blueprint | 修复了在生成资产列表时空指针崩溃的问题，加强了对被垃圾回收弱指针和未编译蓝图的防护。 |
| 2026-05-12 | `f8c7fc88` | [IK Retargeter] Fix active-by-default Override Sets not applied when exporting animations through the batch exporter | 修复了通过批量导出器导出动画时，默认激活的覆盖集未被应用的问题。 |

### 维护评价

**活跃维护**。IKRig 插件自 2020 年创建以来，一直是 UE5 动画系统的核心组件。近期的提交记录（2026年5月）显示其仍在被积极开发和维护，特别是围绕 **IK Retargeter（重定向器）** 功能进行了大量 Bug 修复和优化。这表明 Epic Games 将其视为生产就绪的关键功能。插件稳定，文档和测试相对完善，是实现高质量动画重定向的**推荐使用**的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ik-rig-in-unreal-engine/)（UE官方文档有相关章节，但可能没有专门的插件文档页面）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/IKRig/Source/IKRig/Tests)（示例路径，具体位置需在仓库内搜索）