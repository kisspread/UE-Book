# Concert Insights Visualizer

> Analyses and provides visualization widgets for Concert message types in Unreal Insights.

| 属性 | 值 |
|---|---|
| 中文名 | Concert 可视化分析器 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ConcertInsightsVisualizer` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-06 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer) | |

## 用途

该插件是 Unreal Insights 的一个扩展模块，旨在解决**多用户（Multi-User）会话中的网络活动可视化分析问题**。它通过引入追踪宏（trace macros）来跨多台参与会话的机器关联数据，使开发者能够在 Insights 的时间轴视图中，可视化一个对象（如 Actor）从开始处理、经过网络传输、到最终被接收端处理的完整生命周期。

其核心价值在于，当多个开发者在同一会话中协作编辑场景时，对象同步可能涉及复杂的网络交互和潜在的延迟。此插件将这些原本难以追踪的跨机器网络活动，以直观的时间线形式展示出来，帮助开发者诊断同步问题、分析网络瓶颈或理解对象更新的传播路径。

## 使用场景

-   **大型团队协作开发**：当使用 UE5 的多用户编辑功能时，团队成员需要监控对象同步的状态和性能，以确保协作流畅。
-   **网络同步问题诊断**：当某个对象在客户端和服务器间的同步出现异常（如延迟、丢失、状态不一致）时，可以利用此工具回溯该对象在网络上的完整传输和处理路径。
-   **性能剖析**：分析特定对象在多用户环境下的处理耗时，识别网络传输或特定端点处理过程中的性能热点。

## 蓝图用法

**不适用。** 此插件的核心功能是作为 Unreal Insights 的分析后端和可视化轨道提供程序，其主要接口（`IConcertInsightsVisualizerModule`）是 C++ 模块接口，并未暴露任何蓝图可调用（`BlueprintCallable`）函数或蓝图可读写（`BlueprintReadWrite`）属性。它的使用完全在 Insights 工具的 UI 中进行。

## C++ 用法

此插件并非供游戏逻辑直接调用的 API，而是作为 Unreal Insights 的扩展。其 C++ 用法主要涉及在 Insights 应用内部注册和管理分析模块。

### 头文件引入

```cpp
#include "IConcertInsightsVisualizerModule.h"
```

### 基本用法

主要是检查和访问该 Insights 扩展模块。

```cpp
// 来源: Public/IConcertInsightsVisualizerModule.h

// 获取模块单例
if (UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule::IsAvailable())
{
    UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule& Module = 
        UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule::Get();
    // 模块可用，通常无需直接操作，其功能已自动集成到 Insights UI。
}
```

### 进阶用法

该插件的功能主要通过 Insights 的扩展点实现。开发者无需直接调用其内部类。核心流程如下：
1.  当 Insights 分析一个包含 Concert 追踪事件的 `.utrace` 文件时，插件注册的 `FConcertTraceInsightsModule` 会创建分析器和数据提供者。
2.  `FConcertTimingViewExtender` 负责在 Insights 的时间轴视图中为每个会话创建 `FConcertTimingViewSession`。
3.  `FConcertTimingViewSession` 管理 `FProtocolTrack` 和 `FTraceAggregator`。`FTraceAggregator` 负责关联分析其他相关的 `.utrace` 文件（来自其他参与机器），并将数据聚合。
4.  所有分析出的对象序列、网络范围和处理步骤数据，由 `FProtocolMultiEndpointProvider` 统一管理，并由 `FProtocolTrack` 绘制到时间轴上。

## Demo 示例

这是一个检查 Insights 中 Concert 可视化模块是否加载的最小示例。

**文件： `ConcertInsightsCheck.h`**
```cpp
#pragma once

#include "CoreMinimal.h"

class FConcertInsightsChecker
{
public:
    static void CheckModuleAvailability();
};
```

**文件： `ConcertInsightsCheck.cpp`**
```cpp
#include "ConcertInsightsCheck.h"
#include "IConcertInsightsVisualizerModule.h"

void FConcertInsightsChecker::CheckModuleAvailability()
{
    // 此代码运行在 UnrealInsights 应用中
    const bool bIsAvailable = UE::ConcertInsightsVisualizer::IConcertInsightsVisualizerModule::IsAvailable();
    
    if (bIsAvailable)
    {
        UE_LOG(LogTemp, Log, TEXT("Concert Insights Visualizer 模块已加载，相关追踪可视化轨道可用。"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Concert Insights Visualizer 模块未加载。请确保在 Insights 插件设置中启用它。"));
    }
}
```

## 模块依赖

此插件本身没有特殊的公共模块依赖。它的构建依赖于 Insights 和 Concert 的内部/私有模块。

| 模块 | 用途 |
|---|---|
| `TraceInsights` | Insights 的核心分析和 UI 扩展框架 |
| `TraceAnalysis` | 用于分析 `.utrace` 文件的核心库 |
| `ConcertTransport` | 提供 Concert 传输层和本文档提到的追踪宏 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新版 `UE_LOGF`。 |
| 2025-09-12 | `fd5c41be` | Addressing instances "ignoring return value of function declared with 'nodiscard' attribute" issue f | 修复了若干处忽略 `nodiscard` 属性返回值的问题。 |
| 2024-07-31 | `3d862482` | Fix slowing down Unreal Insights due to ConcertInsights aggregating on the game thread. | 修复了因在游戏线程进行聚合分析导致 Insights 卡顿的性能问题。 |
| 2024-06-27 | `de0f403b` | Fixed missing copyright boilerplate (extra empty line on the top of the header file). | 修复了头文件中缺失或错误的版权声明。 |
| 2024-06-27 | `a1810e80` | [Insights] | （Insights 相关改动，具体内容从哈希推断为早期功能提交）。 |

### 维护评价

该插件创建于 2024 年 5 月，属于较新的实验性功能。从提交历史看，它仍在被积极维护：最近的更新（2025年9月）修复了代码质量问题，而更早的重要更新（2024年7月）解决了关键的性能问题。这表明 Epic 的开发团队在持续关注和改进此工具。

**推荐使用**：对于正在使用 UE5 多用户编辑功能并需要深入分析网络同步行为和性能的团队，这是一个强大且官方支持的诊断工具。虽然标记为实验性且默认不启用，但其功能明确，近期有实质性更新，可以放心用于开发和调试阶段。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertInsights/ConcertInsightsVisualizer)
-   官方文档：此插件暂无独立的官方文档页面。使用说明可参考插件源码中的 `README.txt` 文件（位于插件根目录）。
-   测试用例：该插件没有提供独立的测试用例文件。其功能验证主要通过手动在 Unreal Insights 中加载包含相关追踪事件的 `.utrace` 文件进行。