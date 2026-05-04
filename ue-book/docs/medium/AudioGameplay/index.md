# AudioGameplay

> Core plugin for audio gameplay

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图接口、数据资产基类） |
| 模块 | `AudioGameplay` (Runtime), `AudioGameplayTests` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🏛️ 文物（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioGameplay) | |

## 用途

AudioGameplay 是 UE5 音频系统与 Gameplay 逻辑之间的**桥梁插件**。它解决的核心问题是：如何让游戏中的音频参数、标签（GameplayTag）和音频组件的管理变得与 Gameplay 系统自然衔接。

在 UE5 中，`UAudioComponent` 负责播放声音，但它缺乏以下能力：
- **跨组件的音频参数统一管理**——一个 Actor 上可能有多个 AudioComponent 播放不同声音，需要同时修改它们的音量/音调
- **GameplayTag 与音频资产的关联**——为声音附加元数据标签，以便根据游戏状态筛选/触发声音
- **基于条件的音频开关**——根据空间位置、GameplayTag 等条件自动开关音频
- **音频参数的 Actor 级别广播**——设置一次参数，自动传递给 Actor 上所有正在播放的 AudioComponent

AudioGameplay 提供了 `UAudioComponentGroup`（多组件管理）、`UAudioParameterComponent`（参数广播）、`FFilteredGameplayTagContainer`（条件标签容器）、`FAudioGameplayRequirements`（标签查询预设）等基础设施来解决这些问题。

## 使用场景

- 你有一个角色同时播放脚步声、呼吸声、环境音效，需要一键控制它们的音量 → 用 `UAudioComponentGroup`
- 你需要为声音资产附加 GameplayTag 元数据（如"Combat"、"Ambient"），然后根据游戏状态筛选播放 → 用 `UAudioAssetUserData` + `FAudioGameplayRequirements`
- 你需要一个组件统一管理 Actor 上所有音频的参数（如"室内/室外"状态），并自动传递给正在播放的声音 → 用 `UAudioParameterComponent`
- 你需要实现音频的虚拟化（Virtualization）——当声音远离玩家时暂停播放以节省资源 → 用 `UAudioComponentGroup` 的 `EnableVirtualization` / `DisableVirtualization`
- 你需要根据 GameplayTag 的条件关系动态添加/移除标签（如"战斗音乐"标签依赖"战斗状态"标签存在） → 用 `FFilteredGameplayTagContainer`
- 你需要自定义音频切换条件（如门是否打开、玩家是否在水中） → 实现 `IAudioGameplayCondition` 接口

## 蓝图用法

### 核心节点

#### AudioComponentGroup — 多组件音频管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StaticGetOrCreateComponentGroup` | 静态函数：获取或创建 Actor 上的 AudioComponentGroup | `UAudioComponentGroup` |
| `StopSound` | 停止指定声音在所有组件上的播放，支持淡出时间 | `UAudioComponentGroup` |
| `IsPlayingAny` | 查询是否有任何委托绑定（用于判断是否在播放） | `UAudioComponentGroup` |
| `BroadcastStopAll` | 广播停止所有声音的事件 | `UAudioComponentGroup` |
| `BroadcastKill` | 广播销毁声音的事件 | `UAudioComponentGroup` |
| `BroadcastEvent` | 广播自定义事件名称，触发所有订阅者 | `UAudioComponentGroup` |
| `AddExternalComponent` | 将外部创建的 AudioComponent 加入参数共享 | `UAudioComponentGroup` |
| `RemoveExternalComponent` | 从参数共享中移除外部组件 | `UAudioComponentGroup` |
| `EnableVirtualization` | 启用虚拟化——暂停播放并静音以节省资源 | `UAudioComponentGroup` |
| `DisableVirtualization` | 禁用虚拟化——恢复播放并同步所有缓存参数 | `UAudioComponentGroup` |
| `IsVirtualized` | 查询当前是否处于虚拟化状态 | `UAudioComponentGroup` |
| `SetVolumeMultiplier` | 设置音量乘数（影响组内所有组件） | `UAudioComponentGroup` |
| `SetPitchMultiplier` | 设置音调乘数（影响组内所有组件） | `UAudioComponentGroup` |
| `SetLowPassFilter` | 设置低通滤波频率（影响组内所有组件） | `UAudioComponentGroup` |
| `AddExtension` | 添加扩展接口实现（自定义音量/音调修改逻辑） | `UAudioComponentGroup` |
| `RemoveExtension` | 移除扩展接口实现 | `UAudioComponentGroup` |
| `GetFloatParamValue` | 获取浮点参数的当前值 | `UAudioComponentGroup` |
| `GetBoolParamValue` | 获取布尔参数的当前值 | `UAudioComponentGroup` |
| `GetStringParamValue` | 获取字符串参数的当前值 | `UAudioComponentGroup` |
| `SubscribeToStringParam` | 订阅字符串参数变化事件 | `UAudioComponentGroup` |
| `SubscribeToEvent` | 订阅自定义事件 | `UAudioComponentGroup` |
| `SubscribeToBool` | 订阅布尔参数变化事件 | `UAudioComponentGroup` |
| `UnsubscribeObject` | 取消指定对象的所有订阅 | `UAudioComponentGroup` |

