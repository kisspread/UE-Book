# Waveform Editor

> Editor tool for waveforms

| 属性 | 值 |
|---|---|
| 中文名 | 波形编辑器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器 UI 资源） |
| 模块 | `WaveformEditor` (Editor), `WaveformWidgets` (Runtime), `WaveformTransformations` (Runtime), `WaveformTransformationsWidgets` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-18 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor) | |

## 用途

Waveform Editor 是 UE5 内置的音频波形编辑器插件，提供对 `USoundWave` 资产进行可视化编辑的能力。它解决的核心问题是：在引擎内部直接对音频波形进行非破坏性编辑，包括裁剪（Trim）、淡入淡出（Fade）、标记/循环（Markers/Loops）和响度归一化（Normalize），而无需借助外部 DAW 软件。

该插件采用**变换链（Transformation Chain）**架构，将各种音频处理操作封装为 `UWaveformTransformationBase` 的子类，这些变换可以组合堆叠，按优先级顺序依次处理音频数据。

**核心模块说明**：

| 模块 | 类型 | 职责 |
|---|---|---|
| `WaveformEditor` | Editor | 波形编辑器主界面、工具栏、编辑器窗口 |
| `WaveformTransformations` | Runtime | 音频变换算法（Fade、Trim、Normalize、Markers） |
| `WaveformWidgets` | Runtime | 波形可视化 UI 控件 |
| `WaveformTransformationsWidgets` | Runtime | 变换操作的 UI 控件 |

> ⚠️ 本插件默认未启用（`EnabledByDefault: false`），且标记为 Beta 版本（`IsBetaVersion: true`）。需要在项目设置中手动启用。

## 使用场景

- 你需要对 `USoundWave` 进行裁剪和淡入淡出处理 → 使用 Trim+Fade 变换
- 你需要为音效设置循环区域和 Cue 标记 → 使用 Markers 变换
- 你需要将音频响度归一化到特定分贝值 → 使用 Normalize 变换
- 你需要在编辑器中可视化地查看和编辑音频波形 → 使用 WaveformEditor 主界面
- 你需要自定义淡入淡出曲线（指数、对数、S 形等）→ 使用 Fade 变换的曲线函数系统

## 蓝图用法

WaveformTransformations 模块主要面向编辑器和 C++ 使用，蓝图可访问的 API 有限。标记系统提供了 `BlueprintType` 的 `UWaveCueArray` 类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitMarkersIfNotSet` | 初始化标记数组（如果尚未初始化） | `UWaveCueArray` |
| `Reset` | 清空并重置所有标记 | `UWaveCueArray` |
| `EnableLoopRegion` | 启用/禁用指定标记的循环区域 | `UWaveCueArray` |
| `IsLoopRegionActive` | 查询当前是否有活动的循环区域 | `UWaveformTransformationMarkers` |
| `ResetLoopPreviewing` | 重置循环预览状态，返回是否成功重置 | `UWaveformTransformationMarkers` |
| `AdjustLoopPreviewIfNotAligned` | 调整循环预览使其对齐 | `UWaveformTransformationMarkers` |
| `GetSelectedMarker` | 获取当前选中的标记点指针 | `UWaveformTransformationMarkers` |

### 属性（细节面板）

变换对象通过 `USoundWave` 的 Transformation 链在细节面板中编辑，常见的可编辑属性：

**Trim+Fade 变换**：
- `StartTime` / `EndTime` — 裁剪起止时间
- `FadeTransformation` — 嵌入的 Fade 变换对象

**Fade 变换**：
- `FadeRegions` — 淡入淡出区域数组，每个区域可独立设置：
  - `FadeIn` — 淡入函数（Linear / Exponential / Logarithmic / Sigmoid）
  - `FadeOut` — 淡出函数
  - `Fade Duration` — 淡入淡出持续时间
  - `bLinkDurations` — 是否关联淡入淡出持续时间

**Normalize 变换**：
- `Target` — 目标最大音量（dB）
- `MaxGain` — 最大增益限制（dB）
- `Mode` — 归一化模式（Peak / RMS / DWeightedLoudness）

## C++ 用法

### 头文件引入

```cpp
#include "WaveformTransformationFade.h"
#include "WaveformTransformationTrimFade.h"
#include "WaveformTransformationMarkers.h"
#include "WaveformTransformationNormalize.h"
```

### 基本用法 — 创建自定义变换并应用到 SoundWave

WaveformTransformations 模块使用工厂模式：`UWaveformTransformationBase` 子类负责持有编辑器属性，通过 `CreateTransformation()` 生成实际的 `Audio::IWaveTransformation` 实例执行音频处理。

```cpp
// 创建 Normalize 变换对象
UWaveformTransformationNormalize* NormalizeTransform = NewObject<UWaveformTransformationNormalize>();
NormalizeTransform->Target = -1.0f;      // 目标峰值 -1 dB
NormalizeTransform->MaxGain = 12.0f;     // 最大增益 12 dB
NormalizeTransform->Mode = ENormalizationMode::Peak;

// 创建 Transform 的底层执行对象
Audio::FTransformationPtr Transform = NormalizeTransform->CreateTransformation();

// 准备波形信息并执行处理
Audio::FWaveformTransformationWaveInfo WaveInfo;
WaveInfo.RawPCMData = /* PCM 数据指针 */;
WaveInfo.NumChannels = 2;
WaveInfo.SampleRate = 44100.0f;
WaveInfo.NumFrames = /* 帧数 */;

Transform->ProcessAudio(WaveInfo);
```

*来源：Public/WaveformTransformationNormalize.h*

### 进阶用法 — Fade 变换系统

Fade 变换支持多种曲线函数和多区域淡入淡出：

```cpp
// 创建 Fade 变换
UWaveformTransformationFade* FadeTransform = NewObject<UWaveformTransformationFade>();

// 配置淡入淡出区域
TArray<FTransformationFadeFunctionData>& FadeRegions = FadeTransform->GetMutableFadeRegions();

// 设置第一个区域的淡入函数为指数型
FadeRegions[0].FadeIn = NewObject<UTransformationFadeCurveFunctionExponential>();
FadeRegions[0].FadeIn->Duration = 0.3f;  // 0.3 秒淡入

// 设置淡出函数为对数型
FadeRegions[0].FadeOut = NewObject<UTransformationFadeCurveFunctionLogarithmic>();
FadeRegions[0].FadeOut->Duration = 0.5f; // 0.5 秒淡出

// 使用静态映射获取曲线类型
auto FadeModeMap = UWaveformTransformationFade::FadeModeToFadeFunctionMap;
TSubclassOf<UTransformationFadeFunction>* ExponentialClass = FadeModeMap.Find(EWaveEditorTransformationFadeMode::Exponential);
```

*来源：Public/WaveformTransformationFade.h*

### 进阶用法 — Markers 与循环区域

```cpp
// 获取标记变换
UWaveformTransformationMarkers* MarkerTransform = /* 从 SoundWave 获取 */;

// 获取选中的标记
FSoundWaveCuePoint* SelectedMarker = MarkerTransform->GetSelectedMarker();
if (SelectedMarker)
{
    // 操作标记...
}

// 循环区域操作
if (MarkerTransform->IsLoopRegionActive())
{
    MarkerTransform->SetLoopPreviewing();
}

// 切换循环区域预览
bool bWasReset = MarkerTransform->ResetLoopPreviewing();

// 标记操作绑定到 Shift+Space 等键盘快捷键
MarkerTransform->CycleMarkerLoopRegion(ELoopModificationControls::Next);
MarkerTransform->ModifyMarkerLoopRegion(ELoopModificationControls::Increase, PCMArray, 0.01f);

// 寻找最近的过零点（用于精确剪辑）
int64 NextZeroCrossing = UWaveformTransformationMarkers::GetFramesToNextZeroCrossing(
    StartFrame, EndFrame, PCMArray, true, 0.01f, NumChannels);
```

*来源：Public/WaveformTransformationMarkers.h*

### 音频分析工具函数

```cpp
#include "WaveformAudioAnalysisFunctions.h"

// 使用命名空间内的静态分析函数
Audio::FAlignedFloatBuffer PCMData = /* 加载音频数据 */;

float RMS = WaveformAudioAnalysis::GetRMSPeak(PCMData, 44100.0f, 2);
float Loudness = WaveformAudioAnalysis::GetLoudnessPeak(PCMData, 44100.0f, 2);
float Peak = WaveformAudioAnalysis::GetPeakSampleValue(PCMData);
float LUFS = WaveformAudioAnalysis::GetLUFS(PCMData, 44100.0f, 2);
```

*来源：Public/WaveformAudioAnalysisFunctions.h*

## Demo 示例

以下示例展示如何创建一个完整的 Trim+Fade 变换并应用到 SoundWave：

```cpp
// WaveformTransformDemo.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "WaveformTransformationTrimFade.h"
#include "WaveformTransformationFade.h"
#include "WaveformTransformationNormalize.h"
#include "Sound/SoundWave.h"
#include "WaveformTransformDemo.generated.h"

UCLASS()
class UWaveformTransformDemo : public UObject
{
    GENERATED_BODY()

public:
    // 创建一个带淡入淡出的裁剪变换并应用到 SoundWave
    UFUNCTION(BlueprintCallable, Category = "Audio|Demo")
    static void ApplyTrimFadeToSoundWave(
        USoundWave* SoundWave,
        double StartTime,
        double EndTime,
        float FadeInDuration = 0.05f,
        float FadeOutDuration = 0.05f);

    // 为 SoundWave 添加归一化变换
    UFUNCTION(BlueprintCallable, Category = "Audio|Demo")
    static void ApplyNormalization(
        USoundWave* SoundWave,
        float TargetDB = -1.0f,
        ENormalizationMode Mode = ENormalizationMode::Peak);
};
```

```cpp
// WaveformTransformDemo.cpp
#include "WaveformTransformDemo.h"
#include "WaveformTransformationFade.h"

void UWaveformTransformDemo::ApplyTrimFadeToSoundWave(
    USoundWave* SoundWave,
    double StartTime,
    double EndTime,
    float FadeInDuration,
    float FadeOutDuration)
{
    if (!SoundWave) return;

    // 创建 TrimFade 变换对象
    UWaveformTransformationTrimFade* TrimFade = NewObject<UWaveformTransformationTrimFade>(SoundWave);
    TrimFade->StartTime = StartTime;
    TrimFade->EndTime = EndTime;

    // 创建关联的 Fade 变换
    UWaveformTransformationFade* FadeTransform = NewObject<UWaveformTransformationFade>(TrimFade);
    TArray<FTransformationFadeFunctionData>& Regions = FadeTransform->GetMutableFadeRegions();

    if (Regions.Num() > 0)
    {
        // 设置线性淡入
        UTransformationFadeFunctionLinear* FadeIn = NewObject<UTransformationFadeFunctionLinear>();
        FadeIn->Duration = FadeInDuration;
        Regions[0].FadeIn = FadeIn;

        // 设置线性淡出
        UTransformationFadeFunctionLinear* FadeOut = NewObject<UTransformationFadeFunctionLinear>();
        FadeOut->Duration = FadeOutDuration;
        Regions[0].FadeOut = FadeOut;
    }

    TrimFade->FadeTransformation = FadeTransform;

    // 添加到 SoundWave 的变换链中
    // 实际添加方式取决于编辑器 API 和 USoundWave 的 Transformations 数组
}

void UWaveformTransformDemo::ApplyNormalization(
    USoundWave* SoundWave,
    float TargetDB,
    ENormalizationMode Mode)
{
    if (!SoundWave) return;

    UWaveformTransformationNormalize* Normalize = NewObject<UWaveformTransformationNormalize>(SoundWave);
    Normalize->Target = TargetDB;
    Normalize->MaxGain = 24.0f;
    Normalize->Mode = Mode;
}
```

## 模块依赖

从各模块的 Build.cs 推断的依赖关系：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 底层音频混音和缓冲区处理 |
| `SignalProcessing` | 音频信号处理算法（响度分析、滤波） |

无特殊依赖（仅标准 Core/Engine/Slate 等），该插件主要依赖 UE 内置的音频处理框架。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `40a5c76a` | [Waveform] Performance regression when dragging trimfade extents | 修复拖拽 TrimFade 边界时的性能回退 |
| 2026-05-14 | `1f67ea84` | [Waveform editor] Remove no-op trimfade transform option | 移除无效的 TrimFade 变换选项 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 到 float 截断的编译警告 |
| 2026-04-28 | `d67c3aa3` | [Waveform editor] - Shift + space returns playhead to start, but playback does not start at beginning | 修复 Shift+Space 回到起始位置后播放不在开头开始的问题 |
| 2026-04-17 | `93be7d91` | [Waveform] Performance regression when dragging trimfade extents | 修复拖拽 TrimFade 边界时的性能回退 |

### 维护评价

- **创建时间**：2022 年 8 月，随 UE 5.1 发布引入（从实验目录迁移至正式插件目录）
- **维护活跃度**：✅ 活跃维护。2026 年 4-5 月有多次提交，持续修复 bug 和性能问题
- **Beta 状态**：当前仍标记为 Beta（`IsBetaVersion: true`），API 可能有变动
- **已知限制**：
  - 默认未启用，需手动在插件设置中激活
  - 部分旧版 API 已标记 `UE_DEPRECATED`（5.7/5.8），如 `UFadeFunction` → `UTransformationFadeFunction`
  - 效果链变换（`UWaveformTransformationEffectChain`）已在 5.8 废弃
- **推荐程度**：⭐⭐⭐⭐ 推荐使用。虽然是 Beta 版本，但作为 Epic 官方维护的编辑器工具，处于持续开发和修复中，是 UE5 内编辑音频波形的标准方案。注意关注弃用警告并迁移到新 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Editor/WaveformEditor)
- [官方文档]()（暂无）