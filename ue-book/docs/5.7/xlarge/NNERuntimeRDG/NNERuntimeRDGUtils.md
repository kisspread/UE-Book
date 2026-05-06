# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | NNE RDG 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram), `NNERuntimeRDG` (RuntimeAndProgram), `NNERuntimeRDGData` (RuntimeAndProgram), `NNERuntimeRDGUtils` (EditorAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 Unreal Engine 中神经网络引擎（NNE）的一个运行时实现，其核心执行管道基于渲染依赖图（RDG）。该插件提供了一种在 GPU 上高效运行神经网络推理的方法，利用 RDG 的自动资源管理与异步计算特性，尤其适合与实时渲染管线深度集成的场景。

本插件包含多个子模块，其中 **NNERuntimeRDGUtils** 是一个工具模块，提供模型优化、验证和构建功能。它允许用户将 ONNX 格式的神经网络模型转换为 NNE 内部使用的 RT 格式，或执行 ONNX→ONNX 的优化（如算子融合、消除冗余等）。此外，它还提供了一个模型构建器接口，支持以编程方式从零构建 NNE 模型。

## 使用场景

- 你需要在游戏中运行轻量级神经网络推理，且希望利用 GPU 渲染管线的高效调度。
- 你有一个 ONNX 格式的预训练模型，需要导入到 UE，并利用 RDG 优化执行。
- 你需要对 ONNX 模型进行优化、验证或格式转换，以满足 NNE RuntimeRDG 的要求。
- 你需要以代码方式动态生成神经网络模型（例如在运行时调整网络结构）。

## 蓝图用法

本插件（特别是 NNERuntimeRDGUtils 模块）的接口均为 C++ 原生类，**未暴露蓝图可调用的函数或属性**。所有交互需在 C++ 中完成。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeRDGUtilsModelOptimizer.h"
#include "NNERuntimeRDGUtilsModelBuilderNNE.h"
#include "NNERuntimeRDGUtilsModelOptimizerInterface.h"
```

### 基本用法

#### 创建并运行模型优化器

`NNERuntimeRDGUtils` 提供了 `CreateModelOptimizer` 函数，用于创建默认的模型优化器（ONNX→NNERT 格式）。以下示例展示如何加载一个 ONNX 模型，进行优化并输出优化后的模型。

```cpp
// 文件来源: NNERT 内部测试（模拟）
#include "NNERuntimeRDGUtilsModelOptimizer.h"
#include "HAL/FileManager.h"

using namespace UE::NNERuntimeRDGUtils::Internal;

// 从文件加载 ONNX 二进制数据
TArray<uint8> LoadONNXModel(const FString& FilePath)
{
    TArray<uint8> ModelData;
    FFileHelper::LoadFileToArray(ModelData, *FilePath);
    return ModelData;
}

// 使用默认优化器转换模型
void OptimizeONNXToNNERT()
{
    TUniquePtr<IModelOptimizer> Optimizer = UE::NNERuntimeRDGUtils::Internal::CreateModelOptimizer();
    TArray<uint8> InputModel = LoadONNXModel(TEXT("/Game/Models/MyModel.onnx"));
    TArray<uint8> OutputModel;

    if (Optimizer->Optimize(InputModel, OutputModel))
    {
        // OutputModel 现在是 NNERT 格式（NNE Runtime RDG 内部格式）
        // 可以保存或直接传递给 NNERuntimeRDG 进行推理
        FFileHelper::SaveArrayToFile(OutputModel, TEXT("/Game/Models/MyModel.nnert"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Model optimization failed"));
    }
}
```

#### 获取算子版本号

`NNERuntimeRDGUtils` 的内部辅助函数 `GetOpVersionFromOpsetVersion` 可用于根据 ONNX 算子类型和 opset 版本获取对应算子版本号。

```cpp
// 文件来源: Private/NNERuntimeRDGUtilsHelpers.h
#include "NNERuntimeRDGUtilsHelpers.h"

TOptional<uint32> Version = UE::NNERuntimeRDGUtils::Private::GetOpVersionFromOpsetVersion(TEXT("Conv"), 19);
if (Version.IsSet())
{
    // 使用 Version.GetValue()
}
```

### 进阶用法

#### 自定义优化通道与验证器

你可以为优化器添加自定义的 `IModelOptimizerPass` 和 `IModelValidator`。优化器会依次应用所有 pass，并在每个 pass 之间运行所有验证器。

```cpp
// 文件来源: 基于 Internal 接口示例
#include "NNERuntimeRDGUtilsModelOptimizerInterface.h"

class FCustomOptimizerPass : public UE::NNERuntimeRDGUtils::Internal::IModelOptimizerPass
{
public:
    virtual FString GetName() const override { return TEXT("CustomPass"); }

    virtual bool ApplyPass(TArray<uint8>& Model) const override
    {
        // 对模型数据进行特定变换
        // 返回 true 表示成功
        return true;
    }
};

class FCustomValidator : public UE::NNERuntimeRDGUtils::Internal::IModelValidator
{
public:
    virtual FString GetName() const override { return TEXT("MyValidator"); }

    virtual bool ValidateModel(TConstArrayView<uint8> InputModel) const override
    {
        // 检查模型结构完整性
        return true;
    }
};

void CustomOptimization()
{
    TUniquePtr<IModelOptimizer> Optimizer = CreateModelOptimizer();
    Optimizer->AddOptimizationPass(MakeShared<FCustomOptimizerPass>());
    Optimizer->AddValidator(MakeShared<FCustomValidator>());

    TArray<uint8> Input;
    TArray<uint8> Output;
    Optimizer->Optimize(Input, Output);
}
```

#### 使用模型构建器构建 NNE 模型

模型构建器 (`IModelBuilder`) 允许以编程方式构建 NNE 模型。以下示例创建一个简单的单输入单输出模型（如全连接层）。

```cpp
// 文件来源: Private/NNERuntimeRDGUtilsModelBuilderNNE.h
#include "NNERuntimeRDGUtilsModelBuilderNNE.h"

using namespace UE::NNERuntimeRDGUtils::Private;

void BuildSimpleModel()
{
    TUniquePtr<IModelBuilder> Builder = CreateNNEModelBuilder();
    Builder->Begin(TEXT("MyGraph"));

    // 添加输入张量 (batch, 4)
    IModelBuilder::FHTensor Input = Builder->AddTensor(TEXT("input"), ENNETensorDataType::Float, {1, 4});
    Builder->AddInput(Input);

    // 添加常量权重张量 (4, 4)
    float WeightsData[] = { /* ... */ };
    IModelBuilder::FHTensor Weights = Builder->AddConstantTensor(
        TEXT("weights"), ENNETensorDataType::Float, {4,4}, WeightsData, sizeof(WeightsData));

    // 添加 Gemm 算子 (矩阵乘法)
    IModelBuilder::FHOperator Gemm = Builder->AddOperator(
        TEXT("Gemm"), IModelBuilder::OnnxDomainName, 7, TEXT("MyGemm"));
    Builder->AddOperatorInput(Gemm, Input);
    Builder->AddOperatorInput(Gemm, Weights);
    // 可以设置属性如 alpha=1.0, beta=1.0, transA=0, transB=0
    // Builder->AddOperatorAttribute(Gemm, TEXT("alpha"), ...);

    // 添加输出张量
    IModelBuilder::FHTensor Output = Builder->AddTensor(TEXT("output"), ENNETensorDataType::Float, {1, 4});
    Builder->AddOperatorOutput(Gemm, Output);
    Builder->AddOutput(Output);

    TArray<uint8> ModelData;
    Builder->End(ModelData);
    // ModelData 包含 NNE 格式的序列化模型，可用于推理
}
```

## Demo 示例

以下是一个完整的 C++ 类示例，展示如何将 ONNX 模型转换为 NNERT 格式并保存。

```cpp
// MyModelConverter.h
#pragma once
#include "CoreMinimal.h"

class FMyModelConverter
{
public:
    static bool ConvertONNXToNNERT(const FString& InONNXPath, const FString& OutNNERTPath);
};

// MyModelConverter.cpp
#include "MyModelConverter.h"
#include "NNERuntimeRDGUtilsModelOptimizer.h"
#include "HAL/FileManager.h"

bool FMyModelConverter::ConvertONNXToNNERT(const FString& InONNXPath, const FString& OutNNERTPath)
{
    TArray<uint8> InputModel;
    if (!FFileHelper::LoadFileToArray(InputModel, *InONNXPath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load ONNX file: %s"), *InONNXPath);
        return false;
    }

    TUniquePtr<UE::NNERuntimeRDGUtils::Internal::IModelOptimizer> Optimizer =
        UE::NNERuntimeRDGUtils::Internal::CreateModelOptimizer();

    TArray<uint8> OutputModel;
    if (!Optimizer->Optimize(InputModel, OutputModel))
    {
        UE_LOG(LogTemp, Error, TEXT("Optimization failed for model: %s"), *InONNXPath);
        return false;
    }

    return FFileHelper::SaveArrayToFile(OutputModel, *OutNNERTPath);
}
```

使用方法：

```cpp
FMyModelConverter::ConvertONNXToNNERT(
    TEXT("/Game/Models/ResNet18.onnx"),
    TEXT("/Game/Models/ResNet18.nnert")
);
```

## 模块依赖

### 核心模块（所有子模块共同依赖）

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心接口与类型定义 |

### 各子模块额外依赖

| 子模块 | 依赖模块 | 用途 |
|---|---|---|
| `NNERuntimeRDG` | `MetalRHI`, `VulkanRHI`, `NNERuntimeRDGUtils` | GPU 推理执行层，需要 RHI 绑定与工具模块 |
| `NNERuntimeRDGUtils` | （无额外） | 工具模块仅依赖 `NNE` |

> **说明**：表中未列出的常见依赖（Core, CoreUObject, Engine 等）已被省略。

## 维护状态

### 近期更新

- 2025-07-24 `2412ec9f` — Made TArrayView and Invoke constexpr. Fixed UB GetData and deprecated Alignment in TStaticArray
- 2025-06-12 `9ce28ae0` — Update numeric limits to use std lib instead of macro because it fails to compile on newer Windows 1
- 2025-06-12 `d9dba260` — [NNE] NNERuntimeRDGHlsl arm64 support
- 2025-06-03 `d31855b9` — Fixup build script for libprotobuf-lite & add windows arm64 version
- 2025-05-29 `8cfef610` — Added Greater.h include to files which use TGreater, which will break with an upcoming change to rem

### 维护评价

- **创建时间**：2025‑05‑29（约 3 个月）
- **近期更新**：最近一次提交为 2025‑07‑24，且包含功能增强（arm64 支持）与基础设施改进，更新频率高。
- **活跃度**：非常活跃，持续有神经网络相关功能开发与问题修复。
- **已知问题**：实验性插件，可能有不稳定或不完整的 API。
- **推荐使用**：✅ 推荐，但须注意实验性标签，API 可能发生变动。适合需要 GPU 神经网络推理的 UE5 项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 官方文档](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)
- [测试用例 (部分)](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNERuntimeRDGUtils/Private/Tests)（如存在）