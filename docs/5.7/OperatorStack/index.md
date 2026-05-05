# Operator Stack

> Allows you to display linked objects in a container with an intuitive UI

| 属性 | 值 |
|---|---|
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OperatorStackEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2025-05-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/OperatorStack) | |

## 用途

Operator Stack 是一个编辑器 UI 框架插件，为 Virtual Production 工具链提供**可扩展的树形列表面板**。它解决的核心问题是：当你有大量关联对象（如动画器、属性控制器等）需要在一个统一的、可分层的 UI 中展示和编辑时，如何让不同插件共享同一套编辑器面板基础设施，同时各自定义自己的数据源和渲染逻辑。

这个插件本身不直接面向最终用户——它是一个**基础设施插件**，为其他 VP 插件（如 PropertyAnimatorCore、Motion Design 等）提供 Operator Stack 面板的注册、渲染和交互框架。每个消费者只需继承 `UOperatorStackEditorStackCustomization` 并实现几个虚函数，就能自动获得：

- 树形结构的 Header/Body/Footer 展示
- 搜索过滤
- 拖放支持
- 右键菜单
- Details View 集成
- 多 Stack 切换（工具栏标签页）

插件在编辑器启动时自动扫描所有继承自 `UOperatorStackEditorStackCustomization` 的 UClass 并注册，无需手动调用注册 API。

## 使用场景

- 你在做一个 Virtual Production 工具，需要一个类似 Details Panel 但支持树形层次的自定义面板 → 用 Operator Stack
- 你需要让多个插件共享同一个编辑器面板框架，各自定义数据源和渲染 → 用 Operator Stack
- 你在做属性动画器/控制器，需要在编辑器中展示 Component → Animator → Property 的层次关系 → 用 Operator Stack（参考 PropertyAnimatorCore 的用法）
- 你需要一个支持搜索、拖放、右键菜单的树形列表 UI → 用 Operator Stack

## 蓝图用法

Operator Stack 是纯 Editor C++ 插件，没有暴露 BlueprintCallable 函数。所有交互都通过 C++ 继承体系完成。

## C++ 用法

### 头文件引入

```cpp
#include "Customizations/OperatorStackEditorStackCustomization.h"
#include "Subsystems/OperatorStackEditorSubsystem.h"
#include "Items/OperatorStackEditorObjectItem.h"
#include "Contexts/OperatorStackEditorContext.h"
```

### 核心架构

Operator Stack 的核心设计模式是**模板方法模式**。整个系统由以下层次组成：

1. **`UOperatorStackEditorSubsystem`** — 编辑器子系统，管理所有 Stack Customization 的注册和 Widget 生命周期
2. **`UOperatorStackEditorStackCustomization`** — 抽象基类，每个消费者继承它来定义自己的数据源和 UI 逻辑
3. **`FOperatorStackEditorTree`** — 根据 Context 和 Customization 构建的树结构
4. **`FOperatorStackEditorItem`** — 树中每个节点的数据封装（Object / Struct / Primitive / Group）
5. **Builder 系列**（Header / Body / Footer）— 在 Customization 回调中使用，用于声明式地定义 UI

### 创建自定义 Stack

最典型的用法是继承 `UOperatorStackEditorStackCustomization` 并重写虚函数。以下是来自 `PropertyAnimatorCoreEditor` 的真实示例：

```cpp
// 来源: PropertyAnimatorCore/Source/PropertyAnimatorCoreEditor/Private/Customizations/PropertyAnimatorCoreEditorStackCustomization.h

UCLASS()
class UMyEditorStackCustomization : public UOperatorStackEditorStackCustomization
{
    GENERATED_BODY()

public:
    UMyEditorStackCustomization()
        : UOperatorStackEditorStackCustomization(
            TEXT("MyCustomization"),     // 唯一标识符
            NSLOCTEXT("My", "Label", "My Stack"),  // 工具栏显示名
            100                           // 优先级（越大越靠前）
        )
    {
        // 注册支持的 Item 类型
        RegisterCustomizationFor(UMyComponent::StaticClass());
    }

    // 从 Context 中提取根 Item
    virtual bool GetRootItem(
        const FOperatorStackEditorContext& InContext,
        FOperatorStackEditorItemPtr& OutRootItem) const override;

    // 从父 Item 获取子 Item 列表
    virtual bool GetChildrenItem(
        const FOperatorStackEditorItemPtr& InItem,
        TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const override;

    // 自定义整个 Stack 的 Header
    virtual void CustomizeStackHeader(
        const FOperatorStackEditorTree& InItemTree,
        FOperatorStackEditorHeaderBuilder& InHeaderBuilder) override;

    // 自定义每个 Item 的 Header
    virtual void CustomizeItemHeader(
        const FOperatorStackEditorItemPtr& InItem,
        const FOperatorStackEditorTree& InItemTree,
        FOperatorStackEditorHeaderBuilder& InHeaderBuilder) override;

    // 自定义每个 Item 的 Body（通常显示 Details View）
    virtual void CustomizeItemBody(
        const FOperatorStackEditorItemPtr& InItem,
        const FOperatorStackEditorTree& InItemTree,
        FOperatorStackEditorBodyBuilder& InBodyBuilder) override;
};
```

### Item 类型系统

`FOperatorStackEditorItem` 是所有 Item 的基类，通过模板方法提供类型安全的访问：

```cpp
// 检查 Item 类型
if (Item->IsA<UStaticMeshComponent>())
{
    UStaticMeshComponent* Comp = Item->Get<UStaticMeshComponent>(0);
}

// 获取所有值为特定类型的数组
TArray<UObject*> Objects = Item->GetAsArray<UObject>();

// 支持三种 Item 类型：
// - FOperatorStackEditorObjectItem   : UObject 包装
// - FOperatorStackEditorStructItem   : UStruct / FStructOnScope 包装
// - FOperatorStackEditorPrimitiveItem: POD 类型（int, float, bool 等）
// - FOperatorStackEditorGroupItem    : 同类型 Item 的聚合
```

### Header Builder 用法

Header Builder 使用链式调用模式声明 UI：

```cpp
void UMyCustomization::CustomizeItemHeader(
    const FOperatorStackEditorItemPtr& InItem,
    const FOperatorStackEditorTree& InItemTree,
    FOperatorStackEditorHeaderBuilder& InHeaderBuilder)
{
    InHeaderBuilder
        .SetIcon(FAppStyle::GetBrush("ClassIcon.Actor"))
        .SetLabel(FText::FromString(TEXT("My Actor")))
        .SetTooltip(FText::FromString(TEXT("Tooltip text")))
        .SetExpandable(true)
        .SetStartsExpanded(true)
        .SetSearchAllowed(true)
        .SetSearchKeywords({TEXT("actor"), TEXT("mesh")})
        .SetDraggable(true)
        .SetContextMenu(TEXT("MyContextMenu"))
        .SetProperty(SomeBoolProperty)  // 在 Header 中显示一个属性（如 checkbox）
        .SetToolbarMenu(TEXT("MyToolbarActions"))
        .SetBorderColor(FLinearColor::Green)
        .SetMessageBox(EOperatorStackEditorMessageType::Warning,
                       FText::FromString(TEXT("Missing reference!")));
}
```

### Body Builder 用法

Body Builder 控制 Item 展开后显示的内容：

```cpp
void UMyCustomization::CustomizeItemBody(
    const FOperatorStackEditorItemPtr& InItem,
    const FOperatorStackEditorTree& InItemTree,
    FOperatorStackEditorBodyBuilder& InBodyBuilder)
{
    // 方式 1: 显示 Details View
    InBodyBuilder
        .SetShowDetailsView(true)
        .DisallowProperty(SomeProperty)        // 隐藏特定属性
        .DisallowCategory(TEXT("Hidden"))       // 隐藏特定分类
        .AllowProperty(ImportantProperty)       // 只显示特定属性
        .ExpandProperty(ExpandedProperty)       // 默认展开
        .CollapseProperty(CollapsedProperty);   // 默认折叠

    // 方式 2: 使用自定义 Widget 替代 Details View
    InBodyBuilder.SetCustomWidget(
        SNew(STextBlock).Text(FText::FromString(TEXT("Custom content")))
    );

    // 方式 3: 空 Body 时的提示文本
    InBodyBuilder.SetEmptyBodyText(
        FText::FromString(TEXT("No items to display"))
    );
}
```

### Subsystem API

通过 `UOperatorStackEditorSubsystem` 可以在运行时操作 Stack：

```cpp
UOperatorStackEditorSubsystem* Subsystem = UOperatorStackEditorSubsystem::Get();

// 动态注册/注销 Customization
Subsystem->RegisterStackCustomization(UMyCustomization::StaticClass());
Subsystem->UnregisterStackCustomization(UMyCustomization::StaticClass());

// 生成独立的 Widget（用于嵌入其他面板）
TSharedRef<SOperatorStackEditorWidget> Widget = Subsystem->GenerateWidget();

// 遍历所有已注册 Customization
Subsystem->ForEachCustomization([](UOperatorStackEditorStackCustomization* InCustomization)
{
    UE_LOG(LogTemp, Log, TEXT("Customization: %s"), *InCustomization->GetIdentifier().ToString());
    return true; // 返回 false 停止遍历
});

// 刷新特定 Context 的 Widget
Subsystem->RefreshCustomizationWidget(MyContext, /*bForce=*/false);

// 聚焦特定 Customization
Subsystem->FocusCustomizationWidget(MyContext, TEXT("MyCustomization"));
```

### Widget 嵌入用法

`SOperatorStackEditorWidget` 是对外暴露的主 Widget，可以嵌入任何 Slate 容器：

```cpp
TSharedRef<SOperatorStackEditorWidget> Widget = Subsystem->GenerateWidget();

// 设置 Context（决定显示哪些数据）
FOperatorStackEditorContext Context(TArray<FOperatorStackEditorItemPtr>{
    MakeShared<FOperatorStackEditorObjectItem>(MyActor)
});
Widget->SetContext(Context);

// 控制工具栏
Widget->SetToolbarVisibility(true);
Widget->SetActiveCustomization(TEXT("MyCustomization"));
Widget->SetToolbarCustomizations({TEXT("Custom1"), TEXT("Custom2")});

// 设置 Detail View 相关
Widget->SetKeyframeHandler(MyKeyframeHandler);
Widget->SetDetailColumnSize(MyColumnSize);
Widget->SetPanelTag(TEXT("MyPanel"));
```

### 拖放支持

Customization 可以通过重写拖放相关虚函数支持拖放：

```cpp
virtual bool OnIsItemDraggable(const FOperatorStackEditorItemPtr& InItem) override
{
    return true; // 允许拖动
}

virtual TOptional<EItemDropZone> OnItemCanAcceptDrop(
    const TArray<FOperatorStackEditorItemPtr>& InDraggedItems,
    const FOperatorStackEditorItemPtr& InTargetItem,
    EItemDropZone InTargetZone) override
{
    // 返回有效的 DropZone 表示接受放置
    return EItemDropZone::OntoItem;
}

virtual void OnDropItem(
    const TArray<FOperatorStackEditorItemPtr>& InDraggedItems,
    const FOperatorStackEditorItemPtr& InTargetItem,
    EItemDropZone InTargetZone) override
{
    // 处理放置逻辑
}
```

### 右键菜单

通过 `UOperatorStackEditorMenuContext` 向 ToolMenu 系统传递上下文：

```cpp
// 在 Header Builder 中设置菜单名
InHeaderBuilder.SetContextMenu(TEXT("MyItemContextMenu"));

// 注册菜单（通常在模块 Startup 中）
UToolMenus::RegisterMenu(
    TEXT("MyItemContextMenu"),
    TEXT("MyItemContextMenu"),
    EToolMenuInsertType::Default
);

// 菜单回调中获取 Context
void UMyModule::FillContextMenu(UToolMenu* InToolMenu)
{
    UOperatorStackEditorMenuContext* MenuContext =
        InToolMenu->FindContext<UOperatorStackEditorMenuContext>();
    if (MenuContext)
    {
        FOperatorStackEditorItemPtr Item = MenuContext->GetItem();
        // 根据 Item 添加菜单项...
    }
}
```

## Demo 示例

以下是一个最小的 Customization 实现，展示如何创建一个显示 UObject 树的 Stack：

### MyStackCustomization.h

