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
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

GameplayAbilities (GAS) 是 Unreal Engine 的核心能力系统框架，用于构建和管理游戏中复杂的角色能力、状态效果和属性交互。它解决的核心问题是：如何结构化地处理技能激活、冷却、消耗、效果应用、属性修改、网络同步以及与游戏逻辑（如动画、特效）的集成。

GAS 提供了一套完整的、可扩展的架构，包括：
- **GameplayAbility**：定义能力的逻辑、激活条件、消耗和冷却。
- **GameplayEffect**：定义对属性（如生命值、攻击力）的修改、增益/减益效果、持续时间和叠加规则。
- **AttributeSet**：定义和管理角色的数值属性。
- **AbilitySystemComponent (ASC)**：作为核心组件，管理一个 Actor 的所有能力、效果和属性。
- **GameplayTasks**：提供异步任务（如等待输入、延迟、动画播放），用于构建能力逻辑。
- **GameplayCue**：处理与能力相关的视觉和音频反馈（如粒子、声音）。

该插件默认禁用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。

## 使用场景

- **角色扮演游戏 (RPG)**：管理复杂的技能树、法术系统、装备属性加成、Buff/Debuff。
- **多人在线竞技游戏 (MOBA)**：实现英雄技能、冷却时间、法力消耗、技能效果同步。
- **动作游戏**：处理连招、技能取消、状态切换（如霸体、浮空）。
- **任何需要结构化能力管理的游戏**：当你的游戏有超过 3-5 个主动技能，且需要处理效果叠加、属性计算、网络预测时，GAS 是官方推荐的解决方案。

## 蓝图用法

GAS 提供了丰富的蓝图节点，主要通过 `AbilityTask` 类和 `AbilitySystemComponent` 的函数暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WaitDelay` | 在能力中等待指定时间，功能等同于标准 Delay 节点。 | `UAbilityTask_WaitDelay` |
| `WaitInputPress` | 等待玩家按下激活此能力的输入键。 | `UAbilityTask_WaitInputPress` |
| `WaitInputRelease` | 等待玩家释放激活此能力的输入键。 | `UAbilityTask_WaitInputRelease` |
| `WaitConfirmCancel` | 等待玩家确认或取消（通常用于瞄准类技能）。 | `UAbilityTask_WaitConfirmCancel` |
| `WaitGameplayTagCountChange` | 等待指定 GameplayTag 的计数发生变化。 | `UAbilityTask_WaitGameplayTagCountChanged` |
| `WaitMovementModeChange` | 等待角色移动模式改变（如落地）。 | `UAbilityTask_WaitMovementModeChange` |
| `WaitVelocityChange` | 等待角色速度在指定方向上达到最小值。 | `UAbilityTask_WaitVelocityChange` |
| `RepeatAction` | 以固定间隔重复执行一个动作指定次数。 | `UAbilityTask_Repeat` |
| `WaitGameplayTagCountChangedOnActor` | (Async) 等待目标 Actor 上指定 GameplayTag 计数变化。 | `UAbilityAsync_WaitGameplayTagCountChanged` |

### 使用示例（蓝图描述）

1.  **创建一个简单的延迟能力**：
    - 创建一个继承自 `GameplayAbility` 的蓝图。
    - 在 `ActivateAbility` 事件中，调用 `WaitDelay` 节点，设置时间为 2.0 秒。
    - 将 `OnFinish` 委托连接到 `EndAbility` 节点。
    - 结果：能力激活后等待 2 秒，然后自动结束。

2.  **创建一个需要按住输入的蓄力技能**：
    - 在 `ActivateAbility` 中，调用 `WaitInputRelease` 节点。
    - 将 `OnRelease` 委托连接到后续逻辑（如根据按住时间计算伤害）。
    - 在 `InputReleased` 事件中（当玩家提前松开时），可以调用 `CancelAbility`。

3.  **监听属性变化**：
    - 在角色蓝图中，获取 `AbilitySystemComponent`。
    - 使用 `GetGameplayAttributeValueChangeDelegate` 节点，传入要监听的属性（如 `Health`）。
    - 将返回的委托连接到自定义事件，即可在属性变化时执行逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "AbilitySystemComponent.h"
#include "Abilities/GameplayAbility.h"
#include "GameplayEffect.h"
#include "AttributeSet.h"
```

