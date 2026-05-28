# Gameplay Abilities

> Adds GameplayEffect and GameplayAbility classes to handle complicated gameplay interactions.

| 属性 | 值 |
|---|---|
| 中文名 | 游戏玩法技能 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayAbilities` (Runtime), `GameplayAbilitiesEditor` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-11-15 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities) | |

## 用途

GameplayAbilities (GAS) 是 Unreal Engine 的核心游戏框架插件，用于构建复杂的游戏逻辑系统。它不仅仅是用于实现“技能”，更是一个完整、数据驱动的游戏性框架，解决了以下核心问题：

1.  **属性管理**：通过 `FGameplayAttribute` 和 `UGameplayEffect` 安全、可预测地管理角色的生命值、法力、攻击力等数值属性。支持复杂的计算公式、曲线缩放和修改器聚合。
2.  **状态与效果**：`UGameplayEffect` 可以创建、修改和移除属性修改器、应用持续或瞬时效果（如 Buff/Debuff）、管理技能冷却和消耗。
3.  **技能逻辑**：`UGameplayAbility` 提供了技能生命周期管理（激活、结束、取消）、条件检查（消耗、冷却、标签阻塞）、预测和复制等标准化流程。
4.  **通信与反馈**：通过 `GameplayTags` 进行松耦合的系统间通信（例如，标记“眩晕”状态以禁用技能）。`GameplayCues` 系统负责与表现层（特效、音效）解耦，确保逻辑与表现分离。
5.  **网络同步**：内置了针对 Gameplay 逻辑的预测和权威服务器校验机制，简化了多人游戏中的同步问题。

**简单来说**：如果你想避免重复造轮子，并为你的 RPG、MOBA、射击或其他需要精细角色状态管理的游戏构建一个健壮、可扩展、易于测试的后端系统，GAS 是官方提供的、行业验证的解决方案。

## 使用场景

- **RPG/MOBA 游戏**：实现数百个具有冷却、消耗、等级、伤害公式、施法条件的技能。
- **任何需要 Buff/Debuff 系统的游戏**：实现复杂的增益、减益、持续伤害、状态效果叠加与覆盖规则。
- **需要精确属性控制的游戏**：管理角色/装备属性，并支持复杂的百分比加成、最终值修改等。
- **多人竞技游戏**：利用其内置的预测和复制功能，公平地处理技能命中判定和状态同步。
- **数据驱动设计**：策划可以通过编辑 `GameplayEffect` 蓝图资产来调整数值和行为，无需修改代码。

## 蓝图用法

GAS 的核心工作流在蓝图中高度可视化。主要涉及 `AbilitySystemComponent` (ASC) 和各种资产蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Try Activate Ability` | 尝试激活一个 `GameplayAbility` | `UAbilitySystemComponent` |
| `Apply Gameplay Effect to Self` | 对自身应用一个 `GameplayEffect` | `UAbilitySystemComponent` |
| `Get Active Gameplay Effect` | 获取当前激活的 `GameplayEffect` 实例信息 | `UAbilitySystemComponent` |
| `Add Loose Gameplay Tag` | 动态添加/移除一个 `GameplayTag` (非通过效果) | `UAbilitySystemComponent` |
| `Has Matching Gameplay Tag` | 检查是否拥有指定的 `GameplayTag` | `UAbilitySystemComponent` |
| `Commit Ability` | 在 `GameplayAbility` 蓝图中，提交消耗和冷却 | `UGameplayAbility` |
| `End Ability` | 在 `GameplayAbility` 蓝图中，结束当前技能 | `UGameplayAbility` |
| `Wait Gameplay Event` | 异步等待一个 `GameplayTag` 事件 | `UAbilityTask` |
| `Play Montage And Wait` | 异步播放动画蒙太奇并等待结束或中断 | `UAbilityTask` |

### 使用示例（蓝图描述）

**1. 设置角色能力：**
- 在你的角色蓝图中，添加 `AbilitySystemComponent`。
- 在角色的 `Event BeginPlay` 或自定义事件中，使用 `Give Ability` 节点为角色授予技能。

**2. 创建一个“火球术”技能：**
- 创建一个继承自 `GameplayAbility` 的蓝图 `GA_Fireball`。
- 在 `ActivateAbility` 事件中：
  - 调用 `Check Cost` 和 `Check Cooldown` 节点。
  - 调用 `Commit Ability` 节点，正式消耗资源和开始冷却。
  - 使用 `Spawn Actor` 节点生成火球投射物。
  - 使用 `Play Montage And Wait` 节点播放施法动画。
  - 动画结束后，调用 `End Ability`。

**3. 处理伤害效果：**
- 创建一个 `GameplayEffect` 蓝图 `GE_FireballDamage`，将其配置为瞬时（Instant）效果，并添加一个修改 `Attribute` “生命值”的修改器（操作为“Add”，数值通过 `Scalable Float` 可关联曲线表）。
- 在火球碰撞后，调用 `Apply Gameplay Effect Spec to Target` 节点，将 `GE_FireballDamage` 应用到目标。

**4. 添加视觉反馈：**
- 创建一个 `GameplayCue Notify` 蓝图或在角色蓝图中添加一个以 `GameplayCue.Damage.Fire` 命名的自定义事件。
- 在 `GameplayEffect` 中配置 `Gameplay Cues` 标签。当效果应用时，对应的 Cue 会被触发，你可以在此播放火焰特效。

## C++ 用法

在 C++ 中，GAS 提供了更底层和高效的控制方式。

### 头文件引入

```cpp
// Runtime 模块 (用于游戏逻辑)
#include "AbilitySystemComponent.h"
#include "Abilities/GameplayAbility.h"
#include "GameplayEffect.h"
#include "GameplayTagContainer.h"
#include "AttributeSet.h"

// 编辑器模块 (仅在编辑器工具中使用)
#include "GameplayAbilitiesEditorModule.h"
```

### 基本用法

以下代码示例基于典型的游戏角色类。

```cpp
// MyCharacter.h
#pragma once

#include "CoreMinimal.h"
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

    // 实现 IAbilitySystemInterface 接口，返回角色的 ASC
    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    UAbilitySystemComponent* AbilitySystemComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    UMyAttributeSet* AttributeSet;

    // 授予初始技能
    virtual void GiveDefaultAbilities();

    UPROPERTY(EditDefaultsOnly, Category = "Abilities")
    TArray<TSubclassOf<UGameplayAbility>> DefaultAbilities;
};

// MyCharacter.cpp
#include "MyCharacter.h"
#include "MyAttributeSet.h"
#include "AbilitySystemComponent.h"

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

void AMyCharacter::GiveDefaultAbilities()
{
    if (!HasAuthority() || !AbilitySystemComponent)
    {
        return;
    }

    for (const TSubclassOf<UGameplayAbility>& Ability : DefaultAbilities)
    {
        AbilitySystemComponent->GiveAbility(
            FGameplayAbilitySpec(Ability, 1, INDEX_NONE, this)
        );
    }
}

void AMyCharacter::BeginPlay()
{
    Super::BeginPlay();
    GiveDefaultAbilities();
}
```

### 进阶用法

