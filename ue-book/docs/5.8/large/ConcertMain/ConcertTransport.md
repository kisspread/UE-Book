# Concert - Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 协作会话 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

ConcertMain 是 UE5 **多用户协作编辑**（Multi-User Editing）系统的**传输层核心模块**。它为多个 Editor 实例或专用服务器之间的消息通信提供了完整的基础设施，包括：

- **可靠消息传递**：支持有序、可靠的消息投递，包含确认应答（ACK）、重传、保活（Keep-Alive）和超时机制
- **请求/响应模式**：异步 RPC，发送方通过 `TFuture` 获取响应
- **事件发布/订阅**：支持定向发送和广播发布两种事件模式
- **端点管理**：自动发现、握手协商、连接状态变更通知
- **消息追踪**：集成 Unreal Insights，可追踪复制协议的传输时间线

这不是一个面向最终用户的编辑器功能插件，而是上层 Concert 插件（如 Multi-User Editing UI）依赖的底层传输引擎。它本身默认禁用、标记为隐藏，且仅在特定程序（`UnrealMultiUserServer`、`LiveLinkHub` 等）中加载。

## 使用场景

- 你在开发**多人协作编辑器功能** → 需要实现自定义 Concert 会话协议，依赖 ConcertTransport 的端点 API
- 你在构建**专用多人服务器**（`UnrealMultiUserServer`）→ 使用 ConcertServer 和 ConcertTransport 模块
- 你需要**可靠的跨进程消息传递**→ 使用 `IConcertLocalEndpoint` 的请求/响应和事件机制
- 你需要**调试多用户会话的网络延迟**→ 启用 ConcertTransport 的 Insights 追踪

## 蓝图用法

本插件为纯传输层，**不包含任何 BlueprintCallable 接口**。所有 API 均为 C++ 端点接口。上层蓝图功能由 Concert 插件家族中的其他插件提供。

## C++ 用法

### 头文件引入

```cpp
#include "IConcertEndpoint.h"
#include "IConcertTransportModule.h"
#include "ConcertTransportMessages.h"
#include "IConcertMessageHandler.h"
#include "ConcertMessageContext.h"
```

### 基本用法 — 创建端点并发送请求

```cpp
// 获取 Transport 模块并创建端点提供者
IConcertTransportModule& TransportModule = IConcertTransportModule::Get();
TSharedPtr<IConcertEndpointProvider> EndpointProvider = TransportModule.CreateEndpointProvider();

// 配置端点设置
FConcertEndpointSettings Settings;
Settings.bEnableLogging = true;
Settings.RemoteEndpointTimeoutSeconds = 60;

// 创建本地端点
TSharedPtr<IConcertLocalEndpoint> LocalEndpoint = EndpointProvider->CreateLocalEndpoint(
    TEXT("MyClient"),
    Settings,
    nullptr /* Logger Factory */
);

// 定义请求和响应数据结构
USTRUCT()
struct FMyRequestData : public FConcertRequestData
{
    GENERATED_BODY()
    UPROPERTY()
    FString Payload;
};

USTRUCT()
struct FMyResponseData : public FConcertResponseData
{
    GENERATED_BODY()
    UPROPERTY()
    FString Result;
};

// 注册请求处理器
LocalEndpoint->RegisterRequestHandler<FMyRequestData, FMyResponseData>(
    [](const FConcertMessageContext& Context) -> TFuture<FMyResponseData>
    {
        const FMyRequestData* Request = Context.GetMessage<FMyRequestData>();
        FMyResponseData Response;
        Response.ResponseCode = EConcertResponseCode::Success;
        Response.Result = TEXT("Processed: ") + Request->Payload;
        return FConcertResponseData::AsFuture(MoveTemp(Response));
    }
);

// 发送请求到远程端点
FMyRequestData Request;
Request.Payload = TEXT("Hello");
FGuid RemoteEndpointId = /* 远程端点 ID */;

TFuture<FMyResponseData> Future = LocalEndpoint->SendRequest<FMyRequestData, FMyResponseData>(Request, RemoteEndpointId);
Future.Next([](FMyResponseData&& Response)
{
    if (Response.ResponseCode == EConcertResponseCode::Success)
    {
        UE_LOG(LogConcert, Log, TEXT("Response: %s"), *Response.Result);
    }
});
```

### 基本用法 — 发布和订阅事件

```cpp
// 定义事件数据结构
USTRUCT()
struct FMyEventData : public FConcertEventData
{
    GENERATED_BODY()
    UPROPERTY()
    FString Notification;
};

// 在接收端：订阅事件
// 方式一：成员函数处理器
class FMyEventHandler
{
public:
    void HandleNotification(const FConcertMessageContext& Context)
    {
        const FMyEventData* Event = Context.GetMessage<FMyEventData>();
        UE_LOG(LogConcert, Log, TEXT("Received: %s"), *Event->Notification);
    }
};

FMyEventHandler Handler;
LocalEndpoint->SubscribeEventHandler<FMyEventData>(
    &Handler, &FMyEventHandler::HandleNotification
);

// 方式二：Lambda 处理器（注册定向事件）
LocalEndpoint->RegisterEventHandler<FMyEventData>(
    [](const FConcertMessageContext& Context)
    {
        const FMyEventData* Event = Context.GetMessage<FMyEventData>();
        UE_LOG(LogConcert, Log, TEXT("Event: %s"), *Event->Notification);
    }
);

// 在发送端：发布事件（所有订阅者都能收到）
FMyEventData Event;
Event.Notification = TEXT("Someone joined!");
LocalEndpoint->PublishEvent(Event);

// 或者定向发送事件到特定端点
LocalEndpoint->SendEvent(Event, RemoteEndpointId, EConcertMessageFlags::ReliableOrdered);
```

### 进阶用法 — 监听端点连接变化

```cpp
// 监听远程端点的发现与断开
LocalEndpoint->OnRemoteEndpointConnectionChanged().AddLambda(
    [](const FConcertEndpointContext& RemoteEndpoint, EConcertRemoteEndpointConnection Status)
    {
        switch (Status)
        {
        case EConcertRemoteEndpointConnection::Discovered:
            UE_LOG(LogConcert, Log, TEXT("Discovered: %s"), *RemoteEndpoint.ToString());
            break;
        case EConcertRemoteEndpointConnection::TimedOut:
            UE_LOG(LogConcert, Warning, TEXT("Timed out: %s"), *RemoteEndpoint.ToString());
            break;
        case EConcertRemoteEndpointConnection::ClosedRemotely:
            UE_LOG(LogConcert, Log, TEXT("Closed: %s"), *RemoteEndpoint.ToString());
            break;
        }
    }
);

// 获取所有已连接的远程端点
TArray<FConcertEndpointContext> RemoteEndpoints = LocalEndpoint->GetRemoteEndpoints();
for (const FConcertEndpointContext& Context : RemoteEndpoints)
{
    UE_LOG(LogConcert, Log, TEXT("Remote: %s"), *Context.ToString());
}

// 监听消息确认
LocalEndpoint->OnConcertMessageAcknowledgementReceived().AddLambda(
    [](const FConcertEndpointContext& LocalEndpoint,
       const FConcertEndpointContext& RemoteEndpoint,
       const TSharedRef<IConcertMessage>& AckedMessage,
       const FConcertMessageContext& MessageContext)
    {
        UE_LOG(LogConcert, Verbose, TEXT("Message %s acknowledged by %s"),
            *AckedMessage->GetMessageId().ToString(),
            *RemoteEndpoint.ToString());
    }
);
```

### 进阶用法 — 使用 Scratchpad 存储会话数据

```cpp
#include "ConcertScratchpad.h"

// 创建一个线程安全的 Scratchpad
FConcertScratchpadPtr Scratchpad = MakeShared<FConcertScratchpad>();

// 存储任意类型的数据
Scratchpad->SetValue(TEXT("SessionVersion"), 42);
Scratchpad->SetValue(TEXT("UserName"), FString(TEXT("Alice")));

// 读取数据
if (int32* Version = Scratchpad->GetValue<int32>(TEXT("SessionVersion")))
{
    UE_LOG(LogConcert, Log, TEXT("Session version: %d"), *Version);
}

// 线程安全：多个端点可以共享同一个 Scratchpad
```

### 进阶用法 — 使用 Identifier Table 跨网络映射名称

```cpp
#include "ConcertIdentifierTable.h"
#include "ConcertTransportArchives.h"

// 创建标识符表（用于 FName 的跨网络序列化）
FConcertLocalIdentifierTable IdentifierTable;

// 映射名称到索引
int32 IndexA = IdentifierTable.MapName(FName(TEXT("/Game/MapA")));
int32 IndexB = IdentifierTable.MapName(FName(TEXT("/Game/MapB")));

// 序列化时使用自定义 Archive
TArray<uint8> Buffer;
{
    FConcertIdentifierWriter Writer(&IdentifierTable, Buffer);
    // 序列化包含 FName 的数据，名称会自动映射为索引
    Writer << SomeAssetPath;
}

// 获取表状态以便传输给远程端点
FConcertLocalIdentifierState State;
IdentifierTable.GetState(State);

// 远程端点恢复表
FConcertLocalIdentifierTable RemoteTable;
RemoteTable.SetState(State);
```

## Demo 示例

一个最小的 Concert 端点使用示例，展示创建端点、注册处理器、发送消息：

```cpp
// ConcertDemo.h
#pragma once

#include "IConcertEndpoint.h"
#include "ConcertTransportMessages.h"

USTRUCT()
struct FDemoPingRequest : public FConcertRequestData
{
    GENERATED_BODY()
    UPROPERTY()
    int32 PingId = 0;
};

USTRUCT()
struct FDemoPingResponse : public FConcertResponseData
{
    GENERATED_BODY()
    UPROPERTY()
    int32 PingId = 0;
};

class FConcertDemo
{
public:
    void Initialize();
    void Shutdown();

private:
    void OnPingRequest(const FConcertMessageContext& Context);
    void OnRemoteEndpointChanged(const FConcertEndpointContext& Endpoint, EConcertRemoteEndpointConnection Status);

    TSharedPtr<IConcertLocalEndpoint> Endpoint;
};
```

```cpp
// ConcertDemo.cpp
#include "ConcertDemo.h"
#include "IConcertTransportModule.h"

void FConcertDemo::Initialize()
{
    IConcertTransportModule& TransportModule = IConcertTransportModule::Get();
    TSharedPtr<IConcertEndpointProvider> Provider = TransportModule.CreateEndpointProvider();

    FConcertEndpointSettings Settings;
    Settings.bEnableLogging = false;
    Settings.RemoteEndpointTimeoutSeconds = 30;

    Endpoint = Provider->CreateLocalEndpoint(TEXT("DemoEndpoint"), Settings, nullptr);

    // 注册 Ping 请求处理器
    Endpoint->RegisterRequestHandler<FDemoPingRequest, FDemoPingResponse>(
        this, &FConcertDemo::OnPingRequest
    );

    // 监听连接变化
    Endpoint->OnRemoteEndpointConnectionChanged().AddRaw(
        this, &FConcertDemo::OnRemoteEndpointChanged
    );
}

void FConcertDemo::Shutdown()
{
    if (Endpoint.IsValid())
    {
        Endpoint->UnregisterRequestHandler<FDemoPingRequest>();
        Endpoint.Reset();
    }
}

void FConcertDemo::OnPingRequest(const FConcertMessageContext& Context)
{
    const FDemoPingRequest* Request = Context.GetMessage<FDemoPingRequest>();

    FDemoPingResponse Response;
    Response.PingId = Request->PingId;
    Response.ResponseCode = EConcertResponseCode::Success;
    Response.Reason = FText::FromString(TEXT("Pong!"));

    // 无需手动发送响应，框架通过返回值自动处理
    // 这里展示的是注册处理器时，框架会调用此函数并使用返回的 Future
}

void FConcertDemo::OnRemoteEndpointChanged(
    const FConcertEndpointContext& Endpoint,
    EConcertRemoteEndpointConnection Status)
{
    UE_LOG(LogConcert, Log, TEXT("Endpoint %s: status changed to %d"),
        *Endpoint.ToString(), static_cast<int32>(Status));
}
```

## 模块依赖

从源码分析，ConcertTransport 使用了 UE 的 Messaging 框架（`FMessageEndpoint`、`FMessageBusNotification`）作为底层传输。以下为该插件特有的依赖：

| 模块 | 用途 |
|---|---|
| `Messaging` | UE 消息总线（MessageBus）框架，提供 `FMessageEndpoint` 等底层通信能力 |
| `UnrealInsights` (可选) | 用于 Concert 追踪宏的 Insights 集成（通过 `CPUPROFILERTRACE_ENABLED` 控制） |

无其他特殊依赖（仅标准 Core/CoreUObject/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 格式化宏 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为追踪通道和部分位置添加描述文本 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 添加包保存状态检查相关改动 |
| 2025-12-10 | `11a770db` | Specify FConcertSessionChallengeData::ChallengeKey should be ignored when running member initialization | 修正会话挑战数据成员初始化逻辑 |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will... | 实现用于多用户协作的文件共享系统 |

### 维护评价

- **年龄**：约 7 年（2019 年创建），属于老古董级插件
- **实验性状态**：`IsBetaVersion=true`，始终处于 Beta 阶段
- **隐藏插件**：`Hidden=true`，不在插件浏览器中显示
- **受限加载**：`EnabledByDefault=false`，且通过 `ProgramAllowList` 限制仅在特定程序中加载（Multi-User Server、LiveLinkHub 等）
- **更新频率**：2025-12 至 2026-04 期间有持续更新，内容涵盖日志迁移、追踪改进、新功能（文件共享）
- **结论**：该插件作为 Epic 内部多人协作基础设施**仍在积极维护**，但它是面向**引擎开发者**的底层模块，不推荐直接在项目中使用——应通过上层的 Multi-User Editing 插件间接使用

⚠️ **注意**：此插件标记为 Beta 且隐藏，API 可能在未来版本中发生变化。不建议在生产环境中直接依赖此插件的 API。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-collaborative-tools-in-unreal-engine/)（Multi-User Editing 整体文档）
- 测试用例：插件目录内未包含独立测试文件，测试可能位于 Engine/Tests 或上层 Concert 插件中