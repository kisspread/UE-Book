# Learning Agents (LearningTraining 模块)

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 智能体训练 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、神经网络数据资产） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

`LearningTraining` 模块是整个 Learning Agents 插件中的训练通信层。它负责制定与外部训练进程（通常是 Python 编写的 PPO/强化学习训练器）之间的数据传输协议，并提供两种通信机制：**共享内存 (SharedMemory)** 和 **Socket**。该模块封装了训练配置的发送、经验数据的收集与发送、神经网络的接收与更新、停止信号等基本操作，是连接 Unreal 环境与外部机器学习训练引擎的“桥梁”。

**核心功能**：
- 通过共享内存或 Socket 与外部训练子进程通信
- 发送训练数据（经验数据、配置、网络参数）
- 接收更新后的神经网络权重
- 支持多个实例并行采集经验
- 提供 PPO 训练器设置结构体，配置学习率、批大小、折扣因子等超参数
- 封装子进程管理（启动、检测、终止）

## 使用场景

- **强化学习训练**：你需要训练一个 AI 角色（如四足机器人、竞速车辆）通过 RL 学会行走或驾驶。`LearningTraining` 提供与 Python 训练脚本的高效数据传输通道，让 Unreal 作为模拟环境不断收集经验，发送给训练器，接收更新后的策略网络。
- **模仿学习**：通过记录玩家操作作为示范数据，使用模仿学习算法训练 AI。该模块支持从回放缓冲区发送经验数据。
- **大规模并行训练**：利用共享内存机制，多个 Unreal 进程可以同时采集经验并共享给同一个训练进程，显著加速数据收集。
- **自定义训练器**：如果你需要实现自己的强化学习算法（非 PPO），可以通过 `IExternalTrainer` 接口或直接使用 Socket/SharedMemory 函数与自己的 Python 训练脚本通信。

## 蓝图用法

`LearningTraining` 模块的 API 主要面向 C++，蓝图层面主要提供一个命令let用于启动外部 PPO 训练服务器。其他核心功能（发送经验、接收网络）需要编写 C++ 代码或通过 `LearningAgents` 模块的蓝图节点间接使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ULearningSocketPPOTrainerServerCommandlet` | 启动一个 Socket 模式的 PPO 训练服务器子进程，监听外部连接 | `ULearningSocketPPOTrainerServerCommandlet` |

**使用示例（描述）**：
1. 在项目设置中启用 `LearningAgents` 插件。
2. 在命令行运行编辑器时附加参数：`Run=LearningSocketPPOTrainerServer -maxIterations=100000 -device=GPU`。该命令let会启动一个 Python 训练子进程，等待 Unreal 客户端连接。
3. 在游戏逻辑中通过 C++ 调用 `IExternalTrainer` 或 `SocketTraining::SendConfig` 等函数开始训练循环。

## C++ 用法

### 头文件引入

```cpp
#include "LearningTrainer.h"           // FSubprocess, ETrainerResponse, ELogSetting
#include "LearningExternalTrainer.h"   // IExternalTrainer
#include "LearningSharedMemoryTraining.h" // SharedMemoryTraining 命名空间函数
#include "LearningSocketTraining.h"    // SocketTraining 命名空间函数
#include "LearningExperience.h"        // FEpisodeBuffer, FReplayBuffer
#include "LearningPPOTrainer.h"        // FPPOTrainerTrainingSettings, FPPOTrainerNetworkSettings, FPPOTrainerGameSettings
#include "LearningSharedMemory.h"      // TSharedMemoryArrayView
```

### 基本用法

#### 1. 创建并启动外部训练器（Socket 模式）

```cpp
// 来源: Engine/Plugins/Experimental/LearningAgents/Source/LearningTraining/Private/LearningSocketTraining.cpp

#include "LearningSocketTraining.h"
#include "LearningExternalTrainer.h"

// 创建 Socket 外部训练器
TSharedPtr<UE::Learning::IExternalTrainer> Trainer = UE::Learning::SocketTrainer::Create();

// 配置训练器参数（PPO 设置）
UE::Learning::FPPOTrainerTrainingSettings TrainingSettings;
TrainingSettings.IterationNum = 100000;
TrainingSettings.LearningRatePolicy = 0.0001f;
TrainingSettings.LearningRateCritic = 0.001f;
TrainingSettings.IterationsPerGather = 32;

