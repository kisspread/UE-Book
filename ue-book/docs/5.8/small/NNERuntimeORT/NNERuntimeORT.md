# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX 运行时后端 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 Unreal Engine 神经网络引擎（NNE）的 ONNX Runtime 后端实现。它为 NNE 提供了基于 ONNX Runtime 的推理执行能力，支持两种加速方式：

- **CPU 执行提供程序**：在所有支持的平台上使用 CPU 进行神经网络推理
- **DirectML 执行提供程序**：在 Windows 平台上使用 DirectML 进行 GPU 加速推理

这个插件的核心价值在于将 ONNX Runtime 集成为 NNE 的推理后端，让开发者可以在 UE 项目中加载和运行 ONNX 格式的神经网络模型。ONNX 是机器学习领域最通用的模型格式，通过这个插件，开发者可以使用 PyTorch、TensorFlow 等框架训练的模型，并在 UE 中进行实时推理。

插件支持三种模型实例接口：
1. **IModelCPU / IModelInstanceCPU**：纯 CPU 推理
2. **IModelGPU / IModelInstanceGPU**：DirectML GPU 推理（Windows）
3. **IModelRDG / IModelInstanceRDG**：通过 RDG（Render Dependency Graph）集成的 GPU 推理，可与 UE 渲染管线深度集成

## 使用场景

- 你需要在 UE 中运行 ONNX 格式的神经网络模型（如风格迁移、图像分类、物体检测等）
- 你需要跨平台的 CPU 推理能力 → 使用 CPU 运行时
- 你在 Windows 上需要 GPU 加速推理且不想依赖特定 GPU 厂商的 SDK → 使用 DirectML 运行时
- 你需要将神经网络推理集成到 UE 的渲染管线中（如用于后处理效果）→ 使用 RDG 运行时
- 你需要细粒度控制 ONNX Runtime 的线程配置以优化推理性能

## 蓝图用法

NNERuntimeORT 本身不提供 BlueprintCallable 函数。它是 NNE 的后端实现，通过 NNE 插件的统一接口（如 `UNNEModelData`）间接使用。

要通过蓝图使用 ONNX 模型推理，请参考 NNE 主插件的文档。NNERuntimeORT 注册的运行时名称为：
- CPU 运行时：`"NNERuntimeORTCpu"`
- DirectML 运行时：`"NNERuntimeORTDml"`

### 设置项

NNERuntimeORT 通过项目设置暴露线程配置选项（位于 **编辑 → 项目设置 → 插件 → NNERuntimeORT**）：

| 设置 | 说明 |
|---|---|
| Use global thread pool | 是否使用全局线程池（跨会话共享） |
| Intra-op thread count | 算子内并行线程数（0=默认，1=单线程） |
| Inter-op thread count | 算子间并行线程数（0=默认，1=单线程） |
| Execution mode | 执行模式：SEQUENTIAL（顺序）或 PARALLEL（并行）。注意：DirectML 强制使用顺序模式 |

编辑器和游戏运行时有独立的线程配置。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeORT/NNERuntimeORT.h"  // 若需要直接引用运行时接口
```

### 基本用法：通过 NNE 接口使用 CPU 推理

NNERuntimeORT 作为 NNE 后端，通过 NNE 的标准 API 使用。以下展示了完整的推理流程：

```cpp
#include "NNE.h"
#include "NNEModelData.h"

// 1. 获取 ONNX Runtime CPU 运行时
TArray<UE::NNE::TWeakObjectPtr<UNNERuntimeCPU>> Runtimes = UE::NNE::GetAllRuntime<UNNERuntimeCPU>();
UNNERuntimeORTCpu* ORTRuntime = nullptr;
for (auto& Runtime : Runtimes)
{
    if (Runtime->GetRuntimeName() == TEXT("NNERuntimeORTCpu"))
    {
        ORTRuntime = Cast<UNNERuntimeORTCpu>(Runtime.Get());
        break;
    }
}

// 2. 加载 ONNX 模型数据
TArray64<uint8> ModelDataBuffer;
FFileHelper::LoadFileToArray(ModelDataBuffer, TEXT("MyModel.onnx"));

// 创建模型数据
TMap<FString, TConstArrayView64<uint8>> AdditionalFileData;
FGuid ModelId = FGuid::NewGuid();
TSharedPtr<UE::NNE::FSharedModelData> ModelData = ORTRuntime->CreateModelData(
    TEXT("onnx"), ModelDataBuffer, AdditionalFileData, ModelId, nullptr);

// 3. 创建模型数据资产并生成模型和实例
UObject* Outer = GetTransientPackage();
UNNEModelData* NNEModelData = NewObject<UNNEModelData>(Outer);
NNEModelData->SetModelData(ModelData);

TSharedPtr<UE::NNE::IModelCPU> Model = ORTRuntime->CreateModelCPU(NNEModelData);
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstanceCPU();

// 4. 设置输入形状并运行推理
TConstArrayView<NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
TConstArrayView<NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();

// 构建输入张量形状
TArray<NNE::FTensorShape> InputShapes;
InputShapes.Add(NNE::FTensorShape::Make({1, 3, 224, 224}));
ModelInstance->SetInputTensorShapes(InputShapes);

