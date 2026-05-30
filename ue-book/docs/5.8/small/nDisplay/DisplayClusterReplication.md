# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、着色器、编辑器工具、配置模板） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**集群同步渲染**的核心插件，解决单台 PC 无法满足大型显示场景的渲染需求问题。其核心能力是将一个 UE 场景的渲染工作分配到多台 PC 上，每台 PC 负责渲染画面的不同部分（如不同视角、不同投影区域），并通过自定义网络驱动（`UDisplayClusterNetDriver`）确保所有节点间 Actor 状态和渲染参数的精确同步，最终拼接成无缝的完整画面。

插件涵盖以下核心功能：
- **集群网络同步**：通过 `UDisplayClusterNetDriver` 和 `UDisplayClusterNetConnection` 实现集群节点间的确定性同步复制，确保所有节点在同一帧渲染完全一致的世界状态
- **投影与变形混合（Warp & Blend）**：支持多投影仪边缘融合、几何校正，适配 CAVE 系统、LED 墙、穹顶投影等复杂显示拓扑
- **MPCDI/ICVFX 校准**：支持标准化投影校准格式，集成虚拟摄影棚（ICVFX）工作流
- **媒体输入输出**：通过 `DisplayClusterMedia` 和 `SharedMemoryMedia` 实现与外部设备的视频帧交换
- **电影管线集成**：`DisplayClusterMoviePipeline` 将 nDisplay 渲染集成到 Sequencer/电影渲染管线中
- **多用户协作**：`DisplayClusterMultiUser` 支持多人同时操控集群
- **Stage 监控**：实时监控集群节点状态和性能

**注意**：此插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用。

## 使用场景

- 你正在搭建 **CAVE 沉浸式显示系统** → 用 nDisplay 配置多面投影几何与边缘融合
- 你在制作 **LED 虚拟摄影棚（ICVFX）** → 用 nDisplay 配合 nDisplay Stage Monitor 管理 LED 墙渲染
- 你需要 **多台 PC 驱动超宽分辨率显示器或多台投影仪** → 用 nDisplay 将渲染分配到集群节点
- 你在做 **穹顶投影或环幕影院** → 用 nDisplay 的投影变形（Warp）和边缘混合（Blend）
- 你需要 **电影管线渲染多视角 EXR 多图层输出** → 用 `DisplayClusterMoviePipeline`
- 你想通过 **NDI/共享内存与外部视频设备交换帧** → 用 `DisplayClusterMedia`

## 蓝图用法

nDisplay 的蓝图 API 主要面向运行时集群事件交互和渲染控制，核心节点散布在 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `HandleEvent` | 处理集群二进制事件（同步模式切换、数据包处理） | `UDisplayClusterNetDriver` |
| `AddNodeConnection` | 向集群连接集合添加一个节点连接 | `UDisplayClusterNetDriver` |
| `RemoveNodeConnection` | 从集群连接集合移除一个节点连接 | `UDisplayClusterNetDriver` |
| `ProcessPacket` | 按序处理累积到指定 PacketId 的所有数据包 | `UDisplayClusterNetConnection` |

### 使用示例（蓝图描述）

nDisplay 的主要配置通过 `.ndisplay` 配置文件完成（通常使用 nDisplay Configurator 编辑器工具），而非纯蓝图构建。在蓝图中，你通常：

1. 在编辑器中通过 **nDisplay Configurator** 面板配置集群拓扑（节点数量、IP、视口、投影设置）
2. 使用 **nDisplay Cluster Event** 蓝图节点发送/接收自定义集群事件，在各节点间同步游戏逻辑
3. 通过 `UDisplayClusterNetConnection` 的属性（如 `ClusterId`、`NodeName`、`bNodeIsPrimary`）在蓝图中判断当前节点角色

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterNetDriver.h"
#include "DisplayClusterNetConnection.h"
```

### 基本用法 — 自定义网络驱动

nDisplay 的核心网络同步通过自定义 NetDriver 实现。`UDisplayClusterNetDriver` 继承自 `UIpNetDriver`，重写了 `TickDispatch` 和 `TickFlush` 来实现集群节点间的同步数据包处理：

```cpp
// DisplayClusterReplication 模块核心类
// UDisplayClusterNetDriver 继承 UIpNetDriver

