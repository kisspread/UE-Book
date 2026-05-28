# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | 元人动画工具 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源、插件内容） |
| 模块 | `MetaHumanImageViewerEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-07-26 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具包。`MetaHumanImageViewerEditor` 模块是该工具包的**核心图像查看与编辑组件**，主要用于在虚幻编辑器内查看、对比和编辑来自 MetaHuman 制作流程中的各类素材与数据。

该模块的核心功能是提供一个高性能的编辑器内视口（Viewport），用于：
1.  **显示与对比素材**：查看原始拍摄视频（Footage）、面部追踪曲线（Contour）、深度数据（Depth）等，并支持双视图（A/B 对比）模式。
2.  **交互式编辑**：直接在视口中对面部特征曲线（Facial Contour）的控制点和样条线进行选择、移动、添加/删除等编辑操作。
3.  **集成数据可视化**：将 3D 深度信息、追踪结果等数据实时叠加在 2D 视频画面之上，帮助用户精准定位和调整。

它解决了在 MetaHuman 角色制作（特别是基于视频的 MetaHuman Animator 流程）中，需要在 2D 画面与 3D 数据之间进行反复对照、交互式调试的痛点，是连接视频采集数据与角色生成引擎的关键桥梁。

## 使用场景

-   **使用 MetaHuman Animator 从视频创建角色动画**：在“MetaHuman Animator”窗口中，使用此模块查看导入的参考视频、追踪面部特征点、并预览动画结果。
-   **校正面部追踪数据**：当自动追踪的面部曲线不准确时，可以在此视口中手动微调控制点的位置。
-   **检查深度信息**：将深度传感器或AI生成的深度数据作为网格（Mesh）或颜色映射叠加在视频上，以验证深度信息的准确性。
-   **进行 A/B 对比**：并排或叠加查看原始视频、渲染结果或不同处理阶段的输出，以评估调整效果。
-   **开发自定义 MetaHuman 工具**：在开发需要处理视频、深度或面部追踪数据的编辑器工具时，可以复用或扩展本模块提供的视口和交互功能。

## 蓝图用法

本模块主要提供编辑器扩展和 Slate UI 控件，其核心功能（如曲线编辑、视口控制）主要通过 C++ 在编辑器模块内部使用，而非直接暴露给蓝图。但提供了一些可供蓝图（在编辑器工具或资产中）使用的 UObject 组件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCameraCalibration` | 设置镜头校准数据，用于正确定位和缩放素材平面。 | `UMetaHumanFootageComponent` |
| `SetFootageResolution` | 当未知镜头校准时，手动设置素材分辨率来定位平面。 | `UMetaHumanFootageComponent` |
| `SetMediaTextures` | 设置用于显示颜色和深度数据的媒体纹理。 | `UMetaHumanFootageComponent` |
| `SetFootageVisible` | 设置特定视图模式下素材平面的可见性。 | `UMetaHumanFootageComponent` |
| `SetDepthTexture` | 设置用于显示深度网格的深度纹理。 | `UMetaHumanDepthMeshComponent` |
| `SetDepthRange` | 设置深度显示的范围（近平面和远平面）。 | `UMetaHumanDepthMeshComponent` |
| `SetSize` | 设置深度网格的分辨率。 | `UMetaHumanDepthMeshComponent` |

### 使用示例（蓝图描述）

在一个用于展示 MetaHuman 面部动画的 Actor 蓝图中：
1.  添加一个 `UMetaHumanFootageComponent` 组件。
2.  在构造脚本或初始化事件中，调用 `SetFootageResolution` 或 `SetCameraCalibration` 来设置素材的显示位置。
3.  调用 `SetMediaTextures`，将加载的颜色视频纹理和深度纹理传入。
4.  使用 `ShowColorChannel` 或 `SetViewMode` 来切换查看颜色数据或深度数据。

## C++ 用法

### 头文件引入

```cpp
// 核心图像查看器
#include "STrackerImageViewer.h"
#include "SABImage.h"
// 组件
#include "MetaHumanFootageComponent.h"
#include "MetaHumanDepthMeshComponent.h"
// 编辑器工具
#include "MetaHumanCurveDataController.h" // 假设的控制器头文件
```

