# Socket Subsystem EOS

> Responsible for management of EOS P2P Socket connections.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ❌ `EnabledByDefault: false` |
| 包含内容 | false |
| 模块 | `SocketSubsystemEOS` (RuntimeNoCommandlet, PostConfigInit) |
| 创建时间 | 2022-01-25 |
| 年龄标签 | 🆕 (约 4 年) |
| 平台限制 | Win64, Mac, Android |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/SocketSubsystemEOS) | |

## 用途

SocketSubsystemEOS 为 Unreal Engine 提供了一套基于 **Epic Online Services (EOS) P2P 网络** 的 Socket 子系统实现。它将 UE 标准的 `ISocketSubsystem` 接口对接到 EOS SDK 的 P2P 通信层，使得游戏可以通过 EOS 的对等网络（Peer-to-Peer）功能进行网络通信，而无需依赖传统的 IP/端口直连方式。

**核心价值**：在不需要专用服务器、不需要暴露玩家 IP 地址的情况下，通过 EOS 的 P2P 中继网络实现玩家之间的网络通信。所有数据包经由 EOS 基础设施转发，提供了 NAT 穿透和一定程度的隐私保护。

这个 plugin 实际上是一个**底层网络传输层替换**——它用 EOS P2P 替代了标准的 UDP socket，但上层的 Unreal 网络框架（NetDriver、NetConnection、Replication 等）完全不受影响。

## 使用场景

- **P2P 多人游戏**：你的游戏采用点对点模式进行多人对战，希望借助 EOS 的 NAT 穿透能力让玩家无需手动配置端口转发
- **Epic Games Store 生态**：你的游戏发布在 Epic Games Store，已经集成了 EOS SDK，希望网络层也走 EOS 通道
- **隐藏玩家 IP**：出于隐私考虑，不希望客户端之间直接暴露真实 IP，而是通过 EOS 中继服务器转发流量
- **跨平台 P2P**：Win64、Mac、Android 之间需要跨平台 P2P 通信

**不适用的场景**：
- 专用服务器（Dedicated Server）——此 plugin 在专用服务器模式下自动回退到标准 IP socket（passthrough 模式）
- LAN 局域网游戏——URL 中带 `bIsLanMatch` 选项时会回退到标准 IP socket
- 需要 TCP 连接的场景——此 plugin 仅支持 UDP（无连接/datagram）模式

## 蓝图用法

此 plugin **没有暴露任何蓝图节点**。它是一个纯 C++ 的底层网络传输层，通过 Unreal 的 NetDriver 配置系统在引擎层面自动加载和使用。所有网络操作通过标准的 `UNetDriver`/`UNetConnection` 接口完成，无需蓝图直接操作。

## C++ 用法

此 plugin 通常不需要开发者直接调用 C++ API。它通过 Unreal 的配置系统（`Engine.ini`）激活，由引擎的网络框架自动使用。但如果你需要了解或扩展其内部工作方式，以下是核心类的说明。

### 核心类

| 类名 | 职责 |
|---|---|
| `FSocketSubsystemEOS` | 实现 `ISocketSubsystem` 接口，管理 EOS P2P socket 的创建/销毁，维护 socket 名称绑定 |
| `FSocketEOS` | 实现 `FSocket` 接口，封装 EOS P2P 的 `SendPacket`/`ReceivePacket` 操作 |
| `FInternetAddrEOS` | 实现 `FInternetAddr` 接口，用 `EOS_ProductUserId` 替代传统的 IP:Port 地址 |
| `UNetDriverEOS` | 继承 `UIpNetDriver`，在 `InitConnect`/`InitListen` 中使用 EOS socket |
| `UNetConnectionEOS` | 继承 `UIpConnection`，管理 EOS P2P 连接生命周期 |
| `ISocketSubsystemEOSUtils` | 抽象接口，由 `OnlineSubsystemEOS` 或 `OnlineServicesEOSGS` 提供，获取本地用户 ID 和登录状态 |

### 头文件引入

```cpp
#include "SocketSubsystemEOS.h"      // FSocketSubsystemEOS
#include "SocketEOS.h"               // FSocketEOS
#include "InternetAddrEOS.h"         // FInternetAddrEOS
#include "NetDriverEOS.h"            // UNetDriverEOS
#include "SocketSubsystemEOSUtils.h" // ISocketSubsystemEOSUtils
```

### 配置启用

在 `DefaultEngine.ini` 中配置 NetDriver 使用此 plugin：

