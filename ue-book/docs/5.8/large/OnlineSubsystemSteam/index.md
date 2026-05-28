# Online Subsystem Steam

> Access to Steam platform

| 属性 | 值 |
|---|---|
| 中文名 | Steam 在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemSteam` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏜️ 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemSteam) | |

## 用途

`OnlineSubsystemSteam` 插件是虚幻引擎与 Steamworks SDK 之间的核心桥梁。它的主要职责是将 Steam 平台的在线服务（如多人游戏、身份验证、好友、排行榜、成就、云存储、微交易等）封装并暴露给虚幻引擎的在线子系统框架。

该插件解决的核心问题是：**让虚幻引擎游戏能够无缝、标准化地接入 Steam 平台的所有在线功能**，而无需开发者直接处理复杂的 Steamworks API 和平台特定细节。它实现了 `IOnlineSubsystem` 接口及其所有子接口，使得游戏代码可以通过统一的接口与 Steam 进行交互。

## 使用场景

-   你的游戏计划在 Steam 上发行，并需要使用 Steam 的**大厅、专用服务器列表、P2P 直连**等多人游戏功能。
-   你需要集成 Steam 的**好友系统**，实现邀请加入、好友列表查看和状态追踪。
-   你希望使用 Steam 的**成就系统**来解锁和展示玩家的游戏成就。
-   你需要实现基于 Steam 的**玩家身份验证**（Session Auth）来确保多人游戏的合法性。
-   你的游戏需要**Steam 云存储**功能来同步玩家存档或游戏配置。
-   你计划通过**Steam 商店**进行游戏内微交易或购买 DLC（需要配合后端服务器实现完整流程）。

## 蓝图用法

`OnlineSubsystemSteam` 的大部分功能通过引擎的 `OnlineSubsystem` 接口在 C++ 层面访问。蓝图中直接可用的函数相对较少，通常用于查询状态。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsSteamClientAvailable` | 检查 Steam 客户端接口是否可用（通常需要 Steam 客户端正在运行）。 | `FOnlineSubsystemSteam` |
| `IsSteamServerAvailable` | 检查 Steam 游戏服务器接口是否可用。 | `FOnlineSubsystemSteam` |
| `IsUsingSteamNetworking` | 查询当前是否正在使用 Steam Networking（P2P）功能。 | `FOnlineSubsystemSteam` |
| `GetSteamAppId` | 获取当前应用的 Steam App ID。 | `FOnlineSubsystemSteam` |

### 使用示例（蓝图描述）

1.  **获取在线子系统接口**：在蓝图中，通常通过 `Get Online Subsystem` 节点并传入子系统名称（`STEAM`）来获取 `IOnlineSubsystem` 接口指针。然后可以调用如 `Get Session Interface`、`Get Friends Interface` 等节点来访问具体的服务。
2.  **检查 Steam 可用性**：可以在游戏初始化时，使用 `Is Steam Client Available` 节点来判断当前环境是否支持完整的 Steam 功能。如果不支持，可能需要提示玩家启动 Steam 客户端。

## C++ 用法

该插件的 C++ 用法是核心，通过访问 `FOnlineSubsystemSteam` 实例及其提供的各种接口类来实现。

### 头文件引入

```cpp
#include "OnlineSubsystemSteam.h"
#include "OnlineSubsystemSteamTypes.h" // 对于 FUniqueNetIdSteam 等类型
```

### 基本用法

**获取子系统实例并访问接口**（来源：典型游戏初始化代码模式）：

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSteam.h"

void AMyGameMode::InitOnlineSubsystem()
{
    // 获取 Steam 在线子系统
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (OnlineSub)
    {
        // 获取会话接口
        IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
        if (SessionInterface.IsValid())
        {
            // 使用会话接口...
            // 例如，创建会话
            FOnlineSessionSettings SessionSettings;
            SessionSettings.bIsLANMatch = false;
            SessionSettings.NumPublicConnections = 4;
            SessionSettings.bShouldAdvertise = true;
            SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
        }

        // 获取身份接口
        IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
        if (IdentityInterface.IsValid())
        {
            // 自动登录（通常 Steam 环境下由客户端自动处理）
            IdentityInterface->AutoLogin(0);
        }
    }
}
```

**使用 Steam 特定的唯一网络ID**：

```cpp
#include "OnlineSubsystemSteamTypes.h"

