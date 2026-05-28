# ML Deformer Nearest Neighbor Model (DEPRECATED)

> Nearest Neighbor Model for the ML Deformer Framework. This model has been deprecated. Please use the Detail Pose Model instead.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 最近邻模型 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `NearestNeighborModel` (Runtime), `NearestNeighborModelEditor` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-17 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel) | |

## 用途

**注意：此插件已弃用，官方建议使用 `Detail Pose Model`。**

基于源码分析，该插件为 `MLDeformer` 框架提供了一个基于机器学习（ML）的骨骼网格形变模型。它解决的核心问题是：在运行时以极高的效率为骨骼网格（如角色面部、衣物）产生高质量的顶点级形变（Vertex Delta）。

该插件并非使用通用的神经网络进行端到端的形变预测，而是采用了一种混合方法：
1.  **主成分分析（PCA）**：对形变数据进行降维，学习一组线性基（Basis）。
2.  **最近邻搜索（Nearest Neighbor）**：在预计算的小型数据集中，根据神经网络预测的系数快速找到最相似的预计算形变。
3.  **神经网络**：一个轻量级的网络，根据当前骨骼姿态预测用于PCA降维的系数和用于最近邻搜索的索引。

最终的形变结果由三部分组成：`顶点均值形变 + PCA基 * 预测系数 + 最近邻残差形变`。这种方法相比直接运行完整的神经网络，在保持形变质量的同时，显著降低了运行时的计算开销。该模型还支持将网格划分为多个独立的部分（如上衣、裤子），对每个部分独立进行搜索，以提高精度和灵活性。

## 使用场景

-   你在开发一个对实时性能要求极高的电影级数字人项目，需要高质量的面部/衣物动态褶皱形变，但希望避免纯神经网络推理的性能开销。
-   你需要在运行时为角色服装（如衬衫、裙子）生成基于物理模拟或动画的复杂褶皱，并希望这些褶皱能“记忆”和“粘附”在特定姿态上一段时间（通过 `DecayFactor` 实现时间衰减）。
-   你的骨骼网格由多个独立的可变形部分组成（例如，一个角色模型包含上衣、裤子和头发），并且需要为每个部分独立训练和执行形变，以获得更精确的结果。
-   你正在维护一个旧项目，并且其 ML 变形器系统是基于此插件构建的。**（对于新项目，请直接使用 `Detail Pose Model`）**。

## 蓝图用法

该插件的核心功能主要通过 C++ 类提供，蓝图接口主要用于查询配置和进行特定的推理控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Num Sections` | 获取模型中定义的网格部分数量。 | `UNearestNeighborModel` |
| `Get Section` | 根据索引获取一个网格部分 (`UNearestNeighborModelSection`) 的引用。 | `UNearestNeighborModel` |
| `Does Use PCA` | 查询模型是否使用预计算的 PCA 基。 | `UNearestNeighborModel` |
| `Get Num Basis` | 获取特定部分的 PCA 基数量。 | `UNearestNeighborModelSection` |
| `Reset` | 重置模型实例的内部状态（如上一师权重）。 | `UNearestNeighborModelInstance` |
| `Eval` | （Python/调试用）运行一次网络推理，输入数据，返回输出数据。 | `UNearestNeighborModelInstance` |

### 使用示例（蓝图描述）

1.  **查询模型信息**：
    -   从你的 `MLDeformerComponent` 获取 `NearestNeighborModel` 资产。
    -   调用 `Get Num Sections` 和 `Get Section` 来遍历各部分，并用 `Get Num Basis` 获取每部分的参数。

2.  **控制推理过程**：
    -   获取绑定到 `SkeletalMeshComponent` 的 `NearestNeighborModelInstance`（通常由组件内部管理）。
    -   在需要调试或测试时，可以调用其 `Eval` 函数，传入一个 `TArray<float>` 作为神经网络输入，获得一次完整的推理结果输出。

## C++ 用法

### 头文件引入

```cpp
#include "NearestNeighborModel.h"
#include "NearestNeighborModelInstance.h"
```

### 基本用法

以下代码片段展示了如何获取并查询一个 `UNearestNeighborModel` 的基本配置。通常，模型资产是在编辑器中配置的，运行时主要是通过其对应的 `Instance` 来驱动。

```cpp
// 假设你已经有一个指向 UNearestNeighborModel 的指针 (例如从资产加载)
UNearestNeighborModel* NearestNeighborModel = ...;

// 检查模型是否已准备好用于推理
if (NearestNeighborModel && NearestNeighborModel->IsReadyForInference())
{
    // 获取网格部分数量
    int32 NumSections = NearestNeighborModel->GetNumSections();
    UE_LOG(LogTemp, Log, TEXT("Model has %d sections."), NumSections);

    // 查询第一个部分的信息
    if (NumSections > 0)
    {
        const UNearestNeighborModelSection& FirstSection = NearestNeighborModel->GetSection(0);
        int32 NumBasis = FirstSection.GetNumBasis();
        bool bUsePCA = FirstSection.DoesUsePCA();
        UE_LOG(LogTemp, Log, TEXT("Section 0: NumBasis=%d, UsesPCA=%s"), NumBasis, bUsePCA ? TEXT("true") : TEXT("false"));
    }
}
```

### 进阶用法

当需要更精细地控制网络实例（例如在自定义的计算流程中）时，可以获取 `UNearestNeighborOptimizedNetworkInstance`。

```cpp
// 获取模型中的优化网络
TWeakObjectPtr<const UNearestNeighborOptimizedNetwork> OptimizedNetwork = NearestNeighborModel->GetOptimizedNetwork();

// 创建一个网络实例
UNearestNeighborOptimizedNetworkInstance* NetworkInstance = OptimizedNetwork->CreateInstance();

// 设置输入 (示例数据)
TArrayView<float> Inputs = NetworkInstance->GetInputs();
// ... 用你的骨骼姿态数据填充 Inputs ...

// 运行推理
NetworkInstance->Run();

// 获取输出
TArrayView<const float> Outputs = NetworkInstance->GetOutputs();
// ... 使用 Outputs 中的预测系数 ...
```

## Demo 示例

以下是一个最小化的 C++ 组件示例，演示如何集成 `UNearestNeighborModel` 到自定义逻辑中。

### 头文件 (MyNearestNeighborComponent.h)

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NearestNeighborModel.h" // 包含插件头文件
#include "MyNearestNeighborComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyNearestNeighborComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyNearestNeighborComponent();

protected:
    virtual void BeginPlay() override;

public:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    // 引用一个在编辑器中设置的最近邻模型资产
    UPROPERTY(EditAnywhere, Category = "ML Deformer")
    TObjectPtr<UNearestNeighborModel> NearestNeighborModel;

private:
    TWeakObjectPtr<const UNearestNeighborOptimizedNetwork> CachedNetwork;
    TUniquePtr<UNearestNeighborOptimizedNetworkInstance> NetworkInstance;
};
```

### 源文件 (MyNearestNeighborComponent.cpp)

```cpp
#include "MyNearestNeighborComponent.h"
#include "NearestNeighborOptimizedNetwork.h"

UMyNearestNeighborComponent::UMyNearestNeighborComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyNearestNeighborComponent::BeginPlay()
{
    Super::BeginPlay();

    // 验证并缓存网络
    if (NearestNeighborModel && NearestNeighborModel->IsReadyForInference())
    {
        CachedNetwork = NearestNeighborModel->GetOptimizedNetwork();
        if (CachedNetwork.IsValid())
        {
            // 创建网络实例用于本次计算
            NetworkInstance.Reset(CachedNetwork->CreateInstance());
        }
    }
}

void UMyNearestNeighborComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!NetworkInstance.IsValid() || !CachedNetwork.IsValid())
    {
        return;
    }

    // --- 步骤 1: 准备神经网络输入 ---
    // 你需要从你的动画蓝图或骨骼数据中提取姿态信息，并填充到输入缓冲区
    // 这里仅为示例，实际填充逻辑取决于你的具体数据结构
    TArrayView<float> InputView = NetworkInstance->GetInputs();
    // ... (假设你已经有了一个函数 `MyPrepareInputs` 来填充 InputView) ...
    // MyPrepareInputs(InputView);

    // --- 步骤 2: 运行推理 ---
    NetworkInstance->Run();

    // --- 步骤 3: 获取并使用推理结果 ---
    TArrayView<const float> OutputView = NetworkInstance->GetOutputs();
    // 输出通常是一组系数，用于最近邻搜索和PCA重建。
    // 完整的顶点形变计算通常由 `UMLDeformerComponent` 内部通过 `UNearestNeighborModelInstance::Execute` 完成。
    // 如果你是在扩展该系统，可能需要进一步处理这些输出。
    // UE_LOG(LogTemp, Log, TEXT("Network inference completed. Output sample: %f, %f"), OutputView[0], OutputView[1]);
}
```

## 模块依赖

从 `NearestNeighborModel.Build.cs` 和 `NearestNeighborModelEditor.Build.cs` 分析，使用此插件的主要模块依赖如下：

| 模块 | 用途 |
|---|---|
| `MLDeformer` | 核心 ML 变形器框架，此插件是其一个具体模型实现。 |
| `MLDeformerEditor` | ML 变形器编辑器框架，提供编辑器UI和工作流。 |
| `OptimusCompute` | 计算框架，用于部分骨骼数据接口的 GPU 计算。 |
| `NNE` | (Neural Network Engine) 用于运行优化后的神经网络模型。 |

**注意**：这是该插件特有或关键的依赖，其他常见模块（如 Core, Engine）已省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 清理动画系统中的弃用代码，涉及此插件。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧日志宏迁移至新的日志格式。 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复Optimus运行时的多个问题。 |
| 2026-03-26 | `1bbb77b5` | Optimization to avoid creating duplicate section buffers in Optimus. | 优化以避免在Optimus中创建重复的缓冲区。 |
| 2025-10-07 | `746137a4` | Resubmitted "Refactored skinned mesh system to enable GPU skin support... | 重构蒙皮网格系统以支持GPU蒙皮。 |

### 维护评价

**综合评价：可能废弃，不推荐新项目使用。**

-   **创建与状态**：该插件于2022年9月创建，但其 `.uplugin` 元数据已明确标记为 **DEPRECATED (已弃用)**，并建议使用 `Detail Pose Model`。
-   **更新频率**：从近期的提交记录来看，最后一次实质性的功能性更新可能发生在很久之前。最近的提交全部是维护性清理，如修复编译警告、日志系统迁移和框架底层重构，表明其已进入维护生命周期末期。
-   **已知问题与限制**：主要限制是它已被官方弃用。其功能已由更现代的 `Detail Pose Model` 取代，新版本模型可能在易用性、性能或功能上有所改进。
-   **推荐**：**不推荐**在新项目中使用。对于新项目，请直接使用 `Detail Pose Model`。仅建议在维护基于此插件构建的旧项目时，才参考本文档。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NearestNeighborModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/NearestNeighborModel)（路径推断，具体文件需在源码中查找）