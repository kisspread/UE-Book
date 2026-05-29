# Operator Stack

> Allows you to display linked objects in a container with an intuitive UI

| 属性 | 值 |
|---|---|
| 中文名 | 操作器栈 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OperatorStackEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-09 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/OperatorStack) | |

## 用途

Operator Stack 是一个编辑器扩展插件，旨在为虚拟生产工作流提供高度可定制化的、分层的对象编辑界面。它不仅仅是一个简单的属性编辑器，而是一个框架，允许开发者定义如何将一组相互关联的对象（例如一个对象及其子组件、或一组共享属性的物体）组织成一个直观的、可交互的“栈”式结构。

该插件的核心功能包括：
*   **结构化显示**：将相关对象组织成树状或列表结构，支持展开/折叠。
*   **自定义头部与正文**：为每个栈项（Stack Item）的头部和正文区域提供高度可定制的UI，可以显示图标、标签、工具栏菜单、甚至内联属性编辑。
*   **上下文操作**：支持拖放（Drag & Drop）、选择、搜索过滤、键盘快捷键和上下文菜单。
*   **多栈切换**：在一个面板内，可以通过工具栏快速切换查看同一组对象的不同“定制化”视图（例如，一个栈用于查看场景属性，另一个栈用于查看渲染设置）。

它存在的目的是在虚拟制片等复杂工作流中，为频繁交互的复杂对象集合提供一种比标准细节面板（Details Panel）更直观、更聚焦、功能更强大的专用编辑界面。例如，Motion Design 插件就使用它来构建其场景设置和渲染器管理界面。

## 使用场景

*   **虚拟制片工具链**：为特定于虚拟制片场景的资产（如时间线、渲染层、光照设置）创建专用的、层次清晰的编辑器。
*   **自定义编辑器扩展**：当标准细节面板无法满足你对对象编辑UI的特定需求时，使用此插件构建完全自定义的界面。
*   **复杂对象层次管理**：编辑具有父子关系或逻辑分组的对象集合，允许用户直观地展开/折叠子项并进行批量操作。
*   **Motion Design 工作流**：用于构建 Motion Design 插件自身的编辑面板，如场景设置、克隆器效果器参数面板等。

## 蓝图用法

此插件主要通过 C++ API 进行扩展和自定义，没有暴露 `BlueprintCallable` 函数。其核心功能（如 `UOperatorStackEditorSubsystem`）主要用于底层的编辑器子系统管理，蓝图通常通过该插件的上层应用（如 Motion Design）间接使用其构建的UI。

## C++ 用法

### 头文件引入

```cpp
#include "OperatorStackEditorSubsystem.h"
#include "OperatorStackEditorStackCustomization.h"
#include "OperatorStackEditorItem.h"
#include "OperatorStackEditorObjectItem.h"
#include "OperatorStackEditorStructItem.h"
#include "OperatorStackEditorHeaderBuilder.h"
#include "OperatorStackEditorBodyBuilder.h"
```

### 基本用法

核心用法是继承 `UOperatorStackEditorStackCustomization` 来定义一个自定义的“栈”，并注册到子系统中。这个自定义类决定了如何从上下文中提取要显示的项，以及如何为这些项构建UI。