**AudioComponentGroup 事件委托（BlueprintAssignable）：**

| 事件 | 说明 |
|---|---|
| `OnStopped` | 广播停止所有声音时触发 |
| `OnKilled` | 广播销毁声音时触发 |
| `OnVirtualized` | 启用虚拟化时触发 |
| `OnUnvirtualized` | 禁用虚拟化时触发 |

#### AudioParameterComponent — Actor 级音频参数管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetParameters` | 获取当前存储的所有音频参数 | `UAudioParameterComponent` |
| `SetFloatParameter` | 设置浮点参数（自动传递给 Actor 上所有 AudioComponent） | `UAudioParameterComponent` |
| `SetBoolParameter` | 设置布尔参数 | `UAudioParameterComponent` |
| `SetIntParameter` | 设置整数参数 | `UAudioParameterComponent` |
| `SetStringParameter` | 设置字符串参数 | `UAudioParameterComponent` |
| `SetObjectParameter` | 设置对象参数 | `UAudioParameterComponent` |
| `ResetParameters` | 重置所有参数 | `UAudioParameterComponent` |

#### AudioAssetUserData — 音频资产标签查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAllTags` | 获取声音资产及其 SoundClass 上的所有 AudioAssetUserData 标签 | `UAudioAssetUserData` |
| `HasTag` | 检查声音资产或其 SoundClass 是否拥有指定标签 | `UAudioAssetUserData` |
| `GetFilteredTags` | 获取与指定标签匹配的所有标签 | `UAudioAssetUserData` |

#### AudioGameplayRequirements — 标签匹配查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Matches`（AudioRequirementPreset） | 检查标签容器是否满足预设查询 | `UAudioRequirementPreset` |
| `Matches`（AudioGameplayRequirements） | 检查标签容器是否同时满足 Preset 和 Custom 查询 | `FAudioGameplayRequirements` |

### 使用示例（蓝图描述）

**示例 1：为角色创建音频组件组并控制音量**

```
BeginPlay 事件中:
1. 节点: "Get or Create Component Group" (静态函数, Target为Self Actor)
   → 返回 UAudioComponentGroup 引用, 存为变量 "SoundGroup"

按键事件 (如 VolumeDown):
1. 节点: "Get Float Param Value" (Target: SoundGroup, ParamName: "MasterVolume")
   → 返回当前音量
2. 节点: "Set Float Parameter" (Target: SoundGroup, InName: "MasterVolume", InFloat: CurrentVolume - 0.1)
```

**示例 2：通过 AudioParameterComponent 管理 Actor 音频参数**

