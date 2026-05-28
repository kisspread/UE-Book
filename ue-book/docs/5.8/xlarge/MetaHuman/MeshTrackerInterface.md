# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 超人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（元数据资产、配置文件、可能包含蓝图资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | unknown |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的一整套用于 MetaHuman 角色动画制作的工具套件。它解决的核心问题是：**如何将真实的演员表演（视频、深度数据）高效、准确地转化为高质量的 MetaHuman 面部动画数据**。该插件不仅仅是一个单一功能，而是一个包含数据采集、处理、求解、编辑的完整工作流管线。它通过提供标准化的接口（如 `IMetaHumanFaceTrackerInterface`）和模块化的处理器（如面部追踪器、动画求解器、深度生成器），使得用户可以从多种输入源（如 iPhone 深度相机、多摄像头阵列）捕获表演，并驱动数字孪生体的面部动画。其存在是为了在虚幻引擎内闭环完成从表演捕捉到最终动画资产的全部生产流程。

## 使用场景

- **从演员表演生成面部动画**：你使用 iPhone 的原深感摄像头或其他专业设备拍摄了一段演员的面部表演视频，可以使用此插件将视频转化为控制 MetaHuman 角色的高质量动画序列。
- **批量处理动画资产**：你积累了大量面部表演数据，需要自动化地将其转换为可用于游戏或影视的动画资产，可以使用其批处理模块（`MetaHumanBatchProcessor`）来提高效率。
- **实时或离线面部动捕**：你需要为虚拟制片或游戏内实时演出驱动 MetaHuman 角色的面部，或者进行高质量的离线动画生成，可以使用其内置的面部追踪与求解管线。
- **深度数据优化动画**：你不仅有视频，还有深度图数据，希望获得更精确的面部几何形变动画，可以使用其深度生成与融合模块来提升动画质量。
- **集成到自定义管线**：你需要将 MetaHuman 的动画生成能力嵌入到自己工作室的制作管线中，可以利用其提供的模块化接口（`Modular Feature`）进行深度集成。

## 蓝图用法

根据提供的 `MeshTrackerInterface` 模块源码，该模块主要提供纯 C++ 接口，未直接暴露 `BlueprintCallable` 函数。其核心功能通过 `IModularFeature` 接口在运行时被注册和访问。具体的蓝图节点（例如用于驱动动画、管理资产）很可能位于其他上层模块（如 `MetaHumanToolkit`, `MetaHumanPerformance`）中。本模块可视为引擎底层技术接口层。

## C++ 用法

### 头文件引入

```cpp
// 引入面部追踪器接口头文件
#include "MetaHumanFaceTrackerInterface.h"
```

### 基本用法

该模块的核心是一系列 `IModularFeature` 接口，用于在运行时查找和调用具体的动画处理实现。以下是获取和使用面部追踪器接口的示例逻辑。

```cpp
// 假设在某个管理类中
#include "MetaHumanFaceTrackerInterface.h"
#include "Features/IModularFeatures.h"

void UMyAnimManager::InitializeFaceTracker()
{
    // 1. 通过 Modular Features 查找面部追踪器工厂
    TArray<IFaceTrackerNodeImplFactory*> Factories = IModularFeatures::Get().GetModularFeatureImplementations<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());
    if (Factories.Num() > 0)
    {
        // 2. 从工厂创建具体实现
        TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = Factories[0]->CreateFaceTrackerImplementor();

        if (FaceTracker.IsValid())
        {
            // 3. 初始化追踪器（需要配置JSON字符串和光学流配置）
            FString TemplateJson = TEXT("{ ... }"); // 从配置文件或资产加载
            FString ConfigJson = TEXT("{ ... }");
            FTrackerOpticalFlowConfiguration OptFlowConfig;
            // ... 初始化配置
            bool bSuccess = FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, LUID);

            // 4. 加载DNA资产（定义了MetaHuman的面部拓扑和骨骼）
            TSharedPtr<IDNAReader> DNAResolver = ...; // 获取DNA读取器
            bSuccess = FaceTracker->LoadDNA(DNAResolver);

            // 5. 设置相机（用于立体视觉或深度估计）
            TArray<FCameraCalibration> Calibrations;
            // ... 填充相机标定数据
            bSuccess = FaceTracker->SetCameras(Calibrations);

            // 6. 准备追踪并获取结果
            int32 FrameStart = 0, FrameEnd = 100;
            FaceTracker->ResetTrack(FrameStart, FrameEnd, OptFlowConfig);
            // ... 在循环中为每帧调用 SetInputData 和 Track
            // ... 调用 GetTrackingState 获取头部姿态和面部控制参数
        }
    }
}
```

### 进阶用法

结合后处理接口进行更精细的动画求解。

```cpp
// 假设已获取到 FaceTracker (IMetaHumanFaceTrackerInterface) 和后处理器 (IFaceTrackerPostProcessingInterface)
void UMyAnimManager::RunAdvancedSolve(int32 FrameStart, int32 NumFrames, const TArray<FFrameTrackingContourData>& TrackingData)
{
    // 1. 获取后处理接口（同样通过Modular Features）
    TSharedPtr<IFaceTrackerPostProcessingInterface> PostProcessor = ...;

    // 2. 初始化并加载DNA（注意参数不同，需要SolverDefinitionsJson）
    PostProcessor->Init(TemplateJson, ConfigJson);
    PostProcessor->LoadDNA(DNAResolver, SolverDefinitionsJson);
    PostProcessor->SetGlobalTeethPredictiveSolver(GlobalTeethSolverBuffer);

    // 3. 执行离线全局求解（如眼球注视校正、牙齿拟合）
    TArray<FFrameAnimationData> FrameAnimationDataArray; // 包含每帧的动画状态
    // ... 填充 FrameAnimationDataArray
    PostProcessor->OfflineSolvePrepare(FrameStart, NumFrames, TrackingData, FrameAnimationDataArray);

    // 4. 对每帧进行最终求解
    for (int32 Frame = FrameStart; Frame < FrameStart + NumFrames; ++Frame)
    {
        TArray<int32> UpdatedFrames;
        PostProcessor->OfflineSolveProcessFrame(Frame, FrameStart, NumFrames, FrameAnimationDataArray, UpdatedFrames);
        // ... 处理被更新的帧
    }

    // 5. 可选：应用后处理滤波
    TSharedPtr<IFaceTrackerPostProcessingFilter> Filter = ...;
    Filter->Init(TemplateJson, ConfigJson);
    Filter->LoadDNA(DNAResolver, SolverDefinitionsJson);
    Filter->OfflineFilter(FrameStart, NumFrames, FrameAnimationDataArray);
}
```

## Demo 示例

由于 `MeshTrackerInterface` 是接口定义模块，完整的最小工作示例需要涉及其他模块（如 `MetaHumanCore`）提供数据和驱动逻辑。以下是一个高度简化的 C++ 概念示例，展示如何组合使用这些接口。

```cpp
// MyMetaHumanAnimatorComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MetaHumanFaceTrackerInterface.h" // 引入接口
#include "MyMetaHumanAnimatorComponent.generated.h"

UCLASS(ClassGroup=(MetaHuman), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyMetaHumanAnimatorComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 在编辑器中或初始化时配置的DNA资产路径
    UPROPERTY(EditAnywhere, Category = "Animation")
    FString DNAFilePath;

    // 在编辑器中或初始化时配置的配置文件路径
    UPROPERTY(EditAnywhere, Category = "Animation")
    FString ConfigFilePath;

protected:
    virtual void BeginPlay() override;

public:
    // 蓝图可调用的函数：从图像数据驱动动画
    UFUNCTION(BlueprintCallable, Category = "Animation")
    bool ProcessFrame(const TMap<FString, const unsigned char*>& ImageData);

private:
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker;
    bool bIsInitialized = false;
};
```

