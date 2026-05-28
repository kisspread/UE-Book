# Audio Synesthesia

> A variety of offline analyzers for integrating exposing extracted audio metadata to blueprints.

| 属性 | 值 |
|---|---|
| 中文名 | 音频联觉 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioSynesthesiaCore` (Runtime), `AudioSynesthesia` (Runtime), `AudioSynesthesiaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia) | |

## 用途

AudioSynesthesia 插件提供了一套全面的音频分析工具集，其核心是将音频信号中提取的元数据（如响度、频谱、节奏等）转换为可在蓝图中使用的信息流。它解决了两个关键问题：

1.  **实时音频分析**：允许开发者在运行时分析游戏内的音频总线（AudioBus），获取实时响度、频谱、振幅等信息，并通过委托广播给蓝图，用于实现基于音频的交互（如音频可视化、环境响应等）。
2.  **离线音频分析（NRT - Non-Real-Time）**：允许开发者对静态音频资产（Sound Wave）进行预先分析和计算，将分析结果存储在专用资产中。然后在运行时通过蓝图查询任意时间点的分析数据（如特定时间的响度值、某个时间段内的节奏点），适合用于精确的音频同步、交互音乐设计或数据驱动的音频效果。

## 使用场景

-   你需要在音乐游戏中精确同步游戏事件与音乐的节拍（使用 `UOnsetNRT` 分析节奏点）。
-   你需要根据环境音效的实时响度来控制场景中的灯光或物体动画（使用 `ULoudnessAnalyzer`）。
-   你需要实现一个音乐可视化工具，根据音频的频谱数据生成动态几何体（使用 `UConstantQAnalyzer` 或 `USynesthesiaSpectrumAnalyzer`）。
-   你需要在电影序列播放时，根据音频的峰值响度来触发特效（使用 `UMeterAnalyzer`）。
-   你需要根据音频的整体响度范围（LRA）来动态调整游戏内背景音乐的混音（使用 `ULKFSAnalyzer` 或 `ULKFSNRT`）。

## 蓝图用法

插件提供的所有分析器都支持蓝图，通过 `BlueprintCallable` 函数和 `BlueprintAssignable` 委托进行交互。

### 实时分析器 (Real-Time Analyzers)

用于分析 `AudioBus` 上的实时音频流。

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLoudnessAtTime` | 获取指定时间点的整体响度。 | `ULoudnessAnalyzer` |
| `GetChannelLoudnessAtTime` | 获取指定时间点特定声道的响度。 | `ULoudnessAnalyzer` |
| `OnOverallLoudnessResults` | 委托：接收自上次调用以来的所有整体响度结果数组。 | `ULoudnessAnalyzer` |
| `OnLatestOverallLoudnessResults` | 委托：接收最新的单个整体响度结果。 | `ULoudnessAnalyzer` |
| `GetCenterFrequencies` | 获取 ConstantQ 频谱分析器的中心频率列表。 | `UConstantQAnalyzer` |
| `OnConstantQResults` | 委托：接收自上次调用以来每个通道的 ConstantQ 频谱结果数组。 | `UConstantQAnalyzer` |
| `OnSpectrumResults` | 委托：接收自上次调用以来每个通道的原始频谱结果数组。 | `USynesthesiaSpectrumAnalyzer` |
| `OnOverallMeterResults` | 委托：接收自上次调用以来的所有整体振幅计量结果数组。 | `UMeterAnalyzer` |
| `OnOverallLKFSResults` | 委托：接收自上次调用以来的所有整体 LKFS 响度结果数组。 | `ULKFSAnalyzer` |

#### 使用示例（蓝图描述）

1.  **创建分析器**：在蓝图中，使用 “Create Object from Class” 节点创建一个分析器实例，例如 `ULoudnessAnalyzer`。
2.  **配置设置**：为分析器的 `Settings` 属性创建一个对应的设置对象（如 `ULoudnessSettings`），并配置分析周期、频率范围、响度曲线类型等参数。
3.  **绑定音频总线**：将分析器的 `AudioBus` 属性指向游戏中的一个 `Audio Bus` 资产。
4.  **绑定委托**：将分析器的委托（如 `OnLatestOverallLoudnessResults`）连接到自定义事件或函数。
5.  **启动分析**：调用分析器的 `Start` 函数。分析器将持续运行，并通过委托将结果推送到蓝图。

### 非实时分析器 (Non-Real-Time Analyzers, NRT)

用于分析预先导入的 `Sound Wave` 资产，结果存储在 NRT 资产中。

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetLoudnessAtTime` | 查询指定时间点的整体响度。 | `ULoudnessNRT` |
| `GetNormalizedLoudnessAtTime` | 查询指定时间点的归一化响度（0-1）。 | `ULoudnessNRT` |
| `GetChannelConstantQAtTime` | 查询指定时间点和声道的 ConstantQ 频谱数据。 | `UConstantQNRT` |
| `GetChannelOnsetsBetweenTimes` | 查询指定时间范围内某声道的节奏点（onset）时间戳和强度。 | `UOnsetNRT` |
| `GetLoudnessDataAtTime` | 查询指定时间点的整体 LKFS 响度数据。 | `ULKFSNRT` |
| `GetIntegratedLoudness` | 获取整个音频的整体平均响度。 | `ULKFSNRT` |

