# Neural Rendering

> Enable neural rendering features including: neural post processing

| 属性 | 值 |
|---|---|
| 中文名 | 神经渲染 |
| 分类 | Experimental |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NeuralPostProcessing` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-10-05 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering) | |

## 用途

Neural Rendering 插件的核心功能是在 Unreal Engine 的后处理流程中集成神经网络推理。它并非简单地提供一个现成的后处理效果，而是构建了一个底层管线，允许开发者将自定义的神经网络模型应用于渲染后的图像。

该插件解决的问题是：如何在实时渲染管线（尤其是后处理阶段）高效地执行神经网络计算。它通过 UE 的 NNE (Neural Network Engine) 框架，并利用 RDG (Render Dependency Graph) 进行调度，实现了一个将后处理材质数据作为神经网络输入，并将网络输出写回渲染目标的流程。它支持两种数据索引方式：**纹理索引** (Texture index) 和**缓冲区索引** (Buffer index)，并提供了对大规模输入进行分块（Tiling）处理以模拟更大批次尺寸的功能，以及对重叠区域进行融合处理的策略。

**为什么存在？** 它是为了在 UE5 中探索和实现基于神经网络的实时图像处理技术（如风格迁移、超分辨率、去噪、光照估计等）而提供的一个实验性基础框架。

## 使用场景

-   你需要一个可以自定义的、基于神经网络的后处理效果，而不是使用引擎内置的传统滤镜。
-   你的美术管线或技术研究需要用到自定义训练的神经网络模型来处理游戏画面。
-   你正在开发一个依赖于实时神经渲染的技术原型（如 AI 超分、AI 抗锯齿、AI 特效等）。

## 蓝图用法

该插件主要为 C++ 模块，其核心功能通过**后处理材质 (Post Process Material)** 和**神经网络配置文件 (Neural Profile)** 进行配置和触发，而非直接暴露蓝图节点。用户需要在材质编辑器中创建一个后处理材质，并启用 `Used with Neural Network` 选项，然后通过 `Neural Input` 和 `Neural Output` 节点来定义与神经网络交互的数据。

### 核心材质节点

| 节点 | 说明 | 所在类/上下文 |
|---|---|---|
| `Neural Input` | 定义神经网络的一个输入通道。在材质中使用 `[B, C, U, V]` 索引，`input0` 通常需要 3 个有效通道 (RGB)。通过 `Mask` 引脚控制是否使用该输入。 | 后处理材质 |
| `Neural Output` | 定义神经网络的一个输出通道。允许从网络输出中读取数据并写回渲染目标。 | 后处理材质 |

### 使用示例（材质设置）

1.  创建一个新的**后处理材质**。
2.  在材质细节面板中，勾选 `Used with Neural Network`。
3.  在材质图表中，添加一个 `Neural Input` 节点。这代表了你的神经网络的一个输入源（例如当前场景颜色）。
4.  根据需要配置 `Neural Input` 的参数（如通道索引、是否作为网络输入等）。
5.  添加一个或多个 `Neural Output` 节点，用于从你的网络输出中读取结果。
6.  在项目的后处理体积或摄像机中应用此材质。
7.  在 C++ 或配置文件中，将一个 **Neural Profile**（指定要使用的 NNE 模型数据和运行时）与该后处理材质关联起来。

## C++ 用法

主要的编程接口围绕 `UNeuralPostProcessModelInstance` 类，该类管理着一个神经网络模型实例在 RDG 中的执行。

### 头文件引入

```cpp
#include "NeuralPostProcessing/Public/NeuralPostProcessModelInstance.h"
```

### 基本用法

从 `UNeuralPostProcessModelInstance` 的接口可以推断其基本使用流程。
```cpp
// 假设你已经通过某种方式（例如从配置文件或资产）获取了模型数据和运行时名称
UNNEModelData* MyModelData = /* ... */;
FString RuntimeName = TEXT("NNERuntimeORT");

// 1. 创建模型实例 (通常在游戏线程或某个初始化阶段)
UNeuralPostProcessModelInstance* ModelInstance = NewObject<UNeuralPostProcessModelInstance>();

// 2. 更新模型实例，指定要使用的NNE模型数据和运行时
ModelInstance->Update(MyModelData, RuntimeName);

// 3. 配置分块和重叠参数 (如果需要)
ModelInstance->UpdateTileDimension(FIntPoint(256, 256)); // 设置分块大小
ModelInstance->UpdateTileOverlap(FIntPoint(16, 16)); // 设置重叠区域大小
ModelInstance->UpdateModelTileType(ENeuralModelTileType::Texture); // 设置索引类型
ModelInstance->UpdateTileOverlapResolveType(ETileOverlapResolveType::Feathering); // 设置重叠融合策略
ModelInstance->UpdateDispatchSize(1); // 设置批次大小或调度尺寸

// 4. 在渲染线程的 RDG Pass 中执行 (通常在某个后处理 Pass 中)
FRDGBuilder& GraphBuilder = /* ... */;
// 确保 RDG 缓冲区已创建
ModelInstance->CreateRDGBuffersIfNeeded(GraphBuilder);
// 执行神经网络推理
ModelInstance->Execute(GraphBuilder);

// 5. 获取输入/输出缓冲区，用于在其他 RDG Pass 中读写数据
FRDGBufferRef InputBuffer = ModelInstance->GetInputBuffer();
FRDGBufferRef OutputBuffer = ModelInstance->GetOutputBuffer();
```
*代码逻辑基于 `UNeuralPostProcessModelInstance.h` 中的公共接口推断。*

### 进阶用法

更复杂的用法涉及直接操作 RDG 缓冲区和分块数据。
```cpp
// 获取分块处理后的输入/输出缓冲区
FRDGBufferRef TiledInputBuffer = ModelInstance->GetTiledInputBuffer();
FRDGBufferRef TiledOutputBuffer = ModelInstance->GetTiledOutputBuffer();

// 查询当前模型的输入输出张量形状
UE::NNE::FTensorShape InputShape = ModelInstance->GetResolvedInputTensorShape();
UE::NNE::FTensorShape OutputShape = ModelInstance->GetResolvedOutputTensorShape();

// 修改输入张量的某个维度大小 (可能需要在执行前调用)
bool bSuccess = ModelInstance->ModifyInputShape(0 /* Dimension */, 512 /* NewSize */);
```
*代码逻辑基于 `UNeuralPostProcessModelInstance.h` 中的公共接口推断。*

## Demo 示例

一个最小的、概念性的代码示例，展示如何在后处理 Pass 中初始化和使用神经网络模型实例。
```cpp
// NeuralPostProcessDemo.h
#pragma once

#include "CoreMinimal.h"
#include "NeuralPostProcessModelInstance.h"

class FNeuralPostProcessDemo
{
public:
    void Initialize(UNNEModelData* ModelData, const FString& RuntimeName);
    void Render(FRDGBuilder& GraphBuilder, FRDGTextureRef SceneColorTexture);
    
private:
    UPROPERTY()
    UNeuralPostProcessModelInstance* NeuralModelInstance = nullptr;
};

// NeuralPostProcessDemo.cpp
#include "NeuralPostProcessDemo.h"
#include "RenderGraphBuilder.h"
#include "NeuralPostProcessing/Private/NeuralPostProcessCS.h" // 用于访问内部着色器，实际使用可能不需要

void FNeuralPostProcessDemo::Initialize(UNNEModelData* ModelData, const FString& RuntimeName)
{
    NeuralModelInstance = NewObject<UNeuralPostProcessModelInstance>();
    // 设置一个简单的配置，假设是纹理索引、无分块
    NeuralModelInstance->Update(ModelData, RuntimeName);
    NeuralModelInstance->UpdateModelTileType(ENeuralModelTileType::Texture);
    NeuralModelInstance->UpdateTileDimension(FIntPoint(1, 1));
    NeuralModelInstance->UpdateDispatchSize(1);
}

void FNeuralPostProcessDemo::Render(FRDGBuilder& GraphBuilder, FRDGTextureRef SceneColorTexture)
{
    if (!NeuralModelInstance || !NeuralModelInstance->IsValid())
    {
        return;
    }

    // 确保模型内部的 RDG 缓冲区存在
    NeuralModelInstance->CreateRDGBuffersIfNeeded(GraphBuilder);

    // 这里省略了将 SceneColorTexture 复制到 NeuralModelInstance 输入缓冲区的 RDG Pass。
    // 实际实现需要使用 NeuralPostProcessCS.h 中定义的着色器 (如 FDownScaleTexture, FCopyBetweenTextureAndOverlappedTileBufferCS) 来完成数据准备。

    // 执行神经网络
    NeuralModelInstance->Execute(GraphBuilder);

    // 这里省略了将 NeuralModelInstance 输出缓冲区结果写回或混合到最终输出的 RDG Pass。
}
```

## 模块依赖

从 `.uplugin` 的 `Plugins` 字段和模块功能推断。

| 模块 | 用途 |
|---|---|
| `NNE` | Unreal Engine 的核心神经网络引擎框架，提供模型加载、实例化和基础接口。 |
| `NNERuntimeORT` | 基于 ONNX Runtime 的 NNE 运行时实现，用于实际执行 ONNX 格式的神经网络模型。此插件是功能运行的必要依赖。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换旧的 GPU 同步 API 为新接口 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统更新，迁移至新的 `UE_LOGF` 宏。 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧的 GPU 性能分析相关宏。 |
| 2025-10-27 | `581ba7ee` | [Neural post processing] Fix typo | 修复神经网络后处理代码中的拼写错误。 |
| 2025-10-24 | `260f58f8` | [Neural post processing] Fix cooking fail in editor. | 修复在编辑器环境下烹饪（打包）失败的问题。 |

### 维护评价

这是一个创建于 2023 年的**实验性**插件，标记为 `IsExperimentalVersion: true` 且默认未启用。从提交历史看，**维护活动非常低**。最近的提交主要是适配引擎底层 API 的改动（如日志、GPU 同步、性能分析）和微小的 bug 修复，没有发现功能性的增强或新特性。代码库规模很小（6个文件），接口相对简单。

**综合评价：**
- **活跃度**: 不活跃。自创建以来，没有实质性的功能迭代。
- **稳定性**: 作为实验性项目，主要用于内部研究和探索，稳定性未经大规模验证。
- **推荐使用**: **仅限实验和研究目的**。不推荐在生产项目中使用。由于其强烈的实验性质和对 `NNERuntimeORT` 插件的依赖，以及可能存在的 API 变动风险，开发者应将其视为一个技术参考或原型框架，而非成熟的产品级解决方案。如果未来有神经网络渲染的需求，建议关注引擎后续可能推出的更稳定、功能更完整的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering)
- [官方文档](https://epicgames.com)（无专门文档，链接指向创建者主页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NeuralRendering)（未在信息中提及单独的测试文件，可能包含在插件目录内或 Engine/Tests 下）