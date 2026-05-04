# AnimGen

> （无描述）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、数据资产） |
| 模块 | `AnimGen` (Runtime), `AnimGenEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimGen) | |

## 用途

AnimGen 是一个实验性的、基于机器学习（特别是神经网络）的动画生成与控制系统。它并非用于播放预制动画，而是通过训练一个自编码器（Auto-Encoder）来学习动画数据库中的运动模式，并在运行时根据给定的“控制信号”（如目标轨迹、速度）实时生成新的、连贯的动画姿态。

该插件的核心价值在于：
1.  **动画压缩与重建**：使用自编码器将高维的骨骼动画数据压缩到低维的潜在空间，并能从潜在空间重建出动画。
2.  **可控动画生成**：在潜在空间中，通过定义“行为”（Behavior）和“控制对象”（Control Object），可以引导生成过程，使角色执行特定动作（如跟随轨迹、闲置、转向）。
3.  **与动画蓝图集成**：通过 `AnimNode_AnimGenController` 动画节点和 RigVM 函数，将生成的动画无缝集成到 UE 的动画蓝图系统中。

## 使用场景

-   你需要一个角色能够根据动态生成的路径或玩家输入，实时产生自然的行走、奔跑、转向动画，而不是依赖有限的动画剪辑混合。
-   你希望从一个庞大的动画数据库中学习运动风格，并用它来生成新的、风格一致的动画变体。
-   你在研究或开发基于机器学习的动画系统，需要一个集成在 UE 内的、可训练和调试的框架。

## 蓝图用法

该插件的蓝图接口主要集中在定义行为和调试上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpecifyControl` | （蓝图可实现事件）定义此行为所使用的控制结构（Control Schema）。 | `UAnimGenBehavior` |
| `MakeControlSets` | （蓝图可实现事件）根据动画数据库和帧范围，生成用于训练的控制数据集。 | `UAnimGenBehavior` |
| `DrawDebugControl` | （蓝图可实现事件）在训练视窗中绘制当前帧的控制信息调试视图。 | `UAnimGenBehavior` |
| `InitializeDrawDebug` | （蓝图可实现事件）初始化自编码器的调试绘制所需数据。 | `UAnimGenAutoEncoderDebugDraw` |
| `DrawDebug` | （蓝图可实现事件）每帧绘制自编码器的原始与重建姿态对比调试视图。 | `UAnimGenAutoEncoderDebugDraw` |

### 使用示例（蓝图描述）

1.  **创建自定义行为**：创建一个新的蓝图类，继承自 `UAnimGenBehavior`（例如 `UAnimGenBehavior_TrajectoryFollow`）。在蓝图中重写 `SpecifyControl` 事件，使用 `FAnimGenControlSchema` 相关的函数来定义控制输入（如未来轨迹点）。重写 `MakeControlSets` 事件，从动画数据库中提取与控制信号匹配的动画片段作为训练数据。
2.  **配置控制器**：创建一个 `UAnimGenController` 数据资产。在其属性中，指定一个已训练好的 `UAnimGenAutoEncoder` 资产，并选择一个或多个你定义的 `UAnimGenBehavior`。
3.  **在动画蓝图中使用**：在角色的动画蓝图中，添加 `AnimNode_AnimGenController` 节点。将该节点的 `Controller` 属性设置为上一步创建的控制器资产。将角色的运动轨迹（例如来自 `CharacterMovementComponent`）连接到节点的 `ControlObject` 输入引脚。节点的输出即为生成的动画姿态。

## C++ 用法

### 头文件引入

```cpp
#include "AnimGenController.h"
#include "AnimGenControl.h"
#include "AnimGenBehavior.h"
#include "AnimNode_AnimGenController.h"
```

### 基本用法

定义一个自定义行为类，需要继承 `UAnimGenBehavior` 并实现其核心虚函数。

```cpp
// MyCustomBehavior.h
#pragma once
#include "AnimGenBehavior.h"
#include "MyCustomBehavior.generated.h"

UCLASS(BlueprintType, Blueprintable, meta = (DisplayName = "My Custom Behavior"))
class UMyCustomBehavior : public UAnimGenBehavior
{
    GENERATED_BODY()

#if WITH_EDITOR
public:
    // 定义控制结构
    virtual FAnimGenControlSchemaElement SpecifyControl_Implementation(FAnimGenControlSchema& InControlSchema) const override;
    
    // 生成控制数据集
    virtual void MakeControlSets_Implementation(TArray<FAnimGenControlSet>& OutControlSets, FAnimGenControlObject& InControlObject, const UAnimDatabase* InDatabase, const FAnimDatabaseFrameRanges& InFrameRanges) const override;
#endif
};
```

```cpp
// MyCustomBehavior.cpp
#include "MyCustomBehavior.h"

#if WITH_EDITOR
FAnimGenControlSchemaElement UMyCustomBehavior::SpecifyControl_Implementation(FAnimGenControlSchema& InControlSchema) const
{
    // 使用 InControlSchema 的方法添加一个名为 “TargetPoint” 的向量控制输入
    return InControlSchema.AddVector(TEXT("TargetPoint"));
}

void UMyCustomBehavior::MakeControlSets_Implementation(TArray<FAnimGenControlSet>& OutControlSets, FAnimGenControlObject& InControlObject, const UAnimDatabase* InDatabase, const FAnimDatabaseFrameRanges& InFrameRanges) const
{
    // 遍历动画数据库帧范围，为每一帧创建一个控制集
    // 在控制集中设置 “TargetPoint” 的值（例如，从动画数据中提取角色未来的目标位置）
    // 将创建好的控制集添加到 OutControlSets
}
#endif
```

