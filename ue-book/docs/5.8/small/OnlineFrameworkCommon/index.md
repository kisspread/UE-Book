# Online Framework Common

> Common functionality for Online Frameworks

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架通用 |
| 分类 | Online |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（配置资产） |
| 模块 | `OnlineFrameworkCommon` (Runtime) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2025-07-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFrameworkCommon) | |

## 用途

本插件提供了一套统一的在线账户身份管理和配置框架，用于抽象和整合不同的在线服务后端（如 Epic Online Services (EOS)、Steam、Null 等）。它解决了在同时使用多个在线服务实例或进行多平台开发时，玩家账户身份（`FAccountId`）如何被统一识别和管理的问题。插件通过 `FCommonAccount` 和 `FCommonAccountManager` 实现账户 ID 的查找、关联和合并，并使用 `FCommonConfig` 来解析不同在线服务实例的配置。

## 使用场景

- 你的游戏需要同时集成多个在线服务提供商（例如，主服务用 EOS，特定地区用其他服务）。
- 你在开发多平台游戏（PC, 主机, 移动端），需要一个统一的层来处理不同平台的账户 ID。
- 你需要将旧的 `FUniqueNetId` 系统平滑迁移到新的 `OnlineServices` 框架。
- 你需要自动发现并关联代表同一真实玩家的不同在线服务账户 ID。

## 蓝图用法

此插件主要通过 C++ 接口提供服务，没有直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)`。其功能通常被其他更高层次的在线游戏服务插件（如 `OnlineSubsystem` 或游戏特定的在线功能模块）所使用。若需在蓝图中使用相关功能，应通过封装 C++ 逻辑的蓝图函数库或游戏模块来实现。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineFramework/CommonAccountManager.h"
#include "OnlineFramework/CommonAccount.h"
#include "OnlineFramework/CommonConfig.h"
```

### 基本用法

以下示例展示了如何获取 `FCommonAccountManager` 并使用它来查询一个账户。

```cpp
// 假设在一个 UObject 或有有效 ContextObject 的上下文中
void QueryAccountExample(const UObject* ContextObject)
{
    // 1. 创建或获取 CommonConfig，它会自动从 ContextObject 推断世界和上下文类型
    UE::OnlineFramework::FCommonConfig MyConfig(ContextObject);

    // 2. 获取（或创建）该配置对应的账户管理器单例
    UE::OnlineFramework::FCommonAccountManagerPtr AccountManager = UE::OnlineFramework::FCommonAccountManager::Get(MyConfig);

    // 3. 获取或创建一个表示特定在线服务账户的 CommonAccount 对象
    // 假设 `SomeAccountId` 是来自 EOS 的有效 FAccountId
    UE::OnlineFramework::FCommonAccountPtr MyAccount = AccountManager->GetAccount(SomeAccountId, TEXT("MyEOSFramework"));

    if (MyAccount)
    {
        // 4. 查询这个账户是否关联了另一个框架（如 Steam）的账户 ID
        MyAccount->GetIdAsync(TEXT("MySteamFramework"),
            UE::OnlineFramework::FCommonAccount::FOnGetIdAsyncComplete::CreateLambda(
                [](const UE::OnlineFramework::FCommonAccountRef& ResolvedAccount, UE::Online::FAccountId FoundSteamId)
                {
                    if (FoundSteamId.IsValid())
                    {
                        // 成功找到关联的 Steam ID
                        UE_LOG(LogTemp, Log, TEXT("Found Steam ID: %s for account: %s"), *FoundSteamId.ToString(), *ResolvedAccount->ToLogString());
                    }
                }
            ));
    }
}
```

### 进阶用法

你可以注册自定义的账户 ID 查找逻辑来扩展系统。

```cpp
// 假设你有一个自定义的数据库或服务可以查找账户关联
UE::OnlineFramework::FCommonAccountLookupAccountIdFnHandle MyLookupHandle;

void RegisterCustomLookup(UE::OnlineFramework::FCommonAccountManagerPtr AccountManager)
{
    MyLookupHandle = AccountManager->RegisterAccountIdLookup(TEXT("MyDatabaseLookup"),
        [](UE::OnlineFramework::FCommonAccount& Account, FName RequestingFrameworkInstance, const UE::OnlineFramework::FCommonConfigInstance& ConfigInstance) -> TFuture<UE::Online::FAccountId>
        {
            auto Promise = MakeShared<TPromise<UE::Online::FAccountId>>();
            // ... 异步查询你的数据库 ...
            // 查询完成后设置 Promise 的值
            // Promise->SetValue(FoundAccountId);
            return Promise->GetFuture();
        });
}
// 当不再需要时，MyLookupHandle 的析构函数会自动取消注册
```

监听账户管理器事件以响应账户的创建和合并。

```cpp
FDelegateHandle OnAccountCreatedHandle;
FDelegateHandle OnDuplicateHandle;

void BindAccountEvents(UE::OnlineFramework::FCommonAccountManagerPtr AccountManager)
{
    OnAccountCreatedHandle = AccountManager->OnCommonAccountCreated().AddLambda(
        [](const UE::OnlineFramework::FCommonAccountRef& NewAccount)
        {
            UE_LOG(LogTemp, Log, TEXT("New Common Account Created: %s"), *NewAccount->ToLogString());
        });

    OnDuplicateHandle = AccountManager->OnCommonAccountDuplicateDetected().AddLambda(
        [](const UE::OnlineFramework::FCommonAccountRef& KeptAccount, const UE::OnlineFramework::FCommonAccountRef& RemovedAccount)
        {
            UE_LOG(LogTemp, Warning, TEXT("Account merge detected. Kept: %s, Removed: %s. Update references!"),
                *KeptAccount->ToLogString(), *RemovedAccount->ToLogString());
            // 你的代码需要更新所有引用 RemovedAccount 的地方到 KeptAccount
        });
}
```

