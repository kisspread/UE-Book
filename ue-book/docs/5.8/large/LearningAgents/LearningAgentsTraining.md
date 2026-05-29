# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 智能体学习库 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（数据资产、蓝图工具） |
| 模块 | `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 是一个端到端的机器学习框架，用于在游戏内训练智能体（AI角色）。它并非简单地封装某个ML算法，而是提供了一套完整的工作流，旨在解决将强化学习（RL）和模仿学习（IL）集成到游戏开发中的复杂性问题。通过该框架，开发者可以在游戏运行时定义观察空间、动作空间、奖励函数，并启动训练循环，最终得到一个可部署的策略网络，用于控制游戏中的NPC或玩家角色。

## 使用场景

- 你想让游戏中的NPC（如敌人、同伴）通过“试错”或“模仿人类玩家”来学习复杂的导航、战斗或交互策略。
- 你需要快速原型化不同的AI行为策略，并在真实的游戏环境中进行训练和评估。
- 你的项目需要实现行为克隆（Behavior Cloning），即让AI模仿录制的玩家操作数据。
- 你正在研究游戏AI的强化学习，并希望利用UE5的渲染和物理能力作为训练环境（Gym）。
- 你需要为游戏中的多个并行训练实例（Gym）进行管理，并希望加快训练数据采集速度。

## 蓝图用法

该插件主要通过蓝图暴露功能，核心类继承自`ULearningAgentsManagerListener`，需要在蓝图中实例化并配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakePPOTrainer` | 创建一个PPO（近端策略优化）强化学习训练器 | `ULearningAgentsPPOTrainer` |
| `MakeImitationTrainer` | 创建一个模仿学习训练器 | `ULearningAgentsImitationTrainer` |
| `MakeFlowMatchingTrainer` | 创建一个基于流匹配（Flow Matching）的模仿学习训练器 | `ULearningAgentsFlowMatchingTrainer` |
| `MakeRecorder` | 创建一个数据录制器，用于录制智能体的观察和动作以制作模仿学习数据集 | `ULearningAgentsRecorder` |
| `MakeTrainingEnvironment` | 创建训练环境，负责定义奖励和完成条件 | `ULearningAgentsTrainingEnvironment` |
| `RunTraining` | 便捷函数，启动或继续一轮训练迭代 | `ULearningAgentsPPOTrainer` |
| `ProcessExperience` | 处理收集到的经验，触发训练迭代 | `ULearningAgentsPPOTrainer` |
| `GatherObservations` | 收集当前所有智能体的观察数据（需要在子类中实现） | `ULearningAgentsInteractor` |
| `MakeReward` | 创建一个奖励值（用于在训练环境中定义奖励函数） | `ULearningAgentsRewards` (库) |
| `MakeCompletion` | 创建一个完成状态（用于在训练环境中定义结束条件） | `ULearningAgentsCompletions` (库) |

### 使用示例（蓝图描述）

1.  **训练强化学习智能体**：
    *   创建一个自定义的`ULearningAgentsTrainingEnvironment`蓝图子类，重写`GatherAgentReward`和`GatherAgentCompletion`函数来定义奖励和结束条件。
    *   在关卡蓝图中，使用`MakePPOTrainer`节点创建训练器，传入`ULearningAgentsManager`、`ULearningAgentsInteractor`（需要自定义）、`ULearningAgentsPolicy`、`ULearningAgentsCritic`以及一个`FLearningAgentsCommunicator`。
    *   在事件图表中，使用`RunTraining`节点并配置超参数。每一帧调用它，即可自动完成“收集观察 -> 执行动作 -> 收集奖励 -> 处理经验 -> 更新策略”的循环。
2.  **录制并训练模仿学习智能体**：
    *   使用`MakeRecorder`创建一个录制器。
    *   通过人类玩家或传统AI控制器（如`AIController`）来控制角色，在`GatherObservations`后，调用`AddExperience`来录制（观察-动作）对。
    *   调用`EndRecording`保存为`ULearningAgentsRecording`数据资产。
    *   使用`MakeImitationTrainer`创建模仿学习训练器，并调用`RunTraining`，传入录制的数据资产进行训练。

## C++ 用法

该插件的C++使用主要涉及实现自定义的训练环境、交互器和策略。

### 头文件引入

