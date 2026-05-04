# Niagara Insights

> Niagara Unreal Insights Debugging and Performance

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NiagaraInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2026-03-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraInsights) | |

## 用途

Niagara Insights 插件为 Unreal Insights 工具集添加了专门用于分析和调试 Niagara 粒子系统性能的功能。它不是一个运行时插件，而是作为 Unreal Insights 应用程序的一个扩展模块存在。

该插件的核心价值在于：
1.  **性能数据采集与分析**：通过 `FNiagaraAnalyzer` 接收来自 Niagara 系统的性能跟踪事件（如系统性能、组件激活/停用、数据通道操作），并将这些原始数据解析、聚合到 `FNiagaraProvider` 中。
2.  **可视化与交互**：在 Unreal Insights 的 Timing Profiler 视图中，添加专门的 Niagara 性能图表轨道（`FNiagaraPerformanceGraphTrack`、`FNiagaraInstanceLifecycleTrack`、`FNiagaraDataChannelTrack`），直观展示游戏线程/渲染线程耗时、实例数量、GPU 耗时和内存使用等关键指标。
3.  **范围统计分析**：提供一个名为 “Niagara Range Stats” 的侧边栏视图（`SNiagaraRangeStatsView`），当用户在 Timing Profiler 中选择一个时间范围时，该视图会自动计算并显示该范围内表现最差（Top 5）的 Niagara 系统，帮助开发者快速定位性能瓶颈。

简而言之，它解决了在复杂项目中分析和优化 Niagara 粒子系统性能的难题，将分散的性能数据整合到一个统一的、交互式的分析界面中。

## 使用场景

-   你的游戏或应用中大量使用了 Niagara 粒子系统，但发现帧率下降或 GPU 负载过高 → 使用 Niagara Insights 来识别哪些系统、在哪些时刻消耗了最多的性能资源。
-   你需要优化一个特定的 Niagara 系统，想了解其在不同线程（游戏线程、渲染线程）上的开销分布，以及实例数量的变化如何影响性能 → 使用 Niagara Insights 的图表轨道和范围统计功能进行深入分析。
-   你正在调试 Niagara 数据通道（Data Channel）的发布和写入事件，需要查看事件发生的时间点和相关上下文 → 使用 Niagara Insights 的数据通道轨道进行追踪。

## 蓝图用法

此插件主要作为 Unreal Insights 的扩展模块，其核心功能（数据采集、分析、UI 展示）均在编辑器工具和 Insights 应用程序内部实现，**不提供公开的蓝图 API**。用户通过 Unreal Insights 应用程序的图形界面与其交互。

## C++ 用法

此插件的 C++ 用法主要面向 Insights 模块的开发者，用于扩展或集成 Niagara 的性能分析功能。

### 头文件引入

```cpp
// 引入 Niagara Insights 模块的核心头文件
#include "NiagaraInsightsModule.h"

// 如果需要访问会话数据
#include "NiagaraTimingViewSession.h"
```

### 基本用法

此插件的使用主要通过 Unreal Insights 应用程序进行。在 C++ 层面，其模块会自动注册到 Insights 系统中。以下是其内部工作原理的简要说明：

```cpp
// 1. 模块启动时，会注册一个 Trace 模块和一个 Timing View 扩展器
// 来源: Source/NiagaraInsights/Private/NiagaraInsightsModule.cpp (推断)
void FNiagaraInsightsModule::StartupModule()
{
    // 注册用于接收和解析 Niagara 跟踪事件的模块
    TraceServices::GetModuleService().RegisterModule(TraceModule);
    
    // 注册用于扩展 Timing Profiler 视图的扩展器
    UE::Insights::Timing::GetTimingViewExtenderManager().RegisterExtender(TimingViewExtender);
    
    // 尝试注册 Insights 组件（用于添加 Range Stats 标签页）
    TryRegisterInsightsComponent();
}

// 2. 当用户打开一个包含 Niagara 跟踪数据的 .utrace 文件时，分析器开始工作
// 来源: Source/NiagaraInsights/Private/NiagaraAnalyzer.cpp (推断)
void FNiagaraAnalyzer::OnAnalysisBegin(const FOnAnalysisContext& Context)
{
    // 注册对各种 Niagara 事件路由的监听
    Context.RouteEvent(RouteId_SystemPerformance_GT, "Niagara", "SystemPerformance_GT");
    Context.RouteEvent(RouteId_SystemPerformance_RT, "Niagara", "SystemPerformance_RT");
    // ... 其他事件路由
}

// 3. 当接收到事件时，解析数据并存入 Provider
bool FNiagaraAnalyzer::OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context)
{
    switch (RouteId)
    {
    case RouteId_SystemPerformance_GT:
        // 解析游戏线程性能数据
        const auto& EventData = Context.EventData;
        FSystemPerformanceFrame_GT Frame;
        Frame.Time = EventData.GetValue<double>("Time");
        // ... 解析其他字段
        Provider.AddGameThreadFrame(MoveTemp(Frame));
        break;
    // ... 处理其他事件
    }
    return true;
}
```

### 进阶用法

对于希望扩展或自定义 Niagara Insights 功能的开发者，可以关注其会话管理机制：

```cpp
// 获取当前活跃的 Niagara Timing View 会话
// 来源: Source/NiagaraInsights/Private/NiagaraTimingViewExtender.h
FNiagaraTimingViewSession* Session = TimingViewExtender.FindFirstActiveSession();
if (Session)
{
    // 监听用户选择的时间范围变化
    Session->OnRangeChanged.AddLambda([](double StartTime, double EndTime)
    {
        // 在这里可以基于新的时间范围执行自定义分析
        UE_LOG(LogTemp, Log, TEXT("Niagara selection range changed: [%f, %f]"), StartTime, EndTime);
    });
    
    // 或者，当新的会话开始时进行绑定
    TimingViewExtender.OnSessionBegun.AddLambda([](FNiagaraTimingViewSession& NewSession)
    {
        // 对新会话进行初始化设置
    });
}
```

## Demo 示例

此插件没有独立的运行时 Demo 示例。其功能完全集成在 Unreal Insights 应用程序中。要体验其功能，请执行以下步骤：

1.  确保你的项目启用了 `NiagaraInsights` 插件（默认已启用）。
2.  在编辑器中运行你的游戏或应用，并确保启用了性能跟踪（通常通过 `-trace=niagaratrace,cpu,gpu` 命令行参数）。
3.  生成 `.utrace` 文件。
4.  打开 Unreal Insights 应用程序，加载该 `.utrace` 文件。
5.  在 Timing Profiler 视图中，你将看到新增的 “Niagara” 相关图表轨道。
6.  选择一段时间范围，右侧的 “Niagara Range Stats” 面板将显示该范围内的性能热点。

## 模块依赖

此插件的模块依赖主要面向 Insights 框架，对游戏运行时模块无特殊依赖。

| 模块 | 用途 |
|---|---|
| `InsightsCore` | 提供 Insights 应用程序的核心框架、图表轨道基类等 |
| `TraceServices` | 提供跟踪数据的分析会话、模块服务接口 |
| `TraceAnalysis` | 提供跟踪事件分析器基类 |

## 维护状态

### 近期更新

-   2026-03-24 `b825647e` — 优化：如果没有数据，则不显示 Niagara 轨道
-   2026-03-20 `bee2d01f` — 功能：向 Niagara Insights 添加数据通道事件
-   2026-03-18 `dd555529` — 功能：初始提交，实现 Niagara Insights 核心功能

### 维护评价

-   **创建时间**：2026年3月，是一个非常新的插件。
-   **近期更新**：在创建后一周内连续有三次提交，包括功能添加和优化，表明处于**活跃开发初期**。
-   **维护状态**：**活跃维护中**。作为 Epic Games 官方维护的 Insights 扩展，预计会随着 Niagara 和 Insights 模块的更新而持续维护。
-   **已知限制**：目前仅支持通过 Unreal Insights 应用程序查看，没有编辑器内的实时预览功能。
-   **推荐使用**：**强烈推荐**。对于任何使用 Niagara 并关注性能的项目，这是一个必备的官方分析工具。它提供了深度、直观的性能数据，是优化 Niagara 系统的利器。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/FX/NiagaraInsights)
-   [官方文档]() (暂无)
-   [测试用例]() (暂未发现独立的测试用例文件)