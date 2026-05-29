# Music Environment

> A Project-Wide source of musical information (musically synchronized clocks, events, etc.)

| 属性 | 值 |
|---|---|
| 中文名 | 音乐环境 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MusicEnvironment` (Runtime), `MusicEnvironmentEditor` (Runtime), `MusicEnvironmentTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-12-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment) | |

## 用途

Music Environment 插件是一个项目范围内的音乐信息源，旨在为整个项目提供一套统一、精确的音乐时间管理系统。它的核心功能是将音乐时间线（包括节拍、小节、速度变化和时间签名）抽象为引擎可管理的对象和接口，使游戏逻辑、动画、音频组件和其他系统能够基于精确的“音乐时钟”进行同步，而无需开发者手动处理复杂的时间转换。

简而言之，这个插件解决了**“如何让游戏中的事件与音乐的节拍精准同步”** 的问题。它充当了一个中央权威的音乐时钟，其他系统可以查询当前的音乐时间（例如“当前是第 3 小节，第 2 拍”），并据此触发事件或驱动动画。

## 使用场景

-   **节奏/音乐游戏**：核心场景。用于精确判定玩家输入与音乐节拍的匹配度，生成音符下落轨迹，或在特定拍点触发游戏事件（如得分、特效）。
-   **音乐可视化**：根据音乐的节拍、强度或时间线，动态改变场景中的灯光、粒子效果或物体的运动状态。
-   **同步动画与序列器**：让 `LevelSequence` 或角色动画与游戏背景音乐的节拍严格对齐，实现“音画同步”的效果。
-   **动态音乐系统**：构建复杂的、交互式的动态音乐混合系统。该插件可以管理不同音乐层（Layer）的入口和出口时机，确保它们在正确的音乐小节或拍子上切换。
-   **编辑器音乐预览与调整**：在编辑器内，利用 `UMusicEnvironmentMetronome` 提供的节拍器功能，预览音乐同步效果，并调整 `MusicMap` 中的速度和时间签名事件。

## 蓝图用法

该插件的蓝图 API 围绕几个核心接口和类展开，主要功能分为播放控制、时钟管理和时间查询。

### 核心节点

#### 音乐播放控制 (`IMusicHandle`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play` | 准备并开始播放音乐资产，返回一个音乐句柄。 | `IMusicalAsset` |
| `PrepareToPlay` | 准备音乐资产播放，但不立即开始。 | `IMusicalAsset` |
| `Pause` | 暂停音乐播放。 | `IMusicHandle` |
| `Continue` | 恢复暂停的音乐播放。 | `IMusicHandle` |
| `Stop` | 停止音乐播放。 | `IMusicHandle` |
| `GetTransportState` | 获取当前播放状态（准备、播放、暂停、停止等）。 | `IMusicHandle` |
| `BranchOnTransportState` | 根据播放状态执行不同的执行引脚。 | `IMusicHandle` |
| `GetCurrentBarBeat` | 获取当前的节拍和拍子信息（如“第4小节，第2.5拍”）。 | `IMusicHandle` |

#### 音乐时钟管理 (`UMusicClockSourceManager`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindClock` | 根据标签查找一个注册的音乐时钟源。 | `UMusicClockSourceManager` |
| `AddTaggedClock` | 将一个音乐时钟源注册到一个游戏标签下。 | `UMusicClockSourceManager` |
| `GetGlobalMusicClockAuthority` | 获取当前全局权威音乐时钟。 | `UMusicClockSourceManager` |
| `PushGlobalMusicClockAuthority` | 将一个音乐时钟压入全局权威栈的顶部。 | `UMusicClockSourceManager` |
| `PopMusicClockAuthority` | 弹出全局权威栈顶部的时钟。 | `UMusicClockSourceManager` |

#### 音乐地图与时间转换 (`UFrameBasedMusicMap`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Init` | 用指定的初始速度和时间签名初始化音乐地图。 | `UFrameBasedMusicMap` |
| `GetSeconds` | 将音乐时间（小节/拍）转换为绝对秒数。 | `UFrameBasedMusicMap` |
| `GetFrame` | 将音乐时间转换为基于帧的时间。 | `UFrameBasedMusicMap` |
| `GetMusicalTime` | 将绝对 Tick 或帧时间转换回音乐时间（小节/拍）。 | `UFrameBasedMusicMap` |
| `InsertTempo` | 在指定的时间点插入一个速度变化事件。 | `UFrameBasedMusicMap` |
| `InsertTimeSignature` | 在指定的小节插入一个时间签名变化事件。 | `UFrameBasedMusicMap` |
| `Quantize` | 将一个音乐时间量化（对齐）到指定的细分间隔（如1/4音符）。 | `UFrameBasedMusicMap` |

#### 全局子系统与节拍器 (`UMusicEnvironmentSubsystem`)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get` | 获取 MusicEnvironment 子系统的单例引用。 | `UMusicEnvironmentSubsystem` |
| `GetClockSourceManager` | 获取音乐时钟源管理器的实例。 | `UMusicEnvironmentSubsystem` |
| `SpawnMetronome` | 生成一个节拍器实例。 | `UMusicEnvironmentSubsystem` |
| `CanSpawnMetronome` | 检查是否可以生成节拍器。 | `UMusicEnvironmentSubsystem` |

### 使用示例（蓝图描述）

1.  **播放音乐并同步事件**：
    -   首先，需要一个实现了 `IMusicalAsset` 接口的资产（例如一个 `SoundWave` 或 `MetaSound`）。
    -   调用 `Play` 节点，传入该资产和一个“播放上下文”对象（如当前 Actor），返回一个 `MusicHandle`。
    -   将 `MusicHandle` 存储在一个变量中。
    -   使用 `GetTransportState` 或 `BranchOnTransportState` 持续监控播放状态。
    -   使用 `GetCurrentBarBeat` 每帧查询当前的节拍和拍子。当 `Bar` 和 `Beat` 满足特定条件（例如每小节第一拍）时，触发你的游戏逻辑（如生成音符、播放特效）。

2.  **在编辑器中预览节拍**：
    -   在编辑器工具或 Actor 中，通过 `UMusicEnvironmentSubsystem::Get()` -> `SpawnMetronome` 生成一个节拍器。
    -   为节拍器设置一个 `MusicMap`。
    -   调用 `Start` 启动节拍器，它将开始按照地图定义的节奏和时间签名发出“滴答”声，可用于同步测试。

## C++ 用法

### 头文件引入

```cpp
// 核心子系统和模块
#include "MusicEnvironmentSubsystem.h"
#include "MusicEnvironmentModule.h"

// 核心类型和接口
#include "MusicTypes/MusicalAsset.h"
#include "MusicHandle.h"
#include "MusicClockSourceManager.h"

// 音乐地图
#include "FrameBasedMusicMap.h"

// 可选：如果你要实现自己的节拍器
#include "MusicEnvironmentMetronome.h"
```

### 基本用法

#### 1. 获取子系统并播放音乐资产

```cpp
// 假设你在一个 AActor 子类中
void AMyActor::PlayMyMusic()
{
    // 获取音乐环境子系统
    UMusicEnvironmentSubsystem& MusicSub = UMusicEnvironmentSubsystem::Get();
    
    // 假设你有一个实现了 IMusicalAsset 接口的 UObject* (如你的 MetaSound 源)
    TScriptInterface<IMusicalAsset> MyMusicAsset = MyMetaSoundSourceObject;
    
    if (MyMusicAsset)
    {
        // 播放音乐，并将当前 Actor 作为播放上下文。
        // 第三个参数为从第 0 秒开始，第四个参数为不成为全局时钟权威。
        TScriptInterface<IMusicHandle> Handle = MyMusicAsset->Play(
            this, // PlaybackContext
            nullptr, // AudioComponent (可选)
            0.0f, // FromSeconds
            false // BecomeAuthoritativeClock
        );
        
        if (Handle)
        {
            MyMusicHandle = Handle;
            // 可以开始查询 Handle 的状态了
        }
    }
}
```

#### 2. 在 Tick 中查询音乐时间并同步

```cpp
void AMyActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (MyMusicHandle && MyMusicHandle->IsValid())
    {
        // 更新音乐句柄内部状态
        MyMusicHandle->Tick(DeltaTime);
        
        // 查询当前的音乐时间
        float CurrentBar = 0.f;
        float CurrentBeat = 0.f;
        EMusicHanldeClockValidity Validity;
        MyMusicHandle->GetCurrentBarBeat(CurrentBar, CurrentBeat, Validity);
        
        if (Validity == EMusicHanldeClockValidity::ClockValid)
        {
            // 例如，检查是否到了小节第一拍（整数拍）
            if (FMath::IsNearlyEqual(FMath::Fractional(CurrentBeat), 0.0f, 0.01f))
            {
                UE_LOG(LogMusicEnvironment, Log, TEXT("Downbeat! Bar: %.0f"), CurrentBar);
                // 触发你的游戏事件...
            }
        }
    }
}
```

### 进阶用法

#### 1. 创建和编辑音乐地图（MusicMap）

```cpp
void AMyMusicEditor::CreateAndEditMusicMap()
{
    // 以电影帧率（如 24fps）创建一个音乐地图
    FFrameRate FrameRate(24, 1);
    UFrameBasedMusicMap* MusicMap = NewObject<UFrameBasedMusicMap>(GetTransientPackage());
    MusicMap->SetFrameResolution(FrameRate);
    
    // 初始化：120 BPM，4/4拍，从第0小节第0拍开始
    FFrameBasedTimeSignature InitialTimeSig(4, 4);
    MusicMap->Init(120.0f, InitialTimeSig);
    
    // 在第10小节（Bar 9，从0计数）插入一个拍号变化（3/4拍）
    MusicMap->InsertTimeSignature(9, 3, 4);
    
    // 在第500 Tick（假设是歌曲开头后第2秒处）插入一个速度变化（变为 90 BPM）
    MusicMap->InsertTempo(500, 90.0f);
    
    // 现在，这个 MusicMap 描述了一首前8小节为4/4拍120BPM，第9小节起变为3/4拍90BPM的乐曲。
    // 你可以将它传递给实现了 IMusicMapSource 的资产，或用于驱动节拍器。
}
```

#### 2. 使用音乐时钟同步外部系统

```cpp
// 假设你有一个自定义的特效系统，需要根据音乐节拍脉动
void AMyVisualEffect::SynchronizeWithMusicClock()
{
    UMusicEnvironmentSubsystem& MusicSub = UMusicEnvironmentSubsystem::Get();
    UMusicClockSourceManager* ClockManager = MusicSub.GetClockSourceManager();
    
    if (ClockManager)
    {
        TScriptInterface<IMusicEnvironmentClockSource> GlobalClock = ClockManager->GetGlobalMusicClockAuthority();
        
        if (GlobalClock)
        {
            // 获取全局时钟的当前音乐时间
            FMusicalTime CurrentMusicalTime = GlobalClock->GetPositionMusicalTime();
            
            // 使用音乐时间来驱动特效
            // 例如，根据当前拍子在小节中的位置（0-1之间）来调整粒子系统的生成速率
            float BeatProgress = static_cast<float>(CurrentMusicalTime.TickInBar) / 
                                static_cast<float>(CurrentMusicalTime.TicksPerBar);
            MyParticleComponent->SetFloatParameter("BeatProgress", BeatProgress);
            
            // 或者，量化一个音乐时间并在此刻触发一个事件
            FMusicalTime QuantizedTriggerTime = GlobalClock->Quantize(CurrentMusicalTime, 
                TripletQuantizationTicks::TripletEighth, // 量化到三连音八分音符
                UFrameBasedMusicMap::EQuantizeDirection::Nearest);
            // ... 设置定时器或检查条件，在 QuantizedTriggerTime 到达时触发
        }
    }
}
```

## Demo 示例

以下示例展示了一个简单的 `Actor`，它实现了 `IMusicalAsset` 接口来提供一个硬编码的音乐地图，并可以被播放。

```cpp
// MyHardcodedMusicAsset.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MusicTypes/MusicalAsset.h"
#include "FrameBasedMusicMap.h"
#include "MyHardcodedMusicAsset.generated.h"

UCLASS(BlueprintType)
class MUSICENVIRONMENTTEST_API AMyHardcodedMusicAsset : public AActor, public IMusicalAsset
{
	GENERATED_BODY()

public:
	AMyHardcodedMusicAsset();

	// IMusicMapSource Interface
	virtual void CreateFrameBasedMusicMap(UFrameBasedMusicMap* Map) const override;
	virtual float GetSongLengthSeconds() const override;

protected:
	// IMusicalAsset Interface (需要实现)
	virtual TScriptInterface<IMusicHandle> PrepareToPlay_Internal(UObject* PlaybackContext, UAudioComponent* OnComponent, float FromSeconds, bool IsAudition) override;
	virtual TScriptInterface<IMusicHandle> Play_Internal(UObject* PlaybackContext, UAudioComponent* OnComponent, float FromSeconds, bool IsAudition) override;

private:
	// 一个用于演示的硬编码音乐地图
	UPROPERTY()
	TObjectPtr<UFrameBasedMusicMap> HardcodedMap;
};
```

