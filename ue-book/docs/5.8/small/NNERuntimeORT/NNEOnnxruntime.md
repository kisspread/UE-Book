# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX推理运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 神经网络引擎（NNE）的 **ONNX Runtime 推理后端**。它将开源的 [ONNX Runtime](https://onnxruntime.ai/) 集成为 NNE 框架的运行时，使开发者能够在 UE5 中加载和执行 `.onnx` 格式的神经网络模型。

该插件解决的核心问题是：**在 Unreal Engine 中运行 ONNX 模型进行实时推理**。它封装了 ONNX Runtime 的 C/C++ API，提供两种执行提供者（Execution Provider）：

- **CPU EP**：在 CPU 上执行模型推理，所有平台均支持
- **DirectML EP**：在 Windows 上利用 GPU（通过 DirectML）加速推理，显著提升性能

典型的使用场景包括：风格迁移、图像分类、物体检测、超分辨率等需要在游戏运行时执行神经网络推理的任务。

> ⚠️ **注意**：该插件默认未启用（`EnabledByDefault: false`），且处于 Beta 状态。需要手动在项目设置中启用。

## 使用场景

- 你在做一个需要**实时风格迁移**的游戏 → 用 NNERuntimeORT 加载训练好的风格迁移 ONNX 模型
- 你需要在运行时进行**图像分类或物体检测** → 用 NNERuntimeORT 配合 CPU 或 DirectML 加速
- 你想在 Windows 上利用 **GPU 加速神经网络推理** → NNERuntimeORT 的 DirectML EP 可以直接调用显卡算力
- 你有一个 PyTorch/TensorFlow 训练的模型，需要导出为 ONNX 格式在 UE5 中使用 → NNERuntimeORT 是最直接的运行时选择

## 蓝图用法

NNERuntimeORT 本身作为 NNE 的运行时后端，不直接暴露蓝图节点。用户通过 **NNE 核心插件** 的蓝图 API 加载和运行模型，NNERuntimeORT 作为运行时后端自动被调度使用。开发者通常：

1. 将 `.onnx` 模型文件导入 UE5 项目
2. 通过 NNE 的 `UNNEModelData` 创建模型数据
3. 使用 NNE 的 `INNERuntime` 接口（NNERuntimeORT 实现了该接口）创建推理实例并执行

具体蓝图节点请参考 NNE 核心插件文档。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeCPU.h"
#include "NNERuntimeGPU.h"
```

### 基本用法

NNERuntimeORT 通过 NNE 框架的运行时注册机制工作。以下是基于 NNE 框架使用 ONNX Runtime 的典型流程：

```cpp
#include "NNE.h"
#include "NNECore.h"
#include "NNECoreTypes.h"

// 获取 NNE 运行时（NNERuntimeORT 会自动注册为可用运行时）
TArray<UNNEModelData*> ModelDataArray;
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeORT"));

// 加载 ONNX 模型数据
UNNEModelData* ModelData = UNNEModelData::Create(OnnxModelFile);
if (!ModelData)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model data"));
    return;
}

// 创建模型实例
TWeakInterfacePtr<INNERuntimeCPU> RuntimeCPU = Runtime.Get();
auto Model = RuntimeCPU->CreateModel(ModelData);
if (!Model.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model"));
    return;
}

// 创建模型实例（用于推理）
auto ModelInstance = Model->CreateModelInstance();
```

（来源：NNE 核心 API 设计模式）

### 进阶用法：DirectML 加速

在 Windows 上，可以显式选择 DirectML 后端进行 GPU 加速推理：

```cpp
// 获取 GPU 运行时（DirectML EP）
TWeakInterfacePtr<INNERuntime> GPURuntime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeORTGPU"));

// 使用 GPU 运行时创建模型实例
auto GPUModel = GPURuntime->CreateModel(ModelData);
auto GPUModelInstance = GPUModel->CreateModelInstance();

// 设置输入张量
TArray<float> InputData = { /* ... */ };
NNE::FTensorShape InputShape = NNE::FTensorShape::Make({1, 3, 224, 224});
FNNEInferenceContext Context;
Context.SetInputTensor(0, InputData.GetData(), InputShape);

// 执行推理
ModelInstance->RunSync(Context);

// 获取输出
float* OutputData = Context.GetOutputTensorData<float>(0);
```

（来源：NNERuntimeORT 的 CPU/DirectML 双 EP 架构设计）

## Demo 示例

以下示例展示如何在 UE5 中使用 NNERuntimeORT 加载并运行一个 ONNX 模型：

### MyModelInference.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "NNE.h"
#include "NNECoreTypes.h"

UCLASS()
class UMyModelInference : public UObject
{
    GENERATED_BODY()

public:
    void LoadModel(const FString& OnnxFilePath);
    void RunInference(const TArray<float>& Input, TArray<float>& Output);

private:
    TWeakInterfacePtr<INNERuntime> Runtime;
    TSharedPtr<NNE::IModel> Model;
    TSharedPtr<NNE::IModelInstance> ModelInstance;
};
```

### MyModelInference.cpp

```cpp
#include "MyModelInference.h"
#include "NNECore.h"
#include "Misc/FileHelper.h"

void UMyModelInference::LoadModel(const FString& OnnxFilePath)
{
    // 获取 ONNX Runtime 运行时
    Runtime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeORT"));
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("NNERuntimeORT runtime not available. Is the plugin enabled?"));
        return;
    }

    // 从文件加载模型字节
    TArray<uint8> ModelBytes;
    if (!FFileHelper::LoadFileToArray(ModelBytes, *OnnxFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load ONNX model: %s"), *OnnxFilePath);
        return;
    }

    // 创建模型数据
    UNNEModelData* ModelData = UNNEModelData::Create(ModelBytes);
    if (!ModelData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model data from bytes"));
        return;
    }

    // 创建模型
    Model = Runtime->CreateModel(ModelData);
    if (!Model.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model instance"));
        return;
    }

    // 创建推理实例
    ModelInstance = Model->CreateModelInstance();
    UE_LOG(LogTemp, Log, TEXT("ONNX model loaded successfully"));
}

void UMyModelInference::RunInference(const TArray<float>& Input, TArray<float>& Output)
{
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Model not loaded"));
        return;
    }

    // 设置输入并执行推理（具体 API 取决于 NNE 版本）
    // 推理完成后从输出张量中读取结果到 Output 数组
    UE_LOG(LogTemp, Log, TEXT("Inference completed"));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNECore` | NNE 核心框架，定义了运行时接口（`INNERuntime`）和推理类型 |
| `NNERuntimeCPU` | NNE CPU 运行时接口（`INNERuntimeCPU`） |
| `NNERuntimeGPU` | NNE GPU 运行时接口（`INNERuntimeGPU`），用于 DirectML 后端 |

> **Build.cs 依赖提示**：在你的模块 Build.cs 中添加：
> ```cpp
> PublicDependencyModuleNames.AddRange(new string[] { "NNECore", "NNERuntimeCPU" });
> // 如需 GPU 加速：
> PublicDependencyModuleNames.AddRange(new string[] { "NNERuntimeGPU" });
> ```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退之前的提交 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分 PooledRenderTarget 到独立头文件，添加显式包含 |

### 维护评价

- **活跃维护**：最近更新集中在 2026 年 3-4 月，ONNX Runtime 和 DirectML 库版本持续升级
- **核心依赖更新频繁**：ONNX Runtime 从初始版本升级到 1.24.3，DirectML 升级到 1.15.4，体现了 Epic 对该后端的持续投入
- **Beta 状态**：插件仍标记为 `IsBetaVersion: true`，API 可能在未来版本中发生变化
- **未默认启用**：`EnabledByDefault: false`，需要手动启用
- **平台支持**：Win64、Linux、LinuxArm64、Mac，覆盖面较广；DirectML GPU 加速仅限 Windows

**综合推荐**：该插件处于活跃维护状态，是 UE5 中运行 ONNX 模型的首选后端。虽然仍在 Beta 阶段，但已具备基本可用性。适合需要在 UE5 中进行神经网络推理的项目使用。建议关注版本更新时的 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)
- [NNE 核心插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNE)