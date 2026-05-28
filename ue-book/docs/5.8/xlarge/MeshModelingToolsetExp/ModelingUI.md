# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | 其他 |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（实验性工具和UI组件） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途

这是一个实验性插件，为 UE5 的交互式工具框架（Interactive Tools Framework）提供了一套用于创建和编辑 3D 网格的实验性模块和工具。其主要价值在于提供了一套可扩展、基于 Slate 的 UI 组件（如可拖拽的工具面板），用于构建复杂的建模工具界面，是 UE5 内置建模工具的实验性前身和原型。它解决的核心问题是：在编辑器内，如何为交互式工具快速构建复杂、灵活的用户界面。

## 使用场景

- 你是一个工具开发者，正在为 UE5 编辑器创建自定义的网格编辑工具，需要一个标准化的、可拖拽的工具设置面板。
- 你希望你的工具 UI 能够与 UE5 的工具管理器（Interactive Tools Framework）深度集成，而非从头编写 Slate 代码。
- 你在试验或开发新的网格处理算法，并希望为其快速搭建一个可用的编辑器界面原型。

## 蓝图用法

**注意**: 该插件中的类主要面向 C++ 开发者，用于构建编辑器工具 UI，纯蓝图使用场景有限。以下列出关键的 Slate 控件，可在蓝图中通过 `SNew` 函数或嵌入到自定义工具面板中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Construct` | 构建一个可拖拽的盒状控件覆盖层，其内容可以是任何 Slate 控件。 | `SDraggableBoxOverlay` |
| `SetBoxPosition` | 设置可拖拽盒控件在其父覆盖层中的位置。 | `SDraggableBoxOverlay` |

### 使用示例（蓝图描述）

由于 `SDraggableBoxOverlay` 是一个 Slate 控件，无法直接在蓝图图表中作为节点创建。它的典型使用方式是在 C++ 代码中构建工具面板时使用。在蓝图资产（如 UMG Widget）中，你通常不会直接使用此类。

## C++ 用法

该插件的 API 主要用于在 C++ 中构建自定义编辑器工具的 UI 部分。

### 头文件引入

```cpp
#include "ModelingWidgets/SDraggableBox.h" // 包含可拖拽盒控件
#include "ModelingUIModule.h" // 模块接口
```

### 基本用法

以下代码创建了一个简单的可拖拽工具面板，并将其放置在视图的右下角。
*来源参考: `Public/ModelingWidgets/SDraggableBox.h`*

```cpp
// 在你的工具或编辑器 Utility 类的 Slate 构建代码中（例如 FYourTool::BuildUI）
TSharedRef<SWidget> ToolSettingsPanel =
    SNew(SVerticalBox)
    + SVerticalBox::Slot()
    .AutoHeight()
    [
        SNew(STextBlock)
        .Text(FText::FromString(TEXT("工具设置")))
    ]
    + SVerticalBox::Slot()
    .AutoHeight()
    [
        SNew(SButton)
        .Text(FText::FromString(TEXT("执行操作")))
        .OnClicked_Lambda([]() { /* 按钮逻辑 */ })
    ];

// 创建可拖拽的覆盖层，将设置面板放入其中
TSharedRef<SDraggableBoxOverlay> DraggablePanel =
    SNew(SDraggableBoxOverlay)
    .bPositionRelativeToBottom(true) // 位置相对于底部，适合放在视图下方
    [
        ToolSettingsPanel
    ];

// 设置初始位置（例如：距左边 200 像素，距底部 50 像素）
DraggablePanel->SetBoxPosition(200.f, 50.f);

// 将 DraggablePanel 添加到你的工具的主 UI 容器中
YourMainToolUIContainer->AddSlot()
    [
        DraggablePanel
    ];
```

### 进阶用法

`SDraggableBoxOverlay` 的底层依赖于 `SDraggableBox` 和 `FDraggableBoxUIDragOperation` 来实现拖拽逻辑。虽然这些类在 UE 5.6 已被标记为废弃，并建议使用 `UE::ToolWidgets::SDraggableBoxOverlay`，但了解其原理有助于实现自定义的拖拽行为。当用户拖拽盒子时，`FDraggableBoxUIDragOperation::OnDrop` 会触发，并将最终屏幕坐标传递给 `SDraggableBox::FOnDragComplete` 委托，`SDraggableBoxOverlay` 内部会利用此委托来更新 `SetBoxPosition`。

## Demo 示例

一个最小化的、为自定义工具创建可拖拽设置面板的示例。
*此示例假设你已经在一个继承自 `UInteractiveTool` 或类似的工具类中。*

### MyModelingTool.h

```cpp
#pragma once

#include "InteractiveToolBuilder.h"
#include "BaseTools/InteractiveTool.h"
#include "MyModelingTool.generated.h"

UCLASS()
class UMyModelingToolBuilder : public UInteractiveToolBuilder
{
    GENERATED_BODY()
public:
    virtual bool CanBuildTool(const FToolBuilderState& SceneState) const override { return true; }
    virtual UInteractiveTool* BuildTool(const FToolBuilderState& SceneState) const override;
};

