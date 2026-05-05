# Harmonix

> A package of Harmonix music related audio functionality.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（音频资产、MIDI 资产、MetaSound 节点） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix) | |

---

## 用途

Harmonix 是由 Epic Games 旗下 Harmonix GenTech 团队开发的**音乐与音频功能工具包**。Harmonix 是著名的音乐游戏（Rock Band、Guitar Hero）背后的音乐技术公司，被 Epic 收购后将其核心音频技术整合进了 UE5。

该插件解决的核心问题：

1. **MIDI 解析与处理**（`HarmonixMidi`）：提供完整的 MIDI 文件解析、音符事件处理、节拍/小节映射能力，让游戏可以精确地将音频事件与音乐时间轴对齐
2. **DSP 音频处理**（`HarmonixDsp`）：提供专业的数字信号处理工具，包括 ADSR 包络生成、音频缓冲区对齐处理等音乐游戏常用的 DSP 功能
3. **MetaSound 集成**（`HarmonixMetasound`）：将 Harmonix 的音乐处理能力以 MetaSound 节点的形式暴露，可在 MetaSound 图中直接使用 MIDI 驱动的音频处理
4. **编辑器工具**（`HarmonixEditor`、`HarmonixDspEditor` 等）：提供编辑器内的资产操作、预览和调试工具

**为什么存在**：音乐游戏（rhythm game）需要精确的音乐时间同步、MIDI 事件驱动、实时 DSP 处理等专业音频能力。UE5 原生音频系统不提供这些功能，Harmonix 插件填补了这一空白。即使不做音乐游戏，任何需要 MIDI 驱动或精确音乐同步的项目（如交互式音乐系统、音乐可视化）都能从中受益。

---

## 使用场景

- 你在做一个**音乐节奏游戏**（类似 Rock Band）→ 用 HarmonixMidi 解析音轨，用 HarmonixDsp 处理音频反馈
- 你需要**MIDI 文件驱动游戏事件**（如音符打击判定）→ 用 HarmonixMidi 解析 MIDI 并映射到游戏时间轴
- 你想在 **MetaSound 图中使用 MIDI 数据**→ 用 HarmonixMetasound 提供的 MetaSound 节点
- 你需要**实时 ADSR 包络生成**用于音频可视化或合成→ 用 HarmonixDsp 的包络工具
- 你在构建**交互式音乐系统**（音乐随游戏状态变化）→ Harmonix 提供音乐时间同步基础设施

---

## 蓝图用法

> ⚠️ 本插件为实验性插件，大部分 API 以 C++ 为主。以下为从源码中提取的公开蓝图接口。

### 核心节点

由于 HarmonixDspEditor 模块主要提供编辑器工具函数（C++ 命名空间函数），蓝图可直接调用的节点较少。主要的蓝图接口分布在 `Harmonix` 和 `HarmonixMetasound` 模块中。

| 节点 | 说明 | 所在类 |
|---|---|---|
| ADSR 包络生成 | 根据 ADSR 参数生成音频包络缓冲区（编辑器工具） | `Harmonix::Dsp::Editor` |

### 使用示例（蓝图描述）

HarmonixDspEditor 提供的 ADSR 包络生成主要用于编辑器预览场景：

1. 创建一个 `FAdsrSettings` 结构体，设置 Attack、Decay、Sustain、Release 参数
2. 调用 `GenerateAdsrEnvelope` 生成对应的浮点音频缓冲区
3. 该缓冲区可用于波形预览显示或导出

---

## C++ 用法

### 头文件引入

```cpp
// DSP 编辑器工具
#include "HarmonixDspEditorUtils.h"

// ADSR 设置（来自 HarmonixDsp 模块）
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
```

### 基本用法：生成 ADSR 包络

以下示例展示如何使用 HarmonixDspEditor 生成 ADSR 包络缓冲区：

