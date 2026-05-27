# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（降噪器数据资产类型、映射数据表结构） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 为 UE 的路径追踪器（Path Tracer）提供基于神经网络的实时降噪能力。路径追踪渲染在低采样数下会产生大量噪点（火萤噪声），传统降噪方法效果有限，而神经网络降噪器能利用颜色（Color）、反照率（Albedo）、法线（Normal）等 G-Buffer 信息，通过推理模型输出高质量降噪图像。

该插件的核心价值在于：
- **抽象化神经网络推理流程**：将 NNE（Neural Network Engine）的模型推理集成到渲染管线（RDG）中，用户只需配置资产即可使用
- **支持三种运行时**：CPU、GPU、RDG，可根据硬件能力选择最优执行路径
- **内置分块（Tiling）机制**：对超大分辨率图像自动分块处理，避免 GPU 显存溢出
- **支持时序降噪**：利用运动矢量（Flow）在帧间传递信息，进一步提升降噪质量
- **传输函数支持**：内置 Open Image Denoise（OIDN）兼容的传输函数，将线性空间转换为神经网络友好的表示

## 使用场景

- 你在使用 Lumen 路径追踪器进行高质量离线渲染，但低采样下噪点严重 → 用 NNEDenoiser 配合降噪模型资产进行实时降噪
- 你需要在运行时以较低采样数快速预览路径追踪效果 → 启用 NNEDenoiser，可在 1-4 spp 下获得可用的预览质量
- 你有自训练的 ONNX 降噪模型 → 通过 NNERuntimeORT 加载模型，配置 I/O 映射表即可集成到渲染管线
- 你的渲染分辨率很高（如 4K/8K），GPU 显存不足以一次性推理 → 通过 TilingConfig 设置分块参数自动切块处理

## 蓝图用法

该插件主要通过**资产配置**和**项目设置**驱动，不提供大量蓝图可调用节点。核心交互发生在数据资产和数据表层面。

### 核心数据结构

| 结构体/枚举 | 说明 | 所在类 |
|---|---|---|
| `UNNEDenoiserAsset` | 空间降噪器数据资产，绑定模型和 I/O 映射 | `Public/NNEDenoiserAsset.h` |
| `UNNEDenoiserTemporalAsset` | 时序降噪器数据资产，额外支持运动矢量输入 | `Public/NNEDenoiserTemporalAsset.h` |
| `FTilingConfig` | 分块配置：对齐、重叠、最大/最小块大小 | `Public/NNEDenoiserTilingConfig.h` |
| `EResourceName` | 资源名称枚举：Color/Albedo/Normal/Flow/Output | `Public/NNEDenoiserResourceName.h` |
| `EDenoiserRuntimeType` | 运行时类型：CPU/GPU/RDG | `Public/NNEDenoiserSettings.h` |

### 核心设置类

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DenoiserAsset` | 选择降噪器数据资产 | `UNNEDenoiserSettings` |
| `MaximumTileSizeOverride` | 覆盖资产定义的最大块大小（-1=不覆盖） | `UNNEDenoiserSettings` |
| `RuntimeType` | 选择推理运行时（CPU/GPU/RDG） | `UNNEDenoiserSettings` |
| `RuntimeName` | 指定 NNE 运行时名称（可选） | `UNNEDenoiserSettings` |

### 使用示例（资产配置）

1. **创建降噪器数据资产**：右键 Content Browser → Miscellaneous → Data Asset → 选择 `NNEDenoiserAsset`
2. **配置模型**：在资产中指定 `ModelData`（指向你的 ONNX 模型导入后的 UNNEModelData）
3. **配置输入映射**：创建 DataTable（Row Structure = `NNEDenoiserInputMappingData`），定义张量通道与资源（Color/Albedo/Normal）的映射关系
4. **配置输出映射**：创建 DataTable（Row Structure = `NNEDenoiserOutputMappingData`），定义张量输出通道与 Output 的映射
5. **配置分块参数**：在 `TilingConfig` 中设置 Alignment、Overlap、MaxSize、MinSize
6. **启用降噪器**：在 Project Settings → Rendering → NNE Denoiser 中选择创建的降噪器资产

## C++ 用法

### 头文件引入

```cpp
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserTilingConfig.h"
```

### 基本用法

该插件的核心使用方式是**配置驱动**，C++ 层面主要用于：

1. **程序化创建降噪器资产**：

```cpp
// 创建空间降噪器资产并配置
UNNEDenoiserAsset* DenoiserAsset = NewObject<UNNEDenoiserAsset>();
DenoiserAsset->ModelData = MyModelDataSoftRef;
DenoiserAsset->InputMapping = InputMappingTableSoftRef;
DenoiserAsset->OutputMapping = OutputMappingTableSoftRef;

// 配置分块参数
DenoiserAsset->TilingConfig.Alignment = 8;
DenoiserAsset->TilingConfig.Overlap = 16;
DenoiserAsset->TilingConfig.MaxSize = 512;
DenoiserAsset->TilingConfig.MinSize = 64;
```

2. **运行时修改设置（通过 CVar）**：

```cpp
// 通过控制台变量切换运行时类型
IConsoleVariable* RuntimeTypeVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Type"));
if (RuntimeTypeVar)
{
    RuntimeTypeVar->Set(1); // 0=CPU, 1=GPU, 2=RDG
}

// 通过控制台变量指定运行时名称
IConsoleVariable* RuntimeNameVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Name"));
if (RuntimeNameVar)
{
    RuntimeNameVar->Set(TEXT("NNERuntimeORTDml"));
}
```

### 进阶用法

自定义传输函数和模型实例需要深入内部命名空间 `UE::NNEDenoiser::Private`：

```cpp
#include "NNEDenoiserModelInstance.h"
#include "NNEDenoiserTransferFunction.h"
#include "NNEDenoiserGenericDenoiser.h"
#include "NNEDenoiserResourceMapping.h"

// 通过内部 API 创建模型实例
namespace Private = UE::NNEDenoiser::Private;

// 创建 GPU 模型实例
TUniquePtr<Private::IModelInstance> ModelInstance = Private::FModelInstanceGPU::Make(
    *ModelData, TEXT("NNERuntimeORTDml")
);

// 设置输入张量形状（动态大小模型）
ModelInstance->SetInputTensorShapes(InputShapes);

// 构建资源映射列表
Private::FResourceMappingList InputMapping;
Private::FResourceMapping Mapping;
Mapping.Add(Private::FResourceInfo{EResourceName::Color, 0, 0});   // tensor channel 0 -> Color channel 0
Mapping.Add(Private::FResourceInfo{EResourceName::Color, 1, 0});   // tensor channel 1 -> Color channel 1
Mapping.Add(Private::FResourceInfo{EResourceName::Color, 2, 0});   // tensor channel 2 -> Color channel 2
Mapping.Add(Private::FResourceInfo{EResourceName::Albedo, 0, 0});  // tensor channel 3 -> Albedo channel 0
InputMapping.Add(Mapping);
```

## 模块依赖

从源码分析，插件依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `NNE` | Neural Network Engine 核心，提供模型加载和推理接口 |
| `NNERuntimeORT` | ONNX Runtime 推理后端（.uplugin 中声明为必要依赖） |
| `RenderCore` | RDG 渲染管线集成 |
| `RHI` | GPU 资源读写、纹理拷贝等底层操作 |
| `Renderer` | 路径追踪降噪器接口（IPathTracingDenoiser / IPathTracingSpatialTemporalDenoiser） |

## Demo 示例

### 自定义降噪器数据资产创建

```cpp
// NNEDenoiserDemo.h
#pragma once

#include "CoreMinimal.h"

class UNNEDenoiserAsset;
class UNNEModelData;
class UDataTable;

class FNNEDenoiserDemo
{
public:
    /** 创建一个完整的降噪器资产 */
    static UNNEDenoiserAsset* CreateDenoiserAsset(
        UNNEModelData* ModelData,
        UDataTable* InputMappingTable,
        UDataTable* OutputMappingTable,
        int32 TileSize = 256,
        int32 Overlap = 16);

    /** 创建输入映射数据表（Color + Albedo + Normal -> 3通道张量） */
    static UDataTable* CreateStandardInputMappingTable();

    /** 创建输出映射数据表（3通道张量 -> Output） */
    static UDataTable* CreateStandardOutputMappingTable();
};
```

```cpp
// NNEDenoiserDemo.cpp
#include "NNEDenoiserDemo.h"
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserTilingConfig.h"
#include "Engine/DataTable.h"
#include "NNEModelData.h"

UDataTable* FNNEDenoiserDemo::CreateStandardInputMappingTable()
{
    UDataTable* Table = NewObject<UDataTable>();
    Table->RowStruct = FNNEDenoiserInputMappingData::StaticStruct();

    // Color RGB -> Tensor Channel 0,1,2
    FNNEDenoiserInputMappingData ColorR;
    ColorR.TensorIndex = 0;
    ColorR.TensorChannel = 0;
    ColorR.ResourceChannel = 0; // R
    ColorR.Resource = EInputResourceName::Color;
    Table->AddRow(FName("Color_R"), ColorR);

    FNNEDenoiserInputMappingData ColorG;
    ColorG.TensorIndex = 0;
    ColorG.TensorChannel = 1;
    ColorG.ResourceChannel = 1; // G
    ColorG.Resource = EInputResourceName::Color;
    Table->AddRow(FName("Color_G"), ColorG);

    FNNEDenoiserInputMappingData ColorB;
    ColorB.TensorIndex = 0;
    ColorB.TensorChannel = 2;
    ColorB.ResourceChannel = 2; // B
    ColorB.Resource = EInputResourceName::Color;
    Table->AddRow(FName("Color_B"), ColorB);

    // Albedo RGB -> Tensor Channel 3,4,5
    FNNEDenoiserInputMappingData AlbedoR;
    AlbedoR.TensorIndex = 0;
    AlbedoR.TensorChannel = 3;
    AlbedoR.ResourceChannel = 0;
    AlbedoR.Resource = EInputResourceName::Albedo;
    Table->AddRow(FName("Albedo_R"), AlbedoR);

    FNNEDenoiserInputMappingData AlbedoG;
    AlbedoG.TensorIndex = 0;
    AlbedoG.TensorChannel = 4;
    AlbedoG.ResourceChannel = 1;
    AlbedoG.Resource = EInputResourceName::Albedo;
    Table->AddRow(FName("Albedo_G"), AlbedoG);

    FNNEDenoiserInputMappingData AlbedoB;
    AlbedoB.TensorIndex = 0;
    AlbedoB.TensorChannel = 5;
    AlbedoB.ResourceChannel = 2;
    AlbedoB.Resource = EInputResourceName::Albedo;
    Table->AddRow(FName("Albedo_B"), AlbedoB);

    // Normal RGB -> Tensor Channel 6,7,8
    FNNEDenoiserInputMappingData NormalR;
    NormalR.TensorIndex = 0;
    NormalR.TensorChannel = 6;
    NormalR.ResourceChannel = 0;
    NormalR.Resource = EInputResourceName::Normal;
    Table->AddRow(FName("Normal_R"), NormalR);

    FNNEDenoiserInputMappingData NormalG;
    NormalG.TensorIndex = 0;
    NormalG.TensorChannel = 7;
    NormalG.ResourceChannel = 1;
    NormalG.Resource = EInputResourceName::Normal;
    Table->AddRow(FName("Normal_G"), NormalG);

    FNNEDenoiserInputMappingData NormalB;
    NormalB.TensorIndex = 0;
    NormalB.TensorChannel = 8;
    NormalB.ResourceChannel = 2;
    NormalB.Resource = EInputResourceName::Normal;
    Table->AddRow(FName("Normal_B"), NormalB);

    return Table;
}

UDataTable* FNNEDenoiserDemo::CreateStandardOutputMappingTable()
{
    UDataTable* Table = NewObject<UDataTable>();
    Table->RowStruct = FNNEDenoiserOutputMappingData::StaticStruct();

    // Output RGB <- Tensor Channel 0,1,2
    FNNEDenoiserOutputMappingData OutR;
    OutR.TensorIndex = 0;
    OutR.TensorChannel = 0;
    OutR.ResourceChannel = 0;
    OutR.Resource = EOutputResourceName::Output;
    Table->AddRow(FName("Output_R"), OutR);

    FNNEDenoiserOutputMappingData OutG;
    OutG.TensorIndex = 0;
    OutG.TensorChannel = 1;
    OutG.ResourceChannel = 1;
    OutG.Resource = EOutputResourceName::Output;
    Table->AddRow(FName("Output_G"), OutG);

    FNNEDenoiserOutputMappingData OutB;
    OutB.TensorIndex = 0;
    OutB.TensorChannel = 2;
    OutB.ResourceChannel = 2;
    OutB.Resource = EOutputResourceName::Output;
    Table->AddRow(FName("Output_B"), OutB);

    return Table;
}

UNNEDenoiserAsset* FNNEDenoiserDemo::CreateDenoiserAsset(
    UNNEModelData* ModelData,
    UDataTable* InputMappingTable,
    UDataTable* OutputMappingTable,
    int32 TileSize,
    int32 Overlap)
{
    UNNEDenoiserAsset* Asset = NewObject<UNNEDenoiserAsset>();

    Asset->ModelData = ModelData;
    Asset->InputMapping = InputMappingTable;
    Asset->OutputMapping = OutputMappingTable;

    Asset->TilingConfig.Alignment = 8;
    Asset->TilingConfig.Overlap = Overlap;
    Asset->TilingConfig.MaxSize = TileSize;
    Asset->TilingConfig.MinSize = 64;

    return Asset;
}
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换旧版 GPU 同步 API 为新的统一接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到 UE_LOGF 格式 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染头文件的前置声明和 include |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染资源头文件，添加显式 include |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复上一次批量替换导致的编译错误 |

### 维护评价

- **活跃维护中**：最近一次更新在 2026-04-15，且持续有实质性改动（API 迁移、头文件重构）
- **Beta 状态**：`.uplugin` 标记 `IsBetaVersion=true`，API 可能在未来版本发生变化
- **创建时间短**：2024 年 8 月创建，约 2 年历史，属于较新的插件
- **迭代方向**：近期更新主要是编译兼容性和代码质量改进（头文件清理、API 迁移），说明框架趋于稳定
- **推荐程度**：⭐⭐⭐（3/5）— 功能实用且维护活跃，但 Beta 标签意味着生产环境需谨慎。依赖 NNERuntimeORT，确保目标平台支持 ONNX Runtime 推理

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [官方文档]()（暂无）