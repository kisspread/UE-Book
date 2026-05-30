# Steam Sockets

> New Steamworks Networking code that supports the SteamSockets interface. NOTE: This plugin is only compatible with the SteamSockets Netdriver. It will not work if the proper netdriver definitions have not been set.

| 属性 | 值 |
|---|---|
| 中文名 | Steam Socket 网络 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SteamSockets` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-03 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamSockets) | |

## 用途

本插件提供了一套基于 Valve 新版 Steam 网络接口 (Steam Networking Sockets) 的网络驱动（NetDriver）和 Socket 子系统（Socket Subsystem）实现。它的主要目的是替换 Unreal Engine 默认的 IP 套接字通信方式，转而使用 Steam 的网络层进行数据传输。

**解决的问题**：
1. **Steam 平台集成**：为需要通过 Steam 进行多人游戏的项目提供原生网络支持。
2. **P2P 与中继网络**：支持 Steam 的 P2P 直连和通过其中继网络（Steam Datagram Relay, SDR）进行连接，可以在不暴露玩家真实 IP 的情况下提升连接质量和穿透性。
3. **协议统一**：通过 `FSteamSocketsSubsystem`、`USteamSocketsNetDriver` 和 `USteamSocketsNetConnection` 等类，为 UE 的网络栈提供了一个完整的、专为 Steam 优化的后端实现。

**关键限制**：此插件**必须**与专门的 `SteamSockets` 网络驱动配合使用。它不能与 UE 的默认 IP 网络驱动或其他网络驱动混合使用，否则协议将无法正常工作。

## 使用场景

- **Steam 多人游戏**：你正在开发一款计划在 Steam 上发售的多人游戏，希望利用 Steam 的网络基础设施（如好友列表、邀请、中继服务）来建立和维持玩家之间的连接。
- **P2P 联机**：你需要实现玩家之间的点对点（Peer-to-Peer）连接，避免玩家直接暴露公网 IP，同时利用 Steam 的 NAT 穿透能力。
- **专用服务器**：你的专用服务器（Dedicated Server）需要作为 Steam 服务器运行，接收来自 Steam 客户端的连接。插件支持服务器端 Steam API 初始化。

## 蓝图用法

该插件主要工作在网络底层，不直接向蓝图暴露通用的 `BlueprintCallable` 函数。其功能主要通过**项目配置**和**网络设置**来使用。

### 核心配置

要启用此插件，需要在项目的 `DefaultEngine.ini` 中进行配置，将默认的网络驱动替换为 Steam Sockets 驱动。

```ini
[/Script/OnlineSubsystemSteam.OnlineSubsystemSteam]
bEnabled=true
SteamDevAppId=480  ; 使用 Valve 提供的测试 AppID 480

[URL]
Port=7777

[/Script/Engine.GameEngine]
!NetDriverDefinitions=ClearArray
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="OnlineSubsystemSteam.SteamNetDriver",DriverClassNameFallback="OnlineSubsystemSteam.SteamNetDriver")
```

## C++ 用法

### 头文件引入

```cpp
#include "SteamSocketsSubsystem.h"
#include "SteamSocketsModule.h"
```

### 基本用法

此插件通常通过引擎的网络栈在内部调用，开发者很少需要直接操作其类。但你可以通过模块接口查询插件状态。

```cpp
// 检查 SteamSockets 模块是否已加载并启用
if (FSteamSocketsModule::IsAvailable())
{
    FSteamSocketsModule& SteamSocketsModule = FSteamSocketsModule::Get();
    if (SteamSocketsModule.IsSteamSocketsEnabled())
    {
        UE_LOG(LogTemp, Log, TEXT("Steam Sockets 插件已启用。"));
    }
}
```

### 进阶用法

在自定义网络逻辑或调试时，你可能需要访问底层的 Socket 子系统实例。这通常通过 `ISocketSubsystem::Get` 获取，但你需要确保网络栈配置正确，使其返回的是 `FSteamSocketsSubsystem` 实例。

```cpp
// 获取 Socket 子系统（在网络栈初始化后）
ISocketSubsystem* SocketSub = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
if (SocketSub)
{
    FString APIName = SocketSub->GetSocketAPIName();
    UE_LOG(LogTemp, Log, TEXT("当前使用的 Socket API: %s"), *APIName);
    // 对于本插件，此名称应为 "SteamSockets"
    
    // 还可以检查是否使用了中继网络
    FSteamSocketsSubsystem* SteamSocketSub = static_cast<FSteamSocketsSubsystem*>(SocketSub);
    if (SteamSocketSub && SteamSocketSub->IsUsingRelayNetwork())
    {
        UE_LOG(LogTemp, Log, TEXT("当前使用 Steam 中继网络。"));
    }
}
```
*(示例思路基于 `FSteamSocketsSubsystem` 公共接口)*

## Demo 示例

以下是一个最小的 Actor 示例，用于在运行时检查 SteamSockets 插件的状态。

**SteamSocketsStatusActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SteamSocketsStatusActor.generated.h"

UCLASS()
class YOURPROJECT_API ASteamSocketsStatusActor : public AActor
{
    GENERATED_BODY()

public:
    ASteamSocketsStatusActor();

protected:
    virtual void BeginPlay() override;
};
```

**SteamSocketsStatusActor.cpp**
```cpp
#include "SteamSocketsStatusActor.h"
#include "SteamSocketsModule.h"
#include "Engine/Engine.h"

ASteamSocketsStatusActor::ASteamSocketsStatusActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void ASteamSocketsStatusActor::BeginPlay()
{
    Super::BeginPlay();

    if (FSteamSocketsModule::IsAvailable())
    {
        FSteamSocketsModule& Module = FSteamSocketsModule::Get();
        FString Status = Module.IsSteamSocketsEnabled() ? TEXT("已启用") : TEXT("已禁用");
        
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Green, 
                FString::Printf(TEXT("Steam Sockets 插件状态: %s"), *Status));
        }
    }
    else
    {
        if (GEngine)
        {
            GEngine->AddOnScreenDebugMessage(-1, 5.f, FColor::Red, 
                TEXT("Steam Sockets 插件模块未加载。"));
        }
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | UE 在线子系统框架基础 |
| `OnlineSubsystemSteam` | Steam 在线子系统具体实现，提供 Steam 用户身份、会话等基础服务 |
| `SteamShared` | Steam SDK 公共代码和接口，被多个 Steam 相关插件共享 |
| `Networking` | UE 网络核心模块，提供 `UNetDriver`、`UNetConnection` 等基类 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将UE_LOG宏迁移到UE_LOGF格式，改进日志系统。 |
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复静态分析警告，优化三元运算符使用。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为源码文件添加UE_INLINE_GENERATED_CPP_BY_NAME宏，优化编译。 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 插件模块现在支持按CPU架构进行包含/排除。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 为方法和静态变量添加DLL导出标识，提升二进制兼容性。 |

### 维护评价

- **创建时间**：该插件创建于 2019 年 10 月，已有约 6 年历史。
- **最近更新**：最近的提交（2026年4月，2025年多次）均为底层代码维护，包括日志迁移、编译警告修复、构建系统改进等，表明插件仍在持续维护中，但已无重大的新功能开发。
- **活跃度**：属于**维护中**状态。更新主要围绕引擎大版本升级、编译兼容性和代码质量，保证了插件在最新引擎版本（如5.8）上的可用性。
- **稳定性**：作为一个成熟的网络协议实现，其核心功能已稳定。主要限制是它需要特定的网络驱动配置，且不支持与其他驱动混用。
- **推荐**：**推荐使用**。如果你的游戏面向 Steam 平台，并且需要利用其网络特性（如 P2P、中继），这是一个官方支持的、成熟的解决方案。请务必按照文档进行正确的配置。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/Steam/SteamSockets)