# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容类型待确认） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是 Unreal Engine 基础 TEDS (Typed Element Data Storage) 框架的**高级 UI 功能层**。它并非一个独立的通用功能插件，而是为引擎核心编辑器工具（如内容浏览器、大纲视图、属性编辑器等）提供一套**基于 TEDS 的实验性、高性能替代方案**。

其核心解决的问题是：传统编辑器 UI 通常基于 UObject 或资产注册表（Asset Registry）来获取和显示数据。而 TEDS 系统通过将编辑器中的元素（如 Actor、资产、组件等）抽象为带有不同数据列的**行（Row）**，并使用高性能查询系统来操作它们。`EditorDataStorageFeatures` 中的各个子模块（如 `TedsContentBrowser`、`TedsOutliner`）正是利用 TEDS 的查询和组件化能力，为这些传统 UI 工具构建新的、更具扩展性和性能潜力的前端。

以 `TedsContentBrowser` 模块为例，它实现了 `IContentBrowserViewExtender` 接口，允许内容浏览器使用基于 TEDS 查询（通过 `QueryStack`）和表格/瓦片视图（通过 `TableViewer`）来展示资产，而不是依赖传统的 `FAssetViewItem` 列表。这为深度自定义内容浏览器视图（如添加基于任意 TEDS 数据列的过滤、排序或显示自定义数据列）提供了基础。

**简单来说，这个插件的存在是为了将 UE 编辑器的核心 UI 工具逐步迁移到更现代化、数据驱动的 TEDS 架构上，以提高灵活性和性能。**

## 使用场景

- **你需要高性能、可定制的内容浏览器视图**：当默认内容浏览器的资产展示方式（列表、瓦片）或基于资产注册表的过滤无法满足需求时，TEDS Content Browser 允许你基于任意资产属性或自定义数据列来构建查询和视图。
- **你正在开发深度集成 TEDS 数据的编辑器工具**：如果你的新编辑器面板需要查询和显示引擎中的各种元素（Actor、组件、资产等），并希望利用 TEDS 的查询堆栈和 UI 框架，这个插件提供了现成的集成点和示例。
- **你想实验或测试 TEDS 系统的 UI 能力**：作为 TEDS 生态系统的 UI 展示层，它是学习如何将 TEDS 查询结果转化为 Slate 界面的最佳实践和参考。
- **你正在为 UE5 开发编辑器扩展，并希望使用“下一代”架构**：尽管是实验性的，但它展示了未来编辑器 UI 的一个方向。

## 蓝图用法

根据提供的源码，该模块主要通过 C++ 接口和工厂类注册来提供功能，**没有直接暴露 `BlueprintCallable` 函数给蓝图**。其功能集成在编辑器内容浏览器的视图层。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接蓝图节点） | 功能通过编辑器设置和视图切换启用 | N/A |

### 使用示例（蓝图描述）

无法在蓝图中直接调用该模块的功能。要启用基于 TEDS 的内容浏览器视图，需要在编辑器偏好设置或通过特定的编辑器 UI 交互来切换内容浏览器的视图模式（例如，从传统的“资产视图”切换到“TEDS 资产视图”）。具体交互取决于该实验性功能在编辑器中的集成程度。

## C++ 用法

### 头文件引入

```cpp
#include "TedsContentBrowserModule.h"
#include "TedsContentBrowserAssetViewWidget.h"
#include "ContentBrowserTileViewWidget.h"
```

### 基本用法

以下代码展示了如何利用 `TedsContentBrowser` 模块的核心概念：查询堆栈（Query Stack）和表格查看器（Table Viewer）。这并非直接调用模块的代码，而是理解其内部工作原理的示例。

```cpp
// 引擎内部示例：查询 TEDS 数据并创建查看器（概念性代码）
#include "ICoreProvider.h"
#include "IUiProvider.h"
#include "QueryStack/FRowArrayNode.h"
#include "TableViewer/ITableViewer.h"

using namespace UE::Editor::DataStorage;

// 1. 获取 TEDS 核心提供程序
ICoreProvider* DataStorage = ICoreProvider::Get();
IUiProvider* DataStorageUi = IUiProvider::Get();

// 2. 创建一个查询堆栈节点，用于持有查询结果（行句柄数组）
TSharedPtr<QueryStack::FRowArrayNode> RowQueryStack = MakeShared<QueryStack::FRowArrayNode>();

// 3. 通过 TEDS 查询更新 RowQueryStack 中的数据
// （假设的查询：获取所有带有 FWorldAssetLabel 列的行）
if (DataStorage)
{
    TArray<RowHandle> Results;
    DataStorage->IterateRows(
        FQuery(FCompoundQuery()
            .Add(FTypedElementColumnTypeQuery::Make<UE::Editor::DataStorage::FWorldAssetLabel>()))
        .MakeView(),
        [&](RowHandle Row) { Results.Add(Row); });
    RowQueryStack->SetRows(MoveTemp(Results));
}

// 4. 创建一个表格查看器，并将其绑定到查询堆栈
TSharedPtr<ITableViewer> TableViewer = DataStorageUi->CreateTableViewer(
    FTableViewerInitParams{ /* ... */ },
    RowQueryStack.ToSharedRef());

// 5. 将创建的查看器 Slate 控件添加到你的 UI 中
TSharedRef<SWidget> ViewerWidget = TableViewer->GetWidget();
```

**来源**：基于 `Private/TedsContentBrowserModule.h` 和 `Private/Widgets/ContentBrowserTileViewWidget.h` 中的类定义和用法推断。

### 进阶用法

创建一个自定义的“内容源”（Content Source），并将其注册到 TEDS 内容浏览器系统中。

```cpp
// MyCustomContentSource.h
#pragma once
#include "TedsContentBrowserModule.h" // 为了获取 IContentSource 等接口

class FMyCustomContentSource : public UE::Editor::ContentBrowser::IContentSource
{
public:
    virtual ~FMyCustomContentSource() override = default;

    virtual FName GetName() override { return TEXT("MyCustom"); }
    virtual FText GetDisplayName() override { return NSLOCTEXT("MyCB", "MySource", "My Custom Source"); }
    virtual FSlateIcon GetIcon() override { /* 返回自定义图标 */ }
    
    // 关键：定义如何获取资产列表的初始查询
    virtual void GetAssetViewInitParams(FTableViewerInitParams& OutInitParams) override
    {
        // OutInitParams 可以包含初始 TEDS 查询，用于获取本源需要显示的资产行
        // 例如：只查询带有特定标签的资产
    }
};
```

```cpp
// 在你的编辑器模块 StartupModule 中注册
void FMyEditorModule::StartupModule()
{
    UE::Editor::ContentBrowser::FTedsContentBrowserModule* CBModule = 
        FModuleManager::GetModulePtr<UE::Editor::ContentBrowser::FTedsContentBrowserModule>(TEXT("TedsContentBrowser"));
    if (CBModule)
    {
        // 假设有注册自定义内容源的方法
        // CBModule->RegisterContentSource(MakeShared<FMyCustomContentSource>());
    }
}
```

**来源**：基于 `Private/TedsContentBrowserModule.h` 中 `FTestContentSource` 和 `FTedsContentBrowserModule` 的定义。

## Demo 示例

以下示例展示了如何创建一个简单的 TEDS 小部件工厂，这是扩展 TEDS UI 功能的基础模式。

**MyWidgetFactory.h**
```cpp
#pragma once
#include "EditorDataStorageFactory.h"
#include "SimpleWidgetConstructor.h"
#include "MyWidgetFactory.generated.h"

UCLASS()
class UMyWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual void RegisterWidgetPurposes(UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;
    virtual void RegisterWidgetConstructors(UE::Editor::DataStorage::ICoreProvider& DataStorage, 
                                            UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;
};

USTRUCT()
struct FMySimpleWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()
public:
    FMySimpleWidgetConstructor();

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;
};
```

**MyWidgetFactory.cpp**
```cpp
#include "MyWidgetFactory.h"
#include "SMyCustomWidget.h" // 假设的自定义 Slate 控件

void UMyWidgetFactory::RegisterWidgetPurposes(UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    // 在此声明本工厂提供的小部件目的（Purpose）
    // 例如: DataStorageUi->RegisterWidgetPurpose(FName("MyPurpose"), ...);
}

void UMyWidgetFactory::RegisterWidgetConstructors(UE::Editor::DataStorage::ICoreProvider& DataStorage, 
                                                   UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    // 将本工厂提供的构造器注册到 TEDS 系统
    DataStorageUi->RegisterWidgetConstructor(
        FName("MyWidget"), // 为你的小部件构造器指定一个唯一名称
        MakeShared<FMySimpleWidgetConstructor>()
    );
}

FMySimpleWidgetConstructor::FMySimpleWidgetConstructor()
    : FSimpleWidgetConstructor(/* ... */)
{
}

TSharedPtr<SWidget> FMySimpleWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    // 根据 TargetRow 的数据，创建并返回你的自定义 Slate 控件
    // 例如，读取 TargetRow 上的某个列数据，用于初始化控件
    return SNew(SMyCustomWidget).TargetRow(TargetRow);
}
```

**来源**：基于 `Private/Widgets/ContentBrowserTileViewWidget.h` 和 `TedsContentBrowserAssetViewWidget.h` 中的 `UEditorDataStorageFactory` 和 `FSimpleWidgetConstructor` 子类结构。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心数据存储和查询系统 |
| `QueryStack` | 提供查询结果流式处理的堆栈节点 |
| `TableViewer` | 提供 TEDS 数据的可视化表格/瓦片查看器控件 |
| `TypedElementFramework` | 类型化元素框架，TEDS 的底层元素抽象 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 环境中启用 TEDS 大纲视图 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS 大纲中隐藏非编辑关卡实例内未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | [TEDS大纲] 修复无效的跨关卡拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | [回退] - CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS 大纲中隐藏非编辑关卡实例内未加载的 Actor 行 |

### 维护评价

- **创建时间**：约 1 年前（2024-07-27），是较新的实验性插件。
- **更新频率**：从最近提交看（集中在 2026-05-14），**非常活跃**。更新内容主要集中在 `TedsOutliner` 子模块，包括功能启用、bug 修复和环境适配。
- **维护状态**：**活跃维护中**。作为 Epic 官方主导的实验性项目，它正在快速迭代和集成到编辑器各个部分。
- **注意事项**：该插件被标记为 `IsExperimentalVersion: true` 且默认未启用 (`Installed: false`)。这意味着其 API 和行为可能在不同引擎版本间发生**重大变更**，不建议在生产环境的正式项目中强依赖。它目前是技术预览和内部测试用途。
- **推荐使用**：**仅推荐给希望研究 TEDS 架构、开发编辑器扩展工具链，或参与 UE5 编辑器现代化进程的开发者**。对于常规游戏项目开发，应使用稳定、传统的编辑器 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() （暂无）
- [测试用例]() （源码中未明确指定，可能位于 `Engine/Tests` 相关目录）