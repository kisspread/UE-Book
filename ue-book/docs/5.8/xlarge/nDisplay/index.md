# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多机同步渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、示例场景） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于构建大规模、多屏幕、沉浸式显示环境的核心系统。它解决了使用多台独立 PC（渲染节点）来驱动一个跨越多个物理显示器（如投影仪、LED 墙）的单一、连续虚拟场景的复杂问题。通过精确的同步和通信，nDisplay 让这些 PC 协同工作，仿佛是一个拥有强大分布式渲染能力的单一工作站，确保所有屏幕上的画面在空间和时间上完美对齐。

## 使用场景

- **主题公园/大型景点**：驾驶模拟器、飞行影院、黑暗骑乘（Dark Rides）等需要环绕式屏幕的体验。
- **虚拟制片（Virtual Production）**：驱动 LED 墙（Volume）进行实时合成拍摄。
- **CAVE（沉浸式投影室）**：使用多台投影仪创建全方位的虚拟现实环境。
- **大型可视化与仿真**：汽车设计评审、建筑设计漫游、军事/航空仿真等需要超宽视野或多用户协作的场景。
- **数字艺术装置**：在博物馆或展览中创建多投影仪拼接的复杂视觉艺术作品。

## 蓝图用法

nDisplay 的核心功能通过其专门的蓝图节点提供，用于控制集群的配置、生命周期和状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Initialize nDisplay Cluster` | 根据指定的 .ndisplay 配置文件初始化并启动一个 nDisplay 集群。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster Nodes` | 获取当前集群中所有渲染节点（PC）的列表。 | `UDisplayClusterBlueprintAPI` |
| `Start Cluster` | 启动整个集群的同步渲染流程。 | `UDisplayClusterBlueprintAPI` |
| `Stop Cluster` | 停止集群的渲染和同步。 | `UDisplayClusterBlueprintAPI` |
| `Get nDisplay Configuration` | 获取当前加载的 nDisplay 集群配置对象。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

在一个 Actor 的 BeginPlay 事件中，拖入 `Initialize nDisplay Cluster` 节点。在节点的 `ConfigPath` 参数中，指定你的 `.ndisplay` 配置文件的路径。随后，可以连接一个 `Start Cluster` 节点来启动渲染。在运行时，你可以使用其他节点来查询集群状态、管理节点或与显示配置交互。

## C++ 用法

nDisplay 提供了丰富的 C++ API 用于深度集成和自定义。

### 头文件引入

```cpp
#include "DisplayClusterBlueprintAPI.h"
// 或根据具体功能引入相应模块头文件
```

### 基本用法

以下代码展示了如何以编程方式初始化并启动一个 nDisplay 集群。通常在一个游戏模式或专门的管理类中执行。

```cpp
// 假设 ConfigPath 是一个有效的 .ndisplay 配置文件路径
FString ConfigPath = TEXT("/Game/Config/MyClusterConfig.ndisplay");

// 获取 nDisplay 蓝图 API 的单例
UDisplayClusterBlueprintAPI* nDisplayAPI = UDisplayClusterBlueprintAPI::Get();

if (nDisplayAPI)
{
    // 使用配置文件初始化集群
    nDisplayAPI->InitializeCluster(ConfigPath);

    // 启动集群渲染
    nDisplayAPI->StartCluster();
}
```

### 进阶用法

对于需要更精细控制或集成其他系统（如媒体、远程控制）的场景，可以访问底层的子系统和模块。

```cpp
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"

// 获取 nDisplay 插件主接口
IDisplayCluster* nDisplayPlugin = IDisplayCluster::Get();

if (nDisplayPlugin)
{
    // 获取集群的根 Actor，可用于进一步操作场景对象
    ADisplayClusterRootActor* RootActor = nDisplayPlugin->GetRootActor();
    if (RootActor)
    {
        // 对根 Actor 进行操作，例如获取当前视图位置
        FVector ViewLocation = RootActor->GetActorLocation();
    }

    // 也可以直接访问特定模块，例如投影模块（DisplayClusterProjection）
    // 进行自定义的投影变形或几何校正
}
```

## Demo 示例

一个最小的 Actor 类，用于在游戏开始时初始化并启动一个预定义的 nDisplay 集群。

**NDisplayDemoActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "NDisplayDemoActor.generated.h"

UCLASS()
class MYPROJECT_API ANDisplayDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ANDisplayDemoActor();

protected:
    virtual void BeginPlay() override;

    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString ClusterConfigPath;
};
```

**NDisplayDemoActor.cpp**
```cpp
#include "NDisplayDemoActor.h"
#include "DisplayClusterBlueprintAPI.h"

ANDisplayDemoActor::ANDisplayDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
    ClusterConfigPath = TEXT("/Game/Config/DefaultCluster.ndisplay");
}

void ANDisplayDemoActor::BeginPlay()
{
    Super::BeginPlay();

    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API && !ClusterConfigPath.IsEmpty())
    {
        // 初始化并启动集群
        API->InitializeCluster(ClusterConfigPath);
        API->StartCluster();
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster initialized and started with config: %s"), *ClusterConfigPath);
    }
}

void ANDisplayDemoActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UDisplayClusterBlueprintAPI* API = UDisplayClusterBlueprintAPI::Get();
    if (API)
    {
        // 关闭集群
        API->StopCluster();
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster stopped."));
    }

    Super::EndPlay(EndPlayReason);
}
```

## 模块依赖

nDisplay 是一个复杂的插件，其模块依赖于 UE 的多个子系统。以下列出了一些关键的、不常见的依赖。

| 模块 | 用途 |
|---|---|
| `MediaAssets` | 用于集成媒体播放，支持从视频源或采集卡获取画面（如 `DisplayClusterMedia`, `SharedMemoryMedia`）。 |
| `D3D12RHI` | 为高性能的 GPU 内存共享（Shared Memory Media）提供底层图形 API 支持。 |
| `MPCDI` | 集成 MPCDI 标准，用于高级投影仪几何校正和颜色校准（如 `ScalableMPCDI`）。 |
| `MovieRenderPipeline` | 与电影渲染管线集成，实现 nDisplay 场景的高质量离线渲染输出（`DisplayClusterMoviePipeline`）。 |
| `RemoteControl` | 支持通过远程控制接口（如 Web API）实时调整 nDisplay 集群参数（`DisplayClusterRemoteControlInterceptor`）。 |
| `MultiUserEditing` | 支持多用户协同编辑 nDisplay 场景配置（`DisplayClusterMultiUser`）。 |

## 维护状态

nDisplay 作为 Epic Games 官方支持的大型企业级功能，保持着非常活跃的开发与维护。

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染管线添加了 EXR 多层输出支持，提升了后期合成的灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 优化了电影渲染管线中的变形混合模式，简化了配置。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多根图中的拓扑感知相机命名问题以及MPCDI/ICVFX着色器中的不透明度alpha问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码回退时未能尊重非默认显示伽马值的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当GUI纹理尺寸小于视口尺寸时发生的闪烁问题。 |

### 维护评价

**活跃维护**。nDisplay 创建于 2018 年（约 8 年前），属于成熟的大型插件。从近期提交记录看，它仍在被 Epic Games 团队积极开发，持续引入新功能（如与新的 MovieGraph 管线集成）、修复 bug 并优化性能。尽管默认未启用（`EnabledByDefault: false`），但它是虚拟制片和大型沉浸式项目中的关键生产工具，推荐在相应的专业场景中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/nDisplay)