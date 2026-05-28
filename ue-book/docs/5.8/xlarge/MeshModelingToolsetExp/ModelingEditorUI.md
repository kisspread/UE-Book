# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 实验性网格建模工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（UI 资产） |
| 模块 | `GeometryProcessingAdapters` (Runtime), `MeshModelingToolsEditorOnlyExp` (Runtime), `MeshModelingToolsExp` (Runtime), `ModelingEditorUI` (Runtime), `ModelingUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-07-30 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

## 用途
该插件为UE5的**交互式工具框架**提供了一套实验性的**网格建模工具**所需的**编辑器UI组件和基础设施**。它不是面向最终用户的建模应用，而是**开发工具**，用于为各种网格编辑工具（如雕刻、纹理绘制、属性绘制等）快速构建一致且功能强大的参数面板、资产选择器、图层管理等界面。其核心价值在于封装了复杂的UI交互逻辑，让工具开发者可以专注于功能实现。

## 使用场景
- 你正在开发一个基于**交互式工具框架**的网格雕刻/编辑工具 → 使用 `ModelingEditorUI` 模块中的组件（如 `SToolInputAssetComboPanel`）快速构建参数面板。
- 你的工具需要支持**多图层/堆栈管理**（例如雕刻层、权重绘制层）→ 使用 `SMeshLayersStack` 和 `IMeshLayersController` 实现。
- 你的工具中需要一个**数值化的变换控件**，允许用户直接输入或拖动数值来移动、旋转、缩放对象 → 使用 `STransformGizmoNumericalUIOverlay`。
- 你需要创建一个带有**缩略图、最近使用列表和集合过滤**的资产选择器，用于选择笔刷Alpha纹理等资源 → 使用 `SToolInputAssetComboPanel`。

## 蓝图用法
该插件的核心模块（`ModelingEditorUI`）主要为C++编辑器工具开发提供UI组件，**没有暴露主要的蓝图可调用函数**。其功能通过在C++中构造和配置Slate Widget来实现。部分用于驱动UI的类（如 `FSculptLayersController`）可能作为蓝图可访问对象的属性被间接使用。

## C++ 用法

### 头文件引入
```cpp
#include "ModelingWidgets/STransformGizmoNumericalUIOverlay.h"
#include "ModelingWidgets/SToolInputAssetComboPanel.h"
#include "ModelingWidgets/SMeshLayersStack.h"
#include "ModelingWidgets/SculptLayersController.h"
```

### 基本用法
**1. 创建变换控件数值叠加层**
从 `STransformGizmoNumericalUIOverlay.h` 的注释和接口中提取。
```cpp
// 在编辑器模式或自定义工具中，创建并绑定变换控件数值UI
TSharedRef<STransformGizmoNumericalUIOverlay> NumericalOverlay = SNew(STransformGizmoNumericalUIOverlay);
// 假设已经注册了变换控件上下文对象（通过TransformGizmoUtil）
UInteractiveToolsContext* ToolsContext = ...; // 获取当前的工具上下文
NumericalOverlay->BindToGizmoContextObject(ToolsContext);
// 将叠加层添加到视口或某个Slate容器中
MyViewportOverlay->AddSlot() [NumericalOverlay];
```

**2. 创建资产选择组合面板**
从 `SToolInputAssetComboPanel.h` 的接口中提取。
```cpp
// 在工具参数面板中，添加一个用于选择纹理资产的UI
TArray<TSharedPtr<SToolInputAssetComboPanel::FComboPanelItem>> BrushItems;
BrushItems.Add(MakeShared<SToolInputAssetComboPanel::FComboPanelItem>(...)); // 定义笔刷选项

SAssignNew(BrushPicker, SToolInputAssetComboPanel)
    .AssetClassType(UTexture2D::StaticClass()) // 限定资产类型为2D纹理
    .OnSelectionChanged(FOnSelectedAssetChanged::CreateLambda([this](const FAssetData& AssetData)
    {
        // 处理选中的纹理资产
        MyBrushTexture = Cast<UTexture2D>(AssetData.GetAsset());
    }));

// 将BrushPicker添加到工具参数面板的布局中
```

**3. 创建网格图层堆栈**
从 `SMeshLayersStack.h` 和 `SculptLayersController.h` 的用法中提取。
```cpp
// 假设你有一个实现了IMeshLayersController的类（如FSculptLayersController）来管理图层数据
TSharedPtr<FSculptLayersController> SculptController = MakeShared<FSculptLayersController>();
SculptController->SetProperties(MySculptLayerProperties); // 绑定到实际数据资产

// 创建图层堆栈UI，并与控制器绑定
TSharedPtr<SMeshLayersStack> LayersStack;
SAssignNew(LayersStack, SMeshLayersStack, SculptController.ToWeakPtr())
    .InAllowAddRemove(true)
    .InAllowReordering(true);

// 当数据变化时，刷新UI视图
SculptController->RefreshLayersStackView();
```

### 进阶用法
结合多个组件构建完整的工具参数面板。
```cpp
// 一个虚构的“高级雕刻工具”参数面板构建示例
void FMySculptTool::BuildParameterUI(TSharedRef<SVerticalBox> VBox)
{
    // 1. 笔刷选择器（使用资产组合面板）
    VBox->AddSlot().AutoHeight() [
        SNew(SToolInputAssetComboPanel)
        .AssetClassType(UBrushAlphaTexture::StaticClass())
        .ComboButtonTileSize(FVector2D(40, 40))
        .FlyoutSize(FVector2D(500, 300))
    ];

    // 2. 图层管理（使用图层堆栈）
    VBox->AddSlot().AutoHeight().Padding(0, 10) [
        SNew(STextBlock).Text(LOCTEXT("Layers", "Sculpt Layers"))
    ];
    VBox->AddSlot().AutoHeight() [
        LayersStackWidget.ToSharedRef()
    ];

    // 3. 动态数值输入（用于笔刷强度、半径等）
    TSharedPtr<SDynamicNumericEntry::FDataSource> RadiusSource = SDynamicNumericEntry::MakeSimpleDataSource(
        BrushRadiusHandle,
        TInterval<float>(1.0f, 100.0f), // 值范围
        TInterval<float>(0.0f, 200.0f)  // UI滑块范围
    );
    VBox->AddSlot().AutoHeight() [
        UE::ModelingUI::MakeFixedWidthLabelSliderHBox(BrushRadiusHandle, RadiusSource, 120)
    ];
}
```

## Demo 示例
一个最小的自定义工具参数面板，包含一个资产选择器和一个数值滑块。

**MyToolUI.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"

class SToolInputAssetComboPanel;
class SDynamicNumericEntry;

class SMyToolParameterPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyToolParameterPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SToolInputAssetComboPanel> TexturePicker;
    TSharedPtr<SDynamicNumericEntry> IntensitySlider;
};
```

**MyToolUI.cpp**
```cpp
#include "MyToolUI.h"
#include "ModelingWidgets/SToolInputAssetComboPanel.h"
#include "ModelingWidgets/SDynamicNumericEntry.h"
#include "ModelingWidgets/ModelingCustomizationUtil.h"

void SMyToolParameterPanel::Construct(const FArguments& InArgs)
{
    TSharedPtr<IPropertyHandle> IntensityHandle; // 假设从某个细节面板获取

    ChildSlot
    [
        SNew(SVerticalBox)
        // 资产选择器
        + SVerticalBox::Slot().AutoHeight() [
            SAssignNew(TexturePicker, SToolInputAssetComboPanel)
            .AssetClassType(UTexture::StaticClass())
            .ToolTipText(LOCTEXT("AlphaTexTip", "Select the brush alpha texture"))
            .ComboButtonTileSize(FVector2D(48, 48))
        ]
        // 数值滑块（使用工具UI辅助函数）
        + SVerticalBox::Slot().AutoHeight().Padding(0, 10) [
            UE::ModelingUI::MakeFixedWidthLabelSliderHBox(
                IntensityHandle,
                SDynamicNumericEntry::MakeSimpleDataSource(IntensityHandle, {0.f, 1.f}, {0.f, 2.f}),
                100 // 标签固定宽度
            )
        ]
    ];
}
```

## 模块依赖
无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件的模块主要为其他建模工具模块（如 `MeshModelingToolsExp`）提供 UI 支持，自身不依赖外部特殊模块。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-27 | `32bb5ca4` | [ModelingTools] MeshVertexAttributePaintTool + SkinWeightsPaintTool: added bSyncBrushRadiusAcrossMod | 为顶点属性和蒙皮权重绘制工具添加了跨模式同步笔刷半径的功能。 |
| 2026-05-26 | `cf0257a2` | MeshVertexAttributePaintTool: refactor FStrokeAccumulator to support accumulating relax brush + fix | 重构了顶点属性绘制工具的笔画累加器，以支持松弛笔刷的累积效果，并进行了修复。 |
| 2026-05-22 | `4938c498` | [SkeletalMeshModelingTools] Set AutoCalculated tangents mode on preview/sculpt meshes that lack valid | 在预览/雕刻网格缺少有效切线数据时，为其设置了自动计算切线的模式。 |
| 2026-05-19 | `12cf9c64` | [SkeletalMeshModelingTools] Fixed polygroup edge visualizer not updated after mesh deformation | 修复了骨骼网格建模工具中，多边形组边缘可视化器在网格变形后不更新的问题。 |
| 2026-05-14 | `f6425490` | [ModelingTools] Add UMeshElementsVisualizer to skin-weights tool; default group-boundary settings ON | 为蒙皮权重工具添加了网格元素可视化器，并将默认组边界设置设为开启。 |

### 维护评价
该插件**处于活跃的维护和开发中**。从提交历史看，在2026年5月有密集的功能更新和问题修复，涉及多个具体的建模工具（顶点属性绘制、蒙皮权重、骨骼网格建模）。尽管插件标记为`IsExperimentalVersion`和`Hidden`，表明其API可能不完全稳定，且默认不启用，但其底层的`MeshModelingToolsExp`和`ModelingEditorUI`模块是UE5编辑器中网格建模工具链的**核心UI基础组件**，被广泛使用。因此，**推荐在开发基于交互式工具框架的自定义网格编辑工具时，使用和参考此插件中的UI组件**。需注意其“实验性”状态可能意味着未来版本中API会有变动。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests) (如存在)