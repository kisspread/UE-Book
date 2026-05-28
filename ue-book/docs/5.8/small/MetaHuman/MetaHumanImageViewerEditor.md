# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数字人动画师工具包 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器资产、材质模板、数据资产） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 N 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

基于源码分析，MetaHuman Animator 是一个用于创建 MetaHuman 角色动画的完整工具集。它并非一个简单的运行时插件，而是一套庞大的编辑器和数据处理管线，旨在解决从真实演员表演到虚拟数字人角色动画转换的整个流程问题。

其核心功能包括：
1.  **面部动作捕捉与处理**：支持从多种来源（如深度摄像头、iPhone TrueDepth、视频）捕获面部数据，并通过一系列模块（如 `MetaHumanFaceContourTracker`, `MetaHumanFaceFittingSolver`, `MetaHumanFaceAnimationSolver`）进行跟踪、拟合和求解。
2.  **数字人身份创建与编辑**：`MetaHumanIdentity` 模块用于管理数字人的面部身份、拓扑和骨骼控制绑定，是连接捕获数据与最终动画资产的桥梁。
3.  **数据可视化与编辑**：`MetaHumanImageViewerEditor` 等模块提供在编辑器中查看捕获画面、深度图、轮廓曲线，并进行交互式编辑的能力，这是精确调整动画结果的关键。
4.  **动画序列生成**：最终将处理后的动作数据转换为可驱动 MetaHuman 骨骼的动画序列（Sequencer 或自定义性能资产）。

**为什么存在**：MetaHuman Animator 存在是为了让开发者能够高效、精确地将真实人类的细腻表演“翻译”成高质量的 MetaHuman 虚拟角色动画，这是电影、游戏和实时虚拟制作中创造逼真数字人的核心需求。

## 使用场景

-   你需要将真实演员的面部表演驱动 MetaHuman 角色，用于影视级虚拟制片或游戏过场动画。
-   你使用 iPhone 的 FaceID 摄像头或专业深度摄像头（如 LiDAR）进行面部动作捕捉，并希望将其集成到 UE5 工作流中。
-   你需要对自动捕捉生成的面部曲线和轮廓进行手动校正，以达到完美的动画效果。
-   你正在开发一个需要批量处理大量面部表演数据的系统，例如生成 NPC 动画。
-   你希望将音频（语音）直接转换为面部动画（通过 `MetaHumanSpeech2Face` 模块）。

## 蓝图用法

由于该插件主要由编辑器模块和运行时数据组件构成，其蓝图接口主要集中在数据组件和资产操作上。核心节点多与设置捕获数据、控制显示和驱动动画相关。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Camera Calibration` | 根据相机校准数据，设置素材显示平面的位置和比例。 | `UMetaHumanFootageComponent` |
| `Set Footage Resolution` | 在没有校准数据时，通过指定素材分辨率来设置显示平面。 | `UMetaHumanFootageComponent` |
| `Set Media Texture` | 设置用于显示的颜色和深度纹理。 | `UMetaHumanFootageComponent` |
| `Set View Mode` | 设置 AB 图像查看器的视图模式（单视图/双视图/分屏等）。 | `SABImage` (Slate Widget) |
| `Set Data Controller For Current Frame` | 为当前帧设置曲线数据控制器，用于显示和编辑轮廓线。 | `STrackerImageViewer` |
| `Set Edit Curves And Points Enabled` | 启用或禁用用户对曲线和控制点的交互式编辑。 | `STrackerImageViewer` |

### 使用示例（蓝图描述）

在一个自定义的 MetaHuman 动画编辑器面板中，可以这样使用：
1.  **创建并添加** `UMetaHumanFootageComponent` 组件到场景中的 Actor。
2.  调用 `Set Media Texture` 节点，将捕获流程中得到的彩色纹理和深度纹理分别传入。
3.  调用 `Set Camera Calibration` 节点，传入对应的相机校准数据（`UCameraCalibration` 资产），使画面正确对齐。
4.  为了在自定义 Slate 面板中查看素材，需要创建一个 `SABImage` 或 `STrackerImageViewer` 类型的 Slate 控件，并调用其 `Set Textures` 或 `Set View Mode` 等方法来配置显示。

## C++ 用法

该插件的 C++ 用法通常涉及构建自定义编辑器工具或深度集成 MetaHuman 处理管线。

### 头文件引入

```cpp
// 主要组件和查看器
#include "MetaHumanFootageComponent.h"
#include "STrackerImageViewer.h"
#include "SABImage.h"
#include "MetaHumanDepthMeshComponent.h"

// 数据控制器和操作
#include "MetaHumanCurveDragOperations.h"
```

### 基本用法

**在场景中显示捕获的素材画面**（源自 `UMetaHumanFootageComponent` 的使用模式）：

```cpp
// 假设在一个自定义的 Actor 或 EditorUtilityWidget 中
UPROPERTY()
TObjectPtr<UMetaHumanFootageComponent> FootageComponent;

// 创建并初始化组件
FootageComponent = NewObject<UMetaHumanFootageComponent>(GetOwningActor());
FootageComponent->RegisterComponent();
FootageComponent->AttachToComponent(GetOwningActor()->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);

