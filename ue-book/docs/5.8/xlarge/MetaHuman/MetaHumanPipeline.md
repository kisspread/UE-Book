# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman 数字人资产、追踪器模型、工具集） |
| 模块 | `MetaHumanPipeline` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanFaceTracker` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanToolkit` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的数字人面部动画制作工具集。它提供了一套完整的 **面部追踪（Face Tracking）→ 后处理（Post-Processing）→ 动画求解（Animation Solving）** 管线，用于从各种视频源（立体相机、iPhone 深度摄像头、普通视频）捕获演员面部表演并驱动 MetaHuman 数字人。

**核心问题**：如何从真实演员的面部视频捕获高质量的动画数据，并将其应用到 MetaHuman 角色上？

**解决方案**：MetaHuman Animator 提供了：

1. **多源面部追踪**：支持立体相机（Stereo）、iPhone（TrueDepth）、普通视频等多种输入源
2. **NNE 神经网络追踪器**：基于深度学习的面部特征点检测，包括面部、眼睛、眉毛、嘴唇、牙齿、下巴等 11 个独立追踪器
3. **流式处理管线（Pipeline）**：异步、可缓冲的节点式数据处理架构，支持实时和离线处理
4. **后处理求解**：将追踪到的面部轮廓数据转换为动画控制数据
5. **语音驱动动画**：从音频自动生成面部动画（Speech2Face）
6. **深度生成**：从立体图像生成深度图
7. **光学流**：计算帧间光流用于提高追踪质量

## 使用场景

- **影视制作**：将演员面部表演捕获并应用到 MetaHuman 角色
- **游戏开发**：为游戏内 MetaHuman 角色创建逼真的面部动画
- **实时虚拟人**：使用 iPhone 进行实时面部追踪驱动数字人
- **语音动画**：仅有音频时，自动生成匹配的面部动画
- **批量处理**：处理大量面部动画素材
- **质量诊断**：验证追踪结果的准确性

## 蓝图用法

MetaHuman Animator 的大部分功能在 C++ 管线层面，蓝图接口相对有限。以下是可用的蓝图相关功能：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DoesNNEAssetExist` | 检查 NNE 资产是否存在 | `DoesNNEAssetExist.h` |
| `SetMood` | 设置语音驱动动画的情感 | `FSpeechToAnimNode` |
| `SetMoodIntensity` | 设置情感强度 (0-1) | `FSpeechToAnimNode` |
| `SetOutputControls` | 设置输出控制类型（全脸/选择性） | `FSpeechToAnimNode` |
| `LoadModels` | 加载语音驱动动画模型 | `FSpeechToAnimNode` |
| `CancelModelSolve` | 取消正在进行的模型求解 | `FSpeechToAnimNode` |

## C++ 用法

### 头文件引入

```cpp
// 管线节点
#include "Nodes/FaceTrackerNode.h"
#include "Nodes/HyprsenseNode.h"
#include "Nodes/SpeechToAnimNode.h"
#include "Nodes/FaceTrackerPostProcessingNode.h"
#include "Nodes/AsyncNode.h"

// 工具节点
#include "Nodes/TrackerUtilNodes.h"
#include "Nodes/AnimationUtilNodes.h"
#include "Nodes/ControlUtilNodes.h"

// NNE 资产检查
#include "DoesNNEAssetExist.h"

// 深度图诊断
#include "Nodes/DepthMapDiagnosticsNode.h"
```

### 基本用法：创建 Hyprsense 面部追踪节点

从源码中 `FHyprsenseNode` 的使用方式推断：

```cpp
// 创建 Hyprsense 追踪节点（自动加载 NNE 模型）
FHyprsenseManagedNode* TrackerNode = new FHyprsenseManagedNode("FaceTracker");

// 或指定 NNE 后端
FHyprsenseManagedNode* TrackerNode = new FHyprsenseManagedNode("FaceTracker", "DML");
```

### 基本用法：设置追踪器模型

从 `FHyprsenseNode.h` 提取的 SetTrackers 用法：

```cpp
// 创建追踪节点
FHyprsenseNode HyprsenseNode("MyTracker");

// 设置 NNE 模型（推荐使用 RunSync 接口，5.8 起）
HyprsenseNode.SetTrackers(
    FaceTrackerModel,        // TSharedPtr<NNE::IModelInstanceRunSync>
    FaceDetectorModel,
    EyebrowTrackerModel,
    EyeTrackerModel,
    LipsTrackerModel,
    LipZipTrackerModel,
    NasolabialNoseTrackerModel,
    ChinTrackerModel,
    TeethTrackerModel,
    TeethConfidenceTrackerModel
);

// 选择是否将稀疏追踪结果添加到输出
HyprsenseNode.bAddSparseTrackerResultsToOutput = true;
```

### 基本用法：iPhone 面部追踪

从 `FFaceTrackerIPhoneNode` 提取：

```cpp
// 创建 iPhone 追踪节点（自动加载配置）
FFaceTrackerIPhoneManagedNode* IPhoneTracker = new FFaceTrackerIPhoneManagedNode("IPhoneTracker");

// 设置参数
IPhoneTracker->NumberOfFrames = TotalFrames;  // 总帧数
IPhoneTracker->bSkipDiagnostics = false;      // 是否跳过诊断
IPhoneTracker->bTrackingFailureIsError = true; // 追踪失败是否报错
IPhoneTracker->bSkipPredictiveSolver = false;  // 是否跳过预测求解器
IPhoneTracker->bSkipPerVertexSolve = true;     // 是否跳过逐顶点求解

// 设置 DNA 数据
IPhoneTracker->DNAReader = MyDNAReader;  // TSharedPtr<IDNAReader>

// 设置相机标定
IPhoneTracker->Calibrations = CameraCalibrations;  // TArray<FCameraCalibration>
IPhoneTracker->Camera = "camera_1";
```

### 进阶用法：创建异步追踪管线

从 `FAsyncNode` 模板类提取的用法：

```cpp
// 创建异步版本的 Hyprsense 节点（使用线程池并行处理）
// 模板参数为要异步包装的节点类型，构造参数为并行节点数量 + 节点构造参数
FAsyncNode<FHyprsenseNode> AsyncTracker(
    4,               // 4 个并行节点
    "HyprsenseNode"  // 传递给 FHyprsenseNode 构造函数的参数
);

// 异步节点自动管理：
// - Start: 并行初始化所有内部节点
// - Process: 使用线程池异步处理，支持丢帧
// - Idle: 等待异步结果返回
// - End: 并行结束所有内部节点
```

### 进阶用法：语音驱动动画

从 `FSpeechToAnimNode` 和 `SpeechToAnimNode.h` 提取：

```cpp
// 创建语音驱动动画节点
FSpeechToAnimNode SpeechNode("Speech2Face");

// 加载模型
FAudioDrivenAnimationModels Models = /* 从资产加载 */;
SpeechNode.LoadModels(Models);

// 设置情感
SpeechNode.SetMood(EAudioDrivenAnimationMood::Neutral);
SpeechNode.SetMoodIntensity(0.7f);

// 设置输出控制类型
SpeechNode.SetOutputControls(EAudioDrivenAnimationOutputControls::FullFace);

// 设置音频输入
SpeechNode.Audio = SoundWaveAsset;  // TWeakObjectPtr<USoundWave>
SpeechNode.bDownmixChannels = true;
SpeechNode.AudioChannelIndex = 0;

// 时间参数
SpeechNode.OffsetSec = 0.0f;       // 从音频的哪个时间开始求解
SpeechNode.FrameRate = 30.0f;
SpeechNode.ProcessingStartFrameOffset = 0;

// 控制行为
SpeechNode.bClampTongueInOut = true;  // 钳制舌头控制
SpeechNode.bGenerateBlinks = true;     // 生成眨眼动画
```

### 进阶用法：后处理和滤波

从 `FFaceTrackerPostProcessingNode` 提取：

```cpp
// 创建后处理节点（自动加载配置）
FFaceTrackerPostProcessingManagedNode* PostProcessNode = 
    new FFaceTrackerPostProcessingManagedNode("PostProcess");

// 设置数据
PostProcessNode->DNAReader = MyDNAReader;
PostProcessNode->Calibrations = CameraCalibrations;
PostProcessNode->Camera = "camera_1";
PostProcessNode->bDisableGlobalSolves = false;

// 设置网格求解器定义类型
PostProcessNode->MeshSolverDefinitionsType = EMeshSolverDefinitionsType::Standard;
// 可选值：
// - Standard: 标准求解器
// - Hierarchical: 层次求解器
// - HierarchicalPlusChinCompress: 层次求解器 + 下巴压缩
```

### 进阶用法：动画合并

从 `FAnimationMergeNode` 提取：

```cpp
// 合并两组动画数据
FAnimationMergeNode MergeNode("MergeAnimations");
MergeNode.Animation0Name = "face_tracking";   // 用于日志的友好名称
MergeNode.Animation1Name = "speech_animation";

// 管线中第一个 FFrameAnimationData 为基础
// 第二个 FFrameAnimationData 的控制值会覆盖第一个中的同名控制
// 如果第二个包含第一个中不存在的控制名，会报错
```

## Demo 示例

一个完整的、可编译的最小示例，展示如何使用 MetaHuman Pipeline 构建一个简单的面部追踪处理链：

```cpp
// MyFaceTrackingPipeline.h
#pragma once

#include "CoreMinimal.h"
#include "Pipeline/PipelineData.h"
#include "Nodes/FaceTrackerNode.h"
#include "Nodes/HyprsenseNode.h"
#include "Nodes/FaceTrackerPostProcessingNode.h"
#include "Nodes/FaceTrackerPostProcessingFilterNode.h"
#include "Nodes/DepthMapDiagnosticsNode.h"

class FMyFaceTrackingPipeline
{
public:
    FMyFaceTrackingPipeline();
    ~FMyFaceTrackingPipeline();

    /** 初始化管线，加载所有配置和模型 */
    bool Initialize(const FString& InDNAFilePath, const TArray<FCameraCalibration>& InCalibrations);
    
    /** 处理单帧图像数据 */
    bool ProcessFrame(const TSharedPtr<FPipelineData>& InFrameData);
    
    /** 结束处理 */
    bool Finalize();

private:
    /** Hyprsense NNE 追踪节点 */
    TSharedPtr<UE::MetaHuman::Pipeline::FHyprsenseManagedNode> HyprsenseTracker;
    
    /** 立体相机面部追踪节点 */
    TSharedPtr<UE::MetaHuman::Pipeline::FFaceTrackerStereoNode> StereoTracker;
    
    /** 后处理节点 */
    TSharedPtr<UE::MetaHuman::Pipeline::FFaceTrackerPostProcessingManagedNode> PostProcessor;
    
    /** 后处理滤波节点 */
    TSharedPtr<UE::MetaHuman::Pipeline::FFaceTrackerPostProcessingFilterManagedNode> PostProcessFilter;
    
    /** 深度图诊断节点 */
    TSharedPtr<UE::MetaHuman::Pipeline::FDepthMapDiagnosticsNode> DepthDiagnostics;
};
```

```cpp
// MyFaceTrackingPipeline.cpp
#include "MyFaceTrackingPipeline.h"
#include "DNAReader.h"

FMyFaceTrackingPipeline::FMyFaceTrackingPipeline() = default;
FMyFaceTrackingPipeline::~FMyFaceTrackingPipeline() = default;

bool FMyFaceTrackingPipeline::Initialize(
    const FString& InDNAFilePath, 
    const TArray<FCameraCalibration>& InCalibrations)
{
    // 1. 创建 Hyprsense 追踪器（自动加载 NNE 模型）
    HyprsenseTracker = MakeShared<UE::MetaHuman::Pipeline::FHyprsenseManagedNode>(
        TEXT("HyprsenseTracker"));
    
    // 2. 创建立体相机追踪器
    StereoTracker = MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerStereoNode>(
        TEXT("StereoTracker"));
    StereoTracker->Calibrations = InCalibrations;
    StereoTracker->Camera = TEXT("camera_main");
    StereoTracker->DNAFile = InDNAFilePath;
    StereoTracker->bTrackingFailureIsError = true;
    StereoTracker->bSkipPredictiveSolver = false;
    
    // 3. 创建后处理节点
    PostProcessor = MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerPostProcessingManagedNode>(
        TEXT("PostProcessor"));
    PostProcessor->Calibrations = InCalibrations;
    PostProcessor->Camera = TEXT("camera_main");
    PostProcessor->DNAFile = InDNAFilePath;
    PostProcessor->MeshSolverDefinitionsType = EMeshSolverDefinitionsType::Standard;
    PostProcessor->bDisableGlobalSolves = false;
    
    // 4. 创建后处理滤波节点
    PostProcessFilter = MakeShared<UE::MetaHuman::Pipeline::FFaceTrackerPostProcessingFilterManagedNode>(
        TEXT("PostProcessFilter"));
    PostProcessFilter->DNAFile = InDNAFilePath;
    PostProcessFilter->MeshSolverDefinitionsType = EMeshSolverDefinitionsType::Standard;
    
    // 5. 创建深度图诊断节点（可选，用于立体相机）
    DepthDiagnostics = MakeShared<UE::MetaHuman::Pipeline::FDepthMapDiagnosticsNode>(
        TEXT("DepthDiagnostics"));
    DepthDiagnostics->Calibrations = InCalibrations;
    DepthDiagnostics->Camera = TEXT("camera_main");
    
    return true;
}

bool FMyFaceTrackingPipeline::ProcessFrame(const TSharedPtr<FPipelineData>& InFrameData)
{
    if (!InFrameData.IsValid())
    {
        return false;
    }
    
    // 执行 Hyprsense NNE 追踪
    if (!HyprsenseTracker->Process(InFrameData))
    {
        UE_LOG(LogTemp, Warning, TEXT("Hyprsense tracking failed: %s"), 
            *HyprsenseTracker->GetErrorMessage());
        return false;
    }
    
    // 执行立体相机面部追踪
    if (!StereoTracker->Process(InFrameData))
    {
        UE_LOG(LogTemp, Warning, TEXT("Stereo tracking failed"));
        return false;
    }
    
    // 执行后处理
    if (!PostProcessor->Process(InFrameData))
    {
        UE_LOG(LogTemp, Warning, TEXT("Post processing failed"));
        return false;
    }
    
    // 执行滤波
    if (!PostProcessFilter->Process(InFrameData))
    {
        UE_LOG(LogTemp, Warning, TEXT("Post processing filter failed"));
        return false;
    }
    
    return true;
}

bool FMyFaceTrackingPipeline::Finalize()
{
    auto EndNode = [](auto& Node, const TSharedPtr<FPipelineData>& Data) 
    {
        if (Node.IsValid())
        {
            Node->End(Data);
        }
    };
    
    auto PipelineData = MakeShared<FPipelineData>();
    EndNode(HyprsenseTracker, PipelineData);
    EndNode(StereoTracker, PipelineData);
    EndNode(PostProcessor, PipelineData);
    EndNode(PostProcessFilter, PipelineData);
    EndNode(DepthDiagnostics, PipelineData);
    
    return true;
}
```

## 模块依赖

从各模块的 Build.cs 提取，省略常见依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库（底层数学和算法） |
| `MetaHumanSDKEditor` | MetaHuman SDK 编辑器接口 |
| `ControlRigDeveloper` | Control Rig 开发者接口，用于动画控制 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体工具函数 |
| `MetaHumanImageViewerEditor` | 图像查看器编辑器组件 |
| `NNE` | Neural Network Engine，神经网络推理引擎 |
| `MetaHumanCaptureDataEditor` | 捕获数据编辑器 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器 |
| `MetaHumanFaceFittingSolver` | 面部适配求解器 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器 |
| `MetaHumanDepthGenerator` | 深度图生成器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 禁用身体追踪时的关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已存在网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题 |

### 维护评价

- **创建时间**：约 4 年前（UE5 早期版本）
- **维护频率**：**活跃维护**。最近一周内有 5 次提交，涵盖功能增强（身体追踪、动画导出）、Bug 修复（渲染伪影、缓存问题）
- **活跃度**：Epic Games 官方重点维护项目，是 MetaHuman 产品线的核心组件
- **代码规模**：544 个源文件，28 个模块，属于大型复杂插件
- **已知限制**：需要 MetaHuman 模型资产配合使用；部分功能（如 Speech2Face）需要特定的预训练模型
- **推荐程度**：**强烈推荐**用于任何涉及 MetaHuman 数字人动画制作的项目。这是 Epic Games 官方的生产级工具，持续获得更新和支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/)（Epic Games 官方 MetaHuman Animator 文档）
- [MetaHuman 官网](https://www.unrealengine.com/en-US/metahuman)