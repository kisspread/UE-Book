# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐时钟系统 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点、MIDI 步进序列资产、MIDI 哑音序列资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是 Epic Games 与 Harmonix 合作开发的**音乐时间同步系统**。它解决的核心问题是：**如何让游戏逻辑精确地与音乐节拍、小节、段落保持同步**。

传统做法是用 `GetAudioPlaybackPercent` 或手写计时器，但这些方法无法处理：
- 变速播放、变速率音频
- 音频线程与游戏线程之间的延迟差异
- 多种校准时间基准（音频渲染时间、视频渲染时间、玩家感知时间）
- 音乐中的 loop 区域、seek 操作产生的时间跳变

Harmonix 通过 **MusicClock（音乐时钟）** 概念，将 MIDI 时钟数据从音频线程平滑采样到游戏线程，为游戏提供统一的"音乐时间"。它与 **MetaSound** 深度集成——MetaSound 节点图中的 MIDI 时钟输出会被自动检测、平滑处理，然后通过 `UMusicClockComponent` 暴露给蓝图和 C++。

插件的 EnabledByDefault=false 且 IsExperimentalVersion=true，说明这是 UE 5.4 新引入的实验性功能（从 Harmonix 的独立仓库迁移至引擎）。

## 使用场景

- **节奏游戏**（如 Festival / Fortnite Festival）—— 需要精确到采样的音乐时间，用于判定音符命中
- **音频可视化 / 音频响应式材质** —— 将节拍进度、BPM 写入 Material Parameter Collection，驱动 shader 动画
- **程序化音乐** —— 用 MetaSound 的 MIDI 时钟节点生成或处理 MIDI 序列，实现动态音乐
- **游戏事件触发** —— 在特定节拍或小节触发游戏事件（如敌人攻击波次、环境灯光变化）
- **视频/动画同步** —— 通过校准时间偏移，让视频渲染和音频渲染精确对齐
- **步进音序器** —— 用 `UMidiStepSequence` 创建鼓机风格的 MIDI 图案

## 蓝图用法

### 核心节点

#### 音乐时钟（MusicClockComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMetasoundDrivenMusicClock` | 从 AudioComponent 创建 MetaSound 驱动的时钟 | `UMusicClockComponent` |
| `CreateWallClockDrivenMusicClock` | 从 MIDI 文件创建墙钟驱动的时钟 | `UMusicClockComponent` |
| `Start` / `Stop` / `Pause` / `Continue` | 控制时钟播放状态 | `UMusicClockComponent` |
| `GetState` | 获取时钟状态（Stopped / Paused / Running） | `UMusicClockComponent` |
| `GetCurrentTimestamp` | 获取当前音乐时间戳（小节 + 节拍） | `UMusicClockComponent` |
| `GetCurrentTempo` | 获取当前 MIDI 四分音符 BPM | `UMusicClockComponent` |
| `GetCurrentBeatsPerMinute` | 获取当前真实节拍 BPM（考虑拍号） | `UMusicClockComponent` |
| `GetCurrentTimeSignature` | 获取当前拍号（分子/分母） | `UMusicClockComponent` |
| `GetDistanceToNextBeat` | 距离下一个节拍的进度 [0, 1) | `UMusicClockComponent` |
| `GetDistanceToClosestBar` | 距离最近小节线的进度 | `UMusicClockComponent` |
| `GetCurrentSectionName` | 获取当前段落名称（如 intro、chorus） | `UMusicClockComponent` |
| `GetSecondsIncludingCountIn` | 从音乐开头计起的秒数（含弱起拍） | `UMusicClockComponent` |
| `GetSecondsFromBarOne` | 从 Bar 1 Beat 1 计起的秒数 | `UMusicClockComponent` |
| `SeekedThisFrame` / `LoopedThisFrame` | 检测本帧是否发生 seek / loop | `UMusicClockComponent` |
| `BP_AddTimer` | 添加基于音乐时间的定时器 | `UMusicClockComponent` |
| `Quantize` | 将时间戳量化到最近的网格 | `UMusicClockComponent` |

#### 音乐源（MusicSource）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateMusicSource` | 从设置结构体创建音乐源 | `UMusicSourceBlueprintLibrary` |
| `CreateMusicClock` | 从音乐源创建只读时钟 | `UMusicSourceBlueprintLibrary` |
| `SetParentSource` | 设置偏移源的父源 | `UOffsetMusicSource` |
| `SetOffsetMs` | 设置时间偏移（毫秒） | `UOffsetMusicSource` |
| `SetLoopRegionByBars` | 按小节设置循环区域 | `URuntimeMusicSource` |

#### 节奏表（Tempometer）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetClock` | 设置时钟源 | `UMusicTempometerComponent` |
| `SetMaterialParameterCollection` | 设置要更新的 MPC | `UMusicTempometerComponent` |
| `GetTempo` / `GetBarProgress` / `GetBeatProgress` | 获取节奏数据 | `UMusicTempometerComponent` |

#### 步进音序器

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetCell` / `ToggleCell` | 设置/切换单元格状态 | `UMidiStepSequence` |
| `SetRowNoteNumber` | 设置行对应的 MIDI 音符号 | `UMidiStepSequence` |
| `SetNumPages` / `SetNumRows` / `SetNumColumns` | 调整序列尺寸 | `UMidiStepSequence` |

#### 事件委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `BeatEvent` | 节拍事件（节拍号, 拍中位置） | `UMusicClockComponent` |
| `BarEvent` | 小节事件（小节号） | `UMusicClockComponent` |
| `SectionEvent` | 段落事件（名称, 起始ms, 长度ms） | `UMusicClockComponent` |
| `PlayStateEvent` | 播放状态变化事件 | `UMusicClockComponent` |
| `MusicClockConnectedEvent` | 时钟连接成功事件 | `UMusicClockComponent` |

### 使用示例

**示例 1：创建 MetaSound 驱动的音乐时钟**

1. 在 Actor 上添加 `Music Clock` 组件
2. 设置 `Drive Method` 为 `MetaSound`
3. 在 `MetaSounds Audio Component` 中选择正在播放 MetaSound 的 AudioComponent
4. 蓝图 BeginPlay 调用 `Start`
5. 通过 `GetCurrentTimestamp`、`GetDistanceToNextBeat` 等节点获取时间信息
6. 绑定 `BeatEvent` 委托实现节拍同步逻辑

**示例 2：使用 MusicSource 框架**

1. 创建 `FManualMusicSourceSettings` 结构体，设置初始 BPM 和拍号
2. 调用 `UMusicSourceBlueprintLibrary::CreateMusicSource` 创建源
3. 调用 `UMusicSourceBlueprintLibrary::CreateMusicClock` 创建只读时钟
4. 在 Tick 中读取时钟数据用于游戏逻辑

**示例 3：材质节奏同步**

1. 创建 `UMaterialParameterCollection`，添加 `MusicBarProgress`、`MusicBeatProgress` 等参数
2. 在 Actor 上添加 `Music Tempometer` 组件
3. 设置 `Clock` 指向 MusicClockComponent
4. 设置 `MaterialParameterCollection` 指向你的 MPC
5. 在材质蓝图中引用 MPC 参数驱动 UV 动画或颜色变化

## C++ 用法

### 头文件引入

```cpp
#include "Components/MusicClockComponent.h"
#include "Components/MusicTempometerComponent.h"
#include "DataTypes/MidiStepSequence.h"
#include "DataTypes/MidiClock.h"
#include "MusicSource/MusicSource.h"
#include "MusicSource/MusicSourceSettings.h"
#include "MusicSource/OffsetMusicSource.h"
#include "MusicSource/RuntimeMusicSource.h"
#include "MusicClock/MusicClock.h"
#include "MusicSource/MusicSourceBlueprintLibrary.h"
#include "Analysis/PeakTamer.h"
```

### 基本用法：创建音乐时钟

```cpp
// 创建 MetaSound 驱动的音乐时钟（源自 MusicClockComponent.h）
UMusicClockComponent* Clock = UMusicClockComponent::CreateMetasoundDrivenMusicClock(
    GetWorld(), 
    MyAudioComponent,   // 正在播放 MetaSound 的 AudioComponent
    "MIDI Clock",       // MetaSound 的 MIDI Clock 输出引脚名
    true,               // 立即开始
    false               // 不跨关卡持久化
);

// 读取当前音乐时间
FMusicTimestamp Timestamp = Clock->GetCurrentTimestamp();
int32 CurrentBar = Timestamp.Bar;
float CurrentBeatInBar = Timestamp.Beat;

// 获取距离下一个节拍的进度（可用于节奏游戏的判定）
float DistToNextBeat = Clock->GetDistanceToNextBeat();
```

*来源: Public/HarmonixMetasound/Components/MusicClockComponent.h*

### 基本用法：音乐源框架（UE 5.5+ 新 API）

```cpp
#include "MusicSource/MusicSourceBlueprintLibrary.h"
#include "MusicSource/MusicSourceSettings.h"

