# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 多屏同步显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、配置资源） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是一个高级渲染框架，其核心目标是将 Unreal Engine 的场景同步渲染到由多台 PC（节点）和多个显示设备（屏幕、投影仪）组成的物理显示集群上。它解决的不是简单的多显示器拼接，而是需要精确几何校正、像素级同步以及复杂网络架构的**沉浸式显示系统**问题。通过它，开发者可以构建 CAVE（洞穴自动虚拟环境）、LED 墙、多投影仪球幕、驾驶模拟器等需要多通道、非标准形状投影的设施。插件通过配置文件定义整个显示集群的拓扑结构（节点、视口、投影），并负责节点间的状态同步、帧同步和渲染命令分发。

## 使用场景

- **虚拟制作 (Virtual Production)**：在 LED Volume（LED 墙）拍摄中，使用 nDisplay 驱动高分辨率 LED 屏幕的实时内容渲染，并与摄像机追踪系统联动。
- **大型沉浸式体验**：在主题公园、博物馆或展览馆中，为 CAVE 环境、全景影院或交互装置提供多投影仪无缝拼接和几何校正。
- **专业模拟与仿真**：驾驶模拟器、飞行模拟器中，需要多个精确视角的屏幕或投影面来提供环绕视野。
- **建筑与设计评审**：在超宽屏或环幕上展示建筑模型，提供 1:1 沉浸式评审体验。
- **现场活动与直播**：驱动演唱会、体育赛事直播中的大型 LED 墙内容，并确保所有屏幕的同步与色彩一致。

## 蓝图用法

nDisplay 的蓝图接口主要集中在配置和控制 `ADisplayClusterRootActor`。由于其庞大和专业性，核心交互通常通过配置文件和编辑器工具完成，但运行时也有关键蓝图节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Display Cluster Root Actor` | 在指定世界中查找当前激活的 nDisplay 根 Actor。 | `ADisplayClusterRootActor` (或相关蓝图库) |
| `Get Cluster Node Id` | 获取当前运行节点的集群节点 ID (例如 “node0”, “node1”)。 | `ADisplayClusterRootActor` |
| `Is Primary Node` | 判断当前节点是否是主节点（负责某些集中计算和分发）。 | `ADisplayClusterRootActor` |
| `Render` | 触发一帧 nDisplay 集群渲染（主要用于离线渲染或脚本控制）。 | `ADisplayClusterRootActor` |

### 使用示例（蓝图描述）

1.  **在关卡中放置 nDisplay 根 Actor**：从放置面板拖入一个 `ADisplayClusterRootActor` 到场景中。这是所有 nDisplay 功能的入口。
2.  **在编辑器中配置显示拓扑**：选中该 Actor，在细节面板中通过 **nDisplay Configurator** 工具（或直接编辑 .ndisplay 配置文件）定义视图、投影和集群节点。
3.  **运行时查询节点信息**：在关卡蓝图或任何 Actor 蓝图中，使用“Get Cluster Node Id”节点来根据当前运行的物理机器执行不同的逻辑（例如，在主节点上启动 UI，在渲染节点上隐藏它）。
4.  **控制渲染**：对于需要精确控制渲染时机的场景（如离线渲染），可以使用“Render”节点手动触发渲染帧。

## C++ 用法

C++ 用法主要涉及在插件和引擎扩展中深度集成 nDisplay 的功能。

### 头文件引入

```cpp
// 核心接口
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"
#include "DisplayClusterEnums.h"
```

### 基本用法

在游戏模块中启用和检查 nDisplay 状态。

```cpp
// 来自 DisplayClusterEditor 模块的典型初始化逻辑
void FMyGameModule::StartupModule()
{
    // 检查 nDisplay 模块是否已加载并可用
    if (IDisplayCluster* DisplayCluster = IDisplayCluster::Get())
    {
        // 获取当前集群节点ID，可用于初始化特定于节点的系统
        const FString MyNodeId = DisplayCluster->GetNodeId();
        UE_LOG(LogTemp, Log, TEXT("My nDisplay Node ID: %s"), *MyNodeId);
        
        // 判断是否为编辑器内运行（PIE）模式下的 nDisplay 会话
        // 对于在编辑器和打包后行为不同的逻辑至关重要
        if (DisplayCluster->IsRunning())
        {
            // 执行集群环境下的特定初始化
        }
    }
}
```

### 进阶用法

通过 `UDisplayClusterEditorSettings` 和模块接口控制编辑器集成。

```cpp
// 来自 DisplayClusterEditorModule.cpp - 展示如何注册编辑器设置
void FDisplayClusterEditorModule::RegisterSettings()
{
    // 获取引擎设置对象
    UDisplayClusterEditorSettings* Settings = GetMutableDefault<UDisplayClusterEditorSettings>();
    
    // 监听设置变化
    Settings->OnDisplayClusterSettingsChanged.AddRaw(this, &FDisplayClusterEditorModule::OnSettingsChanged);
}

