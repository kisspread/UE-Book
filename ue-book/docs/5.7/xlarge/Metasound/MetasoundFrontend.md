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
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个基于节点图的音频系统，旨在将音频 DSP（数字信号处理）逻辑的创建和控制权完全交给声音设计师。它解决了传统音频系统中，复杂的音频处理逻辑（如动态混合、实时效果调制、程序化音效生成）通常需要程序员编写 C++ 代码的问题。

通过 MetaSound，设计师可以在蓝图中以可视化的方式构建音频处理图，实现：
1.  **采样精确控制**：音频参数的变化可以精确到每个音频采样，确保平滑无延迟的调制。
2.  **数据驱动**：游戏数据（如玩家速度、生命值）和蓝图事件可以直接作为参数输入到音频图中，驱动声音的变化。
3.  **模块化与复用**：音频处理逻辑可以封装为可复用的 MetaSound 资产，并在不同项目或音效间共享。
4.  **高性能**：系统在底层进行优化，确保复杂的音频图也能高效运行。

其核心是 `MetasoundFrontend` 模块，它定义了节点图的文档结构、数据类型、节点注册、分析器框架以及与蓝图交互的接口。

## 使用场景

-   **动态环境音效**：根据天气、时间、玩家位置实时混合和调制环境音（如风声、雨声、城市背景音）。
-   **交互式音乐**：创建能够根据游戏状态（如战斗、探索、剧情）无缝过渡和变化的音乐系统。
-   **程序化音效**：通过算法生成独一无二的音效，如武器射击声、魔法效果声，避免重复感。
-   **复杂音频处理链**：在蓝图中构建包含滤波器、延迟、失真、侧链压缩等效果的复杂处理链，用于角色语音、UI 音效等。
-   **音频可视化与分析**：利用内置的分析器（如包络跟随器、频谱分析）将音频数据转换为可用于游戏逻辑或视觉反馈的信号。

## 蓝图用法

MetaSound 的蓝图用法主要通过 `MetasoundFrontend` 模块提供的接口和 `MetasoundEngine` 模块暴露的资产类型实现。核心交互发生在 MetaSound 资产编辑器和蓝图图表中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaSound` | 从蓝图创建一个新的 MetaSound 资产实例。 | `UMetaSoundSource` / `UMetaSoundPatch` |
| `Set MetaSound Parameter` | 在运行时设置 MetaSound 实例的输入参数值。 | `UAudioComponent` |
| `Trigger MetaSound Event` | 向 MetaSound 实例发送一个触发事件（如 `OnPlay`）。 | `UAudioComponent` |
| `Get MetaSound Output` | 获取 MetaSound 实例的输出值（如分析器结果）。 | `UAudioComponent` |
| `Register Interface` | (C++ 侧) 注册一个自定义的参数接口，供 MetaSound 图使用。 | `IInterfaceRegistry` |
| `Register Node` | (C++ 侧) 注册一个自定义的 MetaSound 节点。 | `INodeClassRegistry` |

### 使用示例（蓝图描述）

1.  **播放一个 MetaSound**：
    -   在蓝图中，使用 `Spawn Sound 2D` 或 `Spawn Sound at Location` 节点，并选择一个 `MetaSound Source` 资产。
    -   或者，获取一个已存在的 `Audio Component` 引用，调用其 `Set Sound` 函数并传入 MetaSound 资产。

2.  **动态控制参数**：
    -   获取 `Audio Component` 引用。
    -   使用 `Set MetaSound Parameter` 节点，指定参数名称（如 `”Volume”`、`”Pitch”`）和新的值。
    -   参数值可以是 `Float`、`Int`、`Bool`、`String` 或自定义类型。

3.  **响应游戏事件**：
    -   在 MetaSound 资产编辑器中，为图添加一个 `Event` 输入节点（如 `OnPlay`）。
    -   在蓝图中，当游戏事件发生时（如角色跳跃），调用 `Trigger MetaSound Event` 节点，并传入对应的事件名称。

## C++ 用法

C++ 用法主要涉及扩展 MetaSound 系统，例如注册自定义数据类型、节点或分析器。

### 头文件引入

```cpp
#include "MetasoundFrontendRegistries.h"
#include "MetasoundFrontendDocument.h"
#include "MetasoundNodeInterface.h"
#include "MetasoundVertex.h"
```

### 基本用法

**注册一个自定义数据类型** (来自 `MetasoundPrimitives.h` 的模式)：
```cpp
// 在你的模块启动时注册
#include "MetasoundDataReferenceMacro.h"

