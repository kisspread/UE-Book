# Slate Insights

> Allows debugging of Slate via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | Slate 调试洞察 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SlateInsights` (EditorAndProgram) |
| 实验性 | 否 |
| 创建时间 | 2020-09-24 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Slate/SlateInsights) | |

## 用途

这个插件为 Unreal Insights 工具添加了 Slate UI 框架的专门调试和分析能力。它通过 Trace 系统捕获 Slate 应用程序运行时的关键性能数据和事件（如控件更新、失效、绘制步骤等），并将这些数据可视化地展示在 Insights 的时序分析界面中。

该插件的存在是为了解决在复杂 UI 项目中调试 Slate 性能瓶颈（如过度绘制、不必要的失效、布局计算开销等）的问题，使开发者能够直接在 Insights 时间轴中查看、分析和诊断 Slate 的内部工作流程。

## 使用场景

- 你的游戏或应用程序使用 Slate UI 框架，并且遇到了 UI 性能问题（卡顿、掉帧） → 使用 Slate Insights
- 你需要分析某个特定 UI 控件的更新、失效或绘制耗时 → 使用 Slate Insights
- 你想在 Unreal Insights 中查看 Slate 应用程序每帧的控件计数、更新计数、失效计数等统计信息 → 使用 Slate Insights
- 你需要追踪 UI 控件失效的调用栈或脚本调用链 → 使用 Slate Insights

## 蓝图用法

该插件是一个 **EditorAndProgram** 类型的模块，主要用于扩展 Unreal Insights 工具的功能，不直接提供运行时蓝图节点。其功能通过 Insights 界面操作触发。

## C++ 用法

该插件的核心是通过 `TraceServices::IModule` 和 `UE::Insights::Timing::ITimingViewExtender` 接口扩展 Insights。以下为关键用法概述。

### 头文件引入

```cpp
#include "SlateInsightsModule.h"
```

### 基本用法

该插件会自动注册到 Insights 中。要启用 Slate 追踪，需要在启动引擎时添加命令行参数 `-Trace=SlateTrace`，或者在 Insights 工具中连接目标后，通过 UI 开启 Slate 追踪通道。

其核心是 `FSlateAnalyzer`，它负责解析 Slate 追踪事件并将其传递给 `FSlateProvider` 进行存储和索引。

### 进阶用法

如果你想扩展或自定义 Slate 追踪的分析逻辑，可以参考 `FSlateAnalyzer` 的实现。它通过 `OnEvent` 函数接收不同的追踪事件路由（如 `RouteId_WidgetUpdated`），并将解析后的消息（如 `FWidgetUpdatedMessage`）存入 `FSlateProvider`。

`FSlateProvider` 是数据存储的核心，它维护了多个时间线（Timelines），例如：
- `FApplicationTickedTimeline`：存储应用每帧的统计信息（控件数、绘制数等）。
- `FWidgetUpdatedTimeline`：存储单个控件更新的事件。
- `FWidgetInvalidatedTimeline`：存储控件失效事件。

## Demo 示例

该插件主要作为工具扩展，没有直接的运行时示例。其功能集成在 Unreal Insights 工具中。

一个典型的工作流是：
1. 编译并启动项目，命令行添加 `-Trace=SlateTrace` 或 `-Trace=slatetrace`。
2. 打开 Unreal Insights 工具并连接到目标进程。
3. 在 Insights 的“Timing Insights”面板中，通过过滤器菜单找到并启用 Slate 相关的轨道（Track），如“Slate Frame Stats”或“Widget Update Steps”。
4. 在时间轴上选择一段 Slate 活动（如帧），在“Frame Schematic”面板中查看该帧内失效或更新的控件列表及其耗时。

## 模块依赖

该插件的 `Build.cs` 未提供，但根据源码头文件分析，其依赖关系如下。请注意，由于其 `ProgramAllowList` 仅为 `UnrealInsights`，这些依赖主要适用于 Insights 工具程序本身。

| 模块 | 用途 |
|---|---|
| `TraceAnalysis` | 核心追踪事件分析框架 |
| `TraceInsights` | Insights 工具的核心框架，用于提供时序视图扩展 |
| `InsightsCore` | Insights 工具的核心类型和接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2024-06-27 | `a1810e80` | [Insights] | Insights 相关的更新 |
| 2024-06-20 | `1d4beb26` | [Insights] Massive refactoring of TraceInsights module: | Insights 模块的大规模重构 |
| 2024-05-02 | `e0464783` | Slate: Deprecate SListView::ItemHeight and STreeViewItemHeight... | 废弃了 SListView/STreeView 的一些旧属性，可能影响 UI 控件布局 |
| 2024-01-23 | `104c0f24` | Fixed up more bool-taking calls to take EAllowShrinking instead. | 修复了更多函数签名，将布尔参数替换为 EAllowShrinking 枚举 |
| 2023-12-20 | `eaff1e17` | Fix Slate Frame View not working when opened after insights timeline | 修复了在 Insights 时间轴之后打开 Slate 帧视图不起作用的问题 |

### 维护评价

- **创建时间**：2020 年创建，相对较新。
- **维护频率**：在 2023 年和 2024 年仍有实质性更新和 bug 修复，表明 Epic 仍在维护此工具。
- **状态**：**活跃维护中**。作为 Unreal Insights 工具套件的一部分，随着 Insights 的持续改进，Slate Insights 也会同步更新。
- **已知限制**：这是一个工具插件，仅在 Unreal Insights 程序中可用，不提供运行时蓝图 API。需要手动启用追踪并使用命令行参数。
- **推荐使用**：**推荐**。对于任何使用 Slate UI 并关注性能的项目，这是进行深度 UI 性能分析的必备工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Slate/SlateInsights)
- 官方文档：无（插件 .uplugin 未提供 DocsURL）
- 测试用例：无（在提供的信息中未发现测试文件）