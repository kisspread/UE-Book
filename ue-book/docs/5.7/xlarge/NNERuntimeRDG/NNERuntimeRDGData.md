# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | NNE RDG运行时数据 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

本模块（`NNERuntimeRDGData`）是 NNERuntimeRDG 插件中的数据表示层。它提供了一组用于描述神经网络模型的内部数据结构，包括：

- **属性值容器**：`FNNERuntimeRDGDataAttributeValue` 与 `FAttributeMap`，支持多种类型的属性值（float、int32、string、tensor 及其数组），并支持序列化。
- **模型拓扑描述**：`FNNERuntimeRDGDataModelFormat` 定义了完整的模型格式，包含张量描述（输入/输出/中间/初始化）、算子描述（类型、域、版本、输入输出张量索引、属性）以及原始权重数据。
- **张量属性数据**：`FAttributeTensor` 提供了张量形状、数据类型和原始数据的封装，配合 `FNNERuntimeRDGDataAttributeValue` 可存储模型中的常量张量（如 ONNX 的 initializer）。

该模块不直接参与推理执行，而是作为推理准备阶段的数据中转与模型结构化表示的核心。它的存在使得 `NNERuntimeRDG` 运行时可以独立于特定的模型格式（如 ONNX）解析，而是使用本模块的标准数据格式进行后续的算子注册与 RDG 计算图构建。

## 使用场景

- **加载并解析 ONNX 模型**：当 `NNERuntimeRDG` 读入 ONNX 文件后，会将模型中的 node、initializer、input/output 等元素转换为 `FNNERuntimeRDGDataModelFormat` 结构，供后续计算图生成使用。
- **自定义模型导入工具**：如果你需要从其他格式（如 PyTorch 导出的自定义序列化）构建推理图，可以手动填充 `FNNERuntimeRDGDataModelFormat` 中的 Tensor、Operator 和 Attribute 数据，然后利用 `NNERuntimeRDG` 的图构建 API 生成 RDG 计算图。
- **模型可视化或调试**：通过访问 `FNNERuntimeRDGDataModelFormat` 的公开属性，可以在编辑器中展示模型的层次结构（张量名称、形状、算子类型等）。

## 蓝图用法

本模块是一个纯 C++ 数据层，**没有公开任何蓝图标明的函数或可调用节点**。`FNNERuntimeRDGDataAttributeValue`、`FNNERuntimeRDGDataAttributeDesc`、`FNNERuntimeRDGDataOperatorDesc` 等结构是 `USTRUCT`，但未标记 `BlueprintType`，因此不能在蓝图中直接创建或读写。所有操作均需在 C++ 中完成。

如果需要从蓝图获取模型元信息，建议通过 `NNERuntimeRDG` 插件中的其他模块提供蓝图友好的封装，或者在使用前将本模块的数据导出至 `UObject` 派生类。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeRDGData"
#include "Internal/NNERuntimeRDGDataFormat.h"  // 核心模型格式结构
#include "Internal/NNERuntimeRDGDataAttributeMap.h"  // 属性映射
#include "Internal/NNERuntimeRDGDataAttributeTensor.h"
#include "Internal/NNERuntimeRDGDataAttributeValue.h"
```

### 基本用法

#### 创建并查询属性映射

```cpp
// Source: Testing/... (模拟使用场景)
#include "Internal/NNERuntimeRDGDataAttributeMap.h"

using namespace UE::NNERuntimeRDGData::Internal;

FAttributeMap AliasMap;

// 设置 float 属性
AliasMap.SetAttribute<float>(TEXT("scale"), 1.5f);

// 设置 int32 属性
AliasMap.SetAttribute<int32>(TEXT("axis"), -1);

// 设置字符串属性
AliasMap.SetAttribute<FString>(TEXT("mode"), TEXT("nearest"));

// 获取属性（必须存在）
float Scale = AliasMap.GetValue<float>(TEXT("scale"));   // 1.5f
int32 Axis = AliasMap.GetValue<int32>(TEXT("axis"));     // -1

// 安全获取（带默认值）
FString Mode = AliasMap.GetValueOrDefault<FString>(TEXT("mode"), TEXT("linear")); // "nearest"
FString Missing = AliasMap.GetValueOrDefault<FString>(TEXT("padding"), TEXT("zeros")); // "zeros"
```

#### 使用属性张量

```cpp
// 创建一个 2x3 的 float 张量
NNE::FTensorShape Shape = NNE::FTensorShape::Make({2, 3});
TArray<uint8> RawData;
RawData.AddUninitialized(2 * 3 * sizeof(float));
float* DataPtr = reinterpret_cast<float*>(RawData.GetData());
DataPtr[0] = 1.0f; DataPtr[1] = 2.0f; DataPtr[2] = 3.0f;
DataPtr[3] = 4.0f; DataPtr[4] = 5.0f; DataPtr[5] = 6.0f;

FAttributeTensor Tensor = FAttributeTensor::Make(Shape, ENNETensorDataType::Float, RawData);
check(Tensor.GetDataType() == ENNETensorDataType::Float);
check(Tensor.GetShape().Rank() == 2);
check(Tensor.GetShape().GetData()[0] == 2);
check(Tensor.GetShape().GetData()[1] == 3);

// 序列化
FMemoryWriter Ar(RawData);
Ar << Tensor;
```

#### 构建模型格式

```cpp
// 填充 FNNERuntimeRDGDataModelFormat 并序列化
FNNERuntimeRDGDataModelFormat Model;

Model.Tensors.Add(/*...*/);
Model.Operators.Add(/*...*/);
Model.DataSize = 1024;
Model.TensorData.AddUninitialized(Model.DataSize);

FBufferArchive Ar;
Model.Serialize(Ar);
// Ar 现在包含完整的模型描述，可写入磁盘或传递给其他模块
```

### 进阶用法

#### 使用 `FNNERuntimeRDGDataAttributeValue` 作为通用变体存储

```cpp
FNNERuntimeRDGDataAttributeValue Val1(42);               // int32
FNNERuntimeRDGDataAttributeValue Val2(3.14f);            // float
FNNERuntimeRDGDataAttributeValue Val3(FString("hello")); // string

int32 I = Val1.GetValue<int32>();      // 42
float F = Val2.GetValue<float>();      // 3.14f
FString S = Val3.GetValue<FString>();  // "hello"

ENNERuntimeRDGDataAttributeDataType Type = Val1.GetType(); // Int32
```

## Demo 示例

以下示例展示如何创建一个包含单个卷积算子和一个初始化张量的模型格式，然后将其序列化到 `FBufferArchive`。

**MyModelBuilder.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Algo/Transform.h"
#include "Internal/NNERuntimeRDGDataFormat.h"
#include "Internal/NNERuntimeRDGDataAttributeMap.h"
#include "Internal/NNERuntimeRDGDataAttributeTensor.h"
#include "Serialization/BufferArchive.h"
#include "Serialization/MemoryReader.h"

class FMyModelBuilder
{
public:
    // 构建一个简单模型：Conv + Add
    static UE::NNERuntimeRDGData::Internal::FNNERuntimeRDGDataModelFormat BuildConvolutionModel();
};
```

**MyModelBuilder.cpp**

