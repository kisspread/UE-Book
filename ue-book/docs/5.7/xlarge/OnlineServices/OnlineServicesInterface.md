# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-06-24 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices) | |

## 用途

OnlineServices 是 UE5 新一代在线服务抽象层（OSSv2），用于替代旧版 OnlineSubsystem 系统。它定义了一套**平台无关的接口**，涵盖认证、社交、会话、排行榜、成就、商城等全部在线功能，让游戏代码只需对接一套统一 API，即可在 Epic、Steam、PSN、Xbox Live、Nintendo 等任意后端之间无缝切换。

与旧版 OnlineSubsystem 相比，OnlineServices 的核心改进包括：

- **统一的异步操作模型**：所有异步操作返回 `TOnlineAsyncOpHandle<OpType>`，携带类型安全的 Params/Result 结构体，告别旧版模糊的 `FOnlineSessionSearch` 等类型
- **结构化错误系统**：`FOnlineError` + 错误码体系（含分类、系统、错误值三级编码），支持错误链和平台特定错误映射
- **Schema 系统**：为 Lobbies/Sessions 等提供可版本化的属性定义，支持跨版本兼容和搜索过滤
- **工厂注册模式**：通过 `FOnlineServicesRegistry` 注册平台实现，支持优先级覆盖和多实例管理

此插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动启用，或由具体的平台实现插件（如 OnlineServicesNull、OnlineServicesEOS 等）依赖启用。

## 模块概览

| 模块 | 职责 |
|---|---|
| **OnlineServicesInterface** | 定义所有在线服务接口（IAuth、ISessions、ILobbies 等）、错误码、异步操作句柄、Schema 系统等核心类型 |
| **OnlineServicesCommon** | 提供接口的通用基础实现和工具类 |
| **OnlineServicesCommonEngineUtils** | 将在线服务与 UE 引擎子系统（如 World、GameInstance）集成的工具 |

## 使用场景

- 你需要一个**平台无关的多人游戏后端** → 用 OnlineServices 的 ISessions/ILobbies
- 你需要**跨平台好友系统和在线状态** → 用 ISocial/IPresence
- 你需要**游戏内商城和 DLC 管理** → 用 ICommerce
- 你需要**排行榜和成就系统** → 用 ILeaderboards/IAchievements
- 你需要**云端存档（用户文件）** → 用 IUserFile/ITitleFile
- 你正在从旧版 OnlineSubsystem 迁移 → 这就是目标替代方案

## 接口总览

OnlineServices 通过 `IOnlineServices` 主接口暴露以下子接口：

| 子接口 | 头文件 | 功能 |
|---|---|---|
| `IAuth` | `Online/Auth.h` | 登录/登出、凭证管理、账号链接、远程认证票据 |
| `ISessions` | `Online/Sessions.h` | 会话创建/查找/加入/管理，自定义设置，Schema 属性 |
| `ILobbies` | `Online/Lobbies.h` | 大厅创建/查找/加入，成员管理，实时属性同步 |
| `ISocial` | `Online/Social.h` | 好友查询、邀请、屏蔽、关系管理 |
| `IPresence` | `Online/Presence.h` | 在线状态查询/更新、可加入性、自定义状态属性 |
| `IAchievements` | `Online/Achievements.h` | 成就定义查询、解锁、进度跟踪 |
| `ILeaderboards` | `Online/Leaderboards.h` | 排行榜条目查询（按用户/排名/周围） |
| `IStats` | `Online/Stats.h` | 统计数据查询/更新、事件触发 |
| `ICommerce` | `Online/Commerce.h` | 商品查询、购买、权益管理 |
| `IUserInfo` | `Online/UserInfo.h` | 用户信息/头像查询 |
| `IExternalUI` | `Online/ExternalUI.h` | 平台原生 UI（登录、好友列表） |
| `IConnectivity` | `Online/Connectivity.h` | 网络连接状态监控 |
| `IPrivileges` | `Online/Privileges.h` | 用户权限检查（在线游戏、语音、跨平台等） |
| `ITitleFile` | `Online/TitleFile.h` | 标题文件（只读，服务端配置等） |
| `IUserFile` | `Online/UserFile.h` | 用户文件（读写，云存档等） |

## 核心架构

### 异步操作模式

所有异步操作遵循统一模式：

```
操作定义 (struct FOpName)
├── Params   — 输入参数
├── Result   — 输出结果
└── Name     — 操作名称标识符

调用方式:
TOnlineAsyncOpHandle<FOpName> Handle = Interface->OpName(Params);
Handle.OnComplete([](TOnlineResult<FOpName> Result) { ... });
```

### 错误系统

错误码采用 64 位三级编码：

```
[4 bits System][28 bits Category][32 bits Code]
```

- **System**: Engine(1)、Game(2)、ThirdPartyPlugin(3)
- **Category**: Common(0x1)、Windows(0x2)、Presence(0x3)、Auth(0x4)、Achievements(0x5) 等
- **Code**: 具体错误值

### Schema 系统

为 Lobbies/Sessions 提供可版本化的属性定义：

- `FSchemaId` — Schema 名称标识
- `FSchemaCategoryId` — Schema 内分类（如 Lobby vs LobbyMember）
- `FSchemaAttributeId` — 属性标识
- 支持搜索过滤（`ESchemaAttributeComparisonOp`）
- 支持可见性控制（Public/Private）

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServices.h"
#include "Online/OnlineServicesRegistry.h"
#include "Online/Auth.h"
#include "Online/Sessions.h"
#include "Online/Lobbies.h"
```

### 获取在线服务实例

```cpp
// 来源: OnlineServicesRegistry.h
#include "Online/OnlineServicesRegistry.h"

// 获取注册表单例
UE::Online::FOnlineServicesRegistry& Registry = UE::Online::FOnlineServicesRegistry::Get();

// 获取指定平台的在线服务实例
// EOnlinePlatformType: Epic, Steam, PSN, Nintendo, XBL, Unknown
TSharedPtr<UE::Online::IOnlineServices> Services = Registry.GetNamedServicesInstance(
    UE::Online::EOnlinePlatformType::Epic,
    FName("DefaultInstance"),
    FName("DefaultConfig")
);

// 初始化
Services->Init();
```

### 认证（Auth）

```cpp
// 来源: Online/Auth.h
#include "Online/Auth.h"

using namespace UE::Online;

// 获取 Auth 接口
TSharedPtr<IAuth> Auth = Services->GetAuthInterface();

// 构造登录参数
FAuthLogin::Params LoginParams;
LoginParams.PlatformUserId = GetPlatformUserId();
LoginParams.LoginCredentialsType = LoginCredentialsType::Auto;

// 发起登录
TOnlineAsyncOpHandle<FAuthLogin> LoginHandle = Auth->Login(MoveTemp(LoginParams));

LoginHandle.OnComplete([](TOnlineResult<FAuthLogin> Result)
{
    if (Result.IsOk())
    {
        FAuthLogin::Result& LoginResult = Result.GetOkValue();
        FAccountId AccountId = LoginResult.AccountInfo->AccountId;
        UE_LOG(LogOnlineServices, Log, TEXT("Login successful: %s"), *ToLogString(AccountId));
    }
    else
    {
        FOnlineError& Error = Result.GetErrorValue();
        UE_LOG(LogOnlineServices, Error, TEXT("Login failed: %s"), *Error.GetLogString());
    }
});
```

### 会话管理（Sessions）

```cpp
// 来源: Online/Sessions.h
#include "Online/Sessions.h"

using namespace UE::Online;

TSharedPtr<ISessions> Sessions = Services->GetSessionsInterface();

// 创建会话
FCreateSession::Params CreateParams;
CreateParams.LocalAccountId = LocalAccountId;
CreateParams.LocalName = FName("MyGameSession");
CreateParams.SchemaId = FName("GameSessionSchema");
CreateParams.NumMaxConnections = 8;
CreateParams.JoinPolicy = ESessionJoinPolicy::Public;

