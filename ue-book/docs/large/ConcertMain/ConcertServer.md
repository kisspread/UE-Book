# ConcertServer 模块

> 服务端模块，管理 Concert 服务器的生命周期、会话创建/归档/恢复、客户端连接审批等服务端操作。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | UncookedOnly |
| LoadingPhase | PreDefault |
| 文件数 | ~12 (.h + .cpp) |
| 依赖 | `Core`, `CoreUObject`, `ConcertTransport`, `Serialization`, `Concert` |

## 核心职责

ConcertServer 模块实现了 Concert 系统的服务端功能：

1. **服务器生命周期** — 创建、配置、启动、关闭服务器
2. **会话管理** — 创建、复制、归档、恢复、导出、重命名、销毁会话
3. **客户端连接审批** — 控制哪些客户端可以加入会话
4. **会话仓库** — 管理持久化会话存储目录
5. **事件回调** — 通过 `IConcertServerEventSink` 将会话操作委托给上层实现

## 核心接口

### IConcertServerModule

模块入口，工厂模式创建服务器实例：

```cpp
class IConcertServerModule : public IModuleInterface
{
public:
    static IConcertServerModule& Get();
    static bool IsAvailable();

    // 创建指定角色的服务器
    virtual IConcertServerRef CreateServer(
        const FString& InRole,
        const FConcertSessionFilter& InAutoArchiveSessionFilter,
        IConcertServerEventSink* InEventSink) = 0;
};
```

**参数说明：**
- `InRole` — 服务器角色（如 `"MultiUser"`, `"DisasterRecovery"`）
- `InAutoArchiveSessionFilter` — 自动归档时的会话过滤器
- `InEventSink` — 会话操作事件回调接口

### IConcertServer

服务器核心接口：

```cpp
class IConcertServer
{
public:
    // 角色
    virtual const FString& GetRole() const = 0;

    // 配置
    virtual void Configure(const UConcertServerConfig* ServerConfig) = 0;
    virtual bool IsConfigured() const = 0;
    virtual const UConcertServerConfig* GetConfiguration() const = 0;
    virtual const FConcertServerInfo& GetServerInfo() const = 0;

    // 生命周期
    virtual bool IsStarted() const = 0;
    virtual void Startup() = 0;
    virtual void Shutdown() = 0;

    // 远程管理端点
    virtual TArray<FConcertEndpointContext> GetRemoteAdminEndpoints() const = 0;
    virtual FOnConcertRemoteEndpointConnectionChanged& OnRemoteEndpointConnectionChanged() = 0;
    virtual FOnConcertParticipantCanJoinSession& OnConcertParticipantCanJoinSession() = 0;
    virtual FMessageAddress GetRemoteAddress(const FGuid& AdminEndpointId) const = 0;

    // 会话查询
    virtual FGuid GetLiveSessionIdByName(const FString& InName) const = 0;
    virtual FGuid GetArchivedSessionIdByName(const FString& InName) const = 0;
    virtual FConcertSessionInfo CreateSessionInfo() const = 0;
    virtual TArray<FConcertSessionInfo> GetLiveSessionInfos() const = 0;
    virtual TArray<FConcertSessionInfo> GetArchivedSessionInfos() const = 0;
    virtual TArray<TSharedPtr<IConcertServerSession>> GetLiveSessions() const = 0;
    virtual TSharedPtr<IConcertServerSession> GetLiveSession(const FGuid& SessionId) const = 0;
    virtual TOptional<FConcertSessionInfo> GetArchivedSessionInfo(const FGuid& SessionId) const = 0;

    // 会话操作
    virtual TSharedPtr<IConcertServerSession> CreateSession(
        const FConcertSessionInfo& SessionInfo, FText& OutFailureReason) = 0;
    virtual TSharedPtr<IConcertServerSession> CopySession(
        const FGuid& SrcSessionId, const FConcertSessionInfo& NewSessionInfo,
        const FConcertSessionFilter& SessionFilter, FText& OutFailureReason) = 0;
    virtual TSharedPtr<IConcertServerSession> RestoreSession(
        const FGuid& SessionId, const FConcertSessionInfo& SessionInfo,
        const FConcertSessionFilter& SessionFilter, FText& OutFailureReason) = 0;
    virtual FGuid ArchiveSession(
        const FGuid& SessionId, const FString& ArchiveNameOverride,
        const FConcertSessionFilter& SessionFilter, FText& OutFailureReason,
        FGuid ArchiveSessionIdOverride = FGuid::NewGuid()) = 0;
    virtual bool ExportSession(
        const FGuid& SessionId, const FConcertSessionFilter& SessionFilter,
        const FString& DestDir, bool bAnonymizeData, FText& OutFailureReason) = 0;
    virtual bool RenameSession(
        const FGuid& SessionId, const FString& NewName, FText& OutFailureReason) = 0;
    virtual bool DestroySession(const FGuid& SessionId, FText& OutFailureReason) = 0;

    // 回调
    virtual FOnConcertServerSessionStartup& OnConcertServerSessionStartup() = 0;
    virtual FOnConcertServerStartup& OnConcertServerStartup() = 0;
};
```

## 服务器配置

### UConcertServerConfig

```cpp
class UConcertServerConfig : public UObject
{
    // 归档策略
    bool bAutoArchiveOnReboot = false;   // 异常重启时自动归档
    bool bAutoArchiveOnShutdown = true;  // 正常关闭时自动归档

    // 维护设置
    bool bCleanWorkingDir;        // 启动时清理工作目录（-CONCERTCLEAN）
    int32 NumSessionsToKeep;      // 保留的归档会话数量（<0 保留全部）

    // 服务器标识
    FString ServerName;           // 服务器名称（-CONCERTSERVER=）
    FString DefaultSessionName;   // 默认会话名称（-CONCERTSESSION=）

    // 安全
    TSet<FString> AuthorizedClientKeys; // 授权客户端密钥集合

    // 会话恢复
    FString DefaultSessionToRestore; // 默认恢复会话（-CONCERTSESSIONTORESTORE=）

    // 版本信息
    FConcertSessionVersionInfo DefaultVersionInfo; // -CONCERTVERSION=

    // 会话设置
    FConcertSessionSettings DefaultSessionSettings;

    // 服务器运行时设置
    FConcertServerSettings ServerSettings;

    // 端点设置
    FConcertEndpointSettings EndpointSettings;

    // 存储目录
    FString WorkingDir;              // 活跃会话目录（-CONCERTWORKINGDIR=）
    FString ArchiveDir;              // 归档会话目录（-CONCERTSAVEDDIR=）
    FString SessionRepositoryRootDir; // 仓库根目录
    bool bMountDefaultSessionRepository = true; // 挂载默认仓库
};
```

### FConcertServerSettings

```cpp
struct FConcertServerSettings
{
    bool bIgnoreSessionSettingsRestriction = false; // 忽略会话设置限制
    int32 SessionTickFrequencySeconds = 1;          // 会话 Tick 频率
};
```

## 会话操作详解

### 创建会话

```cpp
FConcertSessionInfo Info = Server->CreateSessionInfo();
Info.SessionName = TEXT("MySession");
FText FailureReason;
TSharedPtr<IConcertServerSession> Session = Server->CreateSession(Info, FailureReason);
if (!Session) { /* 处理失败 */ }
```

### 归档会话

将活跃会话的数据持久化到归档目录：

```cpp
FText FailureReason;
FGuid ArchiveId = Server->ArchiveSession(
    LiveSessionId,
    TEXT("MyArchive"),           // 归档名称覆盖
    FConcertSessionFilter(),     // 过滤器
    FailureReason);
```

### 恢复会话

从归档恢复为新的活跃会话：

```cpp
FConcertSessionInfo NewInfo = Server->CreateSessionInfo();
NewInfo.SessionName = TEXT("RestoredSession");
FText FailureReason;
auto RestoredSession = Server->RestoreSession(
    ArchivedSessionId, NewInfo, FConcertSessionFilter(), FailureReason);
```

### 复制会话

复制活跃或归档会话为新的活跃会话（比归档+恢复更快）：

```cpp
auto CopiedSession = Server->CopySession(
    SourceSessionId, NewInfo, SessionFilter, FailureReason);
```

### 导出会将会话

将会话数据复制到外部目录，不再由服务器跟踪：

```cpp
bool bSuccess = Server->ExportSession(
    SessionId, SessionFilter,
    TEXT("/path/to/export"),  // 目标目录
    true,                     // 匿名化数据
    FailureReason);
```

## 事件回调（IConcertServerEventSink）

服务器将实际的会话数据操作委托给 `IConcertServerEventSink` 实现：

```cpp
class IConcertServerEventSink
{
public:
    // 扫描目录获取会话信息
    virtual void GetSessionsFromPath(const IConcertServer& Server,
        const FString& Path, TArray<FConcertSessionInfo>& OutInfos) = 0;

    // 会话生命周期
    virtual bool OnLiveSessionCreated(const IConcertServer& Server,
        TSharedRef<IConcertServerSession> Session,
        const FInternalLiveSessionCreationParams& Params) = 0;
    virtual void OnLiveSessionDestroyed(const IConcertServer& Server,
        TSharedRef<IConcertServerSession> Session) = 0;
    virtual bool OnArchivedSessionCreated(const IConcertServer& Server,
        const FString& Root, const FConcertSessionInfo& Info) = 0;
    virtual void OnArchivedSessionDestroyed(const IConcertServer& Server,
        const FGuid& SessionId) = 0;

    // 数据操作
    virtual bool ArchiveSession(const IConcertServer& Server,
        TSharedRef<IConcertServerSession> Session,
        const FString& ArchiveRoot, const FConcertSessionInfo& ArchiveInfo,
        const FConcertSessionFilter& Filter) = 0;
    virtual bool CopySession(const IConcertServer& Server,
        TSharedRef<IConcertServerSession> Session,
        const FString& NewRoot, const FConcertSessionFilter& Filter) = 0;
    virtual bool RestoreSession(const IConcertServer& Server,
        const FGuid& ArchiveId, const FString& LiveRoot,
        const FConcertSessionInfo& LiveInfo,
        const FConcertSessionFilter& Filter) = 0;
    virtual bool ExportSession(const IConcertServer& Server,
        const FGuid& SessionId, const FString& DestDir,
        const FConcertSessionFilter& Filter, bool bAnonymizeData) = 0;

    // 重命名
    virtual void OnLiveSessionRenamed(const IConcertServer& Server,
        TSharedRef<IConcertServerSession> Session) = 0;
    virtual void OnArchivedSessionRenamed(const IConcertServer& Server,
        const FString& Root, const FConcertSessionInfo& Info) = 0;
};
```

这意味着**实际的数据持久化逻辑不在 ConcertServer 模块中**，而是由上层插件（如 ConcertSyncServer）提供实现。

## 客户端连接审批

通过 `OnConcertParticipantCanJoinSession` 委托控制客户端是否可以加入会话：

```cpp
Server->OnConcertParticipantCanJoinSession().BindLambda(
    [](const FGuid& SessionId, const FGuid& EndpointId,
       const FConcertClientInfo& ClientInfo, FText* OutFailureReason) -> bool
    {
        // 检查客户端是否有权限加入
        if (!IsClientAllowed(ClientInfo))
        {
            if (OutFailureReason)
                *OutFailureReason = NSLOCTEXT("MyApp", "Denied", "Access denied");
            return false;
        }
        return true;
    });
```

## 服务器辅助工具

`ConcertServerUtil.h` 提供服务器相关的工具函数：

```cpp
namespace ConcertServerUtil
{
    // 获取服务器工具函数
    // （具体函数请参考源码）
}
```

## 会话仓库（Session Repository）

服务器支持多个会话仓库，用于组织和持久化会话数据：

- **挂载仓库** — 将目录注册为会话存储位置
- **默认仓库** — 新会话默认存储位置
- **仓库隔离** — 不同服务器实例可以挂载不同仓库
- **仓库删除** — 删除仓库及其所有会话数据

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 反射 |
| `ConcertTransport` | 底层传输 |
| `Serialization` | 序列化支持 |
| `Concert` | 会话接口、管理消息、事件回调 |

## 架构图

```
┌─────────────────────────────────────────────┐
│              ConcertServer                  │
│                                             │
│  ┌─────────────┐    ┌────────────────────┐  │
│  │ IConcert    │    │ IConcertServer     │  │
│  │ ServerModule│───→│ (IConcertServerRef)│  │
│  └─────────────┘    └────────┬───────────┘  │
│                              │              │
│         ┌────────────────────┼────────┐     │
│         │                    │        │     │
│  ┌──────┴──────┐  ┌─────────┴──┐  ┌──┴───┐ │
│  │ Server      │  │ Session    │  │Event │ │
│  │ Config      │  │ Lifecycle  │  │Sink  │ │
│  │ (UConcert   │  │ (Create/   │  │(外部 │ │
│  │ ServerConfig│  │  Archive/  │  │ 实现)│ │
│  │ )           │  │  Restore)  │  │      │ │
│  └─────────────┘  └────────────┘  └──────┘ │
└─────────────────────────────────────────────┘
```
