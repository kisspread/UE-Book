# MetaHuman Animator

> The official MetaHuman Unreal Engine toolkit（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器工具、资产、蓝图资产） |
| 模块 | `MetaHumanToolkit` (Runtime), `MetaHumanCore` (Runtime), `MetaHumanIdentity` (Runtime), `MetaHumanPerformance` (Runtime), `MetaHumanPipeline` (Runtime), `MetaHumanSequencer` (Runtime), `MetaHumanFaceAnimationSolver` (Runtime), `MetaHumanFaceFittingSolver` (Runtime), `MetaHumanFaceContourTracker` (Runtime), `MetaHumanCaptureSource` (Runtime), `MetaHumanCaptureProtocolStack` (Runtime), `MetaHumanCaptureUtils` (Runtime), `MetaHumanDepthGenerator` (Runtime), `MetaHumanFootageIngest` (Runtime), `MetaHumanSpeech2Face` (Runtime), `MetaHumanBatchProcessor` (Runtime), `MetaHumanConfig` (Runtime), `MetaHumanPlatform` (Runtime), `MeshTrackerInterface` (Runtime), `MetaHumanCaptureDataEditor` (Runtime), `MetaHumanImageViewerEditor` (Runtime), `MetaHumanConfigEditor` (Runtime), `MetaHumanCoreEditor` (Runtime), `MetaHumanIdentityEditor` (Runtime), `MetaHumanFaceAnimationSolverEditor` (Runtime), `MetaHumanFaceFittingSolverEditor` (Runtime), `MetaHumanFaceContourTrackerEditor` (Runtime), `MetaHumanControlsConversionTest` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator) | |

## 用途

MetaHuman Animator 是一个用于创建和驱动 MetaHuman 角色面部动画的完整工具链。它解决的核心问题是：**如何从视频素材（如 iPhone 深度摄像头录制的表演）中高效、准确地生成高质量的 MetaHuman 面部动画数据**。

该插件不仅仅是一个简单的动画导入工具，它提供了一套完整的编辑器内工作流程，包括：
1.  **面部追踪与求解**：从视频中追踪面部特征点，并求解出对应的 MetaHuman 骨骼控制数据。
2.  **身份创建与适配**：管理 MetaHuman 角色的身份资产，并将动画数据适配到不同角色上。
3.  **性能处理与编辑**：在 Sequencer 中编辑和混合动画性能。
4.  **批量处理**：支持对大量动画素材进行自动化处理。
5.  **深度与点云处理**：处理深度数据以生成更精确的动画。

其存在是为了让艺术家和开发者能够利用真实的表演数据，快速、逼真地驱动 MetaHuman 角色，极大地简化了数字人动画的制作流程。

## 使用场景

-   你正在开发一个需要大量逼真面部动画的数字人项目（如虚拟主播、游戏过场动画） → 使用 MetaHuman Animator 从演员表演视频中提取动画。
-   你需要将 iPhone 深度摄像头录制的 `.mov` 文件转换为可用于 MetaHuman 角色的动画序列 → 使用 `MetaHumanCaptureSource` 和 `MetaHumanPipeline` 模块。
-   你希望在 Unreal Editor 内直接预览和调整面部追踪结果，对比原始视频和生成的动画 → 使用 `MetaHumanToolkit` 提供的 AB 视口和编辑器工具。
-   你需要对一批表演素材进行统一的动画求解和导出 → 使用 `MetaHumanBatchProcessor` 模块。

## 蓝图用法

