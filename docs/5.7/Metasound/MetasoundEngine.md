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

## 模块总览

MetaSound 是一个大型插件，由 7 个模块组成，共 648 个源文件。以下是各模块职责：

| 模块 | 类型 | 职责 |
|---|---|---|
| **MetasoundGraphCore** | Runtime | 底层图计算框架，定义节点、顶点、算子等核心抽象 |
| **MetasoundFrontend** | Runtime | 前端文档系统，管理 MetaSound 的序列化格式、类注册、数据类型注册 |
| **MetasoundGenerator** | Runtime | 音频生成器，负责将图编译为可执行的 DSP 算子并实时生成音频 |
| **MetasoundEngine** | Runtime | 引擎集成层，提供资产类型（Source/Patch）、子系统、蓝图 API、Builder 系统 |
| **MetasoundStandardNodes** | Runtime | 标准节点库，包含数学、滤波器、包络、采样器等常用 DSP 节点 |
| **MetasoundEditor** | Runtime | 编辑器 UI，提供图编辑器、节点面板、资产编辑器等 |
| **MetasoundEngineTest** | Runtime | 自动化测试 |

---

## 用途

MetaSound 是 UE5 的**下一代音频系统**，替代传统的 Sound Cue 蓝图。它解决的核心问题是：

1. **采样精度的 DSP 图控制**：传统音频系统只能在"事件"粒度上控制声音，MetaSound 允许在每个音频采样（48kHz）级别进行参数调制和信号处理
2. **可视化音频编程**：声音设计师通过节点图构建音频处理管线，无需编写 C++ 代码
3. **运行时动态图修改**：支持在运行时通过参数和事件动态改变音频图的行为
4. **高性能**：图在初始化时编译为优化的算子链，运行时开销极低

**为什么存在**：Sound Cue 的架构无法满足现代游戏对音频交互性和复杂度的需求。MetaSound 提供了类似 Max/MSP 或 Pure Data 的节点图范式，但深度集成到 UE 的资产系统、蓝图系统和音频管线中。

---

## 使用场景

- 你在制作一个射击游戏，需要枪声随距离、环境动态变化 → 用 MetaSound Source 构建参数化枪声音效
- 你需要实现复杂的环境音效（风声+雨声+雷声的动态混合） → 用 MetaSound 的节点图实现多层音频混合
- 你想在蓝图中实时控制音频参数（如引擎转速、角色速度） → 用 MetaSound 的音频参数系统
- 你需要创建可复用的音频处理模块（如自定义混响、失真效果） → 用 MetaSound Patch 封装为可嵌入的子图
- 你需要从 MetaSound 中读取输出值（如音频响度、频谱数据） → 用 MetaSoundOutputSubsystem 监听输出
- 你需要在运行时程序化构建音频图 → 用 MetaSound Builder API

---

## 蓝图用法

### 核心节点

#### 输出监听（MetaSoundOutputSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WatchOutput` | 监听正在播放的 MetaSound 的某个输出值变化 | `UMetaSoundOutputSubsystem` |
| `UnwatchOutput` | 停止监听输出值 | `UMetaSoundOutputSubsystem` |

#### 缓存管理（MetaSoundCacheSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `PrecacheMetaSound` | 预缓存指定数量的 MetaSound 算子实例，避免播放时的创建延迟 | `UMetaSoundCacheSubsystem` |
| `TouchOrPrecacheMetaSound` | 将已缓存的算子移到缓存顶部，不足部分新建 | `UMetaSoundCacheSubsystem` |
| `RemoveCachedOperatorsForMetaSound` | 清除指定 MetaSound 的缓存算子 | `UMetaSoundCacheSubsystem` |

#### Literal 创建（UMetasoundFrontendLiteralBlueprintAccess）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateFloatMetaSoundLiteral` | 从浮点值创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `CreateBoolMetaSoundLiteral` | 从布尔值创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `CreateIntMetaSoundLiteral` | 从整数值创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `CreateStringMetaSoundLiteral` | 从字符串创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `CreateObjectMetaSoundLiteral` | 从 UObject 创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `CreateMetaSoundLiteralFromParam` | 从音频参数创建 MetaSound Literal | `UMetasoundFrontendLiteralBlueprintAccess` |
| `GetType` | 获取 Literal 的类型 | `UMetasoundFrontendLiteralBlueprintAccess` |
| `EqualEqual_MetaSoundLiteral` | 比较两个 Literal 是否相等 | `UMetasoundFrontendLiteralBlueprintAccess` |

#### Builder API（MetaSoundBuilderSubsystem）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Audition` | 在编辑器中预览播放 MetaSound Source | `UMetaSoundSourceBuilder` |
| `SetFormat` | 设置输出音频格式（Mono/Stereo/5.1/7.1） | `UMetaSoundSourceBuilder` |
| `SetSampleRateOverride` | 设置采样率覆盖 | `UMetaSoundSourceBuilder` |
| `SetBlockRateOverride` | 设置块率覆盖 | `UMetaSoundSourceBuilder` |
| `GetLiveUpdatesEnabled` | 查询实时更新是否启用 | `UMetaSoundSourceBuilder` |

### 使用示例

**监听 MetaSound 输出值**：

1. 获取 `UMetaSoundOutputSubsystem`（通过 `GetWorldSubsystem` 节点）
2. 获取播放中的 `UAudioComponent` 引用
3. 调用 `WatchOutput`，传入 AudioComponent、输出名称（如 "Envelope"）、以及一个委托
4. 委托触发时，从 `FMetaSoundOutput` 中提取值

**预缓存 MetaSound**：

1. 获取 `UMetaSoundCacheSubsystem`（通过 `GetAudioEngineSubsystem` 节点）
2. 调用 `PrecacheMetaSound`，传入 `UMetaSoundSource` 资产和实例数量
3. 后续播放该 MetaSound 时将直接使用缓存的算子，消除首次播放延迟

---

## C++ 用法

### 头文件引入

```cpp
// 核心引擎集成
#include "MetasoundSource.h"
#include "Metasound.h"

// 生成器句柄（运行时交互）
#include "MetasoundGeneratorHandle.h"

// 输出监听
#include "MetasoundOutput.h"
#include "MetasoundOutputSubsystem.h"

// Builder API
#include "MetasoundBuilderSubsystem.h"
#include "MetasoundBuilderBase.h"

// 数据类型
#include "MetasoundWave.h"
#include "MetasoundAudioBus.h"
#include "MetasoundWaveTable.h"

// Literal 支持
#include "MetasoundFrontendLiteralBlueprintAccess.h"
```

### 基本用法：通过 GeneratorHandle 设置参数

```cpp
// 创建 GeneratorHandle 来与正在播放的 MetaSound 交互
// 来源: MetasoundGeneratorHandle.h

// 假设已有 UAudioComponent* AudioComponent 正在播放 MetaSound
TSharedPtr<Metasound::FMetasoundGeneratorHandle> Handle = 
    Metasound::FMetasoundGeneratorHandle::Create(AudioComponent);

if (Handle.IsValid())
{
    // 设置浮点参数
    Handle->SetFloatParam(TEXT("Pitch"), 1.5f);
    
    // 设置布尔参数
    Handle->SetBoolParam(TEXT("Muted"), false);
    
    // 设置整数参数
    Handle->SetIntParam(TEXT("Variant"), 2);
    
    // 监听输出值变化
    Handle->WatchOutput(TEXT("Envelope"), 
        FOnMetasoundOutputValueChangedNative::CreateLambda(
            [](FName OutputName, const FMetaSoundOutput& Output)
            {
                float Value;
                if (Output.Get<float>(Value))
                {
                    // 处理输出值
                }
            }));
}
```

### 基本用法：监听 MetaSound 输出

