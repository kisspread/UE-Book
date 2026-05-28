# Audio Synesthesia

> A variety of offline analyzers for integrating exposing extracted audio metadata to blueprints.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 音频分析器 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（分析器资产、设置资产） |
| 模块 | `AudioSynesthesiaCore` (Runtime), `AudioSynesthesia` (Runtime), `AudioSynesthesiaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia) | |

## 用途

AudioSynesthesia 插件的核心目的是为游戏提供**实时音频特征分析**能力。虽然 `.uplugin` 描述中提到“offline analyzers”，但从源码和模块名“Synesthesia”（联觉）来看，其主要功能是让游戏能够“听懂”正在播放的声音，将音频流的元数据（如音高、响度、频谱）实时提取出来，并暴露给蓝图和C++代码。

它解决的问题是：游戏需要基于音频内容进行逻辑响应。例如，一个音乐节奏游戏需要知道当前音符的精确音高来判定得分；一个恐怖游戏可能希望当背景音乐中出现特定频率的惊悚音效时，环境灯光随之闪烁；一个动态音效系统需要根据音乐的整体响度来调整游戏音效的混合比例。AudioSynesthesia 通过提供标准化的分析器和蓝图接口，让开发者无需从零实现复杂的音频信号处理算法。

## 使用场景

- **节奏/音游开发**：需要精确检测音频中特定时刻的音高（Pitch）或节拍（Beat），用于触发游戏玩法。
- **音乐可视化**：根据音乐的频谱或响度，动态生成视觉效果（如灯光、粒子、UI动画）。
- **动态游戏体验**：根据游戏内播放的对话或环境音的响度（Loudness），自动调整字幕大小、UI提示强度或角色情绪状态。
- **自适应音频系统**：分析背景音乐的频谱，用于实时调整音效（如脚步声）的音色，使其与音乐更融合。

## 蓝图用法

该插件主要通过 **异步分析任务（Async Task）** 和 **事件驱动** 的方式在蓝图中使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Audio Synesthesia Settings` | 创建特定分析器（如 `Loudness`、`ConstantQ`）的设置对象。 | `UAudioSynesthesiaSettings` 的子类 |
| `Start Analyzing Audio` | 对一个音频组件启动异步分析任务。 | `UAudioSynesthesiaNRT` (非实时) 或 `UAudioSynesthesia` (实时) |
| `On Latest Results` | 分析器的输出事件，返回最新的分析结果。 | 分析器类的委托 |
| `Get NRT Results` | 对于非实时（NRT）分析，获取完整的分析结果数据。 | `UAudioSynesthesiaNRT` |

### 使用示例（蓝图描述）

1.  **创建分析器设置**：在蓝图中，使用 `Create Loudness Settings` 节点生成一个响度分析器的设置资产。你可以配置分析窗口大小、频率范围等参数。
2.  **启动分析**：将一个 `AudioComponent` 的引用连接到 `Start Analyzing Audio` 节点，同时传入上一步创建的设置对象。该节点会返回一个代表分析任务的对象。
3.  **监听结果**：从分析任务对象的输出引脚，拉出 `On Latest Results` 事件。这个事件会定期触发，提供一个包含当前分析结果的结构体（例如，对于响度分析器，就是当前的响度值）。你可以将这个值连接到一个 `Set Intensity`（用于灯光）或 `Print String` 节点进行测试。
4.  **停止分析**：当不再需要时，调用 `Stop Analyzing` 节点。

## C++ 用法

### 头文件引入

```cpp
// 核心分析框架
#include "AudioAnalyzer.h"

// 具体的分析器（示例）
#include "LoudnessNRT.h"
#include "ConstantQNRT.h"
```

### 基本用法

从测试用例中提取，展示如何创建一个非实时（NRT）响度分析器并获取结果。
（来源：`Engine/Plugins/Runtime/AudioSynesthesia/Source/AudioSynesthesia/Tests/LoudnessNRTTest.cpp`）

