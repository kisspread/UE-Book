# NNERuntimeRDG

> A runtime implementing the Neural Network Engine (NNE) API, using the Render Dependency Graph (RDG).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络RDG运行时 |
| 分类 | ML |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `NNEHlslShaders` (Runtime), `NNERuntimeRDG` (Runtime), `NNERuntimeRDGData` (Runtime), `NNERuntimeRDGUtils` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-05-29 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG) | |

## 用途

NNERuntimeRDG 是 UE5 神经网络引擎（NNE）的一个运行时后端实现，专门利用**渲染依赖图（RDG）**来加速神经网络推理计算。它通过将神经网络算子（如卷积、全连接、归一化、激活函数等）转化为 GPU 可执行的计算着色器（HLSL），在 RDG 框架下高效调度，从而获得接近原生 GPU 的推理性能。

该插件解决的核心问题：在 UE5 中提供一套高性能、可扩展的神经网络推理方案，使游戏和实时应用能够利用 GPU 执行 AI 模型（如 Onnx 模型），而无需引入外部深度学习框架。相比纯 CPU 实现，NNERuntimeRDG 能够显著加速大规模张量运算，尤其适合卷积、矩阵乘等并行密集计算。

## 使用场景

- 你需要在游戏或实时应用中集成**预训练神经网络模型**（如 Onnx 格式），并且希望利用 GPU 获得实时推理性能。
- 你正在开发**基于 AI 的 NPC 行为、物理模拟、超分辨率、风格迁移、音频处理**等功能，需要离线或在线执行模型推理。
- 你希望将推理过程无缝集成到 UE 的渲染管线中，与 RDG 渲染任务协同调度。

## 蓝图用法

本插件主要面向 C++ 开发，不直接暴露蓝图可调用节点。神经网络模型的加载、创建和推理流程需通过 C++ 编程完成。但你可以将推理结果暴露为蓝图可访问的属性或函数（例如通过自定义蓝图节点或派生自 UObject 的封装类）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| 无（本模块未提供 BlueprintCallable 方法） | – | – |

## C++ 用法

### 头文件引入

```cpp
#include "NNERuntimeRDG.h"          // NNERuntimeRDG 运行时核心
#include "NNE.h"                    // NNE 公共 API
#include "NNEModelData.h"           // 模型数据加载
#include "NNERuntimeRDGUtils.h"     // 工具函数（可选）
```

### 基本用法

以下示例展示如何加载一个 Onnx 模型并使用 NNERuntimeRDG 后端创建模型实例，然后执行一次推理。

```cpp
// 1. 加载模型数据（假设模型位于 Content/Models/MyModel.onnx）
UNNEModelData* ModelData = NewObject<UNNEModelData>();
ModelData->LoadFromFile(FPaths::ProjectContentDir() / TEXT("Models/MyModel.onnx"));

// 2. 获取 NNERuntimeRDG 运行时
UNNEModelInstance* ModelInstance = nullptr;
UNNERuntimeRDG* Runtime = FModuleManager::GetModulePtr<UNNERuntimeRDG>("NNERuntimeRDG");
if (Runtime && ModelData)
{
    ModelInstance = Runtime->CreateModelInstance(ModelData);
}

if (!ModelInstance)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to create model instance with NNERuntimeRDG"));
    return;
}

// 3. 设置输入张量（假设模型输入为 1x3x224x224 浮点）
TArray<float> InputData(1 * 3 * 224 * 224, 0.0f);
// 填充实际数据（例如从纹理采样或预处理得到）

TArray<float> OutputData;
ModelInstance->Run(InputData, OutputData);

// 4. 处理输出结果
// OutputData 中存储模型输出张量数据
```

> 实际用法需参考 NNE 官方文档，本示例仅为简化示意。模型输入/输出的具体形状和数量需从模型元数据获取。

### 进阶用法

#### 多输入/多输出推理

使用 `NNE::FModelInstance` 直接操作输入/输出缓冲区：

```cpp
#include "NNE.h"

using namespace UE::NNE;

// 创建模型实例
TUniquePtr<IModelInstance> ModelInstance = Runtime->CreateModelInstance(ModelData);

// 准备输入/输出张量信息
TArray<FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
TArray<FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();

// 分配缓冲区
TArray<TArray<float>> InputBuffers;
TArray<TArray<float>> OutputBuffers;
for (const auto& Desc : InputDescs)
{
    uint32 TotalSize = Desc.GetShape().Volume() * Desc.GetElementSize();
    InputBuffers.Emplace(TotalSize / sizeof(float), 0.0f);
}
for (const auto& Desc : OutputDescs)
{
    uint32 TotalSize = Desc.GetShape().Volume() * Desc.GetElementSize();
    OutputBuffers.Emplace(TotalSize / sizeof(float), 0.0f);
}

// 执行推理
bool bSuccess = ModelInstance->RunSync(
    InputDescs,
    InputBuffers,
    OutputDescs,
    OutputBuffers
);
```

#### 自定义算子注册

如果你需要扩展 NNERuntimeRDG 支持自定义算子，可以通过 `FOperatorRegistryHlsl` 注册：

```cpp
#include "NNERuntimeRDGHlslOp.h"
#include "MyCustomOp.h"

bool RegisterMyCustomOp(FOperatorRegistryHlsl& Registry)
{
    Registry.RegisterOperator(TEXT("MyCustom"), []() -> TUniquePtr<IOperatorHlsl>
    {
        return MakeUnique<FMyCustomOp>();
    });
    return true;
}
```

然后在模块启动时调用注册函数（例如在 `StartupModule` 中）。

> 注意：自定义算子需要提供对应 HLSL 着色器实现，并遵循 RDG 调度规则。

## Demo 示例

一个完整的、可编译的最小示例，演示如何使用 NNERuntimeRDG 加载并运行模型。

**MyNNETest.h**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "MyNNETest.generated.h"

UCLASS(Blueprintable)
class UMyNNETest : public UObject
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "NNE Test")
    void RunInference(const FString& ModelPath);
};
```

**MyNNETest.cpp**

```cpp
#include "MyNNETest.h"
#include "NNERuntimeRDG.h"
#include "NNE.h"
#include "NNEModelData.h"
#include "NNERuntimeRDGModule.h"

void UMyNNETest::RunInference(const FString& ModelPath)
{
    // 加载模型
    UNNEModelData* ModelData = NewObject<UNNEModelData>();
    ModelData->LoadFromFile(ModelPath);
    if (!ModelData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load model: %s"), *ModelPath);
        return;
    }

    // 获取运行时
    UNNERuntimeRDG* Runtime = FModuleManager::GetModulePtr<UNNERuntimeRDG>("NNERuntimeRDG");
    if (!Runtime)
    {
        UE_LOG(LogTemp, Error, TEXT("NNERuntimeRDG module not available"));
        return;
    }

    // 创建模型实例
    TUniquePtr<UE::NNE::IModelInstance> ModelInstance = Runtime->CreateModelInstance(ModelData);
    if (!ModelInstance)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create model instance"));
        return;
    }

    // 获取输入形状并分配数据（此处简化：假设单输入单输出，float 类型）
    TArray<UE::NNE::FTensorDesc> InputDescs = ModelInstance->GetInputTensorDescs();
    if (InputDescs.Num() == 0) return;

    int32 InputSize = InputDescs[0].GetShape().Volume();
    TArray<float> InputData;
    InputData.SetNumZeroed(InputSize); // 用零填充（实际应填充有效数据）

    // 执行同步推理
    TArray<UE::NNE::FTensorDesc> OutputDescs = ModelInstance->GetOutputTensorDescs();
    int32 OutputSize = OutputDescs.Num() > 0 ? OutputDescs[0].GetShape().Volume() : 0;
    TArray<float> OutputData;
    OutputData.SetNumZeroed(OutputSize);

    bool bSuccess = ModelInstance->RunSync(
        InputDescs,
        { MakeArrayView(InputData) },
        OutputDescs,
        { MakeArrayView(OutputData) }
    );

    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Inference succeeded, output[0] = %f"), OutputData[0]);
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Inference failed"));
    }
}
```

## 模块依赖

要用本插件，你的模块需在 `Build.cs` 的 `PublicDependencyModuleNames` 和 `PrivateDependencyModuleNames` 中添加以下依赖（省略常见依赖）：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎公共 API，提供数据类型、接口定义 |
| `NNERuntimeRDGUtils` | 工具函数和辅助方法 |
| `RHI` | 渲染硬件接口，用于 GPU 资源管理 |
| `RenderCore` | RDG 和渲染管线支持 |

> 注意：`MetalRHI`、`VulkanRHI` 等平台 RHI 模块仅在对应平台需要，通常由引擎自动处理，无需手动添加。

## 维护状态

### 近期更新

- 2025-07-24 `2412ec9f` 使 TArrayView 和 Invoke 成为 constexpr；修复 UB GetData 并弃用 TStaticArray 的对齐
- 2025-06-12 `9ce28ae0` 更新数值限制为使用 std 库替代宏，以解决新版 Windows SDK 编译失败问题
- 2025-06-12 `d9dba260` [NNE] NNERuntimeRDGHlsl arm64 支持
- 2025-06-03 `d31855b9` 修复 libprotobuf-lite 构建脚本并添加 Windows arm64 版本
- 2025-05-29 `8cfef610` 添加 Greater.h 包含到使用 TGreater 的文件中

### 维护评价

- 创建于 2025 年 5 月，距今不到 3 个月，属于非常新的插件。
- 更新频率高（几乎每月多次），且包含功能性更新（arm64 支持）和平台适配（Windows arm64）。
- 作为实验性插件，开发活跃，暂无废弃或停滞迹象。
- 目前仅支持 HLSL 着色器路径，对于非 GPU 推理（如 CPU fallback）需使用其他运行时。
- **推荐使用**：如果你的项目需要在 UE5 中运行 GPU 加速的神经网络推理，且可以接受实验性 API 的可能变动，此插件提供了高效的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG)
- [NNE 官方文档（UE5）](https://docs.unrealengine.com/5.7/en-US/neural-network-engine-in-unreal-engine/)
- [测试用例（NNERuntimeRDG）](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/NNERuntimeRDG/Source/NNERuntimeRDG/Private/Tests)（需确认路径是否存在）