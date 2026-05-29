# Multi-server Replication

> Code to help facilitate connecting multiple UE server processes to each other.

| 属性 | 值 |
|---|---|
| 中文名 | 多服务器复制 |
| 分类 | Networking |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MultiServerReplication` (Runtime), `MultiServerConfiguration` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-08-15 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication) | |

## 用途

该插件提供两套机制来连接多个 UE 专用服务器进程并使其互相通信：

1. **MultiServerNode（信标模式）**：基于 OnlineBeacon 的点对点通信系统。通过创建 `UMultiServerNode` 实例，将多个专用服务器互相连接，并通过自定义的 `AMultiServerBeaconClient` 子类实现 RPC 通信。适用于服务器间元数据同步、状态协调等轻量级场景。

2. **Proxy NetDriver（代理模式）**：实现一个网络代理服务器，对客户端表现为普通游戏服务器，对后端服务器表现为普通客户端。代理拦截客户端的网络连接，将其多路复用到多个后端游戏服务器上。每个客户端连接会同时连接到所有注册的后端服务器，其中一个是"主服务器"（负责生成 Pawn 和 PlayerController），其余为"非主服务器"（仅复制状态，不维持玩家存在感）。适用于大规模游戏世界中玩家需要同时与多个游戏服务器交互的场景。

3. **MultiServerTransport（传输层）**：提供底层的加密 UDP 点对点传输通道，使用 HMAC-SHA1 认证和共享会话密钥，支持多线程运行。

## 使用场景

- 你的游戏需要多个专用服务器协同工作（如大世界分区服务器）→ 用 MultiServerNode 的信标模式
- 你需要一个代理服务器将客户端连接透明地分发到多个后端游戏服务器 → 用 Proxy NetDriver 模式
- 你需要玩家同时存在于多个游戏服务器上，由代理负责状态合并和路由 → 用 Proxy NetDriver
- 你需要服务器间轻量级 RPC 通信，不需要完整的代理机制 → 用 MultiServerNode + 自定义 BeaconClient
- 你需要自定义的加密点对点传输层 → 用 MultiServerTransport

## 蓝图用法

该插件主要是 C++ API，蓝图可用节点较少。核心交互通过 RPC 和事件委托实现。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ConnectToServer` | 信标客户端连接到另一个 MultiServer 节点 | `AMultiServerBeaconClient` |
| `ServerUpdateLevelVisibility` | 向主服务器更新关卡可见性 | `AMultiServerBeaconClient` |
| `ServerUpdateMultipleLevelsVisibility` | 批量更新多个关卡可见性 | `AMultiServerBeaconClient` |
| `IsAuthorityBeacon` | 判断信标实例是否具有权限 | `AMultiServerBeaconClient` |
| `GetRemotePeerId` | 获取对端服务器标识 | `AMultiServerBeaconClient` |
| `GetLocalPeerId` | 获取本地服务器标识 | `AMultiServerBeaconClient` |
| `OnAllServersConnected` | 所有服务器连接完成时的委托 | `UMultiServerNode` |

### 使用示例（蓝图描述）

1. **注册服务器并创建 MultiServerNode**（C++ 中）：在 `AGameSession::RegisterServer` 中调用 `UMultiServerNode::Create()`，传入包含 PeerAddresses 的 `FMultiServerNodeCreateParams`。

2. **自定义 BeaconClient**：子类化 `AMultiServerBeaconClient`，在其中定义自定义 Server/Client RPC。在 `OnMultiServerConnected` 回调中获取信标实例并调用自定义 RPC。

3. **使用 Proxy 模式**：通过控制台变量 `net.proxy.Enabled=true` 启动代理服务器。使用 `UProxyNetDriver::RegisterGameServer()` 注册后端游戏服务器地址。

## C++ 用法

### 头文件引入

```cpp
#include "MultiServerNode.h"
#include "MultiServerBeaconClient.h"
#include "MultiServerReplicationModule.h"
```

### 基本用法 — MultiServerNode 信标模式

```cpp
// 在 GameSession 中创建 MultiServerNode
// 来源: Public/MultiServerNode.h

// 1. 子类化 AMultiServerBeaconClient 实现自定义 RPC
UCLASS()
class UMyBeaconClient : public AMultiServerBeaconClient
{
    GENERATED_BODY()

public:
    UFUNCTION(Reliable, Server, WithValidation)
    void ServerSendMessage(const FString& Message);

    UFUNCTION(Reliable, Client)
    void ClientReceiveMessage(const FString& Message);
};

// 2. 在服务器注册时创建节点
void AMyGameSession::RegisterServer()
{
    Super::RegisterServer();

    FMultiServerNodeCreateParams Params;
    // 配置服务器地址列表
    Params.PeerAddresses.Add(TEXT("192.168.1.10:7777"));
    Params.PeerAddresses.Add(TEXT("192.168.1.11:7777"));
    // 设置自定义 Beacon 类
    Params.BeaconClass = UMyBeaconClient::StaticClass();

    // 创建节点，自动尝试连接所有 Peer
    UMultiServerNode* Node = UMultiServerNode::Create(Params);

    // 监听所有服务器连接完成事件
    Node->OnAllServersConnected().AddLambda([](UMultiServerNode* InNode)
    {
        UE_LOG(LogMultiServerReplication, Log, TEXT("所有服务器已连接"));
    });
}
```

