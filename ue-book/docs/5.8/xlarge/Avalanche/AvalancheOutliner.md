# Avalanche Outliner

> Compositing, designer and broadcasting tool. Plugin Dependencies: Advanced Renamer, Custom Details View, Dynamic Material, Geometry Cache, Geometry Scripting, Media Compositing, Media IO Framework, Mesh Modeling Toolset Exp, Remote Control, SVG Importer, Text3D and ActorModifierCore.

| 属性 | 值 |
|---|---|
| 中文名 | 运动设计大纲 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器 UI 资产、自定义 Slate 控件） |
| 模块 | `AvalancheOutliner` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) | |

> **注意**：本文档聚焦于 `AvalancheOutliner` 子模块。该模块是 [Avalanche (Motion Design)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche) 超大型插件（43 个模块、2060 个源文件）的一部分。完整插件文档请参见 Avalanche 主文档。

---

## 用途

AvalancheOutliner 为 Motion Design 工具链提供了一个**专有的场景大纲视图**，替代 Unreal Engine 标准的 Scene Outliner，专门用于管理运动设计中的元素层级关系。

与标准 Scene Outliner 相比，该模块的核心差异在于：

- **支持自定义条目类型**：不仅管理 Actor/Component，还支持文件夹、材质引用、Item Proxy 等自定义节点
- **多视图实例**：一个 FAvaOutliner 可注册多个独立的 FAvaOutlinerView，每个视图有自己的过滤器、选择状态和列配置
- **可扩展的列系统**：通过 `IAvaOutlinerColumn` 和 `FAvaOutlinerColumnExtender` 注册自定义列（如可见性、锁定、颜色、标签）
- **高级文本过滤**：支持表达式工厂（Expression Factory）和建议工厂（Suggestion Factory）的注册机制
- **Item Proxy 系统**：允许在主条目下插入"代理"节点（例如在组件下方显示其材质引用）
- **拖放处理链**：通过可扩展的 DropHandler 实现复杂的拖放逻辑
- **序列化与持久化**：完整保存/恢复大纲状态（包括视图标志、列可见性、颜色映射、自定义过滤器）

---

## 使用场景

- 你在 Motion Design 项目中管理复杂的元素层级 → 使用 AvalancheOutliner 替代标准大纲
- 你需要自定义拖放逻辑（例如将材质拖拽到组件槽位） → 实现 `FAvaOutlinerItemDropHandler` 并注册到 `FAvaOutlinerItemDragDropOp`
- 你需要在大纲中显示自定义信息列（如颜色标记、运行时可见性） → 实现 `IAvaOutlinerColumn`
- 你需要扩展搜索过滤功能 → 注册自定义 `IAvaFilterExpressionFactory` 或 `IAvaFilterSuggestionFactory`
- 你需要为自定义对象类型创建大纲条目 → 继承 `FAvaOutlinerItem` 并通过 `FindOrAdd` 注册

---

## 架构总览

```
UAvaOutlinerSubsystem (UWorldSubsystem)
  └─ FAvaOutliner (IAvaOutliner)
       ├─ FAvaOutlinerTreeRoot (根节点)
       ├─ ItemMap (所有注册条目)
       ├─ ItemProxyRegistry (代理工厂注册表)
       ├─ PendingActions (操作队列)
       └─ FAvaOutlinerView[] (多个视图实例)
            ├─ SAvaOutliner (Slate Widget)
            │    ├─ SAvaOutlinerTreeView (树视图)
            │    ├─ SAvaOutlinerItemFilters (过滤栏)
            │    └─ HeaderRow + Columns
            ├─ TextFilter (文本搜索过滤)
            ├─ ItemFilters[] (类型过滤器)
            └─ SelectedItems[] (视图独立的选择状态)
```

### 核心类

