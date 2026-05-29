# nDisplay

> Support for synchronized clustered rendering using multiple PCs in mono or stereo

| 属性 | 值 |
|---|---|
| 中文名 | 集群显示 |
| 分类 | Misc |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产、着色器、蓝图资产） |
| 模块 | `DisplayCluster` (Runtime), `DisplayClusterColorGrading` (Runtime), `DisplayClusterConfiguration` (Runtime), `DisplayClusterConfigurator` (Runtime), `DisplayClusterDetails` (Runtime), `DisplayClusterEditor` (Runtime), `DisplayClusterFillDerivedDataCache` (Runtime), `DisplayClusterLightCardEditor` (Runtime), `DisplayClusterLightCardEditorShaders` (Runtime), `DisplayClusterMedia` (Runtime), `DisplayClusterMediaEditor` (Runtime), `DisplayClusterMessageInterception` (Runtime), `DisplayClusterMonitor` (Runtime), `DisplayClusterMonitorEditor` (Runtime), `DisplayClusterMoviePipeline` (Runtime), `DisplayClusterMoviePipelineEditor` (Runtime), `DisplayClusterMultiUser` (Runtime), `DisplayClusterOperator` (Runtime), `DisplayClusterProjection` (Runtime), `DisplayClusterRemoteControlInterceptor` (Runtime), `DisplayClusterReplication` (Runtime), `DisplayClusterScenePreview` (Runtime), `DisplayClusterShaders` (Runtime), `DisplayClusterStageMonitoring` (Runtime), `DisplayClusterTests` (Runtime), `DisplayClusterWarp` (Runtime), `SharedMemoryMedia` (Runtime), `SharedMemoryMediaEditor` (Runtime), `ScalableMPCDI` (External) |
| 实验性 | 否 |
| 创建时间 | 2018-06-07 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay) | |

---

## 本文档范围

nDisplay 是一个超大型插件（1351+ 源文件，29 个模块）。本文档作为汇总页，重点详细覆盖 **DisplayClusterMonitor** 子模块，该模块负责集群节点间的实时画面监控与媒体流推送。

各子模块列表见上方属性表。如需其他子模块的详细文档，请按模块拆分阅读。

---

## 用途

nDisplay 解决的核心问题是：**如何用多台 PC 协同渲染一个超大画面（LED 墙、CAVE、穹顶投影等），并保持帧同步。**

典型场景包括：
- 虚拟制片 LED 墙（ICVFX）：多台渲染节点驱动巨幅 LED 屏幕，主节点负责同步
- 穹顶/CAVE 沉浸式体验：多通道投影拼接
- 主题公园大型 LED 装置
- 赛车/飞行模拟器多屏幕环绕

**DisplayClusterMonitor 模块**在此架构中负责：
- **画面监控**：从每个集群节点的各类视口（后缓冲、UI 层、ICVFX 相机、相机瓦片）采集渲染输出
- **NDI 流推送**：将采集到的画面通过 NDI 协议流式推送到网络，供外部监控软件（如 OBS、vMix）实时查看
- **集群通信**：基于 Unreal MessageBus 实现节点间的发现、心跳、指令分发
- **远程控制**：支持从监控端发送控制命令（Play/Pause/Stop）和控制台命令

## 使用场景

- 你在搭建 LED 墙虚拟制片影棚，需要实时监控每个渲染节点的输出画面 → 使用 nDisplay + DisplayClusterMonitor
- 你需要在运维工作站上远程查看集群中每台渲染机的后缓冲或特定 ICVFX 相机画面 → 使用 DisplayClusterMonitor 的 NDI 流推送
- 你需要统一管理集群节点，检测节点崩溃/无响应 → 使用 DisplayClusterMonitor 的心跳机制
- 你需要远程向特定集群节点发送控制台命令 → 使用 DisplayClusterMonitor 的 Messenger 功能

---

## 蓝图用法

