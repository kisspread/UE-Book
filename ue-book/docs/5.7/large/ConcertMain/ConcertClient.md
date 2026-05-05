# ConcertClient 模块

> 客户端模块，管理与 Concert 服务器的连接、会话发现、创建/加入/复制/归档会话等客户端操作。

## 模块信息

| 属性 | 值 |
|---|---|
| 类型 | UncookedOnly |
| LoadingPhase | PreDefault |
| 文件数 | ~10 (.h + .cpp) |
| 依赖 | `Core`, `CoreUObject`, `ConcertTransport`, `Serialization`, `Concert` |
| 私有依赖 | `GameplayTags`, `Engine` |

## 核心职责

ConcertClient 模块实现了 Concert 系统的客户端侧功能：

1. **客户端生命周期** — 创建、配置、启动、关闭客户端
2. **服务器发现** — 通过 UDP 广播发现局域网内的 Concert 服务器
3. **会话管理** — 创建、加入、复制、归档、恢复、删除会话
4. **连接管理** — 自动连接、连接任务管线、错误处理
5. **发送/接收控制** — 支持只读/只发/全双工模式切换

## 核心接口

### IConcertClientModule

模块入口，工厂模式创建客户端实例：

```cpp
class IConcertClientModule : public IModuleInterface
{
public:
    // 单例访问
    static IConcertClientModule& Get();
    static bool IsAvailable();

    // 创建指定角色的客户端
    virtual IConcertClientRef CreateClient(const FString& InRole) = 0;
};
```

**角色（Role）** 示例：`"MultiUser"`, `"DisasterRecovery"` 等，用于区分客户端用途。

### IConcertClient

客户端核心接口：

```cpp
class IConcertClient
{
public:
    // 角色
    virtual const FString& GetRole() const = 0;

    // 配置
    virtual void Configure(const UConcertClientConfig* InSettings) = 0;
    virtual bool IsConfigured() const = 0;
    virtual const UConcertClientConfig* GetConfiguration() const = 0;
    virtual const FConcertClientInfo& GetClientInfo() const = 0;

    // 生命周期
    virtual bool IsStarted() const = 0;
    virtual void Startup() = 0;
    virtual void Shutdown() = 0;

    // 服务器发现
    virtual bool IsDiscoveryEnabled() const = 0;
    virtual void StartDiscovery() = 0;
    virtual void StopDiscovery() = 0;
    virtual TArray<FConcertServerInfo> GetKnownServers() const = 0;
    virtual FSimpleMulticastDelegate& OnKnownServersUpdated() = 0;

    // 自动连接
    virtual bool CanAutoConnect() const = 0;
    virtual bool IsAutoConnecting() const = 0;
    virtual void StartAutoConnect() = 0;
    virtual void StopAutoConnect() = 0;

    // 会话操作
    virtual TFuture<EConcertResponseCode> CreateSession(
        const FGuid& ServerAdminEndpointId,
        const FConcertCreateSessionArgs& Args) = 0;
    virtual TFuture<EConcertResponseCode> JoinSession(
        const FGuid& ServerAdminEndpointId,
        const FGuid& SessionId) = 0;
    virtual TFuture<EConcertResponseCode> RestoreSession(
        const FGuid& ServerAdminEndpointId,
        const FConcertCopySessionArgs& Args) = 0;
    virtual TFuture<EConcertResponseCode> CopySession(
        const FGuid& ServerAdminEndpointId,
        const FConcertCopySessionArgs& Args) = 0;
    virtual TFuture<EConcertResponseCode> ArchiveSession(
        const FGuid& ServerAdminEndpointId,
        const FConcertArchiveSessionArgs& Args) = 0;
    virtual TFuture<EConcertResponseCode> RenameSession(
        const FGuid& ServerAdminEndpointId,
        const FGuid& SessionId, const FString& NewName) = 0;
    virtual TFuture<EConcertResponseCode> DeleteSession(
        const FGuid& ServerAdminEndpointId,
        const FGuid& SessionId) = 0;
    virtual TFuture<FConcertAdmin_BatchDeleteSessionResponse> BatchDeleteSessions(
        const FGuid& ServerAdminEndpointId,
        const FConcertBatchDeleteSessionsArgs& Args) = 0;

    // 当前会话
    virtual void DisconnectSession() = 0;
    virtual TSharedPtr<IConcertClientSession> GetCurrentSession() const = 0;
    virtual EConcertConnectionStatus GetSessionConnectionStatus() const = 0;

    // 发送/接收状态
    virtual EConcertSendReceiveState GetSendReceiveState() const = 0;
    virtual void SetSendReceiveState(EConcertSendReceiveState InSendReceiveState) = 0;

    // 会话仓库
    virtual TFuture<FConcertAdmin_MountSessionRepositoryResponse> MountSessionRepository(
        const FGuid& ServerAdminEndpointId, const FString& RepositoryRootDir,
        const FGuid& RepositoryId, bool bCreateIfNotExist, bool bAsDefault = false) const = 0;
    virtual TFuture<FConcertAdmin_GetSessionRepositoriesResponse> GetSessionRepositories(
        const FGuid& ServerAdminEndpointId) const = 0;
    virtual TFuture<FConcertAdmin_DropSessionRepositoriesResponse> DropSessionRepositories(
        const FGuid& ServerAdminEndpointId, const TArray<FGuid>& RepositoryIds) const = 0;

    // 会话查询
    virtual TFuture<FConcertAdmin_GetAllSessionsResponse> GetServerSessions(
        const FGuid& ServerAdminEndpointId) const = 0;
    virtual TFuture<FConcertAdmin_GetSessionsResponse> GetLiveSessions(
        const FGuid& ServerAdminEndpointId) const = 0;
    virtual TFuture<FConcertAdmin_GetSessionsResponse> GetArchivedSessions(
        const FGuid& ServerAdminEndpointId) const = 0;
    virtual TFuture<FConcertAdmin_GetSessionClientsResponse> GetSessionClients(
        const FGuid& ServerAdminEndpointId, const FGuid& SessionId) const = 0;
    virtual TFuture<FConcertAdmin_GetSessionActivitiesResponse> GetSessionActivities(
        const FGuid& ServerAdminEndpointId, const FGuid& SessionId,
        int64 FromActivityId, int64 ActivityCount, bool bIncludeDetails) const = 0;

    // 委托
    virtual FOnConcertClientSessionStartupOrShutdown& OnSessionStartup() = 0;
    virtual FOnConcertClientSessionStartupOrShutdown& OnSessionShutdown() = 0;
    virtual FOnConcertClientSessionGetPreConnectionTasks& OnGetPreConnectionTasks() = 0;
    virtual FOnConcertClientSessionConnectionChanged& OnSessionConnectionChanged() = 0;
};
```

## 连接任务管线

`IConcertClientConnectionTask` 定义连接过程中可扩展的验证任务：

```cpp
class IConcertClientConnectionTask
{
public:
    virtual void Execute() = 0;
    virtual void Abort() = 0;
    virtual void Tick(EConcertConnectionTaskAction TaskAction) = 0;
    virtual bool CanCancel() const = 0;
    virtual EConcertResponseCode GetStatus() const = 0;
    virtual FText GetDescription() const = 0;
    virtual FText GetPrompt() const = 0;
    virtual FConcertConnectionError GetError() const = 0;
};
```

### 连接错误码

| 错误码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 预连接验证被用户取消 |
| 2 | 连接尝试被用户中止 |
| 3 | 服务器未响应（超时） |
| 4 | 服务器拒绝连接请求 |
| 100 | 工作区验证未知错误 |
| 110-112 | 源码管理验证错误 |
| 113 | 发现未保存的脏包 |

通过 `OnGetPreConnectionTasks` 委托可以注入自定义验证任务（如源码管理检查、脏包检查等）。

## 客户端配置

### UConcertClientConfig

```cpp
class UConcertClientConfig : public UObject
{
    bool bIsHeadless;               // 无头模式（不显示 UI）
    bool bInstallEditorToolbarButton; // 安装编辑器工具栏按钮
    bool bAutoConnect;              // 自动连接（-CONCERTAUTOCONNECT）
    bool bRetryAutoConnectOnError;  // 自动重试（-CONCERTRETRYAUTOCONNECTONERROR）
    EConcertServerType ServerType;  // Console 或 Slate 服务器
    FString DefaultServerURL;       // 默认服务器（-CONCERTSERVER=）
    FString DefaultSessionName;     // 默认会话（-CONCERTSESSION=）
    FString DefaultSessionToRestore; // 默认恢复会话（-CONCERTSESSIONTORESTORE=）
    FString DefaultSaveSessionAs;   // 默认保存名称（-CONCERTSAVESESSIONAS=）
    FGameplayTagContainer ReadOnlyAssignment;  // 只读角色
    FGameplayTagContainer SendOnlyAssignment;  // 只发角色
    bool bShouldPromptForHotReloadOnLevel; // 热重载提示
    FConcertClientSettings ClientSettings;   // 客户端详细设置
    FConcertSourceControlSettings SourceControlSettings; // 源码管理设置
    FConcertEndpointSettings EndpointSettings; // 端点设置
};
```

### FConcertClientSettings

```cpp
struct FConcertClientSettings
{
    FString DisplayName;              // 显示名称（-CONCERTDISPLAYNAME=）
    FLinearColor AvatarColor;         // 头像颜色
    FSoftClassPath DesktopAvatarActorClass; // 桌面头像 Actor 类
    FSoftClassPath VRAvatarActorClass;      // VR 头像 Actor 类
    uint16 ServerPort;                // 服务器端口
    int32 DiscoveryTimeoutSeconds;    // 发现超时（默认 5 秒）
    int32 SessionTickFrequencySeconds; // 会话 Tick 频率（默认 1 秒）
    float LatencyCompensationMs;     // 延迟补偿（毫秒）
    bool bSupportMixedBuildTypes;    // 混合构建类型支持
    TArray<FName> Tags;              // 分类标签
    FString ClientAuthenticationKey; // 认证密钥
};
```

### 源码管理验证模式

```cpp
enum class EConcertSourceValidationMode : uint8
{
    Hard,            // 有任何变更则连接失败
    Soft,            // 警告并提示用户（内存变更热重载）
    SoftAutoProceed, // Soft + 自动继续
};
```

## C++ 使用示例

### 创建并启动客户端

```cpp
#include "IConcertClientModule.h"
#include "IConcertClient.h"

// 获取模块
IConcertClientModule& ClientModule = IConcertClientModule::Get();

// 创建 MultiUser 角色的客户端
IConcertClientPtr Client = ClientModule.CreateClient(TEXT("MultiUser"));

// 配置
UConcertClientConfig* Config = NewObject<UConcertClientConfig>();
Config->DefaultServerURL = TEXT("MyServer");
Config->DefaultSessionName = TEXT("MySession");
Config->ClientSettings.DisplayName = TEXT("MyEditor");
Client->Configure(Config);

// 启动
Client->Startup();

// 开始发现服务器
Client->StartDiscovery();

// 获取已发现的服务器
TArray<FConcertServerInfo> Servers = Client->GetKnownServers();
```

### 创建并加入会话

```cpp
// 创建会话
FConcertCreateSessionArgs CreateArgs;
CreateArgs.SessionName = TEXT("MySession");
TFuture<EConcertResponseCode> Future = Client->CreateSession(
    ServerAdminEndpointId, CreateArgs);

// 或加入已有会话
TFuture<EConcertResponseCode> JoinFuture = Client->JoinSession(
    ServerAdminEndpointId, ExistingSessionId);
```

### 监听连接状态变化

```cpp
Client->OnSessionConnectionChanged().AddLambda(
    [](IConcertClientSession& Session, EConcertConnectionStatus Status)
    {
        if (Status == EConcertConnectionStatus::Connected)
        {
            // 已连接，可以开始工作
        }
    });
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础引擎功能 |
| `CoreUObject` | UObject 反射 |
| `ConcertTransport` | 底层传输 |
| `Serialization` | 序列化支持 |
| `Concert` | 会话接口和管理消息 |
| `GameplayTags` (Private) | 角色标签系统 |
| `Engine` (Private) | 引擎核心功能 |