// 假设你有一个自定义结构体 FMyAudioData
DECLARE_METASOUND_DATA_REFERENCE_TYPES(FMyAudioData, MYMODULE_API, FMyAudioDataTypeInfo, FMyAudioDataReadRef, FMyAudioDataWriteRef);
```

**注册一个简单的节点** (参考 `MetasoundFrontendNodeClassRegistry.h` 的模式)：
```cpp
#include "MetasoundNodeRegistrationMacro.h"

class FMyCustomNode : public Metasound::FNode
{
public:
    // ... 节点实现 ...
    static Metasound::FNodeClassMetadata CreateNodeClassMetadata();
    // ... 其他必要接口 ...
};

// 在模块启动时注册
METASOUND_REGISTER_NODE(FMyCustomNode);
```

### 进阶用法

**注册一个顶点分析器** (来自 `MetasoundFrontendAnalyzerRegistry.h`)：
```cpp
#include "Analysis/MetasoundFrontendAnalyzerRegistry.h"
#include "Analysis/MetasoundFrontendVertexAnalyzer.h"

class FMyCustomAnalyzer : public Metasound::Frontend::FVertexAnalyzerBase
{
public:
    static const FName& GetAnalyzerName();
    static const FName& GetDataType();
    // ... 分析器实现 ...
    virtual void Execute() override;
};

// 在模块启动时注册
METASOUND_REGISTER_VERTEX_ANALYZER_FACTORY(FMyCustomAnalyzer);
```

**使用分析器视图获取数据** (来自 `MetasoundFrontendAnalyzerView.h`)：
```cpp
#include "Analysis/MetasoundFrontendAnalyzerView.h"

// 假设你有一个 FMetasoundAnalyzerView 实例 (通常通过 FMetasoundGraphAnalyzerView 获取)
FMetasoundAnalyzerView& AnalyzerView = ...;
float EnvelopeValue;
if (AnalyzerView.TryGetOutputData<float>(TEXT(“EnvelopeValue”), EnvelopeValue))
{
    // 使用 EnvelopeValue 进行游戏逻辑，例如控制灯光亮度
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何创建一个简单的 MetaSound 节点，该节点将两个浮点数相加。

**MyAddNode.h**
```cpp
#pragma once

#include "MetasoundNodeInterface.h"
#include "MetasoundVertex.h"

namespace Metasound
{
    class FMyAddNode : public FNode
    {
    public:
        FMyAddNode(const FVertexName& InInstanceName, const FGuid& InInstanceID, const FVertexName& InVertexName);
        virtual ~FMyAddNode() = default;

        static FNodeClassMetadata CreateNodeClassMetadata();
        static FVertexInterface CreateVertexInterface();

        virtual const FVertexInterface& GetVertexInterface() const override;
        virtual TSharedRef<IOperator, ESPMode::ThreadSafe> CreateOperator() const override;

    private:
        FVertexInterface VertexInterface;
    };
}
```

**MyAddNode.cpp**
```cpp
#include "MyAddNode.h"
#include "MetasoundExecutableOperator.h"
#include "MetasoundPrimitives.h"
#include "MetasoundNodeRegistrationMacro.h"

namespace Metasound
{
    // 运算符实现
    class FMyAddOperator : public TExecutableOperator<FMyAddOperator>
    {
    public:
        FMyAddOperator(const FFloatReadRef& InA, const FFloatReadRef& InB, const FFloatWriteRef& InSum)
            : A(InA), B(InB), Sum(InSum)
        {}

        virtual void Execute() override
        {
            *Sum = *A + *B;
        }

    private:
        FFloatReadRef A;
        FFloatReadRef B;
        FFloatWriteRef Sum;
    };

    // 节点实现
    FMyAddNode::FMyAddNode(const FVertexName& InInstanceName, const FGuid& InInstanceID, const FVertexName& InVertexName)
        : FNode(InInstanceName, InInstanceID, InVertexName)
        , VertexInterface(CreateVertexInterface())
    {}

    FNodeClassMetadata FMyAddNode::CreateNodeClassMetadata()
    {
        return FNodeClassMetadata
        {
            .ClassName = { TEXT(“MyPlugin”), TEXT(“Add”), FGuid() },
            .MajorVersion = 1,
            .MinorVersion = 0,
            .DisplayName = INVTEXT(“My Add Node”),
            .Description = INVTEXT(“Adds two floats together.”),
            .Author = TEXT(“Your Name”),
            .PromptIfMissing = INVTEXT(“Missing My Add Node”),
            .DefaultInterface = CreateVertexInterface(),
            .CategoryHierarchy = { INVTEXT(“Math”) }
        };
    }

    FVertexInterface FMyAddNode::CreateVertexInterface()
    {
        return FVertexInterface(
            FInputVertexInterface(
                FInputDataVertex(FFloatTypeInfo::GetTypeName(), FName(“A”), INVTEXT(“A”)),
                FInputDataVertex(FFloatTypeInfo::GetTypeName(), FName(“B”), INVTEXT(“B”))
            ),
            FOutputVertexInterface(
                FOutputDataVertex(FFloatTypeInfo::GetTypeName(), FName(“Sum”), INVTEXT(“Sum”))
            )
        );
    }

    const FVertexInterface& FMyAddNode::GetVertexInterface() const
    {
        return VertexInterface;
    }

    TSharedRef<IOperator, ESPMode::ThreadSafe> FMyAddNode::CreateOperator() const
    {
        FFloatReadRef A = GetVertexInputDataReference<FFloatReadRef>(FName(“A”));
        FFloatReadRef B = GetVertexInputDataReference<FFloatReadRef>(FName(“B”));
        FFloatWriteRef Sum = GetVertexOutputDataReference<FFloatWriteRef>(FName(“Sum”));

        return MakeShared<FMyAddOperator, ESPMode::ThreadSafe>(A, B, Sum);
    }

    // 注册节点
    METASOUND_REGISTER_NODE(FMyAddNode);
}
```

## 模块依赖

要使用或扩展 MetaSound，你的模块通常需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 的核心前端逻辑，包括文档结构、节点注册、分析器框架。扩展 MetaSound 必须依赖此模块。 |
| `MetasoundGraphCore` | MetaSound 图的核心运行时逻辑，包括算子、数据引用等。 |
| `MetasoundStandardNodes` | MetaSound 的标准节点库（如数学运算、音频生成器、滤波器）。 |
| `MetasoundEngine` | MetaSound 与 UE 音频引擎集成的模块，提供 `UMetaSoundSource` 等资产类型。 |
| `AudioMixer` | UE 的底层音频混合器，MetaSound 的 DSP 处理依赖于此。 |
| `SignalProcessing` | 提供各种 DSP 算法（FFT、滤波器等），MetaSound 节点可能使用。 |

## 维护状态

### 近期更新

```
- cd60e9b91c03 Reparent MetaSound member metadata when building from builder API
- 15c56a9302d7 Fix MetaSound variable numeric defaults not being draggable
- 2cfc5b3e0cbc Fix infinite recursion in MetaSounds interaction between builder delegates and preset member metadata that is now handled by preset transform - Added protection for editor crash
```

### 维护评价

MetaSound 是一个**活跃维护中**的核心音频系统。
-   **创建时间**：约 5 年前（2020年），已度过初期阶段，成为 UE 音频管线的重要组成部分。
-   **更新频率**：从近期提交记录看，更新频繁，主要集中在功能完善、Bug 修复和 API 优化上。
-   **维护状态**：由 Epic Games 官方团队持续维护和开发，是 UE5 音频功能的重点发展方向。
-   **已知限制**：作为复杂的实时音频系统，学习曲线较陡峭。对于非常简单的音效，使用传统 Sound Cue 可能更直接。
-   **推荐使用**：**强烈推荐**用于任何需要动态、交互式或程序化音频的项目。它是实现下一代游戏音频体验的关键工具。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
-   [官方文档](https://docs.unrealengine.com/5.7/en-US/overview-of-metasounds-in-unreal-engine/) (UE5 官方文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)