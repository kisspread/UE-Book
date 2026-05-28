# Insights Data Source Filters

> Source data filtering for Unreal Insights.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 数据源过滤器 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器UI资产） |
| 模块 | `SourceFilteringCore` (Runtime), `SourceFilteringTrace` (Runtime), `SourceFilteringEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 👴 老古董（推测超过5年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering) | |

## 用途

本插件为 Unreal Insights 性能分析工具提供数据源过滤功能。其核心价值在于允许开发者定义和管理过滤器，并在 Insights 的 UI 中应用这些过滤器，从而能够有选择性地查看和分析来自不同子系统（如特定 Actor、组件或特定类型的追踪事件）的性能数据。这极大地提升了在复杂场景中定位性能瓶颈的效率，避免了被海量无关追踪信息淹没的问题。

简单来说，它解决了 **“在 Unreal Insights 的大量追踪数据中，如何快速、精准地聚焦于你关心的那部分数据”** 这一问题。

## 使用场景

-   当你使用 Unreal Insights 分析一个大型游戏项目的性能时，数据源过多导致界面混乱、分析困难。
-   你需要专注于分析 AI 系统的性能，希望只查看所有与 AI 相关的追踪事件和数据。
-   你在调试一个特定角色的动画性能问题，希望过滤掉其他所有角色和系统的追踪数据。
-   你希望为团队创建一套标准的过滤规则，用于日常的性能监控和回归测试。

## 模块列表

本插件由以下三个模块组成，分别负责核心逻辑、数据追踪和编辑器集成：

| 模块 | 类型 | 说明 | 文档 |
|---|---|---|---|
| `SourceFilteringCore` | Runtime | 定义过滤器框架的核心基类与接口。 | [SourceFilteringCore.md](SourceFilteringCore.md) |
| `SourceFilteringTrace` | Runtime | 负责在 Trace 系统中实际执行数据过滤的逻辑。 | [SourceFilteringTrace.md](SourceFilteringTrace.md) |
| `SourceFilteringEditor` | Editor | 提供在编辑器内配置和管理过滤器的用户界面。 | [SourceFilteringEditor.md](SourceFilteringEditor.md) |

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/TraceSourceFiltering)
-   依赖插件: `GameplayInsights`