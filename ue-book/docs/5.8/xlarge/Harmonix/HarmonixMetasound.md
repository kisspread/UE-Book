# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音乐交互框架 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点、音乐资产、MIDI 工具、DSP 工具） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

---

## 用途

Harmonix 是由 Epic Games 的 Harmonix GenTech 团队开发的**音乐交互音频框架**，为 UE5 提供了一套完整的音乐时间感知和音频处理工具链。

这个插件解决的核心问题是：**让游戏系统能够精确地感知和响应音乐时间**。

传统游戏音频系统只能处理"播放/暂停/音量"等简单控制，而 Harmonix 提供了：

1. **音乐时钟（Music Clock）**——让游戏能精确知道"当前处于哪一小节、第几拍、进度多少"，并与音频渲染线程精确同步
2. **MIDI 处理流水线**——在 MetaSound 图中处理 MIDI 数据，驱动音符生成、节奏同步等
3. **步进序列器（Step Sequencer）**——在 MetaSound 中创建可编辑的节奏 pattern
4. **节拍器（Metronome）**——提供精确的 tempo/time signature 驱动
5. **DSP 工具集**——音频信号处理原语
6. **音乐源抽象层（Music Source）**——统一的音乐时间生产接口，支持 MetaSound 驱动、MIDI 文件驱动、手动配置等多种来源

Harmonix 默认不启用（`EnabledByDefault: false`），且标记为实验性（`IsExperimentalVersion: true`）。需要在项目的 Plugins 设置中手动启用。

---

## 架构概览

Harmonix 由 11 个模块组成，按功能分为四层：

```
┌─────────────────────────────────────────────────────┐
│                   蓝图 / 游戏逻辑层                    │
│  UMusicClockComponent · UMusicTempometerComponent    │
│  UHarmonixMusicHandle · UMusicSourceBlueprintLibrary │
├─────────────────────────────────────────────────────┤
│              音乐源与时钟层 (Music Source)              │
│  IMusicSource → UMetasoundMusicSource                │
│                → URuntimeMusicSource                 │
│                → UOffsetMusicSource                  │
│  UMusicClock (只读时间视图)                            │
│  UMidiClockUpdateSubsystem (帧更新调度)               │
├─────────────────────────────────────────────────────┤
│              MetaSound 集成层                          │
│  HarmonixMetasound: FMidiClock · FMidiStream         │
│  节点: Metronome · StepSeq · MIDIPlayer · Fusion     │
│  分析: SongPosAnalyzer · PeakTamer                    │
│  资产: UMidiStepSequence · UMidiStutterSequence       │
├─────────────────────────────────────────────────────┤
│              基础层                                    │
│  HarmonixMidi: MIDI 文件解析                           │
│  HarmonixDsp: DSP 算法原语                             │
│  Harmonix: 公共基础工具                                │
└─────────────────────────────────────────────────────┘
```

### 模块职责

| 模块 | 职责 |
|---|---|
| **Harmonix** | 公共基础库、日志、版本 |
| **HarmonixDsp** | DSP 算法：滤波器、LFO、延迟、ADSR 等 |
| **HarmonixMidi** | MIDI 文件解析（`.mid`）、MIDI 消息、Song Maps |
| **HarmonixMetasound** | 核心模块：音乐时钟、MetaSound 节点、MIDI 流处理、音乐源抽象、步进序列器 |
| **Harmonix*DspEditor / MidiEditor / MetasoundEditor** | 对应模块的编辑器扩展 |
| **Harmonix*DspTests / MidiTests / MetasoundTests** | 自动化测试 |

> 📖 详细子模块文档见：
> - [HarmonixMetasound 模块](HarmonixMetasound.md)
> - [HarmonixDsp 模块](HarmonixDsp.md)
> - [HarmonixMidi 模块](HarmonixMidi.md)

---

## 蓝图用法

### 核心组件

| 组件 | 说明 | 关键节点 |
|---|---|---|
| `UMusicClockComponent` | 音乐时钟，感知拍/小节/段落 | `Start` / `Stop` / `GetCurrentTimestamp` / `BeatEvent` |
| `UMusicTempometerComponent` | 将音乐时钟数据写入 MPC 供材质使用 | `SetClock` / `SetMaterialParameterCollection` |
| `UHarmonixMusicHandle` | 音乐资产播放句柄 | `Play` / `Pause` / `Continue` / `Stop` |

### 音乐时钟快速上手

#### 创建 MetaSound 驱动的音乐时钟

1. 在 Actor 上添加 `UMusicClockComponent`
2. 设置 `Drive Method = MetaSound`
3. 指向播放 MetaSound 的 `AudioComponent`
4. `Start()` 启动

#### 创建 Wall Clock 驱动的音乐时钟

1. 在 Actor 上添加 `UMusicClockComponent`
2. 设置 `Drive Method = WallClock`
3. 指定 `Tempo Map`（MIDI 文件）
4. `Start()` 启动

#### 使用工厂方法（推荐）

```cpp
// MetaSound 驱动
auto* Clock = UMusicClockComponent::CreateMetasoundDrivenMusicClock(
    WorldContext, AudioComponent, "MIDI Clock", true, false);

// Wall Clock 驱动
auto* Clock = UMusicClockComponent::CreateWallClockDrivenMusicClock(
    WorldContext, MidiFile, true, false);
```

蓝图中对应节点为静态函数 `Create Metasound Driven Music Clock` / `Create Wall Clock Driven Music Clock`。

### 常用蓝图查询

```blueprint
// 获取当前拍号（Bar:Beat）
MusicClock → GetCurrentTimestamp → Timestamp

// 获取当前小节进度 [0,1)
MusicClock → GetDistanceFromCurrentBar → BarProgress

// 获取当前 BPM
MusicClock → GetCurrentBeatsPerMinute → BPM

// 获取节拍事件
MusicClock → BeatEvent (BlueprintAssignable)

// 获取段落变化
MusicClock → SectionEvent (BlueprintAssignable)
```

### 音乐定时器

在特定音乐时间点触发回调：

```blueprint
// 每4小节触发一次
MusicClock → BP_AddTimer
  Interval: (Bar=4, Beat=1)
  Start: (Bar=1, Beat=1)
  Timebase: VideoRenderTime
  Looping: true
  Delegate: → OnTimerFired
```

### 材质同步（Tempometer）

```blueprint
// 1. 添加 MusicTempometerComponent
// 2. 设置 Clock
SetClock → MusicClockComponent
// 3. 设置 MPC
SetMaterialParameterCollection → MPC_Asset
// 4. 在材质中读取参数：
//    MusicSecondsFromBarOne, MusicBarProgress, MusicTempo, ...
```

### 音乐源蓝图使用

```blueprint
// 创建 MetaSound 音乐源
MusicSourceBlueprintLibrary → CreateMusicSource
  Settings: FMetasoundMusicSourceSettings
    AudioComponent: MyAudioComp
    OutputPinName: "MIDI Clock"

// 创建只读音乐时钟
MusicSourceBlueprintLibrary → CreateMusicClock
  Source: (上面创建的 MusicSource)
```

---

## C++ 用法

### 头文件引入

```cpp
// 音乐时钟
#include "HarmonixMetasound/Components/MusicClockComponent.h"

// MIDI 时钟
#include "HarmonixMetasound/DataTypes/MidiClock.h"

// MIDI 流
#include "HarmonixMetasound/DataTypes/MidiStream.h"

// 音乐源接口
#include "HarmonixMetasound/MusicSource/MusicSource.h"

// 步进序列器
#include "HarmonixMetasound/DataTypes/MidiStepSequence.h"

// 音乐定时器
#include "HarmonixMetasound/Components/MusicTimerManager.h"
```

### 基本用法：创建和查询音乐时钟

```cpp
// 创建 MetaSound 驱动的音乐时钟
UMusicClockComponent* Clock = UMusicClockComponent::CreateMetasoundDrivenMusicClock(
    GetWorld(), AudioComponent, FName("MIDI Clock"), /*Start=*/true);

// 查询当前音乐时间
FMusicTimestamp Timestamp = Clock->GetCurrentTimestamp();
int32 CurrentBar = Timestamp.Bar;      // 1-based bar
float CurrentBeat = Timestamp.Beat;    // 1-based beat in bar

// 查询当前段落
FString SectionName = Clock->GetCurrentSectionName();
float SectionStartMs = Clock->GetCurrentSectionStartMs();

// 查询进度
float BeatProgress = Clock->GetDistanceFromCurrentBeat();
float BarProgress = Clock->GetDistanceFromCurrentBar();
```

### 进阶用法：自定义音乐源 + 偏移时钟

```cpp
// 创建基础音乐源（MetaSound 驱动）
UMetasoundMusicSource* BaseSource = NewObject<UMetasoundMusicSource>(Outer);
BaseSource->ConnectToAudioComponent(AudioComp, "MIDI Clock");

// 创建偏移源（视频渲染时间，比音频提前 30ms）
UOffsetMusicSource* VideoSource = NewObject<UOffsetMusicSource>(Outer);
VideoSource->SetParentSource(BaseSource);
VideoSource->SetOffsetMs(-30.0f); // 负值 = 提前

// 创建只读时钟
UMusicClock* VideoClock = NewObject<UMusicClock>(Outer);
VideoClock->SetSource(VideoSource);

// 注册到子系统（自动帧更新）
UMidiClockUpdateSubsystem::TrackMusicSource(BaseSource);
UMidiClockUpdateSubsystem::TrackMusicSource(VideoSource);
UMidiClockUpdateSubsystem::TrackMusicClock(VideoClock);
```

### 进阶用法：MIDI 步进序列器

```cpp
// 创建步进序列器
UMidiStepSequence* StepSeq = NewObject<UMidiStepSequence>(Outer);
StepSeq->SetNumPages(2);
StepSeq->SetNumRows(8);
StepSeq->SetNumColumns(16);

// 设置音符
StepSeq->SetRowNoteNumber(0, 36); // Kick: C2
StepSeq->SetRowNoteNumber(1, 38); // Snare: D2
StepSeq->SetRowNoteNumber(2, 42); // HiHat: F#2

// 设置 pattern
StepSeq->SetCell(0, 0, true);  // Kick on beat 1
StepSeq->SetCell(0, 4, true);  // Kick on beat 3
StepSeq->SetCell(1, 4, true);  // Snare on beat 3
StepSeq->SetCell(2, 0, true);  // HiHat on every 16th
StepSeq->SetCell(2, 2, true);
// ... etc

// 传递给 MetaSound 节点使用
```

---

## Demo 示例

### 最小可编译示例：音乐同步旋转

```cpp
// MusicSyncRotateComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "MusicSyncRotateComponent.generated.h"

class UMusicClockComponent;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMusicSyncRotateComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UPROPERTY(EditAnywhere, Category="Music")
    float RotationDegreesPerBeat = 45.0f;

private:
    UPROPERTY()
    TObjectPtr<UMusicClockComponent> MusicClock;
};
```

```cpp
// MusicSyncRotateComponent.cpp
#include "MusicSyncRotateComponent.h"
#include "HarmonixMetasound/Components/MusicClockComponent.h"

void UMusicSyncRotateComponent::BeginPlay()
{
    Super::BeginPlay();

    // 在同一 Actor 上查找音乐时钟
    MusicClock = GetOwner()->FindComponentByClass<UMusicClockComponent>();
    if (!MusicClock)
    {
        UE_LOG(LogTemp, Warning, TEXT("MusicSyncRotateComponent: No MusicClockComponent found!"));
    }
}

void UMusicSyncRotateComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!MusicClock || MusicClock->GetState() == EMusicClockState::Stopped)
    {
        return;
    }

    // 根据当前拍的进度进行平滑旋转
    float BeatProgress = MusicClock->GetDistanceToClosestBeat();
    float RotAngle = RotationDegreesPerBeat * BeatProgress;

    FRotator DeltaRot(0.0f, RotAngle, 0.0f);
    GetOwner()->AddActorLocalRotation(DeltaRot);
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core", "CoreUObject", "Engine",
    "Harmonix", "HarmonixMetasound"
});
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 图前端框架，所有 MetaSound 节点的基础 |
| `MetasoundEngine` | MetaSound 运行时引擎，音频组件播放 |
| `MetasoundGraphCore` | MetaSound 图核心，数据类型注册 |
| `HarmonixMidi` | MIDI 文件解析、Song Maps、MIDI 消息 |
| `HarmonixDsp` | DSP 原语（用于 Fusion 合成器） |
| `SignalProcessing` | DSP 基础库（延迟线、LFO 等） |
| `AudioMixer` | 音频混合器，音频线程基础设施 |
| `AudioAnalyzer` | 音频分析（峰值检测等） |
| `HarmonixDsp` | DSP 处理原语 |
| `AssetRegistry` | 资产注册（用于编译期依赖分析） |
| `UnrealEd` | 编辑器扩展 |

> ℹ️ 部分模块（如 `HarmonixDsp`）在 `Build.cs` 中声明了 `UnrealEd` 依赖，这可能导致纯 Runtime 打包问题。此为实验性插件的已知限制。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense | 修复 Fusion 音频引擎的声部分配顺序和空指针防御 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup | 解决与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association | 为 Fusion 音色补丁代理添加用户对象，用于活动跟踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |

### 维护评价

**活跃维护中** ✅

- **创建时间**：2024-01-17，从 `ue5-main` 分支移入引擎插件目录，目标版本 UE 5.4
- **更新频率**：高——最近更新 2026 年 5 月，平均每 1-2 周有提交
- **维护团队**：Epic Games Harmonix GenTech（专责团队）
- **活跃度**：持续的 bug 修复和功能增强，包括 Fusion 合成器的持续开发
- **实验性状态**：`IsExperimentalVersion: true`，API 可能在版本间变化
- **注意事项**：
  - 需要手动启用（`EnabledByDefault: false`）
  - 部分模块将 `UnrealEd` 列为运行时依赖，纯打包可能存在编译问题
  - API 尚未稳定，升级引擎版本时可能需要调整代码

**推荐使用**：如果你在开发音乐驱动的游戏（如节奏游戏、音乐互动体验），强烈推荐使用。虽然标记为实验性，但由 Epic 专责团队维护，代码质量高。注意关注引擎升级时的 API 变更。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [HarmonixMetasound 模块文档](HarmonixMetasound.md)
- [HarmonixDsp 模块文档](HarmonixDsp.md)
- [HarmonixMidi 模块文档](HarmonixMidi.md)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)
- [测试用例 - MIDI](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)
- [测试用例 - DSP](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)