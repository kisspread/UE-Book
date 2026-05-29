# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 元声 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个基于图的（node-based）高性能音频系统。其核心目的是取代传统的基于音效线索（Sound Cue）的音频管线，让声音设计师能够通过一个可视化的、基于节点的编辑器，以数据流的方式直接构建和控制底层的数字信号处理（DSP）图。它实现了对音频信号样本级别的精确控制和调制，允许使用游戏逻辑数据、蓝图参数和音频事件作为输入，从而创造出动态、交互式且高品质的声音效果。

当前文档聚焦于 `MetasoundStandardNodes` 模块，该模块是 MetaSound 系统的核心组成部分，提供了构建任何音频DSP图所需的基础和常用节点，例如各种波形的振荡器（LFO）、增益控制、滤波器、触发器逻辑、随机数生成、包络跟随器、延迟、混响等。

## 使用场景

-   **你需要程序化生成或调制音频信号** → 使用 LFO、Noise、Oscillator 等节点创建波形，并用参数（如游戏中的速度）实时调制其频率或振幅。
-   **你需要一个随机化声音事件的触发逻辑** → 使用 `Random (Bool/Int/Float)` 节点配合 `Trigger` 节点，创建可预测的随机序列或变体。
-   **你需要基于游戏事件精确控制声音的开始、停止和参数变化** → 使用 `Trigger` 类型的节点（如 `Trigger Gate`, `Trigger Repeat`）和 `Value` 节点来响应蓝图事件。
-   **你需要比较两个值并触发相应事件** → 使用 `Trigger Compare` 节点，根据条件（大于、等于等）输出 True/False 触发信号。
-   **你需要累积多个触发事件后执行一个动作** → 使用 `Trigger Accumulator` 节点，实现“当所有输入都触发过一次后，再触发输出”的逻辑。

## 蓝图用法

MetaSound 的主要交互界面是其节点图编辑器。在蓝图中，通常通过“播放 MetaSound 源”、“设置 MetaSound 参数”等函数与 MetaSound 资产进行交互。`MetasoundStandardNodes` 提供的节点主要在 MetaSound 编辑器中使用。

### 核心节点（在 MetaSound 编辑器中使用）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SineOscilator` | 生成正弦波音频信号 | `FSineOscilatorNode` |
| `SawOscilator` | 生成锯齿波音频信号 | `FSawOscilatorNode` |
| `TriangleOscilator` | 生成三角波音频信号 | `FTriangleOscilatorNode` |
| `SquareOscilator` | 生成方波音频信号 | `FSquareOscilatorNode` |
| `LFO` | 低频振荡器，可输出不同波形 | `FLfoNode` |
| `Random (Float/Int/Bool/Time)` | 生成可种子化的随机值 | `TRandomNode<ValueType>` |
| `Value` | 设置一个值并在触发时输出 | `TValueNode<ValueType>` |
| `Trigger Compare` | 比较两个值，根据结果触发 True/False | `TTriggerCompareNode<ValueType>` |
| `Trigger Accumulator (N)` | 累积 N 个触发器输入后触发输出 | `TTriggerAccumulatorNode<NumInputs>` |
| `Trigger Toggle` | 每次触发切换布尔状态 | `FTriggerToggleNode` |
| `Trigger Repeat` | 重复触发信号 | `FTriggerRepeatNode` |
| `Noise` | 生成噪声信号 | `FNoiseNode` |
| `BPM To Seconds` | 将 BPM 转换为秒数（用于时间计算） | `FBPMToSecondsNode` |
| `Envelope Follower` | 跟随音频信号的包络 | `FEnvelopeFollowerNode` |

### 使用示例（蓝图描述）

**创建一个简单的可调制 LFO 来控制声音的音高（Pitch）：**
1.  在 MetaSound 图中拖入一个 `Audio` 输入节点（代表音频波形）和一个 `LFO` 节点。
2.  将 `LFO` 节点的 `Frequency` 引脚连接到一个 `Float` 类型的输入参数节点（例如命名为 “VibratoSpeed”）。
3.  将 `LFO` 节点的输出连接到 `Audio` 输入节点的 `Pitch` 调制输入。
4.  在蓝图中，通过 “Set MetaSound Float Parameter” 函数，动态修改 “VibratoSpeed” 参数的值，即可实时改变声音的颤音效果。

**使用触发器逻辑播放一个随机变体：**
1.  创建一个 `Trigger` 输入节点。
2.  连接一个 `Random (Bool)` 节点，将其输出连接到一个 `Trigger Gate` 节点的 “Open” 输入。
3.  将两个不同的音频源节点连接到 `Trigger Gate` 节点的两个 “In” 端口。
4.  当蓝图发送触发信号时，系统会随机选择播放其中一个音频源。

