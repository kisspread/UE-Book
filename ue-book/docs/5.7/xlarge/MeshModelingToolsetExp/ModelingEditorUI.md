# Experimental Mesh Modeling Toolset

> A set of experimental modules implementing 3D mesh creation and editing based on the Interactive Tools Framework

| 属性 | 值 |
|---|---|
| 中文名 | 建模编辑器UI |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（样式图标、UI资源） |
| 模块 | `ModelingEditorUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-29 |
| 年龄标签 | 🆕（约1年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp) | |

---

## 用途

`ModelingEditorUI` 模块是 `MeshModelingToolsetExp` 插件中负责提供编辑器 UI 组件的部分。它并非独立使用，而是为基于交互工具框架（Interactive Tools Framework）的建模工具提供可复用的 Slate 小部件和辅助类。

核心功能包括：

- **网格层管理**：通过 `SMeshLayersStack` / `SMeshLayersList` 和 `IMeshLayersController` 接口，提供可视化的层叠堆栈 UI，支持添加、移除、重命名、拖拽排序、切换可见性等操作。典型应用是雕刻工具的雕刻层管理。
- **通用选择面板**：`SComboPanel` 提供图标网格形式的弹出选择器，`SToolInputAssetComboPanel` 提供专门的资产选择面板（含缩略图、收藏过滤、最近使用等），方便在工具参数面板中选择笔刷纹理、模型等。
- **数值输入控件**：`SDynamicNumericEntry` 封装了可自定义范围、精度的浮点数输入框，适合建模工具中的滑块/数值输入。
- **变换 Gizmo 数值叠加**：`STransformGizmoNumericalUIOverlay` 可在视口上叠加一个可拖拽的面板，同步显示并修改当前变换 Gizmo 的位移、旋转、缩放数值。
- **通用 UI 工具**：`ModelingCustomizationUtil` 提供快速生成标准细节行布局、布尔切换按钮、固定宽度标签/滑块等辅助函数，简化自定义工具面板的构建。
- **样式资源**：`FModelingEditorUIStyle` 注册了网格层 UI 相关的 Slate 样式（图标、边框颜色、透明按钮等）。

该模块解决了在建模工具中需要频繁创建相似 UI 模式（层叠列表、资产选择、数值控制）的问题，提供了统一、一致且可扩展的组件。由于其作为编辑器 UI 模块，仅在 Editor 配置下有效。

## 使用场景

- 开发一个**雕刻工具**（如 `MeshModelingToolsExp` 中的雕刻工具），需要提供雕刻层管理界面，允许用户创建、删除、重命名、拖拽排序层，并设置每层的权重和可见性 → 使用 `SMeshLayersStack` + `FSculptLayersController`。
- 制作一个**笔刷纹理选择器**，需要从内容浏览器中选取纹理资产，并支持最近使用记录和收藏集过滤 → 使用 `SToolInputAssetComboPanel`。
- 开发一个**网格变换工具**，希望在视口内直接以数值形式调整物体的位置、旋转和缩放 → 使用 `STransformGizmoNumericalUIOverlay` 叠加在视口上。
- 构建**工具参数面板**时，需要快速创建具有固定宽度标签和滑块、布尔切换按钮等标准布局 → 使用 `UE::ModelingUI::MakeFixedWidthLabelSliderHBox` 等辅助函数。

## 蓝图用法

该模块完全由 C++ 实现，所有 UI 组件均为 Slate 小部件，**不暴露任何 BlueprintCallable 函数或 BlueprintReadWrite 属性**。蓝图无法直接使用本模块提供的类。如果需要集成到蓝图，需通过 C++ 父类或接口间接暴露。

## C++ 用法

### 头文件引入

根据使用的组件引入对应的头文件：

```cpp
#include "ModelingWidgets/SMeshLayersStack.h"
#include "ModelingWidgets/SculptLayersController.h"
#include "ModelingWidgets/SComboPanel.h"
#include "ModelingWidgets/SToolInputAssetComboPanel.h"
#include "ModelingWidgets/SDynamicNumericEntry.h"
#include "STransformGizmoNumericalUIOverlay.h"
#include "ModelingWidgets/ModelingCustomizationUtil.h"
```

### 基本用法

#### 创建网格层堆栈 UI

```cpp
// 在工具类中（如 UMeshSculptTool）：
// 1. 创建控制器（实现 IMeshLayersController）
TSharedPtr<FSculptLayersController> LayersController = MakeShared<FSculptLayersController>();
LayersController->SetProperties(SculptProperties); // UMeshSculptLayerProperties*

// 2. 创建 SMeshLayersStack 并设置控制器
TSharedPtr<SMeshLayersStack> LayerStack;
SAssignNew(LayerStack, SMeshLayersStack)
    .InController(LayersController)
    .InAllowAddRemove(true)
    .InAllowReordering(true);

// 3. 将 LayerStack 添加到工具的自定义 Slate 面板中
// 例如作为 SScrollBox 的子项
```
*来源：`SMeshLayersStack.h` 的 Construct 方法与 `FSculptLayersController.h`*

#### 创建资产选择面板

```cpp
// 准备资产选择器配置
FAssetPickerConfig Config;
Config.Filter.ClassPaths.Add(UTexture2D::StaticClass()->GetClassPathName());
Config.OnAssetSelected = FOnAssetSelected::CreateLambda([](const FAssetData& AssetData) {
    // 处理选中事件
});

// 创建 SToolInputAssetComboPanel
TSharedRef<SToolInputAssetComboPanel> AssetPanel = SNew(SToolInputAssetComboPanel)
    .ComboButtonTileSize(FVector2D(50, 50))
    .FlyoutTileSize(FVector2D(85, 85))
    .AssetClassType(UTexture2D::StaticClass())
    .OnSelectionChanged_Lambda([](const FAssetData& AssetData) {
        // 处理选择变化
    });
```
*来源：`SToolInputAssetComboPanel.h`*

#### 使用变换 Gizmo 数值叠加

```cpp
// 在自定义编辑器模式下，创建 STransformGizmoNumericalUIOverlay
TSharedPtr<STransformGizmoNumericalUIOverlay> NumericalUI;
SAssignNew(NumericalUI, STransformGizmoNumericalUIOverlay)
    .bPositionRelativeToBottom(true)
    .DefaultLeftPadding(15)
    .DefaultVerticalPadding(15);

// 绑定到工具上下文，使得后续创建的变换 Gizmo 自动关联
NumericalUI->BindToGizmoContextObject(GetToolsContext());
// 设置启用
NumericalUI->SetEnabled(true);
// 添加到视口叠加层（通常通过 ViewportOverlay）
```
*来源：`STransformGizmoNumericalUIOverlay.h`*

### 进阶用法

#### 自定义数值输入源的 SDynamicNumericEntry

```cpp
// 创建一个数据源，连接到自定义属性
TSharedPtr<FDynamicNumericEntry::FDataSource> DataSource = MakeShared<FDynamicNumericEntry::FDataSource>();
DataSource->GetValue = []() -> float { return MyProperty->GetValue(); };
DataSource->SetValue = [](float NewVal, EPropertyValueSetFlags::Type Flags) { MyProperty->SetValue(NewVal, Flags); };
DataSource->GetValueRange = []() -> TInterval<float> { return TInterval<float>(0, 100); };
DataSource->GetUIRange = []() -> TInterval<float> { return TInterval<float>(0, 100); };

// 创建数值输入控件
TSharedRef<SDynamicNumericEntry> Entry = SNew(SDynamicNumericEntry)
    .Source(DataSource)
    .MaxNumFloatDigits(3);
```
*来源：`SDynamicNumericEntry.h`*

#### 通过 ModelingCustomizationUtil 快速构建工具面板

```cpp
using namespace UE::ModelingUI;

// 创建一个切换按钮 + 滑块行
TSharedPtr<IPropertyHandle> BoolHandle = ...; // 指向 bool 属性
TSharedPtr<SDynamicNumericEntry::FDataSource> SliderDataSource = ...;

TSharedRef<SWidget> Row = MakeToggleSliderHBox(
    BoolHandle,
    FText::FromString("Enable Feature"),
    SliderDataSource,
    80     // 切换按钮固定宽度
);
```
*来源：`ModelingCustomizationUtil.h`*

## Demo 示例

以下是一个最小示例，展示如何在自定义工具 Slate 面板中集成 `SMeshLayersStack` 和一个 `SComboPanel`。假设已存在控制器实现和工具上下文。

**MyToolUI.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class IMeshLayersController;
class SComboPanel;

class SMyToolUI : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyToolUI) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, const TSharedPtr<IMeshLayersController>& InLayerController);

private:
    TSharedPtr<SMeshLayersStack> LayerStack;
    TSharedPtr<SComboPanel> ComboPanel;
};
```

**MyToolUI.cpp**
```cpp
#include "MyToolUI.h"
#include "ModelingWidgets/SMeshLayersStack.h"
#include "ModelingWidgets/SComboPanel.h"

void SMyToolUI::Construct(const FArguments& InArgs, const TSharedPtr<IMeshLayersController>& InLayerController)
{
    // 构建网格层堆栈
    SAssignNew(LayerStack, SMeshLayersStack)
        .InController(InLayerController)
        .InAllowAddRemove(true)
        .InAllowReordering(true);

    // 准备 SComboPanel 的列表项
    TArray<TSharedPtr<SComboPanel::FComboPanelItem>> ComboItems;
    for (int i = 0; i < 5; ++i)
    {
        TSharedPtr<SComboPanel::FComboPanelItem> Item = MakeShared<SComboPanel::FComboPanelItem>();
        Item->Name = FText::FromString(FString::Printf(TEXT("Option %d"), i));
        Item->Identifier = i;
        ComboItems.Add(Item);
    }

    // 构建 SComboPanel
    SAssignNew(ComboPanel, SComboPanel)
        .ListItems(ComboItems)
        .ComboButtonTileSize(FVector2D(50, 50))
        .FlyoutTileSize(FVector2D(85, 85))
        .OnSelectionChanged_Lambda([](TSharedPtr<SComboPanel::FComboPanelItem> Selected) {
            UE_LOG(LogTemp, Log, TEXT("Selected option %d: %s"), Selected->Identifier, *Selected->Name.ToString());
        });

    // 组合布局
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            LayerStack.ToSharedRef()
        ]
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(0, 10, 0, 0)
        [
            ComboPanel.ToSharedRef()
        ]
    ];
}
```

## 模块依赖

**省略常见依赖**：Core, CoreUObject, Engine, Slate, SlateCore, UMG, InputCore, UnrealEd, PropertyEditor, DeveloperSettings, Projects。

| 模块 | 用途 |
|---|---|
| `InteractiveToolsFramework` | 提供交互工具上下文和变换 Gizmo 类型 |
| `MeshModelingToolsExp` | 提供网格层属性（`UMeshSculptLayerProperties`）等建模工具类 |
| `AssetRegistry` | 资产浏览和选择后端 |
| `ContentBrowser` | 资产选择器 UI（`SAssetView`、`FAssetPickerConfig`） |
| `ToolWidgets` | 提供可拖动画板叠加层（`SDraggableBoxOverlay`） |

## 维护状态

### 近期更新

- 2025-12-18 `79bdb336` — #jira UE-356302（内部修复）
- 2025-11-18 `e352ab23` — fix crash on converting multiple dynamic mesh sources to static meshes w/ the modeling mode convert
- 2025-10-03 `fea318f1` — PR #13360: Add assign and start new keyboard command to cube grid
- 2025-10-03 `53d4840d` — ModelingTools: Fix CubeGrid "Accept and Start New" action not working correctly when editing an existing...
- 2025-09-29 `300d2503` — Merge Actor - Approximate: Use the correct merge material to avoid showing default engine textures when...

### 维护评价

- **创建时间**：2025-09-29，至今约 1 年。
- **更新频率**：2025 年内有多次实质性提交（功能增加、崩溃修复），最近一次在 2025-12-18，属于活跃维护。
- **稳定性**：插件标记为实验性（`IsExperimentalVersion=true`），API 可能发生变化，但核心 UI 组件已趋于稳定。
- **推荐使用**：如果正在开发建模工具且需要上述 UI 组件，推荐使用。但注意该模块为实验性，在正式项目中需评估 API 变更风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MeshModelingToolsetExp/Tests)（若存在）