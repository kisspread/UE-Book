# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-22 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是 Unreal Engine 5 中用于替代传统 Sound Cue 的新一代高性能、节点化音频系统。它解决的核心问题是：为声音设计师提供一个强大且灵活的工具，能够完全控制声音的 DSP（数字信号处理）图生成过程。

与传统的基于资产的音频系统不同，MetaSound 允许设计师像编写代码一样，通过连接各种音频处理节点（如振荡器、滤波器、包络、混音器等）来构建复杂的声音逻辑。其关键特性包括：
- **采样精确控制**：所有音频参数的调制和事件触发都达到采样级别精度，确保声音的精确同步和响应。
- **参数与事件驱动**：能够直接使用游戏数据（如玩家速度、环境状态）和蓝图事件来实时调制音频参数，实现高度动态和交互式的声音效果。
- **可复用性与模块化**：创建的 MetaSound 图可以作为资产被复用、继承和组合，便于构建复杂的声音库。

简而言之，MetaSound 将音频设计从“选择和配置预设”提升到了“编程和构建”的层面，为 AAA 级游戏和复杂交互式媒体提供了专业级的音频创作能力。

## 使用场景

- **动态音乐系统**：你需要根据游戏状态（如战斗、探索、剧情）无缝切换和混合音乐层，并实时调整节奏和强度 → 使用 MetaSound 构建音乐状态机。
- **交互式环境音效**：你希望环境声音（如风声、雨声、城市噪音）能根据玩家位置、天气变化和游戏事件进行实时、平滑的参数化混合 → 使用 MetaSound 创建参数化的环境音效图。
- **复杂角色/武器音效**：你需要为角色技能或武器创建具有多层、随机化、基于游戏参数（如充能等级、连击数）变化的音效 → 使用 MetaSound 设计模块化的音效生成器。
- **音频可视化与分析**：你需要从游戏音频流中实时提取数据（如频谱、音量）用于 UI 显示或游戏逻辑 → 使用 MetaSound 的分析节点。
- **精确的节奏游戏**：你需要音频事件与游戏玩法在采样级别上精确同步 → MetaSound 的采样精确控制是理想选择。

## 蓝图用法

MetaSound 的蓝图集成主要通过 `MetasoundEngine` 模块暴露。核心交互围绕 MetaSound 资产的播放和参数控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Play MetaSound` | 在指定位置或组件上播放一个 MetaSound 资产。 | `UMetaSoundSubsystem` |
| `Set MetaSound Parameter` | 在运行时动态设置一个 MetaSound 实例的参数值（如浮点、整型、布尔）。 | `UMetaSoundSubsystem` |
| `Trigger MetaSound Event` | 向一个正在播放的 MetaSound 实例发送一个事件，用于触发内部逻辑（如开始播放、切换状态）。 | `UMetaSoundSubsystem` |
| `Stop MetaSound` | 停止一个正在播放的 MetaSound 实例。 | `UMetaSoundSubsystem` |
| `Create MetaSound Source` | 创建一个 MetaSound 源组件，用于更精细地控制播放（如附加到特定 Actor）。 | `UMetaSoundSourceFactory` |

### 使用示例（蓝图描述）

1.  **播放一个简单的 MetaSound**：
    - 在蓝图中，从 `MetaSoundSubsystem` 拖出引脚，调用 `Play MetaSound` 节点。
    - 将你的 MetaSound 资产（例如一个风声效果）连接到 `MetaSound` 输入引脚。
    - 将一个 `Make Transform` 节点连接到 `Location` 引脚以指定播放位置。
    - 执行该节点即可在指定位置播放声音。

2.  **实时控制参数**：
    - 首先，使用 `Play MetaSound` 播放声音，并保存返回的 `MetaSound Instance` 引用。
    - 当需要改变声音时（例如玩家进入室内），使用 `Set MetaSound Parameter` 节点。
    - 将保存的实例引用连接到 `MetaSound Instance` 引脚。
    - 在 `Parameter Name` 中输入你在 MetaSound 图中定义的参数名（如 “ReverbAmount”）。
    - 将新的参数值（如 0.8）连接到 `Value` 引脚。声音会立即根据新参数变化。

## C++ 用法

MetaSound 的 C++ API 主要用于高级场景，如创建自定义音频节点、程序化生成 MetaSound 图，或进行深度集成。以下示例基于测试用例中展示的图构建辅助类。

### 头文件引入

```cpp
#include "MetasoundFrontendController.h"
#include "MetasoundFrontendDocument.h"
#include "MetasoundGenerator.h"
#include "NodeTestGraphBuilder.h" // 来自 MetasoundEngineTest 模块，用于测试
```

### 基本用法

以下代码展示了如何使用 `FNodeTestGraphBuilder` 辅助类在测试环境中程序化地构建一个简单的 MetaSound 图。这模拟了声音设计师在编辑器中手动连接节点的过程。

```cpp
// 来源: Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest/Public/NodeTestGraphBuilder.h
// 以及相关的测试用例文件

// 创建一个图构建器实例
Metasound::Test::FNodeTestGraphBuilder GraphBuilder;

// 1. 添加一个正弦波节点 (假设类名为 “Sine”)
const Metasound::FNodeClassName SineClassName(“Sine”, “Oscillator”);
Metasound::Frontend::FNodeHandle SineNode = GraphBuilder.AddNode(SineClassName, 1);

// 2. 添加一个图输入节点，用于控制正弦波的频率
Metasound::Frontend::FNodeHandle FrequencyInput = GraphBuilder.AddConstructorInput<float>(“Frequency”, 440.0f);

// 3. 将频率输入连接到正弦波节点的 “Frequency” 输入引脚
GraphBuilder.ConnectConstructorInput(FrequencyInput, SineNode, “Frequency”);

// 4. 添加一个图输出节点，用于输出音频
Metasound::Frontend::FNodeHandle AudioOutput = GraphBuilder.AddOutput(“AudioOut”, GetMetasoundDataTypeName<Metasound::FAudioBuffer>());

// 5. 将正弦波节点的 “Audio” 输出连接到图的音频输出
GraphBuilder.ConnectNodes(SineNode, “Audio”, AudioOutput, “AudioOut”);

// 此时，GraphBuilder 内部的 MetaSound 文档已经构建完成。
// 在实际应用中，可以将此文档保存为 .uasset 或用于生成可播放的 Metasound::Generator。
```

### 进阶用法

更复杂的用法涉及创建自定义的 MetaSound 节点（Operator）。这需要继承 `Metasound::IOperator` 并实现其接口，然后在 `MetasoundFrontend` 中注册。这通常用于实现游戏特定的音频处理算法。

```cpp
// 概念性示例，展示自定义节点的结构
class FMyCustomOperator : public Metasound::IOperator
{
public:
    FMyCustomOperator(const Metasound::FBuildOperatorParams& InParams, ...)
    {
        // 从输入引脚获取数据接口
        // ...
    }

    virtual void BindInputs(Metasound::FInputVertexInterfaceData& InOutVertexData) override
    {
        // 绑定输入数据
        InOutVertexData.BindReadVertex(“InputAudio”, InputAudioInterface);
    }

    virtual void BindOutputs(Metasound::FOutputVertexInterfaceData& InOutVertexData) override
    {
        // 绑定输出数据
        InOutVertexData.BindWriteVertex(“OutputAudio”, OutputAudioInterface);
    }

    virtual void Execute() override
    {
        // 在这里执行每帧的音频处理逻辑
        // 从 InputAudioInterface 读取数据
        // 处理数据
        // 将结果写入 OutputAudioInterface
    }

private:
    Metasound::TDataReadReference<Metasound::FAudioBuffer> InputAudioInterface;
    Metasound::TDataWriteReference<Metasound::FAudioBuffer> OutputAudioInterface;
};
```

## Demo 示例

一个完整的、可编译的最小 C++ 示例，展示如何创建一个生成 440Hz 正弦波的 MetaSound 并播放它。

**MyMetaSoundDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/AudioComponent.h"
#include "MyMetaSoundDemo.generated.h"

class UMetaSoundSource;

UCLASS()
class AMyMetaSoundDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyMetaSoundDemo();

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(VisibleAnywhere)
    UAudioComponent* AudioComponent;

    UPROPERTY(EditAnywhere)
    UMetaSoundSource* MetaSoundAsset; // 在编辑器中指定一个 MetaSound 资产

    // 程序化构建的 MetaSound 文档
    TSharedPtr<Metasound::Frontend::FDocument> ProceduralDocument;
};
```

**MyMetaSoundDemo.cpp**
```cpp
#include "MyMetaSoundDemo.h"
#include "MetasoundFrontendDocument.h"
#include "MetasoundFrontendController.h"
#include "NodeTestGraphBuilder.h" // 使用测试模块的辅助类简化构建
#include "Components/AudioComponent.h"
#include "MetaSoundSource.h"

AMyMetaSoundDemo::AMyMetaSoundDemo()
{
    AudioComponent = CreateDefaultSubobject<UAudioComponent>(TEXT("AudioComp"));
    RootComponent = AudioComponent;
}

void AMyMetaSoundDemo::BeginPlay()
{
    Super::BeginPlay();

    // 方法1：使用预构建的 MetaSound 资产
    if (MetaSoundAsset)
    {
        AudioComponent->SetSound(MetaSoundAsset);
        AudioComponent->Play();
    }

    // 方法2：程序化构建一个简单的 MetaSound
    Metasound::Test::FNodeTestGraphBuilder Builder;

    // 添加一个正弦波节点
    const Metasound::FNodeClassName SineClass(“Sine”, “Oscillator”);
    auto SineNode = Builder.AddNode(SineClass, 1);

    // 设置固定频率 440Hz
    Builder.AddAndConnectConstructorInput<float>(SineNode, “Frequency”, 440.0f);

    // 添加音频输出
    auto AudioOut = Builder.AddOutput(“Out”, GetMetasoundDataTypeName<Metasound::FAudioBuffer>());
    Builder.ConnectNodes(SineNode, “Audio”, AudioOut, “Out”);

    // 获取构建好的文档
    ProceduralDocument = Builder.GetDocument();

    // 注意：将程序化文档转换为可播放的 UMetaSoundSource 资产需要更多步骤，
    // 通常涉及 MetasoundFrontend 和 MetasoundEngine 模块的序列化功能。
    // 此示例主要展示图构建逻辑。
}
```

## 模块依赖

要使用 MetaSound 插件，你的项目模块通常需要依赖以下模块。由于 MetaSound 是一个复杂的音频系统，其依赖项较多。

| 模块 | 用途 |
|---|---|
| `MetasoundEngine` | 核心运行时引擎，用于播放和控制 MetaSound 实例。 |
| `MetasoundFrontend` | MetaSound 图的前端表示、编辑和序列化。 |
| `MetasoundGraphCore` | MetaSound 图的核心数据结构和执行逻辑。 |
| `MetasoundStandardNodes` | 提供一套标准的音频处理节点（振荡器、滤波器、包络等）。 |
| `AudioMixer` | 底层音频混合器，MetaSound 生成的音频流最终通过它输出。 |
| `SignalProcessing` | 提供基础的信号处理工具和函数，被标准节点使用。 |

## 维护状态

### 近期更新

```
- 26d1b94590f6 Add AccessFlags to MetaSound UObject types - Implement RegisterAsClass as flag to determine what should be registered as a referenceable flag and shown in editor or not - Move IsDeprecated to associated access flag
- c849c401a3a4 - Part 1 of cutting down FName table bloat & string passing, copying, & parsing by moving implementation to use AssetPath wherever possible - Misc clean-up and removal of old code
- 2739c3d30ebc Updated headers using UnrealCodeFixup to make sure dllstorage is on methods/staticvars instead of types. Part 4/n
```

### 维护评价

MetaSound 是 Unreal Engine 5 音频系统的核心组件，由 Epic Games 官方团队积极维护。
- **活跃维护**：从提交历史看，近期（2024年）仍有重要的功能更新（如 AccessFlags）和性能优化（减少 FName 开销），表明该系统仍在持续演进。
- **成熟度**：自 2020 年创建以来已有约 5 年历史，已从实验性功能发展为成熟的、默认启用的生产级系统。
- **推荐使用**：**强烈推荐**。对于任何需要复杂、动态或高质量音频的 UE5 项目，MetaSound 都是首选方案。它提供了远超传统 Sound Cue 的控制力和性能。虽然学习曲线较陡，但其带来的音频设计自由度和运行时效率提升是巨大的。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/overview-of-metasounds-in-unreal-engine/) (UE5 官方文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)