## C++ 用法

`MetasoundStandardNodes` 主要提供节点实现和工具类，用于构建自定义的 MetaSound 节点。以下是关键头文件和概念的使用示例。

### 头文件引入

```cpp
// 引入标准节点注册相关的头文件
#include "MetasoundStandardNodesCategories.h"
#include "MetasoundStandardNodesNames.h"

// 引入特定节点的头文件
#include "MetasoundOscillators.h"
#include "MetasoundRandomNode.h"
#include "MetasoundValueNode.h"
#include "MetasoundAudioFormats.h"
```

### 基本用法（定义和注册一个自定义节点）

标准节点展示了如何定义节点元数据和操作符。下面是一个简化示例，展示如何创建一个简单的自定义“加倍”节点。
```cpp
// MyDoubleNode.h
#pragma once
#include "MetasoundParamHelper.h"
#include "MetasoundExecutableOperator.h"
#include "MetasoundFacade.h"

namespace Metasound
{
    // 1. 定义输入输出引脚的名称和元数据
    namespace DoubleNodeNames
    {
        METASOUND_PARAM(InputValue, "In", "Input value to be doubled.");
        METASOUND_PARAM(OutputValue, "Out", "Doubled output value.");
    }

    // 2. 定义操作符 (Operator)，实际执行计算逻辑
    template<typename ValueType>
    class TDoubleNodeOperator : public TExecutableOperator<TDoubleNodeOperator<ValueType>>
    {
    public:
        TDoubleNodeOperator(const FOperatorSettings& InSettings, const TDataReadReference<ValueType>& InInputValue)
            : InputValue(InInputValue)
            , OutputValue(TDataWriteReferenceFactory<ValueType>::CreateAny(InSettings))
        {}

        virtual void BindInputs(FInputVertexInterfaceData& InOutVertexData) override
        {
            InOutVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(DoubleNodeNames::InputValue), InputValue);
        }

        virtual void BindOutputs(FOutputVertexInterfaceData& InOutVertexData) override
        {
            InOutVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(DoubleNodeNames::OutputValue), OutputValue);
        }

        void Execute()
        {
            *OutputValue = (*InputValue) * 2.0f; // 假设 ValueType 可以与 float 相乘
        }

        void Reset(const IOperator::FResetParams& InParams) {}

    private:
        TDataReadReference<ValueType> InputValue;
        TDataWriteReference<ValueType> OutputValue;
    };

    // 3. 使用 TNodeFacade 包装操作符，并为其创建元数据
    template<typename ValueType>
    class TDoubleNode : public TNodeFacade<TDoubleNodeOperator<ValueType>>
    {
    public:
        using Super = TNodeFacade<TDoubleNodeOperator<ValueType>>;
        using Super::Super;

        static FNodeClassMetadata CreateNodeClassMetadata()
        {
            FNodeClassMetadata Info;
            Info.ClassName = { StandardNodes::Namespace, TEXT("Double"), GetMetasoundDataTypeDisplayText<ValueType>().ToString() };
            Info.MajorVersion = 1;
            Info.MinorVersion = 0;
            Info.DisplayName = METASOUND_LOCTEXT_FORMAT("DoubleNodeDisplayPattern", "Double ({0})", GetMetasoundDataTypeDisplayText<ValueType>());
            Info.Description = METASOUND_LOCTEXT("DoubleNodeDesc", "Doubles the input value.");
            Info.Author = PluginAuthor;
            Info.PromptIfMissing = PluginNodeMissingPrompt;
            Info.DefaultInterface = GetDefaultInterface();
            Info.CategoryHierarchy.Emplace(NodeCategories::Math); // 使用预定义的节点分类
            return Info;
        }

    private:
        static const FVertexInterface& GetDefaultInterface()
        {
            static const FVertexInterface DefaultInterface(
                FInputVertexInterface(
                    TInputDataVertex<ValueType>(METASOUND_GET_PARAM_NAME_AND_METADATA(DoubleNodeNames::InputValue), 0.0f)
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<ValueType>(METASOUND_GET_PARAM_NAME_AND_METADATA(DoubleNodeNames::OutputValue))
                )
            );
            return DefaultInterface;
        }
    };
}

// 然后在某个模块的启动代码中注册该节点，通常与 MetaSoundStandardNodes 模块中的注册方式类似。
```

### 进阶用法（使用音频格式和采样计数器）

