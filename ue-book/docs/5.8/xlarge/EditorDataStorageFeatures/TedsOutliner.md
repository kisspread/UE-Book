# Teds Outliner

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 大纲视图 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TedsOutliner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

> **注意**：`TedsOutliner` 是 `EditorDataStorageFeatures` 插件 17 个模块之一。本文档聚焦于该模块。完整插件包含 `TedsActorCompatibility`、`TedsAlerts`、`TedsAssetData`、`TedsContentBrowser`、`TedsDebugger` 等共 17 个 Runtime 模块。

---

## 用途

`TedsOutliner` 是 UE5 传统 **Scene Outliner**（场景大纲）的 TEDS 驱动替代方案。它使用 **TEDS（Typed Element Data Storage）** 查询系统来获取、过滤、排序和显示编辑器中的对象行（Actors、文件夹、关卡等），取代了原有的逐对象遍历模型。

**核心设计动机**：
- **性能**：TEDS 使用列式存储和批量查询，大规模场景下远比传统 Outliner 高效
- **统一架构**：所有编辑器 UI（大纲、内容浏览器、属性编辑器等）共用同一套数据存储后端
- **可扩展性**：通过 TEDS 查询描述符（QueryDescription）和列（Column）系统，可以轻松定义新的 Outliner 视图，而无需继承旧的 `ISceneOutlinerMode`
- **现代化过滤系统**：过滤器直接以 TEDS 查询或查询函数的形式定义，支持批量处理

---

## 使用场景

- **大型开放世界关卡**：需要高效显示数万个 Actor 的场景大纲，传统 Outliner 可能卡顿
- **自定义编辑器面板**：需要创建自定义的树形/表格视图来显示 TEDS 数据
- **World Partition 工作流**：与 World Partition 的 Data Layer、Content Bundle、Level Instance 等系统深度集成
- **混合模式**：同时显示 TEDS 行和传统非 TEDS 项目（如自定义文件夹）

---

## 蓝图用法

本模块主要面向 C++ 和编辑器扩展开发，不直接暴露 BlueprintCallable 节点。所有功能通过 C++ API 和编辑器 Widget 系统访问。

---

## C++ 用法

### 头文件引入

```cpp
#include "TedsOutlinerModule.h"
#include "TedsOutlinerImpl.h"
#include "TedsOutlinerFilter.h"
#include "TedsOutlinerHierarchyInterfaces.h"
#include "TedsOutlinerItem.h"
#include "TedsOutlinerHelpers.h"
#include "Widgets/SceneOutlinerWidget.h"
```

### 基本用法：创建一个 TEDS Outliner

通过 `FTedsOutlinerModule` 创建一个基于 TEDS 的 Outliner 面板：

```cpp
#include "TedsOutlinerModule.h"
#include "TedsOutlinerImpl.h"

// 获取模块实例
FTedsOutlinerModule& TedsOutlinerModule = FModuleManager::GetModuleChecked<FTedsOutlinerModule>("TedsOutliner");

// 准备初始化选项
FSceneOutlinerInitializationOptions InitOptions;
InitOptions.bShowHeaderRow = true;
InitOptions.bShowStatusBar = false;

// 准备 TEDS 参数
UE::Editor::Outliner::FTedsOutlinerParams TedsParams(SceneOutlinerPtr);
TedsParams.QueryDescription = MyQueryDescription;  // TEDS 查询描述符
TedsParams.bShowRowHandleColumn = false;
TedsParams.bForceShowParents = true;
TedsParams.bUseDefaultObservers = true;

// 创建 Outliner
TSharedRef<ISceneOutliner> Outliner = TedsOutlinerModule.CreateTedsOutliner(InitOptions, TedsParams);
```

### 定义查询描述符

```cpp
// 定义 TEDS 查询以筛选 Outliner 行
UE::Editor::DataStorage::FQueryDescription QueryDesc;
QueryDesc.All<FTypedElementActorColumn>();  // 只显示 Actor 类型的行

TedsParams.QueryDescription = QueryDesc;
```

### 添加过滤器