### 基本用法

**1. 定义一个属性集 (AttributeSet)**
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
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health, Category = "Vital Attributes")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_MaxHealth, Category = "Vital Attributes")
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

protected:
    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldHealth);
    UFUNCTION()
    void OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth);
};
```

**2. 在 Actor 中集成 AbilitySystemComponent**
```cpp
// MyCharacter.h
#pragma once
#include "GameFramework/Character.h"
#include "AbilitySystemInterface.h"
#include "MyCharacter.generated.h"

class UAbilitySystemComponent;
class UMyAttributeSet;

UCLASS()
class AMyCharacter : public ACharacter, public IAbilitySystemInterface
{
    GENERATED_BODY()

public:
    AMyCharacter();

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;

    UPROPERTY()
    TObjectPtr<UMyAttributeSet> AttributeSet;

    virtual void BeginPlay() override;
};
```
```cpp
// MyCharacter.cpp
#include "MyCharacter.h"
#include "AbilitySystemComponent.h"
#include "MyAttributeSet.h"

AMyCharacter::AMyCharacter()
{
    AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbilitySystemComp"));
    AbilitySystemComponent->SetIsReplicated(true);
    AbilitySystemComponent->SetReplicationMode(EGameplayEffectReplicationMode::Mixed);

    AttributeSet = CreateDefaultSubobject<UMyAttributeSet>(TEXT("AttributeSet"));
}

UAbilitySystemComponent* AMyCharacter::GetAbilitySystemComponent() const
{
    return AbilitySystemComponent;
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    if (AbilitySystemComponent)
    {
        // 初始化属性，例如从 DataTable 或默认值
        AbilitySystemComponent->InitAbilityActorInfo(this, this);
    }
}
```

### 进阶用法

**创建一个自定义的 GameplayEffect 计算类**
```cpp
// MyDamageCalculation.h
#pragma once
#include "GameplayEffectCalculation.h"
#include "MyDamageCalculation.generated.h"

UCLASS()
class UMyDamageCalculation : public UGameplayEffectCalculation
{
    GENERATED_BODY()

public:
    UMyDamageCalculation();

    virtual void Execute_Implementation(const FGameplayEffectCustomExecutionParameters& ExecutionParams, FGameplayEffectCustomExecutionOutput& OutExecutionOutput) const override;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly)
    FGameplayEffectAttributeCaptureDefinition BaseDamageDef;
};
```
```cpp
// MyDamageCalculation.cpp
#include "MyDamageCalculation.h"
#include "AbilitySystemComponent.h"

UMyDamageCalculation::UMyDamageCalculation()
{
    // 定义要捕获的属性（例如，来自源Actor的攻击力）
    BaseDamageDef.AttributeToCapture = UMyAttributeSet::GetAttackPowerAttribute();
    BaseDamageDef.AttributeSource = EGameplayEffectAttributeCaptureSource::Source;
    BaseDamageDef.bSnapshot = false;

    RelevantAttributesToCapture.Add(BaseDamageDef);
}

void UMyDamageCalculation::Execute_Implementation(const FGameplayEffectCustomExecutionParameters& ExecutionParams, FGameplayEffectCustomExecutionOutput& OutExecutionOutput) const
{
    UAbilitySystemComponent* SourceASC = ExecutionParams.GetSourceAbilitySystemComponent();
    UAbilitySystemComponent* TargetASC = ExecutionParams.GetTargetAbilitySystemComponent();

    const FGameplayEffectSpec& Spec = ExecutionParams.GetOwningSpec();

    // 捕获并计算属性值
    FAggregatorEvaluateParameters EvaluationParameters;
    float BaseDamage = 0.0f;
    ExecutionParams.AttemptCalculateCapturedAttributeMagnitude(BaseDamageDef, EvaluationParameters, BaseDamage);

    // 应用自定义公式，例如考虑目标护甲
    float FinalDamage = BaseDamage * 0.8f; // 简化示例

    // 输出修改器
    if (FinalDamage > 0.0f)
    {
        OutExecutionOutput.AddOutputModifier(FGameplayModifierEvaluatedData(
            UMyAttributeSet::GetHealthAttribute(),
            EGameplayModOp::Additive,
            -FinalDamage)); // 对生命值造成伤害
    }
}
```

## Demo 示例

**一个最小的自定义能力示例：治疗能力**

```cpp
// GameplayAbility_Heal.h
#pragma once
#include "Abilities/GameplayAbility.h"
#include "GameplayAbility_Heal.generated.h"

