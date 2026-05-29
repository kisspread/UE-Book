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
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是 UE5 的下一代程序化音频系统，允许声音设计师通过**节点图**来完全控制音频 DSP（数字信号处理）管线。与传统基于资产的音频播放不同，MetaSound 以**图结构**定义音频生成逻辑：每个节点代表一个 DSP 操作（振荡器、滤波器、混音、包络等），节点之间通过输入/输出顶点（Vertex）传递采样级精度的音频数据和控制参数。

**解决的核心问题：**

- **程序化音频生成**：不再只能播放预制音频文件，可以实时合成、处理和混合声音
- **采样级精度控制**：音频参数的调制和事件触发精确到每个采样，避免音频毛刺和延迟
- **蓝图集成**：游戏逻辑通过音频参数接口（Parameter Interface）和音频事件驱动声音，实现数据驱动的音频设计
- **模块化节点系统**：支持自定义节点扩展，声音设计师可以在编辑器中以可视化方式构建复杂的音频逻辑

**插件规模说明：** 本插件包含 **573 个源文件**，分为 7 个模块，涵盖前端文档系统、图核心引擎、运行时生成器、标准节点库、编辑器和测试框架。本文档为汇总页。

## 使用场景

- 你在做第一人称射击游戏 → 用 MetaSound 程序化生成枪声的每一次射击音效，避免素材重复感
- 你需要基于游戏状态实时混合环境音效 → 用 MetaSound 图将风速、雨量等参数实时映射到音频 DSP 参数
- 你想为赛车游戏实现动态引擎音效 → 用 MetaSound 接收 RPM 参数，驱动振荡器频率和滤波器截止频率
- 你正在开发音乐类游戏 → 用 MetaSound 构建合成器节点图，生成程序化音乐
- 你希望声音设计师在编辑器中可视化构建音频逻辑 → 用 MetaSound 编辑器拖拽节点创建音频图

## 蓝图用法

MetaSound 通过 `UMetaSoundBuilderSubsystem` 和 Builder 类提供蓝图接口，允许在运行时程序化构建和修改 MetaSound 图。以下从测试源码中提取的核心节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePatchBuilder` | 创建一个 MetaSound Patch 构建器，用于程序化构建 MetaSound Patch | `UMetaSoundBuilderSubsystem` |
| `AddInterface` | 向构建器添加参数接口（如游戏输入/输出定义） | `UMetaSoundPatchBuilder` |
| `BuildNewMetaSound` | 从构建器生成最终的 MetaSound Patch 或 Source 资产 | `UMetaSoundBuilderBase` |
| `DisconnectInput` | 断开节点的输入连接 | `UMetaSoundBuilderBase` |
| `SetLiteral` | 设置节点输入的默认字面量值 | `UMetaSoundBuilderBase` |
| `RemoveNodeDefaultLiteral` | 移除节点输入的默认字面量 | `UMetaSoundBuilderBase` |

### 使用示例（蓝图描述）

**创建 MetaSound Patch 并添加接口：**

1. 获取 `UMetaSoundBuilderSubsystem` 实例（通过 `Get Game Instance Subsystem` 节点）
2. 调用 `Create Patch Builder`，传入自定义 Builder 名称
3. 对 Builder 调用 `Add Interface`，传入所需的接口名称（如 `"UE.Test.Update"`）
4. 在 Builder 上添加节点、连接输入输出
5. 调用 `Build New MetaSound` 生成最终资产

**程序化断开和重连输入：**

1. 通过 Builder 节点句柄定位到目标节点输入
2. 调用 `Disconnect Input` 断开当前连接
3. 使用 `Set Literal` 设置新的默认值，或使用其他连接节点创建新连接

## C++ 用法

MetaSound 的 C++ 接口主要通过图构建器（Graph Builder）和节点注册系统暴露，测试代码提供了最贴近官方用法的示例。

### 头文件引入

```cpp
#include "MetasoundFrontendDocument.h"
#include "MetasoundBuilderSubsystem.h"
#include "MetasoundBuilderBase.h"
#include "MetasoundEnvironment.h"
#include "NodeTestGraphBuilder.h"  // 测试辅助
```

### 基本用法

**使用 FNodeTestGraphBuilder 构建最小音频图：**

（来源：`Source/MetasoundEngineTest/Public/NodeTestGraphBuilder.h`）

```cpp
#include "NodeTestGraphBuilder.h"

// 创建图构建器
Metasound::Test::FNodeTestGraphBuilder GraphBuilder;

// 添加一个节点（例如三角波生成器）
const FNodeClassName TriGeneratorClass("TriGenerator", "Audio"); // 类名 + 类属名
Frontend::FNodeHandle TriNode = GraphBuilder.AddNode(TriGeneratorClass, /*MajorVersion=*/1);

