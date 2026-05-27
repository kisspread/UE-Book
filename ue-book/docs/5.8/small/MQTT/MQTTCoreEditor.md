# MQTT

> MQTT broker and client（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | MQTT协议 |
| 分类 | 网络 |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `MQTTCore` (Runtime), `MQTTCoreEditor` (Editor) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-08-08 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT) | |

## 用途

MQTT 插件为虚幻引擎提供了完整的 MQTT 协议实现，包括客户端 (`MQTTClient`) 和服务器/消息代理 (`Broker`) 的功能。MQTT 是一种轻量级的、基于发布/订阅模式的物联网 (IoT) 通信协议，专为低带宽、高延迟或不可靠的网络环境设计。该插件允许虚幻引擎应用作为 MQTT 客户端连接到外部代理，也可以在引擎内部实例化一个代理，从而在引擎项目、外部物联网设备、移动应用或其他后端服务之间建立高效、实时的双向通信。

## 使用场景

- **物联网 (IoT) 项目**：开发与智能家居设备、传感器、工业控制器等进行通信的应用。
- **移动应用与游戏通信**：通过 MQTT 代理，手机应用可以作为游戏的遥控器或第二屏幕，实时发送控制指令或接收游戏状态。
- **分布式系统**：在多个虚幻引擎实例之间，或者引擎与其他服务（如 Node.js 后端）之间同步状态或触发事件。
- **实时监控与数据可视化**：从远程设备或模拟环境收集数据流，并在引擎 UI 中实时显示。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Create MQTT Client` | 创建一个新的 MQTT 客户端实例。 | `UMQTTBlueprintLibrary` |
| `Create Broker` | 创建一个新的本地 MQTT 代理实例。 | `UMQTTBlueprintLibrary` |
| `Connect` | 将客户端连接到指定的 MQTT 代理地址和端口。 | `UMQTTClient` |
| `Disconnect` | 断开客户端与代理的连接。 | `UMQTTClient` |
| `Publish` | 向指定的 MQTT 主题发布一条消息（可带 QoS 和保留标志）。 | `UMQTTClient` |
| `Subscribe` | 订阅指定的主题，并设置接收消息时的回调。 | `UMQTTClient` |
| `Unsubscribe` | 取消订阅指定的主题。 | `UMQTTClient` |
| `Start Broker` | 启动本地代理，开始监听客户端连接。 | `UBroker` |
| `Stop Broker` | 停止本地代理。 | `UBroker` |

### 使用示例（蓝图描述）

1.  **作为客户端发布消息**：
    1.  使用 `Create MQTT Client` 节点创建一个客户端对象。
    2.  调用客户端的 `Connect` 节点，输入代理地址（例如 “mqtt.eclipse.org”）和端口（1883）。
    3.  当 `On Connected` 委托触发后，调用 `Publish` 节点，指定主题（如 “ue/game/score”）和消息内容（可以是字符串或序列化后的 JSON）。
2.  **作为客户端订阅并接收消息**：
    1.  创建客户端并连接。
    2.  调用 `Subscribe` 节点，指定要监听的主题（如 “ue/game/command”），并将一个自定义事件绑定到 `On Message Received` 委托。
    3.  在 `On Message Received` 事件中，可以获取消息的主题 (`Topic`) 和载荷 (`Payload`)，并进行处理。
3.  **作为本地代理**：
    1.  使用 `Create Broker` 节点创建一个代理对象。
    2.  调用代理的 `Start Broker` 节点，启动代理服务。之后，其他 MQTT 客户端（包括引擎内的其他 `UMQTTClient`）就可以连接到这个本地代理。

## C++ 用法

### 头文件引入

```cpp
#include "MQTTClient.h"
#include "Broker.h"
```

### 基本用法

以下示例演示了如何创建一个 MQTT 客户端并连接到公共测试服务器。
（参考来源：`MQTTCore/Tests/MQTTConnectionTests.h`）

```cpp
#include "MQTTClient.h"

// 在你的 Actor 或 UObject 中
void AMyActor::BeginPlay()
{
    Super::BeginPlay();

    // 创建客户端实例
    MQTTClient = NewObject<UMQTTClient>(this);

    // 设置回调委托
    MQTTClient->OnConnected.AddDynamic(this, &AMyActor::HandleOnConnected);
    MQTTClient->OnConnectionFailed.AddDynamic(this, &AMyActor::HandleOnConnectionFailed);
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMyActor::HandleOnMessageReceived);

    // 连接到公共测试代理
    FMQTTConnectionSettings Settings;
    Settings.Host = TEXT("broker.hivemq.com");
    Settings.Port = 1883;
    MQTTClient->Connect(Settings);
}

void AMyActor::HandleOnConnected()
{
    UE_LOG(LogTemp, Log, TEXT("Connected to MQTT Broker!"));
    // 连接成功后可以订阅或发布
    MQTTClient->Subscribe(TEXT("ue/test/topic"));
    MQTTClient->Publish(TEXT("ue/test/topic"), TEXT("Hello from Unreal!"));
}

void AMyActor::HandleOnConnectionFailed(const FString& Reason)
{
    UE_LOG(LogTemp, Error, TEXT("Failed to connect: %s"), *Reason);
}

void AMyActor::HandleOnMessageReceived(const FMQTTMessage& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received on [%s]: %s"), *Message.Topic, *Message.Payload);
}
```

### 进阶用法

使用本地代理并让两个客户端通过它通信。
（综合参考 `Broker.h` 和 `MQTTClient` 的使用模式）

```cpp
#include "Broker.h"
#include "MQTTClient.h"

// 在游戏模式或管理器类中
void AMyGameMode::InitGame(...)
{
    Super::InitGame(...);

    // 1. 创建并启动本地代理
    LocalBroker = NewObject<UBroker>(this);
    FBrokerSettings BrokerSettings;
    BrokerSettings.Port = 1883; // 监听端口
    LocalBroker->Start(BrokerSettings);

    // 2. 创建第一个客户端（发布者）
    PublisherClient = NewObject<UMQTTClient>(this);
    FMQTTConnectionSettings PubSettings;
    PubSettings.Host = TEXT("127.0.0.1"); // 连接到本地代理
    PubSettings.Port = BrokerSettings.Port;
    PublisherClient->Connect(PubSettings);

    // 3. 创建第二个客户端（订阅者）
    SubscriberClient = NewObject<UMQTTClient>(this);
    SubscriberClient->OnMessageReceived.AddDynamic(this, &AMyGameMode::HandleGameMessage);
    FMQTTConnectionSettings SubSettings;
    SubSettings.Host = TEXT("127.0.0.1");
    SubSettings.Port = BrokerSettings.Port;
    SubscriberClient->Connect(SubSettings);
}

void AMyGameMode::PostLogin(APlayerController* NewPlayer)
{
    Super::PostLogin(NewPlayer);
    // 当玩家登录时，发布一条消息
    if (PublisherClient && PublisherClient->IsConnected())
    {
        FString PlayerJoinMessage = FString::Printf(TEXT("{\"event\":\"player_join\", \"name\":\"%s\"}"), *NewPlayer->GetName());
        PublisherClient->Publish(TEXT("game/events"), PlayerJoinMessage);
    }
}

void AMyGameMode::HandleGameMessage(const FMQTTMessage& Message)
{
    // 处理来自其他客户端的消息
    UE_LOG(LogTemp, Log, TEXT("Game event received: %s"), *Message.Payload);
}
```

## Demo 示例

以下是一个可编译的最小 Actor 示例，演示基本的连接、发布和订阅。
（文件：`MyMQTTActor.h` 和 `MyMQTTActor.cpp`）

**MyMQTTActor.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MQTTClient.h"
#include "MyMQTTActor.generated.h"

UCLASS()
class MYPROJECT_API AMyMQTTActor : public AActor
{
    GENERATED_BODY()

public:
    AMyMQTTActor();

protected:
    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    UPROPERTY(Transient)
    TObjectPtr<UMQTTClient> MQTTClient;

    UFUNCTION()
    void OnConnected();

    UFUNCTION()
    void OnConnectionFailed(const FString& Reason);

    UFUNCTION()
    void OnMessageReceived(const FMQTTMessage& Message);

    FTimerHandle PublishTimerHandle;

    void PublishPeriodicMessage();
};
```