### 基本用法：创建和使用轨迹图像查看器 (STrackerImageViewer)

`STrackerImageViewer` 是用于显示和编辑面部追踪曲线的 Slate 控件。

```cpp
// 在自定义的 Slate 面板中创建查看器
TSharedPtr<STrackerImageViewer> TrackerViewer;

SAssignNew(TrackerViewer, STrackerImageViewer)
    .Image(MyTextureBrush) // 设置背景图像
    .ShouldDrawPoints(true)
    .ShouldDrawCurves(true)
    .DefaultCurvesColor(FLinearColor::Green)
    .DefaultPointsColor(FLinearColor::Green);

// 将其添加到某个容器中
MyVerticalBox->AddSlot()
[
    TrackerViewer.ToSharedRef()
];
```

```cpp
// 在获得一帧的追踪数据后，更新查看器
// 假设 GetCurveDataControllerForFrame 返回当前帧的控制器
TSharedPtr<FMetaHumanCurveDataController> Controller = GetCurveDataControllerForFrame(FrameIndex);
TrackerViewer->SetDataControllerForCurrentFrame(Controller);
TrackerViewer->UpdateDisplayedDataForWidget(); // 刷新显示
```
*来源：基于 `STrackerImageViewer.h` 接口推断的用法。*

### 基本用法：使用 AB 图像对比 (SABImage)

`SABImage` 继承自 `STrackerImageViewer`，增加了双视图对比功能。

```cpp
// 创建 AB 图像查看器
TSharedPtr<SABImage> ABViewer;
SAssignNew(ABViewer, SABImage)
    .ShouldDrawPoints(false)
    .ShouldDrawCurves(false);

// 设置要对比的两个纹理
ABViewer->SetTextures(ColorTexture, DepthOrRenderedTexture);

// 设置视图模式为左右分屏对比
ABViewer->SetViewMode(EABImageViewMode::ABSide);
```
*来源：基于 `SABImage.h` 接口推断的用法。*

### 进阶用法：在场景中显示素材平面 (UMetaHumanFootageComponent)

`UMetaHumanFootageComponent` 用于在 3D 视口中正确放置和显示 2D 素材。

```cpp
// 假设在某个 Actor 的构造函数或初始化函数中
UMetaHumanFootageComponent* FootageComp = CreateDefaultSubobject<UMetaHumanFootageComponent>(TEXT("FootagePlane"));

// 方式一：已知镜头校准
UCameraCalibration* Calibration = LoadObject<UCameraCalibration>(nullptr, TEXT("/Game/Cameras/MyCalibration"));
FootageComp->SetCameraCalibration(Calibration);
FootageComp->SetCamera(TEXT("CameraA"));

// 方式二：未知校准，仅知道分辨率
FootageComp->SetFootageResolution(FVector2D(1920, 1080));

// 加载媒体纹理
UTexture* ColorTex = LoadObject<UTexture>(nullptr, TEXT("/Game/Videos/MyColorVideo"));
UTexture* DepthTex = LoadObject<UTexture>(nullptr, TEXT("/Game/Videos/MyDepthVideo"));
FootageComp->SetMediaTextures(ColorTex, DepthTex);

// 设置深度显示范围（单位可能是厘米）
FootageComp->SetDepthRange(10, 50);
```
*来源：基于 `MetaHumanFootageComponent.h` 和 `MetaHumanDepthMeshComponent.h` 的公开接口。*

## Demo 示例

一个最小的 Actor 示例，用于在场景中显示一个带校准的素材平面。

**FootageDisplayActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "FootageDisplayActor.generated.h"

class UMetaHumanFootageComponent;
class UCameraCalibration;
class UTexture;

UCLASS()
class AFootageDisplayActor : public AActor
{
    GENERATED_BODY()

public:
    AFootageDisplayActor();

protected:
    UPROPERTY(VisibleAnywhere, Category = "Footage")
    TObjectPtr<UMetaHumanFootageComponent> FootageComponent;

