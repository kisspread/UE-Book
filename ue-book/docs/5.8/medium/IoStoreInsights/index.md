# IoStore Insights

> Allows capturing IoStore activity via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | IoStore 分析器 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `IoStoreInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2024-09-13 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/IoStoreInsights) | |

## 用途

此插件为 Unreal Insights 添加了专门用于分析 **IoStore**（UE5 的资产存储系统）性能的追踪功能。它不是一个直接应用于游戏逻辑的插件，而是一个**性能分析工具**，用于捕获和可视化引擎内部 IoStore 子系统的所有 I/O 请求活动。

通过此插件，开发者可以在 Unreal Insights 的时序视图中直接观察：
- 资产加载过程中哪些数据块被请求读取
- 每个读取请求的耗时、大小和状态（成功/失败）
- 不同后端存储（如本地磁盘、Pak 文件等）的活动
- 读取请求的并发情况和时间分布

它解决了**诊断资产加载性能瓶颈**的核心问题，帮助开发者理解 I/O 层面的加载模式，而不是停留在“资产加载慢”的模糊结论上。

## 使用场景

- **优化加载时间**：你的项目加载关卡时间过长，需要分析具体是哪些资产的哪些数据块在加载过程中耗时过长。
- **分析 I/O 瓶颈**：你怀疑磁盘读取是性能瓶颈，需要查看请求的大小分布、并发情况和后端活动。
- **调试加载失败**：资产加载偶尔失败，需要追踪具体是哪个请求在什么时间点、哪个线程上失败了。
- **研究加载模式**：你想了解引擎的资产加载机制，通过实际追踪数据来学习。

## 蓝图用法

**此插件不提供蓝图 API。** 它完全运行在 Unreal Insights 分析程序内部，其功能是通过 Insights 的 UI 和扩展系统提供的。

## C++ 用法

此插件的核心是作为 **Trace Services 模块** 扩展 Insights 的分析能力。开发者通常不需要直接调用其 API，而是通过启用追踪和在 Insights UI 中查看结果。

### 核心接口

插件公开的核心 API 位于 `IIoStoreInsightsProvider.h`，用于从分析会话中读取已捕获的 IoStore 活动数据：

```cpp
#include "IIoStoreInsightsProvider.h"

// 在你的分析代码中获取 IoStore 活动提供者
void AnalyzeIoStoreActivity(const TraceServices::IAnalysisSession& Session)
{
    const UE::IoStoreInsights::IIoStoreInsightsProvider* IoStoreProvider = 
        UE::IoStoreInsights::ReadIoStoreInsightsProvider(Session);
    
    if (IoStoreProvider)
    {
        // 枚举所有 IoStore 读取请求及其活动时间线
        IoStoreProvider->EnumerateIoStoreRequests(
            [&](const UE::IoStoreInsights::FIoStoreRequest& Request, 
                const UE::IoStoreInsights::IIoStoreInsightsProvider::Timeline& Timeline)
            {
                // 处理每个请求及其活动时间线
                UE_LOG(LogTemp, Log, TEXT("Request for Chunk %u, Offset %llu"), 
                       Request.ChunkIdHash, Request.Offset);
                
                // 遍历该请求的所有活动（读取事件）
                Timeline.EnumerateEvents(-DBL_MAX, DBL_MAX, 
                    [&](double StartTime, double EndTime, 
                        UE::IoStoreInsights::FIoStoreActivity* Activity)
                    {
                        // 活动数据包含耗时、实际大小、后端名称等
                        UE_LOG(LogTemp, Log, TEXT("  Read: %.3fms, Size: %llu"), 
                               (EndTime - StartTime) * 1000.0, Activity->ActualSize);
                        return TraceServices::EEventEnumerate::Continue;
                    });
                
                return true; // 继续枚举
            });
    }
}
```

### 活动类型枚举

插件定义了两种基本的 IoStore 活动类型：

```cpp
enum class EIoStoreActivityType : uint8
{
    Request_Pending, // 请求已创建，等待处理
    Request_Read,    // 正在执行读取操作
    Count,
    Invalid = Count
};
```

## Demo 示例

由于此插件是分析工具，没有独立的运行时示例。使用流程如下：

1.  **启用追踪**：在命令行或项目设置中启用 IoStore 追踪：
    ```
    -Trace=Iostore -iostoretrace
    ```

2.  **运行项目**：正常运行你的 UE5 项目或编辑器，执行需要分析的资产加载操作。

3.  **打开 Unreal Insights**：连接到正在运行的实例，或加载保存的追踪文件。

4.  **查看分析结果**：
    *   在时序视图中，找到 "IoStore Activity" 轨道。
    *   使用 "IoStore Analysis" 面板查看读取大小分布直方图。
    *   筛选、点击事件查看详细信息。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TraceServices` | 分析追踪数据的基础框架 |
| `InsightsCore` | Insights 工具的核心 UI 和框架 |
| `InsightsTiming` | Insights 时序视图相关的扩展 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版本格式 |
| 2026-02-27 | `81ba13b5` | [IoStoreInsights] Fixed deprecated FName for FTableTreeNode constructor. | 修复 FTableTreeNode 构造函数的废弃 FName 参数 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎代码现代化，将空析构函数改为 `= default` |
| 2025-10-01 | `1938c6a2` | Slate Dynamic Invalidation - ProgressBar | Slate 框架更新，影响进度条控件 |
| 2024-11-21 | `0f7f4cfb` | Remove assert for duplicate IoStore activities | 移除重复 IoStore 活动的断言，提高稳定性 |

### 维护评价

IoStoreInsights 是一个相对较新的插件（约 1 年历史），属于 Epic 官方维护的性能分析工具。

*   **活跃维护**：最近 6 个月内有多次更新，包括代码现代化和缺陷修复。
*   **功能稳定**：作为 Insights 的扩展，其核心架构已稳定。
*   **推荐使用**：对于需要进行深入资产加载性能分析的项目，特别是 I/O 层面的优化，此插件是**强烈推荐**使用的官方工具。它直接集成在引擎的分析管线中，能提供最准确和详细的底层数据。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/IoStoreInsights)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/IoStoreInsights/Tests)（如果存在）