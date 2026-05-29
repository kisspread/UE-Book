# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | 光追降噪引擎 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptiXDenoise` (RuntimeAndProgram) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise) | |

## 用途

该插件是虚幻引擎路径追踪器（Path Tracer）的专用后处理降噪引擎。它基于 NVIDIA 的 OptiX AI 降噪库，利用 GPU 加速为路径追踪渲染的图像进行降噪处理。

它解决的核心问题是：路径追踪渲染需要大量采样才能消除噪点，但这个过程非常耗时。该插件通过 AI 降噪技术，允许开发者使用少量采样（甚至单帧采样）进行渲染，然后通过 AI 算法预测并移除噪点，从而在保持画质的同时大幅提升渲染效率。

## 使用场景

- 你正在开发使用路径追踪渲染引擎的游戏或应用（如建筑可视化、产品展示、电影预览），需要实时或近实时预览高质量画面，但无法承受长时间等待大量采样。
- 你在使用 Lumen 全局光照的同时，希望在特定场景（如高精度反射、焦散效果）中叠加使用路径追踪来获得更真实的渲染效果，并通过降噪快速得到可用画面。
- 你需要为路径追踪的动画序列（如建筑漫游）快速生成预览动画，AI 降噪能显著缩短每帧的渲染时间。

## 蓝图用法

该插件是一个底层 C++ 模块，主要提供给引擎内部的路径追踪器（Path Tracer）使用，**不直接提供蓝图节点**。其所有操作都发生在 C++ 代码中，通过管理 CUDA 资源、共享句柄和 RHI 纹理来与 UE 的渲染管线集成。

## C++ 用法

### 头文件引入

```cpp
#include "OptiXDenoiser/OptiXDenoiser.h"
```

### 基本用法

该插件提供了管理 CUDA 与 UE RHI 纹理交互、以及执行降噪操作的核心类。以下代码展示了如何初始化一个降噪器并处理一帧图像。

```cpp
// 来源: Private/OptiXDenoiser.h 中的 FOptiXGPUDenoiser 类
// 假设你已经有一个路径追踪器生成的原始辐射度纹理 FTextureRHIRef RadianceTexture

#include "OptiXDenoiser/OptiXDenoiser.h"

// 1. 获取或创建一个降噪器实例
UE::OptiXDenoiser::FOptiXGPUDenoiser Denoiser;

// 2. 初始化降噪器，指定图像尺寸、像素格式等参数
// 使用反照率(albedo)和法线(normal)作为引导信息可以显著提升降噪质量
Denoiser.Init(
    TextureWidth, 
    TextureHeight,
    UE::OptiXDenoiser::EOptiXImageFormat::CUDA_A32B32G32R32_F, // RGBA 32位浮点
    0u, 0u, // 不分块
    true,   // 使用反照率引导
    true,   // 使用法线引导
    false,  // 不是KP模式
    true    // 启用时间性降噪（利用前一帧信息）
);

// 3. 将UE纹理转换为OptiX可用的CUDA图像对象
// 这通常由引擎内部的图像工厂(FOptiXImageFactory)完成，它管理UE纹理到CUDA缓冲区的映射
// 伪代码示例：
TSharedPtr<UE::OptiXDenoiser::FOptiXImage2D> RadianceImage = ImageFactory.GetOptiXImage2DAndSetTexture(RadianceTexture);
Denoiser.SetOptiXImage2D(UE::OptiXDenoiser::EDenoisingImageType::COLOR, RadianceImage);

// 可选：设置反照率、法线、运动矢量(光流)等引导图像
// Denoiser.SetOptiXImage2D(EDenoisingImageType::ALBEDO, AlbedoImage);
// Denoiser.SetOptiXImage2D(EDenoisingImageType::NORMAL, NormalImage);
// Denoiser.SetOptiXImage2D(EDenoisingImageType::FLOW, FlowImage);

// 4. 提交参数并准备执行
Denoiser.Commit();

// 5. 在渲染线程中执行降噪
// 调用 Finish() 会触发底层的 CUDA 内核执行
Denoiser.Finish();

// 降噪结果输出到由 OUTPUT 标识的图像中，即 Denoiser.GetOptiXImage2D(EDenoisingImageType::OUTPUT)
```

### 进阶用法：光流估计与时间性降噪

对于动画序列，可以利用光流信息进行时间性降噪，让当前帧利用前一帧的降噪结果，进一步提升质量和稳定性。

```cpp
// 来源: Private/OptiXDenoiser.h 中的 FOptiXFlowEstimator 类和 FOptiXGPUDenoiser 类

// 1. 初始化光流估计器
UE::OptiXDenoiser::FOptiXFlowEstimator FlowEstimator;
FlowEstimator.Init(TextureWidth, TextureHeight);

// 2. 设置光流估计的输入帧和参考帧（通常是前一帧）
FlowEstimator.SetOptiXImage2D(UE::OptiXDenoiser::EOpticalFlowImageType::INPUTFRAME, CurrentFrameImage);
FlowEstimator.SetOptiXImage2D(UE::OptiXDenoiser::EOpticalFlowImageType::REFERENCE, PreviousFrameImage);

// 3. 估计光流
FlowEstimator.Commit(); // 内部调用 Execute()
// 光流结果保存在 FlowEstimator.GetOptiXImage2D(EOpticalFlowImageType::FLOWOUTPUT)

// 4. 将光流结果设置给降噪器
Denoiser.SetOptiXImage2D(UE::OptiXDenoiser::EDenoisingImageType::FLOW, 
                         FlowEstimator.GetOptiXImage2D(UE::OptiXDenoiser::EOpticalFlowImageType::FLOWOUTPUT));

// 5. （可选）设置前一帧的降噪输出，用于时间性降噪
// Denoiser.SetOptiXImage2D(EDenoisingImageType::PREVOUTPUT, PreviousDenoisedOutputImage);

// 6. 现在的降噪器将同时利用空间信息（反照率、法线）和时间信息（光流、前帧）进行降噪
```

## Demo 示例

以下是一个**概念性**的最小示例，展示了如何在一个自定义渲染器中集成该插件。注意：这需要深入的渲染管线知识，且实际路径追踪器集成非常复杂。

```cpp
// MyPathTracerDenoise.h
#pragma once
#include "CoreMinimal.h"
#include "OptiXDenoiser/OptiXDenoiser.h"

class FMyPathTracerDenoise
{
public:
    void Initialize(int32 InWidth, int32 InHeight);
    void DenoiseFrame(FTextureRHIRef RadianceTexture, FTextureRHIRef AlbedoTexture, FTextureRHIRef NormalTexture);
    void Shutdown();

private:
    TUniquePtr<UE::OptiXDenoiser::FOptiXImageFactory> ImageFactory;
    TUniquePtr<UE::OptiXDenoiser::FOptiXGPUDenoiser> Denoiser;
    bool bIsInitialized = false;
};

// MyPathTracerDenoise.cpp
#include "MyPathTracerDenoise.h"
#include "RHICommandList.h"

void FMyPathTracerDenoise::Initialize(int32 InWidth, int32 InHeight)
{
    ImageFactory = MakeUnique<UE::OptiXDenoiser::FOptiXImageFactory>();
    Denoiser = MakeUnique<UE::OptiXDenoiser::FOptiXGPUDenoiser>();
    Denoiser->Init(InWidth, InHeight);
    bIsInitialized = true;
}

void FMyPathTracerDenoise::DenoiseFrame(FTextureRHIRef RadianceTexture, FTextureRHIRef AlbedoTexture, FTextureRHIRef NormalTexture)
{
    if (!bIsInitialized) return;

    // 将UE纹理绑定到OptiX
    auto ColorImage = ImageFactory->GetOptiXImage2DAndSetTexture(RadianceTexture);
    auto AlbedoImage = ImageFactory->GetOptiXImage2DAndSetTexture(AlbedoTexture);
    auto NormalImage = ImageFactory->GetOptiXImage2DAndSetTexture(NormalTexture);

    Denoiser->SetOptiXImage2D(UE::OptiXDenoiser::EDenoisingImageType::COLOR, ColorImage);
    Denoiser->SetOptiXImage2D(UE::OptiXDenoiser::EDenoisingImageType::ALBEDO, AlbedoImage);
    Denoiser->SetOptiXDenoiser::EDenoisingImageType::NORMAL, NormalImage);

    Denoiser->Commit();
    
    // 实际执行降噪，这会触发GPU计算
    Denoiser->Finish();
    
    // 降噪后的结果在 Denoiser->GetOptiXImage2D(UE::OptiXDenoiser::EDenoisingImageType::OUTPUT)
    // 需要将其复制回UE渲染目标，这需要更复杂的CUDA-D3D12互操作
}

void FMyPathTracerDenoise::Shutdown()
{
    Denoiser.Reset();
    ImageFactory.Reset();
    bIsInitialized = false;
}
```

