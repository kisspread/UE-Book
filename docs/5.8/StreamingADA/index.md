# Streaming Audio Driven Animation

> Streaming Audio Driven Animation（流式音频驱动动画）

| 属性 | 值 |
|---|---|
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型数据） |
| 模块 | `SpeechAnimationSolver` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-07 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AudioDrivenAnimation/StreamingADA) | |

## 用途

该插件提供了一个基于神经网络（NNE）的实时音频驱动动画求解器。它解决的核心问题是：将实时的音频流（如语音）转换为控制角色面部表情的动画曲线数据。其“流式”特性意味着它可以处理连续到达的音频数据块，而不是一次性处理整个音频文件，非常适合实时应用场景。它通过内置的神经网络模型预测音频对应的面部动画参数，并支持通过情绪（Mood）参数来影响生成的动画风格。

## 使用场景

- **虚拟主播/数字人**：实时将主播的语音转换为虚拟角色的口型和面部表情动画。
- **游戏内实时对话**：在游戏运行时，根据NPC或玩家的语音实时生成对应的面部动画，增强沉浸感。
- **任何需要音频驱动动画的实时应用**：当音频数据是流式传输（例如来自麦克风、网络流）时，使用此插件进行实时转换。

## 蓝图用法

该插件主要通过C++接口提供服务，但其核心数据结构（`FSpeechAnimationAudioFrame`, `FSpeechAnimationFrameData`, `EAudioDrivenAnimationMood`）均为蓝图类型，可在蓝图中构造和传递。

### 核心数据结构

| 结构体/枚举 | 说明 | 所在文件 |
|---|---|---|
| `FSpeechAnimationAudioFrame` | 输入数据结构，包含音频样本、采样率、情绪等信息。 | `SpeechAnimationSolverTypes.h` |
| `FSpeechAnimationFrameData` | 输出数据结构，包含求解出的动画曲线值。 | `SpeechAnimationSolverTypes.h` |
| `EAudioDrivenAnimationMood` | 情绪枚举，用于控制生成动画的风格（如中性、快乐、悲伤等）。 | `SpeechAnimationSolverTypes.h` |

### 使用示例（蓝图描述）

1.  在蓝图中创建一个 `FSpeechAnimationAudioFrame` 结构体变量。
2.  填充其 `AudioSamples`（音频浮点数据）、`SampleRate`（采样率）、`SamplesCount`（样本数）等属性。
3.  设置 `Mood` 属性以指定期望的情绪风格。
4.  通过C++接口（例如自定义蓝图函数库）调用求解器的 `SolveAudioFrame` 函数，传入该结构体。
5.  函数将返回一个 `FSpeechAnimationFrameData` 结构体，其中包含可用于驱动Control Rig或动画蓝图的曲线值。

## C++ 用法

### 头文件引入

```cpp
#include "SpeechAnimationSolverTypes.h"
```

### 基本用法

创建求解器实例并处理单个音频帧。
（来源：`ISpeechAnimationSolver.h`, `SpeechAnimationSolverV3.h`）

```cpp
#include "SpeechAnimationSolverTypes.h"
#include "SpeechAnimationSolverV3.h"
#include "NNE.h"

// 假设已经获取了模型数据 (UNNEModelData*) 和后端名称 (FString)
TObjectPtr<UNNEModelData> ModelData = ...;
FString BackendName = TEXT("ORT");

// 1. 创建求解器实例
TUniquePtr<ISpeechAnimationSolver> Solver = MakeUnique<FSpeechAnimationSolverV3>(ModelData, BackendName);

// 2. 初始化求解器
if (!Solver->Initialize())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to initialize Speech Animation Solver."));
    return;
}

// 3. 准备输入音频帧
FSpeechAnimationAudioFrame AudioFrame;
AudioFrame.AudioSamples = /* 从音频源获取的浮点数据 */;
AudioFrame.SampleRate = 16000; // 例如 16kHz
AudioFrame.SamplesCount = AudioFrame.AudioSamples.Num();
AudioFrame.Mood = EAudioDrivenAnimationMood::Neutral;

// 4. 求解音频帧
FSpeechAnimationFrameData OutputData;
if (Solver->SolveAudioFrame(AudioFrame, OutputData))
{
    // 5. 使用输出数据 (OutputData.CurveValues) 驱动动画
    // 例如，将 OutputData.CurveValues 应用到 Control Rig 的通道上
}

// 6. 在切换说话人或重置状态时，清除缓存
Solver->ClearCache();
```

### 进阶用法

