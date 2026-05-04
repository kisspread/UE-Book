# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

---

## 用途

OnlineFramework 是 Epic 为旗下多人在线游戏（如 Fortnite）构建的**平台无关社交框架**。它在 `IOnlineSubsystem` 之上提供了一层统一抽象，屏蔽了 Steam、PlayStation Network、Xbox Live、Nintendo Switch Online 等各平台在线服务的差异。

该插件解决的核心问题：

1. **跨平台身份统一**：`USocialUser` 将同一玩家在不同平台（Primary OSS + Platform OSS）的身份关联为一个逻辑用户，处理 ID 映射和账号链接
2. **派对（Party）生命周期管理**：创建、加入、离开、踢人、晋升队长，以及跨平台会话（Platform Session）的同步
3. **多频道聊天系统**：支持派对聊天、私聊（Whisper）、团队频道、全局频道、只读频道等
4. **社交交互声明式宏**：通过 `DECLARE_SOCIAL_INTERACTION` 宏以声明式方式定义好友邀请、屏蔽、派对操作等交互，自动生成可用性检查和执行逻辑
5. **可配置用户列表**：基于在线状态、关系类型、子系统、自定义过滤器等条件自动维护用户列表
6. **派对数据复制**：`TPartyDataReplicator` 模板将结构化数据通过 Party Data 同步到所有成员
7. **查询批处理**：`FSocialQueryManager` 将多个用户信息查询合并执行，减少网络开销

> ⚠️ **注意**：此插件 `EnabledByDefault = false`，需要在项目设置中手动启用。

---

## 使用场景

- 你正在开发一款**跨平台多人在线游戏**，需要统一管理不同平台的好友、派对和聊天 → 使用 OnlineFramework 的 Party 模块
- 你需要让玩家在**派对内实时同步自定义数据**（如准备状态、装备选择）→ 使用 `TPartyDataReplicator`
- 你需要实现**多频道聊天**（派对频道、私聊、团队频道切换）→ 使用 `USocialChatManager` 及其频道体系
- 你需要根据**在线状态、平台、关系类型**动态过滤和展示好友列表 → 使用 `ISocialUserList` + `FSocialUserListConfig`
- 你需要在运行时**热修复**游戏逻辑、检查**补丁更新**、限制**游玩时间**、处理**重连**→ 使用对应的 Hotfix / PatchCheck / PlayTimeLimit / Rejoin 模块

---

## 模块总览

| 模块 | 类型 | 说明 |
|---|---|---|
| **Party** | Runtime | 核心社交框架：派对系统、聊天系统、用户管理、社交交互、数据复制 |
| **Qos** | Runtime | Quality of Service 测量，用于选择最佳服务器/数据中心 |
| **Lobby** | Runtime | 大厅系统，用于比赛前的玩家匹配和组织 |
| **Hotfix** | Runtime | 运行时热修复机制，无需客户端更新即可修复服务端逻辑 |
| **LoginFlow** | Runtime | 登录流程管理，处理多平台登录状态机 |
| **PatchCheck** | Runtime | 补丁检查，在进入游戏前验证客户端版本是否需要更新 |
| **PlayTimeLimit** | Runtime | 游玩时间限制，支持家长控制和防沉迷 |
| **Rejoin** | Runtime | 重连机制，处理断线后重新加入派对/游戏 |

---

## Party 模块详解

Party 是 OnlineFramework 中最核心、最复杂的模块，提供了完整的社交基础设施。

### 核心架构

```
USocialManager (单例，GameInstance 级别)
├── USocialToolkit (每个 LocalPlayer 一个)
│   ├── USocialUser[] (所有已知用户)
│   ├── ISocialUserList[] (可配置用户列表)
│   └── USocialChatManager (聊天管理)
│       ├── USocialChatRoom (多人群聊)
│       ├── USocialPartyChatRoom (派对聊天)
│       ├── USocialPrivateMessageChannel (私聊)
│       ├── USocialReadOnlyChatChannel (只读)
│       └── USocialGroupChannel (群组)
├── USocialParty (派对状态)
│   ├── UPartyMember[] (派对成员)
│   └── TPartyDataReplicator<FPartyRepData> (数据复制)
└── USocialDebugTools (调试工具)
```

### 核心类说明

| 类 | 说明 |
|---|---|
| `USocialManager` | 顶层单例管理器，拥有所有 Toolkit，提供派对创建/恢复等全局操作 |
| `USocialToolkit` | 每个本地玩家的社交功能套件，管理用户列表、聊天、在线状态 |
| `USocialUser` | 跨平台用户抽象，聚合 Primary/Platform OSS 的身份和在线状态 |
| `USocialParty` | 抽象派对类，管理派对配置、成员、数据复制和平台会话 |
| `UPartyMember` | 派对成员，包含平台数据、JIP 请求/响应、连接状态 |
| `USocialChatManager` | 聊天管理器，创建和管理各类聊天频道 |
| `USocialChatChannel` | 聊天频道基类，支持消息收发、用户进出通知 |
| `USocialSettings` | 配置驱动的设置对象（CDO），控制派对大小、跨平台偏好等 |
| `FSocialInteractionHandle` | 社交交互句柄，封装交互的名称、可用性检查和执行 |
| `FSocialQueryManager` | 查询批处理器，合并多个用户信息查询 |

### 社交交互系统

Party 模块通过宏声明社交交互，自动生成可用性检查和执行逻辑：

**核心交互**（`CoreInteractions.h`）：

| 交互 | 说明 |
|---|---|
| `AddFriend` | 添加好友 |
| `AddPlatformFriend` | 添加平台好友 |
| `RemoveFriend` | 删除好友 |
| `AcceptFriendInvite` | 接受好友邀请 |
| `RejectFriendInvite` | 拒绝好友邀请 |
| `Block` | 屏蔽用户 |
| `Unblock` | 取消屏蔽 |
| `PrivateMessage` | 发送私信 |
| `ShowPlatformProfile` | 显示平台个人资料 |

**派对交互**（`PartyInteractions.h`）：

| 交互 | 说明 |
|---|---|
| `InviteToParty` | 邀请加入派对 |
| `JoinParty` | 加入派对 |
| `RequestToJoinParty` | 请求加入派对 |
| `AcceptJoinRequest` | 接加入请求 |
| `DismissJoinRequest` | 拒绝加入请求 |
| `AcceptPartyInvite` | 接受邀对邀请 |
| `RejectPartyInvite` | 拒绝派对邀请 |
| `LeaveParty` | 离开派对 |
| `KickPartyMember` | 踢出派对成员 |
| `PromoteToPartyLeader` | 提升为派对队长 |

### 聊天频道类型

| 频道类型 | 类 | 说明 |
|---|---|---|
| Party | `USocialPartyChatRoom` | 派对内多人聊天，成员进出自动管理 |
| Private | `USocialPrivateMessageChannel` | 两人私聊（Whisper） |
| General/Team/Founder | `USocialChatRoom` | 通用多人群聊 |
| System | `USocialReadOnlyChatChannel` | 只读系统消息，不支持发送 |
| Group | `USocialGroupChannel` | 基于 IOnlineGroups 的群组频道 |

### 用户列表过滤

`FSocialUserListConfig` 支持以下过滤维度：

| 过滤维度 | 说明 |
|---|---|
| `RelationshipType` | 关系类型（好友、屏蔽、最近玩家等） |
| `RelevantSubsystems` / `ForbiddenSubsystems` | 必须/禁止存在的 OSS 子系统 |
| `RequiredPresenceFlags` | 必须满足的在线状态标志 |
| `ForbiddenPresenceFlags` | 禁止的在线状态标志 |
| `OnCustomFilterUser` | 自定义过滤委托 |
| `GameSpecificStatusFilters` | 游戏特定状态过滤函数数组 |

`ESocialUserStateFlags` 标志位：`Online`、`Joinable`、`LookingForGroup`、`SamePlatform`、`InGame`、`SameApp`、`SameParty`

---

## 蓝图用法

Party 模块主要面向 C++ 扩展，Blueprint 暴露有限。以下是可用的 Blueprint 类型：

### 可用枚举（BlueprintType）

| 枚举 | 说明 |
|---|---|
| `ESocialChannelType` | 聊道类型：General, Founder, Party, Team, System, Private |
| `ESocialSubsystem` | 子系统类型：Primary（跨平台）, Platform（本平台） |
| `ESocialRelationship` | 关系类型：Friend, BlockedPlayer, RecentPlayer 等 |
| `ECrossplayPreference` | 跨平台偏好：OptedIn, OptedOut 等 |
| `EPartyType` | 派对类型：Public, FriendsOnly, Private |
| `EPartyInviteRestriction` | 邀请限制：AnyMember, LeaderOnly, NoInvites |
| `EPartyJoinDenialReason` | 加入拒绝原因（30+ 种） |

### 配置（Config = Game）

`USocialSettings` 通过 `DefaultGame.ini` 配置：

```ini
[/Script/Party.SocialSettings]
DefaultMaxPartySize=4
bPreferPlatformInvites=true
bMustSendPrimaryInvites=false
bLeavePartyOnDisconnect=true
UserListAutoUpdateRate=30.0
```

> 由于 `USocialManager`、`USocialToolkit`、`USocialParty` 等核心类均为 `MinimalAPI` 且设计为 C++ 子类化，完整的社交功能需要通过 C++ 扩展实现。

---

## C++ 用法

### 头文件引入

```cpp
// 核心管理器
#include "SocialManager.h"
#include "SocialToolkit.h"

// 用户和派对
#include "User/SocialUser.h"
#include "Party/SocialParty.h"
#include "Party/PartyMember.h"
#include "Party/PartyTypes.h"

// 聊天
#include "Chat/SocialChatManager.h"
#include "Chat/SocialChatChannel.h"

// 交互
#include "Interactions/CoreInteractions.h"
#include "Interactions/PartyInteractions.h"
#include "Interactions/SocialInteractionHandle.h"

// 用户列表
#include "User/ISocialUserList.h"

// 设置
#include "SocialSettings.h"
```

### 基本用法：创建派对

```cpp
// 获取 SocialManager（通常在 GameInstance 中持有）
USocialManager* SocialManager = GetGameInstance()->GetSubsystem<USocialManager>();
// 或者通过自定义方式获取

// 创建持久派对（默认配置）
SocialManager->CreatePersistentParty(FOnCreatePartyAttemptComplete::CreateLambda(
    [](ECreatePartyCompletionResult Result)
    {
        if (Result == ECreatePartyCompletionResult::Succeeded)
        {
            UE_LOG(LogTemp, Log, TEXT("Party created successfully"));
        }
    }
));

// 创建自定义配置的派对
FPartyConfiguration PartyConfig;
PartyConfig.MaxMembers = 4;
PartyConfig.JoinPolicy = EPartyType::FriendsOnly;

SocialManager->CreateParty(
    FOnlinePartyTypeId(1),  // 派对类型 ID
    PartyConfig,
    FOnCreatePartyAttemptComplete::CreateLambda(
        [](ECreatePartyCompletionResult Result)
        {
            // 处理结果
        }
    )
);
```

### 基本用法：获取用户信息

```cpp
// 获取本地玩家的 Toolkit
USocialToolkit* Toolkit = SocialManager->GetSocialToolkit(*LocalPlayer);
if (!Toolkit) return;

// 获取本地用户
USocialUser& LocalUser = Toolkit->GetLocalUser();
FString DisplayName = LocalUser.GetDisplayName();
FUniqueNetIdRepl UserId = LocalUser.GetUserId(ESocialSubsystem::Primary);

// 查找其他用户
USocialUser* FoundUser = Toolkit->FindUser(SomeNetId);
if (FoundUser)
{
    bool bIsFriend = FoundUser->IsFriend();
    bool bIsOnline = FoundUser->IsOnline();
    bool bIsPlayingThisGame = FoundUser->IsPlayingThisGame();
    FString Platform = FoundUser->GetCurrentPlatform().ToString();
}
```

### 进阶用法：创建可配置用户列表

```cpp
// 配置一个"在线好友"列表
FSocialUserListConfig OnlineFriendsConfig;
OnlineFriendsConfig.Name = TEXT("OnlineFriends");
OnlineFriendsConfig.RelationshipType = ESocialRelationship::Friend;
OnlineFriendsConfig.RequiredPresenceFlags = ESocialUserStateFlags::Online;
OnlineFriendsConfig.RelevantSubsystems = { ESocialSubsystem::Primary, ESocialSubsystem::Platform };
OnlineFriendsConfig.bAutoUpdate = true;
OnlineFriendsConfig.bSortDuringUpdate = true;

// 添加自定义过滤器
OnlineFriendsConfig.OnCustomFilterUser.BindLambda(
    [](const USocialUser& User) -> bool
    {
        // 排除被屏蔽的用户
        return !User.IsBlocked();
    }
);

// 添加游戏特定状态过滤器
OnlineFriendsConfig.GameSpecificStatusFilters.Add(
    [](const USocialUser& User) -> bool
    {
        // 当用户游戏状态变化时重新评估
        return true;
    }
);

// 创建列表
TSharedRef<ISocialUserList> OnlineFriendsList = Toolkit->CreateUserList(OnlineFriendsConfig);

// 监听列表变化
OnlineFriendsList->OnUserAdded().AddLambda(
    [](USocialUser& User)
    {
        UE_LOG(LogTemp, Log, TEXT("Online friend added: %s"), *User.GetDisplayName());
    }
);

OnlineFriendsList->OnUserRemoved().AddLambda(
    [](const USocialUser& User)
    {
        UE_LOG(LogTemp, Log, TEXT("Online friend removed: %s"), *User.GetDisplayName());
    }
);

// 手动触发更新
OnlineFriendsList->UpdateNow();
```

### 进阶用法：派对数据复制

```cpp
// 定义自定义派对复制数据
USTRUCT()
struct FMyPartyRepData : public FOnlinePartyRepDataBase
{
    GENERATED_BODY()

    UPROPERTY()
    bool bAllReady = false;

    UPROPERTY()
    FString SelectedMapName;

    // 暴露属性供复制
    EXPOSE_REP_DATA_PROPERTY(FMyPartyRepData, bool, bAllReady);
    EXPOSE_REP_DATA_PROPERTY(FMyPartyRepData, FString, SelectedMapName);
};

// 在 USocialParty 子类中使用
class UMyParty : public USocialParty
{
    // ...
    TPartyDataReplicator<FPartyRepData, UMyParty> PartyDataReplicator;
    FMyPartyRepData MyRepData;

    void InitReplication()
    {
        PartyDataReplicator.EstablishRepDataInstance(MyRepData);
    }

    void SetAllReady(bool bReady)
    {
        MyRepData.bAllReady = bReady;
        // 数据变更会自动触发复制
    }
};
```

### 进阶用法：自定义社交交互

```cpp
// 在头文件中声明自定义交互
DECLARE_SOCIAL_INTERACTION_EXPORT(MYGAME_API, TradeWithPlayer);

// 在 cpp 文件中定义
DEFINE_SOCIAL_INTERACTION(TradeWithPlayer)

FText FSocialInteraction_TradeWithPlayer::GetDisplayName(const USocialUser& User)
{
    return NSLOCTEXT("MyGame", "TradeWith", "Trade With Player");
}

FString FSocialInteraction_TradeWithPlayer::GetSlashCommandToken()
{
    return TEXT("/trade");
}

bool FSocialInteraction_TradeWithPlayer::CanExecute(const USocialUser& User)
{
    // 检查是否可以与该用户交易
    return User.IsFriend() && User.IsPlayingThisGame();
}

void FSocialInteraction_TradeWithPlayer::ExecuteInteraction(USocialUser& User)
{
    // 执行交易逻辑
    // ...
}
```

### 进阶用法：聊天系统

```cpp
// 获取聊天管理器
USocialChatManager& ChatManager = Toolkit->GetChatManager();

// 加入公开聊天室
ChatManager.JoinChatRoomPublic(
    FChatRoomId(TEXT("GlobalChat")),
    FChatRoomConfig(),
    ESocialSubsystem::Primary
);

// 加入私密聊天室
ChatManager.JoinChatRoomPrivate(
    FChatRoomId(TEXT("PartyChat")),
    FChatRoomConfig(),
    ESocialSubsystem::Primary
);

// 监听新频道创建
ChatManager.OnChannelCreated().AddLambda(
    [](USocialChatChannel& Channel)
    {
        UE_LOG(LogTemp, Log, TEXT("Channel created: %s"), *Channel.GetChannelDisplayName().ToString());

        // 监听消息
        Channel.OnMessageReceived().AddLambda(
            [](const FSocialChatMessageRef& Message)
            {
                UE_LOG(LogTemp, Log, TEXT("Message: %s"), *Message->GetMessageBody());
            }
        );
    }
);

// 发送消息
USocialChatRoom* ChatRoom = ChatManager.GetChatRoom(FChatRoomId(TEXT("GlobalChat")));
if (ChatRoom)
{
    ChatRoom->SendMessage(TEXT("Hello, world!"));
}
```

---

## Demo 示例

一个最小的自定义 SocialManager 子类，展示框架初始化和派对创建：

### MySocialManager.h

```cpp
#pragma once

#include "SocialManager.h"
#include "MySocialManager.generated.h"

UCLASS()
class UMySocialManager : public USocialManager
{
    GENERATED_BODY()

public:
    virtual void InitSocialManager() override;
    virtual void ShutdownSocialManager() override;

    /** 创建或加入好友的派对 */
    void JoinFriendParty(USocialUser& Friend);

    /** 获取在线好友列表 */
    TSharedRef<ISocialUserList> GetOnlineFriendsList() const { return OnlineFriendsList.ToSharedRef(); }

private:
    void OnPartyJoined(USocialParty& Party);
    void OnToolkitCreated(USocialToolkit& Toolkit);

    TSharedPtr<ISocialUserList> OnlineFriendsList;
};
```

### MySocialManager.cpp

```cpp
#include "MySocialManager.h"
#include "SocialToolkit.h"
#include "User/SocialUser.h"
#include "User/ISocialUserList.h"
#include "Party/SocialParty.h"
#include "Party/PartyTypes.h"

void UMySocialManager::InitSocialManager()
{
    Super::InitSocialManager();

    // 监听 Toolkit 创建
    OnSocialToolkitCreated().AddUObject(this, &UMySocialManager::OnToolkitCreated);

    // 监听派对加入
    OnPartyJoined().AddUObject(this, &UMySocialManager::OnPartyJoined);

    UE_LOG(LogTemp, Log, TEXT("MySocialManager initialized"));
}

void UMySocialManager::ShutdownSocialManager()
{
    OnlineFriendsList.Reset();
    Super::ShutdownSocialManager();
}

void UMySocialManager::OnToolkitCreated(USocialToolkit& Toolkit)
{
    // 创建在线好友列表
    FSocialUserListConfig Config;
    Config.Name = TEXT("OnlineFriends");
    Config.RelationshipType = ESocialRelationship::Friend;
    Config.RequiredPresenceFlags = ESocialUserStateFlags::Online | ESocialUserStateFlags::SameApp;
    Config.bAutoUpdate = true;

    OnlineFriendsList = Toolkit.CreateUserList(Config);

    OnlineFriendsList->OnUserAdded().AddLambda(
        [](USocialUser& User)
        {
            UE_LOG(LogTemp, Log, TEXT("Friend online: %s (%s)"),
                *User.GetDisplayName(),
                *User.GetCurrentPlatform().ToString());
        }
    );
}

void UMySocialManager::JoinFriendParty(USocialUser& Friend)
{
    // 通过交互系统执行加入派对
    FSocialInteractionHandle JoinPartyInteraction = FSocialInteraction_JoinParty::GetHandle();
    if (JoinPartyInteraction.IsAvailable(Friend))
    {
        JoinPartyInteraction.ExecuteInteraction(Friend);
    }
    else
    {
        // 回退：发送派对邀请
        FSocialInteractionHandle InviteInteraction = FSocialInteraction_InviteToParty::GetHandle();
        if (InviteInteraction.IsAvailable(Friend))
        {
            InviteInteraction.ExecuteInteraction(Friend);
        }
    }
}

void UMySocialManager::OnPartyJoined(USocialParty& Party)
{
    UE_LOG(LogTemp, Log, TEXT("Joined party with %d members"), Party.GetPartyMembers().Num());
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 核心依赖：IOnlinePartyInterface、IOnlineChatInterface、IOnlinePresenceInterface、IOnlineGroupsInterface 等所有在线子系统接口 |
| `OnlineSubsystemUtils` | SpectatorBeaconClient 等工具类，用于派对会话管理 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

```
- 077a5cb7599e Include the join info in failed party joins [REVIEW] @sam.zamani #rb Sam.Zamani
- 40d9d6ff222e Added new CVar and logic to disable writing presence to MCP/XMPP
- a34299129f10 Fix delegate lifetime crash with FFortPartyMemberRepData & related structs
```

- 最近一次提交改进了派对加入失败时的信息传递，属于功能增强
- 新增 CVar 控制是否向 MCP/XMPP 写入在线状态，属于运维/调试功能
- 修复了派对成员复制数据的委托生命周期崩溃问题，属于关键 bug 修复

### 维护评价

- **活跃维护**：最近的提交包含功能增强和 bug 修复，表明 Epic 仍在积极维护此插件
- **核心基础设施**：作为 Fortnite 等旗舰产品的社交底层，不太可能被废弃
- **成熟稳定**：创建于 2016 年，经过 9 年迭代，架构已相当成熟
- **⚠️ 注意**：`EnabledByDefault = false` 表明此插件并非面向所有项目开放，而是为特定多人在线游戏设计的专用框架
- **推荐使用**：如果你正在开发大型跨平台多人游戏，且需要 Fortnite 级别的社交功能，此插件是最佳起点。但对于小型项目，直接使用 `OnlineSubsystem` 接口可能更合适

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [Party 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Source/Party)
- [SocialManager 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/OnlineFramework/Source/Party/Public/SocialManager.h)
- [SocialParty 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/OnlineFramework/Source/Party/Public/Party/SocialParty.h)
- [SocialUser 头文件](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/OnlineFramework/Source/Party/Public/User/SocialUser.h)