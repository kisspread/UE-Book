# DisplayClusterLightCardEditorShaders

> 支持使用多台PC进行同步集群渲染（单目或立体）。

| 属性 | 值 |
|---|---|
| 中文名 | 光线卡编辑器着色器 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayClusterLightCardEditorShaders` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders) | |

## 用途

`DisplayClusterLightCardEditorShaders` 模块是 nDisplay 插件的一个子模块，其核心功能是为 **nDisplay 光线卡（Light Card）编辑器**提供**非线性网格投影渲染**能力。

简单来说，它解决的是在 UE 编辑器中 **预览** 场景内容在 nDisplay 所驱动的非平面屏幕（如 LED 弧形墙、CAVE 系统等）上显示效果的问题。传统的平面视口预览无法准确反映内容在复杂投影下的变形情况，而此模块通过自定义的渲染器（`FDisplayClusterMeshProjectionRenderer`），支持将场景中的 Actor（或其组件）按照特定的投影算法（如方位角等距投影）渲染到编辑器的画布上，从而让设计师能够直观地看到并调整内容在最终显示设备上的呈现效果。

它是 nDisplay 工作流程中**编辑器预览和调试**环节的关键技术支撑。

## 使用场景

- **配置大型 LED 墙**：你在为虚拟制片（Virtual Production）设置一块由多台机器驱动的大型弧形 LED 屏幕时，需要在 UE 编辑器中实时预览摄像机视图在该屏幕上的正确投影和变形情况，使用此模块提供的渲染器进行预览。
- **调试 CAVE 系统投影**：你在搭建一个 CAVE（洞穴自动虚拟环境）沉浸式房间，需要在编辑器里检查不同视角下的图像如何被“贴合”到房间的各个墙面，利用其支持的非线性投影类型进行可视化。
- **光线卡（Light Card）布局调整**：nDisplay 使用“光线卡”在特定屏幕上添加环境光照或反射。你需要使用此模块提供的渲染器来绘制这些光线卡的投影预览，确保它们在屏幕上渲染出正确形状和位置。

## 蓝图用法

根据提供的头文件分析，`DisplayClusterLightCardEditorShaders` 模块主要提供底层 C++ API 供其他编辑器工具（如 nDisplay 光线卡编辑器）调用，**并未暴露直接给蓝图使用的 `BlueprintCallable` 函数**。

用户通过 nDisplay 插件提供的**编辑器 UI**（如 nDisplay 配置编辑器、光线卡编辑器窗口）间接使用此模块的功能。

## C++ 用法

此模块的核心类是 `FDisplayClusterMeshProjectionRenderer`，它管理要渲染的组件列表，并支持多种投影模式。

### 头文件引入

```cpp
#include "DisplayClusterMeshProjectionRenderer.h"
```

### 基本用法

以下示例演示了如何创建一个网格投影渲染器，添加一个 Actor，并使用方位角投影将其渲染到编辑器画布上。

```cpp
// 假设在某个编辑器工具代码中
#include "DisplayClusterMeshProjectionRenderer.h"
#include "CanvasItem.h"
#include "CanvasTypes.h"

void PreviewActorOnCurvedScreen(AActor* ActorToPreview, UCanvas* Canvas)
{
    // 1. 创建渲染器实例
    FDisplayClusterMeshProjectionRenderer MeshProjectionRenderer;

    // 2. 将目标 Actor 添加到渲染列表
    MeshProjectionRenderer.AddActor(ActorToPreview);

    // 3. 配置渲染设置
    FDisplayClusterMeshProjectionRenderSettings RenderSettings;
    RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::Azimuthal; // 使用方位角等距投影
    RenderSettings.RenderType = EDisplayClusterMeshProjectionOutput::Color; // 输出颜色

    // (可选) 可以设置视图初始化选项，如摄像机位置等
    // RenderSettings.ViewInitOptions = ...;

    // 4. 执行渲染 (传入引擎的画布和场景接口)
    MeshProjectionRenderer.Render(Canvas->GetCanvas(), Canvas->GetScene(), RenderSettings);
}
```

**代码解析**：
1.  创建 `FDisplayClusterMeshProjectionRenderer` 对象作为渲染器。
2.  使用 `AddActor` 将需要预览的 Actor（及其可见的 `UPrimitiveComponent`）注册到渲染器。
3.  配置 `FDisplayClusterMeshProjectionRenderSettings` 结构体，指定投影类型（如 `Azimuthal` 用于弧形屏预览）、输出类型（颜色或法线）等。
4.  调用 `Render` 方法，传入 `UCanvas` 对象（用于绘制 2D 图形）和当前场景，完成投影渲染。

### 进阶用法

**使用法线输出和滤镜**：
可以配置渲染器输出法线/深度信息，这对于后期处理（如光线卡）或调试非常有用，并且支持滤镜来排除特定组件。

```cpp
// ... 接上文
RenderSettings.RenderType = EDisplayClusterMeshProjectionOutput::Normals;
RenderSettings.NormalCorrectionMatrix = ActorToPreview->GetActorTransform().GetRotation().ToMatrixWithScale().Inverse();

// 设置滤镜，只渲染名为 “ScreenMesh” 的组件
RenderSettings.PrimitiveFilter.ShouldRenderPrimitiveDelegate.BindLambda([](const UPrimitiveComponent* Comp) -> bool {
    return Comp->GetName() == TEXT("ScreenMesh");
});

MeshProjectionRenderer.Render(Canvas->GetCanvas(), Canvas->GetScene(), RenderSettings);
```

**多场景渲染**：
支持同时从多个场景（`FSceneInterface`）收集图元进行渲染。

```cpp
TArray<FSceneInterface*> Scenes;
Scenes.Add(GWorld->Scene);
// Scenes.Add(其他场景);
MeshProjectionRenderer.RenderScenes(Canvas->GetCanvas(), Scenes, RenderSettings);
```

## Demo 示例

一个最小化可编译的编辑器工具类示例，该工具在特定操作下使用网格投影渲染器预览场景。

**MyPreviewTool.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterMeshProjectionRenderer.h"

class FMyPreviewTool
{
public:
    void PreviewCurrentSelection(UCanvas* Canvas);

private:
    FDisplayClusterMeshProjectionRenderer Renderer;
    bool bInitialized = false;
};
```

**MyPreviewTool.cpp**
```cpp
#include "MyPreviewTool.h"
#include "CanvasTypes.h"
#include "Engine/Selection.h"
#include "GameFramework/Actor.h"

void FMyPreviewTool::PreviewCurrentSelection(UCanvas* Canvas)
{
    if (!Canvas) return;

    if (!bInitialized)
    {
        // 清空并重新添加选中的 Actor
        Renderer.ClearScene();
        USelection* SelectedActors = GEditor->GetSelectedActors();
        for (FSelectionIterator It(*SelectedActors); It; ++It)
        {
            AActor* Actor = Cast<AActor>(*It);
            if (Actor)
            {
                Renderer.AddActor(Actor);
            }
        }
        bInitialized = true;
    }

    // 使用简单的线性投影进行预览
    FDisplayClusterMeshProjectionRenderSettings Settings;
    Settings.ProjectionType = EDisplayClusterMeshProjectionType::Linear;
    Settings.RenderType = EDisplayClusterMeshProjectionOutput::Color;

    // 渲染到传入的画布上
    Renderer.Render(Canvas->GetCanvas(), GWorld->GetScene(), Settings);
}
```

## 模块依赖

此模块作为 nDisplay 内部模块，其依赖关系在构建时由 `DisplayClusterLightCardEditorShaders.Build.cs` 定义。对于最终用户，如果需要在自己的模块中引用此模块，通常无需直接依赖，因为它是通过 nDisplay 的编辑器功能间接使用的。

若必须直接引用，需确保 `YourModuleName.Build.cs` 文件中包含：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "DisplayClusterLightCardEditorShaders"
});
PrivateDependencyModuleNames.AddRange(new string[] {
    "UnrealEd" // 用于编辑器场景访问、选择等
});
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 管线添加了多层 EXR 输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 优化了电影渲染管线中的扭曲混合模式，将 Alpha 模式合并到主模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多渲染图中拓扑感知摄像机的命名问题，并修正了 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中未遵循非默认 DisplayGamma 设置的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时导致的闪烁问题。 |

### 维护评价

**活跃维护**。该模块作为 nDisplay 插件的核心组成部分，持续获得功能更新和错误修复。从近期的提交记录看，维护频率很高，且涵盖了从渲染管线（MovieGraph）到具体着色器问题的广泛改进。尽管插件整体创建时间较早（约8年），但其内部模块仍在随着 UE 版本迭代和虚拟制片需求而积极演进。**推荐使用**，它是构建专业级 nDisplay 虚拟制片环境不可或缺的工具链组件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterLightCardEditorShaders)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)（nDisplay 整体文档）