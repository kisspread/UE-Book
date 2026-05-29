# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台PC进行单目或立体的同步集群渲染）

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、示例） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterShaders` (Runtime), `SharedMemoryMedia` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterMediaEditor` (Runtime), `SharedMemoryMediaEditor` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterTests` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 并非一个简单的渲染插件，而是一个完整的**多机同步渲染与输出解决方案框架**。它解决的核心问题是：如何将一个大型、高分辨率的渲染任务（例如一个完整的虚拟场景）拆分并分配给多台联网的 PC 同步渲染，最后将这些渲染结果无缝拼接并输出到大型显示器、LED 屏墙或投影系统上。

其主要功能包括：
1.  **分布式渲染**：将渲染负载分散到集群中的多台机器上，突破单台 PC 的 GPU 和分辨率限制。
2.  **精确同步**：通过网络屏障（Ethernet Barrier）或 V-blank 等机制，确保所有渲染节点在同一时刻（或极短时间差内）输出画面，避免画面撕裂和不同步。
3.  **多视口管理**：支持复杂的多视口（Viewport）配置，每个视口可以独立配置分辨率、投影模式（平面、穹幕、鱼眼等）和扭曲映射（Warp & Blend）。
4.  **媒体输入输出集成**：通过 `DisplayClusterMedia` 等模块，支持从外部视频源（如摄像机）输入画面，或将渲染结果实时捕获并输出到外部设备（如 LED 处理器）。
5.  **虚拟制作支持**：特别针对电影和电视的虚拟制作（Virtual Production）场景，集成了 ICVFX（In-Camera VFX）工作流，支持摄像机内合成的实时预览和输出。
6.  **色彩管理**：集成 OpenColorIO (OCIO) 和自定义色彩空间转换，确保整个渲染管线色彩准确。
7.  **工具链**：提供丰富的编辑器工具（如视口布局编辑器、投影调试工具）和操作界面，方便设计师和工程师进行配置和监控。

简而言之，**nDisplay 存在的目的是为了让 UE5 能够驱动大规模、高精度的实景视觉系统（如穹幕影院、XR 虚拟影棚、多通道驾驶模拟器）**。

## 使用场景

-   你需要构建一个由多台 PC 驱动的**大型穹幕或环幕投影系统** → 使用 nDisplay 配置环形投影并管理多节点渲染与边缘融合。
-   你在搭建一个**XR 虚拟制作影棚（LED Volume）**，需要多块 LED 屏幕同步显示精确的摄像机内合成画面 → 使用 nDisplay 管理多个视口输出、ICVFX 摄像机和色彩。
-   你正在开发一个**多通道驾驶模拟器或飞行模拟器**，需要多个显示器从不同视角渲染同一场景 → 使用 nDisplay 定义多个视点并确保渲染同步。
-   你需要将 UE 的实时渲染画面**低延迟、高帧率地输出到广播设备或 LED 处理器** → 使用 nDisplay 的媒体捕获模块（如 Rivermax 或 NDI）。
-   你有一个大型项目需要**多人协作编辑和调试**一个复杂的 nDisplay 集群配置 → 使用 `DisplayClusterMultiUser` 模块。

## 蓝图用法

nDisplay 的核心运行时逻辑主要以 C++ 接口和类的形式提供，面向高级开发者。蓝图层面主要集中在**配置和策略**上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `DisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier` | 配置基于网络屏障的媒体同步策略，设置屏障超时时间。 | `UDisplayClusterMediaOutputSynchronizationPolicyEthernetBarrier` |
| `DisplayClusterMediaOutputSynchronizationPolicyVblank` | 配置基于显示器垂直同步信号的媒体同步策略，设置同步容限。 | `UDisplayClusterMediaOutputSynchronizationPolicyVblank` |

### 使用示例（蓝图描述）

由于 nDisplay 主要通过配置文件和编辑器工具使用，纯蓝图运行时操作较少。典型的使用流程是在 **nDisplay 配置编辑器**中完成的，但你可以通过蓝图动态获取或操作某些配置对象。例如，你可以在蓝图中创建一个 `UDisplayClusterMediaOutputSynchronizationPolicyVblank` 对象，并将其 `MarginMs` 属性设置为 `5`，然后将其传递给媒体输出设备以实现精准的同步控制。

## C++ 用法

由于 nDisplay 规模巨大且测试用例分散，以下从其核心模块 `DisplayClusterMedia` 的接口类提取用法示例。

### 头文件引入

使用 nDisplay 媒体功能，通常需要引入媒体模块的核心头文件。
```cpp
#include "DisplayClusterMediaModule.h"
#include "DisplayClusterMediaOutputSynchronizationPolicy.h"
```

### 基本用法

nDisplay 的媒体模块 (`FDisplayClusterMediaModule`) 负责管理所有媒体捕获和输入设备的生命周期。它在引擎启动时初始化，并监听渲染事件。

**核心流程概要（基于源码分析）：**
1.  **初始化**：当 `DisplayCluster` 实例加载一个集群配置 (`UDisplayClusterConfigurationClusterNode`) 时，`DisplayClusterMedia` 模块会为配置中的每个视口、ICVFX 摄像机以及节点后缓冲创建对应的媒体捕获 (`FDisplayClusterMediaCaptureBase`) 或输入 (`FDisplayClusterMediaInputBase`) 适配器。
2.  **启动/停止**：引擎事件（如 `PreSubmitViewFamilies`）会触发媒体设备的启动 (`StartCapture`, `Play`) 或停止 (`StopCapture`, `Stop`)。
3.  **渲染线程操作**：实际的媒体数据导入（从媒体源到 nDisplay 缓冲区）和导出（从渲染目标到媒体输出）发生在渲染线程，通过回调函数（如 `OnPostRenderViewFamily_RenderThread`, `OnPostBackbufferUpdated_RenderThread`）实现。
4.  **同步**：媒体输出设备可与一个同步策略 (`UDisplayClusterMediaOutputSynchronizationPolicy`) 绑定，由对应的策略处理器 (`IDisplayClusterMediaOutputSynchronizationPolicyHandler`) 在渲染线程控制输出时机。

**简化的概念代码（展示如何关联同步策略）：**
```cpp
// 创建一个基于 V-blank 的同步策略
UDisplayClusterMediaOutputSynchronizationPolicyVblank* SyncPolicy = NewObject<UDisplayClusterMediaOutputSynchronizationPolicyVblank>();
SyncPolicy->BarrierTimeoutMs = 3000; // 继承自基类
SyncPolicy->MarginMs = 5; // V-blank 特有参数

// 在创建媒体输出时（通常在模块的初始化逻辑中）传入策略
// 以下为伪代码，说明参数传递
TSharedPtr<FDisplayClusterMediaCaptureViewportBase> CaptureDevice = MakeShared<FDisplayClusterMediaCaptureViewportFull>(..., SyncPolicy);
```

**来源文件路径**：`Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMedia/` (特别是 `Private/DisplayClusterMediaModule.h` 和 `Public/Synchronization/` 目录下的文件)。

### 进阶用法

**处理延迟队列（Latency Queue）：**
nDisplay 实现了一个人工延迟队列 (`FDisplayClusterFrameQueue`) 用于缓存渲染数据，这对于在同步渲染中引入可控延迟或处理不同节点的帧率差异至关重要。队列会缓存每一帧每个视口的纹理和着色器参数。

```cpp
// 概念性流程，展示帧队列的使用
FDisplayClusterFrameQueue FrameQueue;
FrameQueue.Init();

// 在渲染管线的合适位置（如HandleBeginDraw, HandleEndDraw）
// 调用 FrameQueue 的处理函数来缓存和读取数据
// HandleProcessLatency_RenderThread 会处理纹理的保存和加载

// 通过 SetLatency_RenderThread 来动态调整延迟帧数
```

**来源文件路径**：`Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterMedia/Private/Synchronization/LatencyQueue/`。

## Demo 示例

nDisplay 的使用主要依赖于其强大的编辑器配置工具和运行时管理器。一个最小的 C++ 集成示例会非常复杂，因为它需要与引擎的渲染管线深度集成。典型的“示例”是学习如何通过编辑器创建和加载一个 nDisplay 配置文件。

**配置文件示例 (`.ndisplay`)**：
```json
{
    "cluster": {
        "nodes": [
            {
                "id": "node_1",
                "primary": true,
                "host": "192.168.1.10",
                "viewports": [
                    {
                        "id": "viewport_main",
                        "bufferRatio": 1.0,
                        "region": { "x": 0.0, "y": 0.0, "w": 1.0, "h": 1.0 }
                    }
                ]
            }
        ],
        "viewports": [
            {
                "id": "viewport_main",
                "camera": "default_camera",
                "projection": { "type": "simple" }
            }
        ]
    }
}
```
然后在 C++ 中，通过 `UDisplayClusterConfiguration` 类加载此文件，并将其应用到 `ADisplayClusterRootActor` 上，即可启动 nDisplay 渲染管线。

## 模块依赖

nDisplay 插件是一个庞大的系统，其内部模块间有复杂的依赖关系。作为**使用者**，你的项目模块如果需要直接调用 nDisplay 的 C++ API，通常需要依赖其核心运行时模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供集群管理、同步、视口处理等基础功能。 |
| `DisplayClusterConfiguration` | 处理 nDisplay 配置文件（`.ndisplay`）的加载、解析和表示。 |
| `DisplayClusterProjection` | 提供各种投影算法（如平面、穹幕、鱼眼）。 |
| `DisplayClusterMedia` | 管理媒体输入输出设备（捕获、播放），以及媒体数据同步。 |
| `DisplayClusterWarp` | 实现几何校正（Warp）和边缘融合（Blend）功能。 |
| `DisplayClusterShaders` | 包含 nDisplay 特有的后处理和合成着色器。 |
| `SharedMemoryMedia` | 提供基于共享内存的低延迟媒体传输方式。 |
| `DisplayClusterMoviePipeline` | 集成 Sequencer/Movie Render Queue，支持从 nDisplay 集群输出高质量离线渲染序列。 |

**省略常见依赖**：此插件依赖大量 UE 核心模块（Core, CoreUObject, Engine, Slate, UMG, MediaUtils, OpenColorIO, Rivermax, NDI 等），已在上表省略。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了 EXR 多层支持，提升离线渲染的合成灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 MoviePipeline 中的 WarpBlendAlpha 模式，简化了边缘融合的配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了在多分辨率网格化渲染中摄像机命名问题，并修正了 MPCDI/ICVFX 着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退路径中，未能正确遵循非默认显示伽马值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能导致的屏幕闪烁问题。 |

### 维护评价

-   **活跃维护**：从近期提交记录看，nDisplay **仍在被 Epic Games 积极维护和更新**。最近的提交集中在 2026 年 5 月，主要涉及功能增强（如多层 EXR、Movie Pipeline 集成改进）和重要的 Bug 修复。
-   **核心企业级特性**：作为面向虚拟制作、大型主题乐园和专业视听领域的插件，nDisplay 的更新与其目标行业的需求（如更高的渲染质量、更稳定的同步、更好的工作流集成）紧密相关。
-   **复杂度与学习曲线**：该插件极其复杂，包含大量模块和子系统，文档和教程相对分散，对初学者不友好。其使用高度依赖于编辑器工具和配置文件。
-   **推荐使用**：**强烈推荐**给需要构建大规模、高精度实时渲染集群的专业团队或项目。它是 UE5 在此领域的官方解决方案，成熟度和支持力度远超第三方方案。但对于简单的多屏扩展，可能有更轻量的替代方案。
-   **警告**：虽然该插件自 2018 年就已存在，但鉴于其近期的活跃更新，**不属于废弃插件**。不过，其庞大的代码库和依赖性意味着集成和调试需要较高的技术能力。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) （UE5 官方 nDisplay 文档入口）
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)