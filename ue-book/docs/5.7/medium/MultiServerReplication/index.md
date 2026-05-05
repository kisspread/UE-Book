# Multi-server Replication

> Code to help facilitate connecting multiple UE server processes to each other.

| 属性 | 值 |
|---|---|
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiServerReplication` (Runtime), `MultiServerConfiguration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-15 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MultiServerReplication) | |

## 用途

这个插件解决的核心问题是**让多个 UE Dedicated Server 进程互相连接并通信**。传统的 UE 网络架构假设一个游戏世界由一台服务器（或一台 Listen Server）服务，但大型在线游戏（如开放世界 MMO、大逃杀）可能需要将游戏世界拆分到多台服务器进程上分别处理，这些服务器之间需要交换玩家状态、RPC 等信息。

MultiServerReplication 插件提供了两套互补的机制：

1. **MultiServerNode（Beacon 模式）**：基于 OnlineBeacon 的服务器间直连网络。每台服务器创建一个 `UMultiServerNode`，通过 `AMultiServerBeaconClient` 相互连接。子类化 `AMultiServerBeaconClient` 即可在服务器之间发送自定义 RPC。适合服务器间消息传递和状态同步。

2. **Proxy 模式（UProxyNetDriver）**：在网络层面实现透明代理。`UProxyNetDriver` 同时扮演游戏客户端（对后端游戏服务器）和游戏服务器（对连接上来的玩家客户端）的角色。玩家连接到 Proxy 后，Proxy 会自动将其路由到一台主游戏服务器（Primary Game Server），同时从其他游戏服务器复制可视状态。玩家无需知道 Proxy 的存在，游戏服务器也无需特殊配置。

**注意**：这是一个实验性插件（`IsExperimentalVersion=true`），默认不启用，API 和行为可能在后续版本中发生变化。

## 使用场景

- 你有一个大型开放世界游戏，需要将地图拆分到多个 Dedicated Server 上运行 → 使用 MultiServerNode 让这些服务器互相通信
- 你需要让玩家在不同服务器之间无缝迁移（如跨越服务器边界的区域切换）→ Proxy 模式可以处理 PlayerController 的重新分配
- 你需要一个网络代理层来汇聚多台游戏服务器的状态，统一对外提供服务 → 使用 UProxyNetDriver
- 你需要在服务器间发送自定义 RPC（如玩家跨服聊天、状态同步）→ 子类化 AMultiServerBeaconClient 并添加自定义 Server/Client RPC

## 蓝图用法

此插件主要是 C++ 层面的系统，没有提供面向蓝图的节点。所有扩展点（自定义 RPC、服务器注册）都需要在 C++ 中实现。

## C++ 用法

### 头文件引入

```cpp
#include "MultiServerNode.h"
#include "MultiServerBeaconClient.h"
#include "MultiServerReplicationTypes.h"
```

### 基本用法 — 创建 MultiServerNode

在 `AGameSession::RegisterServer` 或类似位置创建节点。典型做法是解析命令行参数后初始化：

```cpp
// 来源: Source/MultiServerReplication/Private/MultiServerNode.cpp

// 1. 准备参数
FMultiServerNodeCreateParams Params;
Params.World = GetWorld();
Params.ListenPort = 7778;
Params.NumServers = 4;
Params.PeerAddresses = { "10.0.0.1:7778", "10.0.0.2:7778", "10.0.0.3:7778", "10.0.0.4:7778" };
Params.UserBeaconClass = UMyCustomBeaconClient::StaticClass();
Params.OnMultiServerConnected.BindLambda([](const FString& LocalId, const FString& RemoteId, AMultiServerBeaconClient* Beacon)
{
    UE_LOG(LogTemp, Log, TEXT("Connected to peer %s from %s"), *RemoteId, *LocalId);
});

// 2. 或者从命令行解析
UMultiServerNode::ParseCommandLineIntoCreateParams(Params);
// 命令行: -MultiServerLocalId=Server1 -MultiServerListenPort=7778
//         -MultiServerPeers=10.0.0.2:7778,10.0.0.3:7778,10.0.0.4:7778
//         -MultiServerNumServers=4

// 3. 创建节点
UMultiServerNode* Node = UMultiServerNode::Create(Params);

// 4. 检查所有服务器是否已连接
if (Node && Node->AreAllServersConnected())
{
    UE_LOG(LogTemp, Log, TEXT("All servers are connected!"));
}
```

### 自定义 BeaconClient（发送自定义 RPC）

扩展 `AMultiServerBeaconClient` 来定义服务器间的 RPC：

```cpp
// MyMultiServerBeaconClient.h
#include "MultiServerBeaconClient.h"
#include "MyMultiServerBeaconClient.generated.h"

UCLASS()
class UMyMultiServerBeaconClient : public AMultiServerBeaconClient
{
    GENERATED_BODY()

public:
    // 从当前服务器发送消息到远程服务器
    UFUNCTION(Reliable, Server)
    void ServerSendMessage(const FString& Message);

    // 从远程服务器接收消息（在本地执行）
    UFUNCTION(Reliable, Client)
    void ClientReceiveMessage(const FString& Message);
};
```

通过 `UMultiServerNode::GetBeaconClientForRemotePeer` 获取对应 Peer 的 Beacon 实例并调用 RPC：

```cpp
AMultiServerBeaconClient* Beacon = Node->GetBeaconClientForRemotePeer("Server2");
if (UMyMultiServerBeaconClient* MyBeacon = Cast<UMyMultiServerBeaconClient>(Beacon))
{
    MyBeacon->ServerSendMessage(TEXT("Hello from Server1!"));
}
```

### 进阶用法 — Proxy 模式配置

使用 Proxy 模式需要在 `Engine.ini` 中注册 NetDriver 定义：

```ini
[/Script/Engine.Engine]
+NetDriverDefinitions=(DefName="MultiServerNetDriver", DriverClassName="/Script/MultiServerReplication.MultiServerNetDriver", DriverClassNameFallback="/Script/MultiServerReplication.MultiServerNetDriver")
+NetDriverDefinitions=(DefName="ProxyNetDriver", DriverClassName="/Script/MultiServerReplication.UProxyNetDriver", DriverClassNameFallback="/Script/MultiServerReplication.UProxyNetDriver")
+NetDriverDefinitions=(DefName="ProxyBackendNetDriver", DriverClassName="/Script/MultiServerReplication.UProxyBackendNetDriver", DriverClassNameFallback="/Script/MultiServerReplication.UProxyBackendNetDriver")
```

然后在代码中注册后端游戏服务器：

```cpp
UProxyNetDriver* ProxyDriver = /* 获取 ProxyNetDriver */;
ProxyDriver->RegisterGameServer(FURL(nullptr, TEXT("10.0.0.1:7777"), TRAVEL_Absolute));
ProxyDriver->RegisterGameServer(FURL(nullptr, TEXT("10.0.0.2:7777"), TRAVEL_Absolute));
```

### 进阶用法 — 控制台变量

插件提供了几个控制台变量用于调试和调优：

| CVar | 默认值 | 说明 |
|---|---|---|
| `multiserver.AllowRemoteObjectReferences` | 1 | 是否在服务器间以远程对象引用方式复制 UObject 引用 |
| `net.proxy.NonPrimarySetViewTargetInterval` | 1.0 | 更新非主游戏服务器 ViewTarget 位置的间隔（秒） |
| `net.proxy.EnableDisconnectionSupport` | true | 客户端从 Proxy 断开时是否关闭与后端服务器的连接 |
| `net.proxy.EnableParentConnectionReplication` | false | 是否启用父连接（Parent Connection）的状态复制 |

### 进阶用法 — 配置重连参数

在 `Engine.ini` 中配置 `UMultiServerNode` 的重连行为：

```ini
[/Script/MultiServerReplication.MultiServerNode]
RetryConnectDelay=0.5
RetryConnectMaxDelay=30.0
```

## Demo 示例

### 自定义 MultiServerBeaconClient

```cpp
// MyMultiServerBeaconClient.h
#pragma once
#include "MultiServerBeaconClient.h"
#include "MyMultiServerBeaconClient.generated.h"

UCLASS()
class MYPROJECT_API UMyMultiServerBeaconClient : public AMultiServerBeaconClient
{
    GENERATED_BODY()

public:
    // 向对方服务器请求玩家数量
    UFUNCTION(Reliable, Server, BlueprintCallable)
    void ServerRequestPlayerCount();

    // 回复玩家数量
    UFUNCTION(Reliable, Client)
    void ClientReceivePlayerCount(int32 Count);

    // 服务器端实现
    virtual void ServerRequestPlayerCount_Implementation()
    {
        // 在对方服务器上统计玩家数
        int32 PlayerCount = 0;
        // ... 统计逻辑 ...
        ClientReceivePlayerCount(PlayerCount);
    }

    // 客户端实现（在发起方服务器上执行）
    virtual void ClientReceivePlayerCount_Implementation(int32 Count)
    {
        UE_LOG(LogTemp, Log, TEXT("Remote server has %d players"), Count);
    }
};
```

