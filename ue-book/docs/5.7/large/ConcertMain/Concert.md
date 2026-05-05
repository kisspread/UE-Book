# Concert 模块

> 核心会话抽象层，定义会话接口、管理消息和事件，是 Client/Server 模块的共享基础。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | UncookedOnly |
| LoadingPhase | PreDefault |
| 文件数 | ~20 (.h + .cpp) |
| 依赖 | `Core`, `CoreUObject`, `ConcertTransport`, `Serialization` |

## 核心职责

Concert 模块是 Client 和 Server 之间的**共享抽象层**，定义了：

1. **会话接口** — `IConcertSession`、`IConcertClientSession`、`IConcertServerSession`
2. **管理消息** — 所有 `FConcertAdmin_*` 请求/响应结构体
3. **会话数据** — 会话信息、客户端信息、过滤器等核心数据结构
4. **自定义消息** — 会话级自定义事件和请求的处理器框架
5. **服务器事件** — 会话生命周期事件的全局委托

## 核心接口

### IConcertSession

所有会话的基类接口：

```cpp
class IConcertSession
{
public:
    // 生命周期
    virtual void Startup() = 0;
    virtual void Shutdown() = 0;

    // 会话信息
    virtual const FGuid& GetId() const = 0;
    virtual const FString& GetName() const = 0;
    virtual const FConcertSessionInfo& GetSessionInfo() const = 0;
    virtual FString GetSessionWorkingDirectory() const = 0;

    // 客户端管理
    virtual TArray<FGuid> GetSessionClientEndpointIds() const = 0;
    virtual TArray<FConcertSessionClientInfo> GetSessionClients() const = 0;
    virtual bool FindSessionClient(const FGuid& EndpointId,
        FConcertSessionClientInfo& OutSessionClientInfo) const = 0;

    // Scratchpad
    virtual FConcertScratchpadRef GetScratchpad() const = 0;
    virtual FConcertScratchpadPtr GetClientScratchpad(const FGuid& ClientEndpointId) const = 0;

    // 自定义事件（模板接口）
    template<typename EventType>
    FDelegateHandle RegisterCustomEventHandler(/*...*/);
    template<typename EventType>
    void SendCustomEvent(const EventType& Event, const FGuid& DestEndpointId,
        EConcertMessageFlags Flags, TOptional<FConcertSequencedCustomEvent> SequencedId = {});

    // 自定义请求/响应（模板接口）
    template<typename RequestType, typename ResponseType>
    void RegisterCustomRequestHandler(/*...*/);
    template<typename RequestType, typename ResponseType>
    TFuture<ResponseType> SendCustomRequest(const RequestType& Request,
        const FGuid& DestinationEndpointId);
};
```

### IConcertClientSession

客户端会话接口，扩展了 `IConcertSession`：

```cpp
class IConcertClientSession : public IConcertSession
{
public:
    // 连接状态
    virtual EConcertConnectionStatus GetConnectionStatus() const = 0;
    virtual FGuid GetSessionClientEndpointId() const = 0;
    virtual FGuid GetSessionServerEndpointId() const = 0;

    // 客户端信息
    virtual const FConcertClientInfo& GetLocalClientInfo() const = 0;
    virtual void UpdateLocalClientInfo(const FConcertClientInfoUpdate& UpdatedFields) = 0;

    // 连接控制
    virtual void Connect() = 0;
    virtual void Disconnect() = 0;

    // 发送/接收状态
    virtual EConcertSendReceiveState GetSendReceiveState() const = 0;
    virtual void SetSendReceiveState(EConcertSendReceiveState InSendReceiveState) = 0;

    // 有序事件管理器
    virtual FConcertSequencedCustomEventManager& GetSequencedEventManager() = 0;

    // 回调委托
    virtual FOnConcertClientSessionTick& OnTick() = 0;
    virtual FOnConcertClientSessionConnectionChanged& OnConnectionChanged() = 0;
    virtual FOnConcertClientSessionClientChanged& OnSessionClientChanged() = 0;
    virtual FOnConcertSessionRenamed& OnSessionRenamed() = 0;
};
```

