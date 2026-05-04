# StateTree

> General purpose hierarchical state machine（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器资源） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是 Unreal Engine 的**通用层级状态机（Hierarchical State Machine）**插件，用于构建复杂的游戏逻辑和 AI 行为。与传统的行为树（Behavior Tree）不同，StateTree 采用**状态驱动**的架构，支持：

- **层级状态嵌套**：状态可以包含子状态，形成树状结构
- **状态转换（Transition）**：基于条件的状态切换，支持选择行为（Selection Behavior）
- **状态类型分类**：通过 `EStateTreeStateType` 区分不同状态类型（如 State、Group、Linked 等）
- **内置调试器**：通过 `WITH_STATETREE_TRACE_DEBUGGER` 宏启用的运行时追踪和调试功能，支持帧事件查看、活跃状态可视化
- **紧凑树视图**：`SCompactTreeView` 提供状态树的可视化展示，支持搜索、选择和自定义数据扩展

StateTree 的设计目标是替代或补充行为树，提供更直观的状态管理方式，特别适合需要明确状态定义和转换逻辑的场景（如 AI、游戏流程、UI 状态管理等）。

## 使用场景

- 你需要为 AI 角色构建复杂的行为逻辑，且行为更偏向"状态切换"而非"任务执行" → 用 StateTree
- 你需要管理游戏流程（如菜单 → 加载 → 游戏 → 暂停）的层级状态 → 用 StateTree
- 你需要一个可视化编辑器来设计状态机，且支持运行时调试追踪 → 用 StateTree
- 你需要在状态机中嵌入自定义数据并通过紧凑树视图展示 → 用 StateTree 的 `FStateItemCustomData` 扩展机制

## 蓝图用法

> ⚠️ 由于本次仅提供了 StateTreeDeveloper 模块的源码，核心运行时模块（StateTreeModule）和编辑器模块（StateTreeEditorModule）的蓝图 API 未在本次分析范围内。以下为从 Developer 模块中可提取的有限信息。

### 核心节点

StateTreeDeveloper 模块主要提供编辑器/调试器 UI 组件，不直接暴露蓝图节点。核心蓝图 API 位于 `StateTreeModule` 和 `StateTreeEditorModule` 中。

### 调试器相关（C++ 层面）

| 组件 | 说明 | 所在类 |
|---|---|---|
| `SCompactTreeDebuggerView` | 紧凑树调试视图，显示活跃状态 | `UE::StateTree::SCompactTreeDebuggerView` |
| `SFrameEventsView` | 帧事件查看器，显示某帧的所有追踪事件 | `UE::StateTreeDebugger::SFrameEventsView` |

## C++ 用法

### 头文件引入

```cpp
// 开发者/调试器模块
#include "StateTreeStyle.h"
#include "Widgets/SCompactTreeView.h"

// 调试器视图（需要 WITH_STATETREE_TRACE_DEBUGGER）
#include "Debugger/SCompactTreeDebuggerView.h"
#include "Debugger/SStateTreeFrameEventsView.h"
```

### 基本用法：使用紧凑树视图

紧凑树视图（`SCompactTreeView`）是 StateTree 状态的可视化展示组件，支持搜索、选择和自定义扩展。

```cpp
// 来源: Engine/Plugins/Runtime/StateTree/Source/StateTreeDeveloper/Internal/Widgets/SCompactTreeView.h

// 创建紧凑树视图
TSharedRef<UE::StateTree::SCompactTreeView> TreeView =
    SNew(UE::StateTree::SCompactTreeView)
    .TextStyle(&FCoreStyle::Get().GetWidgetStyle<FTextBlockStyle>("NormalText"))
    .SelectionMode(ESelectionMode::Single)
    .OnSelectionChanged_Lambda([](TConstArrayView<FGuid> SelectedStateIDs)
    {
        // 处理状态选择变更
        for (const FGuid& StateID : SelectedStateIDs)
        {
            UE_LOG(LogTemp, Log, TEXT("Selected State: %s"), *StateID.ToString());
        }
    })
    .OnContextMenuOpening_Lambda([]() -> TSharedPtr<SWidget>
    {
        // 返回右键菜单
        return nullptr;
    });

// 传入 StateTree 资产进行构建
TreeView->Construct(TreeView->GetArgs(), StateTreeAsset);

// 设置/获取选择
TArray<FGuid> CurrentSelection = TreeView->GetSelection();
TreeView->SetSelection({SomeStateGuid});

// 刷新视图
TreeView->Refresh();
```

