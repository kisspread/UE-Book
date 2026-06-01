# RivermaxCore

> Base plugin exposing rivermax to engine

| 属性 | 值 |
|---|---|
| 中文名 | 河流最大核心 |
| 分类 | Virtual Production |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `RivermaxCore` (Runtime), `RivermaxEditor` (Editor), `RivermaxRendering` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-03-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore) | |

## 用途
RivermaxCore 是一个底层插件，用于将 Rivermax 库集成到 Unreal Engine 中。Rivermax 是 NVIDIA 提供的一个高性能网络库，专为专业媒体流传输设计，特别是支持 SMPTE ST 2110 标准。该插件为引擎提供了通过 IP 网络发送和接收符合 ST 2110 标准的未压缩视频流的能力。其核心作用是作为引擎与 Rivermax 库之间的桥梁，处理视频数据的采集、缓冲管理、色彩空间转换以及网络 I/O 操作，是 Unreal Engine 虚拟制片工作流中进行实时高质量视频输入/输出的基础设施。

## 使用场景
- 你在进行虚拟制片，需要从外部专业摄像机或图形工作站实时接收未压缩的 4K/8K 视频流到引擎中，作为虚拟场景的背景或合成源。
- 你需要将 Unreal Engine 的实时渲染画面以广播级质量（如 ST 2110 标准）通过 IP 网络发送给下游的切换台、录制设备或 LED 显示墙处理器。
- 你的工作流涉及远程制作，需要利用 IP 网络替代传统的 SDI 线缆进行多路视频信号的长距离、低延迟传输。

## 蓝图用法
当前查看的 `RivermaxRendering` 模块主要提供底层 GPU 着色器，用于色彩空间转换，不直接暴露蓝图节点。上层的 `RivermaxCore` 和 `RivermaxEditor` 模块（未在此文件中详述）可能提供更高层的蓝图接口来管理输入输出流。核心的着色器功能通过 C++ 在渲染管线中调用。

### 核心节点
| 节点 | 说明 | 所在类 |
|---|---|---|
| 无直接蓝图节点 | 本模块提供底层渲染功能，需通过 C++ 调用 | N/A |

## C++ 用法
`RivermaxRendering` 模块提供了多种计算着色器，用于在 GPU 上高效地将引擎内部的 RGBA 纹理与 Rivermax 库所使用的各种像素格式（如 YUV 4:2:2 8-bit/10-bit, RGB 8-bit/10-bit/12-bit/16-bit float）进行相互转换。

### 头文件引入
```cpp
#include "RivermaxShaders.h"
```

### 基本用法
从 `RivermaxShaders.h` 的声明来看，这些着色器类遵循 UE 的 Global Shader 系统。基本用法是创建着色器参数结构体，分配并设置参数，然后在 RDG (Render Dependency Graph) 中调度。
```cpp
// 引擎源码参考：Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore/Source/RivermaxRendering/Public/RivermaxShaders.h

// 示例：将引擎的 RGBA 纹理转换为 YUV 4:2:2 8-bit 格式，准备通过 Rivermax 发送
FRGBToYUV8Bit422CS::FParameters* Parameters = FRGBToYUV8Bit422CS::AllocateAndSetParameters(
    GraphBuilder,
    SourceTexture,           // 引擎中要发送的渲染目标纹理
    CaptureSize,             // 捕获的分辨率
    SourceViewRect,          // 纹理中要捕获的矩形区域
    OutputSize,              // 输出流的分辨率（应与捕获大小一致或按需缩放）
    ColorTransform,          // RGB 到 YUV 的颜色转换矩阵
    YUVOffset,               // YUV 偏移量（通常为 0）
    bDoLinearToSrgb,         // 是否执行线性到 sRGB 的转换
    OutputBuffer             // 用于存放转换后 YUV 数据的 RDG 缓冲区
);

// 随后，将此着色器任务添加到 RDG 中执行
```

### 进阶用法
实际使用中，这些着色器会集成在 `RivermaxCore` 模块的发送（Output）和接收（Input）管线中。发送时，引擎渲染结果经过 `FRGBToYUV8Bit422CS` 或 `FRGBToRGB10BitCS` 等着色器转换后，写入一个缓冲区，再由 Rivermax 网络层发送。接收时，从 Rivermax 网络层收到的缓冲区数据经过 `FYUV8Bit422ToRGBACS` 或 `FRGB10BitToRGBA10CS` 等着色器转换为引擎可用的纹理。
```cpp
// 引擎源码参考：发送管线可能的集成点
// 1. 分配输出缓冲区（对齐Rivermax要求）
FRDGBufferRef OutputBuffer = GraphBuilder.CreateBuffer(FRDGBufferDesc::CreateStructuredDesc(PixelSizeInBytes, TotalElementCount), TEXT("RivermaxOutputBuffer"));

// 2. 根据目标格式选择着色器并设置参数
if (OutputFormat == ERivermaxPixelFormat::YUV422_8bit)
{
    FRGBToYUV8Bit422CS::FParameters* Params = ...;
    // 添加着色器Pass
    TShaderMapRef<FRGBToYUV8Bit422CS> ComputeShader(GraphBuilder.ShaderMap);
    FComputeShaderUtils::AddPass(GraphBuilder, RDG_EVENTName("ConvertRGBToYUV422_8bit"), ComputeShader, Params, FComputeShaderUtils::GetGroupCount(OutputSize, FIntPoint(8, 8)));
}
else if (OutputFormat == ERivermaxPixelFormat::RGB_10bit)
{
    // ... 使用 FRGBToRGB10BitCS
}

// 3. 执行图形命令，并可能将结果缓冲区映射到 Rivermax 发送内存
GraphBuilder.Execute();
// ... 将 OutputBuffer 映射到 Rivermax 发送包
```

## Demo 示例
以下示例展示了如何在 C++ 中通过 RDG 使用 `FRGBToRGB10BitCS` 着色器将一个纹理转换为打包的 10-bit RGB 格式。

### RivermaxOutputExample.h
```cpp
#pragma once
#include "RivermaxShaders.h"

class FRivermaxOutputExample
{
public:
    /** 将指定纹理转换为打包的 10-bit RGB 格式 */
    static void ConvertTextureToRGB10Bit(
        FRDGBuilder& GraphBuilder,
        FRDGTextureRef SourceTexture,
        const FIntPoint& OutputSize,
        FRDGBufferRef& OutPackedBuffer
    );

private:
    static const int32 OutputBytesPerPixel = 4; // 根据 10-bit 打包格式确定
};
```

### RivermaxOutputExample.cpp
```cpp
#include "RivermaxOutputExample.h"
#include "RivermaxShaders.h"
#include "RenderGraphUtils.h"
#include "ShaderParameterStruct.h"

void FRivermaxOutputExample::ConvertTextureToRGB10Bit(
    FRDGBuilder& GraphBuilder,
    FRDGTextureRef SourceTexture,
    const FIntPoint& OutputSize,
    FRDGBufferRef& OutPackedBuffer)
{
    const uint32 TotalPixelCount = OutputSize.X * OutputSize.Y;
    const uint32 TotalElementCount = TotalPixelCount; // 假设缓冲区描述符单位是像素

    // 1. 创建用于存储转换结果的结构化缓冲区
    // 注意：FRGB10BitBuffer 结构包含 15 个 uint32，对应 16 个 10-bit RGB 像素
    const uint32 BufferElementSize = sizeof(FRivermaxShaders::FRGB10BitBuffer);
    OutPackedBuffer = GraphBuilder.CreateBuffer(
        FRDGBufferDesc::CreateStructuredDesc(BufferElementSize, FMath::DivideAndRoundUp(TotalPixelCount, 16u)),
        TEXT("PackedRGB10BitBuffer"));

    // 2. 设置着色器参数
    TShaderMapRef<FRGBToRGB10BitCS> ComputeShader(GraphBuilder.ShaderMap);
    FRGBToRGB10BitCS::FParameters* ShaderParameters = GraphBuilder.AllocParameters<FRGBToRGB10BitCS::FParameters>();
    ShaderParameters->InputTexture = SourceTexture;
    ShaderParameters->InputSampler = TStaticSamplerState<SF_Bilinear>::GetRHI(); // 采样器状态
    ShaderParameters->CapturedSizeX = OutputSize.X;
    ShaderParameters->OnePixelDeltaX = 1.0f / static_cast<float>(SourceTexture->Desc.GetSize().X);
    ShaderParameters->OnePixelDeltaY = 1.0f / static_cast<float>(SourceTexture->Desc.GetSize().Y);
    ShaderParameters->InputPixelOffsetX = 0.0f;
    ShaderParameters->InputPixelOffsetY = 0.0f;
    ShaderParameters->TotalElementCount = TotalPixelCount;
    ShaderParameters->OutRGB10Buffer = GraphBuilder.CreateUAV(OutPackedBuffer);

    // 3. 计算工作组数量并添加 Pass
    const FIntPoint GroupSize = FComputeShaderUtils::GetGroupCount(OutputSize, FIntPoint(8, 8));
    GraphBuilder.AddPass(
        RDG_EVENTName("ConvertToRGB10Bit"),
        ShaderParameters,
        ERDGPassFlags::Compute,
        [ComputeShader, ShaderParameters, GroupSize](FRHICommandListImmediate& RHICmdList)
        {
            FComputeShaderUtils::Dispatch(RHICmdList, ComputeShader, *ShaderParameters, GroupSize);
        }
    );
}
```

## 模块依赖
从 `RivermaxRendering` 模块的 `Build.cs` 文件分析，其主要依赖为：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口。Rivermax 渲染模块很可能利用 D3D12 的特定功能（如异步计算、缓冲区映射）来实现高性能的流处理。 |

其他如 `Core`, `RenderCore`, `RHI`, `Projects` 等基础依赖已省略。

## 维护状态

### 近期更新
| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为浮点数的警告。 |
| 2026-04-29 | `bef86caa` | Whitespace: followup to migrate UE_LOG to UE_LOGF: Restore newlines in multi-line format strings tha | 空格清理：后续将 UE_LOG 迁移至 UE_LOGF，恢复多行格式字符串中的换行符。 |
| 2026-04-28 | `3348026a` | Rivermax: ANC timecode input, input stream base class refactor, and pixel format unification | Rivermax：增加 ANC 时间码输入、重构输入流基类，并统一像素格式。 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复了在格式化函数中使用作用域枚举可能导致输出乱码的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复了当参数为 64 位时格式说明符仍为 32 位的问题，反之亦然。 |

### 维护评价
RivermaxCore 插件由 Epic Games 官方维护，处于 **活跃维护** 状态。虽然其标记为实验性 (`IsBetaVersion`)，但从最近的提交记录来看，团队仍在持续进行功能增强（如 ANC 时间码支持、输入流重构）、代码质量改进（修复警告、格式化输出）和 bug 修复。创建于 2022 年，年龄约 4 年，是虚拟制片技术栈中相对较新且持续发展的组件。对于需要通过 IP 网络进行专业视频传输的虚拟制片项目，这是一个可靠且在积极演进的基础插件，推荐在相应工作流中使用。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore)
- 官方文档链接未提供
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/VirtualProduction/Rivermax/RivermaxCore/Tests) (推测路径)