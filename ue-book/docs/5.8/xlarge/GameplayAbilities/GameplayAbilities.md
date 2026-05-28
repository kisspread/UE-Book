# Gameplay Abilities

> Adds GameplayEffect and GameplayAbility classes to handle complicated gameplay interactions.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏技能系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayAbilities` (Runtime), `GameplayAbilitiesEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

GameplayAbilities（简称 GAS — Gameplay Ability System）是 Unreal Engine 内置的一套完整的技能效果框架，用于构建 RPG、MOBA、FPS 等游戏中复杂的技能、Buff/Debuff 和属性系统。

它解决的核心问题包括：

- **技能生命周期管理**：从激活、承诺资源消耗、执行到结束的完整流程，支持网络预测和复制
- **属性系统**：定义可被效果修改的数值属性（如生命值、攻击力），支持叠加、钳制和多通道修改器
- **游戏效果（GameplayEffect）**：数据驱动的 Buff/Debuff 系统，支持即时、持续、无限和周期性效果，以及堆叠规则
- **标签系统集成**：通过 GameplayTag 驱动技能的激活条件、阻止条件、冷却和消耗检查
- **GameplayCue**：可复制的视觉/音频反馈系统，支持瞬发和持续效果
- **网络预测**：完整的客户端预测 + 服务端确认机制，确保多人游戏中的流畅体验

GAS 默认不启用（`EnabledByDefault: false`），需要在 `.uproject` 中手动启用插件。

## 使用场景

- 你在做一个有复杂技能系统的 RPG → 用 GAS 管理技能激活、冷却、消耗和效果叠加
- 你需要一套可数据驱动的 Buff/Debuff 系统 → 用 GameplayEffect 配置不同效果类型
- 你的多人游戏需要客户端预测技能效果 → GAS 内置预测窗口和确认机制
- 你需要将属性（血量、攻击力等）与效果系统解耦 → 用 AttributeSet + GameplayEffect
- 你需要基于标签的技能条件系统（如"被沉默时无法施法"）→ 用标签要求和阻止标签
- 你需要技能的视觉/音频反馈与逻辑分离 → 用 GameplayCue 系统

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Ability System Component` | 从 Actor 获取 AbilitySystemComponent，优先检查 IAbilitySystemInterface 接口 | `UAbilitySystemBlueprintLibrary` |
| `Send Gameplay Event To Actor` | 向 Actor 发送携带载荷的 Gameplay 事件，触发对应技能 | `UAbilitySystemBlueprintLibrary` |
| `Make Outgoing Gameplay Effect Spec` | 创建一个 GameplayEffectSpec，用于后续应用效果 | `UAbilitySystemComponent` |
| `Apply Gameplay Effect Spec To Self` | 将效果应用到自身 | `UAbilitySystemComponent` |
| `Apply Gameplay Effect Spec To Target` | 将效果应用到目标 | `UAbilitySystemComponent` |
| `Try Activate Ability By Class` | 尝试通过类激活技能 | `UAbilitySystemComponent` |
| `Try Activate Ability By Tag` | 尝试通过标签激活技能 | `UAbilitySystemComponent` |
| `Make Spec Handle By Class` | 创建 GameplayEffectSpec 句柄 | `UAbilitySystemBlueprintLibrary` |
| `Assign Tag Set By Caller Magnitude` | 设置按标签索引的 SetByCaller 数值 | `UAbilitySystemBlueprintLibrary` |
| `Execute GameplayCue On Actor` | 在 Actor 上触发瞬发 GameplayCue | `UGameplayCueFunctionLibrary` |
| `Add GameplayCue On Actor` | 在 Actor 上添加持续 GameplayCue | `UGameplayCueFunctionLibrary` |
| `Remove GameplayCue On Actor` | 从 Actor 移除持续 GameplayCue | `UGameplayCueFunctionLibrary` |
| `Get Float Attribute` | 获取 Actor 的浮点属性值 | `UAbilitySystemBlueprintLibrary` |
| `Bind Event Wrapper To Gameplay Tag Changed` | 绑定标签变化事件 | `UAbilitySystemBlueprintLibrary` |
| `Make GameplayCue Parameters` | 构造 GameplayCue 参数 | `UAbilitySystemBlueprintLibrary` |

### 使用示例（蓝图描述）

**创建并应用 GameplayEffect：**

1. 获取目标 Actor 的 `AbilitySystemComponent`（调用 `GetAbilitySystemComponent`）
2. 调用 `Make OutgoingSpec`，传入 GameplayEffect 子类、等级和 EffectContext
3. 可选：调用 `AssignTagSetByCallerMagnitude` 设置自定义数值
4. 调用 `ApplyGameplayEffectSpecToTarget` 将效果应用到目标
5. 返回的 `ActiveGameplayEffectHandle` 可用于后续移除

**激活技能：**

1. 先通过 `GiveAbility` 将技能授予 ASC（通常在 BeginPlay 时）
2. 调用 `TryActivateAbilityByClass` 或 `TryActivateAbilityByTag` 激活
3. 技能内部通过 `CommitAbility` 消耗资源和应用冷却
4. 通过 `EndAbility` 正式结束技能

**监听 GameplayCue：**

1. 在 GameplayEffect 资产上设置 GameplayCue 标签
2. 创建 `GameplayCueNotify_Looping` 或 `GameplayCueNotify_Actor` 子类
3. 重写 `OnActive`（开始）、`WhileActive`（持续）、`OnRemove`（结束）事件

## C++ 用法

### 头文件引入

```cpp
#include "AbilitySystemComponent.h"
#include "AbilitySystemGlobals.h"
#include "Abilities/GameplayAbility.h"
#include "GameplayEffect.h"
#include "AttributeSet.h"
#include "GameplayEffectTypes.h"
#include "GameplayTagContainer.h"
```

### 基本用法

**定义 AttributeSet：**

```cpp
// 来源：Public/AttributeSet.h — UAttributeSet 类定义
UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health, Category = "Vital Attributes")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_MaxHealth, Category = "Vital Attributes")
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Mana, Category = "Vital Attributes")
    FGameplayAttributeData Mana;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Mana)

    // 属性修改前的回调，适合做钳制
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override
    {
        Super::PreAttributeChange(Attribute, NewValue);
        if (Attribute == GetHealthAttribute())
        {
            NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxHealth());
        }
    }

    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override
    {
        Super::PostGameplayEffectExecute(Data);
        if (Data.EvaluatedData.Attribute == GetHealthAttribute())
        {
            SetHealth(FMath::Clamp(GetHealth(), 0.0f, GetMaxHealth()));
        }
    }

protected:
    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldHealth) { GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, Health, OldHealth); }
    UFUNCTION()
    void OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth) { GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, MaxHealth, OldMaxHealth); }
    UFUNCTION()
    void OnRep_Mana(const FGameplayAttributeData& OldMana) { GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, Mana, OldMana); }
};
```

**实现 IAbilitySystemInterface：**

```cpp
// 来源：Public/AbilitySystemInterface.h
UCLASS()
class AMyCharacter : public ACharacter, public IAbilitySystemInterface
{
    GENERATED_BODY()

public:
    AMyCharacter();

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override
    {
        return AbilitySystemComponent;
    }

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;

    UPROPERTY()
    TObjectPtr<UMyAttributeSet> AttributeSet;
};
```

### 进阶用法

**自定义 GameplayAbility：**

```cpp
// 来源：Public/Abilities/GameplayAbility.h
UCLASS()
class UGameplayAbility_MyAbility : public UGameplayAbility
{
    GENERATED_BODY()

public:
    UGameplayAbility_MyAbility()
    {
        // 设置实例化策略：每个 Actor 一个实例
        InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
        // 设置网络执行策略：客户端预测
        NetExecutionPolicy = EGameplayAbilityNetExecutionPolicy::LocalPredicted;
    }

    virtual void ActivateAbility(
        const FGameplayAbilitySpecHandle Handle,
        const FGameplayAbilityActorInfo* ActorInfo,
        const FGameplayAbilityActivationInfo ActivationInfo,
        const FGameplayEventData* TriggerEventData) override
    {
        if (!CommitAbility(Handle, ActorInfo, ActivationInfo))
        {
            EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
            return;
        }

        // 执行技能逻辑...
        // 创建并应用 GameplayEffect
        FGameplayEffectSpecHandle SpecHandle = MakeOutgoingGameplayEffectSpec(DamageEffectClass, GetAbilityLevel());
        if (SpecHandle.IsValid())
        {
            ApplyGameplayEffectSpecToTarget(Handle, ActorInfo, ActivationInfo, SpecHandle, TargetAbilitySystemComponent);
        }
    }
};
```

**自定义 GameplayEffectExecutionCalculation：**

```cpp
// 来源：Public/GameplayEffectExecutionCalculation.h
UCLASS()
class UMyDamageExecution : public UGameplayEffectExecutionCalculation
{
    GENERATED_BODY()

public:
    UMyDamageExecution()
    {
        bRequiresPassedInTags = true;

        // 声明属性捕获
        DECLARE_ATTRIBUTE_CAPTUREDEF(AttackPower);
        DECLARE_ATTRIBUTE_CAPTUREDEF(Defense);

        // 定义从源 Actor 捕获攻击力
        DEFINE_ATTRIBUTE_CAPTUREDEF(UMyAttributeSet, AttackPower, Source, false);
        // 定义从目标 Actor 捕获防御力
        DEFINE_ATTRIBUTE_CAPTUREDEF(UMyAttributeSet, Defense, Target, false);
    }

    virtual void Execute_Implementation(
        const FGameplayEffectCustomExecutionParameters& ExecutionParams,
        FGameplayEffectCustomExecutionOutput& OutExecutionOutput) const override
    {
        FAggregatorEvaluateParameters EvalParams;
        EvalParams.SourceTags = ExecutionParams.GetOwningSpec().CapturedSourceTags.GetAggregatedTags();
        EvalParams.TargetTags = ExecutionParams.GetOwningSpec().CapturedTargetTags.GetAggregatedTags();

        float AttackPower = 0.f;
        ExecutionParams.AttemptCalculateCapturedAttributeMagnitude(AttackPowerDef, EvalParams, AttackPower);

        float Defense = 0.f;
        ExecutionParams.AttemptCalculateCapturedAttributeMagnitude(DefenseDef, EvalParams, Defense);

        float Damage = FMath::Max(0.f, AttackPower - Defense);

        OutExecutionOutput.AddOutputModifier(
            FGameplayModifierEvaluatedData(UMyAttributeSet::GetHealthAttribute(), EGameplayModOp::Additive, -Damage));
    }
};
```

**自定义 GameplayEffectComponent（UE 5.3+）：**

```cpp
// 来源：Public/GameplayEffectComponent.h
UCLASS()
class UMyGameplayEffectComponent : public UGameplayEffectComponent
{
    GENERATED_BODY()

public:
    virtual bool CanGameplayEffectApply(
        const FActiveGameplayEffectsContainer& ActiveGEContainer,
        const FGameplayEffectSpec& GESpec) const override
    {
        // 自定义应用前检查
        return true;
    }

    virtual void OnGameplayEffectApplied(
        FActiveGameplayEffectsContainer& ActiveGEContainer,
        FGameplayEffectSpec& GESpec,
        FPredictionKey& PredictionKey) const override
    {
        // 效果被应用时的自定义逻辑
    }
};
```

## Demo 示例

```cpp
// MyAttributeSet.h
#pragma once

