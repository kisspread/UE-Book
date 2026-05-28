# Gameplay Abilities

> Adds GameplayEffect and GameplayAbility classes to handle complicated gameplay interactions.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏能力 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayAbilities` (Runtime), `GameplayAbilitiesEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

GameplayAbilities (GAS) 是 Unreal Engine 中一个功能强大、高度模块化的游戏逻辑框架。它并非一个简单的“技能系统”，而是一套用于定义、激活、管理和同步复杂游戏逻辑的底层架构。其核心解决以下问题：

1.  **标准化的游戏逻辑**：为技能（GameplayAbility）、效果（GameplayEffect）和属性集（AttributeSet）提供一套标准的数据结构和生命周期管理，避免为每个游戏重新设计基础框架。
2.  **复杂的数值修改**：通过 GameplayEffect 和执行计算（GameplayEffectExecutionCalculation），实现可叠加、可预测、可复制的复杂属性修改（如伤害、治疗、Buff/Debuff）。
3.  **网络同步**：内置了用于多人游戏的属性同步和技能激活/预测回滚机制，确保客户端和服务端状态的一致性。
4.  **模块化与可扩展性**：通过 GameplayTask、GameplayCue 和自定义 AbilitySystemComponent，可以灵活地扩展功能，实现从简单到极其复杂的玩法系统。

## 使用场景

*   你正在开发一款**RPG、MOBA、MMO或动作游戏**，需要实现数十甚至上百种拥有不同冷却时间、消耗、条件和效果的技能。
*   你的游戏包含**复杂的属性系统**，需要支持百分比修改、属性依赖、修改器（Modifier）堆叠和优先级。
*   你正在开发一款**多人竞技游戏**，需要一套经过验证的、能够处理技能预测和回滚的网络同步方案。
*   你希望将游戏逻辑（技能、效果）与表现（动画、特效）解耦，并允许设计师通过蓝图或数据驱动方式配置技能。

## 蓝图用法

GAS 框架主要通过 C++ 构建核心逻辑，但提供了大量暴露给蓝图的接口，用于配置、触发和查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ActivateAbility` | 激活一个 GameplayAbility 实例 | `UAbilitySystemComponent` |
| `ApplyGameplayEffectToSelf` / `ApplyGameplayEffectToTarget` | 将一个 GameplayEffect 应用到自身或目标 | `UAbilitySystemComponent` |
| `GetGameplayAttributeValue` | 获取指定属性（Attribute）的当前基础值 | `UAbilitySystemComponent` |
| `MakeGameplayEffectSpec` | 从一个 GameplayEffect CDO 创建一个可修改的规格实例 (Spec) | `UAbilitySystemComponent` |
| `SendGameplayEventToActor` | 向目标的 AbilitySystemComponent 发送一个事件，可能触发技能 | `UAbilitySystemBlueprintLibrary` |
| `EffectContextGetHitResult` | 从效果上下文中提取命中结果 (HitResult) | `UAbilitySystemBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **激活一个技能**：在角色蓝图中，通过 `InputAction` 事件触发 `ActivateAbility` 节点，并传入要激活的 `GameplayAbility` 类。
2.  **应用伤害效果**：在一个攻击能力 (AttackAbility) 的执行逻辑中，先通过 `MakeGameplayEffectSpec` 创建伤害效果的实例，设置好基础伤害值，然后使用 `ApplyGameplayEffectToTarget` 将其应用到被命中的敌人。
3.  **监听属性变化**：在 UI 蓝图中，使用 `BindGameplayEvent` 或通过 `AbilitySystemComponent` 的委托来监听生命值 (Health) 属性的变化，并更新血条。

## C++ 用法

GAS 是一个深度 C++ 框架，核心类通常需要被继承和扩展。

### 头文件引入

```cpp
#include "AbilitySystemComponent.h"
#include "GameplayAbility.h"
#include "GameplayEffect.h"
#include "AttributeSet.h"
```

