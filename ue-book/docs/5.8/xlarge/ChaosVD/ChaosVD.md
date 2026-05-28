# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌物理调试器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器资产、材质模板、天空球网格） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD) | |

---

## 用途

Chaos Visual Debugger (CVD) 是一个**编辑器级别的物理调试工具**，用于对 Chaos 物理模拟进行可视化调试。它解决的核心问题是：**物理模拟是连续且高速的，开发者很难通过传统的日志或断点方式理解物理系统在每一帧、每个求解器阶段到底发生了什么**。

CVD 的工作原理是通过 Unreal 的 Trace 系统录制 Chaos 物理模拟的完整数据（粒子状态、几何体形状、碰撞数据、场景查询等），然后在一个专用的 3D 视口和配套面板中回放这些数据。开发者可以：

- 逐帧、逐求解器阶段地浏览物理模拟过程
- 可视化显示粒子的速度、角速度、加速度、冲量等矢量数据
- 查看场景查询（Scene Query）的详细过程和结果
- 检查碰撞通道、约束关系等底层物理数据
- 连接到**实时运行的游戏实例**进行远程调试，或加载已录制的 Trace 文件

它既是一个独立程序（`ChaosVisualDebugger` 支持程序），也可以作为编辑器内的工具窗口使用。

## 使用场景

- 你在调试物理穿透/穿模问题 → 用 CVD 回放出问题的帧，检查碰撞几何体形状和变换
- 你需要理解一个刚体碎片爆炸效果的物理行为 → 用 CVD 逐帧观察每个碎片的速度、加速度矢量
- 你需要检查多人网络物理预测/修正的问题 → 用 CVD 的 Network Tick 同步模式对比服务器和客户端的物理状态
- 你在调试场景查询（LineTrace/Sweep/Overlap）的漏检问题 → 用 CVD 的 Scene Query Browser 查看查询的完整遍历过程
- 你需要在远程服务器上实时观察物理模拟状态 → 用 CVD 的 Live Session 连接功能

---

## 文档结构

由于本插件源码规模为 **xlarge**（343 个源文件），文档按模块拆分：

| 文档 | 说明 |
|---|---|
| [index.md](index.md)（本页） | 总览、用途、维护状态 |
| [ChaosVD.md](ChaosVD.md) | 核心模块：场景、回放、可视化、数据处理 |
| [ChaosVDBlueprint.md](ChaosVDBlueprint.md) | 蓝图运行时模块 |
| [ChaosVDBuiltInExtensions.md](ChaosVDBuiltInExtensions.md) | 内置扩展模块 |

---

## 模块依赖

从 Build.cs 提取的非标准依赖：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | TEDS（Editor Data Storage）集成，用于场景大纲和选择系统 |
| `EditorDataStorageFeatures` | TEDS 功能特性支持 |
| `GeometryProcessing` | 网格生成（从 Chaos 隐式对象生成可渲染的 Static Mesh） |
| `TraceServices` | Unreal Trace 分析系统，CVD 录制/回放的基础 |
| `TraceAnalysis` | Trace 数据分析 |
| `UnrealInsightsCore` | Insights 核心功能 |

无特殊依赖（仅标准 Core/Engine/Slate 等）的部分已省略。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 重构视口客户端关联/解除关联的通知机制 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回退一个变更（CL53913857） |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit | 视口客户端关联通知重构（重复提交） |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-12 | `b4158d4d` | Make CVD Perf Analysis Async | 将 CVD 性能分析改为异步执行 |

### 维护评价

**活跃维护** — CVD 是一个约 2 年前创建的 Beta 级别插件，仍在积极开发中。

- ✅ **创建时间**：2024-03-20（从 Experimental 文件夹迁出，作为 Beta 发布于 UE 5.4）
- ✅ **最近更新**：截至 2026-05-14 仍有功能性和重构性更新
- ✅ **维护频率**：持续活跃，有视口重构、异步化优化、编译修复等
- ⚠️ **Beta 状态**：`IsBetaVersion=true`，API 可能不稳定
- ⚠️ **大量废弃标记**：源码中大量 `UE_DEPRECATED(5.8, ...)` 标记，表明 5.8 版本正在大规模重构 API，特别是 Trace 管理器和会话管理部分正在迁移到 `UE::TraceBasedDebuggers` 命名空间
- ✅ **推荐使用**：推荐在需要深度调试 Chaos 物理模拟时使用，但注意 API 可能在后续版本中发生变化

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD)
- [官方文档]()（暂无）