# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX运行时后端 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 Unreal Engine **神经网络引擎 (NNE)** 的 ONNX Runtime 后端实现。它为 NNE 提供了一个基于 [ONNX Runtime](https://onnxruntime.ai/) 的推理执行器，支持加载和运行 `.onnx` 格式的神经网络模型。

该插件解决了以下核心问题：
- **ONNX 模型推理**：让 UE5 能够加载和执行 ONNX 格式的神经网络模型（如风格迁移、目标检测等）
- **硬件加速**：通过 CPU（支持 Arena 内存分配优化）和 DirectML（Windows 上的 GPU 加速）两种执行提供程序，利用不同硬件进行加速推理
- **NNE 运行时抽象**：作为 NNE 框架的可插拔后端，通过 `INNERuntime` 接口与 NNE 核心系统解耦

插件使用 **延迟加载** 的方式动态加载 ONNX Runtime 动态库（DLL），避免在编辑器启动时产生不必要的加载开销。

> ⚠️ 该插件当前为 **Beta 版本**（`IsBetaVersion=true`），且默认不启用（`EnabledByDefault=false`），需要在项目设置中手动启用。

## 使用场景

- **风格迁移/图像处理**：使用预训练的风格迁移模型（如神经风格迁移），在游戏运行时实时处理图像
- **游戏内 AI 推理**：加载自训练的 ONNX 模型，在游戏逻辑中执行推理（如 NPC 行为预测、图像分类）
- **程序化内容生成**：利用生成式神经网络模型进行纹理生成、地形生成等
- **语音/音频处理**：加载语音识别或音频分类模型进行实时音频分析
- **需要 GPU 加速的推理**：在 Windows 上利用 DirectML 实现 GPU 加速推理，无需依赖特定 GPU 厂商的 SDK

## 蓝图用法

该插件不直接暴露 Blueprint API。NNERuntimeORT 作为 NNE 的底层运行时后端，通过 NNE 插件的核心接口间接使用。实际的模型加载和推理操作通过 NNE 主插件的 `UNNEModelData`、`INNERuntime` 等接口进行。

如需在蓝图中使用神经网络推理，请参考 NNE 主插件的文档。

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeORT.h"
#include "NNEModelData.h"
```

### 基本用法：获取运行时实例并执行推理

```cpp
// 获取 NNERuntimeORT 运行时实例
TArray<INNERuntime*> Runtimes = UE::NNE::GetAllRegisteredRuntimes();
INNERuntime* ORTRuntime = nullptr;
for (INNERuntime* Runtime : Runtimes)
{
    if (Runtime && Runtime->GetName() == TEXT("NNERuntimeORT"))
    {
        ORTRuntime = Runtime;
        break;
    }
}

// 创建模型数据（通常从资产加载）
TObjectPtr<UNNEModelData> ModelData = NewObject<UNNEModelData>();
// 从文件加载 .onnx 模型字节...
TArray<uint8> ModelBytes = LoadONNXFile("path/to/model.onnx");
ModelData->SetModelData(MakeShared<TArray<uint8>>(ModelBytes));

// 创建推理模型
TWeakInterfacePtr<INNERuntimeCPU> CPURuntime = Cast<INNERuntimeCPU>(ORTRuntime);
TSharedPtr<UE::NNE::IModelCPU> Model = CPURuntime->CreateModel(ModelData);
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Model->CreateModelInstance();

// 设置输入张量形状和数据
TConstArrayView<int32> InputTensorShape = {1, 3, 224, 224};
TArray<float> InputData(InputTensorShape[0] * InputTensorShape[1] * InputTensorShape[2] * InputTensorShape[3]);
// 填充 InputData ...

// 创建输入输出张量绑定
UE::NNE::FTensorShape InputShape = UE::NNE::FTensorShape::Make(InputTensorShape);
TArray<UE::NNE::FTensorBindingCPU> InputBindings = {{InputData.GetData(), InputData.Num() * sizeof(float)}};
TArray<UE::NNE::FTensorBindingCPU> OutputBindings = {{OutputData.GetData(), OutputData.Num() * sizeof(float)}};

// 执行推理
ModelInstance->RunSync(InputBindings, OutputBindings);
```

### 进阶用法：自定义执行提供程序（DirectML）

```cpp
// NNERuntimeORT 在 Windows 上自动支持 DirectML
// 通过 FNNERuntimeORTModule 动态加载 ONNX Runtime DLL 并注册执行提供程序

// ONNX Runtime 的函数指针在 FNNERuntimeORTDllHandler 中加载：
UE::NNEOnnxruntime::FNNERuntimeORTDllHandler DllHandler;

