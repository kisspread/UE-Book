# AudioGameplay

> Core plugin for audio gameplay

| 属性 | 值 |
|---|---|
| 中文名 | 音频游戏玩法 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioGameplay` (Runtime), `AudioGameplayTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay) | |

## 用途

AudioGameplay 插件提供了一套面向游戏玩法的音频管理系统，核心解决以下问题：

1. **音频组件组管理（AudioComponentGroup）**：将多个 AudioComponent 作为一个逻辑组统一控制，包括播放、停止、参数同步、音量/音调修饰器。解决了游戏中同一"音源"可能有多个 AudioComponent（例如同时播放多个 Sound Cue）需要统一管理的需求。

2. **音频参数自动派发（AudioParameterComponent）**：通过 `IActorSoundParameterInterface` 接口，将音频参数自动派发给 Actor 上所有正在播放的声音，无需手动逐个设置。

3. **基于 GameplayTag 的音频条件系统**：提供 `FilteredGameplayTagContainer` 和 `IAudioGameplayCondition` 接口，用于构建依赖 GameplayTag 的音频开关（Audio Toggle），常见于音频体积（Audio Volume）系统中根据标签控制音频行为。

4. **音频资产元数据（AudioAssetUserData）**：允许在音频资产上附加 GameplayTag 元数据，便于按标签过滤和检索音频资源。

5. **SoundHandle 子系统**：提供底层的音频句柄管理，支持基于位置变换的音频播放控制。

## 使用场景

- 你有一个角色同时播放脚步声、环境音效、语音，需要统一控制音量和静音 → 用 **AudioComponentGroup**
- 你需要让 Actor 上的所有音效自动接收音频参数（如被水淹时降低所有音效的高频）→ 用 **AudioParameterComponent**
- 你需要根据 GameplayTag 条件决定是否播放某些音效 → 用 **FAudioGameplayRequirements** + **UAudioRequirementPreset**
- 你需要在音频资产上附加元数据标签（如"恐怖"、"战斗"、"环境"）并按标签查询 → 用 **UAudioAssetUserData**
- 你需要自定义音频组的修饰逻辑（如根据距离自动衰减）→ 实现 **IAudioComponentGroupExtension**

## 蓝图用法

### 核心节点 — UAudioComponentGroup

音频组件组的核心管理类，继承自 SceneComponent，可附加到 Actor 上。

#### 组管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StaticGetOrCreateComponentGroup` | 静态方法，获取或创建指定 Actor 的 AudioComponentGroup | `UAudioComponentGroup` |
| `AddExternalComponent` | 将外部创建的 AudioComponent 纳入本组共享参数 | `UAudioComponentGroup` |
| `RemoveExternalComponent` | 从组中移除外部 AudioComponent | `UAudioComponentGroup` |

#### 播放控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StopSound` | 停止组内所有实例中指定 SoundBase 的播放，支持淡出时间 | `UAudioComponentGroup` |
| `IsPlayingAny` | 查询组内是否有任何声音正在播放 | `UAudioComponentGroup` |
| `BroadcastStopAll` | 广播停止组内所有声音 | `UAudioComponentGroup` |
| `BroadcastKill` | 广播销毁组内所有声音 | `UAudioComponentGroup` |
| `BroadcastEvent` | 广播指定名称的事件到组内所有组件 | `UAudioComponentGroup` |

#### 虚拟化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EnableVirtualization` | 启用虚拟化（暂停音频计算） | `UAudioComponentGroup` |
| `DisableVirtualization` | 禁用虚拟化（恢复音频计算） | `UAudioComponentGroup` |
| `IsVirtualized` | 查询当前是否处于虚拟化状态 | `UAudioComponentGroup` |

#### 修饰器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetVolumeMultiplier` | 设置组整体音量倍率 | `UAudioComponentGroup` |
| `SetPitchMultiplier` | 设置组整体音调倍率 | `UAudioComponentGroup` |
| `SetLowPassFilter` | 设置组整体低通滤波频率 | `UAudioComponentGroup` |

