# Concert - Main

> Allow collaborative multi-users sessions in the Editor

| 属性 | 值 |
|---|---|
| 中文名 | 多人协作主模块 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Concert` (UncookedOnly), `ConcertClient` (UncookedOnly), `ConcertServer` (UncookedOnly), `ConcertTransport` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2019-01-10 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain) | |

## 用途

ConcertMain 是 Unreal Engine **多用户协作编辑（Multi-User Editing）** 的服务端核心实现。它提供了一个基于消息的会话服务器框架，允许多个编辑器实例连接到同一个"会话"中，实时同步资产编辑操作。

该插件解决了以下核心问题：

- **会话生命周期管理**：创建、销毁、归档、恢复、复制、导出协作会话
- **客户端连接管理**：追踪连接的客户端、验证加入权限、处理断线重连
- **会话数据持久化**：将活跃会话保存到磁盘工作目录，归档会话到持久存储目录
- **会话仓库管理**：支持挂载/卸载多个会话存储仓库，实现数据的灵活组织
- **文件共享**：通过文件共享服务让多个客户端高效共享大型资产文件，避免通过网络传输

该插件**默认关闭**且标记为**实验性/Beta**，仅在特定程序目标（`UnrealMultiUserServer`、`LiveLinkHub` 等）中加载，不参与普通游戏打包。

## 使用场景

- 你正在开发需要多人实时协作编辑关卡的项目 → 部署 UnrealMultiUserServer，使用 ConcertServer 管理会话
- 你需要将编辑器修改归档并在之后恢复 → 使用 `ArchiveSession` / `RestoreSession`
- 你需要灾恢复协作会话数据 → 配置 `bAutoArchiveOnReboot`，服务器重启后自动归档残留会话
- 你需要在多人协作中高效共享大型资产 → 启用 `bEnableFileSharing` 配置文件共享路径
- 你在开发 `LiveLinkHub` 或 `CrashReportClientEditor` 等工具程序 → 该插件提供底层会话通信框架

## 蓝图用法

⚠️ 本插件为 **UncookedOnly** 类型，仅在未打包的编辑器及特定服务端程序中可用。由于目标程序为 C++ 服务进程，**不提供蓝图可调用接口**。所有功能通过 C++ API 访问。

## C++ 用法

### 头文件引入

```cpp
// 服务器模块接口
#include "IConcertServerModule.h"
#include "IConcertServer.h"

// 服务器配置
#include "ConcertServerSettings.h"

// 会话相关
#include "IConcertServerSession.h" // 来自 Concert 模块

// 工具函数
#include "ConcertServerUtil.h"
```

### 基本用法 — 创建和启动服务器

通过 `IConcertServerModule` 单例创建服务器实例并启动。

```cpp
#include "IConcertServerModule.h"
#include "ConcertServerSettings.h"

// 获取服务器模块
IConcertServerModule& ConcertServerModule = IConcertServerModule::Get();

// 创建服务器，指定角色（如 "MultiUser"）和自动归档过滤器
FConcertSessionFilter AutoArchiveFilter;
IConcertServerRef Server = ConcertServerModule.CreateServer(
    TEXT("MultiUser"),
    AutoArchiveFilter,
    /*InEventSink=*/ nullptr
);

// 配置服务器
UConcertServerConfig* Config = GetMutableDefault<UConcertServerConfig>();
Config->ServerName = TEXT("MyMultiUserServer");
Config->DefaultSessionName = TEXT("DefaultSession");
Config->bAutoArchiveOnShutdown = true;
Config->NumSessionsToKeep = 10;

Server->Configure(Config);

// 启动服务器
Server->Startup();

// 获取服务器信息
const FConcertServerInfo& Info = Server->GetServerInfo();
```

*来源: Public/IConcertServerModule.h, Public/IConcertServer.h*

### 基本用法 — 创建和管理会话

```cpp
// 创建新会话
FText FailureReason;
FConcertSessionInfo SessionInfo = Server->CreateSessionInfo();
SessionInfo.SessionName = TEXT("MySession");
TSharedPtr<IConcertServerSession> Session = Server->CreateSession(SessionInfo, FailureReason);

if (Session.IsValid())
{
    // 启动会话
    Session->Startup();

    // 获取会话 ID
    const FGuid& SessionId = Session->GetId();

    // 获取连接的客户端列表
    TArray<FConcertSessionClientInfo> Clients = Session->GetSessionClients();

    // 监听会话 Tick
    Session->OnTick().AddLambda([](float DeltaSeconds)
    {
        // 处理每帧会话更新逻辑
    });

    // 监听客户端状态变化
    Session->OnSessionClientChanged().AddLambda([](const FGuid& ClientEndpointId)
    {
        // 处理客户端连接/断开
    });
}

