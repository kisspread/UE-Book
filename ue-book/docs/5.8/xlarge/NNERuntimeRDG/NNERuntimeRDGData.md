# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | RDG神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-06 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是一个 **基于渲染依赖图（Render Dependency Graph， RDG）** 实现的神经网络推理运行时。它作为 Unreal Engine 5 的核心神经网络引擎（NNE）的可插拔后端之一，旨在利用 UE 的 RDG 系统进行高性能的 GPU 计算。

该插件的核心作用是将 ONNX 格式的神经网络模型编译和优化为可在 RDG 管线中高效执行的 **计算图（Compute Graph）**。与传统的 CPU 推理或直接的图形API调用相比，使用 RDG 可以：
- **自动管理资源生命周期**：临时 GPU 缓冲区由 RDG 自动分配和回收，简化了内存管理。
- **优化 GPU 工作负载**：RDG 负责调度和合并 GPU 命令，减少状态切换和同步开销。
- **与渲染管线无缝集成**：推理任务可以轻松地作为计算通道插入到现有的渲染流程中，实现神经网络与图形的深度耦合，例如用于实时风格迁移或图像增强。

简单来说，此插件存在是为了在需要高性能 GPU 推理且希望与 UE 渲染架构紧密结合的项目中，提供一种现代化、高效的神经网络模型执行方案。

## 使用场景

- 你需要在 UE 项目中运行预训练的 ONNX 模型，并且对推理性能有很高要求，特别是需要充分利用 GPU 的计算能力时。
- 你的神经网络推理逻辑需要与游戏的渲染管线紧密集成（例如，在渲染管线的某个阶段插入一个计算着色器进行图像后处理）。
- 你正在开发依赖机器学习技术的实时应用，如动态环境交互、AI 决策或内容生成，并希望它能够无缝地利用引擎的 GPU 基础设施。
- （当前阶段）你正在研究或实验 UE 的 NNE 框架，并希望尝试其基于 RDG 的高性能运行时实现。

## 蓝图用法

由于提供的源码片段主要聚焦于 `NNERuntimeRDGData` 模块的数据结构定义，且该模块为 `Runtime` 类型，其公共接口（如 `UFUNCTION`）可能位于其他关联模块（如 `NNERuntimeRDG` 主模块）中。从现有数据结构来看，本插件主要为 C++ 开发者提供了底层数据操作接口，**直接的蓝图节点可能有限**。实际使用中，神经网络的加载和运行更可能通过上层 NNE 的公共蓝图 API 间接完成。

### 核心节点

（基于当前分析的 `NNERuntimeRDGData` 模块，主要为内部数据结构，暂无公共蓝图节点信息）

### 使用示例（蓝图描述）

（基于现有信息，暂无直接可描述的蓝图用法示例。）

## C++ 用法

以下用法主要基于对 `NNERuntimeRDGData` 模块源码的分析，该模块定义了模型数据在 RDG 运行时中的内部表示和序列化格式。

### 头文件引入

```cpp
// 引入模型数据格式的定义
#include "Internal/NNERuntimeRDGDataFormat.h"
// 引入属性值工具
#include "Internal/NNERuntimeRDGDataAttributeValue.h"
```

### 基本用法

该插件的 `NNERuntimeRDGData` 模块主要提供模型数据的结构化表示。开发者通常不会直接构建这些结构，而是由模型导入/编译流程生成。以下代码展示了这些数据结构的概念性使用：

```cpp
// 假设已经有一个解析好的模型数据
FNNERuntimeRDGDataModelFormat ModelData;

// 添加一个输入张量描述
FNNERuntimeRDGDataTensorDesc InputTensorDesc;
InputTensorDesc.Name = TEXT("input_image");
InputTensorDesc.Shape = { 1, 3, 256, 256 }; // 1x3x256x256
InputTensorDesc.Type = ENNERuntimeRDGDataTensorType::Input;
InputTensorDesc.DataType = ENNETensorDataType::Float;
InputTensorDesc.DataSize = sizeof(float) * 1 * 3 * 256 * 256;
InputTensorDesc.DataOffset = 0;
ModelData.Tensors.Add(InputTensorDesc);

// 添加一个 Relu 操作符描述
FNNERuntimeRDGDataOperatorDesc ReluOpDesc;
ReluOpDesc.TypeName = TEXT("Relu");
ReluOpDesc.DomainName = TEXT("onnx");
ReluOpDesc.Version = 13;
ReluOpDesc.InTensors = { 0 }; // 假设索引0是上一个操作的输出
ReluOpDesc.OutTensors = { 1 }; // 假设索引1是本操作的输出
ModelData.Operators.Add(ReluOpDesc);

// （伪代码）将构建好的模型数据序列化存储或传递给编译器
// ModelData.Serialize(Ar);
```
*（来源：`Internal/NNERuntimeRDGDataFormat.h` 中 `FNNERuntimeRDGDataModelFormat` 的使用逻辑）*

### 进阶用法

属性（Attribute）系统用于为算子传递额外的参数。可以利用 `FAttributeMap` 和 `FNNERuntimeRDGDataAttributeValue` 来管理算子的属性。

```cpp
#include "Internal/NNERuntimeRDGDataAttributeMap.h"
#include "Internal/NNERuntimeRDGDataAttributeTensor.h"

using namespace UE::NNERuntimeRDGData::Internal;

// 为某个算子（例如 Conv）设置属性
FAttributeMap OpAttributes;

// 设置一个浮点数组属性
OpAttributes.SetAttribute(TEXT("kernel_shape"), FNNERuntimeRDGDataAttributeValue(TArray<float>{3.0f, 3.0f}));

// 设置一个字符串属性
OpAttributes.SetAttribute(TEXT("auto_pad"), FNNERuntimeRDGDataAttributeValue(FString(TEXT("SAME_UPPER"))));

// 设置一个自定义的张量属性（例如一个常量权重）
TArray<float> KernelData = { /* ... 卷积核数据 ... */ };
NNE::FTensorShape KernelShape = NNE::FTensorShape::Make({ 64, 3, 3, 3 });
FAttributeTensor KernelTensor = FAttributeTensor::Make(KernelShape, ENNETensorDataType::Float, MakeConstArrayView(reinterpret_cast<const uint8*>(KernelData.GetData()), KernelData.Num() * sizeof(float)));
OpAttributes.SetAttribute(TEXT("kernel"), FNNERuntimeRDGDataAttributeValue(KernelTensor));

// 稍后读取属性
float PaddingVal = OpAttributes.GetValueOrDefault<float>(TEXT("padding"), 0.0f);
FString AutoPadStr = OpAttributes.GetValue<FString>(TEXT("auto_pad"));

// 构造算子描述时关联属性
FNNERuntimeRDGDataOperatorDesc ConvOpDesc;
// ... 设置 TypeName, DomainName, InTensors, OutTensors ...
// 将 FAttributeMap 中的信息转换为 TArray<FNNERuntimeRDGDataAttributeDesc> 赋给 ConvOpDesc.Attributes
```
*（来源：`Internal/NNERuntimeRDGDataAttributeMap.h`， `Internal/NNERuntimeRDGDataAttributeValue.h`， `Internal/NNERuntimeRDGDataAttributeTensor.h` 的组合使用）*

## Demo 示例

一个最小化的示例，展示如何构造并序列化一个简单的 `FNNERuntimeRDGDataModelFormat` 对象。

```cpp
// MyNNEDataDemo.h
#pragma once
#include "Internal/NNERuntimeRDGDataFormat.h"
#include "Serialization/MemoryWriter.h"
#include "Serialization/MemoryReader.h"

DECLARE_LOG_CATEGORY_EXTERN(LogNNEDataDemo, Log, All);

class FMyNNEDataDemo
{
public:
    static void CreateAndSerializeDemoModel();
};
```