```cpp
// 假设已经有一个 USoundWave* SoundWave 指向音频资产
UAudioBus* AudioBus = NewObject<UAudioBus>();
// ... 将音频数据路由到 AudioBus ...

// 1. 创建分析器并配置
ULoudnessNRTSettings* Settings = NewObject<ULoudnessNRTSettings>();
Settings->AnalysisPeriod = 0.1f; // 分析周期

ULoudnessNRT* Analyzer = NewObject<ULoudnessNRT>();
Analyzer->SetAudioBus(AudioBus);
Analyzer->Settings = Settings;

// 2. 运行分析并获取结果
Analyzer->Analyze();
// 分析完成后，可以获取整个音频的响度曲线
const TArray<float>& LoudnessCurve = Analyzer->GetLoudnessCurve();

// 遍历曲线数据
for (int32 i = 0; i < LoudnessCurve.Num(); ++i)
{
    float Time = i * Settings->AnalysisPeriod;
    float Loudness = LoudnessCurve[i];
    UE_LOG(LogTemp, Log, TEXT("Time: %.2f, Loudness: %.2f"), Time, Loudness);
}
```

### 进阶用法

结合事件回调和多个分析器，构建一个实时音频响应系统。
（来源：测试用例逻辑和 `UAudioAnalyzer` 的生命周期管理）

```cpp
class UMyAudioReactionComponent : public UActorComponent
{
    UPROPERTY()
    ULoudnessAnalyzer* LoudnessAnalyzer; // 实时分析器

    virtual void BeginPlay() override
    {
        Super::BeginPlay();
        
        // 获取角色的音频组件
        UAudioComponent* AudioComp = GetOwner()->FindComponentByClass<UAudioComponent>();
        if (!AudioComp) return;

        // 配置并启动分析器
        ULoudnessAnalyzerSettings* Settings = NewObject<ULoudnessAnalyzerSettings>();
        LoudnessAnalyzer = NewObject<ULoudnessAnalyzer>();
        LoudnessAnalyzer->SetAudioComponent(AudioComp);
        LoudnessAnalyzer->Settings = Settings;

        // 绑定回调
        LoudnessAnalyzer->OnResults.AddDynamic(this, &UMyAudioReactionComponent::HandleLoudnessResults);
        LoudnessAnalyzer->StartAnalyzing();
    }

    // 响应回调
    UFUNCTION()
    void HandleLoudnessResults(const FLoudnessResults& Results)
    {
        float AverageLoudness = Results.AverageLoudness;
        if (AverageLoudness > LoudnessThreshold)
        {
            // 触发游戏逻辑，例如：惊吓NPC，震动控制器
            TriggerGameReaction();
        }
    }

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override
    {
        if (LoudnessAnalyzer)
        {
            LoudnessAnalyzer->StopAnalyzing();
        }
        Super::EndPlay(EndPlayReason);
    }
};
```

## Demo 示例

一个最小化的 Actor，当检测到音频响度超过阈值时，点亮一个点光源。

**MyAudioReactiveLight.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AudioAnalyzer.h"
#include "LoudnessAnalyzer.h"
#include "MyAudioReactiveLight.generated.h"

UCLASS()
class MYGAME_API AMyAudioReactiveLight : public AActor
{
    GENERATED_BODY()

public:
    AMyAudioReactiveLight();

    UPROPERTY(VisibleAnywhere)
    UAudioComponent* AudioComponent;

    UPROPERTY(VisibleAnywhere)
    UPointLightComponent* LightComponent;

    UPROPERTY(EditAnywhere)
    float LoudnessThreshold = 0.5f;

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY()
    ULoudnessAnalyzer* Analyzer;

    UFUNCTION()
    void OnLoudnessUpdated(const FLoudnessResults& Results);
};
```

**MyAudioReactiveLight.cpp**
```cpp
#include "MyAudioReactiveLight.h"
#include "Components/AudioComponent.h"
#include "Components/PointLightComponent.h"