```cpp
// 使用查询句柄创建过滤器
auto FilterQuery = Storage->RegisterQuery(
    Storage->Select().All<FVisibleInEditorColumn>()
);
auto VisibleFilter = MakeShared<FTedsOutlinerFilter>(
    FName("ShowVisible"),
    NSLOCTEXT("Outliner", "ShowVisible", "仅可见对象"),
    FilterQuery
);
TedsParams.Filters.Add(VisibleFilter);

// 使用类过滤器
auto ActorFilter = MakeShared<FTedsOutlinerFilter>(
    AActor::StaticClass(),
    nullptr, /* Category */
    true,    /* bInteractiveFilter */
    false    /* bActiveByDefault */
);
TedsParams.Filters.Add(ActorFilter);
```

### 定义列显示

```cpp
// 指定 Outliner 要显示的列
UE::Editor::Outliner::FTedsOutlinerColumnDescription ColumnDesc;
ColumnDesc.GetColumns().Add(StaticStruct<FNameColumn>());
ColumnDesc.GetColumns().Add(StaticStruct<FActorLabelColumn>());
ColumnDesc.GetColumns().Add(StaticStruct<FVisibilityColumn>());

// 设置列参数（优先级、初始可见性）
UE::Editor::Outliner::FTedsOutlinerColumnParams ColParams(
    ESceneOutlinerColumnVisibility::Visible,
    FTedsOutlinerColumnParams::EColumnPriorityGroup::Left
);
ColumnDesc.FindOrAddColumnParams(StaticStruct<FNameColumn>()) = ColParams;

TedsParams.ColumnDescription = ColumnDesc;
```

### 进阶用法：自定义 Widget 构造器

通过继承 `FTedsSceneOutlinerWidgetConstructor` 创建完全自定义的 TEDS Outliner：

```cpp
// SceneOutlinerWidget.h 中的基类
USTRUCT()
struct FMyCustomOutlinerWidgetConstructor : public FTedsSceneOutlinerWidgetConstructor
{
    GENERATED_BODY()

    // 覆写查询描述以定义显示哪些行
    virtual UE::Editor::DataStorage::FQueryDescription GetQueryDescription() const override
    {
        UE::Editor::DataStorage::FQueryDescription Desc;
        Desc.All<FTypedElementActorColumn, FMyCustomTagColumn>();
        return Desc;
    }

    // 覆写列描述以定义显示哪些列
    virtual UE::Editor::Outliner::FTedsOutlinerColumnDescription GetColumnDescription() const override
    {
        TArray<TWeakObjectPtr<const UScriptStruct>> Columns = {
            StaticStruct<FActorLabelColumn>(),
            StaticStruct<FMyCustomColumn>()
        };
        return UE::Editor::Outliner::FTedsOutlinerColumnDescription(Columns);
    }

    // 覆写过滤器
    virtual void GetFilters(UE::Editor::DataStorage::ICoreProvider* DataStorage,
        TArray<TSharedPtr<UE::Editor::Outliner::FTedsOutlinerFilter>>& Filters) const override
    {
        // 添加自定义过滤器
    }

    // 覆写层次结构
    virtual TSharedPtr<UE::Editor::Outliner::ITedsOutlinerHierarchyDataInterface> 
        GetHierarchyData(UE::Editor::DataStorage::ICoreProvider* DataStorage) const override
    {
        // 返回自定义层次接口或 nullptr 表示平铺列表
        return nullptr;
    }
};
```

### 进阶用法：自定义层次结构接口

