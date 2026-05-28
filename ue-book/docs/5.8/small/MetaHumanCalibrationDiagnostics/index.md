# MetaHuman Animator Calibration Diagnostics

> The official MetaHuman Calibration Diagnostics Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 校准诊断工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具） |
| 模块 | `MetaHumanCalibrationDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics) | |

## 用途

该插件为 MetaHuman 相机标定提供**质量诊断与可视化工具**。它解决的核心问题是：在 MetaHuman Animator 工作流中，如何评估相机标定（Camera Calibration）的质量。

具体来说，插件提供：
- **特征点检测与匹配**：在拍摄素材中自动检测棋盘格/特征点，并在多相机之间进行鲁棒匹配
- **重投影误差计算**：计算每个相机、每帧、每个图像块（4×6 分区）的 RMS / Mean / Median / P90 误差
- **可视化诊断窗口**：编辑器中的交互式图像查看器，叠加显示检测到的特征点、误差热力图、感兴趣区域
- **智能标定排序**：基于误差分析和覆盖度评分，自动推荐最佳标定结果

简而言之，它让 MetaHuman 用户能够**直观地看到标定质量的薄弱区域**，并通过量化指标判断标定是否满足要求。

## 使用场景

- 你使用 MetaHuman Animator 捕获了面部表演 → 需要验证多相机标定质量是否可靠
- 标定重投影误差偏高 → 用诊断窗口定位具体是哪个相机、哪帧、哪个区域的误差最大
- 有多组标定结果需要比较 → 用 DiagnosticsBasedSelector 基于评分自动选出最优标定
- 需要精确控制哪些帧参与标定评估 → 通过 FrameProvider 手动指定帧集合

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化特征匹配器（传入素材和选项） | `UMetaHumanRobustFeatureMatcher` |
| `DetectFeatures` | 对指定帧执行特征检测 | `UMetaHumanRobustFeatureMatcher` |
| `GetFeatures` | 获取指定帧的已检测特征数据 | `UMetaHumanRobustFeatureMatcher` |
| `GetCameraNames` | 获取所有相机名称列表 | `UMetaHumanRobustFeatureMatcher` |
| `GetImagePaths` | 获取指定相机的所有帧图像路径 | `UMetaHumanRobustFeatureMatcher` |
| `GetImageSizes` | 获取各相机图像尺寸 | `UMetaHumanRobustFeatureMatcher` |
| `GetSelectedFrames` | 获取选中的帧索引列表 | `UMetaHumanFeatureMatcherFrameProvider` |

### 使用示例（蓝图描述）

1. 创建一个 `UMetaHumanRobustFeatureMatcher` 对象
2. 创建一个 `UMetaHumanCalibrationDiagnosticsOptions` 对象，设置 `CameraCalibration`（要诊断的标定资产）和误差阈值（`RMSErrorThreshold` 默认 3.0）
3. 调用 `Init(CaptureData, Options)` 初始化
4. 循环调用 `DetectFeatures(FrameIndex)` 检测各帧特征点
5. 调用 `GetFeatures(FrameIndex)` 获取 `FDetectedFeatures` 结构体，其中包含 3D 点、各相机 2D 点、重投影后的 2D 点

> **提示**：实际工作流中，推荐通过编辑器菜单直接打开诊断窗口进行交互式操作，而非纯蓝图调用。

## C++ 用法

### 头文件引入

```cpp
#include "Selectors/MetaHumanDiagnosticsBasedSelector.h"
// 私有头文件（仅插件内部使用）：
// #include "UMetaHumanRobustFeatureMatcher.h"
// #include "MetaHumanCalibrationDiagnosticsOptions.h"
// #include "Utils/MetaHumanCalibrationErrorCalculator.h"
// #include "Utils/MetaHumanCalibrationErrorAnalysis.h"
```

> **注意**：该插件大多数头文件位于 `Private/` 目录下，表明其设计为编辑器工具而非对外暴露 API。对外的公共 API 主要是 `UMetaHumanDiagnosticsBasedSelector` 用于标定排序。

### 基本用法

```cpp
// 创建基于诊断的选择器设置
UMetaHumanDiagnosticsBasedSelectorSettings* Settings = NewObject<UMetaHumanDiagnosticsBasedSelectorSettings>();

// 设置手动帧选择器
UMetaHumanManualFrameProvider* FrameProvider = NewObject<UMetaHumanManualFrameProvider>();
FrameProvider->SelectedFrames = {0, 10, 20, 30, 40};
Settings->FrameProvider = FrameProvider;

// 创建选择器并用于排序标定结果
UMetaHumanDiagnosticsBasedSelector* Selector = NewObject<UMetaHumanDiagnosticsBasedSelector>();
TArray<UCameraCalibration*> OrderedCalibrations = Selector->OrderCalibrations(CaptureData, CameraCalibrations);
```

### 进阶用法

```cpp
// 使用误差计算器分析标定质量（插件内部逻辑）
#include "MetaHumanCalibrationErrorCalculator.h"

// 初始化计算器：传入覆盖图尺寸、相机名称、图像尺寸
FMetaHumanCalibrationErrorCalculator Calculator(
    FVector2D(4, 6),           // 覆盖图分为 4x6 块
    CameraNames,               // 相机名称数组
    ImageSizes                 // 各相机图像尺寸
);