// 获取当前 nDisplay NetDriver（如果集群已连接）
UDisplayClusterNetDriver* NetDriver = Cast<UDisplayClusterNetDriver>(
    UNetDriver::FindNetDriver(GetWorld())
);

if (NetDriver)
{
    // 添加一个集群节点连接
    UDisplayClusterNetConnection* NodeConnection = /* ... */;
    NetDriver->AddNodeConnection(NodeConnection);

    // 判断是否为主节点
    if (NodeConnection->bNodeIsPrimary)
    {
        // 主节点特殊逻辑
    }
}
```

*来源：`Public/DisplayClusterNetDriver.h`、`Public/DisplayClusterNetConnection.h`*

### 基本用法 — 集群事件处理

```cpp
// 通过 NetDriver 处理集群二进制事件
// 集群事件用于在节点间同步特定状态（如同步模式启动）
FDisplayClusterClusterEventBinary SyncEvent;
NetDriver->HandleEvent(SyncEvent);

// 自动生成集群命令事件用于同步
FDisplayClusterClusterEventBinary NetworkDriverSyncEvent;
TMap<uint32, int32> Parameters;
NetDriver->GenerateClusterCommandsEvent(
    NetworkDriverSyncEvent,
    UDisplayClusterNetDriver::NodeSyncEvent,  // 同步事件 ID
    Parameters
);
```

*来源：`Public/DisplayClusterNetDriver.h`*

### 进阶用法 — 集群连接管理

```cpp
// UDisplayClusterNetConnection 包含丰富的集群元数据
UDisplayClusterNetConnection* Conn = /* ... */;

// 节点标识
FString Name = Conn->NodeName;           // 从 URL 解析的节点名
FString Addr = Conn->NodeAddress;        // 节点 IP 地址
uint32  ClientId = Conn->ClientId;       // 集群客户端唯一 ID（NetConnection Challenge 的 HashString）
uint32  ClusterId = Conn->ClusterId;     // 集群唯一 ID（配置文件路径的 HashString）
uint32  NodesNum = Conn->ClusterNodesNum;// 集群节点总数
uint16  Port = Conn->NodePort;           // 二进制集群事件端口

// 集群状态
bool bPrimary = Conn->bNodeIsPrimary;        // 是否为主节点
bool bCluster = Conn->bIsClusterConnection;  // 是否为集群连接
bool bSync = Conn->bSynchronousMode;         // 是否处于同步模式

// 同步模式下按序处理数据包
Conn->ProcessPacket(/* PacketId */);
```

*来源：`Public/DisplayClusterNetConnection.h`*

### 进阶用法 — 数据包队列管理

```cpp
// NetDriver 内部维护多个连接队列
// 以下为内部架构（供扩展开发者参考）

// 未处理的数据包队列：connectionID -> packetID 双端队列
TMap<int32, TDeque<int32>> OutPacketsQueues;

// 已准备好进行复制的数据包：connectionID -> packetID
TMap<int32, int32> ReadyOutPackets;

// 集群复制状态 — 用于平衡各同步连接的 Actor 数量
FDisplayClusterReplicationState ClusterReplicationState;

// 通过集群事件通知其他节点已就绪
NetDriver->NotifyClusterAsReadyForSync(Conn->ClusterId);
```

*来源：`Public/DisplayClusterNetDriver.h`*

## Demo 示例

> nDisplay 的完整配置通常通过 nDisplay Configurator 编辑器工具和 `.ndisplay` 配置文件完成，运行时代码示例聚焦于集群事件监听。

```cpp
// DisplayClusterEventExample.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DisplayClusterClusterEvent.h"
#include "DisplayClusterEventExample.generated.h"

UCLASS()
class ADisplayClusterEventExample : public AActor
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    /** 发送自定义集群事件到所有节点 */
    UFUNCTION(BlueprintCallable)
    void BroadcastCustomEvent(const FString& EventName, const FString& EventPayload);

