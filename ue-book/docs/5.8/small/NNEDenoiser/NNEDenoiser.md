# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（降噪器资产、数据表模板） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 为 Unreal 路径追踪渲染器提供基于神经网络的降噪功能。路径追踪（Path Tracing）虽然能产生物理准确的渲染结果，但需要大量采样才能消除噪点，渲染速度较慢。该插件通过 NNE（Neural Network Engine）加载预训练的去噪模型，在少量采样的情况下对渲染结果进行智能降噪，从而大幅减少路径追踪所需的时间。

该插件的核心价值：
- **替代传统的时空域降噪器**：用神经网络模型替代基于传统算法的降噪方案
- **支持多种运行时**：可在 CPU、GPU 和 RDG（Render Dependency Graph）上运行模型推理
- **支持时序降噪**：利用前几帧的信息（通过运动矢量/光流）实现更稳定的降噪效果
- **智能分块处理**：对大尺寸图像自动分块推理，适配模型的输入尺寸限制并优化显存占用
- **灵活的输入输出映射**：通过数据表配置神经网络张量与渲染资源（颜色、Albedo、法线等）之间的通道映射关系

## 使用场景

- 你正在使用路径追踪渲染器，但渲染结果噪点太多且不想等待大量采样 → 使用 NNEDenoiser 自动降噪
- 你需要在实时或近实时的路径追踪预览中获得干净的画面 → 配置 NNEDenoiser 并设置降噪器资产
- 你有自训练的 ONNX 去噪模型，想集成到 UE5 路径追踪管线中 → 创建 `UNNEDenoiserAsset` 资产并配置映射表
- 你需要对降噪过程进行细粒度控制（如分块大小、重叠区域、对齐要求）→ 通过 `FTilingConfig` 进行调整
- 你需要同时支持空间降噪和时空域降噪 → 使用 `UNNEDenoiserAsset`（空间）和 `UNNEDenoiserTemporalAsset`（时空域）

## 蓝图用法

NNEDenoiser 主要是一个通过设置资产和 CVar 配置驱动的系统，不需要直接调用蓝图函数。它通过视图扩展（View Extension）自动注入路径追踪管线。

### 核心资产类型

| 资产类型 | 说明 |
|---|---|
| `UNNEDenoiserAsset` | 降噪器配置资产，包含模型数据、输入/输出映射表和分块配置 |
| `UNNEDenoiserTemporalAsset` | 时序降噪器配置资产，额外支持光流输入和多帧历史 |
| `UNNEDenoiserSettings` | 项目设置（CVar 驱动），选择使用的降噪器资产和运行时类型 |

### 配置流程

1. **创建降噪器资产**：在内容浏览器中右键 → Miscellaneous → Data Asset → 选择 `NNEDenoiserAsset`
2. **配置模型数据**：将 ONNX 模型导入后生成的 `UNNEModelData` 赋值给 `ModelData` 字段
3. **创建输入映射表**：新建 DataTable（行结构选择 `NNEDenoiserInputMappingData`），定义颜色、Albedo、法线等资源到张量的通道映射
4. **创建输出映射表**：新建 DataTable（行结构选择 `NNEDenoiserOutputMappingData`），定义张量到输出资源的通道映射
5. **配置分块参数**：设置 `TilingConfig` 中的对齐、重叠、最大/最小块尺寸
6. **在项目设置中选择资产**：Project Settings → Engine → NNE Denoiser → 选择创建的降噪器资产

### 映射表字段

| 字段 | 说明 |
|---|---|
| `TensorIndex` | 张量索引（一个模型可能有多个输入/输出张量） |
| `TensorChannel` | 张量通道 |
| `ResourceChannel` | 渲染资源通道（如 R/G/B/A） |
| `Resource` | 资源名称（Color/Albedo/Normal/Flow/Output） |
| `FrameIndex` | 帧索引（仅时序降噪器，0=当前帧，1=上一帧等） |

