# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于多PC集群同步渲染的UE插件系统，主要用于驱动大型LED墙、穹幕投影、CAVE系统等复杂的多屏幕显示环境。它解决了以下核心问题：

1.  **多视口同步**：协调多台PC上的多个引擎实例，确保它们渲染同一场景的特定视口（Viewport），并保持帧同步。
2.  **非线性投影**：支持将渲染结果投影到非平面的显示表面（如球幕、圆柱幕、异形屏），内置了方位角等距投影（Azimuthal）和UV投影。
3.  **工作流管理**：提供从配置、预览、校准到最终渲染的完整工作流，包括与媒体捕获、多用户编辑、远程控制等系统的集成。

`DisplayClusterLightCardEditorShaders` 模块是 nDisplay 生态的一部分，专门提供了在编辑器中预览灯光卡（Light Card）效果所需的**非线性网格投影渲染器**。它能将3D场景中的物体（如灯光卡）渲染到2D画布上，并应用特定的投影变换，以便艺术家在编辑器中就能直观地看到最终在LED墙上显示的投射效果。

## 使用场景

-   你在开发一个大型沉浸式LED墙项目（如虚拟制片片场） → 使用 nDisplay 整体驱动渲染，使用 `DisplayClusterLightCardEditorShaders` 在编辑器中预览灯光卡的投射效果。
-   你需要为穹幕影院或CAVE系统创建内容 → 使用 nDisplay 配置多视口和非线性投影。
-   你正在使用 nDisplay，并且需要创建和调整用于模拟实体光源的“灯光卡” → 使用 `DisplayClusterLightCardEditor` 和 `DisplayClusterLightCardEditorShaders` 模块进行编辑和实时预览。

## 蓝图用法

`DisplayClusterLightCardEditorShaders` 模块主要为底层渲染功能提供C++接口，其公开的 `UFUNCTION`/`UPROPERTY` 较少，主要通过委托（Delegate）进行交互。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShouldRenderPrimitiveDelegate` | 委托，用于判断一个组件是否应该被渲染到投影画布上 | `FDisplayClusterMeshProjectionPrimitiveFilter` |
| `ShouldApplyProjectionDelegate` | 委托，用于判断一个组件是否应该应用非线性投影（而非线性渲染） | `FDisplayClusterMeshProjectionPrimitiveFilter` |
| `ActorSelectedDelegate` | 委托，用于判断一个Actor在渲染时是否应显示选中轮廓 | `FDisplayClusterMeshProjectionRenderer` |
| `RenderSimpleElementsDelegate` | 委托，允许在渲染管线的最后添加简单的绘制元素（如线、点） | `FDisplayClusterMeshProjectionRenderer` |

### 使用示例（蓝图描述）

在蓝图中直接使用该模块较为少见，它主要服务于编辑器工具。工作流通常是：
1.  在编辑器中创建或选择一个“灯光卡”Actor。
2.  `DisplayClusterLightCardEditor` 模块会调用 `DisplayClusterLightCardEditorShaders` 提供的渲染器。
3.  渲染器根据配置（如投影类型、UV索引）将场景渲染到编辑器的一个预览窗口中。
4.  通过上述委托，编辑器工具可以精细控制哪些物体参与渲染、是否应用投影以及选中状态的外观。

## C++ 用法

该模块的核心是 `FDisplayClusterMeshProjectionRenderer` 类，它管理一组待渲染的 `UPrimitiveComponent`，并使用特定的投影类型将它们渲染到 `FCanvas`。

### 头文件引入

```cpp
#include "DisplayClusterMeshProjectionRenderer.h"
```

### 基本用法

以下示例展示了如何使用投影渲染器来渲染一个Actor，并输出颜色信息。

**来源文件**: `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders/Public/DisplayClusterMeshProjectionRenderer.h`

```cpp
// 1. 创建渲染器实例
FDisplayClusterMeshProjectionRenderer ProjectionRenderer;

// 2. 将你关心的Actor（例如灯光卡）添加到渲染列表
AActor* MyLightCardActor = ...; // 获取你的灯光卡Actor
ProjectionRenderer.AddActor(MyLightCardActor);

// 3. 配置渲染设置
FDisplayClusterMeshProjectionRenderSettings RenderSettings;
RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::Azimuthal; // 使用方位角等距投影
RenderSettings.RenderType = EDisplayClusterMeshProjectionOutput::Color;       // 输出颜色
// 通常还需要设置 ViewInitOptions（视图矩阵、投影矩阵等）

// 4. 在游戏线程或渲染线程调用Render，将结果绘制到画布上
FCanvas* Canvas = ...; // 获取目标画布（例如来自一个SViewport）
FSceneInterface* Scene = GetWorld()->GetScene();
ProjectionRenderer.Render(Canvas, Scene, RenderSettings);
```

### 进阶用法

你可以通过过滤器控制哪些组件参与渲染，以及通过委托添加自定义渲染内容。

**来源文件**: `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders/Public/DisplayClusterMeshProjectionRenderer.h`

```cpp
// 使用带过滤器的AddActor方法，只渲染特定组件
ProjectionRenderer.AddActor(MyLightCardActor, [](const UPrimitiveComponent* Comp) -> bool
{
    // 例如，只渲染静态网格组件
    return Comp->IsA<UStaticMeshComponent>();
});

// 通过委托，在渲染完成后添加简单的线条
ProjectionRenderer.RenderSimpleElementsDelegate.BindLambda([](const FSceneView* View, FPrimitiveDrawInterface* PDI)
{
    // 在画布的特定位置绘制一个红色的点，用于调试或指示
    PDI->DrawPoint(FVector(0, 0, 100), FLinearColor::Red, 10.f, SDPG_Foreground);
});

// 通过委托控制选中状态
ProjectionRenderer.ActorSelectedDelegate.BindLambda([](const AActor* Actor) -> bool
{
    return Actor->ActorHasTag(FName("SelectedForPreview"));
});

// 动态移除不再需要的Actor
ProjectionRenderer.RemoveActor(MyOldActor);
ProjectionRenderer.ClearScene(); // 或者清空所有
```

## Demo 示例

一个最小化的示例，展示如何在自定义编辑器工具中集成投影渲染器来预览一个立方体。

**LightCardPreviewComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "DisplayClusterMeshProjectionRenderer.h"

class ULightCardPreviewComponent : public UActorComponent
{
public:
    virtual void BeginPlay() override;

    // 调用此函数来触发一次预览渲染
    void RenderPreview(class FCanvas* Canvas);

private:
    FDisplayClusterMeshProjectionRenderer MeshProjectionRenderer;
};
```

**LightCardPreviewComponent.cpp**
```cpp
#include "LightCardPreviewComponent.h"
#include "Engine/StaticMeshActor.h"
#include "CanvasTypes.h"

void ULightCardPreviewComponent::BeginPlay()
{
    Super::BeginPlay();

    // 假设场景中有一个标记为“PreviewTarget”的立方体Actor
    TArray<AActor*> TargetActors;
    UGameplayStatics::GetAllActorsWithTag(GetWorld(), FName("PreviewTarget"), TargetActors);

    if (TargetActors.Num() > 0)
    {
        // 将其添加到渲染器
        MeshProjectionRenderer.AddActor(TargetActors[0]);
    }
}

void ULightCardPreviewComponent::RenderPreview(FCanvas* Canvas)
{
    if (!Canvas) return;

    // 使用编辑器默认的视图设置
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::Linear; // 使用简单线性投影

    // 通常需要从编辑器视口获取正确的视图矩阵和投影矩阵
    // 这里为了演示，使用一个简化的设置
    FSceneViewInitOptions ViewInitOptions;
    ViewInitOptions.ViewOrigin = FVector(0, 0, 500);
    ViewInitOptions.ViewRotationMatrix = FInverseRotationMatrix(FRotator(0, 0, 0));
    ViewInitOptions.ProjectionMatrix = FReversedZPerspectiveMatrix(90.f, 1.f, 1.f);
    RenderSettings.ViewInitOptions = ViewInitOptions;

    // 获取场景并渲染
    if (UWorld* World = GetWorld())
    {
        MeshProjectionRenderer.Render(Canvas, World->GetScene(), RenderSettings);
    }
}
```

## 模块依赖

`DisplayClusterLightCardEditorShaders` 模块依赖于 `UnrealEd`，因此它是一个**编辑器相关的模块**。尽管其模块类型标记为 Runtime，但很可能主要在编辑器环境下使用。

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 访问编辑器相关的功能，如选择、视图等 |
| `RenderCore`, `Renderer` | 底层渲染系统依赖 |
| `DisplayClusterConfiguration` | 可能用于读取nDisplay的投影配置 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为nDisplay的MovieGraph管线添加了EXR多层渲染支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了电影管线中的WarpBlend和WarpBlendAlpha模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多渲染图中的摄像机命名和着色器中的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码时未尊重非默认显示伽马设置的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时出现的闪烁问题 |

### 维护评价

**活跃维护**。nDisplay作为Epic Games官方支持的核心虚拟制片技术栈组件，持续得到更新和功能增强。从近期提交记录看，开发团队正在积极完善其电影管线集成、渲染稳定性和多用户工作流。该模块是UE虚拟制片生产流程中不可或缺的一部分，**强烈推荐**在相关项目中使用。唯一需要注意的是它默认禁用，需要在项目设置中手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) (UE5 nDisplay文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)