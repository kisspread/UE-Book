# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线服务框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices) | |

## 用途

OnlineServices 是 Epic 为替代传统 OnlineSubsystem 而设计的新一代在线服务抽象框架。它定义了一套统一的接口层，用于与各种在线平台服务（EOS、Steam、PSN、Xbox Live 等）交互。

与旧版 OnlineSubsystem 的区别：
- **纯 C++ 接口**：不提供蓝图节点，所有 API 均为 C++ 接口
- **强类型异步操作**：使用 `TOnlineAsyncOpHandle<T>` 和 `TOnlineResult<T>` 替代传统的委托模式
- **结构化参数/结果**：每个操作都有独立的 `Params` 和 `Result` 结构体，类型安全
- **Schema 驱动的数据模型**：使用 Schema 系统定义属性的类型和可见性
- **工厂注册模式**：通过 `FOnlineServicesRegistry` 注册和管理不同平台的实现

本插件本身**不包含任何平台实现**，它仅定义接口。具体实现由其他插件提供（如 OnlineServicesNull、OnlineServicesEOS 等）。

## 使用场景

- 你的游戏需要支持多种在线平台（EOS/Steam/PSN/Xbox） → 用 OnlineServices 作为统一接口层
- 你需要管理玩家认证、好友系统、大厅/会话等在线功能 → 通过 `IOnlineServices` 获取对应子接口
- 你需要异步操作的进度追踪和重试机制 → 使用 `TOnlineAsyncOpHandle` 的回调链
- 你想用结构化方式处理在线错误 → 使用 `FOnlineError` 和 `TOnlineResult<T>`

## 蓝图用法

本插件不包含任何蓝图可调用的节点。所有接口均为纯 C++ 虚函数接口，设计上不暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServices.h"        // 主接口 + 获取服务实例
#include "Online/Auth.h"                  // 认证接口
#include "Online/Sessions.h"              // 会话接口
#include "Online/Lobbies.h"               // 大厅接口
#include "Online/Social.h"                // 好友系统
#include "Online/Achievements.h"          // 成就系统
#include "Online/Commerce.h"              // 商城系统
#include "Online/Presence.h"              // 在线状态
#include "Online/Stats.h"                 // 统计数据
#include "Online/Leaderboards.h"          // 排行榜
```

### 基本用法

```cpp
// 获取在线服务实例
TSharedPtr<IOnlineServices> OnlineServices = UE::Online::GetServices();
if (!OnlineServices.IsValid())
{
    UE_LOG(LogOnlineServices, Warning, TEXT("No online services available"));
    return;
}

// 获取认证接口并登录
IAuthPtr Auth = OnlineServices->GetAuthInterface();
FAuthLogin::Params LoginParams;
LoginParams.PlatformUserId = GetPlatformUserId();
LoginParams.CredentialsType = UE::Online::LoginCredentialsType::Auto;

Auth->Login(MoveTemp(LoginParams))
    .OnComplete([](const TOnlineResult<FAuthLogin>& Result)
    {
        if (Result.IsOk())
        {
            TSharedRef<FAccountInfo> AccountInfo = Result.GetOkValue().AccountInfo;
            UE_LOG(LogOnlineServices, Log, TEXT("Logged in as: %s"), *AccountInfo->AccountId.ToString());
        }
        else
        {
            UE_LOG(LogOnlineServices, Error, TEXT("Login failed: %s"), *Result.GetErrorValue().GetLogString());
        }
    });
```

### 进阶用法

```cpp
// 大厅创建 + 邀请好友的完整流程
IOnlineServicesPtr Services = UE::Online::GetServices();
ILobbiesPtr Lobbies = Services->GetLobbiesInterface();
IAuthPtr Auth = Services->GetAuthInterface();

// 创建大厅
FCreateLobby::Params CreateParams;
CreateParams.LocalAccountId = LocalAccountId;
CreateParams.LocalName = FName("GameLobby");
CreateParams.SchemaId = FName("GameLobbySchema");
CreateParams.MaxMembers = 4;
CreateParams.JoinPolicy = ELobbyJoinPolicy::PublicAdvertised;
CreateParams.Attributes.Add(FName("MapName"), FSchemaVariant(FString("BattleArena")));

Lobbies->CreateLobby(MoveTemp(CreateParams))
    .OnComplete([Lobbies, LocalAccountId](const TOnlineResult<FCreateLobby>& Result)
    {
        if (Result.IsOk())
        {
            TSharedPtr<const FLobby> Lobby = Result.GetOkValue().Lobby;
            UE_LOG(LogOnlineServices, Log, TEXT("Lobby created: %s"), *Lobby->LobbyId.ToString());
            
            // 邀请好友
            FInviteLobbyMember::Params InviteParams;
            InviteParams.LocalAccountId = LocalAccountId;
            InviteParams.LobbyId = Lobby->LobbyId;
            InviteParams.TargetAccountId = FriendAccountId;
            Lobbies->InviteLobbyMember(MoveTemp(InviteParams));
        }
    });

// 监听大厅事件
Lobbies->OnLobbyMemberJoined().Add([](const FLobbyMemberJoined& Event)
{
    UE_LOG(LogOnlineServices, Log, TEXT("Member joined: %s"), 
        *Event.Member->AccountId.ToString());
});
```

```cpp
// 使用 OnWillRetry 处理需要重试的操作
ISessionsPtr Sessions = Services->GetSessionsInterface();

FFindSessions::Params FindParams;
FindParams.LocalAccountId = LocalAccountId;
FindParams.MaxResults = 10;
FindParams.Filters.Add({
    .Key = FName("GameMode"),
    .ComparisonOp = ESchemaAttributeComparisonOp::Equals,
    .Value = FSchemaVariant(FString("Ranked"))
});

Sessions->FindSessions(MoveTemp(FindParams))
    .OnWillRetry([](TOnlineAsyncOpHandle<FFindSessions>& Handle, const FWillRetry& Retry)
    {
        UE_LOG(LogOnlineServices, Warning, 
            TEXT("Session search retrying in %.1fs (attempt %d/%d): %s"),
            Retry.RetryInSeconds, Retry.RetryAttempt, Retry.MaxRetryAttempts,
            *Retry.Reason.GetLogString());
    })
    .OnComplete([](const TOnlineResult<FFindSessions>& Result)
    {
        if (Result.IsOk())
        {
            // 处理搜索结果
        }
    });
```

## Demo 示例

### 在线服务初始化与认证

```cpp
// MyOnlineManager.h
#pragma once

#include "CoreMinimal.h"
#include "Online/OnlineServices.h"
#include "Online/Auth.h"
#include "Online/Sessions.h"
#include "Online/Social.h"

namespace UE::Online
{
class FMyOnlineManager
{
public:
    void Initialize();
    void Shutdown();
    
    void LoginUser(FPlatformUserId PlatformUserId);
    void QueryFriends();
    void CreateSession(FName SessionName);
    
    IOnlineServicesPtr GetServices() const { return OnlineServices; }

private:
    void OnLoginComplete(const TOnlineResult<FAuthLogin>& Result);
    void OnFriendsQueried(const TOnlineResult<FQueryFriends>& Result);
    void OnSessionCreated(const TOnlineResult<FCreateSession>& Result);
    
    IOnlineServicesPtr OnlineServices;
    IAuthPtr AuthInterface;
    ISocialPtr SocialInterface;
    ISessionsPtr SessionsInterface;
    FAccountId LocalAccountId;
};
}
```

```cpp
// MyOnlineManager.cpp
#include "MyOnlineManager.h"
#include "Online/OnlineServicesLog.h"
#include "Online/OnlineErrorDefinitions.h"

namespace UE::Online
{

void FMyOnlineManager::Initialize()
{
    OnlineServices = UE::Online::GetServices();
    if (!OnlineServices.IsValid())
    {
        UE_LOG(LogOnlineServices, Error, TEXT("Failed to get online services"));
        return;
    }
    
    AuthInterface = OnlineServices->GetAuthInterface();
    SocialInterface = OnlineServices->GetSocialInterface();
    SessionsInterface = OnlineServices->GetSessionsInterface();
    
    // 监听连接状态变化
    OnlineServices->GetConnectivityInterface()->OnConnectionStatusChanged().Add(
        [](const FConnectionStatusChanged& Event)
        {
            UE_LOG(LogOnlineServices, Log, TEXT("Connection status: %s -> %s"),
                LexToString(Event.PreviousStatus), LexToString(Event.CurrentStatus));
        });
}

void FMyOnlineManager::Shutdown()
{
    if (AuthInterface.IsValid() && LocalAccountId.IsValid())
    {
        FAuthLogout::Params LogoutParams;
        LogoutParams.LocalAccountId = LocalAccountId;
        AuthInterface->Logout(MoveTemp(LogoutParams));
    }
    
    OnlineServices.Reset();
    AuthInterface.Reset();
    SocialInterface.Reset();
    SessionsInterface.Reset();
}

void FMyOnlineManager::LoginUser(FPlatformUserId PlatformUserId)
{
    if (!AuthInterface.IsValid())
    {
        UE_LOG(LogOnlineServices, Error, TEXT("Auth interface not available"));
        return;
    }
    
    FAuthLogin::Params LoginParams;
    LoginParams.PlatformUserId = PlatformUserId;
    LoginParams.CredentialsType = LoginCredentialsType::Auto;
    
    AuthInterface->Login(MoveTemp(LoginParams))
        .OnComplete([this](const TOnlineResult<FAuthLogin>& Result)
        {
            OnLoginComplete(Result);
        });
}

void FMyOnlineManager::OnLoginComplete(const TOnlineResult<FAuthLogin>& Result)
{
    if (Result.IsOk())
    {
        TSharedRef<FAccountInfo> AccountInfo = Result.GetOkValue().AccountInfo;
        LocalAccountId = AccountInfo->AccountId;
        UE_LOG(LogOnlineServices, Log, TEXT("Login successful. Account: %s"),
            *LocalAccountId.ToString());
        
        // 登录成功后查询好友列表
        QueryFriends();
    }
    else
    {
        FOnlineError Error = Result.GetErrorValue();
        UE_LOG(LogOnlineServices, Error, TEXT("Login failed: %s"), *Error.GetLogString());
        
        // 检查是否需要创建账号或关联账号
        if (Error == Errors::InvalidUser())
        {
            UE_LOG(LogOnlineServices, Warning, 
                TEXT("User not found, may need to create or link account"));
        }
    }
}

void FMyOnlineManager::QueryFriends()
{
    if (!SocialInterface.IsValid() || !LocalAccountId.IsValid())
    {
        return;
    }
    
    FQueryFriends::Params QueryParams;
    QueryParams.LocalAccountId = LocalAccountId;
    
    SocialInterface->QueryFriends(MoveTemp(QueryParams))
        .OnComplete([this](const TOnlineResult<FQueryFriends>& Result)
        {
            OnFriendsQueried(Result);
        });
}

void FMyOnlineManager::OnFriendsQueried(const TOnlineResult<FQueryFriends>& Result)
{
    if (Result.IsOk())
    {
        FGetFriends::Params GetParams;
        GetParams.LocalAccountId = LocalAccountId;
        
        TOnlineResult<FGetFriends> FriendsResult = SocialInterface->GetFriends(MoveTemp(GetParams));
        if (FriendsResult.IsOk())
        {
            const TArray<TSharedRef<FFriend>>& Friends = FriendsResult.GetOkValue().Friends;
            UE_LOG(LogOnlineServices, Log, TEXT("Found %d friends"), Friends.Num());
            
            for (const TSharedRef<FFriend>& Friend : Friends)
            {
                UE_LOG(LogOnlineServices, Log, TEXT("  - %s (%s)"),
                    *Friend->DisplayName, LexToString(Friend->Relationship));
            }
        }
    }
}

void FMyOnlineManager::CreateSession(FName SessionName)
{
    if (!SessionsInterface.IsValid() || !LocalAccountId.IsValid())
    {
        return;
    }
    
    FCreateSession::Params CreateParams;
    CreateParams.LocalAccountId = LocalAccountId;
    CreateParams.LocalName = SessionName;
    CreateParams.SchemaId = FName("DefaultSessionSchema");
    
    // 配置会话设置
    CreateParams.SessionSettings.NumMaxConnections = 8;
    CreateParams.SessionSettings.JoinPolicy = ESessionJoinPolicy::FriendsOnly;
    CreateParams.SessionSettings.CustomSettings.Add(FName("MapName"), 
        { .Data = FSchemaVariant(FString("Arena")), .Visibility = ESchemaAttributeVisibility::Public });
    
    SessionsInterface->CreateSession(MoveTemp(CreateParams))
        .OnComplete([this](const TOnlineResult<FCreateSession>& Result)
        {
            OnSessionCreated(Result);
        });
}

void FMyOnlineManager::OnSessionCreated(const TOnlineResult<FCreateSession>& Result)
{
    if (Result.IsOk())
    {
        UE_LOG(LogOnlineServices, Log, TEXT("Session created successfully"));
        
        // 监听会话事件
        SessionsInterface->OnSessionUpdated().Add(
            [](const FSessionUpdated& Event)
            {
                UE_LOG(LogOnlineServices, Log, TEXT("Session updated"));
            });
        
        SessionsInterface->OnSessionMemberJoined().Add(
            [](const FSessionMemberJoined& Event)
            {
                UE_LOG(LogOnlineServices, Log, TEXT("Player joined session"));
            });
    }
    else
    {
        UE_LOG(LogOnlineServices, Error, TEXT("Failed to create session: %s"),
            *Result.GetErrorValue().GetLogString());
    }
}

}
```

## 模块依赖

本插件依赖 `OnlineBase` 插件（已在 .uplugin 中声明）。

使用本插件时，你的模块通常需要依赖：

| 模块 | 用途 |
|---|---|
| `OnlineServicesInterface` | 主接口定义，包含所有在线服务接口 |
| `OnlineServicesCommon` | 通用实现基类 |
| `OnlineBase` | 基础在线服务类型定义（FAccountId、FOnlineSessionId 等） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下的 double 截断警告 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS | 防御 EOS 返回无效端口值的边界情况 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式化字符串不匹配问题 |
| 2026-04-14 | `2c013d6c` | Online Services EOS Presence Refactor | EOS 在线状态功能重构 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF | 迁移日志宏到 UE_LOGF 格式 |

### 维护评价

**活跃维护**。该插件自 2022 年从 Experimental 迁移后持续受到 Epic 的积极维护。最近的更新集中在：
- 编译警告修复和代码质量改进
- EOS 实现的具体 bug 修复
- Presence 模块的重构

作为 UE5 在线服务的下一代架构，OnlineServices 是 Epic 的重点维护对象。它正在逐步替代传统的 OnlineSubsystem，推荐新项目使用。

**注意**：本插件默认未启用（`EnabledByDefault: false`），需要在项目设置中手动启用或在代码中显式引用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices)
- [OnlineBase 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineBase)（依赖项）