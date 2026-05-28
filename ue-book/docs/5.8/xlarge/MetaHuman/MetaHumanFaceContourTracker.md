# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、模型数据、编辑器工具） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方的 MetaHuman 工具包，它为 UE5 提供了创建和驱动 MetaHuman 数字人角色的完整工作流。这个插件解决的核心问题是**如何将现实世界中的面部表演（来自视频、音频或专用设备）高效、逼真地转化为 MetaHuman 角色的动画数据**。它不是一个简单的模型导入插件，而是一个集成了神经网络推理（NNE）、几何求解、序列化和编辑器集成的复杂系统，旨在让开发者能够在引擎内完成从面部追踪到动画生成的全流程。

## 使用场景

- 你有一段演员的面部表演视频，想要为你的 MetaHuman 角色生成对应的动画 → 使用 `MetaHumanFaceContourTracker` 和 `MetaHumanFaceAnimationSolver` 模块
- 你有一个 MetaHuman 角色的静态模型，想要根据一段音频生成说话口型动画 → 使用 `MetaHumanSpeech2Face` 模块
- 你希望批量处理多个表演数据，以自动化方式生成多个动画序列 → 使用 `MetaHumanBatchProcessor` 模块
- 你正在从 iPhone 的 ARKit 面部追踪数据创建 MetaHuman 动画 → 使用 `MetaHumanCaptureSource` 和相关的数据处理模块
- 你需要创建、编辑和管理一个 MetaHuman “身份”资产，它定义了角色如何从图像或视频中重建 → 使用 `MetaHumanIdentity` 模块及其编辑器

## 蓝图用法

根据源码分析，此插件的主要交互界面集中在编辑器资产和特定的蓝图资产类上，公开的、可直接在游戏逻辑中使用的 `BlueprintCallable` 函数较少。其核心功能主要通过**资产编辑器（Asset Editors）** 和 **Editor Utility Widgets** 来暴露。

### 核心资产与节点

此插件的核心是一个资产体系，而不是通用的蓝图函数库。

| 资产类型 | 说明 | 所在模块 |
|---|---|---|
| `UMetaHumanIdentity` | 核心资产。用于定义一个 MetaHuman 角色，包含从图像/视频重建参数、用于追踪的模板和最终输出的动画资产。 | `MetaHumanIdentity` |
| `UMetaHumanPerformance` | 性能资产。包含从一段表演数据（视频/音频）生成的面部动画曲线数据。 | `MetaHumanPerformance` |
| `UMetaHumanFaceContourTrackerAsset` | 追踪器资产。包含用于在面部图像上检测和追踪特征点（如眼睛、嘴巴轮廓）的多个神经网络模型。 | `MetaHumanFaceContourTracker` |

### 使用示例（蓝图/编辑器描述）

1.  **创建 MetaHuman 身份**：在内容浏览器中右键 -> `Animation` -> `MetaHuman` -> `Identity`，创建一个 `MetaHumanIdentity` 资产。
2.  **配置追踪器**：打开该资产，进入“追踪”（Tracking）选项卡。你需要为其分配一个 `MetaHumanFaceContourTrackerAsset`。插件默认提供了一个，你也可以创建自定义的。
3.  **处理表演数据**：在“性能”（Performance）选项卡，导入你的表演视频或音频文件。插件会使用配置的追踪器和求解器（如 `MetaHumanFaceAnimationSolver`）自动处理数据，生成 `MetaHumanPerformance` 资产。
4.  **应用动画**：将生成的 `MetaHumanPerformance` 资产中的动画序列（通常是一个 `UAnimSequence`）拖拽到你的 MetaHuman 角色的 `AnimSequence` 播放器上，或者在 Sequencer 中使用。

## C++ 用法

插件的 C++ 用法主要面向引擎扩展和深度集成。开发者可能会直接与底层的追踪器、求解器或数据管理类交互。

### 头文件引入