// 准备输入输出数据
TArray<float> InputData(1 * 3 * 224 * 224, 0.0f);  // 填充实际数据
TArray<float> OutputData(1000, 0.0f);

NNE::FTensorBindingCPU InputBinding = {InputData.GetData(), InputData.Num() * sizeof(float)};
NNE::FTensorBindingCPU OutputBinding = {OutputData.GetData(), OutputData.Num() * sizeof(float)};

TConstArrayView<NNE::FTensorBindingCPU> InputBindings = {InputBinding};
TConstArrayView<NNE::FTensorBindingCPU> OutputBindings = {OutputBinding};

// 执行推理
ModelInstance->RunSync(InputBindings, OutputBindings);
```

**来源**：基于 `Private/NNERuntimeORT.h` 和 `Private/NNERuntimeORTModel.h` 的接口定义。

### 进阶用法：DirectML GPU 推理

在 Windows 平台上使用 DirectML 进行 GPU 加速推理：

```cpp
#if PLATFORM_WINDOWS
#include "NNE.h"
#include "NNEModelData.h"

// 获取 DirectML 运行时
TArray<UE::NNE::TWeakObjectPtr<UNNERuntimeGPU>> GPURuntimes = UE::NNE::GetAllRuntime<UNNERuntimeGPU>();
UNNERuntimeORTDmlProxy* DmlRuntime = nullptr;
for (auto& Runtime : GPURuntimes)
{
    if (Runtime->GetRuntimeName() == TEXT("NNERuntimeORTDml"))
    {
        DmlRuntime = Cast<UNNERuntimeORTDmlProxy>(Runtime.Get());
        break;
    }
}

// 加载模型并创建 GPU 模型实例
// （模型数据创建流程与 CPU 相同）
TSharedPtr<UE::NNE::IModelGPU> GPUModel = DmlRuntime->CreateModelGPU(NNEModelData);
TSharedPtr<UE::NNE::IModelInstanceGPU> GPUInstance = GPUModel->CreateModelInstanceGPU();

// GPU 推理同样使用 FTensorBindingCPU（DirectML 在 CPU 内存上操作）
GPUInstance->SetInputTensorShapes(InputShapes);
GPUInstance->RunSync(InputBindings, OutputBindings);
#endif // PLATFORM_WINDOWS
```

### 进阶用法：RDG 集成推理

将推理集成到 UE 渲染管线中（仅 Windows DirectML）：

```cpp
#if PLATFORM_WINDOWS
// 需要通过 UNNERuntimeRDG 接口获取支持 RDG 的运行时
TArray<UE::NNE::TWeakObjectPtr<UNNERuntimeRDG>> RDGRuntimes = UE::NNE::GetAllRuntime<UNNERuntimeRDG>();

TSharedPtr<UE::NNE::IModelRDG> RDGModel = RDGRuntime->CreateModelRDG(NNEModelData);
TSharedPtr<UE::NNE::IModelInstanceRDG> RDGInstance = RDGModel->CreateModelInstanceRDG();

RDGInstance->SetInputTensorShapes(InputShapes);

// 在 RDG Pass 中执行推理
FRDGBuilder& GraphBuilder = ...; // 从渲染线程获取
TConstArrayView<NNE::FTensorBindingRDG> RDGInputs = ...;  // GPU 资源绑定
TConstArrayView<NNE::FTensorBindingRDG> RDGOutputs = ...;
RDGInstance->EnqueueRDG(GraphBuilder, RDGInputs, RDGOutputs);
#endif // PLATFORM_WINDOWS
```

**来源**：基于 `Private/NNERuntimeORTModel.h` 中 `FModelInstanceORTDmlRDG` 类的接口。

## Demo 示例

一个完整的最小 CPU 推理示例（Actor 组件）：

```cpp
// NNEInferenceComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "NNEInferenceComponent.generated.h"

