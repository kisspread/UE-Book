# Online Services EOS (Game Services)

> Online Services implementation for EOS Game services only.

| 属性 | 值 |
|---|---|
| 中文名 | EOS 游戏服务 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesEOSGS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOSGS) | |

## 用途

本插件是 UE5 新一代 Online Services 框架针对 **Epic Online Services (EOS) 游戏服务**的后端实现。它解决了"如何在 UE5 中使用 EOS 提供的全套在线功能"这一核心问题。

与旧版 `OnlineSubsystemEOS` 不同，本插件基于 UE::Online 命名空间下的新式接口体系，仅使用 EOS 的 **Game Services**（游戏服务）部分——即通过 Connect 登录、Sessions、Lobbies 等服务，而不直接依赖 Epic Account Services (EAS) 的完整流程。它继承自 `FOnlineServicesEpicCommon`，是 Epic 平台在线服务的 EOS 游戏端实现。

**存在的意义**：对于只需要 EOS 游戏侧功能（如基于 ProductUserId 的会话匹配、大厅、排行榜等）而不需要完整 Epic 账户体系的项目，此插件提供了轻量级的接入方式。

## 使用场景

- 你正在开发一款 PC/主机多人游戏，需要通过 EOS 匹配系统创建和搜索会话 → 用本插件管理 Sessions
- 你需要实现游戏大厅功能（创建、加入、邀请、踢出、转让房主）→ 用 Lobbies 接口
- 你想使用 EOS 的成就、统计、排行榜系统 → 用 Achievements/Stats/Leaderboards 接口
- 你需要云端玩家数据存储（存档、配置文件）→ 用 UserFile 接口
- 你需要标题级配置文件下载 → 用 TitleFile 接口
- 你需要举报和处罚系统 → 用 PlayerReports/PlayerSanctions 接口
- 你已有 Epic Account Services 认证，想在 EOS Connect 层面建立游戏会话身份 → 用 Auth 接口的双阶段登录

## 蓝图用法

本插件是纯 C++ 运行时模块，**不包含蓝图可调用节点**。所有在线服务接口通过 UE::Online 框架的 C++ 异步操作句柄（`TOnlineAsyncOpHandle`）访问。使用蓝图时需通过游戏层 C++ 代码封装后暴露给蓝图。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesEOSGS.h"
#include "Online/AuthEOSGS.h"
#include "Online/SessionsEOSGS.h"
#include "Online/LobbiesEOSGS.h"
#include "Online/AchievementsEOSGS.h"
#include "Online/StatsEOSGS.h"
#include "Online/LeaderboardsEOSGS.h"
```

### 基本用法

**获取 Online Services 实例并登录**

通过 UE::Online 框架获取 EOSGS 服务实例，然后执行认证登录。认证流程分为两步：先通过 EAS 登录获取 EpicAccountId，再通过 Connect 登录获取 ProductUserId。

```cpp
#include "Online/OnlineServicesEOSGS.h"
#include "Online/AuthEOSGS.h"

using namespace UE::Online;

// 获取 Epic Online Services 实例
FOnlineServicesEOSGS* EOSGSServices = static_cast<FOnlineServicesEOSGS*>(
    Online::GetServices(EOnlineServices::Epic).Get());

if (EOSGSServices)
{
    // 获取认证接口
    IAuth* Auth = EOSGSServices->GetAuth();
    
    // 构造登录参数
    FAuthLogin::Params LoginParams;
    LoginParams.PlatformUserId = PlatformUserId;
    LoginParams.CredentialsType = FCommonCredentialsTypes::ExchangeCode;
    LoginParams.CredentialsId = TEXT("your-exchange-code");
    LoginParams.CredentialsToken = TVariant<FString, FExternalAuthToken>();
    // 设置 token 值...
    
    // 异步执行登录
    TOnlineAsyncOpHandle<FAuthLogin> LoginHandle = Auth->Login(MoveTemp(LoginParams));
    LoginHandle.OnComplete([](const TOnlineResult<FAuthLogin>& Result)
    {
        if (Result.IsOk())
        {
            FAccountId AccountId = Result.GetOk().AccountId;
            // 登录成功，获取到 AccountId
        }
        else
        {
            // 登录失败处理
            UE_LOG(LogOnline, Error, TEXT("Login failed: %s"), 
                *Result.GetErrorValue().GetLogString());
        }
    });
}
```

### 进阶用法

**创建和搜索会话（Sessions）**

```cpp
#include "Online/SessionsEOSGS.h"

