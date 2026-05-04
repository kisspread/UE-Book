# Audio Modulation

> Default implementation of Audio Modulation in the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产工厂、Insights 面板、编辑器布局） |
| 模块 | `AudioModulation` (Runtime), `AudioModulationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioModulation) | |

## 用途

Audio Modulation 是 Unreal 音频引擎的**参数调制框架**。它解决的核心问题是：如何在运行时动态地改变音频参数（如音量、滤波器频率、音高等），而不是在资产中写死固定值。

这个 plugin 提供了一套完整的"信号链"架构：

1. **Parameter（参数）**：定义要调制什么属性（音量、频率等）以及其数值范围和混合方式
2. **Bus（总线）**：承载一个参数值的通道，多个 Bus 可以通过不同的 Parameter 独立控制
3. **Generator（生成器）**：自动生成调制信号的源头（LFO、包络跟随器、AD 包络）
4. **Patch（补丁）**：将多个 Bus 的值通过曲线变换映射到目标参数
5. **Mix（混音）**：对多个 Bus 进行分组管理，支持淡入淡出和时序控制
6. **Destination（目标）**：绑定到具体的音频组件，追踪调制值

为什么需要这个？想象一个恐怖游戏：你希望脚步声的音量随玩家移动速度变化，低通滤波器随环境光照变化，背景音乐混响随距离变化。Audio Modulation 让你可以用资产驱动的方式把所有这些"变化关系"组织在一起，而不需要在蓝图里写大量 Tick 逻辑。

## 使用场景

- **动态音量控制**：用 Bus Mix 管理不同游戏状态（菜单、战斗、过场）的全局音量平衡
- **参数自动化**：用 LFO 或包络跟随器自动生成振荡/跟随信号来调制滤波器、音高等
- **音频分层混合**：通过 Mix 的淡入淡出在不同音频场景之间平滑过渡
- **运行时效果调制**：在蓝图或 C++ 中实时改变音频参数（如根据车速调制引擎音效的音调）
- **MetaSound 集成**：在 MetaSound 图中读取调制器的值，实现更复杂的音频逻辑

## 蓝图用法

所有蓝图节点位于 `Audio > Modulation` 类别下，通过 `UAudioModulationStatics` 蓝图函数库暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Control Bus` | 创建一个控制总线，指定名称和参数类型 | `UAudioModulationStatics` |
| `Create Control Bus Mix` | 创建混音，配置多个 Stage 及其淡入淡出时间 | `UAudioModulationStatics` |
| `Create Control Bus Mix Stage` | 创建单个混音阶段（Bus + 目标值 + Attack/Release） | `UAudioModulationStatics` |
| `Create Bus Mix From Value` | 快速创建：为多个 Bus 生成统一值的 Mix | `UAudioModulationStatics` |
| `Create Modulation Destination` | 创建调制目标，激活并追踪调制器值 | `UAudioModulationStatics` |
| `Create LFO Generator` | 创建 LFO 生成器（正弦/锯齿/方波等） | `UAudioModulationStatics` |
| `Create AD Envelope Generator` | 创建 Attack/Decay 包络生成器 | `UAudioModulationStatics` |
| `Create Envelope Follower Generator` | 创建包络跟随器（跟随 AudioBus 振幅） | `UAudioModulationStatics` |
| `Create Modulation Parameter` | 创建自定义调制参数 | `UAudioModulationStatics` |
| `Activate Control Bus Mix` | 激活一个 Mix | `UAudioModulationStatics` |
| `Deactivate Control Bus Mix` | 停用一个 Mix | `UAudioModulationStatics` |
| `Set Control Bus Mix` | 运行时更新 Mix 的 Stage 值 | `UAudioModulationStatics` |
| `Set Control Bus Mix By Filter` | 按地址/参数类过滤更新 Mix | `UAudioModulationStatics` |
| `Set Global Control Bus Mix Value` | 设置全局 Mix 值（适合始终活跃的 Bus） | `UAudioModulationStatics` |
| `Clear Global Control Bus Mix Value` | 清除全局 Mix 值，淡出到默认 | `UAudioModulationStatics` |
| `Save Control Bus Mix to Profile` | 将 Mix 保存到 ini 配置文件 | `UAudioModulationStatics` |
| `Load Control Bus Mix From Profile` | 从 ini 加载 Mix 配置 | `UAudioModulationStatics` |
| `Get Modulator Value` | 获取调制器当前归一化值 | `UAudioModulationStatics` |
| `Get Modulators From Destination` | 获取目标上绑定的所有调制器 | `UAudioModulationStatics` |
| `Update Modulator` | 将 UObject 修改提交到音频线程 | `UAudioModulationStatics` |
| `Is Control Bus Mix Active` | 查询 Mix 是否激活 | `UAudioModulationStatics` |

