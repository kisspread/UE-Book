# TEDS Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是基于 TEDS (Editor Data Storage) 构建的编辑器用户界面功能集合。TEDS 是 Unreal Engine 新一代的编辑器数据存储与查询系统，旨在取代传统的、分散的编辑器数据模型（如 UPropertyEditor、SOutliner 等底层数据管理）。

本插件并非单一功能，而是一个功能包，包含了利用 TEDS 重构或新建的多种编辑器工具。其核心目标是提供：
1.  **统一的数据模型**：将不同编辑器工具（如细节面板、大纲视图、资产选择器等）所需的数据（Actor、Component、资产信息、属性等）统一纳入 TEDS 表格中进行管理和查询。
2.  **高性能查询**：利用 TEDS 的查询栈 (QueryStack) 进行高效的数据筛选、聚合和转换，替代传统的遍历和事件驱动模式。
3.  **现代化的 UI 架构**：提供基于 TEDS 数据的标准化 UI 组件（如 `SEverythingPicker`），用于构建下一代编辑器界面。

简而言之，这个插件是 TEDS 系统在编辑器 UI 层面的具体实现，旨在让编辑器工具更快、更灵活、更易于扩展和维护。

## 使用场景

- **开发需要高性能和可组合数据查询的编辑器工具时**：例如，你需要构建一个能够根据多种条件（资产类型、标签、状态、自定义数据）实时筛选和展示海量对象的选择器或浏览器。
- **参与 UE 编辑器开发或需要深度定制编辑器体验时**：如果你希望你的自定义编辑器面板（如自定义资产编辑器、调试工具）与 Epic 新一代的编辑器架构对齐，并获得其带来的性能与灵活性优势。
- **体验实验性的新编辑器功能时**：作为实验性插件，它包含了正在开发中的编辑器组件，如 `TedsOutliner`（基于 TEDS 的大纲视图）、`TedsContentBrowser`（基于 TEDS 的内容浏览器）等。

## 蓝图用法

此插件主要面向 C++ 编辑器扩展开发，其核心 UI 组件 `SEverythingPicker` 及其上下文 (Context) 主要用于 Slate C++ 代码中构建自定义编辑器窗口或面板。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SEverythingPicker` | 万能选择器控件，支持通过标签页 (Tab) 来组织不同的数据查询上下文。 | `SEverythingPicker` |
| `SObjectReferenceContextView` | 用于展示和选择对象引用的上下文视图。可以配置查询条件、列显示和搜索功能。 | `SObjectReferenceContextView` |
| `STypeListContextView` | 用于展示和选择 UStruct 类型（类或结构体）的上下文视图。可以基于基类或查询条件来过滤类型列表。 | `STypeListContextView` |

### 使用示例（蓝图描述）

由于核心功能是 Slate C++ 组件，在蓝图中无法直接创建。典型的使用方式是在 C++ 中构建一个 `SEverythingPicker`，并为其添加 `SObjectReferenceContextView` 或 `STypeListContextView` 作为上下文。例如，创建一个用于选择特定类 Actor 的选择器窗口。

## C++ 用法

### 头文件引入

根据你要使用的模块，引入对应的头文件。对于本插件的 TedsEverythingPicker 模块：

```cpp
#include "SEverythingPicker.h"
#include "TedsPickerContextUtil.h" // 用于 SObjectReferenceContextView 和 STypeListContextView
#include "TedsPickerContext.h"     // 用于 FPickerContext
```

### 基本用法

创建一个简单的 `SEverythingPicker`，并为其添加一个对象引用上下文。
*(来源: `Public/Widgets/SEverythingPicker.h` & `Public/Context/TedsPickerContextUtil.h`)*

```cpp
// 1. 定义一个查询条件（这里假设我们想查询所有静态网格体组件）
FQueryDescription MyQuery = Select().Where().All<UStaticMeshComponent>().Compile();

// 2. 创建 SEverythingPicker 控件
SAssignNew(PickerWidget, SEverythingPicker)
    // 添加一个名为 “Actors” 的上下文
    +SEverythingPicker::Context()
    .Label(LOCTEXT("ActorsTab", "Actors"))
    .Content()
    [
        // 在上下文中放置一个对象引用视图
        SNew(SObjectReferenceContextView)
            .Query(MyQuery)
            .SearchingEnabled(true)
            .OnSelectionChanged_Raw(this, &SMyPickerWindow::OnObjectSelected)
    ];
```

### 进阶用法

使用 `STypeListContextView` 创建一个类型选择器，并结合 `SEverythingPicker` 的多标签功能。
*(来源: `Public/Context/TedsPickerContextUtil.h` & `Public/Widgets/SEverythingPicker.h`)*

```cpp
// 查询所有从 AActor 派生的类信息
UStruct* BaseClass = AActor::StaticClass();

SAssignNew(PickerWidget, SEverythingPicker)
    // 标签1：对象选择器
    +SEverythingPicker::Context()
    .Label(LOCTEXT("ObjectsTab", "Objects"))
    .Content()
    [
        SNew(SObjectReferenceContextView)
            .Query(MyActorQuery)
            .SearchingEnabled(true)
    ]
    // 标签2：类型选择器
    +SEverythingPicker::Context()
    .Label(LOCTEXT("TypesTab", "Actor Types"))
    .Content()
    [
        SNew(STypeListContextView)
            .BaseType(BaseClass) // 基于基类过滤
            .SearchingEnabled(true)
            .OnSelectionChanged_Raw(this, &SMyPickerWindow::OnTypeSelected)
    ];
```

## Demo 示例

一个创建包含对象选择器的 SEverythingPicker 窗口的最小示例。
*(注意：此为片段，需在合适的 Slate 窗口或面板上下文中使用)*

**MyPickerWidget.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "Widgets/SEverythingPicker.h"
#include "TedsPickerContextUtil.h"

class SMyPickerWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyPickerWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<UE::Editor::DataStorage::Picker::SEverythingPicker> Picker;
    void OnActorSelected(UE::Editor::DataStorage::RowHandle InRow, ESelectInfo::Type InSelectInfo);
};
```

**MyPickerWidget.cpp**
```cpp
#include "MyPickerWidget.h"
#include "TedsPickerContext.h"
#include "Elements/Framework/TypedElementLabelColumn.h"
#include "Elements/Framework/TypedElementClassTypeInfoColumn.h"

#define LOCTEXT_NAMESPACE "MyPickerWidget"

void SMyPickerWidget::Construct(const FArguments& InArgs)
{
    // 查询所有Actor
    FQueryDescription ActorQuery = Select().Where().All<AActor>().Compile();

    ChildSlot
    [
        SAssignNew(Picker, UE::Editor::DataStorage::Picker::SEverythingPicker)
            .MinDesiredWidth(500.0f)
            .MinDesiredHeight(400.0f)
            +UE::Editor::DataStorage::Picker::SEverythingPicker::Context()
                .Label(LOCTEXT("ActorsContext", "Actors"))
                .Content()
                [
                    SNew(UE::Editor::DataStorage::Picker::SObjectReferenceContextView)
                        .Query(ActorQuery)
                        .SearchingEnabled(true)
                        .Columns({ FTypedElementLabelColumn::StaticStruct(), FTypedElementClassTypeInfoColumn::StaticStruct() })
                        .OnSelectionChanged(this, &SMyPickerWidget::OnActorSelected)
                ]
    ];
}

void SMyPickerWidget::OnActorSelected(UE::Editor::DataStorage::RowHandle InRow, ESelectInfo::Type InSelectInfo)
{
    // 处理选中的Actor行
    UE_LOG(LogTemp, Log, TEXT("Actor with RowHandle %d selected."), InRow.GetIndex());
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

由于本插件由多个独立模块组成，依赖关系分散在各模块的 `Build.cs` 中。以下是主要模块的**独特**依赖：

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | TEDS 系统的基础框架，提供行、列、查询等核心概念。 |
| `DataStorage` | TEDS 的核心实现，提供具体的表格、查询引擎和存储。 |
| `EditorSubsystem` | 用于注册和管理编辑器子系统，许多 TEDS 功能模块以此为基础。 |
| `ToolWidgets` | 提供通用的编辑器工具窗口和控件库，被选择器等UI模块依赖。 |
| `SourceControl` | `TedsRevisionControl` 模块依赖，用于集成源代码控制信息。 |

**注意**：各个 `Teds*` 模块之间也可能存在相互依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的UEFN环境中启用TEDS大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在TEDS大纲中隐藏非编辑关卡实例内未加载的Actor行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | [TedsOutliner] 修复无效的跨关卡拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | [回滚] - CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 重复提交，隐藏非编辑关卡实例内未加载的Actor行 |

### 维护评价

- **创建时间**：2024年7月，非常年轻。
- **最近更新**：近期（2026年5月）有频繁的更新，主要集中在 `TedsOutliner` 模块，进行功能启用、bug修复和UI优化。这表明 `EditorDataStorageFeatures` 作为一个**功能载体**，其下的具体模块（如Outliner）正在被积极开发和集成。
- **活跃度**：**活跃开发中**。尽管插件本身可能没有直接更新，但其子模块频繁被修改和增强。
- **已知问题**：作为实验性插件，稳定性、API向后兼容性无法保证。从更新记录中可以看到有 `Backout`（回滚）操作，说明代码库可能正在快速迭代和调整。
- **推荐使用**：**谨慎推荐**。适合希望体验和参与UE编辑器未来架构（TEDS）的开发者。不建议在生产环境的关键工具中依赖此实验性插件的任何稳定API。请密切关注UE5主线分支的更新说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)