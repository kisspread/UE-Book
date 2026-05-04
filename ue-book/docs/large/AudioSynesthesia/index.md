# Audio Synesthesia

> A variety of offline analyzers for integrating exposing extracted audio metadata to blueprints.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产模板） |
| 模块 | `AudioSynesthesiaCore` (Runtime), `AudioSynesthesia` (Runtime), `AudioSynesthesiaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia) | |

## 用途

Audio Synesthesia 是一套音频分析工具集，提供**实时**和**离线（NRT）**两种模式的音频特征提取能力。它将底层 DSP 算法（响度、频谱、CQT、起音检测、LKFS）封装为蓝图可用的分析器，使开发者无需编写 DSP 代码即可在蓝图中获取音频的感知特征数据。

**核心价值**：将音频信号转化为结构化数据（响度曲线、频谱能量、起音时间点等），供游戏逻辑（如音频可视化、节拍同步、动态混音）使用。

**为什么需要手动启用**：此插件标记为 `EnabledByDefault: false` 且 `IsBetaVersion: true`，表明 Epic 将其视为实验性功能。使用前需在 Plugins 面板或 `.uproject` 中手动启用。

## 模块架构

```
AudioSynesthesiaCore (Runtime, PreDefault)
│  └── 底层 DSP 算法：工厂类、Worker、Result
│
AudioSynesthesia (Runtime, PreDefault)
│  └── 蓝图封装层：Settings 资产 + Analyzer + Delegate
│
AudioSynesthesiaEditor (Editor, PostDefault)
   └── 编辑器集成：资产工厂、资产类型操作、子菜单
```

| 模块 | 说明 | 文档 |
|---|---|---|
| AudioSynesthesiaCore | DSP 分析引擎（Loudness/CQT/Meter/LKFS/Spectrum/Onset/Pitch） | [AudioSynesthesiaCore.md](AudioSynesthesiaCore.md) |
| AudioSynesthesia | 蓝图友好的分析器和 NRT 资产 | [AudioSynesthesia.md](AudioSynesthesia.md) |
| AudioSynesthesiaEditor | 编辑器资产工厂和类型操作 | [AudioSynesthesiaEditor.md](AudioSynesthesiaEditor.md) |

## 分析器总览

### 实时分析器（UAudioAnalyzer 子类）

挂接到 AudioBus，通过 Delegate 实时推送分析结果。

| 分析器 | 设置类 | 功能 |
|---|---|---|
| `ULoudnessAnalyzer` | `ULoudnessSettings` | 感知响度（支持 A/B/C/D/K 加权） |
| `UConstantQAnalyzer` | `UConstantQSettings` | CQT 频谱（对数频率，适合音乐） |
| `UMeterAnalyzer` | `UMeterSettings` | 电平表（RMS/Peak/削波检测） |
| `ULKFSAnalyzer` | `ULKFSSettings` | ITU-R BS.1770 LKFS 响度 |
| `USynesthesiaSpectrumAnalyzer` | `USynesthesiaSpectrumAnalysisSettings` | FFT 频谱 |

### 离线分析器（UAudioAnalyzerNRT 子类）

对 SoundWave 进行预计算，结果保存为资产，通过函数按时间查询。

| 分析器 | 设置类 | 功能 |
|---|---|---|
| `ULoudnessNRT` | `ULoudnessNRTSettings` | 离线响度分析 |
| `UConstantQNRT` | `UConstantQNRTSettings` | 离线 CQT 分析 |
| `ULKFSNRT` | `ULKFSNRTSettings` | 离线 LKFS 响度 |
| `UOnsetNRT` | `UOnsetNRTSettings` | 离线起音检测 |

## 使用场景

- **音频可视化**：用 `ULoudnessAnalyzer` 或 `UConstantQAnalyzer` 驱动 UI 元素的缩放/颜色变化
- **节拍同步**：用 `UOnsetNRT` 预计算音乐的起音点，在游戏中精确触发事件
- **动态混音**：用 `UMeterAnalyzer` 监测音量，自动调整对话/音乐/音效的平衡
- **广播合规**：用 `ULKFSAnalyzer` 确保音频符合 EBU R128 / ITU-R BS.1770 响度标准
- **音乐分析**：用 `UConstantQNRT` 提取音乐的频谱特征，用于程序化内容生成

## 蓝图用法

### 实时分析器使用模式

实时分析器的使用遵循统一模式：

1. 创建设置资产（内容浏览器右键 → Audio → Synesthesia Settings）
2. 创建分析器实例（Spawn Actor 或 Construct Object）
3. 将设置赋给分析器
4. 将分析器挂接到 AudioBus
5. 绑定 Delegate 接收结果

### 核心节点（以 Loudness 为例）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OnOverallLoudnessResults` | 接收整体响度结果数组 | `ULoudnessAnalyzer` |
| `OnLatestOverallLoudnessResults` | 接收最新整体响度 | `ULoudnessAnalyzer` |
| `OnPerChannelLoudnessResults` | 接收每通道响度 | `ULoudnessAnalyzer` |
| `GetCenterFrequencies` | 获取 CQT 中心频率 | `UConstantQAnalyzer` |
| `GetNumCenterFrequencies` | 获取中心频率数量 | `UConstantQAnalyzer` |

### NRT 分析器核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLoudnessAtTime` | 获取指定时间响度 | `ULoudnessNRT` |
| `GetNormalizedLoudnessAtTime` | 获取归一化响度 | `ULoudnessNRT` |
| `GetChannelConstantQAtTime` | 获取指定时间 CQT | `UConstantQNRT` |
| `GetChannelOnsetsBetweenTimes` | 获取时间范围内起音点 | `UOnsetNRT` |
| `GetIntegratedLoudness` | 获取积分响度 | `ULKFSNRT` |
| `GetGatedLoudness` | 获取门控响度 | `ULKFSNRT` |

### 使用示例（蓝图描述）

**实时响度可视化**：

1. 创建 `ULoudnessSettings` 资产，设置 `AnalysisPeriod = 0.01`
2. 在 Actor 蓝图中，使用 `Construct Object from Class` 创建 `ULoudnessAnalyzer`
3. 将 Settings 赋给分析器
4. 调用 `Start Analyzing Audio Bus`（从 AudioAnalyzer 基类继承）
5. 绑定 `OnLatestOverallLoudnessResults` 委托
6. 在委托回调中，用 `NormalizedLoudness` 驱动 UI 元素的 Scale 或 Color

**离线起音检测**：

1. 创建 `UOnsetNRTSettings` 资产，设置 `Sensitivity = 0.5`, `GranularityInSeconds = 0.01`
2. 创建 `UOnsetNRT` 资产，指定目标 SoundWave 和设置
3. 在编辑器中触发分析（右键 → Analyze）
4. 在蓝图中调用 `GetChannelOnsetsBetweenTimes(0, Duration, 0, Timestamps, Strengths)`
5. 用返回的时间戳数组驱动游戏事件

## C++ 用法

### 头文件引入

```cpp
// 实时分析器
#include "Loudness.h"
#include "ConstantQ.h"
#include "Meter.h"
#include "LKFS.h"
#include "SynesthesiaSpectrumAnalysis.h"

// 离线分析器
#include "LoudnessNRT.h"
#include "ConstantQNRT.h"
#include "OnsetNRT.h"
#include "LKFSNRT.h"
```

### 基本用法

```cpp
// 创建响度设置
ULoudnessSettings* Settings = NewObject<ULoudnessSettings>();
Settings->AnalysisPeriod = 0.01f;
Settings->CurveType = ELoudnessCurveTypeEnum::K;
Settings->MinimumFrequency = 20.0f;
Settings->MaximumFrequency = 20000.0f;

// 创建响度分析器
ULoudnessAnalyzer* Analyzer = NewObject<ULoudnessAnalyzer>();
Analyzer->Settings = Settings;

// 绑定委托（C++ 原生委托，非蓝图委托）
Analyzer->OnLatestOverallLoudnessResultsNative.AddLambda(
    [](ULoudnessAnalyzer* InAnalyzer, const FLoudnessResults& Results)
    {
        UE_LOG(LogTemp, Log, TEXT("Loudness: %f dB, Normalized: %f"),
            Results.Loudness, Results.NormalizedLoudness);
    }
);

// 启动分析（需要先设置 AudioBus）
Analyzer->StartAnalyzing(nullptr, AudioBus);
```

### NRT 离线分析用法

