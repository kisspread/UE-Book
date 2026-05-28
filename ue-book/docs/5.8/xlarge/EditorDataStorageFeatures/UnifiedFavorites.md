# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 编辑器数据存储功能 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOperations` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime), `UnifiedFavorites` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-07-27 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 用途

EditorDataStorageFeatures 插件是 UE5 **实验性**的编辑器 UI 功能集合，它构建在 **TEDS (The Editor Data Storage)** 系统之上。TEDS 是一个高性能、数据驱动的编辑器框架，用于替换传统的编辑器 UI 组件（如详情面板、大纲视图等），以提供更好的性能、灵活性和可扩展性。

**核心价值：**
- **统一数据源**：所有编辑器 UI 组件共享同一个数据存储系统，确保数据一致性。
- **高性能**：基于 ECS (实体组件系统) 架构，特别适合处理大量对象（如大型关卡或资产库）。
- **可扩展**：开发者可以轻松创建新的 UI 组件（Widget），并通过 TEDS 系统集成。
- **实验性新功能**：包含一系列新的、实验性的编辑器 UI 组件，旨在改进编辑器的工作流程和用户体验。

## 使用场景

- **处理大型关卡**：传统大纲视图在关卡包含数千个 Actor 时性能低下，TEDS 大纲视图可以高效处理。
- **自定义编辑器 UI**：需要创建高性能、数据驱动的自定义编辑器窗口或面板。
- **资产管理系统**：需要高性能的资产浏览和管理界面（如 TEDS ContentBrowser）。
- **需要统一数据管理的复杂编辑器工具**：避免数据不一致和复杂的同步逻辑。

## 蓝图用法

该插件主要是 **C++ 运行时库**，为编辑器 UI 提供底层支持，不直接暴露蓝图节点。其功能通过编辑器 UI 组件（如自定义的大纲视图、资产浏览器等）间接使用。用户主要通过编辑器界面与这些组件交互。

## C++ 用法

### 核心概念

该插件的所有 UI 功能都通过 TEDS 系统实现。开发者主要与 `UE::Editor::DataStorage` 命名空间下的接口交互。

### 头文件引入

```cpp
// 引入 TEDS 核心接口
#include "EditorDataStorageCore/EditorDataStorageCore.h"

// 引入 UI 提供者接口（用于创建 UI 组件）
#include "EditorDataStorageUI/EditorDataStorageUI.h"

// 引入特定功能模块，例如大纲视图功能
#include "TedsOutliner/TedsOutliner.h"
```

### 基本用法：注册自定义 UI 组件

以下示例展示如何通过 `UEditorDataStorageFactory` 注册一个自定义的 UI Widget 构造器。这通常是实现新编辑器 UI 功能的起点。

```cpp
// 来源: Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/UnifiedFavorites/Private/Widgets/UnifiedFavoritesTableWidget.h

#include "EditorDataStorageCore/EditorDataStorageCore.h"
#include "EditorDataStorageUI/EditorDataStorageUI.h"

// 1. 定义一个 Widget 构造器结构体
USTRUCT()
struct FMyCustomWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

public:
    // 实现 CreateWidget 方法，为指定的 TEDS 行（Row）创建 Slate Widget
    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow, // 数据行句柄
        UE::Editor::DataStorage::RowHandle WidgetRow, // UI 行句柄
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override
    {
        // 在此处创建并返回你的自定义 Slate Widget
        // 通常，你需要使用 DataStorage 接口查询 TargetRow 上的数据来驱动 Widget
        return SNew(STextBlock).Text(FText::FromString(TEXT("My Custom Widget")));
    }
};

// 2. 定义一个工厂类，用于向 TEDS UI 系统注册你的 Widget 构造器
UCLASS()
class UMyCustomWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()

public:
    // 当 TEDS UI 系统初始化时，会调用此方法
    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override
    {
        // 向系统注册你的构造器
        // 参数指定这个 Widget 应用于哪种类型的 TEDS 行（例如，所有 Actor 行）
        DataStorageUi.RegisterWidgetConstructor<FMyCustomWidgetConstructor>(
            UE::Editor::DataStorage::FTypedElementRowType::StaticStruct());
    }
};
```

### 进阶用法：与 TEDS 数据交互

在 Widget 内部，你可以通过 `ICoreProvider` 接口直接查询和操作 TEDS 数据。

```cpp
// 来源: Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/UnifiedFavorites/Private/Widgets/UnifiedFavoritesWidget.h (概念性示例)

// 在自定义 Slate Widget 的实现中
void SMyCustomWidget::Construct(const FArguments& InArgs, ICoreProvider* InDataStorage)
{
    DataStorage = InDataStorage;
    TargetRow = InArgs._RowHandle; // 从参数获取数据行句柄

    // 构建 Slate UI
    ChildSlot
    [
        SNew(SButton)
        .OnClicked_Lambda([this]() -> FReply
        {
            // 示例：点击按钮时，修改 TEDS 数据行上的数据
            if (DataStorage && DataStorage->IsRowValid(TargetRow))
            {
                // 假设我们有一个 FMyDataComponent 组件
                if (FMyDataComponent* Data = DataStorage->GetColumn<FMyDataComponent>(TargetRow))
                {
                    Data->Value = !Data->Value; // 切换值
                    DataStorage->MarkColumnDirty<FMyDataComponent>(TargetRow); // 标记数据已更改，触发UI更新
                }
            }
            return FReply::Handled();
        })
        [
            SNew(STextBlock).Text(FText::FromString(TEXT("Toggle Data")))
        ]
    ];
}
```

## Demo 示例

以下是一个最小化示例，创建一个简单的编辑器面板，其中包含一个由 TEDS 驱动的文本块，显示每个 Actor 的 Name。

```cpp
// MyTedsWidget.h
#pragma once

#include "CoreMinimal.h"
#include "EditorDataStorageCore/EditorDataStorageCore.h"
#include "Widgets/SCompoundWidget.h"

class SMyTedsActorNameWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyTedsActorNameWidget) {}
        SLATE_ARGUMENT(UE::Editor::DataStorage::RowHandle, RowHandle)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, UE::Editor::DataStorage::ICoreProvider* InDataStorage);

private:
    UE::Editor::DataStorage::ICoreProvider* DataStorage;
    UE::Editor::DataStorage::RowHandle RowHandle;
    TSharedPtr<STextBlock> NameTextBlock;

    void UpdateName();
};

// MyTedsWidget.cpp
#include "MyTedsWidget.h"

void SMyTedsActorNameWidget::Construct(const FArguments& InArgs, UE::Editor::DataStorage::ICoreProvider* InDataStorage)
{
    DataStorage = InDataStorage;
    RowHandle = InArgs._RowHandle;

    ChildSlot
    [
        SAssignNew(NameTextBlock, STextBlock)
        .Text(FText::FromString(TEXT("Loading...")))
    ];

    // 首次更新
    UpdateName();
}

void SMyTedsActorNameWidget::UpdateName()
{
    if (DataStorage && DataStorage->IsRowValid(RowHandle))
    {
        // 假设 TEDS 行有一个 FName 列存储了 Actor 的名称
        if (const FName* ActorName = DataStorage->GetColumn<FName>(RowHandle))
        {
            NameTextBlock->SetText(FText::FromName(*ActorName));
            return;
        }
    }
    NameTextBlock->SetText(FText::FromString(TEXT("Invalid Row")));
}

// MyWidgetFactory.h
#include "MyTedsWidget.h"
#include "EditorDataStorageUI/EditorDataStorageUI.h"

USTRUCT()
struct FMyTedsActorNameWidgetConstructor : public FSimpleWidgetConstructor
{
    GENERATED_BODY()

    virtual TSharedPtr<SWidget> CreateWidget(
        UE::Editor::DataStorage::ICoreProvider* DataStorage,
        UE::Editor::DataStorage::IUiProvider* DataStorageUi,
        UE::Editor::DataStorage::RowHandle TargetRow,
        UE::Editor::DataStorage::RowHandle WidgetRow,
        const UE::Editor::DataStorage::FMetaDataView& Arguments) override
    {
        return SNew(SMyTedsActorNameWidget, DataStorage)
            .RowHandle(TargetRow);
    }
};

UCLASS()
class UMyWidgetFactory : public UEditorDataStorageFactory
{
    GENERATED_BODY()
public:
    virtual void RegisterWidgetConstructors(
        UE::Editor::DataStorage::ICoreProvider& DataStorage,
        UE::Editor::DataStorage::IUiProvider& DataStorageUi) const override
    {
        DataStorageUi.RegisterWidgetConstructor<FMyTedsActorNameWidgetConstructor>(
            UE::Editor::DataStorage::FTypedElementRowType::StaticStruct());
    }
};
```

## 模块依赖

`EditorDataStorageFeatures` 插件本身是一个大型插件，包含多个子模块。其核心依赖是 `EditorDataStorageCore` 和 `EditorDataStorageUI` 模块，它们属于 UE5 引擎核心的一部分。

| 模块 | 用途 |
|---|---|
| `EditorDataStorageCore` | TEDS 系统的核心运行时，提供数据存储、查询和处理功能。 |
| `EditorDataStorageUI` | TEDS 系统的 UI 框架，提供 Widget 注册、布局和事件处理。 |
| `TypedElementFramework` | 类型化元素框架，用于在 TEDS 中表示编辑器中的对象（如 Actor、组件）。 |
| `UnrealEd` | Unreal Editor 核心模块，提供编辑器基础功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `c18be83c` | Enable the TEDS Outliner in Restricted UEFN | 在受限的 UEFN 环境中启用 TEDS 大纲视图。 |
| 2026-05-14 | `bd93e418` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲视图中隐藏非编辑关卡实例内未加载的 Actor 行。 |
| 2026-05-14 | `bdc9e0ac` | [TedsOutliner] Fix invalid cross-level drag and drops | 修复 TEDS 大纲视图中跨级别拖放无效的问题。 |
| 2026-05-14 | `6f329dd1` | [Backout] - CL53940377 | 回滚提交 CL53940377。 |
| 2026-05-14 | `ee0aab56` | Hide unloaded actor rows inside non-editing level instances from TEDS Outliner | 从 TEDS 大纲视图中隐藏非编辑关卡实例内未加载的 Actor 行。（可能为重复提交或修正） |

### 维护评价

**活跃维护**。该插件创建于 2024 年 7 月，约 1 年历史，属于 **实验性** 项目。从近期提交记录（2026年5月）来看，开发团队正在积极进行功能开发、bug 修复和环境适配（如 UEFN）。这是一个前沿的、不断演进的功能系统。

**推荐使用**：仅推荐用于 **实验性项目**、**研究学习** 或 **对编辑器性能有极高要求的内部工具开发**。由于其 API 和功能可能随时发生重大变更，不建议在生产环境的稳定项目中依赖它。开发者应密切关注其变更日志和官方文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- [官方文档]() （暂无）
- [测试用例]() （需在引擎源码中搜索 `EditorDataStorageFeatures` 相关测试）