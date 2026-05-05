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

MetaSound 是 UE5 的**节点式音频 DSP 图系统**，替代传统 Sound Cue，让声音设计师在可视化图编辑器中通过连接节点来构建完整的音频处理链路。

与 Sound Cue 的根本区别：

- **采样级精度**：所有音频处理在采样级别运行，支持精确的调制和参数控制
- **完全可编程 DSP 图**：不是简单的"选择音源+加效果"，而是从振荡器、噪声生成器等基础 DSP 原语开始，自由构建任意音频处理逻辑
- **音频参数驱动**：游戏数据（如速度、距离、生命值）可直接映射为音频参数，实时调制 DSP 图中的任意节点
- **音频事件系统**：通过 Trigger 事件驱动图中的逻辑流，实现复杂的音频状态机

简单来说：Sound Cue 是"播放预制音频 + 简单混合"，MetaSound 是"从零合成和处理音频信号"。

## 使用场景

- 你需要**程序化生成音效**（如引擎轰鸣、风声、脚步声），根据游戏状态实时变化 → 用 MetaSound 的振荡器、噪声生成器、滤波器等节点从零构建
- 你需要**复杂的音频调制**，如根据车速改变引擎音高和滤波器截止频率 → 用 MetaSound 的音频参数将游戏数据直接注入 DSP 图
- 你需要**精确的音乐节奏系统**，如 BPM 同步的节拍器或音乐触发器 → 用 MetaSound 的 BPM 节点和 Trigger 系统
- 你需要**多层音频混合和动态处理**，如根据环境自动调整混响和压缩 → 用 MetaSound 的 Dynamics、Reverbs、Mix 节点分类
- 你正在做一个**音频密集型项目**（音乐游戏、沉浸式模拟），需要比 Sound Cue 更强的音频编程能力 → 全面采用 MetaSound

## 模块概览

本插件由 7 个模块组成，形成完整的 MetaSound 运行时和编辑器架构：

| 模块 | 类型 | 职责 |
|---|---|---|
| **MetasoundGraphCore** | Runtime | 图核心数据结构：节点、顶点、边、操作符的基础设施 |
| **MetasoundFrontend** | Runtime | 前端数据表示：MetaSound 资产的序列化、编译、类注册 |
| **MetasoundEngine** | Runtime | 运行时引擎：MetaSound 资产的实例化、播放、参数注入 |
| **MetasoundGenerator** | Runtime | 音频生成器：将编译后的 MetaSound 图转化为实际音频输出 |
| **MetasoundStandardNodes** | Runtime | 标准节点库：振荡器、滤波器、触发器、数学运算等内置节点 |
| **MetasoundEditor** | Runtime | 编辑器：MetaSound 图编辑器 UI、节点拖放、连线交互 |
| **MetasoundEngineTest** | Runtime | 测试模块：引擎功能的自动化测试 |

> 本文档重点介绍 **MetasoundStandardNodes** 模块，即 MetaSound 的内置标准节点库。

---

## MetasoundStandardNodes 模块详解

标准节点库提供了 MetaSound 图中可直接使用的所有内置节点，按功能分为以下类别：

### 节点分类

| 分类 | 说明 | 典型节点 |
|---|---|---|
| **Generators** | 信号生成 | Sine/Saw/Triangle/Square 振荡器、噪声生成器 |
| **Envelopes** | 包络跟踪 | Envelope Follower |
| **Trigger** | 触发器逻辑 | Toggle、Repeat、Accumulator、Compare、OnThreshold |
| **Math** | 数学运算 | 基础算术、比较、Clamp |
| **Mix** | 混合 | 音频混合、增益控制 |
| **Filters** | 滤波器 | 各类音频滤波 |
| **Dynamics** | 动态处理 | 压缩、限制 |
| **Delays** | 延迟 | 延迟线、合唱 |
| **Reverbs** | 混响 | 各类混响效果 |
| **Music** | 音乐工具 | BPM 转秒数、音阶量化 |
| **RandomUtils** | 随机工具 | 随机整数/浮点数生成 |
| **WaveTables** | 波表 | 波表相关操作 |
| **Spatialization** | 空间化 | 3D 音频空间化 |
| **Io** | 输入输出 | 音频输入/输出 |
| **Debug** | 调试 | 调试和可视化工具 |

### 核心节点

#### 振荡器节点（Generators）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Sine Oscillator` | 正弦波振荡器 | `FSineOscilatorNode` |
| `Saw Oscillator` | 锯齿波振荡器 | `FSawOscilatorNode` |
| `Triangle Oscillator` | 三角波振荡器 | `FTriangleOscilatorNode` |
| `Square Oscillator` | 方波振荡器 | `FSquareOscilatorNode` |
| `Noise` | 噪声生成器（可设定种子） | `FNoiseNode` |

所有振荡器共享基类 `FOscilatorNodeBase`，提供统一的输入接口：
- **Frequency**：频率（默认 440Hz）
- **Glide Time**：频率滑动时间
- **Enable**：启用/禁用

#### 触发器节点（Trigger）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Trigger Toggle` | 触发切换开关（开/关交替） | `FTriggerToggleNode` |
| `Trigger Repeat` | 触发重复（按时间间隔重复触发） | `FTriggerRepeatNode` |
| `Trigger Accumulate (N)` | 触发累积器（N 个输入全部触发后才输出） | `TTriggerAccumulatorOperator<N>` |
| `Trigger Compare` | 触发比较（比较 A 和 B，输出 True/False 触发） | `TTriggerCompareNodeOperator<T>` |
| `Trigger On Threshold` | 阈值触发（音频信号超过阈值时触发） | `FTriggerOnThresholdNode` |

#### 包络和分析节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Envelope Follower` | 包络跟踪器（Peak/MeanSquared/RMS 模式） | `FEnvelopeFollowerNode` |

#### 音乐节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BPM To Seconds` | 将 BPM 转换为秒数（支持节拍倍数和全音符分割） | `FBPMToSecondsNode` |

#### 值和随机节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Value` | 值节点（触发时设置/重置输出值） | `TValueOperator<T>` |
| `Random (Int)` | 随机整数生成（可设定种子和范围） | `TRandomNodeSpecialization<int32>` |
| `Random (Float)` | 随机浮点数生成（可设定种子和范围） | `TRandomNodeSpecialization<float>` |

---

## 蓝图用法

MetaSound 的蓝图交互主要通过 **MetaSound Source / MetaSound Patch** 资产和 **Audio Component** 进行。标准节点本身在 MetaSound 图编辑器中使用，不直接暴露为蓝图节点。

### 核心交互节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Float Parameter` | 设置 MetaSound 的浮点参数 | `UAudioComponent` |
| `Set Int Parameter` | 设置 MetaSound 的整数参数 | `UAudioComponent` |
| `Set Bool Parameter` | 设置 MetaSound 的布尔参数 | `UAudioComponent` |
| `Set Trigger Parameter` | 触发 MetaSound 中的 Trigger 事件 | `UAudioComponent` |
| `Play` | 播放 MetaSound | `UAudioComponent` |
| `Stop` | 停止 MetaSound | `UAudioComponent` |

### 使用示例（蓝图描述）

**场景：根据车速动态调整引擎音效**

1. 创建一个 MetaSound Source 资产，在图编辑器中构建：
   - 添加 `Sine Oscillator` 节点，频率连接到一个 `Float` 输入参数 `EngineRPM`
   - 添加 `Noise` 节点，连接到另一个输入参数
   - 通过 `Mix` 节点混合振荡器和噪声
   - 添加 `Filter` 节点，截止频率连接到 `EngineRPM`
   - 输出到音频输出

2. 在蓝图中：
   - 创建 `Audio Component`，设置 Sound 为该 MetaSound Source
   - 在 Tick 中获取车速，调用 `Set Float Parameter("EngineRPM", Speed * RPMFactor)`
   - MetaSound 图中的振荡器频率和滤波器截止频率会实时跟随车速变化

**场景：使用 Trigger 系统实现节拍同步**

1. MetaSound 图中：
   - 添加 `BPM To Seconds` 节点，BPM 设为游戏音乐的 BPM
   - 输出连接到 `Trigger Repeat` 节点的间隔时间
   - `Trigger Repeat` 的输出触发一个 `Sine Oscillator` 的 Enable 输入
   - 实现每拍发出一个短促的正弦音

2. 蓝图中通过 `Set Trigger Parameter` 可以手动触发图中的 Trigger 输入

---

## C++ 用法

### 头文件引入

```cpp
// 使用标准节点
#include "MetasoundStandardNodesNames.h"
#include "MetasoundStandardNodesCategories.h"

// 特定节点
#include "MetasoundOscillatorNodes.h"
#include "MetasoundNoiseGenerator.h"
#include "MetasoundEnvelopeFollowerNode.h"
#include "MetasoundTriggerToggleNode.h"
#include "MetasoundTriggerRepeatNode.h"
#include "MetasoundRandomNode.h"
#include "MetasoundValueNode.h"
```

### 基本用法：创建自定义 MetaSound 节点

MetaSound 的节点通过 `FNodeFacade` 或 `FBasicNode` 基类创建。标准节点展示了标准的节点注册模式：

```cpp
// 来源: MetasoundStandardNodes/Public/MetasoundEnvelopeFollowerNode.h
// 包络跟踪器节点 - 继承 FNodeFacade

#include "MetasoundFacade.h"

namespace Metasound
{
    class FEnvelopeFollowerNode : public FNodeFacade
    {
    public:
        // 前端构造函数（由 MetaSound 系统调用）
        FEnvelopeFollowerNode(const FNodeInitData& InitData);
        
        // 带节点数据的构造函数
        FEnvelopeFollowerNode(FNodeData InNodeData, 
                              TSharedRef<const FNodeClassMetadata> InClassMetadata);

        // 创建节点元数据（名称、描述、分类等）
        static FNodeClassMetadata CreateNodeClassMetadata();
    };
}
```

### 进阶用法：模板化节点（Trigger Compare）

标准节点大量使用模板来支持多种数据类型。以 `Trigger Compare` 节点为例：

```cpp
// 来源: MetasoundStandardNodes/Public/MetasoundTriggerCompareNode.h
// Trigger Compare 节点 - 比较两个值并输出 True/False 触发

#include "MetasoundExecutableOperator.h"
#include "MetasoundFacade.h"
#include "MetasoundPrimitives.h"
#include "MetasoundTrigger.h"

namespace Metasound
{
    // 比较类型枚举
    enum class ETriggerComparisonType
    {
        Equals,
        NotEquals,
        LessThan,
        GreaterThan,
        LessThanOrEquals,
        GreaterThanOrEquals
    };

    // 模板化操作符 - 支持任意可比较类型
    template<typename ValueType>
    class TTriggerCompareNodeOperator : public TExecutableOperator<TTriggerCompareNodeOperator<ValueType>>
    {
    public:
        // 定义默认输入输出接口
        static const FVertexInterface& GetDefaultInterface()
        {
            static const FVertexInterface DefaultInterface(
                FInputVertexInterface(
                    TInputDataVertex<FTrigger>("Compare"),      // 触发比较
                    TInputDataVertex<ValueType>("A"),            // 值 A
                    TInputDataVertex<ValueType>("B"),            // 值 B
                    TInputDataVertex<FEnumTriggerComparisonType>("Type", 
                        (int32)ETriggerComparisonType::Equals)   // 比较类型
                ),
                FOutputVertexInterface(
                    TOutputDataVertex<FTrigger>("True"),         // 比较为真时触发
                    TOutputDataVertex<FTrigger>("False")         // 比较为假时触发
                )
            );
            return DefaultInterface;
        }

        // 工厂方法 - 由 MetaSound 编译器调用
        static TUniquePtr<IOperator> CreateOperator(
            const FBuildOperatorParams& InParams, 
            FBuildResults& OutResults)
        {
            const FInputVertexInterfaceData& InputData = InParams.InputData;
            
            FTriggerReadRef CompareTrigger = InputData.GetOrCreateDefaultDataReadReference<FTrigger>(
                "Compare", InParams.OperatorSettings);
            TDataReadReference<ValueType> A = InputData.GetOrCreateDefaultDataReadReference<ValueType>(
                "A", InParams.OperatorSettings);
            TDataReadReference<ValueType> B = InputData.GetOrCreateDefaultDataReadReference<ValueType>(
                "B", InParams.OperatorSettings);
            FEnumTriggerComparisonTypeReadRef CompareType = 
                InputData.GetOrCreateDefaultDataReadReference<FEnumTriggerComparisonType>(
                    "Type", InParams.OperatorSettings);

            return MakeUnique<TTriggerCompareNodeOperator<ValueType>>(
                InParams.OperatorSettings, CompareTrigger, A, B, CompareType);
        }

        // 每帧执行
        void Execute()
        {
            // 当 Compare 触发时执行比较
            if (CompareTrigger->IsTriggered())
            {
                bool bResult = PerformComparison(*A, *B, *CompareType);
                if (bResult)
                {
                    TrueTrigger->TriggerFrame(InSettings.BlockSize);
                }
                else
                {
                    FalseTrigger->TriggerFrame(InSettings.BlockSize);
                }
            }
        }
    };
}
```

### 进阶用法：Value 节点（触发式值设置）

```cpp
// 来源: MetasoundStandardNodes/Public/MetasoundValueNode.h
// Value 节点 - 允许通过触发器设置和重置输出值

// 使用方式（在 MetaSound 图中）：
// 1. 连接 "Set" 触发器 → 输出值变为 "Target Value"
// 2. 连接 "Reset" 触发器 → 输出值恢复为 "Init Value"
// 3. "Output Value" 始终反映当前值

// 模板实例化支持所有 MetaSound 数据类型：
// TValueOperator<float>, TValueOperator<int32>, TValueOperator<bool>, etc.
```

### 进阶用法：随机节点

```cpp
// 来源: MetasoundStandardNodes/Public/MetasoundRandomNode.h
// Random 节点 - 可种子化的随机数生成

// 在 MetaSound 图中的使用：
// - "Next" 触发 → 生成下一个随机值
// - "Reset" 触发 → 用 Seed 重置随机序列（可复现的随机）
// - Seed = -1 → 使用随机种子
// - Min/Max → 值范围
```

---

## Demo 示例

以下展示如何在 C++ 中创建一个使用标准节点的简单 MetaSound 图：

```cpp
// MyMetaSoundTest.h
#pragma once

#include "CoreMinimal.h"
#include "MetasoundFrontendDocument.h"

class FMyMetaSoundBuilder
{
public:
    /** 创建一个简单的正弦波 MetaSound */
    static TSharedRef<FMetasoundFrontendDocument> CreateSimpleSineMetaSound();
};
```

```cpp
// MyMetaSoundTest.cpp
#include "MyMetaSoundTest.h"
#include "MetasoundFrontendDocument.h"
#include "MetasoundFrontendGraph.h"
#include "MetasoundOscillatorNodes.h"
#include "MetasoundStandardNodesNames.h"

TSharedRef<FMetasoundFrontendDocument> FMyMetaSoundBuilder::CreateSimpleSineMetaSound()
{
    // 注意：实际使用中，MetaSound 通常在编辑器中通过可视化图编辑器创建。
    // C++ 构建主要用于程序化生成 MetaSound 或创建自定义节点。
    //
    // 标准节点（振荡器、滤波器等）在 MetaSound 图编辑器中直接拖拽使用，
    // 无需在 C++ 中手动实例化。
    //
    // 自定义节点的创建模式：
    // 1. 继承 FNodeFacade 或 FBasicNode
    // 2. 实现 CreateNodeClassMetadata() 提供节点信息
    // 3. 实现 IOperatorFactory 创建操作符
    // 4. 在操作符中实现 Execute() 处理音频数据
    
    return MakeShared<FMetasoundFrontendDocument>();
}
```

> **提示**：MetaSound 的主要使用方式是通过**编辑器中的可视化图编辑器**。C++ 层面主要用于创建自定义节点类型。标准节点（振荡器、触发器、滤波器等）在图编辑器中直接使用，无需编写 C++ 代码。

---

## 模块依赖

MetasoundStandardNodes 的独特依赖（从头文件 include 推断）：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | 节点注册、数据类型系统、前端接口 |
| `MetasoundGraphCore` | 图核心：节点基类、操作符接口、顶点系统 |
| `MetasoundGenerator` | 音频生成器基础设施 |
| `AudioMixer` | DSP 工具函数（增益转换等） |
| `SignalProcessing` | 信号处理算法（振荡器、滤波器实现） |

> 使用 MetaSound 插件的项目模块通常只需依赖 `MetasoundEngine`，它会传递依赖其他必要模块。

---

## 维护状态

### 近期更新

```
- c2ae0e8ce918 Fix for delay node pitch shifting issue（修复延迟节点的音高偏移问题）
- 37db075b207d Removing unnecessary fade-in on our oscillator nodes（移除振荡器节点中不必要的淡入）
- 0d06fcfab8b8 Fix for math operations for Reset.（修复数学运算节点的 Reset 功能）
```

### 维护评价

- **活跃维护**：MetaSound 是 UE5 的核心音频系统，由 Epic Games 持续维护
- **持续更新**：近期提交集中在 bug 修复和节点行为优化，表明系统已趋于稳定
- **成熟度高**：自 2020 年创建以来已发展约 5 年，是 UE5 替代 Sound Cue 的官方推荐方案
- **推荐使用**：对于需要程序化音频、复杂 DSP 处理或精细参数控制的项目，MetaSound 是首选方案
- **学习曲线**：相比 Sound Cue，MetaSound 的概念更接近专业音频编程（DSP 图），需要一定的音频工程知识

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasounds-in-unreal-engine)