# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（支持使用多台PC进行同步集群渲染，支持单声道或立体声模式）

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个专为 **虚拟制片（Virtual Production）、沉浸式体验（如CAVE、穹顶投影）和大型LED墙** 设计的高级渲染框架。它不仅仅是多显示器支持，其核心功能在于解决 **跨多台独立PC（节点）的同步、低延迟渲染和状态复制** 问题。

它通过自定义的网络驱动程序（`UDisplayClusterNetDriver`）和连接（`UDisplayClusterNetConnection`），确保所有集群节点在渲染同一帧时，角色（Actor）的状态、位置、动画以及任何可复制的属性都完全一致，从而实现无缝拼接的、无撕裂的宏大视觉输出。这解决了标准UE网络复制在高度同步的视觉输出场景下可能出现的微小抖动和不一致问题。

## 使用场景

- **大型LED墙虚拟制片**：你正在搭建一个由数十个面板组成的大型LED摄影棚，需要多台渲染PC协同输出一个连贯的虚拟场景，且演员的实时动作必须在所有面板上精确同步。
- **穹顶投影系统**：你在建造一个飞行模拟器或天文馆，需要多台投影机覆盖一个球形屏幕，每台PC渲染球体的一部分，并要求所有画面无缝融合。
- **CAVE（洞穴自动虚拟环境）**：你需要在一个由多面屏幕构成的立方体房间内创建沉浸式VR体验，每台PC负责渲染一面墙的内容。
- **多通道音频/视频同步**：你需要确保视觉输出与外部的灯光、音效或其他媒体设备精确同步。
- **离线渲染复杂场景**：利用Movie Pipeline模块，将渲染任务分发到集群中的多台PC上，大幅缩短电影或过场动画的渲染时间。

## 蓝图用法

nDisplay 的配置和操作大量通过其专用的编辑器工具（`DisplayClusterConfigurator`）和运行时API进行。核心的网络同步功能主要在C++层面处理，但以下是一些暴露给蓝图的关键交互点：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node Id` | 获取当前进程在集群中的唯一节点ID（用于主从判断）。 | `UDisplayCluster` |
| `Is Primary Node` | 判断当前节点是否为集群中的主节点。 | `UDisplayCluster` |
| `Get Cluster Event Manager` | 获取集群事件管理器，用于发送/接收自定义二进制或字符串事件。 | `UDisplayCluster` |
| `Get Cluster Sync Object` | 获取集群同步对象，用于在节点间同步自定义状态。 | `UDisplayCluster` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接与 `UDisplayClusterNetDriver` 交互。常见的模式是：

1.  **查询节点信息**：在游戏逻辑开始时，调用 `Get Cluster Node Id` 和 `Is Primary Node`。主节点可以负责初始化需要全局唯一实例的逻辑（如生成最终的游戏管理者）。
2.  **发送集群事件**：当需要触发一个需要在所有节点上同步执行的操作（例如，在特定时间点切换灯光预设），可以通过“Get Cluster Event Manager”获取管理器，然后使用“Send Cluster Event”节点广播一个事件。所有节点的事件监听器都会收到通知并执行相应逻辑。

## C++ 用法

### 头文件引入

根据你使用的模块引入头文件。
```cpp
#include “DisplayCluster/Public/DisplayCluster.h” // 核心模块
#include “DisplayCluster/Public/Cluster/DisplayClusterClusterEvent.h” // 集群事件
```

### 基本用法

从提供的 `DisplayClusterNetConnection.h` 和 `DisplayClusterNetDriver.h` 可以看出，其核心是自定义的网络层。开发者通常不直接实例化这些类，而是通过配置文件和nDisplay运行时来管理。

```cpp
// 示例：检查当前是否为主节点并记录日志
if (IDisplayCluster::IsAvailable())
{
    IDisplayCluster& DisplayClusterModule = IDisplayCluster::Get();
    if (DisplayClusterModule.GetClusterMgr() != nullptr)
    {
        bool bIsPrimary = DisplayClusterModule.GetClusterMgr()->IsPrimary();
        UE_LOG(LogTemp, Log, TEXT(“Current node is primary: %s”), bIsPrimary ? TEXT(“true”) : TEXT(“false”));
    }
}
```

### 进阶用法：处理集群事件

集群事件是节点间通信的关键机制。

```cpp
// 1. 注册一个二进制事件监听器
FOnClusterEventBinaryListener BinaryListener;
BinaryListener.BindLambda([](const FDisplayClusterClusterEventBinary& Event)
{
    // 处理接收到的二进制事件
    // Event.EventId, Event.EventData 可用于识别和解析
});
IDisplayCluster::Get().GetClusterEventMgr()->AddClusterEventListener(BinaryListener);

// 2. 在某个逻辑中发送一个二进制事件
FDisplayClusterClusterEventBinary MyEvent;
MyEvent.EventId = TEXT(“MyCustomEvent”);
MyEvent.EventData.Append((uint8*)”Hello”, 5); // 示例数据
IDisplayCluster::Get().GetClusterEventMgr()->EmitClusterEvent(MyEvent, true); // true表示同步发送
```

## Demo 示例

一个最小的演示，展示如何获取集群模块并进行基本查询。

**NDisplayMinimalDemo.h**
```cpp
#pragma once
#include “CoreMinimal.h”

class FNDisplayMinimalDemo
{
public:
    static void PrintClusterInfo();
};
```

**NDisplayMinimalDemo.cpp**
```cpp
#include “NDisplayMinimalDemo.h”
#include “DisplayCluster/Public/DisplayCluster.h”
#include “DisplayCluster/Public/Cluster/IDisplayClusterClusterManager.h”

void FNDisplayMinimalDemo::PrintClusterInfo()
{
    if (!IDisplayCluster::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT(“nDisplay plugin is not available.”));
        return;
    }

    IDisplayCluster& DC = IDisplayCluster::Get();
    IDisplayClusterClusterManager* ClusterMgr = DC.GetClusterMgr();
    if (!ClusterMgr)
    {
        UE_LOG(LogTemp, Warning, TEXT(“Cluster Manager is not initialized. Running in standalone mode?”));
        return;
    }

    const FString NodeId = ClusterMgr->GetNodeId();
    const bool bIsPrimary = ClusterMgr->IsPrimary();
    const int32 ClusterSize = ClusterMgr->GetNodesAmount();

    UE_LOG(LogTemp, Log,
        TEXT(“nDisplay Cluster Info:\n  Node ID: %s\n  Is Primary: %s\n  Cluster Size: %d”),
        *NodeId,
        bIsPrimary ? TEXT(“Yes”) : TEXT(“No”),
        ClusterSize);
}
```

## 模块依赖

以下列出使用 nDisplay 核心功能时，你的 Build.cs 可能需要依赖的**独特**模块（常见的 Core, Engine 等已省略）。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，提供集群管理和基础功能。 |
| `DisplayClusterConfiguration` | 用于解析和管理 `.ndisplay` 配置文件资产。 |
| `DisplayClusterProjection` | 处理投影（Projection）和变形（Warping）逻辑。 |
| `DisplayClusterMedia` | 用于集成外部媒体源（如SDI捕获卡）到渲染流程中。 |
| `DisplayClusterReplication` | 实现自定义网络驱动，保证多节点状态精确同步。 |
| `DisplayClusterMoviePipeline` | 与Sequencer和Movie Pipeline集成，支持集群离线渲染。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了 EXR 多图层支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将 MoviePipeline 中的 WarpBlendAlpha 模式合并到 WarpBlend 中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知相机的命名问题，以及 MPCDI/ICVFX 着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，遵循非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 是一个**积极维护**的核心功能插件。尽管它自2018年就已存在（属于“老古董”级别），但从近期（2026年5月）的密集提交历史来看，它仍在不断迭代和修复问题。更新内容涵盖了功能增强（如多图层EXR）、与新系统（Movie Graph）的集成、以及针对着色器和渲染管线的具体Bug修复。

**推荐使用**：对于任何需要多机同步渲染的虚拟制片、模拟或沉浸式项目，nDisplay 是 Epic Games 官方提供的唯一且经过生产验证的解决方案。虽然学习曲线较陡峭（涉及网络、渲染、投影等多个领域），但其稳定性和功能深度使其成为大型项目的必然选择。唯一需要注意的是，其默认未启用（`EnabledByDefault: false`），表明它面向特定的、高级的使用场景。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/)（插件专用文档 URL 为空，可参考 UE 官方文档中关于 nDisplay 和虚拟制片的章节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)