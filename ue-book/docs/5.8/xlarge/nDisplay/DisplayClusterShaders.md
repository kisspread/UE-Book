# nDisplay Shaders

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式显示着色器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、着色器资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterMedia` (Runtime), `SharedMemoryMedia` (Runtime) 等（共 30+ 模块） |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterShaders` 模块是 nDisplay 插件的**渲染核心**，它提供了一套底层、高性能的 GPU 着色器工具集，用于实现分布式渲染所需的各种图像合成与后处理操作。它不仅仅是简单的渲染功能封装，而是为复杂的实时合成管线（如 CAVE、多投影系统、LED 墙渲染）提供了构建块。

该模块主要解决以下核心问题：
1.  **纹理操作与格式转换**：提供统一的纹理拷贝、重采样、颜色空间转换（如 PQ/HLG）和 Mipmap 生成工具。
2.  **投影与合成**：实现核心的 `Warp & Blend`（扭曲与融合）渲染算法，支持 MPCDI 标准配置和自定义 ICVFX（沉浸式摄像机视觉特效）渲染流程。
3.  **后处理管线**：集成模糊、输出重映射、纹理变换（旋转/翻转）等后处理着色器。
4.  **资源管理**：提供 `IDisplayClusterShadersTextureUtils` 这一高级抽象，以链式调用的方式简化复杂的多上下文（如左右眼）纹理处理流程。

简而言之，它是让多个独立 PC 的渲染结果最终能在物理显示设备上无缝、同步、高质量地呈现的“粘合剂”和“画笔”。

## 使用场景

-   **你正在搭建 CAVE 系统**：使用多个投影仪创建沉浸式虚拟环境 → 使用 `RenderWarpBlend_MPCDI` 来校正每个投影仪的畸变并融合边缘重叠区域。
-   **你需要为 LED 墙渲染虚拟场景**：使用 `RenderWarpBlend_ICVFX` 结合 `FDisplayClusterShaderParameters_ICVFX` 来实现摄像机内视锥、色键合成、光照卡片层叠等复杂虚拟制片（Virtual Production）流程。
-   **你在处理 HDR/高动态范围媒体流**：使用 `AddLinearToPQPass` 和 `AddPQToLinearPass` 进行线性色彩空间与 PQ 曲线之间的编码转换。
-   **你需要自定义渲染管线中的纹理操作**：使用 `IDisplayClusterShadersTextureUtils` 工具类，以声明式的方式配置输入输出纹理和处理参数，完成拷贝、重采样等操作。

## 蓝图用法

本模块主要提供底层 C++ API，蓝图可直接暴露的功能有限，但提供了一些用于数据交换的结构体。

### 核心结构体

| 结构体 | 说明 | 所在头文件 |
|---|---|---|
| `FMPCDIGeometryImportData` | 用于从蓝图导入 MPCDI 几何数据（顶点、尺寸） | `MPCDIGeometryData.h` |
| `FMPCDIGeometryExportData` | 用于从蓝图导出处理后的几何数据（顶点、法线、UV、三角形） | `MPCDIGeometryData.h` |

### 使用示例（蓝图描述）

这些结构体主要用于编辑器工具或配置数据传递。在蓝图中，你可以创建一个 `FMPCDIGeometryImportData` 变量，设置其 `Vertices` 数组和 `Width`/`Height`，然后传递给 C++ 函数进行处理。处理结果（如 `FMPCDIGeometryExportData`）可以再返回给蓝图用于显示或进一步操作。

## C++ 用法

### 头文件引入

使用 `DisplayClusterShaders` 模块的核心接口和工具类：
```cpp
#include "IDisplayClusterShaders.h"
#include "IDisplayClusterShadersTextureUtils.h"
#include "DisplayClusterShaderParameters_ICVFX.h"
```

### 基本用法：调用核心渲染接口

以下示例展示了如何获取模块接口并执行一个基础的 MPCDI Warp & Blend 渲染。

