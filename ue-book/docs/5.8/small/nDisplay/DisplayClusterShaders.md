# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资源、示例配置） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), ... (共 27 个) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于驱动大规模 LED 虚拟制片摄影棚、多通道投影模拟器（如 CAVE、穹顶）以及多 PC 集群渲染系统的核心插件。其核心功能是实现**多个渲染 PC（或同一 PC 的多个视口）之间高度同步、低延迟的画面输出**，并能精确地将渲染内容映射到复杂的非平面物理屏幕上（如弯曲的 LED 墙、穹幕）。

它不仅仅是简单的多视口渲染，而是一个完整的集群渲染管理框架，解决了以下关键问题：
1.  **帧同步**：确保所有渲染节点在同一时间点渲染并显示画面，避免撕裂和延迟差异。
2.  **投影映射与扭曲混合**：通过 MPCDI（多投影仪校准数据交换）等标准，将渲染画面无缝贴合到任意形状的物理屏幕几何体上，并进行边缘融合。
3.  **摄像机内视效**：在虚拟制片场景中，将 CG 内容实时合成到 LED 墙前的实景摄像机画面中，并处理色度键、光卡等复杂合成逻辑。
4.  **资源管理**：高效地分配、同步和管理分布在不同机器上的纹理、网格和渲染资源。
5.  **色彩校正**：支持通过 Color Grading 模块对多通道输出进行统一的色彩管理。

## 使用场景

- **虚拟制片 LED 摄影棚**：你需要一个实时驱动整面 LED 墙显示 CG 环境的系统，且需要与实景摄像机画面（ICVFX）精确合成。
- **多投影仪沉浸式环境**：你在搭建一个 CAVE（洞穴自动虚拟环境）或穹幕影院，需要多台 PC 分别驱动多个投影仪，并将它们融合成一个无缝的整体。
- **高性能驾驶/飞行模拟器**：你需要环绕驾驶舱的多个高分辨率显示器同步渲染同一场景的不同视角。
- **大规模显示墙**：你需要将一个高分辨率图像或视频分布到由多个物理显示器拼接而成的大型显示墙上，并保证同步和色彩一致。
- **需要精确输出映射的场景**：你的显示器或投影仪经过了复杂的几何校正，需要导入 MPCDI 等校准文件来匹配渲染输出。

## 蓝图用法

nDisplay 的核心功能主要通过 C++ 接口和数据资产（`.ndisplay` 配置文件）驱动，但也提供了一些用于数据交互的蓝图暴露结构体。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FMPCDIGeometryImportData` | 用于从蓝图向引擎导入 MPCDI 几何数据（顶点网格）的结构体。 | `FMPCDIGeometryImportData` |
| `FMPCDIGeometryExportData` | 用于从引擎向蓝图导出 MPCDI 几何数据（顶点、法线、UV、三角形索引）的结构体。 | `FMPCDIGeometryExportData` |

### 使用示例（蓝图描述）

在蓝图中，你主要通过以下方式与 nDisplay 交互：
1.  **创建/修改 `.ndisplay` 配置资产**：这些资产定义了整个集群的拓扑结构、屏幕布局、视口分配等。这通常在编辑器中通过专用的配置器 UI 完成，而非纯蓝图节点。
2.  **加载和使用 MPCDI 数据**：你可以通过蓝图加载 MPCDI 文件，获取其中的几何数据 (`FMPCDIGeometryImportData`)，或者将引擎内生成的几何数据导出 (`FMPCDIGeometryExportData`) 用于校准流程。
3.  **触发运行时事件**：通过 C++ 暴露的事件（如集群连接状态变化、同步信号等），在蓝图中响应集群系统的状态。

## C++ 用法

nDisplay 的强大功能主要通过 C++ 接口 `IDisplayClusterShaders` 和相关参数结构体来实现。

### 头文件引入

```cpp
#include "IDisplayClusterShaders.h"
#include "DisplayClusterShaderParameters_WarpBlend.h"
#include "DisplayClusterShaderParameters_ICVFX.h"
#include "DisplayClusterShadersTextureUtils.h"
```

### 基本用法

获取 `IDisplayClusterShaders` 模块实例并执行一个基础的扭曲混合（Warp&Blend）渲染操作。这通常在渲染线程中调用。
```cpp
// 来源: Public/IDisplayClusterShaders.h
if (IDisplayClusterShaders::IsAvailable())
{
    IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();
    
    // 准备扭曲混合参数
    FDisplayClusterShaderParameters_WarpBlend WarpBlendParams;
    WarpBlendParams.Src.Set(SourceTexture, SourceRect);
    WarpBlendParams.Dest.Set(DestTexture, DestRect);
    // ... 设置WarpInterface和Context
    
    // 在渲染线程执行
    ShadersModule.RenderWarpBlend_MPCDI(RHICmdList, WarpBlendParams);
}
```

### 进阶用法

使用 `IDisplayClusterShadersTextureUtils` 进行复杂的纹理操作，例如带色彩编码转换和 Alpha 混合的上下文解析。这是一个链式调用 API。
```cpp
// 来源: Public/IDisplayClusterShaders.h, Public/IDisplayClusterShadersTextureUtils.h
// 假设我们在渲染线程
if (IDisplayClusterShaders::IsAvailable())
{
    IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();
    
    // 1. 创建纹理工具实例
    TSharedRef<IDisplayClusterShadersTextureUtils> TextureUtils = ShadersModule.CreateTextureUtils_RenderThread(RHICmdList);
    
    // 2. 配置输入输出纹理
    TextureUtils->SetInput(InputTextureViewport, 0);
    TextureUtils->SetOutput(OutputTextureViewport, 0);
    
    // 3. 设置色彩空间转换
    TextureUtils->SetInputEncoding(FDisplayClusterColorEncoding(EColorSpace::sRGB));
    TextureUtils->SetOutputEncoding(FDisplayClusterColorEncoding(EColorSpace::Rec2020));
    
    // 4. 使用设置进行解析（拷贝+可能的色彩转换）
    FDisplayClusterShadersTextureUtilsSettings Settings;
    Settings.ColorMask = EColorWriteMask::CW_RGBA;
    Settings.Flags = EDisplayClusterShaderTextureUtilsFlags::EnableSmoothAlphaFeather;
    // ... 设置边缘融合参数
    
    TextureUtils->Resolve(Settings);
}
```

## Demo 示例

一个最小的示例，演示如何在渲染线程使用 `IDisplayClusterShadersTextureUtils` 进行一个简单的纹理拷贝操作。

**MyNDisplayDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"

class FMyNDisplayDemo
{
public:
    // 模拟一个渲染过程
    static void RenderDemo(FRHICommandListImmediate& RHICmdList, FRHITexture* SourceTexture, FRHITexture* DestTexture);
};
```

**MyNDisplayDemo.cpp**
```cpp
#include "MyNDisplayDemo.h"
#include "IDisplayClusterShaders.h"
#include "DisplayClusterShadersTextureUtils.h"

void FMyNDisplayDemo::RenderDemo(FRHICommandListImmediate& RHICmdList, FRHITexture* SourceTexture, FRHITexture* DestTexture)
{
    if (!IDisplayClusterShaders::IsAvailable())
    {
        return;
    }

    IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();

    // 创建纹理工具 (在渲染线程)
    TSharedRef<IDisplayClusterShadersTextureUtils> TextureUtils = ShadersModule.CreateTextureUtils_RenderThread(RHICmdList);

    // 定义输入和输出区域（整个纹理）
    FIntRect TextureRect(FIntPoint::ZeroValue, FIntPoint(SourceTexture->GetSizeXYZ().X, SourceTexture->GetSizeXYZ().Y));
    
    // 设置输入纹理
    FDisplayClusterShadersTextureViewport InputViewport(SourceTexture, TextureRect, TEXT("DemoInput"));
    TextureUtils->SetInput(InputViewport);

    // 设置输出纹理
    FDisplayClusterShadersTextureViewport OutputViewport(DestTexture, TextureRect, TEXT("DemoOutput"));
    TextureUtils->SetOutput(OutputViewport);

    // 执行一个默认设置的解析（拷贝）
    FDisplayClusterShadersTextureUtilsSettings DefaultSettings;
    TextureUtils->Resolve(DefaultSettings);
    // TextureUtils 析构时，所有挂起的操作（如 RDG 执行）会自动完成。
}
```

## 模块依赖

要使用 `DisplayClusterShaders` 模块，你的模块需要依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块 |
| `DisplayClusterConfiguration` | 读取和管理 `.ndisplay` 配置文件 |
| `DisplayClusterProjection` | 投影矩阵计算和 MPCDI 支持 |
| `DisplayClusterWarp` | 扭曲网格和扭曲混合逻辑 |
| `MPCDI` | (ThirdParty) MPCDI 格式解析库 |
| `RHI`, `RenderCore` | 底层渲染硬件接口和核心渲染功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 添加 EXR 多层输出支持，增强渲染流程灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并电影管线中的 Alpha 模式，简化相关配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复多渲染图层中的相机命名问题及 MPCDI/ICVFX 着色器中的不透明 Alpha 错误。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，尊重非默认的显示 Gamma 设置，改善色彩准确性。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

nDisplay 是一个成熟且活跃维护的**企业级**插件。虽然创建于 2018 年，但近期（2026 年）仍有密集的功能更新和重要的 bug 修复，表明 Epic 对其持续投入资源以满足虚拟制片行业的需求。

- **活跃维护**：最近更新集中在提升工作流效率（如 Movie Graph 集成）、修复边缘案例下的渲染错误（Alpha、Gamma）以及提高稳定性。
- **核心地位**：它是 Unreal Engine 虚拟制片（In-Camera VFX）工作流的核心支柱之一，被大量专业制作团队依赖。
- **复杂性高**：插件本身包含大量模块和深度渲染技术，学习曲线较陡，建议参考官方文档和示例项目。
- **推荐使用**：对于任何涉及多屏、多PC集群渲染或 LED 墙虚拟制片的项目，nDisplay 是**首选且必不可少**的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/n-display-in-unreal-engine/)