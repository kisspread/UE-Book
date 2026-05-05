# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、配置、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画工具包。它解决的核心问题是：**如何将真实演员的面部表演（通过视频或深度数据捕捉）高效、准确地驱动到高保真的 MetaHuman 数字角色上**。

该插件提供了一个完整的端到端工作流程，涵盖了从原始数据导入、面部特征追踪、动画求解到最终角色适配的全过程。它不仅仅是一个简单的追踪器，而是一个包含数据管理、多算法求解器、编辑器工具和批处理能力的综合性动画制作系统。其存在是为了让游戏开发者、影视制作者和虚拟制片团队能够以专业级的质量，将表演数据转化为可用于实时引擎的动画资产。

## 使用场景

- **游戏过场动画制作**：你正在开发一款 3A 级游戏，需要为游戏中的 MetaHuman 角色制作大量高质量的面部动画过场。使用 MetaHuman Animator，你可以从演员在绿幕前的表演视频中提取动画数据，直接驱动游戏内的角色。
- **虚拟制片与实时直播**：在虚拟制片（Virtual Production）环境中，你需要将现场演员的实时面部表演同步到 LED 墙上的 MetaHuman 角色上。该插件的实时追踪和求解能力可以满足这一需求。
- **从 iPhone 深度数据创建动画**：你使用 iPhone 的深度摄像头（LiDAR）录制了演员的面部表演。MetaHuman Animator 可以处理这些深度数据，生成高质量的面部动画，无需复杂的多相机设置。
- **批量处理动画资产**：你的项目有数百个来自不同来源（视频、深度数据）的表演片段需要处理。可以使用 `MetaHumanBatchProcessor` 模块进行自动化批处理，提高生产效率。
- **从音频生成面部动画**：你只有角色的对话音频文件，没有视频。`MetaHumanSpeech2Face` 模块可以基于音频预测出合理的面部动画，用于快速原型制作或补充动画。

## 蓝图用法

由于 MetaHuman Animator 主要是一个底层数据处理和编辑器工具集，其核心功能（如面部追踪、求解）通常通过 C++ 接口或编辑器 UI 调用。然而，一些高层功能和资产管理暴露了蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaHuman Performance` | 从捕获数据资产创建一个新的 MetaHuman Performance（表演）资产。 | `UMetaHumanPerformanceFactoryNew` |
| `Import Footage` | 将视频或图像序列导入为 MetaHuman 捕获数据资产。 | `UMetaHumanFootageIngestFactory` |
| `Start Capture` | 启动来自指定捕获源（如 iPhone）的实时数据流。 | `UMetaHumanCaptureSource` |
| `Apply Animation to MetaHuman` | 将一个 MetaHuman Performance 资产中包含的动画数据应用到目标 MetaHuman 角色的骨骼网格体上。 | `UMetaHumanPerformance` |
| `Get Tracking Data` | 从 Performance 资产中提取原始的追踪数据（如控制值、顶点位置）。 | `UMetaHumanPerformance` |

### 使用示例（蓝图描述）

1.  **从视频创建动画**：
    - 在内容浏览器中右键，选择 `Import` -> `MetaHuman Footage`。
    - 选择一个视频文件，导入后生成一个 `MetaHumanCaptureData` 资产。
    - 右键该资产，选择 `Create MetaHuman Performance`。
    - 在打开的 MetaHuman Animator 编辑器窗口中，配置追踪参数并运行求解。
    - 求解完成后，将生成的 `MetaHumanPerformance` 资产拖拽到场景中的 MetaHuman 角色上，或使用 `Apply Animation to MetaHuman` 节点。

2.  **实时驱动角色**：
    - 使用 `Start Capture` 节点连接 iPhone 或其他捕获设备。
    - 将捕获源的输出连接到 MetaHuman 角色的动画蓝图中，实时更新面部动画。

## C++ 用法

核心的面部追踪和求解功能通过 `IMetaHumanFaceTrackerInterface` 等接口暴露，这些接口是纯虚类，需要由具体的追踪器实现（如基于 PCA Rig 的追踪器）。

### 头文件引入

```cpp
#include "MetaHumanFaceTrackerInterface.h"
#include "MetaHumanCaptureUtils.h"
#include "MetaHumanPerformance.h"
```

### 基本用法

以下示例展示了如何使用面部追踪接口的基本流程。这通常在自定义的动画处理管线或编辑器工具中使用。

```cpp
// 来源：基于 MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h 推断的用法

