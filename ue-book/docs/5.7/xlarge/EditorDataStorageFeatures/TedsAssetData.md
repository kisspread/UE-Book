# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产、配置数据） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

TEDS (Typed Element Data Storage) 是一套基于 ECS（实体组件系统）的数据存储与查询框架，旨在为编辑器提供高性能、可扩展的 UI 和数据管理能力。`EditorDataStorageFeatures` 插件将 TEDS 与各种编辑器子系统（如资产注册表、内容浏览器、大纲视图、属性面板等）桥接起来，使得这些子系统能够利用 TEDS 的行/列模型存储和检索数据，进而实现更灵活、更高效的编辑器体验。

当前文档聚焦于 **TedsAssetData** 子模块，它是该插件中最核心的模块之一，负责将资产注册表（Asset Registry）的数据整合到 TEDS 中。

### TedsAssetData 解决什么问题？

- **统一数据源**：将 `FAssetData`、文件路径、标签元数据等资产相关信息映射到 TEDS 列中，使得任何基于 TEDS 的 UI（如内容浏览器、资产预览面板）都可以直接查询和显示这些数据，而无需重复访问 AssetRegistry。
- **性能优化**：通过批量处理资产添加、更新、删除事件，并利用 TEDS 的查询系统按需刷新，减少主线程开销。
- **元数据缓存**：提供 `FTagsMetadataCache`，对资产标签（Tags）的元数据（如类型、显示名、提示文本）进行缓存，避免反复反射 UClass。
- **虚拟路径支持**：支持将内部资产路径转换为虚拟路径（如考虑插件挂载点、显示所有文件夹等），使路径展示更符合用户预期。
- **丰富的 UI 小部件**：提供一系列基于 TEDS 的资产 UI 组件，如缩略图、标签、磁盘大小、类型图标、名称排序器等，可直接用于内容浏览器、资产预览等面板。

## 使用场景

- **开发基于 TEDS 的自定义编辑器面板**：如果你正在构建一个需要显示和操作资产列表的面板（例如自定义资产管理器、包查看器），可以直接引用 `TedsAssetData` 的列定义和查询，快速获取资产数据。
- **为内容浏览器增加新列或排序功能**：通过 `TedsAssetData` 暴露的列（如 `FAssetNameColumn`、`FDiskSizeColumn`）和自定义排序器，可以轻松在内容浏览器中扩展新的显示列。
- **实现资产预览悬浮窗**：`STedsAssetPreviewWidget` 提供了可复用的资产预览组件，包含头部、缩略图、基本信息、高级信息等区域，可嵌入到任何 Slate UI 中。

## 蓝图用法

本模块为纯 C++ 实现，未暴露任何蓝图可调用函数或属性。所有功能均通过 C++ 接口供其他模块使用。

## C++ 用法

### 头文件引入

```cpp
#include "TedsAssetData/TedsAssetData.h"                 // 模块主头文件（如有）
#include "TedsAssetData/TedsAssetDataColumns.h"          // 列定义
#include "TedsAssetData/TedsAssetDataWidgetColumns.h"    // 小部件列定义
#include "TedsAssetData/TedsAssetDataHelper.h"           // 辅助函数
```

### 基本用法

**启用资产注册表存储**

```cpp
#include "TedsAssetDataModule.h"

// 在模块启动或需要时启用
UE::Editor::AssetData::FTedsAssetDataModule& Module = UE::Editor::AssetData::FTedsAssetDataModule::GetChecked();
Module.EnableTedsAssetRegistryStorage();  // 开始将 AssetRegistry 数据同步到 TEDS
// Module.EnableAssetDataMetadataStorage(); // 同时启用元数据（标签）存储
```

**查询资产并按名称排序**

```cpp
#include "TedsAssetData/TedsAssetDataColumns.h"
#include "DataStorage/Query.h"
#include "DataStorage/QueryHelpers.h"

using namespace UE::Editor::DataStorage;

// 创建查询：获取所有带有 FAssetNameColumn 的行，并允许按名称排序
auto Query = QueryHelpers::MakeQuery<FAssetNameColumn>(Database);
TArray<RowHandle> Rows;
Query.Evaluate();
Query.GetRows(Rows);

// 使用 FAssetNameWidgetSorter_NoSlash 对行进行排序
FAssetNameWidgetSorter_NoSlash Sorter;
Rows.Sort([&](RowHandle A, RowHandle B) {
    const FAssetNameColumn* ColA = Database.GetColumn<FAssetNameColumn>(A);
    const FAssetNameColumn* ColB = Database.GetColumn<FAssetNameColumn>(B);
    return Sorter.Compare(*ColA, *ColB) < 0;
});
```

**获取资产标签元数据**

```cpp
#include "TedsAssetData/CB/TagsMetadataCache.h"
#include "TedsAssetData/TedsAssetDataStructs.h"

using namespace UE::Editor::AssetData::Private;

FTagsMetadataCache Cache;
FTopLevelAssetPath ClassPath = ...;  // 例如 "/Script/Engine.StaticMesh"
Cache.CacheClass(ClassPath);

const FTagsMetadataCache::FClassPropertiesCache* ClassCache = Cache.FindCacheForClass(ClassPath);
if (ClassCache)
{
    TSharedPtr<FItemAttributeMetadata> Meta = ClassCache->GetCacheForTag("Triangles");
    if (Meta)
    {
        // Meta->DisplayName, Meta->Suffix 等
    }
}
```

### 进阶用法

**自定义资产预览面板**

```cpp
// 创建资产预览 widget
#include "Widgets/AssetPreview/STedsAssetPreviewWidget.h"

TSharedRef<STedsAssetPreviewWidget> AssetPreview = SNew(STedsAssetPreviewWidget)
    .WidgetPurpose(UE::Editor::DataStorage::IUiProvider::FPurposeInfo("AssetPreview", "Default", NAME_None).GeneratePurposeID())
    .TargetRow(TargetRowHandle);  // 从 TEDS 查询获得的行句柄

// 将预览嵌入父布局
SomeParentWidget->AddSlot()[AssetPreview];
```

**批量处理资产元数据**

参考 `FTedsAssetDataCBDataSource::PrepopulateTagsMetadataCache()` 中的逻辑，可以手动调用 `Cache.BatchCacheClasses(ArrayOfClassPaths)` 来预热常见 UClass 的标签缓存，提高运行时性能。

## Demo 示例

以下是一个最小示例，展示如何在编辑器模块中使用 TedsAssetData 的功能。

**MyCustomAssetPanel.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "DataStorage/Handles.h"

class IEditorDataStorageProvider;

class SMyCustomAssetPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCustomAssetPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<SWidget> BuildAssetList();
    
    IEditorDataStorageProvider* DataStorage = nullptr;
    TArray<UE::Editor::DataStorage::RowHandle> AssetRows;
};
```

**MyCustomAssetPanel.cpp**
```cpp
#include "MyCustomAssetPanel.h"
#include "TedsAssetData/TedsAssetDataColumns.h"
#include "DataStorage/Query.h"
#include "DataStorage/QueryHelpers.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Views/SListView.h"

void SMyCustomAssetPanel::Construct(const FArguments& InArgs)
{
    // 获取 TEDS 数据库（通常从模块管理器获取）
    DataStorage = ...; // 通过 IEditorDataStorageModule::Get().GetDatabase() 获取

    // 创建查询，获取所有带 FAssetNameColumn 的行
    auto Query = UE::Editor::DataStorage::QueryHelpers::MakeQuery<FAssetNameColumn>(*DataStorage);
    Query.Evaluate();
    Query.GetRows(AssetRows);

    ChildSlot
    [
        BuildAssetList()
    ];
}

TSharedPtr<SWidget> SMyCustomAssetPanel::BuildAssetList()
{
    return SNew(SListView<UE::Editor::DataStorage::RowHandle>)
        .ListItemsSource(&AssetRows)
        .OnGenerateRow_Lambda([this](UE::Editor::DataStorage::RowHandle Row, const TSharedRef<STableViewBase>& Owner)
        {
            const FAssetNameColumn* NameCol = DataStorage->GetColumn<FAssetNameColumn>(Row);
            FText DisplayText = NameCol ? FText::FromName(NameCol->Name) : FText::GetEmpty();
            return SNew(STableRow<UE::Editor::DataStorage::RowHandle>, Owner)
                .Content()
                [
                    SNew(STextBlock).Text(DisplayText)
                ];
        });
}
```

**模块依赖**

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS 核心框架数据库 |
| `AssetRegistry` | 资产注册表数据源 |
| `ContentBrowserData` | 内容浏览器路径和虚拟路径支持（用于 `FVirtualPathProcessor`） |

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` — Fix TedsType info assert when running certain Verse automated tests
- 2025-10-02 `1f8278e6` — Re-enable Teds AssetData after resolving test and FName issues
- 2025-09-26 `7d070444` — [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions on the TEDS S
- 2025-09-25 `8d9818a1` — [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)
- 2025-09-25 `4161c053` — Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module

### 维护评价

该插件创建于 2025 年 9 月，属于全新开发的实验性系统。近期每周均有功能性更新，包括修复稳定性问题、添加新查看器、排序持久化等。团队正在积极开发中，但 `IsExperimentalVersion=true` 表明 API 和架构可能仍有较大变动。建议在非生产性项目中使用，并关注后续更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档](https://dev.epicgames.com/documentation/unreal-engine/typed-element-data-storage)（TEDS 通用文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsAssetData/Tests)（可能不完整，如无则忽略）