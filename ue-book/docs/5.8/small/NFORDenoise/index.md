# NFORDenoise

> Spatial-temporal denoising engine for the Unreal Path Tracer (mainly used with MRQ). It denoises each pixel based on the surrounding patches in space and time in all directions. The algorithm is mainly inspired by Nonlinearly Weighted First-order Regression (NFOR) for Denoising Monte Carlo Renderings.

| 属性 | 值 |
|---|---|
| 中文名 | 路径追踪降噪 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `NFORDenoise` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-04-02 |
| 年龄标签 | 👴 老古董（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NFORDenoise) | |

## 用途

NFORDenoise 是一个为 Unreal Engine 的路径追踪器（Path Tracer）设计的**实验性、高质量的时空降噪引擎**，主要与电影渲染队列（MRQ）配合使用。它并非一个实时降噪方案，而是用于离线渲染管线，旨在大幅减少路径追踪渲染（尤其是低采样率下）产生的蒙特卡洛噪声。

该插件的核心价值在于其算法的先进性。它基于“非线性加权一阶回归”（NFOR）理论，通过对每个像素周围**空间上和时间上**的邻近块（Patch）进行分析和加权平均来重建干净图像。这意味着它不仅利用当前帧的空间信息，还能利用相邻帧（历史帧和未来帧）的信息，从而特别适合处理相机缓慢移动的场景，显著提升渲染结果的**时间稳定性**，避免画面闪烁。

简单来说，当您使用 MRQ 渲染电影级画质的路径追踪动画时，无需等待极高采样数（需要极长渲染时间）就能获得平滑、干净的画面，NFORDenoise 可以在较低的采样数下，通过后处理算法智能地“猜”并填补缺失的信息。

## 使用场景

- **电影级渲染与过场动画**：使用电影渲染队列（MRQ）渲染带有复杂光照、反射、全局光照的路径追踪序列时，使用 NFORDenoise 可以在可接受的时间内获得接近无噪点的最终帧。
- **产品可视化与建筑效果图**：渲染静态或缓慢移动镜头的高品质静态图或动画，追求极致的画面平滑度。
- **需要高时间稳定性的动画**：对于相机缓慢平移、旋转的场景，该降噪器能有效保持帧与帧之间的视觉一致性，避免降噪带来的闪烁或抖动。

## 蓝图用法

该插件**不提供直接的蓝图节点**供调用。其所有功能均通过**控制台变量（Console Variables, CVars）** 进行配置和开关控制。您需要在项目设置、命令行参数或通过游戏内控制台输入这些命令。

### 核心控制台变量

| 变量 | 说明 | 默认值 |
|---|---|---|
| `r.PathTracing.SpatialDenoiser.Type` | **启用降噪器的关键开关**。设置为 `1` 以使用 NFOR 降噪器。 | `0` (关闭) |
| `r.NFOR.FrameCount` | 控制降噪使用的帧历史范围。`0` 为单帧（预览用），`1`/`2`/`3` 代表使用前后各 N 帧。例如 `2` 表示使用 5 帧历史（前 2 + 当前 + 后 2）。 | `0` |
| `r.PathTracing.Denoiser` | 通用降噪器开关。可以先设为 `0` 禁用，修改参数后再设为 `1` 重新应用。 | `1` |
| `r.NFOR.NonLocalMean.Radiance.PatchDistance` | 辐照度（Radiance）滤波的搜索半径。值越大，降噪越强，但计算量更大。 | `9` |
| `r.NFOR.NonLocalMean.Radiance.PatchSize` | 辐照度滤波的块大小。 | `3` |
| `r.NFOR.NonLocalMean.Feature.PatchDistance` | 特征（如法线、深度）滤波的搜索半径。 | `5` |
| `r.NFOR.NonLocalMean.Feature.PatchSize` | 特征滤波的块大小。 | `3` |

### 使用示例（蓝图或控制台操作）

1.  在项目的默认引擎配置中，或者通过编辑器内的控制台（`~`键），输入：
    ```ini
    r.PathTracing.SpatialDenoiser.Type 1
    r.NFOR.FrameCount 2
    ```
    这启用了降噪器，并设定使用 5 帧历史进行降噪。
2.  在 MRQ 设置中，确保开启了**参考运动模糊（Reference Motion Blur）** 并使用了**时间采样（Temporal Samples）**。
3.  如果需要在编辑器中调整降噪强度，可以修改相关参数后，通过开关降噪器来刷新：
    ```ini
    r.PathTracing.Denoiser 0
    r.NFOR.NonLocalMean.Radiance.PatchDistance 12
    r.PathTracing.Denoiser 1
    ```

## C++ 用法

### 头文件引入

```cpp
#include "NFORDenoise.h"
#include "NFORDenoiseCS.h" // 核心降噪着色器和参数定义
```

### 基本用法

从源码分析来看，NFORDenoise 主要是一个**渲染器后端模块**，其核心逻辑是作为 Path Tracer 渲染管线中的一个降噪 Pass。对于插件使用者而言，直接 C++ 调用的情况较少，更多是**配置**和**集成**。但对于希望深入定制或调试渲染管线的开发者，可以参考其内部结构。

以下是一个概念性的示例，展示了如何在自己的渲染 Pass 中查看或获取降噪器状态（基于源码推断，非官方示例）：

```cpp
// 假设在自定义的渲染Pass中
#include "SceneRendering.h"
#include "NFORDenoiseCS.h"

void MyRenderPass(FRHICommandListImmediate& RHICmdList, const FSceneView& View)
{
    // 检查当前视图是否应用了 NFOR 降噪器
    // 实际实现需要在更底层的 PathTracing 渲染逻辑中
    const bool bNFORDenoiserEnabled = IConsoleManager::Get().FindTConsoleVariableDataInt(TEXT("r.PathTracing.SpatialDenoiser.Type"))->GetValueOnRenderThread() == 1;

    if (bNFORDenoiserEnabled)
    {
        // 获取当前帧降噪器使用的历史帧数量
        const int32 FrameCount = NFORDenoise::GetFrameCount(View);
        const int32 DenoisingFrameIndex = NFORDenoise::GetDenoisingFrameIndex(View);

        UE_LOG(LogTemp, Log, TEXT("NFOR Denoiser active. Using %d frames, current index: %d"), FrameCount, DenoisingFrameIndex);
    }
}
```

### 进阶用法

插件的 Private 目录下包含更复杂的数学和计算逻辑，如 **CPU 端的加权最小二乘回归求解器** (`FWeightedLSRDesc`, `SolveWeightedLSRCPU`)。这通常用于调试或作为 GPU 计算的备用方案，普通开发者无需直接使用。

## Demo 示例

以下是一个最小化的场景，演示如何在自定义的渲染通道（Render Pass）中与 NFOR 降噪器的状态进行交互。这并非一个完整的游戏功能示例，而是展示了如何从 C++ 侧感知和控制该降噪器。

**MyNFORDebugPass.h**
```cpp
// MyNFORDebugPass.h
#pragma once

#include "CoreMinimal.h"
#include "Renderer/Private/SceneRendering.h"

class FMyNFORDebugPass
{
public:
    static void Execute(FRHICommandListImmediate& RHICmdList, const FSceneViewFamily& ViewFamily);
};
```

**MyNFORDebugPass.cpp**
```cpp
// MyNFORDebugPass.cpp
#include "MyNFORDebugPass.h"
#include "NFORDenoise.h"
#include "IConsoleManager.h"

void FMyNFORDebugPass::Execute(FRHICommandListImmediate& RHICmdList, const FSceneViewFamily& ViewFamily)
{
    if (ViewFamily.Views.Num() == 0) return;

    const FSceneView& View = *ViewFamily.Views[0];

    // 读取 NFOR 降噪器的核心开关 CVar
    static IConsoleVariable* CVarSpatialDenoiserType = IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracing.SpatialDenoiser.Type"));
    if (CVarSpatialDenoiserType && CVarSpatialDenoiserType->GetInt() == 1)
    {
        // 降噪器已启用，可以获取其内部信息用于调试
        int32 FrameCount = NFORDenoise::GetFrameCount(View);
        int32 CurrentIndex = NFORDenoise::GetDenoisingFrameIndex(View);

        // 在这里可以添加逻辑，比如将信息输出到屏幕
        // GEngine->AddOnScreenDebugMessage(...)
        
        UE_LOG(LogTemp, Log, TEXT("NFOR Debug Pass: Active, FrameCount=%d, Index=%d"), FrameCount, CurrentIndex);
    }
    else
    {
        UE_LOG(LogTemp, Verbose, TEXT("NFOR Debug Pass: Denoiser not active."));
    }
}
```

## 模块依赖

该插件的 `Build.cs` 文件表明其深度集成在 UE 的渲染核心中。以下为关键依赖：

| 模块 | 用途 |
|---|---|
| `Renderer` | 核心渲染器，提供渲染线程、Render Graph (RDG) 基础设施。 |
| `RenderCore` | 提供渲染资源、RHI 管理等核心功能。 |
| `RHI` | 渲染硬件接口，用于与 GPU 交互。 |
| `RDG` | Render Dependency Graph，插件大量使用 RDG 进行计算和图形 Pass 的调度。 |
| `Projects` | 用于项目级插件和模块管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量被截断为浮点数的编译警告。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除旧的 GPU 同步 API，改用更统一的 `SubmitAndBlockUntilGPUIdle`。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移至新的 `UE_LOGF`。 |
| 2026-03-17 | `5b1f483b` | Fix missing includes in non-unity build due to implicit includes from rendering headers. | 修复因渲染头文件隐式包含导致的非 Unity 构建错误。 |
| 2026-02-09 | `4092d701` | Disabled compiling of NFOR shaders on Metal platforms due to atomicBinOp.i64 | 因 Metal 平台不支持 64 位原子操作，禁用该平台上的着色器编译。 |

### 维护评价

NFORDenoise 插件自 2024 年 4 月首次提交以来，一直是 **实验性（Experimental）** 状态，且 `EnabledByDefault` 为 `true`，表明 Epic 将其作为路径追踪渲染管线的一个重要但尚未完全稳定的组件。

- **活跃度**：从近期提交记录看（截止到 2026 年 5 月），插件仍在被维护。最近的更新主要集中在**代码质量**（修复编译警告、统一 API）、**构建系统**修复和**跨平台兼容性**上，而非新功能开发。这表明其核心算法已趋于稳定。
- **现状评估**：该插件属于**维护中，但功能已进入稳定期**的状态。它并非被遗弃，而是进入了一个以修复和优化为主的阶段。
- **使用建议**：推荐在**电影渲染队列（MRQ）** 的**离线路径追踪**工作流中使用。由于其`实验性`标签，不建议在项目关键路径上依赖它作为唯一降噪方案，并需关注未来版本的潜在 API 变动。对于实时渲染需求，此插件不适用。
- **已知限制**：
    1.  平台限制：当前仅支持 **Win64** 和 **Linux**，且**Metal (macOS/iOS) 平台已禁用**着色器编译。
    2.  算法限制：首次提交说明中提到，该算法对“相邻帧历史接近”的慢速移动相机效果较好。
    3.  实验性：`IsExperimentalVersion=true`，意味着其接口和行为可能在未来的引擎版本中发生变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/NFORDenoise)
- [官方文档]() (无)
- [测试用例]() (无明确公开测试用例)