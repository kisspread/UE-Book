# Streaming Audio Driven Animation

> Streaming Audio Driven Animation

| 属性 | 值 |
|---|---|
| 中文名 | 流式音频驱动动画 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型数据） |
| 模块 | `SpeechAnimationSolver` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-02-07 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AudioDrivenAnimation/StreamingADA) | |

## 用途

Streaming ADA 插件旨在提供实时、流式的音频驱动动画（Audio Driven Animation）功能。其核心作用是将实时的音频输入（如麦克风录音或语音流）通过一个训练好的神经网络模型（NNE），快速求解并转换为一系列面部动画曲线值（如 Blendshape 权重），从而实现角色口型与语音的实时同步，甚至能根据语音内容推断情绪。它解决了将实时音频流转化为复杂、逼真面部动画的技术难题，是创建虚拟主播、游戏角色实时对话或任何需要语音驱动面部表情的应用程序的理想选择。

与批处理或离线处理不同，该插件强调“流式”处理，设计用于处理连续的音频流，并为每个音频帧输出对应的动画数据，确保动画的实时性和连贯性。

## 使用场景

- **实时虚拟主播/数字人**：将主播的麦克风实时语音转换为虚拟形象的口型和表情动画。
- **游戏角色对话系统**：在游戏中，角色的对话台词是通过代码或语音合成实时生成的，需要动态驱动角色的面部动画。
- **交互式语音助手**：为屏幕上的虚拟助手赋予与语音内容同步的、富有表现力的面部动画。
- **任何需要根据实时音频生成面部动画的应用程序**。

## 蓝图用法

该插件主要提供 C++ 接口，蓝图功能集中在类型定义和数据结构上。主要的运行时逻辑（模型加载、推理）需要在 C++ 层实现。

### 核心类型（蓝图可读写）

| 类型 | 说明 | 所在头文件 |
|---|---|---|
| `EAudioDrivenAnimationMood` | 枚举，定义了支持的情绪状态（如中立、快乐、悲伤、愤怒等）及自动检测选项。 | `SpeechAnimationSolverTypes.h` |
| `FSpeechAnimationAudioFrame` | 结构体，封装了一帧音频输入的所有参数，包括音频样本、采样率、情绪、前瞻值等。 | `SpeechAnimationSolverTypes.h` |
| `FSpeechAnimationFrameData` | 结构体，封装了求解器输出的一帧动画数据，包括曲线名称、曲线值及对应的输入音频帧信息。 | `SpeechAnimationSolverTypes.h` |

### 使用示例（蓝图描述）

1.  **准备音频数据**：通过蓝图或 C++ 从音频流中获取 `AudioSamples` 数组，并填充 `FSpeechAnimationAudioFrame` 结构体的其他字段（如 `SampleRate`, `Mood`）。
2.  **传递给求解器**：在蓝图中，你可以创建一个 `FSpeechAnimationAudioFrame` 变量，并将其设置为一个自定义事件或函数的输入参数，该函数在 C++ 侧负责调用 `ISpeechAnimationSolver::SolveAudioFrame`。
3.  **获取结果**：求解器输出的 `FSpeechAnimationFrameData` 可以通过事件或回调返回给蓝图，蓝图利用其中的 `CurveNames` 和 `CurveValues` 数组，通过 `AnimCurve` 节点或直接设置动画蓝图变量来驱动角色模型的面部变形。

## C++ 用法

### 头文件引入

```cpp
#include "ISpeechAnimationSolver.h"
#include "SpeechAnimationSolverTypes.h"
// 如果需要使用具体的 Solver 版本
#include "SpeechAnimationSolverV4.h"
```

### 基本用法

使用求解器接口处理音频帧并获取动画数据。
*（来源：基于 `ISpeechAnimationSolver` 和 `FSpeechAnimationAudioFrame`/`FSpeechAnimationFrameData` 的通用设计模式）*

```cpp
// 1. 创建求解器实例 (通常从工厂函数或管理器获取)
// 这里假设有一个工厂函数 CreateSolver()
TUniquePtr<ISpeechAnimationSolver> Solver = CreateSolver(NNEModelData, BackendName);

// 2. 初始化求解器
if (!Solver->Initialize())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to initialize speech animation solver."));
    return;
}

// 3. 准备一帧音频数据
FSpeechAnimationAudioFrame AudioInput;
AudioInput.AudioSamples = YourAudioSamplesArray; // 从音频源获取的样本数据
AudioInput.SamplesCount = YourAudioSamplesArray.Num();
AudioInput.SampleRate = 16000; // 例如 16kHz
AudioInput.Mood = EAudioDrivenAnimationMood::AutoDetect; // 或指定情绪
AudioInput.ArrivalTime = GetWorld()->GetTimeSeconds(); // 当前时间

// 4. 求解音频帧，获取动画输出
FSpeechAnimationFrameData AnimOutput;
if (Solver->SolveAudioFrame(AudioInput, AnimOutput))
{
    // 5. 使用输出数据驱动动画
    // AnimOutput.CurveNames 包含 Blendshape 名称
    // AnimOutput.CurveValues 包含对应的权重值
    // 例如，将其应用到 SkeletalMeshComponent 的 MorphTarget 或 Curve 上
    for (int32 i = 0; i < AnimOutput.CurveNames.Num(); ++i)
    {
        // MySkeletalMeshComponent->SetMorphTarget(AnimOutput.CurveNames[i], AnimOutput.CurveValues[i]);
    }
}

// 6. (可选) 在不同会话间重置求解器内部状态
Solver->ClearCache();
```