#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "MyAttributeSet.generated.h"

// ATTRIBUTE_ACCESSORS 宏简化属性访问器定义
#define ATTRIBUTE_ACCESSORS(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_PROPERTY_GETTER(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_GETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_SETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_INITTER(PropertyName)

UCLASS()
class MYGAME_API UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health, Category = "Attributes")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_MaxHealth, Category = "Attributes")
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

protected:
    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldHealth);
    UFUNCTION()
    void OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth);
};
```

```cpp
// MyAttributeSet.cpp
#include "MyAttributeSet.h"
#include "GameplayEffect.h"
#include "GameplayEffectExtension.h"
#include "Net/UnrealNetwork.h"

void UMyAttributeSet::PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue)
{
    Super::PreAttributeChange(Attribute, NewValue);
    if (Attribute == GetHealthAttribute())
    {
        NewValue = FMath::Clamp(NewValue, 0.0f, GetMaxHealth());
    }
}

void UMyAttributeSet::PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data)
{
    Super::PostGameplayEffectExecute(Data);
    if (Data.EvaluatedData.Attribute == GetHealthAttribute())
    {
        SetHealth(FMath::Clamp(GetHealth(), 0.0f, GetMaxHealth()));
        if (GetHealth() <= 0.0f)
        {
            // 触发死亡逻辑
        }
    }
}

void UMyAttributeSet::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, Health, COND_None, REPNOTIFY_Always);
    DOREPLIFETIME_CONDITION_NOTIFY(UMyAttributeSet, MaxHealth, COND_None, REPNOTIFY_Always);
}

void UMyAttributeSet::OnRep_Health(const FGameplayAttributeData& OldHealth)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, Health, OldHealth);
}

void UMyAttributeSet::OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth)
{
    GAMEPLAYATTRIBUTE_REPNOTIFY(UMyAttributeSet, MaxHealth, OldMaxHealth);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTasks` | 技能任务（AbilityTask）基础框架 |
| `Niagara` | GameplayCue 的粒子效果支持 |
| `SequenceRecorder` | Sequencer 中的 GameplayCue 录制支持 |
| `DataRegistry` | FScalableFloat 的数据注册表支持 |
| `GameplayTagsEditor` | GameplayTag 的编辑器 UI |
| `EngineAssetDefinitions` | 资产定义支持 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点的警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举可能导致垃圾输出的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数位数不匹配的问题 |
| 2026-04-24 | `6962ad56` | Fix incorrect reset of GameplayEffectList Next Ptr. | 修复 GameplayEffectList 的 Next 指针重置错误 |
| 2026-04-16 | `47285bc0` | Added logging on deletion of gameplay effect to help track down rare crash. | 添加 GameplayEffect 删除时的日志以追踪罕见崩溃 |

### 维护评价

**活跃维护**。GAS 自 2016 年创建以来持续得到 Epic Games 的维护和更新，是 Unreal Engine 核心模块之一。近期更新集中在稳定性和编译修复方面。值得注意的是：

- UE 5.3 引入了 `GameplayEffectComponent` 模块化架构，将 GameplayEffect 的行为拆分为可组合的组件
- 多处 `Deprecated` 标记（如 `NonInstanced` 实例化策略、`LinkedGameplayEffects`、旧的 `AbilityTags` 变量）表明 API 持续演进
- 配置变量从 `AbilitySystemGlobals` 逐步迁移至 `GameplayAbilitiesDeveloperSettings`（Project Settings UI）
- 5.7 版本废弃了部分标签复制相关变量，推荐使用新的复制状态

**推荐使用**：GAS 是 UE 中功能最完整的技能效果框架，经过 Fortnite、Paragon 等大型项目的验证。虽然是"文物"级别的插件（约 9 年），但仍在活跃维护且持续改进。默认不启用，需要手动在项目中启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveExperiences/GameplayAbilitySystem/)（GAS 官方文档入口）