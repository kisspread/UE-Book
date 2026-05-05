# SequencerAnimMixerToolset

> EDA toolset for the Sequencer Animation Mixer

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器工具资产） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SequencerAnimMixerToolset) | |

## 用途

这是一个纯内容插件，为 Sequencer 的 Animation Mixer 功能提供 EDA（Editor Design Automation）工具集。它本身不包含任何 C++ 代码，而是作为 Sequencer 动画混合工作流的编辑器工具集合，将 Anim Mixer 相关的工具从主插件中拆分出来，以独立插件形式提供。

该插件依赖 `ToolsetRegistry`（工具集注册系统）和 `MovieSceneAnimMixer`（动画混合核心功能），通过工具集注册机制将动画混合相关的编辑器工具集成到 Sequencer 工作流中。

## 使用场景

- 你在 Sequencer 中需要使用动画混合（Animation Mixer）功能的编辑器工具 → 启用此插件
- 你需要将多个动画轨道混合、叠加或分层编辑 → 配合 MovieSceneAnimMixer 使用此工具集
- 你正在使用 EDA 工具集框架管理 Sequencer 扩展工具 → 此插件是工具集框架的一部分

## 蓝图用法

此插件为纯内容插件，不包含 C++ 源码，因此没有可直接调用的蓝图节点。工具功能通过 Sequencer 编辑器界面以工具面板形式提供。

## C++ 用法

此插件不包含 C++ 模块，无头文件可引入。

## Demo 示例

不适用。此插件为纯内容插件，不包含可编译的 C++ 代码。

## 模块依赖

此插件本身无模块，但依赖以下插件：

| 插件 | 用途 |
|---|---|
| `ToolsetRegistry` | 提供 EDA 工具集注册框架，用于将工具注册到编辑器中 |
| `MovieSceneAnimMixer` | 提供 Sequencer 动画混合的核心功能 |

## 维护状态

### 近期更新

- 2026-04-10 `77af3950` [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin

### 维护评价

- **创建时间**：2026-04-10，非常新的插件
- **更新频率**：仅有 1 次提交，为初始创建
- **维护状态**：🆕 新创建，尚处于早期阶段
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，表明该功能仍处于实验阶段
- **已知限制**：作为纯内容插件，功能完全依赖于 ToolsetRegistry 和 MovieSceneAnimMixer 两个依赖插件

⚠️ **注意**：此插件为实验性功能，API 和功能可能会发生变化。由于创建时间极短且仅有一次提交，建议在生产环境中谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SequencerAnimMixerToolset)
- [ToolsetRegistry 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/ToolsetRegistry)
- [MovieSceneAnimMixer 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieSceneAnimMixer)