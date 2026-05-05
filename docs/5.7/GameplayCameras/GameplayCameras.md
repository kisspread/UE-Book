# Gameplay Cameras

> A modular and data-driven camera system for Unreal（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Cameras |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、摄像机节点、曲线等） |
| 模块 | `GameplayCameras` (Runtime), `GameplayCamerasEditor` (Editor), `GameplayCamerasUncookedOnly` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras) | |

## 用途

GameplayCameras 是一个模块化、数据驱动的摄像机系统，旨在替代或增强 Unreal Engine 传统的 `UCameraComponent` 和 `APlayerCameraManager` 工作流。它通过引入“摄像机资产”（`UCameraAsset`）、“摄像机装备”（`UCameraRigAsset`）和“摄像机节点”（`UCameraNode`）的概念，允许开发者以可视化、可组合的方式构建复杂的摄像机行为。

**核心解决的问题**：
1.  **复杂性管理**：传统摄像机逻辑通常通过蓝图或 C++ 代码堆叠在 `APlayerCameraManager` 中，难以维护和复用。GameplayCameras 将摄像机行为分解为独立的、可配置的节点（如跟随、混合、抖动、取景），并通过资产进行管理。
2.  **数据驱动**：摄像机行为（如混合时间、插值曲线、目标偏移）可以存储在资产中，便于策划调整，无需修改代码。
3.  **模块化与复用**：摄像机装备可以被多个摄像机资产引用，摄像机节点可以在不同装备间共享，提高了资产的复用率。
4.  **高级功能支持**：内置了对摄像机抖动（Shakes）、取景（Framing）、后处理（Post Process）等高级功能的节点支持，并与 Sequencer（通过 `MovieSceneCameraFramingZoneTrack`）和 StateTree 集成。

## 使用场景

-   你在开发一款第三人称动作游戏，需要实现一个平滑跟随角色、在攻击时自动拉近特写、并能在过场动画中精确控制的摄像机系统。
-   你需要为游戏中的不同状态（探索、战斗、对话）快速切换不同的摄像机行为预设。
-   你希望摄像机行为（如跟随的延迟、混合的曲线）能够由策划在编辑器中直接调整，而不是硬编码在程序里。
-   你需要创建复杂的电影化镜头，例如在多个目标之间平滑切换、实现环绕拍摄（Orbit）或基于取景区域（Framing Zone）的自动构图。

## 蓝图用法

GameplayCameras 的核心是资产和节点，其蓝图 API 主要围绕资产的创建、配置和激活。许多节点（如 `UFieldOfViewCameraNode`）的属性是 `UPROPERTY(EditAnywhere)`，这意味着它们主要在资产编辑器中配置，而非通过蓝图节点动态调用。

### 核心资产与组件

| 资产/组件 | 说明 | 所在类 |
|---|---|---|
| `Camera Asset` | 顶层摄像机资产，定义了一个完整的摄像机行为，可包含多个摄像机装备。 | `UCameraAsset` |
| `Camera Rig Asset` | 摄像机装备，定义了一组具体的摄像机节点树，是实际执行摄像机逻辑的单元。 | `UCameraRigAsset` |
| `Camera Rig Proxy` | 摄像机装备代理，用于在摄像机导演中引用装备而不硬编码具体资产，提高复用性。 | `UCameraRigProxyAsset` |
| `Camera Variable Collection` | 摄像机变量集合，用于存储可在节点间共享的变量（如目标位置、旋转）。 | `UCameraVariableCollection` |
| `Gameplay Camera Component` | 挂载在 Actor 上的组件，用于驱动和评估摄像机资产。 | `UGameplayCameraComponent` (推断) |

### 使用示例（蓝图描述）

