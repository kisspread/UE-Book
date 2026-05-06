# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习代理 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑工具） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

`LearningAgentsTrainingEditor` 模块提供了在 Unreal Editor 中直接运行和管理模仿学习训练流程的编辑器扩展工具。它封装了底层 `LearningAgentsImitationTrainer`，允许开发者通过蓝图和编辑器细节面板快速配置训练参数、启动/停止训练，并支持创建文件类型的通信器以导出训练数据用于外部训练。同时，该模块还包含深度图可视化组件，用于在训练过程中实时查看角色的深度感知数据，辅助调试和监控。

该模块的存在意义在于：
- **降低训练集成门槛**：无需编写 C++ 代码即可在蓝图中设置训练流程。
- **提高迭代效率**：直接在编辑器中启动训练，实时观察结果，无需外部启动程序。
- **可视化支持**：提供深度图小部件，帮助理解智能体感知状态。

## 使用场景

- 你在开发需要模仿学习（Imitation Learning）的 AI 角色（例如训练 NPC 模仿玩家动作）。
- 你希望在编辑器中直接配置训练参数，并通过蓝图编排训练循环。
- 你需要可视化智能体的深度传感器（如相机）数据，以检查输入质量。

## 蓝图用法

### 核心 Actor：模仿学习训练器编辑器

该类 `ALearningAgentsImitationTrainerEditor` 是主要的编辑器和可放置 Actor，包含了训练流程的所有控制节点。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetupTraining`（ImplementableEvent） | 在蓝图中实现训练初始化逻辑（如创建管理器、记录器、训练器） | `ALearningAgentsImitationTrainerEditor` |
| `StartTraining` | 开始训练循环 | 同上 |
| `StopTraining` | 停止正在运行的训练 | 同上 |
| `MakeFileCommunicator` | 创建文件型通信器，将训练数据保存到指定目录供外部使用 | 同上 |

**属性 (BlueprintReadWrite)**：
- `LearningAgentsManager` – 智能体管理器引用
- `LearningAgentsImitationTrainer` – 训练器组件
- `Recording` – 录制组件
- `ImitationTrainerSettings` – 训练设置结构体
- `ImitationTrainerTrainingSettings` – 训练过程设置
- `ImitationTrainerPathSettings` – 通信器路径设置

### 深度图可视化组件

`ULearningAgentsDepthMapVisualizerComponent` 提供了一个可放置在 Actor 上的组件，用于在屏幕指定位置渲染深度图。

| 属性 (BlueprintReadWrite) | 说明 |
|---|---|
| `RenderSize` | 渲染目标在屏幕上的大小（像素） |
| `RenderPosition` | 渲染目标在屏幕上的位置 |

### 蓝图使用示例

1. 在关卡中放置一个 `ALearningAgentsImitationTrainerEditor`。
2. 在 `Event BeginPlay` 中调用 `SetupTraining` 事件，并在该事件蓝图中设置 `LearningAgentsManager`、`Recording` 和 `LearningAgentsImitationTrainer` 等引用（通过获取或创建组件）。
3. 调用 `StartTraining` 开始训练，调用 `StopTraining` 停止。
4. 若要导出训练数据，调用 `MakeFileCommunicator` 并指定输出目录。
5. 要显示深度图，将 `ULearningAgentsDepthMapVisualizerComponent` 添加到角色或 Pawn 中，设置 `RenderSize` 和 `RenderPosition`。

## C++ 用法

### 头文件引入

```cpp
#include "LearningAgentsImitationTrainerEditor.h"
#include "LearningAgentsDepthMapVisualizer.h"
```

### 基本用法

以下示例展示了如何在 C++ 中创建训练器 Actor 并启动训练（假设已在世界中有实例）。

**文件**: `Engine/Plugins/Experimental/LearningAgents/Source/LearningAgentsTrainingEditor/...`

```cpp
// 获取或生成训练器
A学习AgentsImitationTrainerEditor* Trainer = ...
Trainer->LearningAgentsManager = CreateManager();
Trainer->Recording = CreateRecording();
Trainer->LearningAgentsImitationTrainer = NewObject<ULearningAgentsImitationTrainer>(Trainer);

// 启动训练
Trainer->StartTraining();
```

**文件**: `Engine/Plugins/Experimental/LearningAgents/Source/LearningAgentsTrainingEditor/Public/LearningAgentsImitationTrainerEditor.h`

### 创建文件通信器

```cpp
FDirectoryPath Path;
Path.Path = TEXT("Intermediate/MyTrainingData");
FLearningAgentsCommunicator Communicator = Trainer->MakeFileCommunicator(Path);
// Communicator 可用于写入训练样本
```

## Demo 示例

以下是一个最小示例，展示如何在游戏模式中放置训练器并启动训练。

**DemoImitationTrainer.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LearningAgentsImitationTrainerEditor.h"
#include "DemoImitationTrainer.generated.h"

UCLASS()
class ADemoImitationTrainer : public AActor
{
    GENERATED_BODY()

public:
    ADemoImitationTrainer();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demo")
    TObjectPtr<ALearningAgentsImitationTrainerEditor> TrainerActor;

    UFUNCTION()
    void OnTrainingStarted();
};
```

**DemoImitationTrainer.cpp**

```cpp
#include "DemoImitationTrainer.h"
#include "LearningAgentsManager.h"
#include "LearningAgentsImitationTrainer.h"
#include "LearningAgentsRecording.h"

ADemoImitationTrainer::ADemoImitationTrainer()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADemoImitationTrainer::BeginPlay()
{
    Super::BeginPlay();

    if (TrainerActor)
    {
        // 设置必要组件（实际应通过蓝图调用来完成更复杂的设置）
        TrainerActor->LearningAgentsManager = NewObject<ULearningAgentsManager>(TrainerActor);
        TrainerActor->Recording = NewObject<ULearningAgentsRecording>(TrainerActor);
        TrainerActor->LearningAgentsImitationTrainer = NewObject<ULearningAgentsImitationTrainer>(TrainerActor);
        
        // 启动训练
        TrainerActor->StartTraining();
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等编辑器公共模块）。

## 维护状态

### 近期更新

- 2025-09-23 e6f9d5f — [LearningAgents] LearningAgentsRecording
- 2025-09-23 dcf81878 — [LearningAgents] bug fix to conv1d conv2d serialization
- 2025-09-23 86de7c71 — [LearningAgents] Missing types in ComputeObservationSchemaSubsetIndices and bugfix
- 2025-09-23 1571e33e — LearningAgents: Ensure instead of check during GetAgent
- 2025-09-16 f485ef53 — [LearningAgents] - schema subset bug fix

### 维护评价

该模块随 Learning Agents 插件一同在 2025 年 9 月首次出现，近期（2025-09-23）仍有多次功能性更新和 bug 修复，说明团队正在积极开发和维护。由于插件非常新（约 0 年），当前没有已知重大限制。推荐在需要模仿学习的项目中使用，但需注意它处于早期阶段（版本 0.2），API 可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档]（暂无）
- [测试用例]（暂无公开测试）