private:
    /** 集群事件回调 */
    void OnClusterEvent(const FDisplayClusterClusterEvent& Event);

    FDelegateHandle EventDelegateHandle;
};
```

```cpp
// DisplayClusterEventExample.cpp
#include "DisplayClusterEventExample.h"
#include "DisplayClusterSubsystem.h"
#include "IDisplayCluster.h"

void ADisplayClusterEventExample::BeginPlay()
{
    Super::BeginPlay();

    // 获取 nDisplay 子系统
    if (UDisplayClusterSubsystem* DCSubsystem = GetWorld()->GetSubsystem<UDisplayClusterSubsystem>())
    {
        // 注册集群事件监听（蓝图兼容事件）
        EventDelegateHandle = DCSubsystem->AddClusterEventListener(
            FOnClusterEvent::FDelegate::CreateUObject(this, &ADisplayClusterEventExample::OnClusterEvent)
        );
    }
}

void ADisplayClusterEventExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    // 清理事件监听
    if (UDisplayClusterSubsystem* DCSubsystem = GetWorld()->GetSubsystem<UDisplayClusterSubsystem>())
    {
        DCSubsystem->RemoveClusterEventListener(EventDelegateHandle);
    }
    Super::EndPlay(EndPlayReason);
}

void ADisplayClusterEventExample::BroadcastCustomEvent(
    const FString& EventName,
    const FString& EventPayload)
{
    // 仅主节点发送事件，其他节点接收
    if (IDisplayCluster::Get().GetOperationMode() == EDisplayClusterOperationMode::Cluster)
    {
        FDisplayClusterClusterEventJson JsonEvent;
        JsonEvent.Name = EventName;
        JsonEvent.Category = TEXT("CustomGameplay");
        JsonEvent.Type = EDisplayClusterClusterEventJsonType::PropertyChanged;
        JsonEvent.Parameters.Add(TEXT("Payload"), EventPayload);

        IDisplayCluster::Get().GetClusterMgr()->EmitClusterEvent(JsonEvent, true);
    }
}

void ADisplayClusterEventExample::OnClusterEvent(const FDisplayClusterClusterEvent& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received cluster event: %s"), *Event.Name);
}
```

## 模块依赖

nDisplay 依赖众多 UE 子系统。以下是**不常见**的特殊依赖（按模块分组）：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | 共享内存媒体传输的 D3D12 资源互操作 |
| `UnrealEd` | 多个模块依赖编辑器功能（投影编辑、媒体编辑、监控编辑等） |
| `EditorWidgets` | 编辑器 UI 组件 |
| `LevelEditor` | 关卡编辑器集成 |
| `MPCDI` | MPCDI 校准格式支持（通过 `ScalableMPCDI` 第三方库） |

> **注意**：`DisplayCluster`、`DisplayClusterMedia`、`DisplayClusterProjection`、`DisplayClusterShaders`、`DisplayClusterWarp` 等多个标为 Runtime 的模块实际依赖 `UnrealEd`，这意味着在打包构建中可能存在条件编译排除。使用者需要关注各模块的 `bUsePrecompiled` 和条件宏设置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 电影渲染图支持 EXR 多图层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 电影管线合并 WarpBlendAlpha 到 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 拓扑感知相机命名及 MPCDI/ICVFX 着色器不透明 Alpha 问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时正确处理非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**🟢 活跃维护**

nDisplay 是 Epic Games 持续投入的重点插件，最近的提交集中在 2026 年 5 月，更新频率高（一周内多次提交），涵盖：
- **功能增强**：电影管线 EXR 多图层支持、WarpBlend 模式合并
- **Bug 修复**：着色器 Alpha 问题、Gamma 处理、GUI 闪烁
- **渲染质量改进**：MPCDI/ICVFX 着色器优化

该插件自 2018 年创建以来持续维护，已从 UE4.20 发展到 UE5 最新版。作为虚拟制作（Virtual Production）和大型沉浸式显示的核心组件，Epic 对其投入稳定，推荐在需要集群渲染的项目中使用。

**注意事项**：
- 默认未启用（`EnabledByDefault: false`），需手动开启
- 源码规模巨大（1351 文件，29+ 模块），学习曲线较陡
- 多个 Runtime 模块依赖 UnrealEd，打包时需确认条件编译行为
- 支持平台仅 Win64 和 Linux

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)