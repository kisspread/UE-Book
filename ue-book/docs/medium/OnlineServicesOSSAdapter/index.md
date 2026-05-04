# Online Services OSS Adapter

> Online Services adapter for Online Subsystem implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesOSSAdapter` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesOSSAdapter) | |

## 用途

OnlineServicesOSSAdapter 是 UE5 在线服务架构迁移过程中的**桥梁层**。它的核心使命是：**让新的 `OnlineServices`（V2）API 能够复用已有的 `OnlineSubsystem`（V1）后端实现**。

UE5 同时维护两套在线服务架构：
- **OnlineSubsystem（OSSv1）**：旧系统，基于 `IOnlineSubsystem` 接口和 `FUniqueNetId`，各平台（Steam、EOS、PlayStation、Xbox 等）都有对应的 OSS 实现
- **OnlineServices（V2）**：新系统，基于 `IOnlineServices` 接口和 `FAccountId`/`TOnlineId`，使用 async op chain 模式

这个 Adapter 插件将 V1 的 `IOnlineSubsystem` 接口逐一包装成 V2 的 `IOnlineServices` 组件（Auth、Sessions、Social、Stats 等），使得游戏代码可以使用新的 V2 API，而底层实际调用的是平台已有的 V1 实现。这样各平台无需重新实现 V2 后端，即可被 V2 API 使用。

**关键设计模式**：每个 Adapter 类继承对应的 `Common` 基类（如 `FAuthCommon`），在 `PostInitialize` 中获取 V1 接口指针，然后在各虚函数中将 V2 参数转换为 V1 调用，再将 V1 结果转换回 V2 类型。

## 使用场景

- 你的项目已经在使用 V2 `OnlineServices` API（如 `Auth->Login()`、`Sessions->FindSessions()`），但平台后端只有 V1 `OnlineSubsystem` 实现 → 启用此 Adapter，V2 API 自动通过 Adapter 调用到 V1 后端
- 你正在从 V1 迁移到 V2 API，需要一个过渡方案 → 启用此 Adapter，逐步将代码从 V1 调用改为 V2 调用
- 你使用 EOS（Epic Online Services）或 Steam 等已有成熟 V1 实现的平台 → 此 Adapter 让你无需等待 V2 原生实现即可使用 V2 API

**注意**：此插件默认禁用（`EnabledByDefault: false`），需要在项目设置或 `.uproject` 中手动启用。

## 蓝图用法

此插件不暴露任何 Blueprint 节点。它是纯 C++ 运行时模块，供引擎内部和 C++ 项目使用。V2 OnlineServices 的蓝图节点（如通过 `OnlineServicesSubsystem` 暴露的节点）在底层会通过此 Adapter 自动路由到 V1 实现。

## C++ 用法

### 头文件引入

```cpp
// 主要入口类
#include "Online/OnlineServicesOSSAdapter.h"

// 各子系统适配器（通常不需要直接引用，通过 OnlineServices 接口使用）
#include "Online/AuthOSSAdapter.h"
#include "Online/SessionsOSSAdapter.h"
#include "Online/SocialOSSAdapter.h"
```

### 基本用法

OnlineServicesOSSAdapter 不需要你直接调用它的类。启用后，它会自动注册到 `OnlineServicesRegistry`，当你通过 V2 API 获取 `IOnlineServices` 实例时，如果匹配的 OSSv1 后端存在，返回的就是 `FOnlineServicesOSSAdapter` 实例。

```cpp
// 获取 V2 OnlineServices 实例（配置正确时自动返回 OSSAdapter 包装的实例）
IOnlineServicesPtr OnlineServices = OnlineServices::Get();
if (OnlineServices)
{
    // 这些 V2 调用在 OSSAdapter 后端下会自动路由到 V1 实现
    IAuthPtr Auth = OnlineServices->GetAuthInterface();
    TOnlineAsyncOpHandle<FAuthLogin> Handle = Auth->Login(FAuthLogin::Params{
        PlatformUserId,
        LoginCredentialsType::Auto
    });
}
```

配置方式（`DefaultEngine.ini`）：

```ini
[OnlineServices.OSSAdapter]
+Services=(Service="Default",ConfigName="Default",OnlineSubsystem="Steam",Priority=0)
```

这段配置告诉引擎：对于 `Default` 服务类型，使用名为 `Steam` 的 OSSv1 后端，优先级为 0。

### 进阶用法

#### ID 转换（OnlineIdOSSAdapter）

Adapter 内部使用 `TOnlineUniqueNetIdRegistry` 将 V1 的 `FUniqueNetIdRef` 映射为 V2 的 `TOnlineId<>`（handle 模式）。这个注册表是双向的：

```cpp
// 从 FUniqueNetIdRef 获取 V2 AccountId
FOnlineAccountIdRegistryOSSAdapter& Registry = Adapter.GetAccountIdRegistry();
FAccountId AccountId = Registry.FindOrAddHandle(UniqueNetIdRef);

// 从 AccountId 回查 FUniqueNetIdRef
FUniqueNetIdPtr NetId = Registry.GetIdValue(AccountId);
```

#### Delegate Adapter 模式

插件内部大量使用 `MakeDelegateAdapter` 和 `MakeMulticastAdapter` 来安全地绑定 V1 异步回调：

```cpp
// DelegateAdapter：绑定单次回调，自动做 weak ptr 检查
Identity->GetAuthToken(LocalUserNum,
    *MakeDelegateAdapter(this, [this](int32 UserNum, FString LoginToken) { ... }));

// MulticastAdapter：绑定到多播委托，lambda 返回 void 则单次执行后自动解绑
MakeMulticastAdapter(this, Identity->OnLoginCompleteDelegates[0],
    [this](int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error) { ... });
```

## Demo 示例

### 配置 OnlineServicesOSSAdapter

最典型的使用场景是配置文件层面的设置，让 V2 API 自动通过 Adapter 路由到 V1 后端：

```cpp
// DefaultEngine.ini 中配置（无需 C++ 代码）
// [OnlineSubsystem.Steam]
// bEnabled=true
//
// [OnlineServices.OSSAdapter]
// +Services=(Service="Default",ConfigName="Default",OnlineSubsystem="Steam",Priority=0)
```

### 在 C++ 中使用 V2 API（底层走 OSSAdapter）

```cpp
// MyGameModule.h
#pragma once
#include "CoreMinimal.h"
#include "Modules/ModuleManager.h"

// MyGameModule.cpp
#include "Online/OnlineServices.h"
#include "Online/Auth.h"

void FMyGameModule::LoginToPlatform()
{
    using namespace UE::Online;

    IOnlineServicesPtr OnlineServices = OnlineServices::Get();
    if (!OnlineServices)
    {
        UE_LOG(LogTemp, Error, TEXT("No online services available"));
        return;
    }

    IAuthPtr Auth = OnlineServices->GetAuthInterface();
    if (!Auth)
    {
        UE_LOG(LogTemp, Error, TEXT("No auth interface available"));
        return;
    }

    // V2 Login — 底层通过 OSSAdapter 调用到 V1 IOnlineIdentity::Login()
    Auth->Login(FAuthLogin::Params{
        FPlatformMisc::GetPlatformUserForUserIndex(0),
        LoginCredentialsType::Auto
    }).OnComplete([](TOnlineResult<FAuthLogin> Result)
    {
        if (Result.IsOk())
        {
            UE_LOG(LogTemp, Log, TEXT("Login successful! AccountId: %s"),
                *ToLogString(Result.GetOkValue().AccountInfo->AccountId));
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Login failed: %s"),
                *Result.GetErrorValue().GetLogString());
        }
    });
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "OnlineServicesInterface",  // V2 接口定义
    "OnlineSubsystem",          // V1 接口（如果需要直接使用 V1 类型）
});
```

## 模块依赖

从 `OnlineServicesOSSAdapter.Build.cs` 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `OnlineServicesInterface` | V2 OnlineServices 接口定义（IAuth、ISessions 等） |
| `OnlineServicesCommon` | V2 OnlineServices 通用基类实现（FAuthCommon、FSessionsCommon 等） |
| `OnlineSubsystem` | V1 OnlineSubsystem 接口定义（IOnlineSubsystem、IOnlineIdentity 等） |
| `Json` | JSON 序列化支持 |

从 `PrivateDependencyModuleNames`：

| 模块 | 用途 |
|---|---|
| `CoreOnline` | 在线核心类型（FUniqueNetId 等） |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `OnlineServices` | V2 OnlineServices 框架 |
| `OnlineSubsystem` | V1 OnlineSubsystem 框架 |

## 架构总览

### 模块注册流程

```
FOnlineServicesOSSAdapterModule::StartupModule()
  ├── 从 GEngineIni 读取 [OnlineServices.OSSAdapter] 配置
  ├── 对每个配置的 Service：
  │   ├── 检查对应 OSSv1 是否启用 (IOnlineSubsystem::IsEnabled)
  │   ├── 注册 FOnlineServicesFactoryOSSAdapter → OnlineServicesRegistry
  │   ├── 注册 FOnlineAccountIdRegistryOSSAdapter → OnlineIdRegistryRegistry
  │   ├── 注册 FOnlineSessionIdRegistryOSSAdapter → OnlineIdRegistryRegistry
  │   └── 注册 FOnlineSessionInviteIdRegistryOSSAdapter → OnlineIdRegistryRegistry
```

### 组件注册流程

```
FOnlineServicesOSSAdapter::RegisterComponents()
  ├── FAuthOSSAdapter          (始终注册)
  ├── FConnectivityOSSAdapter  (始终注册)
  ├── FPresenceOSSAdapter      (始终注册)
  ├── FPrivilegesOSSAdapter    (始终注册)
  ├── FLeaderboardsOSSAdapter  (如果 OSSv1 有 Leaderboards 接口)
  ├── FStatsOSSAdapter         (如果 OSSv1 有 Stats 接口)
  ├── FSocialOSSAdapter        (如果 OSSv1 有 Friends 接口)
  ├── FSessionsOSSAdapter      (如果 OSSv1 有 Session 接口)
  ├── FAchievementsOSSAdapter  (如果 OSSv1 有 Achievements 接口)
  ├── FExternalUIOSSAdapter    (如果 OSSv1 有 ExternalUI 接口)
  ├── FTitleFileOSSAdapter     (如果 OSSv1 有 TitleFile 接口)
  ├── FUserFileOSSAdapter      (如果 OSSv1 有 UserCloud 接口)
  ├── FUserInfoOSSAdapter      (如果 OSSv1 有 User 接口)
  └── FCommerceOSSAdapter      (如果 OSSv1 有 Purchase + StoreV2 接口)
```

### 适配器一览

| V2 适配器类 | V1 接口 | V2 功能 |
|---|---|---|
| `FAuthOSSAdapter` | `IOnlineIdentity` | 登录/登出、外部 Auth Token 查询 |
| `FConnectivityOSSAdapter` | `IOnlineIdentity` | 连接状态监控 |
| `FPresenceOSSAdapter` | `IOnlinePresence` | 在线状态查询/更新 |
| `FPrivilegesOSSAdapter` | `IOnlineIdentity` | 用户权限查询 |
| `FSessionsOSSAdapter` | `IOnlineSession` | 会话创建/查找/加入/离开 |
| `FSocialOSSAdapter` | `IOnlineFriends` | 好友列表、邀请、屏蔽 |
| `FStatsOSSAdapter` | `IOnlineStats` | 统计数据查询/更新 |
| `FLeaderboardsOSSAdapter` | `IOnlineLeaderboards` | 排行榜读取 |
| `FAchievementsOSSAdapter` | `IOnlineAchievements` | 成就定义/状态查询 |
| `FCommerceOSSAdapter` | `IOnlinePurchase` + `IOnlineStoreV2` | 商店、购买、权益 |
| `FExternalUIOSSAdapter` | `IOnlineExternalUI` | 登录 UI、好友 UI |
| `FTitleFileOSSAdapter` | `IOnlineTitleFile` | 服务端文件枚举/读取 |
| `FUserFileOSSAdapter` | `IOnlineUserCloud` | 用户云存档读写 |
| `FUserInfoOSSAdapter` | `IOnlineUser` | 用户信息查询 |

## 模块依赖图

```
OnlineServicesOSSAdapter
├── OnlineServicesInterface   (V2 接口)
│   └── OnlineServicesCommon  (V2 基类)
├── OnlineSubsystem           (V1 接口)
│   └── CoreOnline            (FUniqueNetId)
├── Core
└── Json
```

## 维护状态

### 近期更新

```
9e6ad26 | 2025-08-26 | Add ToAccountId and FromStringData to the ID registry
    为 ID 注册表添加了字符串到 AccountId 的转换支持，增强 ID 系统的互操作性。

bb7ebae | 2025-08-05 | Added support to TNestedVariant in related usage by Presence prototype changes
    Presence 系统的原型变更支持，涉及 TNestedVariant 的使用。

2adf7d9 | 2025-07-24 | OnlineServices Presence and DisplayName related changes
    Presence 和 DisplayName 相关的在线服务变更。
```

### 维护评价

**活跃维护**。此插件由 Epic Games 核心在线服务团队维护，最近 6 个月内有多次功能性更新（ID 注册表增强、Presence 原型变更等）。作为 UE5 在线服务架构迁移的关键桥梁层，它与 OnlineServices 和 OnlineSubsystem 两个核心系统紧密耦合，会随着这两个系统的演进而持续更新。

**使用建议**：
- 如果你的项目使用 V2 OnlineServices API 且目标平台有成熟的 V1 OSS 实现，推荐启用此插件
- 如果你的平台已有 V2 原生实现（如 EOS 的 V2 后端），则不需要此 Adapter
- 注意此插件默认禁用，需要手动启用并配置 `OnlineServices.OSSAdapter` 段

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesOSSAdapter)
- [OnlineServices 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
- [OnlineSubsystem 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystem)