// 内部会调用：
// - OrtSessionOptionsAppendExecutionProvider_CPU：CPU 推理
// - OrtSessionOptionsAppendExecutionProvider_DML：DirectML GPU 推理（仅 Windows）

// 要使用 GPU 推理，需要通过 NNE 运行时的配置机制指定使用 DirectML 后端
```

## Demo 示例

以下是一个最小可编译的自定义推理示例，展示如何使用 NNERuntimeORT 加载 ONNX 模型并执行推理：

```cpp
// MyNeuralNetworkRunner.h
#pragma once

#include "CoreMinimal.h"
#include "NNE.h"
#include "NNERuntimeCPU.h"

class FMyNeuralNetworkRunner
{
public:
    bool Init(const TArray<uint8>& ModelBytes);
    TArray<float> RunInference(const TArray<float>& InputData);

private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
    TArray<int32> InputShape;
    TArray<int32> OutputShape;
};
```

```cpp
// MyNeuralNetworkRunner.cpp
#include "MyNeuralNetworkRunner.h"
#include "NNEModelData.h"
#include "NNECore.h"

bool FMyNeuralNetworkRunner::Init(const TArray<uint8>& ModelBytes)
{
    // 1. 获取 NNE 运行时
    UE::NNE::FRuntimeAndModelInfo RuntimeInfo = UE::NNE::GetRuntimeInfo(TEXT("NNERuntimeORT"));
    if (!RuntimeInfo.Runtime)
    {
        UE_LOG(LogTemp, Error, TEXT("NNERuntimeORT runtime not found"));
        return false;
    }

    // 2. 创建模型数据
    TObjectPtr<UNNEModelData> ModelData = NewObject<UNNEModelData>();
    TSharedPtr<TArray<uint8>> Data = MakeShared<TArray<uint8>>(ModelBytes);
    ModelData->SetModelData(Data);

    // 3. 创建模型
    Model = RuntimeInfo.Runtime->CreateModelCPU(ModelData);
    if (!Model.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model"));
        return false;
    }

    // 4. 创建模型实例
    ModelInstance = Model->CreateModelInstanceCPU();
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model instance"));
        return false;
    }

    // 5. 获取输入输出形状
    TConstArrayView<UE::NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
    TConstArrayView<UE::NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();

    if (InputDescs.Num() > 0)
    {
        InputShape = InputDescs[0].GetShape().GetData();
    }
    if (OutputDescs.Num() > 0)
    {
        OutputShape = OutputDescs[0].GetShape().GetData();
    }

    return true;
}

TArray<float> FMyNeuralNetworkRunner::RunInference(const TArray<float>& InputData)
{
    TArray<float> OutputData;
    OutputData.SetNumUninitialized(
        Algo::Accumulate(OutputShape, 1, [](int32 A, int32 B) { return A * B; }));

    // 绑定输入输出
    TArray<UE::NNE::FTensorBindingCPU> InputBindings = {
        {const_cast<float*>(InputData.GetData()), InputData.Num() * sizeof(float)}
    };
    TArray<UE::NNE::FTensorBindingCPU> OutputBindings = {
        {OutputData.GetData(), OutputData.Num() * sizeof(float)}
    };

    // 设置输入形状
    ModelInstance->SetInputTensorShapes(
        {UE::NNE::FTensorShape::Make(InputShape)});

    // 执行同步推理
    if (ModelInstance->RunSync(InputBindings, OutputBindings) != UE::NNE::ERunSyncStatus::Ok)
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed"));
        return {};
    }

    return OutputData;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | NNE 核心框架，提供运行时接口和模型数据抽象 |
| `NNECore` | NNE 核心类型定义（张量、运行时接口等） |

> 无其他特殊依赖。ONNX Runtime 库（`NNEOnnxruntime` 模块）作为第三方库打包在插件内部，通过 `NNEOnnxruntime.build.cs` 管理，用户无需额外链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏从 UE_LOG 到 UE_LOGF |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退之前的某次提交 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit include | 拆分渲染目标相关头文件，添加显式包含 |

### 维护评价

- **创建时间**：2023 年 11 月，至今约 2 年
- **更新频率**：近 6 个月内有多次实质性更新，主要是 ONNX Runtime 和 DirectML 版本升级
- **维护状态**：**活跃维护中** — Epic Games 持续跟进上游 ONNX Runtime 的版本更新，并进行必要的代码适配
- **已知限制**：
  - 当前为 Beta 版本，API 可能发生变化
  - 默认未启用，需要手动在插件设置中开启
  - DirectML 加速仅支持 Windows 平台
  - 仅支持 Win64、Linux、LinuxArm64、Mac 平台
- **推荐**：✅ 推荐在需要 ONNX 模型推理的项目中使用，这是 UE5 中运行 ONNX 模型的官方推荐方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)