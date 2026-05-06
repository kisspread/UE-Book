# TedsContentBrowser

> Part of the "TEDS: Editor Data Storage Features" plugin. Provides a TEDS-powered view for the Content Browser.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 内容浏览器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、UI资源） |
| 模块 | `TedsContentBrowser` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsContentBrowser/) | |

---

## 用途

TedsContentBrowser 是编辑器数据存储（TEDS）框架在内容浏览器中的一个试验性集成模块。它的核心作用是用 TEDS 数据驱动的行存储代替传统的资产列表管理，以实现更灵活、可扩展的资产展示方式。

具体来说，它解决了以下问题：

- **传统内容浏览器的局限性**：默认的资产视图（如列表、瓷砖视图）使用固定的数据模型和 UI 绑定，难以自定义列、过滤、排序等行为。
- **利用 TEDS 生态**：TEDS 提供了统一的行存储、查询、UI 工厂等能力，TedsContentBrowser 借助这些能力实现资产视图的完全可定制化——包括列标题、行样式、双击行为、上下文菜单等。
- **实验性性能优化**：TEDS 的延迟加载和批量更新机制有望提升大量资产时的浏览性能。

模块主要提供了以下几个关键组件：

| 组件 | 说明 |
|---|---|
| `FTedsContentBrowserViewExtender` | 实现了 `IContentBrowserViewExtender` 接口，替换或扩展内容浏览器中的默认视图。它内部利用 TEDS 的 `ITableViewer` 和 `FQueryStackNode_RowView` 来驱动行数据的查询与显示。 |
| `UContentBrowserTileViewWidgetFactory` | 注册用于瓷砖视图的 UI 窗口部件（widget）构造器，包括缩略图、标签、文件夹样式等。 |
| `UContentBrowserAssetViewWidgetFactory` | 注册用于资产视图（列表/瓷砖）的默认窗口部件构造器，可自定义资产单元格的显示内容。 |
| `FTestContentSource` | 一个测试用的内容源，用于演示查询驱动的资产列表（例如复用 Outliner 的查询）。 |

---

## 使用场景

- 你需要为内容浏览器添加 **自定义的列**（如自定义元数据列）并希望使用 TEDS 的查询和排序功能。
- 你正在开发一个基于 TEDS 的编辑器工具，希望资产浏览部分能与你的数据存储无缝对接。
- 你想研究 TEDS 如何被用于编辑器 UI 扩展，以作为迁移或实验的参考。

---

## 蓝图用法

当前模块**未暴露任何蓝图可调用的函数或属性**。所有扩展点均位于 C++ 级别，需要通过实现 C++ 接口完成。

---

## C++ 用法

### 头文件引入

```cpp
#include "ContentSources/IContentSource.h"
#include "Experimental/ContentBrowserViewExtender.h"
#include "TedsContentBrowserModule.h"          // 模块入口
#include "Widgets/ContentBrowserTileViewWidget.h"
#include "Widgets/TedsContentBrowserAssetViewWidget.h"
```

### 基本用法

#### 创建并注册 TEDS 内容浏览器视图

```cpp
// 在编辑器模块启动时，创建并注册一个 TEDS 驱动的视图
void FMyEditorModule::StartupModule()
{
    // 获取内容浏览器模块
    IContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<IContentBrowserModule>("ContentBrowser");
    
    // 创建 TEDS 视图扩展器
    TSharedPtr<UE::Editor::ContentBrowser::FTedsContentBrowserViewExtender> ViewExtender =
        MakeShared<UE::Editor::ContentBrowser::FTedsContentBrowserViewExtender>();
    
    // 注册到内容浏览器（通常作为替代默认视图）
    ContentBrowserModule.SetViewExtender(ViewExtender);
}
```

#### 自定义资产视图窗口部件

继承 `FSimpleWidgetConstructor` 并注册，以覆盖特定资产类型的显示样式：

```cpp
// 自定义一个仅显示资产名称的简化列表构造器（伪代码）
class FSimpleNameWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()
public:
    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override
    {
        // 从 TEDS 行中读取资产名称
        if (const FAssetRow* AssetRow = DataStorage->GetColumn<FAssetRow>(TargetRow))
        {
            return SNew(STextBlock).Text(FText::FromString(AssetRow->AssetName));
        }
        return SNullWidget::NullWidget;
    }
};

// 在工厂中注册
void UMyWidgetFactory::RegisterWidgetConstructors(ICoreProvider& DataStorage, IUiProvider& DataStorageUi) const
{
    DataStorageUi.RegisterWidgetConstructor(
        Purpose::GetPurposeName(),
        MakeUnique<FSimpleNameWidgetConstructor>());
}
```

### 进阶用法

#### 使用 `FTedsContentBrowserViewExtender` 的动态行刷新

```cpp
// 当资产列表发生变化时（如文件夹切换），手动刷新 TEDS 视图
ViewExtender->OnItemListChanged(&ItemsSource);   // ItemsSource 是 TArray<TSharedPtr<FAssetViewItem>>*
ViewExtender->RefreshRows(&ItemsSource);
```

