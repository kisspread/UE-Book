# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI 组件、查询栈、兼容层） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

---

## 用途

EditorDataStorageFeatures 是一组基于 TEDS（Typed Element Data Storage）构建的**实验性编辑器 UI 特性**。它为 UE5 编辑器的各类面板和功能提供了基于数据存储的现代化实现。

该插件解决了以下核心问题：

1. **编辑器 UI 与数据存储的桥接**：通过 17 个子模块，将编辑器中的 Actor 属性、资产浏览、大纲视图、属性编辑器等 UI 功能统一到 TEDS 数据存储框架上
2. **Actor 属性双向同步**：将 Actor 的移动性、可见性、标签、父级、Socket 等属性在 TEDS 列和 Actor 对象之间双向同步
3. **World Partition 元数据查询**：为 World Partition 环境中的 Actor 提供数据层（Data Layer）、内容包（Content Bundle）和子包（Sub Package）的列式查询支持
4. **查询栈（Query Stack）机制**：提供声明式的查询节点系统，支持行过滤、结果回调、层级展示等复杂数据流

**为什么存在**：TEDS 是 UE5 正在推进的数据存储架构改革，此插件是 TEDS 在编辑器 UI 层面的具体落地实现。它将传统的 Actor 属性访问模式转变为 ECS 风格的列式查询模式，为未来编辑器性能优化（如大规模场景下的大纲视图）奠定基础。

---

## 使用场景

- 你需要在自定义编辑器面板中以高性能方式查询和展示大量 Actor 属性 → 使用 TedsQueryStack + TedsOutliner
- 你需要获取 World Partition 环境中的 Actor 数据层或内容包信息 → 使用 TedsActorCompatibility 中的 World Partition 列
- 你需要在 TEDS 数据存储中维护 Actor 属性的双向同步 → 使用 TedsActorCompatibility 的各类 Factory 查询
- 你需要在编辑器中实现资产选择器（Everything Picker）→ 使用 TedsEverythingPicker
- 你需要为 TEDS 数据添加版本控制集成 → 使用 TedsRevisionControl
- 你需要调试 TEDS 数据存储的内部状态 → 使用 TedsDebugger / TedsTableViewer

---

## 模块架构

本插件包含 17 个子模块，按功能可分为以下几类：

### 数据兼容层
| 模块 | 功能 |
|---|---|
| `TedsActorCompatibility` | Actor 属性与 TEDS 列的双向同步（移动性、可见性、标签、父级、Socket 等） |
| `TedsEditorCompatibility` | 编辑器对象与 TEDS 的兼容适配 |
| `TedsTypedElementBridge` | Typed Element 与 TEDS 数据存储之间的桥接 |

### 编辑器 UI 功能
| 模块 | 功能 |
|---|---|
| `TedsOutliner` | 基于 TEDS 的编辑器大纲视图 |
| `TedsContentBrowser` | 基于 TEDS 的内容浏览器 |
| `TedsPropertyEditor` | 基于 TEDS 的属性编辑器 |
| `TedsEverythingPicker` | 通用选择器/拾取器 |
| `TedsTableViewer` | TEDS 数据表查看器 |

### 基础设施
| 模块 | 功能 |
|---|---|
| `TedsQueryStack` | 声明式查询节点栈系统 |
| `TedsAssetData` | 资产数据在 TEDS 中的管理 |
| `TedsTypeInfo` | TEDS 类型信息注册 |
| `TedsOperations` | TEDS 数据操作接口 |

### 辅助功能
| 模块 | 功能 |
|---|---|
| `TedsAlerts` | 编辑器告警/通知系统 |
| `TedsDebugger` | TEDS 数据存储调试工具 |
| `TedsRevisionControl` | 版本控制集成 |
| `TedsSettings` | TEDS 相关设置 |
| `UnifiedFavorites` | 统一收藏夹功能 |

---

## 蓝图用法

本插件主要面向 C++ 层面的编辑器扩展，蓝图 API 较少。TEDS 列通过 `USTRUCT` 定义，可在蓝图查询系统中使用。

### 核心列（Column）

以下列定义在 `TedsActorCompatibility` 模块中，可在 TEDS 查询中引用：

| 列/标签 | 说明 | 所在头文件 |
|---|---|---|
| `FTedsActorMobilityColumn` | 存储 Actor 场景组件的移动性 | `TedsActorMobilityColumns.h` |
| `FTedsActorSocketColumn` | 存储 Actor 附加到的 Socket 名称 | `TedsActorSocketColumns.h` |
| `FTedsActorUncachedLightsTag` | 标识需要评估未缓存静态光照交互的 Actor | `TedsActorUncachedLightsColumns.h` |
| `FWorldPartitionDataLayerColumn` | 存储 World Partition 数据层名称 | `TedsActorWorldPartitionColumns.h` |
| `FWorldPartitionContentBundleColumn` | 存储 World Partition 内容包显示名称 | `TedsActorWorldPartitionColumns.h` |
| `FWorldPartitionSubPackageColumn` | 存储关卡实例 Actor 的子包名称 | `TedsActorWorldPartitionColumns.h` |
| `FLevelInstanceEditingColumn` | 标识正在编辑的关卡实例 Actor | `TedsLevelInstanceColumns.h` |
| `FLevelInstanceTag` | 标识底层对象为 ILevelInstanceInterface 的行 | `TedsLevelInstanceColumns.h` |
| `FInLevelInstanceTag` | 标识位于关卡实例内部的行 | `TedsLevelInstanceColumns.h` |
| `FActorComponentTypeTag` | 标识 Actor 组件类型行 | `TedsActorComponentCompatibilityColumns.h` |

---

## C++ 用法

### 头文件引入

```cpp
// TEDS 核心接口
#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "Elements/Interfaces/TypedElementDataStorageUiInterface.h"

// Actor 兼容性列
#include "Columns/TedsActorMobilityColumns.h"
#include "Columns/TedsActorSocketColumns.h"
#include "Columns/TedsActorWorldPartitionColumns.h"
#include "Columns/TedsLevelInstanceColumns.h"
#include "Columns/TedsActorComponentCompatibilityColumns.h"

// 查询栈
#include "QueryStackNodes/RowQueryCallbackResultsNode.h"
```

### 基本用法：注册自定义 TEDS 查询

通过继承 `UEditorDataStorageFactory` 并重写 `RegisterQueries`，在 TEDS 中注册自定义查询。

```cpp
// 来源: Private/Compatibility/TedsActorMobilityQueries.h

UCLASS()
class UMyActorDataStorageFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 注册一个查询：为新 Actor 添加移动性列
        RegisterActorAddMobilityColumn(DataStorage);
    }

private:
    void RegisterActorAddMobilityColumn(UE::Editor::DataStorage::ICoreProvider& DataStorage) const
    {
        // 使用 DataStorage API 注册查询
        // 查询条件：匹配 Actor 行且没有 FTedsActorMobilityColumn 列
        // 动作：为匹配行添加 FTedsActorMobilityColumn
    }
};
```

### 基本用法：定义 TEDS 列

```cpp
// 来源: Public/Columns/TedsActorMobilityColumns.h

// 定义一个可排序的列，存储 Actor 的移动性
USTRUCT(meta = (DisplayName = "Mobility"))
struct FTedsActorMobilityColumn final : public FEditorDataStorageColumn
{
    GENERATED_BODY()

    UPROPERTY(meta = (Sortable))
    TEnumAsByte<EComponentMobility::Type> Mobility = EComponentMobility::Movable;
};

// 定义一个标签（Tag），不存储数据，仅用于标记
USTRUCT(meta = (DisplayName = "Uncached Lights"))
struct FTedsActorUncachedLightsTag final : public FEditorDataStorageTag
{
    GENERATED_BODY()
};
```

### 进阶用法：双向同步模式

TEDS Actor 兼容层的核心模式是**双向同步**：Actor 属性 → TEDS 列，TEDS 列 → Actor 属性。

```cpp
// 来源: Private/Compatibility/TedsActorVisibilityQueries.h

UCLASS()
class UActorVisibilityDataStorageFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 1. 为新 Actor 添加可见性列
        RegisterActorAddVisibilityColumn(DataStorage);

        // 2. Actor → TEDS 同步：当 FTypedElementSyncFromWorldTag 存在时，
        //    将 Actor 的可见性复制到 TEDS 列
        RegisterActorVisibilityToColumnQuery(DataStorage);

        // 3. TEDS → Actor 同步：当 FTypedElementSyncBackToWorldTag 存在时，
        //    将 TEDS 列的可见性写回 Actor
        RegisterVisibilityColumnToActorQuery(DataStorage);
    }
};
```

**同步标记说明**：
- `FTypedElementSyncFromWorldTag`：触发从 Actor/World 到 TEDS 列的同步
- `FTypedElementSyncBackToWorldTag`：触发从 TEDS 列到 Actor/World 的同步

### 进阶用法：QueryStack 节点

