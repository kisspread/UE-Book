# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（示例资产） |
| 模块 | `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter) | |

## 用途

`USDStageEditorViewModels` 是 USDImporter 插件的一个模块，为 **USD 舞台编辑器** (USD Stage Editor) 提供视图模型（ViewModel）层。它负责管理 UI 与 USD 数据之间的桥接，将底层的 USD 概念（如图层、基元、变体集、引用、属性、整合等）封装为便于 Slate 绑定的 C++ 对象。该模块主要服务于 USD Stage 编辑器的面板，用于显示和交互操作 USD 舞台的层次结构、图层、引用、变体集、对象字段（元数据/属性/关系）等。解决的核心问题是将复杂的 USD API 抽象为 UE 编辑器友好的数据模型，实现 MVVM 架构中的 ViewModel 部分。

## 使用场景

- 当你需要编写自定义 USD 编辑器面板或扩展 USD Stage 编辑器的功能时
- 需要在 C++ 层面直接操作 USD 舞台的图层、基元、变体集等数据，并希望复用已有的 ViewModel 层
- 开发 USD 导入/导出相关的编辑器工具，需要访问舞台结构并进行修改（如切换变体、加载/卸载 payload、管理引用等）

## 蓝图用法

本模块的所有类均为纯 C++ 类，没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性，因此 **无法在蓝图中直接使用**。所有功能需通过 C++ 扩展实现。

## C++ 用法

### 头文件引入

```cpp
#include "USDLayersViewModel.h"
#include "USDPrimViewModel.h"
#include "USDStageViewModel.h"
#include "USDVariantSetsViewModel.h"
#include "USDReferencesViewModel.h"
#include "USDIntegrationsViewModel.h"
#include "USDObjectFieldViewModel.h"
```

### 基本用法

以下示例展示如何使用 `FUsdStageViewModel` 打开一个 USD 舞台并执行基本操作：

```cpp
// 假设已有一个 AUsdStageActor 实例
AUsdStageActor* StageActor = ...;

FUsdStageViewModel StageVM;
StageVM.UsdStageActor = StageActor;

// 打开一个 USD 文件
StageVM.OpenStage(TEXT("/Game/MyAssets/Scene.usda"));

// 重新加载
StageVM.ReloadStage();

// 导入舞台到指定内容文件夹
StageVM.ImportStage(TEXT("/Game/Imported"));

// 关闭舞台
StageVM.CloseStage();
```

来源：`USDStageViewModel.h`

### 图层操作

使用 `FUsdLayerViewModel` 浏览和管理舞台的图层层次：

```cpp
// 获取主舞台的孤立图层（IsolatedStage）
UE::FUsdStageWeak Stage = ...;
UE::FUsdStageWeak IsolatedStage = ...; // 可选，用于隔离编辑
FString RootLayerId = Stage.GetRootLayer().GetIdentifier();

// 创建根图层视图模型
FUsdLayerViewModel RootLayerVM(nullptr, Stage, IsolatedStage, RootLayerId);
RootLayerVM.RefreshData();
RootLayerVM.FillChildren();

// 遍历子图层
for (const TSharedRef<FUsdLayerViewModel>& Child : RootLayerVM.Children)
{
    // 获取显示名
    FText Name = Child->GetDisplayName();

    // 切换静音状态
    Child->ToggleMuteLayer();

    // 设置为编辑目标
    Child->EditLayer();

    // 添加子图层
    Child->AddSubLayer(TEXT("/Game/MySubLayer.usda"));
}
```

来源：`USDLayersViewModel.h`

### 基元操作

使用 `FUsdPrimViewModel` 遍历和修改舞台中的基元：

```cpp
// 获取舞台根覆盖Prim
UE::FUsdStageWeak Stage = ...;
UE::FUsdPrim RootPrim = Stage.GetPseudoRoot();

// 创建基元视图模型
FUsdPrimViewModel PrimVM(nullptr, Stage, RootPrim);
PrimVM.RefreshData(/* bRefreshChildren */ true);
PrimVM.FillChildren();

// 展开/折叠
PrimVM.SetIsExpanded(true);

// 切换可见性和payload
if (PrimVM.HasVisibilityAttribute())
{
    PrimVM.ToggleVisibility();
}
PrimVM.TogglePayload();

// 应用/移除 schema
PrimVM.ApplySchema(TEXT("GeomSubset"));
PrimVM.RemoveSchema(TEXT("SkelRoot"));

// 检查本地层上的spec
if (PrimVM.HasSpecsOnLocalLayer())
{
    // ...
}
```

来源：`USDPrimViewModel.h`

### 变体集操作

```cpp
FUsdVariantSetsViewModel VariantSetsVM;
VariantSetsVM.UpdateVariantSets(Stage, TEXT("/RootModel"));

