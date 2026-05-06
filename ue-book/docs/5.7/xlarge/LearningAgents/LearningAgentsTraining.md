# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习智能体训练 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资源、训练场景模板、示例记录数据） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约0年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 插件提供了一套完整的机器学习（强化学习与模仿学习）框架，用于在 Unreal Engine 中训练和控制 AI 角色。它抽象了底层训练管道的复杂细节，通过蓝图可读的接口让开发者无需编写 Python/C++ 训练代码即可实现智能体行为的端到端训练。

**解决的问题：**
- 传统行为树或状态机难以手工设计复杂、涌现式的行为（如平衡、追逐、群体协作）
- 将游戏内的观察空间（位置、速度、射线等）和动作空间（移动、转向、技能等）映射到神经网络输入输出需要繁琐的数据管道
- 训练过程中需处理并行训环境（Gym）、回合重置、奖励/完成信号、记录与回放等基础设施

## 使用场景

- **角色控制器训练**：训练一个角色学会奔跑、跳跃、攀爬、闪避等运动技能，并泛化到不同地形
- **非玩家角色（NPC）行为**：训练 NPC 执行巡逻、追捕、掩护等任务，使其行为更自然且适应环境变化
- **群体行为模拟**：同时训练多个智能体，习得合作或竞争策略（如足球、群聚）
- **模仿学习**：通过录制人类或现有 AI 的操作演示，让智能体在短时间内模仿复杂行为

## 蓝图用法

以下节点基于本模块（LearningAgentsTraining）的公开 API 提取，按功能分组。

### 环境训练（Gym）管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Start` | 根据 `GymTemplates` 配置生成并初始化多个 Gym 实例 | `ALearningAgentsGymsManager` |
| `Initialize` | 初始化单个 Gym（调用 `OnGymInitialized` 事件） | `ALearningAgentsGymBase` |
| `Reset` | 重置 Gym 内的所有学习组件，开始新回合 | `ALearningAgentsGymBase` |
| `GetRandomStream` | 获取 Gym 当前使用的随机流，用于一致性随机生成 | `ALearningAgentsGymBase` |
| `GenerateRandomLocationInGym` | 返回 Gym 范围内的随机有效位置（需在子类重写） | `ALearningAgentsGymBase` |
| `GenerateRandomRotationInGym` | 返回 Gym 范围内的随机旋转 | `ALearningAgentsGymBase` |
| `ProjectPointToGym` | 将一个点投影到 Gym 有效区域内 | `ALearningAgentsGymBase` |
| `SpawnEntitiesAtRandomLocations` | 在 Gym 中随机位置生成指定类型的实体（使用对象池） | `ULearningAgentsEntitiesManagerComponent` |
| `SpawnEntityAtProjectedLocation` | 在投影后的位置生成单个实体 | `ULearningAgentsEntitiesManagerComponent` |
| `SpawnEntities` | 在指定变换处批量生成实体 | `ULearningAgentsEntitiesManagerComponent` |

### 奖励（Reward）设计

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeReward` | 根据原始浮点值创建奖励（可缩放） | `ULearningAgentsRewards` |
| `MakeRewardOnCondition` | 条件满足时返回 RewardScale，否则 0 | `ULearningAgentsRewards` |
| `MakeRewardFromLocationDifference` | 基于两个位置之间的距离产生奖励（距离越大奖励越大） | `ULearningAgentsRewards` |
| `MakeRewardOnDistanceBelowThreshold` | 距离低于阈值时产生奖励 | `ULearningAgentsRewards` |
| `MakeRewardOnDistanceAboveThreshold` | 距离高于阈值时产生奖励 | `ULearningAgentsRewards` |

所有奖励函数均支持 `Tag` 调试标签和可视化日志记录（需传入 `VisualLoggerListener`）。

### 完成（Completion）信号

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsCompletionRunning` | 判断完成标志是否为运行中 | `ULearningAgentsCompletions` |
| `IsCompletionCompleted` | 判断是否已完成（截断或终止） | `ULearningAgentsCompletions` |
| `IsCompletionTruncation` | 判断是否被截断（中断但未失败） | `ULearningAgentsCompletions` |
| `IsCompletionTermination` | 判断是否终止（成功/失败，后续步奖励为0） | `ULearningAgentsCompletions` |
| `CompletionOr` / `CompletionAnd` / `CompletionNot` | 组合多个完成信号 | `ULearningAgentsCompletions` |
| `MakeCompletion` | 根据类型创建完成信号，可附加调试标签 | `ULearningAgentsCompletions` |
| `MakeCompletionOnCondition` | 条件成立时创建完成信号 | `ULearningAgentsCompletions` |

