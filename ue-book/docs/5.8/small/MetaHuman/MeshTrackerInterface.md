# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画器 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（模块化特性接口、核心功能库、编辑器工具、测试） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 约 2022-2023 年（确切日期未提供） |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方为 Unreal Engine 5 开发的 MetaHuman 角色动画工具包。它不是一个单一的动画播放器，而是一个完整的**面部捕捉（Face Capture）和动画生成（Animation Generation）管线**。该插件旨在解决从真实的演员表演（如 iPhone 深度摄像头视频）到高质量 MetaHuman 角色面部动画的转换问题。

核心流程包括：
1.  **数据导入与处理**：从 iPhone（使用 ARKit）或其他深度相机导入视频和深度数据。
2.  **面部追踪与解算**：追踪视频中的面部特征点，结合深度数据重建 3D 面部网格，并解算出对应的 MetaHuman 面部控制参数（Rig Controls）。
3.  **动画后处理**：对追踪到的动画数据进行平滑、优化和修正（如眼球注视、牙齿匹配等）。
4.  **输出动画**：将处理后的控制参数应用到 MetaHuman 角色上，生成可用于 Sequencer 或实时动画的面部动画。

`MeshTrackerInterface` 模块是该管线的**核心抽象层**，它定义了一组纯虚接口（C++ Interface），用于与底层的具体追踪和处理算法进行解耦。这使得 Epic 或第三方可以在不修改上层工具代码的情况下，更换或升级底层的面部追踪引擎。

## 使用场景

-   **数字人内容创作**：你正在为 MetaHuman 角色制作电影、广告或游戏过场动画，需要从真人表演中捕捉面部表情。
-   **虚拟主播/VTuber**：你需要实时或近实时地将主播的面部表情驱动到一个 MetaHuman 虚拟形象上。
-   **批量动画制作**：你拥有大量需要进行面部动画制作的资产或场景，可以利用 `MetaHumanBatchProcessor` 进行自动化处理。
-   **研究与自定义集成**：你是技术美术或程序员，希望将 MetaHuman Animator 的面部追踪能力集成到自己的 UE5 插件或自定义管线中。`MeshTrackerInterface` 提供了清晰的接口定义。

## 蓝图用法

此插件主要面向程序员和深度集成，大部分核心功能（特别是 `MeshTrackerInterface` 中定义的接口）在 C++ 层面使用。编辑器内工具和工作流通常通过 `MetaHumanToolkit`、`MetaHumanIdentityEditor` 等模块提供的编辑器窗口和资产浏览器进行操作。

### 核心接口（C++ 层面暴露）

虽然这些是 C++ 接口，但它们通过模块化特性系统（Modular Features）注册，可以在运行时查询和使用。

| 接口 | 说明 | 所在头文件 |
|---|---|---|
| `IMetaHumanFaceTrackerInterface` | 面部追踪器主接口，负责初始化、加载 DNA、设置相机、执行追踪并获取追踪状态（头部姿态、控制参数、网格顶点）。 | `MetaHumanFaceTrackerInterface.h` |
| `IDepthGeneratorInterface` | 深度图生成器接口，用于从立体相机对或图像生成深度图。 | `MetaHumanFaceTrackerInterface.h` |
| `IDepthMapDiagnosticsInterface` | 深度图诊断接口，用于计算和返回深度图质量的诊断信息。 | `MetaHumanFaceTrackerInterface.h` |
| `IOpticalFlowInterface` | 光流计算接口，用于计算两帧图像间的光流，常用于追踪辅助。 | `MetaHumanFaceTrackerInterface.h` |
| `IFaceTrackerPostProcessingInterface` | 面部追踪后处理接口，负责在原始追踪结果之上进行全局求解，如眼球注视修正、牙齿拟合等。 | `MetaHumanFaceTrackerInterface.h` |
| `IFaceTrackerPostProcessingFilter` | 面部追踪后处理滤波器接口，用于对动画数据进行离线滤波和平滑。 | `MetaHumanFaceTrackerInterface.h` |
| `IPredictiveSolverInterface` | 预测求解器训练接口，用于训练用于实时或交互式追踪的预测模型。 | `MetaHumanFaceTrackerInterface.h` |
| `IFaceTrackerNodeImplFactory` | 面部追踪器节点实现工厂接口，用于在流水线中创建上述各个接口的实例。 | `MetaHumanFaceTrackerInterface.h` |

## C++ 用法

### 头文件引入

```cpp
#include "MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h"
```

### 基本用法

`MeshTrackerInterface` 模块的核心是定义接口。典型的使用方式是**实现**这些接口或通过工厂接口**获取**实现。以下是一个简化的、概念性的示例，展示如何通过模块化特性获取追踪器工厂并创建追踪器实例。

**来源文件路径**: `Source/MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h`

```cpp
// 在你的模块或类中，获取面部追踪器工厂
void SetupFaceTracker()
{
    // 通过模块化特性系统查找已注册的工厂
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(IFaceTrackerNodeImplFactory::GetModularFeatureName()))
    {
        // 获取第一个可用的工厂（通常由具体的追踪算法模块注册）
        IFaceTrackerNodeImplFactory* Factory = &ModularFeatures.GetModularFeature<IFaceTrackerNodeImplFactory>(
            IFaceTrackerNodeImplFactory::GetModularFeatureName());

        // 使用工厂创建面部追踪器实例
        TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = Factory->CreateFaceTrackerImplementor();
        if (FaceTracker.IsValid())
        {
            // 初始化追踪器
            FString TemplateJson; // ...从配置加载
            FString ConfigJson;   // ...从配置加载
            FTrackerOpticalFlowConfiguration OptFlowConfig;
            FString PhysicalDeviceLUID = TEXT("0"); // GPU LUID

            if (FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, PhysicalDeviceLUID))
            {
                // 加载 MetaHuman DNA
                FString DNAFile = TEXT("path/to/your/metahuman.dna");
                if (FaceTracker->LoadDNA(DNAFile))
                {
                    // 追踪器已准备好，可以设置相机、输入数据并开始追踪
                    // ... 后续调用 SetCameras, SetInputData, Track 等
                }
            }
        }
    }
}
```

### 进阶用法

结合多个接口进行完整的工作流。例如，先使用 `IDepthGeneratorInterface` 生成深度图，然后将图像和深度图数据一起提供给 `IMetaHumanFaceTrackerInterface` 以提高追踪精度。

```cpp
// 伪代码：结合深度生成和面部追踪
void AdvancedTrackingPipeline(const TArray<FCameraCalibration>& Calibrations,
                               const TMap<FString, const unsigned char*>& Images)
{
    // 获取工厂
    IFaceTrackerNodeImplFactory* Factory = ...;

    // 1. 创建深度生成器并生成深度图
    TSharedPtr<IDepthGeneratorInterface> DepthGen = Factory->CreateDepthGeneratorImplementor();
    DepthGen->Init();
    DepthGen->SetCameras(Calibrations);
    DepthGen->SetStereoCameraPairs(/* 配置相机对 */);
    DepthGen->SetInputData(Images);

    int32 DepthWidth, DepthHeight;
    const float* DepthData = nullptr;
    // 从立体相机对获取深度图
    DepthGen->GetDepthMap(0, DepthWidth, DepthHeight, DepthData, ...);

    // 2. 创建面部追踪器
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = Factory->CreateFaceTrackerImplementor();
    FaceTracker->Init(...);
    FaceTracker->LoadDNA(...);
    FaceTracker->SetCameras(Calibrations);
    FaceTracker->SetStereoCameraPairs(...);

    // 3. 将图像和生成的深度图一起输入追踪器
    TMap<FString, const float*> DepthMaps;
    DepthMaps.Add(TEXT("MainCamera"), DepthData);
    FaceTracker->SetInputData(Images, /* Landmarks */, DepthMaps);

    // 4. 执行追踪
    FaceTracker->Track(0);

    // 5. 获取结果
    FTransform HeadPose;
    TArray<float> HeadPoseRaw;
    TMap<FString, float> Controls;
    TArray<float> FaceMeshVertices;
    // ... 其他输出
    FaceTracker->GetTrackingState(0, HeadPose, HeadPoseRaw, Controls, /* RawControls */, FaceMeshVertices, ...);
}
```

## Demo 示例

以下示例展示如何**实现** `IMetaHumanFaceTrackerInterface` 接口的一个最简骨架。实际实现会非常复杂，涉及底层的计算机视觉和机器学习算法。

```cpp
// MyCustomFaceTracker.h
#pragma once

#include "MetaHumanFaceTrackerInterface.h"

class FMyCustomFaceTracker : public IMetaHumanFaceTrackerInterface
{
public:
    virtual ~FMyCustomFaceTracker() = default;

    // IMetaHumanFaceTrackerInterface 接口实现
    virtual bool Init(const FString& InTemplateDescriptionJson, const FString& InConfigurationJson,
                      const FTrackerOpticalFlowConfiguration& InOptFlowConfig, const FString& InPhysicalDeviceLUID) override;

    virtual bool LoadDNA(const FString& InDNAFile) override;
    virtual bool LoadDNA(TSharedPtr<IDNAReader> InDNAReader) override;

    virtual bool SetCameras(const TArray<FCameraCalibration>& InCalibration) override;
    virtual bool SetCameraRanges(const TMap<FString, TPair<float, float>>& InCameraRanges) override;
    virtual bool ResetTrack(int32 InFrameStart, int32 InFrameEnd, const FTrackerOpticalFlowConfiguration& InOptFlowConfig) override;
    virtual bool SetStereoCameraPairs(const TArray<TPair<FString, FString>>& InStereoReconstructionPairs) override;
    virtual bool SetInputData(const TMap<FString, const unsigned char*>& InImageDataPerCamera,
                              const TMap<FString, const FFrameTrackingContourData*>& InLandmarksDataPerCamera,
                              const TMap<FString, const float*>& InDepthmapDataPerCamera = TMap<FString, const float*>(),
                              int32 InLevel = 0) override;
    virtual bool Track(int32 InFrameNumber, const TMap<FString, TPair<TPair<const float*, const float*>, TPair<TPair<const float*, const float*>, TPair<const float*, const float*>>>>& InFlowInfo = {},
                       bool bUseFastSolver = false, const FString& InDebuggingDataFolder = {}, bool bSkipPredictiveSolver = false, bool bInSkipPerVertexSolve = true) override;
    virtual bool GetTrackingState(int32 InFrameNumber, FTransform& OutHeadPose, TArray<float>& OutHeadPoseRaw,
                                  TMap<FString, float>& OutControls, TMap<FString, float>& OutRawControls, TArray<float>& OutFaceMeshVertices,
                                  TArray<float>& OutTeethMeshVertices, TArray<float>& OutLeftEyeMeshVertices, TArray<float>& OutRightEyeMeshVertices) override;
    // ... 实现其他纯虚函数 ...
};
```

