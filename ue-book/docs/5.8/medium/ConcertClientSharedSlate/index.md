# Concert Shared Slate

> Contains UI that is shared by client UI modules only（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 客户端共享Slate |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertClientSharedSlate` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-23 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertUI/ConcertClientSharedSlate) | |

## 用途

此插件是 Unreal Engine 多用户编辑（Concert）客户端 UI 架构的核心组成部分。其核心作用是提供一组**可复用的、与具体客户端会话逻辑解耦的 Slate UI 组件、工厂函数和数据模型接口**，供各个具体的客户端 UI 模块（如 `ConcertSyncClient`）使用。它解决了客户端 UI 开发中常见的重复代码和耦合问题，通过提供标准化的控件（如可筛选的属性树、客户端信息显示）、编辑器交互逻辑（如拖放、撤销/重做支持）以及数据绑定工具，极大地简化了构建复杂多用户编辑界面的工作。

## 使用场景

-   **开发或扩展 Concert 多用户编辑客户端**：当您需要为自定义工具或扩展功能（如资产同步、特定属性同步）创建用户界面时，应优先使用此插件提供的组件来构建一致的用户体验。
-   **需要构建包含属性树、对象选择器和拖放操作的复杂编辑器 UI**：此插件封装了这些复杂控件的常见实现模式，避免了从头开发。

## 蓝图用法

此插件主要为 C++ 框架，旨在为上层 UI 模块提供底层支持。其公共接口中**没有直接暴露可供蓝图使用的 UFUNCTION 或 UPROPERTY**。主要 API 均通过 C++ 函数和类提供。蓝图在 Concert 客户端 UI 中的使用，通常是上层插件利用此插件的底层组件来构建 Slate Widget 后，再通过其他方式暴露给蓝图。

## C++ 用法

### 头文件引入

根据您要使用的具体功能，引入对应的头文件。

```cpp
// 属性树与模型
#include "Replication/ClientReplicationWidgetFactories.h"
#include "Replication/Editor/Model/PropertyUtils.h"
#include "Replication/Settings/ConcertStreamObjectAutoBindingRules.h"

// 客户端信息与工具
#include "Widgets/Client/ClientInfoHelpers.h"
#include "ConcertClientFrontendUtils.h"
#include "Replication/ObjectNameUtils.h"

// 编辑器交互逻辑
#include "Replication/Editor/UnrealEditor/ModifyObjectInLevelHandler.h"
#include "Replication/Editor/UnrealEditor/HideObjectsNotInWorldLogic.h"
```

### 基本用法：创建一个可筛选的属性树视图

以下示例展示了如何使用工厂函数创建一个具备筛选功能的属性树视图，并将其添加到 Slate 布局中。（来源：`ClientReplicationWidgetFactories.h`）

```cpp
// 创建参数
UE::ConcertClientSharedSlate::FFilterablePropertyTreeViewParams TreeViewParams;
// 可以自定义列和排序
// TreeViewParams.AdditionalPropertyColumns = ...;
// TreeViewParams.PrimaryPropertySort = ...;

// 使用工厂函数创建视图
TSharedRef<ConcertSharedSlate::IPropertyTreeView> PropertyTreeView =
    UE::ConcertClientSharedSlate::CreateFilterablePropertyTreeView(TreeViewParams);

// 将视图的 Widget 添加到您的 Slate 布局中
MyContainer->AddSlot()
[
    PropertyTreeView->GetWidget()
];

// 之后，您需要将属性数据“灌入”这个视图
TArray<ConcertSharedSlate::FPropertyAssignmentEntry> MyPropertyEntries;
// ... 填充 MyPropertyEntries ...
PropertyTreeView->RefreshPropertyData(MyPropertyEntries, false);
```

### 进阶用法：使用事务性流模型并响应编辑器操作

此示例组合了多个功能：创建一个支持撤销/重做的复制流模型，并监听编辑器内对象的增删操作来更新模型。

```cpp
#include "Replication/Editor/Model/Extension/StreamExtenderBySettings.h"
#include "Replication/Editor/UnrealEditor/ModifyObjectInLevelHandler.h"

// 1. 创建基础模型（通常由上层提供，这里假设我们有一个）
TSharedRef<ConcertSharedSlate::IEditableReplicationStreamModel> BaseModel = ...;

// 2. 包装成事务性模型，使其支持编辑器撤销/重做
// 如果绑定到特定的 UObject，使用带参数的重载；否则使用无参版本自动创建内部对象。
TSharedRef<ConcertSharedSlate::IEditableReplicationStreamModel> TransactionalModel =
    UE::ConcertClientSharedSlate::CreateTransactionalStreamModel(BaseModel, *MyOwningObject);

// 3. 创建一个对象层级模型（用于显示组件等子对象）
TSharedRef<ConcertSharedSlate::IObjectHierarchyModel> HierarchyModel =
    UE::ConcertClientSharedSlate::CreateObjectHierarchyForComponentHierarchy();

// 4. 创建一个流扩展器，根据配置自动添加相关对象和属性
// FConcertStreamObjectAutoBindingRules 可以从设置中加载
FConcertStreamObjectAutoBindingRules AutoBindingRules = ...;
TSharedRef<ConcertSharedSlate::IStreamExtender> Extender =
    MakeShared<UE::ConcertClientSharedSlate::FStreamExtenderBySettings>(
        TAttribute<const FConcertStreamObjectAutoBindingRules*>::Create(
            [&AutoBindingRules]() { return &AutoBindingRules; }
        )
    );

// 5. 创建一个处理器，响应编辑器中 Actor 的删除和对象的添加/移除
auto ModifyHandler = MakeUnique<UE::ConcertClientSharedSlate::FModifyObjectInLevelHandler>(*TransactionalModel);
ModifyHandler->OnHierarchyNeedsRefresh().AddLambda([HierarchyModel, TransactionalModel]()
{
    // 当层级可能改变时（例如组件被添加或删除），刷新对象树视图的数据
    // HierachyModel 会被用来构建新的对象列表
    TransactionalModel->... // 可能需要根据新的层级更新模型
});

// 6. 现在，TransactionalModel, HierarchyModel, Extender 可以被传递给更上层的、
//    具体的复制流编辑器 Widget（如 SReplicationStreamEditor）来使用。
```

## Demo 示例

以下是一个最小的、可编译的示例，演示如何创建一个带有拖放支持的复制对象列表面板。

**ClientDemoPanel.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"
#include "Replication/ClientReplicationWidgetDelegates.h"

class SClientDemoPanel : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SClientDemoPanel) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    // 拖放处理函数
    FReply OnHandleDroppedObjects(TConstArrayView<UObject*> DroppedObjects);
    bool OnCanDropObject(UObject& Object);

    // UI 容器
    TSharedPtr<SVerticalBox> ContentBox;
};
```

