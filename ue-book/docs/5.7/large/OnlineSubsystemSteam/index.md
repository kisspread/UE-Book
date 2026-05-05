# Online Subsystem Steam

> Access to Steam platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemSteam` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemSteam) | |

## 用途

OnlineSubsystemSteam 是 UE5 的 Steam 平台在线子系统实现。它将 Steamworks SDK 的各种功能（身份认证、会话管理、好友列表、排行榜、成就、语音、云存储、内购等）封装为 UE 标准的 `IOnlineSubsystem` 接口，使游戏可以通过统一的 API 访问 Steam 平台服务，而无需直接调用 Steamworks SDK。

**核心价值**：通过 UE 的 Online Subsystem 抽象层，一套代码可以在 Steam、EOS、PlayStation 等多个平台之间切换，只需更改配置即可。

**默认不启用**：需要在项目的 `DefaultEngine.ini` 中手动配置 Steam 子系统，并确保 Steamworks SDK 已正确集成。

## 使用场景

- 你在做一个 PC 多人游戏，需要 Steam 好友邀请、大厅匹配和语音聊天 → 使用 OnlineSubsystemSteam
- 你需要 Steam 排行榜和成就系统 → 通过 `IOnlineLeaderboards` 和 `IOnlineAchievements` 接口
- 你要运行 Steam 专用服务器（Dedicated Server）→ 该插件支持 Game Server API 初始化
- 你需要 Steam 云存储来保存玩家数据 → 通过 `IOnlineUserCloud` 和 `IOnlineSharedCloud` 接口
- 你需要集成 Steam 微交易/DLC 购买 → 通过 `IOnlinePurchase` 和 `IOnlineStoreV2` 接口

## 架构总览

### 核心类：`FOnlineSubsystemSteam`

继承自 `FOnlineSubsystemImpl`，是整个 Steam 在线子系统的入口点。它管理所有子接口的生命周期：

```
FOnlineSubsystemSteam
├── SessionInterface        (FOnlineSessionSteam)       — 会话/大厅管理
├── IdentityInterface       (FOnlineIdentitySteam)      — 身份认证
├── FriendInterface         (FOnlineFriendsSteam)       — 好友列表
├── PresenceInterface       (FOnlinePresenceSteam)      — 在线状态
├── AuthInterface           (FOnlineAuthSteam)          — Steam Auth 票据
├── AuthInterfaceUtils      (FOnlineAuthUtilsSteam)     — Auth 工具
├── LeaderboardsInterface   (FOnlineLeaderboardsSteam)  — 排行榜
├── AchievementsInterface   (FOnlineAchievementsSteam)  — 成就
├── VoiceInterface          (FOnlineVoiceSteam)         — 语音
├── ExternalUIInterface     (FOnlineExternalUISteam)    — Steam Overlay UI
├── SharedCloudInterface    (FOnlineSharedCloudSteam)   — 共享云存储
├── UserCloudInterface      (FOnlineUserCloudSteam)     — 用户云存储
├── EncryptedAppTicketInterface (FOnlineEncryptedAppTicketSteam) — 加密票据
├── PingInterface           (FOnlinePingInterfaceSteam) — P2P 延迟计算
├── PurchaseInterface       (FOnlinePurchaseSteam)      — 内购
└── StoreInterface          (FOnlineStoreSteam)         — 商店
```

### 会话类型（ESteamSession）

| 类型 | 说明 |
|---|---|
| `LobbySession` | Steam 大厅会话，由 Steam 后端管理 |
| `AdvertisedSessionHost` | 以 Game Server 模式托管的公开服务器 |
| `AdvertisedSessionClient` | 加入 Game Server 的客户端 |
| `LANSession` | 局域网会话，使用 LAN Beacon 管理 |
| `None` | 未定义 |

### 线程模型

插件使用独立的异步任务线程 `FOnlineAsyncTaskManagerSteam`，所有 Steam API 回调通过该线程处理，再将结果派发到游戏线程。Steam API 回调需要在主线程定期调用 `SteamAPI_RunCallbacks()`，这由 `Tick()` 方法处理。

## 接口详解

### Session（会话管理）

**实现类**：`FOnlineSessionSteam`

支持三种会话模式：

1. **Lobby（大厅）**：玩家通过 Steam 大厅匹配，适合 P2P 游戏
2. **Internet（Game Server）**：专用服务器/Listen 服务器通过 Steam 服务器列表广播
3. **LAN**：局域网匹配，使用 UDP Beacon

关键功能：
- 创建/加入/销毁大厅和服务器会话
- 通过命令行参数解析邀请信息（`-lobby=` 和 IP 地址）
- 自动注册语音系统
- Steam 服务器名称可通过 `-SteamServerName=` 启动参数自定义

### Identity（身份认证）

**实现类**：`FOnlineIdentitySteam`

- 基于 Steam 自动登录机制，`Login()` 和 `AutoLogin()` 行为一致
- 提供 `FUniqueNetIdSteam`（uint64 Steam ID）作为唯一标识
- 获取 Steam 昵称、认证 Token
- 支持 `RevokeAuthToken` 和 `GetLinkedAccountAuthToken`

### Friends（好友系统）

**实现类**：`FOnlineFriendsSteam`

- 读取好友列表（支持默认/在线/游戏中/会话中过滤）
- 发送/接受/拒绝好友邀请
- 屏蔽/解除屏蔽玩家
- 查询最近一起玩的玩家

### Leaderboards（排行榜）

**实现类**：`FOnlineLeaderboardsSteam`

- 创建/查找 Steam 排行榜
- 按排名范围、好友、指定玩家读取排行榜
- 写入并刷新玩家分数

### Achievements（成就）

**实现类**：`FOnlineAchievementsSteam`

- 查询成就进度和描述
- 解锁/写入成就
- 支持从 `DefaultEngine.ini` 配置成就 ID

配置示例：
```ini
[OnlineSubsystemSteam]
Achievement_0_Id=ACH_WIN_ONE_GAME
Achievement_1_Id=ACH_WIN_100_GAMES
```

### External UI（Steam Overlay）

**实现类**：`FOnlineExternalUISteam`

通过 Steam Overlay 打开各种 UI：
- 好友列表、邀请 UI
- 成就 UI、排行榜 UI
- Steam 商店页面
- 玩家资料页面
- 网页 URL、消息发送

### Cloud（云存储）

**用户云存储**（`FOnlineUserCloudSteam`）：
- 枚举、读取、写入、删除用户的云文件
- 每用户最多 100 个文件，单文件最大 100MB（Steam 限制）

**共享云存储**（`FOnlineSharedCloudSteam`）：
- 通过 `UGCHandle` 共享文件给其他玩家

### Auth（认证）

**实现类**：`FOnlineAuthSteam`

- 自动生成和验证 Steam 认证票据
- 支持 `GetAuthTicketForWebApi` 用于 Web API 验证
- 通过 `PacketHandler` 组件自动拦截连接并验证
- 验证失败时自动踢出玩家（可通过 `OverrideFailureDelegate` 覆盖）

**工具类**（`FOnlineAuthUtilsSteam`）：
- `IsSteamAuthEnabled()` 检查是否启用了 Steam Auth
- 提供认证结果委托

### Encrypted App Ticket（加密应用票据）

**实现类**：`FOnlineEncryptedAppTicketSteam`

- 请求加密应用票据（限频：每 60 秒一次）
- 获取加密后的票据数据
- 用于服务端验证玩家身份

### Voice（语音）

**实现类**：`FOnlineVoiceSteam`

- 基于 Steam Voice API 实现语音通信
- 创建 `FVoiceEngineSteam` 处理音频编解码
- 仅在编译引擎时可用（`WITH_ENGINE`）

### Purchase & Store（购买与商店）

**购买接口**（`FOnlinePurchaseSteam`）：
- 支持微交易结账流程
- 需要后端服务器配合 Steam Web API 完成交易
- 提供 `ISteamPurchasingServerLink` 接口供自定义后端集成
- 支持从配置文件定义静态微交易（开发调试用）

配置示例（开发调试）：
```ini
[OnlineSubsystemSteam]
+StaticMicrotransactions=(Id=100, Amount=299, Description=Remove Ads)
+StaticMicrotransactions=(Id=101, Amount=999, Description=Starter Pack)
```

**商店接口**（`FOnlineStoreSteam`）：
- 查询商品分类和商品列表
- 与购买接口联动

### Ping（延迟计算）

**实现类**：`FOnlinePingInterfaceSteam`（抽象类）

- 检查是否使用 P2P Relay 网络
- 获取和计算基于 Steam Relay Network 的延迟数据
- 具体实现依赖网络层（SteamSockets 等）

## 蓝图用法

OnlineSubsystemSteam 本身不直接暴露 `UFUNCTION(BlueprintCallable)` 蓝图节点。它的所有接口都是 C++ 级别的 `IOnlineSubsystem` 抽象。

蓝图中使用 Steam 功能的常见方式：

### 通过 GameInstance 获取子系统

```
Get Game Instance → Get Online Subsystem → 返回 "Steam" 子系统
```

### 通过蓝图函数库

UE 内置的 `OnlineSubsystemBlueprintLibrary` 提供蓝图友好的包装节点：
- `Find Sessions` / `Create Session` / `Join Session`
- `Get Login Status`
- `Read Friends List` / `Get Friends List`
- `Write Leaderboards` / `Read Leaderboards`
- `Write Achievements` / `Query Achievements`
- `Show External UI` (好友邀请、成就页面等)

### 使用示例（蓝图描述）

**创建 Steam 大厅会话**：
1. 在蓝图中调用 `Create Session` 节点
2. 设置 `Num Public Connections`、`bUseLAN=false`、`bAllowInvites=true`
3. 绑定 `On Success` / `On Failure` 委托
4. 成功后其他玩家可通过 `Find Sessions` 搜索并加入

**显示 Steam 好友邀请 UI**：
1. 调用 `Show Invite UI` 节点
2. 传入 `Local Player Index` 和 `Session Name`
3. Steam Overlay 会自动打开邀请界面

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSteam.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineIdentityInterface.h"
```