**MyMQTTActor.cpp**
```cpp
#include "MyMQTTActor.h"

AMyMQTTActor::AMyMQTTActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyMQTTActor::BeginPlay()
{
    Super::BeginPlay();

    MQTTClient = NewObject<UMQTTClient>(this);
    if (!MQTTClient)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to create MQTT Client"));
        return;
    }

    // 绑定回调
    MQTTClient->OnConnected.AddDynamic(this, &AMyMQTTActor::OnConnected);
    MQTTClient->OnConnectionFailed.AddDynamic(this, &AMyMQTTActor::OnConnectionFailed);
    MQTTClient->OnMessageReceived.AddDynamic(this, &AMyMQTTActor::OnMessageReceived);

    // 连接设置
    FMQTTConnectionSettings Settings;
    Settings.Host = TEXT("broker.hivemq.com"); // 公共测试服务器
    Settings.Port = 1883;
    Settings.ClientId = TEXT("UnrealEngine_MQTT_Demo_") + FGuid::NewGuid().ToString();

    UE_LOG(LogTemp, Log, TEXT("Attempting to connect to MQTT Broker at %s:%d"), *Settings.Host, Settings.Port);
    MQTTClient->Connect(Settings);
}

void AMyMQTTActor::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (MQTTClient && MQTTClient->IsConnected())
    {
        MQTTClient->Disconnect();
    }
    GetWorldTimerManager().ClearTimer(PublishTimerHandle);
    Super::EndPlay(EndPlayReason);
}

void AMyMQTTActor::OnConnected()
{
    UE_LOG(LogTemp, Log, TEXT("Successfully connected to MQTT Broker!"));

    // 连接成功后，订阅一个主题
    MQTTClient->Subscribe(TEXT("ue/demo/response"));
    UE_LOG(LogTemp, Log, TEXT("Subscribed to 'ue/demo/response'"));

    // 启动定时器，每2秒发布一次消息
    GetWorldTimerManager().SetTimer(PublishTimerHandle, this, &AMyMQTTActor::PublishPeriodicMessage, 2.0f, true);
}

void AMyMQTTActor::OnConnectionFailed(const FString& Reason)
{
    UE_LOG(LogTemp, Error, TEXT("MQTT Connection Failed: %s"), *Reason);
}

void AMyMQTTActor::OnMessageReceived(const FMQTTMessage& Message)
{
    UE_LOG(LogTemp, Log, TEXT("Received Message on Topic [%s]: %s"), *Message.Topic, *Message.Payload);
    // 这里可以处理响应消息，例如更新UI或游戏状态
}

void AMyMQTTActor::PublishPeriodicMessage()
{
    if (!MQTTClient || !MQTTClient->IsConnected())
    {
        return;
    }

    static int32 Counter = 0;
    FString Payload = FString::Printf(TEXT("{\"message\":\"Hello from Unreal #%d\", \"timestamp\":%f}"), Counter++, FPlatformTime::Seconds());
    MQTTClient->Publish(TEXT("ue/demo/request"), Payload);
    UE_LOG(LogTemp, Log, TEXT("Published: %s"), *Payload);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Mqtt` | MQTT 协议的核心 C/C++ 库实现 |
| `JsonBlueprintUtilities` | 用于处理 JSON 格式的载荷数据（.uplugin 中声明的依赖） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2026-01-30 | `52a87df5` | Fixed a crash that occurred when receiving MQTT packets with payloads =128 bytes due to incorrect va | 修复了接收载荷为128字节的MQTT数据包时发生的崩溃问题。 |
| 2025-06-11 | `afdf8d75` | Replace some usages of FORCEINLINE with inline in Online modules. | 将部分在线模块中的 `FORCEINLINE` 替换为 `inline`。 |
| 2025-05-09 | `163c5cc4` | [MQTT] Removed platform restrictions | 移除了 MQTT 的平台限制。 |
| 2025-02-13 | `ec3fb596` | Replaced `IsValid(this)` under the rest of Engine/. | 将引擎中其他部分的 `IsValid(this)` 替换为更安全的方式。 |

### 维护评价

该插件创建于 2022 年，相对年轻。从提交历史看，它**处于维护中**。最近一次功能性更新（修复崩溃）发生在 2026 年 1 月，表明它仍然被 Epic Games 的团队维护着。插件当前标记为 **实验性 (`IsExperimentalVersion: true`)** 且**默认未启用 (`EnabledByDefault: false`)**，这意味着其 API 可能仍会发生变化，不建议在追求稳定性的核心生产环境中使用。然而，对于原型开发、物联网实验或特定内部项目来说，它是一个强大且在持续改进的工具。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Protocols/MQTT/MQTTCore/Tests)