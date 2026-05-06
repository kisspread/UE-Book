# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 查询堆栈模块 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资源） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

`TedsQueryStack` 是 TEDS（Typed Element Data Storage）框架中的查询管线引擎。它提供了一组**可组合的节点（Node）**，允许将 TEDS 查询结果进行链式处理：过滤、排序、合并、复制、监视变化等。

该模块解决了以下问题：
- **数据管道化**：将复杂的数据处理拆分为一系列独立的步骤，每个步骤是一个节点，便于复用和单元测试。
- **增量更新**：节点通过修订号（Revision）缓存结果，仅当上游数据变更时才重新计算，提高性能。
- **延迟执行**：排序等耗时操作支持帧级分片（`FTimespan` 限制），防止阻塞主线程。
- **可观测性**：提供 `FRowMonitorNode` 监听列的变化并触发事件，使 UI 能响应数据变动。

它通常被上层模块（如 `TedsOutliner`、`TedsTableViewer`）用作底层数据管道，但也可供自定义编辑器 UI 直接使用。

## 使用场景

- **你需要对 TEDS 查询结果进行排序** → 使用 `FRowSortNode`（支持列比较器）或 `FRowHandleSortNode`（直接按行句柄排序）。
- **你需要从查询结果中选出特定行** → 使用 `FRowFilterNode` 配合谓词。
- **你需要将多个数据集合并为一个** → 使用 `FRowMergeNode`（支持追加、排序、去重、交集）。
- **你需要监听特定列的变化并触发更新** → 使用 `FRowMonitorNode` 配合 `OnMonitoredRowsAdded`/`OnMonitoredRowsRemoved` 委托。
- **你需要对大型排序进行帧级分帧** → 设置 `FTimespan` 参数控制每帧排序时间。
- **你需要将查询句柄（`QueryHandle`）转换为行数组** → 使用 `FRowQueryResultsNode` 或 `FQueryHandleNode` + `FRowQueryResultsNode`。

## 蓝图用法

本模块的所有节点均为 C++ 类，**未暴露到蓝图**。如需在蓝图中使用 TEDS 数据，请通过其他公开蓝图功能的模块（如 `TedsOutliner` 或自定义蓝图函数库）间接实现。

## C++ 用法

### 头文件引入

```cpp
#include "TedsQueryStackInterfaces.h"
#include "TedsQueryNode.h"
#include "TedsRowQueryResultsNode.h"
#include "TedsRowSortNode.h"
#include "TedsRowFilterNode.h"
#include "TedsRowMergeNode.h"
#include "TedsRowMonitorNode.h"
// 其他按需引入
```

### 基本用法

以下示例展示了如何创建一个从 TEDS 查询开始，经过排序和过滤，最终得到行列表的管道。

```cpp
#include "DataStorage/ICoreProvider.h"
#include "TedsQueryNode.h"
#include "TedsRowQueryResultsNode.h"
#include "TedsRowSortNode.h"
#include "TedsRowFilterNode.h"

using namespace UE::Editor::DataStorage;
using namespace UE::Editor::DataStorage::QueryStack;

// 假设已获取 ICoreProvider 引用
ICoreProvider& Storage = /* ... */;

// 1. 创建查询节点：查找所有有 FMyColumn 的行
TSharedPtr<FQueryNode> QueryNode = MakeShared<FQueryNode>(Storage);
{
    FQueryDescription Desc;
    Desc.SelectTedsColumns = { FMyColumn::StaticStruct() };
    QueryNode->SetQuery(Desc);
}

// 2. 将查询结果转换为行节点
TSharedPtr<FRowQueryResultsNode> ResultsNode = MakeShared<FRowQueryResultsNode>(
    Storage, QueryNode, FRowQueryResultsNode::ESyncFlags::RefreshOnQueryChange
);

// 3. 按 FMyColumn 的某个字段排序（使用自定义排序器）
//    假设存在一个 FMyColumnSorter : public FColumnSorterInterface 的实现
TSharedPtr<const FColumnSorterInterface> Sorter = MakeShared<FMyColumnSorter>();
TSharedPtr<FRowSortNode> SortNode = MakeShared<FRowSortNode>(
    Storage, ResultsNode, Sorter, FTimespan::FromMilliseconds(5) // 每帧最多 5ms
);

// 4. 过滤结果：只保留满足条件的行
TSharedPtr<FRowFilterNode> FilterNode = MakeShared<FRowFilterNode>(
    &Storage, SortNode,
    [](const ICoreProvider& Provider, RowHandle Row) -> bool
    {
        // 自定义过滤逻辑
        return Provider.GetColumnData(Row, FMyColumn::StaticStruct())->Value > 0;
    }
);

// 5. 获取最终行列表（在 Tick 中调用 Update 后）
FilterNode->Update();
FRowHandleArrayView Rows = FilterNode->GetRows();
```

### 进阶用法

#### 使用监视节点监听列变化

