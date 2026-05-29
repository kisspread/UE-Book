# Online Services EOS

> Online Services implementation for EOS Account and Game services.

| 属性 | 值 |
|---|---|
| 中文名 | EOS在线服务 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesEOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOS) | |

## 用途

该插件是 **Epic Online Services (EOS)** 在 UE5 新版在线服务框架 (`UE::Online`) 下的核心实现。它解决了如何将 EOS 的底层 SDK 功能（如身份验证、好友、在场状态、商城等）以统一的、面向未来的 API 暴露给游戏逻辑的问题。与旧版 `OnlineSubsystemEOS` 不同，此插件遵循 UE5 的模块化设计，将各项在线功能（Auth、Social、Presence、Commerce 等）作为独立的“组件”实现，便于扩展和维护。

简单来说，**它是一个“驱动程序”或“适配层”**，让你的游戏能通过 `UE::Online` 提供的标准接口，使用 EOS 的账号系统、社交功能、游戏内购买、玩家状态同步等服务。

## 使用场景

- 你的游戏需要集成 **Epic Games Store 的商城系统**（DLC、内购）→ 使用 `FCommerceEOS` 组件。
- 你需要通过 EOS 的 **好友系统** 进行查询、添加好友、查看在线状态 → 使用 `FSocialEOS` 和 `FPresenceEOS` 组件。
- 你的游戏需要支持 **跨平台账号**，玩家可以使用 Epic Games 账号登录 → 使用 `FAuthEOS` 组件。
- 你需要使用 **EOS 的玩家身份标识** (`EOS_ProductUserId`, `EOS_EpicAccountId`) 并在内部转换为 UE 的 `FAccountId` → 依赖 `FOnlineAccountIdRegistryEOS` 及相关的解析器。
- 你希望在游戏内展示 **EOS 的官方 UI**（如登录、好友列表）→ 使用 `FExternalUIEOS` 组件。

## 蓝图用法

该插件主要提供 C++ 接口，其在线服务组件通常通过 `UOnlineServicesSubsystem` 或直接通过 `GetOnlineServices()` 获取。蓝图中直接调用的专用节点较少，更多是通过 C++ 逻辑驱动。核心操作均以异步句柄 (`TOnlineAsyncOpHandle`) 形式返回。

### 核心节点

由于插件本身不暴露大量 `UFUNCTION(BlueprintCallable)` 节点，其功能主要通过 UE5 的 `OnlineServices` 子系统在蓝图中进行访问。具体节点取决于你使用的服务（Auth、Social 等）。

### 使用示例（蓝图描述）

1.  **查询并显示好友列表**：
    *   首先，通过 `Online Services Subsystem` 节点，选择 **`EOS`** 作为服务提供者。
    *   调用 `Query Friends` 节点（来自 `Social` 服务），传入本地用户 ID。
    *   在成功回调中，调用 `Get Friends` 节点获取好友数据列表。
    *   遍历该列表，即可在 UI 上显示每个好友的名称、是否在线等信息（在场状态需额外通过 `Presence` 服务查询）。

2.  **发起内购**：
    *   通过 `Online Services Subsystem` 获取 **`EOS`** 的 `Commerce` 服务。
    *   调用 `Query Offers` 节点，从 EOS 后端拉取最新的商品列表（DLC，微交易物品等）。
    *   选择商品后，调用 `Checkout` 节点，这会调起 Epic Games Store 的结账流程。
    *   处理购买成功或失败的回调。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesEOS.h"