UCLASS()
class UGameplayAbility_Heal : public UGameplayAbility
{
    GENERATED_BODY()

public:
    UGameplayAbility_Heal();

    virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;

protected:
    UPROPERTY(EditDefaultsOnly, Category = "Healing")
    TSubclassOf<UGameplayEffect> HealEffectClass;

    UPROPERTY(EditDefaultsOnly, Category = "Healing")
    float HealAmount = 50.0f;
};
```

```cpp
// GameplayAbility_Heal.cpp
#include "GameplayAbility_Heal.h"
#include "AbilitySystemComponent.h"
#include "GameplayEffect.h"

UGameplayAbility_Heal::UGameplayAbility_Heal()
{
    InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
    NetExecutionPolicy = EGameplayAbilityNetExecutionPolicy::LocalPredicted;
}

void UGameplayAbility_Heal::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    if (!CommitAbility(Handle, ActorInfo, ActivationInfo))
    {
        EndAbility(Handle, ActorInfo, ActivationInfo, true, true);
        return;
    }

    UAbilitySystemComponent* SourceASC = ActorInfo->AbilitySystemComponent.Get();
    if (SourceASC && HealEffectClass)
    {
        FGameplayEffectContextHandle EffectContext = SourceASC->MakeEffectContext();
        EffectContext.AddSourceObject(this);

        FGameplayEffectSpecHandle SpecHandle = SourceASC->MakeOutgoingSpec(HealEffectClass, GetAbilityLevel(), EffectContext);
        if (SpecHandle.IsValid())
        {
            // 设置治疗量为一个可修改的 SetByCaller 数值
            SpecHandle.Data->SetSetByCallerMagnitude(FGameplayTag::RequestGameplayTag(FName("Data.HealAmount")), HealAmount);
            SourceASC->ApplyGameplayEffectSpecToSelf(*SpecHandle.Data.Get());
        }
    }

    EndAbility(Handle, ActorInfo, ActivationInfo, true, false);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Niagara` | 用于 GameplayCue 系统集成粒子特效。 |
| `EditorFramework` | 编辑器框架支持。 |
| `UnrealEd` | 编辑器工具和资产类型支持。 |
| `Slate` | 用于编辑器 UI 扩展。 |
| `SequenceRecorder` | 用于录制能力相关的动画序列。 |
| `GameplayTasks` | 提供 AbilityTask 的基础框架。 |

## 维护状态

### 近期更新

```
- 2c26eb2d7521 - gas: change debug info
- 2cf8694a14a9 Unshelved from pending changelist '47949096':
- 39d8bbbc219e [GAS] Using Generic Replication, the GameplayTagCountContainer can get stuck in a state where it constantly replicates a None tag if any of the tags were set to non-replicated.
```

### 维护评价

GameplayAbilities 是 Unreal Engine 的核心系统之一，自 2016 年引入以来一直是官方重点维护的模块。尽管创建时间较早（约 8 年），但它持续获得功能更新和 Bug 修复，以适应新的引擎版本（如 UE5 的 Iris 网络序列化系统）。

- **活跃维护**：作为 Epic 官方插件，其维护状态与引擎版本同步。最近的提交涉及调试信息改进和网络复制 Bug 修复，表明仍在积极维护。
- **稳定性**：经过多年迭代，系统已非常成熟稳定，是众多商业项目的基石。
- **学习曲线**：系统庞大且概念较多，新手需要投入时间学习。
- **推荐使用**：**强烈推荐**。对于任何需要复杂能力、效果和属性系统的游戏项目，GAS 是官方且功能完备的解决方案。虽然默认禁用，但启用后能极大提升开发效率和系统健壮性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayAbilities)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/gameplay-ability-system-for-unreal-engine/) (UE5 官方文档链接)