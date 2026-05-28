# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

---

## 用途

本插件为 Unreal 编辑器的 **TEDS（Typed Element Data Storage）系统**提供了一整套可组合的 UI 数据处理特性。TEDS 本身是一个高性能的表格式数据存储引擎，而本插件在其之上构建了一套**查询栈（Query Stack）管道框架**，用于解决编辑器 UI 面板（如大纲视图、内容浏览器、属性编辑器、资源拾取器等）中高效、增量地展示和操作海量数据的问题。

核心模块 **TedsQueryStack** 提供了一种**有向无环图（DAG）式的数据处理管道**架构：
- **查询节点（IQueryNode）** 定义从 TEDS 中检索哪些数据
- **行节点（IRowNode）** 对查询结果进行过滤、排序、搜索、合并、层级展开等变换
- **执行器（Executor）** 管道的执行时机，支持协作式后台更新，避免阻塞编辑器主线程

该插件默认**不启用**（`Installed: false`），属于实验性功能。其 17 个模块分别对应编辑器中需要 TEDS 数据支持的不同 UI 区域，全部标记为 Runtime 类型。

---

## 使用场景

- 你需要为编辑器构建一个**高性能的数据驱动面板**（如自定义大纲视图、资产浏览器）→ 使用 TedsQueryStack 构建数据管道
- 你需要对 TEDS 中的大量行数据进行**增量搜索**（异步、按帧分配时间）→ 使用 FColumnsSearchNode / FQuerySearchNode
- 你需要对 TEDS 行数据进行**多列排序**且不能阻塞编辑器 → 使用 FRowSortNode + FCooperativeExecutor
- 你需要展示**层级结构数据**（如 Actor 附着层级）→ 使用 FHierarchyRowNode
- 你需要**合并多个查询结果**并去重/排序 → 使用 FRowMergeNode
- 你需要**监听特定列的变化**并触发回调 → 使用 FRowMonitorNode
- 你的 UI 需要支持**反转排序顺序**切换 → 使用 FRowOrderInversionNode

---

## 蓝图用法

本模块是纯 C++ 框架，不暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 接口。所有操作均在 C++ 层完成。

---

## C++ 用法

### 头文件引入

```cpp
// 核心接口
#include "TedsQueryStackInterfaces.h"

// 查询节点
#include "TedsQueryNode.h"
#include "TedsQueryHandleNode.h"
#include "TedsQueryMergeNode.h"

// 行节点
#include "TedsRowQueryResultsNode.h"
#include "TedsRowFilterNode.h"
#include "TedsRowSortNode.h"
#include "TedsRowHandleSortNode.h"
#include "TedsRowMergeNode.h"
#include "TedsRowCopyNode.h"
#include "TedsRowViewNode.h"
#include "TedsRowArrayNode.h"
#include "TedsRowMonitorNode.h"
#include "TedsRowChangeNotifyNode.h"
#include "TedsRowOrderInversionNode.h"
#include "TedsHierarchyNode.h"

// 搜索
#include "TedsColumnsSearchNode.h"
#include "TedsQuerySearchNode.h"
#include "Searching/SearchUtils.h"

// 执行器
#include "TedsQueryStackExecutor.h"
```

### 核心概念

查询栈由两种节点类型组成，通过父子关系连接成链：

```
IQueryNode（查询节点）
    │
    ▼
FRowQueryResultsNode（查询结果节点） ← 将查询转换为行列表
    │
    ▼
FRowFilterNode（过滤节点）
    │
    ▼
FRowSortNode（排序节点）
    │
    ▼
FRowChangeNotifyNode（通知节点） ← 最终输出，提供行列表给 UI
```

**版本控制机制**：每个节点维护一个 `RevisionId`。当内部状态变化时递增版本号，下游节点通过比较版本号来检测变化并按需更新。

### 基本用法：构建查询管道

以下示例演示如何创建一个带过滤和排序的查询栈管道：

