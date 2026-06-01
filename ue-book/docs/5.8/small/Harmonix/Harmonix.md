# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 旗下 Harmonix GenTech 团队（曾开发 Guitar Hero、Rock Band 等知名音乐游戏）打造的**专业级音乐音频框架**。它解决的核心问题是：在 UE5 中实现**帧精确级的音频-视频-输入三路同步**。

这个插件之所以存在，是因为 UE5 内置的音频系统无法满足音乐游戏/节奏游戏的严苛需求：
- **音频渲染线程与游戏线程的数据隔离**：提供了无锁、线程安全的跨线程数据传递机制（`TAudioRenderableProxy`），避免了传统锁带来的音频卡顿
- **多时间基准校准**：音频渲染时间、玩家感知时间、视频渲染时间三者存在固有延迟差，需要精确校准才能让"看到的"和"听到的"完全同步
- **MetaSound 深度集成**：将音乐相关的 DSP、MIDI 功能以 MetaSound 节点形式暴露，可在 MetaSound 图中直接构建音乐逻辑
- **MIDI 支持**：完整的 MIDI 文件解析与回放能力，适用于需要 MIDI 驱动的游戏玩法

## 使用场景

- 你在做**节奏/音乐游戏**（如 Rock Band、Guitar Hero 风格）→ 需要 Harmonix 的校准系统和多时间基准
- 你需要在 MetaSound 图中处理 **MIDI 事件驱动的音频** → 用 HarmonixMetasound + HarmonixMidi
- 你需要自定义 **DSP 效果器**并集成到 MetaSound → 用 HarmonixDsp
- 你需要在**音频渲染线程和游戏线程之间安全地共享参数**（如音量、滤波器频率等）→ 用 `TAudioRenderableProxy` 系统
- 你需要将**音乐节拍信息同步到视觉动画/UI** → 用 `ECalibratedMusicTimebase::VideoRenderTime`

## 蓝图用法

Harmonix 核心模块的蓝图 API 集中在音频校准功能上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 设置玩家体验-音频渲染的延迟偏移（毫秒） | `UHarmonixBlueprintUtil` |
| `GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 获取玩家体验-音频渲染的延迟偏移 | `UHarmonixBlueprintUtil` |
| `SetMeasuredVideoToAudioRenderOffsetMs` | 设置视频渲染-音频渲染的延迟偏移（毫秒） | `UHarmonixBlueprintUtil` |
| `GetMeasuredVideoToAudioRenderOffsetMs` | 获取视频渲染-音频渲染的延迟偏移 | `UHarmonixBlueprintUtil` |

### 使用示例（蓝图描述）

**音频校准流程**：
1. 在游戏启动或校准界面中，调用 `SetMeasuredVideoToAudioRenderOffsetMs` 设置视频与音频之间的已测量偏移
2. 调用 `SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` 设置玩家从看到画面到做出反应的延迟
3. 在游戏中需要获取当前音乐时间时，查询对应的时间基准（音频渲染时间 / 玩家感知时间 / 视频渲染时间）来决定评分窗口或动画同步点

**时间基准枚举 `ECalibratedMusicTimebase`**（在 C++ 中使用，影响时间查询行为）：
- `AudioRenderTime` — 平滑后的音频渲染位置，用于排队音乐事件
- `ExperiencedTime` — 玩家实际感知的时间，用于**评分玩家输入**
- `VideoRenderTime` — 应该绘制视觉内容的时间，用于**同步动画和 UI**
- `RawAudioRenderTime` — 原始未平滑的音频位置，仅用于调试

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix.h"
#include "Harmonix/AudioRenderableProxy.h"
#include "Harmonix/MusicalTimebase.h"
#include "Harmonix/PropertyUtility.h"
#include "Harmonix/LocalMinimumMagnitudeTracker.h"
```

### 基本用法 — 音频校准

```cpp
#include "Harmonix.h"

// 设置音频校准偏移值（通常在游戏启动时或校准UI完成后调用）
void UMyGameInstance::ApplyCalibration()
{
    // 设置视频到音频的渲染偏移（毫秒）
    // 正值表示视频比音频慢，负值表示视频比音频快
    UHarmonixBlueprintUtil::SetMeasuredVideoToAudioRenderOffsetMs(45.0f);
    
    // 设置玩家体验/反应到音频的偏移
    // 用于评分玩家输入的时机
    UHarmonixBlueprintUtil::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(80.0f);
}

// 读取当前校准值
void UMyGameInstance::LogCalibration()
{
    float VideoOffset = UHarmonixBlueprintUtil::GetMeasuredVideoToAudioRenderOffsetMs();
    float InputOffset = UHarmonixBlueprintUtil::GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs();
    
    UE_LOG(LogTemp, Log, TEXT("Video Offset: %.2f ms, Input Offset: %.2f ms"), VideoOffset, InputOffset);
}
```

### 基本用法 — AudioRenderableProxy 线程安全数据共享

