# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 和声引擎 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、MetaSound节点、MIDI资产处理） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMidi` (Runtime), 以及其他编辑器、测试模块 |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是由 Epic Games 与 Harmonix（知名音乐游戏开发商）合作开发的专业音乐音频工具包。它远不止是一个简单的音频处理插件，而是一个**集成化的音乐交互式音频解决方案**。其核心目的是为游戏和应用提供从底层的 MIDI 解析、音频合成与处理，到高层的 MetaSound 节点系统，一整套用于实现复杂、实时音乐交互的工具。它解决了在 Unreal Engine 中构建节奏游戏、音乐可视化工具或任何需要深度音乐逻辑同步的应用时，所面临的复杂性和性能挑战。

## 使用场景

- **开发节奏/音乐游戏**：例如类似《Rock Band》或《Beat Saber》的游戏，需要精确解析 MIDI 谱面、同步音乐节奏、处理玩家输入并给予实时音频反馈。
- **音乐可视化项目**：基于 MIDI 事件或音频频谱数据，驱动场景中的视觉效果。
- **交互式音乐系统**：根据游戏状态（如战斗、探索）动态混合、切换或处理音乐层，实现自适应音乐。
- **音频创意工具**：在引擎内构建合成器、采样器或效果器链，用于声音设计或现场音乐表演。

## 蓝图用法

Harmonix 作为一套底层音频系统，其蓝图 API 主要通过其子模块（如 `HarmonixMidi`, `HarmonixMetasound`）暴露。由于插件规模庞大，此处提供其核心功能的概览。具体节点请参考各子模块文档。

### 核心功能概览

- **MIDI 文件处理**：加载、解析、创建和操作 MIDI 文件。
- **MetaSound 节点**：提供用于在 MetaSound 图表中处理音乐数据（如 MIDI 事件流、时间同步、节奏信息）的节点。
- **音频合成与处理**：提供专业的音频 DSP 功能模块。

### 使用示例（蓝图描述）

要实现一个简单的节拍同步逻辑，你可能会：
1.  使用 `HarmonixMidi` 模块中的节点加载一个包含鼓点轨道的 `.mid` 文件。
2.  通过解析后的 MIDI 事件流，获取每个节拍的精确时间点。
3.  将时间点数据输入到 `HarmonixMetasound` 的 MetaSound 图表中，驱动一个触发音频样本的节点。
4.  在游戏代码中，监听 MIDI 的节拍事件，同步播放动画或 UI 特效。

## C++ 用法

### 头文件引入

根据具体使用的子模块，引入相应的头文件，例如：
```cpp
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixDsp/AudioUtility.h"
```

### 基本用法

以下示例基于测试工具 `MidiTestUtility` 展示如何程序化创建 MIDI 数据：

**来源文件**: `Private/MidiTestUtility.h`

```cpp
#include "HarmonixMidi/MidiFile.h"
// ... 其他必要的 Harmonix 头文件

namespace Harmonix::Testing::Utility::MidiTestUtility
{
    // 创建一个空白的 MIDI 文件
    UMidiFile* TestMidi = CreateAndInitializaMidiFile(
        4.0f,   // 文件长度：4小节
        1,      // 包含1个MIDI通道
        2,      // 2个音轨（通常含一个Conductor轨）
        4,      // 4/4拍
        120     // 120 BPM
    );

    // 在小节1.0，通道0，音轨1上添加一个中央C音符，持续1拍（假设时间分辨率允许）
    AddNoteOnNoteOffPairToFile(
        TestMidi,
        60,     // MIDI音符号 (中央C)
        100,    // 力度
        1,      // 音轨索引
        0,      // MIDI通道
        0,      // 起始Tick (假设从0开始)
        960     // 持续时长Tick (1拍=960ticks @480PPQ)
    );
}
```

### 进阶用法

结合多个子模块，可以实现更复杂的功能，例如创建一个自定义的 MetaSound 节点来处理 MIDI 音符：

```cpp
// 在自定义的 MetaSound 节点或外部处理逻辑中
#include "HarmonixMetasound/MidiStepSequencerNode.h" // 假设的节点
#include "HarmonixMidi/MidiEventStream.h"

// 处理传入的 MIDI 事件流
void ProcessMidiStream(const FMidiEventStream& InStream)
{
    for (const auto& Event : InStream)
    {
        if (Event.IsNoteOn())
        {
            // 根据音符音高和力度，触发不同的音频合成参数
            TriggerSynthNote(Event.GetNoteNumber(), Event.GetVelocity());
        }
        // ... 处理其他事件类型
    }
}
```

## Demo 示例

一个创建 MIDI 文件并添加事件的最小 C++ 示例：

**MidiFileDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class UMidiFile;

class FMidiFileDemo
{
public:
    static UMidiFile* CreateDemoMidiFile();
};
```

**MidiFileDemo.cpp**
```cpp
#include "MidiFileDemo.h"
#include "HarmonixMidi/MidiFile.h" // 需要链接 HarmonixMidi 模块

UMidiFile* FMidiFileDemo::CreateDemoMidiFile()
{
    // 1. 创建一个 2 小节，120 BPM，4/4 拍的 MIDI 文件
    UMidiFile* DemoFile = UMidiFile::Create(2.0f, 2, 4, 4, 120.0f);
    
    if (DemoFile)
    {
        // 2. 在第1小节第1拍添加一个中央C (Note 60)
        const int32 TickPerBeat = DemoFile->GetTicksPerQuarterNote();
        const int32 NoteOnTick = 0; // 第一小节第1拍
        const int32 NoteDuration = TickPerBeat; // 持续1拍

        // 构造 Note On 和 Note Off 事件并添加到音轨1，通道0
        // 具体API请参考 HarmonixMidi 模块文档
    }
    
    return DemoFile;
}
```

## 模块依赖

要使用 Harmonix 的功能，你的模块需要依赖以下 **独特** 模块（除了标准的 Core/Engine/Slate）：

| 模块 | 用途 |
|---|---|
| `HarmonixMidi` | 处理 MIDI 文件的解析、创建和操作。 |
| `HarmonixDsp` | 提供底层的数字信号处理（DSP）工具和音频合成器框架。 |
| `HarmonixMetasound` | 为 MetaSound 系统提供音乐相关的节点和控制器。 |
| `MetasoundFrontend` | MetaSound 图表系统的前端框架（HarmonixMetasound 的基础）。 |
| `Harmonix` | 核心运行时模块，提供基础音乐时钟、同步和 utilities。 |
| `AssetRegistry` | （通过子模块依赖）用于管理和查找资产。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复音频合成器中键区域排序问题并增加空值防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 废弃相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量转浮点的警告。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in associ... | 为 FusionPatch 代理添加用户对象，可用于跟踪活动关联。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正32位格式说明符以匹配64位参数。 |

### 维护评价

Harmonix 插件**处于积极维护中**。尽管标记为实验性且默认未启用，但自2024年创建以来，其代码库（尤其是核心的 `HarmonixDsp` 和 `Harmonix` 模块）一直有持续的功能增强和稳定性修复（如最近的合并冲突解决、音频合成器修复）。最近的更新集中在底层音频引擎的健壮性和 API 适配上。作为 Epic 官方与专业音乐技术公司合作的项目，其长期支持有保障。**推荐**对音乐交互有深度需求的开发者评估和使用，但需接受其“实验性”标签可能带来的 API 变动风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]() （暂无）
- [测试用例]() (测试模块位于各子目录，如 `HarmonixMidiTests`, `HarmonixMetasoundTests`)