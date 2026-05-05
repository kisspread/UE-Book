# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaSound 节点、数据类型、音频资产） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 插件是一个由 Epic Games 旗下 Harmonix GenTech 团队开发的综合性音乐与音频处理工具集。它并非一个简单的音频播放器，而是一套底层框架，旨在为 UE5 的 MetaSound 音频系统提供强大的音乐时间同步、MIDI 处理、音频分析以及高级采样器功能。

该插件的核心价值在于解决以下问题：
1.  **精确的音乐时间同步**：提供 `MidiClock` 等核心概念，使游戏逻辑、视觉效果和音频事件能够与音乐的节拍、小节、时间签名精确同步。
2.  **强大的 MIDI 数据处理流水线**：在 MetaSound 图中提供一系列节点，用于过滤、转置、量化、触发和生成 MIDI 事件流，实现复杂的互动音乐逻辑。
3.  **高级音频分析与效果**：包含 FFT 分析、多频段分析、DJ 滤波器、延迟效果等节点，用于音频可视化或实时音频处理。
4.  **音乐资产抽象**：定义了 `HarmonixMusicAsset` 等资产类型，将 MetaSound 源与 MIDI 文件结合，形成完整的、可同步的音乐作品。

它主要服务于需要高度互动和精确同步的音乐体验，例如音乐游戏、互动音乐系统、音频可视化工具等。

## 使用场景

-   你正在开发一款**节奏游戏**，需要根据玩家的输入在精确的音乐节拍上判定得分 → 使用 `MidiClock`、`MidiQuantizeTriggerNode` 和 `MidiNoteTriggerNode`。
-   你需要创建一个**互动音乐系统**，根据游戏状态（如战斗、探索）无缝切换音乐段落，并保持节拍同步 → 使用 `MidiPlayerNode`、`Transport` 控制节点和 `MidiStream` 处理节点。
-   你正在制作一个**音频可视化工具**，需要实时分析音频的频谱或响度 → 使用 `FFTAnalyzerResult`、`MultibandAnalyzerNode` 和 `PeakNode`。
-   你想在 MetaSound 中实现一个**DJ 风格的滤波器效果** → 使用 `DjFilterNode`。
-   你需要将游戏中的 MIDI 事件**实时录制**到文件中用于调试或创作 → 使用 `MidiStreamWriterNode`。

## 蓝图用法

Harmonix 插件主要通过 MetaSound 节点工作，但也提供了一些用于处理 MetaSound 输出的蓝图函数库。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsTimeSignature` | 检查一个 `FMetaSoundOutput` 是否为时间签名类型 | `UTimeSignatureBlueprintLibrary` |
| `GetTimeSignature` | 从 `FMetaSoundOutput` 中获取时间签名数据 | `UTimeSignatureBlueprintLibrary` |
| `IsMusicTimestamp` | 检查一个 `FMetaSoundOutput` 是否为音乐时间戳类型 | `UMusicTimestampBlueprintLibrary` |
| `GetMusicTimestamp` | 从 `FMetaSoundOutput` 中获取音乐时间戳（小节和拍子） | `UMusicTimestampBlueprintLibrary` |

### 使用示例（蓝图描述）

假设你有一个 MetaSound 源，它输出了当前的音乐时间戳（`FMusicTimestamp`）。你可以在蓝图中这样获取它：

1.  从 MetaSound 组件获取输出（例如通过 `Get MetaSound Output` 节点）。
2.  将输出的 `FMetaSoundOutput` 引用连接到 `UMusicTimestampBlueprintLibrary` 的 `IsMusicTimestamp` 节点进行检查。
3.  如果检查通过，再连接到 `GetMusicTimestamp` 节点，该节点会返回一个 `FMusicTimestamp` 结构体（包含 `Bar` 和 `Beat`）以及一个 `Success` 布尔值。
4.  你可以使用返回的 `Bar` 和 `Beat` 值来驱动 UI 或触发游戏逻辑。

## C++ 用法

Harmonix 的 C++ API 主要用于创建自定义的 MetaSound 节点、操作符或与底层音频线程交互。

### 头文件引入

```cpp
// 核心 MIDI 和 DSP 功能
#include "HarmonixMidi/MidiFile.h"
#include "HarmonixDsp/FusionSampler/FusionPatch.h"

// MetaSound 数据类型和节点
#include "HarmonixMetasound/DataTypes/MidiAsset.h"
#include "HarmonixMetasound/Nodes/MidiPlayerNode.h"
#include "HarmonixMetasound/MidiOps/MidiStreamWriter.h"
```

### 基本用法

以下示例展示了如何使用 `FMidiStreamWriter` 将 MIDI 流写入文件（概念代码，基于头文件推断）：

```cpp
// 假设你有一个 FMidiStream 对象（通常来自 MetaSound 图）
HarmonixMetasound::FMidiStream* MyMidiStream = GetMidiStreamFromSomewhere();

// 创建一个文件归档器
TUniquePtr<FArchive> FileWriter = TUniquePtr<FArchive>(IFileManager::Get().CreateFileWriter(TEXT("Output.mid")));

// 创建 MIDI 流写入器并处理数据
Harmonix::Midi::Ops::FMidiStreamWriter Writer(MoveTemp(FileWriter));
if (MyMidiStream)
{
    Writer.Process(*MyMidiStream);
}
// FileWriter 会在 Writer 析构时自动关闭
```

### 进阶用法

在自定义 MetaSound 节点中使用 `FMidiAsset` 来安全地访问音频线程上的 MIDI 数据：

```cpp
// 在你的 MetaSound 节点操作符类中
class FMyMidiProcessorOperator : public Metasound::FOperator
{
public:
    FMyMidiProcessorOperator(const HarmonixMetasound::FMidiAssetReadRef& InMidiAssetRef)
        : MidiAssetInput(InMidiAssetRef)
    {
    }

    void Execute()
    {
        // 安全地访问 MIDI 数据代理
        const HarmonixMetasound::FMidiAsset& MidiAsset = *MidiAssetInput;
        if (MidiAsset.IsMidiValid())
        {
            const FMidiFileProxy* MidiProxy = MidiAsset.GetMidiProxy().Get();
            // 在音频线程上安全地读取 MIDI 代理数据...
        }
    }

private:
    HarmonixMetasound::FMidiAssetReadRef MidiAssetInput;
};
```

## Demo 示例

一个最小的 C++ 示例，展示如何定义一个使用 `FMidiAsset` 的 MetaSound 节点操作符。

**MyMidiProcessorNode.h**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "MetasoundNodeInterface.h"
#include "HarmonixMetasound/DataTypes/MidiAsset.h"

namespace MyNodes::MidiProcessor
{
    const Metasound::FNodeClassName& GetClassName();

    namespace Inputs
    {
        DECLARE_METASOUND_PARAM_ALIAS(MidiFileAsset);
    }

    namespace Outputs
    {
        // 示例输出：MIDI 文件中的音符数量
        DECLARE_METASOUND_PARAM_EXTERN(NoteCount);
    }
}
```

**MyMidiProcessorNode.cpp**
```cpp
// Copyright Epic Games, Inc. All Rights Reserved.
#include "MyMidiProcessorNode.h"
#include "MetasoundParamHelper.h"
#include "MetasoundVertex.h"

namespace MyNodes::MidiProcessor
{
    using namespace Metasound;

    const FNodeClassName& GetClassName()
    {
        static const FNodeClassName ClassName = { "MyNodes", "MidiProcessor", "" };
        return ClassName;
    }

    // ... (节点注册、工厂类等标准 MetaSound 节点代码) ...

    // 操作符类
    class FMidiProcessorOperator : public FOperator
    {
    public:
        FMidiProcessorOperator(
            const HarmonixMetasound::FMidiAssetReadRef& InMidiAsset,
            const FInt32WriteRef& InOutNoteCount)
            : MidiAssetInput(InMidiAsset)
            , NoteCountOutput(InOutNoteCount)
        {
        }

        virtual void Execute() override
        {
            const HarmonixMetasound::FMidiAsset& Asset = *MidiAssetInput;
            if (Asset.IsMidiValid())
            {
                // 通过代理在音频线程安全访问
                const FMidiFileProxy* Proxy = Asset.GetMidiProxy().Get();
                if (Proxy)
                {
                    // 计算所有轨道的总音符数（示例逻辑）
                    int32 TotalNotes = 0;
                    for (int32 i = 0; i < Proxy->GetNumTracks(); ++i)
                    {
                        TotalNotes += Proxy->GetTrack(i).GetNumNotes();
                    }
                    *NoteCountOutput = TotalNotes;
                }
            }
        }

    private:
        HarmonixMetasound::FMidiAssetReadRef MidiAssetInput;
        FInt32WriteRef NoteCountOutput;
    };
}
```

## 模块依赖

要使用 Harmonix 插件的功能，你的模块通常需要依赖以下模块（根据具体功能选择）：

| 模块 | 用途 |
|---|---|
| `HarmonixMidi` | MIDI 文件解析、数据结构和操作 |
| `HarmonixDsp` | 数字信号处理核心，包括采样器、效果器、分析器 |
| `HarmonixMetasound` | MetaSound 集成，提供节点、数据类型和操作符 |
| `MetasoundFrontend` | MetaSound 前端框架，用于创建自定义节点 |

**注意**：`HarmonixDsp` 和 `HarmonixMetasound` 模块在 Build.cs 中声明了对 `AssetRegistry` 和 `UnrealEd` 的依赖，这表明它们可能包含编辑器工具或资产处理逻辑。在纯运行时模块中引用时需注意。

## 维护状态

### 近期更新

```
- 50fedbc49367 为自定义时钟驱动设置类失败返回有效时钟驱动的情况添加了额外的空值检查和日志记录。
- 8ca2adfc12d4 修复了在时钟的“Reset”中不能直接调用“Seek”的问题。
- 51079168c1af 改进了 MetaSound 节点注册与模块的关联；允许注销 C++ 节点；修复了与新注册机制相关的已弃用代码路径。
```

### 维护评价

Harmonix 是一个相对较新的插件（创建于 2024 年初），目前处于**实验性**阶段（`IsExperimentalVersion: true`，且默认未启用）。从最近的提交记录来看，它仍在**积极维护**中，最近的更新集中在修复关键功能（如时钟重置）、增强系统健壮性（空值检查）以及改进底层架构（节点注册机制）。

**优点**：
-   由 Epic Games 内部专业团队（Harmonix GenTech）开发，技术实力有保障。
-   功能强大且专注，填补了 UE5 在高级音乐互动和同步方面的空白。
-   与 MetaSound 深度集成，符合 UE5 音频系统的发展方向。

**风险与限制**：
-   **实验性**：API 和功能可能在未来版本中发生不兼容的更改。
-   **默认未启用**：需要开发者手动在插件设置中启用，表明 Epic 可能认为其尚未达到面向所有用户的稳定状态。
-   **复杂性高**：涉及音频线程、MIDI 协议和 MetaSound 图形编程，学习曲线较陡。

**推荐**：如果你正在开发对音乐同步和互动性有极高要求的项目（如专业音乐游戏），并且愿意承担实验性 API 可能变化的风险，那么 Harmonix 是一个非常强大且值得投入学习的工具。对于一般性的音频需求，可能使用更成熟、更简单的音频方案更为合适。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests) (HarmonixMetasoundTests 模块)