// 将设置打包成 JSON 发送
TSharedRef<FJsonObject> DataConfig = MakeShared<FJsonObject>();
TSharedRef<FJsonObject> TrainerConfig = MakeShared<FJsonObject>();
// ... 填充配置对象 ...

ETrainerResponse Response = Trainer->SendConfigs(DataConfig, TrainerConfig, ELogSetting::Normal);
if (Response == ETrainerResponse::Success)
{
    // 添加需要训练的网络
    ULearningNeuralNetworkData* Network = NewObject<ULearningNeuralNetworkData>();
    int32 NetworkId = Trainer->AddNetwork(*Network);

    // 开始收集经验并发送
    // ... 收集经验到 FReplayBuffer ...
    Trainer->SendExperience(...); // 重载函数
}
```

#### 2. 使用共享内存训练

```cpp
// 来源: Engine/Plugins/Experimental/LearningAgents/Source/LearningTraining/Private/LearningSharedMemoryTraining.cpp

#include "LearningSharedMemoryTraining.h"
#include "LearningSharedMemory.h"

using namespace UE::Learning;

// 假设我们已经创建了子进程 Process 和共享内存控制区域 Controls
TLearningArrayView<1, volatile int32> Controls; // 映射自共享内存

// 发送训练配置信号（通知训练器读取配置）
ETrainerResponse Response = SharedMemoryTraining::SendConfigSignal(
    Controls,
    ELogSetting::Normal);

// 从共享内存接收更新后的网络
ULearningNeuralNetworkData* OutNetwork = NewObject<ULearningNeuralNetworkData>();
TArray<uint8> NetworkBuffer;
int32 NetworkId = 0;
Response = SharedMemoryTraining::RecvNetwork(
    Controls,
    NetworkId,
    *OutNetwork,
    &Process,
    NetworkBuffer,
    30.0f, // 超时 30 秒
    nullptr,
    ELogSetting::Normal);

// 发送经验数据
FReplayBuffer ReplayBuffer; // 需要预先填充
SharedMemoryTraining::SendExperience(
    EpisodeStarts,
    EpisodeLengths,
    EpisodeCompletionModes,
    FinalObservations,
    FinalMemoryStates,
    Observations,
    Actions,
    ActionModifiers,
    MemoryStates,
    Rewards,
    Controls,
    &Process,
    ReplayBufferId,
    ReplayBuffer,
    30.0f);
```

#### 3. 使用 Socket 发送经验

```cpp
// 来源: Engine/Plugins/Experimental/LearningAgents/Source/LearningTraining/Private/LearningSocketTraining.cpp

#include "LearningSocketTraining.h"

FSocket* Socket = ...; // 已连接到训练服务器的 Socket

// 等待连接建立（服务器端）
ETrainerResponse ConnResponse = SocketTraining::WaitForConnection(
    *Socket,
    &Process,
    *Addr,
    60.0f);

// 发送配置字符串
SocketTraining::SendConfig(
    *Socket,
    ConfigString,
    &Process,
    10.0f);

// 接收网络
ULearningNeuralNetworkData* Network = ...;
int32 NetworkVersion = 0;
TArray<uint8> Buffer;
SocketTraining::RecvNetwork(
    *Socket,
    NetworkId,
    NetworkVersion,
    *Network,
    &Process,
    Buffer,
    30.0f);

// 发送经验
SocketTraining::SendExperience(
    *Socket,
    NetworksVersion,
    ReplayBufferId,
    ReplayBuffer,
    &Process,
    30.0f);
```

### 进阶用法

#### 1. 使用 IExternalTrainer 接口进行全生命周期管理

```cpp
// 来源: Engine/Plugins/Experimental/LearningAgents/Source/LearningTraining/Public/LearningExternalTrainer.h

#include "LearningExternalTrainer.h"

// 创建 Socket 训练器（也可用共享内存：SharedMemoryTrainer::Create()）
TSharedPtr<UE::Learning::IExternalTrainer> Trainer = UE::Learning::SocketTrainer::Create();

// 启动子进程
bool bLaunched = Trainer->Launch(TrainingPath, Params);

