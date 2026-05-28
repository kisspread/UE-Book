# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 顶点增量模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、Deformer Graph） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

VertexDeltaModel 是 UE5 ML Deformer 框架的一个具体实现。它使用一个**完全运行在 GPU 上**的神经网络，直接输出每个顶点的位移增量（Delta），而不是生成传统的 Morph Target。

其核心思想是：神经网络接收骨骼变换和动画曲线作为输入，然后为网格体的每个顶点计算一个三维位移向量。这些增量直接写入一个 GPU 缓冲区，并在 Optimus 变形图中作为输入使用。

**为什么存在？**
- **示例与参考**: 官方注释指出，此模型主要用作如何实现**纯 GPU 模型**的示例。它证明了在 GPU 上进行实时神经网络推理的可行性。
- **性能考量**: 官方也明确说明，它的效率不如 Neural Morph Model（该模型在 CPU 上运行）。因此，它通常用作学习和技术验证，而不是追求极致性能的首选方案。
- **无缝 GPU 流水线**: 由于神经网络推理和顶点位移计算都在 GPU 上完成，避免了 CPU-GPU 数据交换，为纯 GPU 工作流提供了基础。

## 使用场景

- **学习 ML Deformer 框架**: 如果你想了解如何将神经网络集成到 UE 的变形管线中，这是一个很好的起点。它的代码结构清晰，专注于展示 GPU 推理和 Compute Framework 集成。
- **原型开发与验证**: 当你想要快速测试一个新的、简单的神经网络架构是否能驱动骨骼动画时，可以基于此模型进行修改。
- **纯 GPU 工作流**: 如果你的项目对 CPU-GPU 数据同步特别敏感，并且愿意在变形精度和性能上做出权衡，可以考虑使用。
- **不需要 Morph Target**: 传统的 Morph Target 资产需要预生成和存储。VertexDeltaModel 直接计算位移，避免了 Morph Target 资产的创建和管理，但每次推理都需要实时计算。

## 蓝图用法

该插件主要通过编辑器属性和资产进行配置，直接暴露给蓝图的函数和属性较少。

### 核心资产

| 资产类型 | 说明 |
|---|---|
| `UMLDeformerAsset` | 包含 `UVertexDeltaModel` 数据的 ML 变形器资产。在编辑器中创建和训练。 |
| `UMLDeformerComponent` | 将 `UMLDeformerAsset` 应用到 `USkeletalMeshComponent` 的组件。 |
| `UOptimusDeformerGraph` | 用于驱动该模型的 Optimus 变形图。插件会提供默认的图资产路径。 |

### 使用示例（蓝图描述）

1.  **创建资产**: 在内容浏览器中右键 -> Animation -> Machine Learning Deformer Asset。
2.  **编辑资产**: 打开创建的资产，选择模型类型为“Vertex Delta Model”。在细节面板中配置神经网络参数（如隐藏层数、神经元数量等）。
3.  **准备数据**: 在 ML Deformer 资产编辑器中，指定源（Source）和目标（Target）的 Skeletal Mesh，并准备好用于训练的动画序列。
4.  **训练模型**: 点击“Train”按钮。训练过程在 GPU 上进行，完成后模型数据（NNE Model Data）会被保存到资产中。
5.  **应用组件**: 在你的角色蓝图中，为目标 Skeletal Mesh Component 添加一个 `UMLDeformerComponent`。将其 `Deformer Asset` 属性设置为刚刚创建并训练好的资产。
6.  **运行**: 游戏运行时，组件会自动加载模型并实时应用 GPU 变形。

## C++ 用法

### 头文件引入

```cpp
#include "VertexDeltaModel.h"
#include "VertexDeltaModelInstance.h"
// 如果需要处理数据接口，引入相应的头文件
#include "VertexDeltaGraphDataInterface.h"
```

### 基本用法

获取一个已训练的 `UVertexDeltaModel` 的实例，并检查其状态。

```cpp
// 假设你有一个 UMLDeformerComponent* DeformerComponent
if (DeformerComponent)
{
    UMLDeformerModel* Model = DeformerComponent->GetDeformerModel();
    UVertexDeltaModel* VertexDeltaModel = Cast<UVertexDeltaModel>(Model);
    
    if (VertexDeltaModel)
    {
        // 检查模型是否已训练
        bool bIsTrained = VertexDeltaModel->IsTrained();
        UE_LOG(LogTemp, Log, TEXT("Vertex Delta Model Trained: %s"), bIsTrained ? TEXT("Yes") : TEXT("No"));
        
        // 获取神经网络参数（仅在编辑器下有效）
#if WITH_EDITORONLY_DATA
        int32 HiddenLayers = VertexDeltaModel->GetNumHiddenLayers();
        int32 NeuronsPerLayer = VertexDeltaModel->GetNumNeuronsPerLayer();
        UE_LOG(LogTemp, Log, TEXT("Network: %d layers, %d neurons per layer"), HiddenLayers, NeuronsPerLayer);
#endif
    }
}
```
*（代码思路来源于对 `UVertexDeltaModel` 类成员和 `UMLDeformerComponent` 使用逻辑的推断）*

### 进阶用法

直接访问神经网络推理实例和输出缓冲区。这通常在自定义 Compute Data Provider 中完成。

```cpp
#include "VertexDeltaModelInstance.h"

// 在某个继承自 FVertexDeltaGraphDataProviderProxy 或类似 ComputeDataProviderRenderProxy 的类中
void MyCustomDataProvider::GatherDispatchData(FDispatchData const& InDispatchData)
{
    // 假设你已经持有一个 UVertexDeltaModelInstance* ModelInstance
    if (ModelInstance)
    {
        // 获取神经网络 RDG 模型实例，用于调度推理
        UE::NNE::IModelInstanceRDG* NNEModelInstance = ModelInstance->GetNNEModelInstanceRDG();
        
        // 获取包含顶点增量数据的输出缓冲区，用于后续着色器使用
        TRefCountPtr<FRDGPooledBuffer> VertexDeltaBuffer = ModelInstance->GetOutputRDGBuffer();
        
        if (NNEModelInstance && VertexDeltaBuffer)
        {
            // ... 在这里配置 NNE 的输入，并将 VertexDeltaBuffer 作为输出绑定到后续的 Deformer Graph 节点
        }
    }
}
```
*（代码逻辑来源于对 `UVertexDeltaModelInstance` 接口和 `FVertexDeltaGraphDataProviderProxy` 功能的分析）*

## Demo 示例

一个最小化的示例，展示如何在代码中引用和使用 `UVertexDeltaModel`。

```cpp
// MyVertexDeltaActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyVertexDeltaActor.generated.h"

class USkeletalMeshComponent;
class UMLDeformerComponent;
class UMLDeformerAsset;

UCLASS()
class AMyVertexDeltaActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyVertexDeltaActor();

    virtual void BeginPlay() override;

protected:
    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    USkeletalMeshComponent* MeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
    UMLDeformerComponent* DeformerComponent;

    // 在编辑器中指定一个已经训练好的、使用 VertexDeltaModel 的资产
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ML Deformer")
    UMLDeformerAsset* DeformerAsset;

    // 开启/关闭变形效果
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ML Deformer", meta = (ClampMin = "0.0", ClampMax = "1.0"))
    float DeformerWeight = 1.0f;
};

// MyVertexDeltaActor.cpp
#include "MyVertexDeltaActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "MLDeformerComponent.h"

AMyVertexDeltaActor::AMyVertexDeltaActor()
{
    PrimaryActorTick.bCanEverTick = true;

    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    DeformerComponent = CreateDefaultSubobject<UMLDeformerComponent>(TEXT("Deformer"));
    DeformerComponent->SetupAttachment(MeshComponent);
}

void AMyVertexDeltaActor::BeginPlay()
{
    Super::BeginPlay();

    if (DeformerComponent && DeformerAsset)
    {
        // 将资产分配给组件
        DeformerComponent->SetDeformerAsset(DeformerAsset);
        // 设置初始变形权重
        DeformerComponent->SetWeight(DeformerWeight);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 提供神经网络推理（NNE）运行时接口，特别是 GPU RDG 接口 (`IModelInstanceRDG`)。 |
| `MLDeformerFramework` | 提供 ML Deformer 的核心基类，如 `UMLDeformerModel`, `UMLDeformerModelInstance`, `UMLDeformerComponent` 等。 |
| `ComputeFramework` / `Optimus` | 用于构建和执行基于 GPU 的 Compute Graph (Deformer Graph)。`UVertexDeltaGraphDataInterface` 继承自 `UOptimusComputeDataInterface`。 |
| `RenderCore`, `RHI` | 提供底层渲染资源（如 `FRDGBuffer`, `FRHIShaderResourceView`）的管理接口。 |
| `GeometryCache` | 因为 `UVertexDeltaModel` 继承自 `UMLDeformerGeomCacheModel`，可能涉及与几何缓存的比较或数据转换。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 清理 ML Deformer 中的废弃 API，为 5.8 版本做准备。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 UE_LOG 宏迁移到新的 UE_LOGF 宏。 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复 Optimus（变形图）运行时的多个问题。 |
| 2025-06-25 | `a9573a81` | ComputeFramework: Remove old deprecated functions from compute data providers. | 从 Compute Data Provider 中移除旧的废弃函数。 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将 PyTorch 等 Python 依赖移动到独立的 PythonMLPackages 插件。 |

### 维护评价

- **活跃维护**: 从提交历史看，该插件在过去两年内（特别是 2026 年）有**频繁的维护性更新**，包括 API 清理、日志迁移和框架修复。
- **框架核心部分**: 作为 Epic 官方 ML Deformer 框架的一部分，它会跟随引擎主版本进行更新和适配。
- **实验性状态**: 从首次提交信息（“marked as beta”）和 `.uplugin` 中的 `IsBetaVersion` 字段（推断）来看，它仍被标记为实验性或 Beta 功能。
- **代码健康度**: 近期提交侧重于清理（如移除废弃函数）和兼容性，而非新功能开发，表明代码正在趋于稳定。
- **推荐使用**: **推荐用于学习和实验**。对于生产环境，如果性能是关键，应优先考虑 Neural Morph Model。使用时需注意其 Beta 状态可能带来的未来 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Runtime/Engine/Automation/MLDeformer) (框架通用测试)