```cpp
// 来源：基于 TedsQueryNode.h, TedsRowQueryResultsNode.h, TedsRowFilterNode.h, TedsRowSortNode.h 的公共 API

#include "TedsQueryStackInterfaces.h"
#include "TedsQueryNode.h"
#include "TedsRowQueryResultsNode.h"
#include "TedsRowFilterNode.h"
#include "TedsRowHandleSortNode.h"
#include "TedsQueryStackExecutor.h"

using namespace UE::Editor::DataStorage;
using namespace UE::Editor::DataStorage::QueryStack;

// 1. 创建查询节点 - 定义要查询的列
FQueryDescription QueryDesc;
QueryDesc.Columns.Add(UMyActorData::StaticStruct());
QueryDesc.Set<FTypedElementUObjectColumn>(); // 只查询有 UObject 的行

auto QueryNode = MakeShared<FQueryNode>(Storage, QueryDesc);

// 2. 将查询转换为行列表节点
auto RowResults = MakeShared<FRowQueryResultsNode>(
    Storage, QueryNode,
    FRowQueryResultsNode::ESyncActions::RefreshOnUpdate);

// 3. 添加过滤节点 - 过滤掉被标记为隐藏的行
auto FilteredRows = MakeShared<FRowFilterNode>(
    &Storage, RowResults,
    [&Storage](const FRowHandle Row) -> bool
    {
        // 自定义过滤逻辑
        return !Storage.GetColumn<FHiddenColumn>(Row).bIsHidden;
    });

// 4. 按句柄排序（用于后续二分查找等优化）
auto SortedRows = MakeShared<FRowHandleSortNode>(FilteredRows);

// 5. 使用执行器驱动更新
auto Executor = FExplicitUpdateExecutor(
    TEXT("MyQueryStack"), SortedRows);

// 每帧调用
Executor.Update();

// 6. 获取最终结果
FRowHandleArrayView ResultRows = SortedRows->GetRows();
```

### 进阶用法：带搜索和通知的完整管道

```cpp
// 来源：基于 TedsQuerySearchNode.h, TedsRowChangeNotifyNode.h, TedsRowMergeNode.h

#include "TedsQuerySearchNode.h"
#include "TedsRowChangeNotifyNode.h"
#include "TedsRowMergeNode.h"
#include "TedsQueryStackExecutor.h"

// 搜索节点：在查询结果的可搜索列中执行文本搜索
auto SearchNode = MakeShared<FQuerySearchNode>(
    Storage, QueryNode,
    FRowQueryResultsNode::ESyncActions::RefreshOnUpdate);

// 启动搜索（异步，可能需要多帧完成）
SearchNode->StartSearch(TEXT("MyActor"));

// 添加变更通知节点
auto NotifyNode = MakeShared<FRowChangeNotifyNode>(
    SearchNode,
    FRowChangeNotifyNode::FOnRowNodeChange::CreateLambda(
        [this](const TSharedPtr<IRowNode>& ChangedNode)
        {
            // 行列表发生变化时刷新 UI
            RefreshListView();
        }));

// 使用协作式执行器（与其他后台任务公平分配 CPU 时间）
auto Executor = FCooperativeExecutor(
    TEXT("SearchPipeline"), Storage, NotifyNode,
    ICoreProvider::ECooperativeTaskPriority::Normal);

// 检查搜索状态
if (SearchNode->IsSearching())
{
    FTimespan SearchTime = SearchNode->GetQuerySearchTime();
    UE_LOG(LogMyModule, Log, TEXT("搜索耗时: %.2f ms"), SearchTime.GetTotalMilliseconds());
}
```

### 进阶用法：合并多个数据源

```cpp
// 来源：基于 TedsRowMergeNode.h, TedsRowQueryResultsNode.h

// 假设有两个不同查询的结果节点
auto ResultsA = MakeShared<FRowQueryResultsNode>(Storage, QueryNodeA);
auto ResultsB = MakeShared<FRowQueryResultsNode>(Storage, QueryNodeB);

// 合并为唯一行列表（去重 + 排序）
TArray<TSharedPtr<IRowNode>> Sources;
Sources.Add(ResultsA);
Sources.Add(ResultsB);

auto MergedNode = MakeShared<FRowMergeNode>(
    Sources,
    FRowMergeNode::EMergeApproach::Unique);

// 或者使用 Repeating 模式找出同时出现在两个数据源中的行
auto IntersectNode = MakeShared<FRowMergeNode>(
    Sources,
    FRowMergeNode::EMergeApproach::Repeating);
```

### 进阶用法：层级数据遍历

```cpp
// 来源：基于 TedsHierarchyNode.h

#include "TedsHierarchyNode.h"

// 获取层级句柄（假设已通过 TEDS API 注册了层级关系）
FHierarchyHandle HierarchyHandle = Storage.GetHierarchyHandle(FActorHierarchy::StaticStruct());

// 顶层行节点（如所有 World Outliner 根节点）
auto TopLevelRows = MakeShared<FRowQueryResultsNode>(Storage, RootQueryNode);

// 展开所有子节点
auto HierarchyNode = MakeShared<FHierarchyRowNode>(
    Storage,
    HierarchyHandle,
    TopLevelRows,
    FHierarchyRowNode::ESyncFlags::Always,
    FHierarchyRowNode::EFilterFlags::None);

// 获取包含所有后代的行列表
FRowHandleArrayView AllRows = HierarchyNode->GetRows();
```

---

## Demo 示例

一个完整的、可编译的最小示例——创建一个查询栈管道，查询所有 Actor 数据，过滤后排序：

### MyQueryStackDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "TedsQueryStackInterfaces.h"
#include "TedsQueryStackExecutor.h"

namespace UE::Editor::DataStorage { class ICoreProvider; }
namespace UE::Editor::DataStorage::QueryStack
{
    class FQueryNode;
    class FRowQueryResultsNode;
    class FRowFilterNode;
    class FRowHandleSortNode;
    class FRowChangeNotifyNode;
}

class FMyQueryStackDemo
{
public:
    void Initialize(UE::Editor::DataStorage::ICoreProvider& Storage);
    void Deinitialize();

    /** 获取当前过滤后的行列表 */
    UE::Editor::DataStorage::FRowHandleArrayView GetFilteredRows() const;

private:
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FQueryNode> QueryNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowQueryResultsNode> ResultsNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowFilterNode> FilterNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowHandleSortNode> SortNode;
    TSharedPtr<UE::Editor::DataStorage::QueryStack::FRowChangeNotifyNode> NotifyNode;

    TUniquePtr<UE::Editor::DataStorage::QueryStack::FExplicitUpdateExecutor> Executor;
};
```

### MyQueryStackDemo.cpp

```cpp
#include "MyQueryStackDemo.h"
#include "TedsQueryNode.h"
#include "TedsRowQueryResultsNode.h"
#include "TedsRowFilterNode.h"
#include "TedsRowHandleSortNode.h"
#include "TedsRowChangeNotifyNode.h"

using namespace UE::Editor::DataStorage;
using namespace UE::Editor::DataStorage::QueryStack;

void FMyQueryStackDemo::Initialize(ICoreProvider& Storage)
{
    // 1. 创建查询：匹配所有包含 FTypedElementUObjectColumn 的行
    FQueryDescription Desc;
    Desc.Set<FTypedElementUObjectColumn>();
    QueryNode = MakeShared<FQueryNode>(Storage, Desc);

    // 2. 查询结果 → 行列表（每次 Update 时检测变化后刷新）
    ResultsNode = MakeShared<FRowQueryResultsNode>(
        Storage, QueryNode, FRowQueryResultsNode::ESyncActions::RefreshOnUpdate);

    // 3. 过滤：只保留带有特定标记的行
    FilterNode = MakeShared<FRowFilterNode>(
        &Storage, ResultsNode,
        [](const FRowHandle Row) -> bool
        {
            // 示例：始终保留所有行
            return true;
        });

    // 4. 排序
    SortNode = MakeShared<FRowHandleSortNode>(FilterNode);

    // 5. 变更通知
    NotifyNode = MakeShared<FRowChangeNotifyNode>(
        SortNode,
        FRowChangeNotifyNode::FOnRowNodeChange::CreateLambda(
            [](const TSharedPtr<IRowNode>&)
            {
                UE_LOG(LogTemp, Log, TEXT("查询栈行列表已更新"));
            }));

    // 6. 创建显式更新执行器
    Executor = MakeUnique<FExplicitUpdateExecutor>(
        TEXT("MyDemoStack"), NotifyNode);
}

void FMyQueryStackDemo::Deinitialize()
{
    Executor.Reset();
    NotifyNode.Reset();
    SortNode.Reset();
    FilterNode.Reset();
    ResultsNode.Reset();
    QueryNode.Reset();
}

FRowHandleArrayView FMyQueryStackDemo::GetFilteredRows() const
{
    return NotifyNode.IsValid() ? NotifyNode->GetRows() : FRowHandleArrayView();
}
```

---

## 模块依赖

TedsQueryStack 模块的公共依赖：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心提供器（`ICoreProvider`、`QueryHandle`、`RowHandle` 等） |
| `TypedElementFramework` | 类型化元素框架（`FRowHandleArray`、`FRowHandleArrayView` 等行句柄基础设施） |

其他模块依赖均类似——全部建立在 TEDS 核心和 TypedElement 框架之上。无特殊第三方依赖。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在非编辑关卡实例中隐藏未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复跨关卡拖放操作的错误 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退变更 CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑关卡实例中未加载的 Actor 行 |

### 维护评价

- **活跃维护**：近 3 次更新集中在 2026 年 5 月，集中在 TedsOutliner 子模块的功能完善和 Bug 修复
- TedsQueryStack 模块本身相对**稳定成熟**——近期无直接修改，说明核心管道架构已基本定型
- 作为实验性插件（`IsExperimentalVersion=true`，`Installed=false`），API 随时可能发生变化，需关注版本迁移
- **推荐使用**：如果你正在为 TEDS 数据构建编辑器 UI，这是必经之路。但需注意实验性标记意味着接口可能不稳定
- **注意**：本插件默认未启用，使用前需在 `.uproject` 或插件设置中手动启用

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() （暂无）
- [TedsQueryStack 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsQueryStack)