# Music Environment

> A Project-Wide source of musical information (musically synchronized clocks, events, etc.)

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MusicEnvironment` (Runtime), `MusicEnvironmentEditor` (Editor), `MusicEnvironmentTests` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-02 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MusicEnvironment) | |

## 用途

Music Environment 是 Epic 的 Harmonix GenTech 团队开发的**项目级音乐信息基础设施**。它解决的核心问题是：在一个游戏项目中，多个系统（Level Sequencer、音频系统、UI、游戏逻辑）需要共享同一份音乐时钟信息——当前的 bar/beat 位置、tempo（BPM）、拍号（time signature）等。

这个 plugin 本身不播放音乐，也不包含具体的音频资产。它提供：

1. **`UFrameBasedMusicMap`**：一个基于帧精度的音乐地图（tempo map + bar map），支持变速（tempo changes）和变拍号（time signature changes），能在 tick/frame/seconds/musical time 之间互转
2. **`IMusicEnvironmentClockSource` / `IMusicEnvironmentMetronome`**：标准接口，让任何音乐播放系统可以作为"节拍源"注册到全局
3. **`UMusicClockSourceManager`**：一个基于 GameplayTag 的时钟注册表 + 全局权威时钟栈（global clock authority stack），支持在不同场景间切换主时钟
4. **`IMusicHandle` / `IMusicalAsset`**：音乐播放句柄和音乐资产接口，封装了 transport（play/pause/stop/seek）和时钟注册的生命周期管理

简单来说：这是 UE5 中让 Level Sequencer、MetaSounds 等系统与音乐节拍同步的底层框架。

## 使用场景

- 你在做一个节奏游戏，需要让游戏事件精确对齐音乐的 bar/beat → 用 Music Environment 的时钟系统
- 你的 Level Sequencer 需要与背景音乐的 tempo 同步 → 通过 `IMusicEnvironmentClockSource` 接口获取音乐时钟
- 你有多个音乐段落（如战斗音乐、探索音乐），需要在切换时保持全局时钟一致性 → 用 `UMusicClockSourceManager` 的 global authority stack
- 你需要在编辑器中预览音乐同步的 Sequencer 动画 → 用 `CanAuditionInEditor()` 支持的 metronome

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 MusicEnvironmentSubsystem 单例 | `UMusicEnvironmentSubsystem` |
| `GetClockSourceManager` | 获取时钟管理器 | `UMusicEnvironmentSubsystem` |
| `CanSpawnMetronome` | 检查是否能生成 metronome | `UMusicEnvironmentSubsystem` |
| `SpawnMetronome` | 生成一个 metronome 实例 | `UMusicEnvironmentSubsystem` |
| `FindClock` | 按 GameplayTag 查找已注册的时钟 | `UMusicClockSourceManager` |
| `AddTaggedClock` | 注册一个带标签的时钟 | `UMusicClockSourceManager` |
| `RemoveTaggedClock` | 移除已注册的时钟 | `UMusicClockSourceManager` |
| `GetGlobalMusicClockAuthority` | 获取当前全局权威时钟（栈顶） | `UMusicClockSourceManager` |
| `PushGlobalMusicClockAuthority` | 将时钟压入全局权威栈 | `UMusicClockSourceManager` |
| `PopMusicClockAuthority` | 弹出栈顶时钟 | `UMusicClockSourceManager` |
| `Play` | 播放音乐资产，返回 handle | `IMusicalAsset` |
| `PrepareToPlay` | 准备播放（不立即开始） | `IMusicalAsset` |
| `BranchOnTransportState` | 根据 transport 状态分支 | `IMusicHandle` |
| `GetCurrentBarBeat` | 获取当前 bar 和 beat | `IMusicHandle` |
| `BecomeGlobalMusicClockAuthority` | 让此 handle 的时钟成为全局权威 | `IMusicHandle` |
| `RegisterAsTaggedClock` | 按 GameplayTag 注册此 handle 的时钟 | `IMusicHandle` |

### 使用示例（蓝图描述）

**播放音乐并获取全局时钟**：

1. 获取 `MusicEnvironmentSubsystem` → `Get`
2. 拿到一个 `IMusicalAsset`（如通过 MetaSound 或 Harmonix 的资产）
3. 调用 `Play`，勾选 `BecomeAuthoritativeClock = true`
4. 返回的 `FMusicHandle` 可用于后续 transport 控制
5. 任何系统都可以通过 `GetClockSourceManager` → `GetGlobalMusicClockAuthority` 获取当前时钟

**查找特定时钟**：

1. 调用 `GetClockSourceManager` → `FindClock`，传入 GameplayTag（如 `Music.Combat`）
2. 返回的 `IMusicEnvironmentClockSource` 可以查询 bar/beat/position

## C++ 用法

### 头文件引入

```cpp
#include "MusicEnvironmentSubsystem.h"
#include "MusicClockSourceManager.h"
#include "MusicEnvironmentClockSource.h"
#include "FrameBasedMusicMap.h"
#include "MusicTypes/MusicalAsset.h"
#include "MusicTypes/MusicHandle.h"
```

### 基本用法

**获取子系统和时钟管理器**：

```cpp
// 来源: MusicEnvironmentSubsystem.cpp
UMusicEnvironmentSubsystem& Subsystem = UMusicEnvironmentSubsystem::Get();
UMusicClockSourceManager* ClockManager = Subsystem.GetClockSourceManager();
```

**创建和初始化一个 MusicMap**：

```cpp
// 来源: FrameBasedMusicMap.spec.cpp
const FFrameRate FrameResolution(24000, 1);  // 24000 fps
float TempoBpm = 120.0f;
const FFrameBasedTimeSignature TimeSig(4, 4);

UFrameBasedMusicMap* MusicMap = NewObject<UFrameBasedMusicMap>();
MusicMap->SetFrameResolution(FrameResolution);
MusicMap->Init(TempoBpm, TimeSig);
```

**查询 bar/beat 位置**：

```cpp
// 来源: MusicEnvironmentClockSource.cpp
FMusicalTime MusicalTime = ClockSource->GetPositionMusicalTime();
float Bar = MusicalTime.FractionalBar();
float BeatInBar = MusicalTime.FractionalBeatInBar();
```

### 进阶用法

**添加变速和变拍号**：

```cpp
// 来源: FrameBasedMusicMap.spec.cpp
// 在 Bar 2 处添加一个 tempo 变化
int32 AtBar = 2;
int32 AtTick = BarsToTick(TimeSig, AtBar);
float AtMs = TicksToMs(InitTempoBpm, AtTick);
MusicMap->AddTempo(AtTick, AtMs, 100.0f);  // 变为 100 BPM

// 在 Bar 1 处插入新的 tempo（会重新计算后续时间点）
MusicMap->InsertTempo(BarsToTick(TimeSig, 1), 110.0f);

// 添加拍号变化
MusicMap->AddTimeSignature(AtTick, AtBar, 3, 4);  // 变为 3/4 拍
```

**注册自定义时钟源**：

```cpp
// 实现 IMusicEnvironmentClockSource 接口
class UMyMusicClock : public UObject, public IMusicEnvironmentClockSource
{
    GENERATED_BODY()
public:
    virtual float GetPositionSeconds() const override { /* ... */ }
    virtual FMusicalTime GetPositionMusicalTime() const override { /* ... */ }
    virtual int32 GetPositionAbsoluteTick() const override { /* ... */ }
    // ... 其他纯虚函数
};

// 注册为带标签的时钟
UMusicClockSourceManager* ClockMgr = UMusicEnvironmentSubsystem::Get().GetClockSourceManager();
ClockMgr->AddTaggedClock(FGameplayTag::RequestGameplayTag("Music.Battle"), MyClockObject);