```cpp
#pragma once

#include "Customizations/OperatorStackEditorStackCustomization.h"
#include "MyStackCustomization.generated.h"

UCLASS()
class UMyStackCustomization : public UOperatorStackEditorStackCustomization
{
    GENERATED_BODY()

public:
    UMyStackCustomization()
        : UOperatorStackEditorStackCustomization(
            TEXT("MyStack"),
            NSLOCTEXT("MyStack", "Label", "My Objects"),
            100)
    {
        RegisterCustomizationFor(UObject::StaticClass());
    }

    virtual bool GetRootItem(
        const FOperatorStackEditorContext& InContext,
        FOperatorStackEditorItemPtr& OutRootItem) const override
    {
        // 从 Context 的第一个 Item 取出 UObject 作为根
        if (!InContext.GetItems().IsEmpty())
        {
            OutRootItem = InContext.GetItems()[0];
            return OutRootItem.IsValid() && OutRootItem->HasValue();
        }
        return false;
    }

    virtual bool GetChildrenItem(
        const FOperatorStackEditorItemPtr& InItem,
        TArray<FOperatorStackEditorItemPtr>& OutChildrenItems) const override
    {
        // 没有子节点
        return false;
    }

    virtual void CustomizeItemHeader(
        const FOperatorStackEditorItemPtr& InItem,
        const FOperatorStackEditorTree& InItemTree,
        FOperatorStackEditorHeaderBuilder& InHeaderBuilder) override
    {
        if (UObject* Obj = InItem->Get<UObject>(0))
        {
            InHeaderBuilder
                .SetLabel(FText::FromString(Obj->GetName()))
                .SetIcon(FSlateIconFinder::FindIconBrushForClass(Obj->GetClass()))
                .SetExpandable(true)
                .SetSearchAllowed(true)
                .SetSearchKeywords({Obj->GetName()});
        }
    }

    virtual void CustomizeItemBody(
        const FOperatorStackEditorItemPtr& InItem,
        const FOperatorStackEditorTree& InItemTree,
        FOperatorStackEditorBodyBuilder& InBodyBuilder) override
    {
        InBodyBuilder.SetShowDetailsView(true);
    }
};
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject"
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "OperatorStackEditor",  // 核心依赖
    "Slate",
    "SlateCore",
    "ToolMenus"             // 如果需要右键菜单
});
```

## 模块依赖

从 `OperatorStackEditor.Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型和容器 |
| `CoreUObject` | UObject 反射系统 |
| `ApplicationCore` | 应用层基础 |
| `CustomDetailsView` | Details View 自定义渲染（Body Builder 依赖） |
| `EditorSubsystem` | EditorSubsystem 基类 |
| `Engine` | 引擎核心 |
| `InputCore` | 输入处理 |
| `LevelEditor` | 关联 Level Editor Tab |
| `Projects` | 插件项目管理 |
| `PropertyEditor` | 属性编辑器集成 |
| `Slate` / `SlateCore` | UI 框架 |
| `ToolMenus` | 菜单系统（右键菜单、工具栏） |
| `ToolWidgets` | 工具控件 |
| `TypedElementRuntime` | 类型化元素运行时 |
| `UnrealEd` | 编辑器核心 |
| `WorkspaceMenuStructure` | 工作区菜单结构 |

## 维护状态

### 近期更新

```
4bdf8200129b | 2025-09-23 | MotionDesign : OperatorStack - Fixed multiple selection change event causes tab to be invoked when it should not be
→ 修复了多选事件导致 Tab 被错误调用的 bug

df329aa21f92 | 2025-09-23 | Motion Design: removed beta tag from motion design plugins.
→ Motion Design 插件（Operator Stack 的主要消费者）移除了 beta 标记

ce6ff392ddca | 2025-09-12 | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue for FTSTicker::RemoveTicker usage.
→ 修复 nodiscard 编译警告
```

### 维护评价

- **创建时间**：2025-05-08，约 1 年历史，是一个较新的插件
- **维护状态**：活跃维护中，最近更新在 2025 年 9 月
- **定位**：作为 Motion Design 和 PropertyAnimatorCore 的基础设施，跟随 VP 工具链一起演进
- **代码质量**：架构清晰，使用模板方法模式和 Builder 模式，扩展性好
- **API 稳定性**：目前仍在快速迭代中，API 可能有变动
- **推荐使用**：如果你在开发 Virtual Production 相关编辑器工具，推荐使用此框架；对于一般游戏开发，不太会直接用到

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/OperatorStack)
- 无官方文档（.uplugin 中 DocsURL 为空）
- 主要消费者: [PropertyAnimatorCore](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/VirtualProduction/PropertyAnimatorCore)（展示了如何继承和使用 OperatorStack）