### 进阶用法

该插件提供了不同版本的求解器实现（如 `FSpeechAnimationSolverV3`, `FSpeechAnimationSolverV4`）。`V4` 版本增加了情绪状态（`MoodState`）和眨眼相关（`BlinkBound`, `BlinkSel`）的内部状态缓冲区，暗示其可能支持更复杂的表情合成逻辑（如基于情绪的眨眼频率和模式）。选择哪个版本取决于具体的模型和需求。

## Demo 示例

一个最小化的 C++ 使用示例，展示如何创建和使用求解器。

```cpp
// MySpeechAnimationComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "ISpeechAnimationSolver.h"
#include "MySpeechAnimationComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMySpeechAnimationComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMySpeechAnimationComponent();

protected:
    virtual void BeginPlay() override;

public:
    // 蓝图可调用，用于接收并处理音频帧
    UFUNCTION(BlueprintCallable, Category = "Speech Animation")
    void FeedAudioFrame(const FSpeechAnimationAudioFrame& AudioFrame);

private:
    TUniquePtr<ISpeechAnimationSolver> Solver;

    // 用于存储最新的输出结果，供蓝图查询
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Speech Animation", meta=(AllowPrivateAccess=true))
    FSpeechAnimationFrameData LastAnimationOutput;
};

// MySpeechAnimationComponent.cpp
#include "MySpeechAnimationComponent.h"
#include "SpeechAnimationSolverV4.h" // 或其他版本

UMySpeechAnimationComponent::UMySpeechAnimationComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMySpeechAnimationComponent::BeginPlay()
{
    Super::BeginPlay();

    // 初始化：获取或加载模型数据 (示例路径，实际需替换)
    TObjectPtr<UNNEModelData> ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/ADA/V4Model"));
    if (ModelData)
    {
        // 创建 V4 求解器实例
        Solver = MakeUnique<FSpeechAnimationSolverV4>(ModelData, TEXT("NNERuntimeORT"));
        if (Solver && Solver->Initialize())
        {
            UE_LOG(LogTemp, Log, TEXT("Speech Animation Solver initialized successfully."));
        }
    }
}

void UMySpeechAnimationComponent::FeedAudioFrame(const FSpeechAnimationAudioFrame& AudioFrame)
{
    if (Solver)
    {
        // 调用求解器，并将结果存储到成员变量
        Solver->SolveAudioFrame(AudioFrame, LastAnimationOutput);
        // 这里可以添加委托广播或事件，通知其他蓝图/组件动画数据已更新
    }
}
```

## 模块依赖

从插件的依赖和功能推断，要使用此插件，你的项目模块需要依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `SpeechAnimationSolver` | 核心求解器运行时模块，包含接口和实现。 |
| `NNE` (或 `NNERuntimeCore`) | 神经网络引擎基础模块，用于加载和管理模型。 |
| `NNERuntimeORT` 或 `NNERuntimeBasicCpu` | NNE 的具体后端运行时，用于执行模型推理（`.uplugin` 中声明的插件依赖）。 |
| `AudioMixer` 或 `Audio` | 用于音频处理，特别是音频重采样（`Audio::FResampler`）。 |

**注意**：`Core`, `Engine`, `CoreUObject` 等常见模块是隐含的。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `c19bc9c9` | Randomize ADA blink | 为音频驱动动画添加随机眨眼功能，增强表情自然度。 |
| 2026-05-12 | `fa06fada` | New ADA model | 更新了音频驱动动画使用的神经网络模型。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 重构日志系统，使用新的格式化宏。 |
| 2026-02-17 | `67ba5104` | Refactor SpeechAnimationStreaming plugin | 对流式语音动画插件进行重构，可能涉及架构或模块划分调整。 |
| 2026-02-07 | `116aa3f3` | Bugfix for CL 50635208 | 修复了特定变更列表引入的错误。 |

### 维护评价

- **创建时间**：该插件非常新，创建于 2026 年 2 月。
- **更新频率**：在创建后的 3 个月内有多次实质性更新，包括模型更新和功能增强（随机眨眼），表明插件正在积极开发中。
- **阶段**：插件处于 **Beta** 阶段（`IsBetaVersion: true`），且默认未启用（`EnabledByDefault: false`），属于实验性功能。
- **推荐度**：**推荐用于实验和原型开发**。对于需要最新音频驱动动画技术的项目，这是一个值得关注和试用的前沿插件。由于是 Beta 版本，可能存在未修复的 Bug 或 API 变动，不建议直接用于对稳定性要求极高的生产环境。建议密切关注其更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/AudioDrivenAnimation/StreamingADA)
- [官方文档]() （暂无）
- [测试用例]() （插件目录内未发现测试文件，可能位于引擎测试目录）