// 循环：采集经验 -> 发送 -> 接收网络 -> 更新策略
while (!bTrainingComplete)
{
    if (Trainer->HasNetworkOrCompleted())
    {
        // 接收最新的网络（仅当训练器推送了新网络时）
        TArray<ETrainerResponse> Responses = Trainer->ReceiveNetworks(
            {NetworkId1, NetworkId2},
            {Net1, Net2});
    }

    // 收集经验数据并填充 EpisodeBuffer
    FEpisodeBuffer EpisodeBuffer;
    EpisodeBuffer.Resize(MaxInstanceNum, MaxStepNum);
    // ... 填充数据 ...

    // 打包到 FReplayBuffer
    FReplayBuffer ReplayBuffer;
    ReplayBuffer.Reset(Instances);
    // ... 添加 episode 到 ReplayBuffer ...

    // 发送经验给训练器
    ETrainerResponse SendResp = Trainer->SendExperience(ReplayBuffer, CompletionModes, ...);
    if (SendResp == ETrainerResponse::Completed || SendResp == ETrainerResponse::Stopped)
        break;
}

// 停止训练
Trainer->SendStop();
Trainer->Wait(60.0f);
```

#### 2. 使用共享内存实现多进程通信

```cpp
// 来源: Engine/Plugins/Experimental/LearningAgents/Source/LearningTraining/Private/LearningSharedMemoryTraining.cpp

#include "LearningSharedMemory.h"

// 分配一块共享内存用于控制信号（10 个 int32 控制位）
TSharedMemoryArrayView<1, int32> ControlMemory = SharedMemory::Allocate<int32>(
    TLearningArrayShape<1>(10));
FGuid ControlGuid = ControlMemory.Guid;

// 另一个进程可以通过相同的 Guid 映射同一块内存
TSharedMemoryArrayView<1, int32> MappedControl = SharedMemory::Map<int32>(
    ControlGuid,
    TLearningArrayShape<1>(10),
    false); // bCreate = false，因为已存在

// 使用 volatile 方式访问控制信号（保证跨进程可见性）
volatile int32* Controls = MappedControl.View.GetData();
Controls[0] = 1; // 设置信号
```

## Demo 示例

以下是一个完整的、简化的示例，展示如何在 Unreal 中使用 `LearningTraining` 模块通过 Socket 与外部训练器通信并运行训练循环。假设训练器已经启动（如 `LearningSocketPPOTrainerServer`）。

### TrainingController.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LearningTrainer.h"
#include "LearningExternalTrainer.h"
#include "LearningNeuralNetworkData.h"
#include "TrainingController.generated.h"

UCLASS()
class ATrainingController : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

protected:
    void StartTraining();
    void CollectExperience();
    void SendExperienceAndUpdateNetwork();

    UPROPERTY(EditAnywhere, Category = "Training")
    FString TrainingExecutablePath = TEXT("python");

    UPROPERTY(EditAnywhere, Category = "Training")
    FString TrainingArgs = TEXT("train.py --port=12345");

    TSharedPtr<UE::Learning::IExternalTrainer> Trainer;
    UPROPERTY()
    ULearningNeuralNetworkData* PolicyNetwork;

    int32 NetworkId = INDEX_NONE;
    bool bTrainingActive = false;
    int32 EpisodeCounter = 0;
};
```

### TrainingController.cpp

