# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产，材质模板，测试资源） |
| 模块 | `MetaHumanImageViewerEditor` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime), `MeshTrackerInterface` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-11-01 |
| 年龄标签 | 📜 约5年 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一套完整的官方工具包，旨在简化在虚幻引擎中创建、驱动和动画化高保真数字人类（MetaHuman）的完整工作流程。它不仅仅是“官方工具包”，而是一个集成的深度学习和计算摄影系统。其核心价值在于提供从原始捕获数据（如 iPhone 或多摄像头阵列的视频/深度数据）到最终可驱动的数字人类资产的端到端管线。该插件解决了以下关键问题：

1.  **面部数据驱动与动画解算**：能够从视频或深度数据中精确追踪面部关键点，并解算出对应的面部控制曲线，用于驱动 MetaHuman 骨骼动画。
2.  **身份与性能的分离**：通过 `MetaHumanIdentity` 等模块，允许用户独立创建或调整数字人类的静态身份（面部形状），然后应用不同的表演数据。
3.  **深度感知与三维重建**：集成深度生成器和网格追踪器，能够从二维数据推断三维空间信息，提升面部拟合的精度。
4.  **批量处理与自动化**：提供批量处理器和自动化管线，支持对大量表演数据进行高效的动画生成。
5.  **影视级工作流集成**：包含与 Sequencer 深度集成的模块，支持在虚拟制片环境中实时驱动和编辑 MetaHuman 表演。

## 使用场景

-   你是一位影视或游戏美术师，需要从演员的多角度表演视频中快速生成高质量的面部动画，用于游戏过场或电影角色 → 使用 `MetaHumanFaceContourTracker` 和 `MetaHumanFaceAnimationSolver`。
-   你正在开发一个需要大量不同数字人类角色的项目，希望基于一套基础模型，通过不同的表演数据生成多样化的角色表现 → 使用 `MetaHumanIdentity` 创建身份，结合 `MetaHumanPerformance` 应用表演。
-   你在进行虚拟制片，需要在 Sequencer 中实时预览和编辑 MetaHuman 角色的面部表情 → 使用 `MetaHumanSequencer` 模块。
-   你需要处理来自 iPhone TrueDepth 摄像头或专用深度相机的深度视频数据，以创建更精确的 3D 面部几何体 → 使用 `MetaHumanDepthGenerator`。
-   你希望基于音频文件（如语音）自动为 MetaHuman 生成口型同步动画 → 使用 `MetaHumanSpeech2Face`。

## 蓝图用法

基于源码分析，以下是当前模块 `MetaHumanImageViewerEditor` 中可暴露的核心蓝图相关 API。注意，该插件主要是一个编辑器工具套件，大部分功能在编辑器和专用资产中通过 UI 操作，直接暴露给运行时蓝图的节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCameraCalibration` | 设置摄像机标定数据，用于在视口中正确定位画面平面。 | `UMetaHumanFootageComponent` |
| `SetFootageResolution` | 当没有已知标定时，设置画面分辨率以用于定位。 | `UMetaHumanFootageComponent` |
| `SetMediaTextures` | 设置代表颜色和深度数据的媒体纹理。 | `UMetaHumanFootageComponent` |
| `SetDepthRange` | 设置深度数据的近远平面范围。 | `UMetaHumanFootageComponent` |
| `ShowColorChannel` | 在指定的 AB 视图模式下显示颜色通道。 | `UMetaHumanFootageComponent` |
| `SetDepthTexture` | 设置用于显示网格的深度纹理。 | `UMetaHumanDepthMeshComponent` |
| `SetCameraCalibration` | 设置用于计算深度网格位置的摄像机标定。 | `UMetaHumanDepthMeshComponent` |
| `SetDepthRange` | 设置深度显示的近远平面。 | `UMetaHumanDepthMeshComponent` |
| `SetViewMode` | 设置此组件的 ShowFlags 以匹配给定的视图模式索引。 | `UMetaHumanSceneCaptureComponent2D` |
| `SetViewportClient` | 设置控制此组件的视口客户端。 | `UMetaHumanSceneCaptureComponent2D` |
| `SetDataControllerForCurrentFrame` | 为当前帧设置曲线数据控制器，驱动图像查看器显示。 | `STrackerImageViewer` |
| `UpdateDisplayedDataForWidget` | 更新此控件上显示的点和曲线数据。 | `STrackerImageViewer` |
| `SetEditCurvesAndPointsEnabled` | 设置是否允许用户通过交互编辑点和曲线。 | `STrackerImageViewer` |

### 使用示例（蓝图描述）

由于 `STrackerImageViewer` 是一个 Slate 控件，通常不直接在标准游戏蓝图图表中使用。以下示例描述了在编辑器工具蓝图或 Slate UI 中如何配置一个 `UMetaHumanFootageComponent` 来显示带有深度叠加的视频画面：

1.  在场景中放置一个 Actor（如 `AActor`）。
2.  添加一个 `UMetaHumanFootageComponent` 组件。
3.  通过“BeginPlay”或某个自定义事件，调用该组件的 `SetCameraCalibration` 函数，传入一个有效的 `UCameraCalibration` 资产。
4.  接着，调用 `SetMediaTextures` 函数，分别传入颜色纹理和深度纹理（可来自媒体源或渲染目标）。
5.  为了查看深度信息，调用 `ShowColorChannel` 并传入 `EABImageViewMode::A`（假设使用 A 通道显示颜色），然后在同一视图模式下通过材质参数或后续函数调用启用深度显示。
6.  最后，调整摄像机或使用 `GetFootageScreenRect` 函数获取的输出来对齐视口，以完美观察画面。

## C++ 用法

### 头文件引入

```cpp
// 包含图像查看器控件
#include "STrackerImageViewer.h"

