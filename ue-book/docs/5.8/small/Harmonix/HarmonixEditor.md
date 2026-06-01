# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频工具包 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板等） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是 Epic Games 旗下 Harmonix 团队（以音乐游戏如《Rock Band》、《Guitar Hero》闻名）开发的音乐相关音频功能集合。它并非简单的音频播放器，而是一个用于构建复杂音乐交互系统的核心引擎层。其核心价值在于将音乐理论（如节拍、小节、调性）与游戏逻辑深度集成，是开发音乐节奏游戏、互动音乐系统（如动态混音、音乐事件驱动）以及高级音频分析可视化的基石。它在引擎层面实现了类似 “Music Macro Language (MML)” 的功能。

## 使用场景

-   **音乐节奏游戏开发**：你需要精确的时间同步、音乐事件触发、以及基于乐谱的玩法判定时，使用 Harmonix 的序列器和 MIDI 功能。
-   **互动音乐系统**：你希望游戏音乐能根据玩家行为、游戏状态实时变化（如无缝过渡、分支、动态增减乐器轨道），使用 Harmonix 的序列器、Fusion 音源和事件系统。
-   **音频可视化与分析**：你需要提取音频的特征（如节拍、能量、频谱）用于视觉反馈或游戏玩法，使用 Harmonix 的 DSP 分析节点。

## 蓝图用法

Harmonix 提供了丰富的蓝图节点，主要集中在音乐序列控制、MIDI 处理和 MetaSound 集成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MML Sequence Player` | 创建一个基于 MML（音乐宏语言）语法的序列器播放器，用于驱动音乐播放和事件。 | `HarmonixSubsystem` |
| `Load MIDI File` | 异步加载一个 MIDI 文件，并将其解析为 Harmonix 内部可操作的 MIDI 数据对象。 | `HarmonixSubsystem` |
| `Create Fusion Sound Source` | 创建一个 Fusion 音源，它是 Harmonix 的核心音频资产，支持基于键位（Key Zone）的多层采样。 | `FusionSoundSourceFactory` |
| `Create Tempo Sync Driver` | 创建一个节奏同步驱动器，用于将外部事件（如按键）与音乐时钟进行对齐和同步。 | `HarmonixSubsystem` |
| `Get Audio Feature` | 从音频流中提取指定的特征（如平均能量、低频能量），用于驱动视觉效果。 | `AudioAnalyzerSubsystem` |

### 使用示例（蓝图描述）

1.  **播放一段循环音乐**：
    *   使用 `Load MIDI File` 节点加载包含你编写的音乐信息的 MIDI 文件。
    *   使用 `Create MML Sequence Player` 节点创建一个序列器。
    *   将加载好的 MIDI 文件作为 `MidiAsset` 输入连接到序列器。
    *   在 `BeginPlay` 中调用序列器的 `Play` 节点开始播放。
    *   可以连接到序列器的 `On Beat` 或 `On Bar` 事件，在游戏中的特定节拍触发逻辑（如生成障碍物）。

2.  **根据玩家得分动态改变音乐强度**：
    *   创建两个不同的 Fusion 音源：一个用于“基础”强度，另一个用于“高潮”强度。
    *   使用两个 `Create MML Sequence Player` 节点，分别加载为这两种强度编写的 MIDI/乐谱。
    *   当玩家得分达到阈值时，淡出“基础”序列器，同时淡入“高潮”序列器，实现动态混音。

## C++ 用法

### 头文件引入

```cpp
#include "Harmonix/HarmonixSubsystem.h"
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixDsp/Fusion/FusionSoundSource.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码加载 MIDI 文件并播放序列。
*（来源：HarmonixMidiTests/Private/MidiFileTest.cpp）*

```cpp
// 获取 Harmonix 子系统
UHarmonixSubsystem* HarmonixSubsystem = GetWorld()->GetSubsystem<UHarmonixSubsystem>();
if (!HarmonixSubsystem) return;

// 异步加载 MIDI 文件（通过 FSoftObjectPath）
FSoftObjectPath MidiAssetPath(TEXT("/Game/Music/MySong.MySong"));
HarmonixSubsystem->LoadMidiFileAsync(MidiAssetPath, 
    FOnMidiFileLoaded::CreateLambda([this, HarmonixSubsystem](const UMidiFile* LoadedMidiFile)
    {
        if (LoadedMidiFile)
        {
            // 加载成功，创建并播放序列器
            UHarmonixSequencePlayer* Player = HarmonixSubsystem->CreateSequencePlayer(LoadedMidiFile);
            if (Player)
            {
                Player->Play();
                UE_LOG(LogTemp, Log, TEXT("MIDI sequence started playing."));
            }
        }
    }));
```

### 进阶用法