for (auto& SetVM : VariantSetsVM.VariantSets)
{
    // 获取当前选择
    FString CurrentVariant = *SetVM->VariantSelection;

    // 切换变体
    SetVM->SetVariantSelection(MakeShared<FString>(SetVM->Variants[1].Get()));
}
```

来源：`USDVariantSetsViewModel.h`

## Demo 示例

以下是一个最小示例，展示如何在编辑器模块中创建一个简单的 USD 舞台查看器，列出所有基元名称。

**USDMiniViewer.h**

```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "UsdWrappers/UsdStage.h"

class USDSTAGEEDITORVIEWMODELS_API SUsdMiniViewer : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SUsdMiniViewer) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    void OpenStage(const FString& FilePath);
    TSharedRef<SWidget> MakePrimTree();

    UE::FUsdStageWeak Stage;
};
```

**USDMiniViewer.cpp**

```cpp
#include "USDMiniViewer.h"
#include "USDPrimViewModel.h"
#include "Widgets/Views/STreeView.h"

void SUsdMiniViewer::Construct(const FArguments& InArgs)
{
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(SButton)
            .Text(INVTEXT("Open Stage"))
            .OnClicked_Lambda([this]()
            {
                // 实际应用应使用文件对话框
                OpenStage(TEXT("/Game/MyScene.usda"));
                return FReply::Handled();
            })
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            MakePrimTree()
        ]
    ];
}

void SUsdMiniViewer::OpenStage(const FString& FilePath)
{
    // 创建临时舞台actor（实际需从世界获取或创建）
    // 此处仅演示ViewModel用法
    Stage = UE::FUsdStage::Open(FilePath);
}

TSharedRef<SWidget> SUsdMiniViewer::MakePrimTree()
{
    if (!Stage)
        return SNullWidget::NullWidget;

    auto RootVM = MakeShared<FUsdPrimViewModel>(nullptr, Stage, Stage.GetPseudoRoot());
    RootVM->RefreshData(true);
    RootVM->FillChildren();

    return SNew(STreeView<FUsdPrimViewModelRef>)
        .TreeItemsSource(&RootVM->Children)
        .OnGenerateRow_Lambda([](FUsdPrimViewModelRef Item, const TSharedRef<STableViewBase>& Owner)
        {
            return SNew(STableRow<FUsdPrimViewModelRef>, Owner)
                [
                    SNew(STextBlock).Text(Item->UsdPrim.GetName())
                ];
        })
        .OnGetChildren_Lambda([](FUsdPrimViewModelRef Item, TArray<FUsdPrimViewModelRef>& OutChildren)
        {
            OutChildren = Item->Children;
        });
}
```

## 模块依赖

由于未提供 `USDStageEditorViewModels.Build.cs` 文件，无法直接提取依赖。根据常见实践和头文件引用，该模块可能依赖以下模块：

| 模块 | 用途 |
|---|---|
| `USDStage` | 提供 `FUsdStageWeak`、`FUsdPrim` 等基本包装类 |
| `InputCore` | 输入绑定（因编辑器相关） |
| `Slate` / `SlateCore` | UI 框架（视图模型通常绑定 Slate 控件） |
| `DeveloperSettings` | 如果涉及设置 |
| `UMG` | 如果涉及蓝图控件（此模块不涉及） |
| `WorkspaceMenuStructure` | 编辑器菜单注册 |

实际依赖请参考源码中的 `USDStageEditorViewModels.Build.cs` 文件。

## 维护状态

该模块随整个 USDImporter 插件一起维护，近期更新包括：

- 2025-10-22 `a1039b21` — USD: Disabled UE allocator in USD for Windows.
- 2025-10-17 `be609b71` — [Backout] - CL47041219
- 2025-10-17 `7ab79237` — USD: Disabled UE allocator in USD for Windows.
- 2025-10-03 `d887bd60` — USD: Use the default collision profile for generated static meshes.
- 2025-10-01 `b4449c58` — Anim In Engine: Fix broken linked anim sequences.

### 维护评价

- **创建时间**：2025-10-01，距今约 1 年（按当前日期 2026 年计算）
- **活跃度**：从 git 日志看，该插件在持续接受功能性更新和修复，最近一次实质修改（2025-10-22）在过去半年内
- **稳定性**：标记为实验性（IsBetaVersion=true），但经过多次迭代，基本功能稳定
- **推荐使用**：如果需要在 UE 中导入/编辑 USD，推荐启用此插件。对于 USD 舞台编辑器视图模型，该模块是 USD Stage 编辑器的核心组成部分，可靠性高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/WorkingWithUSD/)（USD 工作流程）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Importers/USDImporter/Source/USDTests)