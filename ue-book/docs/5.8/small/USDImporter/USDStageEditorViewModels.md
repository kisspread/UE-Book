# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | 通用场景描述套件 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `USDStageEditorViewModels` (Runtime), `USDStageEditor` (Runtime), `USDStageImporter` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Epic Games 为 Unreal Engine 提供的 **完整 USD (Universal Scene Description) 生态集成插件**。它远不止是简单的文件导入器。其核心目标是将 USD 作为场景描述和资产交换的中心格式，深度集成到 UE 的工作流中。它解决了以下关键问题：

1.  **场景中心化**：允许在 UE 内打开、查看、编辑和保存 USD Stage 文件，并将更改持久化回 USD 层栈。
2.  **资产协作**：为 VFX、动画和虚拟制片团队提供基于 USD 的高效协作流程，支持多人同时编辑同一资产的不同层。
3.  **动画与变形**：通过 `USDAnimation` 模块支持导入和导出动画数据，处理骨骼网格体、变形目标（Blend Shapes）和控制绑定。
4.  **渲染与材质**：通过 `USDSchemas` 和 `USDStage` 模块将 USD 的材质和渲染属性映射到 UE 的材质系统。
5.  **实时预览与编辑**：通过 `USDStageEditor` 和 `USDStageEditorViewModels` 提供强大的编辑器界面，用于检查 Prim 层级、管理图层、编辑属性和应用变体。

简而言之，它是 UE 进入 USD 世界的门户，旨在取代传统 FBX 流水线，为复杂的、跨平台的内容创建管线提供现代、可扩展的基础。

## 使用场景

-   **影视与虚拟制片**：需要在不同 DCC 工具（Houdini, Maya, Katana）和 UE 之间交换复杂场景和动画时。
-   **大型资产协作**：团队成员需要在不互相覆盖的情况下，对同一个环境或角色资产的不同部分（例如，一人改材质，一人改布局）进行并行工作。
-   **程序化生成**：在 Houdini 中生成基于 USD 的程序化资产，并在 UE 中实时预览和编辑。
-   **资产版本控制**：利用 USD 的层栈和引用特性，对资产进行非破坏性的版本迭代和 A/B 测试。
-   **动画生产**：导入并编辑复杂的角色动画，包括面部动画和控制绑定，并在 Sequencer 中进行最终调整。

## 蓝图用法

该插件主要提供编辑器扩展和 ViewModel 类，用于在蓝图或 Slate UI 中驱动 USD Stage 的交互。核心节点集中在数据管理、视图刷新和状态查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenStage` | 打开一个 USD 文件作为当前 Stage。 | `FUsdStageViewModel` |
| `SaveStage` | 保存当前 Stage 的所有修改到原文件。 | `FUsdStageViewModel` |
| `ImportStage` | 将当前 Stage 的资产实际导入到 UE 内容浏览器。 | `FUsdStageViewModel` |
| `ReloadStage` | 从磁盘重新加载当前 Stage。 | `FUsdStageViewModel` |
| `SetIsExpanded` | 控制 Prim 树视图中的展开/折叠状态。 | `FUsdPrimViewModel` |
| `ToggleVisibility` | 切换一个 Prim 在视口中的可见性。 | `FUsdPrimViewModel` |
| `TogglePayload` | 加载或卸载一个 Prim 的 Payload。 | `FUsdPrimViewModel` |
| `ApplySchema` | 将指定的 USD Schema 应用到当前 Prim。 | `FUsdPrimViewModel` |
| `Refresh` | 根据给定的 Prim 路径和时间码，刷新对象属性字段列表。 | `FUsdObjectFieldsViewModel` |
| `SetFieldValue` | 设置指定属性字段的新值。 | `FUsdObjectFieldsViewModel` |
| `ToggleMuteLayer` | 静音或取消静音一个图层。 | `FUsdLayerViewModel` |
| `EditLayer` | 将指定图层设置为当前编辑目标。 | `FUsdLayerViewModel` |
| `UpdateVariantSets` | 根据指定的 Prim 路径，更新变体集列表及其当前选择。 | `FUsdVariantSetsViewModel` |
| `UpdateReferences` | 刷新指定 Prim 的引用（References/Payloads）列表。 | `FUsdReferencesViewModel` |

### 使用示例（蓝图描述）

1.  **打开并浏览 Stage**：
    *   创建一个 `FUsdStageViewModel` 的实例。
    *   调用 `OpenStage` 节点，传入 `.usd` 文件路径。这会更新 `UsdStageActor`。
    *   创建一个 `FUsdPrimViewModel` 根实例，并将其 `UsdStage` 属性连接到 `FUsdStageViewModel` 的 Stage。
    *   将 `FUsdPrimViewModel` 的 `Children` 数组绑定到一个 Slate TreeView 控件，即可显示 Prim 树。
    *   当用户在树中选择一个 Prim 时，使用该 Prim 的路径调用 `FUsdObjectFieldsViewModel::Refresh`，然后将 `Fields` 数组绑定到一个 ListView，显示其元数据、属性和关系。

2.  **编辑图层与变体**：
    *   创建一个 `FUsdLayerViewModel` 实例，关联当前 Stage。将 `GetChildren()` 的结果绑定到图层树视图。
    *   当用户右键点击一个图层时，可以显示一个上下文菜单，绑定到 `ToggleMuteLayer`、`EditLayer` 等节点。
    *   当用户选择一个 Prim 时，使用其路径调用 `FUsdVariantSetsViewModel::UpdateVariantSets`，然后将 `VariantSets` 数组绑定到 UI，其中每个变体集都有一个下拉框（ComboBox）绑定到 `VariantSelection`。

## C++ 用法

本插件的 C++ 用法主要体现在创建和管理 ViewModel 以驱动自定义 UI，以及直接调用底层 USD Stage 操作。

### 头文件引入

```cpp
#include “USDStageViewModel.h“
#include “USDPrimViewModel.h“
#include “USDObjectFieldViewModel.h“
#include “USDLayersViewModel.h“
#include “USDVariantSetsViewModel.h“
#include “USDReferencesViewModel.h“
```

### 基本用法（ViewModel 驱动 UI）

以下示例展示如何在 C++ 中设置一个简单的 Prim 属性编辑器。

```cpp
// 在你的 Slate Widget 或 Actor 中持有这些 ViewModel
TSharedRef<FUsdStageViewModel> StageViewModel = MakeShared<FUsdStageViewModel>();
TSharedRef<FUsdPrimViewModel> RootPrimViewModel = MakeShared<FUsdPrimViewModel>(nullptr, UE::FUsdStageWeak());
TSharedRef<FUsdObjectFieldsViewModel> FieldsViewModel = MakeShared<FUsdObjectFieldsViewModel>();

// 1. 打开 Stage
StageViewModel->OpenStage(TEXT(“/Game/MyAsset.usd“));
if (AUsdStageActor* Actor = StageViewModel->UsdStageActor.Get())
{
    UE::FUsdStageWeak UsdStage = Actor->GetUsdStage();
    // 2. 初始化 Prim ViewModel 树
    RootPrimViewModel = MakeShared<FUsdPrimViewModel>(nullptr, UsdStage, UsdStage->GetPseudoRoot());
    RootPrimViewModel->UpdateChildren(); // 生成第一层子项

    // 3. 当用户选择一个 Prim（例如，从 TreeView 的 OnSelectionChanged 回调）
    auto SelectedPrimVM = /* 从选中项获取 TSharedPtr<FUsdPrimViewModel> */;
    if (SelectedPrimVM.IsValid())
    {
        // 4. 刷新属性视图
        UE::FSdfPath PrimPath = SelectedPrimVM->UsdPrim.GetPath();
        FieldsViewModel->Refresh(UsdStage, *PrimPath.GetString(), UsdStage->GetEditTarget().GetLayer()->GetEndTimeCode());
        // 5. 将 FieldsViewModel->Fields 绑定到 UI Slate ListView
    }
}
```

### 进阶用法（直接操作 Stage）

虽然 ViewModel 提供了高层接口，但你也可以通过 `USDStage` 模块直接操作 USD 对象。

```cpp
#include “USDStageActor.h“
#include “UsdWrappers/UsdStage.h“
#include “UsdWrappers/UsdPrim.h“
#include “UsdWrappers/SdfLayer.h“
#include “UsdWrappers/SdfPath.h“

void MyAdvancedFunction(AUsdStageActor* InStageActor)
{
    UE::FUsdStageWeak UsdStage = InStageActor->GetUsdStage();
    if (!UsdStage) return;

    // 获取或创建一个 Prim
    UE::FUsdPrim Prim = UsdStage->GetPrimAtPath(UE::FSdfPath(“/World/MyProp“));
    if (!Prim)
    {
        Prim = UsdStage->DefinePrim(UE::FSdfPath(“/World/MyProp“), TEXT(“Xform“));
    }

    // 添加一个自定义属性
    UE::FUsdAttribute Attr = Prim.CreateAttribute(
        TEXT(“inputs:myCustomValue“),
        UE::SdfValueTypeNames->Float
    );
    Attr.Set(42.0f);

    // 获取当前编辑图层并保存
    UE::FSdfLayer EditLayer = UsdStage->GetEditTarget().GetLayer();
    EditLayer->Save();
}
```

## Demo 示例

一个最小化示例，展示如何创建一个自定义的 Slate 面板来显示 USD Stage 的属性。

```cpp
// MyUSDPropertyPanel.h
#pragma once
#include “CoreMinimal.h“
#include “Widgets/SCompoundWidget.h“
#include “USDObjectFieldViewModel.h“
#include “USDPrimViewModel.h“
#include “UsdWrappers/UsdStage.h“

class SMyUSDPropertyPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyUSDPropertyPanel) {}
        SLATE_ARGUMENT(TSharedPtr<FUsdPrimViewModel>, PrimViewModel)
        SLATE_ARGUMENT(UE::FUsdStageWeak, UsdStage)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        PrimViewModel = InArgs._PrimViewModel;
        UsdStage = InArgs._UsdStage;
        FieldsViewModel = MakeShared<FUsdObjectFieldsViewModel>();

        ChildSlot
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot().AutoHeight()
            [
                SNew(STextBlock).Text(FText::FromString(TEXT(“Prim Properties“)))
            ]
            + SVerticalBox::Slot().FillHeight(1.0f)
            [
                // 将 ListView 绑定到 FieldsViewModel->Fields
                // 这里需要自定义 Row Widget 来显示 Label, Value 和 Type
                SNew(STextBlock).Text(FText::FromString(TEXT(“List of attributes will appear here...“)))
            ]
        ];

        // 初始刷新
        RefreshProperties();
    }

    void RefreshProperties()
    {
        if (PrimViewModel.IsValid() && UsdStage.IsValid())
        {
            UE::FSdfPath PrimPath = PrimViewModel->UsdPrim.GetPath();
            FieldsViewModel->Refresh(UsdStage, *PrimPath.GetString(), 0.0f);
            // 在这里通知 ListView 刷新
        }
    }

private:
    TSharedPtr<FUsdPrimViewModel> PrimViewModel;
    UE::FUsdStageWeak UsdStage;
    TSharedPtr<FUsdObjectFieldsViewModel> FieldsViewModel;
};
```

## 模块依赖

要使用此插件的任何部分，你的模块通常需要依赖 `USDStage` 或相关的 ViewModel 模块。更具体的功能依赖如下：

| 模块 | 用途 |
|---|---|
| `USDClasses` | USD 核心类和类型定义。 |
| `USDSchemas` | USD 预定义 Schema 到 UE 的映射。 |
| `UsdUtilities` | USD 工具函数和转换器。 |
| `USDStage` | USD Stage 管理、导入和运行时支持。 |
| `USDStageEditor` | USD Stage 编辑器 UI 主模块。 |
| `USDStageEditorViewModels` | 为编辑器 UI 提供数据和行为（ViewModel）。 |
| `USDExporter` | 将 UE 场景/资产导出为 USD。 |
| `USDAnimation` | USD 动画数据支持。 |
| `GeometryCacheUSD` | USD 几何缓存（变形体）支持。 |
| `Sequencer` | 与动画 Sequencer 集成，编辑 USD 动画。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数时产生的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：新增支持分配独立于蓝图的控制绑定。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va… | USD：解决 USD 26.03 更新导致的，当 LOD 级别变化时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了当参数为 64 位时格式化说明符应为 64 位，反之亦然的错误。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：现在可以烘焙曝光动画轨道的所有帧。 |

### 维护评价

**积极维护中**。
-   **创建时间**：插件始于 2018 年，已历经约 7 年发展。
-   **更新频率**：近期（2026 年 4-5 月）有密集的功能性更新和 Bug 修复，表明 Epic Games 仍在持续投入开发，尤其关注动画、渲染和编辑器体验。
-   **活跃状态**：非常活跃。尽管 `.uplugin` 中标记为 `IsBetaVersion: true` 和 `EnabledByDefault: false`，但其功能已相当完整和成熟，是 UE 影视和虚拟制片管线的核心组件之一。
-   **已知限制**：作为 Beta 版本，API 可能仍有变动。对某些 USD 特性的支持可能不完整。
-   **推荐使用**：**强烈推荐**用于任何涉及 USD 工作流、影视制作或需要高级资产协作的项目。它是 Epic 官方维护的解决方案，代表了 UE 在该领域的未来方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]( )