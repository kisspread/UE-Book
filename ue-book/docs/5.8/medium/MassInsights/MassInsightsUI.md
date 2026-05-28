# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | 大规模实体洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (EditorAndProgram), `MassInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights) | |

## 用途

本插件是 Unreal Insights 的一个扩展，专门用于分析和可视化 UE5 的 Mass 实体框架（Mass Entity Framework）在运行时产生的跟踪数据。它解决了在开发使用 Mass 系统的大规模项目时，难以直观理解实体生命周期、原型（Archetype）变化和处理器执行性能的问题。

通过集成到 Unreal Insights 工具中，Mass Insights 能够聚合显示实体创建、销毁和原型变更事件，并在时间线上标记 Mass 处理器的执行阶段，帮助开发者识别性能瓶颈和理解实体数据流。

## 使用场景

- 你正在使用 Mass 框架开发一个包含成千上万个实体的游戏（如RTS、模拟经营游戏），需要分析实体的创建、销毁和原型转换的性能开销。
- 你怀疑某个 Mass 处理器（Processor）执行时间过长，需要在时间线上精确定位其执行区间并分析耗时。
- 你需要跟踪特定实体在运行时的生命周期事件（如创建、组件添加/移除、销毁），以调试与实体状态相关的逻辑错误。
- 你希望了解项目运行时使用了哪些 Mass 原型（Archetype）以及它们各自的片段（Fragment）构成。

## 蓝图用法

本插件主要为 Unreal Insights 程序提供功能扩展，其核心界面和控件不直接面向游戏运行时的蓝图。开发者无法在游戏逻辑蓝图中直接调用其核心分析功能。

在 Unreal Insights 程序内部，其 UI 交互基于 Slate 控件和委托。部分控件可能通过 Slate 控件的 `SNew` 和 `SLATE_ARGUMENT` 间接与蓝图资产（如图表、表格）交互，但这属于编辑器工具开发范畴，而非游戏蓝图用法。

## C++ 用法

本插件主要提供用于扩展 Unreal Insights 程序的 UI 控件和逻辑。其 API 主要面向那些希望将 Mass 分析功能集成到自定义 Insights 选项卡或视图中的开发者。

### 头文件引入

```cpp
// 主分析界面控件
#include "SMassInsightsAnalysisTab.h"

// 实体事件聚合表格控件
#include "SEntityEventAggregationTableView.h"

// 时间线轨道扩展状态
#include "MassInsightsTimingTrack.h"
```

### 基本用法

创建并设置分析主选项卡。这是插件的核心 UI 入口。

```cpp
// 来源: SMassInsightsAnalysisTab.h
using namespace MassInsights;

// 在 Insights 的 Tab 布局中创建 Mass 分析选项卡
TSharedRef<SMassInsightsAnalysisTab> AnalysisTab = SNew(SMassInsightsAnalysisTab);

// 当 Insights 会话改变时，为其设置当前的会话信息
// InTimingViewSession: Insights 时间视图会话
// InAnalysisSession: 正在分析的 Trace 会话
AnalysisTab->SetSession(InTimingViewSession, InAnalysisSession);
```

### 进阶用法

扩展 Unreal Insights 的时间线（Timing View）视图，添加 Mass 特有的区域轨道和菜单。

```cpp
// 来源: MassInsightsTimingTrack.h
// FMassInsightsSharedState 实现了 ITimingViewExtender 接口，用于扩展时间线视图
// 在模块启动时，将其注册到 Insights 的时间线视图扩展器列表中
MassInsightsUI::FMassInsightsSharedState& TimingViewExtender = ...;

// 绑定命令，例如显示/隐藏 Mass 区域轨道
TimingViewExtender.BindCommands();

// 在 Insights 会话开始时，扩展器会自动被通知，并创建自己的轨道（FMassInsightsTrack）
```

使用 `SEntityEventAggregationTableView` 控件，显示实体事件的聚合视图并处理选择事件。

```cpp
// 来源: SEntityEventAggregationTableView.h
TSharedPtr<SEntityEventAggregationTableView> AggregationView;

// 设置当用户选择一个原型时触发的委托
MassInsightsUI::FOnSelectedArchetype OnArchetypeSelected;
OnArchetypeSelected.BindLambda([](uint64 SelectedArchetypeID) {
    // 处理原型选择，例如在另一个控件中显示其详情
});

// 设置当用户选择一个聚合行（代表一个实体）时触发的委托
MassInsightsUI::FEntityEventContainerRowSelected OnRowSelected;
OnRowSelected.BindLambda([](const MassInsights::FEntityEventSummaryRowSelectedParams& Params) {
    if (Params.IsSelected) {
        // 可以使用 Params.EntityID, Params.FirstEventTime 等信息
        // 例如，筛选并显示该实体的所有事件列表
    }
});

// 创建控件并传入委托
AggregationView = SNew(SEntityEventAggregationTableView)
    .OnArchetypeSelected(OnArchetypeSelected)
    .OnRowSelected(OnRowSelected);
```

