# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、配置文件） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterWarp` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterTests` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于实现**大规模、高精度、多节点同步渲染**的核心插件。它解决的核心问题是：如何将一个 UE 场景的渲染输出，精确地分配到由多台 PC（节点）驱动的多个物理显示器或投影仪上，并保持所有输出在时间和空间上完全同步。

其主要应用场景是**虚拟制片（Virtual Production）** 和**沉浸式显示系统**，例如：
- **LED 墙（LED Volume）**：用于电影和电视制作的大型 LED 幕墙，需要将场景渲染到由多个面板组成的巨大屏幕上。
- **CAVE 系统**：沉浸式房间，通常由多面投影墙组成。
- **多投影仪圆顶或环幕**：用于飞行模拟、天文馆等。
- **任何需要将渲染输出分割到多个物理输出设备，并要求帧同步和几何校正的场景。**

插件通过一个主节点（Master）协调多个从节点（Slave），确保它们渲染同一帧的不同部分（视口），并处理复杂的投影几何校正（如平面、圆柱、球面投影）、色彩一致性校准以及节点间的通信同步。

## 使用场景

- **你正在搭建一个用于电影拍摄的虚拟制片 LED 摄影棚** → 使用 nDisplay 配置 LED 墙的每个面板对应的视口，并设置投影和色彩校准。
- **你需要创建一个由 6 个投影仪组成的 CAVE 沉浸式环境** → 使用 nDisplay 定义每个投影仪的几何投影关系（MPCDI 或手动校正），并同步所有节点的渲染。
- **你有一个复杂的多显示器驾驶模拟器，需要精确的几何变形和边缘融合** → 使用 nDisplay 的 Warping 和 Blending 功能。
- **你需要在多个 PC 上同步运行同一个 UE 项目以实现超高分辨率或超高帧率渲染** → 使用 nDisplay 的集群渲染功能。
- **你需要将 nDisplay 的渲染输出集成到后期制作流程中** → 使用其与 Movie Render Queue 的集成。

## 蓝图用法

nDisplay 提供了丰富的蓝图 API 用于运行时控制和查询集群状态。以下按功能分组列出核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前节点的唯一标识符（如 “node_1”）。 | `UDisplayClusterBlueprintAPI` |
| `Is Master` | 判断当前节点是否是主节点。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Nodes Count` | 获取集群中的节点总数。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport ID` | 获取当前渲染的视口 ID。 | `UDisplayClusterBlueprintAPI` |
| `Get Viewport Rect` | 获取指定视口在渲染目标上的矩形区域。 | `UDisplayClusterBlueprintAPI` |
| `Set Cluster Event Listener` | 设置一个蓝图事件监听器，用于接收集群事件（如节点连接/断开）。 | `UDisplayClusterBlueprintAPI` |
| `Send Cluster Event` | 从当前节点向集群中的其他节点广播自定义事件。 | `UDisplayClusterBlueprintAPI` |
| `Get nDisplay Configuration` | 获取当前加载的 nDisplay 配置资产。 | `UDisplayClusterBlueprintAPI` |
| `Reload Configuration` | 在运行时重新加载 nDisplay 配置文件。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **在 BeginPlay 中初始化并检查角色**：
    - 拖入 `Get Cluster Node ID` 节点，将结果打印到屏幕。
    - 拖入 `Is Master` 节点，连接一个 Branch 节点。如果为真，则执行仅主节点需要运行的逻辑（如启动游戏模式）。

2.  **处理节点间通信**：
    - 在主节点的蓝图中，使用 `Send Cluster Event` 节点，指定事件名称（如 “StartSequence”）和数据。
    - 在所有节点（包括主节点）的蓝图中，使用 `Set Cluster Event Listener` 节点注册一个自定义事件。当收到 “StartSequence” 事件时，触发本地的过场动画播放逻辑。

## C++ 用法

nDisplay 的 C++ API 主要用于深度集成、自定义渲染通道或开发编辑器工具。

### 头文件引入

```cpp
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"
```

### 基本用法

以下示例展示了如何在 C++ 中查询集群状态和发送事件。

```cpp
// 来源：基于 DisplayClusterBlueprintAPI.h 的典型用法
#include "DisplayClusterBlueprintAPI.h"

void AMyActor::CheckClusterStatus()
{
    // 获取蓝图 API 单例
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API)
    {
        // 获取当前节点 ID
        FString NodeId = API->GetClusterNodeId();
        UE_LOG(LogTemp, Log, TEXT("Current Node ID: %s"), *NodeId);

        // 判断是否是主节点
        bool bIsMaster = API->IsMaster();
        UE_LOG(LogTemp, Log, TEXT("Is Master: %s"), bIsMaster ? TEXT("True") : TEXT("False"));

        // 获取集群节点数量
        int32 NodeCount = API->GetClusterNodesCount();
        UE_LOG(LogTemp, Log, TEXT("Total Cluster Nodes: %d"), NodeCount);
    }
}

void AMyActor::BroadcastCustomEvent()
{
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API)
    {
        // 创建一个自定义事件数据结构
        FDisplayClusterClusterEventJson Event;
        Event.Name = TEXT("MyCustomEvent");
        Event.Category = TEXT("Gameplay");
        Event.bIsSystemEvent = false;
        Event.Parameters.Add(TEXT("Action"), TEXT("PlayEffect"));

        // 广播事件到集群所有节点
        API->SendClusterEventJson(Event, true); // true 表示也发送给自己
    }
}
```

### 进阶用法

更高级的用法涉及直接操作 `ADisplayClusterRootActor` 和渲染子系统，通常用于开发自定义投影或后处理插件。这需要深入理解 nDisplay 的渲染管线。

## Demo 示例

一个最小的 C++ 示例，展示如何在 Actor 中集成 nDisplay API。

**MyNDisplayActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayActor.generated.h"

UCLASS()
class MYPROJECT_API AMyNDisplayActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayActor();

protected:
    virtual void BeginPlay() override;

public:
    virtual void Tick(float DeltaTime) override;

private:
    void LogClusterInfo();
};
```

**MyNDisplayActor.cpp**
```cpp
#include "MyNDisplayActor.h"
#include "DisplayClusterBlueprintAPI.h"

AMyNDisplayActor::AMyNDisplayActor()
{
    PrimaryActorTick.bCanEverTick = true;
}

void AMyNDisplayActor::BeginPlay()
{
    Super::BeginPlay();
    LogClusterInfo();
}

void AMyNDisplayActor::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
}

void AMyNDisplayActor::LogClusterInfo()
{
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API && API->IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("=== nDisplay Cluster Info ==="));
        UE_LOG(LogTemp, Warning, TEXT("Node ID: %s"), *API->GetClusterNodeId());
        UE_LOG(LogTemp, Warning, TEXT("Is Master: %s"), API->IsMaster() ? TEXT("Yes") : TEXT("No"));
        UE_LOG(LogTemp, Warning, TEXT("Total Nodes: %d"), API->GetClusterNodesCount());
        UE_LOG(LogTemp, Warning, TEXT("============================"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay API not available. Is the plugin enabled?"));
    }
}
```

**MyProject.Build.cs** (相关依赖部分)
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "InputCore",
    "DisplayCluster" // 添加 nDisplay 核心模块依赖
});
```

## 模块依赖

要使用 nDisplay 的核心功能，你的项目模块通常需要依赖以下模块。已省略常见的 Core/Engine/Slate 等依赖。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时逻辑，集群同步、渲染协调。 |
| `DisplayClusterConfiguration` | 解析和管理 `.ndisplay` 配置文件。 |
| `DisplayClusterProjection` | 处理各种投影模式（平面、MPCDI、Mesh 等）。 |
| `DisplayClusterShaders` | nDisplay 专用的着色器和渲染通道。 |
| `DisplayClusterWarp` | 几何变形（Warping）和边缘融合（Blending）功能。 |
| `DisplayClusterColorGrading` | 集群范围内的色彩分级和校准。 |
| `DisplayClusterMedia` | 与媒体框架集成，用于视频输入/输出。 |
| `DisplayClusterReplication` | 处理集群节点间的状态复制。 |
| `DisplayClusterOperator` | 运行时操作员 UI 控制台。 |
| `DisplayClusterStageMonitoring` | 舞台监控和诊断工具。 |
| `DisplayClusterMoviePipeline` | 与 Movie Render Queue 集成，用于离线渲染。 |
| `ScalableMPCDI` | 第三方 MPCDI（多投影仪校准数据交换格式）库。 |

## 维护状态

### 近期更新

1.  **`94e8f3aaca54` (最近)**: `nDisplay: Added ability to override global upscaler settings on a per-viewport basis, and made various enhancements and fixes to the upscaler settings details customization.`
    - **解读**：增加了按视口覆盖全局上采样器（如 DLSS/FSR）设置的功能，并改进了相关 UI。这表明插件正在积极适配现代超分辨率技术，提升渲染质量和灵活性。

2.  **`67cb360f496b`**: `[nDisplay] [Virtual Production] Added global upscaler settings for Outer viewports and Inner Frustum.`
    - **解读**：为外部视口和内部视锥添加了全局上采样器设置。这是虚拟制片工作流的重要增强，允许对 LED 墙的不同区域进行独立的画质优化。

3.  **`a86e9f4e0f3f`**: `[nDisplay] [Virtual Production] DLSS plugin integration for nDisplay.`
    - **解读**：正式集成了 NVIDIA DLSS 插件。这是一个重大功能更新，直接提升了 nDisplay 在虚拟制片场景下的渲染性能和图像质量。

### 维护评价

- **活跃维护**：nDisplay 是 Epic Games 虚拟制片战略的核心组件，从近期提交可以看出，它仍在**非常活跃地开发和维护**中。更新内容聚焦于前沿技术集成（DLSS）和虚拟制片工作流优化，而非简单的 bug 修复。
- **推荐使用**：对于任何涉及多节点同步渲染、虚拟制片 LED 墙或复杂投影系统的项目，nDisplay 是**官方推荐且必不可少**的解决方案。尽管它是一个“老古董”插件（约 7 年），但其功能和集成度随着 UE 版本迭代不断增强。
- **注意事项**：该插件**默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动启用。其配置和调试相对复杂，建议结合官方文档和示例项目学习。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.7/en-US/n-display-in-unreal-engine/) (Unreal Engine 官方文档站)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)