### 进阶用法

在动画蓝图节点 `FAnimNode_AnimGenController` 中配置输出映射，将自编码器生成的属性映射到动画曲线或通知。

```cpp
// 在某个初始化函数中配置 AnimNode
FAnimNode_AnimGenController* AnimGenNode = ...; // 获取动画节点指针

// 配置曲线输出：将自编码器属性 “Speed” 映射到动画曲线 “MovementSpeed”
FAnimGenControllerCurveOutput CurveOutput;
CurveOutput.AutoEncoderAttributeName = FName(TEXT("Speed"));
CurveOutput.OutputCurveName = FName(TEXT("MovementSpeed"));
AnimGenNode->CurveOutputs.Add(CurveOutput);

// 配置动画通知输出：将自编码器属性 “FootStep” 映射到一个自定义的 AnimNotify
FAnimGenControllerAnimNotifyOutput NotifyOutput;
NotifyOutput.AutoEncoderAttributeName = FName(TEXT("FootStep"));
NotifyOutput.AnimNotify = NewObject<UMyAnimNotify>(AnimGenNode);
AnimGenNode->AnimNotifyOutputs.Add(NotifyOutput);
```

## Demo 示例

一个最小化的自定义行为实现，用于控制角色面向某个点。

```cpp
// LookAtBehavior.h
#pragma once
#include "AnimGenBehavior.h"
#include "LookAtBehavior.generated.h"

UCLASS(BlueprintType, Blueprintable, meta = (DisplayName = "Look At Behavior"))
class ULookAtBehavior : public UAnimGenBehavior
{
    GENERATED_BODY()

#if WITH_EDITOR
public:
    virtual FAnimGenControlSchemaElement SpecifyControl_Implementation(FAnimGenControlSchema& InControlSchema) const override;
    virtual void MakeControlSets_Implementation(TArray<FAnimGenControlSet>& OutControlSets, FAnimGenControlObject& InControlObject, const UAnimDatabase* InDatabase, const FAnimDatabaseFrameRanges& InFrameRanges) const override;
#endif
};
```

```cpp
// LookAtBehavior.cpp
#include "LookAtBehavior.h"
#include "AnimDatabase.h"

#if WITH_EDITOR
FAnimGenControlSchemaElement ULookAtBehavior::SpecifyControl_Implementation(FAnimGenControlSchema& InControlSchema) const
{
    // 定义一个名为 “LookAtTarget” 的向量输入
    return InControlSchema.AddVector(TEXT("LookAtTarget"));
}

void ULookAtBehavior::MakeControlSets_Implementation(TArray<FAnimGenControlSet>& OutControlSets, FAnimGenControlObject& InControlObject, const UAnimDatabase* InDatabase, const FAnimDatabaseFrameRanges& InFrameRanges) const
{
    if (!InDatabase) return;

    // 简化示例：为每一帧创建一个控制集，并将 “LookAtTarget” 设置为角色前方的一个点
    for (int32 FrameIndex = InFrameRanges.GetStart(); FrameIndex < InFrameRanges.GetEnd(); ++FrameIndex)
    {
        FAnimGenControlSet ControlSet;
        // 假设有一个函数可以从数据库获取角色在 FrameIndex 的位置和朝向
        FTransform CharacterTransform = InDatabase->GetCharacterTransform(0, FrameIndex);
        FVector LookAtPoint = CharacterTransform.GetLocation() + CharacterTransform.GetRotation().GetForwardVector() * 100.0f;
        
        // 将 LookAtPoint 设置到控制对象中
        InControlObject.SetVector(TEXT("LookAtTarget"), LookAtPoint);
        ControlSet.ControlObject = InControlObject; // 复制当前状态
        OutControlSets.Add(ControlSet);
    }
}
#endif
```

## 模块依赖

从 `AnimGen.Build.cs` 分析，该插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `AnimDatabase` | 提供动画数据库、帧范围、姿态状态等核心数据结构。 |
| `Learning` | Epic 的机器学习框架，提供神经网络、自编码器、训练和推理功能。 |
| `AnimNext` | 提供动画图（AnimGraph）评估框架，包括 Trait、评估任务（EvaluationTask）等。 |
| `RigVM` | 提供 RigVM 虚拟机，用于创建动画蓝图节点和函数。 |

## 维护状态

### 近期更新

（无法从提供的信息中获取 git log）

### 维护评价

-   **创建时间**：2026年4月，非常新。
-   **状态**：插件标记为 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，表明它处于早期实验阶段，API 和功能可能不稳定。
-   **代码结构**：从头文件看，架构清晰，与 UE 的动画、机器学习系统深度集成，但许多实现细节（.cpp）未提供，难以评估完成度。
-   **推荐使用**：**不推荐用于生产环境**。适合对机器学习动画前沿技术感兴趣的研究者和开发者进行学习和实验。使用前需做好应对 API 变更和潜在问题的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimGen)
-   官方文档：无
-   测试用例：未在提供信息中发现。