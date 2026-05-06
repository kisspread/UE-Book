# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容插件） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`EditorDataStorageFeatures` 插件为 **TEDS（Typed Element Data Storage）** 实验性框架提供了一套丰富的编辑器 UI 特性。这些特性构建在 TEDS 核心之上，允许开发者以表格、层级视图、平铺视图等形式可视化并操作 TEDS 中的数据行。

其中 `TedsTableViewer` 模块是该插件的核心 UI 组件，提供：

- **表格/列表视图**（`STedsTableViewer`）：类似 `SListView` 的 TEDS 数据浏览器，支持多列自定义、排序、过滤和搜索。
- **层级视图**（`STedsTreeView` / `SHierarchyViewer`）：支持树形展开/折叠的层级数据展示，适用于有父子关系的数据（如 Actor 层级）。
- **复合层级视图**（`STedsCompositeHierarchyViewer`）：集成搜索框和过滤栏的“开箱即用”完整视图。
- **平铺视图**（`STedsTileViewer`）：以瓦片形式展示每个 TEDS 行，适用于缩略图或图标列表。
- **行详情面板**（`SRowDetails`）：显示一个 TEDS 行上所有列的详细内容。
- **过滤系统**（`STedsFilterBar`、`FTedsFilter`）：通过查询栈（Query Stack）对 TEDS 数据行进行 AND/OR 过滤，支持自定义过滤函数和按类过滤。
- **搜索框**（`STedsSearchBox`）：基于文本匹配的搜索功能。
- **列系统**：通过 `FTedsTableViewerColumn` 将 TEDS 列映射到 UI 列，支持自定义 widget 构造器、排序器、头部行等。

该插件解决了在 TEDS 生态中快速构建数据浏览、选择、编辑界面的需求，特别适合编辑器工具面板的开发。

## 使用场景

- 你在开发一个需要显示和选择编辑器内 Actor/对象列表的工具面板 → 使用 `SHierarchyViewer` 或 `STedsCompositeHierarchyViewer`。
- 你需要展示一组结构化数据（如资产元数据、属性表），并支持多列排序和自定义列 → 使用 `STedsTableViewer`。
- 你想提供一个“搜即可见”的过滤搜索体验 → 使用 `STedsFilterBar` + `STedsSearchBox` 组合。
- 需要查看某个 TEDS 行上的所有列/标签的详细信息 → 使用 `SRowDetails`。
- 数据行以图标或缩略图展示（如材质球、纹理） → 使用 `STedsTileViewer`。

## 蓝图用法

该模块主要提供 C++ API，Slate 控件不支持蓝图直接构造。但以下核心类型和行为可暴露给蓝图：

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无 | 模块核心为 C++ Slate 控件，无蓝图可调用函数。`FTedsRowHandle` 可作为蓝图变量进行传递，但不支持直接通过蓝图节点创建视图。 | - |

**说明**：若需在蓝图中使用，需通过 C++ 父类创建控件并暴露为蓝图函数库。

## C++ 用法

### 头文件引入

```cpp
#include "Widgets/STedsTableViewer.h"
#include "Widgets/STedsHierarchyViewer.h"
#include "Widgets/Composite/STedsCompositeHierarchyViewer.h"
#include "Widgets/STedsFilterBar.h"
#include "Widgets/STedsSearchBox.h"
#include "Widgets/SRowDetails.h"
#include "Widgets/STedsTileViewer.h"
#include "TedsTableViewerModel.h"
#include "TedsFilter.h"
#include "HierarchyViewerIntefaces.h"
```

### 基本用法

#### 1. 创建一个简单的表格视图

```cpp
using namespace UE::Editor::DataStorage;

// 假设已有 TEDS 数据存储和查询栈
TSharedPtr<QueryStack::IRowNode> RowQueryStack = MakeShared<...>(); // 从某处获得

// 定义显示的列
TArray<TWeakObjectPtr<const UScriptStruct>> Columns;
Columns.Add(FTypedElementLabelColumn::StaticStruct());
Columns.Add(FTypedElementClassTypeInfoColumn::StaticStruct());

// 构造表格视图
SAssignNew(MyTableViewer, STedsTableViewer)
    .QueryStack(RowQueryStack)
    .Columns(Columns)
    .ListSelectionMode(ESelectionMode::Type::Multi)
    .OnSelectionChanged_Lambda([](RowHandle SelectedRow) { /* 处理选择 */ });
```

*来源：`Public/Widgets/STedsTableViewer.h`*

#### 2. 创建层级视图

```cpp
TSharedPtr<IHierarchyViewerDataInterface> HierarchyData = 
    MakeShared<FHierarchyViewerData>(FHierarchyHandle::SomeHandle); // 根据实际情况

SAssignNew(MyHierarchyViewer, SHierarchyViewer)
    .AllNodeProvider(RowQueryStack)
    .Columns({
        FTypedElementLabelColumn::StaticStruct(),
        FTypedElementClassTypeInfoColumn::StaticStruct()
    })
    .OnSelectionChanged_Lambda([](RowHandle Row) { /* ... */ })
    .DefaultExpansionState(SHierarchyViewer::EExpansionState::Expanded), // 默认展开
    HierarchyData);
```

*来源：`Public/Widgets/STedsHierarchyViewer.h`*

#### 3. 使用复合层级视图（含搜索和过滤）

```cpp
TArray<FTedsFilterData> Filters;
Filters.Emplace(
    FName("MyFilter"),
    FText::FromString("My Filter"),
    FText::FromString("Filters based on custom condition"),
    FName("Icons.Filter"),
    nullptr,
    [](const RowHandle& InRow) -> bool { /* 返回 true 表示保留 */ }
);

SAssignNew(MyCompositeViewer, STedsCompositeHierarchyViewer)
    .HierarchyViewerArgs(SHierarchyViewer::FArguments()
        .AllNodeProvider(RowQueryStack)
        .Columns(Columns)
        .CellWidgetPurpose("CellWidget"))
    .Filters(Filters)
    .ClassFilters({ UBlueprint::StaticClass() })
    .UseSectionsForCategories(false), // 默认不分组
    HierarchyData);
```

*来源：`Public/Widgets/Composite/STedsCompositeHierarchyViewer.h`*

#### 4. 添加自定义列

```cpp
// 创建自定义 widget 构造器
TSharedPtr<FTypedElementWidgetConstructor> CustomConstructor = ...;

// 构造 FTedsTableViewerColumn
TSharedRef<FTedsTableViewerColumn> CustomColumn = MakeShared<FTedsTableViewerColumn>(
    FName("CustomColumn"),
    CustomConstructor,
    { FMyCustomColumn::StaticStruct() }
);

// 添加到视图
MyTableViewer->AddCustomRowWidget(CustomColumn);
```

*来源：`Public/TedsTableViewerColumn.h`*

#### 5. 过滤数据行

```cpp
// 构建过滤节点
TSharedPtr<QueryStack::IRowNode> FilteredNode;
SAssignNew(MyFilterBar, STedsFilterBar)
    .InFilterableRowNode(RowQueryStack)
    .OutFilteredNode(&FilteredNode)
    .Filters(FilterArray)
    .OnFilterChanged_Lambda([&]() { /* 更新视图的 QueryStack */ });

// 将 FilteredNode 作为表格视图的新数据源
MyTableViewer->SetQueryStack(FilteredNode);
```

*来源：`Public/Widgets/STedsFilterBar.h`*

### 进阶用法

#### 多视图协同

将 `STedsFilterBar`、`STedsSearchBox` 和 `STedsTableViewer` 组合，实现完整的搜索过滤交互：

```cpp
TSharedPtr<QueryStack::IRowNode> FilteredNode;
TSharedPtr<QueryStack::IRowNode> SearchNode;

SAssignNew(SearchBox, STedsSearchBox)
    .InSearchableRowNode(FilteredNode.IsValid() ? FilteredNode : RowQueryStack)
    .OutSearchNode(&SearchNode);

MyTableViewer->SetQueryStack(SearchNode);
```

#### 自定义层级数据接口

实现 `IHierarchyViewerDataInterface` 以支持自定义父子关系：