#### 参数与订阅

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SubscribeToStringParam` | 订阅字符串参数变化 | `UAudioComponentGroup` |
| `SubscribeToEvent` | 订阅事件触发 | `UAudioComponentGroup` |
| `SubscribeToBool` | 订阅布尔参数变化 | `UAudioComponentGroup` |
| `UnsubscribeObject` | 移除指定对象的所有订阅 | `UAudioComponentGroup` |
| `GetFloatParamValue` | 获取浮点参数值 | `UAudioComponentGroup` |
| `GetBoolParamValue` | 获取布尔参数值 | `UAudioComponentGroup` |
| `GetStringParamValue` | 获取字符串参数值 | `UAudioComponentGroup` |

#### 扩展

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddExtension` | 添加 IAudioComponentGroupExtension 扩展 | `UAudioComponentGroup` |
| `RemoveExtension` | 移除扩展 | `UAudioComponentGroup` |

#### 事件（BlueprintAssignable）

| 事件 | 说明 |
|---|---|
| `OnStopped` | 停止播放时触发 |
| `OnKilled` | 强制销毁时触发 |
| `OnVirtualized` | 进入虚拟化状态时触发 |
| `OnUnvirtualized` | 退出虚拟化状态时触发 |

### 核心节点 — UAudioParameterComponent

音频参数组件，存储参数并通过 ActorSoundParameterInterface 自动派发给 Actor 上的所有音效。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetParameters` | 获取当前存储的所有音频参数 | `UAudioParameterComponent` |
| `SetFloatParameter` | 设置浮点参数 | `UAudioParameterComponent` |
| `SetBoolParameter` | 设置布尔参数 | `UAudioParameterComponent` |
| `SetStringParameter` | 设置字符串参数 | `UAudioParameterComponent` |
| `SetIntParameter` | 设置整数参数 | `UAudioParameterComponent` |
| `SetTriggerParameter` | 设置触发器参数 | `UAudioParameterComponent` |
| `ResetParameters` | 重置所有参数 | `UAudioParameterComponent` |
| `SetParameters_Blueprint` | 批量设置参数（蓝图用） | `UAudioParameterComponent` |

### 核心节点 — UAudioAssetUserData

音频资产用户数据，用于给音频资产附加 GameplayTag 元数据。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllTags` | 获取音频资产及其 SoundClass 的所有元数据标签 | `UAudioAssetUserData` |
| `HasTag` | 检查音频资产是否包含指定标签 | `UAudioAssetUserData` |
| `GetFilteredTags` | 获取音频资产中匹配指定标签的元数据 | `UAudioAssetUserData` |

### 核心节点 — UAudioRequirementPreset / FAudioGameplayRequirements

基于 GameplayTag 的音频需求匹配系统。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FAudioGameplayRequirements::Matches` | 检查提供的标签是否匹配预设和自定义查询 | `FAudioGameplayRequirements` |
| `UAudioRequirementPreset` | 可复用的 GameplayTagQuery 数据资产 | `UAudioRequirementPreset` |

### 使用示例（蓝图描述）

**示例 1：统一管理角色音效**

1. 在角色蓝图中，使用 `StaticGetOrCreateComponentGroup` 获取或创建 AudioComponentGroup（通常放在 BeginPlay 中）
2. 将角色的各个 AudioComponent 通过 `AddExternalComponent` 加入组中
3. 需要静音时，调用 `SetVolumeMultiplier(0.0)` 或 `BroadcastStopAll`
4. 监听 `OnStopped` / `OnKilled` 事件做清理

**示例 2：音频参数自动派发**

1. 在 Actor 上添加 `AudioParameterComponent`
2. 在 Component 的 Details 面板中添加 `Parameters` 数组（如 Float 参数 "Underwater"）
3. 游戏逻辑中调用 `SetFloatParameter("Underwater", 0.8)` 设置值
4. 该 Actor 上所有新播放的 AudioComponent 会自动接收这个参数，无需手动传递

**示例 3：基于标签的音频资产查询**

1. 在音频资产（如 SoundWave）的 AssetUserData 中添加 `UAudioAssetUserData`
2. 设置 MetadataTags，如 "Gameplay.Audio.Combat"
3. 代码中调用 `UAudioAssetUserData::HasTag(MySound, CombatTag)` 判断是否为战斗音效

## C++ 用法

### 头文件引入

```cpp
#include "AudioComponentGroup.h"
#include "AudioParameterComponent.h"
#include "AudioAssetUserData.h"
#include "AudioGameplayRequirements.h"
#include "FilteredGameplayTagContainer.h"
```

### 基本用法 — AudioComponentGroup

`AudioComponentGroup` 作为 Actor 的 SceneComponent 管理多个 AudioComponent 的生命周期和参数同步。

```cpp
// 头文件
// AudioComponentGroup.h

