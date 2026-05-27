# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资产） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

本插件是一个利用神经网络（通过 NNE - 神经网络引擎）对 Unreal Engine 的路径追踪器（Path Tracer）输出进行实时降噪的工具。路径追踪渲染在计算收敛（收敛到无噪点）前会产生大量噪点，此插件旨在利用经过训练的神经网络模型，在路径追踪的中间结果上快速推断出干净的图像，从而让美术师能在编辑器中实时预览接近最终效果的渲染视图，极大地提升了交互式工作流的效率。

## 使用场景

- 你在进行建筑可视化、产品设计或电影预渲染时，使用路径追踪器（Path Tracer）进行交互式渲染预览。
- 你希望在路径追踪尚未完全收敛（例如，仅用少量采样）时，就能看到一个干净的预览图，以便快速调整灯光、材质和构图。
- 你需要一个与引擎深度集成的、基于GPU加速的降噪方案，而不是依赖第三方后处理软件。

## 蓝图用法

本插件主要作为路径追踪器的一个集成组件，不直接暴露蓝图可调用函数或属性。其降噪功能通常通过**项目设置**（Project Settings）或**渲染设置**（如 `r.PathTracer.Denoiser` 控制台变量）来启用和配置。

要启用此降噪器，请确保：
1. 项目中启用了 `NNEDenoiser` 插件（默认已启用）。
2. 在项目设置或控制台命令中将路径追踪的降噪器设置为 `NNEDenoiser`。
3. 渲染视口使用路径追踪模式（例如，切换到“Path Tracing”视图模式）。

## C++ 用法

本插件的核心功能作为引擎渲染模块的一部分，与路径追踪管线深度集成。对于大多数用户而言，无需直接进行 C++ 编程。其集成和使用主要通过引擎的渲染系统完成。

### 头文件引入

若需在自定义渲染通道或相关模块中使用本插件提供的特定着色器或功能，可引入以下头文件：

```cpp
// 来自 NNEDenoiser 模块
#include "NNEDenoiserModule.h"

// 来自 NNEDenoiserShaders 模块 (用于自定义计算着色器)
#include "Internal/NNEDenoiserShadersDefaultIOProcessCS.h"
```

### 基本用法

以下代码片段展示了如何在引擎中引用 `NNEDenoiser` 模块。`NNEDenoiser` 本身是一个运行时模块，它的主要功能在引擎启动时由路径追踪系统自动加载和使用。开发者通常需要在 `Build.cs` 中声明依赖，而不是直接实例化它。

```cpp
// 在你的模块构建脚本 (.Build.cs) 中添加对 NNEDenoiser 的依赖
PublicDependencyModuleNames.AddRange(new string[] {
    "NNEDenoiser" // 如果你需要访问该模块导出的特定接口或函数
});
```

### 进阶用法

`NNEDenoiserShaders` 模块包含多个计算着色器，用于在GPU上高效执行降噪所需的预处理和后处理步骤，例如自动曝光计算（AutoExposure）、色调映射函数应用（TransferFunction）以及通道映射复制（MappedCopy）。这些着色器被 `NNEDenoiser` 的运行时模块调用，通常不会由游戏代码直接发起调用。

## Demo 示例

由于本插件是渲染管线的一部分，其“使用”并非通过编写代码来触发降噪过程，而是通过配置渲染设置。以下是一个最小化配置示例，展示如何在 C++ 代码中通过控制台命令启用基于 NNEDenoiser 的路径追踪降噪。

**MyGameMode.cpp**
```cpp
#include "GameFramework/GameModeBase.h"
#include "HAL/IConsoleManager.h"
#include "MyGameMode.h"

void AMyGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取并设置路径追踪降噪器的控制台变量
    IConsoleVariable* DenoiserCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracer.Denoiser"));
    if (DenoiserCVar)
    {
        // 设置为使用 NNEDenoiser (值为 1，具体值取决于引擎版本和实现)
        DenoiserCVar->Set(TEXT("1"), EConsoleVariableFlags::ECVF_SetByCode);
        UE_LOG(LogTemp, Log, TEXT("Path Tracer Denoiser set to NNEDenoiser."));
    }

    // 可选：确保路径追踪启用
    IConsoleVariable* PathTracerCVar = IConsoleManager::Get().FindConsoleVariable(TEXT("r.PathTracer"));
    if (PathTracerCVar)
    {
        PathTracerCVar->Set(TEXT("1"), EConsoleVariableFlags::ECVF_SetByCode);
    }
}
```

## 模块依赖

要使用本插件提供的功能（主要是通过路径追踪降噪），你的项目模块通常需要依赖以下独特的引擎/插件模块。这是本插件正常工作所必需的：

| 模块 | 用途 |
|---|---|
| `NNE` | 核心的神经网络引擎，用于加载、管理和运行降噪模型。 |
| `NNERuntimeORT` | （插件依赖）提供 ONNX Runtime 后端，用于执行神经网络推理。 |
| `RHI` | 渲染硬件接口，用于GPU计算资源的创建和管理。 |
| `RenderCore` | 核心渲染功能，包括渲染命令队列和资源描述符。 |
| `RHICore` | RHI 的核心实现，提供底层渲染资源。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 统一GPU同步操作，使用 `SubmitAndBlockUntilGPUIdle` 替换旧函数，可能提升稳定性或性能。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 `UE_LOG` 宏迁移到新的 `UE_LOGF` 格式，属于日志系统内部更新。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have... | 修复头文件依赖，为渲染相关的头文件添加缺失的包含和前置声明，增强编译稳定性。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 重构渲染头文件，将 `PooledRenderTarget` 和 `SceneRenderingAllocator` 分离到独立头文件，优化编译依赖。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次失败的查找替换操作后的再次提交，通常是对前一次代码重构的修正。 |

### 维护评价

- **活跃维护**：该插件自 2024 年 8 月创建以来，一直有持续的维护活动。最近的更新（截至 2026 年 4 月）集中在代码健壮性、编译优化和底层API的现代化上。
- **状态**：插件在 `.uplugin` 中标记为 `IsBetaVersion: true`，表明它仍处于测试阶段，可能存在不稳定或接口变化。
- **推荐度**：作为 Epic Games 官方推出的前沿功能，**强烈推荐**在需要路径追踪交互预览的项目中启用和使用。尽管是 Beta 版，但更新积极，且集成度高。使用者应关注引擎更新日志，因为其API和行为可能在未来版本中调整。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [官方文档]() (插件元数据中未提供)
- [测试用例]() (基于插件结构，相关测试可能位于 `Engine/Tests/` 目录下)