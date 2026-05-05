# Online Subsystem EOS

> Online Subsystem for Epic Online Services

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemEOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-09 |
| 年龄标签 | 🆕（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemEOS) | |

## 用途

OnlineSubsystemEOS 是 UE5 的 Online Subsystem 抽象层的 **Epic Online Services (EOS)** 实现。它将 UE 内置的 `IOnlineSubsystem` 接口（Session、Identity、Friends、Leaderboards 等）桥接到 EOS SDK，使项目可以通过统一的 UE 网络接口调用 Epic 的后端服务。

与 `OnlineSubsystemEOSPlus`（提供多平台身份桥接、Steam/PSN 登录转发）不同，本插件是 **直接使用 EOS SDK** 的底层实现，适用于不需要第三方平台身份代理的场景——例如纯 EOS 项目或自定义登录流程。

**核心能力：**
- EOS Auth（Epic Account Services）和 EOS Connect（Game Services）双登录模式
- EOS Sessions 和 EOS Lobbies 两种会话机制
- 好友系统、Presence、用户查询（通过 `FUserManagerEOS` 统一管理）
- 排行榜、成就、统计
- 商店（Ecom）、购买
- 标题存储（Title Storage）和玩家数据存储（Player Data Storage）
- 语音聊天（通过 EOSVoiceChat 插件集成）
- 玩家举报与制裁系统
- LAN 会话回退支持

## 使用场景

- 你需要在项目中集成 Epic Online Services 后端 → 启用本插件并配置 Artifact 设置
- 你需要跨平台多人游戏（PC/Mac/Linux/Android）通过 EOS 匹配 → 使用 Session/Lobby 接口
- 你需要 Epic 账号社交功能（好友列表、邀请、Presence）→ 配置 `bUseEAS=true`
- 你只需要 EOS Game Services（无需 Epic 账号）→ 配置 `bUseEOSConnect=true`
- 你需要玩家举报/制裁功能 → 通过 `IOnlinePlayerReportEOS` / `IOnlinePlayerSanctionEOS` 接口

## 蓝图用法

本插件 **没有** 暴露任何 `BlueprintCallable` 或 `BlueprintReadWrite` 函数。所有功能通过 C++ Online Subsystem 接口访问。蓝图可以通过 UE 内置的 Online Subsystem 蓝图节点（如 `GetSubsystem` → `GetSessionInterface`）间接使用。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemEOS.h"
#include "IOnlineSubsystemEOS.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineFriendsInterface.h"
```

### 基本用法：获取 EOS 子系统

```cpp
// 获取 OnlineSubsystemEOS 实例
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
if (OnlineSub)
{
    // 获取各接口指针
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    IOnlineFriendsPtr Friends = OnlineSub->GetFriendsInterface();
    IOnlineLeaderboardsPtr Leaderboards = OnlineSub->GetLeaderboardsInterface();
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    IOnlineStoreV2Ptr Store = OnlineSub->GetStoreV2Interface();
    IOnlineStatsPtr Stats = OnlineSub->GetStatsInterface();
}
```

来源: `OnlineSubsystemEOS/Private/OnlineSubsystemEOS.cpp`

### 登录（Identity）

```cpp
IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();

// EOS Auth 登录（Epic Account Services）
FOnlineAccountCredentials Credentials;
Credentials.Type = TEXT("persistentauth");  // 或 "exchangecode", "password"
Identity->Login(0, Credentials);

// 监听登录完成
Identity->AddOnLoginCompleteDelegate_Handle(
    0,  // LocalUserNum
    FOnLoginCompleteDelegate::CreateLambda(
        [](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
        {
            if (bWasSuccessful)
            {
                UE_LOG(LogTemp, Log, TEXT("EOS Login successful: %s"), *UserId.ToString());
            }
        }));
```

来源: `OnlineSubsystemEOS/Private/UserManagerEOS.h`

### 创建会话（Session）

```cpp
IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

// 创建 EOS Session
FOnlineSessionSettings SessionSettings;
SessionSettings.NumPublicConnections = 4;
SessionSettings.bIsLANMatch = false;
SessionSettings.bUsesPresence = true;
SessionSettings.bAllowJoinInProgress = true;
SessionSettings.Set(SETTING_MAPNAME, FString("MyMap"), EOnlineDataAdvertisementType::ViaOnlineServiceAndPing);

// 可选：通过 BucketId 区分不同类型会话
SessionSettings.Set(OSSEOS_BUCKET_ID_ATTRIBUTE_KEY, FString("Default"), EOnlineDataAdvertisementType::ViaOnlineService);

Sessions->AddOnCreateSessionCompleteDelegate_Handle(
    FOnCreateSessionCompleteDelegate::CreateLambda(
        [](FName SessionName, bool bWasSuccessful)
        {
            UE_LOG(LogTemp, Log, TEXT("Session '%s' created: %s"), *SessionName.ToString(), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
        }));

Sessions->CreateSession(0, NAME_GameSession, SessionSettings);
```

来源: `OnlineSubsystemEOS/Private/OnlineSessionEOS.h`

### 搜索与加入会话

```cpp
// 搜索会话
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->MaxSearchResults = 10;
SearchSettings->bIsLanQuery = false;
// 可选：按 BucketId 搜索
SearchSettings->QuerySettings.Set(OSSEOS_BUCKET_ID_ATTRIBUTE_KEY, FString("Default"), EOnlineComparisonOp::Equals);

Sessions->FindSessions(0, SearchSettings);

// 加入搜索到的会话
// 在 OnFindSessionsComplete 回调中:
TArray<FOnlineSessionSearchResult>& Results = SearchSettings->SearchResults;
if (Results.Num() > 0)
{
    Sessions->JoinSession(0, NAME_GameSession, Results[0]);
}
```

来源: `OnlineSubsystemEOS/Private/OnlineSessionEOS.h`

### EOS 专有接口：玩家举报与制裁

```cpp
// 获取 EOS 专有接口
IOnlineSubsystemEOS* EOSSub = static_cast<IOnlineSubsystemEOS*>(OnlineSub);

// 举报玩家
IOnlinePlayerReportEOSPtr Report = EOSSub->GetPlayerReportEOSInterface();
IOnlinePlayerReportEOS::FSendPlayerReportSettings ReportSettings;
ReportSettings.Category = IOnlinePlayerReportEOS::EPlayerReportCategory::Cheating;
ReportSettings.Message = TEXT("Using aimbot");
Report->SendPlayerReport(MyUserId, TargetUserId, MoveTemp(ReportSettings),
    FOnSendPlayerReportComplete::CreateLambda([](bool bSuccess) {}));

// 查询玩家制裁
IOnlinePlayerSanctionEOSPtr Sanction = EOSSub->GetPlayerSanctionEOSInterface();
Sanction->QueryActivePlayerSanctions(MyUserId, TargetUserId,
    FOnQueryActivePlayerSanctionsComplete::CreateLambda([Sanction, TargetUserId](bool bSuccess)
    {
        if (bSuccess)
        {
            TArray<IOnlinePlayerSanctionEOS::FOnlinePlayerSanction> Sanctions;
            Sanction->GetCachedActivePlayerSanctions(TargetUserId, Sanctions);
        }
    }));
```

来源: `OnlineSubsystemEOS/Public/Interfaces/OnlinePlayerSanctionEOSInterface.h`, `OnlinePlayerReportEOSInterface.h`

### 语音聊天

```cpp
// 获取 EOS 语音聊天用户接口
IOnlineSubsystemEOS* EOSSub = static_cast<IOnlineSubsystemEOS*>(OnlineSub);
IVoiceChatUser* VoiceChatUser = EOSSub->GetVoiceChatUserInterface(LocalUserId);
if (VoiceChatUser)
{
    // 加入语音频道
    VoiceChatUser->JoinChannel(TEXT("TeamChannel"), TEXT(""), EVoiceChatChannelType::NonPositional,
        FOnVoiceChatChannelJoinCompleteDelegate::CreateLambda(
            [](const FString& ChannelName, const FVoiceChatResult& Result) {}));

    // 监听玩家说话状态
    VoiceChatUser->OnVoiceChatPlayerTalkingUpdated().AddLambda(
        [](const FString& PlayerName, bool bIsTalking) {});
}
```

来源: `OnlineSubsystemEOS/Private/OnlineSubsystemEOS.cpp`

### 进阶用法：获取 EOS SDK 原生 Handle

```cpp
// 需要直接操作 EOS SDK 时，获取 Platform Handle
IOnlineSubsystemEOS* EOSSub = static_cast<IOnlineSubsystemEOS*>(OnlineSub);
IEOSPlatformHandlePtr PlatformHandle = EOSSub->GetEOSPlatformHandle();
if (PlatformHandle.IsValid())
{
    // 直接使用 EOS C API
    EOS_HAuth AuthHandle = EOS_Platform_GetAuthInterface(*PlatformHandle);
    // ... 自由使用 EOS SDK
}
```

来源: `OnlineSubsystemEOS/Private/OnlineSubsystemEOS.h`

## Demo 示例

### .h

```cpp
#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "EOSSubsystemExample.generated.h"

UCLASS()
class UEOSSubsystemExample : public UGameInstanceSubsystem
{
    GENERATED_BODY()
public:
    void Initialize(FSubsystemCollectionBase& Collection) override;
    void Deinitialize() override;

    void LoginAndCreateSession();

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnSessionCreated(FName SessionName, bool bWasSuccessful);
};
```

### .cpp

```cpp
#include "EOSSubsystemExample.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemEOS.h"
#include "IOnlineSubsystemEOS.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineSessionInterface.h"

void UEOSSubsystemExample::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
}

void UEOSSubsystemExample::Deinitialize()
{
    Super::Deinitialize();
}

void UEOSSubsystemExample::LoginAndCreateSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return;

    Identity->AddOnLoginCompleteDelegate_Handle(0,
        FOnLoginCompleteDelegate::CreateUObject(this, &UEOSSubsystemExample::OnLoginComplete));

    FOnlineAccountCredentials Credentials;
    Credentials.Type = TEXT("persistentauth");
    Identity->Login(0, Credentials);
}

void UEOSSubsystemExample::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
    const FUniqueNetId& UserId, const FString& Error)
{
    if (!bWasSuccessful) return;

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

    Sessions->AddOnCreateSessionCompleteDelegate_Handle(
        FOnCreateSessionCompleteDelegate::CreateUObject(this, &UEOSSubsystemExample::OnSessionCreated));

    FOnlineSessionSettings Settings;
    Settings.NumPublicConnections = 8;
    Settings.bIsLANMatch = false;
    Settings.bUsesPresence = true;

    Sessions->CreateSession(0, NAME_GameSession, Settings);
}

void UEOSSubsystemExample::OnSessionCreated(FName SessionName, bool bWasSuccessful)
{
    UE_LOG(LogTemp, Log, TEXT("EOS Session created: %s"), bWasSuccessful ? TEXT("OK") : TEXT("FAIL"));
}
```

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "OnlineSubsystem",
    "OnlineSubsystemEOS",
    "EOSShared"
});
```

## 配置说明

通过 `DefaultEngine.ini` 或编辑器 **Project Settings → Plugins → Online Subsystem EOS** 配置：

```ini
[/Script/OnlineSubsystemEOS.EOSSettings]
bUseEAS=false
bUseEOSConnect=true
bUseEOSRTC=true
bEnableOverlay=false
bEnableSocialOverlay=false
DefaultArtifactName=MyGameArtifact

+Artifacts=(ArtifactName="MyGameArtifact",ClientId="abc123",ClientSecret="secret",ProductId="prod-id",SandboxId="sandbox-id",DeploymentId="deploy-id",ClientEncryptionKey="key")
```

**关键设置：**
- `bUseEAS`：启用 Epic Account Services 登录（需要用户拥有 Epic 账号）
- `bUseEOSConnect`：启用 EOS Game Services 登录（匿名或平台 token 登录）
- `bEnableOverlay`：启用 EOS Overlay（用于 Ecom 功能）
- `bEnableSocialOverlay`：启用社交 Overlay（好友、邀请等）
- `Artifacts`：每个环境（Staging/QA/Production）的 Artifact 配置

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EOSSDK` | Epic Online Services C SDK |
| `EOSShared` | EOS SDK 共享工具和类型 |
| `OnlineSubsystem` | UE Online Subsystem 基础框架 |
| `OnlineSubsystemUtils` | OSS 工具函数 |
| `EOSVoiceChat` | EOS 语音聊天实现 |
| `SocketSubsystemEOS` | EOS 网络 Socket 子系统 |
| `Core` | UE 核心 |
| `CoreOnline` | 在线核心类型 |
| `CoreUObject` | UObject 系统 |
| `Engine` | UE 引擎 |
| `Json` | JSON 解析 |
| `OnlineBase` | 在线基础模块 |
| `Sockets` | Socket 抽象 |
| `NetCore` | 网络核心 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-09-23 | `c851b862481e` | EOSSDK CL45343210 Release v1.18.0.4 Full update — EOS SDK 版本升级到 v1.18.0.4 |
| 2025-09-23 | `14fcdb4e2c8d` | [Backout] - CL45934846 回退了上一次更新 |
| 2025-09-23 | `4c26457bcc02` | EOSSDK CL45343210 Release v1.18.0.4 Full update — 同上，重新提交 |

解读：最近更新集中在 EOS SDK 版本升级（v1.18.0.4），属于常规依赖更新，非功能性改动。

### 维护评价

- **创建时间**：2020 年 10 月，约 6 年历史
- **更新频率**：活跃维护中。EOS SDK 定期升级，跟随 Epic 服务端更新
- **维护状态**：✅ **活跃维护** — 作为 Epic 官方 EOS 集成的核心组件，由 Epic Games 持续维护
- **平台支持**：Win64, Mac, Linux, LinuxArm64, Android
- **注意事项**：
  - `EnabledByDefault=false`，需手动在 `.uproject` 或项目设置中启用
  - 需要在 [Epic Developer Portal](https://dev.epicgames.com/services) 注册产品并获取 Artifact 配置
  - `bUseNewLoginFlow` 已在 5.7 标记为废弃（旧登录流程已移除）
- **推荐度**：✅ **强烈推荐** — 使用 EOS 服务的唯一官方 UE 集成方式

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemEOS)
- [Epic Online Services 文档](https://dev.epicgames.com/docs/dev-portal)
- [EOS SDK API 参考](https://dev.epicgames.com/docs/api-ref)
