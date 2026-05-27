# Chaos Insights

> Plugin to gather insights into Chaos（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Chaos 洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `ChaosInsightsAnalysis` (EditorAndProgram), `ChaosInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-11 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights) | |

## 用途

`ChaosInsights` 是一个性能分析工具插件，专门用于在 **Unreal Insights** 中可视化和分析 **Chaos** 物理系统中的 **锁竞争（Lock Contention）** 问题。

在多线程环境下，物理场景（Physics Scene）的主锁（Main Lock）是性能的关键瓶颈。读取物理数据（如查询）需要获取读锁，而更新物体位置则需要获取写锁。当工作线程（Worker Thread）持有锁的时间过长，或者执行大量查询时，游戏线程（Game Thread）在尝试移动组件或同步物理模拟结果时，就会因为等待锁而被阻塞，导致明显的卡顿（Stalls）。这类问题很难通过常规性能分析工具发现。

本插件通过添加名为 `“ChaosLocks”` 的分析通道，启用物理场景锁分析器（Physics Scene Lock Profiler）。它会可视化所有尝试获取物理场景锁的线程，清晰地展示读锁和写锁的等待情况，帮助开发者识别和诊断上述锁竞争导致的性能问题。

## 使用场景

- 你的游戏在复杂场景或大量物理交互下出现主线程卡顿，怀疑是物理引擎导致的。
- 你需要使用 Unreal Insights 进行性能分析，并希望深入了解 Chaos 物理系统的内部线程同步状态。
- 你想知道哪个工作线程在何时因为什么原因阻塞了游戏线程，以便优化任务调度或物理查询逻辑。

## 蓝图用法

此插件不提供传统意义上的蓝图节点。其主要功能是作为 Unreal Insights 工具的一个**扩展轨道（Track）**。其用户界面交互主要通过 Insights 的菜单和快捷键完成。

### 核心功能（Insights UI）

在 Unreal Insights 的 **Timing 视图**中，可以通过以下方式使用本插件：

| 功能 | 说明 |
|---|---|
| **显示/隐藏锁区域轨道** | 通过 Insights 菜单或快捷键，控制是否在 Timing 视图中显示 `LockRegions` 轨道。 |
| **锁事件分析** | 在轨道上，读锁和写锁区域会以不同颜色显示，并标识出线程的等待时间。 |
| **事件搜索与提示** | 支持在轨道上搜索特定的锁事件，并在悬停时显示详细的工具提示（Tooltip），包括递归锁数量等信息。 |

**使用示例（Insights 操作）**：
1.  在项目设置或命令行中，启用 `ChaosLocks` 跟踪通道。
2.  运行游戏并进行性能捕获（Profile Capture）。
3.  在 Unreal Insights 应用程序中打开捕获文件。
4.  在 **Timing** 面板中，找到并启用 `Chaos` 相关的轨道（通常会自动显示），其中就包含 `LockRegions` 轨道。
5.  通过缩放和分析轨道上的色块，观察线程间锁的竞争和等待情况。

## C++ 用法

此插件主要作为 **Unreal Insights 的扩展程序**运行，而非一个直接供游戏代码调用的运行时库。其核心模块类型为 `EditorAndProgram`，并且明确指定了 `ProgramAllowList: ["UnrealInsights"]`，意味着它主要在编辑器和独立的 Insights 分析程序中加载。

开发者的主要“用法”是理解和使用其扩展的 Insights 轨道。如果需要对其进行二次开发或集成，通常涉及实现或继承 Insights 的扩展接口。

### 头文件引入

插件的公共接口主要通过 Insights 的扩展点暴露，没有提供广泛的公共头文件。主要的分析逻辑封装在内部模块中。

### 核心类（用于 Insights 扩展）

以下类是插件功能的基石，但通常由 Insights 框架实例化和管理：

**`FLockRegionsSharedState`**（Private/LockRegionTrack.h）
```cpp
// 继承自 ITimingViewExtender，负责管理锁区域轨道的共享状态和生命周期。
// 它通过 OnBeginSession/OnEndSession/Tick 与 Timing View 会话交互。
ChaosInsights::FLockRegionsSharedState TimingViewExtender;
```

**`FLockRegionsTrack`**（Private/LockRegionTrack.h）
```cpp
// 继承自 FTimingEventsTrack，代表 Insights Timing 视图中显示锁事件的轨道。
// 负责构建绘制状态（BuildDrawState）、初始化工具提示（InitTooltip）和搜索事件（SearchEvent）。
// 是可视化数据的具体实现者。
```

### 基本用法（内部原理）

插件的启动和关闭由 `FChaosInsightsUIModule` 管理。
```cpp
// Private/ChaosInsightsUIModule.h
void FChaosInsightsUIModule::StartupModule()
{
    // 在模块启动时，通常会注册 TimingViewExtender 到 Insights 系统。
    // 注册后，Insights 会话创建/销毁时自动调用 FLockRegionsSharedState 的对应方法。
}

