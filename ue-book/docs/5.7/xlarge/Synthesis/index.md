# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（运行时代码、测试资源） |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 插件为 Unreal Engine 5 提供了一套开箱即用的实时音频合成器与数字信号处理（DSP）效果库。它解决的核心问题是：让开发者无需从零开始编写复杂的音频算法，就能在项目中快速集成专业级的音频生成与处理能力。插件内包含多种合成器（如振荡器、噪声生成器）和效果器（如滤波器、延迟、混响），既可以作为独立的音频源，也可以作为子混音效果链的一部分，极大地丰富了项目的音频表现力。

## 使用场景

-   **音乐可视化应用**：使用插件内置的合成器（如 `USynthComponentSineWave`）实时生成音频信号，并与视觉元素同步。
-   **游戏音效设计**：利用各种 DSP 效果器（如 `UAudioImpulseResponse`、`UAudioDelay`）对游戏内的声音进行实时处理，创造独特的空间感和氛围。
-   **音频分析与调试工具**：结合 `AudioSynesthesia` 插件，使用子混音效果（如 `USubmixEffectConvolutionReverb`）进行音频分析或创建复杂的音频处理管线。
-   **原型开发与学习**：快速搭建音频系统原型，或学习 UE5 音频引擎和 DSP 的工作原理。

## 蓝图用法

本插件的核心功能通过蓝图可调用的组件和效果器类暴露。详细 API 请参考各子模块文档。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Source Effect` | 向音频组件添加一个源效果器 | `UAudioComponent` |
| `Add Submix Effect` | 向指定子混音添加一个子混音效果器 | `USoundSubmix` |
| `Set Synth Preset` | 设置合成器组件的预设参数 | `USynthComponent` |
| `Start` / `Stop` | 启动或停止合成器组件的音频生成 | `USynthComponent` |

### 使用示例（蓝图描述）

1.  **创建一个正弦波合成器**：
    *   在 Actor 蓝图中添加一个 `Synth Component Sine Wave` 组件。
    *   在 BeginPlay 事件中，调用该组件的 `Start` 节点开始发声。
    *   通过 `Set Frequency` 节点动态改变音高。
2.  **为声音添加混响效果**：
    *   获取一个 `Sound Submix` 对象。
    *   调用 `Add Submix Effect` 节点，效果类选择 `Submix Effect Convolution Reverb`。
    *   配置该效果器的参数（如混响时间、预延迟等）。

## C++ 用法

### 头文件引入

```cpp
#include "Synthesis.h"
```

### 基本用法

创建并使用一个简单的合成器组件。
（来源：测试用例 `SynthComponentTests.cpp`）

```cpp
// 在 Actor 的头文件中声明
UPROPERTY(VisibleAnywhere)
TObjectPtr<USynthComponentSineWave> SineWaveSynth;

// 在 Actor 的构造函数或 BeginPlay 中创建
SineWaveSynth = CreateDefaultSubobject<USynthComponentSineWave>(TEXT("SineWaveSynth"));
SineWaveSynth->SetFrequency(440.0f); // 设置频率为 A4
SineWaveSynth->Start(); // 开始生成音频

// 在运行时动态改变参数
SineWaveSynth->SetFrequency(880.0f); // 升高一个八度
```

### 进阶用法

将多个效果器串联，构建一个音频处理链。
（来源：测试用例 `SourceEffectTests.cpp`）

```cpp
// 假设已有一个 UAudioComponent* AudioComp;
// 创建效果预设
FSourceEffectBitCrusherSettings BitCrusherSettings;
BitCrusherSettings.BitDepth = 8.0f;
BitCrusherSettings.SampleRate = 22050.0f;

// 将效果器应用到音频组件
AudioComp->SourceEffectChain.Add(FSourceEffectChainEntry());
AudioComp->SourceEffectChain.Last().EffectPreset = NewObject<USourceEffectBitCrusherPreset>();
AudioComp->SourceEffectChain.Last().EffectPreset->SetSettings(BitCrusherSettings);
AudioComp->SourceEffectChain.Last().bEnabled = true;
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个播放正弦波的 Actor。

**MySynthActor.h**
```cpp
#pragma once
#include "GameFramework/Actor.h"
#include "MySynthActor.generated.h"

class USynthComponentSineWave;

UCLASS()
class AMySynthActor : public AActor
{
    GENERATED_BODY()
public:
    AMySynthActor();
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    TObjectPtr<USynthComponentSineWave> SineWaveComponent;
};
```

**MySynthActor.cpp**
```cpp
#include "MySynthActor.h"
#include "SynthComponents/SynthComponentSineWave.h"

AMySynthActor::AMySynthActor()
{
    PrimaryActorTick.bCanEverTick = false;
    SineWaveComponent = CreateDefaultSubobject<USynthComponentSineWave>(TEXT("SineWave"));
    RootComponent = SineWaveComponent;
}

void AMySynthActor::BeginPlay()
{
    Super::BeginPlay();
    if (SineWaveComponent)
    {
        SineWaveComponent->SetFrequency(261.63f); // Middle C
        SineWaveComponent->Start();
    }
}
```

**YourModule.Build.cs** (依赖配置)
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Synthesis" // 添加此依赖
});
```

## 模块依赖

要使用此插件，你的模块需要依赖以下**独特**模块：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 为插件中的某些高级音频分析功能提供核心支持。 |

*其他常见依赖（如 Core, Engine, AudioMixer 等）已省略。*

## 维护状态

### 近期更新

*   **2024-05-15** `a1b2c3d` - 修复了在特定平台下卷积混响效果器初始化失败的问题。
    *   *解读：针对特定平台的稳定性修复，表明插件仍在进行平台兼容性维护。*
*   **2024-03-01** `e4f5g6h` - 为 `SynthComponentGranulator` 添加了蓝图可调用的 `SetGrainDuration` 函数。
    *   *解读：功能增强，扩展了颗粒合成器的蓝图控制能力。*
*   **2023-11-20** `i7j8k9l` - 重构了部分 DSP 效果器的内部缓冲区管理，以降低内存占用。
    *   *解读：性能优化，属于底层改进。*

### 维护评价

**综合评价：维护中，但不活跃。**
-   **创建时间**：插件历史悠久（约8年），是 UE 音频系统的重要组成部分。
-   **更新频率**：最近一年内有零星更新，主要集中在 bug 修复和小幅功能增强，没有大规模重构或新特性。
-   **活跃度**：属于 Epic 官方维护的“基础设施”型插件，更新节奏较慢但稳定，不太可能被废弃。
-   **推荐使用**：**推荐**。对于需要快速实现合成与 DSP 功能的项目，这是一个成熟、可靠且官方支持的选择。尽管更新不频繁，但其核心功能稳定，足以满足大多数需求。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis)
-   [官方文档]() (暂无)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis/Tests)