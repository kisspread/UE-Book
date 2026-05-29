# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterEditor` (Runtime), ... 及其他多个子模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE 中用于驱动大型、复杂沉浸式显示系统的核心框架。它超越了简单的多屏输出，专注于解决**跨多台物理计算机（PC）的视图同步与渲染**问题。其核心是通过**集群（Cluster）** 架构，由一台主节点（Master）控制多台渲染节点（Slaves），确保所有节点在时间和空间上完美同步地渲染场景的不同视口，从而拼接出一个无缝、高分辨率的大型画面或立体视觉效果。

该插件解决了在虚拟制片（LED墙）、主题公园飞行影院、驾驶模拟器、CAVE（洞穴自动虚拟环境）等场景中，使用单台PC性能不足或需要特殊投影变形（如鱼眼、穹顶）的技术难题。它内置了多种非线性投影（如方位角等距投影）以适应各种曲面屏幕。

## 使用场景

- **LED墙虚拟制片**：在电影拍摄现场，使用多台PC驱动环绕拍摄的巨型LED屏幕，实时渲染并同步演员身后的虚拟场景。
- **CAVE沉浸式系统**：创建由多面投影墙组成的沉浸式房间，每面墙由独立PC渲染，提供完全包围的视觉体验。
- **主题公园飞行影院**：驱动穹顶形屏幕，使用鱼眼或球面投影为观众提供环绕式飞行模拟。
- **多通道视觉模拟器**：用于军事或飞行训练，使用多个高分辨率屏幕提供广阔的视野。
- **复杂的多屏艺术装置**：艺术家利用nDisplay创建跨越多个物理显示器的同步互动视觉作品。

## 蓝图用法

nDisplay 的核心运行时功能主要通过 `FDisplayClusterMeshProjectionRenderer`（用于编辑器预览和特定应用）和通过配置资产驱动的完整渲染管线提供。以下是编辑器和预览相关的核心蓝图节点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddActor` | 将一个Actor的所有可渲染组件添加到投影渲染器的渲染列表中 | `FDisplayClusterMeshProjectionRenderer` |
| `AddActor (带过滤器)` | 将一个Actor添加到渲染列表，并使用回调函数过滤哪些组件需要被渲染 | `FDisplayClusterMeshProjectionRenderer` |
| `RemoveActor` | 将一个Actor的所有可渲染组件从渲染列表中移除 | `FDisplayClusterMeshProjectionRenderer` |
| `ClearScene` | 清空投影渲染器的整个渲染列表 | `FDisplayClusterMeshProjectionRenderer` |
| `Render` | 使用指定的投影类型和设置，将当前渲染列表中的对象渲染到目标画布上 | `FDisplayClusterMeshProjectionRenderer` |
| `ProjectViewPosition` | 将一个普通视图空间坐标投影到指定投影类型（如方位角投影）的非线性空间 | `FDisplayClusterMeshProjectionRenderer` (静态) |
| `UnprojectViewPosition` | 将一个非线性投影空间的坐标反投影回普通视图空间 | `FDisplayClusterMeshProjectionRenderer` (静态) |

### 使用示例（蓝图描述）

1.  **创建渲染器**：在蓝图中，首先需要获取或创建一个 `FDisplayClusterMeshProjectionRenderer` 实例。
2.  **添加对象**：使用 `AddActor` 节点，将你希望被特殊投影渲染的Actor（例如，一个代表场景的Actor）添加到渲染器中。你可以通过带过滤器的版本来只渲染该Actor的特定组件。
3.  **配置设置**：创建一个 `FDisplayClusterMeshProjectionRenderSettings` 结构体变量。在此结构中，你需要设置：
    - `ProjectionType`：选择投影类型，例如 `Azimuthal`（方位角投影，适合球幕）。
    - `RenderType`：设置输出内容，`Color` 用于正常颜色渲染，`Normals` 用于渲染法线深度图。
    - `EngineShowFlags`：配置渲染器显示哪些效果（如后处理、光照）。
4.  **执行渲染**：调用 `Render` 节点，传入你的画布（Canvas）、场景（Scene）和步骤3中配置的设置结构体。渲染器会将添加的物体以你选择的非线性投影方式绘制到画布上。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMeshProjectionRenderer.h"
```

### 基本用法

从 `DisplayClusterMeshProjectionRenderer.h` 中提取的用法示例，展示了如何使用非线性投影渲染一个场景。

```cpp
// 假设在某个编辑器工具或测试代码中
#include "DisplayClusterMeshProjectionRenderer.h"

// 1. 创建投影渲染器实例
TUniquePtr<FDisplayClusterMeshProjectionRenderer> MeshProjectionRenderer = MakeUnique<FDisplayClusterMeshProjectionRenderer>();

// 2. 添加要渲染的Actor
AActor* MySceneActor = GetWorld()->SpawnActor<AActor>();
MeshProjectionRenderer->AddActor(MySceneActor);

// 3. 配置渲染设置
FDisplayClusterMeshProjectionRenderSettings RenderSettings;
RenderSettings.ProjectionType = EDisplayClusterMeshProjectionType::Azimuthal; // 使用方位角等距投影
RenderSettings.RenderType = EDisplayClusterMeshProjectionOutput::Color; // 渲染颜色
// 可以进一步配置 ViewInitOptions, EngineShowFlags 等

// 4. 在渲染循环或需要时执行渲染
// 假设有一个有效的Canvas和SceneInterface
if (FCanvas* Canvas = GetCanvas() && FSceneInterface* Scene = GetWorld()->Scene)
{
    MeshProjectionRenderer->Render(Canvas, Scene, RenderSettings);
}

// 5. 清理（通常在对象销毁时自动处理）
MeshProjectionRenderer->ClearScene();
```
*(示例逻辑基于 `DisplayClusterMeshProjectionRenderer.h` 中的类接口推断)*

### 进阶用法

组合使用投影变换和过滤功能：

```cpp
// 创建一个UV投影变换，用于将3D空间中的点映射到UV空间（常用于自定义纹理映射）
FDisplayClusterMeshProjectionTransform UVProjectionTransform(
    EDisplayClusterMeshProjectionType::UV,
    FMatrix::Identity
);

// 将世界坐标投影到UV投影空间
FVector WorldPos(100.f, 200.f, 300.f);
FVector ProjectedPos = UVProjectionTransform.ProjectPosition(WorldPos);

// 反向投影回世界坐标
FVector ReconstructedWorldPos = UVProjectionTransform.UnprojectPosition(ProjectedPos);

// 使用过滤器，只渲染特定组件
MeshProjectionRenderer->AddActor(MyComplexActor, [](const UPrimitiveComponent* Comp)
{
    // 只渲染名称包含“Visual”的组件
    return Comp->GetName().Contains(TEXT(“Visual”));
});

// 通过委托控制Actor是否被标记为选中（影响编辑器轮廓）
MeshProjectionRenderer->ActorSelectedDelegate.BindLambda([](const AActor* Actor)
{
    return Actor == MySelectedActor;
});
```
*(进阶用法基于 `FDisplayClusterMeshProjectionTransform` 和 `FDisplayClusterMeshProjectionPrimitiveFilter` 的实现)*

## Demo 示例

一个最小化的 C++ 示例，演示如何使用 `FDisplayClusterMeshProjectionRenderer` 进行方位角投影渲染。

**LightCardProjector.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterMeshProjectionRenderer.h"

class FLightCardProjector
{
public:
    FLightCardProjector();
    ~FLightCardProjector();

    void Initialize(UWorld* World);
    void RenderToCanvas(FCanvas* Canvas);

private:
    TUniquePtr<FDisplayClusterMeshProjectionRenderer> Renderer;
    FDisplayClusterMeshProjectionRenderSettings Settings;
};
```

**LightCardProjector.cpp**
```cpp
#include "LightCardProjector.h"

FLightCardProjector::FLightCardProjector()
    : Renderer(MakeUnique<FDisplayClusterMeshProjectionRenderer>())
{
}

FLightCardProjector::~FLightCardProjector()
{
    Renderer.Reset();
}

void FLightCardProjector::Initialize(UWorld* World)
{
    // 清空并重新添加目标Actor
    Renderer->ClearScene();
    
    // 查找并添加场景中所有标记为“ProjectionTarget”的Actor
    for (TActorIterator<AActor> It(World); It; ++It)
    {
        if (It->Tags.Contains(FName("ProjectionTarget")))
        {
            Renderer->AddActor(*It);
        }
    }

    // 配置为方位角投影，用于球幕
    Settings.ProjectionType = EDisplayClusterMeshProjectionType::Azimuthal;
    Settings.RenderType = EDisplayClusterMeshProjectionOutput::Color;
    Settings.ViewInitOptions.ViewOrigin = FVector::ZeroVector;
    // ... 可以进一步配置FOV、旋转等
}

void FLightCardProjector::RenderToCanvas(FCanvas* Canvas)
{
    if (!Canvas) return;
    
    // 需要有效的场景指针，通常从UWorld获取
    FSceneInterface* Scene = GWorld->Scene;
    if (Scene && Renderer.IsValid())
    {
        Renderer->Render(Canvas, Scene, Settings);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `SharedMemoryMedia` | 用于在集群节点之间通过共享内存高效传输渲染的媒体纹理 |
| `ScalableMPCDI` | 第三方库，提供对 MPCDI（多通道投影显示接口）格式的支持，用于定义复杂的投影几何校正 |
| `D3D12RHI` | 用于高级图形API交互，特别是在媒体共享和某些渲染路径中 |
| `UnrealEd` | 提供编辑器集成，用于配置工具、预览和资产编辑 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为MovieGraph和nDisplay添加了EXR多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | nDisplay电影管线：将WarpBlendAlpha模式合并到WarpBlend中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复MRG中拓扑感知摄像机命名问题；修复MPCDI/ICVFX着色器中的不透明Alpha。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay：在输出帧编码回退路径中支持非默认的DisplayGamma。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当GUI纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

- **维护状态**：**活跃维护**。最近一次提交在 2026 年 5 月，且提交内容涉及功能增强（EXR支持）和多个Bug修复，表明 Epic Games 持续投入开发。
- **创建年龄**：插件创建于 2018 年，已有约 8 年历史，是一个成熟的核心功能插件。
- **功能完整性**：插件功能非常全面，覆盖了集群渲染的核心需求，包括投影、同步、媒体传输和编辑器工具。
- **稳定性**：从近期提交看，团队仍在修复特定场景（如GPU、特定格式、编辑器工具）下的问题，说明在复杂应用中可能仍存在边缘情况。
- **推荐使用**：**强烈推荐**。对于任何涉及多PC同步渲染、虚拟制片、沉浸式显示的UE项目，nDisplay 是官方且功能最完整的解决方案。尽管默认未启用（`EnabledByDefault: false`），但它并非实验性功能，而是面向特定高端应用场景的必备工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档]() (当前.uplugin中未提供链接，请查阅UE官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) (位于插件源码内部)