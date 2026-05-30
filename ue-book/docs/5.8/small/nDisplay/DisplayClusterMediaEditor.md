# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 分布式显示系统 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、媒体资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `SharedMemoryMedia` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一套用于在多个物理PC上进行同步、集群化渲染的系统。其核心是通过网络同步多个运行 Unreal Engine 的节点，让它们作为一个统一的“显示集群”协同工作，将画面渲染到由多个显示器或投影仪组成的大型、复杂的视觉系统上。它解决了以下问题：

1.  **多PC同步渲染**：允许将渲染负载分摊到多台机器上，实现超出单机性能上限的超高分辨率或多视角渲染。
2.  **复杂显示拓扑支持**：支持多种显示布局，如多通道CAVE系统、360度环绕LED墙、曲面投影幕等。
3.  **立体渲染支持**：原生支持单目（Mono）和立体（Stereo）渲染模式，适用于VR和大型立体显示装置。
4.  **与虚拟制作（Virtual Production）深度集成**：是大型LED虚拟影棚（ICVFX）渲染管线的核心技术，负责将摄像机视点渲染到LED墙上，确保透视关系正确。
5.  **网络通信与控制**：提供主控（Master）-从属（Cluster）节点架构，管理节点间的状态同步、输入同步和远程控制。

## 使用场景

-   **虚拟制片 (ICVFX)**：你在搭建一个LED虚拟影棚，需要多台渲染服务器同时驱动高分辨率的LED墙，渲染出与摄像机视角完美匹配的背景画面。
-   **大型沉浸式环境**：你在构建一个CAVE（洞穴自动虚拟环境）或一个270度环幕飞行模拟器，需要多个投影仪或屏幕协同显示一个无缝的虚拟世界。
-   **超高分辨率/多视角渲染**：你需要渲染8K或更高分辨率的画面，或者一个画面需要从多个不同角度（如主视角和侧视图）同时输出到不同显示器。
-   **电影长镜头渲染**：在电影制作中，使用`MoviePipeline`模块与nDisplay结合，将复杂的长镜头渲染任务分配到集群上并行执行。
-   **多用户协作与监控**：在集群环境中，你需要一个统一的界面（Operator）来监控所有节点的状态、性能，并进行远程调试。

## 蓝图用法

nDisplay的蓝图API主要集中在配置和运行时控制上，核心类为`UDisplayClusterConfigurationData`和`ADisplayClusterRootActor`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node Id` | 获取当前节点的唯一标识符（如 `node_0`）。用于区分集群中的主节点和从节点。 | `UDisplayCluster` |
| `Get Master Node` | 获取主节点（Master）的标识符。 | `UDisplayCluster` |
| `Is Master` | 判断当前运行实例是否是集群中的主节点。 | `UDisplayCluster` |
| `Get Configuration` | 获取当前加载的nDisplay集群配置数据对象。 | `UDisplayCluster` |
| `Get Viewports` | 获取当前节点负责渲染的所有视口信息。 | `UDisplayClusterConfiguration` |
| `Get Screen` | 根据屏幕ID获取其配置（位置、朝向、投影参数）。 | `UDisplayClusterConfiguration` |

### 使用示例（蓝图描述）

1.  **初始化与判断**：在你的游戏模式或主逻辑蓝图中，首先调用 `Get Cluster Node Id` 获取当前节点ID。然后使用 `Is Master` 节点进行判断，主节点可以执行特殊的逻辑（如启动游戏、管理输入），而从节点则等待主节点的信号。
2.  **配置查询**：通过 `Get Configuration` 获取 `UDisplayClusterConfigurationData` 对象，然后可以调用 `Get Viewports` 或 `Get Screen` 来查询当前节点的渲染设置，用于动态调整渲染内容或进行后处理。
3.  **输入同步**：nDisplay内部处理了输入同步，但你可能需要在蓝图中处理特定的输入逻辑。通常，在主节点上处理输入，从节点通过网络接收同步后的输入状态。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayCluster.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterRootActor.h"
```

### 基本用法：检查集群身份与获取配置

这是nDisplay编程中最常见的起步操作。

```cpp
// 获取nDisplay单例
UDisplayCluster& DisplayCluster = UDisplayCluster::Get();

// 检查当前是否在nDisplay集群中运行
if (DisplayCluster.IsRunning())
{
    // 获取当前节点ID
    const FString CurrentNodeId = DisplayCluster.GetClusterNodeId();

    // 判断是否是主节点
    const bool bIsMaster = DisplayCluster.IsMaster();

    UE_LOG(LogTemp, Log, TEXT("Running in nDisplay cluster. Node: %s, IsMaster: %s"),
        *CurrentNodeId,
        bIsMaster ? TEXT("Yes") : TEXT("No"));

    // 获取集群配置数据
    if (UDisplayClusterConfigurationData* Config = DisplayCluster.GetConfiguration())
    {
        // 访问配置数据，例如获取所有视口信息
        const TMap<FString, FDisplayClusterConfigurationViewport>& Viewports = Config->Viewports;
        // ... 处理视口配置
    }
}
```
*来源：nDisplay核心运行时逻辑的典型模式。*

### 进阶用法：在集群节点间同步游戏状态

主节点收集状态，广播给所有从节点以保持同步。

```cpp
// 假设在一个共享的游戏状态管理类中
void AMyGameState::SyncGameTime()
{
    UDisplayCluster& DisplayCluster = UDisplayCluster::Get();
    if (DisplayCluster.IsRunning() && DisplayCluster.IsMaster())
    {
        // 主节点计算并广播游戏时间
        float CurrentTime = GetWorld()->GetTimeSeconds();
        // 使用nDisplay的集群通信机制进行广播（具体API取决于插件版本）
        // 例如，可能通过自定义消息或利用其网络层
        BroadcastClusterTime(CurrentTime);
    }
    else if (DisplayCluster.IsRunning())
    {
        // 从节点接收并应用游戏时间（通常通过网络回调实现）
        // float ReceivedTime = ...;
        // GetWorld()->SetTimeSeconds(ReceivedTime);
    }
}
```
*来源：基于多PC同步逻辑的常见设计模式推断。*

## Demo 示例

一个最小化的nDisplay应用，演示如何在游戏模式中判断集群角色并执行不同逻辑。

**MyGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyGameMode.generated.h"

UCLASS()
class MYPROJECT_API AMyGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	virtual void StartPlay() override;

private:
	void HandleClusterSetup();
};
```

**MyGameMode.cpp**
```cpp
#include "MyGameMode.h"
#include "DisplayCluster.h"
#include "DisplayClusterLog.h"

void AMyGameMode::StartPlay()
{
	Super::StartPlay();

	HandleClusterSetup();
}

void AMyGameMode::HandleClusterSetup()
{
	UDisplayCluster& DisplayCluster = UDisplayCluster::Get();
	if (DisplayCluster.IsRunning())
	{
		UE_LOG(LogDisplayCluster, Log, TEXT("nDisplay cluster detected."));

		if (DisplayCluster.IsMaster())
		{
			UE_LOG(LogDisplayCluster, Log, TEXT("This is the MASTER node. Initiating game logic."));
			// 主节点：启动游戏逻辑，播放开场动画，接受玩家输入等。
		}
		else
		{
			UE_LOG(LogDisplayCluster, Log, TEXT("This is a CLUSTER node (%s). Waiting for sync."), *DisplayCluster.GetClusterNodeId());
			// 从节点：可能进入只渲染模式，等待主节点的同步信号。
			// 从节点的玩家控制器输入通常被禁用。
		}
	}
	else
	{
		UE_LOG(LogDisplayCluster, Log, TEXT("Running in standalone mode."));
		// 独立模式：执行普通的游戏逻辑。
	}
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MediaUtils` | 处理媒体资产（如SharedMemoryMedia）的基础功能。 |
| `LiveLinkInterface` | 用于与实时动作捕捉等设备进行数据同步（通过LiveLink）。 |
| `D3D12RHI` | 支持DirectX 12渲染硬件接口，用于高性能的跨节点纹理共享（SharedMemoryMedia）。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染图和nDisplay添加了多层EXR图像序列支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在电影渲染管线中，将WarpBlendAlpha模式合并到WarpBlend模式中。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了媒体资源图中的拓扑感知相机命名问题，并修正了MPCDI/ICVFX着色器中的不透明Alpha通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | nDisplay现在能在输出帧编码的回退路径中正确处理非默认的DisplayGamma设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时可能导致的闪烁问题。 |

### 维护评价

nDisplay插件处于**非常活跃**的维护状态。
- **年龄**：插件诞生于2018年（UE4 4.20时期），历史较长，是成熟的技术。
- **活跃度**：最近的提交记录（2026年5月）密集且包含功能性更新、bug修复和着色器优化，表明Epic Games仍在积极投入开发，尤其与虚拟制作和电影渲染管线结合紧密。
- **推荐度**：**强烈推荐**用于任何需要多PC集群渲染、虚拟制片（ICVFX）或多通道投影的项目。它是UE在该领域的核心解决方案，功能完整且持续更新。唯一的门槛是其架构复杂性，需要一定的学习和调试成本。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)