| 类 | 说明 |
|---|---|
| `UAvaOutlinerSubsystem` | World 子系统，负责实例化并持有大纲引用 |
| `FAvaOutliner` | 核心管理器，维护所有条目、代理注册表、操作队列 |
| `FAvaOutlinerView` | 视图实例，管理显示状态、过滤器、选择、列配置 |
| `IAvaOutlinerModule` | 模块接口，提供全局代理注册表和过滤器工厂注册 |
| `IAvaOutlinerProvider` | 提供者接口，由 Motion Design 主模块实现，提供外部能力（世界、模式工具、复制/删除逻辑等） |

### 条目类型层次

```
IAvaOutlinerItem (接口)
  └─ FAvaOutlinerItem (基类实现)
       ├─ FAvaOutlinerTreeRoot (树根)
       ├─ FAvaOutlinerObject (UObject 包装)
       │    ├─ FAvaOutlinerActor (AActor)
       │    ├─ FAvaOutlinerComponent (USceneComponent)
       │    ├─ FAvaOutlinerLevel (ULevel)
       │    ├─ FAvaOutlinerSharedObject (共享对象，如材质)
       │    └─ FAvaOutlinerObjectReference (对象引用)
       │         └─ FAvaOutlinerMaterial (材质引用)
       └─ FAvaOutlinerItemProxy (代理节点)
```

---

## 蓝图用法

> **注意**：AvalancheOutliner 是一个**编辑器运行时模块**，其主要 API 面向 C++ 扩展。`UAvaOutlinerSettings` 提供了部分可配置属性，但大纲的核心交互通过 C++ 接口完成。

### 设置项

大纲行为可通过 `Editor Preferences → Plugins → Outliner` 配置：

| 设置 | 说明 | 默认值 |
|---|---|---|
| `bUseMutedHierarchy` | 当父节点被过滤时，以只读模式显示父节点 | `true` |
| `bAutoExpandToSelection` | 选中条目时自动展开到该条目 | `true` |
| `bAlwaysShowVisibilityState` | 始终显示可见性状态（而非仅悬停时） | `false` |
| `bAlwaysShowLockState` | 始终显示锁定状态（而非仅悬停时） | `false` |
| `ItemDefaultViewMode` | 非 Actor/Component 条目的默认视图模式 | `HorizontalItemList` |
| `ItemProxyViewMode` | 代理条目的默认视图模式 | `None` |
| `ItemColorMap` | 可用的颜色名称 → 颜色值映射 | — |
| `CustomItemTypeFilters` | 自定义类型过滤器定义 | — |

---

## C++ 用法

### 头文件引入

```cpp
// 核心接口
#include "IAvaOutliner.h"
#include "IAvaOutlinerModule.h"
#include "AvaOutlinerSubsystem.h"

// 条目类型
#include "Item/AvaOutlinerItem.h"
#include "Item/AvaOutlinerItemId.h"
#include "Item/AvaOutlinerObject.h"
#include "Item/AvaOutlinerActor.h"
#include "Item/AvaOutlinerComponent.h"

// 过滤器
#include "Filters/AvaOutlinerItemTypeFilter.h"
#include "IAvaFilterExpressionFactory.h"
#include "IAvaFilterSuggestionFactory.h"

// 代理
#include "ItemProxies/AvaOutlinerItemProxyRegistry.h"
#include "Item/AvaOutlinerItemProxy.h"

// 拖放
#include "DragDropOps/AvaOutlinerItemDragDropOp.h"
#include "DragDropOps/Handlers/AvaOutlinerItemDropHandler.h"
```

### 获取大纲实例

```cpp
// 通过 World 子系统获取
UAvaOutlinerSubsystem* Subsystem = World->GetSubsystem<UAvaOutlinerSubsystem>();
TSharedPtr<IAvaOutliner> Outliner = Subsystem->GetOutliner();

// 或创建（需要提供 IAvaOutlinerProvider）
TSharedRef<IAvaOutliner> Outliner = Subsystem->GetOrCreateOutliner(*Provider);
```

### 查找或创建条目

