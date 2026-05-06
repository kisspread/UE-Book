# MetaHuman Animator Calibration Diagnostics

> The official MetaHuman Calibration Diagnostics Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 校准诊断工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器样式） |
| 模块 | `MetaHumanCalibrationDiagnostics` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-24 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics) | |

## 用途

MetaHuman Animator 的校准诊断工具，用于评估和可视化 MetaHuman 面部校准质量。该插件为开发者提供了以下核心能力：

- **校准误差分析**：通过重投影误差（RMS、Mean、Median、P90）量化校准精度。
- **特征点可视化**：在参考帧上叠加显示检测到的特征点、重投影点、逐块误差热图。
- **区域兴趣（AOI）支持**：允许用户框选特定区域（如眼睛、嘴巴），仅对该区域进行误差计算，便于聚焦关键部位。
- **交互式诊断界面**：基于 Slate 的编辑器窗口，提供图像查看器、参数调节、帧浏览、误差统计等功能。

该插件解决了 MetaHuman 面部捕捉管线中“如何判断校准是否足够精确”的问题，是高质量面部动画生产必须的验证步骤。

## 使用场景

- 你正在使用 MetaHuman Animator 采集面部表演数据，需要验证标定数据的质量。
- 你希望直观看到各个相机视角下的特征点检测偏差，定位标定薄弱环节（如特定区域误差过大）。
- 你需要调整校准参数（如 RMS 误差阈值、特征匹配误差阈值）并立即看到效果反馈。
- 你在开发 MetaHuman 相关工具链，需要调用校准诊断的 C++ API 实现自动化验证。

## 蓝图用法

由于插件主要提供编辑器 Slate UI 和 C++ 接口，**没有公开的 BlueprintCallable 函数**（UMetaHumanRobustFeatureMatcher 类有 BlueprintCallable 函数，但需要结合其他类使用，且不是独立节点）。核心功能通过编辑器窗口交互完成。

### 编辑器工具

插件注册了一个编辑器窗口（通过 `SCalibrationDiagnosticsWindow`）。打开方式：

1. 确保已启用插件（编辑→插件→MetaHuman→MetaHuman Animator Calibration Diagnostics 勾选）。
2. 在 MetaHuman Animator 工作流中，选择校准数据后，通过工具栏或菜单打开“Calibration Diagnostics”窗口。
3. 在窗口中可以：
   - 切换不同相机视图（如果有多相机数据）。
   - 使用帧滑块浏览时间序列。
   - 点击“Detect”执行特征检测与误差计算。
   - 切换显示：检测点、逐块误差、兴趣区域。
   - 调整 RMS 误差阈值、特征匹配误差阈值等参数，实时更新颜色反馈。

### 核心节点（C++ 蓝图可调用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 初始化特征匹配器，传入捕获数据和诊断选项 | `UMetaHumanRobustFeatureMatcher` |
| `DetectFeatures` | 对指定帧执行特征检测 | `UMetaHumanRobustFeatureMatcher` |
| `GetFeatures` | 获取指定帧的检测结果（3D点、重投影点等） | `UMetaHumanRobustFeatureMatcher` |
| `GetImagePaths` | 获取指定相机名的图像路径数组 | `UMetaHumanRobustFeatureMatcher` |

由于此类被标记为 `BlueprintType` 和 `BlueprintCallable`，你可以在蓝图创建和调用它，但通常更推荐直接在 C++ 或其他编辑器工具中使用。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCalibrationDiagnosticsModule.h"        // 模块入口
#include "UMetaHumanRobustFeatureMatcher.h"              // 特征匹配器
#include "MetaHumanCalibrationDiagnosticsOptions.h"      // 诊断选项
#include "Utils/MetaHumanCalibrationErrorCalculator.h"   // 误差计算器
#include "Widgets/SCalibrationDiagnosticsWindow.h"       // 编辑器窗口
```

### 基本用法

```cpp
// 1. 准备捕获数据和选项
UFootageCaptureData* CaptureData = ...;  // 从 MetaHuman管线获取
UMetaHumanCalibrationDiagnosticsOptions* Options = NewObject<UMetaHumanCalibrationDiagnosticsOptions>();
Options->CameraCalibration = CaptureData->CameraCalibration;
Options->RMSErrorThreshold = 3.0;
Options->FeatureMatchErrorThreshold = 5.0;