// 添加一个构造器输入节点（常量值），并连接到 TriNode 的 Frequency 输入
GraphBuilder.AddAndConnectConstructorInput<float>(TriNode, FName("Frequency"), 440.0f);

// 添加数据引用输出节点，连接音频输出
GraphBuilder.AddAndConnectDataReferenceOutput(
    TriNode,
    FName("AudioOut"),
    GetMetasoundDataTypeName<FAudioBuffer>()
);

// 从图构建生成器（音频渲染器）
TUniquePtr<FMetasoundGenerator> Generator = GraphBuilder.BuildGenerator(
    /*SampleRate=*/48000,
    /*SamplesPerBlock=*/256
);

// Generator 现在可用于渲染音频块
```

**使用静态方法快速创建单节点图：**

```cpp
// 一行代码创建并返回一个已接线的单节点生成器
TUniquePtr<FMetasoundGenerator> Generator = 
    Metasound::Test::FNodeTestGraphBuilder::MakeSingleNodeGraph(
        FNodeClassName("TriGenerator", "Audio"),
        1,  // MajorVersion
        48000,  // SampleRate
        256     // SamplesPerBlock
    );
```

**连接两个节点：**

```cpp
// 通过输出/输入名称连接
bool bSuccess = FNodeTestGraphBuilder::ConnectNodes(
    LeftNode,    FName("OutputPin"),
    RightNode,   FName("InputPin")
);

// 或者当输入输出同名时使用简写
bool bSuccess = FNodeTestGraphBuilder::ConnectNodes(
    LeftNode, RightNode, FName("AudioData")
);
```

### 进阶用法

**通过 Builder API 程序化创建 MetaSound Patch：**

（来源：`Source/MetasoundEngineTest/Private/EngineTestMetaSoundBuilder.h`）

```cpp
#include "MetasoundBuilderSubsystem.h"

// 获取构建器子系统
UMetaSoundBuilderSubsystem& Subsystem = UMetaSoundBuilderSubsystem::GetChecked();

// 创建 Patch 构建器
EMetaSoundBuilderResult Result = EMetaSoundBuilderResult::Failed;
UMetaSoundPatchBuilder* Builder = Subsystem.CreatePatchBuilder(FName("MyPatchBuilder"), Result);
check(Result == EMetaSoundBuilderResult::Succeeded);

// 添加参数接口（定义输入/输出通道）
Builder->AddInterface(FName("UE.Audio.Envelope"), Result);
check(Result == EMetaSoundBuilderResult::Succeeded);

// 构建 MetaSound Patch 资产
UMetaSoundPatch* Patch = Cast<UMetaSoundPatch>(
    Builder->BuildNewMetaSound(FName("MyMetaSoundPatch")).GetObject()
);
```

**使用参数接口系统：**

（来源：`Source/MetasoundEngineTest/Private/Interfaces/MetasoundTestInterfaces.h`）

```cpp
// 参数接口定义了 MetaSound 与外部系统的通信通道
// 接口有版本控制，支持输入和输出

// 获取接口版本
const FMetasoundFrontendVersion& Version = 
    Metasound::Test::UpdateTestInterface_0_1::GetVersion();

// 使用命名空间定义接口 I/O
// Inputs::InputTrigger  - 外部触发输入
// Outputs::OutputTrigger - 触发输出

// 创建接口实例（绑定到 UClass）
Audio::FParameterInterfacePtr Interface = 
    Metasound::Test::UpdateTestInterface_0_1::CreateInterface(MyClass);
```

**自动化测试节点：**

（来源：`Source/MetasoundEngineTest/Private/EngineTestMetaSoundAutomatedNodeTest.h`）

```cpp
#include "Metasound.h"
#include "MetasoundOperatorInterface.h"

// 获取所有已注册的 MetaSound 节点
TArray<FString> Names, Keys;
Metasound::EngineTest::GetAllRegisteredNativeNodes(Names, Keys, /*bIncludeDeprecated=*/false);

// 从注册表键创建节点实例
TUniquePtr<Metasound::INode> Node = 
    Metasound::EngineTest::CreateNodeFromRegistry(NodeRegistryKey);

// 获取渲染环境
Metasound::FMetasoundEnvironment Env = 
    Metasound::EngineTest::GetSourceEnvironmentForTest();

// 设置输入数据为随机值进行测试
Metasound::EngineTest::FInputVertexDataTestController InputController(
    OperatorSettings, InputInterface, InputData
);
InputController.SetMutableInputsToRandom();
InputController.SetMutableInputsToMin();
InputController.SetMutableInputsToMax();
InputController.SetMutableInputsToDefault();

