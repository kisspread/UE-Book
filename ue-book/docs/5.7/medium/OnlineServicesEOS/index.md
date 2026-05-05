# Online Services EOS

> Online Services implementation for EOS Account and Game services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesEOS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOS) | |

## 用途

OnlineServicesEOS 是 UE5 新一代在线服务框架（`UE::Online`）的 **Epic Online Services (EOS) 完整实现层**。它在 `OnlineServicesEOSGS`（Game Services 基础层）之上注册了 EOS 特有的在线服务组件，包括认证、社交、在线状态、用户信息、商城和外部 UI。

与旧版 `OnlineSubsystemEOS` 不同，本插件基于 UE5 的模块化 `IOnlineServices` 接口体系，每个功能域是独立的组件（Component），可以按需组合。EOS 账号体系有两层 ID：`EOS_EpicAccountId`（Epic 账号，对应 epicgames.com 登录）和 `EOS_ProductUserId`（产品用户 ID，对应游戏内身份），本插件负责两者的映射和管理。

**为什么存在？** EOS SDK 提供了跨平台的在线服务能力，本插件将这些能力桥接到 UE5 的 `IOnlineServices` 抽象层，让游戏代码可以通过统一接口访问 EOS 的认证、好友、商城等功能，而无需直接调用 EOS C API。

## 使用场景

- 你的多人在线游戏需要使用 Epic Online Services 作为后端 → 启用本插件
- 你需要跨平台好友系统（PC/Mac/Linux/Android）→ 本插件提供 EOS Friends 实现
- 你需要 EOS 商城/权益系统（IAP、DLC 验证）→ 使用 `FCommerceEOS` 组件
- 你需要 EOS 登录流程（包括账号关联）→ 使用 `FAuthEOS` 组件
- 你需要显示 EOS Overlay UI（好友列表、登录界面）→ 使用 `FExternalUIEOS`

## 蓝图用法

本插件没有暴露 `BlueprintCallable` 函数。所有功能通过 C++ `IOnlineServices` 接口访问。蓝图层面可通过通用的 Online Services 蓝图库间接使用（如果存在）。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesEOS.h"
#include "Online/AuthEOS.h"
#include "Online/SocialEOS.h"
#include "Online/PresenceEOS.h"
#include "Online/UserInfoEOS.h"
#include "Online/CommerceEOS.h"
#include "Online/ExternalUIEOS.h"
#include "Online/AccountIdEOS.h"
```

### 基本用法 — 获取 EOS 在线服务实例

```cpp
using namespace UE::Online;

// 通过 OnlineServicesRegistry 获取 Epic 在线服务实例
TSharedPtr<IOnlineServices> OnlineServices = FOnlineServicesRegistry::Get().GetServices(EOnlineServices::Epic, NAME_DefaultPlayer);
if (OnlineServices)
{
    // 获取认证接口
    IAuth* Auth = OnlineServices->GetAuthInterface();
    // 获取社交接口
    ISocial* Social = OnlineServices->GetSocialInterface();
    // 获取商城接口
    ICommerce* Commerce = OnlineServices->GetCommerceInterface();
}
```

### 基本用法 — 登录流程

```cpp
using namespace UE::Online;

// Login 是一个 6 步异步流程：
// 1. 验证参数
// 2. EAS (Epic Account Service) 登录
// 3. 获取外部认证令牌
// 4. Connect 登录（获取 ProductUserId）
// 5. 获取用户信息（显示名）
// 6. 触发登录状态变更事件

FAuthLogin::Params LoginParams;
LoginParams.PlatformUserId = PlatformUserId;
LoginParams.CredentialsType = ELoginCredentialsType::ExchangeCode;
LoginParams.CredentialsId = TEXT("...");
LoginParams.CredentialsToken = TEXT("...");

Auth->Login(MoveTemp(LoginParams)).Then([](TOnlineAsyncOpResult<FAuthLogin>&& Result)
{
    if (Result.IsOk())
    {
        // 登录成功，可获取 AccountId
        FAccountId AccountId = Result.GetOkValue().AccountInfo->AccountId;
    }
});
```

### 进阶用法 — 账号 ID 解析

EOS 有两种 ID 互相映射：

```cpp
using namespace UE::Online;

// 从 EpicAccountId 获取 FAccountId
FAccountId AccountId = FindAccountId(EpicAccountId);

// 从 FAccountId 获取 EpicAccountId
EOS_EpicAccountId EpicId = GetEpicAccountId(AccountId);

// 创建同时包含两种 ID 的 AccountId
FAccountId FullAccountId = CreateAccountId(EpicAccountId, ProductUserId);

// 通过 Resolver 组件批量解析
FEpicAccountIdResolverEOS Resolver;
TFuture<TArray<FAccountId>> Resolved = Resolver.ResolveAccountIds(LocalAccountId, EpicAccountIds);
```

来源: `Source/Private/Online/OnlineIdEOS.cpp`

### 进阶用法 — 好友系统

```cpp
using namespace UE::Online;

ISocial* Social = OnlineServices->GetSocialInterface();

// 查询好友列表
FQueryFriends::Params QueryParams;
QueryParams.LocalAccountId = LocalAccountId;
Social->QueryFriends(MoveTemp(QueryParams)).Then([Social, LocalAccountId](TOnlineAsyncOpResult<FQueryFriends>&& Result)
{
    if (Result.IsOk())
    {
        FGetFriends::Params GetParams;
        GetParams.LocalAccountId = LocalAccountId;
        TOnlineResult<FGetFriends> Friends = Social->GetFriends(MoveTemp(GetParams));
    }
});

// 发送好友邀请
FSendFriendInvite::Params InviteParams;
InviteParams.LocalAccountId = LocalAccountId;
InviteParams.FriendAccountId = TargetAccountId;
Social->SendFriendInvite(MoveTemp(InviteParams));
```

### 进阶用法 — 商城/权益

```cpp
using namespace UE::Online;

ICommerce* Commerce = OnlineServices->GetCommerceInterface();

// 查询商品
FCommerceQueryOffers::Params OfferParams;
OfferParams.LocalAccountId = LocalAccountId;
Commerce->QueryOffers(MoveTemp(OfferParams));

// 查询权益
FCommerceQueryEntitlements::Params EntitlementParams;
EntitlementParams.LocalAccountId = LocalAccountId;
Commerce->QueryEntitlements(MoveTemp(EntitlementParams));

// 结账
FCommerceCheckout::Params CheckoutParams;
CheckoutParams.LocalAccountId = LocalAccountId;
CheckoutParams.OfferId = OfferId;
Commerce->Checkout(MoveTemp(CheckoutParams));
```

## Demo 示例

### Build.cs 依赖

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "OnlineServicesInterface",
    "OnlineServicesCommon",
    "OnlineServicesEOSGS"
});
```

### .h + .cpp 最小示例

```cpp
// MyOnlineManager.h
#pragma once
#include "Online/OnlineServicesEOS.h"
#include "Online/AuthEOS.h"

class FMyOnlineManager
{
public:
    void Login(FPlatformUserId UserId);
    void QueryFriends();
};
```