// 包含画面组件
#include "MetaHumanFootageComponent.h"

// 包含深度网格组件
#include "MetaHumanDepthMeshComponent.h"
```

### 基本用法

以下示例展示了如何在编辑器工具代码中创建和使用一个 `STrackerImageViewer` 控件。这通常用于构建自定义的 MetaHuman 面部追踪编辑器界面。

```cpp
// 来源：假设的编辑器工具代码，概念基于 Public/STrackerImageViewer.h
#include "STrackerImageViewer.h"
#include "MetaHumanCurveDataController.h" // 假设的数据控制器

class SMyFaceTrackerPanel : public SCompoundWidget
{
    SLATE_BEGIN_ARGS(SMyFaceTrackerPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        // 创建图像查看器控件
        ChildSlot
        [
            SNew(STrackerImageViewer)
            .Image(FCoreStyle::Get().GetDefaultBrush()) // 使用默认画刷或实际纹理
            .ShouldDrawPoints(true)
            .ShouldDrawCurves(true)
            .DefaultCurvesColor(FLinearColor::Green)
        ];

        // 在初始化后，设置数据控制器
        // 假设 InCurveDataController 是从追踪数据创建的
        TSharedPtr<FMetaHumanCurveDataController> InCurveDataController = ...;
        TrackerImageViewer->SetDataControllerForCurrentFrame(InCurveDataController);
        TrackerImageViewer->UpdateDisplayedDataForWidget();
    }

    TSharedPtr<STrackerImageViewer> TrackerImageViewer;
};
```

**来源文件路径**: `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/STrackerImageViewer.h`

### 进阶用法

结合 `UMetaHumanFootageComponent` 和 `UMetaHumanDepthMeshComponent`，在编辑器工具中构建一个带有深度网格叠加的预览窗口。

```cpp
// 来源：假设的编辑器预览 Actor 代码，基于多个组件头文件
#include "MetaHumanFootageComponent.h"
#include "MetaHumanDepthMeshComponent.h"
#include "Engine/TextureRenderTarget2D.h"

class AMetaHumanPreviewActor : public AActor
{
    UPROPERTY(VisibleAnywhere)
    UMetaHumanFootageComponent* FootageComponent;