#include "Online/PresenceEOS.h"
#include "Online/CommerceEOS.h"
#include "Online/AccountIdEOS.h"
```

### 基本用法

**1. 获取在线服务实例并查询玩家在场状态**
*(概念示例，基于头文件结构推断)*

```cpp
// 在某个拥有世界上下文的类（如 GameInstance）中
void UMyGameInstance::QueryFriendPresence(FAccountId LocalUserId, FAccountId FriendUserId)
{
    // 获取 EOS 在线服务
    UE::Online::FOnlineServicesEOS* OnlineServicesEOS = static_cast<UE::Online::FOnlineServicesEOS*>(
        UE::Online::GetOnlineServices(UE::Online::EOnlineServices::Epic)
    );
    if (!OnlineServicesEOS) return;

    // 获取 Presence 接口
    UE::Online::FPresenceEOS* PresenceEOS = OnlineServicesEOS->GetPresence();
    if (!PresenceEOS) return;

    // 调用查询
    UE::Online::FQueryPresence::Params Params;
    Params.LocalAccountId = LocalUserId;
    Params.AccountIdsToQuery = {FriendUserId};

    PresenceEOS->QueryPresence(MoveTemp(Params))
        .Then([](UE::Online::TOnlineAsyncOpHandle<UE::Online::FQueryPresence> Handle) {
            if (Handle.IsError()) {
                UE_LOG(LogOnline, Error, TEXT("QueryPresence failed: %s"), *Handle.GetErrorValue().GetLogString());
                return;
            }

            // 查询成功，可以通过 GetCachedPresence 获取结果
            UE::Online::FGetPresence::Params GetParams;
            GetParams.LocalAccountId = LocalUserId; // 需要本地用户上下文
            GetParams.AccountId = FriendUserId;

            UE::Online::TOnlineResult<UE::Online::FGetPresence> Result = PresenceEOS->GetCachedPresence(MoveTemp(GetParams));
            if (Result.IsOk()) {
                TSharedRef<UE::Online::FUserPresence> Presence = Result.GetOkValue();
                UE_LOG(LogOnline, Log, TEXT("Friend Status: %s, Title: %s"), 
                    LexToString(Presence->Status), 
                    *Presence->StatusString);
            }
        });
}
```

**2. 使用账号 ID 注册表转换 EOS ID**
*(来源于 `AccountIdEOS.h` 的声明)*

```cpp
#include "Online/AccountIdEOS.h"

void ConvertEOStoUEId()
{
    EOS_EpicAccountId EpicId = ...; // 从 EOS SDK 回调中获得
    EOS_ProductUserId ProductId = ...;

    // 方法一：直接转换为 FAccountId (需要知道服务上下文)
    UE::Online::FAccountId AccountId1 = UE::Online::FindAccountId(UE::Online::EOnlineServices::Epic, EpicId);

    // 方法二：从组件内部转换（更常见）
    // 假设你已经拿到了一个 FOnlineServicesEOS 实例
    UE::Online::FOnlineAccountIdRegistryEOS& Registry = UE::Online::FOnlineAccountIdRegistryEOS::Get();
    UE::Online::FAccountId AccountId2 = Registry.FindOrAddAccountId(EpicId, ProductId);

    // 反向获取 EOS ID
    UE::Online::FOnlineAccountIdDataEOS EOSIds = Registry.GetAccountIdData(AccountId2);
    EOS_EpicAccountId MyEpicId = EOSIds.EpicAccountId;
    EOS_ProductUserId MyProductId = EOSIds.ProductUserId;
}
```

### 进阶用法

**处理账号链接流程**
*(来源于 `AuthEOS.h` 的接口)*

```cpp
// 当需要将本地账号与 Epic Games 账号关联时
void UMyGameInstance::LinkEpicAccount()
{
    UE::Online::FAuthEOS* AuthEOS = ...; // 获取 Auth 接口
    if (!AuthEOS) return;

    UE::Online::FAuthLinkAccount::Params Params;
    // ... 填充必要的参数，例如本地凭证

    AuthEOS->LinkAccount(MoveTemp(Params))
        .Then([AuthEOS](UE::Online::TOnlineAsyncOpHandle<UE::Online::FAuthLinkAccount> Handle) {
            if (Handle.IsError()) {
                // 处理错误
                return;
            }

            // 链接成功，获取继续操作的ID
            UE::Online::FAuthGetLinkAccountContinuationId::Params ContParams;
            ContParams.LocalAccountId = Handle.GetOkValue().LocalAccountId;

            UE::Online::TOnlineResult<UE::Online::FAuthGetLinkAccountContinuationId> Result = AuthEOS->GetLinkAccountContinuationId(ContParams);
            if (Result.IsOk()) {
                // 使用 continuation ID 进行下一步操作（如显示Web登录页面）
            }
        });
}
```

## Demo 示例

一个最小的示例，展示如何从 C++ 初始化并访问 EOS 的 Presence 服务。

**MyOnlineComponent.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Online/OnlineServicesEOS.h"
#include "Online/PresenceEOS.h"
#include "MyOnlineComponent.generated.h"

UCLASS(ClassGroup=(Online), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyOnlineComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable)
    void UpdateMyPresence(const FString& StatusString);

private:
    TWeakObjectPtr<UE::Online::FOnlineServicesEOS> CachedOnlineServices;
    TWeakObjectPtr<UE::Online::FPresenceEOS> CachedPresence;
};
```

