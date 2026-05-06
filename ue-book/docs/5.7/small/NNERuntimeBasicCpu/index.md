# NNERuntimeBasicCpu

> Performant, cross-platform, CPU runtime for the NNE plugin that supports basic models.

| 属性 | 值 |
|---|---|
| 中文名 | 基本CPU运行时 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Python脚本） |
| 模块 | `NNERuntimeBasicCpu` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-06-03 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeBasicCpu) | |

## 用途

NNE（Neural Network Engine）是 UE 的神经网络推理框架。  
**NNERuntimeBasicCpu** 是 NNE 的一个 CPU 运行时后端，专门针对**基本模型（如 MLP - 多层感知机）**进行了优化。它提供：

- 跨平台、高性能的 CPU 推理（支持 ISPC 向量化加速）
- 内存紧凑、低开销的模型格式 `.ubnne`
- 一个 Python 导出脚本（`nne_runtime_basic_cpu.py`），用于将 PyTorch 等框架训练好的模型转换为 `.ubnne` 文件
- C++ 端的模型构建器 `FModelBuilder`，可在内存中直接构造模型并序列化

**为什么需要这个插件？**  
NNE 本身不包含具体的运行时实现，需要依赖后端（如 CPU、GPU、NPU）。  
NNERuntimeBasicCpu 提供了一个可移植的 CPU 参考实现，适合在无法使用 GPU 或需要低功耗推理的场景下运行小型网络。

## 使用场景

- 你在开发一个需要运行小型神经网络（如 MLP）进行决策/预测的游戏，且不想依赖第三方库或 GPU。
- 你需要一个轻量级的跨平台推理方案，用于移动设备或服务器端。
- 你希望在编辑器外或打包后的游戏中运行预训练的模型，且对推理速度有一定要求。

## 蓝图用法

本插件**不暴露任何蓝图节点**。所有操作需要使用 C++ 或 Python 脚本完成。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeBasicCpuBuilder.h"
#include "NNERuntime.h"           // 用于 NNE 通用接口
#include "NNEModelData.h"         // UNNEModelData
#include "NNERuntimeCPU.h"        // INNERuntimeCPU
```

### 基本用法

#### 1. 使用 FModelBuilder 在内存中构建模型并序列化

```cpp
using namespace UE::NNE::RuntimeBasic;

// 创建模型构建器
FModelBuilder Builder;

// 添加层：Linear 层 + ReLU 激活
auto Layer1 = Builder.AddLinearLayer(
    784,        // 输入特征数
    128,        // 输出特征数
    FModelBuilder::ELinearLayerType::Normal,
    FModelBuilder::EWeightInitializationType::KaimingUniform
);
Builder.AddActivation(Layer1, FModelBuilder::EActivationFunction::ReLU);

auto Layer2 = Builder.AddLinearLayer(
    128,        // 输入
    10,         // 输出（分类数）
    FModelBuilder::ELinearLayerType::Normal,
    FModelBuilder::EWeightInitializationType::KaimingUniform
);
// 最后一层不加激活（或加 Softmax，但运行时内部会处理）

// 完成构建，生成 FileData（TArray64<uint8>）
TArray64<uint8> FileData;
Builder.SerializeToData(FileData);

// 将 FileData 保存到文件或直接传给 NNE
```

#### 2. 通过 NNE 加载模型并推理

```cpp
#include "NNEModelData.h"
#include "NNERuntimeCPU.h"

// 假设已获取 FileData（TArray64<uint8>）
UNNEModelData* ModelData = NewObject<UNNEModelData>();
ModelData->Init(TEXT("ubnne"), FileData, FGuid::NewGuid());

// 获取 CPU 模型实例
TSharedPtr<UE::NNE::IModelCPU> ModelCPU = UNNERuntimeBasicCpuImpl::CreateModelCPU(ModelData);
TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = ModelCPU->CreateModelInstanceCPU();

// 设置输入形状（BatchSize=1, InputSize=784）
FTensorShape InputShape = FTensorShape::Make({1, 784});
Instance->SetInputTensorShapes({InputShape});

// 准备输入/输出缓冲（float32，连续内存）
TArray<float> InputData;
InputData.SetNum(784);
TArray<float> OutputData;
OutputData.SetNum(10);

FTensorBindingCPU InputBinding;
InputBinding.Data = InputData.GetData();
InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

FTensorBindingCPU OutputBinding;
OutputBinding.Data = OutputData.GetData();
OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

// 执行推理
Instance->RunSync({InputBinding}, {OutputBinding});

// OutputData 现在包含推理结果
```

### 进阶用法

#### 使用 Python 脚本导出模型

插件 Content 文件夹中提供了 `nne_runtime_basic_cpu.py`，可以在训练完成后导出为 `.ubnne` 文件（参考 Python 文档）。

## Demo 示例

以下是一个完整的最小 C++ 示例，演示如何加载预训练的 `.ubnne` 文件并推理。

**MyModelRunner.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNEModelData.h"
#include "NNERuntimeCPU.h"

class FModelRunner
{
public:
    bool LoadModel(const FString& FilePath, int32 InInputSize, int32 InOutputSize);
    TArray<float> RunInference(const TArray<float>& Input);

private:
    TSharedPtr<UE::NNE::IModelInstanceCPU> Instance;
    int32 InputSize;
    int32 OutputSize;
};
```

**MyModelRunner.cpp**
```cpp
#include "MyModelRunner.h"
#include "NNERuntimeBasicCpu.h"          // UNNERuntimeBasicCpuImpl
#include "Misc/FileHelper.h"

bool FModelRunner::LoadModel(const FString& FilePath, int32 InInputSize, int32 InOutputSize)
{
    // 读取 .ubnne 文件
    TArray64<uint8> FileData;
    if (!FFileHelper::LoadFileToArray(FileData, *FilePath))
        return false;

    // 创建 ModelData
    UNNEModelData* ModelData = NewObject<UNNEModelData>();
    ModelData->Init(TEXT("ubnne"), FileData, FGuid::NewGuid());

    // 获取运行时并创建模型
    UNNERuntimeBasicCpuImpl* Runtime = GetMutableDefault<UNNERuntimeBasicCpuImpl>();
    if (!Runtime->CanCreateModelCPU(ModelData))
        return false;

    TSharedPtr<UE::NNE::IModelCPU> ModelCPU = Runtime->CreateModelCPU(ModelData);
    if (!ModelCPU)
        return false;

    Instance = ModelCPU->CreateModelInstanceCPU();
    if (!Instance)
        return false;

    InputSize = InInputSize;
    OutputSize = InOutputSize;
    return true;
}

TArray<float> FModelRunner::RunInference(const TArray<float>& Input)
{
    // 设置形状
    UE::NNE::FTensorShape Shape = UE::NNE::FTensorShape::Make({1, InputSize});
    Instance->SetInputTensorShapes({Shape});

    // 准备绑定
    UE::NNE::FTensorBindingCPU InputBinding;
    InputBinding.Data = const_cast<float*>(Input.GetData());
    InputBinding.SizeInBytes = Input.Num() * sizeof(float);

    TArray<float> Output;
    Output.SetNum(OutputSize);
    UE::NNE::FTensorBindingCPU OutputBinding;
    OutputBinding.Data = Output.GetData();
    OutputBinding.SizeInBytes = Output.Num() * sizeof(float);

    // 运行
    Instance->RunSync({InputBinding}, {OutputBinding});
    return Output;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎接口（`INNERuntime`, `IModelCPU` 等） |
| `NNECore` | NNE 基础类型（`FTensorShape`, `FTensorBindingCPU` 等） |

其余依赖（Core, CoreUObject, Engine 等）为标准模块，不赘述。

## 维护状态

### 近期更新

- 2025-07-30 e35f1513 — [NNERuntimeBasicCpu] ISPC optimization
- 2025-07-25 c3a842ef — [NNE] [LearningAgents] Trivial - Quality of Life Structs
- 2025-07-18 d4a11ffa — [LearningAgents] [NNE] Conv2d
- 2025-06-26 ec900998 — Added UE_INLINE_GENERATED_CPP_BY_NAME to source files
- 2025-06-03 344cde1a — [NNERuntimeBasicCpu ispc] added pragma ignore to fix compile warning

### 维护评价

该插件创建于 2025 年 6 月，目前处于**活跃维护**状态。最近的更新包括性能优化（ISPC）、与 LearningAgents 集成的调整以及编译修复。虽然被标记为实验性，但功能已基本可用，且代码结构清晰。建议在需要轻量 CPU 推理的场景中使用。

**注意**：该插件仍处于实验阶段，API 可能发生变动。生产环境使用前请充分测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeBasicCpu)
- [Python export script (Content folder)](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Experimental/NNERuntimeBasicCpu/Content/nne_runtime_basic_cpu.py)
- [NNE 官方文档](https://docs.unrealengine.com/5.7/API/Plugins/NNE/)