```cpp
// 注册一个 Actor 条目（如果已存在则返回现有实例）
TSharedRef<FAvaOutlinerActor> ActorItem = Outliner->FindOrAdd<FAvaOutlinerActor>(MyActor);

// 注册一个 Component 条目
TSharedRef<FAvaOutlinerComponent> CompItem = Outliner->FindOrAdd<FAvaOutlinerComponent>(MyComponent);

// 通过 ID 查找条目
FAvaOutlinerItemId ItemId(MyActor);
FAvaOutlinerItemPtr FoundItem = Outliner->FindItem(ItemId);
```

### 注册自定义列

```cpp
// 实现自定义列
class FAvaMyCustomColumn : public IAvaOutlinerColumn
{
public:
    virtual SHeaderRow::FColumn::FArguments ConstructHeaderRowColumn() override
    {
        return SHeaderRow::Column("MyColumn")
            .DefaultLabel(NSLOCTEXT("MyColumn", "Name", "My Column"))
            .FillWidth(0.2f);
    }

    virtual TSharedRef<SWidget> ConstructRowWidget(
        FAvaOutlinerItemPtr InItem,
        const TSharedRef<FAvaOutlinerView>& InOutlinerView,
        const TSharedRef<SAvaOutlinerTreeRow>& InRow) override
    {
        return SNew(STextBlock).Text(FText::FromString(TEXT("Custom")));
    }
};

// 在 IAvaOutlinerProvider::ExtendOutlinerColumns 中注册
void FMyProvider::ExtendOutlinerColumns(FAvaOutlinerColumnExtender& InExtender)
{
    InExtender.AddColumn<FAvaMyCustomColumn>();
}
```

### 注册自定义类型过滤器

```cpp
// 通过模块注册
IAvaOutlinerModule& Module = IAvaOutlinerModule::Get();

// 注册图标覆盖
Module.RegisterOverriddenIcon<FAvaOutlinerActor, FMyActorIconCustomization>(MyActorClass);
```

### 注册过滤器表达式工厂

```cpp
// 实现表达式工厂
class FMyFilterExpressionFactory : public IAvaFilterExpressionFactory
{
public:
    virtual FName GetFilterIdentifier() const override { return FName("MyFilter"); }

    virtual bool FilterExpression(const IAvaOutlinerItem& InItem, const FAvaTextFilterArgs& InArgs) const override
    {
        // 自定义过滤逻辑
        return InArgs.ValueToCheck.ToString().Contains(TEXT("my_keyword"));
    }

    virtual bool SupportsComparisonOperation(const ETextFilterComparisonOperation& InOp) const override
    {
        return InOp == ETextFilterComparisonOperation::Equal;
    }
};

// 注册
FAvaOutlinerModule::Get().RegisterFilterExpressionFactory<FMyFilterExpressionFactory>();
```

### 注册过滤器建议工厂

```cpp
class FMySuggestionFactory : public IAvaFilterSuggestionFactory
{
public:
    virtual EAvaFilterSuggestionType GetSuggestionType() const override
    {
        return EAvaFilterSuggestionType::Generic;
    }

    virtual FName GetSuggestionIdentifier() const override
    {
        return FName("MySuggestion");
    }

    virtual void AddSuggestion(const TSharedRef<FAvaFilterSuggestionPayload> InPayload) override
    {
        InPayload->OutPossibleSuggestions.Add(
            FAssetSearchBoxSuggestion(FText::FromString(TEXT("color:")), FText::GetEmpty()));
    }
};

FAvaOutlinerModule::Get().RegisterFilterSuggestionFactory<FMySuggestionFactory>();
```

### 注册自定义条目代理工厂

```cpp
// 实现代理
class FAvaMyItemProxy : public FAvaOutlinerItemProxy
{
public:
    FAvaMyItemProxy(IAvaOutliner& InOutliner, const FAvaOutlinerItemPtr& InParentItem)
        : FAvaOutlinerItemProxy(InOutliner, InParentItem) {}

    virtual void GetProxiedItems(
        const TSharedRef<IAvaOutlinerItem>& InParent,
        TArray<FAvaOutlinerItemPtr>& OutChildren,
        bool bInRecursive) override
    {
        // 提供代理的子条目
    }

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyProxy", "Name", "My Proxy");
    }
};

// 通过代理注册表注册
FAvaOutlinerItemProxyRegistry& Registry = Module.GetItemProxyRegistry();
Registry.RegisterItemProxyWithDefaultFactory<FAvaMyItemProxy>();
```

### 自定义拖放处理器

```cpp
class FMyDropHandler : public FAvaOutlinerItemDropHandler
{
protected:
    virtual bool IsDraggedItemSupported(const FAvaOutlinerItemPtr& InItem) const override
    {
        return InItem.IsValid() && InItem->IsA<FAvaOutlinerActor>();
    }

    virtual TOptional<EItemDropZone> CanDrop(
        EItemDropZone InDropZone,
        FAvaOutlinerItemPtr InTargetItem) const override
    {
        if (InTargetItem.IsValid() && InTargetItem->IsA<FAvaOutlinerActor>())
        {
            return InDropZone;
        }
        return TOptional<EItemDropZone>();
    }

    virtual bool Drop(EItemDropZone InDropZone, FAvaOutlinerItemPtr InTargetItem) override
    {
        // 实现自定义放置逻辑
        ForEachItem<FAvaOutlinerActor>([&](FAvaOutlinerActor& InActor) -> EIterationResult
        {
            // 处理拖放
            return EIterationResult::Continue;
        });
        return true;
    }
};

// 在 OnItemDragDropOpInitialized 回调中添加
FAvaOutlinerItemDragDropOp::OnItemDragDropOpInitialized().AddLambda(
    [](FAvaOutlinerItemDragDropOp& InOp)
    {
        InOp.AddDropHandler<FMyDropHandler>();
    });
```

### 大纲条目的颜色管理

```cpp
// 设置条目颜色
FAvaOutlinerItemPtr Item = Outliner->FindItem(SomeItemId);
Outliner->SetItemColor(Item, FName("Red"));

// 获取条目颜色（递归查找父节点）
TOptional<FAvaOutlinerColorPair> Color = Outliner->FindItemColor(Item, true);

// 移除颜色
Outliner->RemoveItemColor(Item);
```

### 多视图管理

```cpp
// 注册新视图
TSharedPtr<IAvaOutlinerView> View = Outliner->RegisterOutlinerView(0);
TSharedPtr<IAvaOutlinerView> View2 = Outliner->RegisterOutlinerView(1);

// 获取特定视图
TSharedPtr<IAvaOutlinerView> RetrievedView = Outliner->GetOutlinerView(0);

// 遍历所有视图
// （通过 FAvaOutliner 的 ForEachOutlinerView 方法）
```

### 批量操作

```cpp
// 批量添加条目
FAvaOutlinerAddItemParams AddParams;
AddParams.Items.Add(Item1);
AddParams.Items.Add(Item2);
AddParams.Flags = EAvaOutlinerAddItemFlags::Select | EAvaOutlinerAddItemFlags::Transact;
AddParams.RelativeItem = ReferenceItem;
AddParams.RelativeDropZone = EItemDropZone::Below;
TargetItem->AddChildren(AddParams);

// 复制条目
TArray<FAvaOutlinerItemPtr> ItemsToDuplicate = { Item1, Item2 };
Outliner->DuplicateItems(ItemsToDuplicate, RelativeItem, EItemDropZone::Below);

// 删除条目
TArray<FAvaOutlinerItemPtr> ItemsToDelete = { Item1, Item2 };
Outliner->DeleteItems(ItemsToDelete);
```

---

## Demo 示例

### 自定义大纲条目类型

