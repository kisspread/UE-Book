# MetaHuman Animator Calibration Diagnostics

> The official MetaHuman Calibration Diagnostics Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 校准诊断工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCalibrationDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics) | |

## 用途

该插件是 MetaHuman Animator 工作流中用于 **校准质量诊断** 的专用工具。它解决的核心问题是：在为 MetaHuman 数字人进行相机校准后，如何量化评估校准的准确性，并可视化定位潜在问题区域。插件提供了一套完整的误差分析和可视化方案，允许用户检测特征点、计算重投影误差、将图像划分为网格分析误差分布，并最终基于误差分析结果对不同的校准方案进行排序选择，帮助用户找到最优的校准配置。

## 使用场景

- 当你为 MetaHuman 角色的表演捕捉设置了多相机校准后，需要检查每个相机的校准精度是否达标。
- 你需要对比不同校准方案（例如，不同时间段拍摄的校准数据），并基于客观的误差数据选择最佳的一个。
- 校准后的人脸重建出现扭曲或对不齐的问题，你需要诊断是哪个相机或图像区域的校准存在误差。
- 在自动化流程中，需要根据误差分析自动挑选出最优的校准结果。

## 蓝图用法

该插件的蓝图 API 主要集中在 `UMetaHumanRobustFeatureMatcher` 类，用于进行特征检测和获取检测数据。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 使用捕获数据和诊断选项初始化特征匹配器 | `UMetaHumanRobustFeatureMatcher` |
| `DetectFeatures` | 对指定帧进行特征点检测 | `UMetaHumanRobustFeatureMatcher` |
| `GetFeatures` | 获取指定帧已检测到的特征点数据 | `UMetaHumanRobustFeatureMatcher` |
| `GetCameraNames` | 获取所有相机的名称列表 | `UMetaHumanRobustFeatureMatcher` |
| `GetImageSizes` | 获取所有相机图像的尺寸 | `UMetaHumanRobustFeatureMatcher` |
| `OrderCalibrations` | 根据诊断结果对输入的校准数组进行排序，返回最优的校准 | `UMetaHumanDiagnosticsBasedSelector` |

### 使用示例（蓝图描述）

1.  **初始化与特征检测**：
    - 创建一个 `UMetaHumanRobustFeatureMatcher` 对象。
    - 调用 `Init` 节点，传入你的 `UFootageCaptureData` 和 `UMetaHumanCalibrationDiagnosticsOptions` 资产。
    - 对感兴趣的帧索引（例如 0, 10, 20）调用 `DetectFeatures` 节点进行检测。
    - 随后可以使用 `GetFeatures` 获取包含 3D 点、各相机 2D 点及重投影点的 `FDetectedFeatures` 结构体。

2.  **校准排序（集成到 MetaHuman Animator 流程）**：
    - 创建一个 `UMetaHumanDiagnosticsBasedSelector` 对象。
    - 在其 `Settings` 属性中，配置一个 `UMetaHumanDiagnosticsBasedSelectorSettings`，其中的 `FrameProvider` 可以是 `UMetaHumanManualFrameProvider`（手动指定要评估的帧）。
    - 在需要对多个 `UCameraCalibration` 进行排序时，调用 `OrderCalibrations` 节点，传入 `UCaptureData` 和待排序的校准数组。该节点会基于误差分析返回一个排序后（最优在前）的数组。

## C++ 用法

### 头文件引入

```cpp
#include "UMetaHumanRobustFeatureMatcher.h"
#include "MetaHumanCalibrationDiagnosticsOptions.h"
#include "Selectors/MetaHumanDiagnosticsBasedSelector.h"
// 用于误差计算分析
#include "Utils/MetaHumanCalibrationErrorCalculator.h"
#include "Utils/MetaHumanCalibrationErrorAnalysis.h"
```

### 基本用法

从 `UMetaHumanRobustFeatureMatcher` 的公共接口出发，演示特征检测的基本流程。

```cpp
// 假设已持有有效的 UFootageCaptureData* CaptureData 和 UMetaHumanCalibrationDiagnosticsOptions* Options

// 1. 创建并初始化匹配器
UMetaHumanRobustFeatureMatcher* FeatureMatcher = NewObject<UMetaHumanRobustFeatureMatcher>();
bool bSuccess = FeatureMatcher->Init(CaptureData, Options);
if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("特征匹配器初始化成功，检测到 %d 个相机。"), FeatureMatcher->GetCameraNames().Num());
}

// 2. 检测指定帧的特征点
int64 FrameIndex = 0;
if (FeatureMatcher->DetectFeatures(FrameIndex))
{
    // 3. 获取检测结果
    FDetectedFeatures Detected = FeatureMatcher->GetFeatures(FrameIndex);
    if (Detected.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("帧 %lld: 检测到 %d 个3D点。"), FrameIndex, Detected.Points3d.Num());
        // FDetectedFeatures 包含了用于误差计算的完整数据
    }
}
```

*来源文件：`Source/MetaHumanCalibrationDiagnostics/Private/UMetaHumanRobustFeatureMatcher.h`*

### 进阶用法

结合 `FMetaHumanCalibrationErrorCalculator` 和 `FMetaHumanCalibrationErrorAnalysis` 进行详细的误差分析。

