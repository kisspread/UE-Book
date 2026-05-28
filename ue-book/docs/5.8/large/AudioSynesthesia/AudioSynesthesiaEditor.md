# Audio Synesthesia

> A variety of offline analyzers for integrating exposing extracted audio metadata to blueprints.

| 属性 | 值 |
|---|---|
| 中文名 | 音频联觉 |
| 分类 | Audio |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（分析预设） |
| 模块 | `AudioSynesthesiaCore` (Runtime), `AudioSynesthesia` (Runtime), `AudioSynesthesiaEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-08-02 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia) | |

## 用途

AudioSynesthesia 是一个用于音频分析的插件。它并非实时处理音频流，而是对音频文件进行**离线分析**，提取出丰富的元数据（如音高、响度、频率分布、节拍信息等），并将这些数据存储为可在蓝图中查询的资产。其核心价值在于**将音频内容转化为游戏可交互的结构化数据**，从而实现音频驱动的游戏玩法、动态音效或可视化效果。插件提供了一个可扩展的框架，允许开发者添加自定义的分析算法。

## 使用场景

- **节奏游戏**：分析背景音乐的节拍和强度，用于控制游戏物体的生成时机或动画同步。
- **动态环境音效**：分析环境音文件，当检测到特定频率或响度时，触发游戏事件（如警报、环境变化）。
- **音频可视化**：分析音乐文件，驱动材质参数或粒子效果，创建与音乐同步的视觉体验。
- **语音分析**：用于游戏内语音内容的基本分析，如检测静音或特定音量范围。
- **编辑器工具**：在编辑器中预处理音频资源，为后续的程序化使用（如声景生成）提供数据支持。

## 蓝图用法

插件主要通过 **资产（Asset）** 与蓝图交互。工作流程通常是：1）创建或选择分析设置资产；2）指向一个音频文件进行分析；3）在蓝图中查询分析结果资产中的数据。

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UAudioSynesthesiaNRTSettings` | NRT（非实时）分析设置资产，配置分析器的参数（如FFT大小、窗口类型）。 |
| `UAudioSynesthesiaNRT` | NRT 分析结果资产，包含对指定音频文件分析后的数据。 |
| `UAudioSynesthesiaSettings` | （实时）分析器设置基类，用于配置可扩展的分析行为。 |

### 核心查询节点（在分析结果资产 `UAudioSynesthesiaNRT` 上）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFrequencyAmplitudes` | 获取指定时间点的频率幅度数据。 | `UConstantQNRT` (假设为具体分析器子类) |
| `GetNormalizedChannelConstantQ` | 获取归一化后的常量Q变换结果。 | `UConstantQNRT` |
| `GetTempo` | 获取检测到的节拍信息。 | `UBeatDetectionNRT` |

### 使用示例（蓝图描述）

1.  在内容浏览器中，右键 -> 音频 -> 高级 -> 分析 -> `Synesthesia NRT Settings`。选择具体的分析器类型（如 `ConstantQ Settings`）。
2.  创建 `Synesthesia NRT` 资产，在其细节面板中：
    *   将 `Settings` 属性设置为上一步创建的设置资产。
    *   将 `Sound` 属性指向你要分析的音频文件（Wave资产）。
    *   点击 “分析” 按钮。分析完成后，资产将保存分析数据。
3.  在蓝图中：
    *   通过 `Load Asset` 或引用变量获得该 `NRT` 分析结果资产。
    *   使用 `Get Frequency Amplitudes` 节点，输入目标时间点（秒），输出一个频率幅度数组。
    *   可以将该数组用于驱动材质参数、触发事件或任何逻辑判断。

## C++ 用法

C++ 接口主要用于创建自定义分析器或以编程方式控制分析流程。核心逻辑位于 `AudioSynesthesiaCore` 模块。

### 头文件引入

```cpp
#include "AudioSynesthesiaCore.h"
#include "AudioSynesthesia.h"
```

### 基本用法：查询现有分析结果

以下代码展示如何在 C++ 中访问由编辑器生成的分析结果资产数据。

```cpp
// 来源：基于测试用例及模块接口推断
#include "Synesthesia/ConstantQNRT.h" // 假设使用常量Q分析器

void QueryAnalysisData(UConstantQNRT* InConstantQNRTAsset, float InTimeInSeconds)
{
    if (!InConstantQNRTAsset)
    {
        return;
    }

    // 获取特定时间点的频率幅度
    TArray<float> OutAmplitudes;
    InConstantQNRTAsset->GetChannelConstantQ(0, InTimeInSeconds, OutAmplitudes);

    // 处理数据...
    UE_LOG(LogTemp, Log, TEXT("Query at %.2f seconds: %d frequency bins"), InTimeInSeconds, OutAmplitudes.Num());
}
```

### 进阶用法：配置并触发分析

通常分析在编辑器中完成，但也可以通过代码触发。

```cpp
#include "Audio.h"
#include "AudioSynesthesiaNRTFactory.h"

void AnalyzeAudioFile()
{
    // 1. 加载音频资产
    USoundWave* SoundWave = LoadObject<USoundWave>(nullptr, TEXT("/Game/PathToAudioFile.MySoundWave"));
    if (!SoundWave) return;

    // 2. 创建或获取NRT资产
    // 通常通过 Factory 或 AssetData 操作，此处简化为查找已有资产
    UAudioSynesthesiaNRT* NRTAsset = FindObject<UAudioSynesthesiaNRT>(GetTransientPackage(), TEXT("MyNRTAsset"));

    // 3. 设置分析参数（通过Settings资产）
    UConstantQNRTSettings* Settings = NewObject<UConstantQNRTSettings>(GetTransientPackage());
    Settings->FFTSize = EConstantQFFTSizeEnum::Large;
    // ... 其他设置

    // 4. 关联并执行分析
    NRTAsset->Settings = Settings;
    NRTAsset->Sound = SoundWave;
    NRTAsset->AnalyzeAudio();
}
```

## Demo 示例

一个最小化的 C++ 类，封装了分析并查询音频文件常量Q数据的过程。

```cpp
// SynesthesiaDemoActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Synesthesia/ConstantQNRT.h"
#include "SynesthesiaDemoActor.generated.h"

UCLASS()
class ASynesthesiaDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ASynesthesiaDemoActor();

    virtual void BeginPlay() override;

    /** 要分析的音频资产引用 */
    UPROPERTY(EditAnywhere, Category="Audio")
    USoundWave* TargetSoundWave;

    /** 分析结果资产（运行时填充） */
    UPROPERTY(VisibleAnywhere, Category="Audio")
    UConstantQNRT* AnalysisResult;

    /** 在指定时间点查询并打印数据 */
    UFUNCTION(BlueprintCallable, Category="Audio")
    void QueryAtTime(float TimeSeconds);

private:
    void PerformAnalysis();
};
```

```cpp
// SynesthesiaDemoActor.cpp
#include "SynesthesiaDemoActor.h"
#include "Synesthesia/ConstantQNRTSettings.h"

ASynesthesiaDemoActor::ASynesthesiaDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASynesthesiaDemoActor::BeginPlay()
{
    Super::BeginPlay();
    PerformAnalysis();
}

void ASynesthesiaDemoActor::PerformAnalysis()
{
    if (!TargetSoundWave)
    {
        UE_LOG(LogTemp, Warning, TEXT("No sound wave assigned for analysis."));
        return;
    }

    // 创建分析结果资产实例
    AnalysisResult = NewObject<UConstantQNRT>(this, FName("SynesthesiaResult"));

    // 创建并配置设置
    UConstantQNRTSettings* Settings = NewObject<UConstantQNRTSettings>(GetTransientPackage());
    Settings->FFTSize = EConstantQFFTSizeEnum::Small;
    Settings->StartingFrequency = 60.0f;
    Settings->NumBands = 24;

    // 执行分析
    AnalysisResult->Settings = Settings;
    AnalysisResult->Sound = TargetSoundWave;
    AnalysisResult->AnalyzeAudio();

    UE_LOG(LogTemp, Log, TEXT("Analysis complete for: %s"), *TargetSoundWave->GetName());
}

void ASynesthesiaDemoActor::QueryAtTime(float TimeSeconds)
{
    if (!AnalysisResult)
    {
        UE_LOG(LogTemp, Warning, TEXT("Analysis result is null. Did you call PerformAnalysis?"));
        return;
    }

    TArray<float> ConstantQData;
    AnalysisResult->GetChannelConstantQ(0, TimeSeconds, ConstantQData);

    if (ConstantQData.Num() > 0)
    {
        UE_LOG(LogTemp, Log, TEXT("CQ at %.2fs - Bin0: %.4f, Bin1: %.4f, ..."), TimeSeconds, ConstantQData[0], ConstantQData[1]);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No data returned for time %.2fs"), TimeSeconds);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | AudioSynesthesiaCore 依赖此模块实现底层的频谱分析、FFT 等数字信号处理算法。 |
| `AudioMixer` | 可能用于底层的音频数据格式处理和转换。 |
| `AssetDefinition` | AudioSynesthesiaEditor 依赖此模块来定义新的资产类型及其在内容浏览器中的显示方式。 |
| `UnrealEd` | AudioSynesthesiaEditor 模块依赖，用于编辑器内的资产工厂、自定义界面和资产操作。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `01c9ce5d` | [ContentBrowser] New Add Menu Audio Menu | 更新内容浏览器的右键菜单，将分析资产添加到新的“音频”分类下。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，提升代码一致性。 |
| 2026-04-02 | `ebf191b8` | Add bounds check to skip processing when MaxBin is negative in the auto-correlation pitch detector | 在自相关音高检测器中添加边界检查，当最大频率为负时跳过处理，修复潜在问题。 |
| 2026-03-18 | `803166cc` | Fix swapped arguments to CrossCorrelate in YIN pitch detector that caused truncated autocorrelation | 修复YIN音高检测器中互相关函数的参数顺序错误，该错误导致自相关结果被截断。 |
| 2026-03-16 | `d99b4142` | Add YIN pitch detection algorithm to AudioSynesthesiaCore | 在核心模块中添加了YIN音高检测算法，丰富了分析能力。 |

### 维护评价

**积极维护中**。尽管插件被标记为**实验性（IsBetaVersion: true）** 且**默认未启用（EnabledByDefault: false）**，但从git提交记录来看，维护活动非常频繁。最近几次更新（2026年3月、4月）不仅修复了底层算法（如YIN检测器）的bug，还添加了新的分析算法（YIN），并对编辑器集成（资产菜单）进行了现代化更新。这表明插件仍在由 Epic 团队积极开发和完善。

**推荐使用**：对于需要音频驱动玩法的项目，这是一个功能强大且持续改进的工具。虽然标记为实验性，但已具备生产可用性，只是其API可能在未来版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia)
- [官方文档](（暂无）)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/AudioSynesthesia/Tests)