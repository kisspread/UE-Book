# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、组件蓝图、材质模板、着色器、ThirdParty 库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多机集群同步渲染**的核心系统。它解决的核心问题是：当一台 PC 无法满足超大分辨率或多投影面的渲染需求时，需要多台 PC 协同工作，各自渲染画面的一部分，最终拼接成一个完整的、帧同步的视觉输出。

其主要应用领域包括：

- **虚拟制片 (ICVFX / In-Camera VFX)**：LED 墙幕拍摄场景，需要多台渲染节点驱动 LED 面板，与摄影机视角同步渲染虚拟环境，这是 nDisplay 最核心的使用场景
- **沉浸式显示系统**：CAVE（洞穴自动虚拟环境）、穹顶投影、多屏拼接显示器、飞行模拟器等需要多台 PC 驱动多个显示面的场景
- **大规模可视化**：建筑设计可视化、汽车设计评审等需要超高分辨率或超宽视场角的应用

nDisplay 通过网络通信实现集群节点间的时间同步、渲染同步和数据复制，确保所有节点在同一帧上保持一致。它内置了故障转移机制，在主节点失效时能自动选举新的主节点继续运行。

**重要提示**：该插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你正在搭建 **LED 虚拟制片片场**（如 Unreal Stage）→ 用 nDisplay 配置 ICVFX 摄影机和 LED 面板
- 你需要用多台 PC 驱动一个 **多面投影 CAVE 系统** → 用 nDisplay 配置各节点的投影策略
- 你在做 **飞行/驾驶模拟器**，需要多台 PC 同步渲染不同视角 → 用 nDisplay 集群模式
- 你需要在多台 PC 间 **精确同步游戏状态和时间** → 用 nDisplay 的集群管理器
- 你需要将 nDisplay 视口的渲染结果通过 **共享内存** 传递给其他进程 → 用 SharedMemoryMedia 模块
- 你需要在 **Movie Render Queue** 中录制多视口的多层 EXR 输出 → 用 DisplayClusterMoviePipeline 模块

## 蓝图用法

> **注意**：从 UE 5.4 开始，`IDisplayClusterBlueprintAPI` 中的大部分函数已被废弃，功能迁移到 `UDisplayClusterBlueprintLib` 的静态函数中。以下节点均为新 API。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOperationMode` | 获取当前操作模式（Cluster/Editor/Disabled） | `UDisplayClusterBlueprintLib` |
| `GetRootActor` | 获取当前 nDisplay 根 Actor | `UDisplayClusterBlueprintLib` |
| `GetNodeId` | 获取当前集群节点 ID | `UDisplayClusterBlueprintLib` |
| `GetActiveNodeIds` | 获取所有活跃节点 ID 列表 | `UDisplayClusterBlueprintLib` |
| `GetActiveNodesAmount` | 获取活跃节点数量 | `UDisplayClusterBlueprintLib` |
| `IsPrimary` | 当前节点是否为主节点 | `UDisplayClusterBlueprintLib` |
| `IsSecondary` | 当前节点是否为从节点 | `UDisplayClusterBlueprintLib` |
| `IsBackup` | 当前节点是否为备用节点 | `UDisplayClusterBlueprintLib` |
| `GetClusterRole` | 获取当前节点的集群角色 | `UDisplayClusterBlueprintLib` |
| `AddClusterEventListener` | 添加集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `RemoveClusterEventListener` | 移除集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventJson` | 发射 JSON 格式集群事件 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventBinary` | 发射二进制格式集群事件 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventJsonTo` | 向指定地址发送 JSON 集群事件 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventBinaryTo` | 向指定地址发送二进制集群事件 | `UDisplayClusterBlueprintLib` |

### 集群数据同步节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `RegisterSyncObject` | 注册同步对象到指定同步组（PreTick/Tick/PostTick） | `IDisplayClusterClusterManager` |
| `UnregisterSyncObject` | 取消注册同步对象 | `IDisplayClusterClusterManager` |
| `RegisterCustomState` | 注册自定义状态变量，自动跨节点复制 | `IDisplayClusterClusterManager` |
| `CreateGenericBarriersClient` | 创建通用屏障同步客户端 | `IDisplayClusterClusterManager` |

### 相机组件节点（UDisplayClusterCameraComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInterpupillaryDistance` | 获取瞳距 | `UDisplayClusterCameraComponent` |
| `SetInterpupillaryDistance` | 设置瞳距 | `UDisplayClusterCameraComponent` |
| `GetSwapEyes` | 获取左右眼交换状态 | `UDisplayClusterCameraComponent` |
| `SetSwapEyes` | 设置左右眼交换 | `UDisplayClusterCameraComponent` |
| `ToggleSwapEyes` | 切换左右眼交换 | `UDisplayClusterCameraComponent` |
| `GetStereoOffset` | 获取立体偏移类型（左/右/默认） | `UDisplayClusterCameraComponent` |
| `SetStereoOffset` | 设置立体偏移类型 | `UDisplayClusterCameraComponent` |

### ICVFX 摄影机节点（UDisplayClusterICVFXCameraComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActualCineCameraComponent` | 获取实际引用的电影摄影机组件 | `UDisplayClusterICVFXCameraComponent` |
| `IsICVFXEnabled` | 当前节点上该 ICVFX 摄影机是否启用 | `UDisplayClusterICVFXCameraComponent` |
| `SetDepthOfFieldParameters` | 设置景深参数并更新补偿 LUT | `UDisplayClusterICVFXCameraComponent` |

### Light Card 节点（ADisplayClusterLightCardActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakeFlushToWall` | 使 Light Card 贴合墙面 | `ADisplayClusterLightCardActor` |
| `SetIsLightCardFlag` | 设置为标志类型 Light Card | `ADisplayClusterLightCardActor` |
| `SetIsUVActor` | 设置为 UV 空间中的 Light Card | `ADisplayClusterLightCardActor` |
| `AddToRootActor` | 将 Light Card 添加到指定 Root Actor | `ADisplayClusterLightCardActor` |
| `RemoveFromRootActor` | 从 Root Actor 移除 Light Card | `ADisplayClusterLightCardActor` |

### 使用示例（蓝图描述）

**发送集群事件**：
1. 创建 `FDisplayClusterClusterEventJson` 结构体，设置 Category、Type、Description 等字段
2. 调用 `EmitClusterEventJson` 节点，传入事件和 `bPrimaryOnly=false` 表示广播给所有节点
3. 在需要接收的 Actor 中调用 `AddClusterEventListener`，绑定一个实现了 `IDisplayClusterClusterEventListener` 接口的对象

**获取当前节点信息**：
1. 调用 `GetOperationMode` 确认当前为 Cluster 模式
2. 调用 `IsPrimary` 判断是否为主节点
3. 调用 `GetNodeId` 获取本机节点名称
4. 根据节点角色执行不同的渲染逻辑

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterModule.h"
#include "IDisplayCluster.h"
#include "Cluster/IDisplayClusterClusterManager.h"
#include "Render/IDisplayClusterRenderManager.h"
#include "Blueprints/IDisplayClusterBlueprintAPI.h"
#include "Components/DisplayClusterCameraComponent.h"
#include "Components/DisplayClusterICVFXCameraComponent.h"
#include "DisplayClusterRootActor.h"
#include "DisplayClusterLightCardActor.h"
#include "IDisplayClusterCallbacks.h"
```

### 基本用法

```cpp
// 获取 nDisplay 模块单例
IDisplayCluster& DisplayCluster = IDisplayCluster::Get();

// 获取各管理器接口
IDisplayClusterClusterManager* ClusterMgr = DisplayCluster.GetClusterMgr();
IDisplayClusterRenderManager*  RenderMgr  = DisplayCluster.GetRenderMgr();
IDisplayClusterGameManager*    GameMgr    = DisplayCluster.GetGameMgr();

// 检查当前操作模式
EDisplayClusterOperationMode OpMode = DisplayCluster.GetOperationMode();
if (OpMode == EDisplayClusterOperationMode::Cluster)
{
    // 正在集群模式下运行
}

// 获取集群信息
if (ClusterMgr)
{
    bool bIsPrimary = ClusterMgr->IsPrimary();
    FString NodeId  = ClusterMgr->GetNodeId();
    uint32 NodeCount = ClusterMgr->GetNodesAmount();
    
    TArray<FString> AllNodeIds;
    ClusterMgr->GetNodeIds(AllNodeIds);
}
```

### 集群事件通信

```cpp
// 注册事件监听器
FOnClusterEventJsonListener JsonListener;
JsonListener.BindLambda([](const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received event: Category=%s Type=%s"), 
        *Event.Category, *Event.Type);
});
ClusterMgr->AddClusterEventJsonListener(JsonListener);

// 发射 JSON 集群事件
FDisplayClusterClusterEventJson Event;
Event.Category    = TEXT("MyPlugin");
Event.Type        = TEXT("StateChange");
Event.Description = TEXT("Player entered zone");
Event.bIsSystemEvent = false;

ClusterMgr->EmitClusterEventJson(Event, /*bPrimaryOnly=*/false);

// 向特定地址发送事件（集群外通信）
ClusterMgr->SendClusterEventTo(
    TEXT("192.168.1.100"), 8090, Event, false);

// 清理
ClusterMgr->RemoveClusterEventJsonListener(JsonListener);
```

### 数据同步对象注册

```cpp
// 假设你有一个需要跨节点同步的对象
// 实现 IDisplayClusterClusterSyncObject 接口

// 注册到指定同步组
// EDisplayClusterSyncGroup::PreTick - 在 PreTick 阶段同步
// EDisplayClusterSyncGroup::Tick    - 在 Tick 阶段同步
// EDisplayClusterSyncGroup::PostTick - 在 PostTick 阶段同步
ClusterMgr->RegisterSyncObject(MySyncObject, EDisplayClusterSyncGroup::Tick);

// 取消注册
ClusterMgr->UnregisterSyncObject(MySyncObject);
```

### 自定义分布式状态

```cpp
// 使用模板类创建跨节点自动复制的状态变量
#include "Cluster/CustomStates/DisplayClusterCustomStateDistributed.h"

// 创建一个 float 类型的分布式状态
TSharedPtr<TDistributedCustomState<float>> SharedScore;

void InitSharedState()
{
    // 通过工厂方法创建并自动注册
    SharedScore = TDistributedCustomState<float>::Create(FName("SharedScore"), 0.0f);
}

void UpdateScore(float NewScore)
{
    if (SharedScore)
    {
        // 设置新值，下一帧自动同步到所有节点
        SharedScore->SetData(NewScore);
    }
}

void ReadScore()
{
    if (SharedScore)
    {
        // 获取当前帧的本地值
        float CurrentScore = SharedScore->GetData();
        
        // 获取特定节点的值
        float PrimaryScore = SharedScore->GetData(FName("PrimaryNode"));
        
        // 获取所有可用节点
        TSet<FName> AvailableNodes = SharedScore->GetAvailableNodes();
    }
}
```

### 注册回调

```cpp
#include "IDisplayClusterCallbacks.h"

IDisplayClusterCallbacks& Callbacks = IDisplayCluster::Get().GetCallbacks();

// 监听会话开始事件
Callbacks.OnDisplayClusterStartSession().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("nDisplay session started"));
});

// 监听渲染线程 warp 前事件
Callbacks.OnDisplayClusterPreWarp_RenderThread().AddLambda(
    [](FRHICommandListImmediate& RHICmdList, const IDisplayClusterViewportManagerProxy* Proxy)
{
    // 在 warp 处理前插入自定义渲染逻辑
});

// 监听节点故障
Callbacks.OnDisplayClusterFailoverNodeDown().AddLambda(
    [](const FString& FailedNodeId)
{
    UE_LOG(LogTemp, Warning, TEXT("Cluster node failed: %s"), *FailedNodeId);
});

// 监听主节点变更
Callbacks.OnDisplayClusterFailoverPrimaryNodeChanged().AddLambda(
    [](const FString& NewPrimaryId)
{
    UE_LOG(LogTemp, Log, TEXT("New primary node: %s"), *NewPrimaryId);
});
```

### 注册自定义投影策略工厂

```cpp
#include "Render/IDisplayClusterRenderManager.h"

IDisplayClusterRenderManager* RenderMgr = IDisplayCluster::Get().GetRenderMgr();
if (RenderMgr)
{
    // 注册自定义投影策略
    TSharedPtr<IDisplayClusterProjectionPolicyFactory> MyFactory = 
        MakeShared<FMyProjectionPolicyFactory>();
    RenderMgr->RegisterProjectionPolicyFactory(TEXT("MyProjection"), MyFactory);
    
    // 注册自定义后处理工厂
    TSharedPtr<IDisplayClusterPostProcessFactory> MyPPFactory = 
        MakeShared<FMyPostProcessFactory>();
    RenderMgr->RegisterPostProcessFactory(TEXT("MyPostProcess"), MyPPFactory);
    
    // 注册自定义 warp 策略
    TSharedPtr<IDisplayClusterWarpPolicyFactory> MyWarpFactory = 
        MakeShared<FMyWarpPolicyFactory>();
    RenderMgr->RegisterWarpPolicyFactory(TEXT("MyWarp"), MyWarpFactory);
}
```

## Demo 示例

以下是一个完整的自定义同步状态组件示例，用于在集群中同步一个 float 值：

```cpp
// MyClusterSyncComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "Cluster/CustomStates/DisplayClusterCustomStateDistributed.h"
#include "MyClusterSyncComponent.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyClusterSyncComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UMyClusterSyncComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    /** 设置要同步的值 */
    UFUNCTION(BlueprintCallable, Category = "Cluster Sync")
    void SetSyncedValue(float InValue);

    /** 获取当前同步值 */
    UFUNCTION(BlueprintCallable, Category = "Cluster Sync")
    float GetSyncedValue() const;

    /** 获取主节点的同步值 */
    UFUNCTION(BlueprintCallable, Category = "Cluster Sync")
    float GetPrimaryNodeValue() const;