```cpp
#include "LearningAgentsTraining.h"
#include "LearningAgentsPPOTrainer.h"
#include "LearningAgentsRecorder.h"
// 其他需要的头文件，如 LearningAgentsManager, LearningAgentsPolicy 等
```

### 基本用法 (定义训练环境)

创建一个自定义的训练环境子类来定义奖励和完成逻辑。

```cpp
// MyTrainingEnvironment.h
#pragma once
#include "LearningAgentsTrainingEnvironment.h"
#include "MyTrainingEnvironment.generated.h"

UCLASS()
class UMyTrainingEnvironment : public ULearningAgentsTrainingEnvironment
{
    GENERATED_BODY()

public:
    // 重写收集单个智能体奖励的回调
    virtual void GatherAgentReward_Implementation(float& OutReward, const int32 AgentId) override;
    // 重写收集单个智能体完成状态的回调
    virtual void GatherAgentCompletion_Implementation(ELearningAgentsCompletion& OutCompletion, const int32 AgentId) override;
    // 重写重置单个智能体剧集的回调
    virtual void ResetAgentEpisode_Implementation(const int32 AgentId) override;
};
```

```cpp
// MyTrainingEnvironment.cpp
#include "MyTrainingEnvironment.h"

void UMyTrainingEnvironment::GatherAgentReward_Implementation(float& OutReward, const int32 AgentId)
{
    // 根据游戏逻辑计算奖励，例如到达目标
    bool bReachedGoal = /* ... */;
    if (bReachedGoal)
    {
        OutReward = ULearningAgentsRewards::MakeRewardOnCondition(true, 1.0f);
    }
}

void UMyTrainingEnvironment::GatherAgentCompletion_Implementation(ELearningAgentsCompletion& OutCompletion, const int32 AgentId)
{
    // 当时间超过限制或到达目标时，结束剧集
    float EpisodeTime = GetEpisodeTime(AgentId);
    if (EpisodeTime > 30.0f || bReachedGoal)
    {
        OutCompletion = ULearningAgentsCompletions::MakeCompletion(ELearningAgentsCompletion::Termination);
    }
    else
    {
        OutCompletion = ELearningAgentsCompletion::Running;
    }
}

void UMyTrainingEnvironment::ResetAgentEpisode_Implementation(const int32 AgentId)
{
    // 将智能体重置到起点
    AActor* Agent = GetManager()->GetAgent(AgentId);
    if (Agent)
    {
        Agent->SetActorLocation(FVector::ZeroVector);
    }
}
```

### 进阶用法 (在C++中启动训练循环)

在游戏逻辑中控制训练流程。

```cpp
// 在某个Actor或Component中
UPROPERTY()
TObjectPtr<ULearningAgentsPPOTrainer> PPOTrainer;

void AMyTrainerActor::SetupTraining()
{
    // 假设 Manager, Interactor, Policy, Critic, TrainingEnvironment 等已创建并设置好
    FLearningAgentsCommunicator Communicator = ULearningAgentsCommunicatorLibrary::MakeSharedMemoryTrainingProcess();
    PPOTrainer = ULearningAgentsPPOTrainer::MakePPOTrainer(
        Manager, Interactor, TrainingEnvironment, Policy, Critic, Communicator);
}

void AMyTrainerActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (PPOTrainer)
    {
        // 便捷的训练循环调用，内部处理奖励、完成、经验处理和推理
        PPOTrainer->RunTraining();
    }
}
```

## Demo 示例

一个最小化的C++训练流程设置示例。

```cpp
// MyTrainingSetup.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyTrainingSetup.generated.h"

class ULearningAgentsManager;
class ULearningAgentsInteractor;
class ULearningAgentsPolicy;
class ULearningAgentsPPOTrainer;
class ULearningAgentsTrainingEnvironment;

UCLASS()
class AMyTrainingSetup : public AActor
{
    GENERATED_BODY()

public:
    AMyTrainingSetup();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    UPROPERTY()
    TObjectPtr<ULearningAgentsManager> AgentManager;

    UPROPERTY()
    TObjectPtr<ULearningAgentsInteractor> AgentInteractor;

    UPROPERTY()
    TObjectPtr<ULearningAgentsPolicy> AgentPolicy;

    UPROPERTY()
    TObjectPtr<ULearningAgentsTrainingEnvironment> TrainEnv;

    UPROPERTY()
    TObjectPtr<ULearningAgentsPPOTrainer> PPOTrainer;

    bool bIsTrainingInitialized = false;
};
```

