# Steam Sockets

> New Steamworks Networking code that supports the SteamSockets interface. NOTE: This plugin is only compatible with the SteamSockets Netdriver. It will not work if the proper netdriver definitions have not been set.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | SteamSockets (Runtime) |
| 创建时间 | 2019-09-18 |
| 年龄标签 | 👴 老古董（约7年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamSockets) | |

## 用途

SteamSockets 插件为 UE5 提供了基于 Valve 的 **ISteamNetworkingSockets** API 的网络传输层实现。它是一个完整的 `UNetDriver` / `UNetConnection` / `ISocketSubsystem` 三层替换方案，替代 UE 默认的 UDP/IP 套接字通信，改用 Steam 的可靠/不可靠消息传输协议。

**核心价值：**
- **NAT 穿透**：通过 Steam 的 Relay Network（中继网络）自动处理 NAT 穿透，无需玩家手动配置端口转发
- **P2P 连接**：支持基于 Steam ID 的点对点连接（`SteamSocketsP2P`），玩家只需知道对方的 Steam ID 即可连接
- **IP 连接**：同时支持传统 IP 地址连接（`SteamSocketsIP`），可用于局域网场景
- **加密与认证**：利用 Steam 内置的加密和身份验证机制（通过 `InitAuthentication()`），无需自行实现
- **中继网络**：当直连不可用时，自动通过 Valve 的全球中继服务器转发数据

**与 OnlineSubsystemSteam 的关系：** 本插件依赖 `OnlineSubsystemSteam` 和 `SteamShared` 插件，但提供了独立的 Socket 子系统，避免了旧版 SteamNetworking（基于 UDP）的诸多限制。

## 使用场景

- 你正在开发一个需要 Steam 多人联机的 PC 游戏 → 使用 SteamSockets 替代默认 UDP NetDriver
- 你的游戏需要 NAT 穿透而不想自行维护 STUN/TURN 服务器 → 利用 Steam Relay Network
- 你正在做局域网对战功能（如网吧环境） → 使用 `SteamSocketsIP` 协议并设置 `bIsLanMatch`
- 你有一个专用服务器需要通过 Steam 网络接受连接 → 专用服务器会自动延迟登录并创建监听
- 你在做 Session 搜索和匹配（通过 Steam OSS） → 配合 `OnlineSubsystemSteam` 使用

**⚠️ 重要限制：**
- `EnabledByDefault = false`，必须手动在 Project Settings → Plugins 中启用
- 仅支持 **Win64、Mac、Linux** 平台（不支持 Win64:arm64）
- **必须**同时配置正确的 NetDriver 类型，否则插件不会工作
- 不支持与其他 NetDriver/NetConnection 类型混用

## 蓝图用法

SteamSockets 插件**没有暴露任何蓝图节点**。所有功能通过引擎的网络框架（NetDriver / NetConnection）在底层自动工作。配置通过以下方式完成：

### 配置方法

**1. Engine.ini 配置**

在 `DefaultEngine.ini` 中指定使用 SteamSockets NetDriver：

```ini
[URL]
Port=7777

[/Script/OnlineSubsystemSteam.OnlineSubsystemSteam]
bEnabled=true
bUseSteamNetworking=true
bAllowP2PPacketRelay=true

[/Script/Engine.GameEngine]
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="/Script/SteamSockets.SteamSocketsNetDriver",DriverClassNameFallback="/Script/SteamSockets.SteamSocketsNetDriver")
```

**2. 关键配置项说明**

| 配置项 | 位置 | 说明 |
|---|---|---|
| `bUseSteamNetworking` | `[OnlineSubsystemSteam]` | 是否使用 Steam 网络（控制 Socket 子系统注册） |
| `bAllowP2PPacketRelay` | `[OnlineSubsystemSteam]` | 是否允许使用 P2P 中继网络 |
| `NetDriverDefinitions` | `[GameEngine]` | 将 NetDriver 指向 SteamSocketsNetDriver |

**3. 调试命令（非 Shipping 构建）**

在控制台中可以使用以下命令：

| 命令 | 说明 |
|---|---|
| `PrintSteamSocketInfo` | 打印当前所有 Socket 的信息 |
| `PrintPendingSteamSocketInfo` | 打印等待登录完成的 Pending Socket |
| `ClearSteamSocketInfo` | 强制清理所有 Socket 信息 |
| `TogglePeekMessaging` | 切换 Peek 消息测试模式 |

## C++ 用法

### 头文件引入

```cpp
// NetDriver 类
#include "SteamSocketsNetDriver.h"

// NetConnection 类
#include "SteamSocketsNetConnection.h"

// Socket 子系统
#include "SteamSocketsSubsystem.h"

// 类型定义（协议类型、Socket Handle 类型）
#include "SteamSocketsTypes.h"

// Steam Socket 实现（内部类，一般不需要直接引用）
#include "SteamSocket.h"

// IP 地址类
#include "IPAddressSteamSockets.h"
```

### 基本用法：获取 Socket 子系统

SteamSockets 子系统在模块启动时自动注册为 `STEAM_SOCKETS_SUBSYSTEM`（即 `FName("SteamSockets")`）。

```cpp
// 获取 SteamSockets 子系统实例
FSteamSocketsSubsystem* SteamSocketSub = static_cast<FSteamSocketsSubsystem*>(
    ISocketSubsystem::Get(STEAM_SOCKETS_SUBSYSTEM)
);

// 检查 Steam 是否已初始化
if (SteamSocketSub && SteamSocketSub->IsSteamInitialized())
{
    // Steam Sockets 已就绪
}

// 检查是否正在使用中继网络
bool bUsingRelays = SteamSocketSub->IsUsingRelayNetwork();
```

来源：`SteamSocketsSubsystem.cpp` / `SteamSocketsNetDriver.cpp`

### 基本用法：创建 Socket

```cpp
// 创建一个 P2P Socket（通过 Steam Relay Network）
FSocket* P2PSocket = SteamSocketSub->CreateSocket(
    FName(TEXT("SteamSocket")),
    TEXT("My P2P Socket"),
    FNetworkProtocolTypes::SteamSocketsP2P
);

// 创建一个 IP Socket（用于局域网）
FSocket* IPSocket = SteamSocketSub->CreateSocket(
    FName(TEXT("SteamSocket")),
    TEXT("My LAN Socket"),
    FNetworkProtocolTypes::SteamSocketsIP
);

// 创建 Socket 时不指定协议，会根据 relay 设置自动选择
FSocket* AutoSocket = SteamSocketSub->CreateSocket(
    FName(TEXT("SteamSocket")),
    TEXT("Auto Socket"),
    NAME_None  // 自动选择：有 relay 用 P2P，否则用 IP
);
```

来源：`SteamSocketsSubsystem.cpp` 第 218-242 行

### 进阶用法：自定义发送模式

`FSteamSocket` 的发送模式映射到 Steam API 的消息发送标志：

```cpp
FSteamSocket* SteamSocket = static_cast<FSteamSocket*>(SomeSocket);

// 设置为可靠传输（默认是 UnreliableNoNagle）
// 对应 k_nSteamNetworkingSend_Reliable
SteamSocket->SetSendMode(k_nSteamNetworkingSend_Reliable);

// 设置 NoDelay 会根据当前模式调整：
// - Unreliable → UnreliableNoDelay
// - UnreliableNoNagle → UnreliableNoDelay
// - Reliable → ReliableNoNagle
SteamSocket->SetNoDelay(true);

// 关闭 linger（默认不 linger）
SteamSocket->SetLinger(false);
```

来源：`SteamSocket.cpp` 第 459-497 行

### 进阶用法：LAN 模式

当 URL 包含 `bIsLanMatch` 或 `bPassthrough` 选项时，NetDriver 会自动切换到 IP 模式并设置 LAN 标志：

```cpp
// LAN 模式会自动设置 k_ESteamNetworkingConfig_IP_AllowWithoutAuth
// 这意味着跳过 SDR 验证，允许无 Steam 认证的本地连接
// SteamSocket->bIsLANSocket = true; (由 NetDriver 自动设置)
```

来源：`SteamSocketsNetDriver.cpp` 第 67-69 行、`SteamSocket.cpp` 第 499-520 行

## Demo 示例

### 最小连接示例（Build.cs 依赖）

```csharp
// MyModule.Build.cs
public class MyModule : ModuleRules
{
    public MyModule(ReadOnlyTargetRules Target) : base(Target)
    {
        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "OnlineSubsystem",
            "OnlineSubsystemSteam"
        });

        // SteamSockets 的模块名
        PrivateDependencyModuleNames.Add("SteamSockets");
    }
}
```

### 运行时检查 SteamSockets 状态

```cpp
// MyGameInstance.h
#pragma once
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

UCLASS()
class UMyGameInstance : public UGameInstance
{
    GENERATED_BODY()
public:
    virtual void Init() override;
    
    UFUNCTION(BlueprintCallable, Category = "Network")
    bool IsSteamSocketsAvailable() const;
};

// MyGameInstance.cpp
#include "MyGameInstance.h"
#include "SteamSocketsModule.h"
#include "SteamSocketsSubsystem.h"
#include "SteamSocketsTypes.h"

void UMyGameInstance::Init()
{
    Super::Init();

    // 检查 SteamSockets 模块是否已加载且启用
    if (FSteamSocketsModule::IsAvailable())
    {
        FSteamSocketsModule& SteamSocketsModule = FSteamSocketsModule::Get();
        if (SteamSocketsModule.IsSteamSocketsEnabled())
        {
            UE_LOG(LogTemp, Log, TEXT("SteamSockets is active!"));

            // 获取子系统
            FSteamSocketsSubsystem* Sub = static_cast<FSteamSocketsSubsystem*>(
                ISocketSubsystem::Get(STEAM_SOCKETS_SUBSYSTEM)
            );
            if (Sub)
            {
                UE_LOG(LogTemp, Log, TEXT("Using relay network: %d"), Sub->IsUsingRelayNetwork());
                UE_LOG(LogTemp, Log, TEXT("Steam initialized: %d"), Sub->IsSteamInitialized());
            }
        }
    }
}

bool UMyGameInstance::IsSteamSocketsAvailable() const
{
    return FSteamSocketsModule::IsAvailable() && 
           FSteamSocketsModule::Get().IsSteamSocketsEnabled();
}
```

### DefaultEngine.ini 完整配置

```ini
[URL]
Port=7777

[OnlineSubsystem]
DefaultPlatformName=Steam

[OnlineSubsystemSteam]
bEnabled=true
bUseSteamNetworking=true
bAllowP2PPacketRelay=true
SteamDevAppId=480

[/Script/Engine.GameEngine]
!NetDriverDefinitions=ClearArray
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="/Script/SteamSockets.SteamSocketsNetDriver",DriverClassNameFallback="/Script/SteamSockets.SteamSocketsNetDriver")
+NetDriverDefinitions=(DefName="DemoNetDriver",DriverClassName="/Script/Engine.NetDriver",DriverClassNameFallback="/Script/Engine.NetDriver")
```

## 模块依赖

从 `SteamSockets.Build.cs` 的依赖关系提取。注意：这些是插件自身的**私有依赖**，使用者的模块不需要直接引用这些（除了 `OnlineSubsystemSteam`）。

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `NetCore` | 网络核心模块 |
| `Engine` | 引擎核心（UNetDriver 基类等） |
| `Sockets` | Socket 子系统接口（ISocketSubsystem） |
| `OnlineSubsystem` | 在线子系统基类 |
| `OnlineSubsystemSteam` | Steam 在线子系统（获取 Steam API 句柄、登录状态） |
| `PacketHandler` | 数据包处理器（连接握手、加密） |
| `SteamShared` | Steam SDK 共享模块（DLL 加载管理） |
| `Steamworks` | Valve Steam SDK 静态库（第三方） |

