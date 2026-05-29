# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、编辑器工具、着色器、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于实现**分布式集群渲染**的核心插件。它解决的核心问题是：如何让一台运行 UE 的“主控机”协调多台“渲染节点机”（PC），使它们各自渲染场景的某一部分（如不同视角、不同投影区域），最终在物理上拼接成一个无缝的巨型画面（如LED墙、多投影仪系统、穹幕影院）。这对于虚拟制片（VP）、主题公园体验、大型沉浸式展览、飞行模拟器等需要超大视场角或复杂多屏同步的应用至关重要。

插件通过管理每个显示设备的投影几何（Warp/Blend）、同步渲染状态、协调输入和帧同步来实现这一目标。它内置了对 MPCDI（多投影仪校准数据接口）标准的支持（通过 `ScalableMPCDI` 第三方库），用于加载标准的投影校准文件。

## 使用场景

-   **虚拟制片 (Virtual Production)**：驱动大型LED墙，主摄像机视图同步渲染到整面墙的多个显示区域。
-   **主题公园/沉浸式体验**：为穹幕、CAVE系统或环绕式屏幕集群提供同步渲染。
-   **专业仿真**：在飞行/驾驶模拟器中，为多个环绕显示器提供视角正确、同步的画面。
-   **大型活动/展览**：控制由多台投影仪拼接而成的复杂形状投影面（如柱幕、球幕）。
-   **多GPU渲染**：在单台机器上利用多个GPU分别渲染不同显示区域，以提升性能。

## 蓝图用法

nDisplay 主要通过其配置资产和运行时模块工作，直接暴露给蓝图的高层节点相对较少。它更侧重于在编辑器内配置以及通过 C++ API 进行高级控制。在运行时，蓝图主要用于监听 nDisplay 事件（如集群节点连接状态变化）或进行一些简单的查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get nDisplay Cluster` | 获取当前运行的 nDisplay 集群实例。 | `UDisplayClusterManager` |
| `Get Cluster Node ID` | 获取当前集群节点的唯一标识符。 | `UDisplayClusterManager` |
| `Is Primary` | 判断当前节点是否为主控节点。 | `UDisplayClusterManager` |
| `On Cluster Event` | 接收集群内部事件的委托（如节点加入、离开）。 | `UDisplayClusterClusterEvent` |

## C++ 用法

nDisplay 的 C++ API 主要用于与集群渲染管线深度集成，例如自定义输入处理、实现新的投影策略或扩展媒体功能。

### 头文件引入

```cpp
#include “DisplayCluster/Public/IDisplayCluster.h”
#include “DisplayClusterConfiguration/Public/DisplayClusterConfigurationTypes.h”
```

### 基本用法

获取 nDisplay 模块接口并查询集群状态。

```cpp
// 来源：假想的集群状态查询示例
#include “DisplayCluster/Public/IDisplayCluster.h”

void MyClass::CheckClusterStatus()
{
    // 获取 nDisplay 模块接口
    IDisplayCluster* DisplayClusterModule = FModuleManager::GetModulePtr<IDisplayCluster>(“DisplayCluster”);

    if (DisplayClusterModule)
    {
        // 检查集群是否正在运行
        bool bIsClusterRunning = DisplayClusterModule->IsRunning();

        // 获取当前节点 ID
        FString CurrentNodeId = DisplayClusterModule->GetNodeId();

        // 判断是否是主节点
        bool bIsPrimary = DisplayClusterModule->IsPrimary();

        UE_LOG(LogTemp, Log, TEXT(“Cluster Running: %s, Node: %s, IsPrimary: %s“),
            bIsClusterRunning ? TEXT(“Yes“) : TEXT(“No“),
            *CurrentNodeId,
            bIsPrimary ? TEXT(“Yes“) : TEXT(“No“));
    }
}
```

### 进阶用法

监听 nDisplay 的集群事件，以响应节点动态加入或离开。

```cpp
// 来源：假想的集群事件监听示例
#include “DisplayCluster/Public/IDisplayCluster.h”
#include “DisplayCluster/Public/Cluster/IDisplayClusterClusterManager.h”

void MyClass::SubscribeToClusterEvents()
{
    IDisplayCluster* DisplayClusterModule = FModuleManager::GetModulePtr<IDisplayCluster>(“DisplayCluster”);
    if (DisplayClusterModule)
    {
        IDisplayClusterClusterManager* ClusterMgr = DisplayClusterModule->GetClusterMgr();
        if (ClusterMgr)
        {
            // 使用 Lambda 绑定集群事件
            ClusterMgr->OnClusterEvent().AddLambda([](const FDisplayClusterClusterEvent& Event)
            {
                if (Event.Category == “node_joined“)
                {
                    UE_LOG(LogTemp, Warning, TEXT(“New node joined the cluster: %s“), *Event.Name);
                    // 执行自定义逻辑，例如同步资产
                }
            });
        }
    }
}
```

## Demo 示例

一个最小的 C++ 示例，展示如何初始化并查询 nDisplay 集群的基本信息。

**DisplayClusterDemo.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “GameFramework/Actor.h”
#include “DisplayClusterDemo.generated.h”

UCLASS()
class YOURPROJECT_API ADisplayClusterDemo : public AActor
{
    GENERATED_BODY()

public:
    ADisplayClusterDemo();

protected:
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaTime) override;

private:
    void LogClusterStatus();
    bool bStatusLogged;
};
```

**DisplayClusterDemo.cpp**
```cpp
#include “DisplayClusterDemo.h”
#include “DisplayCluster/Public/IDisplayCluster.h”

ADisplayClusterDemo::ADisplayClusterDemo()
{
    PrimaryActorTick.bCanEverTick = true;
    bStatusLogged = false;
}

void ADisplayClusterDemo::BeginPlay()
{
    Super::BeginPlay();
}

void ADisplayClusterDemo::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);

    // 仅在游戏开始后记录一次状态
    if (!bStatusLogged)
    {
        LogClusterStatus();
        bStatusLogged = true;
    }
}

void ADisplayClusterDemo::LogClusterStatus()
{
    // 尝试获取 nDisplay 模块接口
    IDisplayCluster* DisplayClusterModule = FModuleManager::GetModulePtr<IDisplayCluster>(“DisplayCluster”);

    if (DisplayClusterModule && DisplayClusterModule->IsRunning())
    {
        UE_LOG(LogTemp, Log, TEXT(“[nDisplay Demo] Cluster is active!“));
        UE_LOG(LogTemp, Log, TEXT(“[nDisplay Demo] Current Node ID: %s“), *DisplayClusterModule->GetNodeId());
        UE_LOG(LogTemp, Log, TEXT(“[nDisplay Demo] Is Primary Node: %s“), DisplayClusterModule->IsPrimary() ? TEXT(“Yes“) : TEXT(“No“));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT(“[nDisplay Demo] nDisplay plugin is not loaded or cluster is not running.“));
    }
}
```

## 模块依赖

使用 nDisplay 插件时，你的项目模块（`.Build.cs` 文件）通常需要依赖 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块以访问核心功能。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时模块，包含集群管理、节点通信等核心逻辑。 |
| `DisplayClusterConfiguration` | 处理 nDisplay 配置资产（`.ndisplay` 文件）的序列化和数据结构。 |
| `DisplayClusterProjection` | 提供各种投影策略（如 MPCDI、几何体投影）的实现。 |
| `DisplayClusterWarp` | 处理几何扭曲（Warping）和边缘融合（Blending）计算。 |
| `ScalableMPCDI` | 第三方 MPCDI 标准库，用于读取标准的投影校准文件。 |

**注意**：对于大多数应用场景，依赖 `DisplayCluster` 和 `DisplayClusterConfiguration` 通常就足够了。其他模块（如 `DisplayClusterMedia`， `DisplayClusterShaders`）是为特定高级功能（自定义媒体源、着色器扩展）服务的，按需引入。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加 EXR 多层支持，提升渲染输出灵活性。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 简化 MoviePipeline 中 nDisplay 的混合模式，将 WarpBlendAlpha 合并入 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MovieRenderGraph 中拓扑感知相机命名问题，并修复 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 使输出帧编码回退路径能正确处理非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时可能出现的闪烁问题。 |

### 维护评价

-   **活跃维护**：从 Git 历史看，nDisplay 在最近几个月内持续收到功能更新和错误修复，特别是与新的 MovieRenderGraph、ICVFX 和着色器相关的改进，表明 Epic 团队仍在积极开发和维护此插件。
-   **核心功能**：作为虚拟制片和大型沉浸式显示的关键基础设施，nDisplay 是 Epic Games 重点投资的领域。
-   **复杂度高**：该插件规模庞大，包含近30个模块，涉及集群网络、投影几何、媒体流、编辑器工具等多个复杂子系统。
-   **推荐使用**：对于任何需要使用多机同步渲染或多投影仪系统的 UE 项目，nDisplay 是官方推荐且功能完善的解决方案。尽管默认未启用且学习曲线较陡，但其稳定性和功能完备性很高。
-   **注意**：由于插件复杂且默认禁用，启用前需仔细阅读官方文档，并确保硬件和网络环境满足集群渲染要求。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-unreal-engine/) (UE5.8)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)