#### 使用示例（蓝图描述）

1.  **创建 NRT 设置**：在内容浏览器中右键，创建对应的设置资产，例如 `UOnsetNRTSettings`。
2.  **创建 NRT 分析资产**：右键设置资产，选择 “Create Analyzer” 或在音频资产上右键，找到 “Create Analyzer” 菜单，生成对应的 NRT 分析资产（如 `UOnsetNRT`）。
3.  **指定音频源**：在 NRT 分析资产的详情面板中，将 `Sound` 属性指向要分析的 `Sound Wave`。
4.  **执行分析**：点击详情面板中的 “Analyze” 按钮，等待分析完成。
5.  **运行时查询**：在游戏蓝图中，获取该 NRT 分析资产的引用，然后调用 `GetChannelOnsetsBetweenTimes` 等函数，传入当前音频播放时间，即可获取预计算好的数据。

## C++ 用法

### 头文件引入

```cpp
// 实时分析器
#include "AudioSynesthesia/Classes/Loudness.h"
#include "AudioSynesthesia/Classes/ConstantQ.h"
#include "AudioSynesthesia/Classes/Meter.h"
#include "AudioSynesthesia/Classes/LKFS.h"
#include "AudioSynesthesia/Classes/SynesthesiaSpectrumAnalysis.h"

// 非实时分析器
#include "AudioSynesthesia/Classes/LoudnessNRT.h"
#include "AudioSynesthesia/Classes/ConstantQNRT.h"
#include "AudioSynesthesia/Classes/OnsetNRT.h"
#include "AudioSynesthesia/Classes/LKFSNRT.h"
```

### 基本用法（实时分析器）

以下示例展示了如何在 C++ 中创建和使用一个实时响度分析器。

```cpp
// MyActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioSynesthesia/Classes/Loudness.h"
#include "MyActor.generated.h"

UCLASS()
class MYPROJECT_API AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void HandleLatestLoudness(const FLoudnessResults& LatestLoudness);

    UPROPERTY()
    TObjectPtr<ULoudnessAnalyzer> LoudnessAnalyzer;

    UPROPERTY()
    TObjectPtr<ULoudnessSettings> LoudnessSettings;
};
```

```cpp
// MyActor.cpp
#include "MyActor.h"
#include "AudioDevice.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建分析器设置
    LoudnessSettings = NewObject<ULoudnessSettings>(this);
    LoudnessSettings->AnalysisPeriod = 0.05f; // 每50ms分析一次
    LoudnessSettings->MinimumFrequency = 100.f;
    LoudnessSettings->MaximumFrequency = 5000.f;
    LoudnessSettings->CurveType = ELoudnessCurveTypeEnum::A;

    // 2. 创建分析器实例
    LoudnessAnalyzer = NewObject<ULoudnessAnalyzer>(this);
    LoudnessAnalyzer->Settings = LoudnessSettings;

    // 3. 绑定委托
    LoudnessAnalyzer->OnLatestOverallLoudnessResults.AddDynamic(this, &AMyActor::HandleLatestLoudness);

    // 4. 指定音频总线 (需要先创建一个Audio Bus资产)
    // LoudnessAnalyzer->AudioBus = MyAudioBusAsset;

    // 5. 开始分析
    LoudnessAnalyzer->Start();
}

void AMyActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (LoudnessAnalyzer)
    {
        LoudnessAnalyzer->Stop();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyActor::HandleLatestLoudness(const FLoudnessResults& LatestLoudness)
{
    UE_LOG(LogTemp, Log, TEXT("Loudness: %f dB, Normalized: %f"), LatestLoudness.Loudness, LatestLoudness.NormalizedLoudness);
    // 根据响度值执行游戏逻辑
}
```

### 进阶用法（非实时分析器查询）

以下示例展示了如何在 C++ 中查询一个已存在的 NRT 分析资产。

```cpp
// 假设已经有一个 ULoudnessNRT* LoudnessNRTAsset 指向资产编辑器中创建的分析资产
void AMyActor::QueryNRTPreset(ULoudnessNRT* LoudnessNRTAsset, float CurrentAudioTime)
{
    if (!LoudnessNRTAsset) return;

    // 查询特定时间的整体响度
    float LoudnessAtTime = 0.f;
    LoudnessNRTAsset->GetLoudnessAtTime(CurrentAudioTime, LoudnessAtTime);

    // 查询特定时间、特定声道的归一化响度
    float ChannelLoudnessNormalized = 0.f;
    LoudnessNRTAsset->GetNormalizedChannelLoudnessAtTime(CurrentAudioTime, 0, ChannelLoudnessNormalized);

    UE_LOG(LogTemp, Log, TEXT("At time %f: Overall Loudness = %f dB, Channel 0 Normalized = %f"),
        CurrentAudioTime, LoudnessAtTime, ChannelLoudnessNormalized);
}
```