```cpp
// MyTrainingSetup.cpp
#include "MyTrainingSetup.h"
#include "LearningAgentsManager.h"
#include "LearningAgentsInteractor.h"
#include "LearningAgentsPolicy.h"
#include "LearningAgentsPPOTrainer.h"
#include "LearningAgentsTrainingEnvironment.h"
#include "LearningAgentsCommunicator.h"

AMyTrainingSetup::AMyTrainingSetup()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyTrainingSetup::BeginPlay()
{
    Super::BeginPlay();

    // 1. 创建管理器、交互器、策略等组件 (通常通过蓝图或配置设置，这里为简化示意)
    // AgentManager = NewObject<ULearningAgentsManager>(this);
    // AgentInteractor = NewObject<ULearningAgentsInteractor>(this);
    // ... 等等设置

    // 2. 创建训练环境
    TrainEnv = ULearningAgentsTrainingEnvironment::MakeTrainingEnvironment(
        AgentManager, UMyTrainingEnvironment::StaticClass());

    // 3. 创建通信器并启动训练器
    FLearningAgentsCommunicator Communicator = ULearningAgentsCommunicatorLibrary::MakeSharedMemoryTrainingProcess();
    PPOTrainer = ULearningAgentsPPOTrainer::MakePPOTrainer(
        AgentManager, AgentInteractor, TrainEnv, AgentPolicy, Critic, Communicator);

    // 4. 初始化训练
    if (PPOTrainer)
    {
        PPOTrainer->BeginTraining();
        bIsTrainingInitialized = true;
    }
}

void AMyTrainingSetup::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    if (bIsTrainingInitialized && PPOTrainer)
    {
        // 每帧调用，驱动训练循环
        PPOTrainer->RunTraining();
    }
}
```

## 模块依赖

要使用此插件，你的项目模块通常只需要依赖其核心的`LearningAgents`模块。但具体的实现可能需要额外的模块。

| 模块 | 用途 |
|---|---|
| `LearningAgents` | 插件核心模块，提供基础类型、管理器、交互器、策略等。**这是用户项目最常直接依赖的模块**。 |
| `LearningAgentsTraining` | 包含具体的训练器（PPO、模仿学习、流匹配）和训练环境。依赖于`UnrealEd`（用于与编辑器训练进程通信）。 |
| `LearningAgentsReplay` | 包含数据录制和重放相关的类。 |
| `LearningAgentsTrainingEditor` | 编辑器专用模块，提供训练相关的编辑器工具和UI。 |

**你的模块依赖**:
- 在`.Build.cs`文件中，通常只需要添加对 `LearningAgents` 的依赖。
```csharp
PublicDependencyModuleNames.AddRange(new string[] { "LearningAgents" });
```
- 如果你需要在C++中直接使用PPOTrainer等高级功能，可能需要添加 `LearningAgentsTraining`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0b2b6629` | [LearningAgents] Fix interactor SetActionVector | 修复交互器设置动作向量的bug |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复64位格式说明符不匹配的编译错误 |
| 2026-04-24 | `553c9043` | [LearningAgents] Pass NNECpuPath to python directly | 直接向Python传递NNE CPU路径，简化配置 |
| 2026-04-20 | `305f49dd` | [LearningAgents] Improve reinitialize recording behavior to reset and add new schema (#14361) | 改进录制重初始化行为，支持重置并添加新schema |
| 2026-04-14 | `898b7c7c` | [LACombat] Replay Runtime Recording | 实现战斗演示的运行时录制功能 |

### 维护评价

- **创建时间**: 2023年3月，是UE5中较新的实验性插件。
- **近期更新**: 更新非常活跃，在最近两个月内有多次提交，主要是bug修复、兼容性改进和功能优化，表明该插件处于积极开发和维护阶段。
- **推荐使用**: **是，但需注意其实验性状态**。该插件提供了强大且相对完善的机器学习训练框架，对于希望在游戏中集成ML的开发者来说极具价值。然而，作为“实验性”插件，其API在未来版本中可能发生重大变化，且可能需要更多的学习和调试成本。适合用于原型验证和研究项目，在生产环境中使用需谨慎评估。
- **警告**: 标记为“实验性”（`EnabledByDefault=false`），且文档和社区支持可能有限。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]() （暂无公开文档）
- [测试用例]() （请查阅插件源码目录中的 `Tests` 文件夹）