### 进阶用法：自定义紧凑树视图数据

通过继承 `SCompactTreeView` 并重写虚函数，可以扩展状态项的自定义数据。

```cpp
// 来源: Engine/Plugins/Runtime/StateTree/Source/StateTreeDeveloper/Internal/Widgets/SCompactTreeView.h
// 来源: Engine/Plugins/Runtime/StateTree/Source/StateTreeDeveloper/Internal/Debugger/SCompactTreeDebuggerView.h

// 1. 定义自定义数据结构（必须是 USTRUCT）
USTRUCT()
struct FMyStateItemData : public UE::StateTree::CompactTreeView::FStateItemCustomData
{
    GENERATED_BODY()

    FMyStateItemData() = default;
    explicit FMyStateItemData(const bool bInIsActive)
        : bIsActive(bInIsActive)
    {
    }

    bool bIsActive = false;
};

// 2. 继承 SCompactTreeView 并重写虚函数
class SMyCustomTreeView : public UE::StateTree::SCompactTreeView
{
protected:
    // 创建带自定义数据的状态项
    virtual TSharedRef<FStateItem> CreateStateItemInternal() const override
    {
        TSharedRef<FStateItem> Item = MakeShared<FStateItem>();
        Item->CustomData.InitializeAs<FMyStateItemData>();
        return Item;
    }

    // 缓存状态数据
    virtual void CacheStatesInternal() override
    {
        // 自定义状态缓存逻辑
    }

    // 创建自定义名称控件
    virtual TSharedRef<SWidget> CreateNameWidgetInternal(TSharedPtr<FStateItem> Item) const override
    {
        // 根据自定义数据创建不同的显示
        const FMyStateItemData* Data = Item->CustomData.GetPtr<FMyStateItemData>();
        if (Data && Data->bIsActive)
        {
            return SNew(STextBlock)
                .Text(Item->Desc)
                .ColorAndOpacity(FSlateColor(FLinearColor::Green));
        }
        return SNew(STextBlock).Text(Item->Desc);
    }
};
```

### 调试器用法：帧事件查看

```cpp
// 来源: Engine/Plugins/Runtime/StateTree/Source/StateTreeDeveloper/Internal/Debugger/SStateTreeFrameEventsView.h

#if WITH_STATETREE_TRACE_DEBUGGER

// 创建帧事件视图
TSharedRef<UE::StateTreeDebugger::SFrameEventsView> EventsView =
    SNew(UE::StateTreeDebugger::SFrameEventsView);

EventsView->Construct(EventsView->GetArgs(), StateTreeAsset);

// 根据 scrub 状态刷新事件显示
EventsView->RequestRefresh(ScrubState);

// 按谓词选择事件
EventsView->SelectByPredicate([](const FStateTreeTraceEventVariantType& Event) -> bool
{
    // 选择特定类型的事件
    return true;
});

#endif // WITH_STATETREE_TRACE_DEBUGGER
```

## Demo 示例

以下示例展示如何创建一个自定义的 StateTree 紧凑树视图，带调试数据高亮。

```cpp
// MyStateTreeDebugView.h
#pragma once

#include "Widgets/SCompactTreeView.h"

class SMyStateTreeDebugView : public UE::StateTree::SCompactTreeView
{
public:
    SLATE_BEGIN_ARGS(SMyStateTreeDebugView) {}
        SLATE_ATTRIBUTE(bool, ShowActiveStates)
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs, TNotNull<const UStateTree*> InStateTree);

protected:
    virtual TSharedRef<FStateItem> CreateStateItemInternal() const override;
    virtual void CacheStatesInternal() override;
    virtual TSharedRef<SWidget> CreateNameWidgetInternal(TSharedPtr<FStateItem> Item) const override;

private:
    TAttribute<bool> bShowActiveStates;
};
```

