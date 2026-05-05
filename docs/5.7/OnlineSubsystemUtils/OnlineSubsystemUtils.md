# Online Subsystem Utils

> Shared code for interacting online service and online subsystem implementations.

| 属性 | 值 |
|---|---|
| 分类 | Online Platform |
| 默认启用 | ✅ 是 |
| 包含内容 | ❌ 无 |
| 模块 | `OnlineSubsystemUtils` (Runtime), `OnlineBlueprintSupport` (UncookedOnly) |
| 实验性 | 否 |
| 创建时间 | 2016-07-12 |
| 年龄标签 | 👴 老古董（约 9 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils) | |

---

## 用途

Online Subsystem Utils 是 UE 在线子系统（Online Subsystem）框架的核心工具层，提供三大功能：

1. **Online Beacons（信标系统）**：在正常游戏网络之外建立独立的轻量级网络通道，用于预约、匹配、测试等场景。这是该插件最核心、代码量最大的功能。
2. **VoIP 语音系统**：提供完整的语音捕获、编码、传输、解码、播放管线，包括语音包缓冲、合成组件播放等。
3. **蓝图异步代理**：为成就、排行榜、会话管理、内购、回合制匹配等在线功能提供开箱即用的蓝图节点。

该插件存在的原因是：OnlineSubsystem 模块本身不允许依赖引擎代码，而这些功能需要引擎级别的支持（网络驱动、音频系统、蓝图系统），因此独立成此插件。

## 使用场景

- 你需要在游戏匹配前进行玩家预约（如大厅系统）→ 用 Party Beacon
- 你需要实现观战者预约系统 → 用 Spectator Beacon
- 你需要在两个 UE 实例间建立独立于游戏网络的通信通道 → 用 Online Beacon
- 你需要在蓝图中快速实现登录、会话、成就等在线功能 → 用蓝图异步代理
- 你需要实现游戏内语音聊天 → 用 VoIP 系统
- 你需要在编辑器 PIE 模式下测试在线功能 → 用 Online Services Engine Utils

---

## 蓝图用法

### 会话管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `JoinSession` | 加入远程会话 | `UJoinSessionCallbackProxy` |
| `DestroySession` | 销毁已创建的会话 | `UDestroySessionCallbackProxy` |

### 身份与登录

| 节点 | 说明 | 所在类 |
|---|---|---|
| `ShowExternalLoginUI` | 显示平台登录 UI | `UShowLoginUICallbackProxy` |
| `Logout` | 从在线服务登出 | `ULogoutCallbackProxy` |
| `ConnectToService` | 连接在线服务（已废弃，请用 ShowExternalLoginUI） | `UConnectionCallbackProxy` |

### 成就系统

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CacheAchievements` | 缓存成就进度数据 | `UAchievementQueryCallbackProxy` |
| `CacheAchievementDescriptions` | 缓存成就描述数据 | `UAchievementQueryCallbackProxy` |
| `GetCachedAchievementProgress` | 获取已缓存的成就进度 | `UAchievementBlueprintLibrary` |
| `GetCachedAchievementDescription` | 获取已缓存的成就描述 | `UAchievementBlueprintLibrary` |

### 排行榜

| 节点 | 说明 | 所在类 |
|---|---|---|
| `WriteLeaderboardInteger` | 写入整数值到排行榜 | `ULeaderboardBlueprintLibrary` |
| `CreateProxyObjectForFlush` | 刷新排行榜数据到服务器 | `ULeaderboardFlushCallbackProxy` |

### 内购

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CreateProxyObjectForInAppPurchaseCheckout` | 发起内购交易 | `UInAppPurchaseCheckoutCallbackProxy` |
| `CreateProxyObjectForInAppPurchaseFinalize` | 完成内购交易 | `UInAppPurchaseFinalizeProxy` |

### 回合制匹配

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetIsMyTurn` | 查询是否轮到自己 | `UTurnBasedBlueprintLibrary` |
| `GetMyPlayerIndex` | 获取自己的玩家索引 | `UTurnBasedBlueprintLibrary` |
| `GetPlayerDisplayName` | 获取玩家显示名 | `UTurnBasedBlueprintLibrary` |
| `RegisterTurnBasedMatchInterfaceObject` | 注册回合制匹配接口对象 | `UTurnBasedBlueprintLibrary` |
| `EndTurn` | 结束当前回合 | `UEndTurnCallbackProxy` |
| `EndMatch` | 结束比赛 | `UEndMatchCallbackProxy` |
| `QuitMatch` | 退出比赛 | `UQuitMatchCallbackProxy` |

### 语音

| 节点 | 说明 | 所在类 |
|---|---|---|
| `IsIdling` | 检查语音合成组件是否空闲（无缓冲音频） | `UVoipListenerSynthComponent` |

### 使用示例（蓝图描述）

**加入会话**：搜索会话后，将 `FBlueprintSessionResult` 连接到 `JoinSession` 节点的 `SearchResult` 引脚，绑定 `OnSuccess` 和 `OnFailure` 委托。成功后通过 `GetResolvedConnectString` 获取连接字符串。

**缓存并查询成就**：先调用 `CacheAchievements` 等待 `OnSuccess`，然后调用 `GetCachedAchievementProgress` 传入成就 ID 获取进度值。

**发起内购**：创建 `FInAppPurchaseProductRequest2` 结构体，设置 `ProductIdentifier` 和 `bIsConsumable`，传入 `CreateProxyObjectForInAppPurchaseCheckout`，绑定 `OnSuccess`/`OnFailure` 处理购买结果。

---

## C++ 用法

### 头文件引入

```cpp
#include "OnlineSubsystemUtils.h"
#include "OnlineBeaconHost.h"
#include "OnlineBeaconClient.h"
#include "OnlineBeaconHostObject.h"
#include "PartyBeaconClient.h"
#include "PartyBeaconHost.h"
```

### 基本用法 — Online Beacon 通信

Online Beacon 允许两个 UE 实例在正常游戏网络之外建立独立通信通道。

```cpp
// === 服务端：创建 Beacon Host 并注册 HostObject ===
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/OnlineBeaconHost.h

// 1. 生成 Beacon Host Actor
AOnlineBeaconHost* BeaconHost = GetWorld()->SpawnActor<AOnlineBeaconHost>(AOnlineBeaconHost::StaticClass());
BeaconHost->ListenPort = 7787;
BeaconHost->InitHost();  // 开始监听连接

// 2. 生成自定义 HostObject 并注册
AMyBeaconHostObject* HostObject = GetWorld()->SpawnActor<AMyBeaconHostObject>();
BeaconHost->RegisterHost(HostObject);
```

```cpp
// === 客户端：连接到 Beacon Host ===
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/OnlineBeaconClient.h

AMyBeaconClient* ClientBeacon = GetWorld()->SpawnActor<AMyBeaconClient>();
FURL URL;
URL.Host = TEXT("192.168.1.100");
URL.Port = 7787;
ClientBeacon->InitClient(URL);  // 发起连接

// 连接成功后会调用 OnConnected() 虚函数
// 连接失败会调用 OnFailure() 虚函数
```

### 基本用法 — 获取在线子系统工具接口

```cpp
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/OnlineSubsystemUtilsModule.h

#include "OnlineSubsystemUtilsModule.h"

FOnlineSubsystemUtilsModule& UtilsModule = FModuleManager::GetModuleChecked<FOnlineSubsystemUtilsModule>("OnlineSubsystemUtils");
IOnlineSubsystemUtils* Utils = UtilsModule.GetUtils();

// 获取 PIE 环境下的在线标识
FName OnlineId = Utils->GetOnlineIdentifier(GetWorld());

// 获取当前服务器端口
int32 Port = GetPortFromNetDriver(FName(TEXT("Game")));
```

### 基本用法 — Online Services (OSSv2) 工具

```cpp
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/Online/OnlineServicesEngineUtils.h

#include "Online/OnlineServicesEngineUtils.h"

// 获取当前 World 对应的 Online Services 实例
IOnlineServicesPtr Services = UE::Online::GetServices(GetWorld());

// 获取 PIE 实例名称（编辑器多实例区分）
FName InstanceName = UE::Online::GetServicesInstanceName(GetWorld());
```

### 进阶用法 — Party Beacon 预约系统

Party Beacon 实现了完整的玩家预约流程，适用于大厅/匹配系统。

```cpp
// === 服务端 ===
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/PartyBeaconHost.h

APartyBeaconHost* PartyHost = GetWorld()->SpawnActor<APartyBeaconHost>();

// 初始化：2 队伍，每队 4 人，最多 10 个预约
PartyHost->InitHostBeacon(
    2,           // InTeamCount
    4,           // InTeamSize
    10,          // InMaxReservations
    FName("GameSession"),
    0,           // InForceTeamNum
    true         // bInEnableRemovalRequests
);

// 注册到 Beacon Host
BeaconHost->RegisterHost(PartyHost);

// 绑定验证委托
PartyHost->OnValidatePlayersDelegate.BindLambda([](const TArray<FPlayerReservation>& Players) -> bool {
    // 检查玩家是否被封禁等
    return true;
});

// 绑定预约更新委托
PartyHost->OnReservationUpdateDelegate.BindLambda([]() {
    // 预约数量变化时的处理
});
```

```cpp
// === 客户端 ===
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/PartyBeaconClient.h

APartyBeaconClient* PartyClient = GetWorld()->SpawnActor<APartyBeaconClient>();

// 连接到 Party Beacon Host
FURL URL;
URL.Host = TEXT("192.168.1.100");
URL.Port = 7787;
PartyClient->InitClient(URL);

// 连接成功后发送预约请求
// PartyClient->RequestReservation(DestURL, Reservation);
```

### 进阶用法 — 语音系统

```cpp
// 来源: Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/VoipListenerSynthComponent.h

// 创建语音合成组件用于播放远程语音
UVoipListenerSynthComponent* VoipSynth = CreateVoiceSynthComponent(GetWorld(), SampleRate);

// 打开音频包流，设置缓冲延迟
VoipSynth->OpenPacketStream(StartingSampleCount, BufferSize, JitterDelaySeconds);

// 提交接收到的语音包
VoipSynth->SubmitPacket(AudioData, NumBytes, StartSample, EVoipStreamDataFormat::Int16);

// 检查是否还有缓冲音频
bool bIdle = VoipSynth->IsIdling();

// 关闭流
VoipSynth->ClosePacketStream();
```

---

## Demo 示例

### 自定义 Beacon 通信

```cpp
// MyBeaconHostObject.h
#pragma once

#include "OnlineBeaconHostObject.h"
#include "MyBeaconHostObject.generated.h"

UCLASS()
class AMyBeaconHostObject : public AOnlineBeaconHostObject
{
    GENERATED_BODY()

public:
    AMyBeaconHostObject();

    virtual AOnlineBeaconClient* SpawnBeaconActor(UNetConnection* ClientConnection) override;
    virtual void OnClientConnected(AOnlineBeaconClient* NewClientActor, UNetConnection* ClientConnection) override;
    virtual void NotifyClientDisconnected(AOnlineBeaconClient* LeavingClientActor) override;

    // 自定义 RPC：向所有客户端广播消息
    void BroadcastMessage(const FString& Message);
};
```

```cpp
// MyBeaconHostObject.cpp
#include "MyBeaconHostObject.h"
#include "MyBeaconClient.h"

AMyBeaconHostObject::AMyBeaconHostObject()
{
    ClientBeaconActorClass = AMyBeaconClient::StaticClass();
    BeaconTypeName = TEXT("MyBeacon");
}

AOnlineBeaconClient* AMyBeaconHostObject::SpawnBeaconActor(UNetConnection* ClientConnection)
{
    AMyBeaconClient* NewClient = GetWorld()->SpawnActor<AMyBeaconClient>(ClientBeaconActorClass);
    return NewClient;
}

void AMyBeaconHostObject::OnClientConnected(AOnlineBeaconClient* NewClientActor, UNetConnection* ClientConnection)
{
    Super::OnClientConnected(NewClientActor, ClientConnection);
    UE_LOG(LogTemp, Log, TEXT("Beacon client connected: %s"), *NewClientActor->GetName());
}

void AMyBeaconHostObject::NotifyClientDisconnected(AOnlineBeaconClient* LeavingClientActor)
{
    Super::NotifyClientDisconnected(LeavingClientActor);
    UE_LOG(LogTemp, Log, TEXT("Beacon client disconnected: %s"), *LeavingClientActor->GetName());
}

void AMyBeaconHostObject::BroadcastMessage(const FString& Message)
{
    for (AOnlineBeaconClient* Client : ClientActors)
    {
        if (AMyBeaconClient* MyClient = Cast<AMyBeaconClient>(Client))
        {
            MyClient->ClientReceiveMessage(Message);
        }
    }
}
```

```cpp
// MyBeaconClient.h
#pragma once

#include "OnlineBeaconClient.h"
#include "MyBeaconClient.generated.h"

UCLASS()
class AMyBeaconClient : public AOnlineBeaconClient
{
    GENERATED_BODY()

public:
    virtual void OnConnected() override;
    virtual void OnFailure() override;

    // 服务端调用的客户端 RPC
    UFUNCTION(Client, Reliable)
    void ClientReceiveMessage(const FString& Message);

    // 客户端调用的服务端 RPC
    UFUNCTION(Server, Reliable, WithValidation)
    void ServerSendMessage(const FString& Message);
};
```

```cpp
// MyBeaconClient.cpp
#include "MyBeaconClient.h"

void AMyBeaconClient::OnConnected()
{
    Super::OnConnected();
    UE_LOG(LogTemp, Log, TEXT("Connected to beacon host!"));
    // 连接成功后可以开始发送 RPC
    ServerSendMessage(TEXT("Hello from client!"));
}

void AMyBeaconClient::OnFailure()
{
    Super::OnFailure();
    UE_LOG(LogTemp, Warning, TEXT("Failed to connect to beacon host"));
}

void AMyBeaconClient::ClientReceiveMessage_Implementation(const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received from host: %s"), *Message);
}

bool AMyBeaconClient::ServerSendMessage_Validate(const FString& Message)
{
    return true; // 验证逻辑
}

void AMyBeaconClient::ServerSendMessage_Implementation(const FString& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received from client: %s"), *Message);
}
```

---

## 模块依赖

| 模块 | 用途 |
|---|---|
| `OnlineSubsystem` | 在线子系统核心接口 |
| `OnlineServices` | OSSv2 在线服务接口 |

无其他特殊依赖（仅标准 Core/Engine/Slate 等）。

---

## 维护状态

### 近期更新

```
- 77a167d7c66d Iris Beta - Removed #if UE_WITH_IRIS for Engine/...
  → Iris 网络框架集成，移除条件编译守卫
- 462ec4ed8231 Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and subsequently destroyed.
  → 静态分析警告修复
- ec9009980d52 Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applied using UnrealCodeFixup)
  → 代码生成优化
```

### 维护评价

- **年龄**：约 9 年（2016 年创建），属于老古董级别
- **活跃度**：仍在活跃维护，近期有 Iris 框架集成等实质性更新
- **稳定性**：作为引擎核心在线功能的基础设施，经过大量项目验证
- **重要性**：几乎所有使用在线功能的 UE 项目都间接依赖此插件
- **推荐**：✅ 强烈推荐使用。这是 UE 在线功能的标准基础设施，不是可选插件而是必需品。Online Beacon 系统是 UE 独特的轻量级网络方案，蓝图代理极大简化了在线功能的蓝图集成。

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Online/OnlineSubsystemUtils/Source/OnlineSubsystemUtils/Public/Tests)