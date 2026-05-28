# ML Deformer Vertex Delta Model

> Vertex Delta Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 顶点偏移模型 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `VertexDeltaModel` (Runtime), `VertexDeltaModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel) | |

## 用途

此插件是 **ML Deformer (机器学习变形器)** 框架的一个具体实现模型。它的核心功能是利用预先训练好的神经网络，来预测在动画过程中，由于骨骼变换（例如关节旋转）所导致的顶点位置偏移量（Delta）。简单来说，它比传统的线性蒙皮更精准，能够实时计算并应用类似“肌肉膨胀”、“衣物褶皱拉伸”等复杂的次级动画效果，极大地提升角色动画的真实感。

它解决的核心问题是：**如何在运行时，以高性能的方式，为角色网格体（Skeletal Mesh）添加基于机器学习的、高精度的次级形变**。

## 使用场景

- **高质量角色动画**：当你需要一个游戏角色在各种动画（如奔跑、格斗）中，皮肤、肌肉、衣物都能表现出真实的变形和拉伸感，而不是僵硬的骨骼蒙皮效果时。
- **实时动画修正**：在动画蓝图中，将ML Deformer节点串联到最终动画输出，实时修正网格体的顶点位置，无需美术师手动制作每一个变形状态的模型。
- **复杂的骨骼区域变形**：特别适用于肩部、臀部、膝盖等骨骼活动频繁、传统蒙皮难以处理自然形变的区域。

## 蓝图用法

该插件在运行时没有直接可调用的蓝图函数。它的核心交互发生在**编辑器内的资产设置**和**动画蓝图的图表中**。编辑器端的功能由其`EditorModel`和`Details`定制类提供。

### 核心资产

你需要创建并配置一个 **`UVertexDeltaModel`** 资产。该资产会作为ML Deformer节点的数据源，在动画蓝图中引用。

### 使用示例（蓝图描述）

1.  **创建模型资产**：在内容浏览器中右键 -> `Animation` -> `ML Deformer` -> `Vertex Delta Model`，创建资产。
2.  **配置模型**：打开该资产，在细节面板中设置：
    *   **Skeletal Mesh**：指定要应用变形的目标骨骼网格体。
    *   **Ground Truth**：设置用于训练的变形网格体序列（来自Alembic或几何缓存）。
    *   **Neural Network**：加载或生成用于预测的ONNX格式神经网络模型。
3.  **在动画蓝图中使用**：
    *   打开角色的**动画蓝图**。
    *   在**事件图表**或**动画图表**中，找到`Animation`类别。
    *   添加一个 `ML Deformer` 节点。
    *   将该节点的 `Deformer Model` 属性连接到你创建的 `UVertexDeltaModel` 资产。
    *   将该节点串联到动画管线的最终输出之前（通常在`Output Pose`节点之前）。

## C++ 用法

### 头文件引入

```cpp
#include "VertexDeltaModel.h" // 用于访问 UVertexDeltaModel 类
```

### 基本用法

在 C++ 中，你主要操作的是 `UVertexDeltaModel` 资产对象。它通常被动画蓝图中的 `UMLDeformerComponent` 引用。以下是如何在代码中获取和使用该模型的基本示例。

```cpp
// 假设你有一个指向 UMLDeformerComponent 的指针，通常在 Actor 或 AnimInstance 中获取。
if (UMLDeformerComponent* DeformerComponent = Actor->FindComponentByClass<UMLDeformerComponent>())
{
    // 设置要使用的顶点偏移模型
    if (UVertexDeltaModel* MyModel = LoadObject<UVertexDeltaModel>(nullptr, TEXT("/Game/Path/To/MyVertexDeltaModel")))
    {
        DeformerComponent->SetDeformerModel(MyModel);
        // 模型的训练和神经网络加载通常在编辑器中完成。
        // 运行时，组件会自动使用模型中训练好的网络进行顶点偏移预测。
    }
}
```

### 进阶用法

对于插件的开发者或希望进行深度定制的用户，理解其编辑器模型类是关键。`FVertexDeltaEditorModel` 负责在编辑器中协调训练过程和神经网络的加载。

```cpp
// 在编辑器工具或自动化脚本中，你可以调用训练流程
#include "VertexDeltaEditorModel.h"

// 获取一个模型资产的编辑器模型实例（通常由框架内部管理）
// 此处为示意，实际中框架会处理此创建过程
UE::VertexDeltaModel::FVertexDeltaEditorModel* EditorModel = ...; 

// 触发训练
ETrainingResult Result = EditorModel->Train();
if (Result == ETrainingResult::Success)
{
    UE_LOG(LogTemp, Log, TEXT("顶点偏移模型训练成功！"));
}

// 手动加载一个已有的ONNX网络文件到模型中
EditorModel->LoadNeuralNetworkFromOnnx(TEXT("D:/MLModels/trained_model.onnx"));
```

## Demo 示例

以下是一个最小的 C++ 类示例，展示如何创建一个 Actor，其组件使用 ML Deformer。

```cpp
// MyVertexDeltaActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "MyVertexDeltaActor.generated.h"

class UMLDeformerComponent;
class UVertexDeltaModel;

UCLASS()
class MYPROJECT_API AMyVertexDeltaActor : public AActor
{
    GENERATED_BODY()

public:
    AMyVertexDeltaActor();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<USkeletalMeshComponent> MeshComponent;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
    TObjectPtr<UMLDeformerComponent> DeformerComponent;

    // 在蓝图或编辑器中指定
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MLDeformer")
    TObjectPtr<UVertexDeltaModel> VertexDeltaModel;
};
```

```cpp
// MyVertexDeltaActor.cpp
#include "MyVertexDeltaActor.h"
#include "MLDeformerComponent.h"
#include "VertexDeltaModel.h"

AMyVertexDeltaActor::AMyVertexDeltaActor()
{
    PrimaryActorTick.bCanEverTick = false;

    // 创建骨骼网格体组件
    MeshComponent = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("Mesh"));
    RootComponent = MeshComponent;

    // 创建ML Deformer组件
    DeformerComponent = CreateDefaultSubobject<UMLDeformerComponent>(TEXT("MLDeformer"));
    DeformerComponent->SetupAttachment(MeshComponent);
}

void AMyVertexDeltaActor::BeginPlay()
{
    Super::BeginPlay();

    // 在运行时设置模型
    if (VertexDeltaModel && DeformerComponent)
    {
        DeformerComponent->SetDeformerModel(VertexDeltaModel);
    }
}
```

## 模块依赖

该插件的构建依赖以下相对独特的模块。使用该插件的项目模块需要添加这些依赖。

| 模块 | 用途 |
|---|---|
| `MLDeformer` | ML Deformer框架核心，提供基础类和接口。 |
| `NeuralNetworkInference` | 神经网络推理库，用于运行时执行ONNX模型预测。 |
| `GeometryCache` | 用于处理几何缓存（Alembic）数据，这是训练数据的来源之一。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 对MLDeformer进行代码清理，移除废弃的API，为5.8版本做准备。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏UE_LOG迁移为新的UE_LOGF格式。 |
| 2026-04-02 | `138d5376` | [Deformer Graph] Multiple fixes for Optimus runtime | 修复了与Deformer Graph（Optimus运行时）相关的多个问题。 |
| 2025-06-25 | `a9573a81` | ComputeFramework: Remove old deprecated functions from compute data providers. | 清理计算框架中数据提供者的废弃函数。 |
| 2025-06-20 | `35f8ecb8` | PythonFoundationPackages: Move Torch python requirements to separate PythonMLPackages plugin | 将PyTorch的Python依赖项迁移至独立的PythonMLPackages插件，影响ML Deformer的训练环境配置。 |

### 维护评价

**VertexDeltaModel** 作为 ML Deformer 框架的核心实现之一，于 **2022年9月** 随框架一同从实验性模块迁移并标记为 **Beta**。它**仍在活跃维护中**，最近的提交（2026年4月）主要集中在代码现代化、API清理和框架集成优化上，表明Epic Games仍在持续改进此功能。

**推荐使用**：对于需要高精度实时角色动画的项目，此插件是 **ML Deformer 的推荐模型之一**。尽管标记为Beta，但其功能稳定，且是Epic官方示例（如“`MLDeformer`”示例项目）的基础，有较好的文档和社区支持。需要注意的是，它通常需要额外的Python环境和离线训练流程。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/VertexDeltaModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)