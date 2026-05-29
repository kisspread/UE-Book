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

Audio Game play Volume 插件为 Unreal Engine 提供了一套基于体积（Volume）的音频效果控制系统。它解决了在游戏世界中，音频效果（如混响、Submix 特效）需要根据玩家的位置和所处区域进行动态变化的需求。插件通过创建特定的体积（Volume）演员或组件，当玩家（音频监听器）进入、停留或离开这些体积时，可以自动应用、修改或移除预设的音频效果，从而实现与游戏环境紧密集成的空间音频体验。

## 使用场景

- **场景化音频**：当玩家从室外进入一个山洞或大厅时，自动应用特定的混响（Reverb）效果，模拟真实的声音环境。
- **环境音效区域**：为游戏世界的不同区域（如森林、城市、水下）定义独特的音频处理链（Submix Effects），使背景音效和音乐在区域间平滑过渡。
- **交互式音频**：当玩家靠近某个特定的游戏对象（如电台、魔法物品）时，为其添加特殊的音效处理，离开后效果自动移除。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSubmixEffectSettings` | 设置子混音效果的参数 | `USubmixEffectVolumeComponent` |
| `SetReverbSettings` | 设置混响效果的参数 | `UReverbVolumeComponent` |
| `ActivateVolume` | 激活音量组件，使其开始影响音频 | `UAudioGameplayVolumeComponent` |
| `DeactivateVolume` | 停用音量组件 | `UAudioGameplayVolumeComponent` |

### 使用示例（蓝图描述）

1.  **创建体积**：在场景中放置一个 `Audio Volume` 演员，并为其添加 `Reverb Volume Component` 或 `Submix Effect Volume Component`。
2.  **配置效果**：在组件的细节面板中，选择要应用的混响预设（Reverb Preset）或配置子混音效果链。
3.  **控制激活**：可以通过蓝图调用 `ActivateVolume` 和 `DeactivateVolume` 节点，在游戏逻辑中动态控制音量是否生效。

## C++ 用法

### 头文件引入

```cpp
#include "AudioGameplayVolumeComponent.h"
#include "ReverbVolumeComponent.h"
#include "SubmixEffectVolumeComponent.h"
```

### 基本用法

创建一个自定义的音量组件，覆盖默认的激活和停用行为。

```cpp
// MyAudioVolume.h
#pragma once
#include "CoreMinimal.h"
#include "SubmixEffectVolumeComponent.h"
#include "MyAudioVolume.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAudioVolume : public USubmixEffectVolumeComponent
{
	GENERATED_BODY()

public:
	virtual void Activate(bool bReset) override;
	virtual void Deactivate() override;
};

// MyAudioVolume.cpp
#include "MyAudioVolume.h"

void UMyAudioVolume::Activate(bool bReset)
{
	Super::Activate(bReset);
	// 自定义激活逻辑，例如：记录进入时间，触发UI提示等
	UE_LOG(LogTemp, Log, TEXT("Custom Audio Volume Activated"));
}

void UMyAudioVolume::Deactivate()
{
	Super::Deactivate();
	// 自定义停用逻辑
	UE_LOG(LogTemp, Log, TEXT("Custom Audio Volume Deactivated"));
}
```

### 进阶用法

在运行时动态创建并配置一个音量组件。

```cpp
// 在某个Actor或Component中
#include "ReverbVolumeComponent.h"
#include "Sound/ReverbEffect.h"

UReverbVolumeComponent* ReverbComp = NewObject<UReverbVolumeComponent>(this);
ReverbComp->RegisterComponent();

// 假设已有一个UReverbEffect资产
UReverbEffect* ReverbAsset = LoadObject<UReverbEffect>(nullptr, TEXT("/Game/Audio/ReverbPresets/CaveReverb"));
if (ReverbAsset)
{
	ReverbComp->SetReverbEffect(ReverbAsset);
}
ReverbComp->Activate(true);
```

## Demo 示例

一个最小的自定义音频音量组件示例。

```cpp
// SimpleAudioVolumeComponent.h
#pragma once
#include "CoreMinimal.h"
#include "SubmixEffectVolumeComponent.h"
#include "SimpleAudioVolumeComponent.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API USimpleAudioVolumeComponent : public USubmixEffectVolumeComponent
{
	GENERATED_BODY()

public:
	USimpleAudioVolumeComponent();

protected:
	virtual void BeginPlay() override;
	virtual void OnListenerOverlapBegin() override;
	virtual void OnListenerOverlapEnd() override;

private:
	UPROPERTY(EditAnywhere, Category = "Audio")
	USoundEffectSubmixPreset* MyEffectPreset;
};
```

```cpp
// SimpleAudioVolumeComponent.cpp
#include "SimpleAudioVolumeComponent.h"
#include "Sound/SoundEffectSubmix.h"

USimpleAudioVolumeComponent::USimpleAudioVolumeComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void USimpleAudioVolumeComponent::BeginPlay()
{
	Super::BeginPlay();
	if (MyEffectPreset)
	{
		// 设置组件要使用的Submix效果预设
		SetSubmixEffectPreset(MyEffectPreset);
	}
}

void USimpleAudioVolumeComponent::OnListenerOverlapBegin()
{
	Super::OnListenerOverlapBegin();
	UE_LOG(LogTemp, Log, TEXT("Listener entered simple audio volume."));
}

void USimpleAudioVolumeComponent::OnListenerOverlapEnd()
{
	Super::OnListenerOverlapEnd();
	UE_LOG(LogTemp, Log, TEXT("Listener left simple audio volume."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AudioGameplay` | 提供底层的音频游戏播放框架和接口 |
| `AudioMixer` | 提供音频混合和处理能力 |
| `AudioExtensions` | 提供音频扩展点和接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志宏迁移至UE_LOGF，以支持更灵活的格式化日志输出。 |
| 2026-03-30 | `ffed0384` | [AudioGameplayVolumes] Fix priority system for listener-based mutators (e.g. SubmixOverride) | 修复了基于监听器的音频调节器（如子混音覆盖）的优先级系统。 |
| 2026-01-12 | `0ab2481d` | Fixed dynamic delegate bindings to non-const member functions with const pointers. This is a const- | 修复了动态委托绑定到非常量成员函数时，使用常量指针的问题。 |
| 2026-01-05 | `0d4c00d1` | Fix race condition in AudioGameplayVolumeSubsystem | 修复了音频游戏音量子系统中的竞争条件。 |
| 2025-12-17 | `34b66ba1` | [AGV] Fix early distance culling not working for beam-like primitives: now uses bounding box rather | 修复了早期距离剔除对束状（beam-like）基元无效的问题，现在使用包围盒而非…… |

### 维护评价

该插件创建于 2021 年，虽然 `.uplugin` 文件标记为实验性 (`IsBetaVersion=true`)，但从 git 历史来看，它一直在进行积极的维护和功能修复。最近的更新（2026年）集中在修复底层系统错误、优化优先级逻辑和日志系统迁移，表明该插件仍处于**活跃维护**状态。作为实验性插件，其API在未来版本中可能发生变化，但其核心功能稳定，适合在需要高级空间音频控制的游戏项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AudioGameplayVolume)
- [官方文档]()（暂无）
- [测试用例]()（暂无提供）