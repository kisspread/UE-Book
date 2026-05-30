# Harmonix

> A package of Harmonix music related audio functionality.

| 属性 | 值 |
|---|---|
| 中文名 | 音乐音频套件 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（FusionPatch音色、MIDI相关资产、MetaSound节点） |
| 模块 | `Harmonix` (Runtime), `HarmonixDsp` (Runtime), `HarmonixDspEditor` (Runtime), `HarmonixDspTests` (Runtime), `HarmonixEditor` (Runtime), `HarmonixMetasound` (Runtime), `HarmonixMetasoundEditor` (Runtime), `HarmonixMetasoundTests` (Runtime), `HarmonixMidi` (Runtime), `HarmonixMidiEditor` (Runtime), `HarmonixMidiTests` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2024-01-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix) | |

## 用途

Harmonix 是一个为 Unreal Engine 提供专业级音乐和音频处理功能的插件包。它不仅仅是通用音频工具，而是专注于解决与**音乐性**、**节奏同步**和**乐器式采样**相关的问题。其核心目标是为游戏提供内置的、高度集成的音乐理论引擎和 DSP（数字信号处理）工具。

从源码分析，其具体用途包括：
1.  **创建和编辑 FusionPatch**：一种专有的、高级的采样器音色格式（类似 Kontakt 的乐器），支持从音频样本自动生成多区映射、ADSR 包络、滤波器等复杂 DSP 链。
2.  **处理 MIDI 数据**：提供底层 MIDI 解析、映射和实时操控能力，常用于音乐游戏的节奏判定、音符生成或视觉反馈同步。
3.  **集成 MetaSound**：将音乐相关的处理逻辑（如音高移调、时间拉伸、节拍器）封装为 MetaSound 节点，实现可视化、可数据驱动的音频处理管线。
4.  **提供音乐理论工具**：如音符解析、音阶映射、键区排序等，帮助开发者轻松处理音乐逻辑而无需深厚的音频工程知识。

## 使用场景

-   你正在制作一个类似《摇滚乐队》或《吉他英雄》的**音乐节奏游戏**，需要精确处理乐器样本、同步音符判定 → 使用 `HarmonixDsp` 和 `HarmonixMidi` 模块。
-   你需要为游戏内的可演奏乐器（如钢琴、鼓机）创建**多层、多速度响应的复杂音色** → 使用 `HarmonixDspEditor` 中的 FusionPatch 创建工具。
-   你想要用**可视化节点图**（MetaSound）来搭建音乐特效，例如节拍同步的滤波器扫描或和声器 → 使用 `HarmonixMetasound` 模块提供的节点。
-   你的游戏需要读取外部 **MIDI 文件**来驱动剧情事件或背景音乐 → 使用 `HarmonixMidi` 模块进行解析和事件触发。

## 蓝图用法

Harmonix 的蓝图 API 主要分布在运行时模块中，提供音乐数据查询和实时控制。`HarmonixDspEditor` 作为编辑器模块，主要用于资产创建和属性自定义，其公开的蓝图节点较少。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GenerateAdsrEnvelope` | 根据 ADSR 设置生成一个音频包络数据缓冲区，可用于可视化或进一步处理。 | `Harmonix::Dsp::Editor` (命名空间函数) |

*注意：更丰富的音频播放、MIDI 处理和 MetaSound 节点蓝图 API 存在于 `HarmonixDsp`、`HarmonixMidi` 和 `HarmonixMetasound` 运行时模块中。*

### 使用示例（蓝图描述）

1.  **生成 ADSR 包络波形**：你可以使用一个“Begin Play”事件，调用 `GenerateAdsrEnvelope` 节点，传入一个配置好的 `ADSR Settings` 结构体（例如快速起音、长释音）。将生成的缓冲区数据通过一个“Draw Debug Lines”节点绘制出来，以实时可视化包络形状，用于调试声音设计。

## C++ 用法

### 头文件引入

```cpp
#include "HarmonixDspEditorModule.h"
#include "HarmonixDspEditorUtils.h" // 用于 ADSR 包络生成
```

### 基本用法

`HarmonixDspEditor` 模块主要提供编辑器扩展功能，运行时音频处理能力由 `HarmonixDsp` 等模块提供。以下是使用其工具函数生成 ADSR 包络的示例。

```cpp
// 来源: Public/HarmonixDspEditorUtils.h
// 用途：在编辑器工具或测试中生成音频包络数据

#include "HarmonixDspEditorUtils.h"
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
#include "DSP/AlignedBuffer.h"

// 假设我们有一个编辑器工具或自动化测试
void CreateTestEnvelope()
{
    // 1. 定义 ADSR 参数
    FAdsrSettings AdsrSettings;
    AdsrSettings.AttackTime = 0.01f;  // 10ms 起音
    AdsrSettings.DecayTime = 0.1f;    // 100ms 衰减
    AdsrSettings.SustainLevel = 0.7f; // 保持音量 70%
    AdsrSettings.ReleaseTime = 0.5f;  // 500ms 释音

    // 2. 准备输出缓冲区
    Audio::FAlignedFloatBuffer EnvelopeBuffer;
    float SampleRate = 48000.0f;
    float SustainDuration = 2.0f; // 保持阶段持续 2 秒

    // 3. 生成包络
    Harmonix::Dsp::Editor::GenerateAdsrEnvelope(
        AdsrSettings,
        SustainDuration,
        SampleRate,
        EnvelopeBuffer
    );

    // 4. (示例) 将 EnvelopeBuffer 用于后续处理或可视化
    // 例如，将其写入一个 .wav 文件或绘制图表
}
```

### 进阶用法

虽然 `HarmonixDspEditor` 的主要功能（如 FusionPatch 导入/创建）是通过其内部类（如 `UFusionPatchAssetFactory`, `FFusionPatchJsonImporter`）和 UI 定制（`IDetailCustomization`）实现的，但理解其设计模式有助于扩展。
-   **扩展资产类型**：可以参考 `UAssetDefinition_FusionPatch` 的模式，为自定义的音频资产类型创建定义，控制其在内容浏览器中的显示、颜色和分类。
-   **创建自定义属性面板**：通过继承 `IPropertyTypeCustomization`，你可以为复杂的自定义结构体（类似 `FPannerDetails` 或 `FTypedParameter`）创建直观的编辑器界面。

## Demo 示例

以下是一个最小化的编辑器工具模块示例，展示了如何集成 `HarmonixDspEditor` 模块并生成一个 ADSR 包络。这不是一个完整游戏，而是编辑器扩展的一部分。

**MyHarmonixTool.h**
```cpp
#pragma once
#include "CoreMinimal.h"

class FMyHarmonixTool
{
public:
    static void RunAdsrDemo();
};
```

**MyHarmonixTool.cpp**
```cpp
#include "MyHarmonixTool.h"
#include "HarmonixDspEditorUtils.h"
#include "HarmonixDsp/Modulators/Settings/AdsrSettings.h"
#include "DSP/AlignedBuffer.h"

void FMyHarmonixTool::RunAdsrDemo()
{
    // 配置一个 Pad（铺垫）音色的包络：长起音，无衰减，长保持，长释音
    FAdsrSettings PadSettings;
    PadSettings.AttackTime = 1.0f;     // 1秒起音
    PadSettings.DecayTime = 0.0f;      // 无衰减阶段
    PadSettings.SustainLevel = 1.0f;   // 满音量保持
    PadSettings.ReleaseTime = 3.0f;    // 3秒释音

    Audio::FAlignedFloatBuffer PadEnvelope;
    float SampleRate = 44100.0f;
    float SustainTime = 5.0f; // 保持 5 秒

    // 生成包络
    Harmonix::Dsp::Editor::GenerateAdsrEnvelope(
        PadSettings,
        SustainTime,
        SampleRate,
        PadEnvelope
    );

    // 这里，PadEnvelope 包含了完整的包络数据。
    // 在编辑器中，你可以将它用于预览、写入资产或发送到其他音频系统。
    UE_LOG(LogTemp, Log, TEXT("Generated ADSR envelope with %d samples."), PadEnvelope.Num());
}
```

## 模块依赖

要使用 `HarmonixDspEditor` 模块的功能（如生成 ADSR 包络），你的模块需要依赖它及其运行时库。

| 模块 | 用途 |
|---|---|
| `HarmonixDsp` | 提供核心的 DSP 函数和数据结构，如 ADSR 设置。 |
| `AudioMixer` | 提供底层音频缓冲区类型（`FAlignedFloatBuffer`）。 |
| `HarmonixDspEditor` | 本模块，提供编辑器工具和实用函数。 |

*注意：实际使用 FusionPatch 导入等编辑器功能时，隐含的依赖更多，通常是在插件自身内部处理。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `8513e7f4` | [Audio] Fix FFusionVoice::AssignIDs KeyZone ordering + add structural null defense. | 修复 FusionVoice 中键区分配的排序问题，并增加空结构体防御。 |
| 2026-05-13 | `f91eb8fe` | Resolved merge conflict with FSoundWaveData api deprecation fixup. | 解决与 FSoundWaveData API 弃用修复相关的合并冲突。 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数导致警告的代码。 |
| 2026-05-12 | `0ae74ea8` | [Harmonix] Add user object to the FusionPatch proxy that can be used for tracking activity in association. | 为 FusionPatch 代理添加用户对象，用于关联跟踪活动。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32 位格式说明符与 64 位参数不匹配的问题。 |

### 维护评价

Harmonix 插件**处于非常活跃的维护状态**。
-   **年龄**：作为 2024 年初引入的插件，它相对年轻，但已集成到 UE 5.4+ 的主流分支中。
-   **近期更新**：最近一个月（截至 2026 年 5 月）有多次提交，集中在**Bug 修复、API 适配（如 FSoundWaveData 弃用）和内部优化**（如防御性编程、格式说明符修正）。这表明插件正在积极与 Unreal Engine 的核心变化保持同步，并修复生产中发现的问题。
-   **实验性状态**：`.uplugin` 中 `IsExperimentalVersion: true`，这暗示其 API 可能尚未完全稳定，未来版本中可能会有变动。但频繁的维护更新降低了“被废弃”的风险。
-   **推荐**：对于需要深度音乐音频集成的**新项目**，尤其是计划使用 UE 5.4 及以上版本的项目，**推荐尝试使用**。但对于需要长期维护的旧项目，考虑到其实验性标签，需要谨慎评估 API 稳定性风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Harmonix)
- [官方文档]()（暂无公开文档链接）