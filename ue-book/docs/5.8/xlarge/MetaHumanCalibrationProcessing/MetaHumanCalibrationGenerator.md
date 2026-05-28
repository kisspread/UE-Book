# MetaHuman Animator Calibration Processing

> The official MetaHuman Calibration Processing Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 校准处理 |
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时代码、编辑器工具、配置资产） |
| 模块 | `MetaHumanCalibrationCore` (Runtime), `MetaHumanCalibrationGenerator` (Runtime), `MetaHumanCalibrationLib` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing) | |

## 用途

MetaHumanCalibrationProcessing 是一个专业的相机校准工具集，专门用于 MetaHuman Animator 工作流。它的核心功能是**从棋盘格（如棋盘）校准图像序列中自动、批量地生成相机内参和外参校准资产（`UCameraCalibration`）**。

该插件解决了从原始捕获素材到精确相机模型转换过程中的自动化问题，主要功能包括：
1.  **棋盘格角点检测**：自动识别校准视频中棋盘格的角点。
2.  **自动选帧**：智能选择具有最佳棋盘格覆盖度的帧序列进行校准，提高校准精度。
3.  **批量处理**：支持对多个 `UFootageCaptureData` 资产进行一次性校准，极大提升工作效率。
4.  **可视化调试**：提供编辑器内的图像查看器，用于检查角点检测结果、覆盖度和兴趣区域（AoI）。
5.  **误差评估**：计算并输出重投影误差（RMS Error），作为校准质量的量化指标。

简而言之，这个插件是 MetaHuman 内容创建流程中，确保面部捕获数据能够精确映射到虚拟相机上的关键基础设施。

## 使用场景

-   你正在使用 **MetaHuman Animator** 和双目（立体）相机系统捕获面部表演数据。
-   你需要为每个捕获会话（Session）或设备生成精确的 **相机校准文件**，以确保面部追踪和动画数据的准确性。
-   你需要为大量历史捕获数据 **重新生成或批量更新** 相机校准。
-   你需要可视化检查校准图像，**手动调整兴趣区域**或验证角点检测质量。
-   你正在开发一个涉及复杂相机设置的 **虚拟制片** 或 **面部动捕** 流程。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Batch Generate Camera Calibration` | 最简单的批量校准入口，使用默认选项处理一组 `CaptureData` 资产。 | `UMetaHumanCalibrationBatchLibrary` |
| `Batch Generate Camera Calibration With Options` | 高级批量校准，支持为每个 `CaptureData` 指定自定义选项（如保存路径、选帧）。 | `UMetaHumanCalibrationBatchLibrary` |
| `Construct Default Options For Capture Data` | 为给定的 `CaptureData` 创建一个具有合理默认值的 `Options` 对象（如输出路径、自动选帧）。 | `UMetaHumanCalibrationBatchLibrary` |
| `Run` (Auto Frame Selector) | 对单个 `CaptureData` 和 `Config` 执行自动帧选择，返回推荐的帧索引数组。 | `UMetaHumanCalibrationAutoFrameSelector` |
| `Init` (Calibration Generator) | 使用棋盘格配置初始化校准生成器。 | `UMetaHumanCalibrationGenerator` |
| `Process` (Calibration Generator) | 使用初始化后的生成器和当前 `CaptureData`、`Options` 执行一次完整的校准流程。 | `UMetaHumanCalibrationGenerator` |

### 使用示例（蓝图描述）

**场景一：批量快速校准**
1.  创建一个 `TArray<UFootageCaptureData*>`，包含所有需要校准的捕获数据资产。
2.  创建一个 `UMetaHumanCalibrationGeneratorConfig` 对象，设置你的物理棋盘格尺寸（宽度、高度、方块大小）。
3.  拖拽出 `Batch Generate Camera Calibration` 节点。将捕获数据数组连接到 `CaptureDataAssets` 引脚，将配置对象连接到 `BoardConfig` 引脚。
4.  执行节点，返回一个 `FMetaHumanCalibrationBatchResult` 数组，其中每个元素包含对应资产的校准结果、RMS误差和资产路径。

**场景二：自定义输出路径和选帧**
1.  对于需要特殊处理的 `CaptureData` 资产，使用 `Construct Default Options For Capture Data` 节点获取默认选项。
2.  修改返回的 `Options` 对象的 `PackagePath` 和 `AssetName` 属性，指定自定义输出位置。
3.  （可选）手动设置 `Options` 的 `SelectedFrames` 数组以覆盖自动选帧。
4.  使用 `Batch Generate Camera Calibration With Options` 节点，并将修改后的 `Options` 数组传入 `OptionsPerAsset` 引脚。

**场景三：手动校准流程控制**
1.  创建 `UMetaHumanCalibrationGenerator` 对象。
2.  调用 `Init`，传入 `BoardConfig`。
3.  调用 `ConfigureCameras`，传入 `CaptureData` 以解析相机信息。
4.  调用 `Process`，传入 `CaptureData` 和自定义的 `Options` 执行校准。
5.  通过 `GetLastRMSError` 检查结果。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCalibrationGenerator.h"
#include "MetaHumanCalibrationGeneratorConfig.h"
#include "MetaHumanCalibrationGeneratorOptions.h"
#include "MetaHumanCalibrationBatchLibrary.h" // 用于静态批量函数
#include "FootageCaptureData.h" // 通常来自MetaHumanCalibrationCore
```

