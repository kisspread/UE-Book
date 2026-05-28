# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据资产） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 插件的核心目的是利用神经网络引擎（NNE）为虚幻引擎的路径追踪渲染器提供智能的图像降噪能力。路径追踪器能够生成物理上正确的图像，但往往需要大量采样才能收敛到清晰结果，这导致渲染时间很长。该插件通过集成一个经过训练的神经网络模型，在渲染过程中（或之后）对带有噪声的原始图像进行降噪处理，从而能够在使用较少采样数的情况下，获得视觉上可接受的结果，显著提升渲染效率。

与传统基于滤波的降噪器不同，神经网络降噪器能够学习并理解复杂场景下的噪声模式，在保留细节和材质特性方面表现更佳。

## 使用场景

-   当你在项目中使用**路径追踪器**进行最终画面渲染或预览，但受困于漫长的收敛时间（渲染噪点多）时。
-   希望在保持路径追踪物理正确性的前提下，**实时或准实时地获得降噪后的画面**。
-   需要为大型开放世界场景或复杂光照环境配置一个高效、自适应的降噪流程时。

## 蓝图用法

NNEDenoiser 主要通过 C++ 接口与引擎的渲染管线集成。其提供了一些蓝图可访问的结构和枚举，用于数据配置。

### 核心结构

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EInputResourceName` | 枚举，定义降噪器输入资源类型（Color, Albedo, Normal, Output）。 | `NNEDenoiserIOMappingData` |
| `EOutputResourceName` | 枚举，定义降噪器输出资源类型（Output）。 | `NNEDenoiserIOMappingData` |
| `FNNEDenoiserInputMappingData` | 数据表行结构体，用于定义神经网络输入张量通道到渲染资源（颜色、反照率等）通道的映射。 | `NNEDenoiserIOMappingData` |
| `FNNEDenoiserOutputMappingData` | 数据表行结构体，用于定义神经网络输出张量通道到最终输出资源通道的映射。 | `NNEDenoiserIOMappingData` |
| `FTilingConfig` | 结构体，配置降噪器的分块处理参数（对齐、重叠、尺寸范围）。 | `NNEDenoiserTilingConfig` |
| `UNNEDenoiserAsset` | 数据资产，组合了 NNE 模型数据、输入/输出映射表和分块配置，是配置一个空间降噪器的完整包。 | `NNEDenoiserAsset` |

### 使用示例（蓝图描述）

在编辑器中，你主要通过**项目设置**来配置 NNEDenoiser。
1.  打开“项目设置” -> “引擎” -> “NNE Denoiser”。
2.  在“Denoiser Asset”字段，指定一个你创建好的 `NNEDenoiserAsset` 资产。
3.  （可选）配置“Runtime Type”（CPU/GPU/RDG）和“Maximum tile size override”来优化性能和内存使用。
引擎的路径追踪渲染器在启用降噪后，会自动使用此插件提供的神经网络降噪功能。

## C++ 用法

### 头文件引入

```cpp
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserIOMappingData.h"
```

### 基本用法

该插件主要通过引擎设置类 `UNNEDenoiserSettings` 进行配置，这些设置通常通过编辑器或 CVar 进行管理。核心逻辑由 `FViewExtension` 自动处理。

```cpp
// 通过全局设置访问降噪器配置 (通常不需要直接调用)
const UNNEDenoiserSettings* Settings = GetDefault<UNNEDenoiserSettings>();
if (Settings && Settings->DenoiserAsset.IsValid())
{
    UE_LOG(LogTemp, Log, TEXT("NNE Denoiser asset loaded: %s"), *Settings->DenoiserAsset.GetAssetName());
}
// 运行时类型可通过控制台变量设置: nnedenisor.runtime.type 0 (CPU), 1 (GPU), 2 (RDG)
```

### 进阶用法（自定义模型实例）

对于开发者，插件内部提供了对 CPU、GPU 和 RDG 三种运行时的模型实例封装，用于执行推理。这通常由插件内部的 `FGenericDenoiser` 管理。

```cpp
// 示例：创建一个基于 CPU 的模型实例 (来自 NNEDenoiserModelInstanceCPU.h)
#include "NNEDenoiserModelInstanceCPU.h"
#include "NNE.h"

// 假设 ModelData 是一个 UNNEModelData* 对象
TUniquePtr<UE::NNEDenoiser::Private::FModelInstanceCPU> CPUInstance = 
    UE::NNEDenoiser::Private::FModelInstanceCPU::Make(*ModelData, TEXT("CPURuntimeName"));

if (CPUInstance)
{
    // 获取输入输出张量描述
    TConstArrayView<NNE::FTensorDesc> InputDescs = CPUInstance->GetInputTensorDescs();
    TConstArrayView<NNE::FTensorDesc> OutputDescs = CPUInstance->GetOutputTensorDescs();
    // ... 后续准备数据并推理
}
```

## Demo 示例

以下示例展示了如何创建一个最简单的 `UNNEDenoiserAsset`，用于空间降噪。

**`MyDenoiserAsset.h`**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "NNEDenoiserAsset.h"
#include "MyDenoiserAsset.generated.h"

UCLASS(BlueprintType)
class UMyDenoiserAsset : public UNNEDenoiserAsset
{
    GENERATED_BODY()
public:
    // 此类继承自 UNNEDenoiserAsset，你可以在编辑器中为其设置 ModelData, InputMapping, OutputMapping 和 TilingConfig。
    // 这里不需要额外的代码，所有配置通过编辑器属性完成。
};
```

**`MyDenoiserSubsystem.h` (示例用法)**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NNEDenoiserSettings.h"
#include "MyDenoiserSubsystem.generated.h"

UCLASS()
class UMyDenoiserSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override
    {
        // 获取默认设置并检查降噪器是否已配置
        const UNNEDenoiserSettings* DenoiserSettings = GetDefault<UNNEDenoiserSettings>();
        if (DenoiserSettings->DenoiserAsset.IsNull())
        {
            UE_LOG(LogTemp, Warning, TEXT("NNE Denoiser asset is not configured in Project Settings."));
        }
        else
        {
            UE_LOG(LogTemp, Log, TEXT("NNE Denoiser is configured with asset: %s"), *DenoiserSettings->DenoiserAsset.GetAssetName());
        }

        // 提示：运行时类型可以通过控制台命令 `nnedenisor.runtime.type` 在运行时切换 (0: CPU, 1: GPU, 2: RDG)
    }
};
```

## 模块依赖

从 `Build.cs` 分析，要使用此插件，你的项目需要依赖以下模块（标准核心模块已省略）：

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎模块，提供模型加载、推理等基础功能。 |
| `RenderCore` | 提供 RDG (Render Dependency Graph) 等底层渲染核心支持。 |
| `Renderer` | 引擎渲染器，提供 `IPathTracingDenoiser` 等接口。 |
| `RHI` | 渲染硬件接口，用于 GPU 资源操作和回读。 |
| `Projects` | 用于访问插件和项目设置。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 优化GPU同步，将分离的阻塞操作合并为单一函数调用。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志输出宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染相关头文件的前置声明和包含。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分头文件以改善编译依赖和编译时间。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复前一次提交中错误的查找替换操作。 |

### 维护评价

- **状态**：**活跃维护中**。创建于 2024 年 8 月，至今约 2 年，但属于较新的 UE5 功能。
- **近期活动**：最近几个月有持续的代码提交，包括重构、优化和头文件整理，表明该插件正在积极开发和完善。
- **注意事项**：该插件当前标记为 **Beta 版** (`IsBetaVersion=true`)，这意味着其 API 和功能可能在未来版本中发生变化。
- **推荐度**：**推荐关注和使用**。作为 Epic Games 官方提供的、基于 NNE 的路径追踪降噪解决方案，它代表了引擎在智能渲染方面的重要方向。对于使用路径追踪且对性能或质量有要求的项目，非常值得尝试。但请注意其 Beta 状态，并在生产环境中做好兼容性测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [官方文档]() (暂无)
- [测试用例]() (暂未在提供的信息中定位到具体路径)