```cpp
// MyHardcodedMusicAsset.cpp
#include "MyHardcodedMusicAsset.h"
#include "MusicEnvironmentSubsystem.h"

AMyHardcodedMusicAsset::AMyHardcodedMusicAsset()
{
	// 为我们的资产创建一个内嵌的音乐地图
	HardcodedMap = CreateDefaultSubobject<UFrameBasedMusicMap>(TEXT("HardcodedMusicMap"));
	// 在构造函数中无法调用 Init，所以我们在 CreateFrameBasedMusicMap 中初始化
}

void AMyHardcodedMusicAsset::CreateFrameBasedMusicMap(UFrameBasedMusicMap* Map) const
{
	if (Map)
	{
		// 以 48 fps 初始化一个地图，初始速度 100 BPM，4/4 拍
		FFrameRate FrameRate(48, 1);
		Map->SetFrameResolution(FrameRate);
		FFrameBasedTimeSignature InitialTimeSig(4, 4);
		Map->Init(100.0f, InitialTimeSig);

		// 添加一个变化：在第16小节（Bar 15）变为 6/8 拍
		Map->InsertTimeSignature(15, 6, 8);
		// 在第8小节（Bar 7）的第0拍插入一个速度变化为 120 BPM
		// 注意：InsertTempo 的 tick 参数需要计算，这里简化假设 Bar 7 的开始 tick 已知。
		// 实际中应使用 Map 的计算函数来获取精确 tick。
		Map->InsertTempo(Map->MusicalTimeToTick(FMusicalTime(7, 0, Map->GetTicksInBar(7), Map->GetBeatsInBar(7))), 120.0f);
	}
}

float AMyHardcodedMusicAsset::GetSongLengthSeconds() const
{
	// 假设硬编码的歌曲长度为 60 秒
	return 60.0f;
}

// 注意：以下两个内部函数需要返回一个真正的 IMusicHandle 实现。
// 作为演示，它们返回空句柄。在实际插件中，会由 Audio 系统（如 MetaSounds）创建对应的句柄。
TScriptInterface<IMusicHandle> AMyHardcodedMusicAsset::PrepareToPlay_Internal(UObject* PlaybackContext, UAudioComponent* OnComponent, float FromSeconds, bool IsAudition)
{
	// 实际实现会准备音频组件等
	return TScriptInterface<IMusicHandle>();
}

TScriptInterface<IMusicHandle> AMyHardcodedMusicAsset::Play_Internal(UObject* PlaybackContext, UAudioComponent* OnComponent, float FromSeconds, bool IsAudition)
{
	// 实际实现会启动音频播放并返回句柄
	return TScriptInterface<IMusicHandle>();
}
```

## 模块依赖

该插件的独特依赖较少，主要建立在引擎的核心音频和框架之上。

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于通过 `FGameplayTag` 注册和查找带标签的音乐时钟源。 |
| `AudioMixer` | 内部音频处理和混音器支持。 |
| `AudioModulation` | 可能用于动态音乐调制系统。 |
| `MetasoundGraph` | 插件的主要音乐资产（如 MetaSound）基础。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF 格式，属于日志系统维护性更新。 |
| 2025-09-05 | `de978cf7` | Explicitly adding various missing headers to fix non-unity build errors after large CoreUObject chan | 修复因 CoreUObject 大型改动导致的非统一构建头文件缺失错误。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied to | 为相关源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏以优化编译。 |
| 2025-06-23 | `d42c028c` | Music Map Song Length Data | 为音乐地图添加歌曲长度数据支持。 |
| 2025-06-11 | `e0d87df8` | Replace some usages of FORCEINLINE with inline in Audio modules. | 在音频模块中将部分 `FORCEINLINE` 替换为 `inline`。 |

### 维护评价

Music Environment 是一个**较新但处于活跃实验性开发阶段**的插件。

-   **年龄**：创建于 2024 年 12 月，至今约 2 年，是一个相对较新的功能。
-   **活跃度**：从 git log 看，最近一次有实质功能的更新（歌曲长度数据）在 2025 年 6 月，之后主要是维护性提交（修复编译、更新宏）。更新频率适中，表明仍在维护和改进中。
-   **状态**：`EnabledByDefault = false`, `IsBetaVersion = true`, `IsExperimentalVersion = true` 明确表明这是**实验性功能**。这意味着 API 可能不稳定，功能可能不完整，且不建议在生产环境中直接使用。
-   **推荐度**：如果你正在开发一个高度依赖音乐同步的项目（如节奏游戏），并且希望尝试一个由 Epic（Harmonix GenTech）官方提供的集成方案，那么值得在原型阶段尝试和评估此插件。对于生产项目，需要谨慎评估其实验性状态和未来 API 变动的风险。

**警告**：该插件标记为实验性，且近一年来主要更新为维护性修复，未来可能会有重大 API 变更或功能调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MusicEnvironment/Source/MusicEnvironmentTests)