该插件主要提供编辑器工具和 C++ API，直接暴露给蓝图的节点相对较少，主要集中在资产操作和流程控制上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetTrackerImageViewer` | 获取用于显示追踪图像和轮廓的视图控件引用 | `SMetaHumanEditorViewport` |
| `GetCommandList` | 获取指定视图模式（A或B）的命令列表 | `FMetaHumanABCommandList` |
| `MapAction` | 将UI命令映射到AB视图的执行和检查状态函数 | `FMetaHumanABCommandList` |

### 使用示例（蓝图描述）

由于核心功能是编辑器工具，蓝图主要用于控制流程或访问数据。例如，你可以通过蓝图获取 `FMetaHumanABCommandList` 来程序化地切换视图模式或控制覆盖层的显示。但更常见的用法是直接在 MetaHuman Animator 编辑器中进行交互式操作。

## C++ 用法

该插件的 C++ API 主要用于扩展编辑器工具、自定义视口行为或集成到自动化流水线中。

### 头文件引入

```cpp
#include "MetaHumanToolkitBase.h"
#include "MetaHumanEditorViewportClient.h"
#include "MetaHumanABCommandList.h"
```

### 基本用法

继承 `FMetaHumanToolkitBase` 来创建自定义的 MetaHuman 资产编辑器工具包。这个基类已经集成了视口、细节面板和 Sequencer。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanToolkit/Public/MetaHumanToolkitBase.h
class FMyMetaHumanAssetToolkit : public FMetaHumanToolkitBase
{
public:
    FMyMetaHumanAssetToolkit(UAssetEditor* InOwningAssetEditor)
        : FMetaHumanToolkitBase(InOwningAssetEditor)
    {}

    // 重写以提供自定义的视口底部控件
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override
    {
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Widget")));
    }

    // 重写以向AB视图菜单添加自定义选项
    virtual void HandleGetViewABMenuContents(EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder) override
    {
        InMenuBuilder.AddMenuEntry(
            FText::FromString(TEXT("My Custom Toggle")),
            FText::GetEmpty(),
            FSlateIcon(),
            FUIAction(FExecuteAction::CreateSP(this, &FMyMetaHumanAssetToolkit::OnMyToggle, InViewMode))
        );
    }

private:
    void OnMyToggle(EABImageViewMode InViewMode)
    {
        // 处理自定义切换逻辑
    }
};
```

### 进阶用法

使用 `FMetaHumanEditorViewportClient` 来深度控制视口行为，例如管理深度数据的近远平面。

```cpp
// 来源: Engine/Plugins/MetaHuman/MetaHumanAnimator/Source/MetaHumanToolkit/Public/MetaHumanEditorViewportClient.h
// 假设你已经有一个 FMetaHumanEditorViewportClient 的实例 ViewportClient
FMetaHumanViewportClientDepthData DepthData(10.0f, 55.0f, 5.0f, 100.0f, 2.0f);

// 调整深度数据范围
DepthData.SetNear(15.0f);
DepthData.SetFar(60.0f);

// 将深度数据应用到视口客户端（具体方法取决于视口客户端的实现）
// ViewportClient->SetDepthData(DepthData);
```

## Demo 示例

一个最小化的自定义 MetaHuman 资产编辑器工具包示例。

```cpp
// MyMetaHumanToolkit.h
#pragma once
#include "MetaHumanToolkitBase.h"

class FMyMetaHumanToolkit : public FMetaHumanToolkitBase
{
public:
    FMyMetaHumanToolkit(UAssetEditor* InOwningAssetEditor);
    virtual ~FMyMetaHumanToolkit() override;

    // FBaseAssetToolkit interface
    virtual void CreateWidgets() override;

protected:
    // FMetaHumanToolkitBase interface
    virtual TSharedRef<SWidget> GetViewportExtraContentWidget() override;
    virtual void HandleGetViewABMenuContents(EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder) override;

private:
    TSharedPtr<STextBlock> StatusText;
};
```

