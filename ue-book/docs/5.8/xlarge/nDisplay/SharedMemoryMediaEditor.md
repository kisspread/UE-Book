# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 虚拟制片集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 中用于实现**同步集群渲染**的核心插件。它解决了使用多台 PC（节点）协同工作，共同渲染一个超高分辨率或分布式场景的复杂问题。

其主要用途是驱动**虚拟制片（Virtual Production）** 中的 **LED 墙（LED Volume）**、**多通道投影系统**、**CAVE 洞穴式沉浸环境**、**主题公园**或**科研可视化**等需要超出单台 PC 渲染能力的、由多个显示单元（如投影仪、LED 面板）组成的复杂显示阵列。

nDisplay 确保所有渲染节点（Node）的视图在几何校正（Warping）、颜色分级（Color Grading）、时间同步和立体视觉（Stereo）等方面精确对齐，从而为观众呈现一个无缝、一致的合成画面。

## 使用场景

- **你正在搭建一个 LED 虚拟制片影棚** → 使用 nDisplay 将 Unreal 场景分割并同步渲染到多块 LED 屏幕上，为演员提供正确的背景透视。
- **你需要驱动一个由多个投影仪组成的环幕或球幕影院** → 使用 nDisplay 处理投影融合（Blending）和几何校正（Warping），将一个画面无缝投射到复杂曲面上。
- **你的项目需要多台 PC 协同渲染同一场景，以提升单帧分辨率或帧率** → 使用 nDisplay 配置主从（Master/Slave）架构，分配和同步渲染任务。
- **你正在开发赛车模拟器、飞行模拟器等需要多屏环绕视角的装备** → 使用 nDisplay 管理和同步多个视角的渲染输出。

## 蓝图用法

nDisplay 的功能主要通过其专用的编辑器和配置资产进行管理，但也暴露了关键的运行时蓝图接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Cluster` | 创建一个用于集群通信的 `UDisplayClusterCluster` 对象。 | `UDisplayClusterBlueprintAPI` |
| `Create Node` | 创建一个代表集群中单个 PC 的 `UDisplayClusterNode` 对象。 | `UDisplayClusterBlueprintAPI` |
| `Get Cluster` | 获取当前游戏实例所绑定的集群对象。 | `UDisplayClusterBlueprintAPI` |
| `Get Node` | 获取当前游戏实例对应的节点对象。 | `UDisplayClusterBlueprintAPI` |
| `Get Configuration` | 获取当前加载的 nDisplay 配置资产。 | `UDisplayClusterBlueprintAPI` |
| `Start Cluster` | 启动当前节点的集群网络通信。 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  **初始化集群（通常在 GameMode 或 PlayerController 的 BeginPlay 中）**：
    *   从 `Get Cluster` 节点获取当前集群对象。
    *   检查其 `Is Cluster` 属性是否为 `True`（表示是主控节点）。
    *   如果是主控节点，调用 `Start Cluster` 节点来启动整个集群的通信。

2.  **查询节点信息**：
    *   使用 `Get Node` 节点获取代表当前 PC 的节点对象。
    *   从该对象读取 `Node ID`、`Host` (IP)、`Is Primary` (是否为渲染主节点) 等信息，可用于逻辑分支（如仅在主节点上生成 UI）。

## C++ 用法

nDisplay 的核心 C++ API 用于底层控制和深度集成。

### 头文件引入

```cpp
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterCluster.h"
#include "DisplayClusterNode.h"
```

### 基本用法

（基于公共 API 和常见模式推断）
```cpp
// 获取蓝图API单例
UDisplayClusterBlueprintAPI* DisplayAPI = UDisplayClusterBlueprintAPI::Get();

// 获取当前集群
UDisplayClusterCluster* Cluster = DisplayAPI->GetCluster();
if (Cluster && Cluster->IsCluster())
{
    // 这是主控节点 (Master) 的逻辑
    UE_LOG(LogTemp, Log, TEXT("This is the Master Node. Starting cluster..."));
    DisplayAPI->StartCluster();
}

// 获取当前节点信息
UDisplayClusterNode* CurrentNode = DisplayAPI->GetNode();
if (CurrentNode)
{
    FString NodeID = CurrentNode->GetNodeId();
    UE_LOG(LogTemp, Log, TEXT("Current Node ID: %s"), *NodeID);
}
```

## Demo 示例

一个最小的 nDisplay 集群初始化示例，展示如何在主控节点上启动集群并获取节点信息。

```cpp
// MyClusterManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyClusterManager.generated.h"

class UDisplayClusterBlueprintAPI;

UCLASS()
class MYPROJECT_API AMyClusterManager : public AActor
{
    GENERATED_BODY()

public:
    AMyClusterManager();

protected:
    virtual void BeginPlay() override;

private:
    /** 引用nDisplay蓝图API */
    UPROPERTY()
    UDisplayClusterBlueprintAPI* DisplayAPI;

    /** 日志前缀 */
    const FString LogPrefix = TEXT("[MyClusterMgr] ");
};
```

```cpp
// MyClusterManager.cpp
#include "MyClusterManager.h"
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterCluster.h"
#include "DisplayClusterNode.h"

AMyClusterManager::AMyClusterManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyClusterManager::BeginPlay()
{
    Super::BeginPlay();

    // 1. 获取 nDisplay 蓝图 API
    DisplayAPI = UDisplayClusterBlueprintAPI::Get();
    if (!DisplayAPI)
    {
        UE_LOG(LogTemp, Error, *FString(LogPrefix + TEXT("Failed to get DisplayCluster Blueprint API.")));
        return;
    }

    // 2. 获取当前节点信息
    UDisplayClusterNode* CurrentNode = DisplayAPI->GetNode();
    if (CurrentNode)
    {
        UE_LOG(LogTemp, Log, *FString(LogPrefix + TEXT("Initialized on Node: %s (ID: %s)"),
            *CurrentNode->GetHost(), *CurrentNode->GetNodeId()));
    }

    // 3. 如果是集群主控节点，则启动集群
    UDisplayClusterCluster* Cluster = DisplayAPI->GetCluster();
    if (Cluster && Cluster->IsCluster())
    {
        UE_LOG(LogTemp, Log, *FString(LogPrefix + TEXT("This is the MASTER node. Starting cluster communication...")));
        DisplayAPI->StartCluster();
    }
    else
    {
        UE_LOG(LogTemp, Log, *FString(LogPrefix + TEXT("This is a SLAVE node. Waiting for master connection.")));
    }
}
```

## 模块依赖

使用 nDisplay 插件时，你的项目模块通常需要依赖其核心模块。

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，提供集群管理、节点通信等基础功能。 |
| `DisplayClusterConfiguration` | 用于加载和解析 `.ndisplay` 配置资产。 |
| `MediaFrameworkUtilities` | 媒体框架工具，nDisplay 的媒体传输功能依赖此模块。 |
| `MPCDI` | 支持 MPCDI（Media Player Cluster Display Interchange）格式，用于投影校正数据。 |
| `D3D12RHI` | 高性能 DirectX 12 渲染硬件接口，常用于 GPU 间共享内存等高级渲染特性。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加了 EXR 多图层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在电影渲染管线中将“扭曲混合Alpha”模式合并到标准“扭曲混合”模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了多渲染图生成器中的相机命名问题，以及 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退路径中，现在能正确遵循非默认的显示 Gamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时可能发生的闪烁问题。 |

### 维护评价

- **活跃维护**：从提交记录看，nDisplay 仍处于**非常活跃**的维护和开发状态。最近的提交（2026年5月）均涉及新功能（EXR 多层支持）和重要的 Bug 修复，表明 Epic Games 对该插件持续投入。
- **核心地位**：作为 Unreal Engine 虚拟制片和专业可视化领域的**基石性插件**，它被广泛用于影视、主题公园、汽车设计和模拟等行业，有长期支持的需求。
- **模块庞大**：插件包含近30个子模块，功能极其丰富，这也意味着其复杂度和学习曲线较高。
- **推荐使用**：对于任何需要集群渲染、LED 墙或多屏同步的**专业级项目**，nDisplay 是官方推荐且必不可少的选择。尽管它“默认未启用”，但在目标平台上必须手动启用。不推荐用于简单的分屏或局域网多人游戏，这些场景有更简单的方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)