# Chaos Insights

> Plugin to gather insights into Chaos（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 物理洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

此插件专为 **Unreal Insights** 程序扩展，用于深入分析 **Chaos 物理系统**的性能与行为。其核心功能是提供 **物理场景锁（Physics Scene Lock）性能分析器**。在多线程物理模拟中，线程对主物理场景锁的争用（Contention）可能导致游戏线程卡顿。此工具能可视化所有尝试获取该锁的线程，清晰展示读锁与写锁的等待情况，帮助开发者诊断和解决由锁竞争引起的性能瓶颈。

## 使用场景

- 你开发的游戏包含大量物理交互（如布娃娃、刚体碰撞），在复杂场景下出现随机卡顿 → 使用此插件在 Unreal Insights 中启用 `ChaosLocks` 通道，分析锁等待情况。
- 你怀疑物理查询或角色移动组件（Movement Component）的更新与物理模拟同步发生冲突，导致性能下降 → 使用此插件生成时序图，定位具体的锁争用线程和代码区域。

## 蓝图用法

不适用。此插件为 **Unreal Insights 程序**扩展，其功能通过 Insights 的 Trace Channel 和 Timing View 展现，不提供游戏运行时的蓝图节点。

## C++ 用法

此插件的 API 主要面向 Unreal Insights 程序的内部扩展，而非游戏项目的直接 C++ 调用。其核心是注册自定义的 Trace Channel 和 Timing View 绘制逻辑。

### 核心模块与使用

1.  **启用 Trace Channel**：
    在 Unreal Insights 启动参数或 UI 中启用 `ChaosLocks` 通道，即可开始捕获物理锁事件。
2.  **查看分析结果**：
    在 Unreal Insights 的 **Timing 视图**中，选择 `ChaosLocks` 通道，将显示各线程对物理场景锁的持有与等待时间线，区分读锁（Read）与写锁（Write）。

## 模块列表

| 模块 | 一句话说明 |
|---|---|
| `ChaosInsightsAnalysis` | 负责分析 Chaos 物理锁事件数据，提供查询和统计功能。 |
| `ChaosInsightsUI` | 负责在 Unreal Insights 的 Timing 视图中绘制物理锁分析的时序图表。 |

## Demo 示例

无直接可运行的项目 Demo。功能演示依赖于 Unreal Insights 程序加载此插件后，对目标项目（如包含复杂物理场景的测试项目）进行 Trace 捕获与分析。

## 模块依赖

无特殊依赖（仅标准 Insights 框架及 Chaos 物理模块）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 采用新版日志宏，保持代码规范一致。 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty... | 修正 DLL 导出声明，确保跨模块链接正确。 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing... | 修复了一个在 Timing 视图会话结束后访问无效指针导致的崩溃。 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复了反复启用/禁用 Timing 选项卡时可能导致的崩溃问题。 |
| 2025-04-11 | `7565ac94` | Added ChaosInsights module for Chaos related extensions to insights and implemented a physics scene... | 初始提交，实现了物理场景锁性能分析器的核心功能。 |

### 维护评价

- **状态**：**活跃维护**。
- **分析**：插件创建于 2025 年 4 月，至今约 1 年。从 git 历史看，开发初期集中修复了多个稳定性问题（崩溃），近期有代码规范和工具链适配更新。最后实质性功能修复在 2025 年 4 月底，之后以维护性提交为主。考虑到其作为调试工具的性质，更新频率属正常。
- **建议**：✅ **推荐使用**。该插件是分析 Chaos 物理系统多线程性能问题的专业工具，对于遇到相关卡顿问题的项目有重要价值。虽为实验性（`IsBetaVersion=true`），但已具备核心功能并经过稳定性修复。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
- [官方文档](https://docs.unrealengine.com/)（暂无专属文档页，可查阅 Unreal Insights 及 Chaos 物理系统相关文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)（当前插件目录内无独立测试）