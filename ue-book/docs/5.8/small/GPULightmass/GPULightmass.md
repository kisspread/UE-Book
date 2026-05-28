# GPU Lightmass

> Static lighting building & previewing system using DXR

| 属性 | 值 |
|---|---|
| 中文名 | GPU 光照构建系统 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、设置面板） |
| 模块 | `GPULightmass` (UncookedOnly), `GPULightmassEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2020-06-23 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass) | |

## 用途

GPU Lightmass 是一个使用 DXR（DirectX Raytracing）技术进行静态光照构建和实时预览的系统。它的核心目的是**利用现代 GPU 的光线追踪能力来加速静态光照贴图（Lightmap）的生成**，以替代传统的基于 CPU 的 Lightmass 系统。传统 CPU Lightmass 在处理大型复杂场景时构建速度较慢，而 GPULightmass 通过 GPU 并行计算大幅提升了光照构建效率，特别适合需要快速迭代光照效果的关卡设计和美术工作流。

该插件主要解决以下问题：
1.  **快速迭代**：在编辑器中实现接近实时的“烘焙”预览，允许开发者快速调整灯光和材质并看到结果。
2.  **高质量GI**：通过路径追踪（Path Tracing）计算全局光照（GI），支持辐照度缓存（Irradiance Caching）和首光线引导（First Bounce Ray Guiding）以优化质量和性能。
3.  **功能完整**：支持完整的静态光照特性，包括光照贴图、体积光照贴图（Volumetric Lightmap）、静态阴影深度贴图（Static Shadow Depth Maps）等。

## 使用场景

-   **大型开放世界或复杂室内场景开发**：传统 CPU Lightmass 构建一次可能需要数小时，GPULightmass 能将其缩短至分钟级别，极大提升迭代速度。
-   **需要实时预览光照效果的关卡设计**：设计师可以使用“Bake What You See”模式，在移动相机时逐步生成所见区域的光照贴图，实现交互式光照调整。
-   **使用静态光源（Stationary Lights）的场景**：GPULightmass 能够高效地计算静态阴影通道。
-   **对最终烘焙质量有要求，同时希望利用GPU加速的项目**：虽然主要面向编辑器预览，但其计算方法基于物理，结果可作为最终烘焙的基础。

## 蓝图用法

主要通过 `UGPULightmassSubsystem` 子系统在蓝图中控制烘焙过程。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Settings` | 获取 GPULightmass 的设置对象，用于配置烘焙参数。 | `UGPULightmassSubsystem` |
| `Launch` | 启动光照构建过程。 | `UGPULightmassSubsystem` |
| `Stop` | 停止正在运行的光照构建。 | `UGPULightmassSubsystem` |
| `Is Running` | 查询当前光照构建是否正在运行。 | `UGPULightmassSubsystem` |
| `Get Percentage` | 获取当前构建进度（百分比）。 | `UGPULightmassSubsystem` |
| `Set Realtime` | 设置是否以实时模式运行构建（影响性能分配）。 | `UGPULightmassSubsystem` |
| `Save` | 保存当前烘焙完成的光照贴图结果。 | `UGPULightmassSubsystem` |
| `Start Recording Visible Tiles` | 开始录制可见的虚拟纹理瓦片（用于“Bake What You See”模式）。 | `UGPULightmassSubsystem` |
| `End Recording Visible Tiles` | 结束录制可见瓦片。 | `UGPULightmassSubsystem` |

### 使用示例（蓝图描述）
1.  在关卡蓝图中，通过 `Get World Subsystem` 节点获取 `GPULightmass Subsystem`。
2.  调用 `Get Settings` 节点获取设置对象，可修改如 `GI Samples`（采样数）、`Mode`（模式）等属性。
3.  调用 `Launch` 节点启动烘焙。可以连接一个计时器或事件，定期调用 `Get Percentage` 来更新 UI 进度条。
4.  烘焙完成后，`On Light Build Ended` 委托会触发，此时可以调用 `Save` 保存结果。
5.  若要在移动相机时实时预览，可设置 `Mode` 为 “Bake What You See”，并配合 `Start/End Recording Visible Tiles` 使用。

## C++ 用法

### 头文件引入
```cpp
#include "GPULightmassModule.h"
#include "GPULightmassSettings.h"
```

### 基本用法
GPULightmass 的核心交互通过模块和子系统进行。

```cpp
// 1. 获取模块实例
FGPULightmassModule* GPULightmassModule = FModuleManager::GetModulePtr<FGPULightmassModule>(TEXT("GPULightmass"));

if (GPULightmassModule)
{
    // 2. 为特定世界创建或获取 GPULightmass 实例
    UWorld* MyWorld = GEditor->GetEditorWorldContext().World();
    UGPULightmassSettings* Settings = NewObject<UGPULightmassSettings>();
    Settings->GISamples = 1024; // 自定义设置

    FGPULightmass* LightmassSystem = GPULightmassModule->CreateGPULightmassForWorld(MyWorld, Settings);
}

// 3. 通过子系统控制烘焙（更常用）
if (UWorld* World = GEditor->GetEditorWorldContext().World())
{
    if (UGPULightmassSubsystem* Subsystem = World->GetSubsystem<UGPULightmassSubsystem>())
    {
        // 配置并启动
        UGPULightmassSettings* Settings = Subsystem->GetSettings();
        Settings->Mode = EGPULightmassMode::FullBake;
        Settings->GISamples = 256;
        Subsystem->Launch();

        // 监听完成事件
        Subsystem->OnLightBuildEnded().AddLambda([]()
        {
            UE_LOG(LogTemp, Log, TEXT("GPU Lightmass baking finished!"));
        });
    }
}
```

### 进阶用法
监听世界事件以自动管理光照构建状态：
```cpp
// 在某个编辑器工具或自定义Actor中
void AMyEditorTool::BeginPlay()
{
    Super::BeginPlay();

    // 监听组件注册/注销，以自动更新场景表示
    FGPULightmassModule* Module = FModuleManager::GetModulePtr<FGPULightmassModule>(TEXT("GPULightmass"));
    if (Module && Module->StaticLightingSystems.Contains(GetWorld()))
    {
        FGPULightmass* Lightmass = Module->StaticLightingSystems[GetWorld()];
        // 可以访问 Lightmass->Scene 来获取光照构建场景的高级信息
        // 注意：直接操作场景对象需要对插件内部结构有深入了解
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何在编辑器工具按钮点击后配置并启动 GPULightmass 烘焙。

```cpp
// MyLightBakeTool.h
#pragma once

#include "CoreMinimal.h"
#include "EditorUtilityWidget.h"
#include "MyLightBakeTool.generated.h"

class UGPULightmassSettings;

UCLASS()
class UMyLightBakeTool : public UEditorUtilityWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category="LightBake")
    void StartQuickBake();

private:
    TWeakObjectPtr<UGPULightmassSettings> CachedSettings;
};
```

```cpp
// MyLightBakeTool.cpp
#include "MyLightBakeTool.h"
#include "GPULightmassSettings.h"
#include "GPULightmassModule.h"