**MyOnlineComponent.cpp**
```cpp
#include "MyOnlineComponent.h"

void UMyOnlineComponent::BeginPlay()
{
    Super::BeginPlay();

    // 获取 EOS 在线服务（假设只有一个实例）
    CachedOnlineServices = static_cast<UE::Online::FOnlineServicesEOS*>(
        UE::Online::GetOnlineServices(UE::Online::EOnlineServices::Epic)
    );
    if (CachedOnlineServices.IsValid())
    {
        CachedPresence = CachedOnlineServices->GetPresence();
    }
}

void UMyOnlineComponent::UpdateMyPresence(const FString& StatusString)
{
    if (!CachedPresence.IsValid() || !CachedOnlineServices.IsValid())
    {
        UE_LOG(LogTemp, Warning, TEXT("EOS Online Services or Presence not available."));
        return;
    }

    // 获取本地第一个已登录的账号ID（简化示例）
    UE::Online::FAccountId LocalAccountId;
    // ... 通常通过 Auth 服务获取本地用户列表 ...

    UE::Online::FPartialUpdatePresence::Params Params;
    Params.LocalAccountId = LocalAccountId;
    Params.Mutations.StatusString = StatusString;

    CachedPresence->PartialUpdatePresence(MoveTemp(Params))
        .Then([](UE::Online::TOnlineAsyncOpHandle<UE::Online::FPartialUpdatePresence> Handle) {
            if (Handle.IsOk())
            {
                UE_LOG(LogTemp, Log, TEXT("Presence updated successfully."));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Failed to update presence: %s"), *Handle.GetErrorValue().GetLogString());
            }
        });
}
```

## 模块依赖

你的项目模块如果要使用此插件，需要在 `Build.cs` 中添加以下依赖。注意，此插件自身依赖于 `OnlineServices` 框架和 EOS 共享模块。

| 模块 | 用途 |
|---|---|
| `OnlineServicesEOS` | 核心模块，提供 EOS 在线服务实现 |
| `OnlineServices` | UE5 在线服务基础框架 |
| `OnlineServicesEOSGS` | EOS 的通用服务器端（Game Server）支持，`OnlineServicesEOS` 依赖于此 |
| `EOSShared` | Epic Online Services 的共享工具和类型定义 |
| `OnlineSubsystem` | （可选）如果需要与旧版 `OnlineSubsystem` 接口进行交互或兼容 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-20 | `6c52ba35` | Fix FPresenceEOS local cache drift when PartialUpdatePresence calls merge via GetMergeableOp | 修复了 PartialUpdatePresence 操作合并时导致本地缓存状态漂移的问题 |
| 2026-04-14 | `2c013d6c` | Online Services EOS Presence Refactor: | EOS 在线服务在场状态功能重构 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏 UE_LOG 迁移为新的 UE_LOGF 宏 |
| 2026-01-22 | `f4f02393` | Added logic to clear EOS presence state for user on auth logout | 增加了用户认证登出时清除其 EOS 在场状态的逻辑 |
| 2025-11-20 | `00a3e8e7` | Removal of internal logic setting SentTime attribute. | 移除了内部设置 SentTime 属性的逻辑 |

### 维护评价

该插件处于 **活跃维护** 状态。
1.  **年龄**：创建于 2022 年 9 月，至今约 4 年，属于较新的插件。
2.  **更新频率**：最近一次提交在 2026 年 4 月，且包含功能重构和重要 bug 修复（如在场状态缓存漂移），表明 Epic 团队仍在持续投入开发。
3.  **功能状态**：作为 `OnlineSubsystemEOS` 在 UE5 新架构下的继任者，它是 Epic 官方推荐的 EOS 集成方式，功能稳定且在持续完善。
4.  **已知限制**：插件 `EnabledByDefault` 为 `false`，必须在项目的 `.uproject` 或插件配置中手动启用。平台支持列表中不包含主流主机平台（Xbox, PlayStation, Nintendo Switch），主机支持通常需要通过其他特定于平台的 OnlineSubsystem 插件实现。
5.  **推荐使用**：**强烈推荐** 需要在 UE5 项目中深度集成 Epic Online Services 的开发者使用。它是未来 EOS 集成的标准路径。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOS)
- [官方文档](https://dev.epicgames.com/docs/epic-online-services)（EOS 开发者门户，涵盖所有服务细节）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServicesEOS/Source/OnlineServicesESTest)（注：根据常见结构推测，需在源码库中确认具体路径）