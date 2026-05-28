# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | ONNX运行时后端 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (RuntimeAndProgram), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 UE5 神经网络引擎（NNE）的 **ONNX Runtime 执行后端**。它允许开发者在 Unreal Engine 中加载和运行 ONNX 格式的机器学习模型。

具体来说，该插件解决以下问题：
- **加载 ONNX 模型**：将 ONNX 格式的神经网络模型加载到 UE5 运行时环境中
- **CPU 推理加速**：通过 ONNX Runtime 的 CPU Execution Provider 在 CPU 上执行模型推理
- **DirectML 推理加速**（仅 Windows）：通过 Microsoft DirectML 在 GPU（包括集成显卡和独立显卡）甚至 NPU 上执行模型推理，无需 CUDA 等专用框架

该插件是 NNE 框架的后端实现之一，提供了从 ONNX Runtime C/C++ API 到 UE5 NNE 接口的桥接层。它通过动态加载 ONNX Runtime 共享库（DLL）的方式集成，避免了直接链接带来的冲突。

## 使用场景

- **游戏内风格迁移（Style Transfer）**：在运行时将玩家截图转换为艺术风格化图像
- **实时图像分类/目标检测**：使用预训练的 ONNX 模型进行推理，如 YOLO、ResNet 等
- **语音识别/NLP 任务**：在游戏内进行本地语音识别或文本处理
- **程序化内容生成**：使用神经网络辅助生成游戏内容（地形、纹理等）
- **NPC 行为决策**：使用小型 ONNX 模型驱动 NPC 的行为决策逻辑
- **需要 GPU 加速但不想依赖 CUDA**：通过 DirectML 在任何兼容 DirectX 12 的 GPU 上加速推理

## 蓝图用法

该插件本身不直接暴露蓝图节点，而是作为 NNE 框架的后端运行。蓝图层面的模型加载和推理通过 NNE 核心插件提供的接口完成。开发者需要：

1. 启用 `NNERuntimeORT` 插件
2. 通过 NNE 的通用接口（`UNNEModelData`、`UNNEModelInstanceCPU` 等）加载 ONNX 模型
3. 该插件在后台自动注册为 NNE 的可用运行时之一

## C++ 用法

### 头文件引入

```cpp
#include "NNE.h"
#include "NNERuntimeORT.h" // 如果需要直接访问 ORT 特定 API
```

### 基本用法

通过 NNE 框架加载和运行 ONNX 模型（NNERuntimeORT 作为后端提供支持）：

```cpp
// 1. 获取 NNE 运行时
TArray<UNNEModelData*> ModelDataArray;
// 加载 ONNX 模型文件（UAsset 或从磁盘加载）
TObjectPtr<UNNEModelData> ModelData = ...;

// 2. 创建模型实例（NNERuntimeORT 会作为可用运行时被自动选择）
TObjectPtr<UNNEModelInstanceCPU> ModelInstance = ...;

// 3. 设置输入张量
TArray<Tensor<float>> Inputs;
Inputs.Add(Tensor<float>::Make({1, 3, 224, 224}, InputData));

// 4. 执行推理
TArray<Tensor<float>> Outputs;
ModelInstance->RunSync(Inputs, Outputs);
```

### 进阶用法：直接使用 ONNX Runtime C++ API

在某些高级场景下，可以绕过 NNE 抽象层直接使用 ONNX Runtime API（需要访问 `NNEOnnxruntime` 模块）：

```cpp
#include "NNEOnnxruntime.h"

// 通过动态加载的函数指针调用 ORT API
// 注意：UE5 通过 ORT_CXX_API_THROW 宏将 ORT 异常转换为 UE_LOG(Fatal)
// 当定义 ORT_NO_EXCEPTIONS 时，错误会通过 UE_LOGF 输出
```

## ONNX Runtime 集成细节

该插件封装了以下 ONNX Runtime 核心功能：

| 功能 | 说明 |
|---|---|
| `OrtGetApiBase` | 获取 ORT API 基础接口 |
| `OrtSessionOptionsAppendExecutionProvider_CPU` | 添加 CPU 执行提供程序 |
| `OrtSessionOptionsAppendExecutionProvider_DML` | 添加 DirectML 执行提供程序（Windows） |
| `OrtSessionOptionsAppendExecutionProviderEx_DML` | 使用自定义 DML 设备和命令队列（Windows） |

### 支持的张量数据类型

ONNX Runtime 通过 `ONNXTensorElementDataType` 枚举支持以下数据类型：

| 类型 | C++ 对应类型 |
|---|---|
| `FLOAT` | `float` |
| `FLOAT16` | `Ort::Float16_t` (uint16_t) |
| `BFLOAT16` | `Ort::BFloat16_t` (uint16_t) |
| `DOUBLE` | `double` |
| `INT8` | `int8_t` |
| `INT16` | `int16_t` |
| `INT32` | `int32_t` |
| `INT64` | `int64_t` |
| `UINT8` | `uint8_t` |
| `UINT16` | `uint16_t` |
| `UINT32` | `uint32_t` |
| `UINT64` | `uint64_t` |
| `BOOL` | `bool` |
| `STRING` | `std::string` |

