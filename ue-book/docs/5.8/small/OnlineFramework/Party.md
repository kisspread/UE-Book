# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic 为在线多人游戏提供的**社交与派对系统框架层**。它并非一个具体的在线子系统实现（如 Steam、PSN、Xbox Live），而是在这些子系统之上构建的**高级抽象层**，提供统一的：

1. **Party（派对）系统**：创建、加入、离开、管理多人派对，支持跨平台会话同步、数据复制（RepData）、加入进行中（Join in Progress）等完整生命周期
2. **社交用户管理**：统一的朋友关系、阻止、最近玩家、在线状态等社交图谱，跨多个 OSS（Primary + Platform）聚合
3. **聊天系统**：多频道聊天（全局、队伍、私聊）、斜杠命令系统、消息路由
4. **交互系统**：可扩展的社交交互框架（加好友、邀请派对、踢人等），支持自定义交互注册

该插件存在的意义：不同平台（PC/主机/移动端）的在线服务 API 差异巨大，游戏层需要一个统一的抽象来处理社交和派对逻辑，避免每个平台重复实现。

## 使用场景

- 你的游戏需要**跨平台组队**功能 → 使用 Party 模块
- 你需要管理**好友列表、在线状态、阻止用户**等社交关系 → 使用 USocialToolkit / USocialUser
- 你的游戏需要**队伍内聊天或私聊**功能 → 使用聊天子系统（USocialChatManager 等）
- 你需要在多人游戏中实现**加入进行中（Join in Progress）**的预留系统 → 使用 Party 的 Beacon + JIP 流程
- 你的游戏需要**平台会话同步**（如 PSN Party 同步 XBL 会话） → 使用 FPartyPlatformSessionMonitor
- 你需要**热更新配置**而不发补丁 → 使用 Hotfix 模块
- 你需要在登录前检查客户端版本 → 使用 PatchCheck 模块
- 你需要限制未成年玩家游戏时间 → 使用 PlayTimeLimit 模块
- 你需要自动重连已断开的对局 → 使用 Rejoin 模块

## 蓝图用法

本插件的大部分核心逻辑（USocialManager、USocialParty、USocialUser 等）均为 C++ 类，**没有大量暴露 BlueprintCallable 节点**。社交交互通过 `FSocialInteractionHandle` 系统实现，但该系统主要面向 C++ 扩展。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Exec` (控制台命令) | 通过控制台执行调试命令（登录/组队/聊天等） | `USocialManager` |
| `Exec` (调试工具) | 调试用控制台命令（登录实例、加入队伍、发送数据等） | `USocialDebugTools` |
| `JoinChatRoomPublic` | 加入公开聊天室 | `USocialChatManager` |
| `JoinChatRoomPrivate` | 加入私有聊天室 | `USocialChatManager` |
| `ExitChatRoom` | 离开聊天室 | `USocialChatManager` |
| `SendMessage` | 发送聊天消息 | `USocialChatChannel` |
| `LeaveParty` | 离开当前派对 | `USocialParty` |

### 使用示例（蓝图描述）

本插件设计上主要通过 C++ 继承和扩展使用。典型蓝图集成路径：

1. 创建 `USocialManager` 子类，在 `GameInstance` 初始化时调用 `InitSocialManager()`
2. 创建 `USocialToolkit` 子类处理每个本地玩家的社交逻辑
3. 创建 `USocialParty` 子类实现游戏特定的派对配置和审批逻辑
4. 创建 `UPartyMember` 子类管理成员特有数据

对于简单的调试测试，可以使用 `USocialDebugTools` 提供的控制台命令：
```
// 在控制台中
SocialDebugTools Login <InstanceName>
SocialDebugTools JoinParty <InstanceName> <FriendName>
SocialDebugTools LeaveParty <InstanceName>
SocialDebugTools JoinInProgress <InstanceName>
```

## C++ 用法

### 头文件引入

```cpp
#include "SocialManager.h"
#include "SocialToolkit.h"
#include "SocialUser.h"
#include "Party/SocialParty.h"
#include "Party/PartyMember.h"
#include "Party/PartyTypes.h"
#include "Chat/SocialChatManager.h"
```

### 基本用法

**初始化社交系统**（基于 `USocialManager::InitSocialManager` 的设计）：

```cpp
// 在 GameInstance 的 Init() 中
void UMyGameInstance::Init()
{
    Super::Init();
    
    // 创建社交管理器
    SocialManager = NewObject<UMySocialManager>(this);
    SocialManager->InitSocialManager();
}
```

**创建自定义派对类型**（来源：`Public/Party/SocialParty.h`）：

```cpp
// MyParty.h
UCLASS()
class UMyParty : public USocialParty
{
    GENERATED_BODY()
    
public:
    // 指定成员类型
    virtual TSubclassOf<UPartyMember> GetDesiredMemberClass(bool bLocalPlayer) const override
    {
        return UMyPartyMember::StaticClass();
    }
    
    // 自定义隐私设置
    virtual FPartyPrivacySettings GetDesiredPrivacySettings() const override
    {
        FPartyPrivacySettings Settings;
        Settings.PartyType = EPartyType::FriendsOnly;
        Settings.PartyInviteRestriction = EPartyInviteRestriction::AnyMember;
        Settings.bOnlyLeaderFriendsCanJoin = false;
        return Settings;
    }
    
    // 自定义审批逻辑
    virtual FPartyJoinApproval EvaluateJoinRequest(
        const TArray<IOnlinePartyUserPendingJoinRequestInfoConstRef>& Players, 
        bool bFromJoinRequest) const override
    {
        FPartyJoinApproval Approval;
        // 自定义检查逻辑...
        if (/* 例如检查模式限制 */)
        {
            Approval.SetDenialReason(EPartyJoinDenialReason::GameModeRestricted);
        }
        return Approval;
    }
};
```

**管理派对数据复制**（来源：`Public/Party/PartyDataReplicator.h`、`PartyTypes.h`）：

```cpp
// 自定义派对复制数据
USTRUCT()
struct FMyPartyRepData : public FOnlinePartyRepDataBase
{
    GENERATED_BODY()
    
    // 暴露可复制的属性，自动生成 getter/setter 和变更事件
    UPROPERTY()
    FString CurrentGameMode;
    EXPOSE_REP_DATA_PROPERTY(FMyPartyRepData, FString, CurrentGameMode);
    
    UPROPERTY()
    int32 MaxTeamSize;
    EXPOSE_REP_DATA_PROPERTY(FMyPartyRepData, int32, MaxTeamSize);
    
protected:
    virtual bool CanEditData() const override;
    virtual void CompareAgainst(const FOnlinePartyRepDataBase& OldData) const override;
    virtual const USocialParty* GetOwnerParty() const override;
};

// 在派对中使用
class UMyParty : public USocialParty
{
    // ...
    void InitializePartyRepData() override
    {
        FMyPartyRepData& RepData = /* ... */;
        PartyDataReplicator.EstablishRepDataInstance(RepData);
    }
};
```

### 进阶用法

**跨平台社会工具包**（来源：`Public/SocialToolkit.h`）：

```cpp
// 获取当前本地玩家的社交工具包
void UMyUI::RefreshFriendsList()
{
    USocialToolkit* Toolkit = USocialToolkit::GetToolkitForPlayer<USocialToolkit>(GetOwningLocalPlayer());
    if (!Toolkit) return;
    
    // 查找特定用户
    FUniqueNetIdRepl TargetId = /* ... */;
    USocialUser* User = Toolkit->FindUser(TargetId);
    
    // 或等待用户初始化后再操作
    Toolkit->QueueUserDependentAction(TargetId, 
        [this](USocialUser& User) 
        {
            if (User.IsFriend(ESocialSubsystem::Primary))
            {
                // 显示好友在线状态
                EOnlinePresenceState::Type Status = User.GetOnlineStatus();
            }
        });
    
    // 获取已加入的队伍
    USocialParty* Party = Toolkit->GetSocialManager().GetPersistentParty();
    if (Party)
    {
        for (UPartyMember* Member : Party->GetPartyMembers())
        {
            UE_LOG(LogTemp, Log, TEXT("Member: %s, Leader: %s"), 
                *Member->GetDisplayName(),
                Member->IsPartyLeader() ? TEXT("Yes") : TEXT("No"));
        }
    }
}
```

**自定义社交交互**（来源：`Public/Interactions/`）：

```cpp
// 声明自定义交互
DECLARE_SOCIAL_INTERACTION_EXPORT(MYGAME_API, TradeWithPlayer);

// 实现交互
DEFINE_SOCIAL_INTERACTION(TradeWithPlayer)

FText FSocialInteraction_TradeWithPlayer::GetDisplayName(const USocialUser& User)
{
    return NSLOCTEXT("Trade", "TradeLabel", "发起交易");
}

bool FSocialInteraction_TradeWithPlayer::CanExecute(const USocialUser& User)
{
    return User.IsOnline() && User.IsPlayingThisGame();
}

void FSocialInteraction_TradeWithPlayer::ExecuteInteraction(USocialUser& User)
{
    // 打开交易 UI
}
```

**自定义用户列表过滤**（来源：`Public/User/ISocialUserList.h`）：

```cpp
// 创建一个仅显示在线且可加入的跨平台好友列表
FSocialUserListConfig Config;
Config.Name = TEXT("OnlineFriends");
Config.RelationshipType = ESocialRelationship::Friend;
Config.RequiredPresenceFlags = ESocialUserStateFlags::Online | ESocialUserStateFlags::SameApp;
Config.bAutoUpdate = true;

TSharedRef<ISocialUserList> OnlineFriends = Toolkit->CreateUserList(Config);
OnlineFriends->OnUserAdded().AddLambda([](USocialUser& User) {
    UE_LOG(LogTemp, Log, TEXT("Online friend: %s"), *User.GetDisplayName());
});
```

## Demo 示例

```cpp
// MySocialManager.h
#pragma once
#include "SocialManager.h"
#include "MySocialManager.generated.h"

UCLASS()
class MYGAME_API UMySocialManager : public USocialManager
{
    GENERATED_BODY()
    
protected:
    virtual TSubclassOf<USocialParty> GetPartyClassForType(
        const FOnlinePartyTypeId& PartyTypeId) const override;
    virtual ECrossplayPreference GetCrossplayPreference() const override;
};

// MySocialManager.cpp
#include "MySocialManager.h"
#include "MyParty.h"

TSubclassOf<USocialParty> UMySocialManager::GetPartyClassForType(
    const FOnlinePartyTypeId& PartyTypeId) const
{
    return UMyParty::StaticClass();
}

ECrossplayPreference UMySocialManager::GetCrossplayPreference() const
{
    // 根据用户设置返回跨平台偏好
    return ECrossplayPreference::OptedIn;
}
```

```cpp
// MyParty.h
#pragma once
#include "Party/SocialParty.h"
#include "Party/PartyMember.h"
#include "MyParty.generated.h"

USTRUCT()
struct FMyPartyRepData : public FOnlinePartyRepDataBase
{
    GENERATED_BODY()
    
    UPROPERTY()
    FString GameModeName;
    EXPOSE_REP_DATA_PROPERTY(FMyPartyRepData, FString, GameModeName);
    
protected:
    virtual bool CanEditData() const override { return OwnerParty.IsValid(); }
    virtual const USocialParty* GetOwnerParty() const override { return OwnerParty.Get(); }
    
    TWeakObjectPtr<const USocialParty> OwnerParty;
};

UCLASS()
class MYGAME_API UMyPartyMember : public UPartyMember
{
    GENERATED_BODY()
};

UCLASS()
class MYGAME_API UMyParty : public USocialParty
{
    GENERATED_BODY()
    
protected:
    virtual TSubclassOf<UPartyMember> GetDesiredMemberClass(bool bLocalPlayer) const override
    {
        return UMyPartyMember::StaticClass();
    }
    
    virtual FPartyPrivacySettings GetDesiredPrivacySettings() const override
    {
        return FPartyPrivacySettings();
    }
    
    virtual void InitializePartyRepData() override
    {
        FMyPartyRepData RepData;
        RepData.OwnerParty = this;
        PartyDataReplicator.EstablishRepDataInstance(RepData);
    }
    
    virtual FPartyJoinApproval EvaluateJoinRequest(
        const TArray<IOnlinePartyUserPendingJoinRequestInfoConstRef>& Players,
        bool bFromJoinRequest) const override
    {
        FPartyJoinApproval Approval;
        // 默认允许，可自定义
        return Approval;
    }
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | Party 模块依赖，Xbox/GDK 平台在线子系统支持 |
| `OnlineSubsystem` | 所有模块的核心依赖，在线子系统接口 |
| `OnlineSubsystemUtils` | 在线子系统工具函数 |
| `Networking` | 网络层支持（Beacon 连接等） |
| `Sockets` | 套接字通信 |
| `OnlineServicesInterface` / `OnlineServicesCommon` | 新版在线服务接口（V2 Presence 等） |

> 注：该插件包含 8 个模块（Hotfix、Lobby、LoginFlow、Party、PatchCheck、PlayTimeLimit、Qos、Rejoin），各模块有各自独特的依赖。上表仅列出 Party 模块中较特殊的依赖。其余模块多仅依赖标准 Core/Engine/OnlineSubsystem。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exist | 修复无后端热修复时内置热修复不生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | Epic 派对镜像启用时保护邀请和加入请求调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platform session | 为平台会话监控添加钩子，允许游戏向平台会话添加特殊键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复加载时的摘要日志 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在首次更新处理完成后再广播派对初始化事件 |

### 维护评价

OnlineFramework 是 Epic 在线服务架构中的**核心基础设施**，自 2016 年从引擎内部迁移为插件后持续维护至今。该插件具有以下特点：

- **活跃维护**：最近更新集中在 2026 年 4-5 月，说明 Epic 内部仍在积极使用和维护
- **成熟稳定**：经过 9 年迭代，核心 API（Party、SocialManager、SocialUser）已经非常成熟
- **默认禁用**：`EnabledByDefault = false`，需要游戏项目手动启用并继承扩展
- **大量废弃标记**：代码中包含多个 5.6/5.7/5.8 版本的 `UE_DEPRECATED` 标记，说明 API 在持续演进，需注意版本兼容性
- **高度可扩展**：几乎所有核心类都是 Abstract 或带 virtual 方法，设计上鼓励游戏项目继承实现

**推荐使用**：如果你的多人游戏需要跨平台社交和派对功能，这是 Epic 官方推荐的基础设施。但注意需要大量 C++ 继承和定制工作，不适用于简单的原型开发。

⚠️ 注意：该插件默认禁用，需要在 .uproject 或项目设置中手动启用，并且需要实现自己的子类才能正常使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [官方文档](https://docs.unrealengine.com/en-US/game-framework-and-plugins/online-framework/)（无特定 URL，参考 Online Subsystem 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Tests)（如存在）