void UMyLightBakeTool::StartQuickBake()
{
    UWorld* World = GEditor->GetEditorWorldContext().World();
    if (!World) return;

    UGPULightmassSubsystem* Subsystem = World->GetSubsystem<UGPULightmassSubsystem>();
    if (!Subsystem) return;

    // 获取并配置设置
    UGPULightmassSettings* Settings = Subsystem->GetSettings();
    Settings->GISamples = 128; // 使用较少采样快速预览
    Settings->DenoisingOptions = EGPULightmassDenoisingOptions::DuringInteractivePreview;
    Settings->bUseIrradianceCaching = false; // 关闭IC以简化计算
    Settings->Mode = EGPULightmassMode::BakeWhatYouSee;
    CachedSettings = Settings;

    // 启动
    Subsystem->Launch();

    UE_LOG(LogTemp, Log, TEXT("Started quick GPU Lightmass bake for preview."));
}
```

## 模块依赖

从源码分析，GPULightmass 插件深度集成于 UE 的渲染核心，其构建系统和运行时模块依赖以下**独特或不常见**的模块：

| 模块 | 用途 |
|---|---|
| `Renderer` | 提供核心渲染功能、材质系统、网格处理（MeshPassProcessor）。 |
| `RenderCore` | 提供渲染资源管理、Shader参数、渲染图（RDG）支持。 |
| `RHI` | 底层渲染硬件接口，用于创建和访问 GPU 资源。 |
| `RayTracing` | 提供光线追踪场景（TLAS）、Shader Binding Table (SBT) 等 DXR 基础设施。 |
| `D3D12RHI` | 特定于 D3D12 的 RHI 实现，用于访问 DXR 核心特性。 |
| `VirtualTexture` | 提供虚拟纹理系统框架，用于管理光照贴图的虚拟页表和生产者。 |
| `VirtualTexturing` | 虚拟纹理运行时，用于页面请求、生产和纹理采样。 |
| `MeshDescription` | 可能用于从 UStaticMesh 获取网格数据以构建光追几何体。 |
| `Landscape` | 提供地形组件的渲染支持，插件中有专门的地形光追处理。 |

**注意**：该插件严格限制为 **Win64** 平台，并且要求支持 DXR（DirectX Raytracing）的 GPU 和驱动。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `78d4e656` | [GPULM] Flush deferred SBT static-range frees on cached scene teardown | 在缓存场景拆除时刷新延迟的 SBT 静态范围释放，防止资源泄漏。 |
| 2026-05-12 | `98b3c0ef` | [HWRT] Add MeshBatchesView to FRayTracingDynamicGeometryUpdateParams and unify mesh batch ownership. | 为光线追踪动态几何更新参数添加网格批次视图，统一网格批次所有权。 |
| 2026-04-21 | `a437915f` | [HWRT] Refactored shared vertex buffer management in FRayTracingDynamicGeometryUpdateManager. | 重构光线追踪动态几何更新管理器中的共享顶点缓冲区管理。 |
| 2026-04-15 | `2a295e97` | - Removed BlockUntilGPUIdle and SubmitCommandsAndFlushGPU in place of SubmitAndBlockUntilGPUIdle | 移除旧接口，统一使用新的 `SubmitAndBlockUntilGPUIdle` 方法。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF。 |

### 维护评价
-   **实验性状态**：插件明确标记为 `IsBetaVersion = true`，且默认未启用 (`EnabledByDefault = false`)。这表明它仍被视为实验性功能。
-   **活跃维护**：从最近的提交历史看，该插件在 2026 年 5 月仍有维护性更新。这些更新主要集中在与底层硬件光线追踪（HWRT）系统的兼容性和资源管理优化上，表明 Epic Games 仍在维护和改进此系统。
-   **平台限制**：仅支持 Win64 平台，依赖于特定的 DXR 功能。
-   **使用建议**：对于需要快速光照迭代、愿意接受实验性功能限制的 Win64 项目，GPULightmass 是一个强大的工具。由于其 Beta 状态，在生产环境中作为最终烘焙方案需谨慎评估稳定性。它非常适合用于编辑器内的预览和迭代，最终导出可能仍需使用传统 Lightmass 或其他经过验证的解决方案。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/GPULightmass)
- 官方文档（插件内 DocsURL 为空）：暂无官方文档链接。
- 测试用例：根据源码结构分析，该插件的集成测试可能位于 `Engine/Tests/` 目录下或与主引擎渲染测试结合，未在插件目录内发现独立的单元测试文件。