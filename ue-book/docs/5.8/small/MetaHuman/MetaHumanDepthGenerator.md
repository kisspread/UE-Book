# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的用于创建和驱动高保真数字人（MetaHuman）的综合性工具包。它不仅仅是一个动画工具，而是一个完整的管线，涵盖了从真实世界演员表演捕获（通过视频或专用设备）到生成可在 Unreal Engine 中使用的动画数据的整个流程。

该插件的核心功能是将演员的**面部表演**转换为数字 MetaHuman 角色的动画。它通过复杂的计算机视觉和机器学习算法，从输入的图像序列（可能是来自多视角相机的原始视频）中重建面部深度信息、追踪面部特征点、匹配到 MetaHuman 的面部模板（Identity），并最终求解出面部控制曲线（Control Rig）。整个过程高度自动化，并通过一系列专门的模块（如 `MetaHumanDepthGenerator`, `MetaHumanFaceContourTracker`, `MetaHumanFaceFittingSolver`, `MetaHumanFaceAnimationSolver`）协同工作。

**`MetaHumanDepthGenerator` 模块**是该管线中的关键一环。其核心功能是从多视角图像序列中生成对应的深度图（Depth Map）。深度信息对于后续的面部追踪和动画求解至关重要，因为它提供了面部几何形状的 3D 线索。该模块负责处理来自 `UFootageCaptureData` 的图像序列，应用相机校准信息，并输出可用于下游处理的深度数据资产。

## 使用场景

- **数字人表演捕捉**：你有一段或多段演员正面或侧面的高清视频素材，希望将这些表演“转录”到你的 MetaHuman 角色上，用于游戏过场动画或虚拟制片。
- **深度数据生成**：你拥有来自 MetaHuman Capture 应用或其他来源的多视角视频，并且需要为这些视频序列生成精确的深度信息，以便进行高质量的面部追踪和动画求解。
- **自动化深度处理流程**：你需要在一个批处理管线中自动为大量捕获素材生成深度数据，并希望将深度精度、分辨率等参数作为可配置选项。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Process` | 使用指定选项从 FootageCaptureData 生成深度数据 | `UMetaHumanDepthGenerator` |
| `AssetName` | 生成深度资产的名称 | `UMetaHumanGenerateDepthWindowOptions` |
| `PackagePath` | 深度资产的保存路径 | `UMetaHumanGenerateDepthWindowOptions` |
| `ImageSequenceRootPath` | 输入图像序列的根目录 | `UMetaHumanGenerateDepthWindowOptions` |
| `MinDistance` | 深度信息的有效最小距离（厘米） | `UMetaHumanGenerateDepthWindowOptions` |
| `MaxDistance` | 深度信息的有效最大距离（厘米） | `UMetaHumanGenerateDepthWindowOptions` |
| `DepthPrecision` | 输出深度数据的精度（如 1/80 精度） | `UMetaHumanGenerateDepthWindowOptions` |
| `DepthResolution` | 输出深度数据的分辨率缩放 | `UMetaHumanGenerateDepthWindowOptions` |

### 使用示例（蓝图描述）

1.  **创建选项对象**：在蓝图中创建一个 `UMetaHumanGenerateDepthWindowOptions` 的实例。
2.  **配置选项**：设置其 `AssetName`、`PackagePath`（内容浏览器路径）、`ImageSequenceRootPath`（指向包含视频帧的文件夹）。根据需要调整 `MinDistance`、`MaxDistance` 以及深度精度和分辨率。
3.  **调用处理**：创建一个 `UMetaHumanDepthGenerator` 实例。获取你的 `UFootageCaptureData` 资产引用。将资产引用和配置好的选项对象传递给 `Process` 节点。执行该节点即可启动深度生成流程，生成的深度资产将保存到指定路径。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanDepthGenerator.h"
#include "FootageCaptureData.h"
```

### 基本用法

基于 `UMetaHumanDepthGenerator::Process` 函数的签名和 `UMetaHumanGenerateDepthWindowOptions` 的属性，可以推断出以下用法。

```cpp
// 假设你已经有一个有效的 UFootageCaptureData* 指针
UFootageCaptureData* MyCaptureData = ...;

// 创建深度生成器
UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();

// 创建并配置选项
UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();
Options->AssetName = TEXT("MyDepthData");
Options->PackagePath.Path = TEXT("/Game/MetaHuman/Depths");
Options->ImageSequenceRootPath.Path = TEXT("C:/MyCaptures/Sequence1");
Options->bAutoSaveAssets = true;
Options->MinDistance = 15.0f;
Options->MaxDistance = 30.0f;
Options->DepthPrecision = EMetaHumanCaptureDepthPrecisionType::Quarter;
Options->DepthResolution = EMetaHumanCaptureDepthResolutionType::Full;

// 调用处理
bool bSuccess = DepthGenerator->Process(MyCaptureData, Options);

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("深度数据生成成功。"));
}
else
{
    UE_LOG(LogTemp, Error, TEXT("深度数据生成失败。"));
}
```

### 进阶用法

该模块还提供了用于管理深度数据自动重新导入配置的工具函数（命名空间 `UE::MetaHuman`）。这些函数可能在更复杂的资产管线中用到，例如，当源深度文件被外部工具更新时，需要更新 Unreal 的 `AutoReimport` 监视配置以包含或排除这些文件。

## Demo 示例

一个完整的、可编译的最小示例，展示如何通过C++调用深度生成功能。

```cpp
// MyDepthGeneratorUser.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyDepthGeneratorUser.generated.h"

class UFootageCaptureData;

UCLASS(BlueprintType, Blueprintable)
class UMyDepthGeneratorUser : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void GenerateDepthForCaptureData(UFootageCaptureData* CaptureData, const FString& OutputAssetName);
};

// MyDepthGeneratorUser.cpp
#include "MyDepthGeneratorUser.h"
#include "MetaHumanDepthGenerator.h"
#include "FootageCaptureData.h"
#include "Engine/Engine.h"

void UMyDepthGeneratorUser::GenerateDepthForCaptureData(UFootageCaptureData* CaptureData, const FString& OutputAssetName)
{
    if (!CaptureData)
    {
        UE_LOG(LogTemp, Error, TEXT("CaptureData is null."));
        return;
    }

    UMetaHumanDepthGenerator* DepthGenerator = NewObject<UMetaHumanDepthGenerator>();
    UMetaHumanGenerateDepthWindowOptions* Options = NewObject<UMetaHumanGenerateDepthWindowOptions>();

    // 配置选项
    Options->AssetName = OutputAssetName;
    Options->PackagePath.Path = TEXT("/Game/GeneratedDepths");
    Options->ImageSequenceRootPath.Path = CaptureData->GetFootagePath(); // 假设存在这样的方法获取路径
    Options->bAutoSaveAssets = false; // 在演示中不自动保存，以便检查
    Options->MinDistance = 10.0f;
    Options->MaxDistance = 25.0f;

    // 执行处理
    if (DepthGenerator->Process(CaptureData, Options))
    {
        UE_LOG(LogTemp, Log, TEXT("深度数据生成任务已启动。资产: %s"), *OutputAssetName);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("启动深度数据生成任务失败。"));
    }
}
```

## 模块依赖

根据 `MetaHumanDepthGenerator` 模块的性质，它很可能依赖以下模块（未在提供的信息中直接列出，需查看其 `Build.cs` 文件确认）：

| 模块 | 用途 |
|---|---|
| `MediaUtils`, `Media`, `MediaAssets` | 处理图像/视频媒体框架 |
| `ImageCore`, `ImageWriteQueue` | 图像处理和写入深度文件 |
| `VideoCore`, `CVCommon` | 视频处理基础和计算机视觉通用工具 |
| `MetaHumanCaptureUtils` | MetaHuman 捕获相关的通用工具函数 |
| `MetaHumanPlatform` | 平台相关的配置和路径处理 |
| `CameraCalibrationCore` | 处理 `UCameraCalibration` 数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 身体上的渲染瑕疵问题。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时，过滤掉可视化的辅助对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为已有的 MetaHuman 网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复与 Sequencer 缓存相关的错误。 |

### 维护评价

- **活跃维护**：根据提供的近期提交记录（截至 2026 年 5 月），该插件处于**非常活跃**的维护状态。提交频率高（几乎每天），且内容涉及功能增强（如导出动画序列）和重要的 Bug 修复（渲染瑕疵、缓存问题）。
- **官方支持**：作为 Epic Games 的官方插件，享有持续的技术支持和更新。
- **推荐使用**：**强烈推荐**。MetaHuman Animator 是 Unreal Engine 中创建电影级数字人动画的核心工具。`MetaHumanDepthGenerator` 作为其关键子模块，稳定性和重要性都很高。它与 UE 的工作流程深度集成，并随着引擎版本不断迭代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/metahuman-unreal-engine-documentation/) (MetaHuman 主文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest)