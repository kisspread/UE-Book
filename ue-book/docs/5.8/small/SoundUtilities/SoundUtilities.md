# Sound Utilities

> A variety of BP functions, objects, and utilities for audio.

| 属性 | 值 |
|---|---|
| 中文名 | 音频工具库 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SoundUtilities` (Runtime), `SoundUtilitiesEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities) | |

## 用途

SoundUtilities 提供一套音频相关的数学工具函数和一个简单的随机声音资产类。主要解决以下问题：

1. **MIDI 与频率互转**：在游戏中动态计算音高、频率时，需要 MIDI 编号与 Hz 之间的快速转换
2. **分贝/线性增益转换**：音频系统中常见的 dB ↔ Linear 换算，避免手动写公式
3. **节拍时间计算**：根据 BPM 和节拍划分计算精确的节拍时长，适用于节奏游戏或音乐同步
4. **对数/线性频率映射**：将线性滑块值映射到对数频率范围，常用于 EQ 等音频参数 UI
5. **Q 值/带宽互转**：音频滤波器设计中 Q 因子与带宽的常用换算
6. **简单随机声音**：`USoundSimple` 提供带权重、音量范围、音高范围的多变体声音播放，适用于枪声、脚步声等需要随机变化的音效

## 使用场景

- 你做了一个节奏/音乐游戏，需要根据 BPM 计算节拍间隔 → 用 `GetBeatTempo`
- 你的音频系统需要在 MIDI 编号和频率之间转换 → 用 `GetFrequencyFromMIDIPitch` / `GetMIDIPitchFromFrequency`
- 你有一个线性滑块控制音量，但音频系统需要 dB 值 → 用 `ConvertLinearToDecibels`
- 你想做一个 EQ 效果器，滑条是线性的但频率是对数的 → 用 `GetLogFrequencyClamped` / `GetLinearFrequencyClamped`
- 你的枪声/脚步声有多个音效变体，需要随机播放且可控音量和音高范围 → 用 `USoundSimple`

**注意**：此插件默认未启用，且标记为实验性（Beta）。使用前需在项目设置中手动启用。

## 蓝图用法

所有蓝图函数均来自 `USoundUtilitiesBPFunctionLibrary`，位于 `SoundUtilitiesBPLibrary` 分类下。

### 核心节点

#### 节拍计算

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Beat Tempo` | 根据 BPM、节拍倍数和全音符划分计算节拍时间（秒） | `USoundUtilitiesBPFunctionLibrary` |

#### MIDI 频率转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Frequency From MIDI Pitch` | MIDI 编号 → 频率（Hz） | `USoundUtilitiesBPFunctionLibrary` |
| `Get MIDI Pitch From Frequency` | 频率（Hz）→ 最近的 MIDI 编号 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Pitch Scale From MIDI Pitch` | 根据起始和目标 MIDI 计算音高缩放系数 | `USoundUtilitiesBPFunctionLibrary` |

#### 增益转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Gain From Midi Velocity` | MIDI 力度 [0,127] → 线性增益 | `USoundUtilitiesBPFunctionLibrary` |
| `Convert Linear To Decibels` | 线性增益 → 分贝值 | `USoundUtilitiesBPFunctionLibrary` |
| `Convert Decibels To Linear` | 分贝值 → 线性增益 | `USoundUtilitiesBPFunctionLibrary` |

#### 频率映射

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Log Frequency Clamped` | 线性值映射到对数频率（适用于 EQ 滑条） | `USoundUtilitiesBPFunctionLibrary` |
| `Get Linear Frequency Clamped` | 对数频率映射回线性值（上一个的逆操作） | `USoundUtilitiesBPFunctionLibrary` |
| `Get Frequency Multiplier From Semitones` | 半音数 → 频率倍率 | `USoundUtilitiesBPFunctionLibrary` |

#### 滤波器参数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Bandwidth From Q` | Q 因子 → 带宽 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Q From Bandwidth` | 带宽 → Q 因子 | `USoundUtilitiesBPFunctionLibrary` |

### 使用示例（蓝图描述）

**示例 1：根据 BPM 驱动节拍器**
1. 拖入 `Get Beat Tempo` 节点，设置 BPM=120，BeatMultiplier=1，DivisionsOfWholeNote=4
2. 输出值连接到 `Delay` 节点的 Duration 输入
3. 形成循环，即可每拍触发一次事件

**示例 2：将 MIDI 力度转为音量**
1. 拖入 `Get Gain From Midi Velocity` 节点
2. 将 MIDI 力度值（如从 MIDI 文件解析出的 0-127）输入
3. 输出连接到 `Set Volume Multiplier` 或声音衰减乘数

**示例 3：线性滑条控制对数频率**
1. 从滑条获取 0.0~1.0 的线性值
2. 拖入 `Get Log Frequency Clamped`，设置 Domain=(0,1)，Range=(20, 20000)
3. 输出连接到音频 EQ 的频率参数

**示例 4：使用 USoundSimple 播放随机枪声**
1. 在内容浏览器右键创建 `Sound Simple` 资产
2. 在 Variations 数组中添加多个 `SoundWave`（如枪声1、枪声2、枪声3）
3. 为每个变体设置 `ProbabilityWeight`（如 0.7 / 0.2 / 0.1）
4. 设置 `VolumeRange` 和 `PitchRange`（如 0.9~1.1）实现细微变化
5. 将该资产设置到音频组件的 Sound 属性即可

## C++ 用法

### 头文件引入

```cpp
#include "SoundUtilities.h"
```

### 基本用法

```cpp
// MIDI 频率转换
// 来源: Public/SoundUtilities.h
float Frequency = USoundUtilitiesBPFunctionLibrary::GetFrequencyFromMIDIPitch(69); // A4 = 440Hz
int32 MidiNote = USoundUtilitiesBPFunctionLibrary::GetMIDIPitchFromFrequency(440.0f); // 返回 69

