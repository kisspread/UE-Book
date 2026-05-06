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

该插件为 Unreal Engine 的神经网络引擎（NNE）提供了一个基于 Apple CoreML 的运行时后端，允许在 macOS 设备上利用 CoreML 框架加速神经网络模型的推理计算。CoreML 是 Apple 提供的机器学习框架，针对 Apple Silicon（M 系列芯片）和 Intel Mac 进行了硬件优化。

编辑器模块（`NNERuntimeCoreMLEditor`）提供了 `.mlmodel` 格式模型的导入支持，使开发者能够直接在编辑器中导入 CoreML 模型文件并生成对应的模型资产。

## 使用场景

- 你需要在 macOS 平台（包括 Apple Silicon）上部署神经网络推理，且希望利用 CoreML 的硬件加速能力。
- 你已有一个 CoreML 格式（`.mlmodel`）的模型，希望直接导入到 UE 项目中使用。
- 你的项目使用了 NNE 框架，需要为 macOS 目标平台增加一个运行时后端（目前默认支持 CPU 的 NNE 运行时可能效率不足）。

注意：此插件为**实验性**，默认未启用，且仅支持 macOS（Editor 模块在 macOS 上工作，但运行时仅在 macOS 目标有效）。

## 蓝图用法

该插件的编辑器模块不提供直接的蓝图节点。运行时模块（`NNERuntimeCoreML`）是 NNE 的后端，通过 NNE 系统自动加载。在蓝图中，你只需要使用 NNE 的标准节点（如加载模型、运行推理）即可，无需关心具体运行时。

NNE 的蓝图节点通常位于 `NeuralNetwork` 类别下，具体用法请参考 [NNE 官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeCoreMLEditorModule.h"   // 编辑器模块，用于自定义导入
#include "NNERuntimeCoreMLModelData.h"      // 运行时模型数据类型（如果使用运行时）
```

### 基本用法：导入 CoreML 模型（编辑器）

`NNERuntimeCoreMLEditor` 模块注册了一个 `UNNERuntimeCoreMLModelDataFactory` 工厂类，允许通过 `Import` 对话框导入 `.mlmodel` 文件。使用方式如下：

1. 在内容浏览器中右键 → **Import to /Game/**。
2. 选择 `.mlmodel` 文件。
3. 引擎会自动调用工厂创建 `UNNERuntimeCoreMLModelData` 资产（该资产类定义在运行时模块 `NNERuntimeCoreML` 中）。

你也可以通过 C++ 代码手动触发导入：

```cpp
// 获取工厂实例
UNNERuntimeCoreMLModelDataFactory* Factory = NewObject<UNNERuntimeCoreMLModelDataFactory>();

// 准备导入参数（通常来自文件路径）
FString FilePath = TEXT("/Path/to/MyModel.mlmodel");
bool bSuccess = Factory->ImportObject(..., ...);
```

### 运行时使用模型（C++）

```cpp
// 创建一个 NNE 模型实例
UNNEModel* Model = NNE::CreateModelFromFile(TEXT("/Game/MyCoreMLModel"));

// 创建推理器
UNNEInference* Inference = NNE::CreateInference(Model);

// 设置输入数据（Tensor）
TArray<float> InputData = { ... };
NNE::FTensorBinding InputBinding;
InputBinding.Data = InputData.GetData();
InputBinding.Size = InputData.Num() * sizeof(float);

// 运行推理
Inference->Run(InputBinding, OutputBinding);
```

运行时模块 `NNERuntimeCoreML` 会自动选择 CoreML 作为后端（如果平台支持）。更详细的 NNE API 请参考官方文档。

## Demo 示例

以下是一个最小示例，演示如何在 C++ 中加载并使用 CoreML 模型进行推理（假设已导入模型资产 `MyModel`）。

```cpp
// MyMLInference.h
#pragma once
#include "CoreMinimal.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntime.h"

class FMyMLInference
{
public:
    void LoadAndRun();
};

// MyMLInference.cpp
#include "MyMLInference.h"
#include "NNEModel.h"
#include "NNEInference.h"
#include "NNERuntimeCoreML.h"  // 可选，用于显式指定运行时

void FMyMLInference::LoadAndRun()
{
    // 1. 从资产路径获取模型数据
    UNNEModelData* ModelData = Cast<UNNEModelData>(StaticLoadObject(UNNEModelData::StaticClass(), nullptr, TEXT("/Game/MyModel.MyModel")));
    if (!ModelData) return;

    // 2. 创建 NNE 模型（运行时自动匹配 CoreML 后端）
    UNNEModel* Model = NNE::CreateModel(ModelData);
    if (!Model) return;

    // 3. 创建推理器
    UNNEInference* Inference = NNE::CreateInference(Model);
    if (!Inference) return;

    // 4. 准备输入输出缓冲区
    TArray<float> InputData(10, 0.0f);
    TArray<float> OutputData(5, 0.0f);
    NNE::FTensorBinding InputBinding{ InputData.GetData(), InputData.Num() * sizeof(float) };
    NNE::FTensorBinding OutputBinding{ OutputData.GetData(), OutputData.Num() * sizeof(float) };

    // 5. 执行推理
    Inference->Run(InputBinding, OutputBinding);

    // 输出结果
    for (float Val : OutputData)
    {
        UE_LOG(LogTemp, Log, TEXT("Output: %f"), Val);
    }
}
```

项目依赖：确保 `NNERuntimeCoreML` 已在 `.Build.cs` 的 `PublicDependencyModuleNames` 中添加（见模块依赖章节）。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心模块，提供模型和推理接口 |
| `CoreML` | Apple 原生框架（平台 SDK），Build.cs 中通过 `PublicFrameworks` 引入 |

**编辑器模块额外依赖**：
| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器基础模块，工厂类由此派生 |
| `NNERuntimeCoreML` | 运行时模块，提供模型数据类型 |

**提示**：由于插件项目默认未启用，需要在 `项目名.uproject` 或插件管理界面中手动勾选启用 `NNERuntimeCoreML` 插件。

## 维护状态

### 近期更新

- 2025-04-08 `6c68dafe` — [NNE] CoreML runtime plugin registration improvement
- 2025-01-23 `4bda97f6` — [NNE] NNE internal cleanup step4 : operator attributes
- 2025-01-14 `2380da6f` — [NNE] CoreML runtime: add support for float16/double/int32 for MultyArray input/ouput
- 2025-01-13 `8336b86e` — [NNE] Add GPU and NPU interface to CoreML runtime V2
- 2025-01-08 `be668fcf` — [NNE] Add a CoreML based runtime on mac.

### 维护评价

该插件创建于 2025 年 1 月，属于非常新的实验性插件。近期（2025 年 4 月）仍有功能性更新，开发活跃度较高。已知限制：

- 仅支持 macOS 平台，且需要 macOS 11+ 和 Apple Silicon 或 Intel Mac。
- 实验性阶段，API 可能变动，不建议用于生产项目。
- 导入功能仅支持 `.mlmodel` 格式，不支持更新的 `.mlpackage` 格式。

综合评价：适合尝鲜或原型验证，但在稳定性、错误处理和文档方面尚不完善。若需生产级使用，建议等待正式版或考虑其他运行时（如 ONNX Runtime）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML)
- [官方文档（NNE 入门课程）](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [UE 官方论坛讨论](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeCoreML/Tests)（如有）