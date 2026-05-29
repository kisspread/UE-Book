# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台PC进行同步的集群渲染，支持单声道或立体声模式）

| 属性 | 值 |
|---|---|
| 中文名 | 多显示集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于实现 **同步集群渲染 (Synchronized Clustered Rendering)** 的核心插件。它解决了在虚拟制片、主题公园、大型场馆、模拟训练等专业视觉领域中，需要使用多台PC协同驱动多个显示器（或投影机）来渲染一个连贯、像素精确的视图的关键问题。

插件的核心功能包括：
1.  **显示集群管理**：将一个或多个显示器（视口）组合成一个逻辑上的“显示集群”，并为集群中的每个显示器分配对应的PC（集群节点）。
2.  **精确同步**：确保所有集群节点在渲染帧开始和结束时保持严格同步，避免画面撕裂和延迟。
3.  **投影与几何校正**：支持复杂的多投影面配置（如环幕、球幕），并提供高级的几何校正（Warp）和色彩混合（Blend）功能，以实现无缝拼接。
4.  **立体3D (S3D)**：支持单目和立体渲染模式，满足沉浸式体验的需求。
5.  **渲染与媒体集成**：提供高效的帧共享机制（如`SharedMemoryMedia`模块），并将渲染结果与外部媒体设备或输入源进行集成。

简而言之，nDisplay 使得 Unreal Engine 能够作为一个强大的、可扩展的多显示渲染引擎，用于驱动复杂的视觉装置。

## 使用场景

-   **虚拟制片 (Virtual Production)**：在 LED 体积墙（LED Volume）中，使用多台渲染机驱动墙上的每一个 LED 面板，实现与真实相机视角完美匹配的实时背景渲染。
-   **主题公园与飞行影院**：驱动环绕观众的巨大弧形屏幕或穹顶投影，营造沉浸式飞行体验。
-   **博物馆与展览馆**：构建多通道的沉浸式投影空间，展示大型文物或艺术作品。
-   **模拟与训练**：为驾驶模拟器、飞行模拟器提供环绕视野，模拟真实的驾驶环境。
-   **大型活动与舞台**：在演唱会、发布会等活动中，同步控制多个大屏幕，播放精确同步的视觉内容。
-   **CAVE (Cave Automatic Virtual Environment)**：创建由多面投影墙组成的沉浸式虚拟现实空间。

## 蓝图用法

nDisplay 插件的蓝图功能非常强大，主要集中在显示集群的创建、管理和查询，以及投影几何的编辑上。当前分析的 `DisplayClusterStageMonitoring` 模块主要用于后端监控，其设置通过开发者设置类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get nDisplay Cluster` | 获取当前活动的显示集群实例，是进行集群相关操作的入口点。 | `UDisplayClusterManager` (全局管理器) |
| `Get Cluster Node ID` | 获取当前运行的PC在集群中的节点标识符。 | `UDisplayClusterManager` |
| `Get Stage Monitor Settings` | 获取当前插件的运行时监控配置。 | `UDisplayClusterStageMonitoringSettings` |
| `Set Warp Blend Configuration` | 动态更新投影面的几何校正和混合参数。 | `UDisplayClusterProjectionPolicy` |
| `Synchronize Cluster` | 请求所有集群节点在下一帧执行强制同步。 | `UDisplayClusterSynchronizationManager` |

### 使用示例（蓝图描述）

1.  **初始化显示集群**：
    *   通常在 `BeginPlay` 中，使用 `Get nDisplay Cluster` 节点获取集群实例。
    *   通过集群实例的子节点（如 `Get Projection Policies`）可以访问具体的投影策略，进而调用 `Set Warp Blend Configuration` 等节点来动态调整投影。

2.  **查询本地节点信息**：
    *   调用 `Get Cluster Node ID` 可以得到当前游戏运行所在的集群节点ID（如 “node0”、“node1”）。
    *   结合 `Get Display Cluster Node Viewport` 等节点，可以获取该节点负责渲染的视口信息，用于实现基于节点的逻辑（如只在特定节点上播放UI）。

3.  **访问监控设置**：
    *   使用 `Get Default Object` 节点，并指定 `UDisplayClusterStageMonitoringSettings` 类，可以获取该类的CDO (Class Default Object)，从而读取或修改 `bEnableNvidiaHitchDetection` 等布尔配置。这些设置通常通过编辑器中的“项目设置”进行调整。

## C++ 用法

### 头文件引入

```cpp
// 核心集群管理
#include "DisplayClusterManager.h"
// 投影与校正
#include "DisplayClusterProjectionPolicy.h"
// 阶段监控
#include "DisplayClusterStageMonitoringSettings.h"
// 同步事件数据结构
#include "NvidiaSyncWatchdog.h"
#include "DWMSyncWatchdog.h"
```

### 基本用法 (来自 DisplayClusterStageMonitoringSettings.h)

获取并检查监控设置，这是配置nDisplay性能监控的基础。

```cpp
// 包含头文件
#include "DisplayClusterStageMonitoringSettings.h"

