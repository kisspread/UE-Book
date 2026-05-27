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

该插件为 Unreal Engine 的神经网络引擎 (NNE) 框架提供了一个基于 ONNX Runtime 的推理后端。它使开发者能够将使用 ONNX 格式训练好的模型加载到引擎中，并利用 **CPU** 和 **DirectML** 硬件加速器在 Windows、Linux 和 Mac 平台上运行实时机器学习推理。这解决了在游戏和实时应用中部署机器学习模型的性能问题。

## 使用场景

-   你需要在游戏运行时执行实时的图像处理任务，例如实时风格迁移或图像增强。
-   你希望将训练好的计算机视觉模型（如对象检测、分类）部署到游戏或编辑器工具中，用于资源审核、自动化内容生成等。
-   你需要一个跨平台（Win64, Linux, Mac）的高性能推理方案，不想依赖特定硬件厂商的 SDK。
-   你在开发需要在 CPU 或支持 DirectML 的 GPU 上运行 ONNX 模型的工具或应用。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Runtime` | 创建一个 NNERuntimeORT 运行时实例，用于后续加载和执行 ONNX 模型。 | `UNNERuntimeORTSettings` |
| `Create Model Instance` | 使用已创建的运行时实例，从 ONNX 模型数据创建一个可用于推理的模型实例。 | `UNNERuntimeORTModel` |
| `Run` | 在已创建的模型实例上执行一次推理。 | `UNNERuntimeORTModel` |

### 使用示例（蓝图描述）

1.  使用 `Create Runtime` 节点获取一个运行时对象（通常只需在初始化时调用一次）。
2.  使用 `Create Model Instance` 节点，将一个 `UONNXModel` 资产或原始模型数据（`TArray<uint8>`）加载为一个 `UNNERuntimeORTModel` 对象。
3.  准备输入数据（例如，一个 `TArray<float>` 代表图像数据）和输出缓冲区。
4.  调用 `Run` 节点，将输入数据传入，并接收处理后的输出结果。

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeORT.h"
#include "NNE.h"
```

### 基本用法

创建一个运行时并执行一次推理。 (来源：推测自模块公开API和设计模式)
```cpp
// 1. 获取 NNE 运行时
UNNEModelData* ModelData = ...; // 从资产或文件加载
TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeORT"));
if (!Runtime.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to get NNERuntimeORT runtime"));
    return;
}

// 2. 创建模型实例
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = Runtime->CreateModelCPU(ModelData);
if (!ModelInstance.IsValid())
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance"));
    return;
}

// 3. 准备输入和输出张量
TArray<float> InputData = { /* ... */ };
TConstArrayView<float> InputView = MakeConstArrayView(InputData);
UE::NNE::FTensorShape InputShape = /* ... 根据模型定义 ... */;

TArray<float> OutputData;
OutputData.SetNumUninitialized(/* ... 输出维度大小 ... */);
TArrayView<float> OutputView = MakeArrayView(OutputData);
UE::NNE::FTensorShape OutputShape = /* ... 根据模型定义 ... */;

// 4. 运行推理
UE::NNE::ERunSyncStatus Status = ModelInstance->RunSync(
    { { InputView, InputShape } }, // 输入张量
    { { OutputView, OutputShape } } // 输出张量
);
if (Status == UE::NNE::ERunSyncStatus::Ok)
{
    // 处理 OutputData
}
```

### 进阶用法

使用 DirectML 后端（需要特定硬件和驱动支持）进行推理。运行时会根据当前平台和配置自动选择最优的执行提供程序。
```cpp
// DirectML 加速的运行时和推理流程与上述 CPU 流程类似。
// 主要区别在于：
// 1. 使用的 Runtime 类型可能不同（取决于内部实现），但 API 接口 (`INNERuntime`, `IModelInstance`) 保持一致。
// 2. 性能会显著提升（在支持的硬件上）。
// 3. 需要确保系统安装了最新的 DirectX 12 兼容驱动。
// 模型和数据的准备方式与 CPU 路径完全相同。
```

## Demo 示例

一个加载 ONNX 模型并在 CPU 上运行推理的最小示例。
**NNERuntimeORTDemo.h**
```cpp
// NNERuntimeORTDemo.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NNERuntimeORTDemo.generated.h"

class UNNEModelData;

UCLASS()
class ANNERuntimeORTDemo : public AActor
{
    GENERATED_BODY()

public:
    ANNERuntimeORTDemo();

protected:
    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "NNE Demo")
    TObjectPtr<UNNEModelData> ModelDataAsset;

    TWeakInterfacePtr<INNERuntime> Runtime;
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;

private:
    void RunInference();
};
```
**NNERuntimeORTDemo.cpp**
```cpp
// NNERuntimeORTDemo.cpp
#include "NNERuntimeORTDemo.h"
#include "NNERuntimeORT.h"
#include "NNE.h"

ANNERuntimeORTDemo::ANNERuntimeORTDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ANNERuntimeORTDemo::BeginPlay()
{
    Super::BeginPlay();

    // 获取 ORT 运行时
    Runtime = UE::NNE::GetRuntime<INNERuntime>(TEXT("NNERuntimeORT"));
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("NNERuntimeORT not available!"));
        return;
    }

    // 检查资产是否有效
    if (!ModelDataAsset)
    {
        UE_LOG(LogTemp, Error, TEXT("Model Data Asset is null!"));
        return;
    }

    // 创建模型实例
    ModelInstance = Runtime->CreateModelCPU(ModelDataAsset);
    if (!ModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model instance from asset!"));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("NNE RuntimeORT model loaded successfully!"));
    RunInference();
}

void ANNERuntimeORTDemo::RunInference()
{
    if (!ModelInstance.IsValid())
    {
        return;
    }

    // 假设模型输入为 1 个浮点数，输出也为 1 个浮点数
    TArray<float> Input = { 1.0f };
    TArray<float> Output;
    Output.SetNumUninitialized(1);

    UE::NNE::FTensorShape Shape;
    Shape.Data = { 1 }; // 形状: [1]

    UE::NNE::ERunSyncStatus Status = ModelInstance->RunSync(
        { { MakeConstArrayView(Input), Shape } },
        { { MakeArrayView(Output), Shape } }
    );

    if (Status == UE::NNE::ERunSyncStatus::Ok)
    {
        UE_LOG(LogTemp, Log, TEXT("Inference output: %f"), Output[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed!"));
    }
}
```

## 模块依赖

要使用此插件，你的模块 Build.cs 需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 访问 ORT 运行时和模型实例的创建接口 |
| `NNE` | 访问 NNE 框架的核心接口 (`INNERuntime`, `IModelInstance`) |
| `RenderCore` | 处理渲染相关的数据结构（可能用于图像输入） |
| `RHI` | 渲染硬件接口（DirectML 执行依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-21 | `d9fee063` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 升级了 ONNX Runtime 至 1.24.3 版本，DirectML 至 1.15.4 版本，带来性能改进和新特性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的 `UE_LOG` 宏迁移到新的 `UE_LOGF` 宏，属于代码现代化更新。 |
| 2026-03-30 | `33f008b5` | [Backout] - CL52245530. | 回滚了之前的某次提交 (CL52245530)，可能是因为引入了问题。 |
| 2026-03-30 | `c8c79a38` | [NNE] NNERuntimeORT ONNX Runtime upgrade to version 1.24.3 and DirectML upgrade to version 1.15.4. | 与后续提交内容相同，但被回滚，表明升级过程遇到问题并已修复。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 重构了代码，将 `PooledRenderTarget` 和 `SceneRenderingAllocator` 拆分到独立头文件，改善代码组织和编译依赖。 |

### 维护评价

该插件处于**活跃维护**状态。虽然仍标记为 Beta (IsBetaVersion=true)，但最近一次更新（ONNX Runtime 升级）发生在一个月内，且涉及核心依赖库的重大版本更新，表明 Epic Games 团队正在持续改进和集成最新技术。近期的提交历史显示它是一个**积极开发中**的模块，不断进行依赖升级和代码现代化。**推荐在需要高性能 ONNX 模型推理的新项目中探索和使用**，但请注意其 Beta 状态意味着 API 和行为可能发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)
- [官方文档](https://dev.epicgames.com/community/learning/courses/e7w/unreal-engine-neural-network-engine-nne)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT/Tests)