设置情绪强度和前瞻值（Lookahead）来微调动画效果。
（来源：`SpeechAnimationSolverTypes.h`）

```cpp
FSpeechAnimationAudioFrame AudioFrame;
// ... 填充基础音频数据 ...

// 设置情绪为“快乐”，强度为0.8（范围0-1）
AudioFrame.Mood = EAudioDrivenAnimationMood::Happiness;
AudioFrame.MoodIntensity = 0.8f;

// 设置前瞻值（单位：毫秒），用于平滑动画过渡
AudioFrame.Lookahead = 100; // 100ms

// 标记音频帧是否与上一帧连续（用于流式处理）
AudioFrame.bContiguous = true; // 如果是连续的音频流，设为true

// 然后调用 SolveAudioFrame...
```

## Demo 示例

一个最小化的C++示例，展示如何集成求解器。
（注意：实际使用中需要有效的模型数据和NNE后端）

**MyAudioDrivenAnimComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SpeechAnimationSolverTypes.h"
#include "MyAudioDrivenAnimComponent.generated.h"

class ISpeechAnimationSolver;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAudioDrivenAnimComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyAudioDrivenAnimComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 处理一帧音频数据 */
    UFUNCTION(BlueprintCallable, Category = "Audio Animation")
    bool ProcessAudioFrame(const TArray<float>& InAudioSamples, int32 InSampleRate, EAudioDrivenAnimationMood InMood);

    /** 获取最新的动画曲线值 */
    UFUNCTION(BlueprintCallable, Category = "Audio Animation")
    const TArray<float>& GetLatestCurveValues() const;

private:
    TUniquePtr<ISpeechAnimationSolver> Solver;
    FSpeechAnimationFrameData LastOutputData;
};
```

**MyAudioDrivenAnimComponent.cpp**
```cpp
#include "MyAudioDrivenAnimComponent.h"
#include "SpeechAnimationSolverV3.h"
#include "NNE.h"

UMyAudioDrivenAnimComponent::UMyAudioDrivenAnimComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyAudioDrivenAnimComponent::BeginPlay()
{
    Super::BeginPlay();

    // 在实际项目中，模型数据应从资产加载
    // TObjectPtr<UNNEModelData> ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/Models/ADA_Model"));
    // if (ModelData)
    // {
    //     Solver = MakeUnique<FSpeechAnimationSolverV3>(ModelData, TEXT("ORT"));
    //     Solver->Initialize();
    // }
}

void UMyAudioDrivenAnimComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Solver.Reset();
    Super::EndPlay(EndPlayReason);
}

bool UMyAudioDrivenAnimComponent::ProcessAudioFrame(const TArray<float>& InAudioSamples, int32 InSampleRate, EAudioDrivenAnimationMood InMood)
{
    if (!Solver.IsValid())
    {
        return false;
    }

    FSpeechAnimationAudioFrame AudioFrame;
    AudioFrame.AudioSamples = InAudioSamples;
    AudioFrame.SampleRate = InSampleRate;
    AudioFrame.SamplesCount = InAudioSamples.Num();
    AudioFrame.Mood = InMood;
    AudioFrame.bContiguous = true; // 假设连续输入

    return Solver->SolveAudioFrame(AudioFrame, LastOutputData);
}

const TArray<float>& UMyAudioDrivenAnimComponent::GetLatestCurveValues() const
{
    return LastOutputData.CurveValues;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎，用于加载和运行推理模型。 |
| `AudioResampler` | 用于对输入音频进行重采样，以匹配模型要求的采样率。 |

## 维护状态

### 近期更新

- 2026-04-14 `35e60df1` 将日志宏从 UE_LOG 迁移至 UE_LOGF。
- 2026-02-17 `67ba5104` 重构 SpeechAnimationStreaming 插件。
- 2026-02-07 `116aa3f3` 修复 CL 50635208 的 Bug。
- 2026-02-07 `45975269` 重构 SpeechAnimationStreaming 插件。

### 维护评价

该插件创建于2026年2月，非常新。从提交历史看，近期（2026年4月）仍有维护性更新（日志宏迁移），表明它处于**活跃维护**状态。然而，它被标记为 **Beta 版本** 且 **默认禁用**，这意味着其API和功能可能尚未稳定，不建议在生产环境中直接使用，更适合用于研究、原型开发或内部测试。作为实验性功能，使用时需注意潜在的限制和未来可能的变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AudioDrivenAnimation/StreamingADA)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AudioDrivenAnimation/StreamingADA/Tests) （如果存在）