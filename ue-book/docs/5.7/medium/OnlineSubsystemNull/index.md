# Online Subsystem Null

> Access to NULL platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemNull` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemNull) | |

## 用途

OnlineSubsystemNull 是 UE 在线子系统（Online Subsystem）框架的**占位/桩（stub）实现**。它不连接任何真实的在线服务（如 Steam、PlayStation Network、Xbox Live），而是提供一组本地模拟的在线接口，让游戏在没有后端服务的环境下也能跑通整个在线子系统的代码路径。

这个插件存在的核心目的有两个：

1. **开发期快速迭代** — 在开发早期或单人调试阶段，游戏代码已经写好了对 `IOnlineSubsystem` 的调用，但你还不想（或不能）接入真实平台。Null 子系统让你无需改任何游戏代码就能本地运行。
2. **自动化测试** — UE 的自动化测试框架大量依赖 Null 子系统来测试会话、身份认证、排行榜等功能，因为它不需要网络连接和真实账户。
3. **模拟不同平台行为** — 通过控制台变量（CVar）和配置文件，Null 子系统可以模拟各种平台特性（如自动登录、需要外部 UI 登录、双次登录等），用于测试不同平台的登录流程。

## 提供的接口

Null 子系统**实际实现**了以下在线接口：

| 接口 | 实现类 | 说明 |
|---|---|---|
| Session | `FOnlineSessionNull` | 完整的 LAN 会话支持（创建/搜索/加入/销毁），使用 `FLANSession` 进行局域网广播 |
| Identity | `FOnlineIdentityNull` | 模拟登录/登出，自动生成唯一用户 ID，支持稳定的 NullID |
| Leaderboards | `FOnlineLeaderboardsNull` | 本地内存排行榜，支持读写和查询 |
| Achievements | `FOnlineAchievementsNull` | 从 INI 配置读取成就定义，本地跟踪进度 |
| Voice | `FOnlineVoiceImpl` | 复用引擎内置的语音实现（`WITH_ENGINE` 时可用） |
| ExternalUI | `FOnlineExternalUINull` | 模拟外部 UI（登录页面、好友列表等），受 CVar 控制是否启用 |
| StoreV2 | `FOnlineStoreV2Null` | 模拟商店查询，生成假商品数据 |
| Purchase | `FOnlinePurchaseNull` | 模拟购买流程，生成假收据 |
| MessageSanitizer | `FMessageSanitizerNull` | 消息净化的桩实现，直接通过原始文本 |

以下接口返回 `nullptr`（不支持）：

- Friends、Party、Groups、SharedCloud、UserCloud、Entitlements
- Time、TitleFile、Events、Sharing、User、Message
- Presence、Chat、Stats、TurnBased、Tournament

## 使用场景

- **游戏开发早期**：你的多人游戏代码已经写好 `IOnlineSubsystem` 调用，但还没接入 Steam/EOS → 用 Null 子系统本地测试整个流程
- **LAN 局域网对战**：不需要互联网，两台机器在同一局域网内直接搜到对方的会话
- **自动化测试**：CI/CD 环境中跑在线功能的集成测试，无需真实账户
- **模拟特定平台行为**：通过 CVar 模拟 Switch 的自动登录、PlayStation 的外部 UI 登录等不同平台的登录方式

## 配置选项

Null 子系统的行为可通过两种方式配置：

### 控制台变量（CVar，运行时可改）

所有 CVar 以 `OSSNull.` 为前缀，可在控制台或 PIE 中动态修改：

| CVar | 默认值 | 说明 |
|---|---|---|
| `OSSNull.AutoLoginAtStartup` | `true` | 启动时自动登录第一个用户（模拟单用户平台） |
| `OSSNull.SupportExternalUI` | `false` | 启用外部 UI 接口 |
| `OSSNull.RequireShowLoginUI` | `false` | 登录需要调用 ShowLoginUI（需 SupportExternalUI=true） |
| `OSSNull.ForceShowLoginUIUserChange` | `false` | 登录 UI 中切换用户索引（模拟平台换号） |
| `OSSNull.RequireLoginCredentials` | `false` | 登录需要提供用户名/密码（模拟外部服务） |
| `OSSNull.AddUserNumToNullId` | `false` | 用户 ID 中包含本地用户编号（不同 LocalUserNum 产生不同 ID） |
| `OSSNull.ForceStableNullId` | `false` | 使用稳定的 Null ID（等同于命令行 `-StableNullID`） |
| `OSSNull.ForceOfflineMode` | `false` | 模拟离线模式，所有网络查询失败 |
| `OSSNull.OnlineRequiresSecondLogin` | `false` | 第一次登录仅算本地登录，需要第二次才获得在线访问 |

### INI 配置文件

在 `Engine.ini` 的 `[OnlineSubsystemNull]` 节中设置同样的键名（不含 `OSSNull.` 前缀），仅在初始化时读取一次。

### 命令行参数

| 参数 | 说明 |
|---|---|
| `-StableNullID` | 强制使用稳定的 Null ID（等同 `OSSNull.ForceStableNullId=true`） |

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemNull.h"
```

### 获取 Null 子系统实例

```cpp
// 获取默认的在线子系统（如果 DefaultPlatformService 设为 NULL，则就是 Null 子系统）
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();

// 显式获取 Null 子系统
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(NULL_SUBSYSTEM);
```

### 使用 Session 接口

```cpp
IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
if (SessionInterface.IsValid())
{
    // 创建 LAN 会话
    FOnlineSessionSettings SessionSettings;
    SessionSettings.bIsLANMatch = true;
    SessionSettings.NumPublicConnections = 4;
    SessionSettings.bShouldAdvertise = true;
    SessionSettings.bUsesPresence = true;

    SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);

    // 搜索 LAN 会话
    TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
    SearchSettings->bIsLanQuery = true;
    SearchSettings->MaxSearchResults = 10;
    SessionInterface->FindSessions(0, SearchSettings);
}
```

### 使用 Identity 接口

```cpp
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (IdentityInterface.IsValid())
{
    // 获取当前登录用户的唯一 ID
    FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);

    // 手动登录（当 AutoLoginAtStartup=false 时）
    FOnlineAccountCredentials Credentials;
    Credentials.Type = TEXT("NoAuth");
    IdentityInterface->Login(0, Credentials);

    // 获取登录状态
    ELoginStatus::Type Status = IdentityInterface->GetLoginStatus(0);
}
```

### 使用 Leaderboards 接口

```cpp
IOnlineLeaderboardsPtr LeaderboardsInterface = OnlineSub->GetLeaderboardsInterface();
if (LeaderboardsInterface.IsValid())
{
    // 写入分数
    FOnlineLeaderboardWrite WriteObject;
    WriteObject.SetIntStat(TEXT("Score"), 1000);
    LeaderboardsInterface->WriteLeaderboards(NAME_GameSession, *UserId, WriteObject);
    LeaderboardsInterface->FlushLeaderboards(NAME_GameSession);
}
```

### 使用 Achievements 接口

成就需要在 INI 配置中定义。在 `DefaultEngine.ini` 中：

```ini
[OnlineSubsystemNull]
Achievement_0_Id=Achievement_FirstKill
Achievement_0_Title=First Kill
Achievement_0_LockedDesc=Kill your first enemy
Achievement_0_UnlockedDesc=You killed your first enemy!
Achievement_0_bIsHidden=false
```

```cpp
IOnlineAchievementsPtr AchievementsInterface = OnlineSub->GetAchievementsInterface();
if (AchievementsInterface.IsValid())
{
    // 查询成就
    AchievementsInterface->QueryAchievements(*UserId);

    // 写入成就进度
    FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
    WriteObject->SetFloatStat(TEXT("Achievement_FirstKill"), 1.0);
    AchievementsInterface->WriteAchievements(*UserId, WriteObject);
}
```

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "OnlineSubsystem",
    "OnlineSubsystemUtils"
});
```

### DefaultEngine.ini 配置

```ini
[OnlineSubsystem]
DefaultPlatformService=Null

[OnlineSubsystemNull]
bAutoLoginAtStartup=true
bSupportExternalUI=false
bForceStableNullId=false
```

### 完整示例：LAN 会话创建与搜索

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    void CreateLanSession();
    void FindLanSessions();

private:
    FOnCreateSessionCompleteDelegate CreateSessionDelegate;
    FOnFindSessionsCompleteDelegate FindSessionsDelegate;
    TSharedRef<FOnlineSessionSearch> SessionSearch;

    void OnCreateSessionComplete(FName SessionName, bool bSuccess);
    void OnFindSessionsComplete(bool bSuccess);
};
```

```cpp
// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "OnlineSubsystem.h"
#include "OnlineSessionSettings.h"

void UMyGameInstance::CreateLanSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

    CreateSessionDelegate = FOnCreateSessionCompleteDelegate::CreateUObject(
        this, &UMyGameInstance::OnCreateSessionComplete);
    Sessions->AddOnCreateSessionCompleteDelegate_Handle(CreateSessionDelegate);

    FOnlineSessionSettings Settings;
    Settings.bIsLANMatch = true;
    Settings.NumPublicConnections = 4;
    Settings.bShouldAdvertise = true;

    Sessions->CreateSession(0, NAME_GameSession, Settings);
}

void UMyGameInstance::FindLanSessions()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

    FindSessionsDelegate = FOnFindSessionsCompleteDelegate::CreateUObject(
        this, &UMyGameInstance::OnFindSessionsComplete);
    Sessions->AddOnFindSessionsCompleteDelegate_Handle(FindSessionsDelegate);

    SessionSearch = MakeShared<FOnlineSessionSearch>();
    SessionSearch->bIsLanQuery = true;
    SessionSearch->MaxSearchResults = 10;

    Sessions->FindSessions(0, SessionSearch);
}

void UMyGameInstance::OnCreateSessionComplete(FName SessionName, bool bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("Session %s creation: %s"),
        *SessionName.ToString(), bSuccess ? TEXT("Success") : TEXT("Failed"));
}

void UMyGameInstance::OnFindSessionsComplete(bool bSuccess)
{
    if (bSuccess && SessionSearch.IsValid())
    {
        for (const FOnlineSessionSearchResult& Result : SessionSearch->SearchResults)
        {
            UE_LOG(LogTemp, Log, TEXT("Found session: %s"),
                *Result.Session.GetSessionIdStr());
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统框架核心接口定义 |
| `OnlineSubsystemUtils` | 在线子系统工具函数（Public） |
| `OnlineBase` | 在线基础类型 |
| `Core` | 引擎核心 |
| `CoreUObject` | UObject 系统 |
| `Sockets` | 网络 Socket 支持 |
| `Json` | JSON 解析（用于某些接口实现） |
| `Engine` | 引擎模块（条件依赖，`WITH_ENGINE` 时） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-21 | `2415c7aa` | 修复 Clang 20 编译时的 `[[nodiscard]]` 警告 — 纯编译兼容性修复 |
| 2025-05-15 | `58731816` | 在 OSSTests 中增加 `IOnlinePurchase::QueryReceipts` 测试支持 — 测试覆盖增强 |
| 2025-04-23 | `6ae57335` | 将所有文件的 DLL 导出标记从类型改为方法/静态变量 — 构建系统重构 |

### 维护评价

- **创建时间**：2016 年 7 月，已有约 10 年历史
- **最近更新**：2025 年 7 月仍有活跃更新，但以编译修复和构建系统调整为主，非功能性变更
- **代码稳定性**：核心逻辑非常稳定，近年来几乎无功能变化，说明该模块已进入成熟/维护模式
- **是否推荐使用**：✅ **强烈推荐**。这是 UE 在线子系统开发和测试的基石。所有使用 `IOnlineSubsystem` 的游戏都应该在开发阶段依赖 Null 子系统。`EnabledByDefault=true` 说明 Epic 自己也认为这是默认必备插件
- **注意事项**：Null 子系统仅用于开发和测试，不应作为最终发布的在线后端。发布前需要切换到真实的平台子系统（如 EOS、Steam 等）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemNull)
- [OnlineSubsystem 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystem)
- [OnlineSubsystemUtils 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils)