### 训练器设置与启动

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupRecorder` | 初始化录制组件，用于收集模仿学习训练数据 | `ULearningAgentsRecorder` |
| `MakeRecorder` | 静态构造并初始化录制器 | `ULearningAgentsRecorder` |
| `StartRecording` / `StopRecording` | 开始/停止录制当前回合的观察和动作数据 | `ULearningAgentsRecorder` |
| `SetupTrainingEnvironment` | 设置训练环境（继承 `ULearningAgentsTrainingEnvironment`） | `ULearningAgentsTrainingEnvironment` |
| `GatherAgentReward` | 由训练环境重写，返回单个智能体当前帧的奖励值 | `ULearningAgentsTrainingEnvironment` |
| `GatherAgentCompletion` | 由训练环境重写，返回单个智能体的完成信号 | `ULearningAgentsTrainingEnvironment` |
| `InitializeLearningComponent` | 初始化由 `ULearningAgentsEntitiesManagerComponent` 管理的组件 | `ILearningAgentsLearningComponentInterface` |
| `ResetLearningComponent` | 重置管理组件的状态用于新回合 | `ILearningAgentsLearningComponentInterface` |

### 实体接口

| 节点 | 说明 | 所在类 |
|---|---|---|
| `InitializeEntity` | 在训练开始时初始化实体（如附着到 Gym） | `ILearningAgentsEntityTrainingInterface` |
| `ResetEntity` | 重置实体状态以开始新回合 | `ILearningAgentsEntityTrainingInterface` |
| `EnableEntity` / `DisableEntity` | 启用/禁用实体参与训练 | `ILearningAgentsEntityInterface` |
| `IsEntityEnabled` | 返回该实体当前是否启用 | `ILearningAgentsEntityInterface` |

### 调试与记录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ResetRecording` | 清空记录资产中所有数据 | `ULearningAgentsRecording` |
| `AppendRecordingFromFile` | 从文件追加记录到现有资产 | `ULearningAgentsRecording` |
| `SaveToFile` | 将记录资产保存到磁盘 | `ULearningAgentsRecording` |

### 蓝图使用示例

