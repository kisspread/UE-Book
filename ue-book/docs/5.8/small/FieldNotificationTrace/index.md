# Field Notification Trace

> Add support to trace field notification object.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 字段通知追踪器 |
| 分类 | UI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `FieldNotificationTrace` (Runtime), `FieldNotificationTraceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-24 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace) | |

## 用途

此插件为 UE5 的 UI 框架（如 MVVM）中的字段通知（`FieldNotify`）系统提供了调试支持。它的核心功能是 **在运行时收集并记录字段值的变化事件**，并将这些数据通过 Gameplay Insights 框架集成到 **Rewind Debugger** 中。开发者可以在时间轴上可视化地回放数据流，查看特定属性在游戏运行过程中何时、如何发生变化，从而高效诊断数据绑定和同步问题。

## 使用场景

- 你在使用 UE5 的 MVVM 框架或自定义属性绑定系统构建 UI，遇到数据不同步或更新时机不正确的问题，需要回溯数据流。
- 你需要调试复杂的、跨多个对象的字段依赖关系，想了解属性 A 的变化如何触发属性 B 的连锁更新。
- 你正在使用 **Rewind Debugger** 调试游戏，并希望将 UI 数据的状态变化与游戏逻辑、动画等事件在同一时间线上对齐分析。

## 蓝图用法

此插件主要面向编辑器调试，不直接提供游戏内可调用的蓝图节点。其核心功能通过 **Rewind Debugger** 编辑器面板提供，无公开的可绑定蓝图函数。

## C++ 用法

### 启用插件

此插件默认未启用，需要在项目 `.uproject` 文件中手动添加：
```json
{
    "Plugins": [
        {
            "Name": "FieldNotificationTrace",
            "Enabled": true
        }
    ]
}
```

### 集成到自定义字段通知

此插件会自动为所有实现 `INotifyFieldValueChanged` 接口并使用 `FIELD_NOTIFY` 宏标记的属性添加追踪。你通常无需编写额外代码。只需确保：
1. 启用插件。
2. 确保对象正确实现了字段通知接口。

## Demo 示例

无典型的可运行游戏内示例。此插件为**调试工具**，主要在编辑器中使用。启用后，当你的游戏运行时，打开 **Window -> Developer Tools -> Rewind Debugger**，在场景中选择一个具有字段通知的 Actor，即可在 “Object Properties” 轨道中找到其字段通知事件记录。

## 模块依赖

此插件的核心依赖已在 `.uplugin` 中声明。你项目的模块若想使用其收集的追踪数据，可能需要引用：

| 模块 | 用途 |
|---|---|
| `GameplayInsights` | 插件功能的基础，提供数据追踪与注入的框架。 |
| `RewindDebugger` | 数据最终的展示与回放平台，插件向其注册调试轨道。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-01 | `fb04ebb6` | [MassDebug] | 与大规模调试工具集 MassDebug 相关的维护性更新。 |
| 2026-03-30 | `6004f575` | [RewindDebugger] | 对 Rewind Debugger 集成进行了更新或修复。 |
| 2026-01-16 | `526a5a0a` | [RewindDebugger] Replaced included header by forward declaration for TraceService::Frame | 优化头文件依赖，减少编译耦合。 |
| 2026-01-16 | `e2c597c8` | Fix missing debug tracks in rewind debugger for PoseSearch, SequenceInfo, and EvaluationTask when us... | 修复了其他调试轨道的显示问题，表明此插件与整个调试生态系统紧密集成。 |
| 2026-01-15 | `1be36357` | [Backout] - CL49859133 | 回退了某个更早的改动，表明处于活跃的开发和问题修复阶段。 |

### 维护评价

- **状态**：**活跃维护**。插件虽标记为实验性（Beta），但近期有多次针对调试框架集成的实质性更新和修复，表明仍在积极开发中。
- **创建时间**：约 2 年前，是一个相对较新的工具。
- **推荐度**：**推荐使用**。如果你正在深入使用 UE5 的 MVVM 或字段通知系统并遇到调试困难，此插件是官方提供的、与引擎调试工具深度集成的专业解决方案。需要注意其默认未启用且为 Beta 版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/FieldNotificationTrace/Tests)