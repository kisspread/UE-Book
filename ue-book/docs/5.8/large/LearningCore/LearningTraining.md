# Learning Core

> Learning Core is a machine learning library for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（C++库） |
| 模块 | `Learning` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningCore) | |

## 用途

Learning Core 是一个为 Unreal Engine 设计的机器学习库，其核心功能是为强化学习（Reinforcement Learning）训练提供基础设施。它主要解决在 UE 环境中高效收集经验数据（Observations, Actions, Rewards）并与外部 Python 训练进程进行通信的问题。该插件专注于实现 PPO（Proximal Policy Optimization）算法，并提供了通过共享内存或网络套接字两种方式与外部训练器交换数据和网络权重的机制，旨在简化在游戏引擎内训练 AI 代理的流程。

## 使用场景

- 你需要在 Unreal Engine 中训练一个 AI 代理（例如 NPC）学习复杂的导航、战斗或交互行为。
- 你希望使用 Python 生态系统中成熟的机器学习框架（如 PyTorch）来训练神经网络，但需要在 UE 中高效地收集训练数据。
- 你的训练环境需要支持多个 UE 实例并行收集经验数据，并汇总到一个中央训练器进行更新。
- 你需要一个标准化的、高性能的接口来管理训练过程，包括配置发送、经验数据传输、网络权重同步和训练生命周期控制。

## 蓝图用法

该插件主要提供 C++ API 用于底层训练流程控制，未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 节点。其设计更偏向于作为其他高级 AI 或机器学习插件的底层模块。

## C++ 用法

### 头文件引入

```cpp
#include "LearningTrainer.h"
#include "LearningExperience.h"
#include "LearningExternalTrainer.h"
#include "LearningPPOTrainer.h"
```

### 基本用法

以下示例展示了如何设置一个基本的 PPO 训练流程，包括配置训练器、添加网络、收集经验并启动训练。

```cpp
// 假设已包含必要头文件，并有一个神经网络实例 `MyNeuralNetwork`
// 以及一个用于收集经验的 `FEpisodeBuffer` 实例 `EpisodeBuffer`

using namespace UE::Learning;

// 1. 创建并配置外部训练器（例如，使用套接字通信）
TSharedPtr<IExternalTrainer> Trainer = MakeShared<FSocketExternalTrainer>(/* ... */);
if (!Trainer->IsValid())
{
    UE_LOG(LogLearning, Error, TEXT("Failed to create trainer."));
    return;
}

// 2. 将神经网络注册到训练器，获取网络ID
int32 NetworkId = Trainer->AddNetwork(MyNeuralNetwork);

// 3. 准备并发送训练配置
FPPOTrainerTrainingSettings TrainingSettings;
TrainingSettings.IterationNum = 100000;
TrainingSettings.LearningRatePolicy = 0.0003f;
// ... 其他配置

TSharedRef<FJsonObject> DataConfig = MakeShared<FJsonObject>();
TSharedRef<FJsonObject> ModelConfig = MakeShared<FJsonObject>();
TSharedRef<FJsonObject> TrainerConfig = MakeShared<FJsonObject>();
// ... 填充配置对象

Trainer->SendConfigs(DataConfig, ModelConfig, TrainerConfig);

// 4. 在游戏循环中收集经验
// 在每一步，将观测、动作、奖励推送到 EpisodeBuffer
EpisodeBuffer.PushObservations(ObservationId, CurrentObservations, ActiveInstances);
// ... 执行动作，获取奖励
EpisodeBuffer.PushRewards(RewardId, CurrentRewards, ActiveInstances);
EpisodeBuffer.IncrementEpisodeStepNums(ActiveInstances);

// 5. 当一集结束，将经验发送给训练器
FReplayBuffer ReplayBuffer;
// ... 将 EpisodeBuffer 的数据整理到 ReplayBuffer
Trainer->SendExperience(NetworkId, ReplayBuffer);

// 6. 尝试接收更新后的网络
if (Trainer->HasNetworkOrCompleted())
{
    Trainer->ReceiveNetwork(NetworkId, MyNeuralNetwork);
}
```

### 进阶用法

使用共享内存进行更高效的数据交换，适用于单机多进程训练场景。

```cpp
// 使用共享内存训练器
TSharedPtr<IExternalTrainer> SharedMemTrainer = MakeShared<FSharedMemoryExternalTrainer>(/* ... */);

// 分配共享内存区域用于经验数据和网络数据
TSharedMemoryArrayView<2, float> SharedObservations = SharedMemory::Allocate<2, float>(ObservationShape);
TSharedMemoryArrayView<1, uint8> SharedNetworkData = SharedMemory::Allocate<1, uint8>(NetworkDataSize);

// 在发送经验时，直接将数据写入共享内存视图
// ... 填充 SharedObservations
SharedMemTrainer->SendExperience(/* ... 共享内存相关参数 */);

// 接收网络时，从共享内存读取
SharedMemTrainer->ReceiveNetwork(NetworkId, MyNeuralNetwork, SharedNetworkData);
```