```
蓝图编辑器中:
1. 在角色蓝图上添加 "AudioParameterComponent" 组件
2. 在 Details 面板的 Parameters 数组中添加默认参数:
   - Name: "IsIndoor", Type: Boolean, Value: false

游戏中动态设置:
1. 节点: "Set Bool Parameter" (Target: AudioParameterComponent, InName: "IsIndoor", InValue: true)
   → 自动传递给该 Actor 上所有正在播放的 AudioComponent
```

**示例 3：为声音资产添加 GameplayTag 元数据**

```
在 Content Browser 中:
1. 选择声音资产 → Details → Asset User Data → 添加 "AudioAssetUserData"
2. 在 MetadataTags 中添加标签，如 "Audio.Combat.Impact"

运行时查询:
1. 节点: "Has Tag" (InSound: 某个声音资产, InTag: "Audio.Combat.Impact")
   → 返回 true/false
```

## C++ 用法

### 头文件引入

```cpp
#include "AudioComponentGroup.h"
#include "AudioParameterComponent.h"
#include "AudioGameplayRequirements.h"
#include "AudioAssetUserData.h"
#include "FilteredGameplayTagContainer.h"
```

### 基本用法

**获取或创建 AudioComponentGroup 并管理音频参数：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplay/Private/AudioComponentGroup.cpp

// 获取或创建 Actor 上的 AudioComponentGroup（会自动向上查找 Actor 层级）
UAudioComponentGroup* Group = UAudioComponentGroup::StaticGetOrCreateComponentGroup(MyActor);
if (Group)
{
    // 设置组级别的音量、音调和低通滤波
    Group->SetVolumeMultiplier(0.5f);
    Group->SetPitchMultiplier(1.2f);
    Group->SetLowPassFilter(5000.0f);

    // 设置音频参数（自动同步到组内所有 AudioComponent）
    Group->SetFloatParameter(FName("WindIntensity"), 0.8f);
    Group->SetBoolParameter(FName("IsUnderwater"), true);

    // 停止指定声音
    Group->StopSound(MySoundAsset, 0.5f); // 0.5 秒淡出
}
```

**通过 AudioParameterComponent 管理 Actor 级参数：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplay/Private/AudioParameterComponent.cpp

// 假设已获取 UAudioParameterComponent* ParamComp
ParamComp->SetFloatParameter(FName("ReverbWetLevel"), 0.3f);
ParamComp->SetBoolParameter(FName("IsIndoors"), true);

// 获取所有当前参数
const TArray<FAudioParameter>& Params = ParamComp->GetParameters();
```

**使用 GameplayTag 查询音频需求：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplay/Private/AudioGameplayRequirements.cpp

// 创建需求预设
UAudioRequirementPreset* Preset = NewObject<UAudioRequirementPreset>();
Preset->Query = FGameplayTagQuery::BuildQuery(
    FGameplayTagQueryExpression().AnyTagsMatch()
        .AddTag(FGameplayTag::RequestGameplayTag(FName("Audio.Combat")))
        .AddTag(FGameplayTag::RequestGameplayTag(FName("Audio.Ambient")))
);

// 创建完整需求（Preset + Custom 查询）
FAudioGameplayRequirements Requirements;
Requirements.Preset = Preset;
Requirements.Custom = FGameplayTagQuery::BuildQuery(
    FGameplayTagQueryExpression().NoTagsMatch()
        .AddTag(FGameplayTag::RequestGameplayTag(FName("Audio.Muted")))
);

// 测试标签是否满足需求
FGameplayTagContainer TestTags;
TestTags.AddTag(FGameplayTag::RequestGameplayTag(FName("Audio.Combat")));
bool bMatches = Requirements.Matches(TestTags); // true
```

### 进阶用法

**实现 IAudioComponentGroupExtension 自定义音量修改逻辑：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplay/Public/AudioComponentGroupExtension.h

// Extension 接口允许你自定义音量/音调/低通滤波的计算逻辑
UCLASS()
class UMyAudioExtension : public UObject, public IAudioComponentGroupExtension
{
    GENERATED_BODY()

public:
    // 每帧调用，可修改 OutModifier 的 Volume/Pitch/LowPassFrequency
    virtual void Update(const float DeltaTime, UAudioComponentGroup* Group, FAudioComponentModifier& OutModifier) override
    {
        // 例如：根据距离衰减音量
        float DistanceToListener = CalculateDistance();
        OutModifier.Volume *= FMath::Clamp(1.0f - (DistanceToListener / MaxDistance), 0.0f, 1.0f);
    }

    virtual void OnAddedToGroup(UAudioComponentGroup* NewGroup) override
    {
        // 被添加到组时的初始化逻辑
    }

    virtual void OnComponentAdded(UAudioComponent* NewComponent) override
    {
        // 新组件被添加到组时的回调
    }
};

// 使用方式
Group->AddExtension(MyExtensionObject);
```

**使用 FFilteredGameplayTagContainer 实现条件标签系统：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplayTests/Private/FilteredGameplayTagContainerTests.cpp

FFilteredGameplayTagContainer TagContainer;

// 添加标签（无条件）
FGameplayTag CombatTag = FGameplayTag::RequestGameplayTag(FName("Audio.Combat"));
TagContainer.AddTagFiltered(CombatTag);

// 添加带条件的标签：只有当 CombatTag 存在时，MusicTag 才有效
FGameplayTag MusicTag = FGameplayTag::RequestGameplayTag(FName("Audio.Music"));
FGameplayTagQuery ConditionQuery = FGameplayTagQuery::BuildQuery(
    FGameplayTagQueryExpression().AnyTagsMatch().AddTag(CombatTag)
);
TagContainer.AddTagFiltered(MusicTag, ConditionQuery);
// 此时 MusicTag 被添加成功（因为 CombatTag 存在）

// 移除 CombatTag 时，MusicTag 也会被自动移除（因为条件不再满足）
TagContainer.RemoveTagFiltered(CombatTag);
// MusicTag 已被自动移除

// 监听标签变化
TagContainer.OnGameplayTagAdded.AddLambda([](const FGameplayTag& AddedTag) {
    UE_LOG(LogTemp, Log, TEXT("Tag added: %s"), *AddedTag.ToString());
});
TagContainer.OnGameplayTagRemoved.AddLambda([](const FGameplayTag& RemovedTag) {
    UE_LOG(LogTemp, Log, TEXT("Tag removed: %s"), *RemovedTag.ToString());
});
```

**使用 FShuffleUtil 实现不重复随机播放：**

```cpp
// 来源: Engine/Plugins/AudioGameplay/Source/AudioGameplay/Public/AudioGameplayShuffle.h

UE::Audio::FShuffleUtil Shuffle;
Shuffle.Initialize(SoundArray.Num()); // 初始化为数组大小

for (int32 i = 0; i < SoundArray.Num(); ++i)
{
    uint8 NextIndex = Shuffle.GetNextIndex();
    // NextIndex 返回 0 到 ArraySize-1 之间的值，保证每个索引恰好返回一次后再重置
    PlaySound(SoundArray[NextIndex]);
}
```

## Demo 示例

以下是一个最小可编译示例，展示如何使用 AudioGameplay 插件的核心功能：

### Build.cs 依赖

```csharp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "AudioGameplay",
    "AudioExtensions",
    "Core",
    "GameplayTags",
});
```

### 头文件

```cpp
// MyAudioManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioComponentGroup.h"
#include "AudioParameterComponent.h"
#include "MyAudioManager.generated.h"

UCLASS()
class AMyAudioManager : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioManager();

    virtual void BeginPlay() override;

    // 蓝图可调用：切换室内/室外状态
    UFUNCTION(BlueprintCallable, Category = "Audio")
    void SetIndoorState(bool bIsIndoor);

    // 蓝图可调用：获取音频组件组
    UFUNCTION(BlueprintCallable, Category = "Audio")
    UAudioComponentGroup* GetSoundGroup() const { return SoundGroup; }

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    TObjectPtr<UAudioParameterComponent> AudioParams;

private:
    UPROPERTY()
    TObjectPtr<UAudioComponentGroup> SoundGroup;
};
```

### 实现文件

```cpp
// MyAudioManager.cpp
#include "MyAudioManager.h"
#include "AudioGameplayRequirements.h"

AMyAudioManager::AMyAudioManager()
{
    AudioParams = CreateDefaultSubobject<UAudioParameterComponent>(TEXT("AudioParams"));

    // 设置默认参数
    AudioParams->SetBoolParameter(FName("IsIndoors"), false);
    AudioParams->SetFloatParameter(FName("ReverbWetLevel"), 0.0f);
}

void AMyAudioManager::BeginPlay()
{
    Super::BeginPlay();

    // 获取或创建音频组件组
    SoundGroup = UAudioComponentGroup::StaticGetOrCreateComponentGroup(this);
    if (SoundGroup)
    {
        // 设置默认音量
        SoundGroup->SetVolumeMultiplier(1.0f);
    }
}

void AMyAudioManager::SetIndoorState(bool bIsIndoor)
{
    // 设置参数，自动传递给 Actor 上所有正在播放的 AudioComponent
    AudioParams->SetBoolParameter(FName("IsIndoors"), bIsIndoor);
    AudioParams->SetFloatParameter(FName("ReverbWetLevel"), bIsIndoor ? 0.6f : 0.0f);

    // 同时更新组件组的低通滤波（室内声音更闷）
    if (SoundGroup)
    {
        SoundGroup->SetLowPassFilter(bIsIndoors ? 3000.0f : MAX_FILTER_FREQUENCY);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioExtensions` | 音频扩展接口（IAudioParameterControllerInterface 等） |
| `Core` | UE 核心模块 |
| `GameplayTags` | GameplayTag 系统（标签容器、标签查询） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `Engine` | 引擎核心（AudioComponent、Actor 等，私有依赖） |
| `AudioMixerCore` | 音频混音器核心（私有依赖） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-08-20 | `1746b7434e4f` | AGV Updates: 重命名 Volume Proxy → Audio Toggle，AGV Primitive Proxy → Audio Listener In Primitives 等；批量通知进入/退出代理；更新工具提示 | 大规模重命名和 UI 改进，使 AudioGameplayVolume 子系统更直观。说明该插件仍在被其他系统（如 AudioGameplayVolume）依赖并持续演进 |
| 2025-07-29 | `a6ddb9ae0675` | AudioMixerCore 将 Insights 事件字符串定义移入 .cpp 文件 | 代码组织优化，减少头文件中的字符串定义 |
| 2025-07-25 | `5d147547bdfb` | 为 AudioAssetUserData 添加蓝图工具函数 | 新增 `GetAllTags`、`HasTag`、`GetFilteredTags` 等蓝图可用的静态函数，增强音频资产标签的蓝图查询能力 |

### 维护评价

- **创建时间**: 2021 年 10 月，约 5 年历史
- **最近更新**: 2025 年 8 月，3 个月内有多次实质性更新
- **活跃度**: **活跃维护中**。近期更新包含新功能（BP 工具函数）、大规模重命名重构、以及代码质量改进
- **Beta 状态**: `.uplugin` 中 `IsBetaVersion: true`，表明 Epic 认为此插件尚未完全稳定，API 可能发生变化
- **推荐**: **推荐使用**。该插件是 UE5 音频 Gameplay 系统的基础设施，被 AudioGameplayVolume 等插件依赖。虽然是 Beta 状态，但已有 5 年历史且持续更新，说明它在 Epic 内部被广泛使用。建议使用时注意 API 可能变化，并关注版本更新

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/AudioGameplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AudioGameplay/Source/AudioGameplayTests/Private/FilteredGameplayTagContainerTests.cpp)
