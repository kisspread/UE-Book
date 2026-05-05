# Learning Core

> Learning Core is a machine learning library for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（机器学习代码资产） |
| 模块 | `Learning` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningCore) | |

## 用途

LearningCore 是一个面向 Unreal Engine 的机器学习（ML）基础库。它解决了在游戏引擎中集成和运行机器学习模型的核心问题，为开发者提供了一套 C++ 框架，用于定义、训练和推理神经网络模型。其主要目的是让游戏开发者能够利用机器学习技术来增强游戏玩法、优化性能或创建更智能的 AI 行为，而无需依赖外部复杂的 ML 框架。

## 使用场景

-   你需要为游戏中的 NPC 或角色创建基于学习的、更自然或更复杂的决策行为。
-   你希望使用强化学习（RL）来训练游戏 AI 代理（Agent）在特定环境中学习策略。
-   你需要一个轻量级的、可嵌入游戏运行时的神经网络推理引擎，用于实时预测或分类。
-   你想在 Unreal Engine 内部完成从数据收集、模型定义到训练和部署的完整 ML 工作流。

## 蓝图用法

该插件主要面向 C++ 开发者，提供底层的机器学习基础设施。其核心功能（如网络定义、训练循环）通常通过 C++ API 暴露。蓝图中可能包含一些用于触发训练、加载模型或进行简单推理的高级节点，但具体可用性取决于各子模块的实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （待补充） | （待补充） | （待补充） |

*注：详细的蓝图节点列表请参考各子模块文档。*

## C++ 用法

### 头文件引入

```cpp
#include "Learning/Learning.h"
#include "LearningTraining/LearningTraining.h"
```

### 基本用法

该插件的核心是定义和操作神经网络。以下是一个概念性的用法示例，展示了如何使用 `Learning` 模块定义一个简单的网络。

```cpp
// 概念示例，具体 API 请参考模块文档
#include "Learning/Learning.h"

// 1. 定义一个神经网络结构
FLearningNetworkDefinition NetworkDef;
// ... 配置网络层、激活函数等 ...

// 2. 创建网络实例
FLearningNetwork Network = FLearningNetwork::Create(NetworkDef);

// 3. 准备输入数据
TArray<float> InputData = {1.0f, 2.0f, 3.0f};

// 4. 执行前向推理
TArray<float> OutputData;
Network.Forward(InputData, OutputData);

// 5. 处理输出结果
// ...
```

### 进阶用法

结合 `LearningTraining` 模块，可以实现完整的训练流程。

```cpp
// 概念示例，具体 API 请参考模块文档
#include "Learning/Learning.h"
#include "LearningTraining/LearningTraining.h"

// 1. 定义网络和损失函数
FLearningNetworkDefinition NetworkDef;
// ...
FLearningLossFunction LossFunc = /* ... */;

// 2. 创建训练器
FLearningTrainer Trainer(NetworkDef, LossFunc);

// 3. 准备训练数据集
FLearningDataSet TrainingData = /* ... */;

// 4. 执行训练循环
for (int32 Epoch = 0; Epoch < 100; ++Epoch)
{
    Trainer.TrainEpoch(TrainingData);
    // 可选：评估、保存模型等
}

// 5. 获取训练好的网络用于推理
FLearningNetwork TrainedNetwork = Trainer.GetNetwork();
```

## Demo 示例

一个完整的、可编译的最小示例需要包含网络定义、训练和推理。由于这是一个基础库，示例通常较为复杂。建议参考引擎测试用例或官方示例项目。

```cpp
// LearningCoreDemo.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LearningCoreDemo.generated.h"

UCLASS()
class ALearningCoreDemo : public AActor
{
    GENERATED_BODY()
public:
    ALearningCoreDemo();
    virtual void BeginPlay() override;

private:
    // 用于存储网络和训练器的成员变量
    // FLearningNetwork Network;
    // FLearningTrainer Trainer;
};
```

```cpp
// LearningCoreDemo.cpp
#include "LearningCoreDemo.h"
#include "Learning/Learning.h"
#include "LearningTraining/LearningTraining.h"

ALearningCoreDemo::ALearningCoreDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ALearningCoreDemo::BeginPlay()
{
    Super::BeginPlay();

    // 在此处初始化网络、加载数据、开始训练或执行推理
    // 具体代码取决于您的ML任务
    UE_LOG(LogTemp, Log, TEXT("LearningCoreDemo: BeginPlay - ML workflow would start here."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Learning` | 提供核心的神经网络定义、数据结构和基础推理功能。 |
| `LearningTraining` | 提供模型训练、优化器、损失函数等训练相关的功能。 |

*注：该插件可能还依赖标准的 UE 模块（如 Core, CoreUObject, Engine），但这些是通用依赖，无需特别说明。*

## 维护状态

### 近期更新

- 2026-04-24 `553c9043` [LearningAgents] Pass NNECpuPath to python directly
- 2026-04-24 `e424031e` [LearningAgents] Fix python site-package paths on Linux and Mac
- 2026-04-21 `34a398cd` LearningCore: Added tolerance to FindTime and ContainsTime functions.
- 2026-04-16 `ec5e1d55` LearningCore: Added binary search optimization for find on frames and frame ranges indices.
- 2026-04-14 `25720c8e` LearningCore: Added Sparse and NamedSparse observations

### 维护评价

-   **创建时间**：2026年4月，是一个非常新的插件。
-   **维护状态**：**活跃开发中**。从提交记录看，插件处于早期但积极的开发阶段。
-   **实验性**：插件标记为 `IsExperimentalVersion: true` 且默认未启用，表明其 API 和功能可能不稳定，未来可能发生重大变更。
-   **推荐使用**：适合对机器学习有浓厚兴趣并愿意跟进最新实验性功能的开发者。不建议用于需要长期稳定支持的生产项目。建议密切关注其更新日志和 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningCore)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/LearningCore)