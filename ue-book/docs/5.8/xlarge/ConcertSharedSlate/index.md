# Concert Shared Slate

> Contains UI that is shared for server and client UI modules

| 属性 | 值 |
|---|---|
| 中文名 | Concert 共享 Slate UI |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertSharedSlate` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-02-11 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate) | |

## 用途

ConcertSharedSlate 是 Unreal Engine **多用户编辑（Multi-User Editing）** 系统的共享 UI 组件库。它从原来的 ConcertSyncClient 插件中拆分出来，提取了服务端和客户端 UI 共用的 Slate 控件。

这个插件解决的核心问题是：多用户编辑系统的 UI 组件（会话浏览器、活动列表、复制流编辑器等）在服务端程序（UnrealMultiUserServer）和客户端 UI 中都需要使用，因此需要一个共享层来避免代码重复。它提供了完整的会话管理 UI、活动历史查看、会话恢复界面，以及属性复制流的可视化编辑框架。

**使用限制**：此插件仅在以下特定程序中加载：`UnrealMultiUserServer`、`UnrealMultiUserSlateServer`、`UnrealRecoverySvc`、`CrashReportClientEditor`，不适用于通用游戏项目。

## 使用场景

- 你在开发 Unreal 的**多用户协作服务端程序** → 用此插件提供会话浏览、活动监控等 UI
- 你在实现**会话恢复（Session Recovery）** 功能 → 用此插件的 `SConcertSessionRecovery` 提供恢复界面
- 你需要在编辑器中**可视化编辑复制流（Replication Stream）** → 用此插件的复制流编辑器框架
- 你需要构建**会话活动历史**展示界面 → 用此插件的 `SConcertSessionActivities` / `SSessionHistory`

## 蓝图用法

此插件为纯 C++ Slate UI 库，不包含蓝图可调用节点。所有 API 均为 C++ 接口。

## C++ 用法

### 核心组件概览

本插件主要包含以下功能模块：

| 模块 | 核心类 | 用途 |
|---|---|---|
| 会话浏览器 | `SConcertSessionBrowser` | 浏览、搜索、创建、归档、恢复会话 |
| 会话活动列表 | `SConcertSessionActivities` | 展示会话活动（连接、锁定、包操作、事务等） |
| 会话恢复 | `SConcertSessionRecovery` | 恢复界面，让用户选择要恢复的活动 |
| 会话历史 | `SSessionHistory` | 带搜索和过滤的会话活动历史包装器 |
| 可编辑历史 | `SEditableSessionHistory` | 支持删除/静音操作的活动历史 |
| 复制流模型 | `IReplicationStreamModel` / `IEditableReplicationStreamModel` | 属性复制流的数据模型 |
| 复制流编辑器 | `IReplicationStreamEditor` / `IMultiReplicationStreamEditor` | 复制流的 UI 编辑器 |
| 项目选择源 | `IItemSourceModel` / `FSourceModelBuilders` | 通用的可选项数据源与 UI 构建器 |
| 客户端显示 | `SClientName` / `SHorizontalClientList` | 客户端名称和列表显示 |
| 对象层级 | `IObjectHierarchyModel` | 确定对象间的父子关系 |

### 头文件引入

```cpp
#include "IConcertSharedSlateModule.h"
#include "Session/Browser/SConcertSessionBrowser.h"
#include "Session/Activity/SConcertSessionActivities.h"
#include "Session/History/SSessionHistory.h"
#include "SConcertSessionRecovery.h"
#include "Replication/ReplicationWidgetFactories.h"
#include "Replication/Editor/Model/IReplicationStreamModel.h"
#include "Replication/Editor/Model/IEditableReplicationStreamModel.h"
#include "ConcertFrontendUtils.h"
```

### 基本用法 — 创建只读复制流模型

从 `ReplicationWidgetFactories.h` 提取的工厂函数：

```cpp
#include "Replication/ReplicationWidgetFactories.h"
#include "ConcertSyncSessionDatabase.h" // for FConcertObjectReplicationMap

// 创建一个只读的复制流模型，绑定到属性
TAttribute<const FConcertObjectReplicationMap*> ReplicationMapAttr;
ReplicationMapAttr.BindLambda([this]() -> const FConcertObjectReplicationMap*
{
    return &MyReplicationMap;
});

TSharedRef<UE::ConcertSharedSlate::IReplicationStreamModel> ReadOnlyModel =
    UE::ConcertSharedSlate::CreateReadOnlyStreamModel(ReplicationMapAttr);
```

### 基本用法 — 创建可编辑复制流模型

```cpp
// 创建一个可编辑的复制流模型
TAttribute<FConcertObjectReplicationMap*> EditableMapAttr;
EditableMapAttr.BindLambda([this]() -> FConcertObjectReplicationMap*
{
    return &MyEditableReplicationMap;
});

TSharedRef<UE::ConcertSharedSlate::IEditableReplicationStreamModel> EditableModel =
    UE::ConcertSharedSlate::CreateBaseStreamModel(EditableMapAttr);
```

### 基本用法 — 创建会话活动列表

从 `SConcertSessionActivities.h` 提取的用法：

```cpp
#include "Session/Activity/SConcertSessionActivities.h"

// 创建活动视图
TSharedRef<SConcertSessionActivities> ActivityView = SNew(SConcertSessionActivities)
    .OnFetchActivities_Lambda([this](TArray<TSharedPtr<FConcertSessionActivity>>& InOutActivities, int32& OutFetchedCount, FText& ErrorMsg) -> bool
    {
        // 从服务器获取活动数据
        OutFetchedCount = FetchMoreActivities(InOutActivities);
        return true;
    })
    .OnMapActivityToClient_Lambda([this](FGuid ClientId) -> TOptional<FConcertClientInfo>
    {
        return GetClientInfo(ClientId);
    })
    .ConnectionActivitiesVisibility(EVisibility::Hidden)
    .LockActivitiesVisibility(EVisibility::Hidden)
    .PackageActivitiesVisibility(EVisibility::Visible)
    .TransactionActivitiesVisibility(EVisibility::Visible);

// 追加新活动
ActivityView->Append(MakeShared<FConcertSessionActivity>(NewActivity));
```

### 进阶用法 — 创建复制流编辑器

从 `ReplicationWidgetFactories.h` 提取的完整编辑器创建流程：

```cpp
// 1. 准备模型
TSharedRef<UE::ConcertSharedSlate::IEditableReplicationStreamModel> StreamModel =
    UE::ConcertSharedSlate::CreateBaseStreamModel(ReplicationMapAttribute);

// 2. 准备对象源（确定哪些对象可以添加）
TSharedRef<UE::ConcertSharedSlate::IObjectSelectionSourceModel> ObjectSource =
    CreateMyObjectSelectionSource();

// 3. 准备属性源（确定哪些属性可选）
TSharedRef<UE::ConcertSharedSlate::IPropertySourceProcessor> PropertySource =
    CreateMyPropertySource();

// 4. 构建编辑器参数
UE::ConcertSharedSlate::FCreateEditorParams EditorParams;
EditorParams.DataModel = StreamModel;
EditorParams.ObjectSource = ObjectSource;
EditorParams.PropertySource = PropertySource;
EditorParams.IsEditingEnabled = true;

// 5. 构建查看器参数
UE::ConcertSharedSlate::FCreateViewerParams ViewerParams;
// PropertyAssignmentView 默认使用 CreatePerObjectAssignmentView()

// 6. 创建编辑器
TSharedRef<UE::ConcertSharedSlate::IReplicationStreamEditor> Editor =
    UE::ConcertSharedSlate::CreateBaseStreamEditor(EditorParams, ViewerParams);

// 获取编辑器的 widget 并添加到你的 UI 中
TSharedRef<SWidget> EditorWidget = Editor->GetWidget();
```

### 进阶用法 — 会话恢复界面

从 `SConcertSessionRecovery.h` 提取：

```cpp
#include "SConcertSessionRecovery.h"

// 创建恢复界面
TSharedRef<SConcertSessionRecovery> RecoveryWidget = SNew(SConcertSessionRecovery)
    .IntroductionText(LOCTEXT("RecoveryIntro", "Select which activities to recover:"))
    .ParentWindow(MyWindow)
    .OnFetchActivities_Lambda(/* 获取活动数据 */)
    .OnMapActivityToClient_Lambda(/* 映射客户端信息 */)
    .OnRestore_Lambda([this](TSharedPtr<FConcertSessionActivity> Activity) -> bool
    {
        return RestoreActivity(Activity);
    })
    .OnCancel_Lambda([this]()
    {
        // 取消恢复操作
    })
    .WithClientAvatarColorColumn(true)
    .WithClientNameColumn(true)
    .WithOperationColumn(true)
    .WithPackageColumn(true)
    .AreRecoverAllAndCancelButtonsVisible(true);

// 获取用户选择的恢复点
TSharedPtr<FConcertSessionActivity> RecoverPoint = RecoveryWidget->GetRecoverThroughItem();
```

### 进阶用法 — 使用项目选择源模型

从 `IItemSourceModel.h` 和 `SourceModelBuilders.h` 提取的泛型项目选择系统：

```cpp
// 定义自定义项目源
class FActorSelectionSource : public UE::ConcertSharedSlate::IItemSourceModel<TSoftObjectPtr<AActor>>
{
public:
    virtual UE::ConcertSharedSlate::FSourceDisplayInfo GetDisplayInfo() const override
    {
        return {
            LOCTEXT("FromWorld", "From World"),
            LOCTEXT("FromWorldTip", "Add actors from the current world"),
            FSlateIcon(),
            UE::ConcertSharedSlate::ESourceType::ShowAsList
        };
    }

    virtual void EnumerateSelectableItems(
        TFunctionRef<EBreakBehavior(const TSoftObjectPtr<AActor>&)> Delegate) const override
    {
        UWorld* World = GEditor->GetEditorWorldContext().World();
        for (TActorIterator<AActor> It(World); It; ++It)
        {
            if (Delegate(TSoftObjectPtr<AActor>(*It)) == EBreakBehavior::Break)
                break;
        }
    }
};

// 构建选择 UI
UE::ConcertSharedSlate::FSourceModelBuilders<TSoftObjectPtr<AActor>>::FItemPickerArgs Args(
    FOnItemsSelected::CreateLambda([](TArray<TSoftObjectPtr<AActor>> Selected) { /* 处理选择 */ }),
    FGetItemDisplayString::CreateLambda([](const TSoftObjectPtr<AActor>& Item) -> FString
    {
        return Item.IsValid() ? Item->GetActorNameOrLabel() : Item.ToString();
    })
);

TSharedRef<SWidget> PickerWidget =
    UE::ConcertSharedSlate::FSourceModelBuilders<TSoftObjectPtr<AActor>>::MakeStandaloneWidget(
        MakeShared<FActorSelectionSource>(), Args, FSlateIcon());
```

## Demo 示例

### 最小示例：创建带搜索的属性树视图

```cpp
// MyPropertyTreeWidget.h
#pragma once

#include "CoreMinimal.h"
#include "Replication/PropertyTreeFactory.h"

class SMyPropertyTreeWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyPropertyTreeWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs)
    {
        // 创建带搜索功能的属性树视图
        UE::ConcertSharedSlate::FCreatePropertyTreeViewParams TreeParams;
        // 默认已包含 LabelColumn，可追加更多列
        TreeParams.PropertyColumns.Add(
            UE::ConcertSharedSlate::ReplicationColumns::Property::LabelColumn()
        );

        PropertyTreeView = UE::ConcertSharedSlate::CreateSearchablePropertyTreeView(TreeParams);

        ChildSlot
        [
            PropertyTreeView->GetWidget()
        ];
    }

    void RefreshProperties(const TSet<FConcertPropertyChain>& Properties, const FSoftClassPath& Class)
    {
        UE::ConcertSharedSlate::FPropertyAssignmentEntry Entry;
        Entry.PropertiesToDisplay = Properties;
        Entry.Class = Class;
        PropertyTreeView->RefreshPropertyData({Entry}, true);
    }

private:
    TSharedPtr<UE::ConcertSharedSlate::IPropertyTreeView> PropertyTreeView;
};
```

```cpp
// MyPropertyTreeWidget.cpp
#include "MyPropertyTreeWidget.h"
```

## 模块依赖

此插件依赖以下其他插件（在 .uplugin 中声明）：

| 模块 | 用途 |
|---|---|
| `ConcertMain` | Concert 核心框架，提供基础消息和同步协议 |
| `ConcertSyncCore` | Concert 同步核心，提供活动数据结构（FConcertSyncActivity 等） |

无特殊模块依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF |
| 2025-07-30 | `c87f7654` | Stopped TFunctionRefBase::CheckCallable being instantiated differently for different templates. | 修复 TFunctionRefBase::CheckCallable 在不同模板中实例化不一致的问题 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 为有对应 .gen.cpp 的源文件添加内联宏优化 |
| 2025-05-31 | `8396b185` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用 UnrealCodeFixup 更新头文件，确保 DLL 导出标记在方法和静态变量上 |

### 维护评价

- **年龄**：约 3 年（2022 年创建），属于较新的插件
- **更新频率**：近期（2025-2026）有持续的编译和基础设施修复更新，表明仍在维护
- **维护状态**：**维护中** — 最近 6 个月内有更新，但主要是编译修复和宏迁移，非功能性变更
- **实验性**：`.uplugin` 中 `IsBetaVersion=true`，且 `EnabledByDefault=false`，属于实验性质
- **推荐使用**：⚠️ 仅推荐在开发 Concert 相关工具时使用。这是多用户编辑系统的内部共享 UI 库，不适用于一般游戏项目开发。由于 `SupportedPrograms` 限制，此插件仅在特定编辑器程序中加载。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertUI/ConcertSharedSlate)
- [ConcertMain 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)
- [ConcertSyncCore 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertSyncCore)