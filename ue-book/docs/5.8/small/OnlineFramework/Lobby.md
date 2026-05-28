# Online Framework Plugin

> Shared code for interacting with online gameplay services.

| 属性 | 值 |
|---|---|
| 中文名 | 房间大厅 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Hotfix` (Runtime), `Lobby` (Runtime), `LoginFlow` (Runtime), `Party` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Qos` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 🏛️ 文物（约 10 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途
该插件（OnlineFramework）的核心功能是提供一套**基于在线信标（Online Beacon）的玩家匹配大厅（Lobby）系统**。它解决了在多人在线游戏中，玩家在正式加入游戏服务器之前，需要一个集中的、轻量级的场所进行等待、查看其他玩家、组队协调、准备开始游戏的需求。它本质上是一个独立于游戏主服务器的“预备房间”，通过网络信标进行通信，负责管理玩家的登录、退出、状态同步以及最终的跳转到游戏服务器。

## 使用场景
- 你需要为你的多人游戏创建一个自定义的匹配大厅，让玩家在匹配到对手后等待所有人准备就绪，然后再一起进入游戏。
- 你在构建一个需要玩家进行社交互动（如邀请、查看队伍）的聚会系统，该系统独立于实际的游戏战斗服务器。
- 你的游戏需要实现一个“准备就绪”检查机制，只有当大厅内所有玩家都点击“准备”后，才能开始游戏。

## 蓝图用法

### 核心节点
大厅系统主要由 `ALobbyBeaconHost` (服务端宿主) 和 `ALobbyBeaconClient` (客户端连接) 以及 `ALobbyBeaconState` (共享状态) 构成。蓝图中通常通过客户端信标与系统交互。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConnectToLobby` | 客户端连接到指定的会话大厅 | `ALobbyBeaconClient` |
| `DisconnectFromLobby` | 客户端主动断开与大厅的连接 | `ALobbyBeaconClient` |
| `JoiningServer` | 客户端通知大厅自己即将跳转到游戏服务器 | `ALobbyBeaconClient` |
| `ClientJoinGame` | 服务器通知客户端可以跳转到游戏服务器 | `ALobbyBeaconClient` |
| `KickPlayer` | 客户端（通常是房主）请求踢出另一个玩家 | `ALobbyBeaconClient` |
| `SetPartyOwnerId` | 客户端（请求玩家）更新队伍的拥有者 | `ALobbyBeaconClient` |
| `GetPlayer` | 通过唯一ID获取大厅中的某个玩家状态对象 | `ALobbyBeaconState` |
| `GetAllPlayers` | 获取大厅中所有玩家的状态信息数组 | `ALobbyBeaconState` |
| `HasLobbyStarted` | 检查大厅是否已经开始（倒计时结束） | `ALobbyBeaconState` |

### 使用示例（蓝图描述）
1.  **服务端**：首先，使用 `Create Online Beacon` 节点生成一个 `ALobbyBeaconHost` 对象。调用 `Init` 函数并传入当前会话名（如 `NAME_GameSession`）来初始化它。随后，调用 `SetupLobbyState` 来创建并配置大厅的状态管理对象 `ALobbyBeaconState`。
2.  **客户端**：当玩家需要加入大厅时，生成一个 `ALobbyBeaconClient` 对象。通过搜索在线会话获取 `FOnlineSessionSearchResult`，然后调用 `ConnectToLobby` 函数连接到对应服务器的信标。连接成功后会触发 `OnLobbyConnectionEstablished` 委托。
3.  **状态同步**：客户端可以通过 `LobbyState` 属性访问 `ALobbyBeaconState` 对象，从而获取 `Players` 数组以显示所有玩家列表。当玩家加入、离开或状态变化时，会触发相应的委托（如 `OnPlayerJoined`, `OnPlayerLeft`）。
4.  **开始游戏**：当大厅满足条件（如玩家全部准备、倒计时结束），服务端调用 `ClientJoinGame` 的 RPC 通知所有客户端。客户端收到后，执行实际的服务器旅行（Travel）操作。

## C++ 用法

### 头文件引入
```cpp
#include "LobbyModule.h"
#include "LobbyBeaconHost.h"
#include "LobbyBeaconClient.h"
#include "LobbyBeaconState.h"
#include "LobbyBeaconPlayerState.h"
```

### 基本用法
以下代码展示了如何在服务端初始化一个大厅信标主机。虽然未提供官方测试文件，但此模式与引擎内其他信标和在线子系统的用法一致。
*（用法推断自头文件 `LobbyBeaconHost.h`）*
```cpp
// 在你的游戏模式或会话管理器中
void AMyGameMode::SetupLobbyForSession(FName SessionName)
{
    // 生成并初始化大厅信标主机
    ALobbyBeaconHost* LobbyBeaconHost = GetWorld()->SpawnActor<ALobbyBeaconHost>(ALobbyBeaconHost::StaticClass());
    if (LobbyBeaconHost)
    {
        // 初始化信标，关联到指定的会话
        LobbyBeaconHost->Init(SessionName);
        
        // 设置大厅状态，指定最大玩家数
        LobbyBeaconHost->SetupLobbyState(MaxPlayers);
        
        // 此时，服务器已准备好接收客户端通过 LobbyBeaconClient 的连接
    }
}
```

### 进阶用法
你可以通过派生自定义的 `ALobbyBeaconPlayerState` 来扩展每个玩家在大厅中的数据。
*（概念推断自 `LobbyBeaconPlayerState.h` 的接口）*
```cpp
// MyLobbyPlayerState.h
UCLASS()
class AMyLobbyPlayerState : public ALobbyBeaconPlayerState
{
    GENERATED_BODY()

public:
    // 自定义数据，例如玩家选择的皮肤ID，需要同步
    UPROPERTY(ReplicatedUsing=OnRep_SelectedSkinId)
    FString SelectedSkinId;

    UFUNCTION()
    void OnRep_SelectedSkinId();

    // 重写网络复制方法，添加自定义数据
    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```

## Demo 示例
这是一个简单的自定义大厅玩家状态和使用大厅信标的示例片段。
*（示例基于头文件接口设计，需结合完整项目使用）*
```cpp
// MyLobbyPlayerState.h
#pragma once
#include "LobbyBeaconPlayerState.h"
#include "MyLobbyPlayerState.generated.h"

UCLASS()
class AMyLobbyPlayerState : public ALobbyBeaconPlayerState
{
    GENERATED_BODY()

public:
    UPROPERTY(Replicated, BlueprintReadOnly)
    bool bIsReady = false;

    UPROPERTY(Replicated, BlueprintReadOnly)
    int32 SelectedCharacterId = -1;

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};
```
```cpp
// MyLobbyPlayerState.cpp
#include "MyLobbyPlayerState.h"
#include "Net/UnrealNetwork.h"

void AMyLobbyPlayerState::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
    Super::GetLifetimeReplicatedProps(OutLifetimeProps);
    DOREPLIFETIME(AMyLobbyPlayerState, bIsReady);
    DOREPLIFETIME(AMyLobbyPlayerState, SelectedCharacterId);
}
```

```cpp
// 在游戏逻辑中使用（例如客户端）
void AMyPlayerController::TryJoinLobby(const FOnlineSessionSearchResult& SearchResult)
{
    // 生成客户端信标
    UWorld* World = GetWorld();
    ALobbyBeaconClient* LobbyClient = World->SpawnActor<ALobbyBeaconClient>(ALobbyBeaconClient::StaticClass());
    if (LobbyClient)
    {
        // 监听连接和玩家事件
        LobbyClient->OnLobbyConnectionEstablished().AddUObject(this, &AMyPlayerController::OnConnectedToLobby);
        LobbyClient->OnPlayerJoined().AddUObject(this, &AMyPlayerController::OnPlayerJoinedLobby);
        
        // 发起连接
        LobbyClient->ConnectToLobby(SearchResult);
    }
}

void AMyPlayerController::OnConnectedToLobby()
{
    UE_LOG(LogTemp, Log, TEXT("Successfully connected to lobby beacon!"));
    // 此时可以开始访问 LobbyClient->LobbyState 来获取玩家列表
}
```

## 模块依赖
该插件本身是在线子系统框架的一部分，其模块通常依赖于更基础的在线模块。

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 提供在线子系统的核心抽象和接口，大厅功能建立在此之上。 |
| `OnlineSubsystemUtils` | 提供在线子系统的通用工具类，可能被内部使用。 |
| `OnlineSubsystemGDK` | 对于Xbox/GDK平台的支持，从依赖项中可见。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exis | 修复热修复插件在没有后端热修复时，某些内置热修复无法应用的问题。 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled. | 当启用 Epic 派对镜像功能时，为邀请和加入社交派对的调用添加保护。 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platf | 为 `PartyPlatformSessionMonitor` 添加钩子，允许游戏派对向平台会话添加特殊键。 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复管理器在加载时输出摘要日志的功能。 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理完首次更新后，再广播派对初始化完成事件。 |

### 维护评价
- **活跃维护**：尽管插件创建于2016年（文物级），但从近期的Git记录看，它仍在被积极维护。最近几次提交（2026年4月底至5月）都集中在修复Bug和增强Party、Hotfix等子模块的功能上。
- **核心稳定**：Lobby模块的核心代码（如信标类）在最近提交中未见改动，表明其核心逻辑已非常稳定。
- **状态健康**：该插件是UE在线框架的关键组成部分，被广泛用于管理多人游戏的前置流程。虽然默认未启用（`EnabledByDefault=false`），但这是因为它是可选的高级功能。
- **推荐使用**：对于需要自定义大厅体验的多人游戏项目，推荐启用和使用此插件。其API设计成熟，经过了长期验证。注意，它需要与特定的在线子系统（如OSS, GDK）配合工作。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [官方文档](https://docs.unrealengine.com/en-US/Gameplay/Networking/Online/) (未在.uplugin中指定，此为通用在线文档入口)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Tests) (如果存在)