// 创建手动设置的音乐源
FManualMusicSourceSettings Settings;
Settings.Tempo = 120.f;
Settings.TimeSigNumerator = 4;
Settings.TimeSigDenominator = 4;

TScriptInterface<IMusicSource> Source = UMusicSourceBlueprintLibrary::CreateMusicSource(
    GetTransientPackage(), Settings);

// 基于源创建只读时钟
UMusicClock* Clock = UMusicSourceBlueprintLibrary::CreateMusicClock(
    GetTransientPackage(), Source);

// 控制播放
Source->Start();

// 每帧读取音乐位置
const FMidiSongPos& Pos = Clock->GetCurrentSongPos();
float BeatsFromStart = Pos.BeatsIncludingCountIn;
```

*来源: Public/HarmonixMetasound/MusicSource/MusicSourceBlueprintLibrary.h, MusicSourceSettings.h*

### 进阶用法：校准时间偏移

```cpp
#include "MusicSource/MusicSourceBlueprintLibrary.h"
#include "MusicSource/OffsetMusicSource.h"

// 创建 MetaSound 源
FMetasoundMusicSourceSettings MsSettings;
MsSettings.AudioComponent = MyAudioComponent;
MsSettings.OutputPinName = "MIDI Clock";
TScriptInterface<IMusicSource> AudioRenderSource = 
    UMusicSourceBlueprintLibrary::CreateMusicSource(GetTransientPackage(), MsSettings);

// 创建音频渲染时钟（无偏移）
UMusicClock* AudioRenderClock = UMusicSourceBlueprintLibrary::CreateMusicClock(
    GetTransientPackage(), AudioRenderSource);

// 创建视频渲染偏移源（提前 30ms）
FOffsetMusicSourceSettings VideoOffsetSettings;
VideoOffsetSettings.ParentSource = AudioRenderSource;
VideoOffsetSettings.OffsetMs = -30.f;  // 视频需要提前渲染
TScriptInterface<IMusicSource> VideoSource = 
    UMusicSourceBlueprintLibrary::CreateMusicSource(GetTransientPackage(), VideoOffsetSettings);
UMusicClock* VideoClock = UMusicSourceBlueprintLibrary::CreateMusicClock(
    GetTransientPackage(), VideoSource);

// 创建玩家感知偏移源（延迟 50ms）
FOffsetMusicSourceSettings ExperienceOffsetSettings;
ExperienceOffsetSettings.ParentSource = AudioRenderSource;
ExperienceOffsetSettings.OffsetMs = 50.f;  // 玩家感知延迟
TScriptInterface<IMusicSource> ExperienceSource = 
    UMusicSourceBlueprintLibrary::CreateMusicSource(GetTransientPackage(), ExperienceOffsetSettings);
UMusicClock* ExperienceClock = UMusicSourceBlueprintLibrary::CreateMusicClock(
    GetTransientPackage(), ExperienceSource);
```

*来源: Public/HarmonixMetasound/MusicSource/OffsetMusicSource.h*

### 进阶用法：音频分析峰值检测

```cpp
#include "Analysis/PeakTamer.h"

// 创建峰值检测器
UHarmonixPeakTamer* Tamer = UHarmonixPeakTamer::CreateHarmonixPeakTamer();

// 配置攻击/释放时间
FHarmonixPeakTamerSettings Settings;
Settings.PeakAttackTimeSeconds = 0.01f;
Settings.PeakReleaseTimeSeconds = 2.0f;
Settings.bEnableValueSmoothing = true;
Settings.ValueAttackTimeSeconds = 0.01f;
Settings.ValueReleaseTimeSeconds = 0.01f;
Tamer->Configure(Settings);

// 每帧更新（传入原始音频峰值 0-1）
Tamer->Update(RawPeakValue, DeltaTime);

// 读取平滑后的值
float SmoothedPeak = Tamer->GetPeak();
float SmoothedValue = Tamer->GetValue();
```

*来源: Public/HarmonixMetasound/Analysis/PeakTamer.h*

### 进阶用法：音乐定时器

```cpp
// 通过 MusicClockComponent 添加定时器
FMusicTimeInterval Interval;
Interval.LengthInBars = 0; // 使用小节间隔
Interval.LengthInBeats = 2; // 每2拍触发

FMusicTimestamp StartTime;
StartTime.Bar = 1;
StartTime.Beat = 1.0f;

FMusicTimerHandle TimerHandle = Clock->AddTimerNative(
    Interval, StartTime, 
    ECalibratedMusicTimebase::VideoRenderTime, 
    true, // 循环
    FSimpleDelegate::CreateLambda([this]() {
        // 在每个拍点触发的逻辑
        UE_LOG(LogTemp, Log, TEXT("Beat triggered!"));
    })
);

// 暂停/恢复/移除定时器
Clock->PauseTimer(TimerHandle, true);  // 暂停
Clock->PauseTimer(TimerHandle, false); // 恢复
Clock->RemoveTimer(TimerHandle);       // 移除
```

*来源: Public/HarmonixMetasound/Components/MusicClockComponent.h, MusicTimerManager.h*

## Demo 示例

```cpp
// === MyMusicSyncActor.h ===
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/MusicClockComponent.h"
#include "MyMusicSyncActor.generated.h"

UCLASS()
class AMyMusicSyncActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMusicSyncActor();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UAudioComponent> AudioComponent;

    UPROPERTY(VisibleAnywhere)
    TObjectPtr<UMusicClockComponent> MusicClock;

private:
    // 存储上一次触发的小节号，避免重复触发
    int32 LastTriggeredBar = -1;

    UFUNCTION()
    void OnBeat(int32 BeatNumber, int32 BeatInBar);

    UFUNCTION()
    void OnBar(int32 BarNumber);
};

// === MyMusicSyncActor.cpp ===
#include "MyMusicSyncActor.h"
#include "Components/AudioComponent.h"

AMyMusicSyncActor::AMyMusicSyncActor()
{
    PrimaryActorTick.bCanEverTick = true;

    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("Audio"));
    AudioComponent->SetupAttachment(RootComponent);

    MusicClock = CreateDefaultSubobject<UMusicClockComponent>(TEXT("MusicClock"));
}

void AMyMusicSyncActor::BeginPlay()
{
    Super::BeginPlay();

    // 配置为 MetaSound 驱动
    MusicClock->DriveMethod = EMusicClockDriveMethod::MetaSound;
    MusicClock->MetasoundsAudioComponent = AudioComponent;

    // 绑定事件
    MusicClock->BeatEvent.AddDynamic(this, &AMyMusicSyncActor::OnBeat);
    MusicClock->BarEvent.AddDynamic(this, &AMyMusicSyncActor::OnBar);

    // 启动时钟
    MusicClock->Start();
}

void AMyMusicSyncActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (MusicClock->GetState() != EMusicClockState::Running)
    {
        return;
    }

    // 读取当前音乐时间
    FMusicTimestamp Now = MusicClock->GetCurrentTimestamp();
    float DistToNext = MusicClock->GetDistanceToNextBeat();

    // 例：距离下一个节拍越近，物体越亮
    float Brightness = 1.0f - DistToNext;

    UE_LOG(LogTemp, Verbose, TEXT("Bar %d, Beat %.2f, DistToNext %.3f, Brightness %.2f"),
        Now.Bar, Now.Beat, DistToNext, Brightness);
}

void AMyMusicSyncActor::OnBeat(int32 BeatNumber, int32 BeatInBar)
{
    UE_LOG(LogTemp, Log, TEXT("Beat: %d (in bar: %d)"), BeatNumber, BeatInBar);
}

void AMyMusicSyncActor::OnBar(int32 BarNumber)
{
    UE_LOG(LogTemp, Log, TEXT("Bar: %d"), BarNumber);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetaSound` | MetaSound 音频图系统，Harmonix 的节点和分析器注册于此 |
| `MetasoundEngine` | MetaSound 运行时引擎，提供 Generator 和 AudioComponent 集成 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 采样器音区键排序和空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决 FSoundWaveData API 废弃标记的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 的截断警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associations | FusionPatch 代理中添加用户对象用于关联活动追踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护中**。Harmonix 是 Epic Games 与 Harmonix（《Rock Band》开发商）合作的关键音频技术，是 Fortnite Festival 等节奏游戏的核心基础设施。

- **创建时间**: 2024-01-17，从 Harmonix 独立仓库迁移至 UE 5.4 引擎
- **更新频率**: 极其活跃，几乎每周都有更新，涵盖功能添加和 bug 修复
- **状态**: 实验性 (IsExperimentalVersion=true)，尚未标记为正式发布
- **API 稳定性**: 从代码中可以看到 API 持续演进，如新增 MusicSource 框架（UMusicClock、IMusicSource、UOffsetMusicSource 等）替代旧的 FMusicClockDriverBase 架构
- **推荐使用**: 适合需要精确音乐同步的项目，但需注意 API 可能在后续版本中有变化。建议密切关注版本更新日志

**注意**: 此插件默认未启用 (EnabledByDefault=false)，需要在项目设置中手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- 官方文档（无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)