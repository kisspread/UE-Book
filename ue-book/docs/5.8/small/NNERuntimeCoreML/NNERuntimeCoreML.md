# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CoreML 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreML` (RuntimeAndProgram), `NNERuntimeCoreMLUtils` (RuntimeAndProgram), `NNERuntimeCoreMLEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 用途

本插件为 Unreal Engine 的神经网络引擎 (NNE) 提供了基于 Apple CoreML 框架的推理运行时后端。它允许 UE 项目在 Apple 平台（macOS、iOS 等）上直接调用 CoreML 进行神经网络模型的推理，从而充分利用 Apple 芯片的 CPU、GPU 和 NPU（神经网络处理器）硬件加速能力。它的存在解决了在 Apple 生态系统中缺乏原生、高性能神经网络推理运行时的问题，使得开发者可以将训练好的 CoreML 模型（`.mlmodel` 或 `.mlpackage`）无缝集成到 UE 项目中。

## 使用场景

- 你正在为 macOS 或 iOS 开发游戏或应用，并希望集成机器学习功能，例如风格迁移、物体检测或实时图像分割。
- 你有一个已经用 CoreML 工具（如 Create ML 或 coremltools）训练好的模型，并希望直接在 UE 项目中运行，避免跨平台转换的复杂性。
- 你希望应用能够自动选择在 Apple 设备上可用的最佳计算单元（CPU、GPU 或 NPU）来执行模型推理，以获得最佳性能和能效。

## 蓝图用法

此插件主要提供 C++ 运行时接口，用于在底层注册和管理 CoreML 推理引擎。在当前的源码中，**没有发现直接暴露给蓝图 `BlueprintCallable` 的函数**。通常，对神经网络模型的加载和推理操作是通过 NNE 提供的通用蓝图节点（如 `Load Model`、`Run Inference` 等）来完成的，这些节点会自动使用已注册的最佳运行时（包括 CoreML 运行时）。因此，开发者通常不需要直接调用本插件特定的蓝图节点。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeCoreML.h"
```

### 基本用法

核心用法是使用 NNE 的通用接口。首先，你需要一个有效的 `UNNEModelData` 对象，该对象通常是从 `.mlmodel` 或 `.mlpackage` 文件加载而来。然后，你可以查询并创建针对特定硬件后端的模型实例。本插件提供了三个主要的运行时类，对应不同的硬件加速级别。

```cpp
// 假设你已经有了一个加载好的 UNNEModelData* MyModelData
// 并且处于可以使用 CoreML 的平台 (WITH_NNE_RUNTIME_COREML 为 true)

// 1. 创建一个支持 CPU 和 GPU 的运行时实例
// UNNERuntimeCoreMLCpuGpu 是最常用的，它会在可能的情况下优先使用 GPU。
TObjectPtr<UNNERuntimeCoreMLCpuGpu> RuntimeCpuGpu = NewObject<UNNERuntimeCoreMLCpuGpu>();

// 2. 检查该运行时是否可以为你的模型数据创建 CPU 模型
if (RuntimeCpuGpu->CanCreateModelCPU(MyModelData) == UE::NNE::ECanCreateModelCPUStatus::Ok)
{
    // 3. 创建 CPU 模型
    TSharedPtr<UE::NNE::IModelCPU> ModelCPU = RuntimeCpuGpu->CreateModelCPU(MyModelData);

    // 4. 创建一个模型实例
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstanceCPU = ModelCPU->CreateModelInstanceCPU();

    // 5. 设置输入形状并运行推理（示例代码，实际数据需填充）
    TArray<UE::NNE::FTensorShape> InputShapes;
    // ... 填充 InputShapes ...
    ModelInstanceCPU->SetInputTensorShapes(InputShapes);

    TArray<UE::NNE::FTensorBindingCPU> InputBindings, OutputBindings;
    // ... 填充 InputBindings 和 OutputBindings 的内存视图 ...
    ModelInstanceCPU->RunSync(InputBindings, OutputBindings);
}
```

**来源文件**：`Engine/Plugins/Experimental/NNERuntimeCoreML/Source/NNERuntimeCoreML/Private/NNERuntimeCoreML.h`

### 进阶用法

你可以根据目标硬件选择更具体的运行时类：

- **UNNERuntimeCoreML**: 基础类，仅处理模型数据的验证和标识。
- **UNNERuntimeCoreMLCpuGpu**: 支持 CPU 和 GPU。这是通用的推荐选择。
- **UNNERuntimeCoreMLCpuGpuNpu**: 支持 CPU、GPU 和 NPU。如果你明确知道模型将运行在支持 NPU 的 Apple 设备上，并且模型兼容，可以使用此类以获得最佳硬件利用。

```cpp
// 如果希望使用 NPU
TObjectPtr<UNNERuntimeCoreMLCpuGpuNpu> RuntimeNPU = NewObject<UNNERuntimeCoreMLCpuGpuNpu>();
if (RuntimeNPU->CanCreateModelNPU(MyModelData) == UE::NNE::ECanCreateModelNPUStatus::Ok)
{
    TSharedPtr<UE::NNE::IModelNPU> ModelNPU = RuntimeNPU->CreateModelNPU(MyModelData);
    // ... 后续使用 IModelNPU 和 IModelInstanceNPU 接口进行推理 ...
}
```

**来源文件**：`Engine/Plugins/Experimental/NNERuntimeCoreML/Source/NNERuntimeCoreML/Private/NNERuntimeCoreML.h`, `Engine/Plugins/Experimental/NNERuntimeCoreML/Source/NNERuntimeCoreML/Private/NNERuntimeCoreMLModel.h`

## Demo 示例

以下是一个最小化、完整的 C++ 类，演示了如何在 Actor 中异步加载并运行一个 CoreML 模型。此示例假设项目已正确配置并启用了 NNE 和 NNERuntimeCoreML 插件。

**MyNeuralNetworkActor.h**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NeuralNetworkEngine.h" // 包含 NNE 核心头文件
#include "NNERuntimeCoreML.h"
#include "MyNeuralNetworkActor.generated.h"

UCLASS()
class MYPROJECT_API AMyNeuralNetworkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNeuralNetworkActor();

    // 用于加载模型的资产引用
    UPROPERTY(EditAnywhere, Category = "NNE")
    TObjectPtr<UNNEModelData> ModelDataAsset;

    // 模型实例指针
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;

    // 运行时实例
    TObjectPtr<UNNERuntimeCoreMLCpuGpu> Runtime;

    virtual void BeginPlay() override;

    // 一个简单的函数来触发推理
    UFUNCTION(BlueprintCallable, Category = "NNE")
    void RunSimpleInference();
};
```

**MyNeuralNetworkActor.cpp**
```cpp
// Fill out your copyright notice in the Description page of Project Settings.

#include "MyNeuralNetworkActor.h"
#include "NeuralNetworkEngine.h"

AMyNeuralNetworkActor::AMyNeuralNetworkActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNeuralNetworkActor::BeginPlay()
{
    Super::BeginPlay();

    // 确保资产已设置
    if (!ModelDataAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("AMyNeuralNetworkActor: ModelDataAsset is not set."));
        return;
    }

    // 创建运行时实例
    Runtime = NewObject<UNNERuntimeCoreMLCpuGpu>();

    // 检查并创建模型
    if (Runtime->CanCreateModelCPU(ModelDataAsset) == UE::NNE::ECanCreateModelCPUStatus::Ok)
    {
        TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(ModelDataAsset);
        if (Model)
        {
            ModelInstance = Model->CreateModelInstanceCPU();
            UE_LOG(LogTemp, Log, TEXT("CoreML model instance created successfully."));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("CoreML runtime cannot create a CPU model for the provided data."));
    }
}

void AMyNeuralNetworkActor::RunSimpleInference()
{
    if (!ModelInstance)
    {
        UE_LOG(LogTemp, Warning, TEXT("Model instance is not valid."));
        return;
    }

    // 此处仅为示例。你需要根据你的模型定义具体的输入/输出形状和绑定。
    TArray<UE::NNE::FTensorShape> InputShapes;
    // 假设模型期望一个 1x1x28x28 的输入 (类似 MNIST)
    InputShapes.Add(UE::NNE::FTensorShape::Make({1, 1, 28, 28}));

    // 设置输入形状 (这可能会改变内部缓冲区分配)
    if (ModelInstance->SetInputTensorShapes(InputShapes) != UE::NNE::IModelInstanceCPU::ESetInputTensorShapesStatus::Ok)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to set input tensor shapes."));
        return;
    }

    // 准备输入和输出绑定 (这里用空缓冲区示例)
    TArray<float> InputData(28 * 28, 0.0f); // 784 个零作为输入
    TArray<float> OutputData(10, 0.0f); // 假设输出是10个类别的概率

    TArray<UE::NNE::FTensorBindingCPU> InputBindings;
    InputBindings.Add(UE::NNE::FTensorBindingCPU{InputData.GetData(), InputData.Num() * sizeof(float)});

    TArray<UE::NNE::FTensorBindingCPU> OutputBindings;
    OutputBindings.Add(UE::NNE::FTensorBindingCPU{OutputData.GetData(), OutputData.Num() * sizeof(float)});

    // 同步运行推理
    UE::NNE::IModelInstanceCPU::ERunSyncStatus RunStatus = ModelInstance->RunSync(InputBindings, OutputBindings);
    if (RunStatus == UE::NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("CoreML inference completed successfully."));
        // 在这里处理 OutputData
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("CoreML inference failed."));
    }
}
```

## 模块依赖

从 `NNERuntimeCoreML.Build.cs` 分析，使用本插件的模块需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `NeuralNetworkEngine` | NNE 的核心模块，提供 `UNNEModelData`、`IModelCPU` 等基础接口和类型定义。这是必须的依赖。 |
| `NNERuntimeCoreML` | 本插件的核心运行时模块，提供 `UNNERuntimeCoreMLCpuGpu` 等具体实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 格式。 |
| 2026-03-20 | `2724fcee` | [NNERuntimeCoreML] Fix output copy to use logical size from MLMultiArray shape | 修复输出数据复制，改用 MLMultiArray 形状中的逻辑大小，解决了潜在的数据拷贝错误。 |
| 2026-02-09 | `7c2ef798` | [NNE] NNERuntimeCoreML add .mlpackage format support. | 为 NNERuntimeCoreML 添加了对 `.mlpackage` 格式的支持，功能扩展。 |
| 2026-01-28 | `5f766aee` | Fixed modules that does not support portable toolchain | 修复了不支持可移植工具链的模块问题。 |
| 2026-01-24 | `e793e61e` | Fixed more compile errors when using portable toolchain | 修复了使用可移植工具链时的更多编译错误。 |

### 维护评价

NNERuntimeCoreML 是一个相对年轻的插件，于 2025 年初创建，**目前处于实验性状态 (`IsExperimentalVersion=true`, `EnabledByDefault=false`)**。
从提交历史看，在创建后的一段时间内有持续的功能添加（如支持 `.mlpackage`）和重要的 bug 修复（如输出数据拷贝修复），表明它**仍在积极维护和改进中**。最近的提交（2026年）主要是基础设施和工具链的兼容性修复。
由于它仍是实验性功能，并且依赖于特定的 Apple CoreML 框架，其 API 和行为在未来版本中可能会发生变化。对于在 Apple 平台上需要高性能神经网络推理的项目，可以谨慎评估并使用，但需做好跟进引擎更新的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeCoreML/Source/NNERuntimeCoreMLTests)