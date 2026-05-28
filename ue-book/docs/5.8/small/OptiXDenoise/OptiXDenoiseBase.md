# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | OptiX 降噪引擎 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptiXDenoise` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise) | |

## 用途

此插件为 Unreal 的路径追踪器（Path Tracer）提供了一个基于 NVIDIA OptiX AI 降噪库的高性能降噪引擎。它解决的核心问题是：**路径追踪渲染在有限的采样次数下会产生大量噪点，而此插件利用 AI 算法和时间信息，可以在极低的采样数下生成接近最终渲染质量的图像，从而大幅提升渲染效率。**

该插件主要提供两个核心功能：
1.  **光流估计（Optical Flow Estimation）**：计算相邻帧之间的像素运动信息，用于时间降噪。
2.  **空间与时间降噪（Spatial and Temporal Denoising）**：利用辐射度（Radiance）、反照率（Albedo）、法线（Normal）以及光流（Flow）等辅助信息，对渲染图像进行降噪。

它是一个**底层引擎模块**，不直接暴露给蓝图，需要通过 C++ 代码与 Unreal 的渲染模块集成使用。

## 使用场景

-   **建筑可视化/产品渲染**：需要快速获得高质量预览，但渲染时间有限。
-   **电影/动画预览**：在序列渲染中，使用极低采样（如每帧 1-4 SPP）进行预览，利用时间降噪获得连贯且平滑的图像。
-   **需要 NVIDIA GPU 加速降噪的场景**：该插件依赖 CUDA 和 OptiX 库，因此必须运行在支持 CUDA 的 NVIDIA GPU 上（目前仅支持 Win64 x64 平台）。

## 蓝图用法

无。此插件是底层渲染引擎模块，其功能通过 C++ API 调用，未暴露任何 `BlueprintCallable` 节点。

## C++ 用法

该插件的核心 API 围绕两个主要类展开：`FOptiXDenoiseContext`（降噪上下文）和 `FOpticalFlowContext`（光流上下文）。

### 头文件引入

```cpp
#include "OptiXDenoiseBase.h"
```

### 基本用法（来自核心 API 分析）

以下示例展示了如何初始化一个降噪上下文并执行一次降噪操作。

```cpp
// 假设已经有一个有效的 CUDA 上下文 CUcontext 和流 CUstream
CUcontext CudaContext = /* ... */;
CUstream CudaStream = /* ... */;

// 1. 创建降噪上下文并初始化
FOptiXDenoiseContext DenoiseContext;
DenoiseContext.InitOptiX();
DenoiseContext.CreateContext(CudaContext, /*日志回调*/ nullptr, /*日志级别*/ 0);

// 2. 初始化降噪器（启用法线、反照率引导，启用时间模式）
DenoiseContext.InitializeDenoiser(/*GuideNormal=*/true, /*GuideAlbedo=*/true, /*TemporalMode=*/true);

// 3. 计算所需的内存资源（State 和 Scratch）
const uint32 Width = 1920;
const uint32 Height = 1080;
DenoiseContext.ComputeMemoryResource(Width, Height);
size_t StateSize = DenoiseContext.GetStateSizeInBytes();
size_t ScratchSize = DenoiseContext.GetWithoutOverlapScratchSizeInBytes(); // 或 GetWithOverlapScratchSizeInBytes()

// 在 CUDA 上分配内存 (示例)
CUdeviceptr StateBuffer, ScratchBuffer;
cuMemAlloc(&StateBuffer, StateSize);
cuMemAlloc(&ScratchBuffer, ScratchSize);

// 4. 设置降噪器
DenoiseContext.SetupDenoiser(CudaStream, Width, Height, StateBuffer, StateSize, ScratchBuffer, ScratchSize);

// 5. 配置输入引导层和数据层
FOptiXImageData InputRadianceData, AlbedoData, NormalData, FlowData, OutputDenoisedData;
// ... 初始化以上 FOptiXImageData 结构 ...

DenoiseContext.SetGuideLayerAlbedo(AlbedoData)
    .SetGuideLayerNormal(NormalData)
    .SetGuideLayerFlow(FlowData) // 时间降噪需要
    .SetLayerInput(InputRadianceData)
    .SetLayerOutput(OutputDenoisedData);

// 设置混合因子 (0.0 = 全降噪，1.0 = 不降噪)
DenoiseContext.SetBlendFactor(0.0f);

// 6. 执行降噪
EOptiXDenoiseResult Result = DenoiseContext.InvokeOptiXDenoise(
    CudaStream,
    StateBuffer, StateSize,
    ScratchBuffer, ScratchSize,
    /*Overlap=*/0, /*TileWidth=*/0, /*TileHeight=*/0
);

if (Result != 0) {
    // 错误处理
}

// 7. 清理资源
DenoiseContext.Destroy();
cuMemFree(StateBuffer);
cuMemFree(ScratchBuffer);
```

### 进阶用法（时间降噪）

对于时间降噪，需要额外管理内部引导层和上一帧的信息。

```cpp
// ... 在循环的每帧中 ...

// 初始化时，需要更多的内存
size_t InternalGuideLayerSize = DenoiseContext.GetInternalGuideLayerPixelSizeInBytes() * Width * Height;
CUdeviceptr PrevInternalGuideLayer, CurrInternalGuideLayer;
cuMemAlloc(&PrevInternalGuideLayer, InternalGuideLayerSize);
cuMemAlloc(&CurrInternalGuideLayer, InternalGuideLayerSize);

// 设置内部引导层
FOptiXImageData PrevGuideLayerImage, CurrGuideLayerImage;
PrevGuideLayerImage.Data = PrevInternalGuideLayer;
PrevGuideLayerImage.Width = Width;
PrevGuideLayerImage.Height = Height;
// ... 设置其他格式信息 ...
CurrGuideLayerImage.Data = CurrInternalGuideLayer;
// ... 设置其他格式信息 ...

DenoiseContext.SetPreviousOutputInternalGuideLayer(PrevGuideLayerImage);
DenoiseContext.SetOutputInternalGuideLayer(CurrGuideLayerImage);

// 设置上一帧的降噪输出作为当前帧的“上一帧输出”
DenoiseContext.SetLayerPreviousOutput(LastFrameDenoisedOutputData);

// 执行降噪后，交换内部引导层指针，为下一帧做准备
std::swap(PrevInternalGuideLayer, CurrInternalGuideLayer);

// ... 在渲染循环结束或插件关闭时 ...
DenoiseContext.Destroy();
cuMemFree(PrevInternalGuideLayer);
cuMemFree(CurrInternalGuideLayer);
```

## Demo 示例

由于此插件深度依赖 CUDA 和 OptiX 运行时，且需要与 Unreal 的路径追踪器紧密集成，无法提供一个独立的、可编译的最小示例。典型使用场景是在 Unreal Engine 的 `FPathTracing` 渲染器（位于 `RenderCore` 或 `Renderer` 模块）中集成此插件的 API。

## 模块依赖

要使用此插件，你的模块需要依赖以下独特的模块（常见的 Core/Engine 等依赖已省略）：

| 模块 | 用途 |
|---|---|
| `OptiXDenoise` | 提供降噪和光流计算的核心 API。 |
| `D3D12RHI` | 用于与 DirectX 12 渲染硬件接口交互，获取纹理表面对象。 |
| `MessageLog` | 用于输出日志消息。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至 UE_LOGF。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复了不可达代码的编译错误。 |
| 2025-06-04 | `562eefdb` | disable OptiXDenoise on Windows Arm64 | 禁用了 Windows Arm64 架构下的插件支持。 |
| 2025-05-09 | `da955ce5` | Adding Windows Arm64 libraries for: | 尝试添加 Windows Arm64 的库文件（后被上一步禁用）。 |
| 2024-10-08 | `54fa3a60` | Fix nonportable paths for UnrealEditor (do not submit ClangWarnings.cs!!!!!!!!) | 修复了编辑器相关的不可移植路径问题，并强调禁止提交特定文件。 |

### 维护评价

该插件创建于 2022 年 10 月，已存在约 3 年。从提交历史看，最近一年（2025-2026）的更新主要集中在**编译错误修复和平台适配**（如 Arm64 禁用），而非新功能的添加。最后一次实质性更新可能更早。

**综合评价**：
- **实验性**：明确标记为实验性，且默认禁用。
- **维护状态**：**维护不活跃**。近期无功能性更新，主要活动是维持其能在新引擎版本上编译。
- **推荐使用**：仅推荐给需要深度集成 NVIDIA AI 降噪至 Unreal 路径追踪器的高级开发者，并愿意接受其作为实验性功能且可能不再得到积极维护的风险。普通用户应优先考虑引擎内置的其他降噪方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise)
- [官方文档](https://docs.unrealengine.com/) （插件无专属文档页）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) （此插件测试可能位于引擎测试目录中）