# Online Subsystem GooglePlay

> Access to GooglePlay platform

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（本地化资源） |
| 模块 | `OnlineSubsystemGooglePlay` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/Android/OnlineSubsystemGooglePlay) | |

## 用途

OnlineSubsystemGooglePlay 是 UE5 对 Google Play Games Services 的平台集成插件，为 Android 平台上的游戏提供以下在线服务：

- **身份认证**：通过 Google Play Games 登录，获取玩家唯一 ID 和 Auth Token
- **成就系统**：查询、解锁、上报成就进度（支持标准和递增两种类型）
- **排行榜**：读取、写入和刷新排行榜分数
- **内购（IAP）**：基于 Google Play Billing Library 7.1.1 实现商品查询、购买、消费、收据验证等完整购买流程
- **外部 UI**：调用 Google Play Games 原生 UI（成就展示、排行榜展示等）

该插件通过 JNI（Java Native Interface）与 Java 层的 `GooglePlayGamesWrapper` 和 `GooglePlayStoreHelper` 交互，C++ 层实现 UE 的 `IOnlineSubsystem` 接口体系。

**注意**：此插件仅在 Android 平台可用，且依赖 AndroidRuntimeSettings 中的 `bEnableGooglePlaySupport` 开关。

## 使用场景

- 你的 Android 游戏需要集成 Google Play Games 的登录、成就和排行榜功能
- 你需要通过 Google Play Billing 处理应用内购买（一次性购买或订阅）
- 你想使用 Google Play Games 的原生 UI（如成就展示页面、排行榜页面）
- 你需要在玩家设备上验证购买收据并进行服务端验证

## 蓝图用法

本插件主要通过 Online Subsystem 的标准蓝图接口暴露功能，自身不额外提供 BlueprintCallable 节点。蓝图中的使用方式是通过 `Get Online Subsystem` 节点获取 `GooglePlay` 子系统，然后通过标准的 Online 接口节点（成就、排行榜、购买等）操作。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Subsystem` | 获取 GooglePlay 子系统实例 | Engine 蓝图库 |
| `Query Achievements` | 查询当前玩家的成就列表 | `IOnlineAchievements` |
| `Write Achievements` | 写入成就进度/解锁成就 | `IOnlineAchievements` |
| `Query Achievements Info` | 查询成就描述信息 | `IOnlineAchievements` |
| `Read Leaderboards` | 读取排行榜数据 | `IOnlineLeaderboards` |
| `Write Leaderboards` | 写入排行榜分数 | `IOnlineLeaderboards` |
| `Query Offers` | 查询可购买的商品信息 | `IOnlineStoreV2` |
| `Checkout` | 发起购买请求 | `IOnlinePurchase` |
| `Show External UI - Achievements` | 显示 Google Play 成就 UI | `IOnlineExternalUI` |
| `Show External UI - Leaderboard` | 显示 Google Play 排行榜 UI | `IOnlineExternalUI` |

### 使用示例（蓝图描述）

**查询并显示成就**：
1. 获取 `GooglePlay` 子系统 → 获取 Achievements 接口
2. 调用 `QueryAchievements`（传入玩家 ID）→ 绑定完成回调
3. 回调中调用 `GetCachedAchievements` 获取成就列表
4. 可选：调用 `Show External UI - Achievements` 显示原生成就页面

**发起购买**：
1. 获取 `GooglePlay` 子系统 → 获取 Store V2 接口
2. 调用 `QueryOffersById`（传入商品 ID 数组）→ 绑定完成回调
3. 回调中获取 `Purchase` 接口，调用 `Checkout` 发起购买
4. 监听购买完成回调，处理 `FinalizePurchase`

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemGooglePlay.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineAchievementsInterface.h"
#include "Interfaces/OnlineLeaderboardInterface.h"
#include "Interfaces/OnlineStoreInterfaceV2.h"
#include "Interfaces/OnlinePurchaseInterface.h"
```

### 基本用法

**获取子系统和接口**：

```cpp
// 获取 GooglePlay 在线子系统
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
if (OnlineSub)
{
    // 获取身份接口 — 用于登录和获取玩家信息
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    
    // 获取成就接口
    IOnlineAchievementsPtr AchievementsInterface = OnlineSub->GetAchievementsInterface();
    
    // 获取排行榜接口
    IOnlineLeaderboardsPtr LeaderboardsInterface = OnlineSub->GetLeaderboardsInterface();
    
    // 获取商店和购买接口（需要启用 IAP）
    IOnlineStoreV2Ptr StoreInterface = OnlineSub->GetStoreV2Interface();
    IOnlinePurchasePtr PurchaseInterface = OnlineSub->GetPurchaseInterface();
}
```

**查询成就**：

```cpp
IOnlineAchievementsPtr AchievementsInterface = OnlineSub->GetAchievementsInterface();

FOnQueryAchievementsCompleteDelegate QueryDelegate;
QueryDelegate.BindLambda([](const FUniqueNetId& PlayerId, bool bWasSuccessful)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogOnline, Log, TEXT("Achievements query succeeded"));
    }
});

AchievementsInterface->QueryAchievements(*PlayerId, QueryDelegate);
```

**解锁成就**：

```cpp
FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
WriteObject->SetIntStat(TEXT("Achievement_Id"), 100); // 100% progress

FOnAchievementsWrittenDelegate WriteDelegate;
WriteDelegate.BindLambda([](const FUniqueNetId& PlayerId, bool bWasSuccessful)
{
    UE_LOG(LogOnline, Log, TEXT("Achievement write: %s"), bWasSuccessful ? TEXT("Success") : TEXT("Failed"));
});

AchievementsInterface->WriteAchievements(*PlayerId, WriteObject, WriteDelegate);
```

### 进阶用法

**内购流程（查询商品 → 购买 → 确认）**：

```cpp
// 1. 查询商品信息
IOnlineStoreV2Ptr StoreInterface = OnlineSub->GetStoreV2Interface();
TArray<FUniqueOfferId> OfferIds;
OfferIds.Add(TEXT("com.example.gems_100"));

FOnQueryOnlineStoreOffersCompleteDelegate OffersDelegate;
OffersDelegate.BindLambda([OnlineSub](bool bSuccess, const TArray<FUniqueOfferId>& OfferIds, const FString& Error)
{
    if (bSuccess)
    {
        // 2. 发起购买
        IOnlinePurchasePtr PurchaseInterface = OnlineSub->GetPurchaseInterface();
        FUniqueNetIdRef PlayerId = ...; // 当前玩家 ID
        
        FPurchaseCheckoutRequest CheckoutRequest;
        CheckoutRequest.AddPurchaseOffer(TEXT(""), TEXT("com.example.gems_100"), 1);
        
        FOnPurchaseCheckoutCompleteDelegate PurchaseDelegate;
        PurchaseDelegate.BindLambda([](const FOnlineError& Result, const TSharedRef<FPurchaseReceipt>& Receipt)
        {
            if (Result.WasSuccessful())
            {
                // 3. 确认购买（消费物品）
                IOnlinePurchasePtr Purchase = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM)->GetPurchaseInterface();
                Purchase->FinalizePurchase(*PlayerId, Receipt->TransactionId);
            }
        });
        
        PurchaseInterface->Checkout(*PlayerId, CheckoutRequest, PurchaseDelegate);
    }
});

StoreInterface->QueryOffersById(*PlayerId, OfferIds, OffersDelegate);
```

## Demo 示例

### Build.cs 依赖

```csharp
using UnrealBuildTool;

public class MyGameModule : ModuleRules
{
    public MyGameModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "OnlineSubsystem",
            "OnlineSubsystemUtils"
        });
        
        // OnlineSubsystemGooglePlay 通过 OnlineSubsystem 的插件机制自动加载
        // 不需要直接在 Build.cs 中声明依赖
    }
}
```

### 最小示例（成就查询与解锁）

```cpp
// MyGooglePlayManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "OnlineSubsystem.h"
#include "Interfaces/OnlineIdentityInterface.h"
#include "Interfaces/OnlineAchievementsInterface.h"
#include "MyGooglePlayManager.generated.h"

UCLASS()
class UMyGooglePlayManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 初始化并自动登录 */
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    /** 查询所有成就 */
    UFUNCTION(BlueprintCallable, Category = "GooglePlay")
    void QueryAchievements();

    /** 解锁指定成就 */
    UFUNCTION(BlueprintCallable, Category = "GooglePlay")
    void UnlockAchievement(const FString& AchievementId);

private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    void OnQueryAchievementsComplete(const FUniqueNetId& PlayerId, bool bWasSuccessful);
    void OnAchievementsWritten(const FUniqueNetId& PlayerId, bool bWasSuccessful);
};
```

```cpp
// MyGooglePlayManager.cpp
#include "MyGooglePlayManager.h"
#include "OnlineSubsystemGooglePlay.h"

void UMyGooglePlayManager::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
    if (!OnlineSub)
    {
        UE_LOG(LogTemp, Warning, TEXT("GooglePlay OnlineSubsystem not available"));
        return;
    }

    // 绑定登录回调
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (Identity.IsValid())
    {
        FOnLoginCompleteDelegate LoginDelegate;
        LoginDelegate.AddUObject(this, &UMyGooglePlayManager::OnLoginComplete);
        Identity->AddOnLoginCompleteDelegate_Handle(0, LoginDelegate);
        
        // 自动登录
        Identity->AutoLogin(0);
    }
}

void UMyGooglePlayManager::Deinitialize()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
    if (OnlineSub)
    {
        IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
        if (Identity.IsValid())
        {
            Identity->Logout(0);
        }
    }
    Super::Deinitialize();
}

void UMyGooglePlayManager::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
    const FUniqueNetId& UserId, const FString& Error)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("GooglePlay login succeeded: %s"), *UserId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("GooglePlay login failed: %s"), *Error);
    }
}

void UMyGooglePlayManager::QueryAchievements()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    if (!Identity.IsValid() || !Achievements.IsValid()) return;

    FUniqueNetIdPtr PlayerId = Identity->GetUniquePlayerId(0);
    if (!PlayerId.IsValid()) return;

    FOnQueryAchievementsCompleteDelegate Delegate;
    Delegate.AddUObject(this, &UMyGooglePlayManager::OnQueryAchievementsComplete);
    Achievements->QueryAchievements(*PlayerId, Delegate);
}

void UMyGooglePlayManager::OnQueryAchievementsComplete(const FUniqueNetId& PlayerId, bool bWasSuccessful)
{
    if (!bWasSuccessful) return;

    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    
    TArray<FOnlineAchievement> OutAchievements;
    Achievements->GetCachedAchievements(PlayerId, OutAchievements);
    
    for (const FOnlineAchievement& Ach : OutAchievements)
    {
        UE_LOG(LogTemp, Log, TEXT("Achievement: %s - Progress: %f"), *Ach.Id, Ach.Progress);
    }
}

void UMyGooglePlayManager::UnlockAchievement(const FString& AchievementId)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get(GOOGLEPLAY_SUBSYSTEM);
    if (!OnlineSub) return;

    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    if (!Identity.IsValid() || !Achievements.IsValid()) return;

    FUniqueNetIdPtr PlayerId = Identity->GetUniquePlayerId(0);
    if (!PlayerId.IsValid()) return;

    FOnlineAchievementsWriteRef WriteObject = MakeShared<FOnlineAchievementsWrite>();
    WriteObject->SetIntStat(FName(*AchievementId), 100);

    FOnAchievementsWrittenDelegate Delegate;
    Delegate.AddUObject(this, &UMyGooglePlayManager::OnAchievementsWritten);
    Achievements->WriteAchievements(*PlayerId, WriteObject, Delegate);
}

void UMyGooglePlayManager::OnAchievementsWritten(const FUniqueNetId& PlayerId, bool bWasSuccessful)
{
    UE_LOG(LogTemp, Log, TEXT("Achievement write %s"), bWasSuccessful ? TEXT("succeeded") : TEXT("failed"));
}
```

## 模块依赖

从 Build.cs 的 `PrivateDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `Engine` | 引擎核心功能 |
| `CoreOnline` | 在线子系统核心类型定义 |
| `OnlineSubsystem` | 在线子系统框架接口 |
| `AndroidRuntimeSettings` | 读取 Android 平台配置（如 `bEnableGooglePlaySupport`） |
| `Launch` | 启动模块，用于 UPL 集成 |

**插件依赖**（.uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统基础框架 |
| `AndroidPermission` | Android 运行时权限管理 |

## 配置说明

### 配置项

在 `DefaultEngine.ini` 中需要配置以下内容：

```ini
[/Script/AndroidRuntimeSettings.AndroidRuntimeSettings]
bEnableGooglePlaySupport=True

[OnlineSubsystemGooglePlay.Store]
bSupportsInAppPurchasing=True
```

### 架构概览

插件采用 C++ / Java 双层架构，通过 JNI 桥接：

```
┌─────────────────────────────────────────┐
│  UE5 C++ 层                              │
│  FOnlineSubsystemGooglePlay              │
│  ├── FOnlineIdentityGooglePlay           │
│  ├── FOnlineAchievementsGooglePlay       │
│  ├── FOnlineLeaderboardsGooglePlay       │
│  ├── FOnlineStoreGooglePlayV2            │
│  ├── FOnlinePurchaseGooglePlay           │
│  └── FOnlineExternalUIGooglePlay         │
├─────────────────────────────────────────┤
│  JNI 桥接层                              │
│  FGooglePlayGamesWrapper                 │
│  OnlineJniGooglePlayStoreHelper          │
├─────────────────────────────────────────┤
│  Java 层                                 │
│  GooglePlayGamesWrapper.java             │
│  GooglePlayStoreHelper.java              │
│  (com.android.billingclient:billing:7.1.1) │
└─────────────────────────────────────────┘
```

### 内购响应码

| 枚举值 | 说明 |
|---|---|
| `Ok` (0) | 操作成功 |
| `UserCancelled` (1) | 用户取消 |
| `ServiceUnavailable` (2) | 服务不可用 |
| `BillingUnavailable` (3) | 计费不可用 |
| `ItemUnavailable` (4) | 商品不可用 |
| `DeveloperError` (5) | 开发者错误 |
| `Error` (6) | 通用错误 |
| `ItemAlreadyOwned` (7) | 商品已拥有 |
| `ItemNotOwned` (8) | 商品未拥有 |
| `FeatureNotSupported` (-2) | 功能不支持 |
| `ServiceDisconnected` (-1) | 服务断开 |
| `CustomLogicError` (-127) | Java 侧自定义逻辑错误 |

## 已实现接口

| 接口 | 实现类 | 状态 |
|---|---|---|
| `IOnlineIdentity` | `FOnlineIdentityGooglePlay` | ✅ 完整实现 |
| `IOnlineAchievements` | `FOnlineAchievementsGooglePlay` | ✅ 完整实现 |
| `IOnlineLeaderboards` | `FOnlineLeaderboardsGooglePlay` | ✅ 完整实现 |
| `IOnlineStoreV2` | `FOnlineStoreGooglePlayV2` | ✅ 完整实现 |
| `IOnlinePurchase` | `FOnlinePurchaseGooglePlay` | ✅ 完整实现 |
| `IOnlineExternalUI` | `FOnlineExternalUIGooglePlay` | ✅ 完整实现 |
| `IOnlineSession` | — | ❌ 返回 nullptr |
| `IOnlineFriends` | — | ❌ 返回 nullptr |
| `IOnlineVoice` | — | ❌ 返回 nullptr |
| `IOnlinePresence` | — | ❌ 返回 nullptr |
| `IOnlineChat` | — | ❌ 返回 nullptr |
| `IOnlineUser` | — | ❌ 返回 nullptr |

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-02 | `5a48f72f` | 注册 JNI 函数，创建 JNI 类，新增 thread_local Ue::Jni::Env 全局变量，JNI 相关 bug 修复和清理 |
| 2025-05-07 | `53bfbc88` | 更新 GooglePlay Billing 库至 7.1.1 |
| 2025-03-07 | `4276c916` | 修复 NDK 28+ 上的编译警告 |

### 维护评价

- **活跃维护**：最近 6 个月内有实质性更新（JNI 重构、Billing 库升级）
- **创建时间**：2016 年 7 月，已有约 10 年历史
- **维护频率**：定期更新，紧跟 Google Play Billing Library 的版本迭代
- **平台限制**：仅支持 Android，且需要 Google Play Services 环境
- **推荐程度**：✅ Android 平台开发推荐使用，是 UE5 官方提供的标准 Google Play 集成方案
- **注意事项**：不支持 Session、Friends、Voice 等社交功能；单设备单玩家设计（`MAX_LOCAL_PLAYERS == 1`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/Android/OnlineSubsystemGooglePlay)
