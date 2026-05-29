# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit

| 属性 | 值 |
|---|---|
| 中文名 | MetaHuman 动画师 |
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、测试资源） |
| 模块 | `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanCaptureDataEditor` (Runtime) 等 |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是 Epic Games 官方为 MetaHuman 角色提供的完整动画制作工具链。它解决的核心问题是：**如何将真实的人脸表演（如视频、音频、深度数据）高效、高质量地转换为 MetaHuman 角色的面部动画**。

该插件不是单一功能，而是一个集成的生态系统，包含：
1. **捕获数据处理**：从 iPhone、专业摄像头等设备导入和处理视频、音频、深度数据。
2. **面部追踪与拟合**：分析视频中的面部特征点，追踪面部轮廓。
3. **动画求解**：将追踪到的数据转换为 MetaHuman 角色的骨骼动画（ControlRig）。
4. **动画合成**：管理、编辑、预览和导出动画序列。
5. **批处理流水线**：支持自动化处理大量捕获数据。

它存在的意义是**大幅简化从真实表演到数字角色动画的制作流程**，使非专业人士也能制作出电影级的面部动画。

## 使用场景

- **独立开发者/小型团队**：想用一部 iPhone 快速为自己的 MetaHuman 角色制作对话动画。
- **影视/游戏工作室**：需要批量处理大量演员表演数据，用于制作游戏过场或影视内容。
- **虚拟人直播/内容创作**：需要实时或准实时驱动数字人进行直播或视频创作。
- **研究/教育**：学习面部动画、计算机视觉在游戏开发中的应用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePreviewComponent` | 为捕获数据创建用于在场景中预览的组件 | `MetaHumanCaptureDataUtils` |
| `HandleSourceDataChanged` | 当捕获数据源（如视频、音频）发生变化时调用，用于更新UI和处理逻辑 | `SMetaHumanCameraCombo` |
| `OnSelectionChanged` | 当下拉框选项改变时触发的事件 | `SMetaHumanCameraCombo` |

### 使用示例（蓝图描述）

1.  **数据导入与预览**：
    -   创建一个 `UCaptureData` 资产（如 `UFootageCaptureData`）。
    -   使用 `MetaHumanCaptureDataUtils::CreatePreviewComponent` 节点，将该资产连接，即可在场景中生成一个预览组件，显示捕获的视频帧。
    -   使用 `SMetaHumanCameraCombo` 控件，可以提供一个摄像头选择下拉框，并在数据源改变时（如选中不同摄像头）通过 `HandleSourceDataChanged` 更新相关属性。

2.  **动画制作流水线**：
    -   蓝图中调用 `MetaHumanPipeline` 模块的功能，配置一个处理流水线，输入捕获数据，输出为 `UAnimSequence`。
    -   使用 `MetaHumanPerformance` 模块管理动画表现，可以预览、编辑时间线，并最终导出到 Sequencer。

## C++ 用法

### 头文件引入

```cpp
#include "MetaHumanCaptureDataEditorModule.h"
#include "CaptureDataUtils.h"
```

### 基本用法

从 `CaptureDataUtils.h` 提取的示例：
```cpp
// 假设 InCaptureData 是一个有效的捕获数据资产
// 假设 InObject 是拥有此预览组件的对象（如某个 Actor）
USceneComponent* PreviewComponent = MetaHumanCaptureDataUtils::CreatePreviewComponent(InCaptureData, InObject);
if (PreviewComponent)
{
    // 将预览组件附加到对象上
    PreviewComponent->AttachToComponent(InObject->GetRootComponent(), FAttachmentTransformRules::KeepRelativeTransform);
}
```
*来源文件：Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanCaptureDataEditor/Public/CaptureDataUtils.h*

### 进阶用法

结合 `MetaHumanCaptureDataEditor` 模块的类 `SMetaHumanCameraCombo`，可以在自定义编辑器面板中集成摄像头选择功能：
```cpp
// 创建一个摄像头下拉框控件
TSharedPtr<SMetaHumanCameraCombo> CameraCombo;
SAssignNew(CameraCombo, SMetaHumanCameraCombo, &CameraOptions, &CurrentCameraName, PropertyOwner, PropertyHandle)
    .IsEnabled_Lambda([this]() { return bIsDataLoaded; });