    UPROPERTY(VisibleAnywhere)
    UMetaHumanDepthMeshComponent* DepthMeshComponent;

public:
    void SetupPreview(UTexture* ColorTexture, UTexture* DepthTexture, UCameraCalibration* Calibration)
    {
        FootageComponent = CreateDefaultSubobject<UMetaHumanFootageComponent>(TEXT("Footage"));
        DepthMeshComponent = CreateDefaultSubobject<UMetaHumanDepthMeshComponent>(TEXT("DepthMesh"));

        // 配置画面组件
        FootageComponent->SetCameraCalibration(Calibration);
        FootageComponent->SetMediaTextures(ColorTexture, DepthTexture, true);
        FootageComponent->SetDepthRange(10, 50);

        // 配置深度网格组件
        DepthMeshComponent->SetCameraCalibration(Calibration);
        DepthMeshComponent->SetDepthTexture(DepthTexture);
        DepthMeshComponent->SetDepthRange(10.0f, 55.5f);
        // 根据深度纹理的分辨率设置网格大小
        if (DepthTexture->GetResource())
        {
            int32 Width = DepthTexture->GetSizeX();
            int32 Height = DepthTexture->GetSizeY();
            DepthMeshComponent->SetSize(Width, Height);
        }
    }
};
```

**来源文件路径**:
- `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/MetaHumanFootageComponent.h`
- `Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor/Public/MetaHumanDepthMeshComponent.h`

## Demo 示例

以下是一个最小化的 C++ 示例，演示了如何创建一个显示 MetaHuman 面部追踪曲线的 Slate 控件。

**头文件 (MyFaceViewerWidget.h):**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class STrackerImageViewer;
class FMetaHumanCurveDataController;

class SMyFaceViewerWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyFaceViewerWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);
    void SetCurveData(TSharedPtr<FMetaHumanCurveDataController> InData);

private:
    TSharedPtr<STrackerImageViewer> ImageTracker;
};
```

**源文件 (MyFaceViewerWidget.cpp):**
```cpp
#include "MyFaceViewerWidget.h"
#include "STrackerImageViewer.h"
#include "MetaHumanCurveDataController.h"

void SMyFaceViewerWidget::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SAssignNew(ImageTracker, STrackerImageViewer)
        .ShouldDrawPoints(true)
        .ShouldDrawCurves(true)
    ];
}

void SMyFaceViewerWidget::SetCurveData(TSharedPtr<FMetaHumanCurveDataController> InData)
{
    if (ImageTracker.IsValid() && InData.IsValid())
    {
        ImageTracker->SetDataControllerForCurrentFrame(InData);
        ImageTracker->UpdateDisplayedDataForWidget();
    }
}
```

## 模块依赖

本插件模块众多，且许多依赖于 Epic 内部的专有库（如 `MetaHumanCoreTechLib`）和其他高级插件。以下是 `MetaHumanImageViewerEditor` 模块的一些特殊依赖，这些是使用者在构建依赖于该插件的编辑器工具时需要特别关注的。

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供本模块核心的图像查看控件（如 `SABImage`, `STrackerImageViewer`）。 |
| `MetaHumanCaptureDataEditor` | 提供捕获数据资产的编辑器支持。 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分。 |
| `ControlRigDeveloper` | 用于编辑器中的 Control Rig 开发。 |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格工具的公共功能。 |

*注意：该插件还深度依赖 `UnrealEd` 等编辑器模块，以及内部项目（如 MetaHuman Core Tech Library）的功能，这些在上述表中已省略，但在实际模块的 `.Build.cs` 文件中会声明。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复身体追踪启用时关卡序列导出功能的禁用问题 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象，避免干扰。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MetaHuman Animator] 支持为现有网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 中的缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的、面向未来的数字人类核心创作工具。

-   **活跃维护**：从最近的提交记录来看，插件在**2026年5月**仍有频繁且实质性的功能更新和 Bug 修复（如导出、渲染修复、身体追踪集成）。
-   **持续进化**：提交信息表明该插件正在积极整合新的工作流（如身体追踪），并不断优化现有功能（如 Sequencer 集成）。
-   **官方支持**：作为 Epic 的官方工具，拥有最高的维护优先级和长期支持保障。
-   **状态稳定**：`.uplugin` 中未标记为 Beta 或 Experimental，表明其核心功能已达到生产就绪状态。
-   **推荐使用**：强烈推荐所有需要创建高质量数字人类角色的虚幻引擎项目使用此插件。它是实现该目标最直接、最强大的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/meta-human-animator-in-unreal-engine/) (请访问 Epic 官方文档网站获取最新信息)