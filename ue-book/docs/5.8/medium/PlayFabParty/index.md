# PlayFab Party

> PlayFab Party Socket Subsystem plugin

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `PlayFabParty` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2026-03-06 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/PlayFabParty) | |

## 用途

该插件为 Unreal Engine 提供了一个基于 PlayFab Party 服务的网络传输层实现。它通过实现 `ISocketSubsystem` 和 `FSocket` 接口，将 PlayFab Party 的多人游戏网络功能（如网络发现、连接管理、数据传输）集成到 UE 的标准网络框架中。这使得游戏可以使用 PlayFab 的多人游戏服务进行玩家匹配和网络通信，而无需直接处理底层的 Party API。

## 使用场景

- 你正在开发一个多人在线游戏，并希望使用 Microsoft PlayFab 服务来管理玩家匹配、网络连接和数据传输。
- 你的游戏需要跨平台（目前支持 Win64）的多人游戏功能，并希望利用 PlayFab 提供的可靠网络基础设施。
- 你希望将 PlayFab Party 的网络功能无缝集成到 UE 的 `UNetDriver` 和 `UIpConnection` 体系中，以便使用 UE 内置的网络复制和 RPC 系统。

## 蓝图用法

该插件主要提供底层的网络子系统实现，没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。其功能通过 UE 的标准网络驱动（`UPlayFabPartyNetDriver`）和套接字子系统在后台工作，对蓝图透明。

## C++ 用法

### 头文件引入

```cpp
#include "PlayFabInterface.h"
```

### 基本用法

该插件的核心是提供一个 `ISocketSubsystem` 的实现。通常，你不会直接创建它的实例，而是通过 `UPlayFabPartyNetDriver` 来使用它。`PlayFabInterface.h` 提供了一些辅助函数来查询 PlayFab 实体信息。

```cpp
// 查询某个 Xbox Live 用户 ID (Xuid) 是否有关联的 PlayFab 实体 ID
uint64 XboxUserId = 1234567890;
if (HaveEntityIdForXuid(XboxUserId))
{
    // 获取实体 ID
    const char* EntityId = GetEntityIdForXuid(XboxUserId);
    UE_LOG(LogTemp, Log, TEXT("PlayFab Entity ID for Xuid %llu: %hs"), XboxUserId, EntityId);
    
    // 获取实体令牌（如果可用）
    const char* EntityToken = GetEntityTokenForXuid(XboxUserId);
    if (EntityToken)
    {
        UE_LOG(LogTemp, Log, TEXT("Entity Token: %hs"), EntityToken);
    }
}
```

### 进阶用法

要使用此插件进行网络连接，你需要在项目的网络配置中指定使用 `PlayFabPartyNetDriver`。这通常在 `DefaultEngine.ini` 中配置：

```ini
[/Script/OnlineSubsystemUtils.IpNetDriver]
NetDriverClassName=/Script/PlayFabParty.PlayFabPartyNetDriver
```

然后，你可以像使用任何其他网络驱动一样，通过 `UIpNetDriver` 的接口（如 `InitConnect`， `InitListen`）来建立连接。底层的 `FPlayFabPartySocket` 和 `FPlayFabPartySocketSubsystem` 会处理与 PlayFab Party 服务的交互。

## Demo 示例

以下是一个概念性的示例，展示如何在 C++ 中初始化并使用 PlayFab Party 网络子系统。请注意，实际使用需要先配置好 PlayFab 开发者设置和 Xbox Live 身份验证。

**MyPlayFabNetGameMode.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "MyPlayFabNetGameMode.generated.h"

UCLASS()
class AMyPlayFabNetGameMode : public AGameModeBase
{
    GENERATED_BODY()

public:
    AMyPlayFabNetGameMode();

    virtual void InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage) override;
};
```

**MyPlayFabNetGameMode.cpp**
```cpp
#include "MyPlayFabNetGameMode.h"
#include "PlayFabPartyModule.h"
#include "PlayFabPartySocketSubsystem.h"
#include "OnlineSubsystem.h"
#include "OnlineSubsystemUtils.h"

AMyPlayFabNetGameMode::AMyPlayFabNetGameMode()
{
    // 确保 PlayFabParty 模块已加载
    FPlayFabPartyModule::Get();
}

void AMyPlayFabNetGameMode::InitGame(const FString& MapName, const FString& Options, FString& ErrorMessage)
{
    Super::InitGame(MapName, Options, ErrorMessage);

    // 获取在线子系统
    IOnlineSubsystem* OnlineSub = Online::GetSubsystem(GetWorld());
    if (OnlineSub)
    {
        // 获取套接字子系统，PlayFabParty 会注册自己
        ISocketSubsystem* SocketSub = ISocketSubsystem::Get(PLAYFABPARTY_SOCKETSUBSYSTEM);
        if (SocketSub)
        {
            FPlayFabPartySocketSubsystem* PlayFabSocketSub = static_cast<FPlayFabPartySocketSubsystem*>(SocketSub);
            if (PlayFabSocketSub->IsPlayFabPartyReady())
            {
                UE_LOG(LogTemp, Log, TEXT("PlayFab Party Socket Subsystem is ready!"));
                // 在这里可以使用 PlayFabSocketSub 创建套接字或进行其他网络操作
            }
            else
            {
                UE_LOG(LogTemp, Warning, TEXT("PlayFab Party Socket Subsystem is not ready yet."));
            }
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供在线子系统工具和 `UIpNetDriver` 基础类，是此插件运行的必要依赖。 |

## 维护状态

### 近期更新

- 2026-04-24 `101f2bf3` Enable GDK ARM64 support in plugins (requires April 2026 GDK & modern folder layout)
- 2026-04-14 `35e60df1` Migrate UE_LOG to UE_LOGF.
- 2026-03-09 `5eb8fada` [Backout] - CL51493025

### 维护评价

该插件创建于 2026 年 3 月，是一个非常新的插件。从 git 历史看，它在创建后的一个月内有多次更新，包括功能增强（ARM64 支持）和代码维护（日志迁移）。这表明它正处于**活跃维护**阶段。由于其明确依赖于特定的 GDK 版本和平台（Win64），它主要面向使用 PlayFab 和 Xbox 生态系统的项目。对于需要此特定网络解决方案的项目，推荐使用，但需注意其平台限制和对外部服务（PlayFab， Xbox Live）的依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/Microsoft/PlayFabParty)