```cpp
#include "Harmonix/AudioRenderableProxy.h"

// 1. 定义你的音频参数结构体
struct FMySynthSettings
{
    float Frequency = 440.0f;
    float Volume = 1.0f;
    float FilterCutoff = 1000.0f;
    
    // 必须：声明代理类型名
    IMPL_AUDIORENDERABLE_PROXYABLE(FMySynthSettings)
};

// 2. 声明代理类型
USING_AUDIORENDERABLE_PROXY(FMySynthSettings, FMySynthSettingsProxy);

// 3. 在你的 UObject 或 MetaSound 数据持有者中使用设置队列
class UMySynthPreset : public UObject
{
    Harmonix::TGameThreadToAudioRenderThreadSettingQueue<FMySynthSettings> SettingsQueue;
    
public:
    UMySynthPreset()
        : SettingsQueue(FMySynthSettings{440.0f, 1.0f, 1000.0f})
    {}
    
    // 从游戏线程更新设置（线程安全）
    void UpdateSettings(float NewFrequency, float NewVolume)
    {
        FMySynthSettings NewSettings;
        NewSettings.Frequency = NewFrequency;
        NewSettings.Volume = NewVolume;
        NewSettings.FilterCutoff = 1000.0f;
        SettingsQueue.SetNewSettings(NewSettings);
    }
    
    // 获取代理数据（传递给 MetaSound 节点）
    std::unique_ptr<FMySynthSettingsProxy> CreateProxy()
    {
        auto Proxy = std::make_unique<FMySynthSettingsProxy>();
        Proxy->Init(SettingsQueue);
        return Proxy;
    }
};
```

### 进阶用法 — PropertyUtility 结构体属性追踪

```cpp
#include "Harmonix/PropertyUtility.h"

// 场景：在编辑器中追踪嵌套结构体属性的变化
UCLASS()
class UMyAudioConfig : public UObject
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere)
    FMySynthSettings SynthSettings;

    virtual void PostEditChangeChainProperty(FPropertyChangedChainEvent& PropertyChangedChainEvent) override
    {
        Super::PostEditChangeChainProperty(PropertyChangedChainEvent);
        
        // 获取属性变化的完整路径字符串
        // 例如 "SynthSettings.Frequency = 880.0"
        FString PropertyPath = Harmonix::GetStructPropertyChainString(&SynthSettings, PropertyChangedChainEvent);
        UE_LOG(LogTemp, Log, TEXT("Changed: %s"), *PropertyPath);
        
        // 判断变化类型
        Harmonix::EPostEditAction Action = Harmonix::GetPropertyPostEditAction(
            PropertyChangedChainEvent.Property, 
            PropertyChangedChainEvent.ChangeType);
        
        switch (Action)
        {
        case Harmonix::EPostEditAction::UpdateTrivial:
            // 仅 UI 刷新，无需重新初始化音频
            break;
        case Harmonix::EPostEditAction::UpdateNonTrivial:
            // 需要重新初始化音频引擎
            ReinitializeAudio();
            break;
        }
    }
    
    // 将修改同步到代理副本
    UPROPERTY()
    FMySynthSettings SynthSettingsProxy;
    
    void SyncProxyProperty(const FPropertyChangedChainEvent& Event)
    {
        // 只拷贝被修改的那个属性，避免整个结构体重拷贝
        Harmonix::CopyStructProperty(&SynthSettingsProxy, &SynthSettings, Event);
    }
    
    // 或者拷贝整个结构体
    void FullSync()
    {
        Harmonix::CopyStructProperties(&SynthSettingsProxy, &SynthSettings);
    }
    
    // 调试用：递归打印所有属性值
    void DebugLog()
    {
        Harmonix::LogStructProperties(&SynthSettings);
    }
};
```

### 进阶用法 — LocalMinimumMagnitudeTracker 音频分析

```cpp
#include "Harmonix/LocalMinimumMagnitudeTracker.h"

// 用于音频信号的局部最小值检测（如节拍检测、音量包络分析）
class FMyBeatDetector
{
    // 环形缓冲区大小为 1024 个采样点
    Harmonix::FLocalMinimumMagnitudeTracker<float, 1024> MagnitudeTracker;
    
public:
    void ProcessAudioBuffer(const float* Samples, int32 NumSamples)
    {
        for (int32 i = 0; i < NumSamples; ++i)
        {
            MagnitudeTracker.Push(FMath::Abs(Samples[i]));
        }
        
        // 获取滑动窗口内的最小幅度
        float MinMagnitude = MagnitudeTracker.Min();
        
        // 获取滑动窗口内的平均幅度
        float AvgMagnitude = MagnitudeTracker.Average();
        
        // 可用于检测"静音"段或节拍间的谷值
    }
    
    void Reset()
    {
        MagnitudeTracker.Reset();
    }
};
```

### 进阶用法 — 多时间基准查询