// 回调函数
void FDisplayClusterEditorModule::OnSettingsChanged()
{
    const UDisplayClusterEditorSettings* Settings = GetDefault<UDisplayClusterEditorSettings>();
    
    if (Settings->bEnabled)
    {
        // 当用户启用 nDisplay 设置时，执行必要的引擎类替换等
        // 例如，将默认的 NetDriver 替换为 DisplayClusterNetDriver
    }
}
```

## Demo 示例

以下示例展示如何在 C++ 代码中获取并使用 nDisplay 根 Actor。

**MyDisplayController.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyDisplayController.generated.h"

class ADisplayClusterRootActor;

UCLASS()
class MYPROJECT_API AMyDisplayController : public AActor
{
    GENERATED_BODY()

public:
    AMyDisplayController();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "nDisplay")
    void TriggerRender();

private:
    UPROPERTY()
    ADisplayClusterRootActor* ClusterRoot;
};
```

**MyDisplayController.cpp**
```cpp
#include "MyDisplayController.h"
#include "DisplayClusterRootActor.h"
#include "Kismet/GameplayStatics.h"

AMyDisplayController::AMyDisplayController()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyDisplayController::BeginPlay()
{
    Super::BeginPlay();
    
    // 在场景中查找第一个可用的 nDisplay 根 Actor
    TArray<AActor*> FoundActors;
    UGameplayStatics::GetAllActorsOfClass(GetWorld(), ADisplayClusterRootActor::StaticClass(), FoundActors);
    
    if (FoundActors.Num() > 0)
    {
        ClusterRoot = Cast<ADisplayClusterRootActor>(FoundActors[0]);
        UE_LOG(LogTemp, Log, TEXT("nDisplay Cluster Root found: %s"), *ClusterRoot->GetName());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("No nDisplay Cluster Root Actor found in the world."));
    }
}

void AMyDisplayController::TriggerRender()
{
    if (ClusterRoot)
    {
        // 触发一帧 nDisplay 集群渲染
        // 谨慎使用，通常由引擎自动驱动
        ClusterRoot->Render();
    }
}
```

## 模块依赖

要使用 nDisplay 功能，你的项目模块需要依赖以下核心模块（根据你使用的功能选择）：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 的核心运行时模块，包含集群管理、同步等基础功能。 |
| `DisplayClusterConfiguration` | 处理 .ndisplay 配置文件的加载、解析和管理。 |
| `DisplayClusterProjection` | 实现各种投影几何校正算法（MPCDI, Mesh, EasyBlend 等）。 |
| `DisplayClusterRender` | 负责多视口渲染、后处理和最终帧的合成与分发。 |
| `DisplayClusterReplication` | 处理集群节点间的网络通信和数据同步。 |

**注意**：`DisplayCluster` 及其众多子模块通常通过插件的形式提供，你的项目 `Build.cs` 只需确保 `"nDisplay"` 插件被正确启用。只有在编写与 nDisplay 深度集成的自定义模块时，才需要添加上述具体的模块依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 和 nDisplay 添加 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 MoviePipeline 中的 WarpBlendAlpha 模式到 WarpBlend。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知的相机命名问题及 MPCDI/ICVFX 着色器的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时遵循非默认的 DisplayGamma 设置。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复当 GUI 纹理尺寸小于视口尺寸时发生的闪烁问题。 |

### 维护评价

nDisplay 作为 Unreal Engine 中用于**虚拟制作 (Virtual Production)** 和**沉浸式体验**的关键插件，一直受到 Epic Games 的重点维护和更新。
- **活跃维护**：从近期的 Git 历史来看，该插件在最近一个月内（2026年5月）有连续的 bug 修复和功能增强（如 EXR 多层支持），表明其处于非常活跃的维护状态。
- **重要性高**：它是 Unreal Engine 在影视行业和大型线下娱乐领域应用的基石之一，功能相对复杂且专业。
- **推荐使用**：对于有虚拟制作或多屏幕渲染需求的项目，**强烈推荐使用**。其文档和工具链（如 nDisplay Configurator）也相对完善。需要注意的是，由于其系统级的复杂性，对硬件（多PC、GPU同步卡）和网络配置有较高要求，初始设置门槛较高。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档]() (待补充，通常可在 Epic Games 官方文档站找到)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)