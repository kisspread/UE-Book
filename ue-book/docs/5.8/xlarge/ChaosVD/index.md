# Chaos Visual Debugger

> Enables support for Visual debugging of Chaos Physics simulations

| 属性 | 值 |
|---|---|
| 中文名 | 混沌可视化调试器 |
| 分类 | Physics |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（编辑器与程序内容） |
| 模块 | `ChaosVD` (EditorAndProgram), `ChaosVDBlueprint` (RuntimeAndProgram), `ChaosVDBuiltInExtensions` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-03-20 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD) | |

## 用途
Chaos Visual Debugger (CVD) 是专为 **Chaos 物理引擎** 设计的高级可视化调试工具。它解决的核心问题是：**在复杂的物理模拟中，开发者难以直观地观察、记录、回放和分析物体交互、碰撞响应、约束状态以及性能瓶颈**。
CVD 不仅可以实时查看物理场景，更能录制完整的物理模拟数据，供事后进行精确的步进回放和深度分析，这对于调试物理相关的 Bug 和优化性能至关重要。

## 使用场景
- 你是物理开发者，需要调试刚体间的复杂交互（如堆叠、连锁反应）或碰撞响应问题。
- 你遇到了物理模拟的性能瓶颈，需要逐帧分析特定物理对象的状态变化和计算开销。
- 你正在开发基于物理的AI或角色行为，需要可视化碰撞体、约束和力反馈。
- 你需要将物理模拟的特定问题（如物体飞出场景）记录下来，并分享给团队进行分析。

## 子模块概览
本插件为大型插件，详细文档已拆分至以下子模块：

- **[ChaosVD](ChaosVD.md)**：核心编辑器与独立程序模块。提供物理数据录制、回放、场景状态查看、性能分析等主要功能。
- **[ChaosVDBlueprint](ChaosVDBlueprint.md)**：运行时蓝图模块。提供蓝图可调用的函数，用于在运行时与 CVD 系统交互（如触发录制、查询数据）。
- **[ChaosVDBuiltInExtensions](ChaosVDBuiltInExtensions.md)**：内置扩展开模块。包含由 Epic 官方提供的、用于扩展 CVD 核心功能的附加可视化或数据处理器。

## 蓝图用法 (概要)
详细的 API 列表请参考各子模块文档。主要蓝图功能集中在 `ChaosVDBlueprint` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartRecording` | 开始录制物理模拟数据。 | `UChaosVDSubsystem` |
| `StopRecording` | 停止当前录制。 | `UChaosVDSubsystem` |
| `IsRecording` | 查询当前是否正在录制。 | `UChaosVDSubsystem` |
| `GetAvailableRecordings` | 获取所有可用的录制会话列表。 | `UChaosVDSubsystem` |
| `OpenRecording` | 加载并打开一个已有的录制文件。 | `UChaosVDSubsystem` |

### 使用示例 (蓝图描述)
要在游戏运行时录制物理模拟：首先获取 `ChaosVDSubsystem` 的实例，然后调用 `StartRecording` 节点开始录制。游戏运行一段时间后，调用 `StopRecording` 节点停止。随后，你可以在编辑器中通过 CVD 面板或蓝图中的 `OpenRecording` 节点加载并回放这次录制。

## C++ 用法 (概要)
CVD 主要是一个编辑器和调试工具，其强大的 C++ API 用于插件内部扩展和自定义数据处理器。对于普通项目集成，更推荐使用蓝图接口。

### 基本用法
典型的集成场景是监听物理事件并自定义可视化数据。你需要继承 `ChaosVDDataProcessorBase` 来创建自定义处理器。

```cpp
// MyCustomCVDProcessor.h
#pragma once
#include "ChaosVDRecording/ChaosVDDataProcessorBase.h"

class FMyCustomCVDProcessor : public FChaosVDDataProcessorBase
{
public:
    // 处理每帧的物理数据
    virtual void ProcessNewGameFrameData(const FChaosVDGameFrameData& InFrameData) override;
};
```

## Demo 示例
本插件主要作为独立的可视化调试器使用，其“Demo”就是你自己的项目物理场景。启用插件后，在编辑器菜单中找到 `Window -> Developer Tools -> Chaos Visual Debugger` 即可打开主面板进行录制和分析。

## 模块依赖
要使用本插件（特别是扩展它），你的模块可能需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `EditorDataStorage` | 编辑器数据存储框架，CVD 用其管理录制数据。 |
| `EditorDataStorageFeatures` | 上述框架的功能扩展。 |
| `GeometryProcessing` | 用于处理几何数据，可能用于物理形状的可视化。 |
| `ChaosVD` | 插件的核心模块，若需访问内部类型则需要依赖。 |
| `ChaosVDBlueprint` | 插件的运行时蓝图模块，用于蓝图交互。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `cfb610df` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 重构视口相关代码，优化客户端关联/解耦时的通知逻辑。 |
| 2026-05-14 | `9144f8ac` | [Backout] - CL53913857 | 回滚了之前的某个更改。 |
| 2026-05-14 | `9ede83f2` | Viewport: Factor obligatory copypasta by notifying client when it is associated or disassociated wit... | 继续进行视口代码的重构工作。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-12 | `b4158d4d` | Make CVD Perf Analysis Async | 将性能分析功能改为异步执行，提升用户体验。 |

### 维护评价
**积极维护中**。ChaosVD 是一个相对年轻的插件（约2年），目前处于 **Beta 测试阶段**。从近期提交记录（截至2026年5月）来看，开发团队对其投入持续且密集，更新内容涉及核心架构优化、性能改进和功能完善，显示出它正处于快速迭代期。这是一个非常活跃且值得期待的工具。

**推荐使用**，尤其适合在开发中深度使用 Chaos 物理系统的项目。由于是 Beta 版，部分 API 或功能可能在未来版本中调整，请关注其更新日志。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosVD)
- 官方文档：暂无
- 测试用例：可尝试在 `Engine/Plugins/ChaosVD/` 或 `Engine/Tests/` 目录下查找 `ChaosVD` 相关的自动化测试文件。