### 基本用法

**获取 Steam 子系统**：

```cpp
// 来源: OnlineSubsystemSteam.h
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
if (OnlineSub)
{
    // 获取各种接口
    IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();
}
```

**获取当前登录用户的 Steam ID**：

```cpp
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);
if (UserId.IsValid())
{
    FString PlayerName = IdentityInterface->GetPlayerNickname(0);
    UE_LOG(LogTemp, Log, TEXT("Logged in as: %s"), *PlayerName);
}
```

**创建大厅会话**：

```cpp
IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
if (SessionInterface.IsValid())
{
    FOnlineSessionSettings SessionSettings;
    SessionSettings.NumPublicConnections = 4;
    SessionSettings.bShouldAdvertise = true;
    SessionSettings.bUsesPresence = true;
    SessionSettings.bAllowJoinInProgress = true;
    SessionSettings.bAllowInvites = true;
    
    SessionInterface->OnCreateSessionCompleteDelegates.AddUObject(
        this, &AMyClass::OnCreateSessionComplete);
    SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
}
```

### 进阶用法

**Steam Game Server 模式**：

```cpp
// 来源: OnlineSubsystemSteam.cpp
// 专用服务器通过 Game Server API 初始化
// 配置: DefaultEngine.ini
// [OnlineSubsystemSteam]
// bInitServerOnClient=true  (如果需要在客户端也初始化服务器 API)

// 检查 Game Server 是否就绪
FOnlineSubsystemSteam* SteamOSS = static_cast<FOnlineSubsystemSteam*>(OnlineSub);
if (SteamOSS->IsSteamServerAvailable())
{
    // 服务器 API 已初始化，可以创建服务器会话
}
```

**自定义认证失败处理**：

```cpp
// 来源: OnlineAuthInterfaceUtilsSteam.h
FOnlineSubsystemSteam* SteamOSS = static_cast<FOnlineSubsystemSteam*>(
    IOnlineSubsystem::Get(STEAM_SUBSYSTEM));

FOnlineAuthSteamUtilsPtr AuthUtils = SteamOSS->GetAuthInterfaceUtils();
if (AuthUtils.IsValid())
{
    // 覆盖默认的踢出行为
    AuthUtils->OverrideFailureDelegate.BindLambda(
        [](const FUniqueNetId& FailedUserId)
        {
            UE_LOG(LogTemp, Warning, TEXT("Auth failed for %s, but we're not kicking"),
                *FailedUserId.ToString());
        });
    
    // 监听认证结果
    AuthUtils->OnAuthenticationResultWithCodeDelegate.AddLambda(
        [](const FUniqueNetId& UserId, bool bSuccess, ESteamAuthResponseCode Code)
        {
            UE_LOG(LogTemp, Log, TEXT("Auth result for %s: %s (code %d)"),
                *UserId.ToString(), bSuccess ? TEXT("OK") : TEXT("FAIL"), (int)Code);
        });
}
```

**加密应用票据**：

```cpp
// 来源: OnlineEncryptedAppTicketInterfaceSteam.h
FOnlineEncryptedAppTicketSteamPtr EncTicket = SteamOSS->GetEncryptedAppTicketInterface();
if (EncTicket.IsValid())
{
    // 监听结果
    EncTicket->OnEncryptedAppTicketResultDelegate.AddLambda(
        [EncTicket](bool bAvailable, int32 ResultCode)
        {
            if (bAvailable)
            {
                TArray<uint8> EncryptedData;
                EncTicket->GetEncryptedAppTicket(EncryptedData);
                // 发送 EncryptedData 到后端服务器验证
            }
        });
    
    // 请求加密票据（60 秒限频）
    FString UserData = TEXT("my_server_token");
    EncTicket->RequestEncryptedAppTicket(
        (void*)TCHAR_TO_UTF8(*UserData), UserData.Len());
}
```

**自定义购买后端**：

```cpp
// 来源: OnlinePurchaseInterfaceSteam.h
class FMyPurchasingServerLink : public ISteamPurchasingServerLink
{
public:
    virtual void InitiateTransaction(
        const FUniqueNetId& UserId,
        TArray<FSteamPurchaseDef> Mtxns,
        const FOnPurchaseCheckoutComplete& Delegate) override
    {
        // 调用你的后端服务器，使用 Steam Web API 的 InitTxn
        // 处理完成后触发 Delegate
    }
};

// 注册自定义后端
FOnlinePurchaseSteam* PurchaseInt = static_cast<FOnlinePurchaseSteam*>(
    SteamOSS->GetPurchaseInterface().Get());
PurchaseInt->RegisterServerLink(
    MakeShared<FMyPurchasingServerLink>());
```

## Demo 示例

### 最小 Steam 会话示例

**MyGame.Build.cs**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "OnlineSubsystem",
    "OnlineSubsystemUtils",
    "OnlineSubsystemSteam"
});
```

**DefaultEngine.ini**：
```ini
[OnlineSubsystem]
DefaultPlatformService=Steam

[OnlineSubsystemSteam]
SteamDevAppId=480
bRelaunchInSteam=false
bEnabled=true

[/Script/OnlineSubsystemSteam.OnlineSubsystemSteam]
bInitServerOnClient=false
```

**MyGameInstance.h**：
```cpp
#pragma once
#include "Engine/GameInstance.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    void CreateSteamLobby();
    void FindSteamLobbies();

private:
    void OnCreateSessionComplete(FName SessionName, bool bSuccess);
    void OnFindSessionsComplete(bool bSuccess);
    
    TSharedPtr<FOnlineSessionSearch> SessionSearch;
};
```

**MyGameInstance.cpp**：
```cpp
#include "MyGameInstance.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSteam.h"

void UMyGameInstance::CreateSteamLobby()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    
    Sessions->OnCreateSessionCompleteDelegates.AddUObject(
        this, &UMyGameInstance::OnCreateSessionComplete);
    
    FOnlineSessionSettings Settings;
    Settings.NumPublicConnections = 4;
    Settings.bShouldAdvertise = true;
    Settings.bUsesPresence = true;
    Settings.bAllowJoinInProgress = true;
    
    Sessions->CreateSession(0, NAME_GameSession, Settings);
}

void UMyGameInstance::FindSteamLobbies()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    
    SessionSearch = MakeShareable(new FOnlineSessionSearch());
    SessionSearch->MaxSearchResults = 20;
    SessionSearch->bIsLanQuery = false;
    
    Sessions->OnFindSessionsCompleteDelegates.AddUObject(
        this, &UMyGameInstance::OnFindSessionsComplete);
    Sessions->FindSessions(0, SessionSearch.ToSharedRef());
}

void UMyGameInstance::OnCreateSessionComplete(FName SessionName, bool bSuccess)
{
    if (bSuccess)
    {
        UE_LOG(LogTemp, Log, TEXT("Session '%s' created!"), *SessionName.ToString());
        // GetWorld()->ServerTravel("/Game/Maps/MyMap?listen");
    }
}

void UMyGameInstance::OnFindSessionsComplete(bool bSuccess)
{
    if (bSuccess && SessionSearch.IsValid())
    {
        for (const FOnlineSessionSearchResult& Result : SessionSearch->SearchResults)
        {
            UE_LOG(LogTemp, Log, TEXT("Found session: %s, Ping: %d"),
                *Result.Session.SessionSettings.ToString(), Result.PingInMs);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 核心基础库 |
| `CoreUObject` | UObject 系统 |
| `NetCore` | 网络核心 |
| `OnlineBase` | 在线子系统基础 |
| `OnlineSubsystem` | 在线子系统框架 |
| `OnlineSubsystemUtils` | 在线子系统工具（Public 依赖） |
| `Json` | JSON 解析 |
| `Projects` | 项目/插件管理 |
| `SteamShared` | Steam 共享模块，管理 Steamworks 实例句柄 |
| `PacketHandler` | 网络数据包处理，用于 Steam Auth |
| `Sockets` | 网络 Socket 抽象 |
| `Engine` | 引擎核心（条件依赖，`bCompileAgainstEngine`） |
| `Voice` | 语音引擎（条件依赖） |
| `AudioMixer` | 音频混合器（条件依赖） |
| `Steamworks` | Steam SDK 本体（第三方静态库） |

## 平台支持

| 平台 | 支持 |
|---|---|
| Win64 | ✅（排除 ARM64） |
| Mac | ✅ |
| Linux | ✅ |
| 其他平台 | ❌ |

## 配置参考

### DefaultEngine.ini 完整配置

```ini
[OnlineSubsystem]
DefaultPlatformService=Steam

[OnlineSubsystemSteam]
; 开发用 App ID（480 是 Spacewar 测试 ID）
SteamDevAppId=480

; 是否在非 Steam 启动时自动通过 Steam 重启
bRelaunchInSteam=false

; 是否在客户端也初始化 Game Server API
bInitServerOnClient=false

; 是否允许 P2P 数据包中继（通过 Steam Relay Network）
bAllowP2PPacketRelay=true

; Steam Auth 票据验证相关
; 通过 PacketHandler 配置自动启用

; 成就配置（可选）
Achievement_0_Id=YOUR_ACHIEVEMENT_ID

; 微交易配置（仅开发调试）
; +StaticMicrotransactions=(Id=100, Amount=299, Description=ItemName)

[/Script/Engine.GameEngine]
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="OnlineSubsystemSteam.SteamNetDriver",DriverClassNameFallback="OnlineSubsystemUtils.IpNetDriver")
```

### 启动参数

| 参数 | 说明 |
|---|---|
| `-NOSTEAM` | 禁用 Steam |
| `-SteamServerName=MyServer` | 自定义专用服务器名称 |
| `-lobby=<lobbyid>` | 自动加入指定大厅 |
| `-nullsteam` | 使用 null Steam 实现（测试用） |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-08-27 | `5d419ad8` | 修复 `GetLinkedAccountAuthToken` 绑定了旧式完成委托但未解绑，导致每次调用额外触发一次回调 |
| 2025-08-05 | `67b2a369` | 修复 Steam 共享指针分配导致的 Presence 崩溃问题 |
| 2025-06-26 | `a2e75189` | 为有对应 `.gen.cpp` 的源文件添加 `UE_INLINE_GENERATED_CPP_BY_NAME`（代码修正工具批量处理） |

### 维护评价

- **活跃维护**：最近一次实质性更新在 2025 年 8 月，修复了 bug
- **核心插件**：作为 Epic 官方维护的 Steam 平台集成，是 PC 游戏开发的核心组件
- **稳定性高**：代码成熟，主要更新以 bug 修复和编译兼容性为主
- **注意事项**：
  - Steam 微交易购买接口需要自定义后端服务器实现，Epic 未提供官方参考实现
  - 部分接口返回 `nullptr`（如 Party、Groups、Chat、Stats、Time、Entitlements、TitleFile、Sharing、User、Message、TurnBased、Tournament）
  - 语音功能依赖 `WITH_ENGINE` 编译标记
  - 不支持 Win64:arm64 架构

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemSteam)
- [Steamworks 官方文档](https://partner.steamgames.com/doc/sdk)
- [UE Online Subsystem 文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/online-subsystem-in-unreal-engine)
