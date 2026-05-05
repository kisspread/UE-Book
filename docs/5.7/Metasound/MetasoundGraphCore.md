# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-22 |
| 年龄标签 | 🆕（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound) | |

---

## 用途

MetaSound 是 UE5 的下一代音频系统，用**基于节点的 DSP 图**取代传统的 Sound Cue。它允许声音设计师通过可视化节点图完全控制音频信号的生成、处理和调制，实现**采样精度**的音频处理。

**MetasoundGraphCore** 是整个 MetaSound 系统的**底层图基础设施模块**，提供：

- **图结构**：`FGraph`、`FNode`、`FDataEdge` 等核心图数据结构
- **算子系统**：`IOperator` 接口及 `FGraphOperator` 执行引擎，负责运行时音频处理
- **构建系统**：`FOperatorBuilder` 将图描述编译为可执行的算子链
- **数据引用**：类型安全的 `TDataReadReference`/`TDataWriteReference` 用于节点间数据传递
- **音频缓冲**：`FAudioBuffer` 提供 SIMD 对齐的音频数据容器
- **图验证**：`FGraphLinter` 检测环路、类型不匹配等图错误
- **动态图**：支持运行时修改图结构的 `FDynamicOperatorTransactor`

简而言之，GraphCore 是 MetaSound 的"引擎内核"——所有上层功能（蓝图 API、编辑器 UI、标准节点库）都建立在这个模块之上。

## 使用场景

- 你需要从零开始构建自定义 MetaSound 节点类型 → 使用 `FNodeFacade` + `IOperator` 模式
- 你需要在 C++ 中程序化创建和执行 MetaSound 图 → 使用 `FGraph` + `FOperatorBuilder` + `FGraphOperator`
- 你需要实现运行时可动态修改的音频处理链 → 使用 `FDynamicOperatorTransactor`
- 你需要注册自定义音频数据类型供 MetaSound 系统使用 → 使用 `DECLARE_METASOUND_DATA_REFERENCE_TYPES` 宏
- 你需要追踪音频图的渲染性能开销 → 使用 `FGraphRenderCost` / `FNodeRenderCost`

## 蓝图用法

MetasoundGraphCore 是纯 C++ 底层模块，不直接暴露蓝图节点。蓝图交互通过 **MetasoundFrontend** 和 **MetasoundEngine** 模块提供。但 GraphCore 定义了蓝图可访问的变量节点类名：

### 变量节点类名（用于程序化查找）

| 函数 | 说明 | 所在类 |
|---|---|---|
| `GetVariableNodeClassName<T>()` | 获取指定类型的变量节点类名 | `Metasound::VariableNames` |
| `GetVariableMutatorNodeClassName<T>()` | 获取变量修改器节点类名 | `Metasound::VariableNames` |
| `GetVariableAccessorNodeClassName<T>()` | 获取变量访问器节点类名 | `Metasound::VariableNames` |
| `GetVariableDeferredAccessorNodeClassName<T>()` | 获取延迟变量访问器节点类名 | `Metasound::VariableNames` |

> 蓝图中使用 MetaSound 的完整工作流请参考 MetasoundEngine 模块文档。

## C++ 用法

### 头文件引入

```cpp
// 核心图结构
#include "MetasoundGraph.h"
#include "MetasoundNode.h"
#include "MetasoundFacade.h"

// 算子系统
#include "MetasoundOperatorBuilder.h"
#include "MetasoundGraphOperator.h"
#include "MetasoundExecutableOperator.h"

// 数据类型
#include "MetasoundAudioBuffer.h"
#include "MetasoundDataReference.h"
#include "MetasoundLiteral.h"
#include "MetasoundVariable.h"

// 工具
#include "MetasoundParamHelper.h"
#include "MetasoundGraphLinter.h"
#include "MetasoundOperatorSettings.h"
```

### 基本用法：创建自定义节点

使用 `FNodeFacade` 是创建自定义 MetaSound 节点最简洁的方式。你的算子类需要提供两个静态方法：

```cpp
// 来源: MetasoundGraphCore/Public/MetasoundFacade.h

// 1. 定义算子（运行时执行逻辑）
class FMyGainOperator : public Metasound::TExecutableOperator<FMyGainOperator>
{
public:
    FMyGainOperator(
        const Metasound::FBuildOperatorParams& InParams,
        Metasound::TDataReadReference<Metasound::FAudioBuffer> InAudioInput,
        Metasound::TDataReadReference<float> InGain)
        : AudioInput(InAudioInput)
        , Gain(InGain)
        , AudioOutput(Metasound::TDataWriteReferenceFactory<Metasound::FAudioBuffer>::CreateAnyArgs(InParams.OperatorSettings))
    {
    }

    // 必须：工厂方法
    static TUniquePtr<Metasound::IOperator> CreateOperator(
        const Metasound::FBuildOperatorParams& InParams,
        Metasound::FBuildResults& OutResults);

    // 必须：节点元数据
    static const Metasound::FNodeClassMetadata& GetNodeInfo();

    // 绑定输入输出
    virtual void BindInputs(Metasound::FInputVertexInterfaceData& InVertexData) override
    {
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputAudio), AudioInput);
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputGain), Gain);
    }

    virtual void BindOutputs(Metasound::FOutputVertexInterfaceData& InVertexData) override
    {
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(OutputAudio), AudioOutput);
    }

    // 每个音频块执行一次
    void Execute()
    {
        const Metasound::FAudioBuffer& Input = *AudioInput;
        Metasound::FAudioBuffer& Output = *AudioOutput;
        const float GainValue = *Gain;

        for (int32 i = 0; i < Input.Num(); ++i)
        {
            Output.GetData()[i] = Input.GetData()[i] * GainValue;
        }
    }

private:
    Metasound::TDataReadReference<Metasound::FAudioBuffer> AudioInput;
    Metasound::TDataReadReference<float> Gain;
    Metasound::TDataWriteReference<Metasound::FAudioBuffer> AudioOutput;
};
```

```cpp
// 2. 使用 FNodeFacade 注册节点
// 来源: MetasoundGraphCore/Public/MetasoundFacade.h

namespace Metasound
{
    // FNodeFacade 自动处理 INode 的样板代码
    // TFacadeOperatorClass<FMyGainOperator> 验证 CreateOperator 和 GetNodeInfo 存在
    class FMyGainNode : public FNodeFacade
    {
    public:
        FMyGainNode(const FNodeData& InNodeData, TSharedRef<const FNodeClassMetadata> InMetadata)
            : FNodeFacade(InNodeData, TFacadeOperatorClass<FMyGainOperator>(), InMetadata)
        {
        }
    };
}
```

### 基本用法：定义参数

```cpp
// 来源: MetasoundGraphCore/Public/MetasoundParamHelper.h

namespace Metasound
{
    namespace MyGainNodeNames
    {
        // 定义输入参数（名称、显示名、提示文本）
        METASOUND_PARAM(InputAudio, "Audio In", "Input audio signal");
        METASOUND_PARAM(InputGain, "Gain", "Gain multiplier (1.0 = no change)");
        METASOUND_PARAM(OutputAudio, "Audio Out", "Output audio signal");
    }
}
```

### 进阶用法：程序化构建和执行图

```cpp
// 综合来源: MetasoundGraph.h, MetasoundOperatorBuilder.h, MetasoundGraphOperator.h

#include "MetasoundGraph.h"
#include "MetasoundOperatorBuilder.h"
#include "MetasoundOperatorSettings.h"
#include "MetasoundEnvironment.h"

void BuildAndExecuteMetaSoundGraph()
{
    using namespace Metasound;

    // 1. 配置音频参数：48kHz 采样率，目标 100Hz 块率
    FOperatorSettings Settings(48000, 100.0f);

    // 2. 创建图实例
    FGraph Graph(
        FName("MyProceduralGraph"),
        FGuid::NewGuid());

    // 3. 创建节点（假设已有注册的节点类）
    // FNode MyOscillatorNode(...);
    // FNode MyGainNode(...);

    // 4. 添加边连接节点
    // Graph.AddDataEdge(MyOscillatorNode, "AudioOut", MyGainNode, "AudioIn");

    // 5. 添加图的输入输出
    // Graph.AddInputVertex(...);
    // Graph.AddOutputVertex(...);

    // 6. 验证图结构
    TArray<TUniquePtr<IOperatorBuildError>> Errors;
    bool bValid = FGraphLinter::ValidateNoCyclesInGraph(Graph, Errors);
    bValid &= FGraphLinter::ValidateEdgeDataTypesMatch(Graph, Errors);
    bValid &= FGraphLinter::ValidateVerticesExist(Graph, Errors);

    if (!bValid)
    {
        for (const auto& Error : Errors)
        {
            UE_LOG(LogMetaSound, Error, TEXT("Graph error: %s"),
                *Error->GetErrorDescription().ToString());
        }
        return;
    }

    // 7. 构建可执行算子
    FOperatorBuilderSettings BuilderSettings = FOperatorBuilderSettings::GetDefaultSettings();
    FOperatorBuilder Builder(BuilderSettings);

    FBuildGraphOperatorParams BuildParams{
        Graph,
        Settings,
        FMetasoundEnvironment{}
    };
    FBuildResults BuildResults;

    TUniquePtr<IOperator> Operator = Builder.BuildGraphOperator(BuildParams, BuildResults);

    // 8. 绑定输入输出数据
    FInputVertexInterfaceData InputData;
    FOutputVertexInterfaceData OutputData;
    Operator->BindInputs(InputData);
    Operator->BindOutputs(OutputData);

    // 9. 执行（每帧调用一次，处理一个音频块）
    Operator->Execute();
}
```

### 进阶用法：注册自定义数据类型

```cpp
// 来源: MetasoundGraphCore/Public/MetasoundDataReferenceMacro.h

// 在头文件中声明
DECLARE_METASOUND_DATA_REFERENCE_TYPES(
    FMyCustomType,                    // 数据类型
    MYMODULE_API,                     // 模块导出宏
    FMyCustomTypeInfo,                // 类型信息 typedef
    FMyCustomReadRef,                 // 读引用 typedef
    FMyCustomWriteRef                 // 写引用 typedef
)

// 在 .cpp 文件中定义
DEFINE_METASOUND_DATA_TYPE(FMyCustomType, "MyCustom")
```

### 进阶用法：使用变量（Variable）实现延迟数据

```cpp
// 来源: MetasoundGraphCore/Public/MetasoundVariable.h

// TVariable 包含当前值和上一帧的值，支持延迟数据复制
// 适用于需要"上一帧状态"的逻辑（如触发器检测）

Metasound::TVariable<float> MyVariable(
    Metasound::FLiteral(1.0f),  // 初始值
    Metasound::MetasoundVariablePrivate::FConstructWithLiteral{}
);

// 初始化数据引用
MyVariable.InitDataReference(OperatorSettings);

// 获取当前值
Metasound::TDataReadReference<float> CurrentRef = MyVariable.GetDataReference();

// 获取延迟值（上一帧）
Metasound::TDataReadReference<float> DelayedRef = MyVariable.GetDelayedDataReference();

// 在帧末尾复制数据（当前值 → 延迟值）
if (MyVariable.RequiresDelayedDataCopy())
{
    MyVariable.CopyReferencedData();
}
```

## Demo 示例

一个完整的自定义 MetaSound 节点实现——简单的音频增益节点：

```cpp
// MyGainNode.h
#pragma once

#include "MetasoundFacade.h"
#include "MetasoundExecutableOperator.h"
#include "MetasoundAudioBuffer.h"
#include "MetasoundParamHelper.h"
#include "MetasoundVertex.h"

namespace Metasound
{
    namespace MyGainNodeNames
    {
        METASOUND_PARAM(InputAudio, "Audio In", "Input audio signal");
        METASOUND_PARAM(InputGain, "Gain", "Gain multiplier");
        METASOUND_PARAM(OutputAudio, "Audio Out", "Output audio signal");
    }

    class FMyGainOperator : public TExecutableOperator<FMyGainOperator>
    {
    public:
        FMyGainOperator(
            const FBuildOperatorParams& InParams,
            TDataReadReference<FAudioBuffer> InAudioInput,
            TDataReadReference<float> InGain);

        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams,
            FBuildResults& OutResults);

        static const FNodeClassMetadata& GetNodeInfo();

        virtual void BindInputs(FInputVertexInterfaceData& InVertexData) override;
        virtual void BindOutputs(FOutputVertexInterfaceData& InVertexData) override;
        void Execute();

    private:
        TDataReadReference<FAudioBuffer> AudioInput;
        TDataReadReference<float> Gain;
        TDataWriteReference<FAudioBuffer> AudioOutput;
    };

    class FMyGainNode : public FNodeFacade
    {
    public:
        FMyGainNode(const FNodeData& InNodeData, TSharedRef<const FNodeClassMetadata> InMetadata)
            : FNodeFacade(InNodeData, TFacadeOperatorClass<FMyGainOperator>(), InMetadata)
        {
        }
    };
}
```

