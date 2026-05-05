# Learning Core

> Learning Core is a machine learning library for Unreal Engine.

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（神经网络模型资产） |
| 模块 | `Learning` (Runtime), `LearningTraining` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-14 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/LearningCore) | |

## 用途

LearningCore 是 UE5 原生的机器学习基础库，提供从数据结构到训练推理的完整 ML 工具链。它解决的核心问题是：**在 Unreal Engine 内部高效地进行机器学习计算，而无需依赖外部 Python 环境或跨进程通信**。

具体能力包括：

- **多维数组系统**（`TLearningArray`）：支持任意维度、ISPC SIMD 加速的高性能数组运算，替代简单的 `TArray<float>` 用于 ML 数据存储
- **神经网络集成**：通过 NNE（Neural Network Engine）接口加载和推理 ONNX 模型，提供 `ULearningNeuralNetworkData` 作为可序列化的网络资产
- **黑盒优化器**：Adam、CMA-ES、PSO 三种优化器，用于无梯度或有限差分的参数优化
- **强化学习组件**：Policy（策略网络）、Critic（价值网络）、Observation/Action Schema（观测/动作空间定义），构成 RL 训练的基础构件
- **经典 ML 工具**：PCA 降维、K-Means 聚类
- **高性能随机数**：基于哈希的 PRNG，支持 ISPC 向量化，比 `FRandomStream` 快最高 100 倍
- **时序数据结构**：`FFrameSet`、`FFrameRangeSet`、`FFrameAttribute`，用于高效存储和操作动画/回放数据

该插件默认不启用（`EnabledByDefault: false`），处于实验阶段（`IsExperimentalVersion: true`），版本号 0.1，由 Epic Games 开发维护。

## 使用场景

- 你在做一个需要 **RL-based AI** 的游戏（如角色控制、NPC 行为学习）→ 使用 Policy + Critic + Observation/Action Schema 构建训练管线
- 你需要在运行时 **优化一组参数**（如程序化生成的调参、物理模拟参数搜索）→ 使用 Adam/CMA/PSO 优化器
- 你有大量 **动画或运动捕捉数据** 需要索引、切片、批量操作 → 使用 FrameSet/FrameRangeSet/FrameAttribute
- 你需要对高维特征数据做 **降维**（如将骨骼动画数据压缩）→ 使用 PCA Encoder
- 你需要将数据 **聚类**（如将动画片段自动分组）→ 使用 K-Means
- 你需要在 UE 内 **加载并运行 ONNX 神经网络** → 使用 ULearningNeuralNetworkData + NNE
- 你需要大量高质量 **并行随机数**（如蒙特卡洛采样）→ 使用 Learning::Random

## 蓝图用法

本插件主要面向 C++ 开发者，Blueprint 暴露非常有限。唯一可用的 UObject 是 `ULearningNeuralNetworkData`（标记为 `BlueprintType`），可在蓝图中作为资产引用，但其核心方法（`Init`、`LoadFromSnapshot`、`SaveToSnapshot` 等）均为 C++ 调用，未标记 `BlueprintCallable`。

### 可用的蓝图属性

| 属性 | 类型 | 说明 | 所在类 |
|---|---|---|---|
| `InputSize` | int32 (VisibleAnywhere) | 网络输入维度 | `ULearningNeuralNetworkData` |
| `OutputSize` | int32 (VisibleAnywhere) | 网络输出维度 | `ULearningNeuralNetworkData` |
| `CompatibilityHash` | int32 (VisibleAnywhere) | 兼容性哈希，用于快速校验网络是否匹配 | `ULearningNeuralNetworkData` |
| `ContentHash` | int32 (VisibleAnywhere) | 内容哈希 | `ULearningNeuralNetworkData` |
| `UpdateNumber` | int32 (VisibleAnywhere) | 更新计数，每次从快照加载时递增 | `ULearningNeuralNetworkData` |
| `FileData` | TArray&lt;uint8&gt; (VisibleAnywhere) | 原始网络文件数据 | `ULearningNeuralNetworkData` |

> **注意**：如需在蓝图中使用本插件的功能，建议通过 C++ 编写包装类并暴露 `BlueprintCallable` 函数。

## C++ 用法

### 头文件引入

```cpp
// 核心数组类型
#include "LearningArray.h"

// 神经网络
#include "LearningNeuralNetwork.h"

// 优化器
#include "LearningAdamOptimizer.h"
#include "LearningCMAOptimizer.h"
#include "LearningPSOOptimizer.h"

// 强化学习组件
#include "LearningPolicy.h"
#include "LearningCritic.h"
#include "LearningObservation.h"
#include "LearningAction.h"
#include "LearningCompletion.h"
#include "LearningOptimizationPlanner.h"

// 机器学习工具
#include "LearningPCA.h"
#include "LearningKMeans.h"

// 随机数
#include "LearningRandom.h"

// 帧数据结构
#include "LearningFrameSet.h"
#include "LearningFrameRangeSet.h"
#include "LearningFrameAttribute.h"

// 进度追踪
#include "LearningProgress.h"
```

### 基本用法

#### 1. 多维数组

`TLearningArray` 是插件的核心数据容器，支持任意维度，底层使用 64 位分配器以支持大规模数据。

```cpp
#include "LearningArray.h"

// 创建一个 2D 数组：100 个样本，每个样本 8 维特征
TLearningArray<2, float> Data;
Data.SetNumUninitialized({100, 8});

// 写入数据
for (int32 SampleIdx = 0; SampleIdx < 100; SampleIdx++)
{
    for (int32 DimIdx = 0; DimIdx < 8; DimIdx++)
    {
        Data[SampleIdx][DimIdx] = static_cast<float>(SampleIdx * 8 + DimIdx);
    }
}

// 获取维度大小
int32 SampleNum = Data.Num<0>(); // 100
int32 DimNum = Data.Num<1>();    // 8

// 创建只读视图（零拷贝）
TLearningArrayView<2, const float> DataView = Data;

// 创建 1D 切片视图（第 5 个样本的所有特征）
TLearningArrayView<1, const float> SingleSample = Data[5];
```

#### 2. FIndexSet 索引集合

`FIndexSet` 用于高效表示数据子集，支持连续切片和离散索引两种模式，便于批量操作。

```cpp
#include "LearningArray.h"

// 方式一：连续切片（高效，可被 ISPC 优化）
UE::Learning::FIndexSet SliceIndices(10, 20); // 从索引 10 开始的 20 个元素

// 方式二：离散索引数组
TArray<int32> ActiveInstances = {0, 3, 7, 12, 42};
UE::Learning::FIndexSet DiscreteIndices(ActiveInstances);

// 方式三：单个索引
UE::Learning::FIndexSet SingleIndex(5);

// 遍历索引集合
for (int32 Idx : SliceIndices)
{
    // 处理每个索引
}

// 获取索引数量
int32 Count = SliceIndices.Num();
```

#### 3. 使用优化器

三种优化器均实现 `IOptimizer` 接口，用法一致：`Resize` → `Reset` → 循环 `Update`。

```cpp
#include "LearningAdamOptimizer.h"
#include "LearningArray.h"

// 创建 Adam 优化器
UE::Learning::FAdamOptimizer Optimizer(
    42,  // 随机种子
    UE::Learning::FAdamOptimizerSettings{
        .FiniteDifferenceStd = 0.3f,
        .LearningRate = 0.1f,
        .Beta1 = 0.9f,
        .Beta2 = 0.999f
    }
);

const int32 SampleNum = 16;
const int32 DimNum = 4;

// 分配缓冲区
Optimizer.Resize(SampleNum, DimNum);

TLearningArray<2, float> Samples;
Samples.SetNumUninitialized({SampleNum, DimNum});

TLearningArray<1, float> Losses;
Losses.SetNumUninitialized({SampleNum});

// 初始猜测
TLearningArray<1, float> InitialGuess;
InitialGuess.SetNumUninitialized({DimNum});
for (int32 i = 0; i < DimNum; i++) InitialGuess[i] = 1.0f;

// 初始化采样
Optimizer.Reset(Samples, InitialGuess);

// 优化循环
for (int32 Iter = 0; Iter < 100; Iter++)
{
    // 评估每个样本的损失
    for (int32 s = 0; s < SampleNum; s++)
    {
        float Loss = 0.0f;
        for (int32 d = 0; d < DimNum; d++)
        {
            Loss += Samples[s][d] * Samples[s][d]; // 最小化平方和
        }
        Losses[s] = Loss;
    }

    // 更新优化器（内部会重新采样并根据损失调整）
    Optimizer.Update(Samples, Losses);
}
```

#### 4. 高性能随机数

`Learning::Random` 使用哈希式 PRNG，将状态变异与数值生成分离，天然支持 SIMD 并行。

```cpp
#include "LearningRandom.h"

uint32 State = 12345;

// 生成随机数（不改变状态）
float R0 = UE::Learning::Random::Float(State ^ 0x6591b5b6);
float R1 = UE::Learning::Random::Float(State ^ 0x88f6747a);
int32 R2 = UE::Learning::Random::IntInRange(State ^ 0xabcd1234, 0, 100);
float Gauss = UE::Learning::Random::Gaussian(State ^ 0xdeadbeef, 0.0f, 1.0f);

// 批量生成后变异状态
State = UE::Learning::Random::Int(State ^ 0xec664ea3);

// 大规模并行生成（每个元素独立种子，可被 ISPC 向量化）
const int32 Num = 1024;
TLearningArray<1, float> RandomValues;
RandomValues.SetNumUninitialized({Num});

for (int32 Idx = 0; Idx < Num; Idx++)
{
    const uint32 Seed = UE::Learning::Random::Int(Idx ^ 0x56df2e17);
    RandomValues[Idx] = UE::Learning::Random::Float(State ^ Seed);
}

State = UE::Learning::Random::Int(State ^ 0x017f54f9);
```

### 进阶用法

#### 1. 观测与动作空间定义

Observation 和 Action Schema 系统用于定义 RL 中的状态空间和动作空间，支持嵌套组合。

```cpp
#include "LearningObservation.h"
#include "LearningAction.h"

using namespace UE::Learning;

// 定义观测空间
Observation::FSchema ObservationSchema;

// 添加连续观测（如位置、速度）
Observation::FSchemaElement PositionObs = ObservationSchema.AddContinuous(
    Observation::FSchemaContinuousParameters{
        .Num = 3,  // XYZ
        .NormalizationOption = Observation::ENormalization::AutoPerDimension
    });

// 添加离散观测（如状态枚举）
Observation::FSchemaElement StateObs = ObservationSchema.AddNamedDiscreteExclusive(
    Observation::FSchemaNamedDiscreteExclusiveParameters{
        .Names = {TEXT("Idle"), TEXT("Walking"), TEXT("Running"), TEXT("Jumping")}
    });

// 组合观测
Observation::FSchemaElement CombinedObs = ObservationSchema.AddAnd(
    {PositionObs, StateObs});

// 定义动作空间
Action::FSchema ActionSchema;

// 连续动作（如力向量）
Action::FSchemaElement ForceAction = ActionSchema.AddContinuous(
    Action::FSchemaContinuousParameters{
        .Num = 3,
        .NormalizationOption = Action::ENormalization::AutoPerDimension
    });

// 离散动作（如选择）
Action::FSchemaElement ChoiceAction = ActionSchema.AddDiscreteExclusive(
    Action::FSchemaDiscreteExclusiveParameters{
        .Num = 4
    });
```

#### 2. 神经网络策略与评论家

```cpp
#include "LearningPolicy.h"
#include "LearningCritic.h"
#include "LearningNeuralNetwork.h"

// 假设已有训练好的网络
TSharedPtr<UE::Learning::FNeuralNetwork> PolicyNetwork;
TSharedPtr<UE::Learning::FNeuralNetwork> CriticNetwork;

const int32 MaxInstanceNum = 64;
const int32 ObservationEncodedNum = 128;
const int32 ActionEncodedNum = 32;
const int32 MemoryStateNum = 64;

// 创建策略对象
UE::Learning::FNeuralNetworkPolicy Policy(
    MaxInstanceNum,
    ObservationEncodedNum,
    ActionEncodedNum,
    MemoryStateNum,
    PolicyNetwork);

// 创建评论家对象
UE::Learning::FNeuralNetworkCritic Critic(
    MaxInstanceNum,
    ObservationEncodedNum,
    MemoryStateNum,
    CriticNetwork);

// 分配缓冲区
TLearningArray<2, float> ObsEncoded;
ObsEncoded.SetNumUninitialized({MaxInstanceNum, ObservationEncodedNum});

TLearningArray<2, float> ActionEncoded;
ActionEncoded.SetNumUninitialized({MaxInstanceNum, ActionEncodedNum});

TLearningArray<2, float> MemoryState;
MemoryState.SetNumUninitialized({MaxInstanceNum, MemoryStateNum});

TLearningArray<2, float> NewMemoryState;
NewMemoryState.SetNumUninitialized({MaxInstanceNum, MemoryStateNum});

TLearningArray<1, float> Returns;
Returns.SetNumUninitialized({MaxInstanceNum});

// 定义活跃实例子集
UE::Learning::FIndexSet ActiveInstances(0, 32); // 前 32 个实例

// 评估策略
Policy.Evaluate(
    ActionEncoded,
    NewMemoryState,
    ObsEncoded,
    MemoryState,
    ActiveInstances);

// 评估评论家
Critic.Evaluate(
    Returns,
    ObsEncoded,
    MemoryState,
    ActiveInstances);
```

#### 3. PCA 降维

```cpp
#include "LearningPCA.h"

// 准备数据：1000 个样本，每个 256 维
TLearningArray<2, float> HighDimData;
HighDimData.SetNumUninitialized({1000, 256});

// ... 填充数据 ...

// 创建 PCA 编码器并拟合
UE::Learning::FPCAEncoder PCAEncoder;
UE::Learning::FPCASettings PCASettings;
PCASettings.MaximumDimensions = 32;
PCASettings.MaximumVarianceRatio = 0.95f;
PCASettings.bStableComputation = true;

UE::Learning::FPCAResult Result = PCAEncoder.Fit(HighDimData, PCASettings);

if (Result.bSuccess)
{
    UE_LOG(LogLearning, Log, TEXT("PCA: %d -> %d dimensions, %.2f variance preserved"),
        PCAEncoder.FeatureNum(), PCAEncoder.DimensionNum(), Result.VarianceRatioPreserved);

    // 变换数据
    TLearningArray<2, float> LowDimData;
    LowDimData.SetNumUninitialized({1000, PCAEncoder.DimensionNum()});
    PCAEncoder.Transform(LowDimData, HighDimData);

    // 变换单个向量
    TLearningArray<1, float> SingleLowDim;
    SingleLowDim.SetNumUninitialized({PCAEncoder.DimensionNum()});
    TLearningArray<1, float> SingleHighDim = HighDimData[0]; // 第一个样本
    PCAEncoder.Transform(SingleLowDim, SingleHighDim);
}
```

#### 4. K-Means 聚类

```cpp
#include "LearningKMeans.h"

const int32 ClusterNum = 8;
const int32 SampleNum = 500;
const int32 DimNum = 16;

TLearningArray<2, float> Samples;
Samples.SetNumUninitialized({SampleNum, DimNum});
// ... 填充数据 ...

// 初始化聚类中心
TLearningArray<2, float> Centers;
Centers.SetNumUninitialized({ClusterNum, DimNum});
UE::Learning::KMeans::InitCenters(Centers, Samples, 42);

// 分配缓冲区
TLearningArray<1, int32> Assignments;
Assignments.SetNumUninitialized({SampleNum});

TLearningArray<1, int32> AssignmentCounts;
AssignmentCounts.SetNumUninitialized({ClusterNum});

// 迭代优化
for (int32 Iter = 0; Iter < 20; Iter++)
{
    // 将每个样本分配到最近的聚类中心
    UE::Learning::KMeans::UpdateAssignmentsFromCenters(
        Assignments, Centers, Samples);

    // 统计每个聚类的样本数
    UE::Learning::KMeans::CountClusterAssignments(
        AssignmentCounts, Assignments);

    // 更新聚类中心
    UE::Learning::KMeans::UpdateCenters(
        Centers, Assignments, AssignmentCounts, Samples);
}
```

#### 5. 帧数据结构（动画/回放数据）

```cpp
#include "LearningFrameRangeSet.h"
#include "LearningFrameAttribute.h"

// 创建帧范围集合（用于标记动画片段）
UE::Learning::FFrameRangeSet RangeSet;

// 添加序列 0 的范围：帧 0-30 和帧 60-90
TLearningArray<1, int32> Starts0;
Starts0.SetNumUninitialized({2});
Starts0[0] = 0; Starts0[1] = 60;

TLearningArray<1, int32> Lengths0;
Lengths0.SetNumUninitialized({2});
Lengths0[0] = 30; Lengths0[1] = 30;

RangeSet.AddEntry(0, Starts0, Lengths0);

// 添加序列 1 的范围：帧 10-50
TLearningArray<1, int32> Starts1;
Starts1.SetNumUninitialized({1});
Starts1[0] = 10;

TLearningArray<1, int32> Lengths1;
Lengths1.SetNumUninitialized({1});
Lengths1[0] = 40;

RangeSet.AddEntry(1, Starts1, Lengths1);

// 查询
int32 TotalFrames = RangeSet.GetTotalFrameNum();
int32 EntryNum = RangeSet.GetEntryNum();
```

#### 6. 优化规划器（Model Predictive Control 风格）

```cpp
#include "LearningOptimizationPlanner.h"
#include "LearningAdamOptimizer.h"

// 优化规划器通过反复模拟来寻找最优动作序列
UE::Learning::FOptimizationPlannerBuffer PlannerBuffer;
UE::Learning::FAdamOptimizer PlannerOptimizer(42);

const int32 StepNum = 16;
const int32 ActionDimNum = 3;
const int32 SampleNum = 32;

PlannerBuffer.Resize(SampleNum, StepNum, ActionDimNum);
PlannerOptimizer.Resize(SampleNum, StepNum * ActionDimNum);

TLearningArray<2, float> ActionVectors;
ActionVectors.SetNumUninitialized({StepNum, ActionDimNum});

// 定义回调函数
auto ResetFn = [](const UE::Learning::FIndexSet Instances) { /* 重置环境 */ };
auto ActionFn = [](const UE::Learning::FIndexSet Instances) { /* 执行动作 */ };
auto UpdateFn = [](const UE::Learning::FIndexSet Instances) { /* 更新环境 */ };
auto RewardFn = [](const UE::Learning::FIndexSet Instances) { /* 计算奖励 */ };

TLearningArray<2, float> ActionVectorBuffer;
ActionVectorBuffer.SetNumUninitialized({SampleNum, StepNum * ActionDimNum});

TLearningArray<1, float> RewardBuffer;
RewardBuffer.SetNumUninitialized({SampleNum});

// 运行优化规划
UE::Learning::OptimizationPlanner::Plan(
    ActionVectors,
    PlannerBuffer,
    PlannerOptimizer,
    ActionVectorBuffer,
    RewardBuffer,
    50,  // 迭代次数
    ResetFn,
    ActionFn,
    UpdateFn,
    RewardFn,
    UE::Learning::FIndexSet(0, SampleNum));
```

## Demo 示例

以下示例展示如何创建一个 Actor，使用 CMA 优化器在运行时寻找函数最小值。

### MyCMAOptimizationActor.h

```cpp
// MyCMAOptimizationActor.h
#pragma once

#include "GameFramework/Actor.h"
#include "LearningCMAOptimizer.h"
#include "LearningArray.h"
#include "MyCMAOptimizationActor.generated.h"

UCLASS()
class AMyCMAOptimizationActor : public AActor
{
    GENERATED_BODY()

public:
    AMyCMAOptimizationActor();

    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    void EvaluateLosses();

    UE::Learning::FCMAOptimizer Optimizer;

    TLearningArray<2, float> Samples;
    TLearningArray<1, float> Losses;

    int32 Iteration = 0;

    static constexpr int32 DimensionNum = 4;
    int32 SampleNum = 0;
};
```

### MyCMAOptimizationActor.cpp

```cpp
// MyCMAOptimizationActor.cpp
#include "MyCMAOptimizationActor.h"
#include "LearningLog.h"

AMyCMAOptimizationActor::AMyCMAOptimizationActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyCMAOptimizationActor::BeginPlay()
{
    Super::BeginPlay();

    // CMA 默认采样数约为 4 + 3 * log(DimNum)
    SampleNum = UE::Learning::FCMAOptimizer::DefaultSampleNum(DimensionNum);

    Optimizer = UE::Learning::FCMAOptimizer(
        42,
        UE::Learning::FCMAOptimizerSettings{
            .InitialStepSize = 0.5f,
            .SurvialRatio = 0.5f
        });

    Optimizer.Resize(SampleNum, DimensionNum);

    Samples.SetNumUninitialized({SampleNum, DimensionNum});
    Losses.SetNumUninitialized({SampleNum});

    // 初始猜测：所有维度为 5.0（最优解在原点）
    TLearningArray<1, float> InitialGuess;
    InitialGuess.SetNumUninitialized({DimensionNum});
    for (int32 i = 0; i < DimensionNum; i++)
    {
        InitialGuess[i] = 5.0f;
    }

    Optimizer.Reset(Samples, InitialGuess);

    UE_LOG(LogLearning, Log,
        TEXT("CMA Optimizer started: %d samples, %d dimensions"),
        SampleNum, DimensionNum);
}

void AMyCMAOptimizationActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    EvaluateLosses();
    Optimizer.Update(Samples, Losses);
    Iteration++;

    if (Iteration % 10 == 0)
    {
        // 打印当前最优样本（Losses[0] 是排序后的最优）
        FString SolutionStr;
        for (int32 d = 0; d < DimensionNum; d++)
        {
            SolutionStr += FString::Printf(TEXT("%.4f "), Samples[0][d]);
        }

        UE_LOG(LogLearning, Log,
            TEXT("Iteration %d | Loss: %.6f | Solution: [%s]"),
            Iteration, Losses[0], *SolutionStr);
    }
}

void AMyCMAOptimizationActor::EvaluateLosses()
{
    // 目标函数：Rosenbrock 函数（经典优化测试函数）
    // f(x) = sum(100*(x[i+1] - x[i]^2)^2 + (1-x[i])^2)
    // 最优解在 (1, 1, 1, 1)
    for (int32 s = 0; s < SampleNum; s++)
    {
        float Loss = 0.0f;
        for (int32 d = 0; d < DimensionNum - 1; d++)
        {
            float X = Samples[s][d];
            float Y = Samples[s][d + 1];
            Loss += 100.0f * FMath::Square(Y - X * X) + FMath::Square(1.0f - X);
        }
        Losses[s] = Loss;
    }
}
```

## 模块依赖

从源码头文件的 `#include` 和类型引用推断，本插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `NNE` (Neural Network Engine) | 神经网络模型加载与推理（`ULearningNeuralNetworkData` 通过 NNE 接口执行推理） |
| Eigen（第三方库） | 线性代数运算（矩阵分解、特征值计算等，用于 PCA 和优化器内部） |

此外，本插件可选依赖 Intel ISPC 编译器（通过 `UE_LEARNING_ISPC` 宏控制），启用后可对数组运算和随机数生成进行 SIMD 向量化加速。

无其他特殊依赖（仅标准 Core/Engine/CoreUObject 等）。

## 维护状态

### 近期更新

> ⚠️ 未提供 git log 数据，无法列出具体 commit。以下基于元数据分析。

本插件为实验性插件（`IsExperimentalVersion: true`），版本号 0.1，创建于 2026-04-1