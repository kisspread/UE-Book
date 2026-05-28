# Live Link Hub

> LiveLink Hub allows streaming of animated data into Unreal Engine or UEFN

| 属性 | 值 |
|---|---|
| 中文名 | 实时链接中枢 |
| 分类 | Animation |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `LiveLinkHub` (Runtime), `LiveLinkHubEditor` (Runtime), `LiveLinkHubMessaging` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-02-02 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub) | |

## 用途

LiveLinkHub 是 Epic 为**集中式动画数据分发**设计的实验性插件。它的核心角色是充当 Live Link 网络中的"中枢（Hub）"节点，让多个 Unreal Engine 或 UEFN 实例能够：

1. **自动发现与连接**：通过 MessageBus 协议自动发现局域网中的 LiveLinkHub 实例，并根据拓扑模式（Hub/Spoke/UnrealClient/External）智能决定是否建立连接。
2. **同步引擎设置**：Hub 可以远程控制连接到它的 UE 客户端的 Custom Time Step、Timecode Provider、Source Evaluation Mode 等关键引擎时序设置。
3. **录制集成**：在 Take Recorder 场景中，Hub 作为录制的数据源中心，统一管理多客户端的动画数据流。
4. **辅助通道协商**：通过 Aux Channel 机制支持自定义通信协议扩展，允许第三方在 LiveLink 连接之上叠加自己的控制通道。

简单来说：LiveLinkHub 解决的是**"一个动画数据源同时服务于多个 UE 实例"**的场景，特别适用于虚拟制片、多机位直播和 Take Recorder 录制等需要集中管理 Live Link 连接的工作流。

## 使用场景

- 你在做一个**虚拟制片**项目，需要多个 UE 实例同时接收同一个动捕数据源 → 用 LiveLinkHub 作为中枢转发
- 你使用 **Take Recorder** 录制动画，需要统一管理多客户端的帧同步和录制状态 → LiveLinkHub 自动同步 Time Step 和 Timecode
- 你需要将 Live Link 数据分发到 **UEFN**（Fortnite Creative）实例 → LiveLinkHub 支持 Hub ↔ UnrealClient 拓扑
- 你需要**跨机器自动发现** LiveLink 提供者，不想手动配置 MessageBus 地址 → ConnectionManager 自动轮询和连接
- 你正在开发**自定义的 LiveLink 通道协议**（如自定义音频流、元数据通道）→ Aux Channel 机制提供可扩展的通道协商框架

## 蓝图用法

LiveLinkHubMessaging 模块的主要 API 面向 C++，蓝图可访问的能力集中在设置层面。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `bAllowReceivingFromUnreal` | 控制是否允许 Hub 从 Unreal 实例接收 Live Link 数据 | `ULiveLinkHubMessagingSettings` |
| `AutoConnectMode` | 设置自动连接模式（Disabled/All/LocalOnly） | `ELiveLinkHubAutoConnectMode` |

### 设置面板

在 **Editor Preferences → LiveLink Hub** 中可以配置：

- **Allow Receiving From Unreal**：默认关闭。开启后允许 Hub 接收来自 Unreal 实例的 Live Link 广播数据（适用于 Unreal 也作为数据源的场景）。
- 拓扑模式由代码自动管理，无需手动配置。

### AutoConnect 模式

| 模式 | 说明 |
|---|---|
| `Disabled` | 不自动添加任何客户端 |
| `All` | 自动添加局域网中发现的任何客户端（匹配过滤器） |
| `LocalOnly` | 仅添加本机运行的客户端，覆盖当前过滤器 |

## C++ 用法

### 头文件引入

```cpp
#include "ILiveLinkHubMessagingModule.h"
#include "LiveLinkHubMessages.h"
#include "LiveLinkHubMessagingSettings.h"
```

### 基本用法：获取模块并设置拓扑模式

```cpp
// 来源: Public/ILiveLinkHubMessagingModule.h
#include "ILiveLinkHubMessagingModule.h"

// 获取模块接口
ILiveLinkHubMessagingModule& HubModule = FModuleManager::GetModuleChecked<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");

// 设置当前实例的拓扑模式
HubModule.SetHostTopologyMode(ELiveLinkTopologyMode::Hub);

// 获取当前拓扑模式
ELiveLinkTopologyMode CurrentMode = HubModule.GetHostTopologyMode();

// 设置实例 ID（防止自己连接自己）
FGuid MyId = FApp::GetInstanceId();
HubModule.SetInstanceId(FLiveLinkHubInstanceId(MyId));

// 获取实例 ID
FLiveLinkHubInstanceId InstanceId = HubModule.GetInstanceId();
```

### 基本用法：监听连接建立事件

```cpp
// 来源: Public/ILiveLinkHubMessagingModule.h
#include "ILiveLinkHubMessagingModule.h"

// 绑定连接建立回调
ILiveLinkHubMessagingModule& HubModule = FModuleManager::GetModuleChecked<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");

HubModule.OnConnectionEstablished().AddLambda([](FGuid SourceId)
{
    UE_LOG(LogTemp, Log, TEXT("LiveLinkHub connection established, SourceId: %s"), *SourceId.ToString());
});
```

### 进阶用法：注册辅助通道处理器

```cpp
// 来源: Public/ILiveLinkHubMessagingModule.h
// 辅助通道（Aux Channel）允许在 LiveLink 连接上叠加自定义通信协议

// 1. 定义自定义请求消息（继承自 FLiveLinkHubAuxChannelRequestMessage）
USTRUCT()
struct FMyCustomAuxRequest : public FLiveLinkHubAuxChannelRequestMessage
{
    GENERATED_BODY()
    
    UPROPERTY()
    FString CustomPayload;
};

// 2. 注册处理器
ILiveLinkHubMessagingModule& HubModule = FModuleManager::GetModuleChecked<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");

bool bRegistered = HubModule.RegisterAuxChannelRequestHandler<FMyCustomAuxRequest>(
    TUniqueFunction<void(const FMyCustomAuxRequest&, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>&)>(
        [](const FMyCustomAuxRequest& Message, const TSharedRef<IMessageContext, ESPMode::ThreadSafe>& Context)
        {
            UE_LOG(LogTemp, Log, TEXT("Received custom aux request: %s"), *Message.CustomPayload);
            
            // 处理请求后，发送接受消息
            // FLiveLinkHubAuxChannelAcceptMessage AcceptMsg;
            // AcceptMsg.ChannelId = Message.ChannelId;
            // ... 通过 Endpoint 发送
        }
    )
);

// 3. 取消注册
HubModule.UnregisterAuxChannelRequestHandler<FMyCustomAuxRequest>();
```

### 进阶用法：查询连接兼容性

```cpp
// 来源: Public/LiveLinkHubMessagingSettings.h
#include "LiveLinkHubMessagingSettings.h"

const ULiveLinkHubMessagingSettings* Settings = GetDefault<ULiveLinkHubMessagingSettings>();

// 检查两个拓扑模式之间是否允许连接
bool bCanReceive = Settings->CanReceiveFrom(ELiveLinkTopologyMode::Hub, ELiveLinkTopologyMode::External);
bool bCanTransmit = Settings->CanTransmitTo(ELiveLinkTopologyMode::Spoke, ELiveLinkTopologyMode::Hub);
```

### 进阶用法：自定义时间步和时间码同步消息

```cpp
// 来源: Public/LiveLinkHubMessages.h
// Hub 可以远程设置连接客户端的 Custom Time Step 和 Timecode

// 构造 Custom Time Step 设置
FLiveLinkHubCustomTimeStepSettings TimeStepSettings;
TimeStepSettings.Kind = ELiveLinkHubCustomTimeStepKind::LiveLink;
TimeStepSettings.bLockStepMode = true;
TimeStepSettings.SubjectName = FLiveLinkSubjectName(TEXT("MySubject"));
TimeStepSettings.CustomTimeStepRate = FFrameRate(24, 1);
TimeStepSettings.FrameRateDivider = 1;

// 应用到引擎
TimeStepSettings.AssignCustomTimeStepToEngine();

// 构造 Timecode 设置
FLiveLinkHubTimecodeSettings TimecodeSettings;
TimecodeSettings.Source = ELiveLinkHubTimecodeSource::UseSubjectName;
TimecodeSettings.SubjectName = FLiveLinkSubjectName(TEXT("MySubject"));
TimecodeSettings.DesiredFrameRate = FFrameRate(24, 1);
TimecodeSettings.BufferSize = 2;

// 应用到引擎
TimecodeSettings.AssignTimecodeSettingsAsProviderToEngine();
```

## Demo 示例

一个最小的 LiveLinkHub 连接管理示例——在编辑器启动时自动发现并连接到 LiveLinkHub 实例：

### MyLiveLinkHubConnector.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "ILiveLinkHubMessagingModule.h"
#include "LiveLinkHubMessages.h"

class FMyLiveLinkHubConnector
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnConnectionEstablished(FGuid SourceId);

    FDelegateHandle ConnectionHandle;
};
```

### MyLiveLinkHubConnector.cpp

```cpp
#include "MyLiveLinkHubConnector.h"
#include "ILiveLinkHubMessagingModule.h"
#include "Modules/ModuleManager.h"

void FMyLiveLinkHubConnector::Initialize()
{
    if (!FModuleManager::Get().IsModuleLoaded("LiveLinkHubMessaging"))
    {
        return;
    }

    ILiveLinkHubMessagingModule& HubModule = FModuleManager::GetModuleChecked<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");

    // 设置为 UnrealClient 模式，允许从 Hub 和 External 接收数据
    HubModule.SetHostTopologyMode(ELiveLinkTopologyMode::UnrealClient);

    // 设置实例 ID 防止自连接
    HubModule.SetInstanceId(FLiveLinkHubInstanceId(FApp::GetInstanceId()));

    // 监听连接事件
    ConnectionHandle = HubModule.OnConnectionEstablished().AddRaw(
        this, &FMyLiveLinkHubConnector::OnConnectionEstablished);
}

void FMyLiveLinkHubConnector::Shutdown()
{
    if (!FModuleManager::Get().IsModuleLoaded("LiveLinkHubMessaging"))
    {
        return;
    }

    ILiveLinkHubMessagingModule& HubModule = FModuleManager::GetModuleChecked<ILiveLinkHubMessagingModule>("LiveLinkHubMessaging");
    HubModule.OnConnectionEstablished().Remove(ConnectionHandle);
}

void FMyLiveLinkHubConnector::OnConnectionEstablished(FGuid SourceId)
{
    UE_LOG(LogTemp, Log, TEXT("[LiveLinkHubConnector] 已连接到 LiveLinkHub，SourceId: %s"), *SourceId.ToString());
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `LiveLink` | 核心 LiveLink 框架（消息总线发现管理器、源/客户端接口） |
| `LiveLinkInterface` | LiveLink 基础类型定义（SubjectName、Role、SourceSettings 等） |
| `EngineAnalytics` | 发送连接建立等使用分析事件 |
| `MessageBus` / `MessagingCommon` | UE 消息总线通信基础设施 |
| `TakeRecorder` / `LevelSequence` | 录制集成相关（LiveLinkHubEditor 模块） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-20 | `54cbb9f8` | Ensure a transient MediaProfile always exists from startup | 确保启动时始终存在临时 MediaProfile |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断警告 |
| 2026-05-13 | `1e2d2efc` | Removed delegate pattern for transient profile creation (simplified to direct NewObject in MediaProf | 简化临时配置文件创建，移除委托模式 |
| 2026-05-13 | `be3a46dd` | Fix use of recording directories nested inside the content folder. | 修复嵌套在 Content 目录下的录制路径问题 |
| 2026-05-12 | `ded7015a` | LiveLinkHub - Fix not being able to connect to a client if auto-connect is disabled | 修复禁用自动连接时无法手动连接客户端的问题 |

### 维护评价

LiveLinkHub 作为**实验性 Beta 插件**，目前处于**活跃开发**状态：

- ✅ 2026 年 5 月仍有密集更新（一周内 5 次提交），说明 Epic 正在积极开发
- ✅ Bug 修复及时，覆盖连接管理、录制路径、浮点精度等多方面
- ⚠️ **Beta 状态**，API 和行为可能会在后续版本发生变化
- ⚠️ **默认未启用**（`EnabledByDefault: false`），需手动在插件管理器中启用
- ⚠️ 拓扑模式（Hub/Spoke/External）是较新引入的概念，代码注释中提到"spokes were introduced"
- ⚠️ 存在 Discovery Protocol V1/V2 的兼容性处理，说明协议仍在演进中

**推荐使用**：如果你的项目涉及虚拟制片或多机 LiveLink 数据分发，可以开始试用，但建议做好 API 变更的准备。生产环境使用需谨慎评估 Beta 风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Animation/LiveLinkHub)
- [官方文档]()（暂无）