以下示例展示了如何将自定义的 Fusion 音源分配给序列器的某个音轨，以实现自定义乐器音色。
*（参考：HarmonixMetasound 和 Fusion 相关测试思路）*

```cpp
// 1. 加载或创建一个 Fusion 音源资产
UFusionSoundSource* FusionSource = LoadObject<UFusionSoundSource>(nullptr, TEXT("/Game/Sounds/MyFusionPreset"));

// 2. 获取正在播放的序列器（假设已有 Player 指针）
UHarmonixSequencePlayer* Player = ...; // 从子系统获取

// 3. 获取序列器音轨信息并设置 Fusion 音源
// 注意：这通常需要在加载 MIDI 文件后、播放前，根据音轨索引或名称来设置
int32 TrackIndex = 1; // 例如，为第二条音轨设置
Player->SetFusionSourceForTrack(TrackIndex, FusionSource);

// 4. 开始播放
Player->Play();
```

## Demo 示例

一个可编译的最小示例，展示如何在游戏模式中启动一个简单的 Harmonix 音乐序列。

**MyGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

class UHarmonixSubsystem;
class UHarmonixSequencePlayer;

UCLASS()
class MYPROJECT_API AMyGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	virtual void StartPlay() override;

private:
	UPROPERTY()
	TObjectPtr<UHarmonixSequencePlayer> CurrentPlayer;

	UFUNCTION()
	void OnMidiLoaded(const UMidiFile* LoadedMidiFile);
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "Harmonix/HarmonixSubsystem.h"
#include "HarmonixMidi/MidiFile.h"
#include "Kismet/GameplayStatics.h"

void AMyGameMode::StartPlay()
{
	Super::StartPlay();

	// 确保子系统可用
	UHarmonixSubsystem* HarmonixSS = GetWorld()->GetSubsystem<UHarmonixSubsystem>();
	if (!HarmonixSS)
	{
		UE_LOG(LogTemp, Error, TEXT("HarmonixSubsystem not found!"));
		return;
	}

	// 异步加载 MIDI 文件
	FSoftObjectPath TestMidiPath(TEXT("/Game/Music/TestSong.TestSong"));
	HarmonixSS->LoadMidiFileAsync(TestMidiPath, 
		FOnMidiFileLoaded::CreateUObject(this, &AMyGameMode::OnMidiLoaded));
}

void AMyGameMode::OnMidiLoaded(const UMidiFile* LoadedMidiFile)
{
	if (!LoadedMidiFile)
	{
		UE_LOG(LogTemp, Warning, TEXT("Failed to load MIDI file."));
		return;
	}

	UHarmonixSubsystem* HarmonixSS = GetWorld()->GetSubsystem<UHarmonixSubsystem>();
	if (!HarmonixSS) return;

	// 创建序列器并播放
	CurrentPlayer = HarmonixSS->CreateSequencePlayer(LoadedMidiFile);
	if (CurrentPlayer)
	{
		// 设置循环播放
		CurrentPlayer->SetLooping(true);
		CurrentPlayer->Play();
		UE_LOG(LogTemp, Log, TEXT("Harmonix demo sequence is now playing."));
	}
}
```

## 模块依赖

要使用 Harmonix 插件的功能，你的游戏模块通常需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `Harmonix` | 核心子系统、序列器接口 |
| `HarmonixMidi` | MIDI 文件解析和数据操作 |
| `HarmonixDsp` | Fusion 音源、音频处理 DSP 核心 |
| `HarmonixMetasound` | 提供与 MetaSound 系统集成的节点和功能 |
| `MetaSoundEngine` | *(常见依赖，但 Harmonix 的 MetaSound 节点依赖它)* |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 音源中键区分配的顺序问题，并增加防御性空值检查。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下 double 常量截断为 float 产生的编译警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为 FusionPatch 代理添加用户对象，用于在关联任务中跟踪活动。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中32位/64位整型说明符不匹配的问题。 |

### 维护评价

-   **年龄**：插件于 2024 年初进入 Engine 目录，非常年轻，处于积极开发期。
-   **更新频率与内容**：从提交记录看，维护非常活跃。最近的提交（2026年5月）仍在进行核心功能的Bug修复（如 Fusion 音源）、API 兼容性维护和代码健壮性提升。
-   **状态**：**活跃维护中**。作为 Epic Games 第一方（Harmonix）开发并集成到引擎的核心音频工具包，其持续性有保障。
-   **限制**：插件标记为 **实验性 (IsExperimentalVersion=true)**，且 **默认未启用**。这意味着其 API 未来可能发生变化，需要开发者手动在插件列表中启用。
-   **推荐度**：**强烈推荐**给需要开发音乐驱动或深度互动音频系统的游戏项目。尽管是实验性的，但其底层由专业团队维护，是目前 UE5 中实现高级音乐游戏逻辑最成熟的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]（暂无）