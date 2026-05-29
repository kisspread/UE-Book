# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置资产、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现分布式实时渲染和集群显示的完整框架。其核心功能是同步多台计算机（PC）的渲染输出，将同一个虚拟场景的不同视口无缝地拼接在一起，从而驱动大型显示系统，如 LED 墙、多通道投影、CAVE 系统、穹顶屏幕等。

**解决的问题：**
1.  **视口同步与锁定**：确保所有计算机在同一帧上渲染相同的内容，避免撕裂和延迟。
2.  **复杂显示拓扑管理**：支持对显示器进行任意排列和配置，映射到虚拟场景中的精确位置和方向。
3.  **性能扩展**：将渲染负载分配到多台计算机上，突破单机性能限制。
4.  **统一控制与监控**：提供从单个主控端（Master）对整个集群进行操作、调试和监控的工具。

除了基础的集群渲染，nDisplay 还集成了用于虚拟制片（ICVFX）的 Light Card 编辑、与 Media Framework 的集成（如 DeckLink 采集卡）、对 Sequencer 和 Movie Render Queue 的支持、多用户协作以及远程控制等功能，使其成为专业可视化、虚拟制片和沉浸式体验领域的行业标准工具。

## 使用场景

-  你正在搭建一个大型的 LED 视频墙用于现场活动或建筑投影 → 用 nDisplay 配置每台 PC 驱动一块屏幕。
-  你在为驾驶模拟器构建一个 270 度环绕投影系统（CAVE） → 用 nDisplay 定义投影机布局并生成无缝拼接的画面。
-  你在开发一个需要极高渲染帧率或分辨率的实时应用（如数字孪生、大型场景模拟）→ 用 nDisplay 将渲染任务分配到多台计算机上。
-  你在制作虚拟制片（Virtual Production）项目，使用 LED Volume 作为背景 → 用 nDisplay 的 ICVFX 功能管理和渲染 LED 墙内容，并配合 Light Card 添加可控光源。
-  你需要在运行时远程控制或修改 nDisplay 集群的设置 → 使用 nDisplay 的 Remote Control 和 Multi-User 功能。

## 蓝图用法

nDisplay 提供了大量的蓝图可调用函数，用于在运行时创建、控制和监控集群渲染。其核心接口是 `IDisplayClusterScenePreview`（通过 `FDisplayClusterScenePreviewModule` 实现），主要用于场景预览和渲染，但集群的主要运行时控制通常通过 `ADisplayClusterRootActor` 及其关联组件和函数来完成。

### 核心节点 (IDisplayClusterScenePreview 接口)

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Renderer` | 创建一个新的场景预览渲染器实例，返回一个唯一的 Renderer ID。 | `IDisplayClusterScenePreview` |
| `Destroy Renderer` | 销毁指定 ID 的渲染器并释放资源。 | `IDisplayClusterScenePreview` |
| `Set Renderer Root Actor Path` | 通过资产路径为渲染器设置要预览的 `ADisplayClusterRootActor`。适用于路径可能变化或延迟加载的情况。 | `IDisplayClusterScenePreview` |
| `Set Renderer Root Actor` | 直接为渲染器设置要预览的 `ADisplayClusterRootActor` 对象引用。 | `IDisplayClusterScenePreview` |
| `Add Actor To Renderer` | 将一个额外的 Actor 添加到指定渲染器的预览场景中。 | `IDisplayClusterScenePreview` |
| `Remove Actor From Renderer` | 从渲染器的预览场景中移除一个 Actor。 | `IDisplayClusterScenePreview` |
| `Clear Renderer Scene` | 清空指定渲染器预览场景中的所有 Actor。 | `IDisplayClusterScenePreview` |
| `Render` | 立即执行一次渲染，将结果绘制到提供的 `FCanvas` 上。 | `IDisplayClusterScenePreview` |
| `Render Queued` | 将一次渲染任务放入队列，在未来的 Tick 中执行。通过 `FRenderResultDelegate` 回调获取渲染结果（`FRenderTarget*`）。 | `IDisplayClusterScenePreview` |
| `Is Real Time Preview Enabled` | 检查当前是否启用了实时预览更新（影响 Light Card 等预览纹理的刷新）。 | `IDisplayClusterScenePreview` |

### 使用示例（蓝图描述）

要使用 `IDisplayClusterScenePreview` 接口来渲染一个 nDisplay 场景的预览图：

1.  **获取接口**：使用 `IDisplayClusterScenePreview::Get()` 静态函数获取模块实例。
2.  **创建渲染器**：调用 `Create Renderer` 节点，将返回的 `RendererId` 存储为变量。
3.  **配置根 Actor**：调用 `Set Renderer Root Actor Path` 或 `Set Renderer Root Actor`，将你的 `ADisplayClusterRootActor`（或其路径）关联到刚创建的渲染器。可以传入属性覆盖（`PropertyOverrides`）和预览标志（`PreviewFlags`）。
4.  **（可选）添加额外 Actor**：如果需要预览某些特定的 Light Card 或场景对象，可以使用 `Add Actor To Renderer` 将它们加入。
5.  **执行渲染**：
    *   **同步渲染**：调用 `Render` 节点，传入渲染设置（`RenderSettings`）和一个有效的 `Canvas`。
    *   **异步队列渲染**：调用 `Render Queued` 节点，传入渲染设置和图像尺寸（`Size`），并绑定一个 `On Render Result` 委托。渲染完成后，委托会触发，传入一个 `FRenderTarget`，从中可以提取渲染结果纹理。
6.  **清理**：使用完成后，调用 `Destroy Renderer` 节点释放资源。

## C++ 用法

nDisplay 的 C++ 用法围绕其丰富的模块和接口展开。以下示例聚焦于 `DisplayClusterScenePreview` 模块的使用，该模块提供了在编辑器或工具中渲染 nDisplay 场景预览的能力。

### 头文件引入

```cpp
#include "IDisplayClusterScenePreview.h"
#include "DisplayClusterScenePreviewEnums.h"
#include "DisplayClusterRootActor.h"
```

### 基本用法

创建并配置一个简单的场景预览渲染器。

```cpp
// 获取场景预览模块接口
IDisplayClusterScenePreview& ScenePreviewModule = IDisplayClusterScenePreview::Get();

// 创建一个渲染器实例
int32 RendererId = ScenePreviewModule.CreateRenderer();

// 假设你已经有一个指向场景中 ADisplayClusterRootActor 的指针
ADisplayClusterRootActor* MyRootActor = /* ... */;

// 设置渲染器的根 Actor 和属性覆盖（例如，覆盖某些显示配置）
FDisplayClusterRootActorPropertyOverrides PropertyOverrides;
PropertyOverrides.bOverride_AllowICVFX = true;
PropertyOverrides.AllowICVFX = false; // 示例：禁用 ICVFX 以进行简单预览

// 设置根 Actor，并启用自动更新 Stage Actors（如 Light Card）
EDisplayClusterScenePreviewFlags PreviewFlags = EDisplayClusterScenePreviewFlags::AutoUpdateStageActors;
ScenePreviewModule.SetRendererRootActor(RendererId, MyRootActor, PropertyOverrides, PreviewFlags);
```

### 进阶用法

在编辑器 Tick 或定时器中执行异步队列渲染，并处理结果。

```cpp
// ... (接上文，已有 RendererId)

// 定义渲染设置
FDisplayClusterMeshProjectionRenderSettings RenderSettings;
RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::MPCDI; // 使用 MPCDI 投影
RenderSettings.bWarpBlend = true;
// ... 其他设置

// 定义渲染结果大小
FIntPoint RenderSize(1920, 1080);

// 定义结果回调委托
FRenderResultDelegate ResultDelegate;
ResultDelegate.BindLambda([this](FRenderTarget* RenderTarget)
{
    if (RenderTarget)
    {
        // 渲染成功，可以获取纹理数据，例如用于 UI 显示或保存为文件
        // FTexture2DRHIRef TextureRHI = RenderTarget->GetRenderTargetTexture();
        UE_LOG(LogTemp, Log, TEXT("Preview render completed successfully."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Preview render failed."));
    }
});

// 将渲染任务加入队列
bool bQueued = ScenePreviewModule.RenderQueued(RendererId, RenderSettings, RenderSize, ResultDelegate);

// 在对象销毁或不再需要时，记得销毁渲染器
// ScenePreviewModule.DestroyRenderer(RendererId);
```

## Demo 示例

以下是一个简单的控制台测试程序，演示如何使用 `DisplayClusterScenePreview` 模块来渲染一个 nDisplay 场景。

### MyScenePreviewTest.h
```cpp
// MyScenePreviewTest.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterRootActor.h"

class FMyScenePreviewTest
{
public:
    FMyScenePreviewTest();
    ~FMyScenePreviewTest();

    /** 初始化渲染器并设置根 Actor */
    void Initialize(ADisplayClusterRootActor* InRootActor);

    /** 执行一次同步渲染 */
    void RenderPreview();

    /** 清理资源 */
    void Cleanup();

private:
    /** 场景预览渲染器 ID */
    int32 PreviewRendererId = INDEX_NONE;

    /** 缓存的根 Actor 弱引用 */
    TWeakObjectPtr<ADisplayClusterRootActor> CachedRootActor;
};
```

### MyScenePreviewTest.cpp
```cpp
// MyScenePreviewTest.cpp
#include "MyScenePreviewTest.h"
#include "IDisplayClusterScenePreview.h"
#include "Engine/TextureRenderTarget2D.h"
#include "CanvasItem.h"
#include "CanvasTypes.h"

FMyScenePreviewTest::FMyScenePreviewTest()
{
}

FMyScenePreviewTest::~FMyScenePreviewTest()
{
    Cleanup();
}

void FMyScenePreviewTest::Initialize(ADisplayClusterRootActor* InRootActor)
{
    if (!IDisplayClusterScenePreview::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("DisplayClusterScenePreview module is not loaded."));
        return;
    }

    IDisplayClusterScenePreview& ScenePreview = IDisplayClusterScenePreview::Get();

    // 创建渲染器
    PreviewRendererId = ScenePreview.CreateRenderer();
    if (PreviewRendererId == INDEX_NONE)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create scene preview renderer."));
        return;
    }

    // 设置根 Actor
    CachedRootActor = InRootActor;
    FDisplayClusterRootActorPropertyOverrides Overrides;
    if (!ScenePreview.SetRendererRootActor(PreviewRendererId, InRootActor, Overrides, EDisplayClusterScenePreviewFlags::AutoUpdateStageActors))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to set root actor for renderer %d."), PreviewRendererId);
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Scene preview renderer %d initialized for actor '%s'."), PreviewRendererId, *InRootActor->GetName());
    }
}

void FMyScenePreviewTest::RenderPreview()
{
    if (!IDisplayClusterScenePreview::IsAvailable() || PreviewRendererId == INDEX_NONE || !CachedRootActor.IsValid())
    {
        return;
    }

    IDisplayClusterScenePreview& ScenePreview = IDisplayClusterScenePreview::Get();

    // 创建一个临时的渲染目标用于接收结果
    UTextureRenderTarget2D* RenderTarget = NewObject<UTextureRenderTarget2D>();
    RenderTarget->InitAutoFormat(1920, 1080);
    RenderTarget->UpdateResourceImmediate(true);

    // 创建一个 Canvas 绑定到这个渲染目标
    FRenderTarget* CanvasRenderTarget = static_cast<FRenderTarget*>(RenderTarget->GetRenderTargetResource());
    FCanvas Canvas(CanvasRenderTarget, nullptr, FGameTime(), ERHIFeatureLevel::SM5);

    // 定义渲染设置
    FDisplayClusterMeshProjectionRenderSettings Settings;
    Settings.ProjectionType = EDisplayClusterMeshProjectionType::MPCDI;
    Settings.bWarpBlend = true;

    // 执行渲染
    bool bSuccess = ScenePreview.Render(PreviewRendererId, Settings, Canvas);
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Preview rendered to render target '%s'."), *RenderTarget->GetName());
        // 此处可以对 RenderTarget 进行后续操作，如保存到文件等。
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Preview render failed for renderer %d."), PreviewRendererId);
    }

    // 清理临时对象
    Canvas.Flush();
    RenderTarget->MarkAsGarbage();
}

void FMyScenePreviewTest::Cleanup()
{
    if (IDisplayClusterScenePreview::IsAvailable() && PreviewRendererId != INDEX_NONE)
    {
        IDisplayClusterScenePreview::Get().DestroyRenderer(PreviewRendererId);
        PreviewRendererId = INDEX_NONE;
    }
    CachedRootActor = nullptr;
}
```

## 模块依赖

使用 `nDisplay` 插件时，你的项目模块需要依赖以下特定模块（已省略 Core, CoreUObject, Engine 等通用模块）。具体的依赖列表取决于你使用 nDisplay 的哪些功能。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，包含集群管理、节点通信和主 Actor 逻辑。 |
| `DisplayClusterProjection` | 实现各种投影模型（MPCDI、UV、Mesh 等），是渲染输出的关键。 |
| `DisplayClusterWarp` | 提供几何校正（Warp）和边缘融合（Blend）功能。 |
| `DisplayClusterConfiguration` | 处理 nDisplay 配置资产（`.ndisplay`）的加载和解析。 |
| `DisplayClusterMedia` | 与 Unreal Media Framework 集成，用于视频输入/输出（如 DeckLink）。 |
| `SharedMemoryMedia` | 使用共享内存实现低延迟的媒体帧传输，用于节点间或与外部设备的通信。 |
| `ScalableMPCDI` | 第三方库，用于支持可缩放的 MPCDI 格式。 |
| `DisplayClusterScenePreview` | 提供在编辑器中渲染 nDisplay 场景预览的能力，主要用于 Light Card 编辑器等工具。 |
| `DisplayClusterLightCardEditor` | 用于在 nDisplay 编辑器中创建和管理 Light Card 的工具模块。 |
| `DisplayClusterShaders` | 包含 nDisplay 专用的着色器，如用于 Warp/Blend 和 ICVFX 的着色器。 |
| `DisplayClusterMultiUser` | 支持多用户协作编辑 nDisplay 场景。 |
| `DisplayClusterReplication` | 负责 nDisplay Actor 和组件的网络复制。 |
| `DisplayClusterMoviePipeline` | 与 Movie Render Queue 集成，支持渲染 nDisplay 电影序列。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影图表（Movie Graph）和 nDisplay 添加了对 EXR 多层渲染输出的支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay 电影管线：将独立的“WarpBlendAlpha”渲染模式合并到通用的“WarpBlend”模式中，简化了API。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了在多分辨率网格（MRG）中拓扑感知相机命名的问题；修复了 MPCDI/ICVFX 着色器中不透明度 Alpha 通道的问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码的回退路径中，现在会正确处理非默认的显示 Gamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

**活跃维护。** nDisplay 是 Unreal Engine 中功能最复杂、最关键的插件之一，由 Epic Games 专门的团队维护。

1.  **持续更新**：从 git 历史可见，该插件仍在进行频繁的功能性更新和 Bug 修复（最近提交在 2026 年），以支持新的渲染管线（如 Movie Graph）、虚拟制片工作流和硬件集成。
2.  **核心地位**：它是 Unreal Engine 在大型可视化、虚拟制片和沉浸式体验领域的支柱技术，Epic 有强烈的动力保持其稳定和先进。
3.  **复杂性与稳定性**：由于其庞大的规模和深度集成的特性，使用前需要一定的学习曲线。但作为官方插件，其稳定性和文档（虽然分散）是有保障的。
4.  **推荐使用**：对于任何涉及多屏幕同步渲染、LED 虚拟制片或复杂显示系统的项目，nDisplay 是**官方推荐且唯一成熟**的解决方案。它不是实验性项目，而是生产级工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：虽然 .uplugin 中 DocsURL 为空，但 Epic 提供了详尽的 nDisplay 文档，通常位于 Unreal Engine 文档网站的“可视化和模拟”或“虚拟制片”部分。
- 测试用例：nDisplay 的测试主要位于 `Engine/Source/Runtime/Engine/Tests/` 和各模块的 `Private/Tests` 目录下，例如 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`。