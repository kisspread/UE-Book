# Field Notification Trace

> Add support to trace field notification object.

| 属性 | 值 |
|---|---|
| 中文名 | 字段通知追踪 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FieldNotificationTrace` (Runtime), `FieldNotificationTraceEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

为 UE5 的 Field Notification 系统提供**运行时追踪能力**，将字段值变化事件记录到 Unreal Insights Trace 系统中，并在 **Rewind Debugger** 时间线上可视化展示。

Field Notification 是 UE5 中用于 UI 属性绑定和 MVVM 模式的核心机制（`FieldNotify` 宏标记的属性）。当这些属性发生变化时，本插件会生成对应的 trace 事件，方便开发者回溯调试数据绑定链路中的问题——比如"某个 Widget 为什么没有更新"或"属性变化是否被正确广播"。

**为什么存在**：Field Notification 本身不提供任何调试工具。在复杂 UI 系统中，属性变化可能来自多个源（用户输入、网络同步、逻辑计算等），缺少可视化追踪会让调试变得极其困难。本插件填补了这一空白。

## 使用场景

- 你在使用 **UMG + Field Notify** 构建响应式 UI，需要确认属性变化是否正确触发了 Widget 更新
- 你在用 **Gameplay Insights / Rewind Debugger** 分析帧数据，希望在时间线上看到 Field Notification 事件
- 你在调试 MVVM 绑定链路，需要回溯某个字段值在什么时候被谁修改
- 你在排查数据驱动 UI 的性能问题，需要追踪 FieldNotify 回调频率

## 模块说明

| 模块 | 类型 | 说明 |
|---|---|---|
| [FieldNotificationTrace](FieldNotificationTrace.md) | Runtime | 核心追踪逻辑，捕获 Field Notification 属性变化并写入 Trace 流 |
| [FieldNotificationTraceEditor](FieldNotificationTraceEditor.md) | Editor | Rewind Debugger 集成，在时间线上渲染 Field Notification 追踪轨道 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [FieldNotificationTrace 模块文档](FieldNotificationTrace.md)
- [FieldNotificationTraceEditor 模块文档](FieldNotificationTraceEditor.md)

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与 Mass 框架调试相关的改动 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | RewindDebugger 集成更新 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 将 TraceService::Frame 的包含头文件替换为前向声明，减少编译依赖 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us | 修复多个调试轨道在 Rewind Debugger 中不显示的问题 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退之前的改动 |

### 维护评价

- **创建时间**：2024 年 5 月，相对年轻的插件
- **更新频率**：活跃维护中，2026 年初仍有功能性更新和 bug 修复
- **状态标记**：`IsBetaVersion=true`，`EnabledByDefault=false`——仍在实验阶段，需手动启用
- **依赖关系**：强依赖 GameplayInsights 插件，属于 Unreal Insights 生态的一部分
- **推荐程度**：⚠️ 如果你在使用 Field Notification + Rewind Debugger 工作流，这是一个很有价值的调试辅助工具；但作为 beta 功能，API 可能变动