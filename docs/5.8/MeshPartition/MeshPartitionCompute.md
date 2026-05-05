# Mesh Partition Compute

> Large-scale mesh authoring system through spatial partitioning, non-destructive modifier editing, and platform-adaptive runtime representations.

| 属性 | 值 |
|---|---|
| 分类 | Mesh Partition |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MeshPartitionCompute` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-23 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition/Source/MeshPartitionCompute) | |

## 用途

`MeshPartitionCompute` 模块是 Mesh Partition 插件的**底层计算核心**。它封装了一系列用于处理大规模网格通道数据的 GPU 计算着色器（Compute Shaders）和渲染着色器（Rendering Shaders）。这些着色器负责执行关键的、计算密集型的任务，例如：
1.  **通道光栅化**：将网格的顶点通道数据（如材质ID、权重等）光栅化到 UV 空间的纹理上。
2.  **边界填充**：对光栅化后的通道纹理进行边界扩展填充，以避免采样时出现接缝。
3.  **MIP 链生成**：为通道纹理生成 MIP 链，支持平台自适应的运行时表示。

该模块的存在是为了将高性能的 GPU 计算逻辑与上层的编辑器工具和运行时逻辑解耦，确保这些核心算法可以在不同的加载阶段（如 `PostConfigInit`）稳定运行，尤其是在从编辑器启动独立构建（Standalone Build）时。

## 使用场景

-   **作为底层依赖**：你通常不会直接使用此模块，而是通过 `MeshPartitionEditor` 或 `MeshPartitionModelingToolset` 等上层模块间接调用其功能。
-   **自定义通道处理**：如果你正在开发自定义的网格通道处理管线，并且需要高性能的 GPU 光栅化和填充算法，可以引用此模块并调用其着色器。
-   **平台自适应纹理生成**：当需要为不同平台（如移动端和主机端）生成不同分辨率或格式的通道纹理时，此模块的 MIP 生成着色器是关键组件。

## 蓝图用法

此模块主要提供底层的 C++ 和着色器接口，**不包含任何直接暴露给蓝图的函数或节点**。其功能通过上层模块（如 `MeshPartitionEditor`）的蓝图接口间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "MeshPartitionChannelRasterizationShaders.h"
```

### 基本用法

此模块的核心是定义一系列全局着色器类。以下示例展示了如何在渲染命令中使用这些着色器参数结构体（实际调用通常封装在 `FRDGBuilder` 中）。

```cpp
// 示例：构建一个用于 UV 域绘制的着色器参数结构体 (概念性代码)
// 来源：基于 Public/MeshPartitionChannelRasterizationShaders.h 中的类定义推断
FMeshPartition_DrawUVDomain_Parameters DrawParams;
DrawParams.VS.InMeshIndices = IndexBufferSRV;
DrawParams.VS.InMeshUVs = UVBufferSRV;
DrawParams.VS.InMeshChannels = ChannelBufferSRV;
DrawParams.VS.InDrawCall = FUintVector4(StartIndex, NumIndices, 0, 0);
DrawParams.VS.InChannelOffset = 0; // 指定要光栅化的通道偏移

// 在渲染图中添加 Pass 并绑定参数
GraphBuilder.AddPass(
    RDG_EVENT_NAME("DrawUVDomain"),
    DrawParams,
    ERDGPassFlags::Raster,
    [DrawParams](FRHICommandListImmediate& RHICmdList)
    {
        // 设置渲染状态，绘制全屏四边形或网格
        // ...
    }
);
```

### 进阶用法

组合使用多个着色器 Pass 来完成一个完整的通道纹理生成流程。

```cpp
// 伪代码：通道纹理生成流程
// 1. 光栅化通道到临时纹理
AddDrawUVDomainPass(GraphBuilder, MeshData, ChannelIndex, TempTexture);

// 2. 使用边界填充着色器填充纹理边缘
FMeshPartition_BorderFillCS::FParameters FillParams;
FillParams.Resolution = TextureSize;
FillParams.Mask = MaskTextureSRV;
FillParams.RWSectionTexture = TempTextureUAV;
TShaderMapRef<FMeshPartition_BorderFillCS> FillShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
GraphBuilder.AddPass(RDG_EVENT_NAME("BorderFill"), FillParams, ERDGPassFlags::Compute, ...);

// 3. 生成 MIP 链
for (int32 MipLevel = 1; MipLevel < NumMips; ++MipLevel)
{
    FMeshPartition_FillPullCS::FParameters MipParams;
    MipParams.SectionMipIn = GetSRVForMip(MipLevel - 1);
    MipParams.SectionMipOut = GetUAVForMip(MipLevel);
    // ... 设置其他参数
    TShaderMapRef<FMeshPartition_FillPullCS> MipShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
    GraphBuilder.AddPass(RDG_EVENT_NAME("GenerateMip_%d", MipLevel), MipParams, ERDGPassFlags::Compute, ...);
}
```

