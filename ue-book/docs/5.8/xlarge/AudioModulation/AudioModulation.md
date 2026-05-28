# Audio Modulation

> Default implementation of Audio Modulation in the Unreal Audio Engine.

| 属性 | 值 |
|---|---|
| 中文名 | 音频调制 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频参数资产、调制预设） |
| 模块 | `AudioModulation` (Runtime), `AudioModulationEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2019-08-23 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation) | |

## 用途

Audio Modulation 插件提供了一套完整的音频参数动态调制系统，是 Unreal 音频引擎的默认调制实现。它解决的核心问题是：**在运行时通过各种信号源（LFO、包络跟随器、AD 包络等）动态控制音频参数（音量、滤波频率、声像等）**。

该插件引入了几个关键概念：
- **Control Bus（控制总线）**：承载一个调制参数值的容器，可以被生成器（Generator）驱动
- **Control Bus Mix（控制总线混音）**：一组总线阶段（Stage）的集合，可以同时控制多个总线的值，并支持 Attack/Release 渐变
- **Modulation Patch（调制补丁）**：将多个总线输入通过变换曲线组合为一个输出值
- **Modulation Parameter（调制参数）**：定义输出值的单位和范围（如音量 dB、频率 Hz、双极值等）
- **Modulation Generator（调制生成器）**：算法化的信号源（LFO、包络跟随器、AD 包络）
- **Modulation Destination（调制目标）**：监控和追踪调制器值的观察对象

该插件与 MetaSound 和 Sequencer 深度集成，是构建复杂音频交互（如距离衰减、环境音动态变化、音乐层叠混合）的基础架构。

**重要提示**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你需要基于距离、速度等游戏参数动态控制声音音量 → 使用 Control Bus + Control Bus Mix
- 你需要让声音产生周期性的颤音、震音效果 → 使用 LFO Generator 驱动 Control Bus
- 你需要音频跟随另一个声音的振幅来调制滤波器 → 使用 Envelope Follower Generator
- 你需要在一个 Sequencer 时间线上精确控制音频混合参数 → 使用 Sequencer Audio Control Bus Track
- 你需要快速迭代调试不同混音配置（如不同关卡的音乐层音量平衡）→ 使用 Mix Profile 序列化/反序列化功能
- 你需要在 MetaSound 图中使用调制器 → 使用 MetaSound 集成的 FSoundModulatorAsset

## 蓝图用法

所有蓝图节点集中在 `UAudioModulationStatics` 蓝图函数库中。

### 创建与管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Control Bus` | 创建一个调制控制总线，指定参数和默认值 | `UAudioModulationStatics` |
| `Create Control Bus Mix` | 创建一个控制总线混音，指定多个阶段、激活状态和持续时间 | `UAudioModulationStatics` |
| `Create Control Bus Mix Stage` | 创建一个混音阶段，指定目标总线、值和 Attack/Release 时间 | `UAudioModulationStatics` |
| `Create Bus Mix From Value` | 从一组总线和统一值快速创建混音 | `UAudioModulationStatics` |
| `Create Modulation Parameter` | 创建指定类的调制参数（音量、频率等） | `UAudioModulationStatics` |
| `Create Modulation Destination` | 创建调制监控目标，激活并追踪指定调制器的值 | `UAudioModulationStatics` |

### 生成器创建

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create LFO Generator` | 创建低频振荡器生成器（支持正弦、锯齿、方波、三角、指数、随机采样保持） | `UAudioModulationStatics` |
| `Create Envelope Follower Generator` | 创建包络跟随器生成器，跟随指定 AudioBus 的振幅 | `UAudioModulationStatics` |
| `Create AD Envelope Generator` | 创建 Attack/Decay 包络生成器 | `UAudioModulationStatics` |

### 混音控制

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Activate Control Bus Mix` | 激活指定的控制总线混音 | `UAudioModulationStatics` |
| `Deactivate Control Bus Mix` | 停用指定的控制总线混音 | `UAudioModulationStatics` |
| `Deactivate All Control Bus Mixes` | 停用所有激活的控制总线混音 | `UAudioModulationStatics` |
| `Set Control Bus Mix` | 设置混音阶段数据（不修改 UObject 定义） | `UAudioModulationStatics` |
| `Set Control Bus Mix By Filter` | 通过地址/参数类/参数对象过滤器设置混音阶段 | `UAudioModulationStatics` |
| `Solo Mix` | 独奏此混音（停用其他所有混音） | `UAudioModulationStatics` |
| `Is Control Bus Mix Active` | 查询混音是否处于激活状态 | `UAudioModulationStatics` |

