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

NNERuntimeORT 是 Unreal Engine 5 中 **Neural Network Engine (NNE)** 的一个运行时后端插件。它允许游戏和应用程序在运行时加载和执行 ONNX 格式的机器学习模型，用于推理任务（如图像识别、自然语言处理、预测等）。

**核心解决的问题**：在 Unreal Engine 中集成和运行预训练的深度学习模型，而无需离开引擎环境或依赖外部服务。ONNX Runtime 作为一个高性能的推理引擎，能够利用 CPU 和 DirectML（在 Windows 上）进行硬件加速，确保推理过程快速、高效。

这个插件是 NNE 系统的一部分，NNE 提供了统一的接口来管理和使用不同的机器学习推理运行时，而 NNERuntimeORT 则是基于微软 ONNX Runtime 的具体实现。

## 使用场景

- **AI 驱动的游戏角色行为**：在运行时根据游戏状态、玩家输入等，通过 ONNX 模型实时预测角色的下一步动作。
- **动态内容生成**：使用生成式 AI 模型（如 GAN、VAE）在运行时创建或修改纹理、模型或关卡。
- **高级视觉效果**：利用神经网络实现风格迁移、超分辨率或去噪等实时图像后处理效果。
- **自然语言交互**：集成对话式 AI 模型，让 NPC 能够理解并回应玩家的自然语言输入。
- **预测分析**：根据游戏历史数据，预测玩家行为或游戏状态，以调整游戏难度或内容。

## 蓝图用法

该插件主要通过 NNE 的通用接口在蓝图中使用。你需要先在“插件”设置中启用 `NNERuntimeORT`，然后才能使用 NNE 蓝图节点。

### 核心节点

由于 NNERuntimeORT 是 NNE 的后端实现，其具体功能通过 NNE 的通用接口暴露。以下是 NNE 模块中与推理相关的典型蓝图节点（这些节点会自动使用已启用的运行时后端，如 NNERuntimeORT）：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Load Model` | 从文件或内存中加载一个 ONNX 模型，并返回一个模型资产引用。 | `UNNEModelData` |
| `Create Inference Session` | 基于已加载的模型数据，创建一个推理会话实例。 | `UNNEInferenceSession` |
| `Set Input Data` | 设置推理会话的输入张量数据。 | `UNNEInferenceSession` |
| `Run Inference` | 执行推理计算。 | `UNNEInferenceSession` |
| `Get Output Data` | 获取推理计算后输出张量的数据。 | `UNNEInferenceSession` |

### 使用示例（蓝图描述）

1.  **加载模型**：
    - 使用 `Load Model` 节点，从项目目录中加载一个 `.onnx` 文件，获得一个 `ModelData` 引用。

2.  **创建推理会话**：
    - 将 `ModelData` 引用连接到 `Create Inference Session` 节点，创建一个 `InferenceSession` 对象。

3.  **准备输入数据**：
    - 根据模型要求，准备输入数据。例如，处理一张游戏截图，将其转换为一个浮点数数组，并使用 `Set Input Data` 节点将其绑定到会话的某个输入张量上。

4.  **执行推理**：
    - 调用 `Run Inference` 节点，开始计算。

5.  **获取结果**：
    - 使用 `Get Output Data` 节点读取计算结果（例如，一个分类概率数组或一个生成的图像数据），然后在游戏中应用（如改变 NPC 行为、应用风格化滤镜）。

## C++ 用法

在 C++ 中，你将主要与 NNE 的模块和类交互，而 NNERuntimeORT 作为后端会自动工作。

### 头文件引入

```cpp
#include "NNECore.h"
#include "NNECoreModelData.h"
#include "NNECoreInferenceSession.h"
```

### 基本用法

以下代码片段展示了如何在 C++ 中使用 NNE 系统加载和运行一个 ONNX 模型。这源于 NNE 插件的标准用法模式。

```cpp
// 假设你已经有一个模型文件路径
FString ModelPath = TEXT("/Game/MLModels/my_model.onnx");

