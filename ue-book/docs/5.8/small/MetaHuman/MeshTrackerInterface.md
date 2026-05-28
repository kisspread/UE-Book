# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、材质模板） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-08-01 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 提供的完整 MetaHuman 动画制作工具链。它不是单个功能，而是一整套从面部捕捉数据采集到最终动画输出的端到端管线：

1. **面部追踪（Face Tracking）**：通过多相机立体视觉追踪面部关键点，输出头部姿态和面部控制参数
2. **深度图生成（Depth Generation）**：从多视角图像进行立体重建，生成面部深度图
3. **光流计算（Optical Flow）**：帧间运动估计，辅助追踪稳定性
4. **面部动画求解（Face Animation Solving）**：将追踪数据转化为 MetaHuman 面部骨骼动画
5. **面部拟合求解（Face Fitting Solving）**：将面部追踪结果拟合到特定 MetaHuman 骨骼形态
6. **预测求解器（Predictive Solver）**：基于机器学习的动画增强，包括眼睛注视和牙齿动画的全局优化
7. **语音驱动面部（Speech2Face）**：从音频生成面部动画
8. **序列器集成（Sequencer）**：将动画结果导入 UE5 序列器
9. **批量处理（Batch Processor）**：支持批量导入和处理面部捕捉数据

该插件采用模块化架构，核心计算引擎通过 `IModularFeature` 接口注册，实际的追踪/求解实现由独立插件（如 MeshTracker）提供。

## 使用场景

- 你使用 iPhone 或专业多相机系统拍摄了面部表演视频 → 用 MetaHuman Animator 导入、追踪并生成动画
- 你需要将真实演员的面部表演转移到 MetaHuman 角色上 → 用 Identity 系统匹配面部形态 + Performance 系统驱动动画
- 你有大量面部捕捉数据需要批量处理 → 用 MetaHumanBatchProcessor
- 你想从音频对话自动生成面部动画 → 用 Speech2Face 模块
- 你需要在 Sequencer 中编辑和混合面部动画 → 用 MetaHumanSequencer 模块

## 蓝图用法

### 核心节点

由于 MeshTrackerInterface 是纯 C++ 接口层，大部分高级功能通过编辑器 UI 和 Python/命令行工具暴露。可编程的运行时接口如下：

| 接口 | 说明 | 所在类 |
|---|---|---|
| `IMetaHumanFaceTrackerInterface` | 面部追踪主接口：初始化、加载 DNA、设置相机、执行追踪 | 接口（由 ModularFeature 工厂创建） |
| `IDepthGeneratorInterface` | 深度图生成：立体重建生成深度图 | 接口 |
| `IOpticalFlowInterface` | 光流计算：帧间运动估计 | 接口 |
| `IFaceTrackerPostProcessingInterface` | 追踪后处理：全局求解（眼睛注视、牙齿拟合） | 接口 |
| `IFaceTrackerPostProcessingFilter` | 后处理滤波：离线平滑和修正 | 接口 |
| `IPredictiveSolverInterface` | 预测求解器训练：机器学习模型训练 | `IModularFeature` |

### 使用示例（C++ 调用流程）

由于 MetaHuman Animator 的核心 API 是 C++ 接口，蓝图层面主要通过编辑器 Widget 操作。以下是典型的面部追踪工作流：

```
1. 初始化追踪器
   → IMetaHumanFaceTrackerInterface::Init(Json配置, 设备LUID)

2. 加载面部 DNA
   → LoadDNA(IDNAReader)

3. 设置相机校准
   → SetCameras(相机校准数组)

4. 设置立体相机对
   → SetStereoCameraPairs(相机对列表)

5. 逐帧追踪循环
   → SetInputData(图像数据, 关键点数据, 深度图数据)
   → Track(帧号)
   → GetTrackingState(头部姿态, 控制参数, 网格顶点)

6. 后处理（全局优化）
   → OfflineSolvePrepare(首帧, 帧数, 追踪数据, 帧动画数据)
   → OfflineSolveProcessFrame(帧号, 帧动画数据)

7. 导出动画
   → MetaHumanSequencer 模块处理
```

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanFaceTrackerInterface.h"
```

### 基本用法

**获取面部追踪器实例**（通过 ModularFeature 工厂模式）：

```cpp
#include "MetaHumanFaceTrackerInterface.h"
#include "Features/IModularFeatures.h"