```cpp
// 来源: Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspEditor/Public/HarmonixDspEditorUtils.h

#include "HarmonixDspEditorUtils.h"
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
#include "DSP/AlignedBuffer.h"

void GeneratePreviewEnvelope()
{
    // 1. 配置 ADSR 参数
    FAdsrSettings AdsrSettings;
    AdsrSettings.AttackTimeMs = 10.0f;    // 起音时间 10ms
    AdsrSettings.DecayTimeMs = 50.0f;     // 衰减时间 50ms
    AdsrSettings.SustainLevel = 0.7f;     // 持续电平 70%
    AdsrSettings.ReleaseTimeMs = 100.0f;  // 释音时间 100ms

    // 2. 设置参数
    const float SustainTime = 1.0f;       // 持续阶段持续 1 秒
    const float SampleRate = 48000.0f;    // 采样率 48kHz

    // 3. 生成包络缓冲区
    Audio::FAlignedFloatBuffer EnvelopeBuffer;
    Harmonix::Dsp::Editor::GenerateAdsrEnvelope(
        AdsrSettings,
        SustainTime,
        SampleRate,
        EnvelopeBuffer
    );

    // EnvelopeBuffer 现在包含完整的 ADSR 包络波形数据
    // 可用于编辑器中的波形预览绘制
}
```

### 进阶用法：结合 MetaSound 使用

Harmonix 的真正威力在于将 DSP 处理与 MetaSound 图结合。典型的进阶工作流：

```cpp
// 1. 通过 HarmonixMidi 解析 MIDI 文件获取音符事件
// 2. 使用 HarmonixDsp 进行实时音频处理
// 3. 通过 HarmonixMetasound 将处理节点暴露到 MetaSound 图
// 4. 在编辑器中使用 HarmonixDspEditor 预览包络效果

// 编辑器预览工作流示例
#include "HarmonixDspEditorUtils.h"

void PreviewMultipleEnvelopes()
{
    // 为不同乐器生成不同的包络预览
    TArray<FAdsrSettings> InstrumentEnvelopes;

    // 钢琴：快速起音，中等衰减
    FAdsrSettings Piano;
    Piano.AttackTimeMs = 5.0f;
    Piano.DecayTimeMs = 300.0f;
    Piano.SustainLevel = 0.4f;
    Piano.ReleaseTimeMs = 200.0f;
    InstrumentEnvelopes.Add(Piano);

    // 弦乐：慢起音，高持续
    FAdsrSettings Strings;
    Strings.AttackTimeMs = 100.0f;
    Strings.DecayTimeMs = 50.0f;
    Strings.SustainLevel = 0.9f;
    Strings.ReleaseTimeMs = 500.0f;
    InstrumentEnvelopes.Add(Strings);

    // 为每个乐器生成包络预览
    for (const FAdsrSettings& Settings : InstrumentEnvelopes)
    {
        Audio::FAlignedFloatBuffer Buffer;
        Harmonix::Dsp::Editor::GenerateAdsrEnvelope(
            Settings, 2.0f, 48000.0f, Buffer
        );
        // 将 Buffer 传递给编辑器 UI 进行波形绘制
    }
}
```

---

## Demo 示例

以下是一个最小可编译示例，展示如何在编辑器工具中使用 HarmonixDspEditor 生成 ADSR 包络：

### MyHarmonixTool.h

```cpp
// MyHarmonixTool.h
#pragma once

#include "CoreMinimal.h"

class FMyHarmonixTool
{
public:
    /** 生成指定乐器的 ADSR 包络并返回采样数据 */
    static TArray<float> GenerateInstrumentEnvelope(
        float AttackMs, float DecayMs, float SustainLevel, float ReleaseMs,
        float SustainDurationSec = 1.0f, float SampleRate = 48000.0f);
};
```

### MyHarmonixTool.cpp

```cpp
// MyHarmonixTool.cpp
#include "MyHarmonixTool.h"
#include "HarmonixDspEditorUtils.h"
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
#include "DSP/AlignedBuffer.h"

TArray<float> FMyHarmonixTool::GenerateInstrumentEnvelope(
    float AttackMs, float DecayMs, float SustainLevel, float ReleaseMs,
    float SustainDurationSec, float SampleRate)
{
    FAdsrSettings Settings;
    Settings.AttackTimeMs = AttackMs;
    Settings.DecayTimeMs = DecayMs;
    Settings.SustainLevel = SustainLevel;
    Settings.ReleaseTimeMs = ReleaseMs;

    Audio::FAlignedFloatBuffer AlignedBuffer;
    Harmonix::Dsp::Editor::GenerateAdsrEnvelope(
        Settings, SustainDurationSec, SampleRate, AlignedBuffer);

    // 转换为普通 TArray 以便在编辑器 UI 中使用
    TArray<float> Result;
    Result.SetNumUninitialized(AlignedBuffer.Num());
    FMemory::Memcpy(Result.GetData(), AlignedBuffer.GetData(),
                     AlignedBuffer.Num() * sizeof(float));

    return Result;
}
```

---

## 模块依赖

HarmonixDspEditor 模块的依赖：

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | ADSR 设置结构体、DSP 核心处理功能 |
| `AssetRegistry` | 资产注册与发现（编辑器集成） |
| `UnrealEd` | 编辑器框架支持 |

> 注：Harmonix 插件整体还依赖 `HarmonixMidi`（MIDI 解析）、`HarmonixMetasound`（MetaSound 集成）等内部模块，但这些是插件内部依赖，使用者无需额外配置。

---

## 模块结构概览

由于 Harmonix 是 xlarge 级插件（722 个源文件），以下是各子模块的功能划分：

| 模块 | 类型 | 功能 |
|---|---|---|
| `Harmonix` | Runtime | 核心模块，基础音乐时间同步功能 |
| `HarmonixDsp` | Runtime | DSP 音频处理（ADSR、滤波器、缓冲区处理） |
| `HarmonixDspEditor` | Runtime | DSP 编辑器工具（包络预览等） |
| `HarmonixDspTests` | Runtime | DSP 模块单元测试 |
| `HarmonixEditor` | Runtime | 编辑器集成（资产操作、右键菜单） |
| `HarmonixMetasound` | Runtime | MetaSound 节点集成（MIDI 驱动音频节点） |
| `HarmonixMetasoundEditor` | Runtime | MetaSound 编辑器扩展 |
| `HarmonixMetasoundTests` | Runtime | MetaSound 模块单元测试 |
| `HarmonixMidi` | Runtime | MIDI 文件解析与处理 |
| `HarmonixMidiEditor` | Runtime | MIDI 资产编辑器工具 |
| `HarmonixMidiTests` | Runtime | MIDI 模块单元测试 |

---

## 维护状态

### 近期更新

```
- 9803c43 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
- 800d7a5 Implement feedback & additional tidbits for right-click audio actions including - Clean-up/deprecation of USoundSimple - Shift-right click feature to sort sound/playback actions to top or bottom of right click list and show deprecated options (currently just USoundSimple) if deprecated (also in audio editor user settings) - Utilize asset definition code to keep sections organized and accessible via menu accessor keyed off class type - Rename "ReferencedPreset" to "ParentPreset"
- 2739c3d Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
```

### 维护评价

- **创建时间**：2024 年 1 月，约 2 年历史，属于较新的插件
- **实验性状态**：`IsExperimentalVersion=true`，`EnabledByDefault=false`，表明 Epic 仍在迭代中，API 可能发生变化
- **维护活跃度**：近期 commit 主要是代码质量改进（DLL 导出修正、内联宏添加）和编辑器体验优化，说明仍在积极维护
- **规模庞大**：722 个源文件、11 个模块，表明这是一个功能完整的专业音频工具包
- **已知限制**：
  - 实验性插件，API 不保证向后兼容
  - 需要手动启用（`EnabledByDefault=false`）
  - 部分模块依赖 `UnrealEd`，打包时需注意模块类型配置

**推荐程度**：⭐⭐⭐⭐ 如果你的项目涉及 MIDI 处理、音乐同步或交互式音乐系统，这是目前 UE5 中最专业的解决方案。但由于是实验性状态，建议在生产环境中谨慎使用，密切关注版本更新。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix)
- [HarmonixDspEditor 源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspEditor)
- [HarmonixDspTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixDspTests)
- [HarmonixMetasoundTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMetasoundTests)
- [HarmonixMidiTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Harmonix/Source/HarmonixMidiTests)