## Demo 示例

一个最小化的、可编译的 LKFS 实时分析器示例。

```cpp
// LKFSDemoActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioSynesthesia/Classes/LKFS.h"
#include "LKFSDemoActor.generated.h"

UCLASS()
class ALKFSDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ALKFSDemoActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UFUNCTION()
    void HandleLKFSResults(int32 ChannelIndex, const TArray<FLKFSResults>& Results);

    UPROPERTY()
    TObjectPtr<ULKFSAnalyzer> LKFSAnalyzer;

    UPROPERTY()
    TObjectPtr<ULKFSSettings> LKFSSettings;
};
```

```cpp
// LKFSDemoActor.cpp
#include "LKFSDemoActor.h"

ALKFSDemoActor::ALKFSDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ALKFSDemoActor::BeginPlay()
{
    Super::BeginPlay();

    LKFSSettings = NewObject<ULKFSSettings>(this);
    LKFSSettings->AnalysisPeriod = 0.1f;
    LKFSSettings->AnalysisWindowDuration = 0.4f;
    LKFSSettings->ShortTermLoudnessDuration = 3.0f;

    LKFSAnalyzer = NewObject<ULKFSAnalyzer>(this);
    LKFSAnalyzer->Settings = LKFSSettings;

    LKFSAnalyzer->OnPerChannelLKFSResults.AddDynamic(this, &ALKFSDemoActor::HandleLKFSResults);

    // 绑定音频总线
    // LKFSAnalyzer->AudioBus = ...;

    LKFSAnalyzer->Start();
}

void ALKFSDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (LKFSAnalyzer)
    {
        LKFSAnalyzer->Stop();
    }
    Super::EndPlay(EndPlayReason);
}

void ALKFSDemoActor::HandleLKFSResults(int32 ChannelIndex, const TArray<FLKFSResults>& Results)
{
    if (Results.Num() > 0)
    {
        const FLKFSResults& Latest = Results.Last();
        UE_LOG(LogTemp, Log, TEXT("LKFS Channel %d: %f (Short Term: %f)"),
            ChannelIndex, Latest.Loudness, Latest.ShortTermLoudness);
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下插件模块（在 `.Build.cs` 中添加）：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesia` | 包含所有可蓝图化的分析器类和设置类，是主要功能模块。 |
| `AudioSynesthesiaCore` | 包含底层的音频分析算法和核心框架，由 `AudioSynesthesia` 模块依赖。 |
| `AudioSynesthesiaNRT` | 包含非实时分析器的基类和核心功能，由 `AudioSynesthesia` 模块依赖。 |

在你的项目 `.Build.cs` 中，至少需要添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "AudioSynesthesia" });
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 为内容浏览器添加了新的“音频”菜单项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG日志调用迁移至UE_LOGF。 |
| 2026-04-02 | `ebf191b8` | Add bounds check to skip processing when MaxBin is negative in the auto-correlation pitch detector | 在自相关音高检测器中添加边界检查，当最大频点为负时跳过处理。 |
| 2026-03-18 | `803166cc` | Fix swapped arguments to CrossCorrelate in YIN pitch detector that caused truncated autocorrelation | 修复YIN音高检测器中互相关参数顺序错误导致自相关结果被截断的bug。 |
| 2026-03-16 | `d99b4142` | Add YIN pitch detection algorithm to AudioSynesthesiaCore | 在AudioSynesthesiaCore中添加了YIN音高检测算法。 |

### 维护评价

-   **创建时间**：插件创建于2019年，已有约7年历史。
-   **维护状态**：**维护中**。从git日志看，插件在2026年3-4月仍有实质性功能更新（添加新算法）和Bug修复，说明仍在活跃维护。
-   **已知限制**：`EnabledByDefault = false` 且 `IsBetaVersion = true`，表明这是一个**实验性**插件，API可能在未来版本中发生变化，不建议用于对稳定性要求极高的生产项目。
-   **推荐使用**：如果你的项目需要上述音频分析功能，并且可以接受其Beta状态，那么这是一个功能强大且官方维护的优秀插件。对于简单的音量检测，可能使用引擎内置的 `AudioVolume` 或 `SoundCue` 节点更简单；但对于复杂的、数据驱动的音频交互，AudioSynesthesia 是首选工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)
-   [官方文档] (无)
-   [测试用例] (插件目录下未发现明显测试用例文件)