AMyAudioReactiveLight::AMyAudioReactiveLight()
{
    PrimaryActorTick.bCanEverTick = false;
    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComp"));
    LightComponent = CreateDefaultSubobject<UPointLightComponent>(TEXT("LightComp"));
    RootComponent = LightComponent;
    LightComponent->SetIntensity(0.f);
}

void AMyAudioReactiveLight::BeginPlay()
{
    Super::BeginPlay();
    
    // 设置并启动分析器
    ULoudnessAnalyzerSettings* Settings = NewObject<ULoudnessAnalyzerSettings>();
    Analyzer = NewObject<ULoudnessAnalyzer>();
    Analyzer->SetAudioComponent(AudioComponent);
    Analyzer->Settings = Settings;
    Analyzer->OnResults.AddDynamic(this, &AMyAudioReactiveLight::OnLoudnessUpdated);
    Analyzer->StartAnalyzing();

    // 开始播放音频
    if (AudioComponent && AudioComponent->Sound)
    {
        AudioComponent->Play();
    }
}

void AMyAudioReactiveLight::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (Analyzer)
    {
        Analyzer->StopAnalyzing();
    }
    Super::EndPlay(EndPlayReason);
}

void AMyAudioReactiveLight::OnLoudnessUpdated(const FLoudnessResults& Results)
{
    // 根据响度控制灯光强度
    float NewIntensity = FMath::GetMappedRangeValueClamped(
        FVector2D(0.f, 1.f),
        FVector2D(0.f, 10000.f),
        Results.Loudness
    );
    LightComponent->SetIntensity(NewIntensity);
    
    // 超过阈值时额外效果
    if (Results.Loudness > LoudnessThreshold)
    {
        LightComponent->SetLightColor(FLinearColor::Red);
    }
    else
    {
        LightComponent->SetLightColor(FLinearColor::White);
    }
}
```

## 模块依赖

使用此插件的核心功能（`AudioSynesthesia` 模块），你的项目模块通常需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 音频信号处理底层库，分析器依赖其进行FFT等运算。 |
| `AudioMixer` | 用于访问和管理音频总线（Audio Bus）和音频设备。 |

*注意：`AudioSynesthesiaCore` 模块是分析器的基础，会被 `AudioSynesthesia` 模块自动依赖。`AudioSynesthesiaEditor` 是编辑器专属，仅在插件内部使用。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 在内容浏览器的“添加”菜单中增加了新的音频相关选项。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏统一迁移到新的 UE_LOGF 格式。 |
| 2026-04-02 | `ebf191b8` | Add bounds check to skip processing when MaxBin is negative in the auto-correlation pitch detector | 在自相关音高检测器中添加边界检查，当 MaxBin 为负时跳过处理，修复潜在问题。 |
| 2026-03-18 | `803166cc` | Fix swapped arguments to CrossCorrelate in YIN pitch detector that caused truncated autocorrelation | 修复 YIN 音高检测器中 CrossCorrelate 函数参数顺序错误导致自相关结果被截断的 bug。 |
| 2026-03-16 | `d99b4142` | Add YIN pitch detection algorithm to AudioSynesthesiaCore | 向核心模块新增了 YIN 音高检测算法，提供了更准确的音高分析能力。 |

### 维护评价

- **活跃维护**：该插件近期（2026年3-4月）更新非常频繁，不仅有新功能添加（如 YIN 算法），还有明确的 bug 修复和底层优化（参数修正、边界检查）。
- **状态稳定**：尽管标记为实验性（`IsBetaVersion: true`）且默认不启用，但持续的更新表明它正朝着成熟稳定的状态发展，是 Epic 官方重点维护的音频分析解决方案。
- **推荐使用**：对于需要实时音频分析功能的项目，**强烈推荐使用**。它提供了经过验证的算法和开箱即用的蓝图接口，能极大节省开发时间。需要注意手动启用插件，并关注其 API 可能随着版本迭代发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia/Source/AudioSynesthesia/Tests)