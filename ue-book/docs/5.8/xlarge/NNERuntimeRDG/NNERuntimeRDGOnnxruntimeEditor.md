# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | RDG 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (Runtime), `NNERuntimeRDG` (Runtime), `NNERuntimeRDGData` (Runtime), `NNERuntimeRDGUtils` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-06-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 UE5 神经网络引擎（NNE）的一个**推理运行时后端**，它通过 UE 的渲染依赖图（RDG）系统来执行 ONNX 格式的神经网络模型。

该插件解决的核心问题是：如何在 UE 的 GPU 渲染管线中高效地执行机器学习推理。与直接调用第三方推理引擎不同，NNERuntimeRDG 将模型推理操作转化为 HLSL 着色器，通过 RDG 调度在 GPU 上执行，从而与 UE 的渲染系统深度集成，避免了 CPU↔GPU 之间的数据搬运开销。

插件内部集成了 ONNX Runtime 的模型解析能力（用于加载和优化 ONNX 模型），但实际的算子执行由自定义 HLSL 着色器在 RDG 中完成。同时支持 Windows 上的 DirectML 加速和跨平台的 Metal/Vulkan RHI 后端。

> ⚠️ **实验性插件**：此插件默认未启用（`EnabledByDefault=false`），且标记为实验性（`IsExperimentalVersion=true`）。API 可能在未来版本中发生变化。

## 使用场景

- 你需要在 UE 项目中运行 ONNX 格式的 ML 模型，并希望利用 GPU 渲染管线进行推理 → 使用 NNERuntimeRDG
- 你的 ML 推理需要与渲染管线紧密集成（例如风格迁移、图像增强后处理） → 使用 NNERuntimeRDG 的 RDG 调度
- 你需要在不引入额外第三方推理框架的前提下在 UE 内运行神经网络 → 使用 NNERuntimeRDG（内置 ONNX Runtime 模型解析）
- 你需要跨平台（Windows/Linux/Mac）的 ML 推理能力 → NNERuntimeRDG 支持 MetalRHI 和 VulkanRHI 后端

## 蓝图用法

NNERuntimeRDG 本身不直接暴露 BlueprintCallable 函数。它作为 NNE 框架的一个运行时实现，通过 NNE 的运行时注册机制自动注册。用户通过 NNE 插件的公共 API 进行交互。

### 通过 NNE API 使用

| 节点 | 说明 | 所在插件 |
|---|---|---|
| `UNNEModelData::CreateModelData` | 从 ONNX 模型二进制创建模型数据 | NNE |
| `INNERuntime::CreateModel` | 创建可推理的模型实例 | NNE（NNERuntimeRDG 实现） |
| `INNEModelInstance::RunSync` | 同步执行推理 | NNE（NNERuntimeRDG 实现） |

### 使用示例（蓝图描述）

在蓝图中使用 NNE 时：
1. 通过 `UNNEModelData` 加载 ONNX 模型资产
2. 从可用运行时中选择 RDG 运行时创建模型实例
3. 设置输入张量数据（浮点数组）
4. 调用推理节点获取输出张量

注意：所有 NNE 蓝图节点来自 NNE 核心插件，NNERuntimeRDG 只是其后端之一。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeRDG.h"
```

### 基本用法

通过 NNE 公共 API 获取 RDG 运行时并执行推理。以下为典型使用模式：

```cpp
// 源自 NNE 运行时注册模式
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeRDG.h"

// 1. 获取 NNE 运行时
TArray<UNNERuntime*> Runtimes = UNNE::GetAllRuntimes();
UNNERuntime* RDGRuntime = nullptr;
for (UNNERuntime* Runtime : Runtimes)
{
    if (Runtime && Runtime->GetName().Contains(TEXT("RDG")))
    {
        RDGRuntime = Runtime;
        break;
    }
}

// 2. 加载 ONNX 模型数据
// ModelData 可从 UAsset 或内存中加载
TObjectPtr<UNNEModelData> ModelData = NewObject<UNNEModelData>();
ModelData->SetModelData(OnnxModelBytes, "onnx");

// 3. 创建模型
TUniquePtr<INNERuntimeRDG> RuntimeRDG = MakeUnique<INNERuntimeRDG>();
TUniquePtr<INNERuntimeRDGModel> Model = RuntimeRDG->CreateModel(ModelData);
```

### 进阶用法

结合多个输入/输出张量进行推理：

```cpp
#include "NNE.h"
#include "NNETensor.h"
#include "NNERuntimeRDG.h"

