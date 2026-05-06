# IoStore Insights

> Allows capturing IoStore activity via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | IoStore 活动分析 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `IoStoreInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2024-10-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/IoStoreInsights) | |

## 用途

IoStore Insights 是一个 **Unreal Insights 扩展插件**，用于捕获和可视化 **IoStore（I/O 存储系统）** 在游戏运行过程中的底层 I/O 活动。它通过 Trace 通道收集 IoStore 请求的创建、开始、完成、失败等事件，并在 Insights 的时序视图中以时间线形式展示每条 I/O 请求的生命周期，帮助开发者分析磁盘读取性能、识别瓶颈。

该插件解决的核心问题：在 Unreal Engine 中，资源加载和流式处理经常产生大量 I/O 请求，但传统的 Profiling 工具很难直接关联到具体的 I/O 请求、耗时和失败原因。IoStore Insights 填补了这一空白，让开发者能够像分析渲染/逻辑帧一样分析 I/O 行为。

## 使用场景

- **分析资源加载性能**：当游戏出现卡顿、加载时间过长时，通过 Insigths 查看 IoStore 活动，定位是哪些资源读取耗时高、是否发生死锁或失败。
- **排查 I/O 死锁或泄漏**：请求长时间未完成或失败时，可快速定位具体请求的 ChunkID、偏移量、大小、后端名称等信息。
- **优化打包后加载策略**：比较不同打包格式（如 IoStore vs PakFile）下的 I/O 行为。
- **开发自定义 I/O 后端**：如果使用自定义存储后端，可通过 IoStore Insights 验证其正确性与性能。

## 蓝图用法

该插件不提供公开的蓝图节点。所有功能内置在 Unreal Insights 分析工具中，通过编辑器菜单启动。

### 启用与操作

1. 打开 **Unreal Insights**（编辑器菜单：`工具 → 分析工具 → Unreal Insights`）。
2. 在 Trace 连接设置中确保捕获了 **IoStore** 事件（通常默认开启）。
3. 录制或加载一段 Trace。
4. 在 Timing View 中，找到 **IoStore Activity** 轨道，展开后可看到按时间轴排列的 I/O 事件（Pending 状态和 Read 状态用不同颜色区分）。
5. 点击具体事件可查看详细信息：请求的 ChunkId、ChunkType、偏移、大小、后端名称、耗时、是否失败等。

## C++ 用法

### 头文件引入

```cpp
#include "IIoStoreInsightsProvider.h"
#include "TraceServices/Model/AnalysisSession.h"
```

### 基本用法

本插件主要作为 Insights 内部 Provider，在自定义 Trace 分析过程中通过 `ReadIoStoreInsightsProvider` 函数获取只读接口，然后枚举所有 IoStore 请求及其活动时间线。

```cpp
// 假设在某个分析器内部已经拥有对 IAnalysisSession 的引用
using namespace UE::IoStoreInsights;

const IIoStoreInsightsProvider* Provider = ReadIoStoreInsightsProvider(Session);
if (Provider)
{
    Provider->EnumerateIoStoreRequests(
        [](const FIoStoreRequest& Request, const IIoStoreInsightsProvider::Timeline& Timeline) -> bool
        {
            // 遍历每个请求的详细信息
            UE_LOG(LogTemp, Log, TEXT("Request Index: %u, Package: %s, Offset: %llu, Size: %llu"),
                Request.IoStoreRequestIndex,
                Request.PackageName ? Request.PackageName : TEXT("None"),
                Request.Offset,
                Request.Size);

            // 遍历该请求对应的时间线（Pending 和 Read 活动）
            Timeline.EnumerateEvents(0.0, FLT_MAX,
                [](double StartTime, double EndTime, uint32 Depth, const FIoStoreActivity* Activity)
                {
                    if (Activity)
                    {
                        UE_LOG(LogTemp, Log, TEXT("  Activity: [%f - %f] Type=%s, Backend=%s, Size=%llu, Failed=%d"),
                            StartTime, EndTime,
                            LexToString(Activity->ActivityType),
                            Activity->BackendName ? Activity->BackendName : TEXT("None"),
                            Activity->ActualSize,
                            (int)Activity->Failed);
                    }
                });

            return true; // 继续枚举下一个请求
        });
}
```

**来源**: `Source/IoStoreInsights/Public/IIoStoreInsightsProvider.h`（接口定义）  
**测试用例**: 无独立测试，但可参考插件自身的分析器实现（`FIoStoreInsightsAnalyzer`）。

### 进阶用法

#### 自定义分析器集成

若要扩展 IoStore Insights 的功能，可以创建自己的 Trace 分析器，并依赖 `IoStoreInsights` 模块的 Provider。例如，在 `OnEvent` 中解析自定义 Trace 事件并与 IoStore 请求关联。

```cpp
// 自定义分析器示例
class FCustomIoAnalyzer : public UE::Trace::IAnalyzer
{
public:
    FCustomIoAnalyzer(TraceServices::IAnalysisSession& InSession)
        : Session(InSession)
    {
        // 通过 Provider 访问 IoStore 数据
        IoStoreProvider = UE::IoStoreInsights::ReadIoStoreInsightsProvider(Session);
    }

    virtual void OnAnalysisBegin(const FOnAnalysisContext& Context) override
    {
        // 注册自定义事件路由
    }

    virtual bool OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context) override
    {
        // 在处理自定义事件时，可以查询 IoStore 请求
        if (IoStoreProvider)
        {
            // 例如获取某个索引的请求
            const auto& Request = IoStoreProvider->GetIoStoreRequest(42);
            // ...
        }
        return true;
    }

private:
    TraceServices::IAnalysisSession& Session;
    const UE::IoStoreInsights::IIoStoreInsightsProvider* IoStoreProvider = nullptr;
};
```

#### 自定义表格视图

插件内部提供了一个 `FIoStoreActivityTable` 和 `SActivityTableTreeView`，可在自己的 Widget 中复用，以展示 IoStore 活动表格（包含包名、偏移、大小、耗时、ChunkId 等列）。参考 `SIoStoreAnalysisTab` 的实现。

## Demo 示例

以下是一个最简单的 C++ 示例，展示如何在分析器初始化时挂载 IoStore Insights Provider 并读取数据。

### Header: `MyIoDemoAnalyzer.h`

```cpp
#pragma once

#include "Trace/Analyzer.h"
#include "TraceServices/Model/AnalysisSession.h"

class FMyIoDemoAnalyzer : public UE::Trace::IAnalyzer
{
public:
    FMyIoDemoAnalyzer(TraceServices::IAnalysisSession& InSession);
    virtual void OnAnalysisBegin(const FOnAnalysisContext& Context) override;
    virtual bool OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context) override;

private:
    TraceServices::IAnalysisSession& Session;
};
```

### Source: `MyIoDemoAnalyzer.cpp`

```cpp
#include "MyIoDemoAnalyzer.h"
#include "IIoStoreInsightsProvider.h"

FMyIoDemoAnalyzer::FMyIoDemoAnalyzer(TraceServices::IAnalysisSession& InSession)
    : Session(InSession)
{
}

void FMyIoDemoAnalyzer::OnAnalysisBegin(const FOnAnalysisContext& Context)
{
    // IoStore Insights 已经被 IoStoreInsightsTraceModule 自动注册。
    // 在 OnAnalysisBegin 之后可以安全访问 Provider。
}

bool FMyIoDemoAnalyzer::OnEvent(uint16 RouteId, EStyle Style, const FOnEventContext& Context)
{
    // 示例：在分析过程中打印 IoStore 请求总数
    if (const auto* Provider = UE::IoStoreInsights::ReadIoStoreInsightsProvider(Session))
    {
        int32 Count = 0;
        Provider->EnumerateIoStoreRequests(
            [&Count](const UE::IoStoreInsights::FIoStoreRequest&, const auto&) -> bool
            {
                ++Count;
                return true;
            });
        UE_LOG(LogTemp, Log, TEXT("Total IoStore requests so far: %d"), Count);
    }
    return true;
}
```

**说明**：此示例假设启用了 IoStore Trace 通道，并且分析会话中已经包含了 IoStore 事件。实际使用时，可将 `FMyIoDemoAnalyzer` 注册到 Trace 分析服务中。

## 模块依赖

无特殊依赖（仅标准 Insights 相关模块）。

## 维护状态

### 近期更新

- 2024-11-21 `0f7f4cfb` — Remove assert for duplicate IoStore activities  
- 2024-10-30 `940b4bfa` — Add Backend Name to the IoStore insights table  
- 2024-10-23 `fe71c420` — Replace bespoke activity table view with an Insights TableTreeView.  
- 2024-10-22 `b96b0061` — Adding custom analysis tab for IoStore insights  
- 2024-10-17 `e4de0f87` — [Trivial] add missing file from previous checkin - fix insights provider name.

### 维护评价

- **创建时间**：2024-10-17（约 9 个月前）。
- **最近更新**：最后一次实质性提交在 2024-11-21，距今约 8 个月。但考虑到插件已基本定型，且没有新的功能需求报告，可认为维护状态正常。
- **活跃度**：当前无已知问题或限制。插件功能相对单一但完整，推荐用于 I/O 性能分析场景。
- **风险**：无。

综合评价：🟢 **维护中**，可使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/IoStoreInsights)
- [官方文档](https://docs.unrealengine.com/5.7/zh-CN/insights-overview/)（Unreal Insights 通用文档，该插件作为其子功能）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/IoStoreInsights)（插件源代码即唯一参考）