# RenderTrace Insights

> Rendering debugging facilities in Unreal Insights（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `RenderTraceInsights` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-03-19 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/RenderTraceInsights) | |

## 用途

RenderTrace Insights 插件为 Unreal Insights 分析工具提供了深度的渲染管线调试和可视化功能。它不是一个运行时游戏功能，而是一个**性能分析与调试工具**。其核心目的是帮助开发者理解渲染线程、RHI 线程以及 GPU 提交队列的详细工作流程和时序关系。

通过分析引擎内部的渲染追踪事件（如 RDG Pass 执行、命令列表录制与提交、RHI 翻译任务、同步点等），该插件在 Insights 的 Timing 视图中创建专门的轨道，将这些复杂的、跨线程的渲染活动以直观的时间线形式展现出来。这使得开发者能够精确定位渲染瓶颈、线程同步问题以及 GPU 提交延迟。

## 使用场景

- 你正在优化一个复杂场景的渲染性能，需要分析 **RDG (Render Dependency Graph)** Pass 的执行顺序和耗时。
- 你需要调试 **RHI (Render Hardware Interface)** 线程上的命令列表翻译和提交过程，查看是否存在阻塞或延迟。
- 你怀疑渲染管线中存在 **CPU-GPU 同步问题**，需要查看同步点（Sync Points）和栅栏（Fences）的信号与等待时序。
- 你需要可视化 **命令列表（Command Lists）** 从创建、录制到最终提交给平台 API 的完整生命周期。
- 你希望对比 **游戏线程、渲染线程、RHI 线程** 的活动，分析它们之间的依赖和等待关系。

## 蓝图用法

此插件主要作为 Unreal Insights 的扩展模块运行，**不提供公开的蓝图 API**。其功能完全集成在 Unreal Insights 分析工具的界面中，通过 Timing 视图的轨道和过滤器菜单进行交互。

## C++ 用法

此插件的核心是作为 Unreal Insights 的分析模块。开发者通常不会直接在游戏代码中调用它，而是通过引擎的追踪系统（Trace）来生成数据，然后由本插件在 Insights 中进行分析和展示。

### 头文件引入

```cpp
// 如果你需要实现自定义的渲染追踪数据提供者，需要引入此接口
#include "IRenderTraceProvider.h"
```

### 基本用法

本插件的核心是 `IRenderTraceProvider` 接口和 `FRenderTraceAnalyzer` 分析器。`FRenderTraceAnalyzer` 负责接收来自引擎的追踪事件包，并将解析后的数据（如命令列表、RDG Pass）存储到 `IRenderTraceProvider` 中。

以下是一个简化的分析器处理事件的示例逻辑（基于 `RenderTraceAnalyzer.h`）：

```cpp
// 来源: Engine/Plugins/RenderTraceInsights/Private/RenderTraceAnalyzer.h
// FRenderTraceAnalyzer::OnEvent 是处理所有追踪事件的核心函数
bool FRenderTraceAnalyzer::OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& EventContext)
{
    const auto& EventData = EventContext.EventData;
    switch (RouteId)
    {
    case Packet_CommandListCreated:
    {
        // 从事件数据中读取信息
        uint64 AppID = EventData.GetValue<uint64>(TEXT("AppID"));
        double Timestamp = EventContext.Timestamp;
        ECommandListType Type = static_cast<ECommandListType>(EventData.GetValue<uint8>(TEXT("Type")));

        // 调用 Provider 接口，将解析后的数据存储起来
        auto [ID, CommandList] = Provider.AddCommandList(AppID, Timestamp, Type);
        // ... 处理其他字段
        break;
    }
    case Packet_BeginExecuteRDGPass:
    {
        // 处理 RDG Pass 开始执行的事件
        uint32 PassID = EventData.GetValue<uint32>(TEXT("PassID"));
        // ... 存储到 Provider
        break;
    }
    // ... 处理其他数十种事件类型
    }
    return true;
}
```

### 进阶用法

插件通过 `FRenderTraceTimingViewExtender` 将分析结果集成到 Insights 的 Timing 视图中。它会创建多种专用轨道：

1.  **`FCommandListTrack`**: 显示每个命令列表的生命周期（创建、录制、提交）。
2.  **`FRDGThreadTrack`**: 显示渲染线程上 RDG Pass 的执行时序。
3.  **`FRHIThreadTrack`**: 显示 RHI 线程上的活动，如命令列表翻译。
4.  **`FSubmissionQueueTrack`**: 显示平台命令队列的提交批次和等待事件。
5.  **`FInterruptTrack`**: 显示中断队列相关的唤醒事件。

这些轨道之间会通过 `FRenderTraceRelation` 绘制关联线，直观展示事件之间的因果关系（例如，一个 RDG Pass 的结束触发了某个命令列表的提交）。

## Demo 示例

由于此插件是分析工具，没有典型的运行时游戏代码示例。以下是一个**概念性**的示例，展示如何为自定义的渲染事件创建一个简单的分析器模块，这可以作为理解本插件工作原理的参考。

**MyCustomRenderTraceModule.h**
```cpp
#pragma once
#include "TraceServices/ModuleService.h"

class FMyCustomRenderTraceModule : public TraceServices::IModule
{
public:
    virtual void GetModuleInfo(TraceServices::FModuleInfo& OutModuleInfo) override
    {
        OutModuleInfo.Name = TEXT("MyCustomRenderTrace");
        OutModuleInfo.DisplayName = TEXT("My Custom Render Trace");
    }

    virtual void OnAnalysisBegin(TraceServices::IAnalysisSession& Session) override
    {
        // 在这里创建你的分析器和数据提供者，并注册到 Session 中
        // 例如: Session.AddAnalyzer(new FMyCustomAnalyzer(Session, MyProvider));
    }

    virtual void GetLoggers(TArray<const TCHAR*>& OutLoggers) override
    {
        // 返回你的追踪日志类别
    }

    virtual const TCHAR* GetCommandLineArgument() override
    {
        return TEXT("mycustomrendertrace");
    }
};
```

## 模块依赖

从源码结构推断，此插件深度集成于 Unreal Insights 框架。

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 的核心服务模块，提供分析会话、模块接口等基础功能。 |
| `InsightsCore` | Insights 的核心视图模型和通用组件，如 `FTimingEventsTrack`、`ITimingViewExtender`。 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF。
- 2026-03-27 `a8887563` 修复 RHI 上下文处理中的不一致问题，以及上下文指针可能的 use-after-free 错误。
- 2026-03-25 `c0844f20` RenderTrace: 使用 ID 代替在每个事件上发送完整字符串来表示 RDG Pass 名称。
- 2026-03-20 `5b33fd59` 使用通用名称进行平台提交追踪。
- 2026-03-19 `7214f80a` 渲染事件追踪（初始提交）。

### 维护评价

- **创建时间**：2026年3月，非常新的插件。
- **更新频率**：在创建后的一个月内有多次积极的提交，包括功能优化（使用ID代替字符串）和重要的 Bug 修复（use-after-free）。
- **维护状态**：**活跃维护中**。作为 Epic Games 官方维护的 Insights 扩展，预计会随着引擎版本持续更新。
- **已知限制**：作为分析工具，其功能依赖于引擎内部的追踪点。如果某些渲染活动没有被追踪，将无法在此插件中显示。
- **推荐使用**：**强烈推荐**。对于任何需要深入分析渲染管线性能和调试渲染问题的开发者，这是一个极其强大且官方的工具。它是理解现代 UE 渲染架构工作原理的绝佳窗口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/RenderTraceInsights)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的路径中发现)