void SomeFunction(const FUniqueNetId& NetId)
{
    // 检查该ID是否为Steam类型
    if (NetId.GetType() == STEAM_SUBSYSTEM)
    {
        // 安全地转换为 Steam 专用ID
        const FUniqueNetIdSteam& SteamId = FUniqueNetIdSteam::Cast(NetId);
        // 现在可以获取原始的 CSteamID 或 uint64
        CSteamID NativeSteamID = SteamId;
        uint64 RawSteamID = SteamId.GetUniqueNetId();

        // 用于 Steam 原生 API 调用
        // SteamFriends()->GetFriendPersonaName(NativeSteamID);
    }
}
```

### 进阶用法

**实现 Steam 微交易购买服务端链接**（来源：`OnlinePurchaseInterfaceSteam.h`）：
要使用完整的 Steam 内购功能，你需要实现 `ISteamPurchasingServerLink` 接口，并通过 `FOnlinePurchaseSteam::RegisterServerLink` 注册。

```cpp
// MySteamServerLink.h
#pragma once
#include "OnlinePurchaseInterfaceSteam.h"

class FMySteamServerLink : public ISteamPurchasingServerLink
{
public:
    virtual void InitiateTransaction(const FUniqueNetId& UserId, TArray<FSteamPurchaseDef> Mtxns, const FOnPurchaseCheckoutComplete& Delegate) override;
    // ... 实现其他虚函数
};

// MySteamServerLink.cpp
#include "MySteamServerLink.h"

void FMySteamServerLink::InitiateTransaction(const FUniqueNetId& UserId, TArray<FSteamPurchaseDef> Mtxns, const FOnPurchaseCheckoutComplete& Delegate)
{
    // 在这里调用你的后端服务器API，使用Steam的 InitTxn 接口处理购买请求
    // 你的服务器完成流程后，应调用Delegate并传入结果
    // 示例：
    bool bSuccess = CallMyBackendServer(UserId, Mtxns);
    FPurchaseReceipt Receipt; // 填充收据
    Delegate.ExecuteIfBound(UserId, bSuccess ? EOnlineErrorResult::Success : EOnlineErrorResult::Fail, Receipt);
}
```

**监听 Steam 认证事件**（来源：`OnlineAuthInterfaceUtilsSteam.h`）：

```cpp
#include "OnlineAuthInterfaceUtilsSteam.h"

void AMyGameMode::ListenForAuthEvents()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (FOnlineSubsystemSteam* SteamSub = static_cast<FOnlineSubsystemSteam*>(OnlineSub))
    {
        // 获取认证工具接口
        FOnlineAuthSteamUtilsPtr AuthUtils = SteamSub->GetAuthInterfaceUtils();
        if (AuthUtils.IsValid())
        {
            // 绑定认证失败事件（默认行为是踢出玩家）
            AuthUtils->OverrideFailureDelegate.BindLambda([](const FUniqueNetId& FailedUserId)
            {
                UE_LOG(LogTemp, Warning, TEXT("Player authentication failed: %s"), *FailedUserId.ToString());
                // 可以在此执行自定义逻辑，而不是立即踢出
            });

            // 绑定认证结果事件（更详细的回调）
            AuthUtils->OnAuthenticationResultWithCodeDelegate.AddLambda([](const FUniqueNetId& UserId, bool bSuccess, ESteamAuthResponseCode ResponseCode)
            {
                UE_LOG(LogTemp, Log, TEXT("Auth result for %s: Success=%d, Code=%d"), *UserId.ToString(), bSuccess, (int32)ResponseCode);
            });
        }
    }
}
```

## Demo 示例

一个最小化的 Steam 会话创建和加入示例。

**MySteamGameMode.h**
```cpp
#pragma once
#include "GameFramework/GameModeBase.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "MySteamGameMode.generated.h"

UCLASS()
class AMySteamGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    void CreateSteamSession();
    void FindAndJoinSession();

private:
    void OnCreateSessionComplete(FName SessionName, bool bSuccess);
    void OnFindSessionsComplete(bool bSuccess);

    TSharedPtr<FOnlineSessionSearch> SessionSearch;
    FOnCreateSessionCompleteDelegate CreateSessionCompleteDelegate;
    FOnFindSessionsCompleteDelegate FindSessionsCompleteDelegate;
    FDelegateHandle CreateSessionCompleteDelegateHandle;
    FDelegateHandle FindSessionsCompleteDelegateHandle;
};
```

**MySteamGameMode.cpp**
```cpp
#include "MySteamGameMode.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSteam.h"

void AMySteamGameMode::BeginPlay()
{
    Super::BeginPlay();

    // 绑定委托
    CreateSessionCompleteDelegate = FOnCreateSessionCompleteDelegate::CreateUObject(this, &AMySteamGameMode::OnCreateSessionComplete);
    FindSessionsCompleteDelegate = FOnFindSessionsCompleteDelegate::CreateUObject(this, &AMySteamGameMode::OnFindSessionsComplete);

    // 创建一个会话作为示例
    CreateSteamSession();
}

void AMySteamGameMode::CreateSteamSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
        if (Sessions.IsValid())
        {
            // 配置会话设置
            FOnlineSessionSettings SessionSettings;
            SessionSettings.bIsLANMatch = false;
            SessionSettings.NumPublicConnections = 4;
            SessionSettings.bShouldAdvertise = true;
            SessionSettings.bUsesPresence = true;

            // 绑定并创建会话
            CreateSessionCompleteDelegateHandle = Sessions->AddOnCreateSessionCompleteDelegate_Handle(CreateSessionCompleteDelegate);
            Sessions->CreateSession(0, NAME_GameSession, SessionSettings);
        }
    }
}

void AMySteamGameMode::OnCreateSessionComplete(FName SessionName, bool bSuccess)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
        if (Sessions.IsValid())
        {
            Sessions->ClearOnCreateSessionCompleteDelegate_Handle(CreateSessionCompleteDelegateHandle);
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Session %s created successfully!"), *SessionName.ToString());
                // 会话创建成功，游戏逻辑继续...
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Failed to create session %s."), *SessionName.ToString());
            }
        }
    }
}

void AMySteamGameMode::FindAndJoinSession()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
        if (Sessions.IsValid())
        {
            SessionSearch = MakeShareable(new FOnlineSessionSearch());
            SessionSearch->bIsLanQuery = false;
            SessionSearch->MaxSearchResults = 10;
            SessionSearch->QuerySettings.Set(SEARCH_PRESENCE, true, EOnlineComparisonOp::Equals);

            FindSessionsCompleteDelegateHandle = Sessions->AddOnFindSessionsCompleteDelegate_Handle(FindSessionsCompleteDelegate);
            Sessions->FindSessions(0, SessionSearch.ToSharedRef());
        }
    }
}

void AMySteamGameMode::OnFindSessionsComplete(bool bSuccess)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
        if (Sessions.IsValid())
        {
            Sessions->ClearOnFindSessionsCompleteDelegate_Handle(FindSessionsCompleteDelegateHandle);
            if (bSuccess && SessionSearch.IsValid() && SessionSearch->SearchResults.Num() > 0)
            {
                // 找到了会话，尝试加入第一个
                FOnlineSessionSearchResult& Result = SessionSearch->SearchResults[0];
                Sessions->JoinSession(0, NAME_GameSession, Result);
            }
        }
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下核心在线模块。这些是标准依赖，通常已包含在使用在线功能的项目中。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供所有在线子系统的抽象基类和接口。 |
| `OnlineSubsystemUtils` | 提供在线子系统的工具类和蓝图支持。 |

**特殊说明**：该插件的底层依赖于 **Steamworks SDK**。虽然不直接显示在 `.Build.cs` 的公共依赖中，但引擎构建系统会在启用此插件时自动链接对应的 Steamworks 库（`steam_api64.lib` 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-22 | `f6116b00` | Updating Steamworks to 1.64 + binaries, now with arm64 android support. | 升级Steamworks至1.64，新增arm64安卓支持 |
| 2026-03-25 | `a14ea175` | OpenXR SteamFrame and Android support improvements | 改进OpenXR SteamFrame和安卓平台支持 |
| 2026-02-04 | `e596cc7a` | Disable Steam on Android | 禁用安卓平台的Steam功能 |
| 2026-01-23 | `c73d4bf4` | PR #14263: Updating Steamworks to v1.63, which adds support for Android | 升级Steamworks至v1.63，初步添加安卓支持 |
| 2025-11-21 | `f97662ab` | Iris Parallelization - Added API for network HandlerComponents to indicate support for being run in parallel | 为网络Handler组件添加并行运行支持的API |

### 维护评价

**维护状态：活跃维护**

该插件自 2016 年创建以来一直是虚幻引擎 Steam 集成的官方解决方案。从近期的 git 历史看，维护状态非常积极：
1.  **持续更新**：最近半年有多次提交，主要聚焦于升级 Steamworks SDK 版本和改进跨平台（特别是安卓）支持。
2.  **功能演进**：添加了如 Iris 并行化支持等新特性，表明该插件仍在随引擎技术栈一同演进。
3.  **官方支持**：由 Epic Games 维护，是虚幻引擎 Steam 生态的基石。

**注意事项**：
-   该插件默认禁用（`EnabledByDefault: false`），需要在项目设置中手动启用。
-   实现完整的 Steam 微交易功能需要自行开发后端服务器与 Steam Web API 交互，插件本身只提供了客户端接口框架。
-   在非 Steam 平台（如主机、Epic Games Store）构建时，需要切换到对应的在线子系统或使用 `OnlineSubsystemNull`。

**推荐使用**：如果你的游戏面向 Steam 平台，并且需要多人在线功能，这是**必选且推荐**的插件。其稳定性和功能完整性经过多年验证，是行业标准。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemSteam)
-   [Steamworks SDK 官方文档](https://partner.steamgames.com/doc/sdk)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OnlineSubsystemSteam)