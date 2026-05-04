# HTTP Insights

> Allows capturing HTTP traffic（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `HttpInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2026-02-05 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HttpInsights) | |

## 用途

HttpInsights 是一个专为 Unreal Insights 工具设计的 HTTP 流量分析模块。它并非一个通用的 HTTP 客户端或服务器插件，而是一个**数据模型和分析后端**，用于捕获、结构化并可视化引擎内部（特别是 IAX 流媒体）的 HTTP 请求生命周期数据。其核心价值在于将原始的 HTTP 事件（如请求开始、分块接收、完成）转化为 Insights 时间线视图中可交互的图表和详情面板，帮助开发者诊断网络性能瓶颈、请求失败原因以及资源加载模式。

## 使用场景

- 你正在使用 Unreal Insights 分析游戏或应用的性能，需要深入查看 HTTP 请求的时序、状态码和数据传输细节。
- 你的项目使用了 IAX (Interactive Audio eXtensions) 或类似的流媒体技术，需要监控和调试其底层的 HTTP 流量。
- 你需要一个可视化的工具来关联 HTTP 请求活动与其他引擎性能指标（如 CPU、GPU、内存）。

## 蓝图用法

无。此插件不提供任何蓝图可调用的函数或属性。它是一个纯数据模型和分析模块，其功能通过 Unreal Insights 程序的用户界面呈现。

## C++ 用法

此插件主要定义了用于 Insights 分析的数据结构和模型，不提供面向游戏逻辑的公开 C++ API。其主要用途是作为 Unreal Insights 程序的一个分析插件。

### 头文件引入

```cpp
// 如果你需要在 Insights 插件开发中引用其数据模型
#include "HttpInsights/Model.h"
```

### 基本用法

该模块的核心是定义了一系列数据结构，用于在 Insights 分析会话中表示 HTTP 事件。这些结构体通常由底层的 HTTP 追踪系统填充，并由 Insights 的 UI 消费。

```cpp
// 来源: Source/Private/Model.h
// 定义了一个 HTTP 请求的完整信息
struct FHttpRequest
{
    const FHttpDispatcher& Dispatcher; // 关联的 HTTP 分发器
    double StartTime = 0.0;           // 请求开始时间
    double CompletionTime = 0.0;      // 请求完成时间
    uint32 StatusCode = 0;            // HTTP 状态码
    uint32 ContentLength = 0;         // 内容长度
    FString Host;                     // 主机名
    FString Url;                      // 请求 URL
    // ... 其他字段如分块范围、分类等
};

// 定义了一个 HTTP 分发器（如某个流媒体会话）
struct FHttpDispatcher
{
    const uint64 Handle = 0;
    const FString Name;
};
```

### 进阶用法

模块通过一系列事件结构体（如 `FHttpRequestStarted`, `FHttpChunkRangeAdded`, `FHttpRequestCompleted`）来记录 HTTP 活动的生命周期。这些事件被序列化到 Insights 的追踪流中，随后由 Insights 的 HTTP Insights 面板进行解析和可视化。

## Demo 示例

由于此插件是 Insights 的分析模块，其“使用”体现在 Unreal Insights 程序中。以下是一个最小化的模块注册示例，展示了如何将此分析模块集成到 Insights 程序中。

```cpp
// MyInsightsPlugin.h
#pragma once
#include "Modules/ModuleManager.h"

class FMyInsightsPluginModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyInsightsPlugin.cpp
#include "MyInsightsPlugin.h"
#include "HttpInsights/ModuleInterface.h" // 引入 HttpInsights 模块接口

void FMyInsightsPluginModule::StartupModule()
{
    // 在此，Insights 程序会加载并初始化 HttpInsights 模块
    // 通常不需要手动操作，模块系统会自动处理
}

void FMyInsightsPluginModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyInsightsPluginModule, MyInsightsPlugin)
```

## 模块依赖

从 `HttpInsights.Build.cs` 的依赖项分析，此插件深度集成于 Unreal Insights 的分析框架。

| 模块 | 用途 |
|---|---|
| `TraceServices` | 提供核心的追踪分析服务和会话管理，是构建 Insights 分析模块的基础。 |
| `Insights` | Unreal Insights 程序的核心框架，提供 UI 集成点和分析上下文。 |

## 维护状态

### 近期更新

- `35e60df1` 2026-04-14 — Migrate UE_LOG to UE_LOGF. (将日志宏迁移到新的 UE_LOGF 格式)
- `9dc063f2` 2026-02-12 — Remove mismatched loc text define (移除了不匹配的本地化文本定义)
- `932878c1` 2026-02-06 — Added support for filtering HTTP request(s) based on the selected time range in Insights timing view (增加了在 Insights 时间线视图中基于选定时间范围过滤 HTTP 请求的功能)

### 维护评价

该插件创建于 2026 年 2 月，是一个非常新的模块。从 git 历史看，在创建后的一个月内有多次提交，包括功能增强（时间范围过滤）和代码维护（日志迁移、清理），表明它在发布初期处于**活跃开发**状态。作为 Epic 官方维护的实验性 Insights 模块，其质量和与引擎的集成度有保障。目前没有发现已知的重大问题或限制。**推荐**有 HTTP 流量分析需求的开发者使用，特别是结合 IAX 流媒体调试时。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/HttpInsights)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的信息中发现独立的测试文件)