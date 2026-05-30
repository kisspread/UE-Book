# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多屏渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、媒体资产、材质等） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterMedia` (Runtime) 等共 28 个 |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个用于构建复杂、高性能多显示设备（Multi-Display）渲染系统的核心插件。它解决了在多台 PC 和多个显示器/投影仪之间同步渲染视图、实现色彩管理、进行投影几何校正（Warp/Blend）等技术难题。

其核心价值在于：
1.  **集群渲染**：将一个 Unreal 场景分发到多台联网 PC 上进行并行渲染，每台 PC 负责场景的一部分或一个特定视角，最终拼接成一个大的、连贯的画面。
2.  **精确同步**：通过网络协议和硬件信号（如 Genlock）确保所有渲染节点的帧率、时间码和场景状态严格同步，避免画面撕裂或延迟。
3.  **投影与色彩校正**：支持复杂的投影映射（MPCDI）、网格变形（Warping）、边缘融合（Blending）和色彩校准，适用于各种异形屏幕、曲面屏和投影仪阵列。
4.  **虚拟制片与沉浸式体验**：是驱动 LED 虚拟摄影棚（如 Stagecraft）、穹顶影院、飞行模拟器、CAVE 系统和大型沉浸式展厅的关键技术。

## 使用场景

- **虚拟制片 (Virtual Production)**：驱动摄影棚中的大型 LED 墙幕，实时渲染并同步背景，替代传统绿幕。
- **主题公园与飞行影院**：为球幕或多面体投影提供高分辨率、无延迟的同步渲染内容。
- **CAVE 系统 (Cave Automatic Virtual Environment)**：构建四面、六面甚至更多面的沉浸式投影空间，用于科学可视化或训练模拟。
- **汽车设计与展示**：在超宽曲面屏或环幕上展示车辆模型，提供沉浸式评审环境。
- **现场活动与舞台演出**：为大型现场活动（如演唱会、发布会）提供超高清、超大分辨率的实时视觉内容。

## 蓝图用法

由于 nDisplay 主要是一个底层集群渲染框架，其核心功能通常通过 **配置文件** (`*.ndisplay`) 在编辑器中设置，或通过 C++ 代码进行控制。运行时蓝图接口相对较少，主要集中在状态查询和事件监听上。

**注意**：以下节点仅为示例，实际可用节点请以引擎版本为准。nDisplay 的强大功能主要通过其 **nDisplay 配置资产** 在编辑器中进行可视化配置来实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node` | 获取当前运行的集群节点信息 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport` | 获取 nDisplay 视口实例 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **查询当前节点状态**：在蓝图中，可以通过 `Get Cluster Node` 节点获取当前节点是主节点（Master）还是从节点（Slave），并据此执行不同的逻辑（例如，只在主节点上触发游戏开始逻辑）。
2.  **监听渲染事件**：虽然不常见，但可以通过蓝图接口订阅集群的初始化和关闭事件，用于同步外部硬件设备。

## C++ 用法

nDisplay 的深度集成和自定义扩展主要通过 C++ 完成。

### 头文件引入

```cpp
// 核心集群功能
#include "DisplayCluster.h"
// 配置模型
#include "DisplayClusterConfigurationTypes.h"
// 媒体集成
#include "DisplayClusterMediaHelpers.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码访问 nDisplay 的集群和视口系统。
（注：此为通用示例，实际运行时需要 nDisplay 插件已启用并配置了 `.ndisplay` 文件）

```cpp
// 来源: 基于通用 nDisplay API 设计模式
#include "DisplayCluster.h"
#include "IDisplayCluster.h"

void MyActor::BeginPlay()
{
    Super::BeginPlay();

    // 获取 nDisplay 模块的单例
    IDisplayCluster& DisplayClusterModule = IDisplayCluster::Get();

    if (DisplayClusterModule.IsModuleLoaded())
    {
        // 获取集群的当前节点信息
        const IDisplayClusterClusterManager* ClusterMgr = DisplayClusterModule.GetClusterMgr();
        if (ClusterMgr)
        {
            const FString& NodeId = ClusterMgr->GetNodeId();
            const bool bIsPrimary = ClusterMgr->IsPrimary();
            UE_LOG(LogTemp, Log, TEXT("Running on Node: %s, IsPrimary: %s"), *NodeId, bIsPrimary ? TEXT("True") : TEXT("False"));
        }

        // 获取主视口的引用
        const IDisplayClusterViewportManager* ViewportMgr = DisplayClusterModule.GetViewportMgr();
        if (ViewportMgr)
        {
            // 可以在此处与视口进行交互，例如获取其渲染目标等
        }
    }
}
```

### 进阶用法

进阶用法通常涉及实现自定义的投影策略、色彩管理模块或网络插件。

1.  **自定义投影策略**：继承 `UDisplayClusterRender_MPCDI` 或类似基类，重写 `SetupProjection` 等方法，实现独特的几何校正算法。
2.  **集成自定义硬件**：通过 nDisplay 的 `Interception` 机制（如 `DisplayClusterRemoteControlInterceptor`），可以拦截并转发自定义的网络消息，用于同步外部设备（如灯光控制台、追踪系统）。
3.  **媒体输出定制**：利用 `DisplayClusterMedia` 和 `SharedMemoryMedia` 模块，将渲染结果高效地输出到共享内存或特定硬件接口，供其他软件（如广播系统）消费。

## Demo 示例

以下是一个极简的 C++ 示例，演示如何创建一个 nDisplay 感知的 Actor，并在游戏开始时打印集群信息。
（注：此代码假设 nDisplay 插件已正确配置并启用，且项目已设置好 `.ndisplay` 配置文件）

**MyNDisplayAwareActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayAwareActor.generated.h"

UCLASS()
class AMyNDisplayAwareActor : public AActor
{
	GENERATED_BODY()
	
public:	
	AMyNDisplayAwareActor();

protected:
	virtual void BeginPlay() override;

public:	
	virtual void Tick(float DeltaTime) override;
};
```

**MyNDisplayAwareActor.cpp**
```cpp
#include "MyNDisplayAwareActor.h"
#include "DisplayCluster.h" // 引入 nDisplay 核心头文件
#include "IDisplayCluster.h"

AMyNDisplayAwareActor::AMyNDisplayAwareActor()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AMyNDisplayAwareActor::BeginPlay()
{
	Super::BeginPlay();

	// 检查并获取 nDisplay 模块接口
	if (IDisplayCluster::IsAvailable())
	{
		IDisplayCluster& DCModule = IDisplayCluster::Get();
		const IDisplayClusterClusterManager* ClusterMgr = DCModule.GetClusterMgr();

		if (ClusterMgr)
		{
			const FString NodeId = ClusterMgr->GetNodeId();
			const bool bPrimary = ClusterMgr->IsPrimary();
			UE_LOG(LogTemp, Warning, TEXT("nDisplay Actor Initialized! Node: [%s], Primary: [%s]"), 
				*NodeId, 
				bPrimary ? TEXT("Yes") : TEXT("No"));

			// 如果是主节点，可以执行一些特定逻辑
			if (bPrimary)
			{
				UE_LOG(LogTemp, Warning, TEXT("This is the primary node. Cluster is active."));
			}
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("nDisplay Cluster Manager not available."));
		}
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("nDisplay module is not loaded."));
	}
}

void AMyNDisplayAwareActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
}
```

## 模块依赖

使用 nDisplay 插件的项目通常需要依赖以下核心模块。以下列出了该插件 **独特** 的、不常见的依赖。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，包含集群管理、视口管理等基础功能。 |
| `DisplayClusterProjection` | 处理投影几何校正（Warp/Blend）、MPCDI 支持。 |
| `DisplayClusterMedia` | 处理媒体输入/输出集成，如与摄像机输入、广播输出对接。 |
| `SharedMemoryMedia` | 实现基于共享内存的高性能媒体传输，用于节点间数据交换。 |
| `DisplayClusterShaders` | 提供 nDisplay 专用的渲染着色器，用于色彩校正、变形等效果。 |
| `DisplayClusterWarp` | 提供网格变形（Warp）和混合（Blend）的算法实现。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 nDisplay 的 MovieGraph 渲染管线增加了 EXR 多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了电影渲染管线中的 WarpBlendAlpha 模式到主 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多资源生成器中拓扑感知相机命名问题，并修正了 MPCDI 和 ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码的后备路径中，现在能正确处理非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能导致的画面闪烁问题。 |

### 维护评价

**活跃维护，持续更新**。

-   **创建时间**：始于 2018 年，是一个成熟且功能复杂的核心插件。
-   **更新频率**：近期（2026年5月）有非常密集的更新，涉及功能增强（EXR 多图层）、渲染管线优化（合并模式）以及多个关键 Bug 修复（着色器、闪烁问题）。
-   **活跃度**：尽管不是 Epic 主力游戏开发插件，但作为企业级和虚拟制片领域的关键组件，仍在被积极开发和维护。
-   **已知问题/限制**：配置复杂，对硬件和网络环境要求高。需要深入理解渲染和集群技术。默认未启用，需手动激活。
-   **推荐使用**：**强烈推荐**给需要构建专业多显示设备系统（特别是虚拟制片、沉浸式体验）的团队。对于简单的多显示器游戏或应用，通常使用引擎自带的多视口功能即可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)（Epic 官方 nDisplay 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)（插件内置测试）