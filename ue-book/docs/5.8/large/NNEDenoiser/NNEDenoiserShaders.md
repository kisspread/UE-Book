# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 神经网络降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（预训练模型） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

**NNEDenoiser** 是一个基于 **Unreal 神经网络引擎 (NNE)** 的 **路径追踪降噪器**。它解决的核心问题是：虚幻引擎的路径追踪渲染器在实时或近实时渲染时，由于采样数不足会产生大量噪点。这个插件利用预训练的神经网络模型，在少量采样（例如1个SPP）后对渲染结果进行推理和降噪，从而在保持较高图像质量的同时大幅提升渲染效率。

它主要服务于需要高质量路径追踪光照但又受到渲染时间限制的场景。

## 使用场景

-   **建筑/产品可视化**：使用路径追踪渲染高质量的静态图像或动画时，用NNEDenoiser快速获得清洁的图片，无需等待漫长的高采样渲染。
-   **电影/动画预览**：在最终渲染前快速查看场景的路径追踪光照效果。
-   **游戏内高品质模式**：为支持光线追踪的高品质游戏模式提供快速的降噪方案，提升实时帧率。

## 蓝图用法

该插件的核心功能通常由引擎的渲染管线内部调用，其公开的蓝图接口较少。降噪器的启用和参数设置主要通过项目设置或渲染控制台变量进行配置。

## C++ 用法

### 头文件引入

```cpp
#include "NNEDenoiser.h" // 主模块
// 根据需要可能包含特定着色器头文件
#include "Internal/NNEDenoiserShadersDefaultIOProcessCS.h"
```

### 基本用法

以下示例展示了如何获取并初始化一个默认的神经网络降噪器实例。该实例将被引擎渲染系统用于处理路径追踪输出。

```cpp
// 文件路径: 概念性示例，基于模块API设计推断
#include "NNEDenoiserModule.h"
#include "NNEDenoiserSettings.h"

void InitializeDenoiser()
{
    // 获取 NNE Denoiser 模块接口
    INNEDenoiserModule* DenoiserModule = FModuleManager::GetModulePtr<INNEDenoiserModule>(TEXT("NNEDenoiser"));
    if (DenoiserModule)
    {
        // 创建或获取一个默认的降噪器实例
        // 该实例内部会加载配置的神经网络模型并初始化推理资源
        TSharedPtr<INNEDenoiser> Denoiser = DenoiserModule->GetOrCreateDefaultDenoiser();
        
        if (Denoiser.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("NNE Denoiser initialized successfully."));
            // 后续渲染管线会自动使用该实例进行降噪
        }
    }
}
```

### 进阶用法

可以自定义降噪器的处理流程，例如修改输入图像的预处理（Transfer Function）或后处理逻辑。这涉及到着色器层面的组合。

```cpp
// 文件路径: 概念性示例，基于着色器头文件推断
#include "RenderGraphBuilder.h"
#include "NNEDenoiserShadersAutoExposureCS.h"
#include "NNEDenoiserShadersTransferFunctionOidnCS.h"

void CustomDenoiserPass(FRDGBuilder& GraphBuilder, FRDGTexture* SceneColor, FRDGTexture* DenoisedOutput)
{
    // 1. 计算自动曝光
    auto* AutoExposurePass = GraphBuilder.AddPass<FAutoExposureDownsampleCS::FParameters>(...);
    // 设置 AutoExposure 参数并调度计算着色器 ...

    // 2. 应用传输函数（如 Oidn 的预处理）
    FTransferFunctionOidnCS::FParameters* TransferParams = GraphBuilder.AllocParameters<FTransferFunctionOidnCS::FParameters>();
    TransferParams->InputTexture = SceneColor;
    TransferParams->OutputTexture = /* 处理后的中间纹理 */;
    TransferParams->InputScaleBuffer = AutoExposurePass->GetOutputBuffer();
    // 设置其他参数...
    
    // 3. 执行神经网络推理 (由NNE运行时处理)
    // 4. 应用逆传输函数并输出到 DenoisedOutput
}
```

