# Sequencer Anim Mixer

> System for mixing layered animation in sequences

| 属性 | 值 |
|---|---|
| 中文名 | 序列器动画混合器 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（插件内容） |
| 模块 | `MovieSceneAnimMixer` (Runtime), `MovieSceneAnimMixerEditor` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-20 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer) | |

## 总体用途

Sequencer Anim Mixer 是一个实验性插件，为 Unreal Engine 的 Sequencer 提供**分层动画混合**能力。它允许在序列中将多个动画层（如全身、上半身、面部等）叠加混合，实现局部动画覆盖、动态权重调节等功能。适用于需要精细控制角色动画的复杂场景，如过场动画、角色移动中的姿势混合等。

## 模块列表

| 模块 | 类型 | 一句话总结 | 文档 |
|---|---|---|---|
| `MovieSceneAnimMixer` | Runtime | 运行时核心，定义动画混合数据结构、评估逻辑与轨道系统 | [MovieSceneAnimMixer.md](./MovieSceneAnimMixer.md) |
| `MovieSceneAnimMixerEditor` | UncookedOnly | 编辑器集成，提供自定义轨道 UI、权重编辑、序列配置界面 | [MovieSceneAnimMixerEditor.md](./MovieSceneAnimMixerEditor.md) |

## 使用场景

- **角色过场动画**：在 Sequencer 中为一个角色叠加多个动画层（如行走 + 挥手），通过权重控制局部混合。
- **动态动画调整**：运行时根据游戏状态（如受伤、瞄准）切换或混合不同动画层，实现平滑过渡。
- **动画测试与迭代**：在编辑器中直接预览分层混合效果，快速调整各层权重和顺序。
- **复杂动作组合**：将全身动作（如跑步）与上半身动作（如射击）分开管理，再通过混合系统合成最终姿势。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneAnimMixer)
- [模块文档 · MovieSceneAnimMixer](./MovieSceneAnimMixer.md)
- [模块文档 · MovieSceneAnimMixerEditor](./MovieSceneAnimMixerEditor.md)