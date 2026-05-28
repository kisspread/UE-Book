# NNEDenoiser

> Neural denoiser for the Unreal Path Tracer based on the Neural Network Engine (NNE).

| 属性 | 值 |
|---|---|
| 中文名 | 降噪器 |
| 分类 | Denoising |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（代码资产、着色器） |
| 模块 | `NNEDenoiser` (Runtime), `NNEDenoiserShaders` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-26 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser) | |

## 用途

NNEDenoiser 是一个基于神经网络引擎 (NNE) 的路径追踪降噪器插件。它解决了在使用虚幻引擎路径追踪器时，为了获得高质量画面而需要高采样数所带来的性能问题。该插件通过使用训练好的神经网络模型对低采样数的渲染结果进行智能降噪，能够在保证视觉质量的前提下，显著降低路径追踪所需的采样次数，从而提升渲染性能。

## 使用场景

- 当你使用虚幻引擎的路径追踪器进行渲染，但图像上存在大量噪点时。
- 当你需要快速预览路径追踪效果，但又不想等待高采样数渲染完成时。
- 当你希望在保持高质量光影和反射的同时，降低路径追踪的性能开销时。

## 蓝图用法

主要通过 `UNNEDenoiserSubsystem` 世界子系统来控制降噪器的启用和配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Enable Denoiser` | 为当前世界启用神经网络降噪。 | `UNNEDenoiserSubsystem` |
| `Disable Denoiser` | 为当前世界禁用神经网络降噪。 | `UNNEDenoiserSubsystem` |
| `Is Denoiser Enabled` | 检查当前世界的降噪器是否启用。 | `UNNEDenoiserSubsystem` |

### 使用示例（蓝图描述）

1.  在任何拥有 `UWorld` 上下文的蓝图中（例如 Actor 或 Level Blueprint）。
2.  使用 `Get Subsystem` 节点，子系统类选择 `NNEDenoiserSubsystem`。
3.  将其返回值连接到 `Enable Denoiser` 或 `Disable Denoiser` 节点，即可控制降噪器的开关。

## C++ 用法

### 头文件引入

```cpp
#include "NNEDenoiserSubsystem.h"
```

### 基本用法

获取降噪器子系统并控制其状态。
*(来源：基于 Engine/Plugins/NNE/NNEDenoiser/Tests/ 目录下的测试用例)*

```cpp
// 在拥有 UWorld 上下文的类中（如 Actor、GameMode 等）
if (UWorld* World = GetWorld())
{
    // 获取 NNEDenoiser 子系统
    UNNEDenoiserSubsystem* DenoiserSubsystem = World->GetSubsystem<UNNEDenoiserSubsystem>();
    if (DenoiserSubsystem)
    {
        // 启用降噪
        DenoiserSubsystem->EnableDenoiser();
        
        // 检查状态
        bool bIsEnabled = DenoiserSubsystem->IsDenoiserEnabled();
        
        // 禁用降噪
        DenoiserSubsystem->DisableDenoiser();
    }
}
```

### 进阶用法

结合路径追踪的渲染设置，在渲染通道切换或质量等级变化时动态控制降噪器。

```cpp
// 示例：在切换到路径追踪模式时自动启用降噪器
void AMyGameMode::OnRenderModeChanged(bool bUsePathTracer)
{
    if (UWorld* World = GetWorld())
    {
        if (UNNEDenoiserSubsystem* DenoiserSys = World->GetSubsystem<UNNEDenoiserSubsystem>())
        {
            if (bUsePathTracer)
            {
                DenoiserSys->EnableDenoiser();
            }
            else
            {
                DenoiserSys->DisableDenoiser();
            }
        }
    }
}
```

## Demo 示例

一个最小的 Actor 示例，展示如何通过 C++ 启用和查询降噪器状态。

**MyDenoiserActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDenoiserActor.generated.h"

UCLASS()
class MYPROJECT_API AMyDenoiserActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMyDenoiserActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

    UFUNCTION(BlueprintCallable)
    void ToggleDenoiser();

private:
    UPROPERTY()
    class UNNEDenoiserSubsystem* CachedDenoiserSubsystem;
};
```

**MyDenoiserActor.cpp**
```cpp
#include "MyDenoiserActor.h"
#include "NNEDenoiserSubsystem.h"
#include "Engine/World.h"

AMyDenoiserActor::AMyDenoiserActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyDenoiserActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 缓存子系统指针
    if (UWorld* World = GetWorld())
    {
        CachedDenoiserSubsystem = World->GetSubsystem<UNNEDenoiserSubsystem>();
        // 默认启用降噪器
        if (CachedDenoiserSubsystem)
        {
            CachedDenoiserSubsystem->EnableDenoiser();
            UE_LOG(LogTemp, Log, TEXT("NNEDenoiser 已启用"));
        }
    }
}

void AMyDenoiserActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 示例：每帧检查状态（仅用于演示）
    if (CachedDenoiserSubsystem)
    {
        static bool bLastState = false;
        bool bCurrentState = CachedDenoiserSubsystem->IsDenoiserEnabled();
        if (bCurrentState != bLastState)
        {
            UE_LOG(LogTemp, Warning, TEXT("降噪器状态改变: %s"), bCurrentState ? TEXT("启用") : TEXT("禁用"));
            bLastState = bCurrentState;
        }
    }
}

void AMyDenoiserActor::ToggleDenoiser()
{
    if (CachedDenoiserSubsystem)
    {
        if (CachedDenoiserSubsystem->IsDenoiserEnabled())
        {
            CachedDenoiserSubsystem->DisableDenoiser();
        }
        else
        {
            CachedDenoiserSubsystem->EnableDenoiser();
        }
    }
}
```

## 模块依赖

从 `NNEDenoiser.Build.cs` 分析，要使用此插件的功能，你的模块需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `NNE` | 神经网络引擎核心接口。 |
| `NNERuntime` | NNE 的运行时核心逻辑。 |
| `Renderer` | 渲染器核心模块，用于集成渲染通道。 |
| `RenderCore` | 渲染核心基础类型和工具。 |
| `RHI` | 渲染硬件接口，用于提交 GPU 命令。 |
| `Projects` | 用于项目设置和模块管理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 用新的统一函数 `SubmitAndBlockUntilGPUIdle` 替换了旧的 GPU 同步函数。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 `UE_LOG` 迁移到更现代的 `UE_LOGF`。 |
| 2026-03-15 | `2caebd20` | Add more missing includes and forward declarations for various rendering headers... | 补充了更多渲染头文件的包含和前向声明，修复潜在编译问题。 |
| 2026-03-14 | `95105f12` | Split PooledRenderTarget and SceneRenderingAllocator off into separate header... | 将 `PooledRenderTarget` 等类型拆分到独立头文件，优化编译依赖。 |
| 2026-02-27 | `ae4a826a` | Take two after fixing bad find-and-replace. | 修复了之前一次错误的查找替换操作。 |

### 维护评价

- **创建时间**：约 2 年前（2024 年 8 月）。
- **近期更新**：更新频繁，最近一次提交在 2026 年 4 月，内容涉及底层渲染 API 优化、代码现代化和依赖清理。
- **活跃状态**：**活跃维护中**。虽然标记为 Beta，但 Epic 团队仍在持续优化和修复。
- **已知限制**：1. **Beta 状态**：这意味着其 API 和行为在后续版本中可能会有破坏性变更。2. 依赖于特定的 NNE 运行时（如 `NNERuntimeORT`），需确保目标平台支持。
- **推荐使用**：如果你需要在路径追踪中实时获得更干净的图像预览，这是一个非常有用且正在被积极开发的工具。但在正式生产环境中使用前，需评估 Beta 风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/NNE/NNEDenoiser/Tests)