```cpp
// MyOnlineManager.cpp
#include "MyOnlineManager.h"
#include "Online/OnlineServicesRegistry.h"

void FMyOnlineManager::Login(FPlatformUserId UserId)
{
    using namespace UE::Online;

    TSharedPtr<IOnlineServices> Services = FOnlineServicesRegistry::Get().GetServices(EOnlineServices::Epic, NAME_DefaultPlayer);
    if (!Services) return;

    IAuth* Auth = Services->GetAuthInterface();
    FAuthLogin::Params Params;
    Params.PlatformUserId = UserId;
    Params.CredentialsType = ELoginCredentialsType::ExchangeCode;

    Auth->Login(MoveTemp(Params)).Then([](TOnlineAsyncOpResult<FAuthLogin>&& Result)
    {
        if (Result.IsOk())
        {
            UE_LOG(LogTemp, Log, TEXT("EOS Login successful"));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("EOS Login failed: %s"), *Result.GetErrorValue().GetLogString());
        }
    });
}

void FMyOnlineManager::QueryFriends()
{
    using namespace UE::Online;

    TSharedPtr<IOnlineServices> Services = FOnlineServicesRegistry::Get().GetServices(EOnlineServices::Epic, NAME_DefaultPlayer);
    if (!Services) return;

    ISocial* Social = Services->GetSocialInterface();
    // ... QueryFriends/GetFriends 调用
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `OnlineServicesInterface` | 在线服务抽象接口定义 |
| `OnlineServicesCommon` | 在线服务通用基类实现 |
| `OnlineServicesEOSGS` | EOS Game Services 基础层（本插件继承自它） |
| `CoreOnline` | 在线服务核心类型（FAccountId 等） |
| `CoreUObject` | UObject 基础设施 |
| `EOSSDK` | Epic Online Services SDK |
| `EOSShared` | EOS 共享工具和类型 |
| `OnlineServicesEpicCommon` | Epic 平台在线服务通用实现 |

### 插件依赖

| 插件 | 用途 |
|---|---|
| `OnlineServices` | 在线服务框架基础设施 |
| `OnlineServicesEOSGS` | EOS Game Services 基础实现（认证 Connect 流程） |
| `EOSShared` | EOS SDK 共享层 |

## 组件架构

本插件注册了以下 8 个 EOS 组件（在 `FOnlineServicesEOS::RegisterComponents()` 中）：

| 组件类 | 基类 | 功能 |
|---|---|---|
| `FAuthEOS` | `FAuthEOSGS` | 认证：EAS 登录 + Connect 登录 + 账号关联 |
| `FEpicAccountIdResolverEOS` | `IEpicAccountIdResolver` | EpicAccountId → FAccountId 解析 |
| `FEpicProductUserIdResolverEOS` | `IEpicProductUserIdResolver` | ProductUserId → FAccountId 解析 |
| `FExternalUIEOS` | `FExternalUIEOSGS` | EOS Overlay UI（登录界面、好友界面） |
| `FSocialEOS` | `FSocialEOS` | 好友系统：查询/邀请/接受/拒绝/拉黑 |
| `FPresenceEOS` | `FPresenceCommon` | 在线状态：查询/更新/部分更新 |
| `FUserInfoEOS` | `FUserInfoCommon` | 用户信息：查询/获取显示名等 |
| `FCommerceEOS` | `FCommerceCommon` | 商城：商品查询/结账/权益管理 |

### 账号 ID 体系

EOS 的账号 ID 是 `EOS_EpicAccountId` 和 `EOS_ProductUserId` 的组合：
- **EpicAccountId (EAS)**: Epic Games 账号，用于 epicgames.com 登录
- **ProductUserId (EOS)**: 产品用户 ID，用于游戏内操作

`FOnlineAccountIdRegistryEOS` 管理两者之间的映射，支持：
- 线程安全的读写锁（`FTransactionallySafeRWLock`）
- 双向查找（EpicAccountId ↔ FAccountId, ProductUserId ↔ FAccountId）
- 序列化/反序列化用于网络复制（`ToReplicationData` / `FromReplicationData`）
- 字符串序列化（`ToString` / `FromStringData`，格式为 `EpicAccountId:ProductUserId`）

### 认证流程

`FAuthEOS::Login` 是一个 6 步异步管道：
1. 验证参数，清除旧的 ContinuanceToken
2. 调用 `LoginEASImpl` 进行 Epic Account Service 登录
3. 获取外部认证令牌（`GetExternalAuthTokenImpl`）
4. 调用 `LoginConnectImpl` 进行 Connect 登录获取 ProductUserId
5. 获取用户显示名（`EOS_UserInfo_CopyBestDisplayName`）
6. 注册 AccountInfo，触发 `OnAuthLoginStatusChanged` 事件

`FAuthEOS::LinkAccount` 是 7 步流程，处理账号关联（新用户注册、选择已有账号等场景）。

## 测试用例

测试文件: `Source/Private/Online/Tests/OnlineIdEOSTests.cpp`

测试名称: `System.Engine.Online.EosAccountIdReplicationTest`

测试内容: 验证 `FOnlineAccountIdRegistryEOS` 的序列化/反序列化正确性：
- 同时有 EpicAccountId + ProductUserId 的完整账号
- 只有 EpicAccountId 的账号
- 只有 ProductUserId 的账号

```cpp
// 测试模式：创建账号 → 序列化 → 反序列化 → 比较
FAccountId AccountId = Registry.FindOrAddAccountId(EasId, EosId);
TArray<uint8> RepData = Registry.ToReplicationData(AccountId);
FAccountId AccountId2 = Registry.FromReplicationData(RepData);
UTEST_EQUAL(TEXT(""), AccountId, AccountId2);
```

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-09-26 | `16f8811` | 为 EOS ID 解析调用添加 FastTick 支持 — 提升 ID 解析的响应速度 |
| 2025-09-23 | `0b167ae` | 修复 V2 逻辑中用户在线状态检查；重构从 EOSSDK 读取 presence platform 的逻辑；重构 UserInfoEOS 中 displayname 获取的优先级逻辑 |
| 2025-09-23 | `df6d574` | 添加通过控制台命令打印 presence state 的功能（同时支持 OSS 和 OnlineServices） |

### 维护评价

- **创建时间**: 2022-09-30，约 4 年历史
- **活跃度**: 活跃维护中。2025 年 9 月仍有功能性更新（ID 解析优化、在线状态修复）
- **依赖链**: 本插件是 EOS 在线服务栈的顶层，依赖 `OnlineServicesEOSGS` 提供的 Game Services 基础实现
- **平台支持**: Win64, Mac, Linux, LinuxArm64, Android
- **注意**: `EnabledByDefault: false`，需要在项目设置中手动启用
- **推荐**: ✅ 推荐使用。这是 UE5 官方的 EOS Online Services 实现，活跃维护，功能完整

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOS)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/OnlineServicesEOS/Source/Private/Online/Tests/OnlineIdEOSTests.cpp)