// 或推入全局权威栈
ClockMgr->PushGlobalMusicClockAuthority(MyClockObject);
```

**使用 StrongMusicHandle 防止 GC**：

```cpp
// 来源: MusicHandle.h
// 在非 UCLASS/USTRUCT 上下文中持有 music handle
FStrongMusicHandle StrongHandle;
StrongHandle = MyMusicAsset->Play(GetWorld(), nullptr, 0.0f, true);
// StrongHandle 内部持有 TStrongObjectPtr，防止 UObject 被 GC
StrongHandle->Pause();
StrongHandle->Stop();
```

## Demo 示例

### 自定义 Metronome 实现

**MyMetronome.h**：

```cpp
#pragma once
#include "MusicEnvironmentMetronome.h"
#include "MyMetronome.generated.h"

UCLASS(BlueprintType)
class UMyMetronome : public UObject, public IMusicEnvironmentMetronome
{
    GENERATED_BODY()
public:
    virtual bool Initialize(UWorld* InWorld) override;
    virtual void Tick(float DeltaSeconds) override;
    virtual void Start(double FromSeconds = 0.0) override;
    virtual void Seek(double ToSeconds) override;
    virtual void Stop() override;
    virtual void Pause() override;
    virtual void Resume() override;
    virtual float GetCurrentTempo() const override;
    virtual double GetCurrentPositionSeconds() const override;
    virtual float GetCurrentSpeed() const override;
    virtual float GetCurrentVolume() const override;
    virtual bool IsMuted() const override;

protected:
    virtual void OnMusicMapSet() override;
    virtual void OnSetSpeed(const float Speed) override;
    virtual bool OnSetTempo(const float Bpm) override;
    virtual void OnSetVolume(float NewVolumeLinear) override;
    virtual void OnSetMuted(bool bNewMuted) override;
};
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "MusicEnvironment"
});
```

**注册并使用**：

```cpp
// 在模块 StartupModule 或 GameInstance 初始化时
UMusicEnvironmentSubsystem& Subsystem = UMusicEnvironmentSubsystem::Get();
Subsystem.SetMetronomeClass(UMyMetronome::StaticClass());

// 需要时生成
if (Subsystem.CanSpawnMetronome())
{
    TScriptInterface<IMusicEnvironmentMetronome> Metronome = 
        Subsystem.SpawnMetronome(GetTransientPackage());
    Metronome->Initialize(GetWorld());
    Metronome->Start();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、FString、TArray 等 |
| `CoreUObject` | UObject 系统、UINTERFACE 支持 |
| `Engine` | UEngineSubsystem、UWorld |
| `TimeManagement` | FFrameRate、FFrameTime 帧时间管理 |
| `GameplayTags` | FGameplayTag 用于时钟注册和查找 |
| `MovieScene` | Sequencer 集成（FMusicalTime 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-12 | `8406696` | 修复非 unity build 下的缺失头文件问题（CoreUObject 大规模变更后的适配） |
| 2025-06-26 | `ec90099` | 为有对应 .gen.cpp 的源文件添加 UE_INLINE_GENERATED_CPP_BY_NAME 宏（批量工具 UnrealCodeFixup） |
| 2025-06-23 | `d42c028` | **Music Map Song Length Data** — 为 `IMusicMapSource` 新增 `GetSongLengthSeconds()` 功能 |

### 维护评价

- **年龄**：约 1 年，2024 年 12 月创建
- **状态**：🆕 新插件，仍在积极开发中
- **实验性标记**：`IsBetaVersion=true` 且 `IsExperimentalVersion=true`，`EnabledByDefault=false` — 这是一个实验性插件，需要手动启用
- **更新频率**：近 3 个月内有实质性功能更新（song length 数据支持），说明仍在活跃迭代
- **已知限制**：
  - API 可能随版本变动，不建议在生产环境中重度依赖
  - `IMusicEnvironmentMetronome` 需要自行实现具体类（plugin 不提供默认实现）
  - 没有 `DocsURL`，官方文档暂缺
- **推荐**：如果你在做需要音乐同步的项目（特别是与 Harmonix/MetaSounds 集成），值得关注和试用，但要注意 API 稳定性风险

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MusicEnvironment)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Runtime/MusicEnvironment/Source/MusicEnvironmentTests/Private/FrameBasedMusicMap.spec.cpp)
