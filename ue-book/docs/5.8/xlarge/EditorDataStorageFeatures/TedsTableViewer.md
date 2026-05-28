```markdown
# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器 UI 功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI 小部件和查询组件） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

---

## 用途

**TEDS: Editor Data Storage Features** 是 Epic 为其内部 **TEDS（Typed Element Data Storage）** 框架构建的一套实验性编辑器 UI 组件库。TEDS 本身是一个基于 ECS（实体-组件-系统）模式的编辑器数据存储引擎，而此插件在此基础上提供了**数据可视化和交互的 UI 层**。

这个插件解决的核心问题是：**如何高效地将 TEDS 中存储的海量编辑器数据（Actor、资产、组件等）以多种视图形式呈现给用户，并支持搜索、过滤、排序、层级展开、拖放等交互操作。**

传统编辑器 UI（如 Outliner、Content Browser）各自使用独立的数据模型和刷新机制，而此插件将所有这些 UI 统一到 TEDS 的查询栈（Query Stack）架构上，使得：
- 数据变更自动推送到 UI（响应式更新）
- 多个视图可以共享同一份数据
- 过滤、排序、搜索可以高效级联组合

---

## 模块总览

| 模块 | 职责 |
|---|---|
| **TedsTableViewer** | 核心 UI 组件：表格视图、层级视图、磁贴视图、过滤栏、搜索框、行详情面板 |
| **TedsOutliner** | 基于 TEDS 的大纲视图（替代传统 World Outliner） |
| **TedsContentBrowser** | 基于 TEDS 的内容浏览器 |
| **TedsPropertyEditor** | 基于 TEDS 的属性编辑器 |
| **TedsQueryStack** | 查询栈基础设施：行节点、过滤节点、排序节点、搜索节点 |
| **TedsEverythingPicker** | 通用数据选择器（类似 "Everything Picker"） |
| **TedsAlerts** | 编辑器告警/通知系统 |
| **TedsSettings** | TEDS 配置管理 |
| **TedsDebugger** | TEDS 调试工具 |
| **TedsOperations** | TEDS 批量操作 |
| **TedsActorCompatibility** | Actor 数据桥接到 TEDS |
| **TedsEditorCompatibility** | 编辑器数据桥接到 TEDS |
| **TedsAssetData** | 资产数据管理 |
| **TedsRevisionControl** | 版本控制集成 |
| **TedsTypeInfo** | 类型信息注册与查询 |
| **TedsTypedElementBridge** | Typed Element 与 TEDS 的桥接层 |
| **UnifiedFavorites** | 统一收藏夹功能 |

---

## 使用场景

- 你在开发一个需要**高性能表格视图**的编辑器工具，数据存储在 TEDS 中 → 使用 `STedsTableViewer`
- 你需要一个支持**层级展开**的树形视图（类似大纲），数据来自 TEDS 查询 → 使用 `SHierarchyViewer` / `STedsCompositeHierarchyViewer`
- 你要构建一个**资产选择器**或**磁贴浏览**界面 → 使用 `STedsTileViewer`
- 你需要对 TEDS 数据进行**实时过滤和搜索** → 使用 `STedsFilterBar` + `STedsSearchBox`
- 你要查看某个 TEDS 行的**所有列详情**（类似属性面板）→ 使用 `SRowDetails` / `SRowDetailsNavigator`

---

## 蓝图用法

本插件主要面向 C++ 编辑器扩展开发，不提供蓝图暴露的 API。所有核心接口均为 C++ Slate Widget。

---

## C++ 用法

### 头文件引入

```cpp
// 核心表格/层级视图
#include "Widgets/STedsTableViewer.h"
#include "Widgets/STedsHierarchyViewer.h"
#include "Widgets/Composite/STedsCompositeHierarchyViewer.h"
#include "Widgets/STedsTileViewer.h"

// 过滤与搜索
#include "Widgets/STedsFilterBar.h"
#include "Widgets/STedsSearchBox.h"

// 行详情
#include "Widgets/SRowDetails.h"

// 模型与列定义
#include "TedsTableViewerModel.h"
#include "TedsTableViewerColumn.h"
#include "TedsFilter.h"

// 层级接口
#include "HierarchyViewerIntefaces.h"
```

### 基本用法：创建一个表格视图

> 来源：`Public/Widgets/STedsTableViewer.h` 示例注释

```cpp
// 创建一个基本的 TEDS 表格视图
TSharedPtr<QueryStack::IRowNode> QueryStack = 
    MakeShared<UE::Editor::DataStorage::FQueryStackNode_RowView>(&Rows);

SNew(STedsTableViewer)
    .TableViewerIdentifier(FName("MyTable"))
    .QueryStack(QueryStack)
    .Columns({
        FTypedElementLabelColumn::StaticStruct(), 
        FTypedElementClassTypeInfoColumn::StaticStruct()
    })
    .CellWidgetPurpose(MyPurposeId)
    .ListSelectionMode(ESelectionMode::Single)
```

### 基本用法：创建一个层级视图

> 来源：`Public/Widgets/STedsHierarchyViewer.h` 示例注释

```cpp
// 创建层级视图，支持树状展开
SNew(SHierarchyViewer)
    .TableViewerIdentifier(FName("MyHierarchy"))
    .AllNodeProvider(MyQueryStackNode)
    .Columns({
        FTypedElementLabelColumn::StaticStruct(), 
        FTypedElementClassTypeInfoColumn::StaticStruct()
    })
    .CellWidgetPurpose(MyPurposeId)
    .PrimaryColumn(FTypedElementLabelColumn::StaticStruct())
```

### 进阶用法：组合层级视图（带搜索、过滤、设置）

> 来源：`Public/Widgets/Composite/STedsCompositeHierarchyViewer.h` 示例注释

```cpp
// 创建带搜索和过滤的组合层级视图
SNew(STedsCompositeHierarchyViewer, HierarchyData)
    .EnableSearching(true)
    .EnableFiltering(true)
    .EnableSettings(true)
    .ShowFilteredParentHierarchy(true)
    .HierarchyViewerArgs(
        SHierarchyViewer::FArguments()
            .AllNodeProvider(FilterNode)
            .Columns({
                FTypedElementLabelColumn::StaticStruct(), 
                FTypedElementClassTypeInfoColumn::StaticStruct()
            })
            .CellWidgetPurpose(PurposeId)
    )
    .Filters(MyCustomFilterArray)
```

### 进阶用法：过滤栏 + 搜索框

> 来源：`Public/Widgets/STedsFilterBar.h`、`Public/Widgets/STedsSearchBox.h`

```cpp
// 创建搜索框
TSharedPtr<QueryStack::IRowNode> OutSearchNode;

SAssignNew(SearchBox, STedsSearchBox)
    .InSearchableRowNode(InputRowNode)
    .OutSearchNode(&OutSearchNode);

// 创建过滤栏
TSharedPtr<QueryStack::IRowNode> OutFilteredNode;

SAssignNew(FilterBar, STedsFilterBar)
    .FilterBarIdentifier(FName("MyFilterBar"))
    .InFilterableRowNode(OutSearchNode)
    .OutFilteredNode(&OutFilteredNode)
    .Filters(MyCustomFilters)  // TArray<TSharedPtr<FTedsFilter>>
    .CommonSectionFilters({FName("CommonFilter1")});
```

### 进阶用法：行详情面板（带导航）

> 来源：`Public/Widgets/SRowDetailsNavigator.h`

```cpp
// 行详情导航器 - 支持面包屑导航的详情面板栈
SNew(SRowDetailsNavigator);

// 设置要查看的行
RowDetailsNavigator->SetRow(MyRowHandle);

// 点击关系项时自动推入新面板，面包屑可回退
```

---

## 核心组件说明

### ITableViewer 接口

所有表格/层级/磁贴视图的统一接口：

| 方法 | 说明 |
|---|---|
| `ForEachSelectedRow()` | 遍历所有选中行 |
| `SetSelection()` | 设置行选中状态 |
| `ScrollIntoView()` | 滚动到指定行 |
| `ClearSelection()` | 清除所有选中 |
| `SetQueryStack()` | 设置查询栈节点（动态数据源） |
| `SetColumns()` | 设置显示的列 |
| `AddCustomRowWidget()` | 添加自定义列（非 TEDS 列） |

### 视图类型对比

| 视图类 | 底层 Slate | 特点 |
|---|---|---|
| `STedsTableViewer` | `SListView` | 平面表格，支持列排序、拖放 |
| `SHierarchyViewer` | `STreeView`（自定义） | 树形层级，支持展开/折叠、层级连线 |
| `STedsCompositeHierarchyViewer` | 包装 `SHierarchyViewer` | 在层级视图基础上集成搜索栏、过滤栏、设置按钮 |
| `STedsTileViewer` | `STileView` | 磁贴布局，每个行显示为一个瓦片 |

### IHierarchyViewerDataInterface

层级数据接口，用于从 TEDS 行中提取父子关系：

| 实现类 | 用途 |
|---|---|
| `FHierarchyViewerData` | 基于单个 `FHierarchyHandle` 的层级数据 |
| `FHierarchyViewerMultiData` | 合并多个层级为统一视图 |
| `FRelationTypeHierarchyViewerData` | 基于 `RegisterRelationType` 注册的直接关系 |

---

## Demo 示例

一个最小可编译示例：创建带过滤功能的 TEDS 表格视图。

```cpp
// MyTedsTablePanel.h
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "Widgets/STedsTableViewer.h"
#include "Widgets/STedsFilterBar.h"
#include "TedsFilter.h"

namespace UE::Editor::DataStorage
{
    class SMyTedsTablePanel : public SCompoundWidget
    {
    public:
        SLATE_BEGIN_ARGS(SMyTedsTablePanel) {}
        SLATE_END_ARGS()

        void Construct(const FArguments& InArgs);

    private:
        TSharedPtr<STedsTableViewer> TableViewer;
        TSharedPtr<STedsFilterBar> FilterBar;
        TSharedPtr<QueryStack::IRowNode> FilteredNode;
    };
}
```

```cpp
// MyTedsTablePanel.cpp
#include "MyTedsTablePanel.h"
#include "Widgets/STedsSearchBox.h"
#include "TypedElementColumns.h" // FTypedElementLabelColumn 等

namespace UE::Editor::DataStorage
{
    void SMyTedsTablePanel::Construct(const FArguments& InArgs)
    {
        // 假设已有一个查询栈节点提供行数据
        TSharedPtr<QueryStack::IRowNode> RowNode = /* ... */;

        // 创建过滤栏
        SAssignNew(FilterBar, STedsFilterBar)
            .FilterBarIdentifier(FName("DemoFilterBar"))
            .InFilterableRowNode(RowNode)
            .OutFilteredNode(&FilteredNode)
            .Filters({});

        // 创建表格视图，数据源来自过滤栏输出
        SAssignNew(TableViewer, STedsTableViewer)
            .TableViewerIdentifier(FName("DemoTable"))
            .QueryStack(FilteredNode)
            .Columns({
                FTypedElementLabelColumn::StaticStruct(),
                FTypedElementClassTypeInfoColumn::StaticStruct()
            })
            .ListSelectionMode(ESelectionMode::Single);

        ChildSlot
        [
            SNew(SVerticalBox)
            + SVerticalBox::Slot()
            .AutoHeight()
            [
                FilterBar.ToSharedRef()
            ]
            + SVerticalBox::Slot()
            .FillHeight(1.0f)
            [
                TableViewer.ToSharedRef()
            ]
        ];
    }
}
```

---

## 模块依赖

### TedsTableViewer 模块依赖

基于头文件中引用的类型推断（Build.cs 未直接展示，但以下模块被核心 API 频繁引用）：

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | `RowHandle`、`UScriptStruct` 列定义、`ITypedElementDataStorageInterface` |
| `EditorDataStorage` (TEDS 核心) | `ICoreProvider`、`IUiProvider`、`QueryStack` 基础设施 |
| `EditorWidgets` | `ITedsWidget`、`FWidgetDropHandler`、通用 Slate 扩展 |
| `ToolWidgets` | `SBasicFilterBar` 基类 |
| `UnrealEd` | `UEditorDataStorageFactory`、编辑器集成 |

> **注意**：所有模块类型均为 `Runtime`，说明此 UI 组件可在运行时使用（不仅限编辑器），但实际用途主要面向编辑器。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 模式中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑关卡实例中未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复跨关卡拖放的无效操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退某次提交 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑关卡实例中未加载的 Actor 行（先于回退） |

### 维护评价

- **创建时间**：2024-07-27，约 2 年前
- **最近更新**：2026-05-20，更新非常活跃（最近 1 周内有多次提交）
- **更新内容**：集中在 TedsOutliner 模块，涉及 UEFN 支持、跨关卡拖放修复等功能性改进
- **实验性状态**：`IsExperimentalVersion=true`，尚未毕业为正式插件
- **API 稳定性**：接口仍在演进中，commit message 中可看到回退操作，说明底层仍在调整
- **推荐程度**：**⚠️ 谨慎使用**。这是 Epic 内部积极开发的实验性框架，API 可能在未来版本中发生破坏性变更。适合用于：
  - 研究 Epic 的编辑器架构方向
  - 开发内部编辑器工具（接受 API 不稳定的风险）
  - 不推荐用于需要长期稳定性的第三方插件

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]()（暂无）
- [TedsTableViewer 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsTableViewer)
```