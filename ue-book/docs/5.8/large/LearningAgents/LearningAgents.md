# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、示例地图） |
| 模块 | `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2023-03-30 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 是 UE5 内置的机器学习框架，用于让游戏中的 AI 角色通过**强化学习**或**模仿学习**自主学会控制行为。

传统游戏 AI 依赖行为树或状态机手写规则，而 Learning Agents 让你定义"观察什么"（Observation）和"执行什么动作"（Action），然后通过神经网络策略自动学习从观察到动作的映射。它解决的核心问题是：**不需要手写 AI 逻辑，让角色自己学习最优行为**。

框架提供完整的 ML 管线：
- **Interactor** 定义观察/动作的结构（输入输出接口）
- **Policy** 神经网络策略（将观察映射为动作）
- **Critic** 价值网络（估计未来回报，用于训练）
- **Controller** 手工策略（用于收集模仿学习的示范数据）
- **FlowMatching** 流匹配模型（替代标准策略的生成式方法）

## 使用场景

- 你在做一个赛车游戏 → 让 AI 赛车通过强化学习学会最优驾驶路径
- 你在做一个格斗游戏 → 通过收集人类玩家的示范数据，用模仿学习训练 AI 对手
- 你需要大量同类型 NPC 自主巡逻 → 用 Learning Agents 训练一个通用策略，批量应用到所有 NPC
- 你在做一个物理模拟角色运动 → 让角色通过试错学习行走、跳跃等运动技能
- 你需要可微分的深度观测（如深度图）作为输入 → 使用 `ULearningAgentsDepthMapComponent`

## 蓝图用法

### 核心节点

#### 管理器（Manager）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddAgent` | 将一个 UObject 添加为智能体，返回分配的 ID | `ULearningAgentsManager` |
| `RemoveAgent` | 通过 ID 移除一个智能体 | `ULearningAgentsManager` |
| `ResetAgent` | 重置智能体的所有内部状态 | `ULearningAgentsManager` |
| `GetAgent` | 通过 ID 获取智能体对象 | `ULearningAgentsManager` |
| `GetAllAgents` | 获取所有已注册的智能体 | `ULearningAgentsManager` |
| `SetMaxAgentNum` | 设置最大智能体数量（预分配内存） | `ULearningAgentsManager` |

#### 交互器（Interactor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeInteractor` | 创建并初始化一个交互器 | `ULearningAgentsInteractor` |
| `GatherObservations` | 为所有智能体收集观察数据 | `ULearningAgentsInteractor` |
| `MakeActionModifiers` | 为所有智能体创建动作修正器 | `ULearningAgentsInteractor` |
| `PerformActions` | 执行所有智能体的动作 | `ULearningAgentsInteractor` |

#### 策略（Policy）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakePolicy` | 创建策略网络（编码器+策略+解码器） | `ULearningAgentsPolicy` |
| `RunInference` | 一键执行完整推理：收集观察→编码→策略→解码→执行 | `ULearningAgentsPolicy` |
| `EncodeObservations` | 用编码器网络编码观察向量 | `ULearningAgentsPolicy` |
| `EvaluatePolicy` | 运行策略网络生成编码动作 | `ULearningAgentsPolicy` |
| `DecodeAndSampleActions` | 解码并采样动作向量 | `ULearningAgentsPolicy` |

#### 控制器（Controller）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeController` | 创建手工控制器 | `ULearningAgentsController` |
| `EvaluateController` | 执行控制器逻辑生成动作 | `ULearningAgentsController` |
| `RunController` | 一键执行：收集观察→控制器→执行 | `ULearningAgentsController` |

#### 观察与动作定义

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SpecifyContinuousObservation` | 定义连续浮点观察 | `ULearningAgentsObservations` |
| `SpecifyLocationObservation` | 定义位置观察（自动归一化） | `ULearningAgentsObservations` |
| `SpecifyVelocityObservation` | 定义速度观察 | `ULearningAgentsObservations` |
| `SpecifyRotationObservation` | 定义旋转观察 | `ULearningAgentsObservations` |
| `SpecifyContinuousAction` | 定义连续浮点动作 | `ULearningAgentsActions` |
| `SpecifyLocationAction` | 定义位置动作 | `ULearningAgentsActions` |
| `SpecifyVelocityAction` | 定义速度动作 | `ULearningAgentsActions` |
| `SpecifyDirectionAction` | 定义方向动作 | `ULearningAgentsActions` |
| `SpecifyAngleAction` | 定义角度动作 | `ULearningAgentsActions` |

### 使用示例（蓝图描述）

**基本推理流程**（每帧执行）：

1. **BeginPlay** 阶段初始化：
   - 添加组件 `ULearningAgentsManager`，设置 `MaxAgentNum`
   - 调用 `AddAgent` 注册你的角色对象
   - 调用 `MakeInteractor` 创建交互器（传入 Manager 引用）
   - 调用 `MakePolicy` 创建策略（传入 Manager 和 Interactor 引用）
   - 加载预训练的 `ULearningAgentsNeuralNetwork` 资产到 Policy

2. **Tick** 阶段执行推理：
   - 调用 `Policy.RunInference()` — 内部自动完成：`GatherObservations` → `EncodeObservations` → `EvaluatePolicy` → `DecodeAndSampleActions` → `PerformActions`

3. **实现 Interactor 的回调**（蓝图中重写事件）：
   - `SpecifyAgentObservation`：用 `SpecifyLocationObservation`、`SpecifyVelocityObservation` 等构建观察结构
   - `GatherAgentObservation`：用 `MakeLocationObservation`、`MakeVelocityObservation` 等填入实际数据
   - `SpecifyAgentAction`：用 `SpecifyLocationAction`、`SpecifyVelocityAction` 等定义动作结构
   - `PerformAgentAction`：用 `GetLocationAction`、`GetVelocityAction` 等获取动作值并应用到角色

**使用 Controller 收集示范数据**：

1. 创建 Controller 子类，重写 `EvaluateAgentController` 回调
2. 在回调中用 `MakeLocationAction`、`MakeDirectionAction` 等根据观察构造动作
3. 调用 `RunController` 运行完整收集循环
4. 收集的观察-动作对可用于后续模仿学习训练

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsManager.h"
#include "LearningAgentsInteractor.h"
#include "LearningAgentsPolicy.h"
#include "LearningAgentsObservations.h"
#include "LearningAgentsActions.h"
#include "LearningAgentsController.h"
```

### 基本用法

基于源码中的接口设计，典型的 C++ 用法如下：

```cpp
// 1. 创建 Manager（通常作为 ActorComponent 使用）
ULearningAgentsManager* Manager = NewObject<ULearningAgentsManager>(MyActor);
Manager->SetMaxAgentNum(64);

// 2. 添加智能体
int32 AgentId = Manager->AddAgent(MyCharacterActor);

// 3. 创建 Interactor 子类
UCLASS()
class UMyInteractor : public ULearningAgentsInteractor
{
    GENERATED_BODY()

    virtual void SpecifyAgentObservation_Implementation(
        FLearningAgentsObservationSchemaElement& OutElement,
        ULearningAgentsObservationSchema* Schema) override
    {
        // 定义观察结构：位置 + 速度
        TMap<FName, FLearningAgentsObservationSchemaElement> Elements;
        Elements.Add("Location", ULearningAgentsObservations::SpecifyLocationObservation(Schema));
        Elements.Add("Velocity", ULearningAgentsObservations::SpecifyVelocityObservation(Schema));
        OutElement = ULearningAgentsObservations::SpecifyStructObservation(Schema, Elements);
    }

    virtual void GatherAgentObservation_Implementation(
        FLearningAgentsObservationObjectElement& OutElement,
        ULearningAgentsObservationObject* Object,
        const int32 AgentId) override
    {
        ACharacter* Character = Cast<ACharacter>(GetAgent(AgentId));
        TMap<FName, FLearningAgentsObservationObjectElement> Elements;
        Elements.Add("Location", ULearningAgentsObservations::MakeLocationObservation(
            Object, Character->GetActorLocation()));
        Elements.Add("Velocity", ULearningAgentsObservations::MakeVelocityObservation(
            Object, Character->GetVelocity()));
        ULearningAgentsObservations::MakeStructObservation(Object, OutElement, Elements);
    }

    virtual void SpecifyAgentAction_Implementation(
        FLearningAgentsActionSchemaElement& OutElement,
        ULearningAgentsActionSchema* Schema) override
    {
        OutElement = ULearningAgentsActions::SpecifyDirectionAction(Schema);
    }

    virtual void PerformAgentAction_Implementation(
        const ULearningAgentsActionObject* Object,
        const FLearningAgentsActionObjectElement& Element,
        const int32 AgentId) override
    {
        FVector Direction;
        ULearningAgentsActions::GetDirectionAction(Direction, Object, Element);
        ACharacter* Character = Cast<ACharacter>(GetAgent(AgentId));
        Character->AddMovementInput(Direction);
    }
};
```

### 进阶用法

**使用 Policy 进行推理**：

```cpp
// 在 Tick 中执行完整推理
void AMyAICharacter::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 一键推理
    Policy->RunInference(ActionNoiseScale);

    // 或者分步执行以获得更多控制
    // Interactor->GatherObservations();
    // Policy->EncodeObservations();
    // Policy->EvaluatePolicy();
    // Interactor->MakeActionModifiers();
    // Policy->DecodeAndSampleActions(ActionNoiseScale);
    // Interactor->PerformActions();
}
```

**使用 Controller 收集示范数据**：

```cpp
UCLASS()
class UMyController : public ULearningAgentsController
{
    GENERATED_BODY()

    virtual void EvaluateAgentController_Implementation(
        FLearningAgentsActionObjectElement& OutElement,
        ULearningAgentsActionObject* ActionObject,
        const ULearningAgentsObservationObject* ObsObject,
        const FLearningAgentsObservationObjectElement& ObsElement,
        const int32 AgentId) override
    {
        // 用传统 AI 逻辑或人类输入生成动作
        ACharacter* Character = Cast<ACharacter>(GetAgent(AgentId));
        FVector TargetDirection = (TargetLocation - Character->GetActorLocation()).GetSafeNormal();
        OutElement = ULearningAgentsActions::MakeDirectionAction(ActionObject, TargetDirection);
    }
};

// 运行控制器收集数据
Controller->RunController();
```

## Demo 示例

一个最小可编译的自定义交互器示例：

```cpp
// MyLearningInteractor.h
#pragma once
#include "LearningAgentsInteractor.h"
#include "MyLearningInteractor.generated.h"

UCLASS()
class MYGAME_API UMyLearningInteractor : public ULearningAgentsInteractor
{
    GENERATED_BODY()

public:
    virtual void SpecifyAgentObservation_Implementation(
        FLearningAgentsObservationSchemaElement& OutElement,
        ULearningAgentsObservationSchema* Schema) override;
    
    virtual void GatherAgentObservation_Implementation(
        FLearningAgentsObservationObjectElement& OutElement,
        ULearningAgentsObservationObject* Object,
        const int32 AgentId) override;
    
    virtual void SpecifyAgentAction_Implementation(
        FLearningAgentsActionSchemaElement& OutElement,
        ULearningAgentsActionSchema* Schema) override;
    
    virtual void PerformAgentAction_Implementation(
        const ULearningAgentsActionObject* Object,
        const FLearningAgentsActionObjectElement& Element,
        const int32 AgentId) override;
};
```

