# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储特性 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI 组件、资产数据集成、调试工具） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 是基于 **TEDS（Typed Element Data Storage）** 框架构建的编辑器 UI 功能集合。它解决的核心问题是：**如何利用 ECS 风格的数据存储系统高效地驱动编辑器 UI，替代传统的 UObject/Widget 一对一绑定模式**。

具体来说，这个插件将编辑器中的各种数据（资产信息、Actor 属性、Content Browser 内容、Outliner 层级等）映射为 TEDS 数据库中的"列"（Column）和"行"（Row），然后通过声明式的 Widget 构造器（Widget Constructor）从这些数据行生成 UI 组件。这种方式使得编辑器 UI 的构建更加数据驱动、可组合，且能利用 TEDS 的查询和过滤能力实现高性能的数据展示。

插件内含 17 个子模块，覆盖了编辑器的各个功能领域：

| 模块 | 功能领域 |
|---|---|
| **TedsAssetData** | 资产注册表数据同步、资产预览 UI |
| **TedsContentBrowser** | Content Browser TEDS 集成 |
| **TedsOutliner** | World Outliner TEDS 集成 |
| **TedsPropertyEditor** | 属性编辑器 TEDS 集成 |
| **TedsDebugger** | TEDS 数据调试工具 |
| **TedsTableViewer** | TEDS 表格查看器 |
| **TedsEverythingPicker** | 全局搜索选择器 |
| **TedsAlerts** | TEDS 警告系统 |
| **TedsRevisionControl** | 版本控制集成 |
| **TedsSettings** | TEDS 设置管理 |
| **TedsOperations** | TEDS 操作处理器 |
| **TedsActorCompatibility** | Actor 兼容层 |
| **TedsEditorCompatibility** | 编辑器兼容层 |
| **TedsTypedElementBridge** | Typed Element 桥接 |
| **TedsTypeInfo** | 类型信息管理 |
| **TedsQueryStack** | 查询栈管理 |
| **UnifiedFavorites** | 统一收藏系统 |

## 使用场景

- 你需要在编辑器中以数据驱动方式展示资产列表（名称、缩略图、磁盘大小等） → 用 TedsAssetData 的列和 Widget 构造器
- 你需要自定义 Content Browser 的资产预览面板 → 用 STedsAssetPreviewWidget
- 你需要将资产注册表（Asset Registry）的同步数据高效存储到 TEDS 数据库中 → 用 FTedsAssetDataModule
- 你正在开发基于 TEDS 框架的编辑器工具 → 这个插件提供了大量现成的 Column 定义和 Widget 工厂

## 蓝图用法

本模块主要面向 C++ 编辑器开发，**不暴露 BlueprintCallable 接口**。所有功能通过 C++ API 访问。

## C++ 用法

### 模块接口 — FTedsAssetDataModule

`FTedsAssetDataModule` 是 TedsAssetData 模块的主入口，控制资产注册表数据到 TEDS 的同步。

#### 头文件引入

```cpp
#include "TedsAssetDataModule.h"  // Private/TedsAssetDataModule.h
```

#### 启用/禁用资产注册表存储

```cpp
using namespace UE::Editor::AssetData;

// 获取模块实例
FTedsAssetDataModule& Module = FTedsAssetDataModule::Get();

// 启用资产注册表数据到 TEDS 的同步
Module.EnableTedsAssetRegistryStorage();

// 检查是否已启用
if (Module.IsTedsAssetRegistryStorageEnabled())
{
    UE_LOG(LogTemp, Log, TEXT("TEDS Asset Registry Storage is active"));
}

// 监听存储初始化完成
FSimpleMulticastDelegate& OnReady = Module.OnAssetRegistryStorageInit();
OnReady.AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("TEDS Asset Registry Storage initialized"));
});
```

#### 资产数据元数据存储

```cpp
// 启用资产元数据列（如 DisplayName, Tooltip 等）的存储
Module.EnableAssetDataMetadataStorage();

// 禁用
Module.DisableAssetDataMetadataStorage();
```

#### 自动化脚本中处理依赖事件

```cpp
// 在自动化测试中，手动触发所有待处理事件
// 注意：正常使用编辑器时不需要调用此方法，它仅用于自动化脚本避免不必要的阻塞
Module.ProcessDependentEvents();
```

### 资产数据列（Columns）

资产数据以 TEDS 列的形式存储。以下是 `TedsAssetDataColumns.h` 中定义的核心列：

#### 头文件引入

```cpp
#include "TedsAssetDataColumns.h"
```

#### 列类型一览

| 列结构体 | 用途 | 关键属性 |
|---|---|---|
| `FAssetPathColumn_Experimental` | 资产路径 | `FName Path` |
| `FAssetDataColumn_Experimental` | 完整 FAssetData | `FAssetData AssetData` |
| `FAssetNameColumn` | 资产名称 | `FName Name` |
| `FAssetClassColumn` | 资产类型 | `FTopLevelAssetPath ClassPath` |
| `FDiskSizeColumn` | 磁盘大小 | `int64 DiskSize` |
| `FVersePathColumn` | Verse 路径 | `FVersePath VersePath` |
| `FVirtualPathColumn_Experimental` | 内容浏览器虚拟路径 | `FName VirtualPath` |
| `FItemTextAttributeColumn_Experimental` | 文本属性值 | `FText Value` |
| `FItemStringAttributeColumn_Experimental` | 字符串属性值（动态列） | `FString Value` |

#### 标签（Tags）用于资产分类

```cpp
#include "TedsAssetDataColumns.h"

// 标签用于标识资产类型
FAssetTag              // 通用资产标签
FPrivateAssetTag       // 私有资产
FEpicInternalAssetTag  // Epic 内部资产
FPublicAssetTag        // 公开资产
FUpdatedPathTag        // 路径更新通知标签
FUpdatedAssetDataTag   // 资产数据更新通知标签
```

### Widget 构造器系统

TedsAssetData 通过 **Widget Factory + Widget Constructor** 模式注册 UI 组件。每个 Factory 继承自 `UEditorDataStorageFactory`，在注册时声明 Widget 的用途（Purpose）和构造逻辑。

#### 资产预览 Widget

```cpp
#include "Widgets/AssetPreview/STedsAssetPreviewWidget.h"

// 创建资产预览面板
TSharedRef<STedsAssetPreviewWidget> AssetPreview = SNew(STedsAssetPreviewWidget)
    .WidgetPurpose(UE::Editor::DataStorage::IUiProvider::FPurposeInfo(
        "AssetPreview", "Default", NAME_None).GeneratePurposeID())
    .TargetRow(RowHandle);

// 动态切换预览目标
AssetPreview->SetTargetRow(NewRowHandle);
AssetPreview->ReconstructTedsWidget();

// 获取 Widget 在 TEDS 中的行句柄
UE::Editor::DataStorage::RowHandle WidgetRow = AssetPreview->GetWidgetRowHandle();
```

#### 资产名称超链接 Widget

```cpp
#include "Widgets/SHyperlinkAssetPreviewWidget.h"

// 创建带预览的资产超链接
TSharedRef<SHyperlinkAssetPreviewWidget> Hyperlink = SNew(SHyperlinkAssetPreviewWidget)
    .AssetData(AssetDataAttribute)
    .OnNavigateAsset_Lambda([](const FAssetData& Data)
    {
        // 导航到资产
        FAssetEditorManager::Get().OpenEditorForAsset(Data.GetAsset());
    });

// 获取缩略图预览（用作 tooltip）
TSharedRef<SWidget> Thumbnail = Hyperlink->GetThumbnailWidget();
```

### Widget 辅助列

`TedsAssetDataWidgetColumns.h` 定义了控制 Widget 行为的列：

```cpp
#include "TedsAssetDataWidgetColumns.h"

// 缩略图尺寸控制
FThumbnailSizeColumn_Experimental

// Widget 尺寸值
FSizeValueColumn_Experimental

// Widget 内边距
FWidgetPaddingColumn_Experimental

// 缩略图编辑模式
FThumbnailEditModeColumn_Experimental

// 文本溢出策略
FTextOverflowPolicyColumn_Experimental

// Widget 可见性
FWidgetVisibilityColumn_Experimental

// 字体样式
FFontStyleColumn_Experimental

// Widget 工具提示
FLocalWidgetTooltipColumn_Experimental

// 外部回调：获取 Slate Brush
FOnGetWidgetSlateBrushColumn_Experimental

// 外部回调：获取颜色和透明度
FOnGetWidgetColorAndOpacityColumn_Experimental
```

### 辅助函数

```cpp
#include "TedsAssetDataHelper.h"

// 获取缩略图相关元数据名称
FName StatusName = TedsAssetDataHelper::MetaDataNames::GetThumbnailStatusMetaDataName();
FName FadeInName = TedsAssetDataHelper::MetaDataNames::GetThumbnailFadeInMetaDataName();
FName HintTextName = TedsAssetDataHelper::MetaDataNames::GetThumbnailHintTextMetaDataName();

// 获取 Widget 表名
FName TableName = TedsAssetDataHelper::TableView::GetWidgetTableName();

// 路径工具函数
FString CleanPath = TedsAssetDataHelper::RemoveSlashFromStart(TEXT("/Game/Meshes/"));
FString ParentPath = TedsAssetDataHelper::RemoveAllFromLastSlash(TEXT("/Game/Meshes/Cube"));
```

## Demo 示例

以下示例展示如何注册一个自定义 TEDS Widget 工厂，在 TEDS 数据库中查询资产并展示其信息：

### CustomAssetWidgetFactory.h

```cpp
#pragma once

#include "Elements/Framework/TypedElementDataStorageFactory.h"
#include "Elements/Framework/TypedElementDataStorageWidgetConstructor.h"
#include "TedsAssetDataColumns.h"

UCLASS()
class UCustomAssetWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    virtual ~UCustomAssetWidgetFactory() override = default;

    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override;
};

USTRUCT()
struct FCustomAssetWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    FCustomAssetWidgetConstructor();
    virtual ~FCustomAssetWidgetConstructor() override = default;

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override;

private:
    TArray<TWeakObjectPtr<const UScriptStruct>> GetColumns();
};
```

### CustomAssetWidgetFactory.cpp

