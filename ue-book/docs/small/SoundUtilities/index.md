# Sound Utilities

> A variety of BP functions, objects, and utilities for audio.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否（需手动启用） |
| 包含内容 | 是 |
| 模块 | SoundUtilities (Runtime), SoundUtilitiesEditor (Editor) |
| 创建时间 | 2017-03-22 |
| 年龄标签 | 👴 老古董(>5年) |
| Beta 版本 | ⚠️ 是 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundUtilities) | |

## 用途

SoundUtilities 是一个音频工具集插件，提供两大核心功能：

1. **蓝图音频工具函数库** — 在蓝图中进行 MIDI 音高/频率转换、分贝/线性音量转换、节拍时间计算、Q 值/带宽互转等常用音频数学运算。这些函数在构建合成器 UI、音频可视化、MIDI 交互等功能时非常实用。

2. **Simple Sound 资产** — 一种带权重的音效变体容器。你可以将多个 `SoundWave` 配置为变体，设置每个变体的概率权重、音量范围和音高范围，播放时会随机选择变体并随机化音量和音高，非常适合实现脚步声、枪声等需要自然变化的音效。

**注意**: `USoundSimple`（Simple Sound）已在 UE5.6 中被标记为 **deprecated**。新的音频系统（MetaSounds）提供了更强大的替代方案。蓝图工具函数仍然可用。

## 使用场景

- 你需要在蓝图中进行 MIDI 音高与频率之间的转换 → 用 `GetFrequencyFromMIDIPitch` / `GetMIDIPitchFromFrequency`
- 你在构建音频 UI，需要将线性滑块映射到对数频率刻度 → 用 `GetLogFrequencyClamped` / `GetLinearFrequencyClamped`
- 你需要将音量从线性值转为分贝显示 → 用 `ConvertLinearToDecibels`
- 你想让脚步声/枪声每次播放时有随机的音高和音量变化 → 创建 Simple Sound 资产
- 你在做 BPM 相关的音乐可视化 → 用 `GetBeatTempo` 计算节拍时间

## 蓝图用法

所有蓝图函数都在 `USoundUtilitiesBPFunctionLibrary` 中，通过 **SoundUtilitiesBPLibrary** 类别访问。

### 音高与频率转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Frequency From MIDI Pitch` | MIDI 音符号（0-127）→ 频率（Hz） | `USoundUtilitiesBPFunctionLibrary` |
| `Get MIDI Pitch From Frequency` | 频率（Hz）→ 最近的 MIDI 音符号 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Pitch Scale From MIDI Pitch` | 给定基准和目标 MIDI 音符，计算音高缩放系数 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Frequency Multiplier From Semitones` | 半音数 → 频率倍率 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Gain From Midi Velocity` | MIDI 力度（0-127）→ 线性增益 | `USoundUtilitiesBPFunctionLibrary` |

### 音量转换

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Convert Linear To Decibels` | 线性音量 → 分贝值 | `USoundUtilitiesBPFunctionLibrary` |
| `Convert Decibels To Linear` | 分贝值 → 线性音量 | `USoundUtilitiesBPFunctionLibrary` |

### 频率映射

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Log Frequency Clamped` | 线性值 → 对数频率（适合滑块控制频率） | `USoundUtilitiesBPFunctionLibrary` |
| `Get Linear Frequency Clamped` | 对数频率 → 线性值（反向，适合可视化） | `USoundUtilitiesBPFunctionLibrary` |

### 滤波器参数

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Bandwidth From Q` | Q 值 → 带宽值 | `USoundUtilitiesBPFunctionLibrary` |
| `Get Q From Bandwidth` | 带宽值 → Q 值 | `USoundUtilitiesBPFunctionLibrary` |

### 节拍计算

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Beat Tempo` | BPM + 拍倍数 + 全音符分割数 → 节拍时间（秒） | `USoundUtilitiesBPFunctionLibrary` |

### 使用示例（蓝图描述）

**示例 1：MIDI 音高转频率**

1. 添加一个 `Get Frequency From MIDI Pitch` 节点
2. 将 MIDI 音符号（如 60 = 中央 C）连接到 `MidiNote` 输入
3. 输出即为对应的频率值（约 261.63 Hz）

**示例 2：滑块控制频率（UI 场景）**

1. 有一个 0-1 范围的滑块（如 UISlider）
2. 添加 `Get Log Frequency Clamped` 节点
3. `InValue` 接滑块值，`InDomain` 设为 (0, 1)，`InRange` 设为 (20, 20000)
4. 输出是对数映射后的频率值，适合控制滤波器截止频率

**示例 3：从 SoundWave 创建 Simple Sound**

1. 在内容浏览器中选中一个或多个 `SoundWave` 资产
2. 右键 → Sound → **Create Simple Sound**（需按住 Shift 或启用 legacy asset types）
3. 自动生成一个带 `_SimpleSound` 后缀的 `USoundSimple` 资产
4. 在编辑器中调整各变体的权重、音量范围和音高范围

## C++ 用法

### 头文件引入

```cpp
#include "SoundSimple.h"
#include "SoundUtilities.h"
```

### 基本用法 — 蓝图函数库（C++ 中直接调用）

所有函数都是 `static` 的，可以直接在 C++ 中调用：

```cpp
// MIDI 转频率：MIDI 60（中央 C）→ 261.63 Hz
float Freq = USoundUtilitiesBPFunctionLibrary::GetFrequencyFromMIDIPitch(60);

// 频率转 MIDI：440 Hz → MIDI 69（A4）
int32 MidiNote = USoundUtilitiesBPFunctionLibrary::GetMIDIPitchFromFrequency(440.0f);

// 计算音高缩放：从 MIDI 60 移到 MIDI 72，需要 2.0 的缩放
float Scale = USoundUtilitiesBPFunctionLibrary::GetPitchScaleFromMIDIPitch(60, 72);

// 线性转分贝：1.0 → 0 dB
float dB = USoundUtilitiesBPFunctionLibrary::ConvertLinearToDecibels(1.0f, -60.0f);

// BPM 节拍计算：120 BPM，四分音符 → 0.5 秒
float BeatTime = USoundUtilitiesBPFunctionLibrary::GetBeatTempo(120.0f, 1, 4);
```

### 基本用法 — Simple Sound 资产

```cpp
// 创建一个 USoundSimple 资产
USoundSimple* SimpleSound = NewObject<USoundSimple>();

// 添加变体
FSoundVariation Variation;
Variation.SoundWave = SomeSoundWave;           // 指向一个 USoundWave
Variation.ProbabilityWeight = 1.0f;            // 概率权重（默认 1.0）
Variation.VolumeRange = FVector2D(0.8f, 1.2f); // 音量在 0.8-1.2 之间随机
Variation.PitchRange = FVector2D(0.9f, 1.1f);  // 音高在 0.9-1.1 之间随机
SimpleSound->Variations.Add(Variation);
```

### 进阶用法 — 线性滑块映射到对数频率

适用于自定义音频 UI 中的频率滑块：

```cpp
// 假设有一个线性滑块值 0.5，域为 [0, 1]，范围为 [20, 20000] Hz
float SliderValue = 0.5f;
FVector2D Domain(0.0f, 1.0f);
FVector2D Range(20.0f, 20000.0f);

// 线性 → 对数频率
float LogFreq = USoundUtilitiesBPFunctionLibrary::GetLogFrequencyClamped(SliderValue, Domain, Range);
// 结果约为 632 Hz（对数中间值）

// 反向：对数频率 → 线性值（用于更新滑块位置）
float LinearValue = USoundUtilitiesBPFunctionLibrary::GetLinearFrequencyClamped(LogFreq, Domain, Range);
// 结果约为 0.5
```

## Demo 示例

一个最小可编译示例，在 BeginPlay 中计算 MIDI 频率并打印日志：

**.h 文件**

```cpp
// MyAudioActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyAudioActor.generated.h"

UCLASS()
class AMyAudioActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;
};
```

**.cpp 文件**

```cpp
// MyAudioActor.cpp
#include "MyAudioActor.h"
#include "SoundUtilities.h"

void AMyAudioActor::BeginPlay()
{
    Super::BeginPlay();

    // 中央 C 的频率
    float FreqC4 = USoundUtilitiesBPFunctionLibrary::GetFrequencyFromMIDIPitch(60);
    UE_LOG(LogTemp, Log, TEXT("MIDI 60 (C4) = %.2f Hz"), FreqC4);

    // A4 标准音高
    float FreqA4 = USoundUtilitiesBPFunctionLibrary::GetFrequencyFromMIDIPitch(69);
    UE_LOG(LogTemp, Log, TEXT("MIDI 69 (A4) = %.2f Hz"), FreqA4);

    // 半音到频率倍率：升高一个八度（12半音）= 2倍频率
    float OctaveMultiplier = USoundUtilitiesBPFunctionLibrary::GetFrequencyMultiplierFromSemitones(12.0f);
    UE_LOG(LogTemp, Log, TEXT("12 semitones = %.2fx frequency"), OctaveMultiplier);
}
```

**Build.cs 依赖**

```csharp
PublicDependencyModuleNames.AddRange(new string[] { "SoundUtilities" });
```

## 模块依赖

### SoundUtilities（Runtime 模块）

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（SoundBase、SoundWave 等） |
| `AudioMixer` | 音频混合器（底层 DSP 函数如 `Audio::GetFrequencyFromMidi`） |
| `UMG` | UI 框架 |
| `Slate` / `SlateCore` | Slate UI 框架 |
| `InputCore` | 输入系统 |
| `Projects` | 项目/插件管理 |

### SoundUtilitiesEditor（Editor 模块）

| 模块 | 用途 |
|---|---|
| `SoundUtilities` | Runtime 模块（自身依赖） |
| `UnrealEd` | 编辑器框架 |
| `AssetDefinition` | 资产定义系统 |
| `AudioEditor` | 音频编辑器扩展 |
| `ContentBrowser` | 内容浏览器集成 |
| `ToolMenus` | 右键菜单系统 |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e75189887d` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 代码生成优化，自动批量应用的编译改进 |
| 2025-06-19 | `800d7a513809` | Clean-up/deprecation of USoundSimple; Shift-right click feature; Utilize asset definition code | **重要**：USoundSimple 被标记为 deprecated，右键菜单重构，旧资产类型默认隐藏（需 Shift+右键查看） |
| 2025-04-23 | `93a13080d9ef` | Used LyraGame build target to convert all files to have dllstorage on methods | 批量 DLL 导出声明转换，无功能变化 |

### 维护评价

- **年龄**：约 9 年（2017 年创建），属于 👴 老古董 级别
- **最近更新**：2025-06 有实质性更新，但主要是 **deprecation 标记** 和代码清理
- **活跃度**：维护不活跃 — 最近的更新主要是随引擎批量重构，非功能性增强
- **已知限制**：
  - `USoundSimple` 已被标记为 deprecated，推荐使用 MetaSounds 替代
  - 标记为 Beta 版本（`IsBetaVersion: true`）
  - 默认不启用（`EnabledByDefault: false`），需在插件设置中手动启用
- **推荐使用**：
  - ✅ **蓝图工具函数**（MIDI/频率转换、分贝转换等）— 仍然可用且实用
  - ⚠️ **Simple Sound 资产** — 已废弃，新项目应使用 MetaSounds 的随机变体功能

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SoundUtilities)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：无（Engine/Tests 目录下未找到相关测试）
