# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染系统 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、编辑器工具、第三方库） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

---

## 用途

nDisplay 是 UE5 的**多机集群同步渲染框架**，解决的核心问题是：**如何让多台 PC 各自渲染同一个虚拟场景的不同视角，将画面投射到多块物理显示器/投影幕布上，并保持帧同步与数据一致性。**

具体能力包括：

- **集群节点间网络通信**：通过 `FDisplayClusterClusterManager` 管理 Primary / Secondary / Backup 节点角色，同步时间、对象状态和集群事件
- **多视口独立渲染**：每个物理输出对应一个 nDisplay Viewport，各自拥有独立的投影策略（MPCDI、Mesh、EasyBlend 等）、后处理管线和 Warp&Blend 配置
- **ICVFX（In-Camera VFX）支持**：为虚拟制片场景提供内画幅相机渲染，支持色度键抠像、柔边融合、OCIO 色彩管理
- **渲染设备抽象**：通过 `IDisplayClusterRenderDevice` 抽象立体/单目渲染、帧同步策略和呈现方式
- **高可用与故障转移**：`FDisplayClusterFailoverNodeCtrlMain` 实现节点掉线后自动重新选举 Primary 节点并恢复同步状态
- **跨 GPU 传输**：支持多 GPU 间的渲染目标数据拷贝

## 适用场景

| 场景 | 说明 |
|---|---|
| CAVE / 多面投影系统 | 多台 PC 各驱动一面投影墙，通过 MPCDI 网格校正实现无缝拼接 |
| LED 虚拟制片 (ICVFX) | LED 墙 + 内画幅相机，实时渲染并投射虚拟背景 |
| 多屏赛车/飞行模拟器 | 每个物理显示器对应一个 nDisplay Viewport |
| 大型场馆沉浸式投影 | 多台投影仪拼接，配合 Warp&Blend 实现均匀亮度过渡 |
| 影视级离线渲染 | 配合 MoviePipeline 多机集群渲染 EXR 多层输出 |
| 舞台灯光设计 | LightCard 系统模拟虚拟灯光效果并投射到 LED 墙 |

**注意**：nDisplay 默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。

---

## 蓝图用法

> **重要**：旧版 `IDisplayClusterBlueprintAPI` 中的所有蓝图节点自 UE 5.4 起已全部废弃，迁移到 `UDisplayClusterBlueprintLib`（文档中提供的源码文件未包含该类实现，以下基于接口声明和组件 API 提取）。

### 核心节点

#### 集群信息查询（UDisplayClusterBlueprintLib）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOperationMode` | 获取当前运行模式（Disabled/Cluster/Editor） | `UDisplayClusterBlueprintLib` |
| `GetRootActor` | 获取 nDisplay 根 Actor | `UDisplayClusterBlueprintLib` |
| `GetNodeId` | 获取当前集群节点 ID | `UDisplayClusterBlueprintLib` |
| `GetActiveNodeIds` | 获取所有活跃节点 ID 列表 | `UDisplayClusterBlueprintLib` |
| `GetActiveNodesAmount` | 获取活跃节点数量 | `UDisplayClusterBlueprintLib` |
| `IsPrimary` | 当前节点是否为 Primary | `UDisplayClusterBlueprintLib` |
| `IsSecondary` | 当前节点是否为 Secondary | `UDisplayClusterBlueprintLib` |
| `IsBackup` | 当前节点是否为 Backup | `UDisplayClusterBlueprintLib` |
| `GetClusterRole` | 获取节点角色枚举 | `UDisplayClusterBlueprintLib` |

#### 集群事件

| 节点 | 说明 | 所在类 |
|---|---|---|
| `AddClusterEventListener` | 注册集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `RemoveClusterEventListener` | 移除集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventJson` | 发送 JSON 格式集群事件 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventBinary` | 发送二进制格式集群事件 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventJsonTo` | 向指定地址发送 JSON 事件（集群外） | `UDisplayClusterBlueprintLib` |
| `SendClusterEventBinaryTo` | 向指定地址发送二进制事件（集群外） | `UDisplayClusterBlueprintLib` |

#### 相机组件（UDisplayClusterCameraComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInterpupillaryDistance` | 获取瞳距 | `UDisplayClusterCameraComponent` |
| `SetInterpupillaryDistance` | 设置瞳距 | `UDisplayClusterCameraComponent` |
| `GetSwapEyes` | 获取左右眼交换状态 | `UDisplayClusterCameraComponent` |
| `SetSwapEyes` | 设置左右眼交换状态 | `UDisplayClusterCameraComponent` |
| `ToggleSwapEyes` | 切换左右眼交换状态 | `UDisplayClusterCameraComponent` |
| `GetStereoOffset` | 获取立体偏移类型 | `UDisplayClusterCameraComponent` |
| `SetStereoOffset` | 设置立体偏移类型 | `UDisplayClusterCameraComponent` |

#### ICVFX 相机（UDisplayClusterICVFXCameraComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActualCineCameraComponent` | 获取实际引用的电影摄像机组件 | `UDisplayClusterICVFXCameraComponent` |
| `IsICVFXEnabled` | 当前节点是否启用 ICVFX | `UDisplayClusterICVFXCameraComponent` |
| `SetDepthOfFieldParameters` | 设置景深参数并更新补偿 LUT | `UDisplayClusterICVFXCameraComponent` |

#### 根 Actor（ADisplayClusterRootActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetFlushPositionAndNormal` | 获取舞台上某个世界坐标对应的墙面位置和法线 | `ADisplayClusterRootActor` |
| `MakeStageActorFlushToWall` | 将 Stage Actor 贴合到墙面 | `ADisplayClusterRootActor` |
| `GetDistanceToStageGeometry` | 计算世界坐标到舞台几何体的距离 | `ADisplayClusterRootActor` |
| `GetCommonViewPoint` | 获取最常用的观察点组件 | `ADisplayClusterRootActor` |
| `SetReplaceTextureFlagForAllViewports` | 为所有视口设置纹理替换标志 | `ADisplayClusterRootActor` |
| `SetFreezeOuterViewports` | 冻结/解冻外部视口渲染 | `ADisplayClusterRootActor` |
| `UpdateProceduralMeshComponentData` | 更新程序化网格组件数据 | `ADisplayClusterRootActor` |

#### LightCard（ADisplayClusterLightCardActor）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetLongitude` | 设置经度（极坐标定位） | `ADisplayClusterLightCardActor` |
| `SetLatitude` | 设置纬度（极坐标定位） | `ADisplayClusterLightCardActor` |
| `SetDistanceFromCenter` | 设置到圆心距离 | `ADisplayClusterLightCardActor` |
| `SetSpin` / `SetPitch` / `SetYaw` | 设置旋转 | `ADisplayClusterLightCardActor` |
| `SetUVCoordinates` | 设置 UV 空间坐标 | `ADisplayClusterLightCardActor` |
| `SetScale` | 设置缩放 | `ADisplayClusterLightCardActor` |
| `AddToRootActor` | 将灯光卡片添加到指定根 Actor | `ADisplayClusterLightCardActor` |
| `RemoveFromRootActor` | 从根 Actor 移除灯光卡片 | `ADisplayClusterLightCardActor` |
| `SetIsUVActor` | 标记为 UV 空间灯光卡片 | `ADisplayClusterLightCardActor` |
| `ShowLightCardLabel` | 显示/配置灯光卡片标签 | `ADisplayClusterLightCardActor` |

#### 预览共享组件（UDisplayClusterPreviewShareComponent）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetMode` | 设置共享模式（None/Send/Receive/PullActor） | `UDisplayClusterPreviewShareComponent` |
| `SetUniqueName` | 设置匹配用的唯一名称 | `UDisplayClusterPreviewShareComponent` |

### 使用示例（蓝图描述）

#### 示例 1：集群启动时查询节点角色

1. 在 Level Blueprint 中，使用 `Event BeginPlay` 节点
2. 连接到 `Get Operation Mode` 节点（路径：nDisplay 分类）
3. 用 `Branch` 判断是否为 `EDisplayClusterOperationMode::Cluster`
4. 如果是 Cluster 模式，调用 `Get Node Id` 获取本节点 ID
5. 调用 `Is Primary` 判断是否为主节点，据此执行不同逻辑

#### 示例 2：发送集群事件同步操作

1. 创建一个 `Custom Event`（如 `OnButtonPressed`）
2. 构造 `FDisplayClusterClusterEventJson` 结构体，设置 `Category`、`Type`、`Json` 等字段
3. 连接到 `Emit Cluster Event Json`，`bPrimaryOnly` 设为 `false`（所有节点接收）
4. 在另一处创建事件监听器，实现 `IDisplayClusterClusterEventListener` 接口
5. 在 `BeginPlay` 中调用 `Add Cluster Event Listener` 注册

