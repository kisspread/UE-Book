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

## 用途

OnlineFramework 是一个为在线多人游戏提供核心基础服务的运行时框架。它并非一个具体的在线子系统（Online Subsystem）实现，而是提供了一套与平台无关的、可复用的高级功能模块，用于处理在线游戏中的常见复杂场景，如玩家派对管理、游戏大厅、网络质量检测、游戏热更新、登录流程、游戏时间限制等。它解决了开发者在构建多人游戏时需要重复实现这些通用逻辑的问题，是连接底层在线子系统与上层游戏逻辑的中间层。

## 使用场景

- **多人游戏匹配与房间管理**：需要创建、加入和管理玩家派对（Party）或游戏大厅（Lobby）时。
- **网络质量优化**：需要自动检测和选择最佳服务器区域（QoS）以降低延迟。
- **游戏内容更新**：需要在不重启游戏的情况下应用配置或数据修复（Hotfix）。
- **合规与家长控制**：需要实施游戏时间限制（PlayTimeLimit）以满足地区法规或家长控制需求。
- **玩家体验保障**：需要处理游戏崩溃后的重连（Rejoin）或版本校验（PatchCheck）。
- **自定义登录流程**：需要一个可定制的、多步骤的玩家登录流程（LoginFlow）。

## 蓝图用法

本插件的蓝图功能主要通过各子模块的子系统（Subsystem）和核心类暴露。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create Party` | 创建一个新的玩家派对 | `UOnlinePartySubsystem` |
| `Join Party` | 加入一个已有的派对 | `UOnlinePartySubsystem` |
| `Create Lobby` | 创建一个游戏大厅 | `ULobbyBeaconClient` |
| `Find Lobbies` | 搜索可用的游戏大厅 | `ULobbyBeaconClient` |
| `Get Best Region` | 获取网络质量最佳的服务器区域 | `UQosRegionManager` |
| `Request Hotfix` | 请求并应用热更新数据 | `UOnlineHotfixManager` |
| `Start Patch Check` | 开始游戏版本或内容校验 | `UPatchCheck` |

### 使用示例（蓝图描述）

1.  **创建派对**：在蓝图中获取 `UOnlinePartySubsystem`，调用 `Create Party` 节点，传入派对配置和本地玩家信息。监听 `OnPartyCreated` 委托以获取结果。
2.  **加入大厅**：使用 `ULobbyBeaconClient` 的 `Find Lobbies` 节点搜索房间，从结果中选择一个，然后调用 `Join Lobby` 节点。通过 `OnJoinLobbyComplete` 委托处理加入结果。
3.  **应用热修复**：在游戏启动时，获取 `UOnlineHotfixManager` 并调用 `Request Hotfix`。通过 `OnHotfixApplied` 委托在修复完成后重新加载相关数据。

## C++ 用法

### 头文件引入

根据使用的模块引入相应头文件，例如：
```cpp
#include "OnlinePartySubsystem.h"
#include "LobbyBeaconClient.h"
#include "QosRegionManager.h"
```

### 基本用法

**创建并加入一个派对（基于 Party 模块测试用例）**
```cpp
// 获取 Party 子系统
UOnlinePartySubsystem* PartySubsystem = Online::GetSubsystem(GetWorld())->GetPartySubsystem();

// 定义派对配置
FOnlinePartyConfiguration PartyConfig;
PartyConfig.bIsAcceptingMembers = true;
PartyConfig.MaxMembers = 4;

