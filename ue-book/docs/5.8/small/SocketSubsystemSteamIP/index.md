# Socket Subsystem Steam (IP)

> Responsible for Steam net connections between users. Does NOT use NAT punchthrough, use the SteamSockets plugin for P2P support（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | Steam IP 套接字子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SocketSubsystemSteamIP` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2025-01-31 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/SocketSubsystemSteamIP) | |

## 用途

该插件将 Steam 的底层网络接口封装为虚幻引擎标准的 `ISocketSubsystem` 实现，主要目的是在多人游戏场景中，通过 Steam 的通信网络（而非传统的 IP/端口直连）建立玩家之间的连接。与另一个 `SteamSockets` 插件不同，**它不依赖 Steam 的 NAT 穿透（P2P 中继）技术**，而是提供了一种基于 Steam ID 的、相对简单的网络连接方案。它适用于需要通过 Steam 网络但又不希望使用复杂 P2P 穿透逻辑的场景。

## 使用场景

*   你正在开发一款多人游戏，希望利用 Steam 的社交和网络基础设施进行玩家匹配与连接。
*   你的游戏架构已经基于传统的 `UIpNetDriver` 和 `UIpConnection` 进行设计，现在想无缝切换到使用 Steam 网络通道，而无需重写大量网络层代码。
*   你需要实现专用服务器（Dedicated Server）模式，并且希望服务器也能通过 Steam 网络与客户端通信。
*   **重要**：如果你需要的是玩家之间点对点（P2P）直接连接并希望利用 Steam 的 NAT 穿透功能，应使用 `SteamSockets` 插件，而非本插件。

## 蓝图用法

该插件主要提供 C++ 运行时接口和网络驱动/连接类，不包含可供蓝图直接调用的函数或属性。所有网络操作均在底层通过引擎的网络子系统自动处理。

## C++ 用法

### 头文件引入

```cpp
#include "SocketSubsystemSteam.h"
#include "SteamNetDriver.h"
#include "SteamNetConnection.h"
```

### 基本用法

核心是获取并使用 `FSocketSubsystemSteam` 实例。

```cpp
// 来源: Engine/Plugins/Online/SocketSubsystemSteamIP/Public/SocketSubsystemSteam.h
#include "SocketSubsystem.h"

// 获取 Steam IP Socket 子系统
ISocketSubsystem* SteamSocketSubsystem = ISocketSubsystem::Get(STEAMIP_SUBSYSTEMNAME);

if (SteamSocketSubsystem)
{
    // 创建一个用于 Steam 网络的 Socket（通常是数据报/Datagram 类型）
    FSocket* MySteamSocket = SteamSocketSubsystem->CreateSocket(NAME_DGram, TEXT("MySteamSocket"), NAME_IP);
    
    if (MySteamSocket)
    {
        // 创建一个 Steam 地址
        TSharedRef<FInternetAddr> SteamAddr = SteamSocketSubsystem->CreateInternetAddr();
        
        // 绑定或连接 (地址操作逻辑取决于具体需求)
        // MySteamSocket->Bind(*SteamAddr);
        // MySteamSocket->Connect(*SteamAddr);
        
        // ... 使用 Socket 进行 Send/Recv 等操作 ...
        
        // 使用完毕后销毁
        SteamSocketSubsystem->DestroySocket(MySteamSocket);
    }
}
```

### 进阶用法

#### 配置网络驱动器和连接

在配置引擎网络驱动器（NetDriver）时，可以指定使用 Steam 网络。

```cpp
// 来源: Engine/Plugins/Online/SocketSubsystemSteamIP/Public/SteamNetDriver.h
USteamNetDriver* SteamNetDriver = NewObject<USteamNetDriver>();
// SteamNetDriver->bIsPassthrough = false; // 如果需要直接使用 IP，则设为 true
// 配置其他参数...
// SteamNetDriver->InitBase(...);

// 连接类通常自动使用 USteamNetConnection，无需手动创建
```

#### 连接管理与状态监控

`FSocketSubsystemSteam` 内部管理着 P2P 连接状态。对于需要处理连接生命周期的高级用例，可以关注其包级作用域内的方法。

```cpp
// 以下操作通常由引擎内部或会话接口调用，开发者较少直接接触。
// 来源: Engine/Plugins/Online/SocketSubsystemSteamIP/Public/SocketSubsystemSteam.h

// 假设已有一个 FSocketSubsystemSteam 指针 `SteamSS`
// 关联游戏服务器的 Steam ID
// SteamSS->UpdateGameServerId(GameServerSteamID);

// 清理已断开的连接（内部 Tick 会调用）
// SteamSS->CleanupDeadConnections();

// 获取网络信息用于调试
// SteamSS->DumpAllOpenSteamSessions();
```

## Demo 示例

一个最小化的 C++ 示例，展示如何在 Actor 中创建一个 Steam IP Socket 并尝试绑定。

```cpp
// MySteamNetworkActor.h
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MySteamNetworkActor.generated.h"