```cpp
// MyOutlinerItem.h
#pragma once

#include "Item/AvaOutlinerItem.h"

class FMyOutlinerItem : public FAvaOutlinerItem
{
public:
    UE_AVA_INHERITS_WITH_SUPER(FMyOutlinerItem, FAvaOutlinerItem);

    FMyOutlinerItem(IAvaOutliner& InOutliner, UObject* InCustomObject);

    // IAvaOutlinerItem
    virtual bool IsItemValid() const override;
    virtual void RefreshChildren() override;
    virtual bool CanBeTopLevel() const override { return true; }
    virtual bool CanAddChild(const FAvaOutlinerItemPtr& InChild) const override;
    virtual FText GetDisplayName() const override;
    virtual FText GetClassName() const override;
    virtual FSlateIcon GetIcon() const override;
    virtual bool CanRename() const override { return true; }
    virtual bool Rename(const FString& InName) override;
    virtual bool CanDelete() const override { return true; }
    virtual bool Delete() override;
    virtual TSharedRef<SWidget> GenerateLabelWidget(
        const TSharedRef<SAvaOutlinerTreeRow>& InRow) override;

protected:
    virtual FAvaOutlinerItemId CalculateItemId() const override;

private:
    TWeakObjectPtr<UObject> CustomObject;
};
```

```cpp
// MyOutlinerItem.cpp
#include "MyOutlinerItem.h"

FMyOutlinerItem::FMyOutlinerItem(IAvaOutliner& InOutliner, UObject* InCustomObject)
    : FAvaOutlinerItem(InOutliner)
    , CustomObject(InCustomObject)
{
}

bool FMyOutlinerItem::IsItemValid() const
{
    return CustomObject.IsValid();
}

void FMyOutlinerItem::RefreshChildren()
{
    // 根据自定义对象的逻辑刷新子条目
}

bool FMyOutlinerItem::CanAddChild(const FAvaOutlinerItemPtr& InChild) const
{
    // 定义允许的子条目类型
    return InChild.IsValid() && InChild->IsA<FMyOutlinerItem>();
}

FText FMyOutlinerItem::GetDisplayName() const
{
    if (CustomObject.IsValid())
    {
        return FText::FromString(CustomObject->GetName());
    }
    return FText::GetEmpty();
}

FText FMyOutlinerItem::GetClassName() const
{
    return NSLOCTEXT("MyItem", "ClassName", "My Custom Item");
}

FSlateIcon FMyOutlinerItem::GetIcon() const
{
    return FSlateIcon(FAppStyle::GetAppStyleSetName(), "LevelEditor.Tabs.Viewports");
}

bool FMyOutlinerItem::Rename(const FString& InName)
{
    if (CustomObject.IsValid())
    {
        CustomObject->Rename(*InName);
        return true;
    }
    return false;
}

bool FMyOutlinerItem::Delete()
{
    if (CustomObject.IsValid())
    {
        CustomObject->MarkAsGarbage();
        return true;
    }
    return false;
}

TSharedRef<SWidget> FMyOutlinerItem::GenerateLabelWidget(
    const TSharedRef<SAvaOutlinerTreeRow>& InRow)
{
    return SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .AutoWidth()
        .Padding(4.f, 0.f)
        [
            SNew(SImage).Image(GetIcon().GetIcon())
        ]
        + SHorizontalBox::Slot()
        .FillWidth(1.f)
        .VAlign(VAlign_Center)
        [
            SNew(STextBlock)
            .Text(this, &FMyOutlinerItem::GetDisplayName())
        ];
}

FAvaOutlinerItemId FMyOutlinerItem::CalculateItemId() const
{
    if (CustomObject.IsValid())
    {
        return FAvaOutlinerItemId(CustomObject.Get());
    }
    return FAvaOutlinerItemId();
}

// 注册：在 Outliner 初始化时
void FMyOutlinerProvider::InitializeOutliner(TSharedRef<IAvaOutliner> InOutliner)
{
    InOutliner->FindOrAdd<FMyOutlinerItem>(MyCustomObject);
}
```

### 自定义 Item Proxy

