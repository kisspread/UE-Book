# Animation Layering

> 

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AnimationLayering` (Runtime), `AnimationLayeringUncookedOnly` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimationLayering) | |

## 用途

这是一个实验性的动画插件，旨在提供一套用于动画层叠（Layering）的运行时框架和编辑器支持工具。它解决的核心问题是为复杂的动画混合与分层逻辑提供一个结构化的解决方案，可能用于实现更灵活、可维护的动画状态机或动画蓝图逻辑。

## 使用场景

- 你需要构建一个复杂的角色动画系统，其中多个动画层（如基础移动、上半身动作、面部表情）需要独立控制并混合。
- 你希望将动画逻辑模块化，以便在不同角色或项目间复用动画层。
- 你在开发一个需要高级动画混合功能的项目，并愿意尝试实验性的新工具。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| [AnimationLayering](AnimationLayering.md) | Runtime | 提供动画层叠的核心运行时功能、数据类型和蓝图接口。 |
| [AnimationLayeringUncookedOnly](AnimationLayeringUncookedOnly.md) | Runtime | 提供仅在编辑器（未打包）环境下使用的动画层叠相关工具和资产处理功能。 |

### 近期更新

- 2026-04-23 `ee8f5281` Animation Layering: Add missing CopyBoneMotion AnimGraphNode
- 2026-04-17 `1845d881` AnimationLayering: Add new public experimental Animation Layering plugin

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/Animation/AnimationLayering)