// 列出所有活跃会话
TArray<FConcertSessionInfo> LiveSessions = Server->GetLiveSessionInfos();

// 列出所有归档会话
TArray<FConcertSessionInfo> ArchivedSessions = Server->GetArchivedSessionInfos();
```

*来源: Public/IConcertServer.h, Private/ConcertServerSession.h*

### 进阶用法 — 会话归档与恢复

```cpp
// 归档活跃会话
FText FailureReason;
FGuid ArchivedSessionId = Server->ArchiveSession(
    LiveSessionId,
    TEXT("SessionBackup_2026"),
    FConcertSessionFilter(), // 不过滤，归档全部活动
    FailureReason
);

if (ArchivedSessionId.IsValid())
{
    // 从归档恢复为新会话
    FConcertSessionInfo NewSessionInfo = Server->CreateSessionInfo();
    NewSessionInfo.SessionName = TEXT("RestoredSession");

    TSharedPtr<IConcertServerSession> RestoredSession = Server->RestoreSession(
        ArchivedSessionId,
        NewSessionInfo,
        FConcertSessionFilter(),
        FailureReason
    );
}

// 复制会话（直接从源会话创建新活跃会话，比归档+恢复更快）
TSharedPtr<IConcertServerSession> CopiedSession = Server->CopySession(
    SrcSessionId,
    NewSessionInfo,
    FConcertSessionFilter(),
    FailureReason
);

// 导出会话数据到指定目录
bool bExported = Server->ExportSession(
    SessionId,
    FConcertSessionFilter(),
    TEXT("/path/to/export/dir"),
    /*bAnonymizeData=*/ true, // 匿名化对象和包名
    FailureReason
);

// 重命名会话
Server->RenameSession(SessionId, TEXT("NewSessionName"), FailureReason);

// 销毁会话（自动检测是活跃还是归档）
Server->DestroySession(SessionId, FailureReason);
```

*来源: Public/IConcertServer.h*

### 进阶用法 — 客户端加入验证与权限控制

```cpp
// 注册回调：验证客户端是否可以加入会话
Server->OnConcertParticipantCanJoinSession().BindLambda(
    [](const FGuid& SessionId, const FGuid& EndpointId, const FConcertClientInfo& ClientInfo, FText* OutFailureReason) -> bool
    {
        // 自定义权限检查逻辑
        if (ClientInfo.ClientName.Contains(TEXT("ReadOnly")))
        {
            if (OutFailureReason)
            {
                *OutFailureReason = NSLOCTEXT("MyServer", "ReadOnlyDenied", "Read-only users cannot join.");
            }
            return false;
        }
        return true;
    }
);

// 监听远程管理端点连接变化
Server->OnRemoteEndpointConnectionChanged().AddLambda(
    [](const FConcertEndpointContext& EndpointContext, EConcertRemoteEndpointConnection Connection)
    {
        // 处理管理端点连接/断开
    }
);

// 配置授权客户端密钥（白名单机制）
UConcertServerConfig* Config = GetMutableDefault<UConcertServerConfig>();
Config->AuthorizedClientKeys.Add(TEXT("TeamAlpha"));
Config->AuthorizedClientKeys.Add(TEXT("TeamBeta"));
// 空集合表示允许所有客户端连接
```

*来源: Public/IConcertServer.h, Public/ConcertServerSettings.h*

### 进阶用法 — 使用工具函数

```cpp
#include "ConcertServerUtil.h"

// 获取指定会话中的所有客户端
TArray<FConcertSessionClientInfo> Clients = ConcertUtil::GetSessionClients(
    *Server, SessionId
);

// 根据客户端端点 ID 查找其所在的活跃会话
TSharedPtr<IConcertServerSession> ClientSession = ConcertUtil::GetLiveSessionClientConnectedTo(
    *Server, ClientEndpointId
);
```

*来源: Public/ConcertServerUtil.h*

## Demo 示例

一个最小的多用户协作服务器初始化示例：

```cpp
// MyMultiUserServer.h
#pragma once

#include "CoreMinimal.h"

class IConcertServer;

class FMyMultiUserServer
{
public:
    void Initialize();
    void Shutdown();

private:
    TSharedPtr<IConcertServer> Server;
};
```

```cpp
// MyMultiUserServer.cpp
#include "MyMultiUserServer.h"
#include "IConcertServerModule.h"
#include "IConcertServer.h"
#include "ConcertServerSettings.h"
#include "ConcertMessages.h"

