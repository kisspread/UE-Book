# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产和训练配置） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约1年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 提供了一套完整的框架，用于在 Unreal Engine 中实现基于强化学习和模仿学习的 AI 角色控制。它解决了传统游戏 AI（如行为树、状态机）难以自动学习复杂策略的问题，允许开发者通过定义观察（Observation）、动作（Action）、策略（Policy）和评价器（Critic），让智能体自主从试错或演示数据中学习行为。

核心设计围绕一个**智能体管理器（Manager）**展开，管理器追踪所有参与学习的游戏对象，并通过**监听器（Listener）**模式向策略、评价器、交互器等组件同步状态。用户需要继承 `ULearningAgentsInteractor` 来定义“如何观察世界”和“如何执行动作”，然后使用 *Policy（策略）*（神经网络或手工控制器）生成动作。训练过程可由配套的训练模块（`LearningAgentsTraining`）驱动，支持多种深度强化学习算法。

该插件非常适合以下场景：
- 需要为 NPC 或角色学习复杂移动、战斗或决策行为，而无需手动编写精细的规则。
- 希望从人类玩家或其他 AI 的行为中通过模仿学习快速获得初始策略，再通过强化学习进行优化。
- 在游戏原型阶段快速验证 ML 驱动的 AI 可行性。

## 使用场景

- **训练一个四足机器人走路**：定义观察为关节角度、速度、地面接触，动作为关节力矩，策略网络输出力矩值，评价器给出回报。
- **让 AI 学会玩自定义迷你游戏**：使用 `LearningAgentsManager` 管理多个 Agent，每个 Agent 是一个玩家控制的棋子，交互器定义游戏规则的观察和动作，训练后在运行时加载训练的神经网络资产。
- **从人类演示中学习**：使用 `ULearningAgentsController` 手工编写一个控制器来模拟人类行为，生成的轨迹作为训练数据（通过 `LearningAgentsReplay` 模块记录）。

## 蓝图用法

本模块提供了大量蓝图可调用函数，主要分布在以下几个核心类中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAgent` | 将一个 Actor/Object 作为 Agent 添加到管理器 | `ULearningAgentsManager` |
| `RemoveAgent` | 从管理器移除指定 Agent | `ULearningAgentsManager` |
| `GetAgent` | 根据 AgentId 获取对应的游戏对象 | `ULearningAgentsManagerListener` |
| `MakeInteractor` | 创建并初始化一个交互器实例 | `ULearningAgentsInteractor` |
| `MakePolicy` | 创建并初始化一个策略实例，可指定神经网络资产和设置 | `ULearningAgentsPolicy` |
| `MakeCritic` | 创建并初始化一个评价器实例 | `ULearningAgentsCritic` |
| `MakeController` | 创建并初始化一个手工控制器实例 | `ULearningAgentsController` |
| `GatherObservations` | 收集所有 Agent 的观察数据（需先实现 `SpecifyAgentObservation` 和 `GatherAgentObservation`） | `ULearningAgentsInteractor` |
| `PerformActions` | 执行当前策略或控制器输出的动作 | `ULearningAgentsInteractor` |
| `EvaluatePolicy` | 运行神经网络策略生成动作 | `ULearningAgentsPolicy` |
| `EvaluateController` | 运行手工控制器生成动作 | `ULearningAgentsController` |
| `RunController` | 一步完成收集观察、评估控制器、执行动作 | `ULearningAgentsController` |
| `LoadNetworkFromSnapshot` | 从磁盘加载训练好的神经网络权重 | `ULearningAgentsNeuralNetwork` |
| `SaveNetworkToSnapshot` | 将网络权重保存到磁盘 | `ULearningAgentsNeuralNetwork` |

### 使用示例（蓝图）

1. **初始化系统**  
   在 GameMode 或 Actor 的 BeginPlay 中创建 `LearningAgentsManager` 组件，设置最大 Agent 数量（例如 `SetMaxAgentNum(10)`）。

2. **创建交互器**  
   使用 `MakeInteractor` 创建一个自定义的 `ULearningAgentsInteractor` 蓝图子类。在该子类中重写 `SpecifyAgentObservation` 和 `SpecifyAgentAction` 来定义观察/动作的结构，重写 `GatherAgentObservation` 和 `PerformAgentAction` 来实现具体的读写。

3. **创建策略**  
   使用 `MakePolicy` 创建一个 `ULearningAgentsPolicy` 实例，传入上述交互器和神经网络资产（可选）。策略会自动根据交互器定义的观察和动作结构构建网络。

4. **运行**  
   每帧调用 `Policy` 的 `EvaluatePolicy` 或 `Interactor` 的 `GatherObservations` → `PerformActions` 序列。你可以在蓝图逻辑中控制何时收集、何时执行。

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsManager.h"
#include "LearningAgentsInteractor.h"
#include "LearningAgentsPolicy.h"
```

### 基本用法

以下示例展示了如何创建一个管理器和交互器，并添加一个 Actor 作为 Agent。

```cpp
// 假设我们在一个 AActor 的子类中
#include "LearningAgentsManager.h"
#include "LearningAgentsInteractor.h"
#include "LearningAgentsPolicy.h"

// 创建一个管理者组件（通常在构造函数或 BeginPlay 中）
ULearningAgentsManager* Manager = CreateDefaultSubobject<ULearningAgentsManager>(TEXT("AgentManager"));
Manager->SetMaxAgentNum(5); // 最大支持 5 个 Agent

// 创建一个自定义交互器（你自己的 ULearningAgentsInteractor 子类）
ULearningAgentsInteractor* Interactor = ULearningAgentsInteractor::MakeInteractor(Manager, MyInteractorClass, TEXT("MyInteractor"));

// 添加当前 Actor 作为 Agent
int32 AgentId = Manager->AddAgent(this); // this 可以是一个 AActor 实例

// 之后在游戏循环中收集观察并执行动作
Interactor->GatherObservations();
// （若使用策略）Policy->EvaluatePolicy();
Interactor->PerformActions();
```