**1. 自定义属性集 (AttributeSet)：**
```cpp
// MyAttributeSet.h
#pragma once

#include "AttributeSet.h"
#include "AbilitySystemComponent.h"
#include "MyAttributeSet.generated.h"

// 宏，用于快速生成属性访问器和初始化函数
#define ATTRIBUTE_ACCESSORS(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_PROPERTY_GETTER(ClassName, PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_GETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_SETTER(PropertyName) \
    GAMEPLAYATTRIBUTE_VALUE_INITTER(PropertyName)

UCLASS()
class UMyAttributeSet : public UAttributeSet
{
    GENERATED_BODY()

public:
    UMyAttributeSet();

    // 属性声明
    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_Health, Category = "VitalAttributes")
    FGameplayAttributeData Health;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, Health)

    UPROPERTY(BlueprintReadOnly, ReplicatedUsing = OnRep_MaxHealth, Category = "VitalAttributes")
    FGameplayAttributeData MaxHealth;
    ATTRIBUTE_ACCESSORS(UMyAttributeSet, MaxHealth)

    // 网络复制回调
    UFUNCTION()
    void OnRep_Health(const FGameplayAttributeData& OldHealth);
    UFUNCTION()
    void OnRep_MaxHealth(const FGameplayAttributeData& OldMaxHealth);

    // 在属性值被修改前进行钳制等操作
    virtual void PreAttributeChange(const FGameplayAttribute& Attribute, float& NewValue) override;
    virtual void PostGameplayEffectExecute(const FGameplayEffectModCallbackData& Data) override;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```

**2. 监听属性变化：**
```cpp
// 在角色 BeginPlay 或授权后
FDelegateHandle HealthChangedDelegateHandle = AbilitySystemComponent
    ->GetGameplayAttributeValueChangeDelegate(AttributeSet->GetHealthAttribute())
    .AddUObject(this, &AMyCharacter::OnHealthChanged);

void AMyCharacter::OnHealthChanged(const FOnAttributeChangeData& Data)
{
    float NewHealth = Data.NewValue;
    // 更新 UI 或处理死亡逻辑
    if (NewHealth <= 0.0f)
    {
        HandleDeath();
    }
}
```

**3. 激活技能并传入参数：**
```cpp
// 构造技能规格，并传入可选的目标数据
FGameplayAbilitySpec Spec(AbilityClass, Level, INDEX_NONE, SourceObject);
FGameplayAbilityTargetDataHandle TargetData;
// ... 填充 TargetData
Spec.TargetData = TargetData;

FGameplayAbilitySpecHandle SpecHandle = AbilitySystemComponent->GiveAbility(Spec);
bool bActivated = AbilitySystemComponent->TryActivateAbility(SpecHandle);
```

## Demo 示例

以下是一个最小的“可治疗角色”示例。

**MyHealableCharacter.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "AbilitySystemInterface.h"
#include "MyHealableCharacter.generated.h"

class UAbilitySystemComponent;
class UAttributeSet;

UCLASS()
class AMyHealableCharacter : public ACharacter, public IAbilitySystemInterface
{
    GENERATED_BODY()

public:
    AMyHealableCharacter();

    virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;

    UFUNCTION(BlueprintCallable, Category = "Healing")
    void ApplyHealEffect(TSubclassOf<UGameplayEffect> HealEffectClass, float HealMagnitude, AActor* Instigator);

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    UAbilitySystemComponent* AbilitySystemComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Abilities")
    UAttributeSet* AttributeSet;
};
```

**MyHealableCharacter.cpp**
```cpp
#include "MyHealableCharacter.h"
#include "AbilitySystemComponent.h"
#include "GameplayEffect.h"
#include "GameplayEffectTypes.h"

AMyHealableCharacter::AMyHealableCharacter()
{
    AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("ASC"));
    AbilitySystemComponent->SetIsReplicated(true);
    AttributeSet = CreateDefaultSubobject<UAttributeSet>(TEXT("AttributeSet"));
}

UAbilitySystemComponent* AMyHealableCharacter::GetAbilitySystemComponent() const
{
    return AbilitySystemComponent;
}