```cpp
// 来源: MetasoundOutputSubsystem.h

// 在 WorldSubsystem 中监听 MetaSound 输出
UMetaSoundOutputSubsystem* OutputSubsystem = 
    GetWorld()->GetSubsystem<UMetaSoundOutputSubsystem>();

if (OutputSubsystem)
{
    FOnMetasoundOutputValueChanged OnValueChanged;
    OnValueChanged.BindDynamic(this, &UMyClass::OnMetaSoundOutputChanged);
    
    OutputSubsystem->WatchOutput(
        MyAudioComponent,
        FName("Amplitude"),
        OnValueChanged);
}

// 回调函数
void UMyClass::OnMetaSoundOutputChanged(FName OutputName, const FMetaSoundOutput& Output)
{
    float Amplitude;
    if (Output.Get<float>(Amplitude))
    {
        // 使用音频振幅数据
    }
}
```

### 进阶用法：预缓存 MetaSound 算子

```cpp
// 来源: MetasoundOperatorCacheSubsystem.h

UMetaSoundCacheSubsystem* CacheSubsystem = 
    GEngine->GetEngineSubsystem<UMetaSoundCacheSubsystem>();

if (CacheSubsystem)
{
    // 预缓存 4 个实例，避免播放时的创建开销
    CacheSubsystem->PrecacheMetaSound(MyMetaSoundSource, 4);
    
    // 如果可能已缓存，使用 TouchOrPrecache 避免重复构建
    CacheSubsystem->TouchOrPrecacheMetaSound(MyMetaSoundSource, 4);
    
    // 不再需要时清除缓存
    CacheSubsystem->RemoveCachedOperatorsForMetaSound(MyMetaSoundSource);
}
```

### 进阶用法：程序化创建 MetaSound（Builder API）

```cpp
// 来源: MetasoundBuilderSubsystem.h, MetasoundBuilderBase.h

// 获取 Builder 子系统
UMetaSoundBuilderSubsystem* BuilderSubsystem = 
    GEngine->GetEngineSubsystem<UMetaSoundBuilderSubsystem>();

// 创建一个 MetaSound Source Builder
UMetaSoundSourceBuilder* SourceBuilder = 
    BuilderSubsystem->CreateSourceBuilder(
        FMetaSoundBuilderOptions{ .Name = TEXT("MyProceduralSound") });

if (SourceBuilder)
{
    // 设置输出格式为立体声
    EMetaSoundBuilderResult Result;
    SourceBuilder->SetFormat(EMetaSoundOutputAudioFormat::Stereo, Result);
    
    // 添加节点、连接、设置默认值等...
    // (使用 Builder 的 AddNode, ConnectNodes 等方法)
    
    // 构建最终资产
    TScriptInterface<IMetaSoundDocumentInterface> MetaSound = 
        SourceBuilder->BuildNewMetaSound(TEXT("MySound"));
}
```

### 进阶用法：使用 Audio Bus 进行跨 MetaSound 通信

```cpp
// 来源: MetasoundAudioBus.h, MetasoundAudioBusWriterNode.h

// MetaSound 提供了 Audio Bus Reader/Writer 节点
// 允许一个 MetaSound 向 Audio Bus 写入音频，
// 另一个 MetaSound 从 Audio Bus 读取

// Audio Bus Writer 节点类名（模板化，支持不同通道数）
// Audio Bus Writer (1) - 单声道
// Audio Bus Writer (2) - 立体声
// Audio Bus Writer (4) - 四声道
// Audio Bus Writer (6) - 5.1
// Audio Bus Writer (8) - 7.1

// 在 MetaSound 图中使用这些节点进行跨图音频路由
```

---

## Demo 示例

### 运行时监听 MetaSound 输出并响应

```cpp
// MyMetaSoundListener.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MetasoundGeneratorHandle.h"
#include "MetasoundOutput.h"
#include "Components/AudioComponent.h"
#include "MyMetaSoundListener.generated.h"

UCLASS(ClassGroup=(Audio), meta=(BlueprintSpawnableComponent))
class MYGAME_API UMyMetaSoundListener : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyMetaSoundListener();

    UPROPERTY(EditAnywhere, Category = "MetaSound")
    FName OutputName = FName("Envelope");

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void StartListening(UAudioComponent* InAudioComponent);

    UFUNCTION(BlueprintCallable, Category = "MetaSound")
    void StopListening();

    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnEnvelopeChanged, float, Value);
    
    UPROPERTY(BlueprintAssignable, Category = "MetaSound")
    FOnEnvelopeChanged OnEnvelopeChanged;

private:
    TSharedPtr<Metasound::FMetasoundGeneratorHandle> GeneratorHandle;
    FOnMetasoundOutputValueChangedNative OutputDelegate;

    void HandleOutputValueChanged(FName InOutputName, const FMetaSoundOutput& Output);
};
```

```cpp
// MyMetaSoundListener.cpp
#include "MyMetaSoundListener.h"
#include "MetasoundGeneratorHandle.h"

UMyMetaSoundListener::UMyMetaSoundListener()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UMyMetaSoundListener::StartListening(UAudioComponent* InAudioComponent)
{
    if (!InAudioComponent)
    {
        return;
    }

    GeneratorHandle = Metasound::FMetasoundGeneratorHandle::Create(InAudioComponent);
    
    if (GeneratorHandle.IsValid())
    {
        OutputDelegate.BindUObject(this, &UMyMetaSoundListener::HandleOutputValueChanged);
        GeneratorHandle->WatchOutput(OutputName, OutputDelegate);
    }
}

void UMyMetaSoundListener::StopListening()
{
    if (GeneratorHandle.IsValid())
    {
        OutputDelegate.Unbind();
        GeneratorHandle.Reset();
    }
}

void UMyMetaSoundListener::HandleOutputValueChanged(
    FName InOutputName, const FMetaSoundOutput& Output)
{
    float Value;
    if (Output.Get<float>(Value))
    {
        OnEnvelopeChanged.Broadcast(Value);
    }
}
```

---

## 模块依赖

由于 MetaSound 是一个大型插件，以下是各模块之间的依赖关系概要：

### 外部使用者需要的依赖

如果你要在自己的模块中使用 MetaSound API，需要在 Build.cs 中添加：

| 模块 | 用途 |
|---|---|
| `MetasoundEngine` | 核心引擎集成：资产类型、子系统、Builder API、GeneratorHandle |
| `MetasoundFrontend` | 前端文档操作、数据类型注册、类注册（仅在需要操作文档结构时） |
| `MetasoundStandardNodes` | 标准节点库（仅在需要注册/使用标准节点时） |

**注意**：`MetasoundGraphCore`、`MetasoundGenerator` 通常作为 `MetasoundEngine` 的传递依赖自动引入，无需显式依赖。`MetasoundEditor` 仅在编辑器模块中使用。

---

## 维护状态

### 近期更新

```
- 54dc6942670e Fix for buffer sample vs frame issue
- 289d96b1137e Fix for bus reader node getting stopped while metasound is playing and reading from the bus
- 9d9ae3bc5f4b Fix for runtime data not being invalidated when changing preset state; Minor clean up of delegate collection page code
```

### 维护评价

- **创建时间**：2020-05-22，约 5 年历史
- **活跃程度**：**活跃维护中**。MetaSound 是 Epic 重点投入的音频系统，持续有功能更新和 bug 修复
- **近期更新内容**：最近的提交集中在 bug 修复（缓冲区采样/帧问题、Bus Reader 停止问题、预设状态运行时数据失效），表明系统已趋于成熟稳定
- **代码规模**：648 个源文件，7 个模块，是 UE5 中最大的音频插件之一
- **已知限制**：
  - 学习曲线较陡，需要理解 DSP 概念和节点图编程范式
  - 编辑器 UI 在处理大型图时可能有性能问题
  - 部分 API 标记为 deprecated（如 ModifyContext、旧版接口注册方式），正在向 Builder API 迁移
- **推荐程度**：**强烈推荐**。MetaSound 是 UE5 官方推荐的音频系统，适合所有需要复杂音频交互的项目。对于简单音效，Sound Cue 仍然可用；但对于需要参数化、动态化、高性能的音频需求，MetaSound 是唯一选择。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasounds-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)