private:
    TSharedPtr<TDistributedCustomState<float>> SyncState;
};
```

```cpp
// MyClusterSyncComponent.cpp
#include "MyClusterSyncComponent.h"
#include "IDisplayCluster.h"
#include "Cluster/IDisplayClusterClusterManager.h"

UMyClusterSyncComponent::UMyClusterSyncComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyClusterSyncComponent::BeginPlay()
{
    Super::BeginPlay();

    // 确保 nDisplay 已加载
    if (!IDisplayCluster::IsAvailable())
    {
        UE_LOG(LogTemp, Warning, TEXT("nDisplay not available, sync disabled"));
        return;
    }

    // 创建分布式状态
    SyncState = TDistributedCustomState<float>::Create(
        FName("MySyncedFloat"), 0.0f);

    if (SyncState)
    {
        UE_LOG(LogTemp, Log, TEXT("Cluster sync state created successfully"));
    }
}

void UMyClusterSyncComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    SyncState.Reset();
    Super::EndPlay(EndPlayReason);
}

void UMyClusterSyncComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!SyncState) return;

    // 在主节点上更新值（例如基于游戏逻辑）
    IDisplayClusterClusterManager* ClusterMgr = 
        IDisplayCluster::Get().GetClusterMgr();
    
    if (ClusterMgr && ClusterMgr->IsPrimary())
    {
        float NewValue = SyncState->GetData() + DeltaTime;
        SyncState->SetData(NewValue);
    }
}

void UMyClusterSyncComponent::SetSyncedValue(float InValue)
{
    if (SyncState)
    {
        SyncState->SetData(InValue);
    }
}

float UMyClusterSyncComponent::GetSyncedValue() const
{
    return SyncState ? SyncState->GetData() : 0.0f;
}

float UMyClusterSyncComponent::GetPrimaryNodeValue() const
{
    if (!SyncState) return 0.0f;

    IDisplayClusterClusterManager* ClusterMgr = 
        IDisplayCluster::Get().GetClusterMgr();
    
    if (ClusterMgr)
    {
        return SyncState->GetData(FName(*ClusterMgr->GetPrimaryNodeId()));
    }
    
    return SyncState->GetData();
}
```

## 模块依赖

nDisplay 是一个大型插件，其自身模块众多。以下是使用 nDisplay 时你的项目模块需要的**特殊依赖**：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | nDisplay 核心运行时，提供集群管理、渲染设备、视口管理等基础 API |
| `DisplayClusterConfiguration` | 配置数据资产和配置类，用于定义集群拓扑、视口布局等 |
| `DisplayClusterProjection` | 投影策略实现（简单投影、MPCDI、Mesh 投影等） |
| `DisplayClusterWarp` | Warp/Blend 校正策略，用于几何变形和边缘融合 |
| `DisplayClusterShaders` | nDisplay 专用着色器（ICVFX、WarpBlend、UV LightCard 等） |
| `DisplayClusterColorGrading` | ICVFX 色彩分级支持 |
| `DisplayClusterMedia` | 媒体输入输出集成（MediaCapture、MediaPlayer） |
| `DisplayClusterMultiUser` | 多用户编辑支持 |
| `DisplayClusterReplication` | 网络复制支持 |
| `SharedMemoryMedia` | 基于共享内存的媒体传输，用于进程间帧数据传递 |
| `DisplayClusterMoviePipeline` | Movie Render Queue 集成，支持多层 EXR 输出 |
| `ScalableMPCDI` | 第三方 MPCDI 库（外部依赖） |

> 无特殊依赖（仅标准 Core/Engine/Slate 等）——如果只使用蓝图 API，不需要额外引用这些模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 支持 nDisplay 多层 EXR 输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知摄影机命名及 MPCDI/ICVFX 着色器透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时支持非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护中**。nDisplay 是 Epic Games 虚拟制片（Virtual Production）战略的核心组件，自 2018 年创建以来持续获得大量功能性更新。最近的提交记录显示 2026 年仍在积极开发新功能（如 MovieGraph 多层 EXR 支持）并修复各类渲染问题。

关键特点：
- **模块众多**（29 个模块），架构复杂但分工明确
- 集群通信、故障转移、多视口渲染、ICVFX、WarpBlend 等子系统持续演进
- 蓝图 API 从旧接口迁移到 `UDisplayClusterBlueprintLib`（5.4+），有大量 `UE_DEPRECATED` 标记
- 与 Movie Render Queue、Media Framework、Remote Control 等系统深度集成
- 支持 Windows 和 Linux 平台

**强烈推荐使用**：如果你的项目涉及虚拟制片、LED 墙幕拍摄或任何需要多 PC 同步渲染的场景，nDisplay 是 UE5 中唯一的官方解决方案，且处于高度活跃的维护状态。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：https://docs.unrealengine.com/5.0/en-US/n-display-in-unreal-engine/（.uplugin 中未提供 DocsURL，请参考 Unreal 官方文档站）