### 全局总线值管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Global Control Bus Mix Value` | 为指定总线设置全局混音值（适合始终激活的总线） | `UAudioModulationStatics` |
| `Clear Global Control Bus Mix Value` | 清除指定总线的全局混音值，渐变回到参数默认值 | `UAudioModulationStatics` |
| `Clear All Global Control Bus Mix Values` | 清除所有全局混音值 | `UAudioModulationStatics` |

### 查询与序列化

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Modulator Value` | 获取调制器当前归一化值（未激活时返回 1.0） | `UAudioModulationStatics` |
| `Get Modulators From Destination` | 获取调制目标上应用的调制器集合 | `UAudioModulationStatics` |
| `Save Control Bus Mix to Profile` | 将混音序列化到 .ini 配置文件（用于迭代开发） | `UAudioModulationStatics` |
| `Load Control Bus Mix from Profile` | 从 .ini 配置文件反序列化混音 | `UAudioModulationStatics` |
| `Update Control Bus Mix` | 将 UObject 定义的修改提交到运行时实例 | `UAudioModulationStatics` |
| `Update Modulator` | 将调制器 UObject 定义的修改提交到音频线程 | `UAudioModulationStatics` |

### 使用示例（蓝图描述）

**场景1：距离驱动的音量衰减**

1. 创建一个 `SoundControlBus` 资产，参数选择 `SoundModulationParameterVolume`
2. 创建一个 `SoundModulationPatch`，将总线作为输入，通过距离映射曲线（Transform）变换值
3. 在声音资产的 Modulation 设置中，将音量目标指向此 Patch
4. 运行时通过 `Set Control Bus Mix` 或 `Set Global Control Bus Mix Value` 动态调整

**场景2：LFO 驱动的颤音效果**

1. 创建一个 `SoundModulationGeneratorLFO`，设置 Shape = Sine，Frequency = 5.0，Amplitude = 0.3
2. 创建一个 `SoundControlBus`，将 LFO 添加到 Generators 数组
3. 创建 `Create Modulation Destination` 节点引用该总线，在蓝图中用 `Get Watched Modulator Value` 获取值
4. 将该总线应用到声音的音高调制目标

**场景3：Sequencer 音乐层叠混合**

1. 创建多个 `SoundControlBus`（分别对应音乐层：主旋律、打击乐、氛围）
2. 创建对应的 `SoundControlBusMix`，每个 Mix 包含不同层的 Stage
3. 在 Sequencer 中添加 `AudioControlBusMixTrack`，通过关键帧在不同时间点激活/停用不同混音
4. 利用 Attack/Release 时间实现平滑过渡

## C++ 用法

### 头文件引入

```cpp
// 核心调制系统
#include "AudioModulation.h"

// 蓝图静态函数库
#include "AudioModulationStatics.h"

// 控制总线
#include "SoundControlBus.h"

// 控制总线混音
#include "SoundControlBusMix.h"

// 调制参数
#include "SoundModulationParameter.h"

// 调制补丁
#include "SoundModulationPatch.h"

// 调制生成器
#include "Generators/SoundModulationLFO.h"
#include "Generators/SoundModulationEnvelopeFollower.h"
#include "Generators/SoundModulationADEnvelope.h"

// 调制目标
#include "AudioModulationDestination.h"
```

### 基本用法

```cpp
// 来源: Public/AudioModulationStatics.h

// 获取当前世界的调制管理器
UWorld* World = GetWorld();
AudioModulation::FAudioModulationManager* ModManager = AudioModulation::FAudioModulationManager::GetModulation(World);

// 创建一个控制总线
USoundControlBus* Bus = UAudioModulationStatics::CreateBus(
    this, 
    FName("MyBus"), 
    VolumeParameter,  // USoundModulationParameter*
    true              // Activate
);

// 创建混音阶段
FSoundControlBusMixStage Stage = UAudioModulationStatics::CreateBusMixStage(
    this,
    Bus,           // USoundControlBus*
    0.5f,          // TargetValue
    0.2f,          // AttackTime
    0.2f           // ReleaseTime
);

// 创建控制总线混音
TArray<FSoundControlBusMixStage> Stages;
Stages.Add(Stage);
USoundControlBusMix* Mix = UAudioModulationStatics::CreateBusMix(
    this,
    FName("MyMix"),
    Stages,
    true,          // Activate
    -1.0,          // Duration (negative = infinite)
    false          // bRetriggerOnActivation
);
```

### 进阶用法

```cpp
// 来源: Public/AudioModulationStatics.h + Private/AudioModulationSystem.h

// 创建调制监控目标
UAudioModulationDestination* Dest = UAudioModulationStatics::CreateModulationDestination(
    this, FName("MyDest"), SomeModulator);

// 获取调制器当前值
float Value = UAudioModulationStatics::GetModulatorValue(this, SomeModulator);

// 通过过滤器批量更新混音阶段
UAudioModulationStatics::UpdateMixByFilter(
    this,
    Mix,
    FString("Music"),                          // AddressFilter
    USoundModulationParameterVolume::StaticClass(),  // ParamClassFilter
    nullptr,                                    // ParamFilter
    0.7f,                                       // Value
    0.5f                                        // FadeTime
);

// 设置全局总线值（适合始终激活的总线，如主音量）
UAudioModulationStatics::SetGlobalBusMixValue(this, MasterBus, 0.8f, 0.3f);

// 保存/加载混音 Profile（用于迭代开发）
UAudioModulationStatics::SaveMixToProfile(this, Mix, 0);       // 保存到 Profile 0
TArray<FSoundControlBusMixStage> LoadedStages = 
    UAudioModulationStatics::LoadMixFromProfile(this, Mix, true, 0);

// 在音频线程安全地获取调制器值（从非音频线程）
float ThreadSafeValue = 1.0f;
bool bSuccess = ModSystem->GetModulatorValueThreadSafe(ModulatorHandle, ThreadSafeValue);

// 创建带参数的调制器并提交 UObject 修改到运行时
UAudioModulationStatics::UpdateModulator(this, SomeModulator);
```

## Demo 示例

```cpp
// ModulationDemoComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SoundControlBus.h"
#include "SoundControlBusMix.h"
#include "AudioModulationDestination.h"
#include "ModulationDemoComponent.generated.h"

class USoundModulationParameterVolume;
class USoundModulationGeneratorLFO;

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYGAME_API UModulationDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable)
    void SetMusicLayerVolume(float InVolume, float FadeTime);

    UFUNCTION(BlueprintPure)
    float GetLFOValue() const;

private:
    UPROPERTY()
    TObjectPtr<USoundControlBus> MusicBus;

    UPROPERTY()
    TObjectPtr<USoundControlBusMix> MusicMix;

    UPROPERTY()
    TObjectPtr<USoundModulationGeneratorLFO> LFOGenerator;

    UPROPERTY()
    TObjectPtr<UAudioModulationDestination> LFOWatcher;
};

// ModulationDemoComponent.cpp
#include "ModulationDemoComponent.h"
#include "AudioModulationStatics.h"
#include "SoundModulationParameter.h"
#include "Generators/SoundModulationLFO.h"

void UModulationDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建一个 LFO 生成器
    FSoundModulationLFOParams LFOParams;
    LFOParams.Shape = ESoundModulationLFOShape::Sine;
    LFOParams.Frequency = 2.0f;
    LFOParams.Amplitude = 0.5f;
    LFOParams.Offset = 0.5f;
    LFOGenerator = UAudioModulationStatics::CreateLFOGenerator(
        this, FName("DemoLFO"), LFOParams);

    // 创建音乐层控制总线
    MusicBus = UAudioModulationStatics::CreateBus(
        this, FName("MusicLayerBus"),
        nullptr, true);

    // 创建初始混音
    FSoundControlBusMixStage Stage = UAudioModulationStatics::CreateBusMixStage(
        this, MusicBus, 1.0f, 0.5f, 0.5f);

    TArray<FSoundControlBusMixStage> Stages = {Stage};
    MusicMix = UAudioModulationStatics::CreateBusMix(
        this, FName("MusicMix"), Stages, true);

    // 创建 LFO 监控目标
    LFOWatcher = UAudioModulationStatics::CreateModulationDestination(
        this, FName("LFOTracker"), LFOGenerator);
}

void UModulationDemoComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MusicMix)
    {
        UAudioModulationStatics::DeactivateBusMix(this, MusicMix);
    }
    Super::EndPlay(EndPlayReason);
}

void UModulationDemoComponent::SetMusicLayerVolume(float InVolume, float FadeTime)
{
    UAudioModulationStatics::SetGlobalBusMixValue(
        this, MusicBus, InVolume, FadeTime);
}

float UModulationDemoComponent::GetLFOValue() const
{
    if (LFOWatcher)
    {
        return LFOWatcher->GetValue();
    }
    return 0.0f;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaSound` | MetaSound 图中调制器节点支持（FSoundModulatorAsset 等） |
| `WaveTable` | 调制变换曲线（FSoundModulationTransform 继承自 FWaveTableTransform） |
| `MovieScene` | Sequencer 音频控制总线/混音轨道集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a438ef2` | Provide ownership mechanism to SoundControlBusMixes from CreateBusMixFromValue | 为 CreateBusMixFromValue 提供所有权机制，防止混音被意外回收 |
| 2026-05-13 | `8e94bfe` | [Audio Modulation] [AudioModulationInsights] Added modulator activated/deactivated trace events | 添加调制器激活/停用的 Trace 事件，用于 Insights 分析 |
| 2026-04-28 | `784b2c1` | [Sequencer] - Fix for control bus track crashing when there is no parameter | 修复 Sequencer 控制总线轨道在无参数时的崩溃 |
| 2026-04-16 | `cb44584` | MetaSound: Consolidate pin type registration and associated pin-related MetaSound Editor behavior | 整合 MetaSound 引脚类型注册和编辑器行为 |
| 2026-04-15 | `2010cdb` | [Backout] - CL52717658 - CIS Compile Error | 回滚导致编译错误的改动 |

### 维护评价

**活跃维护中**。Audio Modulation 插件仍在被 Epic Games 积极维护和改进，最近几个月有多次实质性更新，包括：
- 新增 Trace 事件用于 Audio Insights 分析
- 改进内存所有权管理
- 持续修复 Sequencer 集成问题
- 与 MetaSound 的持续整合

该插件自 2019 年创建以来已经历了多次重大重构（如 5.4 版本中弃用了旧的激活/停用方式，引入 `UAudioModulationDestination` 作为新的调制器状态管理方式）。从代码中可以看到多处 `UE_DEPRECATED(5.4, ...)` 和 `UE_DEPRECATED(5.6, ...)` 标记，表明 API 在持续演进。

**需要注意**：
- `EnabledByDefault: false` — 必须在项目设置中手动启用
- 多个旧 API 已标记为弃用（`ActivateBus`、`DeactivateBus`、`ActivateGenerator`、`DeactivateGenerator`），应使用 `CreateModulationDestination` 替代
- 依赖 MetaSound 和 WaveTable 插件

**推荐使用**：✅ 推荐。这是 Unreal 音频引擎的官方调制系统，是构建复杂音频交互的标准方案。活跃维护，API 持续改进。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulation)
- 官方文档（无）
- [Audio Modulation Insights 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioModulationInsights)（配套的音频调制分析工具）