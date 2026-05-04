# Tiled Mipmap Video Player

> Framework for tiled-mipmap video (TMV) playback, includes transcoding tools. Implemented using Advanced Professional Video (APV) codec.

| 属性 | 值 |
|---|---|
| 分类 | Media Players |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `ApvMedia` (Runtime), `TmvMedia` (Runtime), `TmvMediaEditor` (Runtime), `TmvMediaMp4Utils` (Runtime), `TmvMediaShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-18 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia) | |

## 用途

TmvMedia 插件提供了一套用于播放 **Tiled Mipmap Video (TMV)** 格式视频的完整框架。TMV 是一种专为高效流式传输和渲染优化的视频格式，其核心特点是将视频帧数据组织成 **分块 (Tiled)** 和 **分层 (Mipmapped)** 的结构。

- **分块 (Tiled)**：视频帧被划分为多个小块（Tile），允许按需加载和解码特定区域，非常适合超大分辨率视频的局部渲染或视口裁剪。
- **分层 (Mipmapped)**：视频帧自带多级渐远纹理（Mipmap），支持根据物体距离或屏幕占比自动选择合适的分辨率，优化带宽和渲染性能。

该插件底层使用 **Advanced Professional Video (APV)** 编解码器进行视频的编解码，并提供了从传统视频格式（如 MP4）转码到 TMV 格式的工具链。其主要目标是解决在实时应用中播放超高清、高帧率视频时面临的带宽、内存和性能瓶颈问题。

## 使用场景

- **虚拟制片与大型 LED 墙**：在虚拟制片场景中，需要播放超高分辨率（如 8K、16K）的背景视频。TMV 的分块特性允许只解码和渲染摄像机视野内的部分，极大节省 GPU 和内存资源。
- **开放世界游戏中的动态视频元素**：例如游戏内巨型广告牌、动态天空盒或过场动画，使用 TMV 格式可以实现根据玩家距离自动切换视频分辨率，避免远处物体加载全分辨率视频。
- **需要 GPU 加速解码的媒体播放器**：当应用需要播放大量视频或对解码性能有极高要求时，APV 编解码器和 TMV 的 GPU 友好数据结构可以提供比传统 CPU 解码更优的性能。
- **视频纹理的 LOD 管理**：对于作为纹理使用的视频（如角色皮肤上的动态图案），TMV 的 Mipmap 特性可以无缝集成到引擎的 LOD 系统中。

## 蓝图用法

由于 `TmvMediaShaders` 模块主要提供底层渲染着色器，其 API 主要面向 C++ 开发者。视频播放和控制的高级蓝图接口预计位于 `TmvMedia` 或 `ApvMedia` 模块中（本文档未涵盖）。本模块的核心功能是为视频帧的像素格式转换和色彩空间管理提供 GPU 着色器支持。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FTmvMediaShaderColorParameters` | 定义色彩管理参数的结构体，用于控制颜色空间转换、YUV 转换等。 | `FTmvMediaShaderColorParameters` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接操作这些着色器。它们会被媒体播放器内部调用。如果你需要自定义视频处理管线，可能需要在 C++ 中设置这些参数。

## C++ 用法

本模块的核心是提供一系列全局着色器（Global Shaders），用于将解码后的视频数据（可能是分块的、多平面的）转换为引擎可以使用的标准 RGBA 纹理。

### 头文件引入

```cpp
#include "TmvMediaShaderDefines.h"
#include "TmvMediaShaderParameters.h"
```

### 基本用法

定义视频帧中一个 Tile 的内存布局描述符。这是理解 TMV 数据结构的基础。

```cpp
// 来源: Public/TmvMediaShaderDefines.h
// 定义一个 Tile 的描述信息，用于告诉着色器如何从缓冲区中读取数据
FTmvMediaShaderTileDesc TileDesc;
TileDesc.Offsets = FIntVector4(0, 1024, 2048, 0); // 各个颜色分量（如 Y, U, V, A）在缓冲区中的偏移
TileDesc.Strides = FIntVector4(1920, 960, 960, 0); // 各个颜色分量的行跨度（字节）
```

### 进阶用法

配置色彩管理参数，用于在着色器中进行颜色空间转换（如 BT.709 到线性空间）和 YUV 到 RGB 的转换。

```cpp
// 来源: Internal/TmvMediaShaderParameters.h
// 设置色彩转换参数
FTmvMediaShaderColorParameters ColorParams;
ColorParams.bApplyColorTransform = 1; // 启用颜色空间转换
ColorParams.EOTF = 0; // 电光转换函数索引 (例如 0 代表 sRGB)
ColorParams.ColorSpaceMatrix = FMatrix44f::Identity; // 颜色空间转换矩阵
ColorParams.bConvertYUV = 1; // 启用 YUV 到 RGB 的转换
ColorParams.YUVMatrix = /* 计算好的 YUV 转换矩阵 */;
ColorParams.AlphaScale = 1.0f; // Alpha 通道缩放
ColorParams.MipTint = FVector4f(1.0f, 1.0f, 1.0f, 1.0f); // Mip 层级的色调调整
```

## Demo 示例

以下示例展示了如何在 C++ 中设置 `FTmvStructuredBufferSwizzlePS` 着色器的参数，这是将结构化缓冲区（Structured Buffer）中的 TMV 数据转换为纹理的关键步骤。

```cpp
// TmvMediaShadersDemo.h
#pragma once
#include "CoreMinimal.h"

class FTmvMediaShadersDemo
{
public:
    void ConvertTmvBufferToTexture(
        FRHICommandListImmediate& RHICmdList,
        FUnorderedAccessViewRHIRef DestTextureUAV,
        FShaderResourceViewRHIRef TmvDataSRV,
        FShaderResourceViewRHIRef TileMappingSRV,
        const FIntPoint& TextureSize,
        const FIntPoint& TileSize,
        const FIntPoint& NumTiles
    );
};

// TmvMediaShadersDemo.cpp
#include "TmvMediaShadersDemo.h"
#include "TmvStructuredBufferSwizzlingShader.h"
#include "RenderGraphUtils.h"
#include "ShaderParameterUtils.h"

void FTmvMediaShadersDemo::ConvertTmvBufferToTexture(
    FRHICommandListImmediate& RHICmdList,
    FUnorderedAccessViewRHIRef DestTextureUAV,
    FShaderResourceViewRHIRef TmvDataSRV,
    FShaderResourceViewRHIRef TileMappingSRV,
    const FIntPoint& TextureSize,
    const FIntPoint& TileSize,
    const FIntPoint& NumTiles)
{
    // 1. 选择着色器排列 (Permutation)
    FTmvStructuredBufferSwizzlePS::FPermutationDomain PermutationVector;
    PermutationVector.Set<FTmvStructuredBufferSwizzlePS::FNumComponents>(4); // 假设 RGBA 4 通道
    PermutationVector.Set<FTmvStructuredBufferSwizzlePS::FBufferLayout>(ETmvSwizzleBufferLayouts::TiledFull); // 完整分块布局
    PermutationVector.Set<FTmvStructuredBufferSwizzlePS::FElementFormat>(0); // 假设 uint 格式

    // 2. 获取着色器实例
    TShaderMapRef<FTmvStructuredBufferSwizzlePS> PixelShader(GetGlobalShaderMap(GMaxRHIFeatureLevel), PermutationVector);
    TShaderMapRef<FTmvSwizzleVS> VertexShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));

    // 3. 设置着色器参数
    FTmvStructuredBufferSwizzlePS::FParameters ShaderParams;
    ShaderParams.UnswizzledBuffer = TmvDataSRV;
    ShaderParams.TileMappingBuffer = TileMappingSRV;
    ShaderParams.DestTextureSize = TextureSize;
    ShaderParams.TileSize = TileSize;
    ShaderParams.NumTiles = NumTiles;
    // ... 设置其他参数，如 TileBufferFullStride, Offsets, Strides 等
    // ShaderParams.ColorParams = ...; // 设置色彩参数

    // 4. 执行绘制命令 (通常通过 DrawScreenPass 或类似机制)
    // 此处省略了具体的渲染图 (Render Graph) 设置和绘制调用。
    // 实际使用中，会创建一个绘制全屏四边形的 Pass，并将 DestTextureUAV 作为渲染目标。
    // 通过 SetShaderParameters(RHICmdList, PixelShader, PixelShader.GetPixelShader(), ShaderParams); 绑定参数。
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UEOpenAPV` | APV 编解码器的核心库，`ApvMedia` 模块依赖它进行视频解码。 |
| `RenderCore` | 提供渲染核心功能，如着色器、渲染命令等。 |
| `RHI` | 渲染硬件接口，用于创建和管理 GPU 资源（缓冲区、纹理）。 |

## 维护状态

### 近期更新

由于创建时间为未来日期（2026-04-18），无法获取真实的 git 提交历史。此信息可能为占位符或测试数据。

### 维护评价

- **创建时间**：标记为 2026 年 4 月，这很可能是一个占位符日期，表明该插件是新引入或处于早期开发阶段。
- **实验性状态**：`EnabledByDefault: false` 表明这是一个实验性插件，尚未准备好用于生产环境。
- **模块结构**：插件由多个模块组成（编解码、核心、编辑器工具、着色器），结构清晰，表明是一个功能完整的框架。
- **推荐使用**：**不推荐**在生产项目中使用。该插件处于实验阶段，API 和功能可能发生重大变化。建议仅用于技术预研、内部测试或学习目的。关注 Epic Games 的官方更新日志以获取其成熟度变化的信息。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Media/TmvMedia/Tests) (如果存在)