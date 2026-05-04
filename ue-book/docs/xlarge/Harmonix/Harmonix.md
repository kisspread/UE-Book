# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MetaSound 节点） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 旗下 Harmonix GenTech 团队（曾开发 Guitar Hero、Rock Band 等音乐游戏的工作室）打造的**音乐驱动音频框架**。它解决的核心问题是：**如何在游戏运行时精确地将音频、视觉和玩家输入同步到音乐节拍上**。

这个插件不仅仅是一个音频播放工具，而是一整套音乐游戏基础设施：

- **音乐时钟系统**：提供多种校准时间基准（音频渲染时间、玩家体验时间、视频渲染时间），让游戏能精确知道"音乐现在在哪里"
- **MIDI 支持**：完整的 MIDI 文件解析和运行时播放能力，用于驱动音乐游戏的谱面数据
- **DSP 处理**：音频信号处理工具集，用于实时音频效果
- **MetaSound 集成**：将 Harmonix 的音乐功能暴露为 MetaSound 节点，可在 MetaSound 编辑器中可视化编排
- **线程安全数据代理**：通过 `TAudioRenderableProxy` 系统实现游戏线程与音频渲染线程之间的无锁数据传递

**为什么需要手动启用？** 因为这是实验性插件（`IsExperimentalVersion=true`），API 可能发生变化，且依赖较重（722 个源文件），不适合所有项目默认加载。

## 子模块总览

| 子模块 | 类型 | 职责 |
|---|---|---|
| **Harmonix** | Runtime | 核心模块：音乐时间基准、延迟校准、开发者设置、线程安全代理基础设施 |
| **HarmonixDsp** | Runtime | DSP 处理：音频信号处理算法和工具 |
| **HarmonixDspEditor** | Runtime | DSP 编辑器支持 |
| **HarmonixDspTests** | Runtime | DSP 模块的自动化测试 |
| **HarmonixEditor** | Runtime | 核心模块的编辑器支持 |
| **HarmonixMetasound** | Runtime | MetaSound 集成：将 Harmonix 功能暴露为 MetaSound 节点 |
| **HarmonixMetasoundEditor** | Runtime | MetaSound 集成的编辑器支持 |
| **HarmonixMetasoundTests** | Runtime | MetaSound 集成的自动化测试 |
| **HarmonixMidi** | Runtime | MIDI 文件解析与运行时播放 |
| **HarmonixMidiEditor** | Runtime | MIDI 资产的编辑器支持 |
| **HarmonixMidiTests** | Runtime | MIDI 模块的自动化测试 |

## 使用场景

- 你在做**音乐节奏游戏**（类似 Guitar Hero、Beat Saber）→ 用 Harmonix 的音乐时钟 + MIDI 系统精确同步谱面与音频
- 你需要**音乐驱动的视觉效果**（节拍同步的灯光、动画、UI）→ 用 `ECalibratedMusicTimebase::VideoRenderTime` 获取校准后的视频渲染时间
- 你需要**精确的玩家输入评分**（判定 Perfect/Great/Miss）→ 用 `ECalibratedMusicTimebase::ExperiencedTime` 获取玩家实际体验到的音频时间
- 你需要在 **MetaSound 图中使用音乐功能** → 用 HarmonixMetasound 提供的节点
- 你需要**运行时解析和播放 MIDI 文件** → 用 HarmonixMidi 模块
- 你需要**实时音频 DSP 处理** → 用 HarmonixDsp 模块

## 蓝图用法

### 核心枚举

`ECalibratedMusicTimebase`（BlueprintType）定义了四种校准音乐时间基准：

| 枚举值 | 说明 |
|---|---|
| `AudioRenderTime` | 平滑后的音频渲染时间，适合基于当前歌曲时间排队音乐事件 |
| `ExperiencedTime` | 玩家实际听到和看到的时间（校准后），适合评分玩家输入 |
| `VideoRenderTime` | 应该绘制视觉效果的时间（校准后），让视觉与音乐同步 |
| `RawAudioRenderTime` | 原始未平滑的音频渲染时间，仅用于调试 |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 设置玩家体验延迟（毫秒），正值表示玩家听到的是过去渲染的音频 | `FHarmonixModule` |
| `GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs` | 获取当前玩家体验延迟 | `FHarmonixModule` |
| `SetMeasuredVideoToAudioRenderOffsetMs` | 设置视频渲染偏移（毫秒），用于同步视觉与音频 | `FHarmonixModule` |
| `GetMeasuredVideoToAudioRenderOffsetMs` | 获取当前视频渲染偏移 | `FHarmonixModule` |

### 使用示例（延迟校准流程）

Harmonix 提供了两种校准方法（详见源码注释）：

**推荐方法（METHOD 2）**：

1. **校准视频偏移**：播放节拍音乐，让玩家在**看到**视觉节拍指示时按键，测量 `SmoothedAudioRenderTime` 与按键时间的差值，设置为视频偏移
2. **校准体验偏移**：播放节拍音乐，让玩家在**听到**节拍时按键，测量渲染时间与按键时间的差值，设置为体验偏移

校准完成后，系统自动提供三种校准时间：
- `ExperiencedTime` = `SmoothedAudioRenderTime` - 体验偏移（用于输入评分）
- `VideoRenderTime` = `SmoothedAudioRenderTime` - 视频偏移（用于视觉同步）
- `AudioRenderTime` = 平滑后的音频渲染时间（用于音频事件排队）

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix.h"
#include "Harmonix/MusicalTimebase.h"
#include "Harmonix/AudioRenderableProxy.h"
```

### 基本用法 — 延迟校准

```cpp
// 设置玩家体验延迟（从校准流程中测得）
// ExperiencedAudioTime = SmoothedMusicRenderMs - 此值
FHarmonixModule::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(120.0f);

// 设置视频渲染偏移（从校准流程中测得）
// AudioTimeToRenderGraphicsFor = SmoothedMusicRenderMs - 此值
FHarmonixModule::SetMeasuredVideoToAudioRenderOffsetMs(45.0f);

// 读取当前值
float ExperienceOffset = FHarmonixModule::GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs();
float VideoOffset = FHarmonixModule::GetMeasuredVideoToAudioRenderOffsetMs();
```

### 进阶用法 — 线程安全音频数据代理

`TAudioRenderableProxy` 是 Harmonix 的核心基础设施，用于在游戏线程和音频渲染线程之间安全地共享数据：

```cpp
#include "Harmonix/AudioRenderableProxy.h"

// 1. 定义你的音频设置结构体
struct FMyAudioSettings
{
    float Volume = 1.0f;
    float Pitch = 1.0f;
    int32 OctaveShift = 0;
    
    // 必须添加此宏，使结构体可被代理
    IMPL_AUDIORENDERABLE_PROXYABLE(FMyAudioSettings)
};

// 2. 声明代理类型
USING_AUDIORENDERABLE_PROXY(FMyAudioSettings, FMyAudioSettingsProxy)

// 3. 在游戏线程创建并更新设置
TSharedPtr<FMyAudioSettingsProxy> Proxy = MakeShared<FMyAudioSettingsProxy>();

// 更新设置（线程安全，通过无锁队列传递）
FMyAudioSettings NewSettings;
NewSettings.Volume = 0.8f;
NewSettings.Pitch = 1.2f;
Proxy->Set(NewSettings);

// 4. 在音频渲染线程读取设置
// 代理会自动检查是否有更新的设置可用
const FMyAudioSettings& CurrentSettings = Proxy->Get();
float CurrentVolume = CurrentSettings.Volume;
```

### 进阶用法 — 属性编辑工具（编辑器）

```cpp
#include "Harmonix/PropertyUtility.h"

// 在 PostEditChangeChainProperty 中追踪属性变更链
void UMyMusicObject::PostEditChangeChainProperty(FPropertyChangedChainEvent& PropertyChangedChainEvent)
{
    Super::PostEditChangeChainProperty(PropertyChangedChainEvent);
    
    // 获取属性变更的完整路径字符串，如 "MyBar.BazArray[3].Number = 6"
    FString PropertyPath = Harmonix::GetStructPropertyChainString(&MySettings, PropertyChangedChainEvent);
    
    // 判断变更类型
    Harmonix::EPostEditAction Action = Harmonix::GetPropertyPostEditAction(
        PropertyChangedChainEvent.Property, 
        PropertyChangedChainEvent.ChangeType
    );
    
    if (Action == Harmonix::EPostEditAction::UpdateNonTrivial)
    {
        // 需要重新初始化的变更
        ReinitializeAudio();
    }
}
```

## Demo 示例

以下示例展示如何创建一个简单的音乐节拍检测器：

```cpp
// BeatSyncComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "Harmonix/MusicalTimebase.h"
#include "BeatSyncComponent.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class UBeatSyncComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UBeatSyncComponent();

    // 当前使用的音乐时间基准
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Beat Sync")
    ECalibratedMusicTimebase Timebase = ECalibratedMusicTimebase::ExperiencedTime;

    // 节拍回调
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnBeat, float, BeatTimestamp);

    UPROPERTY(BlueprintAssignable, Category = "Beat Sync")
    FOnBeat OnBeat;

    // 获取当前校准后的音乐时间（毫秒）
    UFUNCTION(BlueprintCallable, Category = "Beat Sync")
    float GetCurrentMusicTimeMs() const;

    // 设置音频延迟校准值
    UFUNCTION(BlueprintCallable, Category = "Beat Sync")
    void CalibrateAudioLatency(float ExperienceOffsetMs, float VideoOffsetMs);

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, 
                               FActorComponentTickFunction* ThisTickFunction) override;
};
```

```cpp
// BeatSyncComponent.cpp
#include "BeatSyncComponent.h"
#include "Harmonix.h"