// 获取全局设置实例
const UDisplayClusterStageMonitoringSettings* Settings = GetDefault<UDisplayClusterStageMonitoringSettings>();
if (Settings)
{
    bool bNvidiaEnabled = Settings->ShouldEnableNvidiaWatchdog();
    bool bDWMEnabled = Settings->ShouldEnableDWMWatchdog();
    
    UE_LOG(LogTemp, Log, TEXT("Nvidia Hitch Detection: %s, DWM Hitch Detection: %s"), 
        bNvidiaEnabled ? TEXT("Enabled") : TEXT("Disabled"),
        bDWMEnabled ? TEXT("Enabled") : TEXT("Disabled"));
}
```

### 进阶用法 (来自 NvidiaSyncWatchdog.h 和 DWMSyncWatchdog.h)

理解并处理同步事件，用于性能分析和问题诊断。

```cpp
// 包含头文件
#include "NvidiaSyncWatchdog.h"
#include "DWMSyncWatchdog.h"
#include "StageProviderEventMessage.h" // 假设的基类

// 自定义一个函数来处理接收到的同步事件
void HandleSyncEvent(const FStageProviderEventMessage& Event)
{
    // 尝试转换为NVIDIA事件
    if (const FNvidiaSyncEvent* NvidiaEvent = static_cast<const FNvidiaSyncEvent*>(&Event))
    {
        UE_LOG(LogTemp, Warning, TEXT("Nvidia Sync: Missed %d frames, Last Frame: %.2f ms, Sync Duration: %.2f ms"), 
            NvidiaEvent->MissedFrames,
            NvidiaEvent->LastFrameDuration,
            NvidiaEvent->SynchronizationDuration);
    }
    // 尝试转换为DWM事件
    else if (const FDWMSyncEvent* DWMEvent = static_cast<const FDWMSyncEvent*>(&Event))
    {
        UE_LOG(LogTemp, Warning, TEXT("DWM Sync: Missed %u frames, PresentCount: %u"), 
            DWMEvent->MissedFrames,
            DWMEvent->PresentCount);
    }
}

// 在合适的上下文（例如自定义的渲染器或同步管理器回调）中，你可能会接收到此类事件并调用上面的函数。
// 这些事件通常由内部的FNvidiaSyncWatchdog和FDWMSyncWatchdog类在检测到同步问题时触发。
```

## Demo 示例

一个最小的示例，展示如何访问nDisplay的监控设置并模拟一个简单的同步事件处理。注意：nDisplay的实际使用通常需要通过编辑器进行复杂的显示配置。

```cpp
// MyNDisplayMonitor.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "DisplayClusterStageMonitoringSettings.h"
#include "MyNDisplayMonitor.generated.h"

UCLASS()
class UMyNDisplayMonitor : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 一个简化的函数，用于检查当前配置并打印状态 */
    void PrintMonitoringStatus() const;

private:
    // 存储设置指针（仅为示例，通常直接使用GetDefault）
    const UDisplayClusterStageMonitoringSettings* CachedSettings = nullptr;
};
```

```cpp
// MyNDisplayMonitor.cpp
#include "MyNDisplayMonitor.h"
#include "DisplayClusterStageMonitoringSettings.h"
#include "NvidiaSyncWatchdog.h"
#include "DWMSyncWatchdog.h"

void UMyNDisplayMonitor::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    // 获取并缓存设置（CDO）
    CachedSettings = GetDefault<UDisplayClusterStageMonitoringSettings>();
}