UCLASS()
class AMySteamNetworkActor : public AActor
{
    GENERATED_BODY()
    
public:
    AMySteamNetworkActor();
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

private:
    // 我们创建的 Steam Socket
    FSocket* SteamSocket;
};

// MySteamNetworkActor.cpp
#include "MySteamNetworkActor.h"
#include "SocketSubsystem.h"
#include "SocketSubsystemSteam.h" // 关键头文件

AMySteamNetworkActor::AMySteamNetworkActor()
{
    PrimaryActorTick.bCanEverTick = false;
    SteamSocket = nullptr;
}

void AMySteamNetworkActor::BeginPlay()
{
    Super::BeginPlay();
    
    // 1. 获取 Socket 子系统
    ISocketSubsystem* SocketSub = ISocketSubsystem::Get(STEAMIP_SUBSYSTEMNAME);
    if (!SocketSub)
    {
        UE_LOG(LogTemp, Error, TEXT("无法获取 Steam Socket 子系统，请检查插件是否启用。"));
        return;
    }
    
    // 2. 创建 Socket
    SteamSocket = SocketSub->CreateSocket(NAME_DGram, TEXT("DemoSteamSocket"), NAME_IP);
    if (!SteamSocket)
    {
        UE_LOG(LogTemp, Error, TEXT("创建 Steam Socket 失败。"));
        return;
    }
    
    // 3. 创建并绑定一个地址（绑定到任意可用端口）
    TSharedRef<FInternetAddr> BindAddr = SocketSub->CreateInternetAddr();
    BindAddr->SetIp(0); // INADDR_ANY
    BindAddr->SetPort(0); // 系统分配端口
    
    if (SteamSocket->Bind(*BindAddr))
    {
        UE_LOG(LogTemp, Log, TEXT("Steam Socket 成功绑定到地址: %s"), *BindAddr->ToString(true));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Steam Socket 绑定失败。"));
    }
    
    // 4. 输出 Socket API 名称
    UE_LOG(LogTemp, Log, TEXT("当前使用的 Socket API: %s"), SocketSub->GetSocketAPIName());
}

void AMySteamNetworkActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (SteamSocket)
    {
        // 在 Actor 销毁时清理 Socket
        ISocketSubsystem* SocketSub = ISocketSubsystem::Get(STEAMIP_SUBSYSTEMNAME);
        if (SocketSub)
        {
            SocketSub->DestroySocket(SteamSocket);
            SteamSocket = nullptr;
        }
    }
    Super::EndPlay(EndPlayReason);
}
```

**重要提示**：要使以上代码正常工作，必须在项目的 `.uproject` 或 `DefaultEngine.ini` 中启用该插件，并且项目需要正确集成 Steamworks SDK。由于该插件默认禁用（`EnabledByDefault: false`），你需要手动启用它。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供在线子系统的通用工具和功能。 |
| `SteamShared` | 提供被多个 Steam 相关插件共享的基础设施，特别是 `FInternetAddrSteam` 类的定义。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 UE_LOG 迁移为新版 UE_LOGF 宏。 |
| 2025-06-26 | `a2e75189` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 为有对应 .gen.cpp 文件的源文件添加了 UE_INLINE_GENERATED_CPP_BY_NAME 宏，属于构建系统优化。 |
| 2025-06-03 | `0a44e4b8` | Plugin modules can be included & excluded on a per-architecture basis. | 新增插件模块可按 CPU 架构进行包含/排除的功能，属于构建系统增强。 |
| 2025-04-23 | `93a13080` | Used LyraGame build target to find and convert all files to have dllstorage on methods/staticvar ins | 利用 LyraGame 构建目标，将文件中的方法/静态变量声明统一转换为具有 DLL 导出属性。 |
| 2025-02-15 | `aa030a9a` | OSSSteam: Turn off the accidental setting of steam protocol as the default socketsubsystem. | 修复了一个导致 Steam 协议被意外设置为默认 Socket 子系统的问题。 |

### 维护评价

该插件创建于 2025 年初，是一个相对较新的模块。从 git 历史看，最近一年有持续的更新，但**内容多为构建系统优化、宏迁移和兼容性修复，未见新功能或重大网络逻辑改动**。这表明插件处于**基础维护状态**，核心功能已稳定，但开发侧重点不在此。

考虑到它是由 Epic 官方从 `OnlineSubsystemSteam` 中重构而来，代码质量有保障，但作为“IP”方案，其设计初衷可能不适用于需要最高效率或直接 P2P 的场景。**推荐在需要基于 Steam 网络但无需复杂 P2P 穿透的多人游戏架构中谨慎评估使用。** 使用前务必在 `.uplugin` 或项目配置中手动启用。

## 相关链接

*   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/SocketSubsystemSteamIP)
*   （该插件无官方文档和独立测试用例链接）