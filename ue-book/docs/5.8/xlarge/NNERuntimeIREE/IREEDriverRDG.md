# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 是一个实验性的 Neural Network Engine (NNE) 运行时后端实现。其核心目的是利用 IREE（基于 MLIR 和 LLVM）编译器框架，将神经网络模型（如 ONNX 格式）直接编译为高性能的原生代码，并在运行时高效执行。它旨在为游戏提供一种跨平台、高性能的神经网络推理解决方案，特别是用于替代旧的 ORT (ONNX Runtime) CPU 运行时，尤其擅长处理小型、需要实时推理的神经网络。

## 使用场景

- **实时游戏 AI 推理**：在游戏运行时执行用于角色行为决策、目标识别或环境感知的小型神经网络。
- **需要极致性能的移动端或主机端 AI 功能**：利用 IREE 将模型编译为原生代码，获得比传统解释器更高的执行效率。
- **跨平台部署神经网络模型**：为不同目标平台（PC、主机、移动端）编译优化后的模型，实现统一的部署流程。

## 蓝图用法

此插件作为 NNE 的底层运行时，通常不直接暴露蓝图节点。用户通过标准的 `UNNEModelData` 和 `UNNEModelInstance` API（属于 NNE 核心模块）来使用，而 `NNERuntimeIREE` 会作为其中一个可选的运行时后端自动注册。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Compile Model` | (通过 NNE API) 触发模型编译，将 ONNX 数据编译为 IREE 可执行的格式。 | `UNNEModelData` |
| `Create Instance` | (通过 NNE API) 为已编译的模型创建运行时实例。 | `UNNEModelInstance` |

### 使用示例（蓝图描述）

1.  加载或获取一个 `UNNEModelData` 资产。
2.  调用 `Compile` 节点（或类似功能的函数），确保其内部选择了 `NNERuntimeIREE` 作为后端。
3.  调用 `CreateInstance` 节点，创建一个可用于推理的 `UNNEModelInstance`。
4.  设置输入张量数据，调用推理函数获取输出。

## C++ 用法

在 C++ 中，主要通过 NNE 的统一接口 `UNNEModelData` 和 `UNNEModelInstance` 与 `NNERuntimeIREE` 交互。编译过程是自动的，当选择 IREE 运行时时，会调用插件内部的编译器。

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeIREE.h" // 可能需要包含此头文件以访问特定配置
```

### 基本用法

以下示例展示了如何加载模型数据并尝试通过 IREE 运行时进行编译和推理。核心工作由 NNE 框架协调，用户代码较少直接操作 IREE 底层。

```cpp
// 假设已经加载了 ONNX 模型数据到 UNNEModelData
UNNEModelData* ModelData = ...;

// 创建模型实例（此处会触发编译和加载）
// NNE 框架会根据平台和可用性自动选择合适的运行时（如 IREE）
TObjectPtr<UNNEModelInstance> ModelInstance = ModelData->CreateInstance(TEXT("IREE"));

if (ModelInstance)
{
    // 准备输入数据（示例：一个 Shape 为 [1,3,224,224] 的 Float 张量）
    TArray<float> InputData;
    InputData.SetNumUninitialized(1 * 3 * 224 * 224);
    // ... 填充数据

    // 创建输入张量
    FNNEInferenceContext Context;
    Context.SetInputTensorByName(TEXT("input"), { (uint8*)InputData.GetData(), InputData.Num() * sizeof(float) });

    // 运行推理
    if (ModelInstance->RunSync(Context) == ENNEInferResult::Success)
    {
        // 获取输出数据
        const TConstArrayView<uint8> OutputTensor = Context.GetOutputTensorByName(TEXT("output"));
        const float* OutputData = reinterpret_cast<const float*>(OutputTensor.GetData());
        // ... 处理输出
    }
}
```

### 进阶用法

通过 `NNERuntimeIREEEditor` 模块，可以在编辑器中预烘焙模型数据。对于 `IREEDriverRDG`，它允许将神经网络推理计算图集成到渲染依赖图（RDG）中，实现与 GPU 渲染管线的高效协作。

```cpp
// 在渲染线程中，使用 RDG 驱动器执行推理（概念示例）
FRDGBuilder& GraphBuilder = ...; // 当前 RDG 构建器
FNNERuntimeIREEResource* ShaderResource = ...; // 代表一个编译好的计算内核

// 将 RDG 缓冲区包装为 IREE 缓冲区
FRDGBufferRef RDGBuffer = GraphBuilder.CreateBuffer(...);
iree_hal_buffer_t* IreeBuffer = nullptr;
UE::IREE::HAL::RDG::BufferWrapRDG(..., RDGBuffer, ..., &IreeBuffer);

// 调度包含此缓冲区的推理操作
// ... 具体的调度代码取决于模型结构
```

## Demo 示例

一个最小的 C++ 示例，演示如何使用 NNE API 加载模型并运行推理，此处后端为 `NNERuntimeIREE`。

**MyAIDemoComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "MyAIDemoComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAIDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category = "AI")
    TObjectPtr<UNNEModelData> ModelData;

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "AI")
    void RunInference(const TArray<float>& Input);

private:
    TSharedPtr<UNNEModelInstance> ModelInstance;
};
```

**MyAIDemoComponent.cpp**
```cpp
#include "MyAIDemoComponent.h"

void UMyAIDemoComponent::BeginPlay()
{
    Super::BeginPlay();

    if (ModelData)
    {
        // 创建模型实例，NNE 会尝试使用当前平台最优的运行时（如 IREE）
        ModelInstance = MakeShareable(ModelData->CreateInstance(TEXT("MyAIModel")));
        if (ModelInstance.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("NNE Model Instance Created with IREE Runtime"));
        }
    }
}

void UMyAIDemoComponent::RunInference(const TArray<float>& Input)
{
    if (!ModelInstance.IsValid())
    {
        return;
    }

    // 准备输入上下文
    FNNEInferenceContext Context;
    Context.SetInputTensorByName(TEXT("input"), {(uint8*)Input.GetData(), Input.Num() * sizeof(float)});

    // 执行同步推理
    if (ModelInstance->RunSync(Context) == ENNEInferResult::Success)
    {
        // 处理输出
        TConstArrayView<uint8> Output = Context.GetOutputTensorByName(TEXT("output"));
        if (Output.Num() > 0)
        {
            const float* Result = reinterpret_cast<const float*>(Output.GetData());
            UE_LOG(LogTemp, Log, TEXT("Inference Result: %f"), Result[0]);
        }
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("NNE Inference Failed"));
    }
}
```

## 模块依赖

使用此插件，你的模块不需要直接依赖其内部模块。NNE 的公共 API 已经封装了运行时选择逻辑。如果你需要在 C++ 中直接使用 NNE API，则依赖 `NNE` 模块即可。

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine 的核心公共 API，用于模型加载、编译和推理。 |
| `NNERuntimeIREE` | (内部模块) 提供基于 IREE 的 NNE 运行时实现。 |
| `IREEDriverRDG` | (内部模块) 提供基于渲染依赖图 (RDG) 的 IREE 设备驱动，用于 GPU 计算集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了着色器烹饪期间跨线程访问已释放内存的严重问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了 32/64 位格式说明符不匹配的潜在问题。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一了 GPU 命令提交与同步的 API。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧式日志宏迁移到新式宏。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了着色器作业状态管理，简化了代码。 |

### 维护评价

该插件创建于 2023 年 11 月，属于**实验性**项目。从最近的 Git 记录看，它在 2026 年 4-5 月仍有活跃的开发提交，包括重要的 Bug 修复、API 重构和代码现代化。这表明该插件虽然标记为实验性，但仍在**积极维护和开发中**。它旨在成为 ORT CPU 运行时的高性能替代品，对于追求实时性和性能的小型 AI 模型是一个有潜力的选择。由于其实验性标签和不断发展的模型支持，建议在项目中谨慎评估和集成，并关注其稳定性变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [官方文档]() （暂无）