### 进阶用法

更完整的训练循环示例：

```cpp
// 假设 Manager, Interactor, Policy 已创建
// 每个 Tick 中：
void AMyGameMode::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 1. 收集所有 Agent 的观察
    Interactor->GatherObservations();
    
    // 2. 运行策略生成动作
    Policy->EvaluatePolicy();
    
    // 3. 将动作应用到环境
    Interactor->PerformActions();
    
    // 4. 可选：更新评价器（训练时）
    Critic->EvaluateCritic();
}
```

从训练后的网络资产加载权重：

```cpp
ULearningAgentsNeuralNetwork* NetworkAsset = LoadObject<ULearningAgentsNeuralNetwork>(nullptr, TEXT("/Game/TrainedPolicies/MyPolicy.MyPolicy"));
if (NetworkAsset)
{
    Policy->LoadPolicyFromAsset(NetworkAsset); // 假设该方法存在，实际使用 SetupPolicy 时传入资产
}
```

*来源：`Engine/Plugins/Experimental/LearningAgents/Source/LearningAgents/Public/LearningAgentsManager.h`, `LearningAgentsInteractor.h`, `LearningAgentsPolicy.h`*

## Demo 示例

以下是一个最小可编译的角色组件实现，它创建了 Manager 和交互器，并在 Tick 中驱动单一 Agent。

### MyLearningComponent.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "MyLearningComponent.generated.h"

class ULearningAgentsManager;
class ULearningAgentsInteractor;
class ULearningAgentsPolicy;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class UMyLearningComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyLearningComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

protected:
    UPROPERTY(VisibleAnywhere, Category = "Learning")
    TObjectPtr<ULearningAgentsManager> Manager;

    UPROPERTY(VisibleAnywhere, Category = "Learning")
    TObjectPtr<ULearningAgentsInteractor> Interactor;

    UPROPERTY(VisibleAnywhere, Category = "Learning")
    TObjectPtr<ULearningAgentsPolicy> Policy;
};
```

### MyLearningComponent.cpp

```cpp
#include "MyLearningComponent.h"
#include "LearningAgentsManager.h"
#include "LearningAgentsInteractor.h"
#include "LearningAgentsPolicy.h"

UMyLearningComponent::UMyLearningComponent()
{
    // 让组件每帧 Tick
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyLearningComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建 Manager
    Manager = NewObject<ULearningAgentsManager>(this);
    Manager->SetMaxAgentNum(1);

    // 创建自定义交互器（需要你先实现一个 ULearningAgentsInteractor 的子类）
    // 这里假设你有一个蓝图或 C++ 子类：ULearningAgentsInteractor 的 BlueprintGeneratedClass
    UClass* InteractorClass = ...; // 例如 LoadClass<ULearningAgentsInteractor>(nullptr, TEXT("/Game/MyInteractor.MyInteractor_C"));
    Interactor = ULearningAgentsInteractor::MakeInteractor(Manager, InteractorClass, TEXT("MyInteractor"));

    // 创建策略
    Policy = ULearningAgentsPolicy::MakePolicy(Manager, Interactor, ULearningAgentsPolicy::StaticClass(), TEXT("MyPolicy"));

    // 将当前 Actor 添加为 Agent
    Manager->AddAgent(GetOwner());
}

void UMyLearningComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 收集观察 -> 评估策略 -> 执行动作
    Interactor->GatherObservations();
    Policy->EvaluatePolicy();
    Interactor->PerformActions();
}
```

**注意**：`InteractorClass` 需要替换为实际存在的 `ULearningAgentsInteractor` 子类的 `TSubclassOf`，你可以通过蓝图或 C++ 实现并提供一个默认类。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Learning` | 核心机器学习库（神经网络、优化器、数据容器） |

该插件中的其他模块（如 `LearningAgentsTraining`）可能在编译时需要额外依赖 `UnrealEd` 等，但本模块 `LearningAgents` 自身仅依赖 `Learning` 及标准引擎模块（CoreUObject, Engine 等）。

## 维护状态

### 近期更新

- 2025-09-23 e6f9d5f [LearningAgents] LearningAgentsRecording
- 2025-09-23 dcf81878 [LearningAgents] bug fix to conv1d conv2d serialization
- 2025-09-23 86de7c71 [LearningAgents] Missing types in ComputeObservationSchemaSubsetIndices and bugfix
- 2025-09-23 1571e33e LearningAgents: Ensure instead of check during GetAgent
- 2025-09-16 f485ef53 [LearningAgents] - schema subset bug fix

### 维护评价

该插件自 2025 年 9 月创建以来，在短期内集中进行了多次功能性提交和 bug 修复，但此后超过一年没有实质性的新功能或维护更新。目前处于**维护不活跃**状态。虽然核心功能完整且可正常工作，但建议在使用前确认是否有已知限制（例如缺少官方示例、部分 API 可能不稳定等）。如果项目需要长期依赖此插件，建议关注后续 Epic 是否计划更新（如 UE 5.8 可能包含改进）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档](https://dev.epicgames.com/documentation/en-US/unreal-engine/learning-agents-in-unreal-engine)（尚不完善，推荐参考源码注释）
- [训练模块文档](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents/Source/LearningAgentsTraining)