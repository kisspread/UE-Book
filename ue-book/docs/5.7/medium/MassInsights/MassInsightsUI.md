# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | 群组洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (EditorAndProgram), `MassInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights) | |

## 用途

Mass Insights 是 Unreal Insights 分析工具的一个扩展，专门用于收集和可视化 Mass 框架的执行细节。它通过以下方式帮助开发者深入理解 Mass 系统的运行时行为：

- **时序轨道**：在 Timing Insights 页面中新增 `FMassInsightsTrack`，展示 Mass 系统的活动区间（Regions），可直接在时间轴上查看。
- **实体事件聚合表**：以表格形式汇总每个实体的事件触发频率、总耗时等，支持筛选和排序。
- **片段（Fragment）一览表**：列出所有已知的 Mass Fragment，显示其 ID、名称、类型和大小。
- **构型详情面板**：选中某个构型（Archetype）后，展示其包含的 Fragment 列表及其详细信息。
- **实体事件时间线**：针对特定实体，按时间顺序列出其所有事件，支持跳转到原始事件。

该插件解决了 Mass 开发者缺乏专用可视化调试工具的痛点，将 Mass 的内部执行过程透明化，辅助性能分析、瓶颈定位和逻辑验证。

## 使用场景

- 你正在使用 UE5 的 Mass 框架实现大规模 AI 群体、城市模拟或生态模拟，需要查看每个实体的事件处理顺序和耗时。
- 你想分析 Mass 片段如何在不同构型间分配，确认内存布局是否合理。
- 你需要追踪特定实体在仿真周期中的完整执行路径，检查逻辑顺序正确性。
- 你在进行性能调优，希望识别 Mass 系统中耗时最长的实体或片段。

## 蓝图用法

该插件不暴露任何蓝图可调用的函数。所有功能均通过 Unreal Insights 编辑器界面提供，只有在使用 Unreal Insights 分析捕获的 Mass 跟踪数据时才会激活。

## C++ 用法

插件主要提供 Slate UI 组件和时序视图扩展器。开发者可以引用 `MassInsightsUI` 模块并在自己的编辑器工具中嵌入相关控件，或利用 `FMassInsightsSharedState` 扩展时序视图。

### 头文件引入

```cpp
#include "MassInsightsUI/MassInsightsTimingTrack.h"
#include "MassInsightsUI/Widgets/SMassInsightsAnalysisTab.h"
#include "MassInsightsUI/Widgets/SFragmentTableView.h"
#include "MassInsightsUI/Widgets/SEntityEventAggregationTableView.h"
```

### 基本用法：获取分析标签页

```cpp
// 获取 MassInsightsUI 模块实例
FMassInsightsUIModule& Module = FMassInsightsUIModule::Get();
TSharedPtr<MassInsights::SMassInsightsAnalysisTab> AnalysisTab = Module.GetAnalysisTab();
if (AnalysisTab.IsValid())
{
    // 设置时序视图会话和分析会话
    AnalysisTab->SetSession(TimingViewSession, AnalysisSession);
}
```

*来源：`MassInsightsUIModule.h`*

### 进阶用法：添加自定义时序轨道监听

```cpp
// 创建共享状态并注册为时序视图扩展器
FMassInsightsSharedState SharedState;
// 在模块启动时自动注册，无需手动操作

// 通过命令绑定控制轨道显示
SharedState.BindCommands();
SharedState.ShowHideRegionsTrack();

// 获取轨道可见性
if (SharedState.IsRegionsTrackVisible())
{
    // 轨道可见时执行额外逻辑
}
```

*来源：`MassInsightsTimingTrack.h`*

### 自定义表格格式器

```cpp
// 使用自定义时间格式化器（HH:MM:SS.ssssss）
MassInsightsUI::FTableCellFormatterTimeHMS TimeFormatter;
// 将格式化器应用于表格列
Table->GetColumn("StartTime")->SetValueFormatter(MakeShared<MassInsightsUI::FTableCellFormatterTimeHMS>());
```

*来源：`Common.h`*

## Demo 示例

以下示例创建一个简单的编辑器窗口，嵌入 Mass 实体事件聚合表。假设你有一个编辑器模块，依赖了 `MassInsightsUI`。

### MyMassAnalysisWidget.h

```cpp
#pragma once

#include "MassInsightsUI/Widgets/SEntityEventAggregationTableView.h"
#include "Widgets/SCompoundWidget.h"

class SMyMassAnalysisWidget : public SCompoundWidget
{
public:
    SLATE_BEGIN_ARGS(SMyMassAnalysisWidget) {}
    SLATE_END_ARGS()

    void Construct(const FArguments& InArgs);

private:
    TSharedPtr<MassInsights::SEntityEventAggregationTableView> AggregationTableView;
};
```

### MyMassAnalysisWidget.cpp

```cpp
#include "MyMassAnalysisWidget.h"
#include "MassInsightsUI/Widgets/SEntityEventAggregationTableView.h"

void SMyMassAnalysisWidget::Construct(const FArguments& InArgs)
{
    AggregationTableView = SNew(MassInsights::SEntityEventAggregationTableView)
        .OnArchetypeSelected_Lambda([](uint64 ArchetypeID)
        {
            UE_LOG(LogTemp, Log, TEXT("Selected Archetype ID: %llu"), ArchetypeID);
        })
        .OnRowSelected_Lambda([](const MassInsights::FEntityEventSummaryRowSelectedParams& Params)
        {
            if (Params.IsSelected)
            {
                UE_LOG(LogTemp, Log, TEXT("Entity %llu selected, events from %f to %f"),
                    Params.EntityID, Params.FirstEventTime, Params.LastEventTime);
            }
        });

    ChildSlot
    [
        AggregationTableView.ToSharedRef()
    ];
}
```

使用此组件前，需确保已通过 `FMassInsightsUIModule::GetAnalysisTab()` 之类的接口正确设置了分析会话。该示例仅展示组件嵌入方法。

## 模块依赖

使用 `MassInsightsUI` 模块时，你的模块需要在 Build.cs 中添加以下依赖项（省略通用依赖如 Core、Engine、Slate 等）：

| 模块 | 用途 |
|---|---|
| `MassInsightsAnalysis` | 提供底层 Mass 洞察数据结构（如 `FMassInsights`、`FMassFragmentInfo`） |
| `InsightsCore` | 提供表格、树节点、格式化器等基础 UI 组件 |
| `TraceServices` | 提供追踪分析会话的访问接口 |
| `Insights` | 提供时序视图会话和扩展机制 |

## 维护状态

### 近期更新

- 2025-05-31 `52e3dac` 更新头文件：使用 UnrealCodeFixup 确保 DLL 导出存储位于方法/静态变量而非类型上
- 2025-04-02 `46cab30d` 修复不可达代码警告
- 2025-03-25 `c90dffef` 为 MassInsights 修复 LOCTEXT 缺失
- 2025-03-24 `81901d1e` 修复缺失的 LOCTEXT 键
- 2025-03-20 `0690086f` 修复版权声明

### 维护评价

该插件创建于 2025 年 3 月，截至目前仅有约 5 个月历史，仍处于早期活跃开发阶段。提交记录显示团队正在修复编译警告、本地化文本缺失等基础问题，并进行了头文件适配更新。**虽标记为实验性（Beta）**，但其功能已较为完整，可以用于开发测试。建议生产环境谨慎使用，并留意后续迭代。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights)
- [官方文档](https://docs.unrealengine.com/5.4/en-US/mass-entity-framework-in-unreal-engine/)（Mass 框架概述，非本插件专属）
- 该插件暂无独立测试用例文件。