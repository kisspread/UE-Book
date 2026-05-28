# Animation Insights

> Allows debugging of animation systems via Unreal Insights

| 属性 | 值 |
|---|---|
| 中文名 | 动画洞察 |
| 分类 | Insights |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInsights` (Runtime), `GameplayInsightsEditor` (Runtime), `RewindDebugger` (Runtime), `RewindDebuggerRuntime` (Runtime), `RewindDebuggerVLog` (Runtime), `RewindDebuggerVLogRuntime` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-15 |
| 年龄标签 | 🆕（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights) | |

## 用途

此插件提供了一个基于时间线的调试工具——回放调试器（Rewind Debugger），用于在 Unreal Insights 中回放和分析游戏运行时的各类数据。它超越了单纯的动画调试，能够追踪和可视化游戏对象状态、动画数据（如骨骼姿态）、动画节点图、变量值以及虚拟日志（VLog）等多种信息，支持在时间线上前后滚动查看历史数据，是性能分析和问题排查的强大工具。

## 使用场景

- 你需要调试复杂的动画蓝图或状态机，观察动画节点之间的数据流动和姿态结果
- 你需要分析游戏对象在特定时间点的属性状态，而不仅仅是瞬时快照
- 你需要回放并检查游戏过程中的事件序列，例如输入、动画通知或自定义日志
- 你需要为美术或策划提供一种直观的工具，让他们能查看动画和游戏状态的运行时表现
- 你需要结合 Unreal Insights 的性能数据（CPU、内存等）与游戏逻辑数据进行关联分析

## 模块概览

此插件由六个模块构成，共同组成了回放调试器及其运行时数据收集功能。

| 模块 | 类型 | 说明 |
|---|---|---|
| [GameplayInsights](GameplayInsights.md) | Runtime | 核心运行时模块，负责收集游戏对象和动画的调试数据并提供给 Insights。 |
| [GameplayInsightsEditor](GameplayInsightsEditor.md) | Runtime | 编辑器扩展模块，为回放调试器提供用户界面（如时间线、细节面板）。 |
| [RewindDebugger](RewindDebugger.md) | Runtime | 回放调试器核心逻辑，管理时间线、数据回放和插件扩展点。 |
| [RewindDebuggerRuntime](RewindDebuggerRuntime.md) | Runtime | 回放调试器的运行时基础支持，包含数据录制和回放的基础架构。 |
| [RewindDebuggerVLog](RewindDebuggerVLog.md) | Runtime | 虚拟日志（VLog）的调试器扩展，用于在时间线上显示自定义日志信息。 |
| [RewindDebuggerVLogRuntime](RewindDebuggerVLogRuntime.md) | Runtime | 虚拟日志的运行时数据收集模块。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/GameplayInsights)
- [模块文档](GameplayInsights/GameplayInsights.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a3d17a57` | fix Rewind Debugger eyedropper to cancel when reattaching player control while it's active | 修复了在拾取器激活期间重新附加玩家控制器时的取消逻辑。 |
| 2026-05-13 | `ec80c6b8` | [RewindDebugger] Add programmable scrub and view-centring surface on `IRewindDebugger`. | 在接口上添加了可编程的滚动和视图居中功能，增强了扩展性。 |
| 2026-04-28 | `7805b240` | Rewind Debugger toolbar UX pass. | 对回放调试器的工具栏进行了用户体验优化。 |
| 2026-04-15 | `4b250a9d` | [RewindDebugger] | 提交信息不完整，可能为内部小调整。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 UE_LOG 迁移到 UE_LOGF，统一日志框架。 |

### 维护评价

此插件处于**活跃维护**状态。尽管创建于2019年，但近期（2026年）仍有频繁且实质性的功能更新和优化，例如改进用户交互、增强API可扩展性以及代码现代化。它不是一个实验性项目，已成为 Unreal Insights 生态中进行深度游戏逻辑和动画调试的标准工具。对于需要在开发后期进行复杂调试的团队，强烈推荐使用。