```ini
[/Script/Engine.GameEngine]
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="/Script/SocketSubsystemEOS.NetDriverEOS",DriverClassNameFallback="/Script/OnlineSubsystemUtils.IpNetDriver")

[SocketSubsystemEOS]
; Relay 控制: NoRelays / AllowRelays / ForceRelays
RelayControl=AllowRelays
; 数据包可靠性类型 (EOS_EPacketReliability 的字符串值)
PacketReliabilityType=EOS_PR_UnreliableUnordered
```

> **注意**：此 plugin 的 `EnabledByDefault` 为 `false`，需要通过上述 NetDriver 配置显式启用。

### 地址系统

与传统 socket 使用 `IP:Port` 不同，EOS socket 使用 `EOS_ProductUserId` 标识通信对方：

```cpp
// 创建一个 EOS 地址
FInternetAddrEOS RemoteAddr;
RemoteAddr.SetProductUserId(RemoteUserId); // EOS_ProductUserId

// 地址比较基于 ProductUserId
if (LocalAddr == RemoteAddr)
{
    // 同一用户
}

// 转换为字符串表示
FString AddrStr = RemoteAddr.ToString(false); // 不附带端口
```

### Socket 操作

`FSocketEOS` 只支持无连接（UDP 风格）的操作模式：

```cpp
// 支持的操作
FSocketEOS* Socket = ...;

// 绑定（注册 socket 名称）
Socket->Bind(LocalAddress);

// 监听（注册 EOS P2P 连接请求通知）
Socket->Listen(0);

// 发送数据到指定对等方
int32 BytesSent = 0;
Socket->SendTo(Data, Count, BytesSent, RemoteAddress);

// 接收数据
int32 BytesRead = 0;
FInternetAddrEOS Source;
Socket->RecvFrom(Data, BufferSize, BytesRead, Source);

// 关闭与特定对等方的连接
Socket->Close(RemoteAddress);

// 不支持的操作（会返回错误）
Socket->Connect(Addr);              // SE_EOPNOTSUPP
Socket->Accept(InSocketDescription); // SE_EOPNOTSUPP
Socket->Send(Data, Count, BytesSent); // SE_EOPNOTSUPP (无连接模式)
Socket->Recv(Data, BufferSize, BytesRead); // SE_EOPNOTSUPP
Socket->Wait(Condition, WaitTime);   // SE_EOPNOTSUPP
```

### Passthrough 模式

`UNetDriverEOS` 内置了智能回退机制（`bIsPassthrough`）：

```cpp
// 以下情况会自动回退到标准 IP socket：
// 1. 专用服务器 (IsRunningDedicatedServer() == true)
// 2. EOS SocketSubsystem 不可用
// 3. URL 以 "eos://" 开头但 EOS 不可用
// 4. URL 包含 bIsLanMatch 或 bUseIPSockets 选项

// 在 passthrough 模式下，GetSocketSubsystem() 返回平台默认 socket 子系统
// 而非 EOS socket 子系统
```

### 关键设计细节

1. **Socket 名称绑定**：EOS socket 使用 `SocketName`（即 NetDriver 定义的名称字符串）的 hash 作为 P2P 通道号，确保不同 NetDriver 的数据不会混淆

2. **连接关闭追踪**：`FSocketEOS` 维护一个 `ClosedRemotes` 列表，已关闭的对等方不会被意外重新连接

3. **网络状态变化处理**：监听 EOS SDK 的网络状态变化事件，在网络从离线恢复到在线时自动重新绑定 P2P 连接通知

4. **线程安全**：所有 P2P 操作必须在游戏线程执行（有 `check(IsInGameThread())` 断言）

## Demo 示例

### 最小配置示例

**DefaultEngine.ini** — 启用 EOS P2P 网络：

```ini
; 使用 EOS NetDriver 替代默认的 IpNetDriver
[/Script/Engine.GameEngine]
+NetDriverDefinitions=(DefName="GameNetDriver",DriverClassName="/Script/SocketSubsystemEOS.NetDriverEOS",DriverClassNameFallback="/Script/OnlineSubsystemUtils.IpNetDriver")

; EOS P2P 配置
[SocketSubsystemEOS]
RelayControl=AllowRelays
PacketReliabilityType=EOS_PR_UnreliableUnordered
```

### 自定义 ISocketSubsystemEOSUtils 实现

如果你在自建的 Online Subsystem 中需要集成此 plugin，需实现 `ISocketSubsystemEOSUtils` 接口：

```cpp
// MySocketSubsystemEOSUtils.h
#pragma once
#include "SocketSubsystemEOSUtils.h"

class FMySocketSubsystemEOSUtils : public ISocketSubsystemEOSUtils
{
public:
    FMySocketSubsystemEOSUtils(EOS_ProductUserId InLocalUserId, FName InInstanceName);
    
    virtual EOS_ProductUserId GetLocalUserId() override { return LocalUserId; }
    virtual FString GetSessionId() override { return FString(); }
    virtual FName GetSubsystemInstanceName() override { return InstanceName; }
    virtual bool IsLoggedIn() override { return LocalUserId != nullptr; }

private:
    EOS_ProductUserId LocalUserId;
    FName InstanceName;
};

// MySocketSubsystemEOSUtils.cpp
#include "MySocketSubsystemEOSUtils.h"

FMySocketSubsystemEOSUtils::FMySocketSubsystemEOSUtils(
    EOS_ProductUserId InLocalUserId, FName InInstanceName)
    : LocalUserId(InLocalUserId)
    , InstanceName(InInstanceName)
{
}
```

### 构造 FSocketSubsystemEOS

```cpp
#include "SocketSubsystemEOS.h"

// 通常由 OnlineSubsystem 自动创建，以下是手动创建的示意
TSharedPtr<FMySocketSubsystemEOSUtils> Utils = 
    MakeShared<FMySocketSubsystemEOSUtils>(LocalUserId, NAME_DefaultPlatformService);

FSocketSubsystemEOS SocketSubsystem(PlatformHandle, Utils);

// Init 会自动注册到 FSocketSubsystemModule
FString Error;
SocketSubsystem.Init(Error);
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | UE 核心基础库 |
| `Engine` | 引擎核心，提供 NetDriver/NetConnection 基类 |
| `EOSShared` | EOS SDK 共享类型和工具 |
| `NetCore` | 网络核心模块 |
| `Sockets` | Socket 子系统框架（ISocketSubsystem 注册） |
| `OnlineSubsystemUtils` | 在线子系统工具库 |
| `CoreOnline` | *(私有)* 在线核心类型 |
| `CoreUObject` | *(私有)* UObject 基础设施 |
| `EOSSDK` | *(私有)* EOS SDK P2P 接口 |

**Plugin 依赖**：
- `OnlineSubsystemUtils` — 在线子系统工具
- `EOSShared` — EOS 共享库

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-08-26 | `035350464f1c` | Moving the early return when the user is logged out in SendTo, to after setting OutBytesSent value to 0. | **Bug 修复**：修复了 `SendTo` 中用户未登录时提前返回但未设置 `OutBytesSent=0` 的问题，防止调用方读到未初始化的字节数 |
| 2025-08-25 | `8c90d385bbf5` | Minor fixes in FSocketEOS | **Bug 修复**：FSocketEOS 的小修复，可能是与上述 SendTo 问题相关的连带改动 |
| 2025-08-14 | `83a838fd4fff` | Minor changes as followup to CL 44849953 | **跟进修复**：对之前提交的后续调整 |

### 维护评价

- **活跃维护**：最近 6 个月内有多次实质性代码修复，说明仍在积极维护
- **代码成熟**：创建于 2022 年，已经过约 4 年的迭代，核心功能稳定
- **5.6 版本重构**：`InternetAddrEOS` 在 5.6 中移除了 SocketName/Channel 参数（标记为 deprecated），表明架构在持续简化
- **UNetDriverEOSBase 废弃**：5.6 中 `UNetDriverEOSBase` 被标记为 deprecated，直接使用 `UNetDriverEOS`
- **无测试用例**：在 Engine/Tests 目录和 plugin 自身目录中未找到自动化测试文件
- **推荐使用**：如果你的游戏使用 EOS 作为在线服务，此 plugin 是官方推荐的 P2P 网络传输层，维护状态良好

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/Online/SocketSubsystemEOS)
- [EOS P2P 接口文档](https://dev.epicgames.com/docs/online-services/eos-p2p)（EOS SDK P2P 官方文档）
- 相关 plugin：[OnlineSubsystemEOS](../OnlineSubsystemEOS/)（提供 `FSocketSubsystemEOSUtils_OnlineSubsystemEOS` 实现）
- 相关 plugin：[OnlineServicesEOSGS](../OnlineServicesEOSGS/)（提供 `FSocketSubsystemEOSUtils_OnlineServicesEOSGS` 实现）
