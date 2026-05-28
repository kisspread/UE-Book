# Online Services

> Shared code for interacting with online services implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线服务 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesInterface` (Runtime), `OnlineServicesCommon` (Runtime), `OnlineServicesCommonEngineUtils` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices) | |

## 用途

Online Services 是 UE5 中**新一代在线子系统的底层框架**，用于替代传统的 `OnlineSubsystem`（OSS v1）。它为所有在线平台服务（Epic Online Services、Steam、PlayStation Network、Xbox Live 等）提供统一的 C++ 接口层和通用实现基类。

这个插件**本身不包含任何具体平台实现**，而是定义了一套架构：

- **接口层**（`OnlineServicesInterface`）：定义所有在线服务接口（Auth、Sessions、Lobbies 等）的纯虚接口
- **通用实现层**（`OnlineServicesCommon`）：提供各接口的通用基类，包含异步操作管理、配置加载、控制台命令等基础设施
- **引擎工具层**（`OnlineServicesCommonEngineUtils`）：与 UE 引擎系统的集成工具

### 与 OnlineSubsystem 的关系

Online Services 是 OSS v1 的继任者。两者的主要区别：

| 特性 | OnlineSubsystem (v1) | Online Services (v2) |
|---|---|---|
| 命名空间 | `IOnlineSubsystem` | `UE::Online` |
| 异步模型 | `FOnlineAsyncTask` | `TOnlineAsyncOp`（支持链式操作、Promise） |
| 配置系统 | 基于 UObjects | `IOnlineConfigProvider`（更灵活） |
| ID 系统 | `FUniqueNetId` | `TOnlineId<T>`（类型安全） |
| 错误处理 | `FOnlineError` | `TOnlineResult<OpType>`（类型安全的结果） |
| 组件化 | 整个子系统是一个类 | `TOnlineComponent` 组件模式 |

## 使用场景

- 你正在开发多人在线游戏，需要跨平台登录、配对、大厅等功能 → 使用此插件作为框架，配合具体平台插件（如 `OnlineServicesEOS`）
- 你需要自定义在线服务的缓存策略或配置系统 → 继承 `FOnlineAsyncOpCache` 或 `IOnlineConfigProvider`
- 你正在实现一个新的在线服务平台适配器 → 继承 `FOnlineServicesCommon` 和各接口的 `Common` 基类
- 你需要异步操作的链式执行、串行队列、合并/去重功能 → 使用 `TOnlineAsyncOp` + `FOnlineAsyncOpQueue`

## 蓝图用法

此插件主要面向 C++ 开发者，**不直接暴露蓝图节点**。在线服务功能需要通过具体平台实现插件（如 EOS、Null 等）的蓝图集成层访问。

开发者可以通过**控制台命令**在运行时测试在线服务功能：

```
OnlineServices Index=0 Auth Login Null
OnlineServices Index=0 Presence UpdatePresence 0
OnlineServices Index=0 Lobbies CreateLobby
OnlineServices Index=0 Sessions FindSessions
```

控制台命令语法：
- `OnlineServices` 前缀
- `Index=#` 指定服务实例
- 第二个参数是接口名（Auth、Presence、Lobbies、Sessions 等）
- 第三个参数是操作名
- 后续参数按操作参数顺序传入

## C++ 用法

### 头文件引入

```cpp
// 在线服务核心
#include "Online/OnlineServicesCommon.h"

// 各接口（按需引入）
#include "Online/AuthCommon.h"
#include "Online/SessionsCommon.h"
#include "Online/LobbiesCommon.h"
#include "Online/SocialCommon.h"
#include "Online/PresenceCommon.h"
#include "Online/StatsCommon.h"
#include "Online/LeaderboardsCommon.h"
#include "Online/AchievementsCommon.h"
#include "Online/CommerceCommon.h"

// 异步操作（自动包含，但显式引入更清晰）
#include "Online/OnlineAsyncOp.h"
#include "Online/OnlineAsyncOpQueue.h"
#include "Online/OnlineAsyncOpCache.h"

// 配置系统
#include "Online/OnlineConfig.h"
```

### 基本用法：获取在线服务实例