### 基本用法

**单资产校准（使用生成器对象）**
```cpp
// 来源: Private/MetaHumanCalibrationGenerator.h (结构化示例)
UMetaHumanCalibrationGenerator* CalibGenerator = NewObject<UMetaHumanCalibrationGenerator>();

// 1. 初始化，配置棋盘格参数
UMetaHumanCalibrationGeneratorConfig* Config = NewObject<UMetaHumanCalibrationGeneratorConfig>();
Config->BoardPatternWidth = 11;
Config->BoardPatternHeight = 16;
Config->BoardSquareSize = 0.75f; // 单位通常是厘米
if (!CalibGenerator->Init(Config))
{
    UE_LOG(LogTemp, Error, TEXT("Calibration generator init failed: %s"), *CalibGenerator->GetLastError());
    return;
}

// 2. 配置相机（解析CaptureData中的视频信息）
UFootageCaptureData* CaptureData = LoadObject<UFootageCaptureData>(...);
if (!CalibGenerator->ConfigureCameras(CaptureData))
{
    UE_LOG(LogTemp, Error, TEXT("Camera configuration failed."));
    return;
}

// 3. 配置校准选项
UMetaHumanCalibrationGeneratorOptions* Options = NewObject<UMetaHumanCalibrationGeneratorOptions>();
Options->AssetName = TEXT("MyCustomCalibration");
Options->PackagePath.Path = TEXT("/Game/MetaHumans/Calibrations");
Options->SharpnessThreshold = 6.0f;
// SelectedFrames 留空将使用自动选帧

// 4. 执行校准
if (CalibGenerator->Process(CaptureData, Options))
{
    double RMSError = CalibGenerator->GetLastRMSError();
    UE_LOG(LogTemp, Log, TEXT("Calibration succeeded with RMS error: %.4f"), RMSError);
}
```

### 进阶用法

**批量校准（使用静态库函数）**
```cpp
// 来源: Private/MetaHumanCalibrationBatchLibrary.h (结构化示例)
TArray<UFootageCaptureData*> AssetsToCalibrate = { Asset1, Asset2, Asset3 };
UMetaHumanCalibrationGeneratorConfig* BoardConfig = NewObject<UMetaHumanCalibrationGeneratorConfig>();
// ... 设置 BoardConfig ...

// 简单批量处理
TArray<FMetaHumanCalibrationBatchResult> Results = UMetaHumanCalibrationBatchLibrary::BatchGenerateCalibration(AssetsToCalibrate, BoardConfig);

// 检查结果
for (const FMetaHumanCalibrationBatchResult& Result : Results)
{
    if (Result.bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Asset: %s, RMS: %.4f, Path: %s"),
            *Result.CaptureData->GetName(), Result.RMSError, *Result.CalibrationAssetPath);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed for asset %s: %s"),
            *Result.CaptureData->GetName(), *Result.ErrorMessage);
    }
}
```

**自动帧选择**
```cpp
// 来源: Private/MetaHumanCalibrationAutoFrameSelector.h (结构化示例)
UMetaHumanCalibrationAutoFrameSelector* FrameSelector = NewObject<UMetaHumanCalibrationAutoFrameSelector>();
UMetaHumanCalibrationGeneratorOptions* Options = NewObject<UMetaHumanCalibrationGeneratorOptions>();
// ... 可设置 Options 中的 SharpnessThreshold 等 ...

TArray<int32> SelectedFrames = FrameSelector->Run(CaptureData, BoardConfig, Options);
UE_LOG(LogTemp, Log, TEXT("Auto-selected %d frames for calibration."), SelectedFrames.Num());
// 可将 SelectedFrames 设置到 Options->SelectedFrames 中用于后续 Process 调用
```

## Demo 示例

**CalibrationDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "CalibrationDemo.generated.h"

