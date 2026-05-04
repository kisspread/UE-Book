# Online Subsystem GDK

> Access to GDK platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（本地化资源） |
| 模块 | `OnlineSubsystemGDK` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2026-03-31 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/OnlineSubsystemGDK) | |

## 用途

OnlineSubsystemGDK 是 Unreal Engine 在线子系统（Online Subsystem）框架针对 **Microsoft GDK（Game Development Kit）** 平台的完整实现。GDK 是微软用于 Xbox 和 Windows GDK 游戏开发的官方 SDK，该插件将 UE5 通用的在线服务接口桥接到 Xbox Live 后端服务。

插件的核心价值在于：开发者使用 UE5 标准的 `IOnlineSubsystem` / `IOnlineSession` / `IOnlineIdentity` 等接口编写代码，底层自动对接 Xbox Live 的 MPSD（Multiplayer Session Directory）、SmartMatch 匹配、排行榜、成就、商店等服务。这意味着同一套在线逻辑可以跨平台运行，只需切换 Online Subsystem 实现。

**注意**：该插件需要 Microsoft GDK SDK（`WITH_GRDK` 宏）才能编译，仅支持 Win64 平台，且默认不启用（`EnabledByDefault: false`），需要手动在项目设置中启用。

### 覆盖的在线服务接口

| 接口 | 对应类 | 功能 |
|---|---|---|
| Identity | `FOnlineIdentityGDK` | Xbox Live 登录/登出、XSTS Token、用户权限检查 |
| Session | `FOnlineSessionGDK` | 多人会话创建/加入/销毁，基于 MPSD |
| Matchmaking | `FOnlineMatchmakingInterfaceGDK` | Xbox Live SmartMatch 匹配 |
| User | `FOnlineUserGDK` | 用户信息查询、隐私权限、通信权限 |
| Friends | `FOnlineFriendsGDK` | 好友列表 |
| Leaderboards | `FOnlineLeaderboardsGDK` | 排行榜读取 |
| Achievements | `FOnlineAchievementsGDK` | 成就写入 |
| Store | `FOnlineStoreGDK` | Xbox 商店目录 |
| Purchase | `FOnlinePurchaseGDK` | 购买流程 |
| ExternalUI | `FOnlineExternalUIGDK` | 平台原生 UI（好友邀请等） |
| Presence | `FOnlinePresenceGDK` | 用户在线状态/活动 |
| Voice | `FOnlineVoiceGDK` | 语音聊天 |
| Stats | `FOnlineStatsGDK` | 用户统计数据 |
| Events | `FOnlineEventsGDK` | 遥测事件 |
| Profile | `FOnlineProfileGDK` | 用户资料 |
| UserCloud | `FOnlineUserCloudGDK` | 云存档 |
| MessageSanitizer | `FMessageSanitizerGDK` | 消息过滤 |

## 使用场景

- 你正在为 **Xbox 主机** 或 **Windows GDK** 平台开发多人游戏 → 使用此插件对接 Xbox Live 全套在线服务
- 你需要 Xbox Live 的 **SmartMatch 匹配系统** → 通过 `IOnlineSession::StartMatchmaking` 自动对接
- 你需要 Xbox Live **排行榜和成就** → 通过标准 `IOnlineLeaderboards` / `IOnlineAchievements` 接口
- 你需要 Xbox **商店内购** → 通过 `IOnlineStore` / `IOnlinePurchase` 接口
- 你的游戏需要跨平台在线功能，且其中一方是 Xbox → 此插件作为 Xbox 端的 Online Subsystem 实现

## 蓝图用法

OnlineSubsystemGDK 本身不暴露额外的蓝图节点。所有在线功能通过 UE5 标准的 **Online Subsystem 蓝图库** 访问。确保在 `DefaultEngine.ini` 中配置：

```ini
[OnlineSubsystem]
DefaultPlatformService=GDK

[OnlineSubsystemGDK]
bEnabled=true
```

### 核心节点（通过标准 Online Subsystem 蓝图接口）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Login` | 使用 Xbox Live 账号登录 | `IOnlineIdentity` |
| `GetLoginStatus` | 获取当前登录状态 | `IOnlineIdentity` |
| `GetUniquePlayerId` | 获取本地玩家的唯一 ID（XUID） | `IOnlineIdentity` |
| `CreateSession` | 创建多人会话 | `IOnlineSession` |
| `FindSessions` | 搜索可用会话 | `IOnlineSession` |
| `JoinSession` | 加入已有会话 | `IOnlineSession` |
| `StartMatchmaking` | 启动 SmartMatch 匹配 | `IOnlineSession` |
| `ReadLeaderboards` | 读取排行榜数据 | `IOnlineLeaderboards` |
| `WriteAchievements` | 写入成就进度 | `IOnlineAchievements` |
| `QueryUserInfo` | 查询用户资料信息 | `IOnlineUser` |

### 使用示例（蓝图描述）

**登录 Xbox Live**：
1. 获取 `Get Online Subsystem` 节点 → 选择 `GDK`
2. 连接到 `Get Identity Interface` → 调用 `Login`（LocalUserNum=0）
3. 绑定 `OnLoginComplete` 委托，检查 `bWasSuccessful`

**创建并加入会话**：
1. 获取 `Session Interface` → 调用 `Create Session`（LocalUserNum=0, SessionName="Game"）
2. 在 `OnCreateSessionComplete` 中检查成功后，其他玩家调用 `Find Sessions`
3. 搜索结果中选择会话 → 调用 `Join Session`

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemGDK.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineLeaderboardsInterface.h"
```

### 基本用法

**获取 GDK Online Subsystem 并登录**：

```cpp
// 获取 GDK Online Subsystem
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("GDK"));
if (!OnlineSub)
{
    UE_LOG(LogTemp, Error, TEXT("GDK Online Subsystem not available"));
    return;
}

// 获取 Identity 接口
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (IdentityInterface.IsValid())
{
    // 绑定登录完成回调
    IdentityInterface->AddOnLoginCompleteDelegate_Handle(
        0,  // LocalUserNum
        FOnLoginCompleteDelegate::CreateLambda(
            [](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
            {
                if (bWasSuccessful)
                {
                    UE_LOG(LogTemp, Log, TEXT("GDK Login successful, UserId: %s"), *UserId.ToString());
                }
                else
                {
                    UE_LOG(LogTemp, Error, TEXT("GDK Login failed: %s"), *Error);
                }
            })
    );

    // 执行自动登录（Xbox 平台通常使用 AutoLogin）
    IdentityInterface->AutoLogin(0);
}
```

**检查用户权限**（来源：`OnlineIdentityInterfaceGDK.h`）：

```cpp
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);

if (UserId.IsValid())
{
    // 检查用户是否有在线多人游戏权限
    IdentityInterface->GetUserPrivilege(
        *UserId,
        EUserPrivileges::Type::CanPlayOnline,
        IOnlineIdentity::FOnGetUserPrivilegeCompleteDelegate::CreateLambda(
            [](const FUniqueNetId& UserId, EUserPrivileges::Type Privilege, uint32 PrivilegeResult)
            {
                if (PrivilegeResult == static_cast<uint32>(IOnlineIdentity::EPrivilegeResults::NoFailures))
                {
                    UE_LOG(LogTemp, Log, TEXT("User has online play privilege"));
                }
            }),
        EShowPrivilegeResolveUI::Default  // 可弹出系统 UI 解决权限问题
    );
}
```

### 进阶用法

**创建会话并设置为活动（Activity）**：

```cpp
// 来源：OnlineAsyncTaskGDKCreateSession.h
IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();

FOnlineSessionSettings SessionSettings;
SessionSettings.bIsLANMatch = false;
SessionSettings.NumPublicConnections = 4;
SessionSettings.bShouldAdvertise = true;
SessionSettings.bUsesPresence = true;
SessionSettings.Set(SETTING_MAPNAME, FString(TEXT("MyMap")), EOnlineDataAdvertisementType::ViaOnlineService);

SessionInterface->AddOnCreateSessionCompleteDelegate_Handle(
    FOnCreateSessionCompleteDelegate::CreateLambda(
        [](FName SessionName, bool bWasSuccessful)
        {
            UE_LOG(LogTemp, Log, TEXT("Session '%s' created: %s"),
                *SessionName.ToString(),
                bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
        })
);

SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
```

**通过搜索句柄查找公开会话**：

```cpp
// 来源：OnlineAsyncTaskGDKFindSessionsBySearchHandle.h
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->MaxSearchResults = 10;
SearchSettings->bIsLanQuery = false;
SearchSettings->QuerySettings.Set(SEARCH_PRESENCE, true, EOnlineComparisonOp::Equals);

SessionInterface->AddOnFindSessionsCompleteDelegate_Handle(
    FOnFindSessionsCompleteDelegate::CreateLambda(
        [SessionInterface](bool bWasSuccessful)
        {
            if (bWasSuccessful)
            {
                TSharedRef<FOnlineSessionSearch> Search = SessionInterface->GetSearchResults();
                for (const FOnlineSessionSearchResult& Result : Search->SearchResults)
                {
                    UE_LOG(LogTemp, Log, TEXT("Found session: %s, Ping: %d"),
                        *Result.Session.OwningUserName, Result.PingInMs);
                }
            }
        })
);

SessionInterface->FindSessions(0, SearchSettings);
```

**读取排行榜**：

```cpp
// 来源：OnlineAsyncTaskGDKGetLeaderboard.h
IOnlineLeaderboardsPtr LeaderboardsInterface = OnlineSub->GetLeaderboardsInterface();

FOnlineLeaderboardReadPtr ReadObject = MakeShared<FOnlineLeaderboardRead>();
ReadObject->LeaderboardName = TEXT("GlobalScore");
ReadObject->SortedColumn = TEXT("Score");

LeaderboardsInterface->AddOnLeaderboardReadCompleteDelegate_Handle(
    FOnLeaderboardReadCompleteDelegate::CreateLambda(
        [LeaderboardsInterface](bool bWasSuccessful)
        {
            if (bWasSuccessful)
            {
                // 处理排行榜数据
            }
        })
);

LeaderboardsInterface->ReadLeaderboardsForFriends(0, ReadObject);
```

## Demo 示例

### GDK 登录与会话创建的最小示例

**GDKOnlineDemo.h**：

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "GDKOnlineDemo.generated.h"

UCLASS()
class UGDKOnlineDemo : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 初始化并尝试 GDK 登录 */
    UFUNCTION(BlueprintCallable, Category = "GDK Demo")
    void LoginToGDK();

    /** 创建一个简单的多人会话 */
    UFUNCTION(BlueprintCallable, Category = "GDK Demo")
    void CreateDemoSession(int32 MaxPlayers);

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
                         const FUniqueNetId& UserId, const FString& Error);
    void OnCreateSessionComplete(FName SessionName, bool bWasSuccessful);

    FDelegateHandle LoginDelegateHandle;
    FDelegateHandle CreateSessionDelegateHandle;
};
```

**GDKOnlineDemo.cpp**：

```cpp
#include "GDKOnlineDemo.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSettings.h"

void UGDKOnlineDemo::LoginToGDK()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("GDK"));
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Warning, TEXT("GDK Online Subsystem not found. Ensure it is enabled."));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        return;
    }

    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(
        0, FOnLoginCompleteDelegate::CreateUObject(this, &UGDKOnlineDemo::OnLoginComplete));

    // Xbox 平台使用 AutoLogin，会使用当前 Xbox 用户
    Identity->AutoLogin(0);
}

void UGDKOnlineDemo::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
                                      const FUniqueNetId& UserId, const FString& Error)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("GDK"));
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    Identity->ClearOnLoginCompleteDelegate_Handle(0, LoginDelegateHandle);

    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("GDK Login OK: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("GDK Login Failed: %s"), *Error);
    }
}

void UGDKOnlineDemo::CreateDemoSession(int32 MaxPlayers)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("GDK"));
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    if (!Sessions.IsValid())
    {
        return;
    }

    FOnlineSessionSettings Settings;
    Settings.NumPublicConnections = MaxPlayers;
    Settings.bShouldAdvertise = true;
    Settings.bUsesPresence = true;
    Settings.bIsLANMatch = false;

    CreateSessionDelegateHandle = Sessions->AddOnCreateSessionCompleteDelegate_Handle(
        FOnCreateSessionCompleteDelegate::CreateUObject(
            this, &UGDKOnlineDemo::OnCreateSessionComplete));

    Sessions->CreateSession(0, NAME_GameSession, Settings);
}

void UGDKOnlineDemo::OnCreateSessionComplete(FName SessionName, bool bWasSuccessful)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(TEXT("GDK"));
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    Sessions->ClearOnCreateSessionCompleteDelegate_Handle(CreateSessionDelegateHandle);

    UE_LOG(LogTemp, Log, TEXT("Session '%s' created: %s"),
        *SessionName.ToString(),
        bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
}
```

## 模块依赖

从 `OnlineSubsystemGDK.Build.cs` 和 `.uplugin` 的 Plugins 列表提取：

| 模块 | 用途 |
|---|---|
| `PlayFabParty` | PlayFab Party 网络传输层，用于 GDK 平台的点对点/中继网络通信 |
| `GDKNetDriver` | GDK 平台专用网络驱动，处理底层网络传输 |
| `OnlineSubsystem` | UE5 在线子系统框架基类 |
| `OnlineSubsystemUtils` | 在线子系统工具函数库 |

**外部 SDK 依赖**（编译时需要）：
- Microsoft GDK SDK（`WITH_GRDK` 宏）
- XSAPI-C（Xbox Services API C 绑定）
- XAL（Xbox Authentication Library）
- XUser / XGame / XSystem / XNetworking 等 GDK 运行时头文件

## 维护状态

### 近期更新

```
- 2026-04-24 101f2bf3 Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout)
- 2026-04-17 4260cb83 Load Achivements.json from $(ProjectDir)/Config/Xbl and deprecate the $(ProjectDir)/Platforms/GDK/Co
- 2026-04-16 270dc64a Fix unreachable code warnings
```

### 维护评价

**活跃维护中**。该插件创建于 2026 年 3 月底，至今不到一个月，但已有密集的功能更新：

- **ARM64 支持**（2026-04-24）：新增 GDK ARM64 架构支持，表明正在跟进最新的 GDK SDK 演进
- **成就配置迁移**（2026-04-17）：将 Achievements.json 加载路径迁移到 `$(ProjectDir)/Config/Xbl`，废弃旧路径，说明正在规范化配置结构
- **编译警告修复**（2026-04-16）：修复不可达代码警告，保持代码质量

作为 Epic Games 官方维护的 Xbox 平台核心在线服务插件，它与 GDK SDK 版本紧密绑定，会随 GDK 更新持续维护。**推荐在 Xbox/Windows GDK 项目中使用**。

⚠️ **注意**：该插件默认不启用（`EnabledByDefault: false`），需要手动在项目中启用，并确保开发环境已安装 Microsoft GDK SDK。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/OnlineSubsystemGDK)
- [Microsoft GDK 文档](https://learn.microsoft.com/en-us/gaming/gdk/)
- [Xbox Live Services API (XSAPI)](https://learn.microsoft.com/en-us/gaming/gdk/_content/gc/system/overlive/live-overview)