// 设置数据
FootageComponent->SetMediaTextures(ColorTexture, DepthTexture);
FootageComponent->SetCameraCalibration(SelectedCameraCalibrationAsset);
FootageComponent->ShowColorChannel(EABImageViewMode::A);
```

**在 Slate 窗口中嵌入带曲线编辑功能的图像查看器**（源自 `STrackerImageViewer` 的构建）：

```cpp
// 在构建 Slate UI 的函数中
SNew(STrackerImageViewer)
    .Image(MyBrushWithTexture)
    .ShouldDrawPoints(true)
    .ShouldDrawCurves(true)
    .DefaultCurvesColor(FLinearColor::Green)
    // ... 其他属性
```

### 进阶用法

**实现自定义的曲线拖拽操作**（源自 `IMetaHumanEditorDragOperation` 接口和 `FMetaHumanCurveEditorDelayedDrag`）：

```cpp
// 自定义拖拽操作
class FMyCustomDragOp : public IMetaHumanEditorDragOperation
{
public:
    virtual void OnBeginDrag(const FVector2D& InGeometry, const FPointerEvent& InMouseEvent) override { /* ... */ }
    virtual void OnDrag(const FVector2D& InGeometry, const FPointerEvent& InMouseEvent) override { /* ... */ }
    virtual void OnEndDrag() override { /* ... */ }
    virtual void OnDragOperationPaint(const FGeometry& InAllottedGeometry, FSlateWindowElementList& OutDrawElements, int32 InPaintOnLayerId) override { /* ... */ }
    // 可能还需要持有 FMetaHumanCurveDataController 的指针来实际修改数据
};

// 在某个 Slate Widget 处理鼠标按下时，创建延迟拖拽
FVector2D MousePos = InMouseEvent.GetScreenSpacePosition();
DragOperation = FMetaHumanCurveEditorDelayedDrag(MousePos, EKeys::LeftMouseButton);
DragOperation.DragImpl = MakeUnique<FMyCustomDragOp>();
// ... 在 OnMouseMove 中调用 DragImpl->OnDrag()
```

## Demo 示例

一个最小示例，展示如何在编辑器工具中创建一个 `UMetaHumanFootageComponent` 并设置其属性。

```cpp
// MyEditorTool.h
#pragma once
#include "Components/ActorComponent.h"
#include "MyEditorTool.generated.h"

class UMetaHumanFootageComponent;
class UCameraCalibration;

UCLASS(Blueprintable, BlueprintType)
class UMyEditorTool : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyEditorTool();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "MyTool")
    void SetupFootageDisplay(UCameraCalibration* InCalibration, UTexture* InColorTex, UTexture* InDepthTex);

private:
    UPROPERTY()
    TObjectPtr<UMetaHumanFootageComponent> FootageDisplay;
};
```

```cpp
// MyEditorTool.cpp
#include "MyEditorTool.h"
#include "MetaHumanFootageComponent.h"
#include "Engine/CameraCalibration.h"

UMyEditorTool::UMyEditorTool()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyEditorTool::BeginPlay()
{
    Super::BeginPlay();

    // 创建并附加 MetaHuman 素材显示组件
    FootageDisplay = NewObject<UMetaHumanFootageComponent>(GetOwner());
    if (FootageDisplay)
    {
        FootageDisplay->RegisterComponent();
        FootageDisplay->AttachToComponent(GetOwner()->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
        // 可以在此处设置一些默认值
        FootageDisplay->SetFootageResolution(FVector2D(1920, 1080));
    }
}

void UMyEditorTool::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (FootageDisplay)
    {
        FootageDisplay->DestroyComponent();
        FootageDisplay = nullptr;
    }
    Super::EndPlay(PlayReason);
}

void UMyEditorTool::SetupFootageDisplay(UCameraCalibration* InCalibration, UTexture* InColorTex, UTexture* InDepthTex)
{
    if (!FootageDisplay || !InCalibration)
    {
        return;
    }

    // 设置相机校准以正确定位画面
    FootageDisplay->SetCameraCalibration(InCalibration);
    // 设置用于显示的纹理
    FootageDisplay->SetMediaTextures(InColorTex, InDepthTex, true);
    // 启用颜色通道显示
    FootageDisplay->ShowColorChannel(EABImageViewMode::A);
    // 可以设置深度显示范围
    FootageDisplay->SetDepthRange(10, 50);
}
```

## 模块依赖

MetaHuman Animator 插件包含大量模块，以下是当前文档聚焦的 `MetaHumanImageViewerEditor` 模块的依赖情况。请注意，使用该插件的其他部分（如面部求解器）会依赖更多的模块。

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供本模块的核心查看器控件 |
| `MetaHumanSDKEditor` | 提供与 MetaHuman SDK 相关的编辑器功能 |
| `ControlRigDeveloper` | 用于操作和查看 Control Rig 相关资产 |
| `SkeletalMeshUtilitiesCommon` | 提供骨骼网格体相关的通用工具函数 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 在启用了身体追踪时，禁用关卡序列的导出功能。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复了 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪期间，过滤掉某些可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | [MHA] 为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复了 Sequencer 的缓存问题。 |

### 维护评价

MetaHuman Animator 是 Epic Games 官方维护的核心数字人工具集。尽管其确切的创建时间未知，但从最近的提交记录来看，该插件仍在**非常活跃地维护和更新**。最近的更新集中在修复渲染问题、优化身体追踪集成以及改进动画导出流程，表明其功能仍在不断丰富和完善。

对于需要创建高质量 MetaHuman 动画的项目，**强烈推荐使用**。这是一个成熟且得到官方持续支持的大型工具链。需要注意的是，由于其庞大的模块结构和复杂的管线，初次学习和集成可能需要投入较多时间。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (无公开链接)
- [测试用例]() (通常位于引擎测试目录，如 `Engine/Tests/`)