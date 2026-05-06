# Mass Insights

> Plugin to gather insights into Mass execution

| 属性 | 值 |
|---|---|
| 中文名 | Mass 洞察 |
| 分类 | Insights |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MassInsightsAnalysis` (Runtime), `MassInsightsUI` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights) | |

## 总体用途

Mass Insights 是一个仅为 UnrealInsights 程序（Profiler 工具）设计的插件，用于收集、分析和可视化 **Mass 实体框架**（Mass Entity Framework）的执行数据。通过追踪 Mass 处理器（MassProcessor）的执行路径、耗时、实体访问模式等信息，帮助开发者对 Mass 系统的运行状态进行深度诊断和性能调优。

该插件目前处于 **Beta** 阶段，仅用于 UnrealInsights，不作为游戏运行时的一部分。

## 模块列表

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| `MassInsightsAnalysis` (Runtime) | 核心分析引擎，负责接收底层 Trace 数据并进行结构化分析，生成 Mass 执行洞察报告。 | [MassInsightsAnalysis.md](MassInsightsAnalysis.md) |
| `MassInsightsUI` (Runtime) | 在 UnrealInsights 中提供用户界面，将分析结果以表格、图表等形式直观展示。 | [MassInsightsUI.md](MassInsightsUI.md) |

## 使用场景

- **Mass 性能分析**：排查 Mass 处理器执行耗时异常，定位性能瓶颈。
- **Mass 调试**：观察处理器执行顺序、实体分块访问模式，验证系统拓扑结构。
- **Mass 特性开发**：在添加自定义 Mass 处理器时，验证其执行是否与预期一致。
- **UnrealInsights 集成**：作为 Insights 插件扩展，需要与 UnrealInsights 配合使用。

## 维护状态

### 近期更新（git log）

- 2025-05-31 `52e3dac1` — 更新 DLL 存储相关的头文件修复（UnrealCodeFixup）。
- 2025-04-02 `46cab30d` — 修复不可达代码警告。
- 2025-03-25 `c90dffef` — LOCTEXT 修复（本地化文本）。
- 2025-03-24 `81901d1e` — 修复缺失的 LOCTEXT 键。
- 2025-03-20 `0690086f` — 修正版权声明。

### 维护评价

插件创建于 2025-03-20，为全新的 Beta 功能，近期更新以代码清理、修复警告和本地化为主，未涉及架构变更。维护较为活跃，但功能尚处于早期版本，可能存在接口不稳定的风险。**推荐在 UnrealInsights 中使用以分析 Mass 执行数据，但需关注后续更新。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/MassInsights)
- 无官方文档（Beta 阶段）
- 模块详细文档：见上方模块列表链接