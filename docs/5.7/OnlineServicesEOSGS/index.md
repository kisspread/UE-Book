# Online Services EOS (Game Services)

> Online Services implementation for EOS Game services only.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesEOSGS` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOSGS) | |

## 用途

OnlineServicesEOSGS 是 UE5 新一代 Online Services 框架针对 **Epic Online Services (EOS) Game Services** 的具体实现插件。它继承自 `OnlineServicesEpicCommon`，将 UE 的通用在线服务接口（IAuth、ISessions、ILobbies 等）适配到 EOS SDK 的 Game Services 层。

**为什么存在？** UE5 引入了全新的模块化在线服务架构（`UE::Online`），替代了旧的 `IOnlineSubsystem` 体系。EOS 作为 Epic 自家的在线服务平台，需要两个独立的实现插件：
- **OnlineServicesEOSGS**（本插件）：Game Services — 面向游戏客户端/服务器的在线功能（认证、会话、大厅、成就、排行榜、存储等）
- **OnlineServicesEOS**（另一个插件）：Account Services — 面向账户管理的更底层服务

本插件专注于游戏运行时所需的全部在线功能，是使用 EOS 作为后端时最常用的插件。

### 与旧 OnlineSubsystemEOS 的关系

本插件属于 UE5 新的 `UE::Online` 命名空间下的模块化在线服务系统，与旧的 `OnlineSubsystemEOS` 并行存在。新项目推荐使用本插件而非旧的子系统。

## 使用场景

- 你正在开发一款需要 Epic Games Store 在线功能的多人游戏 → 使用本插件
- 你需要 EOS 提供的跨平台会话匹配（Sessions）和大厅（Lobbies）功能 → 使用本插件
- 你需要 EOS 的成就、排行榜、玩家举报/制裁系统 → 使用本插件
- 你需要 EOS 的 Title Storage / Player Data Storage 云存储 → 使用本插件
- 你只想用 EOS 做基础认证而不需要 Game Services → 考虑 `OnlineServicesEOS` 或直接使用 `EOSShared`

## 蓝图用法

本插件没有暴露任何 `BlueprintCallable` 函数。它是一个纯 C++ 运行时模块，所有在线服务接口通过 `UE::Online` 命名空间下的 C++ API 访问。

如需在蓝图中使用 EOS 在线功能，需要通过其他蓝图友好的包装层（如 OnlineSubsystem 桥接或自定义蓝图节点）。

## C++ 用法

### 架构概览

本插件通过 `FOnlineServicesEOSGS` 类注册以下在线服务组件（Components）：

| 组件 | 类名 | EOS 接口 | 功能 |
|---|---|---|---|
| Auth | `FAuthEOSGS` | Auth + Connect | 用户认证、登录/登出 |
| Sessions | `FSessionsEOSGS` | Sessions | 会话创建/搜索/加入 |
| Lobbies | `FLobbiesEOSGS` | Lobby | 大厅管理 |
| Achievements | `FAchievementsEOSGS` | Achievements | 成就查询/解锁 |
| Leaderboards | `FLeaderboardsEOSGS` | Leaderboards | 排行榜查询 |
| Stats | `FStatsEOSGS` | Stats | 统计数据更新/查询 |
| TitleFile | `FTitleFileEOSGS` | TitleStorage | 标题文件存储 |
| UserFile | `FUserFileEOSGS` | PlayerDataStorage | 玩家数据存储 |
| PlayerReports | `FPlayerReportsEOSGS` | Reports | 玩家举报 |
| PlayerSanctions | `FPlayerSanctionsEOSGS` | Sanctions | 制裁查询/申诉 |
| ExternalUI | `FExternalUIEOSGS` | UI | Epic 覆盖层 UI |
| ProductUserIdResolver | `FEpicProductUserIdResolverEOSGS` | Connect | ProductUserId 解析 |

### 头文件引入

```cpp
#include "Online/OnlineServicesEOSGS.h"
```

### 基本用法 — 获取在线服务实例

```cpp
#include "Online/OnlineServicesSubsystem.h"
#include "Online/OnlineServicesEOSGS.h"

// 通过 Subsystem 获取 EOS Game Services 实例
UE::Online::IOnlineServicesPtr OnlineServices = UE::Online::GetServices(UE::Online::EOnlineServices::Epic);
```

### 认证 (Auth)

```cpp
using namespace UE::Online;

// 登录
TOnlineAsyncOpHandle<FAuthLogin> LoginHandle = OnlineServices->GetAuthInterface()->Login({
    .PlatformUserId = PlatformUserId,
    .CredentialsType = FAuthCredentialsType::ExchangeCode,
    .CredentialsId = TEXT(""),
    .CredentialsToken = ExchangeCodeToken
});

LoginHandle->OnComplete([](const TOnlineResult<FAuthLogin>& Result)
{
    if (Result.IsOk())
    {
        FAccountId AccountId = Result.GetOkValue().AccountInfo->AccountId;
        // 登录成功
    }
});
```

**来源**: `AuthEOSGS.h` — `FAuthEOSGS` 实现了两阶段登录流程：先通过 EOS Auth (EAS) 登录 Epic 账户，再通过 EOS Connect 获取 ProductUserId。

### 会话 (Sessions)

```cpp
using namespace UE::Online;

// 创建会话
TOnlineAsyncOpHandle<FCreateSession> CreateHandle = OnlineServices->GetSessionsInterface()->CreateSession({
    .LocalAccountId = AccountId,
    .SessionName = FName(TEXT("GameSession")),
    .SessionSettings = {
        .NumMaxConnections = 10,
        .bAllowJoinInProgress = true,
        .JoinPolicy = ESessionJoinPolicy::PublicAdvertised
    }
});

// 搜索会话
TOnlineAsyncOpHandle<FFindSessions> FindHandle = OnlineServices->GetSessionsInterface()->FindSessions({
    .LocalAccountId = AccountId,
    .MaxResults = 10
});
```

**来源**: `SessionsEOSGS.h` — `FSessionsEOSGS` 继承自 `FSessionsLAN`，增加了 EOS 特有的会话属性（BucketId、HostAddress 等）和邀请处理。

### 大厅 (Lobbies)

```cpp
using namespace UE::Online;

// 创建大厅
TOnlineAsyncOpHandle<FCreateLobby> LobbyHandle = OnlineServices->GetLobbiesInterface()->CreateLobby({
    .LocalAccountId = AccountId,
    .MaxMembers = 4,
    .JoinPolicy = ELobbyJoinPolicy::PublicAdvertised
});

// 查找大厅
TOnlineAsyncOpHandle<FFindLobbies> FindLobbyHandle = OnlineServices->GetLobbiesInterface()->FindLobbies({
    .LocalAccountId = AccountId
});
```

**来源**: `LobbiesEOSGS.h` — `FLobbiesEOSGS` 提供完整的大厅生命周期管理，包括创建、查找、加入、离开、邀请、踢人、提升拥有者等。

### 成就 (Achievements)

```cpp
using namespace UE::Online;

// 查询成就定义
TOnlineAsyncOpHandle<FQueryAchievementDefinitions> DefHandle =
    OnlineServices->GetAchievementsInterface()->QueryAchievementDefinitions({ .LocalAccountId = AccountId });

// 解锁成就
TOnlineAsyncOpHandle<FUnlockAchievements> UnlockHandle =
    OnlineServices->GetAchievementsInterface()->UnlockAchievements({
        .LocalAccountId = AccountId,
        .AchievementIds = { TEXT("ACH_WIN_10_GAMES") }
    });
```

### 玩家举报 (Player Reports) — EOSGS 独有接口

```cpp
using namespace UE::Online;

// 获取 EOSGS 特有的 Player Reports 接口
FOnlineServicesEOSGS* EOSGSServices = static_cast<FOnlineServicesEOSGS*>(OnlineServices.Get());
IPlayerReportsPtr ReportsInterface = EOSGSServices->GetPlayerReportsInterface();

