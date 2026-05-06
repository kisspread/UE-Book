# NNERuntimeCoreML

> CoreML backed runtime for the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | CoreML 神经网络运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeCoreML` (RuntimeAndProgram), `NNERuntimeCoreMLEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-01-08 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML) | |

## 用途

NNERuntimeCoreML 是 Unreal Engine 神经网络引擎（NNE）的一个运行时插件，专门为 Apple 平台提供硬件加速推理能力。它封装了 Apple 的 CoreML 框架，允许在 macOS（以及可能的 iOS/iPadOS）设备上利用 CPU、GPU 和 NPU（神经网络处理器）高效执行 ONNX 模型。

该插件解决了 NNE 在 Apple 生态下的性能瓶颈，让开发者无需手动管理不同硬件的调度，即可获得 Apple Silicon 芯片的端侧推理加速。通过实现 `INNERuntimeCPU`、`INNERuntimeGPU` 和 `INNERuntimeNPU` 接口，它能够自动适配可用硬件资源，提供统一的运行时体验。

## 使用场景

- 你在 macOS 上开发使用 NNE 的 AI 功能（如物体检测、图像分类、语音识别），需要利用 Apple 原生 CoreML 加速。
- 你的游戏或应用需要在 Mac 上离线运行神经网络模型，且要求低延迟、低功耗。
- 你希望自动在 CPU / GPU / NPU 之间切换，无需手动选择运行时插件。

## 蓝图用法

此插件不直接暴露任何蓝图可调用节点。所有运行时操作均通过 NNE 系统（`UNNEModelData`、`UNNEModelInstance` 等）间接完成。启用该插件后，NNE 自动识别并优先使用 CoreML 运行时。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeCoreML.h"
#include "NNETypes.h"
#include "NNEModelData.h"
```

### 基本用法

以下示例展示如何通过 NNE 系统加载一个 CoreML 模型并执行推理（假设已在项目设置中启用 CoreML 运行时）。

```cpp
// 1. 加载模型数据（通常来自 .onnx 或 .mlmodel 文件）
UNNEModelData* ModelData = NewObject<UNNEModelData>();
// 假设已经通过 LoadModelFromFile 填充数据（具体实现依赖 NNE 工具）

// 2. 获取 CoreML 运行时对象（自动注册，可通过全局查询）
UNNERuntimeCoreMLCpuGpuNpu* CoreMLRuntime = Cast<UNNERuntimeCoreMLCpuGpuNpu>(
    GEngine->GetEngineSubsystem<UNNESubsystem>()->GetRuntimeByName(TEXT("NNERuntimeCoreML"))
);

// 3. 创建模型
TSharedPtr<UE::NNE::IModelCPU> Model = CoreMLRuntime->CreateModelCPU(ModelData);

// 4. 创建实例
TSharedPtr<UE::NNE::IModelInstanceCPU> Instance = Model->CreateModelInstanceCPU();

// 5. 设置输入张量形状（假设模型输入为 1x3x224x224）
TArray<UE::NNE::FTensorShape> InputShapes;
InputShapes.Add(UE::NNE::FTensorShape::MakeFromSymbolic({1, 3, 224, 224}));
Instance->SetInputTensorShapes(InputShapes);

// 6. 准备输入/输出缓冲区
TArray<UE::NNE::FTensorBindingCPU> InputBindings, OutputBindings;
// ... 填充 InputBindings[0] 和 OutputBindings[0] 的 Data 和 Size

// 7. 同步推理
Instance->RunSync(InputBindings, OutputBindings);
```

### 进阶用法

- **GPU / NPU 选择**：运行时提供了 `UNNERuntimeCoreMLCpuGpuNpu`，可通过 `CreateModelGPU()` 或 `CreateModelNPU()` 创建对应硬件的模型。如果设备不支持 NPU，`CanCreateModelNPU()` 将返回 `Fail`，此时应降级到 CPU 或 GPU。
- **多实例并发**：`CreateModelInstanceCPU()` 返回的实例是线程安全的，可在多线程中并行执行推理。
- **模型标识**：`GetModelDataIdentifier()` 返回唯一标识，可用于缓存或调试。

## Demo 示例

以下是一个完整的最小 C++ 示例（无需 Build.cs 修改，依赖已在模块依赖中说明）。

**`MyNNERunner.h`**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "NNEModelData.h"
#include "NNETypes.h"
#include "NNERuntimeCoreML.h"

class FMyNNERunner
{
public:
    bool LoadModel(const FString& ModelFilePath);
    bool RunInference(TArray<float>& InputData, TArray<float>& OutputData);
    
private:
    TSharedPtr<UE::NNE::IModelCPU> Model;
    TSharedPtr<UE::NNE::IModelInstanceCPU> Instance;
    TArray<UE::NNE::FTensorDesc> InputDescs, OutputDescs;
};
```

**`MyNNERunner.cpp`**
```cpp
#include "MyNNERunner.h"
#include "NNESubsystem.h"
#include "Engine/Engine.h"

bool FMyNNERunner::LoadModel(const FString& ModelFilePath)
{
    // 实际应用中，你应该使用 UNNEModelData::LoadFromFile 加载 ONNX/CoreML 模型
    // 此处仅演示获取运行时
    UNNESubsystem* NNESub = GEngine->GetEngineSubsystem<UNNESubsystem>();
    if (!NNESub) return false;

    UNNERuntimeCoreMLCpuGpuNpu* Runtime = Cast<UNNERuntimeCoreMLCpuGpuNpu>(
        NNESub->GetRuntimeByName(TEXT("NNERuntimeCoreML")));
    if (!Runtime) return false;

    // 创建临时 ModelData（生产代码应使用真实数据）
    UNNEModelData* ModelData = NewObject<UNNEModelData>();
    // 假设 ModelData 已正确初始化

    if (Runtime->CanCreateModelCPU(ModelData) != ECanCreateModelCPUStatus::Ok) return false;
    Model = Runtime->CreateModelCPU(ModelData);
    if (!Model.IsValid()) return false;

    Instance = Model->CreateModelInstanceCPU();
    if (!Instance.IsValid()) return false;

    // 获取输入/输出描述
    InputDescs = Instance->GetInputTensorDescs();
    OutputDescs = Instance->GetOutputTensorDescs();
    return true;
}

bool FMyNNERunner::RunInference(TArray<float>& InputData, TArray<float>& OutputData)
{
    // 设置输入形状（假设输入形状已知）
    TArray<UE::NNE::FTensorShape> Shapes;
    Shapes.Add(UE::NNE::FTensorShape::MakeFromSymbolic({1, 3, 224, 224}));
    Instance->SetInputTensorShapes(Shapes);

    // 准备绑定
    UE::NNE::FTensorBindingCPU InputBinding;
    InputBinding.Data = InputData.GetData();
    InputBinding.Size = InputData.Num() * sizeof(float);

    UE::NNE::FTensorBindingCPU OutputBinding;
    OutputData.SetNumUninitialized(1000); // 假设输出 1000 个 float
    OutputBinding.Data = OutputData.GetData();
    OutputBinding.Size = OutputData.Num() * sizeof(float);

    TArray<UE::NNE::FTensorBindingCPU> InputBindings = { InputBinding };
    TArray<UE::NNE::FTensorBindingCPU> OutputBindings = { OutputBinding };

    auto Status = Instance->RunSync(InputBindings, OutputBindings);
    return Status == UE::NNE::IModelInstanceCPU::ERunSyncStatus::Ok;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNECore` | NNE 运行时核心接口与类型定义 |
| `CoreML`（系统框架） | Apple CoreML 框架（仅 Apple 平台可用） |

无其他特殊依赖（标准 Engine/CoreUObject 等已省略）。

## 维护状态

### 近期更新

- 2025-04-08 `6c68dafe` [NNE] CoreML runtime plugin registration improvement
- 2025-01-23 `4bda97f6` [NNE] NNE internal cleanup step4 : operator attributes
- 2025-01-14 `2380da6f` [NNE] CoreML runtime: add support for float16/double/int32 for MultyArray input/ouput
- 2025-01-13 `8336b86e` [NNE] Add GPU and NPU interface to CoreML runtime V2
- 2025-01-08 `be668fcf` [NNE] Add a CoreML based runtime on mac.

### 维护评价

此插件创建于 2025 年 1 月，非常新，仍在积极开发中。近期提交包括注册优化、数据类型支持和 GPU/NPU 接口扩展，表明功能持续完善。目前为实验性状态（`IsExperimentalVersion=true`），不建议在生产环境中使用，但适合评估与测试。预计将在后续版本中稳定化。对于需要在 macOS 上利用 CoreML 加速 NNE 推理的开发者，此插件是首选方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML)
- [官方教程：Neural Network Engine (NNE)](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [Unreal 论坛讨论](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)