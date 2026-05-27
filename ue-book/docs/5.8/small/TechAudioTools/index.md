# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途

TechAudioTools 是一个**实验性**的音频工具集合，专为 UE5 的 **MetaSound** 系统提供扩展功能和编辑器增强。它解决的核心问题是为 MetaSound 图表提供更灵活的数据交互方式，特别是通过引入基于 **Model-View-ViewModel (MVVM)** 模式的数据字面量（Literal）视图模型，简化 MetaSound 节点的参数输入和配置流程。这使得音频设计师和技术美术能够在 MetaSound 图表中以更直观、结构化的方式操作数据，而无需编写复杂的 C++ 代码或创建大量自定义 MetaSound 节点。

## 使用场景

-   **你需要在 MetaSound 图表中处理复杂的结构化数据** → 使用 `TechAudioToolsMetaSound` 模块提供的字面量视图模型，将结构体（如向量、变换）直接暴露为易于在编辑器中配置的输入引脚。
-   **你需要为 MetaSound 开发自定义的编辑器体验** → 使用 `TechAudioToolsMetaSoundEditor` 模块来集成和扩展 MetaSound 编辑器的 UI，例如为自定义字面量类型创建专用的配置界面。
-   **你正在开发需要与 MetaSound 深度集成的音频工具或系统** → 作为 Runtime 模块，`TechAudioTools` 和 `TechAudioToolsMetaSound` 提供了在运行时与 MetaSound 图表和字面量视图模型交互的 API。

## 模块列表

| 模块 | 类型 | 一句话说明 |
|---|---|---|
| `TechAudioTools` | Runtime | 核心音频工具运行时库，提供基础类型和通用功能。 |
| `TechAudioToolsMetaSound` | Runtime | 为 MetaSound 提供字面量（Literal）视图模型，实现基于 MVVM 模式的数据绑定和配置。 |
| `TechAudioToolsMetaSoundEditor` | Editor | 集成在 MetaSound 编辑器中，提供字面量视图模型的自定义编辑界面和交互逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 重构并整合了引脚类型注册及相关的编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回退了一个导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 重构并整合了引脚类型注册及相关的编辑器行为。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量视图模型添加了事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound(Document)Template。 |

### 维护评价

TechAudioTools 是一个非常年轻的插件（创建于 2025 年 4 月），目前处于**活跃维护**状态。从提交历史看，最近一个月内有多次功能性更新和重构（如引脚类型整合、事务支持），表明 Epic Games 的开发团队正在积极开发和迭代此插件的功能。

**需要注意**：
-   该插件标记为 **实验性** (`IsBetaVersion=true`, `IsExperimentalVersion=true`) 且**默认未启用**，这意味着其 API 可能会发生不兼容的更改，不建议在需要稳定性的核心项目中使用。
-   它依赖于 **ModelViewViewModel (MVVM)** 插件，这是一个同样较新的框架。

**推荐使用**：适合在**技术预研、内部工具开发或希望在 MetaSound 中探索更高效工作流**的团队中小范围使用。建议关注其更新日志，并准备好应对可能的 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- 官方文档 (无)
- 测试用例 (信息不足)