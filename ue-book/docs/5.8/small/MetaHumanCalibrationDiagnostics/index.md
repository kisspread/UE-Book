# MetaHuman Animator Calibration Diagnostics

> The official MetaHuman Calibration Diagnostics Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman校准诊断 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具、蓝图资产） |
| 模块 | `MetaHumanCalibrationDiagnostics` (Editor) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2025-09-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics) | |

## 用途

该插件是 MetaHuman Animator 工作流中的**相机校准质量诊断工具**。它用于解决从多视图视频（Footage）中捕捉 MetaHuman 动画时，相机校准不准确导致的动画数据扭曲、抖动等问题。其核心功能是**评估相机标定的精度**，通过检测特征点、计算重投影误差、提供可视化诊断视图，帮助动画师识别哪些相机或哪些画面的标定存在问题，从而指导用户优化标定流程或选择最佳标定结果。

## 使用场景

- 你正在使用 **MetaHuman Animator** 从多机位视频中驱动一个 MetaHuman 角色，但发现生成的面部动画在某些角度或帧有扭曲。
- 你怀疑是**相机标定**不准确，但无法直观地知道问题出在哪个相机或哪几帧画面上。
- 你需要一个工具来**量化**并**可视化**标定误差，以便精准地排查和修复问题。

## 蓝图用法

该插件主要提供编辑器内的诊断窗口，但也暴露了部分核心功能到蓝图，便于高级用户进行自动化分析或自定义流程。

### 核心节点

以下节点均来自 `UMetaHumanRobustFeatureMatcher` 类。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化特征匹配器。需要传入 `FootageCaptureData` 和诊断选项。 | `UMetaHumanRobustFeatureMatcher` |
| `DetectFeatures` | 对指定帧 `InFrame` 进行特征点检测。 | `UMetaHumanRobustFeatureMatcher` |
| `GetFeatures` | 获取指定帧的特征点检测结果，包括2D点、3D点和重投影点。 | `UMetaHumanRobustFeatureMatcher` |
| `GetCameraNames` | 获取当前 Footage 中所有相机的名称列表。 | `UMetaHumanRobustFeatureMatcher` |
| `GetImagePaths` | 获取指定相机的所有帧图像路径。 | `UMetaHumanRobustFeatureMatcher` |

### 使用示例（蓝图描述）

一个典型的蓝图使用流程是：
1.  创建一个 `UMetaHumanRobustFeatureMatcher` 对象。
2.  调用 `Init` 节点，传入你的 `UFootageCaptureData` 资产和一个配置好的 `UMetaHumanCalibrationDiagnosticsOptions` 对象。
3.  循环调用 `DetectFeatures` 节点，处理你需要诊断的帧序列。
4.  在每次检测后，立即调用 `GetFeatures` 节点来获取 `FDetectedFeatures` 结构体，其中包含了该帧的详细诊断数据（原始点、3D点、重投影点等）。
5.  你可以基于获取的数据（例如计算 `Points3d` 和 `Points3dReprojected` 之间的差异）编写自己的误差分析逻辑。

## C++ 用法

虽然该插件主要面向编辑器用户，但其内部的误差计算和分析工具类是纯 C++ 的，可供其他模块引用。

### 头文件引入

```cpp
#include "MetaHumanCalibrationDiagnostics/Utils/MetaHumanCalibrationErrorCalculator.h"
#include "MetaHumanCalibrationDiagnostics/Utils/MetaHumanCalibrationErrorAnalysis.h"
```

### 基本用法

`FMetaHumanCalibrationErrorCalculator` 是核心的误差计算引擎，用于管理按帧、按相机、按图像区块划分的误差数据。

```cpp
// 来源： MetaHumanCalibrationErrorCalculator.h 使用推断
// 假设我们已经有了检测到的特征点数据 FDetectedFeatures 和相机信息
TArray<FString> CameraNames = {TEXT("LeftEye"), TEXT("RightEye"), TEXT("Front")};
TArray<FIntVector2> ImageSizes = {FIntVector2(1920, 1080), FIntVector2(1920, 1080), FIntVector2(1920, 1080)};
FVector2D CoverageMapSize(1920, 1080); // 通常与图像尺寸相同

// 1. 创建计算器
FMetaHumanCalibrationErrorCalculator ErrorCalculator(CoverageMapSize, CameraNames, ImageSizes);

// 2. （可选）为特定相机设置关注区域 (Area of Interest)
FBox2D AreaOfInterest(FVector2D(100, 100), FVector2D(1800, 900)); // 例如排除图像边缘
ErrorCalculator.SetAreaOfInterestForCamera(TEXT("Front"), AreaOfInterest);

// 3. 更新计算器（传入一帧或多帧的检测结果）
// FDetectedFeatures DetectedFeatures = ...; // 从某处获取
ErrorCalculator.Update(DetectedFeatures);

// 4. 查询误差
double FrontCameraFrame5_RMS = ErrorCalculator.GetRMSErrorForFrame(TEXT("Front"), 5);
double TotalMeanError = ErrorCalculator.GetTotalMeanError();
```

### 进阶用法

结合 `FMetaHumanCalibrationErrorAnalysis` 进行多帧排序分析，这在 `UMetaHumanDiagnosticsBasedSelector` 内部被用来寻找最佳标定帧。