```cpp
// MyMetaHumanAnimatorComponent.cpp
#include "MyMetaHumanAnimatorComponent.h"
#include "Features/IModularFeatures.h"
#include "Misc/FileHelper.h"
#include "Interfaces/IPluginManager.h"

void UMyMetaHumanAnimatorComponent::BeginPlay()
{
    Super::BeginPlay();

    // 1. 查找并创建面部追踪器
    TArray<IFaceTrackerNodeImplFactory*> Factories = IModularFeatures::Get().GetModularFeatureImplementations<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());
    if (Factories.Num() == 0)
    {
        UE_LOG(LogTemp, Error, TEXT("MetaHuman FaceTrackerFactory not found!"));
        return;
    }
    FaceTracker = Factories[0]->CreateFaceTrackerImplementor();

    // 2. 加载配置
    FString TemplateJson, ConfigJson;
    // 此处简化，实际应从文件或资产加载
    if (!FFileHelper::LoadFileToString(TemplateJson, *ConfigFilePath) ||
        !FFileHelper::LoadFileToString(ConfigJson, *ConfigFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load config files."));
        return;
    }

    // 3. 初始化追踪器
    FTrackerOpticalFlowConfiguration OptFlowConfig; // 需要正确初始化
    bool bSuccess = FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, TEXT(""));
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("FaceTracker Init failed."));
        return;
    }

    // 4. 加载DNA
    bSuccess = FaceTracker->LoadDNA(DNAFilePath);
    if (!bSuccess)
    {
        UE_LOG(LogTemp, Error, TEXT("LoadDNA failed for %s."), *DNAFilePath);
        return;
    }

    bIsInitialized = true;
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Animator Component initialized."));
}

bool UMyMetaHumanAnimatorComponent::ProcessFrame(const TMap<FString, const unsigned char*>& ImageData)
{
    if (!bIsInitialized || !FaceTracker.IsValid())
    {
        return false;
    }

    // 5. 为当前帧设置输入数据并执行追踪
    TMap<FString, const FFrameTrackingContourData*> LandmarksData; // 此处需由其他模块（如人脸轮廓追踪器）提供
    // LandmarksData = ... 获取当前帧的地标数据

    bool bSuccess = FaceTracker->SetInputData(ImageData, LandmarksData);
    if (!bSuccess) return false;

    int32 FrameNumber = 0; // 需要根据实际情况管理帧号
    bSuccess = FaceTracker->Track(FrameNumber);
    if (!bSuccess) return false;

    // 6. 获取结果
    FTransform HeadPose;
    TArray<float> HeadPoseRaw, FaceMeshVertices, TeethMeshVertices, LeftEyeMeshVertices, RightEyeMeshVertices;
    TMap<FString, float> Controls, RawControls;
    bSuccess = FaceTracker->GetTrackingState(FrameNumber, HeadPose, HeadPoseRaw, Controls, RawControls, FaceMeshVertices, TeethMeshVertices, LeftEyeMeshVertices, RightEyeMeshVertices);

    if (bSuccess)
    {
        // 7. 应用结果（例如，更新角色骨骼或蒙皮网格体）
        // AActor* Owner = GetOwner();
        // ... 使用 HeadPose, Controls 等驱动角色
        UE_LOG(LogTemp, Log, TEXT("Frame %d processed. Head pose: %s"), FrameNumber, *HeadPose.ToString());
    }

    return bSuccess;
}
```

## 模块依赖

`MeshTrackerInterface` 模块是纯接口定义，其 `Build.cs` 依赖项较少。使用者的主要依赖来自于需要调用这些接口的具体功能模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 核心数据结构、资产类型（如 DNA 资产）和基础管理功能 |
| `MetaHumanFaceContourTracker` | 提供人脸轮廓（地标点）的检测和追踪功能 |
| `MetaHumanFaceFittingSolver` | 提供将追踪数据拟合到 MetaHuman 模型上的求解器 |
| `MetaHumanDepthGenerator` | 提供基于立体视觉或深度相机的深度图生成功能 |
| `MetaHumanPerformance` | 提供管理、播放和编辑最终动画性能（Performance）的功能 |
| `MetaHumanToolkit` | 提供高级的蓝图和编辑器工具集，用于整合和展示上述功能 |
| `MetaHumanPipeline` | 提供构建和执行数据处理管线的基础设施 |
| `MetaHumanCaptureUtils` | 提供与数据采集相关的通用工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 为修复冲突，在身体追踪启用时禁用关卡序列导出功能 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪模式下过滤可视化调试对象，保持界面整洁 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已存在的网格体导出动画序列 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer（序列器）相关的缓存问题 |

### 维护评价

MetaHuman Animator 插件处于**积极维护**状态。尽管其具体创建时间未知，但它是 MetaHuman 技术栈的核心组成部分，随着该技术的普及而持续发展。从近期（2026年5月）的提交记录来看，Epic Games 的开发团队仍在频繁地进行功能迭代（如支持已存在网格体的动画导出）和缺陷修复（渲染瑕疵、缓存问题）。这表明该插件是 Epic 官方支持的重点项目之一。对于需要从真实表演创建 MetaHuman 动画的用户，这是一个**推荐使用**的官方工具。需要注意的是，由于其功能复杂且涉及多个底层模块，完整的集成和配置可能需要一定的学习成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/meta-humans-in-unreal-engine/) （注：为 MetaHuman 整体文档入口）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) （例如，模块名包含 “Test” 的源码）