1.  **创建摄像机资产**：在内容浏览器中右键 -> `Cameras` -> `Camera Asset`。打开资产编辑器，你可以添加一个 `Single Camera Director`，并为其指定一个 `Camera Rig Asset`。
2.  **配置摄像机装备**：创建一个 `Camera Rig Asset`。在节点图中，你可以拖入各种摄像机节点（如 `Set Location Camera Node`、`Field Of View Camera Node`、`Linear Blend Camera Node`）并连接它们，构建摄像机行为逻辑。
3.  **激活摄像机**：在你的角色蓝图中，添加一个 `Gameplay Camera Component`。在 BeginPlay 事件中，调用该组件的函数（如 `SetCameraAsset`）来指定要使用的 `Camera Asset`。组件会自动处理评估和激活。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayCameras.h"
#include "Core/CameraAsset.h"
#include "Core/CameraRigAsset.h"
#include "Nodes/Common/FieldOfViewCameraNode.h"
#include "Nodes/Blends/LinearBlendCameraNode.h"
```

### 基本用法

以下示例展示了如何在 C++ 中程序化地创建一个简单的摄像机装备，该装备设置一个固定的视野（FOV）。

```cpp
// 来源：基于 Nodes/Common/FieldOfViewCameraNode.h 和 Core/CameraRigAsset.h 的推断用法
#include "Core/CameraRigAsset.h"
#include "Nodes/Common/FieldOfViewCameraNode.h"

void CreateSimpleCameraRig()
{
    // 1. 创建摄像机装备资产
    UCameraRigAsset* CameraRig = NewObject<UCameraRigAsset>(GetTransientPackage(), TEXT("MySimpleRig"));

    // 2. 创建并配置一个设置FOV的节点
    UFieldOfViewCameraNode* FOVNode = NewObject<UFieldOfViewCameraNode>(CameraRig);
    FOVNode->FieldOfView.Value = 90.0f; // 设置FOV为90度

    // 3. 将节点设置为装备的根节点（或添加到节点树中）
    // 注意：实际API可能需要通过编辑器工具或特定构建流程，此处为概念演示。
    // CameraRig->SetRootNode(FOVNode);

    // 4. 构建装备以使其可用于运行时
    UE::Cameras::FCameraBuildLog BuildLog;
    UE::Cameras::FCameraAssetBuilder Builder(BuildLog);
    // Builder.BuildCameraRig(CameraRig); // 假设存在类似方法
}
```

### 进阶用法

结合多个节点和混合器创建更复杂的行为。

```cpp
// 来源：基于 Nodes/Blends/LinearBlendCameraNode.h 和 Nodes/Common/SetLocationCameraNode.h 的推断用法
#include "Nodes/Blends/LinearBlendCameraNode.h"
#include "Nodes/Common/SetLocationCameraNode.h"