```cpp
// MyNNEDataDemo.cpp
#include "MyNNEDataDemo.h"

DEFINE_LOG_CATEGORY(LogNNEDataDemo);

void FMyNNEDataDemo::CreateAndSerializeDemoModel()
{
    FNNERuntimeRDGDataModelFormat DemoModel;

    // 1. 定义一个输入张量
    FNNERuntimeRDGDataTensorDesc InputTensor;
    InputTensor.Name = TEXT("Input");
    InputTensor.Shape = { 1, 1 }; // 1x1
    InputTensor.Type = ENNERuntimeRDGDataTensorType::Input;
    InputTensor.DataType = ENNETensorDataType::Float;
    InputTensor.DataSize = sizeof(float); // 单个浮点数
    InputTensor.DataOffset = 0;
    DemoModel.Tensors.Add(InputTensor);

    // 2. 定义一个输出张量
    FNNERuntimeRDGDataTensorDesc OutputTensor;
    OutputTensor.Name = TEXT("Output");
    OutputTensor.Shape = { 1, 1 };
    OutputTensor.Type = ENNERuntimeRDGDataTensorType::Output;
    OutputTensor.DataType = ENNETensorDataType::Float;
    OutputTensor.DataSize = sizeof(float);
    OutputTensor.DataOffset = 0; // 假设输入输出数据不共享
    DemoModel.Tensors.Add(OutputTensor);

    // 3. 定义一个简单的“加一”操作（用 Add 算子和常量权重模拟）
    FNNERuntimeRDGDataOperatorDesc AddOp;
    AddOp.TypeName = TEXT("Add");
    AddOp.DomainName = TEXT("onnx");
    AddOp.Version = 13;
    // 假设 Tensor 索引: 0=Input, 1=Weight, 2=Output
    AddOp.InTensors = { 0, 1 }; // 输入和权重
    AddOp.OutTensors = { 2 };
    DemoModel.Operators.Add(AddOp);

    // 4. 添加一个权重张量（常量1.0f）
    FNNERuntimeRDGDataTensorDesc WeightTensor;
    WeightTensor.Name = TEXT("Weight_One");
    WeightTensor.Shape = { 1, 1 };
    WeightTensor.Type = ENNERuntimeRDGDataTensorType::Initializer;
    WeightTensor.DataType = ENNETensorDataType::Float;
    WeightTensor.DataSize = sizeof(float);
    WeightTensor.DataOffset = 0; // 假设数据在文件末尾
    DemoModel.Tensors.Add(WeightTensor);

    // 5. 设置模型的原始权重数据
    const float WeightValue = 1.0f;
    DemoModel.TensorData.Append(reinterpret_cast<const uint8*>(&WeightValue), sizeof(float));

    // 6. 序列化模型到内存（模拟保存）
    TArray<uint8> SerializedData;
    FMemoryWriter ArWriter(SerializedData, true);
    DemoModel.Serialize(ArWriter);

    UE_LOG(LogNNEDataDemo, Log, TEXT("Serialized demo model to %d bytes."), SerializedData.Num());

    // 7. 从内存反序列化（模拟加载）
    FNNERuntimeRDGDataModelFormat LoadedModel;
    FMemoryReader ArReader(SerializedData, true);
    LoadedModel.Serialize(ArReader);

    if (LoadedModel.Tensors.Num() == 3 && LoadedModel.Operators.Num() == 1)
    {
        UE_LOG(LogNNEDataDemo, Log, TEXT("Successfully loaded model with %d tensors and %d operators."),
            LoadedModel.Tensors.Num(), LoadedModel.Operators.Num());
    }
}
```

## 模块依赖

从各模块的 `Build.cs` 分析，此插件依赖一些特定的图形 RHI 模块和内部工具模块。

| 模块 | 用途 |
|---|---|
| `MetalRHI` | 提供 Apple Metal 图形 API 的 RHI 实现，用于在 macOS/iOS 上执行 RDG 计算。 |
| `VulkanRHI` | 提供 Vulkan 图形 API 的 RHI 实现，用于在 Windows、Linux 等平台上执行 RDG 计算。 |
| `NNERuntimeRDGUtils` | 提供编辑器专用的工具和辅助功能（如模型导入、转换）。 |
| `NNE` | UE 的神经网络引擎核心模块，提供公共 API、张量定义和运行时注册表。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串中，参数为64位时使用32位说明符（反之亦然）的问题。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除了旧的 `BlockUntilGPUIdle` 和 `SubmitCommandsAndFlushGPU` 函数，统一使用新的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了与旧版 GPU 分析器相关的宏。 |

### 维护评价

**NNERuntimeRDG** 是一个于 2023 年创建的**实验性插件**。从近期的提交记录（截至 2026 年）看，它仍在**活跃维护**中，主要更新集中在**编译兼容性修复**、**代码现代化**（宏迁移）和**内部API整理**，而非大幅度的功能新增。这表明该插件的核心功能可能已趋于稳定，当前工作重点在于保证其在最新引擎版本中的可靠性和代码质量。

由于其**实验性状态**（`IsExperimentalVersion = true`）和**默认禁用**（`EnabledByDefault = false`）的特性，该插件 API 可能仍在演进中，不建议在追求稳定性的商业项目的核心路径中依赖它。但对于技术预研、原型开发或内部工具项目，这是一个值得关注和尝试的高性能神经网络推理方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档]()（暂无）
- [测试用例]()（可能位于引擎的自动化测试目录中，具体路径待确认）