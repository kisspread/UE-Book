# Synthesis and DSP Effects

> A variety of realtime synthesizers and DSP source and submix effects.

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `Synthesis` (Runtime), `SynthesisEditor` (Editor) |
| 实验性 | 否 |
| 创建时间 | 2017-01-10 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis) | |

## 用途

Synthesis 插件是 Unreal Engine 的核心音频插件之一，它提供了一套完整的、可在运行时使用的实时音频合成器和数字信号处理（DSP）效果。该插件的核心价值在于**程序化音频生成**和**实时音频处理**。

它解决的问题是：游戏开发者不再需要完全依赖预制的音频文件（如 .wav）。通过 Synthesis，开发者可以：
1.  **动态生成声音**：例如，根据游戏逻辑（如角色速度、武器充能）实时调整合成器的参数，生成独一无二的音效。
2.  **实时处理音频流**：对游戏中的任何音频源（如环境音、角色语音）应用复杂的 DSP 效果（如混响、延迟、滤波器），并能在游戏运行时动态改变效果参数。
3.  **创建交互式音乐系统**：利用合成器和音序器，构建能够响应玩家行为而变化的动态音乐。

该插件是 UE5 音频引擎的重要组成部分，为创建沉浸式、动态的音频体验提供了底层工具。

## 使用场景

-   **程序化音效**：你需要一个引擎轰鸣声，其音高和音量随转速实时变化 → 使用 `ModularSynth` 或 `MonoWaveTableSynth` 组件。
-   **动态环境音效**：你希望玩家进入一个洞穴时，脚步声和语音自动添加混响效果 → 使用 `SubmixEffectConvolutionReverb` 或 `SubmixEffectDelay`。
-   **交互式音乐**：你正在制作一个音乐游戏，需要根据玩家输入的节拍生成音符 → 使用 `SynthComponent` 和音序器功能。
-   **音频可视化**：你需要分析游戏音频的频谱来驱动 UI 或游戏元素 → 结合 `AudioSynesthesia` 插件使用。
-   **自定义音频资产**：你需要创建和管理合成器预设库 → 使用 `ModularSynthPresetBank` 和 `MonoWaveTableSynthPresetBank` 资产。

## 蓝图用法

Synthesis 插件提供了丰富的蓝图资产类型和组件，用于在编辑器中管理和在运行时控制音频合成与处理。

### 核心资产

| 资产类型 | 说明 | 所在类 |
|---|---|---|
| `ModularSynthPresetBank` | 用于存储和管理 `ModularSynth` 组件预设的资产库。 | `UModularSynthPresetBank` |
| `MonoWaveTableSynthPresetBank` | 用于存储和管理 `MonoWaveTableSynth` 组件预设的资产库。 | `UMonoWaveTableSynthPresetBank` |
| `AudioImpulseResponse` | 存储音频脉冲响应数据，用于卷积混响效果。 | `UAudioImpulseResponse` |

### 核心组件与节点

在蓝图中，你主要通过向 Actor 添加合成器组件来使用此插件。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Modular Synth Component` | 向 Actor 添加一个模块化合成器组件。 | `UModularSynthComponent` |
| `Add Mono Wave Table Synth Component` | 向 Actor 添加一个单波表合成器组件。 | `UMonoWaveTableSynthComponent` |
| `Set Synth Preset` | 从预设资产库中加载一个预设并应用到合成器组件。 | `UModularSynthComponent` |
| `Note On` / `Note Off` | 向合成器发送 MIDI 音符开/关消息。 | `UModularSynthComponent` |
| `Set Filter Frequency` | 实时设置合成器滤波器的截止频率。 | `UModularSynthComponent` |

### 使用示例（蓝图描述）

1.  **创建一个简单的合成器音效**：
    -   在你的 Actor 蓝图中，添加一个 `ModularSynthComponent`。
    -   在 `BeginPlay` 事件中，调用 `Note On` 节点，设置音高（如 C4）和速度，开始发声。
    -   使用 `Set Filter Frequency` 节点，将其值绑定到一个随时间变化的变量，实现扫频效果。

2.  **应用全局混响效果**：
    -   在项目设置或音频子系统中，找到或创建一个 `Sound Submix`。
    -   为该 Submix 添加一个 `SubmixEffectConvolutionReverb` 效果。
    -   将你希望施加混响的音频源（如 `AudioComponent`）的输出路由到该 Submix。
    -   在蓝图中，通过获取该 Submix 效果的引用来动态调整混响参数（如衰减时间）。

## C++ 用法

在 C++ 中，你可以更底层、更高效地控制 Synthesis 插件的功能。

### 头文件引入

```cpp
// 运行时合成器和效果
#include "SynthComponents/EpicSynth1Component.h"
#include "SubmixEffects/SubmixEffectDelay.h"

// 编辑器资产（仅在编辑器模块中使用）
#include "EpicSynth1PresetBank.h"
#include "AudioImpulseResponseAsset.h"
```

### 基本用法：创建并控制一个合成器

以下示例展示了如何在 C++ 中创建一个 `ModularSynthComponent` 并播放一个音符。

```cpp
// 在你的 Actor 头文件 (.h) 中
UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
TObjectPtr<UModularSynthComponent> SynthComponent;

