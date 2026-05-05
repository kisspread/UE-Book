# Online Services Null

> Online Services implementation without an external service.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineServicesNull` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2022-09-30 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesNull) | |

## 用途

OnlineServicesNull 是 UE5 新版 Online Services 框架（`UE::Online`）的 **空实现（Null Provider）**。它不连接任何外部在线服务（如 Steam、EOS、PlayStation Network 等），而是在本地模拟完整的在线服务功能。

这个 plugin 的存在有两个核心目的：

1. **开发期占位**：在没有平台 SDK 或不联网的开发环境中，让游戏代码可以正常运行完整的在线功能流程（登录、Session、Lobby、成就等），无需修改任何游戏逻辑。
2. **LAN 多人游戏**：Sessions 和 Lobbies 接口基于 LAN Beacon 实现了真实的局域网发现和连接功能，支持本地多人联机测试。

Null 实现的行为类似主机平台——用户没有显式的登录/登出流程，所有本地用户在初始化时自动被视为"已登录"状态。

## 使用场景

- 你在 PC 上开发多人游戏，没有配置任何在线平台 SDK → 启用 OnlineServicesNull，游戏的在线功能代码即可正常编译运行
- 你需要在办公室局域网内测试多人 Session/Lobby → OnlineServicesNull 的 LAN 发现机制自动工作
- 你在编写集成测试或自动化测试，需要一个不依赖外部服务的在线后端 → 使用 Null provider
- 你在 Editor 中调试成就/排行榜/统计系统的逻辑流程 → Null 实现提供完整的内存态存储

## 蓝图用法

OnlineServicesNull 本身不暴露额外的蓝图节点。它通过 UE5 的 `OnlineServices` 子系统接口工作，所有在线操作通过 `UOnlineServicesSubsystem` 等引擎提供的蓝图节点完成。Null 只是在底层替换实际的服务提供者。

因此，蓝图中的用法与使用其他在线平台完全一致——区别仅在于配置文件中选择 Null 作为 provider。

## C++ 用法

### 头文件引入

```cpp
#include "Online/OnlineServicesNull.h"
#include "Online/AuthNull.h"
#include "Online/SessionsNull.h"
#include "Online/LobbiesNull.h"
```

### 获取 Null 在线服务实例

```cpp
using namespace UE::Online;

// 通过 Online Services Registry 获取 Null 实例
FOnlineServicesRegistry& Registry = FOnlineServicesRegistry::Get();
TSharedPtr<IOnlineServices> Services = Registry.GetServices(EOnlineServices::Null);
```

### 认证（Auth）

Null 的认证是自动的——所有本地平台用户在初始化时即被标记为已登录，无需调用 Login。

```cpp
// 获取 Auth 接口
TOnlinePtr<FAuthNull> Auth = Services->GetAuthInterface();

// 检查用户是否已登录（在 Null 下始终为 true）
if (Auth->IsLoggedIn(AccountId))
{
    // 用户已登录，可以使用其他在线功能
}

// 账户 ID 格式：OSSV2-{hostname}-{GUIDorLoginId}[-{userNum}]
// 可通过配置 bAddUserNumToNullId 和 bForceStableNullId 控制 ID 生成策略
```

来源：`Source/Private/Online/AuthNull.cpp`

### Sessions（局域网会话）

Sessions 基于 `FSessionsLAN` 实现，通过 UDP 广播进行局域网 Session 发现。

```cpp
// 获取 Sessions 接口
TOnlinePtr<FSessionsNull> Sessions = Services->GetSessionsInterface();

// Session 操作通过父类 FSessionsLAN 的接口完成
// 创建、搜索、加入、离开 Session 均使用标准的 ISessions 接口方法
```

### Lobbies（局域网大厅）

Lobbies 是功能最完整的接口，支持创建、搜索、加入、离开大厅，同样基于 LAN Beacon。

```cpp
// 获取 Lobbies 接口
TOnlinePtr<FLobbiesNull> Lobbies = Services->GetLobbiesInterface();

// 创建 Lobby
FCreateLobby::Params CreateParams;
CreateParams.LocalAccountId = MyAccountId;
CreateParams.LocalName = FName("MyGameLobby");
CreateParams.Attributes.Add(FName("MapName"), FSchemaVariant(FString("TestMap")));
CreateParams.bPresenceEnabled = true;

TOnlineAsyncOpHandle<FCreateLobby> CreateHandle = Lobbies->CreateLobby(MoveTemp(CreateParams));

// 搜索 LAN 上的 Lobby
FFindLobbies::Params FindParams;
FindParams.LocalAccountId = MyAccountId;
TOnlineAsyncOpHandle<FFindLobbies> FindHandle = Lobbies->FindLobbies(MoveTemp(FindParams));