```cpp
// MyLearningInteractor.cpp
#include "MyLearningInteractor.h"
#include "LearningAgentsObservations.h"
#include "LearningAgentsActions.h"

void UMyLearningInteractor::SpecifyAgentObservation_Implementation(
    FLearningAgentsObservationSchemaElement& OutElement,
    ULearningAgentsObservationSchema* Schema)
{
    TMap<FName, FLearningAgentsObservationSchemaElement> Elements;
    Elements.Add("Location", ULearningAgentsObservations::SpecifyLocationObservation(Schema));
    Elements.Add("Rotation", ULearningAgentsObservations::SpecifyRotationObservation(Schema));
    Elements.Add("Velocity", ULearningAgentsObservations::SpecifyVelocityObservation(Schema));
    OutElement = ULearningAgentsObservations::SpecifyStructObservation(Schema, Elements);
}

void UMyLearningInteractor::GatherAgentObservation_Implementation(
    FLearningAgentsObservationObjectElement& OutElement,
    ULearningAgentsObservationObject* Object,
    const int32 AgentId)
{
    AActor* Agent = Cast<AActor>(GetAgent(AgentId));
    if (!Agent) return;

    TMap<FName, FLearningAgentsObservationObjectElement> Elements;
    Elements.Add("Location", ULearningAgentsObservations::MakeLocationObservation(
        Object, Agent->GetActorLocation(), Agent->GetActorTransform()));
    Elements.Add("Rotation", ULearningAgentsObservations::MakeRotationObservation(
        Object, Agent->GetActorRotation()));
    Elements.Add("Velocity", ULearningAgentsObservations::MakeVelocityObservation(
        Object, Agent->GetVelocity(), Agent->GetActorTransform()));
    ULearningAgentsObservations::MakeStructObservation(Object, OutElement, Elements);
}

void UMyLearningInteractor::SpecifyAgentAction_Implementation(
    FLearningAgentsActionSchemaElement& OutElement,
    ULearningAgentsActionSchema* Schema)
{
    TMap<FName, FLearningAgentsActionSchemaElement> Elements;
    Elements.Add("MoveDirection", ULearningAgentsActions::SpecifyDirectionAction(Schema));
    Elements.Add("ShouldJump", ULearningAgentsActions::SpecifyExclusiveDiscreteAction(Schema, 2));
    OutElement = ULearningAgentsActions::SpecifyStructAction(Schema, Elements);
}

void UMyLearningInteractor::PerformAgentAction_Implementation(
    const ULearningAgentsActionObject* Object,
    const FLearningAgentsActionObjectElement& Element,
    const int32 AgentId)
{
    ACharacter* Character = Cast<ACharacter>(GetAgent(AgentId));
    if (!Character) return;

    // 获取结构化动作
    FLearningAgentsActionObjectElement DirElement, JumpElement;
    ULearningAgentsActions::GetStructAction(DirElement, Object, Element, TEXT("MoveDirection"));
    ULearningAgentsActions::GetStructAction(JumpElement, Object, Element, TEXT("ShouldJump"));

    FVector Direction;
    ULearningAgentsActions::GetDirectionAction(Direction, Object, DirElement,
        FTransform(), true, TEXT("MoveDirection"));
    Character->AddMovementInput(Direction);

    int32 JumpChoice;
    ULearningAgentsActions::GetExclusiveDiscreteAction(JumpChoice, Object, JumpElement,
        true, TEXT("ShouldJump"));
    if (JumpChoice == 1)
    {
        Character->Jump();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎，提供神经网络推理能力 |
| `LearningAgentsTraining` | 训练相关功能（依赖 UnrealEd，仅训练时需要） |
| `LearningAgentsTrainingEditor` | 训练编辑器集成 |
| `LearningAgentsReplay` | 回放录制功能，用于收集训练数据 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0b2b6629` | [LearningAgents] Fix interactor SetActionVector | 修复交互器 SetActionVector 函数的 bug |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化说明符的 32/64 位匹配问题 |
| 2026-04-24 | `553c9043` | [LearningAgents] Pass NNECpuPath to python directly | 将 NNE CPU 路径直接传递给 Python 训练脚本 |
| 2026-04-20 | `305f49dd` | [LearningAgents] Improve reinitialize recording behavior to reset and add new schema | 改进重新初始化录制时重置并添加新 schema 的行为 |
| 2026-04-14 | `898b7c7c` | [LACombat] Replay Runtime Recording | 添加战斗场景回放运行时录制功能 |

### 维护评价

Learning Agents 是 Epic Games 近期重点维护的实验性插件，处于**活跃维护**状态。

- **创建时间**：2023 年 3 月，约 3 年历史
- **更新频率**：近一个月有 5 次提交，包含 bug 修复和功能改进
- **模块规模**：75 个源文件，4 个模块，代码量较大且仍在增长
- **状态**：虽然标记为实验性（位于 `Experimental` 目录），但 `IsBetaVersion=false`，接口相对稳定
- **注意**：`EnabledByDefault=false`，需要手动在项目设置中启用

**推荐使用**：如果你的项目需要机器学习驱动的 AI 角色控制，这是 UE5 官方提供的唯一内置方案。虽然仍在 Experimental 目录下，但已有完整的强化学习和模仿学习管线，且持续有实质性更新。建议关注版本迁移时的 breaking changes。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]()（暂无公开文档链接）