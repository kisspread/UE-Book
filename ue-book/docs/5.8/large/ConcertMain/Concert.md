# Concert Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多用户协作会话 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

Concert Main 是 Unreal Editor **多用户实时协作（Multi-User Editing）** 的核心基础设施插件。它定义了整个多用户编辑系统的基础通信协议、数据结构和会话管理接口。

具体来说，这个插件解决以下问题：

1. **会话管理**：定义了客户端如何发现服务器、创建/加入/断开会话的完整生命周期
2. **消息协议**：提供了自定义事件（Custom Event）和自定义请求/响应（Custom Request/Response）的双向通信机制
3. **数据序列化与压缩**：支持对载荷数据进行 Zlib/Oodle 压缩、CBOR/标准序列化，优化网络传输效率
4. **版本兼容性检查**：确保连接的客户端和服务端在引擎版本、文件版本、自定义版本等维度上兼容
5. **文件共享服务**：提供跨客户端的文件共享接口，用于大型资产（如资产包数据）的传输
6. **会话归档与恢复**：支持将活跃会话归档、从归档恢复、导出等操作

该插件本身**不包含任何可编辑器中直接使用的 UI 或功能**，而是作为底层框架被 `ConcertSyncCore`、`MultiUserClient` 等上层插件所依赖。它设计为仅在特定的可执行程序中加载（UnrealMultiUserServer、LiveLinkHub 等），普通编辑器实例通过 `ConcertClient` 模块参与协作。

## 使用场景

- **多人同时编辑关卡**：多个设计师在同一关卡中同时放置 Actor、调整属性，所有变更实时同步
- **灾难恢复服务**：通过 `UnrealRecoverySvc` 程序持续记录编辑操作，可在崩溃后回溯恢复
- **Live Link Hub 协作**：在 LiveLinkHub 程序中进行多人设备管理与数据分发
- **自定义多人编辑工具**：基于 Concert 的自定义消息系统构建专属的协作工具（如多人蓝图编辑、动画审查等）
- **程序化测试自动化**：在 CI/CD 中使用 UnrealMultiUserServer 运行多用户场景的自动化测试

## 蓝图用法

Concert Main 模块本身**不暴露蓝图 API**。它是一个纯 C++ 框架层，所有蓝图可调用的节点由上层插件（如 `MultiUserClientLibrary`）提供。

该模块的数据结构（如 `FConcertClientInfo`、`FConcertSessionInfo`）虽有 `USTRUCT`/`UENUM` 标记，但主要用于 C++ 层的网络序列化传输，不在蓝图中直接操作。

## C++ 用法

### 头文件引入

```cpp
// 核心会话接口
#include "IConcertSession.h"

// 消息数据结构
#include "ConcertMessages.h"
#include "ConcertMessageData.h"

// 会话处理器接口
#include "IConcertSessionHandler.h"

// 模块接口
#include "IConcertModule.h"

// 服务器事件
#include "IConcertServerEventSink.h"
#include "ConcertServerEvents.h"

// 文件共享
#include "IConcertFileSharingService.h"

// 版本信息
#include "ConcertVersion.h"
```

### 基本用法 — 注册自定义事件处理器

```cpp
// 来源: Public/IConcertSession.h — IConcertSession::RegisterCustomEventHandler

// 定义自定义事件结构体
USTRUCT()
struct FMyCustomEvent : public FConcertEventData
{
    GENERATED_BODY()

    UPROPERTY()
    FString Message;
};

// 注册事件处理器（Lambda 方式）
Session->RegisterCustomEventHandler<FMyCustomEvent>(
    [](const FConcertSessionContext& Context, const FMyCustomEvent& Event)
    {
        UE_LOG(LogTemp, Log, TEXT("收到自定义事件: %s"), *Event.Message);
    }
);

// 注册事件处理器（成员函数方式）
Session->RegisterCustomEventHandler<FMyCustomEvent>(this, &UMyClass::OnCustomEventReceived);
```

### 基本用法 — 发送自定义事件

```cpp
// 来源: Public/IConcertSession.h — IConcertSession::SendCustomEvent

// 发送给单个客户端
FMyCustomEvent Event;
Event.Message = TEXT("Hello from another client!");
Session->SendCustomEvent<FMyCustomEvent>(Event, TargetEndpointId, EConcertMessageFlags::None);

// 发送给多个客户端
TArray<FGuid> Destinations = { EndpointId1, EndpointId2 };
Session->SendCustomEvent<FMyCustomEvent>(Event, Destinations, EConcertMessageFlags::ReliableOrdered);
```

### 基本用法 — 注册自定义请求处理器

```cpp
// 来源: Public/IConcertSession.h — IConcertSession::RegisterCustomRequestHandler

// 定义请求和响应结构体
USTRUCT()
struct FMyQueryRequest : public FConcertRequestData
{
    GENERATED_BODY()
    UPROPERTY()
    FString QueryName;
};

USTRUCT()
struct FMyQueryResponse : public FConcertResponseData
{
    GENERATED_BODY()
    UPROPERTY()
    FString Result;
};

// 注册请求处理器
Session->RegisterCustomRequestHandler<FMyQueryRequest, FMyQueryResponse>(
    [](const FConcertSessionContext& Context, const FMyQueryRequest& Request, FMyQueryResponse& Response) -> EConcertSessionResponseCode
    {
        Response.Result = FString::Printf(TEXT("Query '%s' processed"), *Request.QueryName);
        return EConcertSessionResponseCode::Success;
    }
);
```

### 基本用法 — 发送自定义请求并获取 Future 响应

```cpp
// 来源: Public/IConcertSession.h — IConcertSession::SendCustomRequest

FMyQueryRequest Request;
Request.QueryName = TEXT("AssetCount");

TFuture<FMyQueryResponse> Future = Session->SendCustomRequest<FMyQueryRequest, FMyQueryResponse>(
    Request, ServerEndpointId
);

Future.Next([this](const FMyQueryResponse& Response)
{
    // 在异步结果返回时处理
    UE_LOG(LogTemp, Log, TEXT("服务器返回: %s"), *Response.Result);
});
```

### 进阶用法 — 连接状态监听

```cpp
// 来源: Public/IConcertSession.h — IConcertClientSession

// 监听连接状态变化
IConcertClientSession* ClientSession = /* 获取会话 */;
ClientSession->OnConnectionChanged().AddLambda(
    [](IConcertClientSession& Session, EConcertConnectionStatus Status)
    {
        switch (Status)
        {
        case EConcertConnectionStatus::Connected:
            UE_LOG(LogTemp, Log, TEXT("已连接到 Concert 会话"));
            break;
        case EConcertConnectionStatus::Disconnected:
            UE_LOG(LogTemp, Warning, TEXT("已断开 Concert 会话"));
            break;
        }
    }
);

// 监听客户端加入/离开
ClientSession->OnSessionClientChanged().AddLambda(
    [](IConcertClientSession& Session, EConcertClientStatus Status, const FConcertSessionClientInfo& ClientInfo)
    {
        if (Status == EConcertClientStatus::Connected)
        {
            UE_LOG(LogTemp, Log, TEXT("新客户端加入: %s"), *ClientInfo.ClientInfo.DisplayName);
        }
    }
);

// 发起连接
ClientSession->Connect();
```

### 进阶用法 — 控制发送/接收状态

```cpp
// 来源: Public/IConcertSession.h — IConcertClientSession::SetSendReceiveState

// 暂停接收，仅发送本地变更
ClientSession->SetSendReceiveState(EConcertSendReceiveState::SendOnly);

// 暂停发送，仅接收远程变更
ClientSession->SetSendReceiveState(EConcertSendReceiveState::ReceiveOnly);

// 恢复正常双向通信
ClientSession->SetSendReceiveState(EConcertSendReceiveState::Default);
```

### 进阶用法 — 序列化载荷数据

```cpp
// 来源: Public/ConcertMessageData.h — FConcertSessionSerializedPayload

// 序列化自定义数据
FMyStructData Data;
Data.SomeValue = 42;

FConcertSessionSerializedPayload Payload;
Payload.SetTypedPayload(Data, EConcertPayloadCompressionType::Heuristic);

// 反序列化
FMyStructData RetrievedData;
if (Payload.GetTypedPayload(RetrievedData))
{
    // 使用 RetrievedData
}

// 检查压缩状态
bool bCompressed = Payload.PayloadIsCompressed();
```

## 模块依赖

Concert 插件自身的模块之间有如下依赖关系（从 Build.cs 提取），对外部使用者而言：

| 模块 | 用途 |
|---|---|
| `ConcertTransport` | 底层可靠消息传输协议，Concert 核心通信基础设施 |
| `Concert` | 会话接口定义、消息数据结构、版本检查框架 |
| `ConcertClient` | 客户端会话实现（加入/离开会话、发送/接收消息） |
| `ConcertServer` | 服务端会话实现（管理会话生命周期、客户端连接） |

对于**使用者**（需要在自己的模块中使用 Concert API），通常需要依赖 `Concert` 和 `ConcertClient`（作为客户端参与）或 `ConcertServer`（作为服务端扩展）。无特殊外部依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 宏迁移到新的 UE_LOGF 宏 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为 trace 通道和其他位置添加描述信息 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 修复与 IsSavingPackage 相关的问题 |
| 2025-12-10 | `11a770db` | Specify FConcertSessionChallengeData::ChallengeKey should be ignored when running member initialization tests | 标记 ChallengeKey 字段在成员初始化测试中应被忽略 |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will ... | 实现了可与多用户系统配合使用的文件共享服务 |

### 维护评价

**活跃维护中**。Concert 是 Epic Games 内部核心多用户编辑功能的基础设施，虽然标记为实验性（`IsBetaVersion=true`）且默认不启用（`EnabledByDefault=false`），但它持续获得实质性更新：

- **持续活跃**：2025-2026 年间有多次功能更新（文件共享服务、日志系统迁移等）
- **工程维护**：包括代码现代化（UE_LOG → UE_LOGF）、测试兼容性改进
- **无废弃迹象**：作为 Multi-User Editing、Disaster Recovery、LiveLinkHub 的基础设施，短期内不会废弃
- **注意事项**：
  - 该插件设计为仅在特定可执行程序中加载（UnrealMultiUserServer 等），普通游戏项目不应直接依赖
  - `EnabledByDefault=false` 表示需要手动启用
  - 部分旧 API 已标记 `UE_DEPRECATED(5.8, ...)`（如 `EConcertCompressionDetails`），新代码应使用替代 API
- **推荐使用**：如果你在开发多用户编辑功能或相关工具，这是必经之路；如果只是普通游戏开发，不需要直接接触此插件

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)
- [官方文档](https://docs.unrealengine.com/en-US/Engine/Editor/MultiUserEditing/)（Unreal Editor 多用户编辑文档）