## Demo 示例

一个最小化的 C++ 类，用于在运行时动态控制路径追踪降噪器的启用状态。

**DenoiserController.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DenoiserController.generated.h"

UCLASS()
class ADenoiserController : public AActor
{
    GENERATED_BODY()
    
public:
    ADenoiserController();

protected:
    virtual void BeginPlay() override;

public:
    /** 切换NNE降噪器的启用状态 */
    UFUNCTION(BlueprintCallable, Category = "Denoiser")
    void ToggleNNEDenoiser();

private:
    void SetDenoiserEnabled(bool bEnabled);
};
```

**DenoiserController.cpp**
```cpp
#include "DenoiserController.h"
#include "NNEDenoiserModule.h"
#include "NNEDenoiser.h"
#include "RenderCore.h"

ADenoiserController::ADenoiserController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ADenoiserController::BeginPlay()
{
    Super::BeginPlay();
    // 初始启用降噪器
    SetDenoiserEnabled(true);
}

void ADenoiserController::ToggleNNEDenoiser()
{
    INNEDenoiserModule* Module = FModuleManager::GetModulePtr<INNEDenoiserModule>(TEXT("NNEDenoiser"));
    if (Module)
    {
        TSharedPtr<INNEDenoiser> Denoiser = Module->GetDefaultDenoiser();
        if (Denoiser.IsValid())
        {
            bool bCurrentState = Denoiser->IsEnabled();
            SetDenoiserEnabled(!bCurrentState);
            UE_LOG(LogTemp, Log, TEXT("NNE Denoiser %s"), bCurrentState ? TEXT("disabled") : TEXT("enabled"));
        }
    }
}

void ADenoiserController::SetDenoiserEnabled(bool bEnabled)
{
    INNEDenoiserModule* Module = FModuleManager::GetModulePtr<INNEDenoiserModule>(TEXT("NNEDenoiser"));
    if (Module)
    {
        TSharedPtr<INNEDenoiser> Denoiser = Module->GetDefaultDenoiser();
        if (Denoiser.IsValid())
        {
            Denoiser->SetEnabled(bEnabled);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `NNERuntimeORT` | 提供基于 ONNX Runtime 的神经网络模型推理能力，是降噪器模型运行的基础。 |
| `RenderCore`, `Renderer` | 访问渲染图（RDG）、计算着色器调度等核心渲染功能。 |
| `NNE` | 神经网络引擎的核心接口层。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 更新了GPU同步API，替换为新的统一封装函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧的日志宏迁移为新的UE_LOGF宏格式。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers to files that have | 修复了头文件依赖，补充了缺失的前向声明和包含。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header and add explicit inclu | 重构了头文件，将部分渲染类型拆分到独立头文件以优化编译。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了一次错误的查找替换操作所带来的问题。 |

### 维护评价

**NNEDenoiser** 是一个相对较新的插件（2024年8月创建），目前仍处于 **Beta 测试阶段**（`IsBetaVersion: true`）。
-   **近期活跃度**：过去半年有多次提交，但最近的几次（2026年3月、4月）主要是**代码维护性工作**，如头文件重构、API统一和编译警告修复，而非功能性更新。
-   **功能状态**：作为Beta插件，其核心功能（神经网络降噪）已存在并集成，但可能仍存在限制或不稳定因素。从首次提交信息看，它从`Experimental`文件夹迁移而来，标志着功能趋于成熟。
-   **推荐使用**：对于需要提升路径追踪渲染效率的项目，**值得尝试使用**。但需注意其Beta状态，建议在非关键生产流程中先行测试，并关注未来版本的正式发布。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [测试用例] (测试文件通常位于 `Engine/Tests/` 或插件内部的 `Tests/` 目录，具体路径需在仓库内搜索 `NNEDenoiser` 相关测试文件)