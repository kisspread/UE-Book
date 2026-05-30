# Audio Code Quality Tests

> Audio Code Quality Tests

| 属性 | 值 |
|---|---|
| 中文名 | 音频代码质量测试 |
| 分类 | Testing |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `AudioCQTests` (DeveloperTool) |
| 实验性 | 否 |
| 创建时间 | 2025-08-05 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/AudioCQTests) | |

## 用途

这是一个**用于测试 Unreal Engine 音频子系统**的插件。它不是给最终游戏或应用使用的功能插件，而是 Epic Games 内部用来验证音频系统核心功能（如音频渲染、调度器等）的代码质量（CQ）。插件本身不提供可直接使用的玩家功能，而是包含测试用例和测试辅助组件（如一个生成正弦波的合成组件），用于自动化验证音频相关代码的正确性。

## 使用场景

- 你是引擎开发者或深度修改了音频引擎代码，需要验证你的改动没有破坏核心功能。
- 你需要一个简单的、可控的音频源（如正弦波）来测试自定义的音频处理管线或效果。
- 在进行引擎代码的回归测试时，运行此插件包含的自动化测试用例。

## 蓝图用法

此插件主要包含用于测试的组件，该组件的属性可在蓝图或编辑器中配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FrequencyHz` (属性) | 设置测试正弦波的频率（赫兹） | `UTestSineSynthComponent` |
| `Amplitude` (属性) | 设置测试正弦波的振幅（0到1之间） | `UTestSineSynthComponent` |

### 使用示例（蓝图描述）

1.  在场景中添加一个 Actor。
2.  为其添加一个 `UTestSineSynthComponent` 组件。
3.  在组件的细节面板中，调整 `FrequencyHz`（例如设为 1000）和 `Amplitude`（例如设为 0.5）。
4.  运行游戏，该组件将根据设置持续生成并播放一个单声道正弦波声音。该组件主要用于自动化测试环境中，生成可预测的音频信号。

## C++ 用法

### 头文件引入

```cpp
// 引入测试正弦波合成组件
#include "TestSineSynthComponent.h"
```

### 基本用法

该插件主要提供了一个用于测试的合成组件 `UTestSineSynthComponent`。在 C++ 中，你可以在代码中动态创建或配置它。由于其主要用于测试，通常是在自动化测试用例中使用。

**示例来源**：`Engine/Plugins/Tests/AudioCQTests/Private/TestSineSynthComponent.h`
```cpp
// 假设你已经有了一个 World 上下文 (UWorld* World)
if (UWorld* World = GetWorld())
{
    // 动态生成一个测试用的Actor
    AActor* TestActor = World->SpawnActor<AActor>();
    
    // 为Actor添加测试合成组件
    UTestSineSynthComponent* SineComp = NewObject<UTestSineSynthComponent>(TestActor);
    SineComp->RegisterComponent();
    SineComp->FrequencyHz = 440.0f; // A4音符
    SineComp->Amplitude = 0.3f; // 设置一个较低的振幅，避免过载
    
    // 启动声音播放
    SineComp->Start();
}
```

### 进阶用法

在编写引擎自动化测试时，可能会组合使用此类测试组件与音频引擎的其他部分，来验证渲染或处理流程。

```cpp
// 示例思路（非完整代码，展示测试逻辑）：
// 1. 创建一个带有 TestSineSynthComponent 的Actor。
// 2. 将其音频输出路由到一个自定义的音频总线或子混音。
// 3. 在总线或子混音上应用一个你正在测试的自定义音频效果（例如一个滤波器）。
// 4. 分析处理后的音频数据是否符合预期（例如，验证滤波器是否正确地衰减了特定频率）。
// 5. 这整个流程可能就是 AudioCQTests 插件中某个自动化测试的简化版本。
```

## Demo 示例

以下是一个最小化的 C++ 类，它从 `UTestSineSynthComponent` 继承，用于演示如何基于此插件创建自定义测试音频源。

**TestSineSynthDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/SynthComponent.h"
#include "Audio/SineOsc.h"
#include "TestSineSynthDemoComponent.generated.h"

// 简单的正弦波生成器组件，用于演示或基本音频测试
UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class UTestSineSynthDemoComponent : public USynthComponent
{
    GENERATED_BODY()

public:
    UTestSineSynthDemoComponent();

    // 要生成的音符频率
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    float NoteFrequency = 261.63f; // 中央C

protected:
    // 初始化音频生成器
    virtual bool Init(int32& SampleRate) override;
    
    // 生成音频数据的核心回调
    virtual int32 OnGenerateAudio(float* OutAudio, int32 NumSamples) override;

private:
    // 内部使用的正弦波振荡器
    Audio::FSineOsc SineOsc;
    // 内部生成的单声道缓冲区
    TArray<float> MonoBuffer;
};
```

**TestSineSynthDemoComponent.cpp**
```cpp
#include "TestSineSynthDemoComponent.h"

UTestSineSynthDemoComponent::UTestSineSynthDemoComponent()
{
    // 设置一些默认值，确保组件在场景中可见和可编辑
    bAutoActivate = true;
    PrimaryComponentTick.bCanEverTick = false; // 不需要Tick
}

bool UTestSineSynthDemoComponent::Init(int32& SampleRate)
{
    // 使用引擎传入的采样率初始化正弦波振荡器
    SineOsc.Init((float)SampleRate, NoteFrequency);
    // 本组件生成单声道音频
    NumChannels = 1;
    return true;
}

int32 UTestSineSynthDemoComponent::OnGenerateAudio(float* OutAudio, int32 NumSamples)
{
    // 确保内部缓冲区大小足够
    if (MonoBuffer.Num() < NumSamples)
    {
        MonoBuffer.SetNum(NumSamples);
    }

    // 生成单声道数据
    for (int32 i = 0; i < NumSamples; ++i)
    {
        MonoBuffer[i] = SineOsc.ProcessAudio();
    }

    // 将单声道数据上混到输出的多声道格式
    const int32 NumFrames = NumSamples / NumChannels;
    for (int32 Frame = 0; Frame < NumFrames; ++Frame)
    {
        const float MonoSample = MonoBuffer[Frame];
        for (int32 Channel = 0; Channel < NumChannels; ++Channel)
        {
            OutAudio[Frame * NumChannels + Channel] = MonoSample;
        }
    }

    return NumSamples;
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。其依赖的 `USynthComponent` 和音频基础类来自引擎的 `Engine` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `1dee03ff` | [Audio][RenderScheduler] Add MustPass tags to relevant tests. | 为相关测试添加 MustPass 标签，表明这些测试对音频渲染调度器至关重要。 |
| 2026-03-27 | `fc9b7df7` | Soundfield Rendering Bug fix in first order decoding DSP code. | 修复声场渲染中一阶解码 DSP 代码的 bug。 |
| 2026-03-18 | `60c631b9` | [AudioLink] Add SetOutputFormat() to FDownmixedBufferedSubmixListener for runtime output format chan | 为 AudioLink 的降混缓冲区监听器添加运行时输出格式更改接口。 |
| 2026-02-06 | `34f9b137` | Mark CQ testing modules as DeveloperTool | 将代码质量测试模块标记为 DeveloperTool 类型。 |
| 2026-01-10 | `d8dbe85f` | [Backout] - CL49608042 | 回滚了变更列表 CL49608042 的提交。 |

### 维护评价

这是一个**非常新且活跃维护**的插件（创建于 2025 年底）。从 git 历史看，它在最近几个月内有多次更新，且内容主要围绕为音频引擎的核心功能（渲染调度、声场渲染、AudioLink）添加和调整测试用例。作为 Epic Games 内部使用的测试工具，它会随着被测试的音频系统一同迭代和更新。**强烈推荐**在需要验证音频系统修改时使用或参考此插件的测试方法。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Tests/AudioCQTests)
- [官方文档]() (无)
- [测试用例]() (插件本身即包含测试，路径为 `Engine/Plugins/Tests/AudioCQTests/`)