### 基本用法 — 查询连接状态

```cpp
// 来源: Public/MultiServerNode.h

// 检查所有服务器是否已连接
if (Node->AreAllServersConnected())
{
    // 获取指定远程 Peer 的 BeaconClient
    AMultiServerBeaconClient* Client = Node->GetBeaconClientForRemotePeer(TEXT("Server02"));
    if (Client)
    {
        // 类型安全版本
        UMyBeaconClient* MyClient = Node->GetBeaconClientForRemotePeer<UMyBeaconClient>(TEXT("Server02"));
    }

    // 遍历所有 BeaconClient
    Node->ForEachBeaconClient([](AMultiServerBeaconClient* Beacon)
    {
        // 处理每个连接
    });

    // 获取连接数量
    uint32 Count = Node->GetConnectionCount();
}
```

### 进阶用法 — Proxy 模式

```cpp
// Proxy 模式通过 cvar 启动: net.proxy.Enabled=true
// 代码中检测是否作为代理运行:

// 来源: Public/MultiServerReplicationModule.h
bool bIsProxy = FMultiServerReplicationModule::IsRunningAsProxy();

// 来源: Public/MultiServerProxy.h
// 注册后端游戏服务器
UProxyNetDriver* ProxyDriver = ...;
ProxyDriver->RegisterGameServer(FURL(nullptr, TEXT("192.168.1.10:7778"), ETravelType::TRAVEL_Absolute));
ProxyDriver->RegisterGameServer(FURL(nullptr, TEXT("192.168.1.11:7778"), ETravelType::TRAVEL_Absolute));

// 设置循环分配主服务器（每个客户端连接时轮换主服务器）
ProxyDriver->SetCyclePrimaryGameServer(true);

// 检查是否连接到所有后端服务器
if (ProxyDriver->IsConnectedToAllGameServers())
{
    // 遍历所有后端服务器连接
    int32 ServerCount = ProxyDriver->GetGameServerConnectionCount();
    for (int32 i = 0; i < ServerCount; ++i)
    {
        FGameServerConnectionState* ConnState = ProxyDriver->GetGameServerConnection(i);
        // ConnState->GameServerURL - 服务器地址
        // ConnState->NetDriver - 对应的后端网络驱动
    }
}

// 广播 RPC 到客户端连接的所有游戏服务器
ProxyDriver->BroadcastToAllClientConnectedGameServers(Player, Function, Parms, SubObject);
```

### 进阶用法 — MultiServerTransport

```cpp
// 来源: Public/MultiServerTransport.h
// 直接使用底层传输层

TArray<FString> AllAddresses = {
    TEXT("192.168.1.10:7800"),
    TEXT("192.168.1.11:7800"),
    TEXT("192.168.1.12:7800")
};

FMultiServerTransport Transport(
    TEXT("SharedSecretKey123"),   // 共享会话密钥
    TEXT("Server00"),             // 本地 Peer ID
    7800,                        // 监听端口
    TEXT("192.168.1.10"),         // 本地地址
    AllAddresses,                // 所有服务器地址
    UMyTransportEndpoint::StaticClass()  // 自定义 Endpoint 类
);

Transport.SetWorld(GetWorld());

// 在游戏线程中轮询（处理传入 RPC）
bool bIsRunning = Transport.GameThreadTick();

// 获取指定远程 Peer 的 Endpoint
UMyTransportEndpoint* Endpoint = Transport.GetEndpointForRemotePeer<UMyTransportEndpoint>(TEXT("Server01"));

// 遍历所有 Endpoint
Transport.ForEachEndpoint([](UMultiServerTransportEndpoint* EP)
{
    FString RemoteId = EP->GetRemotePeerId();
});
```

## Demo 示例

### 自定义 BeaconClient 实现服务器间通信