// 1. 获取或创建一个面部追踪器实例（通常通过模块或工厂获取）
TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = /* ... 获取追踪器实例 ... */;

// 2. 初始化追踪器
FString TemplateJson = /* ... 加载模板描述 JSON ... */;
FString ConfigJson = /* ... 加载配置 JSON ... */;
FTrackerOpticalFlowConfiguration OptFlowConfig;
bool bSuccess = FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, TEXT(""));

// 3. 加载角色的 DNA 数据（定义了角色的面部拓扑和变形目标）
UDNAAsset* DNAAsset = /* ... 加载或获取 DNA 资产 ... */;
FaceTracker->LoadDNA(DNAAsset);

// 4. 设置相机校准数据（对于多相机捕捉）
TArray<FCameraCalibration> Calibrations;
// ... 从文件或资产加载校准数据 ...
FaceTracker->SetCameras(Calibrations);

// 5. 重置并开始一个新的追踪序列
int32 FrameStart = 0;
int32 FrameEnd = 100; // 假设序列有100帧
FaceTracker->ResetTrack(FrameStart, FrameEnd, OptFlowConfig);

// 6. 逐帧处理数据
for (int32 Frame = FrameStart; Frame < FrameEnd; ++Frame)
{
    // 准备当前帧的图像数据和地标数据
    TMap<FString, const unsigned char*> ImageDataPerCamera;
    TMap<FString, const FFrameTrackingContourData*> LandmarksPerCamera;
    // ... 填充数据 ...

    // 设置输入数据并执行追踪
    FaceTracker->SetInputData(ImageDataPerCamera, LandmarksPerCamera);
    FaceTracker->Track(Frame);

    // 7. 获取追踪结果
    FTransform HeadPose;
    TArray<float> HeadPoseRaw;
    TMap<FString, float> Controls;
    TMap<FString, float> RawControls;
    TArray<float> FaceMeshVertices;
    // ... 其他输出数组 ...
    FaceTracker->GetTrackingState(Frame, HeadPose, HeadPoseRaw, Controls, RawControls, FaceMeshVertices, /* ... */);

    // 8. 使用结果（例如，应用到骨骼、保存到动画曲线）
    // ...
}
```

### 进阶用法

结合 `MetaHumanPipeline` 模块，可以构建更复杂的处理流程。以下示例展示了如何使用 Pipeline 来自动化从数据导入到动画生成的整个过程。

```cpp
// 来源：基于 MetaHumanPipeline 模块推断的用法

#include "MetaHumanPipeline.h"

// 1. 创建或加载一个预定义的处理管线
UMetaHumanPipeline* Pipeline = NewObject<UMetaHumanPipeline>();
// 或者从资产加载: UMetaHumanPipeline* Pipeline = LoadObject<UMetaHumanPipeline>(nullptr, TEXT("/Path/To/MyPipeline"));

// 2. 配置管线的输入（例如，指向一个捕获数据资产）
Pipeline->SetInput(TEXT("CaptureData"), MyCaptureDataAsset);

// 3. 执行管线（这会自动调用追踪、求解等步骤）
bool bPipelineSuccess = Pipeline->Execute();