```cpp
#include "Online/OnlineServicesCommon.h"

using namespace UE::Online;

// 获取在线服务实例（通过引擎子系统）
IOnlineServicesPtr OnlineServices = Online::GetServices(0);
if (OnlineServices)
{
    // 获取认证接口
    IAuthPtr Auth = OnlineServices->GetAuthInterface();
    if (Auth)
    {
        // 执行登录
        FAuthLogin::Params LoginParams;
        LoginParams.LocalAccountId = FPlatformUserId(0);
        
        Auth->Login(MoveTemp(LoginParams))
        .Then([](TOnlineAsyncOpRef<FAuthLogin> Op)
        {
            if (Op->GetResult().IsOk())
            {
                UE_LOG(LogTemp, Log, TEXT("Login successful!"));
            }
            else
            {
                UE_LOG(LogTemp, Error, TEXT("Login failed: %s"), 
                    *Op->GetResult().GetErrorValue().GetLogMessage());
            }
        });
    }
}
```

### 基本用法：大厅（Lobbies）

```cpp
#include "Online/LobbiesCommon.h"

using namespace UE::Online;

ILobbiesPtr Lobbies = OnlineServices->GetLobbiesInterface();

// 创建大厅
FCreateLobby::Params CreateParams;
CreateParams.LocalAccountId = MyAccountId;
CreateParams.MaxMembers = 8;
CreateParams.JoinPolicy = ELobbyJoinPolicy::PublicAdvertised;

Lobbies->CreateLobby(MoveTemp(CreateParams))
.Then([Lobbies](TOnlineAsyncOpRef<FCreateLobby> Op)
{
    if (Op->GetResult().IsOk())
    {
        TSharedRef<const FLobby> Lobby = Op->GetResult().GetOkValue().Lobby;
        UE_LOG(LogTemp, Log, TEXT("Lobby created: %s"), *Lobby->LobbyId.ToString());
        
        // 监听大厅事件
        Lobbies->OnLobbyMemberJoined().Add(
            [](const FLobbyMemberJoined& Event)
            {
                UE_LOG(LogTemp, Log, TEXT("Member joined lobby"));
            });
    }
});
```

### 基本用法：会话（Sessions）

```cpp
#include "Online/SessionsCommon.h"

using namespace UE::Online;

ISessionsPtr Sessions = OnlineServices->GetSessionsInterface();

// 创建会话
FCreateSession::Params SessionParams;
SessionParams.LocalAccountId = MyAccountId;
SessionParams.SessionName = FName("MyGameSession");
SessionParams.SessionSettings.NumMaxConnections = 16;
SessionParams.SessionSettings.bAllowNewMembers = true;

Sessions->CreateSession(MoveTemp(SessionParams))
.Then([](TOnlineAsyncOpRef<FCreateSession> Op)
{
    if (Op->GetResult().IsOk())
    {
        TSharedRef<const ISession> Session = Op->GetResult().GetOkValue().Session;
        UE_LOG(LogTemp, Log, TEXT("Session created!"));
    }
});

// 查找会话
FFindSessions::Params FindParams;
FindParams.LocalAccountId = MyAccountId;
FindParams.MaxResults = 10;

Sessions->FindSessions(MoveTemp(FindParams))
.Then([](TOnlineAsyncOpRef<FFindSessions> Op)
{
    if (Op->GetResult().IsOk())
    {
        const FFindSessions::Result& Result = Op->GetResult().GetOkValue();
        for (const TSharedRef<const ISearchResult>& SearchResult : Result.SearchResults)
        {
            UE_LOG(LogTemp, Log, TEXT("Found session: %s"),
                *SearchResult->GetSessionInfo().SessionId.ToString());
        }
    }
});
```

### 进阶用法：异步操作缓存（Joinable & Mergeable）

```cpp
#include "Online/OnlineAsyncOpCache.h"

// 同一参数的查询操作会被自动合并，避免重复请求
// TOnlineComponent::GetJoinableOp 会：
//   1. 如果已有相同参数的进行中操作 → 复用（Join）
//   2. 如果有未过期的缓存结果 → 直接返回缓存
//   3. 否则创建新操作

// Mergeable 操作会将多个相同参数的请求合并为一次
// 例如批量修改大厅属性时，多次 ModifyLobbyAttributes 调用会被合并
```

### 进阶用法：配置系统

```cpp
#include "Online/OnlineConfig.h"

// 配置节的层级结构（从通用到具体）：
// OnlineServices
// OnlineServices.<ServiceProvider>
// OnlineServices.<ServiceProvider>.<InterfaceName>
// OnlineServices.<ServiceProvider>.<InterfaceName>.<OperationName>

// 在 DefaultEngine.ini 中配置：
// [OnlineServices]
// CacheExpiration=Duration
// 
// [OnlineServices.Null.Auth.Login]
// MaxRetries=3
```

