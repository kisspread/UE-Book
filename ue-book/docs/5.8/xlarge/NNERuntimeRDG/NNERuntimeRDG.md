# NNE Runtime RDG

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
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

该插件实现了 UE5 神经网络引擎 (NNE) API 的一个具体运行时，它利用引擎的核心渲染管线——**渲染依赖图 (Render Dependency Graph, RDG)**——在 GPU 上高效执行神经网络推理任务。

不同于基于 CPU 或第三方 GPU 推理库的运行时，此插件将机器学习算子 (如卷积、矩阵乘法、激活函数) 实现为 GPU 着色器 (HLSL)，并将其调度为 RDG 任务。这使得神经网络推理能够与游戏/应用的渲染流程深度集成，充分利用现代 GPU 的并行计算能力，并与 RDG 的自动资源管理、异步计算和调试功能相结合。它主要面向希望利用现有图形管线执行机器学习模型，避免引入额外运行时开销的开发者。

## 使用场景

- 你需要在 UE5 游戏或应用中**实时运行神经网络模型**（例如风格迁移、图像超分辨率、物体检测）。
- 你的项目已经**深度使用 RDG 进行渲染**，希望神经网络推理能无缝融入现有管线，享受 RDG 的资源管理和调度优化。
- 你希望**避免依赖外部推理运行时**（如 ONNX Runtime），转而使用引擎原生的、跨平台的图形 API (DirectX 12, Vulkan, Metal) 进行计算。
- 你正在研究或开发 **UE5 原生的机器学习管线**，需要一个基于 RDG 的参考实现。

## 蓝图用法

该插件主要面向 C++ 开发者，通过 NNE 的公共 API 进行交互。其核心功能（模型加载、实例创建、形状设置、推理调度）均未暴露为 `BlueprintCallable` 节点。然而，通过 NNE 插件提供的蓝图接口（例如 `UNNEModelData`），蓝图系统可以间接触发模型加载，但实际的 RDG 推理过程必须在 C++ 的渲染线程上下文中完成。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeRDG.h"
```

### 基本用法

以下代码演示了如何获取 RDG 运行时并检查模型兼容性。此示例基于对 `UNNERuntimeRDGHlslImplRDG` 类的分析。

```cpp
// 1. 获取 RDG 运行时实例
//    NNE 运行时通过 GUID 标识。RDG HLSL 运行时的 GUID 定义在 UNNERuntimeRDGHlslImpl::GUID。
//    你需要通过 NNE 的运行时注册表查找它。
using namespace UE::NNE;

// 假设你已经有了一个 UNNEModelData 对象 (ModelDataPtr)
// 以及对应的运行时 GUID (你需要知道 RDG HLSL 运时的 GUID，或通过某种方式查询到它)

// 2. 检查运行时是否可以处理给定的模型数据
TObjectPtr<UNNEModelData> ModelDataPtr = ...; // 从资产或其他途径获得
FGuid RuntimeGuid = UNNERuntimeRDGHlslImpl::GUID; // 需要包含头文件并访问静态成员

// 通常通过 NNE 的顶层 API 或管理器来操作，这里为演示核心接口
TObjectPtr<INNERuntimeRDG> Runtime = ...; // 如何获取取决于你的项目设置
if (Runtime && Runtime->CanCreateModelRDG(ModelDataPtr) == ECanCreateModelRDGStatus::Ok)
{
    // 3. 创建模型
    TSharedPtr<IModelRDG> Model = Runtime->CreateModelRDG(ModelDataPtr);
    if (Model.IsValid())
    {
        // 4. 创建模型实例
        TSharedPtr<IModelInstanceRDG> ModelInstance = Model->CreateModelInstanceRDG();
        if (ModelInstance.IsValid())
        {
            // 模型创建成功，可以进一步设置输入形状和进行推理
        }
    }
}
```
*来源推断：`Private/NNERuntimeRDGHlsl.h` 中的 `UNNERuntimeRDGHlslImplRDG` 类接口。*

### 进阶用法

以下代码片段展示了如何在一个 RDG 渲染通道内设置输入并调度神经网络推理。这通常发生在 `FRDGBuilder` 的回调函数中。

```cpp
// 假设你已经拥有一个有效的 ModelInstance (TSharedPtr<IModelInstanceRDG>)
// 并且已经通过 SetInputTensorShapes 设置了合适的输入形状

// 准备输入和输出的张量绑定
// NNE::FTensorBindingRDG 结构体需要包含指向 FRDGBuffer 的指针
TArray<NNE::FTensorBindingRDG> InputBindings;
TArray<NNE::FTensorBindingRDG> OutputBindings;

// 填充绑定... (需要根据模型的输入输出描述来准备对应的 RDG 缓冲区)

// 在 RDG 渲染通道中调度模型执行
FRDGBuilder& RDGBuilder = ...; // 通常在渲染线程的 RDG 回调中获取

auto* PassParameters = RDGBuilder.AllocParameters<...>(); // 分配通道参数
// ... 设置 PassParameters，可能将模型输出绑定到后续渲染通道的输入 ...

// 将神经网络推理任务添加到 RDG
IModelInstanceRDG::EEnqueueRDGStatus EnqueueStatus = ModelInstance->EnqueueRDG(
    RDGBuilder,
    InputBindings,
    OutputBindings
);

if (EnqueueStatus == IModelInstanceRDG::EEnqueueRDGStatus::Ok)
{
    // 神经网络推理作为 RDG 计算通道被成功添加
    // 后续可以添加依赖此输出的渲染通道
    RDGBuilder.AddPass(
        RDG_EVENT_NAME("MyPostProcessPass"),
        PassParameters,
        ERDGPassFlags::Compute,
        [/*捕获必要的资源*/](FRHICommandListImmediate& RHICmdList) {
            // ... 使用神经网络推理的结果 (在 OutputBindings 对应的缓冲区中) ...
        }
    );
}
```
*来源推断：`Private/NNERuntimeRDGModel.h` 中的 `FModelInstanceRDG::EnqueueRDG` 接口以及 `Private/NNERuntimeRDGModelHlsl.h` 中 `FModelInstance` 的实现。*

## Demo 示例

一个最小的、可编译的示例，展示如何从创建模型到设置实例。实际的 `EnqueueRDG` 调用需要在渲染线程上下文中进行，此处仅示意。

```cpp
// MyNeuralNetworkManager.h
#pragma once
#include "CoreMinimal.h"
#include "NNE.h"
#include "NNERuntimeRDG.h"

class FMyNeuralNetworkManager
{
public:
    void InitWithModelData(TObjectPtr<UNNEModelData> ModelData)
    {
        // 获取 RDG 运行时 (简化示意，实际获取方式可能更复杂)
        UE::NNE::TObjectPtr<UE::NNE::INNERuntimeRDG> Runtime = GetNNERDGRuntime();

        if (!Runtime || Runtime->CanCreateModelRDG(ModelData) != UE::NNE::ECanCreateModelRDGStatus::Ok)
        {
            UE_LOG(LogTemp, Error, TEXT("Cannot create RDG model from provided data."));
            return;
        }

        // 创建模型
        Model = Runtime->CreateModelRDG(ModelData);
        if (!Model.IsValid())
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to create RDG model."));
            return;
        }

        // 创建模型实例
        ModelInstance = Model->CreateModelInstanceRDG();
        if (!ModelInstance.IsValid())
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to create RDG model instance."));
            return;
        }

        // 此时可以查询输入输出描述
        TConstArrayView<UE::NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
        TConstArrayView<UE::NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();
        UE_LOG(LogTemp, Log, TEXT("Model has %d inputs, %d outputs."), InputDescs.Num(), OutputDescs.Num());
    }

private:
    // 获取 RDG 运行时的辅助函数 (需要项目实际实现)
    UE::NNE::TObjectPtr<UE::NNE::INNERuntimeRDG> GetNNERDGRuntime();

    TSharedPtr<UE::NNE::IModelRDG> Model;
    TSharedPtr<UE::NNE::IModelInstanceRDG> ModelInstance;
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MetalRHI` | 为 Apple 平台 (macOS, iOS) 提供底层 Metal 图形 API 支持，用于执行 HLSL 着色器的跨平台编译和执行。 |
| `VulkanRHI` | 为 Windows、Linux 和 Android 平台提供底层 Vulkan 图形 API 支持，用于执行 HLSL 着色器。 |
| `NNERuntimeRDGUtils` | 提供编辑器工具功能，特别是模型验证（如 `TModelValidatorRDG`）和可能的导入/处理辅助工具。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的编译器警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式说明符与64位参数不匹配的问题，确保跨平台兼容性。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构了 GPU 同步逻辑，使用更统一的 `SubmitAndBlockUntilGPUIdle` 接口。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至更现代的 `UE_LOGF`。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃了旧的 GPU 性能分析相关宏。 |

### 维护评价

- **创建时间**：2023年6月，属于较新的实验性插件。
- **近期活跃度**：最近一次更新在2026年5月，主要集中在代码健壮性、编译警告修复和小规模重构，表明仍在维护中，但近期没有重大功能更新。
- **状态**：**实验性 (IsExperimentalVersion=true)**，且默认禁用。这意味着它处于早期开发阶段，API 和功能可能会发生变化。
- **推荐使用**：适合对 UE5 图形管线和机器学习推理有深入理解的研究人员和早期采用者。对于生产项目，应谨慎评估其稳定性和功能完备性。它是探索 UE5 原生 GPU 机器学习推理潜力的优秀起点，但可能尚不适合用于要求高稳定性的商业产品。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档]()（无）