```cpp
// 创建 NRT 设置
ULoudnessNRTSettings* NRTSettings = NewObject<ULoudnessNRTSettings>();
NRTSettings->AnalysisPeriod = 0.05f;
NRTSettings->CurveType = ELoudnessNRTCurveTypeEnum::K;

// 创建 NRT 资产并指定 SoundWave
ULoudnessNRT* NRTAsset = NewObject<ULoudnessNRT>();
NRTAsset->Settings = NRTSettings;
NRTAsset->Sound = MySoundWave;

// 执行分析（编辑器中通常通过资产操作触发）
NRTAsset->AnalyzeAudio();

// 查询结果
float Loudness = 0.0f;
NRTAsset->GetLoudnessAtTime(1.5f, Loudness);

float NormalizedLoudness = 0.0f;
NRTAsset->GetNormalizedLoudnessAtTime(1.5f, NormalizedLoudness);
```

## Demo 示例

### 最小实时响度监测器

```cpp
// MyLoudnessComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "Loudness.h"
#include "MyLoudnessComponent.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class UMyLoudnessComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<UAudioBus> AudioBus;

    UPROPERTY(EditAnywhere, Category = "Audio")
    TObjectPtr<ULoudnessSettings> LoudnessSettings;

    // 当前响度（蓝图可读）
    UPROPERTY(BlueprintReadOnly, Category = "Audio")
    float CurrentLoudness = 0.0f;

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    TObjectPtr<ULoudnessAnalyzer> Analyzer;

    UFUNCTION()
    void OnLoudnessResults(const FLoudnessResults& Results);
};
```

```cpp
// MyLoudnessComponent.cpp
#include "MyLoudnessComponent.h"
#include "AudioBus.h"

void UMyLoudnessComponent::BeginPlay()
{
    Super::BeginPlay();

    if (!LoudnessSettings)
    {
        LoudnessSettings = NewObject<ULoudnessSettings>(this);
    }

    Analyzer = NewObject<ULoudnessAnalyzer>(this);
    Analyzer->Settings = LoudnessSettings;
    Analyzer->OnLatestOverallLoudnessResults.AddDynamic(this, &UMyLoudnessComponent::OnLoudnessResults);
    Analyzer->StartAnalyzing(nullptr, AudioBus);
}

void UMyLoudnessComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Analyzer)
    {
        Analyzer->StopAnalyzing();
    }
    Super::EndPlay(EndPlayReason);
}

void UMyLoudnessComponent::OnLoudnessResults(const FLoudnessResults& Results)
{
    CurrentLoudness = Results.NormalizedLoudness;
}
```

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "AudioSynesthesia",
    "AudioSynesthesiaCore",
    "AudioMixer"
});
```

## 模块依赖

使用者需要在 Build.cs 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 分析器类和设置 |
| `AudioSynesthesiaCore` | 底层 DSP 类型（FLKFSResults 等） |
| `AudioMixer` | AudioBus 支持 |
| `AudioAnalyzer` | 基类接口 |
| `SignalProcessing` | DSP 工具（如果直接使用底层 API） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-27 | `74386d31` | 修复 API 宏用法（AUDIOSYNESTHESIA_API / AUDIOSYNESTHESIACORE_API） |
| 2025-08-07 | `171a65e7` | **新增 LKFS 实时分析器**（ULKFSAnalyzer），符合 ITU-R BS.1770 标准 |
| 2025-06-23 | `daf49948` | **新增 LKFS NRT 分析器**（ULKFSNRT），支持离线 LKFS 分析 |
| 2025-07-11 | `04930821` | 添加 UE_INLINE_GENERATED_CPP_BY_NAME（代码清理） |
| 2025-06-12 | `436da63f` | LoudnessAnalyzer linter 修复 |

### 维护评价

- **状态**: 活跃维护中
- **创建时间**: 2019 年（约 7 年前）
- **近期活跃度**: 2025 年有多次实质性更新，新增了 LKFS 分析器（实时 + NRT），表明 Epic 仍在积极扩展功能
- **Beta 状态**: 仍标记为 `IsBetaVersion: true`，API 可能发生变化
- **推荐**: 适合原型开发和中小型项目。生产环境需注意 Beta 状态，核心功能（Loudness、ConstantQ、Meter）经过多个版本验证已相对稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/AudioSynesthesia)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 测试用例：未找到独立测试文件
