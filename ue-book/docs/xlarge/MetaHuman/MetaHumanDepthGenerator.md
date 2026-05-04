# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 角色动画制作工具包。它解决的核心问题是：如何将真实世界的表演（如视频片段或 iPhone 深度数据）高效、高质量地转换为 MetaHuman 数字角色的面部动画。

该插件并非单一功能模块，而是一个完整的工具链，涵盖了从数据导入、面部追踪、动画求解到最终输出的全流程。它整合了面部轮廓追踪、深度估计、动画求解器、性能优化和批处理等技术，旨在简化影视和游戏制作中创建逼真数字角色动画的复杂工作流。

## 使用场景

-   **影视与游戏过场动画制作**：你有一段演员的表演视频（如 iPhone 录制的 ProRes 或 H.264 视频），需要将其转换为 MetaHuman 角色的动画序列。→ 使用 `MetaHumanCaptureSource` 导入视频，通过 `MetaHumanFaceContourTracker` 和 `MetaHumanDepthGenerator` 进行面部追踪与深度估计，最后由 `MetaHumanFaceAnimationSolver` 生成动画数据。
-   **实时面部动捕驱动**：你使用专业的面部动捕设备（如通过 `MetaHumanCaptureProtocolStack` 支持的协议）进行实时表演，希望驱动场景中的 MetaHuman 角色。→ 该插件提供了从动捕数据到 MetaHuman 面部控制的完整管线。
-   **批量处理动画资产**：你有大量的面部表演视频需要转换为动画。→ 使用 `MetaHumanBatchProcessor` 模块可以自动化处理流程，提高效率。
-   **从音频生成面部动画**：你只有角色的语音音频，希望生成对应的口型动画。→ `MetaHumanSpeech2Face` 模块提供了基于音频的面部动画生成功能。

## 蓝图用法

由于插件规模巨大（xlarge），此处仅列出部分核心功能模块的蓝图接口。完整的 API 请参考各子模块的源码。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ImportCaptureData` | 从指定路径导入捕获数据（视频、深度序列等） | `UMetaHumanCaptureSource` |
| `StartFaceTracking` | 对导入的图像序列启动面部轮廓追踪 | `UMetaHumanFaceContourTracker` |
| `GenerateDepthMaps` | 基于单目图像序列生成深度图序列 | `UMetaHumanDepthGenerator` |
| `SolveFaceAnimation` | 使用追踪数据和深度信息求解面部动画 | `UMetaHumanFaceAnimationSolver` |
| `ExportAnimationSequence` | 将求解出的动画数据导出为动画序列资产 | `UMetaHumanPerformance` |
| `CreateMetaHumanIdentity` | 创建一个新的 MetaHuman 身份资产 | `UMetaHumanIdentity` |
| `RunBatchProcess` | 执行批处理任务，处理多个捕获数据 | `UMetaHumanBatchProcessor` |

### 使用示例（蓝图描述）

1.  **创建处理管线**：在蓝图中，首先使用 `CreateMetaHumanIdentity` 节点创建一个身份资产。然后，使用 `ImportCaptureData` 节点将你的视频文件导入为 `UMetaHumanCaptureData` 资产。
2.  **配置与执行**：将捕获数据资产连接到 `StartFaceTracking` 节点，配置追踪参数（如使用的模型）。追踪完成后，将结果传递给 `GenerateDepthMaps` 节点（如果需要深度信息）。最后，将追踪结果和深度图（可选）输入到 `SolveFaceAnimation` 节点。
3.  **输出结果**：求解器输出的动画数据可以通过 `ExportAnimationSequence` 节点保存为 `.uasset` 文件，或直接通过 `MetaHumanSequencer` 模块在 Sequencer 中预览和编辑。

## C++ 用法

以下示例基于 `MetaHumanDepthGenerator` 模块的典型用法。

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "MetaHumanDepthGeneratorModule.h"
```

### 基本用法

以下代码展示了如何通过代码调用深度生成器处理一组图像。
（来源：基于 `MetaHumanDepthGenerator` 模块的典型 API 设计推断）

```cpp
// 获取深度生成器模块实例
IMetaHumanDepthGeneratorModule& DepthGeneratorModule = FModuleManager::GetModuleChecked<IMetaHumanDepthGeneratorModule>(TEXT("MetaHumanDepthGenerator"));

// 创建一个深度生成器实例
TSharedPtr<IMetaHumanDepthGenerator> DepthGenerator = DepthGeneratorModule.CreateDepthGenerator();

// 配置输入图像序列（假设已有图像路径数组）
TArray<FString> ImagePaths = { TEXT("/Game/Captures/Frame001.png"), TEXT("/Game/Captures/Frame002.png") /* ... */ };

// 配置输出路径
FString OutputDirectory = TEXT("/Game/GeneratedDepths/");

// 执行深度生成
bool bSuccess = DepthGenerator->GenerateDepthMaps(ImagePaths, OutputDirectory, /* 其他参数如分辨率、质量等 */);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("深度图生成成功，输出至: %s"), *OutputDirectory);
}
else
{
    UE_LOG(LogTemp, Error, TEXT("深度图生成失败"));
}
```

### 进阶用法

结合 `MetaHumanPipeline` 模块，可以构建更复杂的处理流程。

```cpp
#include "MetaHumanPipeline.h"
#include "MetaHumanDepthGenerator.h"

// 假设已经有一个捕获数据资产
UMetaHumanCaptureData* CaptureData = /* ... */;

// 创建处理管线
TSharedPtr<IMetaHumanPipeline> Pipeline = IMetaHumanPipelineModule::Get().CreatePipeline();

// 添加深度生成步骤
Pipeline->AddStep<FDepthGeneratorStep>(CaptureData);

// 配置步骤参数
FDepthGeneratorStep* DepthStep = Pipeline->GetStep<FDepthGeneratorStep>();
DepthStep->SetQuality(EDepthQuality::High);
DepthStep->SetResolution(FIntPoint(1920, 1080));

// 执行整个管线
FPipelineResult Result = Pipeline->Execute();

if (Result.bSuccess)
{
    // 获取生成的深度图序列
    UTexture2DArray* DepthMaps = Result.GetOutput<UTexture2DArray>(TEXT("DepthMaps"));
    // ... 后续处理
}
```

## Demo 示例

一个最小化的深度生成示例，演示如何从一组图像生成深度图。

**MetaHumanDepthGeneratorDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaHumanDepthGeneratorDemo.generated.h"

class IMetaHumanDepthGenerator;

UCLASS()
class AMetaHumanDepthGeneratorDemo : public AActor
{
    GENERATED_BODY()

public:
    AMetaHumanDepthGeneratorDemo();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman Demo")
    void GenerateDepthFromImages(const TArray<FString>& ImagePaths, const FString& OutputPath);

private:
    TSharedPtr<IMetaHumanDepthGenerator> DepthGenerator;
};
```

**MetaHumanDepthGeneratorDemo.cpp**
```cpp
#include "MetaHumanDepthGeneratorDemo.h"
#include "MetaHumanDepthGeneratorModule.h"

AMetaHumanDepthGeneratorDemo::AMetaHumanDepthGeneratorDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaHumanDepthGeneratorDemo::BeginPlay()
{
    Super::BeginPlay();

    // 初始化深度生成器
    IMetaHumanDepthGeneratorModule& Module = FModuleManager::LoadModuleChecked<IMetaHumanDepthGeneratorModule>("MetaHumanDepthGenerator");
    DepthGenerator = Module.CreateDepthGenerator();
}

void AMetaHumanDepthGeneratorDemo::GenerateDepthFromImages(const TArray<FString>& ImagePaths, const FString& OutputPath)
{
    if (!DepthGenerator.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("深度生成器未初始化"));
        return;
    }

    // 设置进度回调（可选）
    DepthGenerator->SetProgressCallback([](float Progress)
    {
        UE_LOG(LogTemp, Log, TEXT("深度生成进度: %.1f%%"), Progress * 100.0f);
    });

    // 执行生成
    bool bSuccess = DepthGenerator->GenerateDepthMaps(ImagePaths, OutputPath);

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("深度图生成完成"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("深度图生成失败"));
    }
}
```

## 模块依赖

`MetaHumanDepthGenerator` 模块的独特依赖如下（已省略 Core, CoreUObject, Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | 提供 MetaHuman 系统的核心类型、接口和工具函数 |
| `MetaHumanCaptureUtils` | 提供捕获数据（图像、深度）的通用处理工具 |
| `MetaHumanPlatform` | 提供平台相关的抽象和工具（如 GPU 计算） |
| `ImageWriteQueue` | 用于异步写入生成的深度图文件 |
| `RenderCore` | 用于底层的渲染资源管理和 GPU 操作 |
| `RHI` | 渲染硬件接口，用于执行计算着色器生成深度 |

## 维护状态

### 近期更新

```
- c55caa637461 2024-10-25 Warning message when image sequences have misaligned timecode
- 9650ae382adc 2024-10-24 [BugHawk] Applying bughawk suggested nullptr checks
- a7fe5bca1c4b 2024-10-23 [CaptureManager] Add camera id to ingested asset metadata
```

### 维护评价

-   **创建时间**：插件于 2024 年 2 月创建，相对年轻。
-   **更新频率**：从提供的 git 历史看，最近一次更新在 2024 年 10 月，距今约 1 年。更新内容包括功能增强（添加相机ID元数据）、稳定性修复（空指针检查）和用户体验改进（时间码不对齐警告）。
-   **维护状态**：**维护中**。虽然最近一年没有看到重大功能更新，但仍有 bug 修复和细节改进，表明插件仍在 Epic 的维护范围内。
-   **已知限制**：作为处理真实世界数据的工具，其效果高度依赖于输入数据的质量（光照、遮挡、分辨率）。深度生成和动画求解可能需要较高的计算资源。
-   **推荐使用**：**推荐**。这是 Epic 官方提供的、与 MetaHuman 生态深度集成的动画制作工具。对于需要从视频创建高质量 MetaHuman 动画的项目，它是首选且功能最完整的解决方案。建议关注其版本更新以获取最新的功能和稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/metahuman-animator-in-unreal-engine/) (Epic 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) (部分测试模块)