// 在你的 Actor 构造函数或 BeginPlay 中 (.cpp)
SynthComponent = CreateDefaultSubobject<UModularSynthComponent>(TEXT("Synth"));
SynthComponent->SetupAttachment(RootComponent);

// 在某个函数中播放音符
void AMyActor::PlaySynthNote()
{
    if (SynthComponent)
    {
        // 发送一个 MIDI 音符开消息 (音符 60 = C4, 力度 100)
        SynthComponent->NoteOn(60, 100);
    }
}
```

### 进阶用法：动态修改合成器参数

你可以通过 C++ 直接访问合成器的内部参数进行精细控制。

```cpp
// 获取合成器的 Patch（音色）并修改滤波器参数
void AMyActor::ModulateSynthFilter()
{
    if (SynthComponent)
    {
        // 获取当前的合成器 Patch
        FEpicSynth1Patch& Patch = SynthComponent->GetSynthPatch();

        // 修改滤波器截止频率 (假设参数索引为 0)
        // 注意：具体的参数索引需要查阅合成器文档或头文件
        Patch.SetParam(0, FMath::Lerp(20.0f, 20000.0f, CurrentFilterCutoff));
    }
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个播放固定音高的合成器 Actor。

**MySynthActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SynthComponents/EpicSynth1Component.h"
#include "MySynthActor.generated.h"

UCLASS()
class MYPROJECT_API AMySynthActor : public AActor
{
    GENERATED_BODY()

public:
    AMySynthActor();

protected:
    virtual void BeginPlay() override;

public:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Audio")
    TObjectPtr<UModularSynthComponent> SynthComponent;
};
```

**MySynthActor.cpp**
```cpp
#include "MySynthActor.h"

AMySynthActor::AMySynthActor()
{
    PrimaryActorTick.bCanEverTick = false;

    SynthComponent = CreateDefaultSubobject<UModularSynthComponent>(TEXT("Synth"));
    RootComponent = SynthComponent;
}

void AMySynthActor::BeginPlay()
{
    Super::BeginPlay();

    // 在游戏开始时播放一个音符 (C4)
    if (SynthComponent)
    {
        SynthComponent->NoteOn(60, 100);
    }
}
```

**MyProject.Build.cs 依赖**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "Synthesis" // 添加对 Synthesis 运行时模块的依赖
});
```

## 模块依赖

要使用 Synthesis 插件的功能，你的模块需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `AudioSynesthesiaCore` | 提供音频分析核心功能，Synthesis 模块依赖它来实现某些高级音频处理特性。 |
| `Synthesis` | **主要依赖**。包含所有运行时合成器组件、DSP 效果和核心功能。 |
| `SynthesisEditor` | **仅编辑器**。包含资产工厂、类型动作和编辑器设置，用于在编辑器中创建和管理 Synthesis 相关资产。 |

## 维护状态

### 近期更新

1.  **`800d7a513809` (2024-07-19)**: 实现了右键音频操作的反馈和附加功能，包括清理/弃用 `USoundSimple`、Shift+右键排序功能、利用资产定义代码保持章节组织等。
    -   **解读**：这是一次针对编辑器工作流和用户体验的改进，涉及资产管理和弃用旧功能，表明插件仍在积极维护和优化。
2.  **`66e9bb39ff7e` (2024-07-18)**: 移除了整个代码库中所有 `#if UE_ENABLE_INCLUDE_ORDER_DEPRECATED_IN_5_2` 的作用域。
    -   **解读**：这是一次代码清理和现代化工作，移除了过时的兼容性宏，使代码更简洁，符合 UE5.2+ 的规范。
3.  **`e1bacd79a0c1` (2024-07-17)**: 第二次尝试实现从 float 到 pcm16 和反向的向量化音频转换，并为 NEON 添加了优化版本，以及一个约 10% 更快的 `ArrayMixIn` NEON 特化。
    -   **解读**：这是一次重要的性能优化，针对 ARM 平台（如移动设备、Apple Silicon）的 NEON 指令集进行了音频处理加速，提升了插件在目标平台上的运行效率。

### 维护评价

**活跃维护**。

-   **创建时间**：插件创建于 2017 年，已有约 8 年历史，是一个成熟的核心音频插件。
-   **最近更新**：最近的提交（2024年7月）显示插件仍在进行**功能性更新**（编辑器工作流改进）、**代码现代化**（移除废弃宏）和**性能优化**（NEON 加速）。这表明 Epic Games 的音频团队仍在积极维护和改进此插件。
-   **已知问题/限制**：作为大型、复杂的音频插件，其学习曲线较陡。部分高级功能（如卷积混响）可能对性能有较高要求。
-   **推荐使用**：**强烈推荐**。Synthesis 是 UE5 官方提供的、功能强大且持续维护的音频合成与处理解决方案。对于任何需要程序化音频或高级实时音频效果的项目，它都是首选工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/audio-synthesis-and-dsp-effects-in-unreal-engine/) (UE5 官方文档中的音频合成章节)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Synthesis/Tests) (插件内部的自动化测试)