```cpp
#include "Harmonix/MusicalTimebase.h"

// 根据不同需求查询不同的音乐时间
void UMyMusicGameMode::OnTick(float DeltaTime)
{
    // 获取当前音频渲染时间（平滑后的，用于排队事件）
    float AudioTime = GetMusicTimeForTimebase(ECalibratedMusicTimebase::AudioRenderTime);
    
    // 获取玩家实际感知的时间（用于评分输入时机）
    float ExperiencedTime = GetMusicTimeForTimebase(ECalibratedMusicTimebase::ExperiencedTime);
    
    // 获取应该用于绘制视觉的时间（用于动画同步）
    float VideoTime = GetMusicTimeForTimebase(ECalibratedMusicTimebase::VideoRenderTime);
    
    // 评分逻辑：比较玩家输入时间和 ExperiencedTime
    ScorePlayerInput(PlayerInputTimestamp, ExperiencedTime);
    
    // 视觉同步：在 VideoTime 时更新动画
    UpdateVisualsAtTime(VideoTime);
}
```

## Demo 示例

一个最小可编译示例：创建一个使用 Harmonix 校准系统和线程安全参数队列的合成器预设。

```cpp
// MyHarmonixSynthPreset.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "Harmonix/AudioRenderableProxy.h"
#include "MyHarmonixSynthPreset.generated.h"

// 定义合成器参数
struct FHarmonixSynthParams
{
    float Frequency = 440.0f;
    float Gain = 0.8f;
    float FilterResonance = 0.5f;
    
    IMPL_AUDIORENDERABLE_PROXYABLE(FHarmonixSynthParams)
};

// 声明代理
USING_AUDIORENDERABLE_PROXY(FHarmonixSynthParams, FHarmonixSynthParamsProxy);

UCLASS(BlueprintType)
class UMyHarmonixSynthPreset : public UObject
{
    GENERATED_BODY()

public:
    UMyHarmonixSynthPreset();
    
    UFUNCTION(BlueprintCallable, Category = "MySynth")
    void SetFrequency(float InFrequency);
    
    UFUNCTION(BlueprintCallable, Category = "MySynth")
    void SetGain(float InGain);
    
    UFUNCTION(BlueprintCallable, Category = "MySynth")
    float GetFrequency() const;

    // 创建音频代理供 MetaSound 节点使用
    std::unique_ptr<FHarmonixSynthParamsProxy> CreateAudioProxy();

private:
    Harmonix::TGameThreadToAudioRenderThreadSettingQueue<FHarmonixSynthParams> SettingsQueue;
};
```

```cpp
// MyHarmonixSynthPreset.cpp
#include "MyHarmonixSynthPreset.h"
#include "Harmonix.h"

UMyHarmonixSynthPreset::UMyHarmonixSynthPreset()
    : SettingsQueue(FHarmonixSynthParams{440.0f, 0.8f, 0.5f})
{
}

void UMyHarmonixSynthPreset::SetFrequency(float InFrequency)
{
    FHarmonixSynthParams Current = *(FHarmonixSynthParams*)SettingsQueue;
    Current.Frequency = FMath::Clamp(InFrequency, 20.0f, 20000.0f);
    SettingsQueue.SetNewSettings(Current);
}

void UMyHarmonixSynthPreset::SetGain(float InGain)
{
    FHarmonixSynthParams Current = *(FHarmonixSynthParams*)SettingsQueue;
    Current.Gain = FMath::Clamp(InGain, 0.0f, 1.0f);
    SettingsQueue.SetNewSettings(Current);
}

float UMyHarmonixSynthPreset::GetFrequency() const
{
    return ((const FHarmonixSynthParams*)SettingsQueue)->Frequency;
}

std::unique_ptr<FHarmonixSynthParamsProxy> UMyHarmonixSynthPreset::CreateAudioProxy()
{
    auto Proxy = std::make_unique<FHarmonixSynthParamsProxy>();
    Proxy->Init(SettingsQueue);
    return Proxy;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `AssetRegistry` | 资产注册与发现（HarmonixDsp/HarmonixMetasound/HarmonixMidi 使用） |
| `UnrealEd` | 编辑器扩展支持（HarmonixDsp/HarmonixMetasound/HarmonixMidi 使用） |

注：模块间存在内部依赖关系。其中 `HarmonixDspEditor`、`HarmonixMetasoundEditor`、`HarmonixMidiEditor` 及对应的 Tests 模块属于开发/测试用途，运行时模块的直接使用依赖较少的外部模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音色 KeyZone 排序问题并增加空值防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的截断警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ | 为 FusionPatch 代理添加用户对象以支持活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护**。Harmonix 自 2024 年 1 月引入引擎后持续获得密集更新（最近一次更新距今不到一个月），且更新内容涵盖核心音频逻辑修复（Fusion 音色系统）、API 适配（FSoundWaveData 废弃迁移）、代码质量改进（浮点精度、格式说明符）等多个维度。

需要注意的是：
- **实验性状态**：`IsExperimentalVersion=true`，API 可能在未来版本中发生变化
- **默认未启用**：`EnabledByDefault=false`，需要在项目设置中手动启用
- **规模化大型插件**：521 个源文件、11 个模块，学习曲线较陡
- **核心为 MetaSound 集成**：大量功能通过 MetaSound 节点暴露，需要对 MetaSound 有一定了解

**推荐使用**：如果你在开发音乐/节奏类游戏，这是目前 UE5 中最专业的解决方案。建议从 `HarmonixMidi` 和 `HarmonixMetasound` 模块开始探索。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档（暂无）