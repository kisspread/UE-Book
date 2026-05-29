# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | RDG神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (Runtime), `NNERuntimeRDG` (Runtime), `NNERuntimeRDGData` (Runtime), `NNERuntimeRDGUtils` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

该插件为虚幻引擎的 **神经网络引擎 (NNE)** 提供了一个**利用渲染依赖图 (RDG) 和 GPU 着色器 (HLSL)** 的运行时实现。其核心作用是将机器学习模型的推理任务，特别是张量计算，卸载到 GPU 上执行，以获得比纯 CPU 运行时（如基于 ONNX Runtime CPU 的运行时）**更高的性能**。

它解决的主要问题是：**在游戏和实时应用中，如何高效地运行复杂的神经网络模型进行实时推理（例如物体识别、风格转换、决策 AI），同时最小化对 CPU 的影响**。通过利用 RDG，该运行时能够更好地与引擎的渲染管线进行调度和资源共享。

## 使用场景

-   **游戏内实时 AI**：需要在每帧或高频进行推理的决策模型或感知模型。
-   **视觉效果与后处理**：例如使用神经网络进行实时图像超分辨率、风格转换或去噪。
-   **物体与场景理解**：基于摄像头或游戏内图像输入的实时物体检测、分割。
-   **物理模拟增强**：使用机器学习来加速或增强复杂的物理模拟计算。
-   适用于目标平台（如 Windows、Linux、Mac）的显卡支持计算着色器，且对 GPU 推理性能有明确需求的项目。

## 蓝图用法

`NNERuntimeRDGUtils` 模块主要为模型优化和构建提供内部工具接口，不直接向蓝图暴露可调用的函数或属性。模型的加载、初始化和推理通常通过核心 `NNE` 模块的蓝图接口完成，而本插件作为底层运行时被自动使用。

## C++ 用法

该插件的核心功能（模型优化、构建）封装在 `NNERuntimeRDGUtils` 模块中，主要用于 C++ 端的模型预处理流程。

### 头文件引入

```cpp
#include "NNERuntimeRDGUtilsModelOptimizer.h"
#include "NNERuntimeRDGUtilsModelBuilder.h"
```

### 基本用法：模型优化

优化器用于将 ONNX 格式的模型转换为适用于本插件 RDG/HLSL 运行时的内部格式。

```cpp
// 来源: Internal/NNERuntimeRDGUtilsModelOptimizer.h
#include "NNERuntimeRDGUtilsModelOptimizer.h"

// 1. 创建模型优化器实例
TUniquePtr<UE::NNERuntimeRDGUtils::Internal::IModelOptimizer> Optimizer = UE::NNERuntimeRDGUtils::Internal::CreateModelOptimizer();

// 2. 加载原始 ONNX 模型数据到 `InputModelData` (TArray<uint8>)
TArray<uint8> InputModelData; // ... 从文件或内存加载

// 3. 执行优化，将结果输出到 `OptimizedModelData`
TArray<uint8> OptimizedModelData;
bool bSuccess = Optimizer->Optimize(InputModelData, OptimizedModelData);

if (bSuccess)
{
    // `OptimizedModelData` 现在可以传递给 NNE 运行时进行加载和推理
}
```

### 进阶用法：自定义优化流程

优化器允许添加自定义的优化过程和验证器。

```cpp
// 来源: Internal/NNERuntimeRDGUtilsModelOptimizerInterface.h
#include "NNERuntimeRDGUtilsModelOptimizer.h"

// 定义一个简单的验证器，确保模型不为空
class FNonEmptyModelValidator : public UE::NNERuntimeRDGUtils::Internal::IModelValidator
{
public:
    virtual FString GetName() const override { return TEXT("NonEmptyValidator"); }
    virtual bool ValidateModel(TConstArrayView<uint8> InputModel) const override
    {
        return InputModel.Num() > 0;
    }
};

// 使用
TUniquePtr<UE::NNERuntimeRDGUtils::Internal::IModelOptimizer> Optimizer = UE::NNERuntimeRDGUtils::Internal::CreateModelOptimizer();

// 添加自定义验证器
Optimizer->AddValidator(MakeShared<FNonEmptyModelValidator>());

// 优化器内部已包含默认的优化过程（如ONNX到NNE格式转换）
// 执行优化
TArray<uint8> OutModel;
bool bValidAndOptimized = Optimizer->Optimize(InputModelData, OutModel);
```

### 进阶用法：模型构建

`IModelBuilder` 提供了一个更底层的接口，用于以编程方式构建模型（例如，将 ONNX 模型转换为 NNE 原生格式）。

```cpp
// 来源: Private/NNERuntimeRDGUtilsModelBuilder.h
#include "NNERuntimeRDGUtilsModelBuilder.h"

// 假设我们有一个从ONNX解析出的模型图，需要转换为NNE格式
// 创建NNE模型构建器
TUniquePtr<UE::NNERuntimeRDGUtils::Private::IModelBuilder> Builder = UE::NNERuntimeRDGUtils::Private::CreateNNEModelBuilder();

// 开始构建
Builder->Begin(TEXT("MyConvertedGraph"));

// 添加张量（例如，输入、权重）
auto InputTensorHandle = Builder->AddInputTensor(Builder->AddTensor(TEXT("input"), ENNETensorDataType::Float, {1, 3, 224, 224}));

// 添加算子
auto ConvOpHandle = Builder->AddOperator(TEXT("Conv"), TEXT("Onnx"));
Builder->AddOperatorInput(ConvOpHandle, InputTensorHandle);
// ... 添加权重、属性、输出

// 结束构建并获取序列化数据
TArray<uint8> NNEModelData;
Builder->End(NNEModelData);
```

## Demo 示例

一个演示如何加载ONNX模型、使用优化器并最终创建推理模型的最小C++示例。

**MyNNEDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "MyNNEDemoActor.generated.h"

UCLASS()
class MYPROJECT_API AMyNNEDemoActor : public AActor
{
    GENERATED_BODY()
public:
    virtual void BeginPlay() override;

private:
    TWeakInterfacePtr<INNERuntime> Runtime;
    TWeakInterfacePtr<INNEModelData> ModelData;
    TWeakInterfacePtr<INNEModelGPU> ModelGPU;
};
```

**MyNNEDemoActor.cpp**
```cpp
#include "MyNNEDemoActor.h"
#include "NNE.h"
#include "NNERuntimeRDGUtilsModelOptimizer.h"

void AMyNNEDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 RDG 运行时
    Runtime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeRDGHlsl"));
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("RDG Runtime not available."));
        return;
    }

    // 2. 加载和优化 ONNX 模型 (简化示例，实际需处理文件I/O)
    TArray<uint8> OnnxModelData = /* ... 从文件加载 ... */;
    auto Optimizer = UE::NNERuntimeRDGUtils::Internal::CreateModelOptimizer();
    TArray<uint8> OptimizedData;
    if (!Optimizer->Optimize(OnnxModelData, OptimizedData))
    {
        UE_LOG(LogTemp, Error, TEXT("Model optimization failed."));
        return;
    }

    // 3. 创建模型数据对象
    ModelData = Runtime->CreateModelData(OptimizedData);
    if (!ModelData.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model data."));
        return;
    }

    // 4. 创建 GPU 推理模型
    ModelGPU = Runtime->CreateModelGPU(*ModelData);
    if (!ModelGPU.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create GPU model."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("NNERuntimeRDG model loaded and ready for inference."));
}
```

## 模块依赖

要使用此插件，你的项目模块通常**无需直接添加依赖**。该插件的 `NNERuntimeRDGUtils` 模块依赖于 `NNE` 核心模块。在你的项目中启用此插件后，通过 `NNE` 模块的 API 来选择并使用 `NNERuntimeRDGHlsl` 运行时即可。

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 的核心公共 API 和运行时注册表。 |
| `NNEHlslShaders` | 包含用于 GPU 推理的 HLSL 着色器代码。 |
| `MetalRHI` / `VulkanRHI` | (被 `NNERuntimeRDG` 模块依赖) 对应平台的图形硬件接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量被截断为浮点数的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串与参数位宽不匹配的问题（32位与64位）。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构GPU命令提交与等待机制，统一使用 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至 `UE_LOGF`。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了遗留的 GPU 性能分析相关宏。 |

### 维护评价

-   **创建时间**: 2023年6月，相对年轻的插件。
-   **近期活动**: 截至2026年5月仍有持续的代码提交，主要集中在编译器警告修复、平台兼容性调整和API现代化，表明仍在**积极维护**。
-   **当前状态**: 作为 **实验性 (`IsExperimentalVersion: true`) 且默认未启用 (`EnabledByDefault: false`)** 的插件。这意味着它在API和功能上可能还不稳定，主要面向高级开发者和实验性项目。
-   **已知限制**: 依赖特定的GPU和RHI支持（HLSL），跨平台能力受限于底层图形API。
-   **推荐使用**: **谨慎推荐**。如果你的项目是Windows/Linux/Mac平台，需要高性能GPU推理，并且愿意承担实验性API可能变动的风险，那么这是一个很有潜力的选择。建议密切跟踪其API变化，并准备好后备的CPU推理方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档]() (暂无)
- [测试用例]() (位于 `Engine/Tests/` 或插件目录内，需在源码中搜索 `NNERuntimeRDG`)