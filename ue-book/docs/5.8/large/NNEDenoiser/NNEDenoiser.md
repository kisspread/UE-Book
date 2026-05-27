# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（降噪资产、数据表） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是一个基于 NNE（Neural Network Engine）的神经网络降噪插件，专门为 Unreal 的路径追踪器（Path Tracer）提供 AI 降噪能力。它通过加载预训练的神经网络模型（如 Intel Open Image Denoise 系列模型），对路径追踪产生的含噪图像进行智能降噪处理，从而大幅减少达到可接受画质所需的采样数。

该插件的核心价值在于：
- **多运行时支持**：支持 CPU、GPU 和 RDG（Render Dependency Graph）三种后端运行时，用户可根据硬件能力选择最优方案
- **时间降噪**：除空间降噪外，还支持时间维度的降噪（Temporal Denoising），利用前帧信息和光流（Flow）实现更稳定的降噪效果
- **分块处理**：内置 Tiling 机制，将大分辨率图像分块处理，使显存有限的 GPU 也能处理大图
- **自动集成**：通过 FViewExtension 自动注入到路径追踪渲染管线中，用户无需手动调用

## 使用场景

- 你在使用 UE5 路径追踪器渲染动画或静帧 → 启用 NNEDenoiser 可以用少量采样获得干净的渲染结果
- 你在做建筑可视化或产品渲染 → 路径追踪配合神经网络降噪可大幅缩短渲染时间
- 你需要时间稳定的降噪效果（避免逐帧闪烁）→ 使用 Temporal 降噪资产配置
- 你的 GPU 显存有限但需要处理高分辨率图像 → 通过调整 Tiling 配置的 MaxSize 控制显存占用

## 蓝图用法

该插件主要通过配置资产和项目设置工作，不暴露通用的蓝图可调用降噪函数。降噪过程在路径追踪管线中自动执行。

### 核心资产类型

| 资产类 | 说明 |
|---|---|
| `UNNEDenoiserAsset` | 空间降噪器资产，包含模型数据、输入/输出映射表和分块配置 |
| `UNNEDenoiserTemporalAsset` | 时间降噪器资产，额外支持光流和历史帧输入 |

### 配置方法

1. **创建降噪器资产**：在内容浏览器中右键 → Miscellaneous → Data Asset → 选择 `NNEDenoiserAsset` 或 `NNEDenoiserTemporalAsset`
2. **配置资产**：指定 NNE 模型数据（`ModelData`）、输入映射表（`InputMapping`）和输出映射表（`OutputMapping`）
3. **在项目设置中启用**：Project Settings → NNE Denoiser → 选择刚创建的资产
4. **运行时自动生效**：启用路径追踪后，降噪器将自动介入

### 设置面板说明

| 设置项 | 说明 |
|---|---|
| Denoiser Asset | 选择空间降噪器资产 |
| Maximum Tile Size Override | 覆盖资产定义的最大分块尺寸（-1 表示不覆盖） |
| Runtime Type | 选择运行时类型：CPU / GPU / RDG（通过控制台变量 `NNEDenoiser.Runtime.Type`） |
| Runtime Name Override | 指定 NNE 运行时名称（通过控制台变量 `NNEDenoiser.Runtime.Name`） |

## C++ 用法

该插件主要作为路径追踪管线的内部组件运行。以下为在 C++ 中与插件交互的核心方式。

### 头文件引入

```cpp
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserResourceName.h"
#include "NNEDenoiserTilingConfig.h"
```

### 基本用法：创建降噪器资产

```cpp
// 源码参考：Public/NNEDenoiserAsset.h

// 创建空间降噪器资产
UNNEDenoiserAsset* DenoiserAsset = NewObject<UNNEDenoiserAsset>();
DenoiserAsset->ModelData = YourNNEModelData;        // NNE 模型数据
DenoiserAsset->InputMapping = YourInputDataTable;   // 输入映射表
DenoiserAsset->OutputMapping = YourOutputDataTable; // 输出映射表

// 配置分块参数
DenoiserAsset->TilingConfig.Alignment = 16;  // 对齐要求（动态尺寸模型适用）
DenoiserAsset->TilingConfig.Overlap = 32;    // 分块重叠像素数
DenoiserAsset->TilingConfig.MaxSize = 1024;  // 最大分块尺寸
DenoiserAsset->TilingConfig.MinSize = 64;    // 最小分块尺寸
```

### 基本用法：配置输入映射表

```cpp
// 源码参考：Public/NNEDenoiserIOMappingData.h

// 输入映射表的每一行定义一个从渲染资源到张量的通道映射
// FNNEDenoiserInputMappingData 结构：
// - Resource: 渲染资源名称（Color/Albedo/Normal/Output）
// - TensorIndex: 目标张量索引
// - TensorChannel: 目标张量通道
// - ResourceChannel: 源资源通道

// 例如：将 Color 纹理的 R/G/B 通道分别映射到张量 0 的通道 0/1/2
FNNEDenoiserInputMappingData Row0;
Row0.Resource = EInputResourceName::Color;
Row0.TensorIndex = 0;
Row0.TensorChannel = 0;
Row0.ResourceChannel = 0;
```

### 进阶用法：访问降噪器设置

```cpp
// 源码参考：Public/NNEDenoiserSettings.h

// 通过 CVar 控制运行时类型
// 控制台变量 NNEDenoiser.Runtime.Type: 0=CPU, 1=GPU, 2=RDG
IConsoleVariable* RuntimeTypeCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Type"));
if (RuntimeTypeCVar)
{
    int32 Type = RuntimeTypeCVar->GetInt(); // 0=CPU, 1=GPU, 2=RDG
}

// 控制台变量 NNEDenoiser.Runtime.Name 指定运行时名称
IConsoleVariable* RuntimeNameCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Name"));
if (RuntimeNameCVar)
{
    FString Name = RuntimeNameCVar->GetString();
}
```

### 进阶用法：时间降噪器配置

```cpp
// 源码参考：Public/NNEDenoiserTemporalAsset.h, Public/NNEDenoiserIOMappingData.h

// 时间降噪器额外支持 Flow（光流）和历史帧输入
// ETemporalInputResourceName 枚举：Color, Albedo, Normal, Flow, Output

// 时间输入映射支持 FrameIndex 字段，用于访问历史帧
FNNEDenoiserTemporalInputMappingData TemporalRow;
TemporalRow.Resource = ETemporalInputResourceName::Color;
TemporalRow.TensorIndex = 0;
TemporalRow.TensorChannel = 0;
TemporalRow.ResourceChannel = 0;
TemporalRow.FrameIndex = 0;  // 0=当前帧, -1=上一帧, 依此类推
```

## Demo 示例

以下示例展示如何在 C++ 中创建一个简单的降噪器配置资产并注册到设置中。

### NNEDenoiserDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NNEDenoiserDemo.generated.h"

class UNNEDenoiserAsset;

UCLASS()
class UNNEDenoiserDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /** 创建一个基础的降噪器资产配置 */
    UFUNCTION(BlueprintCallable, Category = "NNEDenoiser Demo")
    UNNEDenoiserAsset* CreateBasicDenoiserAsset(UObject* Outer);

    /** 获取当前降噪器运行时类型 */
    UFUNCTION(BlueprintPure, Category = "NNEDenoiser Demo")
    int32 GetRuntimeType() const;
};
```

### NNEDenoiserDemo.cpp

```cpp
#include "NNEDenoiserDemo.h"
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserTilingConfig.h"
#include "NNEDenoiserIOMappingData.h"
#include "Engine/DataTable.h"

void UNNEDenoiserDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    
    UE_LOG(LogTemp, Log, TEXT("NNEDenoiser Demo: Plugin initialized."));
    UE_LOG(LogTemp, Log, TEXT("  Supported platforms: Win64, Linux, Mac"));
    UE_LOG(LogTemp, Log, TEXT("  Runtime types: CPU, GPU, RDG"));
}

