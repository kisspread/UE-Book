# Socket Subsystem Steam (IP)

> Responsible for Steam net connections between users. Does NOT use NAT punchthrough, use the SteamSockets plugin for P2P support

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ 否 (`EnabledByDefault: false`) |
| 包含内容 | 否 |
| 模块 | SocketSubsystemSteamIP (RuntimeNoCommandlet) |
| 创建时间 | 2025-01-31 |
| 年龄标签 | 🆕 (~1年) |
| 平台 | Win64, Mac（排除 Win64:arm64） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/SocketSubsystemSteamIP) | |

## 用途

SocketSubsystemSteamIP 为 Unreal Engine 提供了基于 **Steam Networking API (ISteamNetworking)** 的 Socket 子系统实现。它将 UE 的 `ISocketSubsystem` 接口与 Steam 的 P2P 网络层对接，使得游戏可以使用 **Steam ID**（而非传统 IP 地址）来建立玩家之间的网络连接。

### 为什么存在？

UE5 的网络栈默认使用基于 BSD Socket 的 IP 网络。当游戏通过 Steam 分发时，需要一种机制让玩家通过 Steam 好友系统互相连接——而无需知道对方的真实 IP 地址。此插件实现了 `FSocketSubsystemSteam`（继承自 `ISocketSubsystem`），把 Steam P2P 通信包装成标准的 UE Socket 接口，使整个 UE 网络栈（NetDriver、NetConnection）能透明地通过 Steam 进行通信。

### 与 SteamSockets 插件的区别

插件名称中的 "(IP)" 是关键——它表明此插件使用的是 Steam 的 **IP-based** 网络模式。与另一个插件 `SteamSockets`（使用 Steam Datagram Relay / NAT punchthrough）不同，本插件：
- **不支持 NAT 穿透**（P2P relay 是另一条路径）
- 基于 `ISteamNetworking`（旧版 Steam P2P API，非 `ISteamNetworkingSockets`）
- 更接近传统 IP 网络行为，适合不需要 NAT punchthrough 但想用 Steam ID 寻址的场景

## 使用场景

- 你想让玩家通过 **Steam ID** 相互连接，而不需要知道对方的 IP 地址
- 你使用 `OnlineSubsystemSteam` 进行会话管理，希望网络层也通过 Steam 路由
- 你的游戏运行在 Steam 平台上，想利用 Steam 的 P2P relay 作为备选通信路径（当 `bAllowP2PPacketRelay=true`）
- 你需要一个替代默认 `IpNetDriver` 的网络驱动，让 UE 的 Replication 系统透明地走 Steam 通道

## 蓝图用法

此插件 **没有暴露任何蓝图节点**。它是一个底层 Socket 子系统，通过配置驱动，不提供 BlueprintCallable 接口。使用方式完全通过配置（DefaultEngine.ini）和 C++ 代码。

## C++ 用法

此插件主要通过 **配置** 和 **NetDriver 选择** 来使用，而非直接调用其 API。以下是开发者需要了解的核心交互方式。

### 头文件引入

```cpp
#include "SocketSubsystemSteam.h"        // FSocketSubsystemSteam 核心类
#include "SteamNetDriver.h"              // USteamNetDriver 网络驱动
#include "SteamNetConnection.h"          // USteamNetConnection 网络连接
#include "SocketSubsystemSteamIPModule.h" // 模块接口
```

### 核心架构

插件由三个主要类组成：

| 类 | 继承自 | 职责 |
|---|---|---|
| `FSocketSubsystemSteam` | `ISocketSubsystem` | Steam Socket 子系统单例，管理所有 Steam P2P 连接 |
| `USteamNetDriver` | `UIpNetDriver` | Steam 网络驱动，决定使用 Steam Socket 还是标准 IP |
| `USteamNetConnection` | `UIpConnection` | Steam 网络连接，跟踪连接生命周期 |

### 配置使用（DefaultEngine.ini）

```ini
[OnlineSubsystemSteam]
bUseSteamNetworking=true          ; 启用 Steam 网络（使此子系统成为默认 Socket 子系统）

[SocketSubsystemSteamIP]
bAllowP2PPacketRelay=true         ; 允许通过 Steam 服务器中继（当直连失败时）
P2PConnectionTimeout=45.0         ; P2P 会话超时（秒）
P2PCleanupTimeout=1.5             ; 断开连接后的清理延迟（秒）
```

> **注意**：`bAllowP2PPacketRelay`、`P2PConnectionTimeout`、`P2PCleanupTimeout` 原本在 `[OnlineSubsystemSteam]` 节下，现已迁移到 `[SocketSubsystemSteamIP]`。旧位置仍兼容但会输出废弃警告。

### 通过 NetDriver 使用

在 DefaultEngine.ini 中指定使用 Steam NetDriver：

```ini
[URL]
Port=7777

[/Script/OnlineSubsystemUtils.IpNetDriver]
NetDriverClassName=/Script/SocketSubsystemSteamIP.SteamNetDriver
```

或者在 C++ 中动态获取 Socket 子系统：

```cpp
// 获取 Steam Socket 子系统
ISocketSubsystem* SteamSockets = ISocketSubsystem::Get(FName(TEXT("STEAM")));
if (SteamSockets)
{
    // 创建一个 Steam 客户端 Socket
    FSocket* Socket = SteamSockets->CreateSocket(
        FName(TEXT("SteamClientSocket")),
        TEXT("MyGame Client Socket"),
        FNetworkProtocolTypes::SteamSocketsIP
    );
}

// 获取平台原生 Socket 子系统（绕过 Steam）
ISocketSubsystem* PlatformSockets = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
```