```cpp
#include "CustomAssetWidgetFactory.h"
#include "TedsAssetDataColumns.h"
#include "Elements/Interfaces/TypedElementDataStorageUiInterface.h"

void UCustomAssetWidgetFactory::RegisterWidgetConstructors(
    UE::Editor::DataStorage::ICoreProvider& DataStorage,
    UE::Editor::DataStorage::IUiProvider& DataStorageUi) const
{
    using namespace UE::Editor::DataStorage;

    // 注册自定义 Widget 用途
    DataStorageUi.RegisterWidgetPurpose(
        IUiProvider::FPurposeInfo("CustomAssetView", "Default", NAME_None),
        IUiProvider::EPurposeType::Generic,
        FText::FromString(TEXT("Custom Asset View Widget")));

    // 注册构造器
    DataStorageUi.RegisterWidgetConstructor(
        IUiProvider::FPurposeInfo("CustomAssetView", "Default", NAME_None).GeneratePurposeID(),
        MakeUnique<FCustomAssetWidgetConstructor>());
}

FCustomAssetWidgetConstructor::FCustomAssetWidgetConstructor()
    : FSimpleWidgetConstructor(GetColumns())
{
}

TArray<TWeakObjectPtr<const UScriptStruct>> FCustomAssetWidgetConstructor::GetColumns()
{
    return {
        FAssetNameColumn::StaticStruct(),
        FAssetClassColumn::StaticStruct(),
        FDiskSizeColumn::StaticStruct()
    };
}

TSharedPtr<SWidget> FCustomAssetWidgetConstructor::CreateWidget(
    UE::Editor::DataStorage::ICoreProvider* DataStorage,
    UE::Editor::DataStorage::IUiProvider* DataStorageUi,
    UE::Editor::DataStorage::RowHandle TargetRow,
    UE::Editor::DataStorage::RowHandle WidgetRow,
    const UE::Editor::DataStorage::FMetaDataView& Arguments)
{
    if (!DataStorage || TargetRow == UE::Editor::DataStorage::InvalidRowHandle)
    {
        return SNullWidget::NullWidget;
    }

    // 从 TEDS 数据库读取资产名称
    const FAssetNameColumn* NameColumn = DataStorage->GetColumn<FAssetNameColumn>(TargetRow);
    const FAssetClassColumn* ClassColumn = DataStorage->GetColumn<FAssetClassColumn>(TargetRow);
    const FDiskSizeColumn* SizeColumn = DataStorage->GetColumn<FDiskSizeColumn>(TargetRow);

    FText AssetName = NameColumn ? FText::FromName(NameColumn->Name) : FText::GetEmpty();
    FText AssetClass = ClassColumn ? FText::FromName(ClassColumn->ClassPath.GetAssetName()) : FText::GetEmpty();
    FText DiskSize = SizeColumn
        ? FText::Format(NSLOCTEXT("CustomAssetWidget", "SizeFmt", "{0} bytes"),
            FText::AsNumber(SizeColumn->DiskSize))
        : FText::GetEmpty();

    return SNew(SHorizontalBox)
        + SHorizontalBox::Slot().AutoWidth().Padding(4.0f)
        [
            SNew(STextBlock).Text(AssetName)
        ]
        + SHorizontalBox::Slot().AutoWidth().Padding(4.0f)
        [
            SNew(STextBlock).Text(AssetClass).ColorAndOpacity(FSlateColor(FLinearColor::Gray))
        ]
        + SHorizontalBox::Slot().AutoWidth().Padding(4.0f)
        [
            SNew(STextBlock).Text(DiskSize)
        ];
}
```

## 模块依赖

从各模块的 Build.cs 分析，TedsAssetData 及其兄弟模块需要以下依赖：

| 模块 | 用途 |
|---|---|
| `TypedElementDataStorage` | TEDS 核心数据存储框架 |
| `TypedElementFramework` | Typed Element 基础框架 |
| `TypedElementRuntime` | Typed Element 运行时 |
| `AssetRegistry` | 资产注册表数据源 |
| `ContentBrowserData` | Content Browser 数据层 |
| `ContentBrowser` | Content Browser UI 集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限 UEFN 模式下启用 TEDS Outliner |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 在 TEDS Outliner 中隐藏非编辑关卡实例内未加载的 Actor 行 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS Outliner 中无效的跨关卡拖放操作 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回退之前的提交 CL53940377 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 隐藏 TEDS Outliner 中非编辑关卡实例的未加载 Actor |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2024-07-27，约 2 年前
- **实验性状态**：标记为 `IsExperimentalVersion=true`，尚未正式发布
- **最近更新**：2026-05 月有密集的功能性更新，主要集中在 TedsOutliner 子模块的 UEFN 支持和 bug 修复
- **开发团队**：由 Epic Games 官方维护，是 TEDS 架构战略的重要组成部分
- **已知限制**：作为实验性插件，API 带有 `_Experimental` 后缀，可能在后续版本中变更
- **推荐程度**：适合提前了解 TEDS 架构方向的开发者研究学习，不建议在生产项目中直接使用。待其从 Experimental 毕业后可正式采用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- 官方文档（无）