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

`NNERuntimeRDG` 插件为虚幻引擎的 NNE (Neural Network Engine) 提供了一个基于 HLSL 着色器的运行时实现。它并非一个独立的推理框架，而是 UE5 GPU 渲染管线的一部分。其核心目标是将常见的神经网络算子（如卷积、矩阵乘法、池化等）实现为 RDG (Render Dependency Graph) 友好的 HLSL 计算着色器，从而能够将神经网络模型的推理过程无缝集成到渲染管线中执行。

**它解决了什么问题？**
传统的神经网络运行时（如 ONNX Runtime）通常独立于游戏引擎的渲染管线运行，数据传输（CPU ↔ GPU）可能成为性能瓶颈。`NNERuntimeRDG` 通过将推理过程完全置于 GPU 的 RDG 系统内，实现了与渲染逻辑的紧耦合和零拷贝数据共享，特别适用于那些推理结果需要直接用于图形渲染的场景（如风格迁移、AI 生成纹理、实时后处理效果等）。

## 使用场景

- 你在开发一个需要实时 AI 风格迁移的游戏，希望将图像风格转换与游戏渲染管线结合，避免额外的 GPU 数据复制开销。
- 你需要将一个简单的神经网络模型（例如用于图像处理或决策的小型网络）的推理结果直接作为后续渲染 Pass 的输入。
- 你希望利用 UE5 的 RDG 系统来优化神经网络推理的调度和内存管理，并与场景中的其他渲染任务自动同步。
- 你的目标平台是 PC 或主机，并且项目启用了 RDG，需要原生的 HLSL 着色器加速。

## 蓝图用法

本插件主要面向 C++ 开发，未发现公开的蓝图可调用函数或属性。所有操作均通过 NNE 的公共 C++ API 进行。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeRDG.h"
```

### 基本用法

`NNERuntimeRDG` 的使用完全遵循 NNE 的标准工作流：加载模型数据、创建运行时实例、创建推理实例、设置输入输出、执行推理。

```cpp
// 基本用法示例 (简化版)
// 假设你已经通过 UFactory 或其他方式加载了 UNNEModelData
void RunBasicInference(UNNEModelData* ModelData)
{
    // 1. 获取 RDG 运行时（需要在支持 RDG 的环境下，如游戏线程渲染时）
    const FName RuntimeName = TEXT("NNERuntimeRDG");
    TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime(RuntimeName);
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Could not get NNERuntimeRDG runtime."));
        return;
    }

    // 2. 创建模型实例
    TSharedPtr<UE::NNE::IModelRDG> Model = Runtime->CreateModelRDG(ModelData);
    if (!Model.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Could not create model from model data."));
        return;
    }

    // 3. 创建推理实例
    TSharedPtr<UE::NNE::IModelInstanceRDG> ModelInstance = Model->CreateModelInstance();
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Could not create model instance."));
        return;
    }

    // 4. 准备输入输出张量 Shape (具体值需要根据你的模型确定)
    const UE::NNE::FTensorShape InputTensorShape = {1, 3, 224, 224}; // 例如 ImageNet 输入
    const UE::NNE::FTensorShape OutputTensorShape = {1, 1000}; // 例如 ImageNet 分类输出

    // 5. 在 RDG 中分配资源并设置输入/输出
    // 注意：实际执行必须在 FRDGBuilder 的上下文中 (例如在 FSceneRenderer 的某个 Pass 中)
    // 此处为伪代码演示流程
    /*
    FRDGBuilder& GraphBuilder = ...;
    FRDGBufferRef InputBuffer = GraphBuilder.CreateBuffer(..., TEXT("NNInput"));
    FRDGBufferRef OutputBuffer = GraphBuilder.CreateBuffer(..., TEXT("NNOutput"));

    // 将你的图像数据 Upload 到 InputBuffer (或直接引用已有的渲染资源)

    // 设置推理输入输出
    UE::NNE::FTensorBindingRDG InputBinding = {InputBuffer};
    UE::NNE::FTensorBindingRDG OutputBinding = {OutputBuffer};
    TConstArrayView<UE::NNE::FTensorBindingRDG> InputBindings = {InputBinding};
    TConstArrayView<UE::NNE::FTensorBindingRDG> OutputBindings = {OutputBinding};

    // 6. 将推理任务添加到 RDG 图中
    ModelInstance->EnqueueRDG(GraphBuilder, InputBindings, OutputBindings);

    // 7. OutputBuffer 现在可以被后续的渲染 Pass (如 Pixel Shader) 使用
    */
}
```

*来源：基于 NNE 公共 API (`Engine/Plugins/Experimental/NNE/Source/`) 和 NNERuntimeRDG 模块头文件推断。*

### 进阶用法

进阶用法包括处理多个输入输出、动态 Shape 以及与特定 RDG Pass 的集成。`NNERuntimeRDGUtils` 模块（仅编辑器/开发工具）可能包含用于模型转换或优化的辅助函数。

```cpp
// 进阶：在渲染回调中集成推理
void FMyRenderer::Render(FRHICommandListImmediate& RHICmdList, FSceneRenderTargets& SceneContext)
{
    FRDGBuilder GraphBuilder(RHICmdList);

    // ... 其他渲染代码 ...

    // 将神经网络推理插入到 RDG 图中特定的位置
    if (bShouldRunInference && ModelInstance.IsValid())
    {
        // 1. 准备 RDG 输入缓冲区（可能引用渲染中的中间结果，如 GBuffer、屏幕颜色）
        FRDGBufferRef InferenceInputBuffer = GraphBuilder.RegisterExternalBuffer(SceneContext.SomeTexture->GetRHI());
        // ... 创建输入缓冲区 SRV ...

        // 2. 准备 RDG 输出缓冲区
        FRDGBufferDesc OutputDesc = FRDGBufferDesc::CreateBufferDesc(sizeof(float), OutputTensorShape.Volume());
        FRDGBufferRef InferenceOutputBuffer = GraphBuilder.CreateBuffer(OutputDesc, TEXT("InferenceResult"));

        // 3. 设置绑定并执行
        UE::NNE::FTensorBindingRDG InputBinding = {GraphBuilder.CreateSRV(...)};
        UE::NNE::FTensorBindingRDG OutputBinding = {InferenceOutputBuffer};
        ModelInstance->EnqueueRDG(GraphBuilder, {InputBinding}, {OutputBinding});

        // 4. 添加一个后续的 RDG Pass 来使用 InferenceOutputBuffer
        // 例如，添加一个自定义的全屏后处理效果，其 Shader 参数中包含这个缓冲区
        AddMyCustomPassThatUsesInference(GraphBuilder, InferenceOutputBuffer);
    }

    // ... 其他渲染代码 ...
    GraphBuilder.Execute();
}
```

*来源：综合 RDG 和 NNE 集成设计模式。*

## Demo 示例

以下是一个最小化的、概念性的 C++ 示例，展示如何在自定义的渲染组件中集成 `NNERuntimeRDG`。

```cpp
// MyNNRenderingComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeRDG.h"
#include "MyNNRenderingComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyNNRenderingComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UPROPERTY(EditAnywhere, Category="Neural Network")
    UNNEModelData* ModelData;

    virtual void BeginPlay() override;

private:
    TWeakInterfacePtr<INNERuntime> Runtime;
    TSharedPtr<UE::NNE::IModelRDG> Model;
    TSharedPtr<UE::NNE::IModelInstanceRDG> ModelInstance;

    void InitializeModel();
};
```

```cpp
// MyNNRenderingComponent.cpp
#include "MyNNRenderingComponent.h"
#include "Engine/World.h"
#include "Renderer/Private/SceneRendering.h" // 仅为示意，实际应包含正确的渲染头文件

void UMyNNRenderingComponent::BeginPlay()
{
    Super::BeginPlay();
    InitializeModel();
}

void UMyNNRenderingComponent::InitializeModel()
{
    if (!ModelData)
    {
        UE_LOG(LogTemp, Warning, TEXT("ModelData is null."));
        return;
    }

    // 获取 RDG 运行时
    const FName RuntimeName = TEXT("NNERuntimeRDG");
    Runtime = UE::NNE::GetRuntime(RuntimeName);
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get NNERuntimeRDG runtime."));
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
    ModelInstance = Model->CreateModelInstance();
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create RDG model instance."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("NNERuntimeRDG model initialized successfully."));

    // 注意：实际执行推理需要在渲染线程的 RDG 环境中调用 ModelInstance->EnqueueRDG。
    // 你需要将调用绑定到场景的渲染事件上，例如通过订阅 FSceneRenderer 的回调或创建自定义的渲染 Pass。
    // 这超出了此简单示例的范围。
}
```

## 模块依赖

要使用 `NNERuntimeRDG`，你的模块需要链接 NNE 核心模块。`NNERuntimeRDG` 本身依赖于图形 RHI 模块以支持跨平台 HLSL 着色器。

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心公共 API 和接口，**必须依赖** |
| `RHI` | 虚幻引擎渲染硬件接口基础，**必须依赖** |
| `RenderCore` | RDG 和渲染核心功能，**必须依赖** |
| `MetalRHI` | Apple Metal 渲染 API 实现（Mac/iOS 平台支持） |
| `VulkanRHI` | Vulkan 渲染 API 实现（多平台支持） |
| `NNERuntimeRDGUtils` | 编辑器/开发工具，用于模型转换、优化等 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化说明符，使其与 64 位参数匹配。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除旧的 GPU 同步函数，替换为新的统一函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 日志宏迁移到新的 UE_LOGF 宏。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析相关宏。 |

### 维护评价

该插件仍处于 **实验性** 阶段 (`IsExperimentalVersion=true`, `EnabledByDefault=false`)。从提交历史看，近期（2026年初至今）有多次提交，内容主要涉及编译器警告修复、代码清理和 API 迁移，表明该模块仍在**活跃维护**中，以确保其与最新的引擎代码保持兼容。

**建议**：由于其实验性状态，**不建议在追求稳定性的生产项目中直接使用**。它更适合用于**技术预研、内部工具开发或对 AI 渲染集成有强烈需求且愿意跟踪引擎更新的高级用户**。使用时需注意 API 可能发生 breaking change，并关注后续引擎版本的更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- [官方文档](https://docs.unrealengine.com) (暂无特定文档，请关注 NNE 相关部分)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG/Tests) (如果存在)