UCLASS()
class UMyModelingTool : public UInteractiveTool
{
    GENERATED_BODY()
public:
    virtual void Setup() override;
    virtual void Shutdown(EToolShutdownType ShutdownType) override;

    // 工具的主要 UI 面板将由 Slate 构建
    virtual void BuildUIToolPalette(TSharedRef<class SWidget> ParentWidget) override;

private:
    // 可拖拽的面板控件
    TSharedPtr<class SDraggableBoxOverlay> DraggableSettingsPanel;
};
```

### MyModelingTool.cpp

```cpp
#include "MyModelingTool.h"
#include "ModelingWidgets/SDraggableBox.h" // 引入实验性 UI 控件
#include "Widgets/Layout/SBorder.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"

UInteractiveTool* UMyModelingToolBuilder::BuildTool(const FToolBuilderState& SceneState) const
{
    return NewObject<UMyModelingTool>(SceneState.ToolManager);
}

void UMyModelingTool::Setup()
{
    UInteractiveTool::Setup();
}

void UMyModelingTool::Shutdown(EToolShutdownType ShutdownType)
{
    UInteractiveTool::Shutdown(ShutdownType);
}

void UMyModelingTool::BuildUIToolPalette(TSharedRef<SWidget> ParentWidget)
{
    // 1. 构建工具内部的 Slate 控件
    TSharedRef<SWidget> InternalToolUI =
        SNew(SBorder)
        .Padding(FMargin(4.f))
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            .Padding(FMargin(0, 0, 0, 2))
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("我的实验工具")))
            ]
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                SNew(SButton)
                .Text(FText::FromString(TEXT("随机化顶点")))
                .OnClicked_Lambda([this]() {
                    // 在这里实现具体的工具逻辑，例如随机移动顶点
                    return FReply::Handled();
                })
            ]
        ];

    // 2. 使用实验性的 SDraggableBoxOverlay 包装它
    DraggableSettingsPanel = SNew(SDraggableBoxOverlay)
        .bPositionRelativeToBottom(false) // 位置相对于顶部
        [
            InternalToolUI
        ];

    // 3. 将可拖拽面板添加到工具调色板的父控件中
    ParentWidget->AddSlot()
        [
            DraggableSettingsPanel.ToSharedRef()
        ];

    // 4. 设置一个初始位置（例如右上角）
    DraggableSettingsPanel->SetBoxPosition(100.f, 100.f);
}
```

## 模块依赖

该插件的模块依赖主要围绕 Slate UI、交互工具框架和几何处理。使用 `MeshModelingToolsExp` 或 `MeshModelingToolsEditorOnlyExp` 模块中的工具时，你的 Build.cs 需要添加以下依赖。

| 模块 | 用途 |
|---|---|
| `GeometryProcessingAdapters` | 提供几何处理算法与 UE5 数据类型之间的适配器。 |
| `ModelingUI` | 提供实验性的 Slate UI 控件（如 `SDraggableBoxOverlay`），用于构建工具界面。 |
| `ModelingEditorUI` | 提供更高级的编辑器内建模工具 UI 组件。 |
| `ToolWidgets` | UE5 核心工具控件模块（非实验性，`SDraggableBoxOverlay` 的正式替代品所在）。 |
| `InteractiveToolsFramework` | 提供交互式工具的核心框架（`UInteractiveTool` 等）。 |

*注：Core, CoreUObject, Engine, Slate, SlateCore 等标准依赖已省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性绘制和蒙皮权重绘制工具添加笔刷半径跨模式同步功能。 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构顶点绘制工具的笔划累加器，以支持累积松弛笔刷，并修复相关问题。 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid | 在缺乏有效切线的预览/雕刻网格上设置自动计算切线模式。 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复骨骼网格建模工具在网格变形后多边形组边缘可视化不更新的问题。 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 为蒙皮权重工具添加网格元素可视化组件；默认开启组边界显示设置。 |

### 维护评价

**活跃维护中**。

- **年龄与状态**：该插件创建于 2021 年 7 月，已超过 5 年，是一个“老古董”级别的实验性插件。
- **近期活跃度**：从 2026 年 5 月的提交记录来看，该插件仍在被积极更新和改进。更新主要集中在 `MeshModelingToolsExp` 模块中的具体工具（如顶点绘制、骨骼网格编辑），而 `ModelingUI` 等 UI 模块相对稳定。
- **核心功能演变**：注意 `SDraggableBoxOverlay` 等 UI 控件在 UE 5.6 中已被标记为废弃（Deprecated），官方推荐迁移至 `UE::ToolWidgets` 命名空间下的正式版本。这意味着插件的 UI 基础部分正在向引擎核心迁移。
- **推荐度**：**可以用于学习和参考**，特别是了解 UE5 交互式工具的 UI 构建模式。但由于其“实验性”和“隐藏”状态，**不建议直接在新项目中依赖**。对于新的工具开发，应优先使用非实验性的 `ModelingTools` 插件或直接使用 `ToolWidgets` 模块中的控件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- 官方文档：无
- [测试用例（可能位于引擎测试目录）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests)