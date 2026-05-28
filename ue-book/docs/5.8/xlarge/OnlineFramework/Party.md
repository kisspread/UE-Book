# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块、配置资产） |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 插件提供了一套完整的、与具体在线子系统（Online Subsystem）无关的社交与组队框架。它并非一个独立的在线服务实现，而是封装了游戏与在线服务交互的通用逻辑，解决了以下核心问题：

1.  **社交关系管理**：统一管理好友、屏蔽、最近玩家等关系，屏蔽底层不同平台（如 Epic、PSN、Xbox Live）的差异。
2.  **跨平台组队**：提供完整的队伍（Party）生命周期管理，支持跨平台队伍组建、状态同步（队伍数据、成员数据）、平台会话维护以及加入进行中游戏（Join in Progress）等高级功能。
3.  **实时聊天系统**：集成聊天室、私聊、频道管理以及斜杠命令（Slash Commands）系统。
4.  **用户存在状态**：集中处理和分发来自不同子系统的玩家在线状态和活动信息。
5.  **框架级通用功能**：包含热修复（Hotfix）、质量检测（Qos）、登录流程（LoginFlow）、游戏更新检查（PatchCheck）等支撑系统。

**为什么存在**：Epic 开发了《堡垒之夜》等大型跨平台游戏，需要一套强大的、可复用的底层社交架构来支撑其复杂的在线玩法。此插件即是这套架构的引擎侧实现，旨在为开发者提供开箱即用的多人社交游戏基础设施，避免每个项目重复造轮子。

## 使用场景

- 你正在开发一款支持跨平台（PC、主机、移动）组队和聊天的多人在线游戏（如射击、大逃杀、MMO）。
- 你需要一个完整的系统来管理玩家间的社交关系（好友、屏蔽、最近玩家），并在UI中展示。
- 你的游戏需要组建最多N人的小队，并支持队长管理、邀请、加入、踢出等操作，队伍状态需要在所有成员间实时同步。
- 游戏内需要集成世界聊天、队伍聊天、私聊等文本聊天功能，并支持自定义斜杠命令（如 `/invite`、`/kick`）。
- 你的游戏需要处理玩家的在线状态变化（如“在线”、“游戏中”、“离开”），并基于此更新UI或执行逻辑。

## 蓝图用法

该插件的核心类（如 `USocialManager`, `USocialParty`, `USocialUser`）主要通过 C++ 接口暴露功能，蓝图中的可调用节点较少，更多是用于事件绑定和数据读取。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreatePersistentParty` | 创建一个持久化队伍（通常在游戏开始时调用）。 | `USocialManager` |
| `GetPersistentParty` | 获取当前本地玩家所属的持久化队伍对象。 | `USocialManager` |
| `GetSocialToolkit` | 根据 `ULocalPlayer` 获取其专属的社交工具包（Social Toolkit），包含该玩家所有的社交状态。 | `USocialManager` |
| `GetPartyLeader` | 获取当前队伍的队长成员对象。 | `USocialParty` |
| `GetPartyMembers` | 获取当前队伍中所有成员对象的数组。 | `USocialParty` |
| `IsLocalPlayerPartyLeader` | 判断本地玩家是否是当前队伍的队长。 | `USocialParty` |
| `LeaveParty` | 让当前本地玩家离开所在队伍。 | `USocialParty` |
| `GetDisplayName` | 获取社交用户的显示名称。 | `USocialUser` |
| `IsOnline` | 获取社交用户的在线状态。 | `USocialUser` |
| `IsFriend` | 判断该社交用户是否为本地玩家的好友。 | `USocialUser` |
| `InviteToParty` | 邀请指定社交用户加入当前队伍。 | `USocialUser` (通过交互系统) |

### 使用示例（蓝图描述）

**监听队伍创建完成事件**：
1.  在你的游戏实例或玩家控制器中，获取 `USocialManager` 实例（通常通过 `GetGameInstance()->GetSubsystem<USocialSubsystem>()->GetSocialManager()`）。
2.  绑定 `USocialManager::OnPartyJoined` 事件。
3.  在事件处理节点中，可以安全地访问新加入的 `USocialParty` 对象，并获取其成员列表。

**响应玩家加入队伍请求**：
1.  绑定 `USocialParty::OnPartyMemberCreated` 事件。
2.  在事件处理节点中，获取新加入的 `UPartyMember` 对象。
3.  通过该对象的 `GetSocialUser()` 方法获取对应的 `USocialUser`，并调用其交互功能（如打招呼、赠送物品）。

## C++ 用法

### 头文件引入

```cpp
#include "OnlineFramework/SocialManager.h"
#include "OnlineFramework/Party/SocialParty.h"
#include "OnlineFramework/Party/PartyMember.h"
#include "OnlineFramework/User/SocialUser.h"
```

### 基本用法

以下示例展示了如何初始化社交系统并创建一个队伍。代码逻辑基于源码中常见的初始化和操作模式。

**（示例来源：基于 `USocialManager` 和 `USocialParty` 的典型用法推断）**

```cpp
// 在你的 GameInstance 子类中
#include "OnlineFramework/SocialManager.h"
#include "OnlineFramework/Party/SocialParty.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 1. 创建并初始化 SocialManager（通常作为 GameInstance 的子对象）
    SocialManager = NewObject<USocialManager>(this);
    SocialManager->AddToRoot(); // 防止被垃圾回收
    SocialManager->InitSocialManager();

    // 2. 绑定社交系统事件
    SocialManager->OnPartyJoined().AddUObject(this, &UMyGameInstance::HandlePartyJoined);
}

