# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、媒体资产、着色器） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterOperator` (Runtime) 等多个模块 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 插件是一个为高级虚拟制片、大型沉浸式环境（如LED舞台、投影穹顶、CAVE系统）设计的核心集群渲染解决方案。它解决的核心问题是**使用多台联网的计算机（集群）协同渲染一个或多个视图，并将其输出到复杂的物理显示布局上**。

该插件的核心功能包括：
- **同步集群渲染**：精确同步集群中所有PC的渲染，确保多屏幕画面一致。
- **几何校正与投影**：处理复杂的投影面（如曲面、多平面），进行边缘融合和几何畸变校正。
- **颜色分级与管理**：在集群范围内统一管理颜色配置文件和分级参数。
- **媒体输入/输出集成**：通过共享内存等技术实现低延迟、高带宽的媒体流传输，与LED墙等设备对接。
- **远程控制与监控**：提供工具来远程启动、停止和监控集群渲染状态。

它本质上是一个分布式渲染引擎，将Unreal Engine的渲染能力扩展到单台PC之外。

## 使用场景

- **虚拟制片（Virtual Production）**：驱动由多台LED处理器控制的大型LED墙，为电影和电视拍摄提供实时背景。
- **多投影仪环境**：校准并驱动投影到穹顶、曲面或环形幕布上的多个投影仪。
- **CAVE自动虚拟环境**：渲染用于沉浸式科学可视化或训练的多面体显示环境。
- **大型演示装置**：在博物馆、展览馆或企业展厅中，驱动由多个显示屏组成的超大画面或非常规形状的显示墙。

## 蓝图用法

由于nDisplay的蓝图API通常围绕其配置和运行时状态展开，且其核心逻辑位于C++模块中，蓝图节点主要用于配置访问和流程控制。以下为推测的核心功能节点（基于插件架构）：

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node` | 获取当前集群中指定节点的信息。 | `UDisplayClusterManager` (推测) |
| `Apply Configuration` | 从资产文件加载并应用一个nDisplay集群配置。 | `UDisplayClusterConfigurationManager` (推测) |
| `Start Cluster` | 启动集群渲染会话。 | `UDisplayClusterManager` (推测) |
| `Stop Cluster` | 停止当前集群渲染会话。 | `UDisplayClusterManager` (推测) |
| `Get Active Viewport ID` | 获取当前活动的视口标识符。 | `UDisplayClusterViewportManager` (推测) |

### 使用示例（蓝图描述）

在关卡蓝图或GameMode中，你可以这样编排一个基础的集群启动流程：
1.  使用 `Load Asset` 节点加载一个 `UDisplayClusterConfiguration` 资产。
2.  调用 `Apply Configuration` 节点，将加载的配置应用到集群管理器。
3.  调用 `Start Cluster` 节点，根据配置启动所有集群节点。
4.  使用 `Event Tick` 监听 `Get Cluster Node` 的状态，确保所有节点正常运行。
5.  游戏结束时，调用 `Stop Cluster` 节点清理资源。

## C++ 用法

nDisplay的C++集成主要涉及加载配置、管理集群生命周期以及与投影、媒体等子系统交互。

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfiguration.h"
#include "DisplayClusterManager.h" // 可能为IDisplayClusterManager接口
```

### 基本用法

以下代码展示了如何在C++中初始化和应用一个nDisplay配置。
*（来源：基于nDisplay插件架构的典型用法推断）*

```cpp
// 假设你有一个指向集群根Actor的指针
ADisplayClusterRootActor* ClusterRootActor = ...;

// 获取或创建配置资产
UDisplayClusterConfiguration* Configuration = LoadObject<UDisplayClusterConfiguration>(nullptr, TEXT("/Game/MyCluster/ClusterConfig"));

if (Configuration && ClusterRootActor)
{
    // 将配置应用到根Actor（这会触发集群的重新初始化）
    ClusterRootActor->SetConfiguration(Configuration);
    
    // 稍后，你可以通过集群管理器检查状态
    // IDisplayClusterClusterManager* ClusterManager = IDisplayCluster::Get().GetClusterManager();
    // if (ClusterManager && ClusterManager->IsRunning())
    // {
    //     UE_LOG(LogTemp, Log, TEXT("nDisplay cluster is running!"));
    // }
}
```

### 进阶用法

结合媒体模块，设置一个共享内存媒体输出。
*（来源：`DisplayClusterMedia` 模块的设计思路推断）*

