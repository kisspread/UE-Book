# Chaos Insights

> Plugin to gather insights into Chaos

| 属性 | 值 |
|---|---|
| 中文名 | 混沌物理洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

本插件是 Unreal Insights 的专用扩展，旨在为基于 Chaos 物理系统的项目提供深度性能分析能力。其核心功能是可视化 Chaos 物理场景锁（Physics Scene Lock）的争用情况。在多线程环境下，游戏线程与物理工作线程对同一把读写锁的不当持有或等待会导致难以察觉的卡顿。启用本插件的追踪通道后，Insights 将清晰展示各线程何时在等待锁、持有锁的类型（读/写）以及锁的递归深度，从而帮助开发者精确定位由物理系统锁争用引发的性能瓶颈。

## 使用场景

- 你的游戏或应用使用了 Chaos 物理系统，并且在某些复杂场景或高负载时出现不明原因的性能下降或卡顿。
- 你需要一个可视化工具来诊断物理线程与游戏线程之间的同步问题，特别是针对物理场景锁的竞争。

## 蓝图用法

本插件为分析工具，其功能通过 Unreal Insights 界面启用和查看，不提供直接在游戏或编辑器蓝图中调用的节点。

## C++ 用法

本插件作为 Unreal Insights 的分析模块，无需在游戏逻辑代码中集成。其启用和使用主要通过 Unreal Insights 的命令行参数或界面配置完成。

## Demo 示例

以下是一个启用 Chaos 物理锁洞察通道进行分析的最小示例：

1.  在启动游戏或应用程序时，通过命令行参数启用 Insights 追踪并包含 `ChaosLocks` 通道：
    ```bash
    MyGame.exe -trace=ChaosLocks,Default
    ```
2.  打开 Unreal Insights 应用程序（`UnrealInsights.exe`）。
3.  在 Timing 视图中，你将能看到 `ChaosLocks` 相关的时间轴，显示各线程的锁等待、读锁和写锁区域。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `ChaosSolverEngine` | Chaos 物理求解器引擎，用于接入物理模拟数据 |
| `PhysicsCore` | 物理系统核心模块，提供基础物理类型和接口 |
| `TraceInsights` | Unreal Insights 的基础追踪和分析框架 |
| `TraceAnalysis` | 用于分析追踪数据的框架 |
| `UnsavedOnlyTracker` | 编辑器中用于追踪未保存资产的工具模块 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF 新宏 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 修正头文件中的 DLL 导出声明 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing | 修复了因时序视图会话指针失效导致的崩溃 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复了反复开关 Timing 标签页导致的崩溃 |

### 维护评价

该插件创建于 2025 年 4 月，时间不长。从提交历史看，初始版本上线后不久即有针对崩溃的修复和代码整理，表明处于积极开发和维护阶段。由于 `IsBetaVersion=true`，它仍被视为实验性功能，可能存在未发现的局限性。对于正在使用 Chaos 物理系统并遇到性能问题的项目，这是一个非常有价值的诊断工具，推荐在性能分析环节使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
- [官方文档]() (暂无独立文档，请参考 Unreal Insights 相关资料)
- [测试用例]() (暂未发现插件专属测试用例)