DisplayClusterMonitor 模块主要面向 C++ 和编辑器使用，直接暴露的蓝图节点较少。但以下枚举和结构体可通过蓝图访问：

### 核心枚举（BlueprintType）

| 枚举 | 说明 | 用途 |
|---|---|---|
| `EDCObservableType` | 可观察资源类型 | 区分 Backbuffer / UI / Viewport / ICVFXCamera / ICVFXCameraTile |
| `EDCMessengerRole` | Messenger 角色 | 区分 ObservablesProvider（数据提供者）和 Monitor（监控端） |
| `EDCControlCommand` | 控制命令 | Play / Pause / Stop |
| `EDCRequestResult` | 请求结果 | Ok / Fail / NoResult |

### 核心结构体（BlueprintType）

| 结构体 | 说明 |
|---|---|
| `FDCMData_ResidenceDescriptor` | 集群节点驻留信息（ClusterId、NodeId、NodeName、Hostname、是否主节点等） |
| `FDCMData_EndpointDescriptor` | 端点描述（GUID、名称、角色集合） |
| `FDCEndpoint` | 完整端点信息（驻留描述 + 端点描述 + 地址 + 最后活跃时间） |
| `FDCMData_ObservableInfo` | 可观察资源信息（类型、ID、名称、分辨率、瓦片位置等） |

### 编辑器设置

在 **项目设置 → nDisplay → Cluster Monitor** 中可配置：

| 设置 | 说明 | 默认值 |
|---|---|---|
| `HeartbeatInterval` | 心跳脉冲间隔（秒） | 3.0 |
| `UnresponsiveTimeThreshold` | 无响应超时阈值（秒） | 15.0 |
| `bAddNewObservablesToFront` | 新视口是否插入到布局开头 | true |
| `ViewportsInRow` | 每行显示的视口数量 | 2 |
| `bUseFixedViewportHeight` | 是否使用固定视口高度 | true |
| `FixedViewportHeight` | 固定视口高度（像素） | 500 |

---

## C++ 用法

### 头文件引入

```cpp
// Messenger 及通信类型
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"
#include "DisplayClusterMonitorSettings.h"

// Observable 接口
#include "MediaObservables/IMediaObservable.h"
```

### 基本用法 —— 创建 Messenger 并监听消息

DisplayClusterMonitor 的核心通信基于 `FDCMessenger` 类。以下示例展示如何创建一个 Monitor 角色的 Messenger 并注册消息回调。

```cpp
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"

using namespace UE::nDisplay::Monitor;

// 创建 Messenger
TUniquePtr<FDCMessenger> Messenger = MakeUnique<FDCMessenger>();

// 启动 Messenger，指定名称和角色
TSet<EDCMessengerRole> Roles;
Roles.Add(EDCMessengerRole::Monitor);
Messenger->Start(TEXT("MyMonitor"), Roles);

// 监听节点可观察资源变更通知
Messenger->OnMessage<FDCMMessage_NodeObservablesNotification>()
    .AddLambda([](const FDCEndpoint& Endpoint, const FDCMMessage_NodeObservablesNotification& Msg)
    {
        // 处理新增的可观察资源
        for (const FDCMData_ObservableInfo& Info : Msg.Observables.ObservablesAdded)
        {
            UE_LOG(LogDisplayClusterMonitor, Log, TEXT("New observable: %s (%s)"),
                *Info.Name, *LexToString(Info.Type));
        }
    });

// 监听端点加入事件
Messenger->OnEndpointJoined.AddLambda([](const FDCEndpoint& Endpoint)
{
    UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Endpoint joined: %s from %s"),
        *Endpoint.Endpoint.Name, *Endpoint.Residence.Hostname);
});

// 监听端点超时（节点可能崩溃）
Messenger->OnEndpointTimeout.AddLambda([](const FDCEndpoint& Endpoint)
{
    UE_LOG(LogDisplayClusterMonitor, Warning, TEXT("Endpoint unresponsive: %s"),
        *Endpoint.Endpoint.Name);
});
```

**来源**：`Source/DisplayClusterMonitor/Public/DisplayClusterMonitorMessenger.h`

### 基本用法 —— 请求可观察资源列表并开始监控会话

```cpp
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"

using namespace UE::nDisplay::Monitor;

// 向某个集群节点请求可观察资源列表
FDCMMessage_NodeObservablesRequest Request;
TArray<FMessageAddress> Recipients;
Recipients.Add(TargetEndpoint.Address);
Messenger->Send(Recipients, Request);

// 处理响应
Messenger->OnMessage<FDCMMessage_NodeObservablesResponse>()
    .AddLambda([this](const FDCEndpoint& Endpoint, const FDCMMessage_NodeObservablesResponse& Response)
    {
        for (const FDCMData_ObservableInfo& Info : Response.Observables.ObservablesAdded)
        {
            UE_LOG(LogDisplayClusterMonitor, Log,
                TEXT("Observable: %s, Type: %s, Resolution: %dx%d"),
                *Info.Name,
                *LexToString(Info.Type),
                Info.Resolution.X, Info.Resolution.Y);
        }
    });

// 开始某个可观察资源的监控会话
FDCMMessage_StartSessionRequest StartRequest;
StartRequest.ObservableId = ObservableGuid;
Messenger->Send(Recipients, StartRequest);

// 处理会话启动结果
Messenger->OnMessage<FDCMMessage_StartSessionResponse>()
    .AddLambda([](const FDCEndpoint& Endpoint, const FDCMMessage_StartSessionResponse& Response)
    {
        if (Response.Result == EDCRequestResult::Ok)
        {
            UE_LOG(LogDisplayClusterMonitor, Log, TEXT("Session started for observable %s"),
                *Response.ObservableId.ToString());
        }
    });
```

**来源**：`Source/DisplayClusterMonitor/Public/DisplayClusterMonitorTypes.h`

### 进阶用法 —— 自定义消息类型

Messenger 支持发送自定义消息类型，需继承 `FDCMMessage`：

```cpp
// 定义自定义消息
USTRUCT(BlueprintType)
struct FDCMMessage_CustomCommand : public FDCMMessage
{
    GENERATED_BODY()

    UPROPERTY()
    FString Payload;

    UPROPERTY()
    float Value = 0.f;
};

// 注册自定义消息回调
Messenger->OnMessage<FDCMMessage_CustomCommand>()
    .AddLambda([](const FDCEndpoint& Endpoint, const FDCMMessage_CustomCommand& Msg)
    {
        UE_LOG(LogDisplayClusterMonitor, Log,
            TEXT("Received custom message from %s: %s = %f"),
            *Endpoint.Endpoint.Name, *Msg.Payload, Msg.Value);
    });

// 向特定角色的所有端点广播自定义消息
FDCMMessage_CustomCommand CustomMsg;
CustomMsg.Payload = TEXT("LightIntensity");
CustomMsg.Value = 1.5f;
Messenger->Broadcast(CustomMsg);

// 或向指定端点发送
TSet<EDCMessengerRole> TargetRoles;
TargetRoles.Add(EDCMessengerRole::ObservablesProvider);
Messenger->SendToRoles(TargetRoles, CustomMsg);
```

**来源**：`Source/DisplayClusterMonitor/Public/DisplayClusterMonitorMessenger.h`

---

## Demo 示例

以下示例展示如何在自定义编辑器模块中集成 DisplayClusterMonitor 的 Messenger，实现一个简单的集群监控面板：