**使用者需要在 Build.cs 中添加的依赖：**
- 如果只是通过 NetDriver 框架使用：`OnlineSubsystemSteam`（通常已添加）
- 如果需要直接访问子系统：额外添加 `SteamSockets`

## 架构概览

```
┌──────────────────────────────────────────────┐
│  USteamSocketsNetDriver                      │
│  (继承 UNetDriver，管理连接生命周期)           │
├──────────────────────────────────────────────┤
│  USteamSocketsNetConnection                  │
│  (继承 UNetConnection，处理单个连接的数据收发) │
├──────────────────────────────────────────────┤
│  FSteamSocket                                │
│  (继承 FSocket，封装 ISteamNetworkingSockets) │
├──────────────────────────────────────────────┤
│  FSteamSocketsSubsystem                      │
│  (继承 ISocketSubsystem，Socket 工厂 + 状态管理)│
├──────────────────────────────────────────────┤
│  FInternetAddrSteamSockets                   │
│  (继承 FInternetAddr，Steam 地址抽象)         │
├──────────────────────────────────────────────┤
│  FSteamSocketsTaskManager                    │
│  (Steam API 回调事件队列)                     │
├──────────────────────────────────────────────┤
│  Valve ISteamNetworkingSockets API           │
└──────────────────────────────────────────────┘
```

### 两种网络协议

| 协议 | 说明 | 使用场景 |
|---|---|---|
| `SteamSocketsP2P` | 通过 Steam ID 连接，走 Relay Network | 互联网匹配、P2P 房间 |
| `SteamSocketsIP` | 传统 IP 地址连接 | 局域网、专用服务器 |

协议类型由 `FNetworkProtocolTypes::SteamSocketsP2P` 和 `FNetworkProtocolTypes::SteamSocketsIP` 定义。

## 维护状态

### 近期更新

| 日期 | Commit | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed8231` | Fix warning V623: Consider inspecting the '?:' operator | 静态分析警告修复，非功能性更新 |
| 2025-06-26 | `a2e75189887d` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 代码生成优化，非功能性更新 |
| 2025-06-03 | `0a44e4b88efb` | Plugin modules per-architecture include/exclude | 构建系统改进，排除了 Win64:arm64 |

### 维护评价

- **创建时间**：2019-09-18，约7年历史
- **最近更新**：最近 3 次提交（2025-06 至 2025-07）都是编译/构建相关的修复，**没有功能性更新**
- **维护状态**：**维护不活跃** — 插件架构成熟稳定，但近 2 年内没有实质性功能更新
- **已知限制**：
  - 不支持 `Wait` / `WaitForPendingConnection` / `SetNonBlocking` 等阻塞式 API
  - 最大消息大小受限于 `k_cbMaxSteamNetworkingSocketsMessageSizeSend`
  - `UNetConnection` 的最大包大小被硬编码为 1024（Steam 实际支持 512KB）
  - Linux 平台上 `SteamNetworkingUtils()` 初始化有已知问题（代码中有 `#if !PLATFORM_LINUX` 保护）
- **推荐**：✅ **推荐使用** — 作为 Steam 多人游戏的标准网络层，这是官方推荐的方案，架构成熟稳定

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/Steam/SteamSockets)
- [Steam ISteamNetworkingSockets API 文档](https://partner.steamgames.com/doc/api/ISteamNetworkingSockets)
- [Steam 网络消息发送标志说明](https://partner.steamgames.com/doc/api/steamnetworkingtypes#message_sending_flags)
- [OnlineSubsystemSteam 插件](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemSteam)