void CreateBlendedCameraRig()
{
    UCameraRigAsset* Rig = NewObject<UCameraRigAsset>();

    // 创建两个设置不同位置的节点
    USetLocationCameraNode* LocationA = NewObject<USetLocationCameraNode>(Rig);
    LocationA->Location.Value = FVector(0, 0, 100);

    USetLocationCameraNode* LocationB = NewObject<USetLocationCameraNode>(Rig);
    LocationB->Location.Value = FVector(0, 0, 200);

    // 创建一个线性混合节点
    ULinearBlendCameraNode* BlendNode = NewObject<ULinearBlendCameraNode>(Rig);
    BlendNode->SetBlendTime(1.0f); // 假设有设置混合时间的方法

    // 将两个位置节点连接到混合节点的输入
    // BlendNode->SetInputA(LocationA);
    // BlendNode->SetInputB(LocationB);

    // 将混合节点作为装备的根
    // Rig->SetRootNode(BlendNode);
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何定义一个自定义的摄像机节点，该节点简单地将摄像机位置设置为原点上方固定高度。

**MyFixedHeightCameraNode.h**
```cpp
#pragma once

#include "Core/CameraNode.h"
#include "Core/CameraParameters.h"
#include "MyFixedHeightCameraNode.generated.h"

UCLASS(meta=(CameraNodeCategories="Custom,Transform"))
class UMyFixedHeightCameraNode : public UCameraNode
{
    GENERATED_BODY()

public:
    /** 相机距离地面的固定高度 */
    UPROPERTY(EditAnywhere, Category="Custom")
    FFloatCameraParameter Height = 300.0f;

protected:
    virtual FCameraNodeEvaluatorPtr OnBuildEvaluator(FCameraNodeEvaluatorBuilder& Builder) const override;
};
```

**MyFixedHeightCameraNode.cpp**
```cpp
#include "MyFixedHeightCameraNode.h"
#include "Core/CameraNodeEvaluator.h"

// 评估器类，实际执行每帧的摄像机逻辑
class FMyFixedHeightCameraNodeEvaluator : public FCameraNodeEvaluator
{
public:
    FMyFixedHeightCameraNodeEvaluator() {}

    virtual void OnRun(const FCameraNodeEvaluationParams& Params, FCameraNodeEvaluationResult& OutResult) override
    {
        // 获取配置的高度值
        const float CurrentHeight = Height.GetValue(Params.EvaluationTime);

        // 设置摄像机位置：X, Y 保持当前值（或来自上下文），Z 设置为固定高度
        FVector NewLocation = OutResult.CameraPose.GetLocation();
        NewLocation.Z = CurrentHeight;
        OutResult.CameraPose.SetLocation(NewLocation);
    }

    void SetHeightParameter(const FFloatCameraParameter& InHeight) { Height = InHeight; }

private:
    FFloatCameraParameter Height;
};

FCameraNodeEvaluatorPtr UMyFixedHeightCameraNode::OnBuildEvaluator(FCameraNodeEvaluatorBuilder& Builder) const
{
    FMyFixedHeightCameraNodeEvaluator* Evaluator = Builder.BuildEvaluator<FMyFixedHeightCameraNodeEvaluator>();
    Evaluator->SetHeightParameter(Height);
    return Evaluator;
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和模块推断，使用此插件需要以下依赖：

| 模块 | 用途 |
|---|---|
| `EnhancedInput` | 用于处理玩家输入，摄像机节点（如 `UDrivenControlRotationCameraNode`）可能依赖它来获取输入数据。 |
| `StateTree` | 用于实现基于状态树的摄像机导演逻辑，允许摄像机行为与游戏状态机深度集成。 |
| `TemplateSequence` | 用于支持基于模板序列（Template Sequence）的摄像机动画，可能用于过场动画或预设镜头。 |

## 维护状态

### 近期更新

```
- 2025-10-03 e679e914e50f Cameras: fixup default parameters on load as a workaround for a bug in FInstancedPropertyBags #jira UE-353209 #rb bryan.robertson
- 2025-09-15 2a14c8f0afa8 Cameras: fix missing sub-object destruction in gameplay camera component #jira UE-353204 #rb bryan.robertson
- 2025-08-20 7e41262c01bf Cameras: change how auto-build for PIE works to prevent packages from being modified at the wrong time
```

### 维护评价

**综合评价：活跃维护的实验性核心系统。**

-   **创建时间**：约 4 年前（2020年），对于引擎核心系统而言属于较新的模块。
-   **更新频率**：最近 3 次提交均在 2025 年 8 月至 10 月间，且都是针对运行时组件和构建流程的实质性修复与改进，表明该插件仍在被 Epic 积极开发和维护。
-   **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，这意味着其 API 和功能在未来版本中可能发生不兼容的更改。目前不建议在需要长期稳定性的生产项目中作为核心依赖，但非常适合用于原型开发和新项目探索。
-   **推荐使用**：如果你正在启动一个新项目，并且需要强大的、数据驱动的摄像机系统，GameplayCameras 是一个非常有前景的选择。它代表了 UE 摄像机系统的未来方向。对于现有项目，可以谨慎评估并尝试集成，但需做好应对 API 变更的准备。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Cameras/GameplayCameras)
-   [官方文档]() (暂无)
-   [测试用例]() (路径待确认，可能位于 `Engine/Tests/GameplayCameras` 或插件内部的 `Tests` 目录)