#### 双向映射：RowHandle ↔ AssetViewItem

```cpp
// 从行句柄获取对应的 UI 项
TSharedPtr<FAssetViewItem> Item = ViewExtender->GetAssetViewItemFromRow(RowHandle);

// 从 UI 项获取对应的行句柄
DataStorage::RowHandle Row = ViewExtender->GetRowFromAssetViewItem(Item);
```

---

## Demo 示例

以下是一个最小插件模块，演示如何替换内容浏览器默认视图为一个自定义的 TEDS 驱动的视图。

**MyTedsContentBrowserModule.h**
```cpp
#pragma once
#include "Modules/ModuleInterface.h"
#include "Containers/Array.h"
#include "Templates/SharedPointer.h"

namespace UE::Editor::ContentBrowser
{
    class FTedsContentBrowserViewExtender;
}

class FMyTedsContentBrowserModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;

private:
    TSharedPtr<UE::Editor::ContentBrowser::FTedsContentBrowserViewExtender> ViewExtender;
};
```

**MyTedsContentBrowserModule.cpp**
```cpp
#include "MyTedsContentBrowserModule.h"
#include "ContentBrowserModule.h"
#include "TedsContentBrowserModule.h"          // 注册模块依赖
#include "Experimental/ContentBrowserViewExtender.h"

IMPLEMENT_MODULE(FMyTedsContentBrowserModule, MyTedsContentBrowser);

void FMyTedsContentBrowserModule::StartupModule()
{
    // 确保 TEDS 内容浏览器模块已加载
    FModuleManager::LoadModuleChecked<FTedsContentBrowserModule>("TedsContentBrowser");

    IContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<IContentBrowserModule>("ContentBrowser");
    
    ViewExtender = MakeShared<UE::Editor::ContentBrowser::FTedsContentBrowserViewExtender>();
    ContentBrowserModule.SetViewExtender(ViewExtender);
}

void FMyTedsContentBrowserModule::ShutdownModule()
{
    if (ViewExtender.IsValid())
    {
        IContentBrowserModule& ContentBrowserModule = FModuleManager::LoadModuleChecked<IContentBrowserModule>("ContentBrowser");
        ContentBrowserModule.ClearViewExtender();
        ViewExtender.Reset();
    }
}
```

**注意**：需要在你的模块 `Build.cs` 中添加 `TedsContentBrowser` 和 `ContentBrowser` 依赖（详见模块依赖）。

---

## 模块依赖

本模块需要在你的 `Build.cs` 中添加以下依赖（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `TedsCore` | TEDS 核心数据存储接口（通过 `EditorDataStorageFeatures` 插槽） |
| `TedsTableViewer` | TEDS 表格视图组件，用于渲染行数据 |
| `ContentBrowser` | 内容浏览器核心模块，提供 `IContentBrowserViewExtender` 接口 |
| `ContentBrowserAssetView` | 资产视图 UI 组件（可选，用于创建自定义视图） |
| `EditorWidgets` | 编辑器通用窗口部件（如缩略图、标签） |
| `TypedElementFramework` | 类型化元素框架，行句柄和行数组类型 |
| `TedsTypedElementBridge` | TEDS 与类型化元素之间的桥接（可选） |

> 由于本模块高度依赖 TEDS 生态，安装前需确保 `EditorDataStorageFeatures` 插件已启用。

---

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — 修复 TedsTypeInfo 在运行某些 Verse 自动化测试时的 assert
- 2025-10-02 `1f8278e6` — 重新启用 TedsAssetData，解决测试和 FName 问题
- 2025-09-26 `7d070444` — [TEDS Viewers] 允许通过 `IsEnabled` 和 `GetColumnSort` 将排序持久化
- 2025-09-25 `8d9818a1` — [TEDS Viewers] 创建新的复合层级查看器（包含默认的搜索和过滤）
- 2025-09-25 `4161c053` — 添加新的 TEDSFilterBar 窗口部件，并将 TedsFilters 加入 TableViewer 模块

### 维护评价

- **创建时间**：2025-09-25，距今不足 2 个月（截至文档生成时）。
- **更新频率**：非常活跃，几乎每周都有提交，内容为功能增加和问题修复。
- **状态标记**：`IsExperimentalVersion=true`，明确为实验性，API 可能变更。
- **推荐使用**：适合用于体验 TEDS 在内容浏览器中的潜力，以及开发新的资产浏览交互。不建议用于生产项目，因为接口尚未稳定，且会遇到未完毕的功能（如部分列绑定、文件夹视图尚未完全实现）。
- **已知限制**：当前仅实现了瓷砖视图（Tile View）和列表视图（List View）的初始版本；资产预览小部件处于早期阶段；测试用例尚不完整。

---

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [源码（本模块）](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsContentBrowser/)
- [TEDS 官方文档](https://docs.unrealengine.com/5.7/en-US/editor-data-storage/)（英文，实验性）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsContentBrowser/Tests)