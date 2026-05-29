# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 元声音 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是 UE5 的新一代音频系统，解决了传统 SoundCue 系统无法实现采样精确的 DSP 图控制的根本问题。它提供了一个完整的**节点化音频 DSP 图引擎**，允许声音设计师通过连接各种处理节点（生成器、滤波器、调制器、混音器等）来构建自定义音频处理管线，实现：

- **采样精确控制**：所有音频参数在每个音频样本级别上更新，无延迟、无插值误差
- **实时参数调制**：支持从游戏数据和蓝图实时修改音频参数，实现自适应音效
- **动态图修改**：运行时可添加/移除节点、修改连接、淡入淡出音频过渡
- **高性能执行**：基于拓扑排序的运算符表驱动执行，支持 SIMD 对齐的音频缓冲区
- **强类型系统**：完整的数据类型注册和验证机制，包括多态类型支持
- **变量系统**：支持延迟变量（上一帧读取）和即时变量，保证音频线程安全

MetaSound 与传统 SoundCue 的核心区别在于：SoundCue 是一个"播放列表"式的音频混合系统，而 MetaSound 是一个真正的**信号处理图引擎**，每个节点执行 DSP 级别的运算，整体以确定性的顺序执行。

## 使用场景

- 你需要为枪声、脚步声等创建自适应音效，根据距离、材质等游戏数据实时调整 → 用 MetaSound 图 + 蓝图参数驱动
- 你需要构建复杂的音乐系统，根据游戏状态动态切换和混合音乐层 → 用 MetaSound 的动态图修改和变量系统
- 你需要实现自定义 DSP 效果（如自定义延迟、谐振器、物理模拟声源） → 用 MetaSound 节点系统实现
- 你需要精细控制音频参数的调制（LFO、包络、随机等） → 用 MetaSound 的内置调制节点
- 你需要在运行时动态修改音频处理图（添加/移除处理链路） → 用 FDynamicOperatorTransactor API
- 你需要调试和性能分析音频图的执行开销 → 用 FGraphRenderCost 和 FProfilingOperator

## 蓝图用法

> **注意**：MetasoundGraphCore 模块本身主要提供 C++ 核心接口，高级蓝图 API 位于 MetasoundEngine 和 MetasoundFrontend 模块中。以下列出本模块中可用于蓝图集成的核心类。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddNode` | 向动态图中添加节点 | `DynamicGraph::FDynamicOperatorTransactor` |
| `RemoveNode` | 从动态图中移除节点（支持音频淡出） | `DynamicGraph::FDynamicOperatorTransactor` |
| `AddDataEdge` | 在两个节点之间建立数据连接 | `DynamicGraph::FDynamicOperatorTransactor` |
| `RemoveDataEdge` | 断开两个节点之间的连接，替换为字面量值 | `DynamicGraph::FDynamicOperatorTransactor` |
| `SetValue` | 设置节点输入顶点的默认值 | `DynamicGraph::FDynamicOperatorTransactor` |
| `AddInputDataDestination` | 暴露图的内部输入到外部 | `DynamicGraph::FDynamicOperatorTransactor` |
| `AddOutputDataSource` | 暴露图的内部输出到外部 | `DynamicGraph::FDynamicOperatorTransactor` |
| `CreateTransformQueue` | 创建与动态运算符通信的队列 | `DynamicGraph::FDynamicOperatorTransactor` |

### 使用示例（蓝图描述）

MetaSound 的典型蓝图使用流程是通过 **UMetasound** 资产在编辑器中设计音频图，然后通过蓝图设置参数值。对于需要运行时动态修改图结构的高级用法，需要在 C++ 层使用 FDynamicOperatorTransactor：

1. 在 MetaSound 编辑器中创建音频图
2. 定义输入参数（如 Volume、Pitch、FilterCutoff）
3. 在蓝图中通过 `Set MetaSound Parameter` 节点控制参数值
4. 图内部的 DSP 节点自动响应参数变化

## C++ 用法

### 头文件引入

```cpp
// 核心图接口
#include "MetasoundGraphCoreModule.h"
#include "MetasoundGraph.h"
#include "MetasoundNodeInterface.h"
#include "MetasoundOperatorInterface.h"

// 数据引用和类型系统
#include "MetasoundDataReference.h"
#include "MetasoundDataReferenceCollection.h"
#include "MetasoundVertexData.h"

// 运算符和构建器
#include "MetasoundBuilderInterface.h"
#include "MetasoundExecutableOperator.h"
#include "MetasoundOperatorBuilder.h"
#include "MetasoundFacade.h"

// 音频缓冲区
#include "MetasoundAudioBuffer.h"

// 变量和字面量
#include "MetasoundVariable.h"
#include "MetasoundLiteral.h"
#include "MetasoundEnvironment.h"

// 动态图操作
#include "MetasoundDynamicOperatorTransactor.h"

// 图算法和调试
#include "MetasoundGraphAlgo.h"
#include "MetasoundGraphLinter.h"
#include "MetasoundRenderCost.h"
```

### 基本用法 — 创建自定义 MetaSound 运算符

以下示例展示如何创建一个简单的增益（Gain）运算符节点，这是 MetaSound 最基本的自定义节点模式：

```cpp
// 来源: 模式基于 MetasoundFacade.h / MetasoundExecutableOperator.h
#include "MetasoundExecutableOperator.h"
#include "MetasoundFacade.h"
#include "MetasoundVertex.h"
#include "MetasoundParamHelper.h"

namespace Metasound
{
    namespace GainNodeNames
    {
        METASOUND_PARAM(InputAudio, "Audio In", "Input audio signal.");
        METASOUND_PARAM(InputGain, "Gain", "Gain multiplier.");
        METASOUND_PARAM(OutputAudio, "Audio Out", "Output audio signal.");
    }

    class FGainOperator : public TExecutableOperator<FGainOperator>
    {
    public:
        FGainOperator(
            const FOperatorSettings& InSettings,
            TDataReadReference<FAudioBuffer> InAudioInput,
            TDataReadReference<float> InGain)
            : AudioInput(InAudioInput)
            , Gain(InGain)
            , AudioOutput(TDataWriteReference<FAudioBuffer>::CreateNew(InSettings))
        {
        }

        static const FNodeClassMetadata& GetNodeInfo()
        {
            auto CreateMeta = []()
            {
                FNodeClassMetadata Info;
                Info.ClassName = { "MyNodes", "Gain", "" };
                Info.MajorVersion = 1;
                Info.MinorVersion = 0;
                Info.DisplayName = METASOUND_GET_PARAM_NAME_AND_METADATA(OutputAudio);
                Info.Description = NSLOCTEXT("MyNodes", "GainDesc", "Applies gain to an audio signal.");
                Info.Author = TEXT("Me");
                Info.CategoryHierarchy = { NSLOCTEXT("MyNodes", "Audio", "Audio") };
                Info.DefaultInterface = DeclareVertexInterface();
                return Info;
            };
            static const FNodeClassMetadata Meta = CreateMeta();
            return Meta;
        }

        static FVertexInterface DeclareVertexInterface()
        {
            using namespace GainNodeNames;
            return FVertexInterface(
                FInputVertexInterface(
                    TInputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME(InputAudio),
                        METASOUND_GET_PARAM_METADATA(InputAudio)),
                    TInputDataVertex<float>(METASOUND_GET_PARAM_NAME(InputGain),
                        METASOUND_GET_PARAM_METADATA(InputGain), 1.0f)
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME(OutputAudio),
                        METASOUND_GET_PARAM_METADATA(OutputAudio))
                )
            );
        }

        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams,
            FBuildResults& OutResults)
        {
            using namespace GainNodeNames;

            const FOperatorSettings& Settings = InParams.OperatorSettings;
            const FInputVertexInterfaceData& InputData = InParams.InputData;

            TDataReadReference<FAudioBuffer> AudioIn =
                InputData.GetOrCreateDefaultDataReadReference<FAudioBuffer>(
                    METASOUND_GET_PARAM_NAME(InputAudio), Settings);
            TDataReadReference<float> GainValue =
                InputData.GetOrCreateDefaultDataReadReference<float>(
                    METASOUND_GET_PARAM_NAME(InputGain), Settings);

            return MakeUnique<FGainOperator>(Settings, AudioIn, GainValue);
        }

        void BindInputs(FInputVertexInterfaceData& InVertexData) override
        {
            using namespace GainNodeNames;
            InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputAudio), AudioInput);
            InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputGain), Gain);
        }

        void BindOutputs(FOutputVertexInterfaceData& InVertexData) override
        {
            using namespace GainNodeNames;
            InVertexData.BindWriteVertex(METASOUND_GET_PARAM_NAME(OutputAudio), AudioOutput);
        }

        void Execute()
        {
            const float G = *Gain;
            const float* InputData = AudioInput->GetData();
            float* OutputData = AudioOutput->GetData();
            const int32 NumFrames = AudioOutput->Num();

            for (int32 i = 0; i < NumFrames; ++i)
            {
                OutputData[i] = InputData[i] * G;
            }
        }

    private:
        TDataReadReference<FAudioBuffer> AudioInput;
        TDataReadReference<float> Gain;
        TDataWriteReference<FAudioBuffer> AudioOutput;
    };

    // 使用 FNodeFacade 简化节点注册
    using FGainNode = TNodeFacade<FGainOperator>;
}
```

### 基本用法 — 构建和执行图

```cpp
// 来源: 基于 MetasoundGraph.h, MetasoundOperatorBuilder.h
#include "MetasoundGraph.h"
#include "MetasoundOperatorBuilder.h"
#include "MetasoundOperatorBuilderSettings.h"

