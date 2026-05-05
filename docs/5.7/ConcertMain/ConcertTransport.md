# ConcertTransport 模块

> 底层消息传输层，提供端点通信、消息序列化、可靠传输和协议追踪基础设施。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | UncookedOnly |
| LoadingPhase | PreDefault |
| 文件数 | ~30 (.h + .cpp) |
| 依赖 | `Core`, `CoreUObject`, `MessagingCommon`, `TraceLog` |

## 核心职责

ConcertTransport 是整个 Concert 系统的网络传输基础层。它不直接管理会话（session），而是提供：

1. **端点（Endpoint）抽象** — 本地端点和远程端点的通信接口
2. **消息协议** — 定义所有 Concert 消息的基础数据结构
3. **可靠传输** — 基于通道的有序可靠消息传递
4. **消息序列化** — 标识符表（Identifier Table）压缩和序列化归档
5. **协议追踪** — Unreal Insights 集成的 Concert 协议追踪

## 公共接口

### IConcertLocalEndpoint

本地端点，是发送消息的起点。

```cpp
// 发送请求并获取 Future 响应
template<typename RequestType, typename ResponseType>
TFuture<ResponseType> SendRequest(const RequestType& Request, const FGuid& Endpoint);

// 发送事件到指定远程端点
template<typename EventType>
void SendEvent(const EventType& Event, const FGuid& Endpoint,
    EConcertMessageFlags Flags = EConcertMessageFlags::None,
    TMap<FName, FString> Annotations = TMap<FName, FString>());

// 发布事件（订阅者接收）
template<typename EventType>
void PublishEvent(const EventType& Event);

// 注册请求处理器
template<typename RequestType, typename ResponseType>
void RegisterRequestHandler(typename TConcertFunctionRequestHandler<ResponseType>::FFuncType Func);

// 注册事件处理器
template<typename EventType>
void RegisterEventHandler(typename TConcertFunctionEventHandler::FFuncType Func);

// 订阅已发布的事件
template<typename EventType, typename HandlerType>
void SubscribeEventHandler(HandlerType* Handler,
    typename TConcertRawEventHandler<HandlerType>::FFuncType Func);
```

**关键特性：**
- `SendRequest` — 点对点请求/响应模式，返回 `TFuture<ResponseType>`
- `SendEvent` — 点对点事件，可选可靠有序标志
- `PublishEvent` / `SubscribeEventHandler` — 发布/订阅模式
- 自动管理远程端点的发现和超时

### IConcertRemoteEndpoint

远程端点的只读表示：

```cpp
virtual const FConcertEndpointContext& GetEndpointContext() const = 0;
virtual FOnConcertMessageAcknowledgementReceived& OnConcertMessageAcknowledgementReceived() = 0;
```

### FConcertEndpointContext

端点上下文信息：

```cpp
struct FConcertEndpointContext
{
    FGuid EndpointId;           // 端点唯一 ID
    FString EndpointFriendlyName; // 友好名称
};
```

## 消息协议

### 基础消息层次

```
FConcertMessageData          ← 所有消息的基类
├── FConcertEventData        ← 事件消息基类
│   └── FConcertEndpointDiscoveryEvent  ← 端点发现事件
├── FConcertRequestData      ← 请求消息基类
└── FConcertResponseData     ← 响应消息基类（含 ResponseCode）
```

### 消息标志

```cpp
enum class EConcertMessageFlags : uint8
{
    None = 0,
    ReliableOrdered = 1 << 0,  // 保证有序可靠到达
    UniqueId = 1 << 1,         // 跨客户端唯一标识
};
```

### 响应码

```cpp
enum class EConcertResponseCode : uint8
{
    Pending,        // 等待中
    Success,        // 成功
    Failed,         // 失败
    InvalidRequest, // 无效请求
    UnknownRequest, // 未知请求类型
    TimedOut,       // 超时
};
```

### 可靠通道握手

端点之间通过 `FConcertReliableHandshakeData` 协商可靠通道：

- `EConcertReliableHandshakeState::None` → `Negotiate` → `Success`
- 协商通道 ID、消息序号、超时时长

### 消息上下文

```cpp
struct FConcertMessageContext
{
    FGuid SenderConcertEndpointId;
    FDateTime UtcNow;
    const FConcertMessageData* Message;
    const UScriptStruct* MessageType;
    TMap<FName, FString> Annotations;
};
```

## 标识符表（Identifier Table）

用于消息压缩的标识符表系统，减少网络传输中的字符串重复：

| 文件 | 说明 |
|---|---|
| `ConcertIdentifierTable.h` | 标识符表核心实现 |
| `ConcertIdentifierTableData.h` | 表数据结构 |
| `ConcertTransportArchives.h` | 自定义序列化归档，支持标识符表压缩 |

## Scratchpad

会话级临时数据存储：

```cpp
// 获取会话 Scratchpad
FConcertScratchpadRef GetScratchpad() const;

// 获取客户端专属 Scratchpad
FConcertScratchpadPtr GetClientScratchpad(const FGuid& ClientEndpointId) const;
```

Scratchpad 是一个轻量级的键值存储，用于在会话中保存临时状态，例如每个客户端的自定义数据。

## 协议追踪（Trace）

与 Unreal Insights 集成的追踪系统：

| 文件 | 说明 |
|---|---|
| `ConcertTrace.h` / `.cpp` | 主追踪接口 |
| `ConcertProtocolTrace.h` / `.cpp` | 协议级消息追踪 |
| `ConcertTraceConfig.h` | 追踪配置 |
| `ConcertScopedObjectTrace.h` | 作用域对象追踪 |

## 端点配置

```cpp
struct FConcertEndpointSettings
{
    bool bEnableLogging = false;                    // 启用详细日志
    int32 PurgeProcessedMessageDelaySeconds = 30;   // 已处理消息清理延迟
    int32 RemoteEndpointTimeoutSeconds = 60;         // 远程端点超时（最小 4 秒）
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 反射系统（UScriptStruct 等） |
| `MessagingCommon` | UE 消息系统公共基础设施 |
| `TraceLog` | Unreal Insights 追踪日志 |

## 架构图

```
┌─────────────────────────────────────────┐
│           ConcertTransport              │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Local      │  │  Remote          │  │
│  │  Endpoint   │──│  Endpoint        │  │
│  └──────┬──────┘  └──────────────────┘  │
│         │                               │
│  ┌──────┴──────┐  ┌──────────────────┐  │
│  │  Message    │  │  Identifier      │  │
│  │  Protocol   │  │  Table           │  │
│  └─────────────┘  └──────────────────┘  │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  Scratchpad │  │  Trace           │  │
│  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────┘
```
