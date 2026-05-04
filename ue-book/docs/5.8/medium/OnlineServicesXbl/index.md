# Online Services Xbox Live

> Online Services implementation for Xbox Live.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesXbl` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2026-02-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/OnlineServicesXbl) | |

## 用途

`OnlineServicesXbl` 是 UE5 `OnlineServices` 抽象层针对 **Xbox Live** 平台的具体实现插件。它封装了 Xbox Live 的 GDK (Game Development Kit) API，为游戏提供了在 Xbox 平台上访问 Xbox Live 核心在线服务的能力，包括玩家认证、社交关系、成就、排行榜、云存储、商店和特权检查等。

该插件的存在是为了让开发者能够通过 UE5 统一的 `OnlineServices` 接口，无缝地集成 Xbox Live 的功能，而无需直接处理复杂的平台原生 API。

## 使用场景

- 你正在为 **Xbox 平台**（或 Win64 GDK 环境）开发一款游戏，需要集成 Xbox Live 的在线功能。
- 你需要通过统一的 API 来管理玩家的 Xbox Live 账户登录、好友列表、成就解锁、购买和云存档。
- 你的项目需要支持 Xbox Live 的多人游戏会话、排行榜和实时活动。

## 蓝图用法

此插件主要作为 `OnlineServices` 的后端实现，其功能通常通过 `OnlineServices` 的通用蓝图接口（如 `Get Online Services` 节点）来访问。插件本身没有直接暴露特定的蓝图节点，而是通过 `OnlineServices` 的抽象层提供服务。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Services` | 获取当前平台的在线服务实例（对于Xbox平台，将返回 `FOnlineServicesXbl`） | `UOnlineServicesSubsystem` |

### 使用示例（蓝图描述）

1.  在蓝图中，使用 `Get Online Services` 节点获取在线服务实例。
2.  从该实例，你可以调用 `Query Friends`、`Query Achievements` 等通用在线服务节点。
3.  当平台为 Xbox 时，这些调用会自动路由到 `OnlineServicesXbl` 插件进行处理。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesXbl.h"
#include "Online/AuthXbl.h"
#include "Online/SocialXbl.h"
```

### 基本用法

以下示例展示了如何获取 Xbox Live 在线服务实例并查询好友列表。

```cpp
// 来源: 基于 Source/Public/Online/OnlineServicesXbl.h 和 SocialXbl.h 的接口设计
#include "Online/OnlineServicesXbl.h"
#include "Online/SocialXbl.h"

void QueryXboxLiveFriends()
{
    // 获取 Xbox Live 在线服务实例
    UE::Online::FOnlineServicesXbl* XblServices = static_cast<UE::Online::FOnlineServicesXbl*>(
        UE::Online::GetServices(UE::Online::EOnlineServices::Xbox).Get()
    );

    if (!XblServices)
    {
        UE_LOG(LogOnline, Error, TEXT("Failed to get Xbox Live online services."));
        return;
    }

    // 获取社交组件
    UE::Online::FSocialXbl* SocialComponent = XblServices->GetSocial<UE::Online::FSocialXbl>();
    if (!SocialComponent)
    {
        UE_LOG(LogOnline, Error, TEXT("Failed to get Social component."));
        return;
    }

    // 准备查询参数（需要有效的本地账户ID）
    UE::Online::FQueryFriends::Params QueryParams;
    QueryParams.LocalAccountId = /* 你的本地账户ID */;

    // 异步查询好友列表
    SocialComponent->QueryFriends(MoveTemp(QueryParams))
        .OnComplete([](const UE::Online::TOnlineResult<UE::Online::FQueryFriends>& Result)
        {
            if (Result.IsOk())
            {
                UE_LOG(LogOnline, Log, TEXT("Successfully queried Xbox Live friends."));
                // 可以在此处调用 GetFriends 获取结果
            }
            else
            {
                UE_LOG(LogOnline, Error, TEXT("Failed to query friends: %s"), *Result.GetErrorValue().GetLogString());
            }
        });
}
```

### 进阶用法

处理异步操作和事件，例如监听成就解锁通知。

```cpp
// 来源: 基于 Source/Public/Online/AchievementsXbl.h 和 UserContextsManagerXbl.h 的事件机制
#include "Online/AchievementsXbl.h"
#include "Online/UserContextsManagerXbl.h"

void SetupAchievementNotification()
{
    UE::Online::FOnlineServicesXbl* XblServices = /* ... 获取服务实例 ... */;
    UE::Online::FAchievementsXbl* AchievementsComponent = XblServices->GetAchievements<UE::Online::FAchievementsXbl>();

    if (AchievementsComponent)
    {
        // 注册成就解锁通知回调
        // 注意：实际的事件绑定机制可能通过 FUserContextsManagerXbl 或 FOnlineServicesXbl 的事件分发器
        // 这里仅为概念示例
        AchievementsComponent->AchievementUnlockNotificationDelegate.AddLambda(
            [](const UE::Online::FAchievementUpdate& Update)
            {
                UE_LOG(LogOnline, Log, TEXT("Achievement unlocked: %s"), *Update.AchievementId);
            }
        );
    }
}
```

## Demo 示例

一个最小的示例，展示如何初始化并使用 `OnlineServicesXbl` 查询用户信息。

**MyXblServiceUser.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Online/OnlineServicesXbl.h"

class FMyXblServiceUser
{
public:
    void Initialize();
    void QueryUserInfo(const UE::Online::FAccountId& TargetAccountId);

private:
    TSharedPtr<UE::Online::FOnlineServicesXbl> XblServices;
};
```

**MyXblServiceUser.cpp**
```cpp
#include "MyXblServiceUser.h"
#include "Online/UserInfoXbl.h"

void FMyXblServiceUser::Initialize()
{
    // 获取 Xbox Live 服务实例
    XblServices = StaticCastSharedPtr<UE::Online::FOnlineServicesXbl>(
        UE::Online::GetServices(UE::Online::EOnlineServices::Xbox)
    );
}

void FMyXblServiceUser::QueryUserInfo(const UE::Online::FAccountId& TargetAccountId)
{
    if (!XblServices.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Xbox Live services not initialized."));
        return;
    }

    UE::Online::FUserInfoXbl* UserInfoComponent = XblServices->GetUserInfo<UE::Online::FUserInfoXbl>();
    if (!UserInfoComponent)
    {
        UE_LOG(LogTemp, Error, TEXT("UserInfo component not available."));
        return;
    }

    // 假设我们已经有一个本地账户ID
    UE::Online::FAccountId LocalAccountId = /* ... */;

    UE::Online::FQueryUserInfo::Params Params;
    Params.LocalAccountId = LocalAccountId;
    Params.AccountIds = {TargetAccountId};

    UserInfoComponent->QueryUserInfo(MoveTemp(Params))
        .OnComplete([this, TargetAccountId](const UE::Online::TOnlineResult<UE::Online::FQueryUserInfo>& Result)
        {
            if (Result.IsOk())
            {
                // 查询成功，现在可以获取用户信息
                UE::Online::FGetUserInfo::Params GetParams;
                GetParams.LocalAccountId = /* ... */;
                GetParams.AccountId = TargetAccountId;

                UE::Online::TOnlineResult<UE::Online::FGetUserInfo> UserInfoResult = UserInfoComponent->GetUserInfo(MoveTemp(GetParams));
                if (UserInfoResult.IsOk())
                {
                    const UE::Online::FUserInfo& Info = UserInfoResult.GetOkValue();
                    UE_LOG(LogTemp, Log, TEXT("User Name: %s"), *Info.DisplayName);
                }
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Query user info failed."));
            }
        });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineServices` | UE5 在线服务抽象层核心模块，此插件是其后端实现之一 |
| `GDKRuntime` | 提供 Xbox GDK 运行时环境和基础句柄类型 |
| `OnlineSubsystemUtils` | 在线子系统工具函数（可能被间接依赖） |

## 维护状态

### 近期更新

- 2026-04-17 `4260cb83` 从项目目录加载成就配置文件，并废弃旧的平台配置路径
- 2026-04-16 `270dc64a` 修复不可达代码警告
- 2026-04-14 `35e60df1` 将 UE_LOG 迁移至 UE_LOGF 宏

### 维护评价

- **创建时间**：2026年2月，是一个非常新的插件。
- **最近更新**：在2026年4月有多次提交，包括功能改进（配置加载）、代码质量修复（警告、日志宏）和重构。这表明插件正在**积极开发和维护**中。
- **活跃度**：作为 Xbox 平台在线服务的核心实现，预计会随着引擎版本和 GDK 更新而持续维护。
- **已知限制**：仅支持 `Win64` 平台（GDK 环境），且默认禁用，需要手动启用。
- **推荐使用**：**强烈推荐**用于所有面向 Xbox 平台的 UE5 项目。它是集成 Xbox Live 功能的官方且标准的方式。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/OnlineServicesXbl)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/online-subsystem-and-services-in-unreal-engine/) (通用在线服务文档)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/OnlineServices) (通用在线服务测试，可能包含XBL相关测试)