// 获取或创建 Actor 的 AudioComponentGroup
UAudioComponentGroup* Group = UAudioComponentGroup::StaticGetOrCreateComponentGroup(MyActor);

// 停止指定声音
Group->StopSound(MySoundBase, 0.5f); // 0.5 秒淡出

// 设置组修饰器
Group->SetVolumeMultiplier(0.5f);
Group->SetPitchMultiplier(1.2f);
Group->SetLowPassFilter(5000.0f);

// 检查播放状态
if (Group->IsPlayingAny())
{
    // 有声音在播放
}

if (Group->IsVirtualized())
{
    // 已被虚拟化（暂停计算）
}
```

### 基本用法 — AudioParameterComponent

通过 `IAudioParameterControllerInterface` 统一设置音频参数，自动派发到 Actor 上的音效。

```cpp
// 获取组件（假设已附加到 Actor）
UAudioParameterComponent* ParamComp = MyActor->FindComponentByClass<UAudioParameterComponent>();

// 设置参数
ParamComp->SetFloatParameter(FName("WetLevel"), 0.75f);
ParamComp->SetBoolParameter(FName("IsUnderwater"), true);
ParamComp->SetStringParameter(FName("Environment"), TEXT("Cave"));

// 批量设置
TArray<FAudioParameter> Params;
Params.Add(FAudioParameter(FName("Volume"), 0.5f));
Params.Add(FAudioParameter(FName("Filter"), 2000.0f));
ParamComp->SetParameters_Blueprint(Params);
```

### 基本用法 — AudioAssetUserData 标签查询

```cpp
// 获取音频资产上的所有标签
FGameplayTagContainer AllTags = UAudioAssetUserData::GetAllTags(MySoundBase);

// 检查是否包含特定标签
FGameplayTag CombatTag = FGameplayTag::RequestGameplayTag(FName("Gameplay.Audio.Combat"));
if (UAudioAssetUserData::HasTag(MySoundBase, CombatTag, false))
{
    // 这是一个战斗音效
}

// 获取匹配指定标签的子集
FGameplayTagContainer FilteredTags = UAudioAssetUserData::GetFilteredTags(MySoundBase, CombatTag);
```

### 进阶用法 — 自定义 AudioComponentGroupExtension

通过实现 `IAudioComponentGroupExtension` 接口，可以自定义音频组的更新逻辑。

```cpp
// 头文件：MyAudioGroupExtension.h
#pragma once

#include "AudioComponentGroupExtension.h"
#include "MyAudioGroupExtension.generated.h"

UCLASS(BlueprintType, Blueprintable)
class UMyAudioGroupExtension : public UObject, public IAudioComponentGroupExtension
{
    GENERATED_BODY()

public:
    // 每帧更新，通过 OutModifier 修改音频参数
    virtual void Update(const float DeltaTime, UAudioComponentGroup* Group, FAudioComponentModifier& OutModifier) override
    {
        // 根据距离衰减设置音量
        float DistanceFactor = CalculateDistanceFactor(Group);
        OutModifier.Volume *= DistanceFactor;
    }

    virtual void OnAddedToGroup(UAudioComponentGroup* NewGroup) override
    {
        // 被添加到组时的初始化逻辑
    }

private:
    float CalculateDistanceFactor(UAudioComponentGroup* Group)
    {
        // 自定义距离衰减逻辑
        return 1.0f;
    }
};
```

```cpp
// 使用：将扩展添加到 AudioComponentGroup
UMyAudioGroupExtension* Ext = NewObject<UMyAudioGroupExtension>(Group);
Group->AddExtension(Ext);
```

### 进阶用法 — FilteredGameplayTagContainer

带条件过滤的 GameplayTag 容器，标签只有在满足附带查询时才会被添加。

```cpp
#include "FilteredGameplayTagContainer.h"

