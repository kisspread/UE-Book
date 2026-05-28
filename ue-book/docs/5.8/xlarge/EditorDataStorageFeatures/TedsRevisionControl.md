# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS编辑器数据存储特性集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有 (多个Runtime模块) |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnfiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures (TEDS Features) 是 UE5 编辑器的一套实验性 UI 功能集，它**基于 “TEDS: Editor Data Storage” 核心数据存储系统构建**。其主要目标是提供一系列高性能、数据驱动的编辑器 UI 组件，以替代或增强传统的编辑器视图（如大纲、资产浏览器、属性编辑器等）。

该插件解决的核心问题是：**传统编辑器 UI（基于 Slate/UMG 直接绑定资产数据）在处理海量 Actor、资产和复杂场景图时，可能遇到的性能瓶颈和扩展性问题**。TEDS 通过将编辑器数据存储在统一、高效的列式数据库（Editor Data Storage）中，然后基于此数据进行查询和 UI 渲染，从而实现更高的性能和更灵活的数据操作。

## 使用场景

- **大型项目或开放世界游戏**：当你在编辑包含成千上万个 Actor 和资产的超大场景时，使用基于 TEDS 的 “大纲视图” (`TedsOutliner`) 和 “内容浏览器” (`TedsContentBrowser`) 能获得更流畅的滚动和更快的搜索响应。
- **需要自定义或增强编辑器工作流**：如果你需要创建自定义的表格视图来管理特定类型的数据（如任务列表、AI 调试数据），可以使用 `TedsTableViewer` 模块作为基础。
- **需要高性能资产预览和选择**：在 `TedsEverythingPicker` 或自定义面板中快速浏览和选取资产。
- **探索前沿编辑器技术**：作为实验性插件，它代表了 Epic Games 在下一代编辑器数据架构上的探索方向，适合希望了解或提前适配未来技术的开发者。

**不适用于**：对稳定性要求极高的生产环境、不需要处理海量数据的小型项目、或不想引入实验性功能的项目。

## 蓝图用法

由于 TEDS Features 是一个庞大的模块集合，其核心逻辑更多在 C++ 和数据存储查询层面。部分模块（如 `TedsContentBrowser`, `TedsOutliner`）可能提供了一些用于与编辑器框架交互或驱动 UI 的蓝图接口，但这些接口通常较为底层。

**潜在的可扩展点（需查阅具体模块头文件）**：

| 节点/概念 | 说明 | 可能所在模块 |
|---|---|---|
| `数据源` | TEDS UI 组件（如视图、浏览器）的数据源接口，允许你注入或查询自定义数据。 | `TedsQueryStack`, `TedsOutliner` |
| `视图状态` | 控制 TEDS 视图（如大纲树）的展开、过滤、排序等状态。 | `TedsOutliner`, `TedsContentBrowser` |
| `选择器/拾取器` | 用于在 TEDS 驱动的对话框中选择特定类型的数据项。 | `TedsEverythingPicker` |
| `调试工具` | 用于在编辑器中检查 TEDS 数据存储状态的工具。 | `TedsDebugger` |

**使用示例（概念描述）**：
在蓝图中，你通常不会直接创建 TEDS 视图，而是通过 C++ 代码注册自定义的查询和处理器。蓝图主要用于在编辑器工具（Editor Utility Widget）中与已存在的 TEDS 视图进行交互，例如响应用户的选择变化，或触发一次数据刷新。

## C++ 用法

TEDS Features 的 C++ 用法围绕 **“数据存储工厂 (DataStorageFactory)”** 和 **“查询 (Query)”** 展开。

### 头文件引入

根据你使用的具体功能模块，引入对应头文件。
```cpp
#include "TEDS/TedsOutliner/Public/TedsOutlinerModule.h"
#include "TEDS/TedsContentBrowser/Public/TedsContentBrowserModule.h"
#include "EditorDataStorage/Public/EditorDataStorageFactory.h"
```

### 基本用法：注册自定义数据查询

TEDS 的核心是定义查询（Query），用于从数据存储中筛选和组合数据。

```cpp
// 来源于 TedsRevisionControlProcessors.h 和类似模式
// 1. 继承 UEditorDataStorageFactory 来注册你的数据和查询
UCLASS()
class UMyCustomDataFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 定义新的数据列（列是数据存储中的“字段”）
        // DataStorage.RegisterTables<...>();
    }

    void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override
    {
        // 定义查询，用于从数据存储中检索数据
        MyQueryHandle = DataStorage.RegisterQuery(
            UE::Editor::DataStorage::Select(...)
                .Where(...)
                .OrderBy(...)
        );
    }

private:
    UE::Editor::DataStorage::QueryHandle MyQueryHandle = UE::Editor::DataStorage::InvalidQueryHandle;
};
```

### 进阶用法：为 Actor 添加 TEDS 覆盖层

`TedsRevisionControl` 模块展示了如何将版本控制状态（如锁定、修改）显示为 Actor 的覆盖层。这是通过注册处理器（Processor）实现的。

```cpp
// 来源于 RevisionControlProcessors.h
// 在 RegisterQueries 中注册一个处理器，该处理器会在查询结果上执行操作
void URevisionControlDataStorageFactory::RegisterQueries(ICoreProvider& DataStorage)
{
    // 注册一个处理器，当特定条件满足时（如Actor有SCC状态列），为其添加覆盖层组件
    ApplyOverlaysObjectToSCC = DataStorage.RegisterProcessor(
        FProcessorBindngs::Create<
            FTypedElementUObjectPackagePathColumn, // 查询条件
            FSCCStatusColumn                     // 查询条件
        >(),
        // 执行逻辑
        [this](auto& Context, const auto& ...)
        {
            // 为匹配的实体（Entity）添加覆盖层组件
        });
}
```

## Demo 示例

由于 TEDS Features 功能模块众多且高度集成，一个最小的示例是**注册一个自定义的数据存储工厂，定义一个查询并获取数据**。

**MyCustomDataFactory.h**
```cpp
#pragma once

#include "EditorDataStorageFactory.h"
#include "MyCustomDataFactory.generated.h"

// 定义一个简单的自定义数据列
USTRUCT()
struct FMyStatusColumn : public UE::Editor::DataStorage::FColumnData
{
    GENERATED_BODY()
    bool bIsActive = false;
};

UCLASS()
class UMyCustomDataFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    void RegisterTables(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;
    void RegisterQueries(UE::Editor::DataStorage::ICoreProvider& DataStorage) override;

private:
    UE::Editor::DataStorage::QueryHandle AllActiveItemsQuery = UE::Editor::DataStorage::InvalidQueryHandle;
};
```

**MyCustomDataFactory.cpp**
```cpp
#include "MyCustomDataFactory.h"
#include "EditorDataStorage.h"

void UMyCustomDataFactory::RegisterTables(ICoreProvider& DataStorage)
{
    // 注册自定义列
    DataStorage.RegisterColumn<FMyStatusColumn>();
}

void UMyCustomDataFactory::RegisterQueries(ICoreProvider& DataStorage)
{
    // 注册一个查询，用于查找所有 FMyStatusColumn 列且 bIsActive 为 true 的实体
    AllActiveItemsQuery = DataStorage.RegisterQuery(
        Select(
            TEXT("AllActiveItems"),
            FEntityBuilder()
                .Where<FMyStatusColumn>([](const FMyStatusColumn& Status){ return Status.bIsActive; })
        )
    );

    // 你可以在此查询 handle 上附加处理器来对结果进行操作
}
```

## 模块依赖

TEDS Features 依赖于 TEDS 核心系统，这是其独特且必须的依赖。使用前需确保项目启用了相关核心插件。

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心数据存储和查询引擎 |
| `EditorDataStorageCore` | TEDS 核心数据类型和接口定义 |
| `TypedElementFramework` | UE 的类型化元素系统，TEDS 与引擎对象（如 Actor）桥接的基础 |
| `RenderCore` | 部分 UI 覆盖层渲染可能依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的UEFN环境（如Fortnite Creative）中启用TEDS大纲视图。 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从TEDS大纲视图中隐藏未编辑的关卡实例内未加载的Actor行，提升清晰度。 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复TEDS大纲视图中跨关卡拖放导致的无效操作问题。 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退了之前的一个变更（CL53940377）。 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 与 `bd93e418` 相同功能的提交，可能是分支合并或修正。 |

### 维护评价

- **状态**：**活跃维护中**。创建于2024年7月，属于较新的实验性项目。从近期提交记录看（最后更新2026年5月），开发团队正在积极迭代和修复问题。
- **内容**：近期更新集中在 `TedsOutliner` 模块，涉及功能启用（UEFN）、UX改进（隐藏干扰项）和关键Bug修复（跨关卡拖放），表明该项目正在逐步成熟并应用于更多场景。
- **风险**：作为 **`IsExperimentalVersion: true`** 的插件，其API和功能在未来版本中可能发生重大变更，甚至可能被移除或重组。
- **推荐**：适合对编辑器扩展技术有探索兴趣、或项目面临大型数据编辑性能挑战的团队作为研究和原型使用。**不建议**在当前稳定的生产项目中直接依赖其最终用户功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() (暂无)
- [核心依赖插件 (TEDS)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorage)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures/Tests) (如果存在)