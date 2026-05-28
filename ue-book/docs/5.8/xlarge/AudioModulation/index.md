# Audio Modulation

> Default implementation of Audio Modulation in the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频调制 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频相关蓝图资产与元数据） |
| 模块 | `AudioModulation` (Runtime), `AudioModulationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation) | |

## 用途

Audio Modulation 为 Unreal 音频引擎提供了一套完整的音频参数调制框架。它解决了游戏音频中"动态混音"的核心问题：如何在运行时根据游戏状态（如战斗、对话、环境变化）自动、平滑地调整音量、音高等参数，而不需要手动管理每个音效的属性。

该插件引入了 **Bus（总线）**、**Bus Mix（总线混合）** 和 **Modulation Parameter（调制参数）** 三个核心概念：
- **Sound Control Bus**：类似于 DAW 中的控制总线，承载一个可被调制的参数值。
- **Sound Control Bus Mix**：将多个 Bus 的参数组合在一起，便于批量控制和快照切换。
- **调制源**（如 LFO、Sound Wave、MetaSound 输出等）驱动 Bus 上的值，Bus 再影响挂载的音频源。

这个插件默认不启用（`EnabledByDefault: false`），需要手动在项目设置中启用。它依赖 MetaSound 和 WaveTable 插件。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| [AudioModulation](AudioModulation.md) | Runtime | 核心调制运行时框架：Bus、BusMix、参数源、波表 LFO 等 |
| [AudioModulationEditor](AudioModulationEditor.md) | Editor | 编辑器支持：资产类型注册、自定义细节面板、资产工厂 |

## 使用场景

- 你在做一个开放世界游戏，需要在进入室内/室外、战斗/和平等状态间平滑切换环境音和音乐音量 → 用 Bus Mix 快照切换
- 你需要让某个音效的音量随玩家距离/生命值等游戏变量自动变化 → 用 Sound Control Bus 驱动调制
- 你想用 LFO（低频振荡器）为持续音效添加周期性的音量/音高变化 → 用 WaveTable LFO 作为调制源
- 你在使用 MetaSound 图表，需要将 MetaSound 输出值反馈到音频参数 → 通过 MetaSound Modulation 节点桥接
- 你需要在 Sequencer 中沿时间轴控制音频参数 → 使用 Audio Modulation 的 Sequencer Track 支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation)
- [AudioModulation 模块文档](AudioModulation.md)
- [AudioModulationEditor 模块文档](AudioModulationEditor.md)