**ClientDemoPanel.cpp**
```cpp
#include "ClientDemoPanel.h"
#include "Replication/ClientReplicationWidgetFactories.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Text/STextBlock.h"
#include "Widgets/Input/SButton.h"

void SClientDemoPanel::Construct(const FArguments& InArgs)
{
    // 1. 创建拖放包装器的委托
    UE::ConcertClientSharedSlate::FCreateDropTargetOutlinerWrapperParams WrapperParams;
    WrapperParams.HandleDroppedObjectsDelegate.BindRaw(this, &SClientDemoPanel::OnHandleDroppedObjects);
    WrapperParams.CanDropObjectDelegate.BindRaw(this, &SClientDemoPanel::OnCanDropObject);

    // 2. 通过工厂函数获取拖放包装逻辑
    ConcertSharedSlate::FWrapOutlinerWidget DropWrapper =
        UE::ConcertClientSharedSlate::CreateDropTargetOutlinerWrapper(WrapperParams);

    // 3. 构建原始内容（这里用一个简单的按钮作为示例）
    TSharedRef<SWidget> OriginalContent = SNew(SButton)
        .Text(FText::FromString(TEXT("拖放对象到此处")))
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center);

    // 4. 使用包装器包装原始内容
    TSharedRef<SWidget> WrappedContent = DropWrapper.Execute(OriginalContent);

    // 5. 组装最终 UI
    ChildSlot
    [
        SNew(SBox)
        .MinDesiredWidth(300.f)
        .MinDesiredHeight(200.f)
        [
            WrappedContent
        ]
    ];
}

FReply SClientDemoPanel::OnHandleDroppedObjects(TConstArrayView<UObject*> DroppedObjects)
{
    for (UObject* Obj : DroppedObjects)
    {
        UE_LOG(LogTemp, Log, TEXT("Object dropped: %s"), *Obj->GetName());
        // 在此处处理被拖入的对象，例如将其添加到复制流
    }
    return FReply::Handled();
}

bool SClientDemoPanel::OnCanDropObject(UObject& Object)
{
    // 定义哪些类型的对象可以被拖入
    return Object.IsA<AActor>();
}
```

## 模块依赖

从插件的 `.uplugin` 文件和其自身性质推断，要使用此插件的功能，您的模块通常需要依赖以下插件/模块：

| 模块 | 用途 |
|---|---|
| `ConcertSharedSlate` | 提供了此插件所实现接口的基类（如 `IPropertyTreeView`, `IEditableReplicationStreamModel`）和通用 Slate 组件。**核心依赖**。 |
| `ConcertSyncCore` | 提供了核心的复制数据结构（如 `FConcertPropertyChain`, `FConcertObjectReplicationMap`）和同步逻辑。**核心依赖**。 |
| `ConcertMain` | 提供了基础的会话和消息数据结构（如 `FConcertClientInfo`）。**基础依赖**。 |
| `ConcertSyncClient` | 此插件的**主要使用者**，提供了具体的客户端会话管理和 UI。您的代码如果直接与会话交互，需要依赖它。 |

*注：Core, CoreUObject, Engine, Slate, SlateCore, UnrealEd, EditorStyle 等标准模块依赖已被省略。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF 格式。 |
| 2026-04-02 | `50a24ff6` | Deprecated GetObjects*/ForEachObjectWithOuter functions that take bool bIncludeNestedObjects. Introd... | 废弃了部分包含 `bIncludeNestedObjects` 参数的对象枚举函数，并引入了新的 API。 |
| 2026-01-23 | `d793b083` | [Core] Enable range-based for loop support for `TFilterCollection`. | （底层核心改动）为 TFilterCollection 启用基于范围的 for 循环支持。 |
| 2025-06-18 | `c61e4278` | Various fixes to make unreal editor compile with IWYU | 修复了使编辑器能在 IWYU 模式下编译的多种问题。 |
| 2025-05-20 | `b668eee0` | Fixing issue where a USTRUCT inherits from more than one USTRCT. This isn't allowed but wasn't bein... | 修复了一个 USTRUCT 从多个 USTRUCT 继承的非法情况。 |

### 维护评价

-   **状态**：**维护中**。
-   **分析**：插件创建于 2022 年 2 月，最近一次提交在 2026 年 4 月。近期提交集中在**代码现代化、API 清理和编译修复**上，而非新功能开发。这表明该插件功能已趋于稳定，团队在积极维护其代码健康度和兼容性。
-   **建议**：**可以使用**。该插件是 Concert 客户端 UI 架构中经过验证的底层基础组件。尽管被标记为实验性（`IsBetaVersion`）且未默认启用，但其代码质量和近期维护活动表明它是可靠且持续维护的。对于需要自定义 Concert 客户端 UI 的开发者而言，这是推荐使用的基础设施。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertUI/ConcertClientSharedSlate)
-   [官方文档]()（无公开文档链接）
-   [测试用例]()（源码分析中未提供测试文件路径）