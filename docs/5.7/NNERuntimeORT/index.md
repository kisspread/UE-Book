# NNE Runtime ORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 NNE（Neural Network Engine）框架的一个**运行时后端插件**，它基于 Microsoft 的 [ONNX Runtime](https://onnxruntime.ai/) 库实现推理功能。简单来说，它让你能在 Unreal Engine 中**加载并运行 ONNX 格式的神经网络模型**。

这个插件解决的核心问题是：UE 的 NNE 框架定义了一套通用的模型加载、创建和推理接口（`INNERuntime`、`INNERuntimeCPU`、`INNERuntimeGPU` 等），但框架本身不包含推理引擎。NNERuntimeORT 就是 NNE 的"发动机"——它通过 ONNX Runtime 提供实际的推理能力。

该插件支持**三种计算后端**：

1. **CPU 后端**（`UNNERuntimeORTCpu`）：通过 ONNX Runtime 的 CPU Execution Provider 运行模型，在所有平台可用（Win64、Linux、LinuxArm64、Mac）。
2. **GPU 后端**（DirectML）：通过 DirectML Execution Provider 运行模型，**仅限 Windows 平台**。需要 D3D12 兼容硬件。
3. **NPU 后端**：通过 DirectML 驱动专用 NPU（Neural Processing Unit）硬件运行模型，**仅限 Windows 11 24H2+**。支持 Intel NPU 等硬件。

需要注意的是，DirectML GPU 后端是一个组合接口，根据硬件能力动态暴露 GPU、RDG（Render Dependency Graph）和 NPU 三种接口的任意子集。RDG 接口特别重要，因为它允许神经网络推理与 UE 的渲染管线（RDG）无缝集成，在同一 D3D12 命令队列上执行推理操作。

## 使用场景

- 你训练了一个 ONNX 模型（如图像超分、风格迁移、降噪器）→ 用 NNERuntimeORT 在游戏内实时推理
- 你需要在渲染管线中插入神经网络推理步骤（如 AI 降噪）→ 使用 RDG 接口直接与 UE 的渲染图集成
- 你需要在 CPU 上运行轻量级模型（如姿态估计、文本分类）→ 使用 CPU 后端
- 你有 Intel NPU 或类似硬件加速器 → 使用 NPU 后端加速推理
- 你在做 MetaHuman 相关功能（Speech2Face、Face Contour Tracker）→ 底层依赖此插件

## 蓝图用法

NNERuntimeORT 本身**没有蓝图可调用的公开 API**。所有头文件均位于 `Private/` 目录下，不对外暴露蓝图接口。它的功能通过 NNE 框架的统一接口（如 `UNNEModelData`）间接使用。

实际使用时，蓝图中涉及 NNE 的部分请参考 NNE 核心插件的文档。

## C++ 用法

NNERuntimeORT 的所有类均为 Private，不提供对外头文件。用户通过 NNE 框架的标准接口使用它。使用流程如下：

### 工作原理

```
.onnx 文件
    ↓ Import (UNNEModelData)
NNE 框架根据注册的 Runtime 选择合适的后端
    ↓ CreateModelData → CreateModel → CreateModelInstance
NNERuntimeORT 接管：用 ONNX Runtime 加载、优化、执行推理
```

插件在模块启动时自动注册两个 NNE Runtime：
- `NNERuntimeORTCpu` — CPU 推理（所有平台）
- `NNERuntimeORTDml` — DirectML 推理（仅 Windows，名称因硬件能力而异）

### 基本用法（通过 NNE 框架）

由于 NNERuntimeORT 作为 NNE 的底层实现，你通常不直接引用它，而是通过 NNE 的标准接口使用。下面是一个标准的使用流程：

```cpp
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeCPU.h"

// 1. 获取模型数据（通常从 UAsset 加载）
TObjectPtr<UNNEModelData> ModelData = /* 从资产加载 */;

// 2. 选择运行时（NNERuntimeORT 会在启动时自动注册）
TArray<TWeakInterfacePtr<INNERuntime>> Runtimes = UE::NNE::GetAllRuntimes();

// 3. 通过 CPU 运行时创建模型
TWeakInterfacePtr<INNERuntimeCPU> CPURuntime;
for (auto& Runtime : Runtimes)
{
    CPURuntime = TWeakInterfacePtr<INNERuntimeCPU>(Runtime.Get());
    if (CPURuntime.IsValid())
    {
        break;
    }
}

// 4. 创建模型和模型实例
auto Model = CPURuntime->CreateModelCPU(ModelData);
auto ModelInstance = Model->CreateModelInstanceCPU();

// 5. 设置输入形状
TArray<NNE::FTensorShape> InputShapes;
InputShapes.Add(NNE::FTensorShape::Make({1, 3, 224, 224}));
ModelInstance->SetInputTensorShapes(InputShapes);

// 6. 准备输入数据
TArray<float> InputData(1 * 3 * 224 * 224);
// ... 填充数据 ...

NNE::FTensorBindingCPU InputBinding;
InputBinding.Data = InputData.GetData();
InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

// 7. 准备输出缓冲区
TConstArrayView<NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();
TArray<float> OutputData(OutputDescs[0].GetElementCount()); // 简化示意
NNE::FTensorBindingCPU OutputBinding;
OutputBinding.Data = OutputData.GetData();
OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

// 8. 执行推理
ModelInstance->RunSync({InputBinding}, {OutputBinding});
```

### RDG 用法（渲染管线集成，Windows 专属）

RDG（Render Dependency Graph）接口允许将神经网络推理直接嵌入 UE 的渲染管线，在同一 GPU 命令队列上执行。这是 NNERuntimeORT 最独特的能力之一：

```cpp
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeRDG.h"

// 通过 RDG 运行时创建模型（需要 D3D12 RHI）
auto RDGModel = RDGRuntime->CreateModelRDG(ModelData);
auto RDGModelInstance = RDGModel->CreateModelInstanceRDG();

// 在 RDG Pass 中使用
RDGModelInstance->SetInputTensorShapes(InputShapes);

// EnqueueRDG 在 RDG 构建器中排队推理操作
// 输入/输出通过 FRHIBuffer 传递（GPU buffer）
RDGModelInstance->EnqueueRDG(GraphBuilder, InputBindings, OutputBindings);
```

RDG 接口的关键特点：
- 推理操作在 RHI 提交线程（D3D12 命令队列）上执行
- `SetInputTensorShapes()` 从游戏线程或渲染线程调用，会自动同步到 RHI 线程
- 输入/输出通过 `FRHIBuffer`（GPU buffer）传递，零拷贝到 GPU
- 支持动态形状：当输入包含符号维度时，RDG 后端会在 RHI 线程上重建 Session 并设置自由维度覆盖

### 设置项

插件在编辑器设置（Project Settings → Plugins → NNERuntimeORT）中提供以下配置：

| 设置项 | 说明 | 默认值 |
|---|---|---|
| Editor: Use global thread pool | Editor 是否使用全局线程池 | 是 |
| Editor: Intra-op thread count | 算子内并行线程数（0=默认） | 0 |
| Editor: Inter-op thread count | 算子间并行线程数（0=默认） | 0 |
| Editor: Execution mode | 顺序/并行执行模式 | Sequential |
| Game: Use global thread pool | 游戏目标是否使用全局线程池 | 否 |
| Game: Intra-op thread count | 同上 | 1 |
| Game: Inter-op thread count | 同上 | 1 |
| Game: Execution mode | 同上 | Sequential |

修改设置后建议重启编辑器。

## Demo 示例

### 最小 CPU 推理示例

**Build.cs 依赖**：

```csharp
// 你不需要直接依赖 NNERuntimeORT，而是依赖 NNE 框架
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "CoreUObject",
    "Engine",
    "NNE"
});
```

**MyNeuralNetwork.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNEModelData.h"
#include "NNERuntimeCPU.h"

class FMyNeuralNetwork
{
public:
    bool LoadModel(UNNEModelData* InModelData);
    bool RunInference(const TArray<float>& Input, TArray<float>& Output);

private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

**MyNeuralNetwork.cpp**：

```cpp
#include "MyNeuralNetwork.h"
#include "NNE.h"

bool FMyNeuralNetwork::LoadModel(UNNEModelData* InModelData)
{
    // 从 NNE 注册表中找到 CPU 运行时（NNERuntimeORTCpu 会自动注册）
    for (auto& Runtime : UE::NNE::GetAllRuntimes())
    {
        TWeakInterfacePtr<INNERuntimeCPU> CPURuntime(Runtime.Get());
        if (CPURuntime.IsValid() && CPURuntime->CanCreateModelCPU(InModelData) 
            == INNERuntimeCPU::ECanCreateModelCPUStatus::Ok)
        {
            Model = CPURuntime->CreateModelCPU(InModelData);
            if (Model.IsValid())
            {
                ModelInstance = Model->CreateModelInstanceCPU();
                return ModelInstance.IsValid();
            }
        }
    }
    return false;
}

bool FMyNeuralNetwork::RunInference(const TArray<float>& Input, TArray<float>& Output)
{
    if (!ModelInstance.IsValid())
    {
        return false;
    }

    // 假设模型输入: [1, 10] float32
    TArray<NNE::FTensorShape> InputShapes;
    InputShapes.Add(NNE::FTensorShape::Make({1, 10}));
    if (ModelInstance->SetInputTensorShapes(InputShapes) 
        != IModelInstanceCPU::ESetInputTensorShapesStatus::Ok)
    {
        return false;
    }

    // 绑定输入
    NNE::FTensorBindingCPU InputBinding;
    InputBinding.Data = const_cast<float*>(Input.GetData());
    InputBinding.SizeInBytes = Input.Num() * sizeof(float);

    // 准备输出（假设输出也是 [1, 10]）
    Output.SetNum(10);
    NNE::FTensorBindingCPU OutputBinding;
    OutputBinding.Data = Output.GetData();
    OutputBinding.SizeInBytes = Output.Num() * sizeof(float);

    return ModelInstance->RunSync({InputBinding}, {OutputBinding}) 
        == IModelInstanceCPU::ERunSyncStatus::Ok;
}
```

## 模块依赖

NNERuntimeORT 本身不导出任何 Public 模块依赖。以下是其 **Private** 依赖列表（使用者不需要直接依赖这些）：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `NNE` | NNE 框架核心接口（`INNERuntime`、`UNNEModelData` 等） |
| `NNEOnnxruntime` | ONNX Runtime C API 封装 |
| `Projects` | 插件路径查找 |
| `RenderCore` | RDG（Render Dependency Graph）支持 |
| `DeveloperSettings` | 设置系统（`UDeveloperSettings`） |
| `RHI` | 渲染硬件接口 |
| `D3D12RHI` | D3D12 RHI 接口（仅 Win64） |
| `DirectML` | DirectML 第三方库（仅 Win64） |
| `DX12` | DirectX 12 第三方库（仅 Win64） |

**使用者只需依赖 `NNE` 模块**即可，NNE 框架会自动发现并使用 NNERuntimeORT 注册的运行时。

## 维护状态

### 近期更新

- **2025-09-23** `8de988e` — [NNE] NNERuntimeORT fix for new dxcore adapter listing.
  - 修复了使用新 DXCore API 列出适配器时的问题，可能与 Windows 11 24H2 新增的 `D3D12_GENERIC_ML` 适配器属性相关。

- **2025-09-23** `ed2179d` — [NNE] The DirectML NPU interface lists the GPU as NPU.
  - 修复了 DirectML NPU 接口错误地将 GPU 适配器识别为 NPU 的问题。说明 NPU 支持正在活跃开发和修复中。

- **2025-06-26** `a2e7518` — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files.
  - 批量添加 `UE_INLINE_GENERATED_CPP_BY_NAME` 宏，属于 UE5 构建系统优化，无功能变化。

### 维护评价

- **创建时间**：2023-11-07（约 2 年前），属于 UE5.4 时代引入的 NNE 系列插件
- **标记状态**：`IsBetaVersion = true`，仍处于 Beta 阶段
- **默认启用**：否（`EnabledByDefault = false`），需要手动在插件设置中启用
- **活跃程度**：活跃维护中。最近一次更新在 2025 年 9 月，持续修复 DirectML/NPU 相关问题
- **平台支持**：Win64、Linux、LinuxArm64、Mac（CPU 后端全平台；DirectML 仅 Win64）
- **ONNX Runtime 版本**：1.20（从二进制文件名判断：`libonnxruntime.1.20.*`）

**总结**：NNERuntimeORT 是 UE5 NNE 推理引擎的核心后端实现，处于 Beta 阶段但活跃维护。对于需要在 UE 中运行 ONNX 模型的场景，它是唯一的官方支持运行时。DirectML GPU/NPU 支持仍在快速迭代中，建议关注最新 UE 版本的更新。

⚠️ **注意**：Beta 版本，API 和行为可能在后续版本中变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)