```cpp
// MyCustomFaceTracker.cpp
#include "MyCustomFaceTracker.h"

bool FMyCustomFaceTracker::Init(const FString& InTemplateDescriptionJson, const FString& InConfigurationJson,
                                const FTrackerOpticalFlowConfiguration& InOptFlowConfig, const FString& InPhysicalDeviceLUID)
{
    // 初始化你的追踪器资源，解析配置JSON等
    UE_LOG(LogTemp, Log, TEXT("Custom Face Tracker Initialized"));
    return true;
}

bool FMyCustomFaceTracker::LoadDNA(const FString& InDNAFile)
{
    // 加载并解析DNA文件，建立骨骼和网格映射
    UE_LOG(LogTemp, Log, TEXT("Loaded DNA from: %s"), *InDNAFile);
    return true;
}

bool FMyCustomFaceTracker::LoadDNA(TSharedPtr<IDNAReader> InDNAReader)
{
    // 使用提供的DNA Reader
    return true;
}

// ... 实现其他函数 ...

bool FMyCustomFaceTracker::Track(int32 InFrameNumber, ...)
{
    // 核心追踪逻辑：
    // 1. 处理输入的图像、地标和深度图
    // 2. 运行面部特征点检测和3D重建
    // 3. 拟合到MetaHuman Rig
    // 4. 更新内部状态
    UE_LOG(LogTemp, Log, TEXT("Tracked frame: %d"), InFrameNumber);
    return true;
}

bool FMyCustomFaceTracker::GetTrackingState(int32 InFrameNumber, FTransform& OutHeadPose, ...)
{
    // 从内部状态中提取当前帧的结果
    OutHeadPose = CurrentHeadPose;
    OutControls = CurrentControls;
    OutFaceMeshVertices = CurrentFaceVertices;
    // ... 填充其他输出参数
    return true;
}
```

## 模块依赖

本模块 (`MeshTrackerInterface`) 本身是一个纯接口模块，依赖非常少。实际使用此插件时，你的模块需要依赖的模块取决于你集成的部分。以下是该插件中其他模块的**独特**依赖示例（常见依赖已省略）：

| 模块 | 用途 |
|---|---|
| `ControlRigDeveloper` | `MetaHumanIdentity` 模块需要，用于与 Control Rig 开发功能交互。 |
| `MetaHumanCoreTechLib` | `MetaHumanConfig` 模块需要，可能包含核心的数学或几何处理库。 |
| `MetaHumanCaptureDataEditor` | `MetaHumanIdentity` 和 `MetaHumanCaptureDataEditor` 模块内部需要，用于编辑器内的数据捕获资产处理。 |
| `MetaHumanSDKEditor` | `MetaHumanIdentity` 模块需要，用于编辑器集成。 |
| `SkeletalMeshUtilitiesCommon` | `MetaHumanIdentity` 模块需要，用于骨骼网格体工具函数。 |

**对于 `MeshTrackerInterface` 模块**：作为纯接口定义，它通常只需要 `Core` 和 `CoreUObject` 等基础模块，无特殊依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 身体追踪时过滤可视化对象，避免干扰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

-   **创建时间**：该插件是 UE5 的重要组成部分，创建于约 2022-2023 年，与 MetaHuman 角色系统的推广同步。
-   **近期活跃度**：**非常高**。最近一周（截至提供的日志）有多次提交，集中在功能增强（身体追踪集成、序列导出）和 bug 修复（渲染、缓存）。这表明 Epic Games 正在持续积极开发和维护此插件。
-   **状态**：**活跃维护中**。作为官方工具链，它受到 Epic 的持续支持，会随着 UE 版本更新和新功能需求而演进。
-   **推荐使用**：**强烈推荐**。如果你需要使用 MetaHuman 角色进行高质量的面部动画制作，这是官方的、功能完整且持续更新的首选方案。对于需要深度自定义追踪算法的研究者或开发者，`MeshTrackerInterface` 提供了一个清晰的集成点。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-animator-unreal-engine/) (UE5.0 链接，最新文档需在 Epic 官网查找)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)