// 获取已加入的 Lobbies
TOnlineResult<FGetJoinedLobbies> JoinedLobbies = Lobbies->GetJoinedLobbies({ MyAccountId });
```

来源：`Source/Private/Online/LobbiesNull.cpp`

### 成就（Achievements）

支持从配置文件加载成就定义，提供完整的查询、获取状态、解锁流程。

```cpp
// 成就定义通过配置文件注入
// 配置路径：OnlineServices.Null.Achievements

// 查询成就定义
FQueryAchievementDefinitions::Params DefParams;
DefParams.LocalAccountId = MyAccountId;
TOnlineAsyncOpHandle<FQueryAchievementDefinitions> DefHandle = Achievements->QueryAchievementDefinitions(MoveTemp(DefParams));

// 解锁成就
FUnlockAchievements::Params UnlockParams;
UnlockParams.LocalAccountId = MyAccountId;
UnlockParams.AchievementIds.Add("FirstKill");
TOnlineAsyncOpHandle<FUnlockAchievements> UnlockHandle = Achievements->UnlockAchievements(MoveTemp(UnlockParams));
```

来源：`Source/Private/Online/AchievementsNull.cpp`

### 排行榜（Leaderboards）

使用双向链表维护排序数据，支持 KeepBest/Force 更新策略和升序/降序排列。

```cpp
// 写入分数
FWriteLeaderboardScores::Params WriteParams;
WriteParams.LocalAccountId = MyAccountId;
WriteParams.BoardName = "HighScore";
WriteParams.Score = 1000;
Leaderboards->WriteLeaderboardScores(MoveTemp(WriteParams));

// 按排名范围读取
FReadEntriesAroundRank::Params RankParams;
RankParams.BoardName = "HighScore";
RankParams.Rank = 0;
RankParams.Limit = 10;
Leaderboards->ReadEntriesAroundRank(MoveTemp(RankParams));
```

来源：`Source/Private/Online/LeaderboardsNull.cpp`

### 统计（Stats）

内存态统计系统，支持 Set/Sum/Largest/Smallest 四种修改模式。

```cpp
// 更新统计
FUpdateStats::Params StatsParams;
StatsParams.LocalAccountId = MyAccountId;
FUserStats UserStats;
UserStats.AccountId = MyAccountId;
UserStats.Stats.Add("KillCount", FStatValue(int64(1)));
StatsParams.UpdateUsersStats.Add(UserStats);
Stats->UpdateStats(MoveTemp(StatsParams));

// 查询统计
FQueryStats::Params QueryParams;
QueryParams.LocalAccountId = MyAccountId;
QueryParams.TargetAccountId = MyAccountId;
QueryParams.StatNames.Add("KillCount");
Stats->QueryStats(MoveTemp(QueryParams));
```

来源：`Source/Private/Online/StatsNull.cpp`

### 在线状态（Presence）

支持查询、更新、部分更新用户在线状态，包含变更监听机制。

```cpp
// 更新在线状态
FUpdatePresence::Params PresenceParams;
PresenceParams.LocalAccountId = MyAccountId;
PresenceParams.Presence = MakeShared<FUserPresence>();
PresenceParams.Presence->Status = EPresenceStatus::Online;
PresenceParams.Presence->StatusString = "Playing";
Presence->UpdatePresence(MoveTemp(PresenceParams));

// 监听在线状态变更
Presence->OnPresenceUpdatedEvent.AddLambda([](const FPresenceUpdated& Event)
{
    // 处理在线状态变更
});
```

来源：`Source/Private/Online/PresenceNull.cpp`

### 文件系统

支持 Title File（只读标题文件）和 User File（可读写用户文件）。

**Title File**：从配置加载，只读。

```cpp
// 配置路径：OnlineServices.Null.TitleFile
// 枚举并读取标题文件
TitleFile->EnumerateFiles({ LocalAccountId });
TOnlineResult<FTitleFileGetEnumeratedFiles> Files = TitleFile->GetEnumeratedFiles({ LocalAccountId });
```

**User File**：支持完整的 CRUD 操作。

```cpp
// 写入文件
FUserFileWriteFile::Params WriteParams;
WriteParams.LocalAccountId = MyAccountId;
WriteParams.Filename = "save.dat";
WriteParams.FileContents = { /* bytes */ };
UserFile->WriteFile(MoveTemp(WriteParams));

// 读取、复制、删除文件均类似
```

来源：`Source/Private/Online/TitleFileNull.cpp`, `Source/Private/Online/UserFileNull.cpp`

### 配置系统

OnlineServicesNull 使用 UE 的配置系统加载各接口的初始化数据：

| 配置节 | 用途 |
|---|---|
| `OnlineServices.Null` | 平台级配置（TestId 等） |
| `OnlineServices.Null.Auth` | 认证配置（bAddUserNumToNullId, bForceStableNullId） |
| `OnlineServices.Null.Achievements` | 成就定义 |
| `OnlineServices.Null.TitleFile` | 标题文件内容 |
| `OnlineServices.Null.UserFile` | 用户文件初始状态 |

## 模块依赖

从 `OnlineServicesNull.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心 |
| `CoreOnline` | 在线服务基础类型 |
| `Sockets` | 网络 Socket 接口（LAN 发现用） |
| `OnlineServicesInterface` | 在线服务抽象接口定义 |
| `OnlineServicesCommon` | 在线服务通用基类（FAuthCommon, FSessionsCommon 等） |
| `OnlineSubsystem` | 旧版在线子系统兼容 |
| `ApplicationCore` | 平台输入设备映射（私有依赖） |
| `OnlineBase` | 在线服务基础工具（私有依赖） |
| `OnlineServicesCommonEngineUtils` | 引擎工具集成如 GetPortFromNetDriver（私有依赖） |

**Plugin 依赖**：
- `OnlineServices` — 在线服务核心框架
- `OnlineSubsystem` — 旧版在线子系统
- `OnlineSubsystemUtils` — 旧版在线子系统工具

## 架构概览

OnlineServicesNull 实现了 9 个在线服务接口：

| 接口类 | 基类 | 说明 |
|---|---|---|
| `FOnlineServicesNull` | `FOnlineServicesCommon` | 总入口，注册所有子接口，处理 GetResolvedConnectString |
| `FAuthNull` | `FAuthCommon` | 自动登录，监听输入设备连接以自动注册新用户 |
| `FSessionsNull` | `FSessionsLAN` | LAN Session，自定义 NBO 序列化 |
| `FLobbiesNull` | `FLobbiesCommon` | LAN Lobby，完整 CRUD + LAN 发现/广播 |
| `FPresenceNull` | `FPresenceCommon` | 内存态在线状态，支持监听 |
| `FAchievementsNull` | `FAchievementsCommon` | 配置驱动的成就系统 |
| `FLeaderboardsNull` | `FLeaderboardsCommon` | 内存态排行榜，双向链表排序 |
| `FStatsNull` | `FStatsCommon` | 内存态统计，支持多种聚合方式 |
| `FTitleFileNull` | `FTitleFileCommon` | 配置驱动的只读文件 |
| `FUserFileNull` | `FUserFileCommon` | 内存态可读写文件 |

ID 注册表：

| 注册表 | 说明 |
|---|---|
| `FOnlineAccountIdRegistryNull` | 账户 ID（字符串 ↔ FAccountId），基于 `TOnlineBasicAccountIdRegistry<FString>` |
| `FOnlineSessionIdRegistryNull` | Session ID，继承 `FOnlineSessionIdRegistryLAN` |
| `FOnlineLobbyIdRegistryNull` | Lobby ID，自增整数 + GUID 映射 |

模块注册流程（`FOnlineServicesNullModule::StartupModule`）：
1. 确保 `OnlineServicesInterface` 模块已加载
2. 注册 `FOnlineServicesFactoryNull` 工厂到 `FOnlineServicesRegistry`
3. 注册 Account ID 和 Session ID 注册表到 `FOnlineIdRegistryRegistry`

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-26 | `9e6ad262` | 为 ID 注册表添加 `ToAccountId` 和 `FromStringData` 支持，用于将字符串转换为 FAccountId |
| 2025-06-13 | `a769d3a6` | 修复 OSS Null 的 Presence 更新问题 |
| 2025-05-21 | `3b7a381e` | 移除在 5.5 中标记为废弃的在线代码 |

### 维护评价

- **创建时间**：2022-09-30，与 UE5 Online Services 框架同步诞生
- **最近更新**：2025-08-26，近期有活跃的功能性更新（ID 注册表改进）和 bug 修复（Presence 更新）
- **维护状态**：活跃维护中。作为 UE5 新在线框架的基准实现，每次在线框架 API 变更时都需要同步更新
- **代码质量**：部分实现有 `// todo` 标注，表明仍在完善中（如 Lobby 的 HostInfo、排序等）
- **推荐度**：✅ 强烈推荐在开发和测试阶段使用。这是 Epic 官方的在线服务基准实现，所有其他平台 provider 都应与 Null 实现保持行为一致

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServicesNull)
- [Online Services 父插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineServices)