### IConcertServerSession

服务端会话接口：

```cpp
class IConcertServerSession : public IConcertSession
{
public:
    virtual void SetName(const FString& NewName) = 0;
    virtual FMessageAddress GetClientAddress(const FGuid& ClientEndpointId) const = 0;
    virtual FOnConcertServerSessionTick& OnTick() = 0;
    virtual FOnConcertServerSessionClientChanged& OnSessionClientChanged() = 0;
    virtual FOnConcertMessageAcknowledgementReceivedFromLocalEndpoint&
        OnConcertMessageAcknowledgementReceived() = 0;
};
```

## 连接状态枚举

```cpp
enum class EConcertConnectionStatus : uint8
{
    Connecting,     // 正在连接
    Connected,      // 已连接
    Disconnecting,  // 正在断开
    Disconnected,   // 已断开
};

enum class EConcertSendReceiveState : uint8
{
    Default,      // 全双工
    SendOnly,     // 仅发送（本地事务发送但暂停接收）
    ReceiveOnly,  // 仅接收（暂停本地事务，接收远程更新）
};
```

## 管理消息（Admin Messages）

所有 `FConcertAdmin_*` 消息结构体定义在此模块中，用于客户端与服务器之间的管理操作：

### 服务器发现

| 消息 | 方向 | 说明 |
|---|---|---|
| `FConcertAdmin_DiscoverServersEvent` | Client → Server | 发现服务器（含角色、版本、认证 key） |
| `FConcertAdmin_ServerDiscoveredEvent` | Server → Client | 服务器响应发现 |

### 会话 CRUD

| 消息 | 说明 |
|---|---|
| `FConcertAdmin_CreateSessionRequest` | 创建新会话 |
| `FConcertAdmin_FindSessionRequest` | 按 ID 查找会话 |
| `FConcertAdmin_CopySessionRequest` | 复制/恢复会话 |
| `FConcertAdmin_ArchiveSessionRequest` | 归档活跃会话 |
| `FConcertAdmin_RenameSessionRequest` | 重命名会话 |
| `FConcertAdmin_DeleteSessionRequest` | 删除单个会话 |
| `FConcertAdmin_BatchDeleteSessionRequest` | 批量删除会话 |
| `FConcertAdmin_GetAllSessionsRequest` | 获取所有会话（活跃 + 归档） |
| `FConcertAdmin_GetLiveSessionsRequest` | 获取活跃会话列表 |
| `FConcertAdmin_GetArchivedSessionsRequest` | 获取归档会话列表 |

### 会话仓库（Repository）

| 消息 | 说明 |
|---|---|
| `FConcertAdmin_MountSessionRepositoryRequest` | 挂载会话仓库 |
| `FConcertAdmin_GetSessionRepositoriesRequest` | 获取仓库列表 |
| `FConcertAdmin_DropSessionRepositoriesRequest` | 删除仓库 |

## 核心数据结构

### FConcertSessionInfo

会话的完整描述信息：

```cpp
struct FConcertSessionInfo
{
    FGuid ServerInstanceId;
    FGuid ServerEndpointId;
    FGuid OwnerInstanceId;
    FGuid SessionId;
    FString SessionName;
    FString OwnerUserName;
    FString OwnerDeviceName;
    FConcertSessionSettings Settings;
    TArray<FConcertSessionVersionInfo> VersionInfos;
    EConcertSessionState State;
};
```

### FConcertClientInfo

客户端描述信息：

```cpp
struct FConcertClientInfo
{
    FConcertInstanceInfo InstanceInfo;
    FString DeviceName;
    FString PlatformName;
    FString UserName;
    FString DisplayName;
    FLinearColor AvatarColor;
    FString DesktopAvatarActorClass;
    FString VRAvatarActorClass;
    bool bHasEditorData;
    bool bRequiresCookedData;
};
```

### FConcertSessionFilter

会话过滤器，用于归档/复制/恢复时筛选活动：

```cpp
struct FConcertSessionFilter
{
    int64 ActivityIdLowerBound = 1;
    int64 ActivityIdUpperBound = MAX_int64;
    TArray<int64> ActivityIdsToExclude;
    TArray<int64> ActivityIdsToInclude;
    bool bOnlyLiveData = false;
    bool bMetaDataOnly = false;
    bool bIncludeIgnoredActivities = false;
};
```

## 自定义消息框架

会话支持注册自定义事件和请求处理器，用于扩展 Concert 协议：

```cpp
// 自定义事件（Fire-and-forget）
struct FMyCustomEvent : public FConcertEventData
{
    GENERATED_BODY()
    FString Payload;
};

// 注册处理器
Session->RegisterCustomEventHandler<FMyCustomEvent>(
    [](const FConcertSessionContext& Context, const FMyCustomEvent& Event)
    {
        // 处理事件
    });

// 发送事件
Session->SendCustomEvent(MyEvent, TargetEndpointId, EConcertMessageFlags::ReliableOrdered);

// 自定义请求/响应
struct FMyRequest : public FConcertRequestData { GENERATED_BODY() };
struct FMyResponse : public FConcertResponseData { GENERATED_BODY() };

Session->RegisterCustomRequestHandler<FMyRequest, FMyResponse>(
    [](const FConcertSessionContext& Context, const FMyRequest& Req, FMyResponse& Resp)
        -> EConcertSessionResponseCode
    {
        return EConcertSessionResponseCode::Success;
    });

// 发送请求
TFuture<FMyResponse> Future = Session->SendCustomRequest<FMyRequest, FMyResponse>(
    MyRequest, ServerEndpointId);
```

### 有序事件管理

`FConcertSequencedCustomEventManager` 确保自定义事件按序发送：

```cpp
// 预留顺序槽位
FConcertSequencedCustomEvent SeqEvent = EventManager.AddSequencedCustomEvent();

// 填充事件数据（异步操作完成后）
EventManager.FillPendingSequenceEvent(SeqEvent, PendingEventData);

// 按序弹出并发送
while (TOptional<FPendingCustomEvent> Event = EventManager.PopSendEvent())
{
    // 发送事件
}
```

## 服务器事件（全局委托）

`ConcertServerEvents` 命名空间提供全局多播委托，监听服务器级会话生命周期事件：

```cpp
namespace ConcertServerEvents
{
    FOnLiveSessionCreated& OnLiveSessionCreated();
    FOnArchivedSessionCreated& OnArchivedSessionCreated();
    FOnLiveSessionDestroyed& OnLiveSessionDestroyed();
    FOnArchivedSessionDestroyed& OnArchivedSessionDestroyed();
    FArchiveSession_WithSession& ArchiveSession_WithSession();
    FCopySession& CopySession();
    FExportSession& ExportSession();
    FRestoreSession& RestoreSession();
    FOnLiveSessionRenamed& OnLiveSessionRenamed();
    FOnArchivedSessionRenamed& OnArchivedSessionRenamed();
}
```

## 会话设置

```cpp
struct FConcertSessionSettings
{
    FString ProjectName;       // 项目名（-CONCERTPROJECT=）
    uint32 BaseRevision = 0;   // 基础修订号（-CONCERTREVISION=）
    FString ArchiveNameOverride; // 归档名称覆盖（-CONCERTSAVESESSIONAS=）
};
```

## 会话数据压缩

`ConcertMessageData.h` 中定义了完整的压缩框架：

```cpp
enum class EConcertCompressionDetails : uint8
{
    Uncompressed = 0,
    Compressed = 1 << 0,
    CompressWithOodle = 1 << 1,
    CompressForSpeed = 1 << 2,
    CompressForSize = 1 << 3
};
```

支持 Zlib 和 Oodle 两种压缩算法，可通过控制台变量配置。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 反射（USTRUCT、UPROPERTY） |
| `ConcertTransport` | 底层传输层（端点、消息协议） |
| `Serialization` | 序列化支持 |

## IConcertModule

模块单例入口：

```cpp
// 获取模块实例
IConcertModule& Module = IConcertModule::Get();

// 检查模块是否可用
if (IConcertModule::IsAvailable()) { /* ... */ }
```
