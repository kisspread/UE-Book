# Online Subsystem iOS

> Access to iOS platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（本地化资源） |
| 模块 | `OnlineSubsystemIOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/IOS/OnlineSubsystemIOS) | |

## 用途

OnlineSubsystemIOS 是 UE5 对 Apple Game Center 和 iOS StoreKit 的完整封装，为 iOS/tvOS 平台提供统一的在线服务接口。它将 Game Center 的身份认证、排行榜、成就、好友、回合制多人游戏，以及 StoreKit 的内购（IAP）和商店查询功能，全部桥接到 UE 的 `IOnlineSubsystem` 抽象层中。

该插件解决的核心问题是：让 UE 游戏无需直接调用 Apple 原生 API，就能使用 Game Center 和 App Store 的全部在线功能。代码中包含大量 Objective-C++ 和 Swift 混编逻辑（通过 `FAppleAsyncTask` 将 Apple 主线程回调安全地转发到游戏线程），以及 StoreKit 2 的 Swift 互操作层。

**关键特性：**
- **Game Center 集成**：身份认证（`GKLocalPlayer`）、排行榜（`GKLeaderboard`）、成就（`GKAchievement`）、好友列表、回合制多人游戏（`GKTurnBasedMatch`）
- **StoreKit 内购**：商品查询（StoreKit 1 `SKProductsRequest`）、购买流程（`SKPaymentQueue`）、收据验证、退款请求（StoreKit 2 Swift）
- **CloudKit 云存储**：用户云存档（`IOnlineUserCloud`）和共享云存档（`IOnlineSharedCloud`），同步策略可配置
- **MultipeerConnectivity**：iOS 平台的本地多人连接支持（仅 iOS，不含 tvOS）
- **MarketplaceKit**：iOS 16+ Alternative Marketplace 分发支持，非 App Store 渠道时自动禁用 IAP

## 使用场景

- 你在开发 iOS/tvOS 游戏，需要接入 Game Center 的排行榜和成就系统 → 启用此插件（默认已启用），配置 `bEnableGameCenterSupport=true`
- 你的 iOS 游戏需要内购功能（消耗品、非消耗品、订阅） → 在 `OnlineSubsystemIOS.Store` 配置段中设置 `bSupportsInAppPurchasing=true`
- 你需要实现 iOS 回合制多人游戏（如棋类、卡牌异步对战） → 使用 `IOnlineTurnBased` 接口
- 你的游戏需要跨设备云存档 → 启用 CloudKit 支持并配置 `IOSCloudKitSyncStrategy`
- 你使用 Alternative Marketplace（第三方应用商店）分发 iOS 应用 → 插件会自动检测 `MarketplaceType`，非 App Store 时禁用 StoreKit IAP

## 蓝图用法

此插件主要通过 C++ 接口使用，不直接暴露蓝图节点。Game Center 和 StoreKit 的功能通过 UE 的 Online Subsystem 抽象层间接访问，蓝图中可使用 `OnlineSubsystemUtils` 提供的通用在线服务节点。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemIOS.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineStoreInterfaceV2.h"
#include "Interfaces/OnlinePurchaseInterface.h"
#include "Interfaces/OnlineAchievementsInterface.h"
#include "Interfaces/OnlineLeaderboardInterface.h"
```

### 获取 Online Subsystem 实例

```cpp
// 获取 IOS Online Subsystem（IOS_SUBSYSTEM 宏展开为 "IOS"）
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(IOS_SUBSYSTEM);
if (OnlineSub)
{
    // 获取各接口
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    IOnlineStoreV2Ptr Store = OnlineSub->GetStoreV2Interface();
    IOnlinePurchasePtr Purchase = OnlineSub->GetPurchaseInterface();
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    IOnlineLeaderboardsPtr Leaderboards = OnlineSub->GetLeaderboardsInterface();
}
```

### 身份认证（Game Center 登录）

Game Center 的认证流程在首次调用 `Login` 时设置 `authenticateHandler`，后续状态变化通过该 handler 自动通知。

```cpp
IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();

// 绑定登录完成回调
Identity->AddOnLoginCompleteDelegate_Handle(0,
    FOnLoginCompleteDelegate::CreateLambda([](int32 LocalUserNum, bool bWasSuccessful,
        const FUniqueNetId& UserId, const FString& Error)
    {
        if (bWasSuccessful)
        {
            UE_LOG(LogTemp, Log, TEXT("Game Center login succeeded: %s"), *UserId.ToString());
        }
    }));

// 触发登录（仅支持 LocalUserNum=0）
Identity->Login(0, FOnlineAccountCredentials());
```

**注意事项：**
- 仅支持单个本地玩家（`LocalUserNum` 必须为 0）
- 无法从应用内登出 Game Center，`Logout()` 始终返回 `false`
- 用户可在 iOS 设置中切换 Game Center 账号，切换事件通过 `OnLoginStatusChangedDelegates` 通知
- 如果收到 `"UnknownID"`，表示 Game Center 尚未提供有效 ID，需等待后续事件

### 内购流程

```cpp
// 1. 查询商品信息
IOnlineStoreV2Ptr Store = OnlineSub->GetStoreV2Interface();
TArray<FUniqueOfferId> OfferIds;
OfferIds.Add(TEXT("com.mygame.coins_100"));

Store->QueryOffersById(*LocalUserId, OfferIds,
    FOnQueryOnlineStoreOffersComplete::CreateLambda(
        [](bool bSuccess, const TArray<FUniqueOfferId>& OfferIds, const FString& Error)
        {
            if (bSuccess)
            {
                UE_LOG(LogTemp, Log, TEXT("Store offers queried successfully"));
            }
        }));

// 2. 发起购买
IOnlinePurchasePtr Purchase = OnlineSub->GetPurchaseInterface();
FPurchaseCheckoutRequest CheckoutRequest;
CheckoutRequest.PurchaseOffers.Add(
    FPurchaseCheckoutRequest::FPurchaseOfferEntry(
        TEXT("com.mygame.coins_100"), 1));

Purchase->Checkout(*LocalUserId, CheckoutRequest,
    FOnPurchaseCheckoutComplete::CreateLambda(
        [](const FOnlineError& Result, const TSharedRef<FPurchaseReceipt>& Receipt)
        {
            if (Result.bSucceeded)
            {
                UE_LOG(LogTemp, Log, TEXT("Purchase succeeded: %s"), *Receipt->TransactionId);
                // 验证收据后调用 FinalizePurchase 完成交易
            }
        }));

// 3. 完成交易（验证收据后）
Purchase->FinalizePurchase(*LocalUserId, Receipt->TransactionId);
```

**配置要求：**
```ini
[OnlineSubsystemIOS.Store]
bSupportsInAppPurchasing=true
; 可选：禁止某些地区的内购
; BannedLocales=CN,KR
```

### 成就系统

```cpp
IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();

// 查询成就
Achievements->QueryAchievements(*LocalUserId,
    FOnQueryAchievementsCompleteDelegate::CreateLambda(
        [](const FUniqueNetId& PlayerId, bool bSuccess)
        {
            UE_LOG(LogTemp, Log, TEXT("Achievements query: %s"), bSuccess ? TEXT("OK") : TEXT("Failed"));
        }));

// 解锁/更新成就进度
FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
WriteObject->SetIntStat(TEXT("achievement_id"), 100);  // 100% 进度
Achievements->WriteAchievements(*LocalUserId, WriteObject,
    FOnAchievementsWrittenDelegate::CreateLambda(
        [](const FUniqueNetId& PlayerId, bool bSuccess) {}));
```

### 排行榜

```cpp
IOnlineLeaderboardsPtr Leaderboards = OnlineSub->GetLeaderboardsInterface();

// 写入分数
FOnlineLeaderboardWrite WriteObject;
WriteObject.SetIntStat(TEXT("HighScore"), 12500);
WriteObject.LeaderboardNames.Add(TEXT("HighScore"));

Leaderboards->WriteLeaderboards(NAME_None, *LocalUserId, WriteObject);
Leaderboards->FlushLeaderboards(NAME_None);

// 读取好友排行榜
FOnlineLeaderboardReadRef ReadObject = MakeShared<FOnlineLeaderboardRead>();
Leaderboards->ReadLeaderboardsForFriends(0, ReadObject);
```

### 回合制多人游戏

```cpp
IOnlineTurnBasedPtr TurnBased = OnlineSub->GetTurnBasedInterface();

// 显示匹配 UI
FTurnBasedMatchRequest MatchRequest;
MatchRequest.MinPlayers = 2;
MatchRequest.MaxPlayers = 4;
TurnBased->ShowMatchmaker(MatchRequest);

// 加载所有进行中的比赛
TurnBased->LoadAllMatches(
    FLoadTurnBasedMatchesSignature::CreateLambda(
        [](const TArray<FString>& MatchIDs, bool bSuccess)
        {
            for (const FString& ID : MatchIDs)
            {
                UE_LOG(LogTemp, Log, TEXT("Active match: %s"), *ID);
            }
        }));

// 结束回合
FTurnBasedMatchPtr Match = TurnBased->GetMatchWithID(MatchID);
TArray<uint8> MatchData;
// ... 填充比赛数据 ...
Match->EndTurnWithMatchData(MatchData, 60,
    FUploadMatchDataSignature::CreateLambda(
        [](const FString& MatchID, bool bSuccess) {}));
```

## Demo 示例

一个最小的 iOS 内购示例，展示查询商品和购买流程：

