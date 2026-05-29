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
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 Unreal Engine 神经网络引擎 (NNE) 的一个实验性运行时实现。它的核心功能是将神经网络推理计算从传统的 CPU 或独立 GPU 计算路径，转移到引擎的 **渲染依赖图 (Render Dependency Graph， RDG)** 管线中执行。这解决了在实时渲染流程中高效、协调地运行神经网络（如风格化、AI后处理效果）的关键问题，允许神经网络推理作为渲染图的一部分，与现有的渲染通道（如光照、后处理）并行或串行执行，从而优化性能和资源管理。

## 使用场景

- **AI驱动的渲染效果**：你需要在每一帧的渲染管线中实时运行一个轻量级神经网络（例如，用于实时风格迁移、超分辨率、去噪）。
- **与渲染通道紧密集成**：你希望将神经网络推理作为 RDG 的一个通道（Pass），以便引擎可以自动管理 GPU 资源、同步和并行化。
- **评估实验性功能**：你正在探索 Unreal Engine 中基于 GPU 的神经网络推理的最新可能性，并准备处理实验性 API 可能带来的变化。

## 模块概览

本插件由多个模块协作，为 RDG 运行时提供完整支持：

| 模块 | 类型 | 职责 |
|---|---|---|
| `NNEHlslShaders` | Runtime | 包含实现神经网络算子所需的 HLSL 计算着色器。 |
| `NNERuntimeRDG` | Runtime | 核心运行时模块，实现 `INNERuntimeRDG` 接口，管理模型在 RDG 上的加载、编译与执行。 |
| `NNERuntimeRDGData` | Runtime | 定义 RDG 运行时专用的数据格式（如 `FNNERuntimeRDGModelRDG`）和资产类型。 |
| `NNERuntimeRDGUtils` | Editor | 提供编辑器工具，用于处理 ONNX 模型格式的导入、预处理和优化。 |
| `NNERuntimeRDGOnnxEditor` | External | 第三方 ONNX 库的编辑器封装。 |
| `NNERuntimeRDGOnnxruntimeEditor` | External | 第三方 ONNX Runtime 库的编辑器封装。 |
| `NNERuntimeRDGProtobufEditor` | External | 第三方 Protobuf 库的编辑器封装。 |

## 核心蓝图功能

RDG 运行时通过 NNE 的公共 API 暴露其功能。以下是关键蓝图节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateInferenceContextRDG` | 创建一个专门用于 RDG 管线的推理上下文。 | `UNNERuntimeRDGBlueprintLibrary` |
| `CreateModelRDGFromONNX` | 从 ONNX 格式资产创建可用于 RDG 的模型实例。 | `UNNERuntimeRDGBlueprintLibrary` |
| `RunRDGInference` | 在提供的 RDG 管线和输入数据上，同步执行一次模型推理。 | `UNNERuntimeRDGBlueprintLibrary` |

**使用示例（蓝图描述）**
1.  在初始化时，使用 `CreateModelRDGFromONNX` 节点，将一个 `.onnx` 文件资产加载为 RDG 模型。
2.  使用 `CreateInferenceContextRDG` 节点，基于该模型创建推理上下文。
3.  在每帧的渲染事件中，获取当前帧的 RDG 管线引用（`FRDGBuilder`），调用 `RunRDGInference` 节点，传入管线、推理上下文和输入张量，将推理计算添加到渲染图中。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeRDG.h"
#include "NNERuntimeRDGData.h"
```

### 基本用法

通过 NNE 核心 API 获取 RDG 运行时并执行推理。

```cpp
// 来源: NNERuntimeRDG 模块测试用例推断
void RunRDGInferenceExample(UNNEModelData* ModelData, FRDGBuilder& RDGBuilder)
{
    // 1. 获取 RDG 运行时
    const TWeakInterfacePtr<INNERuntime> Runtime = NNE::GetRuntime<INNERuntimeRDG>();
    if (!Runtime.IsValid()) return;

    // 2. 创建模型和上下文
    TWeakInterfacePtr<INNERuntimeRDG::FModelRDG> Model = Runtime->CreateModelRDG(ModelData);
    if (!Model.IsValid()) return;
    TWeakInterfacePtr<INNERuntimeRDG::FModelRDG::FContext> Context = Model->CreateContext();

    // 3. 设置输入输出
    // ... (创建输入输出张量缓冲区)

    // 4. 执行推理 (集成到 RDG)
    {
        FRDGEventName EventName(TEXT("RunRDGInference"));
        RDGBuilder.BeginEventScope(EventName);

        // 将模型执行添加到 RDG
        FNNERuntimeRDGModelRDGUtils::EnqueueRDGDispatch(RDGBuilder, Model, Context);

        RDGBuilder.EndEventScope();
    }
}
```

### 进阶用法

管理模型资产与数据格式转换。

```cpp
// 来源: NNERuntimeRDGData 模块
// 创建一个 RDG 专用的模型数据资产
UNNEModelData* CreateRDGModelData(const FString& ONNXFilePath)
{
    // 假设已通过 NNERuntimeRDGUtils 模块将 ONNX 文件预处理并加载为 UNNEModelData
    // 此处省略了 ONNX 预处理步骤，通常在编辑器工具中完成
    UNNEModelData* ModelData = /* ... */;
    return ModelData;
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在 `UActorComponent` 中使用 RDG 运行时进行推理。

**MyRDGInferenceComponent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNEModelData.h"
#include "NNERuntimeRDGData.h"
#include "MyRDGInferenceComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class YOURPROJECT_API UMyRDGInferenceComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
    UNNEModelData* ModelData;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
    FNNERuntimeRDGModelRDGHandle ModelHandle;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
    FNNERuntimeRDGModelRDGContextHandle ContextHandle;

    virtual void BeginPlay() override;
    void ExecuteRDGInference(FRDGBuilder& RDGBuilder);
};
```

**MyRDGInferenceComponent.cpp**
```cpp
#include "MyRDGInferenceComponent.h"
#include "NNE.h"
#include "NNERuntimeRDG.h"
#include "RenderGraphUtils.h"

void UMyRDGInferenceComponent::BeginPlay()
{
    Super::BeginPlay();

    // 获取运行时并加载模型
    if (const TWeakInterfacePtr<INNERuntime> Runtime = NNE::GetRuntime<INNERuntimeRDG>(); Runtime.IsValid())
    {
        ModelHandle = StaticCastSharedPtr<FNNERuntimeRDGModelRDG>(Runtime->CreateModel(ModelData)).ToSharedRef();
        if (ModelHandle.IsValid())
        {
            ContextHandle = ModelHandle->CreateContext();
        }
    }
}

void UMyRDGInferenceComponent::ExecuteRDGInference(FRDGBuilder& RDGBuilder)
{
    if (!ModelHandle.IsValid() || !ContextHandle.IsValid()) return;

    // 假设输入输出已准备好（例如，从渲染目标读取，写入到另一个缓冲区）
    FRDGBufferRef InputBuffer = /* ... 创建或获取输入 RDG Buffer ... */;
    FRDGBufferRef OutputBuffer = /* ... 创建输出 RDG Buffer ... */;

    // 设置上下文输入输出
    // ... (ContextHandle->SetInput/Output)

    // 在 RDG 中调度推理
    FNNERuntimeRDGDispatchParameters DispatchParams;
    DispatchParams.Graph = &RDGBuilder;
    ModelHandle->Dispatch(ContextHandle, DispatchParams);
}
```

## 模块依赖

要使用本插件，你的模块需要链接以下依赖：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心 API 和运行时注册表。 |
| `NNERuntimeRDGUtils` | 提供 ONNX 模型处理工具（编辑器功能）。 |
| `NNERuntimeRDGData` | 提供 RDG 运行时专用的数据类型和结构。 |
| `RenderCore`, `RHI` | 用于访问 `FRDGBuilder` 等 RDG 核心类型和 RHI 资源。 |

**注意**: `MetalRHI` 和 `VulkanRHI` 是 `NNERuntimeRDG` 模块的构建依赖，用于支持跨平台 GPU 着色器编译。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为单精度时的编译警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了格式化字符串中 32/64 位说明符与实参位数不匹配的问题。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 将 GPU 同步 API 合并为更清晰的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将部分日志调用迁移到更现代的 `UE_LOGF` 宏。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析器相关宏。 |

### 维护评价

NNERuntimeRDG 是一个实验性插件，创建于 2023 年，年龄约 2 年。从近期提交历史看，**最近 6 个月内有持续的代码更新和维护**，但主要集中在编译器警告修复、API 清理和工具链迁移等底层改进，尚未见到重大的功能特性添加。

鉴于其 `IsExperimentalVersion=true` 和 `EnabledByDefault=false` 的状态，该插件仍处于**早期评估和开发阶段**。API 和实现可能在未来发生 breaking changes。对于需要在 UE5 项目中集成 GPU 加速神经网络推理的开发者，此插件是探索 RDG 集成路径的官方实现，值得研究和试用，但**不建议在面向生产的稳定项目中依赖它**，除非你准备好跟进实验性 API 的变化并自行承担维护成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEQA) (位于 NNE 核心插件的 QA 模块中)