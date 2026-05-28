# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

本插件为 Unreal Engine 的 **神经网络引擎 (NNE)** 提供了一个基于 **ONNX Runtime** 的推理后端。它允许开发者直接在 UE 应用程序中加载并运行 `.onnx` 格式的深度学习模型，利用 CPU 和 DirectML 进行硬件加速推理。其核心价值在于打通了从 PyTorch、TensorFlow 等主流框架训练出的模型到 Unreal Engine 实时应用的最后一公里，为游戏和应用的实时 AI 功能（如风格迁移、图像识别、行为预测）提供了高性能的本地推理能力。

## 使用场景

-   **游戏内实时AI**：你需要在游戏运行时对游戏画面、玩家输入或环境数据进行实时分析（如物体检测、动作识别），而非依赖云端服务。
-   **内容生成与增强**：例如实时风格迁移（将游戏画面转换为特定艺术风格）、超分辨率（提升低分辨率纹理）、图像修复等。
-   **复杂决策系统**：需要基于大量特征输入进行快速、复杂决策的NPC行为或游戏系统。
-   **跨平台机器学习部署**：你已在 Python 环境中训练好模型并导出为 `.onnx` 格式，希望在 Windows、Linux 或 macOS 平台的 Unreal 项目中直接使用，无需重写推理代码。

## 蓝图用法

本插件主要作为 NNE 的运行时后端，其核心功能通过 C++ API 暴露。蓝图接口相对简洁，主要用于获取运行时实例。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Runtime` | 获取 `NNERuntimeORT` 的单例运行时实例，用于后续的模型操作。 | `UNNERuntimeORTCpu` |
| `Get Runtime` | 获取支持 DirectML 加速的 `NNERuntimeORT` 运行时实例。 | `UNNERuntimeORTDml` |

### 使用示例（蓝图描述）

1.  在蓝图的“开始游戏”事件中，调用 `UNNERuntimeORTCpu::GetRuntime` 节点，将其返回值（运行时实例）存储在一个变量中。
2.  后续通过 NNE 的通用模型加载与推理节点（位于 NNE 核心插件中），结合上一步获取的运行时实例，来加载 ONNX 模型并执行推理。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeORT.h"
```

### 基本用法

以下代码展示了如何获取 CPU 运行时、创建模型实例并进行简单推理。
*(来源：`Engine/Tests/NNE/NNERuntimeORTTests/NNERuntimeORTTest.cpp`)*

```cpp
// 1. 获取运行时实例
TWeakInterfacePtr<INNERuntime> Runtime = UNNERuntimeORTCpu::GetRuntime();
checkf(Runtime.IsValid(), TEXT("获取NNERuntimeORT CPU运行时失败"));

// 2. 创建模型资源 (假设你已经有了一个UONNXModel*类型的资产引用)
UONNXModel* ModelAsset = LoadObject<UONNXModel>(nullptr, TEXT("/Game/Path/To/Your/Model.YourModel"));
UNNEModelData* ModelData = ModelAsset->ModelData;
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Runtime->CreateModelInstanceCPU(ModelData);

// 3. 准备输入和输出缓冲区
TConstArrayView<UE::NNE::FTensorDesc> InputTensorDescs = ModelInstance->GetInputTensorDescs();
TConstArrayView<UE::NNE::FTensorDesc> OutputTensorDescs = ModelInstance->GetOutputTensorDescs();

// 4. 设置输入数据 (此处为示例，需根据具体模型形状和数据类型填充)
TArray<float> InputData;
InputData.SetNumUninitialized(InputTensorDescs[0].GetElementCount());
// ... 填充 InputData ...

// 5. 执行推理
UE::NNE::FTensorBindingCPU InputBinding = { InputData.GetData(), InputData.Num() * sizeof(float) };
UE::NNE::FTensorBindingCPU OutputBinding = { OutputData.GetData(), OutputData.Num() * sizeof(float) };
ModelInstance->RunSync(MakeArrayView(&InputBinding, 1), MakeArrayView(&OutputBinding, 1));

// 6. 输出数据现已填充在 OutputData 中，可进行后续处理。
```

### 进阶用法

可以复用运行时实例和模型实例，对不同的输入数据进行批量推理，避免重复的初始化开销。

## Demo 示例

以下是一个最小、可编译的 C++ Actor 示例，演示如何加载 ONNX 模型并运行一次推理。

**NNERuntimeDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNERuntimeORT.h"
#include "NNERuntimeDemo.generated.h"

UCLASS()
class ANNERuntimeDemo : public AActor
{
	GENERATED_BODY()
public:
	// 在编辑器中设置你的 .onnx 模型资产
	UPROPERTY(EditAnywhere, Category = "NNE Demo")
	UONNXModel* ONNXModelAsset;

	virtual void BeginPlay() override;

private:
	// 运行时和模型实例
	TWeakInterfacePtr<INNERuntime> Runtime;
	TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

**NNERuntimeDemo.cpp**
```cpp
#include "NNERuntimeDemo.h"
#include "NNEModelData.h"

void ANNERuntimeDemo::BeginPlay()
{
	Super::BeginPlay();

	if (!ONNXModelAsset)
	{
		UE_LOG(LogTemp, Error, TEXT("未指定ONNX模型资产"));
		return;
	}

	// 1. 获取运行时
	Runtime = UNNERuntimeORTCpu::GetRuntime();
	if (!Runtime.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("获取NNERuntimeORT运行时失败"));
		return;
	}

	// 2. 创建模型实例
	UNNEModelData* ModelData = ONNXModelAsset->ModelData;
	ModelInstance = Runtime->CreateModelInstanceCPU(ModelData);
	if (!ModelInstance.IsValid())
	{
		UE_LOG(LogTemp, Error, TEXT("创建模型实例失败"));
		return;
	}

	UE_LOG(LogTemp, Log, TEXT("NNERuntimeORT模型加载成功，准备就绪。"));
}
```

## 模块依赖

要使用此插件，你的项目模块需要依赖以下核心模块（已在 `NNERuntimeORT.Build.cs` 中声明）。

| 模块 | 用途 |
|---|---|
| `NNE` | 提供神经网络引擎（NNE）的核心接口和类型定义，是本插件运行的基础。 |
| `NNEOnnxruntime` (External) | 封装了 ONNX Runtime 第三方库，提供底层的推理引擎实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 将核心的ONNX Runtime库升级至1.24.3，DirectML升级至1.15.4，提升性能和兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志输出宏现代化，统一使用UE_LOGF格式。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530. | 回滚了一次变更，可能用于修复前一次提交引入的问题。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 此前被回滚的ONNX Runtime与DirectML库升级提交。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 将渲染资源相关的头文件拆分，优化编译依赖。 |

### 维护评价

**活跃维护中**。尽管插件标记为 `IsBetaVersion = true`，但从提交记录看，**维护非常活跃**。最近一次更新（ONNX Runtime 升级）距离现在仅数月，且更新内容实质（库版本升级、编译优化）。这表明插件仍处于积极的开发和改进阶段，功能在不断完善。

作为 NNE 生态的关键一环，它提供了在 UE 中运行标准 ONNX 模型的稳定路径。虽然标记为 Beta，但鉴于其明确的官方来源（Epic Games）和持续的维护，**推荐开发者在新项目中积极试用**，特别是对于需要本地高性能机器学习推理的场景。注意其 `EnabledByDefault = false`，需要在项目设置中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
-   [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/NNE/NNERuntimeORTTests)