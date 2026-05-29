# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、着色器、配置模板、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**集群渲染系统**，用于将单个 UE 场景同步分发到多台 PC 上进行渲染，最终拼接成一个完整的超宽视野输出。核心解决以下问题：

- **多机同步渲染**：通过网络协议让多台 PC 以帧级别精度同步渲染同一场景，每台 PC 负责不同的视口（Viewport）区域
- **投影变形与边缘融合（Warp & Blend）**：支持 MPCDI、MESH 等投影策略，对非平面投影表面（如弧形幕、穹顶）进行几何校正和边缘融合
- **虚拟制片 / LED 墙（ICVFX）**：专为 LED Volume 虚拟制片设计，支持 Inner Frustum（摄影机视锥）与 Outer Frustum（LED 墙背景）的分层渲染
- **Movie Pipeline 集成**：将 nDisplay 集群渲染能力接入 Movie Render Queue 和 Movie Graph，支持离线高质量序列渲染，包括路径追踪、立体渲染、多层 EXR 输出等

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用，面向虚拟制片、大型沉浸式装置（CAVE）、LED 墙摄影棚等专业场景。

## 使用场景

- 你在搭建 **LED Volume 摄影棚**（ICVFX） → 用 nDisplay 配置 Inner/Outer Frustum 分层渲染
- 你需要 **多台 PC 同步渲染超宽分辨率**（如 CAVE、飞行模拟器） → 用 nDisplay 配置多节点集群
- 你要用 **Movie Render Queue 离线渲染 nDisplay 配置** → 用 DisplayClusterMoviePipeline 模块
- 你需要 **弧形幕/穹顶投影的几何校正** → 用 nDisplay 的 MPCDI/MESH 投影策略
- 你在做 **多人协同编辑虚拟制片场景** → 用 DisplayClusterMultiUser 模块
- 你需要 **将 nDisplay 渲染输出接入外部媒体管线**（如 SDI 视频卡） → 用 DisplayClusterMedia + SharedMemoryMedia 模块

## 蓝图用法

> **说明**：DisplayClusterMoviePipeline 模块主要为 Movie Pipeline 提供渲染 Pass 节点，蓝图 API 集中在设置和配置层面。核心渲染逻辑通过 Movie Pipeline 的 Pass 系统自动触发。

### 核心设置节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| Configuration 属性编辑 | 配置 nDisplay 根节点 Actor、是否使用视口分辨率、渲染哪些视口 | `UDisplayClusterMoviePipelineSettings` |
| `GetRootActor` | 从当前世界获取 nDisplay 根节点 Actor | `UDisplayClusterMoviePipelineSettings` |
| `GetViewports` | 收集要渲染的视口名称列表和分辨率列表 | `UDisplayClusterMoviePipelineSettings` |

### Movie Pipeline Render Pass 类

在 Movie Pipeline 配置中可添加的 nDisplay 渲染通道：

| 渲染通道 | 说明 | 所在类 |
|---|---|---|
| nDisplay Rendering | 带光照的延迟渲染（Lit） | `UDisplayClusterMoviePipelineViewportPassBase` |
| nDisplay Rendering (Unlit) | 无光照渲染 | `UDisplayClusterMoviePipelineViewportPass_Unlit` |
| nDisplay Rendering (Detail Lighting) | 细节光照渲染 | `UDisplayClusterMoviePipelineViewportPass_DetailLighting` |
| nDisplay Rendering (Lighting Only) | 仅光照渲染 | `UDisplayClusterMoviePipelineViewportPass_LightingOnly` |
| nDisplay Rendering (Reflections Only) | 仅反射渲染 | `UDisplayClusterMoviePipelineViewportPass_ReflectionsOnly` |
| nDisplay Path Tracer | 路径追踪渲染 | `UDisplayClusterMoviePipelineViewportPass_PathTracer` |

### Movie Graph 节点

在 Movie Graph 编辑器中可使用的 nDisplay 节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| nDisplay Deferred Pass | Movie Graph 延迟渲染通道 | `UDisplayClusterMovieGraphDeferredRenderPassNode` |
| nDisplay PathTracer Pass | Movie Graph 路径追踪通道 | `UDisplayClusterMovieGraphPathTracerRenderPassNode` |

### 关键属性（Render Pass 节点）

| 属性 | 类型 | 说明 |
|---|---|---|
| `OutputMethod` | `EDisplayClusterMoviePipelineOutputMethod` | 输出方式：逐视口 / 按节点映射 / 全集群映射 / 180°等距投影 / 360°等距投影 / 自定义网格投影 |
| `StereoMode` | `EDisplayClusterMoviePipelineStereoMode` | 立体模式：无 / 双眼 / 仅左眼 / 仅右眼 |
| `WarpBlendMode` | `EDisplayClusterMoviePipelineWarpBlendMode` | 是否启用变形融合 |
| `ResolutionScale` | `float` | 视口分辨率缩放系数（0.01-1.0） |
| `OutputResolution` | `FIntPoint` | 覆盖输出分辨率 |
| `OverscanMode` | `EDisplayClusterMoviePipelineOverscanMode` | 过扫描来源：MRP 默认 / nDisplay 视口 |
| `EXRLayerGrouping` | `EDisplayClusterMoviePipelineEXRLayerGrouping` | EXR 多层分组：无 / 按视口 / 按节点 / 按集群 |
| `RootActorRef` | `TSoftObjectPtr<ADisplayClusterRootActor>` | 指定 nDisplay 根节点 Actor |
| `AllowedViewportNamesList` | `TArray<FString>` | 仅渲染指定视口 |
| `AllowedNodeNamesList` | `TArray<FString>` | 仅渲染指定节点 |

### 使用示例（蓝图描述）

**配置 Movie Pipeline 渲染 nDisplay**：

1. 在场景中放置 `ADisplayClusterRootActor`，配置集群拓扑和视口
2. 创建 Movie Pipeline 配置资产
3. 添加 `UDisplayClusterMoviePipelineSettings` 设置，引用场景中的 Root Actor
4. 在渲染通道中添加 `UDisplayClusterMoviePipelineViewportPassBase`（或 PathTracer 版本）
5. 配置 Output Method、Stereo Mode 等参数
6. 通过 Movie Render Queue 执行渲染

**使用 Movie Graph 渲染**：

1. 创建 Movie Graph 资产
2. 添加 `UDisplayClusterMovieGraphDeferredRenderPassNode` 或 PathTracer 节点
3. 连接 Output 节点，配置输出格式
4. 节点会自动解析 DCRA、枚举所有视口、为每个集群节点创建独立的 ViewportManager
5. 通过 Movie Graph Pipeline 执行渲染

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMoviePipelineViewportPass.h"
#include "DisplayClusterMoviePipelineSettings.h"
#include "DisplayClusterMoviePipelineEnums.h"
#include "Graph/Nodes/DisplayClusterMovieGraphDeferredPassNode.h"
#include "Graph/Nodes/DisplayClusterMovieGraphPathTracerPassNode.h"
```

### 基本用法 — 自定义 Movie Pipeline Render Pass

基于源码中的 `UDisplayClusterMoviePipelineViewportPassBase` 分析，该类继承自 `UMoviePipelineDeferredPassBase`，重写了视图计算和投影矩阵逻辑：

```cpp
// 创建一个自定义的 nDisplay 渲染 Pass（继承自基础 Pass）
// 来源: Public/DisplayClusterMoviePipelineViewportPass.h
UCLASS(BlueprintType)
class UMyCustomnDisplayPass : public UDisplayClusterMoviePipelineViewportPassBase
{
    GENERATED_BODY()

public:
    UMyCustomnDisplayPass() : UDisplayClusterMoviePipelineViewportPassBase(TEXT("MyCustomnDisplay"))
    {}

    // 可选：覆盖视图显示标志
    virtual void GetViewShowFlags(FEngineShowFlags& OutShowFlag, EViewModeIndex& OutViewModeIndex) const override
    {
        OutShowFlag = FEngineShowFlags(EShowFlagInitMode::ESFIM_Game);
        OutViewModeIndex = EViewModeIndex::VMI_Lit;
    }

#if WITH_EDITOR
    virtual FText GetDisplayText() const override
    {
        return NSLOCTEXT("MyModule", "CustomnDisplay", "My Custom nDisplay Pass");
    }
#endif
};
```

### 基本用法 — 程序化配置 Movie Pipeline Settings

```cpp
// 来源: Public/DisplayClusterMoviePipelineSettings.h
void ConfigureMoviePipeline(UMoviePipeline* InPipeline)
{
    // 获取或添加 nDisplay 设置
    UDisplayClusterMoviePipelineSettings* nDisplaySettings = 
        InPipeline->FindOrAddSettingForShot<UDisplayClusterMoviePipelineSettings>(nullptr);
    
    if (nDisplaySettings)
    {
        // 配置根节点 Actor 引用（软引用）
        nDisplaySettings->Configuration.DCRootActor = 
            TSoftObjectPtr<ADisplayClusterRootActor>(FSoftObjectPath("/Game/MyLevel.MyLevel:PersistentLevel.MyDCRA"));
        
        // 使用视口原始分辨率
        nDisplaySettings->Configuration.bUseViewportResolutions = true;
        
        // 渲染所有视口
        nDisplaySettings->Configuration.bRenderAllViewports = true;
        
        // 或仅渲染指定视口
        nDisplaySettings->Configuration.bRenderAllViewports = false;
        nDisplaySettings->Configuration.AllowedViewportNamesList = {TEXT("viewport_left"), TEXT("viewport_right")};
    }
}
```

### 进阶用法 — 理解 ViewportManager 帧工作流

基于 `FDisplayClusterMoviePipelineViewportManager` 的分析，每帧渲染流程如下：

```cpp
// 来源: Private/DisplayClusterMoviePipelineViewportManager.h
// 说明：每个集群节点拥有一个独立的 ViewportManager

// 1. 创建 ViewportManager（通常由 CameraSource 在 Initialize 时自动创建）
FDisplayClusterMoviePipelineViewportManager ViewportManager(ClusterNodeId, RootActor);

// 2. 每帧开始时调用 BeginNewFrame — 更新视口配置并构建渲染帧
UE::DisplayClusterMoviePipeline::FRenderSettings RenderSettings;
RenderSettings.RenderMode = EDisplayClusterRenderFrameMode::Stereo;
RenderSettings.OverscanMode = EDisplayClusterMoviePipelineOverscanMode::Default;
RenderSettings.RenderResolutionScale = 0.5f;  // 50% 分辨率
RenderSettings.WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend;

bool bSuccess = ViewportManager.BeginNewFrame(RenderSettings);
if (bSuccess)
{
    // 渲染帧已构建，视口代理就绪
}

// 3. 渲染完成后，在渲染线程上应用 WarpBlend 后处理
// （通常由 RenderPass 的 PostRendererSubmission 自动调用）
// void ApplyWarpBlend_RenderThread(FRHICommandListImmediate& RHICmdList,
//     IDisplayClusterViewportProxy* InViewportProxy,
//     const uint32 ContextNum,
//     const FTextureRHIRef& InOutRTT);
```

### 进阶用法 — Movie Graph 自定义渲染节点

```cpp
// 来源: Public/Graph/Nodes/DisplayClusterMovieGraphDeferredRenderPassNode.h
// 说明：Movie Graph 系统中的 nDisplay 延迟渲染节点

// 创建一个 Movie Graph nDisplay 延迟渲染节点实例
// 在蓝图或 C++ 中创建 UDisplayClusterMovieGraphDeferredRenderPassNode

// 关键配置属性（蓝图可编辑）：
// - OutputMethod: 输出方式
// - StereoMode: 立体渲染模式
// - WarpBlendMode: 变形融合模式
// - RootActorRef: 指定 DCRA
// - AllowedViewportNamesList: 限制渲染的视口

// 节点内部工作流：
// 1. SetupImpl() — 初始化，创建 RenderCameraSource
// 2. CreateRenderCameraSourceImpl() — 解析 DCRA，枚举视口，创建每节点的 ViewportManager
// 3. 渲染循环中 CameraSource 提供视图信息和投影矩阵
// 4. PostRendererSubmission() — 对渲染结果应用 WarpBlend
// 5. TeardownImpl() — 清理资源
```

## Demo 示例

### 自定义 Movie Pipeline 渲染通道

```cpp
// MyCustomnDisplayRenderPass.h
#pragma once

#include "DisplayClusterMoviePipelineViewportPass.h"
#include "MyCustomnDisplayRenderPass.generated.h"

/**
 * 自定义 nDisplay 渲染通道示例：仅渲染指定视口并应用自定义后处理
 */
UCLASS(BlueprintType)
class MYPROJECT_API UMyCustomnDisplayRenderPass : public UDisplayClusterMoviePipelineViewportPassBase
{
    GENERATED_BODY()

public:
    UMyCustomnDisplayRenderPass()
        : UDisplayClusterMoviePipelineViewportPassBase(TEXT("MyCustomPass"))
    {}

    // 自定义显示名称
#if WITH_EDITOR
    virtual FText GetDisplayText() const override
    {
        return NSLOCTEXT("MyProject", "CustomnDisplayPass", "Custom nDisplay Rendering");
    }
#endif

    // 配置为仅光照模式
    virtual void GetViewShowFlags(FEngineShowFlags& OutShowFlag, EViewModeIndex& OutViewModeIndex) const override
    {
        OutShowFlag = FEngineShowFlags(EShowFlagInitMode::ESFIM_Game);
        OutShowFlag.SetLightingOnlyOverride(true);
        OutViewModeIndex = EViewModeIndex::VMI_Lit;
    }

    // 启用变形融合
    virtual bool bIsEnabledWarpBlend() const override { return true; }

    // 设置输出排序优先级
    virtual int32 GetOutputFileSortingOrder() const override { return 3; }
};
```

```cpp
// MyCustomnDisplayRenderPass.cpp
#include "MyCustomnDisplayRenderPass.h"

// 该 Pass 会自动被 Movie Pipeline 系统识别
// 无需额外注册代码，UCLASS 宏和继承关系足以让系统发现它
```

### Movie Graph 自定义节点

```cpp
// MyCustomnDisplayGraphNode.h
#pragma once

#include "Graph/Nodes/DisplayClusterMovieGraphDeferredPassNode.h"
#include "MyCustomnDisplayGraphNode.generated.h"

/**
 * 自定义 Movie Graph nDisplay 节点示例
 */
UCLASS(BlueprintType)
class MYPROJECT_API UMyCustomnDisplayGraphNode : public UDisplayClusterMovieGraphDeferredRenderPassNode
{
    GENERATED_BODY()

public:
    UMyCustomnDisplayGraphNode();

#if WITH_EDITOR
    virtual FText GetNodeTitle(const bool bGetDescriptive = false) const override
    {
        return NSLOCTEXT("MyProject", "CustomGraphNode", "Custom nDisplay Graph Pass");
    }
#endif

    // 覆盖默认输出方法
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay")
    EDisplayClusterMoviePipelineOutputMethod CustomOutputMethod = 
        EDisplayClusterMoviePipelineOutputMethod::PerViewportOutput;

    // 覆盖默认立体模式
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay")
    EDisplayClusterMoviePipelineStereoMode CustomStereoMode = 
        EDisplayClusterMoviePipelineStereoMode::None;
};
```

```cpp
// MyCustomnDisplayGraphNode.cpp
#include "MyCustomnDisplayGraphNode.h"

UMyCustomnDisplayGraphNode::UMyCustomnDisplayGraphNode()
{
    // 启用所有覆盖
    bOverride_OutputMethod = true;
    bOverride_StereoMode = true;
    
    // 设置默认值
    OutputMethod = EDisplayClusterMoviePipelineOutputMethod::PerViewportOutput;
    StereoMode = EDisplayClusterMoviePipelineStereoMode::None;
    WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend;
}
```

## 模块依赖

> DisplayClusterMoviePipeline 的 Build.cs 依赖未在提供的信息中完整列出。以下是基于源码头文件分析推断的依赖关系。完整的 nDisplay 插件包含 28 个模块，部分模块（如 `DisplayCluster`、`DisplayClusterMedia`、`DisplayClusterProjection` 等）依赖 `UnrealEd`、`EditorWidgets`、`LevelEditor`、`D3D12RHI` 等。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时，提供 Viewport、RootActor、集群同步等基础设施 |
| `DisplayClusterConfiguration` | nDisplay 配置数据资产和序列化 |
| `DisplayClusterProjection` | 投影策略（MPCDI、MESH、Camera 等） |
| `DisplayClusterShaders` | nDisplay 专用着色器（WarpBlend、ICVFX 等） |
| `DisplayClusterWarp` | 变形融合（Warp & Blend）算法实现 |
| `MovieRenderPipelineCore` | Movie Pipeline 核心框架（Render Pass 基类） |
| `MovieRenderPipelineRenderPasses` | Movie Pipeline 延迟渲染 Pass 基类 |
| `MovieRenderGraphRuntime` | Movie Graph 运行时（Graph 节点基类） |
| `MovieRenderGraphCore` | Movie Graph 核心类型和接口 |
| `ScalableMPCDI` | 第三方 MPCDI 库（External 模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 添加 EXR 多层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 WarpBlendAlpha 模式合并到 WarpBlend 中简化配置 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 Movie Graph 拓扑感知的摄影机命名和 MPCDI/ICVFX 着色器透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码时未正确处理非默认 DisplayGamma 的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

nDisplay 是 Epic Games 虚拟制片（Virtual Production）战略的核心组件之一，自 2018 年随 UE 4.20 引入以来持续获得活跃维护。

**积极信号**：
- 最近更新集中在 2026 年 5 月，且全部是功能性更新（EXR 多层支持、WarpBlend 模式合并、着色器修复），表明插件仍在活跃开发中
- 28 个模块的庞大规模说明功能覆盖面广，Epic 持续投入资源
- Movie Graph 集成是 UE5 Movie Render Graph 的新系统，说明该插件紧跟引擎核心系统演进
- 2026 年 5 月有多次 Movie Graph 相关提交，说明正在完善新渲染管线的集成

**注意事项**：
- `EnabledByDefault: false`，需要手动在项目设置中启用
- 仅支持 Win64 和 Linux 平台
- 插件规模巨大（1351 源文件），入门门槛较高
- 部分模块依赖 `UnrealEd`，这意味着它们是编辑器专用的

**推荐**：✅ 推荐用于虚拟制片和集群渲染场景。该插件是 UE5 官方虚拟制片工作流的核心组件，维护活跃，功能完善。对于不需要集群渲染的常规项目无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/)（nDisplay 官方文档）