## Demo 示例

以下是一个完整的、可运行的最小示例，演示了账户管理器的核心生命周期。

**OnlineFrameworkCommonDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "OnlineFramework/CommonAccountManager.h"
#include "OnlineFramework/CommonAccount.h"

class FOnlineFrameworkCommonDemo
{
public:
    static void RunDemo(const UObject* ContextObject);

private:
    static void HandleGetIdComplete(const UE::OnlineFramework::FCommonAccountRef& Account, UE::Online::FAccountId AccountId);
};
```

**OnlineFrameworkCommonDemo.cpp**
```cpp
#include "OnlineFrameworkCommonDemo.h"
#include "OnlineFramework/CommonConfig.h"
#include "Online/Framework.h" // For FAccountId

void FOnlineFrameworkCommonDemo::RunDemo(const UObject* ContextObject)
{
    if (!ContextObject) return;

    // 创建配置
    UE::OnlineFramework::FCommonConfig DemoConfig(ContextObject);

    // 获取账户管理器
    UE::OnlineFramework::FCommonAccountManagerPtr Manager = UE::OnlineFramework::FCommonAccountManager::Get(DemoConfig);
    if (!Manager) return;

    // 模拟一个来自 EOS 的账户 ID
    UE::Online::FAccountId EosAccountId = UE::Online::FAccountId(TEXT("EOS_USER_123"));

    // 获取对应的 CommonAccount 对象
    UE::OnlineFramework::FCommonAccountPtr Account = Manager->GetAccount(EosAccountId, TEXT("DefaultOnlineServices"));
    if (!Account) return;

    UE_LOG(LogTemp, Log, TEXT("Got Account: %s"), *Account->ToLogString());

    // 尝试查找它在“Null”服务中的关联 ID
    Account->GetIdAsync(TEXT("NullOnlineServices"), 
        UE::OnlineFramework::FCommonAccount::FOnGetIdAsyncComplete::CreateStatic(&FOnlineFrameworkCommonDemo::HandleGetIdComplete));

    // 模拟手动添加一个已知关联
    UE::Online::FAccountId NullAccountId = UE::Online::FAccountId(TEXT("NULL_USER_ABC"));
    Account->AddId(TEXT("NullOnlineServices"), NullAccountId);
    UE_LOG(LogTemp, Log, TEXT("Manually added Null ID. Cached Null ID: %s"), *Account->GetId(TEXT("NullOnlineServices")).ToString());
}

void FOnlineFrameworkCommonDemo::HandleGetIdComplete(const UE::OnlineFramework::FCommonAccountRef& Account, UE::Online::FAccountId AccountId)
{
    if (AccountId.IsValid())
    {
        UE_LOG(LogTemp, Log, TEXT("Asynchronously found associated Null ID: %s for account: %s"), *AccountId.ToString(), *Account->ToLogString());
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Could not find an associated Null ID for account: %s"), *Account->ToLogString());
    }
}
```

## 模块依赖

此插件依赖于以下其他插件，使用前请确保它们已启用：
| 模块 | 用途 |
|---|---|
| `OnlineServices` | 提供核心的 `FAccountId` 和 `IOnlineServices` 接口。 |
| `OnlineServicesNull` | 提供用于测试和开发的空实现在线服务。 |
| `OnlineServicesOSSAdapter` | 提供从旧版 Online Subsystem 到新版 Online Services 的适配层。 |

无特殊模块依赖（仅标准 Core/Engine 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从旧版UE_LOG迁移到UE_LOGF新标准。 |
| 2026-03-03 | `96eff92b` | Compile fixes for programs that do not compile against Application Core and/or Engine. | 修复了在某些不依赖 Application Core 或 Engine 的独立程序中的编译问题。 |
| 2025-12-15 | `6dbfa804` | Fix crash when UpdateRichPresenceForServices is called on a logged out user | 修复了在用户已登出时调用 UpdateRichPresenceForServices 导致的崩溃问题。 |
| 2025-09-22 | `b04077dc` | Use the source account id framework instance name to get the common account | 改进了获取通用账户的逻辑，现在使用源账户ID的框架实例名称。 |
| 2025-09-18 | `732d0694` | Merge conflict from 45968147. | 处理了一次代码合并冲突。 |

### 维护评价

该插件非常新（创建于2025年7月），并且仍在活跃维护中（最近更新在2026年4月）。从提交历史看，更新内容包括功能改进、编译修复和Bug修复。然而，**该插件当前被标记为实验性（`IsBetaVersion: true`）且默认不启用**，这意味着其API和功能在未来版本中可能会有较大变动，不建议在稳定的生产项目中完全依赖。它目前主要服务于Epic内部（如从Fortnite项目迁移而来）或作为在线框架开发的基础组件。如果你正在构建自定义的在线框架或集成，可以将其作为参考或起点，但需做好跟随API变化的准备。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFrameworkCommon)
- [官方文档]()（无）