使用 `FMonoAudioFormat` 和 `FStereoAudioFormat` 来处理多通道音频缓冲区。
```cpp
#include "MetasoundAudioFormats.h"
#include "MetasoundSampleCounter.h"

// 在自定义音频处理节点的 Execute 函数中
void Execute()
{
    // 获取输入的立体声音频
    const FStereoAudioFormat& InputAudio = *InputAudioRef;
    FStereoAudioFormat& OutputAudio = *OutputAudioRef;

    // 获取左右声道的缓冲区
    const FAudioBufferReadRef& LeftIn = InputAudio.GetLeft();
    const FAudioBufferReadRef& RightIn = InputAudio.GetRight();
    FAudioBufferWriteRef& LeftOut = OutputAudio.GetLeft();
    FAudioBufferWriteRef& RightOut = OutputAudio.GetRight();

    // 使用 FSampleCounter 进行精确的样本计数和时间转换
    FSampleCounter CurrentTime(*TimeReadRef, OperatorSettings.GetSampleRate());
    FTime NextEventTime = ...;
    FSampleCount NextEventSamples = FSampleCounter::FromTime(NextEventTime, OperatorSettings.GetSampleRate()).GetNumSamples();

    // 处理每个样本
    const int32 NumFrames = OperatorSettings.GetNumFramesPerBlock();
    for (int32 FrameIndex = 0; FrameIndex < NumFrames; ++FrameIndex)
    {
        // 处理音频数据...
        (*LeftOut)[FrameIndex] = ProcessSample((*LeftIn)[FrameIndex]);
        (*RightOut)[FrameIndex] = ProcessSample((*RightIn)[FrameIndex]);

        // 更新时间计数器
        CurrentTime += 1;
    }
}
```

## Demo 示例

一个最小的 C++ 自定义 MetaSound 节点示例（头文件 + 源文件）。

```cpp
// MyVolumeNode.h
#pragma once
#include "MetasoundParamHelper.h"
#include "MetasoundExecutableOperator.h"
#include "MetasoundFacade.h"
#include "MetasoundAudioBuffer.h"

namespace Metasound
{
    namespace VolumeNodeNames
    {
        METASOUND_PARAM(InputAudio, "In", "Input audio signal.");
        METASOUND_PARAM(InputGain, "Gain", "Gain multiplier (linear).");
        METASOUND_PARAM(OutputAudio, "Out", "Output audio signal.");
    }

    // 操作符：对音频信号应用增益
    class FVolumeNodeOperator : public TExecutableOperator<FVolumeNodeOperator>
    {
    public:
        static const FVertexInterface& GetDefaultInterface();
        static const FNodeClassMetadata& GetNodeInfo();
        static TUniquePtr<IOperator> CreateOperator(const FBuildOperatorParams& InParams, FBuildResults& OutResults);

        FVolumeNodeOperator(const FOperatorSettings& InSettings,
                           const FAudioBufferReadRef& InAudioInput,
                           const FFloatReadRef& InGain)
            : AudioInput(InAudioInput)
            , Gain(InGain)
            , AudioOutput(FAudioBufferWriteRef::CreateNew(InSettings))
        {}

        virtual void BindInputs(FInputVertexInterfaceData& InOutVertexData) override;
        virtual void BindOutputs(FOutputVertexInterfaceData& InOutVertexData) override;
        void Execute();

    private:
        FAudioBufferReadRef AudioInput;
        FFloatReadRef Gain;
        FAudioBufferWriteRef AudioOutput;
    };

    // 使用 Facade 包装
    class FVolumeNode : public TNodeFacade<FVolumeNodeOperator>
    {
    public:
        using Super = TNodeFacade<FVolumeNodeOperator>;
        using Super::Super;

        static FNodeClassMetadata CreateNodeClassMetadata();
    };
}
```

