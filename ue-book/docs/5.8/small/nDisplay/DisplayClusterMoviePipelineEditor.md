# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、蓝图资产、材质模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 用于虚拟制作、投影映射和复杂可视化环境的核心插件。它解决的核心问题是：如何让一个 Unreal Engine 应用程序的内容，同步、精确地显示在由多个物理显示器、投影仪或 LED 面板组成的复杂显示阵列上。这超越了简单的多显示器扩展，实现了跨机器（集群）的帧同步和色彩一致性渲染。它使得创建沉浸式 CAVE（Cave Automatic Virtual Environment）环境、LED 墙虚拟拍摄场景以及复杂的多通道可视化系统成为可能。

## 使用场景

- **虚拟制作 (Virtual Production)**: 你需要在 LED 墙（Volume）上渲染高分辨率、高帧率的虚拟场景，用于电影或电视拍摄。nDisplay 可以管理 LED 墙的多个显示区域，并同步渲染。
- **投影映射 (Projection Mapping)**: 你需要将内容投射到复杂的非平面表面（如建筑物、雕像），并需要边缘融合和几何校正。nDisplay 与 MPCDI 协议集成，支持精确的投影仪校准。
- **沉浸式体验 (Immersive Experiences)**: 你需要构建 CAVE 环境或驾驶模拟器，让多个投影仪环绕用户，提供 180° 或 360° 的视野。
- **高分辨率显示墙 (High-Res Display Walls)**: 你需要将一个超高分辨率的视图（如 8K、16K）分布到多个 4K 显示器上，并保持同步。
- **离线渲染 (Offline Rendering)**: 你需要使用 Movie Render Queue 对 nDisplay 配置进行高质量的离线渲染，并输出 EXR 多层文件。

## 蓝图用法

nDisplay 的蓝图功能主要集中在 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块中，用于运行时控制和配置。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Configuration Data` | 获取当前活跃的 nDisplay 配置数据对象。 | `UDisplayClusterSubsystem` |
| `Get Node` | 根据名称获取配置中的集群节点（即一台 PC）信息。 | `UDisplayClusterConfigurationData` |
| `Get Viewport` | 根据名称获取配置中的视口信息，该视口对应一个物理显示输出。 | `UDisplayClusterConfigurationData` |
| `Get All Viewports` | 获取配置中所有视口的列表。 | `UDisplayClusterConfigurationData` |
| `Get Root Actor` | 获取场景中代表 nDisplay 配置根节点的 Actor。 | `ADisplayClusterRootActor` |
| `Sync Render` | 触发一帧的同步渲染（通常由系统内部调用）。 | `UDisplayClusterSubsystem` |

### 使用示例（蓝图描述）

1.  **初始化与配置加载**:
    - 在游戏开始时，使用 `Get Display Cluster Subsystem` 节点获取子系统。
    - 调用 `Load Configuration` 并传入一个 `UDisplayClusterConfigurationData` 资产，即可激活预设的显示配置。

2.  **运行时参数控制**:
    - 可以通过蓝图获取 `Root Actor`，然后使用 `Get All Viewports` 循环遍历所有视口。
    - 通过视口对象的引用来修改运行时参数，例如动态调整视口的 FOV 或后处理设置。

## C++ 用法

在 C++ 中，nDisplay 提供了一套完整的 API 用于管理配置、控制渲染流程和扩展功能。

### 头文件引入

```cpp
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterSubsystem.h"
```

### 基本用法

以下代码展示了如何在 C++ 中加载和检查一个 nDisplay 配置。

```cpp
// 来源：分析自 DisplayClusterConfiguration 模块逻辑
#include "DisplayClusterConfigurationTypes.h"
#include "Engine/World.h"
#include "Kismet/GameplayStatics.h"

void LoadAndInspectDisplayClusterConfig(UWorld* World)
{
    // 1. 获取 Display Cluster 子系统
    UDisplayClusterSubsystem* DCSubsystem = World->GetSubsystem<UDisplayClusterSubsystem>();
    if (!DCSubsystem)
    {
        UE_LOG(LogTemp, Error, TEXT("Display Cluster Subsystem not found!"));
        return;
    }

    // 2. 加载一个 nDisplay 配置资产 (假设已在编辑器中创建并引用)
    UDisplayClusterConfigurationData* ConfigData = LoadObject<UDisplayClusterConfigurationData>(nullptr, TEXT("/Game/Path/To/MyConfig"));
    if (ConfigData)
    {
        // 3. 应用配置
        DCSubsystem->LoadConfiguration(ConfigData);

        // 4. 查询配置信息
        const FDisplayClusterConfigurationCluster& ClusterConfig = ConfigData->Cluster;
        UE_LOG(LogTemp, Log, TEXT("Cluster contains %d nodes."), ClusterConfig.Nodes.Num());

        for (const auto& NodePair : ClusterConfig.Nodes)
        {
            const FDisplayClusterConfigurationClusterNode& Node = NodePair.Value;
            UE_LOG(LogTemp, Log, TEXT("Node '%s' has %d viewports."), *NodePair.Key, Node.Viewports.Num());
        }
    }
}
```

### 进阶用法

nDisplay 通常与 Unreal 的 Movie Render Queue 集成，用于离线渲染。

```cpp
// 来源：分析自 DisplayClusterMoviePipeline 模块逻辑
#include "MoviePipelineQueueSubsystem.h"
#include "DisplayClusterMoviePipelineSettings.h" // 假设的设置类

void RenderSequenceWithnDisplay(UWorld* World, ULevelSequence* Sequence)
{
    // 1. 获取 Movie Pipeline Queue 子系统
    UMoviePipelineQueueSubsystem* QueueSubsystem = World->GetSubsystem<UMoviePipelineQueueSubsystem>();
    if (QueueSubsystem)
    {
        // 2. 创建一个新的作业 (Job)
        UMoviePipelineExecutorJob* Job = QueueSubsystem->GetQueue()->AllocateNewJob();
        Job->SetSequence(Sequence);

        // 3. 为作业配置 nDisplay 特有的输出设置
        // 这通常在 Movie Pipeline 的配置对象中完成，需要引用一个 nDisplay 配置资产
        // MoviePipeline 的 Output 设置会包含针对 nDisplay 视口的 EXR 分层输出选项。
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，展示如何为一个 nDisplay 根 Actor 设置自定义数据通道，用于在不同集群节点间传递运行时数据。

```cpp
// MyDisplayClusterDataBridge.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterConfigurationTypes.h"
#include "MyDisplayClusterDataBridge.generated.h"

// 自定义数据结构，需要通过网络在节点间同步
USTRUCT(BlueprintType)
struct FMyCustomData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    float Intensity = 1.0f;

    UPROPERTY(BlueprintReadWrite)
    FLinearColor Color = FLinearColor::White;
};

// 自定义数据通道实现类
UCLASS(BlueprintType)
class UMyDisplayClusterDataBridge : public UObject
{
    GENERATED_BODY()

public:
    // 同步数据的函数，在主节点上调用
    UFUNCTION(BlueprintCallable, Category = "nDisplay|CustomData")
    void SynchronizeCustomData(const FMyCustomData& Data);

    // 接收数据的函数，在其他节点上调用
    UFUNCTION(BlueprintCallable, Category = "nDisplay|CustomData")
    FMyCustomData GetSynchronizedCustomData() const;

private:
    UPROPERTY()
    FMyCustomData CachedData;
};

// MyDisplayClusterDataBridge.cpp
#include "MyDisplayClusterDataBridge.h"
#include "DisplayClusterSubsystem.h"

void UMyDisplayClusterDataBridge::SynchronizeCustomData(const FMyCustomData& Data)
{
    CachedData = Data;
    // 这里将调用 nDisplay 的节点间通信机制（如 SharedMemory 或 TCP）将 Data 发送到其他节点
    // 具体实现依赖于 nDisplay 的底层 API，例如 IDisplayClusterClusterManager
}

FMyCustomData UMyDisplayClusterDataBridge::GetSynchronizedCustomData() const
{
    return CachedData;
}
```

## 模块依赖

nDisplay 插件包含许多模块。若要在你的项目或插件中使用 nDisplay，需要依赖相应的模块。以下是不常见的独特依赖：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时逻辑，管理集群、同步和渲染。 |
| `DisplayClusterConfiguration` | nDisplay 配置数据的资产类型和序列化。 |
| `DisplayClusterProjection` | 处理投影映射、MPCDI 校准和几何变换。 |
| `DisplayClusterWarp` | 实现投影仪边缘融合（Warp & Blend）。 |
| `DisplayClusterMedia` | 处理与外部媒体（如 SDI 卡）的输入输出。 |
| `DisplayClusterShaders` | nDisplay 特有的着色器和材质函数。 |
| `DisplayClusterMoviePipeline` | 将 nDisplay 集成到 Movie Render Queue 中进行离线渲染。 |
| `SharedMemoryMedia` | 使用共享内存在同一台机器的不同进程间高效传输视频帧。 |
| `ScalableMPCDI` | (第三方) 用于解析和操作 MPCDI 校准文件的库。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 Movie Graph 和 nDisplay 添加了 EXR 多层文件输出支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 Movie Pipeline 中的 WarpBlendAlpha 模式到标准 WarpBlend 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中拓扑感知摄像机的命名问题，并修复了 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时，尊重非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时出现的闪烁问题。 |

### 维护评价

- **活跃维护**: nDisplay 插件仍在**积极维护**中。最近的提交（截至2026年5月）表明开发团队正在持续添加新功能（如 EXR 多层支持）、修复 Bug 并优化性能。提交信息清晰，改动具有实质性意义。
- **重要性**: 作为 Unreal Engine 在虚拟制作领域的关键基础设施，nDisplay 对 Epic Games 及其合作伙伴（如拍摄现场）至关重要，因此会持续投入资源维护。
- **复杂性**: 该插件规模庞大，子模块众多，涉及渲染、网络、硬件交互等多个领域。其学习曲线较陡，文档相对缺乏，调试也较为复杂。
- **推荐**: 对于有严格同步多显示器需求的项目（如虚拟制片、主题乐园项目、高级可视化），**强烈推荐使用** nDisplay。对于简单的多窗口或多显示器游戏，通常不需要使用如此复杂的系统。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档（暂无直接链接，可在 Unreal Engine 文档站搜索 “nDisplay”）
- 测试用例（位于 `Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests/`）