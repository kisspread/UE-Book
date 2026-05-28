# NNERuntimeORT

> ONNX Runtime backed runtime for the Neural Network Engine (NNE), accelerated by the CPU and DirectML execution providers.

| 属性 | 值 |
|---|---|
| 中文名 | NNE运行时-ONNX |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNERuntimeORT` (Runtime), `NNEOnnxruntime` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2023-11-07 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT) | |

## 用途

NNERuntimeORT 是 **NNE (Neural Network Engine)** 的一个 **运行时插件**。它解决了如何在虚幻引擎中**实际加载并运行 ONNX 格式神经网络模型**的问题。NNE 本身提供了一个抽象的神经网络推理接口，而 NNERuntimeORT 是该接口的具体实现之一，它利用强大的开源机器学习框架 **ONNX Runtime** 作为后端。

其核心价值在于为 UE 提供了一种**跨平台（Windows, Linux, macOS）** 且**高效**的模型推理能力，特别适合在游戏或实时应用中集成 AI 功能（如图像处理、风格迁移、决策制定等）。

## 使用场景

- **游戏内 AI 推理**：在游戏运行时使用训练好的 ONNX 模型进行实时预测，例如角色行为决策、程序化内容生成、动态难度调整。
- **计算机视觉应用**：在引擎内实现图像分类、目标检测、风格迁移（如将游戏画面转为特定艺术风格）等。
- **数据驱动动画**：使用机器学习模型来驱动或混合角色动画。
- **工具开发**：为编辑器工具开发智能化的功能，例如资产自动标记、布局优化建议。
- **跨平台部署**：当你的 AI 模型需要同时在 PC (Win64/Linux/Mac) 上运行时，此插件提供了一致的运行时支持。

> ⚠️ 注意：该插件当前为 **Beta** 状态，主要用于实验和开发目的，不建议在最终商业产品中直接使用，除非你明确了解其风险。

## 蓝图用法

作为运行时插件，其核心功能主要通过 NNE 提供的通用接口在蓝图中暴露。以下是关键的功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Runtime` | 根据指定的运行时类型（如 `ONNXRuntimeCPU`, `ONNXRuntimeDirectML`）创建一个神经网络推理运行时实例。 | `UNNERuntime` (通过工厂) |
| `Load Model` | 从字节数组或资产中加载一个 ONNX 模型。 | `UNNEModelData` |
| `Create Model Instance` | 使用加载的模型数据和运行时，创建一个可执行的模型实例。 | `UNNEModelInstance` |
| `Run Inference` | 对模型实例执行一次推理，输入数据张量并获取输出数据张量。 | `UNNEModelInstance` |

### 使用示例（蓝图描述）

1. **初始化**：在“BeginPlay”事件中，使用 `Create Runtime` 节点，选择 `NNERuntimeORT` 作为运行时名称，并指定 `ONNXRuntimeCPU` 或 `ONNXRuntimeDirectML` 作为执行提供程序。
2. **加载模型**：使用一个“Load Model”节点，从你的 `.uasset` 文件或内存中的字节流加载 ONNX 模型，得到 `UNNEModelData`。
3. **创建实例**：将上一步得到的 `ModelData` 和第一步创建的 `Runtime` 输入到“Create Model Instance”节点，得到可执行的 `UNNEModelInstance`。
4. **推理循环**：在需要推理时（如 Tick 事件），准备好输入数据（通常是包含浮点数的数组，需转换为 `FNNE Tensor`），调用“Run Inference”节点，然后从输出张量中解析结果。

## C++ 用法

以下示例展示了如何在 C++ 中使用 NNERuntimeORT 进行基本的模型推理。

### 头文件引入

```cpp
// 核心 NNE 接口
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntime.h"
#include "NNERuntimeCPU.h" // 如果使用 CPU 运行时
// NNERuntimeORT 特定的运行时类型（通常在 `UNNERuntimeCPU` 中封装，无需直接引用）
// #include "NNERuntimeORT.h" // 可能无需直接包含
```

### 基本用法

以下代码演示了创建运行时、加载模型并运行推理的完整流程。 (概念性示例，细节需参考实际API)

```cpp
// 1. 获取运行时
TObjectPtr<UNNERuntimeCPU> Runtime = UNNERuntimeCPU::GetRuntime(); // 获取 CPU 运行时
// 或者通过 NNE 子系统按名称获取
// UNNERuntime* Runtime = UNNEModule::Get()->GetRuntime(“NNERuntimeORT”);

// 2. 加载模型数据 (假设已加载为字节数组 ModelDataArray)
TObjectPtr<UNNEModelData> ModelData = NewObject<UNNEModelData>();
ModelData->SetData(ModelDataArray);

// 3. 创建模型实例
TObjectPtr<UNNEModelInstance> ModelInstance = Runtime->CreateModelInstance(ModelData);
if (!ModelInstance) { /* 错误处理 */ }

// 4. 准备输入张量
TArray<float> InputData = { /* ... */ };
FNNE Tensor InputTensor;
InputTensor.SetDataFloat(MakeArrayView(InputData));

// 5. 运行推理
TArray<FNNE Tensor> Outputs;
if (ModelInstance->RunSync({InputTensor}, Outputs))
{
    // 6. 处理输出张量 Outputs[0]
    TArrayView<const float> OutputView = Outputs[0].GetDataFloat();
    // 使用输出数据...
}
```

## Demo 示例

这是一个最小的 C++ 示例，演示如何使用 `NNERuntimeORT` 插件在 CPU 上加载并运行一个简单的 ONNX 模型。

**MyNeuralNetworkActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNEModelData.h"
#include "NNERuntimeCPU.h"
#include "MyNeuralNetworkActor.generated.h"

UCLASS()
class AMyNeuralNetworkActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNeuralNetworkActor();

    virtual void BeginPlay() override;

private:
    UPROPERTY()
    TObjectPtr<UNNERuntimeCPU> Runtime;

    UPROPERTY()
    TObjectPtr<UNNEModelData> ModelData;

    UPROPERTY()
    TObjectPtr<UNNEModelInstance> ModelInstance;

    UPROPERTY(EditAnywhere, Category="AI")
    UTexture2D* InputTexture; // 用作示例输入的纹理

    void RunInference();
};
```

**MyNeuralNetworkActor.cpp**
```cpp
#include "MyNeuralNetworkActor.h"
#include "Engine/Texture2D.h"

AMyNeuralNetworkActor::AMyNeuralNetworkActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNeuralNetworkActor::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 CPU 运行时 (NNERuntimeORT 插件提供了此实现)
    Runtime = UNNERuntimeCPU::GetRuntime();
    if (!Runtime) return;

    // 2. 加载模型 (这里假设你有一个名为 `MyModel.uasset` 的 ONNX 模型资产)
    // 实际项目中，这通常通过资产加载异步完成。
    // 这里我们用一个简单的假设：ModelData 已被加载。
    // ModelData = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/MyModel"));

    // 3. 创建模型实例
    if (ModelData)
    {
        ModelInstance = Runtime->CreateModelInstance(ModelData);
        if (ModelInstance)
        {
            UE_LOG(LogTemp, Log, TEXT("Model instance created successfully."));
            // 4. (可选) 在这里或某个事件中触发推理
            // RunInference();
        }
    }
}

void AMyNeuralNetworkActor::RunInference()
{
    if (!ModelInstance || !InputTexture) return;

    // 5. 准备输入数据 (简化示例：将纹理像素转为浮点数组)
    // 注意：真实的模型输入预处理（归一化、缩放、通道顺序）至关重要，必须与训练时一致。
    TArray<float> InputPixelData;
    FTexture2DMipMap& Mip = InputTexture->GetPlatformData()->Mips[0];
    void* TextureData = Mip.BulkData.Lock(LOCK_READ_WRITE);
    // ... 将 TextureData 转换为 InputPixelData (这里省略具体实现)
    Mip.BulkData.Unlock();

    // 6. 创建输入张量
    FNNE Tensor InputTensor;
    InputTensor.SetDataFloat(MakeArrayView(InputPixelData));

    // 7. 运行推理
    TArray<FNNE Tensor> Outputs;
    if (ModelInstance->RunSync({InputTensor}, Outputs))
    {
        UE_LOG(LogTemp, Log, TEXT("Inference completed. Output size: %d"), Outputs[0].GetDataFloat().Num());
        // 8. 处理输出结果
        // ...
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed."));
    }
}
```

## 模块依赖

要使用 `NNERuntimeORT` 插件，你的模块需要依赖 `NNE` 插件模块。

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎的核心接口层，必须依赖。 |
| `ONNXRuntime` | (隐式) `NNERuntimeORT` 依赖 `Onnxruntime` 第三方库，无需手动添加，已由插件处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级了核心依赖 ONNX Runtime 到 1.24.3，DirectML 到 1.15.4，提升性能和兼容性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到 UE_LOGF，符合新的日志系统规范。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530 | 回退了一次提交，说明此次升级过程可能遇到了问题并已修复。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 同样的升级操作，可能是上一次尝试的最终完成。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 代码重构，将部分渲染相关的类拆分到独立头文件，优化编译依赖。 |

### 维护评价

- **创建时间**：约 3 年前创建（2023年底）。
- **更新频率**：近期（2026年3-4月）有密集的更新，主要围绕**底层库升级（ONNX Runtime、DirectML）** 和**代码维护（日志、编译依赖）**，表明插件仍在**活跃维护**中。
- **状态**：插件标记为 `Beta` 且 `EnabledByDefault=false`，说明它仍是**实验性功能**，但 Epic 正在持续投入。
- **建议**：**推荐用于实验和原型开发**。对于生产环境，建议等待其脱离 Beta 阶段或密切关注其稳定性更新。其依赖的核心库（ONNX Runtime）非常成熟，增加了该插件的可靠性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [支持论坛](https://forums.unrealengine.com/t/course-neural-network-engine-nne/1162628)