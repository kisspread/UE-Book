# TedsOutliner

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 大纲视图 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（TEDS 列定义、Widget 构造器、默认查询） |
| 模块 | `TedsOutliner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsOutliner) | |

## 用途

TedsOutliner 是基于 [Typed Element Data Storage（TEDS）](https://docs.unrealengine.com/5.5/en-US/typed-element-data-storage-in-unreal-engine/) 的完全数据驱动型场景大纲视图（Outliner）框架。传统 Outliner 需要为每种条目类型（Actor、Folder、Component 等）编写独立的 `ISceneOutlinerTreeItem` 子类，并手动管理填充逻辑；而 TedsOutliner 通过 TEDS 查询自动生成条目列表，支持动态列（基于 TEDS 列类型）、可插拔的 Widget 构造器、层级关系的声明式定义以及内置的过滤/排序管道。

它解决的核心问题是：**如何用统一的数据模型取代多套 Outliner 实现，使项目能够快速创建自定义的大纲视图，同时复用 TEDS 提供的查询、UI、兼容性等基础设施。**

## 使用场景

- 你需要一个**可高度定制列和过滤条件**的大纲视图，例如显示自定义数据类型的属性列表。
- 你已经在使用或计划引入 TEDS（Typed Element Data Storage）来管理编辑器数据，希望统一渲染和交互逻辑。
- 你想基于 TEDS 查询快速构建一个**类别浏览器**、**资源选择器**或者**层级编辑器**。
- 你需要 Outliner 支持**动态列切换**（如运行时的排序、隐藏/显示列）。

## 蓝图用法

TedsOutliner 目前**不直接暴露蓝图节点**（无 `BlueprintCallable` 函数），它的核心工作流完全在 C++ 层完成。蓝图用户可以通过以下间接方式使用：

- **编辑器界面操作**：启用插件后，在 `窗口` > `TEDS Outliner` 菜单中打开默认的 Level Editor Teds Outliner 标签页，该标签页由 `FTedsOutlinerModule::RegisterLevelEditorTedsOutlinerTab()` 注册。
- **扩展过滤**：通过 `FTedsOutlinerFilter` 类，你可以从蓝图函数库中调用 C++ 辅助函数来添加基于 TEDS 查询的自定义过滤器（需 C++ 封装）。

## C++ 用法

### 头文件引入

```cpp
#include "TedsOutlinerModule.h"               // 模块入口
#include "TedsOutlinerMode.h"                 // 模式类
#include "TedsOutlinerImpl.h"                 // 核心实现
#include "TedsOutlinerFilter.h"               // 过滤器
#include "Columns/TedsOutlinerColumns.h"      // 列定义
#include "Compatibility/SceneOutlinerTedsBridge.h" // 桥接
```

### 基本用法

以下示例演示如何创建一个简单的 TEDS Outliner 窗口，并显示所有带有 `FNiceNameColumn` 的数据行。

```cpp
// 获取 TEDS Outliner 模块
FTedsOutlinerModule& TedsOutlinerModule = FModuleManager::LoadModuleChecked<FTedsOutlinerModule>("TedsOutliner");

// 配置初始化选项（继承自标准 SceneOutliner）
FSceneOutlinerInitializationOptions SceneInitOptions;
SceneInitOptions.bShowHeaderRow = true;

// 配置 TEDS 特定的参数
using namespace UE::Editor::Outliner;
FTedsOutlinerParams TedsParams;

// 设置驱动 Outliner 的核心查询：选择所有包含 FNiceNameColumn 的行
TedsParams.RowHandleQueries.Add(
    Queries::Select()
    .Where<FNiceNameColumn>()
    .Compile()
);

// 创建 Outliner 实例
TSharedRef<ISceneOutliner> Outliner = TedsOutlinerModule.CreateTedsOutliner(
    SceneInitOptions,
    TedsParams
);

