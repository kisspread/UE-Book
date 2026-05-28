# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | 大规模洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (Editor), `MassInsightsUI` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights) | |

## 用途

MassInsights 是 Unreal Insights 分析工具的一个专用插件，其核心功能是**收集、分析并可视化 Unreal Engine 的 Mass（Mass Entity System，大规模实体系统）框架的运行时执行数据**。它解决了在使用 Mass ECS 架构时，难以直接观察和诊断成千上万个实体的创建、原型变更、销毁等生命周期事件，以及各个处理器阶段性能瓶颈的问题。通过将 Mass 的跟踪数据集成到 Unreal Insights 中，开发者可以像分析渲染或 CPU 性能一样，精确地分析 Mass 任务的执行流和耗时。

## 使用场景

- 你正在使用 **Mass Entity System (ECS)** 开发需要处理大量实体（如成群 AI、粒子、物理对象）的游戏或模拟项目。
- 项目在运行 Mass 相关任务时出现性能卡顿，需要定位是哪个**处理器 (Processor)** 阶段或哪类**实体操作**（如原型变更）消耗了过多时间。
- 你希望观察特定实体的生命周期（创建、修改原型、销毁），并理解这些操作如何影响整个系统的执行。
- 需要结合时间轴标记和处理器阶段，对 Mass 系统的执行进行**时序分析和调优**。

## 蓝图用法

**不适用**。此插件是一个**编辑器/程序扩展**，用于增强 Unreal Insights 工具的功能，本身不暴露任何可调用的蓝图节点或属性。其交互完全在 Unreal Insights 应用程序内完成。

## C++ 用法

此插件作为 Unreal Insights 的模块化特性（`TraceServices::IModule`）存在。它的主要 API 是其内部的分析器（Analyzer）和事件解析逻辑。通常**不需要在你的游戏或插件代码中直接调用它**，除非你正在开发一个自定义的 Insights 扩展。

### 头文件引入

对于希望集成或理解其模块结构的开发者：
```cpp
// 核心分析模块的接口
#include "MassInsightsAnalysisModule.h"
```

### 基本用法（集成分析器）

`MassInsightsAnalysis` 模块的核心任务是注册其分析器。以下是其模块实现的关键逻辑示意（源自 `FMassInsightsAnalysisModule`）。

```cpp
// 在模块启动时，将自身注册为 Unreal Insights 的一个分析模块。
// 来源：Private/MassInsightsAnalysisModule.h
void FMassInsightsAnalysisModule::StartupModule()
{
    // 注册此模块，使得 Unreal Insights 启动时能发现并调用它
    TraceServices::GetAnalysisModuleRegistry().RegisterModule(this);
}

// 当一个分析会话开始时，Insights 调用此方法，模块负责创建并注册自己的分析器。
void FMassInsightsAnalysisModule::OnAnalysisBegin(TraceServices::IAnalysisSession& Session)
{
    // 这里会创建 FMassTraceAnalyzer 实例，并向 Session 注册。
    // 该分析器负责解析来自 Mass 框架的二进制跟踪数据，提取实体事件。
    TSharedRef<FMassTraceAnalyzer> Analyzer = MakeShared<FMassTraceAnalyzer>(Session);
    Session.AddAnalyzer(Analyzer);
}
```

## Demo 示例

由于这是一个 Insights 插件，没有传统的运行时 Demo。最小“可运行”示例是**启动 Unreal Insights 并加载一个包含 Mass 活动的跟踪记录**。

**操作步骤**：
1.  在项目设置中确保 `MassInsights` 插件已启用（默认启用）。
2.  运行你的游戏/编辑器，并使用 `-trace=mass` 或通过代码启用 Mass 跟踪通道。
3.  停止跟踪，保存 `.utrace` 文件。
4.  打开 Unreal Insights，加载该 `.utrace` 文件。
5.  在 Insights 中，切换到 “Mass Insights” 选项卡（由 `MassInsightsUI` 模块提供），即可查看实体事件列表、时间线标记和处理器阶段分析。

## 模块依赖

此插件专为 `UnrealInsights` 程序设计。其内部依赖集中在 Mass 和跟踪分析相关模块。

| 模块 | 用途 |
|---|---|
| `MassEntity` | Mass 框架的核心模块，提供需要分析的数据结构和运行时基础。 |
| `TraceAnalysis` | Unreal Insights 分析框架，用于注册模块、解析跟踪流和创建分析器。 |
| `TraceServices` | 提供分析会话、模块注册和数据存储的接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-06 | `973765c5` | [MassInsights] Fixed deprecated FName for FBaseTreeNode constructor. | 修复了使用已废弃的 FName 构造函数导致的编译警告或错误。 |
| 2026-03-31 | `65c8bacb` | [MassTrace] | 提交信息简短，可能为底层 Mass 跟踪（MassTrace）功能的更新或修复。 |
| 2026-03-27 | `51a4c1e5` | [MassTrace] | 同上，为 Mass 跟踪相关的连续性更新。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 引擎级代码格式化，将空的析构函数改为 `= default`，属于维护性修改。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 引擎级代码格式化，调整 DLL 导出标记位置。 |

### 维护评价

MassInsights 是一个**较新且专注于特定领域的插件**。
- **创建时间**：2025 年 3 月，属于 UE5 的较新功能。
- **更新频率**：在创建后的 1 年内有零星的维护性更新（代码格式化、小修复）。最近两次更新（2026-03）集中在 `MassTrace` 模块，可能表示核心功能仍在微调。
- **当前状态**：从首次提交的描述来看，**性能优化尚未完成**，明确说明“Not suitable yet for millions of events”（还不适用于处理数百万事件）。这表明它仍处于**积极开发和完善阶段**。
- **推荐度**：如果你的项目**严重依赖 Mass ECS 并且遇到性能瓶颈**，这是一个**强烈推荐使用的官方工具**。但对于超大规模实体的性能分析，目前可能还有局限性。建议在 UE 5.5 或更高版本中使用，并关注后续的性能更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights)
- [官方文档](https://docs.unrealengine.com)（搜索“Mass Insights”或“Unreal Insights Mass”）
- [测试用例]（暂未在插件目录中发现自动化测试文件）