```cpp
// MyCustomStack.h
#include "OperatorStackEditorStackCustomization.h"
#include "OperatorStackEditorItem.h"

UCLASS()
class UMyCustomStack : public UOperatorStackEditorStackCustomization
{
    GENERATED_BODY()

public:
    UMyCustomStack();
    // 实现基类虚函数以定义栈的行为
    virtual bool GetRootItem(const FOperatorStackEditorContext& InContext, FOperatorStackEditorItemPtr& OutRootItem) const override;
    virtual bool GetChildrenItem(const FOperatorStackEditorItemPtr& InItem, TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const override;
    virtual void CustomizeItemHeader(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorHeaderBuilder& InHeaderBuilder) override;
    virtual void CustomizeItemBody(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorBodyBuilder& InBodyBuilder) override;
};

// MyCustomStack.cpp
UMyCustomStack::UMyCustomStack()
    : UOperatorStackEditorStackCustomization(
        TEXT("MyCustomStack"),          // 唯一标识符
        NSLOCTEXT("MyCustom", "MyCustomStack", "My Custom Stack"), // 工具栏显示名称
        10) // 优先级，数值越大在工具栏越靠前
{
    // 注册此栈支持编辑 AActor 及其子类对象
    RegisterCustomizationFor(AActor::StaticClass());
}

bool UMyCustomStack::GetRootItem(const FOperatorStackEditorContext& InContext, FOperatorStackEditorItemPtr& OutRootItem) const
{
    // 从上下文中获取第一个有效的 Actor 作为栈的根项
    for (const FOperatorStackEditorItemPtr& Item : InContext.GetItems())
    {
        if (Item.IsValid() && Item->IsA<AActor>() && Item->HasValue())
        {
            OutRootItem = Item;
            return true;
        }
    }
    return false;
}

bool UMyCustomStack::GetChildrenItem(const FOperatorStackEditorItemPtr& InItem, TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const
{
    // 对于 Actor 项，返回其 ActorComponent 子项
    if (const AActor* Actor = InItem->Get<AActor>(0))
    {
        TArray<UActorComponent*> Components;
        Actor->GetComponents(Components);
        for (UActorComponent* Comp : Components)
        {
            OutChildrenItems.Add(MakeShared<FOperatorStackEditorObjectItem>(Comp));
        }
        return true;
    }
    return false;
}

void UMyCustomStack::CustomizeItemHeader(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorHeaderBuilder& InHeaderBuilder)
{
    // 为每个项自定义头部
    if (const UObject* Obj = InItem->Get<UObject>(0))
    {
        InHeaderBuilder
            .SetLabel(FText::FromString(Obj->GetName()))
            .SetIcon(FAppStyle::Get().GetBrush(TEXT("ClassIcon.ActorComponent"))) // 设置图标
            .SetExpandable(true) // 允许展开显示子项（组件）
            .SetDraggable(true); // 允许拖放
    }
}

void UMyCustomStack::CustomizeItemBody(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorBodyBuilder& InBodyBuilder)
{
    // 为每个项自定义正文，这里选择显示一个细节视图
    InBodyBuilder
        .SetShowDetailsView(true)
        .DisallowCategory(TEXT("Tags")); // 在细节视图中隐藏“Tags”分类
}
```

### 进阶用法

1.  **注册与激活栈**：在编辑器模块或插件启动时，将自定义栈注册到 `UOperatorStackEditorSubsystem`。
    ```cpp
    // 在你的编辑器模块 StartupModule 中
    UOperatorStackEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UOperatorStackEditorSubsystem>();
    if (Subsystem)
    {
        Subsystem->RegisterStackCustomization(UMyCustomStack::StaticClass());
    }
    ```

2.  **生成与配置面板**：从子系统生成一个可嵌入任何编辑器界面的 Widget。
    ```cpp
    UOperatorStackEditorSubsystem* Subsystem = ...;
    TSharedRef<SOperatorStackEditorWidget> OperatorStackWidget = Subsystem->GenerateWidget();
    // 设置初始上下文（要编辑的对象）
    TArray<TSharedPtr<FOperatorStackEditorItem>> Items;
    Items.Add(MakeShared<FOperatorStackEditorObjectItem>(MyActor));
    OperatorStackWidget->SetContext(FOperatorStackEditorContext(Items));
    // 可以配置工具栏可见性、激活特定栈等
    OperatorStackWidget->SetToolbarVisibility(true);
    OperatorStackWidget->SetActiveCustomization(TEXT("MyCustomStack"));
    ```

3.  **实现拖放**：在自定义栈中重写 `OnIsItemDraggable` 和 `OnDropItem` 虚函数。

4.  **实现搜索**：通过 `FOperatorStackEditorHeaderBuilder::SetSearchAllowed` 和 `SetSearchKeywords` 为项启用搜索关键字。

5.  **自定义上下文菜单**：通过 `FOperatorStackEditorHeaderBuilder::SetContextMenu` 指定一个 `FName`，然后使用 `UToolMenus` 注册该名称的菜单。菜单可以通过 `UOperatorStackEditorMenuContext` 获得当前选中的项和上下文。

## Demo 示例

以下是一个最小的自定义操作器栈实现，用于显示和编辑 `AActor` 及其组件。

**MyOperatorStackDemo.h**
```cpp
#pragma once
#include "OperatorStackEditorStackCustomization.h"
#include "MyOperatorStackDemo.generated.h"

UCLASS()
class UMyOperatorStackDemo : public UOperatorStackEditorStackCustomization
{
    GENERATED_BODY()

public:
    UMyOperatorStackDemo();
    virtual bool GetRootItem(const FOperatorStackEditorContext& InContext, FOperatorStackEditorItemPtr& OutRootItem) const override;
    virtual bool GetChildrenItem(const FOperatorStackEditorItemPtr& InItem, TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const override;
    virtual void CustomizeItemHeader(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorHeaderBuilder& InHeaderBuilder) override;
};
```

**MyOperatorStackDemo.cpp**
```cpp
#include "MyOperatorStackDemo.h"
#include "Actor.h"
#include "Components/ActorComponent.h"
#include "OperatorStackEditorObjectItem.h"
#include "Styling/AppStyle.h"

UMyOperatorStackDemo::UMyOperatorStackDemo()
    : UOperatorStackEditorStackCustomization(
        TEXT("ActorComponentStack"),
        NSLOCTEXT("Demo", "ActorComponentStack", "Actor & Components"),
        100)
{
    RegisterCustomizationFor(AActor::StaticClass());
}

bool UMyOperatorStackDemo::GetRootItem(const FOperatorStackEditorContext& InContext, FOperatorStackEditorItemPtr& OutRootItem) const
{
    if (InContext.GetItems().Num() > 0)
    {
        OutRootItem = InContext.GetItems()[0];
        return true;
    }
    return false;
}

bool UMyOperatorStackDemo::GetChildrenItem(const FOperatorStackEditorItemPtr& InItem, TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const
{
    if (const AActor* Actor = InItem->Get<AActor>(0))
    {
        TInlineComponentArray<UActorComponent*> Components(Actor);
        for (UActorComponent* Comp : Components)
        {
            OutChildrenItems.Add(MakeShared<FOperatorStackEditorObjectItem>(Comp));
        }
        return !OutChildrenItems.IsEmpty();
    }
    return false;
}

void UMyOperatorStackDemo::CustomizeItemHeader(const FOperatorStackEditorItemPtr& InItem, const FOperatorStackEditorTree& InItemTree, FOperatorStackEditorHeaderBuilder& InHeaderBuilder)
{
    if (InItem->IsA<AActor>())
    {
        if (const AActor* Actor = InItem->Get<AActor>(0))
        {
            InHeaderBuilder
                .SetLabel(FText::FromString(*Actor->GetActorLabel()))
                .SetIcon(FAppStyle::Get().GetBrush(TEXT("ClassIcon.Actor")))
                .SetExpandable(true)
                .SetStartsExpanded(true);
        }
    }
    else if (InItem->IsA<UActorComponent>())
    {
        if (const UActorComponent* Comp = InItem->Get<UActorComponent>(0))
        {
            InHeaderBuilder
                .SetLabel(FText::FromString(*Comp->GetName()))
                .SetIcon(FAppStyle::Get().GetBrush(TEXT("ClassIcon.ActorComponent")))
                .SetExpandable(false);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CustomDetailsView` | 在栈项的正文区域嵌入可自定义的细节视图。 |
| `ToolMenus` | 为栈项提供上下文菜单和工具栏菜单功能。 |
| `TypedElementFramework` | 与虚幻引擎的类型化元素选择集集成，处理编辑器中的对象选择。 |
| `TypedElementRuntime` | 类型化元素框架的运行时支持。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `3950790a` | Motion Design: moved Motion-Design tabs (Scene Settings, Outliner) in level editor to their own gro | 将Motion Design的标签页（场景设置、大纲视图）移至独立分组，改善UI组织。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF，可能是代码标准化或兼容性更新。 |
| 2025-11-20 | `f8d6103d` | Enable NDK 29 for Android, fix compilation issues | 启用Android NDK 29支持并修复相关编译问题。 |
| 2025-09-23 | `cfeda80a` | MotionDesign : OperatorStack | 提交信息非常简洁，可能是针对Motion Design中Operator Stack功能的改进或修复。 |
| 2025-09-16 | `77ee7eae` | Motion Design: removed beta tag from motion design plugins. | 从Motion Design插件中移除了beta标签，表明其核心功能已趋于稳定。 |

### 维护评价

*   **创建时间**：创建于 2025 年 5 月，插件历史不到一年。
*   **维护频率**：截至知识截止日期，有持续的提交记录，最近一次更新在 2026 年 5 月，涉及功能调整和代码维护。
*   **维护状态**：**活跃维护中**。插件从实验阶段迁移至 Virtual Production 分类，并移除了 beta 标签，表明 Epic 将其视为该领域的重要工具。后续更新也专注于集成和改进。
*   **已知问题/限制**：作为编辑器扩展插件，其 API 较为底层和复杂，主要面向插件开发者，而非终端用户。没有发现重大的已知限制。
*   **推荐使用**：**推荐**。对于需要构建复杂、自定义编辑器界面的虚拟生产或 Motion Design 相关工具开发，这是一个强大且官方维护的框架。对于其他类型的游戏开发，除非有高度定制编辑器UI的需求，否则可能不需要直接使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/OperatorStack)
- 官方文档：无（未提供）
- 测试用例：源码内未发现独立的测试文件。