```cpp
// MyIAPManager.h
#pragma once
#include "CoreMinimal.h"
#include "Interfaces/OnlineStoreInterfaceV2.h"
#include "Interfaces/OnlinePurchaseInterface.h"

class FMyIAPManager
{
public:
    void Initialize();
    void QueryProducts(const TArray<FString>& ProductIds);
    void BuyProduct(const FString& ProductId);

private:
    void OnQueryComplete(bool bSuccess, const TArray<FUniqueOfferId>& OfferIds, const FString& Error);
    void OnPurchaseComplete(const FOnlineError& Result, const TSharedRef<FPurchaseReceipt>& Receipt);

    TSharedPtr<const FUniqueNetId> LocalUserId;
};

// MyIAPManager.cpp
#include "MyIAPManager.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemIOS.h"

void FMyIAPManager::Initialize()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(IOS_SUBSYSTEM);
    check(OnlineSub);

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    LocalUserId = Identity->GetUniquePlayerId(0);
}

void FMyIAPManager::QueryProducts(const TArray<FString>& ProductIds)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(IOS_SUBSYSTEM);
    IOnlineStoreV2Ptr Store = OnlineSub->GetStoreV2Interface();

    TArray<FUniqueOfferId> OfferIds;
    for (const FString& Id : ProductIds)
    {
        OfferIds.Add(Id);
    }

    Store->QueryOffersById(*LocalUserId, OfferIds,
        FOnQueryOnlineStoreOffersComplete::CreateSP(this, &FMyIAPManager::OnQueryComplete));
}

void FMyIAPManager::BuyProduct(const FString& ProductId)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(IOS_SUBSYSTEM);
    IOnlinePurchasePtr Purchase = OnlineSub->GetPurchaseInterface();

    FPurchaseCheckoutRequest Request;
    Request.PurchaseOffers.Add(
        FPurchaseCheckoutRequest::FPurchaseOfferEntry(ProductId, 1));

    Purchase->Checkout(*LocalUserId, Request,
        FOnPurchaseCheckoutComplete::CreateSP(this, &FMyIAPManager::OnPurchaseComplete));
}
```

**Build.cs 依赖：**
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "OnlineSubsystem",
    "OnlineSubsystemIOS"
});
```

## 模块依赖

从 `OnlineSubsystemIOS.Build.cs` 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心 |
| `HTTP` | HTTP 请求（用于 App Store 验证） |
| `IOSPlatformFeatures` | iOS 平台特性接口 |
| `OnlineSubsystem` | Online Subsystem 基础框架 |
| `Sockets` | 网络 Socket 支持 |
| `MarketplaceKit` | iOS 16+ Alternative Marketplace 支持（仅 iOS，非 tvOS） |

**系统框架依赖：**
- `CloudKit`（弱链接）— 云存储功能
- `MultipeerConnectivity`（弱链接，仅 iOS）— 本地多人连接
- `GameKit` — Game Center 核心框架
- `StoreKit` — 应用内购买框架

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `d2ec2238` | Generalized IOSAsyncTask to AppleAsyncTask | 将 `IOSAsyncTask` 重命名为 `AppleAsyncTask`，为 macOS WebBrowser 插件复用做准备，旧名称保留为废弃警告 |
| 2025-05-27 | `3f7a168b` | Multiple swift file support | 构建系统改进：支持模块内多个 Swift 文件协同编译，自动生成统一的桥接头文件 |
| 2025-05-12 | `f3fea324` | Handle race condition when purchasing same offer after finalizing | 修复了完成购买后立即购买同一商品时的竞态条件，引入延迟购买机制 |

### 维护评价

- **活跃维护**：最近 6 个月内有功能性更新和 bug 修复
- **创建时间**：2016 年，已有约 10 年历史，但持续更新
- **更新频率**：近期保持稳定更新，最近 3 次 commit 涵盖了重构、构建系统改进和 bug 修复
- **平台支持**：iOS + tvOS（从代码看也包含 VisionOS 的条件编译）
- **Swift 集成**：包含 StoreKit 2 的 Swift 互操作层，表明正在向现代 Apple API 迁移
- **已知限制**：
  - 仅支持单个本地玩家
  - `Logout()` 不可用（Apple 限制）
  - 排行榜不支持 `ReadLeaderboardsAroundRank` / `ReadLeaderboardsAroundUser`
  - 排行榜仅支持 `Int32` 数据类型
  - StoreKit 不支持单次交易购买多个不同商品
- **推荐使用**：✅ iOS/tvOS 项目必备，默认启用，稳定可靠

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/IOS/OnlineSubsystemIOS)
- [Apple Game Center 文档](https://developer.apple.com/game-center/)
- [Apple StoreKit 文档](https://developer.apple.com/storekit/)
