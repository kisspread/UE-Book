# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | NNE ONNX 运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 1.5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

`NNERuntimeORT` 是 Unreal Engine 神经网络引擎 (NNE) 的一个 **运行时后端** 插件。它本身不包含 NNE 的核心框架，而是作为 NNE 的一个可插拔的“执行器”存在。

该插件的核心作用是将 **ONNX 格式的神经网络模型** 加载到内存中，并利用 **ONNX Runtime** 库在 CPU 或支持 DirectML 的 GPU 上执行模型的前向推理（即模型推理/预测）。它解决了在 UE 应用程序中高效运行预训练好的 ONNX 神经网络模型的需求。

**简而言之：**
*   **NNE**：是 UE 的神经网络引擎框架（类似一个总线）。
*   **NNERuntimeORT**：是插在 NNE 上的一个“引擎”（后端实现），专门负责运行 ONNX 模型。

## 使用场景

你需要在 Unreal Engine 项目中加载并运行一个使用 ONNX 格式训练好的神经网络模型时，就需要用到此插件。典型场景包括：
*   使用 AI 模型进行实时图像风格迁移（如将游戏画面转换为特定艺术风格）。
*   在游戏中运行复杂的 AI 行为决策模型（非传统的行为树）。
*   集成计算机视觉模型进行物体检测或识别。
*   利用预训练的语音或自然语言处理模型。

## 蓝图用法

根据源码分析，`NNERuntimeORT` 插件主要提供 C++ 接口，作为 NNE 系统的后端实现。其公共 API 主要通过 NNE 框架暴露，而非直接在蓝图中提供独有的节点。要使用此插件运行的模型，应通过 **NNE 插件** 提供的通用蓝图节点来加载 `UNNEModelData` 并创建模型实例，系统会自动调用此插件作为后端执行。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| （无直接暴露的独立蓝图函数） | 通过 NNE 框架的通用接口使用，例如 `CreateModelCPU`, `CreateModelGPU` 等。 | N/A |

### 使用示例（蓝图描述）

1.  首先，确保在项目设置中启用了 `NNE` 和 `NNERuntimeORT` 插件。
2.  将 ONNX 模型文件（`.onnx`）导入 UE 项目，会自动创建 `UNNEModelData` 资产。
3.  在蓝图中，使用 NNE 框架提供的 `Create Model Instance (CPU)` 或类似节点，指定对应的 `UNNEModelData`。
4.  系统会根据 `UNNEModelData` 的格式（ONNX）自动选择 `NNERuntimeORT` 这个运行时来创建和运行模型实例。
5.  之后使用 `Set Input Tensor Shapes`, `Run Sync` 等通用 NNE 节点进行推理。

## C++ 用法

此插件的核心是实现 NNE 定义的运行时接口，供 NNE 框架在后台调用。对于上层开发者而言，主要的交互方式是通过 NNE 的公共 API。

### 头文件引入

使用 NNE 框架的公共头文件即可，无需直接包含此插件的头文件。

```cpp
#include "NNE.h"
```

### 基本用法

以下示例展示了如何通过 NNE 的公共 API，隐式地使用 NNERuntimeORT 后端来加载模型并进行推理。

