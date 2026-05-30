# DisplayClusterMonitor

> Support for synchronized clustered rendering using multiple PCs in mono or stereo（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 集群渲染监控 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-08 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

`DisplayClusterMonitor` 是 nDisplay 插件中的一个模块，专注于**集群渲染环境下的节点状态监控与实时媒体流传输**。

它解决了在多台 PC（节点）组成的同步渲染集群中，中央管理工具（或操作员）无法实时查看各个节点渲染状态和输出画面的问题。该模块通过建立一个基于 Message Bus 的通信网络，实现了以下核心功能：
1.  **节点发现与监控**：自动发现集群中的所有节点，并通过心跳机制监测其是否在线。
2.  **媒体流输出**：允许从集群中的每个节点捕获特定的渲染输出（如内镜头摄像机视图、视口、UI层、后缓冲等），并通过 NDI 等媒体协议流式传输出来，供外部监控设备（如大型调色台、监视墙）实时查看。
3.  **远程控制**：支持从监控端向指定的集群节点发送控制指令（如播放、暂停、停止、执行控制台命令）。

本质上，它是一个**集群渲染的“眼睛”和“遥控器”**，是大规模虚拟制片、大型LED墙、多投影融合等项目中不可或缺的运维和调试工具。

## 使用场景

-   **虚拟制片（Virtual Production）**：在 LED 墙拍摄现场，DIT（数字影像工程师）需要同时监控组成巨幕的每一块 LED 板（每个节点）的渲染画面，确保色彩、内容同步且无异常。通过 Monitor 模块将各节点的内镜头摄像机（ICVFX Camera）画面流式传输到监视器阵列。
-   **大型主题公园或展会**：驱动由数十个投影仪组成的复杂投影融合项目时，运维团队需要监控每个投影节点的输出画面，以检查融合带、校准状态或内容同步。
-   **天文馆/球幕影院**：监控多台渲染服务器输出的球幕画面，确保无缝拼接。
-   **分布式渲染调试**：开发者在调试 nDisplay 集群渲染时，无需在每个节点显示器前切换，直接从操作终端查看任意节点的视口输出。

## 蓝图用法

本模块的核心功能主要通过 C++ 的 `FDCMessenger` 类和一系列 USTRUCT 消息体实现。在蓝图中，主要操作这些**类型和消息结构体**。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `EDCObservableType` (枚举) | 定义了可被监控的资源类型：后缓冲、UI、视口、内镜头摄像机等。 | `DisplayClusterMonitorTypes.h` |
| `EDCMessengerRole` (枚举) | 定义了通信网络中端点的角色：`ObservablesProvider`（数据提供者）或 `Monitor`（监控者）。 | `DisplayClusterMonitorTypes.h` |
| `FDCEndpoint` (结构体) | 包含一个监控端点的所有信息：所在集群/节点、地址、最后活动时间。 | `DisplayClusterMonitorTypes.h` |
| `FDCMMessageBase` 及其子类 | 所有监控消息的基类及具体消息，如发现请求、心跳、会话控制消息等。 | `DisplayClusterMonitorTypes.h` |

### 使用示例（蓝图描述）

由于该模块没有直接暴露给蓝图的核心功能节点（如 `FDCMessenger` 不是 UObject），其蓝图交互主要围绕**数据定义**。
1.  **在蓝图中定义消息**：你可以创建继承自 `FDCMMessageBase` 的蓝图结构体，用于自定义监控协议。
2.  **处理事件**：在 C++ 层绑定 `FDCMessenger` 的委托（如 `OnEndpointJoined`、`OnMessage<FDCMMessage_YourCustom>()`）后，可以通过事件调度器将信息传递到蓝图界面进行显示。
3.  **配置设置**：`UDisplayClusterMonitorSettings` 是一个 UObject，可以在项目设置或蓝图中配置心跳间隔、无响应时间阈值等运行时参数。

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMonitorTypes.h"
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorProviderBase.h"
#include "DisplayClusterMonitorSettings.h"
```

### 基本用法

以下示例展示如何创建一个简单的监控客户端（Monitor 角色），用于发现集群节点并监听其状态。
*(来源：基于 `FDCMessenger` 和 `FDisplayClusterMonitorProviderBase` 类的设计模式推断)*

```cpp
// MyMonitorClient.h
#pragma once
#include "DisplayClusterMonitorMessenger.h"

