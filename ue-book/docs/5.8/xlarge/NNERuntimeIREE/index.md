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

NNERuntimeIREE 是一个基于 IREE（Intermediate Representation Execution Environment）框架的神经网络运行时。它并非简单的推理引擎，而是一个**编译器驱动的运行时**。其核心价值在于利用 MLIR 和 LLVM 工具链，将神经网络模型**直接编译为针对目标平台（CPU/GPU）的原生机器码**，从而获得比传统解释型运行时（如 ONNX Runtime）更高的推理性能，特别适用于游戏内对延迟敏感的实时神经网络推理。

## 使用场景

- **高性能游戏内推理**：当你需要在游戏的每帧或高频循环中运行小型神经网络（如动作识别、实时图像分割、简单决策模型）时，此插件通过编译优化可提供比传统方案更优的性能。
- **跨平台部署**：IREE 框架支持多种后端（CPU、Vulkan、CUDA 等），使用此运行时可以编写一次模型部署逻辑，通过 IREE 的编译能力适配不同目标平台。
- **需要访问底层优化**：当标准的 NNE 运行时（如 NNEOnnxRuntime）性能无法满足需求，且愿意接受实验性风险以换取更高性能时，可考虑此方案。

## 模块列表

此插件规模较大（xlarge），包含多个模块，各模块职责如下：

| 模块 | 类型 | 简要说明 |
|---|---|---|
| [NNERuntimeIREE](NNERuntimeIREE.md) | Runtime | 核心运行时模块，实现 NNE 的 IRuntime 接口，负责模型编译、编译缓存和编译后的模型实例管理。 |
| [IREEDriverRDG](IREEDriverRDG.md) | Runtime | IREE 的 Render Dependency Graph (RDG) 驱动，用于通过 UE 的 RDG 系统调度 GPU 工作负载。 |
| [IREETracing](IREETracing.md) | Runtime | IREE 的性能追踪集成模块，将 IREE 的追踪事件桥接到 UE 的分析系统。 |
| [IREEUtils](IREEUtils.md) | Runtime | IREE 通用工具函数库，提供内存管理、错误处理等辅助功能。 |
| [NNERuntimeIREEShader](NNERuntimeIREEShader.md) | Runtime | 处理 IREE 编译生成的 GPU 着色器模块的加载与管理。 |
| [NNERuntimeIREEEditor](NNERuntimeIREEEditor.md) | Runtime | 编辑器相关功能，如资产处理、可视化调试等（模块类型为 Runtime 可能为兼容性设置）。 |
| [IREE](IREE.md) | External | 第三方 IREE 框架库的构建集成模块。 |
| [NNEMlirTools](NNEMlirTools.md) | External | 第三方 MLIR 工具链库的构建集成模块。 |

*每个子模块的详细 API、使用示例和设计说明，请参见对应的文档链接。*

## 蓝图用法

该运行时主要通过 Unreal Engine 的统一 **NNE (Neural Network Engine)** 接口暴露功能，而非直接提供大量蓝图节点。核心使用流程在蓝图中可通过以下通用 NNE 节点实现：

1.  **获取运行时**：使用 `Get Runtime` 节点，将 `UClass` 设为 `UNNERuntimeIREE`（或在插件设置中将其设为默认运行时）。
2.  **创建模型实例**：使用 `Create Model Instance` 节点，加载 `.onnx` 等模型资产。
3.  **设置输入并运行**：调用模型实例的 `Set Input Tensor` 和 `Run Sync/Run Async` 节点。
4.  **获取输出**：通过 `Get Output Tensor` 节点读取结果。

具体节点的使用方法请参考 **NNE 插件**的官方文档，本插件是其底层运行时之一。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeIREE.h" // 或 NNERuntimeIREEShader.h，取决于具体使用场景
```

### 基本用法

以下为通过 NNE 统一接口使用 IREE 运行时的基本流程。
*来源：通用 NNE 使用模式*

```cpp
// 1. 获取 IREE 运行时
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<UNNERuntimeIREE>();
if (!Runtime.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to get IREE Runtime."));
    return;
}

// 2. 加载模型资源 (假设 ModelAsset 已在编辑器中准备好，类型为 UNNEModelData)
TObjectPtr<UNNEModelData> ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/Path/To/MyModel.MyModel"));
if (!ModelData) return;

// 3. 创建模型实例
TSharedPtr<UE::NNE::IModelInstanceGPU> ModelInstance = Runtime->CreateModelInstanceGPU(ModelData).Get();
if (!ModelInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance."));
    return;
}

// 4. 准备输入/输出张量数据（此处为示例，具体形状和数据需根据模型而定）
TConstArrayView<uint32> InputTensorShape = {1, 3, 224, 224};
TArray<float> InputData(InputTensorShape[0] * InputTensorShape[1] * InputTensorShape[2] * InputTensorShape[3]);
// ... 填充 InputData ...

TConstArrayView<uint32> OutputTensorShape = {1, 1000};
TArray<float> OutputData(OutputTensorShape[0]);

// 5. 设置输入输出并运行推理
ModelInstance->SetInputTensorData(0, MakeShared<UE::NNE::FTensorDataCPU>(InputData));
ModelInstance->SetOutputTensorData(0, MakeShared<UE::NNE::FTensorDataCPU>(OutputData));
ModelInstance->RunSync(); // 或使用 RunAsync
```

### 进阶用法

更高级的用法涉及 GPU 数据的零拷贝推理、使用 RDG 驱动将推理任务集成到渲染管线中，以及手动管理编译缓存等。这些功能分别由 `IREEDriverRDG` 和 `NNERuntimeIREEShader` 模块支持，请参阅对应模块的详细文档。

## Demo 示例

一个最小可编译的示例，展示如何通过 C++ 加载模型并运行一次同步推理。

**MyAIDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyAIDemo.generated.h"

UCLASS()
class AMyAIDemo : public AActor
{
    GENERATED_BODY()
public:
    AMyAIDemo();

    // 在编辑器中指定一个 UNNEModelData 资产
    UPROPERTY(EditAnywhere, Category="AI")
    TObjectPtr<UNNEModelData> ModelAsset;

    virtual void BeginPlay() override;

private:
    TWeakInterfacePtr<INNERuntime> Runtime;
    TSharedPtr<UE::NNE::IModelInstanceGPU> ModelInstance;
};
```

**MyAIDemo.cpp**
```cpp
#include "MyAIDemo.h"
#include "NNE.h"
#include "NNERuntimeIREE.h"

AMyAIDemo::AMyAIDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyAIDemo::BeginPlay()
{
    Super::BeginPlay();

    // 获取运行时并创建实例（示例，实际应添加错误处理和异步逻辑）
    Runtime = UE::NNE::GetRuntime<UNNERuntimeIREE>();
    if (Runtime.IsValid() && ModelAsset)
    {
        ModelInstance = Runtime->CreateModelInstanceGPU(ModelAsset).Get();
        if (ModelInstance.IsValid())
        {
            // 此处可进行一次测试推理...
            UE_LOG(LogTemp, Log, TEXT("IREE Model Instance created successfully."));
        }
    }
}
```

## 模块依赖

使用此插件中的功能时，你的项目模块 `Build.cs` 文件可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `NNERuntimeIREE` | 核心运行时，如果你想直接操作 IREE 特有的编译缓存等高级功能。 |
| `NNE` | NNE 框架核心接口，**必须依赖**，所有推理操作都通过此模块的接口进行。 |
| `IREE` | 第三方 IREE 库，如果你需要链接 IREE 的原生 C API。 |
| `IREETracing` | 集成 IREE 性能追踪。 |
| `IREEDriverRDG` | 将推理任务通过 RDG 提交到 GPU 渲染管线。 |

*注意：通常情况下，只需依赖 `NNE` 即可通过统一接口使用所有运行时。直接依赖其他内部模块通常只用于深度集成或调试。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复着色器编译期间跨线程资源释放后使用的问题，提升稳定性。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复32/64位平台下日志格式说明符不匹配的问题。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构 GPU 同步接口，使用更统一的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF`，可能是向新版日志系统过渡。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构着色器作业状态机，移除显式的状态标志，使用更抽象的状态管理。 |

### 维护评价

**活跃维护**。该插件创建于2023年底，至今仍在积极更新。从近期的 Git 历史来看，开发团队持续进行着**关键错误修复**（如跨线程安全）、**代码现代化**（日志迁移）、**API 重构**（GPU 同步、着色器管理）以及**平台适配性**（32/64位格式符）等工作。尽管仍标记为实验性（`IsExperimentalVersion=true`），但其迭代速度表明它是 Epic 在 AI/ML 运行时领域一个**重点投入和探索的项目**。

对于追求极致推理性能且愿意承担实验性风险的项目，这是一个值得关注和试用的运行时选项。建议在主要平台上进行充分测试后再用于生产环境。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE/Tests)
- **官方文档**：暂无专门文档，请参考 Unreal Engine 官方文档中关于 **NNE (Neural Network Engine)** 的部分。