```cpp
// 假设已有一个 UNNEModelData* ModelData (从资产中加载)
TObjectPtr<UNNEModelData> ModelData = ...; // 来自资产引用

// 1. 创建一个 CPU 模型实例。NNE 会根据 ModelData 的内部格式（ONNX）自动选择 NNERuntimeORT 后端。
TSharedPtr<UE::NNE::IModelCPU> ModelCPU = UE::NNE::GetRuntime<UE::NNE::INNERuntimeCPU>()->CreateModelCPU(ModelData);
if (!ModelCPU.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance."));
    return;
}

// 2. 创建模型实例
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = ModelCPU->CreateModelInstanceCPU();
if (!ModelInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance."));
    return;
}

// 3. 准备输入张量数据 (示例为一个包含 1x3x224x224 浮点数据的数组)
TArray<float> InputData;
InputData.SetNumUninitialized(1 * 3 * 224 * 224);
// ... 填充 InputData ...

// 定义输入张量形状 (N, C, H, W)
TArray<UE::NNE::FTensorShape> InputShapes;
InputShapes.Add(UE::NNE::FTensorShape::Make({1, 3, 224, 224}));

// 4. 设置输入形状
if (ModelInstance->SetInputTensorShapes(InputShapes) != UE::NNE::IModelInstanceCPU::ESetInputTensorShapesStatus::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to set input shapes."));
    return;
}

// 5. 准备张量绑定，将数据指针与输入/输出关联
UE::NNE::FTensorBindingCPU InputBinding;
InputBinding.Data = InputData.GetData();
InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

TArray<float> OutputData;
OutputData.SetNumUninitialized(1000); // 假设输出为 1000 类
UE::NNE::FTensorBindingCPU OutputBinding;
OutputBinding.Data = OutputData.GetData();
OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

// 6. 执行同步推理
auto Status = ModelInstance->RunSync(TConstArrayView<UE::NNE::FTensorBindingCPU>({InputBinding}), TConstArrayView<UE::NNE::FTensorBindingCPU>({OutputBinding}));
if (Status != UE::NNE::IModelInstanceCPU::ERunSyncStatus::Ok)
{
    UE_LOG(LogTemp, Error, TEXT("Inference failed."));
    return;
}

// 7. 处理 OutputData
// ... 对 OutputData 进行后处理 ...
```

## Demo 示例

一个最小的、可编译的 C++ 示例，展示如何使用 NNE 的 CPU 接口来加载 ONNX 模型并执行推理。

```cpp
// MyAIActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "MyAIActor.generated.h"

UCLASS()
class MYPROJECT_API AMyAIActor : public AActor
{
    GENERATED_BODY()

public:
    AMyAIActor();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "AI")
    TObjectPtr<UNNEModelData> ModelDataAsset;

private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

```cpp
// MyAIActor.cpp
#include "MyAIActor.h"

AMyAIActor::AMyAIActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyAIActor::BeginPlay()
{
    Super::BeginPlay();

    if (!ModelDataAsset)
    {
        UE_LOG(LogTemp, Warning, TEXT("ModelDataAsset is null."));
        return;
    }

    // 获取 NNE 的 CPU 运行时并创建模型
    UE::NNE::INNERuntimeCPU* RuntimeCPU = UE::NNE::GetRuntime<UE::NNE::INNERuntimeCPU>();
    if (!RuntimeCPU)
    {
        UE_LOG(LogTemp, Error, TEXT("NNE CPU runtime not available."));
        return;
    }

    Model = RuntimeCPU->CreateModelCPU(ModelDataAsset);
    if (!Model.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model from data."));
        return;
    }

    // 创建模型实例
    ModelInstance = Model->CreateModelInstanceCPU();
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model instance."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("NNE Model (via NNERuntimeORT) loaded successfully."));
}
```

## 模块依赖

此插件作为 NNE 的后端，其核心依赖在于 NNE 框架本身。它还需要链接随插件一同提供的 ONNX Runtime 第三方库。

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心框架，本插件是它的后端实现。 |
| `NNEOnnxruntime` | 本插件附带的第三方模块，封装了 ONNX Runtime 库的链接。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级了核心依赖 ONNX Runtime 和 DirectML 的版本。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退了之前的某项改动。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 同上，升级第三方库版本的提交（可能被回退后重新提交）。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 代码重构，将部分渲染相关类拆分到独立头文件中。 |

### 维护评价

*   **活跃维护**：该插件自 2023 年 11 月创建以来，持续有功能更新和依赖升级，最近的提交集中在 2026 年初，表明仍在积极维护中。
*   **实验性/Beta 状态**：`.uplugin` 中明确标记 `IsBetaVersion: true` 且 `EnabledByDefault: false`，说明它仍处于 Beta 测试阶段，API 和功能可能在未来版本发生变化。
*   **平台支持**：当前支持 Windows (x64)、Linux (x64, ARM64) 和 Mac，覆盖了主流开发平台。
*   **推荐**：对于需要在 UE 项目中运行 ONNX 模型的开发者，这是目前官方提供的、且仍在维护的解决方案。尽管是 Beta 版，但已用于 Epic 内部的风格迁移等项目。建议在开发中关注其 API 变更日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)