// 准备输入张量
TArray<float> InputData;
InputData.SetNumUninitialized(InputSize);
// ... 填充输入数据 ...

// 定义张量形状
FNNEInferenceShape InputShape = {1, 3, 224, 224};  // NCHW 格式
FNNEInferenceTensor InputTensor = {InputData.GetData(), InputShape};

// 定义输出张量
TArray<float> OutputData;
OutputData.SetNumUninitialized(OutputSize);
FNNEInferenceShape OutputShape = {1, 1000};
FNNEInferenceTensor OutputTensor = {OutputData.GetData(), OutputShape};

// 执行推理（通过 RDG 在 GPU 上执行）
TArray<FNNEInferenceTensor> Inputs = {InputTensor};
TArray<FNNEInferenceTensor> Outputs = {OutputTensor};
ModelInstance->RunSync(Inputs, Outputs);
```

## Demo 示例

以下为一个最小化的 C++ 示例，展示如何使用 NNERuntimeRDG 进行推理。

### MyNNERuntimeDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNE.h"
#include "NNERuntimeRDG.h"
#include "GameFramework/Actor.h"
#include "MyNNERuntimeDemo.generated.h"

UCLASS()
class MYPROJECT_API AMyNNERuntimeDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyNNERuntimeDemo();

    UFUNCTION(BlueprintCallable, Category = "ML")
    void RunInference(const TArray<float>& InputData, TArray<float>& OutResult);

protected:
    virtual void BeginPlay() override;

private:
    UPROPERTY(EditAnywhere, Category = "ML")
    TObjectPtr<UObject> ModelAsset;  // 拖入 ONNX 模型资产

    // 内部状态
    TSharedPtr<INNERuntimeRDGModel> RDGModel;
};
```

### MyNNERuntimeDemo.cpp

```cpp
#include "MyNNERuntimeDemo.h"
#include "NNEModelData.h"

AMyNNERuntimeDemo::AMyNNERuntimeDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNNERuntimeDemo::BeginPlay()
{
    Super::BeginPlay();

    // NNE 运行时会在插件加载时自动注册
    // 通过 NNE 公共 API 获取 RDG 运行时并创建模型
    // 实际使用中需参考最新的 NNE 公共 API
}

void AMyNNERuntimeDemo::RunInference(const TArray<float>& InputData, TArray<float>& OutResult)
{
    // 通过 RDG 运行时在 GPU 上执行推理
    // 具体 API 请参考 NNE 插件的公共接口
}
```

## 模块依赖

该插件包含以下自定义依赖（非标准 Core/Engine/Slate 依赖）：

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎 API，NNERuntimeRDG 实现其运行时接口 |
| `MetalRHI` | Metal 渲染硬件接口，支持 macOS/iOS GPU 推理 |
| `VulkanRHI` | Vulkan 渲染硬件接口，支持跨平台 GPU 推理 |

此外，插件内部集成以下第三方库（作为 External 模块）：

| 第三方库 | 用途 |
|---|---|
| ONNX Runtime | ONNX 模型解析和优化（CPU/DML 后端） |
| ONNX | ONNX 格式定义 |
| Protobuf | ONNX 模型的序列化/反序列化 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度到单精度截断的编译警告 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正 32/64 位格式化字符串不匹配问题 |
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 重构 GPU 同步 API，合并为统一接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移至新的 UE_LOGF 格式 |
| 2026-01-07 | `57ff2f55` | Deprecate legacy GPU profiler related macros. | 废弃旧版 GPU 性能分析相关宏 |

### 维护评价

- **创建时间**：2023 年 6 月，约 3 年历史
- **最近更新**：2026 年 5 月，近 5 个月内有多次更新，保持活跃
- **更新性质**：近期更新主要是编译警告修复、API 重构（GPU 同步）和宏迁移，属于维护性更新，未见重大新功能
- **实验性状态**：仍标记为 `IsExperimentalVersion=true`，`EnabledByDefault=false`
- **推荐程度**：该插件作为 NNE 框架的核心 RDG 推理后端，处于持续维护中，但仍在实验阶段。适合探索和原型开发使用，**不建议在生产环境中依赖**。如需在生产项目中使用 ML 推理，建议关注 Epic 的后续正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NNERuntimeRDG)
- 官方文档（暂无）
- [父插件 NNE](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE)