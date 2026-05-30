# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质模板、编辑器工具） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 UE5 中用于**多 PC 集群同步渲染**的核心插件，解决的是"如何让多台电脑协同渲染同一场景，并将画面拼接/投影到复杂的物理显示结构上"的问题。

核心能力包括：

- **集群同步**：多台 PC（节点）通过 TCP 网络同步游戏时间、对象状态、输入事件，确保所有节点的场景模拟完全一致
- **多视口渲染**：每个集群节点可拥有多个独立视口（Viewport），每个视口有独立的投影策略（Projection Policy）用于将 3D 场景投射到物理屏幕上
- **投影变形混合（Warp & Blend）**：支持 MPCDI、EasyBlend 等多种投影数据格式，实现多投影仪画面的几何校正和边缘融合
- **ICVFX（In-Camera VFX）**：影视虚拟制片核心功能，支持内嵌画面（Inner Frustum）和外层画面（Outer Frustum）的分离渲染，用于 LED 墙虚拟拍摄
- **容错机制**：支持主节点故障转移（Failover），集群可自动选举新主节点继续运行
- **自定义状态同步**：提供分布式状态（Custom State）系统，允许用户自定义数据在集群间同步
- **Light Card 系统**：用于在 LED 墙上叠加可控光源卡片，调整虚拟环境照明
- **自动曝光统一**：跨集群节点的多视口自动曝光协调，避免相邻屏幕亮度不一致

简而言之：nDisplay 让你用多台电脑 + 多个显示器/投影仪，搭建一个大型的沉浸式显示环境，比如 CAVE 洞穴系统、LED 虚拟摄影棚、赛车模拟器多屏、主题公园飞行影院等。

## 使用场景

- 你在搭建 **LED 虚拟摄影棚**（ICVFX） → 用 nDisplay 管理内嵌画面渲染、色键（Chromakey）、边缘融合
- 你需要**多台 PC 同步渲染**一个场景并投射到 CAVE/穹顶/弧幕 → 用 nDisplay 的集群模式
- 你在做**多投影仪拼接**（投影映射） → 用 nDisplay 的 MPCDI 投影策略和 Warp&Blend
- 你需要**虚拟制片**中的实时预览 → 用 nDisplay 的编辑器预览功能
- 你在做**主题公园/展览装置**需要多屏同步播放 → 用 nDisplay 的集群同步和 Movie Pipeline 集成
- 你需要**多 PC 间发送自定义事件** → 用 nDisplay 的集群事件系统

## 蓝图用法

> **注意**：nDisplay 的蓝图 API 已从 `IDisplayClusterBlueprintAPI`（旧接口，UE 5.4 废弃）迁移至 `UDisplayClusterBlueprintLib` 静态函数库。以下列出的节点在蓝图搜索中位于 **"nDisplay"** 分类下。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetOperationMode` | 获取当前 nDisplay 操作模式（Cluster/Editor/Disabled） | `UDisplayClusterBlueprintLib` |
| `GetRootActor` | 获取当前 nDisplay 根 Actor | `UDisplayClusterBlueprintLib` |
| `GetNodeId` | 获取当前集群节点 ID | `UDisplayClusterBlueprintLib` |
| `GetActiveNodeIds` | 获取所有活跃集群节点 ID 列表 | `UDisplayClusterBlueprintLib` |
| `GetActiveNodesAmount` | 获取活跃节点数量 | `UDisplayClusterBlueprintLib` |
| `IsPrimary` | 当前节点是否为主节点 | `UDisplayClusterBlueprintLib` |
| `IsSecondary` | 当前节点是否为从节点 | `UDisplayClusterBlueprintLib` |
| `IsBackup` | 当前节点是否为备份节点 | `UDisplayClusterBlueprintLib` |
| `GetClusterRole` | 获取当前节点角色 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventJson` | 发送 JSON 格式集群事件 | `UDisplayClusterBlueprintLib` |
| `EmitClusterEventBinary` | 发送二进制集群事件 | `UDisplayClusterBlueprintLib` |
| `AddClusterEventListener` | 注册集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `RemoveClusterEventListener` | 移除集群事件监听器 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventJsonTo` | 向指定地址发送 JSON 事件 | `UDisplayClusterBlueprintLib` |
| `SendClusterEventBinaryTo` | 向指定地址发送二进制事件 | `UDisplayClusterBlueprintLib` |

### 相机组件节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInterpupillaryDistance` | 获取瞳距 | `UDisplayClusterCameraComponent` |
| `SetInterpupillaryDistance` | 设置瞳距 | `UDisplayClusterCameraComponent` |
| `GetSwapEyes` | 获取左右眼交换状态 | `UDisplayClusterCameraComponent` |
| `SetSwapEyes` | 设置左右眼交换 | `UDisplayClusterCameraComponent` |
| `ToggleSwapEyes` | 切换左右眼 | `UDisplayClusterCameraComponent` |
| `GetStereoOffset` | 获取立体偏移类型 | `UDisplayClusterCameraComponent` |
| `SetStereoOffset` | 设置立体偏移类型 | `UDisplayClusterCameraComponent` |

### ICVFX 相机节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetActualCineCameraComponent` | 获取实际引用的 CineCamera 组件 | `UDisplayClusterICVFXCameraComponent` |
| `IsICVFXEnabled` | 当前相机在此节点是否激活 | `UDisplayClusterICVFXCameraComponent` |
| `SetDepthOfFieldParameters` | 设置景深参数并更新补偿 LUT | `UDisplayClusterICVFXCameraComponent` |

### 使用示例（蓝图描述）

**发送集群事件**：
1. 创建一个 `FDisplayClusterClusterEventJson` 结构体，设置 `Category` 和 `Type`
2. 将事件数据写入 `Parameters` Map
3. 连接到 `EmitClusterEventJson` 节点，设置 `bPrimaryOnly` 为 false 以广播给所有节点
4. 在接收端，通过 `AddClusterEventListener` 注册监听器，或使用委托回调处理事件

**检测节点角色**：
1. 调用 `GetClusterRole` 获取角色枚举值
2. 分支判断：Primary（主节点控制画面输出）、Secondary（从节点跟随同步）、Backup（备份节点待命）

## C++ 用法

### 头文件引入

```cpp
// 核心模块
#include "DisplayClusterModule.h"
#include "IDisplayCluster.h"

// 集群管理
#include "Cluster/IDisplayClusterClusterManager.h"

// 渲染管理
#include "Render/IDisplayClusterRenderManager.h"

// 视口管理
#include "Render/Viewport/IDisplayClusterViewportManager.h"

// 投影策略
#include "Render/Projection/IDisplayClusterProjectionPolicy.h"

// 回调系统
#include "IDisplayClusterCallbacks.h"

// 自定义状态
#include "Cluster/CustomStates/DisplayClusterCustomStateDistributed.h"

// 根 Actor
#include "DisplayClusterRootActor.h"

// 相机组件
#include "Components/DisplayClusterCameraComponent.h"
#include "Components/DisplayClusterICVFXCameraComponent.h"
```

### 基本用法

**获取 nDisplay 模块并访问管理器**（来源：`Private/DisplayClusterModule.h`）：

```cpp
#include "IDisplayCluster.h"

// 检查 nDisplay 是否可用
if (IDisplayCluster::IsAvailable())
{
    // 获取模块实例
    IDisplayCluster& DisplayCluster = IDisplayCluster::Get();

    // 获取操作模式
    EDisplayClusterOperationMode Mode = DisplayCluster.GetOperationMode();

    // 访问集群管理器
    IDisplayClusterClusterManager* ClusterMgr = DisplayCluster.GetClusterMgr();
    if (ClusterMgr)
    {
        FString NodeId = ClusterMgr->GetNodeId();
        bool bIsPrimary = ClusterMgr->IsPrimary();
        EDisplayClusterNodeRole Role = ClusterMgr->GetClusterRole();
    }

    // 访问渲染管理器
    IDisplayClusterRenderManager* RenderMgr = DisplayCluster.GetRenderMgr();
    if (RenderMgr)
    {
        IDisplayClusterViewportManager* ViewportMgr = RenderMgr->GetViewportManager();
    }
}
```

**监听集群事件**（来源：`Public/Cluster/IDisplayClusterClusterManager.h`）：

```cpp
// 注册 JSON 事件监听
FOnClusterEventJsonListener JsonListener;
JsonListener.BindLambda([](const FDisplayClusterClusterEventJson& Event)
{
    UE_LOG(LogTemp, Log, TEXT("Received cluster event: Category=%s, Type=%s"),
        *Event.Category, *Event.Type);
});
ClusterMgr->AddClusterEventJsonListener(JsonListener);

// 发送 JSON 事件
FDisplayClusterClusterEventJson Event;
Event.Category = TEXT("MyCategory");
Event.Type = TEXT("MyType");
Event.Parameters.Add(TEXT("Key"), TEXT("Value"));
Event.bPrimaryOnly = false; // 广播给所有节点
ClusterMgr->EmitClusterEventJson(Event, false);

// 记得在结束时移除监听
ClusterMgr->RemoveClusterEventJsonListener(JsonListener);
```

**注册同步对象**（来源：`Public/Cluster/IDisplayClusterClusterManager.h`）：

```cpp
// 将对象注册到同步组，集群会自动同步其状态
// EDisplayClusterSyncGroup: PreTick, Tick, PostTick
ClusterMgr->RegisterSyncObject(MySyncObject, EDisplayClusterSyncGroup::PreTick);
```

### 进阶用法

**自定义分布式状态**（来源：`Public/Cluster/CustomStates/DisplayClusterCustomStateDistributed.h`）：

```cpp
// 创建一个自定义分布式状态，数据类型为 FVector
// 集群会自动在所有节点间同步此状态
TSharedPtr<TDistributedCustomState<FVector>> MyState = 
    TDistributedCustomState<FVector>::Create(FName("MyDistributedPosition"));

if (MyState.IsValid())
{
    // 设置本地数据（下一帧生效）
    MyState->SetData(FVector(100, 200, 300));

    // 读取本地数据
    const FVector& LocalData = MyState->GetData();

    // 读取特定节点的数据
    const FVector& NodeData = MyState->GetData(FName("Node2"));

    // 获取所有可用节点
    TSet<FName> Nodes = MyState->GetAvailableNodes();

    // 配置上游节点（自定义哪些节点的数据会传播到此状态）
    MyState->SetCustomUpstreamsEnabled(true);
    MyState->SetUpstreams({ FName("PrimaryNode") });
}
```

**注册自定义投影策略工厂**（来源：`Public/Render/IDisplayClusterRenderManager.h`）：

```cpp
// 实现自定义投影策略
class FMyProjectionPolicy : public IDisplayClusterProjectionPolicy
{
    // ... 实现接口方法
};

// 实现工厂
class FMyProjectionPolicyFactory : public IDisplayClusterProjectionPolicyFactory
{
public:
    virtual TSharedPtr<IDisplayClusterProjectionPolicy> Create(
        const FString& ViewportId,
        const FDisplayClusterConfigurationProjection& Configuration) override
    {
        return MakeShared<FMyProjectionPolicy>();
    }
};

// 注册
TSharedPtr<IDisplayClusterProjectionPolicyFactory> Factory = 
    MakeShared<FMyProjectionPolicyFactory>();
RenderMgr->RegisterProjectionPolicyFactory(TEXT("MyProjection"), Factory);
```

**使用回调系统**（来源：`Public/IDisplayClusterCallbacks.h`）：

```cpp
IDisplayClusterCallbacks& Callbacks = IDisplayCluster::Get().GetCallbacks();

// 会话开始回调
Callbacks.OnDisplayClusterStartSession().AddLambda([]()
{
    UE_LOG(LogTemp, Log, TEXT("nDisplay session started"));
});

// 帧渲染前回调
Callbacks.OnDisplayClusterPreWarp_RenderThread().AddLambda(
    [](FRHICommandListImmediate& RHICmdList, const IDisplayClusterViewportManagerProxy* Proxy)
    {
        // 在 warp blend 之前执行自定义渲染操作
    });

// 主节点变更回调（容错系统）
Callbacks.OnDisplayClusterFailoverPrimaryNodeChanged().AddLambda(
    [](const FString& NewPrimaryId)
    {
        UE_LOG(LogTemp, Warning, TEXT("New primary node: %s"), *NewPrimaryId);
    });
```

## Demo 示例

以下是一个最小的 nDisplay 集群事件发送与接收示例：

### MyDisplayClusterExample.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Cluster/IDisplayClusterClusterManager.h"
#include "MyDisplayClusterExample.generated.h"

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyDisplayClusterExample : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UFUNCTION(BlueprintCallable)
    void SendTestEvent(const FString& Message);

private:
    // JSON 事件监听委托
    FOnClusterEventJsonListener JsonEventListener;

    // 二进制事件监听委托
    FOnClusterEventBinaryListener BinaryEventListener;

    void OnJsonEventReceived(const FDisplayClusterClusterEventJson& Event);
    void OnBinaryEventReceived(const FDisplayClusterClusterEventBinary& Event);
};
```

### MyDisplayClusterExample.cpp

```cpp
#include "MyDisplayClusterExample.h"
#include "IDisplayCluster.h"

void UMyDisplayClusterExample::BeginPlay()
{
    Super::BeginPlay();

    if (!IDisplayCluster::IsAvailable())
    {
        return;
    }

    IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();
    if (!ClusterMgr)
    {
        return;
    }

    // 注册事件监听
    JsonEventListener.BindUObject(this, &UMyDisplayClusterExample::OnJsonEventReceived);
    ClusterMgr->AddClusterEventJsonListener(JsonEventListener);

    BinaryEventListener.BindUObject(this, &UMyDisplayClusterExample::OnBinaryEventReceived);
    ClusterMgr->AddClusterEventBinaryListener(BinaryEventListener);

    UE_LOG(LogTemp, Log, TEXT("nDisplay cluster event listeners registered. Node: %s, Role: %s"),
        *ClusterMgr->GetNodeId(),
        *UEnum::GetValueAsString(ClusterMgr->GetClusterRole()));
}

