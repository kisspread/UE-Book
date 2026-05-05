# Online Subsystem

> Shared code for interacting online subsystem implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystem` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystem) | |

## 用途

OnlineSubsystem 是 Unreal Engine 在线服务的**抽象层和框架**。它定义了一套统一的接口（Interface），让你的游戏代码不需要关心底层是 Steam、PlayStation Network、Xbox Live、Epic Online Services 还是其他任何平台。

核心设计思想：**面向接口编程**。`IOnlineSubsystem` 是入口类，通过它获取各种功能接口（Identity、Session、Friends、Leaderboards 等），每个具体平台（如 `OnlineSubsystemSteam`、`OnlineSubsystemEOS`）只需实现这些接口即可。

这个插件本身**不提供任何平台实现**——它只是接口定义和子系统管理框架。实际的平台实现是独立的插件（如 `OnlineSubsystemSteam`、`OnlineSubsystemEOS` 等）。

## 使用场景

- 你需要做一个多人游戏，但不想绑定到某个特定平台 → 用 OnlineSubsystem 的抽象接口
- 你要支持 Steam + PlayStation + Xbox 跨平台 → 每个平台实现相同的接口
- 你需要在运行时切换在线服务（例如从 Steam 切换到 EOS） → 通过配置文件 `DefaultPlatformService` 切换
- 你在做专用服务器（Dedicated Server）→ `IsDedicated()` / `IsServer()` 判断
- 你需要排行榜、成就、好友系统、会话管理等功能 → 通过对应接口访问

## 蓝图用法

OnlineSubsystem 本身几乎**没有暴露蓝图接口**（它是一个纯 C++ 抽象层）。唯一与蓝图相关的是 `TurnBasedMatchInterface`，它提供了两个 BlueprintImplementableEvent：

### 核心接口

| 事件 | 说明 | 所在接口 |
|---|---|---|
| `OnMatchReceivedTurn` | 回合制游戏中轮到你时触发 | `ITurnBasedMatchInterface` |
| `OnMatchEnded` | 回合制游戏结束时触发 | `ITurnBasedMatchInterface` |

> 大多数蓝图中使用的在线功能来自 **OnlineSubsystemUtils** 插件，它提供了 BlueprintCallable 的节点封装。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystem.h"
#include "OnlineSubsystemModule.h"
```

### 基本用法 — 获取子系统实例

```cpp
// 获取默认在线子系统（由 DefaultEngine.ini 中 DefaultPlatformService 指定）
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();

// 按名称获取特定子系统
IOnlineSubsystem* SteamSub = IOnlineSubsystem::Get(STEAM_SUBSYSTEM);
IOnlineSubsystem* EOSSub = IOnlineSubsystem::Get(EOS_SUBSYSTEM);

// 获取当前平台原生子系统
IOnlineSubsystem* NativeSub = IOnlineSubsystem::GetByPlatform();
```

来源: `Source/Public/OnlineSubsystem.h`

### 获取功能接口

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
if (OnlineSub)
{
    // 身份认证接口 — 登录、登出、获取登录状态
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    
    // 会话接口 — 创建/查找/加入游戏会话
    IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();
    
    // 好友接口 — 好友列表、邀请、屏蔽
    IOnlineFriendsPtr Friends = OnlineSub->GetFriendsInterface();
    
    // 排行榜接口
    IOnlineLeaderboardsPtr Leaderboards = OnlineSub->GetLeaderboardsInterface();
    
    // 成就接口
    IOnlineAchievementsPtr Achievements = OnlineSub->GetAchievementsInterface();
    
    // 语音接口
    IOnlineVoicePtr Voice = OnlineSub->GetVoiceInterface();
    
    // 购买/商店接口
    IOnlinePurchasePtr Purchase = OnlineSub->GetPurchaseInterface();
    IOnlineStoreV2Ptr Store = OnlineSub->GetStoreV2Interface();
    
    // Party 系统接口
    IOnlinePartyPtr Party = OnlineSub->GetPartyInterface();
    
    // 消息/聊天接口
    IOnlineMessagePtr Message = OnlineSub->GetMessageInterface();
    IOnlineChatPtr Chat = OnlineSub->GetChatInterface();
}
```

### 登录示例

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();

// 绑定登录完成回调
Identity->AddOnLoginCompleteDelegate_Handle(
    0,  // LocalUserNum
    FOnLoginCompleteDelegate::CreateUObject(this, &UMyClass::OnLoginComplete)
);

// 执行登录
FOnlineAccountCredentials Credentials;
Credentials.Type = TEXT("accountportal");
Credentials.Id = TEXT("");
Credentials.Token = TEXT("");
Identity->Login(0, Credentials);
```

### 会话管理示例

```cpp
IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
IOnlineSessionPtr Sessions = OnlineSub->GetSessionInterface();

// 创建会话
FOnlineSessionSettings SessionSettings;
SessionSettings.NumPublicConnections = 4;
SessionSettings.bIsLANMatch = false;
SessionSettings.bShouldAdvertise = true;
SessionSettings.bUsesPresence = true;

Sessions->AddOnCreateSessionCompleteDelegate_Handle(
    FOnCreateSessionCompleteDelegate::CreateUObject(this, &UMyClass::OnCreateSessionComplete)
);
Sessions->CreateSession(0, NAME_GameSession, SessionSettings);

// 查找会话
TSharedRef<FOnlineSessionSearch> SearchSettings = MakeShared<FOnlineSessionSearch>();
SearchSettings->MaxSearchResults = 10;
SearchSettings->bIsLanQuery = false;

Sessions->AddOnFindSessionsCompleteDelegate_Handle(
    FOnFindSessionsCompleteDelegate::CreateUObject(this, &UMyClass::OnFindSessionsComplete)
);
Sessions->FindSessions(0, SearchSettings);
```

### 子系统工厂注册（实现自定义子系统时）

```cpp
// 自定义在线子系统需要实现 IOnlineFactory 并注册
class FOnlineSubsystemMyPlatformModule : public IModuleInterface
{
    virtual void StartupModule() override
    {
        MyPlatformFactory = new FOnlineFactoryMyPlatform();
        FOnlineSubsystemModule& OSSModule = FModuleManager::GetModuleChecked<FOnlineSubsystemModule>("OnlineSubsystem");
        OSSModule.RegisterPlatformService(MYPLATFORM_SUBSYSTEM, MyPlatformFactory);
    }

    virtual void ShutdownModule() override
    {
        FOnlineSubsystemModule& OSSModule = FModuleManager::GetModuleChecked<FOnlineSubsystemModule>("OnlineSubsystem");
        OSSModule.UnregisterPlatformService(MYPLATFORM_SUBSYSTEM);
    }
};
```

来源: `Source/Public/OnlineSubsystemModule.h`

### 配置文件

在 `DefaultEngine.ini` 中配置默认在线服务：

```ini
[OnlineSubsystem]
DefaultPlatformService=Steam

[OnlineSubsystemSteam]
bEnabled=true
SteamDevAppId=480
```

### 完整接口列表

`IOnlineSubsystem` 提供以下功能接口的访问器：

| 接口 | 获取方法 | 功能 |
|---|---|---|
| `IOnlineSession` | `GetSessionInterface()` | 会话创建/查找/加入/销毁 |
| `IOnlineIdentity` | `GetIdentityInterface()` | 登录/登出/身份验证 |
| `IOnlineFriends` | `GetFriendsInterface()` | 好友列表/邀请/屏蔽 |
| `IOnlinePartySystem` | `GetPartyInterface()` | Party/队伍系统 |
| `IOnlineLeaderboards` | `GetLeaderboardsInterface()` | 排行榜读写 |
| `IOnlineAchievements` | `GetAchievementsInterface()` | 成就系统 |
| `IOnlineVoice` | `GetVoiceInterface()` | 语音通信 |
| `IOnlinePresence` | `GetPresenceInterface()` | 在线状态/Rich Presence |
| `IOnlineStoreV2` | `GetStoreV2Interface()` | 商店浏览 |
| `IOnlinePurchase` | `GetPurchaseInterface()` | 内购/交易 |
| `IOnlineEntitlements` | `GetEntitlementsInterface()` | 用户权益/DLC |
| `IOnlineExternalUI` | `GetExternalUIInterface()` | 平台原生 UI（登录、好友选择等） |
| `IOnlineTime` | `GetTimeInterface()` | 服务器时间 |
| `IOnlineTitleFile` | `GetTitleFileInterface()` | 云端文件下载 |
| `IOnlineSharedCloud` | `GetSharedCloudInterface()` | 共享云存储 |
| `IOnlineUserCloud` | `GetUserCloudInterface()` | 用户云存储 |
| `IOnlineStats` | `GetStatsInterface()` | 在线统计 |
| `IOnlineEvents` | `GetEventsInterface()` | 事件追踪 |
| `IOnlineMessage` | `GetMessageInterface()` | 消息发送 |
| `IOnlineChat` | `GetChatInterface()` | 聊天 |
| `IOnlineSharing` | `GetSharingInterface()` | 社交分享 |
| `IOnlineUser` | `GetUserInterface()` | 用户信息查询 |
| `IOnlineGroups` | `GetGroupsInterface()` | 群组 |
| `IOnlineTurnBased` | `GetTurnBasedInterface()` | 回合制多人 |
| `IOnlineTournament` | `GetTournamentInterface()` | 锦标赛 |
| `IOnlineGameActivity` | `GetGameActivityInterface()` | 游戏活动 |
| `IOnlineGameItemStats` | `GetGameItemStatsInterface()` | 游戏物品统计 |
| `IOnlineGameMatches` | `GetGameMatchesInterface()` | 匹配系统 |
| `IMessageSanitizer` | `GetMessageSanitizer()` | 消息内容过滤 |

### 支持的子系统名称

`OnlineSubsystemNames.h` 中定义了所有已知的子系统名称常量：

| 常量 | 平台 |
|---|---|
| `NULL_SUBSYSTEM` | 空实现（开发/测试用） |
| `STEAM_SUBSYSTEM` | Steam |
| `EOS_SUBSYSTEM` | Epic Online Services |
| `GDK_SUBSYSTEM` | Xbox (GDK) |
| `PS4_SUBSYSTEM` | PlayStation 4 |
| `PS5_SUBSYSTEM` | PlayStation 5 |
| `NINTENDO_SUBSYSTEM` | Nintendo |
| `GOOGLEPLAY_SUBSYSTEM` | Google Play |
| `IOS_SUBSYSTEM` | Apple Game Center (iOS) |
| `APPLE_SUBSYSTEM` | Apple |
| `AMAZON_SUBSYSTEM` | Amazon |
| `FACEBOOK_SUBSYSTEM` | Facebook |
| `TENCENT_SUBSYSTEM` | Tencent |
| `SAMSUNG_SUBSYSTEM` | Samsung |
| `MCP_SUBSYSTEM` | MCP (Epic's backend) |

## Demo 示例

### 最小可编译示例 — 登录并获取用户信息

```cpp
// MyOnlineManager.h
#pragma once
#include "CoreMinimal.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemTypes.h"
#include "MyOnlineManager.generated.h"

UCLASS()
class UMyOnlineManager : public UObject
{
    GENERATED_BODY()

public:
    void Login();
    
private:
    void OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error);
    
    FDelegateHandle LoginDelegateHandle;
};
```

```cpp
// MyOnlineManager.cpp
#include "MyOnlineManager.h"
#include "Interfaces/OnlineIdentityInterface.h"

void UMyOnlineManager::Login()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;
    
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    if (!Identity.IsValid()) return;
    
    LoginDelegateHandle = Identity->AddOnLoginCompleteDelegate_Handle(
        0,
        FOnLoginCompleteDelegate::CreateUObject(this, &UMyOnlineManager::OnLoginComplete)
    );
    
    Identity->Login(0, FOnlineAccountCredentials());
}

void UMyOnlineManager::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, 
    const FUniqueNetId& UserId, const FString& Error)
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineIdentityPtr Identity = OnlineSub->GetIdentityInterface();
    
    Identity->ClearOnLoginCompleteDelegate_Handle(0, LoginDelegateHandle);
    
    if (bWasSuccessful)
    {
        FString PlayerName = Identity->GetPlayerNickname(UserId);
        UE_LOG(LogTemp, Log, TEXT("Login successful: %s"), *PlayerName);
    }
}
```

Build.cs 依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "OnlineSubsystem",
    "OnlineSubsystemUtils"  // 如果需要蓝图封装
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineBase` | 在线服务基础类型（插件依赖） |
| `Json` | JSON 序列化支持 |
| `CoreOnline` | 核心在线类型（FUniqueNetId 等） |
| `SignalProcessing` | 音频信号处理（语音相关） |
| `Core` | 引擎核心（私有依赖） |
| `CoreUObject` | UObject 系统（私有依赖） |
| `JsonUtilities` | JSON 工具（私有依赖） |

> 使用 OnlineSubsystem 的游戏模块通常只需依赖 `OnlineSubsystem` 和 `OnlineSubsystemUtils`。

## 维护状态

### 近期更新

| 日期 | Hash | 说明 |
|---|---|---|
| 2025-08-13 | `65515472` | 废弃 OnlineJsonSerializer.h — 该头文件已被标记为 deprecated，可能在后续版本移除 |
| 2025-07-28 | `1c9d37f9` | 修复迭代器使用中的 remove 问题 — 修复在遍历过程中删除元素的 bug |
| 2025-07-28 | `d1397571` | 回退上述修复（Backout CL44389834），随后重新提交 |

### 维护评价

- **年龄**: 约 10 年（2016 年创建），是 UE 在线系统的基石
- **维护状态**: ✅ **活跃维护** — 最近 1 年内有多次功能性更新
- **稳定性**: 作为抽象框架层，结构非常稳定，变化主要是接口扩展和 bug 修复
- **重要性**: 这是 UE 在线功能的核心，所有在线子系统插件都依赖它
- **推荐**: ✅ **强烈推荐** — 任何使用 UE 在线功能的项目都会自动依赖此插件
- **注意**: `OnlineJsonSerializer.h` 已被废弃，新代码不应使用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystem)
- [OnlineSubsystemUtils 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils) — 蓝图友好封装 + Beacon 等工具
- [OnlineBase 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineBase) — 基础在线类型
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystem/Source/Test) — `Source/Test/Utils/OnlineTestCommon.h`