// 添加自定义设置
FCustomSessionSetting Setting;
Setting.Data = FSchemaVariant(FString(TEXT("MyMap")));
Setting.Visibility = ESchemaAttributeVisibility::Public;
CreateParams.CustomSettings.Add(FName("MapName"), Setting);

TOnlineAsyncOpHandle<FCreateSession> CreateHandle = Sessions->CreateSession(MoveTemp(CreateParams));

CreateHandle.OnComplete([](TOnlineResult<FCreateSession> Result)
{
    if (Result.IsOk())
    {
        TSharedRef<const FSession> Session = Result.GetOkValue().Session;
        UE_LOG(LogOnlineServices, Log, TEXT("Session created: %s"), *Session->LocalName.ToString());
    }
});

// 查找会话
FFindSessions::Params FindParams;
FindParams.LocalAccountId = LocalAccountId;

// 添加搜索过滤
FFindSessionsSearchFilter Filter;
Filter.Key = FName("MapName");
Filter.ComparisonOp = ESchemaAttributeComparisonOp::Equals;
Filter.Value = FSchemaVariant(FString(TEXT("MyMap")));
FindParams.Filters.Add(Filter);

TOnlineAsyncOpHandle<FFindSessions> FindHandle = Sessions->FindSessions(MoveTemp(FindParams));

FindHandle.OnComplete([](TOnlineResult<FFindSessions> Result)
{
    if (Result.IsOk())
    {
        const TArray<TSharedRef<const FSession>>& FoundSessions = Result.GetOkValue().Sessions;
        UE_LOG(LogOnlineServices, Log, TEXT("Found %d sessions"), FoundSessions.Num());
    }
});
```

### 大厅管理（Lobbies）

```cpp
// 来源: Online/Lobbies.h
#include "Online/Lobbies.h"

using namespace UE::Online;

TSharedPtr<ILobbies> Lobbies = Services->GetLobbiesInterface();

// 创建大厅
FCreateLobby::Params LobbyParams;
LobbyParams.LocalAccountId = LocalAccountId;
LobbyParams.LocalName = FName("MyLobby");
LobbyParams.SchemaId = FName("LobbySchema");
LobbyParams.MaxMembers = 4;
LobbyParams.JoinPolicy = ELobbyJoinPolicy::PublicAdvertised;

// 设置大厅属性
LobbyParams.Attributes.Add(FName("GameMode"), FSchemaVariant(FString(TEXT("Deathmatch"))));

TOnlineAsyncOpHandle<FCreateLobby> LobbyHandle = Lobbies->CreateLobby(MoveTemp(LobbyParams));

LobbyHandle.OnComplete([](TOnlineResult<FCreateLobby> Result)
{
    if (Result.IsOk())
    {
        TSharedRef<const FLobby> Lobby = Result.GetOkValue().Lobby;
        UE_LOG(LogOnlineServices, Log, TEXT("Lobby created: %s"), *Lobby->LobbyId.ToString());
    }
});

// 查找大厅
FFindLobby::Params FindLobbyParams;
FindLobbyParams.LocalAccountId = LocalAccountId;

FFindLobbySearchFilter LobbyFilter;
LobbyFilter.AttributeName = FName("GameMode");
LobbyFilter.ComparisonOp = ESchemaAttributeComparisonOp::Equals;
LobbyFilter.ComparisonValue = FSchemaVariant(FString(TEXT("Deathmatch")));
FindLobbyParams.Filters.Add(LobbyFilter);

TOnlineAsyncOpHandle<FFindLobby> FindLobbyHandle = Lobbies->FindLobby(MoveTemp(FindLobbyParams));
```

### 好友与在线状态（Social & Presence）

```cpp
// 来源: Online/Social.h, Online/Presence.h
#include "Online/Social.h"
#include "Online/Presence.h"

using namespace UE::Online;

// 查询好友列表
TSharedPtr<ISocial> Social = Services->GetSocialInterface();

FSocialQueryFriends::Params FriendsParams;
FriendsParams.LocalAccountId = LocalAccountId;

Social->QueryFriends(MoveTemp(FriendsParams)).OnComplete(
    [Social, LocalAccountId](TOnlineResult<FSocialQueryFriends> Result)
{
    if (Result.IsOk())
    {
        FSocialGetFriends::Params GetParams;
        GetParams.LocalAccountId = LocalAccountId;
        TOnlineResult<FSocialGetFriends> FriendsResult = Social->GetFriends(MoveTemp(GetParams));
        
        if (FriendsResult.IsOk())
        {
            for (const TSharedRef<FFriend>& Friend : FriendsResult.GetOkValue().Friends)
            {
                UE_LOG(LogOnlineServices, Log, TEXT("Friend: %s (%s)"),
                    *Friend->DisplayName,
                    LexToString(Friend->Relationship));
            }
        }
    }
});

// 查询在线状态
TSharedPtr<IPresence> Presence = Services->GetPresenceInterface();

FPresenceQuery::Params PresenceParams;
PresenceParams.LocalAccountId = LocalAccountId;
PresenceParams.AccountIds.Add(FriendAccountId);

Presence->QueryPresence(MoveTemp(PresenceParams)).OnComplete(
    [Presence, LocalAccountId](TOnlineResult<FPresenceQuery> Result)
{
    if (Result.IsOk())
    {
        FPresenceGet::Params GetPresenceParams;
        GetPresenceParams.LocalAccountId = LocalAccountId;
        GetPresenceParams.AccountId = FriendAccountId;
        
        TOnlineResult<FPresenceGet> PresenceResult = Presence->GetPresence(MoveTemp(GetPresenceParams));
        if (PresenceResult.IsOk())
        {
            TSharedRef<FUserPresence> UserPresence = PresenceResult.GetOkValue().Presence;
            UE_LOG(LogOnlineServices, Log, TEXT("Status: %s"), LexToString(UserPresence->Status));
        }
    }
});
```

### 连接状态监控

```cpp
// 来源: Online/Connectivity.h
#include "Online/Connectivity.h"

using namespace UE::Online;

TSharedPtr<IConnectivity> Connectivity = Services->GetConnectivityInterface();

// 同步查询连接状态
FConnectivityGetConnectionStatus::Params ConnParams;
TOnlineResult<FConnectivityGetConnectionStatus> ConnResult = Connectivity->GetConnectionStatus(MoveTemp(ConnParams));

if (ConnResult.IsOk())
{
    EOnlineServicesConnectionStatus Status = ConnResult.GetOkValue().Status;
    UE_LOG(LogOnlineServices, Log, TEXT("Connection: %s"), LexToString(Status));
}

// 监听连接状态变化
Connectivity->OnConnectionStatusChanged().Add([](const FConnectionStatusChanged& Event)
{
    UE_LOG(LogOnlineServices, Log, TEXT("Connection changed: %s -> %s (Service: %s)"),
        LexToString(Event.PreviousStatus),
        LexToString(Event.CurrentStatus),
        *Event.ServiceName);
});
```

### 全局委托监听

```cpp
// 来源: Online/OnlineServicesDelegates.h
#include "Online/OnlineServicesDelegates.h"

using namespace UE::Online;

// 监听新在线服务实例创建
OnOnlineServicesCreated.Add([](TSharedRef<IOnlineServices> NewServices)
{
    UE_LOG(LogOnlineServices, Log, TEXT("New online services instance created"));
});

// 监听所有异步操作完成（可用于性能监控/调试）
OnAsyncOpCompleted.Add([](const FOnAsyncOpCompletedParams& Params)
{
    UE_LOG(LogOnlineServices, Verbose, TEXT("Op '%s' on '%s' completed in %.3fs: %s"),
        *Params.OpName,
        *Params.InterfaceName,
        Params.DurationInSeconds,
        Params.OnlineError.IsSet() ? *Params.OnlineError->GetLogString() : TEXT("Success"));
});
```

## Demo 示例

### 最小在线服务使用示例

**MyOnlineGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "Online/OnlineServices.h"
#include "Online/Auth.h"
#include "MyOnlineGameMode.generated.h"

UCLASS()
class AMyOnlineGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

private:
    void OnLoginComplete(UE::Online::TOnlineResult<UE::Online::FAuthLogin> Result);
    
    TSharedPtr<UE::Online::IOnlineServices> OnlineServices;
};
```

**MyOnlineGameMode.cpp**
```cpp
#include "MyOnlineGameMode.h"
#include "Online/OnlineServicesRegistry.h"
#include "Online/OnlineServicesDelegates.h"

using namespace UE::Online;

void AMyOnlineGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 获取在线服务实例
    FOnlineServicesRegistry& Registry = FOnlineServicesRegistry::Get();
    OnlineServices = Registry.GetNamedServicesInstance(
        EOnlinePlatformType::Epic,
        FName("DefaultInstance")
    );

    if (!OnlineServices)
    {
        UE_LOG(LogTemp, Error, TEXT("No online services available"));
        return;
    }

    OnlineServices->Init();

    // 自动登录
    TSharedPtr<IAuth> Auth = OnlineServices->GetAuthInterface();
    if (Auth)
    {
        FAuthLogin::Params LoginParams;
        LoginParams.LoginCredentialsType = LoginCredentialsType::Auto;

        Auth->Login(MoveTemp(LoginParams)).OnComplete(
            [this](TOnlineResult<FAuthLogin> Result)
            {
                OnLoginComplete(MoveTemp(Result));
            });
    }
}

void AMyOnlineGameMode::OnLoginComplete(TOnlineResult<FAuthLogin> Result)
{
    if (Result.IsOk())
    {
        FAccountId AccountId = Result.GetOkValue().AccountInfo->AccountId;
        UE_LOG(LogTemp, Log, TEXT("Logged in as: %s"), *ToLogString(AccountId));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Login failed: %s"), *Result.GetErrorValue().GetLogString());
    }
}
```

**MyProject.Build.cs** 依赖：
```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "OnlineServicesInterface",
    "OnlineServicesCommon",
    "OnlineBase"
});
```

## 模块依赖

从源码头文件分析，此插件依赖 OnlineBase 插件提供基础类型（`FAccountId`、`FLobbyId`、`FOnlineSessionId`、`FOnlineError` 等）。

| 模块 | 用途 |
|---|---|
| `OnlineBase` | 提供核心在线类型定义（AccountId、SessionId 等）和基础错误处理 |
| `OnlineServicesInterface` | 接口定义层，使用其他模块时需依赖此模块 |
| `OnlineServicesCommon` | 通用实现层，平台实现插件通常依赖此模块 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 近期 | `56ebc05` | 为 PSN 平台添加 Sessions 接口方法 |
| 近期 | `8ddbe09` | Session 接口：添加 GetSessionName 辅助方法，修复 meta struct 拼写错误，为移除会话成员操作添加 TargetAccountId 参数 |
| 近期 | `b0ce0f7` | 将 Fortnite 中的 Online Services Presence 使用支持扩展到引擎插件 |

### 维护评价

**活跃维护** ✅

- 创建于 2021 年，是 UE5 的新一代在线服务框架（OSSv2）
- 近期有持续的功能性更新（PSN 支持、接口扩展、Fortnite 实战验证）
- 由 Epic Games 核心团队维护，是官方推荐的在线服务方案
- 正在从 Fortnite 等大型项目中逐步回流改进
- 默认不启用（`EnabledByDefault: false`），说明仍在逐步推广阶段
- 旧版 OnlineSubsystem 仍然可用，但 OnlineServices 是未来方向

**推荐使用**：如果你的新项目需要在线服务，优先考虑此系统而非旧版 OnlineSubsystem。但需注意部分平台实现可能尚未完全覆盖所有接口。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
- [OnlineBase 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineBase)（依赖的基础类型插件）