### 基本用法

一个最简单的自定义技能（GameplayAbility）：
```cpp
// MyGameplayAbility.h
#pragma once
#include "Abilities/GameplayAbility.h"
#include "MyGameplayAbility.generated.h"

UCLASS()
class UMyGameplayAbility : public UGameplayAbility
{
    GENERATED_BODY()
public:
    // 激活技能时调用
    virtual void ActivateAbility(...) override;
};
```
*(来源：常见用法模式)*

### 进阶用法

扩展属性集（AttributeSet）并使用执行计算：
```cpp
// MyAttributeSet.h
#pragma once
#include "AttributeSet.h"
#include "MyAttributeSet.generated.h"

UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()
public:
    // 使用宏定义属性，自动处理蓝图访问和网络同步
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health, Category = "Vital")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)
    // ... 其他属性和回调
};

// 在 GameplayEffectExecutionCalculation 的执行函数中修改属性
void UMyDamageExecution::Execute_Implementation(const FGameplayEffectCustomExecutionParameters& ExecutionParams, FGameplayEffectCustomExecutionOutput& OutExecutionOutput) const
{
    // 计算伤害
    OutExecutionOutput.AddOutputModifier(FGameplayModifierEvaluatedData(UMyAttributeSet::GetHealthAttribute(), EGameplayModOp::Additive, -DamageAmount));
}
```
*(来源：框架设计模式)*

## Demo 示例

此框架极为庞大，一个最小可运行的“Demo”需要初始化 AbilitySystemComponent、定义属性集、创建技能和效果资产。建议参考官方文档或社区教程中关于“GAS (Gameplay Ability System) Quick Start”的示例。其核心结构是：Actor -> UAbilitySystemComponent -> AttributeSet + GameplayAbilities。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | GAS 中大量使用 GameplayTags 来标识技能、效果、状态和事件，是其核心依赖。 |
| `Niagara` | 插件配置中强制依赖。用于 GameplayCue 集成，将粒子效果与游戏逻辑关联。 |
| `DataRegistry` | 插件配置中强制依赖。可能用于数据驱动的技能或效果配置。 |

**注意**：该插件默认**禁用** (`EnabledByDefault: false`)。你必须在你的项目 `.uproject` 文件或编辑器插件设置中手动启用 `GameplayAbilities` 插件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量被截断为浮点数导致的编译警告。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了当参数为64位时格式化说明符仍使用32位（反之亦然）导致的问题。 |
| 2026-04-24 | `6962ad56` | Fix incorrect reset of GameplayEffectList Next Ptr. | 修复了 GameplayEffectList 中 Next 指针的错误重置问题。 |
| 2026-04-16 | `47285bc0` | Added logging on deletion of gameplay effect to help track down rare crash. Logging can be disabled | 为 GameplayEffect 的删除操作添加了日志，以帮助追踪罕见的崩溃。该日志可以关闭。 |

### 维护评价

**积极维护，但需谨慎使用**。从 Git 历史看，Epic Games 持续对该框架进行底层修复和优化（特别是 2026 年），表明其仍被作为引擎的核心组件进行维护。然而，它存在以下显著特点：

1.  **学习曲线陡峭**：GAS 是一个复杂的系统，需要投入大量时间学习其概念（AbilitySystemComponent, GameplayEffect, GameplayTag, Attribute等）。
2.  **文档相对匮乏**：官方文档不够详尽，主要依赖社区知识（如《Gameplay Ability System - Technical Guide》）和源码阅读。
3.  **过度设计的风险**：对于简单的小游戏，引入 GAS 可能会带来不必要的复杂性。
4.  **历史包袱**：创建于2016年，部分API和模式可能略显陈旧，但核心架构依然稳固。

**推荐**：如果你的项目规模中等到大型，并且技能和效果逻辑复杂，GAS 是一个强大且经过验证的选择。否则，应仔细评估其带来的复杂度是否值得。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/GameplayAbilities)