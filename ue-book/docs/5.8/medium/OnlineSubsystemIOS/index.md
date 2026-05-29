# Online Subsystem iOS

> Access to iOS platform

| 属性 | 值 |
|---|---|
| 中文名 | iOS 在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemIOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/IOS/OnlineSubsystemIOS) | |

## 用途

OnlineSubsystemIOS 是 UE5 在线子系统框架的 iOS 平台实现，封装了 Apple GameKit / StoreKit / CloudKit 等原生 SDK，为 UE 项目提供统一的在线服务接口。它解决的核心问题是：**让 iOS 游戏能够使用 Apple 生态的社交、多人、成就、排行榜、内购和云存储服务，而无需直接编写 Objective-C 代码**。

该插件通过实现 `IOnlineSubsystem` 接口，将 Apple Game Center（身份认证、好友、排行榜、成就、回合制多人）、StoreKit（应用内购买、商店查询）、CloudKit（用户/共享云存储）和 MarketplaceKit 等平台服务桥接到 UE 的在线子系统抽象层。

## 使用场景

- 你的 iOS 游戏需要 Game Center 登录身份验证 → 使用 Identity 接口
- 你需要实现 iOS 应用内购买（IAP）→ 使用 StoreV2 / Purchase 接口
- 你想在 iOS 上显示 Game Center 好友列表、排行榜、成就 UI → 使用 ExternalUI 接口
- 你的游戏需要基于 iCloud 的云存档同步 → 使用 UserCloud / SharedCloud 接口
- 你想实现 Game Center 回合制多人对战 → 使用 TurnBased 接口
- 你需要查找、创建、加入 Game Center 多人游戏会话 → 使用 Session 接口

## 蓝图用法

该插件不直接暴露 `BlueprintCallable` 节点。所有功能均通过 UE 的在线子系统抽象层访问，在蓝图中使用 **Online Subsystem** 相关的通用蓝图节点（如 `Get Game Instance → Get Online Subsystem → 获取具体接口`）即可。Game Center 的 UI 功能通过 `ShowExternalUI` 类节点触发。

### 核心功能接口

| 功能 | 接口类型 | 获取方式 |
|---|---|---|
| 身份认证 / Game Center 登录 | `IOnlineIdentity` | `GetIdentityInterface()` |
| 好友列表 | `IOnlineFriends` | `GetFriendsInterface()` |
| 排行榜 | `IOnlineLeaderboards` | `GetLeaderboardsInterface()` |
| 成就 | `IOnlineAchievements` | `GetAchievementsInterface()` |
| 回合制多人 | `IOnlineTurnBased` | `GetTurnBasedInterface()` |
| 会话管理 | `IOnlineSession` | `GetSessionInterface()` |
| 应用内购买 | `IOnlinePurchase` | `GetPurchaseInterface()` |
| 商店查询 | `IOnlineStoreV2` | `GetStoreV2Interface()` |
| 用户云存储 | `IOnlineUserCloud` | `GetUserCloudInterface()` |
| 共享云存储 | `IOnlineSharedCloud` | `GetSharedCloudInterface()` |
| 外部 UI | `IOnlineExternalUI` | `GetExternalUIInterface()` |

### 使用示例（蓝图描述）

1. **Game Center 登录**：使用通用的 `Login` 节点，`FOnlineSubsystemIOS` 会自动调用 Game Center 认证流程
2. **显示成就 UI**：通过 `ShowAchievementsUI` 节点弹出 Game Center 成就页面
3. **应用内购买**：先通过 `QueryOffersById` 查询商品信息，再通过 `Checkout` 发起购买

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemIOS.h"
#include "OnlineSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineSessionInterface.h"
#include "Interfaces/OnlineLeaderboardsInterface.h"
```

### 基本用法：获取在线子系统并使用身份接口

```cpp
// 获取 iOS 在线子系统
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM); // 通常自动解析为 IOS_SUBSYSTEM
if (!OnlineSub)
{
    OnlineSub = IOnlineSubsystem::Get();
}

// 获取身份接口
IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
if (IdentityInterface.IsValid())
{
    // 获取本地玩家唯一 ID
    FUniqueNetIdPtr UserId = IdentityInterface->GetUniquePlayerId(0);
    
    // 获取登录状态
    ELoginStatus::Type LoginStatus = IdentityInterface->GetLoginStatus(0);
    
    // 获取玩家昵称（Game Center 显示名）
    FString PlayerName = IdentityInterface->GetPlayerNickname(0);
}
```

*来源：`OnlineIdentityInterfaceIOS.h` 中 `FOnlineIdentityIOS` 的接口定义*

### 进阶用法：应用内购买流程

```cpp
// 获取购买和商店接口
IOnlineStoreV2Ptr StoreInterface = OnlineSub->GetStoreV2Interface();
IOnlinePurchasePtr PurchaseInterface = OnlineSub->GetPurchaseInterface();

if (StoreInterface.IsValid() && PurchaseInterface.IsValid())
{
    FUniqueNetIdPtr UserId = OnlineSub->GetIdentityInterface()->GetUniquePlayerId(0);
    
    // 查询商品信息
    TArray<FUniqueOfferId> OfferIds;
    OfferIds.Add(TEXT("com.myapp.product1"));
    
    StoreInterface->QueryOffersById(
        *UserId,
        OfferIds,
        FOnQueryOnlineStoreOffersComplete::CreateLambda(
            [](bool bSuccess, const TArray<FUniqueOfferId>& OfferIds, const FString& Error)
            {
                if (bSuccess)
                {
                    UE_LOG(LogTemp, Log, TEXT("Store offers queried successfully"));
                }
            })
    );
    
    // 发起购买
    FPurchaseCheckoutRequest CheckoutRequest;
    CheckoutRequest.AddPurchaseOffer(TEXT(""), TEXT("com.myapp.product1"), 1);
    
    PurchaseInterface->Checkout(
        *UserId,
        CheckoutRequest,
        FOnPurchaseCheckoutComplete::CreateLambda(
            [](const FOnlineError& Result, const TSharedRef<FPurchaseReceipt>& Receipt)
            {
                if (Result.WasSuccessful())
                {
                    UE_LOG(LogTemp, Log, TEXT("Purchase successful, receipt: %s"), *Receipt->TransactionId);
                }
            })
    );
}
```

*来源：`OnlinePurchaseIOS.h` 和 `OnlineStoreIOS.h` 中的接口定义*

### 进阶用法：iCloud 云存储

```cpp
// 获取用户云存储接口
IOnlineUserCloudPtr UserCloudInterface = OnlineSub->GetUserCloudInterface();
if (UserCloudInterface.IsValid())
{
    FUniqueNetIdPtr UserId = OnlineSub->GetIdentityInterface()->GetUniquePlayerId(0);
    
    // 枚举云端文件
    UserCloudInterface->EnumerateUserFiles(*UserId);
    
    // 读取文件
    UserCloudInterface->ReadUserFile(*UserId, TEXT("SaveGame.dat"));
    
    // 写入文件
    TArray<uint8> FileContents;
    // ... 填充数据 ...
    UserCloudInterface->WriteUserFile(*UserId, TEXT("SaveGame.dat"), FileContents);
}
```

*来源：`OnlineUserCloudInterfaceIOS.h` 中 `FOnlineUserCloudInterfaceIOS` 的接口定义*

## Demo 示例

```cpp
// MyIOSOnlineManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineLeaderboardsInterface.h"
#include "MyIOSOnlineManager.generated.h"

UCLASS()
class UMyIOSOnlineManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 刷新 Game Center 排行榜 */
    void RefreshLeaderboard(const FString& BoardName);

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnLeaderboardReadComplete(bool bWasSuccessful, const FUniqueNetId& PlayerId, const FString& LeaderboardName);

    FOnlineLeaderboardReadPtr CachedLeaderboardRead;
};
```

```cpp
// MyIOSOnlineManager.cpp
#include "MyIOSOnlineManager.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemSettings.h"

void UMyIOSOnlineManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;

    // 绑定登录完成回调
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (Identity.IsValid())
    {
        Identity->AddOnLoginCompleteDelegate_Handle(
            0, FOnLoginCompleteDelegate::CreateUObject(this, &UMyIOSOnlineManager::OnLoginComplete));
    }
}

void UMyIOSOnlineManager::Deinitialize()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (Identity.IsValid())
        {
            Identity->ClearOnLoginCompleteDelegates(0);
        }
    }
    Super::Deinitialize();
}

void UMyIOSOnlineManager::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
    const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Game Center login succeeded: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Game Center login failed: %s"), *Error);
    }
}

void UMyIOSOnlineManager::RefreshLeaderboard(const FString& BoardName)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    IOnlineLeaderboardsPtr Leaderboards = OnlineSub->GetLeaderboardsInterface();
    if (!Identity.IsValid() || !Leaderboards.IsValid()) return;

    CachedLeaderboardRead = MakeShared<FOnlineLeaderboardRead>();
    CachedLeaderboardRead->LeaderboardName = FName(*BoardName);

    TArray<FUniqueNetIdRef> Players;
    FUniqueNetIdPtr LocalId = Identity->GetUniquePlayerId(0);
    if (LocalId.IsValid())
    {
        Players.Add(LocalId.ToSharedRef());
    }

    Leaderboards->ReadLeaderboards(Players, CachedLeaderboardRead);
}

void UMyIOSOnlineManager::OnLeaderboardReadComplete(bool bWasSuccessful,
    const FUniqueNetId& PlayerId, const FString& LeaderboardName)
{
    if (bWasSuccessful && CachedLeaderboardRead.IsValid())
    {
        for (const FOnlineStatsRow& Row : CachedLeaderboardRead->Rows)
        {
            UE_LOG(LogTemp, Log, TEXT("Rank %d: %s"), Row.Rank, *Row.NickName);
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `MarketplaceKit` | Apple MarketplaceKit 框架集成，用于 iOS 应用商店相关功能 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的警告 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到新的 UE_LOGF 宏 |
| 2026-04-10 | `d6ab8d7c` | [iOS CTC Reporting]: | 新增 iOS 商业合规报告功能 |
| 2026-04-08 | `8baf75b6` | Switch to using an embedded weak framework for the MarketplaceKit swift lib to allow supporting APIs | 改用嵌入式弱链接 MarketKit Swift 库以支持更多 API |
| 2026-03-11 | `967d8c69` | [iOS CT Token]: | 新增 iOS 商业合规令牌功能 |

### 维护评价

OnlineSubsystemIOS 是一个**长期活跃维护**的核心平台插件。自 2016 年创建以来，随着每次 iOS 系统和 GameKit API 的更新持续获得维护。最近几个月的更新集中在 Apple 商业合规（Commerce Token）相关的新平台要求上，说明 Epic 正在积极跟踪 Apple 的政策变化。

- **活跃维护**: 最近 6 个月内有多次功能性更新
- **核心依赖**: 作为 iOS 平台的默认在线子系统，任何使用 UE 在线服务的 iOS 项目都会依赖此插件
- **平台限制**: 仅在 iOS / tvOS 目标平台生效，其他平台会自动回退到其他子系统（如 Null）
- **推荐使用**: ✅ iOS 项目的在线功能首选，Epic 官方维护，无需额外配置

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/IOS/OnlineSubsystemIOS)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/IOS/OnlineSubsystemIOS/Tests)（如有）