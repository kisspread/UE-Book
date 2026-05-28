# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、动画数据） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-01-19 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的核心工具集，旨在将真实世界的人脸表演（来自多视角摄像机、深度摄像头或单视频）高保真地转换为驱动 MetaHuman 角色的面部动画。它不仅仅是一个面部追踪器，而是一个完整的管线，覆盖了从原始视频素材导入、面部特征点追踪、基于深度和光学流的立体重建、到最终动画数据（包括头部姿态、面部表情控制、眼球、牙齿等）的生成与优化。其核心是提供了一系列模块化、可配置的接口（如 `IMetaHumanFaceTrackerInterface`），这些接口由具体的“追踪器实现”提供，并通过工厂模式（`IFaceTrackerNodeImplFactory`）创建，使得底层算法可以灵活替换或升级。

## 使用场景

-   **电影与视觉特效制作**：将演员的现场表演录制，转换为高质量的 MetaHuman 角色动画。
-   **虚拟主播与实时直播**：利用摄像头捕捉主播面部，实时驱动虚拟形象。
-   **游戏开发**：为游戏内的过场动画或关键角色制作基于真人表演的面部动画。
-   **内容创作与原型设计**：快速验证角色动画创意，无需复杂的手动关键帧制作。
-   **研究与开发**：基于其开放的接口，集成或开发新的面部捕捉与动画算法。

## 蓝图用法

当前分析的 `MeshTrackerInterface` 模块主要提供了 C++ 级别的抽象接口，用于定义面部追踪器、深度生成器、光学流计算器等组件的合约。这些接口本身不直接暴露蓝图节点。实际的蓝图功能（如 `MetaHumanToolkit` 模块提供的编辑器工具和资产处理器）由其他模块提供。

## C++ 用法

### 头文件引入

```cpp
#include "MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h"
```

### 基本用法

`MeshTrackerInterface` 定义了一组核心接口，用于与底层的追踪和深度处理算法交互。以下示例展示了如何使用 `IMetaHumanFaceTrackerInterface` 的基本工作流。

**示例：初始化并执行一次面部追踪** (概念代码)
```cpp
// 假设你已经通过工厂获取了 IMetaHumanFaceTrackerInterface 的实现
TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = /* ... */;

// 1. 初始化追踪器
FString TemplateJson = /* 加载 template_description.json 内容 */;
FString ConfigJson = /* 加载 configuration.json 内容 */;
FTrackerOpticalFlowConfiguration OpticalFlowConfig = /* 初始化光流配置 */;
FString DeviceLUID = /* 获取GPU设备LUID，可选 */;

if (FaceTracker->Init(TemplateJson, ConfigJson, OpticalFlowConfig, DeviceLUID))
{
    // 2. 加载目标角色的DNA数据（用于驱动面部网格）
    FString DNARigPath = TEXT("/Game/Characters/MyMetaHuman/DNA/MyMetaHuman.dna");
    if (FaceTracker->LoadDNA(DNARigPath))
    {
        // 3. 设置相机校准数据
        TArray<FCameraCalibration> CameraCalibrations = /* 从拍摄数据中获取 */;
        FaceTracker->SetCameras(CameraCalibrations);
        
        // 4. 重置并设置新的追踪序列
        int32 FrameStart = 0;
        int32 FrameEnd = 100;
        FaceTracker->ResetTrack(FrameStart, FrameEnd, OpticalFlowConfig);
        
        // 5. 循环处理每一帧
        for (int32 FrameIndex = FrameStart; FrameIndex < FrameEnd; ++FrameIndex)
        {
            // 准备当前帧的图像和特征点数据
            TMap<FString, const unsigned char*> ImageDataPerCamera = /* ... */;
            TMap<FString, const FFrameTrackingContourData*> LandmarksPerCamera = /* ... */;
            
            // 设置输入数据并执行追踪
            if (FaceTracker->SetInputData(ImageDataPerCamera, LandmarksPerCamera))
            {
                if (FaceTracker->Track(FrameIndex))
                {
                    // 6. 获取追踪结果
                    FTransform HeadPose;
                    TArray<float> HeadPoseRaw;
                    TMap<FString, float> Controls, RawControls;
                    TArray<float> FaceVertices, TeethVertices, LeftEyeVertices, RightEyeVertices;
                    
                    if (FaceTracker->GetTrackingState(FrameIndex, HeadPose, HeadPoseRaw, 
                        Controls, RawControls, FaceVertices, TeethVertices, 
                        LeftEyeVertices, RightEyeVertices))
                    {
                        // 使用 Controls 驱动 MetaHuman 面部动画蓝图
                        // 使用 HeadPose 设置头部变换
                        // 使用 Mesh Vertices 更新网格形状
                    }
                }
            }
        }
    }
}
```