```cpp
// 实现自定义层次结构
class FMyCustomHierarchyInterface : public ITedsOutlinerHierarchyDataInterface
{
public:
    // 注册查询以追踪层次变化
    virtual void RegisterQueries(
        UE::Editor::DataStorage::ICoreProvider& Storage,
        const UE::Editor::DataStorage::FQueryDescription& OutlinerQueryDescription,
        TWeakPtr<ISceneOutliner> Outliner,
        bool bUsingQueryConditionsSyntax) override
    {
        // 合并自定义查询与 Outliner 查询
    }

    virtual void UnregisterQueries(UE::Editor::DataStorage::ICoreProvider& Storage) override { }

    // 获取父节点
    virtual UE::Editor::DataStorage::RowHandle GetParent(
        const UE::Editor::DataStorage::ICoreProvider& Storage,
        UE::Editor::DataStorage::RowHandle InRow) const override
    {
        // 返回父行句柄
        return UE::Editor::DataStorage::InvalidRowHandle;
    }

    // 遍历子节点
    virtual void WalkDepthFirst(
        const UE::Editor::DataStorage::ICoreProvider& Storage,
        UE::Editor::DataStorage::RowHandle InRow,
        UE::Editor::DataStorage::ICoreProvider::FHierarchyIterationCallback VisitFn,
        UE::Editor::DataStorage::ICoreProvider::ETraversalOrder TraversalOrder) const override
    {
        // 深度优先遍历
    }

    // 遍历直接父节点（支持多父节点情况）
    virtual void ForEachImmediateParent(
        const UE::Editor::DataStorage::ICoreProvider& Storage,
        UE::Editor::DataStorage::RowHandle InRow,
        FParentIterationCallback Callback) override
    {
        // 遍历所有直接父节点
    }
};
```

### 进阶用法：外部过滤器提供器

通过 Widget 工厂注册外部过滤器（`SceneOutlinerWidget.h`）：

```cpp
// 获取 Outliner Widget 工厂
UTedsOutlinerWidgetFactory* Factory = GetMutableDefault<UTedsOutlinerWidgetFactory>();

// 注册外部过滤器提供器
Factory->RegisterExternalFilterProvider(FName("MyPlugin"), 
    [](TArray<TSharedPtr<FTedsOutlinerFilter>>& Filters, 
       UE::Editor::DataStorage::ICoreProvider* DataStorage)
    {
        // 为所有 TEDS Outliner 添加来自你的插件的过滤器
        auto MyFilter = MakeShared<FTedsOutlinerFilter>(
            FName("MyCustomFilter"),
            NSLOCTEXT("MyPlugin", "CustomFilter", "自定义过滤"),
            MyFilterQueryHandle
        );
        Filters.Add(MyFilter);
    }
);
```

### 进阶用法：辅助工具函数

```cpp
#include "TedsOutlinerHelpers.h"

using namespace UE::Editor::Outliner::Helpers;

// 从行句柄获取树项目
FSceneOutlinerTreeItemPtr Item = GetTreeItemFromRowHandle(Storage, OutlinerRef, RowHandle);

// 刷新所有关卡编辑器中的 Outliner
RefreshLevelEditorOutliners();

// 查找包含当前行的 Level Instance
UE::Editor::DataStorage::RowHandle LevelInstanceRow = 
    LevelInstance::FindContainingLevelInstanceRow(Storage, RowHandle);

// 检查是否在编辑中的 Level Instance 层次内
bool bEditing = LevelInstance::IsInEditingLevelInstanceHierarchy(Storage, RowHandle);

// 自然排序键（"Actor2" 排在 "Actor10" 前面）
FString SortKey = BuildNaturalSortKey("MyActor10");
```

---

## Demo 示例

一个最小化的自定义 TEDS Outliner 创建示例：

```cpp
// MyTedsOutliner.h
#pragma once

#include "CoreMinimal.h"
#include "TedsOutlinerModule.h"
#include "TedsOutlinerImpl.h"
#include "TedsOutlinerFilter.h"

namespace MyEditor
{
    class FMyTedsOutliner
    {
    public:
        static TSharedRef<ISceneOutliner> CreateActorOutliner();
        
    private:
        static UE::Editor::DataStorage::FQueryDescription BuildActorQuery();
        static TArray<TSharedPtr<UE::Editor::Outliner::FTedsOutlinerFilter>> BuildFilters(
            UE::Editor::DataStorage::ICoreProvider* Storage);
        static UE::Editor::Outliner::FTedsOutlinerColumnDescription BuildColumns();
    };
}
```

```cpp
// MyTedsOutliner.cpp
#include "MyTedsOutliner.h"
#include "TedsOutlinerFilter.h"

// 需要引入 TEDS 列头文件来引用列类型
#include "Elements/Framework/TypedElementRegistry.h"

namespace MyEditor
{
    TSharedRef<ISceneOutliner> FMyTedsOutliner::CreateActorOutliner()
    {
        FTedsOutlinerModule& Module = 
            FModuleManager::GetModuleChecked<FTedsOutlinerModule>("TedsOutliner");

        // 1. 标准 Scene Outliner 初始化选项
        FSceneOutlinerInitializationOptions InitOptions;
        InitOptions.bShowHeaderRow = true;
        InitOptions.bShowFilterBar = true;

        // 2. TEDS 参数
        FTedsOutlinerParams TedsParams(/*SceneOutliner*/ nullptr);
        TedsParams.QueryDescription = BuildActorQuery();
        TedsParams.ColumnDescription = BuildColumns();
        TedsParams.Filters = BuildFilters(TedsParams.QueryDescription.GetStorage());
        TedsParams.bForceShowParents = true;
        TedsParams.bUseDefaultObservers = true;
        TedsParams.bShowRowHandleColumn = false;
        TedsParams.bShowViewButton = true;

        // 3. 创建并返回 Outliner Widget
        return Module.CreateTedsOutliner(InitOptions, TedsParams);
    }

    UE::Editor::DataStorage::FQueryDescription FMyTedsOutliner::BuildActorQuery()
    {
        UE::Editor::DataStorage::FQueryDescription Desc;
        // 只显示 Actor 类型的行
        Desc.All<FTypedElementActorColumn>();
        return Desc;
    }

    TArray<TSharedPtr<UE::Editor::Outliner::FTedsOutlinerFilter>> FMyTedsOutliner::BuildFilters(
        UE::Editor::DataStorage::ICoreProvider* Storage)
    {
        TArray<TSharedPtr<UE::Editor::Outliner::FTedsOutlinerFilter>> Filters;
        
        // 按类过滤 - 只显示 AStaticMeshActor
        Filters.Add(MakeShared<FTedsOutlinerFilter>(
            AStaticMeshActor::StaticClass(),
            nullptr, /* Category */
            true,    /* bInteractiveFilter */
            false    /* bActiveByDefault */
        ));

        return Filters;
    }

    UE::Editor::Outliner::FTedsOutlinerColumnDescription FMyTedsOutliner::BuildColumns()
    {
        TArray<TWeakObjectPtr<const UScriptStruct>> Columns;
        // 注：实际列类型取决于项目中可用的 TEDS 列结构体
        // 这里展示的是结构，具体列类型需根据 TEDS 注册情况确定
        return UE::Editor::Outliner::FTedsOutlinerColumnDescription(Columns);
    }
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TypedElementFramework` | 类型化元素框架，提供 RowHandle、Column 等基础类型 |
| `TypedElementRuntime` | 类型化元素运行时，选择集和交互接口 |
| `EditorDataStorage` | TEDS 核心数据存储（ICoreProvider） |
| `EditorDataStorageFeatures` | TEDS UI 提供器（IUiProvider） |
| `SceneOutliner` | 传统 Scene Outliner 框架（ISceneOutliner 接口、树项目类型） |
| `QueryStack` | TEDS 查询栈节点系统（FRowFilterNode、FRowSortNode 等） |

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 模式下启用 TEDS Outliner |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑中的 Level Instance 内未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复无效的跨关卡拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退 CL53940377 变更 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏非编辑中 Level Instance 的未加载 Actor（与 bd93e418 重复提交） |

### 维护评价

- **活跃维护中**：近期（2026年5月）仍有密集的功能更新和 Bug 修复
- **实验性状态**：`IsExperimentalVersion=true`，API 随时可能发生破坏性变更
- **快速迭代**：创建仅约 1 年，已有 423 个源文件，架构仍在演进中
- **生产级代码**：尽管标记为实验性，已在 UEFN 等受限环境中启用，说明经过了一定的稳定性验证
- **已知限制**：扩展状态（expansion state）目前通过临时桥接（`FTedsOutlinerExpansionStateBridge`）处理，标注为 `UE_EXPERIMENTAL(5.8)`
- **推荐**：适合需要自定义编辑器大纲视图的高级编辑器扩展场景；不建议在生产蓝图工作流中依赖此模块的稳定性

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]()（暂无）