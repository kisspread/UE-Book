# Online Subsystem EOS

> Online Subsystem for Epic Online Services

| 属性 | 值 |
|---|---|
| 中文名 | EOS 在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemEOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2020-10-10 |
| 年龄标签 | 👴 老古董（约 5 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemEOS) | |

## 用途

OnlineSubsystemEOS 是 Epic Games 为 **Epic Online Services (EOS)** 提供的 UE 在线子系统实现。它将 EOS SDK 的各项功能封装为 UE 标准的 `IOnlineSubsystem` 接口，使开发者可以通过统一的 `OnlineSubsystem` 抽象层访问 EOS 的所有在线服务。

该插件解决的核心问题是：让 UE 游戏能通过标准的在线子系统 API（如 `IOnlineIdentity`、`IOnlineSession`、`IOnlineFriends` 等）直接使用 EOS 服务，而无需直接调用 EOS C SDK。它同时支持 **Epic Account Services (EAS)** 和 **EOS Game Services (EOS Connect)** 两种认证模式，并集成了 Epic Games Store 的商城功能。

与 `OnlineSubsystemEOSPlus`（旧的桥接方案）不同，本插件直接实现 EOS 子系统，是 Epic 官方推荐的 EOS 集成方式。

## 使用场景

- 你的游戏需要**跨平台多人在线功能**（会话、匹配、邀请） → 使用 EOS Sessions & Lobbies
- 你需要**统一的跨平台账号系统**（支持 Epic、Steam、Nintendo 等身份提供商） → 使用 EOS Connect + EAS
- 你要实现**成就、排行榜、统计数据** → 使用 EOS Achievements/Leaderboards/Stats
- 你需要**云端存档**（Title Storage / Player Data Storage） → 使用 EOS Storage
- 你的游戏要接入 **Epic Games Store 商城**（购买、内购、权益） → 使用 EOS Ecom
- 你需要**实时语音聊天** → 使用 EOS RTC（Real-Time Communication）
- 你需要**玩家举报和制裁系统** → 使用 EOS Sanctions & Reports
- 你想在游戏内显示 **EOS 叠加层**（Overlay）用于社交/商城交互 → 配置 `bEnableOverlay`

## 蓝图用法

OnlineSubsystemEOS 是一个底层的 Runtime 插件，不直接暴露蓝图节点。所有功能通过 UE 标准的在线子系统蓝图接口访问（如 `GetSubsystem` 节点后调用 Friends/Session 等接口）。

### 核心配置（UEOSSettings）

在 `DefaultEngine.ini` 中配置 EOS 行为：

| 配置项 | 类型 | 说明 |
|---|---|---|
| `bUseEAS` | bool | 启用 Epic Account Services 登录（需要 Epic 账号） |
| `bUseEOSConnect` | bool | 启用 EOS Connect 登录（用于 Game Services） |
| `bEnableOverlay` | bool | 启用 EOS 叠加层（商城功能） |
| `bEnableSocialOverlay` | bool | 启用社交叠加层（好友、邀请） |
| `bEnableEditorOverlay` | bool | 编辑器中启用叠加层 |
| `bUseEOSRTC` | bool | 启用实时语音聊天 |
| `bUseNewEcomFlow` | bool | 使用新的 Ecom 集成（IOnlineEntitlements + IOnlinePurchase + IOnlineStoreV2） |
| `bPreferPersistentAuth` | bool | 登录时优先使用持久化认证 |
| `SteamTokenType` | FString | Steam 跨平台登录的 Token 类型（推荐 `"WebApi"`） |
| `TickBudgetInMilliseconds` | int32 | EOS 每帧 Tick 的时间预算（毫秒） |
| `DefaultArtifactName` | FString | 默认 Artifact 名称 |

### EOS 特有蓝图接口

通过 `IOnlineSubsystemEOS` 获取 EOS 专有功能：

| 接口 | 获取方式 | 说明 |
|---|---|---|
| `IOnlinePlayerSanctionEOS` | `GetPlayerSanctionEOSInterface()` | 查询玩家制裁、发起申诉 |
| `IOnlinePlayerReportEOS` | `GetPlayerReportEOSInterface()` | 发送玩家举报 |
| `IVoiceChatUser` | `GetVoiceChatUserInterface()` | 获取语音聊天用户接口 |
| `IEOSPlatformHandle` | `GetEOSPlatformHandle()` | 获取原始 EOS Platform Handle |

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemEOS.h"
#include "IOnlineSubsystemEOS.h"
#include "Interfaces/OnlinePlayerSanctionEOSInterface.h"
#include "Interfaces/OnlinePlayerReportEOSInterface.h"
```

### 基本用法：获取 EOS 子系统实例

```cpp
// 获取默认在线子系统（根据配置自动选择）
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();

// 或者显式获取 EOS 子系统
IOnlineSubsystem* OnlineSubEOS = IOnlineSubsystem::Get(EOS_SUBSYSTEM);

// 获取 EOS 专有接口
IOnlineSubsystemEOS* EOSSubsystem = static_cast<IOnlineSubsystemEOS*>(OnlineSubEOS);
if (EOSSubsystem)
{
    // 获取 EOS Platform Handle
    IEOSPlatformHandlePtr PlatformHandle = EOSSubsystem->GetEOSPlatformHandle();
    
    // 获取语音聊天用户
    IVoiceChatUser* VoiceChatUser = EOSSubsystem->GetVoiceChatUserInterface(*LocalUserId);
}
```

### 身份认证

```cpp
// 获取身份接口
IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();

// 使用 EOS Connect 登录（Game Services）
FOnlineAccountCredentials Credentials;
Credentials.Type = TEXT("accountportal");
Identity->Login(0, Credentials);

// 使用 exchange code 登录（从 Epic Games Launcher 启动时）
Credentials.Type = TEXT("exchangecode");
Credentials.Token = FCommandLine::Get().Get(TEXT("AUTH_LOGIN"));
Credentials.Id = TEXT("localhost");
Identity->Login(0, Credentials);
```

### 会话与大厅（Sessions & Lobbies）

```cpp
// 获取会话接口
IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

// 创建大厅会话
FOnlineSessionSettings Settings;
Settings.NumPublicConnections = 4;
Settings.bIsLANMatch = false;
Settings.bUsesPresence = true;
Settings.bAllowJoinInProgress = true;
Settings.bAllowJoinViaPresence = true;

// 通过自定义属性设置 BucketId
Settings.Set(OSSEOS_BUCKET_ID_ATTRIBUTE_KEY, FString(TEXT("MyBucket")), EOnlineDataAdvertisementType::ViaOnlineService);

Sessions->CreateSession(0, NAME_GameSession, Settings);

// 搜索会话
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->MaxSearchResults = 10;
SearchSettings->bIsLanQuery = false;

// 添加 BucketId 搜索过滤器
SearchSettings->QuerySettings.Set(OSSEOS_BUCKET_ID_ATTRIBUTE_KEY, FString(TEXT("MyBucket")), EOnlineComparisonOp::Equals);

Sessions->FindSessions(0, SearchSettings);
```

### 玩家举报

```cpp
#include "Interfaces/OnlinePlayerReportEOSInterface.h"

IOnlineSubsystemEOS* EOSSubsystem = static_cast<IOnlineSubsystemEOS*>(IOnlineSubsystem::Get(EOS_SUBSYSTEM));
IOnlinePlayerReportEOSPtr ReportInterface = EOSSubsystem->GetPlayerReportEOSInterface();

IOnlinePlayerReportEOS::FSendPlayerReportSettings ReportSettings;
ReportSettings.Category = IOnlinePlayerReportEOS::EPlayerReportCategory::Cheating;
ReportSettings.Message = TEXT("Using aimbot in competitive match");
ReportSettings.Context = TEXT("{\"matchId\":\"abc123\",\"gameMode\":\"ranked\"}");

ReportInterface->SendPlayerReport(
    *LocalUserId,
    *TargetUserId,
    MoveTemp(ReportSettings),
    FOnSendPlayerReportComplete::CreateLambda([](bool bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Player report sent: %s"), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
    })
);
```

### 玩家制裁查询

```cpp
#include "Interfaces/OnlinePlayerSanctionEOSInterface.h"

IOnlinePlayerSanctionEOSPtr SanctionInterface = EOSSubsystem->GetPlayerSanctionEOSInterface();

// 查询活跃制裁
SanctionInterface->QueryActivePlayerSanctions(
    *LocalUserId,
    *TargetUserId,
    FOnQueryActivePlayerSanctionsComplete::CreateLambda([SanctionInterface, TargetUserId](bool bWasSuccessful)
    {
        if (bWasSuccessful)
        {
            TArray<IOnlinePlayerSanctionEOS::FOnlinePlayerSanction> Sanctions;
            EOnlineCachedResult::Type Result = SanctionInterface->GetCachedActivePlayerSanctions(*TargetUserId, Sanctions);
            
            for (const auto& Sanction : Sanctions)
            {
                UE_LOG(LogTemp, Log, TEXT("Sanction: %s, Expires: %lld"), *Sanction.Action, Sanction.TimeExpires);
            }
        }
    })
);

