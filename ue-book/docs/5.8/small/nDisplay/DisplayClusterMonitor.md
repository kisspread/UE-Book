# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | nDisplay 集群渲染 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、材质、蓝图） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

## 用途

nDisplay 是 Unreal Engine 的集群渲染解决方案，用于将单个 UE 应用程序的渲染输出同步到多台 PC 上的多个显示设备。它支持单目和立体渲染，适用于大型沉浸式显示环境，如 CAVE（洞穴自动虚拟环境）、穹顶投影、LED 墙和多屏幕设置。

该插件的核心功能包括：
- **同步渲染**：确保所有集群节点在同一时间点渲染相同的帧，避免视觉撕裂
- **多投影支持**：处理复杂的投影几何和变形（warp/blend）
- **媒体输出**：提供将渲染内容流式传输到外部设备的能力
- **集群监控**：提供对集群节点状态和渲染资源的实时监控
- **远程控制**：允许通过消息总线对集群进行配置和控制
- **电影渲染管线集成**：支持使用 nDisplay 进行离线渲染

## 使用场景

- **虚拟制片**：使用 LED 墙显示实时背景，演员在前景表演
- **主题公园娱乐**：在多台投影仪上同步渲染 360 度或穹顶内容
- **科学可视化**：在 CAVE 环境中进行大规模数据可视化
- **大型活动**：在多个显示屏上同步显示实时内容
- **电影级离线渲染**：使用集群进行高分辨率、高质量的最终帧渲染

## 蓝图用法

由于 nDisplay 主要是一个配置和管理系统，其蓝图 API 主要集中在监控和控制方面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `StartSession` | 启动对指定可观察对象的监控会话 | `FDCMessenger` |
| `StopSession` | 停止监控会话 | `FDCMessenger` |
| `SendCommand` | 向集群节点发送控制命令 | `FDCMessenger` |
| `GetDiscoveredEndpoints` | 获取已发现的所有集群端点 | `FDCMessenger` |

### 使用示例（蓝图描述）

要监控特定视口的渲染输出：
1. 获取 `UDisplayClusterMonitorSettings` 实例
2. 通过消息总线连接到集群监控端点
3. 发送 `NodeObservablesRequest` 消息获取可用资源列表
4. 发送 `StartSessionRequest` 开始接收指定资源的媒体流
5. 在接收到媒体数据后进行处理

## C++ 用法

### 头文件引入

```cpp
#include "DisplayClusterMonitorModule.h"
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"
```

### 基本用法

建立集群监控连接和基础消息处理：

```cpp
// 来源: DisplayClusterMonitorMessenger.h
using namespace UE::nDisplay::Monitor;

// 创建并启动监控信使
FDCMessenger Messenger;
TSet<EDCMessengerRole> Roles;
Roles.Add(EDCMessengerRole::Monitor);

if (Messenger.Start(TEXT("MyMonitor"), Roles))
{
    // 监听端点发现
    Messenger.OnEndpointJoined.AddLambda([](const FDCEndpoint& Endpoint)
    {
        UE_LOG(LogTemp, Log, TEXT("新端点加入: %s"), *Endpoint.Endpoint.Name);
    });

    // 监听心跳超时
    Messenger.OnEndpointTimeout.AddLambda([](const FDCEndpoint& Endpoint)
    {
        UE_LOG(LogTemp, Warning, TEXT("端点超时: %s"), *Endpoint.Endpoint.Name);
    });

    // 注册自定义消息处理
    Messenger.OnMessage<FDCMMessage_NodeObservablesNotification>().AddLambda(
        [](const FDCEndpoint& Endpoint, const FDCMMessage_NodeObservablesNotification& Msg)
    {
        // 处理可观察对象更新
        for (const FDCMData_ObservableInfo& Info : Msg.Observables.ObservablesAdded)
        {
            UE_LOG(LogTemp, Log, TEXT("新增可观察对象: %s"), *Info.Name);
        }
    });
}
```

### 进阶用法

控制远程节点的渲染输出：

```cpp
// 来源: DisplayClusterMonitorProviderMedia.h
// 获取媒体提供者
FDisplayClusterMonitorProviderMedia MediaProvider;

// 请求所有可用的可观察对象
FDCMMessage_NodeObservablesRequest Request;
TArray<FMessageAddress> Recipients;
// 填充目标地址...

MediaProvider.GetMessenger()->Send(Recipients, Request);

// 开始特定视口的捕获会话
FDCMMessage_StartSessionRequest StartRequest;
StartRequest.ObservableId = SomeObservableGuid;
MediaProvider.GetMessenger()->Send(Recipients, StartRequest);

// 发送播放/暂停控制命令
FDCMMessage_ObservableControlRequest ControlRequest;
ControlRequest.ObservableId = SomeObservableGuid;
ControlRequest.Command = EDCControlCommand::Play;
MediaProvider.GetMessenger()->Send(Recipients, ControlRequest);
```

## Demo 示例

一个完整的集群监控客户端示例：

```cpp
// DisplayClusterMonitorClient.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"

class FDisplayClusterMonitorClient
{
public:
    FDisplayClusterMonitorClient();
    ~FDisplayClusterMonitorClient();

    bool Initialize(const FString& ClientName);
    void Shutdown();
    
    void RequestAvailableResources();
    void StartMonitoring(const FGuid& ObservableId);
    void StopMonitoring(const FGuid& ObservableId);

private:
    void OnEndpointDiscovered(const FDCEndpoint& Endpoint);
    void OnResourcesReceived(const FDCEndpoint& Endpoint, const FDCMMessage_NodeObservablesResponse& Response);
    void OnSessionStarted(const FDCEndpoint& Endpoint, const FDCMMessage_StartSessionResponse& Response);
    void OnMediaDataReceived(const FDCEndpoint& Endpoint, const FDCMMessage_NodeObservablesNotification& Notification);

    UE::nDisplay::Monitor::FDCMessenger Messenger;
    TArray<FGuid> ActiveSessions;
};
```