UNNEDenoiserAsset* UNNEDenoiserDemoSubsystem::CreateBasicDenoiserAsset(UObject* Outer)
{
    if (!Outer)
    {
        Outer = GetTransientPackage();
    }

    UNNEDenoiserAsset* Asset = NewObject<UNNEDenoiserAsset>(Outer, NAME_None, RF_Transient);
    
    // 配置分块参数（典型 ONNX 模型的配置）
    Asset->TilingConfig.Alignment = 16;
    Asset->TilingConfig.Overlap = 32;
    Asset->TilingConfig.MaxSize = 2048;
    Asset->TilingConfig.MinSize = 64;

    // 创建输入映射表
    UDataTable* InputTable = NewObject<UDataTable>(Asset, NAME_None, RF_Transient);
    InputTable->RowStruct = FNNEDenoiserInputMappingData::StaticStruct();

    // Color R -> Tensor 0, Channel 0
    FNNEDenoiserInputMappingData* ColorR = new FNNEDenoiserInputMappingData();
    ColorR->Resource = EInputResourceName::Color;
    ColorR->TensorIndex = 0;
    ColorR->TensorChannel = 0;
    ColorR->ResourceChannel = 0;
    InputTable->AddRow(FName("ColorR"), *ColorR);

    // Color G -> Tensor 0, Channel 1
    FNNEDenoiserInputMappingData* ColorG = new FNNEDenoiserInputMappingData();
    ColorG->Resource = EInputResourceName::Color;
    ColorG->TensorIndex = 0;
    ColorG->TensorChannel = 1;
    ColorG->ResourceChannel = 1;
    InputTable->AddRow(FName("ColorG"), *ColorG);

    // Color B -> Tensor 0, Channel 2
    FNNEDenoiserInputMappingData* ColorB = new FNNEDenoiserInputMappingData();
    ColorB->Resource = EInputResourceName::Color;
    ColorB->TensorIndex = 0;
    ColorB->TensorChannel = 2;
    ColorB->ResourceChannel = 2;
    InputTable->AddRow(FName("ColorB"), *ColorB);

    Asset->InputMapping = InputTable;

    // 创建输出映射表
    UDataTable* OutputTable = NewObject<UDataTable>(Asset, NAME_None, RF_Transient);
    OutputTable->RowStruct = FNNEDenoiserOutputMappingData::StaticStruct();

    // Tensor 0, Channel 0 -> Output R
    FNNEDenoiserOutputMappingData* OutR = new FNNEDenoiserOutputMappingData();
    OutR->Resource = EOutputResourceName::Output;
    OutR->TensorIndex = 0;
    OutR->TensorChannel = 0;
    OutR->ResourceChannel = 0;
    OutputTable->AddRow(FName("OutR"), *OutR);

    // Tensor 0, Channel 1 -> Output G
    FNNEDenoiserOutputMappingData* OutG = new FNNEDenoiserOutputMappingData();
    OutG->Resource = EOutputResourceName::Output;
    OutG->TensorIndex = 0;
    OutG->TensorChannel = 1;
    OutG->ResourceChannel = 1;
    OutputTable->AddRow(FName("OutG"), *OutG);

    // Tensor 0, Channel 2 -> Output B
    FNNEDenoiserOutputMappingData* OutB = new FNNEDenoiserOutputMappingData();
    OutB->Resource = EOutputResourceName::Output;
    OutB->TensorIndex = 0;
    OutB->TensorChannel = 2;
    OutB->ResourceChannel = 2;
    OutputTable->AddRow(FName("OutB"), *OutB);

    Asset->OutputMapping = OutputTable;

    return Asset;
}

int32 UNNEDenoiserDemoSubsystem::GetRuntimeType() const
{
    const IConsoleVariable* CVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Type"));
    return CVar ? CVar->GetInt() : 0;
}
```

## 模块依赖

从 Build.cs 和 .uplugin 分析得出的依赖关系：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心，提供模型加载和推理接口 |
| `NNERuntimeORT` | ONNX Runtime 后端（插件级依赖，提供 CPU/GPU 推理能力） |
| `RenderCore` | RDG（Render Dependency Graph）渲染管线集成 |
| `RHI` | 渲染硬件接口，用于 GPU/CPU 数据拷贝 |
| `Renderer` | 路径追踪器降噪接口（IPathTracingDenoiser） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换废弃的 GPU 同步 API 为新接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF 格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染相关头文件的前向声明 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染头文件，增加显式包含 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换操作 |

### 维护评价

NNEDenoiser 是一个较新的插件（约 2 年历史），由 Epic Games 官方维护。最近半年内有持续的代码维护活动，主要集中在编译兼容性修复和 API 迁移（如 UE_LOG → UE_LOGF、GPU 同步 API 更新等）。

**当前状态**：
- ⚠️ **Beta 阶段**：.uplugin 标记为 `IsBetaVersion=true`，API 可能发生变化
- ✅ **活跃维护**：最近 3 个月内有多次更新，紧跟引擎 API 变更
- ✅ **官方支持**：由 Epic Games 维护，与引擎路径追踪器紧密集成
- ⚠️ **依赖 NNERuntimeORT**：需要启用 ONNX Runtime 后端插件才能正常工作

**推荐**：适合在 Beta 环境和原型开发中使用。生产环境需关注 Beta 标记带来的 API 稳定性风险。由于该插件通过 FViewExtension 自动集成到路径追踪管线，用户使用门槛较低，主要工作在于准备合适的 NNE 降噪模型。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [官方文档]()（暂无）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser/Tests)（如有）