class UMetaHumanCalibrationGenerator;
class UMetaHumanCalibrationGeneratorConfig;
class UMetaHumanCalibrationGeneratorOptions;
class UFootageCaptureData;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UCalibrationDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UCalibrationDemoComponent();

    UFUNCTION(BlueprintCallable, Category="MetaHumanDemo")
    bool RunSimpleCalibrationDemo(UFootageCaptureData* CaptureData, const FString& OutputPath);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanCalibrationGenerator> CalibrationGenerator;

    bool InitializeGenerator();
};
```

**CalibrationDemo.cpp**
```cpp
#include "CalibrationDemo.h"
#include "MetaHumanCalibrationGenerator.h"
#include "MetaHumanCalibrationGeneratorConfig.h"
#include "MetaHumanCalibrationGeneratorOptions.h"
#include "FootageCaptureData.h"

UCalibrationDemoComponent::UCalibrationDemoComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UCalibrationDemoComponent::InitializeGenerator()
{
    if (!CalibrationGenerator)
    {
        CalibrationGenerator = NewObject<UMetaHumanCalibrationGenerator>(this);
    }

    // 使用默认棋盘格配置 (11x16, 0.75cm)
    UMetaHumanCalibrationGeneratorConfig* Config = NewObject<UMetaHumanCalibrationGeneratorConfig>();
    return CalibrationGenerator->Init(Config);
}

bool UCalibrationDemoComponent::RunSimpleCalibrationDemo(UFootageCaptureData* CaptureData, const FString& OutputPath)
{
    if (!CaptureData)
    {
        UE_LOG(LogTemp, Warning, TEXT("CaptureData is null."));
        return false;
    }

    if (!InitializeGenerator())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize calibration generator."));
        return false;
    }

    // 配置相机信息
    if (!CalibrationGenerator->ConfigureCameras(CaptureData))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to configure cameras from CaptureData."));
        return false;
    }

    // 创建校准选项，使用默认选帧
    UMetaHumanCalibrationGeneratorOptions* Options = NewObject<UMetaHumanCalibrationGeneratorOptions>();
    Options->PackagePath.Path = OutputPath;
    Options->AssetName = FString::Printf(TEXT("CC_%s"), *CaptureData->GetName());
    Options->bAutoSaveAssets = true; // 自动保存结果资产

    // 执行校准
    if (!CalibrationGenerator->Process(CaptureData, Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Calibration process failed: %s"), *CalibrationGenerator->GetLastError());
        return false;
    }

    double RMSError = CalibrationGenerator->GetLastRMSError();
    UE_LOG(LogTemp, Log, TEXT("Demo calibration completed. RMS Error: %.4f"), RMSError);
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationCore` | 提供核心数据类型（如 `UFootageCaptureData`, `FMetaHumanAreaOfInterest`）和接口。 |
| `MetaHumanCalibrationLib` | 底层的计算机视觉库，依赖 `UnrealEd`，可能封装了 OpenCV 或其他校准算法。 |
| `OpenCV` | 用于棋盘格角点检测和相机标定算法的底层库（通过 `MetaHumanCalibrationLib` 间接依赖）。 |

*注：该插件依赖关系清晰，`MetaHumanCalibrationGenerator` 模块作为主要功能层，依赖另外两个核心模块。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `7f10fbf1` | [MetaHuman] Titan v9.0.8 | 升级至 Titan v9.0.8 版本 |
| 2026-05-26 | `cfa3dac6` | [MetaHuman] Titan v9.0.7 | 升级至 Titan v9.0.7 版本 |
| 2026-05-21 | `e936df4b` | [MetaHuman] Titan v9.0.6 | 升级至 Titan v9.0.6 版本 |
| 2026-05-14 | `52cbd20d` | [MetaHuman] titan v9.0.5 | 升级至 Titan v9.0.5 版本 |
| 2026-05-13 | `df646fb2` | Use infinity as limit for initial distance, to not overflow float in calculations | 修复初始距离计算中的浮点数溢出问题 |

### 维护评价

-   **活跃维护**：插件创建于 2025 年 4 月，至今仅约 1 年，属于较新的插件。近期 git 历史（2026年5月）显示**持续、频繁的更新**，主要集中在底层 Titan 库的版本升级上，表明该插件与 MetaHuman 核心技术栈同步紧密。
-   **开发状态**：`.uplugin` 明确标示 `IsBetaVersion: false` 和 `IsExperimentalVersion: false`，表明其为**正式发布**的功能。`Installed: false` 说明它不是引擎默认捆绑插件，但作为 MetaHuman 套件的一部分，在相关工作流中会按需启用。
-   **推荐使用**：**强烈推荐**。该插件是 MetaHuman Animator 工作流中进行精确相机标定的官方且必要的工具。活跃的维护保证了与最新 MetaHuman 技术（Titan）的兼容性和稳定性。对于任何涉及 MetaHuman 面部动画捕获的项目，此插件都应视为基础设施的一部分。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing)
-   测试用例：（根据上下文，此插件的测试可能位于 `Engine/Plugins/MetaHuman/MetaHumanCalibrationProcessing/Tests/` 目录或引擎测试套件中）