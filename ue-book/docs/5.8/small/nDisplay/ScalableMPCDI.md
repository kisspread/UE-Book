# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台 PC 进行同步集群渲染，可单目或立体显示）

| 属性 | 值 |
|---|---|
| 中文名 | 多屏显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、示例配置） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`nDisplay` 是 UE5 的官方多屏幕集群渲染解决方案，用于将单个 UE 项目同步渲染到多个显示设备（如 LED 墙、CAVE 系统、投影阵列）上。它解决的核心问题是如何让一个场景在多台电脑（渲染节点）上协调渲染，确保画面在几何校正、颜色一致性和时间同步后能无缝拼接成一个完整的视觉画面。

它不只是简单的分屏，而是一个完整的集群管理系统，包含了：
*   **集群架构**：定义主节点、渲染节点（簇）和备份节点的通信与控制。
*   **几何校正与投影**：支持 MPCDI、Camera Link 等投影技术，处理曲面、复杂几何表面的投影。
*   **同步与锁定**：确保所有渲染节点的帧、时间和参数严格同步。
*   **资源管理**：集中管理集群的配置、资产和渲染设置。
*   **编辑器工具**：提供可视化配置工具、远程控制和监控面板。

其最终目的是支持电影虚拟制片（Virtual Production）、沉浸式体验（主题乐园、展览）、飞行模拟器等专业领域。

## 使用场景

*   你在使用 **LED 墙进行影视虚拟制片**，需要将 UE 场景实时、同步地渲染到由多台 GPU 驱动的 LED 面板组成的巨幕上。→ 使用 `nDisplay` 配置 LED 墙的拓扑、几何校正，并驱动所有渲染节点。
*   你正在搭建一个 **CAVE（洞穴自动虚拟环境）** 或 **沉浸式穹顶**，需要将画面投影到房间的多个面上（地面、天花板、四面墙）。→ 使用 `nDisplay` 定义每个投影面的几何与视图，并同步所有投影仪的输出。
*   你需要为一个 **多屏幕驾驶模拟器** 创建无缝的视野，每块屏幕由独立的 PC 渲染。→ 使用 `nDisplay` 配置屏幕布局，确保驾驶视角在各个屏幕间平滑过渡。
*   你在 **大型展览或主题乐园** 项目中，需要远程监控和管理一个由数十台渲染 PC 组成的集群。→ 使用 `nDisplay` 的 Operator 控制台和 Stage Monitor 工具。

## 蓝图用法

`nDisplay` 在蓝图中暴露了强大的控制接口，主要用于运行时查询状态和远程控制。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前运行实例的集群节点 ID（字符串）。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Role` | 获取当前节点的角色（Primary / Secondary / Backup）。 | `UDisplayClusterBlueprintAPI` |
| `Is Cluster Primary` | 判断当前节点是否是主节点。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Time` | 获取经过同步校准的集群全局时间。 | `UDisplayClusterBlueprintAPI` |
| `Get Sync Policy` | 获取当前使用的同步策略。 | `UDisplayClusterBlueprintAPI` |
| `Trigger Cluster Event` | 向集群中的所有节点广播一个自定义事件。 | `UDisplayClusterBlueprintAPI` |
| `Get All Cluster Node IDs` | 获取集群中所有节点的 ID 列表。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **判断当前节点并执行逻辑**：
    *   使用 `Get Cluster Role` 节点。
    *   通过 `Switch` 或 `Branch` 节点判断返回值。
    *   如果 `Role == Primary`，则执行主节点独有的逻辑（如游戏逻辑）。
    *   如果 `Role == Secondary`，则可能只执行渲染或特定的子任务。

2.  **在所有节点上同步播放一个声音**：
    *   使用 `Trigger Cluster Event` 节点，设置事件名称（例如 `"PlaySound"`）和自定义参数。
    *   每个节点上都注册一个 `Bind Event to Cluster Event` 事件，监听 `"PlaySound"` 事件。
    *   在事件处理函数中，使用接收到的参数（如声音资产路径）来播放声音。

## C++ 用法

C++ 接口提供了对 `nDisplay` 核心系统的底层访问，主要用于创建自定义模块、扩展功能或进行深度集成。

### 头文件引入

```cpp
// 核心集群 API
#include "DisplayCluster.h"
#include "DisplayClusterModule.h"

// 配置相关
#include "DisplayClusterConfigurationTypes.h"

// 投影相关 (如需自定义投影)
#include "IDisplayClusterProjectionPolicy.h"
```

### 基本用法

**1. 获取集群信息**
```cpp
// 来自 DisplayCluster 模块的公开接口
IDisplayCluster& DisplayClusterModule = IDisplayCluster::Get();
FString NodeId = DisplayClusterModule.GetCurrentNodeId();
EDisplayClusterNodeRole Role = DisplayClusterModule.GetCurrentNodeRole();

if (Role == EDisplayClusterNodeRole::Primary)
{
    // 主节点逻辑
}
```

**2. 访问和修改配置**
```cpp
// 获取当前的 nDisplay 配置资产 (UDisplayClusterConfigurationData)
const UDisplayClusterConfigurationData* ConfigData = DisplayClusterModule.GetConfiguration();

if (ConfigData && ConfigData->Cluster)
{
    // 遍历所有节点配置
    for (const auto& NodePair : ConfigData->Cluster->Nodes)
    {
        const FDisplayClusterConfigurationClusterNode& NodeConfig = NodePair.Value;
        UE_LOG(LogTemp, Log, TEXT("Node ID: %s, Host: %s"), *NodePair.Key, *NodeConfig.Host);
    }
}
```

### 进阶用法

**创建自定义的投影策略 (Projection Policy)**
nDisplay 允许通过插件扩展投影方式。你需要实现 `IDisplayClusterProjectionPolicyFactory` 接口来注册你的策略工厂。
```cpp
// 1. 定义你的工厂类
class FMyProjectionPolicyFactory : public IDisplayClusterProjectionPolicyFactory
{
public:
    virtual TSharedPtr<IDisplayClusterProjectionPolicy> Create(const FString& ProjectionPolicyId, const FDisplayClusterConfigurationProjection* InConfigurationPolicy) override
    {
        // 在此创建并返回你的自定义投影策略实例
        return MakeShared<FMyProjectionPolicy>(ProjectionPolicyId, InConfigurationPolicy);
    }
};

// 2. 在你的模块 StartupModule 中注册工厂
void FMyModule::StartupModule()
{
    IDisplayCluster::Get().RegisterProjectionPolicyFactory(TEXT("MyPolicy"), MakeShared<FMyProjectionPolicyFactory>());
}
```

## Demo 示例

以下示例展示了一个最小的 `nDisplay` 主节点程序，它初始化集群并输出基本的集群信息。

**MyDisplayClusterGameMode.h**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "MyDisplayClusterGameMode.generated.h"

UCLASS()
class AMyDisplayClusterGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void StartPlay() override;
    void LogClusterInfo();
};
```

**MyDisplayClusterGameMode.cpp**
```cpp
#include "MyDisplayClusterGameMode.h"
#include "DisplayCluster.h"

void AMyDisplayClusterGameMode::StartPlay()
{
    Super::StartPlay();

    // 仅在主节点上执行初始化
    if (IDisplayCluster::Get().GetCurrentNodeRole() == EDisplayClusterNodeRole::Primary)
    {
        LogClusterInfo();
        UE_LOG(LogTemp, Warning, TEXT("nDisplay Primary Node has started the game."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay Secondary Node %s is ready."), *IDisplayCluster::Get().GetCurrentNodeId());
    }
}

void AMyDisplayClusterGameMode::LogClusterInfo()
{
    IDisplayCluster& DC = IDisplayCluster::Get();
    UE_LOG(LogTemp, Log, TEXT("=== Cluster Info ==="));
    UE_LOG(LogTemp, Log, TEXT("Node ID: %s"), *DC.GetCurrentNodeId());
    UE_LOG(LogTemp, Log, TEXT("Role: %s"), (DC.GetCurrentNodeRole() == EDisplayClusterNodeRole::Primary) ? TEXT("Primary") : TEXT("Secondary"));

    const UDisplayClusterConfigurationData* Config = DC.GetConfiguration();
    if (Config && Config->Cluster)
    {
        UE_LOG(LogTemp, Log, TEXT("Total Nodes in Config: %d"), Config->Cluster->Nodes.Num());
    }
}
```

## 模块依赖

`nDisplay` 插件拥有庞大而复杂的模块体系。为了在你的项目或插件中使用它，主要的依赖项如下：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 核心运行时逻辑，集群管理，API 入口点。 |
| `DisplayClusterConfiguration` | 处理 `.ndisplay` 配置文件的数据模型和解析。 |
| `DisplayClusterProjection` | 各种投影策略（MPCDI, Camera Link, Mesh等）的实现。 |
| `DisplayClusterShaders` | 用于几何校正、颜色混合和后处理的着色器。 |
| `MediaFrameworkUtilities` | 集成媒体框架，用于外部视频输入/输出（如与媒体播放器协作）。 |
| `Networking`, `Sockets` | 用于集群节点间的 TCP/UDP 通信。 |

**注意**：许多模块（如 `DisplayClusterEditor`, `DisplayClusterLightCardEditor`）依赖于 `UnrealEd`，这些是编辑器专用模块，在打包项目中不可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了 EXR 多图层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 中的 WarpBlendAlpha 模式合并到 WarpBlend 功能中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机命名问题；修复了 MPCDI/ICVFX 着色器中的不透明 Alpha 通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 使 nDisplay 在输出帧编码回退时能正确处理非默认的显示伽马值。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时产生的闪烁问题。 |

### 维护评价

`nDisplay` 是 Epic Games 官方维护的**核心虚拟制片模块**之一，属于**活跃维护**状态。
*   **活跃度**：从 git 历史看，最近几个月仍有持续的功能更新（如 EXR 多图层、MoviePipeline 集成）和重要的 bug 修复。
*   **重要性**：作为 Unreal Engine 虚拟制片工具链的基石，其地位类似于 Chaos 物理系统或 Niagara 特效系统，是长期支持的重点。
*   **复杂性**：由于其专业性和庞大的模块数量（29个模块），学习和调试曲线较陡峭，但文档和示例在不断完善。
*   **推荐**：对于需要集群渲染的影视、仿真和沉浸式体验项目，`nDisplay` 是**官方推荐且唯一成熟的解决方案**，应优先使用并关注其更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)