// 获取工厂实例
IFaceTrackerNodeImplFactory* Factory = IModularFeatures::Get()
    .GetModularInstance<IFaceTrackerNodeImplFactory>(
        IFaceTrackerNodeImplFactory::GetModularFeatureName());

if (Factory)
{
    // 创建面部追踪器
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = 
        Factory->CreateFaceTrackerImplementor();
    
    // 创建深度生成器
    TSharedPtr<IDepthGeneratorInterface> DepthGenerator = 
        Factory->CreateDepthGeneratorImplementor();
    
    // 创建光流计算器
    TSharedPtr<IOpticalFlowInterface> OpticalFlow = 
        Factory->CreateOpticalFlowImplementor();
}
```

**初始化并执行面部追踪**：

```cpp
// 初始化追踪器
bool bSuccess = FaceTracker->Init(
    TemplateDescriptionJson,   // 模板描述 JSON
    ConfigurationJson,          // 配置 JSON
    OpticalFlowConfig,          // 光流配置
    PhysicalDeviceLUID          // GPU 设备 LUID
);

// 加载 DNA（面部骨骼形态定义）
FaceTracker->LoadDNA(DNAFilePath);
// 或使用 IDNAReader（推荐，UE 5.8+）
FaceTracker->LoadDNA(DNAReaderSharedPtr);

// 设置相机校准参数
TArray<FCameraCalibration> Calibrations;
// ... 填充校准数据
FaceTracker->SetCameras(Calibrations);

// 设置相机范围
TMap<FString, TPair<float, float>> CameraRanges;
FaceTracker->SetCameraRanges(CameraRanges);

// 设置立体重建相机对
TArray<TPair<FString, FString>> StereoPairs;
FaceTracker->SetStereoCameraPairs(StereoPairs);

// 重置追踪（指定帧范围）
FaceTracker->ResetTrack(0, 100, OpticalFlowConfig);
```

### 进阶用法

**逐帧追踪并获取结果**：

```cpp
// 设置输入数据（图像、关键点、深度图）
TMap<FString, const unsigned char*> ImageDataPerCamera;
TMap<FString, const FFrameTrackingContourData*> LandmarksPerCamera;
TMap<FString, const float*> DepthMapPerCamera;

// ... 填充图像和追踪数据
FaceTracker->SetInputData(ImageDataPerCamera, LandmarksPerCamera, DepthMapPerCamera);

// 执行追踪
FaceTracker->Track(InFrameNumber);

// 获取追踪结果
FTransform HeadPose;
TArray<float> HeadPoseRaw;
TMap<FString, float> Controls;       // UI 控制参数
TMap<FString, float> RawControls;    // 原始控制参数
TArray<float> FaceMeshVertices;
TArray<float> TeethMeshVertices;
TArray<float> LeftEyeMeshVertices;
TArray<float> RightEyeMeshVertices;

FaceTracker->GetTrackingState(
    InFrameNumber, HeadPose, HeadPoseRaw,
    Controls, RawControls, FaceMeshVertices,
    TeethMeshVertices, LeftEyeMeshVertices, RightEyeMeshVertices
);
```

**后处理：全局求解（眼睛注视 + 牙齿优化）**：

```cpp
TSharedPtr<IFaceTrackerPostProcessingInterface> PostProcessing = 
    Factory->CreateFaceTrackerPostProcessingImplementor();

PostProcessing->Init(TemplateDescriptionJson, ConfigurationJson);
PostProcessing->LoadDNA(DNAFile, SolverDefinitionsJson);
PostProcessing->SetCameras(Calibrations, CameraName);

// 设置预测求解器
TArray<uint8> TeethSolverBuffer;
FaceTracker->GetGlobalTeethPredictiveSolver(TeethSolverBuffer);
PostProcessing->SetGlobalTeethPredictiveSolver(TeethSolverBuffer);

