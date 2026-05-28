# NNERuntimeIREE

> A runtime implementing the Neural Network Engine (NNE) API which is based on IREE, MLIR and LLVM and compiles neural networks directly to game code.

| 属性 | 值 |
|---|---|
| 中文名 | IREE 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeIREE` (Runtime), `NNERuntimeIREEEditor` (Runtime), `NNERuntimeIREEShader` (Runtime), `IREEDriverRDG` (Runtime), `IREETracing` (Runtime), `IREEUtils` (Runtime), `IREE` (External), `NNEMlirTools` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-22 |
| 年龄标签 | 🍃 新兴（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE) | |

## 用途

NNERuntimeIREE 插件提供了一个基于现代编译器技术的神经网络运行时后端。它解决了在 Unreal Engine 游戏中实时、高性能运行小型神经网络的问题。与之前基于 ONNX Runtime 的 CPU 运行时（ORTCpu）相比，它通过 IREE 框架将神经网络模型（如 ONNX 格式）编译为高效的、平台原生的代码（包括 CPU 机器码和 GPU 着色器），从而在运行时提供更佳的性能，尤其是在处理小型网络时。该插件是 UE5 神经网络引擎 (NNE) 框架的一个可选后端实现。

## 使用场景

-   **实时游戏 AI**：你需要在游戏中运行实时推理的小型神经网络模型（例如行为决策、简单图像分类、角色动画状态检测），并且追求比标准 ORT CPU 后端更低的延迟和更高的吞吐量。
-   **跨平台部署**：你的游戏需要支持多种硬件平台（如 Windows, Linux, 主机），并希望使用同一个模型文件，由运行时针对当前平台的 CPU 或 GPU 架构进行最优编译。
-   **集成 GPU 计算到渲染管线**：你需要利用神经网络进行一些计算密集型任务（例如程序化内容生成、后处理），并希望将这些计算直接集成到 UE 的渲染依赖图 (RDG) 中，减少数据拷贝，与现有渲染操作高效协同。
-   **编译型工作流**：你倾向于将模型提前编译为原生库，而不是在运行时解释执行，以获得最佳性能。

## 蓝图用法

NNERuntimeIREE 主要是一个 C++ 插件，不直接暴露蓝图节点。其功能通过标准的 NNE 蓝图接口（如 `UNNERuntime` 资产）被间接使用。使用前，需要在项目设置中启用该插件，并在 NNE 相关设置中将其对应的运行时（如 `NNERuntimeIREECpu`）设为可用。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Runtime Name` | 获取运行时名称（如 "NNERuntimeIREECpu"），用于标识。 | `UNNERuntimeIREECpu` 等 |
| `Can Create Model CPU/GPU/RDG` | 检查给定模型数据是否能被当前运行时创建对应的 CPU/GPU/RDG 模型。 | `UNNERuntimeIREECpu`, `UNNERuntimeIREEGpu`, `UNNERuntimeIREERdg` |
| `Create Model CPU/GPU/RDG` | 从模型数据创建可用于推理的 CPU/GPU/RDG 模型实例。 | `UNNERuntimeIREECpu`, `UNNERuntimeIREEGpu`, `UNNERuntimeIREERdg` |

### 使用示例（蓝图描述）

1.  **加载模型并创建模型实例**：
    *   使用 `Load Model Data` 节点从文件或数据资产加载 `UNNEModelData`。
    *   获取一个已注册的 `NNERuntimeIREECpu` 运行时实例。
    *   调用 `Create Model CPU` 节点，传入模型数据，获得一个 `IModelCPU` 对象。
    *   在该对象上调用 `Create Model Instance CPU` 获得一个可执行的模型实例。

2.  **运行推理**：
    *   在模型实例上调用 `Set Input Tensor Shapes` 设置输入张量的形状（如果模型支持动态形状）。
    *   准备输入和输出张量数据（`FTensorBindingCPU`）。
    *   调用 `Run Sync` 节点执行推理。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h" // 核心 NNE 接口
#include "NNERuntimeIREE.h" // IREE 运行时特定头文件（通常不直接包含）
```

### 基本用法

使用 NNE 运行时的标准模式加载模型并创建 CPU 模型实例。

```cpp
// 假设你已经有了 TSharedPtr<UE::NNE::FSharedModelData> ModelData;
// 通常通过 UNNERuntime 的 CreateModelData 获取

// 1. 获取 IREE CPU 运行时 (通常通过 NNE 模块注册表查找)
TArray<INNERuntime*> Runtimes;
UNNE::Get().GetAllRuntimes(Runtimes);
INNERuntime* IREERuntime = nullptr;
for (auto* Runtime : Runtimes)
{
    if (Runtime && Runtime->GetRuntimeName() == TEXT("NNERuntimeIREECpu"))
    {
        IREERuntime = Runtime;
        break;
    }
}
if (!IREERuntime) return;

// 2. 使用运行时创建模型
if (IREERuntime->CanCreateModelCPU(ModelData.Get()) == ECanCreateModelCPUStatus::Fail)
{
    // 处理错误
    return;
}
TSharedPtr<UE::NNE::IModelCPU> Model = IREERuntime->CreateModelCPU(ModelData.Get());
if (!Model) return;

// 3. 创建模型实例
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstanceCPU();
if (!ModelInstance) return;

// 4. 设置输入形状 (如果需要)
TArray<UE::NNE::FTensorShape> InputShapes;
// ... 根据模型定义填充 InputShapes
auto SetStatus = ModelInstance->SetInputTensorShapes(InputShapes);
if (SetStatus != UE::NNE::IModelInstanceCPU::ESetInputTensorShapesStatus::Ok) return;

// 5. 准备输入输出并运行推理
TArray<float> InputData, OutputData;
// ... 填充 InputData
TArray<UE::NNE::FTensorBindingCPU> InputBindings = { {InputData.GetData(), InputData.Num() * sizeof(float)} };
TArray<UE::NNE::FTensorBindingCPU> OutputBindings = { {OutputData.GetData(), OutputData.Num() * sizeof(float)} };
auto RunStatus = ModelInstance->RunSync(InputBindings, OutputBindings);
if (RunStatus != UE::NNE::IModelInstanceCPU::ERunSyncStatus::Ok) return;
// OutputData 现在包含推理结果
```

### 进阶用法

使用 RDG 运行时将推理集成到渲染管线中。

```cpp
// 假设已获取 IRDG 运行时 (INNERuntimeRDG*) 和创建了 RDG 模型 (IModelRDG*) 及其实例 (IModelInstanceRDG*)

// 在 RDG Pass 中执行推理
FRDGBuilder& GraphBuilder = ...; // 当前 RDG 构建器
TConstArrayView<UE::NNE::FTensorBindingRDG> InputBindings = ...; // RDG 资源绑定
TConstArrayView<UE::NNE::FTensorBindingRDG> OutputBindings = ...;

auto EnqueueStatus = RDGModelInstance->EnqueueRDG(GraphBuilder, InputBindings, OutputBindings);
if (EnqueueStatus == UE::NNE::IModelInstanceRDG::EEnqueueRDGStatus::Ok)
{
    // 推理计算将作为 RDG Pass 被自动调度和执行
}
```

## Demo 示例

一个最小化的 CPU 推理示例。演示如何从已知的模型数据中运行推理。

```cpp
// MyNNEActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "MyNNEActor.generated.h"

UCLASS()
class AMyNNEActor : public AActor
{
	GENERATED_BODY()

public:
	AMyNNEActor();

	virtual void BeginPlay() override;

	// 用于测试的模型数据资产引用
	UPROPERTY(EditAnywhere, Category="NNE")
	TObjectPtr<UNNEModelData> ModelDataAsset;

private:
	TSharedPtr<UE::NNE::IModelCPU> Model;
	TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

```cpp
// MyNNEActor.cpp
#include "MyNNEActor.h"
#include "NNERuntimeIREE.h" // 可选，用于类型提示

AMyNNEActor::AMyNNEActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyNNEActor::BeginPlay()
{
	Super::BeginPlay();

	if (!ModelDataAsset || !ModelDataAsset->ModelData.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("Model Data Asset is invalid!"));
		return;
	}

	// 1. 获取 IREE CPU 运行时
	TArray<INNERuntime*> Runtimes;
	UNNE::Get().GetAllRuntimes(Runtimes);
	UE::NNE::IModelCPU* IREERuntime = nullptr;
	for (auto* Runtime : Runtimes)
	{
		// 尝试将运行时转换为 INNERuntimeCPU 并检查是否是 IREE 实现
		// 这里简化处理，实际应更严谨
		if (Runtime && Runtime->GetRuntimeName().Contains(TEXT("IREE")))
		{
			// 假设找到了 CPU 运行时
			IREERuntime = static_cast<UE::NNE::IModelCPU*>(Runtime);
			break;
		}
	}
	if (!IREERuntime)
	{
		UE_LOG(LogTemp, Error, TEXT("Could not find IREE CPU Runtime!"));
		return;
	}

	// 2. 创建模型 (通常在加载时完成一次)
	Model = IREERuntime->CreateModelCPU(ModelDataAsset);
	if (!Model)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create IREE Model!"));
		return;
	}

	// 3. 创建模型实例
	ModelInstance = Model->CreateModelInstanceCPU();
	if (!ModelInstance)
	{
		UE_LOG(LogTemp, Error, TEXT("Failed to create IREE Model Instance!"));
		return;
	}

	// 4. 准备并运行推理 (假设模型输入输出形状已知)
	TArray<float> InputData(10, 1.0f); // 示例输入
	TArray<float> OutputData(5, 0.0f); // 示例输出缓冲区

	TConstArrayView<UE::NNE::FTensorBindingCPU> Inputs = { {InputData.GetData(), InputData.Num() * sizeof(float)} };
	TConstArrayView<UE::NNE::FTensorBindingCPU> Outputs = { {OutputData.GetData(), OutputData.Num() * sizeof(float)} };

	auto RunStatus = ModelInstance->RunSync(Inputs, Outputs);
	if (RunStatus == UE::NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
	{
		UE_LOG(LogTemp, Log, TEXT("Inference succeeded. Output[0]: %f"), OutputData[0]);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("Inference failed!"));
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，提供 `INNERuntime`, `IModelCPU` 等基础接口。 |
| `RenderCore` | RDG 运行时所需，用于构建渲染依赖图。 |
| `RHI` | RDG 和 GPU 运行时所需的渲染硬件接口抽象。 |
| `Projects` | 用于查询插件状态和平台信息。 |
| `IREE` (External) | IREE 框架的第三方库封装。 |
| `NNEMlirTools` (External) | MLIR 工具链的第三方库封装。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `9456b28d` | [NNE] NNERuntimeIREERdg fix cross-thread use-after-free during shader cook. | 修复了 RDG 运行时在 Shader Cook 期间的跨线程使用后释放错误。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式化字符串说明符与参数位宽不匹配的问题。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一了 GPU 同步接口，用 `SubmitAndBlockUntilGPUIdle` 替换了旧函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 `UE_LOGF` 格式。 |
| 2026-04-09 | `e0689004` | [shaders] remove explicit finalized/released flags from job struct, replace with extended/refactored | 重构了 Shader 作业结构体的状态管理逻辑。 |

### 维护评价

NNERuntimeIREE 是一个**非常活跃**的实验性插件。尽管它创建于约 2 年前，但自 2026 年 4 月以来有持续且密集的更新，主要聚焦于**Bug 修复（特别是 RDG 运行时）、代码重构、API 标准化和平台兼容性改进**。这些更新表明 Epic Games 内部正在积极使用和开发该插件，用于解决实时神经网络推理的需求。

**优点**：
*   **技术前沿**：采用 IREE/MLIR/LLVM 编译型方案，代表了游戏 AI 运行时的前沿方向。
*   **性能潜力**：针对游戏场景优化，尤其对小型模型性能优于传统解释执行。
*   **积极维护**：近期更新非常频繁，核心团队在持续改进。

**限制与注意**：
*   **实验性**：插件标记为实验性 (`IsExperimentalVersion=true`)，默认不启用，API 和行为可能在未来版本中发生变化。
*   **复杂性**：依赖于庞大的编译器工具链（IREE, LLVM），对环境配置和模型转换流程有一定要求。
*   **平台支持**：GPU 运行时依赖特定的图形 API（CUDA/Vulkan），需要目标平台支持。

**结论**：如果你正在寻求 UE5 中最高性能的神经网络推理方案，并且愿意接受实验性状态和相应的复杂性，**强烈推荐试用和关注此插件**。它是 NNE 框架中最具潜力的后端之一。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeIREE)
- [官方文档]() (暂无)
- [测试用例]() (测试通常位于 Engine/Tests/ 目录下，需查找相关自动化测试模块)