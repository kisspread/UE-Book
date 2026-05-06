# DaySequence

> （描述为空，基于功能推断）DaySequence 插件提供基于 Sequencer 的昼夜循环系统，允许在关卡中创建动态时间驱动的内容。

| 属性 | 值 |
|---|---|
| 中文名 | 昼夜序列 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资源、编辑器配置） |
| 模块 | `DaySequence` (Runtime), `DaySequenceEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DaySequence) | |

## 总体用途

DaySequence 是一个实验性插件，用于在 Unreal Engine 中实现高度灵活的昼夜循环系统。它利用 LevelSequence 作为底层驱动，将时间轴与游戏内时间（如一天中的小时）绑定，从而控制光照、天空、环境等属性的动态变化。通过 `DaySequenceModifierComponent` 等运行时组件，开发人员可以方便地设置昼夜循环参数，并在编辑器（基于 Sequencer）中可视化编辑。

该插件主要解决传统昼夜循环难以与 Sequencer 工作流集成的问题，让美术和设计人员能在熟悉的序列编辑器中调整昼夜关键帧，同时保持运行时性能可控。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [DaySequence](DaySequence.md) | Runtime | 提供核心运行时逻辑，包括 `DaySequenceModifierComponent`、时间计算、昼夜周期管理等 |
| [DaySequenceEditor](DaySequenceEditor.md) | Editor | 提供编辑器集成，包含自定义 Sequencer 轨道、面板、细节定制，方便编辑昼夜序列 |

## 使用场景

- **开放世界昼夜循环**：在地面或天空光照、后处理、植被动画等元素上应用基于时间的关键帧动画，实现平滑的昼夜过渡。
- **时间敏感的游戏机制**：如特定时间刷新的资源、敌人行为变化、NPC 日程等，通过 DaySequence 的时间驱动机制触发。
- **电影化过场与动态时间**：在过场动画或脚本事件中控制时间流逝速度、暂停或跳转，实现电影式的时间调度。
- **编辑器预览与迭代**：美术人员可直接在编辑器中使用 Sequencer 调节昼夜关键帧，无需编写代码或频繁运行游戏。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/DaySequence)
- [DaySequence 运行时模块文档](DaySequence.md)
- [DaySequenceEditor 编辑器模块文档](DaySequenceEditor.md)