# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 制作工具链，它不是一个单一功能的插件，而是一个完整的动画制作流水线。其核心目的是将真实人物的面部表演捕获数据，转化为可以在 Unreal Engine 中驱动 MetaHuman 数字人的动画资产。它解决的问题是：如何高效、准确地从 iPhone 或专业多相机系统捕获的视频/深度数据中，提取面部肌肉的运动信息，并应用到 MetaHuman 的骨骼和蒙皮系统上，最终生成可用于 Sequencer 的动画序列。该插件包含了从数据导入、面部跟踪、动画解算、后处理到最终导出的全套工具。

## 使用场景

- **表演动画制作**：你有一段演员表演的面部视频（来自 iPhone 的 TrueDepth 相机或多相机系统），需要为你的 MetaHuman 角色创建同步的动画。
- **面部跟踪与解算**：你需要对捕获的视频进行面部特征点跟踪、深度图生成，并基于这些数据解算出 MetaHuman 的面部控制参数。
- **动画后处理与优化**：原始跟踪数据可能存在抖动或不准确，需要应用过滤、全局牙齿/眼动解算等后处理步骤来提升动画质量。
- **批量处理**：你有大量的表演片段需要处理成动画，可以使用 `MetaHumanBatchProcessor` 模块进行自动化批量作业。
- **创建数字人资产**：你需要将真实的人脸照片或扫描数据，通过 `MetaHumanIdentity` 模块转化为可用于 MetaHuman 系统的拓扑资产。

## 蓝图用法

该插件的核心功能主要通过 C++ 接口和模块化特性提供，直接暴露给蓝图的函数较少。其使用通常通过编辑器中的专用资产（如 `MetaHumanPerformance`）和菜单/操作来完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCameras` | 设置用于跟踪的相机校准数据。 | `IMetaHumanFaceTrackerInterface` |
| `LoadDNA` | 加载 DNA 文件或资产，为面部网格提供变形基础。 | `IMetaHumanFaceTrackerInterface` |
| `Track` | 对一帧输入数据执行面部跟踪。 | `IMetaHumanFaceTrackerInterface` |
| `GetTrackingState` | 获取跟踪结果，包括头部姿态、控制参数和面部网格顶点。 | `IMetaHumanFaceTrackerInterface` |
| `OfflineSolvePrepare` | 执行离线全局解算准备，如眼动和牙齿校正。 | `IFaceTrackerPostProcessingInterface` |
| `OfflineFilter` | 对动画数据进行离线滤波，平滑结果。 | `IFaceTrackerPostProcessingFilter` |

### 使用示例（蓝图描述）

由于核心算法接口多为 C++ 纯虚类，典型的蓝图工作流并非直接连接函数节点。正确的方式是：
1.  在内容浏览器中，右键创建 `MetaHumanPerformance` 类型的资产。
2.  该资产的编辑器面板提供完整的向导式界面，引导用户导入视频、选择 DNA、配置相机、执行跟踪和解算。
3.  最终，在 `MetaHumanPerformance` 资产上右键选择“Export to Sequence”，即可将生成的动画数据导出为可放入 Sequencer 的 Level Sequence 资产。
此流程封装了底层对 `IMetaHumanFaceTrackerInterface` 和 `IFaceTrackerPostProcessingInterface` 等接口的复杂调用。

## C++ 用法

该插件主要通过接口（Interface）和模块化特性（Modular Feature）进行扩展和使用。核心算法由 `FaceTrackerNodeFactory` 模块化特性提供，应用层代码通常通过工厂创建具体的实现。

### 头文件引入

```cpp
#include "MetaHumanFaceTrackerInterface.h" // 包含所有核心接口定义
```

### 基本用法

以下示例展示了如何获取并使用面部跟踪器接口。（来源：基于 `IMetaHumanFaceTrackerInterface` 和 `IFaceTrackerNodeImplFactory` 接口设计的典型用法）

```cpp
// 1. 获取面部跟踪器节点工厂
IModularFeatures& ModularFeatures = IModularFeatures::Get();
if (ModularFeatures.IsModularFeatureAvailable(IFaceTrackerNodeImplFactory::GetModularFeatureName()))
{
    IFaceTrackerNodeImplFactory& Factory = ModularFeatures.GetModularFeature<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());

    // 2. 创建面部跟踪器实例
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = Factory.CreateFaceTrackerImplementor();

    // 3. 初始化跟踪器
    FString TemplateJson = TEXT("{\"...\": \"...\"}"); // 从配置资产加载
    FString ConfigJson = TEXT("{\"...\": \"...\"}");
    FTrackerOpticalFlowConfiguration OptFlowConfig;
    FString PhysicalDeviceLUID = TEXT("0"); // GPU设备标识，可为空
    if (FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, PhysicalDeviceLUID))
    {
        // 4. 加载DNA资产
        TSharedPtr<IDNAReader> DnaReader = /* 从DNA资产获取 */;
        FaceTracker->LoadDNA(DnaReader);

        // 5. 设置相机校准数据
        TArray<FCameraCalibration> Calibrations;
        // ... 填充校准数据 ...
        FaceTracker->SetCameras(Calibrations);

        // 6. 设置跟踪范围并开始跟踪
        FaceTracker->ResetTrack(0, 100, OptFlowConfig);
        
        for (int32 Frame = 0; Frame < 100; ++Frame)
        {
            // 准备该帧的图像和地标数据
            TMap<FString, const unsigned char*> ImageDataPerCamera;
            TMap<FString, const FFrameTrackingContourData*> LandmarkData;
            // ... 填充数据 ...

            // 执行跟踪
            FaceTracker->SetInputData(ImageDataPerCamera, LandmarkData);
            FaceTracker->Track(Frame);

            // 获取结果
            FTransform HeadPose;
            TArray<float> HeadPoseRaw;
            TMap<FString, float> Controls, RawControls;
            TArray<float> FaceMeshVertices;
            FaceTracker->GetTrackingState(Frame, HeadPose, HeadPoseRaw, Controls, RawControls, FaceMeshVertices);
            
            // 使用 Controls 和 MeshVertices 驱动 MetaHuman 角色
        }
    }
}
```

### 进阶用法

跟踪完成后，通常需要后处理来优化动画质量。这涉及 `IFaceTrackerPostProcessingInterface`。

```cpp
// 接续上面的跟踪循环
TArray<FFrameTrackingContourData> AllTrackingData; // 假设已收集所有帧的跟踪数据
TArray<FFrameAnimationData> AllFrameAnimationData; // 假设已从GetTrackingState构建

// 获取后处理器实例
TSharedPtr<IFaceTrackerPostProcessingInterface> PostProcessor = Factory.CreateFaceTrackerPostProcessingImplementor();
PostProcessor->Init(TemplateJson, ConfigJson);
PostProcessor->LoadDNA(DnaReader, SolverDefinitionsJson); // 需要解算器定义JSON

// 执行离线全局解算（如眼动、牙齿）
const int32 FirstFrame = 0;
const int32 NumFrames = AllTrackingData.Num();
FString DebugFolder = TEXT("C:/Temp/MH_Debug");
PostProcessor->OfflineSolvePrepare(FirstFrame, NumFrames, AllTrackingData, AllFrameAnimationData, DebugFolder);

// 逐帧应用全局解算结果
for (int32 Frame = FirstFrame; Frame < NumFrames; ++Frame)
{
    TArray<int32> UpdatedFrames;
    PostProcessor->OfflineSolveProcessFrame(Frame, FirstFrame, NumFrames, AllFrameAnimationData, UpdatedFrames);
    // UpdatedFrames 会告知哪些帧因全局解算而被更新
}

// 可选：应用滤波器进一步平滑
TSharedPtr<IFaceTrackerPostProcessingFilter> Filter = Factory.CreateFaceTrackerPostProcessingFilterImplementor();
Filter->Init(TemplateJson, ConfigJson);
Filter->LoadDNA(DnaReader, SolverDefinitionsJson);
Filter->OfflineFilter(FirstFrame, NumFrames, AllFrameAnimationData);
```

## Demo 示例

以下示例演示了如何以编程方式执行一次基本的面部跟踪任务。（注：实际运行需要有效的配置JSON、DNA文件和图像数据）

```cpp
// MetaHumanFaceTrackerDemo.h
#pragma once

#include "CoreMinimal.h"

class FMetaHumanFaceTrackerDemo
{
public:
    static void RunDemo();
};
```

```cpp
// MetaHumanFaceTrackerDemo.cpp
#include "MetaHumanFaceTrackerDemo.h"
#include "MetaHumanFaceTrackerInterface.h"
#include "IModularFeatures.h"

void FMetaHumanFaceTrackerDemo::RunDemo()
{
    // 1. 检查并获取工厂
    if (!IModularFeatures::Get().IsModularFeatureAvailable(IFaceTrackerNodeImplFactory::GetModularFeatureName()))
    {
        UE_LOG(LogTemp, Error, TEXT("FaceTrackerNodeFactory 模块化特性不可用。MetaHuman Animator 插件可能未启用或加载失败。"));
        return;
    }
    auto& Factory = IModularFeatures::Get().GetModularFeature<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());

    // 2. 创建跟踪器和后处理器
    auto Tracker = Factory.CreateFaceTrackerImplementor();
    auto PostProcessor = Factory.CreateFaceTrackerPostProcessingImplementor();

    // 3. 配置参数（实际项目中应从资产加载）
    FString TemplateJson = TEXT("{\"template_description\": \"...\"}");
    FString ConfigJson = TEXT("{\"configuration\": \"...\"}");
    FString SolverDefsJson = TEXT("{\"solver_definitions\": \"...\"}");
    FTrackerOpticalFlowConfiguration OptFlowConfig;

    // 4. 初始化
    if (!Tracker->Init(TemplateJson, ConfigJson, OptFlowConfig, TEXT(""))) return;
    if (!PostProcessor->Init(TemplateJson, ConfigJson)) return;

    // 5. 加载DNA (假设路径已知)
    FString DnaPath = TEXT("/Game/MetaHumans/Common/Female/Tall/NormalWeight/F_Tall_NormalWeight");
    Tracker->LoadDNA(DnaPath);
    PostProcessor->LoadDNA(DnaPath, SolverDefsJson);

    // 6. 模拟跟踪（实际需真实数据）
    TArray<FCameraCalibration> Cals;
    // ... 填充校准数据
    Tracker->SetCameras(Cals);
    Tracker->ResetTrack(0, 10, OptFlowConfig);

    TArray<FFrameTrackingContourData> TrackingResults;
    TArray<FFrameAnimationData> AnimationResults;

    for (int32 i = 0; i < 10; ++i)
    {
        TMap<FString, const unsigned char*> Images;
        TMap<FString, const FFrameTrackingContourData*> Landmarks;
        // ... 准备数据 Images, Landmarks for frame i
        Tracker->SetInputData(Images, Landmarks);
        Tracker->Track(i);

        FTransform Pose;
        TArray<float> RawPose;
        TMap<FString, float> Controls, RawControls;
        TArray<float> Verts;
        Tracker->GetTrackingState(i, Pose, RawPose, Controls, RawControls, Verts);

        // 存储结果用于后处理
        FFrameTrackingContourData FrameContourData;
        // ... 从 Landmarks 或 Controls 构建
        TrackingResults.Add(FrameContourData);

        FFrameAnimationData FrameAnimData;
        // ... 从 Controls, Pose, Verts 构建
        AnimationResults.Add(FrameAnimData);
    }

    // 7. 后处理优化
    PostProcessor->OfflineSolvePrepare(0, 10, TrackingResults, AnimationResults);
    for (int32 i = 0; i < 10; ++i)
    {
        TArray<int32> Updated;
        PostProcessor->OfflineSolveProcessFrame(i, 0, 10, AnimationResults, Updated);
    }

    UE_LOG(LogTemp, Log, TEXT("MetaHuman Animator Demo 完成，处理了 %d 帧动画。"), AnimationResults.Num());
}
```

## 模块依赖

该插件的模块众多，依赖关系复杂。以下是使用者在开发依赖此插件的模块时，**最可能需要**依赖的独特模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供核心数据结构、工具和基础功能。 |
| `MetaHumanIdentity` | 提供基于照片或扫描创建 MetaHuman 身份资产的功能。 |
| `MetaHumanPerformance` | 提供用于管理面部表演动画资产的类和编辑器工具。 |
| `MetaHumanPipeline` | 定义处理流程节点，用于构建可配置的动画数据处理管线。 |
| `MetaHumanSequencer` | 提供与 Sequencer 的集成功能，用于导出和编辑动画序列。 |
| `MetaHumanCaptureData` | 处理来自各种来源（iPhone, 多相机）的原始捕获数据。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器扩展，是许多编辑器功能的依赖项。 |

**注意**：由于模块数量极多且相互关联，建议在项目的 `.Build.cs` 文件中添加对 `MetaHumanAnimator` 插件的依赖，然后按需引入特定子模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体跟踪时，过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存相关的问题。 |

*注：提供的git历史日期指向2026年，这可能与实际的UE 5.8分支时间线不符，但反映了在当前代码快照中该插件处于非常活跃的更新状态。*

### 维护评价

**维护状态：活跃维护**
- 从提供的git历史看，该插件在**极近的时间内**有频繁的提交（2026-05-20至22日），并且包含功能增加（身体跟踪集成、网格体导出）和重要bug修复（渲染瑕疵、缓存问题）。
- 作为 Epic Games 官方 MetaHuman 工具链的核心部分，该插件是其数字人战略的关键组件，预计将持续获得长期投入和支持。
- 该插件功能庞大且复杂，依赖众多，可能存在已知的性能边界问题或特定平台兼容性要求，使用前应查阅官方发布的最新兼容性说明。
- **强烈推荐使用**：如果你的工作流涉及 MetaHuman 的动画制作，这是官方提供的标准且功能最完整的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() （暂无直接链接，通常集成在 MetaHuman 文档中心）
- [测试用例]() （测试文件可能位于 `Engine/Tests/` 或插件内部，需具体查找）