// 2. 创建特征匹配器
UMetaHumanRobustFeatureMatcher* FeatureMatcher = NewObject<UMetaHumanRobustFeatureMatcher>();
if (FeatureMatcher->Init(CaptureData, Options))
{
    // 3. 对第0帧进行检测
    int64 FrameIndex = 0;
    if (FeatureMatcher->DetectFeatures(FrameIndex))
    {
        FDetectedFeatures Features = FeatureMatcher->GetFeatures(FrameIndex);
        // 访问检测结果
        for (const FCameraPoints& CamPoints : Features.CameraPoints)
        {
            for (const FVector2D& Pt : CamPoints.Points)
            {
                UE_LOG(LogTemp, Log, TEXT("Camera point: %s"), *Pt.ToString());
            }
        }
    }
}
```
*来源: `Source/MetaHumanCalibrationDiagnostics/Private/UMetaHumanRobustFeatureMatcher.h`*

### 进阶用法

```cpp
// 使用误差计算器分析结果
TArray<FString> CameraNames = { TEXT("Camera1"), TEXT("Camera2") };
TArray<FIntVector2> ImageSizes = { FIntVector2(1920, 1080), FIntVector2(1920, 1080) };
FMetaHumanCalibrationErrorCalculator ErrorCalculator(FVector2D(1920, 1080), CameraNames, ImageSizes);

// 设置兴趣区域（仅计算局部误差）
FBox2D AOI(FVector2D(400, 300), FVector2D(800, 700));
ErrorCalculator.SetAreaOfInterestForCamera(TEXT("Camera1"), AOI);

// 更新检测结果
TArray<FDetectedFeatures> FeaturesArray;
// ... 填充检测结果 ...
ErrorCalculator.Update(FeaturesArray);

// 获取误差统计
double RMSError = ErrorCalculator.GetTotalRMSError();
double MeanError = ErrorCalculator.GetTotalMeanError();
double P90BlockError = ErrorCalculator.GetP90ErrorForBlock(TEXT("Camera1"), 5, 0);
```
*来源: `Source/MetaHumanCalibrationDiagnostics/Private/Utils/MetaHumanCalibrationErrorCalculator.h`*

### 编辑器窗口调用

```cpp
// 在模块加载时注册窗口
void FMetaHumanCalibrationDiagnosticsModule::StartupModule()
{
    // 将 SCalibrationDiagnosticsWindow 注册为独立编辑器窗口
    // 实际代码在模块的 StartupModule 中实现 SpawnTab 逻辑
}

// 打开窗口（示例）
TSharedRef<SWindow> DiagnoseWindow = SNew(SWindow)
    .Title(NSLOCTEXT("MetaHumanCalibrationDiagnostics", "WindowTitle", "Calibration Diagnostics"))
    .ClientSize(FVector2D(1280, 720))
    [
        SNew(SCalibrationDiagnosticsWindow)
            .FootageCaptureData(CaptureData)
    ];
FSlateApplication::Get().AddWindow(DiagnoseWindow);
```
*来源: `Source/MetaHumanCalibrationDiagnostics/Private/Widgets/SCalibrationDiagnosticsWindow.h`*

## Demo 示例

以下是一个完整的 C++ 编辑器模块示例，注册一个按钮打开诊断窗口。

**CalibrationDiagnosticsDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Modules/ModuleInterface.h"

class FCalibrationDiagnosticsDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class FUICommandList> PluginCommands;
    void OpenDiagnosticsWindow();
};
```