```cpp
// 访问面部轮廓追踪器资产
#include "MetaHumanFaceContourTracker/Public/MetaHumanFaceContourTrackerAsset.h"

// 访问 MetaHuman 身份资产
#include "MetaHumanIdentity/Public/MetaHumanIdentity.h"

// 访问管道（Pipeline）系统
#include "MetaHumanPipeline/Public/Nodes/PipelineNode.h"
```

### 基本用法：加载并使用面部追踪器

以下代码展示了如何以编程方式加载默认的面部轮廓追踪器模型，并检查其状态。这是执行面部追踪前的关键步骤。

```cpp
// 来自：MetaHumanFaceContourTrackerAsset.h 和相关测试用例
void LoadAndQueryTracker()
{
    // 1. 获取或创建一个追踪器资产实例
    TObjectPtr<UMetaHumanFaceContourTrackerAsset> Tracker = UMetaHumanFaceContourTrackerAsset::LoadDefaultTracker();
    if (!Tracker)
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load default face contour tracker asset."));
        return;
    }

    // 2. 检查追踪器是否已准备好（模型数据是否已加载）
    if (Tracker->CanProcess())
    {
        UE_LOG(LogTemp, Log, TEXT("Face contour tracker is ready to process frames."));
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Tracker models are not loaded. Starting asynchronous load..."));
        // 3. 异步加载模型
        Tracker->LoadTrackers(true, [Tracker](bool bSuccess) {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Tracker models loaded successfully."));
                // 在这里可以开始使用 Tracker 处理视频帧
            }
        });
    }

    // 可选：查询或设置 NNE 后端
    FString CurrentBackend = Tracker->GetNNEBackend();
    UE_LOG(LogTemp, Log, TEXT("Current NNE Backend: %s"), *CurrentBackend);
    // Tracker->SetNNEBackend(TEXT("CUDA")); // 如果需要切换后端
}
```
*来源: 基于 `UMetaHumanFaceContourTrackerAsset` 公共接口分析*

### 进阶用法：理解 MetaHuman Pipeline

许多高级操作（如从图像创建身份、执行面部拟合）在内部通过一个“管道”（Pipeline）系统执行。开发者可以通过继承 `FPipelineNode` 来扩展或自定义处理流程。

```cpp
// 来自：MetaHumanPipeline 模块的核心概念
// 管道由多个节点（Nodes）组成，数据在节点之间流动。
// 例如，一个处理视频帧的简单管道可能包含：
// 1. 视频帧读取节点
// 2. 面部检测节点 (使用 FaceContourTracker)
// 3. 特征点优化节点
// 4. 动画求解节点
// 5. 动画输出节点

// 通常，开发者不会直接编写完整的管道，而是通过编辑器UI（如 MetaHumanIdentity 编辑器）来配置它。
// 但理解这个架构有助于调试和理解插件的工作流。
```
*来源: 基于模块架构和依赖关系分析*

## Demo 示例

由于这是一个主要面向编辑器和工作流的插件，一个“最小可编译示例”通常是一个使用其资产的编辑器工具或自定义处理步骤。下面的示例展示了如何创建一个简单的编辑器工具按钮，用于检查场景中一个 Actor 的 MetaHuman 动画资产。

```cpp
// MyMetaHumanAnimChecker.h
#pragma once
#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyMetaHumanAnimChecker.generated.h"

class UMetaHumanPerformance;
UCLASS()
class UMyMetaHumanAnimChecker : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "MetaHuman Utility")
    void CheckSelectedActorMetaHumanAnim();

private:
    // 从 MetaHumanPerformance 资产中提取关键动画曲线数据
    void AnalyzePerformanceAsset(UMetaHumanPerformance* InPerfAsset);
};

// MyMetaHumanAnimChecker.cpp
#include "MyMetaHumanAnimChecker.h"
#include "MetaHumanPerformance/Public/MetaHumanPerformance.h"
#include "Engine/Selection.h"

void UMyMetaHumanAnimChecker::CheckSelectedActorMetaHumanAnim()
{
    AActor* SelectedActor = nullptr;
    if (GEditor)
    {
        USelection* Selection = GEditor->GetSelectedActors();
        if (Selection && Selection->Num() > 0)
        {
            SelectedActor = Cast<AActor>(Selection->GetSelectedObject(0));
        }
    }

    if (!SelectedActor)
    {
        UE_LOG(LogTemp, Warning, TEXT("No actor selected."));
        return;
    }

    // 此处仅为演示目的。在实际项目中，你可能需要从 Actor 的动画蓝图或组件中查找关联的 MetaHumanPerformance 资产。
    UE_LOG(LogTemp, Log, TEXT("Selected Actor: %s"), *SelectedActor->GetName());
    UE_LOG(LogTemp, Log, TEXT("To fully integrate, you would need to locate the associated UMetaHumanPerformance asset from this actor's animation system."));
}

void UMyMetaHumanAnimChecker::AnalyzePerformanceAsset(UMetaHumanPerformance* InPerfAsset)
{
    if (!InPerfAsset) return;

    // UMetaHumanPerformance 内部包含面部动画曲线数据，但其公开接口可能不直接暴露这些数据。
    // 它的主要作用是作为数据的容器，并在编辑器中提供预览和操作UI。
    // 通常，它的最终输出是生成的 UAnimSequence 资产，可以直接应用于骨架网格体。
    UE_LOG(LogTemp, Log, TEXT("Analyzing MetaHuman Performance asset: %s"), *InPerfAsset->GetName());
    // ... 在这里可以添加你的分析逻辑，例如检查生成的 AnimSequence 的帧率、长度等。
}
```

## 模块依赖

要使用此插件的功能，你的项目模块通常需要依赖 `MetaHumanCore`，如果涉及特定功能则依赖对应模块。以下是关键的独特依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanFaceContourTracker` | 提供面部特征点追踪的核心神经网络资产和功能 |
| `MetaHumanFaceAnimationSolver` | 提供将追踪到的特征点转换为面部动画参数的求解器 |
| `MetaHumanIdentity` | 提供 MetaHuman 角色“身份”资产和相关的编辑器逻辑 |
| `MetaHumanPerformance` | 提供存储和管理表演动画数据的资产 |
| `MetaHumanPipeline` | 提供底层处理管道的节点化框架 |
| `MetaHumanCaptureSource` | 提供从各种设备（如iPhone）导入捕获数据的功能 |
| `MetaHumanCaptureProtocolStack` | 提供实时捕获协议的支持 |
| `ControlRigDeveloper` | 用于与 Control Rig 集成，可能用于自定义动画逻辑 |
| `SkeletalMeshUtilitiesCommon` | 提供通用的骨骼网格体操作工具函数 |
| `MetaHumanSDKEditor` | 提供 MetaHuman SDK 相关的编辑器集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象，优化性能和显示 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为现有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题 |

### 维护评价

- **活跃维护**：从最近的 Git 提交记录来看，该插件仍在被 Epic Games **非常活跃地维护和更新**。最近几次提交（2026年5月）集中在功能改进（如身体追踪集成）、渲染问题修复和稳定性提升上。
- **版本状态**：`.uplugin` 显示版本为 `5.0.0`，且 `IsBetaVersion` 和 `IsExperimentalVersion` 均为 `false`，表明这是一个正式发布的稳定版本。
- **创建时间未知**：由于用户提供的信息中创建时间未知，无法准确评估插件年龄。但从其在 UE5 生态中的核心地位和持续更新来看，它是一个长期存在且重要的官方插件。
- **推荐使用**：**强烈推荐**给所有希望使用 MetaHuman 技术的 UE5 项目。它是官方支持的核心工具链，文档和社区支持相对完善，且持续获得新功能和修复。
- **潜在复杂性**：插件由 28 个模块组成，规模庞大，内部交互复杂。对于初学者来说，通过编辑器 UI（如 MetaHumanIdentity 编辑器）进行操作是推荐的学习路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-unreal-engine-5-guide/) （注：.uplugin 中 DocsURL 为空，此链接为 Epic 官方 MetaHuman 文档首页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) （插件内包含 `MetaHumanControlsConversionTest` 模块，可作为部分功能测试参考）