```cpp
// 来源： MetaHumanCalibrationErrorAnalysis.h 和 Selectors/MetaHumanDiagnosticsBasedSelector.h
// 假设 ErrorCalculator 已经更新了多帧数据
TArray<int32> SelectedFrames = {10, 15, 20, 25, 30}; // 一些待分析的帧

// 创建错误分析器
FMetaHumanCalibrationErrorAnalysis ErrorAnalysis(ErrorCalculator, SelectedFrames);

// 运行分析，得到每个相机在各帧上的综合评分
TMap<FString, FCameraCalibrationScore> CameraScores = ErrorAnalysis.Analyze();

// 遍历结果，找到每个相机评分最高的帧
for (const auto& Pair : CameraScores)
{
    const FString& CameraName = Pair.Key;
    const FCameraCalibrationScore& Score = Pair.Value;
    
    int32 BestFrame = INDEX_NONE;
    double HighestTotalScore = -TNumericLimits<double>::Max();
    
    for (const auto& FrameScorePair : Score.TotalScorePerFrame)
    {
        if (FrameScorePair.Value > HighestTotalScore)
        {
            HighestTotalScore = FrameScorePair.Value;
            BestFrame = FrameScorePair.Key;
        }
    }
    // 现在 BestFrame 对于 CameraName 来说是评分最高的帧
    UE_LOG(LogMetaHuman, Log, TEXT("Best frame for camera %s is %d with score %f"), *CameraName, BestFrame, HighestTotalScore);
}
```

## Demo 示例

一个演示如何使用蓝图 API 初始化并运行特征检测的最小 C++ 代码。

```cpp
// MyCalibrationDiagnostics.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/EngineSubsystem.h"
#include "MyCalibrationDiagnostics.generated.h"

class UFootageCaptureData;
class UMetaHumanCalibrationDiagnosticsOptions;
class UMetaHumanRobustFeatureMatcher;

UCLASS()
class UMyCalibrationDiagnosticsSubsystem : public UEngineSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "MyDiagnostics")
    void RunDiagnosticsOnFootage(UFootageCaptureData* InFootageData, UMetaHumanCalibrationDiagnosticsOptions* InOptions, const TArray<int32>& InFrames);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanRobustFeatureMatcher> FeatureMatcher;
};
```

```cpp
// MyCalibrationDiagnostics.cpp
#include "MyCalibrationDiagnostics.h"
#include "MetaHumanCalibrationDiagnostics/UMetaHumanRobustFeatureMatcher.h"
#include "MetaHumanCalibrationDiagnostics/MetaHumanCalibrationDiagnosticsOptions.h"
#include "FootageCaptureData.h"

void UMyCalibrationDiagnosticsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    FeatureMatcher = NewObject<UMetaHumanRobustFeatureMatcher>();
}

void UMyCalibrationDiagnosticsSubsystem::Deinitialize()
{
    FeatureMatcher = nullptr;
    Super::Deinitialize();
}

void UMyCalibrationDiagnosticsSubsystem::RunDiagnosticsOnFootage(
    UFootageCaptureData* InFootageData, 
    UMetaHumanCalibrationDiagnosticsOptions* InOptions, 
    const TArray<int32>& InFrames)
{
    if (!FeatureMatcher || !InFootageData || !InOptions)
    {
        return;
    }

    // 1. 初始化
    if (!FeatureMatcher->Init(InFootageData, InOptions))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Feature Matcher."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("Initialized feature matcher. Starting diagnostics for %d frames."), InFrames.Num());

    // 2. 遍历指定帧进行检测
    for (int32 FrameIndex : InFrames)
    {
        if (FeatureMatcher->DetectFeatures(FrameIndex))
        {
            FDetectedFeatures Features = FeatureMatcher->GetFeatures(FrameIndex);
            if (Features.IsValid())
            {
                // 这里可以进行更复杂的分析，比如计算重投影误差
                // 为简化示例，我们只打印信息
                UE_LOG(LogTemp, Log, TEXT("Frame %d: Detected %d 3D points, %d camera point sets."), 
                    FrameIndex, Features.Points3d.Num(), Features.CameraPoints.Num());
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("Frame %d: Detection succeeded but returned invalid features."), FrameIndex);
            }
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("Frame %d: Feature detection failed."), FrameIndex);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("Diagnostics complete."));
}
```

## 模块依赖

该插件本身依赖一个同级的核心处理插件。

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationProcessing` | 提供底层的相机标定处理逻辑，是本诊断工具的数据基础和依赖项。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志和字符串格式化中的平台兼容性问题。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的UE_LOG宏迁移到新的UE_LOGF宏。 |
| 2026-04-13 | `6f8e9aeb` | [MetaHumanCalibration] Enable MetaHumanCalibrationProcessing on Mac | 启用了对Mac平台的支持。 |
| 2026-03-30 | `91150aa0` | Finding best calibration based on diagnostics | 实现了基于诊断数据自动寻找最佳标定结果的核心功能。 |
| 2026-03-18 | `aa1f1c34` | Diagnostics data with error analysis | 添加了错误分析数据结构和计算逻辑。 |

### 维护评价

该插件**处于活跃维护中**。它创建于2025年9月，并在2026年3月至4月期间有多次实质性功能更新（错误分析、跨平台支持、最佳标定查找）和代码质量改进（宏迁移、格式修复）。作为`Experimental`状态且`EnabledByDefault=false`的插件，它仍在积极开发迭代中。预计随着MetaHuman Animator工具链的成熟，此诊断工具也将持续完善。当前推荐在开发或测试环境中使用，以诊断和解决MetaHuman动画工作流中的相机标定问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics)
- [官方文档]() (暂无)