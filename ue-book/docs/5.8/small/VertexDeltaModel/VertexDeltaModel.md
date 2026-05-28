# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 顶点偏移模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Compute Framework 数据接口） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

VertexDeltaModel 是 ML Deformer 框架的一种 GPU 神经网络变形模型实现。它使用基于 GPU 的神经网络（通过 NNE - Neural Network Engine）直接输出每个顶点的位置偏移量（vertex deltas），而非生成中间形态目标（morph targets）。

**核心特点**：
- **纯 GPU 推理**：所有神经网络推理都在 GPU 上执行，输出的顶点偏移缓冲区直接保留在 GPU 内存中
- **无 Morph Target**：不像 Neural Morph Model 那样生成 morph targets，而是直接输出顶点偏移
- **NNE 集成**：使用 Unreal 的 Neural Network Engine（NNE）运行 ORT DML 后端
- **示例性质**：源码注释表明该模型更多是一个 GPU 模型实现的示例，效率不如 Neural Morph Model

该模型适用于需要完全在 GPU 上完成神经网络推理的场景，避免了 CPU 到 GPU 的数据传输开销。

## 使用场景

- **GPU 优先的工作流**：当你的变形需求需要完全在 GPU 上完成，避免 CPU 回读
- **学习 GPU 神经网络**：作为 ML Deformer 框架中 GPU 模型实现的参考示例
- **Compute Framework 集成**：通过 Optimus/Deformer Graph 与 UE 的 Compute Framework 集成
- **简单变形需求**：适用于不需要复杂形态目标的直接顶点偏移场景

## 蓝图用法

### 核心属性

| 属性 | 说明 | 所在类 |
|---|---|---|
| `NumHiddenLayers` | 神经网络隐藏层数（1-10），越多越慢但能处理更复杂变形 | `UVertexDeltaModel` |
| `NumNeuronsPerLayer` | 每个隐藏层的神经元数（≥1），越多越慢但能处理更复杂变形 | `UVertexDeltaModel` |
| `NumIterations` | 训练迭代次数（≥1） | `UVertexDeltaModel` |
| `BatchSize` | 训练时每批次帧数（≥1） | `UVertexDeltaModel` |
| `LearningRate` | 训练学习率（0.000001 - 1.0） | `UVertexDeltaModel` |
| `NNEModel` | NNE 神经网络模型数据 | `UVertexDeltaModel` |
| `DeformerComponent` | 关联的变形器组件 | `UVertexDeltaGraphDataProvider` |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Execute` | 执行模型变形，传入模型权重 | `UVertexDeltaModelInstance` |
| `SetupInputs` | 设置神经网络输入（关节矩阵/曲线浮点数） | `UVertexDeltaModelInstance` |
| `IsValidForDataProvider` | 检查模型实例是否可用于数据提供者 | `UVertexDeltaModelInstance` |
| `CheckCompatibility` | 检查骨骼网格体组件的兼容性 | `UVertexDeltaModelInstance` |
| `GetNNEModelInstanceRDG` | 获取 NNE RDG 模型实例 | `UVertexDeltaModelInstance` |
| `GetOutputRDGBuffer` | 获取输出顶点偏移 RDG 缓冲区 | `UVertexDeltaModelInstance` |

### 使用示例（蓝图描述）

1. **配置训练参数**：
   - 创建或编辑 `UVertexDeltaModel` 资产
   - 在 "Training Settings" 分类下设置 `NumHiddenLayers`、`NumNeuronsPerLayer`、`NumIterations`、`BatchSize`、`LearningRate`

2. **通过 Deformer Graph 使用**：
   - VertexDeltaModel 通过 `UVertexDeltaGraphDataInterface` 与 Optimus Deformer Graph 集成
   - 在 Deformer Graph 中使用 VertexDeltaModelData 节点获取顶点偏移
   - 通过 `UVertexDeltaGraphDataProvider` 将 MLDeformerComponent 绑定到图

3. **调试可视化**（已废弃）：
   - 原本通过 `UDEPRECATED_VertexDeltaGraphDebugDataInterface` 进行调试
   - 现在应使用 `UMLDeformerGraphDebugDataInterface`

## C++ 用法

### 头文件引入

```cpp
#include "VertexDeltaModel.h"
#include "VertexDeltaModelInstance.h"
#include "VertexDeltaGraphDataInterface.h"
```

### 基本用法

创建和配置 VertexDeltaModel：

```cpp
// 创建模型资产
UVertexDeltaModel* VertexDeltaModel = NewObject<UVertexDeltaModel>();

// 配置训练参数（仅编辑器）
#if WITH_EDITORONLY_DATA
VertexDeltaModel->NumHiddenLayers = 3;        // 隐藏层数
VertexDeltaModel->NumNeuronsPerLayer = 256;    // 每层神经元数
VertexDeltaModel->NumIterations = 10000;       // 训练迭代次数
VertexDeltaModel->BatchSize = 128;             // 批次大小
VertexDeltaModel->LearningRate = 0.001f;       // 学习率
#endif

// 设置 NNE 模型数据
VertexDeltaModel->SetNNEModelData(NNEModelData);

// 检查是否已训练
bool bTrained = VertexDeltaModel->IsTrained();
```

### 进阶用法

通过 ModelInstance 执行推理并获取输出缓冲区：

```cpp
// 获取模型实例
UVertexDeltaModel* Model = Cast<UVertexDeltaModel>(DeformerModel);
UVertexDeltaModelInstance* Instance = Model->CreateModelInstance(DeformerComponent);

// 设置输入数据
bool bInputSetup = Instance->SetupInputs();

// 执行变形（ModelWeight 通常为 0.0 - 1.0）
Instance->Execute(1.0f);

// 获取 NNE RDG 模型实例用于自定义推理
UE::NNE::IModelInstanceRDG* RDGModelInstance = Instance->GetNNEModelInstanceRDG();

// 获取输出顶点偏移缓冲区（RDG 缓冲区）
TRefCountPtr<FRDGPooledBuffer> VertexDeltaBuffer = Instance->GetOutputRDGBuffer();

// 检查 RDG 缓冲区描述
FRDGBufferDesc BufferDesc;
TArray<UE::NNE::FTensorDesc> OutputTensorDescs;
bool bFlatBuffer = Instance->GetRDGVertexBufferDesc(OutputTensorDescs, BufferDesc);
```

通过 Compute Framework Data Interface 集成：

```cpp
// 创建数据提供者
UVertexDeltaGraphDataProvider* DataProvider = NewObject<UVertexDeltaGraphDataProvider>();
DataProvider->DeformerComponent = MyDeformerComponent;

// 数据提供者会自动创建 FVertexDeltaGraphDataProviderProxy
// 用于在渲染线程上执行 GPU 推理
```

## Demo 示例

### 最小 GPU 神经网络变形示例

```cpp
// MyVertexDeltaDeformerComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "MyVertexDeltaDeformerComponent.generated.h"

class UMLDeformerComponent;
class UVertexDeltaModel;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyVertexDeltaDeformerComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyVertexDeltaDeformerComponent();

    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

    /** 更新变形器权重 */
    UFUNCTION(BlueprintCallable, Category = "Deformer")
    void SetDeformerWeight(float InWeight);

protected:
    /** ML Deformer 组件引用 */
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Deformer")
    TObjectPtr<UMLDeformerComponent> MLDeformerComponent;

    /** Vertex Delta Model 资产 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Deformer")
    TObjectPtr<UVertexDeltaModel> VertexDeltaModel;

    /** 当前变形权重 */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Deformer", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float DeformerWeight = 1.0f;
};
```

```cpp
// MyVertexDeltaDeformerComponent.cpp
#include "MyVertexDeltaDeformerComponent.h"
#include "MLDeformerComponent.h"
#include "VertexDeltaModel.h"
#include "VertexDeltaModelInstance.h"

UMyVertexDeltaDeformerComponent::UMyVertexDeltaDeformerComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyVertexDeltaDeformerComponent::BeginPlay()
{
    Super::BeginPlay();

    // 查找或创建 ML Deformer 组件
    MLDeformerComponent = GetOwner()->FindComponentByClass<UMLDeformerComponent>();
    if (!MLDeformerComponent)
    {
        MLDeformerComponent = NewObject<UMLDeformerComponent>(GetOwner());
        MLDeformerComponent->RegisterComponent();
    }

    // 设置模型
    if (VertexDeltaModel && MLDeformerComponent)
    {
        MLDeformerComponent->SetDeformerAsset(VertexDeltaModel);
    }
}

void UMyVertexDeltaDeformerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    // 更新变形器权重
    if (MLDeformerComponent)
    {
        MLDeformerComponent->SetWeight(DeformerWeight);
    }
}

void UMyVertexDeltaDeformerComponent::SetDeformerWeight(float InWeight)
{
    DeformerWeight = FMath::Clamp(InWeight, 0.0f, 1.0f);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine，用于加载和运行神经网络模型 |
| `ComputeFramework` | UE 的 GPU 计算框架，提供 Data Interface/Provider 架构 |
| `MLDeformer` | ML Deformer 框架基础，提供 Model/ModelInstance 基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | UE 5.8 动画废弃代码清理，涉及 MLDeformer |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF（格式化日志） |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | Deformer Graph 的 Optimus 运行时多项修复 |
| 2025-06-25 | `a9573a81` | ComputeFramework: Remove old deprecated functions from compute data providers. | ComputeFramework 移除旧的废弃函数 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 Torch Python 依赖移至独立的 PythonMLPackages 插件 |

### 维护评价

**状态：维护中**

- **创建时间**：2022 年 9 月，从 Experimental 移出并标记为 Beta
- **最近更新**：2026 年 4 月有活跃更新，主要涉及 UE 5.8 适配、代码清理和运行时修复
- **Beta 状态**：该插件仍处于 Beta 状态，API 可能变化
- **已知限制**：
  - 源码注释指出效率不如 Neural Morph Model
  - 标记为示例性质的 GPU 实现
  - 已有部分类被废弃（Debug Data Interface），需迁移到 MLDeformer 核心类
- **推荐程度**：适合学习 GPU 神经网络实现或需要纯 GPU 工作流的场景。生产环境建议评估 Neural Morph Model 作为替代方案

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [ML Deformer 主文档](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer)