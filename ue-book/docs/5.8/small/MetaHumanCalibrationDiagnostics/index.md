# MetaHuman Animator Calibration Diagnostics

> The official MetaHuman Calibration Diagnostics Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 校准诊断 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MetaHumanCalibrationDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-18 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics) | |

## 用途
这是一个面向 MetaHuman 动画制作流程的质量分析与问题诊断工具包。它并非一个简单的功能封装，而是为了解决 MetaHuman 校准过程中可能出现的复杂质量问题而存在。
其核心功能是**量化评估相机校准结果的准确性**，通过分析特征匹配点的重投影误差，提供可视化的误差分布图、块级误差统计和全局误差指标。这帮助技术美术师或动画师识别校准质量不佳的区域（如特定相机视角或图像区域），从而精准定位问题，优化校准流程或调整拍摄参数，最终获得更高质量的数字人面部动画数据。

## 使用场景
- 当你使用 **MetaHuman Animator** 处理面部捕捉素材（如iPhone视频）并生成相机校准后，需要评估校准质量是否满足动画要求。
- 当你发现最终渲染的数字人面部动画存在细微的扭曲、拉伸或不自然变形，怀疑是源头校准数据有问题时，使用此插件进行**定量误差分析**。
- 你需要为多个镜头或场景优化校准参数，希望找到一个**最优校准**（误差最小），而非手动逐个尝试。
- 你需要向团队其他成员展示或汇报校准质量问题，需要直观的**可视化报告**（如热力图、误差数值）。

## 蓝图用法
该插件主要面向**技术人员和高级用户**，其核心功能通常通过 C++ 接口调用或在编辑器 UI 中使用。提供的蓝图接口主要用于**配置和驱动**诊断流程。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化特征匹配器，传入捕捉数据和诊断选项 | `UMetaHumanRobustFeatureMatcher` |
| `DetectFeatures` | 对指定帧进行特征检测 | `UMetaHumanRobustFeatureMatcher` |
| `GetFeatures` | 获取指定帧的检测结果（2D点、3D点、重投影点） | `UMetaHumanRobustFeatureMatcher` |
| `OrderCalibrations` | 根据诊断结果对一组相机校准进行排序，最优在前 | `UMetaHumanDiagnosticsBasedSelector` |
| `GetSelectedFrames` | 获取用于计算最佳校准的帧索引列表 | `UMetaHumanFeatureMatcherFrameProvider` |

### 使用示例（蓝图描述）
在蓝图中配置一个 `UMetaHumanDiagnosticsBasedSelectorSettings` 对象，为其设置一个 `FrameProvider`（如 `UMetaHumanManualFrameProvider` 来指定要分析的关键帧）。然后，在驱动 MetaHuman 校准流程的逻辑中，使用 `UMetaHumanDiagnosticsBasedSelector` 作为校准选择器。当流程调用 `OrderCalibrations` 时，该选择器会在后台运行诊断分析，根据误差得分对传入的校准数组进行排序，并返回最优的校准序列。

## C++ 用法
该插件的 C++ 用法集中于对校准误差进行底层计算和分析。

### 头文件引入
```cpp
#include "MetaHumanRobustFeatureMatcher.h"
#include "MetaHumanCalibrationErrorCalculator.h"
#include "MetaHumanCalibrationErrorAnalysis.h"
```

### 基本用法
**使用 `UMetaHumanRobustFeatureMatcher` 检测特征并获取原始误差数据。**
```cpp
// 创建并初始化匹配器
UMetaHumanRobustFeatureMatcher* Matcher = NewObject<UMetaHumanRobustFeatureMatcher>();
bool bSuccess = Matcher->Init(CaptureData, DiagnosticsOptions);

if (bSuccess)
{
    // 对第10帧进行特征检测
    Matcher->DetectFeatures(10);
    // 获取该帧的检测结果
    FDetectedFeatures Features = Matcher->GetFeatures(10);
    
    // Features 现在包含了该帧所有相机的2D点、3D点及重投影点，可用于后续分析
}
```
*(来源: `UMetaHumanRobustFeatureMatcher.h`)*

### 进阶用法
**结合 `FMetaHumanCalibrationErrorCalculator` 和 `FMetaHumanCalibrationErrorAnalysis` 进行深度误差统计。**
```cpp
// 假设已有 Features 数据和相机信息
FMetaHumanCalibrationErrorCalculator Calculator(ImageSize, CameraNames, ImageSizes);
// 可选：设置感兴趣的区域
Calculator.SetAreaOfInterestForCamera(CameraName, AreaOfInterestBox);
// 更新计算器以包含新帧的数据
Calculator.Update(Features);

// 创建分析器，传入计算器和要分析的帧列表
FMetaHumanCalibrationErrorAnalysis Analyzer(Calculator, FrameIndices);
// 进行分析，获取每个相机的详细评分
TMap<FString, FCameraCalibrationScore> Scores = Analyzer.Analyze();

// 访问特定相机在特定帧的误差指标
double FrameRMSError = Calculator.GetRMSErrorForFrame(CameraName, FrameIndex);
FErrors BlockErrors = Calculator.GetErrorsForBlock(CameraName, BlockIndex, FrameIndex);
```
*(来源: `MetaHumanCalibrationErrorCalculator.h`, `MetaHumanCalibrationErrorAnalysis.h`)*

## Demo 示例
一个最小化的 C++ 示例，展示如何初始化诊断选项并运行一次基于诊断的校准排序。

**.h 文件**
```cpp
// MetaHumanCalibrationDemo.h
#pragma once
#include "CoreMinimal.h"

class UCameraCalibration;
class UFootageCaptureData;
class UMetaHumanCalibrationDiagnosticsOptions;

class FMetaHumanCalibrationDemo
{
public:
    void RunDiagnostics(UFootageCaptureData* InCaptureData, const TArray<UCameraCalibration*>& InCalibrations);

private:
    TStrongObjectPtr<UMetaHumanCalibrationDiagnosticsOptions> DiagnosticsOptions;
};
```

**.cpp 文件**
```cpp
// MetaHumanCalibrationDemo.cpp
#include "MetaHumanCalibrationDemo.h"
#include "MetaHumanCalibrationDiagnosticsOptions.h"
#include "MetaHumanDiagnosticsBasedSelector.h"
#include "FootageCaptureData.h"
#include "CameraCalibration.h"

void FMetaHumanCalibrationDemo::RunDiagnostics(UFootageCaptureData* InCaptureData, const TArray<UCameraCalibration*>& InCalibrations)
{
    if (!InCaptureData)
    {
        return;
    }

    // 创建并配置诊断选项
    DiagnosticsOptions = NewObject<UMetaHumanCalibrationDiagnosticsOptions>();
    DiagnosticsOptions->RMSErrorThreshold = 2.5; // 设置一个更严格的阈值

    // 创建基于诊断的选择器
    UMetaHumanDiagnosticsBasedSelector* Selector = NewObject<UMetaHumanDiagnosticsBasedSelector>();

    // 创建一个手动帧提供者，指定分析前10帧
    UMetaHumanManualFrameProvider* FrameProvider = NewObject<UMetaHumanManualFrameProvider>();
    for (int32 i = 0; i < 10; ++i)
    {
        FrameProvider->SelectedFrames.Add(i);
    }

    // 为选择器配置设置（这里简化了，实际中设置类通过 GetSettingsClass 获知）
    UMetaHumanDiagnosticsBasedSelectorSettings* Settings = NewObject<UMetaHumanDiagnosticsBasedSelectorSettings>();
    Settings->FrameProvider = FrameProvider;
    Selector->SetSettings(Settings); // 假设有此方法或通过其他方式关联

    // 执行排序：传入原始校准数组，得到按诊断得分排序后的新数组
    TArray<UCameraCalibration*> OrderedCalibrations = Selector->OrderCalibrations(InCaptureData, InCalibrations);

    // OrderedCalibrations[0] 现在是诊断认为最优的校准
    UE_LOG(LogTemp, Log, TEXT("Best calibration found: %s"), *GetNameSafe(OrderedCalibrations[0]));
}
```

## 模块依赖
该插件依赖 MetaHuman 核心的校准处理模块。
| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationProcessing` | 提供基础的相机校准数据结构和处理功能 |

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复日志输出中64位格式说明符的正确使用问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到更安全的 `UE_LOGF` 宏 |
| 2026-04-13 | `6f8e9aeb` | [MetaHumanCalibration] Enable MetaHumanCalibrationProcessing on Mac | 在 Mac 平台上启用 MetaHuman 校准处理功能 |
| 2026-03-30 | `91150aa0` | Finding best calibration based on diagnostics | 新增基于诊断结果查找最佳校准的核心功能 |
| 2026-03-18 | `aa1f1c34` | Diagnostics data with error analysis | 增加了误差分析的核心数据结构和计算逻辑 |

### 维护评价
- **创建时间**: 2025年9月，插件较新。
- **近期更新**: 最近3个月内有**实质性功能更新**（添加最佳校准查找、误差分析）和平台支持扩展（Mac），以及代码质量改进（日志宏、格式修复）。更新频率较高。
- **活跃度**: **活跃维护中**。Epic Games 的 MetaHuman 团队似乎正在积极开发和完善此工具。
- **已知限制**: 作为实验性插件，API 和功能可能在未来版本中发生变化。其依赖的 `MetaHumanCalibrationProcessing` 插件也是必需的。
- **推荐使用**: **推荐**。对于从事 MetaHuman 资产制作和校准工作的用户，这是一个非常有用的官方质量保障工具。尽管标记为实验性，但其活跃的开发状态表明它正在走向成熟。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics)
- [官方文档]()（暂无）
- [测试用例]()（暂未在该插件目录内发现测试文件）