## C++ 用法

### 头文件引入

```cpp
#include "NNEDenoiserAsset.h"
#include "NNEDenoiserTemporalAsset.h"
#include "NNEDenoiserSettings.h"
#include "NNEDenoiserIOMappingData.h"
#include "NNEDenoiserTilingConfig.h"
#include "NNEDenoiserResourceName.h"
```

### 基本用法：程序化创建降噪器资产

以下代码展示如何通过 C++ 创建和配置一个降噪器资产（来源于资产结构定义 `Public/NNEDenoiserAsset.h`）：

```cpp
// 创建降噪器资产
UNNEDenoiserAsset* DenoiserAsset = NewObject<UNNEDenoiserAsset>();

// 绑定 NNE 模型数据（假设已导入 ONNX 模型）
UNNEModelData* ModelData = /* 从已导入的模型获取 */;
DenoiserAsset->ModelData = ModelData;

// 配置分块参数
DenoiserAsset->TilingConfig.Alignment = 16;    // 对齐到 16 像素
DenoiserAsset->TilingConfig.Overlap = 32;      // 32 像素重叠
DenoiserAsset->TilingConfig.MaxSize = 512;     // 最大 512x512 分块
DenoiserAsset->TilingConfig.MinSize = 64;      // 最小 64x64 分块
```

### 基本用法：配置输入/输出映射表

（来源于 `Public/NNEDenoiserIOMappingData.h` 的结构体定义）

```cpp
// 创建输入映射表
UDataTable* InputMappingTable = NewObject<UDataTable>();
InputMappingTable->RowStruct = FNNEDenoiserInputMappingData::StaticStruct();

// 添加颜色通道映射：将渲染的 Color RGB 映射到张量的通道 0/1/2
FNNEDenoiserInputMappingData ColorR;
ColorR.Resource = EInputResourceName::Color;
ColorR.TensorIndex = 0;
ColorR.TensorChannel = 0;
ColorR.ResourceChannel = 0;  // R 通道
InputMappingTable->AddRow(FName("ColorR"), ColorR);

FNNEDenoiserInputMappingData ColorG = ColorR;
ColorG.TensorChannel = 1;
ColorG.ResourceChannel = 1;  // G 通道
InputMappingTable->AddRow(FName("ColorG"), ColorG);

FNNEDenoiserInputMappingData ColorB = ColorR;
ColorB.TensorChannel = 2;
ColorB.ResourceChannel = 2;  // B 通道
InputMappingTable->AddRow(FName("ColorB"), ColorB);

// 添加 Albedo 通道映射
FNNEDenoiserInputMappingData AlbedoR;
AlbedoR.Resource = EInputResourceName::Albedo;
AlbedoR.TensorIndex = 1;
AlbedoR.TensorChannel = 0;
AlbedoR.ResourceChannel = 0;
InputMappingTable->AddRow(FName("AlbedoR"), AlbedoR);

// 创建输出映射表
UDataTable* OutputMappingTable = NewObject<UDataTable>();
OutputMappingTable->RowStruct = FNNEDenoiserOutputMappingData::StaticStruct();

FNNEDenoiserOutputMappingData OutputR;
OutputR.Resource = EOutputResourceName::Output;
OutputR.TensorIndex = 0;
OutputR.TensorChannel = 0;
OutputR.ResourceChannel = 0;
OutputMappingTable->AddRow(FName("OutputR"), OutputR);
```

### 进阶用法：时序降噪器配置

（来源于 `Public/NNEDenoiserTemporalAsset.h` 和 `Public/NNEDenoiserIOMappingData.h`）

```cpp
// 创建时序降噪器资产
UNNEDenoiserTemporalAsset* TemporalAsset = NewObject<UNNEDenoiserTemporalAsset>();
TemporalAsset->ModelData = TemporalModelData;

// 时序输入映射需要额外的 FrameIndex 字段
UDataTable* TemporalInputTable = NewObject<UDataTable>();
TemporalInputTable->RowStruct = FNNEDenoiserTemporalInputMappingData::StaticStruct();

// 当前帧颜色
FNNEDenoiserTemporalInputMappingData CurrentColor;
CurrentColor.Resource = ETemporalInputResourceName::Color;
CurrentColor.TensorIndex = 0;
CurrentColor.TensorChannel = 0;
CurrentColor.ResourceChannel = 0;
CurrentColor.FrameIndex = 0;  // 当前帧
TemporalInputTable->AddRow(FName("CurrentColorR"), CurrentColor);

// 前一帧颜色（用于时序稳定性）
FNNEDenoiserTemporalInputMappingData PrevColor = CurrentColor;
PrevColor.FrameIndex = 1;  // 上一帧
TemporalInputTable->AddRow(FName("PrevColorR"), PrevColor);

// 光流输入（用于帧间对齐）
FNNEDenoiserTemporalInputMappingData Flow;
Flow.Resource = ETemporalInputResourceName::Flow;
Flow.TensorIndex = 2;
Flow.TensorChannel = 0;
Flow.ResourceChannel = 0;
Flow.FrameIndex = 0;
TemporalInputTable->AddRow(FName("FlowX"), Flow);
```

### 进阶用法：通过 CVar 控制运行时

（来源于 `Public/NNEDenoiserSettings.h`）

```cpp
// 控制台变量控制
// NNEDenoiser.Runtime.Type - 运行时类型 (0=CPU, 1=GPU, 2=RDG)
// NNEDenoiser.Runtime.Name - 运行时名称（如 "ORTDml" 使用 DirectML）

// 在代码中设置
IConsoleVariable* RuntimeTypeCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Type"));
if (RuntimeTypeCVar)
{
    RuntimeTypeCVar->Set(2);  // 使用 RDG 运行时
}

IConsoleVariable* RuntimeNameCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("NNEDenoiser.Runtime.Name"));
if (RuntimeNameCVar)
{
    RuntimeNameCVar->Set(TEXT("ORTDml"));  // 使用 DirectML 加速
}
```

## 模块依赖

该插件依赖 `NNERuntimeORT` 插件（ONNX Runtime 推理后端）。

从源码结构和接口来看，使用者的模块需要依赖以下特殊模块：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心，提供模型加载和推理接口 |
| `NNERuntimeORT` | ONNX Runtime 推理后端，实际执行模型推理 |
| `Renderer` | 路径追踪降噪器接口（`IPathTracingDenoiser`、`IPathTracingSpatialTemporalDenoiser`） |
| `RenderCore` | RDG 构建器、渲染目标池等核心渲染基础设施 |
| `RHI` | 底层 GPU 资源（纹理、Buffer、Readback 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 合并 GPU 等待调用为统一 API |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移至 UE_LOGF |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染相关头文件的前向声明 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染目标相关头文件结构 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复批量替换导致的错误后重新提交 |

### 维护评价

- **创建时间**：2024-08-26，约 1 年前从 Experimental 文件夹迁出至正式插件目录
- **Beta 状态**：标记为 Beta，API 和行为可能在后续版本中发生变化
- **更新频率**：最近 3 个月内有多次更新，但主要是编译适配和头文件整理，无功能性改动
- **首次提交**：2024-08-26 的提交是将插件从 Experimental 迁移出来，说明此前已在实验阶段经过验证
- **依赖关系**：依赖 `NNERuntimeORT` 插件，间接依赖 ONNX Runtime
- **平台支持**：Win64、Linux、Mac

⚠️ **Beta 警告**：该插件标记为 Beta，使用前请注意 API 可能不稳定。目前更新以维护性修复为主，功能层面已相对完善。推荐在路径追踪场景中尝试使用，但不建议在生产环境中作为唯一依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [NNE 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE)
- [NNERuntimeORT 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)