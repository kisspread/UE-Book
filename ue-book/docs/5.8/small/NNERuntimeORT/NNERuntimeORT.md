# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 Unreal Engine 5 神经网络引擎 (NNE) 的一个后端运行时实现，它使用 ONNX Runtime 库来执行 ONNX 格式的神经网络模型。这个插件的主要目的是为 UE5 提供一个高性能、跨平台的神经网络推理引擎，支持 CPU 和 GPU（通过 DirectML）两种加速方式。

简单来说，它解决了如何在 Unreal Engine 中高效运行 ONNX 模型的问题。NNE 本身是一个抽象层，而 NNERuntimeORT 是其中一个具体的、基于 ONNX Runtime 的实现。这使得开发者可以训练模型，导出为 ONNX 格式，然后在 UE5 中通过统一的 NNE 接口加载并运行，无需关心底层的具体执行细节。

## 使用场景

- 你在做一个需要实时神经网络推理的游戏或应用，比如风格迁移、物体检测、图像分割。
- 你有一个用 PyTorch 或 TensorFlow 训练的模型，可以导出为 ONNX 格式。
- 你希望在 Windows、Linux 或 macOS 上运行模型，并且希望利用 CPU 或支持 DirectML 的 GPU 进行加速。
- 你需要一个官方支持的、与引擎深度集成的推理后端，而不是集成第三方 SDK。

## 蓝图用法

该插件本身主要提供 C++ 接口和 NNE 运行时后端，并不直接暴露大量蓝图节点。其功能通过 NNE 插件的蓝图接口间接使用。开发者通常通过 NNE 的蓝图 API（如加载模型、创建模型实例、设置输入数据、运行推理）来使用，而 NNERuntimeORT 作为其中一个可选的运行时后端被自动识别和使用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRuntimeName` | 返回运行时的名称标识（例如 "NNERuntimeORTCpu" 或 "NNERuntimeORTDml"） | `UNNERuntimeORTCpu`, `UNNERuntimeORTDmlProxy` |
| `CanCreateModelData` | 检查是否能从给定的文件数据创建模型数据 | `UNNERuntimeORTCpu`, `UNNERuntimeORTDmlProxy` |
| `CreateModelData` | 从文件数据创建模型数据 | `UNNERuntimeORTCpu`, `UNNERuntimeORTDmlProxy` |
| `CanCreateModelCPU` | 检查是否能从模型数据创建 CPU 模型实例 | `UNNERuntimeORTCpu` |
| `CreateModelCPU` | 从模型数据创建 CPU 模型实例 | `UNNERuntimeORTCpu` |
| `CanCreateModelGPU` | 检查是否能从模型数据创建 GPU 模型实例（仅 DirectML） | `UNNERuntimeORTDmlProxy` |
| `CreateModelGPU` | 从模型数据创建 GPU 模型实例（仅 DirectML） | `UNNERuntimeORTDmlProxy` |

### 使用示例（蓝图描述）

由于是运行时后端，蓝图中不直接调用 NNERuntimeORT 的函数。典型的使用流程是：
1.  **加载模型**: 使用 `UNNEModelData::LoadModel` 节点（来自 NNE 插件），指定 ONNX 文件。
2.  **创建模型实例**: 使用 `UNNEModelData::CreateModelInstanceCPU` 或 `CreateModelInstanceGPU` 节点。NNE 系统会自动选择一个可用的运行时（如 NNERuntimeORT）来执行创建。
3.  **设置输入**: 使用模型实例的 `SetInputTensorData` 节点设置输入数据。
4.  **运行推理**: 使用模型实例的 `RunSync` 或 `RunAsync` 节点执行推理。
5.  **获取输出**: 使用模型实例的 `GetOutputTensorData` 节点获取输出结果。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeORT.h" // 包含运行时类定义
#include "NNE.h" // 包含 NNE 核心接口
#include "NNERuntimeCPU.h" // 包含 CPU 模型接口
```

### 基本用法

以下是基于源码推断的典型使用流程。注意：在实际应用中，你通常通过 NNE 的通用接口 (`UNNEModelData`) 来交互，而 NNERuntimeORT 在后台工作。这里的示例展示了底层可能的 C++ 交互。

**场景：使用 CPU 运行时加载并运行一个 ONNX 模型。**

```cpp
// 步骤 1: 获取 NNERuntimeORT CPU 运行时
// 通常通过 NNE 模块的 GetRuntime 接口，按名称或 GUID 获取。
TArray<TWeakObjectPtr<INNERuntime>> Runtimes = UE::NNE::Get()->GetAllRuntimes();
TWeakObjectPtr<INNERuntime> RuntimeORTCpu = Runtimes.FindByPredicate([](const TWeakObjectPtr<INNERuntime>& Runtime) {
    return Runtime.IsValid() && Runtime->GetRuntimeName() == TEXT("NNERuntimeORTCpu");
});

if (!RuntimeORTCpu.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("NNERuntimeORTCpu runtime not available."));
    return;
}

// 步骤 2: 创建模型数据
// 假设我们有一段 ONNX 模型的二进制数据
TArray64<uint8> ModelFileData; // 填充你的 .onnx 文件数据
TMap<FString, TConstArrayView64<uint8>> AdditionalFiles; // ONNX 模型可能需要的外部数据文件
if (RuntimeORTCpu->CanCreateModelData(TEXT("onnx"), ModelFileData, AdditionalFiles, FGuid(), nullptr) != INNERuntime::ECanCreateModelDataStatus::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Cannot create model data from provided ONNX data."));
    return;
}
TSharedPtr<UE::NNE::FSharedModelData> ModelData = RuntimeORTCpu->CreateModelData(TEXT("onnx"), ModelFileData, AdditionalFiles, FGuid(), nullptr);

// 步骤 3: 创建模型实例
if (RuntimeORTCpu->CanCreateModelCPU(ModelData.Get()) != INNERuntime::ECanCreateModelCPUStatus::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Cannot create CPU model from model data."));
    return;
}
TSharedPtr<UE::NNE::IModelCPU> Model = RuntimeORTCpu->CreateModelCPU(ModelData.Get());
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstanceCPU();

// 步骤 4: 设置输入形状和运行
// 1. 获取输入输出张量描述
TConstArrayView<NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
TConstArrayView<NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();

// 2. (可选) 设置输入形状，如果模型支持动态形状
// TArray<NNE::FTensorShape> InputShapes = ...; // 根据 InputDescs 和你的实际数据计算
// ModelInstance->SetInputTensorShapes(InputShapes);

// 3. 准备输入输出数据缓冲区
// 假设模型第一个输入是 [1, 3, 224, 224] 的浮点型图像
const int32 InputSize = 1 * 3 * 224 * 224 * sizeof(float);
const int32 OutputSize = 1 * 1000 * sizeof(float); // 假设输出是 1000 类
TArray<float> InputData;
TArray<float> OutputData;
InputData.SetNumUninitialized(InputSize / sizeof(float));
OutputData.SetNumUninitialized(OutputSize / sizeof(float));

// 4. 创建 Tensor 绑定
NNE::FTensorBindingCPU InputBinding;
InputBinding.Data = InputData.GetData();
InputBinding.SizeInBytes = InputSize;

NNE::FTensorBindingCPU OutputBinding;
OutputBinding.Data = OutputData.GetData();
OutputBinding.SizeInBytes = OutputSize;

// 5. 运行推理
NNE::IModelInstanceCPU::ERunSyncStatus Status = ModelInstance->RunSync(
    MakeConstArrayView({InputBinding}),
    MakeConstArrayView({OutputBinding})
);

if (Status != NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Model inference failed."));
    return;
}

// OutputData 现在包含了推理结果
```

### 进阶用法

1.  **使用 DirectML (GPU) 运行时**：流程类似，但使用 `INNERuntimeGPU` 或 `INNERuntimeRDG` 接口，并可能涉及 RDG (Render Dependency Graph) 集成以更好地与渲染流水线协作。
2.  **配置运行时线程**：通过编辑器或项目设置中的 `NNERuntimeORT` 设置项（`UNNERuntimeORTSettings`）来调整 ONNX Runtime 的线程池配置，以优化不同平台（编辑器/游戏）下的性能。
3.  **模型优化**：插件内部会根据配置对模型进行优化（如 `GraphOptimizationLevel`），开发者可通过设置间接控制。

## Demo 示例

以下是一个最小的 C++ 类示例，演示如何在 Actor 中集成 NNERuntimeORT（通过 NNE 通用接口）进行推理。为简化，省略了部分错误处理和资源管理。

```cpp
// MyNNEActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "NNERuntimeCPU.h"
#include "MyNNEActor.generated.h"

UCLASS()
class AMyNNEActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNNEActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "NNE")
    void RunInference();

private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;

    void LoadModel();
};
```

```cpp
// MyNNEActor.cpp
#include "MyNNEActor.h"
#include "UObject/UObjectGlobals.h"

AMyNNEActor::AMyNNEActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNNEActor::BeginPlay()
{
    Super::BeginPlay();
    LoadModel();
}

void AMyNNEActor::LoadModel()
{
    // 1. 加载 ONNX 文件（假设已导入到内容目录，路径为 /Game/MyModel.onnx）
    // 注意：在实际打包后，可能需要使用 FPaths::ProjectContentDir() 等构建路径
    FString ModelPath = FPaths::ProjectContentDir() / TEXT("MyModel.onnx");
    TArray64<uint8> ModelFileData;
    if (!FFileHelper::LoadFileToArray(ModelFileData, *ModelPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load model file: %s"), *ModelPath);
        return;
    }

    // 2. 获取 NNE 运行时并创建模型
    // 这里直接通过 NNE 的通用模型数据接口，让系统自动选择运行时
    UE::NNE::FModelData ModelData;
    if (!ModelData.LoadFromOnnxFile(ModelFileData))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to parse ONNX model data."));
        return;
    }

    // 3. 创建 CPU 模型实例
    Model = ModelData.CreateModelCPU();
    if (Model.IsValid())
    {
        ModelInstance = Model->CreateModelInstanceCPU();
        if (ModelInstance.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("NNE Model loaded successfully."));
        }
    }
}

void AMyNNEActor::RunInference()
{
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Model instance is not valid."));
        return;
    }

    // 准备一个简单的示例输入（例如，全零的 1x3x224x224 张量）
    TArray<float> InputData;
    InputData.SetNumZeroed(1 * 3 * 224 * 224);
    NNE::FTensorBindingCPU InputBinding;
    InputBinding.Data = InputData.GetData();
    InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

    // 准备输出缓冲区
    TArray<float> OutputData;
    OutputData.SetNumZeroed(1000); // 假设输出类别数
    NNE::FTensorBindingCPU OutputBinding;
    OutputBinding.Data = OutputData.GetData();
    OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

    // 运行推理
    auto Status = ModelInstance->RunSync(
        MakeConstArrayView({InputBinding}),
        MakeConstArrayView({OutputBinding})
    );

    if (Status == NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("Inference completed successfully. Output sample: %f"), OutputData[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed with status: %d"), static_cast<int32>(Status));
    }
}
```

## 模块依赖

从 `NNERuntimeORT.Build.cs` 分析，该插件的核心运行时模块依赖相对简洁。

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎的核心接口和类型定义，必须依赖。 |
| `RenderCore` | 用于 RDG (Render Dependency Graph) 集成，特别是 DML RDG 后端。 |
| `RHI` | 用于检查 RHI (Render Hardware Interface) 特性，如 D3D12 可用性。 |
| `NNEOnnxruntime` | 第三方 ONNX Runtime 库的 UE 封装模块，提供了 `Ort::Env` 等核心类。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移至 UE_LOGF |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回滚了之前的某个改动 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 尝试升级库版本（后被回滚） |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 代码重构，拆分头文件并优化包含 |

### 维护评价

**活跃维护中**。
- **创建时间**：约 3 年，属于较新的插件。
- **更新频率**：近期（2026年3月-4月）有连续的更新，主要是依赖库的版本升级（ONNX Runtime, DirectML）和底层代码重构。这表明该插件仍在积极维护以跟进上游库的发展。
- **已知限制**：插件标记为 **Beta** (`IsBetaVersion=true`)，且默认**未启用** (`EnabledByDefault=false`)。这意味着它虽然功能可用，但 API 和行为可能在未来的版本中发生变化，不建议在生产环境中不加测试地直接使用。
- **平台支持**：明确支持 Windows、Linux 和 macOS。
- **推荐**：对于需要 ONNX 推理能力的 UE5 项目，尤其是在开发原型或内部工具时，推荐尝试使用。对于面向最终用户的生产项目，需谨慎评估其 Beta 状态和未来可能的 API 变动风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)