```cpp
// 1. 准备数据：假设已经通过 FeatureMatcher 对一组帧 (SelectedFrames) 进行了检测，并收集了 FDetectedFeatures 数组
TArray<FDetectedFeatures> AllDetectedFeatures;
// ... 填充 AllDetectedFeatures ...

// 2. 初始化误差计算器
// 获取相机信息
TArray<FString> CameraNames = FeatureMatcher->GetCameraNames();
TArray<FIntVector2> ImageSizes = FeatureMatcher->GetImageSizes();

// 设定分析区域（可选），例如设置第一块区域
FBox2D AreaForFirstCamera(FVector2D(0.2, 0.2), FVector2D(0.8, 0.8));

FMetaHumanCalibrationErrorCalculator ErrorCalculator(FVector2D(640, 480), // 覆盖图尺寸，根据需要设定
                                                     CameraNames,
                                                     ImageSizes);
// 为特定相机设置感兴趣区域
ErrorCalculator.SetAreaOfInterestForCamera(CameraNames[0], AreaForFirstCamera);

// 3. 更新计算器数据
ErrorCalculator.Update(AllDetectedFeatures);

// 4. 进行误差分析
TArray<int32> FramesToAnalyze = {0, 5, 10}; // 分析哪些帧
FMetaHumanCalibrationErrorAnalysis ErrorAnalysis(ErrorCalculator, FramesToAnalyze);
TMap<FString, FCameraCalibrationScore> Scores = ErrorAnalysis.Analyze();

// 5. 解读分析结果
for (const auto& Pair : Scores)
{
    const FString& CameraName = Pair.Key;
    const FCameraCalibrationScore& CameraScore = Pair.Value;
    UE_LOG(LogTemp, Log, TEXT("相机 '%s' 的平均总分: %f, 平均误差分: %f"),
           *CameraName, CameraScore.MeanTotalScore, CameraScore.MeanErrorScore);
}
```

*来源文件：`Source/MetaHumanCalibrationDiagnostics/Private/Utils/MetaHumanCalibrationErrorCalculator.h`, `.../MetaHumanCalibrationErrorAnalysis.h`*

## Demo 示例

一个最小的控制台程序示例，展示如何使用 `UMetaHumanRobustFeatureMatcher` 进行初始化和特征检测。

```cpp
// MyDiagnosticsDemo.h
#pragma once
#include "CoreMinimal.h"
#include "UMetaHumanRobustFeatureMatcher.h"

class FMyDiagnosticsDemo
{
public:
    void RunDiagnosticsDemo(UFootageCaptureData* InCaptureData, UMetaHumanCalibrationDiagnosticsOptions* InOptions);
};
```

```cpp
// MyDiagnosticsDemo.cpp
#include "MyDiagnosticsDemo.h"
#include "UMetaHumanRobustFeatureMatcher.h"

void FMyDiagnosticsDemo::RunDiagnosticsDemo(UFootageCaptureData* InCaptureData, UMetaHumanCalibrationDiagnosticsOptions* InOptions)
{
    if (!InCaptureData || !InOptions)
    {
        UE_LOG(LogTemp, Error, TEXT("无效的输入数据。"));
        return;
    }

    // 创建并初始化特征匹配器
    UMetaHumanRobustFeatureMatcher* Matcher = NewObject<UMetaHumanRobustFeatureMatcher>();
    if (!Matcher->Init(InCaptureData, InOptions))
    {
        UE_LOG(LogTemp, Error, TEXT("特征匹配器初始化失败。"));
        return;
    }

    TArray<FString> Cameras = Matcher->GetCameraNames();
    UE_LOG(LogTemp, Log, TEXT("可用相机: %s"), *FString::Join(Cameras, TEXT(", ")));

    // 检测第一帧
    const int64 TargetFrame = 0;
    if (Matcher->DetectFeatures(TargetFrame))
    {
        FDetectedFeatures Features = Matcher->GetFeatures(TargetFrame);
        UE_LOG(LogTemp, Log, TEXT("在帧 %lld 上成功检测到特征点。3D点数: %d"), TargetFrame, Features.Points3d.Num());
        for (const FCameraPoints& CP : Features.CameraPoints)
        {
            UE_LOG(LogTemp, Verbose, TEXT("  - 某相机检测到 %d 个2D点"), CP.Points.Num());
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("在帧 %lld 上未检测到特征点。"), TargetFrame);
    }
}
```

## 模块依赖

除了常见的 Core/Engine/Slate 等基础模块外，该插件有一个关键的外部依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationProcessing` | 提供底层的校准处理功能，是本插件进行特征检测和误差计算的基础引擎。 |

此外，插件本身是编辑器插件（`Type: Editor`），依赖 `UnrealEd` 等模块来实现其UI窗口和编辑器工具功能。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志打印中 32/64 位格式说明符与参数位数不匹配的警告。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏统一迁移到 UE_LOGF 宏。 |
| 2026-04-13 | `6f8e9aeb` | [MetaHumanCalibration] Enable MetaHumanCalibrationProcessing on Mac | 为 Mac 平台启用了依赖的 MetaHumanCalibrationProcessing 插件。 |
| 2026-03-30 | `91150aa0` | Finding best calibration based on diagnostics | 实现了基于诊断结果自动寻找最佳校准的功能。 |
| 2026-03-18 | `aa1f1c34` | Diagnostics data with error analysis | 新增了带有误差分析的诊断数据功能。 |

### 维护评价

该插件于 **2025年9月** 创建，目前仍处于 **实验性（Experimental）** 状态。从 Git 历史看，最近半年有**持续的功能性更新**（新增误差分析、校准排序功能）和**平台兼容性维护**（Mac 支持），表明其**开发活跃**。

**主要特点**：
- 功能聚焦，为 MetaHuman Animator 的校准质量验证提供了专业工具。
- 作为实验性插件，API 和功能在正式版前可能会有变动。
- 依赖 `MetaHumanCalibrationProcessing`，需确保该插件可用。

**推荐**：对于正在使用 MetaHuman Animator 并对校准精度有高要求的开发者，推荐尝试使用此插件进行诊断。但请注意其**实验性**状态，不建议在需要高度稳定的生产环境中立即采用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics/Tests) (如果存在)