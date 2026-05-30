# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（材质、着色器、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterMedia` (Runtime), `SharedMemoryMedia` (Runtime) 等 30 个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的分布式集群渲染系统，解决的核心问题是：**如何让多台 PC 同步渲染同一场景的不同视角，并将画面输出到多块物理屏幕或投影仪上，形成一个完整、无缝的虚拟环境**。

典型应用场景包括 CAVE 系统（沉浸式立方体投影室）、LED 虚拟摄影棚（如 ICVFX/In-Camera VFX）、穹顶投影、环幕驾驶模拟器，以及任何需要多台机器协同渲染的大型显示系统。

nDisplay 通过一个 `ADisplayClusterRootActor`（DCRA）在场景中定义整个集群的拓扑结构——哪些 PC 负责哪些视口、如何投影（平面/球面/MPCDI）、如何变形混合（WarpBlend）——然后由集群中的每个节点同步执行渲染，保证所有屏幕的画面在时间上完全对齐。

本文档重点介绍 **DisplayClusterMoviePipeline** 子模块，它将 nDisplay 集成到 Movie Render Pipeline（MRP）和 Movie Render Graph（MRG）中，使你能够以离线、高质量的方式渲染 nDisplay 配置，用于影视级输出。

## 使用场景

- 你正在搭建 LED 虚拟摄影棚（ICVFX）→ 需要用 nDisplay 管理多块 LED 屏的渲染和投影
- 你有一个 CAVE 系统需要多台 PC 同步渲染不同墙壁的画面 → 用 nDisplay 配置集群拓扑
- 你需要将 nDisplay 集群的渲染结果通过 Movie Pipeline 离线录制为高质量视频或 EXR 序列 → 用 DisplayClusterMoviePipeline
- 你需要将 nDisplay 的渲染结果输出为 360° 等距柱状投影的全景图 → 选择 FullProjection 输出模式
- 你需要将多个 nDisplay 视口的渲染结果合并到一个多层 EXR 文件中 → 使用 EXR Layer Grouping 功能

## 蓝图用法

DisplayClusterMoviePipeline 模块主要通过 Movie Pipeline 的设置和渲染节点来使用，蓝图交互以配置为主。

### 核心属性

#### 渲染通道节点（Deferred / PathTracer）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `OutputMethod` | nDisplay 输出方式：逐视口、逐节点输出映射、全集群输出映射、180°/360° 等距柱状投影、自定义网格投影 | `UDisplayClusterMovieGraphDeferredRenderPassNode` / `UDisplayClusterMovieGraphPathTracerRenderPassNode` |
| `ResolutionScale` | 统一缩放视口分辨率 [0.01, 1.0] | 同上 |
| `OutputResolution` | 覆盖输出分辨率 | 同上 |
| `WarpBlendMode` | 变形混合模式：None 或 WarpBlend | 同上 |
| `StereoMode` | 立体渲染模式：无、立体、仅左眼、仅右眼 | 同上 |
| `OverscanMode` | 过扫描来源：默认（MRP）或 nDisplay 视口 | 同上 |
| `RootActorRef` | 指定使用的 nDisplay Root Actor | 同上 |
| `AllowedViewportNamesList` | 仅渲染指定视口 | 同上 |
| `AllowedNodeNamesList` | 仅渲染指定集群节点 | 同上 |
| `EXRLayerGrouping` | 多层 EXR 分组方式：无、按视口、按节点、按集群 | 同上 |

#### 渲染通道（Viewport Pass）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `bEnabledWarpBlend` | 是否启用变形混合 | `UDisplayClusterMoviePipelineViewportPassBase` |

#### Movie Pipeline 设置

| 属性 | 说明 | 所在类 |
|---|---|---|
| `Configuration.DCRootActor` | 指定 DC Root Actor 引用 | `UDisplayClusterMoviePipelineSettings` |
| `Configuration.bUseViewportResolutions` | 使用 nDisplay 视口分辨率 | 同上 |
| `Configuration.bRenderAllViewports` | 渲染所有视口 | 同上 |
| `Configuration.AllowedViewportNamesList` | 仅渲染指定视口列表 | 同上 |

### 使用示例（蓝图描述）

在 Movie Render Queue 的作业配置中：

1. 添加 `nDisplay` 设置（`UDisplayClusterMoviePipelineSettings`），配置要使用的 DC Root Actor
2. 在渲染通道中选择 `nDisplay Rendering`（Lit）、`nDisplay Rendering (Unlit)`、`nDisplay Path Tracer` 等通道之一
3. 如果使用 Movie Render Graph，在图中添加 `DisplayClusterMovieGraphDeferredRenderPassNode` 或 `DisplayClusterMovieGraphPathTracerRenderPassNode`
4. 在节点属性中设置 OutputMethod、StereoMode、WarpBlendMode 等
5. 通过 `AllowedViewportNamesList` 筛选要渲染的视口

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMoviePipelineViewportPass.h"
#include "DisplayClusterMoviePipelineSettings.h"
#include "DisplayClusterMoviePipelineEnums.h"
#include "DisplayClusterMovieGraphRenderCameraSource.h"
```

### 基本用法 — 配置 Movie Pipeline Settings

通过 C++ 动态配置 nDisplay 的 Movie Pipeline 设置。

```cpp
// 来源: Public/DisplayClusterMoviePipelineSettings.h
#include "DisplayClusterMoviePipelineSettings.h"

// 获取 nDisplay Movie Pipeline 设置并配置
UDisplayClusterMoviePipelineSettings* NdSettings = NewObject<UDisplayClusterMoviePipelineSettings>();
NdSettings->Configuration.bUseViewportResolutions = true;
NdSettings->Configuration.bRenderAllViewports = false;

// 仅渲染指定视口
NdSettings->Configuration.AllowedViewportNamesList.Add(TEXT("VP_Camera1"));
NdSettings->Configuration.AllowedViewportNamesList.Add(TEXT("VP_Camera2"));

// 将设置添加到 Movie Pipeline 配置
UMoviePipeline* Pipeline = ...; // 已有的 Movie Pipeline 实例
Pipeline->GetConfiguration()->FindOrAddSettingByClass(UDisplayClusterMoviePipelineSettings::StaticClass());
```

### 基本用法 — 查询可用视口

```cpp
// 来源: Public/DisplayClusterMoviePipelineSettings.h
#include "DisplayClusterMoviePipelineSettings.h"

UDisplayClusterMoviePipelineSettings* Settings = GetNdSettings();
TArray<FString> ViewportNames;
TArray<FIntPoint> ViewportResolutions;

// 获取当前世界的 nDisplay 视口列表及其分辨率
if (Settings->GetViewports(GetWorld(), ViewportNames, ViewportResolutions))
{
    for (int32 i = 0; i < ViewportNames.Num(); ++i)
    {
        UE_LOG(LogTemp, Log, TEXT("Viewport: %s, Resolution: %dx%d"),
            *ViewportNames[i], ViewportResolutions[i].X, ViewportResolutions[i].Y);
    }
}
```

### 进阶用法 — 使用 ViewportManager 管理渲染帧

```cpp
// 来源: Private/DisplayClusterMoviePipelineViewportManager.h
#include "DisplayClusterMoviePipelineViewportManager.h"

// 为特定集群节点创建视口管理器
const FString ClusterNodeId = TEXT("Node_0");
ADisplayClusterRootActor* RootActor = GetRootActor();

FDisplayClusterMoviePipelineViewportManager ViewportManager(ClusterNodeId, RootActor);

// 配置渲染设置
UE::DisplayClusterMoviePipeline::FRenderSettings RenderSettings;
RenderSettings.RenderMode = EDisplayClusterRenderFrameMode::Mono;
RenderSettings.WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend;
RenderSettings.RenderResolutionScale = 1.0f;

// 开始新帧的渲染
if (ViewportManager.BeginNewFrame(RenderSettings))
{
    // 渲染帧已构建成功，RenderFrame 中包含了所有视口的渲染数据
    // 实际渲染由 Movie Pipeline 系统驱动
}
```

### 进阶用法 — 解析 Root Actor

```cpp
// 来源: Private/DisplayClusterMoviePipelineViewportManager.h
// 根据软引用和类引用来查找最佳匹配的 DCRA
UMovieSceneSequencePlayer* SequencePlayer = GetSequencePlayer();
TSoftObjectPtr<ADisplayClusterRootActor> PreferredActor = nullptr; // 不指定特定 Actor
TSoftClassPtr<ADisplayClusterRootActor> PreferredClass = nullptr;  // 不指定特定类

ADisplayClusterRootActor* ResolvedActor = FDisplayClusterMoviePipelineViewportManager::ResolveRootActor(
    SequencePlayer,
    PreferredActor,
    PreferredClass
);

if (ResolvedActor)
{
    // 找到了可用的 DCRA，可以用于渲染
    UE_LOG(LogTemp, Log, TEXT("Resolved DCRA: %s"), *ResolvedActor->GetName());
}
```

### 进阶用法 — Movie Render Graph Camera Source

```cpp
// 来源: Private/Graph/DisplayClusterMovieGraphRenderCameraSource.h
#include "DisplayClusterMovieGraphRenderCameraSource.h"

// 在 Movie Graph 渲染流程中，nDisplay 通过 FDisplayClusterMovieGraphRenderCameraSource
// 将 nDisplay 视口映射为 MRG 相机

FDisplayClusterMovieGraphRenderCameraSource CameraSource;

// 初始化：解析 DCRA、枚举视口、创建每节点的 ViewportManager
bool bSuccess = CameraSource.Initialize(RenderPassNode, MovieGraphPipeline, EvaluatedConfig);

if (bSuccess)
{
    // 查询相机数量（每个视口上下文 = 一个相机）
    int32 NumCameras = CameraSource.GetNumCameras();

    for (int32 i = 0; i < NumCameras; ++i)
    {
        FString CameraName;
        CameraSource.GetCameraName(i, CameraName);

        FMinimalViewInfo ViewInfo;
        CameraSource.GetCameraViewInfo(i, ViewInfo);

        UE_LOG(LogTemp, Log, TEXT("Camera %d: %s, FOV: %.1f"), i, *CameraName, ViewInfo.FOV);
    }
}
```

## Demo 示例

以下示例展示如何创建一个自定义的 Movie Pipeline 渲染通道来利用 nDisplay 视口。

```cpp
// MyNdDisplayRenderJob.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterMoviePipelineViewportManager.h"
#include "DisplayClusterMoviePipelineEnums.h"

class FMyNdDisplayRenderHelper
{
public:
    /** 为指定集群节点创建视口管理器并执行一帧渲染。 */
    static bool RenderFrame(
        ADisplayClusterRootActor* InRootActor,
        const FString& InClusterNodeId,
        const bool bEnableWarpBlend = true)
    {
        if (!InRootActor)
        {
            return false;
        }

        // 创建视口管理器（绑定到特定集群节点）
        FDisplayClusterMoviePipelineViewportManager ViewportMgr(InClusterNodeId, InRootActor);

        // 配置渲染参数
        UE::DisplayClusterMoviePipeline::FRenderSettings Settings;
        Settings.RenderMode = EDisplayClusterRenderFrameMode::Mono;
        Settings.WarpBlendMode = bEnableWarpBlend
            ? EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend
            : EDisplayClusterMoviePipelineWarpBlendMode::None;
        Settings.RenderResolutionScale = 1.0f;

        // 构建渲染帧
        return ViewportMgr.BeginNewFrame(Settings);
    }
};
```

```cpp
// MyNdDisplayRenderJob.cpp
#include "MyNdDisplayRenderJob.h"
// FMyNdDisplayRenderHelper 的所有实现已在头文件中以静态方法形式提供
```

## 模块依赖

DisplayClusterMoviePipeline 模块依赖以下非标准模块：

| 模块 | 用途 |
|---|---|
| `MovieRenderPipelineCore` | Movie Pipeline 基础框架 |
| `MovieRenderPipelineRenderPasses` | 延迟渲染通道基类（`UMoviePipelineDeferredPassBase`） |
| `MovieGraph` / `MovieRenderPipelineCore` | Movie Render Graph 节点和相机源（`UMovieGraphDeferredRenderPassNode` 等） |
| `DisplayCluster` | nDisplay 核心模块，提供视口管理器和集群通信 |
| `DisplayClusterConfiguration` | nDisplay 集群配置数据 |
| `RenderCore` / `RHI` | 渲染线程操作（`FRHICommandListImmediate`、`FTextureRHIRef`） |
| `Renderer` | 场景视图和渲染管线 |
| `D3D12RHI` | Direct3D 12 渲染硬件接口（Windows 平台） |

整个 nDisplay 插件还依赖 `UnrealEd`（编辑器集成）、`LevelEditor`、`D3D12RHI`、`DisplayClusterWarp`（变形混合策略）、`DisplayClusterProjection`（投影策略）等。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | Movie Graph 中添加 nDisplay 多层 EXR 输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 WarpBlendAlpha 模式合并到 WarpBlend 中简化配置 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名和 MPCDI 着色器的 alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复非默认 DisplayGamma 在输出帧编码回退路径中的处理 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的画面闪烁问题 |

### 维护评价

nDisplay 是 Epic Games 官方维护的核心企业级功能，自 2018 年引入以来持续活跃更新。从最近的 commit 记录来看，**维护非常活跃**——最近一周内就有 5 次实质性提交，涵盖新功能（EXR 多层输出）、功能简化（WarpBlendAlpha 合并）、以及多个 bug 修复。

关键评价：
- **活跃度**：极高，属于 Epic 的重点维护项目，服务于虚拟制片（Virtual Production）核心工作流
- **稳定性**：已有 7 年历史，经过大量商业项目验证（LED 虚拟摄影棚等）
- **复杂度**：插件规模极大（1351 个源文件，30 个模块），学习曲线陡峭
- **平台支持**：仅支持 Win64 和 Linux，不支持 macOS/主机平台
- **推荐使用**：✅ 如果你的项目涉及多机协同渲染、LED 墙或 CAVE 系统，这是 UE5 中的唯一选择且质量可靠；对于简单的单机项目则不需要

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/ndisplay-in-unreal-engine)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)