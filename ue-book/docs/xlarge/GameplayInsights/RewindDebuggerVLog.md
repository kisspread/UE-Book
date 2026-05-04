# Animation Insights

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

GameplayInsights 是一个**大型调试工具插件**，将动画系统和游戏玩法的调试数据集成到 Unreal Insights 追踪系统中。它包含两个核心子系统：

1. **GameplayInsights**：将动画状态机、动画蓝图、属性值等运行时数据写入 Unreal Insights 追踪通道，支持在 Insights 工具中可视化分析动画系统的性能和行为。

2. **RewindDebugger（倒带调试器）**：提供时间回溯调试功能，允许开发者在编辑器中"倒带"回放游戏过程，逐帧检查动画状态、可视化日志（Visual Logger）等数据。这是 Unreal Insights 的 `SupportedPrograms` 中列出的核心功能。

插件默认禁用（`EnabledByDefault: false`），需要手动启用后才能在 Unreal Insights 和编辑器中使用。

## 模块总览

| 模块 | 类型 | 职责 |
|---|---|---|
| `GameplayInsights` | Runtime | 核心追踪通道定义，将动画数据写入 Insights 追踪流 |
| `GameplayInsightsEditor` | Runtime | 编辑器集成，提供 Insights 中的动画调试视图 |
| `RewindDebugger` | Runtime | 倒带调试器 UI 和编辑器工具 |
| `RewindDebuggerRuntime` | Runtime | 倒带调试器的运行时数据采集 |
| `RewindDebuggerVLog` | Runtime | 将 Visual Logger 数据集成到倒带调试器（Trace 分析端） |
| `RewindDebuggerVLogRuntime` | Runtime | Visual Logger 运行时数据写入 |

## 使用场景

- 你在开发动画密集型游戏（如动作游戏、格斗游戏），需要分析动画蓝图的性能瓶颈 → 用 GameplayInsights 在 Unreal Insights 中查看动画状态机的耗时
- 你需要回溯调试某个动画状态转换问题，但断点调试无法重现 → 用 RewindDebugger 倒带回放逐帧检查
- 你想在 Unreal Insights 中查看 Visual Logger 的时间线数据 → 用 RewindDebuggerVLog 模块
- 你在做性能优化，需要同时查看 CPU/GPU 性能和动画系统状态 → 启用此插件后在 Insights 中关联分析

## 蓝图用法

本插件主要面向**编辑器工具和 Unreal Insights 集成**，不提供常规的蓝图节点。其功能通过以下方式访问：

- **Unreal Insights 工具**：启用插件后，在 Unreal Insights 的 Trace 通道中会出现动画相关的追踪通道
- **RewindDebugger 面板**：在编辑器中通过 Window → Developer Tools 打开
- **命令行参数**：通过 `-trace=animation` 等参数启用追踪

## C++ 用法

### 头文件引入

```cpp
#include "IVisualLoggerProvider.h"
```

### 基本用法 - 读取 Visual Logger 时间线

`IVisualLoggerProvider` 是 TraceServices 的 Provider 接口，用于在 Unreal Insights 分析端读取 Visual Logger 数据：

```cpp
// 来源: Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLog/Public/IVisualLoggerProvider.h

// 获取 Provider 后，读取某个对象的 Visual Log 时间线
const IVisualLoggerProvider* Provider = /* 从 AnalysisSession 获取 */;

Provider->ReadVisualLogEntryTimeline(ObjectId, [](const IVisualLoggerProvider::VisualLogEntryTimeline& Timeline)
{
    // 遍历时间线中的每个 FVisualLogEntry
    Timeline.EnumerateEvents(0, Timeline.GetEventCount(), 
        [](double Time, const FVisualLogEntry& Entry)
        {
            // 处理每个日志条目
            // Entry 包含日志文本、位置、形状等信息
        });
});
```

### 遍历日志分类

```cpp
// 来源: Engine/Plugins/Animation/GameplayInsights/Source/RewindDebuggerVLog/Public/IVisualLoggerProvider.h

Provider->EnumerateCategories([](const FName& CategoryName)
{
    // 处理每个日志分类
    UE_LOG(LogTemp, Log, TEXT("Found VLog category: %s"), *CategoryName.ToString());
});
```

## 模块依赖

由于本插件包含 6 个模块，以下列出各模块的**独特依赖**（省略 Core/Engine 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `TraceServices` | Unreal Insights 的追踪服务框架，提供 Provider/Timeline 接口 |
| `TraceAnalysis` | 追踪数据分析框架 |
| `VisualLogger` | Visual Logger 系统，提供 FVisualLogEntry 等类型 |
| `GameplayInsights` | 本插件的核心模块，其他模块依赖它 |

## 维护状态

### 近期更新

```
- 0b295b01ed6d [RewindDebugger] added missing shape type
- fcb1f434851f Fix typo in comment, ty BugHawk
- e964babb2d08 Fix non unity build
```

最近的更新主要是小修复：补充了缺失的形状类型、修复注释拼写错误、修复非 Unity 构建问题。没有功能性大改动。

### 维护评价

- **创建时间**：2019 年 10 月，已有约 6 年历史
- **维护状态**：**维护中** — 仍有零星更新，但以修复为主
- **成熟度**：作为 Epic 官方的动画调试工具，功能已相对稳定
- **注意事项**：
  - 默认禁用，说明 Epic 认为这不是所有项目都需要的功能
  - 仅支持 `UnrealInsights` 程序，不适用于独立游戏运行时
  - 所有模块标记为 Runtime 类型，但实际主要在编辑器/Insights 工具中使用
- **推荐度**：如果你需要深度动画调试和性能分析，推荐启用；对于简单项目可以忽略

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GameplayInsights)
- [Unreal Insights 官方文档](https://docs.unrealengine.com/5.7/en-US/unreal-insights-in-unreal-engine/)