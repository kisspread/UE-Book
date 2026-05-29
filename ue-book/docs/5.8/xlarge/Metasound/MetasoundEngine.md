# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 元音效 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产，测试资源） |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个**程序化音频系统**，旨在取代传统的、仅播放预制音频资产的系统。它允许声音设计师和程序员通过**可视化的节点图**来构建声音生成与处理的逻辑（DSP 图），从而实现高度动态、参数化、模块化和可精确控制的声音。

核心价值在于：
*   **参数化声音**：游戏中的实时参数（如角色速度、距离、生命值）可以直接连接到音效的音高、音量、滤波器截止频率等参数，创造高度响应式的声音体验。
*   **模块化组合**：将简单的音频操作（如振荡器、滤波器、包络、采样器）像乐高积木一样连接，构建出复杂的声音源或效果器。
*   **精确时间控制**：支持采样级精度的事件和参数调制，确保声音同步。
*   **蓝图/代码驱动**：既可在 MetaSound 编辑器中设计，也完全支持通过蓝图和 C++ 在运行时创建、修改和播放 MetaSound，实现完全动态的音频生成。
*   **性能优化**：其图编译和执行模型旨在为实时音频渲染提供高性能。

## 使用场景

*   你需要根据玩家操作实时改变枪声的力度、音高和混响？ → 使用 MetaSound 节点图将游戏参数映射到声音属性。
*   你想要创建一个复杂的环境声景，由多个随机播放的音效层混合而成，并动态混合？ → 在 MetaSound 中组合多个音频播放器、随机节点和混合器节点。
*   你需要为音乐互动游戏生成基于玩家输入的程序化音乐？ → 使用 MetaSound 构建音乐逻辑和合成器。
*   你希望在运行时通过代码或蓝图完全动态地生成声音（例如，根据物理材质生成碰撞声）？ → 使用 MetaSound Builder API 在 C++ 或蓝图中程序化构建 MetaSound。

## 蓝图用法

MetaSound 为蓝图提供了从资产管理到运行时控制的全面 API。

### 核心节点

#### 构建与管理 (MetaSound Builder Subsystem)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Patch Builder` | 创建一个用于构建 MetaSound Patch（纯数据节点图，无音频输出）的构建器。 | `UMetaSoundBuilderSubsystem` |
| `Create Source Builder` | 创建一个用于构建 MetaSound Source（可播放的音频源）的构建器，同时返回 `OnPlay`、`OnFinished` 和音频输出等关键句柄。 | `UMetaSoundBuilderSubsystem` |
| `Create Patch/Source Preset Builder` | 创建基于现有 MetaSound 的预设构建器，允许覆盖特定参数。 | `UMetaSoundBuilderSubsystem` |
| `Create MetaSound Literal From...` | 创建用于设置节点输入默认值的字面量（Literal），支持 Bool、Float、Int、String、Object 等类型。 | `UMetaSoundBuilderSubsystem` |
| `Find Builder` | 通过名称或 MetaSound 对象查找已注册的构建器。 | `UMetaSoundBuilderSubsystem` |
| `Register Builder` | 将构建器注册到子系统，使其可被跨系统或蓝图持久访问。 | `UMetaSoundBuilderSubsystem` |

