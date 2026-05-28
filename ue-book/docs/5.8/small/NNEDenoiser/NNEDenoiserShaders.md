# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（计算着色器、降噪模型配置） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是基于 UE 神经网络引擎（NNE）实现的**路径追踪器实时降噪插件**。它解决了路径追踪渲染中光线采样数不足导致的噪声问题——通过预训练的神经网络模型对低采样渲染结果进行推断，输出高质量的去噪画面。

该插件的完整管线包括：

1. **预处理阶段**（GPU 计算着色器）：自动曝光计算、输入缓冲区映射（Texture ↔ Buffer 通道重排）、Transfer Function 变换（OIDN 风格）
2. **神经网络推断阶段**（通过 NNE + NNERuntimeORT）：将预处理后的张量送入 ONNX Runtime 推断引擎
3. **后处理阶段**（GPU 计算着色器）：将推断结果映射回渲染纹理

NNEDenoiserShaders 模块提供了上述管线中所有 GPU 计算着色器，是该插件的底层渲染支撑。

## 使用场景

- 你使用 **Path Tracer** 进行离线或实时渲染，但采样数较低导致画面有明显噪声 → 启用 NNEDenoiser 进行神经网络降噪
- 你需要在 **Movie Render Queue** 中快速输出高质量路径追踪结果 → NNEDenoiser 可以在低采样下获得接近高采样的画质
- 你正在开发自定义的 NNE 推断管线，需要 Texture ↔ Buffer 映射着色器 → NNEDenoiserShaders 提供了通用的映射拷贝着色器

## 蓝图用法

NNEDenoiser 主要通过路径追踪器设置自动集成，无需直接的蓝图调用。降噪功能通过以下方式启用：

1. 在 **项目设置 → 渲染 → Path Tracing** 中启用降噪
2. 通过控制台命令 `r.PathTracing.Denoiser` 控制降噪器类型
3. NNEDenoiser 依赖 NNERuntimeORT 插件，确保该插件已启用

## C++ 用法

NNEDenoiserShaders 模块的所有着色器均位于 `UE::NNEDenoiserShaders::Internal` 命名空间下，属于内部实现，不建议外部直接使用。以下是模块内部着色器的简要说明：

### 内部着色器概览

| 计算着色器 | 用途 |
|---|---|
| `FTextureBufferMappedCopyCS` | 纹理到缓冲区的通道映射拷贝 |
| `FBufferTextureMappedCopyCS` | 缓冲区到纹理的通道映射拷贝 |
| `FAutoExposureDownsampleCS` | 自动曝光下采样（分 bin） |
| `FAutoExposureReduceCS` | 自动曝光归约（求和/计数） |
| `FAutoExposureReduceFinalCS` | 自动曝光最终归约 |
| `FTransferFunctionOidnCS` | OIDN 风格的前向/逆向传递函数 |
| `FDefaultIOProcessCS` | 默认 I/O 处理（Color/Albedo/Normal/Flow/Output） |

### 头文件引入

如需在模块内引用 NNEDenoiserShaders 的公共头文件：

```cpp
#include "NNEDenoiserShadersAutoExposureCS.h"
#include "NNEDenoiserShadersMappedCopyCS.h"
#include "NNEDenoiserShadersTransferFunctionOidnCS.h"
#include "NNEDenoiserShadersDefaultIOProcessCS.h"
```

### 着色器参数结构（内部用法）

每个着色器均使用 `SHADER_USE_PARAMETER_STRUCT` 声明，通过 `FParameters` 结构传递参数。以通道映射拷贝为例：

```cpp
// 来源: Engine/Plugins/NNE/NNEDenoiser/Source/NNEDenoiserShaders/Internal/NNEDenoiserShadersMappedCopyCS.h
using namespace UE::NNEDenoiserShaders::Internal;

// 纹理到缓冲区的映射拷贝
FTextureBufferMappedCopyCS::FParameters TextureToBufferParams;
TextureToBufferParams.Width = Width;
TextureToBufferParams.Height = Height;
TextureToBufferParams.InputTexture = InputTexture;
TextureToBufferParams.OutputBuffer = OutputBufferUAV;
// 通道映射: 每个 FIntVector4 表示 (输出通道, 输入通道, 未用, 未用)
TextureToBufferParams.OutputChannel_InputChannel_Unused_Unused[0] = FIntVector4(0, 0, 0, 0);
TextureToBufferParams.OutputChannel_InputChannel_Unused_Unused[1] = FIntVector4(1, 1, 0, 0);
TextureToBufferParams.OutputChannel_InputChannel_Unused_Unused[2] = FIntVector4(2, 2, 0, 0);
```

### 排列组合（Permutation）

着色器支持多种排列维度，编译时自动生成变体：

```cpp
// 来源: NNEDenoiserShadersMappedCopyCS.h
// 输入/输出数据类型排列（Half 或 Float）
using FInputDataType = FTextureBufferMappedCopyCS::FInputDataType;
using FOutputDataType = FTextureBufferMappedCopyCS::FOutputDataType;
using FNumMappedChannels = FTextureBufferMappedCopyCS::FNumMappedChannels;

FTextureBufferMappedCopyCS::FPermutationDomain PermutationVector;
PermutationVector.Set<FInputDataType>(EDataType::Float);
PermutationVector.Set<FOutputDataType>(EDataType::Half);
PermutationVector.Set<FNumMappedChannels>(3); // 映射 3 个通道
```

### 数据类型定义

```cpp
// 来源: NNEDenoiserShadersMappedCopyCS.h
enum class EDataType : uint8
{
    None = 0,
    Half = 3,
    Float,
    MAX
};
// 对应 NNE 张量数据类型 ENNETensorDataType
```

## Demo 示例

以下展示如何使用 NNEDenoiserShaders 模块中的 MappedCopy 计算着色器进行纹理到缓冲区的通道映射拷贝：

```cpp
// NNEDenoiserDemo.h
#pragma once

#include "RenderGraphUtils.h"
#include "ShaderParameterStruct.h"

class FNNEDenoiserDemo
{
public:
    // 将纹理数据映射拷贝到缓冲区，支持通道重排
    static void TextureToBufferMappedCopy(
        FRDGBuilder& GraphBuilder,
        FRDGTextureRef InputTexture,
        FRDGBufferUAVRef OutputBufferUAV,
        int32 Width,
        int32 Height,
        int32 NumChannels,
        const FIntVector4* ChannelMapping);
};
```

```cpp
// NNEDenoiserDemo.cpp
#include "NNEDenoiserDemo.h"
#include "NNEDenoiserShadersMappedCopyCS.h"
#include "RenderGraphUtils.h"

using namespace UE::NNEDenoiserShaders::Internal;

void FNNEDenoiserDemo::TextureToBufferMappedCopy(
    FRDGBuilder& GraphBuilder,
    FRDGTextureRef InputTexture,
    FRDGBufferUAVRef OutputBufferUAV,
    int32 Width,
    int32 Height,
    int32 NumChannels,
    const FIntVector4* ChannelMapping)
{
    // 选择着色器排列: Float 输入, Float 输出, 指定通道数
    FTextureBufferMappedCopyCS::FPermutationDomain PermutationVector;
    PermutationVector.Set<FTextureBufferMappedCopyCS::FInputDataType>(EDataType::Float);
    PermutationVector.Set<FTextureBufferMappedCopyCS::FOutputDataType>(EDataType::Float);
    PermutationVector.Set<FTextureBufferMappedCopyCS::FNumMappedChannels>(NumChannels);

    TShaderMapRef<FTextureBufferMappedCopyCS> ComputeShader(
        GetGlobalShaderMap(GMaxRHIFeatureLevel), PermutationVector);

    // 设置着色器参数
    FTextureBufferMappedCopyCS::FParameters* PassParameters =
        GraphBuilder.AllocParameters<FTextureBufferMappedCopyCS::FParameters>();
    PassParameters->Width = Width;
    PassParameters->Height = Height;
    PassParameters->InputTexture = InputTexture;
    PassParameters->OutputBuffer = OutputBufferUAV;

    // 填充通道映射（最多支持 4 通道）
    const int32 MaxChannels = FMappedCopyConstants::MAX_NUM_MAPPED_CHANNELS;
    for (int32 i = 0; i < FMath::Min(NumChannels, MaxChannels); ++i)
    {
        PassParameters->OutputChannel_InputChannel_Unused_Unused[i] = ChannelMapping[i];
    }

    // 计算线程组数量并分派
    const FIntVector GroupCount = FComputeShaderUtils::GetGroupCount(
        FIntPoint(Width, Height), FIntPoint(FMappedCopyConstants::THREAD_GROUP_SIZE));

    FComputeShaderUtils::AddPass(
        GraphBuilder,
        RDG_EVENTName("NNEDenoiser::MappedCopyTextureToBuffer"),
        ComputeShader, PassParameters, GroupCount);
}
```

## 模块依赖

NNEDenoiserShaders 是一个底层着色器模块，NNEDenoiser 的主要模块依赖关系如下：

| 模块 | 用途 |
|---|---|
| `NNEDenoiserShaders` | GPU 计算着色器（预处理/后处理） |
| `NNERuntimeORT` | ONNX Runtime 神经网络推断引擎（插件依赖） |
| `NNE` | UE 神经网络引擎核心接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 替换旧版 GPU 同步 API 为新的统一接口 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移到新格式化接口 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 补充渲染头文件的前置声明和包含 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 拆分渲染头文件，添加显式包含 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复错误的查找替换操作 |

### 维护评价

NNEDenoiser 创建于 2024 年 8 月，是一个较新的插件（约 1 年）。近期更新均为**引擎级维护改动**（头文件拆分、API 迁移、日志格式化），而非功能性的降噪算法更新。这表明插件功能已基本稳定。

⚠️ **注意**：该插件标记为 `IsBetaVersion = true`，意味着 API 可能在未来版本中发生变化。尽管默认启用，但在生产环境中使用时需谨慎评估稳定性。

该插件**仍在维护中**，依赖 NNERuntimeORT 提供的 ONNX 推理能力，是 UE5 路径追踪降噪的核心组件。推荐在使用 Path Tracer 时启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [NNEDenoiserShaders Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/NNE/NNEDenoiser/Source/NNEDenoiserShaders/NNEDenoiserShaders.Build.cs)
- [NNEDenoiser Build.cs](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/NNE/NNEDenoiser/Source/NNEDenoiser/NNEDenoiser.Build.cs)
- [NNERuntimeORT 插件（依赖）](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNERuntimeORT)