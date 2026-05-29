# Audio Insights

> Suite of tools to profile, debug, and monitor aspects of audio in the Unreal Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频洞察 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（分析工具模板） |
| 模块 | `AudioInsights` (EditorAndProgram), `AudioInsightsEditor` (EditorNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2023-12-01 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights) | |

## 用途

该插件旨在将音频分析、调试与监控功能深度集成到 Unreal Insights 分析工具和 Unreal Editor 中。它解决的核心问题是**音频开发与性能调试的黑盒问题**，允许开发者实时追踪音频资产的生命周期、监控音频线程性能、查看信号流程图，从而更高效地定位音频相关的性能瓶颈、资源泄漏或播放异常。其存在价值在于将传统依赖日志和截图的音频调试流程，转变为可视化、数据驱动的专业分析流程。

## 使用场景

- 你正在开发一个包含复杂动态音乐和大量音效的游戏，并需要精确分析各音频资产的内存占用与加载情况 → **使用 Audio Insights 的资产追踪与内存分析功能**。
- 你的游戏出现音频卡顿或延迟，需要定位是音频线程处理过载、资源未释放，还是系统API调用问题 → **使用 Audio Insights 的性能分析器和信号流监控**。
- 你需要测试不同音频设备（扬声器、耳机）的输出效果或验证音频空间化（如 3D 音效、HRTF）是否正确 → **使用 Audio Insights 的音频总线监控和空间化分析功能**。
- 你需要为项目创建自定义的音频分析通道（Channel）来监控特定类型的声音事件 → **参考插件模板扩展 Audio Insights**。

## 蓝图用法

本插件主要作为 **Unreal Insights 分析工具** 和 **编辑器停靠面板** 存在，其核心功能并非通过蓝图节点暴露给游戏运行时逻辑。交互主要发生在 `UnrealInsights` 应用程序或编辑器的 `Audio Insights` 窗口中。

### 核心交互界面

| 界面/窗口 | 说明 | 所在模块 |
|---|---|---|
| **Unreal Insights - Audio Insights** | 在 UnrealInsights 程序中打开 `.utrace` 文件后，可使用此标签页分析音频性能、资产、内存和信号流。 | `AudioInsights` |
| **Editor - Audio Insights** | Unreal Editor 内的停靠面板，提供更实时、更集成的音频监控与分析视图。 | `AudioInsightsEditor` |

## C++ 用法

本插件主要作为独立分析工具使用，其 C++ 接口主要用于**扩展**自定义的分析通道和数据处理逻辑，而非在游戏逻辑中直接调用。

### 扩展插件（创建自定义分析通道）

插件提供了一个模板项目，用于指导用户如何扩展 Audio Insights。核心步骤包括：

1.  **创建分析器与数据源**：继承自 `UE::Audio::Insights::TTraceAnalyzerBase` 和 `UE::Audio::Insights::TDataSourceBase`。
2.  **注册自定义通道**：在模块的 `StartupModule` 中，通过 `UE::Audio::Insights::IInsightsManager` 注册自定义的分析器和数据源。
3.  **在编辑器面板中添加视图**：继承 `FAudioInsightsTraceModule` 或相关类，在编辑器面板中为你的分析数据创建可视化的Widget。

*(详细实现请参考 `Templates/Basic/` 目录下的示例代码。)*

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| `AudioInsights` | EditorAndProgram | 核心分析模块，集成于 Unreal Insights 分析工具中，负责数据采集、分析和呈现。 |
| `AudioInsightsEditor` | EditorNoCommandlet | 编辑器集成模块，提供在 Unreal Editor 内访问音频分析功能的窗口和工具。 |
| `PLUGIN_NAME` (模板) | Runtime | 提供给用户用于创建自定义 Audio Insights 扩展插件的模板。 |

## 模块依赖

此插件的依赖旨在支撑其深度集成的分析能力，无特殊依赖（仅标准 Core/Engine/Slate 等）的常见模块已省略。

| 模块 | 用途 |
|---|---|
| `InsightsCore` | Unreal Insights 分析工具的核心框架，提供数据追踪和分析基础设施。 |
| `TraceAnalysis` | 用于处理 `.utrace` 跟踪文件的分析引擎。 |
| `TraceInsights` | Unreal Insights 应用程序的主要框架。 |
| `AudioWidgets` | 提供用于音频信号可视化（如波形图、频谱图）的 UI 组件。 |
| `AssetTools` | （编辑器模块）用于音频资产相关的编辑器操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-21 | `28c5c884` | [Audio Insights] Plugin template readme file to assist users when expanding Audio Insights with cust | 添加模板插件的 README，指导用户扩展自定义分析。 |
| 2026-05-19 | `a9b19eba` | [Audio Insights] Stop Event Log from automatically setting new items in the details panel when scrub | 修复事件日志面板在时间轴拖动时自动选中新项的问题。 |
| 2026-05-14 | `d492400a` | [Audio Insights] Fix localization for event log filter menu strings | 修复事件日志过滤器菜单的本地化字符串问题。 |
| 2026-05-14 | `64ecb7b0` | [Audio Insights] Setting Audio Insights and Audio Insights Runtime plugins to be Production | 将插件状态从 Beta 升级为 Production（生产就绪）。 |
| 2026-05-14 | `62b99116` | [Audio Insights] Add user-adjustable node padding multipliers to signal flow graph settings menu. Tw | 在信号流图设置中添加可调节的节点间距倍数。 |

### 维护评价

**积极维护中**。
- **创建时间**：2023年底，相对较新。
- **更新频率**：截至2026年5月仍有高频提交，内容包含功能增强、bug修复和状态升级（Beta -> Production）。
- **活跃度**：属于 Epic Games 直接维护的官方生产级工具，开发活跃，且近期完成了关键的生产状态标记。
- **推荐程度**：**强烈推荐**。对于任何涉及复杂音频功能的 Unreal 项目，Audio Insights 是官方提供的、功能完备的专业调试工具，应作为音频开发的标准流程工具集成使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights)
- [扩展模板](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioInsights/Templates/Basic)