```cpp
// MyVolumeNode.cpp
#include "MyVolumeNode.h"

namespace Metasound
{
    const FVertexInterface& FVolumeNodeOperator::GetDefaultInterface()
    {
        static const FVertexInterface DefaultInterface(
            FInputVertexInterface(
                TInputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME_AND_METADATA(VolumeNodeNames::InputAudio)),
                TInputDataVertex<float>(METASOUND_GET_PARAM_NAME_AND_METADATA(VolumeNodeNames::InputGain), 1.0f)
            ),
            FOutputVertexInterface(
                TOutputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME_AND_METADATA(VolumeNodeNames::OutputAudio))
            )
        );
        return DefaultInterface;
    }

    const FNodeClassMetadata& FVolumeNodeOperator::GetNodeInfo()
    {
        auto InitNodeInfo = []() -> FNodeClassMetadata
        {
            FNodeClassMetadata Info;
            Info.ClassName = { StandardNodes::Namespace, TEXT("VolumeNode"), TEXT("") };
            Info.MajorVersion = 1;
            Info.MinorVersion = 0;
            Info.DisplayName = METASOUND_LOCTEXT("VolumeNodeDisplayName", "Volume");
            Info.Description = METASOUND_LOCTEXT("VolumeNodeDescription", "Applies linear gain to an audio signal.");
            Info.Author = TEXT("Custom");
            Info.DefaultInterface = GetDefaultInterface();
            Info.CategoryHierarchy.Emplace(NodeCategories::Dynamics);
            return Info;
        };

        static const FNodeClassMetadata Info = InitNodeInfo();
        return Info;
    }

    TUniquePtr<IOperator> FVolumeNodeOperator::CreateOperator(const FBuildOperatorParams& InParams, FBuildResults& OutResults)
    {
        const FInputVertexInterfaceData& InputData = InParams.InputData;
        FAudioBufferReadRef InAudio = InputData.GetOrCreateDefaultDataReadReference<FAudioBuffer>(METASOUND_GET_PARAM_NAME(VolumeNodeNames::InputAudio), InParams.OperatorSettings);
        FFloatReadRef InGain = InputData.GetOrCreateDefaultDataReadReference<float>(METASOUND_GET_PARAM_NAME(VolumeNodeNames::InputGain), InParams.OperatorSettings);

        return MakeUnique<FVolumeNodeOperator>(InParams.OperatorSettings, InAudio, InGain);
    }

    void FVolumeNodeOperator::BindInputs(FInputVertexInterfaceData& InOutVertexData)
    {
        InOutVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(VolumeNodeNames::InputAudio), AudioInput);
        InOutVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(VolumeNodeNames::InputGain), Gain);
    }

    void FVolumeNodeOperator::BindOutputs(FOutputVertexInterfaceData& InOutVertexData)
    {
        InOutVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(VolumeNodeNames::OutputAudio), AudioOutput);
    }

    void FVolumeNodeOperator::Execute()
    {
        const float CurrentGain = *Gain;
        const int32 NumSamples = AudioInput->Num();
        const float* InputData = AudioInput->GetData();
        float* OutputData = AudioOutput->GetData();

        for (int32 i = 0; i < NumSamples; ++i)
        {
            OutputData[i] = InputData[i] * CurrentGain;
        }
    }

    FNodeClassMetadata FVolumeNode::CreateNodeClassMetadata()
    {
        return FVolumeNodeOperator::GetNodeInfo();
    }
}
```

## 模块依赖

`MetasoundStandardNodes` 模块依赖 MetaSound 核心框架。要在你的 C++ 项目中使用这些节点或创建基于它们的自定义节点，你需要在你的模块 `Build.cs` 文件中添加对相关模块的依赖。

| 模块 | 用途 |
|---|---|
| `MetasoundGraphCore` | 提供 MetaSound 图、节点、操作符的核心抽象和基础设施。 |
| `MetasoundFrontend` | MetaSound 前端，处理资产序列化、图表编辑器交互等。 |
| `MetasoundEngine` | MetaSound 运行时引擎，负责实例化和执行 MetaSound 图。 |
| `MetasoundGenerator` | MetaSound 生成器，用于产生音频流。 |

**注意**：以上模块均为 MetaSound 插件的内部模块，外部项目通常只需要依赖 `MetasoundEngine` 来播放 MetaSound 源。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复删除并重新添加 MetaSound 页面图时的断言错误 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 修复创建 MetaSound 预设时，父资产不可引用导致的潜在问题 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 在发行版中保护目标页面ID不被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 清理之前修复进入PIE时死锁问题的代码 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 针对进入PIE时可能出现的冻结问题的推测性修复 |

### 维护评价

MetaSound 是 Epic Games 持续投入和维护的 UE5 核心音频系统。
-   **活跃维护**：从 git 历史看，最近的更新（2026年5月）集中在稳定性和 bug 修复上，表明项目处于积极的维护阶段。
-   **重要性**：它是 UE5 音频管线的未来方向，替代了传统的 Sound Cue，因此获得了长期支持。
-   **状态**：`MetasoundStandardNodes` 作为其基础节点库，随着核心系统的更新而同步维护。
-   **推荐**：对于任何需要程序化、交互式音频的新 UE5 项目，强烈推荐使用 MetaSound 及其标准节点。它是官方支持且不断完善的系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/metahall/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)