典型训练循环蓝图逻辑：
1. 在 Level 中放置 `ALearningAgentsGymsManager`，设置 `GymTemplates` 数组（指定 Gym 类与数量）
2. 调用 `Start` 生成 Gym 实例 → 各 Gym 触发 `OnGymInitialized` 事件
3. 在每个 `GymBase` 的 `BeginPlay` 或事件中，使用 `SpawnEntitiesAtRandomLocations` 产生训练用 Actor
4. 每帧（通过 `OnAgentsManagerTick`）为每个智能体收集观察并执行动作（由底层 `ULearningAgentsInteractor` 处理）
5. 在 `ULearningAgentsTrainingEnvironment` 的蓝图子类中重写 `GatherAgentReward` 和 `GatherAgentCompletion`，使用上述奖励和完成节点
6. 训练器（如 PPO 或 Imitation）自动收集数据并迭代更新网络，通过 `ULearningAgentsPPOTrainer` / `ULearningAgentsImitationTrainer` 配置

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsTraining.h"
#include "LearningAgentsEntitiesManagerComponent.h"
#include "LearningAgentsGym.h"
#include "LearningAgentsTrainingEnvironment.h"
#include "LearningAgentsRewards.h"
#include "LearningAgentsCompletions.h"
```

### 基本用法

#### 创建 Gym 并生成实体（来源：`LearningAgentsEntitiesManagerComponent.h`）

```cpp
// 假设已在 Actor 中挂载 ULearningAgentsEntitiesManagerComponent
ULearningAgentsEntitiesManagerComponent* EntitiesManager = FindComponentByClass<ULearningAgentsEntitiesManagerComponent>();
if (EntitiesManager)
{
    // 初始化所有管理实体
    EntitiesManager->InitializeLearningComponent();

    // 随机生成 5 个 AMyAgentActor 类型的实体
    TSubclassOf<AActor> AgentClass = AMyAgentActor::StaticClass();
    const float ZOffset = 100.0f;
    const int32 SpawnCount = 5;
    TScriptInterface<ILearningAgentsEntityInterface> Spawned = EntitiesManager->SpawnEntitiesAtRandomLocations(AgentClass, ZOffset, SpawnCount);
}
```

#### 实现训练环境（来源：`LearningAgentsTrainingEnvironment.h`）

```cpp
UCLASS(Blueprintable)
class UMyTrainingEnvironment : public ULearningAgentsTrainingEnvironment
{
    GENERATED_BODY()

public:
    // 必须实现：返回单个智能体的奖励
    virtual void GatherAgentReward_Implementation(float& OutReward, const int32 AgentId) override
    {
        OutReward = 0.0f;
        AActor* Agent = Cast<AActor>(GetManager()->GetAgent(AgentId));
        if (Agent)
        {
            // 例如：距离目标越近奖励越大
            const float Dist = FVector::Dist(Agent->GetActorLocation(), TargetLocation);
            OutReward = ULearningAgentsRewards::MakeRewardFromLocationDifference(
                Agent->GetActorLocation(), TargetLocation, 100.0f, -1.0f);
        }
    }

    // 必须实现：返回完成信号
    virtual void GatherAgentCompletion_Implementation(ELearningAgentsCompletion& OutCompletion, const int32 AgentId) override
    {
        AActor* Agent = Cast<AActor>(GetManager()->GetAgent(AgentId));
        if (Agent && FVector::Dist(Agent->GetActorLocation(), TargetLocation) < ReachThreshold)
        {
            OutCompletion = ELearningAgentsCompletion::Termination;
        }
        else
        {
            OutCompletion = ELearningAgentsCompletion::Running;
        }
    }

private:
    FVector TargetLocation = FVector(1000.0f, 0.0f, 0.0f);
    float ReachThreshold = 100.0f;
};
```

#### 使用录制器（来源：`LearningAgentsRecorder.h`）

```cpp
ULearningAgentsRecorder* Recorder = ULearningAgentsRecorder::MakeRecorder(
    Manager,
    Interactor,
    ULearningAgentsRecorder::StaticClass(),
    FName("MyRecorder"),
    FLearningAgentsRecorderPathSettings(),
    nullptr,
    true);
Recorder->StartRecording();
// ... 运行若干帧训练 ...
Recorder->StopRecording();
Recorder->SaveToFile("MyRecording");
```

### 进阶用法

#### 多 Gym 并行训练（来源：`LearningAgentsGymsManager.h`）

```cpp
// 在 Level 蓝图中创建 GymsManager 并配置
ALearningAgentsGymsManager* Manager = GetWorld()->SpawnActor<ALearningAgentsGymsManager>();
Manager->GymTemplates.Add({ AMyGymClass::StaticClass(), 4 }); // 生成 4 个 Gym
Manager->GymsSpacing = 500.0f;
Manager->Start();
int32 GymCount = Manager->GetGymsCount(); // 4
```

#### 自定义完成组合（来源：`LearningAgentsCompletions.h`）

```cpp
ELearningAgentsCompletion A = /* 用时超限 */;
ELearningAgentsCompletion B = /* 碰撞障碍物 */;
// 逻辑或：任一结束则结束
ELearningAgentsCompletion Combined = ULearningAgentsCompletions::CompletionOr(A, B);
// 逻辑与：两者均结束才结束
ELearningAgentsCompletion CombinedAnd = ULearningAgentsCompletions::CompletionAnd(A, B);
```

## Demo 示例

以下是一个最小可编译的 Actor 脚本，演示如何将训练环境与实体管理器连接：

```cpp
// MyTrainingActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LearningAgentsGym.h"
#include "LearningAgentsEntitiesManagerComponent.h"
#include "MyTrainingActor.generated.h"

UCLASS()
class AMyTrainingActor : public AActor
{
    GENERATED_BODY()

public:
    AMyTrainingActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(VisibleAnywhere, Category = "Learning")
    ULearningAgentsEntitiesManagerComponent* EntitiesManager;

    UPROPERTY(EditDefaultsOnly, Category = "Learning")
    TSubclassOf<AActor> AgentClass;
};

// MyTrainingActor.cpp
#include "MyTrainingActor.h"
#include "LearningAgentsRewards.h"
#include "LearningAgentsCompletions.h"

AMyTrainingActor::AMyTrainingActor()
{
    EntitiesManager = CreateDefaultSubobject<ULearningAgentsEntitiesManagerComponent>(TEXT("EntitiesManager"));
    PrimaryActorTick.bCanEverTick = true;
}

void AMyTrainingActor::BeginPlay()
{
    Super::BeginPlay();
    if (EntitiesManager && AgentClass)
    {
        FLearningAgentsEntityInfo Info;
        Info.EntityClass = AgentClass;
        Info.EpisodeEntitySpawnCountMin = 1;
        Info.EpisodeEntitySpawnCountMax = 1;
        EntitiesManager->Entities.Add(Info);
        EntitiesManager->InitializeLearningComponent();

        // 生成一个实体
        TScriptInterface<ILearningAgentsEntityInterface> Spawned = 
            EntitiesManager->SpawnEntitiesAtRandomLocations(AgentClass, 0.0f, 1);
    }
}
```

## 模块依赖

使用本模块（LearningAgentsTraining）时，你的模块的 `Build.cs` 需要添加以下依赖（省略通用依赖）：

| 模块 | 用途 |
|---|---|
| `Learning` | 底层神经网络接口、训练管道、缓冲区数据结构 |
| `LearningAgents` | 高层智能体交互、策略与评价网络封装 |
| `LearningAgentsReplay` | 回放与录制支持（可选） |
| `LearningTraining` | 通用训练基础设施（迭代器、日志） |
| `UnrealEd` | 编辑器相关功能（如录制文件保存对话框） |

```cpp
// YourModule.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "Learning",
    "LearningAgents",
    "LearningAgentsTraining",
    "LearningAgentsReplay",
    "LearningTraining"
});

// 如需编辑器功能（如 TrainingEditor）则额外添加
if (Target.bBuildEditor)
{
    PrivateDependencyModuleNames.Add("LearningAgentsTrainingEditor");
}
```

## 维护状态

### 近期更新

- 2025-09-23 e6f9d5f LearningAgentsRecording（录制功能更新）
- 2025-09-23 dcf8187 bug fix to conv1d conv2d serialization（卷积层序列化修复）
- 2025-09-23 86de7c7 Missing types in ComputeObservationSchemaSubsetIndices and bugfix（模式子集索引修复）
- 2025-09-23 1571e33 Ensure instead of check during GetAgent（将断言改为确保，提升稳定性）
- 2025-09-16 f485ef5 [LearningAgents] - schema subset bug fix

### 维护评价

- **创建时间短**：2025年9月16日，距今不足1个月。
- **更新频繁**：9月23日有连续4次提交，涵盖功能开发、Bug 修复和稳定性改进。
- **活跃程度**：项目处于积极开发初期，社区和 Epic 内部持续投入。
- **已知限制**：文档中提到 “beta” 已不存在（`IsBetaVersion=false`），但版本号仍为 0.2，暗示 API 可能尚未完全稳定。
- **推荐使用**：对于希望尝试现代强化学习集成到 UE 的开发者，这是一个极有前景的工具。建议关注后续版本更新和示例内容，当前适用于原型验证和实验性项目。

## 相关链接

- [源码（插件根目录）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]（暂无独立文档链接，可参考 UE 文档站未来更新）
- [测试用例]（测试位于 `Engine/Plugins/Experimental/LearningAgents/Source/LearningAgentsTraining/Private/Tests/`，但尚未公开）