class FMyMonitorClient
{
public:
    bool Initialize();
    void Shutdown();

private:
    void HandleEndpointJoined(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint);
    void HandleEndpointTimeout(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint);

private:
    TUniquePtr<UE::nDisplay::Monitor::FDCMessenger> Messenger;
};
```

```cpp
// MyMonitorClient.cpp
#include "MyMonitorClient.h"

bool FMyMonitorClient::Initialize()
{
    Messenger = MakeUnique<UE::nDisplay::Monitor::FDCMessenger>();
    
    // 启动 Messenger，角色为 Monitor
    if (!Messenger->Start(TEXT("MyMonitor"), { UE::nDisplay::Monitor::EDCMessengerRole::Monitor }))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to start Monitor Messenger"));
        return false;
    }

    // 绑定事件委托
    Messenger->OnEndpointJoined.AddRaw(this, &FMyMonitorClient::HandleEndpointJoined);
    Messenger->OnEndpointTimeout.AddRaw(this, &FMyMonitorClient::HandleEndpointTimeout);

    UE_LOG(LogTemp, Log, TEXT("Monitor client started successfully"));
    return true;
}

void FMyMonitorClient::Shutdown()
{
    if (Messenger)
    {
        Messenger->Stop(TEXT("Client shutdown"));
    }
}

void FMyMonitorClient::HandleEndpointJoined(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint)
{
    UE_LOG(LogTemp, Log, TEXT("Endpoint joined: Node '%s' on host '%s'"),
        *Endpoint.Residence.NodeName, *Endpoint.Residence.Hostname);
}

void FMyMonitorClient::HandleEndpointTimeout(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint)
{
    UE_LOG(LogTemp, Warning, TEXT("Endpoint timeout: Node '%s' on host '%s'"),
        *Endpoint.Residence.NodeName, *Endpoint.Residence.Hostname);
}
```

### 进阶用法

向已发现的特定节点发送一个请求，查询其可用的可监控资源列表。
*(来源：基于 `FDCMessenger::Send` 和 `FDCMMessage_NodeObservablesRequest` 的设计推断)*

```cpp
// 在 FMyMonitorClient 类中添加成员
void RequestObservablesFromEndpoint(const UE::nDisplay::Monitor::FDCEndpoint& TargetEndpoint);

void FMyMonitorClient::RequestObservablesFromEndpoint(const UE::nDisplay::Monitor::FDCEndpoint& TargetEndpoint)
{
    if (!Messenger || !Messenger->IsRunning())
    {
        return;
    }

    // 构造请求消息
    UE::nDisplay::Monitor::FDCMMessage_NodeObservablesRequest RequestMsg;

    // 发送给特定节点的地址
    TArray<FMessageAddress> Recipients = { TargetEndpoint.Address };
    Messenger->Send(Recipients, RequestMsg);

    // 同时，需要在 Messenger 上绑定对此请求的响应处理
    // Messenger->OnMessage<UE::nDisplay::Monitor::FDCMMessage_NodeObservablesResponse>()
    //     .AddRaw(this, &FMyMonitorClient::HandleObservablesResponse);
}
```

## Demo 示例

一个最小的、可运行的 `DisplayClusterMonitorProvider`，用于暴露当前进程的后缓冲（Backbuffer）供监控。
*(注意：此示例仅为演示结构，实际集成到 nDisplay 会话需要更多回调和数据源。)*

```cpp
// MySimpleProvider.h
#pragma once
#include "DisplayClusterMonitorProviderBase.h"
#include "DisplayClusterMonitorTypes.h"

class FMySimpleProvider : public UE::nDisplay::Monitor::FDisplayClusterMonitorProviderBase
{
public:
    virtual FString GetMessengerName() const override;
    virtual bool Start() override;
    virtual void Stop() override;

private:
    // 模拟的资源列表更新和会话管理函数
    void UpdateResources();
    // ... 其他私有辅助函数
};
```

```cpp
// MySimpleProvider.cpp
#include "MySimpleProvider.h"
#include "DisplayClusterMonitorMessenger.h"

FString FMySimpleProvider::GetMessengerName() const
{
    return TEXT("SimpleBackbufferProvider");
}