```cpp
// MyItemProxy.h
#pragma once

#include "Item/AvaOutlinerItemProxy.h"

class FMyItemProxy : public FAvaOutlinerItemProxy
{
public:
    UE_AVA_INHERITS_WITH_SUPER(FMyItemProxy, FAvaOutlinerItemProxy);

    FMyItemProxy(IAvaOutliner& InOutliner, const FAvaOutlinerItemPtr& InParentItem)
        : FAvaOutlinerItemProxy(InOutliner, InParentItem) {}

    virtual FText GetDisplayName() const override
    {
        return NSLOCTEXT("MyProxy", "Name", "Related Items");
    }

    virtual FText GetClassName() const override
    {
        return NSLOCTEXT("MyProxy", "Class", "Proxy");
    }

    virtual FSlateIcon GetIcon() const override
    {
        return FSlateIcon(FAppStyle::GetAppStyleSetName(), "Icons.FilledCircle");
    }

    virtual void GetProxiedItems(
        const TSharedRef<IAvaOutlinerItem>& InParent,
        TArray<FAvaOutlinerItemPtr>& OutChildren,
        bool bInRecursive) override
    {
        // 从父条目获取关联的条目
        // 例如：获取组件引用的材质列表
    }

    virtual TSharedRef<SWidget> GenerateLabelWidget(
        const TSharedRef<SAvaOutlinerTreeRow>& InRow) override
    {
        return SNew(STextBlock)
            .Text(this, &FMyItemProxy::GetDisplayName())
            .ColorAndOpacity(FSlateColor(FLinearColor(0.6f, 0.6f, 0.6f)));
    }
};
```

---

## 模块依赖

> AvalancheOutliner 的 Build.cs 未提供，以下依赖基于源码分析推断。

| 模块 | 用途 |
|---|---|
| `AvalancheCore` | 提供 `TAvaType`、`FAvaTypeId` 等 Motion Design 核心类型系统 |
| `AvalancheSceneTree` | 场景树序列化支持（`FAvaSceneTree`、`FAvaSceneItem`） |

> 其余均为标准引擎模块（Core, CoreUObject, Engine, Slate, SlateCore, DeveloperSettings, InputCore, ToolMenus 等）。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own group | 将场景设置和大纲标签页移至独立标签组 |
| 2026-05-20 | `505de853` | Motion Design: added MRQ analytics when using the Rundown Page setting | 添加 MRQ 分析功能 |
| 2026-05-19 | `16f8f83c` | Motion Design: added page loading options (All, Next, Selected) to the show control toolbar and added | 添加页面加载选项到播放控制工具栏 |
| 2026-05-14 | `bf538a9e` | Motion Design: added project setting to force disable collisions for Text3D and shapes. | 添加强制禁用 Text3D 和形状碰撞的项目设置 |
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated with context | 重构视口客户端关联/解除关联的通知逻辑 |

### 维护评价

- **活跃维护**：AvalancheOutliner 作为 Motion Design 核心组件正在被积极维护。近期更新包括 UI 布局调整（`3950790a` 直接涉及大纲标签页），表明该模块仍在功能迭代中。
- **创建时间**：2025 年 5 月从 `Plugins/Experimental` 迁移至 `Plugins/VirtualProduction`，标志着从实验性状态向正式发布过渡。实际源码历史更长（此前在 Experimental 目录下开发）。
- **实验性标记**：插件仍在 `IsBetaVersion=true` 状态，API 可能在未来版本中发生变化。
- **注意事项**：
  - 插件默认未启用（`EnabledByDefault=false`），需在项目设置中手动启用
  - 作为 Motion Design 插件的一部分，需要多个依赖插件（Remote Control、Text3D、SVG Importer 等）
  - 主要面向编辑器场景（虽然模块类型为 Runtime，但核心使用场景在编辑器内）

**推荐使用**：✅ 适合正在使用 Motion Design 工具链的项目。如果只需要标准大纲视图，无需引入此模块。

---

## 相关链接

- [源码 (Avalanche 插件根目录)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche)
- [源码 (AvalancheOutliner 模块)](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheOutliner)
- [AvalancheOutliner Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheOutliner/AvalancheOutliner.Build.cs)
- [IAvaOutliner.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheOutliner/Public/IAvaOutliner.h)
- [IAvaOutlinerModule.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheOutliner/Public/IAvaOutlinerModule.h)
- [IAvaOutlinerItem.h](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/VirtualProduction/Avalanche/Source/AvalancheOutliner/Public/Item/IAvaOutlinerItem.h)