UBeatSyncComponent::UBeatSyncComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

float UBeatSyncComponent::GetCurrentMusicTimeMs() const
{
    // 实际实现需要从音乐时钟获取对应时间基准的当前时间
    // 这里展示的是校准偏移的计算逻辑
    float SmoothedRenderTime = 0.0f; // 从音乐时钟获取
    
    switch (Timebase)
    {
    case ECalibratedMusicTimebase::ExperiencedTime:
        return SmoothedRenderTime - FHarmonixModule::GetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs();
    case ECalibratedMusicTimebase::VideoRenderTime:
        return SmoothedRenderTime - FHarmonixModule::GetMeasuredVideoToAudioRenderOffsetMs();
    case ECalibratedMusicTimebase::AudioRenderTime:
    case ECalibratedMusicTimebase::RawAudioRenderTime:
    default:
        return SmoothedRenderTime;
    }
}

void UBeatSyncComponent::CalibrateAudioLatency(float ExperienceOffsetMs, float VideoOffsetMs)
{
    FHarmonixModule::SetMeasuredUserExperienceAndReactionToAudioRenderOffsetMs(ExperienceOffsetMs);
    FHarmonixModule::SetMeasuredVideoToAudioRenderOffsetMs(VideoOffsetMs);
}

void UBeatSyncComponent::TickComponent(float DeltaTime, ELevelTick TickType,
                                        FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
    // 实际的节拍检测逻辑在此实现
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetasoundEngine` | MetaSound 运行时引擎，HarmonixMetasound 模块依赖 |
| `MetasoundFrontend` | MetaSound 前端框架，用于注册自定义节点 |
| `AssetRegistry` | 资产注册表，用于资产发现和引用 |
| `HarmonixDsp` | DSP 处理模块，被 HarmonixMetasound 依赖 |
| `HarmonixMidi` | MIDI 处理模块，被 HarmonixMetasound 依赖 |

> **注意**：`HarmonixDsp`、`HarmonixMetasound`、`HarmonixMidi` 三个运行时模块均依赖 `AssetRegistry` 和 `UnrealEd`，这在 Runtime 模块中较为少见，可能用于编辑器内的资产烘焙或预处理流程。

## 维护状态

### 近期更新

```
- f50c5f2de17b Migrate MusicClockDriver members tied to specific timebases into arrays indexed by ECalibratedMusicTimebase
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files
- 939cc6e51c10 Used FortniteClient build target to find and convert all files to have dllstorage on methods/staticvar instead of on types
```

### 维护评价

- **创建时间**：2024 年 1 月，约 2 年历史，相对较新的插件
- **活跃度**：近期有实质性架构更新（MusicClockDriver 重构为按时间基准索引的数组），说明仍在积极开发
- **实验性状态**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，API 可能发生变化
- **代码规模**：722 个源文件，11 个模块，是一个大型、功能完整的框架
- **团队背景**：由 Harmonix GenTech 团队开发，有丰富的音乐游戏开发经验
- **已知限制**：实验性插件，不建议在生产环境中直接使用；部分 Runtime 模块依赖 UnrealEd，可能影响打包

**推荐程度**：如果你正在开发音乐节奏类游戏或需要精确音乐同步的项目，这是目前 UE5 中最专业的解决方案。但由于实验性状态，建议密切关注 API 变化，并做好适配准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [Harmonix 核心模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/Harmonix)
- [HarmonixDsp 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDsp)
- [HarmonixMetasound 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasound)
- [HarmonixMidi 模块](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidi)
- [HarmonixDspTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [HarmonixMetasoundTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)
- [HarmonixMidiTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)