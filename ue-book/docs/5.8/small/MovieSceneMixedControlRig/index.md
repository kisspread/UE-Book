# Sequencer Mixed Control Rig

> System for using the Anim Mixer to mix control rig tracks

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `MovieSceneMixedControlRig` (Runtime), `MovieSceneMixedControlRigEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig) | |

## 用途

该插件为 Unreal Engine 的 **Sequencer**（序列器）和 **Control Rig**（控制绑定）系统提供了一个扩展功能。其核心目的是允许动画师在 Sequencer 时间线上，利用 **Anim Mixer**（动画混合器）的功能，直接对 Control Rig 轨道进行混合操作。这解决了在 Sequencer 中编辑复杂 Control Rig 动画时，难以直观地进行多轨道动画混合与过渡的问题，使得动画流程更加高效和直观。

## 使用场景

- 你正在使用 Control Rig 制作复杂的角色动画，并在 Sequencer 中进行编辑和合成。
- 你需要在 Sequencer 时间线上，将多个 Control Rig 动画轨道（例如，不同的姿态或动画层）进行平滑混合或过渡。
- 你希望利用 Sequencer 已有的动画混合工具（Anim Mixer）来管理 Control Rig 动画，而不是在蓝图或代码中手动处理混合逻辑。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `MovieSceneMixedControlRig` | Runtime | 提供核心运行时逻辑，定义混合 Control Rig 轨道所需的数据结构和评估功能。 |
| `MovieSceneMixedControlRigEditor` | Runtime | 提供编辑器集成，将混合功能注册到 Sequencer 编辑器界面中，使用户能够操作。 |

### 近期更新

- 2026-04-21 `eb0331ca` 动画混合器：为动画混合器的绑定、混合器轨道和混合器层添加了“烘焙到控制绑定”和“动画序列”支持。
- 2026-04-17 `62f614c6` Sequencer：修复了在动画混合器中使用多层根运动时，控制绑定 Gizmo 绘制偏移的问题。
- 2026-04-07 `8bf4fb4b` Sequencer：围绕层重构了混合器评估系统；引入了新的遮罩混合系统。
- 2026-03-31 `b48e7f74` 修复了 MovieScene 的关闭问题。
- 2026-03-31 `c7aaaa03` Sequencer：在动画混合器中为控制绑定启用了根运动提取功能。

### 维护评价

该插件处于**活跃开发**状态。在约三周的时间内有五次提交，更新频率较高。提交内容涵盖了新功能开发（动画混合器支持、根运动提取）、关键问题修复以及核心评估系统的重构，表明团队正在积极完善其功能并优化架构，很可能在为即将到来的引擎版本（如5.8）做准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/MovieSceneMixedControlRig)
- [MovieSceneMixedControlRig 模块文档](MovieSceneMixedControlRig.md)
- [MovieSceneMixedControlRigEditor 模块文档](MovieSceneMixedControlRigEditor.md)