```cpp
#include "SharedMemoryMediaOutput.h"
#include "DisplayClusterViewport.h"

// 在集群的某个节点上，获取其主视口
UDisplayClusterViewport* Viewport = ClusterRootActor->GetViewport(TEXT("viewport_left"));

if (Viewport)
{
    // 创建共享内存媒体输出
    USharedMemoryMediaOutput* MediaOutput = NewObject<USharedMemoryMediaOutput>(GetTransientPackage());
    MediaOutput->MediaName = TEXT("LedWallLeft");
    // ... 配置共享内存名称、尺寸等参数 ...

    // 将媒体输出绑定到视口
    // Viewport->SetMediaOutput(MediaOutput); // 接口名可能不同
}
```

## Demo 示例

一个最小的、用于启动本地集群（单机模拟）的C++示例。
*（基于插件核心接口的简化用法）*

**DisplayClusterDemo.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterDemo.generated.h"

class UDisplayClusterConfiguration;

UCLASS()
class ADisplayClusterDemo : public AActor
{
	GENERATED_BODY()

public:
	ADisplayClusterDemo();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

protected:
	UPROPERTY(EditAnywhere, Category = "nDisplay")
	TObjectPtr<UDisplayClusterConfiguration> ClusterConfig;
};
```

**DisplayClusterDemo.cpp**
```cpp
#include "DisplayClusterDemo.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfiguration.h"
#include "DisplayClusterSubsystem.h"
#include "Engine/World.h"

ADisplayClusterDemo::ADisplayClusterDemo()
{
	PrimaryActorTick.bCanEverTick = false;
}

void ADisplayClusterDemo::BeginPlay()
{
	Super::BeginPlay();

	// 获取或生成集群根Actor
	ADisplayClusterRootActor* RootActor = nullptr;
	for (TActorIterator<ADisplayClusterRootActor> It(GetWorld()); It; ++It)
	{
		RootActor = *It;
		break;
	}
	if (!RootActor)
	{
		RootActor = GetWorld()->SpawnActor<ADisplayClusterRootActor>();
	}

	// 应用配置（如果在编辑器中指定了）
	if (ClusterConfig && RootActor)
	{
		RootActor->SetConfiguration(ClusterConfig);
		UE_LOG(LogTemp, Log, TEXT("Applied nDisplay configuration."));
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("No nDisplay configuration set on the demo actor."));
	}
}

void ADisplayClusterDemo::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	Super::EndPlay(EndPlayReason);
	// 集群的停止通常由根Actor或子系统自动处理，无需手动代码
}
```

## 模块依赖

要使用nDisplay插件，你的项目模块通常需要依赖以下模块（已排除标准Core/Engine依赖）：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay的核心运行时逻辑。 |
| `DisplayClusterConfiguration` | 处理集群配置资产（`.ndisplay` 文件）。 |
| `DisplayClusterProjection` | 负责几何校正、投影映射和边缘融合。 |
| `DisplayClusterMedia` | 提供媒体流输入/输出功能（如共享内存）。 |
| `SharedMemoryMedia` | 共享内存媒体传输的底层实现。 |
| `MediaFrameworkUtilities` | Epic媒体框架的工具集。 |
| `MPCDI` | 支持多通道像素延迟积分（MPCDI）标准。 |
| `ProceduralMeshComponent` | 可能用于动态生成投影网格。 |
| `DisplayClusterOperator` | 提供操作员UI和远程控制功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为nDisplay的电影管线图添加了EXR多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线中简化了WarpBlend模式，将WarpBlendAlpha合并。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了MRG中拓扑感知的相机命名问题，以及MPCDI/ICVFX着色器的不透明alpha通道问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退路径中支持非默认的DisplayGamma设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

nDisplay插件是一个**成熟且活跃维护**的核心商业与行业应用插件。
- **创建时间**：创建于2018年（UE 4.20时代），历史较长。
- **近期更新频率**：非常活跃。最近一周内有多次更新，集中在电影管线集成、着色器修复和功能优化上，表明其仍在积极开发。
- **活跃度**：作为Unreal Engine在虚拟制片和广播领域的支柱功能，Epic Games持续投入资源进行维护和升级。
- **已知限制**：作为默认禁用(`EnabledByDefault=false`)的插件，它专用于特定行业场景，配置复杂，不适合一般游戏项目。
- **推荐使用**：**强烈推荐**用于虚拟制片、广播、主题公园娱乐、大型仿真等需要集群渲染的领域。对于小型项目或学习，可研究其架构但无需启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/index.html)（Epic官方虚拟制片文档中的nDisplay部分）