# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | NNE ONNX 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime) |
| 实验性 | ⚦️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是虚幻引擎神经网络引擎 (NNE) 的一个运行时后端插件。它解决了在 UE5 中使用 ONNX 格式模型进行实时机器学习推理的问题。其核心作用是将 NNE 的抽象神经网络模型接口，映射到高性能的 ONNX Runtime (ORT) 引擎上执行。

该插件存在的主要意义在于：
1.  **CPU 与 GPU 推理支持**：提供在 CPU 上运行 ONNX 模型的能力（通过 `INNERuntimeCPU`），并**仅限于 Windows 平台**，通过 DirectML 提供对 GPU 加速的推理支持（通过 `INNERuntimeGPU` 和 `INNERuntimeRDG`）。
2.  **集成到虚幻渲染管线**：通过 `INNERuntimeRDG` 接口，将 GPU 推理操作集成到虚幻的渲染依赖图（RDG）中，允许神经网络推理与渲染管线高效协同。
3.  **提供可配置的运行时环境**：允许用户通过开发者设置（`UNNERuntimeORTSettings`）精细控制 ONNX Runtime 的线程池和执行模式（顺序/并行），以优化性能。

简而言之，它是连接虚幻引擎 NNE 抽象层与工业级推理引擎 ONNX Runtime 的桥梁，让开发者能在游戏中或编辑器里高效运行 ONNX 模型。

## 使用场景

-   你在开发一个需要实时 AI 行为的游戏（如角色决策、路径规划），希望使用预训练的 ONNX 模型在 CPU 或 GPU 上进行推理 → 使用 `NNERuntimeCpu` 或 `NNERuntimeDml`（Windows）。
-   你正在制作一个图像风格迁移、超分辨率或降噪等视觉效果工具，需要将计算任务无缝集成到虚幻的渲染管线中，避免 GPU 同步开销 → 使用 `NNERuntimeDmlRDG`（仅限 Windows + D3D12）。
-   你希望优化推理性能，需要调整 ONNX Runtime 的线程数、是否使用全局线程池以及执行模式（顺序/并行） → 配置 `Project Settings > Plugins > NNERuntimeORT`。

## 蓝图用法

此插件本身不直接暴露蓝图节点。它的所有功能都通过 NNE（神经网络引擎）核心插件的蓝图接口来使用。在蓝图中，你操作的是 NNE 提供的通用 `UNNEModelData`、`UNNEModelInstanceCPU` 等对象，而 NNE 会在后台根据模型格式（ONNX）和选择的运行时（NNERuntimeORT）调用此插件的具体实现。

因此，蓝图用法遵循 NNE 的标准流程：
1.  加载 `UNNEModelData` 资产。
2.  使用 NNE 的蓝图节点（如 `Create Model Instance`）创建模型实例。
3.  设置输入数据并运行推理。

**核心节点**（均来自 NNE 核心插件）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Model Instance` | 从 `UNNEModelData` 创建一个可运行的模型实例。 | `NNEBlueprintLibrary` |
| `Set Input Data` / `Set Input Tensor` | 设置模型实例的输入数据。 | `UNNEModelInstance*` |
| `Run` / `Run Sync` | 执行模型推理。 | `UNNEModelInstance*` |

### 使用示例（蓝图描述）

在蓝图中，流程如下：
1.  引用一个已导入的 `UNNEModelData` 资产（`.onnx` 文件）。
2.  使用 “Create Model Instance” 节点，输入该模型数据，输出一个模型实例对象（例如，`UNNEModelInstanceCPU`）。
3.  使用 “Set Input Data” 节点，为模型实例的输入张量赋值（例如，一个代表图像数据的浮点数组）。
4.  调用 “Run Sync” 节点执行同步推理。
5.  使用 “Get Output Data” 节点获取推理结果。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeCPU.h" // 用于 CPU 推理
#include "NNERuntimeGPU.h" // 用于 GPU 推理 (Windows)
#include "NNERuntimeRDG.h" // 用于 RDG 集成 (Windows + D3D12)
```

### 基本用法

从测试用例和插件代码中提取的典型 CPU 推理流程。

```cpp
// (基于测试用例和 NNE 核心 API 模拟的代码)
// 假设你已经有一个 UNNEModelData* ModelData 指针

// 1. 获取一个可用的运行时（例如，ORT CPU 运行时）
TWeakObjectPtr<UNNE::INNERuntime> Runtime = UNNE::GetRuntime(TEXT("NNERuntimeORTCpu"));

// 2. 检查运行时是否可以为此模型数据创建 CPU 模型
if (Runtime->CanCreateModelCPU(ModelData) == NNE::ECanCreateModelCPUStatus::Ok)
{
    // 3. 创建 CPU 模型
    TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(ModelData);

    if (Model.IsValid())
    {
        // 4. 创建模型实例
        TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstanceCPU();

        if (ModelInstance.IsValid())
        {
            // 5. 设置输入数据（示例，假设只有一个输入张量）
            TArray<float> InputData; // 填充你的输入数据
            NNE::FTensorBindingCPU InputBinding;
            InputBinding.Data = InputData.GetData();
            InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

            // 6. 设置输出缓冲区
            TArray<float> OutputData;
            OutputData.SetNumUninitialized(/* 根据模型输出描述计算 */);
            NNE::FTensorBindingCPU OutputBinding;
            OutputBinding.Data = OutputData.GetData();
            OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

            // 7. 运行推理
            NNE::IModelInstanceCPU::ERunSyncStatus Status = ModelInstance->RunSync({InputBinding}, {OutputBinding});
            if (Status == NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
            {
                // 8. 使用 OutputData 中的推理结果
            }
        }
    }
}
```

**来源文件路径**：逻辑基于 `Private/NNERuntimeORT.h` (`UNNERuntimeORTCpu`) 和 `Private/NNERuntimeORTModel.h` (`FModelInstanceORTCpu`, `FModelORTCpu`) 中的接口实现。

### 进阶用法

使用 RDG 接口将 GPU 推理集成到渲染管线中（仅限 Windows D3D12）。这更复杂，通常用于后处理等场景。

```cpp
// (概念性代码，展示了集成思路，非直接可编译片段)
#include "RenderGraphBuilder.h"

// 在你的渲染通道或自定义 Pass 中...
FRDGBuilder& GraphBuilder = ...; // 通常从 FSceneView 或 FRenderingCompositePassContext 获取

// 1. 获取 ORT DML RDG 运行时并创建 RDG 模型实例 (假设已缓存)
TSharedPtr<NNE::IModelInstanceRDG> RDGModelInstance = ...;

// 2. 准备输入输出的 RDG 缓冲区 (FRDGBufferSRV*, FRDGBufferUAV*)
FRDGBufferSRV* InputBufferSRV = ...;
FRDGBufferUAV* OutputBufferUAV = ...;

// 3. 构建输入输出绑定
NNE::FTensorBindingRDG InputBinding = {InputBufferSRV};
NNE::FTensorBindingRDG OutputBinding = {OutputBufferUAV};

// 4. 将推理任务加入 RDG
NNE::IModelInstanceRDG::EEnqueueRDGStatus EnqueueStatus = RDGModelInstance->EnqueueRDG(GraphBuilder, {InputBinding}, {OutputBinding});

if (EnqueueStatus == NNE::IModelInstanceRDG::EEnqueueRDGStatus::Ok)
{
    // 推理操作已被添加到渲染图，将在后续执行
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何使用 ORT CPU 运行时进行推理。此示例假设你已经通过其他方式（如资产加载）获得了 `ModelData`。

**NNEORTDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class UNNEModelData;

class FNNEORTDemo
{
public:
    void RunSimpleInference(UNNEModelData* ModelData);
};
```