```cpp
// MyMetaHumanToolkit.cpp
#include "MyMetaHumanToolkit.h"
#include "Widgets/Text/STextBlock.h"

FMyMetaHumanToolkit::FMyMetaHumanToolkit(UAssetEditor* InOwningAssetEditor)
    : FMetaHumanToolkitBase(InOwningAssetEditor)
{
}

FMyMetaHumanToolkit::~FMyMetaHumanToolkit()
{
}

void FMyMetaHumanToolkit::CreateWidgets()
{
    // 调用基类创建视口、细节面板等
    FMetaHumanToolkitBase::CreateWidgets();

    // 创建自定义状态文本
    StatusText = SNew(STextBlock).Text(FText::FromString(TEXT("Ready")));
}

TSharedRef<SWidget> FMyMetaHumanToolkit::GetViewportExtraContentWidget()
{
    // 在视口底部显示状态文本
    return StatusText.ToSharedRef();
}

void FMyMetaHumanToolkit::HandleGetViewABMenuContents(EABImageViewMode InViewMode, FMenuBuilder& InMenuBuilder)
{
    // 向视图A/B的菜单添加一个重置按钮
    InMenuBuilder.AddMenuEntry(
        FText::FromString(TEXT("Reset View")),
        FText::FromString(TEXT("Resets the view to default")),
        FSlateIcon(),
        FUIAction(FExecuteAction::CreateLambda([this, InViewMode]()
        {
            // 实现重置逻辑
            if (StatusText.IsValid())
            {
                StatusText->SetText(FText::FromString(
                    FString::Printf(TEXT("View %s Reset"), InViewMode == EABImageViewMode::A ? TEXT("A") : TEXT("B"))));
            }
        }))
    );
}
```

## 模块依赖

该插件包含大量模块，依赖关系复杂。以下是使用该插件时，你的模块可能需要依赖的一些**独特**模块（除了标准的 Core, Engine, Slate 等）：

| 模块 | 用途 |
|---|---|
| `MetaHumanCore` | MetaHuman 核心数据类型和工具 |
| `MetaHumanCoreTechLib` | MetaHuman 底层技术库（被 `MetaHumanConfig` 依赖） |
| `MetaHumanCaptureProtocolStack` | 处理捕获设备通信协议 |
| `MetaHumanCaptureSource` | 处理来自不同设备（如iPhone）的捕获数据源 |
| `MetaHumanFaceAnimationSolver` | 面部动画求解器核心算法 |
| `MetaHumanFaceFittingSolver` | 面部网格拟合求解器 |
| `MetaHumanFaceContourTracker` | 面部轮廓追踪器 |
| `MetaHumanPipeline` | 动画处理流水线框架 |
| `MetaHumanIdentity` | MetaHuman 角色身份资产管理 |
| `MetaHumanPerformance` | 动画性能数据管理 |
| `MetaHumanSequencer` | Sequencer 集成和 MetaHuman 轨道 |
| `ControlRigDeveloper` | ControlRig 开发支持（被 `MetaHumanIdentity` 依赖） |
| `SkeletalMeshUtilitiesCommon` | 骨骼网格体通用工具（被 `MetaHumanIdentity` 依赖） |

## 维护状态

### 近期更新

```
- 2025-10-03 d3626f211bdb [MHA] Sequencer related crashing with MetaHuman tracks #rb Andrew.Rodham
- 2025-09-15 6e87ed46f813 Sequencer: Refactor mute/solo to use UMovieSceneMuteSoloDecoration
- 2025-08-20 c67e2f49f855 Separate camera speed min/max into absolute and UI min/max values. Hide camera min/max UI in the camera speed menu. Add shortcut to the viewport settings page.
```

### 维护评价

**活跃维护**。MetaHuman Animator 是 Epic Games 的核心数字人技术栈的一部分，创建于 2024 年初，是一个相对较新的插件。从近期的 git 历史看，它仍在持续进行功能更新和 bug 修复（例如 Sequencer 集成改进、视口相机控制优化）。作为官方工具，其稳定性和支持是有保障的。**强烈推荐**用于任何涉及 MetaHuman 角色动画制作的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MetaHuman/MetaHumanAnimator)
- [官方文档]() (暂无)
- [测试用例]() (可能位于 `Engine/Tests/` 目录下，具体路径需进一步确认)