#### 示例 3：灯光卡片动态控制

1. 获取场景中的 `ADisplayClusterLightCardActor` 引用
2. 用 `Set Latitude` 设置纬度（如 45.0）
3. 用 `Set Longitude` 设置经度（如 90.0）
4. 用 `Set Distance From Center` 设置距离（如 500.0）
5. 用 `Set Gain` 和 `Set Opacity` 控制外观

---

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "IDisplayCluster.h"
#include "IDisplayClusterClusterManager.h"
#include "IDisplayClusterRenderManager.h"

// 视口管理
#include "IDisplayClusterViewportManager.h"
#include "IDisplayClusterViewportManagerProxy.h"

// 组件
#include "DisplayClusterRootActor.h"
#include "DisplayClusterCameraComponent.h"
#include "DisplayClusterICVFXCameraComponent.h"
#include "DisplayClusterLightCardActor.h"

// 集群自定义状态
#include "DisplayClusterCustomStateDistributed.h"

// 投影策略接口
#include "IDisplayClusterProjectionPolicy.h"

// 回调
#include "IDisplayClusterCallbacks.h"
```

### 基本用法 — 获取 nDisplay 模块接口

```cpp
// 来源：Private/DisplayClusterModule.h
// 获取 nDisplay 模块单例
IDisplayCluster& DisplayCluster = IDisplayCluster::Get();

// 检查运行模式
EDisplayClusterOperationMode Mode = DisplayCluster.GetOperationMode();
if (Mode == EDisplayClusterOperationMode::Cluster)
{
    // 集群模式运行
    IDisplayClusterClusterManager* ClusterMgr = DisplayCluster.GetClusterMgr();
    FString NodeId = ClusterMgr->GetNodeId();
    bool bPrimary = ClusterMgr->IsPrimary();
}
```

### 基本用法 — 集群事件收发

```cpp
// 来源：Public/Cluster/IDisplayClusterClusterManager.h
IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();

// 注册 JSON 事件监听
FOnClusterEventJsonListener JsonListener;
JsonListener.BindLambda([](const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received JSON event: Category=%s, Type=%s"),
        *Event.Category, *Event.Type);
});
ClusterMgr->AddClusterEventJsonListener(JsonListener);

// 发送 JSON 集群事件
FDisplayClusterClusterEventJson Event;
Event.Category = TEXT("Gameplay");
Event.Type = TEXT("PlayerAction");
Event.Json = TEXT("{\"action\":\"fire\"}");
Event.bIsSystemEvent = false;
ClusterMgr->EmitClusterEventJson(Event, false); // false = 所有节点接收

// 清理
ClusterMgr->RemoveClusterEventJsonListener(JsonListener);
```

### 基本用法 — 注册同步对象

```cpp
// 来源：Public/Cluster/IDisplayClusterClusterManager.h
// 任何实现了 IDisplayClusterClusterSyncObject 接口的对象都可以注册同步
IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();

// 注册到 PreTick 同步组（可选 PreTick/Tick/PostTick）
MySyncObject* SyncObj = new MySyncObject();
ClusterMgr->RegisterSyncObject(SyncObj, EDisplayClusterSyncGroup::PreTick);

// 注销
ClusterMgr->UnregisterSyncObject(SyncObj);
```

### 进阶用法 — 自定义分布式状态（Distributed Custom State）

```cpp
// 来源：Public/Cluster/CustomStates/DisplayClusterCustomStateDistributed.h
// 自定义状态允许在集群各节点间同步任意类型的数据

// 1. 定义你的数据结构
struct FMyClusterState
{
    float Health = 100.f;
    FVector Position = FVector::ZeroVector;

    // 必须提供序列化操作符
    friend FArchive& operator<<(FArchive& Ar, FMyClusterState& State)
    {
        Ar << State.Health;
        Ar << State.Position;
        return Ar;
    }
};

// 2. 创建分布式自定义状态实例（自动注册到集群管理器）
TSharedPtr<TDistributedCustomState<FMyClusterState>> GameState =
    TDistributedCustomState<FMyClusterState>::Create(FName("GameState"));

if (GameState.IsValid())
{
    // 3. 写入本地状态数据
    FMyClusterState NewState;
    NewState.Health = 80.f;
    NewState.Position = FVector(100, 200, 300);
    GameState->SetData(NewState);

    // 4. 读取本节点状态数据
    const FMyClusterState& LocalData = GameState->GetData();

    // 5. 读取其他节点的状态数据（集群同步后可用）
    TSet<FName> AvailableNodes = GameState->GetAvailableNodes();
    for (const FName& NodeId : AvailableNodes)
    {
        const FMyClusterState& NodeData = GameState->GetData(NodeId);
        UE_LOG(LogTemp, Log, TEXT("Node %s: Health=%.1f"), *NodeId.ToString(), NodeData.Health);
    }

    // 6. 配置自定义上游节点（可选）
    GameState->SetCustomUpstreamsEnabled(true);
    TSet<FName> UpstreamNodes;
    UpstreamNodes.Add(FName("NodeA"));
    UpstreamNodes.Add(FName("NodeB"));
    GameState->SetUpstreams(UpstreamNodes);
}
```

### 进阶用法 — 使用回调系统

```cpp
// 来源：Public/IDisplayClusterCallbacks.h
IDisplayClusterCallbacks& Callbacks = IDisplayCluster::Get().GetCallbacks();

// 监听 session 开始
Callbacks.OnDisplayClusterStartSession().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("nDisplay session started"));
});

// 监听帧呈现完成（RHI 线程）
Callbacks.OnDisplayClusterFramePresented_RHIThread().AddLambda(
    [](bool bNativePresent)
    {
        // 帧已呈现到屏幕
    });

// 监听集群节点故障
Callbacks.OnDisplayClusterFailoverNodeDown().AddLambda(
    [](const FString& FailedNodeId)
    {
        UE_LOG(LogTemp, Warning, TEXT("Cluster node failed: %s"), *FailedNodeId);
    });

// 监听新 Primary 节点选举
Callbacks.OnDisplayClusterFailoverPrimaryNodeChanged().AddLambda(
    [](const FString& NewPrimaryId)
    {
        UE_LOG(LogTemp, Log, TEXT("New primary node: %s"), *NewPrimaryId);
    });

// 渲染线程：在 Warp 之前执行自定义操作
Callbacks.OnDisplayClusterPreWarp_RenderThread().AddLambda(
    [](FRHICommandListImmediate& RHICmdList, const IDisplayClusterViewportManagerProxy* VPMProxy)
    {
        // 在所有视口 warp 之前执行自定义渲染操作
    });
```

### 进阶用法 — 创建通用屏障同步客户端

```cpp
// 来源：Public/Cluster/IDisplayClusterClusterManager.h
IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();

// 创建通用屏障客户端（用于自定义同步点）
TSharedRef<IDisplayClusterGenericBarriersClient> BarrierClient =
    ClusterMgr->CreateGenericBarriersClient();

// 使用屏障进行节点间同步
// 具体用法参见 IDisplayClusterGenericBarriersClient 接口
```

---

## Demo 示例

### 集群状态同步的最小完整示例

```cpp
// MyClusterSyncComponent.h
#pragma once

#include "Components/ActorComponent.h"
#include "DisplayClusterCustomStateDistributed.h"
#include "MyClusterSyncComponent.generated.h"

USTRUCT(BlueprintType)
struct FSyncedPlayerState
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite)
    float Health = 100.f;

    UPROPERTY(BlueprintReadWrite)
    FVector Location = FVector::ZeroVector;

    friend FArchive& operator<<(FArchive& Ar, FSyncedPlayerState& State)
    {
        Ar << State.Health;
        Ar << State.Location;
        return Ar;
    }
};

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class UMyClusterSyncComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType,
        FActorComponentTickFunction* ThisTickFunction) override;

    UFUNCTION(BlueprintCallable)
    void SetPlayerHealth(float NewHealth);

    UFUNCTION(BlueprintCallable)
    float GetRemotePlayerHealth(const FString& NodeId) const;

    UFUNCTION(BlueprintCallable)
    TArray<FString> GetAvailableNodeIds() const;

private:
    TSharedPtr<TDistributedCustomState<FSyncedPlayerState>> SyncedState;
};
```

```cpp
// MyClusterSyncComponent.cpp
#include "MyClusterSyncComponent.h"
#include "IDisplayCluster.h"
#include "IDisplayClusterClusterManager.h"

void UMyClusterSyncComponent::BeginPlay()
{
    Super::BeginPlay();

    // 创建分布式自定义状态，自动注册到集群管理器
    SyncedState = TDistributedCustomState<FSyncedPlayerState>::Create(
        FName("PlayerSyncState"));

    if (!SyncedState.IsValid())
    {
        UE_LOG(LogTemp, Warning,
            TEXT("Failed to create custom state. Is nDisplay enabled and in Cluster mode?"));
    }
}

void UMyClusterSyncComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 状态会在集群管理器中自动注销
    SyncedState.Reset();
    Super::EndPlay(EndPlayReason);
}

void UMyClusterSyncComponent::TickComponent(float DeltaTime, ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (!SyncedState.IsValid()) return;

    // 更新本地状态（每帧写入，下一帧自动同步到所有节点）
    FSyncedPlayerState CurrentState;
    CurrentState.Health = GetPlayerHealth(); // 你的实际逻辑
    CurrentState.Location = GetOwner()->GetActorLocation();
    SyncedState->SetData(CurrentState);
}

void UMyClusterSyncComponent::SetPlayerHealth(float NewHealth)
{
    if (SyncedState.IsValid())
    {
        FSyncedPlayerState State = SyncedState->GetData();
        State.Health = NewHealth;
        SyncedState->SetData(State);
    }
}

float UMyClusterSyncComponent::GetRemotePlayerHealth(const FString& NodeId) const
{
    if (SyncedState.IsValid())
    {
        return SyncedState->GetData(FName(*NodeId)).Health;
    }
    return 0.f;
}

TArray<FString> UMyClusterSyncComponent::GetAvailableNodeIds() const
{
    TArray<FString> Result;
    if (SyncedState.IsValid())
    {
        TSet<FName> Nodes = SyncedState->GetAvailableNodes();
        for (const FName& Node : Nodes)
        {
            Result.Add(Node.ToString());
        }
    }
    return Result;
}
```

---

## 模块依赖

本插件共有 28 个模块，依赖关系复杂。以下列出**使用者项目**最可能需要关注的依赖：

| 模块 | 用途 |
|---|---|
| `DisplayCluster` | 核心模块：集群管理、渲染设备、视口管理 |
| `DisplayClusterConfiguration` | 配置数据模型（.ndisplay 配置文件解析） |
| `DisplayClusterProjection` | 投影策略实现（MPCDI、Mesh、EasyBlend 等） |
| `DisplayClusterWarp` | Warp&Blend 处理 |
| `DisplayClusterShaders` | nDisplay 专用渲染着色器 |
| `DisplayClusterColorGrading` | ICVFX 色彩分级 |
| `DisplayClusterMedia` | 媒体输入输出（依赖 `D3D12RHI`） |
| `DisplayClusterMultiUser` | 多用户编辑协作支持 |
| `DisplayClusterMoviePipeline` | Movie Pipeline 集群渲染支持 |
| `DisplayClusterReplication` | 网络复制支持 |
| `ScalableMPCDI` (External) | 第三方 MPCDI 库 |

**注意**：多个模块依赖 `UnrealEd`，表明这些模块包含编辑器功能，尽管它们全部标记为 `Runtime` 类型。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 的 nDisplay 渲染添加 EXR 多层输出支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 中将 WarpBlendAlpha 模式合并到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中拓扑感知相机命名；修复 MPCDI/ICVFX 着色器中的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退路径中正确处理非默认的 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的画面闪烁 |

### 维护评价

- **活跃维护**：最近 2 周内有多次实质性功能更新和 bug 修复，保持高频迭代
- **成熟度高**：创建于 2018 年（约 8 年），经过大量生产项目验证，是虚拟制片和沉浸式体验的核心技术栈
- **API 稳定性**：旧版 API 有清晰的废弃迁移路径（`IDisplayClusterBlueprintAPI` → `UDisplayClusterBlueprintLib`），但部分 5.3/5.4 废弃标记尚未完全移除
- **模块规模庞大**：1351 个源文件、28 个模块，涵盖集群同步、渲染管线、投影、色彩管理、媒体、故障转移等全链路
- **已知限制**：默认禁用需手动启用；所有模块均标记为 Runtime 但实际包含大量编辑器代码；入门门槛较高
- **推荐使用**：如果你的项目需要多机集群渲染、虚拟制片 ICVFX、或沉浸式投影系统，这是 UE5 官方唯一推荐的方案，**强烈推荐使用**。对于简单的多屏需求，可能过于复杂。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/RenderingAndGraphics/nDisplay/Overview/)（.uplugin 未提供 DocsURL，此为 UE 官方文档链接）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay/Source/DisplayClusterTests)