    // 在编辑器中设置这些资产
    UPROPERTY(EditAnywhere, Category = "Footage|Assets")
    TObjectPtr<UCameraCalibration> CameraCalibrationAsset;

    UPROPERTY(EditAnywhere, Category = "Footage|Assets")
    FString CameraName = TEXT("CameraA");

    UPROPERTY(EditAnywhere, Category = "Footage|Assets")
    TObjectPtr<UTexture> ColorTexture;

    UPROPERTY(EditAnywhere, Category = "Footage|Assets")
    TObjectPtr<UTexture> DepthTexture;

    UPROPERTY(EditAnywhere, Category = "Footage|Settings")
    int32 DepthNear = 10;

    UPROPERTY(EditAnywhere, Category = "Footage|Settings")
    int32 DepthFar = 50;
};
```

**FootageDisplayActor.cpp**
```cpp
#include "FootageDisplayActor.h"
#include "MetaHumanFootageComponent.h"
#include "CameraCalibration.h"

AFootageDisplayActor::AFootageDisplayActor()
{
    // 创建素材组件
    FootageComponent = CreateDefaultSubobject<UMetaHumanFootageComponent>(TEXT("FootagePlane"));
    RootComponent = FootageComponent;
}

// 可以在 PostInitializeComponents 或蓝图的 BeginPlay 中调用初始化
void AFootageDisplayActor::InitializeFootage()
{
    if (CameraCalibrationAsset)
    {
        FootageComponent->SetCameraCalibration(CameraCalibrationAsset);
        FootageComponent->SetCamera(CameraName);
    }
    else if (ColorTexture)
    {
        // 如果没有校准，尝试从纹理推断分辨率（示例）
        FootageComponent->SetFootageResolution(FVector2D(ColorTexture->GetSizeX(), ColorTexture->GetSizeY()));
    }

    FootageComponent->SetMediaTextures(ColorTexture, DepthTexture);
    FootageComponent->SetDepthRange(DepthNear, DepthFar);
}
```

## 模块依赖

从提供的 Build.cs 依赖信息分析，`MetaHumanImageViewerEditor` 模块本身是一个相对独立的视图组件。要在你的项目中使用它，你的模块需要在 `.Build.cs` 文件中添加以下依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "MetaHumanImageViewerEditor",
    // 根据你使用的功能，可能还需要：
    // "MetaHumanCaptureData", // 如果处理采集数据
    // "CameraCalibration",    // 如果使用镜头校准
});
```

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

从 Git 历史看，该插件（作为 MetaHuman Animator 的一部分）处于**非常活跃**的维护状态。

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 修复：启用身体追踪时禁用关卡序列导出功能 |
| 2025-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复：解决 MetaHuman 上的渲染瑕疵问题 |
| 2025-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 优化：在身体追踪模式下过滤可视化对象 |
| 2025-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 功能：支持为已有网格导出动画序列 |
| 2025-05-20 | `35537544` | Fix sequencer caching issues | 修复：解决 Sequencer 缓存导致的问题 |

### 维护评价

-   **活跃维护**：最近 5 次提交均在 2025 年 5 月内，且包含功能增强和重要的 Bug 修复，表明 Epic Games 正在积极维护此工具。
-   **核心功能**：作为 MetaHuman 官方工具链的核心部分，其稳定性和功能完整性有保障。
-   **与最新 UE 版本同步**：提交记录显示其随虚幻引擎主线一起更新。
-   **推荐使用**：**强烈推荐**所有使用 MetaHuman Animator 工作流的项目使用此模块。它是该工作流不可或缺的一部分。对于需要自定义视频或面部追踪数据处理管线的开发者，本模块也提供了强大的可扩展基础。
-   **注意**：此插件默认未启用 (`"Installed": false`)，需要在项目设置的插件列表中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanImageViewerEditor)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/metahuman-animator-in-unreal-engine/) (MetaHuman Animator 整体文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Tests) (通常位于插件根目录的 `Tests` 文件夹下)