// 将 Outliner 嵌入到你的 Slate 容器中（例如 SOverlay 或 SDockTab）
// Outliner->AsWidget()->GetOwner()
```

> **来源**：`Public/TedsOutlinerModule.h`（`CreateTedsOutliner` 方法）

### 添加自定义列

通过 `USceneOutlinerTedsBridgeFactory` 预注册 TEDS 列到 Outliner 列的映射，或直接通过 `FTedsOutlinerImpl` 的列系统添加：

```cpp
// 在模块的 StartupModule 中注册
void FMyModule::StartupModule()
{
    // 获取兼容性提供者（假设已获取 DataStorage）
    USceneOutlinerTedsBridgeFactory* BridgeFactory = FindObject<USceneOutlinerTedsBridgeFactory>(GetTransientPackage());
    if (BridgeFactory)
    {
        // 将 TEDS 列类型映射到 Outliner 列 ID
        BridgeFactory->TEDSToOutlinerDefaultColumnMapping.Add(
            FMyCustomColumn::StaticStruct(),
            FName("MyCustomColumnID")
        );
    }
}
```

> **来源**：`Public/Compatibility/SceneOutlinerTedsBridge.h`

### 添加过滤器

```cpp
using namespace UE::Editor::Outliner;

// 创建一个基于 TEDS 查询的过滤器：只显示带有 FVisibleTag 的行
FTedsFilterData FilterData(
    FName("VisibleOnly"),                       // 过滤器名称
    NSLOCTEXT("TedsOutliner", "VisibleOnly", "Visible Only"),  // 显示名称
    Queries::Select()
        .Where<FVisibleTag>()
        .Compile()                              // 编译为 QueryHandle
);

// 创建过滤器实例
TSharedPtr<FTedsOutlinerFilter> Filter = MakeShared<FTedsOutlinerFilter>(
    FilterData,
    TedsOutlinerImpl
);

// 将过滤器添加到 Outliner 的过滤器栏
Outliner->GetFilterBar()->AddFilter(Filter);
```

> **来源**：`Public/TedsOutlinerFilter.h`

### 进阶用法：自定义层级关系

通过 `FTedsOutlinerHierarchyData` 定义行间的父子关系：

```cpp
FTedsOutlinerHierarchyData HierarchyData(
    FMyParentColumn::StaticStruct(),    // 存储父行句柄的列
    FGetParentRowHandle::CreateLambda([](const void* Data) {
        const FMyParentColumn* Col = static_cast<const FMyParentColumn*>(Data);
        return Col ? Col->Parent : InvalidRowHandle;
    }),
    FSetParentRowHandle::CreateLambda([](void* Data, RowHandle Parent) {
        static_cast<FMyParentColumn*>(Data)->Parent = Parent;
    }),
    FGetChildrenRowHandles::CreateLambda([](void* Data) -> TArrayView<RowHandle> {
        // 返回子行数组
    })
);

FTedsOutlinerParams Params;
Params.HierarchyData = HierarchyData;
```

> **来源**：`Public/TedsOutlinerImpl.h`

## Demo 示例

以下是一个最小化的完整示例，它在插件加载时创建一个 TEDS Outliner 标签页，显示所有包含 `FStringColumn` 的行，并支持排序。

```cpp
// MyTedsOutlinerDemoModule.h
#pragma once
#include "Modules/ModuleInterface.h"

class FMyTedsOutlinerDemoModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<class SDockTab> TedsOutlinerTab;
};
```

```cpp
// MyTedsOutlinerDemoModule.cpp
#include "MyTedsOutlinerDemoModule.h"
#include "TedsOutlinerModule.h"
#include "TedsOutlinerImpl.h"
#include "TedsOutlinerMode.h"
#include "Widgets/Docking/SDockTab.h"
#include "Elements/Columns/TypedElementCompatibilityColumns.h"