void FMyMultiUserServer::Initialize()
{
    if (!IConcertServerModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("ConcertServer module is not available."));
        return;
    }

    IConcertServerModule& Module = IConcertServerModule::Get();

    // 创建服务器，角色为 "MultiUser"
    FConcertSessionFilter AutoArchiveFilter;
    Server = Module.CreateServer(TEXT("MultiUser"), AutoArchiveFilter, nullptr).ToSharedPtr();

    if (!Server.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create Concert server."));
        return;
    }

    // 配置服务器
    UConcertServerConfig* Config = GetMutableDefault<UConcertServerConfig>();
    Config->ServerName = TEXT("MyMUServer");
    Config->DefaultSessionName = TEXT("DefaultSession");
    Config->bAutoArchiveOnShutdown = true;
    Config->NumSessionsToKeep = 5;
    Config->bCleanWorkingDir = false;

    Server->Configure(Config);

    // 注册客户端加入验证
    Server->OnConcertParticipantCanJoinSession().BindLambda(
        [](const FGuid& SessionId, const FGuid& EndpointId,
           const FConcertClientInfo& ClientInfo, FText* OutFailureReason) -> bool
        {
            UE_LOG(LogTemp, Log, TEXT("Client '%s' requesting to join session %s"),
                *ClientInfo.ClientName, *SessionId.ToString());
            return true; // 允许所有客户端加入
        }
    );

    // 注册会话创建回调
    Server->OnConcertServerSessionStartup().AddLambda(
        [](TWeakPtr<IConcertServerSession> WeakSession)
        {
            if (TSharedPtr<IConcertServerSession> Session = WeakSession.Pin())
            {
                UE_LOG(LogTemp, Log, TEXT("Session '%s' started with ID: %s"),
                    *Session->GetName(), *Session->GetId().ToString());
            }
        }
    );

    // 启动服务器
    Server->Startup();

    // 创建默认会话
    FText FailureReason;
    FConcertSessionInfo SessionInfo = Server->CreateSessionInfo();
    SessionInfo.SessionName = Config->DefaultSessionName;
    TSharedPtr<IConcertServerSession> Session = Server->CreateSession(SessionInfo, FailureReason);

    if (Session.IsValid())
    {
        Session->Startup();
        UE_LOG(LogTemp, Log, TEXT("Default session created: %s"), *Session->GetId().ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to create default session: %s"),
            *FailureReason.ToString());
    }
}

void FMyMultiUserServer::Shutdown()
{
    if (Server.IsValid())
    {
        Server->Shutdown();
        Server.Reset();
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Concert` | Concert 共享核心模块，提供会话接口 (`IConcertServerSession`)、消息定义、通用实现 |
| `ConcertTransport` | Concert 传输层，提供端点（Endpoint）通信基础设施 |
| `ConcertShared` | 共享数据结构和工具（FConcertSessionInfo、FConcertEndpointContext 等） |
| `Json` | 会话数据序列化（数据库、配置持久化） |
| `Serialization` | 数据序列化支持 |

无特殊依赖（仅标准 Core/Engine/Json/Serialization 等）。客户端模块 `ConcertClient` 额外依赖 `Concert` 和 `ConcertTransport`，但不需要由服务器使用者直接引用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新的 UE_LOGF 格式 |
| 2026-04-02 | `5cc4482f` | Add descriptions to trace channels and a few other places. | 为追踪通道添加描述信息 |
| 2026-03-10 | `a69ab07d` | [IsSavingPackage] | 保存包状态相关改动 |
| 2025-12-10 | `11a770db` | Specify FConcertSessionChallengeData::ChallengeKey should be ignored when running member initializat | 明确 ChallengeKey 在成员初始化时应被忽略 |
| 2025-12-08 | `ce8c0205` | Implements a file sharing system that can be used with Multi-user. FConcertCloudSharingService will | 实现基于云的文件共享系统，用于多用户协作中的大型资产共享 |

### 维护评价

**状态：活跃维护中（Beta）**

- **活跃度**：插件持续获得更新，2026 年 4 月仍有实质性改动（日志迁移、追踪通道描述等），2025 年 12 月还实现了新的文件共享系统
- **成熟度**：虽然已存在约 7 年，但仍标记为 `IsBetaVersion=true`，说明 API 可能不稳定
- **特殊性**：默认关闭（`EnabledByDefault=false`），仅限特定服务端程序加载，隐藏于常规插件列表中
- **风险提示**：该插件的 `UncookedOnly` 类型和 `ProgramAllowList` 限制意味着它**仅用于编辑器多用户服务端**，不适合作为运行时依赖。Beta 状态意味着升级引擎版本时 API 可能变动
- **推荐**：如果你需要使用 Unreal 的多用户编辑功能，该模块是必需的基础设施。建议通过 `IConcertServerModule::Get()` 获取接口，避免直接依赖具体实现类

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/multi-user-editing-in-unreal-engine/)（UE 多用户编辑概述）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Developer/Concert/ConcertMain/Tests)（如有）