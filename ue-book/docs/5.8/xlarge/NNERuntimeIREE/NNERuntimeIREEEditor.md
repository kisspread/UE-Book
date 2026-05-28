# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

此插件是 UE5 神经网络引擎 (NNE) API 的一个具体**运行时**实现。它的核心价值在于使用 **IREE**（基于 MLIR 和 LLVM 的编译器基础设施）作为后端，将训练好的神经网络模型直接编译、优化为目标平台的原生机器码（“游戏代码”）。

它主要解决在游戏或应用中**实时运行小型神经网络**的需求，提供了一个平台无关且性能优越的 CPU 推理方案。根据首次提交信息，它旨在替代之前可能使用的 ONNX Runtime CPU (ORT Cpu) 后端，以在小型网络上获得更好的性能，并拥有更广泛的平台支持。其应用场景包括实时 AI 决策、视觉处理、音频分析等需要神经网络推理的游戏内功能。

## 使用场景

-   你需要在游戏逻辑中实时运行一个小型神经网络（例如，用于敌人行为决策或简单的图像分类），并且对推理性能有较高要求。
-   你需要一个跨平台（CPU）的神经网络推理后端，希望利用 MLIR/LLVM 的优化能力获得比传统 ONNX Runtime 更优的性能。
-   你正在开发一个基于 UE5 NNE API 的应用，并希望使用一个实验性但高性能的 IREE 后端。

## 蓝图用法

此插件主要提供底层的 C++ 运行时和编译管线。直接面向蓝图的功能主要集中在**编辑器工具**部分，用于模型资产的导入。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UNNERuntimeIREEModelDataFactory` (导入器) | 负责将外部训练好的神经网络模型文件（例如 `.mlir`， `.vmfb` 等 IREE 兼容格式）导入为引擎内的资产。 | `UNNERuntimeIREEModelDataFactory` |

**说明**: 该工厂类（`UFactory` 子类）被引擎的资产导入系统自动调用。当用户尝试拖拽支持的模型文件到内容浏览器时，会触发此工厂进行创建和转换。具体的导入逻辑在 `FactoryCreateBinary` 中实现。在蓝图层面，用户通常不直接调用此工厂，而是通过标准的资产导入流程使用它。

## C++ 用法

主要使用方式是利用 UE5 的 `NNE` API，并通过此运行时后端来执行推理。开发者通常不直接与此插件的类交互，而是通过 `NNE` 模块的通用接口。

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeIREE.h"
```

### 基本用法 (伪代码)

以下代码片段展示了如何利用 NNE API 与 NNERuntimeIREE 后端的基本工作流（基于通用 NNE 使用模式推断）：

```cpp
// 假设已经有一个加载到内存中的模型数据（例如从UNNERuntimeIREEModeData资产）
TConstArrayView<uint8> ModelData = /* ... */;

// 1. 查找 IREE 运行时 (Runtime)
//    NNE 会根据当前环境和用户设置返回合适的运行时实例。
TWeakInterfacePtr<INNERuntime> Runtime = NNE::GetRuntime<INNERuntimeIREE>();
if (!Runtime.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to get NNERuntimeIREE runtime."));
    return;
}

// 2. 创建模型实例
TSharedPtr<INNERuntimeIREE::FModelInstance> ModelInstance = Runtime->CreateModelInstance(ModelData).Get();
if (!ModelInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance from IREE runtime."));
    return;
}

// 3. 设置输入张量
//    假设我们知道模型的输入形状和类型 (例如 [1, 3, 224, 224] 的 Float32 图像)
FNNEInferenceContext InferenceContext;
InferenceContext.AddInputTensor(FNNETensorDesc::Create(EInferenceDataType::Float, {1, 3, 224, 224}));

// 4. 执行推理
bool bSuccess = ModelInstance->Run(InferenceContext).Get();
if (!bSuccess)
{
    UE_LOG(LogTemp, Error, TEXT("IREE model inference failed."));
    return;
}

// 5. 获取输出张量并处理结果
TConstArrayView<float> OutputData = InferenceContext.GetOutputTensorDataView<float>(0);
// ... 处理 OutputData ...
```

**来源**: 此示例逻辑基于插件的功能描述和通用 NNE 编程模式编写。具体的 API 细节（如 `FModelInstance` 类型）需要参考 `NNERuntimeIREE` 模块的头文件定义。

### 进阶用法

进阶用法可能涉及：
1.  **异步推理**：使用 `Run` 方法的异步版本以避免阻塞游戏线程。
2.  **输入输出缓冲区管理**：对于高性能场景，直接管理输入输出数据的缓冲区，避免拷贝。
3.  **多模型并行推理**：利用多个模型实例在任务系统上进行并行计算。
4.  **与 RDG (Render Dependency Graph) 集成**：通过 `IREEDriverRDG` 模块，可能支持将神经网络推理作为渲染图中的一个节点，用于图形相关的神经网络处理。

## Demo 示例

由于此插件主要是一个底层运行时，没有独立的蓝图资产或完整的游戏示例。一个“最小可运行示例”需要：
1.  一个支持的神经网络模型文件（例如，一个简单的分类网络，使用 MLIR 方言或编译后的 IREE `.vmfb` 文件）。
2.  使用上文 C++ 用法中的代码框架。
3.  正确的 `Build.cs` 依赖（见下文）。

## 模块依赖

要使用此插件提供的运行时，你的模块需要依赖以下模块（根据 `NNERuntimeIREE` 模块的 `Build.cs` 推断）：

| 模块 | 用途 |
|---|---|
| `NNE` | UE5 核心的神经网络引擎框架，定义了通用的运行时和模型接口。 |
| `NNERuntimeIREE` | 本插件的主模块，提供基于 IREE 的运行时实现。 |
| `IREEDriverRDG` | IREE 的 RDG 驱动，用于与 UE5 渲染管线的深度集成。 |
| `IREEUtils` | IREE 相关的工具函数和类型定义。 |
| `IREE` (ThirdParty) | IREE 框架的核心库（外部依赖）。 |

**注意**: `NNERuntimeIREEEditor` 是编辑器模块，仅用于模型资产导入，运行时代码无需依赖它。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了着色器编译期间因多线程访问导致的 use-after-free 崩溃问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了日志格式化字符串中 32/64 位说明符与参数不匹配的问题，提升了代码健壮性。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 清理了冗余的 GPU 同步函数，统一使用更高效的提交并等待函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将传统的 UE_LOG 宏迁移到更现代的 UE_LOGF 宏，遵循最新的编码规范。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了着色器任务结构，用更通用的状态管理替换了特定的完成/释放标志，简化了代码。 |

### 维护评价

**状态：活跃维护中**。

该插件自创建以来一直保持更新，最近一次实质性更新（包括 bug 修复和功能重构）发生在 **2026 年 5 月**，距离现在非常近。更新记录显示开发团队正在积极解决跨线程安全问题、优化 API 使用、重构内部模块以及提升代码质量。虽然它仍被标记为**实验性** (`IsExperimentalVersion=true`)，但这表明它是 Epic 内部和 UE5 未来 NNE 功能的一个重要发展方向。鉴于其持续的维护和明确的性能目标，**推荐关注和测试使用**，但应清楚其 API 可能会发生变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
-   官方文档：无
-   测试用例：位于插件目录下的 `Tests/` 子文件夹中，例如 `Source/NNERuntimeIREE/Tests/`，但具体内容需查看源码。