```cpp
// MyGainNode.cpp
#include "MyGainNode.h"

namespace Metasound
{
    using namespace MyGainNodeNames;

    FMyGainOperator::FMyGainOperator(
        const FBuildOperatorParams& InParams,
        TDataReadReference<FAudioBuffer> InAudioInput,
        TDataReadReference<float> InGain)
        : AudioInput(InAudioInput)
        , Gain(InGain)
        , AudioOutput(TDataWriteReferenceFactory<FAudioBuffer>::CreateAnyArgs(InParams.OperatorSettings))
    {
    }

    TUniquePtr<IOperator> FMyGainOperator::CreateOperator(
        const FBuildOperatorParams& InParams,
        FBuildResults& OutResults)
    {
        using namespace MyGainNodeNames;

        TDataReadReference<FAudioBuffer> AudioIn =
            InParams.InputData.GetOrConstructDataReadReference<FAudioBuffer>(
                METASOUND_GET_PARAM_NAME(InputAudio), InParams.OperatorSettings);

        TDataReadReference<float> GainIn =
            InParams.InputData.GetOrConstructDataReadReference<float>(
                METASOUND_GET_PARAM_NAME(InputGain), 1.0f);

        return MakeUnique<FMyGainOperator>(InParams, AudioIn, GainIn);
    }

    const FNodeClassMetadata& FMyGainOperator::GetNodeInfo()
    {
        auto InitNodeInfo = []() -> FNodeClassMetadata
        {
            FNodeClassMetadata Info;
            Info.ClassName = { "MyNodes", "Gain", "" };
            Info.MajorVersion = 1;
            Info.MinorVersion = 0;
            Info.DisplayName = LOCTEXT("MyGainDisplayName", "My Gain");
            Info.Description = LOCTEXT("MyGainDesc", "Applies gain to an audio signal");
            Info.Author = "Custom";
            Info.PromptIfMissing = PluginNodeMissingPrompt;
            Info.DefaultInterface = FVertexInterface(
                FInputVertexInterface(
                    TInputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME_AND_METADATA(InputAudio)),
                    TInputDataVertex<float>(METASOUND_GET_PARAM_NAME_AND_METADATA(InputGain))
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<FAudioBuffer>(METASOUND_GET_PARAM_NAME_AND_METADATA(OutputAudio))
                )
            );
            return Info;
        };

        static const FNodeClassMetadata Info = InitNodeInfo();
        return Info;
    }

    void FMyGainOperator::BindInputs(FInputVertexInterfaceData& InVertexData)
    {
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputAudio), AudioInput);
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(InputGain), Gain);
    }

    void FMyGainOperator::BindOutputs(FOutputVertexInterfaceData& InVertexData)
    {
        InVertexData.BindReadVertex(METASOUND_GET_PARAM_NAME(OutputAudio), AudioOutput);
    }

    void FMyGainOperator::Execute()
    {
        const FAudioBuffer& Input = *AudioInput;
        FAudioBuffer& Output = *AudioOutput;
        const float GainValue = *Gain;
        const int32 NumSamples = Input.Num();

        const float* InputData = Input.GetData();
        float* OutputData = Output.GetData();

        for (int32 i = 0; i < NumSamples; ++i)
        {
            OutputData[i] = InputData[i] * GainValue;
        }
    }
}
```

## 模块依赖

MetasoundGraphCore 的独特依赖（排除标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `AudioMixer` | 提供 `FAlignedFloatBuffer` 等 SIMD 对齐音频缓冲区 |
| `SignalProcessing` | DSP 数学运算和音频信号处理工具函数 |

## 维护状态

### 近期更新

```
- dccf718ec762 Fix strange interaction with MetaSound variables and subgraphs causing delayed trigger variables to not execute. #jira UE-307830
- 39badeb09b1c Experimental Support for Polymorphic Datatypes in Metasound
- d2415f5f6e79 Fix static analysis warning - possible module by zero
```

### 维护评价

MetaSound 是 Epic 的**战略性音频系统**，旨在取代传统 Sound Cue，维护状态**非常活跃**：

- **创建时间**：2020 年 5 月，随 UE5 早期开发启动
- **更新频率**：持续有功能性更新和 bug 修复，包括新的多态数据类型支持（实验性）
- **活跃度**：作为 UE5 核心音频系统，由 Epic 音频团队持续维护
- **已知限制**：
  - 多态数据类型（Polymorphic Datatypes）仍标记为实验性（`UE_EXPERIMENTAL(5.7)`）
  - `IOperator::GetInputs()`/`GetOutputs()` 已废弃，需迁移到 `BindInputs()`/`BindOutputs()`
  - `FGraph::SetVertexInterface()` 在 5.6 已废弃
- **推荐使用**：✅ 强烈推荐。MetaSound 是 UE5 官方推荐的音频系统，GraphCore 作为其基础设施稳定可靠

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundGraphCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)