### 调制目标（Destination）节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Watched Modulator` | 设置要追踪的调制器 | `UAudioModulationDestination` |
| `Clear Modulator` | 清除追踪的调制器 | `UAudioModulationDestination` |
| `Get Watched Modulator Value` | 获取追踪到的调制器当前值 | `UAudioModulationDestination` |
| `Get Modulator` | 获取当前设置的调制器对象 | `UAudioModulationDestination` |

### 使用示例（蓝图描述）

**示例 1：创建一个 LFO 控制的音量调制**

1. 调用 `Create Modulation Parameter`，ParamClass 选择 `SoundModulationParameterVolume`，创建音量参数
2. 调用 `Create Control Bus`，传入上一步的 Parameter，得到一个 Bus
3. 调用 `Create LFO Generator`，配置 Shape=Sine, Frequency=2.0, Amplitude=0.5
4. 在音频组件的 Modulation 设置中，将 Bus 指定为音量的 Modulation Source
5. 调用 `Activate Control Bus Mix` 或使用 `Create Modulation Destination` 激活

**示例 2：用 Mix 管理游戏状态音频**

1. 创建多个 Bus：MusicVolumeBus、SFXVolumeBus、VoiceVolumeBus
2. 为每种状态创建 Mix：CombatMix（SFX=1.0, Music=0.3）、ExplorationMix（SFX=0.7, Music=0.8）
3. 状态切换时调用 `Deactivate Control Bus Mix` 停用当前 Mix，`Activate Control Bus Mix` 激活新 Mix
4. Mix 会自动按配置的 AttackTime/ReleaseTime 平滑过渡

**示例 3：运行时读取调制值**

1. 创建 `Create Modulation Destination`，绑定一个 Bus
2. 在 Tick 中调用 `Get Watched Modulator Value` 读取当前值
3. 用该值驱动其他逻辑（如 UI 音量表）

## C++ 用法

### 头文件引入

```cpp
#include "AudioModulationStatics.h"   // 蓝图函数库（静态方法）
#include "SoundControlBus.h"           // 控制总线
#include "SoundControlBusMix.h"        // 总线混音
#include "SoundModulationPatch.h"      // 调制补丁
#include "SoundModulationParameter.h"  // 调制参数
#include "SoundModulationGenerator.h"  // 生成器基类
#include "Generators/SoundModulationLFO.h"              // LFO
#include "Generators/SoundModulationADEnvelope.h"        // AD 包络
#include "Generators/SoundModulationEnvelopeFollower.h"  // 包络跟随器
#include "AudioModulationDestination.h"                 // 调制目标
#include "AudioModulation.h"                            // 模块/Manager
```

### 基本用法

**创建参数和 Bus：**

```cpp
// 创建一个音量参数
USoundModulationParameter* VolumeParam = UAudioModulationStatics::CreateModulationParameter(
    WorldContext, TEXT("MyVolume"), USoundModulationParameterVolume::StaticClass(), 1.0f);

// 创建一个控制 Bus
USoundControlBus* Bus = UAudioModulationStatics::CreateBus(
    WorldContext, TEXT("SFXVolume"), VolumeParam, false);
```

**创建 Mix 并激活：**

```cpp
// 创建 Mix Stage
FSoundControlBusMixStage Stage = UAudioModulationStatics::CreateBusMixStage(
    WorldContext, Bus, 0.8f, 0.2f, 0.2f);  // 值=0.8, Attack=0.2s, Release=0.2s

// 创建并激活 Mix
TArray<FSoundControlBusMixStage> Stages = { Stage };
USoundControlBusMix* Mix = UAudioModulationStatics::CreateBusMix(
    WorldContext, TEXT("MyMix"), Stages, true, -1.0, false);
```

**创建调制目标并追踪值：**

```cpp
// 创建 Destination 来激活并追踪一个 Bus
UAudioModulationDestination* Dest = UAudioModulationStatics::CreateModulationDestination(
    WorldContext, TEXT("MyDest"), Bus);

// 在 Tick 中读取值
float CurrentValue = Dest->GetValue();
```

**创建 LFO 生成器：**

```cpp
FSoundModulationLFOParams LFOParams;
LFOParams.Shape = ESoundModulationLFOShape::Sine;
LFOParams.Frequency = 2.0f;
LFOParams.Amplitude = 0.5f;
LFOParams.Offset = 0.5f;

USoundModulationGeneratorLFO* LFO = UAudioModulationStatics::CreateLFOGenerator(
    WorldContext, TEXT("MyLFO"), LFOParams);
```

### 进阶用法

**通过 Filter 更新 Mix（适合大型项目分组管理）：**

```cpp
// 设置 Bus 的 Address（用于过滤）
Bus->Address = TEXT("Music.Volume");

// 按地址过滤更新所有匹配的 Stage
UAudioModulationStatics::UpdateMixByFilter(
    WorldContext, Mix, TEXT("Music.*"),
    USoundModulationParameterVolume::StaticClass(), nullptr,
    0.5f, 0.3f);  // 值=0.5, FadeTime=0.3s
```

**使用 C++ Manager API 直接操作：**

```cpp
// 获取 Modulation Manager
AudioModulation::FAudioModulationManager* ModMgr = 
    UAudioModulationStatics::GetModulation(World);

// 直接操作 Mix
ModMgr->UpdateMix(Stages, *Mix, /*bUpdateObject=*/false, 0.2f);

// 设置全局 Bus Mix（适合始终活跃的 Bus）
ModMgr->SetGlobalBusMixValue(*Bus, 0.7f, 0.1f);

// Solo 一个 Mix（停用其他所有 Mix）
ModMgr->SoloBusMix(*Mix);
```

**创建自定义调制参数类型：**

```cpp
UCLASS(BlueprintType)
class USoundModulationParameterMyCustom : public USoundModulationParameter
{
    GENERATED_BODY()
public:
    virtual bool RequiresUnitConversion() const override { return true; }
    
    virtual Audio::FModulationMixFunction GetMixFunction() const override
    {
        // 自定义混合方式：取最小值
        return [](float A, float B) { return FMath::Min(A, B); };
    }
    
    virtual float GetUnitMin() const override { return -1.0f; }
    virtual float GetUnitMax() const override { return 1.0f; }
};
```

## Demo 示例

### 最小完整示例：LFO 控制音量

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "AudioModulation",
    "Engine",
    "Core"
});
```

**MyAudioModulator.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyAudioModulator.generated.h"

class USoundControlBus;
class USoundControlBusMix;
class USoundModulationGeneratorLFO;
class UAudioModulationDestination;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyAudioModulator : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

private:
    UPROPERTY()
    TObjectPtr<USoundControlBus> VolumeBus;

    UPROPERTY()
    TObjectPtr<USoundControlBusMix> VolumeMix;

    UPROPERTY()
    TObjectPtr<USoundModulationGeneratorLFO> LFOGenerator;

    UPROPERTY()
    TObjectPtr<UAudioModulationDestination> Destination;
};
```

**MyAudioModulator.cpp：**

```cpp
#include "MyAudioModulator.h"
#include "AudioModulationStatics.h"
#include "SoundControlBus.h"
#include "SoundControlBusMix.h"
#include "Generators/SoundModulationLFO.h"
#include "AudioModulationDestination.h"
#include "SoundModulationParameter.h"

void UMyAudioModulator::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建音量参数
    USoundModulationParameter* Param = UAudioModulationStatics::CreateModulationParameter(
        this, TEXT("MasterVolume"), USoundModulationParameterVolume::StaticClass(), 1.0f);

    // 2. 创建 Bus
    VolumeBus = UAudioModulationStatics::CreateBus(
        this, TEXT("MyVolumeBus"), Param, false);

    // 3. 创建 LFO
    FSoundModulationLFOParams LFOParams;
    LFOParams.Shape = ESoundModulationLFOShape::Sine;
    LFOParams.Frequency = 0.5f;
    LFOParams.Amplitude = 0.3f;
    LFOParams.Offset = 0.7f;
    LFOGenerator = UAudioModulationStatics::CreateLFOGenerator(
        this, TEXT("VolumeLFO"), LFOParams);

    // 4. 创建 Mix 并激活
    FSoundControlBusMixStage Stage = UAudioModulationStatics::CreateBusMixStage(
        this, VolumeBus, 1.0f, 0.1f, 0.1f);
    TArray<FSoundControlBusMixStage> Stages = { Stage };
    VolumeMix = UAudioModulationStatics::CreateBusMix(
        this, TEXT("MyVolumeMix"), Stages, true);

    // 5. 创建 Destination 以便追踪值
    Destination = UAudioModulationStatics::CreateModulationDestination(
        this, TEXT("MyDestination"), VolumeBus);
}

void UMyAudioModulator::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 读取当前调制值（归一化 0-1）
    float ModValue = Destination->GetValue();
    UE_LOG(LogTemp, Log, TEXT("Current modulation value: %f"), ModValue);
}
```

## 模块依赖

使用 AudioModulation plugin 时，你的 Build.cs 需要引用以下模块：

| 模块 | 用途 |
|---|---|
| `AudioModulation` | 调制框架核心（Bus、Mix、Parameter、Generator 等） |
| `AudioExtensions` | 音频扩展接口（公共依赖，Audio Modulation 自动带入） |
| `WaveTable` | 波表变换（用于 Patch 中的曲线映射，公共依赖） |
| `Engine` | 引擎核心（隐含依赖） |
| `CoreUObject` | UObject 系统（隐含依赖） |

**插件级依赖**（.uplugin 中声明，自动启用）：

| 插件 | 用途 |
|---|---|
| `MetaSound` | 在 MetaSound 图中集成调制器节点 |
| `WaveTable` | Patch 曲线变换支持 |
| `AudioInsights` | 调试面板（Control Bus Dashboard、Modulation Matrix） |

## 内置调制参数类型

| 类 | 说明 | 混合方式 |
|---|---|---|
| `USoundModulationParameter` | 基类，归一化 [0,1] | 乘法（默认） |
| `USoundModulationParameterScaled` | 线性缩放到 [UnitMin, UnitMax] | 乘法 |
| `USoundModulationParameterVolume` | 对数音量（dB），支持 MinVolume | 乘法 |
| `USoundModulationParameterFrequency` | 对数频率，自定义 min/max | 乘法 |
| `USoundModulationParameterFilterFrequency` | 标准滤波器频率范围 | 乘法 |
| `USoundModulationParameterLPFFrequency` | 低通滤波器频率 | 取最小值（更激进） |
| `USoundModulationParameterHPFFrequency` | 高通滤波器频率 | 取最大值（更激进） |
| `USoundModulationParameterBipolar` | 双极范围 [-Range/2, +Range/2] | 加法 |
| `USoundModulationParameterAdditive` | 自定义范围，加法混合 | 加法 |

## 内置生成器类型

| 类 | 说明 |
|---|---|
| `USoundModulationGeneratorLFO` | 低频振荡器，支持 Sine/Saw/Square/Triangle/Exponential/Random 波形 |
| `USoundModulationGeneratorADEnvelope` | Attack/Decay 包络，支持循环和曲线控制 |
| `USoundModulationGeneratorEnvelopeFollower` | 包络跟随器，跟随指定 AudioBus 的振幅 |

## 维护状态

### 近期更新

- `2b8b371` (2025-09-10) — [Audio Insights] 修复 Control Bus Dashboard 在蓝图创建 Bus 时显示 Level 名称的问题，新增 `ResolveObjectDisplayName` 函数
- `df5f33f` (2025-09-03) — [Audio Insights] 将暂停/恢复 Trace 数据的方法移到基类
- `112064d` (2025-08-21) — [Audio Insights] 修复 Modulation Matrix 在蓝图创建 Mix 时显示 Level 名称的问题

### 维护评价

- **创建时间**：2019-08-23，至今约 7 年
- **最近更新**：2025 年 9 月仍在活跃维护，主要是 Audio Insights 调试面板相关的修复和改进
- **维护状态**：**活跃维护中**。该 plugin 是 UE 音频引擎的核心调制框架，持续收到更新
- **5.6 版本变化**：新增 `CreateModulationDestination` API，旧的 `ActivateBus`/`DeactivateBus`/`ActivateGenerator`/`DeactivateGenerator` 标记为 deprecated（5.6 起），推荐使用 `UAudioModulationDestination` 管理激活状态
- **已知限制**：默认不启用（`EnabledByDefault=false`），需要手动在插件设置中启用
- **推荐程度**：✅ **强烈推荐**。这是 UE 音频系统官方推荐的参数调制方案，替代了旧的 Sound Class 混音方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioModulation)
- [官方文档]()（.uplugin 中未提供 DocsURL）
