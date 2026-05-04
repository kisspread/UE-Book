# GeneSplicer Plugin v9.8.2

> GeneSplicer plugin for facial animation

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GeneSplicerLib` (Runtime), `GeneSplicerLibTest` (Runtime), `GeneSplicerModule` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2024-10-21 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer) | |

## 用途

GeneSplicer 是一个用于高级面部动画的插件，它提供了一套基于“基因剪接”技术的框架。该插件的核心目标是允许开发者通过程序化方式混合、变形和驱动复杂的面部网格体动画，通常用于实现高度可定制和动态的角色表情系统。它依赖于 `RigLogic` 和 `ControlRig` 插件，表明其底层可能结合了基于规则的逻辑和控制绑定技术来实现精细的面部控制。

## 使用场景

- 你需要为游戏角色创建一个高度可定制、支持程序化混合的面部表情系统。
- 你的项目需要实现复杂的、基于数据驱动的面部动画，例如根据对话内容或情绪状态动态生成表情。
- 你正在开发一个需要大量独特面部动画变体，但希望通过算法生成而非手动制作来提高效率的项目。

## 模块列表

| 模块 | 类型 | 一句话总结 |
|---|---|---|
| `GeneSplicerLib` | Runtime | 插件的核心算法库，包含面部动画基因剪接的底层实现和数据结构。 |
| `GeneSplicerModule` | Runtime | 插件的 UE 集成层，负责将核心库的功能暴露给引擎和蓝图系统。 |
| `GeneSplicerEditor` | Runtime | 提供编辑器内的工具和资产处理支持（尽管类型为 Runtime，但通常包含编辑器功能）。 |
| `GeneSplicerLibTest` | Runtime | 用于验证核心库功能的自动化测试模块。 |

*各模块的详细 API 和用法，请参阅对应的模块文档。*

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/GeneSplicer/Source/GeneSplicerLibTest)