### 在 GameSession 中初始化

```cpp
// MyGameSession.h
#pragma once
#include "GameFramework/GameSession.h"
#include "MyGameSession.generated.h"

class UMultiServerNode;

UCLASS()
class AMyGameSession : public AGameSession
{
    GENERATED_BODY()

public:
    virtual void RegisterServer() override;

private:
    UPROPERTY()
    TObjectPtr<UMultiServerNode> MultiServerNode;
};

// MyGameSession.cpp
#include "MyGameSession.h"
#include "MultiServerNode.h"
#include "MyMultiServerBeaconClient.h"

void AMyGameSession::RegisterServer()
{
    Super::RegisterServer();

    FMultiServerNodeCreateParams Params;
    Params.World = GetWorld();
    Params.UserBeaconClass = UMyMultiServerBeaconClient::StaticClass();

    // 从命令行解析参数
    UMultiServerNode::ParseCommandLineIntoCreateParams(Params);

    if (Params.LocalPeerId.IsEmpty())
    {
        // 非多服务器模式，不需要初始化
        return;
    }

    MultiServerNode = UMultiServerNode::Create(Params);
    if (MultiServerNode)
    {
        UE_LOG(LogTemp, Log, TEXT("MultiServer node created, local ID: %s"), *Params.LocalPeerId);
    }
}
```

### Build.cs 依赖

```csharp
// MyProject.Build.cs
PublicDependencyModuleNames.AddRange(new string[]
{
    "OnlineSubsystemUtils"  // MultiServerReplication 的公共依赖
});

PrivateDependencyModuleNames.AddRange(new string[]
{
    "MultiServerReplication"  // 直接使用 MultiServer 功能
});
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | OnlineBeacon 基础设施（公共依赖） |
| `Core` | UE 核心库 |
| `CoreUObject` | UObject 系统 |
| `CoreOnline` | 在线服务核心 |
| `Engine` | 引擎核心（NetDriver、World 等） |
| `NetCore` | 网络核心（NetGUID、ReplicationSystem 等） |
| `MultiServerConfiguration` | MultiServer 配置模块（同插件内部） |

此外，插件依赖 `OnlineSubsystemUtils` 插件。

## 维护状态

### 近期更新

| 日期 | Commit | 内容 | 解读 |
|---|---|---|---|
| 2025-08-26 | `b20c34b7` | Stop game state from replicating using the proxy parent connection | 优化 Proxy 模式：禁止父连接复制游戏状态，减少不必要的网络流量 |
| 2025-08-14 | `302f4f21` | Fixes for ANoPawnPlayerController leaks when migrating player controllers | 修复玩家控制器迁移时 ANoPawnPlayerController 的内存泄漏 |
| 2025-08-13 | `a1710b3a` | Add support for closing child connections in the net driver | 增加关闭子连接的支持，完善连接生命周期管理 |

### 维护评价

- **创建时间**：2024-08-15，约 2 年历史
- **实验性标记**：`IsExperimentalVersion=true`，`EnabledByDefault=false`
- **活跃度**：最近一次更新在 2025 年 8 月，持续有实质性功能修复和优化，属于**活跃维护**状态
- **代码质量**：代码注释详尽，架构清晰（Node/Beacon/Proxy 三层分离），有完善的内部文档
- **已知限制**：
  - 实验性 API，未来可能有 breaking changes
  - Proxy 模式目前不支持在连接时加载关卡（通过 UGameServerNotify 绕过）
  - 默认不启用，需要手动配置 NetDriverDefinition
  - 没有找到独立的自动化测试文件（测试可能在 EngineTest 中）
- **推荐程度**：如果你正在构建需要多服务器架构的大型在线游戏，这是 Epic 官方提供的基础设施，值得关注和试用。但由于是实验性状态，生产环境使用需要谨慎评估。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/MultiServerReplication)