```cpp
// 创建监视节点，监听 FMyColumn 的变化
TSharedPtr<FRowMonitorNode> MonitorNode = MakeShared<FRowMonitorNode>(
    Storage, SortNode, MakeShared<FQueryNode>(Storage) // 可选的查询节点
);
MonitorNode->Update(); // 必须调用 Update 才会刷新

// 绑定事件委托
MonitorNode->OnMonitoredRowsAdded().AddRaw(this, &YourClass::OnRowsAdded);
MonitorNode->OnMonitoredRowsRemoved().AddRaw(this, &YourClass::OnRowsRemoved);
```

#### 合并多个行源

```cpp
TArray<TSharedPtr<IRowNode>> Sources;
Sources.Add(SourceA);
Sources.Add(SourceB);

// 合并方式：Unique 去重并排序
TSharedPtr<FRowMergeNode> MergeNode = MakeShared<FRowMergeNode>(
    Sources, FRowMergeNode::EMergeApproach::Unique
);
```

#### 反转顺序

```cpp
TSharedPtr<FRowOrderInversionNode> InvertNode = MakeShared<FRowOrderInversionNode>(
    SourceNode, true // 启用反转
);
```

#### 使用行复制节点避免双向影响

```cpp
// 当需要独立处理排序结果，又不希望改动原始数据时
TSharedPtr<FRowCopyNode> CopyNode = MakeShared<FRowCopyNode>(SourceNode);
CopyNode->Reset(); // 复制当前父节点行
```

## Demo 示例

以下是一个完整可编译的最小示例，展示如何构建一个简单的管道并获取行数据。

**MyWidget.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "TedsQueryStackInterfaces.h"

class ICoreProvider;

class SMyTedsWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTedsWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

    void Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, const float InDeltaTime) override;

private:
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowQueryResultsNode> ResultsNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowSortNode> SortNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowFilterNode> FilterNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowHandleSortNode> HandleSortNode;
};
```

**MyWidget.cpp**
```cpp
#include "MyWidget.h"
#include "DataStorage/ICoreProvider.h"
#include "DataStorage/Queries/Description.h"
#include "TedsQueryNode.h"
#include "TedsRowQueryResultsNode.h"
#include "TedsRowSortNode.h"
#include "TedsRowFilterNode.h"
#include "TedsRowHandleSortNode.h"

using namespace UE::Editor::DataStorage;
using namespace UE::Editor::DataStorage::QueryStack;

void SMyTedsWidget::Construct(const FArguments& InArgs)
{
    ICoreProvider* Storage = /* 从某个子系统获取 */;
    check(Storage);

    // 查询所有带有 FTagColumn 的行
    TSharedPtr<FQueryNode> QueryNode = MakeShared<FQueryNode>(*Storage);
    FQueryDescription Desc;
    Desc.SelectTedsColumns = { FTagColumn::StaticStruct() };
    QueryNode->SetQuery(Desc);

    // 结果节点：每次查询变化时刷新
    ResultsNode = MakeShared<FRowQueryResultsNode>(
        *Storage, QueryNode, FRowQueryResultsNode::ESyncFlags::RefreshOnQueryChange
    );

    // 按行句柄排序（快速）
    HandleSortNode = MakeShared<FRowHandleSortNode>(ResultsNode);

    // 过滤：仅保留特定条件的行
    FilterNode = MakeShared<FRowFilterNode>(
        Storage, HandleSortNode,
        [](const ICoreProvider& Provider, RowHandle Row) -> bool
        {
            // 实际过滤逻辑，例如检查某列值
            return true;
        }
    );

    // 最终排序：按自定义列排序
    TSharedPtr<const FColumnSorterInterface> Sorter = /* 创建或获取 */;
    SortNode = MakeShared<FRowSortNode>(*Storage, FilterNode, Sorter, FTimespan::FromMilliseconds(3));
}

void SMyTedsWidget::Tick(const FGeometry& AllottedGeometry, const double InCurrentTime, const float InDeltaTime)
{
    // 必须在每帧调用 Update 以处理异步排序等
    if (SortNode.IsValid())
    {
        SortNode->Update();
        // 获取当前行列表
        FRowHandleArrayView Rows = SortNode->GetRows();
        // 更新 UI 显示...
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | TEDS 核心数据存储，提供 `ICoreProvider`、`FQueryDescription`、`RowHandle` 等基础类型 |
| `UETypedElementFramework` | 行句柄数组（`FRowHandleArray`、`FRowHandleArrayView`）类型 |
| `EditorDataStorageFramework` | 提供 `FColumnSorterInterface` 等高级接口 |

**补充说明**：上述依赖为第三方模块使用 `TedsQueryStack` 时必须添加的 `PublicDependencyModuleNames`。本模块自身在 `.Build.cs` 中已包含这些依赖。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module (TedsOutlinerFilter to

### 维护评价

- **创建时间**：2025-09-25（不足 1 个月）
- **近期更新**：最近有多个提交，涉及 Bug 修复和功能增强（排序持久化、层次查看器、过滤器等），表明团队正在积极开发。
- **活跃度**：活跃维护，几乎每日都有提交。
- **已知限制**：目前处于实验性阶段，API 可能频繁变动；部分功能（如 `FRowSortNode` 的排序实现）仍在完善中。
- **推荐使用**：适合尝鲜和配合 TEDS 生态开发，但**不推荐用于生产项目**直至稳定。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsQueryStack/Tests)（存在，但用户未提供，请自行搜索）