```cpp
class FMyHierarchyData : public IHierarchyViewerDataInterface
{
public:
    virtual RowHandle GetParent(const ICoreProvider& Storage, RowHandle InRow) const override
    {
        // 返回父级 row handle，或 InvalidRowHandle
        FParentColumn* ParentCol = Storage.GetColumn<FParentColumn>(InRow);
        return ParentCol ? ParentCol->Parent : InvalidRowHandle;
    }
};

TSharedPtr<IHierarchyViewerDataInterface> MyHierarchyData = MakeShared<FMyHierarchyData>();
SAssignNew(MyHierarchyViewer, SHierarchyViewer, MyHierarchyData)
    .AllNodeProvider(RowQueryStack)
    .Columns({ ... });
```

*来源：`Public/HierarchyViewerIntefaces.h`*

## Demo 示例

以下是一个可在编辑器模块中编译的最小示例，展示如何创建并显示一个简单表格视图。

### TedsTableViewerDemo.h

```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "DataStorage/Handles.h"
#include "TedsTableViewerModel.h"

namespace UE::Editor::DataStorage
{
    class STedsTableViewer;
}

class STedsTableViewerDemo : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(STedsTableViewerDemo) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<UE::Editor::DataStorage::STedsTableViewer> TableViewer;
    TSharedPtr<UE::Editor::DataStorage::FTedsTableViewerModel> Model;
};
```

### TedsTableViewerDemo.cpp

```cpp
#include "TedsTableViewerDemo.h"
#include "Widgets/STedsTableViewer.h"
#include "Elements/Columns/TypedElementLabelColumns.h"
#include "Elements/Columns/TypedElementTypeInfoColumns.h"

void STedsTableViewerDemo::Construct(const FArguments& InArgs)
{
    // 获取 TEDS 核心接口
    using namespace UE::Editor::DataStorage;
    ICoreProvider* DataStorage = ...;   // 需通过 Feature 获取
    IUiProvider* DataStorageUi = ...;

    // 构造一个简单的查询栈：从所有行中获取
    // 实际应用中需要从具体数据源获得
    TSharedPtr<QueryStack::IRowNode> AllRowsNode = ...;

    // 定义列
    TArray<TWeakObjectPtr<const UScriptStruct>> Columns = {
        FTypedElementLabelColumn::StaticStruct(),
        FTypedElementObjectTypeInfoColumn::StaticStruct()
    };

    // 构造表格视图
    ChildSlot
    [
        SNew(STedsTableViewer)
            .QueryStack(AllRowsNode)
            .Columns(Columns)
            .ListSelectionMode(ESelectionMode::Type::Single)
            .OnSelectionChanged_Lambda([this](RowHandle Selected)
            {
                UE_LOG(LogTemp, Log, TEXT("Selected row: %llu"), Selected.RowHandle);
            })
    ];
}
```

## 模块依赖

以下列出 `TedsTableViewer` 模块（基于其公开头文件推断的依赖）的关键外部模块。标准 Core/Engine/Slate 等已省略。

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | 提供 TEDS 核心数据存储接口（`ICoreProvider`）、查询栈、行句柄等 |
| `TypedElementDataStorageUI` | 提供 UI 构造器系统（`IUiProvider`、`FTypedElementWidgetConstructor`） |
| `EditorWidgets` | Slate 控件基础（`SBasicFilterBar` 等） |
| `Slate` | Slate UI 框架（`STreeView`、`SListView`、`SHeaderRow`） |
| `ToolMenus` | 过滤器下拉菜单管理 |
| `ApplicationCore` | 输入/焦点等 |

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S
- 2025-09-25 `8d9818a1` [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module (TedsOutlinerFilter to ...)

### 维护评价

- **创建时间**：2025-09-25（约 0 年）。
- **更新频率**：非常活跃，几乎每周都有功能性提交。
- **内容**：主要专注于视图层功能补全（复合视图、搜索、过滤、排序持久化）及 bug 修复。
- **稳定性**：标记为 Experimental，`IsExperimentalVersion=true`，API 可能频繁变动。
- **推荐使用**：适合在实验性项目或自定义编辑器工具中使用，但需注意 API 不稳定，可能随 UE 版本升级需调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [TEDS 介绍文档（假设存在）](https://docs.unrealengine.com/5.7/...)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsTableViewer/Tests)