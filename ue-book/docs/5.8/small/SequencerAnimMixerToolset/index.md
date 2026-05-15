# SequencerAnimMixerToolset

> EDA toolset for the Sequencer Animation Mixer

| 属性 | 值 |
|---|---|
| 中文名 | 动画混合器工具集 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、工具集） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `EditorDevelopmentAssistant` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2026-04-10 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SequencerAnimMixerToolset) | |

## 用途

此插件是一个 **专用工具集插件**，是 UE5 `SequencerTools` 大型工具集的一个子集。它将 **Sequencer 动画混合器 (Anim Mixer)** 相关的编辑助手工具从主 `AnimationAssistantToolset` 中分离出来，成为一个独立的插件。

其核心目的是**依赖解耦**。主 `AnimationAssistantToolset` 会被 `FortniteGame` 等大型项目依赖，而动画混合器功能依赖于 `MovieSceneAnimMixer` 模块。将这部分工具独立出来，可以避免为那些不需要动画混合器功能的项目引入不必要的模块依赖。

## 使用场景

- 你正在使用 Sequencer 进行复杂的动画混合、分层和过渡动画编辑。
- 你的项目需要使用 Sequencer 的“动画混合器”功能来创建更高级的动画效果。
- 你希望避免为整个 Sequencer 工具集引入 `MovieSceneAnimMixer` 模块的依赖，但又需要它的编辑工具。

## 蓝图用法

该插件主要提供蓝图资产形式的编辑器工具，而非可直接在运行时蓝图中调用的节点。根据提交信息，它包含 **21 个专用的动画混合器工具**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateAnimMixerLayer` | 在 Sequencer 动画混合器中创建新的混合器层 | `AnimMixerAssistantToolset` |
| `EditTransitionParams` | 编辑动画混合器中过渡混合的参数 | `AnimMixerAssistantToolset` |
| `ManageDecorations` | 管理动画混合器层的装饰（如名称、颜色等） | `AnimMixerAssistantToolset` |

**说明**: 由于当前分析无源码文件（源码文件数为 0），上述函数名为根据提交信息中的描述 “mixer layers, transitions, and decorations” 推断的示例性命名。实际使用时，这些工具通常以 `Editor Utility Widget` 或 `Blutility` 的形式在 Sequencer 编辑器内通过按钮或菜单触发。

### 使用示例（蓝图描述）

这些工具无法在普通的游戏逻辑蓝图中调用。它们作为 Sequencer 的“助手”工具存在：
1.  在编辑器中，启用该插件。
2.  打开 Sequencer 编辑器，添加或编辑一个动画轨道。
3.  应该能在 Sequencer 的工具栏、菜单或特定面板中找到“动画混合器”相关的工具按钮。
4.  点击这些按钮将执行预设的蓝图逻辑，例如快速创建混合层、批量设置过渡曲线等。

## C++ 用法

该插件本身**不提供新的 C++ 公共 API**。其价值在于提供蓝图资产工具。与动画混合器直接交互的 C++ 脚本扩展（如提交信息中提到的 `MovieSceneAnimMixer` 插件中的 C++ 扩展）是另一个独立的模块。

## Demo 示例

由于该插件以蓝图资产工具为主，且当前分析无直接源码，建议参考 UE5 编辑器中已有的 `SequencerTools` 使用模式。其结构类似于一组预置的 `Editor Utility Widget`。

## 模块依赖

从 `.uplugin` 文件的依赖项可以看出，要使此插件正常工作，你的项目/模块需要依赖：

| 模块 | 用途 |
|---|---|
| `ToolsetRegistry` | 用于注册和管理 EDA (Editor Development Assistant) 工具集 |
| `MovieSceneAnimMixer` | 提供动画混合器的核心运行时功能，是本插件工具集操作的对象 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-10 | `77af3950` | [EDA] Add SequencerTools toolset with Anim Mixer split into separate plugin | 首次提交，将动画混合器工具从主工具集分离为独立插件 |

### 维护评价

这是一个**全新创建的实验性插件**。
- **创建时间**：刚刚创建（2026-04-10）。
- **更新频率**：目前只有初始提交。
- **活跃状态**：作为大型 Sequencer 工具集重构的一部分而创建，预计会随主项目同步维护。
- **已知限制**：作为实验性（`IsExperimentalVersion: true`）且默认不启用（`EnabledByDefault: false`）的插件，其 API 和功能可能在未来发生变化。主要作为编辑器开发助手存在。
- **推荐**：如果你需要 Sequencer 动画混合器的专用编辑工具，且接受其当前的实验性状态，可以启用并使用。对于纯游戏运行时逻辑，无需关注此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/SequencerAnimMixerToolset)
- [测试用例] (当前分析无公开测试用例路径)