**来源**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h`

### 进阶用法

插件的后期处理和预测求解器接口 (`IFaceTrackerPostProcessingInterface`, `IPredictiveSolverInterface`) 提供了更高级的功能。

**示例：训练和应用预测求解器** (概念代码)
```cpp
// IPredictiveSolverInterface 用于训练一个“预测求解器”
// 该求解器可以根据少量面部标记点预测更完整的面部动画状态。
// 获取方式与 FaceTracker 类似，通过 ModularFeature 系统。
TSharedPtr<IPredictiveSolverInterface> Solver = FModuleManager::Get().LoadModulePtr<IMeshTrackerInterfaceModule>(TEXT("MeshTrackerInterface"))->GetPredictiveSolver();

if (Solver)
{
    FPredictiveSolversTaskConfig SolverConfig;
    SolverConfig.TrainingDataPath = TEXT("/Path/To/TrainingData");
    // ... 配置其他训练参数
    
    FPredictiveSolversResult Result;
    std::atomic<bool> bIsDone(false);
    std::atomic<float> Progress(0.0f);
    std::atomic<bool> bCancelled(false);
    
    Solver->TrainPredictiveSolver(bIsDone, Progress,
        [](float InProgress) { /* 更新进度UI */ },
        bCancelled, SolverConfig, Result);
        
    // 训练完成后，可以将 Result 保存或用于 IFaceTrackerPostProcessingInterface
}

// IFaceTrackerPostProcessingInterface 用于对原始追踪数据进行全局优化（如眼球、牙齿）
// 它通常在主追踪循环之后，对整个序列进行离线处理。
// 假设已有 FaceTrackerPostProcessing 实现。
TSharedPtr<IFaceTrackerPostProcessingInterface> PostProcessor = /* ... */;
PostProcessor->Init(TemplateJson, ConfigJson);
PostProcessor->LoadDNA(DNARigPath, SolverDefinitionsJson);
PostProcessor->SetCameras(CameraCalibrations, MainCameraName);
PostProcessor->SetGlobalTeethPredictiveSolver(TrainedTeethSolverBuffer);

// 执行离线全局求解
TArray<FFrameAnimationData> FrameDatas = /* 从主追踪循环收集的动画数据 */;
TArray<FFrameTrackingContourData> TrackingData = /* 从主追踪循环收集的原始特征点数据 */;
PostProcessor->OfflineSolvePrepare(0, FrameDatas.Num(), TrackingData, FrameDatas, DebugFolder);

// 然后可以逐帧应用最终结果
for (int32 Frame = 0; Frame < FrameDatas.Num(); ++Frame)
{
    PostProcessor->OfflineSolveProcessFrame(Frame, 0, FrameDatas.Num(), FrameDatas, UpdatedFrames);
}
```

**来源**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h`

## Demo 示例

一个最小化的 C++ 示例，演示如何声明并调用一个 MetaHuman 面部追踪器工厂。

**MyMetaHumanAnimatorComponent.h**
```cpp
#pragma once

#include "Components/ActorComponent.h"
#include "MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h"
#include "MyMetaHumanAnimatorComponent.generated.h"

UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMetaHumanAnimatorComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UMyMetaHumanAnimatorComponent();
	virtual void BeginPlay() override;

	/** 用于初始化和测试追踪器的蓝图函数 */
	UFUNCTION(BlueprintCallable, Category = "MetaHuman|Animator")
	bool TestFaceTrackerInitialization();

private:
	/** 通过 ModularFeature 系统获取的追踪器工厂 */
	TSharedPtr<IFaceTrackerNodeImplFactory> FaceTrackerFactory;
	
	/** 由工厂创建的追踪器实例 */
	TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker;
};
```

**MyMetaHumanAnimatorComponent.cpp**
```cpp
#include "MyMetaHumanAnimatorComponent.h"
#include "Features/IModularFeatures.h"

UMyMetaHumanAnimatorComponent::UMyMetaHumanAnimatorComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UMyMetaHumanAnimatorComponent::BeginPlay()
{
	Super::BeginPlay();

	// 从 Modular Features 系统中获取可用的面部追踪器工厂
	// 实际的工厂实现由底层的 MeshTracker 插件提供（例如基于OpenCV或专有算法）
	TArray<IFaceTrackerNodeImplFactory*> Factories = IModularFeatures::Get().GetModularFeatureImplementations<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());
	if (Factories.Num() > 0)
	{
		FaceTrackerFactory = Factories[0];
	}
}

bool UMyMetaHumanAnimatorComponent::TestFaceTrackerInitialization()
{
	if (!FaceTrackerFactory.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("No face tracker factory found."));
		return false;
	}

	// 使用工厂创建追踪器实例
	FaceTracker = FaceTrackerFactory->CreateFaceTrackerImplementor();
	if (!FaceTracker.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("Failed to create face tracker implementor."));
		return false;
	}

	// 尝试初始化（使用最小的、虚拟的配置）
	FString DummyJson = TEXT("{}");
	FTrackerOpticalFlowConfiguration DummyConfig;
	bool bSuccess = FaceTracker->Init(DummyJson, DummyJson, DummyConfig, TEXT(""));
	
	UE_LOG(LogTemp, Log, TEXT("Face tracker initialization test %s."), bSuccess ? TEXT("succeeded") : TEXT("failed"));
	return bSuccess;
}
```

## 模块依赖

`MetaHumanAnimator` 插件本身包含大量相互依赖的模块。对于使用此插件的外部模块，依赖关系主要通过以下独特模块体现。标准依赖如 `Core`, `Engine`, `Slate` 等已省略。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层算法和数据结构。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器工具和资产处理器。 |
| `ControlRigDeveloper` | 用于与 Control Rig 集成，驱动面部骨骼和动画。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格公共工具，用于网格变形和更新。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用全身追踪时，禁用关卡序列导出功能以避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 模型上的渲染瑕疵 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 进行全身追踪时，过滤掉用于可视化的辅助对象 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已存在的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器相关的缓存问题 |

### 维护评价

MetaHuman Animator 是一个仍在**积极维护**的核心插件。从提交历史看，最近的更新（2026年5月）集中在功能优化（如全身追踪时的导出逻辑）、渲染问题修复和用户工作流改进（为现有网格导出动画）。考虑到 MetaHuman 技术是 Epic Games 在数字人类领域的战略重点，该插件预计会持续获得长期支持和功能更新。插件未标记为实验性或Beta，适用于生产环境使用，但其庞大的模块化结构和复杂的依赖意味着使用时需仔细配置。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/using-metahuman-animator-in-unreal-engine/) (链接基于一般知识推断，.uplugin 中 DocsURL 为空)
-   测试用例路径未在本次分析中提供，通常位于插件目录的 `Tests` 子文件夹或 `Engine/Tests` 下。