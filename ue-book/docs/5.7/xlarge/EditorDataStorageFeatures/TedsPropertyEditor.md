# TedsPropertyEditor

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDs 属性编辑器 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器小部件、蓝图资产） |
| 模块 | `TedsPropertyEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsPropertyEditor) | |

## 用途

`TedsPropertyEditor` 模块扩展了 Unreal Engine 的属性编辑器（Property Editor），使其能够通过 **TEDS（Editor Data Storage）** 框架选择数据行（`RowHandle`）作为属性值。它提供了类似 **Actor 拾取（Actor Picking）** 模式的交互方式，但操作的是 TEDS 数据存储中的行。

该模块解决的核心问题：**在属性面板中，当属性类型为 TEDS RowHandle 时，如何让用户直观地从成千上万的行中选取一个？** 通过 `SPropertyMenuTedsRowPicker` 小部件，开发者可以快速集成一个支持查询、过滤、交互的拾取菜单，而无需重复实现底层的大纲视图和选择逻辑。

## 使用场景

- 你正在开发一个基于 TEDS 的编辑器工具（例如自定义资产管理器、数据表格编辑器），属性面板中需要显示一个 `RowHandle` 类型的属性，并允许用户从数据存储中选取特定行。
- 你需要为 TEDS 数据行提供类似场景大纲视图（Scene Outliner）的交互式选择体验，但只对特定查询结果开放（例如只显示满足某种标签的行）。
- 你希望复用现有的 TEDS 场景大纲视图（`TedsOutliner`）的视觉风格和导航行为，作为属性编辑器中的拾取对话框。

## 蓝图用法

本模块未直接暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 的 API。所有功能均为 C++ 级别的编辑器扩展。蓝图用户可以通过以下间接方式使用：

- 如果某个 TEDS 行引用的属性在蓝图类中使用，并在细节面板中编辑，则该模块会在编辑器内自动启用拾取功能（前提是插件已启用）。
- 自定义蓝图函数库（例如 `UTedsBlueprintLibrary`）若有调用 `RowHandle` 相关的属性编辑器交互，也会受益于此模块的拾取 UI。

## C++ 用法

### 头文件引入

根据使用场景，需要包含以下头文件之一或全部：

```cpp
#include "TedsRowPickingMode.h"
#include "SPropertyMenuTedsRowPicker.h"
```

### 基本用法

**创建 TEDS 行拾取器菜单**

在属性编辑器的 `CustomizeDetails` 或 `CreateWidget` 中，使用 `SPropertyMenuTedsRowPicker` 构建一个拾取按钮，用户点击后弹出基于 TEDS 大纲视图的选择器。

```cpp
// 来源：Source/TedsPropertyEditor/Public/Widgets/SPropertyMenuTedsRowPicker.h

// 假设当前有一属性 RowHandleProperty，类型为 UE::Editor::DataStorage::RowHandle
SAssignNew(TedsPicker, SPropertyMenuTedsRowPicker)
    .AllowClear(true)
    .QueryFilter(MyQueryDescription)               // 定义拾取器应该显示哪些行
    .ElementFilter(FOnShouldFilterTedsRow::CreateLambda([](RowHandle Row) {
        // 返回 true 表示该行可被选择，false 则过滤掉
        return IsRowValid(Row);
    }))
    .InteractiveFilter(FOnShouldInteractTedsRow::CreateLambda([](RowHandle Row) {
        // 返回 true 表示该行可交互（例如可以双击确认）
        return true;
    }))
    .OnSet(FOnTedsRowSelected::CreateLambda([this](RowHandle SelectedRow) {
        // 用户选择了某行
        SetPropertyValue(SelectedRow);
    }))
    .OnClose(FSimpleDelegate::CreateLambda([this]() {
        // 拾取器关闭时的回调
    }));
```

**自定义拾取模式**

如果你需要完全控制拾取行为（例如在非属性面板的场合），可以直接继承 `FTedsRowPickingMode` 并覆盖 `OnItemSelectionChanged` 和 `OnFilterTextCommited`。

```cpp
// 来源：Source/TedsPropertyEditor/Public/TedsRowPickingMode.h

class FMyCustomPickingMode : public FTedsRowPickingMode
{
public:
    using FTedsRowPickingMode::FTedsRowPickingMode;

    virtual void OnItemSelectionChanged(FSceneOutlinerTreeItemPtr Item, ESelectInfo::Type SelectionType, 
                                         const FSceneOutlinerItemSelection& Selection) override
    {
        // 自定义选择行为
        if (Selection.IsValid())
        {
            OnItemPicked.ExecuteIfBound(Item);
        }
    }
};
```

### 进阶用法

**过滤器与查询组合使用**

通过 `FQueryDescription` 定义拾取器的行源，结合 `ElementFilter` 和 `InteractiveFilter` 实现多层过滤，同时保留底层 TEDS 查询的高性能筛选能力。

```cpp
// 创建查询：只显示类型为“UObject”关联的行
UE::Editor::DataStorage::FQueryDescription QueryDesc;
QueryDesc.AddCondition<FObjectTag>(UE::Editor::DataStorage::FQueryCondition::Exist);

// 额外过滤：排除正在被删除的行
auto Filter = FOnShouldFilterTedsRow::CreateLambda([](RowHandle Row) {
    return !IsRowMarkedForDeletion(Row);
});

auto Picker = SNew(SPropertyMenuTedsRowPicker)
    .QueryFilter(QueryDesc)
    .ElementFilter(Filter)
    .OnSet(...);
```

**与属性编辑器集成**

结合 `IPropertyTypeCustomization` 或 `IPropertyHandle`，将拾取器嵌入到细节面板的编辑器中。

```cpp
TSharedRef<SWidget> CreateRowHandleWidget(TSharedPtr<IPropertyHandle> PropertyHandle)
{
    UE::Editor::DataStorage::RowHandle CurrentValue;
    PropertyHandle->GetValue(CurrentValue);

    return SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            SNew(SPropertyMenuTedsRowPicker)
                .AllowClear(true)
                .QueryFilter(...)
                .OnSet([PropertyHandle](RowHandle NewValue) {
                    PropertyHandle->SetValue(NewValue);
                })
        ]
        + SHorizontalBox::Slot()
        .Padding(4, 0)
        [
            SNew(STextBlock)
                .Text(FText::FromString(FString::Printf(TEXT("Row: %llu"), CurrentValue)))
        ];
}
```

## Demo 示例

以下是一个完整的、最小可编译的编辑器模块示例，演示如何在属性面板中为指定的属性类型显示 TEDS 行拾取器。

### MyCustomization.h

```cpp
#pragma once

#include "IPropertyTypeCustomization.h"
#include "Widgets/SPropertyMenuTedsRowPicker.h"
#include "DataStorage/Handles.h"

class FMyRowHandleCustomization : public IPropertyTypeCustomization
{
public:
    static TSharedRef<IPropertyTypeCustomization> MakeInstance()
    {
        return MakeShareable(new FMyRowHandleCustomization());
    }

    virtual void CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, 
                                  FDetailWidgetRow& HeaderRow, 
                                  IPropertyTypeCustomizationUtils& CustomizationUtils) override;

    virtual void CustomizeChildren(TSharedRef<IPropertyHandle> PropertyHandle, 
                                    IDetailChildrenBuilder& ChildBuilder, 
                                    IPropertyTypeCustomizationUtils& CustomizationUtils) override {}
};
```

### MyCustomization.cpp

```cpp
#include "MyCustomization.h"
#include "PropertyHandle.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Layout/SBox.h"

