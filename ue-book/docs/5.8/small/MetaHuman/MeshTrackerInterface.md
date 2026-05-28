# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人类动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数字人资产、动画数据、配置文件） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-11-08 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 为 MetaHuman 数字人系统提供的官方动画制作与驱动工具包。它并非一个单一功能插件，而是一个集成了完整工作流的庞大套件，解决了从真实世界捕捉数据到驱动高保真 MetaHuman 角色动画的端到端问题。

其核心价值在于：
1.  **数据摄取与处理**：提供标准化的接口和工具，用于接收来自外部设备（如 iPhone 的 ARKit 面部捕捉、专业立体摄影机阵列、音频文件）的原始数据。
2.  **面部动画解算**：包含先进的面部追踪、轮廓追踪、深度生成（立体视觉）、动画求解器等算法，能将 2D 视频或深度数据精确地解算为 MetaHuman 骨骼控制器的动画数据。
3.  **性能与质量优化**：提供后处理滤镜、全局优化（如眼动和牙齿求解）、以及预测性求解器，用于提升动画的平滑度、真实感和稳定性。
4.  **资产管理与集成**：包含“身份”和“性能”资产概念，管理从捕捉到最终动画的数据，并与 UE 的序列器、Control Rig 等系统深度集成，实现批量处理和非线性编辑。

简单来说，MetaHuman Animator 是让 MetaHuman “活起来”的专业动画引擎。

## 使用场景

-   **影视级数字人制作**：使用专业立体摄影机阵列拍摄演员表演，通过 MetaHuman Animator 生成与 MetaHuman 角色一一对应的高精度面部动画序列。
-   **游戏中的实时角色动画**：利用 iPhone 的 ARKit 面部捕捉数据，实时或离线驱动游戏内的 MetaHuman 角色表情，用于过场动画或玩家角色。
-   **VTuber 与虚拟直播**：将摄像头捕捉的面部表情实时映射到 MetaHuman 虚拟形象上，用于直播或视频录制。
-   **音频驱动动画**：通过 `MetaHumanSpeech2Face` 模块，仅从音频文件即可生成对应的口型与面部动画，适用于快速原型或配音场景。
-   **批量处理与管线集成**：使用 `MetaHumanBatchProcessor` 模块，在无人值守的情况下处理大量捕捉素材，适配专业影视或游戏生产管线。

## 蓝图用法

MetaHuman Animator 主要通过编辑器界面和资产驱动，但其底层逻辑也暴露了部分蓝图节点，主要用于流程控制和查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize` | 初始化面部追踪器实例 | `IMetaHumanFaceTrackerInterface` |
| `LoadDNA` (从文件路径) | 加载 DNA 资产文件 | `IMetaHumanFaceTrackerInterface` |
| `SetCameras` | 设置用于追踪的相机标定数据 | `IMetaHumanFaceTrackerInterface` |
| `ResetTrack` | 重置并开始一段新的追踪序列 | `IMetaHumanFaceTrackerInterface` |
| `SetInputData` | 设置当前帧的图像和地标数据 | `IMetaHumanFaceTrackerInterface` |
| `Track` | 执行单帧面部追踪并获取结果 | `IMetaHumanFaceTrackerInterface` |
| `GetTrackingState` | 获取追踪状态（头姿、控制值、网格顶点等） | `IMetaHumanFaceTrackerInterface` |
| `Init` | 初始化深度生成器 | `IDepthGeneratorInterface` |
| `GetDepthMap` | 获取计算得到的深度图 | `IDepthGeneratorInterface` |
| `Init` | 初始化光学流计算器 | `IOpticalFlowInterface` |
| `CalculateFlow` | 计算两帧图像间的光流 | `IOpticalFlowInterface` |
| `TrainPredictiveSolver` | 训练预测性求解器 | `IPredictiveSolverInterface` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接实例化这些接口。标准工作流是：
1.  **准备数据**：使用“元人类性能”资产导入或录制的视频/音频数据。
2.  **创建“元人类身份”**：在内容浏览器中创建该资产，它将管理一个 MetaHuman 角色的追踪配置。
3.  **执行追踪**：在身份资产的编辑器界面中，配置好视频源、相机设置后，点击“追踪”按钮。这个过程在后台调用了上述蓝图接口（如 `SetCameras`, `SetInputData`, `Track` 的连续循环）。
4.  **查看与导出**：追踪完成后，结果会显示在性能资产中。你可以通过“导出”功能将动画数据（Control Rig 轨道）添加到关卡序列器，或直接作为动画序列保存。

## C++ 用法

高级用户或需要深度集成的插件开发者可以通过 C++ 接口直接控制 MetaHuman Animator 的核心流程。这些接口以 `IModularFeature` 的形式存在，需要从模块系统中获取。

### 头文件引入

```cpp
#include "MeshTrackerInterface/Public/MetaHumanFaceTrackerInterface.h"
```

### 基本用法

获取面部追踪器接口的工厂，并创建一个追踪器实例进行初始化。

```cpp
// 示例：获取面部追踪器工厂并创建实例（代码逻辑示意）
#include "IModularFeatures.h"
#include "MetaHumanFaceTrackerInterface.h"

