# Gameplay Abilities

> Adds GameplayEffect and GameplayAbility classes to handle complicated gameplay interactions.

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayAbilities` (Runtime), `GameplayAbilitiesEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

Gameplay Abilities (GAS) 是 Unreal Engine 中一套强大且高度模块化的技能系统框架。它不仅仅是一个简单的技能触发器，而是一个完整的、数据驱动的运行时系统，用于管理复杂的游戏逻辑，包括技能激活、效果应用、属性（Attribute）管理、冷却（Cooldown）计算、成本（Cost）消耗以及技能间的交互。

它解决的核心问题是：在大型、复杂的游戏项目中（如 RPG、MOBA、动作游戏），如何以可维护、可扩展且数据驱动的方式，实现成百上千种技能、Buff/Debuff、状态效果及其复杂的叠加、覆盖和交互逻辑。GAS 通过将游戏逻辑抽象为 `GameplayAbility`（技能）和 `GameplayEffect`（效果）两个核心概念，并配合 `AbilitySystemComponent`（ASC）进行管理，极大地简化了这类系统的开发。

## 使用场景

-   **RPG 游戏**：实现复杂的技能树、法术系统、装备附魔效果、持续伤害（DOT）、治疗、属性增减益（Buff/Debuff）。
-   **MOBA 游戏**：管理英雄技能的冷却、法力消耗、技能升级、命中判定、以及各种技能效果（击飞、沉默、减速）的叠加与免疫。
-   **动作/格斗游戏**：实现连招系统、状态机驱动的攻击、受击反馈、霸体、格挡等状态管理。
-   **任何需要复杂游戏逻辑交互的项目**：当你的游戏逻辑开始变得难以用简单的状态机或事件分发来管理时，GAS 提供了一个经过验证的、可扩展的解决方案。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| **GameplayAbilities** | Runtime | 核心运行时模块，包含所有游戏逻辑类（`UAbilitySystemComponent`, `UGameplayAbility`, `UGameplayEffect` 等）以及网络同步、预测、GameplayCue 等系统。 |
| **GameplayAbilitiesEditor** | UncookedOnly | 编辑器模块，提供用于创建和编辑 `GameplayAbility` 和 `GameplayEffect` 蓝图资产的自定义编辑器工具和界面。 |

*各模块的详细 API 和用法，请参阅对应的模块文档：*
-   [GameplayAbilities 模块文档](GameplayAbilities.md)
-   [GameplayAbilitiesEditor 模块文档](GameplayAbilitiesEditor.md)

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities/Tests)