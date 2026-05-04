# Message Bus Insights

> Allows debugging of Message Bus via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `UdpMessagingInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2025-12-11 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/MessagingInsights) | |

## 用途

该插件将 Unreal Engine 的 UDP 消息总线（UdpMessaging）的运行时事件集成到 Unreal Insights 的时间线视图中。它解决了消息总线调试困难的问题，允许开发者在 Insights 中可视化地分析消息的发送、接收、生命周期（如创建、分段、确认、超时等）以及相关的性能指标，从而诊断消息丢失、延迟或性能瓶颈等问题。

## 使用场景

- 你正在使用 UDP 消息总线进行进程间通信（如游戏客户端与服务器、编辑器与独立进程），并遇到了消息延迟或丢失的问题。
- 你需要分析消息总线的性能，例如查看特定消息类型的发送/接收频率、大小以及处理耗时。
- 你希望在 Unreal Insights 的时间线上直观地看到消息事件的时序关系，以便理解复杂的通信流程。

## 蓝图用法

该插件不提供蓝图可调用的函数或属性。其功能完全集成在 Unreal Insights 工具中，通过 Insights 的 UI 进行交互。

## C++ 用法

该插件主要作为 Unreal Insights 的扩展模块运行，其核心功能是通过 Trace 和 Insights 的 API 实现的。开发者通常不需要直接调用其 C++ API，而是通过启用插件并在 Insights 中查看结果。

### 头文件引入

```cpp
// 主要用于 Insights 扩展开发
#include "Insights/ITimingViewExtender.h"
#include "TraceServices/ModuleService.h"
```

### 基本用法

该插件通过注册 Trace 分析模块和 Timing 视图扩展器来工作。以下代码展示了其核心注册逻辑（摘自 `UdpMessagingTraceModule.cpp` 和 `UdpMessagingTimingViewExtender.cpp`）：

```cpp
// 注册 Trace 分析模块，用于处理 UDP 消息的追踪事件
void FUdpMessagingTraceModule::GetModuleInfo(TraceServices::FModuleInfo& OutModuleInfo)
{
    OutModuleInfo.Name = TEXT("UdpMessaging");
    OutModuleInfo.DisplayName = TEXT("UDP Messaging");
}

// 当分析会话开始时，创建并注册分析器
void FUdpMessagingTraceModule::OnAnalysisBegin(TraceServices::IAnalysisSession& Session)
{
    // 创建用于存储分析数据的 Provider
    auto Provider = MakeShared<FUdpMessagingProvider>(Session);
    Session.AddProvider(FUdpMessagingProvider::ProviderName, Provider);

    // 创建并注册分析器，用于解析原始的 Trace 事件
    Session.AddAnalyzer(new FUdpMessagingAnalyzer(Session, *Provider));
}

// 注册 Timing 视图扩展器，用于在 Insights 时间线中显示消息轨道
void FUdpMessagingTimingViewExtender::OnBeginSession(UE::Insights::Timing::ITimingViewSession& InSession)
{
    // 为每个 Insights 会话创建并存储会话数据
    FPerSessionData& Data = PerSessionDataMap.Add(&InSession);
    Data.SharedData = MakePimpl<FUdpMessagingTimingViewSession>();
    Data.SharedData->OnBeginSession(InSession);
}
```

### 进阶用法

插件的核心数据结构定义了如何将原始的 Trace 事件转换为 Insights 可显示的时间事件。例如，`FMessageLifecycleEvent` 结构体用于表示消息生命周期中的一个事件点（如发送、接收、确认），并包含计算出的“泳道深度”（`LaneDepth`）以便在时间线上正确布局。

```cpp
// 消息生命周期事件，包含事件类型和计算出的泳道深度
struct FMessageLifecycleEvent
{
    uint64 Cycle; // 事件发生的 CPU 周期
    uint16 SenderShortId;
    uint16 RecipientShortId;
    uint32 MessageId;
    // ... 其他字段
    int32 LaneDepth = 0; // 用于在时间线轨道中垂直排列事件

    static FMessageLifecycleEvent FromEventData(const UE::Trace::IAnalyzer::FEventData& EventData);
};
```

## Demo 示例

以下是一个最小示例，展示如何将 `MessagingInsights` 插件的功能集成到自定义的 Insights 扩展中。请注意，这通常不是最终用户需要做的，而是 Insights 扩展开发者的参考。

**MyInsightsExtension.h**
```cpp
#pragma once

#include "Insights/ITimingViewExtender.h"

class FMyInsightsExtension : public UE::Insights::Timing::ITimingViewExtender
{
public:
    //~ Begin ITimingViewExtender interface
    virtual void OnBeginSession(UE::Insights::Timing::ITimingViewSession& InSession) override;
    virtual void OnEndSession(UE::Insights::Timing::ITimingViewSession& InSession) override;
    virtual void Tick(const UE::Insights::Timing::FTimingViewExtenderTickParams& InParams) override;
    //~ End ITimingViewExtender interface
};
```

**MyInsightsExtension.cpp**
```cpp
#include "MyInsightsExtension.h"
#include "UdpMessagingTimingViewSession.h" // 引用插件提供的会话管理类

void FMyInsightsExtension::OnBeginSession(UE::Insights::Timing::ITimingViewSession& InSession)
{
    // 在这里，你可以创建一个 FUdpMessagingTimingViewSession 实例
    // 并调用其 OnBeginSession 方法，就像插件内部所做的那样。
    // 这将把 UDP 消息轨道添加到你的 Insights 视图中。
    // auto MessagingSession = MakeShared<UE::MessagingInsights::FUdpMessagingTimingViewSession>();
    // MessagingSession->OnBeginSession(InSession);
}

void FMyInsightsExtension::OnEndSession(UE::Insights::Timing::ITimingViewSession& InSession)
{
    // 清理会话数据
}

void FMyInsightsExtension::Tick(const UE::Insights::Timing::FTimingViewExtenderTickParams& InParams)
{
    // 更新轨道数据
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Trace` | 提供底层的 Trace 事件分析框架 |
| `TraceServices` | 提供 Trace 分析会话和模块管理服务 |
| `Insights` | 提供 Unreal Insights 的核心视图和扩展接口 |
| `UdpMessaging` | 提供 UDP 消息总线的运行时实现和 Trace 事件定义 |

## 维护状态

### 近期更新

- `ca4a6ebe` 2025-12-11 — UdpMessaging: Add MessagingInsights plugin for Unreal Insights, and corresponding instrumentation.

### 维护评价

- **创建时间**：该插件于 2025 年 12 月创建，是一个非常新的功能。
- **更新频率**：目前仅有一次初始提交，表明它处于早期开发或刚刚发布阶段。
- **活跃度**：作为新插件，其长期维护状态尚不明确，但由 Epic Games 创建，通常会有持续支持。
- **已知限制**：插件默认未启用（`EnabledByDefault: false`），需要用户手动在项目设置中启用。它仅支持 `UnrealInsights` 程序。
- **推荐使用**：**推荐**。如果你正在使用 UDP 消息总线并需要进行深度调试和性能分析，这是一个非常有价值的工具。鉴于其新特性，建议关注后续更新以获取更多功能和稳定性改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Messaging/MessagingInsights)