// 可选：设置感兴趣区域以限定评估范围
Calculator.SetAreaOfInterestForCamera(CameraName, FBox2D(Min, Max));

// 更新检测到的特征
Calculator.Update(DetectedFeaturesArray);

// 获取各层级误差
double TotalRMS = Calculator.GetTotalRMSError();
double FrameRMS = Calculator.GetRMSErrorForFrame(FrameIndex);
double CameraRMS = Calculator.GetRMSErrorForFrame(CameraName, FrameIndex);
double BlockRMS = Calculator.GetRMSErrorForBlock(CameraName, BlockIndex, FrameIndex);

// 使用误差分析对多标定结果评分
FMetaHumanCalibrationErrorAnalysis Analysis(Calculator, SelectedFrames);
TMap<FString, FCameraCalibrationScore> Scores = Analysis.Analyze();
```

## Demo 示例

```cpp
// MetaHumanCalibrationDiagnosticsDemo.h
#pragma once
#include "CoreMinimal.h"
#include "CameraCalibration.h"

// 前置声明（这些类来自 MetaHumanCalibrationDiagnostics 和 MetaHumanCalibrationProcessing 插件）
class UFootageCaptureData;
class UMetaHumanRobustFeatureMatcher;
class UMetaHumanCalibrationDiagnosticsOptions;

UCLASS(BlueprintType)
class UCalibrationDiagnosticsDemo : public UObject
{
    GENERATED_BODY()

public:
    /** 运行一个简单的标定诊断流程 */
    UFUNCTION(BlueprintCallable, Category = "Demo")
    void RunDiagnostics(UFootageCaptureData* InCaptureData, UCameraCalibration* InCalibration);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanRobustFeatureMatcher> FeatureMatcher;

    UPROPERTY()
    TObjectPtr<UMetaHumanCalibrationDiagnosticsOptions> Options;
};
```

```cpp
// MetaHumanCalibrationDiagnosticsDemo.cpp
#include "MetaHumanCalibrationDiagnosticsDemo.h"
#include "UMetaHumanRobustFeatureMatcher.h"
#include "MetaHumanCalibrationDiagnosticsOptions.h"
#include "FootageCaptureData.h"

void UCalibrationDiagnosticsDemo::RunDiagnostics(
    UFootageCaptureData* InCaptureData,
    UCameraCalibration* InCalibration)
{
    if (!InCaptureData || !InCalibration)
    {
        UE_LOG(LogTemp, Warning, TEXT("Invalid input data"));
        return;
    }

    // 1. 创建并配置选项
    Options = NewObject<UMetaHumanCalibrationDiagnosticsOptions>();
    Options->CameraCalibration = InCalibration;
    Options->RMSErrorThreshold = 3.0;
    Options->FeatureMatchErrorThreshold = 5.0;

    // 2. 创建特征匹配器并初始化
    FeatureMatcher = NewObject<UMetaHumanRobustFeatureMatcher>();
    if (!FeatureMatcher->Init(InCaptureData, Options))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize feature matcher"));
        return;
    }

    // 3. 获取相机信息
    TArray<FString> CameraNames = FeatureMatcher->GetCameraNames();
    TArray<FIntVector2> ImageSizes = FeatureMatcher->GetImageSizes();

    UE_LOG(LogTemp, Log, TEXT("Found %d cameras"), CameraNames.Num());

    // 4. 对第 0 帧执行特征检测
    const int64 FrameIndex = 0;
    FeatureMatcher->DetectFeatures(FrameIndex);

    // 5. 获取检测结果
    FDetectedFeatures Features = FeatureMatcher->GetFeatures(FrameIndex);

    if (Features.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Frame %lld: Detected %d 3D points across %d cameras"),
            FrameIndex, Features.Points3d.Num(), Features.CameraPoints.Num());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Frame %lld: Feature detection failed"), FrameIndex);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationProcessing` | 核心标定处理逻辑（通过 Plugin 依赖声明） |

> 其余为标准 Core/Engine/Slate 等依赖，无特殊模块需求。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移 UE_LOG 宏到 UE_LOGF 新标准 |
| 2026-04-13 | `6f8e9aeb` | [MetaHumanCalibration] Enable MetaHumanCalibrationProcessing on Mac | 为 Mac 平台启用标定处理支持 |
| 2026-03-30 | `91150aa0` | Finding best calibration based on diagnostics | 新增基于诊断结果自动寻找最佳标定功能 |
| 2026-03-18 | `aa1f1c34` | Diagnostics data with error analysis | 新增带误差分析的诊断数据功能 |

### 维护评价

该插件创建于 2025 年 9 月，目前处于**活跃开发**状态：

- ✅ **持续更新**：最近 1 个月内有 3 次实质性功能提交（误差分析、最佳标定选择、跨平台支持）
- ✅ **代码质量**：近期提交包含格式修复和宏迁移，表明在持续改善代码规范
- ⚠️ **实验性状态**：标记为 `IsExperimentalVersion=true`，API 可能变动
- ⚠️ **编辑器专用**：仅限 Editor 模块，不能用于运行时打包

**推荐使用**：作为 MetaHuman Animator 工作流的一部分，该工具在标定质量诊断场景下是不可或缺的。但由于处于实验阶段，建议关注版本更新时的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics)
- 官方文档：无
- 测试用例：未找到（插件内无测试目录）