// 创建会话
void CreateGameSession(IAuth* Auth, FAccountId LocalAccountId)
{
    ISessions* Sessions = GetOnlineServices()->GetSessions();
    
    FCreateSession::Params CreateParams;
    CreateParams.LocalAccountId = LocalAccountId;
    CreateParams.SessionName = FName(TEXT("GameSession"));
    CreateParams.bPresenceEnabled = true;
    CreateParams.JoinPolicy = ESessionJoinPolicy::PublicAdvertised;
    CreateParams.MaxPlayers = 4;
    
    // 添加自定义属性
    CreateParams.Attributes.Emplace(FName(TEXT("MapName")), 
        FSchemaVariant(FString(TEXT("BattleArena"))));
    
    TOnlineAsyncOpHandle<FCreateSession> Handle = 
        Sessions->CreateSession(MoveTemp(CreateParams));
    
    Handle.OnComplete([](const TOnlineResult<FCreateSession>& Result)
    {
        if (Result.IsOk())
        {
            FOnlineSessionId SessionId = Result.GetOk().Session->GetSessionId();
            // 会话创建成功
        }
    });
}

// 搜索会话
void FindGameSessions(FAccountId LocalAccountId)
{
    ISessions* Sessions = GetOnlineServices()->GetSessions();
    
    FFindSessions::Params FindParams;
    FindParams.LocalAccountId = LocalAccountId;
    
    // 设置搜索过滤器
    FFindSessionsSearchFilter Filter;
    Filter.ComparisonOp = ESchemaAttributeComparisonOp::Equals;
    Filter.Key = FName(TEXT("MapName"));
    Filter.Value = FSchemaVariant(FString(TEXT("BattleArena")));
    FindParams.Filters.Add(MoveTemp(Filter));
    
    TOnlineAsyncOpHandle<FFindSessions> Handle = 
        Sessions->FindSessions(MoveTemp(FindParams));
    
    Handle.OnComplete([](const TOnlineResult<FFindSessions>& Result)
    {
        if (Result.IsOk())
        {
            for (const TSharedRef<ISession>& FoundSession : Result.GetOk().Sessions)
            {
                // 处理搜索结果
                FOnlineSessionId SessionId = FoundSession->GetSessionId();
                int32 CurrentPlayers = FoundSession->GetSessionMembers().Num();
            }
        }
    });
}
```

**大厅（Lobbies）管理**

```cpp
#include "Online/LobbiesEOSGS.h"

// 创建大厅
void CreateLobby(FAccountId LocalAccountId)
{
    ILobbies* Lobbies = GetOnlineServices()->GetLobbies();
    
    FCreateLobby::Params CreateParams;
    CreateParams.LocalAccountId = LocalAccountId;
    CreateParams.MaxMembers = 10;
    CreateParams.JoinPolicy = ELobbyJoinPolicy::PublicAdvertised;
    
    // 设置大厅属性
    CreateParams.Attributes.Emplace(FName(TEXT("GameMode")), 
        FSchemaVariant(FString(TEXT("TeamDeathmatch"))));
    
    TOnlineAsyncOpHandle<FCreateLobby> Handle = 
        Lobbies->CreateLobby(MoveTemp(CreateParams));
    
    Handle.OnComplete([Lobbies](const TOnlineResult<FCreateLobby>& Result)
    {
        if (Result.IsOk())
        {
            FLobbyId LobbyId = Result.GetOk().LobbyId;
            // 大厅创建成功，可以邀请成员
        }
    });
}

// 搜索大厅
void FindLobbies(FAccountId LocalAccountId)
{
    ILobbies* Lobbies = GetOnlineServices()->GetLobbies();
    
    FFindLobbies::Params FindParams;
    FindParams.LocalAccountId = LocalAccountId;
    
    TOnlineAsyncOpHandle<FFindLobbies> Handle = 
        Lobbies->FindLobbies(MoveTemp(FindParams));
    
    Handle.OnComplete([](const TOnlineResult<FFindLobbies>& Result)
    {
        if (Result.IsOk())
        {
            for (const TSharedRef<FLobby>& Lobby : Result.GetOk().Lobbies)
            {
                // 遍历搜索到的大厅
            }
        }
    });
}
```

**玩家举报与制裁**

```cpp
#include "Online/PlayerReportsEOSGS.h"
#include "Online/PlayerSanctionsEOSGS.h"

// 获取 PlayerReports 接口（注意：通过 FOnlineServicesEOSGS 专有方法获取）
FOnlineServicesEOSGS* EOSGSServices = static_cast<FOnlineServicesEOSGS*>(
    Online::GetServices(EOnlineServices::Epic).Get());

// 发送玩家举报
IPlayerReportsPtr Reports = EOSGSServices->GetPlayerReportsInterface();
FSendPlayerReport::Params ReportParams;
ReportParams.LocalAccountId = LocalAccountId;
ReportParams.TargetAccountId = OffenderAccountId;
ReportParams.Category = EPlayerReportCategory::Cheating;
ReportParams.Message = TEXT("使用外挂加速");

Reports->SendPlayerReport(MoveTemp(ReportParams)).OnComplete(
    [](const TOnlineResult<FSendPlayerReport>& Result)
    {
        // 举报发送完成
    });

// 查询活跃制裁
IPlayerSanctionsPtr Sanctions = EOSGSServices->GetPlayerSanctionsInterface();
FReadActivePlayerSanctions::Params SanctionParams;
SanctionParams.LocalAccountId = LocalAccountId;
SanctionParams.TargetAccountId = TargetAccountId;

Sanctions->ReadEntriesForUser(MoveTemp(SanctionParams)).OnComplete(
    [](const TOnlineResult<FReadActivePlayerSanctions>& Result)
    {
        if (Result.IsOk())
        {
            for (const FActivePlayerSanctionEntry& Entry : Result.GetOk().Entries)
            {
                // 处理制裁记录: Entry.Action, Entry.TimeExpires, Entry.ReferenceId
            }
        }
    });
```

## Demo 示例

以下是一个最小可编译示例，展示如何初始化 EOSGS 服务并执行登录。

```cpp
// MyOnlineManager.h
#pragma once

#include "CoreMinimal.h"
#include "Online/OnlineServicesEOSGS.h"

class FMyOnlineManager
{
public:
    void Initialize();
    void Login(FPlatformUserId PlatformUserId);

private:
    UE::Online::FOnlineServicesEOSGS* OnlineServices = nullptr;
};
```

```cpp
// MyOnlineManager.cpp
#include "MyOnlineManager.h"
#include "Online/OnlineServicesEOSGS.h"
#include "Online/AuthEOSGS.h"

using namespace UE::Online;

void FMyOnlineManager::Initialize()
{
    // 获取 EOSGS 在线服务实例
    TOnlineServicesPtr Services = Online::GetServices(EOnlineServices::Epic);
    OnlineServices = static_cast<FOnlineServicesEOSGS*>(Services.Get());
    
    if (OnlineServices)
    {
        UE_LOG(LogTemp, Log, TEXT("EOSGS Online Services initialized"));
    }
}

void FMyOnlineManager::Login(FPlatformUserId PlatformUserId)
{
    if (!OnlineServices) return;
    
    IAuth* Auth = OnlineServices->GetAuth();
    
    FAuthLogin::Params Params;
    Params.PlatformUserId = PlatformUserId;
    Params.CredentialsType = FCommonCredentialsTypes::ExchangeCode;
    // ExchangeCode 通常由启动器注入到命令行
    
    Auth->Login(MoveTemp(Params)).OnComplete(
        [](const TOnlineResult<FAuthLogin>& Result)
        {
            if (Result.IsOk())
            {
                UE_LOG(LogTemp, Log, TEXT("Login succeeded, AccountId: %s"),
                    *Result.GetOk().AccountId.ToString());
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Login failed: %s"),
                    *Result.GetErrorValue().GetLogString());
            }
        });
}
```

## 模块依赖

从 Build.cs 分析，本插件唯一列出的显式依赖为 `ApplicationCore`。实际运行时还隐式依赖 EOS SDK 和 Epic 公共在线服务模块。

| 模块 | 用途 |
|---|---|
| `OnlineServicesEpicCommon` | Epic 平台在线服务公共基类，本插件继承自该模块 |
| `EOSSDK` | Epic Online Services SDK，提供底层 API（Auth/Connect/Sessions/Lobbies 等） |
| `OnlineServicesUtils` | 在线服务通用工具函数 |
| `ApplicationCore` | 平台应用核心（Build.cs 显式声明） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2fc71253` | OnlineSubsystemEOS/OnlineServicesEOSGS: trigger OnExternalUIChange on bIsExclusiveInput, dedup uncha | 修复 ExternalUI 在独占输入模式下触发变更事件，并去重通知 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移至 UE_LOGF 宏 |
| 2026-03-02 | `33662059` | Add brackets to EOS P2P connection string in OnlineServicesEOSGS | 修复 EOS P2P 连接字符串格式，添加方括号 |
| 2026-02-09 | `52a2dc16` | Support EOS_P2P not being present in per-project SDK | 支持项目 SDK 中不包含 EOS_P2P 模块的场景 |
| 2026-02-05 | `ed292d1f` | Clear session cache when EOS_Sessions_DestroySession returns EOS_NotFound in FSessionsEOSGS::LeaveSe | LeaveSession 时若 DestroySession 返回 NotFound 则清除本地缓存 |

### 维护评价

- **活跃维护**：最近 3 个月内有多次功能性更新和 bug 修复，维护频率稳定
- **创建于 2022 年**：从 Experimental 迁移至正式版本，已有约 4 年历史，属于成熟的在线服务插件
- **平台支持**：限定为 Win64、Mac、Linux 平台（`.uplugin` PlatformAllowList）
- **需手动启用**：`EnabledByDefault=false`，使用前需在项目设置中手动启用
- **推荐使用**：对于需要 EOS 完整在线功能的项目，推荐使用本插件替代旧版 `OnlineSubsystemEOS`；它基于 UE5 新式 Online Services 框架，API 更现代且与引擎其他部分集成更紧密
- **注意事项**：本插件仅提供 EOS Game Services 部分，如需完整 Epic Account Services 集成需配合其他模块使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOSGS)
- [Epic Online Services 开发者文档](https://dev.epicgames.com/docs/epic-online-services)