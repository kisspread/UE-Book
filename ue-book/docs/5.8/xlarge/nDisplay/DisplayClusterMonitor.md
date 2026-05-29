# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质、着色器、测试资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的专业级集群渲染解决方案，用于驱动大规模、高分辨率的显示系统，如 LED 墙、穹幕投影、CAVE 系统和大型媒体外墙。它解决的核心问题是：**如何让多台计算机协同工作，将一个虚拟场景同步渲染到多个物理显示器上，最终呈现一个无缝、同步的宏大画面。**

其存在价值在于：
1.  **突破单机性能极限**：通过将渲染负载分配到多台计算机上，实现单机无法达到的超高分辨率和帧率。
2.  **几何变形与色彩校准**：支持对每个显示面（如弯曲的 LED 面板）进行精确的几何校正（Warp & Blend）和色彩一致性校准。
3.  **专业影视制作**：支持 ICVFX（即时视觉特效）拍摄，通过 LED 墙实现实时背景渲染，与摄像机运动同步，是虚拟制片的核心技术。
4.  **集中管理与控制**：提供统一的配置、监控和控制界面，简化复杂的多机系统的运维。

## 使用场景

-   **虚拟制片 (Virtual Production)**：使用大型 LED 墙替代绿幕，实时渲染并显示与摄像机运动同步的逼真背景，演员可在 LED 墙前表演。
-   **主题公园与博物馆**：驱动穹幕、环幕或大型互动装置，提供沉浸式体验。
-   **高性能可视化**：在汽车、建筑、工程领域进行大规模 CAD 模型的协同评审。
-   **直播与活动**：为大型现场活动（如演唱会、体育赛事）提供实时渲染的巨幅 LED 视觉效果。
-   **沉浸式娱乐**：构建多通道 CAVE 系统，用于科研模拟或高端娱乐体验。

## 蓝图用法

nDisplay 的核心功能通常通过配置资产和 C++ API 驱动，直接暴露给蓝图的接口较少，主要集中在运行时控制和查询上。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get All nDisplay Clusters` | 获取当前场景中所有 nDisplay 集群配置 | `UDisplayClusterBlueprintAPI` |
| `Get nDisplay Cluster by ID` | 根据 ID 获取特定的 nDisplay 集群配置 | `UDisplayClusterBlueprintAPI` |
| `Start nDisplay Cluster` | 启动指定的 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |
| `Stop nDisplay Cluster` | 停止指定的 nDisplay 集群 | `UDisplayClusterBlueprintAPI` |

### 使用示例（蓝图描述）

1.  在 `BeginPlay` 事件中，调用 `Get All nDisplay Clusters` 获取集群列表。
2.  通过 `Get nDisplay Cluster by ID` 或遍历列表找到目标集群（例如，根据集群名称）。
3.  调用 `Start nDisplay Cluster` 并传入集群引用，启动渲染。
4.  在 `EndPlay` 中调用 `Stop nDisplay Cluster` 进行清理。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterBlueprintAPI.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
```

### 基本用法

以下示例展示了如何通过 C++ 启动和管理一个 nDisplay 集群。

**来源文件**：`Engine/Plugins/Runtime/nDisplay/Source/DisplayCluster/Classes/DisplayClusterBlueprintAPI.h`
```cpp
// 获取全局 nDisplay API 单例
UDisplayClusterBlueprintAPI* nDisplayAPI = UDisplayClusterBlueprintAPI::Get();

if (nDisplayAPI)
{
    // 获取场景中所有的 nDisplay 集群配置
    TArray<UDisplayClusterConfigurationData*> AllClusters = nDisplayAPI->GetAllConfigurations();

    // 启动第一个找到的集群
    if (AllClusters.Num() > 0)
    {
        UDisplayClusterConfigurationData* ClusterConfig = AllClusters[0];
        nDisplayAPI->StartCluster(ClusterConfig);
    }
}
```

### 进阶用法

一个更完整的例子，展示了如何监听集群状态并处理错误。