// 4. 从管线输出中获取结果
if (bPipelineSuccess)
{
    UMetaHumanPerformance* ResultPerformance = Cast<UMetaHumanPerformance>(Pipeline->GetOutput(TEXT("Performance")));
    if (ResultPerformance)
    {
        // 使用生成的 Performance 资产
        // ...
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何设置一个基本的面部追踪任务。

```cpp
// MetaHumanAnimatorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanFaceTrackerInterface.h"
#include "MetaHumanAnimatorDemo.generated.h"

UCLASS()
class MYPROJECT_API AMetaHumanAnimatorDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanAnimatorDemo();

protected:
    virtual void BeginPlay() override;

private:
    TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker;

    void RunBasicTrackingDemo();
};
```

```cpp
// MetaHumanAnimatorDemo.cpp
#include "MetaHumanAnimatorDemo.h"
#include "MetaHumanFaceTrackerInterface.h"
#include "DNAAsset.h" // 假设的 DNA 资产头文件

AMetaHumanAnimatorDemo::AMetaHumanAnimatorDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanAnimatorDemo::BeginPlay()
{
    Super::BeginPlay();
    RunBasicTrackingDemo();
}

void AMetaHumanAnimatorDemo::RunBasicTrackingDemo()
{
    // 注意：在实际项目中，追踪器实例通常通过模块接口获取，此处为示意。
    // 例如：IMetaHumanCaptureModule& CaptureModule = FModuleManager::Get().LoadModuleChecked<IMetaHumanCaptureModule>(TEXT("MetaHumanCaptureSource"));
    // FaceTracker = CaptureModule.CreateFaceTracker();

    // 1. 初始化
    FString TemplateJson = TEXT("{\"template\": \"basic\"}");
    FString ConfigJson = TEXT("{\"solver\": \"default\"}");
    FTrackerOpticalFlowConfiguration OptFlowConfig;
    if (FaceTracker.IsValid() && FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, TEXT("")))
    {
        UE_LOG(LogTemp, Log, TEXT("FaceTracker initialized successfully."));

        // 2. 加载 DNA (需要有效的 DNA 资产路径)
        UDNAAsset* DNA = LoadObject<UDNAAsset>(nullptr, TEXT("/Game/MetaHumans/Common/DefaultDNA"));
        if (DNA && FaceTracker->LoadDNA(DNA))
        {
            UE_LOG(LogTemp, Log, TEXT("DNA loaded."));

            // 3. 设置相机 (简化示例，通常需要真实的校准数据)
            TArray<FCameraCalibration> Calibrations;
            // ... 填充校准数据 ...
            if (FaceTracker->SetCameras(Calibrations))
            {
                // 4. 重置追踪
                if (FaceTracker->ResetTrack(0, 10, OptFlowConfig))
                {
                    UE_LOG(LogTemp, Log, TEXT("Tracking sequence reset. Ready to process frames."));
                    // 在此处可以添加逐帧处理的逻辑，如基本用法所示。
                }
            }
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize FaceTracker."));
    }
}
```

## 模块依赖

该插件依赖于多个 Epic 内部和第三方库来实现其高级功能。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层的数学、几何和求解算法。 |
| `ControlRig` / `ControlRigDeveloper` | 用于将追踪结果映射到 MetaHuman 角色的 Control Rig 系统。 |
| `MediaUtils` / `MediaAssets` | 处理视频和图像序列的导入与播放。 |
| `ImageWriteQueue` | 用于将处理后的图像（如深度图）异步写入磁盘。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体相关的通用工具函数。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，用于资产管理和集成。 |

## 维护状态

### 近期更新

```
- 2024-02-02 717bd7019d0f [Backout] - CL41136011 [FYI] jon.cook #rnx Original CL Desc ----------------------------------------------------------------- Tech debt relating to MetaHuman plugin move #rb Jane.Haslam
- 2024-02-02 1fcc80df7f4a Tech debt relating to MetaHuman plugin move #rb Jane.Haslam
- 2024-02-02 2a7f797f2bdd [MH-Plugin] Migrate the animator plugin from restricted #rb Jane.Haslam [REVIEW] thanasis.vogiannou
```

### 维护评价

MetaHuman Animator 是一个**非常新且处于活跃维护状态**的插件。

- **创建时间**：2024年2月，非常年轻。
- **近期更新**：最近的提交（2024-02-02）显示插件刚刚从 Epic 的内部“restricted”仓库迁移到公开的引擎仓库中，并进行了一些技术债务清理。这表明该插件正在经历一个重要的公开化阶段，后续很可能会有持续的功能更新和优化。
- **活跃度**：作为 MetaHuman 生态系统的核心组件，它由 Epic Games 官方团队维护，预计会保持高频率的更新，以支持新功能、修复问题并适配引擎新版本。
- **已知限制**：由于其复杂性，对硬件（特别是 GPU）和输入数据质量有一定要求。部分高级功能（如实时流式处理）可能需要特定的设备支持。
- **推荐使用**：**强烈推荐**。对于任何需要从表演数据创建高质量 MetaHuman 面部动画的项目，这是官方且功能最完整的解决方案。尽管它很新，但基于 Epic 的技术积累，其稳定性和可靠性有保障。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档页面)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (包含一个专门的测试模块)