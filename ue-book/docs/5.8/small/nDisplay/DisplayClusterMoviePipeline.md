# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay MRG集成模块 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（Movie Render Graph渲染通道） |
| 模块 | `DisplayClusterMoviePipeline` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-08 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

此插件是 **nDisplay** 集群渲染系统的核心集成模块，专门负责将 nDisplay 集群的视口配置与 **Movie Render Graph (MRG)** 和 **Movie Render Pipeline (MRP)** 系统连接起来。它的核心价值在于：

1.  **电影级质量输出**：允许在由多台 PC 组成的 nDisplay 集群上（例如用于 LED Volume 或多屏投影），使用 UE5 的电影渲染管线（MRP/MRG）进行高质量、可离线的渲染。
2.  **复杂输出控制**：提供多种输出模式（如按视口、按节点、全集群或等矩形投影），支持立体渲染、变形融合（Warp-Blend）、超采样等高级特性，并能将多个视口整合为多层 EXR 文件输出。
3.  **工作流程整合**：将 nDisplay 集群视为一个统一的“相机集合”提供给 MRG，使艺术家能在熟悉的 MRG 工作流程中（如使用 Sequencer 时间线）控制 nDisplay 集群的渲染，而无需手动管理每台 PC。

简而言之，它是连接“实时集群渲染（nDisplay）”与“离线电影渲染（MRP/MRG）”的关键桥梁。

## 使用场景

- **虚拟制片（Virtual Production）**：在 LED Volume 或大型投影墙场景中，需要从多个摄像机视角渲染高分辨率、高质量的最终影片或转盘动画。
- **多屏内容制作**：为飞行模拟器、沉浸式体验空间等多屏项目，生成与屏幕物理布局精确匹配的同步渲染内容。
- **立体渲染（Stereo）**：在 nDisplay 集群上渲染左眼/右眼视图，用于生成立体视频或 VR 内容。
- **复杂投影校正**：需要使用 nDisplay 的变形融合（Warp-Blend）和投影策略来校正非平面或复杂形状屏幕上的渲染输出。
- **统一资产管理**：在 Sequencer 中统一管理 nDisplay 集群的渲染序列，使用 MRG 的高级采样、降噪和输出格式功能。

## 蓝图用法

该模块主要通过 Movie Render Graph 的节点和设置类暴露给蓝图，用于配置渲染行为。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OutputMethod` | 设置 nDisplay 的渲染输出方式（按视口、按节点、全集群、等矩形投影等）。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `StereoMode` | 设置立体渲染模式（无、立体、仅左眼、仅右眼）。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `WarpBlendMode` | 控制是否应用及如何应用变形融合。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `RootActorRef` | 指定用于渲染的 nDisplay 根据 Actor（DCRA）。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `AllowedViewportNamesList` | 仅渲染在此列表中指定的视口名称。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `ResolutionScale` | 对视口渲染分辨率进行统一缩放。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| `EXRLayerGrouping` | 控制多个视口如何分组到多层 EXR 文件中。 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |

### 使用示例（蓝图描述）

在 Movie Render Graph 编辑器中：
1.  从节点菜单添加一个 `nDisplay Deferred Render Pass` 节点。
2.  连接到 `Final Output` 节点。
3.  在该节点的细节面板中，启用并设置 `Output Method` 为 `Per-Node Output Mapping`。
4.  启用 `Stereo Mode` 并设为 `Stereo` 以渲染立体内容。
5.  指定 `Override nDisplay Actor` 到场景中特定的 nDisplay 根据 Actor。
6.  启用 `Render Selected Viewports Only` 并在 `Allowed Viewport Names List` 中只添加你需要渲染的视口 ID，以优化性能。
7.  配置渲染设置（如质量、降噪）并执行渲染，最终输出将包含符合 nDisplay 集群配置的精确多视角画面。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMoviePipelineViewportPass.h"
#include "DisplayClusterMovieGraphDeferredPassNode.h"
```

### 基本用法

获取并配置一个 nDisplay 的 Movie Render Graph 延迟渲染通道节点。
*(注：以下为示意性代码，演示核心配置)*

```cpp
// 在一个 UMovieGraphSetup 函数或 Actor 中
UMovieGraph* Graph = /* ... 获取或创建你的MovieGraph ... */;
UDisplayClusterMovieGraphDeferredRenderPassNode* nDisplayPass = Graph->FindNodeByClass<UDisplayClusterMovieGraphDeferredRenderPassNode>();

if (nDisplayPass)
{
    // 启用并配置输出方法为全集群投影
    nDisplayPass->bOverride_OutputMethod = true;
    nDisplayPass->OutputMethod = EDisplayClusterMoviePipelineOutputMethod::FullClusterOutputMapping;

    // 启用立体渲染
    nDisplayPass->bOverride_StereoMode = true;
    nDisplayPass->StereoMode = EDisplayClusterMoviePipelineStereoMode::Stereo;

    // 禁用变形融合，输出原始渲染结果
    nDisplayPass->bOverride_WarpBlendMode = true;
    nDisplayPass->WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::None;

    // 仅渲染特定视口
    nDisplayPass->bOverride_AllowedViewportNamesList = true;
    nDisplayPass->AllowedViewportNamesList = { TEXT("viewport_main"), TEXT("viewport_left") };
}
```

### 进阶用法

结合 `UDisplayClusterMoviePipelineSettings` 和蓝图中不可见的 C++ 功能进行更精细的控制。
*(注：基于源码结构推断的用法)*

```cpp
#include "DisplayClusterMoviePipelineSettings.h"

// 在创建 MoviePipeline 实例时，添加并配置 nDisplay 设置
UMoviePipeline* Pipeline = /* ... */;
UDisplayClusterMoviePipelineSettings* nDisplaySettings = Pipeline->FindOrAddSettingForShot<UDisplayClusterMoviePipelineSettings>();

if (nDisplaySettings)
{
    // 通过程序指定 DCRA，而不是依赖场景中的第一个
    TSoftObjectPtr<ADisplayClusterRootActor> SpecificRootActorPtr = TSoftObjectPtr<ADisplayClusterRootActor>(FSoftObjectPath("/Game/Maps/MyMap.MyMap:PersistentLevel.MySpecificDCRA"));
    nDisplaySettings->Configuration.DCRootActor = SpecificRootActorPtr;

    // 不使用视口原始分辨率，自定义输出
    nDisplaySettings->Configuration.bUseViewportResolutions = false;

    // 仅渲染指定视口
    nDisplaySettings->Configuration.bRenderAllViewports = false;
    nDisplaySettings->Configuration.AllowedViewportNamesList = { TEXT("left_wall"), TEXT("right_wall") };
}
```

## Demo 示例

一个最小示例，演示如何在 C++ 中创建并添加一个 nDisplay Path Tracer 渲染通道到 Movie Graph 中。

```cpp
// MyGraphBuilder.h
#pragma once
#include "CoreMinimal.h"
#include "DisplayClusterMovieGraphPathTracerPassNode.h"
#include "MovieGraph.h"

class FMyGraphBuilder
{
public:
    static UMovieGraph* CreatenDisplayPathTracerGraph()
    {
        // 创建一个新的 Movie Graph 资产
        UMovieGraph* NewGraph = NewObject<UMovieGraph>();
        
        // 创建一个 nDisplay Path Tracer 通道节点
        UDisplayClusterMovieGraphPathTracerRenderPassNode* PathTracerNode = NewObject<UDisplayClusterMovieGraphPathTracerRenderPassNode>(NewGraph);
        PathTracerNode->SetFlags(RF_Transactional); // 允许在编辑器中撤销
        NewGraph->AddNode(PathTracerNode);

        // 配置节点参数
        PathTracerNode->bOverride_StereoMode = true;
        PathTracerNode->StereoMode = EDisplayClusterMoviePipelineStereoMode::None; // 仅渲染单目

        PathTracerNode->bOverride_WarpBlendMode = true;
        PathTracerNode->WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend; // 应用变形融合

        // 注意：在此最小示例中，还需要连接 Final Output 节点并进行序列化等操作才能实际使用。
        return NewGraph;
    }
};
```

```cpp
// MyGraphBuilder.cpp
#include "MyGraphBuilder.h"

// 使用示例（可能在游戏模式初始化或编辑器工具中调用）
void Init()
{
    UMovieGraph* MyGraph = FMyGraphBuilder::CreatenDisplayPathTracerGraph();
    if (MyGraph)
    {
        // 这个图现在可以用于渲染任务或保存为资产
        UE_LOG(LogTemp, Log, TEXT("Created nDisplay Path Tracer Graph: %s"), *MyGraph->GetName());
    }
}
```

## 模块依赖

要使用 `DisplayClusterMoviePipeline` 模块，你的项目模块需要在 `Build.cs` 文件中添加以下依赖（省略了 Core, Engine, MovieRenderPipelineCore 等常见依赖）：

| 模块 | 用途 |
|---|---|
| `DisplayClusterConfiguration` | 提供 nDisplay 集群配置数据模型。 |
| `DisplayCluster` | 提供 nDisplay 运行时核心功能和视口管理。 |
| `DisplayClusterWarp` | 提供变形融合和投影策略实现。 |
| `DisplayClusterProjection` | 提供投影策略相关功能。 |
| `MovieRenderPipelineCore` | 提供 Movie Render Pipeline 核心框架。 |
| `MovieRenderPipelineRenderPasses` | 提供基础的延迟渲染通道（DeferredPass）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MRG 添加 nDisplay EXR 多层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将变形融合的 Alpha 模式合并到主模式中，简化设置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名问题；修复 MPCDI 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码的后备路径中支持非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**维护状态：活跃维护**

- **年龄**：该插件自 2018 年随 UE4.20 推出，已存在近 7 年，是成熟的生产工具。
- **近期更新**：在最近一个月内（2026年5月）有持续的、实质性的功能更新和 Bug 修复，特别是围绕 Movie Render Graph 的最新集成（EXR 多层），表明 Epic 仍在积极维护和扩展其功能。
- **功能完整性**：提供的节点和 API 覆盖了集群渲染与电影管线集成的主要需求。
- **推荐使用**：**强烈推荐**用于需要高质量、可控输出的 nDisplay 虚拟制片或多屏项目。它提供了从蓝图到 C++ 的完整工作流程，且处于活跃维护中，能跟上 UE5 主线更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/) （nDisplay 总体文档，MoviePipeline 部分通常在其“渲染”章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests) （注意：主要测试在核心模块，此集成模块的测试较少）