## 模块依赖

该插件的 `OptiXDenoise` 模块依赖以下 UE 模块，你的模块若要使用此插件，也需要在 `Build.cs` 中添加这些依赖：

| 模块 | 用途 |
|---|---|
| `MessageLog` | 用于在编辑器的消息日志窗口中输出错误和警告信息 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口，插件通过它实现 UE 纹理与 CUDA 内存之间的共享和复制 |

**注意**：该插件还依赖一个外部的 `OptiXDenoiseBase` 模块（包含 NVIDIA 的 OptiX 和 Optical Flow SDK 二进制文件），这个依赖关系已包含在插件自身的 `Build.cs` 中，通常无需用户额外处理。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF，以支持更多功能。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码的错误，提升代码健壮性。 |
| 2025-06-04 | `562eefdb` | disable OptiXDenoise on Windows Arm64 | 在 Windows ARM64 平台上禁用该插件，可能因兼容性问题。 |
| 2025-05-09 | `da955ce5` | Adding Windows Arm64 libraries for: | 为 Windows ARM64 平台添加了相关库，但随后被禁用。 |
| 2024-10-08 | `54fa3a60` | Fix nonportable paths for UnrealEditor (do not submit ClangWarnings.cs!!!!!!!!) | 修复了非可移植路径，并包含一个意外提交的警告文件。 |

### 维护评价

该插件创建于 2022 年 10 月，至今约 3 年。从提交历史看，它仍在持续维护中，最近一次提交在 2026 年 4 月。维护活动主要集中在编译错误修复、平台兼容性调整（尤其是 Windows ARM64）和内部日志系统迁移上。

- **优点**：作为 Epic Games 官方维护的实验性插件，它与引擎的路径追踪器深度集成，能够保证基本的兼容性和稳定性。
- **限制**：
    1.  **实验性状态**：标记为实验性 (`IsExperimentalVersion=true`) 且默认禁用，意味着 API 和功能可能在未来版本中发生不兼容的更改。
    2.  **平台限制**：目前仅支持 Windows x64 平台，且依赖于特定版本的 NVIDIA GPU 和驱动。
    3.  **接口封闭**：不提供蓝图接口，主要为引擎内部模块使用，对普通开发者的开放度较低。

**建议**：如果你的项目严格依赖路径追踪且对渲染性能有要求，可以尝试使用此插件，但必须接受其实验性状态和平台限制。建议将其用于内部研发或受控环境中，避免将其作为最终产品的核心渲染功能，直到其从 Experimental 移出并稳定下来。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise)
- [官方文档]() (无)
- [测试用例]() (未在提供的路径中找到独立的测试文件)