**CalibrationDiagnosticsDemo.cpp**
```cpp
#include "CalibrationDiagnosticsDemo.h"
#include "LevelEditor.h"
#include "Widgets/Docking/SDockTab.h"
#include "Widgets/SCalibrationDiagnosticsWindow.h"
#include "MetaHumanCalibrationDiagnosticsOptions.h"
#include "UMetaHumanRobustFeatureMatcher.h"
#include "CaptureData.h"

IMPLEMENT_MODULE(FCalibrationDiagnosticsDemoModule, CalibrationDiagnosticsDemo);

void FCalibrationDiagnosticsDemoModule::StartupModule()
{
    // 注册菜单扩展
    FLevelEditorModule& LevelEditor = FModuleManager::LoadModuleChecked<FLevelEditorModule>("LevelEditor");
    TSharedPtr<FExtender> MenuExtender = MakeShareable(new FExtender());
    MenuExtender->AddMenuExtension(
        "WindowLayout",
        EExtensionHook::After,
        PluginCommands,
        FMenuExtensionDelegate::CreateLambda([this](FMenuBuilder& Builder)
        {
            Builder.AddMenuEntry(
                NSLOCTEXT("Demo", "OpenCalibDiag", "Open Calibration Diagnostics"),
                NSLOCTEXT("Demo", "OpenCalibDiagTooltip", "Opens the MetaHuman calibration diagnostics window"),
                FSlateIcon(),
                FUIAction(FExecuteAction::CreateRaw(this, &FCalibrationDiagnosticsDemoModule::OpenDiagnosticsWindow))
            );
        })
    );
    LevelEditor.GetMenuExtensibilityManager()->AddExtender(MenuExtender);
}

void FCalibrationDiagnosticsDemoModule::ShutdownModule()
{
}

void FCalibrationDiagnosticsDemoModule::OpenDiagnosticsWindow()
{
    // 假设已有 FootageCaptureData （实际需要从 MetaHuman 管线获取）
    UFootageCaptureData* CaptureData = NewObject<UFootageCaptureData>();
    // 实际使用时需要填充真实数据，此处仅为演示框架

    TSharedRef<SWindow> DiagnoseWindow = SNew(SWindow)
        .Title(NSLOCTEXT("Demo", "DiagWindowTitle", "Calibration Diagnostics"))
        .ClientSize(FVector2D(1280, 720))
        [
            SNew(SCalibrationDiagnosticsWindow)
                .FootageCaptureData(CaptureData)
        ];
    FSlateApplication::Get().AddWindow(DiagnoseWindow);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCalibrationProcessing` | 提供校准处理和原生包装器（FeatureMatcher） |
| `InputCore` | 键盘快捷键支持（F、P、E 等） |
| `Slate` | 自定义 Slate 视图控件 |
| `SlateCore` | Slate 基础框架 |
| `UMG` | 选项编辑器的 UObject 属性渲染 |
| `EditorStyle` | 图标和样式 |
| `WorkspaceMenuStructure` | 窗口管理 |
| `Documentation` | 文档链接 |

## 维护状态

### 近期更新

- 2026-02-20 `594886ad` Remove PCH and use of binaries when compiling
- 2025-10-02 `07527885` Diagnostics refreshes the RMS when user selects different area of interest
- 2025-09-26 `c8c5fdb3` Allow running calibration on Capture Data with more than 2 image sequences
- 2025-09-25 `973c68a9` Updating Calibration icons
- 2025-09-24 `5c0153a1` Resolving bughawk issues

### 维护评价

该插件创建于 2025 年 9 月，属于较新的 MetaHuman 工具链组件。从提交记录看，半年内有多次功能性更新（支持多相机序列、RMS 动态刷新、编译系统清理），表明仍在活跃维护中。当前标为“实验性”，但实际已具备生产级功能。建议在 MetaHuman 管线中正常使用，但需留意后续可能的 API 调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/meta-human-animator-calibration-diagnostics/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/MetaHuman/MetaHumanCalibrationDiagnostics/Tests/)（暂无独立测试文件，集成在 MetaHuman 管线测试中）