void UMyNDisplayMonitor::Deinitialize()
{
    CachedSettings = nullptr;
    Super::Deinitialize();
}

void UMyNDisplayMonitor::PrintMonitoringStatus() const
{
    if (!CachedSettings)
    {
        UE_LOG(LogTemp, Error, TEXT("StageMonitoring settings not available."));
        return;
    }

    UE_LOG(LogTemp, Display, TEXT("=== nDisplay Stage Monitoring Status ==="));
    UE_LOG(LogTemp, Display, TEXT("NVIDIA Hitch Detection: %s"), 
        CachedSettings->ShouldEnableNvidiaWatchdog() ? TEXT("ON") : TEXT("OFF"));
    UE_LOG(LogTemp, Display, TEXT("DWM Hitch Detection: %s"), 
        CachedSettings->ShouldEnableDWMWatchdog() ? TEXT("ON") : TEXT("OFF"));

    // 模拟创建一个同步事件用于演示其结构
    FNvidiaSyncEvent NvidiaEvent(3, 16.67f, 2.1f); // 错过3帧，上一帧耗时16.67ms，同步耗时2.1ms
    UE_LOG(LogTemp, Display, TEXT("Example Nvidia Event: %s"), *NvidiaEvent.ToString());

    FDWMSyncEvent DWMEvent(1, 100, 99, 60); // 错过1帧，当前呈现计数100，上一次99，刷新计数60
    UE_LOG(LogTemp, Display, TEXT("Example DWM Event: %s"), *DWMEvent.ToString());
}

// 你可以在某个Actor或另一个子系统中调用：
// UGameInstance* GI = ...;
// if (UMyNDisplayMonitor* Monitor = GI->GetSubsystem<UMyNDisplayMonitor>())
// {
//     Monitor->PrintMonitoringStatus();
// }
```

## 模块依赖

根据提供的模块依赖信息，nDisplay插件的模块普遍依赖于标准的引擎模块（如Core, CoreUObject, Engine等）。以下列出了比较特殊或不常见的依赖项。

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | `DisplayClusterMedia`和`SharedMemoryMedia`模块依赖此模块，用于与DirectX 12渲染硬件接口交互，实现高效的帧共享和媒体输出。 |
| `UnrealEd`, `EditorWidgets`, `LevelEditor` | 多个`Editor`后缀的模块依赖这些，用于在Unreal编辑器中提供专属的配置界面、工具栏和资产编辑器。 |
| 无（纯内容插件） | `ScalableMPCDI`是一个外部依赖模块，为MPCDI（多投影机校准数据接口）提供支持。 |

**注意**：由于该插件模块众多且功能复杂，使用时请根据所需功能，在项目的`.Build.cs`文件中添加对应的模块依赖。例如，若需要使用集群投影功能，则可能需要依赖`DisplayClusterProjection`。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为nDisplay的MoviePipeline添加多层EXR渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 统一MoviePipeline中的几何校正/混合模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了MRG中相机命名问题和MPCDI着色器的alpha混合问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码回退时忽略自定义Gamma值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理小于视口尺寸时出现的闪烁问题。 |

### 维护评价

**综合评价：活跃维护，推荐用于专业项目。**

-   **创建时间**：该插件自2018年随UE 4.20版本引入，已发展超过8年，是一个成熟且专业的解决方案。
-   **近期更新频率和内容**：从Git历史看，在2026年5月仍有密集且重要的功能更新（如多层EXR支持、着色器修复）和错误修复。更新内容集中在核心渲染功能、管线集成和稳定性上，表明该插件仍在被Epic Games积极开发和优化。
-   **活跃维护**：是。最近一次实质性更新距今非常近。
-   **已知问题或限制**：作为专业级工具，其配置和部署相对复杂，需要硬件和网络环境的支持。从近期更新看，团队正在持续解决各种渲染和同步边缘情况的问题。
-   **推荐使用**：对于虚拟制片、大型沉浸式投影、多屏模拟等专业且高预算的项目，nDisplay是UE官方提供的核心且强大的解决方案，强烈推荐使用。对于简单的多显示器扩展需求，可能有些“重”，但其提供的精确同步和几何校正能力是无可替代的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/) (官方文档链接，非.uplugin提供)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)