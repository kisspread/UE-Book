# Learning Agents

> Learning Agents is a machine learning library for AI character control in games. It simplifies the use of reinforcement and imitation learning in Unreal.

| 属性 | 值 |
|---|---|
| 中文名 | 学习代理 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（训练配置文件、演示地图等资产） |
| 模块 | `Learning` (Runtime), `LearningAgents` (Runtime), `LearningAgentsReplay` (Runtime), `LearningAgentsTraining` (Runtime), `LearningAgentsTrainingEditor` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2025-09-16 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents) | |

## 用途

Learning Agents 是 Epic Games 为 Unreal Engine 提供的机器学习教育库，专注于简化强化学习和模仿学习在游戏 AI 中的应用。该插件提供：

- **核心算法**：包括 Adam、CMA-ES、PSO 等多种无梯度优化器，K-Means 聚类，PCA 降维等基础机器学习组件。
- **神经网络支持**：通过 UE 的 NNE 接口加载和运行 ONNX 模型，支持策略网络（Policy）和价值网络（Critic）的推理。
- **高效数据容器**：专为强化学习设计的多维数组 (`TMultiArray`)、帧集合 (`FFrameSet`/`FFrameRangeSet`) 和帧属性 (`FFrameAttribute`)，支持批处理和 SIMD 优化。
- **动作/观测模式**：提供连续、离散、命名离散、组合等多种动作和观测类型的 Schema 定义，便于模型输入输出描述。
- **优化规划器**：支持基于模型预测控制（MPC）思想的规划算法，结合优化器在线搜索最优行动序列。

该插件解决的核心问题是：**降低在 Unreal 中集成机器学习的门槛**，让游戏开发者无需深入底层算法细节即可为 AI 角色赋予学习和决策能力。它并非一个完整的训练框架，而是提供在游戏运行时或训练期间所需的基础计算模块。

## 使用场景

- 你正在开发一个需要自适应 AI 对手的游戏，希望使用强化学习离线训练策略，并在运行时加载模型进行推理。
- 你需要在游戏内进行在线优化（如路径规划、技能选择），利用无梯度优化器对连续参数空间进行搜索。
- 你希望为 AI 设计复杂的动作空间（如组合技能、互斥选择、固定长度序列），本插件的 Action Schema 提供了声明式定义方式。
- 你需要高效处理大量并行的 AI 实例（如群体 AI），利用 `FIndexSet` 和批处理数组减少内存和计算开销。

## 蓝图用法

Learning 模块本身主要提供 C++ 底层支持，但通过 `ULearningNeuralNetworkData` 可以在蓝图中操作神经网络数据：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInputSize` | 返回网络输入维度 | `ULearningNeuralNetworkData` |
| `GetOutputSize` | 返回网络输出维度 | `ULearningNeuralNetworkData` |
| `GetCompatibilityHash` | 返回兼容性哈希，用于快速验证网络是否匹配 | `ULearningNeuralNetworkData` |
| `GetContentHash` | 返回内容哈希，用于验证网络数据是否变化 | `ULearningNeuralNetworkData` |
| `IsEmpty` | 判断网络数据是否为空 | `ULearningNeuralNetworkData` |

### 使用示例

1. 加载一个训练好的神经网络模型（资产类型为 `ULearningNeuralNetworkData`）。
2. 在蓝图节点中调用 `GetInputSize` 获取输入维度，以确保传递给网络的观测向量大小正确。
3. 在运行时通过 C++ 封装的 `FNeuralNetworkPolicy` 或 `FNeuralNetworkCritic` 进行推理（蓝图无直接暴露这些结构体，需通过 C++ 或自定义函数库使用）。

## C++ 用法

### 头文件引入

```cpp
#include "LearningArray.h"
#include "LearningNeuralNetwork.h"
#include "LearningOptimizer.h"
#include "LearningAdamOptimizer.h"
#include "LearningPolicy.h"
#include "LearningObservation.h"
#include "LearningAction.h"
```

### 基本用法

#### 1. 多维数组操作

来源：`Engine/Plugins/Experimental/LearningAgents/Source/Learning/Public/LearningArray.h`

```cpp
// 创建一个形状为 (3, 4) 的二维 float 数组
TLearningArray<2, float> Data = { {1.0f, 2.0f, 3.0f, 4.0f},
                                  {5.0f, 6.0f, 7.0f, 8.0f},
                                  {9.0f, 10.0f, 11.0f, 12.0f} };

// 获取形状
auto Shape = Data.Shape(); // [3, 4]

// 访问元素 (0-based)
float& Val = Data[1][2]; // 第1行第2列，值为 7.0f

// 遍历所有元素
for (int64 i = 0; i < Data.Num(); ++i)
{
    for (int64 j = 0; j < Data.Num<1>(); ++j)
    {
        Data[i][j] *= 2.0f;
    }
}
```

#### 2. 使用 Adam 优化器

来源：`Engine/Plugins/Experimental/LearningAgents/Source/Learning/Public/LearningAdamOptimizer.h`

```cpp
#include "LearningAdamOptimizer.h"

// 创建优化器
UE::Learning::FAdamOptimizerSettings Settings;
Settings.LearningRate = 0.1f;
Settings.FiniteDifferenceStd = 0.3f;

UE::Learning::FAdamOptimizer Optimizer(12345, Settings);

// 假设我们在优化一个 2 维参数，使用 10 个样本
constexpr int32 SampleNum = 10;
constexpr int32 DimNum = 2;
Optimizer.Resize(SampleNum, DimNum);

// 初始猜测为零向量
TLearningArray<1, float> InitialGuess({0.0f, 0.0f});
TLearningArray<2, float> Samples;
Samples.SetUninitialized({SampleNum, DimNum});

// 重置优化器，生成初始样本
Optimizer.Reset(Samples, InitialGuess);

// 模拟一轮优化：计算每个样本的损失，然后更新
TLearningArray<1, float> Losses;
Losses.SetUninitialized({SampleNum});
for (int32 i = 0; i < SampleNum; ++i)
{
    Losses[i] = (Samples[i][0] - 5.0f) * (Samples[i][0] - 5.0f) + Samples[i][1] * Samples[i][1]; // 最小化 (x-5)^2 + y^2
}
Optimizer.Update(Samples, Losses, UE::Learning::ELogSetting::Normal);
```

#### 3. 创建策略网络推理对象

来源：`Engine/Plugins/Experimental/LearningAgents/Source/Learning/Public/LearningPolicy.h`

```cpp
#include "LearningPolicy.h"
#include "LearningNeuralNetwork.h"

// 假设已经有一个训练好的神经网络模型
TSharedPtr<UE::Learning::FNeuralNetwork> NeuralNetwork = ...;

// 创建 Policy 对象，用于 100 个并行实例
constexpr int32 MaxInstanceNum = 100;
constexpr int32 ObsEncodedNum = 64;
constexpr int32 ActionEncodedNum = 10;
constexpr int32 MemoryStateNum = 32;
UE::Learning::FNeuralNetworkPolicy Policy(
    MaxInstanceNum,
    ObsEncodedNum,
    ActionEncodedNum,
    MemoryStateNum,
    NeuralNetwork);

// 准备输入数据
TLearningArray<2, float> Observations({MaxInstanceNum, ObsEncodedNum});
TLearningArray<2, float> Memory({MaxInstanceNum, MemoryStateNum});
// ... 填充观测和记忆状态 ...

// 输出容器
TLearningArray<2, float> ActionVectors({MaxInstanceNum, ActionEncodedNum});
TLearningArray<2, float> NewMemory({MaxInstanceNum, MemoryStateNum});

// 只评估前 10 个实例
UE::Learning::FIndexSet Instances(0, 10);
Policy.Evaluate(ActionVectors, NewMemory, Observations, Memory, Instances);
```

#### 4. 使用动作模式构建动作空间描述

来源：`Engine/Plugins/Experimental/LearningAgents/Source/Learning/Public/LearningAction.h`

```cpp
#include "LearningAction.h"

// 创建一个动作 Schema：组合（连续移动 + 离散攻击按钮）
UE::Learning::Action::FSchema Schema;

// 连续动作（移动方向：2维）
auto MoveAction = Schema.AddContinuous(2);
Schema.FinishContinuous(MoveAction, 1.0f); // 缩放因子 1.0

// 离散独占动作（攻击类型：3种）
auto AttackAction = Schema.AddDiscreteExclusive(3);
TArray<float> PriorProbs = {0.5f, 0.3f, 0.2f};
Schema.FinishDiscreteExclusive(AttackAction, PriorProbs);

// 最终组合为 And 动作
auto Root = Schema.AddAnd({MoveAction, AttackAction});
Schema.FinishAnd(Root);

// 设置根元素
Schema.SetRoot(Root);

// 获取编码后的总维度
int32 ActionDimensionNum = Schema.GetEncodedSize(); // 连续维度 + 离散编码维度
```

### 进阶用法

#### 结合 CMA-ES 优化器进行在线规划

来源：`Engine/Plugins/Experimental/LearningAgents/Source/Learning/Public/LearningOptimizationPlanner.h`

```cpp
#include "LearningOptimizationPlanner.h"
#include "LearningCMAOptimizer.h"

// 创建 CMA 优化器
UE::Learning::FCMAOptimizer Optimizer(42);
Optimizer.Resize(/*SampleNum=*/64, /*DimNum=*/10);

// 创建规划器缓冲区
UE::Learning::FOptimizationPlannerBuffer Buffer;
Buffer.Resize(/*SampleNum=*/64, /*StepNum=*/20, /*ActionVectorDimNum=*/10);

// 定义环境函数（重置、行动、更新、奖励）
auto ResetFunc = [](const UE::Learning::FIndexSet Instances) {
    // 重置指定实例的环境
};
auto ActionFunc = [](const UE::Learning::FIndexSet Instances) {
    // 将动作向量应用到实例
};
auto UpdateFunc = [](const UE::Learning::FIndexSet Instances) {
    // 更新环境模拟一步
};
auto RewardFunc = [](const UE::Learning::FIndexSet Instances) {
    // 返回每个实例的奖励
};

// 初始动作向量（20步，10维）
TLearningArray<2, float> ActionVectors({20, 10});
ActionVectors.SetZero();

// 运行规划器（迭代优化）
UE::Learning::OptimizationPlanner::Plan(
    ActionVectors,
    Buffer,
    Optimizer,
    /*ActionVectorBuffer=*/Buffer.Samples[0], // 复用缓冲区
    /*RewardBuffer=*/Buffer.Losses,
    /*IterationNum=*/100,
    ResetFunc, ActionFunc, UpdateFunc, RewardFunc,
    UE::Learning::FIndexSet(0, 1), // 只规划第0个实例
    UE::Learning::ELogSetting::Normal
);
```

## Demo 示例

### 示例：使用 Adam 优化器最小化简单函数

**LearningDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "LearningArray.h"
#include "LearningAdamOptimizer.h"

/**
 * 演示如何使用 Adam 优化器进行最小化
 */
class FLearningDemo
{
public:
    void RunOptimization();
};
```

**LearningDemo.cpp**
```cpp
#include "LearningDemo.h"

void FLearningDemo::RunOptimization()
{
    using namespace UE::Learning;

    // 目标：最小化 f(x,y) = (x-3)^2 + (y+1)^2
    FAdamOptimizerSettings Settings;
    Settings.LearningRate = 0.2f;
    Settings.FiniteDifferenceStd = 0.5f;

    FAdamOptimizer Optimizer(0xDEADBEEF, Settings);

    constexpr int32 SampleNum = 20;
    constexpr int32 DimNum = 2;
    Optimizer.Resize(SampleNum, DimNum);

    TLearningArray<2, float> Samples;
    Samples.SetUninitialized({SampleNum, DimNum});

    TLearningArray<1, float> InitialGuess({0.0f, 0.0f});
    Optimizer.Reset(Samples, InitialGuess);

    TLearningArray<1, float> Losses;
    Losses.SetUninitialized({SampleNum});

    constexpr int32 Iterations = 50;
    for (int32 Iter = 0; Iter < Iterations; ++Iter)
    {
        // 计算每个样本的损失
        for (int32 i = 0; i < SampleNum; ++i)
        {
            float x = Samples[i][0];
            float y = Samples[i][1];
            Losses[i] = (x - 3.0f)*(x - 3.0f) + (y + 1.0f)*(y + 1.0f);
        }

        // 优化一步
        Optimizer.Update(Samples, Losses, ELogSetting::Silent);
    }

    // 取最佳样本（假设损失最小为第一个样本，实际应遍历）
    float BestX = Samples[0][0];
    float BestY = Samples[0][1];
    UE_LOG(LogTemp, Log, TEXT("Best solution: x=%f, y=%f"), BestX, BestY);
}
```

## 模块依赖

`Learning` 模块作为核心算法库，其依赖主要在 `Build.cs` 中配置。以下基于源码分析列出独特依赖：

| 模块 | 用途 |
|---|---|
| `Eigen` (第三方) | 线性代数运算（矩阵分解、特征值计算等），通过 `LearningEigen.h` 封装 |
| `NNE` | 神经网络推理运行时（加载 ONNX 模型） |
| `NNEOnnxruntime` (推断) | ONNX 运行时的 UE 集成（在 `LearningNeuralNetwork.h` 中通过 `UNNEModelData` 使用） |

其他模块（如 `LearningAgents`、`LearningAgentsTraining`）会额外依赖：
- `LearningAgentsTraining` 依赖 `UnrealEd`（用于编辑器功能）
- `LearningAgentsReplay` 可能依赖 `LevelSequence` 等（未详细分析）

> **注意**：如果你的模块只需使用 `Learning` 基础库（数组、优化器、规划器），请确保在 `Build.cs` 中添加以下依赖：
> ```csharp
> PublicDependencyModuleNames.AddRange(
>     new string[] {
>         "Learning",
>         // 如需神经网络则额外加：
>         // "NNE", "NNEOnnxruntime"
>     }
> );
> ```

## 维护状态

### 近期更新

从 git log 可见最近活跃的提交（截至 2025-09-23）：

- 2025-09-23 `e6f9d5f` — [LearningAgents] LearningAgentsRecording (新增录制功能)
- 2025-09-23 `dcf81878` — [LearningAgents] bug fix to conv1d conv2d serialization (修复1D/2D卷积序列化bug)
- 2025-09-23 `86de7c71` — [LearningAgents] Missing types in ComputeObservationSchemaSubsetIndices and bugfix (修复观测子集索引遗漏的类型)
- 2025-09-23 `1571e33e` — LearningAgents: Ensure instead of check during GetAgent (将 Check 改为 Ensure)
- 2025-09-16 `f485ef53` — [LearningAgents] - schema subset bug fix (修复Schema子集bug)

### 维护评价

- **创建时间**：2025-09-16，距今不到1个月（从当前时间计算），属于**全新插件**。
- **更新频率**：近期每日有提交，表明处于**积极开发阶段**。
- **功能成熟度**：基础算法（优化器、数组、神经网络）已较完善，但高层的 `LearningAgents` 模块仍在快速迭代，存在一些 bug 修复。
- **已知问题**：卷积序列化存在 bug（已修复），Schema 子集索引有遗漏类型（已修复）。插件仍在实验性质，虽未标记为 Beta，但 `EnabledByDefault=false` 暗示需要手动启用。
- **推荐使用**：对于需要集成机器学习的 UE 项目，强烈推荐使用此插件作为底层基础设施。但由于仍在活跃更新，建议跟踪官方 changelog，并注意接口可能发生微小变化。

**综合评价**：🆕 全新插件，积极开发中，推荐用于新项目或作为学习参考。对于生产环境，建议锁定特定 commit 版本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/learning-agents-in-unreal-engine)（引擎文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/LearningAgents/Source/LearningAgentsTraining/Private/Tests)（部分测试位于训练模块下）