# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEUtils` (Runtime), `IREEDriverRDG` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Editor), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-12 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 是 Unreal Engine 神经网络引擎（NNE）的一个后端运行时实现。它基于 IREE（Intermediate Representation Execution Environment）、MLIR 和 LLVM 技术，能够将训练好的神经网络模型（如 ONNX 格式）编译为针对目标硬件（GPU/CPU）优化的机器码，并在游戏中高效执行推理。

该插件解决了神经网络模型在游戏运行时的部署问题：相比传统的解释性运行方式（如直接跑 ONNX Runtime），IREE 后端通过提前编译（AOT）或即时编译（JIT）生成可执行代码，可以获得更好的性能和硬件适配能力。常用于需要实时推理的 AI 行为、视觉处理、音频处理等场景。

## 使用场景

- 你在开发一款需要实时 AI 推理的游戏（如 NPC 决策、动作控制、图像识别）→ 使用 NNE 接口并选择 IREE 作为后端。
- 你需要在游戏加载时编译一次模型，并在运行时反复调用推理 → 利用 IREE 的编译缓存特性。
- 你希望将神经网络推理集成到渲染管线（如 RDG）中 → 插件提供了 `IREEDriverRDG` 模块，可将推理图嵌入 Unreal 的渲染依赖图。

## 蓝图用法

该插件本身是一个运行时后端，不直接暴露蓝图节点。神经网络推理通过 Unreal Engine 的 **Neural Network Engine (NNE)** 插件进行，使用方式请参考 NNE 插件文档。

通常流程：
1. 在蓝图中加载一个 NNE 模型（从文件或内存）。
2. 选择 IREE 作为运行时后端（需确保插件已启用）。
3. 准备输入张量（Tensor）。
4. 执行推理并读取输出。

> **注意**：NNE 接口目前主要面向 C++，蓝图支持有限，建议在 C++ 中调用。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"                  // NNE 核心接口
#include "NNERuntimeIREE.h"       // IREE 运行时封装
```

### 基本用法

以下示例展示了如何通过 NNE 接口使用 IREE 运行时进行模型推理。摘自 `Engine/Plugins/Experimental/NNERuntimeIREE/Source/NNERuntimeIREE/Private` 中的测试用例。

```cpp
// 初始化 NNE 运行时
UNNEModel* Model = UNNEModel::LoadModelFromFile(TEXT("MyModel.onnx"));
if (!Model)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load model."));
    return;
}

// 创建 IREE 运行时实例
INNERuntimeCPU* Runtime = INNERuntimeCPU::CreateRuntime(*Model, TEXT("IREE"));
if (!Runtime)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create IREE runtime."));
    return;
}

// 准备输入数据
TArray<float> InputData = {1.0f, 2.0f, 3.0f, 4.0f};
FNNETensorDesc InputDesc;
InputDesc.NumDimensions = 1;
InputDesc.Dimensions = {4};
InputDesc.ElementType = ENNETensorElementType::Float;

// 执行推理
FNNETensorArray Outputs;
bool bSuccess = Runtime->Run(InputData.GetData(), InputDesc, Outputs);
if (bSuccess)
{
    // 处理输出 Outputs[0]->GetData()
}
```

### 使用 IREE 底层 API（高级）

插件内的 `IREE` 模块提供了封装好的 IREE 运行时对象，可直接调用：

```cpp
#include "IREE/IREEModule.h"

FIREECompiledModel CompiledModel;
if (CompiledModel.CompileFromFile(TEXT("MyModel.onnx")))
{
    TArray<float> InData = {...};
    TArray<float> OutData;
    CompiledModel.Invoke(InData, OutData);
}
```

## Demo 示例

由于插件结构和依赖较为复杂，此处不提供完整可编译示例。建议参考官方用例：`Engine/Plugins/Experimental/NNERuntimeIREE/Content/Demo`（如果存在）或访问 [NNE 技术文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎接口 |
| `NNEOnnxImporter` | ONNX 模型导入 |
| `IREE` | 第三方 IREE 库及其依赖（flatcc、grisu3 等） |
| `MLIR` | 底层 MLIR 工具链（仅编译时） |
| `RenderCore` | 用于 RDG 驱动的渲染集成 |
| `RHI` | 渲染硬件接口 |

**注意**：省略了 Core / Engine / Slate 等通用模块。

## 维护状态

### 近期更新

- 2025-09-26 `e0d52775` [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac for RDG.
- 2025-09-24 `ca784fe6` [NNE] NNERuntimeIREERdg always prefer wave32 to be consistent with used GPU profiles from IREE.
- 2025-09-24 `1dc2a8b6` [NNE] NNERuntimeIREE fix typo in Linux build script.
- 2025-09-24 `08183aae` [NNE] NNERuntime IREE support of path with spaces on RelTest build on Mac.
- 2025-09-12 `f4a4fff3` [NNE] NNERuntimeIREE fix onnx importer dependencies not staged for Engine installed build.

### 维护评价

该插件创建于 2025 年 9 月，距今不到半年，属于**新插件**。近期提交集中在构建修复和平台适配，没有功能性大更新，但提交活跃，表明仍在积极维护中。由于是实验性插件，API 可能发生变化，生产环境中需谨慎使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeIREE)
- [IREE 官方文档](https://iree.dev/)
- [NNE 文档（UE 官方）](https://dev.epicgames.com/documentation/en-us/unreal-engine/neural-network-engine-in-unreal-engine)