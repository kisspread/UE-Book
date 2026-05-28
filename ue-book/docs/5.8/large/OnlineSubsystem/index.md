# Online Subsystem

> Shared code for interacting online subsystem implementations.

| 属性 | 值 |
|---|---|
| 中文名 | 在线子系统 |
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystem` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem) | |

## 用途

**Online Subsystem** 插件本身并不提供任何特定在线平台（如 Steam, PlayStation Network, Xbox Live 等）的具体功能实现。相反，它定义了一个统一、抽象的**接口层**，用于游戏和引擎与各种在线服务进行交互。

这个插件的核心价值在于：
1.  **平台抽象**：游戏代码只需依赖 `OnlineSubsystem` 插件提供的接口，就可以与底层平台进行通信。这使得游戏可以在不修改核心逻辑的情况下，发布到不同的游戏平台。
2.  **功能统一**：它标准化了如用户会话、好友列表、排行榜、成就、聊天、购买等在线功能的访问方式。每个具体的在线子系统插件（如 `OnlineSubsystemSteam`）负责实现这些接口。
3.  **解耦**：将在线服务的实现从游戏逻辑中分离出来，提高了代码的模块化和可维护性。

简而言之，如果你需要在游戏中实现任何在线功能，**Online Subsystem** 是你必须依赖的“中间人”或“合同定义者”。

## 使用场景

-   你正在开发一款需要支持多人在线对战或合作的游戏 → 你需要使用 `IOnlineSession` 接口来管理游戏会话。
-   你的游戏有好友系统、排行榜或成就系统 → 你需要使用 `IOnlineFriends`, `IOnlineLeaderboards`, `IOnlineAchievements` 等接口。
-   你希望游戏能够支持内购（IAP）→ 你需要使用 `IOnlinePurchase` 和 `IOnlineStoreV2` 接口。
-   你希望游戏代码能同时在 PC（Steam）、主机（PS/Xbox）甚至移动平台上编译运行，而无需为每个平台编写不同的网络代码 → **Online Subsystem** 提供了这种跨平台抽象。
-   你只是需要一个简单可靠的“玩家唯一标识符”（`FUniqueNetId`）来区分不同平台的玩家 → 这也是由 **Online Subsystem** 基础类型提供的。

## 蓝图用法

`Online Subsystem` 核心模块本身主要定义了纯 C++ 的抽象接口类，并未直接暴露大量的蓝图节点。实际的蓝图功能通常由具体的平台子系统插件（例如 `OnlineSubsystemSteam`）或在线工具插件（`OnlineSubsystemUtils`）提供。

然而，通过访问 `UOnlineSubsystemBlueprintLibrary` 等工具类，蓝图可以间接地使用部分功能。核心是理解如何通过蓝图获取和访问各种在线服务接口。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Online Subsystem` | 根据传入的 `SubsystemName` (如 `”Steam”`, `”NULL”`) 获取对应的在线子系统实例。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Session Interface` | 从在线子系统实例中获取会话接口（`IOnlineSession`）。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Friends Interface` | 从在线子系统实例中获取好友接口（`IOnlineFriends`）。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Leaderboard Interface` | 从在线子系统实例中获取排行榜接口（`IOnlineLeaderboards`）。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Achievements Interface` | 从在线子系统实例中获取成就接口（`IOnlineAchievements`）。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Identity Interface` | 从在线子系统实例中获取身份认证接口（`IOnlineIdentity`）。 | `UOnlineSubsystemBlueprintLibrary` |
| `Get Presence Interface` | 从在线子系统实例中获取状态接口（`IOnlinePresence`）。 | `UOnlineSubsystemBlueprintLibrary` |

### 使用示例（蓝图描述）

1.  **获取在线子系统**：在蓝图中，使用 `Get Online Subsystem` 节点。你可以将 `SubsystemName` 留空（使用默认平台服务）或指定一个名称（如 `”Steam”`）。将返回的 `IOnlineSubsystem` 对象引用传递给后续节点。
2.  **进行身份登录**：从上一步获取的子系统对象，使用 `Get Identity Interface` 节点获得 `IOnlineIdentity` 接口。然后调用 `Login` 方法，传入本地玩家索引（通常为0）和登录凭证。
3.  **查询好友列表**：获取 `IOnlineFriends` 接口后，调用 `ReadFriendsList` 方法（异步操作）。监听 `OnReadFriendsListComplete` 委托来获取结果。完成后，可以调用 `GetFriendsList` 来获取好友数据。
4.  **创建游戏会话**：获取 `IOnlineSession` 接口后，使用 `CreateSession` 方法创建一个自定义的会话会话。需要配置 `FOnlineSessionSettings` 来定义会话是否公开、最大人数、自定义键值对等。
5.  **查找并加入会话**：使用 `FindSessions` 方法搜索可用的游戏会话。在搜索结果回调中，选择一个会话，然后调用 `JoinSession` 尝试加入。

**重要提示**：蓝图中直接操作这些底层接口通常比较复杂。许多游戏会使用 **Online Subsystem Utils** 插件或自定义的蓝图库来封装这些调用，以简化蓝图的使用。

## C++ 用法

### 头文件引入

```cpp
// 核心在线子系统模块
#include "OnlineSubsystem.h"
#include "OnlineSubsystemModule.h"

// 引入你需要的特定接口，例如会话接口
#include "Interfaces/OnlineSessionInterface.h"
#include "OnlineSessionSettings.h"

// 引入基础类型
#include "OnlineSubsystemTypes.h"
```

### 基本用法

以下代码展示了如何在 C++ 中初始化并使用在线子系统的基本功能，以获取一个会话接口为例。

```cpp
// (来自引擎内部或示例)
void AMyGameMode::InitOnlineSubsystem()
{
    // 获取默认在线子系统（根据 DefaultEngine.ini 中的 [OnlineSubsystem] DefaultPlatformService 配置）
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        UE_LOG(LogTemp, Log, TEXT("Online Subsystem: %s"), *OnlineSub->GetSubsystemName().ToString());

        // 获取会话接口
        IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
        if (SessionInterface.IsValid())
        {
            // 绑定会话创建完成委托
            SessionInterface->AddOnCreateSessionCompleteDelegate_Handle(FOnCreateSessionCompleteDelegate::CreateUObject(this, &AMyGameMode::OnCreateSessionComplete));

            // 准备会话设置
            FOnlineSessionSettings SessionSettings;
            SessionSettings.NumPublicConnections = 4;
            SessionSettings.bShouldAdvertise = true;
            SessionSettings.bUsesPresence = true;
            SessionSettings.bAllowJoinInProgress = true;
            SessionSettings.Set(SETTING_MAPNAME, FString(TEXT("MyAwesomeMap")), EOnlineDataAdvertisementType::ViaOnlineServiceAndPing);

            // 创建会话
            SessionInterface->CreateSession(0, NAME_GameSession, SessionSettings);
        }
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to get Online Subsystem."));
    }
}

void AMyGameMode::OnCreateSessionComplete(FName SessionName, bool bWasSuccessful)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogTemp, Log, TEXT("Session '%s' created successfully."), *SessionName.ToString());
        // 会话创建成功后，可以开始监听加入请求或通知其他玩家
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create session."));
    }
}
```

### 进阶用法

更复杂的用法可能涉及使用身份接口登录、然后查询好友、最后邀请好友加入会话的组合流程。

```cpp
void AMyPlayerController::LoginAndInviteFriend()
{
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (!OnlineSub) return;

    // 1. 获取身份接口并尝试自动登录
    IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
    if (IdentityInterface.IsValid())
    {
        // 绑定登录完成委托
        IdentityInterface->AddOnLoginCompleteDelegate_Handle(0, FOnLoginCompleteDelegate::CreateUObject(this, &AMyPlayerController::OnLoginComplete));
        // 尝试使用平台默认方式自动登录
        IdentityInterface->AutoLogin(0);
    }
}

void AMyPlayerController::OnLoginComplete(int32 LocalUserNum, bool bWasSuccessful, const FUniqueNetId& UserId, const FString& Error)
{
    if (!bWasSuccessful)
    {
        UE_LOG(LogTemp, Error, TEXT("Login failed: %s"), *Error);
        return;
    }
    UE_LOG(LogTemp, Log, TEXT("Login successful. UserId: %s"), *UserId.ToString());

    // 2. 登录成功，获取好友接口并读取好友列表
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();
    if (FriendsInterface.IsValid())
    {
        FriendsInterface->AddOnReadFriendsListComplete_Handle(0, FOnReadFriendsListCompleteDelegate::CreateUObject(this, &AMyPlayerController::OnReadFriendsListComplete));
        FriendsInterface->ReadFriendsList(0, EFriendsLists::ToString(EFriendsLists::Default));
    }
}

void AMyPlayerController::OnReadFriendsListComplete(int32 LocalUserNum, bool bWasSuccessful, const FString& ListName, const FString& ErrorStr)
{
    if (!bWasSuccessful) return;

    // 3. 读取成功，获取第一个在线好友并邀请
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();
    if (FriendsInterface.IsValid())
    {
        TArray<TSharedRef<FOnlineFriend>> Friends;
        FriendsInterface->GetFriendsList(0, ListName, Friends);
        // 查找第一个在线好友
        for (const TSharedRef<FOnlineFriend>& Friend : Friends)
        {
            if (Friend->GetPresence().bIsOnline)
            {
                // 假设我们已经有了一个活动的会话 (NAME_GameSession)
                IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
                if (SessionInterface.IsValid())
                {
                    SessionInterface->SendSessionInviteToFriend(0, NAME_GameSession, *Friend->GetUserId());
                    UE_LOG(LogTemp, Log, TEXT("Invite sent to friend: %s"), *Friend->GetDisplayName());
                    break;
                }
            }
        }
    }
}
```

## Demo 示例

以下是一个最小的 C++ 示例，演示如何检查并获取在线子系统实例，并打印其信息。

**MyOnlineSubsystemDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyOnlineSubsystemDemo.generated.h"

UCLASS()
class AMyOnlineSubsystemDemo : public AActor
{
    GENERATED_BODY()

public:
    AMyOnlineSubsystemDemo();

    virtual void BeginPlay() override;

private:
    void QueryOnlineSubsystem();
};
```

**MyOnlineSubsystemDemo.cpp**
```cpp
#include "MyOnlineSubsystemDemo.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemModule.h"
#include "Interfaces/OnlineIdentityInterface.h" // 仅用于示例获取接口类型信息

AMyOnlineSubsystemDemo::AMyOnlineSubsystemDemo()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyOnlineSubsystemDemo::BeginPlay()
{
    Super::BeginPlay();
    QueryOnlineSubsystem();
}

void AMyOnlineSubsystemDemo::QueryOnlineSubsystem()
{
    // 获取在线子系统模块
    FOnlineSubsystemModule& OSSModule = FModuleManager::LoadModuleChecked<FOnlineSubsystemModule>("OnlineSubsystem");

    // 获取默认的在线子系统实例
    IOnlineSubsystem* OnlineSub = IOnlineSubsystem::Get();
    if (OnlineSub)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully obtained Online Subsystem!"));
        UE_LOG(LogTemp, Log, TEXT("  Subsystem Name: %s"), *OnlineSub->GetSubsystemName().ToString());
        UE_LOG(LogTemp, Log, TEXT("  Instance Name: %s"), *OnlineSub->GetInstanceName().ToString());
        UE_LOG(LogTemp, Log, TEXT("  Is Server: %s"), OnlineSub->IsServer() ? TEXT("True") : TEXT("False"));
        UE_LOG(LogTemp, Log, TEXT("  Is Dedicated: %s"), OnlineSub->IsDedicated() ? TEXT("True") : TEXT("False"));

        // 检查一些常用接口是否可用
        IOnlineIdentityPtr IdentityInterface = OnlineSub->GetIdentityInterface();
        UE_LOG(LogTemp, Log, TEXT("  Identity Interface Available: %s"), IdentityInterface.IsValid() ? TEXT("True") : TEXT("False"));

        IOnlineSessionPtr SessionInterface = OnlineSub->GetSessionInterface();
        UE_LOG(LogTemp, Log, TEXT("  Session Interface Available: %s"), SessionInterface.IsValid() ? TEXT("True") : TEXT("False"));

        IOnlineFriendsPtr FriendsInterface = OnlineSub->GetFriendsInterface();
        UE_LOG(LogTemp, Log, TEXT("  Friends Interface Available: %s"), FriendsInterface.IsValid() ? TEXT("True") : TEXT("False"));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to obtain Online Subsystem. Make sure a default platform service is configured in DefaultEngine.ini ([OnlineSubsystem] DefaultPlatformService=)"));
    }
}
```

## 模块依赖

要使用 **Online Subsystem** 插件，你的项目模块通常不需要直接依赖除了 `OnlineSubsystem` 以外的很多独特模块。它的核心职责是定义接口，具体实现由其他子系统插件完成。

但是，根据你使用的具体功能，可能会间接依赖其他模块。以下是 **Online Subsystem** 插件自身的一些关键依赖。

| 模块 | 用途 |
|---|---|
| `OnlineBase` | 在线子系统的基础设施，提供了一些通用的类型和工具。 |
| `OnlineSubsystemUtils` | 提供了许多在线功能的蓝图工具类和辅助函数。如果需要在蓝图中使用在线功能，通常需要此模块。 |
| `Json` | 被 `FOnlinePartyData` 等用于序列化/反序列化 JSON 数据。 |

**对于你的项目**：
- 如果你的代码只需要使用 `OnlineSubsystem` 定义的核心接口（`IOnlineSession` 等），通常只需在你的模块 `.Build.cs` 文件中添加 `"OnlineSubsystem"` 到 `PublicDependencyModuleNames` 或 `PrivateDependencyModuleNames`。
- 如果你需要蓝图节点（如 `Get Online Subsystem`），则还需要依赖 `"OnlineSubsystemUtils"`。
- 具体的平台子系统插件（如 `OnlineSubsystemSteam`）会自动声明它们对 `OnlineSubsystem` 的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-30 | `361e0c84` | Refactored FJsonObject to support both FString and UE::FSharedString | 重构 FJsonObject 以同时支持 FString 和 UE::FSharedString |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF。 |
| 2026-04-10 | `d6ab8d7c` | [iOS CTC Reporting]: | [iOS CTC 报告]：（具体改动未详述） |
| 2026-04-08 | `8baf75b6` | Switch to using an embedded weak framework for the MarketplaceKit swift lib to allow supporting APIs | 改为使用嵌入式弱框架引用 MarketplaceKit Swift 库，以支持相关 API |
| 2026-03-24 | `5a9ca5d3` | UE: Fix memory leak in FOnlineAsyncTaskManager cleanup | UE: 修复 FOnlineAsyncTaskManager 清理时的内存泄漏 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次提交，且包含实质性改动（如重构、内存泄漏修复、平台适配），表明该插件仍在被 Epic Games 积极维护和更新。
- **核心基础设施**：作为所有在线功能的基石，它几乎是所有联网游戏项目的必选依赖，其重要性不言而喻。
- **年龄**：作为“老古董”，其设计和 API 非常成熟稳定，但也可能存在一些历史包袱。
- **推荐使用**：**强烈推荐**。它是 UE 官方在线功能的标准方案，除非你有极端特殊的平台或需求，否则都应以此为基础构建在线功能。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystem)
- [官方文档 - Online Subsystem](https://docs.unrealengine.com/5.8/en-US/online-subsystem-in-unreal-engine/)
- [官方文档 - Sessions and Matchmaking](https://docs.unrealengine.com/5.8/en-US/sessions-and-matchmaking-in-unreal-engine/)
- [官方文档 - Online Leaderboard Interface](https://docs.unrealengine.com/5.8/en-US/online-leaderboard-interface-in-unreal-engine/)