```cpp
#include "TrainingController.h"
#include "LearningNeuralNetworkData.h"
#include "LearningExternalTrainer.h"
#include "LearningExperience.h"
#include "LearningAction.h"
#include "LearningObservation.h"
#include "Engine/World.h"

void ATrainingController::BeginPlay()
{
    Super::BeginPlay();
    StartTraining();
}

void ATrainingController::StartTraining()
{
    // 创建 Socket 训练器
    Trainer = UE::Learning::SocketTrainer::Create();
    if (!Trainer.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create trainer"));
        return;
    }

    // 启动外部训练进程
    bool bLaunched = Trainer->Launch(TrainingExecutablePath, TrainingArgs);
    if (!bLaunched)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to launch training subprocess"));
        return;
    }

    // 创建策略网络并注册到训练器
    PolicyNetwork = NewObject<ULearningNeuralNetworkData>(this);
    NetworkId = Trainer->AddNetwork(*PolicyNetwork);
    if (NetworkId == INDEX_NONE)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to add network to trainer"));
        return;
    }

    // 发送配置（此处简化，实际需要构建 JSON）
    TSharedRef<FJsonObject> DataConfig = MakeShared<FJsonObject>();
    // 填充 Observation/Action 模式等...
    TSharedRef<FJsonObject> TrainerConfig = MakeShared<FJsonObject>();
    TrainerConfig->SetNumberField(TEXT("IterationNum"), 100000);
    TrainerConfig->SetNumberField(TEXT("LearningRatePolicy"), 0.0001f);

    ETrainerResponse Response = Trainer->SendConfigs(DataConfig, TrainerConfig);
    if (Response == ETrainerResponse::Success)
    {
        bTrainingActive = true;
        UE_LOG(LogTemp, Log, TEXT("Training started"));
    }
}

void ATrainingController::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    if (!bTrainingActive) return;

    // 简单的训练循环：每帧收集一次经验，每 100 帧发送一次
    CollectExperience();
    if (++EpisodeCounter >= 100)
    {
        EpisodeCounter = 0;
        SendExperienceAndUpdateNetwork();
    }
}

void ATrainingController::CollectExperience()
{
    // 模拟收集经验：填充 EpisodeBuffer
    // 实际应用中需根据游戏状态填充 Observation/Action/Reward
}

void ATrainingController::SendExperienceAndUpdateNetwork()
{
    // 创建 ReplayBuffer 并填充经验
    UE::Learning::FReplayBuffer ReplayBuffer;
    // ... 填充数据 ...

    // 发送经验
    ETrainerResponse SendResp = Trainer->SendExperience(
        ReplayBuffer,
        TArray<UE::Learning::ECompletionMode>(),
        {}  // 可选的 FinalObservations 等
    );

    if (SendResp == ETrainerResponse::Completed)
    {
        UE_LOG(LogTemp, Log, TEXT("Training completed"));
        bTrainingActive = false;
        return;
    }

    // 检查是否有更新后的网络
    if (Trainer->HasNetworkOrCompleted())
    {
        ETrainerResponse RecvResp = Trainer->ReceiveNetwork(
            NetworkId,
            *PolicyNetwork,
            nullptr,
            UE::Learning::ELogSetting::Normal);
        if (RecvResp == ETrainerResponse::Success)
        {
            UE_LOG(LogTemp, Log, TEXT("Network updated"));
            // 应用新网络到角色控制器
        }
    }
}
```

## 模块依赖

本模块依赖的核心插件模块。公共依赖（Core, Engine 等已省略）。

| 模块 | 用途 |
|---|---|
| `Learning` | 学习算法基础库（数组、观察/动作模式、神经网络基础类型） |
| `Sockets` | Socket 通信功能 (SocketTraining 使用) |
| `Json` | 配置 JSON 序列化与反序列化 |
| `Projects` | 子进程路径解析 |
| `UnrealEd` | 仅在 `LearningAgentsTraining` 模块需要，本模块直接依赖 `LearningAgentsTraining` 可能间接依赖 |

需要在你的项目的 `Build.cs` 中添加：

```csharp
PublicDependencyModuleNames.AddRange(
    new string[]
    {
        "LearningTraining",
        "Learning",
        "Sockets",
        "Json",
    }
);
```

## 维护状态

### 近期更新

- 2025-09-23 e6f9d5f — [LearningAgents] LearningAgentsRecording
- 2025-09-23 dcf81878 — [LearningAgents] bug fix to conv1d conv2d serialization
- 2025-09-23 86de7c71 — [LearningAgents] Missing types in ComputeObservationSchemaSubsetIndices and bugfix
- 2025-09-23 1571e33e — LearningAgents: Ensure instead of check during GetAgent
- 2025-09-16 f485ef53 — [LearningAgents] - schema subset bug fix

### 维护评价

- **创建时间**：2025-09-16，距今不足一个月。
- **更新频率**：在近一周内（2025-09-23）有多次提交，修复了多个 bug，并增加了录制功能。更新活跃。
- **状态**：该插件目前处于实验性阶段，但代码质量和维护力度较高，Epic 持续投入。暂无废弃迹象。
- **推荐使用**：非常适合需要将 Unreal 作为模拟环境进行强化学习训练的项目。由于是实验性插件，API 可能发生变化，建议锁定版本并关注更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/learning-agents-in-unreal-engine/)（待完善）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents/Tests)