// 当外部捕获数据源变化时，通知控件更新
CameraCombo->HandleSourceDataChanged(FootageCaptureData, AudioWave, true);
```

## Demo 示例

```cpp
// MetaHumanPreviewActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MetaHumanPreviewActor.generated.h"

class UCaptureData;
class USceneComponent;

UCLASS()
class AMetaHumanPreviewActor : public AActor
{
    GENERATED_BODY()
public:
    AMetaHumanPreviewActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MetaHuman")
    TObjectPtr<UCaptureData> CaptureDataAsset;

    UFUNCTION(BlueprintCallable, Category = "MetaHuman")
    void UpdatePreview();

protected:
    virtual void OnConstruction(const FTransform& Transform) override;

private:
    UPROPERTY()
    TObjectPtr<USceneComponent> PreviewRoot;
};

// MetaHumanPreviewActor.cpp
#include "MetaHumanPreviewActor.h"
#include "CaptureDataUtils.h"
#include "Engine/CaptureData.h"

AMetaHumanPreviewActor::AMetaHumanPreviewActor()
{
    PrimaryActorTick.bCanEverTick = false;
    PreviewRoot = CreateDefaultSubobject<USceneComponent>(TEXT("PreviewRoot"));
    RootComponent = PreviewRoot;
}

void AMetaHumanPreviewActor::OnConstruction(const FTransform& Transform)
{
    Super::OnConstruction(Transform);
    UpdatePreview();
}

void AMetaHumanPreviewActor::UpdatePreview()
{
    // 清除旧的预览组件
    if (PreviewRoot->GetNumChildrenComponents() > 0)
    {
        PreviewRoot->DestroyChildren();
    }

    if (CaptureDataAsset)
    {
        // 使用工具函数创建新的预览组件
        USceneComponent* NewPreviewComp = MetaHumanCaptureDataUtils::CreatePreviewComponent(CaptureDataAsset, this);
        if (NewPreviewComp)
        {
            NewPreviewComp->AttachToComponent(PreviewRoot, FAttachmentTransformRules::KeepRelativeTransform);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaHumanCoreTechLib` | MetaHuman 核心技术库，包含底层算法和数据结构 |
| `MetaHumanSDKEditor` | MetaHuman SDK 的编辑器部分，提供资产编辑和管理功能 |
| `ControlRigDeveloper` | ControlRig 开发工具，用于面部骨骼动画的求解和驱动 |
| `MetaHumanImageViewerEditor` | 提供图像查看器的编辑器功能，用于预览捕获的视频帧 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-22 | `7a048bf4` | Disable level sequence export when body tracking enabled | 当启用身体追踪时，禁用关卡序列导出功能，避免冲突 |
| 2026-05-21 | `9c78518c` | Fix rendering artefacts on MH. | 修复 MetaHuman 角色上的渲染伪影问题 |
| 2026-05-21 | `1396cbbf` | Filter visualization objects when body tracking | 在身体追踪时过滤可视化对象，提升性能或清晰度 |
| 2026-05-21 | `0d185763` | [MHA] Export animation sequence for existing mesh | 支持为现有网格体导出动画序列，增强工作流灵活性 |
| 2026-05-20 | `35537544` | Fix sequencer caching issues | 修复 Sequencer 缓存问题，提升编辑器稳定性 |

### 维护评价

-   **活跃维护**：从最近的提交记录看，该插件在 2026 年 5 月仍有频繁的功能更新和 Bug 修复（涉及动画导出、渲染、追踪等核心功能）。
-   **重要性高**：作为 Epic 官方 MetaHuman 工具链的核心组成部分，其维护优先级很高。
-   **推荐使用**：如果你的项目使用了 MetaHuman 角色并需要制作面部动画，这是官方推荐且持续维护的首选工具。
-   **注意**：该插件规模庞大（544个源文件），学习曲线较陡，且可能依赖于特定的 MetaHuman 资产格式和工作流。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MetaHuman/MetaHumanAnimator)
-   官方文档：无（DocsURL 为空）
-   测试用例：未在分析中提供路径，通常位于插件源码的 `Tests` 目录下。