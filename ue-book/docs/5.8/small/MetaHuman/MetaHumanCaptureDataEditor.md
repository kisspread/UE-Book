# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具、配置） |
| 模块 | `MeshTrackerInterface` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanPlatform` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanToolkit` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 🆕（约 < 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方提供的 MetaHuman 工具套件。它不仅仅是一个插件，而是一个完整的管线，旨在将真实的面部表演数据（如来自 iPhone 或专业动捕设备的视频）转化为可驱动 MetaHuman 角色的动画资产。该插件解决了从原始捕获数据到高质量面部动画的端到端处理问题，涵盖了数据导入、特征点追踪、动画求解、资产编辑和最终输出等各个环节。

核心价值在于它提供了自动化工具链，极大地简化了创建逼真数字人动画的技术门槛和工作流程，使艺术家和开发者能够高效地将真实世界的表演赋予虚拟角色。

## 使用场景

- **影视与游戏过场动画制作**：你需要为一个逼真的数字人角色创建基于演员真实表演的面部动画。
- **虚拟直播与实时应用**：你希望使用 iPhone 或其他摄像头，实时或离线驱动 MetaHuman 角色进行直播或交互。
- **大规模内容生产**：你需要批量处理大量的面部表演数据，生成对应的动画序列。
- **角色定制与资产创建**：你需要从多张照片或视频中创建一个基础的 MetaHuman 角色身份（Identity）。

## 蓝图用法

`MetaHumanCaptureDataEditor` 模块提供了一些用于在编辑器中处理捕获数据的UI工具和实用函数。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HandleSourceDataChanged` | 当源捕获数据（如影片或音频）发生更改时，更新相关UI控件（如下拉框选项、时间范围）。 | `SMetaHumanCameraCombo` |
| `OnSelectionChanged` | 当用户在相机选择下拉框中选择一个新选项时触发的回调。 | `SMetaHumanCameraCombo` |
| `CreatePreviewComponent` | 为指定的捕获数据资产（`UCaptureData`）创建并返回一个用于在编辑器中预览的场景组件。 | `MetaHumanCaptureDataUtils` |

### 使用示例（蓝图描述）

1.  **创建相机选择下拉框**：在编辑器工具控件（Editor Utility Widget）中，可以使用 `SMetaHumanCameraCombo` 来构建一个允许用户从 `UFootageCaptureData` 资产中选择特定摄像机的下拉列表。
2.  **预览捕获数据**：通过调用 `MetaHumanCaptureDataUtils::CreatePreviewComponent` 并传入一个 `UCaptureData` 对象，可以在编辑器视口中生成一个预览该捕获数据内容的组件（例如显示深度图或影片帧），方便检查数据质量。

## C++ 用法

### 头文件引入

```cpp
#include "CaptureDataUtils.h"
#include "SMetaHumanCameraCombo.h"
```

### 基本用法

**来源文件**: `Source/MetaHumanCaptureDataEditor/Public/CaptureDataUtils.h`

```cpp
// 假设在某个编辑器工具的代码中
#include "CaptureDataUtils.h"
#include "CaptureData/CaptureData.h" // UCaptureData 基类

void AMyEditorTool::ShowCaptureDataPreview(UCaptureData* CaptureDataAsset)
{
    if (CaptureDataAsset)
    {
        // 为捕获数据资产创建一个预览组件，并将其附加到某个对象（如当前Actor）上
        USceneComponent* PreviewComp = MetaHumanCaptureDataUtils::CreatePreviewComponent(CaptureDataAsset, this);
        if (PreviewComp)
        {
            // 例如，将其附加到根组件
            PreviewComp->AttachToComponent(GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
        }
    }
}
```

### 进阶用法

结合 `SMetaHumanCameraCombo` 和 `CaptureDataUtils` 来构建一个完整的编辑器面板。当用户在下拉框中选择不同的相机时，更新场景中的预览组件。

```cpp
// 在 Slate 控件中
void SMyPanel::Construct()
{
    // ... 初始化相机选项列表
    TArray<TSharedPtr<FString>> CameraOptions;

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        [
            // 创建一个 MetaHuman 相机选择下拉框
            SAssignNew(CameraCombo, SMetaHumanCameraCombo, &CameraOptions, &CurrentCameraName, PropertyOwner, PropertyHandle)
        ]
        // ... 其他控件
    ];

    // 绑定下拉框的更改事件
    CameraCombo->OnSelectionChangedDelegate = [this](TSharedPtr<FString> NewCamera) {
        UpdatePreviewForCamera(*NewCamera);
    };
}

