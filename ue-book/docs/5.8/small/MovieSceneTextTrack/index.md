# Movie Scene Text Track

> Deprecated plugin. Text support moved to Movie Scene Tracks (built-in).

| 属性 | 值 |
|---|---|
| 中文名 | 场景文本轨道 |
| 分类 | Text |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieSceneTextTrack` (Runtime), `MovieSceneTextTrackEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-09 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack) | |

## 用途

此插件**已被废弃**。它最初用于为 Sequencer（电影场景编辑器）提供文本轨道，允许用户为 UMG (UI)、3D Text 等组件中的文本属性创建关键帧动画，特别是支持本地化文本。该功能已迁移并合并到引擎内置的 **Movie Scene Tracks** 模块中，无需再使用此插件。

## 使用场景

- **历史用途**：如果你需要在 Sequencer 中为 UMG 界面或 3D 场景中的文本组件制作动画（例如，让文本淡入、改变内容并配合本地化），曾需要此插件。
- **当前建议**：**不要使用此插件**。应直接使用引擎内置的 Sequencer 功能来实现文本动画。

## 蓝图用法

此插件已被废弃，其功能已内置到引擎中。任何相关蓝图节点（如文本轨道相关操作）应通过内置的 Sequencer 功能访问。

## C++ 用法

此插件已被废弃。其 C++ 模块（`MovieSceneTextTrack` 和 `MovieSceneTextTrackEditor`）不应在新项目中依赖。相关功能已集成到引擎的 `MovieScene` 核心模块中。

## Demo 示例

由于此插件已被废弃，不建议创建新的使用示例。如需了解文本轨道在 Sequencer 中的用法，请参考引擎内置 Movie Scene Tracks 的相关文档或示例。

## 模块依赖

无特殊依赖（仅标准 Core/Engine/MovieScene 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-08-07 | `b074e345` | Movie Scene: migrate text track to movie scene tracks | 功能迁移：将文本轨道功能合并至内置电影场景轨道模块。 |
| 2025-06-13 | `b3edcb21` | Replace some usages of FORCEINLINE with inline in MovieScene modules. | 代码维护：将部分模块中的 `FORCEINLINE` 替换为 `inline`。 |
| 2024-12-02 | `027924bd` | Sequencer: Added missing CurveValueType typedefs, SupportsDefaults, and EvaluateChannel | 功能补充：为曲线评估添加缺失的类型定义与接口。 |
| 2024-11-27 | `33517915` | Movied previously committed squencer changes for music mode into a new Musical Mode plugin | 重构：将音乐模式相关的 Sequencer 代码迁移到新的插件中。 |
| 2024-10-23 | `6145872a` | MUSIC_IN_SEQUENCER [Initial Check-In] | 功能引入：首次提交 Sequencer 音乐模式的基础支持。 |

### 维护评价

此插件已**正式废弃**。根据最后一次提交 (`b074e345`)，其核心功能已明确迁移至引擎内置模块。`.uplugin` 中 `Installed: false` 也表明其不默认安装。**强烈不推荐在新项目中使用此插件**，旧项目也应尽快迁移到内置功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/MovieSceneTextTrack)