## Demo 示例

由于此模块是底层计算模块，没有独立的、可运行的最小示例。其典型用法体现在 `MeshPartitionEditor` 模块中。要理解其工作方式，建议查看 `MeshPartitionEditor` 模块中调用这些着色器的代码。

一个概念性的集成示例框架如下：

```cpp
// MyCustomChannelProcessor.h
#pragma once
#include "MeshPartitionChannelRasterizationShaders.h"

class FMyCustomChannelProcessor
{
public:
    static void ProcessChannelData(FRHICommandListImmediate& RHICmdList, const FMeshData& Mesh, int32 ChannelIndex, FTextureRHIRef OutputTexture);
};
```

```cpp
// MyCustomChannelProcessor.cpp
#include "MyCustomChannelProcessor.h"
#include "RenderGraphUtils.h"
#include "MeshPartitionChannelRasterizationShaders.h"

void FMyCustomChannelProcessor::ProcessChannelData(FRHICommandListImmediate& RHICmdList, const FMeshData& Mesh, int32 ChannelIndex, FTextureRHIRef OutputTexture)
{
    FRDGBuilder GraphBuilder(RHICmdList);
    
    // ... 创建 RDG 纹理、缓冲区等资源 ...
    
    // 1. 添加光栅化 Pass
    FMeshPartition_DrawUVDomain_Parameters DrawParams;
    // ... 填充 DrawParams ...
    TShaderMapRef<FMeshPartition_DrawUVDomainVS> VertexShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
    TShaderMapRef<FMeshPartition_DrawUVDomainPS> PixelShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
    // ... 添加光栅化 Pass ...

    // 2. 添加边界填充 Pass
    FMeshPartition_BorderFillCS::FParameters FillParams;
    // ... 填充 FillParams ...
    TShaderMapRef<FMeshPartition_BorderFillCS> FillShader(GetGlobalShaderMap(GMaxRHIFeatureLevel));
    GraphBuilder.AddPass(RDG_EVENT_NAME("CustomBorderFill"), FillParams, ERDGPassFlags::Compute,
        [FillShader](FRHICommandListImmediate& RHICmdList, const FMeshPartition_BorderFillCS::FParameters& Parameters)
        {
            FComputeShaderUtils::Dispatch(RHICmdList, FillShader, Parameters, FIntVector(Parameters.Resolution.X, Parameters.Resolution.Y, 1));
        });

    // ... 执行渲染图 ...
    GraphBuilder.Execute();
}
```

## 模块依赖

从模块名称和头文件包含关系推断，此模块依赖以下关键模块：

| 模块 | 用途 |
|---|---|
| `MeshPartition` | 核心运行时数据结构和类型定义 |
| `RenderCore` | 提供渲染命令、RDG（Render Dependency Graph）等核心渲染基础设施 |
| `RHI` | 渲染硬件接口，用于创建和管理 GPU 资源（纹理、缓冲区） |
| `Projects` | 模块加载和插件系统支持 |

## 维护状态

### 近期更新

- 2026-04-24 `44085aba` Mesh Partition: avoid passing hard-coded SM6 argument to GenerateMips. Fixes a crash on projects wit
- 2026-04-24 `473e05b1` Mesh Terrain sculpt layer tools:
- 2026-04-24 `bb6e1b38` Guard against empty UV-Layers and unset element triangles
- 2026-04-23 `2a27739c` Add a path where the for-all-modifiers iteration allows null modifiers to be silently skipped, to av
- 2026-04-23 `dbed6742` Fix broken handling of UV seams at mesh skirt vertices -- take care to copy the UVs from the vertice

### 维护评价

-   **状态**: **实验性/积极开发中**。
-   **分析**: 该模块是 Mesh Partition 这一实验性大型功能的核心组成部分。创建时间非常近，表明它正处于活跃的开发阶段。作为底层计算模块，其稳定性对上层功能至关重要，因此预计会随着主插件功能的完善而持续更新。
-   **风险**: 作为实验性功能，其 API 和内部实现可能会发生 breaking changes。
-   **推荐**: **仅推荐给正在研究或扩展 Mesh Partition 插件功能的开发者**。对于一般项目，应等待该功能从实验阶段毕业。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition/Source/MeshPartitionCompute)
-   [官方文档](https://dev.epicgames.com/community/learning/knowledge-base/nK7J/unreal-engine-introduction-to-mesh-terrain) (Mesh Terrain 概述，可能包含相关概念)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/MeshPartition/Tests) (假设存在，路径需确认)