TOnlineAsyncOpHandle<FSendPlayerReport> ReportHandle = ReportsInterface->SendPlayerReport({
    .LocalAccountId = LocalAccountId,
    .TargetAccountId = TargetAccountId,
    .Category = EPlayerReportCategory::Cheating,
    .Message = TEXT("使用外挂"),
    .Context = TEXT("{\"gameMode\":\"ranked\",\"map\":\"test\"}")
});
```

**来源**: `OnlineServicesEOSGSInterfaces/PlayerReports.h` — `IPlayerReports` 是 EOSGS 独有的接口，不在通用 `UE::Online` 接口中，需要通过 `FOnlineServicesEOSGS` 的专用方法获取。

### 玩家制裁 (Player Sanctions) — EOSGS 独有接口

```cpp
using namespace UE::Online;

IPlayerSanctionsPtr SanctionsInterface = EOSGSServices->GetPlayerSanctionsInterface();

// 查询当前有效制裁
TOnlineAsyncOpHandle<FReadActivePlayerSanctions> SanctionsHandle =
    SanctionsInterface->ReadEntriesForUser({
        .LocalAccountId = LocalAccountId,
        .TargetAccountId = TargetAccountId
    });

// 提交制裁申诉
TOnlineAsyncOpHandle<FCreatePlayerSanctionAppeal> AppealHandle =
    SanctionsInterface->CreatePlayerSanctionAppeal({
        .LocalAccountId = LocalAccountId,
        .Reason = EPlayerSanctionAppealReason::IncorrectSanction,
        .ReferenceId = TEXT("sanction-id-123")
    });
```

### ID 系统

EOS 使用双重 ID 系统：
- **EpicAccountId** — Epic Games Store 账户 ID（用于社交功能）
- **ProductUserId** — 产品级用户 ID（用于游戏功能）

```cpp
#include "Online/OnlineIdEOSGS.h"

using namespace UE::Online;

// AccountId 与 ProductUserId 互转
EOS_ProductUserId PUID = GetProductUserId(AccountId);
FAccountId FoundAccountId = FindAccountId(EOnlineServices::Epic, PUID);
```

### 进阶用法 — 连接字符串解析

```cpp
using namespace UE::Online;

// 从 Lobby 获取连接字符串（用于 P2P 连接）
TOnlineResult<FGetResolvedConnectString> ConnectResult =
    OnlineServices->GetResolvedConnectString({
        .LocalAccountId = LocalAccountId,
        .LobbyId = LobbyId
    });

if (ConnectResult.IsOk())
{
    FString ConnectString = ConnectResult.GetOkValue().ConnectString;
    // 格式: "EOS:0002aeeb5b2d4388a3752dd6d31222ec"
}
```

**来源**: `OnlineServicesEOSGS.cpp` — `GetResolvedConnectString` 支持从 Lobby 和 Session 两种方式解析连接字符串。

## Demo 示例

以下是一个最小的 EOS 认证示例：

### Build.cs

```csharp
using UnrealBuildTool;

public class MyGame : ModuleRules
{
    public MyGame(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "OnlineServicesInterface",    // UE::Online 通用接口
            "OnlineServicesEOSGS",        // EOS Game Services 实现
            "OnlineBase"
        });
    }
}
```

### MyGameAuth.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Online/OnlineServicesEOSGS.h"

class FMyGameAuth
{
public:
    void LoginWithEOS(FPlatformUserId PlatformUserId);

private:
    void OnLoginComplete(const UE::Online::TOnlineResult<UE::Online::FAuthLogin>& Result);
};
```

### MyGameAuth.cpp

```cpp
#include "MyGameAuth.h"
#include "Online/OnlineServicesEOSGS.h"

using namespace UE::Online;

void FMyGameAuth::LoginWithEOS(FPlatformUserId PlatformUserId)
{
    IOnlineServicesPtr OnlineServices = GetServices(EOnlineServices::Epic);
    if (!OnlineServices)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to get EOS Online Services"));
        return;
    }

    IAuthPtr AuthInterface = OnlineServices->GetAuthInterface();

    FAuthLogin::Params LoginParams;
    LoginParams.PlatformUserId = PlatformUserId;
    LoginParams.CredentialsType = FName(TEXT("ExchangeCode"));

    AuthInterface->Login(MoveTemp(LoginParams))
        ->OnComplete(TOnlineAsyncOpDelegate<FAuthLogin>::CreateRaw(
            this, &FMyGameAuth::OnLoginComplete));
}

void FMyGameAuth::OnLoginComplete(const TOnlineResult<FAuthLogin>& Result)
{
    if (Result.IsOk())
    {
        const FAccountInfo& AccountInfo = *Result.GetOkValue().AccountInfo;
        UE_LOG(LogTemp, Log, TEXT("EOS Login successful. AccountId: %s"),
            *AccountInfo.AccountId.ToString());
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("EOS Login failed: %s"),
            *Result.GetErrorValue().GetLogString());
    }
}
```

## 模块依赖

### 插件依赖

| 插件 | 用途 |
|---|---|
| `OnlineServices` | 在线服务框架核心 |
| `OnlineServicesEpicCommon` | Epic 平台通用在线服务基类 |
| `EOSShared` | EOS SDK 共享类型和工具 |
| `SocketSubsystemEOS` | EOS Socket 子系统 |

### 模块依赖 (Build.cs)

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `EOSSDK` | Epic Online Services SDK |
| `OnlineServicesInterface` | UE::Online 通用接口定义 |
| `OnlineServicesEpicCommon` | Epic 平台通用实现基类 |
| `OnlineServicesCommon` | 在线服务通用工具 |
| `OnlineServicesCommonEngineUtils` | 引擎集成工具 |
| `OnlineBase` | 在线服务基础类型 |
| `CoreOnline` | 在线核心类型（私有依赖） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `EOSShared` | EOS 共享模块（私有依赖） |
| `Sockets` | Socket 接口（私有依赖） |
| `SocketSubsystemEOS` | EOS Socket 子系统（仅 WITH_ENGINE） |

## 维护状态

### 近期更新

1. **2025-08-26** `9e6ad262` — Add ToAccountId and FromStringData to the ID registry to support converting account strings to FAccountIDs
   - 为 ID 注册表添加字符串到 AccountId 的转换支持，增强 ID 系统的互操作性

2. **2025-08-22** `b0624d77` — Remove unused constants
   - 清理无用常量，代码维护

3. **2025-08-14** `581de5f6` — Reduced members of FInternetAddrEOS and refactored usage accordingly
   - 精简 FInternetAddrEOS 结构并重构相关用法

### 维护评价

- **创建时间**: 2022-09-30（约 4 年前）
- **最近更新**: 2025-08-26，约 8 个月前有实质性更新
- **维护状态**: **活跃维护** — 2025 年内有多次功能性更新，包括 ID 系统增强和代码优化
- **平台支持**: Win64、Mac、Linux、LinuxArm64、Android
- **已知限制**:
  - Stats 系统仅支持 int32 类型，double 和 int64 会被截断，不支持 string 类型
  - TitleFile 和 UserFile 需要正确配置加密密钥，否则对应的 Storage 接口不可用
  - 本插件不提供任何蓝图接口，纯 C++ 使用
  - `EnabledByDefault = false`，需要在项目设置中手动启用
- **推荐**: ✅ 推荐使用。这是 Epic 官方维护的 EOS Game Services 实现，处于活跃开发状态，是 UE5 项目使用 EOS 后端的标准选择

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEOSGS)
- [EOS 官方文档](https://dev.epicgames.com/docs/online-services)
- 插件依赖: [OnlineServices](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices), [OnlineServicesEpicCommon](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesEpicCommon), [EOSShared](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/EOSShared)