```cpp
#include "MyModelBuilder.h"

using namespace UE::NNERuntimeRDGData::Internal;

FNNERuntimeRDGDataModelFormat FMyModelBuilder::BuildConvolutionModel()
{
    FNNERuntimeRDGDataModelFormat Model;

    // ---- 张量定义 ----
    // Input tensor (N=1, C=1, H=3, W=3)
    FNNERuntimeRDGDataTensorDesc InputDesc;
    InputDesc.Name = TEXT("input");
    InputDesc.Shape = {1, 1, 3, 3};
    InputDesc.Type = ENNERuntimeRDGDataTensorType::Input;
    InputDesc.DataType = ENNETensorDataType::Float;
    InputDesc.DataSize = 1 * 1 * 3 * 3 * sizeof(float);
    InputDesc.DataOffset = 0;
    Model.Tensors.Add(InputDesc);

    // Weight tensor (1x1x2x2)
    FNNERuntimeRDGDataTensorDesc WeightDesc;
    WeightDesc.Name = TEXT("weight");
    WeightDesc.Shape = {1, 1, 2, 2};
    WeightDesc.Type = ENNERuntimeRDGDataTensorType::Initializer;
    WeightDesc.DataType = ENNETensorDataType::Float;
    WeightDesc.DataSize = 1 * 1 * 2 * 2 * sizeof(float);
    WeightDesc.DataOffset = InputDesc.DataSize; // 紧跟 input 数据
    Model.Tensors.Add(WeightDesc);

    // Output tensor (N=1, C=1, H=2, W=2) after valid convolution
    FNNERuntimeRDGDataTensorDesc OutputDesc;
    OutputDesc.Name = TEXT("output");
    OutputDesc.Shape = {1, 1, 2, 2};
    OutputDesc.Type = ENNERuntimeRDGDataTensorType::Output;
    OutputDesc.DataType = ENNETensorDataType::Float;
    OutputDesc.DataSize = 1 * 1 * 2 * 2 * sizeof(float);
    OutputDesc.DataOffset = WeightDesc.DataOffset + WeightDesc.DataSize;
    Model.Tensors.Add(OutputDesc);

    // ---- 算子定义 ----
    FNNERuntimeRDGDataOperatorDesc ConvOp;
    ConvOp.TypeName = TEXT("Conv");
    ConvOp.DomainName = TEXT("onnx");
    ConvOp.Version = 11;
    ConvOp.InTensors = {0, 1};          // 索引对应 input & weight
    ConvOp.OutTensors = {2};            // 索引 output
    // 属性：dilations, group, kernel_shape, pads, strides
    FNNERuntimeRDGDataAttributeMap AttrMap;
    AttrMap.SetAttribute<TArray<int32>>(TEXT("dilations"), {1, 1});
    AttrMap.SetAttribute<int32>(TEXT("group"), 1);
    AttrMap.SetAttribute<TArray<int32>>(TEXT("kernel_shape"), {2, 2});
    AttrMap.SetAttribute<TArray<int32>>(TEXT("pads"), {0, 0, 0, 0});
    AttrMap.SetAttribute<TArray<int32>>(TEXT("strides"), {1, 1});

    for (int32 i = 0; i < AttrMap.Num(); ++i)
    {
        FNNERuntimeRDGDataAttributeDesc AttrDesc;
        AttrDesc.Name = AttrMap.GetName(i);
        AttrDesc.Value = AttrMap.GetAttributeValue(i);
        ConvOp.Attributes.Add(AttrDesc);
    }
    Model.Operators.Add(ConvOp);

    // ---- 填充张量数据 ----
    // 简单赋数值：input 全1，weight 全0.5
    auto FillTensor = [](TArray64<uint8>& Dest, uint64 Offset, uint64 Size, float Value)
    {
        check(Offset + Size <= Dest.Num());
        float* Data = reinterpret_cast<float*>(Dest.GetData() + Offset);
        for (uint64 i = 0; i < Size / sizeof(float); ++i)
            Data[i] = Value;
    };
    Model.TensorData.AddUninitialized(InputDesc.DataSize + WeightDesc.DataSize + OutputDesc.DataSize);
    FillTensor(Model.TensorData, InputDesc.DataOffset, InputDesc.DataSize, 1.0f);
    FillTensor(Model.TensorData, WeightDesc.DataOffset, WeightDesc.DataSize, 0.5f);

    Model.DataSize = Model.TensorData.Num();
    return Model;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 提供核心类型如 `ENNETensorDataType`、`FTensorShape` 等推理基础结构 |
| （无特殊依赖） | 所有其他依赖均为标准 Core/Engine/Slate 等常见模块 |

## 维护状态

### 近期更新

- 2025-07-24 `2412ec9f` 使 TArrayView 和 Invoke 为 constexpr；修复 TStaticArray 中的 UB 以及对齐弃用
- 2025-06-12 `9ce28ae0` 更新 numeric limits 使用标准库而非宏，修复新 Windows SDK 编译
- 2025-06-12 `d9dba260` [NNE] NNERuntimeRDGHlsl arm64 支持
- 2025-06-03 `d31855b9` 修复 libprotobuf-lite 构建脚本，添加 Windows arm64 版本
- 2025-05-29 `8cfef610` 向使用 TGreater 的文件添加 Greater.h 包含

### 维护评价

本模块创建于 2025 年 5 月，距离编写日期（2026 年约 1 年），更新频率高且内容涉及跨平台编译修复和性能改进。插件整体仍处于实验性阶段（`IsExperimentalVersion=true`），API 和数据结构可能在未来版本中发生变化。建议用于技术预览和评估，但不推荐在正式产品中依赖其 AB I 稳定性。对于需要稳定推理流程的团队，可关注后续版本的非实验性更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 官方文档](https://docs.unrealengine.com/5.4/zh-CN/neural-network-engine-in-unreal-engine/)（需根据你的引擎版本查看）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNERuntimeRDGData/Private/Tests)