void FMyRowHandleCustomization::CustomizeHeader(TSharedRef<IPropertyHandle> PropertyHandle, 
                                                 FDetailWidgetRow& HeaderRow, 
                                                 IPropertyTypeCustomizationUtils& CustomizationUtils)
{
    // 获取当前值
    UE::Editor::DataStorage::RowHandle CurrentValue = UE::Editor::DataStorage::InvalidRowHandle;
    PropertyHandle->GetValue(CurrentValue);

    // 构建拾取器
    TSharedRef<SPropertyMenuTedsRowPicker> Picker = 
        SNew(SPropertyMenuTedsRowPicker)
        .AllowClear(true)
        .QueryFilter(UE::Editor::DataStorage::FQueryDescription()) // 实际使用时需要填充有意义的条件
        .OnSet([PropertyHandle](UE::Editor::DataStorage::RowHandle NewValue)
        {
            PropertyHandle->SetValue(NewValue);
        })
        .OnClose(FSimpleDelegate());

    // 组装行
    HeaderRow
    .NameContent()
    [
        PropertyHandle->CreatePropertyNameWidget()
    ]
    .ValueContent()
    [
        SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            Picker
        ]
        + SHorizontalBox::Slot()
        .Padding(4, 0)
        [
            SNew(STextBlock)
            .Text(FText::FromString(FString::Printf(TEXT("%llu"), CurrentValue)))
            .Font(IDetailLayoutBuilder::GetDetailFont())
        ]
    ];
}
```

### 注册自定义类型

在你的模块的 `StartupModule` 中注册该自定义化：

```cpp
#include "PropertyEditorModule.h"
#include "MyCustomization.h"

void FMyModule::StartupModule()
{
    FPropertyEditorModule& PropertyModule = FModuleManager::LoadModuleChecked<FPropertyEditorModule>("PropertyEditor");
    PropertyModule.RegisterCustomPropertyTypeLayout("MyRowHandle", FOnGetPropertyTypeCustomizationInstance::CreateStatic(&FMyRowHandleCustomization::MakeInstance));
}
```

## 模块依赖

`TedsPropertyEditor` 运行时依赖以下独特模块（省略常见 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `TedsOutliner` | 提供 `FTedsOutlinerMode` 基类，用于 TEDS 场景大纲视图的拾取模式 |
| `TedsCore`（或 `EditorDataStorage`） | 提供 `RowHandle` 类型、查询描述、数据存储核心功能 |
| `SceneOutliner` | 提供 `FSceneOutlinerItemSelection`、`FSceneOutlinerTreeItemPtr` 等场景大纲视图基础设施 |
| `PropertyEditor` | 提供属性编辑器自定义框架，用于集成 `SPropertyMenuTedsRowPicker` |

注：`SceneOutliner` 和 `PropertyEditor` 虽然常见于编辑器插件，但此处是功能上的强依赖，故列出。

## 维护状态

### 近期更新

- 2025-10-14 `267e8191` Fix TedsType info assert when running certain Verse automated tests（修复断言）
- 2025-10-02 `1f8278e6` Re-enable Teds AssetData after resolving test and FName issues（修复后重新启用）
- 2025-09-26 `7d070444` [TEDS Viewers] Allow Sorting to be persisted via IsEnabled and GetColumnSort functions（排序持久化）
- 2025-09-25 `8d9818a1` [TEDS Viewers] Create a new composite hierarchy viewer (include searching and filtering by default)（新增复合层级查看器）
- 2025-09-25 `4161c053` Add a new TEDSFilterBar Widget and add TedsFilters to the TableViewer module（新增过滤条）

### 维护评价

- **创建时间**：2025-09-25，非常新的实验性模块。
- **最近更新频率**：2025-09-25 至 2025-10-14，不到一个月内有多项功能更新和修复，开发活跃。
- **活跃程度**：非常活跃，每几天就有提交，且涉及功能增强和 bug 修复。
- **已知问题**：项目中曾出现测试和 FName 相关问题（已修复），TedsType info 有断言（已修复）。
- **推荐使用**：**强烈推荐**用于需要 TEDS 属性拾取的编辑器项目，但请注意它仍处于实验阶段，未来 API 可能发生较大变化。建议配合最新源码使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures/Source/TedsPropertyEditor)
- [官方文档]（暂无，因插件处于早期实验阶段）
- [测试用例]（未提供公开测试，但可通过源码仓库搜索 `TedsPropertyEditor` 相关测试文件）