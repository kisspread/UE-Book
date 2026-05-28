# Audio Gameplay Volume

> Audio Gameplay Volume Plugin

| 属性 | 值 |
|---|---|
| 中文名 | 音频游戏音量 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioGameplayVolume` (Runtime), `AudioGameplayVolumeEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2021-10-27 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplayVolume) | |

## 用途

AudioGameplayVolume 提供了一套**基于组件的音频空间音量系统**，用于根据音频监听器（玩家）与音量区域的相对位置，动态调整音频行为。与 UE4 时代的 `AudioVolume` Actor 不同，本插件采用**组合式（Component-Based）架构**，将音量行为拆分为可独立配置的组件模块。

核心解决的问题：
- 当玩家从室外走进室内时，室外声音需要降低音量、增加低通滤波，同时应用室内混响
- 不同音量区域可以叠加，通过优先级系统决定哪个效果生效
- 需要将音频效果（衰减、滤波、混响、子混音发送/覆盖）作为独立组件灵活组合，而非一次性配置所有属性

底层通过 `UAudioGameplayVolumeSubsystem`（音频引擎子系统）在音频线程上安全地管理代理（Proxy）数据，避免游戏线程与音频线程的竞态条件。

## 使用场景

- **建筑室内/室外音频过渡**：玩家走进房子时，外部环境音自动衰减、加滤波，室内自动应用混响
- **多区域音频优先级**：场景中有多个重叠的音量区域，需要根据优先级决定哪个效果生效
- **基于条件的音频触发**：不依赖物理碰撞，而是通过任意游戏逻辑条件（实现 `IAudioGameplayCondition` 接口）来触发音量效果
- **自定义音频交互**：通过继承 `UAudioGameplayVolumeComponentBase` 创建完全自定义的音量交互行为
- **Submix 动态路由**：根据监听器位置动态改变音频的 Submix 发送或效果链覆盖

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Enabled` | 启用/禁用音量，禁用后不再参与碰撞检测 | `AAudioGameplayVolume` |
| `Set Exterior Volume` | 设置监听器在音量内时，外部声音的音量（可插值） | `UAttenuationVolumeComponent` |
| `Set Interior Volume` | 设置监听器在音量外时，内部声音的音量（可插值） | `UAttenuationVolumeComponent` |
| `Set Exterior LPF` | 设置监听器在音量内时，外部声音的低通滤波频率（可插值） | `UFilterVolumeComponent` |
| `Set Interior LPF` | 设置监听器在音量外时，内部声音的低通滤波频率（可插值） | `UFilterVolumeComponent` |
| `Set Reverb Settings` | 设置该音量区域的混响参数 | `UReverbVolumeComponent` |
| `Set Submix Send Settings` | 设置 Submix 发送规则（基于声源/监听器位置） | `USubmixSendVolumeComponent` |
| `Set Submix Override Settings` | 设置 Submix 效果链覆盖规则 | `USubmixOverrideVolumeComponent` |
| `Set Priority` | 设置该组件的优先级（多音量重叠时取最高优先级） | `UAudioGameplayVolumeMutator` |

### 事件

| 事件 | 说明 | 所在类 |
|---|---|---|
| `On Listener Enter` | 监听器进入音量时触发（可覆盖原生事件） | `AAudioGameplayVolume` |
| `On Listener Exit` | 监听器离开音量时触发（可覆盖原生事件） | `AAudioGameplayVolume` |
| `On Toggled On` | Audio Toggle 从 Off 变为 On 时触发 | `UAudioGameplayVolumeComponent` |
| `On Toggled Off` | Audio Toggle 从 On 变为 Off 时触发 | `UAudioGameplayVolumeComponent` |

### 使用示例（蓝图描述）

**基本室内/室外音频设置：**

1. 在场景中放置一个 `AudioGameplayVolume` Actor，调整 Brush 形状覆盖室内区域
2. 为其添加 `AttenuationVolumeComponent`：设置 `ExteriorVolume = 0.2`（在室内时室外声音降至 20%）、`InteriorVolume = 1.0`、插值时间 0.5 秒
3. 为其添加 `FilterVolumeComponent`：设置 `ExteriorLPF = 2000`（在室内时外部声音加 2kHz 低通滤波）
4. 为其添加 `ReverbVolumeComponent`：配置混响预设参数
5. 所有 Mutator 组件的 `Priority` 保持默认 0 即可；如果多个音量重叠，优先级高的组件效果覆盖优先级低的

**自定义条件触发：**

1. 创建一个 Actor 并实现 `IAudioGameplayCondition` 接口
2. 添加 `AudioGameplayVolumeComponent`（即"Audio Toggle"组件）
3. 将 Toggle Condition 设置为 `Arbitrary` 类型
4. 在 Actor 的 `ConditionMet` 函数中编写自定义游戏逻辑（如：当某个开关打开时返回 true）
5. 按需添加各种 Mutator 组件

## C++ 用法

### 头文件引入

```cpp
#include "AudioGameplayVolume.h"
#include "AudioGameplayVolumeComponent.h"
#include "AudioGameplayVolumeSubsystem.h"
#include "AttenuationVolumeComponent.h"
#include "FilterVolumeComponent.h"
#include "ReverbVolumeComponent.h"
#include "SubmixSendVolumeComponent.h"
#include "SubmixOverrideVolumeComponent.h"
```

### 基本用法

创建一个带有完整音频效果的 AudioGameplayVolume：

```cpp
// 在场景中生成一个 AudioGameplayVolume 并配置效果
// 来源: Public/AudioGameplayVolume.h, Public/AttenuationVolumeComponent.h