**NNEORTDemo.cpp**
```cpp
#include "NNEORTDemo.h"
#include "NNE.h"
#include "NNERuntimeCPU.h"

void FNNEORTDemo::RunSimpleInference(UNNEModelData* ModelData)
{
    if (!ModelData) return;

    // 1. 获取 ORT CPU 运行时
    const FName RuntimeName = TEXT("NNERuntimeORTCpu");
    TWeakObjectPtr<UNNE::INNERuntime> Runtime = UNNE::GetRuntime(RuntimeName);
    if (!Runtime.IsValid() || Runtime->CanCreateModelCPU(ModelData) != NNE::ECanCreateModelCPUStatus::Ok)
    {
        UE_LOG(LogTemp, Error, TEXT("ORT CPU runtime not available or cannot create model."));
        return;
    }

    // 2. 创建模型与实例
    TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(ModelData);
    TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = Model->CreateModelInstanceCPU();

    // 3. 查询输入输出描述（实际应用需根据描述计算尺寸）
    TConstArrayView<NNE::FTensorDesc> InputDescs = Instance->GetInputTensorDescs();
    TConstArrayView<NNE::FTensorDesc> OutputDescs = Instance->GetOutputTensorDescs();

    if (InputDescs.Num() == 0 || OutputDescs.Num() == 0)
    {
        UE_LOG(LogTemp, Warning, TEXT("Model has no inputs or outputs."));
        return;
    }

    // 4. 准备示例输入数据（假设第一个输入是浮点张量，形状为 [1,3,224,224]）
    const NNE::FTensorDesc& FirstInputDesc = InputDescs[0];
    const NNE::FTensorShape InputShape = NNE::FTensorShape::MakeFromSymbolic(FirstInputDesc.GetShape());
    const uint64 InputDataSize = InputShape.Volume() * sizeof(float);
    TArray<float> InputData;
    InputData.AddZeroed(InputShape.Volume());

    // 5. 准备输出缓冲区
    const NNE::FTensorDesc& FirstOutputDesc = OutputDescs[0];
    const NNE::FTensorShape OutputShape = NNE::FTensorShape::MakeFromSymbolic(FirstOutputDesc.GetShape());
    const uint64 OutputDataSize = OutputShape.Volume() * sizeof(float);
    TArray<float> OutputData;
    OutputData.AddZeroed(OutputShape.Volume());

    // 6. 绑定并运行
    NNE::FTensorBindingCPU InputBinding = {InputData.GetData(), InputDataSize};
    NNE::FTensorBindingCPU OutputBinding = {OutputData.GetData(), OutputDataSize};

    auto Status = Instance->RunSync({InputBinding}, {OutputBinding});
    if (Status == NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("Inference completed successfully. First output value: %f"), OutputData[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed."));
    }
}
```

## 模块依赖

从 `Build.cs` 分析，使用此插件你的模块需要依赖以下特定模块：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，提供 `IModelCPU`, `IModelGPU` 等抽象接口。 |
| `NNEOnnxruntime` | 第三方 ONNX Runtime 的构建模块。 |
| `DirectML` | (仅限 Windows) 微软的 DirectML 框架，用于 GPU 加速。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 将 ONNX Runtime 升级至 1.24.3，DirectML 升级至 1.15.4，提升推理性能和兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志系统从 UE_LOG 迁移至 UE_LOGF，属于引擎级日志系统更新适配。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退了之前的某次提交（CL52245530），可能涉及不稳定的改动。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 同样的升级提交，可能是之前的提交被回退后重新提交。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 重构代码，将 `PooledRenderTarget` 和 `SceneRenderingAllocator` 拆分到单独的头文件中，改善代码组织。 |

### 维护评价

-   **活跃维护**：该插件仍在积极维护中。最近一次提交（2026-04-21）是关键依赖（ONNX Runtime, DirectML）的版本升级，这表明团队在持续跟进上游更新以获取性能改进和新特性。
-   **Beta 状态**：插件标记为 `IsBetaVersion=true` 且默认未启用（`EnabledByDefault=false`），这表明它可能还未达到完全稳定的生产就绪状态，API 或行为在未来版本中可能会有变动。
-   **平台限制**：核心的 GPU (DirectML) 推理和 RDG 集成功能仅限于 Windows 平台。
-   **推荐使用**：**推荐在 Windows 平台上进行机器学习相关的 UE5 项目开发时使用**。对于 CPU 推理需求，它是跨平台（Win64, Linux, Mac）的可靠选择。由于其 Beta 状态，建议在生产环境中充分测试，并关注版本更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
-   [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
-   [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)