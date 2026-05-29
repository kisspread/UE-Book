# Customizable Sequencer Tracks (Experimental)

> Library that provides a blueprintable track type that can be added to sequencer

| 属性 | 值 |
|---|---|
| 中文名 | 可定制序列器轨道 |
| 分类 | Runtime |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CustomizableSequencerTracks` (Runtime), `CustomizableSequencerTracksEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-08-11 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks) | |

## 用途

该插件的核心功能是扩展 UE5 的 Sequencer（定序器）。它允许开发者通过蓝图系统，创建和自定义全新的、可添加到 Sequencer 时间轴上的轨道类型。这解决了 Sequencer 原生轨道功能有限、需要编写 C++ 才能扩展的痛点，使得策划或开发者能够更快速地为游戏内的特殊动画需求或过场动画系统实现自定义逻辑。

## 使用场景

- 你需要在 Sequencer 时间轴上控制一个非标准的游戏对象属性（例如：自定义粒子系统的复杂参数、动态材质实例的特定标量值），而现有轨道无法满足需求。
- 你希望快速原型化一个新的 Sequencer 功能，但不想或无法编写 C++ 代码，想在蓝图中完成轨道逻辑的开发和调试。

## 模块列表

- **`CustomizableSequencerTracks`** (Runtime): 核心运行时模块，提供蓝图化轨道类型的基础类和逻辑。
- **`CustomizableSequencerTracksEditor`** (Editor): 编辑器集成模块，负责将自定义轨道在 Sequencer 编辑器 UI 中进行注册和展示。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/MovieScene/CustomizableSequencerTracks/Tests) （如有）