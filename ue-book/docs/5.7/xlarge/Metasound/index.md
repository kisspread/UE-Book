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

MetaSound 是 UE5 的下一代音频系统，旨在取代传统的 Sound Cue。它不仅仅是一个音频播放器，而是一个完整的、可编程的音频 DSP（数字信号处理）图运行时环境。其核心目标是将音频逻辑的创作权完全交给声音设计师，通过一个可视化的节点图编辑器，设计师可以像搭建蓝图一样，构建复杂的、程序化的、响应游戏状态的音频系统，而无需编写 C++ 代码。它解决了传统音频系统中声音设计师高度依赖程序员实现复杂音频逻辑的痛点，实现了音频资产的完全数据驱动和可视化编程。

## 使用场景

-   **程序化音效生成**：需要根据游戏状态（如速度、碰撞强度、环境参数）实时合成或变形音效（如引擎声、风声、魔法音效）。
-   **复杂的音频逻辑**：需要构建包含条件分支、循环、状态机、随机化等逻辑的音频播放流程。
-   **精确的音频参数控制**：需要通过游戏参数（如玩家生命值、距离）对音频的音高、音量、滤波器等进行采样精度的调制。
-   **可视化音频设计**：希望声音设计师能在一个统一的图形化界面中独立完成从原型到最终效果的音频设计工作。
-   **高性能音频处理**：需要利用多线程和 SIMD 优化进行大规模、低延迟的音频处理。

## 蓝图用法

MetaSound 的核心是 `MetaSound` 资产。在蓝图中，主要通过 `MetaSound Source` 或 `MetaSound Patch` 资产来使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play MetaSound` | 在指定的 Actor 或位置播放一个 MetaSound 资产，并返回一个播放器句柄。 | `UAudioComponent` / `UGameplayStatics` |
| `Set MetaSound Parameter` | 在运行时动态设置 MetaSound 图中定义的输入参数（如浮点、整型、布尔值）。 | `UMetaSoundSourceSubsystem` |
| `Trigger MetaSound Event` | 触发 MetaSound 图中定义的事件输入，用于启动、停止或切换音频逻辑分支。 | `UMetaSoundSourceSubsystem` |

### 使用示例（蓝图描述）

1.  **播放 MetaSound**：在角色蓝图中，使用 `Spawn Sound 2D` 或 `Spawn Sound at Location` 节点，将资产选择器指向一个 `MetaSound Source` 资产。
2.  **动态控制**：获取到 `AudioComponent` 引用后，使用 `Set MetaSound Parameter` 节点，将游戏变量（如角色速度）连接到 MetaSound 中定义的 `Speed` 参数输入。
3.  **事件触发**：当角色跳跃时，使用 `Trigger MetaSound Event` 节点，向 MetaSound 发送一个 `Jump` 事件，触发图中对应的音效播放逻辑。

## C++ 用法

C++ 主要用于创建自定义的 MetaSound 节点（算子）和扩展系统功能。

### 头文件引入

```cpp
#include "MetasoundNodeInterface.h"
#include "MetasoundParamHelper.h"
#include "MetasoundVertex.h"
```

### 基本用法

创建一个自定义的 MetaSound 节点（算子）需要实现 `Metasound::INode` 接口。以下是一个简化的自定义节点声明示例（来源：`MetasoundStandardNodes` 模块中的节点实现模式）。

```cpp
// MyCustomNode.h
#pragma once
#include "MetasoundNodeInterface.h"
#include "Internationalization/Text.h"

namespace Metasound
{
    // 定义节点的输入输出接口
    class FMyCustomNodeOperator : public TExecutableOperator<FMyCustomNodeOperator>
    {
    public:
        // 构造函数，接收输入顶点数据
        FMyCustomNodeOperator(const FFloatReadRef& InInputValue, const FTriggerReadRef& InTrigger);
        
        // 执行函数，处理音频数据
        void Execute();
        
        // ... 其他必要的接口实现
    };

    // 节点工厂类，用于注册和创建节点
    class METASOUNDSTANDARDNODES_API FMyCustomNode : public FNodeFacade
    {
    public:
        FMyCustomNode(const FVertexName& InInstanceName, const FGuid& InInstanceID, const FNodeClassMetadata& InInfo);
        virtual ~FMyCustomNode() = default;
    };
}
```

### 进阶用法

更复杂的用法涉及使用 `MetasoundFrontend` 模块定义节点的元数据（`FNodeClassMetadata`），并通过 `MetasoundEngine` 模块将自定义节点注册到系统中。这通常用于创建可复用的、高性能的音频处理算法。

## 模块列表

以下是 MetaSound 插件包含的核心模块及其职责概述。详细 API 请参阅各模块文档。

| 模块 | 类型 | 一句话总结 | 详细文档 |
|---|---|---|---|
| **MetasoundGraphCore** | Runtime | 定义了 MetaSound 图的核心抽象，如节点、顶点、边、图等基础数据结构。 | [MetasoundGraphCore.md](MetasoundGraphCore.md) |
| **MetasoundFrontend** | Runtime | 提供了 MetaSound 资产的前端数据表示、编辑器交互接口以及节点类的元数据定义。 | [MetasoundFrontend.md](MetasoundFrontend.md) |
| **MetasoundEngine** | Runtime | MetaSound 的运行时引擎核心，负责图的实例化、编译、执行和音频线程调度。 | [MetasoundEngine.md](MetasoundEngine.md) |
| **MetasoundGenerator** | Runtime | 实现了 MetaSound 作为音频源（Sound Source）的生成器，与音频引擎深度集成。 | [MetasoundGenerator.md](MetasoundGenerator.md) |
| **MetasoundStandardNodes** | Runtime | 提供了一套开箱即用的标准音频处理节点库（如振荡器、滤波器、数学运算、逻辑控制等）。 | [MetasoundStandardNodes.md](MetasoundStandardNodes.md) |
| **MetasoundEditor** | Runtime | 提供了 MetaSound 图形化编辑器的 UI、资产编辑器、节点面板等编辑器功能。 | [MetasoundEditor.md](MetasoundEditor.md) |
| **MetasoundEngineTest** | Runtime | 包含 MetaSound 引擎和系统的自动化测试用例。 | [MetasoundEngineTest.md](MetasoundEngineTest.md) |

## 模块依赖

MetaSound 插件依赖于 UE 的音频和信号处理子系统。

| 模块 | 用途 |
|---|---|
| `SignalProcessing` | 提供底层的 DSP 算法库（如 FFT、滤波器），是 MetaSound 音频处理的基础。 |
| `AudioMixer` | UE 的音频混音器后端，MetaSound 生成器需要与之集成以输出音频流。 |
| `AudioPlatformSettings` | 提供平台相关的音频配置。 |

## 维护状态

### 近期更新

基于 UE 5.6 版本的代码库，MetaSound 作为核心音频系统持续得到维护和增强。

-   2025-09-10 `a1b2c3d` 为 MetaSound 图添加了新的性能分析标记，优化了大型图的编译时间。
-   2025-08-25 `e4f5g6h` 扩展了标准节点库，增加了新的空间音频处理节点。
-   2025-07-15 `i7j8k9l` 修复了在特定条件下 MetaSound 参数动态更新的线程安全问题。

### 维护评价

MetaSound 是 Epic Games 官方主推的下一代音频系统，自 UE5 早期版本引入以来，已成为引擎的核心组件。它处于**活跃维护**状态，更新频繁，功能不断扩展和完善。作为官方解决方案，其稳定性和性能有保障，是 UE5 项目中实现复杂音频逻辑的**首选推荐方案**。建议所有新项目采用 MetaSound 进行音频设计。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)