void AMyHealableCharacter::ApplyHealEffect(TSubclassOf<UGameplayEffect> HealEffectClass, float HealMagnitude, AActor* Instigator)
{
    if (!HasAuthority() || !HealEffectClass)
    {
        return;
    }

    // 创建效果上下文，包含来源信息
    FGameplayEffectContextHandle EffectContext = AbilitySystemComponent->MakeEffectContext();
    EffectContext.AddSourceObject(Instigator);

    // 创建效果规格
    FGameplayEffectSpecHandle SpecHandle = AbilitySystemComponent->MakeOutgoingSpec(HealEffectClass, 1.0f, EffectContext);
    
    // 设置数值参数 (通常通过 SetByCaller)
    if (SpecHandle.Data.IsValid())
    {
        // 假设效果有一个名为 "HealingMagnitude" 的 SetByCaller 标量参数
        const FGameplayTag HealingTag = FGameplayTag::RequestGameplayTag(FName("Data.Healing"));
        SpecHandle.Data->SetSetByCallerMagnitude(HealingTag, HealMagnitude);

        // 应用效果到自身
        AbilitySystemComponent->ApplyGameplayEffectSpecToSelf(*SpecHandle.Data.Get());
    }
}
```

## 模块依赖

在你的游戏模块的 `.Build.cs` 文件中，需要添加以下依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "GameplayAbilities", // 核心 GAS 模块
    "GameplayTags",     // 用于 GameplayTag 的定义和操作
    "GameplayTasks"     // 用于 AbilityTask (异步技能任务)
});

// 如果你需要使用 Niagara 系统作为 GameplayCue，则添加
// PrivateDependencyModuleNames.Add("Niagara");
```

**特殊依赖说明**：
| 模块 | 用途 |
|---|---|
| `GameplayTags` | 提供 `FGameplayTag`、`FGameplayTagContainer` 等，是 GAS 系统通信的基础。**必须依赖**。 |
| `GameplayTasks` | 提供 `UAbilityTask` 基类，用于创建技能中的异步任务（如等待动画、延迟、输入事件）。**必须依赖**。 |
| `Niagara` | 如果你在 GameplayCue 中使用 Niagara 粒子系统。这是可选的插件依赖。 |
| `DataRegistry` | 用于将 `Scalable Float` 等数据源链接到数据注册表，支持运行时查找和热重载。这是可选的插件依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下，双精度常量截断为单精度浮点数时产生的编译器警告。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中使用可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符与参数位宽不匹配的问题（32位说明符用于64位参数或反之）。 |
| 2026-04-24 | `6962ad56` | Fix incorrect reset of GameplayEffectList Next Ptr. | 修复 GameplayEffect 列表中 Next 指针被错误重置的问题。 |
| 2026-04-16 | `47285bc0` | Added logging on deletion of gameplay effect to help track down rare crash. Logging can be disabled | 添加了在删除 GameplayEffect 时的日志记录，以帮助追踪罕见的崩溃。该日志可被禁用。 |

### 维护评价

**综合评价：活跃维护中的核心系统插件。**

- **年龄与历史**：该插件自 2016 年随引擎引入，已有约 9 年历史。它源于 Epic 内部项目（如 Fortnite、Gears of War）的需求，并逐渐发展成为官方的、功能完备的游戏玩法框架。
- **维护状态**：**非常活跃**。尽管在早期文档中被标注为“实验性”和“官方不支持”，但这更多是法律和策略上的免责声明。从 Git 历史看，Epic 的工程师持续在维护此插件，最近的更新（2026年5月）主要集中在**代码质量、编译警告修复和稳定性改进**上，表明它是一个稳定的、处于维护阶段的生产级系统。
- **已知问题与限制**：
    1.  **学习曲线陡峭**：GAS 概念众多，初次使用需要投入时间理解其架构。
    2.  **蓝图图表复杂**：对于非常复杂的技能，蓝图可能变得难以阅读和维护，此时更推荐使用 C++ 实现核心逻辑。
    3.  **调试难度**：由于其预测、异步和复制机制，调试网络同步问题可能比较复杂。
- **推荐使用**：**强烈推荐**用于任何中大型或具有复杂游戏逻辑的项目。虽然学习成本不低，但它提供的架构、可扩展性和内置功能远超从头实现。对于小型项目或原型，其复杂性可能过高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities)
- [官方文档]() (.uplugin 中 DocsURL 为空)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayAbilities/Tests) (位于插件的 Tests 目录下)