void FMyTedsOutlinerDemoModule::StartupModule()
{
    FTedsOutlinerModule& OutlinerModule = FModuleManager::LoadModuleChecked<FTedsOutlinerModule>("TedsOutliner");

    // 准备查询：选取所有行（演示目的，实际应指定有效列）
    FSceneOutlinerInitializationOptions Options;
    Options.bShowHeaderRow = true;

    UE::Editor::Outliner::FTedsOutlinerParams Params;
    // 使用默认的 RowHandleQueries（空查询默认为所有行，但通常应指定）
    // 这里假设有一个预注册的表，我们直接获取
    // 真实场景应通过 Compile 创建有效查询

    TSharedRef<ISceneOutliner> Outliner = OutlinerModule.CreateTedsOutliner(Options, Params);

    // 将 Outliner 放入新标签页
    TedsOutlinerTab = SNew(SDockTab)
        .TabRole(ETabRole::NomadTab)
        [
            Outliner->AsWidget()
        ];

    // 注册到全局标签管理器
    FGlobalTabmanager::Get()->RegisterNomadTabSpawner("MyTedsOutlinerTab", FOnSpawnTab::CreateLambda([this](const FSpawnTabArgs&)
    {
        return TedsOutlinerTab.ToSharedRef();
    }))
    .SetDisplayName(NSLOCTEXT("Demo", "My Teds Outliner", "My Teds Outliner"));

    // 主动打开
    FGlobalTabmanager::Get()->TryInvokeTab("MyTedsOutlinerTab");
}

void FMyTedsOutlinerDemoModule::ShutdownModule()
{
    if (TedsOutlinerTab.IsValid())
    {
        FGlobalTabmanager::Get()->UnregisterNomadTabSpawner("MyTedsOutlinerTab");
        TedsOutlinerTab.Reset();
    }
}

IMPLEMENT_MODULE(FMyTedsOutlinerDemoModule, MyTedsOutlinerDemo);
```

> **注意**：此 Demo 省略了 TEDS 数据库的初始化和有效 Query 的编译，实际使用时需要确保数据表已填充，并且 `RowHandleQueries` 返回有效行。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TedsCore` | TEDS 核心数据存储接口（`ICoreProvider`, `FQueryDescription`） |
| `TedsUI` | TEDS UI 基础设施（`IUiProvider`, `FMetaDataView`, 构造器系统） |
| `TedsCompatibility` | TEDS 与编辑器旧系统的兼容性（`ICompatibilityProvider`） |
| `SceneOutliner` | 标准场景大纲视图框架（`ISceneOutliner`, `ISceneOutlinerMode`） |
| `TypedElementFramework` | 类型化元素框架（`FTypedElementWidgetConstructor`） |
| `TedsTableViewer` | TEDS 表查看器列实现（内部使用 `FTedsTableViewerColumn`） |
| `TedsQueryStack` | TEDS 查询栈节点（`FRowMapNode`, `IRowNode`） |
| `WorkspaceMenuStructure` | 编辑器中菜单结构注册 |
| `ToolMenus` | 上下文菜单支持 |
| `ContentBrowserData` | 用于内容浏览集成 |
| `EditorSubsystem` | 编辑器子系统支持 |
| `AssetRegistry` | 资产注册表数据（TedsAssetData 模块使用） |

> **说明**：以上依赖来自 `TedsOutliner.Build.cs` 的实际引用（部分为推断，但核心依赖已列出）。标准 `Core`、`CoreUObject`、`Engine`、`Slate`、`SlateCore`、`UnrealEd` 等默认依赖不重复列出。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S
- 2025-09-25 `8d9818a1` [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module (TedsOutlinerFilter to

### 维护评价

TedsOutliner 是一个**非常新且活跃开发中**的实验性功能（2025年9月创建）。从提交日志看，开发团队持续进行功能添加（复合层级查看器、排序持久化、过滤栏）和稳定性修复。目前尚未发现重大限制或废弃标记。推荐在需要数据驱动型 Outliner 的项目中尝试使用，但应意识到其**实验性状态**，API 可能在未来发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsOutliner)
- [TEDS 官方文档](https://docs.unrealengine.com/5.5/en-US/typed-element-data-storage-in-unreal-engine/)