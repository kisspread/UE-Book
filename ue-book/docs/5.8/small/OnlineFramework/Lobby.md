# Online Framework Plugin

> Shared code for interacting with online gameplay services.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | 在线框架 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `Qos` (Runtime), `Party` (Runtime), `Lobby` (Runtime), `Hotfix` (Runtime), `LoginFlow` (Runtime), `PatchCheck` (Runtime), `PlayTimeLimit` (Runtime), `Rejoin` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2016-07-13 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 UE 在线子系统（Online Subsystem）之上的**通用在线交互框架层**，提供与具体平台无关的高层在线功能。它不直接对接 Steam、PlayStation 等平台 SDK，而是封装了所有在线游戏都需要的通用逻辑：

- **Lobby（大厅）**：基于 Online Beacon 的轻量级大厅系统，在玩家正式连接游戏服务器前提供等待房间、玩家管理、踢人等功能
- **Party（派对）**：好友组队系统，支持跨平台派对同步与平台会话镜像
- **Qos（服务质量）**：网络质量探测与延迟评估，用于服务器选择和匹配
- **Hotfix（热修复）**：运行时配置下发与热更新，无需重新打包即可修复服务端配置
- **LoginFlow（登录流程）**：平台登录流程抽象层
- **PatchCheck（补丁检查）**：版本与补丁一致性校验
- **PlayTimeLimit（游戏时长限制）**：特别是针对青少年玩家的游玩时间管控
- **Rejoin（重连）**：断线重连机制

该插件默认不启用（`EnabledByDefault: false`），需要在项目设置中手动开启。

## 使用场景

- 你正在开发一款多人在线游戏，需要在匹配成功后、正式进入游戏前有一个等待大厅 → 用 **Lobby** 模块
- 你需要让好友组队后再一起匹配服务器 → 用 **Party** 模块
- 你需要在多个可用服务器间选择延迟最低的 → 用 **Qos** 模块
- 你需要在不停服的情况下下发配置修复 → 用 **Hotfix** 模块
- 你的游戏需要防沉迷或家长控制功能 → 用 **PlayTimeLimit** 模块
- 你需要断线后重新加入正在进行的游戏 → 用 **Rejoin** 模块

## 蓝图用法

> 注：Lobby 模块的核心交互主要通过 C++ 网络函数（`UFUNCTION(Server/Client, Reliable)`）进行，不直接暴露为蓝图节点。以下列出可供蓝图监听的关键委托。

### 核心委托

| 委托 | 说明 | 所在类 |
|---|---|---|
| `OnLobbyConnectionEstablished` | 客户端与大厅 Beacon 连接建立时触发 | `ALobbyBeaconClient` |
| `OnLoginComplete` | 登录握手完成时触发 | `ALobbyBeaconClient` |
| `OnPlayerJoined` | 新玩家加入大厅时触发 | `ALobbyBeaconClient` |
| `OnPlayerLeft` | 玩家离开大厅时触发 | `ALobbyBeaconClient` |
| `OnJoiningGame` | 服务器通知客户端加入游戏时触发 | `ALobbyBeaconClient` |
| `OnPlayerLobbyStateAdded` | 玩家状态被添加到大厅列表时触发 | `ALobbyBeaconState` |
| `OnPlayerLobbyStateRemoved` | 玩家状态从大厅列表移除时触发 | `ALobbyBeaconState` |
| `OnLobbyStarted` | 大厅正式启动时触发 | `ALobbyBeaconState` |
| `OnLobbyWaitingForPlayersUpdate` | 等待玩家倒计时更新时触发 | `ALobbyBeaconState` |
| `OnUniqueIdReplicated` | 玩家唯一 ID 复制完成时触发 | `ALobbyBeaconPlayerState` |
| `OnPlayerStateChanged` | 玩家状态发生变更时触发 | `ALobbyBeaconPlayerState` |
| `OnPartyOwnerChanged` | 派对队长变更时触发 | `ALobbyBeaconPlayerState` |

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConnectToLobby` | 连接到指定大厅主机 | `ALobbyBeaconClient` |
| `DisconnectFromLobby` | 优雅断开与大厅的连接 | `ALobbyBeaconClient` |
| `JoiningServer` | 通知服务器客户端即将加入游戏 | `ALobbyBeaconClient` |
| `KickPlayer` | 请求踢出指定玩家 | `ALobbyBeaconClient` |
| `SetPartyOwnerId` | 设置派对队长 | `ALobbyBeaconClient` |
| `ClientJoinGame` | 服务器通知客户端加入游戏（Client RPC） | `ALobbyBeaconClient` |
| `AddPlayer` | 向大厅添加玩家 | `ALobbyBeaconState` |
| `RemovePlayer` | 从大厅移除玩家 | `ALobbyBeaconState` |
| `GetPlayer` | 获取大厅中的玩家状态 | `ALobbyBeaconState` |
| `UpdatePartyLeader` | 更新玩家的派对队长 | `ALobbyBeaconState` |
| `StartLobby` | 启动大厅 | `ALobbyBeaconState` |
| `SetupLobbyState` | 创建大厅状态并设置最大玩家数 | `ALobbyBeaconHost` |
| `Init` | 初始化大厅 Beacon 主机 | `ALobbyBeaconHost` |
| `KickPlayer` | 踢出指定客户端 | `ALobbyBeaconHost` |
| `HandlePlayerLogout` | 处理玩家断线 | `ALobbyBeaconHost` |
| `AdvertiseSessionJoinability` | 广播会话可加入状态给所有客户端 | `ALobbyBeaconHost` |

### 使用示例（蓝图描述）

**服务端 — 创建大厅**：
1. 创建 `ALobbyBeaconHost` 子类实例
2. 调用 `Init(SessionName)` 关联到当前会话
3. 调用 `SetupLobbyState(MaxPlayers)` 设置最大玩家数
4. 当玩家匹配成功时，通过 `AdvertiseSessionJoinability(Settings)` 更新可加入状态
5. 绑定 `OnLobbyStarted` 委托，在所有玩家就绪后触发游戏开始逻辑

**客户端 — 加入大厅**：
1. 通过会话搜索获取目标主机信息
2. 创建 `ALobbyBeaconClient` 子类实例
3. 调用 `ConnectToLobby(DesiredHost)` 连接到大厅
4. 绑定 `OnLobbyConnectionEstablished` 确认连接成功
5. 绑定 `OnJoiningGame` 等待服务器通知加入游戏
6. 收到通知后执行关卡切换

## C++ 用法

### 头文件引入

```cpp
#include "LobbyBeaconHost.h"
#include "LobbyBeaconClient.h"
#include "LobbyBeaconState.h"
#include "LobbyBeaconPlayerState.h"
```

### 基本用法 — 服务端创建大厅

基于 `ALobbyBeaconHost` 的 API 分析：

```cpp
// MyLobbyHost.h
#pragma once