// 捕获并验证输出
Metasound::EngineTest::FOutputVertexDataTestController OutputController(
    OutputInterface, OutputData
);
OutputController.CaptureCurrentOutputValues();
bool bUnchanged = OutputController.AreAllOutputValuesEqualToCapturedValues();
```

## Demo 示例

以下是一个完整的最小示例，展示如何在 C++ 中构建 MetaSound 图并生成音频：

```cpp
// MetaSoundMinimalExample.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MetasoundGenerator.h"
#include "MetasoundFrontendDocument.h"
#include "NodeTestGraphBuilder.h"
#include "MetaSoundMinimalExample.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class UMetaSoundMinimalExample : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void SetFrequency(float InFrequency);

private:
    TUniquePtr<Metasound::FMetasoundGenerator> Generator;
};
```

```cpp
// MetaSoundMinimalExample.cpp
#include "MetaSoundMinimalExample.h"
#include "MetasoundFrontend.h"
#include "MetasoundDataReference.h"
#include "NodeTestGraphBuilder.h"

void UMetaSoundMinimalExample::BeginPlay()
{
    Super::BeginPlay();

    // 使用测试图构建器创建一个最小音频图
    using namespace Metasound;
    using namespace Metasound::Test;

    FNodeTestGraphBuilder Builder;

    // 添加三角波节点
    const FNodeClassName TriClass(TEXT("TriGenerator"), TEXT("Audio"));
    Frontend::FNodeHandle TriNode = Builder.AddNode(TriClass, 1);

    if (TriNode->IsValid())
    {
        // 连接常量频率 440Hz
        Builder.AddAndConnectConstructorInput<float>(
            TriNode, FName(TEXT("Frequency")), 440.0f
        );

        // 连接常量音量 0.5
        Builder.AddAndConnectConstructorInput<float>(
            TriNode, FName(TEXT("Amplitude")), 0.5f
        );

        // 添加音频输出
        Builder.AddAndConnectDataReferenceOutput(
            TriNode,
            FName(TEXT("OutAudio")),
            GetMetasoundDataTypeName<FAudioBuffer>()
        );
    }

    // 生成音频渲染器
    Generator = Builder.BuildGenerator(48000, 256);
}

void UMetaSoundMinimalExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    Generator.Reset();
    Super::EndPlay(EndPlayReason);
}

void UMetaSoundMinimalExample::SetFrequency(float InFrequency)
{
    // 在运行时通过音频参数系统更新频率
    // 完整实现需要通过 FMetasoundEnvironment 或参数接口传递
    // 此处为概念演示
    if (Generator.IsValid())
    {
        // 通过生成器的音频参数接口设置新值
        // 具体 API 取决于 MetaSound 版本和参数接口绑定方式
    }
}
```

## 模块依赖

MetaSound 是一个大型插件，模块间存在分层依赖关系。对于外部使用者，核心依赖如下：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 前端文档系统，定义图结构、节点接口、参数接口 |
| `MetasoundGraphCore` | 图核心运行时，提供运算符（Operator）和执行框架 |
| `MetasoundEngine` | 引擎集成层，提供 UMetaSoundSource、UMetaSoundPatch 等资产类型 |
| `MetasoundGenerator` | 音频生成器，将图编译为可渲染的音频运算符链 |
| `MetasoundStandardNodes` | 标准节点库（振荡器、滤波器、混音等 DSP 节点） |
| `MetasoundEditor` | 编辑器集成，提供 MetaSound 图编辑器 UI |
| `AudioMixer` | 底层音频混音器，MetaSound 的音频数据流经此模块输出 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复删除后重新添加 Page 图时的断言失败 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 修复非可引用父对象创建预设时的防护检查 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 防止打包版本中目标 PageID 被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 清理之前 PIE 死锁修复的遗留代码 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 修复进入 PIE 时可能的冻结问题 |

### 维护评价

MetaSound 是 UE5 的**核心音频系统**，由 Epic Games 官方维护。

- **活跃程度**：极为活跃——最近的提交全部在 2026 年 5 月 14 日，一天内有多次提交，涵盖 bug 修复、死锁修复、新功能（Page 图系统、预设系统）等
- **功能演进**：从提交历史可以看到持续增加新功能（Page 图、预设、参数接口版本化），表明该系统仍在积极扩展
- **稳定性**：近期提交集中在 bug 修复和防护措施，说明系统已进入成熟稳定阶段，同时仍在处理边界情况
- **推荐度**：⭐⭐⭐⭐⭐ **强烈推荐**。MetaSound 是 UE5 官方推荐的程序化音频方案，已取代旧的 Sound Cue 系统成为音频设计的首选工具。如果你的项目涉及任何程序化或交互式音频，MetaSound 是必选项

> ⚠️ **注意**：MetaSound 是一个大型系统（573 个源文件），学习曲线较陡。建议从官方文档和示例 MetaSound 资产入手，逐步理解节点图 → 参数接口 → 蓝图集成的工作流。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/en-US/InteractiveAudio/MetaSounds/)（Unreal Engine MetaSounds 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)