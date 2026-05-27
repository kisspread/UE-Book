# Chaos Insights

> Plugin to gather insights into Chaos

| 属性 | 值 |
|---|---|
| 中文名 | 混沌洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

这个插件是 **Unreal Insights 工具的专用扩展**，专门用于分析 **Chaos 物理系统** 的性能和行为。它的核心功能是提供一个 **物理场景锁分析器**，帮助开发者检测多线程环境下的锁争用问题。

**解决的问题**：
1.  **锁争用可视化**：多线程物理系统中，游戏线程和工作线程都需要访问物理场景数据，这需要读写锁。当多个线程竞争同一把锁时，会导致等待和卡顿。
2.  **难以察觉的性能瓶颈**：这些锁争用通常很难通过常规的性能分析工具发现，因为它们分散在多个线程中。
3.  **操作密度分析**：帮助开发者理解在一段代码区域内锁被递归获取的次数，从而评估操作的复杂度和并发性。

**为什么存在**：
它填补了现有性能分析工具在分析 Chaos 物理系统多线程锁行为方面的空白，使开发者能够直观地看到锁的等待、持有和递归情况，从而优化代码，减少游戏线程的卡顿。

## 使用场景

-   你在开发一个使用 **Chaos 物理引擎** 且涉及大量 **物理查询或异步物理模拟** 的项目。
-   你的游戏在特定场景下出现 **间歇性卡顿**，怀疑是物理系统的多线程锁争用导致。
-   你需要在 **Unreal Insights** 中捕获并分析物理场景锁的争用情况，以定位并优化问题代码。
-   你需要分析物理系统的并发性能，了解锁操作的密度和分布。

## 蓝图用法

此插件为 **Unreal Insights 工具专用插件**，其模块类型为 `EditorAndProgram`，仅支持 `UnrealInsights` 程序。它不提供任何可供游戏运行时使用的蓝图节点或资产。

**使用方式**：
在 Unreal Insights 工具中，启用 `ChaosLocks` 通道进行捕获，即可在 Insights 的时间线视图中查看物理场景锁的争用情况。

## C++ 用法

此插件的分析逻辑是 Unreal Insights Trace 分析器的一部分，**不提供给游戏或编辑器模块直接使用的公共 C++ API**。其公共头文件主要用于为 Unreal Insights 工具提供数据模型。

### 头文件引入 (仅用于 Insights 分析器开发)

```cpp
// 用于构建 Insights 分析器的锁区域模型
#include "ChaosInsightsAnalysis/Model/LockRegions.h"
```

### 基本用法 (作为 Insights 分析器开发者)

如果你正在开发一个需要集成 Chaos 锁分析的 Unreal Insights 扩展，可以参考以下模式。

```cpp
// 在你的 Insights 分析模块中，实现获取锁区域提供者的功能
// 来源：Private/ChaosInsightsAnalysisModule.h 和 Public/ChaosInsightsAnalysis/Model/LockRegions.h

// 1. 获取锁区域提供者
const ChaosInsightsAnalysis::ILockRegionProvider& Provider = ChaosInsightsAnalysis::ReadRegionProvider(*AnalysisSession);

// 2. 遍历所有锁区域以进行数据聚合
uint64 TotalRegions = Provider.GetRegionCount();
int32 LaneCount = Provider.GetLaneCount();

// 3. 在特定时间范围内迭代区域
double Start = 0.0;
double End = 10.0; // 10秒内
Provider.ForEachRegionInRange(Start, End, [](const ChaosInsightsAnalysis::FLockRegion& Region)
{
    // 处理每个锁区域的数据
    // Region.BeginTime, .AcquireTime, .EndTime, .bIsWrite, .LockCount 等
    return true; // 返回 true 继续迭代
});
```

### 进阶用法 (数据模型分析)

```cpp
// 来源：Public/ChaosInsightsAnalysis/Model/LockRegions.h
// FLockRegion 结构体包含了完整的锁生命周期信息

ChaosInsightsAnalysis::FLockRegion SomeRegion = ...;
// 分析锁等待时间
double WaitDuration = SomeRegion.AcquireTime - SomeRegion.BeginTime;
// 分析锁持有时间
double HoldDuration = SomeRegion.EndTime - SomeRegion.AcquireTime;
// 判断是读锁还是写锁
bool bIsExclusiveLock = SomeRegion.bIsWrite;
// 检查递归锁深度
int32 RecursiveLocks = SomeRegion.LockCount;
```

## Demo 示例

由于此插件是 Unreal Insights 工具的内部组件，不提供面向游戏或编辑器的独立演示。一个“最小示例”就是使用 Unreal Insights 工具捕获带有 `ChaosLocks` 通道的会话。

**使用步骤**：
1.  启用 `ChaosInsights` 插件（默认已启用）。
2.  启动 Unreal Insights 工具（`UnrealInsights.exe`）。
3.  在目标应用程序（如编辑器或游戏）中，通过 `trace.start ChaosLocks` 控制台命令启动包含 Chaos 锁分析的追踪会话。
4.  在 Unreal Insights 中打开捕获的 `.utrace` 文件。
5.  在时间线视图中查找 “Chaos Locks” 区域，查看各个线程的锁争用情况。

## 模块依赖

从模块名称和插件类型推断，此插件依赖 Unreal Insights 的核心分析和 UI 框架。对于使用此插件的最终用户（即使用 Unreal Insights 工具的开发者），无需额外处理依赖关系。

对于扩展此插件的开发者，典型的依赖可能包括：

| 模块 | 用途 |
|---|---|
| `TraceAnalysis` | 提供 Unreal Insights 的底层分析框架 |
| `TraceServices` | 提供分析会话、数据存储和线性分配器等服务 |
| `InsightsCore` | Unreal Insights 的核心功能模块 |
| `InsightsFrontend` | Unreal Insights 的前端 UI 框架 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式，可能是 UE 内部规范更新。 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 更新头文件以符合代码规范，确保 DLL 导出宏放在正确的位置。 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing | 修复了在 Insights 时间线视图标签页禁用后，因悬空指针导致的崩溃。 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复了启用和禁用 Insights 时间线标签页后导致的追踪崩溃。 |
| 2025-04-11 | `7565ac94` | Added ChaosInsights module for Chaos related extensions to insights and implemented a physics scene lock profiler. | 初始提交：添加了 ChaosInsights 模块，并实现了物理场景锁性能分析器。 |

### 维护评价

-   **创建时间**：插件创建于 2025 年 4 月，历史不长，属于较新的工具。
-   **维护活跃度**：在创建后的一个多月内（至 2025 年 5 月）有密集的 bug 修复和规范更新。最近一次更新（2026 年 4 月）是内部日志规范的迁移。整体来看，**处于维护中**，但近期更新主要是内部规范调整，无重大功能迭代。
-   **状态**：插件标记为 `IsBetaVersion: true`，说明仍处于 **实验性/测试阶段**。
-   **限制**：作为 Insights 专用插件，功能高度专业化，仅适用于物理调试场景。
-   **推荐使用**：如果你的项目正在使用 Chaos 物理并面临棘手的多线程性能问题，**强烈推荐** 尝试此插件来定位锁争用。对于没有相关问题的项目，则无需关注。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
-   官方文档 (暂无)
-   测试用例 (插件内未包含测试用例)