void UMyGameInstance::CreateGameParty()
{
    if (SocialManager)
    {
        // 3. 创建一个持久化队伍，使用默认配置
        SocialManager->CreatePersistentParty(FOnCreatePartyAttemptComplete::CreateLambda(
            [this](ECreatePartyCompletionResult Result)
            {
                if (Result == ECreatePartyCompletionResult::Succeeded)
                {
                    UE_LOG(LogTemp, Log, TEXT("Persistent party created successfully."));
                }
                else
                {
                    UE_LOG(LogTemp, Warning, TEXT("Failed to create persistent party."));
                }
            }));
    }
}

void UMyGameInstance::HandlePartyJoined(USocialParty& NewParty)
{
    UE_LOG(LogTemp, Log, TEXT("Joined a party with ID: %s"), *NewParty.GetPartyId().ToString());
    
    // 4. 获取队伍信息
    UPartyMember* Leader = NewParty.GetPartyLeader();
    if (Leader)
    {
        UE_LOG(LogTemp, Log, TEXT("Party leader: %s"), *Leader->GetDisplayName());
    }

    // 5. 遍历所有成员
    TArray<UPartyMember*> Members = NewParty.GetPartyMembers();
    for (UPartyMember* Member : Members)
    {
        // 获取每个成员的社交用户对象，用于进一步交互
        USocialUser* User = Member->GetSocialUser();
        if (User)
        {
            UE_LOG(LogTemp, Verbose, TEXT("Member: %s, Online: %s"), 
                *User->GetDisplayName(),
                User->IsOnline() ? TEXT("Yes") : TEXT("No"));
        }
    }
}

// 在 GameInstance 关闭时清理
void UMyGameInstance::Shutdown()
{
    if (SocialManager)
    {
        SocialManager->ShutdownSocialManager();
        SocialManager->RemoveFromRoot();
        SocialManager = nullptr;
    }
    Super::Shutdown();
}
```

### 进阶用法

**处理跨平台用户标识和平台会话**：

Social Framework 的核心之一是处理来自不同子系统的唯一用户标识（`FUniqueNetIdRepl`）。以下代码展示了如何安全地检查用户信息。

```cpp
// 在某个需要检查玩家信息的地方
void UMyWidget::UpdatePlayerInfo(const UPartyMember* Member)
{
    if (!Member) return;

    // 获取主子系统（通常是 Epic Online Services）的ID
    FUniqueNetIdRepl PrimaryId = Member->GetPrimaryNetId();
    if (PrimaryId.IsValid())
    {
        // 通过 SocialToolkit 获取或查找对应的 SocialUser
        USocialToolkit* Toolkit = SocialManager->GetSocialToolkit(0); // 通常玩家0
        USocialUser* User = Toolkit->FindUser(PrimaryId);
        if (User)
        {
            // 获取该用户在不同子系统下的ID
            FUniqueNetIdRepl PlatformId = User->GetUserId(ESocialSubsystem::Platform);
            // 使用平台ID进行特定平台的操作（如查看平台档案）
        }
    }

    // 直接检查成员的平台会话信息
    const FPartyMemberRepData& RepData = Member->GetRepData();
    // 注意：访问复制数据中的平台信息，需要该成员数据已同步完成
}
```

## Demo 示例

以下是一个最小化的游戏场景实现，演示如何创建游戏实例、初始化社交系统、创建并管理一个简单的队伍。

**MyGameInstance.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "OnlineFramework/SocialManager.h"
#include "OnlineFramework/Party/SocialParty.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	virtual void Init() override;
	virtual void Shutdown() override;

	UFUNCTION(BlueprintCallable, Category = "Online")
	void CreateGameParty();

private:
	UPROPERTY()
	TObjectPtr<USocialManager> SocialManager;

	void HandlePartyJoined(USocialParty& NewParty);
	void HandlePartyMemberCreated(UPartyMember& NewMember);
};
```