#include "LobbyBeaconHost.h"
#include "MyLobbyHost.generated.h"

UCLASS()
class AMyLobbyHost : public ALobbyBeaconHost
{
    GENERATED_BODY()

public:
    void StartLobbyForSession(FName InSessionName, int32 InMaxPlayers)
    {
        // 初始化大厅 Beacon，关联到指定会话
        if (Init(InSessionName))
        {
            // 创建大厅状态并设置最大玩家数
            SetupLobbyState(InMaxPlayers);
        }
    }

    // 重写踢人逻辑，添加自定义校验
    virtual bool ProcessKickPlayer(ALobbyBeaconClient* Instigator,
        const FUniqueNetIdRepl& PlayerToKick,
        const FText& Reason) override
    {
        // 仅房主可踢人
        // 自定义权限校验逻辑...
        return Super::ProcessKickPlayer(Instigator, PlayerToKick, Reason);
    }
};
```

### 基本用法 — 客户端连接大厅

基于 `ALobbyBeaconClient` 的 API 分析：

```cpp
// MyLobbyClient.h
#pragma once

#include "LobbyBeaconClient.h"
#include "MyLobbyClient.generated.h"

UCLASS()
class AMyLobbyClient : public ALobbyBeaconClient
{
    GENERATED_BODY()

public:
    void JoinLobby(const FOnlineSessionSearchResult& DesiredHost)
    {
        // 绑定连接建立回调
        OnLobbyConnectionEstablished().AddUObject(
            this, &AMyLobbyClient::HandleLobbyConnected);

        // 绑定加入游戏回调
        OnJoiningGame().AddUObject(
            this, &AMyLobbyClient::HandleJoiningGame);

        // 绑定玩家加入/离开回调
        OnPlayerJoined().AddUObject(
            this, &AMyLobbyClient::HandlePlayerJoined);
        OnPlayerLeft().AddUObject(
            this, &AMyLobbyClient::HandlePlayerLeft);

        // 发起连接
        ConnectToLobby(DesiredHost);
    }

private:
    void HandleLobbyConnected()
    {
        UE_LOG(LogLobby, Log, TEXT("Successfully connected to lobby"));
    }

    void HandleJoiningGame()
    {
        // 服务器通知客户端加入游戏，执行关卡切换
        UE_LOG(LogLobby, Log, TEXT("Server instructed to join game"));
    }

    void HandlePlayerJoined(const FUniqueNetIdRepl& UniqueId,
                            const FText& PlayerName)
    {
        UE_LOG(LogLobby, Log, TEXT("Player joined: %s"), *PlayerName.ToString());
    }