void CreateAndInitFaceTracker()
{
    // 1. 从模块化特性系统中获取工厂
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(IFaceTrackerNodeImplFactory::GetModularFeatureName()))
    {
        IFaceTrackerNodeImplFactory* FaceTrackerFactory = &ModularFeatures.GetModularFeature<IFaceTrackerNodeImplFactory>(IFaceTrackerNodeImplFactory::GetModularFeatureName());

        // 2. 使用工厂创建具体的追踪器实现
        TSharedPtr<IMetaHumanFaceTrackerInterface> FaceTracker = FaceTrackerFactory->CreateFaceTrackerImplementor();

        // 3. 初始化追踪器 (需要有效的配置JSON字符串)
        FString TemplateJson = TEXT("{\"template\": \"...\"}");
        FString ConfigJson = TEXT("{\"config\": \"...\"}");
        FTrackerOpticalFlowConfiguration OptFlowConfig;
        FString DeviceLUID; // 通常为空，或从 DepthProcessingMetadataProvider 获取
        
        if (FaceTracker->Init(TemplateJson, ConfigJson, OptFlowConfig, DeviceLUID))
        {
            UE_LOG(LogTemp, Log, TEXT("Face Tracker Initialized Successfully."));
            
            // 后续步骤：LoadDNA, SetCameras, ResetTrack, 循环 SetInputData -> Track -> GetTrackingState
        }
    }
}
```

### 进阶用法

结合 `IPredictiveSolverInterface` 进行求解器训练，或使用 `IFaceTrackerPostProcessingInterface` 进行离线全局优化。这些通常发生在批处理流程中。

```cpp
// 示例：使用预测性求解器接口（代码逻辑示意）
void TrainSolver()
{
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    if (ModularFeatures.IsModularFeatureAvailable(IPredictiveSolverInterface::GetModularFeatureName()))
    {
        IPredictiveSolverInterface* SolverInterface = &ModularFeatures.GetModularFeature<IPredictiveSolverInterface>(IPredictiveSolverInterface::GetModularFeatureName());
        
        // 准备训练配置和结果结构体
        FPredictiveSolversTaskConfig TrainConfig;
        // ... 填充配置数据 ...
        
        FPredictiveSolversResult TrainResult;
        
        // 使用原子变量进行进度和取消控制
        std::atomic<bool> bIsDone(false);
        std::atomic<float> Progress(0.0f);
        std::atomic<bool> bIsCancelled(false);
        
        auto ProgressCallback = [](float InProgress)
        {
            UE_LOG(LogTemp, Log, TEXT("Training Progress: %.2f%%"), InProgress * 100.0f);
        };
        
        // 启动异步训练（可能需要在一个单独线程中调用）
        SolverInterface->TrainPredictiveSolver(bIsDone, Progress, ProgressCallback, bIsCancelled, TrainConfig, TrainResult);
        
        // 在另一个地方（例如 Tick 或定时器）检查 bIsDone 并处理 TrainResult
    }
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何检查 MetaHuman Animator 核心接口是否可用。由于完整的追踪流程需要配置文件和资源，此处仅展示接口获取。

```cpp
// MetaHumanDemoModule.h
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

class FMetaHumanDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MetaHumanDemoModule.cpp
#include "MetaHumanDemoModule.h"
#include "IModularFeatures.h"
#include "MetaHumanFaceTrackerInterface.h"

#define LOCTEXT_NAMESPACE "FMetaHumanDemoModule"

void FMetaHumanDemoModule::StartupModule()
{
    // 在插件加载后检查核心接口
    IModularFeatures& ModularFeatures = IModularFeatures::Get();
    
    bool bHasFaceTrackerFactory = ModularFeatures.IsModularFeatureAvailable(IFaceTrackerNodeImplFactory::GetModularFeatureName());
    bool bHasPredictiveSolver = ModularFeatures.IsModularFeatureAvailable(IPredictiveSolverInterface::GetModularFeatureName());
    bool bHasDepthProcessor = ModularFeatures.IsModularFeatureAvailable(IDepthProcessingMetadataProvider::GetModularFeatureName());
    
    UE_LOG(LogTemp, Log, TEXT("MetaHuman Animator Core Interfaces Available: FaceTrackerFactory=%s, PredictiveSolver=%s, DepthProcessor=%s"),
        bHasFaceTrackerFactory ? TEXT("True") : TEXT("False"),
        bHasPredictiveSolver ? TEXT("True") : TEXT("False"),
        bHasDepthProcessor ? TEXT("True") : TEXT("False"));
}

void FMetaHumanDemoModule::ShutdownModule()
{
    // 清理工作
}

#undef LOCTEXT_NAMESPACE
    
IMPLEMENT_MODULE(FMetaHumanDemoModule, MetaHumanDemo)
```

## 模块依赖

要使用 MetaHuman Animator 的功能，你的项目模块通常需要依赖 `MetaHumanCore` 和 `MetaHumanSDKEditor`。更具体的依赖取决于你使用的功能。

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 底层核心计算库，包含面部追踪、解算器等算法实现。 |
| `MetaHumanSDKEditor` | MetaHuman 编辑器工具和资产类型的 SDK。 |
| `ControlRigDeveloper` | 用于与 Control Rig 资产交互，生成驱动骨骼动画的控制逻辑。 |
| `SkeletalMeshUtilitiesCommon` | 用于处理骨骼网格体相关的通用工具函数。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 启用身体追踪时禁用关卡序列导出，避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色身上的渲染伪影问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在进行身体追踪时过滤可视化对象，优化性能。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为已存在的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复序列器缓存导致的问题。 |

### 维护评价

**活跃维护**。MetaHuman Animator 是 Epic Games 主推的数字人核心工具之一，自2021年创建以来持续更新。从最近的提交记录看（截至2026年5月），开发团队仍在积极修复问题、优化性能并添加新功能（如身体追踪集成）。其作为“官方工具包”的定位也保证了其长期维护。这是一个**推荐使用**的、功能完整且不断进化的专业插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/MetaHuman/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) （示例）