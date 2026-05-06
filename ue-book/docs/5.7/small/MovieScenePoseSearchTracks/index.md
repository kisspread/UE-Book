# Movie Scene Pose Search Tracks

> Sequencer pose search tracks using the Anim Mixer

| 属性 | 值 |
|---|---|
| 中文名 | 序列器姿态搜索轨道 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MovieScenePoseSearchTracks` (Runtime), `MovieScenePoseSearchTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks) | |

## 总体用途

本插件为 Sequencer（序列器）提供基于姿态搜索（Pose Search）的轨道系统，允许用户在动画序列中通过姿态相似性查找并混合动画片段。它依赖于 **Anim Mixer**（动画混合器）和 **UAFPoseSearch**（Unreal Animation Framework 姿态搜索）插件，将姿态搜索功能集成到 Sequencer 的工作流程中，使动画师能够更直观地基于动作姿态匹配来创建过渡和混合。

该插件属于实验性阶段，主要用于在 Sequencer 中配合 Anim Mixer 使用姿态搜索轨道（Pose Search Track），以实现高级动画编排。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MovieScenePoseSearchTracks` | Runtime | 定义姿态搜索轨道、节拍（Section）及运行时数据模型 |
| `MovieScenePoseSearchTracksEditor` | Editor | 提供轨道编辑器支持（UI、细节面板、自定义操作） |

各模块的详细 API 请参见：
- [MovieScenePoseSearchTracks 模块文档](MovieScenePoseSearchTracks.md)
- [MovieScenePoseSearchTracksEditor 模块文档](MovieScenePoseSearchTracksEditor.md)

## 使用场景

- **动画制作流程优化**：在 Sequencer 中快速根据角色当前姿态搜索数据库中最匹配的动画片段，自动插入并混合。
- **动作过渡混合**：配合 Anim Mixer 在时间线上创建基于姿态搜索结果的动作过渡，减少手动调整渐变的步骤。
- **程序化动画编排**：在过场动画或游戏内序列中动态选取姿态匹配的动画，实现角色根据输入或上下文自动切换动作。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieScenePoseSearchTracks)
- [UAFPoseSearch 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/UAFPoseSearch)
- [MovieSceneAnimMixer 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer)