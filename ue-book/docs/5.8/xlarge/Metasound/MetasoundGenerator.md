# MetaSound

> A high-performance audio system that enables sound designers to have complete control over audio DSP graph generation of sound sources, via sample-accurate control and modulation of sound using audio parameters and audio events from game data and Blueprints

| 属性 | 值 |
|---|---|
| 中文名 | 元音效 |
| 分类 | Audio |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `MetasoundEditor` (Runtime), `MetasoundEngine` (Runtime), `MetasoundEngineTest` (Runtime), `MetasoundFrontend` (Runtime), `MetasoundGenerator` (Runtime), `MetasoundGraphCore` (Runtime), `MetasoundStandardNodes` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-05-23 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound) | |

## 用途

MetaSound 是一个用于实时音频合成、处理与播放的完整系统。它解决的核心问题是：**为声音设计师提供一种直观的、基于节点图的可视化工具来设计复杂的音频处理流程，并能在游戏运行时以极高的性能精确执行这些流程。**

其存在意义在于：
1.  **设计师友好**：声音设计师可以在编辑器中通过类似蓝图的视觉化节点图（MetaSound Graph）来构建音频逻辑，无需编写C++代码。
2.  **实时性与精确性**：生成的音频处理图（DSP Graph）在音频线程上以采样精度运行，支持实时参数调制和事件触发，确保声音反馈的即时性和准确性。
3.  **高性能**：系统内置了算子缓存池（Operator Pool）、异步构建、并发实例计数等机制，优化了音频资产的加载、复用和渲染性能，适合在游戏中大量使用。
4.  **蓝图集成**：可以通过蓝图发送音频参数和事件，驱动MetaSound的行为，实现游戏逻辑与音效的深度联动。

## 使用场景

-   你需要创建一个复杂的声音效果，例如：
    -   根据角色速度实时变调的引擎声浪。
    -   受环境遮挡和材质影响的环境音。
    -   响应游戏中多个事件（如射击、换弹、命中）的武器音效，并且各层音效能平滑过渡和混合。
-   你希望声音设计师能独立创建和迭代音效资产，而不必等待程序员编写代码。
-   你的游戏需要大量的、可定制的声音，且对运行时性能（CPU、内存）有严格要求。
-   你需要通过蓝图或C++代码，在游戏运行时精确控制声音的各个参数（如音高、音量、滤波器截止频率）。

## 蓝图用法

MetaSound 的蓝图交互主要通过其暴露的委托和函数进行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Add Graph Set Callback` | 当MetaSound生成器的新图构建完成并设置后，绑定一个委托进行回调。 | `FMetasoundGenerator` |
| `Remove Graph Set Callback` | 移除通过 `Add Graph Set Callback` 绑定的委托。 | `FMetasoundGenerator` |
| `On Next Buffer` | 将一个函数加入队列，在生成器下一次请求音频缓冲区时（在音频线程上）执行，确保线程安全地访问生成器状态。 | `FMetasoundGenerator` |
| `On Output Changed` | 多播委托，当MetaSound图的某个输出端口值发生变化时广播。 | `FMetasoundGenerator` |
| `On Vertex Interface Data Updated` | 多播委托，当MetaSound的顶点接口数据（输入/输出）更新时广播。 | `FMetasoundGenerator` |

### 使用示例（蓝图描述）

1.  **监听MetaSound播放完成**：在MetaSound的“On Finished”输出引脚上连接一个自定义事件，或在蓝图中绑定 `FMetasoundGenerator::OnFinishedTriggerRef` 相关的委托。
2.  **实时修改参数**：在MetaSound播放过程中，通过 `SetInputValue` 或发送参数包的方式，动态改变如“Pitch”、“Volume”等输入参数的值，实现动态音效。
3.  **响应输出变化**：绑定 `OnOutputChanged` 委托，当MetaSound图内部计算出新的状态（如一个“IsInCombat”布尔输出）时，蓝图可以接收到通知并执行相应逻辑。

## C++ 用法

### 头文件引入

```cpp
#include "MetasoundGenerator.h"
#include "MetasoundOperatorCache.h"
#include "MetasoundGeneratorModule.h"
```

### 基本用法

以下示例展示了如何异步构建并播放一个MetaSound资产。

```cpp
// 来自 MetasoundGenerator.h 和 MetasoundOperatorCache.h
// 1. 获取 OperatorPool（通常通过模块接口）
Metasound::IMetasoundGeneratorModule& GeneratorModule = FModuleManager::GetModuleChecked<Metasound::IMetasoundGeneratorModule>(TEXT("MetasoundGenerator"));
TSharedPtr<Metasound::FOperatorPool> OperatorPool = GeneratorModule.GetOperatorPool();

// 2. 准备初始化参数
Metasound::FGeneratorInitParams InitParams;
InitParams.Graph = /* 你的 MetaSound 图数据 */;
InitParams.OperatorSettings.SampleRate = 44100;
InitParams.OperatorSettings.NumFramesPerBuffer = 512;
InitParams.AudioOutputNames.Add(FName("Out0")); // 指定音频输出端口名
// ... 设置其他必要参数，如AssetPath

// 3. 创建生成器实例（这里以 FMetasoundConstGraphGenerator 为例）
TSharedPtr<Metasound::FMetasoundConstGraphGenerator> Generator = MakeShared<Metasound::FMetasoundConstGraphGenerator>(InitParams.OperatorSettings);
Generator->Init(MoveTemp(InitParams)); // 内部将触发异步构建

// 4. 将生成器交给音频系统播放（通常需要集成到声源或声音基础架构中）
// 例如，设置为某个USoundBase或ASourceActor的输出。
```

### 进阶用法

利用算子缓存池预热资源，减少首次播放延迟。

```cpp
// 来自 MetasoundOperatorCache.h
// 在游戏加载或关卡开始时，预缓存特定MetaSound资产的多个实例
Metasound::FOperatorPoolEntryID OperatorID(/* ... */); // 通常由资产ID生成
Metasound::FOperatorBuildData BuildData(MoveTemp(InitParams), OperatorID.RegistryKey, OperatorID.OperatorID, /*NumInstances=*/3);
OperatorPool->BuildAndAddOperator(MakeUnique<Metasound::FOperatorBuildData>(MoveTemp(BuildData)));

// 之后当需要播放时，可以直接从池中索取已构建好的算子，极大降低播放延迟
Metasound::FOperatorAndInputs ClaimedOp = OperatorPool->ClaimOperator(OperatorID, OperatorContext);
```

## Demo 示例

一个最小的、用于演示创建并启动一个MetaSound生成器的C++类片段。

```cpp
// MyMetaSoundPlayer.h
#pragma once
#include "CoreMinimal.h"
#include "MetasoundGenerator.h"

class UMetaSound;

class FMyMetaSoundPlayer
{
public:
    void PlayMetaSound(UMetaSound* MetaSoundAsset);

private:
    TSharedPtr<Metasound::FMetasoundConstGraphGenerator> ActiveGenerator;
};
```

```cpp
// MyMetaSoundPlayer.cpp
#include "MyMetaSoundPlayer.h"
#include "MetasoundFrontend.h"
#include "MetasoundGeneratorModule.h"
#include "AssetRegistry/AssetData.h"

void FMyMetaSoundPlayer::PlayMetaSound(UMetaSound* MetaSoundAsset)
{
    if (!MetaSoundAsset) return;

    // 1. 从资产获取图数据（实际过程更复杂，涉及Frontend模块）
    // Metasound::Frontend::FGraphRegistryKey RegistryKey = ...;
    // TSharedPtr<Metasound::IGraph> Graph = ...;

    // 2. 准备参数
    Metasound::FGeneratorInitParams InitParams;
    InitParams.Graph = /* Graph */;
    InitParams.AssetPath = MetaSoundAsset->GetPathName();
    InitParams.OperatorSettings = Metasound::FOperatorSettings(48000.f, 480); // 48kHz, 480 samples/buffer
    InitParams.AudioOutputNames.Add(FName("MonoOut"));
    InitParams.bBuildSynchronous = true; // 为简化Demo，使用同步构建

    // 3. 创建并初始化生成器
    ActiveGenerator = MakeShared<Metasound::FMetasoundConstGraphGenerator>(InitParams.OperatorSettings);
    ActiveGenerator->Init(MoveTemp(InitParams));

    // 4. 在实际项目中，这里需要将 ActiveGenerator 注册到音频混合器或声源组件
    // 以便音频系统定期调用其 OnGenerateAudio 函数。
    // 例如: AudioDevice->StartSound(ActiveGenerator.ToSharedRef());
    UE_LOG(LogTemp, Log, TEXT("MetaSound generator initialized and ready."));
}
```

## 模块依赖

要使用 `MetasoundGenerator` 模块的功能，你的模块需要在 `Build.cs` 中添加对它的依赖。

| 模块 | 用途 |
|---|---|
| `MetasoundFrontend` | 用于访问MetaSound图的前端数据结构、编译器和注册表。 |
| `MetasoundGraphCore` | MetaSound图和算子的核心运行时实现。 |
| `MetasoundStandardNodes` | 包含MetaSound标准库中的所有内置节点（如振荡器、滤波器、数学运算等）。 |
| `AudioMixer` | 底层音频混合器，MetaSound生成器需要与之集成以输出音频。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `17643970` | Fix ensure when deleting and re-adding a MetaSound Page graph | 修复了删除后重新添加MetaSound页面图时的断言问题 |
| 2026-05-14 | `278def59` | Guard MetaSound preset creation against non-Referenceable parents | 保护了MetaSound预设创建过程，防止其引用无法引用的父项 |
| 2026-05-14 | `6121cd30` | Protect against mutation of target PageID in shipped builds | 在发布版本中保护了目标PageID不被意外修改 |
| 2026-05-14 | `79768793` | Clean-up pass on prior fix for deadlock fix when entering PIE | 对之前修复进入PIE模式时死锁的代码进行了清理 |
| 2026-05-14 | `de6200e1` | Speculative fix for freeze when entering PIE | 修复了进入PIE模式时可能出现的卡顿问题 |

### 维护评价

**评价：积极维护中。**
-   **活跃度高**：最近一次更新距今很近（假设当前为2026年），且从提交信息看，均为**Bug修复和稳定性改进**（死锁、断言错误），表明团队仍在积极解决已知问题，保障系统稳定。
-   **成熟度高**：自2020年创建以来已有6年，是UE5音频的核心子系统之一，功能完善，性能经过优化。
-   **推荐使用**：作为官方力推的音频解决方案，MetaSound功能强大、性能优越、文档和示例日益完善，是任何对音频有较高要求的项目的**首选方案**。无需担心其维护状态。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound)
-   [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/metasound-in-unreal-engine) (需从描述补充或假设)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Metasound/Source/MetasoundEngineTest)