void UMyDisplayClusterExample::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (IDisplayCluster::IsAvailable())
    {
        IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();
        if (ClusterMgr)
        {
            ClusterMgr->RemoveClusterEventJsonListener(JsonEventListener);
            ClusterMgr->RemoveClusterEventBinaryListener(BinaryEventListener);
        }
    }

    Super::EndPlay(EndPlayReason);
}

void UMyDisplayClusterExample::SendTestEvent(const FString& Message)
{
    if (!IDisplayCluster::IsAvailable())
    {
        return;
    }

    IDisplayClusterClusterManager* ClusterMgr = IDisplayCluster::Get().GetClusterMgr();
    if (!ClusterMgr)
    {
        return;
    }

    FDisplayClusterClusterEventJson Event;
    Event.Category = TEXT("Test");
    Event.Type = TEXT("Message");
    Event.Parameters.Add(TEXT("NodeId"), ClusterMgr->GetNodeId());
    Event.Parameters.Add(TEXT("Message"), Message);
    Event.bPrimaryOnly = false; // 广播到所有节点

    ClusterMgr->EmitClusterEventJson(Event, false);

    UE_LOG(LogTemp, Log, TEXT("Sent cluster event: %s"), *Message);
}

void UMyDisplayClusterExample::OnJsonEventReceived(const FDisplayClusterClusterEventJson& Event)
{
    if (Event.Category == TEXT("Test") && Event.Type == TEXT("Message"))
    {
        FString SenderNodeId = Event.Parameters.FindRef(TEXT("NodeId"));
        FString ReceivedMessage = Event.Parameters.FindRef(TEXT("Message"));
        UE_LOG(LogTemp, Log, TEXT("Received cluster event from %s: %s"),
            *SenderNodeId, *ReceivedMessage);
    }
}

void UMyDisplayClusterExample::OnBinaryEventReceived(const FDisplayClusterClusterEventBinary& Event)
{
    // 处理二进制事件
}
```

## 模块依赖

nDisplay 插件内部模块众多，模块间依赖复杂。以下是使用该插件时需要关注的关键外部依赖：

| 模块 | 用途 |
|---|---|
| `D3D12RHI` | Direct3D 12 渲染硬件接口（DisplayClusterMedia、SharedMemoryMedia 依赖） |
| `MediaUtils` | 媒体框架工具（媒体输入输出支持） |
| `MPCDI` | MPCDI 投影数据格式支持（可选） |
| `OpenColorIO` | OCIO 色彩管理支持（可选） |
| `MovieRenderPipeline` | 影片渲染管线集成（MoviePipeline 模块依赖） |

> **注意**：该插件自身大量模块之间存在内部依赖。如仅使用基础集群功能，通常只需链接 `DisplayCluster` 和 `DisplayClusterConfiguration` 模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | MovieGraph 节点支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | MoviePipeline 合并 WarpBlendAlpha 模式到 WarpBlend |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 拓扑感知相机命名和 MPCDI 着色器不透明 alpha |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码回退时尊重非默认 DisplayGamma 设置 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2018 年 6 月（约 8 年前），是 UE 企业级功能的核心组件
- **更新频率**：极其活跃，每周都有多次功能性更新和 bug 修复
- **维护团队**：Epic Games 核心团队持续维护
- **已知问题**：插件默认关闭（`EnabledByDefault: false`），需手动启用；模块标记为 Runtime 但大量依赖 UnrealEd，说明混有编辑器功能
- **已废弃 API**：UE 5.4 时大量 API 从 `IDisplayClusterBlueprintAPI` 迁移至 `UDisplayClusterBlueprintLib`，旧接口带有 deprecated 标记
- **推荐使用**：如果你需要多 PC 集群渲染、ICVFX 虚拟制片或多投影仪场景，这是 UE5 中唯一且官方推荐的解决方案。非常成熟稳定，文档和社区资源丰富。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- 官方文档：[nDisplay Overview](https://docs.unrealengine.com/5.8/en-US/ndisplay-overview-in-unreal-engine/)（.uplugin 中未提供 DocsURL，链接为通用文档地址）
- [nDisplay 配置参考](https://docs.unrealengine.com/5.8/en-US/ndisplay-config-file-reference-for-unreal-engine/)