### Steam ID 地址解析

`FSocketSubsystemSteam` 能将 Steam ID 字符串解析为 `FInternetAddrSteam`：

```cpp
// 从 Steam ID 字符串创建地址
ISocketSubsystem* SteamSockets = ISocketSubsystem::Get(FName(TEXT("STEAM")));

// GetAddressFromString: 数字字符串会被解析为 SteamID，否则回退到标准 IP
TSharedPtr<FInternetAddr> Addr = SteamSockets->GetAddressFromString(TEXT("76561198012345678"));

// GetAddressInfo: 支持 Steam URL 前缀
FAddressInfoResult Result = SteamSockets->GetAddressInfo(
    TEXT("76561198012345678"),  // Steam ID（纯数字）
    TEXT("7777")                // 端口（在 Steam 中对应 channel）
);
```

### 调试命令

在非 Shipping 构建中，控制台命令 `dumpsteamsessions` 可以输出所有当前 Steam P2P 连接的状态信息。

## Demo 示例

### 最小配置示例

**DefaultEngine.ini** — 启用 Steam Socket 子系统：

```ini
[OnlineSubsystem]
DefaultPlatformService=Steam

[OnlineSubsystemSteam]
bEnabled=true
bUseSteamNetworking=true

[SocketSubsystemSteamIP]
bAllowP2PPacketRelay=true
P2PConnectionTimeout=45.0
P2PCleanupTimeout=1.5
```

**Build.cs** — 依赖声明：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "Core",
    "Engine",
    "Sockets",
    "OnlineSubsystemUtils",
    "SocketSubsystemSteamIP"
});
```

**MyGameNetDriver.h** — 自定义 NetDriver（可选，直接使用 USteamNetDriver 也可以）：

```cpp
#pragma once
#include "SteamNetDriver.h"
#include "MyGameNetDriver.generated.h"

UCLASS()
class UMyGameNetDriver : public USteamNetDriver
{
    GENERATED_UCLASS_BODY()
    // 可在此添加游戏特定的网络逻辑
};
```

### C++ 获取 Socket 子系统

```cpp
// MyGameSubsystem.cpp
#include "SocketSubsystemSteam.h"
#include "Sockets.h"

void UMyGameSubsystem::InitSteamSocket()
{
    // 检查 Steam Socket 子系统是否可用
    ISocketSubsystem* SteamSS = ISocketSubsystem::Get(FName(TEXT("STEAM")));
    if (!SteamSS)
    {
        UE_LOG(LogTemp, Warning, TEXT("Steam Socket Subsystem not available"));
        return;
    }

    // 获取本地绑定地址（返回 Steam ID 地址）
    TArray<TSharedRef<FInternetAddr>> BindAddrs = SteamSS->GetLocalBindAddresses();
    for (const auto& Addr : BindAddrs)
    {
        UE_LOG(LogTemp, Log, TEXT("Local Steam Address: %s"), *Addr->ToString(true));
    }
}
```

## 模块依赖

从 `SocketSubsystemSteamIP.Build.cs` 提取：

| 模块 | 用途 |
|---|---|
| `Core` | 引擎核心基础模块 |
| `Engine` | 引擎核心功能 |
| `NetCore` | 网络核心类型和工具 |
| `Sockets` | Socket 子系统基类接口 |
| `OnlineSubsystemUtils` | 在线子系统工具函数 |
| `CoreOnline` | 在线服务类型定义（私有） |
| `SteamShared` | Steam SDK 共享加载逻辑（私有） |
| `CoreUObject` | UObject 系统（私有） |
| `Steamworks` | Steam SDK 静态库（第三方，私有） |

### Plugin 依赖

| Plugin | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 在线子系统工具 |
| `SteamShared` | Steam SDK DLL 加载和共享 |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-06-26 | `a2e7518` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files | 自动生成的 .cpp 文件内联优化，批量工具改动 |
| 2025-06-03 | `0a44e4b` | Plugin modules can be included & excluded on a per-architecture basis | 新增 `PlatformArchitectureDenyList: ["Win64:arm64"]`，排除 ARM64 平台 |
| 2025-04-23 | `93a1308` | Used LyraGame build target to convert all files to have dllstorage | API 导出宏从类型级改为方法/变量级，改善 DLL 边界 |

### 维护评价

- **创建时间**：2025-01-31，插件相对年轻（~1年）
- **维护状态**：**维护中** — 最近 3 次提交均为引擎级别的批量重构（inline generated、架构过滤、DLL storage），非此插件特有的功能更新，但说明它仍在活跃的代码库中被持续维护
- **代码质量**：代码结构清晰，注释完整，有完善的连接生命周期管理
- **已知限制**：
  - 不支持 NAT 穿透（需使用 SteamSockets 插件）
  - 使用的是旧版 `ISteamNetworking` API（非 `ISteamNetworkingSockets`）
  - 仅支持 Win64 和 Mac 平台
  - 无自动化测试用例
  - `TranslateErrorCode` 有 TODO 注释，错误码转换尚未完善
- **推荐使用**：如果你需要通过 Steam ID 进行 IP-style 的 P2P 通信且不需要 NAT punchthrough，此插件是合适的选择。如果需要更现代的 Steam 网络功能（NAT 穿透、Steam Datagram Relay），应使用 `SteamSockets` 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/SocketSubsystemSteamIP)
- 测试用例：无（此插件无自动化测试）