    void HandlePlayerLeft(const FUniqueNetIdRepl& UniqueId)
    {
        UE_LOG(LogLobby, Log, TEXT("Player left lobby"));
    }
};
```

### 进阶用法 — 自定义大厅玩家状态

基于 `ALobbyBeaconPlayerState` 和 `ALobbyBeaconState` 的 API 分析：

```cpp
// MyLobbyBeaconState.h
#pragma once

#include "LobbyBeaconState.h"
#include "MyLobbyBeaconState.generated.h"

UCLASS()
class AMyLobbyBeaconState : public ALobbyBeaconState
{
    GENERATED_BODY()

public:
    // 自定义是否需要满员才能开始
    virtual bool RequireFullLobbyToStart() const override
    {
        return true; // 必须满员才允许开始
    }

    // 自定义玩家创建逻辑
    virtual ALobbyBeaconPlayerState* CreateNewPlayer(
        const FText& PlayerName,
        const FUniqueNetIdRepl& UniqueId) override
    {
        auto* PlayerState = Super::CreateNewPlayer(PlayerName, UniqueId);
        if (PlayerState)
        {
            // 自定义初始化逻辑
            PlayerState->OnPlayerStateChanged().AddUObject(
                this, &AMyLobbyBeaconState::HandlePlayerStateChanged);
        }
        return PlayerState;
    }

    // 等待阶段的自定义逻辑
    virtual void OnPreLobbyStartedTickInternal(double DeltaTime) override
    {
        Super::OnPreLobbyStartedTickInternal(DeltaTime);
        // 在等待阶段执行自定义逻辑，如检查玩家准备状态
    }

private:
    void HandlePlayerStateChanged(const FUniqueNetIdRepl& UniqueId)
    {
        // 处理玩家状态变更
    }
};
```

### 进阶用法 — 派对管理与会话广播

```cpp
// 在大厅主机中管理派对队长
void AMyLobbyHost::OnNewPlayerJoined(ALobbyBeaconClient* Client)
{
    // 获取玩家状态
    auto* PlayerState = LobbyState->GetPlayer(Client);
    if (PlayerState)
    {
        // 监听派对队长变更
        PlayerState->OnPartyOwnerChanged().AddUObject(
            this, &AMyLobbyHost::HandlePartyOwnerChanged);

        // 监听玩家是否仍在大厅
        PlayerState->OnPlayerStateChanged().AddUObject(
            this, &AMyLobbyHost::HandlePlayerStateChanged);
    }
}

// 广播当前会话可加入性设置
void AMyLobbyHost::UpdateSessionJoinability(bool bAllowJoin)
{
    FJoinabilitySettings Settings;
    // 配置 Settings...
    AdvertiseSessionJoinability(Settings);
}

// 服务端踢人
void AMyLobbyHost::RequestKickPlayer(ALobbyBeaconClient* Target,
                                      const FText& Reason)
{
    KickPlayer(Target, Reason);
}
```

## Demo 示例

### 服务端 Lobby Host

```cpp
// MyLobbyGameMode.h
#pragma once

#include "GameFramework/GameModeBase.h"
#include "LobbyBeaconHost.h"
#include "MyLobbyGameMode.generated.h"

UCLASS()
class AMyLobbyGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    virtual void InitGame(const FString& MapName,
                          const FString& Options,
                          FString& ErrorMessage) override;

    UFUNCTION(BlueprintCallable)
    void StartLobby(int32 MaxPlayers);

    UFUNCTION(BlueprintCallable)
    void KickFromLobby(const FUniqueNetIdRepl& PlayerId, const FText& Reason);

private:
    UPROPERTY()
    TObjectPtr<ALobbyBeaconHost> LobbyHost;

    void HandleLobbyStarted();
};
```

```cpp
// MyLobbyGameMode.cpp
#include "MyLobbyGameMode.h"
#include "LobbyBeaconHost.h"
#include "LobbyBeaconState.h"

void AMyLobbyGameMode::InitGame(const FString& MapName,
                                 const FString& Options,
                                 FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);
}

void AMyLobbyGameMode::StartLobby(int32 MaxPlayers)
{
    // 创建大厅 Beacon Host
    LobbyHost = GetWorld()->SpawnActor<ALobbyBeaconHost>(ALobbyBeaconHost::StaticClass());
    if (LobbyHost)
    {
        FName SessionName = NAME_GameSession;
        if (LobbyHost->Init(SessionName))
        {
            LobbyHost->SetupLobbyState(MaxPlayers);
            UE_LOG(LogLobby, Log, TEXT("Lobby started with max %d players"), MaxPlayers);
        }
    }
}

void AMyLobbyGameMode::KickFromLobby(const FUniqueNetIdRepl& PlayerId,
                                      const FText& Reason)
{
    if (LobbyHost && LobbyHost->LobbyState)
    {
        auto* PlayerState = LobbyHost->LobbyState->GetPlayer(PlayerId);
        if (PlayerState && PlayerState->ClientActor)
        {
            LobbyHost->KickPlayer(
                Cast<ALobbyBeaconClient>(PlayerState->ClientActor), Reason);
        }
    }
}

void AMyLobbyGameMode::HandleLobbyStarted()
{
    UE_LOG(LogLobby, Log, TEXT("All players ready, starting game"));
    // 执行开始游戏逻辑...
}
```

### 客户端 Lobby 连接器

```cpp
// MyLobbyConnector.h
#pragma once

#include "OnlineBeaconClient.h"
#include "LobbyBeaconClient.h"
#include "MyLobbyConnector.generated.h"

UCLASS()
class AMyLobbyConnector : public ALobbyBeaconClient
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable)
    void ConnectToGameLobby(const FOnlineSessionSearchResult& TargetHost);

    DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnLobbyReady);
    DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnLobbyError, const FText&, ErrorMsg);

    UPROPERTY(BlueprintAssignable)
    FOnLobbyReady OnLobbyReady;

    UPROPERTY(BlueprintAssignable)
    FOnLobbyError OnLobbyError;

private:
    void HandleConnectionEstablished();
    void HandleKick(const FText& KickReason);
};
```

```cpp
// MyLobbyConnector.cpp
#include "MyLobbyConnector.h"

void AMyLobbyConnector::ConnectToGameLobby(
    const FOnlineSessionSearchResult& TargetHost)
{
    OnLobbyConnectionEstablished().AddUObject(
        this, &AMyLobbyConnector::HandleConnectionEstablished);

    ConnectToLobby(TargetHost);
}

void AMyLobbyConnector::HandleConnectionEstablished()
{
    UE_LOG(LogLobby, Log, TEXT("Connected to lobby, waiting for game start"));
    OnLobbyReady.Broadcast();
}

void AMyLobbyConnector::HandleKick(const FText& KickReason)
{
    UE_LOG(LogLobby, Warning, TEXT("Kicked from lobby: %s"),
           *KickReason.ToString());
    OnLobbyError.Broadcast(KickReason);
}
```

## 模块依赖

从 Build.cs 分析，Lobby 模块的依赖如下：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemGDK` | Party 模块依赖的 GDK 平台在线子系统 |
| `OnlineSubsystemUtils` | 在线子系统工具库，提供会话管理、Beacon 等基础设施 |

> 注：各子模块之间也可能存在内部依赖（如 Lobby 依赖 Party 进行派对管理）。实际使用时需参考对应模块的 Build.cs 文件。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `09a2dfc6` | [Hotfix on Load] Fix issue where certain baked hotfixes will not apply when no backend hotfixes exist | 修复内置热修复在无后端热修复时不生效的问题 |
| 2026-05-12 | `0b9170a8` | Guard Invite and RTJ social party calls when epic parties mirroring is enabled | Epic 派对镜像启用时保护邀请和加入派对的调用 |
| 2026-04-30 | `fe1eaff2` | Add a hook for PartyPlatformSessionMonitor to allow the game party to add a special key to the platform session | 为派对平台会话监视器添加钩子以支持自定义会话键 |
| 2026-04-29 | `0badc43f` | Restore LogHotfixManager summary logs for hotfix on load | 恢复热修复加载时的日志摘要输出 |
| 2026-04-28 | `85cae1c6` | Broadcast party initialization after we've processed our first update | 在处理首次更新后再广播派对初始化事件 |

### 维护评价

**🟢 活跃维护中**

OnlineFramework 插件自 2016 年创建以来一直保持活跃维护。从近期提交记录看，2026 年 4-5 月仍有功能性更新（Hotfix 修复、Party 派对系统增强、日志改进），说明 Epic 内部团队仍在持续使用和维护此框架。

**优势**：
- 核心框架代码成熟稳定，经过 9 年迭代
- 持续收到 bug 修复和功能增强
- 作为 Fortnite 等大型在线游戏的基础设施，维护优先级高

**注意事项**：
- 默认不启用（`EnabledByDefault: false`），需手动在项目设置中开启
- Party 模块依赖 `OnlineSubsystemGDK`，可能与特定平台绑定
- 模块较多，按需引入，不要全量启用
- 部分 API 通过网络复制函数（Server/Client RPC）实现，需理解 UE 网络架构

**推荐使用**：✅ 如果你的项目需要一个经过大规模生产验证的在线框架层（大厅、派对、热修复等），这是一个可靠的选择。但由于模块间耦合和平台依赖，建议仅引入所需模块。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineFramework/Tests)（如存在）