FFilteredGameplayTagContainer TagContainer;

// 添加标签及其关联查询
FGameplayTag RainTag = FGameplayTag::RequestGameplayTag(FName("Weather.Rain"));
FGameplayTagQuery RainQuery = FGameplayTagQuery::MakeQuery_MatchAllTags(
    FGameplayTagContainer::CreateFromArray({FGameplayTag::RequestGameplayTag(FName("World.Outdoor"))})
);

bool bAdded = TagContainer.AddTagFiltered(RainTag, RainQuery);

// 监听标签变化
TagContainer.OnGameplayTagAdded.AddLambda([](FGameplayTag Tag)
{
    UE_LOG(LogTemp, Log, TEXT("Tag added: %s"), *Tag.ToString());
});

TagContainer.OnGameplayTagRemoved.AddLambda([](FGameplayTag Tag)
{
    UE_LOG(LogTemp, Log, TEXT("Tag removed: %s"), *Tag.ToString());
});

// 移除标签时，会自动重新过滤容器中剩余标签的查询条件
TagContainer.RemoveTagFiltered(RainTag);
```

### 进阶用法 — FAudioGameplayRequirements

用于音频系统中根据 GameplayTag 查询决定是否匹配某种音频需求。

```cpp
#include "AudioGameplayRequirements.h"

// 使用预设
UAudioRequirementPreset* Preset = LoadObject<UAudioRequirementPreset>(nullptr, TEXT("/Game/Audio/Presets/CombatPreset"));

FAudioGameplayRequirements Requirements;
Requirements.Preset = Preset;

FGameplayTagContainer CurrentTags;
CurrentTags.AddTag(FGameplayTag::RequestGameplayTag(FName("State.Combat")));
CurrentTags.AddTag(FGameplayTag::RequestGameplayTag(FName("Biome.Forest")));

if (Requirements.Matches(CurrentTags))
{
    // 当前标签满足音频需求，可以播放
}

// 或使用自定义查询
FAudioGameplayRequirements CustomRequirements;
CustomRequirements.Custom = FGameplayTagQuery::MakeQuery_MatchAnyTags(
    FGameplayTagContainer::CreateFromArray({
        FGameplayTag::RequestGameplayTag(FName("State.Combat")),
        FGameplayTag::RequestGameplayTag(FName("State.Alert"))
    })
);

bool bMatches = CustomRequirements.Matches(CurrentTags);
```

### 进阶用法 — 订阅系统

AudioComponentGroup 提供了字符串、布尔、事件三种订阅机制，用于响应参数变化。

```cpp
// 订阅字符串参数变化
Group->SubscribeToStringParam(FName("MusicState"), 
    FStringParamCallback::CreateLambda([](const FString& Value)
    {
        UE_LOG(LogTemp, Log, TEXT("Music state changed to: %s"), *Value);
    })
);

// 订阅事件
Group->SubscribeToEvent(FName("Explosion"),
    FSoundCallback::CreateLambda([]()
    {
        UE_LOG(LogTemp, Log, TEXT("Explosion event triggered!"));
    })
);

// 订阅布尔参数
Group->SubscribeToBool(FName("IsInCombat"),
    FBoolParamCallback::CreateLambda([](bool bValue)
    {
        UE_LOG(LogTemp, Log, TEXT("Combat state: %s"), bValue ? TEXT("true") : TEXT("false"));
    })
);

// 清理时取消订阅
Group->UnsubscribeObject(MyObject);
```

## Demo 示例

一个完整的、可编译的最小示例：创建一个带有 AudioComponentGroup 的 Actor，演示组件组管理和参数控制。

### MyAudioActor.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioComponentGroup.h"
#include "AudioParameterComponent.h"
#include "MyAudioActor.generated.h"

UCLASS()
class AMyAudioActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    // 蓝图可调用：播放指定声音
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void PlayGroupSound(USoundBase* Sound);

    // 蓝图可调用：设置全局音量
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void SetGroupVolume(float Volume);

    // 蓝图可调用：停止所有声音
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void StopAllSounds();

    // 蓝图可调用：切换虚拟化
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void ToggleVirtualization();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    TObjectPtr<UAudioComponentGroup> AudioGroup;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    TObjectPtr<UAudioParameterComponent> AudioParams;
};
```

