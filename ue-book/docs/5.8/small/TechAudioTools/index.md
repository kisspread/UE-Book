# Tech Audio Tools

> A collection of audio-related tools and utilities.

| 属性 | 值 |
|---|---|
| 中文名 | 音频技术工具集 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时功能模块、编辑器扩展） |
| 模块 | `TechAudioTools` (Runtime), `TechAudioToolsMetaSound` (Runtime), `TechAudioToolsMetaSoundEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-04-22 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools) | |

## 用途
该插件是一个面向 MetaSound 系统的高级工具与扩展集合，旨在提供更强大、更灵活的音频设计与编程能力。它通过添加新的自定义节点、数据类型和编辑器工具，来解决 MetaSound 原生功能在复杂音频项目中的局限性，使音频设计师和技术美术师能以更高效、更可视化的方式构建和调试音频逻辑。

## 使用场景
- 你需要扩展 MetaSound 的节点库，使用更专业或项目特定的音频处理节点 → 使用 `TechAudioToolsMetaSound` 提供的自定义节点。
- 你希望在 MetaSound 编辑器中拥有更便捷的资产浏览、编辑或调试工具 → 使用 `TechAudioToolsMetaSoundEditor` 提供的编辑器扩展。
- 你需要通过可视化的视图模型（MVVM）模式来管理音频资产的参数或配置 → 此插件依赖 `ModelViewViewModel` 插件，旨在为此类需求提供支持。

## 蓝图用法
此插件的核心功能主要面向编辑器（MetaSound 图形编辑）和底层 C++ 开发，直接的蓝图节点较少。主要的使用方式是在 MetaSound 图形编辑器中操作由插件提供的新节点和工具。
详细的 API（包括自定义节点和可用工具）请参考各子模块文档：`TechAudioToolsMetaSound.md` 和 `TechAudioToolsMetaSoundEditor.md`。

## C++ 用法
插件功能主要通过其子模块的 C++ 接口提供。
- **运行时模块** (`TechAudioTools`, `TechAudioToolsMetaSound`) 可能提供用于扩展 MetaSound 系统的基类、数据类型或工厂类。
- **编辑器模块** (`TechAudioToolsMetaSoundEditor`) 提供用于构建自定义编辑器工具和视图模型的 API。
具体的类和接口使用方法，请查阅对应模块的详细文档。

## Demo 示例
由于此插件主要为 MetaSound 提供扩展功能，建议在启用插件后，在 MetaSound 编辑器中查看新增的节点和工具面板，或参考引擎内相关的测试用例或示例项目来了解具体用法。

## 模块依赖
要使用此插件的功能，你的项目或模块通常需要依赖以下插件（已在 .uplugin 中声明）：
| 插件 | 用途 |
|---|---|
| `Metasound` | 核心音频图系统，本插件在此基础上进行扩展。 |
| `ModelViewViewModel` | 提供视图模型架构支持，用于构建编辑器中的数据驱动UI。 |

*注：插件的 Build.cs 可能还会依赖其他常见引擎模块（如 `Core`, `Engine`），此处仅列出插件间独特的依赖关系。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-16 | `cb44584a` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 整合了 MetaSound 引脚类型注册及其相关的编辑器行为。 |
| 2026-04-15 | `2010cdbb` | [Backout] - CL52717658 - CIS Compile Error | 回滚了一次导致编译错误的提交。 |
| 2026-04-14 | `d9dda16b` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior in | 对 MetaSound 引脚系统进行了重大重构和整合。 |
| 2026-04-09 | `77ec5174` | [TechAudioTools] Added support for transactions in MetaSound Literal Viewmodels | 为 MetaSound 字面量的视图模型添加了事务支持。 |
| 2026-03-16 | `e8ed118a` | DocumentConfiguration Rename to MetaSound(Document)Template | 将 DocumentConfiguration 重命名为 MetaSound(Document)Template。 |

### 维护评价
该插件创建于 **2025年4月**，至今约 **1年**。从 git 历史来看，近期（2026年3-4月）有密集的功能更新和重构活动，表明其处于**活跃维护**的实验性开发阶段。
由于 `IsBetaVersion=true` 且 `IsExperimentalVersion=true`，其 API 和功能可能在未来版本中发生变化。目前来看，它是一个**正在积极发展**的前沿工具集，适合希望探索或依赖 MetaSound 高级扩展功能的开发者使用，但需注意其潜在的不稳定性。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/TechAudioTools/Tests) *(如果存在)*