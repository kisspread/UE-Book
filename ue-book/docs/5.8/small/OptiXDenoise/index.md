# OptiXDenoise

> Denoising engine for the Unreal Path Tracer based on NVIDIA's OptiX AI-Accelerated Denoiser library.

| 属性 | 值 |
|---|---|
| 中文名 | OptiX 降噪 |
| 分类 | Denoising |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OptixDenoise` (Runtime), `OptiXDenoiseBase` (External) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-10-10 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise) | |

## 用途

此插件为 UE5 的 **Path Tracer (路径追踪器)** 提供 AI 加速的降噪功能。它封装了 NVIDIA 的 OptiX SDK 和 Optical Flow SDK，核心解决路径追踪渲染中固有的**高噪声问题**。通过利用 AI 算法，它能够从含有大量噪点的路径追踪渲染结果（辅以场景几何和材质信息如 albedo、normal）中，重建出干净、平滑的图像。这对于使用路径追踪进行离线渲染预览、或实时渲染中降低收敛时间至关重要。

## 使用场景

- 你正在使用 UE5 的 Path Tracer 制作**影视预览**或**高质量静态帧**，希望快速获得无噪声的结果。
- 你在开发**建筑可视化**或**产品展示**项目，依赖路径追踪的真实光照，但等待完全收敛时间过长。
- 你在制作游戏过场动画，使用路径追踪实现电影级光照效果，需要加速渲染预览流程。
- 你需要在渲染动画序列时，对每一帧进行独立的时空降噪，以获得稳定的动画效果。

## 蓝图用法

此插件主要通过 **UnrealInsights 的 Trace 通道** 与路径追踪器集成，并不直接暴露为蓝图节点。用户通过以下方式间接使用：
1.  在项目设置或通过控制台命令启用路径追踪和降噪功能。
2.  降噪器作为 Path Tracer 的内部后处理步骤自动触发。

**核心控制点（通过设置/命令）**：
-  控制是否启用降噪。
-  选择使用仅空间降噪或结合运动矢量的时空降噪。

## C++ 用法

### 头文件引入

```cpp
#include "OptiXDenoiseModule.h"
#include "PathTracingDenoiser.h"
```

### 基本用法

该插件的核心是为 `FPathTracingDenoiser` 提供一个 OptiX 后端实现。使用者通常不直接创建降噪器，而是由路径追踪器根据配置自动选取。

```cpp
// 文件：Engine/Source/Runtime/Renderer/Private/PathTracing/PathTracingDenoiser.h
// (此文件为接口定义，OptiXDenoise 模块是其具体实现之一)
class FPathTracingDenoiser
{
public:
    // ... 其他接口
    virtual bool Denoise(
        FRHICommandListImmediate& RHICmdList,
        FViewInfo& View,
        const FPathTracingDenoiseInput& Input,
        const FPathTracingDenoiseSettings& Settings) = 0;
};
```

### 进阶用法

降噪过程需要正确的输入，包括：
1.  **含噪辐射度 (Radiance)**: 路径追踪器直接输出的原始结果。
2.  **Albedo (反照率)**: 场景的纯材质颜色，无光照信息。
3.  **Normal (法线)**: 视空间法线。
4.  **Flow (运动矢量)**: 用于时空降噪，匹配相邻帧之间的像素运动。

```cpp
// 构造降噪输入的简化示例
FPathTracingDenoiseInput DenoiseInput;
DenoiseInput.Color = RenderTargetRadiance;
DenoiseInput.Albedo = RenderTargetAlbedo;
DenoiseInput.Normal = RenderTargetNormal;
DenoiseInput.Flow = RenderTargetOpticalFlow; // 可选，用于时空降噪

FPathTracingDenoiseSettings Settings;
Settings.bDenoise = true;
Settings.bTemporal = true; // 启用时空降噪

// 调用降噪（通常由渲染线程自动调用）
bool bSuccess = Denoiser->Denoise(RHICmdList, View, DenoiseInput, Settings);
```

## Demo 示例

一个概念性的演示，展示如何配置降噪输入：

```cpp
// .h
#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "PathTracingDenoiser.h" // 依赖路径追踪器接口
#include "OptiXDenoiseDemoComponent.generated.h"

UCLASS(ClassGroup=(Rendering), meta=(BlueprintSpawnableComponent))
class UOptiXDenoiseDemoComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    // 模拟填充降噪所需纹理的过程
    UFUNCTION(BlueprintCallable, Category = "Rendering|PathTracer")
    void SimulateDenoiseSetup();
};
```

```cpp
// .cpp
#include "OptiXDenoiseDemoComponent.h"
#include "RHICommandList.h"

void UOptiXDenoiseDemoComponent::SimulateDenoiseSetup()
{
    // 1. 在实际渲染管线中，路径追踪器会生成以下纹理：
    //    - HDR辐射度纹理 (Color)
    //    - Albedo纹理
    //    - Normal纹理
    //    - Optical Flow纹理 (可选)

    // 2. OptiXDenoise插件的降噪器（FOptiXPathTracingDenoiser）被实例化。
    //    它检查输入纹理的有效性，并调用OptiX库执行AI推理。

    // 3. 最终，干净的输出纹理被用于后续的色调映射和显示。
    UE_LOG(LogTemp, Log, TEXT("OptiX Denoise setup simulated. In a real pipeline, the denoiser would process path tracing output."));
}
```

## 模块依赖

该插件的模块有特殊的依赖关系：

| 模块 | 用途 |
|---|---|
| `MessageLog` | 用于报告初始化和错误信息 |
| `D3D12RHI` | 与 DirectX 12 渲染硬件接口交互，因为OptiX与GPU计算紧密集成 |
| **OptiXDenoiseBase** (External) | 封装了 NVIDIA OptiX SDK 和 Optical Flow SDK 的二进制库文件，是插件的核心计算引擎 |

**注意**：此插件**仅支持 Windows 64位 (Win64) 平台**，且明确**不支持 Win64 的 ARM64 架构**。使用前需确保开发环境满足要求。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移至新的 UE_LOGF。 |
| 2026-02-03 | `88ba268b` | Fix unreachable code errors | 修复不可达代码的编译错误。 |
| 2025-06-04 | `562eefdb` | disable OptiXDenoise on Windows Arm64 | 在 Windows ARM64 平台上禁用此插件。 |
| 2025-05-09 | `da955ce5` | Adding Windows Arm64 libraries for: | 添加了 Windows ARM64 的库文件（但随后被禁用）。 |
| 2024-10-08 | `54fa3a60` | Fix nonportable paths for UnrealEditor (do not submit ClangWarnings.cs!!!!!!!!) | 修复编辑器中的不可移植路径问题。 |

### 维护评价

- **活跃状态**：最近一次实质性更新在 2026 年 2 月，修复了编译问题，表明仍在维护。
- **平台限制**：从最近的提交看，开发团队正在处理 ARM64 兼容性，但目前结论是**不支持**。该插件功能强大但平台绑定性强。
- **实验性风险**：作为 `Experimental` 插件，其 API 和行为可能在后续引擎版本中发生变化。
- **推荐度**：如果你在 **Win64 (x64)** 平台进行开发，且依赖 **Path Tracer**，**可以尝试使用**。但它属于实验性功能，应做好未来版本变动的准备。对于其他平台或非路径追踪工作流，不适用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/OptiXDenoise)
- 官方文档：无（.uplugin 未提供）
- [相关测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/PathTracing) (通常在渲染器测试中)