#### 图构建 (MetaSound Builder)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add MetaSound Node By ClassName` | 根据原生类名（如 “Sine”）向图中添加一个标准节点。 | `UMetaSoundBuilderBase` |
| `Add MetaSound Node From Asset Class` | 根据一个 MetaSound 资产（如另一个 Patch）向图中添加一个节点。 | `UMetaSoundBuilderBase` |
| `Add Graph Input Node` | 添加一个图输入节点，用于接收外部参数。 | `UMetaSoundBuilderBase` |
| `Add Graph Output Node` | 添加一个图输出节点（Patch 无音频输出，Source 有音频输出）。 | `UMetaSoundBuilderBase` |
| `Connect Nodes` | 连接一个节点的输出到另一个节点的输入。 | `UMetaSoundBuilderBase` |
| `Connect Node Output To Graph Output` | 将节点的输出连接到图的最终输出。 | `UMetaSoundBuilderBase` |
| `Connect Node Input To Graph Input` | 将图的输入连接到节点的输入。 | `UMetaSoundBuilderBase` |
| `Remove Node` | 从图中移除一个节点。 | `UMetaSoundBuilderBase` |
| `Find Node Input/Output` | 查找节点上的输入/输出句柄。 | `UMetaSoundBuilderBase` |
| `Set Node Input Default` | 设置节点输入的默认值（当无连接时使用）。 | `UMetaSoundBuilderBase` |

#### 运行时控制 (MetaSound Generator Handle)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MetaSound Generator Handle` | 为一个正在播放 MetaSound 的 `UAudioComponent` 创建句柄，用于运行时控制。 | `UMetasoundGeneratorHandle` |
| `Apply Parameter Pack` | 向播放中的 MetaSound 异步发送一个参数包。 | `UMetasoundGeneratorHandle` |
| `Watch Output` | 监听 MetaSound 输出的特定值（如用于 UI 显示），当值变化时触发事件。 | `UMetasoundGeneratorHandle` / `UMetaSoundOutputSubsystem` |
| `Get CPU Core Utilization` | 获取该 MetaSound 实例的 CPU 使用率（需先启用渲染计时）。 | `UMetasoundGeneratorHandle` |

### 使用示例（蓝图描述）

1.  **动态构建一个简单的音效并播放**：
    *   获取 `MetaSoundBuilderSubsystem`，调用 `Create Source Builder`，选择输出格式（如 `Mono`）和一次性音效 `bIsOneShot = true`。
    *   在返回的 `UMetaSoundSourceBuilder` 上，调用 `Add MetaSound Node By ClassName` 添加一个 “Sine”（正弦波）节点。
    *   调用 `Find Node Output` 找到 Sine 节点的 “Audio” 输出。
    *   调用 `Connect Node Output To Graph Output` 将此输出连接到图的音频输出。
    *   最后调用 `Build MetaSound` 构建资产，并使用 `Play Sound at Location` 播放。

2.  **运行时改变播放中声音的音高**：
    *   有一个已播放的 MetaSound 的 `AudioComponent`。
    *   调用 `Create MetaSound Generator Handle` 为其创建句柄。
    *   调用 `Create Float MetaSound Literal` 创建一个包含新音高值（如 1.5）的字面量。
    *   调用 `Create Audio Parameter`，将字面量赋值给一个名为 “Pitch” 的参数。
    *   调用 `Apply Parameter Pack` 将参数包发送给生成器。

## C++ 用法

### 头文件引入

使用 `MetaSoundEngine` 模块的功能：
```cpp
#include "MetaSoundBuilderSubsystem.h"
#include "MetaSoundSource.h"
#include "MetaSoundPatch.h"
#include "MetasoundGeneratorHandle.h"
#include "MetasoundFrontendDocumentBuilder.h"
```

### 基本用法：程序化构建一个 MetaSound 并播放

以下示例创建一个播放正弦波的简单 MetaSound Source 并在世界中播放。
（基于 `MetasoundEngineTest` 模块中的测试逻辑推导）