```cpp
// 来源: Private/ActorComponentDebugHierarchyWidget/QueryStackNodes/RowQueryCallbackResultsNode.h

// FRowQueryCallbackResultsNode 是一个查询栈节点，
// 配合查询和回调函数，可以读取、过滤查询结果行，并输出 0 或多个结果行

using EmitRowFn = TFunctionRef<void(TArrayView<const RowHandle>)>;
using CallbackFn = TFunction<void(
    IDirectQueryContext&,
    TArrayView<const RowHandle>,
    EmitRowFn EmitRows
)>;

// 创建节点：绑定查询节点 + 回调函数
auto CallbackNode = MakeShared<FRowQueryCallbackResultsNode>(
    DataStorage,
    QueryNode,
    [](IDirectQueryContext& Context, TArrayView<const RowHandle> Rows, EmitRowFn EmitRows)
    {
        // 在回调中过滤和收集行
        TArray<RowHandle> FilteredRows;
        for (RowHandle Row : Rows)
        {
            // 对每行进行逻辑处理...
            // ...
        }
        // 发射结果行
        EmitRows(MakeArrayView(FilteredRows));
    }
);
```

---

## Demo 示例

一个最小示例：自定义 TEDS 工厂，注册包含移动性列的 Actor 表查询。

### MyActorMobilityFactory.h

```cpp
// MyActorMobilityFactory.h
#pragma once

#include "Elements/Interfaces/TypedElementDataStorageFactory.h"
#include "CoreMinimal.h"
#include "MyActorMobilityFactory.generated.h"

UCLASS()
class UMyActorMobilityFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    virtual void PreRegister(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    virtual void PreShutdown(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    virtual void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

private:
    void RegisterMobilitySyncQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) const;

    UE::Editor::DataStorage::TableHandle ActorTable{UE::Editor::DataStorage::InvalidTableHandle};
};
```

### MyActorMobilityFactory.cpp

```cpp
// MyActorMobilityFactory.cpp
#include "MyActorMobilityFactory.h"
#include "Columns/TedsActorMobilityColumns.h"
#include "Elements/Framework/TypedElementDataStorageWidget.h"

void UMyActorMobilityFactory::PreRegister(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 在预注册阶段可以创建自定义表
}

void UMyActorMobilityFactory::PreShutdown(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    // 清理资源
}

void UMyActorMobilityFactory::RegisterQueries(
    UE::Editor::DataStorage::ICoreProvider& DataStorage)
{
    RegisterMobilitySyncQueries(DataStorage);
}

void UMyActorMobilityFactory::RegisterMobilitySyncQueries(
    UE::Editor::DataStorage::ICoreProvider& DataStorage) const
{
    // 此处使用 DataStorage 的查询注册 API
    // 具体 API 取决于 TEDS 核心模块（EditorDataStorage 提供）
    // 
    // 典型模式：
    // 1. 为匹配 Actor 条件的行添加 FTedsActorMobilityColumn
    // 2. 当 SyncFromWorld 时，从 Actor 的 Mobility 属性写入列
    // 3. 当 SyncBackToWorld 时，从列写回 Actor 的 Mobility 属性
    //
    // 实际查询注册方式请参考 TedsActorCompatibility 模块中的实现
}
```

---

## 模块依赖

由于本插件包含 17 个子模块，以下列出各模块的关键依赖关系（基于模块名称推断）：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` (EditorDataStorage) | TEDS 核心数据存储引擎，所有 Teds* 模块的基础 |
| `TypedElementFramework` | Typed Element 框架，提供 `ITypedElementDataStorageFactory` 等基类 |
| `LevelInstanceEditor` | 关卡实例编辑器模块，`TedsLevelInstance` 依赖 |
| `WorldPartition` | World Partition 框架，`TedsActorCompatibility` 的 WP 列依赖 |
| `QueryStack` | 查询栈基础设施（可能内置于 `TedsQueryStack`） |

**注意**：各子模块的具体 Build.cs 依赖请参阅对应的 `.build.cs` 文件。所有子模块均继承标准 Core/Engine 依赖。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 模式中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS 大纲中隐藏非编辑关卡实例内的未加载 Actor |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS 大纲中跨关卡拖放的无效操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退之前的提交 CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑关卡实例中的未加载 Actor 行 |

### 维护评价

- **创建时间**：2024-07-27，约 2 年历史
- **活跃度**：**非常活跃** — 2026 年 5 月仍有密集的功能更新和 bug 修复
- **实验性标记**：`IsExperimentalVersion = true`，`Installed = false`，需手动启用
- **模块规模**：423 个源文件、17 个子模块，属于大型插件
- **发展方向**：从 commit 历史看，TEDS 大纲视图（TedsOutliner）正在积极开发中，已支持 UEFN 受限模式、关卡实例编辑等高级场景
- **推荐状态**：作为 Epic 官方实验性插件，质量有保障，但 API 可能随版本变动。**不建议在生产环境中直接依赖**，适合用于学习 TEDS 架构和编辑器扩展开发的研究性项目

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [TedsActorCompatibility 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsActorCompatibility)
- [TedsOutliner 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsOutliner)
- [TedsQueryStack 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsQueryStack)
- [TedsTableViewer 模块](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsTableViewer)