# Custom Details View

> 

| 属性 | 值 |
|---|---|
| 中文名 | 自定义详情面板 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomDetailsView` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CustomDetailsView) | |

## 用途

CustomDetailsView 是一个高度可定制的属性详情面板框架，专为 Virtual Production（特别是 Motion Design 工具链）设计。它替代了 UE 标准的 `IDetailsView`，允许开发者构建具有以下能力的自定义属性面板：

- **树形结构展示**：以可展开/折叠的树形层级展示属性，支持自定义分类和自定义节点
- **精细过滤控制**：通过 AllowList/DisallowList 机制精确控制哪些属性分类、属性项、以及组件类型（名称/值/整行/扩展按钮）可见
- **完全自定义 Widget**：支持替换名称列、值列、整行或扩展按钮区域的 Widget
- **动态扩展系统**：可以在任意属性项的前后或子级位置插入自定义节点
- **列宽同步**：多个自定义详情面板可以共享同一份列宽数据，实现列宽同步
- **Sequencer 集成**：内置关键帧按钮支持，与 Sequencer 时间轴联动
- **撤销/重置支持**：自动处理属性重置到默认值的功能

该插件是 Motion Design 编辑器工具链的核心组件，从 Experimental 迁移至 VirtualProduction，为 Motion Design 插件提供更灵活的属性编辑体验。

## 使用场景

- 你在做 Virtual Production / Motion Design 相关的编辑器工具 → 用 CustomDetailsView 构建自定义属性面板
- 你需要一个可以控制显示哪些属性分类、哪些属性项的详情面板 → 用 AllowList 机制过滤
- 你需要在属性列表中插入自定义的 UI 节点（如按钮、分隔线、自定义控件） → 用 ExtendTree / CreateCustomItem
- 你需要多个面板同步列宽 → 共享 `ColumnSizeData`
- 你需要给属性面板的关键帧按钮、重置按钮做深度定制 → 用 Item 级别的 Override 机制
- 你需要根据上下文动态生成子属性项 → 用 `SetCreateChildItemDelegate`

## 蓝图用法

此插件为纯 C++ 框架，无 BlueprintCallable 节点。所有 API 均通过 C++ 接口访问。

## C++ 用法

### 头文件引入

```cpp
#include "CustomDetailsViewModule.h"
#include "CustomDetailsViewArgs.h"
#include "ICustomDetailsView.h"
#include "Items/ICustomDetailsViewItem.h"
#include "Items/ICustomDetailsViewCustomItem.h"
#include "Items/ICustomDetailsViewCustomCategoryItem.h"
#include "Items/CustomDetailsViewItemId.h"
```

### 基本用法：创建一个自定义详情面板

通过 `ICustomDetailsViewModule` 工厂方法创建实例，并绑定对象。

```cpp
// 来源: Source/CustomDetailsView/Public/CustomDetailsViewModule.h
// 来源: Source/CustomDetailsView/Public/ICustomDetailsView.h

// 1. 配置参数
FCustomDetailsViewArgs Args;
Args.bShowCategories = true;
Args.ValueColumnWidth = 0.6f;
Args.bAllowResetToDefault = true;

// 2. 创建自定义详情面板
ICustomDetailsViewModule& Module = ICustomDetailsViewModule::Get();
TSharedRef<ICustomDetailsView> DetailsView = Module.CreateCustomDetailsView(Args);

// 3. 绑定要编辑的对象
DetailsView->SetObject(MyActor);

// 4. 添加到你的 Slate 布局中
SNew(SVerticalBox)
    + SVerticalBox::Slot()
    .AutoHeight()
    [
        DetailsView
    ];
```

### 过滤属性项

使用 AllowList/DisallowList 机制控制可见性。

```cpp
// 来源: Source/CustomDetailsView/Public/CustomDetailsViewArgs.h

FCustomDetailsViewArgs Args;

// 只显示特定分类（设了 AllowedList 后，只有列表中的分类可见）
Args.CategoryAllowList.Allow(FName("Transform"));
Args.CategoryAllowList.Allow(FName("Rendering"));

// 显式禁止某个分类（即使在 AllowedList 中也会被禁止）
// Args.CategoryAllowList.Disallow(FName("Rendering"));

// 只显示特定类型的 Widget 组件（名称、值、整行、扩展按钮）
Args.WidgetTypeAllowList.Allow(ECustomDetailsViewWidgetType::Name);
Args.WidgetTypeAllowList.Allow(ECustomDetailsViewWidgetType::Value);

// 排除结构体子属性（避免过滤时误匹配结构体内部字段）
Args.bExcludeStructChildPropertiesFromFilters = true;
```

### 进阶用法：扩展树形结构并添加自定义节点

```cpp
// 来源: Source/CustomDetailsView/Public/ICustomDetailsView.h
// 来源: Source/CustomDetailsView/Public/Items/CustomDetailsViewItemId.h

// 在某个属性项前插入自定义节点
FCustomDetailsViewItemId HookId = FCustomDetailsViewItemId::MakePropertyId<MyActorClass>(GET_MEMBER_NAME_CHECKED(MyActorClass, MyProperty));
TSharedPtr<ICustomDetailsViewCustomItem> CustomItem = DetailsView->CreateCustomItem(
    DetailsView->GetRootItem(),
    FName("MyCustomNode"),
    LOCTEXT("CustomLabel", "自定义节点"),
    LOCTEXT("CustomToolTip", "这是一个自定义节点")
);

if (CustomItem.IsValid())
{
    CustomItem->SetLabel(LOCTEXT("Label", "自定义标签"));
    CustomItem->SetToolTip(LOCTEXT("Tooltip", "自定义提示"));

    // 设置值列的自定义 Widget
    CustomItem->SetValueWidget(
        SNew(STextBlock).Text(LOCTEXT("CustomValue", "自定义值"))
    );

    // 或者设置整行自定义 Widget（会覆盖名称和值列）
    // CustomItem->SetWholeRowWidget(MyCustomWholeRowWidget);

    // 将自定义节点插入到 HookId 对应的属性项之前
    DetailsView->ExtendTree(HookId, ECustomDetailsTreeInsertPosition::Before, CustomItem->AsItem());
}

// 添加自定义分类
TSharedPtr<ICustomDetailsViewCustomCategoryItem> CategoryItem = DetailsView->CreateCustomCategoryItem(
    DetailsView->GetRootItem(),
    FName("MyCategory"),
    LOCTEXT("CategoryName", "自定义分类")
);

if (CategoryItem.IsValid())
{
    CategoryItem->SetLabel(LOCTEXT("CatLabel", "我的分类"));
    // 插入为子级
    DetailsView->ExtendTree(HookId, ECustomDetailsTreeInsertPosition::Child, CategoryItem->AsItem());
}
```

### 进阶用法：自定义子属性生成和上下文菜单

```cpp
// 来源: Source/CustomDetailsView/Public/Items/ICustomDetailsViewItem.h

// 自定义子属性项生成
DetailsView->FindItem(ItemId)->SetCreateChildItemDelegate(
    FOnCustomDetailsViewGenerateChildItem::CreateLambda(
        [](const TSharedRef<ICustomDetailsView>& InView,
           const TSharedPtr<ICustomDetailsViewItem>& InParent,
           const TSharedRef<IDetailTreeNode>& InChildNode) -> TSharedPtr<ICustomDetailsViewItem>
        {
            // 返回 nullptr 使用默认行为，或返回自定义 Item 完全覆盖
            return nullptr;
        }
    )
);

// 自定义右键菜单上下文
DetailsView->FindItem(ItemId)->SetCustomizeItemMenuContext(
    FOnCustomDetailsViewCustomizeItemMenuContext::CreateLambda(
        [](const TSharedRef<ICustomDetailsView>& InView,
           const TSharedPtr<ICustomDetailsViewItem>& InItem,
           UObject* InMenuContext,
           TArray<TSharedPtr<IPropertyHandle>>& InPropertyHandles)
        {
            // 自定义菜单内容
        }
    )
);
```

## Demo 示例

```cpp
// MyCustomDetailsPanel.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"

class ICustomDetailsView;
struct FCustomDetailsViewArgs;

class SMyCustomDetailsPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyCustomDetailsPanel) {}
        SLATE_ARGUMENT(UObject*, TargetObject)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<ICustomDetailsView> DetailsView;
};
```

```cpp
// MyCustomDetailsPanel.cpp
#include "MyCustomDetailsPanel.h"

#include "CustomDetailsViewModule.h"
#include "CustomDetailsViewArgs.h"
#include "ICustomDetailsView.h"
#include "Items/ICustomDetailsViewItem.h"
#include "Items/ICustomDetailsViewCustomItem.h"
#include "Items/CustomDetailsViewItemId.h"

#define LOCTEXT_NAMESPACE "MyCustomDetailsPanel"

void SMyCustomDetailsPanel::Construct(const FArguments& InArgs)
{
    // 配置
    FCustomDetailsViewArgs Args;
    Args.bShowCategories = true;
    Args.ValueColumnWidth = 0.55f;
    Args.bAllowResetToDefault = true;
    Args.bDefaultItemsExpanded = false;

    // 设置默认展开状态
    Args.ExpansionState.Add(
        FCustomDetailsViewItemId(),
        ECustomDetailsViewExpansion::SelfExpanded
    );

    // 属性变化回调
    Args.OnFinishedChangingProperties.AddLambda([](const FPropertyChangedEvent& Event)
    {
        UE_LOG(LogTemp, Log, TEXT("Property changed: %s"), *Event.GetPropertyName().ToString());
    });

    // 创建面板
    ICustomDetailsViewModule& Module = ICustomDetailsViewModule::Get();
    DetailsView = Module.CreateCustomDetailsView(Args);

    // 添加一个自定义分隔节点
    TSharedPtr<ICustomDetailsViewCustomItem> Separator = DetailsView->CreateCustomItem(
        DetailsView->GetRootItem(),
        FName("Separator"),
        LOCTEXT("SepLabel", "--- 自定义区域 ---")
    );
    if (Separator.IsValid())
    {
        Separator->SetWholeRowWidget(
            SNew(SBorder)
            .BorderImage(FAppStyle::Get().GetBrush("ToolPanel.GroupBorder"))
            .Padding(FMargin(4.f, 2.f))
            [
                SNew(STextBlock)
                .Text(LOCTEXT("SepText", "自定义区域"))
                .Font(FCoreStyle::GetDefaultFontStyle("Bold", 10))
            ]
        );
        DetailsView->ExtendTree(
            FCustomDetailsViewItemId(),
            ECustomDetailsTreeInsertPosition::FirstChild,
            Separator->AsItem()
        );
    }

    // 绑定对象
    if (InArgs._TargetObject)
    {
        DetailsView->SetObject(InArgs._TargetObject);
    }

    // 布局
    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .FillHeight(1.f)
        [
            DetailsView.ToSharedRef()
        ]
    ];
}

#undef LOCTEXT_NAMESPACE
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyEditor` | 属性行生成器（IPropertyRowGenerator）、属性句柄（IPropertyHandle） |
| `ToolMenus` | 右键菜单扩展注册（UToolMenu） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-01-15 | `5902c2e1` | [AvalancheTests] Automate 'Sequence - Verify Direction and Role can be changed' | 自动化序列测试（非插件核心改动） |
| 2026-01-13 | `d54226b7` | [Backout] - CL49758479 | 回退一次变更（非插件核心改动） |
| 2026-01-13 | `59e0accd` | [AvalancheTests] Automate 'Sequence - Verify Direction and Role can be changed' | 自动化序列测试（非插件核心改动） |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 移除 Motion Design 插件的 Beta 标签，宣告正式发布 |
| 2025-07-12 | `2a264ce3` | Used UnrealCodeFixup to fix dll storage on code | 修复 DLL 导出符号问题 |

### 维护评价

CustomDetailsView 是 Motion Design 工具链的一部分，于 2025 年 5 月从 Experimental 迁移到 VirtualProduction，2025 年 9 月正式移除 Beta 标签。最近的提交（2026 年 1 月）主要涉及 AvalancheTests 自动化测试，并非插件核心代码变动，表明该插件已趋于稳定。

作为 Motion Design 生态的核心组件，它由 Epic 内部团队维护，短期内不太可能被废弃。当前插件仍在 VirtualProduction 目录下活跃存在，**推荐用于 Virtual Production / Motion Design 相关的编辑器扩展开发**。

注意：该插件默认未启用（`Installed: false`），需要手动在项目设置中启用或在模块的 `.Build.cs` 中显式依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/CustomDetailsView)
- [官方文档]()（无）
- [测试用例]()（插件目录内未发现独立测试文件）