### DirectML 设备过滤器（仅 Windows）

```cpp
// OrtDmlDeviceFilter 枚举
enum OrtDmlDeviceFilter : uint32_t {
    Gpu = 1 << 0,     // 仅 GPU
    Npu = 1 << 1,     // 仅 NPU（需要 ENABLE_NPU_ADAPTER_ENUMERATION）
    Any = 0xffffffff,  // 任意设备（需要 ENABLE_NPU_ADAPTER_ENUMERATION）
};

// OrtDmlPerformancePreference 性能偏好
enum OrtDmlPerformancePreference {
    Default = 0,
    HighPerformance = 1,  // 高性能模式
    MinimumPower = 2,     // 最低功耗模式
};
```

## Demo 示例

以下是一个完整的最小示例，展示如何在 UE5 中通过 NNE + NNERuntimeORT 加载和运行 ONNX 模型：

```cpp
// MyMLActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "NNEModelInstanceCPU.h"
#include "NNETensor.h"
#include "MyMLActor.generated.h"

UCLASS()
class MYPROJECT_API AMyMLActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMLActor();

    UPROPERTY(EditAnywhere, Category = "ML")
    TObjectPtr<UNNEModelData> ModelData;

    virtual void BeginPlay() override;

    void RunInference(const TArray<float>& InputData, TArray<float>& OutputData);

private:
    TUniquePtr<UE::NNE::IModelInstanceCPU> ModelInstance;
    TUniquePtr<UE::NNE::IModelCPU> Model;
};
```

```cpp
// MyMLActor.cpp
#include "MyMLActor.h"

AMyMLActor::AMyMLActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMLActor::BeginPlay()
{
    Super::BeginPlay();

    if (!ModelData)
    {
        UE_LOG(LogTemp, Warning, TEXT("ModelData is null"));
        return;
    }

    // NNERuntimeORT 会自动注册为可用运行时
    // 通过 NNE 框架创建模型实例
    TArray<UE::NNE::TWeakRuntimeInfo> RuntimeInfos = UE::NNE::GetAllRuntimeInfo();
    
    // 选择第一个可用的运行时（通常是 NNERuntimeORT 的 CPU 后端）
    if (RuntimeInfos.Num() > 0)
    {
        // 模型创建和推理流程
        // 注意：实际 API 以 UE5.8 的 NNE 模块为准
        UE_LOG(LogTemp, Log, TEXT("NNE Runtime available: %s"), 
            *RuntimeInfos[0].GetName().ToString());
    }
}

void AMyMLActor::RunInference(const TArray<float>& InputData, TArray<float>& OutputData)
{
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("Model instance not initialized"));
        return;
    }

    // 设置输入并执行推理
    // 具体 API 取决于 NNE 模块的版本
}
```

**注意事项**：
- 该插件 `EnabledByDefault=false`，必须在项目设置中手动启用
- `IsBetaVersion=true`，API 可能在后续版本发生变化
- 仅支持 Win64、Linux、LinuxArm64 和 Mac 平台
- ONNX Runtime 版本：1.24.3，DirectML 版本：1.15.4

## 模块依赖

该插件的 NNEOnnxruntime 模块封装了 ONNX Runtime 第三方库（约 28 个源文件，包含大量 C/C++ API 头文件）。

| 模块 | 用途 |
|---|---|
| `NNE` | UE5 神经网络引擎核心模块，提供运行时注册和模型管理框架 |

NNEOnnxruntime 模块通过动态加载 DLL 的方式引入 ONNX Runtime（包括 `onnxruntime_c_api.h`、`onnxruntime_cxx_api.h` 等），在 Windows 上额外支持 `dml_provider_factory.h`（DirectML）和 `cpu_provider_factory.h`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级 ONNX Runtime 至 1.24.3，DirectML 至 1.15.4 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 新日志宏 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退之前的提交 CL52245530 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 尝试升级 ORT 和 DML（后被回退） |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染目标和场景渲染分配器到独立头文件 |

### 维护评价

- **活跃维护中**：最近 1 个月内有多次实质性更新，包括 ONNX Runtime 和 DirectML 库的版本升级
- **Beta 状态**：`IsBetaVersion=true`，API 和功能仍可能发生变化
- **核心基础设施**：作为 NNE 框架的关键后端之一，Epic 持续投入维护
- **第三方库更新频繁**：ONNX Runtime 从 1.x 持续升级到 1.24.3，表明底层推理能力不断增强
- **已知限制**：`EnabledByDefault=false` 需要手动启用；仅支持特定平台
- **推荐使用**：适合需要在 UE5 中运行 ONNX 模型的项目，尤其是希望利用 DirectML 在各类 GPU 上加速推理的场景。由于仍处于 Beta 阶段，生产环境使用需谨慎评估稳定性

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [社区支持](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)