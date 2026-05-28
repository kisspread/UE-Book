# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | Mass框架性能分析 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (EditorAndProgram), `MassInsightsUI` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights) | |

## 用途

MassInsights 是一个专门为 Unreal Insights 性能分析工具设计的插件，用于深入分析 Unreal Engine 中 Mass 框架（大规模实体组件系统）的运行时行为和性能。它解决了在开发使用 Mass 框架的大型项目时，难以追踪实体生命周期事件（创建、原型变更、销毁）和处理器执行阶段性能瓶颈的问题。该插件将 Mass 的跟踪数据集成到 Unreal Insights 中，为开发者提供直观的性能分析视图。

## 使用场景

- **性能优化**：当你使用 Mass 框架管理成千上万个实体（如大型 RTS 游戏、模拟游戏）并需要找出性能瓶颈时，可以使用此插件分析实体生命周期事件和处理器执行时间。
- **调试实体状态**：当实体在运行时频繁变更原型（Archetype）导致预期外的行为时，可以通过该插件的事件列表和时间线标记来追踪具体的原型变更。
- **分析处理器阶段**：对于 Mass 系统的处理器（Processor）执行阶段（如 Pre、On、Post），可以查看各阶段耗时，优化关键路径。
- **配合 Unreal Insights 使用**：此插件专为 Unreal Insights 程序设计，是 Mass 框架性能分析的标准工具链的一部分。

## 蓝图用法

此插件**不提供蓝图节点**，其核心功能完全在 Unreal Insights 程序中以分析视图的形式呈现。用户通过 Unreal Insights 界面进行交互，而不是在游戏或编辑器蓝图中使用。

## C++ 用法

此插件主要面向 Unreal Insights 程序，其 API 用于扩展分析功能，而不是在游戏代码中直接调用。开发者可以通过扩展 `MassInsightsAnalysis` 模块来添加自定义的分析逻辑。

### 头文件引入

```cpp
#include "MassInsightsAnalysis.h"
```

### 基本用法

从测试用例 `Engine/Tests/MassInsightsTests/` 中可以看到，该插件的核心是解析和展示 Mass 的跟踪事件。

```cpp
// 假设要集成一个新的分析器
// 来自测试用例 Engine/Tests/MassInsightsTests/MassInsightsAnalyzerTest.cpp
#include "Trace/MassTraceAnalysis.h"

class FMyCustomMassAnalyzer : public IMassTraceAnalyzer
{
    // 实现分析接口，处理 MassTrace 事件
};
```

### 进阶用法

通过实现 `IMassTraceAnalyzer` 接口，可以创建自定义分析器，处理从 Mass 系统接收到的跟踪数据（如实体创建、销毁、事件等），并将其集成到 Unreal Insights 的用户界面中。

## Demo 示例

此插件没有独立的 Demo 项目，但可以在 Unreal Insights 程序中直接体验。启动 Unreal Insights 并选择 Mass 跟踪频道，即可看到 MassInsights 提供的视图。

1. 打开 Unreal Insights 程序。
2. 连接到正在运行的游戏实例或加载 `.utrace` 文件。
3. 在 Insights 的左侧栏中，选择 "Mass" 选项卡。
4. 查看实体事件列表、时间线标记和处理器阶段耗时。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MassInsightsAnalysis` | 核心分析逻辑，负责解析 MassTrace 数据并生成分析结果。 |
| `MassInsightsUI` | 用户界面模块，在 Unreal Insights 中渲染分析视图、事件列表和时间线。 |

**特殊依赖**：此插件完全依赖于 Unreal Insights 程序（`SupportedPrograms: ["UnrealInsights"]`），并且需要目标游戏或项目已经集成了 Mass 框架并开启了 MassTrace 跟踪。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-06 | `973765c5` | [MassInsights] Fixed deprecated FName for FBaseTreeNode constructor. | 修复了 FBaseTreeNode 构造函数中已弃用的 FName 用法。 |
| 2026-03-31 | `65c8bacb` | [MassTrace] | 与 MassTrace 模块相关的更新（未提供详细信息）。 |
| 2026-03-27 | `51a4c1e5` | [MassTrace] | 与 MassTrace 模块相关的更新（未提供详细信息）。 |
| 2025-10-30 | `a0e12af6` | Ran UnrealCodeFixup on Engine to change all ~Type() {} to instead be ~Type() = default | 全局代码修复，将析构函数实现改为 `= default`。 |
| 2025-05-31 | `52e3dac1` | Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of ty | 头文件更新，确保 DLL 导出符号正确。 |

### 维护评价

MassInsights 是一个相对较新的插件（创建于 2025 年初），目前仍处于 **Beta 阶段**（IsBetaVersion: true）。从最近的提交记录看，它仍在积极维护，最近的更新集中在 2026 年 3-4 月，主要修复了与底层 MassTrace 模块同步的编译问题。然而，初始提交中明确提到“性能仍是工作进行中，尚不适合处理数百万事件”，这表明其性能可能还有优化空间。由于它是 Mass 框架性能分析的官方工具，随着 Mass 框架的成熟，它预计会持续更新。

**结论**：✅ 推荐使用，但需注意其 Beta 状态和潜在的性能限制。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MassInsights)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/) (未找到此插件专用文档，可参考 Mass 框架和 Unreal Insights 文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/MassInsightsTests)