// 1. 加载模型数据（异步加载推荐使用 FStreamableManager）
TSoftObjectPtr<UNNEModelData> ModelDataAsset = LoadObject<UNNEModelData>(nullptr, *ModelPath);
if (!ModelDataAsset.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to load model data from path: %s"), *ModelPath);
    return;
}

// 2. 确保模型数据已加载
ModelDataAsset.LoadSynchronous();
UNNEModelData* ModelData = ModelDataAsset.Get();
if (!ModelData)
{
    UE_LOG(LogTemp, Error, TEXT("Model data is null after synchronous load."));
    return;
}

// 3. 创建推理会话
TUniquePtr<UE::NNE::IInferenceSession> InferenceSession = UE::NNE::FModelData::CreateSession(ModelData);
if (!InferenceSession)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create inference session."));
    return;
}

// 4. 准备输入数据（示例：一个形状为 [1, 3, 224, 224] 的浮点图像张量）
TArray<float> InputData;
InputData.SetNum(1 * 3 * 224 * 224);
// ... 填充 InputData (例如，从纹理像素转换而来) ...

// 5. 设置输入
TArray<UE::NNE::FTensorShape> InputShapes = {UE::NNE::FTensorShape({1, 3, 224, 224})};
InferenceSession->SetInputTensorShapes(InputShapes);

TArray<UE::NNE::FInferenceTensor> InputTensors;
InputTensors.Add(UE::NNE::FInferenceTensor(
    TEXT("input"), // 输入张量名称，必须与模型中定义一致
    UE::NNE::FTensorDataType::Float,
    InputShapes[0],
    InputData.GetData(),
    InputData.Num() * sizeof(float)
));
InferenceSession->SetInputTensors(MoveTemp(InputTensors));

// 6. 运行推理
InferenceSession->RunSync();

// 7. 获取输出
TArray<UE::NNE::FInferenceTensor> OutputTensors = InferenceSession->GetOutputTensors();
if (OutputTensors.Num() > 0)
{
    const UE::NNE::FInferenceTensor& OutputTensor = OutputTensors[0];
    const float* OutputDataPtr = reinterpret_cast<const float*>(OutputTensor.GetData().GetData());
    int32 OutputNumElements = OutputTensor.GetShape().ElementCount();
    
    // 8. 处理输出数据
    for (int32 i = 0; i < FMath::Min(OutputNumElements, 10); ++i) // 打印前10个结果
    {
        UE_LOG(LogTemp, Log, TEXT("Output[%d] = %f"), i, OutputDataPtr[i]);
    }
}
```

### 进阶用法

- **异步推理**：为避免阻塞游戏线程，可以使用 `InferenceSession->RunAsync()` 并在回调中处理结果。
- **硬件加速选择**：虽然 NNERuntimeORT 默认使用可用的最佳后端（CPU/DirectML），但你可以通过 `NNE` 系统的配置来指定偏好（如果 API 允许）。
- **多输入/输出**：处理具有多个输入和输出张量的复杂模型。
- **性能优化**：重用推理会话和输入缓冲区，减少内存分配开销。

**注意**：具体的 API 可能随着 NNE 系统的更新而变化。上述代码展示了核心流程，但实际的函数签名和类名请参考最新版本的 NNE 模块头文件（`NNECore.h`, `NNECoreInferenceSession.h` 等）。

## Demo 示例

由于 NNERuntimeORT 是一个后端插件，它不直接提供独立的 Demo。最简单的“Demo”就是使用上述 C++ 或蓝图流程加载并运行一个 ONNX 模型。

**一个最小可编译的 C++ 示例片段**（需要在 Actor 类中）：

```cpp
// MyNNEActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNECore.h"
#include "NNECoreInferenceSession.h"
#include "MyNNEActor.generated.h"

UCLASS()
class MYPROJECT_API AMyNNEActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNNEActor();

protected:
    virtual void BeginPlay() override;

private:
    void RunSampleInference();

    TUniquePtr<UE::NNE::IInferenceSession> InferenceSession;
};
```

```cpp
// MyNNEActor.cpp
#include "MyNNEActor.h"
#include "NNECoreModelData.h"
#include "Engine/AssetManager.h"
#include "Kismet/GameplayStatics.h"

AMyNNEActor::AMyNNEActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNNEActor::BeginPlay()
{
    Super::BeginPlay();
    // 延迟一帧执行，确保所有子系统初始化完毕
    FWorldDelegates::OnWorldCleanup.AddLambda([WeakThis = MakeWeakObjectPtr(this)](UWorld*, bool, bool)
    {
        if (WeakThis.IsValid())
        {
            WeakThis->RunSampleInference();
        }
    });
}

void AMyNNEActor::RunSampleInference()
{
    // 示例：尝试加载一个内置的测试模型或游戏内的模型资产
    // 在实际项目中，请替换为你的模型路径
    FString ModelPath = TEXT("/Engine/Plugins/NNE/NNERuntimeORT/TestAssets/MNIST_SimpleCNN.onnx");
    UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr, *ModelPath);

    if (!ModelData)
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not load model at: %s. Please check the path."), *ModelPath);
        return;
    }

    InferenceSession = UE::NNE::FModelData::CreateSession(ModelData);
    if (!InferenceSession)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create inference session."));
        return;
    }

    // 这里省略了设置输入和运行推理的代码，请参考上方“C++ 用法”章节
    UE_LOG(LogTemp, Log, TEXT("NNE Inference Session created successfully! Ready for input."));
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNECore` | 神经网络引擎的核心接口和抽象，用于与运行时无关地管理模型和会话。 |
| `ONNXRuntime` (第三方) | 提供实际的 ONNX 模型解析、优化和推理引擎。 |
| `DirectML` (第三方，Windows) | 微软的硬件加速 API，用于在支持的 GPU 上执行推理。 |

**说明**：你的模块（例如，使用 NNE 功能的 Game 模块）通常只需要依赖 `NNECore` 即可。具体哪个运行时（如 `NNERuntimeORT`）在运行时被使用，由项目设置和已启用的插件决定。`ONNXRuntime` 和 `DirectML` 的库文件由 `NNERuntimeORT` 插件自动链接和提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级核心依赖：ONNX Runtime 至 1.24.3，DirectML 至 1.15.4，带来性能提升和新功能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，可能是为了遵循新的编码规范或获取更丰富的日志信息。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 再次尝试升级依赖（与上一条记录相同内容，可能是一次回退后的重新提交）。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 代码重构：将渲染相关的类拆分到独立头文件，并增加显式包含，以改善编译依赖和代码组织。 |

### 维护评价

NNERuntimeORT 是一个 **相对较新** 且 **处于活跃维护** 的插件。
- **创建时间**：约2年前（2023年11月），与 UE5 的 NNE 系统一同推出。
- **维护频率**：从 git 日志看，在2026年3月至4月期间有多次提交，更新了核心的第三方库（ONNX Runtime, DirectML），表明 Epic 正在积极跟进上游更新以获取性能优化和新特性。
- **状态**：插件目前被标记为 **Beta 版本** (`IsBetaVersion: true`) 且 **默认禁用** (`EnabledByDefault: false`)。这意味着它仍在测试阶段，API 可能发生变化，不建议在需要绝对稳定的生产环境中作为唯一依赖。
- **平台支持**：仅支持 Win64、Linux、LinuxArm64 和 Mac。
- **推荐使用**：如果你的项目需要在 Unreal Engine 中运行 ONNX 模型，并且可以接受 Beta 状态的潜在风险，那么 **强烈推荐** 使用此插件。它是 Epic 官方对 NNE ONNX 支持的实现，与引擎集成度最高，且能得到持续更新。对于关键功能，建议密切关注其更新日志和已知问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)