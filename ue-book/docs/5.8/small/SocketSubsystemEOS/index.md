# Socket Subsystem EOS

> Responsible for management of EOS P2P Socket connections.

| 属性 | 值 |
|---|---|
| 中文名 | EOS P2P 套接字子系统 |
| 分类 | Online Platform |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `SocketSubsystemEOS` (RuntimeNoCommandlet) |
| 实验性 | 否 |
| 创建时间 | 2022-01-25 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/SocketSubsystemEOS) | |

## 用途

该插件为 Epic Online Services (EOS) 的 P2P（点对点）通信提供了完整的 Socket 子系统实现。它本质上是一个 `ISocketSubsystem` 的自定义实现，底层使用 EOS SDK 的 P2P API 进行数据传输，而非传统的 UDP/TCP 套接字。

**解决的问题**：在 EOS 生态中，玩家之间建立直接的 P2P 连接时，不能使用常规的操作系统 Socket，而是需要通过 EOS SDK 提供的 NAT 穿透和 relay 机制。该插件将 EOS P2P 通信抽象为标准的 Socket 接口（`FSocketEOS`），使得 UE5 的网络驱动（`UNetDriver`）可以透明地使用 EOS P2P 通道，而无需关心底层 EOS API 细节。

该插件最初是从 `OnlineSubsystemEOS` 插件中独立拆分出来的（见首次 commit），目的是让 EOS P2P Socket 功能可以被任何网络子系统复用，而非绑定在特定的 OnlineSubsystem 实现上。

**关键设计**：
- `FSocketEOS` — 实现标准 `FSocket` 接口，内部通过 EOS P2P API 发送/接收数据
- `FInternetAddrEOS` — 以 `EOS_ProductUserId` 作为地址标识（而非 IP+端口）
- `FSocketSubsystemEOS` — 管理所有 P2P Socket 的生命周期，按 World 隔离实例（支持 PIE 多实例）
- `UNetDriverEOS` — 继承自 `UIpNetDriver`，绑定 EOS Socket 子系统

## 使用场景

- 你使用 EOS（Epic Online Services）作为在线平台，需要通过 P2P 进行玩家间通信
- 你开发多人在线游戏，希望通过 EOS 的 NAT 穿透和 relay 功能建立玩家直连
- 你需要将 EOS P2P 通道暴露为标准 Socket 接口，以便 UE5 的网络复制系统透明使用
- 你在 EOS 基础上构建自定义网络子系统，需要一个可复用的 P2P Socket 实现

## 蓝图用法

该插件主要面向 C++ 网络层，几乎没有直接的蓝图节点。`UNetDriverEOS` 是一个 UCLASS，可以在项目的网络配置中引用，但通常不直接在蓝图中操作。

### 核心类

| 类 | 说明 | 层级 |
|---|---|---|
| `UNetDriverEOS` | EOS P2P 网络驱动，继承自 UIpNetDriver | 网络驱动 |
| `UNetConnectionEOS` | EOS P2P 连接，继承自 UIpConnection | 连接 |
| `FSocketSubsystemEOS` | EOS Socket 子系统，实现 ISocketSubsystem | 子系统 |
| `FSocketEOS` | EOS P2P Socket，实现 FSocket 接口 | Socket |
| `FInternetAddrEOS` | EOS 地址（基于 ProductUserId） | 地址 |

### 配置方式

在 `DefaultEngine.ini` 中设置 EOS 网络驱动：

```ini
[URL]
Port=7777

[OnlineSubsystem]
DefaultPlatformService=EOS

[/Script/OnlineSubsystemUtils.IpNetDriver]
NetDriverClassName=/Script/SocketSubsystemEOS.NetDriverEOS
```

或在代码中通过 `Engine.ini` / `Game.ini` 指定使用 `UNetDriverEOS` 作为网络驱动。

## C++ 用法

该插件没有提供自动化测试用例，用法基于源码中的接口定义。

### 头文件引入

```cpp
#include "SocketSubsystemEOS.h"
#include "SocketEOS.h"
#include "InternetAddrEOS.h"
#include "NetDriverEOS.h"
```

### 基本用法

获取 EOS Socket 子系统实例并创建 P2P Socket：

```cpp
// 获取 EOS Socket 子系统（通过 ISocketSubsystem 接口）
ISocketSubsystem* SocketSubsystem = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
if (SocketSubsystem && SocketSubsystem->GetSocketAPIName() == FString(TEXT("EOS")))
{
    FSocketSubsystemEOS* EOSSubsystem = static_cast<FSocketSubsystemEOS*>(SocketSubsystem);

    // 创建 EOS P2P Socket
    FSocket* Socket = EOSSubsystem->CreateSocket(
        FName(TEXT("EOS_P2P")),
        FString(TEXT("GameP2PSocket")),
        FName(NAME_None)
    );
}
```

### 进阶用法

使用 `ISocketSubsystemEOSUtils` 接口与特定 OnlineSubsystem 集成：

```cpp
// ISocketSubsystemEOSUtils 是连接 Socket 子系统与在线平台的桥梁
// 它提供本地用户 ID、会话 ID、子系统实例名和登录状态
// 你需要实现此接口来适配你的在线子系统

class FMySocketSubsystemUtils : public ISocketSubsystemEOSUtils
{
public:
    virtual EOS_ProductUserId GetLocalUserId() override
    {
        // 返回当前本地玩家的 EOS ProductUserId
        return CachedLocalUserId;
    }

    virtual FString GetSessionId() override
    {
        // 返回当前 EOS 会话 ID
        return CurrentSessionId;
    }

    virtual FName GetSubsystemInstanceName() override
    {
        // 返回关联的 OnlineSubsystem 实例名称
        return NAME_DefaultPlatformService;
    }

    virtual bool IsLoggedIn() override
    {
        // 返回是否已登录 EOS
        return bIsLoggedIn;
    }
};
```

创建 `FInternetAddrEOS` 地址用于连接：

```cpp
// 创建 EOS 地址（基于 ProductUserId 字符串）
FInternetAddrEOS RemoteAddr(TEXT("some-product-user-id-string"));

// 或使用 EOS SDK 的 ProductUserId
#if WITH_EOS_P2P
EOS_ProductUserId TargetUserId = /* ... */;
FInternetAddrEOS RemoteAddr(TargetUserId);
#endif
```

自定义 Socket 的数据包可靠性：

```cpp
// FSocketEOS 内部使用 EOS_EPacketReliability 控制包的可靠性
// 默认为 EOS_PR_UnreliableUnordered（不可靠无序）
// 可通过 EOS_P2P_SendPacketOptions 的 PacketReliability 字段配置
```

管理 Socket 名称绑定（防止端口冲突）：

```cpp
FSocketSubsystemEOS* Subsystem = /* ... */;

// 绑定 Socket 名称，确保同一名称不会被重复使用
bool bSuccess = Subsystem->BindSocketName(TEXT("GameSocket"));

// 使用完毕后解绑
Subsystem->UnbindSocketName(TEXT("GameSocket"));
```

按 World 获取 Socket 子系统实例（PIE 多实例支持）：

```cpp
FSocketSubsystemEOS* Subsystem = /* ... */;
FSocketSubsystemEOS* WorldSubsystem = Subsystem->GetSocketSubsystemForWorld(MyWorld);
```

## Demo 示例

一个完整的 EOS P2P Socket 使用示例：

```cpp
// MyEOSSocketExample.h
#pragma once

#include "CoreMinimal.h"
#include "SocketSubsystemEOS.h"
#include "SocketEOS.h"
#include "InternetAddrEOS.h"

class FMyEOSSocketExample
{
public:
    void Initialize()
    {
        // 1. 获取 EOS Socket 子系统
        ISocketSubsystem* RawSubsystem = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
        FSocketSubsystemEOS* EOSSubsystem = static_cast<FSocketSubsystemEOS*>(RawSubsystem);
        if (!EOSSubsystem) return;

        // 2. 创建 P2P Socket
        P2PSocket = EOSSubsystem->CreateSocket(
            FName(TEXT("EOS_P2P")),
            FString(TEXT("GameSocket")),
            NAME_None
        );
        if (!P2PSocket) return;

        // 3. 绑定本地地址
        FInternetAddrEOS LocalAddr;
        LocalAddr.SetAnyAddress();
        P2PSocket->Bind(LocalAddr);
    }

    void SendDataToRemote(EOS_ProductUserId RemoteUserId, const uint8* Data, int32 DataSize)
    {
        if (!P2PSocket) return;

        // 创建远程 EOS 地址
        FInternetAddrEOS RemoteAddr(RemoteUserId);

        // 发送数据
        int32 BytesSent = 0;
        P2PSocket->SendTo(Data, DataSize, BytesSent, RemoteAddr);
    }

    void ReceiveData(uint8* Buffer, int32 BufferSize)
    {
        if (!P2PSocket) return;

        int32 BytesRead = 0;
        FInternetAddrEOS SourceAddr;
        P2PSocket->RecvFrom(Buffer, BufferSize, BytesRead, SourceAddr);

        if (BytesRead > 0)
        {
            // SourceAddr.GetProductUserId() 获取发送者的 ProductUserId
        }
    }

    void Shutdown()
    {
        if (P2PSocket)
        {
            ISocketSubsystem* RawSubsystem = ISocketSubsystem::Get(PLATFORM_SOCKETSUBSYSTEM);
            if (RawSubsystem)
            {
                RawSubsystem->DestroySocket(P2PSocket);
            }
            P2PSocket = nullptr;
        }
    }

private:
    FSocket* P2PSocket = nullptr;
};
```

## 模块依赖

从插件的 `.uplugin` 和构建系统中提取：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 在线子系统工具类，提供 `UIpNetDriver` 等网络基础设施 |
| `EOSShared` | EOS SDK 公共头文件和类型定义 |

插件依赖（Plugins）：
- `OnlineSubsystemUtils` — 必需，提供基类网络驱动
- `EOSShared` — 必需，提供 EOS SDK 类型和回调基础设施

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的问题 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移为 UE_LOGF 宏 |
| 2026-02-10 | `bb264d17` | - Fix unreachable code error | 修复不可达代码错误 |
| 2026-02-10 | `e7d277e7` | - Minor whitespace | 微小空格调整 |
| 2026-02-09 | `52a2dc16` | - Support EOS_P2P not being present in per-project SDK | 支持项目 SDK 中不包含 EOS_P2P 的情况 |

### 维护评价

- **创建时间**：2022-01-25，约 4 年历史，属于 UE5 早期阶段从 OnlineSubsystemEOS 中独立出来的模块
- **最近更新**：2026 年仍有活跃更新，主要集中在编译兼容性修复（UE_LOG 迁移、64 位格式修复）和 EOS SDK 可选性支持
- **维护状态**：**活跃维护中** — 近 3 个月有多次提交，均为代码质量和兼容性改进
- **已知限制**：
  - 仅支持 Win64、Mac、Android 三个平台
  - 需要 `WITH_EOS_P2P` 编译宏（EOS P2P SDK 存在时才启用完整功能）
  - `UNetDriverEOSBase` 已在 5.6 标记为废弃，应使用 `UNetDriverEOS`
  - `FInternetAddrEOS` 的旧构造函数（带 SocketName/Channel 参数）已在 5.6 标记为废弃
- **推荐**：如果你的项目使用 EOS 作为在线平台并需要 P2P 通信，这是必选插件。但注意 `EnabledByDefault=false`，需手动启用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/SocketSubsystemEOS)
- [EOSShared 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/EOSShared)
- [OnlineSubsystemEOS 插件](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Online/OnlineSubsystemEOS)