UWorld* World = GetWorld();
FActorSpawnParameters SpawnParams;
AAudioGameplayVolume* Volume = World->SpawnActor<AAudioGameplayVolume>(
    AAudioGameplayVolume::StaticClass(),
    FVector::ZeroVector,
    FRotator::ZeroRotator,
    SpawnParams
);

// 添加内部/外部衰减组件
UAttenuationVolumeComponent* AttenuationComp = NewObject<UAttenuationVolumeComponent>(Volume);
AttenuationComp->SetupAttachment(Volume->GetRootComponent());
AttenuationComp->SetInteriorVolume(1.0f, 0.5f);   // 室内声音: 满音量, 0.5秒插值
AttenuationComp->SetExteriorVolume(0.3f, 0.5f);    // 室外声音: 30%音量, 0.5秒插值
AttenuationComp->SetPriority(0);
AttenuationComp->RegisterComponent();

// 添加低通滤波组件
UFilterVolumeComponent* FilterComp = NewObject<UFilterVolumeComponent>(Volume);
FilterComp->SetupAttachment(Volume->GetRootComponent());
FilterComp->SetInteriorLPF(MAX_FILTER_FREQUENCY, 0.5f);  // 室内声音: 无滤波
FilterComp->SetExteriorLPF(1500.0f, 0.5f);               // 室外声音: 1.5kHz 截止频率
FilterComp->SetPriority(0);
FilterComp->RegisterComponent();

// 添加混响组件
UReverbVolumeComponent* ReverbComp = NewObject<UReverbVolumeComponent>(Volume);
ReverbComp->SetupAttachment(Volume->GetRootComponent());
FReverbSettings ReverbSettings;
ReverbSettings.bApplyReverb = true;
ReverbSettings.ReverbEffect = SomeReverbEffect;
ReverbSettings.Volume = 0.7f;
ReverbSettings.FadeTime = 2.0f;
ReverbComp->SetReverbSettings(ReverbSettings);
ReverbComp->RegisterComponent();
```

### 进阶用法

通过 C++ 创建自定义条件代理和自定义交互组件：

```cpp
// 1. 自定义 AudioGameplayVolumeComponentBase 以实现监听器进入/退出回调
// 来源: Public/AudioGameplayVolumeComponent.h

UCLASS()
class UMyVolumeComponent : public UAudioGameplayVolumeComponentBase
{
    GENERATED_BODY()

public:
    // IAudioGameplayVolumeInteraction 接口实现
    virtual void OnListenerEnter_Implementation(UAudioGameplayComponent* Target) override
    {
        UE_LOG(LogTemp, Log, TEXT("Listener entered custom volume"));
    }

    virtual void OnListenerExit_Implementation(UAudioGameplayComponent* Target) override
    {
        UE_LOG(LogTemp, Log, TEXT("Listener exited custom volume"));
    }
};

// 2. 创建自定义条件（通过 IAudioGameplayCondition 接口）
// 来源: Public/AudioGameplayVolumeProxy.h (UAGVConditionProxy 会查找实现此接口的对象)

UCLASS()
class AMyConditionActor : public AActor, public IAudioGameplayCondition
{
    GENERATED_BODY()

public:
    virtual bool ConditionMet_Implementation() const override
    {
        // 自定义条件逻辑
        return bSomeGameState;
    }

    virtual bool ConditionMet_Position_Implementation(const FVector& Position) const override
    {
        return ConditionMet_Implementation();
    }
};
```

### 子混音动态路由

```cpp
// 来源: Public/SubmixSendVolumeComponent.h, Public/SubmixOverrideVolumeComponent.h

// Submix Send - 根据监听器位置动态发送音频到 Submix
USubmixSendVolumeComponent* SubmixSendComp = NewObject<USubmixSendVolumeComponent>(Volume);
TArray<FAudioVolumeSubmixSendSettings> SendSettings;
// ... 配置 SendSettings
SubmixSendComp->SetSubmixSendSettings(SendSettings);
SubmixSendComp->RegisterComponent();

// Submix Override - 覆盖特定 Submix 的效果链
USubmixOverrideVolumeComponent* SubmixOverrideComp = NewObject<USubmixOverrideVolumeComponent>(Volume);
TArray<FAudioVolumeSubmixOverrideSettings> OverrideSettings;
// ... 配置 OverrideSettings
SubmixOverrideComp->SetSubmixOverrideSettings(OverrideSettings);
SubmixOverrideComp->RegisterComponent();
```

## Demo 示例

以下是一个最小可编译示例，创建一个带完整室内音频效果的音量 Actor：

```cpp
// MyIndoorAudioVolume.h
#pragma once

#include "CoreMinimal.h"
#include "AudioGameplayVolume.h"
#include "MyIndoorAudioVolume.generated.h"

class UAttenuationVolumeComponent;
class UFilterVolumeComponent;
class UReverbVolumeComponent;

UCLASS()
class MYGAME_API AMyIndoorAudioVolume : public AAudioGameplayVolume
{
    GENERATED_BODY()

public:
    AMyIndoorAudioVolume();

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UAttenuationVolumeComponent> Attenuation;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UFilterVolumeComponent> Filter;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UReverbVolumeComponent> Reverb;
};
```

```cpp
// MyIndoorAudioVolume.cpp
#include "MyIndoorAudioVolume.h"
#include "AttenuationVolumeComponent.h"
#include "FilterVolumeComponent.h"
#include "ReverbVolumeComponent.h"

AMyIndoorAudioVolume::AMyIndoorAudioVolume()
{
    // 内部/外部音量衰减：玩家在室内时，室外声音降至 20%
    Attenuation = CreateDefaultSubobject<UAttenuationVolumeComponent>(TEXT("Attenuation"));
    Attenuation->SetInteriorVolume(1.0f, 0.3f);
    Attenuation->SetExteriorVolume(0.2f, 0.3f);

    // 低通滤波：玩家在室内时，室外声音加 1.5kHz 低通
    Filter = CreateDefaultSubobject<UFilterVolumeComponent>(TEXT("Filter"));
    Filter->SetInteriorLPF(MAX_FILTER_FREQUENCY, 0.3f);
    Filter->SetExteriorLPF(1500.0f, 0.3f);

    // 混响
    Reverb = CreateDefaultSubobject<UReverbVolumeComponent>(TEXT("Reverb"));
    FReverbSettings Settings;
    Settings.bApplyReverb = true;
    Settings.Volume = 0.6f;
    Settings.FadeTime = 1.0f;
    Reverb->SetReverbSettings(Settings);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioGameplay` | 基础音频游戏交互框架（插件声明的 Plugin 依赖） |
| `AudioMixer` | 音频混音器子系统支持 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到 UE_LOGF 格式 |
| 2026-03-30 | `ffed0384` | [AudioGameplayVolumes] Fix priority system for listener-based mutators (e.g. SubmixOverride) | 修复基于监听器的 Mutator 优先级系统（如 SubmixOverride） |
| 2026-01-12 | `0ab2481d` | Fixed dynamic delegate bindings to non-const member functions with const pointers. This is a const-... | 修复将动态委托绑定到非 const 成员函数时 const 指针的问题 |
| 2026-01-05 | `0d4c00d1` | Fix race condition in AudioGameplayVolumeSubsystem | 修复 AudioGameplayVolumeSubsystem 中的竞态条件 |
| 2025-12-17 | `34b66ba1` | [AGV] Fix early distance culling not working for beam-like primitives: now uses bounding box rather ... | 修复细长图元的早期距离剔除失效问题，改用包围盒判断 |

### 维护评价

- **状态**：实验性插件（`IsBetaVersion: true`），仍在活跃维护中
- **最近更新**：最近 6 个月内有多次实质性修复（竞态条件、优先级系统、剔除逻辑），表明 Epic 内部仍在持续使用和维护
- **年龄**：约 4 年（2021-10 创建），属于 UE5 早期引入的较新插件
- **已知限制**：Beta 状态意味着 API 可能在未来版本发生变化；`AudioGameplayVolumeProxyMutator.h` 已在 5.1 中废弃，分散到其他头文件
- **推荐度**：✅ 推荐使用。虽然是 Beta，但功能完整、持续维护、修复及时。对于需要精细控制室内/室外音频过渡的项目，这是官方推荐的方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplayVolume)
- 官方文档（暂无）