```cpp
// MyMultiServerBeaconClient.h
#pragma once

#include "CoreMinimal.h"
#include "MultiServerBeaconClient.h"
#include "MyMultiServerBeaconClient.generated.h"

UCLASS()
class MYGAME_API UMyMultiServerBeaconClient : public AMultiServerBeaconClient
{
    GENERATED_BODY()

public:
    // 自定义 Server RPC：通知主服务器玩家分数更新
    UFUNCTION(Reliable, Server, WithValidation)
    void ServerUpdatePlayerScore(int32 PlayerId, int32 NewScore);

    // 自定义 Client RPC：通知其他服务器分数已同步
    UFUNCTION(Reliable, Client)
    void ClientScoreUpdated(int32 PlayerId, int32 NewScore);

    // 委托：接收到分数更新时触发
    DECLARE_DELEGATE_TwoParams(FOnScoreUpdated, int32 /*PlayerId*/, int32 /*Score*/);
    FOnScoreUpdated OnScoreUpdated;
};

// MyMultiServerBeaconClient.cpp
#include "MyMultiServerBeaconClient.h"
#include "Net/UnrealNetwork.h"

bool UMyMultiServerBeaconClient::ServerUpdatePlayerScore_Validate(int32 PlayerId, int32 NewScore)
{
    return PlayerId >= 0 && NewScore >= 0;
}

void UMyMultiServerBeaconClient::ServerUpdatePlayerScore_Implementation(int32 PlayerId, int32 NewScore)
{
    // 在主服务器上处理分数更新
    UE_LOG(LogTemp, Log, TEXT("Server received score update: Player %d -> %d"), PlayerId, NewScore);

    // 广播给其他连接的服务器
    ClientScoreUpdated(PlayerId, NewScore);
}

void UMyMultiServerBeaconClient::ClientScoreUpdated_Implementation(int32 PlayerId, int32 NewScore)
{
    UE_LOG(LogTemp, Log, TEXT("Client received score update: Player %d -> %d"), PlayerId, NewScore);

    if (OnScoreUpdated.IsBound())
    {
        OnScoreUpdated.Execute(PlayerId, NewScore);
    }
}
```

```cpp
// MyGameSession.h
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameSession.h"
#include "MyGameSession.generated.h"

class UMultiServerNode;
class UMyMultiServerBeaconClient;

UCLASS()
class MYGAME_API AMyGameSession : public AGameSession
{
    GENERATED_BODY()

public:
    virtual void RegisterServer() override;

private:
    UPROPERTY()
    TObjectPtr<UMultiServerNode> MultiServerNode;

    void OnServerConnected(UMultiServerNode* Node);
};
```

```cpp
// MyGameSession.cpp
#include "MyGameSession.h"
#include "MultiServerNode.h"
#include "MyMultiServerBeaconClient.h"

void AMyGameSession::RegisterServer()
{
    Super::RegisterServer();

    FMultiServerNodeCreateParams Params;
    // 通过命令行参数解析 Peer 地址
    UMultiServerNode::ParseCommandLineIntoCreateParams(Params);

    // 创建 MultiServer 节点
    MultiServerNode = UMultiServerNode::Create(Params);
    if (MultiServerNode)
    {
        // 注册连接完成回调
        MultiServerNode->OnAllServersConnected().AddUObject(
            this, &AMyGameSession::OnServerConnected);
    }
}

void AMyGameSession::OnServerConnected(UMultiServerNode* Node)
{
    UE_LOG(LogTemp, Log, TEXT("All MultiServer peers connected! Connection count: %u"),
        Node->GetConnectionCount());

    // 遍历所有连接并设置自定义回调
    Node->ForEachBeaconClient([Node](AMultiServerBeaconClient* Beacon)
    {
        UMyMultiServerBeaconClient* MyBeacon = Cast<UMyMultiServerBeaconClient>(Beacon);
        if (MyBeacon)
        {
            FString RemoteId = MyBeacon->GetRemotePeerId();
            UE_LOG(LogTemp, Log, TEXT("Connected to peer: %s"), *RemoteId);

            MyBeacon->OnScoreUpdated.BindLambda([](int32 PlayerId, int32 Score)
            {
                UE_LOG(LogTemp, Log, TEXT("Synced score: Player %d -> %d"), PlayerId, Score);
            });
        }
    });
}
```

## 模块依赖

从 Build.cs 分析，该插件依赖了以下特殊模块：

| 模块 | 用途 |
|---|---|
| `OnlineSubsystemUtils` | 提供 OnlineBeacon 基础设施（BeaconHost、BeaconClient 等） |

其余为标准 Core/Engine/Networking 依赖，无需特别说明。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中 scoped enum 导致输出乱码的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配的编译问题 |
| 2026-04-15 | `025454a5` | static analysis fix: using alloca in a loop | 修复静态分析检测到的循环内 alloca 使用问题 |
| 2026-04-15 | `f0b565cd` | FMultiServerTransport | 新增 FMultiServerTransport 底层传输层实现 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将 UE_LOG 迁移到 UE_LOGF 新日志宏 |

### 维护评价

- **创建时间**：2024 年 8 月，插件非常年轻（约 1 年）
- **实验性状态**：`.uplugin` 中 `IsExperimentalVersion=true`，且默认未启用（`EnabledByDefault=false`），需手动在 Plugins 面板中启用
- **更新频率**：近期（2026 年 4 月）有多次功能性更新（新增 MultiServerTransport 传输层）和代码质量修复，表明仍在**积极开发中**
- **已知限制**：作为实验性功能，API 可能会发生变化；Proxy 模式下不支持关卡加载（见 `UGameServerNotify` 注释）；当前未默认安装（`Installed=false`）
- **推荐程度**：如果你需要多服务器协同功能，这是一个值得关注的实验性插件，但不建议在生产环境直接使用。适合在原型阶段提前评估和测试多服务器架构方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/MultiServerReplication)
- 官方文档：暂无（实验性插件）