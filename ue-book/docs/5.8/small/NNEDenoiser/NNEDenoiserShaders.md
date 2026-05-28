# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络去噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（测试资源） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是一个专门为 Unreal Engine 的路径追踪器（Path Tracer）设计的 AI 降噪后处理插件。它利用 NNE (Neural Network Engine) 框架来运行神经网络模型，实时去除路径追踪渲染中因低采样率（SPP）产生的噪点。该插件通过在渲染管线中插入一个基于计算着色器的预处理、AI 推理和后处理步骤，显著提升低质量路径追踪图像的视觉质量，从而在保持较高渲染速度的同时获得平滑的输出。

其存在意义在于解决路径追踪渲染中“速度与质量”的经典矛盾：为了快速预览或实时交互，通常会使用很低的采样率，导致图像充满噪声；而 NNEDenoiser 能够智能地“猜测”并填补缺失的信息，让低采样率的渲染结果看起来像更高采样率的版本。

## 使用场景

-   你在进行**建筑可视化**或**产品渲染**，希望使用路径追踪获得真实的光影效果，但需要快速迭代和预览。
-   你在制作**动画序列**，使用路径追踪进行最终渲染，希望利用 AI 去噪来大幅缩短每帧的渲染时间，同时保持画面质量。
-   你的项目启用了**路径追踪**，但受限于 GPU 性能或云渲染成本，需要最大化每一帧的渲染效率。
-   你正在开发需要**实时或近似实时**全局光照效果的应用程序，并愿意接受 AI 去噪引入的少量视觉伪影。

## 蓝图用法

NNEDenoiser 主要通过渲染命令行和项目设置进行配置，其核心推理过程由引擎的渲染管线内部调用。对外暴露的蓝图 API 相对有限，通常用于控制去噪器的状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set Denoiser` | 设置当前路径追踪器使用的降噪器类型（例如，切换到 NNEDenoiser）。 | `UPathTracingDenoiserSettings` (通过系统设置或控制台命令访问) |

### 使用示例（蓝图描述）

该插件的使用通常不涉及直接连接蓝图节点，而是通过以下方式配置：

1.  **项目设置**: 在 `项目设置 -> 引擎 -> 渲染 -> 路径追踪` 下，查找降噪相关选项，选择 “NNE Denoiser”。
2.  **控制台命令**: 在运行时，可以通过控制台命令 `r.PathTracing.Denoiser` 来切换降噪器（例如，`r.PathTracing.Denoiser 1` 可能对应 NNEDenoiser）。
3.  **材质与后处理**: 去噪过程是自动的。当路径追踪器被激活且配置了 NNEDenoiser 后，其输出会自动经过神经网络处理。

## C++ 用法

该插件的 C++ API 主要服务于引擎内部的渲染模块，用于集成和配置去噪管线。对于插件使用者，主要通过配置而非直接编码来使用。以下是基于其模块结构和依赖关系的典型使用模式。

### 头文件引入

```cpp
#include "NNEDenoiser.h"
// 通常还需要引入渲染相关头文件
#include "SceneView.h"
#include "RenderTargetPool.h"
```

### 基本用法

以下代码展示了如何在渲染器中检查和激活 NNEDenoiser（通常由引擎内部完成，此处仅为示意）。

*来源：基于 `Engine/Plugins/NNE/NNEDenoiser/` 的模块结构推断*

```cpp
// 在渲染器的路径追踪相关代码中
#include "NNEDenoiser.h"
// ... 在某个初始化函数中
if (NNEDenoiser::IsSupported())
{
    // 配置去噪参数
    NNEDenoiser::FDenoiserParameters DenoiserParams;
    DenoiserParams.InputWidth = RenderTargetWidth;
    DenoiserParams.InputHeight = RenderTargetHeight;
    DenoiserParams.bUseAlbedo = bUseAlbedoBuffer; // 是否使用反照率缓冲作为辅助输入
    DenoiserParams.bUseNormal = bUseNormalBuffer; // 是否使用法线缓冲作为辅助输入
    
    // 创建并初始化去噪器实例
    NNEDenoiser::FDenoiserPtr Denoiser = NNEDenoiser::CreateDenoiser();
    if (Denoiser->Initialize(DenoiserParams))
    {
        // 去噪器准备就绪，可以在后续的路径追踪渲染Pass中调用Denoiser->Execute()
    }
}
```

### 进阶用法

在自定义的后处理 Pass 中集成去噪流程，可能需要直接操作 RDG（Render Dependency Graph）。

*概念示例，非直接提取自提供的代码片段*

```cpp
// 在一个 RDG 计算着色器 Pass 中
void AddNNEDenoiserPass(FRDGBuilder& GraphBuilder, const FViewInfo& View)
{
    // 1. 获取去噪器需要的输入纹理（通常来自路径追踪Pass的输出）
    FRDGTextureRef PathTracerOutput = /* ... */;
    FRDGTextureRef AlbedoBuffer = /* ... */;
    
    // 2. 创建 NNEDenoiser 的参数和资源绑定
    NNEDenoiserShaders::Internal::FDefaultIOProcessCS::FParameters* ProcessParams = 
        GraphBuilder.AllocParameters<NNEDenoiserShaders::Internal::FDefaultIOProcessCS::FParameters>();
    ProcessParams->Width = View.ViewRect.Width();
    ProcessParams->Height = View.ViewRect.Height();
    ProcessParams->InputTexture = PathTracerOutput;
    // ... 绑定其他参数
    
    // 3. 添加 GPU 计算 Pass 来执行去噪（这通常由 NNEDenoiser 模块内部的调度器完成）
    // FComputeShaderUtils::AddPass(GraphBuilder, RDGEventName, DenoiserShader, ProcessParams, FIntVector(...));
}
```

## Demo 示例

一个可编译的最小 C++ 示例，演示如何在游戏模块中查询 NNEDenoiser 的状态。

**MyGameDenoiserChecker.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "MyGameDenoiserChecker.generated.h"

UCLASS()
class UMyGameDenoiserChecker : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    /** 检查 NNEDenoiser 插件是否可用并输出日志 */
    UFUNCTION(BlueprintCallable, Category = "Rendering|Denoiser")
    void CheckNNEDenoiserAvailability() const;
};
```

**MyGameDenoiserChecker.cpp**
```cpp
#include "MyGameDenoiserChecker.h"
#include "NNEDenoiser.h" // 包含 NNEDenoiser 模块头
#include "Kismet/GameplayStatics.h"

void UMyGameDenoiserChecker::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 初始化时进行检查
    CheckNNEDenoiserAvailability();
}

void UMyGameDenoiserChecker::CheckNNEDenoiserAvailability() const
{
    // 检查模块是否加载（更基础的检查）
    FModuleManager& ModuleManager = FModuleManager::Get();
    if (ModuleManager.IsModuleLoaded(TEXT("NNEDenoiser")))
    {
        UE_LOG(LogTemp, Log, TEXT("NNEDenoiser 模块已加载。"));
        // 进一步检查功能是否支持（例如，GPU 支持、模型是否就绪）
        // 注意：IsSupported 是 NNEDenoiser 模块内假设的函数，实际API请查阅模块头文件
        if (NNEDenoiser::IsSupported())
        {
            UE_LOG(LogTemp, Log, TEXT("当前环境支持 NNEDenoiser 功能。"));
        }
        else
        {
            UE_LOG(LogTemp, Warning, TEXT("NNEDenoiser 模块已加载，但当前环境不支持。"));
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("NNEDenoiser 模块未加载。请确认插件已启用。"));
    }
}
```

## 模块依赖

要使用 NNEDenoiser，你的模块需要依赖以下核心模块（已在 NNEDenoiser 的 Build.cs 中声明）：

| 模块 | 用途 |
|---|---|
| `NNE` | 核心神经网络引擎，提供模型管理和推理接口。 |
| `RenderCore` | 渲染核心库，提供 RDG、渲染资源等基础功能。 |
| `RHI` | 渲染硬件接口，用于底层 GPU 资源管理。 |
| `Renderer` | 引擎主渲染器，路径追踪等高级渲染特性位于此。 |
| `NNECore` | NNE 的核心模块，提供张量、运行时等抽象。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 更新GPU同步API，用新函数替换旧函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have ... | 修复编译依赖，添加缺失的头文件包含和前向声明。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu... | 重构头文件，将特定类型拆分出去，并显式包含。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复一次错误的批量替换操作。 |

### 维护评价

NNEDenoiser 是一个相对较新的插件（创建于 2024 年 8 月），但维护非常活跃。从近期 git 历史可以看出，它正紧密跟随 UE5 渲染器的演进，进行 API 迁移、编译修复和代码清理。这表明 Epic Games 的开发团队正在积极维护和更新该插件，以确保其与最新引擎版本的兼容性和稳定性。

**推荐使用**：对于需要在路径追踪中实现快速降噪的项目，NNEDenoiser 是一个官方推荐的、处于积极维护中的解决方案。尽管它标记为实验性（Beta），但鉴于其活跃的更新和明确的集成，可以视为一个可靠的功能进行评估和使用。需要注意的是，作为实验性功能，其 API 和行为在未来版本中可能会有变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/NNE) (基于 NNE 插件的通用测试位置推断)