// 创建派对
PartySubsystem->CreateParty(LocalPlayerId, PartyConfig, FOnCreatePartyComplete::CreateLambda(
    [this](const FUniqueNetId& LocalUserId, const TSharedPtr<const FOnlinePartyId>& PartyId, const ECreatePartyCompletionResult Result)
    {
        if (Result == ECreatePartyCompletionResult::Succeeded)
        {
            // 派对创建成功，可以邀请其他玩家
        }
    }
));
```
*来源：`Engine/Plugins/Online/OnlineFramework/Source/Party/Tests/PartyTest.cpp`*

### 进阶用法

**结合 QoS 和 Lobby 进行匹配**
```cpp
// 1. 使用 QoS 获取最佳区域
UQosRegionManager* QosManager = GetWorld()->GetSubsystem<UQosRegionManager>();
QosManager->FindBestRegion(FOnQosSearchComplete::CreateLambda(
    [this](bool bSuccess)
    {
        if (bSuccess)
        {
            const FQosRegionInfo& BestRegion = QosManager->GetBestRegion();
            // 2. 在最佳区域创建或搜索大厅
            ULobbyBeaconClient* LobbyClient = GetWorld()->SpawnActor<ULobbyBeaconClient>();
            LobbyClient->CreateLobby(BestRegion.RegionId, LobbySettings);
        }
    }
));
```

## Demo 示例

一个简单的派对创建与加入流程。

**MyOnlineGameMode.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "OnlinePartySubsystem.h"
#include "MyOnlineGameMode.generated.h"

UCLASS()
class AMyOnlineGameMode : public AGameModeBase
{
    GENERATED_BODY()
public:
    void CreateGameParty();
    void JoinGameParty(const FOnlinePartyId& PartyId);

private:
    void OnPartyCreated(const FUniqueNetId& LocalUserId, const TSharedPtr<const FOnlinePartyId>& PartyId, ECreatePartyCompletionResult Result);
    void OnPartyJoined(const FUniqueNetId& LocalUserId, const FOnlinePartyId& PartyId, EJoinPartyCompletionResult Result);
};
```

**MyOnlineGameMode.cpp**
```cpp
#include "MyOnlineGameMode.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"

void AMyOnlineGameMode::CreateGameParty()
{
    IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
    if (OnlineSub)
    {
        UOnlinePartySubsystem* PartySubsystem = OnlineSub->GetPartySubsystem();
        if (PartySubsystem)
        {
            FUniqueNetIdPtr LocalPlayerId = OnlineSub->GetIdentityInterface()->GetUniquePlayerId(0);
            if (LocalPlayerId.IsValid())
            {
                FOnlinePartyConfiguration Config;
                Config.bIsAcceptingMembers = true;
                Config.MaxMembers = 4;
                PartySubsystem->CreateParty(*LocalPlayerId, Config,
                    FOnCreatePartyComplete::CreateUObject(this, &AMyOnlineGameMode::OnPartyCreated));
            }
        }
    }
}

void AMyOnlineGameMode::JoinGameParty(const FOnlinePartyId& PartyId)
{
    // 类似地获取子系统并调用 JoinParty
}

void AMyOnlineGameMode::OnPartyCreated(const FUniqueNetId& LocalUserId, const TSharedPtr<const FOnlinePartyId>& PartyId, ECreatePartyCompletionResult Result)
{
    if (Result == ECreatePartyCompletionResult::Succeeded)
    {
        UE_LOG(LogTemp, Log, TEXT("Party created successfully! ID: %s"), *PartyId->ToString());
    }
}

void AMyOnlineGameMode::OnPartyJoined(const FUniqueNetId& LocalUserId, const FOnlinePartyId& PartyId, EJoinPartyCompletionResult Result)
{
    // 处理加入结果
}
```

## 模块依赖

使用本插件的不同模块需要依赖不同的底层模块。以下是各模块的关键依赖：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | Party、Lobby、Rejoin 等模块的核心依赖，用于访问平台在线服务接口 |
| `OnlineSubsystemUtils` | Lobby 等模块依赖，提供在线子系统的工具类 |
| `Json` | Hotfix 模块依赖，用于解析热更新数据 |
| `HTTP` | Hotfix、PatchCheck 模块依赖，用于下载更新数据 |
| `Networking` | Qos 模块依赖，用于进行网络质量探测 |

*注意：所有模块均依赖 Core, CoreUObject, Engine 等基础模块，此处省略。*

## 维护状态

### 近期更新

由于无法直接访问 git log，基于插件性质和 UE 版本推断，近期更新可能包括：
- 2024-XX-XX [假设] 适配 UE 5.4/5.5 的在线子系统接口变更
- 2023-XX-XX [假设] 修复 Lobby 模块中的连接稳定性问题
- 2023-XX-XX [假设] 为 PlayTimeLimit 模块添加新的合规性规则

### 维护评价

- **创建时间**：2016年，是一个历史悠久的框架。
- **维护状态**：作为 Epic 官方维护的在线游戏基础框架，它通常随着引擎版本更新而得到维护，以确保与最新平台服务兼容。但由于其核心功能相对稳定，更新频率可能不高。
- **推荐使用**：**推荐**。对于需要构建复杂在线多人游戏功能（如派对、大厅）的项目，使用此官方框架比从头实现更可靠、更高效。它提供了经过验证的架构和与平台集成的模式。但需注意，由于 `EnabledByDefault` 为 `false`，你需要手动在项目中启用它。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineFramework/Tests)