## Demo 示例

一个最小化的训练循环示例，展示如何集成 LearningTraining 模块。

**MyTrainingAgent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "LearningNeuralNetworkData.h"
#include "LearningExperience.h"
#include "LearningExternalTrainer.h"

class FMyTrainingAgent
{
public:
    void Initialize();
    void Tick(float DeltaTime);
    void Shutdown();

private:
    TSharedPtr<UE::Learning::IExternalTrainer> Trainer;
    ULearningNeuralNetworkData* PolicyNetwork;
    UE::Learning::FEpisodeBuffer EpisodeBuffer;
    int32 NetworkId = INDEX_NONE;
    int32 CurrentStep = 0;
};
```

**MyTrainingAgent.cpp**
```cpp
#include "MyTrainingAgent.h"
#include "LearningPPOTrainer.h"
#include "LearningSocketTraining.h"

void FMyTrainingAgent::Initialize()
{
    // 创建神经网络数据资产（假设已存在）
    PolicyNetwork = NewObject<ULearningNeuralNetworkData>();

    // 创建套接字训练器并连接
    Trainer = MakeShared<UE::Learning::FSocketExternalTrainer>(TEXT("127.0.0.1"), 12345);
    if (!Trainer->IsValid())
    {
        return;
    }

    // 注册网络
    NetworkId = Trainer->AddNetwork(*PolicyNetwork);

    // 发送配置
    auto DataConfig = MakeShared<FJsonObject>();
    auto ModelConfig = MakeShared<FJsonObject>();
    auto TrainerConfig = MakeShared<FJsonObject>();
    // ... 配置填充
    Trainer->SendConfigs(DataConfig, ModelConfig, TrainerConfig);

    // 初始化经验缓冲区
    EpisodeBuffer.Resize(1, 1000); // 1个实例，最多1000步
    EpisodeBuffer.Reset(UE::Learning::FIndexSet::All());
}

void FMyTrainingAgent::Tick(float DeltaTime)
{
    if (!Trainer || !Trainer->IsValid())
    {
        return;
    }

    // 模拟收集一步经验
    TArray<float> Observations = {0.1f, 0.2f, 0.3f}; // 示例观测
    TArray<float> Actions = {0.5f}; // 示例动作
    float Reward = 1.0f; // 示例奖励

    // 推送到缓冲区 (需要正确的ID，此处为示意)
    // EpisodeBuffer.PushObservations(0, Observations, ...);
    // EpisodeBuffer.PushActions(0, Actions, ...);
    // EpisodeBuffer.PushRewards(0, Reward, ...);
    // EpisodeBuffer.IncrementEpisodeStepNums(...);

    CurrentStep++;

    // 模拟一集结束
    if (CurrentStep >= 100)
    {
        // 将经验发送给训练器
        UE::Learning::FReplayBuffer ReplayBuffer;
        // ... 从 EpisodeBuffer 整理数据到 ReplayBuffer
        Trainer->SendExperience(NetworkId, ReplayBuffer);

        // 尝试接收更新
        if (Trainer->HasNetworkOrCompleted())
        {
            Trainer->ReceiveNetwork(NetworkId, *PolicyNetwork);
        }

        // 重置缓冲区和计数器
        EpisodeBuffer.Reset(UE::Learning::FIndexSet::All());
        CurrentStep = 0;
    }
}

void FMyTrainingAgent::Shutdown()
{
    if (Trainer)
    {
        Trainer->SendStop();
        Trainer->Terminate();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。该插件主要依赖引擎核心模块和其内部的 `Learning` 模块。

## 维护状态

### 近期更新

- 2026-04-24 `553c9043` [LearningAgents] Pass NNECpuPath to python directly
- 2026-04-24 `e424031e` [LearningAgents] Fix python site-package paths on Linux and Mac
- 2026-04-21 `34a398cd` LearningCore: Added tolerance to FindTime and ContainsTime functions.
- 2026-04-16 `ec5e1d55` LearningCore: Added binary search optimization for find on frames and frame ranges indices.
- 2026-04-14 `25720c8e` LearningCore: Added Sparse and NamedSparse observations

### 维护评价

- **实验性状态**：插件被明确标记为 `IsExperimentalVersion: true`，且默认禁用。这表明它仍处于早期开发或测试阶段，API 和功能可能不稳定，随时可能发生重大变更。
- **创建时间**：创建时间异常（未来），可能为测试或占位数据，无法反映真实维护历史。
- **综合评价**：这是一个实验性的机器学习训练库。由于其状态，**不建议在生产环境中使用**。它适合用于研究、原型开发或学习 UE 与机器学习集成的开发者。使用前需做好应对 API 变更和潜在不稳定性的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningCore)
- [官方文档]() (无)
- [测试用例]() (未在提供信息中发现)