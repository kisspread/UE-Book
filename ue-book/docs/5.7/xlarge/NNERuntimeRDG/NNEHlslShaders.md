# NNEHlslShaders

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | NNE HLSL 着色器 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

`NNEHlslShaders` 是 `NNERuntimeRDG` 插件的底层着色器库，提供了在 GPU 上执行神经网络运算所需的全部 Compute Shader 内核。它实现了 NEural Network Engine（NNE）API 的 GPU 加速部分，通过 Unreal Engine 的 Render Dependency Graph（RDG）来高效调度计算任务。

该模块封装了各类神经网络操作（如卷积、池化、归一化、激活函数、张量变换等）对应的 HLSL 计算着色器，并将这些着色器以全局着色器（`FGlobalShader`）的形式暴露给上层 `NNERuntimeRDG` 模块。它不直接暴露运行时接口，而是作为纯 GPU 计算能力的提供者存在。

**为什么存在？**  
神经网络推理在 CPU 上可能较慢，尤其对于视觉模型（如 CNN）。该模块通过利用 GPU 的大规模并行性，将模型推理速度提升数倍至数十倍，使得实时 AI 功能在游戏中成为可能。

## 使用场景

- 在游戏或应用中集成神经网络推理，要求低延迟和高吞吐量。
- 使用基于 ONNX 的模型，并通过 `NNERuntimeRDG` 运行时在 GPU 上执行。
- 开发者希望直接编写或复用 GPU 内核来加速自定义神经网络操作。
- 需要了解底层 RDG 调度方式以优化特定模型性能。

## 蓝图用法

此模块不直接提供蓝图可调用的函数或资产。所有着色器内核通过 C++ 在 `NNERuntimeRDG` 模块内部调度，再由引擎自动渲染。蓝图使用者应通过 `NNERuntimeRDG` 暴露的 API（如加载模型、执行推理）来间接受益。

因此，没有可供蓝图的节点或属性。

## C++ 用法

### 头文件引入

```cpp
#include "NNEHlslShadersBase.h"               // 基类
#include "NNEHlslShadersReduceCS.h"            // 以 Reduce 为例
#include "NNEHlslShadersConvCS.h"              // 以卷积为例
```

### 基本用法

#### 1. 使用助手函数填充 shader 参数

```cpp
// 文件：Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNEHlslShaders/Internal/NNEHlslShadersReduceCS.h
// 对张量沿指定轴求平均值（Average），并提交 GPU 计算
void RunReduceAverage(FRDGBuilder& GraphBuilder, FRDGBufferRef InputBuffer, FRDGBufferRef OutputBuffer, TConstArrayView<uint32> Shape, int32 Axis)
{
    using namespace UE::NNEHlslShaders::Internal;

    // 1. 填写 shader 参数
    TReduceCS::FParameters Params;
    TReduceCS::FillInParameters(Shape, Axis, &Params);   // 填充 NumElemBeforeAxis, AxisSize 等

    // 2. 调度 reduce 计算（模板函数根据算子类型自动选择 permutation）
    TReduceCS::EnqueueRDG(GraphBuilder, &Params, InputBuffer, OutputBuffer, EReduceOperatorType::Average);
}
```

#### 2. 获取卷积输出形状

```cpp
// 文件：Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNEHlslShaders/Internal/NNEHlslShadersConvCS.h
// 预先计算卷积的输出尺寸
TArray<int32> OutputShape = FConvCS::GetOutputShape(
    XShape, WShape,
    EConvAutoPad::NOTSET,
    Dilations, Strides, Pads
);
```

### 进阶用法

组合多个操作构成一个简单的神经网络层：