bool FMySimpleProvider::Start()
{
    // 1. 启动基类的 Messenger
    if (!Super::Start())
    {
        return false;
    }

    // 2. 设置角色为数据提供者
    if (!Messenger->Start(GetMessengerName(), { UE::nDisplay::Monitor::EDCMessengerRole::ObservablesProvider }))
    {
        return false;
    }

    // 3. (在实际插件中) 在这里绑定处理来自 Monitor 的各种请求消息的委托
    // 例如：Messenger->OnMessage<FDCMMessage_NodeObservablesRequest>().AddRaw(...)

    // 4. 开始模拟资源评估
    // GetWorld()->GetTimerManager().SetTimer(...)
    UpdateResources();

    return true;
}

void FMySimpleProvider::Stop()
{
    // 停止计时器等...
    Super::Stop();
}

void FMySimpleProvider::UpdateResources()
{
    // 模拟：每次“评估”时，我们只有一个固定的“后缓冲”资源
    UE::nDisplay::Monitor::FDCMData_ObservableInfo BackbufferInfo;
    BackbufferInfo.Type = UE::nDisplay::Monitor::EDCObservableType::Backbuffer;
    BackbufferInfo.Id = FGuid::NewGuid(); // 在实际中，这应该是稳定的ID
    BackbufferInfo.Name = TEXT("Main Backbuffer");
    BackbufferInfo.Resolution = GEngine->GameViewport->Viewport->GetSizeXY();

    // 构造更新消息
    UE::nDisplay::Monitor::FDCMData_NodeObservables ObservablesUpdate;
    // 第一次是“添加”
    ObservablesUpdate.ObservablesAdded.Add(BackbufferInfo);

    // 广播更新通知给所有监控者
    UE::nDisplay::Monitor::FDCMMessage_NodeObservablesNotification NotificationMsg;
    NotificationMsg.Observables = ObservablesUpdate;

    if (Messenger)
    {
        // 使用 Broadcast 发送给所有监控端点
        Messenger->Broadcast(MoveTemp(NotificationMsg));
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MessageBus` | 用于集群节点间的异步消息通信，是整个 Monitor 模块的通信基石。 |
| `Media` / `MediaUtils` | 提供 `UMediaCapture`, `UMediaOutput` 等媒体捕获和输出的基础设施。 |
| `DisplayCluster` | nDisplay 核心插件，提供集群节点管理、视口代理 (`IDisplayClusterViewport`) 等必要接口。 |
| `NDIMedia` (可选) | 如果使用 NDI 作为流媒体传输协议，则需要依赖此模块。 |

**注意**：`Build.cs` 中列出的 `UnrealEd` 依赖通常仅用于编辑器扩展（如 Monitor 面板的 UI），对于纯运行时监控功能，可能并不需要。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为 MovieGraph 添加多层 EXR 支持。 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并了 MoviePipeline 中的扭曲混合 Alpha 模式。 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复了 MRG 中的拓扑感知摄像机命名，以及 MPCDI/ICVFX 着色器中的不透明 Alpha 问题。 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 修复了在输出帧编码回退时未使用非默认 DisplayGamma 的问题。 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复了当 GUI 纹理尺寸小于视口尺寸时的闪烁问题。 |

### 维护评价

**活跃维护**。

该插件模块自 2018 年创建以来持续更新，最近的提交记录（2026 年 5 月）表明 Epic Games 仍在积极开发和修复问题。近期更新主要集中在：
1.  **功能增强**：如为 MovieGraph 添加新特性。
2.  **Bug 修复**：修复了着色器、渲染、流媒体传输等多个方面的具体问题，显示了对其在复杂项目中应用稳定性的关注。
3.  **技术整合**：与 Movie Pipeline、MRG（Multi-Resolution Graphics）等其他 UE 子系统的协同工作。

**推荐使用**：对于需要多 PC 同步渲染和实时监控的大型虚拟制片或沉浸式项目，nDisplay 及其 Monitor 模块是官方且功能完备的解决方案。它仍在积极维护，能够适应最新的引擎功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/ndisplay-in-unreal-engine/) （nDisplay 总体文档）
- 测试用例：未在提供的文件路径中直接发现明确的 `DisplayClusterMonitor` 测试文件，通常集成在 nDisplay 的整体自动化测试中。