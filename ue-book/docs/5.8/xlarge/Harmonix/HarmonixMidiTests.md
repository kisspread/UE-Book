# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 和声组件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（资产、示例） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 旗下以开发音乐游戏闻名的 Harmonix GenTech 团队开发的音频插件。它并非通用的音频工具，而是一套专门为实现**音乐交互**和**音乐驱动玩法**而设计的底层技术框架。

它解决的核心问题是：如何在虚幻引擎中实现专业级、高精度的音乐处理、同步和交互，超越了简单的音效播放。主要功能包括：

1.  **MIDI 核心支持**：提供在引擎内创建、读取、解析和操作 MIDI 数据的能力，这是音乐交互的基础。
2.  **MetaSound 深度集成**：将音乐处理（如节拍同步、音符事件）作为节点暴露给 MetaSound 图，让作曲家和音频设计师可以用可视化方式构建复杂的音乐逻辑。
3.  **高级音频 DSP（数字信号处理）**：提供 Fusion 等系统，用于实现音高变换、时间拉伸、多采样合成等专业音效。
4.  **音乐同步与调度**：提供精确的基于小节、节拍的时钟和事件调度，让游戏逻辑、动画、特效能与音乐的特定时刻完美同步。

**为什么存在？** 它最初是为《Fortnite Festival》这类音乐游戏服务的，旨在将音乐游戏开发中复杂的节奏同步、音轨切换、玩家输入评估等专业需求，封装成通用的、可集成到引擎中的工具。

## 使用场景

-   **你正在开发节奏游戏（如《Hi-Fi Rush》、《Fortnite Festival》）**：需要精确到毫秒的音乐节拍同步、打击判定和音轨切换。→ 使用 Harmonix 的 MIDI 处理和节拍同步系统。
-   **你的游戏玩法与音乐深度绑定**：例如，场景破坏、角色技能释放、镜头运动需要与音乐的重拍、段落变化同步。→ 使用 Harmonix 的音乐时钟和 MetaSound 事件驱动游戏逻辑。
-   **你需要动态的音乐系统**：背景音乐能根据玩家的战斗状态、探索区域无缝过渡和混合（Horizontal Re-Sequencing）。→ 使用 Harmonix 的多轨音乐管理和调度系统。
-   **你需要对音频进行高级实时处理**：例如，根据游戏参数实时改变乐器的音色、进行变调或变速播放。→ 使用 Harmonix 的 DSP 模块（如 Fusion）。

## 蓝图用法

由于 Harmonix 主要是一个底层运行时框架，其核心 API 通过 C++ 暴露。部分模块（如 `HarmonixMetasound`）会将功能封装为 MetaSound 节点，音频设计师可在 MetaSound 编辑器中使用。

### 核心节点 (MetaSound Nodes)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Harmonix Metasound` 类别下的节点 | 例如节拍检测器、MIDI 事件接收器、音乐时钟等 | 由 `HarmonixMetasound` 模块提供 |
| `Fusion` 类别下的节点 | 用于多采样乐器合成、音高变换等 | 由 `HarmonixDsp` 模块提供 |

### 使用示例（蓝图/编辑器描述）

在 `Harmonix` 插件启用后，你可以在 **MetaSound 编辑器** 中：
1.  在节点搜索栏中搜索 “Harmonix” 或 “Fusion”。
2.  添加“MIDI File Player”或“Music Clock”等节点。
3.  将 MIDI 文件资产连接到播放器节点的输入。
4.  将播放器输出的“MIDI Event”引脚连接到“MIDI to Control”节点，将音符转换为参数。
5.  使用“Music Clock”节点获取当前的小节、节拍信息，并用这些信息驱动其他 MetaSound 节点或蓝图中的游戏逻辑。

## C++ 用法

### 头文件引入

```cpp
// 核心 MIDI 功能
#include "HarmonixMidi/MidiFile.h"
// MetaSound 集成 (通常通过 Subsystem 或直接使用 MetaSound 节点)
// DSP 功能 (如 Fusion)
#include "HarmonixDsp/Fusion/CoalescingFusionSynthesizer.h"
```

### 基本用法（创建和操作 MIDI 文件）

以下示例改编自测试用例 `Private/MidiTestUtility.h`，展示了如何用代码创建一个简单的 MIDI 文件。
*来源：Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests/Private/MidiTestUtility.h*

```cpp
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixMidi/MidiEvent.h"

// 1. 创建一个空的 MIDI 文件：4小节长，1个音轨，4/4拍，120 BPM
UMidiFile* MyMidiFile = Harmonix::Testing::Utility::MidiTestUtility::CreateAndInitializeMidiFile(
    4.0f,       // FileLengthBars: 文件长度（小节数，支持小数）
    1,          // NumTracksIncludingConductor: 包含指挥轨的总音轨数
    4,          // InTimeSigNum: 拍号分子
    4,          // InTimeSigDenom: 拍号分母
    120.0f,     // InTempo: 速度 (BPM)
    true        // PutTextEventOnLastTick: 在最后一拍添加一个文本事件作为标记
);

// 2. 在文件中添加一个音符事件
Harmonix::Testing::Utility::MidiTestUtility::AddNoteOnNoteOffPairToFile(
    MyMidiFile,
    60,         // InNoteNumber: MIDI 音符号 (60 = Middle C)
    100,        // InNoteVelocity: 力度
    0,          // InTrackIndex: 音轨索引
    0,          // InChannel: MIDI 通道
    0,          // AtTick: 开始的 Tick 位置
    480         // DurationTicks: 持续的 Tick 数 (通常1拍=480 ticks)
);

// 此时 MyMidiFile 包含一个从第0拍开始、持续1拍的中央C音符。
// 可以将其保存为 .mid 文件或直接在 MetaSound 的 MIDI 播放器节点中使用。
```

### 进阶用法（集成到游戏逻辑）

更典型的用法是运行时监听 MIDI 事件或音乐节拍。这通常通过监听由 `HarmonixMetasound` 模块提供的 MetaSound 输出或使用其内部的 `MusicClock` 系统。

```cpp
// 假设你有一个播放 Harmonix 音乐的 MetaSound Component
UMetaSoundSourceComponent* MetaSoundComp = GetMetaSoundComponent();

// 通过订阅或轮询 MetaSound 输出的参数，可以获取当前的音乐信息
// 例如，MetaSound 内部可能通过 “BeatCount” 参数输出当前节拍数
// 具体实现依赖于 MetaSound 图的设计
```

## Demo 示例

一个演示如何创建包含多音符 MIDI 序列的最小示例。
*注：此示例基于 `HarmonixMidi` 模块的测试工具函数，实际运行需要启用插件并包含相应模块。*

```cpp
// MidiDemo.h
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MidiDemo.generated.h"

class UMidiFile;

UCLASS()
class UMidiDemoSubsystem : public UGameInstanceSubsystem
{
	GENERATED_BODY()
public:
	virtual void Initialize(FSubsystemCollectionBase& Collection) override;

	// 创建并展示一个演示 MIDI 文件
	UFUNCTION(BlueprintCallable, Category = "MidiDemo")
	void CreateDemoMidiFile();
};

// MidiDemo.cpp
#include "MidiDemo.h"
#include "HarmonixMidi/MidiFile.h"
// 引入测试工具（注意：此工具为测试用途，生产环境应自行封装或使用正式API）
#include "HarmonixMidiTests/Private/MidiTestUtility.h"

void UMidiDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
	Super::Initialize(Collection);
}

void UMidiDemoSubsystem::CreateDemoMidiFile()
{
	using namespace Harmonix::Testing::Utility;

	// 创建一个2小节的MIDI文件，4/4拍，120 BPM
	UMidiFile* DemoFile = MidiTestUtility::CreateAndInitializeMidiFile(2.0f, 2, 4, 4, 120.0f);

	if (DemoFile)
	{
		// 在音轨0，通道0，第0拍添加一个C4音符(音符号60)
		MidiTestUtility::AddNoteOnNoteOffPairToFile(DemoFile, 60, 127, 0, 0, 0, 960); // 持续2拍

		// 在音轨0，通道0，第960 tick（第2拍开始）添加一个E4音符(音符号64)
		MidiTestUtility::AddNoteOnNoteOffPairToFile(DemoFile, 64, 100, 0, 0, 960, 480); // 持续1拍

		// 在音轨1，通道1，第0拍添加一个控制器变化事件(CC#1, Modulation)
		MidiTestUtility::AddCCEventToFile(DemoFile, 1, 64, 1, 1, 0);

		UE_LOG(LogTemp, Log, TEXT("Demo MIDI File created with %d tracks."), DemoFile->GetNumTracks());
		// 在此可以将 DemoFile 保存到磁盘或用于播放
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Harmonix` | 核心运行时模块，提供基础功能和 Subsystem |
| `HarmonixMidi` | MIDI 文件解析和操作的核心模块 |
| `HarmonixMetasound` | 将 Harmonix 功能暴露为 MetaSound 节点的集成模块 |
| `HarmonixDsp` | 提供高级数字信号处理，如 Fusion 合成器 |
| `HarmonixMidiEditor`, `HarmonixMetasoundEditor`, `HarmonixDspEditor` | 提供相应的编辑器扩展、资产类型和自定义面板 |
| `HarmonixMidiTests`, `HarmonixMetasoundTests`, `HarmonixDspTests` | 单元测试模块，**不应**作为运行时依赖 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 Fusion 合成器中音区键位排序问题，并增加防御性代码 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决了与 FSoundWaveData API 废弃相关的合并冲突 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量截断为 float 产生的警告 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association. | 为 FusionPatch 代理添加了用户对象，用于关联活动跟踪 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa. | 修复了格式化字符串中 32 位与 64 位说明符的匹配问题 |

### 维护评价

**活跃维护**。Harmonix 插件正在被 **积极维护和开发**。
-   **年龄**：作为 UE 5.4 (2024年) 引入的较新插件，正处在功能快速迭代期。
-   **更新频率**：近期（2026年5月）有多次提交，修复了多个影响稳定性和兼容性的问题，表明核心团队仍在持续关注。
-   **功能状态**：目前标记为 **实验性** (`IsExperimentalVersion: true`) 且 **默认不启用** (`EnabledByDefault: false`)。这意味着 API 可能发生变化，功能尚未完全稳定，不建议在最终发布产品中依赖其当前状态。
-   **风险与建议**：虽然维护活跃，但其**实验性**标签是明确的警告。如果你的项目依赖其核心功能（特别是节奏游戏），需要准备好应对未来的 API 变更，并密切关注更新日志。适用于原型开发、技术研究或对前沿音频技术有强烈需求的项目。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests) (以MidiTests为例，其他Tests模块结构类似)