void SMyPanel::UpdatePreviewForCamera(const FString& CameraName)
{
    if (CurrentFootageData)
    {
        // 根据用户选择的相机名称，可能需要在FootageCaptureData中查找对应的数据源
        // 然后创建或更新预览
        USceneComponent* Preview = MetaHumanCaptureDataUtils::CreatePreviewComponent(CurrentFootageData, PreviewOwner);
        // ... 更新UI或场景
    }
}
```

## Demo 示例

一个最小化的示例，展示如何在编辑器工具中集成 `MetaHumanCaptureDataEditor` 的功能。

```cpp
// MyMetaHumanTool.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "CaptureDataUtils.h"
#include "SMetaHumanCameraCombo.h"

class UFootageCaptureData;
class USceneComponent;

UCLASS(BlueprintType)
class UMyMetaHumanTool : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    TObjectPtr<UFootageCaptureData> FootageData;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void CreateDataPreview();

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void UpdateCameraSelection(const FString& SelectedCamera);

private:
    UPROPERTY()
    TObjectPtr<USceneComponent> CurrentPreviewComponent;
    FString CurrentCamera;
};
```

```cpp
// MyMetaHumanTool.cpp
#include "MyMetaHumanTool.h"
#include "CaptureData/FootageCaptureData.h"

void UMyMetaHumanTool::CreateDataPreview()
{
    if (FootageData)
    {
        // 销毁旧的预览组件（如果存在）
        if (CurrentPreviewComponent)
        {
            CurrentPreviewComponent->DestroyComponent();
            CurrentPreviewComponent = nullptr;
        }

        // 使用工具模块创建新的预览组件
        // 注意：此处需要一个合适的UObject作为Outer，这里使用this示例。
        // 在实际编辑器工具中，Outer可能是工具窗口的宿主对象。
        CurrentPreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(FootageData, this);
        if (CurrentPreviewComponent)
        {
            // 设置位置等...
            UE_LOG(LogTemp, Log, TEXT("Preview component created for camera: %s"), *CurrentCamera);
        }
    }
}

void UMyMetaHumanTool::UpdateCameraSelection(const FString& SelectedCamera)
{
    CurrentCamera = SelectedCamera;
    // 通常，相机选择更改后，需要重新生成预览以显示对应相机的数据
    CreateDataPreview();
}
```

## 模块依赖

使用 `MetaHumanCaptureDataEditor` 模块，你的 `Build.cs` 文件需要声明对以下模块的依赖：

| 模块 | 用途 |
|---|---|
| `MetaHumanImageViewerEditor` | 提供图像查看相关的编辑器功能，是本模块的直接依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，以避免冲突。 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 上的渲染瑕疵。 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 当进行身体追踪时，过滤掉特定的可视化对象。 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 允许为已有的网格体导出动画序列。 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 的缓存相关问题。 |

### 维护评价

该插件由 Epic Games 官方维护，从其近期的 Git 历史（尽管提供的日期在2026年，可能为示例或特定分支）来看，它处于**活跃维护**状态。更新频繁，且集中于功能完善（如身体追踪支持）和缺陷修复（渲染瑕疵、缓存问题），表明这是一个正在持续开发和改进的核心工具链。

作为 MetaHuman 生态的关键组成部分，它被强烈推荐用于所有涉及高质量面部动画制作的项目。需要注意的是，该插件可能依赖于额外的 MetaHuman 资产或外部服务（如用于处理深度数据的服务），使用时请参照 Epic 官方的完整指南。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureDataEditor)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-media/eye-tracked-morph-targets-in-unreal-engine/) (MetaHuman 相关，非此模块专用，仅供参考)