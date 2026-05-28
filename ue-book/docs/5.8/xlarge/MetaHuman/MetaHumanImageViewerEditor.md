# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（混合媒体资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个完整的面部动画制作工具包，其核心功能是将真实的演员表演（通常来自深度摄像头或立体摄像机录制的视频）转换为可驱动 MetaHuman 角色的高质量面部动画。它提供了一套完整的工作流程，涵盖从素材导入、面部跟踪、曲线编辑、动画解算到最终驱动 MetaHuman 角色的全过程。与简单的动画重定向不同，该插件专注于处理包含深度信息的“表演捕捉”数据，以生成更精准、更符合原始表演的动画结果。插件内置了先进的面部轮廓跟踪器、动画解算器和图像查看器，使得动画师可以在编辑器中直接对跟踪数据进行精细调整和验证。

## 使用场景

-   **基于深度摄像头（如 iPhone Lidar）的面部动画制作**：你使用了支持深度捕捉的设备录制了演员的面部表演，需要将这些深度视频序列（`.abc` 或自定义格式）导入 Unreal Engine，并将其驱动 MetaHuman 角色的面部骨骼和变形器。
-   **复杂的面部表演优化**：你从外部捕捉软件获得了初步的面部跟踪数据，但需要在引擎内进行迭代优化，特别是处理闭眼、夸张表情或面部遮挡等情况。你可以使用本插件的编辑器工具查看、编辑和验证这些曲线数据。
-   **批量处理面部动画素材**：你有多段同一演员的表演素材需要快速处理成动画。你可以使用 `MetaHumanBatchProcessor` 模块在编辑器外自动化执行跟踪、解算等流程。
-   **创建高质量面部动画序列**：你需要为 MetaHuman 角色制作一段完整的对话或表演动画，并希望动画能保留演员表演的细微差别。你可以使用 `MetaHumanPerformance` 模块将处理好的动画应用到 MetaHuman 角色上，并导出为动画序列。
-   **需要深度网格可视化进行调试**：在调试面部跟踪或解算问题时，你希望将深度数据以网格形式叠加显示在 2D 素材上，以便更直观地观察空间关系。可以使用 `UMetaHumanDepthMeshComponent` 实现此功能。

## 蓝图用法

此插件主要为 C++ 编辑器工具和底层处理管线提供支持，其用户交互层面主要通过 Slate UI 控件实现。以下是关键的可交互组件：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UpdateDisplayedDataForWidget` | 从底层的曲线数据控制器（`FMetaHumanCurveDataController`）更新当前帧的显示数据（控制顶点和稠密样条点），刷新查看器的可视化。 | `STrackerImageViewer` |
| `SetDataControllerForCurrentFrame` | 为图像查看器设置指定帧的曲线数据控制器，该控制器包含了所有曲线的顶点、样条点等信息。 | `STrackerImageViewer` |
| `SetEditCurvesAndPointsEnabled` | 设置用户是否可以与查看器中的曲线和控制点进行交互编辑（移动、添加/删除等）。 | `STrackerImageViewer` |
| `SetMediaTextures` | 为素材组件设置代表颜色和深度的媒体纹理。纹理的可见性由视图模式（A/B视图）和通道显示（`ShowRGBChannel`/`ShowDepthChannel`）控制。 | `UMetaHumanFootageComponent` |
| `ShowColorChannel` | 在指定的AB视图模式（如A视图或B视图）下显示颜色通道。 | `UMetaHumanFootageComponent` |
| `SetUndistortionEnabled` | 设置是否对正在显示的素材启用去畸变处理。 | `UMetaHumanFootageComponent` |
| `SetDepthTexture` | 为深度网格组件设置包含深度数据的纹理。 | `UMetaHumanDepthMeshComponent` |
| `SetDepthRange` | 设置深度网格或素材平面材质中可见的深度近平面和远平面，用于调整深度数据的可视化范围。 | `UMetaHumanDepthMeshComponent`, `UMetaHumanFootageComponent` |

### 使用示例（蓝图描述）

虽然无法直接截图，但使用流程通常如下：

1.  在自定义的编辑器面板或窗口中，添加一个 `STrackerImageViewer` 控件。该控件可以内嵌在 Slate 布局中。
2.  当用户在时间轴上选择或预览某帧素材时，你的 C++ 编辑器模块会从 `MetaHumanPerformance` 或 `MetaHumanFaceContourTracker` 等模块获取该帧的 `FMetaHumanCurveDataController` 对象。
3.  调用 `STrackerImageViewer::SetDataControllerForCurrentFrame(DataController)` 将数据绑定到查看器。
4.  调用 `STrackerImageViewer::UpdateDisplayedDataForWidget()` 来立即刷新视图。
5.  同时，你可能有一个 `UMetaHumanFootageComponent` 在场景中，它代表了原始素材平面。你可以通过 `SetMediaTextures(ColorTexture, DepthTexture)` 来同步更新它显示的图像。

## C++ 用法

### 头文件引入

```cpp
#include "STrackerImageViewer.h"
#include "SABImage.h"
#include "MetaHumanFootageComponent.h"
#include "MetaHumanDepthMeshComponent.h"
#include "MetaHumanCurveDataController.h" // 来自其他模块，是核心数据类
```

### 基本用法

以下代码片段展示如何在编辑器面板中创建并配置一个面部跟踪图像查看器。

```cpp
// 创建一个 STrackerImageViewer 实例
TSharedRef<STrackerImageViewer> TrackerImageViewer = SNew(STrackerImageViewer)
    .Image(FCoreStyle::Get().GetDefaultBrush()) // 通常后续会通过 SetTextures 设置真实纹理
    .DefaultCurvesColor(FLinearColor::Green)
    .DefaultPointsColor(FLinearColor::Yellow)
    .ShouldDrawPoints(true)
    .ShouldDrawCurves(true);

