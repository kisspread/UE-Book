# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、配置资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**集群渲染**的核心插件，它解决了在多台计算机上同步渲染同一场景并投射到复杂显示设备（如 LED 墙、穹顶、多通道 CAVE 系统）的关键问题。其核心价值在于：

1. **同步渲染**：确保多个渲染节点（PC）的帧完全同步，避免撕裂和延迟。
2. **复杂显示拓扑**：支持将单一场景分发到任意形状的物理屏幕（平面、曲面、环形等）。
3. **立体渲染**：支持为每只眼睛分别渲染，用于 VR 或立体显示。
4. **ICVFX 虚拟制片**：为 LED 虚拟制片（如使用 Unreal 的虚拟制片管线）提供核心支持，允许控制虚拟场景与物理 LED 墙的精确对齐和色彩匹配。

**本质**：nDisplay 不是一个简单的显示输出插件，而是一个**分布式渲染和合成引擎**。它将一个 UE 场景切分、投影并合成到由多个物理输出组成的虚拟画布上。

## 使用场景

- **大型 LED 虚拟制片片场**：你需要将虚拟场景渲染到环绕片场的 LED 墙上，并确保摄像机运动时，虚拟场景的透视和亮度与物理环境完美匹配。
- **沉浸式穹顶/CAVE 系统**：你需要在多通道投影或显示器组成的沉浸式环境中运行一个实时应用。
- **专业多屏设置**：你需要将同一个应用的视图扩展到多个物理显示器上，且要求严格的同步和色彩一致性。
- **电影级离线渲染输出**：使用 Movie Graph 框架通过 nDisplay 进行分块、同步的离线渲染。

## 蓝图用法

nDisplay 的核心功能主要通过 C++ 和编辑器配置驱动，但提供了关键的蓝图接口用于运行时控制和查询。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get nDisplay Cluster Config` | 获取当前 nDisplay 集群的配置对象 | `UDisplayClusterConfiguration` |
| `Get All Viewports` | 获取所有 nDisplay 视口（渲染输出）的列表 | `ADisplayClusterRootActor` |
| `Set nDisplay Config` | 运行时加载并应用新的 nDisplay 配置文件 (.ndisplay) | `ADisplayClusterRootActor` |
| `Set Viewport Region` | 运行时修改指定视口的渲染区域（x, y, width, height） | `ADisplayClusterRootActor` |
| `Toggle Viewport` | 运行时启用或禁用指定的视口 | `ADisplayClusterRootActor` |
| `Set View Visibility` | 控制指定视口的可见性 | `ADisplayClusterRootActor` |
| `Sync Transport` | 控制 nDisplay 集群的同步传输（Play, Stop, Pause） | `IDisplayClusterClusterManager` |
| `Is Cluster Synced` | 查询集群是否处于同步状态 | `IDisplayClusterClusterManager` |

### 使用示例（蓝图描述）

要动态调整 LED 墙上虚拟场景的曝光：

1. 获取场景中的 `ADisplayClusterRootActor` 引用。
2. 使用 `Get All Viewports` 节点获取所有视口。
3. 遍历视口列表，对每个视口使用 `Set Viewport Region` 修改其渲染区域，或使用 `Set View Visibility` 控制可见性。
4. 通过 `Get nDisplay Cluster Config` 获取配置，可以动态修改材质参数或投影设置。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterRootActor.h"
#include "IDisplayCluster.h"
#include "DisplayClusterConfigurationTypes.h"
```

### 基本用法

**获取并遍历所有 nDisplay 视口**（来自 `DisplayClusterRootActor` 的测试用例）

```cpp
// 获取场景中的 nDisplay 根 Actor
ADisplayClusterRootActor* RootActor = GetRootActor(); // 通常通过场景查找或引用获取
if (!RootActor) return;

// 获取所有视口
TArray<UDisplayClusterConfigurationViewport*> Viewports;
RootActor->GetAllViewports(Viewports);

// 遍历视口
for (UDisplayClusterConfigurationViewport* Viewport : Viewports)
{
    UE_LOG(LogTemp, Log, TEXT("Viewport Name: %s, Region: %s"), 
           *Viewport->GetId().ToString(),
           *Viewport->GetRegion().ToString());
    
    // 可以访问视口的投影、色彩校正等配置
    const FDisplayClusterConfigurationProjection* ProjectionConfig = Viewport->GetProjection();
}
```

**运行时同步控制**（来自 `IDisplayCluster` 接口）

```cpp
// 获取 nDisplay 模块接口
IDisplayCluster& nDisplayModule = IDisplayCluster::Get();

// 获取集群管理器
IDisplayClusterClusterManager* ClusterManager = nDisplayModule.GetClusterMgr();
if (ClusterManager)
{
    // 检查是否为主节点（在集群中负责分发命令）
    if (ClusterManager->IsPrimary())
    {
        // 发送同步命令，所有节点将同时开始播放
        ClusterManager->SyncBarrier(TEXT("MySyncGroup"));
        
        // 发送自定义事件到所有节点
        ClusterManager->SendClusterEvent(TEXT("MyEvent"), TEXT("PayloadData"), true);
    }
}
```

### 进阶用法

**动态创建和配置 nDisplay 配置**（组合自多个配置相关测试）

```cpp
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterRootActor.h"

// 创建一个临时的 nDisplay 配置对象
UDisplayClusterConfiguration* NewConfig = NewObject<UDisplayClusterConfiguration>();

// 配置集群
FDisplayClusterConfigurationCluster& ClusterConfig = NewConfig->GetClusterConfig();
ClusterConfig.ClusterNodes.Add(TEXT("Node1"), FDisplayClusterConfigurationClusterNode());
ClusterConfig.ClusterNodes[TEXT("Node1")].Host = TEXT("192.168.1.101");
ClusterConfig.ClusterNodes[TEXT("Node1")].bIsPrimary = true;

// 配置一个视口
FDisplayClusterConfigurationViewport ViewportConfig;
ViewportConfig.Id = TEXT("MainViewport");
ViewportConfig.Region = FDisplayClusterRectangle(0, 0, 1920, 1080);

// 将视口分配给主节点
ClusterConfig.ClusterNodes[TEXT("Node1")].Viewports.Add(ViewportConfig.Id);

// 将配置应用到根 Actor
RootActor->SetConfiguration(NewConfig);
RootActor->RebuildConfiguration();
```

**监听和处理 nDisplay 事件**（来自消息拦截模块）

```cpp
#include "DisplayClusterMessageInterception.h"

// 订阅 nDisplay 内部事件
FDelegateHandle EventHandle = IDisplayCluster::Get().GetClusterMgr()->AddClusterEventListener(
    FOnDisplayClusterClusterEvent::CreateLambda([](const FDisplayClusterClusterEvent& Event)
    {
        if (Event.Name == TEXT("nDisplay.Node.Sync"))
        {
            UE_LOG(LogTemp, Log, TEXT("Received sync event from node: %s"), *Event.SenderId);
        }
    })
);

// 在模块关闭时解除订阅
// IDisplayCluster::Get().GetClusterMgr()->RemoveClusterEventListener(EventHandle);
```

## Demo 示例

一个最小示例，展示如何获取 nDisplay 根 Actor 并修改其一个视口的渲染区域。

### LightCardDemoActor.h
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LightCardDemoActor.generated.h"

class ADisplayClusterRootActor;
class UDisplayClusterConfigurationViewport;

UCLASS()
class ALightCardDemoActor : public AActor
{
    GENERATED_BODY()

public:
    ALightCardDemoActor();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "nDisplay Demo")
    void MoveViewportToCorner(const FString& ViewportId, float XOffset, float YOffset);

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay Demo")
    ADisplayClusterRootActor* nDisplayRootActor;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "nDisplay Demo")
    FString TargetViewportId = TEXT("MainViewport");
};
```

### LightCardDemoActor.cpp
```cpp
#include "LightCardDemoActor.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterConfigurationTypes.h"
#include "DisplayClusterLog.h"

ALightCardDemoActor::ALightCardDemoActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ALightCardDemoActor::BeginPlay()
{
    Super::BeginPlay();

    // 如果未指定根 Actor，则尝试在场景中查找
    if (!nDisplayRootActor)
    {
        TArray<AActor*> FoundActors;
        UGameplayStatics::GetAllActorsOfClass(GetWorld(), ADisplayClusterRootActor::StaticClass(), FoundActors);
        if (FoundActors.Num() > 0)
        {
            nDisplayRootActor = Cast<ADisplayClusterRootActor>(FoundActors[0]);
            UE_LOG(LogTemp, Log, TEXT("Found nDisplay Root Actor: %s"), *nDisplayRootActor->GetName());
        }
    }
}

void ALightCardDemoActor::MoveViewportToCorner(const FString& ViewportId, float XOffset, float YOffset)
{
    if (!nDisplayRootActor)
    {
        UE_LOG(LogTemp, Error, TEXT("nDisplay Root Actor is not set!"));
        return;
    }

    // 获取目标视口的当前配置
    UDisplayClusterConfigurationViewport* Viewport = nDisplayRootActor->GetViewportById(ViewportId);
    if (!Viewport)
    {
        UE_LOG(LogTemp, Warning, TEXT("Viewport '%s' not found."), *ViewportId);
        return;
    }

    // 获取当前渲染区域
    FDisplayClusterRectangle CurrentRegion = Viewport->GetRegion();
    UE_LOG(LogTemp, Log, TEXT("Current viewport region: %s"), *CurrentRegion.ToString());

    // 计算新位置（保持大小，移动位置）
    FDisplayClusterRectangle NewRegion;
    NewRegion.X = CurrentRegion.X + XOffset;
    NewRegion.Y = CurrentRegion.Y + YOffset;
    NewRegion.W = CurrentRegion.W;
    NewRegion.H = CurrentRegion.H;

    // 应用新的渲染区域
    Viewport->SetRegion(NewRegion);
    UE_LOG(LogTemp, Log, TEXT("Moved viewport '%s' to region: %s"), *ViewportId, *NewRegion.ToString());

    // 通知 nDisplay 配置已更改（可能需要在运行时重建设备）
    // 注意：运行时修改可能需要额外的同步步骤，具体取决于你的 nDisplay 配置
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `DisplayClusterShaders` | 提供 nDisplay 专用的着色器，用于投影、色彩校正和混合 |
| `DisplayClusterProjection` | 处理各种投影模型（MPCDI、Warp 等） |
| `DisplayClusterWarp` | 负责几何校正（Warping）和边缘融合 |
| `DisplayClusterMedia` | 处理与媒体框架（如 SRT、NDI）的集成 |
| `DisplayClusterReplication` | 管理 nDisplay 集群中的 Actor 和组件复制 |
| `DisplayClusterMultiUser` | 与 Unreal 的多人编辑功能集成 |
| `DisplayClusterConfiguration` | 定义和解析 .ndisplay 配置文件的数据结构 |
| `SharedMemoryMedia` | 通过共享内存实现超低延迟的帧传输 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 框架添加了 EXR 多层渲染支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 在 MoviePipeline 中统一了 WarpBlendAlpha 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中的摄像机命名问题和着色器中的不透明度问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了输出帧编码时未正确使用非默认 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理小于视口尺寸时出现的闪烁问题。 |

### 维护评价

nDisplay 是 Unreal Engine 中**活跃维护且至关重要**的插件。
- **创建时间**：2018 年，随 UE4.20 引入，已迭代超过 7 年。
- **维护活跃度**：最近一个月内有多次功能性更新和关键 Bug 修复，尤其是围绕 MovieGraph 和着色器。这表明 Epic Games 将其作为虚拟制片和集群渲染的**核心基础设施**在持续投入。
- **推荐使用**：**强烈推荐**。对于任何需要大规模、高精度同步渲染的项目（尤其是虚拟制片），nDisplay 是**标准且必需的解决方案**。尽管它复杂且默认禁用，但其稳定性和功能深度是无与伦比的。
- **已知限制**：配置复杂，对网络和硬件要求高。初学者的学习曲线陡峭。某些高级功能（如自定义投影）需要深入的 C++ 知识。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.0/en-US/ndisplay-in-unreal-engine/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)