### MyAudioActor.cpp

```cpp
#include "MyAudioActor.h"
#include "Components/AudioComponent.h"

AMyAudioActor::AMyAudioActor()
{
    PrimaryActorTick.bCanEverTick = true;

    // 创建 AudioComponentGroup 作为 SceneComponent
    AudioGroup = CreateDefaultSubobject<UAudioComponentGroup>(TEXT("AudioGroup"));
    RootComponent = AudioGroup;

    // 创建 AudioParameterComponent
    AudioParams = CreateDefaultSubobject<UAudioParameterComponent>(TEXT("AudioParams"));
    AudioParams->SetupAttachment(RootComponent);
}

void AMyAudioActor::BeginPlay()
{
    Super::BeginPlay();

    // 注册 OnStopped 事件
    if (AudioGroup)
    {
        AudioGroup->OnStopped.AddDynamic(this, &AMyAudioActor::OnGroupStopped);
        
        // 订阅字符串参数变化
        AudioGroup->SubscribeToStringParam(FName("MusicMood"),
            FStringParamCallback::CreateWeakLambda(this, [this](const FString& Value)
            {
                UE_LOG(LogTemp, Log, TEXT("Music mood changed to: %s"), *Value);
            })
        );
    }

    // 通过 AudioParameterComponent 设置初始参数
    if (AudioParams)
    {
        AudioParams->SetFloatParameter(FName("ReverbLevel"), 0.3f);
        AudioParams->SetBoolParameter(FName("IsIndoor"), false);
    }
}

void AMyAudioActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMyAudioActor::PlayGroupSound(USoundBase* Sound)
{
    if (!AudioGroup || !Sound) return;

    // AudioComponentGroup 会自动管理内部组件池
    UAudioComponent* Comp = AudioGroup->GetNextAvailableComponent();
    if (Comp)
    {
        Comp->SetSound(Sound);
        Comp->Play();
    }
}

void AMyAudioActor::SetGroupVolume(float Volume)
{
    if (AudioGroup)
    {
        AudioGroup->SetVolumeMultiplier(FMath::Clamp(Volume, 0.0f, 1.0f));
    }
}

void AMyAudioActor::StopAllSounds()
{
    if (AudioGroup)
    {
        AudioGroup->BroadcastStopAll();
    }
}

void AMyAudioActor::ToggleVirtualization()
{
    if (!AudioGroup) return;

    if (AudioGroup->IsVirtualized())
    {
        AudioGroup->DisableVirtualization();
    }
    else
    {
        AudioGroup->EnableVirtualization();
    }
}

// BeginPlay 中注册的回调
// UFUNCTION() 需要声明在 .h 中，此处简化展示
void AMyAudioActor::OnGroupStopped()
{
    UE_LOG(LogTemp, Log, TEXT("All sounds in group stopped."));
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/GameplayTags 等）。该插件的 Build.cs 仅依赖 UE 核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新宏 |
| 2025-09-09 | `723f87e6` | Added missing include. | 修复缺失的头文件引用 |
| 2025-08-20 | `1746b743` | AGV Updates / Glow up | AudioGameplayVolume 系统更新与优化 |
| 2025-07-29 | `a6ddb9ae` | AudioMixerCore put string definitions for Insights events into .cpp file | Insights 事件字符串定义移入源文件 |
| 2025-07-25 | `5d147547` | [Audio] Add BP utility functions to AudioAssetUserData for interacting with audio asset tags | 为 AudioAssetUserData 添加蓝图标签查询工具函数 |

### 维护评价

- **状态**：**活跃维护中**
- 该插件自 2021 年创建以来持续更新，最近一次实质性更新在 2025 年 8 月（AGV 系统大更新），2025 年 7 月还新增了蓝图工具函数
- 标记为 **IsBetaVersion = true** 且 **Installed = false**，说明仍处于实验阶段，默认不启用
- 近期更新涵盖功能增强（新增蓝图 API）、代码质量改进（头文件修复、日志宏迁移）、以及 AudioGameplayVolume 系统的 UI 优化
- 推荐在需要复杂音频玩法控制的项目中使用，但需注意其 Beta 状态，API 可能在未来版本中变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplay)