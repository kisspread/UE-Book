# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 神经网络引擎 (NNE) 框架的一个具体运行时实现，它将 ONNX Runtime 作为其后端。该插件的核心作用是为开发者提供在 Unreal Engine 中加载和运行 ONNX 格式机器学习模型的能力。它通过 ONNX Runtime 库，利用 CPU 和 DirectML（DirectX 机器学习）执行提供程序进行推理加速，从而在游戏或实时应用中实现高性能的 AI 推理任务，例如实时图像处理、风格迁移或行为预测。

简单来说，它解决了“如何在 UE5 中运行一个现成的 ONNX 神经网络模型”的问题。

## 使用场景

-   **游戏内 AI 功能**：为 NPC 或游戏系统添加基于神经网络的决策能力，例如行为预测、环境感知。
-   **实时图像/视频处理**：实现游戏内的实时风格迁移、图像增强、超分辨率或物体检测等后处理效果。
-   **内容创作辅助**：在编辑器中或运行时，利用 AI 模型辅助资产生成、内容优化等任务。
-   **原型与研究**：快速在 UE 环境中验证和测试新的机器学习模型。

## 蓝图用法

该插件主要作为运行时后端，其核心功能通过 NNE 接口暴露，而非直接提供大量 `BlueprintCallable` 节点。在蓝图中，您通常会：

1.  通过 `UNNEModelData` 资产加载模型。
2.  使用 NNE 接口创建模型运行实例。
3.  调用推理函数进行计算。

更复杂的逻辑（如输入输出 Tensor 的准备与解析）通常在 C++ 层面完成。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeCPU.h" // 根据所需执行提供程序引入
```

### 基本用法

基于 NNE 标准接口，使用 NNERuntimeORT 后端进行推理。

```cpp
// 假设已经有一个加载好的 UNNEModelData* ModelData
// 1. 获取 NNERuntimeORT 运行时
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<INNERuntimeCPU>(); // 或 DirectML 对应接口

// 2. 使用模型数据和运行时创建模型实例
TWeakInterfacePtr<INNERuntimeGPUModel> Model;
if (Runtime && ModelData)
{
    Model = Runtime->CreateModel(ModelData->GetModelData());
}

// 3. 创建模型实例并进行推理（简化示例，实际需处理输入输出 Tensor 形状与数据）
if (Model)
{
    // ... 准备输入 Tensor 数据
    // 调用 Model->RunSync(...) 或 RunAsync(...)
}
```

**注意**：实际用法更复杂，涉及 Tensor (张量) 的创建、数据填充和形状管理，建议参考官方 NNE 教程和测试用例。

### 进阶用法

-   **异步推理**：使用 `RunAsync` 在后台线程执行推理，避免阻塞游戏线程。
-   **批量处理**：将多个输入数据组合成一个批次进行推理以提高吞吐量。
-   **多后端切换**：同一份 NNE 接口代码，可以无缝切换 NNERuntimeORT (CPU/DirectML) 或其他 NNE 运行时（如 TensorRT）。

## Demo 示例

一个最小的 C++ 示例，演示如何初始化并运行一个 ONNX 模型。

**MyAIComponent.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "NNE.h"
#include "MyAIComponent.generated.h"

class UNNEModelData;
class INNERuntimeGPUModel;

UCLASS(ClassGroup=(AI), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyAIComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UMyAIComponent();

protected:
	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
	// 模型资产引用，在蓝图编辑器中设置
	UPROPERTY(EditAnywhere, Category = "AI")
	TObjectPtr<UNNEModelData> ModelData;

	// NNE 运行时接口
	TWeakInterfacePtr<INNERuntime> Runtime;
	// 模型实例
	TWeakInterfacePtr<INNERuntimeGPUModel> ModelInstance;

	void InitializeModel();
	void RunInference();
};
```

**MyAIComponent.cpp**
```cpp
#include "MyAIComponent.h"
#include "NNEModelData.h"

UMyAIComponent::UMyAIComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UMyAIComponent::BeginPlay()
{
	Super::BeginPlay();
	InitializeModel();
}

void UMyAIComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (ModelInstance)
	{
		RunInference();
	}
}

void UMyAIComponent::InitializeModel()
{
	if (!ModelData) return;

	// 1. 获取运行时 (此处以 CPU 运行时为例)
	Runtime = UE::NNE::GetRuntime<INNERuntimeCPU>();
	if (!Runtime)
	{
		UE_LOG(LogTemp, Warning, TEXT("Failed to get NNE CPU Runtime"));
		return;
	}

	// 2. 创建模型实例
	ModelInstance = Runtime->CreateModel(ModelData->GetModelData());
	if (!ModelInstance)
	{
		UE_LOG(LogTemp, Warning, TEXT("Failed to create model instance"));
	}
}

void UMyAIComponent::RunInference()
{
	// 此处省略了具体的 Tensor 创建、数据填充和结果读取逻辑
	// 实际代码需要根据模型输入输出的定义来构建输入 Tensor 并解析输出 Tensor
	// TConstArrayView<UE::NNE::FTensor> InputTensors = { ... };
	// ModelInstance->RunSync(InputTensors, OutputTensors);
	UE_LOG(LogTemp, Log, TEXT("Model inference executed."));
}
```

## 模块依赖

要使用此插件，您的模块需要在 `Build.cs` 中添加对 `NNE` 模块的依赖。

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎的核心接口模块，所有 NNE 运行时的基础。 |

此外，插件本身静态链接了第三方库 `NNEOnnxruntime`（ONNX Runtime 和 DirectML），使用方无需额外处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级底层 ONNX Runtime 和 DirectML 库至新版本。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统从 UE_LOG 迁移至 UE_LOGF 宏。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退了某次提交的更改。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 再次尝试升级 ONNX Runtime 和 DirectML 库。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 代码重构，分离渲染相关头文件并添加显式包含。 |

### 维护评价

NNERuntimeORT 是一个于 **2023 年底创建**的较新插件，目前处于 **Beta 测试**阶段。从近期的 Git 提交记录看，它**仍在被积极维护**，更新内容主要包括核心依赖库（ONNX Runtime, DirectML）的版本升级和内部代码优化。这表明 Epic 正在持续改进其 NNE 生态系统。

作为 NNE 框架的关键运行时之一，它对于需要在 UE5 中进行本地机器学习推理的开发者至关重要。虽然它是 Beta 状态且默认未启用，但对于相关领域（如游戏 AI、计算机图形学研究）的探索和原型开发非常有价值。建议在使用时关注其版本更新和 API 变动。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT/Tests) *(推测路径，通常插件包含测试)*