**来源文件**：`Engine/Plugins/Runtime/nDisplay/Source/DisplayCluster/Private/DisplayClusterRootActor.cpp` (结合事件处理逻辑)
```cpp
// 监听集群启动/停止事件
class FMyClusterListener
{
public:
    FMyClusterListener()
    {
        // 绑定事件
        if (UWorld* World = GetWorld())
        {
            if (ADisplayClusterRootActor* RootActor = ADisplayClusterRootActor::GetRootActor(World))
            {
                RootActor->OnDisplayClusterStart.AddRaw(this, &FMyClusterListener::HandleClusterStart);
                RootActor->OnDisplayClusterStop.AddRaw(this, &FMyClusterListener::HandleClusterStop);
                RootActor->OnDisplayClusterError.AddRaw(this, &FMyClusterListener::HandleClusterError);
            }
        }
    }

private:
    void HandleClusterStart()
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster has started successfully."));
    }

    void HandleClusterStop()
    {
        UE_LOG(LogTemp, Log, TEXT("nDisplay cluster has been stopped."));
    }

    void HandleClusterError(const FString& ErrorMessage)
    {
        UE_LOG(LogTemp, Error, TEXT("nDisplay cluster error: %s"), *ErrorMessage);
    }
};
```

## Demo 示例

一个最小的可运行示例，用于启动一个简单的单节点 nDisplay 集群。

**前提**：在编辑器中已经创建并配置好一个 `ADisplayClusterRootActor`。

```cpp
// MyClusterManager.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyClusterManager.generated.h"

class ADisplayClusterRootActor;

UCLASS()
class AMyClusterManager : public AActor
{
    GENERATED_BODY()

public:
    AMyClusterManager();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    UPROPERTY(EditInstanceOnly, Category = "nDisplay")
    TSoftObjectPtr<ADisplayClusterRootActor> ClusterRootActor;

    void StartCluster();
    void StopCluster();
};
```

```cpp
// MyClusterManager.cpp
#include "MyClusterManager.h"
#include "DisplayClusterRootActor.h"

AMyClusterManager::AMyClusterManager()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyClusterManager::BeginPlay()
{
    Super::BeginPlay();
    StartCluster();
}

void AMyClusterManager::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    StopCluster();
    Super::EndPlay(EndPlayReason);
}

void AMyClusterManager::StartCluster()
{
    ADisplayClusterRootActor* RootActor = ClusterRootActor.Get();
    if (RootActor)
    {
        RootActor->StartCluster();
    }
}

void AMyClusterManager::StopCluster()
{
    ADisplayClusterRootActor* RootActor = ClusterRootActor.Get();
    if (RootActor)
    {
        RootActor->StopCluster();
    }
}
```

## 模块依赖

`DisplayClusterMonitor` 模块依赖于以下非标准模块：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成，用于获取场景中的视口和资产信息 |

**注意**：`DisplayClusterMonitor` 是 nDisplay 插件中的一个子模块，负责监控集群节点的健康状态和媒体输出。要使用整个 nDisplay 功能，你的项目模块通常需要依赖 `DisplayCluster` 核心模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了多层 EXR 文件支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 将电影渲染管线中的 WarpBlendAlpha 模式合并到 WarpBlend 模式中 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知的摄像机命名问题，并修复了 MPCDI/ICVFX 着色器中的不透明 Alpha 通道问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，现在会正确应用非默认的 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题 |

### 维护评价

**维护状态：活跃维护中**

nDisplay 是 Unreal Engine 中持续活跃开发的核心模块之一，特别是在虚拟制片领域。从近期提交历史看：
- **更新频繁**：在最近一周内就有 5 次提交，修复了多个实际渲染问题。
- **功能增强**：增加了对多层 EXR 的支持，改进了电影渲染管线。
- **稳定性改进**：持续修复各类渲染瑕疵（闪烁、Alpha 通道、Gamma 校正等）。

考虑到插件的年龄（约 7 年）和其作为 Epic Games 官方重点支持的特性，其稳定性和可靠性很高。它是虚拟制片、大型活动和高端可视化项目的**强烈推荐**选择。

**注意事项**：
-   插件默认未启用 (`EnabledByDefault: false`)，需要在项目设置中手动启用。
-   涉及多机协同和硬件配置，设置和调试相对复杂，建议参考官方文档和示例项目。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/index.html)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)