using namespace Metasound;

// 1. 创建图
FGuid GraphID = FGuid::NewGuid();
FGraph MyGraph(FName("TestGraph"), GraphID);

// 2. 添加节点到图
FGuid NodeA_ID = FGuid::NewGuid();
auto NodeA = MakeUnique<FGainNode>(FName("Gain1"), NodeA_ID);
MyGraph.AddNode(NodeA_ID, MoveTemp(NodeA));

// 3. 连接输入/输出
MyGraph.AddInputDataDestination(*MyGraph.FindNode(NodeA_ID), FName("Audio In"));
MyGraph.AddOutputDataSource(*MyGraph.FindNode(NodeA_ID), FName("Audio Out"));

// 4. 构建运算符
FOperatorBuilderSettings Settings = FOperatorBuilderSettings::GetDefaultSettings();
FOperatorBuilder Builder(Settings);

FOperatorSettings OpSettings(48000.0f, 100.0f);
FInputVertexInterfaceData InputData;
FMetasoundEnvironment Env;

FBuildResults Results;
TUniquePtr<IOperator> GraphOperator = Builder.BuildGraphOperator(
    FBuildGraphOperatorParams(MyGraph, OpSettings, InputData, Env),
    Results);

// 5. 检查构建结果
if (Results.Errors.Num() > 0)
{
    for (const auto& Error : Results.Errors)
    {
        UE_LOG(LogMetaSound, Warning, TEXT("Build Error: %s - %s"),
            *Error->GetErrorType().ToString(),
            *Error->GetErrorDescription().ToString());
    }
}
```

### 进阶用法 — 动态图修改（运行时添加/移除节点和连接）

```cpp
// 来源: 基于 MetasoundDynamicOperatorTransactor.h
#include "MetasoundDynamicOperatorTransactor.h"
#include "MetasoundGraph.h"
#include "MetasoundOperatorBuilder.h"

using namespace Metasound;

// 1. 创建初始图
FGuid GraphID = FGuid::NewGuid();
FGraph MyGraph(FName("DynamicGraph"), GraphID);

// 2. 创建 Transactor（图操纵器）
DynamicGraph::FDynamicOperatorTransactor Transactor(MyGraph);

// 3. 创建变换队列（用于与音频线程通信）
FOperatorSettings OpSettings(48000.0f, 100.0f);
FMetasoundEnvironment Env;
auto RenderCost = FGraphRenderCost::MakeGraphRenderCost();
auto TransformQueue = Transactor.CreateTransformQueue(OpSettings, Env, RenderCost);

// 4. 动态添加节点
FGuid NewNodeID = FGuid::NewGuid();
auto NewNode = MakeUnique<FGainNode>(FName("DynamicGain"), NewNodeID);
Transactor.AddNode(NewNodeID, MoveTemp(NewNode));

// 5. 动态建立连接
Transactor.AddDataEdge(
    SourceNodeID, FName("Audio Out"),
    NewNodeID, FName("Audio In"));

// 6. 动态移除连接（替换为静音值）
Transactor.RemoveDataEdge(
    SourceNodeID, FName("Audio Out"),
    NewNodeID, FName("Audio In"),
    FLiteral(0.0f),  // 替换为 0.0
    [](const FOperatorSettings& InSettings, FName DataType,
       const FLiteral& InLiteral, EDataReferenceAccessType AccessType)
        -> TOptional<FAnyDataReference>
    {
        // 自定义参考创建函数
        return TDataReadReference<float>::CreateNew(
            InLiteral.Get<FNone>() ? 0.0f : InLiteral.Get<float>());
    });

// 7. 动态移除节点（自动执行淡出处理）
Transactor.RemoveNode(RemovingNodeID);
```

### 进阶用法 — 拓扑排序和图分析

```cpp
// 来源: 基于 MetasoundGraphAlgo.h, MetasoundGraphLinter.h
#include "MetasoundGraphAlgo.h"
#include "MetasoundGraphLinter.h"

using namespace Metasound;

// 拓扑排序
TArray<const INode*> SortedNodes;
bool bSuccess = DirectedGraphAlgo::KahnTopologicalSort(MyGraph, SortedNodes);

if (bSuccess)
{
    for (const INode* Node : SortedNodes)
    {
        const FNodeClassMetadata& Meta = Node->GetMetadata();
        UE_LOG(LogMetaSound, Log, TEXT("Node: %s"), *Meta.ClassName.ToString());
    }
}

// 查找强连通组件（用于检测循环）
TArray<DirectedGraphAlgo::FStronglyConnectedComponent> Components;
if (DirectedGraphAlgo::TarjanStronglyConnectedComponents(MyGraph, Components))
{
    UE_LOG(LogMetaSound, Warning, TEXT("Found %d cycle(s) in graph!"), Components.Num());
}

// 图验证（Lint）
TArray<TUniquePtr<IOperatorBuildError>> Errors;
FGraphLinter::ValidateNoCyclesInGraph(MyGraph, Errors);
FGraphLinter::ValidateEdgeDataTypesMatch(MyGraph, Errors);
FGraphLinter::ValidateNoDuplicateInputs(MyGraph, Errors);
FGraphLinter::ValidateVerticesExist(MyGraph, Errors);
```

### 进阶用法 — 渲染开销追踪

```cpp
// 来源: 基于 MetasoundRenderCost.h
#include "MetasoundRenderCost.h"

// 创建图的渲染开销追踪器
TSharedRef<FGraphRenderCost> RenderCost = FGraphRenderCost::MakeGraphRenderCost();

// 为每个节点添加开销追踪
FNodeRenderCost NodeCost = RenderCost->AddNode(NodeInstanceID, Environment);

// 在运算符执行中报告开销（纳秒级别）
// NodeCost.SetRenderCost(ExecutionTimeNs);

// 计算图的总渲染开销
float TotalCost = RenderCost->ComputeGraphRenderCost();
```

## Demo 示例

一个完整的、可编译的自定义 MetaSound 运算符示例（带正弦波生成器）：

```cpp
// SinOscOperator.h
#pragma once

#include "MetasoundExecutableOperator.h"
#include "MetasoundParamHelper.h"
#include "MetasoundVertex.h"
#include "MetasoundVertexData.h"
#include "MetasoundAudioBuffer.h"
#include "MetasoundFacade.h"

namespace Metasound
{
    namespace SinOscNodeNames
    {
        METASOUND_PARAM(InputFrequency, "Frequency", "Frequency in Hz.");
        METASOUND_PARAM(OutputAudio, "Audio Out", "Output sine wave.");
    }

    class FSinOscOperator : public TExecutableOperator<FSinOscOperator>
    {
    public:
        FSinOscOperator(
            const FOperatorSettings& InSettings,
            TDataReadReference<float> InFrequency)
            : Frequency(InFrequency)
            , AudioOutput(TDataWriteReference<FAudioBuffer>::CreateNew(InSettings))
            , SampleRate(InSettings.GetSampleRate())
            , Phase(0.0f)
        {
        }

        static const FNodeClassMetadata& GetNodeInfo()
        {
            auto CreateMeta = []()
            {
                using namespace SinOscNodeNames;
                FNodeClassMetadata Info;
                Info.ClassName = { "MyNodes", "SineOscillator", "" };
                Info.MajorVersion = 1;
                Info.MinorVersion = 0;
                Info.DisplayName = NSLOCTEXT("MyNodes", "SineOsc", "Sine Oscillator");
                Info.Description = NSLOCTEXT("MyNodes", "SineOscDesc",
                    "Generates a sine wave at the specified frequency.");
                Info.Author = TEXT("Custom");
                Info.CategoryHierarchy = {
                    NSLOCTEXT("MyNodes", "Generators", "Generators")
                };
                Info.DefaultInterface = DeclareVertexInterface();
                return Info;
            };
            static const FNodeClassMetadata Meta = CreateMeta();
            return Meta;
        }

        static FVertexInterface DeclareVertexInterface()
        {
            using namespace SinOscNodeNames;
            return FVertexInterface(
                FInputVertexInterface(
                    TInputDataVertex<float>(
                        METASOUND_GET_PARAM_NAME(InputFrequency),
                        METASOUND_GET_PARAM_METADATA(InputFrequency),
                        440.0f)
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<FAudioBuffer>(
                        METASOUND_GET_PARAM_NAME(OutputAudio),
                        METASOUND_GET_PARAM_METADATA(OutputAudio))
                )
            );
        }

        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams,
            FBuildResults& OutResults)
        {
            using namespace SinOscNodeNames;

            TDataReadReference<float> Freq =
                InParams.InputData.GetOrCreateDefaultDataReadReference<float>(
                    METASOUND_GET_PARAM_NAME(InputFrequency),
                    InParams.OperatorSettings);

            return MakeUnique<FSinOscOperator>(InParams.OperatorSettings, Freq);
        }

        void BindInputs(FInputVertexInterfaceData& InVertexData) override
        {
            using namespace SinOscNodeNames;
            InVertexData.BindReadVertex(
                METASOUND_GET_PARAM_NAME(InputFrequency), Frequency);
        }

        void BindOutputs(FOutputVertexInterfaceData& InVertexData) override
        {
            using namespace SinOscNodeNames;
            InVertexData.BindWriteVertex(
                METASOUND_GET_PARAM_NAME(OutputAudio), AudioOutput);
        }

        void Execute()
        {
            const float Freq = *Frequency;
            float* OutputData = AudioOutput->GetData();
            const int32 NumFrames = AudioOutput->Num();

            const float PhaseIncrement = 2.0f * PI * Freq / SampleRate;

            for (int32 i = 0; i < NumFrames; ++i)
            {
                OutputData[i] = FMath::Sin(Phase);
                Phase += PhaseIncrement;
            }

            // 保持相位在合理范围内避免精度丢失
            while (Phase > 2.0f * PI)
            {
                Phase -= 2.0f * PI;
            }
        }

    private:
        TDataReadReference<float> Frequency;
        TDataWriteReference<FAudioBuffer> AudioOutput;
        float SampleRate;
        float Phase;
    };

    // 使用 TNodeFacade 简化节点定义
    using FSinOscNode = TNodeFacade<FSinOscOperator>;
}
```

## 模块依赖

MetaSoundGraphCore 是底层模块，其 Build.cs 中的依赖关系如下：

| 模块 | 用途 |
|---|---|
| `AudioMixerCore` | 音频混音器核心基础设施 |
| `AudioPlatformSettings` | 平台音频设置 |

> 注：该模块还依赖 Core、CoreUObject、Engine 等标准模块（按省略规则不列出）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复删除并重新添加 MetaSound 页面图时的断言错误 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 防止基于不可引用的父项创建 MetaSound 预设 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 在发行版本中防止目标 PageID 被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 清理之前修复 PIE 进入时死锁问题的代码 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 推测性修复进入 PIE 时的冻结问题 |

### 维护评价

**积极维护中** — MetaSound 作为 UE5 的核心音频系统之一，处于非常活跃的维护状态。从提交历史来看，近期的更新集中在：

- **稳定性修复**：多个关于 PIE（Play In Editor）模式下的死锁和冻结问题修复，表明该系统在持续改进运行时稳定性
- **页面图（Page Graph）管理**：修复页面图的删除和重建逻辑，这是 MetaSound 在 UE5.x 中引入的图分组功能
- **预设系统健壮性**：加强预设创建的校验逻辑，防止无效操作
- **构建类型防护**：确保关键逻辑在 Shipping 构建中保持正确行为

该项目创建于 2020 年（约 6 年前），作为一个大型音频系统（573 个源文件、7 个模块），其代码规模和复杂度都在持续增长。Epic Games 作为创建者和维护者，持续投入开发资源。**推荐使用** MetaSound 作为 UE5 项目的标准音频系统，特别适合需要高级音频处理能力的项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasound-overview-in-unreal-engine)（Epic 官方 MetaSound 文档）