```cpp
// 伪代码：实现一个 Conv + BatchNormalization + Relu 层在 GPU 上
void RunConvBNRelu(FRDGBuilder& GraphBuilder, FRDGBufferRef Input, ...)
{
    // 1. Conv
    FRDGBufferRef ConvOutput = GraphBuilder.CreateBuffer(...);
    FConvCS::FParameters ConvParams;
    FConvCS::FillInParameters(..., ConvParams);
    // 创建 shader 并 Dispatch
    // ...

    // 2. BatchNormalization
    FRDGBufferRef BNOutput = GraphBuilder.CreateBuffer(...);
    TBatchNormalizationCS::FParameters BNParams;
    // ... 填充参数
    // 创建 shader 并 Dispatch

    // 3. Relu（使用 ElementWiseUnary）
    FRDGBufferRef ReluOutput = GraphBuilder.CreateBuffer(...);
    TElementWiseUnaryCS::FParameters ReluParams;
    // ... 填充
    // Dispatch

    // 最终结果在 ReluOutput 中
}
```

## Demo 示例

以下演示如何在 `NNERuntimeRDG` 运行时内部间接使用 `NNEHlslShaders` 执行一次矩阵乘法（Gemm）。该代码片段来自 `NNERuntimeRDG` 模块的内部实现，展现了如何利用着色器函数填充参数并调度。

```cpp
// 文件：NNERuntimeRDG/Source/NNERuntimeRDG/Private/Operators/NNERuntimeRDGOpGemm.cpp（伪代码近似）
#include "NNEHlslShadersGemmCS.h"

using namespace UE::NNEHlslShaders::Internal;

void DispatchGemm(FRDGBuilder& GraphBuilder, FRDGBufferRef A, FRDGBufferRef B, FRDGBufferRef C, FRDGBufferRef Y,
                  float Alpha, float Beta, bool TransA, bool TransB, const FTensorShape& ShapeA, const FTensorShape& ShapeB)
{
    TGemmCS::FParameters Params;
    TGemmCS::FillInParameters(Alpha, Beta, TransA ? 1 : 0, TransB ? 1 : 0, ShapeA, ShapeB, &C ? &ShapeC : nullptr, 0.0f, Params);

    auto GetGroupCount = [&]() { return TGemmCS::GetGroupCount(Params, TGemmCS::GetAlgorithm(Params), ...); };

    // 实际 Dispatch 由 NNERuntimeRDG 内部完成，此处省略 RDG 调用。
    // 但读者可通过查看 TGemmCS.cpp 中的实现了解完整流程。
}
```

> 注：实际使用时，开发者很少直接操作这些 shader 类，而是通过 `NNERuntimeRDG` 的高级 API。本示例仅展示底层机制。

## 模块依赖

**本模块（NNEHlslShaders）的公共依赖：**

| 模块 | 用途 |
|---|---|
| `NNE` | 提供神经网络类型定义（`ENNETensorDataType`, `FTensorShape` 等） |

其余依赖（如 `Core`, `CoreUObject`, `Engine`, `RenderCore`, `RHI` 等）均为标准引擎模块，未列出。

## 维护状态

### 近期更新

| 日期 | Hash | Commit |
|---|---|---|
| 2025-07-24 | `2412ec9f` | Made TArrayView and Invoke constexpr. Fixed UB GetData and deprecated Alignment in TStaticArray |
| 2025-06-12 | `9ce28ae0` | Update numeric limits to use std lib instead of macro because it fails to compile on newer Windows |
| 2025-06-12 | `d9dba260` | [NNE] NNERuntimeRDGHlsl arm64 support |
| 2025-06-03 | `d31855b9` | Fixup build script for libprotobuf-lite & add windows arm64 version |
| 2025-05-29 | `8cfef610` | Added Greater.h include to files which use TGreater, which will break with an upcoming change to rem |

### 维护评价

- **创建时间**：2025-05-29（约 2 个月前）
- **近期更新**：包含 arm64 支持、编译修复、标准库适配等实质性改进。
- **活跃度**：较为活跃，近期有功能性更新且修复了跨平台问题。
- **风险**：插件标记为**实验性**，API 和着色器接口可能随版本迭代发生变化。版本号为 0.1，处于早期开发阶段。
- **推荐使用**：对于需要 GPU 推理的项目非常值得尝试，但应预留测试和适配时间。

## 相关链接

- [源码仓库](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)（该插件为 NNE 在 GPU 上的实现）