UCLASS(ClassGroup=(NNE), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UNNEInferenceComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UNNEInferenceComponent();

    /** 加载 ONNX 模型文件 */
    UFUNCTION(BlueprintCallable, Category = "NNE")
    bool LoadModel(const FString& ModelPath);

    /** 运行推理（简化示例） */
    UFUNCTION(BlueprintCallable, Category = "NNE")
    bool RunInference(const TArray<float>& InputData, TArray<float>& OutputData);

protected:
    UPROPERTY(EditAnywhere, Category = "NNE")
    FString RuntimeName = TEXT("NNERuntimeORTCpu");

    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

```cpp
// NNEInferenceComponent.cpp
#include "NNEInferenceComponent.h"
#include "HAL/FileManager.h"
#include "Misc/FileHelper.h"

UNNEInferenceComponent::UNNEInferenceComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

bool UNNEInferenceComponent::LoadModel(const FString& ModelPath)
{
    // 加载模型文件
    TArray64<uint8> ModelBuffer;
    if (!FFileHelper::LoadFileToArray(ModelBuffer, *ModelPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load model: %s"), *ModelPath);
        return false;
    }

    // 查找运行时
    TArray<UE::NNE::TWeakObjectPtr<UNNERuntimeCPU>> Runtimes = UE::NNE::GetAllRuntime<UNNERuntimeCPU>();
    UNNERuntimeCPU* Runtime = nullptr;
    for (auto& R : Runtimes)
    {
        if (R.IsValid() && R->GetRuntimeName() == RuntimeName)
        {
            Runtime = R.Get();
            break;
        }
    }

    if (!Runtime)
    {
        UE_LOG(LogTemp, Error, TEXT("Runtime %s not found"), *RuntimeName);
        return false;
    }

    // 创建模型数据
    TMap<FString, TConstArrayView64<uint8>> AdditionalData;
    FGuid FileId = FGuid::NewGuid();
    TSharedPtr<UE::NNE::FSharedModelData> ModelData = 
        Runtime->CreateModelData(TEXT("onnx"), ModelBuffer, AdditionalData, FileId, nullptr);

    if (!ModelData.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model data"));
        return false;
    }

    // 包装为 UNNEModelData
    UNNEModelData* NNEData = NewObject<UNNEModelData>(GetTransientPackage());
    NNEData->SetModelData(ModelData);

    // 创建模型和实例
    TSharedPtr<UE::NNE::IModelCPU> NewModel = Runtime->CreateModelCPU(NNEData);
    if (!NewModel.IsValid()) return false;

    TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = NewModel->CreateModelInstanceCPU();
    if (!Instance.IsValid()) return false;

    Model = NewModel;
    ModelInstance = Instance;

    UE_LOG(LogTemp, Log, TEXT("Model loaded successfully. Inputs: %d, Outputs: %d"),
        ModelInstance->GetInputTensorDescs().Num(),
        ModelInstance->GetOutputTensorDescs().Num());
    
    return true;
}

bool UNNEInferenceComponent::RunInference(const TArray<float>& InputData, TArray<float>& OutputData)
{
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Model instance not initialized"));
        return false;
    }

    // 根据模型描述设置输入形状
    TConstArrayView<NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
    TConstArrayView<NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();

    if (InputDescs.Num() == 0 || OutputDescs.Num() == 0) return false;

    // 使用符号化形状（假设模型使用动态形状或已知形状）
    TArray<NNE::FTensorShape> InputShapes;
    for (const auto& Desc : InputDescs)
    {
        InputShapes.Add(NNE::FTensorShape::MakeFromSymbolic(Desc.GetShape()));
    }
    
    ModelInstance->SetInputTensorShapes(InputShapes);

    // 准备输出缓冲区
    int32 OutputSize = 1;
    for (const auto& Desc : OutputDescs)
    {
        for (int32 Dim : Desc.GetShape())
        {
            if (Dim > 0) OutputSize *= Dim;
        }
    }
    OutputData.SetNumZeroed(OutputSize);

    // 绑定数据
    NNE::FTensorBindingCPU InputBinding;
    InputBinding.Data = InputData.GetData();
    InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

    NNE::FTensorBindingCPU OutputBinding;
    OutputBinding.Data = OutputData.GetData();
    OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

    TConstArrayView<NNE::FTensorBindingCPU> Inputs(&InputBinding, 1);
    TConstArrayView<NNE::FTensorBindingCPU> Outputs(&OutputBinding, 1);

    // 执行推理
    auto Status = ModelInstance->RunSync(Inputs, Outputs);
    return Status == NNE::IModelInstanceCPU::ERunSyncStatus::Ok;
}
```

> **注意**：`SetInputTensorShapes` 需要根据具体模型的实际输入维度来设置。上面示例使用了符号化形状作为简化，实际使用时需要根据模型的输入维度构造具体的形状值。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，定义运行时接口（IModelCPU、IModelGPU、IModelRDG 等） |
| `NNEOnnxruntime` | 第三方 ONNX Runtime 库的构建模块（External 类型） |
| `DirectML` | DirectML GPU 加速支持（Windows 平台条件依赖） |
| `RenderCore` | RDG（Render Dependency Graph）集成所需的渲染核心 |
| `RHI` | 渲染硬件接口，用于 DirectML 与 D3D12 的集成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3 和 DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移至新 UE_LOGF 宏 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退了之前的提交 CL52245530 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 再次尝试升级 ONNX Runtime 和 DirectML 版本 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染资源头文件，优化编译依赖 |

### 维护评价

- **活跃维护**：最近 6 个月内有持续的功能更新和依赖库升级
- **ONNX Runtime 依赖频繁升级**：最近的提交主要集中在升级第三方 ONNX Runtime 和 DirectML 库版本，表明 Epic 在积极跟进上游更新
- **Beta 状态**：`.uplugin` 中 `IsBetaVersion=true` 且 `EnabledByDefault=false`，说明此插件仍处于 Beta 阶段
- **跨平台支持**：仅支持 Win64、Linux、LinuxArm64、Mac，DirectML GPU 加速仅限 Windows
- **推荐使用**：作为 NNE 的主要推理后端之一，适合需要在 UE 中运行 ONNX 模型的场景。但需要注意其 Beta 状态，API 可能在后续版本中发生变化

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [NNE 主插件源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNE)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)