# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 神经去噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（计算着色器） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

此插件解决了 Unreal Engine **路径追踪器（Path Tracer）** 在渲染过程中产生大量噪点的问题。路径追踪通过模拟光线物理行为实现高质量渲染，但需要大量样本（SPP）才能获得干净结果，这导致渲染非常缓慢。

NNEDenoiser 的核心作用是将 **神经网络推理** 与 **GPU 计算着色器** 结合，对路径追踪器的低样本（噪点）输出进行实时或近实时的去噪处理。它不仅仅是简单的降噪滤波，而是一个完整的图像处理管线，包括：
1.  **输入预处理**：将路径追踪器输出的 RGB 颜色、反照率（Albedo）、法线（Normal）等数据，通过特定的转移函数（Transfer Function）转换为适合神经网络处理的格式。
2.  **自动曝光计算**：通过分桶（Binning）和归约（Reduce）算法在 GPU 上高效计算场景平均亮度，用于自适应缩放输入数据。
3.  **通道映射复制**：高效地在 GPU 纹理和缓冲区（NNE 张量）之间映射并复制数据，支持灵活的通道重排。
4.  **神经网络推理**：调用 NNE（Neural Network Engine）运行时，执行用户提供的预训练神经网络模型。
5.  **输出后处理**：将神经网络输出的张量数据转换回标准的渲染输出格式（如 HDR 颜色）。

本质上，它为路径追踪器提供了一个 **AI 去噪后端**，使得在较低的 SPP 下也能获得接近收敛的高质量画面，显著提升了创作迭代效率。

## 使用场景

-   **你在使用 Unreal 的路径追踪器进行电影级渲染或产品可视化**：路径追踪质量高但慢，使用此插件可以在 1/4 甚至更低的样本数下，通过 AI 去噪获得干净的预览，极大加速灯光和材质的调优过程。
-   **你需要在编辑器中实时预览路径追踪的最终效果**：启用此去噪器后，即使在 “进程式”（Progressive）模式下，画面也能快速变得清晰，提供更接近最终渲染的实时反馈。
-   **你计划开发自定义的去噪后处理管线**：此插件的架构（预处理 -> 推理 -> 后处理）和模块化设计，可以作为开发自定义 AI 去噪方案的参考框架。

## 蓝图用法

**注意**：当前版本的 `NNEDenoiserShaders` 模块主要封装底层 GPU 计算逻辑，并未暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 节点。去噪功能的配置和使用主要通过项目设置和 C++ API 进行。

### 核心配置（项目设置）

插件的启用和模型选择通过编辑器中的 **项目设置** 完成：
1.  打开 **项目设置（Project Settings）**。
2.  导航至 **引擎（Engine） -> 渲染（Rendering） -> 去噪（Denoising）**。
3.  你可以在此处为路径追踪器（Path Tracer）选择并配置一个基于 NNE 的去噪器。你需要提供一个包含合适神经网络模型的 `UNNEModelData` 资产。

### 使用示例（蓝图描述）

虽然无法在蓝图中直接调用去噪函数，但你可以通过蓝图控制渲染设置：
1.  在蓝图中，通过 `Get Game User Settings` 节点获取 `UGameUserSettings` 对象。
2.  使用 `Get Path Tracer Settings` 或类似节点访问路径追踪设置。
3.  通常，去噪器的启用状态是绑定在路径追踪器整体设置上的，无法通过蓝图为单个视口独立开关。你需要确保在项目设置中已正确配置去噪器。

## C++ 用法

用法主要涉及配置项目以使用特定的去噪模型，并可能实现自定义的去噪处理器。

### 头文件引入

```cpp
#include "NNEDenoiser.h"
#include "NNERuntimeORT.h"
```

### 基本用法：配置使用 NNE 去噪器

此示例展示如何在 C++ 中设置路径追踪器使用 NNE 去噪器（通常已在项目设置中完成）。
**来源参考**：测试用例通常模拟项目设置流程。

```cpp
// 1. 获取路径追踪设置（通常通过配置系统）
// FPathTracingSettings& PathTracingSettings = GetMutableDefault<URendererSettings>()->PathTracing;
// 2. 确保启用了 NNE 去噪器。这通常通过 CVar 控制。
// 例如，设置控制台变量：
// IConsoleManager::Get().SetConsoleVariableRef(TEXT("r.PathTracing.Denoiser"), 1);
// IConsoleManager::Get().SetConsoleVariableRef(TEXT("r.PathTracing.Denoiser.NNE.Model"), TEXT("/Game/Denoiser/MyModel.MyModel"));
```

### 进阶用法：创建自定义的去噪处理器（概要）

插件架构允许继承自定义处理器。核心基类是 `FNNEDenoiserDenoiser`。
**来源参考**：源码中的 `FNNEDenoiserDenoiser` 类。

```cpp
// 自定义去噪器处理器，需实现 IImagePassProcessor 接口或类似抽象
class FMyCustomDenoiserProcessor : public FSceneViewFamilyViewFamilyExtension // 或相关基类
{
public:
    // 初始化时，可能需要创建 NNE 模型实例
    virtual void Setup(const FViewFamilyInfo& InViewFamily) override;

    // 执行去噪，通常是一个后渲染阶段
    virtual void Render(FRHICommandListImmediate& RHICmdList, const FSceneView& View) override;

private:
    // 持有 NNE 模型和运行时句柄
    TUniquePtr<UE::NNE::IModelInstance> ModelInstance;
};
```

## Demo 示例

一个展示如何创建和初始化 NNE 去噪模型实例的最小示例。
**注意**：实际的去噪过程涉及复杂的渲染通道交互，此示例仅展示 NNE 模型初始化部分。

```cpp
// MyDenoiserExample.h
#pragma once
#include "CoreMinimal.h"

class FMyDenoiserExample
{
public:
    void InitializeDenoiser(const FString& ModelAssetPath);
    void RunInference(const TArray<float>& InputData, TArray<float>& OutputData);

private:
    TSharedPtr<UE::NNE::IModel> NNEModel;
    TUniquePtr<UE::NNE::IModelInstance> NNEModelInstance;
};
```

```cpp
// MyDenoiserExample.cpp
#include "MyDenoiserExample.h"
#include "NNE.h"
#include "NNERuntimeORT.h"

void FMyDenoiserExample::InitializeDenoiser(const FString& ModelAssetPath)
{
    // 加载模型资产
    const UNNEModelData* ModelData = LoadObject<UNNEModelData>(nullptr, *ModelAssetPath);
    if (!ModelData)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load NNE model data from: %s"), *ModelAssetPath);
        return;
    }

    // 获取默认运行时（通常是 ONNX Runtime）
    TArray<UE::NNE::ERuntimeType> RuntimeTypes;
    RuntimeTypes.Add(UE::NNE::ERuntimeType::ONNX);
    const TWeakInterfacePtr<UE::NNE::IRuntime> Runtime = UE::NNE::GetRuntime(RuntimeTypes);
    if (!Runtime.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get NNE runtime."));
        return;
    }

    // 创建模型和模型实例
    NNEModel = Runtime->CreateModel(ModelData->GetModelData());
    if (!NNEModel.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create NNE model."));
        return;
    }

    NNEModelInstance = NNEModel->CreateModelInstance();
    if (!NNEModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create NNE model instance."));
        return;
    }

    UE_LOG(LogTemp, Log, TEXT("NNE Denoiser model initialized successfully."));
}

void FMyDenoiserExample::RunInference(const TArray<float>& InputData, TArray<float>& OutputData)
{
    if (!NNEModelInstance.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Model instance not initialized."));
        return;
    }

    // 设置输入张量（尺寸需要与模型匹配）
    UE::NNE::FTensorBindingInput InputBinding;
    InputBinding.Data = InputData.GetData();
    InputBinding.SizeInBytes = InputData.Num() * sizeof(float);

    // 设置输出张量缓冲区
    const int32 OutputSize = /* 根据模型输出形状计算 */ 1024; // 示例值
    OutputData.SetNum(OutputSize);
    UE::NNE::FTensorBindingOutput OutputBinding;
    OutputBinding.Data = OutputData.GetData();
    OutputBinding.SizeInBytes = OutputData.Num() * sizeof(float);

    // 执行推理
    NNEModelInstance->RunSync({InputBinding}, {OutputBinding});
}
```

## 模块依赖

从 `NNEDenoiserShaders.Build.cs` 分析，此插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | NNE 的 ONNX Runtime 运行时实现，负责加载和执行 ONNX 神经网络模型。 |
| `RenderCore` | 提供渲染核心类型和工具（如 `FRDGBuilder`， RDG 资源）。 |
| `Renderer` | 提供场景渲染器和渲染通道支持。 |
| `RHICore` | RHI (Render Hardware Interface) 核心层。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 优化 GPU 同步原语，将两个函数合并为更高效的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将过时的 `UE_LOG` 宏迁移到新的、功能更强的 `UE_LOGF` 宏。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 修复编译依赖，为渲染相关头文件添加了缺失的 `#include` 和前向声明。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 重构渲染资源分配，将 `PooledRenderTarget` 和 `SceneRenderingAllocator` 拆分到独立头文件。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的全局查找替换导致的代码问题。 |

### 维护评价

-   **活跃维护**：插件自 2024 年 8 月从实验文件夹移出并标记为 Beta 以来，一直保持**非常频繁的更新**。最近一次更新距今仅数月。
-   **内容分析**：近期的提交主要集中在**底层优化**（GPU 同步、编译修复、头文件重构）和**代码现代化**（宏迁移），表明开发团队正在积极巩固代码基础、提升性能和可维护性，为正式发布做准备。
-   **已知限制**：当前为 **Beta** 状态（`IsBetaVersion=true`），意味着 API 可能发生变化，且可能包含未发现的缺陷。
-   **推荐使用**：**强烈推荐**给所有使用 Unreal 路径追踪器并寻求实时预览工作流的用户。尽管是 Beta，但作为 Epic 官方维护的核心组件，其稳定性和质量有保障。在生产环境中使用时，请关注 Beta 状态的更新日志。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser/Tests)（如果存在）
-   [依赖的 NNERuntimeORT 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)