```cpp
// MyStateTreeDebugView.cpp
#include "MyStateTreeDebugView.h"

void SMyStateTreeDebugView::Construct(const FArguments& InArgs, TNotNull<const UStateTree*> InStateTree)
{
    bShowActiveStates = InArgs._ShowActiveStates;
    SCompactTreeView::Construct(SCompactTreeView::FArguments(), InStateTree);
}

TSharedRef<UE::StateTree::SCompactTreeView::FStateItem> SMyStateTreeDebugView::CreateStateItemInternal() const
{
    TSharedRef<FStateItem> Item = MakeShared<FStateItem>();
    Item->CustomData.InitializeAs<UE::StateTree::CompactTreeView::FStateItemDebuggerData>();
    return Item;
}

void SMyStateTreeDebugView::CacheStatesInternal()
{
    // 从 StateTree 资产缓存状态层级
    // 实际实现需要遍历 UStateTree 的状态数组
}

TSharedRef<SWidget> SMyStateTreeDebugView::CreateNameWidgetInternal(TSharedPtr<FStateItem> Item) const
{
    const auto* DebugData = Item->CustomData.GetPtr<UE::StateTree::CompactTreeView::FStateItemDebuggerData>();

    FSlateColor TextColor = FSlateColor(FLinearColor::White);
    if (DebugData && DebugData->bIsActive && bShowActiveStates.Get())
    {
        TextColor = FSlateColor(FLinearColor::Green);
    }

    return SNew(SHorizontalBox)
        + SHorizontalBox::Slot()
        .AutoWidth()
        [
            SNew(SImage)
            .Image(Item->Icon)
        ]
        + SHorizontalBox::Slot()
        .FillWidth(1.0f)
        .Padding(4.0f, 0.0f)
        [
            SNew(STextBlock)
            .Text(Item->Desc)
            .ToolTipText(Item->TooltipText)
            .ColorAndOpacity(TextColor)
        ];
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `StructUtils` | 提供 `TInstancedStruct` 等结构体工具，用于状态项自定义数据扩展 |
| `EditorFramework` | 编辑器框架支持（StateTreeTestSuite 依赖） |
| `UnrealEd` | 编辑器功能（StateTreeTestSuite 依赖） |

> 注：核心运行时模块（StateTreeModule）和编辑器模块（StateTreeEditorModule）的完整依赖列表未在本次分析范围内。StateTreeDeveloper 模块无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- e5f43979b0ba [StateTree] moved RewindDebugger runtime extension from the Editor module to the Developer module since it is meant to be used when recording the data, not analyzing it
- c025768499a7 Run UnrealCodeFixup to add #include UE_INLINE_GENERATED_CPP_BY_NAME
- 09963dce5a3a [StateTreeDebugger] used on stack copy of the active states for recursive call
```

### 维护评价

- **创建时间**：2021 年 9 月，约 4 年历史
- **活跃度**：**活跃维护中**。近期有功能性更新（RewindDebugger 运行时扩展迁移、调试器 bug 修复）和代码质量改进（UE_INLINE_GENERATED_CPP_BY_NAME）
- **规模**：484 个源文件，属于大型插件，说明功能丰富且持续扩展
- **版本状态**：Version 0.1，但 IsBetaVersion=false，说明已脱离 Beta 状态
- **默认启用**：否，需要手动在项目设置中启用
- **推荐程度**：⭐⭐⭐⭐ **推荐使用**。StateTree 是 Epic 官方重点维护的状态机方案，正在逐步替代行为树成为 AI 和游戏逻辑的首选方案。活跃的开发和调试器支持使其成为生产可用的选择。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)