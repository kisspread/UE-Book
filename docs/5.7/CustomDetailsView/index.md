# Custom Details View

> 

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomDetailsView` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2024-01-28 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CustomDetailsView) | |

## 用途

Custom Details View 是一个 Editor 模块，提供可编程的属性面板（Details View）Slate 控件。它基于 UE 的 `IDetailTreeNode` / `IPropertyRowGenerator` 体系，但允许开发者完全自定义树结构：在运行时插入自定义节点、过滤属性行、控制展开状态、替换 Name/Value 列的 Widget，以及与 Sequencer 关键帧系统集成。

与标准的 `SDetailsView` 不同，Custom Details View 的核心设计目标是**可扩展的树结构**——你可以在任意位置插入自定义 Category 或自定义 Item，也可以通过 Allow/Disallow 列表精细控制哪些属性行可见。这使它成为 Motion Design 等 Virtual Production 工具链中构建自定义属性面板的基础组件。

## 使用场景

- 你需要一个只显示特定属性子集的精简属性面板 → 使用 `CategoryAllowList` / `ItemAllowList` 过滤
- 你需要在属性树中插入自定义控件（如按钮、分隔符、自定义分类）→ 使用 `ExtendTree()` + `CreateCustomItem()` / `CreateCustomCategoryItem()`
- 你需要多个属性面板同步列宽 → 共享同一个 `FDetailColumnSizeData`
- 你需要在自定义属性面板中支持 Sequencer 关键帧按钮 → 设置 `KeyframeHandler` + `bAllowGlobalExtensions = true`
- 你需要控制每个属性行的展开/折叠状态 → 使用 `ExpansionState` Map 或 `SetItemExpansionState()`
- 你需要替换某个属性行的 Name 列或 Value 列 Widget → 使用 `ICustomDetailsViewItem::SetOverrideWidget()`

## C++ 用法

### 头文件引入

```cpp
#include "CustomDetailsViewModule.h"
#include "ICustomDetailsView.h"
#include "CustomDetailsViewArgs.h"
```

### Build.cs 依赖

在你的模块 Build.cs 中添加：

```cpp
PublicDependencyModuleNames.Add("CustomDetailsView");
```

### 基本用法：创建 Custom Details View

通过模块接口创建实例：

```cpp
// 获取模块
ICustomDetailsViewModule& Module = ICustomDetailsViewModule::Get();

// 配置参数
FCustomDetailsViewArgs Args;
Args.bShowCategories = true;
Args.bAllowResetToDefault = true;
Args.ValueColumnWidth = 0.6f;

// 创建 View
TSharedRef<ICustomDetailsView> DetailsView = Module.CreateCustomDetailsView(Args);

// 绑定对象
DetailsView->SetObject(MyActor);
```

（来源：`CustomDetailsViewModule.cpp` — `CreateCustomDetailsView`）

### 过滤属性

使用 `TAllowList` 控制可见的 Category 和属性：

```cpp
FCustomDetailsViewArgs Args;

// 只允许特定 Category
Args.CategoryAllowList.Allow(FName("Rendering"));
Args.CategoryAllowList.Allow(FName("Physics"));

// 禁止特定属性
Args.ItemAllowList.Disallow(FCustomDetailsViewItemId::MakePropertyId<AActor>(FName("bHidden")));

// 控制 Widget 类型可见性（只显示 Value 列，隐藏 Name 列）
Args.WidgetTypeAllowList.Allow(ECustomDetailsViewWidgetType::Value);
Args.WidgetTypeAllowList.Allow(ECustomDetailsViewWidgetType::WholeRow);
```

（来源：`CustomDetailsViewArgs.h` — `TAllowList`）

### 插入自定义节点

在树的任意位置插入自定义 Item 或 Category：

```cpp
// 创建自定义 Item
TSharedPtr<ICustomDetailsViewCustomItem> CustomItem = DetailsView->CreateCustomItem(
    RootItem, FName("MyCustomItem"), 
    NSLOCTEXT("MyPlugin", "CustomLabel", "My Custom Control"));

if (CustomItem.IsValid())
{
    CustomItem->SetValueWidget(SNew(STextBlock).Text(FText::FromString("Hello")));
}

// 在某个 hook 节点之后插入
FCustomDetailsViewItemId HookId = FCustomDetailsViewItemId::MakePropertyId<AActor>(FName("ActorLabel"));
DetailsView->ExtendTree(HookId, ECustomDetailsTreeInsertPosition::After, CustomItem->AsItem());