void FChaosInsightsUIModule::ShutdownModule()
{
    // 反注册扩展，清理资源。
}
```

## Demo 示例

本插件是一个分析工具，没有提供可直接集成到游戏项目中的运行时 Demo。其“Demo”即是在 Unreal Insights 中查看 Chaos 物理锁竞争的轨道。

要验证插件是否工作，可以：
1.  确保项目启用了 Chaos 物理。
2.  创建一个包含大量物理体或复杂碰撞检测的场景。
3.  使用 `-trace=ChaosLocks` 命令行参数启动游戏或编辑器。
4.  使用 Unreal Insights 打开生成的 `.utrace` 文件，在 Timing 面板中查找新增的锁相关轨道。

## 模块依赖

从模块类型 (`EditorAndProgram`) 和用途推断，其构建依赖很可能包含 Unreal Insights 相关的模块。由于 `Build.cs` 文件内容未提供，以下为基于其功能合理推测的依赖关系：

| 模块 | 用途 |
|---|---|
| `TraceServices` | 核心的追踪服务接口，用于读取和分析追踪数据。 |
| `InsightsCore` | Insights 框架的核心模块，提供 Timing View、会话管理等基础功能。 |
| `InsightsFrontend` | Insights 前端 UI 框架，用于构建轨道和工具提示。 |
| `Chaos` 或 `PhysicsCore` | 可能用于获取 Chaos 物理系统的类型信息或事件定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 UE_LOG 迁移到 UE_LOGF。 |
| 2025-05-30 | `20572801` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 使用工具修复头文件，确保 DLL 导出标记正确。 |
| 2025-04-30 | `e9656f2e` | [Insights] Chaos Insights: Fixed crash due to usage of a ITimingViewSession pointer after the Timing... | 修复了在 Timing 视图会话结束后使用其指针导致的崩溃。 |
| 2025-04-29 | `ee649d35` | Fix Unreal Insights Trace crashes after enabling and disabling the Timing Tab. | 修复了在 Insights 中反复启用/禁用 Timing 标签页导致的崩溃。 |
| 2025-04-11 | `7565ac94` | Added ChaosInsights module for Chaos related extensions to insights and implemented a physics scene... | 插件初次提交，实现了物理场景锁分析器。 |

### 维护评价

- **活跃度**: 插件于 2025 年 4 月创建，至今约 1 年。初始提交后，有几次关键的 bug 修复和一次工具链更新。最近的更新（2026年4月）是日志系统迁移，属于维护性更新。
- **状态**: 标记为 `IsBetaVersion`，表明它仍处于测试阶段，可能并非最终形态。
- **评价**: 作为一个新晋的、专注于特定问题的分析工具，它目前处于**维护中**状态。它解决了 Chaos 物理在 Insights 中监控困难的实际问题，具有明确的实用价值。对于需要深度优化物理性能的项目，推荐尝试使用，但需注意其 Beta 状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights)
- [官方文档](https://docs.unrealengine.com/) (未在 .uplugin 中指定)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosInsights/Tests) (可能位于插件目录或 Engine/Tests/ 下)