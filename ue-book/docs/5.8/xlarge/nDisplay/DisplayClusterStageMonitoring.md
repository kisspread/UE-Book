# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 多机渲染 |
| 分类 | Miscellaneous |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、示例场景） |
| 模块 | `DisplayCluster` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一套完整的集群渲染解决方案，其核心是解决 **单台 PC 性能不足以驱动超大或多显示输出** 的难题。它允许多台运行 Unreal Engine 的 PC（节点）通过高速网络连接，精确同步地渲染同一场景的不同视角，并将输出组合到一个或多个物理显示器上。

该插件的存在主要用于以下高端专业场景：
- **虚拟制片 (Virtual Production)**：驱动大型 LED 墙，将 CG 环境实时渲染并投射到 LED 屏上，与演员和物理场景结合拍摄。
- **多通道投影**：创建穹顶投影、CAVE (Cave Automatic Virtual Environment) 系统、多面环绕投影等沉浸式环境。
- **高性能模拟器**：驾驶模拟器、飞行模拟器中多屏拼接的高保真视图。
- **可视化集群**：用于建筑、汽车等领域的超大分辨率静态图像或动画渲染。

它通过 **集群配置文件** 定义拓扑结构，使用 **同步策略** (如 DWM 同步、Nvidia Sync) 保证所有渲染节点帧同步，并提供 **投影混合 (Warp & Blend)** 功能来校正和无缝拼接多个投影仪的输出。

## 使用场景

- 你正在搭建一个用于电影拍摄的 **LED 墙虚拟摄影棚** → 用 nDisplay 配置墙的拓扑、投影和同步。
- 你需要为一个科学演示创建一个 **180度穹顶投影** → 用 nDisplay 管理多台投影仪的边缘融合和几何校正。
- 你在开发一个 **飞行模拟器**，需要四个屏幕构成环绕视野 → 用 nDisplay 实现多视口渲染与严格帧同步。
- 你的项目要求使用 **多台 PC 渲染同一个超大场景的不同部分** 以分担 GPU 压力 → 用 nDisplay 进行集群渲染和管理。

## 蓝图用法

nDisplay 提供了用于在运行时控制集群状态和行为的蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Cluster Node ID` | 获取当前运行实例的集群节点 ID | `UDisplayClusterConfiguration` |
| `Apply Config` | 应用一个 `.ndisplay` 配置文件到当前集群 | `UDisplayClusterConfiguration` |
| `Get Media Output` | 获取用于集群媒体输出的 `UMediaOutput` 对象 | `UDisplayClusterMediaOutput` |
| `Is Cluster Node Primary` | 判断当前节点是否是主节点（负责协调同步） | `UDisplayClusterClusterManager` |
| `Get Sync Policy` | 获取当前集群使用的同步策略 | `UDisplayClusterClusterManager` |

### 使用示例（蓝图描述）

1.  **创建根 Actor**：在场景中放置一个 `ADisplayClusterRootActor`，它是所有 nDisplay 相关功能的根。
2.  **应用配置**：通过蓝图的 `BeginPlay` 事件，调用 `Apply Config` 节点，将设计好的 `.ndisplay` 配置文件路径（如 `”/Game/Configs/MyCluster.ndisplay”`）传入，加载集群设置。
3.  **运行时控制**：可以使用 `Is Cluster Node Primary` 节点来区分主从节点，让主节点执行额外的逻辑（如 UI 控制），从节点只进行渲染。
4.  **媒体输出**：使用 `Get Media Output` 节点获取媒体输出对象，可以将其连接到 `OpenCV` 或其他媒体框架进行实时视频合成或捕捉。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfiguration.h"
#include "DisplayClusterClusterManager.h"
// 包含对应模块的头文件
```

### 基本用法

从测试用例中可以看到初始化集群和获取状态的基本模式。

```cpp
// 来源：Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/Private/DisplayClusterClusterManagerTest.cpp
// 假设我们有一个 ADisplayClusterRootActor 指针 RootActor
if (UDisplayClusterClusterManager* ClusterManager = RootActor->GetClusterManager())
{
    // 启动集群
    if (!ClusterManager->StartCluster())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to start nDisplay cluster!"));
        return;
    }

    // 检查同步状态
    if (ClusterManager->IsSynced())
    {
        UE_LOG(LogTemp, Log, TEXT("Cluster is synchronized."));
    }

    // 获取集群配置
    const UDisplayClusterConfiguration* Config = ClusterManager->GetConfiguration();
    if (Config)
    {
        const FDisplayClusterConfigurationCluster& ClusterConfig = Config->GetCluster();
        UE_LOG(LogTemp, Log, TEXT("Cluster has %d nodes."), ClusterConfig.Nodes.Num());
    }
}
```

### 进阶用法

结合同步监控模块，可以实现自定义的性能监控和诊断。

```cpp
// 来源：Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterStageMonitoring/Private/ (结合多个文件)
// 假设我们注册了同步事件监听
void AMyActor::OnSyncEventReceived(const FStageProviderEventMessage& EventMessage)
{
    // 检查是否是 DWM 同步事件
    if (const FDWMSyncEvent* DWMSyncEvent = dynamic_cast<const FDWMSyncEvent*>(&EventMessage))
    {
        if (DWMSyncEvent->MissedFrames > 0)
        {
            UE_LOG(LogTemp, Warning, TEXT("DWM Sync Missed %d frames! Last duration: %f ms"),
                DWMSyncEvent->MissedFrames,
                DWMSyncEvent->LastFrameDuration);
        }
    }
    // 检查是否是 Nvidia 同步事件
    else if (const FNvidiaSyncEvent* NvidiaSyncEvent = dynamic_cast<const FNvidiaSyncEvent*>(&EventMessage))
    {
        if (NvidiaSyncEvent->MissedFrames > 0)
        {
            UE_LOG(LogTemp, Warning, TEXT("Nvidia Sync Missed %d frames! Sync duration: %f ms"),
                NvidiaSyncEvent->MissedFrames,
                NvidiaSyncEvent->SynchronizationDuration);
        }
    }
}
```

## Demo 示例

一个最小的 C++ 示例，用于初始化一个 nDisplay 根 Actor 并应用配置。

```cpp
// MyNDisplayActor.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyNDisplayActor.generated.h"

class ADisplayClusterRootActor;

UCLASS()
class AMyNDisplayActor : public AActor
{
    GENERATED_BODY()

public:
    AMyNDisplayActor();

protected:
    virtual void BeginPlay() override;

private:
    // 指向场景中 nDisplay 根 Actor 的引用
    UPROPERTY()
    ADisplayClusterRootActor* NDisplayRoot;

    // 配置文件路径
    UPROPERTY(EditAnywhere, Category = "nDisplay")
    FString ConfigAssetPath = TEXT("/Game/Configs/DefaultCluster.ndisplay");
};
```

```cpp
// MyNDisplayActor.cpp
#include "MyNDisplayActor.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfiguration.h"
#include "DisplayClusterClusterManager.h"

AMyNDisplayActor::AMyNDisplayActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyNDisplayActor::BeginPlay()
{
    Super::BeginPlay();

    // 在场景中查找或生成 nDisplay 根 Actor
    NDisplayRoot = FindFirstObjectByClass<ADisplayClusterRootActor>();
    if (!NDisplayRoot)
    {
        UE_LOG(LogTemp, Error, TEXT("No DisplayClusterRootActor found in the world!"));
        return;
    }

    // 获取配置管理器并应用配置
    UDisplayClusterConfiguration* ConfigManager = NDisplayRoot->GetConfiguration();
    if (ConfigManager)
    {
        bool bSuccess = ConfigManager->ApplyConfiguration(ConfigAssetPath);
        if (bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("nDisplay configuration applied successfully: %s"), *ConfigAssetPath);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to apply nDisplay configuration: %s"), *ConfigAssetPath);
        }
    }

    // 启动集群
    UDisplayClusterClusterManager* ClusterManager = NDisplayRoot->GetClusterManager();
    if (ClusterManager && !ClusterManager->IsRunning())
    {
        ClusterManager->StartCluster();
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster started."));
    }
}
```

## 模块依赖

该插件依赖许多 Unreal Engine 的核心模块，同时也引入了一些独特的依赖项。

| 模块 | 用途 |
|---|---|
| `UnrealEd`, `EditorWidgets`, `LevelEditor` | 为 nDisplay 提供自定义编辑器界面和工作流集成（如配置编辑器、预览窗口）。 |
| `D3D12RHI` | 支持通过共享内存 (Shared Memory) 进行高性能的 GPU 到 GPU 传输，这是 nDisplay 集群内低延迟视频流传输的关键。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影渲染管线添加 EXR 多图层输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 简化电影管线中的 Alpha 通道合成模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复摄影机命名和 ICVFX 通道的透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复输出帧编码时的 Gamma 校正问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时导致的画面闪烁。 |

### 维护评价

- **创建时间**：约 8 年前（2018年），属于成熟的“老古董”级插件。
- **更新频率**：非常活跃。仅 2026 年 5 月就有至少 5 次重要提交，涉及功能增强（EXR 多图层）、流程优化（合并渲染模式）和 Bug 修复。
- **维护状态**：**活跃维护中**。作为 Unreal Engine 虚拟制片工作流的核心组件，Epic Games 持续投入开发资源。
- **已知限制**：主要面向 Windows (Win64) 和 Linux 平台。功能复杂，配置和调试需要一定的专业知识。
- **推荐使用**：**强烈推荐**。如果你正在开发需要超大分辨率、多屏幕拼接或分布式渲染的专业级应用（尤其是虚拟制片），nDisplay 是官方提供的成熟、功能完备的解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/n-display-in-unreal-engine/) (注：链接可能随版本变化，需在 Epic 官网查找最新文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)