// 离线全局求解准备（眼睛注视校正、牙齿拟合）
TArray<FFrameAnimationData> FrameData;
PostProcessing->OfflineSolvePrepare(
    InFrameNumberFirst, InNumFramesToSolve, 
    TrackingData, FrameData, DebugFolder
);

// 逐帧处理
TArray<int32> UpdatedFrames;
PostProcessing->OfflineSolveProcessFrame(
    InFrameNumber, InFrameNumberFirst, InNumFramesToSolve,
    FrameData, UpdatedFrames
);
```

**训练预测求解器**：

```cpp
// 通过 ModularFeature 获取预测求解器
IPredictiveSolverInterface* PredictiveSolver = 
    IModularFeatures::Get().GetModularInstance<IPredictiveSolverInterface>(
        IPredictiveSolverInterface::GetModularFeatureName());

// 异步训练
std::atomic<bool> bIsDone{false};
std::atomic<float> Progress{0.0f};
std::atomic<bool> bCancelled{false};

FPredictiveSolversTaskConfig Config;
FPredictiveSolversResult Result;

PredictiveSolver->TrainPredictiveSolver(
    bIsDone, Progress,
    [](float P) { /* 进度回调 */ },
    bCancelled, Config, Result
);
```

**深度图生成**：

```cpp
TSharedPtr<IDepthGeneratorInterface> DepthGen = 
    Factory->CreateDepthGeneratorImplementor();

DepthGen->Init(PhysicalDeviceLUID);
DepthGen->SetCameras(Calibrations);
DepthGen->SetStereoCameraPairs(StereoPairs);
DepthGen->SetInputData(ImageDataPerCamera);

// 获取深度图
int32 Width, Height;
const float* DepthData;
const float* Intrinsics;
const float* Extrinsics;
DepthGen->GetDepthMap(StereoPairIndex, Width, Height, DepthData, Intrinsics, Extrinsics);
```

## Demo 示例

```cpp
// MetaHumanTrackerExample.h
#pragma once

#include "CoreMinimal.h"
#include "MetaHumanFaceTrackerInterface.h"

class FMetaHumanTrackerExample
{
public:
    void RunTracking(const FString& DNAPath, const FString& ConfigPath);
    
private:
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker;
    TSharedPtr<IFaceTrackerPostProcessingInterface> PostProcessing;
    
    bool InitializeTracker(const FString& ConfigPath);
    bool TrackSequence(const FString& DNAPath, int32 NumFrames);
    void PostProcessResults(int32 NumFrames);
};
```

```cpp
// MetaHumanTrackerExample.cpp
#include "MetaHumanTrackerExample.h"
#include "Features/IModularFeatures.h"

void FMetaHumanTrackerExample::RunTracking(const FString& DNAPath, const FString& ConfigPath)
{
    if (!InitializeTracker(ConfigPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize face tracker"));
        return;
    }
    
    // 加载 DNA
    if (!FaceTracker->LoadDNA(DNAPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load DNA: %s"), *DNAPath);
        return;
    }
    
    // 执行 100 帧追踪
    const int32 NumFrames = 100;
    if (!TrackSequence(DNAPath, NumFrames))
    {
        UE_LOG(LogTemp, Error, TEXT("Tracking failed"));
        return;
    }
    
    // 后处理
    PostProcessResults(NumFrames);
}

bool FMetaHumanTrackerExample::InitializeTracker(const FString& ConfigPath)
{
    // 通过 ModularFeature 获取工厂
    IFaceTrackerNodeImplFactory* Factory = IModularFeatures::Get()
        .GetModularInstance<IFaceTrackerNodeImplFactory>(
            IFaceTrackerNodeImplFactory::GetModularFeatureName());
    
    if (!Factory)
    {
        UE_LOG(LogTemp, Error, TEXT("FaceTrackerNodeFactory not found"));
        return false;
    }
    
    FaceTracker = Factory->CreateFaceTrackerImplementor();
    PostProcessing = Factory->CreateFaceTrackerPostProcessingImplementor();
    
    if (!FaceTracker.IsValid())
    {
        return false;
    }
    
    // 加载配置
    FString TemplateJson, ConfigJson;
    // ... 从 ConfigPath 读取 JSON
    
    FTrackerOpticalFlowConfiguration OptFlowConfig;
    
    return FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, TEXT(""));
}

bool FMetaHumanTrackerExample::TrackSequence(const FString& DNAPath, int32 NumFrames)
{
    FTrackerOpticalFlowConfiguration OptFlowConfig;
    if (!FaceTracker->ResetTrack(0, NumFrames, OptFlowConfig))
    {
        return false;
    }
    
    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        // 设置当前帧输入数据
        TMap<FString, const unsigned char*> ImageData;
        TMap<FString, const FFrameTrackingContourData*> Landmarks;
        
        // ... 填充 ImageData 和 Landmarks
        FaceTracker->SetInputData(ImageData, Landmarks);
        
        // 执行追踪
        if (!FaceTracker->Track(Frame))
        {
            UE_LOG(LogTemp, Warning, TEXT("Tracking failed at frame %d"), Frame);
            continue;
        }
        
        // 获取结果
        FTransform HeadPose;
        TArray<float> HeadPoseRaw;
        TMap<FString, float> Controls, RawControls;
        TArray<float> FaceVerts, TeethVerts, LeftEyeVerts, RightEyeVerts;
        
        FaceTracker->GetTrackingState(
            Frame, HeadPose, HeadPoseRaw,
            Controls, RawControls, FaceVerts,
            TeethVerts, LeftEyeVerts, RightEyeVerts
        );
        
        UE_LOG(LogTemp, Log, TEXT("Frame %d: Head at %s"), 
            Frame, *HeadPose.GetLocation().ToString());
    }
    
    return true;
}

void FMetaHumanTrackerExample::PostProcessResults(int32 NumFrames)
{
    if (!PostProcessing.IsValid())
    {
        return;
    }
    
    // ... 初始化 PostProcessing（Init, LoadDNA, SetCameras 等）
    
    TArray<FFrameTrackingContourData> AllTrackingData;
    TArray<FFrameAnimationData> AllFrameData;
    
    // 全局求解（眼睛注视校正 + 牙齿拟合）
    PostProcessing->OfflineSolvePrepare(0, NumFrames, AllTrackingData, AllFrameData);
    
    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        TArray<int32> UpdatedFrames;
        PostProcessing->OfflineSolveProcessFrame(
            Frame, 0, NumFrames, AllFrameData, UpdatedFrames);
    }
}
```

## 模块依赖

本插件包含 28 个模块，模块间依赖关系复杂。以下是外部独特依赖：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | MetaHumanIdentity 模块依赖，用于骨骼控制绑定开发 |
| `SkeletalMeshUtilitiesCommon` | MetaHumanIdentity 模块依赖，用于骨骼网格体工具 |
| `MetaHumanSDKEditor` | MetaHumanIdentity 模块依赖，与 MetaHuman SDK 编辑器集成 |
| `MetaHumanCoreTechLib` | MetaHumanConfig 模块依赖，MetaHuman 核心技术库（底层算法） |

大部分模块仅依赖标准 Core/Engine/Slate 等常见模块。注意 `MetaHumanCore` 和 `MetaHumanPipeline` 依赖 `UnrealEd`，表明这些模块仅在编辑器环境中可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染伪影 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存问题 |

### 维护评价

**活跃维护中** ✅

- MetaHuman Animator 是 Epic Games 的旗舰产品级插件，承载着 MetaHuman 生态系统的核心动画管线
- 近期（2026 年 5 月）仍有多次实质性更新，包括身体追踪集成、渲染修复和序列器改进
- 插件规模庞大（28 个模块、544 个源文件），说明功能仍在持续扩展
- 采用模块化架构（IModularFeature），便于第三方扩展和引擎版本迁移
- 作为 Epic 官方工具链，享有最高优先级的维护和更新

**注意事项**：
- 插件标记为 `EnabledByDefault: false`，需要在项目设置中手动启用
- 部分高级功能需要配套的 MeshTracker 插件（提供实际的追踪/求解实现）
- 面部追踪管线依赖 GPU 计算，需要支持的硬件设备

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [MetaHuman 官方文档](https://docs.unrealengine.com/en-US/metahuman/)
- [MeshTrackerInterface 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h)