```cpp
// MyMetaSoundExample.h
#pragma once
#include "CoreMinimal.h"
#include "Components/AudioComponent.h"

class FMyMetaSoundExample
{
public:
    static UMetaSoundSource* BuildSimpleSineWaveMetaSound(UObject* InOuter, FName InName = TEXT("SimpleSine"));
    static UAudioComponent* PlayMetaSoundAtLocation(UObject* WorldContextObject, UMetaSoundSource* InSource, const FVector& Location);
};

// MyMetaSoundExample.cpp
#include "MyMetaSoundExample.h"
#include "MetaSoundBuilderSubsystem.h"
#include "MetaSoundSource.h"
#include "Kismet/GameplayStatics.h"

UMetaSoundSource* FMyMetaSoundExample::BuildSimpleSineWaveMetaSound(UObject* InOuter, FName InName)
{
    // 1. 获取构建器子系统
    UMetaSoundBuilderSubsystem* BuilderSubsystem = GEngine->GetEngineSubsystem<UMetaSoundBuilderSubsystem>();
    if (!BuilderSubsystem) return nullptr;

    // 2. 创建一个 Source 构建器
    EMetaSoundBuilderResult BuildResult;
    FMetaSoundBuilderNodeOutputHandle OnPlayOutput, OnFinishedOutput;
    TArray<FMetaSoundBuilderNodeInputHandle> AudioOutputs;
    UMetaSoundSourceBuilder* SourceBuilder = BuilderSubsystem->CreateSourceBuilder(
        InName,
        OnPlayOutput,
        OnFinishedOutput,
        AudioOutputs,
        BuildResult,
        EMetaSoundOutputAudioFormat::Mono // 单声道
    );
    if (BuildResult != EMetaSoundBuilderResult::Succeeded || !SourceBuilder) return nullptr;

    // 3. 向图中添加一个 “Sine” 节点（原生节点）
    FMetasoundFrontendClassName SineClassName;
    SineClassName.SetWithImplicitNamespace(TEXT("Sine"));
    FMetaSoundNodeHandle SineNode = SourceBuilder->AddNodeByClassName(SineClassName, BuildResult);

    // 4. 找到 Sine 节点的 “Audio” 输出和 “Frequency” 输入
    FMetaSoundBuilderNodeOutputHandle SineAudioOutput = SourceBuilder->FindNodeOutputByName(SineNode, TEXT("Audio"), BuildResult);
    FMetaSoundBuilderNodeInputHandle SineFrequencyInput = SourceBuilder->FindNodeInputByName(SineNode, TEXT("Frequency"), BuildResult);

    // 5. 设置 “Frequency” 输入的默认值为 440Hz (A4)
    FMetasoundFrontendLiteral FrequencyLiteral;
    FrequencyLiteral.Set(440.0f);
    SourceBuilder->SetNodeInputDefault(SineFrequencyInput, FrequencyLiteral, BuildResult);

    // 6. 将 Sine 节点的输出连接到图的音频输出（此处假设图只有一个音频输出）
    if (AudioOutputs.Num() > 0)
    {
        SourceBuilder->ConnectNodeOutputToGraphOutput(AudioOutputs[0].Name, SineAudioOutput, BuildResult);
    }

    // 7. 构建 MetaSound 对象
    FMetaSoundBuilderOptions BuildOptions;
    BuildOptions.Name = InName;
    BuildOptions.bAddToRegistry = true; // 添加到注册表以便使用
    UMetaSoundSource* NewSource = &SourceBuilder->Build<UMetaSoundSource>(InOuter, BuildOptions);

    return NewSource;
}

UAudioComponent* FMyMetaSoundExample::PlayMetaSoundAtLocation(UObject* WorldContextObject, UMetaSoundSource* InSource, const FVector& Location)
{
    if (!InSource) return nullptr;
    return UGameplayStatics::SpawnSoundAtLocation(
        WorldContextObject,
        InSource,
        Location
    );
}
```

### 进阶用法：运行时发送参数

```cpp
// 继续上面的例子，假设已有一个正在播放的 AudioComponent
void UpdateMetaSoundPitch(UAudioComponent* AudioComp, float NewPitch)
{
    // 1. 为 AudioComponent 创建 Generator Handle
    UMetasoundGeneratorHandle* GeneratorHandle = UMetasoundGeneratorHandle::CreateMetaSoundGeneratorHandle(AudioComp);
    if (!GeneratorHandle) return;

    // 2. 创建参数包
    UMetasoundParameterPack* ParamPack = NewObject<UMetasoundParameterPack>();
    ParamPack->SetFloat(TEXT("Frequency"), NewPitch); // 假设 MetaSound 中有名为 “Frequency” 的图输入

    // 3. 应用参数包
    GeneratorHandle->ApplyParameterPack(ParamPack);
}
```

## Demo 示例

（因篇幅限制，以下为最小可运行示例框架，需在 UE5 项目中创建对应文件）

**MetaSoundExample.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MetaSoundExample.generated.h"

class UMetaSoundSource;
class UAudioComponent;

UCLASS()
class AMetaSoundExampleActor : public AActor
{
    GENERATED_BODY()
public:
    AMetaSoundExampleActor();
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void PlayDynamicMetaSound();

protected:
    UPROPERTY()
    TObjectPtr<UMetaSoundSource> DynamicMetaSoundAsset;

    UPROPERTY()
    TObjectPtr<UAudioComponent> PlayingComponent;
};
```

**MetaSoundExample.cpp**
```cpp
#include "MetaSoundExample.h"
#include "MetaSoundBuilderSubsystem.h"
#include "MetaSoundSource.h"
#include "Components/AudioComponent.h"
#include "Kismet/GameplayStatics.h"

AMetaSoundExampleActor::AMetaSoundExampleActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMetaSoundExampleActor::BeginPlay()
{
    Super::BeginPlay();
    // 在 BeginPlay 中动态构建 MetaSound 资产
    DynamicMetaSoundAsset = FMyMetaSoundExample::BuildSimpleSineWaveMetaSound(GetTransientPackage(), TEXT("MyDynamicSine"));
}

void AMetaSoundExampleActor::PlayDynamicMetaSound()
{
    if (DynamicMetaSoundAsset && !PlayingComponent)
    {
        PlayingComponent = FMyMetaSoundExample::PlayMetaSoundAtLocation(this, DynamicMetaSoundAsset, GetActorLocation());
    }
}
```

## 模块依赖

`MetasoundEngine` 模块依赖于多个音频相关模块，以下是该插件**独特**的依赖项：

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | MetaSound 的前端文档、节点定义和接口系统 |
| `MetasoundGraphCore` | MetaSound 图的核心数据结构和执行逻辑 |
| `MetasoundGenerator` | MetaSound 的实际音频生成器实现 |
| `MetasoundStandardNodes` | 内置标准节点库（如数学运算、振荡器、滤波器） |
| `WaveTable` | 波表合成和音频资产支持 |
| `AudioMixer` | 底层音频混合器，MetaSound Source 输出到此 |

其他如 `Core`, `Engine`, `Slate` 等常见依赖已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复了删除并重新添加 MetaSound 页面图时触发断言的问题 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 增加了防护措施，防止基于不可引用的父项创建 MetaSound 预设 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 在发布版本中保护目标 PageID 不被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 对先前进入 PIE 时死锁修复的代码进行清理 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 尝试性修复进入 PIE 时出现的冻结问题 |

### 维护评价

**活跃维护中**。

MetaSound 是 Unreal Engine 5 中**持续投入开发的核心音频系统**。尽管首次提交于 2020 年，但近期（2026 年 5 月）仍有**频繁的实质性更新**，主要集中在稳定性修复、编辑器体验改进和对新功能（如 Pages、CAT 格式）的完善上。从最近的提交历史看，Epic 团队正在积极解决开发者遇到的具体问题，并持续打磨此系统。

*   **优势**：API 暴露全面，蓝图和 C++ 双轨支持，性能导向，功能强大。
*   **注意点**：系统较为复杂，学习曲线较陡峭。部分 API（如 Pages）仍标记为实验性（Experimental）。
*   **推荐**：**强烈推荐**用于任何对音频有定制化、动态化或高性能要求的 UE5 项目。它是 UE5 音频功能的未来方向。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/overview-of-metasounds-in-unreal-engine/)（注意：文档可能滞后于代码）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)