**MyGameInstance.cpp**
```cpp
#include "MyGameInstance.h"
#include "OnlineFramework/Party/PartyMember.h"
#include "OnlineFramework/User/SocialUser.h"

void UMyGameInstance::Init()
{
	Super::Init();

	// 创建社交管理器
	SocialManager = NewObject<USocialManager>(this);
	SocialManager->AddToRoot();
	SocialManager->InitSocialManager();

	// 绑定事件：加入队伍时
	SocialManager->OnPartyJoined().AddUObject(this, &UMyGameInstance::HandlePartyJoined);

	UE_LOG(LogTemp, Log, TEXT("Social Manager initialized."));
}

void UMyGameInstance::CreateGameParty()
{
	if (SocialManager && !SocialManager->GetPersistentParty())
	{
		SocialManager->CreatePersistentParty();
		UE_LOG(LogTemp, Log, TEXT("Attempting to create persistent party..."));
	}
	else if (SocialManager->GetPersistentParty())
	{
		UE_LOG(LogTemp, Warning, TEXT("A persistent party already exists."));
	}
}

void UMyGameInstance::HandlePartyJoined(USocialParty& NewParty)
{
	UE_LOG(LogTemp, Log, TEXT("Successfully joined party %s"), *NewParty.GetPartyId().ToString());

	// 绑定事件：有新成员加入时
	NewParty.OnPartyMemberCreated().AddUObject(this, &UMyGameInstance::HandlePartyMemberCreated);

	// 立即处理已存在的成员
	TArray<UPartyMember*> Members = NewParty.GetPartyMembers();
	for (UPartyMember* Member : Members)
	{
		HandlePartyMemberCreated(*Member);
	}
}

void UMyGameInstance::HandlePartyMemberCreated(UPartyMember& NewMember)
{
	if (USocialUser* User = NewMember.GetSocialUser())
	{
		UE_LOG(LogTemp, Log, TEXT("Party member joined: %s"), *User->GetDisplayName());

		// 示例：当有新成员加入时，你可以在这里触发一个游戏内事件或更新UI
		// OnPartyMemberJoinedBlueprintEvent.Broadcast(User->GetDisplayName());
	}
}

void UMyGameInstance::Shutdown()
{
	if (SocialManager)
	{
		SocialManager->ShutdownSocialManager();
		SocialManager->RemoveFromRoot();
		SocialManager = nullptr;
	}

	Super::Shutdown();
}
```

## 模块依赖

`Party` 模块是此插件的核心，其依赖如下（摘自 `Party.Build.cs`）：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | 为 Xbox/GDK 平台提供特定的在线会话和朋友列表支持。**这是一个平台特定依赖。** |
| `OnlineSubsystem` | 提供与平台无关的在线服务抽象层，Party 模块通过它与底层 OSS 交互。 |
| `OnlineSubsystemUtils` | 提供在线子系统的通用工具函数和蓝图支持。 |
| `Engine` | 引擎核心模块，提供游戏实例、世界、定时器等基础功能。 |
| `CoreUObject` | UObject 系统基础。 |
| `Slate`, `SlateCore`, `UMG` | 用于构建社交调试工具和可能的UI界面。 |

**开发者说明**：要在你自己的项目中使用 `Party` 模块，你的项目 `.Build.cs` 文件需要添加对 `Party`、`OnlineSubsystem` 和 `OnlineSubsystemUtils` 的依赖。`OnlineSubsystemGDK` 的依赖取决于你是否需要支持 Xbox 平台。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复热修复系统中，当后端无更新时，某些预置修复无法正确应用的问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用 Epic 队伍镜像功能时，为邀请和“请求加入”操作添加了保护性检查。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为平台会话监控器添加钩子，允许游戏在平台会话设置中插入特殊键值。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复了热修复管理器在加载时输出摘要日志的功能。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 调整了队伍初始化的广播时机，在首次状态更新处理完成后才广播，避免过早触发。 |

### 维护评价

OnlineFramework 插件是一个**成熟、复杂且处于长期维护状态**的核心模块。

-   **年龄与稳定性**：创建于 2016 年，已有约 10 年历史，是 Epic 旗舰产品《堡垒之夜》的底层支撑之一，经过了海量用户和复杂场景的实战检验，架构稳定。
-   **更新频率**：从近期提交记录看，仍处于**活跃维护**中（最近更新在 2026 年 5 月）。更新内容主要以 Bug 修复、平台兼容性增强和功能微调为主，而非大规模重构，表明系统已进入稳定期。
-   **使用建议**：
    -   **强烈推荐**：对于需要开箱即用的跨平台社交和组队功能的中大型项目，这是一个非常强大的选择。它能极大节省开发时间，并避免踩坑。
    -   **注意事项**：
        1.  **默认未启用**：需要在项目的 `.uproject` 文件中手动启用该插件。
        2.  **复杂度高**：源码量大（121个文件），内部抽象层次多。深度定制或排查问题需要较深的源码阅读能力。
        3.  **平台依赖**：部分功能（如 `Party` 模块）强依赖于特定的 `OnlineSubsystem`（如 `OnlineSubsystemGDK`），需要为你的目标平台配置对应的 OSS。
        4.  **文档缺失**：Epic 官方没有提供此插件的公开文档，学习和使用主要依赖源码分析和社区经验。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- 官方文档：无公开官方文档。
- [测试用例]：引擎测试目录 `Engine/Tests/Runtime/OnlineFramework/` 下可能包含相关测试，但不在插件目录内。