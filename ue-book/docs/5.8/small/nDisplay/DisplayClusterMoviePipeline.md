# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 的**多机集群同步渲染系统**，解决的核心问题是：**将一个场景的渲染工作分散到多台 PC 上，每台 PC 负责渲染画面的一个子区域（视口），最终拼合成一个完整的超大画面**。

它的存在价值在于：

- **突破单机性能上限**：单台 PC 的 GPU 无法驱动超高分辨率（如 8K×4K LED 墙），nDisplay 让多台 PC 各渲染一部分
- **精确的投影几何矫正**：支持弧面屏幕、多投影仪拼接、CAVE 洞穴等复杂几何形状的实时投影映射
- **帧同步保障**：所有集群节点在严格同步的帧时序下渲染，避免画面撕裂和延迟
- **虚拟制片（Virtual Production）**：配合 LED 卷幕墙实现摄影机内外的实时合成渲染
- **影视离线渲染**：通过 Movie Pipeline / Movie Render Graph 集成，将 nDisplay 集群配置用于高质量离线序列帧渲染

简而言之，nDisplay 是 UE5 面向**虚拟制片、大型模拟器、沉浸式投影装置**等专业场景的核心基础设施。

## 使用场景

- 你在搭建 **LED 虚拟制片影棚**（类似《曼达洛人》的 StageCraft） → 用 nDisplay 配置 LED 墙的视口和投影映射
- 你需要构建 **驾驶模拟器**，多台投影仪投射到弧面屏幕上 → 用 nDisplay 的 MPCDI/WarpBlend 投影策略
- 你要做 **CAVE 沉浸式环境**，多个面各由独立 PC 渲染 → 用 nDisplay 配置多集群节点
- 你想将 nDisplay 集群配置用于 **Movie Render Graph 离线渲染** → 用 DisplayClusterMoviePipeline 模块
- 你需要 **多台 PC 的 EXR 多层输出**，将不同视口打包到单个 EXR 文件中 → 用 EXR Layer Grouping 功能

## 蓝图用法

nDisplay 的核心功能通过编辑器配置和 `ADisplayClusterRootActor` 实现，Movie Pipeline 集成部分主要通过 `UMoviePipelineSetting` 和渲染通道节点暴露给蓝图。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetRootActor` | 从当前世界获取 nDisplay 根 Actor | `UDisplayClusterMoviePipelineSettings` |
| `GetViewports` | 收集用于 Movie Pipeline 渲染的视口列表及其分辨率 | `UDisplayClusterMoviePipelineSettings` |

### Movie Pipeline 渲染通道

在 Movie Pipeline 配置中可添加以下 nDisplay 专用渲染通道：

| 渲染通道类 | 显示名称 | 说明 |
|---|---|---|
| `UDisplayClusterMoviePipelineViewportPassBase` | nDisplay Rendering | 基础 Lit 渲染通道 |
| `UDisplayClusterMoviePipelineViewportPass_Unlit` | nDisplay Rendering (Unlit) | 无光照渲染通道 |
| `UDisplayClusterMoviePipelineViewportPass_DetailLighting` | nDisplay Rendering (Detail Lighting) | 细节光照渲染通道 |
| `UDisplayClusterMoviePipelineViewportPass_LightingOnly` | nDisplay Rendering (Lighting Only) | 仅光照渲染通道 |
| `UDisplayClusterMoviePipelineViewportPass_ReflectionsOnly` | nDisplay Rendering (Reflections Only) | 仅反射渲染通道 |
| `UDisplayClusterMoviePipelineViewportPass_PathTracer` | nDisplay Path Tracer | 路径追踪渲染通道 |

### Movie Render Graph 节点

在 Movie Render Graph 编辑器中可添加以下 nDisplay 专用节点：

| 节点类 | 说明 |
|---|---|
| `UDisplayClusterMovieGraphDeferredRenderPassNode` | nDisplay 延迟渲染通道节点 |
| `UDisplayClusterMovieGraphPathTracerRenderPassNode` | nDisplay 路径追踪渲染通道节点 |

### 使用示例（蓝图描述）

**配置 Movie Pipeline 使用 nDisplay 渲染**：

1. 在 Sequencer 中打开 Movie Pipeline 配置资产
2. 添加 `UDisplayClusterMoviePipelineSettings` 设置项，在 `Configuration` 字段中指定 `DCRootActor`（或留空自动查找场景中第一个 DCRA）
3. 添加 nDisplay 渲染通道（如 `UDisplayClusterMoviePipelineViewportPassBase`）
4. 在渲染通道的 `bEnabledWarpBlend` 中启用/禁用 WarpBlend 混合
5. 执行渲染，Movie Pipeline 会自动解析 nDisplay 集群拓扑并为每个视口生成对应的渲染任务

**配置 Movie Render Graph 使用 nDisplay**：

1. 在 MRG 编辑器中，添加 `UDisplayClusterMovieGraphDeferredRenderPassNode` 或 `UDisplayClusterMovieGraphPathTracerRenderPassNode`
2. 设置 `OutputMethod`（逐视口/逐节点映射/全集群映射/等距柱状投影等）
3. 可选设置 `StereoMode`（单目/立体/仅左眼/仅右眼）
4. 可选设置 `EXRLayerGrouping`（无/按视口/按节点/按集群）控制多层 EXR 输出分组
5. 指定 `RootActorRef` 或留空自动解析

## C++ 用法

### 头文件引入

```cpp
// Movie Pipeline 集成
#include "DisplayClusterMoviePipelineViewportPass.h"
#include "DisplayClusterMoviePipelineSettings.h"
#include "DisplayClusterMoviePipelineEnums.h"

// Movie Render Graph 节点
#include "Graph/Nodes/DisplayClusterMovieGraphDeferredPassNode.h"
#include "Graph/Nodes/DisplayClusterMovieGraphPathTracerPassNode.h"

// 内部视口管理
#include "DisplayClusterMoviePipelineViewportManager.h"
#include "DisplayClusterMoviePipelineViewportCameraInfo.h"
#include "DisplayClusterMoviePipelineRenderSettings.h"
```

### 基本用法

**解析 nDisplay 根 Actor 并获取视口信息**（来源：`DisplayClusterMoviePipelineViewportManager.h`）：

```cpp
// 从序列播放器中解析 nDisplay 根 Actor
// 搜索优先级：1. 序列绑定 > 2. 世界中的 Actor
// 匹配优先级：a. 精确名称+类匹配 > b. 仅类匹配 > c. 任意 DCRA
ADisplayClusterRootActor* RootActor = FDisplayClusterMoviePipelineViewportManager::ResolveRootActor(
    SequencePlayer,           // UMovieSceneSequencePlayer*
    TSoftObjectPtr<ADisplayClusterRootActor>(SpecificActorPath),  // 优先使用的 Actor 引用
    TSoftClassPtr<ADisplayClusterRootActor>(RootActorClassPath)   // 优先使用的类引用
);
```

**创建视口管理器并构建渲染帧**（来源：`DisplayClusterMoviePipelineViewportManager.h`）：

```cpp
// 为指定集群节点创建视口管理器
FDisplayClusterMoviePipelineViewportManager ViewportManager(ClusterNodeId, RootActor);

// 构建新一帧的渲染数据
UE::DisplayClusterMoviePipeline::FRenderSettings RenderSettings;
RenderSettings.RenderMode = EDisplayClusterRenderFrameMode::Stereo;
RenderSettings.WarpBlendMode = EDisplayClusterMoviePipelineWarpBlendMode::WarpBlend;

bool bSuccess = ViewportManager.BeginNewFrame(RenderSettings, World, &FrameNumber);
```

### 进阶用法

**通过 C++ 配置 Movie Pipeline 的 nDisplay 设置**（来源：`DisplayClusterMoviePipelineSettings.h`）：

```cpp
// 获取 Movie Pipeline 设置
UDisplayClusterMoviePipelineSettings* Settings = MyPipeline->FindSetting<UDisplayClusterMoviePipelineSettings>();

// 配置根 Actor
Settings->Configuration.DCRootActor = TSoftObjectPtr<ADisplayClusterRootActor>(MyDCRAPath);
Settings->Configuration.bUseViewportResolutions = true;
Settings->Configuration.bRenderAllViewports = false;

// 指定只渲染特定视口
Settings->Configuration.AllowedViewportNamesList.Add(TEXT("viewport_left"));
Settings->Configuration.AllowedViewportNamesList.Add(TEXT("viewport_right"));

// 收集视口信息
TArray<FString> ViewportNames;
TArray<FIntPoint> ViewportResolutions;
bool bHasViewports = Settings->GetViewports(World, ViewportNames, ViewportResolutions);
```

**在渲染线程中应用 WarpBlend**（来源：`DisplayClusterMoviePipelineViewportManager.h`）：

```cpp
// 在渲染线程中对视口应用 WarpBlend 后处理
// 流程：RTT → copy → TempIn → WarpShader → TempOut → copy back → RTT
void MyRenderFunction(FRHICommandListImmediate& RHICmdList,
                      IDisplayClusterViewportProxy* ViewportProxy,
                      uint32 ContextNum,
                      FTextureRHIRef& RenderTarget)
{
    ViewportManager.ApplyWarpBlend_RenderThread(
        RHICmdList, ViewportProxy, ContextNum, RenderTarget);
}
```

## Demo 示例

以下展示如何在 C++ 中创建自定义的 nDisplay Movie Pipeline 渲染通道：

```cpp
// MyNDisplayRenderJob.h
#pragma once

#include "MoviePipeline.h"
#include "DisplayClusterMoviePipelineSettings.h"

class FMyNDisplayRenderHelper
{
public:
    /** 配置并启动 nDisplay 离线渲染 */
    static bool StartNDisplayRender(UMoviePipeline* InPipeline, ADisplayClusterRootActor* InDCRA)
    {
        if (!InPipeline || !InDCRA)
        {
            return false;
        }

        // 1. 获取或创建 nDisplay 设置
        UDisplayClusterMoviePipelineSettings* NDSettings =
            InPipeline->FindOrAddSettingForShot<UDisplayClusterMoviePipelineSettings>(nullptr);
        if (!NDSettings)
        {
            return false;
        }

        // 2. 指定 nDisplay 根 Actor
        NDSettings->Configuration.DCRootActor =
            TSoftObjectPtr<ADisplayClusterRootActor>(InDCRA);

        // 3. 使用视口原始分辨率
        NDSettings->Configuration.bUseViewportResolutions = true;

        // 4. 渲染所有视口
        NDSettings->Configuration.bRenderAllViewports = true;

        // 5. 收集视口信息验证配置
        TArray<FString> ViewportNames;
        TArray<FIntPoint> ViewportResolutions;
        const UWorld* World = InDCRA->GetWorld();
        if (NDSettings->GetViewports(World, ViewportNames, ViewportResolutions))
        {
            UE_LOG(LogTemp, Log,
                TEXT("nDisplay render configured: %d viewports ready"), ViewportNames.Num());
            for (int32 i = 0; i < ViewportNames.Num(); ++i)
            {
                UE_LOG(LogTemp, Log,
                    TEXT("  Viewport[%d]: %s (%dx%d)"),
                    i, *ViewportNames[i],
                    ViewportResolutions[i].X, ViewportResolutions[i].Y);
            }
        }

        return true;
    }
};
```

```cpp
// MyNDisplayRenderJob.cpp
#include "MyNDisplayRenderJob.h"
#include "DisplayClusterRootActor.h"
```

## 模块依赖

从 Build.cs 分析，nDisplay 插件依赖了大量 UE 标准模块，同时有一些**独特依赖**：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | DisplayClusterMedia、SharedMemoryMedia 模块的 DirectX 12 共享内存渲染支持 |
| `ScalableMPCDI` (External) | 第三方 MPCDI（Multi-Projector Calibration Data Interchange）投影校准数据格式支持 |
| `UnrealEd` | 多个模块（DisplayCluster、DisplayClusterMedia、DisplayClusterProjection 等）依赖编辑器功能 |

注意：许多标记为 Runtime 的模块（如 DisplayClusterConfigurator、DisplayClusterEditor、DisplayClusterOperator 等）实际上包含了编辑器 UI 代码，存在对 UnrealEd 的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Render Graph 添加 nDisplay EXR 多层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 WarpBlendAlpha 模式合并到 WarpBlend，简化配置 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名和 MPCDI/ICVFX 着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码回退时未使用非默认 DisplayGamma 的问题 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护**。nDisplay 是 Epic Games 持续投入的核心虚拟制片基础设施，具备以下特征：

- **更新频繁**：近 10 天内有 5 次实质性提交，涵盖新功能（EXR 多层输出）、重构（WarpBlend 合并）和 Bug 修复
- **持续演进**：与 Movie Render Graph 的深度集成仍在积极开发中，支持最新的渲染管线特性
- **成熟稳定**：自 2018 年创建以来已走过 8 年，从 UE4.20 发展到 UE5.8，代码规模达 1351 个源文件、29 个模块
- **生产验证**：广泛用于虚拟制片行业（LED Volume、CAVE、模拟器等）
- **默认未启用**：由于功能专业且依赖特定硬件配置，`EnabledByDefault=false`，需要用户手动启用

⚠️ **注意**：nDisplay 是一个大型复杂插件（29 个模块），建议有特定硬件需求（LED 墙、多投影仪、集群渲染）时再启用。普通项目无需开启此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [Movie Pipeline 渲染通道源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMoviePipeline/)
- [Movie Render Graph 节点源码](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMoviePipeline/Public/Graph/Nodes/)
- [枚举定义](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMoviePipeline/Public/DisplayClusterMoviePipelineEnums.h)