### 进阶用法：自定义在线服务平台适配器

```cpp
#include "Online/OnlineServicesCommon.h"

// 自定义在线服务实现
class FOnlineServicesMyPlatform : public FOnlineServicesCommon
{
public:
    FOnlineServicesMyPlatform(const FString& InServiceConfigName, 
                              FName InInstanceName,
                              FName InInstanceConfigName)
        : FOnlineServicesCommon(InServiceConfigName, InInstanceName, InInstanceConfigName)
    {
    }

    virtual void RegisterComponents() override
    {
        // 注册自定义组件
        Components.Register<FMyAuth>(TEXT("Auth"), *this);
        Components.Register<FMySessions>(TEXT("Sessions"), *this);
        Components.Register<FMyLobbies>(TEXT("Lobbies"), *this);
        // ... 其他接口
    }
};

// 自定义认证组件
class FMyAuth : public FAuthCommon
{
public:
    FMyAuth(FOnlineServicesCommon& InServices)
        : FAuthCommon(InServices)
    {
    }

    virtual TOnlineAsyncOpHandle<FAuthLogin> Login(FAuthLogin::Params&& Params) override
    {
        TOnlineAsyncOpRef<FAuthLogin> Op = GetOp<FAuthLogin>(MoveTemp(Params));
        
        Op->Then([this](TOnlineAsyncOp<FAuthLogin>& Op)
        {
            // 实现平台特定的登录逻辑
            // ...
            Op.Complete(FAuthLogin::Result());
        });
        
        return Op->GetHandle();
    }
};
```

## Demo 示例

```cpp
// MyOnlineServicesModule.h
#pragma once

#include "Modules/ModuleManager.h"

class FMyOnlineServicesModule : public IModuleInterface
{
public:
    virtual void StartupModule() override;
    virtual void ShutdownModule() override;
};

// MyOnlineServicesModule.cpp
#include "MyOnlineServicesModule.h"
#include "Online/OnlineServicesCommon.h"

void FMyOnlineServicesModule::StartupModule()
{
    // 注册自定义在线服务
    UE::Online::FOnlineServicesFactory::Register(
        UE::Online::EOnlineServices::Null,
        [](const FString& ConfigName, FName InstanceName, FName InstanceConfigName)
        {
            return MakeShared<UE::Online::FOnlineServicesCommon>(
                ConfigName, InstanceName, InstanceConfigName);
        });
}

void FMyOnlineServicesModule::ShutdownModule()
{
}

IMPLEMENT_MODULE(FMyOnlineServicesModule, MyOnlineServices)
```

```cpp
// MyGameOnlineManager.h
#pragma once

#include "Online/OnlineServicesCommon.h"

class FMyGameOnlineManager
{
public:
    void Initialize(UE::Online::IOnlineServicesPtr OnlineServices);
    void Login(const FPlatformUserId& PlatformUserId);
    void CreateLobby(int32 MaxMembers);
    void FindLobbies();
    
    DECLARE_EVENT_OneParam(FMyGameOnlineManager, FOnLoginComplete, bool /* bSuccess */)
    FOnLoginComplete OnLoginComplete;

private:
    UE::Online::IOnlineServicesPtr OnlineServices;
    UE::Online::FAccountId LocalAccountId;
};
```

```cpp
// MyGameOnlineManager.cpp
#include "MyGameOnlineManager.h"

using namespace UE::Online;

void FMyGameOnlineManager::Initialize(IOnlineServicesPtr InOnlineServices)
{
    OnlineServices = InOnlineServices;
}

void FMyGameOnlineManager::Login(const FPlatformUserId& PlatformUserId)
{
    IAuthPtr Auth = OnlineServices->GetAuthInterface();
    if (!Auth) return;

    FAuthLogin::Params Params;
    Params.LocalAccountId = FAccountId(); // 会由具体实现解析

    Auth->Login(MoveTemp(Params))
    .Then([this](TOnlineAsyncOpRef<FAuthLogin> Op)
    {
        if (Op->GetResult().IsOk())
        {
            LocalAccountId = Op->GetResult().GetOkValue().AccountInfo->AccountId;
            OnLoginComplete.Broadcast(true);
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Login failed: %s"),
                *Op->GetResult().GetErrorValue().GetLogMessage());
            OnLoginComplete.Broadcast(false);
        }
    });
}

void FMyGameOnlineManager::CreateLobby(int32 MaxMembers)
{
    ILobbiesPtr Lobbies = OnlineServices->GetLobbiesInterface();
    if (!Lobbies) return;

    FCreateLobby::Params Params;
    Params.LocalAccountId = LocalAccountId;
    Params.MaxMembers = MaxMembers;
    Params.JoinPolicy = ELobbyJoinPolicy::FriendsOnly;

    Lobbies->CreateLobby(MoveTemp(Params))
    .Then([](TOnlineAsyncOpRef<FCreateLobby> Op)
    {
        if (Op->GetResult().IsOk())
        {
            TSharedRef<const FLobby> Lobby = Op->GetResult().GetOkValue().Lobby;
            UE_LOG(LogTemp, Log, TEXT("Created lobby: %s"), *Lobby->LobbyId.ToString());
        }
    });
}

void FMyGameOnlineManager::FindLobbies()
{
    ILobbiesPtr Lobbies = OnlineServices->GetLobbiesInterface();
    if (!Lobbies) return;

    FFindLobbies::Params Params;
    Params.LocalAccountId = LocalAccountId;

    Lobbies->FindLobbies(MoveTemp(Params))
    .Then([](TOnlineAsyncOpRef<FFindLobbies> Op)
    {
        if (Op->GetResult().IsOk())
        {
            const FFindLobbies::Result& Result = Op->GetResult().GetOkValue();
            for (const TSharedRef<const FLobbySearchResult>& SearchResult : Result.LobbySearchResults)
            {
                UE_LOG(LogTemp, Log, TEXT("Found lobby: max=%d, members=%d"),
                    SearchResult->Lobby->MaxMembers,
                    SearchResult->Lobby->Members.Num());
            }
        }
    });
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineBase` | 基础在线类型定义（OnlineId、OnlineError、Schema 等） |
| `OnlineSubsystemUtils` | 传统 OSS 工具模块（兼容性） |

## 架构概览

### 核心类关系图

```
IOnlineServices (接口)
    └── FOnlineServicesCommon (通用实现基类)
            ├── FOnlineComponentRegistry (组件注册表)
            │       ├── IOnlineComponent
            │       │       ├── FAuthCommon → IAuth
            │       │       ├── FSessionsCommon → ISessions
            │       │       ├── FLobbiesCommon → ILobbies
            │       │       ├── FSocialCommon → ISocial
            │       │       ├── FPresenceCommon → IPresence
            │       │       ├── FStatsCommon → IStats
            │       │       ├── FLeaderboardsCommon → ILeaderboards
            │       │       ├── FAchievementsCommon → IAchievements
            │       │       ├── FCommerceCommon → ICommerce
            │       │       ├── FExternalUICommon → IExternalUI
            │       │       ├── FUserInfoCommon → IUserInfo
            │       │       ├── FConnectivityCommon → IConnectivity
            │       │       ├── FPrivilegesCommon → IPrivileges
            │       │       ├── FTitleFileCommon → ITitleFile
            │       │       └── FUserFileCommon → IUserFile
            │       └── (具体平台插件添加自己的组件)
            └── FOnlineAsyncOpCache (异步操作缓存)
```

### 异步操作流程

```
用户代码 → GetOp<OpType>(Params)
               ↓
       FOnlineAsyncOpCache (去重/缓存/合并)
               ↓
       TOnlineAsyncOp<OpType> (操作对象)
               ↓
       Step 1 → Step 2 → Step 3 (链式执行)
               ↓
       OnComplete 回调
```

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的警告 |
| 2026-05-12 | `4ad1dbcc` | [OnlineSubsystem][OnlineServices] Guard SetPort callers against bogus port values from EOS:\<PUID\> ad | 防御 EOS 返回异常端口值导致的崩溃 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配问题 |
| 2026-04-14 | `2c013d6c` | Online Services EOS Presence Refactor: | EOS Presence 接口重大重构 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 日志宏 |

### 维护评价

**活跃维护中** ✅

- 该插件自 2022 年从 Experimental 移出后持续开发，是 UE5 在线功能的未来方向
- 最近更新（2026 年 5 月）仍在活跃进行，包含代码质量改进、EOS 适配优化和 Presence 功能重构
- 作为 `OnlineSubsystem` 的替代方案，Epic Games 正在积极将各平台实现迁移到此架构
- 该插件默认不启用（`EnabledByDefault: false`），需要手动启用
- **推荐使用**：对于新项目，建议基于此框架开发，而非使用已逐渐废弃的 OnlineSubsystem

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineServices)
- [OnlineBase 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineBase)（基础类型定义）