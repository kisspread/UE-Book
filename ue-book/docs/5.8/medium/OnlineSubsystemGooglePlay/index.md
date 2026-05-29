# Online Subsystem GooglePlay

> Access to GooglePlay platform

| 属性 | 值 |
|---|---|
| 中文名 | 谷歌商店在线服务 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemGooglePlay` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Android/OnlineSubsystemGooglePlay) | |

## 用途

本插件为 Android 平台提供 Google Play Games Services 的完整集成，是 UE5 在线子系统（Online Subsystem）架构的一部分。它封装了 Google Play Games 的登录认证、应用内购买（IAP）、排行榜、成就系统和外部 UI 等功能，使得开发者可以通过统一的 `IOnlineSubsystem` 接口访问 Google Play 服务，而无需直接编写 Java/JNI 代码。

插件内部通过 JNI 桥接（`GooglePlayGamesWrapper` 和 `GooglePlayStoreHelper`）与 Java 层的 `GooglePlayGamesWrapper` 和 `GooglePlayStoreHelper` 通信，将所有 Google Play API 调用异步化，避免阻塞游戏线程。

**支持的接口：**
- **Identity** — Google Play Games 登录/认证
- **StoreV2** — 商品目录查询
- **Purchase** — 应用内购买（包括订阅和替代计费）
- **Achievements** — 成就解锁与进度
- **Leaderboards** — 排行榜读写
- **ExternalUI** — Google Play 内置 UI（成就页、排行榜页等）

**不支持的接口（返回 nullptr）：**
Session、Friends、Party、Groups、Voice、Stats、Presence、Chat、Events、Message、Sharing、TurnBased、Tournament

## 使用场景

- 你在开发 Android 游戏并需要集成 Google Play Games 登录 → 用此插件的 Identity 接口
- 你需要实现内购（一次性购买或订阅）并支持 Google Play Billing → 用此插件的 Purchase 接口
- 你需要排行榜和成就系统但不想自己实现后端 → 用此插件的 Leaderboards/Achievements 接口
- 你需要支持 Google Play 的替代计费（Alternative Billing）→ 用 Purchase 接口中的 `ShowAlternativeBillingInformationDialog`

## 蓝图用法

本插件不直接暴露 BlueprintCallable 节点。所有功能通过 UE5 通用的 Online Subsystem 蓝图接口访问（如 `GetSubsystem` + `IOnlineSubsystem` 接口），或通过 `OnlineSubsystemUtils` 提供的异步蓝图代理节点使用。

### 使用示例（蓝图描述）

由于本插件没有直接的蓝图节点，以下描述通过通用 OSS 蓝图方式访问：

**Google Play 登录：**
1. 获取 `OnlineSubsystem` → `GetIdentityInterface` → 调用 `AutoLogin(0)`
2. 绑定 `OnLoginComplete` 委托获取登录结果

**购买商品：**
1. 获取 `OnlineSubsystem` → `GetPurchaseInterface` → 调用 `Checkout`
2. 传入 `FPurchaseCheckoutRequest`，绑定 `OnPurchaseCheckoutComplete` 委托

**写入成就：**
1. 获取 `OnlineSubsystem` → `GetAchievementsInterface` → 调用 `WriteAchievements`
2. 绑定 `OnAchievementsWritten` 委托

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemGooglePlay.h"
```

通常不需要直接包含此头文件。通过通用接口使用：

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlinePurchaseInterface.h"
#include "Interfaces/OnlineLeaderboardInterface.h"
#include "Interfaces/OnlineAchievementsInterface.h"
```

### 基本用法

通过通用 Online Subsystem 接口获取 Google Play 子系统，无需直接引用 GooglePlay 专有类型。

**登录 Google Play Games：**

```cpp
// 来源: 概念源自 Source/Private/OnlineIdentityInterfaceGooglePlay.h
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
if (OSS)
{
    IOnlineIdentityPtr Identity = OSS->GetIdentityInterface();
    if (Identity.IsValid())
    {
        Identity->OnLoginCompleteDelegates->AddUObject(
            this, &UMyClass::OnLoginComplete);
        Identity->AutoLogin(0);
    }
}
```

**查询排行榜：**

```cpp
// 来源: 概念源自 Source/Private/OnlineLeaderboardInterfaceGooglePlay.h
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
IOnlineLeaderboardsPtr Leaderboards = OSS->GetLeaderboardsInterface();

FOnlineLeaderboardReadRef ReadObject = MakeShared<FOnlineLeaderboardRead>();
ReadObject->LeaderboardName = TEXT("MyLeaderboard");

Leaderboards->OnLeaderboardReadCompleteDelegates.AddUObject(
    this, &UMyClass::OnLeaderboardReadComplete);
Leaderboards->ReadLeaderboards({LocalPlayerId}, ReadObject);
```

**写入成就进度：**

```cpp
// 来源: 概念源自 Source/Private/OnlineAchievementsInterfaceGooglePlay.h
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
IOnlineAchievementsPtr Achievements = OSS->GetAchievementsInterface();

FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
WriteObject->SetIntStat(TEXT("achievement_id"), 100);

Achievements->WriteAchievements(*LocalPlayerId, WriteObject);
```

### 进阶用法

**查询并购买商品：**

```cpp
// 来源: 概念源自 Source/Public/OnlineStoreGooglePlay.h 和 OnlinePurchaseGooglePlay.h
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
IOnlineStoreV2Ptr Store = OSS->GetStoreV2Interface();
IOnlinePurchasePtr Purchase = OSS->GetPurchaseInterface();

// 1. 查询商品
Store->QueryOffersById(*LocalPlayerId, {TEXT("product_sku_1")},
    FOnQueryOnlineStoreOffersComplete::CreateLambda(
        [this, Purchase, LocalPlayerId](bool bSuccess, const TArray<FUniqueOfferId>& OfferIds, const FString& Error)
        {
            if (bSuccess)
            {
                // 2. 发起购买
                FPurchaseCheckoutRequest CheckoutRequest;
                CheckoutRequest.AddPurchaseOffer(TEXT(""), TEXT("product_sku_1"), 1);
                
                Purchase->Checkout(*LocalPlayerId, CheckoutRequest,
                    FOnPurchaseCheckoutComplete::CreateLambda(
                        [](const FOnlineError& Result, const TSharedRef<FPurchaseReceipt>& Receipt)
                        {
                            // 处理购买结果
                        }));
            }
        }));
```

**使用 Google Play 专有类型避免转换：**

```cpp
// 来源: Source/Public/OnlineSubsystemGooglePlay.h
IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
FOnlineSubsystemGooglePlay* GooglePlayOSS = 
    static_cast<FOnlineSubsystemGooglePlay*>(OSS);

// 直接获取 Google Play 专有接口，避免不必要的类型转换
FOnlineIdentityGooglePlayPtr Identity = GooglePlayOSS->GetIdentityGooglePlay();
FOnlineLeaderboardsGooglePlayPtr Leaderboards = GooglePlayOSS->GetLeaderboardsGooglePlay();
FOnlineAchievementsGooglePlayPtr Achievements = GooglePlayOSS->GetAchievementsGooglePlay();

// 检查 IAP 是否可用
bool bIAPEnabled = GooglePlayOSS->IsInAppPurchasingEnabled();
```

**处理 Google Play 购买收据验证数据：**

```cpp
// 来源: Source/Public/OnlinePurchaseGooglePlay.h
// FGoogleTransactionData 提供了收据验证所需的所有数据
const FGoogleTransactionData& TransactionData = /* 从回调中获取 */;
FString ReceiptData = TransactionData.GetReceiptData();      // Google 收据数据
FString Signature = TransactionData.GetSignature();           // 签名用于服务器验证
FString Token = TransactionData.GetTransactionIdentifier();   // PurchaseToken
TArray<FString> OfferIds = TransactionData.GetOfferIds();     // 商品 ID 列表
bool bIsSubscription = TransactionData.IsSubscriptionProductId(OfferIds[0]);
```

## Demo 示例

```cpp
// MyGooglePlayManager.h
#pragma once

#include "CoreMinimal.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineLeaderboardInterface.h"
#include "Interfaces/OnlineAchievementsInterface.h"

class FMyGooglePlayManager
{
public:
    void Login();
    void ReadLeaderboard(const FString& LeaderboardName);
    void UnlockAchievement(const FString& AchievementId);

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
        const FUniqueNetId& UserId, const FString& Error);
    void OnLeaderboardReadComplete(bool bWasSuccessful);
    void OnAchievementsWritten(const FUniqueNetId& PlayerId, bool bWasSuccessful);

    FOnlineLeaderboardReadPtr CachedReadObject;
};
```

```cpp
// MyGooglePlayManager.cpp
#include "MyGooglePlayManager.h"

void FMyGooglePlayManager::Login()
{
    IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
    if (!OSS) return;

    IOnlineIdentityPtr Identity = OSS->GetIdentityInterface();
    if (Identity.IsValid())
    {
        Identity->AddOnLoginCompleteDelegate_Handle(0,
            FOnLoginCompleteDelegate::CreateRaw(this, &FMyGooglePlayManager::OnLoginComplete));
        Identity->AutoLogin(0);
    }
}

void FMyGooglePlayManager::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful,
    const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Google Play 登录成功: %s"), *UserId.ToString());
    }
}

void FMyGooglePlayManager::ReadLeaderboard(const FString& LeaderboardName)
{
    IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
    if (!OSS) return;

    IOnlineLeaderboardsPtr Leaderboards = OSS->GetLeaderboardsInterface();
    if (!Leaderboards.IsValid()) return;

    CachedReadObject = MakeShared<FOnlineLeaderboardRead>();
    CachedReadObject->LeaderboardName = FName(*LeaderboardName);

    Leaderboards->AddOnLeaderboardReadCompleteDelegate_Handle(
        FOnLeaderboardReadCompleteDelegate::CreateRaw(
            this, &FMyGooglePlayManager::OnLeaderboardReadComplete));

    FUniqueNetIdPtr PlayerId = OSS->GetIdentityInterface()->GetUniquePlayerId(0);
    Leaderboards->ReadLeaderboards({PlayerId.ToSharedRef()}, CachedReadObject.ToSharedRef());
}

void FMyGooglePlayManager::OnLeaderboardReadComplete(bool bWasSuccessful)
{
    if (bWasSuccessful && CachedReadObject.IsValid())
    {
        for (const FOnlineStatsRow& Row : CachedReadObject->Rows)
        {
            UE_LOG(LogTemp, Log, TEXT("排行榜: %s 分数=%s"),
                *Row.NickName, *Row.Columns[TEXT("score")].ToString());
        }
    }
}

void FMyGooglePlayManager::UnlockAchievement(const FString& AchievementId)
{
    IOnlineSubsystem* OSS = IOnlineSubsystem::Get();
    if (!OSS) return;

    IOnlineAchievementsPtr Achievements = OSS->GetAchievementsInterface();
    if (!Achievements.IsValid()) return;

    FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
    WriteObject->SetIntStat(FName(*AchievementId), 100);

    FUniqueNetIdPtr PlayerId = OSS->GetIdentityInterface()->GetUniquePlayerId(0);
    Achievements->WriteAchievements(*PlayerId, WriteObject,
        FOnAchievementsWrittenDelegate::CreateRaw(
            this, &FMyGooglePlayManager::OnAchievementsWritten));
}

void FMyGooglePlayManager::OnAchievementsWritten(const FUniqueNetId& PlayerId, bool bWasSuccessful)
{
    UE_LOG(LogTemp, Log, TEXT("成就写入: %s"),
        bWasSuccessful ? TEXT("成功") : TEXT("失败"));
}
```

## 模块依赖

本插件无特殊依赖（仅标准 Core/Engine/Slate 等），以及以下 Online Subsystem 相关模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统基础框架和接口定义 |
| `OnlineSubsystemUtils` | 在线子系统蓝图工具和异步代理 |

插件声明的插件依赖（.uplugin Plugins 字段）：

| 插件 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供 `IOnlineSubsystem` 及所有子接口定义 |
| `AndroidPermission` | Android 运行时权限管理 |

**平台限制**：本插件仅在 Android 平台可用（`SupportedTargetPlatforms: ["Android"]`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `a5fdbc04` | FORT-1067735 [Client] Support Google Play discounted offer | 支持 Google Play 折扣优惠商品 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复作用域枚举在格式化函数中导致输出乱码的问题 |
| 2026-04-02 | `2449363d` | FIx LexToString for EOnlineKeyValuePairDataType. This was probably silently converting to bool befo | 修复 LexToString 类型转换可能静默转为 bool 的 bug |
| 2026-01-28 | `0020b7a0` | Update Google Play Store Online Subsystem to support current requirements for alternative billing | 更新以支持 Google Play 替代计费的最新要求 |
| 2026-01-26 | `fe81366e` | Change Google Play Billing errors to display additional debug info, get rid of delay for BILLING_UNA | 增强计费错误的调试信息显示 |

### 维护评价

- **活跃维护中**：最近 6 个月内有多次实质性更新，包括新功能（折扣优惠、替代计费）和 bug 修复
- Google Play Billing API 变化频繁，Epic 持续跟进 Google 的政策要求
- 作为 Android 上 Google Play 分发的必备组件，预计会长期维护
- 当前版本（5.8）仍有活跃的开发投入

**推荐使用**：✅ 推荐。这是 Android 平台上使用 Google Play Games Services 和应用内购买的标准方案，由 Epic 官方维护，且近期仍有功能性更新。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Android/OnlineSubsystemGooglePlay)