## Demo 示例

以下示例展示了如何创建一个简单的 Insights 主选项卡，其中包含 Mass Insights 的聚合视图。

```cpp
// MyInsightsMassTab.h
#pragma once

#include "CoreMinimal.h"
#include "Widgets/SCompoundWidget.h"
#include "SEntityEventAggregationTableView.h"

class SMyInsightsMassTab : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyInsightsMassTab) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<MassInsights::SEntityEventAggregationTableView> AggregationView;
};
```

```cpp
// MyInsightsMassTab.cpp
#include "MyInsightsMassTab.h"
#include "Widgets/SEntityEventAggregationTableView.h"

void SMyInsightsMassTab::Construct(const FArguments& InArgs)
{
    // 定义选择原型时的回调
    MassInsightsUI::FOnSelectedArchetype OnArchetypeSelected;
    OnArchetypeSelected.BindLambda([this](uint64 ArchetypeID) {
        UE_LOG(LogTemp, Log, TEXT("Selected Archetype ID: %llu"), ArchetypeID);
        // 在此可以打开原型详情视图
    });

    ChildSlot
    [
        SNew(SVerticalBox)
        + SVerticalBox::Slot()
        .AutoHeight()
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Mass Entity Event Aggregation")))
        ]
        + SVerticalBox::Slot()
        .FillHeight(1.0f)
        [
            // 创建核心的实体事件聚合表格控件
            SAssignNew(AggregationView, MassInsights::SEntityEventAggregationTableView)
            .OnArchetypeSelected(OnArchetypeSelected)
        ]
    ];
}
```

## 模块依赖

从模块的 `Build.cs` 文件分析，要使用本插件的功能（特别是分析模块），你的模块可能需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `InsightsCore` | 提供 Insights 的基础框架、表格视图模型、工具命令等。 |
| `Insights` | 提供 Unreal Insights 程序的核心接口和扩展点（如 `ITimingViewExtender`）。 |
| `TraceAnalysis` | 用于解析和查询来自应用程序的 Trace 数据会话 (`IAnalysisSession`)。 |
| `TraceServices` | 提供 Trace 会话服务的接口定义。 |
| `MassEntity` | Mass 实体框架的核心，提供了定义实体、片段、系统等的基础结构。 |
| `MassInsightsAnalysis` | 本插件的分析逻辑模块，负责处理原始的 Mass Trace 事件。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-06 | `973765c5` | [MassInsights] Fixed deprecated FName for FBaseTreeNode constructor. | 修复了 `FBaseTreeNode` 构造函数中已废弃的 `FName` 用法，属于编译兼容性维护。 |
| 2026-03-31 | `65c8bacb` | [MassTrace] | 与 Mass 跟踪系统相关的改动，可能涉及数据结构或接口变更。 |
| 2026-03-27 | `51a4c1e5` | [MassTrace] | 与 Mass 跟踪系统相关的改动，可能涉及数据结构或接口变更。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 对整个引擎运行代码修复工具，将空析构函数改为 `= default`，属于全局代码风格/性能优化。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty... | 使用代码修复工具更新头文件，确保 DLL 导出/导入声明在方法和静态变量上正确，属于平台兼容性修复。 |

### 维护评价

- **活跃维护**: 本插件创建于 2025 年 3 月，是一个非常新的插件。最近几次更新（2026年3-4月）均集中在适应底层框架（MassTrace）的变化和保持编译兼容性上，表明它仍在随着引擎版本演进进行积极维护。
- **实验性**: 插件自身标记为 `IsBetaVersion=true`，且其功能描述中提到“Performance is still a work in progress. Not suitable yet for millions of events.”，明确表示其性能尚未优化到处理海量事件的程度。
- **推荐使用**: 推荐在开发使用 Mass 框架的大型项目时**尝试使用**，以获取宝贵的性能洞察。但由于其 beta 状态和明确的性能限制，不建议在生产环境或处理超大规模事件的场景中过度依赖其UI的响应性。它是目前官方提供的唯一专门用于分析 Mass 框架运行时行为的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights)
- [官方文档](https://docs.unrealengine.com) （暂无专门页面，可参考 Unreal Insights 文档）
- [测试用例] （暂未发现独立的测试文件）