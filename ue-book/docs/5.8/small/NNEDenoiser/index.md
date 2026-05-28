# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有着色器代码 |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 插件为 Unreal Engine 的路径追踪器 (Path Tracer) 提供基于神经网络的实时降噪功能。它用一个预训练的神经网络模型取代了传统的时域降噪算法，能够在极低采样率（例如每像素1个样本）下生成高质量、接近收敛的图像。其核心价值在于**用 AI 推理换取渲染速度**，特别适用于对渲染质量要求高、但又需要交互式或近实时预览的场景，如建筑可视化、产品渲染和电影级虚拟制片。

## 使用场景

- **你正在进行建筑可视化项目**，需要快速迭代光照和材质，同时保持最终渲染质量 → 使用 NNEDenoiser 让路径追踪器在 viewport 中提供实时反馈。
- **你正在制作产品宣传动画**，希望缩短渲染时间而不损失图像细节 → 在最终渲染序列中启用 NNEDenoiser，以更低的采样率实现同等效果。
- **你的项目包含复杂的全局光照和反射**，传统降噪器容易产生模糊或鬼影 → 使用神经网络降噪器来更好地保留高频细节。

## 蓝图用法

本插件主要集成在渲染管线内部，**没有直接暴露给蓝图的自定义节点**。降噪功能通常通过引擎的 `Path Tracer` 后处理设置来启用和配置。

## C++ 用法

### 核心模块与类

插件主要由两个模块构成，共同完成神经网络降噪的集成。

**`NNEDenoiser` 模块 (Runtime)**
负责降噪模型的生命周期管理、输入输出缓冲区的准备以及与 NNE 引擎的交互。
- `UNNEDenoiserSubsystem`: 游戏子系统，负责管理降噪模型实例的加载、缓存和请求。
- `FNNE`: 提供静态方法，用于从 NNE 资产创建或获取一个可运行的模型。

**`NNEDenoiserShaders` 模块 (Runtime)**
包含将神经网络推理结果合成到最终渲染画面所需的计算着色器。
- `FNNEShaders`: 提供渲染命令封装，用于调度降噪相关的 GPU 计算。

### 基本用法 (启用降噪)

降噪通常通过引擎的渲染设置自动生效。以下代码展示了如何通过渲染设置启用它：

```cpp
#include "RenderCore/Public/PathTracingDenoiser.h"

// 获取当前世界设置并启用路径追踪降噪
UWorld* World = ...;
URendererSettings* RendererSettings = GetMutableDefault<URendererSettings>();
RendererSettings->PathTracingDenoiser = EPathTracingDenoiserType::NNE; // 选择NNE作为降噪器
```

### 进阶用法 (直接管理降噪模型)

如果需要更精细的控制（如自定义降噪流程或进行研究），可以直接与 `UNNEDenoiserSubsystem` 交互：

```cpp
#include "NNEDenoiserSubsystem.h"
#include "NNE.h"

// 1. 获取降噪器子系统
UNNEDenoiserSubsystem* DenoiserSubsystem = World->GetSubsystem<UNNEDenoiserSubsystem>();

// 2. 请求一个模型（内部会处理加载和缓存）
TObjectPtr<UNNEModelData> ModelData = ...; // 从资产获取的模型数据
TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance = DenoiserSubsystem->GetModelInstance(ModelData);

// 3. 准备输入（例如，一个低采样的渲染帧缓冲）
TArray<float> InputBuffer = ...; // 格式通常为 NCHW
UE::NNE::FTensor InputTensor = UE::NNE::FTensor::Create({1, 3, Height, Width}, MakeArrayView(InputBuffer));

// 4. 执行推理
TArray<float> OutputBuffer;
UE::NNE::FTensor OutputTensor = UE::NNE::FTensor::Create({1, 3, Height, Width}, MakeArrayView(OutputBuffer));
ModelInstance->RunSync(TArray<UE::NNE::FTensor>{InputTensor}, TArray<UE::NNE::FTensor>{OutputTensor});
// OutputBuffer 现在包含降噪后的图像数据
```

## Demo 示例

一个最小化的、直接使用 NNE 引擎进行推理的示例（非完整渲染集成，用于展示核心调用流程）：

**NNEInferenceDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NNE.h"
#include "NNEInferenceDemo.generated.h"

UCLASS()
class UNNEInferenceDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    void RunBasicInference();
private:
    TSharedPtr<UE::NNE::IModelInstanceCPU> ModelInstance;
};
```

**NNEInferenceDemo.cpp**
```cpp
#include "NNEInferenceDemo.h"
#include "NNEUtilsTensor.h"
#include "NNEDenoiserSubsystem.h"

void UNNEInferenceDemoSubsystem::RunBasicInference()
{
    // 此示例假定你已有一个有效的 UNNEModelData (ModelDataAsset)
    UNNEModelData* ModelDataAsset = LoadObject<UNNEModelData>(nullptr, TEXT("/Game/MyDenoiserModel"));

    // 通过引擎通用的 NNE 接口创建模型实例
    TWeakInterfacePtr<INNERuntime> Runtime = UE::NNE::GetRuntime<INNERuntime>();
    if (!Runtime.IsValid()) return;

    TSharedPtr<UE::NNE::IModelCPU> Model = Runtime->CreateModelCPU(ModelDataAsset);
    ModelInstance = Model->CreateModelInstanceCPU();

    // 准备输入输出张量
    constexpr int32 Width = 256, Height = 256;
    TArray<float> InputData, OutputData;
    InputData.SetNumZeroed(1 * 3 * Height * Width);
    OutputData.SetNumZeroed(1 * 3 * Height * Width);

    TArray<UE::NNE::FTensor> Inputs, Outputs;
    Inputs.Add(UE::NNE::FTensor::Create({1, 3, Height, Width}, MakeArrayView(InputData)));
    Outputs.Add(UE::NNE::FTensor::Create({1, 3, Height, Width}, MakeArrayView(OutputData)));

    // 运行同步推理
    ModelInstance->RunSync(Inputs, Outputs);
    // 处理 OutputData ...
}
```

## 模块依赖

你的项目模块如果要使用本插件的功能（如直接调用降噪模型），需要在 `.Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心，提供模型加载、运行时接口 (`INNERuntime`)。 |
| `NeuralNetworkInference` | 提供具体的推理执行器和张量操作。 |
| `RenderCore` | 渲染核心，提供路径追踪、渲染目标等基础设施。 |
| `Renderer` | 高级渲染器，包含路径追踪器和降噪器集成点。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 简化GPU同步逻辑，替换过时的等待命令。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新的 UE_LOGF 格式。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have... | 补充头文件包含，修复编译依赖问题。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 重构头文件结构，将池化渲染目标分离，改善编译。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次失败的代码批量替换。 |

### 维护评价

**积极维护中的前沿功能**。

- **创建时间短**：插件于2024年8月从 Experimental 文件夹移出并升级为 Beta，历史不足两年。
- **更新活跃且专注**：近期提交（2026年2月至4月）主要集中在**渲染代码重构、编译依赖清理和GPU同步优化**上，表明开发团队正在积极优化其稳定性和与引擎核心渲染代码的集成，而非添加大量新功能。
- **Beta 状态**：`.uplugin` 中明确标记为 `IsBetaVersion: true`，说明其 API 和行为可能在未来版本中发生变化。
- **功能依赖**：插件严重依赖特定的 NNE 运行时 (`NNERuntimeORT`) 和 GPU 架构，使用时需注意平台兼容性（当前支持 Win64, Linux, Mac）。

**结论**：这是一个**推荐关注并试用**的先进功能插件。它代表了引擎在实时渲染 AI 加速方面的重要进展。尽管处于 Beta 状态，但近期持续的维护和重构表明它正在走向成熟。建议在开发或测试分支中使用，并留意后续版本更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [NNEDenoiser 模块文档](NNEDenoiser.md)
- [NNEDenoiserShaders 模块文档](NNEDenoiserShaders.md)