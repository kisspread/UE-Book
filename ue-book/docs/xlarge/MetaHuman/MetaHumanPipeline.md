# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置数据、NNE模型） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它解决的核心问题是**将真实世界的面部表演（来自 iPhone、立体相机或音频）高效、高质量地转换为 MetaHuman 角色的动画数据**。

该插件并非一个简单的单一功能，而是一个庞大的、模块化的**动画处理流水线系统**。它集成了从数据采集（`MetaHumanCaptureSource`）、面部追踪（`MetaHumanFaceContourTracker`）、深度生成（`MetaHumanDepthGenerator`）、动画求解（`MetaHumanFaceAnimationSolver`、`MetaHumanSpeech2Face`）到最终在引擎中驱动角色（`MetaHumanPerformance`、`MetaHumanSequencer`）的完整工作流。其存在是为了让开发者能够以专业级的精度和效率，为 MetaHuman 角色创建逼真的面部动画，而无需依赖外部昂贵的动捕设备或复杂的第三方软件。

## 使用场景

- **你正在使用 iPhone 的 TrueDepth 相机或立体相机录制演员的面部表演** → 使用 `MetaHumanCaptureSource` 和 `MetaHumanFaceTrackerNode` 进行面部追踪和动画求解。
- **你希望用一段音频文件（如配音）来驱动 MetaHuman 角色的口型和面部表情** → 使用 `MetaHumanSpeech2Face` 模块和 `FSpeechToAnimNode` 节点。
- **你需要批量处理大量的面部表演素材，将其转换为动画序列** → 使用 `MetaHumanBatchProcessor` 模块。
- **你希望将捕捉到的动画数据应用到特定的 MetaHuman 角色上，并进行精细调整** → 使用 `MetaHumanIdentity` 和 `MetaHumanPerformance` 模块。
- **你正在开发一个需要实时面部动画驱动的应用（如虚拟主播）** → 可以利用流水线中的 `FHyprsenseNode` 等节点进行实时推理。

## 蓝图用法

**重要说明**：`MetaHumanPipeline` 模块的核心功能是通过一个**节点化、数据驱动的 C++ 流水线系统**实现的，其设计更偏向于底层数据处理和自动化流程，而非直接暴露给蓝图设计师使用的高层级节点。因此，该模块中**没有发现直接标记为 `BlueprintCallable` 的函数**。

其使用模式通常是：
1.  在 C++ 中构建一个由各种 `FNode`（如 `FFaceTrackerStereoNode`, `FSpeechToAnimNode`）组成的流水线。
2.  配置每个节点的参数（如相机标定数据、DNA 资产、音频文件等）。
3.  将流水线提交给 `MetaHumanBatchProcessor` 或 `MetaHumanToolkit` 等更高层的系统执行。

对于蓝图用户，更常见的交互是通过 `MetaHumanToolkit` 或 `MetaHumanPerformance` 等编辑器工具提供的 UI 面板来操作，这些面板内部封装了流水线的调用。

## C++ 用法

### 头文件引入

```cpp
#include "Nodes/FaceTrackerNode.h"
#include "Nodes/SpeechToAnimNode.h"
#include "Pipeline/Pipeline.h"
```

### 基本用法

以下示例展示了如何创建一个简单的面部追踪流水线节点并配置其基本参数。此模式是使用 `MetaHumanPipeline` 的基础。

```cpp
// 来源：基于 Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanPipeline/Public/Nodes/FaceTrackerNode.h 推断

// 1. 创建一个用于处理 iPhone 捕捉数据的面部追踪节点
TSharedPtr<UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode> TrackerNode = 
    MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerIPhoneNode>(TEXT("MyFaceTracker"));

// 2. 配置节点参数
TrackerNode->DNAFile = TEXT("/Game/MetaHumans/Common/Heads/UEFN_Male_01/UEFN_Male_01.dna");
TrackerNode->Camera = TEXT("iPhone");
TrackerNode->bIsFirstPass = true;
TrackerNode->bSkipPredictiveSolver = false;

// 3. 将节点添加到流水线中（流水线对象通常由上层系统管理）
// Pipeline->AddNode(TrackerNode);
```

### 进阶用法

构建一个包含面部追踪和语音驱动动画的复合流水线。这展示了如何将不同类型的节点连接起来，处理不同来源的数据。

```cpp
// 来源：基于多个头文件（FaceTrackerNode.h, SpeechToAnimNode.h）推断的组合用法

// 创建面部追踪节点（处理视频流）
auto FaceTrackerNode = MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerStereoNode>(TEXT("StereoTracker"));
FaceTrackerNode->Calibrations = LoadStereoCameraCalibrations(); // 假设的函数
FaceTrackerNode->DNAAsset = LoadDNAAsset();

// 创建语音转动画节点（处理音频）
auto SpeechToAnimNode = MakeShared<UE::MetaHuman::Pipeline::FSpeechToAnimNode>(TEXT("AudioDrivenAnim"));
SpeechToAnimNode->Audio = LoadSoundWaveAsset();
SpeechToAnimNode->FrameRate = 30.0f;
SpeechToAnimNode->SetMood(EAudioDrivenAnimationMood::Neutral);
SpeechToAnimNode->SetMoodIntensity(0.5f);

// 创建一个动画合并节点，将两种来源的动画数据合并
auto MergeNode = MakeShared<UE::MetaHuman::Pipeline::FAnimationMergeNode>(TEXT("MergeAnimations"));

// 构建流水线连接关系（伪代码，具体连接方式取决于流水线实现）
// Pipeline->Connect(FaceTrackerNode->GetOutputPin("AnimationData"), MergeNode->GetInputPin("Base"));
// Pipeline->Connect(SpeechToAnimNode->GetOutputPin("AnimationData"), MergeNode->GetInputPin("Overlay"));
// Pipeline->SetOutputNode(MergeNode);

// 启动流水线处理
// Pipeline->Start();
// while (Pipeline->ProcessNextFrame()) { ... }
// Pipeline->End();
```

## Demo 示例

一个最小化的示例，演示如何创建一个 `FSpeechToAnimNode` 并设置其基本属性。请注意，实际运行需要完整的流水线上下文和资源。

**MyAudioDrivenAnim.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Nodes/SpeechToAnimNode.h"

class FMyAudioDrivenAnim
{
public:
    void SetupAudioDrivenAnimation();
    
private:
    TSharedPtr<UE::MetaHuman::Pipeline::FSpeechToAnimNode> SpeechNode;
};
```

**MyAudioDrivenAnim.cpp**
```cpp
#include "MyAudioDrivenAnim.h"
#include "Sound/SoundWave.h"

void FMyAudioDrivenAnim::SetupAudioDrivenAnimation()
{
    // 创建节点
    SpeechNode = MakeShared<UE::MetaHuman::Pipeline::FSpeechToAnimNode>(TEXT("MySpeechSolver"));
    
    // 加载音频资产（示例路径）
    USoundWave* AudioAsset = LoadObject<USoundWave>(nullptr, TEXT("/Game/Audio/Dialogue/Line01"));
    if (AudioAsset)
    {
        SpeechNode->Audio = AudioAsset;
    }
    
    // 配置参数
    SpeechNode->FrameRate = 24.0f;
    SpeechNode->OffsetSec = 0.5f; // 从音频的0.5秒处开始处理
    SpeechNode->bClampTongueInOut = true;
    SpeechNode->bGenerateBlinks = true;
    
    // 设置情绪和输出控制
    SpeechNode->SetMood(EAudioDrivenAnimationMood::Happy);
    SpeechNode->SetMoodIntensity(0.7f);
    SpeechNode->SetOutputControls(EAudioDrivenAnimationOutputControls::FullFace);
    
    // 注意：此节点需要被添加到一个有效的 MetaHumanPipeline 中才能执行 Start/Process/End。
    // 通常由 MetaHumanToolkit 或 BatchProcessor 等系统管理。
    UE_LOG(LogTemp, Log, TEXT("SpeechToAnimNode configured. Ready to be added to a pipeline."));
}
```

## 模块依赖

从 `MetaHumanPipeline.Build.cs` 分析，该模块依赖 `UnrealEd`。对于使用者而言，要利用此模块的功能，你的项目模块通常需要依赖 `MetaHumanPipeline` 以及相关的 `MetaHumanCore` 等模块。由于这是一个庞大的插件，具体依赖关系复杂，建议参考插件内其他模块（如 `MetaHumanToolkit`）的 `Build.cs` 来了解完整的依赖图。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 提供编辑器功能，用于节点配置、资产处理等。 |

## 维护状态

### 近期更新

```
- a7fe5bca1c4b 2024-10-03 [CaptureManager] Add camera id to ingested asset metadata
- 90a98e69f1f3 2024-10-02 Fix issues detected by BugHawk #rb aleksandr.cicenkov
- 3deb508fe050 2024-10-01 Update audio solve model to support emotion (2nd attempt) #rb robert.hillary
```

### 维护评价

- **创建时间**：约 1 年前（2024年2月），属于较新的插件。
- **最近更新频率**：**活跃维护**。最近的提交（2024年10月）显示有功能性更新（支持情绪的音频模型、元数据增强）和问题修复。
- **维护状态**：作为 Epic Games 官方 MetaHuman 工具链的核心部分，该插件处于**积极开发和维护**中，是 MetaHuman 生态的关键组件。
- **已知问题或限制**：该插件非常庞大且复杂，模块间耦合度高。`MetaHumanPipeline` 模块本身依赖 `UnrealEd`，这意味着其核心处理逻辑可能无法在纯运行时（非编辑器）环境下使用，更适合编辑器工具或打包后的专用应用。
- **推荐使用**：**强烈推荐**。如果你正在使用 MetaHuman 角色并需要创建高质量的面部动画，这是官方提供的最直接、功能最完整的解决方案。尽管学习曲线较陡，但其提供的自动化流水线能极大提升工作效率。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]()（.uplugin 中未提供 DocsURL）
- [测试用例]()（未在提供的信息中明确指定路径，通常位于 `Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests/` 或 `Engine/Tests/` 下）