// 创建自定义 Category
TSharedPtr<ICustomDetailsViewCustomCategoryItem> CustomCat = DetailsView->CreateCustomCategoryItem(
    RootItem, FName("MyCategory"),
    NSLOCTEXT("MyPlugin", "CatLabel", "My Custom Category"));
```

（来源：`ICustomDetailsView.h` — `ExtendTree()` / `CreateCustomItem()` / `CreateCustomCategoryItem()`）

### 控制展开状态

```cpp
// 设置展开状态
FCustomDetailsViewItemId ItemId = FCustomDetailsViewItemId::MakeCategoryId(FName("Rendering"));
DetailsView->SetItemExpansionState(ItemId, ECustomDetailsViewExpansion::SelfAndChildrenExpanded);

// 读取展开状态
ECustomDetailsViewExpansion Expansion;
if (DetailsView->GetItemExpansionState(ItemId, Expansion))
{
    // Expansion 包含当前状态
}
```

（来源：`ICustomDetailsView.h` — `GetItemExpansionState()` / `SetItemExpansionState()`）

### 自定义 Widget 覆盖

替换属性行的 Name 或 Value 列 Widget：

```cpp
TSharedPtr<ICustomDetailsViewItem> Item = DetailsView->FindItem(PropertyItemId);
if (Item.IsValid())
{
    // 替换 Value 列
    Item->SetOverrideWidget(ECustomDetailsViewWidgetType::Value,
        SNew(STextBlock).Text(FText::FromString("Custom Value")));
    
    // 替换整行
    Item->SetOverrideWidget(ECustomDetailsViewWidgetType::WholeRow,
        SNew(SHorizontalBox) + SHorizontalBox::Slot() [ SNew(STextBlock).Text(FText::FromString("Custom Row")) ]);
}
```

（来源：`ICustomDetailsViewItem.h` — `SetOverrideWidget()`）

### 过滤搜索

```cpp
// 按关键字过滤，返回是否有匹配项
TArray<FString> FilterStrings = { TEXT("Location"), TEXT("Rotation") };
bool bFound = DetailsView->FilterItems(FilterStrings);
```

（来源：`ICustomDetailsView.h` — `FilterItems()`）

### Sequencer 关键帧集成

为属性行添加 Sequencer 关键帧按钮：

```cpp
FCustomDetailsViewArgs Args;
Args.bAllowGlobalExtensions = true;
Args.KeyframeHandler = MyKeyframeHandler;

// 或手动创建 Sequencer 扩展按钮
TArray<FPropertyRowExtensionButton> ExtensionButtons;
FCustomDetailsViewSequencerUtils::CreateSequencerExtensionButton(
    MyKeyframeHandlerDelegate, PropertyHandle, ExtensionButtons);
```

（来源：`CustomDetailsViewSequencer.h` / `CustomDetailsViewSequencer.cpp`）

### 列宽同步

多个 CustomDetailsView 共享列宽：

```cpp
TSharedPtr<FDetailColumnSizeData> SharedColumnSize = MakeShared<FDetailColumnSizeData>();

FCustomDetailsViewArgs Args1;
Args1.ColumnSizeData = SharedColumnSize;

FCustomDetailsViewArgs Args2;
Args2.ColumnSizeData = SharedColumnSize;

// 两个 View 的列宽会自动同步
```

（来源：`CustomDetailsViewArgs.h` — `ColumnSizeData`）

### 事件委托

```cpp
// 监听 Widget 生成事件
Args.OnItemWidgetGenerated.AddLambda([](TSharedPtr<ICustomDetailsViewItem> Item)
{
    // 每当一个 Item 的 Widget 被创建时触发
});

// 监听树重建完成
Args.OnTreeViewRegenerated.AddLambda([]()
{
    // 整个树的 Widget 重新生成完毕
});

// 监听属性变更完成
Args.OnFinishedChangingProperties.AddLambda([](const FPropertyChangedEvent& Event)
{
    // 用户修改属性后的回调
});

// 监听展开状态变化
Args.OnExpansionStateChanged.AddLambda([](const TSharedRef<ICustomDetailsViewItem>& Item, bool bExpanded)
{
    // 节点展开/折叠时触发
});
```

（来源：`CustomDetailsViewArgs.h`）

## 核心类图

| 类/接口 | 说明 |
|---|---|
| `ICustomDetailsViewModule` | 模块接口，负责创建 `ICustomDetailsView` 实例 |
| `ICustomDetailsView` | 主控件接口，管理整个属性树的生命周期 |
| `ICustomDetailsViewItem` | 树中单个节点的接口，提供 Widget 创建和子节点管理 |
| `ICustomDetailsViewCustomItem` | 自定义 Item 接口，可设置 Label / Value Widget |
| `ICustomDetailsViewCustomCategoryItem` | 自定义 Category 接口 |
| `FCustomDetailsViewItemId` | 节点唯一标识符，基于属性名/类型哈希 |
| `FCustomDetailsViewArgs` | 创建 View 时的配置参数 |
| `FCustomDetailsViewSequencerUtils` | Sequencer 关键帧按钮的工具函数 |
| `UCustomDetailsViewMenuContext` | 右键菜单上下文 UObject |

## Demo 示例

以下展示如何创建一个只显示 Actor Transform 属性的精简面板，并在其中插入一个自定义按钮：

### MyCustomPanel.h

```cpp
#pragma once

#include "ICustomDetailsView.h"
#include "CustomDetailsViewArgs.h"

class FMyCustomPanel
{
public:
    void Init(UObject* InObject);

    TSharedRef<ICustomDetailsView> GetView() const { return DetailsView.ToSharedRef(); }

private:
    TSharedPtr<ICustomDetailsView> DetailsView;
};
```

### MyCustomPanel.cpp

```cpp
#include "MyCustomPanel.h"
#include "CustomDetailsViewModule.h"
#include "CustomDetailsViewArgs.h"
#include "GameFramework/Actor.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Text/STextBlock.h"

void FMyCustomPanel::Init(UObject* InObject)
{
    ICustomDetailsViewModule& Module = ICustomDetailsViewModule::Get();

    FCustomDetailsViewArgs Args;
    Args.bShowCategories = false;
    Args.bAllowResetToDefault = true;
    Args.ValueColumnWidth = 0.5f;

    // 只允许 Transform 相关属性
    Args.ItemAllowList.Allow(FCustomDetailsViewItemId::MakePropertyId<AActor>(FName("RootComponent")));
    
    DetailsView = Module.CreateCustomDetailsView(Args);

    // 插入自定义按钮
    TSharedPtr<ICustomDetailsViewItem> RootItem = DetailsView->GetRootItem();
    TSharedPtr<ICustomDetailsViewCustomItem> ButtonItem = DetailsView->CreateCustomItem(
        RootItem->AsShared(), FName("ResetTransformButton"),
        NSLOCTEXT("MyPanel", "ResetBtn", "Reset Transform"));

    if (ButtonItem.IsValid())
    {
        ButtonItem->SetWholeRowWidget(
            SNew(SButton)
            .Text(NSLOCTEXT("MyPanel", "ResetBtnLabel", "Reset All Transforms"))
            .OnClicked_Lambda([InObject]() -> FReply
            {
                if (AActor* Actor = Cast<AActor>(InObject))
                {
                    Actor->SetActorTransform(FTransform::Identity);
                }
                return FReply::Handled();
            })
        );

        DetailsView->ExtendTree(
            FCustomDetailsViewItemId(), 
            ECustomDetailsTreeInsertPosition::FirstChild, 
            ButtonItem->AsItem());
    }

    DetailsView->SetObject(InObject);
}
```

### Build.cs

```cpp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Slate",
    "SlateCore",
    "CustomDetailsView"
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 系统 |
| `InputCore` | 输入处理 |
| `Slate` | Slate UI 框架 |
| `SlateCore` | Slate 核心类型 |
| `Engine` | 引擎核心（私有依赖） |
| `PropertyEditor` | 属性编辑器基础设施（私有依赖） |
| `ToolMenus` | 右键菜单系统（私有依赖） |
| `UnrealEd` | 编辑器功能（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `df329aa` | Motion Design: 移除 beta 标签 — 插件从 beta 毕业，表明 Epic 认为已达到稳定状态 |
| 2025-07-11 | `2a264ce` | 使用 UnrealCodeFixup 修复 DLL 导出符号 — 代码质量维护 |
| 2025-05-08 | `bdd7ab5` | Motion Design: 从 Experimental 迁移到 VirtualProduction 并标记为 beta — 正式进入 VP 工具链 |

### 维护评价

- **创建时间**：2024-01-28（约 2 年前，在 Experimental 下）
- **迁移路径**：Experimental → VirtualProduction（2025-05），随后移除 beta 标签（2025-09）
- **最近更新**：2025-09，距今约 8 个月
- **活跃度**：活跃维护中。作为 Motion Design 工具链的核心组件，由 Epic VP 团队维护
- **稳定性**：已从 beta 毕业，API 应该趋于稳定
- **推荐使用**：✅ 推荐。适合需要高度自定义属性面板的 Editor 工具开发

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/CustomDetailsView)