// 发起制裁申诉
IOnlinePlayerSanctionEOS::FPlayerSanctionAppealSettings AppealSettings;
AppealSettings.Reason = IOnlinePlayerSanctionEOS::EPlayerSanctionAppealReason::IncorrectSanction;
AppealSettings.ReferenceId = TEXT("sanction-id-to-appeal");

SanctionInterface->CreatePlayerSanctionAppeal(
    *LocalUserId,
    MoveTemp(AppealSettings),
    FOnCreatePlayerSanctionAppealComplete::CreateLambda([](bool bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Appeal submitted: %s"), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
    })
);
```

## Demo 示例

### EOS 基础连接与登录

```cpp
// EOSDemo.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "OnlineSubsystem.h"
#include "IOnlineSubsystemEOS.h"
#include "EOSDemo.generated.h"

UCLASS()
class UEOSDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintCallable, Category = "EOS Demo")
    void LoginWithAccountPortal();

    UFUNCTION(BlueprintCallable, Category = "EOS Demo")
    void QueryAndDisplaySanctions(const FString& TargetUserIdStr);

    UFUNCTION(BlueprintCallable, Category = "EOS Demo")
    void SendReport(const FString& TargetUserIdStr, int32 CategoryIndex, const FString& Message);

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnSanctionsQueryComplete(bool bWasSuccessful);

    FDelegateHandle LoginDelegateHandle;
};
```

```cpp
// EOSDemo.cpp
#include "EOSDemo.h"
#include "OnlineIdentityInterface.h"
#include "OnlineSubsystemEOS.h"
#include "Interfaces/OnlinePlayerSanctionEOSInterface.h"
#include "Interfaces/OnlinePlayerReportEOSInterface.h"

void UEOSDemoSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Log, TEXT("EOSDemo: Subsystem initialized"));
}

void UEOSDemoSubsystem::Deinitialize()
{
    // 清理委托
    if (IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM))
    {
        if (IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface())
        {
            if (LoginDelegateHandle.IsValid())
            {
                Identity->ClearOnLoginCompleteDelegate_Handle(0, LoginDelegateHandle);
            }
        }
    }
    Super::Deinitialize();
}

void UEOSDemoSubsystem::LoginWithAccountPortal()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Error, TEXT("EOSDemo: EOS subsystem not available"));
        return;
    }

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("EOSDemo: Identity interface not available"));
        return;
    }

    // 注册登录完成回调
    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(0,
        FOnLoginCompleteDelegate::CreateUObject(this, &UEOSDemoSubsystem::OnLoginComplete));

    // 使用 account portal 方式登录
    FOnlineAccountCredentials Credentials;
    Credentials.Type = TEXT("accountportal");
    Identity->Login(0, Credentials);

    UE_LOG(LogTemp, Log, TEXT("EOSDemo: Login initiated via account portal"));
}

void UEOSDemoSubsystem::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("EOSDemo: Login successful, UserId: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("EOSDemo: Login failed: %s"), *Error);
    }
}

void UEOSDemoSubsystem::QueryAndDisplaySanctions(const FString& TargetUserIdStr)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineSubsystemEOS* EOSSubsystem = static_cast<IOnlineSubsystemEOS*>(OnlineSub);
    IOnlinePlayerSanctionEOSPtr SanctionInterface = EOSSubsystem->GetPlayerSanctionEOSInterface();
    if (!SanctionInterface.IsValid()) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    FUniqueNetIdPtr LocalUserId = Identity->GetUniquePlayerId(0);
    if (!LocalUserId.IsValid()) return;

    TSharedRef<const FUniqueNetId> TargetId = Identity->CreateUniquePlayerId(TargetUserIdStr);
    IOnlinePlayerSanctionEOSPtr SanctionRef = SanctionInterface;

    SanctionInterface->QueryActivePlayerSanctions(
        *LocalUserId,
        *TargetId,
        FOnQueryActivePlayerSanctionsComplete::CreateLambda([SanctionRef, TargetId](bool bSuccess)
        {
            if (bSuccess)
            {
                TArray<IOnlinePlayerSanctionEOS::FOnlinePlayerSanction> Sanctions;
                SanctionRef->GetCachedActivePlayerSanctions(*TargetId, Sanctions);
                for (const auto& S : Sanctions)
                {
                    UE_LOG(LogTemp, Log, TEXT("Sanction: %s, Expires: %lld"), *S.Action, S.TimeExpires);
                }
            }
        })
    );
}

void UEOSDemoSubsystem::SendReport(const FString& TargetUserIdStr, int32 CategoryIndex, const FString& Message)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineSubsystemEOS* EOSSubsystem = static_cast<IOnlineSubsystemEOS*>(OnlineSub);
    IOnlinePlayerReportEOSPtr ReportInterface = EOSSubsystem->GetPlayerReportEOSInterface();
    if (!ReportInterface.IsValid()) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    FUniqueNetIdPtr LocalUserId = Identity->GetUniquePlayerId(0);
    if (!LocalUserId.IsValid()) return;

    TSharedRef<const FUniqueNetId> TargetId = Identity->CreateUniquePlayerId(TargetUserIdStr);

    IOnlinePlayerReportEOS::FSendPlayerReportSettings ReportSettings;
    ReportSettings.Category = static_cast<IOnlinePlayerReportEOS::EPlayerReportCategory>(CategoryIndex);
    ReportSettings.Message = Message;

    ReportInterface->SendPlayerReport(
        *LocalUserId,
        *TargetId,
        MoveTemp(ReportSettings),
        FOnSendPlayerReportComplete::CreateLambda([](bool bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Report sent: %s"), bSuccess ? TEXT("OK") : TEXT("Failed"));
        })
    );
}
```

## 模块依赖

该插件的 Build.cs 依赖以下模块（省略常见的 Core/Engine/Slate 等）：

| 模块 | 用途 |
|---|---|
| `EOSSDK` | Epic Online Services 核心 SDK |
| `OnlineSubsystem` | UE 在线子系统框架基类 |
| `OnlineSubsystemUtils` | 在线子系统工具函数 |
| `OnlineBase` | 在线系统基础设施 |
| `Sockets` | 网络 Socket 支持（EOS P2P） |
| `Networking` | 网络传输层 |
| `VoiceChat` | 语音聊天基础设施（EOS RTC） |

**使用方注意事项**：你的模块 Build.cs 需要添加对 `OnlineSubsystemEOS` 的依赖才能使用 EOS 专有接口（如 `IOnlinePlayerSanctionEOS`、`IOnlinePlayerReportEOS`）。标准在线接口通过 `OnlineSubsystem` 模块访问即可。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `2fc71253` | OnlineSubsystemEOS/OnlineServicesEOSGS: trigger OnExternalUIChange on bIsExclusiveInput, dedup uncha | 修复外部 UI 变更事件触发逻辑 |
| 2026-05-12 | `6ff79bee` | - Add new call stats delegate passing a channelName | 新增带频道名的通话统计委托 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 64 位格式化字符串兼容性问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志系统迁移到 UE_LOGF 宏 |
| 2026-04-03 | `ec1a1dbf` | Add CVar to disable EOS Connect logout cascading to EAS logout | 新增 CVar 控制 Connect 登出是否级联到 EAS 登出 |

### 维护评价

**活跃维护**。OnlineSubsystemEOS 是 Epic Games 的核心在线服务插件，自 2020 年创建以来持续获得功能性更新和 Bug 修复。近期（2026 年）仍有实质性的功能增强和问题修复，包括语音统计改进、日志系统迁移、登出行为配置化等。

**注意事项**：
- 该插件 **默认未启用**（`EnabledByDefault: false`），需要在项目设置中手动启用
- 需要有效的 EOS SDK 和开发者账号配置
- 已废弃 `bUseNewLoginFlow` 配置项（旧登录流程已移除）
- `SteamTokenType` 的默认值 `"Session"` 已标记为废弃，推荐迁移到 `"WebApi"`
- 插件受 `WITH_EOS_SDK` 宏控制，未安装 EOS SDK 时会编译为空实现

**推荐使用**：这是 Epic Games 官方的 EOS 集成方案，适合所有需要接入 Epic Online Services 的项目。相比社区方案，它享有最高优先级的官方支持和维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemEOS)
- [EOS 开发者文档](https://dev.epicgames.com/docs/epic-online-services)
- [EOS SDK 官网](https://dev.epicgames.com/en-US/sdk)