// 分贝转换
float dB = USoundUtilitiesBPFunctionLibrary::ConvertLinearToDecibels(1.0f, -60.0f); // 0 dB
float Linear = USoundUtilitiesBPFunctionLibrary::ConvertDecibelsToLinear(-6.0f); // ~0.5

// 节拍计算
float BeatTime = USoundUtilitiesBPFunctionLibrary::GetBeatTempo(120.0f, 1, 4); // 0.5秒（120BPM四分音符）
```

### 进阶用法

```cpp
// 构建一个简单的音高变换系统
// 来源: Public/SoundUtilities.h

// 假设基础采样是 C4（MIDI 60），想播放 E4（MIDI 64）
float PitchMultiplier = USoundUtilitiesBPFunctionLibrary::GetPitchScaleFromMIDIPitch(60, 64);
// 将 PitchMultiplier 应用到 UAudioComponent

// 半音移调
float FreqMult = USoundUtilitiesBPFunctionLibrary::GetFrequencyMultiplierFromSemitones(12.0f);
// 返回 2.0（升一个八度频率翻倍）

// 滤波器 Q/带宽转换（常用于自定义 EQ 效果器）
float Q = USoundUtilitiesBPFunctionLibrary::GetQFromBandwidth(1.0f);
float BW = USoundUtilitiesBPFunctionLibrary::GetBandwidthFromQ(Q); // 回到 1.0

// 线性滑条 → 对数频率（用于 UI 控件）
FVector2D Domain(0.0f, 1.0f);
FVector2D Range(20.0f, 20000.0f);
float Freq = USoundUtilitiesBPFunctionLibrary::GetLogFrequencyClamped(0.5f, Domain, Range);
// 在对数刻度上，0.5 映射到约 632Hz
```

## Demo 示例

### 使用 USoundSimple 变体结构体

```cpp
// MyAudioManager.h
#pragma once

#include "CoreMinimal.h"
#include "SoundSimple.h"

UCLASS()
class AMyAudioManager : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioManager();

    // 创建一个包含多个变体的 USoundSimple 资产
    UFUNCTION(BlueprintCallable)
    USoundSimple* CreateRandomizedSound();

    // 使用工具函数计算音频参数
    UFUNCTION(BlueprintCallable)
    void ApplyMidiPitch(UAudioComponent* AudioComp, int32 BaseNote, int32 TargetNote);
};
```

```cpp
// MyAudioManager.cpp
#include "MyAudioManager.h"
#include "SoundUtilities.h"
#include "Components/AudioComponent.h"
#include "Sound/SoundWave.h"

AMyAudioManager::AMyAudioManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

USoundSimple* AMyAudioManager::CreateRandomizedSound()
{
    USoundSimple* SimpleSound = NewObject<USoundSimple>();

    FSoundVariation Var1;
    Var1.SoundWave = nullptr; // 实际使用时加载具体资产
    Var1.ProbabilityWeight = 0.7f;
    Var1.VolumeRange = FVector2D(0.9f, 1.1f);
    Var1.PitchRange = FVector2D(0.95f, 1.05f);

    FSoundVariation Var2;
    Var2.SoundWave = nullptr;
    Var2.ProbabilityWeight = 0.3f;
    Var2.VolumeRange = FVector2D(0.8f, 1.0f);
    Var2.PitchRange = FVector2D(0.9f, 1.0f);

    SimpleSound->Variations.Add(Var1);
    SimpleSound->Variations.Add(Var2);

    return SimpleSound;
}

void AMyAudioManager::ApplyMidiPitch(UAudioComponent* AudioComp, int32 BaseNote, int32 TargetNote)
{
    if (!AudioComp) return;

    float Scale = USoundUtilitiesBPFunctionLibrary::GetPitchScaleFromMIDIPitch(BaseNote, TargetNote);
    AudioComp->SetPitchMultiplier(Scale);
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. | 添加内联生成宏，优化编译性能 |
| 2025-06-19 | `800d7a51` | Implement feedback & additional tidbits for right-click audio actions including | 实现右键音频操作的反馈改进 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar | 统一添加 DLL 导出声明 |
| 2025-04-11 | `b4924cdc` | Fixing crash in simple sound | 修复 USoundSimple 的崩溃问题 |
| 2023-01-16 | `bbc37aa2` | [Engine/Plugins] | 引擎插件通用维护更新 |

### 维护评价

SoundUtilities 自 2017 年创建至今约 8 年，仍保持一定程度的维护（最近一次更新在 2025 年 6 月）。但需注意：

- **仍标记为 Beta**：`IsBetaVersion=true`，Epic 尚未将其标记为稳定
- **默认未启用**：`EnabledByDefault=false`，需要手动在插件设置中启用
- **更新性质**：近期更新以引擎级别改动为主（DLL 导出、编译优化），功能性更新较少（仅有一次崩溃修复）
- **代码规模小**：仅 14 个源文件，功能单一且稳定
- **实用价值高**：虽然标记为实验性，但提供的 MIDI/频率/分贝转换工具非常实用，且 API 简洁

**推荐使用**：对于需要音频数学工具的项目，推荐启用此插件。虽然标记为 Beta，但 API 稳定、功能明确。`USoundSimple` 在 2025 年有过崩溃修复，说明仍在被使用和维护。但请留意 Beta 标记意味着 API 可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/SoundUtilities)
- [SoundUtilities 模块头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/SoundUtilities/Source/SoundUtilities/Public/SoundUtilities.h)
- [USoundSimple 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/SoundUtilities/Source/SoundUtilities/Public/SoundSimple.h)