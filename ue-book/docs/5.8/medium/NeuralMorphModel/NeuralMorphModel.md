# ML Deformer Neural Morph Model

> Neural Morph Model for the ML Deformer Framework

| 属性 | 值 |
|---|---|
| 中文名 | 神经形态模型 |
| 分类 | Animation |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（训练模型资产） |
| 模块 | `NeuralMorphModel` (Runtime), `NeuralMorphModelEditor` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-09-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel) | |

## 用途

NeuralMorphModel 是 ML Deformer 框架中的一个核心模型插件。它通过训练一个专门的神经网络，生成一组高度压缩的“形态目标”（Morph Targets），用于在运行时近似基于骨骼旋转和/或动画曲线输入的目标顶点位移。

该插件解决的问题是：在需要高质量、实时的角色肌肉/骨骼变形（如皮肤褶皱、肌肉膨胀）时，传统线性混合蒙皮（LBS）效果不佳，而完整的顶点动画或物理模拟开销过大。NeuralMorphModel 通过机器学习找到一种高效的数据驱动近似方法，能够在运行时以较低的CPU开销（神经网络推理）驱动GPU压缩的形态目标，从而获得接近训练数据的高质量变形效果。

## 使用场景

- **高品质游戏角色动画**：你的角色模型需要表现复杂的肌肉运动、面部表情（基于骨骼）或衣物褶皱，且需要在目标平台（如主机、PC）上保持高帧率。
- **性能敏感的实时应用**：你希望在运行时获得高质量的变形效果，但不想承担完整物理模拟或每帧CPU蒙皮的巨大开销。
- **数据驱动的工作流**：你已经有高质量的变形参考动画（如从Maya、Houdini导出的顶点动画），希望机器学习模型来“学习”这些变形规律。

## 蓝图用法

该插件的核心功能主要通过 `UMLDeformerComponent` 在运行时自动调用，而非直接通过蓝图节点操作。蓝图中主要接触的是模型的配置属性，这些属性通常在资产编辑器中设置。

### 核心节点

由于该插件的核心逻辑是运行时的神经网络推理，因此没有大量 `BlueprintCallable` 函数。主要接口是通过 `UNeuralMorphModel` 资产暴露的属性，以及被 `UMLDeformerComponent` 使用的实例。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetSkinningMode` | 设置模型训练所用的蒙皮模式（线性/对偶四元数） | `UNeuralMorphModel` |
| `UpdateMissingGroupNames` | 用于修复和更新骨骼组或曲线组中可能缺失的名称 | `UNeuralMorphModel` |

### 使用示例（蓝图描述）

在资产编辑器（如 `UMLDeformerAsset`）中，你可以找到 `NeuralMorphModel` 的详细设置面板。
1.  **设置训练参数**：在 `Training Settings` 类别下，配置 `Mode`（局部/全局）、`Num Morphs Per Bone/Curve/Group`、`Num Iterations` 等。
2.  **定义组**：在 `Bone Groups` 或 `Curve Groups` 数组中，添加组，并在每个组中指定相关的骨骼或曲线。这适用于多个骨骼/曲线共同影响一个变形的情况。
3.  **启用骨骼遮罩**：在局部模式下，可以勾选 `b Enable Bone Masks` 来启用基于蒙皮权重的区域遮罩，这有助于提升性能并使变形更局部化。
4.  **训练模型**：配置好所有参数后，使用 ML Deformer 框架的训练功能启动训练过程。训练好的网络权重会被序列化到资产中。
5.  **运行时使用**：将训练好的 `UMLDeformerAsset` 资产赋予 `UMLDeformerComponent`，组件会在初始化时自动创建 `UNeuralMorphModelInstance` 并在每帧执行推理。

## C++ 用法

### 头文件引入

```cpp
#include "NeuralMorphModel.h"
#include "MLDeformerMorphModel.h" // 基类
#include "MLDeformerComponent.h"  // 组件
```

### 基本用法

以下代码演示如何创建和使用一个 Neural Morph Model 实例进行推理。
*来源：基于 `UNeuralMorphModel` 和 `UNeuralMorphModelInstance` 的公共接口推断。*

```cpp
// 假设你已经有一个加载好的 UNeuralMorphModel 资产指针 (NeuralMorphModelAsset)
// 和一个有效的 UMLDeformerComponent 指针 (MLDeformerComponent)

// 1. 创建模型实例
UNeuralMorphModelInstance* ModelInstance = NeuralMorphModelAsset->CreateModelInstance(MLDeformerComponent);

// 2. 初始化实例，通常发生在组件初始化时
ModelInstance->Init(MLDeformerComponent->GetSkeletalMeshComponent());

// 3. 在每帧的动画更新中执行
// 设置曲线输入 (如果模型使用了曲线)
bool bSuccess = ModelInstance->SetupInputs();
if (bSuccess)
{
    // 4. 执行神经网络推理，权重通常由动画蓝图控制
    ModelInstance->Execute(1.0f); // 1.0f 为变形权重
}
```

### 进阶用法

可以手动访问底层的神经网络实例以获得更精细的控制。
*来源：基于 `UNeuralMorphNetwork` 和 `UNeuralMorphNetworkInstance` 的接口。*

```cpp
// 从模型中获取神经网络对象
const UNeuralMorphNetwork* NeuralNetwork = NeuralMorphModelAsset->GetNeuralMorphNetwork();
if (NeuralNetwork && !NeuralNetwork->IsEmpty())
{
    // 为每个需要并行执行的组件创建一个独立的网络实例
    UNeuralMorphNetworkInstance* NetworkInstance = NeuralNetwork->CreateInstance();

    // 填充输入 (骨骼旋转变换、曲线值等，具体方式复杂，通常由 ModelInstance 内部处理)
    TArrayView<float> Inputs = NetworkInstance->GetInputs();
    // ... 填充Inputs数据 ...

    // 执行一次推理
    NetworkInstance->Run();

    // 获取输出的形态目标权重
    TArrayView<const float> MorphWeights = NetworkInstance->GetOutputs();
    // 将 MorphWeights 应用到顶点变形计算中 ...
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何从模型资产中获取网络信息。
*注意：完整的训练和推理流程集成在 MLDeformer 框架内，此示例仅用于展示直接 API 的访问。*

**NeuralMorphDemoActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NeuralMorphDemoActor.generated.h"

class UNeuralMorphModel;
class UNeuralMorphNetwork;

UCLASS()
class ANeuralMorphDemoActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Demo")
    TSoftObjectPtr<UNeuralMorphModel> NeuralMorphModelAsset;

    void PrintNetworkInfo() const;

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UNeuralMorphNetwork> LoadedNetwork;
};
```

**NeuralMorphDemoActor.cpp**
```cpp
#include "NeuralMorphDemoActor.h"
#include "NeuralMorphModel.h"
#include "NeuralMorphNetwork.h"
#include "Engine/AssetManager.h"

void ANeuralMorphDemoActor::BeginPlay()
{
    Super::BeginPlay();
    PrintNetworkInfo();
}

void ANeuralMorphDemoActor::PrintNetworkInfo() const
{
    if (!NeuralMorphModelAsset.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("NeuralMorphModelAsset is not valid."));
        return;
    }

    const UNeuralMorphModel* Model = NeuralMorphModelAsset.Get();
    const UNeuralMorphNetwork* Network = Model->GetNeuralMorphNetwork();

    if (!Network || Network->IsEmpty())
    {
        UE_LOG(LogTemp, Warning, TEXT("Neural Morph Network is empty or not loaded."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("=== Neural Morph Network Info ==="));
    UE_LOG(LogTemp, Log, TEXT("Mode: %s"), Network->GetMode() == ENeuralMorphMode::Local ? TEXT("Local") : TEXT("Global"));
    UE_LOG(LogTemp, Log, TEXT("Num Bones: %d"), Network->GetNumBones());
    UE_LOG(LogTemp, Log, TEXT("Num Curves: %d"), Network->GetNumCurves());
    UE_LOG(LogTemp, Log, TEXT("Num Main Inputs: %d"), Network->GetNumMainInputs());
    UE_LOG(LogTemp, Log, TEXT("Num Main Outputs: %d"), Network->GetNumMainOutputs());
    UE_LOG(LogTemp, Log, TEXT("Num Groups: %d"), Network->GetNumGroups());
    UE_LOG(LogTemp, Log, TEXT("Num Morphs Per Bone (Local): %d"), Network->GetNumMorphsPerBone());
    UE_LOG(LogTemp, Log, TEXT("Num Total Morphs (Global): %d"), Network->GetNumOutputs()); // Global模式下总输出即为总形态目标数
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MLDeformerFramework` | 核心框架，提供模型、组件和训练的基类。 |
| `NNE` | Neural Network Engine， 提供通用的神经网络模型加载和推理接口。 |
| `RigLogic` | 用于处理骨骼映射和输入数据转换。 |
| `MeshDescription` | 处理网格体数据，用于生成形态目标。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `1d7ad320` | UE 5.8 Animation deprecation clean up (CL 8/10): MLDeformer | 针对5.8版本的动画废弃清理，涉及MLDeformer框架。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从UE_LOG迁移到UE_LOGF。 |
| 2025-07-10 | `9803c443` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 在源文件中添加内联生成代码的宏，优化编译。 |
| 2025-06-27 | `6a731b96` | [MLDeformer] Crash fix when pasting a list of bones in the Neural Morph Model when there is no skele | 修复了在神经形态模型中粘贴骨骼列表时若无骨骼会导致崩溃的问题。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 继续添加内联生成代码的宏。 |

### 维护评价

该插件自2022年9月从实验性功能移出并标记为Beta，至今约4年。从提交历史看，最近在2026年4月仍有更新，表明其处于**活跃维护**状态。更新内容主要包括：跟随引擎大版本的清理、编译优化和关键Bug修复。

需要注意的是，神经网络推理部分在 **5.4 版本经历了重大重构**，从自定义的 `UNeuralMorphMLP` 迁移到了更通用的 `NNE (Neural Network Engine)` 框架。旧的 `UNeuralMorphMLP` 和 `UNeuralMorphMLPLayer` 类已被标记为废弃（`UE_DEPRECATED(5.4, ...)`）。因此，**新代码应避免使用这些已废弃的类**，而应通过 `UNeuralMorphNetwork` 的 `GetMainModel()` 和 `GetGroupModel()` 接口访问 NNE 模型。

**推荐使用**：该插件是 Epic 官方 ML Deformer 框架的核心组件之一，文档相对齐全，持续维护，并且是创建高质量实时角色变形的推荐方案之一。只要你的项目需求与之匹配，可以放心使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/using-the-machine-learning-deformer-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/MLDeformer/NeuralMorphModel/Tests) （如果存在）