```cpp
// ClusterMonitorPanel.h
#pragma once

#include "CoreMinimal.h"
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"

class FClusterMonitorPanel
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnEndpointJoined(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint);
    void OnEndpointTimeout(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint);
    void OnEndpointLeft(const UE::nDisplay::Monitor::FDCEndpoint& Endpoint, const FString& Reason);
    void OnObservablesNotification(
        const UE::nDisplay::Monitor::FDCEndpoint& Endpoint,
        const UE::nDisplay::Monitor::FDCMMessage_NodeObservablesNotification& Msg);

    TUniquePtr<UE::nDisplay::Monitor::FDCMessenger> Messenger;
};
```

```cpp
// ClusterMonitorPanel.cpp
#include "ClusterMonitorPanel.h"
#include "DisplayClusterMonitorMessenger.h"
#include "DisplayClusterMonitorTypes.h"

using namespace UE::nDisplay::Monitor;

void FClusterMonitorPanel::Initialize()
{
    Messenger = MakeUnique<FDCMessenger>();

    // 以 Monitor 角色启动
    TSet<EDCMessengerRole> Roles;
    Roles.Add(EDCMessengerRole::Monitor);
    Messenger->Start(TEXT("EditorMonitor"), Roles);

    // 绑定生命周期事件
    Messenger->OnEndpointJoined.AddRaw(this, &FClusterMonitorPanel::OnEndpointJoined);
    Messenger->OnEndpointTimeout.AddRaw(this, &FClusterMonitorPanel::OnEndpointTimeout);
    Messenger->OnEndpointLeft.AddRaw(this, &FClusterMonitorPanel::OnEndpointLeft);

    // 绑定可观察资源通知
    Messenger->OnMessage<FDCMMessage_NodeObservablesNotification>()
        .AddRaw(this, &FClusterMonitorPanel::OnObservablesNotification);
}

void FClusterMonitorPanel::Shutdown()
{
    if (Messenger)
    {
        Messenger->Stop(TEXT("Editor panel shutdown"));
        Messenger.Reset();
    }
}

void FClusterMonitorPanel::OnEndpointJoined(const FDCEndpoint& Endpoint)
{
    UE_LOG(LogDisplayClusterMonitor, Log,
        TEXT("[%s] Node '%s' (%s) joined cluster"),
        *Endpoint.Residence.Hostname,
        *Endpoint.Residence.NodeName,
        Endpoint.Residence.bIsPrimary ? TEXT("Primary") : TEXT("Secondary"));
}

void FClusterMonitorPanel::OnEndpointTimeout(const FDCEndpoint& Endpoint)
{
    UE_LOG(LogDisplayClusterMonitor, Warning,
        TEXT("[%s] Node '%s' is unresponsive!"),
        *Endpoint.Residence.Hostname,
        *Endpoint.Residence.NodeName);
}

void FClusterMonitorPanel::OnEndpointLeft(const FDCEndpoint& Endpoint, const FString& Reason)
{
    UE_LOG(LogDisplayClusterMonitor, Log,
        TEXT("[%s] Node '%s' left: %s"),
        *Endpoint.Residence.Hostname,
        *Endpoint.Residence.NodeName,
        *Reason);
}

void FClusterMonitorPanel::OnObservablesNotification(
    const FDCEndpoint& Endpoint,
    const FDCMMessage_NodeObservablesNotification& Msg)
{
    for (const FDCMData_ObservableInfo& Info : Msg.Observables.ObservablesAdded)
    {
        UE_LOG(LogDisplayClusterMonitor, Log,
            TEXT("[%s] New observable '%s' (%dx%d)"),
            *Endpoint.Residence.Hostname,
            *Info.Name,
            Info.Resolution.X, Info.Resolution.Y);
    }
}
```

---

## 模块依赖

以下为 DisplayClusterMonitor 模块的特殊依赖（其余插件模块仅依赖标准 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `UnrealEd` | 编辑器集成（视口捕获、设置面板） |
| `DisplayCluster` | nDisplay 核心运行时（集群管理、视口系统、会话管理） |
| `MediaUtils` / `MediaFrameworkUtilities` | NDI MediaOutput / MediaCapture 媒体捕获基础设施 |
| `MessageBus` / `Messaging` | Unreal 消息总线（集群节点间通信） |

> **注意**：完整插件中部分模块还依赖 `D3D12RHI`（SharedMemoryMedia、DisplayClusterMedia）、`EditorWidgets`、`LevelEditor`、`PropertyEditor` 等。

---

## 架构概览（DisplayClusterMonitor 模块）

```
DisplayClusterMonitorModule
├── FDisplayClusterMonitorProviderMedia    ← 可观察资源提供者
│   ├── FDCMessenger                        ← MessageBus 通信封装
│   │   ├── 发现/心跳/离开                  ← 集群节点生命周期
│   │   ├── 消息分发（按类型委托）           ← 自定义消息路由
│   │   └── 远程控制台命令                   ← 跨节点执行命令
│   │
│   ├── Evaluate*()                         ← 评估各类视口资源
│   │   ├── EvaluateBackbuffer()            ← 后缓冲
│   │   ├── EvaluateUI()                    ← UI 层
│   │   ├── EvaluateViewport()              ← 普通视口
│   │   ├── EvaluateICVFXCamera()           ← ICVFX 相机
│   │   └── EvaluateICVFXCameraTile()       ← ICVFX 相机瓦片
│   │
│   └── IMediaObservable                    ← 媒体捕获接口
│       ├── FMediaObservableBackbuffer      ← 后缓冲捕获
│       ├── FMediaObservableUI              ← UI 层捕获
│       └── FMediaObservablePostRender      ← 渲染后回调捕获
│
└── UDisplayClusterMonitorSettings          ← 配置（心跳间隔、UI 布局等）
```

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-26 | `b75c0fdc` | [MovieGraph][nDisplay] EXR multi-layer support | MovieGraph 支持 EXR 多层输出 |
| 2026-05-26 | `1c0f63c6` | [nDisplay] MoviePipeline: merge WarpBlendAlpha mode into WarpBlend | 合并 WarpBlendAlpha 到 WarpBlend 模式 |
| 2026-05-21 | `63098dc2` | [nDisplay] Fix topology-aware camera naming in MRG; fix opaque alpha in MPCDI/ICVFX shaders | 修复 MRG 中相机命名和 MPCDI/ICVFX 着色器透明度 |
| 2026-05-19 | `f8f04c61` | nDisplay: Honor non-default DisplayGamma at output-frame encoding fallback | 输出帧编码时尊重非默认 DisplayGamma |
| 2026-05-16 | `f8b15904` | [nDisplay] Fixed flickering when GUI texture size is less than viewport size | 修复 GUI 纹理小于视口尺寸时的闪烁问题 |

### 维护评价

**活跃维护** ✅

- **创建时间**：2018 年（约 8 年历史），随 UE4.20 Enterprise 版本引入
- **更新频率**：非常活跃，最近一周内有多次提交，持续获得功能性更新
- **维护团队**：Epic Games 官方维护，与虚拟制片/ICVFX 流水线紧密集成
- **成熟度**：经过多年迭代，架构稳定（MessageBus 通信、NDI 媒体流、多类型可观察资源），是 Epic 虚拟制片方案的核心组件
- **注意事项**：
  - 默认未启用（`EnabledByDefault=false`），需手动在插件设置中开启
  - 仅支持 Win64 和 Linux 平台
  - 依赖 NDI SDK 进行媒体流传输
  - 是超大型插件（29 个模块），文档覆盖其他子模块需另行查阅

**推荐使用**：如果你的项目涉及多机渲染、LED 墙、虚拟制片，nDisplay 是标准选择，DisplayClusterMonitor 模块为运维监控提供了完善的基础设施。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/nDisplay)
- [官方文档](https://docs.unrealengine.com/en-US/ProductionPipelines/VirtualProduction/nDisplay/)（nDisplay 虚拟制片文档）