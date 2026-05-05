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
| 年龄标签 | 🏛️ 文物（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework) | |

## 用途

OnlineFramework 是 Epic 为在线游戏服务提供的**底层框架插件**，封装了与在线平台交互的通用功能模块。它不是一个完整的在线子系统实现，而是提供可复用的基础设施，供具体的在线平台插件（如 EOS、Steam 等）组合使用。

该插件解决的核心问题：
- **大厅（Lobby）管理**：玩家在正式加入游戏服务器前的等待/匹配区域，基于 Online Beacon 实现轻量级连接
- **组队（Party）系统**：跨游戏的玩家组队功能
- **QoS 测量**：网络质量检测，用于选择最佳服务器
- **登录流程（LoginFlow）**：标准化的登录认证流程
- **热修复（Hotfix）**：运行时配置热更新
- **补丁检查（PatchCheck）**：客户端版本/补丁校验
- **游戏时长限制（PlayTimeLimit）**：防沉迷/家长控制
- **重连（Rejoin）**：断线重连支持

**重要**：此插件默认禁用（`EnabledByDefault: false`），需要手动在项目设置中启用。

## 使用场景

- 你需要在玩家匹配成功后、正式进入游戏前展示一个等待大厅 → 用 **Lobby** 模块
- 你需要实现跨会话的玩家组队功能 → 用 **Party** 模块
- 你需要在多个服务器之间选择延迟最低的 → 用 **Qos** 模块
- 你需要实现断线后重新加入游戏 → 用 **Rejoin** 模块
- 你需要在不重启服务器的情况下更新游戏配置 → 用 **Hotfix** 模块
- 你需要检查客户端是否需要更新补丁 → 用 **PatchCheck** 模块

## 模块总览

| 模块 | 用途 |
|---|---|
| **Lobby** | 基于 Online Beacon 的大厅系统，管理玩家在加入游戏前的等待状态 |
| **Party** | 跨会话的玩家组队系统 |
| **Qos** | Quality of Service 网络质量测量 |
| **LoginFlow** | 标准化登录认证流程 |
| **Hotfix** | 运行时配置热更新 |
| **PatchCheck** | 客户端补丁/版本检查 |
| **PlayTimeLimit** | 游戏时长限制（防沉迷） |
| **Rejoin** | 断线重连支持 |

---

## Lobby 模块详解

Lobby 是本插件中最核心的模块，基于 Unreal 的 Online Beacon 系统实现大厅功能。

### 架构概览

```
┌─────────────────────────────────────────────────┐
│                   Server Side                    │
│                                                  │
│  ALobbyBeaconHost ──► ALobbyBeaconState          │
│       │                     │                    │
│       │              ALobbyBeaconPlayerState[]   │
│       │                                          │
└───────┼──────────────────────────────────────────┘
        │  Online Beacon Connection
┌───────┼──────────────────────────────────────────┐
│       ▼           Client Side                    │
│  ALobbyBeaconClient ──► ALobbyBeaconState (Rep)  │
│       │                     │                    │
│       │              ALobbyBeaconPlayerState (Rep)│
│                                                  │
└─────────────────────────────────────────────────┘
```

### 核心类

| 类 | 说明 |
|---|---|
| `ALobbyBeaconHost` | 服务端大厅宿主对象，管理大厅生命周期和玩家连接 |
| `ALobbyBeaconClient` | 客户端大厅信标，处理与大厅服务器的通信 |
| `ALobbyBeaconState` | 大厅状态（类似 AGameState），通过 FastArraySerializer 同步玩家列表 |
| `ALobbyBeaconPlayerState` | 玩家在大厅中的轻量级状态表示 |
| `FLobbyModule` | Lobby 模块接口 |

### 蓝图用法

Lobby 模块的类主要通过 C++ 使用，蓝图可访问的 API 较少。以下是关键的可调用接口：

#### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ClientJoinGame` | 服务端通知客户端加入游戏（Client RPC） | `ALobbyBeaconClient` |
| `ConnectToLobby` | 连接到大厅宿主 | `ALobbyBeaconClient` |
| `DisconnectFromLobby` | 优雅断开大厅连接 | `ALobbyBeaconClient` |
| `KickPlayer` | 将玩家踢出大厅 | `ALobbyBeaconHost` |
| `UpdatePartyLeader` | 更新队伍领袖 | `ALobbyBeaconHost` |

#### 关键委托

| 委托 | 参数 | 说明 |
|---|---|---|
| `FOnLobbyConnectionEstablished` | 无 | 大厅连接建立（尚未登录） |
| `FOnLobbyPlayerJoined` | `FText DisplayName`, `FUniqueNetIdRepl UniqueId` | 玩家加入大厅 |
| `FOnLobbyPlayerLeft` | `FUniqueNetIdRepl UniqueId` | 玩家离开大厅 |
| `FOnLobbyLoginComplete` | `bool bWasSuccessful` | 登录握手完成 |
| `FOnJoiningGame` | 无 | 玩家正在从大厅加入游戏 |
| `FOnLobbyStarted` | 无 | 大厅开放接受玩家 |
| `FOnPlayerLobbyStateChanged` | `ALobbyBeaconPlayerState*` | 大厅中玩家状态变化 |

#### 连接状态枚举

```cpp
enum class ELobbyBeaconJoinState : uint8
{
    None,                    // 未连接或无加入意图
    SentJoinRequest,         // 已发送加入请求，等待响应
    JoinRequestAcknowledged  // 加入请求已被确认
};
```

### C++ 用法

#### 头文件引入

```cpp
#include "LobbyBeaconHost.h"
#include "LobbyBeaconClient.h"
#include "LobbyBeaconState.h"
#include "LobbyBeaconPlayerState.h"
```

#### 基本用法：创建大厅宿主

```cpp
// 来源: LobbyBeaconHost.h
// 在服务端创建大厅宿主并初始化

// 1. 生成大厅宿主
ALobbyBeaconHost* LobbyHost = GetWorld()->SpawnActor<ALobbyBeaconHost>(ALobbyBeaconHost::StaticClass());

// 2. 初始化，关联到指定会话
LobbyHost->Init(FName("GameSession"));

// 3. 设置大厅状态，指定最大玩家数
LobbyHost->SetupLobbyState(16);
```

#### 基本用法：客户端连接大厅

```cpp
// 来源: LobbyBeaconClient.h
// 客户端连接到大厅

// 1. 生成客户端信标
ALobbyBeaconClient* LobbyClient = GetWorld()->SpawnActor<ALobbyBeaconClient>(ALobbyBeaconClient::StaticClass());

// 2. 绑定回调
LobbyClient->OnLobbyConnectionEstablished().BindLambda([]()
{
    UE_LOG(LogLobby, Log, TEXT("Connected to lobby"));
});

LobbyClient->OnLobbyPlayerJoined().BindLambda([](const FText& DisplayName, const FUniqueNetIdRepl& UniqueId)
{
    UE_LOG(LogLobby, Log, TEXT("Player joined: %s"), *DisplayName.ToString());
});

LobbyClient->OnLobbyLoginComplete().BindLambda([](bool bWasSuccessful)
{
    if (bWasSuccessful)
    {
        UE_LOG(LogLobby, Log, TEXT("Lobby login complete"));
    }
});

// 3. 连接到大厅（传入搜索到的会话结果）
LobbyClient->ConnectToLobby(DesiredSessionResult);
```

#### 进阶用法：完整大厅流程

```cpp
// 来源: 综合 LobbyBeaconHost.h, LobbyBeaconClient.h, LobbyBeaconState.h
// 完整的大厅创建和管理流程

// ===== 服务端 =====

// 创建并初始化大厅宿主
ALobbyBeaconHost* Host = World->SpawnActor<ALobbyBeaconHost>();
Host->Init(SessionName);
Host->SetupLobbyState(MaxPlayers);

// 当玩家断开连接时的处理
Host->NotifyClientDisconnected(LeavingClient);

// 踢出玩家
Host->KickPlayer(ClientActor, FText::FromString(TEXT("违规行为")));

// 更新队伍领袖
Host->UpdatePartyLeader(PartyMemberId, NewLeaderId);

// 广播可加入性设置变更
Host->AdvertiseSessionJoinability(JoinabilitySettings);

// 验证会话是否匹配
if (Host->DoesSessionMatch(IncomingSessionId))
{
    // 允许连接
}

// 调试：输出当前大厅状态
Host->DumpState();

// ===== 客户端 =====

ALobbyBeaconClient* Client = World->SpawnActor<ALobbyBeaconClient>();

// 监听玩家加入/离开
Client->OnLobbyPlayerJoined().BindLambda([](const FText& Name, const FUniqueNetIdRepl& Id)
{
    // 更新 UI 显示玩家列表
});

Client->OnLobbyPlayerLeft().BindLambda([](const FUniqueNetIdRepl& Id)
{
    // 从 UI 移除玩家
});

// 连接大厅
Client->ConnectToLobby(SearchResult);

// 准备加入游戏
Client->JoiningServer();

// 收到服务端的加入游戏指令后
// ClientJoinGame() 会被服务端调用

// 离开大厅
Client->DisconnectFromLobby();
```

#### 玩家状态监听

```cpp
// 来源: LobbyBeaconPlayerState.h
// 监听大厅中玩家状态的变化

ALobbyBeaconPlayerState* PlayerState = /* 获取玩家状态 */;

// 监听 UniqueId 同步完成
PlayerState->OnUniqueIdReplicated().AddLambda([](const FUniqueNetIdRepl& UniqueId)
{
    UE_LOG(LogLobby, Log, TEXT("Player UniqueId replicated: %s"), *UniqueId.ToString());
});

// 监听玩家状态变化
PlayerState->OnPlayerStateChanged().AddLambda([](const FUniqueNetIdRepl& UniqueId)
{
    // 玩家状态发生变化，更新 UI
});

// 监听队伍领袖变化
PlayerState->OnPartyOwnerChanged().AddLambda([](const FUniqueNetIdRepl& UniqueId)
{
    // 队伍领袖变更
});

// 检查玩家是否在大厅中
if (PlayerState->bInLobby)
{
    // 玩家在大厅等待中
}
```

### Demo 示例

```cpp
// MyLobbyManager.h
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "LobbyBeaconHost.h"
#include "LobbyBeaconClient.h"
#include "MyLobbyManager.generated.h"

UCLASS()
class UMyLobbyManager : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    /** 服务端：创建大厅 */
    UFUNCTION(BlueprintCallable, Category = "Lobby")
    void CreateLobby(UWorld* World, FName SessionName, int32 MaxPlayers);

    /** 客户端：加入大厅 */
    UFUNCTION(BlueprintCallable, Category = "Lobby")
    void JoinLobby(UWorld* World, const FOnlineSessionSearchResult& SearchResult);

    /** 客户端：离开大厅 */
    UFUNCTION(BlueprintCallable, Category = "Lobby")
    void LeaveLobby();

    /** 服务端：踢出玩家 */
    UFUNCTION(BlueprintCallable, Category = "Lobby")
    void KickPlayerFromLobby(ALobbyBeaconClient* Client, const FText& Reason);

private:
    UPROPERTY()
    TObjectPtr<ALobbyBeaconHost> LobbyHost;

    UPROPERTY()
    TObjectPtr<ALobbyBeaconClient> LobbyClient;
};
```

```cpp
// MyLobbyManager.cpp
#include "MyLobbyManager.h"
#include "LobbyBeaconState.h"
#include "LobbyBeaconPlayerState.h"

void UMyLobbyManager::CreateLobby(UWorld* World, FName SessionName, int32 MaxPlayers)
{
    if (!World) return;

    FActorSpawnParameters SpawnParams;
    LobbyHost = World->SpawnActor<ALobbyBeaconHost>(ALobbyBeaconHost::StaticClass(), SpawnParams);
    
    if (LobbyHost)
    {
        LobbyHost->Init(SessionName);
        LobbyHost->SetupLobbyState(MaxPlayers);
        UE_LOG(LogLobby, Log, TEXT("Lobby created for session %s, max players: %d"), 
            *SessionName.ToString(), MaxPlayers);
    }
}

void UMyLobbyManager::JoinLobby(UWorld* World, const FOnlineSessionSearchResult& SearchResult)
{
    if (!World) return;

    FActorSpawnParameters SpawnParams;
    LobbyClient = World->SpawnActor<ALobbyBeaconClient>(ALobbyBeaconClient::StaticClass(), SpawnParams);

    if (LobbyClient)
    {
        // 绑定事件
        LobbyClient->OnLobbyConnectionEstablished().BindLambda([this]()
        {
            UE_LOG(LogLobby, Log, TEXT("Connected to lobby server"));
        });

        LobbyClient->OnLobbyPlayerJoined().BindLambda(
            [](const FText& DisplayName, const FUniqueNetIdRepl& UniqueId)
        {
            UE_LOG(LogLobby, Log, TEXT("Player joined lobby: %s"), *DisplayName.ToString());
        });

        LobbyClient->OnLobbyLoginComplete().BindLambda([this](bool bSuccess)
        {
            if (bSuccess)
            {
                UE_LOG(LogLobby, Log, TEXT("Successfully logged into lobby"));
            }
        });

        LobbyClient->ConnectToLobby(SearchResult);
    }
}

void UMyLobbyManager::LeaveLobby()
{
    if (LobbyClient)
    {
        LobbyClient->DisconnectFromLobby();
        LobbyClient = nullptr;
    }
}

void UMyLobbyManager::KickPlayerFromLobby(ALobbyBeaconClient* Client, const FText& Reason)
{
    if (LobbyHost && Client)
    {
        LobbyHost->KickPlayer(Client, Reason);
    }
}
```

## 模块依赖

从各模块的 Build.cs 分析，OnlineFramework 的模块依赖如下：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统基础接口 |
| `OnlineSubsystemUtils` | 在线子系统工具函数 |
| `Beacon` / `OnlineBeacon` | Online Beacon 通信框架（Lobby 模块依赖） |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

```
- afdf8d7528de Replace some usages of FORCEINLINE with inline in Online modules.
- 93a13080d9ef Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar instead of on types.
- 26e632ffddcb PR #12306: Fix Crash in Lobby Beacon Host for Logging
```

- 第一条：代码规范调整，将 `FORCEINLINE` 替换为 `inline`，属于编译器兼容性修复
- 第二条：DLL 导出符号规范化，与 Lyra 示例项目构建目标对齐
- 第三条：修复 Lobby Beacon Host 中的日志崩溃问题，属于 bug 修复

### 维护评价

OnlineFramework 自 2016 年创建以来已有约 9 年历史，是 Unreal 在线功能的基础设施层。从近期 commit 来看，更新主要是编译兼容性和 bug 修复，而非功能性迭代。这说明该插件已进入**成熟稳定期**，核心功能已经完善。

**注意事项**：
- 该插件**默认禁用**，需要在项目设置中手动启用
- 作为 Runtime 模块集合，它提供的是底层框架而非完整解决方案
- Lobby 模块依赖 Online Beacon 系统，需要理解 Beacon 的工作原理
- 适合需要自定义在线服务流程的项目，如果只需要简单的会话管理，直接使用 OnlineSubsystem 即可

**推荐**：如果你的项目需要大厅等待、组队、QoS 测量等高级在线功能，推荐使用此插件作为基础。但需注意它默认禁用，且需要配合具体的 OnlineSubsystem 实现使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [Lobby 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Source/Lobby)