```cpp
// 来源于对 IDisplayClusterShaders 接口的典型使用
void RenderViewportWithWarpBlend(FRHICommandListImmediate& RHICmdList)
{
    // 1. 检查并获取 DisplayClusterShaders 模块接口
    if (IDisplayClusterShaders::IsAvailable())
    {
        IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();

        // 2. 准备 WarpBlend 参数（通常由上层模块如 DisplayClusterWarp 组装）
        FDisplayClusterShaderParameters_WarpBlend WarpBlendParams;
        WarpBlendParams.Src.Set(SourceTextureRHI, SourceRect);
        WarpBlendParams.Dest.Set(DestTextureRHI, DestRect);
        WarpBlendParams.WarpInterface = WarpContext; // 从 Warp 模块获取
        // ... 设置其他参数

        // 3. 执行渲染
        bool bSuccess = ShadersModule.RenderWarpBlend_MPCDI(RHICmdList, WarpBlendParams);
    }
}
```

### 进阶用法：使用 TextureUtils 工具链

`IDisplayClusterShadersTextureUtils` 提供了一个流式接口，用于安全、清晰地执行多步纹理操作。

```cpp
// 来源于对 FDisplayClusterShadersTextureUtils 的链式调用模式
void CompositeICVFXLayers(FRHICommandListImmediate& RHICmdList, const IDisplayClusterViewportProxy* ViewportProxy)
{
    // 1. 创建 TextureUtils 实例
    TSharedRef<IDisplayClusterShadersTextureUtils> TextureUtils = 
        IDisplayClusterShaders::Get().CreateTextureUtils_RenderThread(RHICmdList);

    // 2. 定义输入输出上下文（例如：将输入的中间渲染结果输出到最终合成纹理）
    FDisplayClusterShadersTextureViewport InputViewport(InputIntermediateRT, InputRect);
    FDisplayClusterShadersTextureViewport OutputViewport(OutputCompositeRT, OutputRect);

    // 3. 设置输入输出，并配置颜色编码
    TextureUtils
        ->SetInput(InputViewport)
        .SetOutput(OutputViewport)
        .SetInputEncoding(FLinearColor) // 假设输入是线性色彩空间
        .SetOutputEncoding(FDisplayClusterColorEncoding::sRGB()); // 输出到 sRGB

    // 4. 配置处理选项：禁用重采样着色器，仅进行简单拷贝
    FDisplayClusterShadersTextureUtilsSettings Settings;
    Settings.Flags = EDisplayClusterShaderTextureUtilsFlags::DisableResampleShader;

    // 5. 执行解析（拷贝）
    TextureUtils->Resolve(Settings);

    // TextureUtils 在函数结束时自动清理资源
}
```

### 进阶用法：设置 ICVFX 渲染参数

为 ICVFX（虚拟制片内摄像机）渲染准备复杂的合成参数。

```cpp
// 来源于对 FDisplayClusterShaderParameters_ICVFX 结构体的组装
FDisplayClusterShaderParameters_ICVFX PrepareICVFXParameters()
{
    FDisplayClusterShaderParameters_ICVFX ICVFXParams;

    // 1. 设置全局灯光卡片（LightCard）资源
    ICVFXParams.LightCardOver.ViewportId = TEXT("LC_Over_VP");
    ICVFXParams.LightCardGamma = 2.2f;

    // 2. 设置第一个内摄像机（Inner Camera）
    FDisplayClusterShaderParameters_ICVFX::FCameraSettings Camera0;
    Camera0.Resource.ViewportId = TEXT("Camera_VP_0");
    Camera0.ChromakeySource = EDisplayClusterShaderParametersICVFX_ChromakeySource::FrameColor;
    Camera0.ChromakeyColor = FLinearColor::Green;
    Camera0.RenderOrder = 0; // 先渲染，在底层
    Camera0.ViewProjection = CalculateViewProjectionForCamera0(); // 计算视图投影矩阵

    // 3. 设置第二个内摄像机，具有更高渲染顺序
    FDisplayClusterShaderParameters_ICVFX::FCameraSettings Camera1;
    Camera1.Resource.ViewportId = TEXT("Camera_VP_1");
    Camera1.RenderOrder = 1; // 后渲染，在顶层
    // ... 设置其他参数

    // 4. 添加到相机列表并排序
    ICVFXParams.Cameras.Add(Camera0);
    ICVFXParams.Cameras.Add(Camera1);
    ICVFXParams.SortCamerasRenderOrder(); // 按照 RenderOrder 排序

    return ICVFXParams;
}
```

## Demo 示例

一个最小化的 C++ 示例，演示如何集成 `DisplayClusterShaders` 模块来执行基本的后处理模糊操作。

```cpp
// MyNDisplayPostProcess.h
#pragma once
#include "CoreMinimal.h"

class UMyNDisplayComponent;

class FMyNDisplayPostProcess
{
public:
    void ApplyBlurToRenderTarget(UMyNDisplayComponent* InComponent, FRHICommandListImmediate& RHICmdList, FRHITexture* InSourceTexture);
};
```

```cpp
// MyNDisplayPostProcess.cpp
#include "MyNDisplayPostProcess.h"
#include "IDisplayClusterShaders.h" // 引入模块接口
#include "DisplayClusterShaderParameters_PostprocessBlur.h" // 引入模糊参数结构体

void FMyNDisplayPostProcess::ApplyBlurToRenderTarget(UMyNDisplayComponent* InComponent, FRHICommandListImmediate& RHICmdList, FRHITexture* InSourceTexture)
{
    // 检查模块是否可用
    if (!IDisplayClusterShaders::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("DisplayClusterShaders module is not loaded."));
        return;
    }

    // 获取着色器模块接口
    IDisplayClusterShaders& ShadersModule = IDisplayClusterShaders::Get();

    // 准备模糊参数
    FDisplayClusterShaderParameters_PostprocessBlur BlurParams;
    BlurParams.Mode = EDisplayClusterShaderParameters_PostprocessBlur::Gaussian; // 使用高斯模糊
    BlurParams.KernelRadius = 3; // 模糊半径
    BlurParams.KernelScale = 1.5f; // 模糊强度

    // 假设我们有一个用于输出的 RTT
    FRHITexture* OutputTexture = ... // 从组件或其他地方获取

    // 调用模糊渲染函数
    bool bSuccess = ShadersModule.RenderPostprocess_Blur(
        RHICmdList,
        InSourceTexture, // 源纹理
        OutputTexture,   // 目标纹理（需为 RenderTargetable）
        BlurParams
    );

    if (bSuccess)
    {
        // 后处理应用成功
    }
}
```

## 模块依赖

`DisplayClusterShaders` 模块依赖于多个其他 nDisplay 内部模块和引擎模块。对于使用者（开发者）来说，你的项目模块需要依赖 `DisplayClusterShaders` 模块本身即可。该模块内部已经封装了所需的所有底层依赖。

要使用此模块，在你的模块 `.Build.cs` 文件中添加：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DisplayClusterShaders" // 你的模块需要依赖它
    // 其他你需要的模块...
});
```

该插件无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 在 MovieGraph 和 nDisplay 中支持 EXR 多图层格式。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 为 MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend 中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知的摄像机命名问题，并修复了 MPCDI/ICVFX 着色器中不透明 alpha 的问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，尊重非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**维护状态：活跃维护**

-   **创建时间**：2018年，是 Unreal Engine 中成熟的插件。
-   **更新频率**：近期（2026年5月）有非常密集的功能更新和错误修复，表明该模块仍在被积极开发和改进，以适应最新的 MovieGraph、虚拟制片等工作流。
-   **活跃度**：非常活跃。最近的更新涉及新功能（EXR 多图层）、现有功能优化（WarpBlend 模式合并）以及重要的渲染 bug 修复（alpha 处理、闪烁问题）。
-   **限制与已知问题**：由于其复杂性，可能需要深入了解 nDisplay 的整体架构才能完全驾驭。部分功能（如 ICVFX）配置繁琐。
-   **推荐使用**：**强烈推荐**。如果你的项目涉及到 nDisplay 分布式渲染、虚拟制片或多投影系统，这个模块是必不可少的基石。它得到了 Epic 的持续维护和更新，性能与功能都在不断进化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.0/en-US/n-display-in-unreal-engine/) (UE5 nDisplay 整体文档)