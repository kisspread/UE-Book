# Concert Shared Slate

> Contains UI that is shared for server and client UI modules（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSharedSlate` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate) | |

## 用途

ConcertSharedSlate 是 Unreal Engine 多用户编辑（Concert）系统中的一个共享 UI 组件库。它并非一个独立运行的插件，而是为 Concert 的服务器端（如 UnrealMultiUserServer）和客户端 UI 模块提供了一套可复用的 Slate 控件、数据模型和接口。

**核心问题**：在多用户编辑场景中，服务器和客户端都需要展示会话列表、活动历史、复制流配置等相似的 UI。如果各自独立实现，会导致代码重复和维护困难。

**解决方案**：此插件将通用的 UI 逻辑和视图抽象出来，形成共享层。服务器和客户端 UI 模块可以基于这些共享接口和控件进行开发，确保 UI 行为的一致性，并减少重复代码。

## 使用场景

- **开发多用户编辑服务器 UI**：当你需要为 UnrealMultiUserServer 构建管理界面，用于查看活跃/归档会话、监控用户活动时。
- **构建客户端会话浏览器**：在编辑器或独立客户端中，需要一个标准化的界面来发现、加入或管理多用户会话。
- **实现复制流编辑器**：需要为对象和属性配置网络复制规则时，使用此插件提供的标准化编辑器控件和模型。
- **显示会话活动历史**：需要以表格形式展示会话中的操作记录（如资产保存、Actor修改），并支持撤销历史查看。

## 蓝图用法

此插件主要提供 C++ 接口和 Slate 控件，不包含 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其 UI 组件通过 C++ 代码在 Slate 层级中构建和使用。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertSharedSlateModule.h"
#include "ConcertFrontendStyle.h"
// 根据需要引入具体模块的头文件，例如：
#include "Session/Browser/SSessionHistory.h"
#include "Replication/Editor/View/IReplicationStreamEditor.h"
```

### 基本用法

**1. 初始化模块和样式**
在使用任何共享 UI 控件前，需要确保模块已加载并初始化样式。
```cpp
// 获取模块实例（通常在插件启动时自动完成）
IConcertSharedSlateModule& SharedSlateModule = IConcertSharedSlateModule::Get();

// 初始化 Concert 前端样式（通常在模块 StartupModule 中调用）
FConcertFrontendStyle::Initialize();
```

**2. 创建会话历史控件**
`SSessionHistory` 是显示会话活动列表的核心控件。
```cpp
// 假设你有一个会话历史控制器的实现
TSharedRef<FAbstractSessionHistoryController> HistoryController = ...;

// 创建会话历史控件
TSharedRef<SSessionHistory> SessionHistoryWidget = SNew(SSessionHistory)
    .Controller(HistoryController);

// 将控件添加到你的 Slate 布局中
MyContainer->AddSlot()
[
    SessionHistoryWidget
];
```
*来源：基于 `SSessionHistory.h` 和 `SSessionHistoryWrapper.h` 的接口设计。*

**3. 使用预定义的活动列**
`PredefinedActivityColumns.h` 提供了常用的活动列表列。
```cpp
#include "Session/Activity/PredefinedActivityColumns.h"

// 创建一个包含时间、客户端名和操作描述的列集合
TArray<FActivityColumn> Columns;
Columns.Add(UE::ConcertSharedSlate::ActivityColumn::DateTime());
Columns.Add(UE::ConcertSharedSlate::ActivityColumn::ClientName());
Columns.Add(UE::ConcertSharedSlate::ActivityColumn::Operation());
Columns.Add(UE::ConcertSharedSlate::ActivityColumn::Summary());

// 将这些列传递给 SConcertSessionActivities 控件进行配置
```

### 进阶用法

**1. 实现自定义复制流列**
通过实现 `IReplicationTreeColumn` 接口，可以为对象或属性树添加自定义列。
```cpp
#include "Replication/Editor/View/Column/IObjectTreeColumn.h"

class FMyCustomObjectColumn : public UE::ConcertSharedSlate::IObjectTreeColumn
{
public:
    virtual SHeaderRow::FColumn::FArguments CreateHeaderRowArgs() const override
    {
        return SHeaderRow::Column("MyColumnId")
            .DefaultLabel(NSLOCTEXT("MyColumn", "Label", "Custom Info"))
            .FillWidth(0.5f);
    }

    virtual TSharedRef<SWidget> GenerateColumnWidget(const FBuildArgs& InArgs) override
    {
        // InArgs.RowData 包含 FReplicatedObjectData，可用于获取对象路径等信息
        const FSoftObjectPath& ObjectPath = InArgs.RowData.GetObjectPath();
        return SNew(STextBlock).Text(FText::FromString(ObjectPath.GetAssetName()));
    }
};

// 注册列
TArray<UE::ConcertSharedSlate::FObjectColumnEntry> ColumnEntries;
ColumnEntries.Add({
    .CreateColumn = []() { return MakeShared<FMyCustomObjectColumn>(); },
    .ColumnId = "MyColumnId",
    .ColumnInfo = { .SortOrder = 100 }
});
```

**2. 扩展复制流模型**
使用 `IStreamExtender` 在对象被添加到复制流时，自动添加关联的子对象或属性。
```cpp
#include "Replication/Editor/Model/Extension/IStreamExtender.h"
#include "Replication/Editor/Model/Extension/IStreamExtensionContext.h"

class FActorComponentExtender : public UE::ConcertSharedSlate::IStreamExtender
{
public:
    virtual void ExtendStream(UObject& ExtendedObject, IStreamExtensionContext& Context) override
    {
        if (AActor* Actor = Cast<AActor>(&ExtendedObject))
        {
            // 当一个 Actor 被添加时，自动将其所有组件也添加到复制流
            TArray<UActorComponent*> Components;
            Actor->GetComponents(Components);
            for (UActorComponent* Comp : Components)
            {
                if (Comp && Comp->GetIsReplicated())
                {
                    Context.AddAdditionalObject(*Comp);
                }
            }
        }
    }
};
```

## Demo 示例

以下示例展示如何创建一个简单的会话浏览器窗口。

**SessionBrowserWindow.h**
```cpp
#pragma once

#include "Widgets/SCompoundWidget.h"

class FAbstractSessionHistoryController;

class SSessionBrowserWindow : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SSessionBrowserWindow) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<FAbstractSessionHistoryController> HistoryController;
};
```

**SessionBrowserWindow.cpp**
```cpp
#include "SessionBrowserWindow.h"
#include "Session/History/SSessionHistoryWrapper.h"
#include "Session/History/AbstractSessionHistoryController.h"
#include "ConcertFrontendStyle.h"

void SSessionBrowserWindow::Construct(const FArguments& InArgs)
{
    // 确保样式已初始化
    FConcertFrontendStyle::Initialize();

    // 创建一个具体的会话历史控制器（此处为示意，实际需要根据你的数据源实现）
    HistoryController = MakeShared<FAbstractSessionHistoryController>(/* ... */);

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        .Padding(5.0f)
        [
            SNew(STextBlock)
            .Text(NSLOCTEXT("SessionBrowser", "Title", "Multi-User Session Browser"))
            .Font(FCoreStyle::GetDefaultFontStyle("Bold", 18))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            // 使用 SSessionHistoryWrapper 来管理控制器的生命周期
            SNew(SSessionHistoryWrapper, HistoryController.ToSharedRef())
        ]
    ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ConcertMain` | Concert 系统的核心模块，提供基础会话和连接管理。 |
| `ConcertSyncCore` | Concert 同步核心，提供事务、活动等数据结构和同步逻辑。 |

## 维护状态

### 近期更新

```
- c87f7654873f Stopped TFunctionRefBase::CheckCallable being instantiated differently for different templates. Deprecated member CheckCallable which was never intended to be public.
- a2e75189887d Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup using LyraEditor win64 development as target)
- 8396b185774c Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 2/n
```
*解读：最近的提交主要是代码清理和编译修复，包括模板实例化问题修复、添加内联生成宏以优化编译、以及调整 DLL 导出符号。*

### 维护评价

- **活跃维护**：插件创建于 2022 年，属于较新的模块。近期（2024年）仍有代码维护和优化提交。
- **实验性状态**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，表明它仍处于实验阶段，API 可能发生变化。
- **专用性**：此插件是 Concert 多用户编辑系统的内部 UI 组件，不面向通用游戏开发。其维护与 Concert 系统的整体开发紧密相关。
- **推荐使用**：**仅推荐**给正在开发或扩展 Unreal Engine 多用户编辑功能（如自定义服务器/客户端 UI）的开发者。对于普通游戏项目，无需关注此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate/Tests) (如果存在)