// 假设我们通过某个模块获取了当前帧的曲线数据控制器
TSharedPtr<FMetaHumanCurveDataController> CurrentFrameData = GetCurveDataControllerForCurrentFrame();

// 将数据控制器绑定到查看器
TrackerImageViewer->SetDataControllerForCurrentFrame(CurrentFrameData);

// 刷新显示
TrackerImageViewer->UpdateDisplayedDataForWidget();

// 设置图像尺寸（通常从视频元数据或校准信息中获取）
TrackerImageViewer->SetTrackerImageSize(FIntPoint(1920, 1080));

// 禁用用户编辑（如果处于只读预览模式）
TrackerImageViewer->SetEditCurvesAndPointsEnabled(false);
```

### 进阶用法

结合素材组件和深度网格组件，构建一个完整的预览视图。

```cpp
// 在 Actor 或 Component 中
UPROPERTY()
TObjectPtr<UMetaHumanFootageComponent> FootageComponent;

UPROPERTY()
TObjectPtr<UMetaHumanDepthMeshComponent> DepthMeshComponent;

// 初始化素材组件
FootageComponent = CreateDefaultSubobject<UMetaHumanFootageComponent>(TEXT("FootageComponent"));

// 假设已加载颜色和深度纹理
UTexture* ColorTexture = LoadObject<UTexture>(nullptr, TEXT("/Path/To/ColorSequence"));
UTexture* DepthTexture = LoadObject<UTexture>(nullptr, TEXT("/Path/To/DepthSequence"));

// 设置素材纹理
FootageComponent->SetMediaTextures(ColorTexture, DepthTexture, true);

// 设置相机校准（从捕捉数据中解析）
FootageComponent->SetCameraCalibration(MyCameraCalibrationAsset);

// 在AB视图模式下显示颜色通道
FootageComponent->ShowColorChannel(EABImageViewMode::A);

// 初始化深度网格组件
DepthMeshComponent = CreateDefaultSubobject<UMetaHumanDepthMeshComponent>(TEXT("DepthMeshComponent"));

// 设置深度纹理和校准
DepthMeshComponent->SetDepthTexture(DepthTexture);
DepthMeshComponent->SetCameraCalibration(MyCameraCalibrationAsset);
DepthMeshComponent->SetDepthRange(10.0f, 55.5f);
DepthMeshComponent->SetSize(1920, 1080); // 与视频分辨率匹配
```

## Demo 示例

这是一个最小的编辑器工具面板实现，包含一个 `STrackerImageViewer` 用于显示和编辑面部曲线。

**`MyFaceTrackerPanel.h`**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "STrackerImageViewer.h"

class FMetaHumanCurveDataController;

class SMyFaceTrackerPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyFaceTrackerPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    void SetCurveDataController(TSharedPtr<FMetaHumanCurveDataController> InDataController);
    void RefreshView();

private:
    TSharedPtr<STrackerImageViewer> TrackerViewer;
};
```

**`MyFaceTrackerPanel.cpp`**
```cpp
#include "MyFaceTrackerPanel.h"
#include "MetaHumanCurveDataController.h" // 假设存在此头文件

void SMyFaceTrackerPanel::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            SAssignNew(TrackerViewer, STrackerImageViewer)
            .ShouldDrawPoints(true)
            .ShouldDrawCurves(true)
            .DefaultCurvesColor(FLinearColor(0.2f, 0.8f, 0.2f, 1.0f))
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.0f)
        [
            SNew(SButton)
            .Text(FText::FromString(TEXT("Refresh View")))
            .OnClicked_Lambda([this]() -> FReply
            {
                RefreshView();
                return FReply::Handled();
            })
        ]
    ];
}

void SMyFaceTrackerPanel::SetCurveDataController(TSharedPtr<FMetaHumanCurveDataController> InDataController)
{
    if (TrackerViewer.IsValid())
    {
        TrackerViewer->SetDataControllerForCurrentFrame(InDataController);
    }
}

void SMyFaceTrackerPanel::RefreshView()
{
    if (TrackerViewer.IsValid())
    {
        TrackerViewer->UpdateDisplayedDataForWidget();
    }
}
```

## 模块依赖

要使用 `MetaHumanImageViewerEditor` 模块的功能，你的模块需要在 `.Build.cs` 文件中添加以下依赖。注意，下表仅列出了不常见或特定的依赖项。

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供核心的 `STrackerImageViewer` 和 `SABImage` 控件。 |
| `MetaHumanCore` | 提供基础类型、工具和核心功能。 |
| `MetaHumanIdentity` | 提供 MetaHuman 角色身份资产及其相关功能。 |
| `MetaHumanPerformance` | 提供将动画应用到 MetaHuman 角色的功能。 |
| `MetaHumanFaceContourTracker` | 提供面部轮廓跟踪的算法和数据结构。 |
| `MetaHumanFaceFittingSolver` | 提供面部拟合解算器。 |
| `MetaHumanFaceAnimationSolver` | 提供面部动画解算器。 |
| `MetaHumanCaptureDataEditor` | 提供捕捉数据（视频、深度序列）的编辑器支持。 |
| `MetaHumanSequencer` | 提供与 Unreal Sequencer 的深度集成。 |
| `MetaHumanPipeline` | 提供处理管线的基础架构。 |
| `MetaHumanConfig` | 提供插件配置管理。 |
| `MetaHumanPlatform` | 提供平台相关的特定功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体跟踪时，禁用关卡序列导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了MetaHuman角色上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体跟踪时过滤可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了Sequencer的缓存问题。 |

### 维护评价

-   **活跃维护**：该插件由 Epic Games 官方维护，是 MetaHuman 工具链的核心部分。从 Git 历史看，在 2026 年 5 月仍有连续的功能更新和重要的 Bug 修复，表明其处于**活跃维护**状态。
-   **功能复杂**：插件包含大量模块，涵盖从底层算法到上层编辑器工具的完整栈，代码量巨大（544个源文件），属于“xlarge”级别。
-   **官方支持**：作为 Epic 官方插件，其稳定性和与引擎新版本的兼容性有较高保障。
-   **依赖性强**：由于其深度集成于 MetaHuman 生态，单独使用可能需要同时启用 MetaHuman 角色及相关插件。
-   **推荐使用**：对于所有需要进行高质量 MetaHuman 面部动画制作，特别是使用深度/立体捕捉数据的项目，**强烈推荐**使用此插件。它是实现从表演到角色动画端到端工作流的官方解决方案。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) （Epic MetaHuman Animator 文档）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanControlsConversionTest) （插件内包含 `MetaHumanControlsConversionTest` 测试模块）