```cpp
// DisplayClusterMonitorClient.cpp
#include "DisplayClusterMonitorClient.h"
#include "DisplayClusterMonitorLog.h"

FDisplayClusterMonitorClient::FDisplayClusterMonitorClient()
{
}

FDisplayClusterMonitorClient::~FDisplayClusterMonitorClient()
{
    Shutdown();
}

bool FDisplayClusterMonitorClient::Initialize(const FString& ClientName)
{
    TSet<UE::nDisplay::Monitor::EDCMessengerRole> Roles;
    Roles.Add(UE::nDisplay::Monitor::EDCMessengerRole::Monitor);
    
    if (!Messenger.Start(ClientName, Roles))
    {
        UE_LOG(LogDisplayClusterMonitor, Error, TEXT("Failed to start monitor messenger"));
        return false;
    }

    // 绑定事件处理
    Messenger.OnEndpointJoined.AddRaw(this, &FDisplayClusterMonitorClient::OnEndpointDiscovered);
    
    Messenger.OnMessage<UE::nDisplay::Monitor::FDCMMessage_NodeObservablesResponse>().AddRaw(
        this, &FDisplayClusterMonitorClient::OnResourcesReceived);
    
    Messenger.OnMessage<UE::nDisplay::Monitor::FDCMMessage_StartSessionResponse>().AddRaw(
        this, &FDisplayClusterMonitorClient::OnSessionStarted);
    
    Messenger.OnMessage<UE::nDisplay::Monitor::FDCMMessage_NodeObservablesNotification>().AddRaw(
        this, &FDisplayClusterMonitorClient::OnMediaDataReceived);

    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Monitor client initialized: %s"), *ClientName);
    return true;
}

void FDisplayClusterMonitorClient::Shutdown()
{
    // 停止所有活动会话
    for (const FGuid& SessionId : ActiveSessions)
    {
        UE::nDisplay::Monitor::FDCMMessage_StopSessionRequest StopRequest;
        StopRequest.ObservableId = SessionId;
        
        TArray<FMessageAddress> Recipients;
        // 填充目标地址...
        Messenger.Send(Recipients, StopRequest);
    }
    
    ActiveSessions.Empty();
    Messenger.Stop(TEXT("Client shutdown"));
}

void FDisplayClusterMonitorClient::RequestAvailableResources()
{
    UE::nDisplay::Monitor::FDCMMessage_NodeObservablesRequest Request;
    
    // 向所有已发现的端点发送请求
    TArray<FMessageAddress> Recipients;
    for (const auto& Endpoint : Messenger.GetDiscoveredEndpoints())
    {
        Recipients.Add(Endpoint.Address);
    }
    
    if (Recipients.Num() > 0)
    {
        Messenger.Send(Recipients, Request);
        UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Requested available resources from %d endpoints"), Recipients.Num());
    }
}

void FDisplayClusterMonitorClient::StartMonitoring(const FGuid& ObservableId)
{
    UE::nDisplay::Monitor::FDCMMessage_StartSessionRequest Request;
    Request.ObservableId = ObservableId;
    
    TArray<FMessageAddress> Recipients;
    // 填充目标地址...
    Messenger.Send(Recipients, Request);
    
    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Started monitoring session: %s"), *ObservableId.ToString());
}

void FDisplayClusterMonitorClient::StopMonitoring(const FGuid& ObservableId)
{
    UE::nDisplay::Monitor::FDCMMessage_StopSessionRequest Request;
    Request.ObservableId = ObservableId;
    
    TArray<FMessageAddress> Recipients;
    // 填充目标地址...
    Messenger.Send(Recipients, Request);
    
    ActiveSessions.Remove(ObservableId);
    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Stopped monitoring session: %s"), *ObservableId.ToString());
}

void FDisplayClusterMonitorClient::OnEndpointDiscovered(const FDCEndpoint& Endpoint)
{
    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Discovered endpoint: %s (%s)"), 
        *Endpoint.Endpoint.Name, *Endpoint.Residence.Hostname);
}

void FDisplayClusterMonitorClient::OnResourcesReceived(
    const FDCEndpoint& Endpoint, 
    const FDCMMessage_NodeObservablesResponse& Response)
{
    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Received resources from %s:"), *Endpoint.Endpoint.Name);
    
    for (const auto& Observable : Response.Observables.ObservablesAdded)
    {
        UE_LOG(LogDisplayClusterMonitor, Log, TEXT("  - %s [%s] %dx%d"),
            *Observable.Name,
            *UEnum::GetValueAsString(Observable.Type),
            Observable.Resolution.X, Observable.Resolution.Y);
    }
}

void FDisplayClusterMonitorClient::OnSessionStarted(
    const FDCEndpoint& Endpoint, 
    const FDCMMessage_StartSessionResponse& Response)
{
    if (Response.Result == UE::nDisplay::Monitor::EDCRequestResult::Ok)
    {
        ActiveSessions.Add(Response.ObservableId);
        UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Session started: %s"), *Response.ObservableId.ToString());
    }
    else
    {
        UE_LOG(LogDisplayClusterMonitor, Warning, TEXT("Failed to start session: %s"), *Response.ObservableId.ToString());
    }
}

void FDisplayClusterMonitorClient::OnMediaDataReceived(
    const FDCEndpoint& Endpoint, 
    const FDCMMessage_NodeObservablesNotification& Notification)
{
    // 处理接收到的媒体数据
    for (const auto& Observable : Notification.Observables.ObservablesAdded)
    {
        UE_LOG(LogDisplayClusterMonitor, Verbose, TEXT("New observable data: %s"), *Observable.Name);
    }
    
    for (const auto& Observable : Notification.Observables.ObservablesUpdated)
    {
        UE_LOG(LogDisplayClusterMonitor, Verbose, TEXT("Updated observable: %s"), *Observable.Name);
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成和资产编辑功能 |
| `D3D12RHI` | DirectX 12 渲染硬件接口，用于媒体输出 |
| `MediaUtils` | 媒体捕获和输出工具 |

**注意**：nDisplay 插件包含大量模块，不同功能需要不同的依赖。DisplayClusterMonitor 模块主要依赖 UnrealEd 用于编辑器集成。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support. | 为电影图和 nDisplay 添加 EXR 多层支持 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并电影管线中的变形混合模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复拓扑感知相机命名和着色器中的不透明度问题 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 在输出帧编码回退时正确处理非默认显示伽马值 |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理尺寸小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** - nDisplay 是 Epic Games 持续维护的核心技术之一：

1. **创建时间**：2018 年创建，已有 7 年历史，是成熟的工业级解决方案
2. **更新频率**：非常活跃，2026 年 5 月有多次重要更新，表明持续开发中
3. **功能范围**：功能不断扩展，包括电影管线集成、新的投影技术、性能优化等
4. **平台支持**：支持 Win64 和 Linux，适用于各种工业部署环境
5. **社区使用**：广泛应用于虚拟制片、主题公园、科学可视化等领域

**推荐使用**：对于需要多机同步渲染、大型显示墙或虚拟制片的项目，nDisplay 是官方推荐的解决方案。虽然需要手动启用（`EnabledByDefault: false`），但功能完整、文档完善，适合生产环境使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/nDisplay-in-Unreal-Engine/)